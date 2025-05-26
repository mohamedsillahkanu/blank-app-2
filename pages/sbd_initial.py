import streamlit as st
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

# Configure Streamlit page
st.set_page_config(
    page_title="ITN Data Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    /* Main theme colors */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    .main-header h1 {
        color: white;
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        text-align: center;
        font-size: 1.2rem;
        margin: 0;
    }
    
    /* Card styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        margin-bottom: 1rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Data frame styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        font-weight: bold;
        margin: 2rem 0 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Set matplotlib and seaborn style
plt.style.use('dark_background')
sns.set_palette("husl")

# Custom color palette
colors = ['#667eea', '#764ba2', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7']

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 ITN Data Analytics Dashboard</h1>
    <p>Advanced Text Data Extraction & Visualization Platform</p>
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
        if column != "Scan QR code":  # Skip the QR code column since we've already processed it
            extracted_df[column] = df_original[column]
    
    # Key Metrics Dashboard
    st.markdown('<p class="section-header">📈 Key Metrics Overview</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_received = extracted_df["ITN received"].sum()
        st.metric("Total ITN Received", f"{total_received:,}", delta=None)
    
    with col2:
        total_given = extracted_df["ITN given"].sum()
        st.metric("Total ITN Given", f"{total_given:,}", delta=None)
    
    with col3:
        difference = total_received - total_given
        st.metric("Difference", f"{difference:,}", delta=f"{difference}")
    
    with col4:
        efficiency = (total_given / total_received * 100) if total_received > 0 else 0
        st.metric("Distribution Efficiency", f"{efficiency:.1f}%", delta=None)
    
    # Display Original Data Sample
    st.markdown('<p class="section-header">📄 Original Data Sample</p>', unsafe_allow_html=True)
    st.dataframe(df_original.head(), use_container_width=True)
    
    # Display Extracted Data
    st.markdown('<p class="section-header">📋 Extracted Data</p>', unsafe_allow_html=True)
    st.dataframe(extracted_df, use_container_width=True)
    
    # Summary Reports Section
    st.markdown('<p class="section-header">📊 Summary Reports</p>', unsafe_allow_html=True)
    
    # Create tabs for different summary views
    tab1, tab2 = st.tabs(["📍 District Analysis", "🏘️ Chiefdom Analysis"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        # District Summary
        district_summary = extracted_df.groupby("District").agg({
            "ITN received": "sum",
            "ITN given": "sum"
        }).reset_index()
        district_summary["Difference"] = district_summary["ITN received"] - district_summary["ITN given"]
        
        with col1:
            st.subheader("📈 District Summary Table")
            st.dataframe(district_summary, use_container_width=True)
        
        with col2:
            st.subheader("🥧 District Distribution")
            # Pie chart for ITN received by district
            fig, ax = plt.subplots(figsize=(8, 8), facecolor='none')
            ax.set_facecolor('none')
            wedges, texts, autotexts = ax.pie(district_summary["ITN received"], 
                                              labels=district_summary["District"],
                                              autopct='%1.1f%%',
                                              colors=colors[:len(district_summary)])
            
            # Style the pie chart
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            for text in texts:
                text.set_color('white')
                text.set_fontweight('bold')
            
            ax.set_title("ITN Received Distribution by District", color='white', fontsize=14, fontweight='bold', pad=20)
            st.pyplot(fig, transparent=True)
        
        # Bar chart for district comparison
        st.subheader("📊 District Comparison Chart")
        fig, ax = plt.subplots(figsize=(14, 8), facecolor='none')
        ax.set_facecolor('none')
        
        x = np.arange(len(district_summary))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, district_summary["ITN received"], width, 
                       label='ITN Received', color=colors[0], alpha=0.8)
        bars2 = ax.bar(x + width/2, district_summary["ITN given"], width, 
                       label='ITN Given', color=colors[1], alpha=0.8)
        
        ax.set_xlabel('District', color='white', fontweight='bold')
        ax.set_ylabel('Count', color='white', fontweight='bold')
        ax.set_title('ITN Received vs. ITN Given by District', color='white', fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(district_summary["District"], rotation=45, ha='right', color='white')
        ax.legend()
        ax.tick_params(colors='white')
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'{int(height)}', ha='center', va='bottom', color='white', fontweight='bold')
        
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'{int(height)}', ha='center', va='bottom', color='white', fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig, transparent=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        # Chiefdom Summary
        chiefdom_summary = extracted_df.groupby(["District", "Chiefdom"]).agg({
            "ITN received": "sum",
            "ITN given": "sum"
        }).reset_index()
        chiefdom_summary["Difference"] = chiefdom_summary["ITN received"] - chiefdom_summary["ITN given"]
        
        with col1:
            st.subheader("📈 Chiefdom Summary Table")
            st.dataframe(chiefdom_summary, use_container_width=True)
        
        with col2:
            st.subheader("🥧 Chiefdom Distribution")
            # Pie chart for ITN received by chiefdom
            fig, ax = plt.subplots(figsize=(8, 8), facecolor='none')
            ax.set_facecolor('none')
            
            # Create labels with district and chiefdom
            labels = [f"{row['District']}\n{row['Chiefdom']}" for _, row in chiefdom_summary.iterrows()]
            
            wedges, texts, autotexts = ax.pie(chiefdom_summary["ITN received"], 
                                              labels=labels,
                                              autopct='%1.1f%%',
                                              colors=colors[:len(chiefdom_summary)])
            
            # Style the pie chart
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(8)
            for text in texts:
                text.set_color('white')
                text.set_fontweight('bold')
                text.set_fontsize(8)
            
            ax.set_title("ITN Received Distribution by Chiefdom", color='white', fontsize=14, fontweight='bold', pad=20)
            st.pyplot(fig, transparent=True)
        
        # Bar chart for chiefdom comparison
        st.subheader("📊 Chiefdom Comparison Chart")
        chiefdom_summary['Label'] = chiefdom_summary['District'] + ' - ' + chiefdom_summary['Chiefdom']
        
        fig, ax = plt.subplots(figsize=(16, 8), facecolor='none')
        ax.set_facecolor('none')
        
        x = np.arange(len(chiefdom_summary))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, chiefdom_summary["ITN received"], width, 
                       label='ITN Received', color=colors[2], alpha=0.8)
        bars2 = ax.bar(x + width/2, chiefdom_summary["ITN given"], width, 
                       label='ITN Given', color=colors[3], alpha=0.8)
        
        ax.set_xlabel('Chiefdom', color='white', fontweight='bold')
        ax.set_ylabel('Count', color='white', fontweight='bold')
        ax.set_title('ITN Received vs. ITN Given by Chiefdom', color='white', fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(chiefdom_summary["Label"], rotation=45, ha='right', color='white')
        ax.legend()
        ax.tick_params(colors='white')
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'{int(height)}', ha='center', va='bottom', color='white', fontweight='bold', fontsize=8)
        
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'{int(height)}', ha='center', va='bottom', color='white', fontweight='bold', fontsize=8)
        
        plt.tight_layout()
        st.pyplot(fig, transparent=True)
    
    # Interactive Filtering Section
    st.markdown('<p class="section-header">🔍 Interactive Data Explorer</p>', unsafe_allow_html=True)
    
    # Create sidebar for filtering options
    with st.sidebar:
        st.markdown("### 🎛️ Filter Controls")
        
        # Create radio buttons to select which level to group by
        grouping_selection = st.radio(
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
    with st.sidebar:
        for level in hierarchy[grouping_selection]:
            # Filter out None/NaN values and get sorted unique values
            level_values = sorted(filtered_df[level].dropna().unique())
            
            if level_values:
                # Create selectbox for this level
                selected_value = st.selectbox(f"Select {level}", level_values)
                selected_values[level] = selected_value
                
                # Apply filter to the dataframe
                filtered_df = filtered_df[filtered_df[level] == selected_value]
    
    # Check if data is available after filtering
    if filtered_df.empty:
        st.warning("⚠️ No data available for the selected filters.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"### 📋 Filtered Data - {len(filtered_df)} records")
            st.dataframe(filtered_df, use_container_width=True)
        
        with col2:
            # Quick stats for filtered data
            st.write("### 📊 Quick Stats")
            filtered_received = filtered_df["ITN received"].sum()
            filtered_given = filtered_df["ITN given"].sum()
            filtered_diff = filtered_received - filtered_given
            
            st.metric("Filtered ITN Received", f"{filtered_received:,}")
            st.metric("Filtered ITN Given", f"{filtered_given:,}")
            st.metric("Filtered Difference", f"{filtered_diff:,}")
        
        # Define the hierarchy levels to include in the summary
        group_columns = hierarchy[grouping_selection]
        
        # Group by the selected hierarchical columns
        grouped_data = filtered_df.groupby(group_columns).agg({
            "ITN received": "sum",
            "ITN given": "sum"
        }).reset_index()
        
        # Add difference column
        grouped_data["Difference"] = grouped_data["ITN received"] - grouped_data["ITN given"]
        
        # Summary visualization
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Detailed Summary Table")
            st.dataframe(grouped_data, use_container_width=True)
        
        with col2:
            if len(grouped_data) > 1:
                st.subheader("🥧 Distribution Pie Chart")
                fig, ax = plt.subplots(figsize=(8, 8), facecolor='none')
                ax.set_facecolor('none')
                
                # Create labels for pie chart
                grouped_data['Group'] = grouped_data[group_columns].apply(
                    lambda row: '\n'.join(row.astype(str)), axis=1
                )
                
                wedges, texts, autotexts = ax.pie(grouped_data["ITN received"], 
                                                  labels=grouped_data['Group'],
                                                  autopct='%1.1f%%',
                                                  colors=colors[:len(grouped_data)])
                
                # Style the pie chart
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                for text in texts:
                    text.set_color('white')
                    text.set_fontweight('bold')
                    text.set_fontsize(9)
                
                ax.set_title(f"ITN Distribution by {grouping_selection}", 
                           color='white', fontsize=14, fontweight='bold', pad=20)
                st.pyplot(fig, transparent=True)
        
        # Detailed comparison chart
        if len(grouped_data) > 1:
            st.subheader("📊 Detailed Comparison Chart")
            grouped_data['Group'] = grouped_data[group_columns].apply(
                lambda row: ' - '.join(row.astype(str)), axis=1
            )
            
            fig, ax = plt.subplots(figsize=(14, 8), facecolor='none')
            ax.set_facecolor('none')
            
            x = np.arange(len(grouped_data))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, grouped_data["ITN received"], width, 
                           label='ITN Received', color=colors[4], alpha=0.8)
            bars2 = ax.bar(x + width/2, grouped_data["ITN given"], width, 
                           label='ITN Given', color=colors[5], alpha=0.8)
            
            ax.set_xlabel(grouping_selection, color='white', fontweight='bold')
            ax.set_ylabel('Count', color='white', fontweight='bold')
            ax.set_title(f'ITN Comparison by {grouping_selection}', 
                        color='white', fontsize=16, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(grouped_data["Group"], rotation=45, ha='right', color='white')
            ax.legend()
            ax.tick_params(colors='white')
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{int(height)}', ha='center', va='bottom', color='white', fontweight='bold')
            
            for bar in bars2:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{int(height)}', ha='center', va='bottom', color='white', fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig, transparent=True)

# Footer
st.markdown("""
---
<div style="text-align: center; color: rgba(255, 255, 255, 0.7); padding: 2rem;">
    <p>📊 ITN Data Analytics Dashboard | Built with Streamlit & Python</p>
</div>
""", unsafe_allow_html=True)
