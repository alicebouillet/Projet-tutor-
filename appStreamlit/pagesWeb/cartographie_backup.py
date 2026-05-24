import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk
from pathlib import Path

# ── Palette ───────────────────────────────────────────────────────────────
TEAL        = "#C7EFCF"
TEAL_LIGHT  = "#E3F7E8"
SAGE        = "#FFCCBA"
DARK        = "#010221"
GOLD        = "#F0B67F"
BRICK       = "#FE5F55"
ORANGE      = "#F3986D"

SAGE_SHADES = ["#FFCCBA", "#FFDBCF", "#FFE8DF", "#FFF5F0"]

# ── Chemins ───────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_FILE = DATA_DIR / "airbnb_enrichi.csv"

# ── Couleurs par gravité ──────────────────────────────────────────────────
GRAV_LABELS = {1: "Indemne", 2: "Tué", 3: "Hospitalisé", 4: "Blessé léger"}
GRAV_COLORS_RGBA = {
    1: [242, 242, 242, 160],  # SAGE
    2: [250,  89,  94, 210],  # BRICK
    3: [242, 159,   5, 210],  # GOLD
    4: [ 62, 154, 157, 180],  # TEAL
}

# ── Types de colonnes ─────────────────────────────────────────────────────
DTYPE_STR = {
    "Num_Acc": "str", "dep": "str", "com": "str",
    "id_usager": "str", "id_vehicule": "str",
    "hrmn": "str", "actp": "str",
    "voie": "str", "v1": "str", "v2": "str",
    "pr": "str", "pr1": "str", "larrout": "str", "gps": "str",
}

# ── Correspondance département → région ───────────────────────────────────
DEP_TO_REGION = {
    "01": "Auvergne-Rhône-Alpes", "03": "Auvergne-Rhône-Alpes", "07": "Auvergne-Rhône-Alpes",
    "15": "Auvergne-Rhône-Alpes", "26": "Auvergne-Rhône-Alpes", "38": "Auvergne-Rhône-Alpes",
    "42": "Auvergne-Rhône-Alpes", "43": "Auvergne-Rhône-Alpes", "63": "Auvergne-Rhône-Alpes",
    "69": "Auvergne-Rhône-Alpes", "73": "Auvergne-Rhône-Alpes", "74": "Auvergne-Rhône-Alpes",
    "21": "Bourgogne-Franche-Comté", "25": "Bourgogne-Franche-Comté", "39": "Bourgogne-Franche-Comté",
    "58": "Bourgogne-Franche-Comté", "70": "Bourgogne-Franche-Comté", "71": "Bourgogne-Franche-Comté",
    "89": "Bourgogne-Franche-Comté", "90": "Bourgogne-Franche-Comté",
    "22": "Bretagne", "29": "Bretagne", "35": "Bretagne", "56": "Bretagne",
    "18": "Centre-Val de Loire", "28": "Centre-Val de Loire", "36": "Centre-Val de Loire",
    "37": "Centre-Val de Loire", "41": "Centre-Val de Loire", "45": "Centre-Val de Loire",
    "2A": "Corse", "2B": "Corse", "20": "Corse",
    "08": "Grand Est", "10": "Grand Est", "51": "Grand Est", "52": "Grand Est",
    "54": "Grand Est", "55": "Grand Est", "57": "Grand Est", "67": "Grand Est",
    "68": "Grand Est", "88": "Grand Est",
    "02": "Hauts-de-France", "59": "Hauts-de-France", "60": "Hauts-de-France",
    "62": "Hauts-de-France", "80": "Hauts-de-France",
    "75": "Île-de-France", "77": "Île-de-France", "78": "Île-de-France",
    "91": "Île-de-France", "92": "Île-de-France", "93": "Île-de-France",
    "94": "Île-de-France", "95": "Île-de-France",
    "14": "Normandie", "27": "Normandie", "50": "Normandie", "61": "Normandie", "76": "Normandie",
    "16": "Nouvelle-Aquitaine", "17": "Nouvelle-Aquitaine", "19": "Nouvelle-Aquitaine",
    "23": "Nouvelle-Aquitaine", "24": "Nouvelle-Aquitaine", "33": "Nouvelle-Aquitaine",
    "40": "Nouvelle-Aquitaine", "47": "Nouvelle-Aquitaine", "64": "Nouvelle-Aquitaine",
    "79": "Nouvelle-Aquitaine", "86": "Nouvelle-Aquitaine", "87": "Nouvelle-Aquitaine",
    "09": "Occitanie", "11": "Occitanie", "12": "Occitanie", "30": "Occitanie",
    "31": "Occitanie", "32": "Occitanie", "34": "Occitanie", "46": "Occitanie",
    "48": "Occitanie", "65": "Occitanie", "66": "Occitanie", "81": "Occitanie", "82": "Occitanie",
    "44": "Pays de la Loire", "49": "Pays de la Loire", "53": "Pays de la Loire",
    "72": "Pays de la Loire", "85": "Pays de la Loire",
    "04": "Provence-Alpes-Côte d'Azur", "05": "Provence-Alpes-Côte d'Azur",
    "06": "Provence-Alpes-Côte d'Azur", "13": "Provence-Alpes-Côte d'Azur",
    "83": "Provence-Alpes-Côte d'Azur", "84": "Provence-Alpes-Côte d'Azur",
    "971": "Guadeloupe", "972": "Martinique", "973": "Guyane", "974": "La Réunion", "976": "Mayotte",
}


# ── Chargement des données ────────────────────────────────────────────────
@st.cache_data(show_spinner="Chargement des données géographiques…")
def _load_geo() -> pd.DataFrame | None:
    """Charge les données du fichier airbnb_enrichi.csv."""
    if not DATA_FILE.exists():
        return None
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig", low_memory=False)
    df["lat"]  = pd.to_numeric(df["lat"],  errors="coerce")
    df["long"] = pd.to_numeric(df["long"], errors="coerce")
    
    # Ajout de la région
    df["region"] = df["dep"].map(DEP_TO_REGION).fillna("Autre")
    
    return df


@st.cache_data(show_spinner="Chargement des données temporelles…")
def _load_temporal() -> pd.DataFrame | None:
    """Charge les données temporelles du fichier airbnb_enrichi.csv."""
    if not DATA_FILE.exists():
        return None
    df = pd.read_csv(DATA_FILE, encoding="utf-8-sig", low_memory=False)
    # Ajout de la région si la colonne dep existe
    if "dep" in df.columns:
        df["region"] = df["dep"].map(DEP_TO_REGION).fillna("Autre")
    return df


# ── Carte PyDeck ──────────────────────────────────────────────────────────
def _pydeck_map(df: pd.DataFrame, radius: int = 800) -> pdk.Deck:
    df = df.dropna(subset=["lat", "long"]).copy()
    _default = [150, 150, 150, 160]
    df["color"] = df["grav"].map(GRAV_COLORS_RGBA).apply(
        lambda x: x if isinstance(x, list) else _default
    )
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["long", "lat"],
        get_color="color",
        get_radius=radius,
        pickable=True,
    )
    view = pdk.ViewState(latitude=46.5, longitude=2.3, zoom=5, pitch=0)
    tooltip = {
        "html": "<b>Dept :</b> {dep}<br/><b>Gravité :</b> {grav}<br/><b>Année :</b> {an}",
        "style": {"backgroundColor": "#010221", "color": "#FFCCBA"},
    }
    return pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    )


def _pydeck_heatmap(df: pd.DataFrame) -> pdk.Deck:
    """Carte de chaleur des accidents."""
    df = df.dropna(subset=["lat", "long"]).copy()
    
    layer = pdk.Layer(
        "HeatmapLayer",
        data=df,
        get_position=["long", "lat"],
        aggregation="SUM",
        get_weight=1,
        radius_pixels=50,
        intensity=1,
        threshold=0.05,
    )
    view = pdk.ViewState(latitude=46.5, longitude=2.3, zoom=5, pitch=0)
    return pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    )


# ── Graphiques Altair ─────────────────────────────────────────────────────
def _chart_dep(df: pd.DataFrame, top_n: int = 20) -> alt.Chart:
    """Classement des départements par nombre d'accidents."""
    counts = (
        df.groupby("dep")["Num_Acc"]
        .nunique()
        .reset_index(name="accidents")
        .sort_values("accidents", ascending=False)
        .head(top_n)
    )
    return (
        alt.Chart(counts)
        .mark_bar(color=TEAL)
        .encode(
            x=alt.X("accidents:Q", title="Nombre d'accidents"),
            y=alt.Y("dep:N", sort="-x", title="Département"),
            tooltip=[
                alt.Tooltip("dep:N",        title="Département"),
                alt.Tooltip("accidents:Q",  title="Nb accidents", format=","),
            ],
        )
        .properties(height=500, title=f"Top {top_n} départements par nombre d'accidents")
    )


def _chart_region(df: pd.DataFrame) -> alt.Chart:
    """Classement des régions par nombre d'accidents."""
    counts = (
        df.groupby("region")["Num_Acc"]
        .nunique()
        .reset_index(name="accidents")
        .sort_values("accidents", ascending=False)
    )
    return (
        alt.Chart(counts)
        .mark_bar(color=GOLD)
        .encode(
            x=alt.X("accidents:Q", title="Nombre d'accidents"),
            y=alt.Y("region:N", sort="-x", title="Région"),
            tooltip=[
                alt.Tooltip("region:N",     title="Région"),
                alt.Tooltip("accidents:Q",  title="Nb accidents", format=","),
            ],
        )
        .properties(height=400, title="Répartition par région")
    )


def _chart_heatmap_temporal(df: pd.DataFrame) -> alt.Chart:
    """Heatmap année × mois pour les accidents."""
    df = df[df["mois"].notna()].copy()
    counts = (
        df.groupby(["an", "mois"])["Num_Acc"]
        .nunique()
        .reset_index(name="accidents")
    )
    counts["an"] = counts["an"].astype(int)
    counts["mois"] = counts["mois"].astype(int)
    
    # Noms des mois
    mois_labels = {
        1: "Jan", 2: "Fév", 3: "Mar", 4: "Avr", 5: "Mai", 6: "Juin",
        7: "Juil", 8: "Août", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Déc"
    }
    counts["mois_nom"] = counts["mois"].map(mois_labels)
    
    return (
        alt.Chart(counts)
        .mark_rect()
        .encode(
            x=alt.X("an:O", title="Année"),
            y=alt.Y("mois_nom:N", title="Mois", sort=list(mois_labels.values())),
            color=alt.Color(
                "accidents:Q",
                scale=alt.Scale(scheme="teals"),
                legend=alt.Legend(title="Nb accidents")
            ),
            tooltip=[
                alt.Tooltip("an:O",          title="Année"),
                alt.Tooltip("mois_nom:N",    title="Mois"),
                alt.Tooltip("accidents:Q",   title="Nb accidents", format=","),
            ],
        )
        .properties(
            height=300,
            title="Distribution temporelle des accidents (heatmap année × mois)"
        )
    )


def _chart_grav_by_region(df: pd.DataFrame) -> alt.Chart:
    """Répartition de la gravité par région."""
    df = df[df["grav"].isin([1, 2, 3, 4])].copy()
    df["grav_label"] = df["grav"].map(GRAV_LABELS)
    
    counts = (
        df.groupby(["region", "grav_label"])["Num_Acc"]
        .nunique()
        .reset_index(name="accidents")
    )
    
    color_scale = alt.Scale(
        domain=["Indemne", "Blessé léger", "Hospitalisé", "Tué"],
        range=["rgb(242,242,242)", "rgb(62,154,157)", "rgb(242,159,5)", "rgb(250,89,94)"],
    )
    
    return (
        alt.Chart(counts)
        .mark_bar()
        .encode(
            x=alt.X("accidents:Q", title="Nombre d'accidents", stack="normalize"),
            y=alt.Y("region:N", sort="-x", title="Région"),
            color=alt.Color(
                "grav_label:N",
                scale=color_scale,
                legend=alt.Legend(title="Gravité")
            ),
            tooltip=[
                alt.Tooltip("region:N",      title="Région"),
                alt.Tooltip("grav_label:N",  title="Gravité"),
                alt.Tooltip("accidents:Q",   title="Nb accidents", format=","),
            ],
        )
        .properties(
            height=400,
            title="Répartition de la gravité par région (proportions)"
        )
    )


# ── KPI card ──────────────────────────────────────────────────────────────
def _kpi_card(label: str, value: int | float, unit: str = "") -> str:
    return f"""
    <div style="
        background:{TEAL};border-radius:12px;padding:1.5em 1em;
        text-align:center;height:100%;
    ">
        <div style="color:{SAGE};font-size:0.85em;font-weight:600;margin-bottom:0.6em;">
            {label}
        </div>
        <div style="color:{GOLD};font-size:2.5em;font-weight:700;line-height:1.1;">
            {value:,}
        </div>
        <div style="color:{SAGE};font-size:0.75em;margin-top:0.4em;">
            {unit}
        </div>
    </div>
    """


# ── Point d'entrée ────────────────────────────────────────────────────────
def app():
    """Page principale de cartographie des accidents."""
    
    # ── En-tête ───────────────────────────────────────────────────────────
    st.markdown(
        """
        <h1 style="text-align:center; color:#C7EFCF;">🗺️ Cartographie des accidents</h1>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <h3 style="text-align:center; color:#FFCCBA; background-color:#C7EFCF; padding: 0.5em 0; border-radius: 8px;">
        Visualisation géographique des accidents de la route en France
        </h3>
        """,
        unsafe_allow_html=True
    )
    
    st.divider()
    
    # ── Chargement des données ────────────────────────────────────────────
    df_geo = _load_geo()
    if df_geo is None:
        st.error(
            "Le fichier `airbnb_enrichi.csv` est introuvable dans le dossier `data/`. "
            "Vérifiez que le fichier existe."
        )
        return
    
    # ── Panneau de filtres ────────────────────────────────────────────────
    st.markdown(f"<h3 style='color:{TEAL};'>🔍 Filtres de sélection</h3>", unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        annees_dispo = sorted(df_geo["an"].dropna().unique().astype(int).tolist())
        annee_sel = st.selectbox(
            "📅 Année",
            ["Toutes"] + annees_dispo,
            index=0
        )
    
    with col_f2:
        grav_opts = {f"{k} – {GRAV_LABELS[k]}": k for k in sorted(GRAV_LABELS)}
        grav_sel = st.multiselect(
            "⚠️ Gravité",
            options=list(grav_opts.keys()),
            default=["2 – Tué", "3 – Hospitalisé"],
        )
    
    with col_f3:
        regions_dispo = sorted(df_geo["region"].unique().tolist())
        region_sel = st.multiselect(
            "🌍 Région",
            options=regions_dispo,
            default=[],
        )
    
    # ── Application des filtres ───────────────────────────────────────────
    df_filtered = df_geo.copy()
    
    if annee_sel != "Toutes":
        df_filtered = df_filtered[df_filtered["an"] == annee_sel]
    
    if grav_sel:
        codes = [grav_opts[g] for g in grav_sel]
        df_filtered = df_filtered[df_filtered["grav"].isin(codes)]
    
    if region_sel:
        df_filtered = df_filtered[df_filtered["region"].isin(region_sel)]
    
    # ── KPIs ──────────────────────────────────────────────────────────────
    st.divider()
    
    nb_accidents = len(df_filtered)
    nb_deps = df_filtered["dep"].nunique()
    nb_regions = df_filtered["region"].nunique()
    has_coords = df_filtered[["lat", "long"]].notna().all(axis=1).sum()
    
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        st.markdown(_kpi_card("Accidents", nb_accidents, "entrées"), unsafe_allow_html=True)
    with kpi_cols[1]:
        st.markdown(_kpi_card("Départements", nb_deps, "uniques"), unsafe_allow_html=True)
    with kpi_cols[2]:
        st.markdown(_kpi_card("Régions", nb_regions, "couvertes"), unsafe_allow_html=True)
    with kpi_cols[3]:
        pct_coords = (has_coords / nb_accidents * 100) if nb_accidents > 0 else 0
        st.markdown(_kpi_card("Géolocalisés", int(pct_coords), "%"), unsafe_allow_html=True)
    
    st.divider()
    
    # ── Onglets de visualisation ──────────────────────────────────────────
    tab_map, tab_heat, tab_stats = st.tabs([
        "🗺️ Carte interactive",
        "🔥 Carte de chaleur",
        "📊 Statistiques géographiques"
    ])
    
    # ────────────────────────────────────────────────────────────────────
    # Onglet 1 : Carte interactive
    # ────────────────────────────────────────────────────────────────────
    with tab_map:
        st.markdown(f"<h3 style='color:{TEAL};margin-top:0.5em;'>Carte interactive des accidents</h3>", unsafe_allow_html=True)
        
        has_coords_data = df_filtered[["lat", "long"]].notna().all(axis=1).any()
        if not has_coords_data:
            st.warning(
                "⚠️ Coordonnées GPS absentes pour cette sélection. "
                "Relancez `scoring_accident/dev/chargement_donnee.py`."
            )
        else:
            # Légende des couleurs
            legend_html = "".join(
                f"<span style='display:inline-block;width:14px;height:14px;"
                f"background:rgb({r},{g},{b});border-radius:50%;margin-right:6px;'></span>"
                f"<span style='margin-right:20px;font-size:0.9em;color:{DARK};'>{GRAV_LABELS[k]}</span>"
                for k, (r, g, b, _) in GRAV_COLORS_RGBA.items()
            )
            st.markdown(
                f"<div style='margin-bottom:1em;padding:0.8em;background-color:#FFFFFF;border:2px solid {TEAL};border-radius:8px;'>"
                f"<b style='color:{TEAL};'>Légende :</b> {legend_html}</div>",
                unsafe_allow_html=True,
            )
            
            # Échantillonnage si trop de points
            sample = df_filtered.dropna(subset=["lat", "long"])
            if len(sample) > 50_000:
                st.info(f"📌 Affichage d'un échantillon de 50 000 accidents (sur {len(sample):,} disponibles)")
                sample = sample.sample(50_000, random_state=42)
            else:
                st.caption(f"📌 Affichage de {len(sample):,} accidents géolocalisés")
            
            # Slider pour ajuster la taille des points
            radius = st.slider(
                "Taille des points sur la carte",
                min_value=200,
                max_value=2000,
                value=800,
                step=100,
                help="Ajustez la taille des points pour une meilleure visualisation"
            )
            
            st.pydeck_chart(_pydeck_map(sample, radius=radius), use_container_width=True)
    
    # ────────────────────────────────────────────────────────────────────
    # Onglet 2 : Carte de chaleur
    # ────────────────────────────────────────────────────────────────────
    with tab_heat:
        st.markdown(f"<h3 style='color:{TEAL};margin-top:0.5em;'>Carte de chaleur (heatmap)</h3>", unsafe_allow_html=True)
        st.caption("Visualisation de la densité d'accidents par zone géographique")
        
        has_coords_data = df_filtered[["lat", "long"]].notna().all(axis=1).any()
        if not has_coords_data:
            st.warning("⚠️ Coordonnées GPS absentes pour cette sélection.")
        else:
            sample_heat = df_filtered.dropna(subset=["lat", "long"])
            if len(sample_heat) > 100_000:
                st.info(f"📌 Échantillon de 100 000 accidents (sur {len(sample_heat):,} disponibles)")
                sample_heat = sample_heat.sample(100_000, random_state=42)
            else:
                st.caption(f"📌 {len(sample_heat):,} accidents géolocalisés")
            
            st.pydeck_chart(_pydeck_heatmap(sample_heat), use_container_width=True)
            
            st.info(
                "💡 **Interprétation :** Les zones rouges/oranges indiquent une forte concentration d'accidents. "
                "Cette visualisation permet d'identifier les points chauds du territoire."
            )
    
    # ────────────────────────────────────────────────────────────────────
    # Onglet 3 : Statistiques géographiques
    # ────────────────────────────────────────────────────────────────────
    with tab_stats:
        st.markdown(f"<h3 style='color:{TEAL};margin-top:0.5em;'>Analyse statistique par territoire</h3>", unsafe_allow_html=True)
        
        # ── Classements ───────────────────────────────────────────────────
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown(f"<h4 style='color:{TEAL};'>Par département</h4>", unsafe_allow_html=True)
            top_n = st.slider("Nombre de départements à afficher", 5, 50, 20, 5, key="slider_dep")
            st.altair_chart(_chart_dep(df_filtered, top_n=top_n), use_container_width=True)
        
        with col_chart2:
            st.markdown(f"<h4 style='color:{TEAL};'>Par région</h4>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)  # alignement
            st.altair_chart(_chart_region(df_filtered), use_container_width=True)
        
        st.divider()
        
        # ── Gravité par région ────────────────────────────────────────────
        st.markdown(f"<h4 style='color:{TEAL};margin-top:1em;'>Répartition de la gravité par région</h4>", unsafe_allow_html=True)
        st.altair_chart(_chart_grav_by_region(df_filtered), use_container_width=True)
        
        st.divider()
        
        # ── Temporel ──────────────────────────────────────────────────────
        st.markdown(f"<h4 style='color:{TEAL};margin-top:1em;'>Distribution temporelle</h4>", unsafe_allow_html=True)
        
        df_temporal = _load_temporal()
        if df_temporal is not None:
            # Appliquer les mêmes filtres
            df_temp_filtered = df_temporal.copy()
            if annee_sel != "Toutes":
                df_temp_filtered = df_temp_filtered[df_temp_filtered["an"] == annee_sel]
            if grav_sel:
                codes = [grav_opts[g] for g in grav_sel]
                df_temp_filtered = df_temp_filtered[df_temp_filtered["grav"].isin(codes)]
            if region_sel:
                df_temp_filtered = df_temp_filtered[df_temp_filtered["region"].isin(region_sel)]
            
            st.altair_chart(_chart_heatmap_temporal(df_temp_filtered), use_container_width=True)
        else:
            st.warning("Données temporelles non disponibles.")
        
        st.divider()
        
        # ── Tableau récapitulatif ─────────────────────────────────────────
        st.markdown(f"<h4 style='color:{TEAL};margin-top:1em;'>📋 Tableau récapitulatif par région</h4>", unsafe_allow_html=True)
        
        summary = (
            df_filtered.groupby("region")
            .agg({
                "Num_Acc": "nunique",
                "dep": "nunique",
            })
            .reset_index()
            .rename(columns={
                "region": "Région",
                "Num_Acc": "Nombre d'accidents",
                "dep": "Départements couverts"
            })
            .sort_values("Nombre d'accidents", ascending=False)
        )
        
        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Région": st.column_config.TextColumn("Région", width="medium"),
                "Nombre d'accidents": st.column_config.NumberColumn(
                    "Nombre d'accidents",
                    format="%d"
                ),
                "Départements couverts": st.column_config.NumberColumn(
                    "Départements couverts",
                    format="%d"
                ),
            }
        )
    
    st.divider()
    
    # ── Footer ────────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style='text-align:center; padding:1em; color:{SAGE}; font-size:0.85em;'>
        💡 Les données affichées sont issues de la base BAAC (2019-2024)<br>
        Survolez les graphiques et la carte pour plus d'informations détaillées
        </div>
        """,
        unsafe_allow_html=True
    )
