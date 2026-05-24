"""
pagesWeb/modelePrediction.py
Page de prédiction de prix Airbnb Paris
Streamlit multi-pages, présentation jury.

Modèle : Random Forest / Gradient Boosting / Extra Trees
Features : property_type, room_type, accommodates, latitude, longitude,
           minimum_nights, maximum_nights, instant_bookable, amenities, transport
"""

import joblib
import json
import os
import numpy as np
import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# FONCTION PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────

def app():
    # ─────────────────────────────────────────────────────────────────────────────
    # STYLE
    # ─────────────────────────────────────────────────────────────────────────────

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #ffffff; }

.hero { margin-bottom: 1.8rem; }
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    color: #1a202c;
    line-height: 1.15;
    margin-bottom: 0.3rem;
}
.hero-sub { font-size: 0.9rem; color: #4a5568; }
.hero-pill {
    display: inline-block;
    background: #f7fafc;
    border: 1px solid #e2e8f0;
    border-radius: 99px;
    padding: 0.2rem 0.75rem;
    font-size: 0.75rem;
    color: #4a5568;
    margin-right: 0.4rem;
    margin-top: 0.5rem;
}

.card {
    background: #f7fafc;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.3rem 1.5rem 1.5rem;
    margin-bottom: 1rem;
}
.card-title {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: #2d3748;
    margin-bottom: 1.1rem;
}

label { color: #2d3748 !important; font-size: 0.83rem !important; }

.result-panel {
    border-radius: 16px;
    padding: 2.2rem 1.8rem;
    text-align: center;
}
.result-grave {
    background: #fef2f2;
    border: 2px solid #fca5a5;
}
.result-ok {
    background: #f0fdf4;
    border: 2px solid #86efac;
}
.score-num {
    font-family: 'DM Serif Display', serif;
    font-size: 4.2rem;
    line-height: 1;
    margin-bottom: 0.2rem;
}
.score-label {
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.score-desc { font-size: 0.82rem; color: #4a5568; margin-bottom: 1.2rem; }

.gauge-bg {
    background: #e5e7eb;
    border-radius: 99px;
    height: 6px;
    overflow: hidden;
    margin-bottom: 1rem;
}
.gauge-fill { height: 6px; border-radius: 99px; }

.risk-badge {
    display: inline-block;
    padding: 0.3rem 1rem;
    border-radius: 99px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.06em;
}
.risk-low   { background:#dcfce7; color:#16a34a; border:1px solid #86efac; }
.risk-mod   { background:#fef3c7; color:#ca8a04; border:1px solid #fde047; }
.risk-high  { background:#fed7aa; color:#ea580c; border:1px solid #fdba74; }
.risk-vhigh { background:#fee2e2; color:#dc2626; border:1px solid #fca5a5; }

.threshold-note { font-size:0.75rem; color:#4a5568; margin-top:1rem; text-align:center; }

.detail-card {
    background:#f9fafb; border:1px solid #e5e7eb;
    border-radius:12px; padding:1rem 1.2rem; margin-top:1rem;
}
.detail-title {
    font-size:0.68rem; font-weight:600;
    letter-spacing:0.12em; text-transform:uppercase;
    color:#4a5568; margin-bottom:0.7rem;
}
.prob-row { display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem; }
.prob-label { font-size:0.83rem; color:#6b7280; }
.prob-val { font-size:0.95rem; font-weight:600; }

.empty-state {
    background:#f9fafb; border:1px solid #e5e7eb;
    border-radius:14px; padding:3.5rem 1.5rem; text-align:center;
}
.empty-icon { font-size:2.8rem; margin-bottom:1rem; }
.empty-text { font-size:0.9rem; color:#6b7280; line-height:1.6; }

    #MainMenu, header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────────
    # CHARGEMENT MODÈLE & MÉTRIQUES
    # ─────────────────────────────────────────────────────────────────────────────

    # Chemin relatif au répertoire parent (appStreamlit)
    CURRENT_DIR = os.path.dirname(__file__)
    MODELS_DIR = os.path.join(CURRENT_DIR, "..", "models")

    @st.cache_resource
    def load_assets():
        model_path = os.path.join(MODELS_DIR, "novabank_airbnb_model.pkl")
        params_path = os.path.join(MODELS_DIR, "model_params.json")
        
        model = joblib.load(model_path)
        params = {}
        if os.path.exists(params_path):
            with open(params_path, encoding="utf-8") as f:
                params = json.load(f)
        return model, params

    try:
        model, params = load_assets()
        model_ok = True
        metrics = params.get("model_info", {}).get("metrics", {})
        features_list = params.get("features", [])
    except FileNotFoundError as e:
        model_ok = False
        load_error = str(e)
        metrics = {}
        features_list = []

    # ─────────────────────────────────────────────────────────────────────────────
    # DICTIONNAIRES MODALITÉS AIRBNB
    # ─────────────────────────────────────────────────────────────────────────────

    PROPERTY_TYPES = [
        "Entire apartment", "Private room in apartment", "Entire condo", 
        "Entire loft", "Private room in townhouse", "Entire townhouse",
        "Entire rental unit", "Entire place", "Entire serviced apartment",
        "Private room in rental unit", "Entire home", "Private room in home",
        "Private room in bed and breakfast", "Room in boutique hotel",
        "Room in hotel", "Shared room in apartment", "Entire guest suite",
        "Private room in guest suite", "Private room in loft"
    ]
    
    ROOM_TYPES = ["Entire place", "Private room", "Shared room", "Hotel room"]
    
    ARRONDISSEMENTS = [
        "Louvre", "Bourse", "Temple", "Hôtel-de-Ville", "Panthéon",
        "Luxembourg", "Palais-Bourbon", "Élysée", "Opéra", "Entrepôt",
        "Popincourt", "Reuilly", "Gobelins", "Observatoire", "Vaugirard",
        "Passy", "Batignolles-Monceau", "Buttes-Montmartre", "Buttes-Chaumont",
        "Ménilmontant"
    ]

    # ─────────────────────────────────────────────────────────────────────────────
    # HEADER
    # ─────────────────────────────────────────────────────────────────────────────

    st.markdown("""
    <div class='hero'>
      <div class='hero-title'>🏠 Prédiction de prix Airbnb Paris</div>
      <div class='hero-sub'>
        <span class='hero-pill'>LightGBM · OrdinalEncoder</span>
        <span class='hero-pill'>Dataset enrichi avec transport</span>
        <span class='hero-pill'>R² = 0.54 · MAE = 28.5€</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if not model_ok:
        st.warning(f"""
        ⚠️ **Modèle introuvable**
        
        Le modèle n'a pas encore été créé. Pour générer le modèle:
        
        1. Lance le script de training: 
           ```bash
           python dev/modele/testModele.py
           ```
        2. Sauvegarde le meilleur modèle dans `appStreamlit/models/novabank_airbnb_model.pkl`
        3. Sauvegarde les paramètres dans `appStreamlit/models/model_params.json`
        
        **Erreur**: `{load_error}`
        """)
        st.stop()

    # ─────────────────────────────────────────────────────────────────────────────
    # FORMULAIRE
    # ─────────────────────────────────────────────────────────────────────────────

    col_form, col_result = st.columns([1.15, 0.85], gap="large")

    with col_form:

        # ── Caractéristiques du logement ─────────────────────────────────────────
        st.markdown("<div class='card'><div class='card-title'>🏠 Caractéristiques du logement</div>", unsafe_allow_html=True)
        
        property_type = st.selectbox("Type de propriété", PROPERTY_TYPES, index=0)
        room_type = st.selectbox("Type de location", ROOM_TYPES, index=0)
        
        r1c1, r1c2 = st.columns(2)
        accommodates = r1c1.number_input("Nombre de voyageurs", 1, 16, 2, help="Capacité d'accueil")
        minimum_nights = r1c2.number_input("Nuits minimum", 1, 1125, 2)
        
        r2c1, r2c2 = st.columns(2)
        maximum_nights = r2c1.number_input("Nuits maximum", 1, 1125, 1125)
        instant_bookable = r2c2.selectbox("Réservation instantanée", ["Non", "Oui"])
        
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Localisation ──────────────────────────────────────────────────────────
        st.markdown("<div class='card'><div class='card-title'>📍 Localisation</div>", unsafe_allow_html=True)
        
        neighbourhood = st.selectbox("Quartier/Arrondissement", ARRONDISSEMENTS, index=17)
        
        lc1, lc2 = st.columns(2)
        latitude = lc1.number_input("Latitude", 48.80, 48.92, 48.86, step=0.001, 
                                     help="Entre 48.80 et 48.92 pour Paris")
        longitude = lc2.number_input("Longitude", 2.20, 2.45, 2.35, step=0.001,
                                      help="Entre 2.20 et 2.45 pour Paris")
        
        st.markdown("**Transport à proximité**")
        tc1, tc2, tc3, tc4 = st.columns(4)
        flag_metro = tc1.checkbox("Métro", value=True)
        flag_rer = tc2.checkbox("RER", value=False)
        flag_gare_sncf = tc3.checkbox("Gare SNCF", value=False)
        flag_transport = tc4.checkbox("Transport", value=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Équipements ───────────────────────────────────────────────────────────
        st.markdown("<div class='card'><div class='card-title'>✨ Équipements & Commodités</div>", unsafe_allow_html=True)
        
        st.markdown("**Équipements essentiels**")
        eq1c1, eq1c2, eq1c3, eq1c4 = st.columns(4)
        amenity_wifi = eq1c1.checkbox("WiFi", value=True)
        amenity_tv = eq1c2.checkbox("TV", value=False)
        amenity_kitchen = eq1c3.checkbox("Cuisine", value=True)
        amenity_washer = eq1c4.checkbox("Lave-linge", value=False)
        
        eq2c1, eq2c2, eq2c3, eq2c4 = st.columns(4)
        amenity_air_conditioning = eq2c1.checkbox("Climatisation", value=False)
        amenity_heating = eq2c2.checkbox("Chauffage", value=True)
        amenity_parking = eq2c3.checkbox("Parking", value=False)
        amenity_elevator = eq2c4.checkbox("Ascenseur", value=False)
        
        st.markdown("**Confort & Sécurité**")
        eq3c1, eq3c2, eq3c3, eq3c4 = st.columns(4)
        amenity_essentials = eq3c1.checkbox("Essentiels", value=False)
        amenity_smoke_alarm = eq3c2.checkbox("Détecteur fumée", value=False)
        amenity_fire_extinguisher = eq3c3.checkbox("Extincteur", value=False)
        amenity_carbon_monoxide_alarm = eq3c4.checkbox("Détecteur CO", value=False)
        
        eq4c1, eq4c2, eq4c3, eq4c4 = st.columns(4)
        amenity_hot_water = eq4c1.checkbox("Eau chaude", value=False)
        amenity_hangers = eq4c2.checkbox("Cintres", value=False)
        amenity_dedicated_workspace = eq4c3.checkbox("Espace travail", value=False)
        amenity_long_term_stays_allowed = eq4c4.checkbox("Séjour long", value=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

        predict_btn = st.button("💰 Estimer le prix",
                                 type="primary", use_container_width=True)

    # ─────────────────────────────────────────────────────────────────────────────
    # RÉSULTAT
    # ─────────────────────────────────────────────────────────────────────────────

    with col_result:
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        if predict_btn:
            # Préparer les données pour la prédiction
            # Créer un DataFrame avec toutes les colonnes attendues par le modèle
            
            # Créer le dictionnaire de données avec les features attendues
            input_data = {
                "neighbourhood": neighbourhood,
                "latitude": latitude,
                "longitude": longitude,
                "property_type": property_type,
                "room_type": room_type,
                "accommodates": accommodates,
                "minimum_nights": minimum_nights,
                "maximum_nights": maximum_nights,
                "instant_bookable": instant_bookable,
                # Amenities
                "amenity_wifi": int(amenity_wifi),
                "amenity_tv": int(amenity_tv),
                "amenity_kitchen": int(amenity_kitchen),
                "amenity_washer": int(amenity_washer),
                "amenity_air_conditioning": int(amenity_air_conditioning),
                "amenity_heating": int(amenity_heating),
                "amenity_parking": int(amenity_parking),
                "amenity_bathtub": 0,
                "amenity_shampoo": 0,
                "amenity_coffee": 0,
                "amenity_pets_allowed": 0,
                "amenity_pool": 0,
                "amenity_long_term_stays_allowed": int(amenity_long_term_stays_allowed),
                "amenity_essentials": int(amenity_essentials),
                "amenity_elevator": int(amenity_elevator),
                "amenity_smoke_alarm": int(amenity_smoke_alarm),
                "amenity_fire_extinguisher": int(amenity_fire_extinguisher),
                "amenity_iron": 0,
                "amenity_hot_water": int(amenity_hot_water),
                "amenity_hangers": int(amenity_hangers),
                "amenity_dedicated_workspace": int(amenity_dedicated_workspace),
                "amenity_host_greets_you": 0,
                "amenity_carbon_monoxide_alarm": int(amenity_carbon_monoxide_alarm),
                "amenity_stove": 0,
                "amenity_dishes_and_silverware": 0,
                "amenity_bed_linens": 0,
                "amenity_indoor_fireplace": 0,
                "amenity_breakfast": 0,
                "amenity_first_aid_kit": 0,
                "amenity_luggage_dropoff_allowed": 0,
                "amenity_patio_or_balcony": 0,
                "amenity_extra_pillows_and_blankets": 0,
                "amenity_private_entrance": 0,
                "amenity_ethernet_connection": 0,
                "amenity_lockbox": 0,
                # Transport flags
                "flag_metro": int(flag_metro),
                "flag_rer": int(flag_rer),
                "flag_gare_sncf": int(flag_gare_sncf),
                "flag_transport": int(flag_transport),
            }
            
            X = pd.DataFrame([input_data])
            
            # S'assurer que les colonnes sont dans le bon ordre si features_list est disponible
            if features_list:
                # Ajouter les colonnes manquantes avec valeur 0
                for col in features_list:
                    if col not in X.columns:
                        X[col] = 0
                # Réorganiser les colonnes dans l'ordre attendu
                X = X[features_list]
            
            # Prédiction (le modèle prédit log1p(price), donc on applique expm1)
            log_price_pred = float(model.predict(X)[0])
            price_pred = float(np.expm1(log_price_pred))
            
            # Arrondir le prix
            price_pred = round(price_pred, 2)
            
            # Catégorisation du prix
            if price_pred < 50:
                niveau, price_cls, bar_color = "Budget",        "risk-low",   "#34d399"
            elif price_pred < 100:
                niveau, price_cls, bar_color = "Économique",    "risk-mod",   "#fbbf24"
            elif price_pred < 150:
                niveau, price_cls, bar_color = "Moyen",         "risk-high",  "#fb923c"
            elif price_pred < 250:
                niveau, price_cls, bar_color = "Élevé",         "risk-vhigh", "#f87171"
            else:
                niveau, price_cls, bar_color = "Premium",       "risk-vhigh", "#dc2626"

            result_cls  = "result-ok"
            score_color = "#2563eb"
            emoji       = "💰"
            
            # Calcul du prix par voyageur
            price_per_guest = price_pred / accommodates if accommodates > 0 else price_pred

            st.markdown(f"""
            <div class='result-panel {result_cls}' style='border-color:{bar_color}'>
                <div style='font-size:2rem; margin-bottom:0.5rem'>{emoji}</div>
                <div class='score-num' style='color:{score_color}'>{price_pred:.0f}€</div>
                <div class='score-label' style='color:{score_color}'>PRIX ESTIMÉ / NUIT</div>
                <div class='score-desc'>Prédiction basée sur {accommodates} voyageur(s)</div>
                <div class='gauge-bg'>
                    <div class='gauge-fill'
                         style='width:{min(price_pred/3, 100):.1f}%; background:{bar_color}'></div>
                </div>
                <span class='risk-badge {price_cls}'>{niveau}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class='detail-card'>
                <div class='detail-title'>Détail du prix</div>
                <div class='prob-row'>
                    <span class='prob-label'>Prix par nuit</span>
                    <span class='prob-val' style='color:#2563eb'>{price_pred:.0f}€</span>
                </div>
                <div class='prob-row'>
                    <span class='prob-label'>Prix par voyageur</span>
                    <span class='prob-val' style='color:#2563eb'>{price_per_guest:.0f}€</span>
                </div>
                <div class='prob-row'>
                    <span class='prob-label'>Prix pour {minimum_nights} nuits (minimum)</span>
                    <span class='prob-val' style='color:#2563eb'>{price_pred * minimum_nights:.0f}€</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if metrics:
                st.markdown(f"""
                <div class='detail-card'>
                    <div class='detail-title'>Performances du modèle</div>
                    <div class='prob-row'>
                        <span class='prob-label'>R² Score</span>
                        <span class='prob-val' style='color:#8892a4'>{metrics.get("R2","—")}</span>
                    </div>
                    <div class='prob-row'>
                        <span class='prob-label'>RMSE</span>
                        <span class='prob-val' style='color:#8892a4'>{metrics.get("RMSE_eur","—")}€</span>
                    </div>
                    <div class='prob-row'>
                        <span class='prob-label'>MAE</span>
                        <span class='prob-val' style='color:#8892a4'>{metrics.get("MAE_eur","—")}€</span>
                    </div>
                    <div class='prob-row'>
                        <span class='prob-label'>MAPE</span>
                        <span class='prob-val' style='color:#8892a4'>{metrics.get("MAPE_pct","—")}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
                        <div class='threshold-note'>
                        Estimation basée sur les données enrichies des Airbnb à Paris
                        </div>
                        """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class='empty-state'>
                <div class='empty-icon'>💰</div>
                <div class='empty-text'>
                    Remplis le formulaire à gauche<br>
                    et clique sur <strong>Estimer le prix</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)