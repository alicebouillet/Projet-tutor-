import pandas as pd
import chardet
from pathlib import Path

def detect_encoding(file_path: Path, n_bytes: int = 1_000_000) -> str:
    with open(file_path, "rb") as f:
        raw = f.read(n_bytes)
    result = chardet.detect(raw)
    return result.get("encoding") or "cp1252"

def chargement_donnees():
    # Attention: suppression du point final dans le nom de fichier
    csv_path = Path("data/Listings.csv")

    enc = detect_encoding(csv_path)
    try:
        data_listings = pd.read_csv(csv_path, sep=",", encoding=enc, low_memory=False)
    except UnicodeDecodeError:
        # fallback Windows fréquent
        data_listings = pd.read_csv(csv_path, sep=",", encoding="cp1252", low_memory=False)

    data_listings = data_listings[data_listings["city"] == "Paris"]
    return data_listings

df = chargement_donnees()
