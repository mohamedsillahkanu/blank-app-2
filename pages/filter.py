import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# Set page config
st.set_page_config(layout="wide", page_title="Chiefdom Map Dashboard")

# App title
st.title("Chiefdom Map Dashboard")
st.markdown("Upload your Excel data to create an interactive map with the Chiefdom 2021 shapefile.")

# Load the shapefile directly
@st.cache_data
def load_chiefdom_shapefile():
    # Replace with your actual GitHub repo URL - this is a placeholder
    shapefile_url = "https://github.com/mohamedsillahkanu/blank-app-2/raw/30b91c6276a480fd7c2a3580c39a2d195c00ed86/Chiefdom%202021.shp"
    
    try:
        # For demonstration purposes - in production, use the BytesIO approach from the main app
        # This assumes the shapefile is public and accessible
        shapefile = gpd.read_file(shapefile_url)
        return shapefile
    except Exception as e:
        st.error(f"Error loading Chiefdom shapefile: {str(e)}")
        return None

# Load the shapefile on app startup
with st.spinner("Loading Chiefdom shapefile..."):
    gdf = load_chiefdom_shapefile()
    
    if gdf is not None:
        st.success("Chiefdom shapefile loaded successfully!")
        
        # Display shapefile info
        st.subheader("Shapefile Information")
        st.write(f"Number of features: {len(gdf)}")
        st.write(f"CRS: {gdf.crs}")
        
        # Show the column names
        st.subheader("Shapefile Columns")
        st.write(gdf.columns.tolist())
        
        # Excel file uploader
        st.subheader("Upload Excel Data")
        excel_file = st.file_uploader("Choose an Excel file to join with the Chiefdom data", type=['xlsx', 'xls'])
        
        if excel_file:
            # Load the Excel file
            df = pd.read_excel(excel_file)
            
            # Display Excel info
            st.subheader("Excel Data Information")
            st.write(f"Number of rows: {len(df)}")
            st.write(f"Columns: {df.columns.tolist()}")
            
            # Join configuration
            st.subheader("Join Configuration")
            col1, col2 = st.columns(2)
            
            with col1:
                excel_key = st.selectbox("Select Excel join column", options=df.columns.tolist())
            
            with col2:
                shape_key = st.selectbox("Select Shapefile join column", options=gdf.columns.tolist())
            
            # Join button
            if st.button("Join Data and Create Map"):
                # Convert join columns to strings for safer joining
                df[excel_key] = df[excel_key].astype(str)
                gdf[shape_key] = gdf[shape_key].astype(str)
                
                # Perform the join
                merged_gdf = gdf.merge(df, left_on=shape_key, right_on=excel_key, how='left')
                
                # Display the number of matches
                match_count = merged_gdf[~merged_gdf[excel_key].isna()].shape[0]
                st.write(f"Matched {match_count} out of {len(gdf)} features")
                
                # Identify numeric columns for choropleth
                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
                
                if numeric_cols:
                    # Choose column to visualize
                    color_col = st.selectbox("Select column to visualize", options=numeric_cols)
                    
                    # Create the map
                    st.subheader("Chiefdom Map")
                    
                    # Ensure the geodataframe is in the right projection
                    if merged_gdf.crs != "EPSG:4326":
                        merged_gdf = merged_gdf.to_crs(epsg=4326)
                    
                    # Create choropleth map
                    fig = px.choropleth_mapbox(
                        merged_gdf,
                        geojson=merged_gdf.geometry.__geo_interface__,
                        locations=merged_gdf.index,
                        color=color_col if color_col in merged_gdf.columns else None,
                        color_continuous_scale="Viridis",
                        mapbox_style="carto-positron",
                        zoom=6,
                        opacity=0.8,
                        labels={color_col: color_col}
                    )
                    
                    # Center map on data
                    center_lon = merged_gdf.geometry.centroid.x.mean()
                    center_lat = merged_gdf.geometry.centroid.y.mean()
                    fig.update_layout(
                        margin={"r":0,"t":0,"l":0,"b":0},
                        mapbox=dict(center=dict(lon=center_lon, lat=center_lat))
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No numeric columns found in the Excel data for visualization.")
    else:
        st.error("Failed to load the Chiefdom shapefile. Please check the URL or file path.")

st.markdown("---")
st.markdown("Chiefdom Map Dashboard | Built with Streamlit")
