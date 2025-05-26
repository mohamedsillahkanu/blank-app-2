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
    page_title="ITN Distribution Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for light blue theme and modern design
st.markdown("""
<style>
    /* Main background */
    .main {
        background: linear-gradient(135deg, #e3f2fd 0%, #f0f8ff 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2196f3 0%, #1976d2 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1976d2 0%, #2196f3 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    /* Logo containers */
    .logo-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
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
        color: white;
        border: 2px solid rgba(255,255,255,0.3);
    }
    
    /* Feature cards */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border-left: 5px solid #2196f3;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid #e3f2fd;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1976d2;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Overview section */
    .overview-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
    }
    
    /* Data table styling */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    /* Section headers */
    .section-header {
        color: #1976d2;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e3f2fd;
    }
</style>
""", unsafe_allow_html=True)

# Header with logos
st.markdown("""
<div class="main-header">
    <div class="logo-container">
        <div class="logo-placeholder">🏥</div>
        <div>
            <h1 style="margin: 0; font-size: 2.5rem;">School Based Distribution of ITNs</h1>
            <p style="margin: 0; font-size: 1.1rem; opacity: 0.9;">Monitoring & Evaluation Dashboard</p>
        </div>
        <div class="logo-placeholder">🎓</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Upload file section
uploaded_file = "GMB253374_sbd_1740943126553_submissions.xlsx"

# Overview Section
st.markdown("""
<div class="overview-section">
    <h2 style="color: #1976d2; margin-bottom: 1rem;">📊 Program Overview</h2>
    <p style="font-size: 1.1rem; line-height: 1.6; color: #555;">
        The School-Based Distribution (SBD) of Insecticide-Treated Nets (ITNs) is a critical public health intervention 
        designed to ensure universal coverage of malaria prevention tools. This dashboard provides comprehensive monitoring 
        and evaluation capabilities for tracking ITN distribution across districts, chiefdoms, PHUs, communities, and schools.
    </p>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 2rem;">
        <div style="text-align: center; padding: 1rem; background: #e3f2fd; border-radius: 10px;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🏫</div>
            <div style="font-weight: bold; color: #1976d2;">School-Based</div>
            <div style="font-size: 0.9rem; color: #666;">Distribution Model</div>
        </div>
        <div style="text-align: center; padding: 1rem; background: #e8f5e8; border-radius: 10px;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🛡️</div>
            <div style="font-weight: bold; color: #2e7d32;">Malaria Prevention</div>
            <div style="font-size: 0.9rem; color: #666;">ITN Coverage</div>
        </div>
        <div style="text-align: center; padding: 1rem; background: #fff3e0; border-radius: 10px;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📈</div>
            <div style="font-weight: bold; color: #f57c00;">Real-time Monitoring</div>
            <div style="font-size: 0.9rem; color: #666;">Data Analytics</div>
        </div>
        <div style="text-align: center; padding: 1rem; background: #f3e5f5; border-radius: 10px;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎯</div>
            <div style="font-weight: bold; color: #7b1fa2;">Universal Coverage</div>
            <div style="font-size: 0.9rem; color: #666;">Health Equity</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if uploaded_file:
    # Read and process data
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
        
        # Calculate summary statistics
        total_records = len(extracted_df)
        total_received = extracted_df["ITN received"].sum() if "ITN received" in extracted_df.columns else 0
        total_given = extracted_df["ITN given"].sum() if "ITN given" in extracted_df.columns else 0
        total_districts = extracted_df["District"].nunique()
        total_schools = extracted_df["School Name"].nunique()
        distribution_rate = (total_given / total_received * 100) if total_received > 0 else 0
        
        # Summary Statistics Cards
        st.markdown('<div class="section-header">📊 Key Performance Indicators</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_records:,}</div>
                <div class="metric-label">Total Records</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_received:,}</div>
                <div class="metric-label">ITNs Received</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_given:,}</div>
                <div class="metric-label">ITNs Distributed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{distribution_rate:.1f}%</div>
                <div class="metric-label">Distribution Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_districts}</div>
                <div class="metric-label">Districts</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_schools}</div>
                <div class="metric-label">Schools</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Feature Cards Section
        st.markdown('<div class="section-header">🚀 Dashboard Features</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h3 style="color: #1976d2; margin-bottom: 1rem;">📊 Multi-Level Analysis</h3>
                <p>Analyze distribution data across multiple administrative levels including districts, chiefdoms, PHUs, communities, and schools.</p>
                <ul style="color: #666;">
                    <li>Hierarchical filtering</li>
                    <li>Drill-down capabilities</li>
                    <li>Cross-level comparisons</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h3 style="color: #1976d2; margin-bottom: 1rem;">📈 Real-time Monitoring</h3>
                <p>Track ITN distribution progress with live data updates and comprehensive performance metrics.</p>
                <ul style="color: #666;">
                    <li>Distribution rates</li>
                    <li>Coverage analysis</li>
                    <li>Performance indicators</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h3 style="color: #1976d2; margin-bottom: 1rem;">🎯 Data Visualization</h3>
                <p>Interactive charts and graphs for better insights into distribution patterns and trends.</p>
                <ul style="color: #666;">
                    <li>Interactive charts</li>
                    <li>Comparative analysis</li>
                    <li>Trend visualization</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Data Display Section
        st.markdown('<div class="section-header">📋 Data Overview</div>', unsafe_allow_html=True)
        
        # Tabs for different views
        tab1, tab2 = st.tabs(["📄 Original Data", "📊 Processed Data"])
        
        with tab1:
            st.markdown("**Sample of original data from the Excel file:**")
            st.dataframe(df_original.head(10), use_container_width=True)
        
        with tab2:
            st.markdown("**Processed data with extracted information:**")
            st.dataframe(extracted_df.head(10), use_container_width=True)
        
        # Analysis Section
        st.markdown('<div class="section-header">📊 Distribution Analysis</div>', unsafe_allow_html=True)
        
        # Create analysis buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            district_analysis = st.button("🏛️ District Analysis", use_container_width=True)
        
        with col2:
            chiefdom_analysis = st.button("🏘️ Chiefdom Analysis", use_container_width=True)
        
        with col3:
            school_analysis = st.button("🏫 School Analysis", use_container_width=True)
        
        # District Analysis
        if district_analysis:
            st.markdown("### 🏛️ District-Level Analysis")
            
            district_summary = extracted_df.groupby("District").agg({
                "ITN received": "sum",
                "ITN given": "sum"
            }).reset_index()
            district_summary["Difference"] = district_summary["ITN received"] - district_summary["ITN given"]
            district_summary["Distribution Rate"] = (district_summary["ITN given"] / district_summary["ITN received"] * 100).round(1)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.bar(district_summary, x="District", y=["ITN received", "ITN given"],
                            title="ITN Distribution by District", barmode="group",
                            color_discrete_map={"ITN received": "#2196f3", "ITN given": "#ff9800"})
                fig.update_layout(height=500, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**District Summary:**")
                st.dataframe(district_summary, use_container_width=True)
        
        # Chiefdom Analysis
        if chiefdom_analysis:
            st.markdown("### 🏘️ Chiefdom-Level Analysis")
            
            chiefdom_summary = extracted_df.groupby(["District", "Chiefdom"]).agg({
                "ITN received": "sum",
                "ITN given": "sum"
            }).reset_index()
            chiefdom_summary["Difference"] = chiefdom_summary["ITN received"] - chiefdom_summary["ITN given"]
            chiefdom_summary["Distribution Rate"] = (chiefdom_summary["ITN given"] / chiefdom_summary["ITN received"] * 100).round(1)
            
            # Create a combined label for better visualization
            chiefdom_summary['Location'] = chiefdom_summary['District'] + ' - ' + chiefdom_summary['Chiefdom']
            
            fig = px.bar(chiefdom_summary, x="Location", y=["ITN received", "ITN given"],
                        title="ITN Distribution by District and Chiefdom", barmode="group",
                        color_discrete_map={"ITN received": "#2196f3", "ITN given": "#ff9800"})
            fig.update_layout(height=600, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(chiefdom_summary.drop('Location', axis=1), use_container_width=True)
        
        # School Analysis
        if school_analysis:
            st.markdown("### 🏫 School-Level Analysis")
            
            school_summary = extracted_df.groupby(["District", "School Name"]).agg({
                "ITN received": "sum",
                "ITN given": "sum"
            }).reset_index()
            school_summary["Difference"] = school_summary["ITN received"] - school_summary["ITN given"]
            school_summary["Distribution Rate"] = (school_summary["ITN given"] / school_summary["ITN received"] * 100).round(1)
            
            # Top 10 schools by ITN received
            top_schools = school_summary.nlargest(10, "ITN received")
            
            fig = px.bar(top_schools, x="School Name", y=["ITN received", "ITN given"],
                        title="Top 10 Schools by ITN Distribution", barmode="group",
                        color_discrete_map={"ITN received": "#2196f3", "ITN given": "#ff9800"})
            fig.update_layout(height=500, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(school_summary, use_container_width=True)
        
        # Advanced Filtering Section
        st.markdown('<div class="section-header">🔍 Advanced Data Filtering</div>', unsafe_allow_html=True)
        
        # Sidebar filters
        st.sidebar.markdown("### 🎛️ Filter Controls")
        
        # Grouping selection
        grouping_selection = st.sidebar.selectbox(
            "📊 Select Analysis Level:",
            ["District", "Chiefdom", "PHU Name", "Community Name", "School Name"],
            index=0
        )
        
        # Hierarchy definition
        hierarchy = {
            "District": ["District"],
            "Chiefdom": ["District", "Chiefdom"],
            "PHU Name": ["District", "Chiefdom", "PHU Name"],
            "Community Name": ["District", "Chiefdom", "PHU Name", "Community Name"],
            "School Name": ["District", "Chiefdom", "PHU Name", "Community Name", "School Name"]
        }
        
        # Apply hierarchical filters
        filtered_df = extracted_df.copy()
        selected_values = {}
        
        for level in hierarchy[grouping_selection]:
            level_values = sorted(filtered_df[level].dropna().unique())
            if level_values:
                selected_value = st.sidebar.selectbox(f"🎯 Select {level}:", level_values)
                selected_values[level] = selected_value
                filtered_df = filtered_df[filtered_df[level] == selected_value]
        
        # Display filtered results
        if not filtered_df.empty:
            st.markdown(f"### 📊 Filtered Results ({len(filtered_df)} records)")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.dataframe(filtered_df, use_container_width=True)
            
            with col2:
                # Quick stats for filtered data
                filtered_received = filtered_df["ITN received"].sum()
                filtered_given = filtered_df["ITN given"].sum()
                filtered_rate = (filtered_given / filtered_received * 100) if filtered_received > 0 else 0
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{filtered_received:,}</div>
                    <div class="metric-label">ITNs Received</div>
                </div>
                <div class="metric-card" style="margin-top: 1rem;">
                    <div class="metric-value">{filtered_given:,}</div>
                    <div class="metric-label">ITNs Distributed</div>
                </div>
                <div class="metric-card" style="margin-top: 1rem;">
                    <div class="metric-value">{filtered_rate:.1f}%</div>
                    <div class="metric-label">Distribution Rate</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No data available for the selected filters.")
    
    except Exception as e:
        st.error(f"❌ Error processing the data: {str(e)}")
        st.info("Please ensure the Excel file contains the expected columns and data format.")

else:
    st.info("📁 Please upload an Excel file to begin the analysis.")
    
    # Show sample data structure
    st.markdown("""
    <div class="feature-card">
        <h3 style="color: #1976d2; margin-bottom: 1rem;">📋 Expected Data Format</h3>
        <p>The Excel file should contain the following columns:</p>
        <ul style="color: #666;">
            <li><strong>Scan QR code:</strong> Contains location and school information</li>
            <li><strong>ITN received:</strong> Number of ITNs received</li>
            <li><strong>ITN given:</strong> Number of ITNs distributed</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="margin-top: 4rem; padding: 2rem; background: white; border-radius: 15px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
    <p style="color: #666; margin: 0;">
        <strong>School Based Distribution of ITNs Dashboard</strong> | 
        Monitoring & Evaluation System | 
        Powered by Advanced Analytics
    </p>
</div>
""", unsafe_allow_html=True)
