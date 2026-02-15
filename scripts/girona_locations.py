# Coordinates for Girona Health Region
# Hospitals
hospitals = {
    "HJT": {"name": "Hospital Univ. Dr. Josep Trueta", "coords": [41.9964, 2.8242], "role": "Reference Hub"},
    "HSC": {"name": "Hospital Santa Caterina (Salt)", "coords": [41.9680, 2.7800], "role": "Cluster Hub"},
    "HF":  {"name": "Hospital de Figueres", "coords": [42.2665, 2.9560], "role": "Comarcal"},
    "HP":  {"name": "Hospital de Palamós", "coords": [41.8500, 3.1280], "role": "Comarcal"},
    "HO":  {"name": "Hospital d'Olot i Comarcal", "coords": [42.1890, 2.4770], "role": "Comarcal"},
    "HB":  {"name": "Hospital de Blanes", "coords": [41.6780, 2.7830], "role": "Comarcal"},
    "HCAR": {"name": "Hospital de Campdevànol", "coords": [42.2280, 2.1690], "role": "Comarcal"}
}

# Primary Care Centers (CAP) - Selection
caps = {
    "CAP_Girona_Guell": {"name": "CAP Güell (Girona)", "coords": [41.9780, 2.8150], "parent": "HJT"},
    "CAP_Girona_CanGibert": {"name": "CAP Can Gibert del Pla", "coords": [41.9720, 2.8080], "parent": "HSC"},
    "CAP_Salt": {"name": "CAP Salt", "coords": [41.9700, 2.7850], "parent": "HSC"},
    "CAP_Figueres": {"name": "CAP Ernest Lluch (Figueres)", "coords": [42.2690, 2.9650], "parent": "HF"},
    "CAP_Roses": {"name": "CAP Roses", "coords": [42.2630, 3.1790], "parent": "HF"},
    "CAP_Escala": {"name": "CAP L'Escala", "coords": [42.1190, 3.1310], "parent": "HF"}, # Or Palamós? Baix Emporda border.
    "CAP_Palamos": {"name": "CAP Palamós", "coords": [41.8520, 3.1300], "parent": "HP"},
    "CAP_Palafrugell": {"name": "CAP Palafrugell", "coords": [41.9126, 3.1650], "parent": "HP"},
    "CAP_Bisbal": {"name": "CAP La Bisbal", "coords": [41.9600, 3.0300], "parent": "HP"},
    "CAP_Olot": {"name": "CAP Garrotxa", "coords": [42.1810, 2.4900], "parent": "HO"},
    "CAP_Besalu": {"name": "CAP Besalú", "coords": [42.1990, 2.7000], "parent": "HO"}, 
    "CAP_Blanes": {"name": "CAP Blanes", "coords": [41.6740, 2.7900], "parent": "HB"},
    "CAP_Lloret": {"name": "CAP Lloret de Mar", "coords": [41.7000, 2.8400], "parent": "HB"},
    "CAP_Ripoll": {"name": "CAP Ripoll", "coords": [42.2000, 2.1900], "parent": "HCAR"},
    "CAP_Banyoles": {"name": "CAP Banyoles", "coords": [42.1180, 2.7660], "parent": "HJT"}, 
}

# Combine
locations = {**hospitals, **caps}
