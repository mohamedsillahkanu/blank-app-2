import streamlit as st
import time
import random
import threading

st.set_page_config(page_title="Geospatial Analysis Tool", page_icon="🗺️", layout="wide")

# Initialize session state for animations
if 'last_animation' not in st.session_state:
    st.session_state.last_animation = time.time()
    st.session_state.first_load = True

# First load animations
if st.session_state.first_load:
    st.balloons()
    st.snow()
    welcome_placeholder = st.empty()
    welcome_placeholder.success("Welcome to the Geospatial Analysis Tool! 🌍")
    time.sleep(3)
    welcome_placeholder.empty()
    st.session_state.first_load = False

# Custom CSS styling
st.markdown("""
    <style>
        /* App background */
        .stApp {
            background-color: #000000;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: white !important;
            border-right: 2px solid #3498db !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stMarkdown"] {
            color: #3498db !important;
            font-weight: 700 !important;
            text-shadow: 0 0 1px rgba(52, 152, 219, 0.3) !important;
            font-size: 1.1em !important;
        }
        
        /* Sidebar buttons */
        [data-testid="stSidebar"] button {
            background-color: #3498db !important;
            color: white !important;
            border: none !important;
            border-radius: 20px !important;
            padding: 0.5rem 1rem !important;
            margin: 0.25rem 0 !important;
            font-weight: 600 !important;
            box-shadow: 0 2px 4px rgba(52, 152, 219, 0.2) !important;
            transition: all 0.3s ease !important;
        }
        
        [data-testid="stSidebar"] button:hover {
            background-color: #2980b9 !important;
            box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3) !important;
            transform: translateY(-1px) !important;
        }
        
        /* Sidebar inputs */
        [data-testid="stSidebar"] input,
        [data-testid="stSidebar"] textarea {
            background-color: white !important;
            color: #333333 !important;
            border: 2px solid #3498db !important;
            border-radius: 8px !important;
        }
        
        /* Sidebar select boxes */
        [data-testid="stSidebar"] .stSelectbox > div > div {
            background-color: white !important;
            color: #333333 !important;
            border: 2px solid #3498db !important;
            border-radius: 8px !important;
        }
        
        /* Sidebar multiselect */
        [data-testid="stSidebar"] .stMultiSelect > div > div {
            background-color: white !important;
            color: #333333 !important;
            border: 2px solid #3498db !important;
            border-radius: 8px !important;
        }
        
        /* Main content styling */
        .stMarkdown, p, h1, h2, h3 {
            color: #E0E0E0 !important;
        }
        
        .custom-title {
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            padding: 1rem 0;
            margin-bottom: 2rem;
            color: #E0E0E0;
            background: linear-gradient(135deg, #3498db, #2ecc71);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .section-card {
            background: #1E1E1E;
            color: #E0E0E0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            border-left: 5px solid #3498db;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            animation: slideIn 0.5s ease-out;
        }
        
        .section-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.5);
            background: #2E2E2E;
        }

        .section-header {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #3498db !important;
        }
        
        .custom-bullet {
            margin-left: 20px;
            position: relative;
            color: #E0E0E0 !important;
        }
        
        .custom-bullet::before {
            content: "•";
            color: #E0E0E0;
            position: absolute;
            left: -15px;
        }
        
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

# Check time for periodic animations
current_time = time.time()
if current_time - st.session_state.last_animation >= 30:
    st.session_state.last_animation = current_time
    st.balloons()

# Your main app content goes here
st.markdown('<h1 class="custom-title">Geospatial Analysis Tool 🌍</h1>', unsafe_allow_html=True)

# Example section cards
with st.container():
    st.markdown("""
    <div class="section-card">
        <div class="section-header text-center">Welcome to the Geospatial Analysis Tool</div>
        <p class="content-text">This tool helps you analyze and visualize geospatial data effectively.</p>
    </div>
    """, unsafe_allow_html=True)

st.title("Automated Geospatial Analysis for Sub-National Tailoring of Malaria Interventions")

st.markdown("""
    <div class="img-container" style="text-align: center;">
        <img src="https://github.com/mohamedsillahkanu/si/raw/b0706926bf09ba23d8e90c394fdbb17e864121d8/Sierra%20Leone%20Map.png" 
             style="width: 50%; max-width: 500px; margin: 20px auto;">
    </div>
""", unsafe_allow_html=True)

sections = {
    "Overview": """Before now, the Sub-National Tailoring (SNT) process took a considerable amount of time to complete analysis. Based on the experience of the 2023 SNT implementation, we have developed an automated tool using the same validated codes with additional enhanced features. This innovation aims to build the capacity of National Malaria Control Program (NMCP) to conduct SNT easily on a yearly basis and monitor activities effectively using this tool. The tool is designed to be user-friendly and offers high processing speed.

The integration of automation in geospatial analysis significantly enhances the efficiency and effectiveness of data management and visualization tasks. With the introduction of this automated system, analysis time has been drastically reduced from one year to one week. This shift not only streamlines operations but also allows analysts to focus on interpreting results rather than being bogged down by technical processes.""",
    
    "Objectives": """The main objectives of implementing automated systems for geospatial analysis and data management are:
    <div class='custom-bullet'>Reduce Time and Effort: Significantly decrease the time required to create maps and analyze data, enabling quicker decision-making.</div>
    <div class='custom-bullet'>Enhance Skill Accessibility: Provide tools that can be used effectively by individuals without extensive technical training.</div>
    <div class='custom-bullet'>Improve Data Management Efficiency: Streamline data management processes that currently can take days to complete.</div>
    <div class='custom-bullet'>Facilitate Rapid Analysis: Enable automated analysis of uploaded datasets within minutes.</div>""",
    
    "Scope": """
    <div class='custom-bullet'>The development and implementation of an automated system that simplifies the creation of geospatial visualizations.</div>
    <div class='custom-bullet'>A comprehensive automated data analysis tool that processes datasets quickly and efficiently, enabling analysts to obtain insights in less than 20 minutes.</div>
    <div class='custom-bullet'>Training and support for users to maximize the benefits of these tools, ensuring that even those with limited technical skills can leverage automation for their analytical needs.</div>""",
    
    "Target Audience": """
    <div class='custom-bullet'>Public health officials and analysts working within NMCPs who require efficient mapping and data analysis solutions.</div>
    <div class='custom-bullet'>Data managers and decision-makers seeking to improve operational efficiency and responsiveness to health challenges.</div>
    <div class='custom-bullet'>Organizations interested in integrating automation into their workflows to enhance data-driven decision-making capabilities.</div>""",
    
    "Conclusion": """The adoption of this automated system for SNT analysis represents a transformative opportunity for NMCPs. By significantly reducing the time and effort required for these tasks, programs can enhance their efficiency, improve the quality of their analyses, and ultimately lead to more timely and informed decision-making. This tool, built on the experience of the 2023 SNT implementation, not only addresses existing operational challenges but also empowers analysts to focus on deriving insights rather than getting lost in technical details. The user-friendly interface and high processing speed make it an invaluable asset for regular SNT updates and monitoring of malaria control activities."""
}

for i, (title, content) in enumerate(sections.items()):
    time.sleep(0.2)
    st.markdown(f"""
        <div class="section-card">
            <div class="section-header">{title}</div>
            <div class="content-text">{content}</div>
        </div>
    """, unsafe_allow_html=True)

def show_confetti():
    st.markdown("""
        <style>
            @keyframes confetti {
                0% { transform: translateY(0) rotate(0deg); }
                100% { transform: translateY(100vh) rotate(360deg); }
            }
            .confetti {
                position: fixed;
                animation: confetti 4s linear;
                z-index: 9999;
            }
        </style>
    """, unsafe_allow_html=True)
    for i in range(50):
        color = f"hsl({random.randint(0, 360)}, 100%, 50%)"
        left = random.randint(0, 100)
        st.markdown(f"""
            <div class="confetti" style="left: {left}vw; background: {color}; 
            width: 10px; height: 10px; border-radius: 50%;"></div>
        """, unsafe_allow_html=True)

def show_sparkles():
    st.markdown("""
        <style>
            @keyframes sparkle {
                0% { transform: scale(0); opacity: 0; }
                50% { transform: scale(1); opacity: 1; }
                100% { transform: scale(0); opacity: 0; }
            }
            .sparkle {
                position: fixed;
                animation: sparkle 2s infinite;
            }
        </style>
    """, unsafe_allow_html=True)
    for i in range(20):
        left = random.randint(0, 100)
        top = random.randint(0, 100)
        st.markdown(f"""
            <div class="sparkle" style="left: {left}vw; top: {top}vh; 
            background: gold; width: 5px; height: 5px; border-radius: 50%;"></div>
        """, unsafe_allow_html=True)

def show_fireworks():
    animations = [st.balloons(), st.snow(), show_confetti(), show_sparkles()]
    random.choice(animations)

animations_list = [
    st.balloons,
    st.snow,
    show_confetti,
    show_sparkles,
    show_fireworks,
    lambda: [st.balloons(), st.snow()],
    lambda: [show_confetti(), show_sparkles()],
    lambda: [st.balloons(), show_confetti()],
    lambda: [st.snow(), show_sparkles()],
    lambda: [show_confetti(), st.snow()]
]



