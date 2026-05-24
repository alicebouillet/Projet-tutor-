import streamlit as st
import pandas as pd

# ── Palette de couleurs ───────────────────────────────────────────────────
TEAL        = "#C7EFCF"
TEAL_LIGHT  = "#E3F7E8"
SAGE        = "#FFCCBA"
DARK        = "#010221"
GOLD        = "#F0B67F"
BRICK       = "#FE5F55"
ORANGE      = "#F3986D"

# ── Dictionnaire des variables Airbnb ────────────────────────────────────
DICT_AIRBNB = {
    "Hôte": [
        {"variable": "host_id",                 "type": "int",   "définition": "Identifiant unique de l'hôte"},
        {"variable": "host_since",              "type": "date",  "définition": "Date d'inscription de l'hôte"},
        {"variable": "host_location",           "type": "str",   "définition": "Localisation de l'hôte"},
        {"variable": "host_response_time",      "type": "str",   "définition": "Temps de réponse de l'hôte"},
        {"variable": "host_response_rate",      "type": "float", "définition": "Taux de réponse de l'hôte (%)"},
        {"variable": "host_acceptance_rate",    "type": "float", "définition": "Taux d'acceptation de l'hôte (%)"},
        {"variable": "host_is_superhost",       "type": "bool",  "définition": "L'hôte est-il un Superhost"},
        {"variable": "host_total_listings_count", "type": "int", "définition": "Nombre total d'annonces de l'hôte"},
        {"variable": "host_has_profile_pic",    "type": "bool",  "définition": "L'hôte a-t-il une photo de profil"},
        {"variable": "host_identity_verified",  "type": "bool",  "définition": "L'identité de l'hôte est-elle vérifiée"},
    ],
    "Localisation": [
        {"variable": "listing_id",     "type": "int",   "définition": "Identifiant unique du logement"},
        {"variable": "neighbourhood",  "type": "str",   "définition": "Quartier du logement"},
        {"variable": "district",       "type": "str",   "définition": "District du logement"},
        {"variable": "arrondissement", "type": "str",   "définition": "Arrondissement parisien (1er à 20e)"},
        {"variable": "city",           "type": "str",   "définition": "Ville (Paris)"},
        {"variable": "latitude",       "type": "float", "définition": "Latitude (WGS84)"},
        {"variable": "longitude",      "type": "float", "définition": "Longitude (WGS84)"},
    ],
    "Logement": [
        {"variable": "name",          "type": "str",   "définition": "Nom de l'annonce"},
        {"variable": "property_type", "type": "str",   "définition": "Type de propriété (appartement, maison, etc.)"},
        {"variable": "room_type",     "type": "str",   "définition": "Type de chambre (logement entier, chambre privée, etc.)"},
        {"variable": "accommodates",  "type": "int",   "définition": "Nombre de personnes accueillies"},
        {"variable": "bedrooms",      "type": "float", "définition": "Nombre de chambres"},
        {"variable": "amenities",     "type": "str",   "définition": "Liste des équipements (format JSON)"},
    ],
    "Tarification": [
        {"variable": "price",          "type": "float", "définition": "Prix par nuit (€)"},
        {"variable": "minimum_nights", "type": "int",   "définition": "Nombre minimum de nuits"},
        {"variable": "maximum_nights", "type": "int",   "définition": "Nombre maximum de nuits"},
        {"variable": "instant_bookable", "type": "bool", "définition": "Réservation instantanée disponible"},
    ],
    "Évaluations": [
        {"variable": "review_scores_rating",        "type": "float", "définition": "Note globale (0-100)"},
        {"variable": "review_scores_accuracy",      "type": "float", "définition": "Note pour la précision de l'annonce (0-10)"},
        {"variable": "review_scores_cleanliness",   "type": "float", "définition": "Note pour la propreté (0-10)"},
        {"variable": "review_scores_checkin",       "type": "float", "définition": "Note pour l'arrivée (0-10)"},
        {"variable": "review_scores_communication", "type": "float", "définition": "Note pour la communication (0-10)"},
        {"variable": "review_scores_location",      "type": "float", "définition": "Note pour l'emplacement (0-10)"},
        {"variable": "review_scores_value",         "type": "float", "définition": "Note pour le rapport qualité-prix (0-10)"},
    ],
    "Équipements": [
        {"variable": "amenity_wifi",                    "type": "bool", "définition": "Wi-Fi disponible"},
        {"variable": "amenity_tv",                      "type": "bool", "définition": "Télévision disponible"},
        {"variable": "amenity_kitchen",                 "type": "bool", "définition": "Cuisine disponible"},
        {"variable": "amenity_washer",                  "type": "bool", "définition": "Machine à laver disponible"},
        {"variable": "amenity_air_conditioning",        "type": "bool", "définition": "Climatisation disponible"},
        {"variable": "amenity_heating",                 "type": "bool", "définition": "Chauffage disponible"},
        {"variable": "amenity_parking",                 "type": "bool", "définition": "Parking disponible"},
        {"variable": "amenity_elevator",                "type": "bool", "définition": "Ascenseur disponible"},
        {"variable": "amenity_dedicated_workspace",     "type": "bool", "définition": "Espace de travail dédié"},
        {"variable": "amenity_pool",                    "type": "bool", "définition": "Piscine disponible"},
        {"variable": "amenity_hot_water",               "type": "bool", "définition": "Eau chaude disponible"},
        {"variable": "amenity_essentials",              "type": "bool", "définition": "Produits de base disponibles"},
        {"variable": "amenity_smoke_alarm",             "type": "bool", "définition": "Détecteur de fumée présent"},
        {"variable": "amenity_fire_extinguisher",       "type": "bool", "définition": "Extincteur présent"},
        {"variable": "amenity_carbon_monoxide_alarm",   "type": "bool", "définition": "Détecteur de monoxyde de carbone"},
        {"variable": "amenity_first_aid_kit",           "type": "bool", "définition": "Trousse de premiers secours"},
    ],
    "Transport": [
        {"variable": "flag_metro",     "type": "bool", "définition": "Logement à moins de 400m d'une station de métro"},
        {"variable": "flag_rer",       "type": "bool", "définition": "Logement à moins de 400m d'une station RER"},
        {"variable": "flag_gare_sncf", "type": "bool", "définition": "Logement à moins de 400m d'une gare SNCF"},
        {"variable": "flag_transport", "type": "bool", "définition": "Logement à moins de 400m d'un transport en commun (métro, RER ou gare)"},
    ],
}

# ── Modalités détaillées pour les variables principales ───────────────────
MODALITES = {
    "room_type": {
        "titre": "Type de chambre",
        "valeurs": {
            "Entire place": "Logement entier - Le voyageur dispose de tout le logement pour lui",
            "Private room": "Chambre privée - Le voyageur dort dans une chambre privée mais partage certains espaces",
            "Shared room": "Chambre partagée - Le voyageur dort dans un espace partagé avec d'autres",
            "Hotel room": "Chambre d'hôtel - Une chambre dans un hôtel ou établissement similaire"
        }
    },
    "property_type": {
        "titre": "Type de propriété",
        "valeurs": {
            "Entire apartment": "Appartement entier",
            "Entire rental unit": "Unité locative entière",
            "Private room in apartment": "Chambre privée dans un appartement",
            "Entire condo": "Condominium entier",
            "Entire loft": "Loft entier",
            "Entire townhouse": "Maison de ville entière",
            "Entire home": "Maison entière",
            "Room in hotel": "Chambre dans un hôtel",
            "Entire serviced apartment": "Appartement avec services entier"
        }
    },
    "host_response_time": {
        "titre": "Temps de réponse de l'hôte",
        "valeurs": {
            "within an hour": "En moins d'une heure",
            "within a few hours": "En quelques heures",
            "within a day": "En moins d'un jour",
            "a few days or more": "Plusieurs jours ou plus"
        }
    },
    "host_is_superhost": {
        "titre": "Statut Superhost",
        "valeurs": {
            "t": "Oui - L'hôte est un Superhost (hôte expérimenté avec d'excellentes évaluations)",
            "f": "Non - L'hôte n'a pas le statut Superhost"
        }
    },
    "instant_bookable": {
        "titre": "Réservation instantanée",
        "valeurs": {
            "t": "Oui - Les voyageurs peuvent réserver instantanément sans attendre l'approbation de l'hôte",
            "f": "Non - L'hôte doit approuver chaque demande de réservation"
        }
    },
    "arrondissement": {
        "titre": "Arrondissements de Paris",
        "valeurs": {
            "Louvre": "1er - Louvre",
            "Bourse": "2e - Bourse",
            "Temple": "3e - Temple",
            "Hôtel-de-Ville": "4e - Hôtel-de-Ville",
            "Panthéon": "5e - Panthéon",
            "Luxembourg": "6e - Luxembourg",
            "Palais-Bourbon": "7e - Palais-Bourbon",
            "Élysée": "8e - Élysée",
            "Opéra": "9e - Opéra",
            "Entrepôt": "10e - Entrepôt",
            "Popincourt": "11e - Popincourt",
            "Reuilly": "12e - Reuilly",
            "Gobelins": "13e - Gobelins",
            "Observatoire": "14e - Observatoire",
            "Vaugirard": "15e - Vaugirard",
            "Passy": "16e - Passy",
            "Batignolles-Monceau": "17e - Batignolles-Monceau",
            "Buttes-Montmartre": "18e - Buttes-Montmartre",
            "Buttes-Chaumont": "19e - Buttes-Chaumont",
            "Ménilmontant": "20e - Ménilmontant"
        },
        "schema": """
        <div style="text-align:center; margin-top:1em; padding:1em; background-color:#E3F7E8; border-radius:8px;">
            <p style="font-weight:bold; color:#C7EFCF; margin-bottom:0.5em;">Carte des arrondissements de Paris</p>
            <div style="display:inline-block; padding:1em; background-color:white; border-radius:8px; border:3px solid #C7EFCF;">
                <svg width="400" height="400" viewBox="0 0 400 400" style="background-color:#FFCCBA10;">
                    <text x="200" y="30" text-anchor="middle" font-size="16" font-weight="bold" fill="#010221">Arrondissements de Paris (disposition en spirale)</text>
                    <circle cx="200" cy="220" r="30" fill="#C7EFCF" opacity="0.7"/>
                    <text x="200" y="225" text-anchor="middle" font-size="14" font-weight="bold">1er-4e</text>
                    <circle cx="160" cy="180" r="25" fill="#FFCCBA" opacity="0.7"/>
                    <text x="160" y="185" text-anchor="middle" font-size="12">5e-6e</text>
                    <circle cx="240" cy="180" r="25" fill="#FFCCBA" opacity="0.7"/>
                    <text x="240" y="185" text-anchor="middle" font-size="12">7e-8e</text>
                    <circle cx="200" cy="140" r="25" fill="#F0B67F" opacity="0.7"/>
                    <text x="200" y="145" text-anchor="middle" font-size="12">9e-10e</text>
                    <circle cx="130" cy="220" r="25" fill="#F0B67F" opacity="0.7"/>
                    <text x="130" y="225" text-anchor="middle" font-size="12">11e-12e</text>
                    <circle cx="270" cy="220" r="25" fill="#F0B67F" opacity="0.7"/>
                    <text x="270" y="225" text-anchor="middle" font-size="12">13e-14e</text>
                    <circle cx="160" cy="270" r="25" fill="#FE5F55" opacity="0.7"/>
                    <text x="160" y="275" text-anchor="middle" font-size="12">15e-16e</text>
                    <circle cx="240" cy="270" r="25" fill="#FE5F55" opacity="0.7"/>
                    <text x="240" y="275" text-anchor="middle" font-size="12">17e-18e</text>
                    <circle cx="200" cy="300" r="25" fill="#FE5F55" opacity="0.7"/>
                    <text x="200" y="305" text-anchor="middle" font-size="12">19e-20e</text>
                </svg>
            </div>
            <p style="margin-top:1em; font-size:0.9em; color:#666;">
                Les arrondissements de Paris sont organisés en spirale horaire,<br/>
                partant du centre (1er-4e) vers l'extérieur (19e-20e)
            </p>
        </div>
        """
    },
    "flag_transport": {
        "titre": "Proximité des transports en commun",
        "valeurs": {
            "1": "Oui - Le logement est situé à moins de 400 mètres (environ 5 minutes à pied) d'au moins une station de métro, RER ou gare SNCF",
            "0": "Non - Le logement est situé à plus de 400 mètres de toute station de transport en commun"
        },
        "schema": """
        <div style="text-align:center; margin-top:1em; padding:1em; background-color:#E3F7E8; border-radius:8px;">
            <p style="font-weight:bold; color:#C7EFCF; margin-bottom:0.5em;">Rayon de proximité des transports</p>
            <div style="display:inline-block; padding:1em; background-color:white; border-radius:8px; border:3px solid #C7EFCF;">
                <svg width="350" height="250" viewBox="0 0 350 250">
                    <text x="175" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#010221">Détection de proximité : rayon de 400m</text>
                    
                    <!-- Station centrale -->
                    <circle cx="175" cy="125" r="8" fill="#FE5F55" stroke="#010221" stroke-width="2"/>
                    <text x="175" y="105" text-anchor="middle" font-size="12" font-weight="bold" fill="#010221">Station</text>
                    
                    <!-- Cercle rayon 400m -->
                    <circle cx="175" cy="125" r="80" fill="none" stroke="#C7EFCF" stroke-width="3" stroke-dasharray="5,5"/>
                    <text x="175" y="215" text-anchor="middle" font-size="11" fill="#C7EFCF" font-weight="bold">400 mètres (≈ 5 min à pied)</text>
                    
                    <!-- Logement proche (flag=1) -->
                    <circle cx="220" cy="100" r="6" fill="#F0B67F" stroke="#010221" stroke-width="1.5"/>
                    <line x1="220" y1="100" x2="220" y2="80" stroke="#010221" stroke-width="1"/>
                    <text x="220" y="73" text-anchor="middle" font-size="10" fill="#010221" font-weight="bold">flag_transport = 1</text>
                    
                    <!-- Logement éloigné (flag=0) -->
                    <circle cx="290" cy="125" r="6" fill="#FFCCBA" stroke="#010221" stroke-width="1.5"/>
                    <line x1="290" y1="125" x2="310" y2="125" stroke="#010221" stroke-width="1"/>
                    <text x="328" y="130" text-anchor="middle" font-size="10" fill="#010221" font-weight="bold">flag_transport = 0</text>
                    
                    <!-- Types de transport -->
                    <g transform="translate(20, 160)">
                        <text x="0" y="0" font-size="11" font-weight="bold" fill="#010221">Types de transport détectés :</text>
                        <text x="0" y="18" font-size="10" fill="#666">🚇 Métro (flag_metro)</text>
                        <text x="150" y="18" font-size="10" fill="#666">🚆 RER (flag_rer)</text>
                        <text x="0" y="35" font-size="10" fill="#666">🚉 Gare SNCF (flag_gare_sncf)</text>
                    </g>
                </svg>
            </div>
            <p style="margin-top:1em; font-size:0.9em; color:#666;">
                La proximité est calculée en <b>distance à vol d'oiseau</b> entre le logement<br/>
                et les stations de transport public de Paris et région Île-de-France
            </p>
        </div>
        """
    }
}


def app():
    """Page du dictionnaire des données"""
    
    # ── En-tête ───────────────────────────────────────────────────────────
    st.markdown(
        """
        <h1 style="text-align:center; color:#C7EFCF;">📚 Dictionnaire des données</h1>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <h3 style="text-align:center; color:#FFCCBA; background-color:#C7EFCF; padding: 0.5em 0; border-radius: 8px;">
        Variables des annonces Airbnb à Paris
        </h3>
        """,
        unsafe_allow_html=True
    )
    
    st.divider()
    
    # ── Introduction ──────────────────────────────────────────────────────
    st.markdown(
        """
        ### 📖 À propos de ce dictionnaire
        
        Cette page présente l'ensemble des **variables utilisées** dans notre application d'analyse des logements Airbnb à Paris.
        Les données proviennent de **Airbnb** et ont été enrichies avec des informations sur les équipements et la localisation.
        
        Les variables sont organisées en **7 catégories principales** :
        - 🏠 **Hôte** : informations sur l'hôte (profil, expérience, taux de réponse)
        - 📍 **Localisation** : adresse, coordonnées GPS, arrondissement
        - 🛏️ **Logement** : type de propriété, capacité d'accueil
        - 💰 **Tarification** : prix, durée de séjour
        - ⭐ **Évaluations** : notes et avis des voyageurs
        - 🔧 **Équipements** : wifi, cuisine, parking, etc.
        - 🚇 **Transport** : proximité des transports en commun (métro, RER, gare)
        """
    )
    
    st.divider()
    
    # ── Barre de recherche ───────────────────────────────────────────────
    st.markdown("### 🔍 Rechercher une variable")
    search_term = st.text_input(
        "Entrez le nom d'une variable ou un mot-clé :",
        placeholder="Ex : gravité, météo, collision...",
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # ── Affichage des tables ──────────────────────────────────────────────
    for table_name, variables in DICT_AIRBNB.items():
        
        # Filtre selon la recherche
        if search_term:
            variables = [
                v for v in variables 
                if search_term.lower() in v["variable"].lower() 
                or search_term.lower() in v["définition"].lower()
            ]
        
        # Affichage seulement si des variables correspondent
        if variables:
            # Icône selon la table
            icons = {
                "Hôte": "👤",
                "Localisation": "📍",
                "Logement": "🛏️",
                "Tarification": "💰",
                "Évaluations": "⭐",
                "Équipements": "🔧",
                "Transport": "🚇"
            }
            icon = icons.get(table_name, "📊")
            
            # Titre de la table
            st.markdown(f"### {icon} {table_name}")
            st.markdown(f"*{len(variables)} variable(s)*")
            
            # Tableau des variables
            df_table = pd.DataFrame(variables)
            df_table = df_table.rename(columns={
                "variable": "Variable",
                "type": "Type",
                "définition": "Définition"
            })
            
            # Style personnalisé pour le tableau
            st.dataframe(
                df_table,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Variable": st.column_config.TextColumn(
                        "Variable",
                        width="small",
                    ),
                    "Type": st.column_config.TextColumn(
                        "Type",
                        width="small",
                    ),
                    "Définition": st.column_config.TextColumn(
                        "Définition",
                        width="large",
                    ),
                }
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
    
    # Message si aucune variable trouvée
    if search_term:
        total_found = sum(
            len([v for v in vars_list 
                 if search_term.lower() in v["variable"].lower() 
                 or search_term.lower() in v["définition"].lower()])
            for vars_list in DICT_AIRBNB.values()
        )
        if total_found == 0:
            st.warning(f"Aucune variable trouvée pour : **{search_term}**")
    
    st.divider()
    
    # ── Modalités des variables principales ───────────────────────────────
    st.markdown("### 🎯 Modalités des variables principales")
    st.markdown(
        """
        Voici le détail des **modalités** (valeurs possibles) pour les variables les plus importantes :
        """
    )
    
    # Sélecteur de variable
    selected_var = st.selectbox(
        "Choisissez une variable :",
        options=list(MODALITES.keys()),
        format_func=lambda x: f"{x} - {MODALITES[x]['titre']}"
    )
    
    if selected_var:
        modal_info = MODALITES[selected_var]
        
        # Affichage des modalités dans un tableau coloré
        modal_df = pd.DataFrame([
            {"Valeur": str(code), "Description": libelle}
            for code, libelle in modal_info["valeurs"].items()
        ])
        
        st.markdown(f"#### {modal_info['titre']} (`{selected_var}`)")
        st.dataframe(
            modal_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Valeur": st.column_config.TextColumn(
                    "Valeur",
                    width="medium",
                ),
                "Description": st.column_config.TextColumn(
                    "Description",
                    width="large",
                ),
            }
        )
        
        # Affichage du schéma visuel si disponible
        if "schema" in modal_info:
            st.markdown(modal_info["schema"], unsafe_allow_html=True)
    
    st.divider()
    
    # ── Informations complémentaires ──────────────────────────────────────
    st.markdown("### ℹ️ Informations complémentaires")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            f"""
            <div style="background-color:{TEAL}; padding: 1em; border-radius: 8px; color:white;">
                <h4 style="color:{GOLD};">📅 Données actuelles</h4>
                <p>Les données Airbnb à Paris comprennent des milliers d'annonces 
                réparties dans les <b>20 arrondissements</b> de la capitale.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="background-color:{SAGE}; padding: 1em; border-radius: 8px; color:{DARK};">
                <h4 style="color:{TEAL};">🎯 Variables clés</h4>
                <p>Le <code><b>prix</b></code> (tarif par nuit) et le <code><b>room_type</b></code> 
                (type de logement) sont les variables principales de l'analyse.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ── Source des données ────────────────────────────────────────────────
    st.info(
        """
        **📚 Source des données :** Airbnb  
        **🏙️ Ville :** Paris, France  
        **📊 Variables enrichies :** Équipements, notes, localisation géographique précise
        """
    )
