import streamlit as st
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from io import BytesIO
from datetime import datetime
import os

# Custom CSS with blue and white theme and zoom functionality
st.markdown("""
<style>
    /* Allow zoom functionality */
    .stApp {
        zoom: 1 !important;
        transform: scale(1) !important;
        transform-origin: 0 0 !important;
    }
    
    /* Increase sidebar width */
    section[data-testid="stSidebar"] {
        width: 320px !important;
        background-color: #f8f9fd !important;
    }
    
    /* Main app styling with blue theme */
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-left: 0 !important;
        max-width: none !important;
        background-color: white !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        margin-top: 1rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Title styling */
    h1 {
        color: #2c3e50 !important;
        text-align: center !important;
        font-weight: 700 !important;
        margin-bottom: 2rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* Subheader styling */
    h2, h3 {
        color: #34495e !important;
        border-bottom: 2px solid #3498db !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding-left: 1rem !important;
        margin-left: 0 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #3498db, #2980b9) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.5rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #2980b9, #1f5f8b) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4) !important;
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(45deg, #27ae60, #229954) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.5rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(45deg, #229954, #1e7e34) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(39, 174, 96, 0.4) !important;
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #74b9ff, #0984e3) !important;
        border: 1px solid #ddd !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    [data-testid="metric-container"] > div {
        color: white !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* Info box styling */
    .stInfo {
        background: linear-gradient(135deg, #74b9ff, #0984e3) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    
    /* Warning box styling */
    .stWarning {
        background: linear-gradient(135deg, #fdcb6e, #e17055) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    
    /* Success box styling */
    .stSuccess {
        background: linear-gradient(135deg, #00b894, #00a085) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    
    /* Logo container styling for consistent alignment */
    .logo-container {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        padding: 1rem 0 !important;
        margin-bottom: 1rem !important;
        border-bottom: 2px solid #f0f0f0 !important;
    }
    
    .logo-item {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 300px !important;
        height: 200px !important;
        border: 2px solid #3498db !important;
        border-radius: 15px !important;
        background: linear-gradient(135deg, #f8f9fd, #e3f2fd) !important;
        overflow: hidden !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }
    
    .logo-item img {
        max-width: 280px !important;
        max-height: 180px !important;
        width: auto !important;
        height: auto !important;
        object-fit: contain !important;
    }
    
    .logo-placeholder {
        width: 280px !important;
        height: 180px !important;
        border: 2px dashed #3498db !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: linear-gradient(135deg, #f8f9fd, #e3f2fd) !important;
        border-radius: 15px !important;
        font-size: 14px !important;
        color: #2c3e50 !important;
        text-align: center !important;
        font-weight: 600 !important;
    }
    
    /* Report export button styling */
    .report-button {
        background: linear-gradient(45deg, #e74c3c, #c0392b) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3) !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        width: 100% !important;
        margin: 1rem 0 !important;
    }
    
    .report-button:hover {
        background: linear-gradient(45deg, #c0392b, #a93226) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Logo Section with consistent alignment
st.markdown("""
<div class="logo-container">
    <div class="logo-item" id="logo1"></div>
    <div class="logo-item" id="logo2"></div>
    <div class="logo-item" id="logo3"></div>
</div>
""", unsafe_allow_html=True)

# Add logos with consistent sizing using columns
col1, col2, col3 = st.columns(3)
with col1:
    try:
        st.markdown('<div style="text-align: center; margin-bottom: 1rem;">', unsafe_allow_html=True)
        st.image("NMCP.png", width=280, caption="National Malaria Control Program")
        st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.markdown("""
        <div class="logo-placeholder">
            NMCP.png<br>
            Not Found<br>
            Please upload logo
        </div>
        """, unsafe_allow_html=True)

with col2:
    try:
        st.markdown('<div style="text-align: center; margin-bottom: 1rem;">', unsafe_allow_html=True)
        st.image("icf_sl (2).jpg", width=280, caption="ICF Sierra Leone")
        st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.markdown("""
        <div class="logo-placeholder">
            icf_sl (2).jpg<br>
            Not Found<br>
            Please upload logo
        </div>
        """, unsafe_allow_html=True)

with col3:
    # Placeholder for third logo
    st.markdown("""
    <div class="logo-placeholder">
        Partner Logo<br>
        (Right Position)<br>
        Upload .png/.jpg
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")  # Add a horizontal line separator

# Streamlit App
st.title("📊 Text Data Extraction & Visualization")

# Use embedded file
uploaded_file = "Report_GMB253374_SBD_1749318384635_submissions.xlsx"

try:
    # Read the Excel file
    df_original = pd.read_excel(uploaded_file)
    st.success(f"✅ File loaded successfully! {len(df_original)} records found.")
except Exception as e:
    st.error(f"❌ Error reading file: {e}")
    st.write("Please ensure the file 'Report_GMB253374_SBD_1749318384635_submissions.xlsx' exists in the same directory.")
    st.stop()
    
    # Load shapefile
    try:
        gdf = gpd.read_file("Chiefdom 2021.shp")
        st.success("✅ Shapefile loaded successfully!")
    except Exception as e:
        st.error(f"❌ Could not load shapefile: {e}")
        gdf = None
    
    # Check if QR code column exists
    if "Scan QR code" not in df_original.columns:
        st.error("❌ 'Scan QR code' column not found in the uploaded file.")
        st.write("Available columns:", list(df_original.columns))
        st.stop()
    
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
        
        # Calculate coverage percentage
        coverage = (total_itn / total_enrollment * 100) if total_enrollment > 0 else 0
        
        district_analysis.append({
            'District': district,
            'Total_Enrollment': total_enrollment,
            'Total_ITN': total_itn,
            'Coverage': coverage
        })
    
    district_df = pd.DataFrame(district_analysis)
    
    # Create bar charts for district analysis
    if len(district_df) > 0:
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
        plt.close(fig)
    else:
        st.warning("No district data available for analysis.")
    
    # Display final summary
    st.info(f"📋 **Dataset Summary**: {len(extracted_df)} total records extracted and processed")
