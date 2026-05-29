import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================
st.set_page_config(
    page_title="Dashboard Airbnb",
    page_icon="🏠",
    layout="wide"
)

# ============================================================
# TITRE ET INTRODUCTION
# ============================================================
st.title("🏠 Dashboard Airbnb - Analyse descriptive et visualisation")
st.markdown(
    """
    Cette application Streamlit permet d'explorer un jeu de données Airbnb enrichi.
    Elle propose :
    - une vue générale du dataset,
    - une analyse descriptive du prix,
    - une analyse des équipements,
    - des filtres interactifs,
    - des visualisations simples et lisibles.
    """
)

# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================
# Le cache permet d'éviter de recharger le fichier à chaque interaction.
@st.cache_data

def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, low_memory=False)

    # Conversion du prix en numérique si nécessaire
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")

    return df

# ============================================================
# SIDEBAR - CHARGEMENT FICHIER
# ============================================================
st.sidebar.header("⚙️ Paramètres")
file_path = st.sidebar.text_input(
    "Chemin du fichier CSV",
    value="airbnb_enrichi.csv"
)

try:
    df = load_data(file_path)
except Exception as e:
    st.error(f"Impossible de charger le fichier : {e}")
    st.stop()

# ============================================================
# NETTOYAGE MINIMAL
# ============================================================
df_clean = df.copy()
if "price" in df_clean.columns:
    df_clean = df_clean.dropna(subset=["price"])

# Détection automatique des colonnes d'équipements
amenity_cols = [col for col in df_clean.columns if col.startswith("amenity_")]

# ============================================================
# SIDEBAR - FILTRES
# ============================================================
st.sidebar.subheader("🔎 Filtres")

# Filtre sur le prix
if "price" in df_clean.columns and not df_clean["price"].dropna().empty:
    min_price = float(df_clean["price"].min())
    max_price = float(df_clean["price"].max())

    price_range = st.sidebar.slider(
        "Intervalle de prix",
        min_value=float(min_price),
        max_value=float(max_price),
        value=(float(min_price), float(max_price))
    )

    df_filtered = df_clean[
        (df_clean["price"] >= price_range[0]) &
        (df_clean["price"] <= price_range[1])
    ].copy()
else:
    df_filtered = df_clean.copy()

# Filtre sur le type de logement si disponible
if "room_type" in df_filtered.columns:
    room_types = ["Tous"] + sorted(df_filtered["room_type"].dropna().astype(str).unique().tolist())
    selected_room_type = st.sidebar.selectbox("Type de logement", room_types)

    if selected_room_type != "Tous":
        df_filtered = df_filtered[df_filtered["room_type"].astype(str) == selected_room_type]

# Filtre sur un équipement
selected_amenity = None
if amenity_cols:
    selected_amenity = st.sidebar.selectbox(
        "Équipement à analyser",
        amenity_cols,
        format_func=lambda x: x.replace("amenity_", "").replace("_", " ").capitalize()
    )

# ============================================================
# INDICATEURS CLÉS
# ============================================================
st.subheader("📌 Indicateurs clés")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Nombre de logements", f"{len(df_filtered):,}".replace(",", " "))

with col2:
    if "price" in df_filtered.columns and not df_filtered["price"].dropna().empty:
        st.metric("Prix moyen", f"{df_filtered['price'].mean():.2f} €")
    else:
        st.metric("Prix moyen", "N/A")

with col3:
    if "price" in df_filtered.columns and not df_filtered["price"].dropna().empty:
        st.metric("Prix médian", f"{df_filtered['price'].median():.2f} €")
    else:
        st.metric("Prix médian", "N/A")

with col4:
    if amenity_cols:
        st.metric("Nb équipements suivis", len(amenity_cols))
    else:
        st.metric("Nb équipements suivis", 0)

# ============================================================
# APERÇU DES DONNÉES
# ============================================================
with st.expander("📄 Aperçu du dataset"):
    st.write("Dimensions du dataset filtré :", df_filtered.shape)
    st.dataframe(df_filtered.head(20))

# ============================================================
# STATISTIQUE DESCRIPTIVE DU PRIX
# ============================================================
st.subheader("💰 Analyse descriptive du prix")

if "price" in df_filtered.columns and not df_filtered["price"].dropna().empty:
    desc = df_filtered["price"].describe().to_frame().rename(columns={"price": "Valeur"})
    st.dataframe(desc)

    st.markdown(
        """
        **Interprétation :**
        - La moyenne permet d'avoir une idée du niveau général des prix.
        - La médiane est souvent plus robuste en présence de logements très chers.
        - Si la moyenne est nettement supérieure à la médiane, cela suggère une distribution asymétrique.
        """
    )

    fig_price, ax_price = plt.subplots(figsize=(8, 4))
    ax_price.hist(df_filtered["price"].dropna(), bins=40)
    ax_price.set_title("Distribution des prix")
    ax_price.set_xlabel("Prix")
    ax_price.set_ylabel("Nombre de logements")
    st.pyplot(fig_price)
else:
    st.warning("La colonne 'price' est absente ou vide après filtrage.")

# ============================================================
# ANALYSE DES ÉQUIPEMENTS
# ============================================================
st.subheader("🛠️ Analyse des équipements")

if amenity_cols:
    equip_stats = []
    total = len(df_filtered)

    for col in amenity_cols:
        # On suppose ici que les colonnes amenity_* sont binaires (0/1)
        count = int(df_filtered[col].fillna(0).sum())
        pct = (count / total * 100) if total > 0 else 0
        equip_stats.append([
            col,
            col.replace("amenity_", "").replace("_", " ").capitalize(),
            count,
            pct
        ])

    equip_df = pd.DataFrame(
        equip_stats,
        columns=["colonne", "equipement", "nombre_logements", "pourcentage"]
    ).sort_values(by="nombre_logements", ascending=False)

    st.dataframe(equip_df[["equipement", "nombre_logements", "pourcentage"]])

    st.markdown(
        """
        **Interprétation :**
        - Les équipements les plus fréquents correspondent souvent aux standards du marché.
        - Les équipements rares peuvent permettre de différencier un logement.
        - Plus un équipement est rare, plus il peut avoir un effet sur le positionnement prix.
        """
    )

    top_n = st.slider("Nombre d'équipements à afficher", 5, min(20, len(equip_df)), 10)
    fig_equip, ax_equip = plt.subplots(figsize=(10, 5))
    top_data = equip_df.head(top_n)
    ax_equip.bar(top_data["equipement"], top_data["nombre_logements"])
    ax_equip.set_title("Top équipements les plus présents")
    ax_equip.set_xlabel("Équipement")
    ax_equip.set_ylabel("Nombre de logements")
    ax_equip.tick_params(axis="x", rotation=45)
    st.pyplot(fig_equip)
else:
    st.info("Aucune colonne amenity_* n'a été détectée.")

# ============================================================
# IMPACT D'UN ÉQUIPEMENT SUR LE PRIX
# ============================================================
st.subheader("📈 Impact d'un équipement sur le prix")

if selected_amenity and selected_amenity in df_filtered.columns and "price" in df_filtered.columns:
    # On compare les prix moyens avec et sans l'équipement sélectionné
    with_amenity = df_filtered[df_filtered[selected_amenity] == 1]
    without_amenity = df_filtered[df_filtered[selected_amenity] == 0]

    mean_with = with_amenity["price"].mean() if not with_amenity.empty else None
    mean_without = without_amenity["price"].mean() if not without_amenity.empty else None

    c1, c2 = st.columns(2)
    with c1:
        st.metric(
            f"Prix moyen avec {selected_amenity.replace('amenity_', '')}",
            "N/A" if mean_with is None or pd.isna(mean_with) else f"{mean_with:.2f} €"
        )
    with c2:
        st.metric(
            f"Prix moyen sans {selected_amenity.replace('amenity_', '')}",
            "N/A" if mean_without is None or pd.isna(mean_without) else f"{mean_without:.2f} €"
        )

    compare_df = pd.DataFrame({
        "catégorie": ["Sans équipement", "Avec équipement"],
        "prix_moyen": [
            0 if mean_without is None or pd.isna(mean_without) else mean_without,
            0 if mean_with is None or pd.isna(mean_with) else mean_with,
        ]
    })

    fig_compare, ax_compare = plt.subplots(figsize=(6, 4))
    ax_compare.bar(compare_df["catégorie"], compare_df["prix_moyen"])
    ax_compare.set_title("Comparaison du prix moyen")
    ax_compare.set_ylabel("Prix moyen")
    st.pyplot(fig_compare)

    st.markdown(
        """
        **Interprétation :**
        - Si le prix moyen avec l'équipement est plus élevé, cela suggère un positionnement plus premium.
        - Attention : cela n'implique pas à lui seul une causalité.
        - D'autres facteurs peuvent influencer le prix, comme la localisation ou la taille du logement.
        """
    )

# ============================================================
# ANALYSE PAR TYPE DE LOGEMENT
# ============================================================
st.subheader("🏘️ Analyse par type de logement")

if "room_type" in df_filtered.columns and "price" in df_filtered.columns:
    room_summary = (
        df_filtered.groupby("room_type")["price"]
        .agg(["count", "mean", "median", "min", "max"])
        .reset_index()
        .sort_values(by="mean", ascending=False)
    )

    st.dataframe(room_summary)

    fig_room, ax_room = plt.subplots(figsize=(8, 4))
    ax_room.bar(room_summary["room_type"].astype(str), room_summary["mean"])
    ax_room.set_title("Prix moyen par type de logement")
    ax_room.set_xlabel("Type de logement")
    ax_room.set_ylabel("Prix moyen")
    ax_room.tick_params(axis="x", rotation=30)
    st.pyplot(fig_room)

    st.markdown(
        """
        **Interprétation :**
        - Certains types de logements affichent des prix moyens plus élevés.
        - Cela permet de repérer rapidement les segments les plus premium.
        """
    )

# ============================================================
# CORRÉLATIONS SIMPLES
# ============================================================
st.subheader("🔗 Corrélations avec le prix")

if "price" in df_filtered.columns:
    numeric_df = df_filtered.select_dtypes(include=["int64", "float64", "int32", "float32"]).copy()

    if "price" in numeric_df.columns and len(numeric_df.columns) > 1:
        corr_price = (
            numeric_df.corr(numeric_only=True)["price"]
            .sort_values(ascending=False)
            .dropna()
        )

        corr_price = corr_price.drop(labels=["price"], errors="ignore")
        corr_display = corr_price.head(15).to_frame().rename(columns={"price": "corrélation"})
        st.dataframe(corr_display)

        st.markdown(
            """
            **Interprétation :**
            - Une corrélation positive signifie qu'une variable augmente en même temps que le prix.
            - Une corrélation négative signifie qu'une variable augmente quand le prix baisse.
            - Une corrélation ne prouve pas une relation de cause à effet.
            """
        )
    else:
        st.info("Pas assez de colonnes numériques pour calculer des corrélations pertinentes.")

# ============================================================
# CONCLUSION
# ============================================================
st.subheader("✅ Conclusion")
st.markdown(
    """
    Cette application montre que l'analyse descriptive permet de dégager plusieurs constats :
    - le prix des logements n'est pas réparti uniformément,
    - certains équipements sont devenus des standards,
    - les équipements plus rares peuvent contribuer à un positionnement plus haut de gamme,
    - la comparaison entre segments permet de mieux comprendre la structure du marché Airbnb.

    Cette base peut être enrichie avec :
    - une carte interactive,
    - des graphiques Plotly,
    - une analyse par quartier,
    - un scoring des logements.
    """
)
