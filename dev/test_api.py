import requests

urls = {
    "metro": (
        "https://data.ratp.fr/api/explore/v2.1/catalog/datasets/"
        "positions-geographiques-des-stations-du-reseau-ratp/exports/json"
        "?where=reseau%3D'Metro'&limit=5"
    ),
    "rer": (
        "https://data.ratp.fr/api/explore/v2.1/catalog/datasets/"
        "positions-geographiques-des-stations-du-reseau-ratp/exports/json"
        "?where=reseau%3D'RER'&limit=5"
    ),
    "sncf": (
        "https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/"
        "referentiel-gares-voyageurs/exports/json"
        "?where=departement_libellemin%20IN%20('paris')&limit=5"
    ),
}

for nom, url in urls.items():
    try:
        r = requests.get(url, timeout=30)
        print(f"\n── {nom} ──")
        print(f"   Status  : {r.status_code}")
        print(f"   Headers : {dict(r.headers).get('Content-Type', '?')}")
        print(f"   Contenu : {r.text[:300]}")
    except Exception as e:
        print(f"\n── {nom} ── ERREUR : {e}")