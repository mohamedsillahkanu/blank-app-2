import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from shapely.geometry import Point
import io
import zipfile
import numpy as np

st.set_page_config(layout="wide", page_title="Sierra Leone District Maps")
st.title("Sierra Leone District-Chiefdom Static Maps Generator")

# Define colors for different facility types
TYPE_COLORS = {
    'HF': '#1f77b4',      # Blue
    'HTR': '#2ca02c',     # Green
    'ETR': '#9467bd',     # Purple
    'HTR/ETR': '#ff7f0e'  # Orange
}

try:
    # Read files directly
    shapefile = gpd.read_file("Chiefdom 2021.shp")
    facility_data = pd.read_excel("CHW Geo (1).xlsx")

    # Set the CRS for the shapefile if not already set
    if shapefile.crs is None:
        shapefile = shapefile.set_crs(epsg=4326)
    
    # Clean the facility data - remove rows with missing coordinates
    clean_facility_data = facility_data.dropna(subset=['w_long', 'w_lat']).copy()
    
    # Create GeoDataFrame from facility data
    facilities_gdf = gpd.GeoDataFrame(
        clean_facility_data,
        geometry=[Point(xy) for xy in zip(clean_facility_data['w_long'], clean_facility_data['w_lat'])],
        crs=shapefile.crs
    )

    # Spatial join to add district and chiefdom information to facilities
    facilities_with_admin = gpd.sjoin(
        facilities_gdf,
        shapefile[['FIRST_DNAM', 'FIRST_CHIE', 'geometry']],
        how="left",
        predicate="within"
    )

    # Get all districts
    districts = sorted(shapefile['FIRST_DNAM'].unique())
    
    st.write(f"**Found {len(districts)} districts in Sierra Leone**")
    
    # Create ZIP file for all maps
    if st.button("Generate All District Maps"):
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for district_idx, district in enumerate(districts):
                status_text.text(f'Generating map for {district} District...')
                
                # Filter data for this district
                district_shapefile = shapefile[shapefile['FIRST_DNAM'] == district]
                district_facilities = facilities_with_admin[facilities_with_admin['FIRST_DNAM'] == district]
                
                # Get chiefdoms in this district
                chiefdoms = sorted(district_shapefile['FIRST_CHIE'].unique())
                
                # Calculate subplot dimensions (4 columns)
                cols = 4
                rows = (len(chiefdoms) + cols - 1) // cols  # Ceiling division
                
                # Create figure
                fig, axes = plt.subplots(rows, cols, figsize=(20, 5*rows))
                fig.suptitle(f'{district} District - Chiefdoms', fontsize=16, fontweight='bold')
                
                # Ensure axes is always a 2D array for consistent indexing
                if rows == 1 and cols == 1:
                    axes = np.array([[axes]])
                elif rows == 1:
                    axes = axes.reshape(1, -1)
                elif cols == 1:
                    axes = axes.reshape(-1, 1)
                
                # Plot each chiefdom
                for idx, chiefdom in enumerate(chiefdoms):
                    row = idx // cols
                    col = idx % cols
                    ax = axes[row, col]
                    
                    # Filter data for this chiefdom
                    chiefdom_shape = district_shapefile[district_shapefile['FIRST_CHIE'] == chiefdom]
                    chiefdom_facilities = district_facilities[district_facilities['FIRST_CHIE'] == chiefdom]
                    
                    # Plot chiefdom boundary
                    chiefdom_shape.boundary.plot(ax=ax, color='black', linewidth=1)
                    chiefdom_shape.plot(ax=ax, color='lightgray', alpha=0.3)
                    
                    # Plot facilities by type
                    for facility_type in chiefdom_facilities['type'].unique():
                        if pd.notna(facility_type):
                            type_facilities = chiefdom_facilities[chiefdom_facilities['type'] == facility_type]
                            ax.scatter(
                                type_facilities['w_long'], 
                                type_facilities['w_lat'],
                                c=TYPE_COLORS.get(facility_type, '#666666'),
                                s=30,
                                alpha=0.8,
                                label=f'{facility_type} ({len(type_facilities)})',
                                edgecolors='white',
                                linewidth=0.5
                            )
                    
                    # Set title and formatting
                    ax.set_title(f'{chiefdom}\n({len(chiefdom_facilities)} hf/chw)', 
                               fontsize=10, fontweight='bold')
                    ax.set_aspect('equal')
                    ax.axis('off')  # Turn off axes
                    
                    # Add legend if there are facilities
                    if len(chiefdom_facilities) > 0:
                        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
                
                # Hide empty subplots
                total_subplots = rows * cols
                for idx in range(len(chiefdoms), total_subplots):
                    row = idx // cols
                    col = idx % cols
                    ax = axes[row, col]
                    ax.set_visible(False)
                
                plt.tight_layout()
                
                # Save to ZIP
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
                img_buffer.seek(0)
                
                zip_file.writestr(f'{district.replace(" ", "_")}_district_chiefdoms.png', img_buffer.getvalue())
                plt.close()
                
                # Update progress
                progress_bar.progress((district_idx + 1) / len(districts))
            
            # Create summary map of all districts
            status_text.text('Creating summary map...')
            
            fig, ax = plt.subplots(1, 1, figsize=(15, 12))
            
            # Plot all districts with different colors
            district_colors = plt.cm.Set3(np.linspace(0, 1, len(districts)))
            
            for idx, district in enumerate(districts):
                district_shape = shapefile[shapefile['FIRST_DNAM'] == district]
                district_shape.plot(ax=ax, color=district_colors[idx], alpha=0.6, 
                                  edgecolor='black', linewidth=0.5)
                
                # Add district label at centroid
                centroid = district_shape.geometry.centroid.iloc[0]
                ax.annotate(district, xy=(centroid.x, centroid.y), 
                          fontsize=8, ha='center', va='center', fontweight='bold')
            
            # Plot all facilities
            for facility_type in facilities_with_admin['type'].unique():
                if pd.notna(facility_type):
                    type_facilities = facilities_with_admin[facilities_with_admin['type'] == facility_type]
                    ax.scatter(
                        type_facilities['w_long'], 
                        type_facilities['w_lat'],
                        c=TYPE_COLORS.get(facility_type, '#666666'),
                        s=15,
                        alpha=0.8,
                        label=f'{facility_type} ({len(type_facilities)})',
                        edgecolors='white',
                        linewidth=0.3
                    )
            
            ax.set_title('Sierra Leone - All Districts and Health Facilities', 
                        fontsize=16, fontweight='bold')
            ax.set_aspect('equal')
            ax.axis('off')  # Turn off axes
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.tight_layout()
            
            # Save summary to ZIP
            summary_buffer = io.BytesIO()
            plt.savefig(summary_buffer, format='png', dpi=300, bbox_inches='tight')
            summary_buffer.seek(0)
            
            zip_file.writestr('00_Sierra_Leone_Summary.png', summary_buffer.getvalue())
            plt.close()
            
            status_text.text('Complete!')
            progress_bar.progress(1.0)
        
        zip_buffer.seek(0)
        
        # Download button for ZIP file
        st.download_button(
            label="📦 Download All District Maps (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="sierra_leone_district_maps.zip",
            mime="application/zip"
        )
        
        st.success(f"Generated {len(districts)} district maps + 1 summary map!")
        
        # Show summary statistics
        st.write("**District Summary:**")
        for district in districts:
            district_facilities = facilities_with_admin[facilities_with_admin['FIRST_DNAM'] == district]
            district_chiefdoms = shapefile[shapefile['FIRST_DNAM'] == district]['FIRST_CHIE'].nunique()
            st.write(f"- **{district}**: {district_chiefdoms} chiefdoms, {len(district_facilities)} facilities")

    # Individual district selector
    st.header("Generate Individual District Map")
    selected_district = st.selectbox("Select District for Individual Map", districts)
    
    if st.button("Generate Single District Map"):
        # Filter data for selected district
        district_shapefile = shapefile[shapefile['FIRST_DNAM'] == selected_district]
        district_facilities = facilities_with_admin[facilities_with_admin['FIRST_DNAM'] == selected_district]
        
        # Get chiefdoms in this district
        chiefdoms = sorted(district_shapefile['FIRST_CHIE'].unique())
        
        # Calculate subplot dimensions (4 columns)
        cols = 4
        rows = (len(chiefdoms) + cols - 1) // cols
        
        # Create figure
        fig, axes = plt.subplots(rows, cols, figsize=(20, 5*rows))
        fig.suptitle(f'{selected_district} District - Chiefdoms', fontsize=16, fontweight='bold')
        
        # Ensure axes is always a 2D array for consistent indexing
        if rows == 1 and cols == 1:
            axes = np.array([[axes]])
        elif rows == 1:
            axes = axes.reshape(1, -1)
        elif cols == 1:
            axes = axes.reshape(-1, 1)
        
        # Plot each chiefdom
        for idx, chiefdom in enumerate(chiefdoms):
            row = idx // cols
            col = idx % cols
            ax = axes[row, col]
            
            # Filter data for this chiefdom
            chiefdom_shape = district_shapefile[district_shapefile['FIRST_CHIE'] == chiefdom]
            chiefdom_facilities = district_facilities[district_facilities['FIRST_CHIE'] == chiefdom]
            
            # Plot chiefdom boundary
            chiefdom_shape.boundary.plot(ax=ax, color='black', linewidth=1)
            chiefdom_shape.plot(ax=ax, color='lightgray', alpha=0.3)
            
            # Plot facilities by type
            for facility_type in chiefdom_facilities['type'].unique():
                if pd.notna(facility_type):
                    type_facilities = chiefdom_facilities[chiefdom_facilities['type'] == facility_type]
                    ax.scatter(
                        type_facilities['w_long'], 
                        type_facilities['w_lat'],
                        c=TYPE_COLORS.get(facility_type, '#666666'),
                        s=30,
                        alpha=0.8,
                        label=f'{facility_type} ({len(type_facilities)})',
                        edgecolors='white',
                        linewidth=0.5
                    )
            
            # Set title and formatting
            ax.set_title(f'{chiefdom}\n({len(chiefdom_facilities)} hf/chw)', 
                       fontsize=10, fontweight='bold')
            ax.set_aspect('equal')
            ax.axis('off')  # Turn off axes
            
            # Add legend if there are facilities
            if len(chiefdom_facilities) > 0:
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        
        # Hide empty subplots
        total_subplots = rows * cols
        for idx in range(len(chiefdoms), total_subplots):
            row = idx // cols
            col = idx % cols
            ax = axes[row, col]
            ax.set_visible(False)
        
        plt.tight_layout()
        
        # Display the plot
        st.pyplot(fig)
        
        # Save as PNG for download
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        
        st.download_button(
            label=f"📷 Download {selected_district} District Map (PNG)",
            data=img_buffer.getvalue(),
            file_name=f"{selected_district.replace(' ', '_')}_district_chiefdoms.png",
            mime="image/png"
        )
        
        # Show district statistics
        st.write(f"**{selected_district} District Summary:**")
        st.write(f"- **Chiefdoms**: {len(chiefdoms)}")
        st.write(f"- **Total Facilities**: {len(district_facilities)}")
        
        type_counts = district_facilities['type'].value_counts()
        for facility_type, count in type_counts.items():
            color_name = {
                'HF': '🔵 Blue',
                'HTR': '🟢 Green', 
                'ETR': '🟣 Purple',
                'HTR/ETR': '🟠 Orange'
            }.get(facility_type, '⚫ Unknown')
            st.write(f"  - {color_name} **{facility_type}**: {count} hf/chw")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.write("Please ensure the required files are in the correct location:")
    st.write("- CHW Geo.xlsx")
    st.write("- Chiefdom 2021.shp (and associated .shx, .dbf files)")
