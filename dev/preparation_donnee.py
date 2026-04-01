import pandas as pd
import geopandas as gpd
import ast

# ── 1. Chargement ─────────────────────────────────────────────────────────────
df = pd.read_csv("data/datalistings_paris.csv")
df = df.dropna(subset=["latitude", "longitude"])

# ── 2. Colonne arrondissement ─────────────────────────────────────────────────
url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson"
arrondissements = gpd.read_file(url)[["l_aroff", "geometry"]].rename(columns={"l_aroff": "arrondissement"})
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")
arrondissements = arrondissements.to_crs("EPSG:4326")
gdf = gpd.sjoin(gdf, arrondissements[["arrondissement", "geometry"]], how="left", predicate="within")
gdf = gdf.drop(columns=["geometry", "index_right"])
df = pd.DataFrame(gdf)

# ── 3. Parsing amenities ──────────────────────────────────────────────────────
def parse_amenities(val):
    if pd.isna(val):
        return []
    try:
        return ast.literal_eval(val)
    except:
        return []

df["amenities_parsed"] = df["amenities"].apply(parse_amenities)

# ── 4. Dictionnaire de catégories (mot-clé → nom de colonne) ─────────────────
CATEGORIES = {
    "amenity_wifi":              ["wifi", "internet"],
    "amenity_tv":                ["tv", "television", "netflix", "hbo", "disney", "apple tv", "chromecast"],
    "amenity_kitchen":           ["kitchen", "oven", "microwave", "fridge", "refrigerator", "cooking", "kitchenette"],
    "amenity_washer":            ["washer", "dryer", "washing"],
    "amenity_air_conditioning":  ["air condition", "ac ", " ac", "split-type", "portable ac", "climati"],
    "amenity_heating":           ["heat", "chauffage"],
    "amenity_parking":           ["parking", "garage", "ev charger"],
    "amenity_bathtub":           ["bathtub", " bath", "hot tub", "jacuzzi", "soaking tub"],
    "amenity_shampoo":           ["shampoo", "conditioner", "body wash", "body soap", "shower gel"],
    "amenity_coffee":            ["coffee", "espresso", "nespresso", "keurig", "french press"],
    "amenity_pets_allowed":      ["pet", "dog", "cat allowed"],
    "amenity_pool":              ["pool", "piscine"],
}

# ── 5. Fonction de matching par mot-clé ──────────────────────────────────────
def match_category(amenity_list, keywords):
    for amenity in amenity_list:
        amenity_lower = amenity.lower()
        if any(kw in amenity_lower for kw in keywords):
            return 1
    return 0

# ── 6. Création des flags catégorisés ────────────────────────────────────────
for col, keywords in CATEGORIES.items():
    df[col] = df["amenities_parsed"].apply(lambda lst: match_category(lst, keywords))

# ── 7. Flags pour équipements non catégorisés (si présents dans >= 5%) ──────
SEUIL = 0.05
n = len(df)

# Récupère tous les équipements qui ne matchent aucune catégorie
all_keywords_flat = [kw for kws in CATEGORIES.values() for kw in kws]

def get_uncategorized(amenity_list):
    result = []
    for amenity in amenity_list:
        a_lower = amenity.lower()
        if not any(kw in a_lower for kw in all_keywords_flat):
            result.append(amenity)
    return result

df["amenities_uncategorized"] = df["amenities_parsed"].apply(get_uncategorized)

# Compte les occurrences de chaque équipement non catégorisé
from collections import Counter
counter = Counter(a for lst in df["amenities_uncategorized"] for a in lst)

# Garde uniquement ceux présents dans >= 5% des logements
kept = {amenity: count for amenity, count in counter.items() if count / n >= SEUIL}

print(f"\n📌 Équipements non catégorisés conservés (>= {SEUIL*100:.0f}%) : {len(kept)}")
for amenity, count in sorted(kept.items(), key=lambda x: -x[1]):
    print(f"   • {amenity} → {count} ({count/n*100:.1f}%)")

# Crée un flag pour chacun
def clean_col_name(name):
    return "amenity_" + name.lower().replace(" ", "_").replace("/", "_").replace("-", "_")

for amenity in kept:
    col = clean_col_name(amenity)
    df[col] = df["amenities_uncategorized"].apply(lambda lst: int(amenity in lst))

# ── 8. Nettoyage colonnes intermédiaires ─────────────────────────────────────
df = df.drop(columns=["amenities_parsed", "amenities_uncategorized"])

# ── 9. Export ─────────────────────────────────────────────────────────────────
df.to_csv("airbnb_enrichi.csv", index=False)
print(f"\n✅ Fichier exporté : airbnb_enrichi.csv")
print(f"   Dimensions : {df.shape[0]} lignes × {df.shape[1]} colonnes")

# ── 10. Résumé des flags créés ────────────────────────────────────────────────
cols_amenity = [c for c in df.columns if c.startswith("amenity_")]
print(f"\n📊 Taux de présence par équipement :")
summary = df[cols_amenity].mean().sort_values(ascending=False) * 100
for col, pct in summary.items():
    print(f"   {col:<40} {pct:.1f}%")