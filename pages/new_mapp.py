import streamlit as st
import geopandas as gpd
import rasterio
import rasterio.mask
import requests
import tempfile
import os
import gzip
from io import BytesIO
import math
import numpy as np
from matplotlib import pyplot as plt
import zipfile
import pandas as pd
import time

# Set page config
st.set_page_config(
    page_title="CHIRPS Rainfall Analysis",
    page_icon="🌧️",
    layout="wide"
)

# Add caching for better performance
@st.cache_data
def check_file_exists(url):
    """Check if a file exists on GitHub with timeout"""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

@st.cache_data
def download_shapefile_from_gadm(country_code, admin_level):
    """Download and load shapefiles directly from GADM website"""
    gadm_url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_{country_code}_shp.zip"
    
    try:
        # Download the zip file
        response = requests.get(gadm_url, timeout=60, stream=True)
        response.raise_for_status()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save zip file
            zip_path = os.path.join(tmpdir, f"gadm41_{country_code}.zip")
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract zip file
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)
            
            # Find the correct shapefile for the admin level
            shapefile_name = f"gadm41_{country_code}_{admin_level}.shp"
            shapefile_path = os.path.join(tmpdir, shapefile_name)
            
            if not os.path.exists(shapefile_path):
                available_files = [f for f in os.listdir(tmpdir) if f.endswith('.shp')]
                raise FileNotFoundError(f"Admin level {admin_level} not found. Available levels: {available_files}")
            
            # Load the shapefile
            gdf = gpd.read_file(shapefile_path)
            
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to download from GADM: {str(e)}")
    except zipfile.BadZipFile:
        raise ValueError("Downloaded file is not a valid zip file")
    except Exception as e:
        raise ValueError(f"Failed to process shapefile: {str(e)}")
    
    # Ensure CRS is set
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    
    return gdf

def validate_chirps_date(year, month):
    """Validate if CHIRPS data is available for the given date"""
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    if year < 1981:
        return False, "CHIRPS data starts from 1981"
    if year > current_year or (year == current_year and month > current_month - 2):
        return False, "CHIRPS data has ~2 month delay"
    return True, ""

@st.cache_data
def process_chirps_data(gdf, year, month):
    """Process CHIRPS rainfall data with improved error handling"""
    
    # Validate date first
    is_valid, error_msg = validate_chirps_date(year, month)
    if not is_valid:
        raise ValueError(error_msg)
    
    link = f"https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_monthly/tifs/chirps-v2.0.{year}.{month:02d}.tif.gz"
    
    try:
        response = requests.get(link, timeout=60, stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to download CHIRPS data: {str(e)}")

    with tempfile.TemporaryDirectory() as tmpdir:
        zipped_file_path = os.path.join(tmpdir, "chirps.tif.gz")
        
        # Download with progress
        with open(zipped_file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        unzipped_file_path = os.path.join(tmpdir, "chirps.tif")
        
        try:
            with gzip.open(zipped_file_path, "rb") as gz:
                with open(unzipped_file_path, "wb") as tif:
                    tif.write(gz.read())
        except gzip.BadGzipFile:
            raise ValueError("Downloaded file is not a valid gzip file")

        try:
            with rasterio.open(unzipped_file_path) as src:
                # Reproject geodataframe to match raster CRS
                gdf_reproj = gdf.to_crs(src.crs)
                
                mean_rains = []
                valid_pixels_count = []
                
                for idx, geom in enumerate(gdf_reproj.geometry):
                    try:
                        masked_data, _ = rasterio.mask.mask(src, [geom], crop=True, nodata=src.nodata)
                        masked_data = masked_data.flatten()
                        
                        # Filter out nodata values
                        valid_data = masked_data[masked_data != src.nodata]
                        valid_data = valid_data[~np.isnan(valid_data)]
                        
                        if len(valid_data) > 0:
                            mean_rains.append(np.mean(valid_data))
                            valid_pixels_count.append(len(valid_data))
                        else:
                            mean_rains.append(np.nan)
                            valid_pixels_count.append(0)
                    except Exception as e:
                        st.warning(f"Error processing geometry {idx}: {str(e)}")
                        mean_rains.append(np.nan)
                        valid_pixels_count.append(0)

                gdf["mean_rain"] = mean_rains
                gdf["valid_pixels"] = valid_pixels_count
        except rasterio.errors.RasterioIOError as e:
            raise ValueError(f"Failed to process raster file: {str(e)}")
    
    return gdf

# Main app layout
st.title("🌧️ CHIRPS Rainfall Data Analysis and Map Generation")
st.markdown("*Analyze seasonal rainfall patterns for malaria intervention planning*")

# Sidebar for controls
with st.sidebar:
    st.header("Analysis Parameters")
    
    # Define country codes (ISO 3166-1 alpha-3)
    country_options = {
        "Sierra Leone": "SLE",
        "Guinea": "GIN", 
        "Mali": "MLI",
        "Burkina Faso": "BFA",
        "Niger": "NER",
        "Ghana": "GHA",
        "Ivory Coast": "CIV",
        "Liberia": "LBR",
        "Senegal": "SEN",
        "Guinea-Bissau": "GNB",
        "Mauritania": "MRT",
        "Nigeria": "NGA",
        "Benin": "BEN",
        "Togo": "TGO",
        "Chad": "TCD",
        "Cameroon": "CMR",
        "Central African Republic": "CAF",
        "Gabon": "GAB",
        "Equatorial Guinea": "GNQ",
        "Republic of the Congo": "COG",
        "Democratic Republic of the Congo": "COD",
        "Angola": "AGO",
        "Zambia": "ZMB",
        "Kenya": "KEN",
        "Tanzania": "TZA",
        "Uganda": "UGA",
        "Rwanda": "RWA",
        "Burundi": "BDI",
        "Ethiopia": "ETH",
        "South Sudan": "SSD",
        "Sudan": "SDN",
        "Madagascar": "MDG",
        "Mozambique": "MOZ",
        "Malawi": "MWI",
        "Zimbabwe": "ZWE",
        "Botswana": "BWA",
        "Namibia": "NAM",
        "South Africa": "ZAF"
    }

    # Country and admin level selection
    country = st.selectbox("🌍 Select Country", list(country_options.keys()), 
                          help="Select any African country")
    admin_level = st.selectbox("🏛️ Administrative Level", [0, 1, 2, 3, 4], 
                              help="0=Country, 1=Regions, 2=Districts, 3=Communes, 4=Localities")
    
    # Show admin level description
    level_descriptions = {
        0: "Country boundary",
        1: "First-level admin (regions/states)",
        2: "Second-level admin (districts/provinces)", 
        3: "Third-level admin (communes/counties)",
        4: "Fourth-level admin (localities/wards)"
    }
    st.caption(f"Level {admin_level}: {level_descriptions.get(admin_level, 'Administrative division')}")

    # Date selection with validation
    current_year = datetime.now().year
    year = st.selectbox("📅 Select Year", range(1981, current_year + 1), index=current_year-1981-2)

    # Month selection with names
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    
    selected_months = st.multiselect(
        "📊 Select Months", 
        options=list(month_names.keys()),
        format_func=lambda x: month_names[x],
        default=[6, 7, 8, 9],  # Peak malaria season
        help="Select months for analysis (typically Jun-Sep for West Africa)"
    )

    # Analysis options
    st.subheader("Display Options")
    show_statistics = st.checkbox("📈 Show Statistics", value=True)
    color_scheme = st.selectbox("🎨 Color Scheme", ["Blues", "viridis", "plasma", "YlOrRd"])

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    if st.button("🔄 Generate Analysis", type="primary", use_container_width=True):
        if not selected_months:
            st.error("Please select at least one month for analysis.")
        else:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Download shapefile from GADM
                status_text.text("🔍 Checking GADM database...")
                progress_bar.progress(10)
                
                country_code = country_options[country]
                
                status_text.text(f"📥 Downloading {country} shapefile from GADM...")
                progress_bar.progress(20)
                
                gdf = download_shapefile_from_gadm(country_code, admin_level)
                st.success(f"✅ {country} Admin Level {admin_level} shapefile loaded ({len(gdf)} features)")
                
                # Show some basic info about the shapefile
                if hasattr(gdf, 'NAME_1') and admin_level >= 1:
                    st.info(f"📋 Contains regions: {', '.join(gdf['NAME_1'].unique()[:5])}{'...' if len(gdf['NAME_1'].unique()) > 5 else ''}")
                elif hasattr(gdf, 'NAME_0'):
                    st.info(f"📋 Country: {gdf['NAME_0'].iloc[0]}")
                
                # Step 2: Process CHIRPS data
                status_text.text("🌧️ Processing CHIRPS rainfall data...")
                processed_data = []
                
                for i, month in enumerate(selected_months):
                    progress = 20 + (60 * (i + 1) / len(selected_months))
                    progress_bar.progress(int(progress))
                    status_text.text(f"🌧️ Processing {month_names[month]} {year}...")
                    
                    try:
                        processed_gdf = process_chirps_data(gdf.copy(), year, month)
                        processed_data.append((month, processed_gdf))
                    except Exception as e:
                        st.error(f"❌ Error processing {month_names[month]}: {str(e)}")
                        continue

                if not processed_data:
                    st.error("❌ No data could be processed for the selected months.")
                    st.stop()

                # Step 3: Generate visualizations
                status_text.text("📊 Generating maps...")
                progress_bar.progress(90)
                
                # Create subplots
                num_months = len(processed_data)
                if num_months == 1:
                    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
                    axes = [ax]
                else:
                    num_cols = min(3, num_months)
                    num_rows = math.ceil(num_months / num_cols)
                    fig, axes = plt.subplots(num_rows, num_cols, figsize=(5 * num_cols, 4 * num_rows))
                    if num_months > 1:
                        axes = axes.flatten() if num_rows > 1 else [axes] if num_cols == 1 else axes

                # Plot each month
                all_values = []
                for month, processed_gdf in processed_data:
                    valid_values = processed_gdf['mean_rain'].dropna()
                    all_values.extend(valid_values)

                if all_values:
                    vmin, vmax = np.percentile(all_values, [5, 95])  # Use percentiles for better visualization
                else:
                    vmin, vmax = 0, 100

                for i, (month, processed_gdf) in enumerate(processed_data):
                    ax = axes[i] if len(axes) > 1 else axes[0]
                    
                    # Handle missing data
                    plot_data = processed_gdf.copy()
                    if plot_data['mean_rain'].isna().all():
                        ax.text(0.5, 0.5, f'No data available\nfor {month_names[month]} {year}', 
                               ha='center', va='center', transform=ax.transAxes)
                        ax.set_title(f"{country} - {month_names[month]} {year}")
                        ax.set_axis_off()
                        continue
                    
                    # Create the plot
                    plot_data.plot(
                        column="mean_rain",
                        ax=ax,
                        legend=True,
                        cmap=color_scheme,
                        edgecolor="white",
                        linewidth=0.5,
                        legend_kwds={"shrink": 0.6, "label": "Rainfall (mm)"},
                        vmin=vmin,
                        vmax=vmax,
                        missing_kwds={"color": "lightgray", "label": "No data"}
                    )
                    ax.set_title(f"{country} - {month_names[month]} {year}", fontweight='bold')
                    ax.set_axis_off()

                # Remove empty subplots
                if len(processed_data) < len(axes):
                    for j in range(len(processed_data), len(axes)):
                        fig.delaxes(axes[j])

                plt.tight_layout()
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                st.pyplot(fig)

                # Show statistics if requested
                if show_statistics:
                    st.subheader("📊 Rainfall Statistics")
                    
                    stats_data = []
                    for month, processed_gdf in processed_data:
                        valid_data = processed_gdf['mean_rain'].dropna()
                        if len(valid_data) > 0:
                            stats_data.append({
                                'Month': month_names[month],
                                'Mean (mm)': f"{valid_data.mean():.1f}",
                                'Std (mm)': f"{valid_data.std():.1f}",
                                'Min (mm)': f"{valid_data.min():.1f}",
                                'Max (mm)': f"{valid_data.max():.1f}",
                                'Valid Areas': len(valid_data)
                            })
                    
                    if stats_data:
                        stats_df = pd.DataFrame(stats_data)
                        st.dataframe(stats_df, use_container_width=True)

            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                st.error("Please try again or contact support if the issue persists.")

with col2:
    st.subheader("ℹ️ About This Tool")
    st.markdown("""
    **CHIRPS Rainfall Analysis Tool**
    
    This tool analyzes satellite-derived rainfall data for malaria intervention planning in West Africa.
    
    **Data Sources:**
    - **CHIRPS**: Climate Hazards Group InfraRed Precipitation with Station data
    - **GADM**: Global Administrative Areas database (official country boundaries)
    
    **Coverage:**
    - All African countries supported
    - Administrative levels 0-4 (where available)
    - Monthly rainfall data from 1981-present
    
    **Use Cases:**
    - Seasonal Malaria Chemoprevention planning
    - Intervention targeting
    - Climate-informed public health decisions
    
    **Technical Notes:**
    - Data resolution: ~5km
    - Temporal coverage: 1981-present
    - Update frequency: Monthly (~2 month delay)
    """)
    
    with st.expander("📋 Usage Tips"):
        st.markdown("""
        - **Peak season**: Jun-Sep for West Africa
        - **Admin levels**: Use level 2 for districts
        - **Color schemes**: Blues for rainfall, viridis for diversity
        - **Performance**: Fewer months = faster processing
        """)
    
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        - **Slow loading**: Try fewer months or lower admin level
        - **No data**: Check if recent months (data has ~2 month delay)
        - **Error messages**: Often due to network connectivity
        """)

# Footer
st.markdown("---")
st.markdown("*Built for malaria researchers and public health professionals*")
st.markdown("**Contact**: Mohamed Sillah Kanu | Northwestern University Malaria Modeling Team")
