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

# Define colors for different facility types (updated as requested)
TYPE_COLORS = {
    'HF': '#2E86AB',      # Blue
    'HTR': '#28A745',     # Green
    'ETR': '#6F42C1',     # Purple
    'HTR/ETR': '#FD7E14'  # Orange
}

try:
    # Read files directly
    shapefile = gpd.read_file("Chiefdom 2021.shp")
    facility_data = pd.read_excel("CHW Geo.xlsx")

    # Debug: Show data info
    st.write(f"**Data loaded:** {len(facility_data)} records")
    st.write(f"**Columns:** {list(facility_data.columns)}")
    
    # Check for missing coordinates
    missing_coords = facility_data[['w_long', 'w_lat']].isnull().any(axis=1).sum()
    if missing_coords > 0:
        st.warning(f"Found {missing_coords} records with missing coordinates")
    
    # Show unique facility types
    if 'type' in facility_data.columns:
        unique_types = facility_data['type'].value_counts()
        st.write("**Facility types found:**")
        for ftype, count in unique_types.items():
            st.write(f"- {ftype}: {count}")
    else:
        st.error("'type' column not found in data")
        st.stop()

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
        
        # Clean the facility data - remove rows with missing coordinates
        clean_facility_data = facility_data.dropna(subset=['w_long', 'w_lat']).copy()
        st.write(f"**Clean data:** {len(clean_facility_data)} records with valid coordinates")
        
        # Create GeoDataFrame from facility data with explicit CRS
        facilities_gdf = gpd.GeoDataFrame(
            clean_facility_data,
            geometry=[Point(xy) for xy in zip(clean_facility_data['w_long'], clean_facility_data['w_lat'])],
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
            # Show some debug info
            st.write("**Debug info:**")
            st.write(f"District bounds: {district_shapefile.total_bounds}")
            if len(facilities_gdf) > 0:
                st.write(f"Facility coordinate range:")
                st.write(f"Longitude: {facilities_gdf['w_long'].min():.6f} to {facilities_gdf['w_long'].max():.6f}")
                st.write(f"Latitude: {facilities_gdf['w_lat'].min():.6f} to {facilities_gdf['w_lat'].max():.6f}")
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
                        width=BOUNDARY_WIDTH
                    ),
                    name=chiefdom['FIRST_CHIE'],
                    showlegend=False,
                    hovertemplate=f"Chiefdom: {chiefdom['FIRST_CHIE']}<extra></extra>"
                )
            )
        
        # Add facilities grouped by type for different colors
        for type_value in district_facilities['type'].unique():
            if pd.notna(type_value):  # Skip NaN values
                type_facilities = district_facilities[district_facilities['type'] == type_value]
                
                # Use facility name column - check if 'hf' exists, otherwise use first text column
                name_column = 'hf' if 'hf' in type_facilities.columns else type_facilities.select_dtypes(include=['object']).columns[0]
                
                fig.add_trace(
                    go.Scattermapbox(
                        lat=type_facilities['w_lat'],
                        lon=type_facilities['w_long'],
                        mode='markers',
                        marker=dict(
                            size=POINT_SIZE,
                            color=TYPE_COLORS.get(type_value, '#666666'),  # Default gray for unknown types
                        ),
                        text=type_facilities[name_column] if name_column in type_facilities.columns else type_facilities.index,
                        hovertemplate=(
                            "<b>%{text}</b><br>" +
                            f"Type: {type_value}<br>" +
                            "Chiefdom: " + type_facilities['FIRST_CHIE'].astype(str) + "<br>" +
                            f"Coordinates: %{{lon:.6f}}, %{{lat:.6f}}<br>" +
                            "<extra></extra>"
                        ),
                        name=f'{type_value} ({len(type_facilities)})'
                    )
                )

        # Update layout with fixed settings
        fig.update_layout(
            height=MAP_HEIGHT,
            title={
                'text': f"Health Facility Distribution<br>{selected_district} District",
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
                zoom=ZOOM_LEVEL
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

        # Display success message with facility count and type breakdown
        st.success(f"Generated map for {selected_district} District with {len(district_facilities)} facilities")
        
        # Show facility type breakdown with updated colors
        type_counts = district_facilities['type'].value_counts()
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
