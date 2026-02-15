import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, PillowWriter
from datetime import datetime, timedelta
import girona_locations
import geopandas as gpd
from shapely.geometry import Point
import contextily as cx
from matplotlib.gridspec import GridSpec

def create_dashboard_animation():
    print("Loading data...")
    try:
        df = pd.read_csv("derivacions_girona_extended.csv")
    except:
        print("Data not found. Run generate_girona_referrals.py first.")
        return
        
    locs = girona_locations.locations
    
    # Filter for a busy window
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    day_one = df['Timestamp'].dt.date.min()
    start_time = datetime.combine(day_one, datetime.min.time()) + timedelta(hours=8)
    end_time = start_time + timedelta(hours=14)
    df = df[(df['Timestamp'] >= start_time) & (df['Timestamp'] < end_time)]
    
    # --- SETUP FIGURE WITH GRIDSPEC ---
    # Width ratio: 3:1 (Map : Sidebar)
    fig = plt.figure(figsize=(16, 9), facecolor='#2b2b2b')
    gs = GridSpec(1, 4, figure=fig)
    
    # AX1: Map
    ax_map = fig.add_subplot(gs[0, 0:3])
    ax_map.axis('off')
    
    # AX2: Sidebar
    ax_side = fig.add_subplot(gs[0, 3])
    ax_side.set_facecolor('#1e1e1e')
    ax_side.axis('off') # We'll draw text manually
    
    # --- GEOSPATIAL MAP SETUP ---
    print("Setting up Map...")
    data_list = []
    for code, data in locs.items():
        lat, lon = data['coords']
        data_list.append({
            "code": code, 
            "name": data['name'], 
            "geometry": Point(lon, lat)
        })
    gdf = gpd.GeoDataFrame(data_list, crs="EPSG:4326")
    gdf_web = gdf.to_crs(epsg=3857)
    
    # Extent
    minx, miny, maxx, maxy = gdf_web.total_bounds
    buffer = 10000 
    ax_map.set_xlim(minx - buffer, maxx + buffer)
    ax_map.set_ylim(miny - buffer, maxy + buffer)
    
    # Static Nodes
    for idx, row in gdf_web.iterrows():
        size = 60
        color = 'skyblue'
        zorder = 2
        if "Hospital" in row['name']: size = 180; color = 'orange'
        if row['code'] == 'HJT': size = 350; color = 'red'
        ax_map.scatter(row.geometry.x, row.geometry.y, s=size, c=color, edgecolors='white', zorder=zorder)
        if "Hospital" in row['name']:
             ax_map.text(row.geometry.x, row.geometry.y + 1800, row['code'], ha='center', fontsize=9, fontweight='bold', color='white', zorder=zorder+1)

    try:
        cx.add_basemap(ax_map, crs=gdf_web.crs.to_string(), source=cx.providers.CartoDB.DarkMatterNoLabels, alpha=1.0)
    except:
        ax_map.set_facecolor('#2b2b2b')

    # --- SIDEBAR SETUP ---
    # Static Text
    ax_side.text(0.5, 0.95, "CENTRE DE CONTROL", ha='center', va='top', fontsize=16, color='#00ced1', fontweight='bold')
    ax_side.text(0.5, 0.92, "REGIO SANITARIA GIRONA", ha='center', va='top', fontsize=10, color='#aaaaaa')
    
    # Dynamic Stats Placeholders
    text_time = ax_side.text(0.5, 0.85, "", ha='center', fontsize=14, color='white', fontweight='bold')
    text_active = ax_side.text(0.1, 0.78, "", ha='left', fontsize=12, color='#cccccc')
    
    divider = patches.Rectangle((0, 0.72), 1, 0.005, color='#444444')
    ax_side.add_patch(divider)
    
    # Patient Panel Placeholders
    panel_title = ax_side.text(0.5, 0.68, "FITXA PACIENT", ha='center', fontsize=14, color='#ffa500', fontweight='bold', visible=False)
    
    # We will use a list of text objects for details to easily update/hide
    detail_texts = []
    labels = ["ID PACIENT:", "NOM:", "EDAT/SEXE:", "PATOLOGIA:", "ORIGEN:", "DESTI:", "PRIORITAT:"]
    start_y = 0.60
    gap = 0.06
    
    for i, label in enumerate(labels):
        lbl = ax_side.text(0.05, start_y - (i*gap), label, ha='left', fontsize=8, color='#888888', visible=False)
        val = ax_side.text(0.05, start_y - (i*gap) - 0.025, "", ha='left', fontsize=11, color='white', visible=False)
        detail_texts.append((lbl, val))

    # --- ANIMATION PREP ---
    node_coords = {row['code']: (row.geometry.x, row.geometry.y) for idx, row in gdf_web.iterrows()}
    
    fps = 20
    sim_duration_sec = 10
    pause_sec = 4
    base_frames = fps * sim_duration_sec
    pause_frames = fps * pause_sec
    total_frames = base_frames + pause_frames
    
    sim_delta_total = (end_time - start_time).total_seconds()
    particles = []
    candidates = []
    
    selection_trigger_frame = int(base_frames * 0.5)
    
    for idx, row in df.iterrows():
        orig = row['Origin']
        dest = row['Destination']
        ts = row['Timestamp']
        
        if orig not in node_coords or dest not in node_coords: continue
        
        p0 = np.array(node_coords[orig])
        p1 = np.array(node_coords[dest])
        
        start_sec = (ts - start_time).total_seconds()
        start_ratio = start_sec / sim_delta_total
        trip_duration_ratio = 0.08 
        end_ratio = start_ratio + trip_duration_ratio
        
        start_f = int(start_ratio * base_frames)
        end_f = int(end_ratio * base_frames)
        
        if start_f >= base_frames: continue
        
        path = np.linspace(p0, p1, max(2, end_f - start_f))
        
        p_data = {
            "id": row['Patient_ID'],
            "name": row['Name'],
            "age": row['Age'],
            "gender": row['Gender'],
            "pathology": row['Pathology'],
            "urgency": row['Urgency'],
            "ori": row['Origin'],
            "dst": row['Destination'],
            "start_frame": start_f,
            "end_frame": end_f,
            "path": path,
            "color": '#ff4444' if row['Urgency'] == 'Emergencia' else '#ffd700' if row['Urgency'] == 'Urgent' else '#32cd32'
        }
        particles.append(p_data)
        
        if start_f < selection_trigger_frame < end_f:
            candidates.append(p_data)
            
    if not candidates:
        target_patient = particles[0] if particles else None
    else:
        urgents = [p for p in candidates if p['urgency'] in ['Urgent', 'Emergencia']]
        target_patient = urgents[0] if urgents else candidates[0]
        
    print(f"Target: {target_patient['name']}")
    
    scat = ax_map.scatter([], [], s=80, zorder=5, edgecolors='black')
    
    # Highlight
    highlight_circle = patches.Circle((0,0), radius=3000, fill=False, color='#00ced1', lw=3, zorder=6, visible=False)
    ax_map.add_patch(highlight_circle)

    def update(frame):
        is_paused = False
        logical_frame = frame
        
        if frame >= selection_trigger_frame:
            if frame < selection_trigger_frame + pause_frames:
                is_paused = True
                logical_frame = selection_trigger_frame
            else:
                logical_frame = frame - pause_frames
                
        if logical_frame >= base_frames: logical_frame = base_frames - 1
        
        # Calculate Current Sim Time
        curr_sim_ratio = logical_frame / base_frames
        curr_time = start_time + timedelta(seconds=curr_sim_ratio * sim_delta_total)
        text_time.set_text(curr_time.strftime("%H:%M:%S"))
        
        # Particles
        px, py, pc = [], [], []
        target_pos = None
        active_count = 0
        
        for p in particles:
            if p['start_frame'] <= logical_frame < p['end_frame']:
                active_count += 1
                idx = logical_frame - p['start_frame']
                if idx < len(p['path']):
                    pos = p['path'][idx]
                    color = p['color']
                    
                    if p is target_patient:
                        target_pos = pos
                        if is_paused: color = '#00ced1' # Cyan highlight
                    
                    px.append(pos[0])
                    py.append(pos[1])
                    pc.append(color)
                    
        if px:
            scat.set_offsets(np.c_[px, py])
            scat.set_color(pc)
        else:
            scat.set_offsets(np.empty((0, 2)))
            
        text_active.set_text(f"TRANSITS ACTIUS: {active_count}")
            
        # UI Sidebar Logic
        if is_paused and target_pos is not None:
            highlight_circle.set_center(target_pos)
            highlight_circle.set_visible(True)
            
            # Show Panel
            panel_title.set_visible(True)
            
            # Update Details
            vals = [
                target_patient['id'],
                target_patient['name'],
                f"{target_patient['age']} / {target_patient['gender']}",
                target_patient['pathology'],
                target_patient['ori'], # Could use full name locs[code]['name'] but code fits dashboard better
                target_patient['dst'],
                target_patient['urgency'].upper()
            ]
            
            for i, (lbl, val_obj) in enumerate(detail_texts):
                lbl.set_visible(True)
                val_obj.set_text(vals[i])
                val_obj.set_visible(True)
                # Color code priority
                if i == 6: # Priority
                    val_obj.set_color(target_patient['color'])
                    
        else:
            highlight_circle.set_visible(False)
            panel_title.set_visible(False)
            for lbl, val_obj in detail_texts:
                lbl.set_visible(False)
                val_obj.set_visible(False)
            
    ani = FuncAnimation(fig, update, frames=total_frames, interval=1000/fps)
    out = "flux_dashboard.gif"
    ani.save(out, writer=PillowWriter(fps=fps))
    print(f"Dashboard animation saved to {out}")

if __name__ == "__main__":
    create_dashboard_animation()
