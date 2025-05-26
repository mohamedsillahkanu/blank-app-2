import streamlit as st
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set up colorful theme
plt.style.use('seaborn-v0_8')
# Define beautiful color palettes
bar_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
pie_colors = ['#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43', '#10AC84', '#EE5A24', '#0984E3']

# Custom CSS for blue theme
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    }
    
    .stTitle {
        color: #1565c0 !important;
        font-weight: 700 !important;
        text-align: center;
        padding: 20px 0;
        background: linear-gradient(90deg, #1976d2, #2196f3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stSubheader {
        color: #1976d2 !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #2196f3;
        padding-bottom: 5px;
        margin-bottom: 15px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        box-shadow: 0 4px 8px rgba(33, 150, 243, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
        box-shadow: 0 6px 12px rgba(33, 150, 243, 0.4);
        transform: translateY(-2px);
    }
    
    .stSelectbox > div > div {
        background-color: #e3f2fd;
        border: 2px solid #2196f3;
        border-radius: 8px;
    }
    
    .stRadio > div {
        background-color: #f3e5f5;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #2196f3;
    }
    
    .stDataFrame {
        border: 2px solid #2196f3;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .stWarning {
        background-color: #fff3e0;
        border: 1px solid #ff9800;
        color: #e65100;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #e3f2fd 0%, #bbdefb 100%);
    }
    
    .stSidebar > div {
        background: linear-gradient(180deg, #e3f2fd 0%, #bbdefb 100%);
    }
</style>
""", unsafe_allow_html=True)

# Streamlit App
st.title("📊 Text Data Extraction & Visualization")

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
        
        # Create two columns for charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Create a colorful bar chart for district summary
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            # Use colorful scheme
            x = np.arange(len(district_summary))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, district_summary["ITN received"], width, 
                          label='ITN Received', color=bar_colors[0], alpha=0.8,
                          edgecolor='white', linewidth=2)
            bars2 = ax.bar(x + width/2, district_summary["ITN given"], width,
                          label='ITN Given', color=bar_colors[1], alpha=0.8,
                          edgecolor='white', linewidth=2)
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            for bar in bars2:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            
            ax.set_title("📊 ITN by District (Bar Chart)", 
                        fontsize=14, fontweight='bold', color='#2C3E50', pad=20)
            ax.set_xlabel("District", fontweight='bold', color='#34495E')
            ax.set_ylabel("Count", fontweight='bold', color='#34495E')
            ax.set_xticks(x)
            ax.set_xticklabels(district_summary["District"], rotation=45, ha='right')
            ax.grid(True, alpha=0.3, color='#BDC3C7')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            plt.legend(frameon=True, fancybox=True, shadow=True, 
                      facecolor='#ECF0F1', edgecolor='#34495E')
            plt.tight_layout()
            st.pyplot(fig)
        
        with chart_col2:
            # Create colorful pie charts
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            fig.patch.set_facecolor('#f8f9fa')
            
            # Pie chart for ITN Received
            wedges1, texts1, autotexts1 = ax1.pie(district_summary["ITN received"], 
                                                  labels=district_summary["District"],
                                                  autopct='%1.1f%%', startangle=90,
                                                  colors=pie_colors[:len(district_summary)],
                                                  explode=[0.05] * len(district_summary),
                                                  shadow=True, textprops={'fontweight': 'bold'})
            ax1.set_title("🥧 ITN Received Distribution", fontweight='bold', color='#2C3E50', pad=20)
            
            # Pie chart for ITN Given
            wedges2, texts2, autotexts2 = ax2.pie(district_summary["ITN given"], 
                                                  labels=district_summary["District"],
                                                  autopct='%1.1f%%', startangle=90,
                                                  colors=pie_colors[2:2+len(district_summary)],
                                                  explode=[0.05] * len(district_summary),
                                                  shadow=True, textprops={'fontweight': 'bold'})
            ax2.set_title("🥧 ITN Given Distribution", fontweight='bold', color='#2C3E50', pad=20)
            
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
        chiefdom_summary['Label'] = chiefdom_summary['District'] + ' - ' + chiefdom_summary['Chiefdom']
        
        # Create two columns for charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Create a colorful bar chart for chiefdom summary
            fig, ax = plt.subplots(figsize=(12, 8))
            fig.patch.set_facecolor('#f8f9fa')
            ax.set_facecolor('#ffffff')
            
            # Use colorful scheme
            x = np.arange(len(chiefdom_summary))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, chiefdom_summary["ITN received"], width, 
                          label='ITN Received', color=bar_colors[2], alpha=0.8,
                          edgecolor='white', linewidth=2)
            bars2 = ax.bar(x + width/2, chiefdom_summary["ITN given"], width,
                          label='ITN Given', color=bar_colors[3], alpha=0.8,
                          edgecolor='white', linewidth=2)
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{int(height)}', ha='center', va='bottom', fontweight='bold', fontsize=8)
            for bar in bars2:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{int(height)}', ha='center', va='bottom', fontweight='bold', fontsize=8)
            
            ax.set_title("📊 ITN by District and Chiefdom", 
                        fontsize=14, fontweight='bold', color='#2C3E50', pad=20)
            ax.set_xlabel("District - Chiefdom", fontweight='bold', color='#34495E')
            ax.set_ylabel("Count", fontweight='bold', color='#34495E')
            ax.set_xticks(x)
            ax.set_xticklabels(chiefdom_summary["Label"], rotation=45, ha='right')
            ax.grid(True, alpha=0.3, color='#BDC3C7')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            plt.legend(frameon=True, fancybox=True, shadow=True, 
                      facecolor='#ECF0F1', edgecolor='#34495E')
            plt.tight_layout()
            st.pyplot(fig)
        
        with chart_col2:
            # Create colorful pie charts for chiefdom
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
            fig.patch.set_facecolor('#f8f9fa')
            
            # Pie chart for ITN Received
            wedges1, texts1, autotexts1 = ax1.pie(chiefdom_summary["ITN received"], 
                                                  labels=chiefdom_summary["Label"],
                                                  autopct='%1.1f%%', startangle=90,
                                                  colors=pie_colors[:len(chiefdom_summary)],
                                                  explode=[0.02] * len(chiefdom_summary),
                                                  shadow=True, textprops={'fontweight': 'bold', 'fontsize': 8})
            ax1.set_title("🥧 ITN Received by Chiefdom", fontweight='bold', color='#2C3E50', pad=20)
            
            # Pie chart for ITN Given
            wedges2, texts2, autotexts2 = ax2.pie(chiefdom_summary["ITN given"], 
                                                  labels=chiefdom_summary["Label"],
                                                  autopct='%1.1f%%', startangle=90,
                                                  colors=pie_colors[3:3+len(chiefdom_summary)],
                                                  explode=[0.02] * len(chiefdom_summary),
                                                  shadow=True, textprops={'fontweight': 'bold', 'fontsize': 8})
            ax2.set_title("🥧 ITN Given by Chiefdom", fontweight='bold', color='#2C3E50', pad=20)
            
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
        
        # Create a bar chart with blue theme
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('#f8f9fa')
        ax.set_facecolor('#ffffff')
        
        # Use blue color scheme
        colors = ['#2196f3', '#1976d2']
        grouped_data.plot(kind="bar", x="Group", y=["ITN received", "ITN given"], 
                        ax=ax, color=colors, width=0.8)
        
        # Set title based on the grouping selection
        chart_title = f"📊 ITN Data by {grouping_selection}"
        ax.set_title(chart_title, fontsize=16, fontweight='bold', color='#1565c0', pad=20)
        
        ax.set_xlabel("")
        ax.set_ylabel("Count", fontweight='bold', color='#1976d2')
        ax.grid(True, alpha=0.3, color='#2196f3')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#2196f3')
        ax.spines['bottom'].set_color('#2196f3')
        
        plt.xticks(rotation=45, ha='right')
        plt.legend(frameon=True, fancybox=True, shadow=True, 
                  facecolor='#e3f2fd', edgecolor='#2196f3')
        plt.tight_layout()
        st.pyplot(fig)
