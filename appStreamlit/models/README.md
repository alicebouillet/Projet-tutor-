# Modèle de Prédiction de Prix Airbnb Paris

## 📋 Vue d'ensemble

Ce module permet de prédire le prix par nuit des locations Airbnb à Paris en utilisant des algorithmes de Machine Learning (Random Forest, Gradient Boosting, Extra Trees).

## 🚀 Étapes pour utiliser le modèle

### 1. Entraîner et sauvegarder le modèle

Avant de pouvoir utiliser la page de prédiction dans Streamlit, tu dois d'abord entraîner et sauvegarder le modèle :

```bash
# Depuis la racine du projet
python dev/modele/save_model.py
```

Ce script va :
- ✅ Charger et nettoyer les données `data/airbnb_enrichi.csv`
- ✅ Entraîner un modèle Random Forest optimisé
- ✅ Sauvegarder 3 fichiers dans `appStreamlit/models/` :
  - `model_airbnb.pkl` : le modèle entraîné
  - `scaler_airbnb.pkl` : le StandardScaler pour normaliser les données
  - `metrics_airbnb.json` : les métriques de performance (R², RMSE, MAE)

### 2. Lancer l'application Streamlit

Une fois le modèle sauvegardé, tu peux lancer l'application :

```bash
cd appStreamlit
streamlit run app.py
```

### 3. Utiliser la page de prédiction

Dans l'application Streamlit, navigue vers la page **"Modèle de Prédiction"** et remplis le formulaire :

#### 🏠 Caractéristiques du logement
- Type de propriété (appartement, chambre privée, etc.)
- Type de location (logement entier, chambre privée, etc.)
- Nombre de voyageurs
- Nuits minimum/maximum
- Réservation instantanée

#### 📍 Localisation
- Arrondissement de Paris
- Coordonnées GPS (latitude/longitude)
- Transport à proximité (métro, RER, gare SNCF)

#### ✨ Équipements
- Équipements essentiels (WiFi, cuisine, lave-linge, etc.)
- Confort (climatisation, chauffage, ascenseur)
- Sécurité (détecteurs de fumée, extincteur, etc.)

Clique sur **"💰 Estimer le prix"** pour obtenir :
- Le prix estimé par nuit
- Le prix par voyageur
- Le coût total pour le séjour minimum
- La catégorie de prix (Budget, Économique, Moyen, Élevé, Premium)

## 📊 Performances du modèle

Les performances typiques attendues (peuvent varier selon les données) :
- **R² Score** : ~0.50-0.70 (explique 50-70% de la variance des prix)
- **RMSE** : ~30-50€ (erreur moyenne)
- **MAE** : ~20-40€ (erreur absolue moyenne)

## 🔧 Pour un entraînement plus poussé

Si tu veux tester différents modèles et optimisations, utilise le script complet :

```bash
python dev/modele/testModele.py
```

Ce script teste plusieurs algorithmes (Linear Regression, Ridge, Lasso, Random Forest, Gradient Boosting, etc.) et optimise leurs hyperparamètres.

## 📁 Structure des fichiers

```
appStreamlit/
├── models/                          # Modèles sauvegardés
│   ├── model_airbnb.pkl            # Modèle de prédiction
│   ├── scaler_airbnb.pkl           # Scaler pour normalisation
│   └── metrics_airbnb.json         # Métriques de performance
├── pagesWeb/
│   └── modelePrediction.py         # Page Streamlit de prédiction
└── app.py                          # Application principale

dev/modele/
├── testModele.py                   # Script complet d'entraînement
└── save_model.py                   # Script rapide pour sauvegarder le modèle

data/
└── airbnb_enrichi.csv              # Dataset avec features enrichies
```

## 🎯 Features utilisées par le modèle

Le modèle utilise les features suivantes (après encodage) :
- **Logement** : property_type, room_type, accommodates
- **Localisation** : latitude, longitude, arrondissement
- **Séjour** : minimum_nights, maximum_nights, instant_bookable
- **Équipements** : 30+ amenities (wifi, tv, kitchen, etc.)
- **Transport** : flag_metro, flag_rer, flag_gare_sncf, flag_transport

## ⚠️ Notes importantes

1. **Encodage** : Les variables catégorielles (property_type, room_type, arrondissement) sont automatiquement encodées par LabelEncoder dans la page de prédiction.

2. **Normalisation** : Si un scaler est disponible, les features numériques sont normalisées avant la prédiction.

3. **Données manquantes** : Les amenities non cochés sont considérés comme 0 (absent).

4. **Limites** : Le modèle est entraîné sur les données de Paris uniquement. Les prédictions pour d'autres villes ne seront pas fiables.

## 🐛 Dépannage

**Erreur "Modèle introuvable"**
→ Lance `python dev/modele/save_model.py` pour créer le modèle

**Erreur "Module not found"**
→ Installe les dépendances : `pip install -r requirements.txt`

**Prédictions incohérentes**
→ Vérifie que les coordonnées GPS sont bien dans Paris (48.80-48.92, 2.20-2.45)

**Erreur de dimension**
→ Assure-toi que le dataset utilisé pour l'entraînement correspond bien à `data/airbnb_enrichi.csv`
