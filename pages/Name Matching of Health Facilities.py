import streamlit as st
import time
import random
import threading

# Set page config first
st.set_page_config(page_title="Geospatial Analysis Tool", page_icon="🗺️", layout="wide")

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
        }
        
        /* Dark theme for all text */
        .stMarkdown, p, h1, h2, h3 {
            color: #E0E0E0 !important;
        }
        
        /* Dark theme for selectbox */
        .stSelectbox > div > div {
            background-color: #1E1E1E !important;
            color: #E0E0E0 !important;
        }
        
        /* Dark theme for checkbox */
        .stCheckbox > div > div > label {
            color: #E0E0E0 !important;
        }
        
        /* Update section cards for dark theme */
        .section-card {
            background: #1E1E1E !important;
            color: #E0E0E0 !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
        }
        
        .section-card:hover {
            background: #2E2E2E !important;
        }
        
        /* Dark theme for content text */
        .content-text {
            color: #E0E0E0 !important;
        }

        /* Bullet points */
        .custom-bullet {
            margin-left: 20px;
            position: relative;
        }
        .custom-bullet::before {
            content: "•";
            color: #E0E0E0;
            position: absolute;
            left: -15px;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session states
if 'last_animation' not in st.session_state:
    st.session_state.last_animation = time.time()
    st.session_state.theme_index = 0
    st.session_state.first_load = True

# Define dark themes
themes = {
    "Dark Modern": {
        "bg": "#0E1117",
        "accent": "#3498db",
        "text": "#E0E0E0",
        "gradient": "linear-gradient(135deg, #3498db, #2ecc71)"
    },
    "Dark Elegance": {
        "bg": "#1a1a1a",
        "accent": "#e74c3c",
        "text": "#E0E0E0",
        "gradient": "linear-gradient(135deg, #e74c3c, #c0392b)"
    },
    "Dark Nature": {
        "bg": "#1E1E1E",
        "accent": "#27ae60",
        "text": "#E0E0E0",
        "gradient": "linear-gradient(135deg, #27ae60, #2ecc71)"
    },
    "Dark Cosmic": {
        "bg": "#2c0337",
        "accent": "#9b59b6",
        "text": "#E0E0E0",
        "gradient": "linear-gradient(135deg, #9b59b6, #8e44ad)"
    },
    "Dark Ocean": {
        "bg": "#1A2632",
        "accent": "#00a8cc",
        "text": "#E0E0E0",
        "gradient": "linear-gradient(135deg, #00a8cc, #0089a7)"
    }
}

# Welcome animation on first load
if st.session_state.first_load:
    st.balloons()
    st.snow()
    welcome_placeholder = st.empty()
    welcome_placeholder.success("Welcome to the Geospatial Analysis Tool! 🌍")
    time.sleep(3)
    welcome_placeholder.empty()
    st.session_state.first_load = False

# Auto theme changer and animation
current_time = time.time()
if current_time - st.session_state.last_animation >= 30:
    st.session_state.last_animation = current_time
    theme_keys = list(themes.keys())
    st.session_state.theme_index = (st.session_state.theme_index + 1) % len(theme_keys)
    selected_theme = theme_keys[st.session_state.theme_index]
    st.balloons()
else:
    selected_theme = list(themes.keys())[st.session_state.theme_index]

# Get current theme
theme = themes[selected_theme]

# Apply dark styling
st.markdown(f"""
    <style>
        /* Global Styles */
        .main {{
            background-color: {theme["bg"]};
            color: {theme["text"]};
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        /* Header Styles */
        h1 {{
            background: {theme["gradient"]};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 2rem;
            text-align: center;
            animation: fadeIn 1.5s ease-in;
        }}
        
        /* Section Cards */
        .section-card {{
            background: {theme["bg"]};
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            border-left: 5px solid {theme["accent"]};
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            animation: slideIn 0.5s ease-out;
            color: {theme["text"]};
        }}
        
        .section-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.5);
            background: #2E2E2E;
        }}
        
        /* Section Headers */
        .section-header {{
            color: {theme["accent"]};
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }}
        
        /* Content Text */
        .content-text {{
            line-height: 1.6;
            color: {theme["text"]};
        }}
        
        /* Image Container */
        .img-container {{
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            animation: scaleIn 1s ease;
            background: {theme["bg"]};
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        @keyframes slideIn {{
            from {{ transform: translateX(-20px); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        
        @keyframes scaleIn {{
            from {{ transform: scale(0.95); opacity: 0; }}
            to {{ transform: scale(1); opacity: 1; }}
        }}
    </style>
""", unsafe_allow_html=True)

# Title and Image

st.markdown("""
    <h1 class="title">
        Automated Geospatial Analysis for Sub-National Tailoring of Malaria Interventions
    </h1>
""", unsafe_allow_html=True)

# Adding the title again with custom styling
st.markdown("""
    <h1 class="custom-title">
        Automated Geospatial Analysis for Sub-National Tailoring of Malaria Interventions
    </h1>
""", unsafe_allow_html=True)


# Center the image using markdown with HTML attributes
st.markdown("""
    <p align="center">
        <img src="https://github.com/mohamedsillahkanu/si/raw/b0706926bf09ba23d8e90c394fdbb17e864121d8/Sierra%20Leone%20Map.png" 
             width="30%"
             style="display: block; margin-left: auto; margin-right: auto;">
    </p>
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

# Sidebar theme selector
st.sidebar.selectbox(
    "🎨 Select Theme",
    list(themes.keys()),
    index=st.session_state.theme_index,
    key='theme_selector'
)

# Enable/Disable animations toggle
if st.sidebar.checkbox("Enable Auto Animations", value=True):
    def show_periodic_animations():
        while True:
            time.sleep(60)
            st.balloons()
            time.sleep(10)
            st.snow()

    # Start animation thread if not already running
    if not hasattr(st.session_state, 'animation_thread'):
        st.session_state.animation_thread = threading.Thread(target=show_periodic_animations)
        st.session_state.animation_thread.daemon = True
        st.session_state.animation_thread.start()
