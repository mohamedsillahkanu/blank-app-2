import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configure page
st.set_page_config(
    page_title="ITN Data Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set up matplotlib and seaborn styling
plt.style.use('default')
sns.set_palette("husl")

# Custom CSS for enhanced blue theme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main theme colors */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #667eea 100%);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .header-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='4'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        opacity: 0.3;
    }
    
    .header-title {
        color: white;
        text-align: center;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .header-subtitle {
        color: #e8f4fd;
        text-align: center;
        font-size: 1.3rem;
        margin-top: 10px;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    /* Logo styling */
    .logo-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        position: relative;
        z-index: 1;
    }
    
    .logo-placeholder {
        width: 140px;
        height: 100px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        transition: transform 0.3s ease;
        border: 2px solid rgba(255,255,255,0.2);
    }
    
    .logo-placeholder:hover {
        transform: translateY(-5px);
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 20px 25px;
        border-radius: 15px;
        margin: 25px 0 20px 0;
        font-size: 1.4rem;
        font-weight: 600;
        box-shadow: 0 4px 20px rgba(79, 172, 254, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .section-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .section-header:hover::before {
        left: 100%;
    }
    
    /* Enhanced Cards styling */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid rgba(79, 172, 254, 0.1);
        margin: 15px 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #4facfe 0%, #667eea 100%);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    /* Enhanced Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 15px 30px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        background: rgba(255,255,255,0.2);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Enhanced DataFrame styling */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid rgba(79, 172, 254, 0.1);
    }
    
    /* Chart container */
    .chart-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 20px 0;
        border: 1px solid rgba(79, 172, 254, 0.1);
    }
    
    /* Stats container */
    .stats-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    /* Enhanced alerts */
    .stAlert {
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Plotly chart styling */
    .js-plotly-plot {
        border-radius: 15px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Header with logos
st.markdown("""
<div class="header-container">
    <div class="logo-container">
        <div class="logo-placeholder">
            🏢<br>ORG LOGO<br>PLACEHOLDER
        </div>
        <div>
            <h1 class="header-title">📊 ITN Data Analytics Dashboard</h1>
            <p class="header-subtitle">Advanced Text Data Extraction & Visualization Platform</p>
        </div>
        <div class="logo-placeholder">
            🏛️<br>PARTNER<br>LOGO
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# File upload section
st.markdown('<div class="section-header">📁 Data Upload & Processing</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Choose your Excel file", 
    type=['xlsx', 'xls'],
    help="Upload your Excel file containing QR code data"
)

# For demo purposes, use the hardcoded file if no file is uploaded
if uploaded_file is None:
    uploaded_file = "Report_GMB253374_SBD_1749318384635_submissions.xlsx"
    st.info("📝 Using default file: Report_GMB253374_SBD_1749318384635_submissions.xlsx")

if uploaded_file:
    try:
        # Read the uploaded Excel file
        if isinstance(uploaded_file, str):
            df_original = pd.read_excel(uploaded_file)
        else:
            df_original = pd.read_excel(uploaded_file)
        
        st.success(f"✅ Successfully loaded {len(df_original)} records from Excel file")
        
        # Display column information
        st.markdown("**📋 Available Columns:**")
        cols_info = ", ".join([f"`{col}`" for col in df_original.columns])
        st.markdown(f"<div style='background: #f0f2f6; padding: 10px; border-radius: 10px; font-family: monospace;'>{cols_info}</div>", unsafe_allow_html=True)
        
        # Check if required columns exist
        required_columns = ["Scan QR code"]
        missing_cols = [col for col in required_columns if col not in df_original.columns]
        
        if missing_cols:
            st.error(f"❌ Missing required columns: {missing_cols}")
            st.stop()
        
        # Create empty lists to store extracted data
        districts, chiefdoms, phu_names, community_names, school_names = [], [], [], [], []
        
        # Process each row in the "Scan QR code" column
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, qr_text in enumerate(df_original["Scan QR code"]):
            progress_bar.progress((i + 1) / len(df_original))
            status_text.text(f'Processing record {i + 1} of {len(df_original)}')
            
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
        
        progress_bar.empty()
        status_text.empty()
        
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
        
        # Identify numeric columns for aggregation
        numeric_columns = extracted_df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Specific enrollment columns
        enrollment_columns = [col for col in extracted_df.columns if 'enrollment' in col.lower()]
        boys_columns = [col for col in extracted_df.columns if 'boys' in col.lower()]
        girls_columns = [col for col in extracted_df.columns if 'girls' in col.lower()]
        class_columns = [col for col in extracted_df.columns if 'class' in col.lower()]
        
        # Create class-wise mapping
        class_data = {}
        for i in range(1, 6):  # Classes 1-5
            class_data[f'Class {i}'] = {
                'total': f'Number of enrollments in class {i}',
                'boys': f'Number of boys in class {i}',
                'girls': f'Number of girls in class {i}'
            }
        
        st.markdown(f"**🔢 Found {len(numeric_columns)} numeric columns:** {', '.join([f'`{col}`' for col in numeric_columns[:5]])}{'...' if len(numeric_columns) > 5 else ''}")
        
        if enrollment_columns:
            st.success(f"📚 **Educational Data Detected**: {len(enrollment_columns)} enrollment columns across {len([c for c in class_columns if 'enrollment' in c])} classes")
        
        # Data Overview Section
        st.markdown('<div class="section-header">📊 Data Overview & Key Metrics</div>', unsafe_allow_html=True)
        
        # Create metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #667eea; margin: 0; font-size: 1.1rem;">📝 Total Records</h3>
                <h2 style="color: #333; margin: 5px 0; font-size: 2.2rem;">{:,}</h2>
                <p style="color: #666; margin: 0; font-size: 0.9rem;">Data points processed</p>
            </div>
            """.format(len(extracted_df)), unsafe_allow_html=True)
        
        with col2:
            if enrollment_columns:
                total_enrollment = sum([extracted_df[col].sum() for col in enrollment_columns if col in extracted_df.columns])
                st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0; font-size: 1.1rem;">📚 Total Enrollment</h3>
                    <h2 style="color: #333; margin: 5px 0; font-size: 2.2rem;">{:,}</h2>
                    <p style="color: #666; margin: 0; font-size: 0.9rem;">Students across all classes</p>
                </div>
                """.format(int(total_enrollment)), unsafe_allow_html=True)
            else:
                unique_districts = extracted_df["District"].nunique()
                st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0; font-size: 1.1rem;">🌍 Districts</h3>
                    <h2 style="color: #333; margin: 5px 0; font-size: 2.2rem;">{}</h2>
                    <p style="color: #666; margin: 0; font-size: 0.9rem;">Unique districts</p>
                </div>
                """.format(unique_districts), unsafe_allow_html=True)
        
        with col3:
            if boys_columns and girls_columns:
                total_boys = sum([extracted_df[col].sum() for col in boys_columns if col in extracted_df.columns])
                total_girls = sum([extracted_df[col].sum() for col in girls_columns if col in extracted_df.columns])
                gender_ratio = (total_girls / total_boys * 100) if total_boys > 0 else 0
                st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0; font-size: 1.1rem;">⚖️ Gender Ratio</h3>
                    <h2 style="color: #333; margin: 5px 0; font-size: 2.2rem;">{:.1f}%</h2>
                    <p style="color: #666; margin: 0; font-size: 0.9rem;">Girls to boys ratio</p>
                </div>
                """.format(gender_ratio), unsafe_allow_html=True)
            else:
                unique_chiefdoms = extracted_df["Chiefdom"].nunique()
                st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0; font-size: 1.1rem;">🏘️ Chiefdoms</h3>
                    <h2 style="color: #333; margin: 5px 0; font-size: 2.2rem;">{}</h2>
                    <p style="color: #666; margin: 0; font-size: 0.9rem;">Unique chiefdoms</p>
                </div>
                """.format(unique_chiefdoms), unsafe_allow_html=True)
        
        with col4:
            if boys_columns and girls_columns:
                total_boys = sum([extracted_df[col].sum() for col in boys_columns if col in extracted_df.columns])
                total_girls = sum([extracted_df[col].sum() for col in girls_columns if col in extracted_df.columns])
                st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0; font-size: 1.1rem;">👥 Students</h3>
                    <h2 style="color: #333; margin: 5px 0; font-size: 1.8rem;">♂️{:,} ♀️{:,}</h2>
                    <p style="color: #666; margin: 0; font-size: 0.9rem;">Boys & Girls</p>
                </div>
                """.format(int(total_boys), int(total_girls)), unsafe_allow_html=True)
            elif numeric_columns:
                total_sum = extracted_df[numeric_columns].sum().sum()
                st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0; font-size: 1.1rem;">📊 Total Count</h3>
                    <h2 style="color: #333; margin: 5px 0; font-size: 2.2rem;">{:,}</h2>
                    <p style="color: #666; margin: 0; font-size: 0.9rem;">All numeric values</p>
                </div>
                """.format(int(total_sum)), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card">
                    <h3 style="color: #667eea; margin: 0; font-size: 1.1rem;">📊 Data Quality</h3>
                    <h2 style="color: #28a745; margin: 5px 0; font-size: 2.2rem;">✓</h2>
                    <p style="color: #666; margin: 0; font-size: 0.9rem;">Processing complete</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Enhanced Data Visualization Section
        st.markdown('<div class="section-header">📈 Interactive Data Visualizations</div>', unsafe_allow_html=True)
        
        # Create tabs for different visualizations
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🌍 Geographic Analysis", "📚 Educational Analysis", "📊 Statistical Overview", "🔍 Detailed Filtering", "📋 Data Tables"])
        
        with tab1:
            st.markdown("### 🗺️ Geographic Distribution Analysis")
            
            if not extracted_df["District"].isna().all():
                # District distribution
                district_counts = extracted_df["District"].value_counts()
                
                # Create interactive plotly chart
                fig_district = px.bar(
                    x=district_counts.index,
                    y=district_counts.values,
                    title="Distribution of Records by District",
                    labels={'x': 'District', 'y': 'Number of Records'},
                    color=district_counts.values,
                    color_continuous_scale='Blues'
                )
                fig_district.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter, sans-serif"),
                    title_font_size=18,
                    showlegend=False
                )
                st.plotly_chart(fig_district, use_container_width=True)
                
                # Chiefdom distribution
                if not extracted_df["Chiefdom"].isna().all():
                    chiefdom_counts = extracted_df.groupby(["District", "Chiefdom"]).size().reset_index(name='Count')
                    
                    fig_chiefdom = px.treemap(
                        chiefdom_counts,
                        path=['District', 'Chiefdom'],
                        values='Count',
                        title="Hierarchical View: Districts and Chiefdoms",
                        color='Count',
                        color_continuous_scale='Blues'
                    )
                    fig_chiefdom.update_layout(
                        font=dict(family="Inter, sans-serif"),
                        title_font_size=18
                    )
                    st.plotly_chart(fig_chiefdom, use_container_width=True)
            else:
                st.info("🔍 No geographic data available for visualization")
        
        with tab2:
            st.markdown("### 📚 Educational Data Analysis")
            
            if enrollment_columns or boys_columns or girls_columns:
                # Class-wise enrollment analysis
                st.markdown("#### 🎓 Class-wise Enrollment Overview")
                
                # Create class-wise summary
                class_summary = []
                for class_num in range(1, 6):
                    enrollment_col = f'Number of enrollments in class {class_num}'
                    boys_col = f'Number of boys in class {class_num}'
                    girls_col = f'Number of girls in class {class_num}'
                    
                    if enrollment_col in extracted_df.columns:
                        total_enrollment = extracted_df[enrollment_col].sum()
                        boys_count = extracted_df[boys_col].sum() if boys_col in extracted_df.columns else 0
                        girls_count = extracted_df[girls_col].sum() if girls_col in extracted_df.columns else 0
                        
                        class_summary.append({
                            'Class': f'Class {class_num}',
                            'Total Enrollment': int(total_enrollment),
                            'Boys': int(boys_count),
                            'Girls': int(girls_count),
                            'Gender Ratio (G/B)': round(girls_count/boys_count, 2) if boys_count > 0 else 0
                        })
                
                if class_summary:
                    class_df = pd.DataFrame(class_summary)
                    
                    # Display class summary table
                    st.dataframe(class_df, use_container_width=True)
                    
                    # Create visualizations
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Enrollment by class
                        fig_enrollment = px.bar(
                            class_df,
                            x='Class',
                            y='Total Enrollment',
                            title='Total Enrollment by Class',
                            color='Total Enrollment',
                            color_continuous_scale='Blues',
                            text='Total Enrollment'
                        )
                        fig_enrollment.update_traces(texttemplate='%{text}', textposition='outside')
                        fig_enrollment.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(family="Inter, sans-serif"),
                            showlegend=False
                        )
                        st.plotly_chart(fig_enrollment, use_container_width=True)
                    
                    with col2:
                        # Gender distribution
                        fig_gender = px.bar(
                            class_df,
                            x='Class',
                            y=['Boys', 'Girls'],
                            title='Gender Distribution by Class',
                            color_discrete_sequence=['#4facfe', '#ff6b9d'],
                            barmode='group'
                        )
                        fig_gender.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(family="Inter, sans-serif")
                        )
                        st.plotly_chart(fig_gender, use_container_width=True)
                    
                    # Advanced educational analysis
                    st.markdown("#### 📈 Educational Insights")
                    
                    # Overall statistics
                    total_students = class_df['Total Enrollment'].sum()
                    total_boys = class_df['Boys'].sum()
                    total_girls = class_df['Girls'].sum()
                    overall_ratio = total_girls / total_boys if total_boys > 0 else 0
                    
                    # Create metrics
                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                    
                    with metric_col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="color: #667eea; margin: 0;">👥 Total Students</h4>
                            <h3 style="color: #333; margin: 5px 0;">{total_students:,}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with metric_col2:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="color: #667eea; margin: 0;">♂️ Total Boys</h4>
                            <h3 style="color: #333; margin: 5px 0;">{total_boys:,}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with metric_col3:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="color: #667eea; margin: 0;">♀️ Total Girls</h4>
                            <h3 style="color: #333; margin: 5px 0;">{total_girls:,}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with metric_col4:
                        ratio_color = "#28a745" if 0.8 <= overall_ratio <= 1.2 else "#ffc107" if 0.6 <= overall_ratio <= 1.4 else "#dc3545"
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4 style="color: #667eea; margin: 0;">⚖️ Gender Ratio</h4>
                            <h3 style="color: {ratio_color}; margin: 5px 0;">{overall_ratio:.2f}</h3>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Class progression analysis
                    st.markdown("#### 📉 Class Progression Analysis")
                    
                    # Calculate dropout rates between classes
                    progression_data = []
                    for i in range(len(class_df) - 1):
                        current_class = class_df.iloc[i]
                        next_class = class_df.iloc[i + 1]
                        
                        if current_class['Total Enrollment'] > 0:
                            retention_rate = (next_class['Total Enrollment'] / current_class['Total Enrollment']) * 100
                            dropout_rate = 100 - retention_rate
                            
                            progression_data.append({
                                'Transition': f"{current_class['Class']} → {next_class['Class']}",
                                'Retention Rate (%)': round(retention_rate, 1),
                                'Dropout Rate (%)': round(dropout_rate, 1)
                            })
                    
                    if progression_data:
                        progression_df = pd.DataFrame(progression_data)
                        st.dataframe(progression_df, use_container_width=True)
                        
                        # Visualize progression
                        fig_progression = px.line(
                            class_df,
                            x='Class',
                            y='Total Enrollment',
                            title='Student Progression Across Classes',
                            markers=True,
                            line_shape='linear'
                        )
                        fig_progression.update_traces(
                            line=dict(color='#667eea', width=3),
                            marker=dict(size=10, color='#764ba2')
                        )
                        fig_progression.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(family="Inter, sans-serif")
                        )
                        st.plotly_chart(fig_progression, use_container_width=True)
                    
                    # School-wise analysis if multiple schools
                    if not extracted_df["School Name"].isna().all():
                        st.markdown("#### 🏫 School-wise Educational Performance")
                        
                        school_enrollment = extracted_df.groupby("School Name")[enrollment_columns].sum().sum(axis=1).sort_values(ascending=False)
                        
                        if len(school_enrollment) > 1:
                            top_schools = school_enrollment.head(10)
                            
                            fig_schools = px.bar(
                                x=top_schools.values,
                                y=top_schools.index,
                                orientation='h',
                                title='Top 10 Schools by Total Enrollment',
                                color=top_schools.values,
                                color_continuous_scale='Blues'
                            )
                            fig_schools.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(family="Inter, sans-serif"),
                                yaxis={'categoryorder': 'total ascending'},
                                showlegend=False
                            )
                            st.plotly_chart(fig_schools, use_container_width=True)
            else:
                st.info("📚 No educational enrollment data found in the current dataset.")
        
        with tab5:
            st.markdown("### 📊 Statistical Analysis Dashboard")
            
            if numeric_columns:
                # Create a comprehensive statistical overview
                col1, col2 = st.columns(2)
                
                with col1:
                    # Summary statistics
                    st.markdown("#### 📈 Summary Statistics")
                    summary_stats = extracted_df[numeric_columns].describe()
                    st.dataframe(summary_stats.round(2), use_container_width=True)
                
                with col2:
                    # Correlation heatmap if multiple numeric columns
                    if len(numeric_columns) > 1:
                        st.markdown("#### 🔗 Correlation Matrix")
                        corr_matrix = extracted_df[numeric_columns].corr()
                        
                        fig_heatmap = px.imshow(
                            corr_matrix,
                            title="Correlation Between Numeric Variables",
                            color_continuous_scale='RdBu_r',
                            aspect='auto'
                        )
                        fig_heatmap.update_layout(
                            font=dict(family="Inter, sans-serif"),
                            title_font_size=16
                        )
                        st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Distribution plots
                st.markdown("#### 📊 Data Distribution Analysis")
                selected_column = st.selectbox("Select column for distribution analysis:", numeric_columns)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Histogram
                    fig_hist = px.histogram(
                        extracted_df,
                        x=selected_column,
                        title=f"Distribution of {selected_column}",
                        color_discrete_sequence=['#667eea']
                    )
                    fig_hist.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter, sans-serif")
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                with col2:
                    # Box plot
                    fig_box = px.box(
                        extracted_df,
                        y=selected_column,
                        title=f"Box Plot of {selected_column}",
                        color_discrete_sequence=['#764ba2']
                    )
                    fig_box.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter, sans-serif")
                    )
                    st.plotly_chart(fig_box, use_container_width=True)
            else:
                st.info("📊 No numeric columns available for statistical analysis")
                
                # Show data quality metrics instead
                st.markdown("#### 🔍 Data Quality Overview")
                quality_metrics = {
                    "Total Records": len(extracted_df),
                    "Complete Records": len(extracted_df.dropna()),
                    "Missing Values": extracted_df.isnull().sum().sum(),
                    "Duplicate Records": extracted_df.duplicated().sum()
                }
                
                quality_df = pd.DataFrame(list(quality_metrics.items()), columns=['Metric', 'Value'])
                
                fig_quality = px.bar(
                    quality_df,
                    x='Metric',
                    y='Value',
                    title="Data Quality Metrics",
                    color='Value',
                    color_continuous_scale='Blues'
                )
                fig_quality.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(family="Inter, sans-serif"),
                    showlegend=False
                )
                st.plotly_chart(fig_quality, use_container_width=True)
        
        with tab3:
            st.markdown("### 🔍 Advanced Data Filtering & Analysis")
            
            # Create a sidebar for filtering options
            st.sidebar.markdown("### 🎛️ Advanced Filter Options")
            st.sidebar.markdown("---")
            
            # Hierarchy selection
            grouping_selection = st.sidebar.radio(
                "📊 Select analysis level:",
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
            
            # Initialize filtered dataframe
            filtered_df = extracted_df.copy()
            selected_values = {}
            
            # Apply hierarchical filters
            for level in hierarchy[grouping_selection]:
                level_values = sorted(filtered_df[level].dropna().unique())
                
                if level_values:
                    selected_value = st.sidebar.selectbox(f"🔽 Select {level}", level_values)
                    selected_values[level] = selected_value
                    filtered_df = filtered_df[filtered_df[level] == selected_value]
            
            # Display filtered results
            if filtered_df.empty:
                st.warning("⚠️ No data matches the selected filters.")
            else:
                st.success(f"✅ Found {len(filtered_df)} records matching your filters")
                
                # Show filtered metrics
                if numeric_columns:
                    metric_cols = st.columns(len(numeric_columns))
                    for i, col in enumerate(numeric_columns):
                        with metric_cols[i]:
                            total_val = filtered_df[col].sum()
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4 style="color: #667eea; margin: 0;">{col}</h4>
                                <h3 style="color: #333; margin: 5px 0;">{total_val:,.0f}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Create grouped analysis
                if numeric_columns:
                    group_columns = hierarchy[grouping_selection]
                    
                    # Safe aggregation with error handling
                    try:
                        available_numeric = [col for col in numeric_columns if col in filtered_df.columns]
                        if available_numeric:
                            grouped_data = filtered_df.groupby(group_columns)[available_numeric].sum().reset_index()
                            
                            # Create visualization
                            if len(available_numeric) > 1:
                                # Multi-variable comparison
                                fig = make_subplots(
                                    rows=1, cols=len(available_numeric),
                                    subplot_titles=available_numeric,
                                    shared_yaxis=True
                                )
                                
                                colors = ['#667eea', '#764ba2', '#4facfe', '#00f2fe']
                                for i, col in enumerate(available_numeric):
                                    fig.add_trace(
                                        go.Bar(
                                            x=grouped_data[group_columns[-1]] if len(group_columns) == 1 else grouped_data.index,
                                            y=grouped_data[col],
                                            name=col,
                                            marker_color=colors[i % len(colors)]
                                        ),
                                        row=1, col=i+1
                                    )
                                
                                fig.update_layout(
                                    title_text=f"Comparison Across {grouping_selection}",
                                    font=dict(family="Inter, sans-serif"),
                                    height=500,
                                    showlegend=False
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                # Single variable analysis
                                fig_single = px.bar(
                                    grouped_data,
                                    x=group_columns[-1] if len(group_columns) == 1 else grouped_data.index,
                                    y=available_numeric[0],
                                    title=f"{available_numeric[0]} by {grouping_selection}",
                                    color=available_numeric[0],
                                    color_continuous_scale='Blues'
                                )
                                fig_single.update_layout(
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    font=dict(family="Inter, sans-serif")
                                )
                                st.plotly_chart(fig_single, use_container_width=True)
                            
                            # Show the grouped data table
                            st.markdown("#### 📋 Grouped Analysis Results")
                            st.dataframe(grouped_data, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"❌ Error in grouping analysis: {str(e)}")
                        st.info("💡 This might be due to missing or incompatible data types in the selected columns.")
        
        with tab4:
            st.markdown("### 📋 Data Tables & Export Options")
            
            # Data table options
            table_option = st.radio(
                "Select data view:",
                ["Original Data", "Extracted Data", "Summary by District", "Summary by Chiefdom"],
                horizontal=True
            )
            
            if table_option == "Original Data":
                st.markdown("#### 📄 Original Excel Data")
                st.dataframe(df_original, use_container_width=True)
                
            elif table_option == "Extracted Data":
                st.markdown("#### 📋 Processed & Extracted Data")
                st.dataframe(extracted_df, use_container_width=True)
                
            elif table_option == "Summary by District" and not extracted_df["District"].isna().all():
                st.markdown("#### 🌍 District Summary")
                if numeric_columns:
                    district_summary = extracted_df.groupby("District")[numeric_columns].sum().reset_index()
                    st.dataframe(district_summary, use_container_width=True)
                    
                    # Create download button for district summary
                    csv_district = district_summary.to_csv(index=False)
                    st.download_button(
                        label="📥 Download District Summary",
                        data=csv_district,
                        file_name="district_summary.csv",
                        mime="text/csv"
                    )
                else:
                    district_counts = extracted_df["District"].value_counts().reset_index()
                    district_counts.columns = ["District", "Count"]
                    st.dataframe(district_counts, use_container_width=True)
                
            elif table_option == "Summary by Chiefdom" and not extracted_df["Chiefdom"].isna().all():
                st.markdown("#### 🏘️ Chiefdom Summary")
                if numeric_columns:
                    chiefdom_summary = extracted_df.groupby(["District", "Chiefdom"])[numeric_columns].sum().reset_index()
                    st.dataframe(chiefdom_summary, use_container_width=True)
                    
                    # Create download button for chiefdom summary
                    csv_chiefdom = chiefdom_summary.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Chiefdom Summary",
                        data=csv_chiefdom,
                        file_name="chiefdom_summary.csv",
                        mime="text/csv"
                    )
                else:
                    chiefdom_counts = extracted_df.groupby(["District", "Chiefdom"]).size().reset_index(name="Count")
                    st.dataframe(chiefdom_counts, use_container_width=True)
            
            # Export options
            st.markdown("#### 📤 Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Download extracted data
                csv_extracted = extracted_df.to_csv(index=False)
                st.download_button(
                    label="📊 Download Extracted Data",
                    data=csv_extracted,
                    file_name="extracted_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Download original data
                csv_original = df_original.to_csv(index=False)
                st.download_button(
                    label="📋 Download Original Data",
                    data=csv_original,
                    file_name="original_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col3:
                if numeric_columns:
                    # Download summary statistics
                    summary_stats = extracted_df[numeric_columns].describe()
                    csv_stats = summary_stats.to_csv()
                    st.download_button(
                        label="📈 Download Statistics",
                        data=csv_stats,
                        file_name="summary_statistics.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        
        # Enhanced Quick Actions Section
        st.markdown('<div class="section-header">⚡ Quick Analysis Actions</div>', unsafe_allow_html=True)
        
        # Create action buttons
        action_col1, action_col2, action_col3, action_col4 = st.columns(4)
        
        with action_col1:
            if st.button("🌍 Geographic Overview", use_container_width=True):
                st.markdown("### 🗺️ Geographic Distribution Summary")
                
                # Create comprehensive geographic overview
                if not extracted_df["District"].isna().all():
                    geo_summary = extracted_df.groupby("District").agg({
                        'Chiefdom': 'nunique',
                        'PHU Name': 'nunique',
                        'Community Name': 'nunique',
                        'School Name': 'nunique'
                    }).round(2)
                    geo_summary.columns = ['Chiefdoms', 'PHUs', 'Communities', 'Schools']
                    
                    # Add total records per district
                    geo_summary['Total Records'] = extracted_df.groupby("District").size()
                    
                    # Add numeric totals if available
                    if numeric_columns:
                        for col in numeric_columns:
                            geo_summary[f'Total {col}'] = extracted_df.groupby("District")[col].sum()
                    
                    st.dataframe(geo_summary, use_container_width=True)
                    
                    # Create a comprehensive visualization
                    fig_geo = px.bar(
                        x=geo_summary.index,
                        y=geo_summary['Total Records'],
                        title="Records Distribution Across Districts",
                        labels={'x': 'District', 'y': 'Number of Records'},
                        color=geo_summary['Total Records'],
                        color_continuous_scale='Blues',
                        text=geo_summary['Total Records']
                    )
                    fig_geo.update_traces(texttemplate='%{text}', textposition='outside')
                    fig_geo.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter, sans-serif"),
                        title_font_size=18,
                        showlegend=False
                    )
                    st.plotly_chart(fig_geo, use_container_width=True)
        
        with action_col3:
            if st.button("📊 Statistical Summary", use_container_width=True) and numeric_columns:
            if st.button("📚 Educational Overview", use_container_width=True):
                st.markdown("### 🎓 Comprehensive Educational Analysis")
                
                if enrollment_columns or boys_columns or girls_columns:
                    # Create comprehensive educational summary
                    edu_summary = {
                        "Metric": [],
                        "Value": [],
                        "Details": []
                    }
                    
                    # Calculate totals for each class
                    for class_num in range(1, 6):
                        enrollment_col = f'Number of enrollments in class {class_num}'
                        boys_col = f'Number of boys in class {class_num}'
                        girls_col = f'Number of girls in class {class_num}'
                        
                        if enrollment_col in extracted_df.columns:
                            total_enrollment = extracted_df[enrollment_col].sum()
                            boys_count = extracted_df[boys_col].sum() if boys_col in extracted_df.columns else 0
                            girls_count = extracted_df[girls_col].sum() if girls_col in extracted_df.columns else 0
                            
                            edu_summary["Metric"].extend([
                                f"Class {class_num} Total",
                                f"Class {class_num} Boys",
                                f"Class {class_num} Girls"
                            ])
                            
                            edu_summary["Value"].extend([
                                f"{total_enrollment:,}",
                                f"{boys_count:,}",
                                f"{girls_count:,}"
                            ])
                            
                            gender_ratio = girls_count / boys_count if boys_count > 0 else 0
                            edu_summary["Details"].extend([
                                f"📊 Total students in Class {class_num}",
                                f"♂️ Male students ({boys_count/total_enrollment*100:.1f}%)" if total_enrollment > 0 else "♂️ Male students",
                                f"♀️ Female students ({girls_count/total_enrollment*100:.1f}%)" if total_enrollment > 0 else "♀️ Female students"
                            ])
                    
                    # Overall statistics
                    total_students = sum([extracted_df[col].sum() for col in enrollment_columns if col in extracted_df.columns])
                    total_boys = sum([extracted_df[col].sum() for col in boys_columns if col in extracted_df.columns])
                    total_girls = sum([extracted_df[col].sum() for col in girls_columns if col in extracted_df.columns])
                    
                    edu_summary["Metric"].extend([
                        "🎯 Total Students",
                        "♂️ Total Boys",
                        "♀️ Total Girls",
                        "⚖️ Gender Parity Index"
                    ])
                    
                    gpi = total_girls / total_boys if total_boys > 0 else 0
                    parity_status = "✅ Good" if 0.97 <= gpi <= 1.03 else "⚠️ Attention Needed"
                    
                    edu_summary["Value"].extend([
                        f"{total_students:,}",
                        f"{total_boys:,}",
                        f"{total_girls:,}",
                        f"{gpi:.3f}"
                    ])
                    
                    edu_summary["Details"].extend([
                        "📚 All students across classes 1-5",
                        f"🔵 {total_boys/total_students*100:.1f}% of total enrollment" if total_students > 0 else "🔵 Male enrollment",
                        f"🟡 {total_girls/total_students*100:.1f}% of total enrollment" if total_students > 0 else "🟡 Female enrollment",
                        f"{parity_status} (Target: 0.97-1.03)"
                    ])
                    
                    edu_df = pd.DataFrame(edu_summary)
                    st.dataframe(edu_df, use_container_width=True)
                    
                    # Educational insights
                    st.markdown("#### 💡 Key Educational Insights")
                    insights = []
                    
                    if gpi < 0.9:
                        insights.append("🚨 **Gender Gap Alert**: Significant underrepresentation of girls in enrollment")
                    elif gpi > 1.1:
                        insights.append("📈 **Girls Leading**: Higher female enrollment than male")
                    else:
                        insights.append("⚖️ **Balanced Enrollment**: Good gender parity in student enrollment")
                    
                    # Find class with highest/lowest enrollment
                    class_enrollments = []
                    for class_num in range(1, 6):
                        enrollment_col = f'Number of enrollments in class {class_num}'
                        if enrollment_col in extracted_df.columns:
                            class_enrollments.append((class_num, extracted_df[enrollment_col].sum()))
                    
                    if class_enrollments:
                        highest_class = max(class_enrollments, key=lambda x: x[1])
                        lowest_class = min(class_enrollments, key=lambda x: x[1])
                        
                        insights.append(f"📊 **Highest Enrollment**: Class {highest_class[0]} ({highest_class[1]:,} students)")
                        insights.append(f"📉 **Lowest Enrollment**: Class {lowest_class[0]} ({lowest_class[1]:,} students)")
                        
                        # Calculate retention between classes
                        retention_issues = []
                        for i in range(len(class_enrollments) - 1):
                            current = class_enrollments[i][1]
                            next_class = class_enrollments[i + 1][1]
                            if current > 0:
                                retention_rate = (next_class / current) * 100
                                if retention_rate < 85:  # Less than 85% retention
                                    retention_issues.append(f"Class {class_enrollments[i][0]} to {class_enrollments[i + 1][0]} ({retention_rate:.1f}%)")
                        
                        if retention_issues:
                            insights.append(f"⚠️ **Retention Concerns**: {', '.join(retention_issues)}")
                    
                    for insight in insights:
                        st.markdown(f"- {insight}")
                else:
                    st.info("📚 No educational enrollment data available for analysis.")
        
        with action_col3:
            if st.button("📊 Data Quality Check", use_container_width=True):
                st.markdown("### 🔍 Data Quality Assessment")
                
                # Comprehensive data quality analysis
                quality_report = {
                    "Metric": [],
                    "Value": [],
                    "Percentage": [],
                    "Status": []
                }
                
                total_records = len(extracted_df)
                
                # Check completeness for each column
                for col in extracted_df.columns:
                    missing_count = extracted_df[col].isnull().sum()
                    missing_pct = (missing_count / total_records) * 100
                    
                    quality_report["Metric"].append(f"Missing {col}")
                    quality_report["Value"].append(missing_count)
                    quality_report["Percentage"].append(f"{missing_pct:.1f}%")
                    
                    if missing_pct < 5:
                        status = "✅ Excellent"
                    elif missing_pct < 15:
                        status = "⚠️ Good"
                    elif missing_pct < 30:
                        status = "🔶 Fair"
                    else:
                        status = "❌ Poor"
                    quality_report["Status"].append(status)
                
                # Add overall statistics
                quality_report["Metric"].extend([
                    "Total Records",
                    "Complete Records",
                    "Duplicate Records",
                    "Unique Districts",
                    "Unique Chiefdoms"
                ])
                
                complete_records = len(extracted_df.dropna())
                duplicate_records = extracted_df.duplicated().sum()
                
                quality_report["Value"].extend([
                    total_records,
                    complete_records,
                    duplicate_records,
                    extracted_df["District"].nunique(),
                    extracted_df["Chiefdom"].nunique()
                ])
                
                quality_report["Percentage"].extend([
                    "100%",
                    f"{(complete_records/total_records)*100:.1f}%",
                    f"{(duplicate_records/total_records)*100:.1f}%",
                    "-",
                    "-"
                ])
                
                quality_report["Status"].extend([
                    "ℹ️ Info",
                    "✅ Excellent" if complete_records/total_records > 0.8 else "⚠️ Review",
                    "✅ Good" if duplicate_records == 0 else "⚠️ Check",
                    "ℹ️ Info",
                    "ℹ️ Info"
                ])
                
                quality_df = pd.DataFrame(quality_report)
                st.dataframe(quality_df, use_container_width=True)
        
        with action_col3:
            if st.button("📈 Statistical Summary", use_container_width=True) and numeric_columns:
                st.markdown("### 📊 Comprehensive Statistical Analysis")
                
                # Enhanced statistical overview
                stats_summary = extracted_df[numeric_columns].describe()
                st.dataframe(stats_summary.round(2), use_container_width=True)
                
                # Create distribution comparison
                if len(numeric_columns) > 1:
                    fig_dist = make_subplots(
                        rows=1, cols=len(numeric_columns),
                        subplot_titles=numeric_columns
                    )
                    
                    colors = ['#667eea', '#764ba2', '#4facfe', '#00f2fe']
                    for i, col in enumerate(numeric_columns):
                        fig_dist.add_trace(
                            go.Histogram(
                                x=extracted_df[col],
                                name=col,
                                marker_color=colors[i % len(colors)],
                                opacity=0.7
                            ),
                            row=1, col=i+1
                        )
                    
                    fig_dist.update_layout(
                        title_text="Distribution Comparison of Numeric Variables",
                        font=dict(family="Inter, sans-serif"),
                        height=400,
                        showlegend=False
                    )
                    st.plotly_chart(fig_dist, use_container_width=True)
                
                # Statistical insights
                st.markdown("#### 🔍 Key Statistical Insights")
                for col in numeric_columns:
                    col_data = extracted_df[col].dropna()
                    if len(col_data) > 0:
                        st.markdown(f"""
                        **{col}:**
                        - Mean: {col_data.mean():.2f}
                        - Median: {col_data.median():.2f}
                        - Standard Deviation: {col_data.std():.2f}
                        - Range: {col_data.min():.0f} to {col_data.max():.0f}
                        """)
        
        with action_col4:
            if st.button("🎯 Smart Insights", use_container_width=True):
                st.markdown("### 🧠 AI-Powered Data Insights")
                
                insights = []
                
                # Geographic insights
                if not extracted_df["District"].isna().all():
                    district_counts = extracted_df["District"].value_counts()
                    top_district = district_counts.index[0]
                    top_count = district_counts.iloc[0]
                    insights.append(f"🌍 **Top District**: {top_district} has the highest number of records ({top_count})")
                
                # Data completeness insights
                completeness = (extracted_df.notna().sum() / len(extracted_df)) * 100
                most_complete = completeness.idxmax()
                least_complete = completeness.idxmin()
                insights.append(f"📊 **Data Quality**: '{most_complete}' is most complete ({completeness[most_complete]:.1f}%), '{least_complete}' needs attention ({completeness[least_complete]:.1f}%)")
                
                # Numeric insights
                if numeric_columns:
                    for col in numeric_columns[:2]:  # Limit to first 2 numeric columns
                        col_data = extracted_df[col].dropna()
                        if len(col_data) > 0:
                            if col_data.std() / col_data.mean() > 1:
                                insights.append(f"📈 **{col}**: Shows high variability (CV: {(col_data.std()/col_data.mean()):.2f})")
                            else:
                                insights.append(f"📊 **{col}**: Shows consistent values (CV: {(col_data.std()/col_data.mean()):.2f})")
                
                # Pattern insights
                if not extracted_df["District"].isna().all() and not extracted_df["Chiefdom"].isna().all():
                    district_chiefdom_ratio = extracted_df.groupby("District")["Chiefdom"].nunique()
                    avg_chiefdoms = district_chiefdom_ratio.mean()
                    insights.append(f"🏘️ **Geographic Structure**: Average of {avg_chiefdoms:.1f} chiefdoms per district")
                
                # Display insights
                for i, insight in enumerate(insights, 1):
                    st.markdown(f"{i}. {insight}")
                
                # Recommendations
                st.markdown("#### 💡 Recommendations")
                recommendations = [
                    "🔍 Focus data collection efforts on districts with fewer records",
                    "📊 Improve data entry processes for fields with high missing rates",
                    "🎯 Consider standardizing data formats across all collection points",
                    "📈 Regular monitoring of data quality metrics is recommended"
                ]
                
                for rec in recommendations:
                    st.markdown(f"- {rec}")
    
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.markdown("""
        ### 💡 Troubleshooting Tips:
        1. **File Format**: Ensure your file is in Excel format (.xlsx or .xls)
        2. **Required Columns**: Your file must contain a 'Scan QR code' column
        3. **Data Format**: QR code data should contain patterns like 'District:', 'Chiefdom:', etc.
        4. **File Size**: Large files may take longer to process
        
        ### 📋 Expected Data Format:
        The QR code column should contain text with patterns like:
        ```
        District: [District Name]
        Chiefdom: [Chiefdom Name]
        PHU name: [PHU Name]
        Community name: [Community Name]
        Name of school: [School Name]
        ```
        """)

# Enhanced Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-top: 30px;">
    <h3 style="margin: 0; font-size: 1.5rem;">📊 ITN Data Analytics Dashboard</h3>
    <p style="margin: 10px 0; opacity: 0.9;">Advanced Text Data Extraction & Visualization Platform</p>
    <p style="margin: 0; font-size: 0.9rem; opacity: 0.8;">Built with Streamlit • Enhanced Data Processing • Interactive Visualizations</p>
</div>
""", unsafe_allow_html=True)
