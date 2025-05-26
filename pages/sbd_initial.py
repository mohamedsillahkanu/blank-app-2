import streamlit as st
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import base64
from io import BytesIO

# Configure page layout
st.set_page_config(
    page_title="ITN Data Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Header styling */
    .header-container {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 10px 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .logo-placeholder {
        width: 80px;
        height: 80px;
        background: rgba(255,255,255,0.2);
        border: 2px dashed rgba(255,255,255,0.5);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 12px;
        text-align: center;
    }
    
    .header-title {
        color: white;
        text-align: center;
        flex-grow: 1;
        margin: 0 20px;
    }
    
    .header-title h1 {
        margin: 0;
        font-size: 2.5em;
        font-weight: bold;
    }
    
    .header-title p {
        margin: 5px 0 0 0;
        font-size: 1.1em;
        opacity: 0.9;
    }
    
    /* Footer styling */
    .footer-container {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        margin: 3rem -1rem -1rem -1rem;
        border-radius: 10px 10px 0 0;
        color: white;
        text-align: center;
    }
    
    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .footer-links {
        margin: 10px 0;
    }
    
    .footer-links a {
        color: rgba(255,255,255,0.8);
        text-decoration: none;
        margin: 0 15px;
        transition: color 0.3s;
    }
    
    .footer-links a:hover {
        color: white;
    }
    
    /* Main content styling */
    .main-content {
        min-height: 60vh;
        padding: 0 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
<div class="header-container">
    <div class="header-content">
        <div class="logo-placeholder">
            LEFT<br>LOGO<br>HERE
        </div>
        <div class="header-title">
            <h1>📊 ITN Data Analysis Dashboard</h1>
            <p>Text Data Extraction & Visualization System</p>
        </div>
        <div class="logo-placeholder">
            RIGHT<br>LOGO<br>HERE
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main content wrapper
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# File upload section
st.subheader("📁 Data Upload")
uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])

# If no file is uploaded, use the default file
if not uploaded_file:
    uploaded_file = "GMB253374_sbd_1740943126553_submissions.xlsx"
    st.info("Using default file: GMB253374_sbd_1740943126553_submissions.xlsx")

if uploaded_file:
    try:
        # Read the uploaded Excel file
        if isinstance(uploaded_file, str):
            df_original = pd.read_excel(uploaded_file)
        else:
            df_original = pd.read_excel(uploaded_file)
        
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
        
        # Display success message
        st.success(f"✅ Successfully processed {len(extracted_df)} records!")
        
        # Create tabs for better organization
        tab1, tab2, tab3, tab4 = st.tabs(["📄 Data Preview", "📊 Quick Summaries", "🔍 Detailed Analysis", "📈 Export Data"])
        
        with tab1:
            st.subheader("📄 Original Data Sample")
            st.dataframe(df_original.head(), height=300)
            
            st.subheader("📋 Extracted Data Preview")
            st.dataframe(extracted_df.head(), height=300)
            
            # Display basic statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(extracted_df))
            with col2:
                st.metric("Districts", extracted_df['District'].nunique())
            with col3:
                st.metric("Chiefdoms", extracted_df['Chiefdom'].nunique())
        
        with tab2:
            st.subheader("📊 Quick Summary Reports")
            
            # Create two columns for the summary buttons
            col1, col2 = st.columns(2)
            
            # Button for District Summary
            with col1:
                district_summary_button = st.button("🏛️ Show District Summary", key="district_btn")
            
            # Button for Chiefdom Summary
            with col2:
                chiefdom_summary_button = st.button("🏘️ Show Chiefdom Summary", key="chiefdom_btn")
            
            # Display District Summary when button is clicked
            if district_summary_button:
                st.subheader("📈 Summary by District")
                
                # Group by District and aggregate
                district_summary = extracted_df.groupby("District").agg({
                    "ITN received": "sum",
                    "ITN given": "sum"
                }).reset_index()
                
                # Calculate difference
                district_summary["Difference"] = district_summary["ITN received"] - district_summary["ITN given"]
                
                # Display summary table
                st.dataframe(district_summary, use_container_width=True)
                
                # Create a bar chart for district summary
                fig, ax = plt.subplots(figsize=(12, 8))
                district_summary.plot(kind="bar", x="District", y=["ITN received", "ITN given"], ax=ax, color=["#1e3c72", "#ff6b35"])
                ax.set_title("📊 ITN Received vs. ITN Given by District", fontsize=16, fontweight='bold')
                ax.set_xlabel("")
                ax.set_ylabel("Count")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
            
            # Display Chiefdom Summary when button is clicked
            if chiefdom_summary_button:
                st.subheader("📈 Summary by Chiefdom")
                
                # Group by District and Chiefdom and aggregate
                chiefdom_summary = extracted_df.groupby(["District", "Chiefdom"]).agg({
                    "ITN received": "sum",
                    "ITN given": "sum"
                }).reset_index()
                
                # Calculate difference
                chiefdom_summary["Difference"] = chiefdom_summary["ITN received"] - chiefdom_summary["ITN given"]
                
                # Display summary table
                st.dataframe(chiefdom_summary, use_container_width=True)
                
                # Create a temporary label for the chart
                chiefdom_summary['Label'] = chiefdom_summary['District'] + ' - ' + chiefdom_summary['Chiefdom']
                
                # Create a bar chart for chiefdom summary
                fig, ax = plt.subplots(figsize=(14, 10))
                chiefdom_summary.plot(kind="bar", x="Label", y=["ITN received", "ITN given"], ax=ax, color=["#1e3c72", "#ff6b35"])
                ax.set_title("📊 ITN Received vs. ITN Given by District and Chiefdom", fontsize=16, fontweight='bold')
                ax.set_xlabel("")
                ax.set_ylabel("Count")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
        
        with tab3:
            st.subheader("🔍 Detailed Data Filtering and Visualization")
            
            # Create a sidebar for filtering options
            st.sidebar.header("🎛️ Filter Options")
            
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
                st.warning("⚠️ No data available for the selected filters.")
            else:
                st.write(f"### Filtered Data - {len(filtered_df)} records")
                st.dataframe(filtered_df, use_container_width=True)
                
                # Define the hierarchy levels to include in the summary
                group_columns = hierarchy[grouping_selection]
                
                # Group by the selected hierarchical columns
                grouped_data = filtered_df.groupby(group_columns).agg({
                    "ITN received": "sum",
                    "ITN given": "sum"
                }).reset_index()
                
                # Add difference column
                grouped_data["Difference"] = grouped_data["ITN received"] - grouped_data["ITN given"]
                
                # Summary Table with separate columns for each level
                st.subheader("📊 Detailed Summary Table")
                st.dataframe(grouped_data, use_container_width=True)
                
                # Create a temporary group column for the chart
                grouped_data['Group'] = grouped_data[group_columns].apply(lambda row: ' - '.join(row.astype(str)), axis=1)
                
                # Create a bar chart
                fig, ax = plt.subplots(figsize=(12, 8))
                grouped_data.plot(kind="bar", x="Group", y=["ITN received", "ITN given"], ax=ax, color=["#1e3c72", "#ff6b35"])
                ax.set_title(f"📊 Analysis by {grouping_selection}", fontsize=16, fontweight='bold')
                ax.set_xlabel("")
                ax.set_ylabel("Count")
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
        
        with tab4:
            st.subheader("📈 Export Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Download extracted data as CSV
                csv = extracted_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Extracted Data as CSV",
                    data=csv,
                    file_name="extracted_itn_data.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Download summary data
                if 'district_summary' in locals():
                    summary_csv = district_summary.to_csv(index=False)
                    st.download_button(
                        label="📥 Download District Summary",
                        data=summary_csv,
                        file_name="district_summary.csv",
                        mime="text/csv"
                    )
            
            st.info("💡 Use the download buttons above to export your processed data for further analysis.")
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("Please ensure your Excel file contains a 'Scan QR code' column with the expected data format.")

# Close main content wrapper
st.markdown('</div>', unsafe_allow_html=True)

# Footer Section
st.markdown("""
<div class="footer-container">
    <div class="footer-content">
        <h3>ITN Data Analysis Dashboard</h3>
        <div class="footer-links">
            <a href="#about">About</a>
            <a href="#contact">Contact</a>
            <a href="#support">Support</a>
            <a href="#privacy">Privacy Policy</a>
        </div>
        <p>© 2025 Your Organization Name. All rights reserved.</p>
        <p>Powered by Streamlit | Data Analytics & Visualization Platform</p>
    </div>
</div>
""", unsafe_allow_html=True)
