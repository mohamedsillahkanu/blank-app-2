import streamlit as st
import pandas as pd
import re
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from io import BytesIO
import base64

# Configure page
st.set_page_config(
    page_title="ITN Distribution Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium gold standard theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f8fbff 0%, #e8f4f8 50%, #f0f8ff 100%);
        min-height: 100vh;
    }
    
    /* Premium Header */
    .premium-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #60a5fa 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(30, 58, 138, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .premium-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
        opacity: 0.3;
    }
    
    .header-content {
        position: relative;
        z-index: 2;
    }
    
    .logo-section {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    .logo-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        min-width: 140px;
        text-align: center;
    }
    
    .logo-text {
        font-weight: 700;
        color: #1e3a8a;
        font-size: 0.9rem;
        line-height: 1.2;
    }
    
    .main-title {
        color: white;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        margin: 1rem 0;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.3rem;
        text-align: center;
        font-weight: 400;
        margin-bottom: 1rem;
    }
    
    .version-badge {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 500;
        text-align: center;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Premium Cards */
    .gold-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(59, 130, 246, 0.1);
        margin: 2rem 0;
        position: relative;
        overflow: hidden;
    }
    
    .gold-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #60a5fa, #93c5fd);
    }
    
    .intro-section {
        background: linear-gradient(135deg, #fef7e0 0%, #fef3c7 50%, #fde68a 100%);
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem 0;
        box-shadow: 0 20px 60px rgba(245, 158, 11, 0.15);
        border: 2px solid rgba(245, 158, 11, 0.2);
        position: relative;
    }
    
    .intro-title {
        color: #92400e;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .intro-text {
        color: #78350f;
        font-size: 1.1rem;
        line-height: 1.8;
        text-align: justify;
        margin-bottom: 1.5rem;
    }
    
    .highlights {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .highlight-item {
        background: rgba(255, 255, 255, 0.7);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .highlight-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .highlight-text {
        color: #92400e;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Premium Metrics */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(59, 130, 246, 0.1);
        position: relative;
        overflow: hidden;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.15);
    }
    
    .metric-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #3b82f6, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 700;
        color: #1e3a8a;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #64748b;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .metric-trend {
        font-size: 0.9rem;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 500;
        margin-top: 0.5rem;
        display: inline-block;
    }
    
    .trend-positive {
        background: rgba(34, 197, 94, 0.1);
        color: #059669;
    }
    
    .trend-neutral {
        background: rgba(59, 130, 246, 0.1);
        color: #2563eb;
    }
    
    /* Premium Buttons */
    .premium-button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
        width: 100%;
        margin: 0.5rem 0;
    }
    
    .premium-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 35px rgba(59, 130, 246, 0.4);
    }
    
    /* Advanced Analytics Section */
    .analytics-section {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem 0;
        border: 2px solid rgba(14, 165, 233, 0.2);
    }
    
    .section-title {
        color: #0c4a6e;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Export Section */
    .export-section {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        border: 2px solid rgba(34, 197, 94, 0.2);
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    .status-success {
        background: rgba(34, 197, 94, 0.1);
        color: #059669;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .status-warning {
        background: rgba(245, 158, 11, 0.1);
        color: #d97706;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .status-error {
        background: rgba(239, 68, 68, 0.1);
        color: #dc2626;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Data Quality Indicators */
    .quality-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .quality-excellent {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
    }
    
    .quality-good {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
    }
    
    .quality-fair {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
    }
    
    .quality-poor {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def calculate_data_quality_score(df):
    """Calculate data quality score based on completeness and consistency"""
    total_cells = df.size
    missing_cells = df.isnull().sum().sum()
    completeness = ((total_cells - missing_cells) / total_cells) * 100
    
    # Additional quality checks
    consistency_score = 100  # Start with perfect score
    
    # Check for negative values in ITN columns
    if 'ITN received' in df.columns and 'ITN given' in df.columns:
        negative_received = (df['ITN received'] < 0).sum()
        negative_given = (df['ITN given'] < 0).sum()
        if negative_received > 0 or negative_given > 0:
            consistency_score -= 10
    
    # Check for impossible distributions (given > received)
    if 'ITN received' in df.columns and 'ITN given' in df.columns:
        impossible_distributions = (df['ITN given'] > df['ITN received']).sum()
        if impossible_distributions > 0:
            consistency_score -= 20
    
    overall_score = (completeness + consistency_score) / 2
    return overall_score, completeness, consistency_score

def get_quality_badge(score):
    """Return quality badge based on score"""
    if score >= 95:
        return "quality-excellent", "EXCELLENT"
    elif score >= 85:
        return "quality-good", "GOOD"
    elif score >= 70:
        return "quality-fair", "FAIR"
    else:
        return "quality-poor", "POOR"

def create_download_link(df, filename):
    """Create a download link for dataframe"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='ITN_Data', index=False)
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" class="premium-button" style="text-decoration: none; display: inline-block;">📥 Download Excel Report</a>'
    return href

# Main Application Header
st.markdown("""
<div class="premium-header">
    <div class="header-content">
        <div class="logo-section">
            <div class="logo-card">
                <div class="logo-text">🏥<br>MINISTRY OF<br>HEALTH<br>SIERRA LEONE</div>
            </div>
            <div style="flex-grow: 1; text-align: center;">
                <h1 class="main-title">🏫 ITN DISTRIBUTION ANALYTICS</h1>
                <p class="subtitle">Advanced School-Based Insecticide Treated Nets Distribution Monitoring Platform</p>
                <div class="version-badge">Gold Standard Analytics Platform v2.0</div>
            </div>
            <div class="logo-card">
                <div class="logo-text">🦄<br>UNICEF<br>SIERRA LEONE<br>PARTNERSHIP</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Introduction Section
st.markdown("""
<div class="intro-section">
    <h2 class="intro-title">🎯 Mission: Eliminating Malaria Through Strategic ITN Distribution</h2>
    <p class="intro-text">
        The School-Based Insecticide Treated Nets (ITN) Distribution Program represents Sierra Leone's most comprehensive 
        and innovative approach to malaria prevention. This gold-standard analytics platform transforms raw distribution 
        data into actionable insights, enabling health officials to monitor, analyze, and optimize ITN coverage across 
        every district, chiefdom, and community. Through advanced data visualization, predictive analytics, and 
        real-time monitoring, we ensure that every family receives life-saving protection against malaria.
    </p>
    <p class="intro-text">
        This platform integrates cutting-edge technology with public health expertise to deliver unprecedented visibility 
        into distribution patterns, identify coverage gaps, and drive evidence-based decision making for maximum 
        population health impact.
    </p>
    <div class="highlights">
        <div class="highlight-item">
            <div class="highlight-icon">📊</div>
            <div class="highlight-text">Real-time Analytics</div>
        </div>
        <div class="highlight-item">
            <div class="highlight-icon">🎯</div>
            <div class="highlight-text">Precision Targeting</div>
        </div>
        <div class="highlight-item">
            <div class="highlight-icon">📈</div>
            <div class="highlight-text">Predictive Insights</div>
        </div>
        <div class="highlight-item">
            <div class="highlight-icon">🔍</div>
            <div class="highlight-text">Quality Assurance</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# File Processing Section
st.markdown('<div class="gold-card">', unsafe_allow_html=True)
st.markdown('<h2 class="section-title">📁 Data Processing Center</h2>', unsafe_allow_html=True)

# Hard-coded file for demo
uploaded_file = "GMB253374_sbd_1740943126553_submissions.xlsx"

# File upload option
upload_option = st.radio(
    "Choose data source:",
    ["Use sample data (GMB253374_sbd_1740943126553_submissions.xlsx)", "Upload new file"],
    index=0
)

if upload_option == "Upload new file":
    uploaded_file = st.file_uploader(
        "Upload Excel file containing ITN distribution data", 
        type=["xlsx"],
        help="Please upload an Excel file with QR code scan data from ITN distribution activities"
    )

if uploaded_file:
    try:
        # Read the uploaded Excel file
        if isinstance(uploaded_file, str):
            df_original = pd.read_excel(uploaded_file)
            st.success(f"✅ Successfully loaded sample data: {uploaded_file}")
        else:
            df_original = pd.read_excel(uploaded_file)
            st.success(f"✅ Successfully uploaded: {uploaded_file.name}")
        
        # Data Quality Assessment
        quality_score, completeness, consistency = calculate_data_quality_score(df_original)
        quality_class, quality_text = get_quality_badge(quality_score)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="status-indicator status-success">
                📊 {len(df_original)} Records Loaded
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="quality-badge {quality_class}">
                Data Quality: {quality_text}
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="status-indicator status-{'success' if completeness > 90 else 'warning'}">
                🎯 {completeness:.1f}% Complete
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="status-indicator status-{'success' if consistency > 90 else 'warning'}">
                ✅ {consistency:.1f}% Consistent
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Data Processing
        with st.spinner("🔄 Processing QR code data and extracting geographic information..."):
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
            
            # Add calculated fields
            extracted_df['Distribution Efficiency'] = (
                extracted_df['ITN given'] / extracted_df['ITN received'] * 100
            ).fillna(0).round(1)
            
            extracted_df['Remaining ITNs'] = extracted_df['ITN received'] - extracted_df['ITN given']
            
            # Add date processing if available
            if 'start' in extracted_df.columns:
                extracted_df['Date'] = pd.to_datetime(extracted_df['start'], errors='coerce')
                extracted_df['Month'] = extracted_df['Date'].dt.strftime('%Y-%m')
                extracted_df['Week'] = extracted_df['Date'].dt.isocalendar().week
        
        st.success("🎉 Data processing completed successfully!")
        
        # Executive Dashboard
        st.markdown('<div class="analytics-section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">📊 Executive Dashboard</h2>', unsafe_allow_html=True)
        
        # Key Performance Indicators
        total_received = extracted_df["ITN received"].sum()
        total_given = extracted_df["ITN given"].sum()
        distribution_rate = (total_given / total_received * 100) if total_received > 0 else 0
        total_schools = extracted_df["School Name"].nunique()
        total_districts = extracted_df["District"].nunique()
        total_chiefdoms = extracted_df["Chiefdom"].nunique()
        avg_efficiency = extracted_df['Distribution Efficiency'].mean()
        remaining_stock = total_received - total_given
        
        st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)
        
        metrics_data = [
            ("📦", total_received, "Total ITN Received", "🟢 Operational", "trend-positive"),
            ("🎯", total_given, "Total ITN Distributed", f"{distribution_rate:.1f}% Rate", "trend-positive"),
            ("⚡", f"{avg_efficiency:.1f}%", "Avg Distribution Efficiency", "📈 Optimizing", "trend-neutral"),
            ("🏫", total_schools, "Schools Participating", f"{total_districts} Districts", "trend-positive"),
            ("📍", total_chiefdoms, "Chiefdoms Covered", "🌍 Nationwide", "trend-positive"),
            ("📋", remaining_stock, "Remaining Stock", "💼 Available", "trend-neutral")
        ]
        
        for icon, value, label, trend, trend_class in metrics_data:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <div class="metric-value">{value:,}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-trend {trend_class}">{trend}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Advanced Analytics Section
        st.markdown('<div class="gold-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">🔬 Advanced Analytics & Insights</h2>', unsafe_allow_html=True)
        
        # Create tabs for different analysis views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🏛️ District Analysis", 
            "🏘️ Chiefdom Deep Dive", 
            "📈 Trend Analysis", 
            "🎯 Performance Matrix",
            "📊 Custom Reports"
        ])
        
        with tab1:
            st.subheader("District-Level Distribution Analysis")
            
            district_summary = extracted_df.groupby("District").agg({
                "ITN received": "sum",
                "ITN given": "sum",
                "School Name": "nunique"
            }).reset_index()
            
            district_summary["Distribution Rate (%)"] = (
                district_summary["ITN given"] / district_summary["ITN received"] * 100
            ).round(1)
            district_summary["Remaining ITNs"] = district_summary["ITN received"] - district_summary["ITN given"]
            district_summary.rename(columns={"School Name": "Schools Count"}, inplace=True)
            
            # District performance visualization
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Distribution by District', 'Distribution Rates', 'School Coverage', 'Remaining Stock'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Chart 1: Distribution volumes
            fig.add_trace(
                go.Bar(name='ITN Received', x=district_summary['District'], y=district_summary['ITN received'],
                       marker_color='#3b82f6', text=district_summary['ITN received'], textposition='auto'),
                row=1, col=1
            )
            fig.add_trace(
                go.Bar(name='ITN Given', x=district_summary['District'], y=district_summary['ITN given'],
                       marker_color='#10b981', text=district_summary['ITN given'], textposition='auto'),
                row=1, col=1
            )
            
            # Chart 2: Distribution rates
            fig.add_trace(
                go.Scatter(x=district_summary['District'], y=district_summary['Distribution Rate (%)'],
                          mode='markers+lines', marker_color='#f59e0b', marker_size=12,
                          name='Distribution Rate (%)', text=district_summary['Distribution Rate (%)'],
                          textposition='top center'),
                row=1, col=2
            )
            
            # Chart 3: School coverage
            fig.add_trace(
                go.Bar(x=district_summary['District'], y=district_summary['Schools Count'],
                       marker_color='#8b5cf6', name='Schools Count',
                       text=district_summary['Schools Count'], textposition='auto'),
                row=2, col=1
            )
            
            # Chart 4: Remaining stock
            fig.add_trace(
                go.Bar(x=district_summary['District'], y=district_summary['Remaining ITNs'],
                       marker_color='#ef4444', name='Remaining ITNs',
                       text=district_summary['Remaining ITNs'], textposition='auto'),
                row=2, col=2
            )
            
            fig.update_layout(height=800, showlegend=True, template='plotly_white',
                            title_text="Comprehensive District Analysis Dashboard")
            st.plotly_chart(fig, use_container_width=True)
            
            # District summary table
            st.subheader("📋 District Performance Summary")
            st.dataframe(district_summary, use_container_width=True)
        
        with tab2:
            st.subheader("Chiefdom-Level Deep Dive Analysis")
            
            chiefdom_summary = extracted_df.groupby(["District", "Chiefdom"]).agg({
                "ITN received": "sum",
                "ITN given": "sum",
                "School Name": "nunique",
                "Community Name": "nunique"
            }).reset_index()
            
            chiefdom_summary["Distribution Rate (%)"] = (
                chiefdom_summary["ITN given"] / chiefdom_summary["ITN received"] * 100
            ).round(1)
            chiefdom_summary["Efficiency Score"] = np.where(
                chiefdom_summary["Distribution Rate (%)"] >= 95, "🟢 Excellent",
                np.where(chiefdom_summary["Distribution Rate (%)"] >= 85, "🟡 Good",
                        np.where(chiefdom_summary["Distribution Rate (%)"] >= 70, "🟠 Fair", "🔴 Needs Attention"))
            )
            chiefdom_summary.rename(columns={
                "School Name": "Schools Count",
                "Community Name": "Communities Count"
            }, inplace=True)
            
            # Interactive chiefdom analysis
            selected_district = st.selectbox("Select District for Detailed Analysis:", 
                                           sorted(chiefdom_summary['District'].unique()))
            
            filtered_chiefdom = chiefdom_summary[chiefdom_summary['District'] == selected_district]
            
            if len(filtered_chiefdom) > 0:
                # Create chiefdom visualization
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=filtered_chiefdom['ITN received'],
                    y=filtered_chiefdom['Distribution Rate (%)'],
                    mode='markers+text',
                    marker=dict(
                        size=filtered_chiefdom['Schools Count'] * 5,
                        color=filtered_chiefdom['Distribution Rate (%)'],
                        colorscale='RdYlGn',
                        showscale=True,
                        colorbar=dict(title="Distribution Rate (%)")
                    ),
                    text=filtered_chiefdom['Chiefdom'],
                    textposition='top center',
                    hovertemplate='<b>%{text}</b><br>' +
                                'ITNs Received: %{x}<br>' +
                                'Distribution Rate: %{y}%<br>' +
                                'Schools: ' + filtered_chiefdom['Schools Count'].astype(str) +
                                '<extra></extra>'
                ))
                
                fig.update_layout(
                    title=f'Chiefdom Performance Matrix - {selected_district}',
                    xaxis_title='ITNs Received',
                    yaxis_title='Distribution Rate (%)',
                    template='plotly_white',
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(filtered_chiefdom, use_container_width=True)
            else:
                st.warning("No data available for selected district.")
        
        with tab3:
            st.subheader("📈 Temporal Trend Analysis")
            
            if 'Date' in extracted_df.columns:
                # Monthly trend analysis
                monthly_trend = extracted_df.groupby('Month').agg({
                    "ITN received": "sum",
                    "ITN given": "sum",
                    "School Name": "nunique"
                }).reset_index()
                
                monthly_trend['Distribution Rate'] = (
                    monthly_trend['ITN given'] / monthly_trend['ITN received'] * 100
                ).round(1)
                
                # Create trend visualization
                fig = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('Monthly Distribution Volumes', 'Distribution Efficiency Trend'),
                    specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
                )
                
                # Monthly volumes
                fig.add_trace(
                    go.Bar(x=monthly_trend['Month'], y=monthly_trend['ITN received'],
                           name='ITN Received', marker_color='#3b82f6'),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Bar(x=monthly_trend['Month'], y=monthly_trend['ITN given'],
                           name='ITN Given', marker_color='#10b981'),
                    row=1, col=1
                )
                
                # Add schools count as secondary y-axis
                fig.add_trace(
                    go.Scatter(x=monthly_trend['Month'], y=monthly_trend['School Name'],
                              mode='markers+lines', name='Schools Active',
                              marker_color='#f59e0b', yaxis='y2'),
                    row=1, col=1, secondary_y=True
                )
                
                # Distribution rate trend
                fig.add_trace(
                    go.Scatter(x=monthly_trend['Month'], y=monthly_trend['Distribution Rate'],
                              mode='markers+lines', name='Distribution Rate (%)',
                              marker_color='#8b5cf6', line=dict(width=3)),
                    row=2, col=1
                )
                
                fig.update_yaxes(title_text="Number of ITNs", row=1, col=1)
                fig.update_yaxes(title_text="Number of Schools", row=1, col=1, secondary_y=True)
                fig.update_yaxes(title_text="Distribution Rate (%)", row=2, col=1)
                fig.update_xaxes(title_text="Month", row=2, col=1)
                
                fig.update_layout(height=800, template='plotly_white',
                                title_text="ITN Distribution Temporal Analysis")
                
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(monthly_trend, use_container_width=True)
            else:
                st.info("📅 Date information not available in current dataset for trend analysis.")
        
        with tab4:
            st.subheader("🎯 Performance Matrix & Risk Assessment")
            
            # Calculate performance metrics by school
            school_performance = extracted_df.groupby(['District', 'Chiefdom', 'School Name']).agg({
                "ITN received": "sum",
                "ITN given": "sum"
            }).reset_index()
            
            school_performance['Distribution Rate'] = (
                school_performance['ITN given'] / school_performance['ITN received'] * 100
            ).round(1)
            
            school_performance['Risk Level'] = np.where(
                school_performance['Distribution Rate'] < 70, '🔴 High Risk',
                np.where(school_performance['Distribution Rate'] < 85, '🟡 Medium Risk', '🟢 Low Risk')
            )
            
            # Performance matrix visualization
            fig = px.scatter(
                school_performance,
                x='ITN received',
                y='Distribution Rate',
                color='District',
                size='ITN given',
                hover_data=['School Name', 'Chiefdom'],
                title='School Performance Matrix: Distribution Efficiency vs Volume'
            )
            
            # Add reference lines
            fig.add_hline(y=85, line_dash="dash", line_color="orange", 
                         annotation_text="Target Efficiency (85%)")
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         annotation_text="Minimum Threshold (70%)")
            
            fig.update_layout(height=600, template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
            
            # Risk assessment summary
            risk_summary = school_performance['Risk Level'].value_counts().reset_index()
            risk_summary.columns = ['Risk Level', 'Number of Schools']
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🚨 Risk Assessment Summary")
                st.dataframe(risk_summary, use_container_width=True)
            
            with col2:
                # Risk distribution pie chart
                fig_pie = px.pie(risk_summary, values='Number of Schools', names='Risk Level',
                               title='Distribution of School Risk Levels',
                               color_discrete_map={
                                   '🟢 Low Risk': '#10b981',
                                   '🟡 Medium Risk': '#f59e0b',
                                   '🔴 High Risk': '#ef4444'
                               })
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # High-risk schools table
            high_risk_schools = school_performance[
                school_performance['Risk Level'] == '🔴 High Risk'
            ].sort_values('Distribution Rate')
            
            if len(high_risk_schools) > 0:
                st.subheader("⚠️ Schools Requiring Immediate Attention")
                st.dataframe(high_risk_schools, use_container_width=True)
            else:
                st.success("🎉 No high-risk schools identified!")
        
        with tab5:
            st.subheader("📊 Custom Reports & Export Center")
            
            # Report configuration
            col1, col2 = st.columns(2)
            
            with col1:
                report_level = st.selectbox(
                    "Select Report Level:",
                    ["District", "Chiefdom", "PHU Name", "Community Name", "School Name"]
                )
                
                include_metrics = st.multiselect(
                    "Include Metrics:",
                    ["ITN received", "ITN given", "Distribution Rate", "Remaining ITNs", 
                     "School Count", "Community Count", "Efficiency Score"],
                    default=["ITN received", "ITN given", "Distribution Rate"]
                )
            
            with col2:
                date_filter = st.checkbox("Apply Date Filter")
                if date_filter and 'Date' in extracted_df.columns:
                    date_range = st.date_input(
                        "Select Date Range:",
                        value=[extracted_df['Date'].min(), extracted_df['Date'].max()],
                        min_value=extracted_df['Date'].min(),
                        max_value=extracted_df['Date'].max()
                    )
                
                export_format = st.selectbox(
                    "Export Format:",
                    ["Excel", "CSV", "JSON"]
                )
            
            # Generate custom report
            if st.button("🚀 Generate Custom Report", key="custom_report"):
                # Filter data based on selections
                report_df = extracted_df.copy()
                
                if date_filter and 'Date' in extracted_df.columns and len(date_range) == 2:
                    report_df = report_df[
                        (report_df['Date'] >= pd.Timestamp(date_range[0])) & 
                        (report_df['Date'] <= pd.Timestamp(date_range[1]))
                    ]
                
                # Group by selected level
                if report_level == "School Name":
                    group_cols = ["District", "Chiefdom", "PHU Name", "Community Name", "School Name"]
                elif report_level == "Community Name":
                    group_cols = ["District", "Chiefdom", "PHU Name", "Community Name"]
                elif report_level == "PHU Name":
                    group_cols = ["District", "Chiefdom", "PHU Name"]
                elif report_level == "Chiefdom":
                    group_cols = ["District", "Chiefdom"]
                else:
                    group_cols = ["District"]
                
                # Generate aggregated report
                custom_report = report_df.groupby(group_cols).agg({
                    "ITN received": "sum",
                    "ITN given": "sum",
                    "School Name": "nunique",
                    "Community Name": "nunique"
                }).reset_index()
                
                # Add calculated metrics
                custom_report["Distribution Rate"] = (
                    custom_report["ITN given"] / custom_report["ITN received"] * 100
                ).round(1)
                custom_report["Remaining ITNs"] = custom_report["ITN received"] - custom_report["ITN given"]
                custom_report["Efficiency Score"] = np.where(
                    custom_report["Distribution Rate"] >= 95, "Excellent",
                    np.where(custom_report["Distribution Rate"] >= 85, "Good",
                            np.where(custom_report["Distribution Rate"] >= 70, "Fair", "Needs Attention"))
                )
                
                # Filter columns based on selection
                display_cols = group_cols.copy()
                if "ITN received" in include_metrics:
                    display_cols.append("ITN received")
                if "ITN given" in include_metrics:
                    display_cols.append("ITN given")
                if "Distribution Rate" in include_metrics:
                    display_cols.append("Distribution Rate")
                if "Remaining ITNs" in include_metrics:
                    display_cols.append("Remaining ITNs")
                if "School Count" in include_metrics:
                    display_cols.append("School Name")
                if "Community Count" in include_metrics:
                    display_cols.append("Community Name")
                if "Efficiency Score" in include_metrics:
                    display_cols.append("Efficiency Score")
                
                final_report = custom_report[display_cols]
                
                st.success(f"✅ Custom report generated with {len(final_report)} records")
                st.dataframe(final_report, use_container_width=True)
                
                # Export functionality
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"ITN_Distribution_Report_{report_level}_{timestamp}"
                
                if export_format == "Excel":
                    st.markdown(create_download_link(final_report, f"{filename}.xlsx"), 
                              unsafe_allow_html=True)
                elif export_format == "CSV":
                    csv = final_report.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV Report",
                        data=csv,
                        file_name=f"{filename}.csv",
                        mime="text/csv"
                    )
                elif export_format == "JSON":
                    json_data = final_report.to_json(orient='records', indent=2)
                    st.download_button(
                        label="📥 Download JSON Report",
                        data=json_data,
                        file_name=f"{filename}.json",
                        mime="application/json"
                    )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Data Explorer Section
        st.markdown('<div class="gold-card">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">🔍 Interactive Data Explorer</h2>', unsafe_allow_html=True)
        
        # Sidebar filters
        st.sidebar.markdown("### 🎛️ Advanced Filters")
        st.sidebar.markdown("---")
        
        # Multi-level filtering
        selected_districts = st.sidebar.multiselect(
            "Select Districts:",
            options=sorted(extracted_df['District'].dropna().unique()),
            default=sorted(extracted_df['District'].dropna().unique())[:3]
        )
        
        if selected_districts:
            filtered_chiefdoms = extracted_df[extracted_df['District'].isin(selected_districts)]['Chiefdom'].dropna().unique()
            selected_chiefdoms = st.sidebar.multiselect(
                "Select Chiefdoms:",
                options=sorted(filtered_chiefdoms),
                default=[]
            )
            
            # Distribution efficiency filter
            min_efficiency = st.sidebar.slider(
                "Minimum Distribution Efficiency (%):",
                min_value=0,
                max_value=100,
                value=0,
                step=5
            )
            
            # ITN volume filter
            min_itn_received = st.sidebar.number_input(
                "Minimum ITNs Received:",
                min_value=0,
                value=0,
                step=10
            )
            
            # Apply filters
            explorer_df = extracted_df[
                (extracted_df['District'].isin(selected_districts)) &
                (extracted_df['Distribution Efficiency'] >= min_efficiency) &
                (extracted_df['ITN received'] >= min_itn_received)
            ]
            
            if selected_chiefdoms:
                explorer_df = explorer_df[explorer_df['Chiefdom'].isin(selected_chiefdoms)]
            
            st.write(f"### 📊 Filtered Results: {len(explorer_df)} records")
            
            if len(explorer_df) > 0:
                # Summary metrics for filtered data
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total ITNs Received", f"{explorer_df['ITN received'].sum():,}")
                with col2:
                    st.metric("Total ITNs Given", f"{explorer_df['ITN given'].sum():,}")
                with col3:
                    st.metric("Avg Efficiency", f"{explorer_df['Distribution Efficiency'].mean():.1f}%")
                with col4:
                    st.metric("Schools Involved", f"{explorer_df['School Name'].nunique()}")
                
                # Interactive scatter plot
                fig = px.scatter(
                    explorer_df,
                    x='ITN received',
                    y='ITN given',
                    color='District',
                    size='Distribution Efficiency',
                    hover_data=['School Name', 'Chiefdom', 'Community Name'],
                    title='Distribution Scatter Analysis (Filtered Data)',
                    labels={'ITN received': 'ITNs Received', 'ITN given': 'ITNs Distributed'}
                )
                
                # Add perfect distribution line
                max_val = max(explorer_df['ITN received'].max(), explorer_df['ITN given'].max())
                fig.add_trace(go.Scatter(
                    x=[0, max_val],
                    y=[0, max_val],
                    mode='lines',
                    line=dict(dash='dash', color='red'),
                    name='Perfect Distribution (100%)',
                    showlegend=True
                ))
                
                fig.update_layout(height=600, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)
                
                # Detailed table
                st.subheader("📋 Detailed Filtered Data")
                display_columns = ['District', 'Chiefdom', 'School Name', 'ITN received', 
                                 'ITN given', 'Distribution Efficiency', 'Remaining ITNs']
                st.dataframe(explorer_df[display_columns], use_container_width=True)
                
            else:
                st.warning("⚠️ No data matches the selected filters. Please adjust your criteria.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export and Reporting Section
        st.markdown('<div class="export-section">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">📤 Data Export & Reporting Hub</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export Complete Dataset", use_container_width=True):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                st.markdown(create_download_link(extracted_df, f"Complete_ITN_Data_{timestamp}.xlsx"), 
                          unsafe_allow_html=True)
        
        with col2:
            if st.button("📈 Export District Summary", use_container_width=True):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                district_export = extracted_df.groupby("District").agg({
                    "ITN received": "sum",
                    "ITN given": "sum",
                    "School Name": "nunique"
                }).reset_index()
                district_export["Distribution Rate (%)"] = (
                    district_export["ITN given"] / district_export["ITN received"] * 100
                ).round(1)
                st.markdown(create_download_link(district_export, f"District_Summary_{timestamp}.xlsx"), 
                          unsafe_allow_html=True)
        
        with col3:
            if st.button("📋 Export Performance Report", use_container_width=True):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                performance_export = extracted_df.groupby(['District', 'Chiefdom', 'School Name']).agg({
                    "ITN received": "sum",
                    "ITN given": "sum"
                }).reset_index()
                performance_export['Distribution Rate'] = (
                    performance_export['ITN given'] / performance_export['ITN received'] * 100
                ).round(1)
                performance_export['Status'] = np.where(
                    performance_export['Distribution Rate'] >= 90, 'Excellent',
                    np.where(performance_export['Distribution Rate'] >= 75, 'Good', 'Needs Improvement')
                )
                st.markdown(create_download_link(performance_export, f"Performance_Report_{timestamp}.xlsx"), 
                          unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("Please ensure your Excel file contains a 'Scan QR code' column with the required data format.")

else:
    # Welcome screen when no file is uploaded
    st.markdown('<div class="gold-card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h2 style="color: #1e3a8a; margin-bottom: 2rem;">🚀 Ready to Begin Analysis</h2>
        <p style="font-size: 1.2rem; color: #64748b; margin-bottom: 2rem;">
            Upload your ITN distribution data to unlock powerful insights and comprehensive analytics.
        </p>
        <div style="background: linear-gradient(135deg, #f0f9ff, #e0f2fe); padding: 2rem; border-radius: 15px; border: 2px solid rgba(59, 130, 246, 0.2);">
            <h3 style="color: #0c4a6e;">📋 Expected Data Format:</h3>
            <ul style="text-align: left; color: #334155; font-size: 1rem; line-height: 1.8;">
                <li><strong>Scan QR code</strong> column containing geographic and institutional data</li>
                <li><strong>ITN received</strong> and <strong>ITN given</strong> columns with distribution numbers</li>
                <li><strong>Date/time</strong> information for temporal analysis</li>
                <li>Additional contextual columns as available</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8fafc, #f1f5f9); border-radius: 15px; margin-top: 2rem;">
    <h3 style="color: #1e3a8a; margin-bottom: 1rem;">🏥 ITN Distribution Analytics Platform</h3>
    <p style="color: #64748b; font-size: 1rem; margin-bottom: 1rem;">
        <strong>Ministry of Health, Sierra Leone</strong> | <strong>UNICEF Partnership</strong> | <strong>Malaria Elimination Initiative</strong>
    </p>
    <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 1rem;">
        <div style="color: #059669;">✅ Real-time Monitoring</div>
        <div style="color: #0ea5e9;">📊 Advanced Analytics</div>
        <div style="color: #8b5cf6;">🎯 Performance Optimization</div>
        <div style="color: #f59e0b;">📈 Predictive Insights</div>
    </div>
    <p style="color: #9ca3af; font-size: 0.9rem; margin-top: 1.5rem;">
        Gold Standard Platform v2.0 | Powered by Advanced Data Science | Built for Public Health Impact
    </p>
</div>
""", unsafe_allow_html=True)
