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
        gdf = gpd.read_file("Chiefdom 2021.shp")
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
    
    # Create sidebar filters early so they're available for all sections
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
    
    # Display Dual Maps at the top
    st.subheader("🗺️ Geographic Distribution Maps")
    
    if gdf is not None and "GPS Location" in extracted_df.columns:
        # Define specific districts for left and right maps
        left_district = "BO"
        right_district = "BOMBALI"
        
        # Create two columns for side-by-side maps
        col1, col2 = st.columns(2)
        
        # LEFT MAP - BO District with its Chiefdoms
        with col1:
            st.write(f"**{left_district} District - All Chiefdoms**")
            
            # Filter data for BO district
            district_data = extracted_df[extracted_df["District"] == left_district].copy()
                
                if len(district_data) > 0:
                    # Extract GPS coordinates for this district
                    gps_data = district_data["GPS Location"].dropna()
                    coords_extracted = []
                    
                    for gps_val in gps_data:
                        coords = re.findall(r'-?\d+\.?\d*', str(gps_val))
                        if len(coords) >= 2:
                            coords_extracted.append([float(coords[0]), float(coords[1])])
                        else:
                            coords_extracted.append([None, None])
                    
                    # Create map data
                    map_data_left = district_data.copy()
                    map_data_left['temp_lat'] = [coord[0] if i < len(coords_extracted) and coord[0] is not None else np.nan 
                                               for i, coord in enumerate(coords_extracted + [[None, None]] * max(0, len(map_data_left) - len(coords_extracted)))]
                    map_data_left['temp_lon'] = [coord[1] if i < len(coords_extracted) and coord[1] is not None else np.nan 
                                               for i, coord in enumerate(coords_extracted + [[None, None]] * max(0, len(map_data_left) - len(coords_extracted)))]
                    
                    # Remove rows with missing GPS data
                    map_data_left = map_data_left.dropna(subset=['temp_lat', 'temp_lon'])
                    
                    if len(map_data_left) > 0:
                        # Calculate total enrollment
                        map_data_left["Total Enrollment"] = 0
                        for class_num in range(1, 6):
                            total_col = f"Number of enrollments in class {class_num}"
                            if total_col in map_data_left.columns:
                                map_data_left["Total Enrollment"] += map_data_left[total_col].fillna(0)
                        
                        # Create the left plot
                        fig_left, ax_left = plt.subplots(figsize=(8, 8))
                        
                        # Filter shapefile to show only chiefdoms of BO district
                        district_gdf = gdf[gdf['FIRST_DNAM'] == left_district] if 'FIRST_DNAM' in gdf.columns else gdf
                        
                        # Plot shapefile boundaries in white with black edges
                        district_gdf.plot(ax=ax_left, color='white', edgecolor='black', alpha=0.8, linewidth=1)
                        
                        # Plot school points in blue
                        ax_left.scatter(
                            map_data_left['temp_lon'], 
                            map_data_left['temp_lat'],
                            c='blue',
                            s=60,  # Fixed size for better visibility
                            alpha=0.8,
                            edgecolors='darkblue',
                            linewidth=1
                        )
                        
                        # Customize plot
                        ax_left.set_title(f'{left_district} District\nSchools: {len(map_data_left)}', fontsize=12, fontweight='bold')
                        ax_left.set_xlabel('Longitude')
                        ax_left.set_ylabel('Latitude')
                        
                        # Remove axis ticks for cleaner look
                        ax_left.set_xticks([])
                        ax_left.set_yticks([])
                        
                        plt.tight_layout()
                        st.pyplot(fig_left)
                        
                        # Display chiefdoms in this district
                        unique_chiefdoms = map_data_left['Chiefdom'].dropna().unique()
                        st.write(f"**Chiefdoms ({len(unique_chiefdoms)}):** {', '.join(unique_chiefdoms)}")
                        
                        # Summary metrics
                        st.metric("Total Students", int(map_data_left['Total Enrollment'].sum()))
                    else:
                        st.warning("No valid GPS coordinates found for this district.")
                else:
                    st.warning(f"No data found for {left_district} district.")
            
            # RIGHT MAP - BOMBALI District
            with col2:
                st.write(f"**{right_district} District - All Chiefdoms**")
                
                # Filter data for BOMBALI district
                bombali_data = extracted_df[extracted_df["District"] == right_district].copy()
                
                if len(bombali_data) > 0:
                    # Extract GPS coordinates for BOMBALI district
                    gps_data = bombali_data["GPS Location"].dropna()
                    coords_extracted = []
                    
                    for gps_val in gps_data:
                        coords = re.findall(r'-?\d+\.?\d*', str(gps_val))
                        if len(coords) >= 2:
                            coords_extracted.append([float(coords[0]), float(coords[1])])
                        else:
                            coords_extracted.append([None, None])
                    
                    # Create map data
                    map_data_right = bombali_data.copy()
                    map_data_right['temp_lat'] = [coord[0] if i < len(coords_extracted) and coord[0] is not None else np.nan 
                                                for i, coord in enumerate(coords_extracted + [[None, None]] * max(0, len(map_data_right) - len(coords_extracted)))]
                    map_data_right['temp_lon'] = [coord[1] if i < len(coords_extracted) and coord[1] is not None else np.nan 
                                                for i, coord in enumerate(coords_extracted + [[None, None]] * max(0, len(map_data_right) - len(coords_extracted)))]
                    
                    # Remove rows with missing GPS data
                    map_data_right = map_data_right.dropna(subset=['temp_lat', 'temp_lon'])
                    
                    if len(map_data_right) > 0:
                        # Calculate total enrollment
                        map_data_right["Total Enrollment"] = 0
                        for class_num in range(1, 6):
                            total_col = f"Number of enrollments in class {class_num}"
                            if total_col in map_data_right.columns:
                                map_data_right["Total Enrollment"] += map_data_right[total_col].fillna(0)
                        
                        # Create the right plot
                        fig_right, ax_right = plt.subplots(figsize=(8, 8))
                        
                        # Filter shapefile to show only chiefdoms of BOMBALI district
                        bombali_gdf = gdf[gdf['FIRST_DNAM'] == right_district] if 'FIRST_DNAM' in gdf.columns else gdf
                        
                        # Plot shapefile boundaries in white with black edges
                        bombali_gdf.plot(ax=ax_right, color='white', edgecolor='black', alpha=0.8, linewidth=1)
                        
                        # Plot school points in blue
                        ax_right.scatter(
                            map_data_right['temp_lon'], 
                            map_data_right['temp_lat'],
                            c='blue',
                            s=60,  # Fixed size for better visibility
                            alpha=0.8,
                            edgecolors='darkblue',
                            linewidth=1
                        )
                        
                        # Customize plot
                        ax_right.set_title(f'{right_district} District\nSchools: {len(map_data_right)}', fontsize=12, fontweight='bold')
                        ax_right.set_xlabel('Longitude')
                        ax_right.set_ylabel('Latitude')
                        
                        # Remove axis ticks for cleaner look
                        ax_right.set_xticks([])
                        ax_right.set_yticks([])
                        
                        plt.tight_layout()
                        st.pyplot(fig_right)
                        
                        # Display chiefdoms in BOMBALI district
                        unique_chiefdoms = map_data_right['Chiefdom'].dropna().unique()
                        st.write(f"**Chiefdoms ({len(unique_chiefdoms)}):** {', '.join(unique_chiefdoms)}")
                        
                        # Summary metrics
                        st.metric("Total Students", int(map_data_right['Total Enrollment'].sum()))
                    else:
                        st.warning("No valid GPS coordinates found for BOMBALI district.")
                else:
                    st.warning(f"No data found for {right_district} district.")
    else:
        st.error("Shapefile not loaded or GPS Location column not found.")
    
    # Display Original Data Sample
    st.subheader("📄 Original Data Sample")
    st.dataframe(df_original.head())
    
    # Display Extracted Data
    st.subheader("📋 Extracted Data")
    st.dataframe(extracted_df)
    
    # Add download button for CSV
    csv = extracted_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Extracted Data as CSV",
        data=csv,
        file_name="extracted_school_data.csv",
        mime="text/csv"
    )
    
    # Summary buttons section
    st.subheader("📊 Summary Reports")
    
    # Create two columns for the summary buttons
    col1, col2 = st.columns(2)
    
    # Button for District Summary
    with col1:
        district_summary_button = st.button("Show District Summary")
    
    # Button for Chiefdom Summary
    with col2:
        chiefdom_summary_button = st.button("Show Chiefdom Summary")
    
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
        
        # Download button for district summary
        district_csv = district_summary.to_csv(index=False)
        st.download_button(
            label="📥 Download District Summary as CSV",
            data=district_csv,
            file_name="district_summary.csv",
            mime="text/csv"
        )
        
        # Create a bar chart for district summary
        fig, ax = plt.subplots(figsize=(12, 8))
        district_summary.plot(kind="bar", x="District", y="Total Enrollment", ax=ax, color="blue")
        ax.set_title("📊 Total Enrollment by District")
        ax.set_xlabel("")
        ax.set_ylabel("Number of Students")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    
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
        
        # Download button for chiefdom summary
        chiefdom_csv = chiefdom_summary.to_csv(index=False)
        st.download_button(
            label="📥 Download Chiefdom Summary as CSV",
            data=chiefdom_csv,
            file_name="chiefdom_summary.csv",
            mime="text/csv"
        )
        
        # Create a temporary label for the chart
        chiefdom_summary['Label'] = chiefdom_summary['District'] + '\n' + chiefdom_summary['Chiefdom']
        
        # Create a bar chart for chiefdom summary
        fig, ax = plt.subplots(figsize=(14, 10))
        chiefdom_summary.plot(kind="barh", x="Label", y="Total Enrollment", ax=ax, color="blue")
        ax.set_title("📊 Total Enrollment by District and Chiefdom")
        ax.set_ylabel("")
        ax.set_xlabel("Number of Students")
        plt.tight_layout()
        st.pyplot(fig)
    
    # Visualization and filtering section
    st.subheader("🔍 Detailed Data Filtering and Visualization")
    
    # Check if data is available after filtering
    if not filtered_df.empty:
        st.write(f"### Filtered Data - {len(filtered_df)} records")
        st.dataframe(filtered_df)
        
        # Download button for filtered data
        filtered_csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=filtered_csv,
            file_name="filtered_data.csv",
            mime="text/csv"
        )
        
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
    else:
        st.warning("No data available for the selected filters.")
