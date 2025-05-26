import streamlit as st
import pandas as pd
import re
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime
import gc

# Set page config
st.set_page_config(
    page_title="Text Data Extraction & Visualization",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 1rem 1rem;
    }
    
    .stats-card {
        background-color: #fff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 3px solid #FF6B6B;
        margin: 0.5rem 0;
    }
    
    .filter-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4ECDC4;
        margin: 1rem 0;
    }
    
    .summary-card {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 0.5rem 0;
    }
    
    .memory-info {
        background-color: #e3f2fd;
        padding: 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
        color: #1976d2;
        margin: 0.5rem 0;
    }
    
    .upload-section {
        background-color: #fff3e0;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #FF6B6B;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 Text Data Extraction & Visualization Tool</h1>
    <p>Advanced QR code data extraction with interactive visualization and filtering</p>
</div>
""", unsafe_allow_html=True)

# Memory optimization functions
@st.cache_data
def optimize_dataframe_memory(df):
    """Optimize dataframe memory usage"""
    df_optimized = df.copy()
    
    for col in df_optimized.columns:
        if df_optimized[col].dtype == 'object':
            # Convert to category if unique values < 50% of total
            unique_ratio = df_optimized[col].nunique() / len(df_optimized)
            if unique_ratio < 0.5:
                df_optimized[col] = df_optimized[col].astype('category')
        elif df_optimized[col].dtype in ['int64', 'int32']:
            df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='integer')
        elif df_optimized[col].dtype in ['float64', 'float32']:
            df_optimized[col] = pd.to_numeric(df_optimized[col], downcast='float')
    
    return df_optimized

def get_memory_usage(df):
    """Get memory usage information"""
    memory_usage = df.memory_usage(deep=True).sum()
    return f"{memory_usage / 1024**2:.2f} MB"

@st.cache_data
def extract_qr_data(df_original):
    """Optimized QR code data extraction with caching"""
    # Pre-compile regex patterns for better performance
    patterns = {
        'district': re.compile(r"District:\s*([^\n]+)", re.IGNORECASE),
        'chiefdom': re.compile(r"Chiefdom:\s*([^\n]+)", re.IGNORECASE),
        'phu': re.compile(r"PHU name:\s*([^\n]+)", re.IGNORECASE),
        'community': re.compile(r"Community name:\s*([^\n]+)", re.IGNORECASE),
        'school': re.compile(r"Name of school:\s*([^\n]+)", re.IGNORECASE)
    }
    
    # Initialize lists with proper capacity
    num_rows = len(df_original)
    extracted_data = {
        "District": [None] * num_rows,
        "Chiefdom": [None] * num_rows,
        "PHU Name": [None] * num_rows,
        "Community Name": [None] * num_rows,
        "School Name": [None] * num_rows
    }
    
    # Vectorized processing
    qr_column = df_original["Scan QR code"].fillna('')
    
    for idx, qr_text in enumerate(qr_column):
        if qr_text:
            qr_str = str(qr_text)
            
            # Extract using pre-compiled patterns
            district_match = patterns['district'].search(qr_str)
            extracted_data["District"][idx] = district_match.group(1).strip() if district_match else None
            
            chiefdom_match = patterns['chiefdom'].search(qr_str)
            extracted_data["Chiefdom"][idx] = chiefdom_match.group(1).strip() if chiefdom_match else None
            
            phu_match = patterns['phu'].search(qr_str)
            extracted_data["PHU Name"][idx] = phu_match.group(1).strip() if phu_match else None
            
            community_match = patterns['community'].search(qr_str)
            extracted_data["Community Name"][idx] = community_match.group(1).strip() if community_match else None
            
            school_match = patterns['school'].search(qr_str)
            extracted_data["School Name"][idx] = school_match.group(1).strip() if school_match else None
    
    # Create DataFrame and add other columns efficiently
    extracted_df = pd.DataFrame(extracted_data)
    
    # Add other columns (excluding QR code column)
    for column in df_original.columns:
        if column != "Scan QR code":
            extracted_df[column] = df_original[column]
    
    # Optimize memory
    extracted_df = optimize_dataframe_memory(extracted_df)
    
    return extracted_df

@st.cache_data
def create_summary_data(df, group_columns, metrics=['ITN received', 'ITN given']):
    """Create optimized summary data with caching"""
    if df.empty:
        return pd.DataFrame()
    
    # Group and aggregate efficiently
    grouped_data = df.groupby(group_columns)[metrics].sum().reset_index()
    
    # Calculate difference
    if len(metrics) >= 2:
        grouped_data["Difference"] = grouped_data[metrics[0]] - grouped_data[metrics[1]]
        grouped_data["Efficiency (%)"] = (grouped_data[metrics[1]] / grouped_data[metrics[0]] * 100).round(2)
    
    return grouped_data

def create_interactive_chart(data, title, x_col, y_cols, chart_type="bar"):
    """Create interactive Plotly charts"""
    if data.empty:
        st.warning("No data available for visualization")
        return
    
    if chart_type == "bar":
        fig = go.Figure()
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        for i, col in enumerate(y_cols):
            fig.add_trace(go.Bar(
                name=col,
                x=data[x_col],
                y=data[col],
                marker_color=colors[i % len(colors)],
                text=data[col],
                textposition='auto',
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="",
            yaxis_title="Count",
            barmode='group',
            height=500,
            showlegend=True,
            hovermode='x unified'
        )
        
        fig.update_xaxes(tickangle=45)
        
    elif chart_type == "pie":
        fig = go.Figure(data=[go.Pie(
            labels=data[x_col],
            values=data[y_cols[0]],
            hole=0.3,
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig.update_layout(
            title=title,
            height=500
        )
    
    st.plotly_chart(fig, use_container_width=True)

# Initialize session state
if 'extracted_df' not in st.session_state:
    st.session_state.extracted_df = None
if 'original_df' not in st.session_state:
    st.session_state.original_df = None

# File upload section
st.markdown("""
<div class="upload-section">
    <h3>📁 Upload Your Excel File</h3>
    <p>Upload an Excel file containing QR code data for extraction and analysis</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose an Excel file",
    type=['xlsx', 'xls'],
    help="Upload Excel files with QR code data"
)

if uploaded_file is not None:
    with st.spinner("Loading and processing file..."):
        try:
            # Read Excel file
            df_original = pd.read_excel(uploaded_file)
            
            # Check for required column
            if "Scan QR code" not in df_original.columns:
                st.error("❌ File must contain a 'Scan QR code' column")
                st.stop()
            
            # Extract QR data
            extracted_df = extract_qr_data(df_original)
            
            # Store in session state
            st.session_state.original_df = df_original
            st.session_state.extracted_df = extracted_df
            
            st.success("✅ File processed successfully!")
            
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.stop()

# Main content when file is uploaded
if st.session_state.extracted_df is not None:
    df_original = st.session_state.original_df
    extracted_df = st.session_state.extracted_df
    
    # Show file statistics
    st.subheader("📊 File Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <h3>{len(extracted_df):,}</h3>
            <p>Total Records</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        valid_extractions = extracted_df['District'].notna().sum()
        st.markdown(f"""
        <div class="stats-card">
            <h3>{valid_extractions:,}</h3>
            <p>Valid Extractions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        extraction_rate = (valid_extractions / len(extracted_df) * 100) if len(extracted_df) > 0 else 0
        st.markdown(f"""
        <div class="stats-card">
            <h3>{extraction_rate:.1f}%</h3>
            <p>Extraction Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <h3>{get_memory_usage(extracted_df)}</h3>
            <p>Memory Usage</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Data preview section
    with st.expander("📄 View Data Samples", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Original Data (first 5 rows):**")
            st.dataframe(df_original.head(), use_container_width=True, height=200)
        
        with col2:
            st.markdown("**Extracted Data (first 5 rows):**")
            st.dataframe(extracted_df.head(), use_container_width=True, height=200)
    
    # Quick Summary Section
    st.subheader("⚡ Quick Summaries")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 District Summary", type="secondary"):
            st.session_state.show_district_summary = True
            st.session_state.show_chiefdom_summary = False
            st.session_state.show_detailed_analysis = False
    
    with col2:
        if st.button("🏘️ Chiefdom Summary", type="secondary"):
            st.session_state.show_chiefdom_summary = True
            st.session_state.show_district_summary = False
            st.session_state.show_detailed_analysis = False
    
    with col3:
        if st.button("🔍 Detailed Analysis", type="primary"):
            st.session_state.show_detailed_analysis = True
            st.session_state.show_district_summary = False
            st.session_state.show_chiefdom_summary = False
    
    # District Summary
    if st.session_state.get('show_district_summary', False):
        st.markdown("### 📈 District Summary")
        
        with st.spinner("Generating district summary..."):
            district_summary = create_summary_data(extracted_df, ["District"])
            
            if not district_summary.empty:
                st.markdown(f"""
                <div class="summary-card">
                    <strong>District Analysis</strong><br>
                    📊 Total Districts: {len(district_summary)}<br>
                    📈 Total ITN Received: {district_summary['ITN received'].sum():,}<br>
                    📉 Total ITN Given: {district_summary['ITN given'].sum():,}<br>
                    🎯 Overall Efficiency: {(district_summary['ITN given'].sum() / district_summary['ITN received'].sum() * 100):.1f}%
                </div>
                """, unsafe_allow_html=True)
                
                # Display table
                st.dataframe(district_summary, use_container_width=True, height=300)
                
                # Interactive chart
                create_interactive_chart(
                    district_summary, 
                    "📊 ITN Distribution by District",
                    "District", 
                    ["ITN received", "ITN given"]
                )
                
                # Download option
                csv_buffer = io.StringIO()
                district_summary.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📥 Download District Summary (CSV)",
                    data=csv_buffer.getvalue(),
                    file_name=f"district_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
    
    # Chiefdom Summary
    if st.session_state.get('show_chiefdom_summary', False):
        st.markdown("### 🏘️ Chiefdom Summary")
        
        with st.spinner("Generating chiefdom summary..."):
            chiefdom_summary = create_summary_data(extracted_df, ["District", "Chiefdom"])
            
            if not chiefdom_summary.empty:
                st.markdown(f"""
                <div class="summary-card">
                    <strong>Chiefdom Analysis</strong><br>
                    🏘️ Total Chiefdoms: {len(chiefdom_summary)}<br>
                    📈 Total ITN Received: {chiefdom_summary['ITN received'].sum():,}<br>
                    📉 Total ITN Given: {chiefdom_summary['ITN given'].sum():,}<br>
                    🎯 Overall Efficiency: {(chiefdom_summary['ITN given'].sum() / chiefdom_summary['ITN received'].sum() * 100):.1f}%
                </div>
                """, unsafe_allow_html=True)
                
                # Create display labels
                chiefdom_summary['Display_Label'] = chiefdom_summary['District'] + ' - ' + chiefdom_summary['Chiefdom']
                
                # Display table
                st.dataframe(chiefdom_summary.drop('Display_Label', axis=1), use_container_width=True, height=300)
                
                # Interactive chart
                create_interactive_chart(
                    chiefdom_summary, 
                    "📊 ITN Distribution by District and Chiefdom",
                    "Display_Label", 
                    ["ITN received", "ITN given"]
                )
                
                # Download option
                csv_buffer = io.StringIO()
                chiefdom_summary.drop('Display_Label', axis=1).to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📥 Download Chiefdom Summary (CSV)",
                    data=csv_buffer.getvalue(),
                    file_name=f"chiefdom_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
    
    # Detailed Analysis Section
    if st.session_state.get('show_detailed_analysis', False):
        st.markdown("### 🔍 Detailed Analysis & Filtering")
        
        # Sidebar for filtering
        with st.sidebar:
            st.header("🎛️ Filter Controls")
            
            # Grouping selection
            hierarchy = {
                "District": ["District"],
                "Chiefdom": ["District", "Chiefdom"],
                "PHU Name": ["District", "Chiefdom", "PHU Name"],
                "Community Name": ["District", "Chiefdom", "PHU Name", "Community Name"],
                "School Name": ["District", "Chiefdom", "PHU Name", "Community Name", "School Name"]
            }
            
            grouping_selection = st.radio(
                "📊 Select grouping level:",
                list(hierarchy.keys()),
                index=0
            )
            
            # Chart type selection
            chart_type = st.selectbox(
                "📈 Chart type:",
                ["Bar Chart", "Pie Chart"],
                index=0
            )
            
            # Metric selection
            available_metrics = ['ITN received', 'ITN given']
            numeric_cols = extracted_df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) > 2:
                available_metrics.extend([col for col in numeric_cols if col not in available_metrics])
            
            selected_metrics = st.multiselect(
                "📊 Select metrics:",
                available_metrics,
                default=['ITN received', 'ITN given']
            )
        
        # Apply hierarchical filtering
        filtered_df = extracted_df.copy()
        selected_values = {}
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("""
            <div class="filter-section">
                <h4>🎯 Apply Filters</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for level in hierarchy[grouping_selection]:
                level_values = sorted(filtered_df[level].dropna().unique())
                
                if level_values:
                    selected_value = st.selectbox(
                        f"📍 Select {level}:",
                        ["All"] + list(level_values),
                        key=f"filter_{level}"
                    )
                    
                    if selected_value != "All":
                        selected_values[level] = selected_value
                        filtered_df = filtered_df[filtered_df[level] == selected_value]
        
        with col2:
            if not filtered_df.empty and selected_metrics:
                # Create summary
                group_columns = hierarchy[grouping_selection]
                summary_data = create_summary_data(filtered_df, group_columns, selected_metrics)
                
                if not summary_data.empty:
                    # Display metrics
                    metrics_cols = st.columns(len(selected_metrics))
                    for i, metric in enumerate(selected_metrics):
                        with metrics_cols[i]:
                            total_value = summary_data[metric].sum()
                            st.metric(metric, f"{total_value:,}")
                    
                    # Display summary table
                    st.markdown("**📋 Summary Table:**")
                    st.dataframe(summary_data, use_container_width=True, height=250)
                    
                    # Create visualization
                    if len(summary_data) > 0:
                        # Create display column for chart
                        if len(group_columns) == 1:
                            display_col = group_columns[0]
                        else:
                            summary_data['Display'] = summary_data[group_columns].apply(
                                lambda row: ' - '.join(row.astype(str)), axis=1
                            )
                            display_col = 'Display'
                        
                        chart_type_map = {"Bar Chart": "bar", "Pie Chart": "pie"}
                        create_interactive_chart(
                            summary_data,
                            f"📊 {grouping_selection} Analysis",
                            display_col,
                            selected_metrics,
                            chart_type_map[chart_type]
                        )
                        
                        # Download filtered data
                        csv_buffer = io.StringIO()
                        filtered_df.to_csv(csv_buffer, index=False)
                        st.download_button(
                            label="📥 Download Filtered Data (CSV)",
                            data=csv_buffer.getvalue(),
                            file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.warning("No data available for the selected filters and metrics.")
            else:
                st.info("Apply filters and select metrics to view analysis.")
    
    # Reset button
    if st.button("🔄 Reset All Views", type="secondary"):
        for key in ['show_district_summary', 'show_chiefdom_summary', 'show_detailed_analysis']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Show features when no file is uploaded
else:
    st.subheader("✨ Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🚀 Advanced Processing:**
        - Optimized regex extraction
        - Memory-efficient data handling
        - Cached processing for speed
        - Error handling and validation
        
        **📊 Smart Analytics:**
        - Quick summary buttons
        - Interactive Plotly charts
        - Efficiency calculations
        - Real-time filtering
        """)
    
    with col2:
        st.markdown("""
        **🎯 Interactive Features:**
        - Hierarchical filtering system
        - Multiple chart types
        - Dynamic metric selection
        - Progressive data disclosure
        
        **💾 Export Options:**
        - CSV downloads for all views
        - Filtered data export
        - Summary reports
        - Timestamped filenames
        """)

# Footer
st.markdown("---")
current_memory = "N/A"
if st.session_state.extracted_df is not None:
    current_memory = get_memory_usage(st.session_state.extracted_df)

st.markdown(f"""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>📊 Built with Streamlit | Text Data Extraction & Visualization Tool | Memory Usage: {current_memory}</p>
</div>
""", unsafe_allow_html=True)
