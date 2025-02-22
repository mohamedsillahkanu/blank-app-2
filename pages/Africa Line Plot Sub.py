import streamlit as st
import geopandas as gpd
import rasterio
import rasterio.mask
import requests
import tempfile
import os
import gzip
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt

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
        # Save the .tif.gz file
        zipped_file_path = os.path.join(tmpdir, "chirps.tif.gz")
        with open(zipped_file_path, "wb") as f:
            f.write(response.content)

        # Decompress the .gz file to extract the .tif file
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
st.title("CHIRPS Rainfall Data Line Plot by Admin Levels")

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

# Multi-select for years and months
years = st.multiselect("Select Years", range(1981, 2025), default=[2020])
months = st.multiselect("Select Months", range(1, 13), default=[1, 2, 3])

if st.button("Generate Line Plot"):
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

        rainfall_data = []

        with st.spinner("Processing CHIRPS rainfall data..."):
            try:
                for year in years:
                    for month in months:
                        processed_gdf = process_chirps_data(gdf.copy(), year, month)
                        processed_gdf["Month"] = month
                        processed_gdf["Year"] = year
                        rainfall_data.append(processed_gdf)
                st.success("CHIRPS rainfall data processed successfully!")
            except Exception as e:
                st.error(f"Error processing CHIRPS data: {str(e)}")
                st.stop()

        # Combine all rainfall data into a single GeoDataFrame
        combined_gdf = gpd.GeoDataFrame(pd.concat(rainfall_data, ignore_index=True))

        # Preview the DataFrame in the app
        st.write("### Preview of Rainfall Data")
        preview_df = combined_gdf.drop(columns=["geometry"], errors="ignore")
        st.dataframe(preview_df)

        # Define the column for subcategory plotting
        subcategory_column = f"NAME_{admin_level}"

        # Generate line plots for each subcategory
        if subcategory_column in combined_gdf.columns:
            unique_names = combined_gdf[subcategory_column].unique()
            for subcategory in unique_names:
                st.write(f"### Rainfall Line Plot for {subcategory}")

                subcategory_df = combined_gdf[combined_gdf[subcategory_column] == subcategory]
                df = subcategory_df[["Year", "Month", "mean_rain"]].groupby(["Year", "Month"]).mean().reset_index()

                fig, ax = plt.subplots(figsize=(12, 6))
                for year in df["Year"].unique():
                    year_data = df[df["Year"] == year]
                    ax.plot(
                        year_data["Month"],
                        year_data["mean_rain"],
                        marker="o",
                        label=f"Year {year}"
                    )
                ax.set_title(f"Mean Rainfall for {subcategory} (Admin Level {admin_level})", fontsize=16)
                ax.set_xlabel("Month")
                ax.set_ylabel("Mean Rainfall (mm)")
                ax.legend(title="Year")
                ax.grid()

                st.pyplot(fig)
        else:
            st.warning(f"No '{subcategory_column}' column found in the shapefile to generate subcategory plots.")

        # Export all data as CSV
        csv_data = BytesIO()
        combined_gdf.to_csv(csv_data, index=False)
        st.download_button(
            label="Download Full Rainfall Data as CSV",
            data=csv_data.getvalue(),
            file_name=f"rainfall_data_{country_code}_admin{admin_level}.csv",
            mime="text/csv"
        )
