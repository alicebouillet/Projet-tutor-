import pandas as pd
import numpy as np
import requests
import json

# ── 1. Chargement de ta base ──────────────────────────────────────────────────
df = pd.read_csv("data/airbnb_enrichi.csv")

# ── 2. Récupération des stations ──────────────────────────────────────────────
def fetch_stations():
    stations = []

    # Métro + RER (RATP)
    for reseau, type_label in [("Metro", "metro"), ("RER", "rer")]:
        print(f"📥 Chargement stations {reseau}...")
        url = (
            "https://data.ratp.fr/api/explore/v2.1/catalog/datasets/"
            "positions-geographiques-des-stations-du-reseau-ratp/exports/json"
            f"?where=reseau%3D'{reseau}'&limit=-1"
        )
        r = requests.get(url, timeout=30)
        data = r.json() if isinstance(r.json(), list) else json.loads(r.text)

        for s in data:
            # Certaines APIs renvoient les lignes comme strings JSON imbriquées
            if isinstance(s, str):
                s = json.loads(s)
            try:
                geo = s.get("geo_point_2d", {})
                # geo peut être un dict {"lat":..., "lon":...} ou une string "lat,lon"
                if isinstance(geo, str):
                    lat, lon = map(float, geo.split(","))
                else:
                    lat = float(geo["lat"])
                    lon = float(geo["lon"])
                stations.append({
                    "nom":  s.get("nom_clean") or s.get("nom", ""),
                    "lat":  lat,
                    "lon":  lon,
                    "type": type_label
                })
            except (KeyError, TypeError, ValueError):
                continue

    # Gares SNCF
    print("📥 Chargement gares SNCF...")
    url_sncf = (
        "https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/"
        "referentiel-gares-voyageurs/exports/json"
        "?where=departement_libellemin%20IN%20('paris','seine-et-marne',"
        "'yvelines','essonne','hauts-de-seine','seine-saint-denis',"
        "'val-de-marne','val-d-oise')&limit=-1"
    )
    r = requests.get(url_sncf, timeout=30)
    data = r.json() if isinstance(r.json(), list) else json.loads(r.text)

    for s in data:
        if isinstance(s, str):
            s = json.loads(s)
        try:
            geo = s.get("wgs_84", {})
            if isinstance(geo, str):
                lat, lon = map(float, geo.split(","))
            else:
                lat = float(geo["lat"])
                lon = float(geo["lon"])
            stations.append({
                "nom":  s.get("intitule_gare", ""),
                "lat":  lat,
                "lon":  lon,
                "type": "gare_sncf"
            })
        except (KeyError, TypeError, ValueError):
            continue

    df_stations = pd.DataFrame(stations).drop_duplicates(subset=["lat", "lon"])
    print(f"✅ {len(df_stations)} stations chargées "
          f"({(df_stations.type=='metro').sum()} métro, "
          f"{(df_stations.type=='rer').sum()} RER, "
          f"{(df_stations.type=='gare_sncf').sum()} SNCF)")
    return df_stations

stations = fetch_stations()

# ── 3. Haversine vectorisé ────────────────────────────────────────────────────
def haversine_vectorized(lat1, lon1, lat2_arr, lon2_arr):
    R = 6371000
    phi1, phi2 = np.radians(lat1), np.radians(lat2_arr)
    dphi    = np.radians(lat2_arr - lat1)
    dlambda = np.radians(lon2_arr - lon1)
    a = np.sin(dphi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

# ── 4. Flags ──────────────────────────────────────────────────────────────────
metros = stations[stations["type"] == "metro"][["lat", "lon"]].values
rers   = stations[stations["type"] == "rer"][["lat", "lon"]].values
gares  = stations[stations["type"] == "gare_sncf"][["lat", "lon"]].values

RAYON = 400

def flag_proche(lat, lon, stations_arr, rayon):
    if pd.isna(lat) or pd.isna(lon) or len(stations_arr) == 0:
        return 0
    distances = haversine_vectorized(lat, lon, stations_arr[:, 0], stations_arr[:, 1])
    return int(distances.min() <= rayon)

print("\n⏳ Calcul des distances...")
df["flag_metro"]     = df.apply(lambda r: flag_proche(r.latitude, r.longitude, metros, RAYON), axis=1)
df["flag_rer"]       = df.apply(lambda r: flag_proche(r.latitude, r.longitude, rers,   RAYON), axis=1)
df["flag_gare_sncf"] = df.apply(lambda r: flag_proche(r.latitude, r.longitude, gares,  RAYON), axis=1)
df["flag_transport"] = ((df["flag_metro"] == 1) | (df["flag_rer"] == 1) | (df["flag_gare_sncf"] == 1)).astype(int)

# ── 5. Export ─────────────────────────────────────────────────────────────────
df.to_csv("airbnb_enrichi.csv", index=False)
print("\n✅ Fichier mis à jour : airbnb_enrichi.csv")
print(f"\n📊 Résumé (rayon {RAYON}m) :")
print(f"   flag_metro     : {df.flag_metro.sum()} logements ({df.flag_metro.mean()*100:.1f}%)")
print(f"   flag_rer       : {df.flag_rer.sum()} logements ({df.flag_rer.mean()*100:.1f}%)")
print(f"   flag_gare_sncf : {df.flag_gare_sncf.sum()} logements ({df.flag_gare_sncf.mean()*100:.1f}%)")
print(f"   flag_transport : {df.flag_transport.sum()} logements ({df.flag_transport.mean()*100:.1f}%)")