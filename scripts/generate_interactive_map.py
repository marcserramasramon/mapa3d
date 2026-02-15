import pandas as pd
import folium
from folium import plugins

def generate_interactive_map():
    print("Loading data...")
    try:
        df = pd.read_csv("derivacions_pacients.csv")
    except FileNotFoundError:
        print("Data file not found. Please generate referrals first.")
        return

    # Real GPS Coordinates
    locations = {
        "HVD": {"name": "Hospital Vall d'Hebron", "coords": [41.4276, 2.1449]},
        "HC": {"name": "Hospital Clínic", "coords": [41.3896, 2.1557]},
        "HSP": {"name": "Hospital Sant Pau", "coords": [41.4130, 2.1760]},
        "HB": {"name": "Hospital Bellvitge", "coords": [41.3444, 2.1066]},
        "HCR": {"name": "Hospital Can Ruti", "coords": [41.4816, 2.2389]},
        "HAV": {"name": "Hospital Arnau de Vilanova", "coords": [41.6247, 0.6083]},
        "HJT": {"name": "Hospital Josep Trueta", "coords": [41.9964, 2.8242]}
    }
    
    # Create Map centered on Catalonia
    m = folium.Map(location=[41.6, 1.8], zoom_start=8, tiles='CartoDB dark_matter')
    
    # Calculate Node Volumes
    node_stats = {code: {"in": 0, "out": 0} for code in locations}
    
    # Flow aggregation
    flows = df.groupby(['Origin', 'Destination']).size().reset_index(name='count')
    
    for _, row in flows.iterrows():
        orig = row['Origin']
        dest = row['Destination']
        count = row['count']
        
        if orig in node_stats: node_stats[orig]["out"] += count
        if dest in node_stats: node_stats[dest]["in"] += count
    
    max_flow = flows['count'].max()

    # Draw Lines (Flows)
    for _, row in flows.iterrows():
        orig = row['Origin']
        dest = row['Destination']
        count = row['count']
        
        if orig in locations and dest in locations:
            p1 = locations[orig]['coords']
            p2 = locations[dest]['coords']
            
            # Weight line by count
            weight = 2 + (count / max_flow) * 5
            opacity = 0.3 + (count / max_flow) * 0.7
            
            # Centralist coloring
            color = '#3388ff' # Default Blue
            hubs = ["HVD", "HC", "HSP"] # Strict Hubs
            
            # Visual Logic: Arrow direction? PolyLine doesn't show arrows easily without plugins.
            # Color logic:
            if dest in hubs: color = '#00ff00' # Green (Inbound to Center)
            elif orig in hubs: color = '#ff0000' # Red (Outbound from Center)
            
            tooltip_txt = f"{orig} -> {dest}: {count}"
            
            folium.PolyLine(
                [p1, p2], 
                weight=weight, 
                color=color, 
                opacity=opacity, 
                tooltip=tooltip_txt
            ).add_to(m)

    # Draw Nodes (Circles)
    for code, data in locations.items():
        stats = node_stats[code]
        total_vol = stats["in"] + stats["out"]
        
        # Radius based on volume
        radius = 5 + (total_vol * 0.5) 
        
        color = 'cyan'
        if code in ["HVD", "HC", "HSP"]: color = 'magenta' # Main Hubs
        
        popup_text = f"""
        <div style="width: 200px;">
            <h4>{data['name']} ({code})</h4>
            <hr>
            <b>Volume: {total_vol}</b><br>
            In: {stats['in']} | Out: {stats['out']}
        </div>
        """
        
        folium.CircleMarker(
            location=data['coords'],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=f"{data['name']}: {total_vol} patients"
        ).add_to(m)

    output = "mapa_interactiu_derivacions.html"
    m.save(output)
    print(f"Saved interactive map to {output}")

if __name__ == "__main__":
    generate_interactive_map()
