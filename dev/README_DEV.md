# 🛠️ Dossier `dev/` - Scripts de Développement

Ce dossier contient l'ensemble des scripts Python utilisés pour le développement du projet Airbnb Paris Analytics. Ces scripts constituent le **pipeline de traitement des données** depuis le chargement initial jusqu'à l'entraînement du modèle de machine learning.

---

## 📋 Vue d'Ensemble

Le dossier `dev/` regroupe les scripts de traitement de données et d'analyse exploratoire qui ont permis de :
1. Charger et filtrer les données brutes Airbnb
2. Enrichir le dataset avec des informations géographiques et fonctionnelles
3. Analyser et visualiser les données
4. Générer des cartes interactives
5. Entraîner et évaluer des modèles de prédiction

**Note importante** : Ces scripts sont des **outils de développement** et ne sont pas intégrés directement dans l'application Streamlit finale. Ils ont servi à préparer les données et les modèles utilisés par l'application.

---

## 📂 Structure

```
dev/
├── lecture_donnee.py              # 1️⃣ Chargement initial des données
├── preparation_donnee.py          # 2️⃣ Enrichissement (arrondissements + équipements)
├── ajout_service_transport.py     # 3️⃣ Ajout des transports en commun
├── analyse_donnee.py              # 4️⃣ Analyses exploratoires et visualisations
├── 📁 cartographie/               # 5️⃣ Génération de cartes interactives
│   ├── cartographie.py            #    → Carte de chaleur (heatmap)
│   ├── cartographie_points.py     #    → Carte avec marqueurs individuels
│   └── carte_airbnb_paris.html    #    → Résultat HTML exporté
└── 📁 modele/                     # 6️⃣ Pipeline de machine learning
    ├── airbnb_model_training.py   #    → Script principal d'entraînement
    ├── save_model.py              #    → Tests de sauvegarde
    ├── testModele.py              #    → Tests divers
    └── modele.md                  #    → Documentation détaillée
```

---

## 🔄 Pipeline de Traitement des Données

### Étape 1️⃣ : Chargement des Données Brutes

**📄 Fichier** : [`lecture_donnee.py`](lecture_donnee.py)

#### 🎯 Objectif
Charger le dataset Airbnb brut et filtrer uniquement les annonces situées à Paris.

#### ⚙️ Fonctionnalités
- **Détection automatique de l'encodage** : Utilise `chardet` pour détecter l'encodage du fichier CSV
- **Gestion multi-encodage** : Essaie plusieurs encodages (UTF-8, détecté, Latin-1) pour garantir le chargement
- **Filtrage géographique** : Conserve uniquement les annonces où `city == "Paris"`
- **Export optimisé** : Sauvegarde en `utf-8-sig` pour éviter les problèmes d'encodage futurs

#### 📊 Données en Entrée
- **Fichier source** : `data/Listings.csv` (dataset brut Airbnb)
- **Taille typique** : ~100k+ annonces (France entière)

#### 📤 Données en Sortie
- **Fichier exporté** : `data/datalistings_paris.csv`
- **Contenu** : Uniquement les annonces parisiennes (~65k annonces)
- **Encodage** : UTF-8 avec BOM

#### 🚀 Utilisation
```bash
python lecture_donnee.py
```

---

### Étape 2️⃣ : Enrichissement Géographique et Équipements

**📄 Fichier** : [`preparation_donnee.py`](preparation_donnee.py)

#### 🎯 Objectif
Enrichir le dataset avec les arrondissements parisiens et créer des variables binaires pour les équipements.

#### ⚙️ Fonctionnalités Principales

##### 🗺️ A. Ajout de la Colonne Arrondissement
- **Source** : API Open Data Paris (`arrondissements/exports/geojson`)
- **Méthode** : Spatial join avec GeoPandas
- **Principe** : 
  - Conversion des annonces en GeoDataFrame avec `points_from_xy(longitude, latitude)`
  - Intersection spatiale (`sjoin`) avec les polygones d'arrondissements
  - Attribution automatique selon la position GPS

##### 🏠 B. Parsing des Équipements (Amenities)
- **Variable source** : `amenities` (format liste Python en string)
- **Parsing** : `ast.literal_eval()` pour convertir en liste réelle
- **Catégorisation** : Création de 12 colonnes binaires (0/1)

#### 📊 Catégories d'Équipements Créées

| Colonne | Mots-clés recherchés |
|---------|---------------------|
| `amenity_wifi` | wifi, internet |
| `amenity_tv` | tv, television, netflix, hbo, disney, apple tv, chromecast |
| `amenity_kitchen` | kitchen, oven, microwave, fridge, refrigerator, cooking |
| `amenity_washer` | washer, dryer, washing |
| `amenity_air_conditioning` | air condition, ac, split-type, portable ac, climati |
| `amenity_heating` | heat, chauffage |
| `amenity_parking` | parking, garage, ev charger |
| `amenity_bathtub` | bathtub, bath, hot tub, jacuzzi, soaking tub |
| `amenity_shampoo` | shampoo, conditioner, body wash, body soap, shower gel |
| `amenity_coffee` | coffee, espresso, nespresso, keurig, french press |
| `amenity_pets_allowed` | pet, dog, cat allowed |
| `amenity_pool` | pool, piscine |

#### 🔍 Méthode de Matching
- **Recherche insensible à la casse** : Conversion en `lower()` avant matching
- **Matching par mots-clés** : Recherche de sous-chaînes dans chaque équipement
- **Résultat binaire** : 1 si au moins un mot-clé est trouvé, 0 sinon

#### 📊 Données en Entrée
- `data/datalistings_paris.csv` (résultat de l'étape 1)

#### 📤 Données en Sortie
- **Fichier exporté** : `data/airbnb_enrichi_v1.csv`
- **Nouvelles colonnes** : 
  - `arrondissement` (1er au 20e)
  - `amenity_*` (12 colonnes binaires)
  - `amenities_parsed` (liste Python)

#### 🚀 Utilisation
```bash
python preparation_donnee.py
```

---

### Étape 3️⃣ : Ajout des Transports en Commun

**📄 Fichier** : [`ajout_service_transport.py`](ajout_service_transport.py)

#### 🎯 Objectif
Enrichir chaque annonce avec des informations sur la proximité des transports en commun (métro, RER, tramway).

#### ⚙️ Fonctionnalités

##### 🚇 Base de Données Statique de Stations
Le script contient une base embarquée de **~441 stations** de transport :
- **Métro** : Lignes 1 à 14 (~300 stations)
- **RER** : Lignes A à E (~50 stations)
- **Tramway** : Lignes T1 à T9 (~90 stations)

**Format** :
```python
("Nom Station", latitude, longitude, "type")
# Exemple :
("Châtelet", 48.8598, 2.3469, "metro")
```

##### 📏 Calcul de Proximité
- **Méthode** : Distance haversine (distance géodésique)
- **Rayon de recherche** : 500 mètres
- **Optimisation** : Filtrage initial par bounding box (±0.005° ≈ 550m)

##### 🎯 Variables Créées

| Colonne | Description | Type |
|---------|-------------|------|
| `flag_metro` | Métro à moins de 500m | Binaire (0/1) |
| `flag_rer` | RER à moins de 500m | Binaire (0/1) |
| `flag_tram` | Tramway à moins de 500m | Binaire (0/1) |
| `distance_metro_m` | Distance en mètres au métro le plus proche | Float |
| `distance_rer_m` | Distance en mètres au RER le plus proche | Float |
| `distance_tram_m` | Distance en mètres au tram le plus proche | Float |

#### 🔬 Formule Haversine
Calcul de la distance entre deux points GPS en tenant compte de la courbure terrestre :

```python
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Rayon de la Terre en mètres
    φ1 = radians(lat1)
    φ2 = radians(lat2)
    Δφ = radians(lat2 - lat1)
    Δλ = radians(lon2 - lon1)
    a = sin(Δφ/2)**2 + cos(φ1) * cos(φ2) * sin(Δλ/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c  # Distance en mètres
```

#### 📊 Données en Entrée
- `data/airbnb_enrichi_v1.csv` (résultat de l'étape 2)

#### 📤 Données en Sortie
- **Fichier exporté** : `data/airbnb_enrichi.csv` ⭐ (dataset final)
- **Nouvelles colonnes** : 6 colonnes de proximité transport

#### 🚀 Utilisation
```bash
python ajout_service_transport.py
```

#### 💡 Note Importante
Les coordonnées des stations proviennent de sources Open Data (OSM, RATP, SNCF) et sont statiques. Pour une mise à jour, il faudrait interroger les APIs officielles, ce qui nécessite des clés d'accès et une connexion réseau.

---

### Étape 4️⃣ : Analyses Exploratoires et Visualisations

**📄 Fichier** : [`analyse_donnee.py`](analyse_donnee.py)

#### 🎯 Objectif
Analyser la qualité des données et générer des visualisations pour l'exploration du dataset enrichi.

#### ⚙️ Fonctionnalités

##### 📊 A. Analyse des Valeurs Manquantes
- **Calcul** : Nombre et pourcentage de valeurs nulles par colonne
- **Tri** : Par ordre décroissant de pourcentage
- **Export tableau** : `data/table_nulls.csv`

##### 📈 B. Visualisation des Données Manquantes
- **Graphique en barres horizontales** : Une barre par colonne avec valeurs manquantes
- **Code couleur** :
  - 🔴 **Rouge** : > 50% de valeurs manquantes (critique)
  - 🟠 **Orange** : 20-50% (attention)
  - 🟡 **Jaune** : < 20% (acceptable)
- **Annotations** : Nombre exact de valeurs manquantes sur chaque barre
- **Lignes de référence** : Seuils à 20% et 50%
- **Export** : `data/missing_bar.png` (haute résolution, 150 dpi)

##### 📋 C. Statistiques Descriptives
- Résumé statistique complet : min, max, moyenne, médiane, écart-type
- Distribution des variables catégorielles
- Détection des outliers

#### 📊 Données en Entrée
- `data/airbnb_enrichi.csv` (dataset final)

#### 📤 Fichiers Générés
- `data/table_nulls.csv` : Tableau des valeurs manquantes
- `data/missing_bar.png` : Graphique des valeurs manquantes
- `data/values_summary.csv` : Statistiques descriptives (si implémenté)

#### 🚀 Utilisation
```bash
python analyse_donnee.py
```

#### 📌 Utilité
Ce script permet de :
- ✅ Valider la qualité du nettoyage de données
- ✅ Identifier les colonnes à exclure pour le modèle ML
- ✅ Comprendre la distribution des variables
- ✅ Détecter d'éventuelles anomalies

---

### Étape 5️⃣ : Génération de Cartes Interactives

**📁 Dossier** : [`cartographie/`](cartographie/)

Ce sous-dossier contient les scripts de visualisation géographique utilisant la bibliothèque **Folium**.

#### 📄 Fichier 1 : `cartographie.py` - Carte de Chaleur

##### 🎯 Objectif
Générer une **heatmap** (carte de chaleur) montrant la densité et les prix des logements Airbnb à Paris.

##### ⚙️ Fonctionnalités
- **Carte de base Folium** centrée sur Paris (48.8566, 2.3522)
- **Heatmap plugin** : Visualisation de la densité d'annonces
- **Gradient de couleur** : Reflète la concentration des logements
- **Interactivité** : Zoom, déplacement, info-bulles
- **Couches multiples** : 
  - Fond de carte OpenStreetMap
  - Couche heatmap superposée

##### 📊 Données Utilisées
- Coordonnées GPS : `latitude`, `longitude`
- Optionnel : `price` comme poids de la heatmap

##### 📤 Sortie
- **Fichier HTML interactif** : Carte visualisable dans un navigateur
- **Taille légère** : Optimisée pour le web

#### 📄 Fichier 2 : `cartographie_points.py` - Carte avec Marqueurs

##### 🎯 Objectif
Générer une carte avec des **marqueurs individuels** pour chaque annonce, permettant de cliquer pour voir les détails.

##### ⚙️ Fonctionnalités
- **Marqueurs cliquables** : Un marqueur par annonce
- **Info-bulles (popups)** : Affichage au clic avec :
  - Nom du logement
  - Prix par nuit
  - Type de propriété
  - Arrondissement
  - Équipements principaux
- **Code couleur** : Marqueurs colorés selon le prix ou le type de logement
- **Clustering** (optionnel) : Regroupement automatique des marqueurs proches au zoom éloigné
- **Filtres** : Possibilité de filtrer par arrondissement ou gamme de prix

##### 📊 Données Utilisées
- Coordonnées : `latitude`, `longitude`
- Métadonnées : `name`, `price`, `property_type`, `room_type`, `arrondissement`

##### 📤 Sortie
- **Fichier HTML** : `carte_airbnb_paris.html`
- **Interactivité avancée** : Navigation, zoom, filtres

#### 📤 Fichier Résultat : `carte_airbnb_paris.html`

Carte HTML interactive générée, prête à être :
- 📂 Ouverte directement dans un navigateur
- 🌐 Intégrée dans une page web
- 📧 Partagée avec des collaborateurs
- 📱 Visualisée sur mobile

#### 🚀 Utilisation

**Générer la heatmap** :
```bash
python cartographie/cartographie.py
```

**Générer la carte avec marqueurs** :
```bash
python cartographie/cartographie_points.py
```

**Visualiser le résultat** :
```bash
# Ouvrir avec le navigateur par défaut
start cartographie/carte_airbnb_paris.html  # Windows
open cartographie/carte_airbnb_paris.html   # Mac
xdg-open cartographie/carte_airbnb_paris.html  # Linux
```

---

### Étape 6️⃣ : Pipeline de Machine Learning

**📁 Dossier** : [`modele/`](modele/)

Ce sous-dossier contient tous les scripts liés à l'entraînement et l'évaluation des modèles de prédiction.

#### 📄 Fichier Principal : `airbnb_model_training.py` ⭐

**Documentation complète** : Voir [`modele/modele.md`](modele/modele.md)

##### 🎯 Objectif
Entraîner et comparer 6 modèles de machine learning pour prédire les prix Airbnb, puis exporter le meilleur.

##### 📊 Pipeline Complet
1. Chargement de `data/airbnb_enrichi.csv`
2. Filtrage des outliers (0 < prix ≤ 500€)
3. Sélection des features (colonnes 100% complètes)
4. Transformation log1p(price) pour réduire le skew
5. Benchmark de 6 modèles (Ridge, Lasso, RF, XGBoost, LightGBM, CatBoost)
6. Évaluation (MAE, RMSE, R², MAPE)
7. Analyse feature importance
8. Export du meilleur modèle

##### 📤 Fichiers Générés
- `best_model.pkl` : Pipeline complet (preprocessing + modèle)
- `model_params.json` : Métadonnées et métriques

#### 📄 Fichiers de Test
- **`save_model.py`** : Tests de sérialisation pickle
- **`testModele.py`** : Expérimentations diverses

---

## 🔗 Dépendances entre Scripts

Le pipeline suit un ordre séquentiel strict :

```
lecture_donnee.py
       ↓
preparation_donnee.py
       ↓
ajout_service_transport.py
       ↓
       ├─→ analyse_donnee.py (analyse parallèle)
       ├─→ cartographie/*.py (visualisation parallèle)
       └─→ modele/airbnb_model_training.py (modélisation)
```

**Important** : Chaque étape dépend de la précédente. Ne pas exécuter dans le désordre.

---

## 🚀 Exécution du Pipeline Complet

Pour reproduire l'intégralité du traitement des données :

```bash
# Étape 1 : Chargement
python dev/lecture_donnee.py

# Étape 2 : Enrichissement géographique et équipements
python dev/preparation_donnee.py

# Étape 3 : Ajout des transports
python dev/ajout_service_transport.py

# Étape 4 : Analyses exploratoires
python dev/analyse_donnee.py

# Étape 5 : Cartographie
python dev/cartographie/cartographie.py
python dev/cartographie/cartographie_points.py

# Étape 6 : Entraînement du modèle
python dev/modele/airbnb_model_training.py
```

**Durée totale estimée** : ~10-15 minutes (selon la machine)

---

## 📦 Dépendances Requises

```bash
pip install pandas numpy chardet geopandas shapely folium branca matplotlib seaborn scikit-learn xgboost lightgbm catboost
```

Ou via requirements.txt :
```bash
pip install -r requirements.txt
```

---

## 📊 Données Produites

### Fichiers Intermédiaires
| Fichier | Étape | Contenu |
|---------|-------|---------|
| `data/datalistings_paris.csv` | 1 | Données brutes Paris uniquement |
| `data/airbnb_enrichi_v1.csv` | 2 | + Arrondissements + Équipements |
| `data/airbnb_enrichi.csv` ⭐ | 3 | + Transports (dataset final) |

### Fichiers d'Analyse
| Fichier | Script | Description |
|---------|--------|-------------|
| `data/table_nulls.csv` | analyse_donnee.py | Valeurs manquantes |
| `data/missing_bar.png` | analyse_donnee.py | Graphique des nulls |
| `data/equipements_stats.csv` | analyse_donnee.py | Stats équipements |
| `cartographie/carte_airbnb_paris.html` | cartographie/*.py | Carte interactive |

### Fichiers de Modélisation
| Fichier | Script | Description |
|---------|--------|-------------|
| `best_model.pkl` | airbnb_model_training.py | Modèle ML entraîné |
| `model_params.json` | airbnb_model_training.py | Métriques et config |

---

## 🎓 Notes Pédagogiques

### Bonnes Pratiques Appliquées
✅ **Modularité** : Un script = une tâche précise  
✅ **Pipeline séquentiel** : Dépendances claires entre étapes  
✅ **Exports intermédiaires** : Possibilité de reprendre à n'importe quelle étape  
✅ **Gestion des encodages** : Détection automatique pour éviter les erreurs  
✅ **Validation des données** : Analyses exploratoires avant modélisation  
✅ **Documentation** : README et commentaires dans le code  

### Concepts Techniques Illustrés
🔹 **ETL** (Extract, Transform, Load)  
🔹 **Feature Engineering** : Création de variables pertinentes  
🔹 **Géospatial Join** : Intersection spatiale avec GeoPandas  
🔹 **Text Parsing** : Extraction d'informations de colonnes textuelles  
🔹 **Distance géodésique** : Formule haversine pour calculs GPS  
🔹 **Pipeline ML** : ColumnTransformer, preprocessing, benchmark  
🔹 **Sérialisation** : Pickle pour sauvegarder les modèles  

---

## 🚨 Limitations & Améliorations Possibles

### Limitations Actuelles
⚠️ **Données statiques** : Pas de connexion API en temps réel  
⚠️ **Stations embarquées** : Base de données de transports figée  
⚠️ **Pas de validation temporelle** : Le modèle ne gère pas la saisonnalité  
⚠️ **Scripts manuels** : Pas d'automatisation (pas de workflow orchestrator)  

### Améliorations Futures
🔮 **Apache Airflow** : Orchestration automatique du pipeline  
🔮 **API RATP/SNCF** : Mise à jour dynamique des stations de transport  
🔮 **CI/CD** : Automatisation des tests et du déploiement  
🔮 **Docker** : Conteneurisation pour reproductibilité  
🔮 **DVC** : Versioning des données (Data Version Control)  
🔮 **MLflow** : Tracking des expériences ML  
🔮 **Great Expectations** : Validation automatique de la qualité des données  

---

<div align="center">

**🛠️ Pipeline de Data Science complet - Du CSV brut au modèle en production 🚀**

</div>
