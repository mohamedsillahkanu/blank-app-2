import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import numpy as np
from PIL import Image
import io
import requests
import base64

# Set page configuration with custom theme
st.set_page_config(
    page_title="Chiefdom Map Dashboard",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Custom styling for headers */
    h1 {
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0;
    }
    h2 {
        color: #1E3A8A;
        font-weight: 600;
    }
    h3 {
        color: #2563EB;
        font-weight: 600;
    }
    
    /* Card-like containers */
    .card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    }
    
    /* Card header */
    .card-header {
        font-weight: 600;
        font-size: 1.2rem;
        margin-bottom: 1rem;
        color: #1E3A8A;
        border-bottom: 1px solid #E5E7EB;
        padding-bottom: 0.5rem;
    }
    
    /* Filter container */
    .filter-container {
        background-color: #F3F4F6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #2563EB;
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 0.25rem;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #1D4ED8;
    }
    
    /* Success messages */
    .success-message {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 0.75rem;
        border-radius: 0.25rem;
        font-weight: 500;
        margin: 0.5rem 0;
    }
    
    /* Warning messages */
    .warning-message {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 0.75rem;
        border-radius: 0.25rem;
        font-weight: 500;
        margin: 0.5rem 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F3F4F6;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563EB;
        color: white;
    }
    
    /* Footer styling */
    .footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #E5E7EB;
        text-align: center;
        color: #6B7280;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# Function to add custom card container
def card_container(title, content_function):
    st.markdown(f'<div class="card"><div class="card-header">{title}</div>', unsafe_allow_html=True)
    content_function()
    st.markdown('</div>', unsafe_allow_html=True)

# Function to create a centered header with optional icon
def styled_header(title, icon=None):
    if icon:
        st.markdown(f'<h1><i class="{icon}"></i> {title}</h1>', unsafe_allow_html=True)
    else:
        st.markdown(f'<h1>{title}</h1>', unsafe_allow_html=True)

# Function to create success message
def success_message(message):
    st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)

# Function to create warning message
def warning_message(message):
    st.markdown(f'<div class="warning-message">{message}</div>', unsafe_allow_html=True)

# Load the shapefile directly
@st.cache_data
def load_chiefdom_shapefile():
    # Replace with your actual GitHub repo URL
    shapefile_url = "https://raw.githubusercontent.com/yourusername/yourrepository/main/Chiefdom%202021.shp"
    
    try:
        # For demonstration purposes - in production use the appropriate method
        shapefile = gpd.read_file(shapefile_url)
        return shapefile
    except Exception as e:
        st.error(f"Error loading Chiefdom shapefile: {str(e)}")
        return None

# Function to get color scale based on data
def get_color_scale(data, color_scheme):
    # Normalize data for better color distribution
    q1, q3 = np.percentile(data, [25, 75])
    iqr = q3 - q1
    lower = max(data.min(), q1 - 1.5 * iqr)
    upper = min(data.max(), q3 + 1.5 * iqr)
    
    # Return color scale configuration
    return {
        'color_continuous_scale': color_scheme.lower(),
        'range_color': (lower, upper)
    }

# Main app layout
def main():
    # App header with logo (replace with actual logo if available)
    col1, col2 = st.columns([1, 5])
    
    with col1:
        # You can replace this with an actual logo
        st.image("https://via.placeholder.com/100x100.png?text=Logo", width=100)
    
    with col2:
        styled_header("Chiefdom Map Dashboard")
        st.markdown("""
        Visualize Chiefdom data with interactive filters and dynamic mapping. 
        Upload your Excel data to join with the Chiefdom 2021 shapefile using FIRST_DNAM and FIRST_CHIE columns.
        """)
    
    # Create a separator
    st.markdown("---")
    
    # Initialize the sidebar
    with st.sidebar:
        st.header("Dashboard Controls")
        
        st.subheader("About This Dashboard")
        st.markdown("""
        This dashboard visualizes geospatial data for Chiefdoms. 
        
        **Features:**
        - Automatic joining with Chiefdom shapefile
        - Interactive filtering
        - Dynamic map visualization
        - Data insights and statistics
        
        Upload your Excel file to get started.
        """)
        
        st.markdown("---")
        
        # Theme selection
        st.subheader("Map Appearance")
        map_style = st.selectbox(
            "Map Style",
            options=["carto-positron", "open-street-map", "carto-darkmatter", "white-bg", "stamen-terrain"],
            index=0
        )
        
        # Color schemes with previews
        st.subheader("Color Schemes")
        col_schemes = {
            "Viridis": ["#440154", "#414487", "#2A788E", "#22A884", "#7AD151", "#FDE725"],
            "Plasma": ["#0D0887", "#6A00A8", "#B12A90", "#E16462", "#FCA636", "#F0F921"],
            "Inferno": ["#000004", "#420A68", "#932667", "#DD513A", "#FCA50A", "#FCFFA4"],
            "Blues": ["#F7FBFF", "#D0E1F2", "#94C4DF", "#4A98C9", "#1764AB", "#08306B"],
            "Reds": ["#FFF5F0", "#FEE0D2", "#FCAA8E", "#FC7651", "#E31A1C", "#67000D"]
        }
        
        # Display color scheme previews
        for name, colors in col_schemes.items():
            cols = st.columns(len(colors))
            for i, col in enumerate(cols):
                col.markdown(f'<div style="background-color: {colors[i]}; height: 20px; border-radius: 2px;"></div>', unsafe_allow_html=True)
            st.radio(name, [name], key=f"scheme_{name}", horizontal=True)
        
        default_scheme = "Viridis"
    
    # Load shapefile
    with st.spinner("Loading Chiefdom shapefile..."):
        gdf = load_chiefdom_shapefile()
    
    if gdf is not None:
        success_message("Chiefdom shapefile loaded successfully!")
        
        # Create tabs for better organization
        main_tab, info_tab, help_tab = st.tabs(["📊 Dashboard", "ℹ️ Data Info", "❓ Help"])
        
        with info_tab:
            def show_shapefile_info():
                st.write(f"Number of features: {len(gdf)}")
                st.write(f"Coordinate System: {gdf.crs}")
                
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
                st.dataframe(sample_df, use_container_width=True)
            
            card_container("Shapefile Information", show_shapefile_info)
            
            # Show a preview map of the shapefile
            def show_preview_map():
                fig = px.choropleth_mapbox(
                    gdf,
                    geojson=gdf.geometry.__geo_interface__,
                    locations=gdf.index,
                    mapbox_style="carto-positron",
                    zoom=6,
                    opacity=0.7
                )
                
                # Center map on data
                center_lon = gdf.geometry.centroid.x.mean()
                center_lat = gdf.geometry.centroid.y.mean()
                fig.update_layout(
                    margin={"r":0,"t":0,"l":0,"b":0},
                    mapbox=dict(center=dict(lon=center_lon, lat=center_lat)),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            card_container("Shapefile Preview", show_preview_map)
        
        with help_tab:
            st.subheader("How to Use This Dashboard")
            
            st.markdown("""
            ### Step 1: Upload Data
            - Click on "Choose a file" in the Dashboard tab
            - Select an Excel file (.xlsx or .xls) containing your data
            - Make sure your Excel file has a column named 'FIRST_DNAM' for joining
            
            ### Step 2: Join and Filter
            - The dashboard will automatically join your data with the Chiefdom shapefile
            - Use the filter options to explore your data
            - Numeric filters let you select ranges of values
            - Categorical filters let you select specific values
            
            ### Step 3: Customize Visualization
            - Select a column to color the map by
            - Choose a color scheme from the sidebar
            - Adjust the map style as needed
            
            ### Tips for Best Results
            - Make sure your data is clean and properly formatted
            - Use meaningful numeric columns for coloring the map
            - Try different color schemes to highlight patterns
            
            ### Need More Help?
            Contact support at support@example.com
            """)
        
        with main_tab:
            # Excel file uploader
            def show_file_uploader():
                return st.file_uploader("Choose an Excel file to join with the Chiefdom data", type=['xlsx', 'xls'])
            
            excel_file = show_file_uploader()
            
            if excel_file:
                try:
                    # Load the Excel file
                    df = pd.read_excel(excel_file)
                    success_message(f"Successfully loaded {excel_file.name} with {len(df)} rows and {len(df.columns)} columns")
                    
                    # Check for required columns
                    excel_cols = df.columns.tolist()
                    shape_cols = gdf.columns.tolist()
                    
                    # Join Configuration
                    def show_join_configuration():
                        if 'FIRST_DNAM' in excel_cols:
                            excel_key = 'FIRST_DNAM'
                            success_message(f"Using 'FIRST_DNAM' from Excel data as join key")
                        else:
                            warning_message("Excel column 'FIRST_DNAM' not found")
                            excel_key = st.selectbox("Select alternative Excel join column:", options=excel_cols)
                        
                        if 'FIRST_CHIE' in shape_cols:
                            shape_key = 'FIRST_CHIE'
                            success_message(f"Using 'FIRST_CHIE' from shapefile as join key")
                        else:
                            warning_message("Shapefile column 'FIRST_CHIE' not found")
                            shape_key = st.selectbox("Select alternative shapefile join column:", options=shape_cols)
                        
                        return excel_key, shape_key
                    
                    card_container("Join Configuration", lambda: None)
                    excel_key, shape_key = show_join_configuration()
                    
                    # Join button
                    if st.button("Join Data and Create Map", key="join_button"):
                        with st.spinner("Joining data and creating visualization..."):
                            # Convert join columns to strings for safer joining
                            df[excel_key] = df[excel_key].astype(str)
                            gdf[shape_key] = gdf[shape_key].astype(str)
                            
                            # Perform the join
                            merged_gdf = gdf.merge(df, left_on=shape_key, right_on=excel_key, how='left')
                            
                            # Display only the number of matches
                            match_count = merged_gdf[~merged_gdf[excel_key].isna()].shape[0]
                            st.write(f"Matched {match_count} out of {len(gdf)} features")
                            
                            # Create filter and visualization section
                            filter_col, map_col = st.columns([1, 2])
                            
                            with filter_col:
                                st.subheader("Filter Options")
                                
                                # Identify numeric and categorical columns for filtering
                                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
                                cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                                
                                st.markdown('<div class="filter-container">', unsafe_allow_html=True)
                                
                                # Add numeric filters
                                numeric_filters = {}
                                if numeric_cols:
                                    st.markdown("#### Numeric Filters")
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
                                cat_filters = {}
                                if cat_cols:
                                    st.markdown("#### Categorical Filters")
                                    for col in cat_cols[:3]:  # Limit to first 3 for simplicity
                                        if col in df.columns and col != excel_key:  # Skip join key
                                            unique_vals = df[col].dropna().unique().tolist()
                                            cat_filters[col] = st.multiselect(
                                                f"Select {col}",
                                                options=unique_vals,
                                                default=unique_vals
                                            )
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                # Visualization options
                                st.subheader("Map Options")
                                
                                # Choose column to visualize
                                color_col = st.selectbox("Color by", options=numeric_cols)
                                
                                # Choose color scheme
                                color_schemes = ["Viridis", "Plasma", "Inferno", "Blues", "Reds", "YlOrRd", "YlGnBu", "Greens"]
                                color_scheme = st.selectbox("Color scheme", options=color_schemes, index=color_schemes.index(default_scheme) if default_scheme in color_schemes else 0)
                                
                                # Stats and insights 
                                st.subheader("Data Insights")
                                
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
                                
                                # Show some quick stats
                                if color_col in filtered_df.columns:
                                    st.metric("Average", f"{filtered_df[color_col].mean():.2f}")
                                    st.metric("Median", f"{filtered_df[color_col].median():.2f}")
                                    st.metric("Range", f"{filtered_df[color_col].min():.2f} - {filtered_df[color_col].max():.2f}")
                            
                            with map_col:
                                # Re-merge with filtered data
                                filtered_gdf = gdf.merge(filtered_df, left_on=shape_key, right_on=excel_key, how='inner')
                                
                                # Create the map
                                st.subheader("Chiefdom Map")
                                
                                # Display number of features on the map
                                st.write(f"Showing {len(filtered_gdf)} chiefdoms based on current filters")
                                
                                # Ensure the geodataframe is in the right projection
                                if filtered_gdf.crs != "EPSG:4326":
                                    filtered_gdf = filtered_gdf.to_crs(epsg=4326)
                                
                                # Get color scale parameters
                                if color_col in filtered_gdf.columns and len(filtered_gdf) > 0:
                                    color_params = get_color_scale(filtered_gdf[color_col], color_scheme)
                                    
                                    # Create choropleth map with filtered data
                                    fig = px.choropleth_mapbox(
                                        filtered_gdf,
                                        geojson=filtered_gdf.geometry.__geo_interface__,
                                        locations=filtered_gdf.index,
                                        color=color_col,
                                        color_continuous_scale=color_params['color_continuous_scale'],
                                        range_color=color_params['range_color'],
                                        mapbox_style=map_style,
                                        zoom=6,
                                        opacity=0.8,
                                        labels={color_col: color_col},
                                        hover_data=[shape_key] + [col for col in filtered_df.columns if col != excel_key][:5]
                                    )
                                    
                                    # Center map on data
                                    center_lon = filtered_gdf.geometry.centroid.x.mean()
                                    center_lat = filtered_gdf.geometry.centroid.y.mean()
                                    fig.update_layout(
                                        margin={"r":0,"t":0,"l":0,"b":0},
                                        mapbox=dict(center=dict(lon=center_lon, lat=center_lat)),
                                        height=600
                                    )
                                    
                                    st.plotly_chart(fig, use_container_width=True)
                                else:
                                    warning_message(f"Column '{color_col}' not found in joined data or no data matches the current filters.")
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
            else:
                # Display a placeholder graphic when no file is uploaded
                st.markdown(
                    """
                    <div style="display: flex; justify-content: center; align-items: center; height: 400px; 
                    background-color: #F9FAFB; border-radius: 0.5rem; border: 1px dashed #D1D5DB; margin: 2rem 0;">
                        <div style="text-align: center;">
                            <div style="font-size: 3rem; color: #9CA3AF; margin-bottom: 1rem;">📊</div>
                            <div style="font-size: 1.25rem; font-weight: 600; color: #4B5563;">Upload an Excel file to get started</div>
                            <div style="color: #6B7280; margin-top: 0.5rem;">Data will be automatically joined with the Chiefdom shapefile</div>
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
    else:
        st.error("Failed to load the Chiefdom shapefile. Please check the URL or file path.")
    
    # Footer
    st.markdown('<div class="footer">Chiefdom Map Dashboard | Built with Streamlit</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
