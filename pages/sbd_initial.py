import streamlit as st
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd

# Streamlit App
st.title("📊 Text Data Extraction & Visualization")

# Upload file
uploaded_file = "Report_GMB253374_SBD_1749318384635_submissions.xlsx"
if uploaded_file:
    # Read the uploaded Excel file
    df_original = pd.read_excel(uploaded_file)
    
    # Load shapefile
    try:
        gdf = gpd.read_file("Chiefdom2021.shp")
        st.success("✅ Shapefile loaded successfully!")
    except Exception as e:
        st.error(f"❌ Could not load shapefile: {e}")
        gdf = None
    
    # Create empty lists to store extracted data
    districts, chiefdoms, phu_names, community_names, school_names = [], [], [], [], []
    
    # Process each row in the "Scan QR code" column
    for qr_text in df_original["Scan QR code"]:
        if pd.isna(qr_text):
            districts.append(None)
            chiefdoms.append(None)
            phu_names.append(None)
            community_names.append(None)
            school_names.append(None)
            continue
            
        # Extract values using regex patterns
        district_match = re.search(r"District:\s*([^\n]+)", str(qr_text))
        districts.append(district_match.group(1).strip() if district_match else None)
        
        chiefdom_match = re.search(r"Chiefdom:\s*([^\n]+)", str(qr_text))
        chiefdoms.append(chiefdom_match.group(1).strip() if chiefdom_match else None)
        
        phu_match = re.search(r"PHU name:\s*([^\n]+)", str(qr_text))
        phu_names.append(phu_match.group(1).strip() if phu_match else None)
        
        community_match = re.search(r"Community name:\s*([^\n]+)", str(qr_text))
        community_names.append(community_match.group(1).strip() if community_match else None)
        
        school_match = re.search(r"Name of school:\s*([^\n]+)", str(qr_text))
        school_names.append(school_match.group(1).strip() if school_match else None)
    
    # Create a new DataFrame with extracted values
    extracted_df = pd.DataFrame({
        "District": districts,
        "Chiefdom": chiefdoms,
        "PHU Name": phu_names,
        "Community Name": community_names,
        "School Name": school_names
    })
    
    # Add all other columns from the original DataFrame
    for column in df_original.columns:
        if column != "Scan QR code":  # Skip the QR code column since we've already processed it
            extracted_df[column] = df_original[column]
    
    # Display Original Data Sample
    st.subheader("📄 Original Data Sample")
    st.dataframe(df_original.head())
    
    # Display Extracted Data
    st.subheader("📋 Extracted Data")
    st.dataframe(extracted_df)
    
    # Summary buttons section
    st.subheader("📊 Summary Reports")
    
    # Create three columns for the summary buttons
    col1, col2, col3 = st.columns(3)
    
    # Button for District Summary
    with col1:
        district_summary_button = st.button("Show District Summary")
    
    # Button for Chiefdom Summary
    with col2:
        chiefdom_summary_button = st.button("Show Chiefdom Summary")
    
    # Button for Map View
    with col3:
        map_button = st.button("Show Map")
    
    # Display District Summary when button is clicked
    if district_summary_button:
        st.subheader("📈 Summary by District")
        
        # Create aggregation dictionary
        agg_dict = {}
        
        # Add enrollment columns to aggregation
        for class_num in range(1, 6):
            total_col = f"Number of enrollments in class {class_num}"
            boys_col = f"Number of boys in class {class_num}"
            girls_col = f"Number of girls in class {class_num}"
            
            if total_col in extracted_df.columns:
                agg_dict[total_col] = "sum"
            if boys_col in extracted_df.columns:
                agg_dict[boys_col] = "sum"
            if girls_col in extracted_df.columns:
                agg_dict[girls_col] = "sum"
        
        # Group by District and aggregate
        district_summary = extracted_df.groupby("District").agg(agg_dict).reset_index()
        
        # Calculate total enrollment
        district_summary["Total Enrollment"] = 0
        for class_num in range(1, 6):
            total_col = f"Number of enrollments in class {class_num}"
            if total_col in district_summary.columns:
                district_summary["Total Enrollment"] += district_summary[total_col]
        
        # Display summary table
        st.dataframe(district_summary)
        
        # Create a bar chart for district summary
        fig, ax = plt.subplots(figsize=(12, 8))
        district_summary.plot(kind="bar", x="District", y="Total Enrollment", ax=ax, color="blue")
        ax.set_title("📊 Total Enrollment by District")
        ax.set_xlabel("")
        ax.set_ylabel("Number of Students")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    
    # Display Map when button is clicked
    if map_button:
        st.subheader("🗺️ Geographic Distribution Map")
        
        if gdf is not None:
            # District name mapping (your data -> shapefile)
            district_mapping = {
                'Bo': 'BO',
                'Bombali': 'BOMBALI',
                # Add more mappings as needed
            }
            
            # Auto-detect GPS columns
            gps_columns = []
            lat_col = None
            lon_col = None
            
            # Look for the specific "GPS Location" column
            if "GPS Location" in extracted_df.columns:
                gps_data = extracted_df["GPS Location"].dropna()
                if len(gps_data) > 0:
                    # Try to parse GPS Location column (assuming it contains lat,lon or similar format)
                    sample = str(gps_data.iloc[0])
                    st.write(f"GPS Location format detected: {sample}")
                    
                    # Extract coordinates from GPS Location
                    coords_extracted = []
                    for gps_val in gps_data:
                        coords = re.findall(r'-?\d+\.?\d*', str(gps_val))
                        if len(coords) >= 2:
                            coords_extracted.append([float(coords[0]), float(coords[1])])
                        else:
                            coords_extracted.append([None, None])
                    
                    # Create temporary lat/lon columns
                    map_data = extracted_df.copy()
                    map_data['temp_lat'] = [coord[0] if coord[0] is not None else np.nan for coord in coords_extracted + [[None, None]] * (len(map_data) - len(coords_extracted))]
                    map_data['temp_lon'] = [coord[1] if coord[1] is not None else np.nan for coord in coords_extracted + [[None, None]] * (len(map_data) - len(coords_extracted))]
                    
                    lat_col = 'temp_lat'
                    lon_col = 'temp_lon'
                    
            else:
                # Fallback to original GPS detection method
                for col in extracted_df.columns:
                    col_lower = col.lower()
                    if any(gps_name in col_lower for gps_name in ['gps', 'latitude', 'longitude', 'lat', 'lon']):
                        gps_columns.append(col)
                
                if len(gps_columns) >= 2:
                    for col in gps_columns:
                        col_lower = col.lower()
                        if 'lat' in col_lower and lat_col is None:
                            lat_col = col
                        elif 'lon' in col_lower and lon_col is None:
                            lon_col = col
                    
                    if lat_col is None or lon_col is None:
                        lat_col = gps_columns[0]
                        lon_col = gps_columns[1]
                    
                    map_data = extracted_df.copy()
            
            if lat_col and lon_col:
                
                st.write(f"Using GPS column: GPS Location")
                
                # Get selected district from sidebar filter if available
                selected_district = None
                if 'District' in selected_values:
                    selected_district = selected_values['District']
                
                # Filter by district if selected
                if selected_district:
                    map_data = map_data[map_data['District'] == selected_district]
                    st.write(f"Showing data for: {selected_district}")
                
                # Clean GPS data for non-GPS Location columns
                if lat_col not in ['temp_lat', 'temp_lon']:
                    for col in [lat_col, lon_col]:
                        if col in map_data.columns:
                            map_data[col] = map_data[col].astype(str).str.extract(r'(-?\d+\.?\d*)')[0]
                            map_data[col] = pd.to_numeric(map_data[col], errors='coerce')
                
                # Remove rows with missing GPS data
                map_data = map_data.dropna(subset=[lat_col, lon_col])
                
                if len(map_data) > 0:
                    # Calculate total enrollment
                    map_data["Total Enrollment"] = 0
                    for class_num in range(1, 6):
                        total_col = f"Number of enrollments in class {class_num}"
                        if total_col in map_data.columns:
                            map_data["Total Enrollment"] += map_data[total_col].fillna(0)
                    
                    # Filter shapefile by selected district
                    gdf_filtered = gdf.copy()
                    if selected_district:
                        # Map district name to shapefile format
                        shapefile_district = district_mapping.get(selected_district, selected_district.upper())
                        gdf_filtered = gdf[gdf['FIRST_DIST'].str.upper() == shapefile_district.upper()]
                    
                    # Create the plot
                    fig, ax = plt.subplots(figsize=(12, 10))
                    
                    # Plot shapefile boundaries
                    gdf_filtered.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.5)
                    
                    # Plot school points
                    scatter = ax.scatter(
                        map_data[lon_col], 
                        map_data[lat_col],
                        c=map_data['Total Enrollment'],
                        s=map_data['Total Enrollment']/10,  # Size based on enrollment
                        cmap='viridis',
                        alpha=0.7,
                        edgecolors='black',
                        linewidth=0.5
                    )
                    
                    # Add colorbar
                    cbar = plt.colorbar(scatter, ax=ax)
                    cbar.set_label('Total Enrollment', rotation=270, labelpad=15)
                    
                    # Customize plot
                    ax.set_title(f'School Distribution Map{" - " + selected_district if selected_district else ""}')
                    ax.set_xlabel('Longitude')
                    ax.set_ylabel('Latitude')
                    
                    # Remove axis ticks for cleaner look
                    ax.set_xticks([])
                    ax.set_yticks([])
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Display summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Schools Plotted", len(map_data))
                    with col2:
                        st.metric("Total Students", int(map_data['Total Enrollment'].sum()))
                    with col3:
                        st.metric("Avg Students/School", int(map_data['Total Enrollment'].mean()))
                    
                    # Show schools data table
                    if st.checkbox("Show school details"):
                        display_cols = ['School Name', 'District', 'Chiefdom', 'Total Enrollment']
                        if all(col in map_data.columns for col in display_cols):
                            st.dataframe(map_data[display_cols].sort_values('Total Enrollment', ascending=False))
                    
                else:
                    st.warning("No valid GPS coordinates found in the filtered data.")
            else:
                st.warning("GPS Location column not found and no other GPS columns detected.")
        else:
            st.error("Shapefile not loaded. Cannot display map.")
    
    # Display Chiefdom Summary when button is clicked
    if chiefdom_summary_button:
        st.subheader("📈 Summary by Chiefdom")
        
        # Create aggregation dictionary
        agg_dict = {}
        
        # Add enrollment columns to aggregation
        for class_num in range(1, 6):
            total_col = f"Number of enrollments in class {class_num}"
            boys_col = f"Number of boys in class {class_num}"
            girls_col = f"Number of girls in class {class_num}"
            
            if total_col in extracted_df.columns:
                agg_dict[total_col] = "sum"
            if boys_col in extracted_df.columns:
                agg_dict[boys_col] = "sum"
            if girls_col in extracted_df.columns:
                agg_dict[girls_col] = "sum"
        
        # Group by District and Chiefdom and aggregate
        chiefdom_summary = extracted_df.groupby(["District", "Chiefdom"]).agg(agg_dict).reset_index()
        
        # Calculate total enrollment
        chiefdom_summary["Total Enrollment"] = 0
        for class_num in range(1, 6):
            total_col = f"Number of enrollments in class {class_num}"
            if total_col in chiefdom_summary.columns:
                chiefdom_summary["Total Enrollment"] += chiefdom_summary[total_col]
        
        # Display summary table
        st.dataframe(chiefdom_summary)
        
        # Create a temporary label for the chart
        chiefdom_summary['Label'] = chiefdom_summary['District'] + '\n' + chiefdom_summary['Chiefdom']
        
        # Create a bar chart for chiefdom summary
        fig, ax = plt.subplots(figsize=(14, 10))
        chiefdom_summary.plot(kind="bar", x="Label", y="Total Enrollment", ax=ax, color="blue")
        ax.set_title("📊 Total Enrollment by District and Chiefdom")
        ax.set_xlabel("")
        ax.set_ylabel("Number of Students")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    
    # Visualization and filtering section
    st.subheader("🔍 Detailed Data Filtering and Visualization")
    
    # Create a sidebar for filtering options
    st.sidebar.header("Filter Options")
    
    # Create radio buttons to select which level to group by
    grouping_selection = st.sidebar.radio(
        "Select the level for grouping:",
        ["District", "Chiefdom", "PHU Name", "Community Name", "School Name"],
        index=0  # Default to 'District'
    )
    
    # Dictionary to define the hierarchy for each grouping level
    hierarchy = {
        "District": ["District"],
        "Chiefdom": ["District", "Chiefdom"],
        "PHU Name": ["District", "Chiefdom", "PHU Name"],
        "Community Name": ["District", "Chiefdom", "PHU Name", "Community Name"],
        "School Name": ["District", "Chiefdom", "PHU Name", "Community Name", "School Name"]
    }
    
    # Initialize filtered dataframe with the full dataset
    filtered_df = extracted_df.copy()
    
    # Dictionary to store selected values for each level
    selected_values = {}
    
    # Apply filters based on the hierarchy for the selected grouping level
    for level in hierarchy[grouping_selection]:
        # Filter out None/NaN values and get sorted unique values
        level_values = sorted(filtered_df[level].dropna().unique())
        
        if level_values:
            # Create selectbox for this level
            selected_value = st.sidebar.selectbox(f"Select {level}", level_values)
            selected_values[level] = selected_value
            
            # Apply filter to the dataframe
            filtered_df = filtered_df[filtered_df[level] == selected_value]
    
    # Check if data is available after filtering
    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:
        st.write(f"### Filtered Data - {len(filtered_df)} records")
        st.dataframe(filtered_df)
        
        # Define the hierarchy levels to include in the summary
        group_columns = hierarchy[grouping_selection]
        
        # Create aggregation dictionary for enrollment data
        agg_dict = {}
        for class_num in range(1, 6):
            total_col = f"Number of enrollments in class {class_num}"
            boys_col = f"Number of boys in class {class_num}"
            girls_col = f"Number of girls in class {class_num}"
            
            if total_col in filtered_df.columns:
                agg_dict[total_col] = "sum"
            if boys_col in filtered_df.columns:
                agg_dict[boys_col] = "sum"
            if girls_col in filtered_df.columns:
                agg_dict[girls_col] = "sum"
        
        # Group by the selected hierarchical columns
        grouped_data = filtered_df.groupby(group_columns).agg(agg_dict).reset_index()
        
        # Calculate total enrollment
        grouped_data["Total Enrollment"] = 0
        for class_num in range(1, 6):
            total_col = f"Number of enrollments in class {class_num}"
            if total_col in grouped_data.columns:
                grouped_data["Total Enrollment"] += grouped_data[total_col]
        
        # Summary Table with separate columns for each level
        st.subheader("📊 Detailed Summary Table")
        st.dataframe(grouped_data)
        
        # Create a temporary group column for the chart
        grouped_data['Group'] = grouped_data[group_columns].apply(lambda row: ','.join(row.astype(str)), axis=1)
        
        # Create a bar chart
        fig, ax = plt.subplots(figsize=(12, 8))
        grouped_data.plot(kind="bar", x="Group", y="Total Enrollment", ax=ax, color="blue")
        ax.set_title(f"Total Enrollment by {grouping_selection}")
        
        # Remove x-label as requested
        ax.set_xlabel("")
        
        ax.set_ylabel("Number of Students")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
