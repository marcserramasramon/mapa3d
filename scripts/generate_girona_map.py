import pandas as pd
import folium
import girona_locations

def generate_girona_map():
    print("Loading data...")
    try:
        df = pd.read_csv("derivacions_girona.csv")
    except:
        print("Data not found.")
        return
        
    locs = girona_locations.locations
    
    # Calculate Center
    latitudes = [v['coords'][0] for v in locs.values()]
    longitudes = [v['coords'][1] for v in locs.values()]
    center_lat = sum(latitudes) / len(latitudes)
    center_lon = sum(longitudes) / len(longitudes)
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10, tiles='CartoDB dark_matter')
    
    # Flow Volumes
    node_stats = {code: {"in": 0, "out": 0} for code in locs}
    flows = df.groupby(['Origin', 'Destination']).size().reset_index(name='count')
    max_flow = flows['count'].max()

    # Draw Lines
    for _, row in flows.iterrows():
        orig = row['Origin']
        dest = row['Destination']
        count = row['count']
        
        if orig in node_stats: node_stats[orig]["out"] += count
        if dest in node_stats: node_stats[dest]["in"] += count
        
        if orig in locs and dest in locs:
            p1 = locs[orig]['coords']
            p2 = locs[dest]['coords']
            
            # Logic: CAP -> Hospital (Blue/Green), Hospital -> Hub (Red)
            color = "#3388ff"
            role_dest = locs[dest].get('role', '') # Hospital roles
            if role_dest == "Reference Hub": color = "red" # Getting sent to Trueta
            elif "Hospital" in locs[dest]['name']: color = "orange" # Sent to Comarcal
            
            weight = 1 + (count / max_flow) * 5
            
            folium.PolyLine([p1, p2], color=color, weight=weight, opacity=0.5,
                           tooltip=f"{orig}->{dest}: {count}").add_to(m)

    # Draw Markers
    for code, data in locs.items():
        stats = node_stats[code]
        total = stats["in"] + stats["out"]
        
        color = 'blue' # CAP defaults
        if "Hospital" in data['name']: 
            if data.get('role') == "Reference Hub": color = 'red'
            else: color = 'orange'
            
        radius = 3 + (total * 0.2)
        
        popup_txt = f"<b>{data['name']}</b><br>In: {stats['in']}<br>Out: {stats['out']}"
        
        folium.CircleMarker(
            location=data['coords'],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=popup_txt,
            tooltip=data['name']
        ).add_to(m)
        
    out = "mapa_girona.html"
    m.save(out)
    print(f"Saved {out}")

if __name__ == "__main__":
    generate_girona_map()
