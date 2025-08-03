import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from shapely.geometry import Point

st.set_page_config(layout="wide", page_title="Health Facility Map Generator")
st.title("Interactive Health Facility/CHW Map Generator")
st.write("Sierra Leone Health Facilities Map")

# Add celebration effects
st.snow()
st.balloons()
st.toast('Hooray!', icon='🎉')

# Fixed styling settings
POINT_SIZE = 12
BOUNDARY_WIDTH = 2
MAP_HEIGHT = 800
ZOOM_LEVEL = 9

# Define colors for different facility types (more distinct colors)
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

    # Debug: Show data info - SPECIFICALLY LOOK FOR HF
    st.write(f"**Data loaded:** {len(facility_data)} records")
    
    # Show ALL unique values in 'type' column 
    if 'type' in facility_data.columns:
        st.write("**ALL values in 'type' column:**")
        all_types = facility_data['type'].value_counts(dropna=False)
        for type_val, count in all_types.items():
            color_display = {
                'HF': '🔵 Blue',
                'HTR': '🟢 Green', 
                'ETR': '🟣 Purple',
                'HTR/ETR': '🟠 Orange'
            }.get(type_val, '⚫ Unknown')
            st.write(f"- {color_display} **'{type_val}'**: {count} records")
            
        # SPECIFICALLY check for HF
        hf_exists = 'HF' in facility_data['type'].values
        st.write(f"**Does 'HF' exist in type column? {hf_exists}**")
        
        if hf_exists:
            hf_records = facility_data[facility_data['type'] == 'HF']
            st.write(f"**HF records found: {len(hf_records)}**")
            
            # Check HF coordinates
            hf_missing_coords = hf_records[['w_long', 'w_lat']].isnull().any(axis=1).sum()
            st.write(f"**HF records with missing coordinates: {hf_missing_coords}**")
            
    else:
        st.error("Column 'type' not found in data")
        st.stop()

    # Get districts and chiefdoms for user selection
    districts = sorted(shapefile['FIRST_DNAM'].unique())
    selected_district = st.selectbox("Select District", districts)
    
    # Filter chiefdoms based on selected district
    district_chiefdoms = shapefile[shapefile['FIRST_DNAM'] == selected_district]['FIRST_CHIE'].unique()
    chiefdoms = sorted(district_chiefdoms)
    selected_chiefdom = st.selectbox("Select Chiefdom", chiefdoms)

    # Generate Map button
    if st.button("Generate Map"):
        # Filter shapefile for selected chiefdom
        chiefdom_shapefile = shapefile[shapefile['FIRST_CHIE'] == selected_chiefdom].copy()
        
        # Set the CRS for the shapefile if not already set
        if chiefdom_shapefile.crs is None:
            chiefdom_shapefile = chiefdom_shapefile.set_crs(epsg=4326)
        
        # Clean the facility data - remove rows with missing coordinates
        clean_facility_data = facility_data.dropna(subset=['w_long', 'w_lat']).copy()
        st.write(f"**Clean data:** {len(clean_facility_data)} records with valid coordinates")
        
        # Show types BEFORE spatial filtering
        st.write("**Types in clean data BEFORE district filtering:**")
        types_before = clean_facility_data['type'].value_counts()
        for type_val, count in types_before.items():
            st.write(f"- {type_val}: {count}")
        
        # Create GeoDataFrame from facility data with explicit CRS
        facilities_gdf = gpd.GeoDataFrame(
            clean_facility_data,
            geometry=[Point(xy) for xy in zip(clean_facility_data['w_long'], clean_facility_data['w_lat'])],
            crs=chiefdom_shapefile.crs
        )

        # Spatial join to get facilities within the chiefdom
        chiefdom_facilities = gpd.sjoin(
            facilities_gdf,
            chiefdom_shapefile,
            how="inner",
            predicate="within"
        )

        # Show types AFTER spatial filtering
        st.write("**Types AFTER chiefdom spatial filtering:**")
        if len(chiefdom_facilities) > 0:
            types_after = chiefdom_facilities['type'].value_counts()
            for type_val, count in types_after.items():
                st.write(f"- {type_val}: {count}")
        else:
            st.write("No facilities found within chiefdom boundaries")

        if len(chiefdom_facilities) == 0:
            st.warning(f"No facilities found within {selected_chiefdom} Chiefdom boundaries.")
            # Show some debug info
            st.write("**Debug info:**")
            st.write(f"Chiefdom bounds: {chiefdom_shapefile.total_bounds}")
            if len(facilities_gdf) > 0:
                st.write(f"Facility coordinate range:")
                st.write(f"Longitude: {facilities_gdf['w_long'].min():.6f} to {facilities_gdf['w_long'].max():.6f}")
                st.write(f"Latitude: {facilities_gdf['w_lat'].min():.6f} to {facilities_gdf['w_lat'].max():.6f}")
            st.stop()

        # Get chiefdom boundary coordinates
        bounds = chiefdom_shapefile.total_bounds
        
        # Create figure
        fig = go.Figure()
        
        # Add chiefdom boundary
        for _, chiefdom in chiefdom_shapefile.iterrows():
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
                    name=chiefdom['FIRST_CHIE'],
                    showlegend=False,
                    hovertemplate=f"Chiefdom: {chiefdom['FIRST_CHIE']}<extra></extra>"
                )
            )
        
        # Add facilities grouped by type for different colors
        for type_value in chiefdom_facilities['type'].unique():
            if pd.notna(type_value):  # Skip NaN values
                type_facilities = chiefdom_facilities[chiefdom_facilities['type'] == type_value]
                
                # Create different hover templates based on type
                if type_value == 'HF':
                    # For HF: show facility name from 'hf' column, chiefdom, and coordinates
                    hover_template = (
                        "<b>%{text}</b><br>" +
                        "Chiefdom: " + type_facilities['FIRST_CHIE'].astype(str) + "<br>" +
                        f"Coordinates: %{{lon:.6f}}, %{{lat:.6f}}<br>" +
                        "<extra></extra>"
                    )
                    # Use the 'hf' column for HF facilities
                    text_data = type_facilities['hf'] if 'hf' in type_facilities.columns else type_facilities.index
                else:
                    # For others: show type, chiefdom, and coordinates
                    hover_template = (
                        f"<b>{type_value}</b><br>" +
                        "Chiefdom: " + type_facilities['FIRST_CHIE'].astype(str) + "<br>" +
                        f"Coordinates: %{{lon:.6f}}, %{{lat:.6f}}<br>" +
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
                            color=TYPE_COLORS.get(type_value, '#666666'),  # Default gray for unknown types
                        ),
                        text=text_data,
                        hovertemplate=hover_template,
                        name=f'{type_value} ({len(type_facilities)})'
                    )
                )

        # Update layout with fixed settings
        fig.update_layout(
            height=MAP_HEIGHT,
            title={
                'text': f"Health Facility Distribution<br>{selected_chiefdom} Chiefdom, {selected_district} District",
                'y': 0.98,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
            },
            mapbox=dict(
                style="carto-positron",
                center=dict(
                    lat=np.mean([bounds[1], bounds[3]]),
                    lon=np.mean([bounds[0], bounds[2]])
                ),
                zoom=11  # Higher zoom for chiefdom level
            ),
            showlegend=True,
            margin=dict(t=100, r=30, l=30, b=30),
            paper_bgcolor='white'
        )

        # Display interactive map
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': True,
            'scrollZoom': True,
            'displaylogo': False,
            'modeBarButtonsToAdd': ['drawrect', 'eraseshape'],
        })

        # Create GitHub-friendly interactive HTML
        github_html = fig.to_html(
            config={
                'displayModeBar': True,
                'scrollZoom': True,
                'doubleClick': 'reset+autosize',
                'displaylogo': False,
                'responsive': True,
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'{selected_chiefdom}_{selected_district}_health_facilities',
                    'height': 800,
                    'width': 1200,
                    'scale': 1
                }
            },
            include_plotlyjs='cdn',  # Use CDN for GitHub compatibility
            div_id="health-facility-map",
            full_html=True
        )
        
        # Add GitHub Pages compatible styling
        github_ready_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{selected_chiefdom} Chiefdom - Health Facilities Map</title>
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
            <h1>Health Facilities Distribution</h1>
            <p>{selected_chiefdom} Chiefdom, {selected_district} District, Sierra Leone</p>
        </div>
        <div class="map-container">
            {github_html.split('<body>')[1].split('</body>')[0]}
        </div>
        <div class="footer">
            Interactive map showing health facility locations | Generated with Plotly
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

        # Download options
        col7, col8, col9 = st.columns(3)
        
        with col7:
            st.download_button(
                label=f"📱 GitHub-Ready Map (HTML)",
                data=github_ready_html,
                file_name=f"health_facility_map_{selected_chiefdom.lower().replace(' ', '_')}_{selected_district.lower().replace(' ', '_')}.html",
                mime='text/html',
                help="Interactive HTML file optimized for GitHub Pages and web embedding"
            )

        with col8:
            # JSON export for developers
            facility_type_counts = chiefdom_facilities['type'].value_counts()
            json_data = {
                "district": selected_district,
                "chiefdom": selected_chiefdom,
                "facilities": chiefdom_facilities[['w_lat', 'w_long', 'type']].to_dict('records'),
                "bounds": bounds.tolist(),
                "total_count": len(chiefdom_facilities),
                "type_counts": facility_type_counts.to_dict()
            }
            st.download_button(
                label="📊 Data (JSON)",
                data=pd.Series(json_data).to_json(),
                file_name=f"health_facilities_{selected_chiefdom.lower().replace(' ', '_')}_{selected_district.lower().replace(' ', '_')}.json",
                mime="application/json",
                help="Structured data for developers"
            )

        with col9:
            if len(chiefdom_facilities) > 0:
                csv = chiefdom_facilities.to_csv(index=False)
                st.download_button(
                    label="📄 Data (CSV)",
                    data=csv,
                    file_name=f"health_facilities_{selected_chiefdom.lower().replace(' ', '_')}_{selected_district.lower().replace(' ', '_')}.csv",
                    mime="text/csv",
                    help="Spreadsheet-compatible data export"
                )

        # Display success message with facility count
        st.success(f"Generated map for {selected_chiefdom} Chiefdom, {selected_district} District with {len(chiefdom_facilities)} facilities")
        
        # Calculate and show facility type breakdown with updated colors
        type_counts = chiefdom_facilities['type'].value_counts()
        st.write("**Facility Type Breakdown:**")
        for type_value, count in type_counts.items():
            color_name = {
                'HF': '🔵 Blue',
                'HTR': '🟢 Green', 
                'ETR': '🟣 Purple',
                'HTR/ETR': '🟠 Orange'
            }.get(type_value, '⚫ Gray')
            st.write(f"{color_name} **{type_value}**: {count} facilities")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please ensure the required files are in the correct location:")
    st.write("- CHW Geo.xlsx")
    st.write("- Chiefdom 2021.shp (and associated .shx, .dbf files)")
    
    # Additional debug info
    st.write("**Debug information:**")
    try:
        if 'facility_data' in locals():
            st.write(f"Data shape: {facility_data.shape}")
            st.write(f"Columns: {list(facility_data.columns)}")
            st.write("First few rows:")
            st.dataframe(facility_data.head())
    except:
        st.write("Could not load debug information")
