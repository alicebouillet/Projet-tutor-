"""
Script pour entraîner et sauvegarder le meilleur modèle Airbnb
avec le scaler et les métriques pour l'application Streamlit
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
import joblib
import json
import warnings
import os
warnings.filterwarnings('ignore')


print("=" * 80)
print("ENTRAÎNEMENT ET SAUVEGARDE DU MODÈLE AIRBNB")
print("=" * 80)

# ===== CHARGEMENT & NETTOYAGE =====

print("\n📂 Chargement des données...")
df = pd.read_csv('data/airbnb_enrichi.csv')
print(f"Dataset initial: {df.shape}")

colonnes_a_supprimer = [
    'district', 'host_response_time', 'host_response_rate', 'host_acceptance_rate',
    'review_scores_location', 'review_scores_value', 'review_scores_checkin',
    'review_scores_accuracy', 'review_scores_communication', 'review_scores_cleanliness',
    'review_scores_rating', 'bedrooms', 'host_location', 'name',
    'host_since', 'host_has_profile_pic', 'host_identity_verified',
    'host_is_superhost', 'host_total_listings_count',
    'listing_id', 'host_id', 'neighbourhood', 'amenities'
]
df = df.drop(columns=[c for c in colonnes_a_supprimer if c in df.columns])
df = df.dropna(subset=['price'])

# Filtrage des outliers
Q1, Q3 = df['price'].quantile(0.01), df['price'].quantile(0.99)
df = df[(df['price'] >= Q1) & (df['price'] <= Q3)]
print(f"Dataset après nettoyage: {df.shape}")


# ===== PRÉPARATION DES FEATURES =====

print("\n🔧 Préparation des features...")
y = df['price']
X = df.drop('price', axis=1)

colonnes_cat = X.select_dtypes(include=['object', 'bool']).columns
colonnes_num = X.select_dtypes(include=['int64', 'float64']).columns

# Encodage des variables catégorielles
for col in colonnes_cat:
    X[col] = LabelEncoder().fit_transform(X[col].astype(str))

# Remplissage des valeurs manquantes
for col in X.columns:
    if X[col].isnull().any():
        X[col].fillna(X[col].median() if col in colonnes_num else X[col].mode()[0], inplace=True)

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardisation
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

print(f"Train: {X_train.shape} | Test: {X_test.shape}")


# ===== SÉLECTION ET OPTIMISATION DU MODÈLE =====

print("\n🤖 Entraînement du modèle...")

# On utilise Random Forest avec une optimisation légère
# (pour un meilleur résultat, utilise le script testModele.py complet)

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4],
    'max_features': ['sqrt', 'log2']
}

rf = RandomForestRegressor(random_state=42, n_jobs=-1)
search = RandomizedSearchCV(
    rf, param_grid, n_iter=20, cv=5, scoring='r2',
    n_jobs=-1, random_state=42, verbose=1
)

print("Optimisation des hyperparamètres...")
search.fit(X_train_s, y_train)

best_model = search.best_estimator_
print(f"\n✅ Meilleur modèle entraîné!")
print(f"Best params: {search.best_params_}")


# ===== ÉVALUATION =====

print("\n📊 Évaluation du modèle...")
y_pred = best_model.predict(X_test_s)

r2_cv = search.best_score_
r2_test = r2_score(y_test, y_pred)
rmse_test = np.sqrt(mean_squared_error(y_test, y_pred))
mae_test = mean_absolute_error(y_test, y_pred)

print(f"  R² (CV): {r2_cv:.4f}")
print(f"  R² (Test): {r2_test:.4f}")
print(f"  RMSE (Test): {rmse_test:.2f}€")
print(f"  MAE (Test): {mae_test:.2f}€")

# Exemples de prédictions
print("\n🔍 Exemples de prédictions:")
for i in range(min(5, len(y_test))):
    print(f"  Réel: {y_test.iloc[i]:.0f}€ | Prédit: {y_pred[i]:.0f}€ | Erreur: {abs(y_test.iloc[i] - y_pred[i]):.0f}€")


# ===== SAUVEGARDE =====

print("\n💾 Sauvegarde du modèle...")

# Créer le dossier models s'il n'existe pas
models_dir = "appStreamlit/models"
os.makedirs(models_dir, exist_ok=True)

# Sauvegarder le modèle
model_path = os.path.join(models_dir, "model_airbnb.pkl")
joblib.dump(best_model, model_path)
print(f"  ✓ Modèle sauvegardé: {model_path}")

# Sauvegarder le scaler
scaler_path = os.path.join(models_dir, "scaler_airbnb.pkl")
joblib.dump(scaler, scaler_path)
print(f"  ✓ Scaler sauvegardé: {scaler_path}")

# Sauvegarder les métriques
metrics = {
    "r2_cv": round(r2_cv, 4),
    "r2_test": round(r2_test, 4),
    "rmse_test": round(rmse_test, 2),
    "mae_test": round(mae_test, 2),
    "best_params": search.best_params_,
    "n_features": X.shape[1],
    "n_train": len(X_train),
    "n_test": len(X_test)
}

metrics_path = os.path.join(models_dir, "metrics_airbnb.json")
with open(metrics_path, 'w', encoding='utf-8') as f:
    json.dump(metrics, f, indent=2, ensure_ascii=False)
print(f"  ✓ Métriques sauvegardées: {metrics_path}")

print("\n" + "=" * 80)
print("✅ SUCCÈS! Le modèle est prêt à être utilisé dans Streamlit")
print("=" * 80)
print("\nPour tester l'application:")
print("  cd appStreamlit")
print("  streamlit run app.py")
