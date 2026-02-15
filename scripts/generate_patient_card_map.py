import pandas as pd
import folium
from folium import plugins
import girona_locations

def generate_patient_map():
    # Load extended data
    try:
        df = pd.read_csv("derivacions_girona_extended.csv")
        # Keep only recent or random subset if too many? 
        # For demo, let's keep all 7 days of data (~200 records usually)
    except FileNotFoundError:
        print("Data file not found. Please run generate_girona_referrals.py first.")
        return

    locs = girona_locations.locations
    
    # Create Map
    m = folium.Map(location=[41.95, 2.75], zoom_start=9, tiles='CartoDB dark_matter')
    
    # Feature Group for Patients
    patient_group = folium.FeatureGroup(name="Pacients")
    
    for _, row in df.iterrows():
        pid = row['Patient_ID']
        name = row['Name']
        orig = row['Origin']
        dest = row['Destination']
        pathology = row['Pathology']
        age = row['Age']
        urgency = row['Urgency']
        
        # Determine location: Plot at Origin (start of referral)
        if orig in locs:
            coords = locs[orig]['coords']
            
            # Create Custom Icon or simple marker
            # Color by Urgency
            color = 'blue'
            if urgency == 'Urgent': color = 'orange'
            if urgency == 'Emergencia': color = 'red'
            
            # HTML Card for Popup
            # Using table for clean layout
            popup_html = f"""
            <div style="font-family: Arial; min-width: 250px;">
                <h3 style="margin-bottom:5px; color:#2c3e50;">{name}</h3>
                <span style="background-color:#eee; padding:2px 5px; border-radius:3px; font-size:12px;">ID: {pid}</span>
                <hr style="margin: 5px 0;">
                <table style="width:100%; font-size:13px;">
                    <tr><td><b>Edat:</b></td><td>{age} anys ({row['Gender']})</td></tr>
                    <tr><td><b>Patologia:</b></td><td>{pathology}</td></tr>
                    <tr><td><b>Origen:</b></td><td>{locs[orig]['name']}</td></tr>
                    <tr><td><b>Destí:</b></td><td>{locs[dest]['name']}</td></tr>
                    <tr><td><b>Urgència:</b></td><td><b style="color:{color}">{urgency}</b></td></tr>
                </table>
                <div style="margin-top:10px; font-size:11px; color:#777;">
                    Data: {row['Timestamp']}
                </div>
            </div>
            """
            
            # We add specific searchable text to the Marker
            # The search plugin usually looks at properties.
            # folium.Marker doesn't strictly have 'properties' like GeoJSON. 
            # But the Search plugin for Marker objects often searches the Popup or Tooltip text if configured.
            # HOWEVER, robust search usually requires GeoJson. 
            # Let's try making a Marker with a clearly defined 'name' attribute or similar.
            
            marker = folium.Marker(
                location=coords,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{name} ({pid})",
                icon=folium.Icon(color=color, icon='user', prefix='fa')
            )
            
            # Hack: Add attributes to the marker object that the Search plugin might find?
            # actually, using a FeatureGroup + Search plugin is tricky with standard Markers.
            # The best way using Folium plugins.Search is often with GeoJSON.
            # But let's try standard Marker and see if "search_label" works or if we need to search 'tooltip'.
            
            # Actually, let's stick to standard Markers and configure Search to look at 'tooltip'.
            marker.add_to(patient_group)

    patient_group.add_to(m)
    
    # Add Search Plugin
    # Search needs a layer to search. We generally search a FeatureGroup or GeoJson.
    # search_label='tooltip' means it will search the text in the tooltip.
    search = plugins.Search(
        layer=patient_group,
        geom_type='Point',
        placeholder='Buscar pacient (ID o Nom)...',
        collapsed=False,
        search_label='tooltip', # This is key: search inside the tooltip text
        weight=3
    ).add_to(m)

    # Add other layers (Hospitals) as context but faint?
    # Or just keep it focused on patients.
    
    output = "mapa_fitxa_pacient.html"
    m.save(output)
    print(f"Saved patient card map to {output}")

if __name__ == "__main__":
    generate_patient_map()
