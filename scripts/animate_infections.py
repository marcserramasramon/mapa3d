import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.animation import FuncAnimation, PillowWriter

def create_animation():
    # Load Data
    print("Loading data...")
    df = pd.read_csv("infeccions_nocosmials_wide.csv")
    dates = sorted(df["Data"].unique())
    
    # Load Image
    print("Loading map...")
    img = mpimg.imread("map_dots.png")
    
    # Coordinates from detect_hospitals.py (Sorted by X)
    # Mapping assumed: West -> East assignment
    coords = [
        (243, 523),   # Hospital 1 (West-most) -> HAV
        (518, 596),   # Hospital 2
        (790, 1560),  # Hospital 3
        (929, 1490),  # Hospital 4
        (968, 967),   # Hospital 5
        (1156, 462),  # Hospital 6 -> HJT (North East)
        (1363, 1162)  # Hospital 7 (East-most)
    ]
    
    # Hospitals in approximate W->E order based on their location
    # HAV (Lleida), HB (Hosp), HVD (BCN), HC (BCN), HSP (BCN), HCR (Badalona), HJT (Girona)
    # Adjust this list to match the mapping you desire
    hospitals_ordered = ["HAV", "HB", "HVD", "HC", "HSP", "HCR", "HJT"]
    
    # Setup Figure
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(img)
    ax.axis('off')
    
    # Title
    title = ax.text(0.5, 1.02, "", transform=ax.transAxes, ha="center", fontsize=16, fontweight='bold')
    
    # Create Inset Axes for each hospital
    insets = []
    # Size of pie charts
    pie_size = 60 
    
    for i, (x, y) in enumerate(coords):
        # Convert pixel (x, y) to display coords is tricky in generic matplotlib without knowing DPI/fig size relation precisely
        # But inset_axes works with transform=ax.transData to place it at data coords!
        # width/height in data coords? 
        # For imshow, data coords are pixels.
        # inset_axes([x, y, w, h], transform=ax.transData) -> x,y is bottom-left?
        # We want center at x,y.
        w, h = pie_size*2, pie_size*2
        sub_ax = ax.inset_axes([x - w/2, y - h/2, w, h], transform=ax.transData)
        sub_ax.axis('off')
        insets.append(sub_ax)
        
    # Pre-calculate colors for age groups
    age_groups = sorted(df["Grup_Edat"].unique())
    colors = plt.cm.viridis(np.linspace(0, 1, len(age_groups)))
    
    def update(frame_date):
        day_df = df[df["Data"] == frame_date]
        title.set_text(f"Infeccions Nosocomials - Data: {frame_date}")
        
        for i, hosp_code in enumerate(hospitals_ordered):
            # Aggregate by Age Group
            if hosp_code in day_df.columns:
                # Group by Age and sum infections
                # day_df has multiple rows used for age/gender breakdowns
                # We need to sum the column 'hosp_code' grouping by 'Grup_Edat'
                # But day_df is already the wide format?
                # No, day_df has columns [Data, Grup_Edat, Genere, HAV, HB...]
                # So we select relevant cols
                
                group_data = day_df.groupby("Grup_Edat")[hosp_code].sum()
                
                total_infections = group_data.sum()
                
                sub_ax = insets[i]
                sub_ax.clear()
                
                # Dynamic Radius roughly based on total infections?
                # Or fixed radius pie chart?
                # Let's do fixed pie, with a label of total count.
                
                if total_infections > 0:
                    sub_ax.pie(group_data, colors=colors, startangle=90)
                    # Add Count in center
                    sub_ax.text(0, 0, str(int(total_infections)), ha='center', va='center', 
                               fontweight='bold', color='white', 
                               bbox=dict(facecolor='black', alpha=0.5, boxstyle='round,pad=0.2'))
                else:
                    # Draw empty placeholder?
                    sub_ax.text(0, 0, "0", ha='center', va='center', fontsize=8, color='black')

    print("Creating animation (this may take a minute)...")
    ani = FuncAnimation(fig, update, frames=dates, interval=200) # 200ms per day
    
    output_file = "infeccions_mapa_animat.gif"
    print(f"Saving to {output_file}...")
    ani.save(output_file, writer=PillowWriter(fps=5))
    print("Done!")

if __name__ == "__main__":
    create_animation()
