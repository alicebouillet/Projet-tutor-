import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
import numpy as np

# Chargement des données
df = pd.read_csv("data/airbnb_enrichi.csv")
df = df.dropna(subset=["latitude", "longitude"])

# Récupération des arrondissements
url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson"
arrondissements = gpd.read_file(url)
arrondissements = arrondissements[["l_aroff", "geometry"]].rename(columns={"l_aroff": "arrondissement"})
arrondissements = arrondissements.to_crs("EPSG:4326")

# Jointure spatiale
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")
if "arrondissement" in gdf.columns:
    gdf = gdf.drop(columns=["arrondissement"])
gdf = gpd.sjoin(gdf, arrondissements[["arrondissement", "geometry"]], how="left", predicate="within")

# ✅ AJOUT ICI — supprimer les doublons du sjoin
gdf = gdf[~gdf.index.duplicated(keep='first')]

print(f"Airbnb après déduplication : {len(gdf)}") 

# Statistiques par arrondissement
stats_arron = gdf.groupby("arrondissement").agg(
    prix_moyen=("price", "mean"),
    prix_std=("price", "std"),
    note_moyenne=("review_scores_rating", "mean"),
).reset_index()

gdf = gdf.merge(stats_arron, on="arrondissement", how="left")

# Catégorisation
def categoriser_airbnb(row):
    if pd.notna(row.get('price')) and pd.notna(row.get('prix_moyen')) and pd.notna(row.get('prix_std')):
        if row['price'] > row['prix_moyen'] + 1.5 * row['prix_std']:
            return "prix_élevé"
        elif row['price'] < row['prix_moyen'] - 1.5 * row['prix_std']:
            return "prix_bas"
    if pd.notna(row.get('review_scores_rating')):
        if row['review_scores_rating'] >= 95:
            return "note_excellente"
        elif row['review_scores_rating'] < 70:
            return "note_faible"
    if pd.notna(row.get('number_of_reviews')) and row['number_of_reviews'] > 100:
        return "très_populaire"
    return "normal"

gdf['categorie_principale'] = gdf.apply(categoriser_airbnb, axis=1)
print(f"\nRépartition :")
print(gdf['categorie_principale'].value_counts())

# ⚠️ Folium n'accepte pas 'gray' → utiliser 'lightgray'
couleurs_folium = {
    "prix_élevé":     "red",
    "prix_bas":       "green",
    "note_excellente":"blue",
    "note_faible":    "orange",
    "très_populaire": "purple",
    "normal":         "lightgray"  # ← corrigé
}

couleurs_legende = {
    "prix_élevé":     "red",
    "prix_bas":       "green",
    "note_excellente":"blue",
    "note_faible":    "orange",
    "très_populaire": "purple",
    "normal":         "gray"
}

# Création de la carte
m = folium.Map(location=[48.8566, 2.3522], zoom_start=12, tiles="CartoDB positron")

# Contours arrondissements
folium.GeoJson(
    arrondissements.__geo_interface__,
    name="Arrondissements",
    style_function=lambda x: {
        "fillColor": "transparent",
        "color": "black",
        "weight": 2,
        "fillOpacity": 0.1
    },
    tooltip=folium.GeoJsonTooltip(fields=["arrondissement"], aliases=["Arrondissement :"])
).add_to(m)

# Ajout des marqueurs par catégorie
for categorie, couleur in couleurs_folium.items():
    gdf_cat = gdf[gdf['categorie_principale'] == categorie].copy()
    if len(gdf_cat) == 0:
        continue

    print(f"Ajout de {len(gdf_cat)} points — {categorie}")

    marker_cluster = MarkerCluster(
        name=f"{categorie.replace('_', ' ').title()} ({len(gdf_cat)})",
        overlay=True,
        control=True,
        show=(categorie != "normal")  # cacher 'normal' par défaut pour alléger
    )

    for _, row in gdf_cat.iterrows():
        try:
            lat, lon = float(row['latitude']), float(row['longitude'])
            if np.isnan(lat) or np.isnan(lon):
                continue

            nom = str(row.get('name', 'Sans nom'))[:50] if pd.notna(row.get('name')) else 'Sans nom'
            prix = f"{row['price']:.0f}€" if pd.notna(row.get('price')) else "N/A"
            note = f"{row['review_scores_rating']:.1f}/100" if pd.notna(row.get('review_scores_rating')) else "N/A"
            prix_moy = f"{row['prix_moyen']:.0f}€" if pd.notna(row.get('prix_moyen')) else "N/A"
            nb_avis = int(row['number_of_reviews']) if pd.notna(row.get('number_of_reviews')) else 0

            popup_html = f"""
            <div style="font-family: Arial; width: 220px;">
                <h4 style="margin: 5px 0;">{nom}</h4>
                <b>Prix :</b> {prix}<br>
                <b>Note :</b> {note}<br>
                <b>Type :</b> {row.get('room_type', 'N/A')}<br>
                <b>Arrondissement :</b> {row.get('arrondissement', 'N/A')}<br>
                <b>Prix moyen arrond. :</b> {prix_moy}<br>
                <b>Capacité :</b> {row.get('accommodates', 'N/A')} pers.<br>
                <b>Avis :</b> {nb_avis} reviews
            </div>
            """

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{nom} — {prix}",
                icon=folium.Icon(color=couleur, icon='home', prefix='fa')
            ).add_to(marker_cluster)

        except Exception as e:
            print(f"  ⚠️ Erreur sur un point : {e}")
            continue

    marker_cluster.add_to(m)

# Légende
legend_html = '''
<div style="position: fixed; top: 10px; right: 10px; width: 230px;
            background-color: white; border:2px solid grey; z-index:9999;
            font-size:14px; padding: 10px; border-radius: 5px;">
  <h4 style="margin-top:0">Légende</h4>
  <p><span style="color:red;font-size:18px">●</span> Prix élevé (&gt; moy + 1.5σ)</p>
  <p><span style="color:green;font-size:18px">●</span> Prix bas (&lt; moy − 1.5σ)</p>
  <p><span style="color:blue;font-size:18px">●</span> Note excellente (≥ 95)</p>
  <p><span style="color:orange;font-size:18px">●</span> Note faible (&lt; 70)</p>
  <p><span style="color:purple;font-size:18px">●</span> Très populaire (&gt; 100 avis)</p>
  <p><span style="color:gray;font-size:18px">●</span> Normal</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

folium.LayerControl(collapsed=False).add_to(m)

m.save("carte_airbnb_points.html")
print("\n✅ Carte exportée : carte_airbnb_points.html")