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

    detected = detect_encoding(csv_path)
    tried_encodings = ["utf-8", detected, "latin-1"]
    data_listings = None
    for enc in tried_encodings:
        if not enc:
            continue
        try:
            data_listings = pd.read_csv(csv_path, sep=",", encoding=enc, low_memory=False)
            break
        except (UnicodeDecodeError, LookupError):
            continue
    if data_listings is None:
        # As a last resort use latin-1 which maps all bytes 0-255
        data_listings = pd.read_csv(csv_path, sep=",", encoding="latin-1", low_memory=False)

    data_listings = data_listings[data_listings["city"] == "Paris"]
    return data_listings

df = chargement_donnees()
df.to_csv("C:\\Users\\alice\\OneDrive - Université de Poitiers\\INGE2\\cloneGIT_airbnb\\Projet-tutor-\\datalistings_paris.csv", index=False, encoding="utf-8-sig")  # Export pour éviter de refaire le chargement à chaque fois
print(df.head())
print(df.info())
print(df.shape)