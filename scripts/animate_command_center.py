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

def create_command_center_animation():
    print("Loading data...")
    try:
        df = pd.read_csv("derivacions_girona_extended.csv")
    except:
        print("Data not found. Run generate_girona_referrals.py first.")
        return
        
    locs = girona_locations.locations
    
    # Filter for a window (12 hours)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    day_one = df['Timestamp'].dt.date.min()
    start_time = datetime.combine(day_one, datetime.min.time()) + timedelta(hours=8)
    end_time = start_time + timedelta(hours=14)
    df = df[(df['Timestamp'] >= start_time) & (df['Timestamp'] < end_time)]
    
    # --- SETUP GRIDSPEC LAYOUT ---
    plt.style.use('dark_background')
    
    # PALETTE "MEDIC BLUE"
    COLOR_BG = '#001020'       # Very dark blue
    COLOR_PANEL = '#002040'    # Panel Blue
    COLOR_TEXT_MAIN = '#e0f7fa' # White/Cyan
    COLOR_TEXT_DIM = '#4fc3f7'  # Light Blue
    COLOR_ACCENT = '#00e5ff'    # Bright Cyan
    COLOR_ALERT = '#ffffff'     # White for alert (or keep red?) -> Let's use Bright White for max contrast
    COLOR_GRAPH = '#0277bd'     # Medium Blue
    
    fig = plt.figure(figsize=(19, 10), facecolor=COLOR_BG)
    
    # Grid: 
    # Row 0: Timeline (Height 1)
    # Row 1: Main (Height 6) -> Split into Left (KPI), Middle (Map), Right (Details)
    # Row 2: Bottom Graphs (Height 3)
    
    gs = GridSpec(10, 12, figure=fig)
    
    # Timeline (Top)
    ax_timeline = fig.add_subplot(gs[0, :])
    ax_timeline.set_facecolor(COLOR_BG)
    
    # KPI Panel (Left)
    ax_kpi = fig.add_subplot(gs[1:7, 0:2])
    ax_kpi.axis('off')
    
    # Map (Center)
    ax_map = fig.add_subplot(gs[1:7, 2:10])
    ax_map.axis('off')
    
    # Details Panel (Right)
    ax_details = fig.add_subplot(gs[1:7, 10:])
    ax_details.axis('off')
    ax_details.set_facecolor(COLOR_PANEL)
    
    # Bottom Graphs
    ax_graph1 = fig.add_subplot(gs[7:, 0:6]) # Time Series
    ax_graph2 = fig.add_subplot(gs[7:, 6:])  # Bar Chart
    
    # --- STATIC UI ELEMENTS ---
    
    # Timeline Background Data
    df['hour_bin'] = df['Timestamp'].dt.floor('30min')
    counts = df.groupby('hour_bin').size()
    times = counts.index
    vals = counts.values
    ax_timeline.bar(times, vals, width=0.015, color=COLOR_GRAPH, edgecolor=COLOR_ACCENT, alpha=0.6)
    ax_timeline.set_xlim(start_time, end_time)
    ax_timeline.axis('off')
    time_cursor = ax_timeline.axvline(start_time, color='white', lw=2)
    
    # KPI Text
    kpi_texts = {}
    labels = ["ACTIUS", "URGENTS", "EMERG.", "LLITS"]
    y_pos = 0.9
    for lbl in labels:
        ax_kpi.text(0.1, y_pos, lbl, color=COLOR_TEXT_DIM, fontsize=10, fontweight='bold')
        val = ax_kpi.text(0.1, y_pos-0.05, "0", color=COLOR_TEXT_MAIN, fontsize=24, fontweight='bold')
        kpi_texts[lbl] = val
        y_pos -= 0.15
        
    # Details Panel
    ax_details.text(0.5, 0.95, "FITXA PACIENT", ha='center', color=COLOR_ACCENT, fontsize=12, fontweight='bold')
    patient_details = []
    labels_pat = ["ID", "NOM", "EDAT", "ORIGEN", "DESTI", "ESTAT"]
    y_start = 0.8
    for lbl in labels_pat:
        ax_details.text(0.1, y_start, lbl, color=COLOR_TEXT_DIM, fontsize=8)
        val = ax_details.text(0.1, y_start-0.03, "-", color='white', fontsize=10)
        patient_details.append(val)
        y_start -= 0.1
        
    # Graphs Initial Setup
    line_x, line_y = [], []
    line_plot, = ax_graph1.plot([], [], color=COLOR_ACCENT, lw=2)
    ax_graph1.set_title("FLUX ACUMULAT", fontsize=10, color=COLOR_TEXT_DIM)
    ax_graph1.set_facecolor(COLOR_BG)
    ax_graph1.grid(True, color='#003366', linestyle='--')
    ax_graph1.tick_params(axis='x', colors=COLOR_TEXT_DIM)
    ax_graph1.tick_params(axis='y', colors=COLOR_TEXT_DIM)
    for spine in ax_graph1.spines.values(): spine.set_edgecolor(COLOR_PANEL)
    
    bars_specialty = ax_graph2.bar([], [])
    ax_graph2.set_title("ESPECIALITAT", fontsize=10, color=COLOR_TEXT_DIM)
    ax_graph2.set_facecolor(COLOR_BG)
    ax_graph2.tick_params(axis='x', colors=COLOR_TEXT_DIM)
    ax_graph2.tick_params(axis='y', colors=COLOR_TEXT_DIM)
    for spine in ax_graph2.spines.values(): spine.set_edgecolor(COLOR_PANEL)

    # --- MAP SETUP ---
    data_list = []
    for code, data in locs.items():
        lat, lon = data['coords']
        data_list.append({ "code": code, "name": data['name'], "geometry": Point(lon, lat) })
    gdf = gpd.GeoDataFrame(data_list, crs="EPSG:4326")
    gdf_web = gdf.to_crs(epsg=3857)
    
    # Extent
    minx, miny, maxx, maxy = gdf_web.total_bounds
    buffer = 8000
    ax_map.set_xlim(minx - buffer, maxx + buffer)
    ax_map.set_ylim(miny - buffer, maxy + buffer)
    
    # Nodes (Blue Theme)
    for idx, row in gdf_web.iterrows():
        size = 50; color = '#0288d1' # Light Blue
        if "Hospital" in row['name']: size = 150; color = '#01579b' # Deep Blue
        if row['code'] == 'HJT': size = 300; color = '#e1f5fe' # White/Ice
        ax_map.scatter(row.geometry.x, row.geometry.y, s=size, c=color, edgecolors='white', zorder=2)
        if "Hospital" in row['name']:
            ax_map.text(row.geometry.x, row.geometry.y + 1500, row['code'], ha='center', fontsize=8, color=COLOR_TEXT_MAIN, fontweight='bold')

    try:
        # Voyager is nicer for blue theme than DarkMatter sometimes, but let's stick to DarkMatter for contrast
        cx.add_basemap(ax_map, crs=gdf_web.crs.to_string(), source=cx.providers.CartoDB.DarkMatterNoLabels)
    except: pass

    # --- PARTICLES ---
    node_coords = {row['code']: (row.geometry.x, row.geometry.y) for idx, row in gdf_web.iterrows()}
    
    fps = 20
    sim_duration = 12
    pause_sec = 4
    base_frames = fps * sim_duration
    pause_frames = fps * pause_sec
    total_frames = base_frames + pause_frames
    
    sim_seconds_total = (end_time - start_time).total_seconds()
    
    particles = []
    candidates = []
    selection_trigger = int(base_frames * 0.6)
    
    for idx, row in df.iterrows():
        orig = row['Origin']
        dest = row['Destination']
        ts = row['Timestamp']
        if orig not in node_coords or dest not in node_coords: continue
        
        start_ratio = (ts - start_time).total_seconds() / sim_seconds_total
        if not (0 <= start_ratio <= 1): continue
        
        trip_len = 0.08
        start_f = int(start_ratio * base_frames)
        end_f = int((start_ratio + trip_len) * base_frames)
        
        path = np.linspace(np.array(node_coords[orig]), np.array(node_coords[dest]), max(2, end_f - start_f))
        
        # Colors: White for Emergency, Cyan for Urgent, Medium Blue for Routine
        p_color = '#4fc3f7' # Routine
        if row['Urgency'] == 'Urgent': p_color = '#00e5ff' # High Cyan
        if row['Urgency'] == 'Emergencia': p_color = '#ffffff' # White hot
        
        p = {
            "id": row['Patient_ID'],
            "name": row['Name'],
            "age": row['Age'],
            "ori": row['Origin'],
            "dst": row['Destination'],
            "urgency": row['Urgency'],
            "specialty": row['Specialty'],
            "path": path,
            "start": start_f,
            "end": end_f,
            "color": p_color
        }
        particles.append(p)
        if start_f < selection_trigger < end_f:
            candidates.append(p)
            
    target = candidates[0] if candidates else (particles[0] if particles else None)
    
    scat = ax_map.scatter([], [], s=60, zorder=5)
    highlight = patches.Circle((0,0), radius=3000, fill=False, color=COLOR_ACCENT, lw=2, visible=False)
    ax_map.add_patch(highlight)
    
    def update(frame):
        # Time logic
        is_paused = False
        logical_frame = frame
        if frame >= selection_trigger:
            if frame < selection_trigger + pause_frames:
                is_paused = True
                logical_frame = selection_trigger
            else:
                logical_frame = frame - pause_frames
        if logical_frame >= base_frames: logical_frame = base_frames - 1
        
        # Cursor
        curr_ratio = logical_frame / base_frames
        curr_time = start_time + timedelta(seconds=curr_ratio * sim_seconds_total)
        time_cursor.set_xdata([curr_time])
        
        # Particles
        px, py, pc = [], [], []
        target_pos = None
        current_active = []
        
        for p in particles:
            if p['start'] <= logical_frame < p['end']:
                current_active.append(p)
                idx = logical_frame - p['start']
                if idx < len(p['path']):
                    pos = p['path'][idx]
                    color = p['color']
                    if p is target and is_paused: 
                        target_pos = pos
                        color = COLOR_ACCENT
                    px.append(pos[0])
                    py.append(pos[1])
                    pc.append(color)
                    
        if px:
            scat.set_offsets(np.c_[px, py])
            scat.set_color(pc)
        else:
            scat.set_offsets(np.empty((0, 2)))
            
        # KPIs
        count_active = len(current_active)
        count_urgent = sum(1 for p in current_active if p['urgency'] in ['Urgent', 'Emergencia'])
        count_emerg = sum(1 for p in current_active if p['urgency'] == 'Emergencia')
        
        kpi_texts["ACTIUS"].set_text(str(count_active))
        kpi_texts["URGENTS"].set_text(str(count_urgent))
        kpi_texts["EMERG."].set_text(str(count_emerg))
        kpi_texts["LLITS"].set_text(f"{min(100, int(count_active*1.5))}%")
        
        # Detail Panel
        if is_paused and target:
            highlight.set_center(target_pos); highlight.set_visible(True)
            vals = [target['id'], target['name'], str(target['age']), target['ori'], target['dst'], target['urgency']]
            for i, txt in enumerate(patient_details):
                txt.set_text(vals[i])
                if i == 5: txt.set_color(COLOR_ACCENT) # Highlight Status
        else:
            highlight.set_visible(False)
            for txt in patient_details: txt.set_text("-")
            
        if not is_paused:
            line_x.append(curr_time)
            line_y.append(count_active)
            line_plot.set_data(line_x, line_y)
            ax_graph1.set_xlim(start_time, end_time)
            ax_graph1.set_ylim(0, max(20, max(line_y) if line_y else 0))
            
            s_counts = pd.Series([p['specialty'] for p in current_active]).value_counts()
            if not s_counts.empty:
                ax_graph2.clear()
                ax_graph2.bar(s_counts.index, s_counts.values, color='#0277bd', width=0.6)
                ax_graph2.set_title("ESPECIALITAT", fontsize=10, color=COLOR_TEXT_DIM)
                ax_graph2.tick_params(axis='x', labelsize=8, rotation=45, colors=COLOR_TEXT_DIM)
                ax_graph2.tick_params(axis='y', colors=COLOR_TEXT_DIM)
                ax_graph2.set_facecolor(COLOR_BG)
                for spine in ax_graph2.spines.values(): spine.set_edgecolor(COLOR_PANEL)

    ani = FuncAnimation(fig, update, frames=total_frames, interval=1000/fps)
    out = "command_center.gif"
    ani.save(out, writer=PillowWriter(fps=fps))
    print(f"Saved {out}")

if __name__ == "__main__":
    create_command_center_animation()
