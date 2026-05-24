import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
import requests
#regarder dans les arrondissment les points 
#. Chargement des données
df = pd.read_csv("data/airbnb_enrichi.csv")  
df = df.dropna(subset=["latitude", "longitude"])

#Contours officiels des arrondissements de Paris (open data)
url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson"
arrondissements = gpd.read_file(url)
arrondissements = arrondissements[["l_aroff", "geometry"]].rename(columns={"l_aroff": "arrondissement"})

# Jointure spatiale lat/lon → arrondissement 
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")
arrondissements = arrondissements.to_crs("EPSG:4326")
# Supprimer la colonne arrondissement existante pour éviter les conflits
if "arrondissement" in gdf.columns:
    gdf = gdf.drop(columns=["arrondissement"])
gdf = gpd.sjoin(gdf, arrondissements, how="left", predicate="within")

# Agrégation par arrondissement 
agg = gdf.groupby("arrondissement").agg(
    nb_annonces       = ("listing_id", "count"),
    prix_moyen        = ("price", "mean"),
    note_moyenne      = ("review_scores_rating", "mean"),
    pct_logement_entier = ("room_type", lambda x: x.astype(str).str.contains(r"Entire|Entire place|Entire apartment|Entire home|Entire home/apt", case=False, na=False).mean() * 100),
).reset_index().round(2)

print("Valeurs distinctes de `room_type` (extrait):", df['room_type'].dropna().unique()[:10])

#  Fusion avec le GeoJSON pour la carte 
arrondissements = arrondissements.merge(agg, on="arrondissement", how="left")

# Carte Folium avec onglets par métrique 
m = folium.Map(location=[48.8566, 2.3522], zoom_start=12, tiles="CartoDB positron")

metriques = {
    "nb_annonces":          ("Nombre d'annonces",        "YlOrRd"),
    "prix_moyen":           ("Prix moyen (€)",           "YlGn"),
    "note_moyenne":         ("Note moyenne",             "Blues"),
    "pct_logement_entier":  ("% logements entiers",      "PuRd"),
}

for col, (label, palette) in metriques.items():
    folium.Choropleth(
        geo_data=arrondissements.__geo_interface__,
        data=arrondissements,
        columns=["arrondissement", col],
        key_on="feature.properties.arrondissement",
        fill_color=palette,
        fill_opacity=0.7,
        line_opacity=0.4,
        legend_name=label,
        name=label,
        highlight=True,
    ).add_to(m)

# Tooltips interactifs au survol
folium.GeoJson(
    arrondissements.__geo_interface__,
    name="Détail",
    style_function=lambda x: {"fillOpacity": 0, "weight": 0},
    tooltip=folium.GeoJsonTooltip(
        fields=["arrondissement", "nb_annonces", "prix_moyen", "note_moyenne", "pct_logement_entier"],
        aliases=["Arrondissement", "Nb annonces", "Prix moyen (€)", "Note moyenne", "% logements entiers"],
        localize=True,
    )
).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

m.save("carte_airbnb_paris.html")
print("✅ Carte exportée : carte_airbnb_paris.html")
