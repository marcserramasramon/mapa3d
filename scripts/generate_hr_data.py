import pandas as pd
import numpy as np
import random

def generate_hr_data():
    # Hospitals in Girona Health Region (plus main hubs for reference if needed, but let's focus on Girona network)
    # Using the same coordinates/codes as previous maps for consistency
    locations = {
        "HJT": "Hospital Josep Trueta",
        "HSC": "Hospital Santa Caterina",
        "HOL": "Hospital d'Olot",
        "HCF": "Hospital de Campdevànol",
        "HP": "Hospital de Palamós",
        "HBF": "Hospital de Blanes",
        "HCS": "Hospital de la Selva", 
        "ABS_Girona": "CAP Girona",
        "ABS_Salt": "CAP Salt",
        "ABS_Banyoles": "CAP Banyoles"
    }
    
    # 1. Staff Distribution
    records_dist = []
    categories = ["Metges", "Infermeres", "Administratius", "Altres"]
    
    for code, name in locations.items():
        # Base size depends on hospital type
        if code == "HJT": base = 2500 # Big Hub
        elif code in ["HSC", "HP"]: base = 1000 # Medium
        elif "ABS" in code: base = 100 # Primary Care
        else: base = 400 # Small/Medium
        
        total_staff = int(np.random.normal(base, base*0.1))
        
        # approximate ratios
        ratios = [0.25, 0.40, 0.15, 0.20] 
        counts = np.random.multinomial(total_staff, ratios)
        
        for cat, count in zip(categories, counts):
            records_dist.append({
                "Hospital_Code": code,
                "Hospital_Name": name,
                "Categoria": cat,
                "Personal": count
            })
            
    df_dist = pd.DataFrame(records_dist)
    df_dist.to_csv("recursos_humans_distribucio.csv", index=False)
    print("Saved recursos_humans_distribucio.csv")

    # 2. Collaborations / Rotations (Edges)
    records_collab = []
    
    # Define some likely flows
    # Hub -> Spoke (Specialists visiting)
    # Spoke -> Hub (Training/Referrals)
    
    hospitals = list(locations.keys())
    
    for _ in range(30): # 30 random links
        orig = random.choice(hospitals)
        dest = random.choice(hospitals)
        
        if orig == dest: continue
        
        # Logic: More likely to collaborate if one is HJT (Trueta)
        if "HJT" not in [orig, dest] and random.random() > 0.3: continue
        
        # Types of collaboration
        types = ["Guàrdies Compartides", "Rotació Residents", "Suport Especialista", "Formació"]
        type_collab = random.choice(types)
        
        staff_moving = np.random.randint(1, 10)
        
        records_collab.append({
            "Origen": orig,
            "Desti": dest,
            "Tipus": type_collab,
            "Personal_Movil": staff_moving
        })

    df_collab = pd.DataFrame(records_collab)
    # Aggregate if same link exists
    df_collab = df_collab.groupby(['Origen', 'Desti', 'Tipus']).sum().reset_index()
    
    df_collab.to_csv("recursos_humans_colaboracions.csv", index=False)
    print("Saved recursos_humans_colaboracions.csv")

if __name__ == "__main__":
    generate_hr_data()
