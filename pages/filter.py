import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import requests
import io
import json
from urllib.parse import urlparse

st.set_page_config(layout="wide", page_title="Interactive Map Dashboard")

# Custom CSS for better styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    .stButton button {
        width: 100%;
    }
    h1, h2, h3 {
        margin-top: 0;
    }
    .filter-section {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.title("Interactive Geospatial Dashboard")
st.markdown("Upload your Excel data and select GitHub-hosted shapefiles to create an interactive map visualization.")

# Function to load GeoJSON from GitHub
@st.cache_data
def load_geojson_from_github(github_url):
    """
    Load GeoJSON from a GitHub URL
    
    Parameters:
    github_url (str): URL to the GeoJSON file on GitHub
    
    Returns:
    geopandas.GeoDataFrame: Loaded geodataframe
    """
    # Convert GitHub URL to raw content URL if needed
    parsed_url = urlparse(github_url)
    if parsed_url.netloc == 'github.com':
        # Convert github.com URL to raw.githubusercontent.com
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) >= 3:
            user = path_parts[0]
            repo = path_parts[1]
            branch = 'main' if path_parts[2] == 'blob' and path_parts[3] == 'main' else path_parts[3]
            file_path = '/'.join(path_parts[4:]) if path_parts[2] == 'blob' else '/'.join(path_parts[4:])
            raw_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"
        else:
            raise ValueError("Invalid GitHub URL format. Please provide a URL to a specific file.")
    else:
        # Assume it's already a raw URL
        raw_url = github_url

    try:
        response = requests.get(raw_url)
        response.raise_for_status()  # Raise an error for bad responses
        
        # Load the GeoJSON content
        geojson = json.loads(response.content)
        gdf = gpd.GeoDataFrame.from_features(geojson["features"])
        
        # Ensure it has a CRS
        if gdf.crs is None:
            gdf = gdf.set_crs(epsg=4326)  # Assume WGS84 if not specified
            
        return gdf
    except Exception as e:
        st.error(f"Error loading GeoJSON from {raw_url}: {str(e)}")
        return None

# Predefined shapefile options
shapefile_options = {
    "US States": "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
    "World Countries": "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json",
    "US Counties": "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
}

# Custom GitHub URL option
custom_github_url = "Custom GitHub URL"
shapefile_options[custom_github_url] = None

# File upload section
st.header("Data Upload")
col1, col2 = st.columns(2)

# Excel file uploader
with col1:
    st.subheader("Upload Excel Data")
    excel_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])
    if excel_file:
        st.success(f"Successfully uploaded: {excel_file.name}")

# GitHub shapefile selector
with col2:
    st.subheader("Select Shapefile")
    selected_shapefile = st.selectbox(
        "Choose a predefined shapefile or enter custom URL",
        options=list(shapefile_options.keys())
    )
    
    if selected_shapefile == custom_github_url:
        github_url = st.text_input("Enter GitHub URL to GeoJSON file")
    else:
        github_url = shapefile_options[selected_shapefile]
        st.info(f"Using: {github_url}")

# Process the uploaded files
if excel_file and github_url:
    # Create a progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Process Excel file
        status_text.text("Loading Excel data...")
        df = pd.read_excel(excel_file)
        progress_bar.progress(25)
        
        # Load GeoJSON from GitHub
        status_text.text("Loading shapefile from GitHub...")
        gdf = load_geojson_from_github(github_url)
        
        if gdf is None:
            st.error("Failed to load GeoJSON from the provided URL.")
        else:
            progress_bar.progress(50)
            
            # Display data info
            status_text.text("Analyzing data...")
            
            # Create two columns: one for dataset info and one for map
            info_col, map_col = st.columns([1, 2])
            
            with info_col:
                st.subheader("Dataset Information")
                st.write(f"Excel Data: {df.shape[0]} rows, {df.shape[1]} columns")
                st.write(f"Shapefile: {gdf.shape[0]} features")
                
                # Show Excel columns
                st.subheader("Excel Data Columns")
                st.dataframe(pd.DataFrame({
                    'Column': df.columns.tolist(),
                    'Type': df.dtypes.astype(str).tolist()
                }).reset_index(drop=True), height=200)
                
                # Show Shapefile columns
                st.subheader("Shapefile Columns")
                st.dataframe(pd.DataFrame({
                    'Column': gdf.columns.tolist(),
                    'Type': gdf.dtypes.astype(str).tolist()
                }).reset_index(drop=True), height=200)
                
                # Join key selection
                st.subheader("Join Configuration")
                excel_key = st.selectbox("Select Excel join column", options=df.columns.tolist())
                shape_key = st.selectbox("Select Shapefile join column", options=gdf.columns.tolist())
                
                join_button = st.button("Join Data and Create Map")
            
            progress_bar.progress(75)
            
            if join_button:
                try:
                    # Perform the join
                    status_text.text("Joining data...")
                    
                    # Make sure key columns match type
                    if df[excel_key].dtype != gdf[shape_key].dtype:
                        # Try to convert them to strings for joining
                        df[excel_key] = df[excel_key].astype(str)
                        gdf[shape_key] = gdf[shape_key].astype(str)
                    
                    # Merge the dataframes
                    merged_gdf = gdf.merge(df, left_on=shape_key, right_on=excel_key, how='left')
                    
                    # Create filter section
                    st.header("Filter Options")
                    filter_cols = st.columns(3)
                    
                    # Identify numeric and categorical columns
                    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
                    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                    
                    filters = {}
                    
                    # Create filters dynamically
                    with filter_cols[0]:
                        if numeric_cols:
                            st.subheader("Numeric Filters")
                            for col in numeric_cols[:3]:  # Limit to first 3 for simplicity
                                min_val = float(df[col].min())
                                max_val = float(df[col].max())
                                filters[col] = st.slider(
                                    f"Filter by {col}", 
                                    min_value=min_val,
                                    max_value=max_val,
                                    value=(min_val, max_val)
                                )
                    
                    with filter_cols[1]:
                        if cat_cols:
                            st.subheader("Categorical Filters")
                            for col in cat_cols[:3]:  # Limit to first 3 for simplicity
                                unique_vals = df[col].dropna().unique().tolist()
                                filters[col] = st.multiselect(
                                    f"Select {col}",
                                    options=unique_vals,
                                    default=unique_vals
                                )
                    
                    with filter_cols[2]:
                        st.subheader("Map Options")
                        color_by = st.selectbox(
                            "Color by",
                            options=numeric_cols,
                            index=0 if numeric_cols else None
                        )
                        color_scheme = st.selectbox(
                            "Color scheme",
                            options=['Viridis', 'Plasma', 'Inferno', 'Magma', 'Cividis', 'Turbo'],
                            index=0
                        )
                    
                    # Apply filters to create filtered DataFrame
                    filtered_df = df.copy()
                    
                    for col, filter_val in filters.items():
                        if col in numeric_cols:
                            filtered_df = filtered_df[(filtered_df[col] >= filter_val[0]) & 
                                                      (filtered_df[col] <= filter_val[1])]
                        elif col in cat_cols and filter_val:  # Check if any categories selected
                            filtered_df = filtered_df[filtered_df[col].isin(filter_val)]
                    
                    # Create filtered geodataframe
                    filtered_gdf = gdf.merge(filtered_df, left_on=shape_key, right_on=excel_key, how='inner')
                    
                    # Display the map
                    with map_col:
                        st.subheader("Interactive Map")
                        
                        if len(filtered_gdf) > 0:
                            # Create choropleth map
                            if color_by in filtered_gdf.columns:
                                # Convert to WGS84 for Plotly
                                if filtered_gdf.crs != "EPSG:4326":
                                    filtered_gdf = filtered_gdf.to_crs(epsg=4326)
                                
                                # Create the figure
                                fig = px.choropleth_mapbox(
                                    filtered_gdf,
                                    geojson=filtered_gdf.geometry.__geo_interface__,
                                    locations=filtered_gdf.index,
                                    color=color_by,
                                    color_continuous_scale=color_scheme.lower(),
                                    mapbox_style="carto-positron",
                                    zoom=3,
                                    opacity=0.8,
                                    labels={color_by: color_by}
                                )
                                
                                # Try to center map on data
                                try:
                                    center_lon = filtered_gdf.geometry.centroid.x.mean()
                                    center_lat = filtered_gdf.geometry.centroid.y.mean()
                                    fig.update_layout(
                                        margin={"r":0,"t":0,"l":0,"b":0},
                                        mapbox=dict(center=dict(lon=center_lon, lat=center_lat))
                                    )
                                except:
                                    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Display summary table
                                st.subheader("Filtered Data Preview")
                                st.dataframe(filtered_df.head(10), height=200)
                                
                                # Show basic statistics for the filtered data
                                st.subheader("Summary Statistics")
                                st.dataframe(filtered_df.describe())
                            else:
                                st.error(f"Column '{color_by}' not found in the joined data.")
                        else:
                            st.warning("No data matches the current filters. Please adjust your filter criteria.")
                    
                    progress_bar.progress(100)
                    status_text.text("Completed!")
                    
                except Exception as e:
                    st.error(f"Error joining data: {str(e)}")
            else:
                with map_col:
                    st.info("Configure the join columns and click 'Join Data and Create Map' to generate the visualization.")
    
    except Exception as e:
        st.error(f"Error processing files: {str(e)}")
        progress_bar.empty()
        status_text.empty()

else:
    st.info("Please upload an Excel file and select a shapefile to proceed.")

# Add instructions at the bottom
with st.expander("How to Use This Dashboard"):
    st.markdown("""
    ## Instructions
    
    1. **Upload Data Files**:
       - Upload an Excel file (.xlsx or .xls) containing your tabular data
       - Select a predefined shapefile from the dropdown or enter a custom GitHub URL
    
    2. **Configure Join**:
       - Select the column from your Excel data to join with the shapefile
       - Select the corresponding column from the shapefile
       - Click "Join Data and Create Map" to perform the join
    
    3. **Filter Data**:
       - Use the filter controls to subset the data
       - The map will automatically update based on your filter selections
    
    4. **Customize Map**:
       - Select a column to color the map by
       - Choose a color scheme for better visualization
    
    ## Adding Custom Shapefiles
    
    To use a custom shapefile, select "Custom GitHub URL" and enter the URL to a GeoJSON file hosted on GitHub.
    
    For example:
    - US States: https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json
    - World Countries: https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json
    
    If you provide a regular GitHub URL, the application will attempt to convert it to a raw content URL.
    """)

# Add option to directly input GeoJSON
st.header("Advanced: Direct GeoJSON Input")
with st.expander("Paste GeoJSON directly"):
    geojson_text = st.text_area("Paste GeoJSON content here", height=200)
    if st.button("Load GeoJSON"):
        if geojson_text:
            try:
                geojson_data = json.loads(geojson_text)
                direct_gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
                st.success(f"Successfully loaded GeoJSON with {len(direct_gdf)} features")
                st.write("Preview:")
                st.dataframe(direct_gdf.head())
            except Exception as e:
                st.error(f"Error loading GeoJSON: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Interactive Geospatial Dashboard | Built with Streamlit")
