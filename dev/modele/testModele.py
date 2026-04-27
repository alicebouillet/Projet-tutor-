"""
Script de test et sélection du meilleur modèle pour prédire le prix des Airbnb
- Test de plusieurs modèles
- Sélection des features importantes
- Optimisation des hyperparamètres
- Validation croisée
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.feature_selection import SelectKBest, f_regression, RFE
from sklearn.neighbors import KNeighborsRegressor
import warnings
warnings.filterwarnings('ignore')

# ===== 1. CHARGEMENT DES DONNÉES =====
print("="*80)
print("CHARGEMENT DES DONNÉES")
print("="*80)

df = pd.read_csv('data/airbnb_enrichi.csv')
print(f"Dimensions du dataset: {df.shape}")
print(f"Nombre de lignes: {len(df)}")

# ===== 2. SUPPRESSION DES COLONNES AVEC TROP DE NULLS =====
print("\n" + "="*80)
print("SUPPRESSION DES COLONNES AVEC TROP DE VALEURS NULLES")
print("="*80)

colonnes_a_exclure = [
    'district', 'host_response_time', 'host_response_rate', 'host_acceptance_rate',
    'review_scores_location', 'review_scores_value', 'review_scores_checkin',
    'review_scores_accuracy', 'review_scores_communication', 'review_scores_cleanliness',
    'review_scores_rating', 'bedrooms', 'host_location', 'name', 'arrondissement',
    'host_since', 'host_has_profile_pic', 'host_identity_verified',
    'host_is_superhost', 'host_total_listings_count'
]

print(f"Colonnes exclues: {len(colonnes_a_exclure)}")
for col in colonnes_a_exclure:
    if col in df.columns:
        df = df.drop(col, axis=1)

print(f"Dimensions après exclusion: {df.shape}")

# ===== 3. SUPPRESSION DES IDS ET COLONNES NON PERTINENTES =====
colonnes_non_pertinentes = ['listing_id', 'host_id', 'neighbourhood', 'amenities']
for col in colonnes_non_pertinentes:
    if col in df.columns:
        df = df.drop(col, axis=1)

print(f"Dimensions après suppression des IDs: {df.shape}")

# ===== 4. TRAITEMENT DE LA VARIABLE CIBLE =====
print("\n" + "="*80)
print("ANALYSE DE LA VARIABLE CIBLE 'price'")
print("="*80)

# Suppression des lignes avec price null
df = df.dropna(subset=['price'])
print(f"Prix - Statistiques descriptives:")
print(df['price'].describe())

# Traitement des outliers (prix extrêmes)
Q1 = df['price'].quantile(0.01)
Q3 = df['price'].quantile(0.99)
print(f"\nSuppression des prix < {Q1:.2f}€ et > {Q3:.2f}€")
df = df[(df['price'] >= Q1) & (df['price'] <= Q3)]
print(f"Dimensions après traitement des outliers: {df.shape}")

# ===== 5. PRÉPARATION DES FEATURES =====
print("\n" + "="*80)
print("PRÉPARATION DES FEATURES")
print("="*80)

# Séparation X et y
y = df['price']
X = df.drop('price', axis=1)

print(f"Features disponibles: {X.shape[1]}")
print(f"Colonnes: {list(X.columns)}")

# Identification des colonnes catégorielles et numériques
colonnes_categorielles = X.select_dtypes(include=['object', 'bool']).columns.tolist()
colonnes_numeriques = X.select_dtypes(include=['int64', 'float64']).columns.tolist()

print(f"\nColonnes catégorielles ({len(colonnes_categorielles)}): {colonnes_categorielles}")
print(f"Colonnes numériques ({len(colonnes_numeriques)}): {len(colonnes_numeriques)}")

# Encodage des variables catégorielles
for col in colonnes_categorielles:
    if col in X.columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))

# Gestion des valeurs manquantes restantes
print(f"\nValeurs manquantes avant traitement:")
print(X.isnull().sum()[X.isnull().sum() > 0])

# Remplissage des valeurs manquantes
for col in X.columns:
    if X[col].isnull().sum() > 0:
        if col in colonnes_numeriques:
            X[col].fillna(X[col].median(), inplace=True)
        else:
            X[col].fillna(X[col].mode()[0], inplace=True)

print(f"Valeurs manquantes après traitement: {X.isnull().sum().sum()}")

# ===== 6. SPLIT DES DONNÉES =====
print("\n" + "="*80)
print("SÉPARATION TRAIN/TEST")
print("="*80)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Taille du jeu d'entraînement: {X_train.shape}")
print(f"Taille du jeu de test: {X_test.shape}")

# ===== 7. NORMALISATION =====
print("\n" + "="*80)
print("NORMALISATION DES DONNÉES")
print("="*80)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
print("Normalisation effectuée avec StandardScaler")

# ===== 8. SÉLECTION DES FEATURES IMPORTANTES =====
print("\n" + "="*80)
print("SÉLECTION DES FEATURES IMPORTANTES")
print("="*80)

# Méthode 1: SelectKBest avec f_regression
selector = SelectKBest(f_regression, k=min(30, X_train.shape[1]))
selector.fit(X_train_scaled, y_train)
scores = pd.DataFrame({
    'Feature': X.columns,
    'Score': selector.scores_
}).sort_values('Score', ascending=False)

print("\nTop 20 features selon SelectKBest:")
print(scores.head(20))

# Méthode 2: Random Forest pour l'importance des features
rf_temp = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf_temp.fit(X_train_scaled, y_train)
feature_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': rf_temp.feature_importances_
}).sort_values('Importance', ascending=False)

print("\nTop 20 features selon Random Forest:")
print(feature_importance.head(20))

# ===== 9. TEST DE PLUSIEURS MODÈLES =====
print("\n" + "="*80)
print("TEST DE PLUSIEURS MODÈLES (BASELINE)")
print("="*80)

modeles = {
    'Linear Regression': LinearRegression(),
    'Ridge': Ridge(random_state=42),
    'Lasso': Lasso(random_state=42),
    'ElasticNet': ElasticNet(random_state=42),
    'Decision Tree': DecisionTreeRegressor(random_state=42),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
    'Extra Trees': ExtraTreesRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    'KNN': KNeighborsRegressor(n_neighbors=5)
}

resultats = []

for nom, modele in modeles.items():
    print(f"\n{nom}...")
    
    # Cross-validation sur le jeu d'entraînement
    cv_scores = cross_val_score(modele, X_train_scaled, y_train, 
                                 cv=5, scoring='r2', n_jobs=-1)
    cv_rmse = -cross_val_score(modele, X_train_scaled, y_train, 
                                cv=5, scoring='neg_root_mean_squared_error', n_jobs=-1)
    
    # Entraînement et prédiction
    modele.fit(X_train_scaled, y_train)
    y_pred = modele.predict(X_test_scaled)
    
    # Calcul des métriques
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    
    resultats.append({
        'Modèle': nom,
        'R² (CV)': cv_scores.mean(),
        'R² (Test)': r2,
        'RMSE (CV)': cv_rmse.mean(),
        'RMSE (Test)': rmse,
        'MAE (Test)': mae
    })
    
    print(f"  R² (CV): {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    print(f"  R² (Test): {r2:.4f}")
    print(f"  RMSE (CV): {cv_rmse.mean():.2f} (+/- {cv_rmse.std():.2f})")
    print(f"  RMSE (Test): {rmse:.2f}")
    print(f"  MAE (Test): {mae:.2f}")

df_resultats = pd.DataFrame(resultats).sort_values('R² (Test)', ascending=False)
print("\n" + "="*80)
print("RÉSUMÉ DES PERFORMANCES")
print("="*80)
print(df_resultats.to_string(index=False))

# ===== 10. OPTIMISATION DES MEILLEURS MODÈLES =====
print("\n" + "="*80)
print("OPTIMISATION DES HYPERPARAMÈTRES")
print("="*80)

# Sélection des 3 meilleurs modèles
meilleurs_modeles = df_resultats.head(3)['Modèle'].tolist()
print(f"Modèles sélectionnés pour l'optimisation: {meilleurs_modeles}")

resultats_optimises = []

# Random Forest
if 'Random Forest' in meilleurs_modeles:
    print("\n--- RANDOM FOREST ---")
    param_grid_rf = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 20, 30, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2']
    }
    
    rf = RandomForestRegressor(random_state=42, n_jobs=-1)
    grid_rf = RandomizedSearchCV(rf, param_grid_rf, n_iter=20, cv=5, 
                                  scoring='r2', n_jobs=-1, random_state=42, verbose=1)
    grid_rf.fit(X_train_scaled, y_train)
    
    print(f"Meilleurs paramètres: {grid_rf.best_params_}")
    print(f"Meilleur score CV: {grid_rf.best_score_:.4f}")
    
    y_pred = grid_rf.predict(X_test_scaled)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    
    resultats_optimises.append({
        'Modèle': 'Random Forest (Optimisé)',
        'Params': str(grid_rf.best_params_),
        'R² (CV)': grid_rf.best_score_,
        'R² (Test)': r2,
        'RMSE (Test)': rmse,
        'MAE (Test)': mae
    })
    
    print(f"R² (Test): {r2:.4f}")
    print(f"RMSE (Test): {rmse:.2f}")

# Gradient Boosting
if 'Gradient Boosting' in meilleurs_modeles:
    print("\n--- GRADIENT BOOSTING ---")
    param_grid_gb = {
        'n_estimators': [100, 200, 300],
        'learning_rate': [0.01, 0.05, 0.1],
        'max_depth': [3, 5, 7],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'subsample': [0.8, 0.9, 1.0]
    }
    
    gb = GradientBoostingRegressor(random_state=42)
    grid_gb = RandomizedSearchCV(gb, param_grid_gb, n_iter=20, cv=5, 
                                  scoring='r2', n_jobs=-1, random_state=42, verbose=1)
    grid_gb.fit(X_train_scaled, y_train)
    
    print(f"Meilleurs paramètres: {grid_gb.best_params_}")
    print(f"Meilleur score CV: {grid_gb.best_score_:.4f}")
    
    y_pred = grid_gb.predict(X_test_scaled)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    
    resultats_optimises.append({
        'Modèle': 'Gradient Boosting (Optimisé)',
        'Params': str(grid_gb.best_params_),
        'R² (CV)': grid_gb.best_score_,
        'R² (Test)': r2,
        'RMSE (Test)': rmse,
        'MAE (Test)': mae
    })
    
    print(f"R² (Test): {r2:.4f}")
    print(f"RMSE (Test): {rmse:.2f}")

# Extra Trees
if 'Extra Trees' in meilleurs_modeles:
    print("\n--- EXTRA TREES ---")
    param_grid_et = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 20, 30, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2']
    }
    
    et = ExtraTreesRegressor(random_state=42, n_jobs=-1)
    grid_et = RandomizedSearchCV(et, param_grid_et, n_iter=20, cv=5, 
                                  scoring='r2', n_jobs=-1, random_state=42, verbose=1)
    grid_et.fit(X_train_scaled, y_train)
    
    print(f"Meilleurs paramètres: {grid_et.best_params_}")
    print(f"Meilleur score CV: {grid_et.best_score_:.4f}")
    
    y_pred = grid_et.predict(X_test_scaled)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    
    resultats_optimises.append({
        'Modèle': 'Extra Trees (Optimisé)',
        'Params': str(grid_et.best_params_),
        'R² (CV)': grid_et.best_score_,
        'R² (Test)': r2,
        'RMSE (Test)': rmse,
        'MAE (Test)': mae
    })
    
    print(f"R² (Test): {r2:.4f}")
    print(f"RMSE (Test): {rmse:.2f}")

# Ridge (rapide à optimiser)
if 'Ridge' in meilleurs_modeles:
    print("\n--- RIDGE ---")
    param_grid_ridge = {
        'alpha': [0.001, 0.01, 0.1, 1, 10, 100, 1000]
    }
    
    ridge = Ridge(random_state=42)
    grid_ridge = GridSearchCV(ridge, param_grid_ridge, cv=5, 
                              scoring='r2', n_jobs=-1, verbose=1)
    grid_ridge.fit(X_train_scaled, y_train)
    
    print(f"Meilleurs paramètres: {grid_ridge.best_params_}")
    print(f"Meilleur score CV: {grid_ridge.best_score_:.4f}")
    
    y_pred = grid_ridge.predict(X_test_scaled)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    
    resultats_optimises.append({
        'Modèle': 'Ridge (Optimisé)',
        'Params': str(grid_ridge.best_params_),
        'R² (CV)': grid_ridge.best_score_,
        'R² (Test)': r2,
        'RMSE (Test)': rmse,
        'MAE (Test)': mae
    })
    
    print(f"R² (Test): {r2:.4f}")
    print(f"RMSE (Test): {rmse:.2f}")

# ===== 11. RÉSULTATS FINAUX =====
print("\n" + "="*80)
print("RÉSULTATS FINAUX - MODÈLES OPTIMISÉS")
print("="*80)

df_optimises = pd.DataFrame(resultats_optimises).sort_values('R² (Test)', ascending=False)
print(df_optimises[['Modèle', 'R² (CV)', 'R² (Test)', 'RMSE (Test)', 'MAE (Test)']].to_string(index=False))

print("\n" + "="*80)
print("MEILLEUR MODÈLE")
print("="*80)
meilleur = df_optimises.iloc[0]
print(f"Modèle: {meilleur['Modèle']}")
print(f"Paramètres: {meilleur['Params']}")
print(f"R² (Cross-Validation): {meilleur['R² (CV)']:.4f}")
print(f"R² (Test): {meilleur['R² (Test)']:.4f}")
print(f"RMSE (Test): {meilleur['RMSE (Test)']:.2f}€")
print(f"MAE (Test): {meilleur['MAE (Test)']:.2f}€")

print("\n" + "="*80)
print("FIN DU SCRIPT")
print("="*80)
