import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import os

st.set_page_config(layout="wide", page_title="Health Facilities Distribution")

st.markdown("<h1 class='main-header'>Health Facilities Distribution</h1>", unsafe_allow_html=True)
st.write("Sierra Leone Health Facilities Map")

try:
    # Read files directly
    shapefile = gpd.read_file("Chiefdom 2021.shp")
    coordinates_data = pd.read_excel("master_hf_list.xlsx")

    # Display data preview
    st.subheader("Data Preview")
    st.dataframe(coordinates_data.head())

    # Map customization options
    st.header("Map Customization")
    st.snow()
    st.balloons()
    st.toast('Hooray!', icon='🎉')
    
    col4, col5 = st.columns(2)
    
    # Embed longitude and latitude columns
    longitude_col = "w_long"
    latitude_col = "w_lat"

    with col4:
        # Visual customization
        map_title = st.text_input("Map Title", "Health Facility Distribution")
        point_size = st.slider("Point Size", 10, 200, 50)
        point_alpha = st.slider("Point Transparency", 0.1, 1.0, 0.7)
        line_width = st.slider("Border Line Width", 0.1, 5.0, 0.5, 0.1)

    with col5:
        # Color selection
        background_colors = ["white", "lightgray", "beige", "lightblue", "black"]
        point_colors = ["#47B5FF", "red", "green", "purple", "orange"]
        line_colors = ["black", "gray", "darkgray", "dimgray", "lightgray"]
        
        background_color = st.selectbox("Background Color", background_colors)
        point_color = st.selectbox("Point Color", point_colors)
        line_color = st.selectbox("Border Line Color", line_colors)

    # Data processing
    # Remove missing coordinates
    coordinates_data = coordinates_data.dropna(subset=[longitude_col, latitude_col])
    
    # Filter invalid coordinates
    coordinates_data = coordinates_data[
        (coordinates_data[longitude_col].between(-180, 180)) &
        (coordinates_data[latitude_col].between(-90, 90))
    ]

    if len(coordinates_data) == 0:
        st.error("No valid coordinates found in the data after filtering.")
        st.stop()

    # Convert to GeoDataFrame
    geometry = [Point(xy) for xy in zip(coordinates_data[longitude_col], coordinates_data[latitude_col])]
    coordinates_gdf = gpd.GeoDataFrame(coordinates_data, geometry=geometry, crs="EPSG:4326")

    # Ensure consistent CRS
    if shapefile.crs is None:
        shapefile = shapefile.set_crs(epsg=4326)
    else:
        shapefile = shapefile.to_crs(epsg=4326)

    # Create the map with fixed aspect and centered
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111)

    # Plot shapefile with custom style
    shapefile.plot(ax=ax, color=background_color, edgecolor=line_color, linewidth=line_width)

    # Calculate and set appropriate aspect ratio
    bounds = shapefile.total_bounds
    mid_y = np.mean([bounds[1], bounds[3]])  # middle latitude
    aspect = 1.0  # default aspect ratio
    
    if -90 < mid_y < 90:  # check if latitude is valid
        try:
            aspect = 1 / np.cos(np.radians(mid_y))
            if not np.isfinite(aspect) or aspect <= 0:
                aspect = 1.0
        except:
            aspect = 1.0
    
    ax.set_aspect(aspect)

    # Plot points with custom style
    coordinates_gdf.plot(
        ax=ax,
        color=point_color,
        markersize=point_size,
        alpha=point_alpha
    )

    # Customize map appearance
    plt.title(map_title, fontsize=20, pad=20)
    plt.axis('off')

    # Add statistics
    stats_text = (
        f"Total Facilities: {len(coordinates_data)}\n"
        f"Coordinates Range:\n"
        f"Longitude: {coordinates_data[longitude_col].min():.2f}° to {coordinates_data[longitude_col].max():.2f}°\n"
        f"Latitude: {coordinates_data[latitude_col].min():.2f}° to {coordinates_data[latitude_col].max():.2f}°"
    )
    plt.figtext(0.02, 0.02, stats_text, fontsize=8, bbox=dict(facecolor='white', alpha=0.8))

    # Adjust layout to ensure map is centered
    plt.tight_layout()

    # Display the map
    st.pyplot(fig)
    st.snow()
    st.balloons()
    st.toast('Hooray!', icon='🎉')

    # Download options
    col6, col7 = st.columns(2)
    
    with col6:
        # Save high-resolution PNG with the map centered
        output_path_png = "health_facility_map.png"
        plt.figure(fig.number)  # Make sure we're working with the same figure
        plt.tight_layout()  # Apply tight layout before saving
        plt.savefig(output_path_png, 
                   dpi=300,
                   bbox_inches='tight',
                   pad_inches=0.5,
                   facecolor='white')
        
        with open(output_path_png, "rb") as file:
            st.download_button(
                label="Download Map (PNG)",
                data=file,
                file_name="health_facility_map.png",
                mime="image/png"
            )

    with col7:
        # Export coordinates as CSV
        csv = coordinates_data.to_csv(index=False)
        st.download_button(
            label="Download Processed Data (CSV)",
            data=csv,
            file_name="processed_coordinates.csv",
            mime="text/csv"
        )

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please ensure the required files are in the correct location:")
    st.write("- master_hf_list.xlsx")
    st.write("- Chiefdom 2021.shp (and associated .shx, .dbf files)")
