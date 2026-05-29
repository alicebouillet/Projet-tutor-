# 🎨 Application Streamlit - Interface Utilisateur

Ce dossier contient l'**application web interactive** développée avec Streamlit pour visualiser, analyser et prédire les prix Airbnb à Paris. C'est le **produit final** du projet, accessible aux utilisateurs finaux.

---

## 📋 Vue d'Ensemble

L'application **Airbnb Paris Analytics** est une plateforme web complète qui permet aux utilisateurs d'explorer les données Airbnb parisiennes de manière interactive, sans nécessiter de connaissances en programmation.

### 🎯 Public Cible
- 🧳 **Voyageurs** : Comparer les prix et trouver le meilleur logement
- 🏠 **Hôtes Airbnb** : Optimiser leur stratégie de pricing
- 📊 **Analystes** : Explorer les tendances du marché locatif
- 🎓 **Étudiants/Chercheurs** : Étudier les données géospatiales et le machine learning

### ✨ Points Forts
- ⚡ **Interface moderne et responsive** avec une charte graphique professionnelle
- 🎨 **Visualisations interactives** (Altair, Folium, Plotly)
- 🤖 **Prédiction en temps réel** avec des modèles de machine learning
- 🗺️ **Cartographie avancée** avec GeoPandas et Folium
- 💾 **Cache intelligent** pour des performances optimales
- 📱 **Compatible mobile** grâce au design adaptatif

---

## 📂 Structure de l'Application

```
appStreamlit/
├── app.py                        # 🚀 Point d'entrée principal
│
├── 📁 pagesWeb/                  # Pages de l'application
│   ├── presentation.py           # Page 1 : Accueil et présentation
│   ├── analyseDonnee.py          # Page 2 : Analyses statistiques
│   ├── cartographie.py           # Page 3 : Cartographie interactive
│   ├── modelePrediction.py       # Page 4 : Prédiction de prix
│   ├── dictionnaire.py           # Page 5 : Dictionnaire des variables
│   ├── analyseDonnee_backup.py   # (backup)
│   ├── cartographie_backup.py    # (backup)
│   └── modelePrediction_expert.py # (version avancée)
│
└── 📁 models/                    # Modèles et configurations
    ├── airbnb_model.pkl # Modèle ML entraîné (pickle)
    ├── model_params.json         # Paramètres et métriques du modèle
    ├── README.md                 # Documentation des modèles
    ├── GUIDE_JE_SAIS_PAS.md      # Guide de debugging
    └── IMPACT_VALEURS_INCONNUES.md # Documentation technique
```

---

## 🚀 Lancement de l'Application

### Prérequis
- Python 3.11+
- Environnement virtuel activé (`env_ptut`)
- Dépendances installées (`requirements.txt`)

### Commandes de Lancement

#### Option 1 : Depuis la racine du projet
```bash
cd appStreamlit
streamlit run app.py
```

#### Option 2 : Avec activation de l'environnement (Windows PowerShell)
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\env_ptut\Scripts\Activate.ps1
cd appStreamlit
streamlit run app.py
```

#### Option 3 : Depuis n'importe quel répertoire
```bash
streamlit run appStreamlit/app.py
```

### 🌐 Accès à l'Application
Une fois lancée, l'application s'ouvre automatiquement dans votre navigateur à l'adresse :
```
http://localhost:8501
```

---

## 📄 Fichier Principal : `app.py`

### 🎯 Rôle
Point d'entrée de l'application qui gère :
- Configuration globale de Streamlit
- Navigation entre les pages via la sidebar
- Routing vers les modules appropriés

### ⚙️ Configuration
```python
st.set_page_config(
    page_title="Airbnb Analytics",    # Titre de l'onglet navigateur
    layout="wide",                    # Mode large pour exploiter l'espace
    initial_sidebar_state="expanded"  # Sidebar ouverte par défaut
)
```

### 🧭 Navigation
L'application utilise un **menu radio** dans la sidebar pour naviguer entre 5 pages :
1. 📝 Présentation du projet
2. 📊 Analyse des données
3. 🗺️ Cartographie des données
4. 📈 Modèle de prédiction
5. 📚 Dictionnaire des données

### 🔄 Architecture Modulaire
Chaque page est un module indépendant avec une fonction `app()` :
```python
if onglet == "📝 Présentation du projet":
    presentation.app()
elif onglet == "📊 Analyse des données":
    analyseDonnee.app()
# ... etc.
```

---

## 📑 Pages de l'Application

### Page 1 : 📝 Présentation du Projet

**Fichier** : [`pagesWeb/presentation.py`](pagesWeb/presentation.py)

#### 🎯 Objectif
Page d'accueil présentant le projet et ses objectifs de manière visuelle et engageante.

#### 🎨 Contenu
- **Hero section** avec dégradé coloré et typographie moderne
- **Statistiques clés** :
  - 📅 Source de données (Données Airbnb)
  - 🏠 Nombre d'annonces (~60 000)
  - 📍 Arrondissements couverts (20)
- **Présentation de l'outil** : Description du projet et de ses fonctionnalités
- **Objectifs du projet** : Liste des 4 objectifs principaux
- **Fonctionnalités disponibles** : Aperçu des 5 pages

#### 🎨 Design
- **Palette de couleurs** :
  - `TEAL` (#C7EFCF) : Vert menthe (couleur principale)
  - `SAGE` (#FFCCBA) : Saumon pastel (accents)
  - `GOLD` (#F0B67F) : Or doux (highlights)
  - `BRICK` (#FE5F55) : Rouge brique (alertes)
  - `DARK` (#010221) : Bleu nuit (texte)
- **Cartes statistiques** avec dégradés et ombres portées
- **Sections structurées** avec bordures colorées

#### 📊 Fonctions Utilitaires
```python
_get_data_stats()  # Récupère les statistiques du dataset
```

---

### Page 2 : 📊 Analyse des Données

**Fichier** : [`pagesWeb/analyseDonnee.py`](pagesWeb/analyseDonnee.py)

#### 🎯 Objectif
Fournir des analyses statistiques et des visualisations interactives sur les données Airbnb.

#### 📊 Contenu

##### A. Indicateurs Clés (KPIs)
4 cartes affichant :
- 🏠 **Nombre de logements** total
- 💰 **Prix moyen** par nuit
- 📊 **Prix médian** par nuit
- 📍 **Nombre d'arrondissements** couverts

##### B. Analyses par Type de Logement
- **Tableau récapitulatif** : count, mean, median, min, max par `room_type`
- **Types** : Entire home/apt, Private room, Shared room, Hotel room

##### C. Prix Moyens par Arrondissement
- **Graphique en barres horizontales** (Altair) : Top 15 arrondissements
- **Tri décroissant** par prix moyen
- **Code couleur** selon le niveau de prix

##### D. Distribution des Prix
- **Histogramme interactif** : Répartition des prix par tranches
- **Filtres** : Possibilité d'exclure les valeurs extrêmes
- **Statistiques** : Moyenne, médiane, écart-type

##### E. Équipements Populaires
- **Graphique en barres** : Top équipements (WiFi, cuisine, TV, etc.)
- **Pourcentages** : Part de logements disposant de chaque équipement

##### F. Corrélations
- **Heatmap** : Matrice de corrélation entre variables numériques
- **Variables analysées** : prix, accommodates, bedrooms, minimum_nights, etc.

#### ⚙️ Fonctions Principales
```python
_load_data()                    # Chargement avec cache
_compute_kpis(df)               # Calcul des KPIs
_compute_room_type_stats(df)   # Stats par type de logement
_compute_price_quartier(df)    # Prix par arrondissement
```

#### 🎨 Visualisations
- **Altair** : Graphiques interactifs avec tooltips
- **Pandas Styler** : Tableaux formatés avec codes couleur
- **Streamlit metrics** : Cartes de KPIs natives

---

### Page 3 : 🗺️ Cartographie des Données

**Fichier** : [`pagesWeb/cartographie.py`](pagesWeb/cartographie.py)

#### 🎯 Objectif
Visualiser géographiquement la distribution des logements Airbnb à Paris avec des cartes interactives.

#### 🗺️ Types de Visualisations

##### A. Carte Choroplèthe (Heatmap par Arrondissement)
- **Polygones colorés** : Chaque arrondissement est coloré selon le prix moyen
- **Gradient de couleur** : Du vert (prix bas) au rouge (prix élevé)
- **Info-bulles** : Au survol, affiche :
  - Nom de l'arrondissement
  - Prix moyen
  - Nombre de logements
  - Prix médian

##### B. Carte de Chaleur (Densité)
- **Heatmap plugin** : Visualisation de la densité d'annonces
- **Gradient de chaleur** : Zones denses = rouge, zones clairsemées = bleu
- **Intensité** : Basée sur le nombre de logements par zone

##### C. Carte avec Marqueurs Individuels
- **Marqueurs cliquables** : Un point par annonce
- **Clustering** : Regroupement automatique au zoom éloigné
- **Popups** : Au clic, affiche les détails du logement

#### 🎛️ Filtres Interactifs
- **Arrondissements** : Sélection multiple via multiselect
- **Gamme de prix** : Slider pour filtrer par prix (0-1000€)
- **Type de logement** : Filtrage par property_type
- **Capacité d'accueil** : Filtrage par nombre de personnes

#### ⚙️ Technologies Utilisées
- **Folium** : Génération de cartes interactives
- **GeoPandas** : Manipulation de données géospatiales
- **streamlit_folium** : Intégration Folium dans Streamlit
- **API Open Data Paris** : Récupération des contours d'arrondissements

#### 🎨 Personnalisation
- **Fond de carte** : OpenStreetMap (par défaut)
- **Centre** : Paris (48.8566°N, 2.3522°E)
- **Zoom initial** : 12 (vue d'ensemble de Paris)
- **Palette de couleurs** : YlOrRd (jaune-orange-rouge)

#### ⚙️ Fonctions Principales
```python
_load_data()                          # Chargement des annonces
_load_arrondissements()               # Chargement des polygones
_compute_arrondissement_stats(df, arr) # Agrégation par arrondissement
_create_choropleth_map(stats)         # Création de la carte choroplèthe
_create_heatmap(df)                   # Création de la heatmap
_create_cluster_map(df)               # Création de la carte avec marqueurs
```

---

### Page 4 : 📈 Modèle de Prédiction

**Fichier** : [`pagesWeb/modelePrediction.py`](pagesWeb/modelePrediction.py)

#### 🎯 Objectif
Permettre aux utilisateurs de **prédire le prix d'un logement Airbnb** en temps réel en saisissant ses caractéristiques.

#### 🤖 Pipeline de Prédiction

##### 1. Chargement du Modèle
```python
model = joblib.load("models/airbnb_model.pkl")
params = json.load(open("models/model_params.json"))
```

##### 2. Interface de Saisie
L'utilisateur renseigne les caractéristiques du logement via des widgets Streamlit :

**Localisation** :
- 📍 **Arrondissement** : Selectbox (1er au 20e)
- 🗺️ **Coordonnées GPS** : Sliders pour latitude/longitude (pré-remplis selon l'arrondissement)

**Logement** :
- 🏠 **Type de propriété** : Selectbox (Apartment, House, Loft, etc.)
- 🛏️ **Type de chambre** : Radio buttons (Entire home, Private room, Shared room)
- 👥 **Capacité d'accueil** : Number input (1-16 personnes)

**Conditions de Séjour** :
- 📅 **Nuits minimum** : Number input (1-365)
- 📅 **Nuits maximum** : Number input (1-1000)
- ⚡ **Réservation instantanée** : Checkbox

**Équipements** (12 checkboxes) :
- ☑️ WiFi, TV, Cuisine, Machine à laver
- ☑️ Climatisation, Chauffage, Parking, Baignoire
- ☑️ Produits de toilette, Machine à café, Animaux acceptés, Piscine

**Transports** (3 checkboxes) :
- 🚇 Métro à proximité (<500m)
- 🚊 RER à proximité (<500m)
- 🚋 Tramway à proximité (<500m)

##### 3. Préparation des Features
```python
input_data = {
    "neighbourhood": arrondissement,
    "property_type": property_type,
    "room_type": room_type,
    "accommodates": accommodates,
    "latitude": latitude,
    "longitude": longitude,
    "minimum_nights": min_nights,
    "maximum_nights": max_nights,
    "instant_bookable": int(instant_bookable),
    "amenity_wifi": int(wifi),
    # ... toutes les autres features
}
input_df = pd.DataFrame([input_data])
```

##### 4. Prédiction
```python
# Le modèle prédit log1p(price)
prediction_log = model.predict(input_df)[0]

# Transformation inverse pour obtenir le prix réel
predicted_price = np.expm1(prediction_log)
```

##### 5. Affichage du Résultat
- **Panneau de résultat** avec design professionnel
- **Prix prédit** en gros caractères (€/nuit)
- **Code couleur** :
  - 🟢 Vert : Prix acceptable (< 150€)
  - 🟡 Jaune : Prix moyen (150-300€)
  - 🔴 Rouge : Prix élevé (> 300€)
- **Comparaison** avec les prix moyens du marché
- **Fourchette de confiance** (optionnel)

#### 🎨 Design
- **Style moderne** inspiré de DM Sans / DM Serif Display
- **Cartes (cards)** pour regrouper les sections
- **Labels en majuscules** avec espacement des lettres
- **Résultat visuellement impactant** : grande typographie, couleurs vives

#### 📊 Métriques du Modèle
Affichage des performances du modèle chargé :
- **MAE** : ~15-20€
- **RMSE** : ~25-30€
- **R²** : ~0.75-0.80
- **MAPE** : ~20-25%

#### ⚙️ Fonctions Principales
```python
app()                     # Fonction principale de la page
load_model()              # Chargement du modèle pickle
load_params()             # Chargement des paramètres JSON
get_arrondissement_coords() # Coordonnées par défaut par arrondissement
predict_price(input_df)   # Prédiction du prix
```

---

### Page 5 : 📚 Dictionnaire des Données

**Fichier** : [`pagesWeb/dictionnaire.py`](pagesWeb/dictionnaire.py)

#### 🎯 Objectif
Fournir une **référence complète** de toutes les variables du dataset pour faciliter la compréhension et l'exploitation des données.

#### 📖 Contenu

##### Structure du Dictionnaire
Les variables sont organisées en **7 catégories** :

1. **👤 Hôte** (Host)
   - `host_id`, `host_since`, `host_location`
   - `host_response_time`, `host_response_rate`
   - `host_is_superhost`, `host_identity_verified`

2. **📍 Localisation** (Location)
   - `listing_id`, `neighbourhood`, `arrondissement`
   - `latitude`, `longitude`

3. **🏠 Logement** (Property)
   - `name`, `property_type`, `room_type`
   - `accommodates`, `bedrooms`, `amenities`

4. **💰 Tarification** (Pricing)
   - `price`, `minimum_nights`, `maximum_nights`
   - `instant_bookable`

5. **⭐ Évaluations** (Reviews)
   - `review_scores_rating`, `review_scores_accuracy`
   - `review_scores_cleanliness`, `review_scores_location`

6. **🛋️ Équipements** (Amenities)
   - `amenity_wifi`, `amenity_tv`, `amenity_kitchen`
   - `amenity_air_conditioning`, `amenity_parking`, etc.

7. **🚇 Transports** (Transport)
   - `flag_metro`, `flag_rer`, `flag_tram`
   - `distance_metro_m`, `distance_rer_m`, `distance_tram_m`

##### Format d'Affichage
Pour chaque variable :
- **Nom** : Nom technique de la colonne
- **Type** : `int`, `float`, `str`, `bool`, `date`
- **Définition** : Description claire et concise

##### Présentation
- **Onglets (tabs)** : Une tab par catégorie
- **Tableaux formatés** : DataFrames Streamlit stylisés
- **Search bar** (optionnel) : Recherche par mot-clé
- **Statistiques** (optionnel) : Min, max, count pour chaque variable

#### 🎨 Design
- **Interface claire** avec onglets bien visibles
- **Tableaux sans index** pour la lisibilité
- **Tooltips** sur les types de données
- **Sections repliables** (expanders) pour les détails

#### ⚙️ Structure de Données
```python
DICT_AIRBNB = {
    "Hôte": [
        {"variable": "host_id", "type": "int", "définition": "..."},
        {"variable": "host_since", "type": "date", "définition": "..."},
        # ...
    ],
    "Localisation": [...],
    # ...
}
```

---

## 📁 Dossier `models/`

Ce dossier contient les **artefacts du machine learning** utilisés par la page de prédiction.

### 📄 Fichiers

#### 1. `airbnb_model.pkl` ⭐
- **Type** : Fichier pickle (binaire)
- **Contenu** : Pipeline Scikit-learn complet (preprocessing + modèle)
- **Taille** : ~20-50 Mo (selon le modèle)
- **Modèle** : LightGBM 
- **Chargement** :
  ```python
  import joblib
  model = joblib.load("models/airbnb_model.pkl")
  ```

#### 2. `model_params.json`
- **Type** : Fichier JSON
- **Contenu** : Métadonnées et paramètres du modèle
- **Sections** :
  - `model_info` : Nom du modèle, métriques (MAE, RMSE, R², MAPE)
  - `features` : Liste des features utilisées
  - `categorical_features` : Variables catégorielles
  - `numerical_features` : Variables numériques
  - `feature_importance` : Importance de chaque variable
  - `top_features` : Top 10 des features les plus influentes
  - `encoders` : Modalités possibles pour chaque variable catégorielle
  - `numerical_ranges` : Min, max, mean, median pour chaque variable numérique
  - `benchmark` : Résultats des 6 modèles comparés

#### 3. Documentation Technique
- **`README.md`** : Vue d'ensemble des modèles
- **`GUIDE_JE_SAIS_PAS.md`** : Guide de debugging pour les erreurs courantes
- **`IMPACT_VALEURS_INCONNUES.md`** : Documentation sur la gestion des valeurs inconnues

---

## 🎨 Design System

### Palette de Couleurs Principale
```python
TEAL        = "#C7EFCF"  # Vert menthe (primaire)
TEAL_LIGHT  = "#E3F7E8"  # Vert menthe clair
SAGE        = "#FFCCBA"  # Saumon pastel (secondaire)
DARK        = "#010221"  # Bleu nuit (texte)
GOLD        = "#F0B67F"  # Or doux (highlights)
BRICK       = "#FE5F55"  # Rouge brique (alertes)
ORANGE      = "#F3986D"  # Orange (accents)
```

### Typographie
- **Police principale** : DM Sans (sans-serif moderne)
- **Police titres** : DM Serif Display (serif élégante)
- **Import Google Fonts** :
  ```css
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');
  ```

### Composants Réutilisables

#### Cartes (Cards)
```python
st.markdown("""
<div style="
    background: #f7fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
">
    <div class="card-title">Titre Section</div>
    <!-- Contenu -->
</div>
""", unsafe_allow_html=True)
```

#### KPIs / Métriques
```python
st.metric(
    label="Nombre de logements",
    value=f"{nb_logements:,}",
    delta="+5.2%"  # optionnel
)
```

#### Hero Section
```python
st.markdown(f"""
<div style="
    background: linear-gradient(135deg, {TEAL} 0%, {TEAL_LIGHT} 100%);
    padding: 3em 2em;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
">
    <h1 style="text-align:center; color:white;">Titre</h1>
    <p style="text-align:center; color:{SAGE};">Sous-titre</p>
</div>
""", unsafe_allow_html=True)
```

---

## 🚀 Performances & Optimisations

### Cache Streamlit
L'application utilise `@st.cache_data` pour optimiser les performances :

```python
@st.cache_data(show_spinner="Chargement des données…")
def _load_data():
    return pd.read_csv("data/airbnb_enrichi.csv")
```

**Avantages** :
- ✅ Pas de rechargement à chaque interaction
- ✅ Réponse instantanée lors du changement de page
- ✅ Économie de mémoire et de CPU

### Chargement Différé
- Les données ne sont chargées que **lorsqu'elles sont nécessaires**
- Chaque page gère son propre chargement de données
- Les modèles ML sont chargés uniquement sur la page de prédiction

### Gestion des Erreurs
```python
if not DATA_FILE.exists():
    st.error("❌ Fichier de données introuvable")
    st.stop()
```

---

## 🛠️ Technologies & Dépendances

### Frameworks Principaux
- **Streamlit 1.30+** : Framework web interactif
- **Pandas 2.0+** : Manipulation de données
- **NumPy 1.24+** : Calculs numériques

### Visualisation
- **Altair 5.0+** : Graphiques interactifs (grammaire déclarative)
- **Folium 0.15+** : Cartes géographiques interactives
- **streamlit_folium** : Intégration Folium dans Streamlit
- **Matplotlib 3.7+** : Graphiques statiques (backup)
- **Plotly 5.17+** : Graphiques 3D et interactifs avancés

### Géospatial
- **GeoPandas 0.14+** : Manipulation de données géospatiales
- **Shapely** : Opérations géométriques
- **Branca** : Composants cartographiques

### Machine Learning
- **Scikit-learn 1.3+** : Preprocessing et pipelines
- **XGBoost 2.0+** : Modèle de gradient boosting
- **LightGBM 4.0+** : Modèle de gradient boosting
- **Joblib** : Sérialisation des modèles

---

## 📊 Fichiers de Données Requis

L'application nécessite les fichiers suivants pour fonctionner :

### Données Brutes
- **`data/airbnb_enrichi.csv`** ⭐ : Dataset principal (~60k annonces, 73 colonnes)

### Modèles
- **`appStreamlit/models/airbnb_model.pkl`** : Modèle ML entraîné
- **`appStreamlit/models/model_params.json`** : Paramètres du modèle

### Sources Externes (chargées via API)
- **Contours d'arrondissements** : API Open Data Paris (automatique)

---

## 🐛 Debugging & Troubleshooting

### Erreur : "FileNotFoundError: data/airbnb_enrichi.csv"
**Cause** : Le fichier de données n'existe pas  
**Solution** :
```bash
# Exécuter le pipeline complet dans dev/
python dev/lecture_donnee.py
python dev/preparation_donnee.py
python dev/ajout_service_transport.py
```

### Erreur : "ModuleNotFoundError: No module named 'streamlit'"
**Cause** : Dépendances non installées  
**Solution** :
```bash
pip install -r requirements.txt
```

### Erreur : "Port 8501 already in use"
**Cause** : Une instance de Streamlit est déjà en cours  
**Solution** :
```bash
# Tuer le processus existant
taskkill /F /IM streamlit.exe  # Windows
pkill -f streamlit             # Linux/Mac

# Ou utiliser un autre port
streamlit run app.py --server.port 8502
```

### Page blanche / Application ne démarre pas
**Cause** : Erreur dans le code Python  
**Solution** :
1. Vérifier les logs dans le terminal
2. Activer le debug mode : `streamlit run app.py --logger.level=debug`
3. Consulter `GUIDE_JE_SAIS_PAS.md` dans le dossier models/

### Carte ne s'affiche pas
**Cause** : Problème de connexion API Open Data Paris  
**Solution** :
- Vérifier la connexion internet
- Réessayer plus tard (l'API peut être temporairement indisponible)
- Les données sont mises en cache après le premier chargement

---

## 🚀 Déploiement

### Déploiement Local (Production)
```bash
streamlit run appStreamlit/app.py --server.headless true
```

### Déploiement Cloud

#### Option 1 : Streamlit Cloud (Recommandé)
1. Push le code sur GitHub
2. Se connecter sur [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connecter le repository GitHub
4. Déployer automatiquement

#### Option 2 : Heroku
1. Créer un `Procfile` :
   ```
   web: streamlit run appStreamlit/app.py --server.port $PORT
   ```
2. Déployer via Heroku CLI

#### Option 3 : Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "appStreamlit/app.py"]
```

---

## 📈 Améliorations Futures

### Fonctionnalités
- 🔐 **Authentification** : Login pour sauvegarder les favoris
- 💾 **Export de données** : Télécharger les résultats en CSV/Excel
- 📧 **Notifications** : Alertes email pour les nouvelles annonces
- 🌍 **Multi-langues** : Support FR/EN/ES
- 📱 **Progressive Web App** : Installation sur mobile
- 🔄 **Actualisation automatique** : Scraping régulier des données Airbnb

### Visualisations
- 📊 **Graphiques avancés** : Animations, 3D, séries temporelles
- 🗺️ **Carte 3D** : Visualisation en relief avec altitude = prix
- 🎨 **Thèmes** : Mode sombre/clair
- 📐 **Dashboard personnalisable** : Drag & drop des widgets

### Machine Learning
- 🧠 **Modèles avancés** : Deep Learning (LSTM, Transformers)
- 🔮 **Prédiction temporelle** : Forecast des prix sur 30 jours
- 🎯 **Recommandation** : Suggérer les meilleurs logements
- 📊 **A/B Testing** : Comparer plusieurs modèles en live

### Techniques
- ⚡ **Optimisation** : Lazy loading, pagination
- 🔄 **CI/CD** : Tests automatisés, déploiement continu
- 📊 **Analytics** : Tracking des interactions utilisateurs (Google Analytics)
- 🐳 **Conteneurisation** : Docker Compose pour dev/prod

---

## 📞 Support & Contact

### Documentation
- **README principal** : [`README.md`](../README.md)
- **Documentation dev** : [`dev/README.md`](../dev/README.md)
- **Documentation modèles** : [`models/README.md`](models/README.md)

---

<div align="center">

**🎨 Interface moderne • 🗺️ Cartographie interactive • 🤖 Machine Learning • 📊 Analyses avancées**

Made with ❤️, 🐍 and Streamlit by Alice & Claudia

</div>
