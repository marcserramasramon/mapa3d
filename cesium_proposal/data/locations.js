export const hospitals = {
    "HJT": { "name": "Hospital Univ. Dr. Josep Trueta", "coords": [2.8242, 41.9964], "role": "Reference Hub", "patients": 450, "capacity": 600 },
    "HSC": { "name": "Hospital Santa Caterina (Salt)", "coords": [2.7800, 41.9680], "role": "Cluster Hub", "patients": 200, "capacity": 300 },
    "HF": { "name": "Hospital de Figueres", "coords": [2.9560, 42.2665], "role": "Comarcal", "patients": 150, "capacity": 250 },
    "HP": { "name": "Hospital de Palamós", "coords": [3.1280, 41.8500], "role": "Comarcal", "patients": 120, "capacity": 200 },
    "HO": { "name": "Hospital d'Olot i Comarcal", "coords": [2.4770, 42.1890], "role": "Comarcal", "patients": 100, "capacity": 180 },
    "HB": { "name": "Hospital de Blanes", "coords": [2.7830, 41.6780], "role": "Comarcal", "patients": 130, "capacity": 220 },
    "HCAR": { "name": "Hospital de Campdevànol", "coords": [2.1690, 42.2280], "role": "Comarcal", "patients": 80, "capacity": 150 }
};

export const caps = {
    "CAP_Girona_Guell": { "name": "CAP Güell (Girona)", "coords": [2.8150, 41.9780], "parent": "HJT", "patients": 45, "capacity": 80 },
    "CAP_Girona_CanGibert": { "name": "CAP Can Gibert del Pla", "coords": [2.8080, 41.9720], "parent": "HSC", "patients": 30, "capacity": 60 },
    "CAP_Salt": { "name": "CAP Salt", "coords": [2.7850, 41.9700], "parent": "HSC", "patients": 40, "capacity": 70 },
    "CAP_Figueres": { "name": "CAP Ernest Lluch (Figueres)", "coords": [2.9650, 42.2690], "parent": "HF", "patients": 50, "capacity": 90 },
    "CAP_Roses": { "name": "CAP Roses", "coords": [3.1790, 42.2630], "parent": "HF", "patients": 25, "capacity": 50 },
    "CAP_Escala": { "name": "CAP L'Escala", "coords": [3.1310, 42.1190], "parent": "HF", "patients": 20, "capacity": 40 },
    "CAP_Palamos": { "name": "CAP Palamós", "coords": [3.1300, 41.8520], "parent": "HP", "patients": 35, "capacity": 60 },
    "CAP_Palafrugell": { "name": "CAP Palafrugell", "coords": [3.1650, 41.9126], "parent": "HP", "patients": 28, "capacity": 55 },
    "CAP_Bisbal": { "name": "CAP La Bisbal", "coords": [3.0300, 41.9600], "parent": "HP", "patients": 22, "capacity": 45 },
    "CAP_Olot": { "name": "CAP Garrotxa", "coords": [2.4900, 42.1810], "parent": "HO", "patients": 32, "capacity": 65 },
    "CAP_Besalu": { "name": "CAP Besalú", "coords": [2.7000, 42.1990], "parent": "HO", "patients": 15, "capacity": 30 },
    "CAP_Blanes": { "name": "CAP Blanes", "coords": [2.7900, 41.6740], "parent": "HB", "patients": 38, "capacity": 75 },
    "CAP_Lloret": { "name": "CAP Lloret de Mar", "coords": [2.8400, 41.7000], "parent": "HB", "patients": 42, "capacity": 80 },
    "CAP_Ripoll": { "name": "CAP Ripoll", "coords": [2.1900, 42.2000], "parent": "HCAR", "patients": 18, "capacity": 35 },
    "CAP_Banyoles": { "name": "CAP Banyoles", "coords": [2.7660, 42.1180], "parent": "HJT", "patients": 27, "capacity": 55 }
};
