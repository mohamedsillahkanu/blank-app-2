import streamlit as st
import time

# Set page config first
st.set_page_config(page_title="Geospatial Analysis Tool", page_icon="🗺️", layout="wide")

# Initialize session state for first load
if 'first_load' not in st.session_state:
    st.session_state.first_load = True

# Force dark theme across the entire app
st.markdown("""
    <style>
        /* Override Streamlit's default theme to force dark mode */
        .stApp {
            background-color: #0E1117 !important;
        }
        
        /* Dark theme for sidebar */
        [data-testid="stSidebar"] {
            background-color: #1E1E1E !important;
            border-right: 1px solid #2E2E2E;
            display: none;  /* Hide sidebar */
        }
        
        /* Dark theme for all text */
        .stMarkdown, p, h1, h2, h3 {
            color: #E0E0E0 !important;
        }
        
        /* Section Cards */
        .section-card {
            background: #1E1E1E !important;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            border-left: 5px solid #3498db;
            transition: transform 0.3s ease;
            animation: slideIn 0.5s ease-out;
            color: #E0E0E0;
        }
        
        .section-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.5);
            background: #2E2E2E !important;
        }
        
        /* Header Styles */
        h1 {
            background: linear-gradient(135deg, #3498db, #2ecc71);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 2rem;
            text-align: center;
            animation: fadeIn 1.5s ease-in;
        }
        
        /* Section Headers */
        .section-header {
            color: #3498db;
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        /* Bullet points */
        .custom-bullet {
            margin-left: 20px;
            position: relative;
            margin-bottom: 10px;
        }
        .custom-bullet::before {
            content: "•";
            color: #3498db;
            position: absolute;
            left: -15px;
        }
        
        /* Image Container */
        .img-container {
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            animation: scaleIn 1s ease;
        }
        
        /* Success Message */
        .stSuccess {
            background-color: #2E2E2E !important;
            color: #E0E0E0 !important;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideIn {
            from { transform: translateX(-20px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes scaleIn {
            from { transform: scale(0.95); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
    </style>
""", unsafe_allow_html=True)

# Welcome animation on first load
if st.session_state.first_load:
    st.snow()  # First snow animation
    time.sleep(1)  # Short delay
    st.balloons()  # Then balloons
    welcome_placeholder = st.empty()
    welcome_placeholder.success("Welcome to the Geospatial Analysis Tool! 🌍")
    time.sleep(3)
    welcome_placeholder.empty()
    st.session_state.first_load = False

# Title and Image
st.markdown("<h1>Automated Geospatial Analysis for Sub-National Tailoring of Malaria Interventions</h1>", unsafe_allow_html=True)

st.markdown("""
    <div class="img-container">
        <img src="https://github.com/mohamedsillahkanu/si/raw/b0706926bf09ba23d8e90c394fdbb17e864121d8/Sierra%20Leone%20Map.png" 
             style="width: 100%; height: auto;">
    </div>
""", unsafe_allow_html=True)

# Content Sections
sections = {
    "Overview": """Before now, the Sub-National Tailoring (SNT) process took a considerable amount of time to complete analysis. Based on the experience of the 2023 SNT implementation, we have developed an automated tool using the same validated codes with additional enhanced features. This innovation aims to build the capacity of National Malaria Control Program (NMCP) to conduct SNT easily on a yearly basis and monitor activities effectively using this tool. The tool is designed to be user-friendly and offers high processing speed.

The integration of automation in geospatial analysis significantly enhances the efficiency and effectiveness of data management and visualization tasks. With the introduction of this automated system, analysis time has been drastically reduced from one year to one week. This shift not only streamlines operations but also allows analysts to focus on interpreting results rather than being bogged down by technical processes.""",
    
    "Objectives": """The main objectives of implementing automated systems for geospatial analysis and data management are:
    <div class='custom-bullet'>Reduce Time and Effort: Significantly decrease the time required to create maps and analyze data, enabling quicker decision-making.</div>
    <div class='custom-bullet'>Enhance Skill Accessibility: Provide tools that can be used effectively by individuals without extensive technical training.</div>
    <div class='custom-bullet'>Improve Data Management Efficiency: Streamline data management processes that currently can take days to complete.</div>
    <div class='custom-bullet'>Facilitate Rapid Analysis: Enable automated analysis of uploaded datasets within minutes.</div>""",
    
    "Scope": """The scope of this project encompasses:
    <div class='custom-bullet'>The development and implementation of an automated system that simplifies the creation of geospatial visualizations.</div>
    <div class='custom-bullet'>A comprehensive automated data analysis tool that processes datasets quickly and efficiently, enabling analysts to obtain insights in less than 20 minutes.</div>
    <div class='custom-bullet'>Training and support for users to maximize the benefits of these tools, ensuring that even those with limited technical skills can leverage automation for their analytical needs.</div>""",
    
    "Target Audience": """The target audience includes:
    <div class='custom-bullet'>Public health officials and analysts working within NMCPs who require efficient mapping and data analysis solutions.</div>
    <div class='custom-bullet'>Data managers and decision-makers seeking to improve operational efficiency and responsiveness to health challenges.</div>
    <div class='custom-bullet'>Organizations interested in integrating automation into their workflows to enhance data-driven decision-making capabilities.</div>""",
    
    "Conclusion": """The adoption of this automated system for SNT analysis represents a transformative opportunity for NMCPs. By significantly reducing the time and effort required for these tasks, programs can enhance their efficiency, improve the quality of their analyses, and ultimately lead to more timely and informed decision-making. This tool, built on the experience of the 2023 SNT implementation, not only addresses existing operational challenges but also empowers analysts to focus on deriving insights rather than getting lost in technical details. The user-friendly interface and high processing speed make it an invaluable asset for regular SNT updates and monitoring of malaria control activities."""
}

# Display sections with animation delay
for i, (title, content) in enumerate(sections.items()):
    time.sleep(0.2)  # Small delay between sections
    st.markdown(f"""
        <div class="section-card">
            <div class="section-header">{title}</div>
            <div class="content-text">{content}</div>
        </div>
    """, unsafe_allow_html=True)
