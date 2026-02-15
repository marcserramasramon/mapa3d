import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_data():
    # Configuration
    hospitals = [
        "Hospital Vall d'Hebron",
        "Hospital Clínic",
        "Hospital Sant Pau",
        "Hospital Bellvitge",
        "Hospital Can Ruti",
        "Hospital Arnau de Vilanova",
        "Hospital Josep Trueta"
    ]
    
    age_groups = ["0-14", "15-44", "45-64", "65+"]
    genders = ["Dona", "Home"]
    
    start_date = datetime(2025, 1, 1)
    num_days = 60
    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    
    # Simulation Parameters
    # Base infection rate per hospital (simulating size differences)
    base_rates = {h: np.random.uniform(5, 15) for h in hospitals}
    
    # Contagion Wave: A peak that moves across hospitals (simulating spread between cities)
    # We'll assign an index to hospitals to simulate "distance" or order of spread
    hospital_order = {h: i for i, h in enumerate(hospitals)}
    wave_speed = 3  # Days to move to next hospital
    wave_peak_day_start = 10 # First hospital hits peak at day 10
    wave_intensity = 20 # Max additional cases during outbreak
    wave_width = 5 # Standard deviation of the Gaussian outbreak
    
    # Cyclical Factor: Weekly cycle (higher on weekdays, lower on weekends for reporting?) 
    # Or biological cycle? Let's assume a 7-day reporting cycle.
    
    records = []
    
    for day_idx, date in enumerate(dates):
        # 7-day cycle (simulating reporting or staffing patterns)
        # sin wave oscillating between 0.8 and 1.2
        cycle_factor = 1 + 0.2 * np.sin(day_idx * (2 * np.pi / 7))
        
        for hospital in hospitals:
            h_idx = hospital_order[hospital]
            
            # Contagion Wave Calculation
            # Gaussian function: A * exp(-(x - delay)^2 / (2*sigma^2))
            peak_day = wave_peak_day_start + (h_idx * wave_speed)
            contagion_factor = wave_intensity * np.exp(-((day_idx - peak_day)**2) / (2 * wave_width**2))
            
            # Base cases for this hospital
            daily_base = base_rates[hospital]
            
            # Total expected cases for this hospital on this day
            lambda_val = (daily_base * cycle_factor) + contagion_factor
            
            # Ensure non-negative
            lambda_val = max(0, lambda_val)
            
            # Poisson variation for realistic counts
            total_cases = np.random.poisson(lambda_val)
            
            # Distribute cases among age/gender groups
            # We'll distribute them forcefully to ensure the sum matches total_cases
            # using random choice with weights
            
            if total_cases > 0:
                # Weights for demographics (e.g., older people more susceptible)
                # Age weights: 0-14: 0.1, 15-44: 0.2, 45-64: 0.3, 65+: 0.4
                age_weights = [0.1, 0.2, 0.3, 0.4]
                gender_weights = [0.5, 0.5] # Assume equal split
                
                # Combine weights
                combinations = []
                combo_weights = []
                for i, age in enumerate(age_groups):
                    for j, gender in enumerate(genders):
                        combinations.append((age, gender))
                        combo_weights.append(age_weights[i] * gender_weights[j])
                
                # Normalize weights
                combo_weights = np.array(combo_weights)
                combo_weights /= combo_weights.sum()
                
                # Distribute cases
                distributions = np.random.multinomial(total_cases, combo_weights)
                
                for (age, gender), count in zip(combinations, distributions):
                    if count > 0:
                        records.append({
                            "Data": date.strftime("%Y-%m-%d"),
                            "Hospital": hospital,
                            "Grup_Edat": age,
                            "Genere": gender,
                            "Infeccions": count
                        })
            else:
                 # Add at least one zero record or skip? 
                 # Usually datasets might have 0s. Let's add 0s for all groups if we want a complete grid,
                 # but for "infections", sparse might be better. 
                 # Request says "table of values", implies a grid or list of incidents.
                 # Let's produce a list of non-zero daily aggregates to keep it clean, 
                 # or a full grid if they want to analyze 0s.
                 # Let's Generate a full grid (all combos) with local noise to ensure data density
                 pass

    # Re-generating with a Full Grid approach per day/hospital/age/gender is often better for analysis
    records_grid = []
    for day_idx, date in enumerate(dates):
        cycle_factor = 1 + 0.2 * np.sin(day_idx * (2 * np.pi / 7))
        
        for hospital in hospitals:
            h_idx = hospital_order[hospital]
            peak_day = wave_peak_day_start + (h_idx * wave_speed)
            contagion_factor = wave_intensity * np.exp(-((day_idx - peak_day)**2) / (2 * wave_width**2))
            
            daily_base = base_rates[hospital]
            lambda_val_total = (daily_base * cycle_factor) + contagion_factor
            lambda_val_total = max(0.1, lambda_val_total) # Avoid true 0 for rates
            
            for age in age_groups:
                # Age specific weighting
                age_mod = 1.0
                if age == "0-14": age_mod = 0.5
                elif age == "65+": age_mod = 2.0
                
                for gender in genders:
                    # Gender specific weighting (slight random per hospital?)
                    gender_mod = 1.0
                    
                    # Calculate group lambda
                    # Divide total lambda roughly by 8 groups (4 ages * 2 genders) but weighted
                    group_lambda = (lambda_val_total / 8) * age_mod * gender_mod
                    
                    cases = np.random.poisson(group_lambda)
                    
                    records_grid.append({
                        "Data": date.strftime("%Y-%m-%d"),
                        "Hospital": hospital,
                        "Acronim": "".join([word[0] for word in hospital.split() if len(word)>2]).upper(),
                        "Grup_Edat": age,
                        "Genere": gender,
                        "Infeccions": cases,
                        # Add some metadata for "cycle" and "contagion_risk" for visualization fun
                        "Risc_Contagi_Calc": round(contagion_factor, 2)
                    })
                    
    df = pd.DataFrame(records_grid)
    
    # Pivot to have Hospitals (Acronyms) as columns
    # Preserving Data, Grup_Edat, Genere as row identifiers
    pivot_df = df.pivot_table(
        index=['Data', 'Grup_Edat', 'Genere'], 
        columns='Acronim', 
        values='Infeccions', 
        fill_value=0
    ).reset_index()
    
    # Sort key columns just in case
    pivot_df = pivot_df.sort_values(['Data', 'Grup_Edat', 'Genere'])
    
    return pivot_df

if __name__ == "__main__":
    print("Generating infection data...")
    df = generate_data()
    output_path = "infeccions_nocosmials_wide.csv"
    df.to_csv(output_path, index=False)
    print(f"Data generated: {len(df)} rows.")
    print(f"Saved to {output_path}")
    print(df.head())
