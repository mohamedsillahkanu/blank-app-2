import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

st.set_page_config(layout="wide", page_title="Chiefdom Center Points Map")
st.title("🗺️ Interactive Chiefdom Center Points Map")
st.markdown("Upload your Excel file and place interactive points at the center of each chiefdom!")

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'shapefile' not in st.session_state:
    st.session_state.shapefile = None

# Load shapefile
st.markdown("### 🗺️ Loading Shapefile")
try:
    shapefile = gpd.read_file("Chiefdom 2021.shp")
    st.session_state.shapefile = shapefile
    
    if shapefile.crs is None:
        shapefile = shapefile.set_crs(epsg=4326)
    
    st.success(f"✅ Shapefile loaded successfully! Found {len(shapefile)} chiefdoms.")
    
    # Calculate center points for each chiefdom
    shapefile['center_lat'] = shapefile.geometry.centroid.y
    shapefile['center_lon'] = shapefile.geometry.centroid.x
    
    # Show shapefile info
    with st.expander("🗺️ Shapefile Information"):
        st.write(f"**Number of chiefdoms:** {len(shapefile)}")
        if 'FIRST_DNAM' in shapefile.columns:
            districts = shapefile['FIRST_DNAM'].unique()
            st.write(f"**Districts found:** {', '.join(sorted(districts))}")
        if 'FIRST_CHIE' in shapefile.columns:
            chiefdoms = sorted(shapefile['FIRST_CHIE'].unique())
            st.write(f"**Chiefdoms found:** {len(chiefdoms)} total")
            
        st.write(f"**Columns:** {list(shapefile.columns)}")
        st.write("**Sample chiefdom centers:**")
        center_sample = shapefile[['FIRST_CHIE', 'center_lat', 'center_lon']].head()
        st.dataframe(center_sample)
        
except Exception as e:
    st.error(f"❌ Could not load shapefile: {str(e)}")
    st.markdown("""
    **Please ensure you have:**
    - `Chiefdom 2021.shp`
    - `Chiefdom 2021.shx` 
    - `Chiefdom 2021.dbf`
    - All files in the same directory as your script
    """)
    st.stop()

# File upload section
st.markdown("### 📁 Upload Your Excel File")
uploaded_file = st.file_uploader(
    "Choose an Excel file", 
    type=['xlsx', 'xls'],
    help="Upload your Excel file containing the data you want to display at each chiefdom center"
)

if uploaded_file is not None:
    try:
        # Load the data
        df = pd.read_excel(uploaded_file)
        st.session_state.data = df
        
        st.success(f"✅ File uploaded successfully! Found {len(df)} rows and {len(df.columns)} columns.")
        
        # Show data preview
        with st.expander("📊 Data Preview"):
            st.dataframe(df.head())
            
        # Show column information
        with st.expander("📋 Column Information"):
            col_info = []
            for col in df.columns:
                non_null = df[col].notna().sum()
                data_type = str(df[col].dtype)
                sample_values = df[col].dropna().head(3).tolist()
                col_info.append({
                    'Column': col,
                    'Non-null Count': f"{non_null}/{len(df)}",
                    'Data Type': data_type,
                    'Sample Values': str(sample_values)[:100] + ("..." if len(str(sample_values)) > 100 else "")
                })
            st.dataframe(pd.DataFrame(col_info))

        # Step 1: Link data to chiefdoms (optional)
        st.markdown("### 🔗 Step 1: Link Data to Chiefdoms (Optional)")
        
        link_option = st.radio(
            "How do you want to display data?",
            [
                "Same data for all chiefdoms", 
                "Different data per chiefdom (link by column)",
                "Show summary statistics for all chiefdoms"
            ]
        )
        
        linked_data = None
        
        if link_option == "Different data per chiefdom (link by column)":
            # Try to find a column that matches chiefdom names
            potential_columns = [col for col in df.columns if df[col].dtype == 'object']
            
            if potential_columns:
                link_column = st.selectbox(
                    "Select column that contains chiefdom names:",
                    options=potential_columns,
                    help="Choose the column that contains names matching your shapefile chiefdoms"
                )
                
                # Show matching analysis
                chiefdom_names = set(shapefile['FIRST_CHIE'].str.upper().str.strip())
                data_names = set(df[link_column].str.upper().str.strip()) if df[link_column].dtype == 'object' else set()
                
                matches = chiefdom_names.intersection(data_names)
                st.write(f"**Matching analysis:**")
                st.write(f"- Chiefdoms in shapefile: {len(chiefdom_names)}")
                st.write(f"- Unique values in data: {len(data_names)}")
                st.write(f"- **Matches found: {len(matches)}**")
                
                if matches:
                    st.success(f"✅ Found {len(matches)} matching chiefdom names!")
                    with st.expander("View Matches"):
                        st.write(sorted(matches))
                    
                    # Create linked data
                    df_upper = df.copy()
                    df_upper[link_column] = df_upper[link_column].str.upper().str.strip()
                    linked_data = df_upper
                else:
                    st.warning("⚠️ No exact matches found. Data will be applied to all chiefdoms.")
            else:
                st.warning("⚠️ No text columns found for linking. Using same data for all chiefdoms.")
        
        elif link_option == "Show summary statistics for all chiefdoms":
            # Create summary statistics
            summary_data = {}
            for col in df.columns:
                if df[col].dtype in ['float64', 'int64']:
                    summary_data[f"{col}_mean"] = df[col].mean()
                    summary_data[f"{col}_sum"] = df[col].sum()
                    summary_data[f"{col}_count"] = df[col].count()
                elif df[col].dtype == 'object':
                    summary_data[f"{col}_unique"] = df[col].nunique()
                    summary_data[f"{col}_mode"] = df[col].mode().iloc[0] if len(df[col].mode()) > 0 else "N/A"
            
            # Convert to single row dataframe
            linked_data = pd.DataFrame([summary_data])
        
        # Step 2: Select variables for hover popup
        st.markdown("### 🎯 Step 2: Select Variables for Interactive Popup")
        st.markdown("Choose which columns you want to display when hovering over each chiefdom center:")
        
        # Use appropriate dataframe for variable selection
        source_df = linked_data if linked_data is not None else df
        
        # Create columns for better layout
        n_cols = 3
        cols = st.columns(n_cols)
        
        selected_vars = []
        available_columns = list(source_df.columns)
        
        for i, col in enumerate(available_columns):
            with cols[i % n_cols]:
                if st.checkbox(f"📌 {col}", key=f"var_{col}"):
                    selected_vars.append(col)
        
        # Quick select options
        st.markdown("#### 🚀 Quick Select Options:")
        quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)
        
        with quick_col1:
            if st.button("Select All"):
                for col in available_columns:
                    st.session_state[f"var_{col}"] = True
                st.experimental_rerun()
        
        with quick_col2:
            if st.button("Clear All"):
                for col in available_columns:
                    st.session_state[f"var_{col}"] = False
                st.experimental_rerun()
        
        with quick_col3:
            if st.button("Text Columns Only"):
                for col in available_columns:
                    if source_df[col].dtype == 'object':
                        st.session_state[f"var_{col}"] = True
                    else:
                        st.session_state[f"var_{col}"] = False
                st.experimental_rerun()
        
        with quick_col4:
            if st.button("Numeric Columns Only"):
                for col in available_columns:
                    if source_df[col].dtype in ['float64', 'int64']:
                        st.session_state[f"var_{col}"] = True
                    else:
                        st.session_state[f"var_{col}"] = False
                st.experimental_rerun()

        # Update selected_vars based on session state
        selected_vars = [col for col in available_columns if st.session_state.get(f"var_{col}", False)]

        if selected_vars:
            st.success(f"✅ Selected {len(selected_vars)} variables for display: {', '.join(selected_vars)}")
            
            # Step 3: Customize appearance
            st.markdown("### 🎨 Step 3: Customize Map Appearance")
            
            appearance_col1, appearance_col2, appearance_col3 = st.columns(3)
            
            with appearance_col1:
                point_size = st.slider("Point Size", 8, 30, 15)
                point_color = st.color_picker("Point Color", "#FF6B6B")
            
            with appearance_col2:
                boundary_color = st.color_picker("Boundary Color", "#2E86AB")
                boundary_width = st.slider("Boundary Width", 1, 5, 2)
            
            with appearance_col3:
                map_height = st.slider("Map Height", 400, 1000, 700)
                point_opacity = st.slider("Point Opacity", 0.3, 1.0, 0.9)

            # Optional: Filter by district
            if 'FIRST_DNAM' in shapefile.columns:
                st.markdown("#### 🗺️ Optional: Filter by District")
                districts = ['All Districts'] + sorted(shapefile['FIRST_DNAM'].unique())
                selected_district = st.selectbox("Select District (optional)", districts)
            else:
                selected_district = 'All Districts'

            # Step 4: Generate Map
            st.markdown("### 🚀 Step 4: Generate Your Interactive Map")
            
            if st.button("🗺️ Generate Chiefdom Centers Map", type="primary", use_container_width=True):
                with st.spinner("Creating your interactive map with chiefdom centers..."):
                    
                    # Filter shapefile by district if selected
                    if selected_district != 'All Districts':
                        filtered_shapefile = shapefile[shapefile['FIRST_DNAM'] == selected_district].copy()
                    else:
                        filtered_shapefile = shapefile.copy()
                    
                    if len(filtered_shapefile) == 0:
                        st.error("❌ No chiefdoms found for selected district!")
                        st.stop()
                    
                    # Create hover template function
                    def create_hover_template(chiefdom_name, row_data=None):
                        hover_parts = [f"<b>🏛️ {chiefdom_name}</b><br>"]
                        hover_parts.append("=" * 40 + "<br>")
                        
                        if row_data is not None:
                            for var in selected_vars:
                                if var in row_data.index and pd.notna(row_data[var]):
                                    value = row_data[var]
                                    if isinstance(value, float):
                                        if value.is_integer():
                                            value = int(value)
                                        else:
                                            value = f"{value:.3f}"
                                    
                                    hover_parts.append(f"<b>{var}:</b> {value}<br>")
                        else:
                            # Use default row data
                            if link_option == "Same data for all chiefdoms" and len(df) > 0:
                                default_row = df.iloc[0]
                                for var in selected_vars:
                                    if var in default_row.index and pd.notna(default_row[var]):
                                        value = default_row[var]
                                        if isinstance(value, float):
                                            if value.is_integer():
                                                value = int(value)
                                            else:
                                                value = f"{value:.3f}"
                                        hover_parts.append(f"<b>{var}:</b> {value}<br>")
                        
                        hover_parts.append(f"<br><b>📍 Coordinates:</b><br>")
                        hover_parts.append(f"Lat: {filtered_shapefile[filtered_shapefile['FIRST_CHIE'] == chiefdom_name]['center_lat'].iloc[0]:.6f}<br>")
                        hover_parts.append(f"Lon: {filtered_shapefile[filtered_shapefile['FIRST_CHIE'] == chiefdom_name]['center_lon'].iloc[0]:.6f}")
                        hover_parts.append(f"<br><i>💡 Click for detailed view</i>")
                        
                        return "".join(hover_parts) + "<extra></extra>"

                    # Create figure
                    fig = go.Figure()
                    
                    # Add chiefdom boundaries
                    for _, boundary in filtered_shapefile.iterrows():
                        boundary_geojson = boundary.geometry.__geo_interface__
                        
                        # Handle both Polygon and MultiPolygon
                        coords_list = []
                        if boundary_geojson['type'] == 'Polygon':
                            coords_list = [boundary_geojson['coordinates'][0]]
                        elif boundary_geojson['type'] == 'MultiPolygon':
                            coords_list = [poly[0] for poly in boundary_geojson['coordinates']]
                        
                        chiefdom_name = boundary.get('FIRST_CHIE', 'Unknown')
                        
                        for coords in coords_list:
                            fig.add_trace(
                                go.Scatter(
                                    mode='lines',
                                    x=[coord[0] for coord in coords],
                                    y=[coord[1] for coord in coords],
                                    line=dict(color=boundary_color, width=boundary_width),
                                    name=f"Boundary: {chiefdom_name}",
                                    showlegend=False,
                                    hovertemplate=f"<b>🗺️ {chiefdom_name} Boundary</b><extra></extra>",
                                    fill='none'
                                )
                            )

                    # Add center points for each chiefdom
                    center_lats = []
                    center_lons = []
                    hover_templates = []
                    point_names = []
                    
                    for _, chiefdom in filtered_shapefile.iterrows():
                        chiefdom_name = chiefdom['FIRST_CHIE']
                        center_lat = chiefdom['center_lat']
                        center_lon = chiefdom['center_lon']
                        
                        center_lats.append(center_lat)
                        center_lons.append(center_lon)
                        point_names.append(chiefdom_name)
                        
                        # Get data for this chiefdom
                        chiefdom_data = None
                        if link_option == "Different data per chiefdom (link by column)" and linked_data is not None:
                            matching_rows = linked_data[linked_data[link_column].str.upper().str.strip() == chiefdom_name.upper().strip()]
                            if len(matching_rows) > 0:
                                chiefdom_data = matching_rows.iloc[0]
                        elif link_option == "Show summary statistics for all chiefdoms" and linked_data is not None:
                            chiefdom_data = linked_data.iloc[0]
                        
                        hover_template = create_hover_template(chiefdom_name, chiefdom_data)
                        hover_templates.append(hover_template)
                    
                    # Add all center points as one trace
                    fig.add_trace(
                        go.Scatter(
                            x=center_lons,
                            y=center_lats,
                            mode='markers',
                            marker=dict(
                                size=point_size,
                                color=point_color,
                                opacity=point_opacity,
                                symbol='circle'
                            ),
                            hovertemplate=hover_templates,
                            name=f'Chiefdom Centers ({len(center_lats)})',
                            text=point_names
                        )
                    )

                    # Calculate bounds for the map
                    bounds = filtered_shapefile.total_bounds
                    center_lat = (bounds[1] + bounds[3]) / 2
                    center_lon = (bounds[0] + bounds[2]) / 2

                    # Update layout for shapefile-only view
                    fig.update_layout(
                        height=map_height,
                        title={
                            'text': f"Interactive Chiefdom Centers Map<br><small>{len(filtered_shapefile)} chiefdoms with {len(selected_vars)} data variables</small>",
                            'y': 0.98,
                            'x': 0.5,
                            'xanchor': 'center',
                            'yanchor': 'top',
                            'font': {'size': 18}
                        },
                        xaxis=dict(
                            title='Longitude',
                            range=[bounds[0] - 0.01, bounds[2] + 0.01],
                            showgrid=True,
                            gridcolor='lightgray'
                        ),
                        yaxis=dict(
                            title='Latitude',
                            range=[bounds[1] - 0.01, bounds[3] + 0.01],
                            showgrid=True,
                            gridcolor='lightgray',
                            scaleanchor="x",
                            scaleratio=1
                        ),
                        showlegend=True,
                        legend=dict(
                            yanchor="top",
                            y=0.99,
                            xanchor="left",
                            x=0.01,
                            bgcolor="rgba(255,255,255,0.8)",
                            bordercolor="rgba(0,0,0,0.2)",
                            borderwidth=1
                        ),
                        margin=dict(t=100, r=30, l=30, b=30),
                        plot_bgcolor='white',
                        paper_bgcolor='white'
                    )

                    # Display the map
                    st.plotly_chart(fig, use_container_width=True, config={
                        'displayModeBar': True,
                        'scrollZoom': True,
                        'displaylogo': False,
                        'toImageButtonOptions': {
                            'format': 'png',
                            'filename': 'chiefdom_centers_map',
                            'height': map_height,
                            'width': 1200,
                            'scale': 2
                        }
                    })

                    # Display summary information
                    st.markdown("### 📊 Map Summary")
                    
                    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
                    
                    with summary_col1:
                        st.metric("Chiefdoms Displayed", len(filtered_shapefile))
                    with summary_col2:
                        st.metric("Variables per Point", len(selected_vars))
                    with summary_col3:
                        if selected_district != 'All Districts':
                            st.metric("District", selected_district)
                        else:
                            districts_shown = filtered_shapefile['FIRST_DNAM'].nunique()
                            st.metric("Districts Shown", districts_shown)
                    with summary_col4:
                        st.metric("Map Center", f"{center_lat:.3f}, {center_lon:.3f}")

                    # Show chiefdom list
                    with st.expander("📋 Chiefdom Centers List"):
                        chiefdom_list = filtered_shapefile[['FIRST_CHIE', 'FIRST_DNAM', 'center_lat', 'center_lon']].copy()
                        chiefdom_list['center_lat'] = chiefdom_list['center_lat'].round(6)
                        chiefdom_list['center_lon'] = chiefdom_list['center_lon'].round(6)
                        st.dataframe(chiefdom_list)

                    # Download options
                    st.markdown("### 💾 Download Options")
                    
                    download_col1, download_col2 = st.columns(2)
                    
                    with download_col1:
                        # HTML download
                        html_map = fig.to_html(
                            config={
                                'displayModeBar': True,
                                'scrollZoom': True,
                                'displaylogo': False,
                                'responsive': True
                            },
                            include_plotlyjs='cdn'
                        )
                        
                        st.download_button(
                            label="🌐 Download Interactive Map (HTML)",
                            data=html_map,
                            file_name="chiefdom_centers_map.html",
                            mime="text/html"
                        )
                    
                    with download_col2:
                        # CSV download of centers
                        centers_csv = filtered_shapefile[['FIRST_CHIE', 'FIRST_DNAM', 'center_lat', 'center_lon']].to_csv(index=False)
                        st.download_button(
                            label="📊 Download Centers Data (CSV)",
                            data=centers_csv,
                            file_name="chiefdom_centers.csv",
                            mime="text/csv"
                        )

                    st.success("🎉 Interactive chiefdom centers map generated successfully!")

        else:
            st.warning("⚠️ Please select at least one variable to display in the popup.")

    except Exception as e:
        st.error(f"❌ Error reading the Excel file: {str(e)}")
        st.markdown("""
        **Common issues:**
        - Make sure the file is a valid Excel file (.xlsx or .xls)
        - Check that the file is not corrupted
        - Ensure the file contains data with proper column headers
        """)

else:
    st.info("👆 Please upload an Excel file to get started.")
    
    # Show example of what the app can do
    st.markdown("""
    ### 🎯 What This App Does:
    
    1. **🗺️ Loads your shapefile** automatically (Chiefdom 2021.shp)
    2. **📍 Calculates center points** for each chiefdom automatically
    3. **📁 Upload Excel data** to display at each center point
    4. **🔗 Link data** to specific chiefdoms or use same data for all
    5. **🎯 Choose variables** to show in interactive popups
    6. **🎨 Customize appearance** and filter by district
    7. **🗺️ Generate pure shapefile map** (no external map tiles needed)
    
    ### 📋 Features:
    - **One interactive point per chiefdom** at geometric center
    - **Automatic center calculation** using shapefile geometry
    - **Pure shapefile visualization** (no Google Maps or external tiles)
    - **Custom hover popups** with your selected Excel variables
    - **District filtering** for focused views
    - **Data linking options** for chiefdom-specific information
    - **Clean boundary display** with customizable styling
    
    ### 🌟 Perfect For:
    - Regional data visualization
    - Administrative boundary analysis
    - Chiefdom-level statistics display
    - Local government data presentation
    """)

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** The map will show one interactive point at the center of each chiefdom with your selected data variables!")
