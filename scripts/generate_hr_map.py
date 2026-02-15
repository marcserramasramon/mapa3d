import pandas as pd
import folium
from folium import plugins

def generate_hr_map():
    # Load Data
    try:
        df_dist = pd.read_csv("recursos_humans_distribucio.csv")
        df_collab = pd.read_csv("recursos_humans_colaboracions.csv")
    except FileNotFoundError:
        print("Data files not found. running generate_hr_data...")
        # (Assuming data exists per previous step)
        return

    # Coordinates (Approximate for Girona region)
    locations = {
        "HJT": {"name": "Hospital Josep Trueta", "coords": [41.9964, 2.8242]},
        "HSC": {"name": "Hospital Santa Caterina", "coords": [41.9723, 2.8094]},
        "HOL": {"name": "Hospital d'Olot", "coords": [42.1833, 2.4833]},
        "HCF": {"name": "Hospital de Campdevànol", "coords": [42.2285, 2.1667]},
        "HP": {"name": "Hospital de Palamós", "coords": [41.8500, 3.1333]},
        "HBF": {"name": "Hospital de Blanes", "coords": [41.6750, 2.7917]},
        "HCS": {"name": "Hospital de la Selva", "coords": [41.8333, 2.6667]}, # Approx. Santa Coloma de Farners
        "ABS_Girona": {"name": "CAP Girona", "coords": [41.9800, 2.8200]},
        "ABS_Salt": {"name": "CAP Salt", "coords": [41.9700, 2.7900]},
        "ABS_Banyoles": {"name": "CAP Banyoles", "coords": [42.1167, 2.7667]}
    }
    
    # Create Base Map
    m = folium.Map(location=[41.95, 2.75], zoom_start=9, tiles='CartoDB dark_matter')
    
    # 1. Visualization of Collaborations (Edges)
    for _, row in df_collab.iterrows():
        orig = row['Origen']
        dest = row['Desti']
        count = row['Personal_Movil']
        tipo = row['Tipus']
        
        if orig in locations and dest in locations:
            p1 = locations[orig]['coords']
            p2 = locations[dest]['coords']
            
            # Styling based on type
            color = 'orange'
            dash_array = None
            
            if tipo == "Formació": 
                color = 'green'
                dash_array = '5, 5'
            elif tipo == "Suport Especialista":
                color = 'cyan'
            
            weight = 2 + (count * 0.5)
            
            tooltip_txt = f"{orig} -> {dest}<br>{tipo}: {count} pax"
            
            folium.PolyLine(
                [p1, p2],
                color=color,
                weight=weight,
                opacity=0.6,
                dash_array=dash_array,
                tooltip=tooltip_txt
            ).add_to(m)

    # 2. Visualization of Nodes (Staff Density)
    # Aggregate total staff per hospital
    total_staff = df_dist.groupby('Hospital_Code')['Personal'].sum()
    
    for code, data in locations.items():
        if code in total_staff:
            count = total_staff[code]
            
            # Popup Content: Table of categories
            subset = df_dist[df_dist['Hospital_Code'] == code]
            
            table_html = """<table style="width:100%">
              <tr>
                <th>Categoria</th>
                <th>Personal</th> 
              </tr>"""
              
            for _, r in subset.iterrows():
                table_html += f"<tr><td>{r['Categoria']}</td><td>{r['Personal']}</td></tr>"
            
            table_html += "</table>"
            
            popup_html = f"""
            <div style="font-family: sans-serif; min-width: 200px;">
                <h4>{data['name']}</h4>
                <p><b>Total Personal: {count}</b></p>
                {table_html}
            </div>
            """
            
            # Circle Marker
            radius = 5 + (count / 100) # Scaling factor
            if radius > 40: radius = 40
            
            folium.CircleMarker(
                location=data['coords'],
                radius=radius,
                color='#ff9900', # HR Color (Orange-ish)
                fill=True,
                fill_color='#ff9900',
                fill_opacity=0.7,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{data['name']}"
            ).add_to(m)

    # Legend
    legend_html = '''
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 180px; height: 140px; 
     border:2px solid grey; z-index:9999; font-size:14px;
     background-color:rgba(255, 255, 255, 0.8);
     padding: 10px;
     border-radius: 5px;">
     <b>Llegenda RRHH</b><br>
     <i style="background:orange; width:10px; height:10px; display:inline-block; border-radius:50%"></i> Personal Total<br>
     <hr>
     <b>Fluxes:</b><br>
     <span style="color:cyan">---</span> Suport Esp.<br>
     <span style="color:green">- -</span> Formació<br>
     <span style="color:orange">---</span> Altres
     </div>
     '''
    m.get_root().html.add_child(folium.Element(legend_html))

    output = "mapa_recursos_humans.html"
    m.save(output)
    print(f"Saved HR map to {output}")

if __name__ == "__main__":
    generate_hr_map()
