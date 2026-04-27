import streamlit as st
from pagesWeb import presentation, analyseDonnee, cartographie, modelePrediction, dictionnaire
#from utils.data_loader import load_all_data

st.set_page_config(
    page_title="RiskScore Analytics",  
    layout="wide",                  
    initial_sidebar_state="expanded" 
)

# Barre de navigation 
st.sidebar.title("Navigation")
onglet = st.sidebar.radio("Aller à :", [
    "📝 Présentation du projet",
    "📊 Analyse des données", 
    "🗺️ Cartographie des données", 
    "📈 Modèle de prédiction", 
    "📚 Dictionnaire des données"])

# Chargement des données
#() = load_all_data()

# Onglet 1 : Présentation du projet 
if onglet == "📝 Présentation du projet":
    presentation.app()

# Onglet 2 : Analyse des données
elif onglet == "📊 Analyse des données":
    analyseDonnee.app()

# Onglet 3 : Données cartographiques
elif onglet == "🗺️ Cartographie des données":
    cartographie.app()

# Onglet 4 : Modèle de prédiction
elif onglet == "📈 Modèle de prédiction":
    modelePrediction.app()

# Onglet 5 : Dictionnaire des données
elif onglet == "📚 Dictionnaire des données" :
    dictionnaire.app()