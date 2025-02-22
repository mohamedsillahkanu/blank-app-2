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
from matplotlib import pyplot as plt

# Function to check if a file exists on GitHub
def check_file_exists(url):
    response = requests.head(url)
    return response.status_code == 200

# Function to download and load shapefiles from GitHub
def download_shapefile(github_link, country_code, admin_level):
    with tempfile.TemporaryDirectory() as tmpdir:
        file_base = f"gadm41_{country_code}_{admin_level}"
        components = ['.shp', '.shx', '.dbf']

        for ext in components:
            url = f"{github_link}/{file_base}{ext}"
            response = requests.get(url)
            if response.status_code == 200:
                file_path = os.path.join(tmpdir, f"{file_base}{ext}")
                with open(file_path, "wb") as f:
                    f.write(response.content)
            else:
                raise FileNotFoundError(f"File {file_base}{ext} not found at {url}.")

        shapefile_path = os.path.join(tmpdir, f"{file_base}.shp")
        gdf = gpd.read_file(shapefile_path)
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    return gdf

# Function to process CHIRPS rainfall data
def process_chirps_data(gdf, year, month):
    link = f"https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_monthly/tifs/chirps-v2.0.{year}.{month:02d}.tif.gz"
    response = requests.get(link)

    with tempfile.TemporaryDirectory() as tmpdir:
        zipped_file_path = os.path.join(tmpdir, "chirps.tif.gz")
        with open(zipped_file_path, "wb") as f:
            f.write(response.content)

        unzipped_file_path = os.path.join(tmpdir, "chirps.tif")
        with gzip.open(zipped_file_path, "rb") as gz:
            with open(unzipped_file_path, "wb") as tif:
                tif.write(gz.read())

        with rasterio.open(unzipped_file_path) as src:
            gdf = gdf.to_crs(src.crs)
            mean_rains = []
            for geom in gdf.geometry:
                masked_data, _ = rasterio.mask.mask(src, [geom], crop=True)
                masked_data = masked_data.flatten()
                masked_data = masked_data[masked_data != src.nodata]
                mean_rains.append(masked_data.mean())

            gdf["mean_rain"] = mean_rains
    return gdf

# Streamlit app layout
st.title("CHIRPS Rainfall Data Analysis and Map Generation")

# Define GitHub links and country codes
github_links = {
    "Sierra Leone": {
        "link": "https://raw.githubusercontent.com/mohamedsillahkanu/si/554bb45b390b5b2fb1de04540f1c8202a3510456/shapefiles/Sierra%20Leone",
        "code": "SLE"
    },
    "Guinea": {
        "link": "https://raw.githubusercontent.com/mohamedsillahkanu/si/6d9453ea42ce867562ee71a3f59d8aa5dcc23b7b/shapefiles/Guinea",
        "code": "GIN"
    }
}

# Country and admin level selection
country = st.selectbox("Select Country", list(github_links.keys()))
admin_level = st.selectbox("Select Admin Level", [1, 2, 3])

# Year selection
year = st.selectbox("Select Year", range(1981, 2025))

# Multiselect for months
months = st.multiselect("Select Months", list(range(1, 13)), default=[1])

# Generate button
generate = st.button("Generate Maps")

if generate:
    github_link = github_links[country]["link"]
    country_code = github_links[country]["code"]

    file_base = f"gadm41_{country_code}_{admin_level}"
    shapefile_url = f"{github_link}/{file_base}.shp"

    if check_file_exists(shapefile_url):
        with st.spinner("Downloading and loading shapefile..."):
            try:
                gdf = download_shapefile(github_link, country_code, admin_level)
                st.success(f"{country} Admin Level {admin_level} shapefile loaded successfully!")
            except FileNotFoundError as e:
                st.error(str(e))
                st.stop()

        with st.spinner("Processing CHIRPS rainfall data..."):
            try:
                # Process CHIRPS data for selected months
                figs = []
                for month in months:
                    processed_gdf = process_chirps_data(gdf.copy(), year, month)
                    figs.append((month, processed_gdf))
                st.success("CHIRPS rainfall data processed successfully!")
            except Exception as e:
                st.error(f"Error processing CHIRPS data: {str(e)}")
                st.stop()

        # Create subplots
        num_months = len(months)
        num_cols = 3
        num_rows = math.ceil(num_months / num_cols)
        fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 5 * num_rows))
        axes = axes.flatten()

        for i, (month, processed_gdf) in enumerate(figs):
            ax = axes[i]
            processed_gdf.plot(
                column="mean_rain",
                ax=ax,
                legend=True,
                cmap="Blues",
                edgecolor="black",
                legend_kwds={"shrink": 0.5},
            )
            ax.set_title(f"{country} - {year}-{month:02d}")
            ax.set_axis_off()

        # Remove empty subplots
        for j in range(len(months), len(axes)):
            fig.delaxes(axes[j])

        st.pyplot(fig)
