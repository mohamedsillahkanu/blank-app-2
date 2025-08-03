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

# Define colors for different facility types
TYPE_COLORS = {
    'HF': '#2E86AB',      # Blue
    'HTR': '#A23B72',     # Magenta
    'ETR': '#F18F01',     # Orange
    'HTR/ETR': '#C73E1D'  # Red
}

try:
    # Read files directly
    shapefile = gpd.read_file("Chiefdom 2021.shp")
    facility_data = pd.read_excel("CHW Geo.xlsx")

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
        
        # Create GeoDataFrame from facility data with explicit CRS
        facilities_gdf = gpd.GeoDataFrame(
            facility_data,
            geometry=[Point(xy) for xy in zip(facility_data['w_long'], facility_data['w_lat'])],
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
                        width=BOUNDARY_WIDTH
                    ),
                    name=chiefdom['FIRST_CHIE'],
                    hovertemplate=f"Chiefdom: {chiefdom['FIRST_CHIE']}<extra></extra>"
                )
            )
        
        # Add facilities grouped by type for different colors
        for facility_type in district_facilities['type'].unique():
            type_facilities = district_facilities[district_facilities['type'] == facility_type]
            
            fig.add_trace(
                go.Scattermapbox(
                    lat=type_facilities['w_lat'],
                    lon=type_facilities['w_long'],
                    mode='markers',
                    marker=dict(
                        size=POINT_SIZE,
                        color=TYPE_COLORS.get(facility_type, '#666666'),  # Default gray for unknown types
                    ),
                    text=type_facilities['hf'],
                    hovertemplate=(
                        "<b>%{text}</b><br>" +
                        f"Type: {facility_type}<br>" +
                        "Chiefdom: " + type_facilities['FIRST_CHIE'] + "<br>" +
                        f"Coordinates: %{{lon:.6f}}, %{{lat:.6f}}<br>" +
                        "<extra></extra>"
                    ),
                    name=f'{facility_type} Facilities'
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
        
        # Show facility type breakdown
        type_counts = district_facilities['type'].value_counts()
        st.write("**Facility Type Breakdown:**")
        for facility_type, count in type_counts.items():
            color = TYPE_COLORS.get(facility_type, '#666666')
            st.write(f"🔵 **{facility_type}**: {count} facilities", unsafe_allow_html=False)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please ensure the required files are in the correct location:")
    st.write("- master_hf_list.xlsx")
    st.write("- Chiefdom 2021.shp (and associated .shx, .dbf files)")
