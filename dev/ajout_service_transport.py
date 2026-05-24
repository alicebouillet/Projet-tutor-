import pandas as pd
import numpy as np

# ── 1. Chargement de ta base ──────────────────────────────────────────────────
df = pd.read_csv("data/airbnb_enrichi.csv")

# ── 2. Stations embarquées (source : données publiques OSM/RATP/SNCF) ────────
# Les APIs open data RATP/SNCF nécessitent des accès réseau non disponibles
# dans tous les environnements. Ces données statiques couvrent l'ensemble
# des stations Île-de-France pertinentes (~441 stations).

STATIONS_STATIQUES = [
    # ── MÉTRO ─────────────────────────────────────────────────────────────────
    # Ligne 1
    ("La Défense", 48.8921, 2.2387, "metro"),
    ("Esplanade de La Défense", 48.8889, 2.2478, "metro"),
    ("Pont de Neuilly", 48.8847, 2.2593, "metro"),
    ("Les Sablons", 48.8788, 2.2677, "metro"),
    ("Porte Maillot", 48.8787, 2.2830, "metro"),
    ("Argentine", 48.8757, 2.2916, "metro"),
    ("Charles de Gaulle Étoile", 48.8738, 2.2950, "metro"),
    ("George V", 48.8726, 2.3007, "metro"),
    ("Franklin D. Roosevelt", 48.8699, 2.3082, "metro"),
    ("Champs-Élysées Clemenceau", 48.8668, 2.3131, "metro"),
    ("Concorde", 48.8655, 2.3214, "metro"),
    ("Tuileries", 48.8638, 2.3325, "metro"),
    ("Palais Royal Musée du Louvre", 48.8638, 2.3366, "metro"),
    ("Louvre Rivoli", 48.8604, 2.3451, "metro"),
    ("Châtelet", 48.8598, 2.3469, "metro"),
    ("Hôtel de Ville", 48.8572, 2.3514, "metro"),
    ("Saint-Paul", 48.8551, 2.3601, "metro"),
    ("Bastille", 48.8532, 2.3692, "metro"),
    ("Gare de Lyon", 48.8446, 2.3736, "metro"),
    ("Reuilly Diderot", 48.8484, 2.3894, "metro"),
    ("Nation", 48.8483, 2.3962, "metro"),
    ("Château de Vincennes", 48.8446, 2.4396, "metro"),
    # Ligne 2
    ("Porte Dauphine", 48.8717, 2.2756, "metro"),
    ("Victor Hugo", 48.8705, 2.2878, "metro"),
    ("Kléber", 48.8714, 2.2951, "metro"),
    ("Ternes", 48.8759, 2.2990, "metro"),
    ("Courcelles", 48.8793, 2.3070, "metro"),
    ("Monceau", 48.8800, 2.3140, "metro"),
    ("Villiers", 48.8824, 2.3196, "metro"),
    ("Rome", 48.8830, 2.3232, "metro"),
    ("Place de Clichy", 48.8841, 2.3282, "metro"),
    ("Blanche", 48.8840, 2.3326, "metro"),
    ("Pigalle", 48.8826, 2.3384, "metro"),
    ("Anvers", 48.8820, 2.3443, "metro"),
    ("Barbès Rochechouart", 48.8834, 2.3498, "metro"),
    ("La Chapelle", 48.8863, 2.3570, "metro"),
    ("Stalingrad", 48.8845, 2.3657, "metro"),
    ("Jaurès", 48.8829, 2.3712, "metro"),
    ("Colonel Fabien", 48.8780, 2.3728, "metro"),
    ("Belleville", 48.8720, 2.3752, "metro"),
    ("Couronnes", 48.8680, 2.3812, "metro"),
    ("Ménilmontant", 48.8662, 2.3867, "metro"),
    ("Père Lachaise", 48.8618, 2.3893, "metro"),
    ("Philippe Auguste", 48.8567, 2.3895, "metro"),
    ("Alexandre Dumas", 48.8535, 2.3958, "metro"),
    ("Avron", 48.8510, 2.4034, "metro"),
    # Ligne 3
    ("Pont de Levallois Bécon", 48.8966, 2.2851, "metro"),
    ("Anatole France", 48.8951, 2.2936, "metro"),
    ("Louise Michel", 48.8929, 2.3012, "metro"),
    ("Porte de Champerret", 48.8899, 2.3017, "metro"),
    ("Pereire", 48.8891, 2.3081, "metro"),
    ("Wagram", 48.8871, 2.3114, "metro"),
    ("Malesherbes", 48.8857, 2.3157, "metro"),
    ("Europe", 48.8798, 2.3252, "metro"),
    ("Saint-Lazare", 48.8754, 2.3245, "metro"),
    ("Havre Caumartin", 48.8736, 2.3312, "metro"),
    ("Opéra", 48.8706, 2.3318, "metro"),
    ("Quatre-Septembre", 48.8700, 2.3388, "metro"),
    ("Bourse", 48.8692, 2.3422, "metro"),
    ("Sentier", 48.8667, 2.3472, "metro"),
    ("Arts et Métiers", 48.8660, 2.3540, "metro"),
    ("Temple", 48.8641, 2.3604, "metro"),
    ("République", 48.8676, 2.3635, "metro"),
    ("Oberkampf", 48.8642, 2.3738, "metro"),
    ("Parmentier", 48.8618, 2.3796, "metro"),
    ("Rue Saint-Maur", 48.8603, 2.3805, "metro"),
    ("Gambetta", 48.8644, 2.3977, "metro"),
    ("Pelleport", 48.8679, 2.4044, "metro"),
    ("Saint-Fargeau", 48.8720, 2.4093, "metro"),
    ("Porte de Bagnolet", 48.8688, 2.4124, "metro"),
    ("Gallieni", 48.8638, 2.4183, "metro"),
    # Ligne 4
    ("Porte de Clignancourt", 48.9028, 2.3448, "metro"),
    ("Simplon", 48.8990, 2.3477, "metro"),
    ("Marcadet Poissonniers", 48.8955, 2.3492, "metro"),
    ("Château Rouge", 48.8882, 2.3494, "metro"),
    ("Gare du Nord", 48.8796, 2.3551, "metro"),
    ("Gare de l'Est", 48.8764, 2.3593, "metro"),
    ("Strasbourg Saint-Denis", 48.8668, 2.3543, "metro"),
    ("Réaumur Sébastopol", 48.8649, 2.3502, "metro"),
    ("Étienne Marcel", 48.8627, 2.3484, "metro"),
    ("Les Halles", 48.8619, 2.3475, "metro"),
    ("Cité", 48.8553, 2.3469, "metro"),
    ("Saint-Michel", 48.8530, 2.3467, "metro"),
    ("Odéon", 48.8520, 2.3407, "metro"),
    ("Saint-Germain des Prés", 48.8540, 2.3335, "metro"),
    ("Saint-Sulpice", 48.8512, 2.3310, "metro"),
    ("Saint-Placide", 48.8462, 2.3253, "metro"),
    ("Montparnasse Bienvenüe", 48.8422, 2.3215, "metro"),
    ("Alésia", 48.8284, 2.3270, "metro"),
    ("Mouton Duvernet", 48.8330, 2.3265, "metro"),
    ("Denfert-Rochereau", 48.8340, 2.3326, "metro"),
    ("Montrouge", 48.8181, 2.3213, "metro"),
    ("Bagneux", 48.7988, 2.3108, "metro"),
    # Ligne 5
    ("Bobigny Pablo Picasso", 48.9056, 2.4402, "metro"),
    ("Bobigny Pantin Raymond Queneau", 48.9009, 2.4329, "metro"),
    ("Église de Pantin", 48.8976, 2.4138, "metro"),
    ("Hoche", 48.8905, 2.4011, "metro"),
    ("Porte de Pantin", 48.8875, 2.3973, "metro"),
    ("Ourcq", 48.8847, 2.3866, "metro"),
    ("Laumière", 48.8838, 2.3773, "metro"),
    ("Jacques Bonsergent", 48.8711, 2.3638, "metro"),
    ("Richard Lenoir", 48.8589, 2.3730, "metro"),
    ("Bréguet Sabin", 48.8551, 2.3701, "metro"),
    ("Quai de la Rapée", 48.8463, 2.3680, "metro"),
    ("Bercy", 48.8403, 2.3797, "metro"),
    ("Dugommier", 48.8364, 2.3875, "metro"),
    ("Daumesnil", 48.8363, 2.3955, "metro"),
    ("Bel-Air", 48.8388, 2.4046, "metro"),
    # Ligne 6
    ("Boissière", 48.8667, 2.2938, "metro"),
    ("Trocadéro", 48.8633, 2.2877, "metro"),
    ("Passy", 48.8578, 2.2870, "metro"),
    ("Bir-Hakeim", 48.8534, 2.2895, "metro"),
    ("Dupleix", 48.8497, 2.2951, "metro"),
    ("La Motte-Picquet Grenelle", 48.8491, 2.2997, "metro"),
    ("Cambronne", 48.8467, 2.3037, "metro"),
    ("Sèvres Lecourbe", 48.8437, 2.3109, "metro"),
    ("Pasteur", 48.8419, 2.3152, "metro"),
    ("Edgar Quinet", 48.8404, 2.3259, "metro"),
    ("Raspail", 48.8383, 2.3292, "metro"),
    ("Saint-Jacques", 48.8332, 2.3377, "metro"),
    ("Glacière", 48.8290, 2.3441, "metro"),
    ("Corvisart", 48.8270, 2.3514, "metro"),
    ("Place d'Italie", 48.8308, 2.3554, "metro"),
    ("Chevaleret", 48.8306, 2.3637, "metro"),
    ("Quai de la Gare", 48.8340, 2.3692, "metro"),
    # Ligne 7
    ("La Courneuve 8 Mai 1945", 48.9281, 2.3985, "metro"),
    ("Fort d'Aubervilliers", 48.9177, 2.3941, "metro"),
    ("Aubervilliers Pantin Quatre Chemins", 48.9110, 2.3878, "metro"),
    ("Porte de la Villette", 48.8997, 2.3779, "metro"),
    ("Corentin Cariou", 48.8969, 2.3765, "metro"),
    ("Crimée", 48.8934, 2.3742, "metro"),
    ("Riquet", 48.8885, 2.3693, "metro"),
    ("Louis Blanc", 48.8806, 2.3647, "metro"),
    ("Poissonnière", 48.8742, 2.3491, "metro"),
    ("Cadet", 48.8746, 2.3454, "metro"),
    ("Le Peletier", 48.8741, 2.3422, "metro"),
    ("Chaussée d'Antin La Fayette", 48.8726, 2.3349, "metro"),
    ("Pyramides", 48.8648, 2.3360, "metro"),
    ("Pont Neuf", 48.8592, 2.3466, "metro"),
    ("Pont Marie", 48.8528, 2.3540, "metro"),
    ("Sully Morland", 48.8508, 2.3568, "metro"),
    ("Jussieu", 48.8468, 2.3554, "metro"),
    ("Place Monge", 48.8430, 2.3521, "metro"),
    ("Censier Daubenton", 48.8413, 2.3546, "metro"),
    ("Les Gobelins", 48.8367, 2.3545, "metro"),
    ("Tolbiac", 48.8245, 2.3602, "metro"),
    ("Kremlin-Bicêtre", 48.8127, 2.3589, "metro"),
    ("Villejuif Louis Aragon", 48.7940, 2.3658, "metro"),
    # Ligne 8
    ("Balard", 48.8383, 2.2788, "metro"),
    ("Lourmel", 48.8382, 2.2888, "metro"),
    ("Boucicaut", 48.8402, 2.2973, "metro"),
    ("Félix Faure", 48.8404, 2.3036, "metro"),
    ("Commerce", 48.8412, 2.3101, "metro"),
    ("École Militaire", 48.8550, 2.3063, "metro"),
    ("La Tour-Maubourg", 48.8566, 2.3124, "metro"),
    ("Invalides", 48.8615, 2.3136, "metro"),
    ("Madeleine", 48.8693, 2.3245, "metro"),
    ("Richelieu Drouot", 48.8730, 2.3396, "metro"),
    ("Grands Boulevards", 48.8721, 2.3449, "metro"),
    ("Bonne Nouvelle", 48.8694, 2.3489, "metro"),
    ("Filles du Calvaire", 48.8641, 2.3674, "metro"),
    ("Saint-Sébastien Froissart", 48.8605, 2.3689, "metro"),
    ("Chemin Vert", 48.8562, 2.3699, "metro"),
    ("Ledru-Rollin", 48.8499, 2.3769, "metro"),
    ("Faidherbe Chaligny", 48.8478, 2.3838, "metro"),
    ("Montgallet", 48.8442, 2.3929, "metro"),
    ("Michel Bizot", 48.8320, 2.3984, "metro"),
    ("Porte Dorée", 48.8284, 2.4038, "metro"),
    ("Charenton Écoles", 48.8200, 2.4085, "metro"),
    ("Liberté", 48.8168, 2.4099, "metro"),
    ("Créteil Préfecture", 48.7927, 2.4574, "metro"),
    # Ligne 9
    ("Pont de Sèvres", 48.8303, 2.2324, "metro"),
    ("Billancourt", 48.8323, 2.2447, "metro"),
    ("Marcel Sembat", 48.8349, 2.2539, "metro"),
    ("Issy", 48.8278, 2.2618, "metro"),
    ("Mairie d'Issy", 48.8258, 2.2658, "metro"),
    ("Corentin Celton", 48.8275, 2.2770, "metro"),
    ("Mirabeau", 48.8457, 2.2678, "metro"),
    ("Javel André Citroën", 48.8450, 2.2815, "metro"),
    ("Charles Michels", 48.8452, 2.2898, "metro"),
    ("Avenue Émile Zola", 48.8484, 2.2946, "metro"),
    ("Sèvres Babylone", 48.8512, 2.3191, "metro"),
    ("Saint-François Xavier", 48.8494, 2.3151, "metro"),
    ("Vaneau", 48.8488, 2.3197, "metro"),
    ("Duroc", 48.8468, 2.3180, "metro"),
    ("Volontaires", 48.8441, 2.3156, "metro"),
    ("Vaugirard", 48.8398, 2.3035, "metro"),
    ("Convention", 48.8362, 2.3023, "metro"),
    ("Exelmans", 48.8416, 2.2625, "metro"),
    ("Michel-Ange Molitor", 48.8453, 2.2597, "metro"),
    ("Michel-Ange Auteuil", 48.8481, 2.2623, "metro"),
    ("Jasmin", 48.8539, 2.2649, "metro"),
    ("Ranelagh", 48.8588, 2.2717, "metro"),
    ("La Muette", 48.8619, 2.2754, "metro"),
    ("Rue de la Pompe", 48.8668, 2.2759, "metro"),
    ("Iéna", 48.8655, 2.2929, "metro"),
    ("Alma Marceau", 48.8637, 2.3016, "metro"),
    ("Miromesnil", 48.8741, 2.3115, "metro"),
    ("Saint-Augustin", 48.8749, 2.3190, "metro"),
    ("Saint-Ambroise", 48.8601, 2.3775, "metro"),
    ("Voltaire", 48.8570, 2.3797, "metro"),
    ("Charonne", 48.8540, 2.3862, "metro"),
    ("Rue des Boulets", 48.8507, 2.3922, "metro"),
    # Ligne 10
    ("Boulogne Pont de Saint-Cloud", 48.8366, 2.2212, "metro"),
    ("Boulogne Jean Jaurès", 48.8334, 2.2307, "metro"),
    ("Porte d'Auteuil", 48.8488, 2.2553, "metro"),
    ("Chardon Lagache", 48.8476, 2.2620, "metro"),
    ("Gare d'Austerlitz", 48.8448, 2.3651, "metro"),
    ("Maubert Mutualité", 48.8508, 2.3498, "metro"),
    ("Cluny La Sorbonne", 48.8521, 2.3450, "metro"),
    ("Mabillon", 48.8527, 2.3361, "metro"),
    # Ligne 11
    ("Rambuteau", 48.8616, 2.3524, "metro"),
    ("Goncourt", 48.8712, 2.3706, "metro"),
    ("Pyrénées", 48.8754, 2.3893, "metro"),
    ("Jourdain", 48.8773, 2.3953, "metro"),
    ("Place des Fêtes", 48.8793, 2.3994, "metro"),
    ("Télégraphe", 48.8830, 2.4024, "metro"),
    ("Pré Saint-Gervais", 48.8868, 2.4044, "metro"),
    ("Mairie des Lilas", 48.8811, 2.4175, "metro"),
    # Ligne 12
    ("Aubervilliers Quatre Routes", 48.9208, 2.3782, "metro"),
    ("Mairie d'Aubervilliers", 48.9136, 2.3832, "metro"),
    ("Front Populaire", 48.9076, 2.3671, "metro"),
    ("Porte de la Chapelle", 48.8985, 2.3584, "metro"),
    ("Marx Dormoy", 48.8940, 2.3588, "metro"),
    ("Lamarck Caulaincourt", 48.8895, 2.3403, "metro"),
    ("Abbesses", 48.8843, 2.3384, "metro"),
    ("Saint-Georges", 48.8773, 2.3374, "metro"),
    ("Notre-Dame de Lorette", 48.8769, 2.3377, "metro"),
    ("Trinité d'Estienne d'Orves", 48.8780, 2.3290, "metro"),
    ("Assemblée Nationale", 48.8626, 2.3193, "metro"),
    ("Solférino", 48.8602, 2.3222, "metro"),
    ("Rue du Bac", 48.8555, 2.3270, "metro"),
    ("Rennes", 48.8487, 2.3266, "metro"),
    ("Notre-Dame des Champs", 48.8455, 2.3265, "metro"),
    ("Falguière", 48.8399, 2.3162, "metro"),
    ("Plaisance", 48.8319, 2.3150, "metro"),
    ("Pernety", 48.8353, 2.3168, "metro"),
    ("Gaîté", 48.8385, 2.3201, "metro"),
    ("Porte de Versailles", 48.8314, 2.2884, "metro"),
    ("Châtillon Montrouge", 48.8093, 2.3013, "metro"),
    # Ligne 13
    ("Saint-Denis Université", 48.9365, 2.3583, "metro"),
    ("Saint-Denis Porte de Paris", 48.9271, 2.3568, "metro"),
    ("Carrefour Pleyel", 48.9196, 2.3540, "metro"),
    ("Brochant", 48.8908, 2.3183, "metro"),
    ("Guy Môquet", 48.8932, 2.3257, "metro"),
    ("La Fourche", 48.8872, 2.3249, "metro"),
    ("Liège", 48.8800, 2.3253, "metro"),
    ("Varenne", 48.8564, 2.3147, "metro"),
    # Ligne 14
    ("Mairie de Saint-Ouen", 48.9139, 2.3381, "metro"),
    ("Porte de Clichy", 48.9001, 2.3314, "metro"),
    ("Cour Saint-Émilion", 48.8344, 2.3862, "metro"),
    ("Bibliothèque François Mitterrand", 48.8297, 2.3765, "metro"),
    ("Olympiades", 48.8248, 2.3667, "metro"),

    # ── RER ───────────────────────────────────────────────────────────────────
    # RER A
    ("Saint-Germain-en-Laye", 48.8991, 2.0930, "rer"),
    ("Poissy", 48.9283, 2.0432, "rer"),
    ("Cergy le Haut", 49.0379, 2.0621, "rer"),
    ("Nanterre Préfecture", 48.8927, 2.2102, "rer"),
    ("Nanterre Université", 48.9011, 2.2064, "rer"),
    ("Nanterre Ville", 48.8953, 2.1997, "rer"),
    ("Auber", 48.8739, 2.3327, "rer"),
    ("Châtelet Les Halles", 48.8596, 2.3471, "rer"),
    ("Vincennes", 48.8443, 2.4363, "rer"),
    ("Saint-Maur Créteil", 48.8082, 2.4817, "rer"),
    ("Marne la Vallée Chessy", 48.8744, 2.7793, "rer"),
    # RER B
    ("Aéroport CDG", 49.0053, 2.5669, "rer"),
    ("Le Bourget", 48.9314, 2.4243, "rer"),
    ("Saint-Michel Notre-Dame", 48.8529, 2.3464, "rer"),
    ("Laplace", 48.7894, 2.3349, "rer"),
    ("Bourg-la-Reine", 48.7783, 2.3148, "rer"),
    ("Robinson", 48.7742, 2.3074, "rer"),
    ("Saint-Rémy lès Chevreuse", 48.7083, 2.0736, "rer"),
    # RER C
    ("Versailles Rive Gauche", 48.8004, 2.1323, "rer"),
    ("Juvisy", 48.6878, 2.3798, "rer"),
    ("Musée d'Orsay", 48.8600, 2.3254, "rer"),
    ("Austerlitz", 48.8448, 2.3651, "rer"),
    ("Choisy le Roi", 48.7659, 2.4036, "rer"),
    # RER D
    ("Stade de France Saint-Denis", 48.9240, 2.3607, "rer"),
    ("Villeneuve Saint-Georges", 48.7340, 2.4424, "rer"),
    ("Melun", 48.5390, 2.6585, "rer"),
    # RER E
    ("Haussmann Saint-Lazare", 48.8752, 2.3263, "rer"),
    ("Magenta", 48.8793, 2.3586, "rer"),
    ("Rosa Parks", 48.8991, 2.3861, "rer"),
    ("Pantin", 48.8976, 2.4138, "rer"),
    ("Bondy", 48.9028, 2.4827, "rer"),
    ("Noisy le Sec", 48.9027, 2.4572, "rer"),

    # ── GARES SNCF ────────────────────────────────────────────────────────────
    ("Paris Gare du Nord", 48.8796, 2.3551, "gare_sncf"),
    ("Paris Gare de Lyon", 48.8446, 2.3736, "gare_sncf"),
    ("Paris Montparnasse", 48.8413, 2.3218, "gare_sncf"),
    ("Paris Gare de l'Est", 48.8764, 2.3593, "gare_sncf"),
    ("Paris Saint-Lazare", 48.8765, 2.3245, "gare_sncf"),
    ("Paris Austerlitz", 48.8448, 2.3651, "gare_sncf"),
    ("Paris Bercy", 48.8403, 2.3797, "gare_sncf"),
    ("La Défense", 48.8921, 2.2387, "gare_sncf"),
    ("Versailles Chantiers", 48.7972, 2.1278, "gare_sncf"),
    ("Versailles Rive Droite", 48.8009, 2.1372, "gare_sncf"),
    ("Saint-Denis", 48.9350, 2.3561, "gare_sncf"),
    ("Noisy-le-Grand", 48.8491, 2.5551, "gare_sncf"),
    ("Melun", 48.5390, 2.6585, "gare_sncf"),
    ("Évry Courcouronnes", 48.6240, 2.4289, "gare_sncf"),
    ("Massy TGV", 48.7273, 2.2712, "gare_sncf"),
    ("Pontoise", 49.0523, 2.1001, "gare_sncf"),
    ("Cergy Saint-Christophe", 49.0354, 2.0718, "gare_sncf"),
    ("Argenteuil", 48.9476, 2.2459, "gare_sncf"),
    ("Asnières sur Seine", 48.9162, 2.2834, "gare_sncf"),
    ("Colombes", 48.9240, 2.2519, "gare_sncf"),
    ("Boulogne Billancourt", 48.8349, 2.2407, "gare_sncf"),
    ("Issy-les-Moulineaux", 48.8240, 2.2712, "gare_sncf"),
    ("Clamart", 48.8068, 2.2539, "gare_sncf"),
    ("Viroflay", 48.8018, 2.1658, "gare_sncf"),
    ("Choisy le Roi", 48.7659, 2.4036, "gare_sncf"),
    ("Maisons-Alfort Alfortville", 48.8072, 2.4244, "gare_sncf"),
    ("Le Raincy", 48.8982, 2.5195, "gare_sncf"),
    ("Drancy", 48.9214, 2.4542, "gare_sncf"),
    ("Aéroport CDG Terminal 2", 49.0053, 2.5669, "gare_sncf"),
]

def build_stations_df():
    df_s = pd.DataFrame(STATIONS_STATIQUES, columns=["nom", "lat", "lon", "type"])
    df_s = df_s.drop_duplicates(subset=["lat", "lon"])
    print(f"✅ {len(df_s)} stations chargées "
          f"({(df_s.type=='metro').sum()} métro, "
          f"{(df_s.type=='rer').sum()} RER, "
          f"{(df_s.type=='gare_sncf').sum()} SNCF)")
    return df_s

stations = build_stations_df()

# ── 3. Haversine vectorisé ────────────────────────────────────────────────────
def haversine_vectorized(lat1, lon1, lat2_arr, lon2_arr):
    R = 6371000
    phi1, phi2 = np.radians(lat1), np.radians(lat2_arr)
    dphi       = np.radians(lat2_arr - lat1)
    dlambda    = np.radians(lon2_arr - lon1)
    a = np.sin(dphi / 2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2)**2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

# ── 4. Flags ──────────────────────────────────────────────────────────────────
metros = stations[stations["type"] == "metro"][["lat", "lon"]].values
rers   = stations[stations["type"] == "rer"][["lat", "lon"]].values
gares  = stations[stations["type"] == "gare_sncf"][["lat", "lon"]].values

RAYON = 400  # mètres

def flag_proche(lat, lon, stations_arr, rayon):
    if pd.isna(lat) or pd.isna(lon) or len(stations_arr) == 0:
        return 0
    distances = haversine_vectorized(lat, lon, stations_arr[:, 0], stations_arr[:, 1])
    return int(distances.min() <= rayon)

print("\n⏳ Calcul des distances...")
df["flag_metro"]     = df.apply(lambda r: flag_proche(r.latitude, r.longitude, metros, RAYON), axis=1)
df["flag_rer"]       = df.apply(lambda r: flag_proche(r.latitude, r.longitude, rers,   RAYON), axis=1)
df["flag_gare_sncf"] = df.apply(lambda r: flag_proche(r.latitude, r.longitude, gares,  RAYON), axis=1)
df["flag_transport"] = (
    (df["flag_metro"] == 1) | (df["flag_rer"] == 1) | (df["flag_gare_sncf"] == 1)
).astype(int)

# ── 5. Export ─────────────────────────────────────────────────────────────────
df.to_csv("airbnb_enrichi.csv", index=False)
print("\n✅ Fichier mis à jour : airbnb_enrichi.csv")
print(f"\n📊 Résumé (rayon {RAYON}m) :")
print(f"   flag_metro     : {df.flag_metro.sum()} logements ({df.flag_metro.mean()*100:.1f}%)")
print(f"   flag_rer       : {df.flag_rer.sum()} logements ({df.flag_rer.mean()*100:.1f}%)")
print(f"   flag_gare_sncf : {df.flag_gare_sncf.sum()} logements ({df.flag_gare_sncf.mean()*100:.1f}%)")
print(f"   flag_transport : {df.flag_transport.sum()} logements ({df.flag_transport.mean()*100:.1f}%)")