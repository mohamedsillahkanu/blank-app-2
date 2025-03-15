import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import numpy as np
import tempfile
import os
import io
import colorsys

# Set page configuration
st.set_page_config(
    page_title="Interactive Chiefdom Map",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main .block-container {padding-top: 1rem;}
    h1 {color: #2C3E50; font-weight: 700;}
    h2 {color: #2C3E50; font-weight: 600;}
    h3 {color: #34495E; font-weight: 600;}
    
    /* Card styling */
    .card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    }
    
    /* Filter section */
    .filter-section {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #2C3E50;
    }
    
    /* Button styling */
    .primary-button {
        background-color: #2C3E50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        text-align: center;
        margin: 0.5rem 0;
        text-decoration: none;
        display: inline-block;
        border: none;
        cursor: pointer;
    }
    
    /* Color palette */
    .color-box {
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-right: 5px;
        border: 1px solid #ddd;
    }
    
    /* Upload area */
    .upload-container {
        border: 2px dashed #ddd;
        border-radius: 0.5rem;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Divider */
    .divider {
        margin: 1rem 0;
        border-top: 1px solid #eee;
    }
    
    /* Status indicators */
    .status-success {
        color: #27ae60;
        font-weight: 500;
    }
    .status-warning {
        color: #f39c12;
        font-weight: 500;
    }
    .status-error {
        color: #e74c3c;
        font-weight: 500;
    }
    
    /* Footer */
    .footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
        text-align: center;
        color: #7f8c8d;
        font-size: 0.875rem;
    }
    
    /* Checkbox container */
    .checkbox-container {
        max-height: 200px;
        overflow-y: auto;
        border: 1px solid #eee;
        padding: 0.5rem;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Function to generate color palettes
def generate_color_palette(base_hue, n_colors=5, scheme_type="sequential"):
    colors = []
    if scheme_type == "sequential":
        # Sequential palette: same hue, varying saturation and lightness
        for i in range(n_colors):
            saturation = 0.4 + (0.6 * i / (n_colors - 1))  # 0.4 to 1.0
            lightness = 0.9 - (0.7 * i / (n_colors - 1))   # 0.9 to 0.2
            rgb = colorsys.hls_to_rgb(base_hue, lightness, saturation)
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
            )
            colors.append(hex_color)
    elif scheme_type == "diverging":
        # Diverging palette: two hues, varying saturation and lightness
        second_hue = (base_hue + 0.5) % 1.0  # Opposite hue
        for i in range(n_colors):
            if i < n_colors // 2:
                # First half - base hue
                progress = i / (n_colors // 2)
                saturation = 0.8 - (0.6 * (1 - progress))
                lightness = 0.9 - (0.4 * progress)
                current_hue = base_hue
            else:
                # Second half - opposite hue
                progress = (i - n_colors // 2) / (n_colors - n_colors // 2)
                saturation = 0.2 + (0.6 * progress)
                lightness = 0.5 + (0.4 * (1 - progress))
                current_hue = second_hue
                
            rgb = colorsys.hls_to_rgb(current_hue, lightness, saturation)
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
            )
            colors.append(hex_color)
    else:  # Qualitative
        # Qualitative palette: varying hues, consistent saturation and lightness
        for i in range(n_colors):
            # Distribute hues evenly, but with a golden ratio to avoid adjacency
            hue = (base_hue + i * 0.618033988749895) % 1.0
            rgb = colorsys.hls_to_rgb(hue, 0.6, 0.7)
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
            )
            colors.append(hex_color)
            
    return colors

# Function to create filter controls based on column type
def create_filter_control(df, col_name, col_type, filter_state):
    if col_name in filter_state:
        # If the filter is already in state, just return without creating new control
        return
    
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
    elif col_type in ['object', 'category']:
        unique_vals = df[col_name].dropna().unique().tolist()
        filter_state[col_name] = st.multiselect(
            f"Select {col_name}",
            options=unique_vals,
            default=unique_vals,
            key=f"filter_{col_name}"
        )
    # For boolean columns
    elif col_type == 'bool':
        filter_state[col_name] = st.multiselect(
            f"Select {col_name}",
            options=[True, False],
            default=[True, False],
            key=f"filter_{col_name}"
        )
    # For datetime columns
    elif col_type in ['datetime64[ns]', 'datetime64']:
        min_date = df[col_name].min().date()
        max_date = df[col_name].max().date()
        filter_state[col_name] = st.date_range_slider(
            f"Select date range for {col_name}",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
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
            elif col_type in ['object', 'category', 'bool']:
                if filter_val:  # Only filter if values are selected
                    filtered_df = filtered_df[filtered_df[col_name].isin(filter_val)]
            
            # For datetime columns (using date range)
            elif col_type in ['datetime64[ns]', 'datetime64']:
                filtered_df = filtered_df[(filtered_df[col_name].dt.date >= filter_val[0]) & 
                                         (filtered_df[col_name].dt.date <= filter_val[1])]
    
    return filtered_df

# Function to load shapefile from uploaded components
def load_shapefile_from_components(shp_file, shx_file, dbf_file, prj_file=None):
    """Load a shapefile from its component files."""
    # Create a temporary directory to store the files
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Save uploaded files to the temporary directory
        file_paths = {}
        
        for file_obj, ext in zip(
            [shp_file, shx_file, dbf_file, prj_file],
            ['.shp', '.shx', '.dbf', '.prj']
        ):
            if file_obj is not None:
                file_path = os.path.join(tmp_dir, f"shapefile{ext}")
                with open(file_path, "wb") as f:
                    f.write(file_obj.getbuffer())
                file_paths[ext] = file_path
        
        # Check that we have the essential components
        if not all(ext in file_paths for ext in ['.shp', '.shx', '.dbf']):
            missing = [ext for ext in ['.shp', '.shx', '.dbf'] if ext not in file_paths]
            raise ValueError(f"Missing required shapefile components: {', '.join(missing)}")
        
        # Load the shapefile
        gdf = gpd.read_file(file_paths['.shp'])
        return gdf

# Main application
def main():
    # Application title
    st.title("Interactive Chiefdom Map Dashboard")
    st.markdown("Upload Excel data and shapefile components to create a customized, filterable map visualization.")
    
    # Initialize session state for storing data and filters
    if 'excel_data' not in st.session_state:
        st.session_state.excel_data = None
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
    
    # Create layout with sidebar
    with st.sidebar:
        st.header("Dashboard Controls")
        
        # File uploaders
        st.subheader("1. Upload Data")
        
        # Excel uploader
        excel_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])
        
        # Individual shapefile component uploaders
        st.markdown("#### Upload Shapefile Components")
        
        col1, col2 = st.columns(2)
        
        with col1:
            shp_file = st.file_uploader("Upload .shp file", type=['shp'])
            dbf_file = st.file_uploader("Upload .dbf file", type=['dbf'])
        
        with col2:
            shx_file = st.file_uploader("Upload .shx file", type=['shx'])
            prj_file = st.file_uploader("Upload .prj file (optional)", type=['prj'])
        
        # Process files if uploaded
        if excel_file and shp_file and shx_file and dbf_file:
            # Process Excel file
            try:
                df = pd.read_excel(excel_file)
                st.session_state.excel_data = df
                st.sidebar.success(f"Excel file loaded: {len(df)} rows, {len(df.columns)} columns")
            except Exception as e:
                st.sidebar.error(f"Error loading Excel file: {str(e)}")
            
            # Process shapefile components
            try:
                gdf = load_shapefile_from_components(shp_file, shx_file, dbf_file, prj_file)
                st.session_state.shapefile_data = gdf
                st.sidebar.success(f"Shapefile loaded: {len(gdf)} features")
                
                # Check if FIRST_CHIE exists in the shapefile
                if 'FIRST_CHIE' not in gdf.columns:
                    st.sidebar.warning("Column 'FIRST_CHIE' not found in shapefile. Joining may fail.")
            except Exception as e:
                st.sidebar.error(f"Error loading shapefile: {str(e)}")
        
        # If both data sources are loaded, set up join options
        if st.session_state.excel_data is not None and st.session_state.shapefile_data is not None:
            st.subheader("2. Join Configuration")
            
            # Get the dataframes
            df = st.session_state.excel_data
            gdf = st.session_state.shapefile_data
            
            # Check for FIRST_DNAM in Excel data
            excel_join_col = 'FIRST_DNAM'
            if excel_join_col not in df.columns:
                excel_join_col = st.selectbox(
                    "FIRST_DNAM not found. Select Excel join column:",
                    options=df.columns.tolist()
                )
            else:
                st.success(f"Using '{excel_join_col}' from Excel for joining")
            
            # Check for FIRST_CHIE in shapefile
            shape_join_col = 'FIRST_CHIE'
            if shape_join_col not in gdf.columns:
                shape_join_col = st.selectbox(
                    "FIRST_CHIE not found. Select Shapefile join column:",
                    options=gdf.columns.tolist()
                )
            else:
                st.success(f"Using '{shape_join_col}' from Shapefile for joining")
            
            # Perform the join when the button is clicked
            if st.button("Join Data"):
                try:
                    # Convert join columns to string for safer joining
                    df[excel_join_col] = df[excel_join_col].astype(str)
                    gdf[shape_join_col] = gdf[shape_join_col].astype(str)
                    
                    # Merge dataframes
                    merged_gdf = gdf.merge(df, left_on=shape_join_col, right_on=excel_join_col, how='inner')
                    
                    # Store the merged data
                    st.session_state.merged_data = merged_gdf
                    
                    # Display join results
                    match_count = len(merged_gdf)
                    total_features = len(gdf)
                    st.success(f"Join complete: {match_count} matches out of {total_features} features")
                    
                    # Reset any existing filters
                    st.session_state.filter_state = {}
                    st.session_state.selected_columns = []
                except Exception as e:
                    st.error(f"Error joining data: {str(e)}")
            
            # If data is joined, show column selection
            if st.session_state.merged_data is not None:
                st.subheader("3. Select Columns for Filtering")
                
                merged_df = st.session_state.merged_data
                
                # Get all columns from Excel data (excluding geometry and join column)
                all_columns = [col for col in merged_df.columns if col not in ['geometry', shape_join_col, excel_join_col]]
                
                # Allow user to select which columns to use for filtering
                with st.expander("Column Selection", expanded=True):
                    # Group columns by data type for easier selection
                    numeric_cols = [col for col in all_columns if merged_df[col].dtype in ['int64', 'float64']]
                    categorical_cols = [col for col in all_columns if merged_df[col].dtype in ['object', 'category']]
                    other_cols = [col for col in all_columns if col not in numeric_cols + categorical_cols]
                    
                    # Create selection for numeric columns
                    if numeric_cols:
                        st.markdown("#### Numeric Columns")
                        numeric_selected = st.multiselect(
                            "Select numeric columns for filtering:",
                            options=numeric_cols,
                            default=[]
                        )
                    
                    # Create selection for categorical columns
                    if categorical_cols:
                        st.markdown("#### Categorical Columns")
                        categorical_selected = st.multiselect(
                            "Select categorical columns for filtering:",
                            options=categorical_cols,
                            default=[]
                        )
                    
                    # Create selection for other columns
                    if other_cols:
                        st.markdown("#### Other Columns")
                        other_selected = st.multiselect(
                            "Select other columns for filtering:",
                            options=other_cols,
                            default=[]
                        )
                    
                    # Combine all selected columns
                    selected_columns = numeric_selected + categorical_selected + other_selected
                    st.session_state.selected_columns = selected_columns
                
                # Choose a column for coloring the map
                st.subheader("4. Map Visualization")
                
                # Only show numeric columns for coloring
                color_column_options = [col for col in all_columns if merged_df[col].dtype in ['int64', 'float64']]
                if color_column_options:
                    color_column = st.selectbox(
                        "Select column for coloring the map:",
                        options=color_column_options
                    )
                    st.session_state.color_column = color_column
                else:
                    st.warning("No numeric columns available for coloring the map.")
                
                # Color scheme options
                st.markdown("#### Color Scheme")
                color_scheme_type = st.radio(
                    "Select color scheme type:",
                    options=["Sequential", "Diverging", "Qualitative"],
                    horizontal=True
                )
                
                # Color hue selection
                base_hue_options = {
                    "Blue": 0.6,
                    "Green": 0.3,
                    "Red": 0.0,
                    "Purple": 0.8,
                    "Orange": 0.1,
                    "Teal": 0.5,
                }
                
                base_hue_name = st.selectbox(
                    "Select base color:",
                    options=list(base_hue_options.keys())
                )
                base_hue = base_hue_options[base_hue_name]
                
                # Generate and display color palette preview
                n_colors = 5
                palette = generate_color_palette(
                    base_hue, 
                    n_colors, 
                    scheme_type=color_scheme_type.lower()
                )
                
                # Display color preview
                st.markdown("#### Color Preview")
                cols = st.columns(n_colors)
                for i, (col, color) in enumerate(zip(cols, palette)):
                    col.markdown(
                        f'<div style="background-color: {color}; height: 30px; border-radius: 3px;"></div>',
                        unsafe_allow_html=True
                    )
                
                # Legend title
                legend_title = st.text_input(
                    "Enter legend title:", 
                    value=st.session_state.color_column if st.session_state.color_column else "Value"
                )
                
                # Map style
                map_style = st.selectbox(
                    "Select map style:",
                    options=["carto-positron", "open-street-map", "carto-darkmatter", "white-bg"],
                    index=0
                )
    
    # Main content area
    if st.session_state.merged_data is not None and st.session_state.selected_columns:
        # Create layout with two columns - one for filters and one for the map
        filter_col, map_col = st.columns([1, 2])
        
        with filter_col:
            st.header("Filters")
            st.markdown("Use these filters to customize the map visualization.")
            
            # Create filter section
            st.markdown('<div class="filter-section">', unsafe_allow_html=True)
            
            merged_df = st.session_state.merged_data
            
            # Create filter controls for selected columns
            for col_name in st.session_state.selected_columns:
                if col_name in merged_df.columns:
                    col_type = str(merged_df[col_name].dtype)
                    create_filter_control(merged_df, col_name, col_type, st.session_state.filter_state)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Apply filters button
            if st.button("Apply Filters", key="apply_filters"):
                st.experimental_rerun()
        
        with map_col:
            st.header("Chiefdom Map")
            
            # Apply filters to get filtered dataframe
            filtered_df = apply_filters(st.session_state.merged_data, st.session_state.filter_state)
            
            # Display filtered data count
            st.write(f"Showing {len(filtered_df)} features based on current filters")
            
            # Create the map
            if st.session_state.color_column and st.session_state.color_column in filtered_df.columns:
                # Ensure the geodataframe is in the right projection
                if filtered_df.crs != "EPSG:4326":
                    filtered_df = filtered_df.to_crs(epsg=4326)
                
                # Generate color scale
                color_scale = generate_color_palette(
                    base_hue, 
                    5, 
                    scheme_type=color_scheme_type.lower()
                )
                
                # Create choropleth map
                fig = px.choropleth_mapbox(
                    filtered_df,
                    geojson=filtered_df.geometry.__geo_interface__,
                    locations=filtered_df.index,
                    color=st.session_state.color_column,
                    color_continuous_scale=color_scale,
                    mapbox_style=map_style,
                    zoom=6,
                    opacity=0.8,
                    labels={st.session_state.color_column: legend_title},
                    hover_data=st.session_state.selected_columns[:5]  # Show first 5 selected columns in hover
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
            else:
                st.warning("Please select a numeric column for coloring the map.")
            
            # Show data statistics
            with st.expander("Data Statistics"):
                if st.session_state.color_column:
                    st.subheader(f"Statistics for {st.session_state.color_column}")
                    stats_df = filtered_df[st.session_state.color_column].describe().reset_index()
                    stats_df.columns = ['Statistic', 'Value']
                    st.dataframe(stats_df, use_container_width=True)
    
    # Initial state - no data loaded yet
    elif st.session_state.excel_data is None or st.session_state.shapefile_data is None:
        st.info("Please upload Excel data and all required shapefile components (.shp, .shx, .dbf) in the sidebar to get started.")
        
        # Placeholder with instructions
        st.markdown(
            """
            <div style="text-align: center; padding: 3rem; background-color: #f8f9fa; border-radius: 0.5rem;">
                <h3>How to use this dashboard</h3>
                <ol style="text-align: left; display: inline-block;">
                    <li>Upload your Excel file and shapefile components in the sidebar:
                        <ul>
                            <li><b>.shp file</b> - Contains the geometry data</li>
                            <li><b>.shx file</b> - Contains the shape index</li>
                            <li><b>.dbf file</b> - Contains the attribute data</li>
                            <li><b>.prj file</b> - Contains the projection information (optional but recommended)</li>
                        </ul>
                    </li>
                    <li>Confirm the join columns (FIRST_DNAM and FIRST_CHIE will be used if available)</li>
                    <li>Select which columns you want to use for filtering</li>
                    <li>Choose a column for coloring the map and customize the color scheme</li>
                    <li>Apply filters to update the visualization</li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True
        )
    # Data loaded but not joined, or columns not selected
    else:
        if st.session_state.merged_data is None:
            st.warning("Please join the data using the button in the sidebar.")
        else:
            st.warning("Please select columns for filtering in the sidebar.")
    
    # Footer
    st.markdown(
        '<div class="footer">Interactive Chiefdom Map Dashboard | Built with Streamlit</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
