import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from matplotlib.colors import ListedColormap
from lecture_donnee import chargement_donnees

df = chargement_donnees()
dossier = r"c:/Users/alice/OneDrive - Université de Poitiers/INGE2/cloneGIT_airbnb/airbnb_bordeaux/data/"
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
    ax.set_title(f"Colonnes avec valeurs manquantes ({len(table_avec_nulls)}/{len(table_df)})")
    ax.axvline(x=50, color='red', linestyle='--', linewidth=1)
    ax.axvline(x=20, color='orange', linestyle='--', linewidth=1)
    ax.invert_yaxis()

    patch_rouge  = mpatches.Patch(color='#d73027', label='> 50%')
    patch_orange = mpatches.Patch(color='#fc8d59', label='20% – 50%')
    patch_jaune  = mpatches.Patch(color='#fee08b', label='< 20%')
    ax.legend(handles=[patch_rouge, patch_orange, patch_jaune])

    plt.tight_layout()
    bar_out = os.path.join(dossier, "missing_bar.png")
    plt.savefig(bar_out, dpi=150)
    plt.close()

    # --- Heatmap (vert = présent, rouge = manquant) ---
    if not table_df.empty:
        cols_heat = table_df["Colonne"].tolist()
        sample = df[cols_heat].head(1000).isna().astype(int)

        cmap = ListedColormap(["#2ca25f", "#de2d26"])  # 0 = vert, 1 = rouge

        fig, ax = plt.subplots(figsize=(14, max(4, len(cols_heat) * 0.28)))
        sns.heatmap(
            sample.T,
            cmap=cmap,
            vmin=0,
            vmax=1,
            cbar=True,
            cbar_kws={"ticks": [0, 1], "label": "Valeur"},
            ax=ax
        )

        ax.set_title("Heatmap valeurs manquantes (1 000 premières lignes)")
        ax.set_xlabel("Lignes")
        ax.set_ylabel("Colonnes")

        cbar = ax.collections[0].colorbar
        cbar.set_ticklabels(["Présent (0)", "Manquant (1)"])

        plt.tight_layout()
        heatmap_out = os.path.join(dossier, "missing_heatmap.png")
        plt.savefig(heatmap_out, dpi=150)
        plt.close()

    # --- Export CSV brut ---
    csv_out = os.path.join(dossier, "table_nulls.csv")
    table_df.to_csv(csv_out, index=False, encoding="utf-8-sig")

    print(" - Graphique barres : missing_bar.png")
    print(" - Heatmap          : missing_heatmap.png")
