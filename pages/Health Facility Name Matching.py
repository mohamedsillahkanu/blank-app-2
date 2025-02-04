import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import numpy as np
from io import BytesIO

# Page configuration - must be the first Streamlit command
st.set_page_config(
    page_title="Health Facility Matching",
    page_icon="🗺️",
    layout="wide"
)

# Theme and styling
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
    }
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .uploadedFile {
        margin-bottom: 1rem;
    }
    .stDataFrame {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

def prepare_facility_data(facility_data, source):
    """
    Prepare facility data by adding appropriate suffixes to column names
    source: 'MFL' or 'DHIS2'
    """
    renamed_df = facility_data.copy()
    suffix = f"_{source}"
    renamed_df.columns = [f"{col}{suffix}" for col in renamed_df.columns]
    return renamed_df

def process_map(shapefile_data, mfl_data, dhis2_data, config):
    """Process and create the map with the given configuration"""
    try:
        # Prepare both datasets with appropriate suffixes
        mfl_data_processed = prepare_facility_data(mfl_data, "MFL")
        dhis2_data_processed = prepare_facility_data(dhis2_data, "DHIS2")

        # Create geometry for MFL data
        mfl_geometry = [Point(xy) for xy in zip(
            mfl_data[config['mfl_longitude_col']], 
            mfl_data[config['mfl_latitude_col']]
        )]
        mfl_gdf = gpd.GeoDataFrame(
            mfl_data_processed, 
            geometry=mfl_geometry, 
            crs="EPSG:4326"
        )

        # Create geometry for DHIS2 data
        dhis2_geometry = [Point(xy) for xy in zip(
            dhis2_data[config['dhis2_longitude_col']], 
            dhis2_data[config['dhis2_latitude_col']]
        )]
        dhis2_gdf = gpd.GeoDataFrame(
            dhis2_data_processed, 
            geometry=dhis2_geometry, 
            crs="EPSG:4326"
        )

        # Ensure consistent CRS for shapefile
        if shapefile_data.crs is None:
            shapefile_data = shapefile_data.set_crs(epsg=4326)
        else:
            shapefile_data = shapefile_data.to_crs(epsg=4326)

        # Create the map
        fig, ax = plt.subplots(figsize=(15, 10))
        
        # Plot shapefile
        shapefile_data.plot(
            ax=ax, 
            color=config['background_color'], 
            edgecolor='black', 
            linewidth=0.5
        )

        # Calculate aspect ratio
        bounds = shapefile_data.total_bounds
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

        # Plot MFL facilities in blue
        mfl_gdf.plot(
            ax=ax,
            color='blue',
            markersize=config['point_size'],
            alpha=config['point_alpha'],
            label='MFL Facilities'
        )

        # Plot DHIS2 facilities in red
        dhis2_gdf.plot(
            ax=ax,
            color='red',
            markersize=config['point_size'],
            alpha=config['point_alpha'],
            label='DHIS2 Facilities'
        )

        # Add legend
        ax.legend()

        # Customize appearance
        plt.title(config['map_title'], fontsize=20, pad=20)
        plt.axis('off')

        return fig, mfl_data_processed, dhis2_data_processed

    except Exception as e:
        st.error(f"Error in map processing: {str(e)}")
        return None, None, None

def main():
    st.title("Health Facility Distribution")
    st.write("Upload your shapefiles, MFL data, and DHIS2 data to generate a customized map.")

    # File upload section
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Upload Shapefiles")
        shp_file = st.file_uploader("Upload .shp file", type=["shp"])
        shx_file = st.file_uploader("Upload .shx file", type=["shx"])
        dbf_file = st.file_uploader("Upload .dbf file", type=["dbf"])

    with col2:
        st.header("Upload MFL Data")
        mfl_file = st.file_uploader("Upload MFL Excel file (.xlsx)", type=["xlsx"], key="mfl")

    with col3:
        st.header("Upload DHIS2 Data")
        dhis2_file = st.file_uploader("Upload DHIS2 Excel file (.xlsx)", type=["xlsx"], key="dhis2")

    # Process files if all are uploaded
    if all([shp_file, shx_file, dbf_file, mfl_file, dhis2_file]):
        try:
            # Read files
            shapefile = gpd.read_file(shp_file)
            mfl_data = pd.read_excel(mfl_file)
            dhis2_data = pd.read_excel(dhis2_file)
            
            # Preview the data
            st.subheader("MFL Data Preview")
            st.dataframe(mfl_data.head())
            st.subheader("DHIS2 Data Preview")
            st.dataframe(dhis2_data.head())

            # Map customization options
            st.header("Map Customization")
            
            col1, col2 = st.columns(2)
            
            with col1:
                map_title = st.text_input("Map Title", "Health Facility Distribution")
                point_size = st.slider("Point Size", 10, 200, 50)
                
            with col2:
                point_alpha = st.slider("Point Transparency", 0.1, 1.0, 0.7)
                background_color = st.selectbox(
                    "Background Color",
                    ["white", "lightgray", "beige", "lightblue"]
                )

            # Automatically set configuration using standardized column names
            config = {
                'mfl_longitude_col': next((col for col in mfl_data.columns if 'long' in col.lower()), mfl_data.columns[0]),
                'mfl_latitude_col': next((col for col in mfl_data.columns if 'lat' in col.lower()), mfl_data.columns[1]),
                'dhis2_longitude_col': next((col for col in dhis2_data.columns if 'long' in col.lower()), dhis2_data.columns[0]),
                'dhis2_latitude_col': next((col for col in dhis2_data.columns if 'lat' in col.lower()), dhis2_data.columns[1]),
                'map_title': map_title,
                'point_size': point_size,
                'point_alpha': point_alpha,
                'background_color': background_color
            }

            # Process and display map
            fig, mfl_processed, dhis2_processed = process_map(shapefile, mfl_data, dhis2_data, config)
            
            if fig and mfl_processed is not None and dhis2_processed is not None:
                st.pyplot(fig)

                # Combine processed data
                combined_data = pd.concat([mfl_processed, dhis2_processed], axis=1)

                # Download buttons
                col1, col2 = st.columns(2)
                with col1:
                    buf = BytesIO()
                    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                    st.download_button(
                        "Download Map (PNG)",
                        buf.getvalue(),
                        "health_facility_map.png",
                        "image/png"
                    )
                
                with col2:
                    csv = combined_data.to_csv(index=False)
                    st.download_button(
                        "Download Combined Data (CSV)",
                        csv,
                        "combined_facility_data.csv",
                        "text/csv"
                    )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.write("Please check your input files and try again.")
    else:
        st.info("""Please upload all required files to generate the map. You need:
        1. Shapefile components (.shp, .shx, .dbf)
        2. MFL Excel file (.xlsx)
        3. DHIS2 Excel file (.xlsx)
        """)

if __name__ == "__main__":
    main()
