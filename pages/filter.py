import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import tempfile
import os

# Set page configuration
st.set_page_config(
    page_title="Chiefdom Map Dashboard",
    page_icon="🗺️",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main .block-container {padding-top: 1rem;}
    h1 {color: #2C3E50; font-weight: 700;}
    h2 {color: #2C3E50; font-weight: 600;}
    .upload-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .filter-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Function to load shapefile from uploaded components
def load_shapefile_from_components(shp_file, shx_file, dbf_file):
    """Load a shapefile from its component files."""
    # Create a temporary directory to store the files
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Save uploaded files to the temporary directory
        shp_path = os.path.join(tmp_dir, "shapefile.shp")
        shx_path = os.path.join(tmp_dir, "shapefile.shx")
        dbf_path = os.path.join(tmp_dir, "shapefile.dbf")
        
        with open(shp_path, "wb") as f:
            f.write(shp_file.getbuffer())
        with open(shx_path, "wb") as f:
            f.write(shx_file.getbuffer())
        with open(dbf_path, "wb") as f:
            f.write(dbf_file.getbuffer())
        
        # Load the shapefile
        gdf = gpd.read_file(shp_path)
        return gdf

# Function to load data file
def load_data_file(file):
    """Load data from Excel or CSV file."""
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:  # Excel file
        return pd.read_excel(file)

# Function to create filter controls based on column type
def create_filter_control(df, col_name, filter_state):
    col_type = str(df[col_name].dtype)
    
    # For numeric columns
    if col_type in ['int64', 'float64']:
        min_val = float(df[col_name].min())
        max_val = float(df[col_name].max())
        filter_state[col_name] = st.slider(
            f"Filter by {col_name}", 
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val),
            key=f"filter_{col_name}"
        )
    # For categorical columns
    else:
        unique_vals = df[col_name].dropna().unique().tolist()
        filter_state[col_name] = st.multiselect(
            f"Select {col_name}",
            options=unique_vals,
            default=unique_vals,
            key=f"filter_{col_name}"
        )

# Function to apply filters to a dataframe
def apply_filters(df, filter_state):
    filtered_df = df.copy()
    
    for col_name, filter_val in filter_state.items():
        if col_name in filtered_df.columns:
            col_type = str(filtered_df[col_name].dtype)
            
            # For numeric columns (using slider ranges)
            if col_type in ['int64', 'float64']:
                filtered_df = filtered_df[(filtered_df[col_name] >= filter_val[0]) & 
                                         (filtered_df[col_name] <= filter_val[1])]
            
            # For categorical columns (using multiselect)
            else:
                if filter_val:  # Only filter if values are selected
                    filtered_df = filtered_df[filtered_df[col_name].isin(filter_val)]
    
    return filtered_df

# Main application
def main():
    # App title
    st.title("Chiefdom Map Dashboard")
    
    # Initialize session state variables
    if 'data_file' not in st.session_state:
        st.session_state.data_file = None
    if 'shapefile_data' not in st.session_state:
        st.session_state.shapefile_data = None
    if 'merged_data' not in st.session_state:
        st.session_state.merged_data = None
    if 'filter_state' not in st.session_state:
        st.session_state.filter_state = {}
    if 'selected_columns' not in st.session_state:
        st.session_state.selected_columns = []
    if 'color_column' not in st.session_state:
        st.session_state.color_column = None
    
    # File Upload Section
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        data_file = st.file_uploader("Upload Data (.xlsx, .xls, .csv)", type=['xlsx', 'xls', 'csv'])
    
    with col2:
        shp_file = st.file_uploader("Upload .shp file", type=['shp'])
    
    with col3:
        shx_file = st.file_uploader("Upload .shx file", type=['shx'])
    
    with col4:
        dbf_file = st.file_uploader("Upload .dbf file", type=['dbf'])
    
    # Process files if uploaded
    if data_file and shp_file and shx_file and dbf_file:
        # Load data file
        try:
            df = load_data_file(data_file)
            st.session_state.data_file = df
        except Exception as e:
            st.error(f"Error loading data file: {str(e)}")
        
        # Load shapefile components
        try:
            gdf = load_shapefile_from_components(shp_file, shx_file, dbf_file)
            st.session_state.shapefile_data = gdf
        except Exception as e:
            st.error(f"Error loading shapefile: {str(e)}")
        
        # If both data sources are loaded, set up join
        if st.session_state.data_file is not None and st.session_state.shapefile_data is not None:
            # Get the dataframes
            df = st.session_state.data_file
            gdf = st.session_state.shapefile_data
            
            # Check for FIRST_DNAM in data file
            excel_join_col = 'FIRST_DNAM'
            if excel_join_col not in df.columns:
                excel_join_col = st.selectbox(
                    "Select data join column:",
                    options=df.columns.tolist()
                )
            
            # Check for FIRST_CHIE in shapefile
            shape_join_col = 'FIRST_CHIE'
            if shape_join_col not in gdf.columns:
                shape_join_col = st.selectbox(
                    "Select shapefile join column:",
                    options=gdf.columns.tolist()
                )
            
            # Join button
            join_btn = st.button("Join Data")
            
            if join_btn:
                try:
                    # Convert join columns to string for safer joining
                    df[excel_join_col] = df[excel_join_col].astype(str)
                    gdf[shape_join_col] = gdf[shape_join_col].astype(str)
                    
                    # Merge dataframes
                    merged_gdf = gdf.merge(df, left_on=shape_join_col, right_on=excel_join_col, how='inner')
                    
                    # Store the merged data
                    st.session_state.merged_data = merged_gdf
                except Exception as e:
                    st.error(f"Error joining data: {str(e)}")
            
            # If data is joined, show column selection and map
            if st.session_state.merged_data is not None:
                merged_df = st.session_state.merged_data
                
                # Column selection
                col_select, map_col = st.columns([1, 3])
                
                with col_select:
                    # Get all columns from data file (excluding geometry and join columns)
                    all_columns = [col for col in merged_df.columns if col not in ['geometry', shape_join_col, excel_join_col]]
                    
                    # Column selection for filtering
                    st.subheader("Filter Columns")
                    selected_columns = st.multiselect(
                        "Select columns for filtering:",
                        options=all_columns,
                        default=[]
                    )
                    st.session_state.selected_columns = selected_columns
                    
                    # Choose column for map coloring
                    numeric_cols = [col for col in all_columns if merged_df[col].dtype in ['int64', 'float64']]
                    if numeric_cols:
                        st.subheader("Map Color")
                        color_column = st.selectbox(
                            "Color by:",
                            options=numeric_cols
                        )
                        st.session_state.color_column = color_column
                    
                    # Create filters
                    if selected_columns:
                        st.subheader("Filters")
                        for col_name in selected_columns:
                            if col_name in merged_df.columns:
                                create_filter_control(merged_df, col_name, st.session_state.filter_state)
                        
                        if st.button("Apply Filters"):
                            st.experimental_rerun()
                
                with map_col:
                    # Apply filters to get filtered dataframe
                    filtered_df = apply_filters(merged_df, st.session_state.filter_state)
                    
                    # Create the map
                    if st.session_state.color_column in filtered_df.columns:
                        # Ensure the geodataframe is in the right projection
                        if filtered_df.crs != "EPSG:4326":
                            filtered_df = filtered_df.to_crs(epsg=4326)
                        
                        # Create choropleth map
                        fig = px.choropleth_mapbox(
                            filtered_df,
                            geojson=filtered_df.geometry.__geo_interface__,
                            locations=filtered_df.index,
                            color=st.session_state.color_column,
                            color_continuous_scale="Viridis",
                            mapbox_style="carto-positron",
                            zoom=6,
                            opacity=0.8,
                            labels={st.session_state.color_column: st.session_state.color_column},
                            hover_data=st.session_state.selected_columns[:5]
                        )
                        
                        # Center map on data
                        center_lon = filtered_df.geometry.centroid.x.mean()
                        center_lat = filtered_df.geometry.centroid.y.mean()
                        fig.update_layout(
                            margin={"r":0,"t":0,"l":0,"b":0},
                            mapbox=dict(center=dict(lon=center_lon, lat=center_lat)),
                            height=600
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
