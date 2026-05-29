import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from matplotlib.colors import ListedColormap

df = pd.read_csv("data/airbnb_enrichi.csv", encoding="utf-8-sig")
# --- Tableau complet (% null de chaque colonne), trié décroissant ---
table_df = pd.DataFrame({
    "Colonne": df.columns,
    "Valeurs_nulles": df.isna().sum().values,
    "Pourcentage_null": (df.isna().mean() * 100).values
}).sort_values("Pourcentage_null", ascending=False).reset_index(drop=True)

print(table_df)

# --- Vérification : aucune valeur manquante ---
if table_df['Valeurs_nulles'].sum() == 0:
    print("[INFO] : aucune valeur manquante, graphiques ignorés.")
else:
    # --- Graphique en barres (uniquement les colonnes avec des valeurs manquantes) ---
    table_avec_nulls = table_df[table_df['Pourcentage_null'] > 0]

    colors = [
        '#d73027' if p > 50 else '#fc8d59' if p > 20 else '#fee08b'
        for p in table_avec_nulls['Pourcentage_null']
    ]

    fig, ax = plt.subplots(figsize=(12, max(6, len(table_avec_nulls) * 0.4)))
    fig.suptitle("Données manquantes :", fontsize=14, fontweight='bold')

    ax.barh(
        table_avec_nulls['Colonne'],
        table_avec_nulls['Pourcentage_null'],
        color=colors
    )
    ax.set_xlabel("% de valeurs manquantes")
    # Annoter chaque barre avec le nombre de valeurs manquantes
    for i, (_, row) in enumerate(table_avec_nulls.iterrows()):
        pct = row['Pourcentage_null']
        cnt = int(row['Valeurs_nulles'])
        ax.text(pct + 0.5, i, f"{cnt}", va='center', fontsize=9)
    ax.set_title(f"Colonnes avec valeurs manquantes ({len(table_avec_nulls)}/{len(table_df)})")
    ax.axvline(x=50, color='red', linestyle='--', linewidth=1)
    ax.axvline(x=20, color='orange', linestyle='--', linewidth=1)
    ax.invert_yaxis()

    patch_rouge  = mpatches.Patch(color='#d73027', label='> 50%')
    patch_orange = mpatches.Patch(color='#fc8d59', label='20% – 50%')
    patch_jaune  = mpatches.Patch(color='#fee08b', label='< 20%')
    ax.legend(handles=[patch_rouge, patch_orange, patch_jaune])

    plt.tight_layout()
    bar_out = os.path.join("data", "missing_bar.png")
    plt.savefig(bar_out, dpi=150)
    plt.close()


    # --- Export CSV brut ---
    csv_out = os.path.join("data", "table_nulls.csv")
    table_df.to_csv(csv_out, index=False, encoding="utf-8-sig")

    print(" - Graphique barres : missing_bar.png")

    # --- Résumé des valeurs disponibles par colonne ---
    values_summary = []
    for col in df.columns:
        non_null = df[col].dropna()
        n_unique = int(non_null.nunique())
        top = non_null.value_counts().head(5)
        examples = "; ".join([f"{str(v)} ({c})" for v, c in top.items()])
        values_summary.append({
            "Colonne": col,
            "N_unique": n_unique,
            "Exemples": examples
        })

    vals_df = pd.DataFrame(values_summary).sort_values("N_unique", ascending=False).reset_index(drop=True)

    csv_vals_out = os.path.join("data", "values_summary.csv")
    vals_df.to_csv(csv_vals_out, index=False, encoding="utf-8-sig")


    SEUIL_CATEGORIELLE = 20  # colonnes avec moins de 20 valeurs uniques = affichage complet

    print("=" * 60)
    print(f"Base : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    print("=" * 60)

    for col in df.columns:
        n_unique = df[col].nunique()
        dtype = df[col].dtype
        n_manquants = df[col].isna().sum()
        pct_manquants = n_manquants / len(df) * 100

        print(f"\n📌 {col}")
        print(f"   Type : {dtype} | Valeurs uniques : {n_unique} | Manquants : {n_manquants} ({pct_manquants:.1f}%)")

        if n_unique <= SEUIL_CATEGORIELLE:
            # Affiche toutes les valeurs avec leur fréquence
            counts = df[col].value_counts(dropna=False)
            for val, count in counts.items():
                pct = count / len(df) * 100
                print(f"     • {val} → {count} ({pct:.1f}%)")

        elif dtype in ["int64", "float64"]:
            # Variable numérique avec trop de valeurs uniques : stats
            print(f"   Min : {df[col].min():.2f} | Max : {df[col].max():.2f} | "
                f"Moyenne : {df[col].mean():.2f} | Médiane : {df[col].median():.2f}")

        else:
            # Texte libre avec trop de valeurs : juste un aperçu
            exemples = df[col].dropna().unique()[:5]
            print(f"   Exemples : {list(exemples)}")

    print("\n" + "=" * 60)

    print(" - Graphique résumé valeurs : values_summary_bar.png")
# Détecter les doublons (True/False)
doublons = df.duplicated()  # Garde la première occurrence, marque les suivantes
print(f"\nNombre de doublons : {doublons.sum()}")

#Valeurs aberrantes : par exemple, prix négatif ou très élevé
prix_negatif = df[df["price"] < 0]
prix_eleve = df[df["price"] > 1000]  # seuil arbitra
print(f"\nAnnonces avec prix négatif : {len(prix_negatif)}")
print(f"Annonces avec prix > 1000€ : {len(prix_eleve)} nom du listing_id : {prix_eleve['listing_id'].tolist()}")


