import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.animation import FuncAnimation, PillowWriter
from scipy.interpolate import griddata

def create_heatmap_animation():
    print("Loading data...")
    df = pd.read_csv("infeccions_nocosmials_wide.csv")
    dates = sorted(df["Data"].unique())
    
    print("Loading map...")
    img = mpimg.imread("map_dots.png")
    height, width, _ = img.shape
    
    # Coordinates (West -> East) - Same as before
    coords = [
        (243, 523),   # HAV
        (518, 596),   # HB
        (790, 1560),  # HVD
        (929, 1490),  # HC
        (968, 967),   # HSP
        (1156, 462),  # HCR 
        (1363, 1162)  # HJT
    ]
    hospitals_ordered = ["HAV", "HB", "HVD", "HC", "HSP", "HCR", "HJT"]
    
    # Points for interpolation
    points = np.array(coords)
    
    # Grid for interpolation
    # Reduce resolution for speed, then extent to image size
    grid_x, grid_y = np.mgrid[0:width:100j, 0:height:100j]
    
    # Setup Figure
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')
    
    # Background Image
    # Plot map faint
    ax.imshow(img, alpha=0.3)
    
    # Prepare Heatmap Imshow object
    # Initialize with zeros
    # extent=[0, width, height, 0] because vertically flipped usually in images?
    # mpl imshow: origin='upper' by default. extent=(left, right, bottom, top)
    # image coords: (0,0) top left. 
    # So extent should be (0, width, height, 0) to match image coords?
    # Let's test standard imshow defaults.
    
    # Placeholders
    heatmap_img = ax.imshow(np.zeros((100, 100)), extent=(0, width, height, 0), 
                           origin='upper', cmap='YlOrRd', alpha=0.6, vmin=0, vmax=50) # Adjust vmax
    
    # Scatter points to show locations
    ax.scatter(points[:,0], points[:,1], c='black', s=20, alpha=0.5)
    
    # Date Text
    title = ax.text(0.05, 0.95, "", transform=ax.transAxes, fontsize=16, fontweight='bold', color='black')

    def update(frame_idx):
        date = dates[frame_idx]
        title.set_text(f"Infections Heatmap: {date}")
        
        day_df = df[df["Data"] == date]
        
        values = []
        for h in hospitals_ordered:
            if h in day_df.columns:
                val = day_df[h].sum()
                values.append(val)
            else:
                values.append(0)
        
        values = np.array(values)
        
        # Interpolate
        # 'linear' creates triangles, 'cubic' smooth but might overshoot, 'nearest' voronoi.
        # RBF (Radial Basis Function) usually better for smooth "heat". 
        # But griddata 'cubic' is okay if points are well distributed. 
        # Since points are few (7), interpolation might be weird.
        # Let's try 'linear' for robustness or 'cubic' for smooth.
        # Issues with cubic on few points: can be unstable.
        
        # Let's use simple RBF approximation via griddata is hard. 
        # Using griddata(..., method='linear').
        # To make it cover "tot el territori" (whole territory), we need edge points with 0?
        # Otherwise interpolation is only within the convex hull of points!
        # Fix: Add dummy boundary points with 0 value?
        # Or use 'nearest' to extrapolate? nearest looks blocky.
        # Use simple distance-based weighting (IDW) manually? 
        # Or RBFInterpolator from scipy.interpolate?
        # Let's stick to griddata(method='linear') naturally limits to hull.
        # If user wants "whole territory", convex hull is probably Catalonia.
        
        try:
            grid_z = griddata(points, values, (grid_x, grid_y), method='linear', fill_value=0)
            # Smooth it?
            # grid_z might have nans outside hull if fill_value is nan. 
            # fill_value=0 makes outside hull 0.
            
            # Need to transpose grid_z for imshow?
            # grid_x shape (100, 100). grid_z shape (100, 100).
            # imshow expects (Rows, Cols). 
            # grid_y varies along axis 1? 
            # mgrid[0:w, 0:h] -> x varies along axis 0?
            # Usually: X, Y = meshgrid.
            # mgrid returns Z, Y, X order?
            # Let's just swap axes if needed.
            
            heatmap_img.set_data(grid_z.T) 
            
            # Determine max for scaling color dynamically? Or fixed?
            # heatmap_img.set_clim(vmin=0, vmax=max(values)*1.2) # Dynamic
        except Exception as e:
            print(f"Interpolation error: {e}")

    print("Rendering heatmap animation...")
    ani = FuncAnimation(fig, update, frames=len(dates), interval=150)
    
    output = "infeccions_calor.gif"
    ani.save(output, writer=PillowWriter(fps=8))
    print(f"Saved {output}")

if __name__ == "__main__":
    create_heatmap_animation()
