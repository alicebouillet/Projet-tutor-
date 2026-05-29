import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# ── Palette de couleurs ───────────────────────────────────────────────────
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
    
    # Conversion du prix en numérique si nécessaire
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
    
    # Filtrer les prix aberrants (>3000€)
    if "price" in df.columns:
        df = df[df["price"] <= 3000]
    
    return df


# ── Calculs et statistiques ───────────────────────────────────────────────
def _compute_kpis(df: pd.DataFrame) -> dict:
    """Calcule les indicateurs clés."""
    stats = {
        "nb_logements": len(df),
        "prix_moyen": df["price"].mean() if "price" in df.columns else 0,
        "prix_median": df["price"].median() if "price" in df.columns else 0,
        "nb_quartiers": df["arrondissement"].nunique() if "arrondissement" in df.columns else 0,
    }
    return stats


def _compute_room_type_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule les statistiques par type de logement."""
    if "room_type" not in df.columns or "price" not in df.columns:
        return pd.DataFrame()
    
    room_summary = (
        df.groupby("room_type")["price"]
        .agg(["count", "mean", "median", "min", "max"])
        .reset_index()
        .sort_values(by="mean", ascending=False)
    )
    
    return room_summary


def _compute_price_quartier(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Calcule le prix moyen par arrondissement."""
    if "arrondissement" not in df.columns or "price" not in df.columns:
        return pd.DataFrame()
    
    quartier_stats = (
        df.groupby("arrondissement")["price"]
        .agg(["mean", "count"])
        .reset_index()
        .sort_values(by="mean", ascending=False)
        .head(top_n)
    )
    
    return quartier_stats


def _detect_amenity_cols(df: pd.DataFrame) -> list:
    """Détecte les colonnes d'équipements."""
    return [col for col in df.columns if col.startswith("amenity_")]


def _compute_amenity_stats(df: pd.DataFrame, amenity_cols: list) -> pd.DataFrame:
    """Calcule les statistiques des équipements."""
    if not amenity_cols:
        return pd.DataFrame()
    
    equip_stats = []
    total = len(df)
    
    for col in amenity_cols:
        count = int(df[col].fillna(0).sum())
        pct = (count / total * 100) if total > 0 else 0
        equip_stats.append({
            "colonne": col,
            "equipement": col.replace("amenity_", "").replace("_", " ").capitalize(),
            "nombre_logements": count,
            "pourcentage": pct
        })
    
    equip_df = pd.DataFrame(equip_stats).sort_values(by="nombre_logements", ascending=False)
    return equip_df


# ── Graphiques Altair ─────────────────────────────────────────────────────
def _chart_price_distribution(df: pd.DataFrame) -> alt.Chart:
    """Graphique de distribution des prix."""
    return (
        alt.Chart(df)
        .mark_bar(color=TEAL)
        .encode(
            alt.X("price:Q", bin=alt.Bin(maxbins=50), title="Prix (€)"),
            alt.Y("count()", title="Nombre de logements"),
            tooltip=[
                alt.Tooltip("price:Q", bin=alt.Bin(maxbins=50), title="Prix (€)"),
                alt.Tooltip("count()", title="Nombre"),
            ]
        )
        .properties(
            height=350,
            title="Distribution des prix"
        )
    )


def _chart_room_type(df: pd.DataFrame) -> alt.Chart:
    """Graphique du prix moyen par type de logement."""
    return (
        alt.Chart(df)
        .mark_bar(color=GOLD)
        .encode(
            x=alt.X("mean:Q", title="Prix moyen (€)"),
            y=alt.Y("room_type:N", sort="-x", title="Type de logement"),
            tooltip=[
                alt.Tooltip("room_type:N", title="Type"),
                alt.Tooltip("count:Q", title="Nb logements", format=","),
                alt.Tooltip("mean:Q", title="Prix moyen", format=".2f"),
                alt.Tooltip("median:Q", title="Prix médian", format=".2f"),
            ]
        )
        .properties(
            height=300,
            title="Prix moyen par type de logement"
        )
    )


def _chart_quartier(df: pd.DataFrame) -> alt.Chart:
    """Graphique du prix moyen par arrondissement."""
    return (
        alt.Chart(df)
        .mark_bar(color=BRICK)
        .encode(
            x=alt.X("mean:Q", title="Prix moyen (€)"),
            y=alt.Y("arrondissement:N", sort="-x", title="Arrondissement"),
            tooltip=[
                alt.Tooltip("arrondissement:N", title="Arrondissement"),
                alt.Tooltip("count:Q", title="Nb logements", format=","),
                alt.Tooltip("mean:Q", title="Prix moyen", format=".2f"),
            ]
        )
        .properties(
            height=450,
            title="Top arrondissements par prix moyen"
        )
    )


def _chart_amenity_top(df: pd.DataFrame, top_n: int = 15) -> alt.Chart:
    """Graphique des équipements les plus fréquents."""
    top_data = df.head(top_n)
    return (
        alt.Chart(top_data)
        .mark_bar(color=SAGE)
        .encode(
            x=alt.X("nombre_logements:Q", title="Nombre de logements"),
            y=alt.Y("equipement:N", sort="-x", title="Équipement"),
            tooltip=[
                alt.Tooltip("equipement:N", title="Équipement"),
                alt.Tooltip("nombre_logements:Q", title="Nb logements", format=","),
                alt.Tooltip("pourcentage:Q", title="Pourcentage", format=".1f"),
            ]
        )
        .properties(
            height=450,
            title=f"Top {top_n} des équipements les plus fréquents"
        )
    )


def _chart_amenity_impact(with_mean: float, without_mean: float, amenity_name: str) -> alt.Chart:
    """Graphique de l'impact d'un équipement sur le prix."""
    compare_df = pd.DataFrame({
        "categorie": ["Sans équipement", "Avec équipement"],
        "prix_moyen": [without_mean, with_mean]
    })
    
    return (
        alt.Chart(compare_df)
        .mark_bar(color=ORANGE)
        .encode(
            x=alt.X("categorie:N", title=None),
            y=alt.Y("prix_moyen:Q", title="Prix moyen (€)"),
            tooltip=[
                alt.Tooltip("categorie:N", title="Catégorie"),
                alt.Tooltip("prix_moyen:Q", title="Prix moyen", format=".2f"),
            ]
        )
        .properties(
            height=300,
            title=f"Impact de l'équipement : {amenity_name}"
        )
    )


# ── KPI cards HTML ────────────────────────────────────────────────────────
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
    """Point d'entrée de l'application."""
    
    # ── Titre ──────────────────────────────────────────────────────────────
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
                📊 Analyse des données Airbnb
            </h2>
            <p style="text-align:center; color:{SAGE}; font-size:1.1em; margin-top:0.5em;">
                Exploration statistique et visualisation des annonces à Paris
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
    
    # Nettoyage minimal
    df_clean = df.copy()
    if "price" in df_clean.columns:
        df_clean = df_clean.dropna(subset=["price"])
        df_clean = df_clean[df_clean["price"] > 0]
    
    # Détection des équipements
    amenity_cols = _detect_amenity_cols(df_clean)
    
    # ── Sidebar - Filtres ──────────────────────────────────────────────────
    st.sidebar.header("🔎 Filtres")
    
    # Filtre sur le prix
    if "price" in df_clean.columns and not df_clean["price"].dropna().empty:
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
        arrondissements = ["Tous"] + sorted(df_filtered["arrondissement"].dropna().astype(str).unique().tolist())
        selected_arrondissement = st.sidebar.selectbox("Arrondissement", arrondissements)
        
        if selected_arrondissement != "Tous":
            df_filtered = df_filtered[df_filtered["arrondissement"].astype(str) == selected_arrondissement]
    
    # ── Onglets ────────────────────────────────────────────────────────────
    tab_vue, tab_prix, tab_equip, tab_geo = st.tabs([
        "📋 Vue d'ensemble",
        "💰 Analyse des prix",
        "🛠️ Équipements",
        "🗺️ Analyse géographique"
    ])
    
    # ── Onglet 1 : Vue d'ensemble ──────────────────────────────────────────
    with tab_vue:
        st.markdown(
            f"<h3 style='color:{TEAL};margin-top:0.5em;'>📌 Indicateurs clés</h3>",
            unsafe_allow_html=True
        )
        
        kpis = _compute_kpis(df_filtered)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                _kpi_card(
                    "Logements",
                    f"{kpis['nb_logements']:,}".replace(",", " "),
                    "🏠",
                    TEAL
                ),
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                _kpi_card(
                    "Prix moyen",
                    f"{kpis['prix_moyen']:.0f} €",
                    "💰",
                    GOLD
                ),
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                _kpi_card(
                    "Prix médian",
                    f"{kpis['prix_median']:.0f} €",
                    "📊",
                    BRICK
                ),
                unsafe_allow_html=True
            )
        
        with col4:
            st.markdown(
                _kpi_card(
                    "Arrondissements",
                    f"{kpis['nb_quartiers']}",
                    "📍",
                    SAGE
                ),
                unsafe_allow_html=True
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ── Aperçu du dataset ──────────────────────────────────────────────
        with st.expander("📄 Aperçu du dataset filtré"):
            st.write(f"**Dimensions :** {df_filtered.shape[0]} lignes × {df_filtered.shape[1]} colonnes")
            st.dataframe(df_filtered.head(20), use_container_width=True)
        
        # ── Statistiques descriptives ──────────────────────────────────────
        st.markdown(
            f"<h3 style='color:{TEAL};margin-top:1.5em;'>📈 Statistiques descriptives du prix</h3>",
            unsafe_allow_html=True
        )
        
        if "price" in df_filtered.columns and not df_filtered["price"].dropna().empty:
            col_stat1, col_stat2 = st.columns([1, 2])
            
            with col_stat1:
                desc = df_filtered["price"].describe().to_frame().rename(columns={"price": "Valeur (€)"})
                st.dataframe(desc, use_container_width=True)
                
                st.markdown(
                    f"""
                    <div style="
                        background-color:{TEAL_LIGHT};
                        padding:1em;
                        border-radius:8px;
                        margin-top:1em;
                    ">
                        <p style="margin:0;font-size:0.9em;color:{DARK};">
                            <b>💡 Interprétation :</b><br>
                            • La moyenne donne le niveau général<br>
                            • La médiane est robuste aux valeurs extrêmes<br>
                            • L'écart entre moyenne et médiane indique l'asymétrie
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col_stat2:
                st.altair_chart(_chart_price_distribution(df_filtered), use_container_width=True)
    
    # ── Onglet 2 : Analyse des prix ────────────────────────────────────────
    with tab_prix:
        st.markdown(
            f"<h3 style='color:{GOLD};margin-top:0.5em;'>💰 Analyse détaillée des prix</h3>",
            unsafe_allow_html=True
        )
        
        # ── Prix par type de logement ──────────────────────────────────────
        st.markdown(
            f"<h4 style='color:{GOLD};margin-top:1em;'>Prix par type de logement</h4>",
            unsafe_allow_html=True
        )
        
        room_stats = _compute_room_type_stats(df_filtered)
        if not room_stats.empty:
            col_room1, col_room2 = st.columns([1, 1])
            
            with col_room1:
                st.dataframe(
                    room_stats.style.format({
                        "count": "{:,.0f}",
                        "mean": "{:.2f}",
                        "median": "{:.2f}",
                        "min": "{:.2f}",
                        "max": "{:.2f}"
                    }),
                    use_container_width=True
                )
            
            with col_room2:
                st.altair_chart(_chart_room_type(room_stats), use_container_width=True)
        else:
            st.warning("Données de type de logement non disponibles.")
        
        # ── Prix par arrondissement ────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"<h4 style='color:{GOLD};margin-top:1em;'>Prix par arrondissement</h4>",
            unsafe_allow_html=True
        )
        
        top_n_quartier = st.slider("Nombre d'arrondissements à afficher", 5, 20, 15, key="slider_quartier")
        
        quartier_stats = _compute_price_quartier(df_filtered, top_n=top_n_quartier)
        if not quartier_stats.empty:
            st.altair_chart(_chart_quartier(quartier_stats), use_container_width=True)
        else:
            st.warning("Données d'arrondissement non disponibles.")
    
    # ── Onglet 3 : Équipements ─────────────────────────────────────────────
    with tab_equip:
        st.markdown(
            f"<h3 style='color:{SAGE};margin-top:0.5em;'>🛠️ Analyse des équipements</h3>",
            unsafe_allow_html=True
        )
        
        if amenity_cols:
            equip_df = _compute_amenity_stats(df_filtered, amenity_cols)
            
            # ── Top équipements ────────────────────────────────────────────
            st.markdown(
                f"<h4 style='color:{SAGE};margin-top:1em;'>Équipements les plus fréquents</h4>",
                unsafe_allow_html=True
            )
            
            top_n_equip = st.slider("Nombre d'équipements à afficher", 5, 30, 15, key="slider_equip")
            
            col_equip1, col_equip2 = st.columns([1, 1])
            
            with col_equip1:
                st.dataframe(
                    equip_df[["equipement", "nombre_logements", "pourcentage"]].head(top_n_equip),
                    use_container_width=True
                )
            
            with col_equip2:
                st.altair_chart(_chart_amenity_top(equip_df, top_n=top_n_equip), use_container_width=True)
            
            # ── Impact d'un équipement sur le prix ────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"<h4 style='color:{SAGE};margin-top:1em;'>📈 Impact d'un équipement sur le prix</h4>",
                unsafe_allow_html=True
            )
            
            selected_amenity = st.selectbox(
                "Sélectionnez un équipement",
                amenity_cols,
                format_func=lambda x: x.replace("amenity_", "").replace("_", " ").capitalize()
            )
            
            if selected_amenity and "price" in df_filtered.columns:
                with_amenity = df_filtered[df_filtered[selected_amenity] == 1]
                without_amenity = df_filtered[df_filtered[selected_amenity] == 0]
                
                mean_with = with_amenity["price"].mean() if not with_amenity.empty else 0
                mean_without = without_amenity["price"].mean() if not without_amenity.empty else 0
                
                col_impact1, col_impact2, col_impact3 = st.columns(3)
                
                with col_impact1:
                    st.metric(
                        "Sans équipement",
                        f"{mean_without:.2f} €",
                        f"{len(without_amenity)} logements"
                    )
                
                with col_impact2:
                    st.metric(
                        "Avec équipement",
                        f"{mean_with:.2f} €",
                        f"{len(with_amenity)} logements"
                    )
                
                with col_impact3:
                    diff = mean_with - mean_without
                    pct_diff = (diff / mean_without * 100) if mean_without > 0 else 0
                    st.metric(
                        "Différence",
                        f"{diff:.2f} €",
                        f"{pct_diff:+.1f}%"
                    )
                
                amenity_name = selected_amenity.replace("amenity_", "").replace("_", " ").capitalize()
                st.altair_chart(
                    _chart_amenity_impact(mean_with, mean_without, amenity_name),
                    use_container_width=True
                )
                
                st.info(
                    "💡 **Remarque** : Une différence de prix ne signifie pas nécessairement une relation de cause à effet. "
                    "D'autres facteurs (localisation, taille, etc.) peuvent influencer le prix."
                )
        else:
            st.info("Aucune colonne d'équipement (amenity_*) n'a été détectée dans les données.")
    
    # ── Onglet 4 : Analyse géographique ────────────────────────────────────
    with tab_geo:
        st.markdown(
            f"<h3 style='color:{BRICK};margin-top:0.5em;'>🗺️ Répartition géographique</h3>",
            unsafe_allow_html=True
        )
        
        if "arrondissement" in df_filtered.columns:
            # ── Distribution par arrondissement ────────────────────────────
            st.markdown(
                f"<h4 style='color:{BRICK};margin-top:1em;'>Distribution des logements par arrondissement</h4>",
                unsafe_allow_html=True
            )
            
            quartier_count = (
                df_filtered["arrondissement"]
                .value_counts()
                .reset_index()
                .rename(columns={"index": "arrondissement", "arrondissement": "count"})
            )
            quartier_count.columns = ["arrondissement", "count"]
            
            col_geo1, col_geo2 = st.columns([1, 1])
            
            with col_geo1:
                st.dataframe(
                    quartier_count.head(20),
                    use_container_width=True
                )
            
            with col_geo2:
                chart_quartier_count = (
                    alt.Chart(quartier_count.head(20))
                    .mark_bar(color=BRICK)
                    .encode(
                        x=alt.X("count:Q", title="Nombre de logements"),
                        y=alt.Y("arrondissement:N", sort="-x", title="Arrondissement"),
                        tooltip=[
                            alt.Tooltip("arrondissement:N", title="Arrondissement"),
                            alt.Tooltip("count:Q", title="Nb logements", format=","),
                        ]
                    )
                    .properties(
                        height=450,
                        title="Arrondissements par nombre de logements"
                    )
                )
                st.altair_chart(chart_quartier_count, use_container_width=True)
            
            st.info(
                "💡 **Astuce** : Pour une cartographie interactive complète, "
                "consultez l'onglet **🗺️ Cartographie** dans le menu principal."
            )
        else:
            st.warning("Données géographiques non disponibles.")
        
        # ── Corrélations avec le prix ──────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"<h4 style='color:{BRICK};margin-top:1em;'>🔗 Corrélations numériques avec le prix</h4>",
            unsafe_allow_html=True
        )
        
        if "price" in df_filtered.columns:
            numeric_df = df_filtered.select_dtypes(include=["int64", "float64", "int32", "float32"]).copy()
            
            if "price" in numeric_df.columns and len(numeric_df.columns) > 1:
                corr_price = (
                    numeric_df.corr(numeric_only=True)["price"]
                    .sort_values(ascending=False)
                    .dropna()
                )
                
                corr_price = corr_price.drop(labels=["price"], errors="ignore")
                corr_display = corr_price.head(20).to_frame().rename(columns={"price": "corrélation"})
                
                st.dataframe(corr_display, use_container_width=True)
                
                st.markdown(
                    f"""
                    <div style="
                        background-color:{TEAL_LIGHT};
                        padding:1em;
                        border-radius:8px;
                        margin-top:1em;
                    ">
                        <p style="margin:0;font-size:0.9em;color:{DARK};">
                            <b>💡 Interprétation :</b><br>
                            • Corrélation positive : la variable augmente avec le prix<br>
                            • Corrélation négative : la variable diminue quand le prix augmente<br>
                            • Attention : corrélation ≠ causalité
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.info("Pas assez de colonnes numériques pour calculer des corrélations.")
