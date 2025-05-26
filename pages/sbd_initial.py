import streamlit as st
import pandas as pd
import re
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from datetime import datetime

# Set page config with SBD theme
st.set_page_config(
    page_title="Sierra Leone SBD Analytics Platform",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for professional blue theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1a365d 0%, #2b77ad 25%, #3182ce 50%, #4299e1 100%);
        padding: 3rem 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
        opacity: 0.3;
    }
    
    .main-header h1 {
        position: relative;
        z-index: 1;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        position: relative;
        z-index: 1;
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 25px rgba(66, 153, 225, 0.3);
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(66, 153, 225, 0.4);
    }
    
    .metric-card h3 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .metric-card p {
        font-size: 1rem;
        font-weight: 500;
        opacity: 0.9;
    }
    
    .info-card {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 6px solid #3182ce;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(49, 130, 206, 0.2);
    }
    
    .summary-card {
        background: linear-gradient(135deg, #e6f3ff 0%, #cce7ff 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 6px solid #2b77ad;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .summary-card h3 {
        color: #1a365d;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .filter-section {
        background: linear-gradient(135deg, #f0f8ff 0%, #e1f1ff 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #4299e1;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(66, 153, 225, 0.2);
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-item {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-top: 4px solid #4299e1;
        transition: all 0.3s ease;
    }
    
    .stat-item:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .stat-item h4 {
        color: #3182ce;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .stat-item p {
        color: #4a5568;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    /* Enhanced button styling */
    .stButton > button {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(66, 153, 225, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #3182ce 0%, #2c5aa0 100%);
        box-shadow: 0 8px 25px rgba(66, 153, 225, 0.4);
        transform: translateY(-2px);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f0f8ff 0%, #e1f1ff 100%);
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #3182ce 0%, #2b77ad 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(49, 130, 206, 0.3);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        color: white;
        border-color: #2b77ad;
    }
    
    /* Data frame styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(49, 130, 206, 0.2);
    }
    
    /* Progress bar styling */
    .stProgress .st-bo {
        background: linear-gradient(90deg, #4299e1 0%, #3182ce 100%);
    }
    
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid rgba(49, 130, 206, 0.1);
    }
    
    .district-badge {
        display: inline-block;
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.2rem;
        box-shadow: 0 2px 8px rgba(66, 153, 225, 0.3);
    }
    
    .success-banner {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
    }
    
    .warning-banner {
        background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(237, 137, 54, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Main header with SBD branding
st.markdown("""
<div class="main-header">
    <h1>🏫 Sierra Leone School-Based Distribution Analytics</h1>
    <p>Comprehensive ITN Distribution Data Analysis & Visualization Platform</p>
    <p style="font-size: 1rem; margin-top: 1rem; opacity: 0.8;">
        Supporting Universal ITN Coverage Through School-Based Distribution Strategy
    </p>
</div>
""", unsafe_allow_html=True)

# SBD Districts Information
sbd_districts = {
    "Bo": {"chiefdoms": 16, "schools": 686, "phus": 149, "enrollment": 150335},
    "Bombali": {"chiefdoms": 13, "schools": 430, "phus": 96, "enrollment": 104467},
    "Bonthe": {"chiefdoms": 12, "schools": 227, "phus": 89, "enrollment": 54282},
    "Kambia": {"chiefdoms": 10, "schools": 366, "phus": 74, "enrollment": 130413},
    "Koinadugu": {"chiefdoms": 10, "schools": 247, "phus": 65, "enrollment": 57106},
    "Pujehun": {"chiefdoms": 14, "schools": 290, "phus": 103, "enrollment": 61624},
    "Tonkolili": {"chiefdoms": 19, "schools": 588, "phus": 111, "enrollment": 139224}
}

# Display SBD Districts Overview
st.markdown("### 🎯 School-Based Distribution Target Districts")
st.markdown("""
<div class="info-card">
    <strong>SBD Implementation Districts (April/May 2025):</strong><br>
    These 7 districts were selected based on malaria prevalence, ITN access, and Annual Parasite Incidence
</div>
""", unsafe_allow_html=True)

# District badges
district_badges = ""
for district in sbd_districts.keys():
    district_badges += f'<span class="district-badge">{district}</span>'
st.markdown(f'<div style="text-align: center; margin: 1rem 0;">{district_badges}</div>', unsafe_allow_html=True)

# SBD Summary Statistics
col1, col2, col3, col4 = st.columns(4)

total_schools = sum([info["schools"] for info in sbd_districts.values()])
total_phus = sum([info["phus"] for info in sbd_districts.values()])
total_enrollment = sum([info["enrollment"] for info in sbd_districts.values()])
target_itns = int(total_enrollment * 1.1)  # With 10% buffer

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>7</h3>
        <p>Target Districts</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>{total_schools:,}</h3>
        <p>Primary Schools</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3>{total_enrollment:,}</h3>
        <p>Target Pupils</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h3>{target_itns:,}</h3>
        <p>ITNs Required</p>
    </div>
    """, unsafe_allow_html=True)

# File upload section with Clappia integration
st.markdown("---")
st.markdown("### 📡 Data Source: Clappia SBD Platform")

# Direct Clappia URL integration
clappia_url = "https://icf.clappia.com/app/GMB253374/submissions"

st.markdown(f"""
<div class="info-card">
    <h4>🌐 Live Data Source</h4>
    <p><strong>Clappia URL:</strong> {clappia_url}</p>
    <p>Attempting to fetch live SBD submission data...</p>
</div>
""", unsafe_allow_html=True)

# Add requests import at the top (if not already imported)
import requests
import json
from urllib.parse import urljoin

# Attempt to fetch data from Clappia
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_clappia_data(url):
    """Attempt to fetch data from Clappia URL"""
    try:
        # First, try a simple GET request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Try to parse as JSON first
            try:
                data = response.json()
                return data, "json"
            except:
                # If not JSON, return text content
                return response.text, "html"
        else:
            return None, f"HTTP {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return None, str(e)

# Try to fetch data
with st.spinner("🔄 Fetching data from Clappia..."):
    data_result, data_type = fetch_clappia_data(clappia_url)

df_original = None

if data_result is not None:
    if data_type == "json":
        try:
            # If we got JSON data, try to convert to DataFrame
            if isinstance(data_result, dict):
                if 'submissions' in data_result:
                    df_original = pd.DataFrame(data_result['submissions'])
                elif 'data' in data_result:
                    df_original = pd.DataFrame(data_result['data'])
                else:
                    # Flatten the JSON if it's nested
                    df_original = pd.json_normalize(data_result)
            elif isinstance(data_result, list):
                df_original = pd.DataFrame(data_result)
            
            if df_original is not None and len(df_original) > 0:
                st.success(f"✅ Successfully fetched {len(df_original)} records from Clappia!")
            else:
                st.warning("⚠️ No data found in the response")
                
        except Exception as e:
            st.error(f"❌ Error processing JSON data: {str(e)}")
            
    elif data_type == "html":
        st.warning("⚠️ Received HTML response - this might be a login page or require authentication")
        
        # Provide alternative options
        st.markdown("""
        <div class="warning-banner">
            <strong>Authentication Required</strong><br>
            The Clappia URL might require authentication. Please try one of these options:
        </div>
        """, unsafe_allow_html=True)
        
        # Show authentication options
        auth_col1, auth_col2 = st.columns(2)
        
        with auth_col1:
            st.markdown("""
            <div class="info-card">
                <h4>🔐 Option 1: API Authentication</h4>
                <p>Provide your Clappia credentials below:</p>
            </div>
            """, unsafe_allow_html=True)
            
            username = st.text_input("👤 Username/Email")
            password = st.text_input("🔒 Password", type="password")
            api_token = st.text_input("🎫 API Token (if available)", type="password")
            
            if st.button("🔐 Authenticate & Fetch Data"):
                if username and password:
                    # Attempt authenticated request
                    with st.spinner("🔐 Authenticating..."):
                        try:
                            session = requests.Session()
                            
                            # Try different authentication methods
                            auth_data = {
                                'username': username,
                                'password': password,
                                'email': username
                            }
                            
                            # Attempt login
                            login_url = "https://icf.clappia.com/login"  # Assuming standard login endpoint
                            login_response = session.post(login_url, data=auth_data, timeout=10)
                            
                            if login_response.status_code == 200:
                                # Try to fetch data with authenticated session
                                data_response = session.get(clappia_url, timeout=10)
                                
                                if data_response.status_code == 200:
                                    try:
                                        auth_data = data_response.json()
                                        df_original = pd.DataFrame(auth_data)
                                        st.success(f"✅ Authenticated successfully! Fetched {len(df_original)} records")
                                    except:
                                        st.error("❌ Could not parse authenticated response as JSON")
                                else:
                                    st.error(f"❌ Failed to fetch data after authentication: {data_response.status_code}")
                            else:
                                st.error("❌ Authentication failed - please check your credentials")
                                
                        except Exception as e:
                            st.error(f"❌ Authentication error: {str(e)}")
                else:
                    st.error("❌ Please provide username and password")
        
        with auth_col2:
            st.markdown("""
            <div class="info-card">
                <h4>📁 Option 2: Manual Export</h4>
                <p>Export data from Clappia and upload here:</p>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "📁 Upload Clappia Export", 
                type=['xlsx', 'xls', 'csv', 'json'],
                help="Export your data from Clappia and upload it here"
            )
            
            if uploaded_file:
                try:
                    if uploaded_file.name.endswith('.json'):
                        json_data = json.load(uploaded_file)
                        df_original = pd.json_normalize(json_data)
                    elif uploaded_file.name.endswith('.csv'):
                        df_original = pd.read_csv(uploaded_file)
                    else:
                        df_original = pd.read_excel(uploaded_file)
                    
                    st.success(f"✅ File uploaded successfully! {len(df_original)} records loaded")
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
    else:
        st.error(f"❌ Failed to fetch data: {data_type}")
        
        # Provide fallback options
        st.markdown("""
        <div class="warning-banner">
            <strong>Connection Failed</strong><br>
            Unable to connect to Clappia. This could be due to network restrictions, authentication requirements, or CORS policies.
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "📁 Upload Clappia Data File", 
            type=['xlsx', 'xls', 'csv', 'json'],
            help="Please export your data from Clappia and upload it here"
        )
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.json'):
                    json_data = json.load(uploaded_file)
                    df_original = pd.json_normalize(json_data)
                elif uploaded_file.name.endswith('.csv'):
                    df_original = pd.read_csv(uploaded_file)
                else:
                    df_original = pd.read_excel(uploaded_file)
                
                st.success(f"✅ File uploaded successfully! {len(df_original)} records loaded")
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")

else:
    st.error("❌ Unable to fetch data from Clappia URL")
    
    # Provide manual upload option
    uploaded_file = st.file_uploader(
        "📁 Upload Clappia Data File", 
        type=['xlsx', 'xls', 'csv', 'json'],
        help="Please export your data from Clappia and upload it here"
    )
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.json'):
                json_data = json.load(uploaded_file)
                df_original = pd.json_normalize(json_data)
            elif uploaded_file.name.endswith('.csv'):
                df_original = pd.read_csv(uploaded_file)
            else:
                df_original = pd.read_excel(uploaded_file)
            
            st.success(f"✅ File uploaded successfully! {len(df_original)} records loaded")
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

# Continue with the rest of the analysis if we have data
if df_original is not None and len(df_original) > 0:
    try:
        # Read the uploaded file
        if uploaded_file.name.endswith('.csv'):
            df_original = pd.read_csv(uploaded_file)
        else:
            df_original = pd.read_excel(uploaded_file)
        
        # Create enhanced extraction for SBD data
        districts, chiefdoms, phu_names, community_names, school_names = [], [], [], [], []
        
        # Process QR code data with enhanced patterns
        qr_column = None
        for col in df_original.columns:
            if 'qr' in col.lower() or 'scan' in col.lower():
                qr_column = col
                break
        
        if qr_column:
            for qr_text in df_original[qr_column]:
                if pd.isna(qr_text):
                    districts.append(None)
                    chiefdoms.append(None)
                    phu_names.append(None)
                    community_names.append(None)
                    school_names.append(None)
                    continue
                    
                # Enhanced regex patterns for SBD data
                district_match = re.search(r"District:\s*([^\n\r]+)", str(qr_text), re.IGNORECASE)
                districts.append(district_match.group(1).strip() if district_match else None)
                
                chiefdom_match = re.search(r"Chiefdom:\s*([^\n\r]+)", str(qr_text), re.IGNORECASE)
                chiefdoms.append(chiefdom_match.group(1).strip() if chiefdom_match else None)
                
                phu_match = re.search(r"PHU\s*name:\s*([^\n\r]+)", str(qr_text), re.IGNORECASE)
                phu_names.append(phu_match.group(1).strip() if phu_match else None)
                
                community_match = re.search(r"Community\s*name:\s*([^\n\r]+)", str(qr_text), re.IGNORECASE)
                community_names.append(community_match.group(1).strip() if community_match else None)
                
                school_match = re.search(r"(?:Name of school|School name):\s*([^\n\r]+)", str(qr_text), re.IGNORECASE)
                school_names.append(school_match.group(1).strip() if school_match else None)
        
        # Create enhanced DataFrame
        extracted_df = pd.DataFrame({
            "District": districts,
            "Chiefdom": chiefdoms,
            "PHU_Name": phu_names,
            "Community_Name": community_names,
            "School_Name": school_names
        })
        
        # Add all other columns from original DataFrame
        for column in df_original.columns:
            if column != qr_column:
                extracted_df[column] = df_original[column]
        
        # Enhanced metrics calculation
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_records = len(extracted_df)
        unique_schools = extracted_df['School_Name'].nunique()
        unique_districts = extracted_df['District'].nunique()
        
        # Calculate ITN metrics if columns exist
        itn_received = 0
        itn_given = 0
        for col in extracted_df.columns:
            if 'received' in col.lower() and 'itn' in col.lower():
                itn_received = extracted_df[col].sum()
            if 'given' in col.lower() and 'itn' in col.lower():
                itn_given = extracted_df[col].sum()
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{total_records:,}</h3>
                <p>Total Records</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{unique_schools:,}</h3>
                <p>Schools Covered</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{unique_districts}</h3>
                <p>Districts</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{itn_received:,}</h3>
                <p>ITNs Received</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="metric-card">
                <h3>{itn_given:,}</h3>
                <p>ITNs Distributed</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Coverage Analysis
        st.markdown("---")
        st.markdown("### 📊 SBD Coverage Analysis")
        
        coverage_data = []
        for district, info in sbd_districts.items():
            district_data = extracted_df[extracted_df['District'] == district]
            schools_covered = district_data['School_Name'].nunique()
            coverage_percentage = (schools_covered / info['schools']) * 100 if info['schools'] > 0 else 0
            
            coverage_data.append({
                'District': district,
                'Target_Schools': info['schools'],
                'Schools_Covered': schools_covered,
                'Coverage_Percentage': coverage_percentage,
                'Target_Enrollment': info['enrollment']
            })
        
        coverage_df = pd.DataFrame(coverage_data)
        
        # Display coverage summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 School Coverage by District")
            fig_coverage = px.bar(
                coverage_df,
                x='District',
                y=['Target_Schools', 'Schools_Covered'],
                title="School Coverage Progress",
                color_discrete_sequence=['#90cdf4', '#4299e1'],
                barmode='group'
            )
            fig_coverage.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#2d3748'),
                title_font_size=16,
                xaxis_title="District",
                yaxis_title="Number of Schools"
            )
            st.plotly_chart(fig_coverage, use_container_width=True)
        
        with col2:
            st.markdown("#### 📈 Coverage Percentage")
            fig_pie = px.pie(
                coverage_df,
                values='Schools_Covered',
                names='District',
                title="Distribution of Covered Schools by District",
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#2d3748'),
                title_font_size=16
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Data Quality Assessment
        st.markdown("### 🔍 Data Quality Assessment")
        
        quality_metrics = []
        for col in ['District', 'Chiefdom', 'PHU_Name', 'School_Name']:
            if col in extracted_df.columns:
                completeness = (extracted_df[col].notna().sum() / len(extracted_df)) * 100
                unique_count = extracted_df[col].nunique()
                quality_metrics.append({
                    'Field': col,
                    'Completeness_%': completeness,
                    'Unique_Values': unique_count
                })
        
        quality_df = pd.DataFrame(quality_metrics)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📋 Data Completeness")
            fig_quality = px.bar(
                quality_df,
                x='Field',
                y='Completeness_%',
                title="Data Completeness by Field",
                color='Completeness_%',
                color_continuous_scale='Blues'
            )
            fig_quality.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#2d3748'),
                title_font_size=16,
                xaxis_title="Data Fields",
                yaxis_title="Completeness (%)"
            )
            st.plotly_chart(fig_quality, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Data Summary Table")
            st.dataframe(quality_df, use_container_width=True)
        
        # Enhanced Data Display
        st.markdown("---")
        st.markdown("### 📄 Data Overview")
        
        tab1, tab2, tab3 = st.tabs(["📊 Summary Statistics", "📋 Extracted Data", "🔍 Raw Data Sample"])
        
        with tab1:
            # District summary
            if 'District' in extracted_df.columns:
                district_summary = extracted_df.groupby('District').agg({
                    'School_Name': 'nunique',
                    'PHU_Name': 'nunique',
                    'Chiefdom': 'nunique'
                }).round(2)
                district_summary.columns = ['Unique Schools', 'Unique PHUs', 'Unique Chiefdoms']
                district_summary = district_summary.reset_index()
                
                st.markdown("#### 🏛️ District Summary")
                st.dataframe(district_summary, use_container_width=True)
        
        with tab2:
            st.markdown("#### 📋 Processed SBD Data")
            st.dataframe(extracted_df.head(20), use_container_width=True)
            
            # Download processed data
            csv_processed = extracted_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Processed Data (CSV)",
                data=csv_processed,
                file_name=f"sbd_processed_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                help="Download the processed SBD data with extracted location information"
            )
        
        with tab3:
            st.markdown("#### 🔍 Original Data Sample")
            st.dataframe(df_original.head(10), use_container_width=True)
        
        # Advanced Analytics Section
        st.markdown("---")
        st.markdown("### 🎯 Advanced SBD Analytics")
        
        # Interactive Filtering
        with st.sidebar:
            st.markdown("""
            <div class="sidebar-header">
                🎛️ SBD Analytics Filters
            </div>
            """, unsafe_allow_html=True)
            
            # Filter options
            available_districts = extracted_df['District'].dropna().unique()
            selected_districts = st.multiselect(
                "🏛️ Select Districts",
                options=available_districts,
                default=available_districts[:3] if len(available_districts) >= 3 else available_districts,
                help="Choose districts for detailed analysis"
            )
            
            st.markdown("---")
            st.markdown("### 📊 Analysis Options")
            
            analysis_type = st.selectbox(
                "Choose Analysis Type",
                ["District Overview", "School Performance", "PHU Coverage", "Chiefdom Analysis"],
                help="Select the type of analysis to perform"
            )
            
            st.markdown("---")
            st.markdown("### 🎯 SBD Strategy Info")
            st.info("""
            **Target:** 95% registration and distribution coverage
            
            **Classes:** 1, 3, and 5 (updated from original 1-5)
            
            **Method:** Digital registration with QR codes
            """)
        
        # Filtered analysis
        if selected_districts:
            filtered_df = extracted_df[extracted_df['District'].isin(selected_districts)]
            
            st.markdown(f"### 📊 Analysis Results: {analysis_type}")
            st.markdown(f"**Filtered Data:** {len(filtered_df):,} records from {len(selected_districts)} districts")
            
            if analysis_type == "District Overview":
                # District comparison charts
                col1, col2 = st.columns(2)
                
                with col1:
                    district_counts = filtered_df['District'].value_counts()
                    fig_dist = px.bar(
                        x=district_counts.index,
                        y=district_counts.values,
                        title="Records by District",
                        color=district_counts.values,
                        color_continuous_scale='Blues'
                    )
                    fig_dist.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#2d3748'),
                        title_font_size=16,
                        xaxis_title="District",
                        yaxis_title="Number of Records"
                    )
                    st.plotly_chart(fig_dist, use_container_width=True)
                
                with col2:
                    if len(selected_districts) > 1:
                        fig_pie_dist = px.pie(
                            values=district_counts.values,
                            names=district_counts.index,
                            title="Distribution Proportion",
                            color_discrete_sequence=px.colors.sequential.Blues_r
                        )
                        fig_pie_dist.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#2d3748'),
                            title_font_size=16
                        )
                        st.plotly_chart(fig_pie_dist, use_container_width=True)
            
            elif analysis_type == "School Performance":
                if 'School_Name' in filtered_df.columns:
                    school_performance = filtered_df.groupby(['District', 'School_Name']).size().reset_index(name='Records')
                    top_schools = school_performance.nlargest(15, 'Records')
                    
                    fig_schools = px.bar(
                        top_schools,
                        x='Records',
                        y='School_Name',
                        color='District',
                        title="Top 15 Schools by Activity Records",
                        orientation='h',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
