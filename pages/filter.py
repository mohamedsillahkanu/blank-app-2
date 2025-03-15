import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# Set page config
st.set_page_config(layout="wide", page_title="Chiefdom Map Dashboard")

# App title and description
st.title("Chiefdom Map Dashboard")
st.markdown("""
This dashboard visualizes Chiefdom data using the Chiefdom 2021 shapefile. 
Upload your Excel data to create an interactive map with dynamic filtering capabilities.

The dashboard will automatically join your data with the shapefile using FIRST_DNAM (Excel) and FIRST_CHIE (Shapefile) columns.
""")

# Load the shapefile directly
@st.cache_data
def load_chiefdom_shapefile():
    # Replace with your actual GitHub repo URL - this is a placeholder
    shapefile_url = "https://raw.githubusercontent.com/yourusername/yourrepository/main/Chiefdom%202021.shp"
    
    try:
        # For demonstration purposes - in production, use the BytesIO approach from the main app
        # This assumes the shapefile is public and accessible
        shapefile = gpd.read_file(shapefile_url)
        return shapefile
    except Exception as e:
        st.error(f"Error loading Chiefdom shapefile: {str(e)}")
        return None

        # Load the shapefile on app startup with a spinner for better UX
with st.spinner("Loading Chiefdom shapefile..."):
    gdf = load_chiefdom_shapefile()
    
    if gdf is not None:
        st.success("Chiefdom shapefile loaded successfully!")
        
        # Create tabs for better organization
        main_tab, info_tab = st.tabs(["Dashboard", "Shapefile Information"])
        
        with info_tab:
            # Display shapefile info
            st.subheader("Shapefile Information")
            st.write(f"Number of features: {len(gdf)}")
            st.write(f"CRS: {gdf.crs}")
            
            # Show the column names and sample values
            st.subheader("Shapefile Columns")
            
            # Create a more informative dataframe with column names and sample values
            sample_values = []
            for col in gdf.columns:
                if col != 'geometry':  # Skip the geometry column
                    sample_values.append({
                        'Column': col,
                        'Type': str(gdf[col].dtype),
                        'Sample Value': str(gdf[col].iloc[0]) if len(gdf) > 0 else 'N/A'
                    })
            
            sample_df = pd.DataFrame(sample_values)
            st.dataframe(sample_df)
            
        with main_tab:
        
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
            
            # Use predefined join keys
            st.subheader("Join Configuration")
            
            # Check if the expected columns exist
            excel_cols = df.columns.tolist()
            shape_cols = gdf.columns.tolist()
            
            if 'FIRST_DNAM' in excel_cols:
                excel_key = 'FIRST_DNAM'
                st.success(f"Using 'FIRST_DNAM' from Excel data as join key")
            else:
                excel_key = st.selectbox("Excel column 'FIRST_DNAM' not found. Select alternative join column:", 
                                       options=excel_cols)
            
            if 'FIRST_CHIE' in shape_cols:
                shape_key = 'FIRST_CHIE'
                st.success(f"Using 'FIRST_CHIE' from shapefile as join key")
            else:
                shape_key = st.selectbox("Shapefile column 'FIRST_CHIE' not found. Select alternative join column:", 
                                       options=shape_cols)
            
            # Join button
            if st.button("Join Data and Create Map"):
                # Convert join columns to strings for safer joining
                df[excel_key] = df[excel_key].astype(str)
                gdf[shape_key] = gdf[shape_key].astype(str)
                
                # Perform the join
                merged_gdf = gdf.merge(df, left_on=shape_key, right_on=excel_key, how='left')
                
                # Display only the number of matches without showing the dataframe
                match_count = merged_gdf[~merged_gdf[excel_key].isna()].shape[0]
                st.write(f"Matched {match_count} out of {len(gdf)} features")
                
                # Create filter options
                st.subheader("Filter Options")
                
                # Identify numeric and categorical columns for filtering
                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
                cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                
                # Create layout for filters
                filter_col1, filter_col2 = st.columns(2)
                
                # Add numeric filters
                with filter_col1:
                    numeric_filters = {}
                    if numeric_cols:
                        for col in numeric_cols[:3]:  # Limit to first 3 for simplicity
                            if col in df.columns:
                                min_val = float(df[col].min())
                                max_val = float(df[col].max())
                                numeric_filters[col] = st.slider(
                                    f"Filter by {col}", 
                                    min_value=min_val,
                                    max_value=max_val,
                                    value=(min_val, max_val)
                                )
                
                # Add categorical filters
                with filter_col2:
                    cat_filters = {}
                    if cat_cols:
                        for col in cat_cols[:3]:  # Limit to first 3 for simplicity
                            if col in df.columns and col != excel_key:  # Skip join key
                                unique_vals = df[col].dropna().unique().tolist()
                                cat_filters[col] = st.multiselect(
                                    f"Select {col}",
                                    options=unique_vals,
                                    default=unique_vals
                                )
                
                # Apply filters to create filtered DataFrame
                filtered_df = df.copy()
                
                # Apply numeric filters
                for col, filter_val in numeric_filters.items():
                    filtered_df = filtered_df[(filtered_df[col] >= filter_val[0]) & 
                                            (filtered_df[col] <= filter_val[1])]
                
                # Apply categorical filters
                for col, filter_val in cat_filters.items():
                    if filter_val:  # Only filter if values are selected
                        filtered_df = filtered_df[filtered_df[col].isin(filter_val)]
                
                # Re-merge with filtered data
                filtered_gdf = gdf.merge(filtered_df, left_on=shape_key, right_on=excel_key, how='inner')
                
                # Continue with visualization
                if numeric_cols:
                    # Choose column to visualize
                    color_col = st.selectbox("Select column to visualize", options=numeric_cols)
                    
                    # Choose color scheme
                    color_schemes = ["Viridis", "Plasma", "Inferno", "Magma", "Cividis", "Blues", "Greens", "Reds", "YlOrRd", "YlGnBu"]
                    color_scheme = st.selectbox("Select color scheme", options=color_schemes)
                    
                    # Create the map
                    st.subheader("Chiefdom Map")
                    
                    # Display number of features on the map
                    st.write(f"Showing {len(filtered_gdf)} chiefdoms based on current filters")
                    
                    # Ensure the geodataframe is in the right projection
                    if filtered_gdf.crs != "EPSG:4326":
                        filtered_gdf = filtered_gdf.to_crs(epsg=4326)
                    
                    # Create choropleth map with filtered data
                    fig = px.choropleth_mapbox(
                        filtered_gdf,
                        geojson=filtered_gdf.geometry.__geo_interface__,
                        locations=filtered_gdf.index,
                        color=color_col if color_col in filtered_gdf.columns else None,
                        color_continuous_scale=color_scheme.lower(),
                        mapbox_style="carto-positron",
                        zoom=6,
                        opacity=0.8,
                        labels={color_col: color_col},
                        hover_data=[shape_key] + [col for col in filtered_df.columns if col != excel_key][:5]  # Add hover data
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
