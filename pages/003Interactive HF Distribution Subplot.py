import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from shapely.geometry import Point

st.set_page_config(layout="wide", page_title="Health Facility Map Generator")

st.title("Interactive Health Facility Map Generator")
st.write("Sierra Leone Health Facilities Map")

try:
    # Read files directly
    shapefile = gpd.read_file("Chiefdom 2021.shp")
    facility_data = pd.read_excel("master_hf_list.xlsx")

    # Customization options
    st.header("Map Customization")
    col6, col7, col8 = st.columns(3)

    with col6:
        # Title customization
        map_title = st.text_input("Map Title", "Health Facility Distribution by Chiefdom")
        title_font_size = st.slider("Title Font Size", 12, 48, 24)
        title_spacing = st.slider("Title Top Spacing", 0, 200, 50, help="Adjust space above the title")
        point_size = st.slider("Point Size", 5, 20, 10)

    with col7:
        # Color selection
        point_color = st.color_picker("Point Color", "#FF4B4B")
        background_color = st.color_picker("Background Color", "#FFFFFF")

    with col8:
        # Additional options
        show_facility_count = st.checkbox("Show Facility Count", value=True)
        show_chiefdom_name = st.checkbox("Show Chiefdom Name", value=True)

    # Convert facility data to GeoDataFrame
    geometry = [Point(xy) for xy in zip(facility_data['w_long'], facility_data['w_lat'])]
    facilities_gdf = gpd.GeoDataFrame(
        facility_data, 
        geometry=geometry,
        crs="EPSG:4326"
    )

    # Get unique districts from shapefile
    districts = sorted(shapefile['FIRST_DNAM'].unique())
    selected_district = st.selectbox("Select District", districts)

    # Filter shapefile for selected district
    district_shapefile = shapefile[shapefile['FIRST_DNAM'] == selected_district]
    
    # Get unique chiefdoms for the selected district
    chiefdoms = sorted(district_shapefile['FIRST_CHIE'].unique())
    
    # Calculate grid dimensions for 4x4 layout
    n_chiefdoms = len(chiefdoms)
    grid_size = min(4, max(2, int(np.ceil(np.sqrt(n_chiefdoms)))))
    
    # Create subplot figure
    subplot_titles = [f"{chiefdom}" for chiefdom in chiefdoms[:grid_size*grid_size]]
    fig = make_subplots(
        rows=grid_size,
        cols=grid_size,
        subplot_titles=subplot_titles,
        specs=[[{"type": "scattermapbox"} for _ in range(grid_size)] for _ in range(grid_size)]
    )

    # Plot each chiefdom
    for idx, chiefdom in enumerate(chiefdoms[:grid_size*grid_size]):
        row = idx // grid_size + 1
        col = idx % grid_size + 1
        
        # Filter shapefile for current chiefdom
        chiefdom_shapefile = district_shapefile[district_shapefile['FIRST_CHIE'] == chiefdom]
        
        # Get chiefdom boundary coordinates
        bounds = chiefdom_shapefile.total_bounds
        
        # Spatial join to get facilities within the chiefdom
        chiefdom_facilities = gpd.sjoin(
            facilities_gdf,
            chiefdom_shapefile,
            how="inner",
            predicate="within"
        )
        
        if len(chiefdom_facilities) > 0:
            # Add scatter mapbox trace for facilities
            fig.add_trace(
                go.Scattermapbox(
                    lat=chiefdom_facilities['w_lat'],
                    lon=chiefdom_facilities['w_long'],
                    mode='markers',
                    marker=dict(
                        size=point_size,
                        color=point_color,
                    ),
                    text=chiefdom_facilities['facility'],
                    hovertemplate=(
                        f"Facility: %{{text}}<br>"
                        f"Latitude: %{{lat}}<br>"
                        f"Longitude: %{{lon}}<br>"
                        "<extra></extra>"
                    ),
                    name=chiefdom
                ),
                row=row,
                col=col
            )

        # Update layout for each subplot
        fig.update_layout({
            f'mapbox{idx+1}': {
                'style': "carto-positron",
                'center': {
                    'lat': np.mean([bounds[1], bounds[3]]),
                    'lon': np.mean([bounds[0], bounds[2]])
                },
                'zoom': 8
            }
        })

    # Update overall layout
    fig.update_layout(
        height=1000,
        title={
            'text': f"{map_title} {selected_district} District",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': title_font_size}
        },
        showlegend=False,
        margin=dict(t=title_spacing + title_font_size + 10, r=10, l=10, b=10)
    )

    # Display the map
    st.plotly_chart(fig, use_container_width=True)

    # Download options
    col9, col10 = st.columns(2)
    
    with col9:
        # Save as HTML
        html_file = f"health_facility_map_{selected_district}.html"
        fig.write_html(html_file)
        with open(html_file, "rb") as file:
            st.download_button(
                label="Download Interactive Map (HTML)",
                data=file,
                file_name=html_file,
                mime="text/html"
            )

    with col10:
        # Export facility data
        if len(chiefdom_facilities) > 0:
            csv = chiefdom_facilities.to_csv(index=False)
            st.download_button(
                label="Download Processed Data (CSV)",
                data=csv,
                file_name=f"health_facilities_{selected_district}.csv",
                mime="text/csv"
            )

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please ensure the required files are in the correct location:")
    st.write("- master_hf_list.xlsx")
    st.write("- Chiefdom 2021.shp (and associated .shx, .dbf files)")
