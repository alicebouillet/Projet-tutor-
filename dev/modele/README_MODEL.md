# Modèle de Prédiction des Prix Airbnb Paris 2024

## 📌 Fichier Principal

**`airbnb_model_training.py`** - Script complet d'entraînement et de benchmark des modèles de prédiction des prix Airbnb.

### 🎯 Objectif
Prédire le prix par nuit des logements Airbnb à Paris en utilisant des algorithmes de machine learning et sélectionner le meilleur modèle basé sur les performances.

### 📊 Données
- **Source** : `airbnb_enrichi.csv`
- **Échantillon initial** : 64 690 annonces
- **Colonnes** : 73 features
- **Filtre appliqué** : Prix entre 0€ et 500€ par nuit (suppression des outliers)

### 🔄 Pipeline de Machine Learning

Le script exécute un pipeline complet en 6 étapes :

#### 1. **Chargement & Nettoyage**
   - Chargement du dataset enrichi
   - Suppression des outliers de prix (> 500€ ou prix nul)
   - Validation de la qualité des données

#### 2. **Sélection des Features**
   - **Règle** : Sélection uniquement des colonnes 100% complètes (sans valeurs manquantes)
   - **Exclusions** : 
     - Identifiants (`listing_id`, `host_id`)
     - Texte libre non structuré (`name`, `amenities`)
     - Colonnes non pertinentes (`city`, `host_since`, `host_location`)
   - **Features catégorielles** : 
     - `neighbourhood` (quartier)
     - `property_type` (type de logement)
     - `room_type` (type de chambre)
     - `instant_bookable` (réservation instantanée)
   - **Features numériques** : Localisation GPS, capacité d'accueil, durées de séjour, équipements, transports, etc.

#### 3. **Préparation X / y**
   - **Transformation de la cible** : `log1p(price)` pour réduire le skew et améliorer les performances
   - **Inverse transform** : `np.expm1()` pour retrouver les prix réels lors des prédictions
   - **Split des données** : 80% train / 20% test (stratégie fixe avec `random_state=42`)

#### 4. **Benchmark de 6 Modèles**
   Les modèles suivants sont entraînés et comparés :
   
   - **Ridge** : Régression linéaire régularisée L2 (α=10.0)
   - **Lasso** : Régression linéaire régularisée L1 (α=0.001)
   - **Random Forest** : 200 arbres, profondeur max=15
   - **XGBoost** : 800 estimateurs, learning_rate=0.05, profondeur=6
   - **LightGBM** : 800 estimateurs, learning_rate=0.05, 63 feuilles
   - **CatBoost** : 800 itérations, learning_rate=0.05, profondeur=6

   **Preprocessing** :
   - Encodage ordinal pour les variables catégorielles (valeurs inconnues → -1)
   - Normalisation (StandardScaler) pour les modèles linéaires uniquement

#### 5. **Évaluation des Performances**
   Métriques calculées sur les prix réels (après `expm1`) :
   - **MAE** (Mean Absolute Error) : Erreur moyenne en euros
   - **RMSE** (Root Mean Squared Error) : Erreur quadratique moyenne
   - **R²** (Coefficient de détermination) : Pourcentage de variance expliquée
   - **MAPE** (Mean Absolute Percentage Error) : Erreur en pourcentage

   Le meilleur modèle est sélectionné automatiquement selon le R² le plus élevé.

#### 6. **Analyse du Poids des Variables**
   Calcul de l'importance des features pour le meilleur modèle avec regroupement par catégories :
   - Localisation GPS (latitude, longitude)
   - Contraintes de séjour (minimum_nights, maximum_nights)
   - Logement & quartier (accommodates, neighbourhood, property_type, room_type)
   - Équipements (amenities)
   - Transports (flags)

### 💾 Exports Générés

Le script génère deux fichiers essentiels :

1. **`best_model.pkl`** (fichier pickle)
   - Pipeline complet : preprocessing + modèle entraîné
   - Prêt à être chargé et utilisé pour les prédictions
   - Utilisé par l'application Streamlit

2. **`model_params.json`** (fichier JSON)
   - Métadonnées du modèle (nom, métriques, configuration)
   - Liste des features et leur importance
   - Résultats du benchmark complet
   - Valeurs min/max/mean/median de chaque feature numérique
   - Modalités possibles pour chaque variable catégorielle
   - Utilisé par l'application Streamlit pour l'interface utilisateur

### 📦 Dépendances Requises
```bash
pip install lightgbm xgboost catboost scikit-learn pandas numpy
```

### 🚀 Utilisation
```bash
python airbnb_model_training.py
```

Le script affiche en temps réel :
- Les statistiques de nettoyage des données
- Les performances de chaque modèle (tableau comparatif)
- Le meilleur modèle sélectionné
- Le Top 20 des features les plus importantes
- La confirmation des exports

---

## 🧪 Fichiers de Test

Les autres fichiers présents dans ce dossier sont des fichiers de test utilisés durant le développement :

### `save_model.py`
Tests pour valider la sauvegarde et le chargement du modèle :
- Sérialisation pickle
- Vérification de l'intégrité du pipeline
- Tests de compatibilité des versions

### `testModele.py`
Tests divers pour expérimentation :
- Essais de différentes configurations d'hyperparamètres
- Validation de nouvelles approches
- Debugging du preprocessing

**Note** : Ces fichiers ne sont pas utilisés en production et servent uniquement à l'expérimentation et la validation durant la phase de développement.
