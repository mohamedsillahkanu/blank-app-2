import streamlit as st
import pandas as pd
import re
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

# Custom CSS for styling with bright blue theme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling with bright sky blue */
    .header-container {
        background: linear-gradient(135deg, #00bfff 0%, #1e90ff 50%, #4169e1 100%);
        padding: 25px;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 8px 32px rgba(0, 191, 255, 0.3);
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .logo-placeholder {
        width: 90px;
        height: 90px;
        background: rgba(255,255,255,0.15);
        border: 2px dashed rgba(255,255,255,0.6);
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 11px;
        text-align: center;
        font-weight: 500;
        backdrop-filter: blur(10px);
    }
    
    .header-title {
        color: white;
        text-align: center;
        flex-grow: 1;
        margin: 0 30px;
    }
    
    .header-title h1 {
        margin: 0;
        font-size: 3em;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .header-title p {
        margin: 8px 0 0 0;
        font-size: 1.2em;
        opacity: 0.95;
        font-weight: 400;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fdff 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 191, 255, 0.1);
        border: 1px solid rgba(0, 191, 255, 0.1);
        text-align: center;
        transition: all 0.3s ease;
        margin: 10px 0;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 191, 255, 0.2);
    }
    
    .metric-number {
        font-size: 2.5em;
        font-weight: 700;
        color: #1e90ff;
        margin: 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 1.1em;
        color: #4a5568;
        margin: 8px 0 0 0;
        font-weight: 500;
    }
    
    .metric-icon {
        font-size: 2em;
        margin-bottom: 10px;
        color: #00bfff;
    }
    
    /* Overview cards */
    .overview-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 191, 255, 0.15);
        border: 1px solid rgba(0, 191, 255, 0.2);
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    
    .overview-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 50px rgba(0, 191, 255, 0.25);
    }
    
    .card-title {
        font-size: 1.5em;
        font-weight: 600;
        color: #1e90ff;
        margin: 0 0 15px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Footer styling */
    .footer-container {
        background: linear-gradient(135deg, #00bfff 0%, #1e90ff 50%, #4169e1 100%);
        padding: 30px;
        margin: 3rem -1rem -1rem -1rem;
        border-radius: 20px 20px 0 0;
        color: white;
        text-align: center;
    }
    
    .footer-content {
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .footer-links {
        margin: 15px 0;
    }
    
    .footer-links a {
        color: rgba(255,255,255,0.9);
        text-decoration: none;
        margin: 0 20px;
        transition: all 0.3s;
        font-weight: 500;
    }
    
    .footer-links a:hover {
        color: white;
        text-shadow: 0 0 10px rgba(255,255,255,0.5);
    }
    
    /* Main content styling */
    .main-content {
        min-height: 70vh;
        padding: 0 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #00bfff 0%, #1e90ff 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 15px 30px;
        transition: all 0.3s;
        font-weight: 600;
        font-size: 1em;
        box-shadow: 0 4px 15px rgba(0, 191, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 191, 255, 0.4);
        background: linear-gradient(135deg, #1e90ff 0%, #4169e1 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: white !important;
        border-right: 2px solid #e0f2fe;
    }
    
    .css-1d391kg .css-1cpxqw2 {
        background: white !important;
    }
    
    .css-1d391kg .stSelectbox > div > div {
        background: white;
        border: 2px solid #e0f2fe;
        border-radius: 10px;
    }
    
    .css-1d391kg .stRadio > div {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0f2fe;
    }
    
    .css-1d391kg .stRadio > div > label {
        color: #1e90ff;
        font-weight: 500;
    }
    
    .css-1d391kg h3 {
        color: #1e90ff;
        font-weight: 600;
        border-bottom: 2px solid #e0f2fe;
        padding-bottom: 10px;
    }
    
    /* Sidebar header styling */
    .css-1d391kg .css-1avcm0n {
        background: white !important;
        border-bottom: 2px solid #e0f2fe;
        padding: 20px 15px;
    }
    
    /* Sidebar content area */
    .css-1d391kg .css-1offfwp {
        background: white !important;
        padding: 20px 15px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #f0f9ff 0%, #e6f3ff 100%);
        border-radius: 10px;
        color: #1e90ff;
        font-weight: 600;
        border: 1px solid rgba(0, 191, 255, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00bfff 0%, #1e90ff 100%);
        color: white;
    }
    
    /* Data frame styling */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 191, 255, 0.1);
    }
    
    /* Success/Info messages */
    .stSuccess {
        background: linear-gradient(135deg, #00ff9f 0%, #00bcd4 100%);
        border-radius: 10px;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #00bfff 0%, #87ceeb 100%);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("""
<div class="header-container">
    <div class="header-content">
        <div class="logo-placeholder">
            <div>
                LEFT<br>LOGO<br>HERE
            </div>
        </div>
        <div class="header-title">
            <h1>📊 ITN Data Analysis Dashboard</h1>
            <p>Interactive Text Data Extraction & Visualization System</p>
        </div>
        <div class="logo-placeholder">
            <div>
                RIGHT<br>LOGO<br>HERE
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main content wrapper
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# File upload section
st.markdown("""
<div class="overview-card">
    <div class="card-title">📁 Data Upload & Processing</div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])

# If no file is uploaded, use the default file
if not uploaded_file:
    uploaded_file = "GMB253374_sbd_1740943126553_submissions.xlsx"
    st.info("🔄 Using default file: GMB253374_sbd_1740943126553_submissions.xlsx")

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
            if column != "Scan QR code":
                extracted_df[column] = df_original[column]
        
        # Display success message
        st.success(f"✅ Successfully processed {len(extracted_df)} records!")
        
        # Overview Cards Section
        st.markdown("""
        <div class="overview-card">
            <div class="card-title">📊 Data Overview</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create metric cards
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📄</div>
                <div class="metric-number">{len(extracted_df)}</div>
                <div class="metric-label">Total Records</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🏛️</div>
                <div class="metric-number">{extracted_df['District'].nunique()}</div>
                <div class="metric-label">Districts</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🏘️</div>
                <div class="metric-number">{extracted_df['Chiefdom'].nunique()}</div>
                <div class="metric-label">Chiefdoms</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_received = extracted_df['ITN received'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📥</div>
                <div class="metric-number">{total_received:,}</div>
                <div class="metric-label">ITN Received</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            total_given = extracted_df['ITN given'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📤</div>
                <div class="metric-number">{total_given:,}</div>
                <div class="metric-label">ITN Given</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Create tabs for better organization
        tab1, tab2, tab3, tab4 = st.tabs(["📄 Data Preview", "📊 Interactive Summaries", "🔍 Detailed Analysis", "📈 Export Data"])
        
        with tab1:
            st.markdown("""
            <div class="overview-card">
                <div class="card-title">📄 Original Data Sample</div>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(df_original.head(), height=300, use_container_width=True)
            
            st.markdown("""
            <div class="overview-card">
                <div class="card-title">📋 Extracted Data Preview</div>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(extracted_df.head(), height=300, use_container_width=True)
        
        with tab2:
            st.markdown("""
            <div class="overview-card">
                <div class="card-title">📊 Interactive Summary Reports</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Create two columns for the summary buttons
            col1, col2 = st.columns(2)
            
            with col1:
                district_summary_button = st.button("🏛️ Show District Summary", key="district_btn")
            
            with col2:
                chiefdom_summary_button = st.button("🏘️ Show Chiefdom Summary", key="chiefdom_btn")
            
            # Display District Summary when button is clicked
            if district_summary_button:
                st.markdown("""
                <div class="overview-card">
                    <div class="card-title">📈 Summary by District</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Group by District and aggregate
                district_summary = extracted_df.groupby("District").agg({
                    "ITN received": "sum",
                    "ITN given": "sum"
                }).reset_index()
                
                # Calculate difference
                district_summary["Difference"] = district_summary["ITN received"] - district_summary["ITN given"]
                
                # Display summary table
                st.dataframe(district_summary, use_container_width=True)
                
                # Create interactive bar chart
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='ITN Received',
                    x=district_summary['District'],
                    y=district_summary['ITN received'],
                    marker_color='#00bfff',
                    hovertemplate='<b>%{x}</b><br>ITN Received: %{y}<extra></extra>'
                ))
                
                fig.add_trace(go.Bar(
                    name='ITN Given',
                    x=district_summary['District'],
                    y=district_summary['ITN given'],
                    marker_color='#ff6b35',
                    hovertemplate='<b>%{x}</b><br>ITN Given: %{y}<extra></extra>'
                ))
                
                fig.update_layout(
                    title={
                        'text': '📊 ITN Received vs. ITN Given by District',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 20, 'color': '#1e90ff'}
                    },
                    xaxis_title="District",
                    yaxis_title="Count",
                    barmode='group',
                    template='plotly_white',
                    height=500,
                    font=dict(family='Inter, sans-serif'),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add a pie chart for distribution
                fig_pie = px.pie(
                    district_summary, 
                    values='ITN received', 
                    names='District',
                    title='🥧 Distribution of ITN Received by District',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                
                fig_pie.update_layout(
                    title={
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 18, 'color': '#1e90ff'}
                    },
                    font=dict(family='Inter, sans-serif')
                )
                
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Display Chiefdom Summary when button is clicked
            if chiefdom_summary_button:
                st.markdown("""
                <div class="overview-card">
                    <div class="card-title">📈 Summary by Chiefdom</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Group by District and Chiefdom and aggregate
                chiefdom_summary = extracted_df.groupby(["District", "Chiefdom"]).agg({
                    "ITN received": "sum",
                    "ITN given": "sum"
                }).reset_index()
                
                # Calculate difference
                chiefdom_summary["Difference"] = chiefdom_summary["ITN received"] - chiefdom_summary["ITN given"]
                
                # Display summary table
                st.dataframe(chiefdom_summary, use_container_width=True)
                
                # Create a combined label for better visualization
                chiefdom_summary['Label'] = chiefdom_summary['District'] + ' - ' + chiefdom_summary['Chiefdom']
                
                # Create interactive grouped bar chart
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='ITN Received',
                    x=chiefdom_summary['Label'],
                    y=chiefdom_summary['ITN received'],
                    marker_color='#00bfff',
                    hovertemplate='<b>%{x}</b><br>ITN Received: %{y}<extra></extra>'
                ))
                
                fig.add_trace(go.Bar(
                    name='ITN Given',
                    x=chiefdom_summary['Label'],
                    y=chiefdom_summary['ITN given'],
                    marker_color='#ff6b35',
                    hovertemplate='<b>%{x}</b><br>ITN Given: %{y}<extra></extra>'
                ))
                
                fig.update_layout(
                    title={
                        'text': '📊 ITN Received vs. ITN Given by District and Chiefdom',
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 20, 'color': '#1e90ff'}
                    },
                    xaxis_title="District - Chiefdom",
                    yaxis_title="Count",
                    barmode='group',
                    template='plotly_white',
                    height=600,
                    font=dict(family='Inter, sans-serif'),
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add a treemap for hierarchical view
                fig_tree = px.treemap(
                    chiefdom_summary,
                    path=['District', 'Chiefdom'],
                    values='ITN received',
                    title='🌳 Hierarchical View of ITN Distribution',
                    color='ITN received',
                    color_continuous_scale='Blues'
                )
                
                fig_tree.update_layout(
                    title={
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 18, 'color': '#1e90ff'}
                    },
                    font=dict(family='Inter, sans-serif')
                )
                
                st.plotly_chart(fig_tree, use_container_width=True)
        
        with tab3:
            st.markdown("""
            <div class="overview-card">
                <div class="card-title">🔍 Detailed Data Filtering and Visualization</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Create a sidebar for filtering options
            st.sidebar.markdown("### 🎛️ Filter Options")
            
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
                
                # Create interactive visualization
                fig = px.bar(
                    grouped_data,
                    x='Group',
                    y=['ITN received', 'ITN given'],
                    title=f'📊 Interactive Analysis by {grouping_selection}',
                    color_discrete_map={
                        'ITN received': '#00bfff',
                        'ITN given': '#ff6b35'
                    },
                    barmode='group'
                )
                
                fig.update_layout(
                    title={
                        'x': 0.5,
                        'xanchor': 'center',
                        'font': {'size': 18, 'color': '#1e90ff'}
                    },
                    xaxis_title="",
                    yaxis_title="Count",
                    template='plotly_white',
                    height=500,
                    font=dict(family='Inter, sans-serif'),
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add scatter plot for correlation analysis
                if len(grouped_data) > 1:
                    fig_scatter = px.scatter(
                        grouped_data,
                        x='ITN received',
                        y='ITN given',
                        size='Difference',
                        hover_name='Group',
                        title='🔍 Correlation: ITN Received vs ITN Given',
                        color='Difference',
                        color_continuous_scale='RdYlBu'
                    )
                    
                    fig_scatter.update_layout(
                        title={
                            'x': 0.5,
                            'xanchor': 'center',
                            'font': {'size': 18, 'color': '#1e90ff'}
                        },
                        template='plotly_white',
                        font=dict(family='Inter, sans-serif')
                    )
                    
                    st.plotly_chart(fig_scatter, use_container_width=True)
        
        with tab4:
            st.markdown("""
            <div class="overview-card">
                <div class="card-title">📈 Export Data</div>
            </div>
            """, unsafe_allow_html=True)
            
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
        <p>© 2025 Informatics Consultancy Firm- Sierra Leone. All rights reserved.</p>
        <p>Powered by Streamlit & Plotly | Interactive Data Analytics Platform</p>
    </div>
</div>
""", unsafe_allow_html=True)
