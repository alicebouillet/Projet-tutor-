"""
Script de test et sélection du meilleur modèle pour prédire le prix des Airbnb
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, RandomizedSearchCV, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.neighbors import KNeighborsRegressor
import warnings
warnings.filterwarnings('ignore')


# ===== CHARGEMENT & NETTOYAGE =====

df = pd.read_csv('data/airbnb_enrichi.csv')

colonnes_a_supprimer = [
    'district', 'host_response_time', 'host_response_rate', 'host_acceptance_rate',
    'review_scores_location', 'review_scores_value', 'review_scores_checkin',
    'review_scores_accuracy', 'review_scores_communication', 'review_scores_cleanliness',
    'review_scores_rating', 'bedrooms', 'host_location', 'name', 'arrondissement',
    'host_since', 'host_has_profile_pic', 'host_identity_verified',
    'host_is_superhost', 'host_total_listings_count',
    'listing_id', 'host_id', 'neighbourhood', 'amenities'
]
df = df.drop(columns=[c for c in colonnes_a_supprimer if c in df.columns])
df = df.dropna(subset=['price'])

Q1, Q3 = df['price'].quantile(0.01), df['price'].quantile(0.99)
df = df[(df['price'] >= Q1) & (df['price'] <= Q3)]
print(f"Dataset final: {df.shape}")


# ===== PRÉPARATION DES FEATURES =====

y = df['price']
X = df.drop('price', axis=1)

colonnes_cat = X.select_dtypes(include=['object', 'bool']).columns
colonnes_num = X.select_dtypes(include=['int64', 'float64']).columns

for col in colonnes_cat:
    X[col] = LabelEncoder().fit_transform(X[col].astype(str))

for col in X.columns:
    if X[col].isnull().any():
        X[col].fillna(X[col].median() if col in colonnes_num else X[col].mode()[0], inplace=True)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

print(f"Train: {X_train.shape} | Test: {X_test.shape}")


# ===== SÉLECTION DES FEATURES =====

selector = SelectKBest(f_regression, k=min(30, X_train.shape[1]))
selector.fit(X_train_s, y_train)
scores_kbest = pd.DataFrame({'Feature': X.columns, 'Score': selector.scores_}).sort_values('Score', ascending=False)
print("\nTop 10 features (SelectKBest):")
print(scores_kbest.head(10).to_string(index=False))

rf_temp = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf_temp.fit(X_train_s, y_train)
scores_rf = pd.DataFrame({'Feature': X.columns, 'Importance': rf_temp.feature_importances_}).sort_values('Importance', ascending=False)
print("\nTop 10 features (Random Forest):")
print(scores_rf.head(10).to_string(index=False))


# ===== BENCHMARK =====

def evaluer(modele, nom):
    cv_r2   = cross_val_score(modele, X_train_s, y_train, cv=5, scoring='r2', n_jobs=-1).mean()
    cv_rmse = -cross_val_score(modele, X_train_s, y_train, cv=5, scoring='neg_root_mean_squared_error', n_jobs=-1).mean()
    modele.fit(X_train_s, y_train)
    y_pred  = modele.predict(X_test_s)
    return {
        'Modèle': nom,
        'R² (CV)': round(cv_r2, 4),
        'R² (Test)': round(r2_score(y_test, y_pred), 4),
        'RMSE (CV)': round(cv_rmse, 2),
        'RMSE (Test)': round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
        'MAE (Test)': round(mean_absolute_error(y_test, y_pred), 2),
    }

modeles_baseline = {
    'Linear Regression':  LinearRegression(),
    'Ridge':              Ridge(random_state=42),
    'Lasso':              Lasso(random_state=42),
    'ElasticNet':         ElasticNet(random_state=42),
    'Decision Tree':      DecisionTreeRegressor(random_state=42),
    'Random Forest':      RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    'Gradient Boosting':  GradientBoostingRegressor(n_estimators=100, random_state=42),
    'Extra Trees':        ExtraTreesRegressor(n_estimators=100, random_state=42, n_jobs=-1),
    'KNN':                KNeighborsRegressor(n_neighbors=5),
}

resultats = pd.DataFrame([evaluer(m, n) for n, m in modeles_baseline.items()])
resultats = resultats.sort_values('R² (Test)', ascending=False)
print("\n===== BENCHMARK =====")
print(resultats.to_string(index=False))


# ===== OPTIMISATION DES HYPERPARAMÈTRES =====

top3 = resultats.head(3)['Modèle'].tolist()

grilles = {
    'Random Forest': (
        RandomForestRegressor(random_state=42, n_jobs=-1),
        {'n_estimators': [100, 200, 300], 'max_depth': [10, 20, 30, None],
         'min_samples_split': [2, 5, 10], 'min_samples_leaf': [1, 2, 4], 'max_features': ['sqrt', 'log2']},
        'random'
    ),
    'Gradient Boosting': (
        GradientBoostingRegressor(random_state=42),
        {'n_estimators': [100, 200, 300], 'learning_rate': [0.01, 0.05, 0.1],
         'max_depth': [3, 5, 7], 'min_samples_split': [2, 5, 10],
         'min_samples_leaf': [1, 2, 4], 'subsample': [0.8, 0.9, 1.0]},
        'random'
    ),
    'Extra Trees': (
        ExtraTreesRegressor(random_state=42, n_jobs=-1),
        {'n_estimators': [100, 200, 300], 'max_depth': [10, 20, 30, None],
         'min_samples_split': [2, 5, 10], 'min_samples_leaf': [1, 2, 4], 'max_features': ['sqrt', 'log2']},
        'random'
    ),
    'Ridge': (
        Ridge(random_state=42),
        {'alpha': [0.001, 0.01, 0.1, 1, 10, 100, 1000]},
        'grid'
    ),
}

resultats_opt = []

for nom in top3:
    if nom not in grilles:
        continue
    modele, params, methode = grilles[nom]
    print(f"\n--- Optimisation: {nom} ---")

    search = (
        RandomizedSearchCV(modele, params, n_iter=20, cv=5, scoring='r2', n_jobs=-1, random_state=42, verbose=1)
        if methode == 'random'
        else GridSearchCV(modele, params, cv=5, scoring='r2', n_jobs=-1, verbose=1)
    )
    search.fit(X_train_s, y_train)

    y_pred = search.predict(X_test_s)
    resultats_opt.append({
        'Modèle': f'{nom} (Optimisé)',
        'Params': str(search.best_params_),
        'R² (CV)': round(search.best_score_, 4),
        'R² (Test)': round(r2_score(y_test, y_pred), 4),
        'RMSE (Test)': round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
        'MAE (Test)': round(mean_absolute_error(y_test, y_pred), 2),
    })
    print(f"  Best params: {search.best_params_}")
    print(f"  R²(CV)={search.best_score_:.4f} | R²(Test)={resultats_opt[-1]['R² (Test)']:.4f} | RMSE={resultats_opt[-1]['RMSE (Test)']:.2f}")


# ===== RÉSULTATS FINAUX =====

df_opt = pd.DataFrame(resultats_opt).sort_values('R² (Test)', ascending=False)
print("\n===== MODÈLES OPTIMISÉS =====")
print(df_opt[['Modèle', 'R² (CV)', 'R² (Test)', 'RMSE (Test)', 'MAE (Test)']].to_string(index=False))

meilleur = df_opt.iloc[0]
print(f"\nMeilleur modèle : {meilleur['Modèle']}")
print(f"  Params : {meilleur['Params']}")
print(f"  R²(CV)={meilleur['R² (CV)']} | R²(Test)={meilleur['R² (Test)']} | RMSE={meilleur['RMSE (Test)']}€ | MAE={meilleur['MAE (Test)']}€")
