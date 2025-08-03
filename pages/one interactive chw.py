import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from shapely.geometry import Point

st.set_page_config(layout="wide", page_title="Sierra Leone Health Facilities")
st.title("Sierra Leone Health Facilities Map")

# Fixed styling settings
POINT_SIZE = 8
BOUNDARY_WIDTH = 1
MAP_HEIGHT = 800

# Define colors for different facility types
TYPE_COLORS = {
    'HF': '#1f77b4',      # Blue
    'HTR': '#2ca02c',     # Green
    'ETR': '#9467bd',     # Purple
    'HTR/ETR': '#ff7f0e'  # Orange
}

try:
    # Read files directly
    shapefile = gpd.read_file("Chiefdom 2021.shp")
    facility_data = pd.read_excel("CHW Geo (1).xlsx")

    # Set the CRS for the shapefile if not already set
    if shapefile.crs is None:
        shapefile = shapefile.set_crs(epsg=4326)
    
    # Clean the facility data - remove rows with missing coordinates
    clean_facility_data = facility_data.dropna(subset=['w_long', 'w_lat']).copy()
    
    # Debug: Show facility types in original data
    st.write("**Facility types in data:**")
    type_counts_original = clean_facility_data['type'].value_counts()
    for type_val, count in type_counts_original.items():
        st.write(f"- {type_val}: {count}")
    
    # Create GeoDataFrame from facility data
    facilities_gdf = gpd.GeoDataFrame(
        clean_facility_data,
        geometry=[Point(xy) for xy in zip(clean_facility_data['w_long'], clean_facility_data['w_lat'])],
        crs=shapefile.crs
    )

    # Spatial join to add district and chiefdom information to facilities
    facilities_with_admin = gpd.sjoin(
        facilities_gdf,
        shapefile[['FIRST_DNAM', 'FIRST_CHIE', 'geometry']],
        how="left",
        predicate="within"
    )
    
    # Debug: Show facility types after spatial join
    st.write("**Facility types after adding district/chiefdom info:**")
    type_counts_after = facilities_with_admin['type'].value_counts()
    for type_val, count in type_counts_after.items():
        st.write(f"- {type_val}: {count}")

    # Get country bounds for centering
    bounds = shapefile.total_bounds
    
    # Create figure
    fig = go.Figure()
    
    # Add all chiefdom boundaries
    for _, chiefdom in shapefile.iterrows():
        chiefdom_geojson = chiefdom.geometry.__geo_interface__
        
        fig.add_trace(
            go.Scattermapbox(
                mode='lines',
                lon=[coord[0] for coord in chiefdom_geojson['coordinates'][0]],
                lat=[coord[1] for coord in chiefdom_geojson['coordinates'][0]],
                line=dict(
                    color='black',
                    width=BOUNDARY_WIDTH
                ),
                showlegend=False,
                hoverinfo='skip'
            )
        )
    
    # Add all facilities grouped by type
    for type_value in facilities_with_admin['type'].unique():
        if pd.notna(type_value):  # Skip NaN values
            type_facilities = facilities_with_admin[facilities_with_admin['type'] == type_value]
            
            # Debug: Show count for each type being plotted
            st.write(f"Plotting {type_value}: {len(type_facilities)} facilities")
            
            # Create different hover templates based on type
            if type_value == 'HF':
                # For HF: show facility name from 'hf' column
                hover_template = (
                    "<b>%{text}</b><br>" +
                    "District: " + type_facilities['FIRST_DNAM'].fillna('Unknown').astype(str) + "<br>" +
                    "Chiefdom: " + type_facilities['FIRST_CHIE'].fillna('Unknown').astype(str) + "<br>" +
                    "Coordinates: %{lon:.6f}, %{lat:.6f}<br>" +
                    "<extra></extra>"
                )
                # Use the 'hf' column for HF facilities
                text_data = type_facilities['hf'] if 'hf' in type_facilities.columns else [f"HF Facility {i}" for i in range(len(type_facilities))]
            else:
                # For others: show type
                hover_template = (
                    f"<b>{type_value}</b><br>" +
                    "District: " + type_facilities['FIRST_DNAM'].fillna('Unknown').astype(str) + "<br>" +
                    "Chiefdom: " + type_facilities['FIRST_CHIE'].fillna('Unknown').astype(str) + "<br>" +
                    "Coordinates: %{lon:.6f}, %{lat:.6f}<br>" +
                    "<extra></extra>"
                )
                # Use the type value for other facilities
                text_data = [type_value] * len(type_facilities)
            
            fig.add_trace(
                go.Scattermapbox(
                    lat=type_facilities['w_lat'],
                    lon=type_facilities['w_long'],
                    mode='markers',
                    marker=dict(
                        size=POINT_SIZE,
                        color=TYPE_COLORS.get(type_value, '#666666'),
                        opacity=0.8
                    ),
                    text=text_data,
                    hovertemplate=hover_template,
                    name=f'{type_value} ({len(type_facilities)})'
                )
            )

    # Update layout for full country view
    fig.update_layout(
        height=MAP_HEIGHT,
        title={
            'text': "Sierra Leone Health Facilities Distribution",
            'y': 0.98,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20}
        },
        mapbox=dict(
            style="carto-positron",
            center=dict(
                lat=np.mean([bounds[1], bounds[3]]),
                lon=np.mean([bounds[0], bounds[2]])
            ),
            zoom=7  # Full country view
        ),
        showlegend=True,
        margin=dict(t=100, r=30, l=30, b=30),
        paper_bgcolor='white'
    )

    # Display the map
    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': True,
        'scrollZoom': True,
        'displaylogo': False,
    })

    # Create GitHub-ready HTML
    github_html = fig.to_html(
        config={
            'displayModeBar': True,
            'scrollZoom': True,
            'doubleClick': 'reset+autosize',
            'displaylogo': False,
            'responsive': True,
        },
        include_plotlyjs='cdn',
        div_id="health-facility-map",
        full_html=True
    )
    
    # GitHub Pages compatible styling
    github_ready_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sierra Leone Health Facilities Map</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .map-container {{
            padding: 0;
            height: 800px;
        }}
        #health-facility-map {{
            height: 100% !important;
            width: 100% !important;
        }}
        .footer {{
            padding: 15px 20px;
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
        }}
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            .header h1 {{
                font-size: 1.5em;
            }}
            .map-container {{
                height: 600px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Sierra Leone Health Facilities</h1>
            <p>Complete distribution of health facilities across all chiefdoms</p>
        </div>
        <div class="map-container">
            {github_html.split('<body>')[1].split('</body>')[0]}
        </div>
        <div class="footer">
            Interactive map showing all health facility locations | Generated with Plotly
        </div>
    </div>
    <script>
        window.addEventListener('load', function() {{
            setTimeout(function() {{
                window.dispatchEvent(new Event('resize'));
                if (window.Plotly) {{
                    window.Plotly.Plots.resize('health-facility-map');
                }}
            }}, 100);
        }});
    </script>
</body>
</html>"""

    # Download button
    st.download_button(
        label="📱 Download Complete Map (HTML)",
        data=github_ready_html,
        file_name="sierra_leone_health_facilities_complete.html",
        mime='text/html',
        help="Interactive HTML file showing all health facilities"
    )

    # Show total summary
    total_facilities = len(facilities_with_admin)
    type_counts = facilities_with_admin['type'].value_counts()
    
    st.write(f"**Total Health Facilities: {total_facilities}**")
    
    for type_value, count in type_counts.items():
        color_name = {
            'HF': '🔵 Blue',
            'HTR': '🟢 Green', 
            'ETR': '🟣 Purple',
            'HTR/ETR': '🟠 Orange'
        }.get(type_value, '⚫ Unknown')
        st.write(f"{color_name} **{type_value}**: {count} facilities")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please ensure the required files are in the correct location:")
    st.write("- CHW Geo.xlsx")
    st.write("- Chiefdom 2021.shp (and associated .shx, .dbf files)")
