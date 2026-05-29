import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium import plugins
from streamlit_folium import st_folium
from pathlib import Path
import altair as alt

# ── Palette ───────────────────────────────────────────────────────────────
TEAL        = "#C7EFCF"
TEAL_LIGHT  = "#E3F7E8"
SAGE        = "#FFCCBA"
DARK        = "#010221"
GOLD        = "#F0B67F"
BRICK       = "#FE5F55"
ORANGE      = "#F3986D"

# ── Chemins ───────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_FILE = DATA_DIR / "airbnb_enrichi.csv"


# ── Chargement des données ────────────────────────────────────────────────
@st.cache_data(show_spinner="Chargement des données…")
def _load_data() -> pd.DataFrame | None:
    """Charge les données du fichier airbnb_enrichi.csv."""
    if not DATA_FILE.exists():
        return None
    
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig", low_memory=False)
    
    # Conversion des types
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
    if "latitude" in df.columns:
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    if "longitude" in df.columns:
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    
    # Filtrer les prix aberrants (> 3000€)
    if "price" in df.columns:
        df = df[df["price"] <= 3000]
    
    return df


@st.cache_data(show_spinner="Chargement des arrondissements…")
def _load_arrondissements() -> gpd.GeoDataFrame | None:
    """Charge les contours des arrondissements de Paris."""
    try:
        url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson"
        arrondissements = gpd.read_file(url)
        arrondissements = arrondissements[["l_aroff", "geometry"]].rename(columns={"l_aroff": "arrondissement"})
        return arrondissements
    except Exception:
        return None


@st.cache_data(show_spinner="Calcul des statistiques par arrondissement…")
def _compute_arrondissement_stats(df: pd.DataFrame, _arrondissements: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Calcule les statistiques agrégées par arrondissement."""
    # Création du GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )
    
    arrondissements = _arrondissements.copy().to_crs("EPSG:4326")
    
    # Supprimer la colonne arrondissement existante pour éviter les conflits
    if "arrondissement" in gdf.columns:
        gdf = gdf.drop(columns=["arrondissement"])
    
    # Jointure spatiale
    gdf = gpd.sjoin(gdf, arrondissements, how="left", predicate="within")
    
    # Agrégation par arrondissement
    agg = gdf.groupby("arrondissement").agg(
        nb_annonces=("listing_id", "count"),
        prix_moyen=("price", "mean"),
        note_moyenne=("review_scores_rating", "mean"),
        pct_logement_entier=("room_type", lambda x: x.astype(str).str.contains(
            r"Entire|Entire place|Entire apartment|Entire home|Entire home/apt",
            case=False, na=False
        ).mean() * 100),
    ).reset_index().round(2)
    
    # Fusion avec le GeoJSON
    arrondissements = arrondissements.merge(agg, on="arrondissement", how="left")
    
    return arrondissements


# ── Création des cartes Folium ────────────────────────────────────────────
def _create_points_map(df: pd.DataFrame, sample_size: int = 1000) -> folium.Map:
    """Crée une carte avec des points individuels."""
    # Filtrer les données valides
    df_clean = df.dropna(subset=["latitude", "longitude", "price"]).copy()
    
    # Échantillonnage si nécessaire
    if len(df_clean) > sample_size:
        df_sample = df_clean.sample(sample_size, random_state=42)
    else:
        df_sample = df_clean
    
    # Créer la carte centrée sur Paris
    m = folium.Map(
        location=[48.8566, 2.3522],
        zoom_start=12,
        tiles="CartoDB positron"
    )
    
    # Ajouter les marqueurs avec clustering
    marker_cluster = plugins.MarkerCluster(
        name="Annonces Airbnb",
        overlay=True,
        control=True,
    ).add_to(m)
    
    for idx, row in df_sample.iterrows():
        # Déterminer la couleur selon le prix
        price = row["price"]
        if price < 50:
            color = "green"
        elif price < 100:
            color = "blue"
        elif price < 150:
            color = "orange"
        else:
            color = "red"
        
        # Créer le popup
        name = str(row.get('name', 'Sans nom'))[:50] if pd.notna(row.get('name')) else 'Sans nom'
        room_type = str(row.get('room_type', 'N/A')) if pd.notna(row.get('room_type')) else 'N/A'
        arrondissement = str(row.get('arrondissement', 'N/A')) if pd.notna(row.get('arrondissement')) else 'N/A'
        note = f"{row.get('review_scores_rating', 'N/A'):.1f}" if pd.notna(row.get('review_scores_rating')) else 'N/A'
        
        popup_html = f"""
        <div style="font-family: Arial; font-size: 12px; width: 200px;">
            <b>{name}</b><br>
            <hr style="margin: 5px 0;">
            <b>Prix:</b> {price:.0f} €<br>
            <b>Type:</b> {room_type}<br>
            <b>Arrondissement:</b> {arrondissement}<br>
            <b>Note:</b> {note}/5
        </div>
        """
        
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=5,
            popup=folium.Popup(popup_html, max_width=250),
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.6,
        ).add_to(marker_cluster)
    
    # Ajouter un contrôle de couches
    folium.LayerControl().add_to(m)
    
    return m


def _create_choropleth_map(arrondissements: gpd.GeoDataFrame) -> folium.Map:
    """Crée une carte choroplèthe par arrondissement."""
    import branca.colormap as cm
    
    # Créer la carte centrée sur Paris
    m = folium.Map(
        location=[48.8566, 2.3522],
        zoom_start=12,
        tiles="CartoDB positron"
    )
    
    # Métriques à afficher avec colormaps personnalisées
    metriques = {
        "nb_annonces": ("Nombre d'annonces", ["#FFF5F0", "#FEE5D9", "#FCBBA1", "#FC9272", "#FB6A4A", "#EF3B2C", "#CB181D", "#99000D"]),
        "prix_moyen": ("Prix moyen (€)", ["#FFFFE5", "#F7FCB9", "#D9F0A3", "#ADDD8E", "#78C679", "#41AB5D", "#238443", "#005A32"]),
        "note_moyenne": ("Note moyenne", ["#F7FBFF", "#DEEBF7", "#C6DBEF", "#9ECAE1", "#6BAED6", "#4292C6", "#2171B5", "#084594"]),
        "pct_logement_entier": ("% logements entiers", ["#F7F4F9", "#E7E1EF", "#D4B9DA", "#C994C7", "#DF65B0", "#E7298A", "#CE1256", "#91003F"]),
    }
    
    # Créer des feature groups pour chaque métrique
    for col, (label, colors) in metriques.items():
        fg = folium.FeatureGroup(name=label, show=col == "nb_annonces")  # Première couche visible par défaut
        
        # Calculer min/max pour la normalisation
        values = arrondissements[col].dropna()
        if len(values) > 0:
            vmin, vmax = values.min(), values.max()
        else:
            vmin, vmax = 0, 1
        
        # Créer la colormap avec les couleurs personnalisées
        colormap = cm.LinearColormap(colors=colors, vmin=vmin, vmax=vmax)
        
        # Fonction de style
        def style_function(feature, col=col, colormap=colormap):
            value = feature['properties'].get(col)
            if value is None or pd.isna(value):
                return {
                    'fillColor': '#gray',
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.5
                }
            return {
                'fillColor': colormap(value),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            }
        
        # Ajouter le GeoJson avec style et tooltip
        folium.GeoJson(
            arrondissements.__geo_interface__,
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=["arrondissement", "nb_annonces", "prix_moyen", "note_moyenne", "pct_logement_entier"],
                aliases=["Arrondissement", "Nb annonces", "Prix moyen (€)", "Note moyenne", "% logements entiers"],
                localize=True,
            )
        ).add_to(fg)
        
        # Ajouter la légende de couleur
        colormap.caption = label
        colormap.add_to(m)
        
        fg.add_to(m)
    
    # Ajouter un contrôle de couches
    folium.LayerControl(collapsed=False).add_to(m)
    
    return m


# ── Graphiques Altair ─────────────────────────────────────────────────────
def _chart_arrondissement(df: pd.DataFrame) -> alt.Chart:
    """Graphique du nombre d'annonces par arrondissement."""
    counts = (
        df.groupby("arrondissement")
        .size()
        .reset_index(name="nb_annonces")
        .sort_values("nb_annonces", ascending=False)
    )
    
    return (
        alt.Chart(counts)
        .mark_bar(color=TEAL)
        .encode(
            x=alt.X("nb_annonces:Q", title="Nombre d'annonces"),
            y=alt.Y("arrondissement:N", sort="-x", title="Arrondissement"),
            tooltip=[
                alt.Tooltip("arrondissement:N", title="Arrondissement"),
                alt.Tooltip("nb_annonces:Q", title="Nb annonces", format=","),
            ]
        )
        .properties(
            height=500,
            title="Nombre d'annonces par arrondissement"
        )
    )


def _chart_price_arrondissement(df: pd.DataFrame) -> alt.Chart:
    """Graphique du prix moyen par arrondissement."""
    price_stats = (
        df.groupby("arrondissement")["price"]
        .mean()
        .reset_index(name="prix_moyen")
        .sort_values("prix_moyen", ascending=False)
    )
    
    return (
        alt.Chart(price_stats)
        .mark_bar(color=GOLD)
        .encode(
            x=alt.X("prix_moyen:Q", title="Prix moyen (€)"),
            y=alt.Y("arrondissement:N", sort="-x", title="Arrondissement"),
            tooltip=[
                alt.Tooltip("arrondissement:N", title="Arrondissement"),
                alt.Tooltip("prix_moyen:Q", title="Prix moyen", format=".2f"),
            ]
        )
        .properties(
            height=500,
            title="Prix moyen par arrondissement"
        )
    )


# ── KPI cards ─────────────────────────────────────────────────────────────
def _kpi_card(label: str, value: str, icon: str, color: str) -> str:
    return f"""
    <div style="
        background:{color};
        border-radius:12px;
        padding:1.5em 1em;
        text-align:center;
        height:100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <div style="font-size:3em;margin-bottom:0.2em;">{icon}</div>
        <div style="color:white;font-size:2.2em;font-weight:700;margin:0.3em 0;">
            {value}
        </div>
        <div style="color:{SAGE};font-size:0.9em;font-weight:600;">
            {label}
        </div>
    </div>
    """


# ── Point d'entrée ────────────────────────────────────────────────────────
def app():
    """Page principale de cartographie Airbnb."""
    
    # ── En-tête ───────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {TEAL} 0%, {TEAL_LIGHT} 100%);
            padding: 2em;
            border-radius: 12px;
            margin-bottom: 2em;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <h2 style="text-align:center; color:white; margin:0;">
                🗺️ Cartographie des annonces Airbnb à Paris
            </h2>
            <p style="text-align:center; color:{SAGE}; font-size:1.1em; margin-top:0.5em;">
                Visualisation géographique et analyse par arrondissement
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ── Chargement des données ────────────────────────────────────────────
    df = _load_data()
    if df is None:
        st.error(
            f"❌ Fichier de données introuvable : `{DATA_FILE}`\n\n"
            "Veuillez vous assurer que le fichier `airbnb_enrichi.csv` est présent dans le dossier `data/`."
        )
        return
    
    # Filtrer les données avec coordonnées valides
    df_clean = df.dropna(subset=["latitude", "longitude", "price"]).copy()
    
    # ── Sidebar - Filtres ──────────────────────────────────────────────────
    st.sidebar.header("🔎 Filtres")
    
    # Filtre sur le prix
    if "price" in df_clean.columns:
        min_price = float(df_clean["price"].min())
        max_price = float(df_clean["price"].max())
        
        price_range = st.sidebar.slider(
            "Intervalle de prix (€)",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price)
        )
        
        df_filtered = df_clean[
            (df_clean["price"] >= price_range[0]) &
            (df_clean["price"] <= price_range[1])
        ].copy()
    else:
        df_filtered = df_clean.copy()
    
    # Filtre sur le type de logement
    if "room_type" in df_filtered.columns:
        room_types = ["Tous"] + sorted(df_filtered["room_type"].dropna().astype(str).unique().tolist())
        selected_room_type = st.sidebar.selectbox("Type de logement", room_types)
        
        if selected_room_type != "Tous":
            df_filtered = df_filtered[df_filtered["room_type"].astype(str) == selected_room_type]
    
    # Filtre sur l'arrondissement
    if "arrondissement" in df_filtered.columns:
        arrondissements_list = ["Tous"] + sorted(df_filtered["arrondissement"].dropna().astype(str).unique().tolist())
        selected_arr = st.sidebar.selectbox("Arrondissement", arrondissements_list)
        
        if selected_arr != "Tous":
            df_filtered = df_filtered[df_filtered["arrondissement"].astype(str) == selected_arr]
    
    # ── KPIs ──────────────────────────────────────────────────────────────
    st.markdown(
        f"<h3 style='color:{TEAL};margin-top:0.5em;'>📌 Indicateurs clés</h3>",
        unsafe_allow_html=True
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    nb_annonces = len(df_filtered)
    prix_moyen = df_filtered["price"].mean() if "price" in df_filtered.columns else 0
    nb_arr = df_filtered["arrondissement"].nunique() if "arrondissement" in df_filtered.columns else 0
    pct_geo = (len(df_filtered) / len(df) * 100) if len(df) > 0 else 0
    
    with col1:
        st.markdown(
            _kpi_card("Annonces", f"{nb_annonces:,}".replace(",", " "), "🏠", TEAL),
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            _kpi_card("Prix moyen", f"{prix_moyen:.0f} €", "💰", GOLD),
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            _kpi_card("Arrondissements", f"{nb_arr}", "📍", BRICK),
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            _kpi_card("Géolocalisés", f"{pct_geo:.0f}%", "🗺️", SAGE),
            unsafe_allow_html=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ── Onglets ────────────────────────────────────────────────────────────
    tab_points, tab_choropleth, tab_stats = st.tabs([
        "📍 Carte des points",
        "🗺️ Carte par arrondissement",
        "📊 Statistiques"
    ])
    
    # ── Onglet 1 : Carte des points ────────────────────────────────────────
    with tab_points:
        st.markdown(
            f"<h3 style='color:{TEAL};margin-top:0.5em;'>Carte interactive des annonces</h3>",
            unsafe_allow_html=True
        )
        
        st.caption("🔵 Prix < 50€  |  🔵 Prix 50-100€  |  🟠 Prix 100-150€  |  🔴 Prix > 150€")
        
        # Slider pour le nombre de points
        sample_size = st.slider(
            "Nombre d'annonces à afficher",
            min_value=100,
            max_value=min(5000, len(df_filtered)),
            value=min(1000, len(df_filtered)),
            step=100,
            help="Afficher trop de points peut ralentir la carte"
        )
        
        if len(df_filtered) > 0:
            m_points = _create_points_map(df_filtered, sample_size=sample_size)
            st_folium(m_points, width=None, height=600)
            
            st.info(
                f"💡 **Astuce** : Cliquez sur les clusters pour zoomer. "
                f"Affichage de {min(sample_size, len(df_filtered)):,} annonces sur {len(df_filtered):,} disponibles."
            )
        else:
            st.warning("Aucune annonce disponible avec ces filtres.")
    
    # ── Onglet 2 : Carte choroplèthe ───────────────────────────────────────
    with tab_choropleth:
        st.markdown(
            f"<h3 style='color:{TEAL};margin-top:0.5em;'>Analyse par arrondissement</h3>",
            unsafe_allow_html=True
        )
        
        st.caption(
            "Carte choroplèthe avec 4 métriques : nombre d'annonces, prix moyen, note moyenne, % logements entiers"
        )
        
        # Chargement des arrondissements
        arrondissements = _load_arrondissements()
        
        if arrondissements is not None:
            # Calcul des statistiques
            arrondissements_stats = _compute_arrondissement_stats(df_filtered, arrondissements)
            
            # Créer la carte
            m_choropleth = _create_choropleth_map(arrondissements_stats)
            st_folium(m_choropleth, width=None, height=600)
            
            st.info(
                "💡 **Astuce** : Utilisez le sélecteur de couches en haut à droite pour changer de métrique. "
                "Survolez les arrondissements pour voir les détails."
            )
            
            # Afficher le tableau des statistiques
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"<h4 style='color:{TEAL};'>📋 Statistiques par arrondissement</h4>",
                unsafe_allow_html=True
            )
            
            stats_df = arrondissements_stats.drop(columns=["geometry"])
            stats_df = stats_df.sort_values("nb_annonces", ascending=False)
            st.dataframe(stats_df, use_container_width=True, hide_index=True)
        else:
            st.error(
                "❌ Impossible de charger les contours des arrondissements de Paris. "
                "Vérifiez votre connexion internet."
            )
    
    # ── Onglet 3 : Statistiques ────────────────────────────────────────────
    with tab_stats:
        st.markdown(
            f"<h3 style='color:{TEAL};margin-top:0.5em;'>Analyse statistique par arrondissement</h3>",
            unsafe_allow_html=True
        )
        
        if "arrondissement" in df_filtered.columns:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.altair_chart(_chart_arrondissement(df_filtered), use_container_width=True)
            
            with col_chart2:
                st.altair_chart(_chart_price_arrondissement(df_filtered), use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Tableau récapitulatif
            st.markdown(
                f"<h4 style='color:{TEAL};margin-top:1em;'>📋 Tableau récapitulatif</h4>",
                unsafe_allow_html=True
            )
            
            summary = (
                df_filtered.groupby("arrondissement")
                .agg({
                    "listing_id": "count",
                    "price": ["mean", "median", "min", "max"],
                    "review_scores_rating": "mean"
                })
                .reset_index()
            )
            
            summary.columns = [
                "Arrondissement",
                "Nb annonces",
                "Prix moyen",
                "Prix médian",
                "Prix min",
                "Prix max",
                "Note moyenne"
            ]
            
            summary = summary.sort_values("Nb annonces", ascending=False)
            
            st.dataframe(
                summary.style.format({
                    "Nb annonces": "{:,.0f}",
                    "Prix moyen": "{:.2f} €",
                    "Prix médian": "{:.2f} €",
                    "Prix min": "{:.2f} €",
                    "Prix max": "{:.2f} €",
                    "Note moyenne": "{:.2f}/5"
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("Données d'arrondissement non disponibles.")
