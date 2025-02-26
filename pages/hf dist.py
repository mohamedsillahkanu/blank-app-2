import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import os
import io

st.set_page_config(layout="wide", page_title="Health Facilities Distribution")

st.markdown("<h1 class='main-header'>Health Facilities Distribution</h1>", unsafe_allow_html=True)
st.write("Sierra Leone Health Facilities Map")

try:
    # Load embedded shapefile
    shapefile = gpd.read_file("Chiefdom 2021.shp")
    
    # File upload section - only for health facilities data
    st.header("Upload Health Facilities Data")
    
    data_upload = st.file_uploader("Upload Health Facilities Data (.xlsx, .xls, .csv)", 
                                   type=["xlsx", "xls", "csv"])
    
    if data_upload is not None:
        # Read coordinates data based on file type
        file_extension = data_upload.name.split(".")[-1].lower()
        
        if file_extension == "csv":
            coordinates_data = pd.read_csv(data_upload)
        else:  # xlsx or xls
            coordinates_data = pd.read_excel(data_upload)
        
        # Display data preview
        st.subheader("Data Preview")
        st.dataframe(coordinates_data.head())
        
        # Column selection for coordinates
        st.subheader("Select Coordinate Columns")
        numeric_columns = coordinates_data.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns.tolist()
        
        col1, col2 = st.columns(2)
        
        with col1:
            longitude_col = st.selectbox("Select Longitude Column", options=numeric_columns)
        
        with col2:
            latitude_col = st.selectbox("Select Latitude Column", options=numeric_columns if len(numeric_columns) > 0 else ["No numeric columns found"])
        
        # Only proceed if user has selected coordinate columns
        if longitude_col != "No numeric columns found" and latitude_col != "No numeric columns found":
            # Map customization options
            st.header("Map Customization")
            
            col4, col5 = st.columns(2)
            
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
            # Drop rows with missing coordinates
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
            
            # Adjust layout to ensure map is centered first
            plt.tight_layout()
            
            # Add statistics at the bottom center of the map
            valid_points_count = len(coordinates_data)
            total_rows = len(pd.read_csv(data_upload) if file_extension == "csv" else pd.read_excel(data_upload))
            invalid_points = total_rows - valid_points_count
            
            stats_text = (
                f"Valid Facilities: {valid_points_count} (of {total_rows} total)\n"
                f"Invalid/Missing Coordinates: {invalid_points}\n"
                f"Coordinates Range:\n"
                f"Longitude: {coordinates_data[longitude_col].min():.2f}° to {coordinates_data[longitude_col].max():.2f}°\n"
                f"Latitude: {coordinates_data[latitude_col].min():.2f}° to {coordinates_data[latitude_col].max():.2f}°"
            )
            # Center the statistics at the bottom of the figure
            plt.figtext(0.5, 0.01, stats_text, fontsize=8, ha='center', 
                       bbox=dict(facecolor='white', alpha=0.8, boxstyle='round,pad=0.5'))
            
            # Display the map (centered in the page)
            col_left, col_map, col_right = st.columns([1, 10, 1])
            with col_map:
                st.pyplot(fig)
            
            # Optional celebrations
            if st.button("Celebrate!"):
                st.snow()
                st.balloons()
                st.toast('Hooray!', icon='🎉')
            
            # Download options
            col6, col7 = st.columns(2)
            
            with col6:
                # Save high-resolution PNG with the map centered
                buffer = io.BytesIO()
                plt.figure(fig.number)  # Make sure we're working with the same figure
                plt.tight_layout()  # Apply tight layout before saving
                plt.savefig(buffer, 
                           dpi=300,
                           bbox_inches='tight',
                           pad_inches=0.5,
                           facecolor='white',
                           format="png")
                buffer.seek(0)
                
                st.download_button(
                    label="Download Map (PNG)",
                    data=buffer,
                    file_name="health_facility_map.png",
                    mime="image/png"
                )
            
            with col7:
                # Export valid coordinates as CSV
                csv_buffer = io.StringIO()
                coordinates_data.to_csv(csv_buffer, index=False)
                csv_str = csv_buffer.getvalue()
                
                st.download_button(
                    label="Download Processed Data (CSV)",
                    data=csv_str,
                    file_name="processed_coordinates.csv",
                    mime="text/csv"
                )
        else:
            st.warning("Please select both longitude and latitude columns to proceed.")
    else:
        st.info("Please upload health facilities data file (.xlsx, .xls, or .csv) to begin.")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please check the following:")
    st.write("1. Make sure the embedded shapefile 'Chiefdom 2021.shp' and associated files are in the app directory")
    st.write("2. Upload a valid health facilities data file (.xlsx, .xls, or .csv) with coordinate columns")
