import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from datetime import datetime, timedelta
import girona_locations
import geopandas as gpd
from shapely.geometry import Point
import contextily as cx

def create_girona_animation():
    print("Loading data...")
    try:
        df = pd.read_csv("derivacions_girona.csv")
    except:
        print("Data not found.")
        return
        
    locs = girona_locations.locations
    
    # Filter for 24h
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    start_time = df['Timestamp'].min()
    end_time = start_time + timedelta(hours=24)
    df = df[df['Timestamp'] < end_time]
    
    # --- GEOSPATIAL SETUP ---
    print("Setting up Map...")
    
    # Create GeoDataFrame for Nodes
    data_list = []
    for code, data in locs.items():
        lat, lon = data['coords']
        data_list.append({
            "code": code, 
            "name": data['name'], 
            "role": data.get('role', 'CAP'),
            "geometry": Point(lon, lat) # Lon, Lat for Point
        })
        
    gdf = gpd.GeoDataFrame(data_list, crs="EPSG:4326")
    
    # Reproject to Web Mercator (EPSG:3857) for Contextily
    gdf_web = gdf.to_crs(epsg=3857)
    
    # Setup Figure
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.axis('off')
    
    # Plot Static Nodes
    # Hubs Red, Comarcals Orange, CAPs Blue
    for idx, row in gdf_web.iterrows():
        size = 50
        color = 'blue'
        zorder = 2
        name = row['name']
        role = row['role']
        code = row['code']
        
        if "Hospital" in name:
            size = 150
            color = 'orange'
            if role == 'Reference Hub': # Trueta
                size = 300
                color = 'red'
                zorder = 3
        
        ax.scatter(row.geometry.x, row.geometry.y, s=size, c=color, edgecolors='white', zorder=zorder)
        # Offset label slightly
        ax.text(row.geometry.x, row.geometry.y + 500, code, ha='center', fontsize=8, fontweight='bold', zorder=zorder+1)

    # Add Basemap
    # CartoDB.Positron is clean/white style.
    try:
        cx.add_basemap(ax, crs=gdf_web.crs.to_string(), source=cx.providers.CartoDB.Positron)
    except Exception as e:
        print(f"Error fetching tiles: {e}")
        # Fallback to just plot?
        pass

    # --- ANIMATION ---
    print(f"Animating {len(df)} referrals...")
    
    # Pre-calculate projected coordinates for quick access
    # Create a mapping code -> (x, y) in 3857
    node_coords = {}
    for idx, row in gdf_web.iterrows():
        node_coords[row['code']] = (row.geometry.x, row.geometry.y)
        
    fps = 20
    duration_sec = 10
    total_frames = fps * duration_sec
    sim_duration = (end_time - start_time).total_seconds()
    time_per_frame = sim_duration / total_frames
    
    particles = []
    for idx, row in df.iterrows():
        orig = row['Origin']
        dest = row['Destination']
        ts = row['Timestamp']
        urgency = row['Urgency']
        
        if orig not in node_coords or dest not in node_coords: continue
        
        p0 = np.array(node_coords[orig])
        p1 = np.array(node_coords[dest])
        
        start_sec = (ts - start_time).total_seconds()
        start_frame = int(start_sec / time_per_frame)
        
        steps = 30
        if urgency == "Urgent": steps = 20
        if urgency == "Emergencia": steps = 10
        end_frame = start_frame + steps
        
        path = np.linspace(p0, p1, steps)
        color = 'green' # Standard
        if urgency == "Urgent": color = 'orange' # Contextily map is light, yellow might be hard to see. Orange/Gold better.
        if urgency == "Emergencia": color = 'red'
        
        particles.append({
            "start": start_frame,
            "end": end_frame,
            "path": path,
            "color": color
        })
        
    scat = ax.scatter([], [], s=40, zorder=4)
    t_text = ax.text(0.05, 0.95, "", transform=ax.transAxes, fontsize=12, fontweight='bold')
    
    def update(frame):
        curr_time = start_time + timedelta(seconds=frame*time_per_frame)
        t_text.set_text(f"{curr_time.strftime('%Y-%m-%d %H:%M')}")
        
        px, py, pc = [], [], []
        for p in particles:
            if p['start'] <= frame < p['end']:
                idx = frame - p['start']
                if idx < len(p['path']):
                    pos = p['path'][idx]
                    px.append(pos[0])
                    py.append(pos[1])
                    pc.append(p['color'])
        
        if px:
            scat.set_offsets(np.c_[px, py])
            scat.set_color(pc)
        else:
            scat.set_offsets(np.empty((0, 2)))
            
    ani = FuncAnimation(fig, update, frames=total_frames, interval=100)
    out = "flux_girona.gif"
    ani.save(out, writer=PillowWriter(fps=fps))
    print(f"Saved {out}")

if __name__ == "__main__":
    create_girona_animation()
