"""
=============================================================================
 Airbnb Paris 2024 — Benchmark de modèles & prédiction du prix par nuit
=============================================================================
Auteur  : Alice & Claudia
Données : airbnb_enrichi.csv  (64 690 annonces, 73 colonnes)

Pipeline :
  1. Chargement & nettoyage (filtre outliers prix)
  2. Sélection des features (colonnes 100 % complètes, hors IDs/texte brut)
  3. Préparation X / y  (log-transformation du prix pour corriger le skew)
  4. Benchmark de 6 modèles avec métriques comparées
  5. Analyse du poids des variables (feature importance)
  6. Export du meilleur modèle (.pkl) + paramètres Streamlit (.json)

Prérequis :
  pip install lightgbm xgboost catboost scikit-learn pandas numpy
=============================================================================
"""

import pandas as pd
import numpy as np
import json
import pickle
import time
import warnings
warnings.filterwarnings("ignore")

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostRegressor

# ─────────────────────────────────────────────────────────────────────────────
# 1. CHARGEMENT & NETTOYAGE
# ─────────────────────────────────────────────────────────────────────────────
DATA_PATH = "airbnb_enrichi.csv"   # à adapter si besoin

df = pd.read_csv(DATA_PATH, low_memory=False)
print(f"Lignes initiales         : {len(df):>7,}")

# Suppression des outliers prix (> 500 € ou prix nul)
df = df[(df["price"] > 0) & (df["price"] <= 500)]
print(f"Après filtre prix        : {len(df):>7,}  (0 < prix ≤ 500 €)")

# ─────────────────────────────────────────────────────────────────────────────
# 2. SÉLECTION DES FEATURES
#    Règle : colonnes 100 % complètes, hors identifiants et texte brut
# ─────────────────────────────────────────────────────────────────────────────
EXCLUDE = [
    "listing_id", "host_id",        # identifiants
    "name", "amenities",            # texte libre non structuré
    "city", "host_since",           # constante / temporel inutile ici
    "host_location",                # trop de modalités
    "price",                        # cible
]

complete_cols = df.columns[df.isnull().sum() == 0].tolist()
FEATURES   = [c for c in complete_cols if c not in EXCLUDE]
CATEGORICAL = ["neighbourhood", "property_type", "room_type", "instant_bookable"]
NUMERICAL   = [f for f in FEATURES if f not in CATEGORICAL]

print(f"\nFeatures retenues        : {len(FEATURES)}")
print(f"  → Catégorielles        : {CATEGORICAL}")
print(f"  → Numériques           : {len(NUMERICAL)} colonnes")

# ─────────────────────────────────────────────────────────────────────────────
# 3. PRÉPARATION X / y
#    log1p(price) : réduit le skew, améliore les modèles sur données continues
# ─────────────────────────────────────────────────────────────────────────────
X = df[FEATURES].copy()
y = np.log1p(df["price"])          # inverse : np.expm1(y_pred)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\nSplit 80/20 — Train : {len(X_train):,}  |  Test : {len(X_test):,}")

# ─────────────────────────────────────────────────────────────────────────────
# 4. BENCHMARK DES MODÈLES
# ─────────────────────────────────────────────────────────────────────────────

def make_preprocessor(scale_num: bool = False) -> ColumnTransformer:
    """
    Encodeur ordinal pour les catégorielles (inconnu → -1).
    Normalisation optionnelle pour les modèles linéaires.
    """
    num_transformer = StandardScaler() if scale_num else "passthrough"
    return ColumnTransformer(transformers=[
        ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), CATEGORICAL),
        ("num", num_transformer, NUMERICAL),
    ], remainder="drop")


def evaluate(pipeline, X_te, y_te):
    """Retourne MAE, RMSE, R², MAPE sur les prix réels (après expm1)."""
    y_pred_log = pipeline.predict(X_te)
    y_pred     = np.expm1(y_pred_log)
    y_true     = np.expm1(y_te)
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2   = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    return mae, rmse, r2, mape


# Définition des modèles
models = {
    "Ridge": Pipeline([
        ("prep",  make_preprocessor(scale_num=True)),
        ("model", Ridge(alpha=10.0)),
    ]),
    "Lasso": Pipeline([
        ("prep",  make_preprocessor(scale_num=True)),
        ("model", Lasso(alpha=0.001, max_iter=5000)),
    ]),
    "Random Forest": Pipeline([
        ("prep",  make_preprocessor()),
        ("model", RandomForestRegressor(
            n_estimators=200, max_depth=15,
            min_samples_leaf=5, n_jobs=-1, random_state=42
        )),
    ]),
    "XGBoost": Pipeline([
        ("prep",  make_preprocessor()),
        ("model", xgb.XGBRegressor(
            n_estimators=800, learning_rate=0.05, max_depth=6,
            subsample=0.8, colsample_bytree=0.8,
            reg_alpha=0.1, reg_lambda=0.1,
            random_state=42, verbosity=0, n_jobs=-1
        )),
    ]),
    "LightGBM": Pipeline([
        ("prep",  make_preprocessor()),
        ("model", lgb.LGBMRegressor(
            n_estimators=800, learning_rate=0.05, num_leaves=63,
            feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=5,
            reg_alpha=0.1, reg_lambda=0.1,
            random_state=42, verbose=-1, n_jobs=-1
        )),
    ]),
    "CatBoost": Pipeline([
        ("prep",  make_preprocessor()),
        ("model", CatBoostRegressor(
            iterations=800, learning_rate=0.05, depth=6,
            l2_leaf_reg=3, random_seed=42, verbose=0
        )),
    ]),
}

# Entraînement & évaluation
print(f"\n{'─'*65}")
print(f"{'Modèle':<20} {'MAE':>9} {'RMSE':>9} {'R²':>7} {'MAPE':>7} {'Temps':>7}")
print(f"{'─'*65}")

results      = []
best_r2      = -999
best_name    = ""
best_pipeline = None

for name, pipeline in models.items():
    t0 = time.time()
    try:
        pipeline.fit(X_train, y_train)
        elapsed = time.time() - t0
        mae, rmse, r2, mape = evaluate(pipeline, X_test, y_test)
        flag = " ← meilleur" if r2 > best_r2 else ""
        print(f"{name:<20} {mae:>8.2f}€ {rmse:>8.2f}€ {r2:>7.4f} {mape:>6.1f}% {elapsed:>5.1f}s{flag}")
        results.append({"model": name, "MAE": round(mae, 2), "RMSE": round(rmse, 2),
                        "R2": round(r2, 4), "MAPE": round(mape, 1), "time_s": round(elapsed, 1)})
        if r2 > best_r2:
            best_r2       = r2
            best_name     = name
            best_pipeline = pipeline
    except Exception as e:
        elapsed = time.time() - t0
        print(f"{name:<20} {'ERREUR':<9} {'—':>9} {'—':>7} {'—':>7} {elapsed:>5.1f}s  ({e})")
        results.append({"model": name, "MAE": None, "RMSE": None, "R2": None, "MAPE": None, "time_s": round(elapsed, 1)})

print(f"{'─'*65}")
print(f"\n🏆 Meilleur modèle : {best_name}  (R² = {best_r2:.4f})")

# ─────────────────────────────────────────────────────────────────────────────
# 5. POIDS DES VARIABLES (feature importance)
# ─────────────────────────────────────────────────────────────────────────────
all_feature_names = CATEGORICAL + NUMERICAL
model_step = best_pipeline.named_steps["model"]

if hasattr(model_step, "feature_importances_"):
    importances = model_step.feature_importances_
    importance_type = "gain (split-based)"
elif hasattr(model_step, "coef_"):
    importances = np.abs(model_step.coef_)
    importance_type = "|coefficient| (standardisé)"
else:
    importances = np.zeros(len(all_feature_names))
    importance_type = "non disponible"

fi_df = (
    pd.DataFrame({"feature": all_feature_names, "importance": importances})
    .sort_values("importance", ascending=False)
    .reset_index(drop=True)
)
fi_df["importance_pct"] = (fi_df["importance"] / fi_df["importance"].sum() * 100).round(2)

print(f"\n{'─'*50}")
print(f"📊 Poids des variables — {best_name}  ({importance_type})")
print(f"{'─'*50}")
print(fi_df[["feature", "importance", "importance_pct"]]
      .head(20)
      .to_string(index=False))

# Top catégories
geo      = fi_df[fi_df["feature"].isin(["latitude", "longitude"])]["importance_pct"].sum()
sejour   = fi_df[fi_df["feature"].isin(["minimum_nights", "maximum_nights"])]["importance_pct"].sum()
logement = fi_df[fi_df["feature"].isin(["accommodates", "neighbourhood", "property_type", "room_type"])]["importance_pct"].sum()
amenites = fi_df[fi_df["feature"].str.startswith("amenity")]["importance_pct"].sum()
transport = fi_df[fi_df["feature"].str.startswith("flag")]["importance_pct"].sum()

print(f"\n  Localisation GPS       : {geo:.1f} %")
print(f"  Contraintes de séjour  : {sejour:.1f} %")
print(f"  Logement & quartier    : {logement:.1f} %")
print(f"  Équipements (amenities): {amenites:.1f} %")
print(f"  Transports (flags)     : {transport:.1f} %")

# ─────────────────────────────────────────────────────────────────────────────
# 6. EXPORT
# ─────────────────────────────────────────────────────────────────────────────

# — Modèle .pkl (pipeline complet : préprocessing + modèle)
pkl_path = "best_model.pkl"
with open(pkl_path, "wb") as f:
    pickle.dump(best_pipeline, f)
print(f"\n✅ Modèle exporté        : {pkl_path}")

# — Paramètres .json (pour l'app Streamlit)
best_metrics = next(r for r in results if r["model"] == best_name)

params = {
    "model_info": {
        "best_model": best_name,
        "target": "log1p(price)",
        "inverse_transform": "np.expm1(prediction)",
        "price_filter": "0 < price <= 500",
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "metrics": best_metrics,
        "benchmark": results,
    },
    "features": FEATURES,
    "categorical_features": CATEGORICAL,
    "numerical_features": NUMERICAL,
    "feature_importance": (
        fi_df.set_index("feature")["importance"].round(2).to_dict()
    ),
    "feature_importance_pct": (
        fi_df.set_index("feature")["importance_pct"].to_dict()
    ),
    "top_features": fi_df.head(10)["feature"].tolist(),
    "encoders": {
        col: sorted(df[col].dropna().unique().tolist())
        for col in CATEGORICAL
    },
    "numerical_ranges": {
        col: {
            "min":    float(df[col].min()),
            "max":    float(df[col].max()),
            "mean":   float(df[col].mean()),
            "median": float(df[col].median()),
        }
        for col in NUMERICAL
    },
}

json_path = "model_params.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(params, f, ensure_ascii=False, indent=2)
print(f"✅ Paramètres exportés   : {json_path}")
print("\n✓ Pipeline terminé.")
