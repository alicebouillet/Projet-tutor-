# 🏠 Airbnb Paris Analytics - Projet Tuteuré

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)]()

## 📚 Description du Projet

**Airbnb Paris Analytics** est une plateforme d'analyse et de prédiction des prix des logements Airbnb à Paris. Ce projet académique de science des données combine la visualisation de données, l'analyse géospatiale et le machine learning pour fournir des insights sur le marché locatif parisien.

### 🎯 Objectifs

- 📊 **Analyser** les tendances du marché Airbnb à Paris (prix, disponibilité, caractéristiques)
- 🗺️ **Visualiser** géographiquement la distribution des logements et leurs caractéristiques
- 🤖 **Prédire** les prix des logements en utilisant des algorithmes de machine learning
- 📈 **Identifier** les facteurs influençant le plus les prix (localisation, équipements, transports)

### 👥 Équipe

- **Benyamine DJALANE** & **Cheikh SARR** & **Robin DEVAUX COLNOT** & **Alice BOUILLET**
- Projet Tuteuré - Cycle Science de la Donnée
- Université de Poitiers - INGE2

---

## 🚀 Fonctionnalités

### 1. 📝 Présentation du Projet
- Vue d'ensemble du projet et de ses objectifs
- Statistiques clés sur le dataset (nombre d'annonces, quartiers couverts)
- Contexte et méthodologie

### 2. 📊 Analyse des Données
- **Statistiques descriptives** : distribution des prix, types de logements, capacité d'accueil
- **Visualisations interactives** : 
  - Histogrammes de prix par arrondissement
  - Répartition des types de propriétés
  - Analyse des équipements (WiFi, cuisine, climatisation, etc.)
  - Corrélations entre variables
- **Insights business** : prix moyens, tendances par quartier

### 3. 🗺️ Cartographie Interactive
- **Carte de chaleur** (heatmap) des prix à Paris
- **Visualisation par points** géolocalisés des annonces
- **Filtres interactifs** :
  - Par arrondissement
  - Par type de logement (appartement, maison, chambre privée)
  - Par gamme de prix
- **Proximité des transports** : métro, RER, tramway visualisés
- Utilisation de **Folium** pour des cartes HTML interactives

### 4. 📈 Modèle de Prédiction
- **Prédiction du prix par nuit** basée sur les caractéristiques du logement
- **6 modèles comparés** : Ridge, Lasso, Random Forest, XGBoost, LightGBM, CatBoost
- **Interface utilisateur intuitive** :
  - Sélection des caractéristiques (quartier, type, capacité, équipements)
  - Affichage du prix prédit en temps réel
  - Visualisation de l'importance des variables
- **Métriques de performance** : MAE, RMSE, R², MAPE

### 5. 📚 Dictionnaire des Données
- Description complète de toutes les variables du dataset
- Types de données et valeurs possibles
- Statistiques par colonne (min, max, moyenne, valeurs manquantes)

---

## 📂 Structure du Projet

```
Projet-tutor-/
│
├── 📁 appStreamlit/                 # Application Streamlit principale
│   ├── app.py                       # Point d'entrée de l'application
│   ├── 📁 pagesWeb/                 # Pages de l'interface
│   │   ├── presentation.py          # Page d'accueil
│   │   ├── analyseDonnee.py         # Analyses statistiques
│   │   ├── cartographie.py          # Visualisations géographiques
│   │   ├── modelePrediction.py      # Interface de prédiction
│   │   └── dictionnaire.py          # Dictionnaire des données
│   └── 📁 models/                   # Modèles ML et configurations
│       ├── best_model.pkl           # Modèle entraîné (pickle)
│       ├── model_params.json        # Paramètres et métriques
│       ├── README.md                # Documentation des modèles
│       └── modele.md                # Description détaillée du pipeline ML
│
├── 📁 dev/                          # Scripts de développement
│   ├── lecture_donnee.py            # Chargement et exploration
│   ├── preparation_donnee.py        # Enrichissement (arrondissements, équipements)
│   ├── ajout_service_transport.py   # Ajout des stations de transport
│   ├── analyse_donnee.py            # Analyses exploratoires
│   ├── cartographie.py              # Génération de cartes
│   ├── test_api.py                  # Tests API externes
│   └── 📁 modele/                   # Pipeline de machine learning
│       ├── airbnb_model_training.py # Entraînement & benchmark des modèles ⭐
│       ├── save_model.py            # Tests de sauvegarde
│       └── testModele.py            # Tests divers
│
├── 📁 data/                         # Données brutes et enrichies
│   ├── airbnb_enrichi.csv           # Dataset final (64k+ annonces, 73 colonnes)
│   ├── equipements_stats.csv        # Statistiques des équipements
│   ├── table_nulls.csv              # Analyse des valeurs manquantes
│   └── values_summary.csv           # Résumé des valeurs
│
├── 📁 env_ptut/                     # Environnement virtuel Python
│
├── airbnb_enrichi.csv               # Dataset principal (copie racine)
├── carte_airbnb_paris.html          # Carte interactive générée
└── README.md                        # Ce fichier

```

---

## 🛠️ Technologies Utilisées

### Langage & Environnement
- **Python 3.11+** : Langage principal
- **Environnement virtuel** : `venv` pour l'isolation des dépendances

### Frameworks & Bibliothèques Principales

#### Visualisation & Interface
- **Streamlit** : Framework pour l'application web interactive
- **Matplotlib** : Graphiques statiques
- **Plotly** : Graphiques interactifs
- **Folium** : Cartes géographiques interactives

#### Data Science & Machine Learning
- **Pandas** : Manipulation de données tabulaires
- **NumPy** : Calculs numériques
- **Scikit-learn** : Preprocessing, modèles linéaires, métriques
- **XGBoost** : Gradient boosting optimisé
- **LightGBM** : Gradient boosting léger et rapide
- **CatBoost** : Gradient boosting avec support natif des catégories

#### Géospatial
- **GeoPandas** : Manipulation de données géographiques
- **Shapely** : Opérations géométriques
- **Branca** : Composants de visualisation cartographique

#### Autres
- **Requests** : Appels API HTTP
- **JSON** : Sérialisation des paramètres

---

## ⚙️ Installation & Configuration

### 1. Cloner le Projet

```bash
git clone <url-du-repo>
cd Projet-tutor-
```

### 2. Créer l'Environnement Virtuel

```bash
python -m venv env_ptut
```

### 3. Activer l'Environnement

**Windows (PowerShell)** :
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\env_ptut\Scripts\Activate.ps1
```

**Windows (CMD)** :
```cmd
env_ptut\Scripts\activate.bat
```

**Linux/Mac** :
```bash
source env_ptut/bin/activate
```

### 4. Installer les Dépendances

```bash
pip install -r requirements.txt
```

### Dépendances Principales
```txt
streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=2.0.0
lightgbm>=4.0.0
catboost>=1.2.0
geopandas>=0.14.0
folium>=0.15.0
plotly>=5.17.0
matplotlib>=3.7.0
requests>=2.31.0
```

---

## 🎮 Utilisation

### Lancer l'Application Streamlit

```bash
cd appStreamlit
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:8501`

### Navigation dans l'Application

1. **📝 Présentation du projet** : Découvrez les objectifs et le contexte
2. **📊 Analyse des données** : Explorez les statistiques et visualisations
3. **🗺️ Cartographie des données** : Visualisez les logements sur une carte interactive
4. **📈 Modèle de prédiction** : Prédisez le prix d'un logement en temps réel
5. **📚 Dictionnaire des données** : Consultez la documentation des variables

---

## 🧪 Pipeline de Données

### 1. Chargement des Données Brutes
- Source : Dataset Airbnb Paris (64 690+ annonces)
- Format : CSV avec 73 colonnes

### 2. Enrichissement des Données

#### 2.1 Ajout des Arrondissements (`preparation_donnee.py`)
- Utilisation de l'**API Open Data Paris** pour récupérer les géométries des arrondissements
- Spatial join avec **GeoPandas** pour attribuer chaque annonce à son arrondissement
- Basé sur les coordonnées GPS (latitude, longitude)

#### 2.2 Parsing des Équipements (`preparation_donnee.py`)
- Parsing de la colonne `amenities` (format liste)
- Création de colonnes binaires pour 12 catégories d'équipements :
  - `amenity_wifi` : WiFi, Internet
  - `amenity_tv` : TV, Netflix, HBO, Disney+
  - `amenity_kitchen` : Cuisine équipée
  - `amenity_washer` : Machine à laver
  - `amenity_air_conditioning` : Climatisation
  - `amenity_heating` : Chauffage
  - `amenity_parking` : Parking, garage
  - `amenity_bathtub` : Baignoire, jacuzzi
  - `amenity_shampoo` : Produits de toilette
  - `amenity_coffee` : Machine à café
  - `amenity_pets_allowed` : Animaux acceptés
  - `amenity_pool` : Piscine

#### 2.3 Ajout des Transports en Commun (`ajout_service_transport.py`)
- Création de flags de proximité (rayon de 500m) pour :
  - **Métro** : ~300 stations (lignes 1-14)
  - **RER** : ~50 stations (lignes A-E)
  - **Tramway** : ~90 stations (T1-T9)
- Calcul de la distance haversine (formule géographique)
- Variables générées :
  - `flag_metro` : 1 si métro à proximité
  - `flag_rer` : 1 si RER à proximité
  - `flag_tram` : 1 si tramway à proximité
  - `distance_metro_m` : Distance en mètres à la station la plus proche

### 3. Nettoyage & Filtrage
- Suppression des valeurs manquantes critiques
- Filtrage des outliers de prix (0 < prix ≤ 500€)
- Validation des coordonnées GPS

### 4. Export Final
- Fichier : `data/airbnb_enrichi.csv`
- ~60 000 annonces exploitables
- 73 colonnes (features originales + enrichissements)

---

## 🤖 Modèle de Machine Learning

### Pipeline Complet (`dev/modele/airbnb_model_training.py`)

#### 1. Préparation des Features
- **Sélection** : Uniquement les colonnes 100% complètes
- **Variables catégorielles** : 
  - `neighbourhood` (arrondissement)
  - `property_type` (type de propriété)
  - `room_type` (type de chambre)
  - `instant_bookable` (réservation instantanée)
- **Variables numériques** : ~50+ features (GPS, capacité, équipements, transports, etc.)
- **Transformation de la cible** : `log1p(price)` pour réduire le skew

#### 2. Preprocessing
- **Encodage ordinal** pour les variables catégorielles (valeurs inconnues → -1)
- **StandardScaler** uniquement pour les modèles linéaires
- Pipeline Scikit-learn : `ColumnTransformer` → `Model`

#### 3. Benchmark de 6 Modèles

| Modèle | Type | Hyperparamètres Clés |
|--------|------|----------------------|
| **Ridge** | Régression linéaire régularisée | α=10.0 |
| **Lasso** | Régression linéaire régularisée | α=0.001 |
| **Random Forest** | Ensemble d'arbres | 200 arbres, depth=15 |
| **XGBoost** | Gradient boosting | 800 estimateurs, lr=0.05 |
| **LightGBM** ⭐ | Gradient boosting | 800 estimateurs, lr=0.05 |
| **CatBoost** | Gradient boosting | 800 itérations, depth=6 |

#### 4. Métriques d'Évaluation
- **MAE** (Mean Absolute Error) : Erreur moyenne en euros
- **RMSE** (Root Mean Squared Error) : Erreur quadratique
- **R²** : Pourcentage de variance expliquée
- **MAPE** : Erreur en pourcentage

#### 5. Résultats Typiques
Le meilleur modèle (généralement **LightGBM** ou **XGBoost**) atteint :
- MAE : ~15-20€
- RMSE : ~25-30€
- R² : ~0.75-0.80
- MAPE : ~20-25%

#### 6. Feature Importance
Les variables les plus influentes sont généralement :
1. **Localisation GPS** (latitude, longitude) : ~30-40%
2. **Capacité d'accueil** (`accommodates`) : ~15-20%
3. **Type de logement** (`property_type`, `room_type`) : ~10-15%
4. **Arrondissement** (`neighbourhood`) : ~8-12%
5. **Contraintes de séjour** (`minimum_nights`) : ~5-8%
6. **Proximité transports** (flags) : ~3-5%
7. **Équipements** (amenities) : ~2-4% cumulés

#### 7. Export
- **`best_model.pkl`** : Pipeline complet sérialisé (preprocessing + modèle)
- **`model_params.json`** : Métadonnées, métriques, feature importance

---

## 📊 Dataset - Variables Clés

### Variables Cibles
- **`price`** : Prix par nuit en euros (variable à prédire)

### Variables Géographiques
- **`latitude`**, **`longitude`** : Coordonnées GPS
- **`arrondissement`** : Arrondissement parisien (1er au 20e)
- **`neighbourhood`** : Quartier détaillé

### Variables Descriptives
- **`property_type`** : Type de propriété (Apartment, House, Loft, etc.)
- **`room_type`** : Type de chambre (Entire home, Private room, Shared room)
- **`accommodates`** : Nombre de personnes maximum
- **`bedrooms`** : Nombre de chambres
- **`bathrooms`** : Nombre de salles de bain
- **`beds`** : Nombre de lits

### Variables de Séjour
- **`minimum_nights`** : Nombre minimum de nuits
- **`maximum_nights`** : Nombre maximum de nuits
- **`instant_bookable`** : Réservation instantanée (0/1)

### Variables d'Équipements (12 catégories binaires)
- **`amenity_wifi`**, **`amenity_tv`**, **`amenity_kitchen`**, etc.

### Variables de Transport (3 flags binaires)
- **`flag_metro`** : Métro à moins de 500m
- **`flag_rer`** : RER à moins de 500m
- **`flag_tram`** : Tramway à moins de 500m
- **`distance_metro_m`** : Distance au métro le plus proche

### Variables d'Hôte
- **`host_id`** : Identifiant de l'hôte
- **`host_since`** : Date d'inscription de l'hôte
- **`host_location`** : Localisation de l'hôte

---

## 📈 Cas d'Usage

### Pour les Voyageurs
- 🔍 **Comparer les prix** par quartier avant de réserver
- 📍 **Visualiser** la distribution des logements sur une carte
- 💡 **Comprendre** quels facteurs influencent les prix

### Pour les Hôtes Airbnb
- 💰 **Estimer** le prix optimal de leur logement
- 📊 **Identifier** les équipements qui ajoutent le plus de valeur
- 🎯 **Positionner** leur offre par rapport au marché

### Pour les Analystes
- 📉 **Analyser** les tendances du marché locatif parisien
- 🗺️ **Identifier** les zones sous/sur-valorisées
- 🔬 **Expérimenter** avec différents modèles de machine learning

---

## 🚧 Limitations & Perspectives

### Limitations Actuelles
- ⚠️ **Données statiques** : Pas de mise à jour en temps réel
- 📅 **Pas de saisonnalité** : Le modèle ne prend pas en compte les variations temporelles
- 🌍 **Périmètre limité** : Uniquement Paris intra-muros
- 🔄 **Prédictions moyennes** : Le modèle prédit un prix moyen, pas les variations jour par jour

### Améliorations Futures
- 🔄 **Scraping automatique** : Mise à jour régulière des données Airbnb
- 📅 **Prédiction temporelle** : Intégrer les événements (JO 2024, Fashion Week, etc.)
- 🌡️ **Variables météo** : Impact de la saisonnalité
- 🧠 **Deep Learning** : Tester des architectures neuronales (LSTM pour séries temporelles)
- 📱 **API REST** : Exposer le modèle via FastAPI/Flask
- 🌐 **Extension géographique** : Étendre à d'autres villes (Lyon, Bordeaux, Marseille)
- 📸 **Analyse d'images** : Utiliser les photos des logements (CNN)

---

## 🤝 Contribution

Ce projet est académique et n'accepte pas de contributions externes. Cependant, n'hésitez pas à :
- 🐛 Signaler des bugs
- 💡 Proposer des améliorations
- 🌟 Utiliser ce projet comme référence pour vos propres analyses

---

## 📄 Licence

Projet académique - Tous droits réservés  
© 2024-2026 Alice & Claudia - Université de Poitiers

---

## 📞 Contact

Pour toute question relative au projet :
- **Institution** : ENSAR - Université de Poitiers 
- **Cadre** : Projet Tuteuré - Science des Données

---

<div align="center">
</div>
