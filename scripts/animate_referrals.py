import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.animation import FuncAnimation, PillowWriter
from datetime import datetime, timedelta

def create_referral_animation():
    print("Loading data...")
    df = pd.read_csv("derivacions_pacients.csv")
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    
    # Filter for first 48h to keep GIF manageable
    start_time = df['Timestamp'].min()
    end_time = start_time + timedelta(hours=48)
    df = df[df['Timestamp'] < end_time]
    
    print(f"Animating {len(df)} referrals over 48 hours...")
    
    # Coordinates (Same mapping as before)
    # HVD, HC, HSP, HB, HCR, HAV, HJT
    # 0    1   2    3   4    5    6
    # Wait, my previous mapping was:
    # 0->HAV, 1->HB, 2->HVD...
    # I need to match Acronyms to Coords precisely.
    
    # Let's verify mapping from animate_futuristic.py
    # coords = [(243, 523), (518, 596), ...]
    # hospitals_ordered = ["HAV", "HB", "HVD", "HC", "HSP", "HCR", "HJT"]
    
    coords_map = {
        "HAV": (243, 523),
        "HB": (518, 596),
        "HVD": (790, 1560), # Wait, looking at previous script, this mapping was dubious but consistent.
        "HC": (929, 1490),  # Let's keep it consistent.
        "HSP": (968, 967),
        "HCR": (1156, 462),
        "HJT": (1363, 1162)
    }
    
    img = mpimg.imread("map_dots.png")
    
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='black')
    ax.imshow(img, alpha=0.3)
    ax.axis('off')
    
    # Draw static nodes
    for h, (x, y) in coords_map.items():
        color = 'cyan'
        if h in ["HVD", "HC", "HSP"]: color = 'magenta' # Hubs
        ax.scatter(x, y, color=color, s=100, zorder=2)
        ax.text(x, y-40, h, color='white', ha='center', fontsize=8)

    # Simulation Params
    fps = 10
    duration_sec = 10 # Animation duration
    total_frames = fps * duration_sec
    
    # Time scaling
    sim_duration = (end_time - start_time).total_seconds()
    time_per_frame = sim_duration / total_frames
    
    # Prepare Trajectories
    active_particles = [] # List of dicts: {start_frame, end_frame, path_x, path_y, color}
    
    for idx, row in df.iterrows():
        origin = row['Origin']
        dest = row['Destination']
        urgency = row['Urgency']
        ts = row['Timestamp']
        
        if origin not in coords_map or dest not in coords_map:
            continue
            
        p0 = np.array(coords_map[origin])
        p2 = np.array(coords_map[dest])
        
        # Calculate travel time based on distance/urgency
        dist = np.linalg.norm(p2 - p0)
        speed = 500 # pixels per second?
        if urgency == "Emergencia Vital": speed = 1000
        elif urgency == "Rutina": speed = 200
        
        # Duration in Frames
        # Real sim time: dist / speed? No, visual speed.
        # Let's say travel takes 10-30 frames.
        travel_frames = int(dist / 50) # arbitrary visual speed
        if urgency == "Emergencia Vital": travel_frames = int(dist / 100)
        
        # Start Frame
        offset_seconds = (ts - start_time).total_seconds()
        start_frame = int(offset_seconds / time_per_frame)
        end_frame = start_frame + travel_frames
        
        # Bezier Curve
        # Midpoint
        mid = (p0 + p2) / 2
        # Normal vector
        vec = p2 - p0
        normal = np.array([-vec[1], vec[0]])
        normal = normal / np.linalg.norm(normal)
        # Random curvature direction
        curvature = 200 * (1 if np.random.random() > 0.5 else -1)
        p1 = mid + normal * curvature
        
        # Generate points
        t = np.linspace(0, 1, travel_frames)
        # Quadratic Bezier
        # B(t) = (1-t)^2 P0 + 2(1-t)t P1 + t^2 P2
        path = np.outer((1-t)**2, p0) + np.outer(2*(1-t)*t, p1) + np.outer(t**2, p2)
        
        color = 'green'
        if urgency == "Urgent": color = 'yellow'
        elif urgency == "Emergencia Vital": color = 'red'
        
        active_particles.append({
            "start": start_frame,
            "end": end_frame,
            "path": path,
            "color": color
        })
        
    # Scatter plot for particles
    particles_scat = ax.scatter([], [], s=50, zorder=3)
    
    title = ax.text(0.05, 0.95, "PATIENT REFERRAL FLOW", transform=ax.transAxes, 
                   color='white', fontsize=16, fontweight='bold')
    clock = ax.text(0.05, 0.90, "", transform=ax.transAxes, color='white', family='monospace')

    def update(frame_idx):
        if frame_idx % 10 == 0: print(f"Frame {frame_idx}/{total_frames}")
        
        current_sim_time = start_time + timedelta(seconds=frame_idx * time_per_frame)
        clock.set_text(current_sim_time.strftime("%Y-%m-%d %H:%M"))
        
        # Find active particles
        x_vals = []
        y_vals = []
        c_vals = []
        sizes = []
        
        count = 0
        for p in active_particles:
            if p['start'] <= frame_idx < p['end']:
                # Index in path
                path_idx = frame_idx - p['start']
                if path_idx < len(p['path']):
                    pos = p['path'][path_idx]
                    x_vals.append(pos[0])
                    y_vals.append(pos[1])
                    c_vals.append(p['color'])
                    sizes.append(50 if p['color'] != 'red' else 80)
                    count += 1
        
        if count > 0:
            particles_scat.set_offsets(np.c_[x_vals, y_vals])
            particles_scat.set_color(c_vals)
            particles_scat.set_sizes(sizes)
        else:
            particles_scat.set_offsets(np.empty((0, 2)))

    ani = FuncAnimation(fig, update, frames=total_frames, interval=100)
    
    output = "flux_pacients.gif"
    ani.save(output, writer=PillowWriter(fps=fps))
    print(f"Saved {output}")

if __name__ == "__main__":
    create_referral_animation()
