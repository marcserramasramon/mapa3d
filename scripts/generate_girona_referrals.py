import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import girona_locations

def generate_girona_referrals():
    print("Generating Girona referral data...")
    
    locs = girona_locations.locations
    
    # Identify roles
    hospitals = {k:v for k,v in locs.items() if "Hospital" in v['name']}
    caps = {k:v for k,v in locs.items() if "CAP" in v['name']}
    
    # Simulation Period: 7 Days
    start_time = datetime(2025, 2, 1, 0, 0, 0)
    end_time = start_time + timedelta(days=7)
    
    records = []
    current_time = start_time
    
    # Rate: Higher because more nodes (CAPs generate a lot of traffic)
    # Day rate: 10 per hour?
    
    specialties = ["General", "Pediatria", "Gine", "Trauma", "Cardio", "Digestiu"]
    urgencies = ["Rutina", "Urgent", "Emergencia"]
    
    while current_time < end_time:
        hour = current_time.hour
        rate_lambda = 5.0 if 8 <= hour <= 20 else 1.0
            
        inter_arrival_minutes = np.random.exponential(60 / rate_lambda)
        current_time += timedelta(minutes=inter_arrival_minutes)
        if current_time >= end_time: break
            
        # Logic 1: CAP -> Assigned Hospital (Most common)
        # Logic 2: Hospital -> Hub (Trueta HJT) (Complex)
        # Logic 3: Any -> Any (Rare)
        
        roll = random.random()
        origin = ""
        destination = ""
        
        if roll < 0.8:
            # CAP -> Parent Hospital
            # Pick a random CAP
            cap_code, cap_data = random.choice(list(caps.items()))
            origin = cap_code
            destination = cap_data.get('parent', 'HJT') # Default to Trueta if no parent
            
        elif roll < 0.95:
            # Comarcal Hospital -> Hub (Trueta)
            # Pick a hospital that is NOT Trueta
            comarcals = [h for h in hospitals if h != "HJT"]
            origin = random.choice(comarcals)
            destination = "HJT" # All roads lead to Trueta
            
        else:
            # Hub -> Comarcal (Return)
            origin = "HJT"
            comarcals = [h for h in hospitals if h != "HJT"]
            destination = random.choice(comarcals)

        urgency = "Rutina"
        u_roll = random.random()
        if u_roll > 0.8: urgency = "Urgent"
        if u_roll > 0.98: urgency = "Emergencia"
        
        # Patient Identity
        patient_id = f"PAC-{random.randint(1000, 9999)}"
        age = random.randint(0, 95)
        gender = random.choice(["Home", "Dona"])
        
        # Simple Name Generator
        first_names = ["Jordi", "Maria", "Joan", "Anna", "Pere", "Laura", "Marc", "Cristina", "Josep", "Marta", "Albert", "Nuria"]
        last_names = ["Garcia", "Martine", "Lopez", "Sanchez", "Rodriguez", "Fernandez", "Perez", "Gomez", "Ruiz", "Hernandez"]
        name = f"{random.choice(first_names)} {random.choice(last_names)}"

        # Pathologies per specialty
        pathologies = {
            "General": ["Febre sense focus", "Malestar general", "Dolor abdominal inespecífic"],
            "Pediatria": ["Bronquiolitis", "Otitis", "Gastroenteritis", "Asma"],
            "Gine": ["Control gestació", "Metrorràgia", "Dolor pèlvic"],
            "Trauma": ["Fractura de radi", "Esquinç de turmell", "Contusió costal", "Fractura de fèmur"],
            "Cardio": ["Insuficiència cardíaca", "Arítmia", "Dolor toràcic", "Angina"],
            "Digestiu": ["Còlic biliar", "Hemorràgia digestiva", "Pancreatitis"]
        }
        
        specialty = random.choice(specialties)
        pathology = random.choice(pathologies.get(specialty, ["Altres"]))

        records.append({
            "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Patient_ID": patient_id,
            "Name": name,
            "Age": age,
            "Gender": gender,
            "Origin": origin,
            "Destination": destination,
            "Urgency": urgency,
            "Specialty": specialty,
            "Pathology": pathology
        })
        
    df = pd.DataFrame(records)
    output_path = "derivacions_girona_extended.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} referrals with patient data. Saved to {output_path}")

if __name__ == "__main__":
    generate_girona_referrals()
