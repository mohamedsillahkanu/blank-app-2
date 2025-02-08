import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from shapely.geometry import Point

st.set_page_config(layout="wide", page_title="Health Facility Map Generator")
st.title("Interactive Health Facility Map Generator")
st.write("Sierra Leone Health Facilities Map")

# Add celebration effects
st.snow()
st.balloons()
st.toast('Hooray!', icon='🎉')

try:
    # Read files directly
    shapefile = gpd.read_file("Chiefdom 2021.shp")
    facility_data = pd.read_excel("master_hf_list.xlsx")

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
        background_color = st.color_picker("Background Color", "#FFFFFF")

    with col6:
        map_height = st.slider("Map Height", 400, 1000, 800)
        zoom_level = st.slider("Initial Zoom Level", 5, 15, 9)

    # Get districts and user selection
    districts = sorted(shapefile['FIRST_DNAM'].unique())
    selected_district = st.selectbox("Select District", districts)

    # Generate Map button
    if st.button("Generate Map"):
        # Create GeoDataFrame from facility data
        geometry = [Point(xy) for xy in zip(facility_data['w_long'], facility_data['w_lat'])]
        facilities_gdf = gpd.GeoDataFrame(
            facility_data, 
            geometry=geometry,
            crs="EPSG:4326"
        )

        # Filter for selected district
        district_shapefile = shapefile[shapefile['FIRST_DNAM'] == selected_district]
        
        # Get district boundary coordinates
        bounds = district_shapefile.total_bounds
        
        # Spatial join to get facilities within the district
        district_facilities = gpd.sjoin(
            facilities_gdf,
            district_shapefile,
            how="inner",
            predicate="within"
        )
        
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
        if len(district_facilities) > 0:
            fig.add_trace(
                go.Scattermapbox(
                    lat=district_facilities['w_lat'],
                    lon=district_facilities['w_long'],
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
            paper_bgcolor=background_color
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

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please ensure the required files are in the correct location:")
    st.write("- master_hf_list.xlsx")
    st.write("- Chiefdom 2021.shp (and associated .shx, .dbf files)")
