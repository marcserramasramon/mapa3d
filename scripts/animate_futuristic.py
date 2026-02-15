import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.patheffects as path_effects
from datetime import datetime

def create_futuristic_animation():
    # Load Data
    print("Loading data...")
    df = pd.read_csv("infeccions_nocosmials_wide.csv")
    dates = sorted(df["Data"].unique())
    
    # Coordinates (West -> East)
    coords = [
        (243, 523),   # HAV
        (518, 596),   # HB
        (790, 1560),  # HVD
        (929, 1490),  # HC
        (968, 967),   # HSP
        (1156, 462),  # HCR (Wait, check order again?)
        (1363, 1162)  # HJT
    ]
    # Let's trust the previous mapping for consistency or refine it
    # Coordinates used in animate_infections.py were:
    # 0: HAV, 1: HB, 2: HVD...
    # Let's stick to the same index-to-hospital mapping
    hospitals_ordered = ["HAV", "HB", "HVD", "HC", "HSP", "HCR", "HJT"]

    # Setup Figure with Dark Background
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 10), facecolor='black')
    
    # Load Map implies standard map. 
    # For futuristic look, we can process the map to be "wireframe" or dark.
    # Or just ignore map and use grid? No, user wants map.
    # We'll plot map with low opacity or tint it cyan.
    img = mpimg.imread("map_dots.png")
    # Tint map: make it grayscale then cyan
    # Simple way: plot it with alpha and distinctive cmap if it was single channel
    # It's likely RGB. Let's just plot it dark.
    ax.imshow(img, alpha=0.3) 
    ax.axis('off')
    
    # Draw Connectivity Lines (Mesh/Network effect)
    # Connect every node to 2 nearest neighbors? Or just a web?
    # Let's draw lines between all hospitals to simulate a network, with low alpha
    for i in range(len(coords)):
        for j in range(i + 1, len(coords)):
            p1 = coords[i]
            p2 = coords[j]
            # Distance check to avoid messy full mesh?
            dist = np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
            if dist < 800: # Connect nearby cities
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#00FFFF', alpha=0.1, linewidth=1, zorder=0)

    # Scatters for nodes (to be updated)
    # Start with empty
    scat = ax.scatter([], [], s=[], c=[], cmap='cool', alpha=0.8, edgecolors='white', zorder=2)
    # Glow effect scatter (larger, lower alpha)
    scat_glow = ax.scatter([], [], s=[], c=[], cmap='cool', alpha=0.3, zorder=1)
    
    # Text labels
    labels = []
    for i, (x, y) in enumerate(coords):
        # Acronym label
        t = ax.text(x, y - 40, hospitals_ordered[i], color='white', fontsize=10, ha='center', fontweight='bold')
        t.set_path_effects([path_effects.withStroke(linewidth=2, foreground='black')])
        labels.append(t)
        
        # Count label (will update)
        t_val = ax.text(x, y, "0", color='#00FFFF', fontsize=12, ha='center', va='center', fontweight='bold')
        t_val.set_path_effects([path_effects.withStroke(linewidth=3, foreground='black')])
        labels.append(t_val) # We'll need to update these separate from acronyms?
                             # Better storage structure needed.

    # Store reference to value texts
    value_texts = [labels[i*2+1] for i in range(len(coords))]

    # HUD Elements
    # Title
    title_text = ax.text(0.05, 0.95, "BIOSURVEILLANCE//SYSTEM", transform=ax.transAxes, 
                        color='#00FF00', fontsize=20, fontweight='bold', ha='left')
    date_text = ax.text(0.05, 0.90, "DATE: 2025-01-01", transform=ax.transAxes,
                       color='white', fontsize=14, ha='left', family='monospace')
    
    total_text = ax.text(0.95, 0.95, "TOTAL CASES: 0", transform=ax.transAxes,
                        color='#FF00FF', fontsize=18, fontweight='bold', ha='right')
    
    # Grid lines overlay for "HUD" feel
    ax.vlines(np.linspace(0, img.shape[1], 10), 0, img.shape[0], color='green', alpha=0.05)
    ax.hlines(np.linspace(0, img.shape[0], 10), 0, img.shape[1], color='green', alpha=0.05)
    
    # Bar chart at bottom (timeline)
    # Implementation complexity: animating a line graph inside the same figure
    # We can use inset axes at bottom
    ax_timeline = ax.inset_axes([0.1, 0.05, 0.8, 0.15])
    ax_timeline.set_facecolor('#001100')
    ax_timeline.tick_params(axis='x', colors='white')
    ax_timeline.tick_params(axis='y', colors='white')
    # Pre-calculate total timeline
    timeline_totals = []
    for d in dates:
        day_df = df[df["Data"] == d]
        # Sum all hospital cols
        # Need to be careful about format.
        # Wide format: HAV, HB...
        # Just sum the columns that are hospitals
        cols = [c for c in df.columns if c in hospitals_ordered]
        daily_sum = day_df[cols].sum().sum()
        timeline_totals.append(daily_sum)
    
    timeline_x = np.arange(len(dates))
    line, = ax_timeline.plot([], [], color='#00FF00', linewidth=2)
    ax_timeline.set_xlim(0, len(dates))
    ax_timeline.set_ylim(0, max(timeline_totals)*1.2)
    ax_timeline.set_title("TEMPORAL PROGRESSION", color='white', fontsize=8)

    def update(frame_idx):
        date = dates[frame_idx]
        current_total = timeline_totals[frame_idx]
        
        # Update HUD
        date_text.set_text(f"DATE: {date} | T-{frame_idx:02d}")
        total_text.set_text(f"ACTV CASES: {int(current_total)}")
        
        # Update Timeline
        line.set_data(timeline_x[:frame_idx+1], timeline_totals[:frame_idx+1])
        
        # Update Nodes
        day_df = df[df["Data"] == date]
        
        sizes = []
        colors = []
        
        for i, hosp in enumerate(hospitals_ordered):
            if hosp in day_df.columns:
                # Sum for this hospital on this day
                # day_df might have multiple rows (age groups), we need sum
                val = day_df[hosp].sum()
                
                # Update text
                value_texts[i].set_text(str(int(val)))
                
                # Size bubble
                # Base size 100 + val*10
                s = 200 + val * 20
                sizes.append(s)
                
                # Color based on intensity
                # Normal: Cyan -> Warning: Magenta -> Critical: Red
                if val > 30:
                    colors.append('#FF0000') # Red
                elif val > 15:
                    colors.append('#FF00FF') # Magenta
                else:
                    colors.append('#00FFFF') # Cyan
        
        # Update scatter
        offsets = np.array(coords)
        scat.set_offsets(offsets)
        scat.set_sizes(sizes)
        scat.set_color(colors)
        
        scat_glow.set_offsets(offsets)
        scat_glow.set_sizes([s*2 for s in sizes]) # Larger glow
        scat_glow.set_color(colors)
        
        # Warning flash?
        if current_total > 150: # Arbitrary global threshold
            ax.set_facecolor('#110000') # Red tint bg
        else:
            ax.set_facecolor('black')

    print("Rendering futuristic animation...")
    ani = FuncAnimation(fig, update, frames=len(dates), interval=150)
    
    output = "infeccions_futurista.gif"
    ani.save(output, writer=PillowWriter(fps=8))
    print(f"Saved {output}")

if __name__ == "__main__":
    create_futuristic_animation()
