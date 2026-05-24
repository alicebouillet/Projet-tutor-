import streamlit as st
import pandas as pd
import altair as alt
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
# analyseDonnee.py → pagesWeb/ → appStreamlit/ → Projet-tutor- → data/
DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_FILE = DATA_DIR / "airbnb_enrichi.csv"

# ── Couleurs par gravité ──────────────────────────────────────────────────
# grav : 1=indemne, 2=tué, 3=hospitalisé, 4=blessé léger
GRAV_LABELS = {1: "Indemne", 2: "Tué", 3: "Hospitalisé", 4: "Blessé léger"}
GRAV_COLORS_RGBA = {
    1: [242, 242, 242, 160],
    2: [250,  89,  94, 210],
    3: [242, 159,   5, 210],
    4: [ 62, 154, 157, 180],
}

# ── Colonnes par table BAAC d'origine ────────────────────────────────────
COLS_BAAC = {
    "Caractéristiques": [
        "lum", "agg", "int", "atm", "col",
        "an", "mois", "jour", "hrmn", "dep", "com", "lat", "long",
    ],
    "Lieux": [
        "catr", "circ", "nbv", "vosp", "prof",
        "plan", "surf", "infra", "situ", "vma",
    ],
    "Véhicules": [
        # occutc exclu : toujours vide après filtre catv==7 (VL ≠ TC)
        "catv", "obs", "obsm", "choc", "manv", "motor",
    ],
    "Usagers": [
        "catu", "grav", "sexe", "trajet", "locp",
        "actp", "secu1", "secu2", "secu3", "an_nais", "place",
    ],
}

# ── Dictionnaire des variables ────────────────────────────────────────────
DICT_BAAC = {
    "Caractéristiques": [
        {"variable": "an",   "type": "int",   "définition": "Année de l'accident"},
        {"variable": "mois", "type": "int",   "définition": "Mois de l'accident"},
        {"variable": "jour", "type": "int",   "définition": "Jour de la semaine"},
        {"variable": "hrmn", "type": "str",   "définition": "Heure et minute (HHMM)"},
        {"variable": "lum",  "type": "int",   "définition": "Conditions d'éclairage"},
        {"variable": "agg",  "type": "int",   "définition": "Localisation en agglomération"},
        {"variable": "int",  "type": "int",   "définition": "Type d'intersection"},
        {"variable": "atm",  "type": "int",   "définition": "Conditions atmosphériques"},
        {"variable": "col",  "type": "int",   "définition": "Type de collision"},
        {"variable": "dep",  "type": "str",   "définition": "Code département (INSEE)"},
        {"variable": "com",  "type": "str",   "définition": "Code commune (INSEE)"},
        {"variable": "lat",  "type": "float", "définition": "Latitude (WGS84)"},
        {"variable": "long", "type": "float", "définition": "Longitude (WGS84)"},
    ],
    "Lieux": [
        {"variable": "catr",  "type": "int", "définition": "Catégorie de route"},
        {"variable": "circ",  "type": "int", "définition": "Régime de circulation"},
        {"variable": "nbv",   "type": "int", "définition": "Nombre de voies"},
        {"variable": "vosp",  "type": "int", "définition": "Présence d'une voie réservée"},
        {"variable": "prof",  "type": "int", "définition": "Profil en long de la route"},
        {"variable": "plan",  "type": "int", "définition": "Tracé en plan"},
        {"variable": "surf",  "type": "int", "définition": "État de la surface"},
        {"variable": "infra", "type": "int", "définition": "Aménagement de l'infrastructure"},
        {"variable": "situ",  "type": "int", "définition": "Situation de l'accident sur la route"},
        {"variable": "vma",   "type": "int", "définition": "Vitesse maximale autorisée (km/h)"},
    ],
    "Véhicules": [
        {"variable": "catv",   "type": "int", "définition": "Catégorie du véhicule"},
        {"variable": "obs",    "type": "int", "définition": "Obstacle fixe heurté"},
        {"variable": "obsm",   "type": "int", "définition": "Obstacle mobile heurté"},
        {"variable": "choc",   "type": "int", "définition": "Point de choc initial"},
        {"variable": "manv",   "type": "int", "définition": "Manœuvre principale avant l'accident"},
        {"variable": "motor",  "type": "int", "définition": "Type de motorisation"},
    ],
    "Usagers": [
        {"variable": "catu",    "type": "int",   "définition": "Catégorie d'usager"},
        {"variable": "grav",    "type": "int",   "définition": "Gravité de la blessure"},
        {"variable": "sexe",    "type": "int",   "définition": "Sexe de l'usager"},
        {"variable": "an_nais", "type": "float", "définition": "Année de naissance"},
        {"variable": "trajet",  "type": "int",   "définition": "Motif du déplacement"},
        {"variable": "secu1",   "type": "int",   "définition": "Équipement de sécurité 1"},
        {"variable": "secu2",   "type": "int",   "définition": "Équipement de sécurité 2"},
        {"variable": "secu3",   "type": "int",   "définition": "Équipement de sécurité 3"},
        {"variable": "locp",    "type": "int",   "définition": "Localisation du piéton"},
        {"variable": "actp",    "type": "str",   "définition": "Action du piéton"},
        {"variable": "place",   "type": "int",   "définition": "Place occupée dans le véhicule"},
    ],
}

# Colonnes à forcer en str lors du read_csv (cf. _utils.obtenir_types_lecture_csv)
DTYPE_STR = {
    "Num_Acc": "str", "dep": "str", "com": "str",
    "id_usager": "str", "id_vehicule": "str",
    "hrmn": "str", "actp": "str",
    "voie": "str", "v1": "str", "v2": "str",
    "pr": "str", "pr1": "str", "larrout": "str", "gps": "str",
}


# ── Chargement des données ────────────────────────────────────────────────
@st.cache_data(show_spinner="Chargement des données…")
def _load_light() -> pd.DataFrame | None:
    """Charge les colonnes de base du fichier airbnb_enrichi.csv."""
    if not DATA_FILE.exists():
        return None
    return pd.read_csv(DATA_FILE, encoding="utf-8-sig", low_memory=False)


@st.cache_data(show_spinner="Chargement des données qualitatives…")
def _load_for_nulls() -> pd.DataFrame | None:
    """Charge toutes les colonnes du fichier airbnb_enrichi.csv."""
    if not DATA_FILE.exists():
        return None
    return pd.read_csv(DATA_FILE, encoding="utf-8-sig", low_memory=False)


# ── Calculs ───────────────────────────────────────────────────────────────
def _compute_kpis(df: pd.DataFrame) -> dict:
    """Calcule les KPIs de base sur les données."""
    return {
        "Total": {
            "n_usagers": len(df),
            "n_accidents": len(df),
        }
    }


def _compute_temporal(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la répartition temporelle (fonction à adapter selon les données Airbnb)."""
    # TODO: Adapter cette fonction aux colonnes du dataset Airbnb
    return pd.DataFrame()


def _compute_completeness(df: pd.DataFrame) -> dict:
    result = {}
    for table, cols in COLS_BAAC.items():
        existing = [c for c in cols if c in df.columns]
        comp = (
            (1 - df[existing].isnull().mean())
            .mul(100)
            .round(1)
            .reset_index()
        )
        comp.columns = ["variable", "completude"]
        comp = comp.sort_values("completude")   # pire en haut du graphique
        result[table] = comp
    return result


# ── Graphiques Altair ─────────────────────────────────────────────────────
def _chart_temporal(df: pd.DataFrame) -> alt.Chart:
    color_scale = alt.Scale(
        domain=["Grave (Tué / Hosp.)", "Non grave (Léger / Indemne)"],
        range=[BRICK, TEAL],
    )
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("an:O", title="Année"),
            y=alt.Y(
                "proportion:Q",
                stack="normalize",
                axis=alt.Axis(format="%", title="Proportion"),
            ),
            color=alt.Color(
                "categorie:N",
                scale=color_scale,
                legend=alt.Legend(title=None, orient="bottom"),
            ),
            tooltip=[
                alt.Tooltip("an:O",          title="Année"),
                alt.Tooltip("categorie:N",   title="Catégorie"),
                alt.Tooltip("nb:Q",          title="Nb usagers", format=","),
                alt.Tooltip("proportion:Q",  title="Proportion", format=".1%"),
            ],
        )
        .properties(
            height=380,
            title="Évolution de la gravité des accidents (VL – toutes personnes impliquées)",
        )
    )


_BAR_SIZE     = 22   # épaisseur d'une barre (px)
_BAR_STEP     = 34   # barre + espacement
_CHART_OVERHEAD = 60 # titre + axe x


def _chart_completeness(comp_df: pd.DataFrame, color: str, title: str) -> alt.Chart:
    """comp_df doit contenir : variable, completude, type, définition."""
    height = len(comp_df) * _BAR_STEP + _CHART_OVERHEAD
    tooltip = [
        alt.Tooltip("variable:N",   title="Variable"),
        alt.Tooltip("type:N",       title="Type"),
        alt.Tooltip("définition:N", title="Définition"),
        alt.Tooltip("completude:Q", title="Complétude (%)", format=".1f"),
    ]
    return (
        alt.Chart(comp_df)
        .mark_bar(color=color, size=_BAR_SIZE)
        .encode(
            y=alt.Y("variable:N", sort="x", title=None),
            x=alt.X(
                "completude:Q",
                title="Complétude (%)",
                scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(format=".0f"),
            ),
            tooltip=tooltip,
        )
        .properties(height=height, title=title)
    )


# ── KPI card HTML ─────────────────────────────────────────────────────────
def _kpi_card(label: str, n_usagers: int, n_accidents: int) -> str:
    return f"""
    <div style="
        background:{TEAL};border-radius:12px;padding:1.2em 1em;
        text-align:center;height:100%;
    ">
        <div style="color:{SAGE};font-size:0.85em;font-weight:600;margin-bottom:0.4em;">
            {label}
        </div>
        <div style="color:{GOLD};font-size:2em;font-weight:700;line-height:1.1;">
            {n_usagers:,}
        </div>
        <div style="color:{SAGE};font-size:0.75em;margin-bottom:0.8em;">
            entrées (usagers VL)
        </div>
        <hr style="border:none;border-top:1px solid {TEAL_LIGHT};margin:0.5em 0;"/>
        <div style="color:{GOLD};font-size:1.3em;font-weight:700;">
            {n_accidents:,}
        </div>
        <div style="color:{SAGE};font-size:0.75em;">
            accidents uniques
        </div>
    </div>
    """


@st.cache_data(show_spinner="Chargement des données d'analyse…")
def _load_analysis() -> pd.DataFrame | None:
    """Charge les données du fichier airbnb_enrichi.csv pour les analyses."""
    if not DATA_FILE.exists():
        return None
    return pd.read_csv(DATA_FILE, encoding="utf-8-sig", low_memory=False)


def _compute_atm_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la distribution des accidents par conditions atmosphériques."""
    atm_labels = {
        1: "Normale",
        2: "Pluie légère",
        3: "Pluie forte",
        4: "Neige/Grêle",
        5: "Brouillard",
        6: "Vent fort",
        7: "Temps éblouissant",
        8: "Temps couvert",
        9: "Autre"
    }
    df_atm = df[df["atm"].isin(atm_labels.keys())].copy()
    counts = df_atm.groupby("atm")["Num_Acc"].nunique().reset_index(name="accidents")
    counts["label"] = counts["atm"].map(atm_labels)
    counts = counts.sort_values("accidents", ascending=False)
    return counts


def _compute_lum_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la distribution des accidents par conditions d'éclairage."""
    lum_labels = {
        1: "Plein jour",
        2: "Crépuscule/Aube",
        3: "Nuit sans éclairage",
        4: "Nuit éclairage non allumé",
        5: "Nuit éclairage allumé"
    }
    df_lum = df[df["lum"].isin(lum_labels.keys())].copy()
    counts = df_lum.groupby("lum")["Num_Acc"].nunique().reset_index(name="accidents")
    counts["label"] = counts["lum"].map(lum_labels)
    counts = counts.sort_values("accidents", ascending=False)
    return counts


def _compute_col_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la distribution des accidents par type de collision."""
    col_labels = {
        1: "Frontale",
        2: "Par l'arrière",
        3: "Par le côté",
        4: "En chaîne",
        5: "Collisions multiples",
        6: "Autre collision",
        7: "Sans collision"
    }
    df_col = df[df["col"].isin(col_labels.keys())].copy()
    counts = df_col.groupby("col")["Num_Acc"].nunique().reset_index(name="accidents")
    counts["label"] = counts["col"].map(col_labels)
    counts = counts.sort_values("accidents", ascending=False)
    return counts


def _compute_jour_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la distribution des accidents par jour de la semaine."""
    jour_labels = {
        1: "Lundi",
        2: "Mardi",
        3: "Mercredi",
        4: "Jeudi",
        5: "Vendredi",
        6: "Samedi",
        7: "Dimanche"
    }
    df_jour = df[df["jour"].isin(jour_labels.keys())].copy()
    counts = df_jour.groupby("jour")["Num_Acc"].nunique().reset_index(name="accidents")
    counts["label"] = counts["jour"].map(jour_labels)
    return counts


def _compute_mois_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule la distribution des accidents par mois."""
    mois_labels = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
        7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }
    df_mois = df[df["mois"].isin(mois_labels.keys())].copy()
    counts = df_mois.groupby("mois")["Num_Acc"].nunique().reset_index(name="accidents")
    counts["label"] = counts["mois"].map(mois_labels)
    return counts


def _compute_sexe_by_grav(df: pd.DataFrame) -> pd.DataFrame:
    """Répartition de la gravité par sexe."""
    sexe_labels = {1: "Masculin", 2: "Féminin"}
    df_clean = df[(df["sexe"].isin([1, 2])) & (df["grav"].isin([1, 2, 3, 4]))].copy()
    df_clean["sexe_label"] = df_clean["sexe"].map(sexe_labels)
    df_clean["grav_label"] = df_clean["grav"].map(GRAV_LABELS)
    
    counts = df_clean.groupby(["sexe_label", "grav_label"]).size().reset_index(name="usagers")
    return counts


def _chart_atm(df: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_bar(color=TEAL)
        .encode(
            x=alt.X("accidents:Q", title="Nombre d'accidents"),
            y=alt.Y("label:N", sort="-x", title="Conditions atmosphériques"),
            tooltip=[
                alt.Tooltip("label:N", title="Conditions"),
                alt.Tooltip("accidents:Q", title="Nb accidents", format=","),
            ],
        )
        .properties(height=300, title="Distribution par conditions atmosphériques")
    )


def _chart_lum(df: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_bar(color=GOLD)
        .encode(
            x=alt.X("accidents:Q", title="Nombre d'accidents"),
            y=alt.Y("label:N", sort="-x", title="Conditions d'éclairage"),
            tooltip=[
                alt.Tooltip("label:N", title="Éclairage"),
                alt.Tooltip("accidents:Q", title="Nb accidents", format=","),
            ],
        )
        .properties(height=250, title="Distribution par conditions d'éclairage")
    )


def _chart_col(df: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_bar(color=BRICK)
        .encode(
            x=alt.X("accidents:Q", title="Nombre d'accidents"),
            y=alt.Y("label:N", sort="-x", title="Type de collision"),
            tooltip=[
                alt.Tooltip("label:N", title="Type"),
                alt.Tooltip("accidents:Q", title="Nb accidents", format=","),
            ],
        )
        .properties(height=280, title="Distribution par type de collision")
    )


def _chart_jour(df: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_bar(color=SAGE)
        .encode(
            x=alt.X("label:N", title="Jour de la semaine", 
                    sort=["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]),
            y=alt.Y("accidents:Q", title="Nombre d'accidents"),
            tooltip=[
                alt.Tooltip("label:N", title="Jour"),
                alt.Tooltip("accidents:Q", title="Nb accidents", format=","),
            ],
        )
        .properties(height=300, title="Distribution par jour de la semaine")
    )


def _chart_mois(df: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_line(point=True, color=TEAL, strokeWidth=3)
        .encode(
            x=alt.X("mois:O", title="Mois", 
                    axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("accidents:Q", title="Nombre d'accidents"),
            tooltip=[
                alt.Tooltip("label:N", title="Mois"),
                alt.Tooltip("accidents:Q", title="Nb accidents", format=","),
            ],
        )
        .properties(height=300, title="Distribution par mois de l'année")
    )


def _chart_sexe_grav(df: pd.DataFrame) -> alt.Chart:
    color_scale = alt.Scale(
        domain=["Indemne", "Blessé léger", "Hospitalisé", "Tué"],
        range=["rgb(183,191,153)", "rgb(10,115,115)", "rgb(237,170,37)", "rgb(196,51,2)"],
    )
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("usagers:Q", title="Nombre d'usagers", stack="normalize"),
            y=alt.Y("sexe_label:N", title="Sexe"),
            color=alt.Color("grav_label:N", scale=color_scale, legend=alt.Legend(title="Gravité")),
            tooltip=[
                alt.Tooltip("sexe_label:N", title="Sexe"),
                alt.Tooltip("grav_label:N", title="Gravité"),
                alt.Tooltip("usagers:Q", title="Nb usagers", format=","),
            ],
        )
        .properties(height=200, title="Répartition de la gravité par sexe (proportions)")
    )


# ── Point d'entrée ────────────────────────────────────────────────────────
def app():
    st.title("Analyse des données")

    df_light = _load_light()
    if df_light is None:
        st.error(
            "Aucun fichier `table_finale_{année}.csv` trouvé dans `scoring_accident/data/tables_finales/`. "
            "Lancez d'abord `scoring_accident/dev/chargement_donnee.py`."
        )
        return

    tab_desc, tab_qual = st.tabs([
        "📊 Analyse descriptive",
        "🔍 Analyse qualitative",
    ])

    # ── Onglet 1 : Analyse descriptive ────────────────────────────────────
    with tab_desc:
        st.markdown(
            f"<h3 style='color:{TEAL};margin-top:0.5em;'>Indicateurs clés</h3>",
            unsafe_allow_html=True,
        )

        kpis = _compute_kpis(df_light)
        cols = st.columns(3)
        for col, (label, vals) in zip(cols, kpis.items()):
            with col:
                st.markdown(
                    _kpi_card(label, vals["usagers"], vals["accidents"]),
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"<h3 style='color:{TEAL};'>Évolution temporelle de la gravité</h3>",
            unsafe_allow_html=True,
        )
        df_temporal = _compute_temporal(df_light)
        st.altair_chart(_chart_temporal(df_temporal), use_container_width=True)

        # ── Analyses multifactorielles ────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"<h3 style='color:{TEAL};'>Analyses multifactorielles</h3>",
            unsafe_allow_html=True,
        )
        
        df_analysis = _load_analysis()
        if df_analysis is None:
            st.error("Données d'analyse indisponibles.")
        else:
            # ── Conditions environnementales ──────────────────────────────
            st.markdown(
                f"<h4 style='color:{TEAL};margin-top:1em;'>Conditions environnementales</h4>",
                unsafe_allow_html=True,
            )
            
            col_env1, col_env2 = st.columns(2)
            with col_env1:
                df_atm = _compute_atm_distribution(df_analysis)
                st.altair_chart(_chart_atm(df_atm), use_container_width=True)
            
            with col_env2:
                df_lum = _compute_lum_distribution(df_analysis)
                st.altair_chart(_chart_lum(df_lum), use_container_width=True)
            
            # ── Type de collision ─────────────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"<h4 style='color:{TEAL};margin-top:1em;'>Circonstances de l'accident</h4>",
                unsafe_allow_html=True,
            )
            
            df_col = _compute_col_distribution(df_analysis)
            st.altair_chart(_chart_col(df_col), use_container_width=True)
            
            # ── Distribution temporelle ───────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"<h4 style='color:{TEAL};margin-top:1em;'>Répartition temporelle</h4>",
                unsafe_allow_html=True,
            )
            
            col_temp1, col_temp2 = st.columns(2)
            with col_temp1:
                df_jour = _compute_jour_distribution(df_analysis)
                st.altair_chart(_chart_jour(df_jour), use_container_width=True)
            
            with col_temp2:
                df_mois = _compute_mois_distribution(df_analysis)
                st.altair_chart(_chart_mois(df_mois), use_container_width=True)
            
            # ── Analyse démographique ─────────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"<h4 style='color:{TEAL};margin-top:1em;'>Analyse démographique</h4>",
                unsafe_allow_html=True,
            )
            
            df_sexe_grav = _compute_sexe_by_grav(df_analysis)
            st.altair_chart(_chart_sexe_grav(df_sexe_grav), use_container_width=True)
            
            st.info(
                "💡 **Remarque** : Pour une analyse géographique détaillée, "
                "consultez l'onglet **🗺️ Cartographie des données**"
            )

    # ── Onglet 2 : Analyse qualitative ────────────────────────────────────
    with tab_qual:
        st.markdown(
            f"<h3 style='color:{SAGE};margin-top:0.5em;'>Complétude par table BAAC</h3>",
            unsafe_allow_html=True,
        )
        st.caption("2019 – 2024 · Toutes les variables · Survoler une barre pour obtenir les informations sur la variable")

        df_full = _load_for_nulls()
        if df_full is None:
            st.error("Données indisponibles.")
        else:
            comp_data = _compute_completeness(df_full)

            max_h = max(
                len(df) * _BAR_STEP + _CHART_OVERHEAD
                for df in comp_data.values()
            )

            cols = st.columns(4)
            for col, (table_name, comp_df), color in zip(cols, comp_data.items(), SAGE_SHADES):
                with col:
                    chart_h = len(comp_df) * _BAR_STEP + _CHART_OVERHEAD
                    pad = max_h - chart_h
                    if pad > 0:
                        st.markdown(
                            f"<div style='height:{pad}px'></div>",
                            unsafe_allow_html=True,
                        )

                    # Enrichit comp_df avec type et définition pour l'infobulle
                    dict_df = pd.DataFrame(DICT_BAAC[table_name])
                    comp_rich = comp_df.merge(dict_df, on="variable", how="left")

                    st.altair_chart(
                        _chart_completeness(comp_rich, color, table_name),
                        use_container_width=True,
                    )

                    n_nulls = int((comp_df["completude"] < 100.0).sum())
                    if n_nulls > 0:
                        st.caption(f"{n_nulls} variable{'s' if n_nulls > 1 else ''} présentant des valeurs nulles")
                    else:
                        st.caption("Toutes les variables sont renseignées pour chaque entrée")