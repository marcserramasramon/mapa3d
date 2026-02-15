import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_referrals():
    print("Generating referral data...")
    
    hospitals = [
        "Hospital Vall d'Hebron", # Hub
        "Hospital Clínic",        # Hub
        "Hospital Sant Pau",      # Hub
        "Hospital Bellvitge",     # Semi-Hub
        "Hospital Can Ruti",      # Semi-Hub
        "Hospital Arnau de Vilanova", # Spoke (Lleida)
        "Hospital Josep Trueta"       # Spoke (Girona)
    ]
    
    # Acronym mapping for CSV
    acronyms = {
        "Hospital Vall d'Hebron": "HVD",
        "Hospital Clínic": "HC",
        "Hospital Sant Pau": "HSP",
        "Hospital Bellvitge": "HB",
        "Hospital Can Ruti": "HCR",
        "Hospital Arnau de Vilanova": "HAV",
        "Hospital Josep Trueta": "HJT"
    }
    
    # Define Roles
    hubs = ["HVD", "HC", "HSP"]
    spokes = ["HAV", "HJT", "HB", "HCR"]
    
    # Simulation Period: 7 Days
    start_time = datetime(2025, 2, 1, 0, 0, 0)
    end_time = start_time + timedelta(days=7)
    
    records = []
    current_time = start_time
    
    # Rate of events (referrals per hour)
    # Day (8-20): High. Night (20-8): Low.
    
    # Specialties
    specialties = ["Cardiologia", "Neurologia", "Oncologia", "Traumatologia", "Cremats", "Trasplantament"]
    urgencies = ["Rutina", "Urgent", "Emergencia Vital"]
    
    while current_time < end_time:
        # Determine generation rate based on hour
        hour = current_time.hour
        if 8 <= hour <= 20:
            rate_lambda = 2.0 # Avg 2 referrals per hour across network
        else:
            rate_lambda = 0.5
            
        # Poisson arrival
        inter_arrival_minutes = np.random.exponential(60 / rate_lambda)
        current_time += timedelta(minutes=inter_arrival_minutes)
        
        if current_time >= end_time:
            break
            
        # Determine Origin and Destination
        # Logic: Spokes send to Hubs mostly.
        # Hubs send to Hubs (rare, hyper-specialized).
        # Hubs send to Spokes (Repatriation/Recovery - less common in acute phase visualizations but exists).
        
        # 80% Spoke -> Hub
        # 10% Hub -> Hub
        # 10% Hub -> Spoke
        
        roll = random.random()
        
        origin = ""
        destination = ""
        
        if roll < 0.8:
            origin = random.choice(spokes)
            # Choose compatible hub (distance based preference usually, or specialty)
            # HAV (Lleida) prefers HVD or HB?
            # HJT (Girona) prefers HSP or HVD?
            # Let's randomise for web effect.
            destination = random.choice(hubs)
            
            # Special rule: HB and HCR are big, they act as Hubs sometimes too. 
            # But let's keep it simple: They send to HVD/HC/HSP for specific things.
            
        elif roll < 0.9:
            # Hub to Hub (e.g. HC -> HVD for Burns)
            origin = random.choice(hubs)
            destination = random.choice([h for h in hubs if h != origin])
            
        else:
            # Repatriation: Hub to Spoke
            origin = random.choice(hubs)
            destination = random.choice(spokes)
            
        # Urgency Profile
        # 70% Routine, 20% Urgent, 10% Emergency
        u_roll = random.random()
        if u_roll < 0.7: urgency = "Rutina"
        elif u_roll < 0.9: urgency = "Urgent"
        else: urgency = "Emergencia Vital"
        
        specialty = random.choice(specialties)
        
        records.append({
            "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Origin": origin,
            "Destination": destination,
            "Specialty": specialty,
            "Urgency": urgency
        })
        
    df = pd.DataFrame(records)
    output_path = "derivacions_pacients.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} referrals. Saved to {output_path}")

if __name__ == "__main__":
    generate_referrals()
