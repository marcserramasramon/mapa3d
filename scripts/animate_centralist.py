import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.animation import FuncAnimation, PillowWriter
from datetime import datetime, timedelta

def create_centralist_animation():
    print("Loading data...")
    try:
        df = pd.read_csv("derivacions_pacients.csv")
    except:
        print("Data not found. Run generate_referrals.py first.")
        return
        
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Filter for first 24h to keep it focused and fast
    start_time = df['Timestamp'].min()
    end_time = start_time + timedelta(hours=24)
    df = df[df['Timestamp'] < end_time]
    
    print(f"Animating {len(df)} referrals over 24 hours...")
    
    # Coords from generate_interactive_map.py (Real GPS approximated to map_dots.png pixel space?)
    # Wait, previous scripts used pixel coords for map_dots.png.
    # Interactive map used GPS.
    # I must use PIXEL COORDS for the GIF if I use `map_dots.png` as background.
    # I'll stick to the Pixel Coords from `animate_referrals.py`.
    
    pixel_coords = {
        "HAV": (243, 523),
        "HB": (518, 596),
        "HVD": (790, 1560),
        "HC": (929, 1490),
        "HSP": (968, 967),
        "HCR": (1156, 462),
        "HJT": (1363, 1162)
    }
    
    # Load Map
    img = mpimg.imread("map_dots.png")
    
    # Setup Figure (White Background)
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')
    ax.imshow(img, alpha=0.15) # Very faint map
    ax.axis('off')
    
    # Simulation Params
    fps = 15
    duration_sec = 10 
    total_frames = fps * duration_sec
    sim_duration = (end_time - start_time).total_seconds()
    time_per_frame = sim_duration / total_frames
    
    # Pre-calculate particles
    particles = []
    
    for idx, row in df.iterrows():
        origin = row['Origin']
        dest = row['Destination']
        urgency = row['Urgency']
        ts = row['Timestamp']
        
        if origin not in pixel_coords or dest not in pixel_coords: continue
        
        p0 = np.array(pixel_coords[origin])
        p1 = np.array(pixel_coords[dest])
        
        # Distance & Speed
        dist = np.linalg.norm(p1 - p0)
        # Visual speed: pixels per frame?
        # Let's say travel takes ~1 sec (15 frames) for average.
        steps = 15
        if dist > 800: steps = 25
        if urgency == "Emergencia Vital": steps = int(steps / 2)
        
        # Start Frame
        start_seconds = (ts - start_time).total_seconds()
        start_frame = int(start_seconds / time_per_frame)
        end_frame = start_frame + steps
        
        # Linear path (Centralist flow is usually direct)
        path = np.linspace(p0, p1, steps)
        
        color = 'black' # Standard
        if urgency == "Urgent": color = 'orange'
        if urgency == "Emergencia Vital": color = 'red'
        
        particles.append({
            "start": start_frame,
            "end": end_frame,
            "path": path,
            "color": color,
            "dest": dest
        })

    # Nodes
    # We need to update node sizes.
    # Algorithm: calculate "Active Inbound" for every frame for every node.
    node_sizes_per_frame = {h: np.zeros(total_frames) for h in pixel_coords}
    base_size = 100
    
    # Populate sizes
    for p in particles:
        # While particle is moving, Destination "anticipates" or Origin "sends"?
        # User said: "segons el nombre de pacients".
        # Let's count Accumulative Arrivals (Pressure) with decay?
        # Or just "Active transfers targeting this node".
        d = p['dest']
        if d in node_sizes_per_frame:
            # Increase size during the transfer duration
            s = p['start']
            e = p['end']
            # Add +20 to size for each incoming patient
            if s < total_frames:
                limit = min(e, total_frames)
                node_sizes_per_frame[d][s:limit] += 50 
                
    # Scatter objects
    scat_nodes = ax.scatter([], [], s=[], c=[], zorder=2, edgecolors='black')
    scat_particles = ax.scatter([], [], s=30, zorder=3)
    
    # Labels
    for h, (x, y) in pixel_coords.items():
        ax.text(x, y - 50, h, ha='center', fontsize=10, fontweight='bold', color='#333333')

    # Title
    t_date = ax.text(0.05, 0.95, "", transform=ax.transAxes, fontsize=14, color='black')

    def update(frame):
        # Time
        curr_time = start_time + timedelta(seconds=frame*time_per_frame)
        t_date.set_text(f"Simulation: {curr_time.strftime('%H:%M')}")
        
        # Update Nodes
        node_x = []
        node_y = []
        node_s = []
        node_c = []
        
        for h, (x, y) in pixel_coords.items():
            node_x.append(x)
            node_y.append(y)
            # Size
            added = node_sizes_per_frame[h][frame]
            s = base_size + added
            node_s.append(s)
            # Color: Hubs (HVD, HC, HSP) distinct?
            if h in ["HVD", "HC", "HSP"]:
                node_c.append('#FF5733') # Red-ish for Hubs
            else:
                node_c.append('#33AABB') # Blue-ish for Spokes
                
        scat_nodes.set_offsets(np.c_[node_x, node_y])
        scat_nodes.set_sizes(node_s)
        scat_nodes.set_color(node_c)
        
        # Update Particles
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
            scat_particles.set_offsets(np.c_[px, py])
            scat_particles.set_color(pc)
        else:
            scat_particles.set_offsets(np.empty((0, 2)))

    ani = FuncAnimation(fig, update, frames=total_frames, interval=100)
    out = "flux_centralista.gif"
    ani.save(out, writer=PillowWriter(fps=fps))
    print(f"Saved {out}")

if __name__ == "__main__":
    create_centralist_animation()
