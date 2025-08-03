import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from shapely.geometry import Point

st.set_page_config(layout="wide", page_title="Sierra Leone Health Facilities Map")
st.title("Sierra Leone Health Facilities Map")

# Fixed styling settings
POINT_SIZE = 8
BOUNDARY_WIDTH = 1
MAP_HEIGHT = 800

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
    facility_data = pd.read_excel("CHW Geo (1).xlsx")

    # Set the CRS for the shapefile if not already set
    if shapefile.crs is None:
        shapefile = shapefile.set_crs(epsg=4326)
    
    # Create GeoDataFrame from facility data with explicit CRS
    facilities_gdf = gpd.GeoDataFrame(
        facility_data,
        geometry=[Point(xy) for xy in zip(facility_data['w_long'], facility_data['w_lat'])],
        crs=shapefile.crs
    )

    # Get country boundary coordinates for centering
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
                name=chiefdom['FIRST_CHIE'],
                showlegend=False,
                hoverinfo='skip'
            )
        )
    
    # Add all facilities grouped by type for different colors
    for facility_type in facilities_gdf['type'].unique():
        if pd.notna(facility_type):  # Skip NaN values
            type_facilities = facilities_gdf[facilities_gdf['type'] == facility_type]
            
            fig.add_trace(
                go.Scattermapbox(
                    lat=type_facilities['w_lat'],
                    lon=type_facilities['w_long'],
                    mode='markers',
                    marker=dict(
                        size=POINT_SIZE,
                        color=TYPE_COLORS.get(facility_type, '#666666'),
                    ),
                    name=f'{facility_type} ({len(type_facilities)})',
                    hoverinfo='skip'
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
            zoom=7  # Zoom level to show entire country
        ),
        showlegend=True,
        margin=dict(t=100, r=30, l=30, b=30),
        paper_bgcolor='white'
    )

    # Display static map (no interactivity)
    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': False,
        'scrollZoom': False,
        'doubleClick': False,
        'showTips': False,
        'displaylogo': False,
        'staticPlot': True
    })

    # Display summary statistics
    st.header("Facility Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Count facilities by type
    type_counts = facilities_gdf['type'].value_counts()
    
    with col1:
        if 'HF' in type_counts:
            st.metric("Health Facilities (HF)", type_counts['HF'])
        else:
            st.metric("Health Facilities (HF)", 0)
    
    with col2:
        if 'HTR' in type_counts:
            st.metric("Health Treatment (HTR)", type_counts['HTR'])
        else:
            st.metric("Health Treatment (HTR)", 0)
    
    with col3:
        if 'ETR' in type_counts:
            st.metric("Emergency Treatment (ETR)", type_counts['ETR'])
        else:
            st.metric("Emergency Treatment (ETR)", 0)
    
    with col4:
        if 'HTR/ETR' in type_counts:
            st.metric("Combined (HTR/ETR)", type_counts['HTR/ETR'])
        else:
            st.metric("Combined (HTR/ETR)", 0)

    # Total facilities
    total_facilities = len(facilities_gdf)
    st.metric("**Total Health Facilities**", total_facilities)

    # Download option for the static map
    html_content = fig.to_html(
        config={
            'displayModeBar': False,
            'staticPlot': True
        },
        include_plotlyjs=True,
        full_html=True,
        include_mathjax=False
    )

    st.download_button(
        label="Download Static Map (HTML)",
        data=html_content,
        file_name="sierra_leone_health_facilities_map.html",
        mime='text/html'
    )

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please ensure the required files are in the correct location:")
    st.write("- master_hf_list.xlsx")
    st.write("- Chiefdom 2021.shp (and associated .shx, .dbf files)")
