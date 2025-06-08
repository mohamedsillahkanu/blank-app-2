import streamlit as st
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px

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
            # Check for GPS columns
            gps_columns = []
            possible_gps_names = ['GPS', 'gps', 'Latitude', 'Longitude', 'lat', 'lon', 'LAT', 'LON', 'latitude', 'longitude']
            
            for col in extracted_df.columns:
                if any(gps_name in col for gps_name in possible_gps_names):
                    gps_columns.append(col)
            
            if gps_columns:
                st.write(f"Found GPS columns: {gps_columns}")
                
                # Let user select GPS columns
                col1, col2 = st.columns(2)
                with col1:
                    lat_col = st.selectbox("Select Latitude column:", gps_columns)
                with col2:
                    lon_col = st.selectbox("Select Longitude column:", gps_columns)
                
                # Clean GPS data
                map_data = extracted_df.copy()
                
                # Try to extract coordinates if they're in a combined format
                for col in [lat_col, lon_col]:
                    if col in map_data.columns:
                        # Handle various GPS formats
                        map_data[col] = map_data[col].astype(str).str.extract(r'(-?\d+\.?\d*)')[0]
                        map_data[col] = pd.to_numeric(map_data[col], errors='coerce')
                
                # Filter out rows with missing GPS data
                map_data = map_data.dropna(subset=[lat_col, lon_col])
                
                if len(map_data) > 0:
                    # Calculate total enrollment for each point
                    map_data["Total Enrollment"] = 0
                    for class_num in range(1, 6):
                        total_col = f"Number of enrollments in class {class_num}"
                        if total_col in map_data.columns:
                            map_data["Total Enrollment"] += map_data[total_col].fillna(0)
                    
                    # Create Folium map
                    center_lat = map_data[lat_col].mean()
                    center_lon = map_data[lon_col].mean()
                    
                    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
                    
                    # Add shapefile as base layer
                    folium.GeoJson(
                        gdf.to_json(),
                        style_function=lambda feature: {
                            'fillColor': 'lightblue',
                            'color': 'black',
                            'weight': 2,
                            'fillOpacity': 0.3,
                        }
                    ).add_to(m)
                    
                    # Add points for schools
                    for idx, row in map_data.iterrows():
                        # Create popup text
                        popup_text = f"""
                        <b>School:</b> {row.get('School Name', 'Unknown')}<br>
                        <b>District:</b> {row.get('District', 'Unknown')}<br>
                        <b>Chiefdom:</b> {row.get('Chiefdom', 'Unknown')}<br>
                        <b>Total Enrollment:</b> {row['Total Enrollment']}<br>
                        """
                        
                        # Color code by enrollment size
                        if row['Total Enrollment'] > 500:
                            color = 'red'
                            size = 8
                        elif row['Total Enrollment'] > 200:
                            color = 'orange'
                            size = 6
                        else:
                            color = 'green'
                            size = 4
                        
                        folium.CircleMarker(
                            location=[row[lat_col], row[lon_col]],
                            radius=size,
                            popup=folium.Popup(popup_text, max_width=300),
                            color=color,
                            fill=True,
                            fillColor=color,
                            fillOpacity=0.7
                        ).add_to(m)
                    
                    # Add legend
                    legend_html = '''
                    <div style="position: fixed; 
                                bottom: 50px; left: 50px; width: 150px; height: 90px; 
                                background-color: white; border:2px solid grey; z-index:9999; 
                                font-size:14px; padding: 10px">
                    <p><b>School Size</b></p>
                    <p><i class="fa fa-circle" style="color:red"></i> > 500 students</p>
                    <p><i class="fa fa-circle" style="color:orange"></i> 200-500 students</p>
                    <p><i class="fa fa-circle" style="color:green"></i> < 200 students</p>
                    </div>
                    '''
                    m.get_root().html.add_child(folium.Element(legend_html))
                    
                    # Display map
                    st_folium(m, width=700, height=500)
                    
                    # Display summary statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Schools Mapped", len(map_data))
                    with col2:
                        st.metric("Total Students", int(map_data['Total Enrollment'].sum()))
                    with col3:
                        st.metric("Avg Students/School", int(map_data['Total Enrollment'].mean()))
                    
                else:
                    st.warning("No valid GPS coordinates found in the data.")
            else:
                st.warning("No GPS columns found. Please ensure your data contains latitude and longitude columns.")
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
