import pandas as pd
import matplotlib.pyplot as plt
import os 

# =========================
# 1. Chargement
# =========================
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
df = pd.read_csv(os.path.join(project_root, "data/airbnb_enrichi.csv"), low_memory=False)

print("="*60)
print("INFO DATASET")
print("="*60)
print(df.shape)
print(df.info())

# =========================
# 2. Nettoyage prix
# =========================
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df = df.dropna(subset=["price"])

# =========================
# 3. Statistiques de base
# =========================
print("="*60)
print("STATISTIQUES PRIX")
print("="*60)
print(df["price"].describe())

# =========================
# 4. Distribution du prix
# =========================
plt.figure()
df["price"].hist(bins=50)
plt.title("Distribution des prix")
plt.xlabel("Prix")
plt.ylabel("Nombre")
plt.show()

# =========================
# 5. Équipements
# =========================
amenity_cols = [col for col in df.columns if col.startswith("amenity_")]

equip_stats = []

for col in amenity_cols:
    count = df[col].sum()
    pct = count / len(df) * 100
    equip_stats.append([col.replace("amenity_", ""), count, pct])

equip_df = pd.DataFrame(equip_stats, columns=["equipement", "count", "pct"])
equip_df = equip_df.sort_values(by="count", ascending=False)

print(equip_df.head(10))

# =========================
# 6. Top équipements (graph)
# =========================
plt.figure()
plt.bar(equip_df["equipement"].head(10), equip_df["count"].head(10))
plt.xticks(rotation=45)
plt.title("Top équipements")
plt.show()

# =========================
# 7. Impact des équipements sur le prix
# =========================
important_features = [
    "amenity_wifi",
    "amenity_air_conditioning",
    "amenity_parking",
    "amenity_pool",
    "amenity_dedicated_workspace"
]

for col in important_features:
    if col in df.columns:
        print("="*50)
        print(col)
        print("Avec :", df[df[col] == 1]["price"].mean())
        print("Sans :", df[df[col] == 0]["price"].mean())

# =========================
# 8. Boxplot (impact prix)
# =========================
for col in important_features:
    if col in df.columns:
        plt.figure()
        df.boxplot(column="price", by=col)
        plt.title(f"Prix vs {col}")
        plt.suptitle("")
        plt.show()

# =========================
# 9. Corrélation
# =========================
numeric_cols = df.select_dtypes(include=["float64", "int64"])

corr = numeric_cols.corr()

plt.figure()
plt.imshow(corr)
plt.colorbar()
plt.title("Matrice de corrélation")
plt.show()

# =========================
# 10. Top corrélations avec prix
# =========================
corr_price = corr["price"].sort_values(ascending=False)
print("="*60)
print("Corrélation avec le prix")
print("="*60)
print(corr_price.head(15))

# =========================
# 11. Segmentation prix
# =========================
df["price_category"] = pd.cut(
    df["price"],
    bins=[0, 50, 100, 200, 1000],
    labels=["cheap", "medium", "high", "luxury"]
)

print(df["price_category"].value_counts())

# =========================
# 12. Analyse équipements par catégorie
# =========================
for col in important_features:
    if col in df.columns:
        print("="*50)
        print(f"Equipement : {col}")
        print(pd.crosstab(df["price_category"], df[col]))

# =========================
# 13. Analyse géographique (si dispo)
# =========================
for col in ["neighbourhood", "district", "arrondissement"]:
    if col in df.columns:
        print("="*60)
        print(f"Top zones : {col}")
        print(df.groupby(col)["price"].mean().sort_values(ascending=False).head(10))

# =========================
# 14. Sauvegarde
# =========================
equip_df.to_csv("equipements_stats.csv", index=False)

print("Analyse terminée.")