import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import numpy as np

st.set_page_config(layout="wide", page_title="Health Facility Map Generator")

st.title("Health Facilities Distribution by district")
st.write("Sierra Leone Health Facilities Map")

# Add celebration effects at the start
st.snow()
st.balloons()
st.toast('Hooray!', icon='🎉')

try:
    # Read files directly
    shapefile = gpd.read_file("Chiefdom 2021.shp")
    facility_data = pd.read_excel("master_hf_list.xlsx")

    # Customization options
    st.header("Map Customization")

    # Map title in its own row
    map_title = st.text_input("Map Title", "Health Facility Distribution by Chiefdom", max_chars=100)

    # Other customization options in three columns
    col3, col4, col5 = st.columns(3)

    with col3:
        # Visual customization
        point_size = st.slider("Point Size", 10, 200, 50)
        point_alpha = st.slider("Point Transparency", 0.1, 1.0, 0.7)

    with col4:
        # Color selection
        background_colors = ["white", "lightgray", "beige", "lightblue"]
        point_colors = ["#47B5FF", "red", "green", "purple", "orange"]
        
        background_color = st.selectbox("Background Color", background_colors)
        point_color = st.selectbox("Point Color", point_colors)

    with col5:
        # Additional options
        show_facility_count = st.checkbox("Show Facility Count", value=True)
        show_chiefdom_name = st.checkbox("Show Chiefdom Name", value=True)

    # Rest of the code remains the same...
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
    
    # Set the grid size to 5 rows and 4 columns
    n_rows = 5
    n_cols = 4
    
    # Create figure with subplots and more space for title
    fig = plt.figure(figsize=(20, 25))
    fig.suptitle(map_title, fontsize=24, y=0.95)  # Adjusted y value for more space

    # Rest of the plotting code...
    for idx, chiefdom in enumerate(chiefdoms[:20]):
        if idx >= n_rows * n_cols:
            break
            
        # Create subplot
        ax = plt.subplot(n_rows, n_cols, idx + 1)
        
        # Filter shapefile for current chiefdom
        chiefdom_shapefile = district_shapefile[district_shapefile['FIRST_CHIE'] == chiefdom]
        
        # Plot chiefdom boundary
        chiefdom_shapefile.plot(ax=ax, color=background_color, edgecolor='black', linewidth=0.5)
        
        # Spatial join to get facilities within the chiefdom
        chiefdom_facilities = gpd.sjoin(
            facilities_gdf,
            chiefdom_shapefile,
            how="inner",
            predicate="within"
        )
        
        # Plot facilities
        if len(chiefdom_facilities) > 0:
            chiefdom_facilities.plot(
                ax=ax,
                color=point_color,
                markersize=point_size,
                alpha=point_alpha
            )
        
        # Set title
        title = ""
        if show_chiefdom_name:
            title += f"{chiefdom}"
        if show_facility_count:
            title += f"\n({len(chiefdom_facilities)} facilities)"
        
        ax.set_title(title, fontsize=12, pad=10)
        ax.axis('off')
        
        # Calculate and set aspect ratio
        bounds = chiefdom_shapefile.total_bounds
        mid_y = np.mean([bounds[1], bounds[3]])
        aspect = 1.0
        if -90 < mid_y < 90:
            try:
                aspect = 1 / np.cos(np.radians(mid_y))
                if not np.isfinite(aspect) or aspect <= 0:
                    aspect = 1.0
            except:
                aspect = 1.0
        ax.set_aspect(aspect)
        
        # Zoom to chiefdom bounds
        ax.set_xlim(bounds[0], bounds[2])
        ax.set_ylim(bounds[1], bounds[3])

    # Adjust layout with more space at the top
    plt.tight_layout()
    plt.subplots_adjust(top=0.90)
    
    # Display the map
    st.pyplot(fig)
    
    # Add celebration effects after map display
    st.snow()
    st.balloons()
    st.toast('Hooray!', icon='🎉')

    # Download options
    col6, col7 = st.columns(2)
    
    with col6:
        # Save high-resolution PNG centered
        output_path_png = "health_facility_map.png"
        plt.figure(fig.number)
        plt.tight_layout()
        plt.savefig(output_path_png, 
                   dpi=300, 
                   bbox_inches='tight', 
                   pad_inches=0.5,
                   facecolor='white')
        
        with open(output_path_png, "rb") as file:
            st.download_button(
                label="Download Map (PNG)",
                data=file,
                file_name=f"health_facility_map_{selected_district}.png",
                mime="image/png"
            )

    with col7:
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
