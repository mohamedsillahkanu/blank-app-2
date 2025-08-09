import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import geopandas as gpd

st.set_page_config(layout="wide", page_title="Central Point Interactive Map")
st.title("🎯 Central Point Interactive Map Generator")
st.markdown("Upload your Excel file and create a map with one central interactive point showing your selected data!")

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
    
    st.success(f"✅ Shapefile loaded successfully! Found {len(shapefile)} boundaries.")
    
    # Show shapefile info
    with st.expander("🗺️ Shapefile Information"):
        st.write(f"**Number of boundaries:** {len(shapefile)}")
        if 'FIRST_DNAM' in shapefile.columns:
            districts = shapefile['FIRST_DNAM'].unique()
            st.write(f"**Districts found:** {', '.join(sorted(districts))}")
        st.write(f"**Columns:** {list(shapefile.columns)}")
        
        # Calculate shapefile bounds for auto-centering
        bounds = shapefile.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        st.write(f"**Auto-calculated center:** {center_lat:.4f}, {center_lon:.4f}")
        
        # Store bounds for later use
        st.session_state.shapefile_bounds = bounds
        st.session_state.auto_center = (center_lat, center_lon)
        
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
st.markdown("### 📁 Step 1: Upload Your Excel File")
uploaded_file = st.file_uploader(
    "Choose an Excel file", 
    type=['xlsx', 'xls'],
    help="Upload your Excel file containing the data you want to display"
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

        # Step 2: Select variables for hover popup
        st.markdown("### 🎯 Step 2: Select Variables for Interactive Popup")
        st.markdown("Choose which columns you want to display when hovering over the central point:")
        
        # Create columns for better layout
        n_cols = 3
        cols = st.columns(n_cols)
        
        selected_vars = []
        available_columns = list(df.columns)
        
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
                    if df[col].dtype == 'object':
                        st.session_state[f"var_{col}"] = True
                    else:
                        st.session_state[f"var_{col}"] = False
                st.experimental_rerun()
        
        with quick_col4:
            if st.button("Numeric Columns Only"):
                for col in available_columns:
                    if df[col].dtype in ['float64', 'int64']:
                        st.session_state[f"var_{col}"] = True
                    else:
                        st.session_state[f"var_{col}"] = False
                st.experimental_rerun()

        # Update selected_vars based on session state
        selected_vars = [col for col in available_columns if st.session_state.get(f"var_{col}", False)]

        if selected_vars:
            st.success(f"✅ Selected {len(selected_vars)} variables for display: {', '.join(selected_vars)}")
            
            # Step 3: Select which row to display (if multiple rows)
            st.markdown("### 📋 Step 3: Select Data Row")
            if len(df) > 1:
                st.markdown(f"Your file has {len(df)} rows. Which row would you like to display in the popup?")
                
                # Show a preview of rows to help user choose
                with st.expander("👀 Preview Rows"):
                    for idx, row in df.head(10).iterrows():
                        st.write(f"**Row {idx + 1}:** {dict(row[selected_vars] if selected_vars else row)}")
                        if idx >= 4:  # Show only first 5 rows in preview
                            if len(df) > 5:
                                st.write(f"... and {len(df) - 5} more rows")
                            break
                
                row_selection_method = st.radio(
                    "How would you like to select the row?",
                    ["Select by row number", "Select by specific value", "Show all rows as summary"]
                )
                
                if row_selection_method == "Select by row number":
                    selected_row_idx = st.selectbox(
                        "Select row number",
                        options=list(range(len(df))),
                        format_func=lambda x: f"Row {x + 1}"
                    )
                    selected_data = df.iloc[selected_row_idx]
                    display_mode = "single_row"
                    
                elif row_selection_method == "Select by specific value":
                    filter_col = st.selectbox(
                        "Select column to filter by",
                        options=df.columns.tolist()
                    )
                    unique_values = df[filter_col].dropna().unique()
                    selected_value = st.selectbox(
                        f"Select value from '{filter_col}' column",
                        options=unique_values
                    )
                    filtered_df = df[df[filter_col] == selected_value]
                    if len(filtered_df) > 0:
                        if len(filtered_df) == 1:
                            selected_data = filtered_df.iloc[0]
                            display_mode = "single_row"
                        else:
                            st.info(f"Found {len(filtered_df)} rows matching '{selected_value}'. Will show the first one.")
                            selected_data = filtered_df.iloc[0]
                            display_mode = "single_row"
                    else:
                        st.error("No rows found with that value!")
                        st.stop()
                        
                else:  # Show all rows as summary
                    selected_data = df
                    display_mode = "summary"
                    
            else:
                selected_data = df.iloc[0]
                display_mode = "single_row"
                st.info("Single row detected - will display this row's data.")

            # Step 4: Customize map appearance
            st.markdown("### 🎨 Step 4: Customize Map Appearance")
            
            appearance_col1, appearance_col2, appearance_col3 = st.columns(3)
            
            with appearance_col1:
                point_size = st.slider("Point Size", 10, 50, 25)
                point_color = st.color_picker("Point Color", "#FF6B6B")
            
            with appearance_col2:
                map_style = st.selectbox(
                    "Map Style",
                    ["carto-positron", "open-street-map", "carto-darkmatter", "satellite-streets"]
                )
                opacity = st.slider("Point Opacity", 0.3, 1.0, 0.9)
            
            with appearance_col3:
                map_height = st.slider("Map Height", 400, 1000, 600)
                show_border = st.checkbox("Show Point Border", True)

            # Map center location
            st.markdown("#### 🌍 Map Center Location")
            
            # Option to use shapefile center or custom location
            center_option = st.radio(
                "Choose center location:",
                ["Use shapefile center (auto)", "Custom coordinates"]
            )
            
            if center_option == "Use shapefile center (auto)" and 'auto_center' in st.session_state:
                center_lat, center_lon = st.session_state.auto_center
                st.info(f"Using shapefile center: {center_lat:.4f}, {center_lon:.4f}")
            else:
                location_col1, location_col2 = st.columns(2)
                
                with location_col1:
                    center_lat = st.number_input("Center Latitude", value=8.460555, format="%.6f")
                with location_col2:
                    center_lon = st.number_input("Center Longitude", value=-11.779889, format="%.6f")
                
                # Quick location presets
                st.markdown("**Quick Location Presets:**")
                preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)
                
                with preset_col1:
                    if st.button("🇺🇸 USA Center"):
                        st.session_state.preset_lat = 39.8283
                        st.session_state.preset_lon = -98.5795
                with preset_col2:
                    if st.button("🇪🇺 Europe Center"):
                        st.session_state.preset_lat = 54.5260
                        st.session_state.preset_lon = 15.2551
                with preset_col3:
                    if st.button("🌍 World Center"):
                        st.session_state.preset_lat = 0.0
                        st.session_state.preset_lon = 0.0
                with preset_col4:
                    if st.button("🇸🇱 Sierra Leone"):
                        st.session_state.preset_lat = 8.460555
                        st.session_state.preset_lon = -11.779889

                # Apply preset if selected
                if 'preset_lat' in st.session_state:
                    center_lat = st.session_state.preset_lat
                    center_lon = st.session_state.preset_lon
                    del st.session_state.preset_lat
                    del st.session_state.preset_lon
                    st.experimental_rerun()

            zoom_level = st.slider("Zoom Level", 1, 15, 8)  # Default higher zoom for shapefile view

            # Step 5: Generate Map
            st.markdown("### 🚀 Step 5: Generate Your Interactive Map")
            
            if st.button("🗺️ Generate Interactive Map", type="primary", use_container_width=True):
                with st.spinner("Creating your interactive map..."):
                    
                    # Create hover template based on display mode
                    if display_mode == "single_row":
                        def create_hover_template():
                            hover_parts = ["<b>📊 Data Information</b><br>"]
                            hover_parts.append("=" * 30 + "<br>")
                            
                            for var in selected_vars:
                                if pd.notna(selected_data[var]):
                                    # Format the value nicely
                                    value = selected_data[var]
                                    if isinstance(value, float):
                                        if value.is_integer():
                                            value = int(value)
                                        else:
                                            value = f"{value:.3f}"
                                    
                                    hover_parts.append(f"<b>{var}:</b> {value}<br>")
                            
                            hover_parts.append(f"<br><i>💡 Click for more details</i>")
                            return "".join(hover_parts) + "<extra></extra>"
                    
                    else:  # summary mode
                        def create_hover_template():
                            hover_parts = ["<b>📊 Dataset Summary</b><br>"]
                            hover_parts.append("=" * 30 + "<br>")
                            hover_parts.append(f"<b>Total Rows:</b> {len(selected_data)}<br>")
                            hover_parts.append(f"<b>Selected Variables:</b> {len(selected_vars)}<br><br>")
                            
                            # Show summary statistics for selected numeric columns
                            numeric_vars = [var for var in selected_vars if selected_data[var].dtype in ['float64', 'int64']]
                            if numeric_vars:
                                hover_parts.append("<b>📈 Numeric Summaries:</b><br>")
                                for var in numeric_vars[:3]:  # Show only first 3 to avoid clutter
                                    mean_val = selected_data[var].mean()
                                    hover_parts.append(f"• {var}: Avg {mean_val:.2f}<br>")
                            
                            # Show unique counts for categorical columns
                            categorical_vars = [var for var in selected_vars if selected_data[var].dtype == 'object']
                            if categorical_vars:
                                hover_parts.append("<br><b>📋 Categories:</b><br>")
                                for var in categorical_vars[:3]:  # Show only first 3
                                    unique_count = selected_data[var].nunique()
                                    hover_parts.append(f"• {var}: {unique_count} unique values<br>")
                            
                            hover_parts.append(f"<br><i>💡 Click for detailed breakdown</i>")
                            return "".join(hover_parts) + "<extra></extra>"

                    # Create figure
                    fig = go.Figure()
                    
                    # Add shapefile boundaries first
                    if 'shapefile' in st.session_state and st.session_state.shapefile is not None:
                        shapefile = st.session_state.shapefile
                        
                        # Add boundaries for each chiefdom/district
                        for _, boundary in shapefile.iterrows():
                            boundary_geojson = boundary.geometry.__geo_interface__
                            
                            # Handle both Polygon and MultiPolygon
                            coords_list = []
                            if boundary_geojson['type'] == 'Polygon':
                                coords_list = [boundary_geojson['coordinates'][0]]
                            elif boundary_geojson['type'] == 'MultiPolygon':
                                coords_list = [poly[0] for poly in boundary_geojson['coordinates']]
                            
                            # Get boundary name for hover
                            boundary_name = "Boundary"
                            if 'FIRST_CHIE' in boundary.index:
                                boundary_name = f"Chiefdom: {boundary['FIRST_CHIE']}"
                            elif 'FIRST_DNAM' in boundary.index:
                                boundary_name = f"District: {boundary['FIRST_DNAM']}"
                            
                            for coords in coords_list:
                                fig.add_trace(
                                    go.Scattermapbox(
                                        mode='lines',
                                        lon=[coord[0] for coord in coords],
                                        lat=[coord[1] for coord in coords],
                                        line=dict(color='rgba(0,0,0,0.6)', width=2),
                                        name=boundary_name,
                                        showlegend=False,
                                        hovertemplate=f"<b>{boundary_name}</b><extra></extra>",
                                        fill='none'
                                    )
                                )
                    
                    # Add the central point on top of boundaries
                    fig.add_trace(
                        go.Scattermapbox(
                            lat=[center_lat],
                            lon=[center_lon],
                            mode='markers',
                            marker=dict(
                                size=point_size,
                                color=point_color,
                                opacity=opacity,
                                line=dict(width=3 if show_border else 0, color='white'),
                                symbol='circle'
                            ),
                            hovertemplate=create_hover_template(),
                            name='Data Point',
                            text=['Interactive Data Point']
                        )
                    )

                    # Update layout
                    fig.update_layout(
                        height=map_height,
                        title={
                            'text': f"Interactive Map with Boundaries & Central Point<br><small>Displaying {len(selected_vars)} variables from your data</small>",
                            'y': 0.98,
                            'x': 0.5,
                            'xanchor': 'center',
                            'yanchor': 'top',
                            'font': {'size': 20}
                        },
                        mapbox=dict(
                            style=map_style,
                            center=dict(lat=center_lat, lon=center_lon),
                            zoom=zoom_level
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
                        margin=dict(t=100, r=30, l=30, b=30)
                    )

                    # Display the map
                    st.plotly_chart(fig, use_container_width=True, config={
                        'displayModeBar': True,
                        'scrollZoom': True,
                        'displaylogo': False,
                        'toImageButtonOptions': {
                            'format': 'png',
                            'filename': 'central_point_interactive_map',
                            'height': map_height,
                            'width': 1200,
                            'scale': 2
                        }
                    })

                    # Display detailed information below the map
                    st.markdown("### 📋 Detailed Data View")
                    
                    if display_mode == "single_row":
                        # Show the selected row data in a nice format
                        data_display = {}
                        for var in selected_vars:
                            if pd.notna(selected_data[var]):
                                data_display[var] = selected_data[var]
                        
                        # Create a formatted display
                        col1, col2 = st.columns(2)
                        items = list(data_display.items())
                        mid_point = len(items) // 2
                        
                        with col1:
                            for var, value in items[:mid_point]:
                                st.metric(var, value)
                        
                        with col2:
                            for var, value in items[mid_point:]:
                                st.metric(var, value)
                    
                    else:  # summary mode
                        # Show summary statistics
                        summary_stats = {}
                        for var in selected_vars:
                            if df[var].dtype in ['float64', 'int64']:
                                summary_stats[f"{var} (mean)"] = f"{df[var].mean():.2f}"
                                summary_stats[f"{var} (total)"] = f"{df[var].sum():.2f}"
                            else:
                                summary_stats[f"{var} (unique)"] = df[var].nunique()
                                summary_stats[f"{var} (most common)"] = df[var].mode().iloc[0] if len(df[var].mode()) > 0 else "N/A"
                        
                        # Display summary
                        col1, col2 = st.columns(2)
                        items = list(summary_stats.items())
                        mid_point = len(items) // 2
                        
                        with col1:
                            for key, value in items[:mid_point]:
                                st.metric(key, value)
                        
                        with col2:
                            for key, value in items[mid_point:]:
                                st.metric(key, value)

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
                            file_name="central_point_map.html",
                            mime="text/html"
                        )
                    
                    with download_col2:
                        # CSV download of selected data
                        if display_mode == "single_row":
                            csv_data = pd.DataFrame([selected_data[selected_vars]]).to_csv(index=False)
                        else:
                            csv_data = df[selected_vars].to_csv(index=False)
                        
                        st.download_button(
                            label="📊 Download Selected Data (CSV)",
                            data=csv_data,
                            file_name="selected_data.csv",
                            mime="text/csv"
                        )

                    st.success("🎉 Interactive central point map generated successfully!")

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
    
    1. **📁 Upload any Excel file** with your data
    2. **🎯 Choose which variables** to show in hover popup
    3. **📋 Select which row** to display (or show summary)
    4. **🌍 Set map center location** where the point appears
    5. **🎨 Customize appearance** (colors, size, style)
    6. **🗺️ Generate interactive map** with one central point
    7. **💾 Download** as HTML or CSV
    
    ### 📋 Requirements:
    - Excel file (.xlsx or .xls) with any structure
    - No coordinate data needed!
    
    ### 🌟 Features:
    - **Single central interactive point** placed anywhere on the map
    - **Custom hover popups** with your selected variables
    - **Multiple display modes** (single row or summary statistics)
    - **Location presets** for quick map centering
    - **Fully customizable** appearance and styling
    - **Download options** for sharing and embedding
    """)

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Perfect for displaying summary information, company data, or any dataset as a single interactive point on a map!")
