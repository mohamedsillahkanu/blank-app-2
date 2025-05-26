import streamlit as st
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configure page
st.set_page_config(
    page_title="ITN Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for light blue theme
st.markdown("""
<style>
    /* Main theme colors */
    .stApp {
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(90deg, #87ceeb 0%, #b0e0e6 50%, #87ceeb 100%);
        padding: 1rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-bottom: 3px solid #4682b4;
        box-shadow: 0 2px 10px rgba(70, 130, 180, 0.3);
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
        background: white;
        border: 2px dashed #4682b4;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        color: #4682b4;
        text-align: center;
    }
    
    .main-title {
        color: #2c5aa0;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        margin: 0;
    }
    
    .subtitle {
        color: #4682b4;
        font-size: 1.2rem;
        text-align: center;
        margin: 0.5rem 0 0 0;
    }
    
    /* Footer styling */
    .footer-container {
        background: linear-gradient(90deg, #87ceeb 0%, #b0e0e6 50%, #87ceeb 100%);
        padding: 2rem;
        margin: 3rem -1rem -1rem -1rem;
        border-top: 3px solid #4682b4;
        text-align: center;
        color: #2c5aa0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f0f8ff 0%, #e1f5fe 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #4682b4, #87ceeb);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(70, 130, 180, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(70, 130, 180, 0.4);
    }
    
    /* Card styling for metrics */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(70, 130, 180, 0.1);
        border-left: 4px solid #4682b4;
        margin: 1rem 0;
    }
    
    /* Custom selectbox styling */
    .stSelectbox > div > div {
        background-color: white;
        border: 2px solid #87ceeb;
        border-radius: 5px;
    }
    
    /* Section headers */
    .section-header {
        color: #2c5aa0;
        border-bottom: 2px solid #87ceeb;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header with logo placeholders
st.markdown("""
<div class="header-container">
    <div class="header-content">
        <div class="logo-placeholder">
            Logo<br>Left
        </div>
        <div>
            <h1 class="main-title">📊 ITN Data Dashboard</h1>
            <p class="subtitle">Text Data Extraction & Visualization Platform</p>
        </div>
        <div class="logo-placeholder">
            Logo<br>Right
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# File upload section
uploaded_file = "GMB253374_sbd_1740943126553_submissions.xlsx"

if uploaded_file:
    # Read the uploaded Excel file
    try:
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
        
        # Key metrics section
        st.markdown('<h2 class="section-header">📈 Key Metrics Overview</h2>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_received = extracted_df["ITN received"].sum()
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #4682b4; margin: 0;">Total ITN Received</h3>
                <h2 style="color: #2c5aa0; margin: 0.5rem 0 0 0;">{total_received:,}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_given = extracted_df["ITN given"].sum()
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #4682b4; margin: 0;">Total ITN Given</h3>
                <h2 style="color: #2c5aa0; margin: 0.5rem 0 0 0;">{total_given:,}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            difference = total_received - total_given
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #4682b4; margin: 0;">Difference</h3>
                <h2 style="color: {'#d32f2f' if difference < 0 else '#2e7d32'}; margin: 0.5rem 0 0 0;">{difference:,}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            districts_count = extracted_df["District"].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #4682b4; margin: 0;">Total Districts</h3>
                <h2 style="color: #2c5aa0; margin: 0.5rem 0 0 0;">{districts_count}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Interactive dashboard section
        st.markdown('<h2 class="section-header">🎛️ Interactive Dashboard</h2>', unsafe_allow_html=True)
        
        # Sidebar for filtering options
        st.sidebar.markdown('<h2 style="color: #2c5aa0;">🔍 Filter Options</h2>', unsafe_allow_html=True)
        
        # Dashboard type selection
        dashboard_type = st.sidebar.selectbox(
            "📊 Select Dashboard Type:",
            ["Overview", "District Analysis", "Chiefdom Analysis", "Detailed Filtering"],
            index=0
        )
        
        if dashboard_type == "Overview":
            # Overview dashboard with pie charts and bar charts
            col1, col2 = st.columns(2)
            
            with col1:
                # District distribution pie chart
                district_summary = extracted_df.groupby("District").agg({
                    "ITN received": "sum",
                    "ITN given": "sum"
                }).reset_index()
                
                fig_pie1 = px.pie(
                    district_summary, 
                    values='ITN received', 
                    names='District',
                    title='ITN Received Distribution by District',
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig_pie1.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#2c5aa0'
                )
                st.plotly_chart(fig_pie1, use_container_width=True)
            
            with col2:
                # ITN Given distribution pie chart
                fig_pie2 = px.pie(
                    district_summary, 
                    values='ITN given', 
                    names='District',
                    title='ITN Given Distribution by District',
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig_pie2.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#2c5aa0'
                )
                st.plotly_chart(fig_pie2, use_container_width=True)
            
            # Interactive bar chart
            fig_bar = px.bar(
                district_summary,
                x='District',
                y=['ITN received', 'ITN given'],
                title='ITN Received vs Given by District',
                barmode='group',
                color_discrete_sequence=['#4682b4', '#87ceeb']
            )
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#2c5aa0',
                xaxis_title="",
                yaxis_title="Count"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        elif dashboard_type == "District Analysis":
            # District-specific analysis
            selected_district = st.sidebar.selectbox(
                "Select District:",
                sorted(extracted_df["District"].dropna().unique())
            )
            
            if selected_district:
                district_data = extracted_df[extracted_df["District"] == selected_district]
                
                st.subheader(f"📊 Analysis for {selected_district} District")
                
                # Metrics for selected district
                col1, col2, col3 = st.columns(3)
                with col1:
                    dist_received = district_data["ITN received"].sum()
                    st.metric("ITN Received", f"{dist_received:,}")
                with col2:
                    dist_given = district_data["ITN given"].sum()
                    st.metric("ITN Given", f"{dist_given:,}")
                with col3:
                    dist_chiefdoms = district_data["Chiefdom"].nunique()
                    st.metric("Chiefdoms", dist_chiefdoms)
                
                # Chiefdom breakdown
                chiefdom_summary = district_data.groupby("Chiefdom").agg({
                    "ITN received": "sum",
                    "ITN given": "sum"
                }).reset_index()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_pie = px.pie(
                        chiefdom_summary,
                        values='ITN received',
                        names='Chiefdom',
                        title=f'ITN Received by Chiefdom in {selected_district}',
                        color_discrete_sequence=px.colors.sequential.Blues_r
                    )
                    fig_pie.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#2c5aa0'
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    fig_bar = px.bar(
                        chiefdom_summary,
                        x='Chiefdom',
                        y=['ITN received', 'ITN given'],
                        title=f'ITN Distribution in {selected_district}',
                        barmode='group',
                        color_discrete_sequence=['#4682b4', '#87ceeb']
                    )
                    fig_bar.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='#2c5aa0',
                        xaxis_title="",
                        yaxis_title="Count"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
        
        elif dashboard_type == "Chiefdom Analysis":
            # Chiefdom-specific analysis
            selected_district = st.sidebar.selectbox(
                "Select District:",
                sorted(extracted_df["District"].dropna().unique())
            )
            
            if selected_district:
                district_data = extracted_df[extracted_df["District"] == selected_district]
                selected_chiefdom = st.sidebar.selectbox(
                    "Select Chiefdom:",
                    sorted(district_data["Chiefdom"].dropna().unique())
                )
                
                if selected_chiefdom:
                    chiefdom_data = district_data[district_data["Chiefdom"] == selected_chiefdom]
                    
                    st.subheader(f"📊 Analysis for {selected_chiefdom} Chiefdom, {selected_district} District")
                    
                    # PHU analysis
                    phu_summary = chiefdom_data.groupby("PHU Name").agg({
                        "ITN received": "sum",
                        "ITN given": "sum"
                    }).reset_index()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if not phu_summary.empty:
                            fig_pie = px.pie(
                                phu_summary,
                                values='ITN received',
                                names='PHU Name',
                                title='ITN Received by PHU',
                                color_discrete_sequence=px.colors.sequential.Blues_r
                            )
                            fig_pie.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font_color='#2c5aa0'
                            )
                            st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with col2:
                        if not phu_summary.empty:
                            fig_bar = px.bar(
                                phu_summary,
                                x='PHU Name',
                                y=['ITN received', 'ITN given'],
                                title='ITN Distribution by PHU',
                                barmode='group',
                                color_discrete_sequence=['#4682b4', '#87ceeb']
                            )
                            fig_bar.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font_color='#2c5aa0',
                                xaxis_title="",
                                yaxis_title="Count"
                            )
                            st.plotly_chart(fig_bar, use_container_width=True)
        
        else:  # Detailed Filtering
            # Original detailed filtering functionality with enhancements
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
            selected_values = {}
            
            # Apply filters based on the hierarchy for the selected grouping level
            for level in hierarchy[grouping_selection]:
                level_values = sorted(filtered_df[level].dropna().unique())
                
                if level_values:
                    selected_value = st.sidebar.selectbox(f"Select {level}", level_values)
                    selected_values[level] = selected_value
                    filtered_df = filtered_df[filtered_df[level] == selected_value]
            
            # Check if data is available after filtering
            if filtered_df.empty:
                st.warning("⚠️ No data available for the selected filters.")
            else:
                st.write(f"### 📋 Filtered Data - {len(filtered_df)} records")
                
                # Display filtered data in an interactive table
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
                
                # Summary with interactive charts
                st.subheader("📊 Interactive Summary")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Interactive pie chart
                    if not grouped_data.empty:
                        fig_pie = px.pie(
                            grouped_data,
                            values='ITN received',
                            names=group_columns[-1],  # Use the last level for names
                            title=f'ITN Received Distribution by {grouping_selection}',
                            color_discrete_sequence=px.colors.sequential.Blues_r
                        )
                        fig_pie.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='#2c5aa0'
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    # Interactive bar chart
                    if not grouped_data.empty:
                        fig_bar = px.bar(
                            grouped_data,
                            x=group_columns[-1],
                            y=['ITN received', 'ITN given'],
                            title=f'ITN Distribution by {grouping_selection}',
                            barmode='group',
                            color_discrete_sequence=['#4682b4', '#87ceeb']
                        )
                        fig_bar.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='#2c5aa0',
                            xaxis_title="",
                            yaxis_title="Count"
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)
                
                # Summary table
                st.dataframe(grouped_data, use_container_width=True)
        
        # Raw data section (collapsible)
        with st.expander("📄 View Raw Data"):
            st.subheader("Original Data Sample")
            st.dataframe(df_original.head(10), use_container_width=True)
            
            st.subheader("Extracted Data Sample")
            st.dataframe(extracted_df.head(10), use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("Please ensure the file contains the expected 'Scan QR code' column.")

else:
    st.info("📁 Please upload an Excel file to begin analysis.")

# Footer
st.markdown("""
<div class="footer-container">
    <h3>ITN Data Dashboard</h3>
    <p>Powered by Streamlit • Interactive Data Visualization Platform</p>
    <p style="font-size: 0.9rem; margin-top: 1rem;">
        © 2025 • Built with ❤️ for data-driven insights
    </p>
</div>
""", unsafe_allow_html=True)
