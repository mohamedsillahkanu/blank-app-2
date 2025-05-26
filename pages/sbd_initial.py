import streamlit as st
import pandas as pd
import requests
import json
import re
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import time

# Set page config
st.set_page_config(
    page_title="Clappia API Data Fetcher",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e88e5 0%, #1976d2 100%);
        padding: 2rem 1rem;
        border-radius: 0 0 20px 20px;
        margin: -1rem -1rem 2rem -1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .logo-left, .logo-right {
        width: 80px;
        height: 80px;
        background: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        color: #1e88e5;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .header-title {
        text-align: center;
        flex: 1;
        margin: 0 2rem;
    }
    
    .header-title h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .header-title p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* API status indicators */
    .api-status {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 600;
    }
    
    .api-success {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .api-error {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .api-warning {
        background: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .api-info {
        background: #e3f2fd;
        color: #1565c0;
        border: 1px solid #bbdefb;
    }
    
    /* Connection status */
    .connection-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #1e88e5;
        margin: 1rem 0;
    }
    
    /* Data cards */
    .data-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #1e88e5;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-top: 3px solid #1e88e5;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1e88e5;
        margin: 0;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1e88e5 0%, #1976d2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Footer styling */
    .footer {
        background: linear-gradient(135deg, #1e88e5 0%, #1976d2 100%);
        color: white;
        padding: 2rem 1rem;
        margin: 3rem -1rem -1rem -1rem;
        border-radius: 20px 20px 0 0;
        text-align: center;
    }
    
    /* Loading animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #1e88e5;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 10px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <div class="header-content">
        <div class="logo-left">🔗</div>
        <div class="header-title">
            <h1>🔗 Clappia API Data Fetcher</h1>
            <p>Real-time Data Extraction and Analysis Platform</p>
        </div>
        <div class="logo-right">📊</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_data' not in st.session_state:
    st.session_state.api_data = None
if 'connection_status' not in st.session_state:
    st.session_state.connection_status = None
if 'last_fetch_time' not in st.session_state:
    st.session_state.last_fetch_time = None

# API Configuration
API_BASE_URL = "https://icf.clappia.com/app/GMB253374/submissions"
API_KEY = "icf24737083d43486e1c64bad81b107147dbff8d3"

def test_api_connection():
    """Test the API connection"""
    try:
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Try a simple request to test connection
        response = requests.get(API_BASE_URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return True, "Connection successful", response
        elif response.status_code == 401:
            return False, "Authentication failed - Invalid API key", response
        elif response.status_code == 403:
            return False, "Access forbidden - Check permissions", response
        elif response.status_code == 404:
            return False, "Endpoint not found - Check URL", response
        else:
            return False, f"API returned status code: {response.status_code}", response
            
    except requests.exceptions.Timeout:
        return False, "Connection timeout - API server may be slow", None
    except requests.exceptions.ConnectionError:
        return False, "Connection error - Check internet connection", None
    except Exception as e:
        return False, f"Unexpected error: {str(e)}", None

def fetch_clappia_data(limit=None, offset=0, filters=None):
    """Fetch data from Clappia API"""
    try:
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Build query parameters
        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        if filters:
            params.update(filters)
        
        # Make API request
        response = requests.get(API_BASE_URL, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return True, "Data fetched successfully", data
        else:
            return False, f"API error: {response.status_code} - {response.text}", None
            
    except Exception as e:
        return False, f"Error fetching data: {str(e)}", None

def process_clappia_data(api_data):
    """Process the API response data into a pandas DataFrame"""
    try:
        # Handle different possible API response structures
        if isinstance(api_data, dict):
            if 'data' in api_data:
                records = api_data['data']
            elif 'submissions' in api_data:
                records = api_data['submissions']
            elif 'records' in api_data:
                records = api_data['records']
            else:
                # If it's a dict but no clear data key, try to use it directly
                records = [api_data]
        elif isinstance(api_data, list):
            records = api_data
        else:
            return None, "Unknown data format"
        
        if not records:
            return None, "No records found in API response"
        
        # Convert to DataFrame
        df = pd.DataFrame(records)
        
        # If there's a nested structure, try to flatten it
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if column contains dictionaries
                sample_val = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                if isinstance(sample_val, dict):
                    # Flatten the dictionary columns
                    expanded = pd.json_normalize(df[col])
                    expanded.columns = [f"{col}_{subcol}" for subcol in expanded.columns]
                    df = pd.concat([df.drop(columns=[col]), expanded], axis=1)
        
        return df, "Data processed successfully"
        
    except Exception as e:
        return None, f"Error processing data: {str(e)}"

def extract_qr_data(df, qr_column_name):
    """Extract structured data from QR code text"""
    if qr_column_name not in df.columns:
        return df, f"Column '{qr_column_name}' not found"
    
    # Create empty lists to store extracted data
    districts, chiefdoms, phu_names, community_names, school_names = [], [], [], [], []
    
    # Process each row in the QR code column
    for qr_text in df[qr_column_name]:
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
    
    # Add extracted columns to dataframe
    df['District'] = districts
    df['Chiefdom'] = chiefdoms
    df['PHU_Name'] = phu_names
    df['Community_Name'] = community_names
    df['School_Name'] = school_names
    
    return df, "QR data extracted successfully"

# Sidebar for API controls
with st.sidebar:
    st.header("🔗 API Connection")
    
    # Connection test
    if st.button("🔍 Test API Connection", use_container_width=True):
        with st.spinner("Testing connection..."):
            success, message, response = test_api_connection()
            st.session_state.connection_status = (success, message, response)
        
        if success:
            st.success(f"✅ {message}")
        else:
            st.error(f"❌ {message}")
    
    st.markdown("---")
    
    # Data fetching options
    st.header("📥 Fetch Data")
    
    # Fetch parameters
    fetch_limit = st.number_input(
        "Records to fetch",
        min_value=1,
        max_value=10000,
        value=100,
        help="Number of records to fetch (max 10,000)"
    )
    
    fetch_offset = st.number_input(
        "Start from record",
        min_value=0,
        value=0,
        help="Skip this many records from the beginning"
    )
    
    # Advanced filters
    with st.expander("🔧 Advanced Filters"):
        st.info("Add custom filters for the API request")
        
        # Date filters
        date_from = st.date_input("From date", value=None)
        date_to = st.date_input("To date", value=None)
        
        # Custom filter
        custom_filter = st.text_input("Custom filter (JSON format)", placeholder='{"field": "value"}')
    
    # Fetch button
    if st.button("📥 Fetch Data from API", type="primary", use_container_width=True):
        with st.spinner("Fetching data from Clappia API..."):
            # Build filters
            filters = {}
            if date_from:
                filters['date_from'] = date_from.isoformat()
            if date_to:
                filters['date_to'] = date_to.isoformat()
            if custom_filter:
                try:
                    custom_filters = json.loads(custom_filter)
                    filters.update(custom_filters)
                except:
                    st.error("Invalid JSON in custom filter")
            
            # Fetch data
            success, message, data = fetch_clappia_data(
                limit=fetch_limit,
                offset=fetch_offset,
                filters=filters if filters else None
            )
            
            if success:
                st.session_state.api_data = data
                st.session_state.last_fetch_time = datetime.now()
                st.success(f"✅ {message}")
                st.rerun()
            else:
                st.error(f"❌ {message}")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔗 API Connection Status")

with col2:
    if st.session_state.last_fetch_time:
        st.info(f"Last fetch: {st.session_state.last_fetch_time.strftime('%Y-%m-%d %H:%M:%S')}")

# Connection status display
if st.session_state.connection_status:
    success, message, response = st.session_state.connection_status
    
    if success:
        st.markdown(f"""
        <div class="api-status api-success">
            ✅ <strong>API Connection:</strong> {message}
        </div>
        """, unsafe_allow_html=True)
        
        if response:
            st.markdown(f"""
            <div class="connection-card">
                <h4>📊 Connection Details</h4>
                <p><strong>Endpoint:</strong> {API_BASE_URL}</p>
                <p><strong>Status Code:</strong> {response.status_code}</p>
                <p><strong>Response Time:</strong> {response.elapsed.total_seconds():.2f} seconds</p>
                <p><strong>Content Type:</strong> {response.headers.get('content-type', 'Unknown')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="api-status api-error">
            ❌ <strong>API Connection:</strong> {message}
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="api-status api-info">
        ℹ️ <strong>API Connection:</strong> Not tested yet. Click "Test API Connection" to verify.
    </div>
    """, unsafe_allow_html=True)

# Display API configuration
st.markdown(f"""
<div class="data-card">
    <h4>⚙️ API Configuration</h4>
    <p><strong>Base URL:</strong> {API_BASE_URL}</p>
    <p><strong>API Key:</strong> icf24737083d43486e1c64bad81b107147dbff8d3 (configured)</p>
    <p><strong>Authentication:</strong> Bearer Token</p>
</div>
""", unsafe_allow_html=True)

# Data processing and display
if st.session_state.api_data:
    st.subheader("📊 Fetched Data Analysis")
    
    # Process the API data
    with st.spinner("Processing API data..."):
        df, process_message = process_clappia_data(st.session_state.api_data)
    
    if df is not None:
        st.markdown(f"""
        <div class="api-status api-success">
            ✅ <strong>Data Processing:</strong> {process_message}
        </div>
        """, unsafe_allow_html=True)
        
        # Quick metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(df)}</div>
                <div class="metric-label">Total Records</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(df.columns)}</div>
                <div class="metric-label">Columns</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Check for potential QR code columns
            qr_columns = [col for col in df.columns if 'qr' in col.lower() or 'scan' in col.lower() or 'code' in col.lower()]
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(qr_columns)}</div>
                <div class="metric-label">QR Columns</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            data_size = len(df) * len(df.columns)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{data_size:,}</div>
                <div class="metric-label">Data Points</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Create tabs for data analysis
        tab1, tab2, tab3, tab4 = st.tabs(["📄 Raw Data", "🔍 QR Extraction", "📊 Analysis", "📥 Export"])
        
        with tab1:
            st.subheader("📄 Raw API Data")
            st.dataframe(df, use_container_width=True)
            
            # Show column information
            with st.expander("📋 Column Information"):
                col_info = pd.DataFrame({
                    'Column': df.columns,
                    'Type': df.dtypes.astype(str),
                    'Non-Null Count': df.notna().sum(),
                    'Null Count': df.isna().sum(),
                    'Sample Value': [str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else 'N/A' for col in df.columns]
                })
                st.dataframe(col_info, use_container_width=True)
        
        with tab2:
            st.subheader("🔍 QR Code Data Extraction")
            
            # Find potential QR code columns
            qr_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['qr', 'scan', 'code', 'text'])]
            
            if qr_columns:
                selected_qr_column = st.selectbox(
                    "Select QR code column:",
                    qr_columns,
                    help="Choose the column containing QR code text data"
                )
                
                if st.button("🔄 Extract QR Data", use_container_width=True):
                    with st.spinner("Extracting structured data from QR codes..."):
                        extracted_df, extract_message = extract_qr_data(df, selected_qr_column)
                    
                    st.success(f"✅ {extract_message}")
                    
                    # Show extracted data
                    extracted_columns = ['District', 'Chiefdom', 'PHU_Name', 'Community_Name', 'School_Name']
                    available_extracted = [col for col in extracted_columns if col in extracted_df.columns]
                    
                    if available_extracted:
                        st.subheader("📋 Extracted Structured Data")
                        st.dataframe(extracted_df[available_extracted + [col for col in extracted_df.columns if col not in available_extracted]], use_container_width=True)
                        
                        # Extraction summary
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Extraction Summary:**")
                            for col in available_extracted:
                                unique_count = extracted_df[col].nunique()
                                st.write(f"- {col.replace('_', ' ')}: {unique_count} unique values")
                        
                        with col2:
                            # Check for ITN columns
                            itn_columns = [col for col in extracted_df.columns if 'itn' in col.lower()]
                            if itn_columns:
                                st.write("**ITN Data Found:**")
                                for col in itn_columns[:5]:  # Show first 5 ITN columns
                                    if pd.api.types.is_numeric_dtype(extracted_df[col]):
                                        total = extracted_df[col].sum()
                                        st.write(f"- {col}: {total:,} total")
                        
                        # Store processed data in session state
                        st.session_state.processed_data = extracted_df
            else:
                st.warning("⚠️ No potential QR code columns found. Look for columns containing 'qr', 'scan', 'code', or 'text' in their names.")
                st.write("**Available columns:**", list(df.columns))
        
        with tab3:
            st.subheader("📊 Data Analysis")
            
            # Use processed data if available, otherwise use raw data
            analysis_df = st.session_state.get('processed_data', df)
            
            # Numeric columns analysis
            numeric_cols = analysis_df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                st.write("### 📈 Numeric Data Summary")
                
                selected_numeric = st.multiselect(
                    "Select numeric columns to analyze:",
                    numeric_cols,
                    default=numeric_cols[:3] if len(numeric_cols) >= 3 else numeric_cols
                )
                
                if selected_numeric:
                    # Summary statistics
                    summary_stats = analysis_df[selected_numeric].describe()
                    st.dataframe(summary_stats, use_container_width=True)
                    
                    # Simple visualizations
                    for col in selected_numeric[:3]:  # Limit to first 3 columns
                        if analysis_df[col].notna().sum() > 0:
                            fig = px.histogram(analysis_df, x=col, title=f"Distribution of {col}")
                            st.plotly_chart(fig, use_container_width=True)
            
            # Categorical analysis
            categorical_cols = analysis_df.select_dtypes(include=['object']).columns.tolist()
            if categorical_cols:
                st.write("### 📊 Categorical Data Summary")
                
                for col in categorical_cols[:3]:  # Show first 3 categorical columns
                    if analysis_df[col].notna().sum() > 0:
                        value_counts = analysis_df[col].value_counts().head(10)
                        if len(value_counts) > 1:
                            fig = px.bar(x=value_counts.index, y=value_counts.values, title=f"Top 10 {col} Values")
                            st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            st.subheader("📥 Export Data")
            
            # Choose data to export
            export_data = st.session_state.get('processed_data', df)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV export
                csv_buffer = BytesIO()
                export_data.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv_data,
                    file_name=f"clappia_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Excel export
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    export_data.to_excel(writer, sheet_name='API Data', index=False)
                    
                    # Add metadata sheet
                    metadata = pd.DataFrame({
                        'Property': ['Fetch Time', 'Records Count', 'Columns Count', 'API Endpoint', 'Data Source'],
                        'Value': [
                            st.session_state.last_fetch_time.strftime('%Y-%m-%d %H:%M:%S') if st.session_state.last_fetch_time else 'Unknown',
                            len(export_data),
                            len(export_data.columns),
                            API_BASE_URL,
                            'Clappia API'
                        ]
                    })
                    metadata.to_excel(writer, sheet_name='Metadata', index=False)
                
                excel_data = excel_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download as Excel",
                    data=excel_data,
                    file_name=f"clappia_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
    
    else:
        st.markdown(f"""
        <div class="api-status api-error">
            ❌ <strong>Data Processing Failed:</strong> {process_message}
        </div>
        """, unsafe_allow_html=True)

else:
    # Show instructions when no data is fetched
    st.markdown("""
    <div class="data-card">
        <h3>🚀 Getting Started</h3>
        <p>Follow these steps to fetch and analyze your Clappia data:</p>
        <ol>
            <li><strong>Test Connection:</strong> Click "Test API Connection" in the sidebar to verify connectivity</li>
            <li><strong>Configure Fetch:</strong> Set the number of records and any filters you need</li>
            <li><strong>Fetch Data:</strong> Click "Fetch Data from API" to retrieve your data</li>
            <li><strong>Extract QR Data:</strong> If your data contains QR codes, use the extraction feature</li>
            <li><strong>Analyze:</strong> Use the analysis tab to explore your data</li>
            <li><strong>Export:</strong> Download your processed data in CSV or Excel format</li>
        </ol>
        
        <h4>🔧 API Configuration</h4>
        <p>The tool is pre-configured to connect to your Clappia application:</p>
        <ul>
            <li><strong>App ID:</strong> GMB253374</li>
            <li><strong>Endpoint:</strong> /submissions</li>
            <li><strong>Authentication:</strong> Bearer token authentication</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div class="footer">
    <div style="max-width: 1200px; margin: 0 auto;">
        <div style="display: flex; justify-content: center; gap: 2rem; margin-bottom: 1rem; flex-wrap: wrap;">
            <a href="#" style="color: white; text-decoration: none; opacity: 0.8;">🔗 API Docs</a>
            <a href="#" style="color: white; text-decoration: none; opacity: 0.8;">📊 Dashboard</a>
            <a href="#" style="color: white; text-decoration: none; opacity: 0.8;">📋 Reports</a>
            <a href="#" style="color: white; text-decoration: none; opacity: 0.8;">⚙️ Settings</a>
            <a href="#" style="color: white; text-decoration: none; opacity: 0.8;">❓ Help</a>
        </div>
        <hr style="border-color: rgba(255,255,255,0.3); margin: 1rem 0;">
        <p style="margin: 0.5rem 0;">© 2025 Clappia API Data Fetcher | Version 1.0</p>
        <p style="margin: 0; opacity: 0.8; font-size: 0.9rem;">
            Last updated: {datetime.now().strftime("%B %d, %Y")} | 
            Powered by Streamlit & Clappia API
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
