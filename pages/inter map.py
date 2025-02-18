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

    # Get available columns for both facility and boundary data
    facility_columns = [col for col in facility_data.columns if col not in ['w_long', 'w_lat', 'geometry']]
    boundary_columns = [col for col in shapefile.columns if col not in ['geometry']]
    
    # Let user select which columns to show in hover
    st.subheader("Hover Information")
    
    col_hover1, col_hover2 = st.columns(2)
    
    with col_hover1:
        st.markdown("**Facility Point Information**")
        default_facility_columns = ['facility', 'FIRST_CHIE']  # Always show these
        facility_additional_columns = st.multiselect(
            "Select information to show when hovering over facilities",
            facility_columns,
            default=[]
        )
    
    with col_hover2:
        st.markdown("**Boundary Information**")
        default_boundary_columns = ['FIRST_CHIE']  # Always show chiefdom name
        boundary_additional_columns = st.multiselect(
            "Select information to show when hovering over boundaries",
            boundary_columns,
            default=[]
        )
    
    # Format selected columns for better display
    def format_column_name(col):
        return col.replace('_', ' ').title()

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
        
        # After spatial join, aggregate data at chiefdom level
        chiefdom_stats = district_facilities.groupby('FIRST_CHIE').agg({
            'facility': 'count',  # Count of facilities
            **{col: lambda x: ', '.join(x.astype(str).unique()) for col in facility_additional_columns}  # Aggregate other selected columns
        }).reset_index()
        
        # Merge aggregated stats back to district shapefile
        district_shapefile = district_shapefile.merge(
            chiefdom_stats,
            on='FIRST_CHIE',
            how='left'
        )
        
        # Fill NaN values
        district_shapefile = district_shapefile.fillna(0)
        
        # Add chiefdom boundaries with aggregated information
        for _, chiefdom in district_shapefile.iterrows():
            chiefdom_geojson = chiefdom.geometry.__geo_interface__
            
            # Create hover template for boundaries
            boundary_hover = f"<b>Chiefdom: {chiefdom['FIRST_CHIE']}</b><br>"
            boundary_hover += f"Total Facilities: {int(chiefdom['facility'])}<br>"
            
            # Add selected boundary columns to hover template
            for col in facility_additional_columns:
                if col in chiefdom.index:
                    formatted_name = format_column_name(col)
                    boundary_hover += f"{formatted_name}: {chiefdom[col]}<br>"
            
            boundary_hover += "<extra></extra>"
            
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
                    hovertemplate=boundary_hover
                )
            )
        
        # Create hover template with selected columns for facilities
        hover_template = "<b>%{text}</b><br>"
        hover_template += "Chiefdom: " + district_facilities['FIRST_CHIE'] + "<br>"
        
        # Add selected facility columns to hover template
        for col in facility_additional_columns:
            if col in district_facilities.columns:
                formatted_name = format_column_name(col)
                hover_template += f"{formatted_name}: " + district_facilities[col].astype(str) + "<br>"
        
        hover_template += "Coordinates: %{lon:.6f}, %{lat:.6f}<br>"
        hover_template += "<extra></extra>"
        
        # Add facilities with coordinates
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
                hovertemplate=hover_template,
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

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please ensure the required files are in the correct location:")
    st.write("- master_hf_list.xlsx")
    st.write("- Chiefdom 2021.shp (and associated .shx, .dbf files)")
