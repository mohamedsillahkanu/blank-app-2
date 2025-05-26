import streamlit as st
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(
    page_title="School-Based Distribution of ITNs",
    page_icon="🏫",
    layout="wide"
)

# Custom CSS for styling with blue header and footer
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 1rem 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    .logo-placeholder {
        width: 80px;
        height: 80px;
        background: rgba(255,255,255,0.2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        border: 2px solid rgba(255,255,255,0.3);
    }
    
    .header-title {
        flex-grow: 1;
        text-align: center;
        margin: 0 2rem;
    }
    
    .header-title h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header-title p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    .main-footer {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        margin: 3rem -1rem -1rem -1rem;
        border-radius: 1rem 1rem 0 0;
        box-shadow: 0 -4px 8px rgba(0,0,0,0.2);
    }
    
    .footer-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .footer-info {
        flex-grow: 1;
        text-align: center;
        margin: 0 2rem;
    }
    
    .footer-info h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.5rem;
        color: #ffffff;
    }
    
    .footer-info p {
        margin: 0.25rem 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    
    /* Hide Streamlit default header/footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom styling for the app content */
    .stDataFrame {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    
    .stRadio > div {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2a5298;
    }
    
    /* Section headers */
    h2, h3 {
        color: #1e3c72;
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header with logo placeholders
st.markdown("""
<div class="main-header">
    <div class="header-content">
        <div class="logo-placeholder">
            🏢
        </div>
        <div class="header-title">
            <h1>School-Based Distribution of ITNs</h1>
            <p>Insecticide-Treated Nets Distribution Management System</p>
        </div>
        <div class="logo-placeholder">
            🏫
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Upload file
uploaded_file = "GMB253374_sbd_1740943126553_submissions.xlsx"

if uploaded_file:
    # Read the uploaded Excel file
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
        if column != "Scan QR code":
            extracted_df[column] = df_original[column]
    
    # Display Original Data Sample
    st.subheader("📄 Original Data Sample")
    st.dataframe(df_original.head())
    
    # Display Extracted Data
    st.subheader("📋 Extracted Data")
    st.dataframe(extracted_df)
    
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
        
        # Group by District and aggregate
        district_summary = extracted_df.groupby("District").agg({
            "ITN received": "sum",
            "ITN given": "sum"
        }).reset_index()
        
        # Calculate difference
        district_summary["Difference"] = district_summary["ITN received"] - district_summary["ITN given"]
        
        # Display summary table
        st.dataframe(district_summary)
        
        # Create a bar chart for district summary
        fig, ax = plt.subplots(figsize=(12, 8))
        district_summary.plot(kind="bar", x="District", y=["ITN received", "ITN given"], ax=ax, color=["#1e3c72", "#2a5298"])
        ax.set_title("📊 ITN Received vs. ITN Given by District")
        ax.set_xlabel("")
        ax.set_ylabel("Count")
        plt.xticks(rotation=0, ha='right')
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
        st.dataframe(chiefdom_summary)
        
        # Create a temporary label for the chart
        chiefdom_summary['Label'] = chiefdom_summary['District'] + '\n' + chiefdom_summary['Chiefdom']
        
        # Create a bar chart for chiefdom summary
        fig, ax = plt.subplots(figsize=(14, 10))
        chiefdom_summary.plot(kind="bar", x="Label", y=["ITN received", "ITN given"], ax=ax, color=["#1e3c72", "#2a5298"])
        ax.set_title("📊 ITN Received vs. ITN Given by District and Chiefdom")
        ax.set_xlabel("")
        ax.set_ylabel("Count")
        plt.xticks(rotation=0, ha='right')
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
        index=0
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
        
        # Group by the selected hierarchical columns
        grouped_data = filtered_df.groupby(group_columns).agg({
            "ITN received": "sum",
            "ITN given": "sum"
        }).reset_index()
        
        # Add difference column
        grouped_data["Difference"] = grouped_data["ITN received"] - grouped_data["ITN given"]
        
        # Summary Table with separate columns for each level
        st.subheader("📊 Detailed Summary Table")
        st.dataframe(grouped_data)
        
        # Create a temporary group column for the chart
        grouped_data['Group'] = grouped_data[group_columns].apply(lambda row: ','.join(row.astype(str)), axis=1)
        
        # Create a bar chart
        fig, ax = plt.subplots(figsize=(12, 8))
        grouped_data.plot(kind="bar", x="Group", y=["ITN received", "ITN given"], ax=ax, color=["#1e3c72", "#2a5298"])
        ax.set_title(f"{grouped_data['Group'].unique()[0]}")
        ax.set_xlabel("")
        ax.set_ylabel("Count")
        plt.xticks(rotation=0, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

# Footer with logo placeholders
st.markdown("""
<div class="main-footer">
    <div class="footer-content">
        <div class="logo-placeholder">
            🌍
        </div>
        <div class="footer-info">
            <h3>ITN Distribution System</h3>
            <p>Powered by Advanced Analytics | Ministry of Health Partnership</p>
            <p>© 2025 School-Based Distribution Platform</p>
        </div>
        <div class="logo-placeholder">
            📊
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
