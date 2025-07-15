import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from shapely.geometry import Point
import re

st.set_page_config(layout="wide", page_title="Health Facility Map Generator")
st.title("Interactive Health Facility Map Generator")
st.write("Sierra Leone Health Facilities Map")

# File Upload Section
st.header("📁 Upload Health Facilities Data")

uploaded_excel = st.file_uploader(
    "Upload Excel file with health facilities data",
    type=['xlsx', 'xls'],
    help="File should contain 'GPS Location' column with format: 'latitude,longitude'"
)

# Check if required file is uploaded
if not uploaded_excel:
    st.warning("⚠️ Please upload the Excel file containing health facilities data")
    st.info("Expected format: Excel file with 'GPS Location' column containing coordinates like '8.2458033,-11.5196267'")
    st.stop()

# Add celebration effects only when file is uploaded
st.balloons()
st.toast('Excel file uploaded successfully! 🎉', icon='🎉')

def parse_gps_location(gps_string):
    """
    Parse GPS location string and return latitude and longitude
    Expected format: "latitude,longitude" (e.g., "8.2458033,-11.5196267")
    """
    if pd.isna(gps_string) or gps_string == "":
        return None, None
    
    try:
        # Convert to string and strip whitespace
        gps_str = str(gps_string).strip()
        
        # Split by comma
        coords = gps_str.split(',')
        
        if len(coords) == 2:
            lat = float(coords[0].strip())
            lon = float(coords[1].strip())
            return lat, lon
        else:
            return None, None
    except (ValueError, AttributeError):
        return None, None

try:
    # Read the uploaded Excel file
    import tempfile
    import os
    
    # Save Excel file temporarily
    temp_dir = tempfile.mkdtemp()
    excel_path = os.path.join(temp_dir, uploaded_excel.name)
    with open(excel_path, "wb") as f:
        f.write(uploaded_excel.getbuffer())
    
    # Read Excel file
    st.info("📖 Reading uploaded Excel file...")
    facility_data = pd.read_excel(excel_path)
    
    # Read embedded shapefile (you'll need to place these files in your app directory)
    st.info("📖 Loading Sierra Leone administrative boundaries...")
    shapefile = gpd.read_file("Chiefdom 2021.shp")
    
    # Display file information
    st.success(f"✅ Successfully loaded {len(facility_data)} facilities and {len(shapefile)} administrative boundaries")
    
    # Show data preview
    with st.expander("📊 Data Preview"):
        st.write("**Health Facilities Data (first 5 rows):**")
        st.dataframe(facility_data.head())
        st.write(f"Columns: {', '.join(facility_data.columns.tolist())}")
        
        if 'GPS Location' in facility_data.columns:
            # Show sample GPS locations
            sample_gps = facility_data['GPS Location'].dropna().head(3).tolist()
            st.write(f"**Sample GPS Locations:** {sample_gps}")
        
        st.write("**Administrative Boundaries:**")
        st.write(f"Districts available: {', '.join(sorted(shapefile['FIRST_DNAM'].unique()))}")

    # Parse GPS Location column to extract latitude and longitude
    if 'GPS Location' in facility_data.columns:
        facility_data[['parsed_lat', 'parsed_lon']] = facility_data['GPS Location'].apply(
            lambda x: pd.Series(parse_gps_location(x))
        )
        
        # Drop rows with invalid GPS coordinates
        original_count = len(facility_data)
        facility_data = facility_data.dropna(subset=['parsed_lat', 'parsed_lon'])
        invalid_count = original_count - len(facility_data)
        
        if invalid_count > 0:
            st.info(f"Note: {invalid_count} facilities were excluded due to invalid GPS coordinates.")
        
        # Check if we have the old column names as fallback
        if 'w_lat' in facility_data.columns and 'w_long' in facility_data.columns:
            # Use parsed coordinates if available, otherwise fall back to old columns
            facility_data['final_lat'] = facility_data['parsed_lat'].fillna(facility_data['w_lat'])
            facility_data['final_lon'] = facility_data['parsed_lon'].fillna(facility_data['w_long'])
        else:
            # Use only the parsed coordinates
            facility_data['final_lat'] = facility_data['parsed_lat']
            facility_data['final_lon'] = facility_data['parsed_lon']
            
    elif 'w_lat' in facility_data.columns and 'w_long' in facility_data.columns:
        # Fallback to old column names if GPS Location doesn't exist
        facility_data['final_lat'] = facility_data['w_lat']
        facility_data['final_lon'] = facility_data['w_long']
        st.warning("Using legacy coordinate columns (w_lat, w_long). Consider updating to GPS Location format.")
    else:
        st.error("No valid GPS coordinate columns found. Expected 'GPS Location' or 'w_lat'/'w_long' columns.")
        st.stop()

    # Remove any remaining rows with invalid coordinates
    facility_data = facility_data.dropna(subset=['final_lat', 'final_lon'])

    if len(facility_data) == 0:
        st.error("No facilities with valid GPS coordinates found.")
        st.stop()

    # Map Customization
    st.header("Map Customization")
    
    # Map title in its own row
    map_title = st.text_input("Map Title", "Health Facility Distribution")

    # Other options in columns
    col4, col5, col6 = st.columns(3)
    
    with col4:
        point_size = st.slider("Point Size", 5, 20, 10)
        boundary_width = st.slider("Boundary Line Width", 1, 10, 3)

    with col5:
        # Point color dropdown
        point_colors = {
            "Blue": "#47B5FF",
            "Red": "#FF4B4B",
            "Green": "#00FF00",
            "Purple": "#800080",
            "Orange": "#FFA500"
        }
        selected_color = st.selectbox("Point Color", list(point_colors.keys()))
        point_color = point_colors[selected_color]

    with col6:
        map_height = st.slider("Map Height", 400, 1000, 800)
        zoom_level = st.slider("Initial Zoom Level", 5, 15, 9)

    # Get districts and user selection
    districts = sorted(shapefile['FIRST_DNAM'].unique())
    selected_district = st.selectbox("Select District", districts)

    # Generate Map button
    if st.button("Generate Map"):
        # Filter shapefile for selected district first
        district_shapefile = shapefile[shapefile['FIRST_DNAM'] == selected_district].copy()
        
        # Set the CRS for the shapefile if not already set
        if district_shapefile.crs is None:
            district_shapefile = district_shapefile.set_crs(epsg=4326)
        
        # Create GeoDataFrame from facility data with explicit CRS using the final coordinates
        facilities_gdf = gpd.GeoDataFrame(
            facility_data,
            geometry=[Point(xy) for xy in zip(facility_data['final_lon'], facility_data['final_lat'])],
            crs=district_shapefile.crs
        )

        # Spatial join to get facilities within the district
        district_facilities = gpd.sjoin(
            facilities_gdf,
            district_shapefile,
            how="inner",
            predicate="within"
        )

        if len(district_facilities) == 0:
            st.warning(f"No facilities found within {selected_district} District boundaries.")
            st.stop()

        # Get district boundary coordinates
        bounds = district_shapefile.total_bounds
        
        # Create figure
        fig = go.Figure()
        
        # Add chiefdom boundaries
        for _, chiefdom in district_shapefile.iterrows():
            chiefdom_geojson = chiefdom.geometry.__geo_interface__
            
            fig.add_trace(
                go.Scattermapbox(
                    mode='lines',
                    lon=[coord[0] for coord in chiefdom_geojson['coordinates'][0]],
                    lat=[coord[1] for coord in chiefdom_geojson['coordinates'][0]],
                    line=dict(
                        color='black',
                        width=boundary_width
                    ),
                    name=chiefdom['FIRST_CHIE'],
                    hovertemplate=f"Chiefdom: {chiefdom['FIRST_CHIE']}<extra></extra>"
                )
            )
        
        # Add facilities with coordinates
        fig.add_trace(
            go.Scattermapbox(
                lat=district_facilities['final_lat'],
                lon=district_facilities['final_lon'],
                mode='markers',
                marker=dict(
                    size=point_size,
                    color=point_color,
                ),
                text=district_facilities['facility'],
                hovertemplate=(
                    "<b>%{text}</b><br>" +
                    "Chiefdom: " + district_facilities['FIRST_CHIE'] + "<br>" +
                    f"Coordinates: %{{lon:.6f}}, %{{lat:.6f}}<br>" +
                    "<extra></extra>"
                ),
                name='Health Facilities'
            )
        )

        # Update layout with dynamic height
        fig.update_layout(
            height=map_height,
            title={
                'text': f"{map_title}<br>{selected_district} District",
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
                zoom=zoom_level
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

        # For the HTML download, create a version with full browser height
        html_content = fig.to_html(
            config={
                'displayModeBar': True,
                'scrollZoom': True,
                'displaylogo': False,
                'responsive': True,
            },
            include_plotlyjs=True,
            full_html=True,
            include_mathjax=False
        )

        # Add CSS to make the HTML version full screen
        full_screen_html = f"""
        <html>
            <head>
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        overflow: hidden;
                    }}
                    .js-plotly-plot {{
                        height: 100vh !important;
                    }}
                    .plotly-graph-div {{
                        height: 100vh !important;
                    }}
                </style>
            </head>
            <body>
                {html_content}
                <script>
                    window.onload = function() {{
                        setTimeout(function() {{
                            window.dispatchEvent(new Event('resize'));
                        }}, 100);
                    }};
                </script>
            </body>
        </html>
        """

        # Download options
        col7, col8 = st.columns(2)
        
        with col7:
            st.download_button(
                label=f"Download {selected_district} District Map (HTML)",
                data=full_screen_html,
                file_name=f"health_facility_map_{selected_district}.html",
                mime='text/html'
            )

        with col8:
            if len(district_facilities) > 0:
                csv = district_facilities.to_csv(index=False)
                st.download_button(
                    label="Download Facility Data (CSV)",
                    data=csv,
                    file_name=f"health_facilities_{selected_district}.csv",
                    mime="text/csv"
                )

        # Display success message with facility count
        st.success(f"Generated map for {selected_district} District with {len(district_facilities)} facilities")
        
        # Show coordinate format information
        st.info(f"Using GPS coordinates from: {'GPS Location column' if 'GPS Location' in facility_data.columns else 'Legacy w_lat/w_long columns'}")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please ensure you upload the correct files:")
    st.write("- Excel file (.xlsx or .xls) with health facilities data containing 'GPS Location' column")
    st.write("- Complete shapefile components (.shp, .shx, .dbf files)")
    st.write("Expected GPS Location format: '8.2458033,-11.5196267' (latitude,longitude)")
    
    # Clean up temporary directory if it exists
    try:
        if 'temp_dir' in locals():
            import shutil
            shutil.rmtree(temp_dir)
    except:
        pass
