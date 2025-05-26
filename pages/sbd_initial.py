import streamlit as st
import pandas as pd
import re
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page config with blue theme
st.set_page_config(
    page_title="Text Data Extraction & Visualization",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for blue theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    
    .summary-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2196f3;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .filter-section {
        background: linear-gradient(135deg, #f8fbff 0%, #e8f4fd 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #2196f3;
        margin: 1rem 0;
    }
    
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #e3f2fd 0%, #bbdefb 100%);
    }
    
    .sidebar-header {
        background: #2196f3;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>📊 Text Data Extraction & Visualization</h1>
    <p>Interactive data analysis with dynamic filtering and visualization</p>
</div>
""", unsafe_allow_html=True)

# Upload file
uploaded_file = st.file_uploader(
    "📁 Choose an Excel file", 
    type=['xlsx', 'xls'],
    help="Upload your Excel file containing QR code data"
)

# For demo purposes, you can set a default file
# uploaded_file = "GMB253374_sbd_1740943126553_submissions.xlsx"

if uploaded_file:
    try:
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
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_records = len(extracted_df)
            st.markdown(f"""
            <div class="metric-card">
                <h3>{total_records:,}</h3>
                <p>Total Records</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_received = extracted_df['ITN received'].sum() if 'ITN received' in extracted_df.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3>{total_received:,}</h3>
                <p>Total ITN Received</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_given = extracted_df['ITN given'].sum() if 'ITN given' in extracted_df.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3>{total_given:,}</h3>
                <p>Total ITN Given</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            difference = total_received - total_given
            st.markdown(f"""
            <div class="metric-card">
                <h3>{difference:,}</h3>
                <p>Difference</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Data display section
        st.markdown("---")
        
        # Tabs for data display
        tab1, tab2 = st.tabs(["📄 Original Data", "📋 Extracted Data"])
        
        with tab1:
            st.markdown("**Original Data Sample (First 10 rows)**")
            st.dataframe(df_original.head(10), use_container_width=True)
        
        with tab2:
            st.markdown("**Extracted and Processed Data**")
            st.dataframe(extracted_df.head(10), use_container_width=True)
        
        # Summary Reports Section
        st.markdown("---")
        st.markdown("""
        <div class="summary-card">
            <h3>📊 Interactive Summary Reports</h3>
            <p>Click the buttons below to generate interactive visualizations and summaries</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create columns for summary buttons
        col1, col2 = st.columns(2)
        
        # Button for District Summary
        with col1:
            district_summary_button = st.button("🏙️ Show District Summary", use_container_width=True)
        
        # Button for Chiefdom Summary
        with col2:
            chiefdom_summary_button = st.button("🏘️ Show Chiefdom Summary", use_container_width=True)
        
        # Display District Summary when button is clicked
        if district_summary_button:
            st.markdown("---")
            st.subheader("🏙️ Summary by District")
            
            # Group by District and aggregate
            district_summary = extracted_df.groupby("District").agg({
                "ITN received": "sum",
                "ITN given": "sum"
            }).reset_index()
            
            # Calculate difference
            district_summary["Difference"] = district_summary["ITN received"] - district_summary["ITN given"]
            
            # Display summary table
            st.markdown("**📋 District Summary Table**")
            st.dataframe(district_summary, use_container_width=True)
            
            # Create interactive visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Interactive bar chart
                fig_bar = px.bar(
                    district_summary,
                    x="District",
                    y=["ITN received", "ITN given"],
                    title="📊 ITN Received vs Given by District",
                    color_discrete_sequence=["#2196f3", "#ff9800"],
                    barmode="group"
                )
                fig_bar.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#1976d2"),
                    title_font_size=16,
                    xaxis_title="District",
                    yaxis_title="Count"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # Interactive pie chart for ITN received
                fig_pie = px.pie(
                    district_summary,
                    values="ITN received",
                    names="District",
                    title="🥧 ITN Received Distribution by District",
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig_pie.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#1976d2"),
                    title_font_size=16
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Additional pie chart for ITN given
            col3, col4 = st.columns(2)
            
            with col3:
                # Pie chart for ITN given
                fig_pie_given = px.pie(
                    district_summary,
                    values="ITN given",
                    names="District",
                    title="🥧 ITN Given Distribution by District",
                    color_discrete_sequence=px.colors.sequential.Oranges_r
                )
                fig_pie_given.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#1976d2"),
                    title_font_size=16
                )
                st.plotly_chart(fig_pie_given, use_container_width=True)
            
            with col4:
                # Line chart showing difference
                fig_line = px.line(
                    district_summary,
                    x="District",
                    y="Difference",
                    title="📈 Difference (Received - Given) by District",
                    markers=True,
                    color_discrete_sequence=["#4caf50"]
                )
                fig_line.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#1976d2"),
                    title_font_size=16,
                    xaxis_title="District",
                    yaxis_title="Difference"
                )
                st.plotly_chart(fig_line, use_container_width=True)
        
        # Display Chiefdom Summary when button is clicked
        if chiefdom_summary_button:
            st.markdown("---")
            st.subheader("🏘️ Summary by Chiefdom")
            
            # Group by District and Chiefdom and aggregate
            chiefdom_summary = extracted_df.groupby(["District", "Chiefdom"]).agg({
                "ITN received": "sum",
                "ITN given": "sum"
            }).reset_index()
            
            # Calculate difference
            chiefdom_summary["Difference"] = chiefdom_summary["ITN received"] - chiefdom_summary["ITN given"]
            
            # Create a combined label for better visualization
            chiefdom_summary['Combined_Label'] = chiefdom_summary['District'] + ' - ' + chiefdom_summary['Chiefdom']
            
            # Display summary table
            st.markdown("**📋 Chiefdom Summary Table**")
            st.dataframe(chiefdom_summary.drop('Combined_Label', axis=1), use_container_width=True)
            
            # Create interactive visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Interactive bar chart
                fig_bar_chief = px.bar(
                    chiefdom_summary,
                    x="Combined_Label",
                    y=["ITN received", "ITN given"],
                    title="📊 ITN Received vs Given by District-Chiefdom",
                    color_discrete_sequence=["#2196f3", "#ff9800"],
                    barmode="group"
                )
                fig_bar_chief.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#1976d2"),
                    title_font_size=16,
                    xaxis_title="District - Chiefdom",
                    yaxis_title="Count",
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig_bar_chief, use_container_width=True)
            
            with col2:
                # Interactive pie chart for ITN received by chiefdom
                fig_pie_chief = px.pie(
                    chiefdom_summary,
                    values="ITN received",
                    names="Combined_Label",
                    title="🥧 ITN Received Distribution by Chiefdom",
                    color_discrete_sequence=px.colors.sequential.Blues_r
                )
                fig_pie_chief.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#1976d2"),
                    title_font_size=16
                )
                st.plotly_chart(fig_pie_chief, use_container_width=True)
        
        # Advanced Filtering Section
        st.markdown("---")
        st.markdown("""
        <div class="filter-section">
            <h3>🔍 Advanced Data Filtering and Visualization</h3>
            <p>Use the sidebar filters to drill down into specific data segments</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar for filtering options
        with st.sidebar:
            st.markdown("""
            <div class="sidebar-header">
                🎛️ Filter Options
            </div>
            """, unsafe_allow_html=True)
            
            # Create radio buttons to select which level to group by
            grouping_selection = st.radio(
                "📊 Select grouping level:",
                ["District", "Chiefdom", "PHU Name", "Community Name", "School Name"],
                index=0,
                help="Choose the hierarchical level for data analysis"
            )
            
            st.markdown("---")
            st.markdown("### 🎯 Hierarchical Filters")
        
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
                    selected_value = st.selectbox(
                        f"🎯 Select {level}",
                        level_values,
                        help=f"Choose a specific {level.lower()} to filter the data"
                    )
                    selected_values[level] = selected_value
                    
                    # Apply filter to the dataframe
                    filtered_df = filtered_df[filtered_df[level] == selected_value]
        
        # Check if data is available after filtering
        if filtered_df.empty:
            st.warning("⚠️ No data available for the selected filters.")
        else:
            # Display filtered results
            st.markdown(f"### 📊 Filtered Results - {len(filtered_df):,} records")
            
            # Show filtered data
            with st.expander("📋 View Filtered Data", expanded=False):
                st.dataframe(filtered_df, use_container_width=True)
            
            # Define the hierarchy levels to include in the summary
            group_columns = hierarchy[grouping_selection]
            
            # Group by the selected hierarchical columns
            if len(filtered_df) > 0:
                grouped_data = filtered_df.groupby(group_columns).agg({
                    "ITN received": "sum",
                    "ITN given": "sum"
                }).reset_index()
                
                # Add difference column
                grouped_data["Difference"] = grouped_data["ITN received"] - grouped_data["ITN given"]
                
                # Create a temporary group column for visualization
                grouped_data['Group_Label'] = grouped_data[group_columns].apply(
                    lambda row: ' - '.join(row.astype(str)), axis=1
                )
                
                # Display summary table
                st.markdown("### 📊 Detailed Summary Table")
                st.dataframe(grouped_data.drop('Group_Label', axis=1), use_container_width=True)
                
                # Create interactive visualizations for filtered data
                if len(grouped_data) > 0:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Interactive bar chart for filtered data
                        fig_filtered_bar = px.bar(
                            grouped_data,
                            x="Group_Label",
                            y=["ITN received", "ITN given"],
                            title=f"📊 ITN Analysis - {grouping_selection} Level",
                            color_discrete_sequence=["#2196f3", "#ff9800"],
                            barmode="group"
                        )
                        fig_filtered_bar.update_layout(
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            font=dict(color="#1976d2"),
                            title_font_size=16,
                            xaxis_title="",
                            yaxis_title="Count",
                            xaxis_tickangle=-45
                        )
                        st.plotly_chart(fig_filtered_bar, use_container_width=True)
                    
                    with col2:
                        # Interactive pie chart for filtered data
                        if len(grouped_data) > 1:  # Only show pie chart if there are multiple groups
                            fig_filtered_pie = px.pie(
                                grouped_data,
                                values="ITN received",
                                names="Group_Label",
                                title=f"🥧 ITN Received Distribution - {grouping_selection}",
                                color_discrete_sequence=px.colors.sequential.Blues_r
                            )
                            fig_filtered_pie.update_layout(
                                plot_bgcolor="rgba(0,0,0,0)",
                                paper_bgcolor="rgba(0,0,0,0)",
                                font=dict(color="#1976d2"),
                                title_font_size=16
                            )
                            st.plotly_chart(fig_filtered_pie, use_container_width=True)
                        else:
                            # Show metrics instead of pie chart for single group
                            st.markdown("### 📈 Key Metrics")
                            met_col1, met_col2, met_col3 = st.columns(3)
                            
                            with met_col1:
                                st.metric("ITN Received", f"{grouped_data['ITN received'].iloc[0]:,}")
                            with met_col2:
                                st.metric("ITN Given", f"{grouped_data['ITN given'].iloc[0]:,}")
                            with met_col3:
                                st.metric("Difference", f"{grouped_data['Difference'].iloc[0]:,}")
                    
                    # Additional visualization: Difference analysis
                    if len(grouped_data) > 1:
                        st.markdown("### 📈 Difference Analysis")
                        
                        fig_diff = px.scatter(
                            grouped_data,
                            x="ITN received",
                            y="ITN given",
                            size="Difference",
                            hover_name="Group_Label",
                            title="📈 ITN Received vs Given Correlation",
                            color="Difference",
                            color_continuous_scale="RdYlBu"
                        )
                        fig_diff.update_layout(
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            font=dict(color="#1976d2"),
                            title_font_size=16
                        )
                        st.plotly_chart(fig_diff, use_container_width=True)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            <p>📊 Interactive Text Data Extraction & Visualization Tool | Built with Streamlit & Plotly</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("💡 Please ensure your Excel file contains a 'Scan QR code' column with the expected data format.")

else:
    # Instructions when no file is uploaded
    st.markdown("""
    <div class="summary-card">
        <h3>📁 Getting Started</h3>
        <p><strong>Upload an Excel file to begin:</strong></p>
        <ul>
            <li>📄 File should contain a "Scan QR code" column</li>
            <li>🏷️ QR code data should include District, Chiefdom, PHU name, Community name, and School name</li>
            <li>📊 ITN received and ITN given columns for analysis</li>
        </ul>
        <p><strong>Features:</strong></p>
        <ul>
            <li>🔍 Interactive data filtering and visualization</li>
            <li>📊 Multiple chart types: Bar charts, Pie charts, Line charts, Scatter plots</li>
            <li>🎯 Hierarchical filtering from District to School level</li>
            <li>💙 Beautiful blue-themed interface</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
