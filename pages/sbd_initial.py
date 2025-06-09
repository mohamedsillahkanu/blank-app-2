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
    
    if gdf is not None:
        # Define specific districts for left and right maps
        left_district = "BO"
        right_district = "BOMBALI"
        
        # BO DISTRICT MAP - Full width
        st.write(f"**{left_district} District - All Chiefdoms**")
        
        # Filter shapefile for BO district
        bo_gdf = gdf[gdf['FIRST_DNAM'] == left_district].copy()
        
        if len(bo_gdf) > 0:
            # Filter data for BO district to get GPS coordinates
            bo_data = extracted_df[extracted_df["District"] == left_district].copy()
            
            # Create the BO district plot
            fig_bo, ax_bo = plt.subplots(figsize=(16, 10))
            
            # Plot chiefdom boundaries in white with black edges
            bo_gdf.plot(ax=ax_bo, color='white', edgecolor='black', alpha=0.8, linewidth=1)
            
            # Add chiefdom labels
            for idx, row in bo_gdf.iterrows():
                if 'FIRST_CHIE' in row and pd.notna(row['FIRST_CHIE']):
                    centroid = row.geometry.centroid
                    ax_bo.annotate(
                        row['FIRST_CHIE'], 
                        (centroid.x, centroid.y),
                        xytext=(5, 5), 
                        textcoords='offset points',
                        fontsize=10,
                        ha='left',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
                    )
            
            # Plot GPS coordinates if available
            if len(bo_data) > 0 and "GPS Location" in bo_data.columns:
                gps_data = bo_data["GPS Location"].dropna()
                coords_extracted = []
                
                for gps_val in gps_data:
                    coords = re.findall(r'-?\d+\.?\d*', str(gps_val))
                    if len(coords) >= 2:
                        try:
                            lat, lon = float(coords[0]), float(coords[1])
                            coords_extracted.append([lat, lon])
                        except:
                            continue
                
                if coords_extracted:
                    lats, lons = zip(*coords_extracted)
                    ax_bo.scatter(
                        lons, lats,
                        c='blue',
                        s=60,
                        alpha=0.8,
                        edgecolors='darkblue',
                        linewidth=1,
                        zorder=5,
                        label=f'Schools ({len(coords_extracted)})'
                    )
                    ax_bo.legend()
            
            # Customize plot
            ax_bo.set_title(f'{left_district} District - Chiefdoms: {len(bo_gdf)}', fontsize=16, fontweight='bold')
            ax_bo.set_xlabel('Longitude', fontsize=12)
            ax_bo.set_ylabel('Latitude', fontsize=12)
            
            # Remove axis ticks for cleaner look
            ax_bo.set_xticks([])
            ax_bo.set_yticks([])
            
            plt.tight_layout()
            st.pyplot(fig_bo)
            
            # Display chiefdoms list
            if 'FIRST_CHIE' in bo_gdf.columns:
                chiefdoms = bo_gdf['FIRST_CHIE'].dropna().tolist()
                st.write(f"**Chiefdoms in {left_district} District ({len(chiefdoms)}):**")
                chiefdom_cols = st.columns(3)
                for i, chiefdom in enumerate(chiefdoms):
                    with chiefdom_cols[i % 3]:
                        st.write(f"• {chiefdom}")
        else:
            st.warning(f"No chiefdoms found for {left_district} district in shapefile")
        
        st.divider()
        
        # BOMBALI DISTRICT MAP - Full width
        st.write(f"**{right_district} District - All Chiefdoms**")
        
        # Filter shapefile for BOMBALI district
        bombali_gdf = gdf[gdf['FIRST_DNAM'] == right_district].copy()
        
        if len(bombali_gdf) > 0:
            # Filter data for BOMBALI district to get GPS coordinates
            bombali_data = extracted_df[extracted_df["District"] == right_district].copy()
            
            # Create the BOMBALI district plot
            fig_bombali, ax_bombali = plt.subplots(figsize=(16, 10))
            
            # Plot chiefdom boundaries in white with black edges
            bombali_gdf.plot(ax=ax_bombali, color='white', edgecolor='black', alpha=0.8, linewidth=1)
            
            # Add chiefdom labels
            for idx, row in bombali_gdf.iterrows():
                if 'FIRST_CHIE' in row and pd.notna(row['FIRST_CHIE']):
                    centroid = row.geometry.centroid
                    ax_bombali.annotate(
                        row['FIRST_CHIE'], 
                        (centroid.x, centroid.y),
                        xytext=(5, 5), 
                        textcoords='offset points',
                        fontsize=10,
                        ha='left',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
                    )
            
            # Plot GPS coordinates if available
            if len(bombali_data) > 0 and "GPS Location" in bombali_data.columns:
                gps_data = bombali_data["GPS Location"].dropna()
                coords_extracted = []
                
                for gps_val in gps_data:
                    coords = re.findall(r'-?\d+\.?\d*', str(gps_val))
                    if len(coords) >= 2:
                        try:
                            lat, lon = float(coords[0]), float(coords[1])
                            coords_extracted.append([lat, lon])
                        except:
                            continue
                
                if coords_extracted:
                    lats, lons = zip(*coords_extracted)
                    ax_bombali.scatter(
                        lons, lats,
                        c='blue',
                        s=60,
                        alpha=0.8,
                        edgecolors='darkblue',
                        linewidth=1,
                        zorder=5,
                        label=f'Schools ({len(coords_extracted)})'
                    )
                    ax_bombali.legend()
            
            # Customize plot
            ax_bombali.set_title(f'{right_district} District - Chiefdoms: {len(bombali_gdf)}', fontsize=16, fontweight='bold')
            ax_bombali.set_xlabel('Longitude', fontsize=12)
            ax_bombali.set_ylabel('Latitude', fontsize=12)
            
            # Remove axis ticks for cleaner look
            ax_bombali.set_xticks([])
            ax_bombali.set_yticks([])
            
            plt.tight_layout()
            st.pyplot(fig_bombali)
            
            # Display chiefdoms list
            if 'FIRST_CHIE' in bombali_gdf.columns:
                chiefdoms = bombali_gdf['FIRST_CHIE'].dropna().tolist()
                st.write(f"**Chiefdoms in {right_district} District ({len(chiefdoms)}):**")
                chiefdom_cols = st.columns(3)
                for i, chiefdom in enumerate(chiefdoms):
                    with chiefdom_cols[i % 3]:
                        st.write(f"• {chiefdom}")
        else:
            st.warning(f"No chiefdoms found for {right_district} district in shapefile")
    else:
        st.error("Shapefile not loaded. Cannot display map.")
    
    # Enrollment and ITN Distribution Analysis
    st.subheader("📊 Enrollment and ITN Distribution Analysis")
    
    # Calculate total enrollment and ITN distribution by district
    district_analysis = []
    
    for district in extracted_df['District'].dropna().unique():
        district_data = extracted_df[extracted_df['District'] == district]
        
        total_enrollment = 0
        total_itn = 0
        
        # Sum enrollments and ITN by class
        for class_num in range(1, 6):
            boys_col = f"Number of boys in class {class_num}"
            girls_col = f"Number of girls in class {class_num}"
            itn_col = f"Number of ITN distributed to class {class_num}"
            
            if boys_col in district_data.columns:
                total_enrollment += district_data[boys_col].fillna(0).sum()
            if girls_col in district_data.columns:
                total_enrollment += district_data[girls_col].fillna(0).sum()
            if itn_col in district_data.columns:
                total_itn += district_data[itn_col].fillna(0).sum()
        
        district_analysis.append({
            'District': district,
            'Total_Enrollment': total_enrollment,
            'Total_ITN': total_itn
        })
    
    district_df = pd.DataFrame(district_analysis)
    
    # Create 2-column subplot for district analysis
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Total Enrollment by District
    ax1.bar(district_df['District'], district_df['Total_Enrollment'], color='skyblue', edgecolor='navy')
    ax1.set_title('Total Enrollment by District', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Number of Students')
    ax1.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for i, v in enumerate(district_df['Total_Enrollment']):
        ax1.text(i, v + max(district_df['Total_Enrollment']) * 0.01, str(int(v)), ha='center', fontweight='bold')
    
    # Total ITN Distributed by District
    ax2.bar(district_df['District'], district_df['Total_ITN'], color='lightcoral', edgecolor='darkred')
    ax2.set_title('Total ITN Distributed by District', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Number of ITNs')
    ax2.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for i, v in enumerate(district_df['Total_ITN']):
        ax2.text(i, v + max(district_df['Total_ITN']) * 0.01, str(int(v)), ha='center', fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # BO District Chiefdoms Analysis
    st.subheader("📊 BO District - Chiefdoms Analysis")
    
    bo_district_data = extracted_df[extracted_df['District'] == 'BO']
    if len(bo_district_data) > 0:
        # Calculate by chiefdom
        bo_chiefdom_analysis = []
        
        for chiefdom in bo_district_data['Chiefdom'].dropna().unique():
            chiefdom_data = bo_district_data[bo_district_data['Chiefdom'] == chiefdom]
            
            total_enrollment = 0
            total_itn = 0
            
            for class_num in range(1, 6):
                boys_col = f"Number of boys in class {class_num}"
                girls_col = f"Number of girls in class {class_num}"
                itn_col = f"Number of ITN distributed to class {class_num}"
                
                if boys_col in chiefdom_data.columns:
                    total_enrollment += chiefdom_data[boys_col].fillna(0).sum()
                if girls_col in chiefdom_data.columns:
                    total_enrollment += chiefdom_data[girls_col].fillna(0).sum()
                if itn_col in chiefdom_data.columns:
                    total_itn += chiefdom_data[itn_col].fillna(0).sum()
            
            bo_chiefdom_analysis.append({
                'Chiefdom': chiefdom,
                'Total_Enrollment': total_enrollment,
                'Total_ITN': total_itn
            })
        
        bo_chiefdom_df = pd.DataFrame(bo_chiefdom_analysis)
        
        if len(bo_chiefdom_df) > 0:
            # Create 2-column subplot for BO chiefdoms
            fig_bo, (ax1_bo, ax2_bo) = plt.subplots(1, 2, figsize=(16, 8))
            
            # Total Enrollment by BO Chiefdoms
            ax1_bo.barh(bo_chiefdom_df['Chiefdom'], bo_chiefdom_df['Total_Enrollment'], color='lightgreen', edgecolor='darkgreen')
            ax1_bo.set_title('BO District - Total Enrollment by Chiefdom', fontsize=14, fontweight='bold')
            ax1_bo.set_xlabel('Number of Students')
            
            # Add value labels
            for i, v in enumerate(bo_chiefdom_df['Total_Enrollment']):
                ax1_bo.text(v + max(bo_chiefdom_df['Total_Enrollment']) * 0.01, i, str(int(v)), va='center', fontweight='bold')
            
            # Total ITN by BO Chiefdoms
            ax2_bo.barh(bo_chiefdom_df['Chiefdom'], bo_chiefdom_df['Total_ITN'], color='orange', edgecolor='darkorange')
            ax2_bo.set_title('BO District - Total ITN Distributed by Chiefdom', fontsize=14, fontweight='bold')
            ax2_bo.set_xlabel('Number of ITNs')
            
            # Add value labels
            for i, v in enumerate(bo_chiefdom_df['Total_ITN']):
                ax2_bo.text(v + max(bo_chiefdom_df['Total_ITN']) * 0.01, i, str(int(v)), va='center', fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig_bo)
        else:
            st.warning("No chiefdom data available for BO district")
    else:
        st.warning("No data available for BO district")
    
    # BOMBALI District Chiefdoms Analysis
    st.subheader("📊 BOMBALI District - Chiefdoms Analysis")
    
    bombali_district_data = extracted_df[extracted_df['District'] == 'BOMBALI']
    if len(bombali_district_data) > 0:
        # Calculate by chiefdom
        bombali_chiefdom_analysis = []
        
        for chiefdom in bombali_district_data['Chiefdom'].dropna().unique():
            chiefdom_data = bombali_district_data[bombali_district_data['Chiefdom'] == chiefdom]
            
            total_enrollment = 0
            total_itn = 0
            
            for class_num in range(1, 6):
                boys_col = f"Number of boys in class {class_num}"
                girls_col = f"Number of girls in class {class_num}"
                itn_col = f"Number of ITN distributed to class {class_num}"
                
                if boys_col in chiefdom_data.columns:
                    total_enrollment += chiefdom_data[boys_col].fillna(0).sum()
                if girls_col in chiefdom_data.columns:
                    total_enrollment += chiefdom_data[girls_col].fillna(0).sum()
                if itn_col in chiefdom_data.columns:
                    total_itn += chiefdom_data[itn_col].fillna(0).sum()
            
            bombali_chiefdom_analysis.append({
                'Chiefdom': chiefdom,
                'Total_Enrollment': total_enrollment,
                'Total_ITN': total_itn
            })
        
        bombali_chiefdom_df = pd.DataFrame(bombali_chiefdom_analysis)
        
        if len(bombali_chiefdom_df) > 0:
            # Create 2-column subplot for BOMBALI chiefdoms
            fig_bombali, (ax1_bombali, ax2_bombali) = plt.subplots(1, 2, figsize=(16, 8))
            
            # Total Enrollment by BOMBALI Chiefdoms
            ax1_bombali.barh(bombali_chiefdom_df['Chiefdom'], bombali_chiefdom_df['Total_Enrollment'], color='lightblue', edgecolor='darkblue')
            ax1_bombali.set_title('BOMBALI District - Total Enrollment by Chiefdom', fontsize=14, fontweight='bold')
            ax1_bombali.set_xlabel('Number of Students')
            
            # Add value labels
            for i, v in enumerate(bombali_chiefdom_df['Total_Enrollment']):
                ax1_bombali.text(v + max(bombali_chiefdom_df['Total_Enrollment']) * 0.01, i, str(int(v)), va='center', fontweight='bold')
            
            # Total ITN by BOMBALI Chiefdoms
            ax2_bombali.barh(bombali_chiefdom_df['Chiefdom'], bombali_chiefdom_df['Total_ITN'], color='plum', edgecolor='purple')
            ax2_bombali.set_title('BOMBALI District - Total ITN Distributed by Chiefdom', fontsize=14, fontweight='bold')
            ax2_bombali.set_xlabel('Number of ITNs')
            
            # Add value labels
            for i, v in enumerate(bombali_chiefdom_df['Total_ITN']):
                ax2_bombali.text(v + max(bombali_chiefdom_df['Total_ITN']) * 0.01, i, str(int(v)), va='center', fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig_bombali)
        else:
            st.warning("No chiefdom data available for BOMBALI district")
    else:
        st.warning("No data available for BOMBALI district")
    
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
