import streamlit as st
import pandas as pd
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


def _get_data_stats():
    """Récupère des statistiques rapides sur les données disponibles."""
    try:
        if not DATA_FILE.exists():
            return None
            
        df = pd.read_csv(DATA_FILE, encoding="utf-8-sig", low_memory=False)
        
        # Filtrer les prix aberrants (> 1000€)
        if "price" in df.columns:
            df["price"] = pd.to_numeric(df["price"], errors="coerce")
            df = df[df["price"] <= 1000]
        
        return {
            "years": "Données Airbnb",
            "annonces": len(df),
            "quartiers": df['arrondissement'].nunique() if 'arrondissement' in df.columns else 20
        }
    except:
        return {
            "years": "Données Airbnb",
            "annonces": 0,
            "quartiers": 0
        }


def app():
    # ── En-tête avec gradient ─────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {TEAL} 0%, {TEAL_LIGHT} 100%);
            padding: 3em 2em;
            border-radius: 15px;
            margin-bottom: 2em;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <h1 style="text-align:center; color:white; margin:0; font-size:3em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                🏠 Airbnb Paris Analytics
            </h1>
            <p style="text-align:center; color:{SAGE}; font-size:1.3em; margin-top:0.5em; font-weight:500;">
                Plateforme d'analyse et de prédiction des prix Airbnb à Paris
            </p>
            <p style="text-align:center; color:white; font-size:1em; margin-top:1em; font-style:italic;">
                📚 Projet académique – Cycle Science de la donnée
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ── Statistiques clés ─────────────────────────────────────────────────
    stats = _get_data_stats()
    
    st.markdown(
        f"<h3 style='text-align:center; color:{TEAL}; margin-bottom:1em;'>📊 Données analysées</h3>",
        unsafe_allow_html=True
    )
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, {GOLD} 0%, #F7C04A 100%);
                padding: 2em 1em;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 3em; color:white; font-weight:bold;">📅</div>
                <div style="font-size: 2.5em; color:white; font-weight:bold; margin:0.3em 0;">{stats['years']}</div>
                <div style="font-size: 1.1em; color:{DARK}; font-weight:600;">Source de données</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col_stat2:
        annonces_display = f"{stats['annonces']:,}" if stats['annonces'] > 0 else "---"
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, {BRICK} 0%, #FC8285 100%);
                padding: 2em 1em;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 3em; color:white; font-weight:bold;">🏠</div>
                <div style="font-size: 2.5em; color:white; font-weight:bold; margin:0.3em 0;">{annonces_display}</div>
                <div style="font-size: 1.1em; color:white; font-weight:600;">Annonces Airbnb</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col_stat3:
        quartiers_display = "20"
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, {TEAL} 0%, {TEAL_LIGHT} 100%);
                padding: 2em 1em;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 3em; color:white; font-weight:bold;">📍</div>
                <div style="font-size: 2.5em; color:white; font-weight:bold; margin:0.3em 0;">{quartiers_display}</div>
                <div style="font-size: 1.1em; color:{SAGE}; font-weight:600;">Arrondissements</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Présentation de l'outil ───────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            background-color: #F8F9FA;
            padding: 2em;
            border-radius: 12px;
            border-left: 5px solid {TEAL};
            margin: 2em 0;
        ">
            <h3 style="color:{TEAL}; margin-top:0;">🎯 À propos de Airbnb Paris Analytics</h3>
            <p style="font-size:1.1em; line-height:1.8; color:{DARK};">
                <b>Airbnb Paris Analytics</b> est une plateforme interactive d'analyse et de prédiction des prix Airbnb à Paris,
                développée dans le cadre d'un projet académique en science de la donnée.
            </p>
            <p style="font-size:1.1em; line-height:1.8; color:{DARK};">
                L'application permet d'explorer les données des annonces Airbnb à Paris,
                d'identifier les facteurs influençant les prix, et de prédire les tarifs de location à l'aide de modèles de machine learning.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ── Fonctionnalités principales ───────────────────────────────────────
    st.markdown(
        f"<h3 style='text-align:center; color:{TEAL}; margin:2em 0 1em 0;'>⚙️ Fonctionnalités principales</h3>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div style="
                background-color:white;
                border: 2px solid {TEAL};
                border-radius:15px;
                padding:2em;
                min-height:250px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.3s;
            ">
                <div style="text-align:center; font-size:4em; margin-bottom:0.3em;">📊</div>
                <h4 style='color:{TEAL}; text-align:center; margin-bottom:1em;'>Analyse des données</h4>
                <ul style='color:{DARK}; font-size:1em; line-height:2;'>
                    <li>Statistiques descriptives et KPIs</li>
                    <li>Distribution des prix par arrondissement</li>
                    <li>Analyse des types de logements</li>
                    <li>Disponibilité et taux d'occupation</li>
                    <li>Répartition temporelle des réservations</li>
                    <li>Analyse qualitative des équipements</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(
            f"""
            <div style="
                background-color:white;
                border: 2px solid {GOLD};
                border-radius:15px;
                padding:2em;
                min-height:250px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <div style="text-align:center; font-size:4em; margin-bottom:0.3em;">📚</div>
                <h4 style='color:{GOLD}; text-align:center; margin-bottom:1em;'>Dictionnaire des données</h4>
                <ul style='color:{DARK}; font-size:1em; line-height:2;'>
                    <li>Description complète des variables</li>
                    <li>Types de logements et équipements</li>
                    <li>Schémas explicatifs des caractéristiques</li>
                    <li>Fonction de recherche intégrée</li>
                    <li>Documentation Airbnb détaillée</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="
                background-color:white;
                border: 2px solid {BRICK};
                border-radius:15px;
                padding:2em;
                min-height:250px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <div style="text-align:center; font-size:4em; margin-bottom:0.3em;">🗺️</div>
                <h4 style='color:{BRICK}; text-align:center; margin-bottom:1em;'>Cartographie interactive</h4>
                <ul style='color:{DARK}; font-size:1em; line-height:2;'>
                    <li>Carte interactive des annonces</li>
                    <li>Carte de chaleur des prix</li>
                    <li>Filtres par arrondissement, prix et type</li>
                    <li>Classement par arrondissement</li>
                    <li>Analyse spatiale des équipements</li>
                    <li>Distribution géographique des logements</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(
            f"""
            <div style="
                background-color:white;
                border: 2px solid {SAGE};
                border-radius:15px;
                padding:2em;
                min-height:250px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            ">
                <div style="text-align:center; font-size:4em; margin-bottom:0.3em;">🤖</div>
                <h4 style='color:{SAGE}; text-align:center; margin-bottom:1em;'>Modèle de prédiction</h4>
                <ul style='color:{DARK}; font-size:1em; line-height:2;'>
                    <li>Prédiction des prix de location</li>
                    <li>Modèle XGBoost optimisé</li>
                    <li>Interface de saisie intuitive</li>
                    <li>Métriques de performance détaillées</li>
                    <li>Interprétation des résultats</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ── Guide de démarrage rapide ─────────────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {TEAL} 0%, {TEAL_LIGHT} 100%);
            padding: 2em;
            border-radius: 12px;
            margin: 2em 0;
        ">
            <h3 style="color:white; margin-top:0; text-align:center;">🚀 Guide de démarrage rapide</h3>
            <div style="display:flex; justify-content:space-around; flex-wrap:wrap; margin-top:2em;">
                <div style="text-align:center; color:white; margin:1em;">
                    <div style="font-size:3em; margin-bottom:0.3em;">1️⃣</div>
                    <div style="font-weight:bold; font-size:1.2em; color:{GOLD};">Explorez les données</div>
                    <div style="font-size:0.9em; margin-top:0.5em;">Onglet "Analyse des données"</div>
                </div>
                <div style="text-align:center; color:white; margin:1em;">
                    <div style="font-size:3em; margin-bottom:0.3em;">2️⃣</div>
                    <div style="font-weight:bold; font-size:1.2em; color:{GOLD};">Visualisez sur la carte</div>
                    <div style="font-size:0.9em; margin-top:0.5em;">Onglet "Cartographie"</div>
                </div>
                <div style="text-align:center; color:white; margin:1em;">
                    <div style="font-size:3em; margin-bottom:0.3em;">3️⃣</div>
                    <div style="font-weight:bold; font-size:1.2em; color:{GOLD};">Consultez le dictionnaire</div>
                    <div style="font-size:0.9em; margin-top:0.5em;">Onglet "Dictionnaire"</div>
                </div>
                <div style="text-align:center; color:white; margin:1em;">
                    <div style="font-size:3em; margin-bottom:0.3em;">4️⃣</div>
                    <div style="font-weight:bold; font-size:1.2em; color:{GOLD};">Testez le modèle</div>
                    <div style="font-size:0.9em; margin-top:0.5em;">Onglet "Modèle de prédiction"</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ── Source des données ────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="
            background-color: {SAGE};
            padding: 1.5em;
            border-radius: 12px;
            margin: 2em 0;
        ">
            <h4 style="color:{DARK}; margin-top:0;">📂 Source des données</h4>
            <p style="color:{DARK}; margin-bottom:0.5em;">
                <b>Base de données :</b> Inside Airbnb - Données enrichies avec services de transport
            </p>
            <p style="color:{DARK}; margin-bottom:0.5em;">
                <b>Plateforme :</b> Inside Airbnb - Initiative communautaire de transparence
            </p>
            <p style="color:{DARK}; margin-bottom:0.5em;">
                <b>Périmètre :</b> Annonces Airbnb à Paris avec données géographiques par arrondissement
            </p>
            <p style="color:{DARK}; margin-bottom:0;">
                <b>Disponibilité :</b> <a href="http://insideairbnb.com/get-the-data.html" target="_blank" style="color:{TEAL}; font-weight:bold;">insideairbnb.com</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ── Technologies utilisées ────────────────────────────────────────────
    st.markdown(
        f"<h4 style='color:{TEAL}; text-align:center; margin:2em 0 1em 0;'>🛠️ Technologies utilisées</h4>",
        unsafe_allow_html=True
    )
    
    tech_col1, tech_col2, tech_col3, tech_col4 = st.columns(4)
    
    with tech_col1:
        st.markdown(
            f"""
            <div style="text-align:center; padding:1em; background-color:{TEAL}; border-radius:10px;">
                <div style="font-size:2.5em; margin-bottom:0.3em;">🐍</div>
                <div style="color:white; font-weight:bold;">Python</div>
                <div style="color:{SAGE}; font-size:0.9em;">Langage principal</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with tech_col2:
        st.markdown(
            f"""
            <div style="text-align:center; padding:1em; background-color:{GOLD}; border-radius:10px;">
                <div style="font-size:2.5em; margin-bottom:0.3em;">📊</div>
                <div style="color:white; font-weight:bold;">Streamlit</div>
                <div style="color:{DARK}; font-size:0.9em;">Interface web</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with tech_col3:
        st.markdown(
            f"""
            <div style="text-align:center; padding:1em; background-color:{BRICK}; border-radius:10px;">
                <div style="font-size:2.5em; margin-bottom:0.3em;">🤖</div>
                <div style="color:white; font-weight:bold;">XGBoost</div>
                <div style="color:white; font-size:0.9em;">Machine Learning</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with tech_col4:
        st.markdown(
            f"""
            <div style="text-align:center; padding:1em; background-color:{SAGE}; border-radius:10px;">
                <div style="font-size:2.5em; margin-bottom:0.3em;">🗺️</div>
                <div style="color:{DARK}; font-weight:bold;">Folium</div>
                <div style="color:{DARK}; font-size:0.9em;">Cartographie</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ── Footer ────────────────────────────────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="
            text-align:center;
            background: linear-gradient(135deg, {DARK} 0%, #0A1929 100%);
            padding:2em;
            border-radius:12px;
            margin-top:3em;
            border-top:3px solid {GOLD};
        ">
            <p style="color:{SAGE}; font-size:1.1em; margin-bottom:0.5em;">
                Application développée avec <span style='color:{GOLD}; font-weight:bold;'>Python</span> et <span style='color:{GOLD}; font-weight:bold;'>Streamlit</span>
            </p>
            <p style="color:{TEAL}; font-size:0.95em; margin-bottom:0;">
                © 2024-2026 · ENSAR – École d'ingénieur · Cycle Science de la donnée
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
