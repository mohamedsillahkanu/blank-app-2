import streamlit as st
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import numpy as np
from io import BytesIO

# Page configuration - must be the first Streamlit command
st.set_page_config(
    page_title="Health Facility Map Generator",
    page_icon="🗺️",
    layout="wide"
)

# Light Sand Theme styling
st.markdown("""
    <style>
    .stApp {
        background-color: #FAFAFA;
    }
    .main {
        padding: 2rem;
        color: #424242;
    }
    .stButton>button {
        background-color: #FF7043 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        width: 100%;
        margin-top: 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FFB74D !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .uploadedFile {
        margin-bottom: 1rem;
        background: #FFFFFF;
        padding: 1rem;
        border-radius: 4px;
        border: 1px solid #FFB74D;
    }
    .stDataFrame {
        margin-top: 1rem;
        margin-bottom: 1rem;
        background: #FFFFFF;
        padding: 1rem;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stSelectbox > div > div {
        background-color: #FFFFFF;
        border: 1px solid #FFB74D;
    }
    .stTextInput > div > div > input {
        border: 1px solid #FFB74D;
    }
    .stSlider > div > div > div {
        background-color: #FF7043;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #424242;
    }
    .stMarkdown {
        color: #424242;
    }
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 4px;
        border: 1px solid #FFB74D;
    }
    [data-testid="stHeader"] {
        background: linear-gradient(135deg, #FF7043, #FFB74D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    </style>
""", unsafe_allow_html=True)

def read_data_file(file):
    """Read different types of data files"""
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file)
        else:
            raise ValueError(f"Unsupported file format: {file.name}")
    except Exception as e:
        st.error(f"Error reading file {file.name}: {str(e)}")
        return None
    """
    Prepare facility data by adding appropriate suffixes to column names
    source: 'MFL' or 'DHIS2'
    """
    renamed_df = facility_data.copy()
    suffix = f"_{source}"
    renamed_df.columns = [f"{col}{suffix}" for col in renamed_df.columns]
    return renamed_df

def process_map(shapefile_data, mfl_data, dhis2_data, config):
    """Process and create the map with the given configuration using Light Sand theme colors"""
    plt.style.use('seaborn-whitegrid')
    plt.rcParams.update({
        'figure.facecolor': '#FAFAFA',
        'axes.facecolor': '#FFFFFF',
        'figure.figsize': (15, 10)
    })
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
    st.title("Health Facility Distribution Map Generator")

    # Import required libraries for handling different file formats
    shp_file = st.file_uploader("Upload Shapefile (.shp)", type=["shp"])
    shx_file = st.file_uploader("Upload Shapefile Index (.shx)", type=["shx"])
    dbf_file = st.file_uploader("Upload Attribute Database (.dbf)", type=["dbf"])
    mfl_file = st.file_uploader("Upload MFL Data (.xlsx, .xls, .csv)", type=["xlsx", "xls", "csv"], key="mfl")
    dhis2_file = st.file_uploader("Upload DHIS2 Data (.xlsx, .xls, .csv)", type=["xlsx", "xls", "csv"], key="dhis2")

    # Process files if all are uploaded
    if all([shp_file, shx_file, dbf_file, mfl_file, dhis2_file]):
        try:
            # Read files using BytesIO for shapefiles
            import tempfile
            import os

            # Create a temporary directory
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Save shapefile components to temporary directory
                shp_path = os.path.join(tmp_dir, "temp.shp")
                shx_path = os.path.join(tmp_dir, "temp.shx")
                dbf_path = os.path.join(tmp_dir, "temp.dbf")
                
                # Write the uploaded files to temporary location
                with open(shp_path, 'wb') as f:
                    f.write(shp_file.getvalue())
                with open(shx_path, 'wb') as f:
                    f.write(shx_file.getvalue())
                with open(dbf_path, 'wb') as f:
                    f.write(dbf_file.getvalue())
                
                # Read the shapefile from temporary directory
                shapefile = gpd.read_file(shp_path)
            
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
