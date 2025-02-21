import streamlit as st
import time
import random
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Geospatial Analysis Tool",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme configuration
theme = {
    "bg": "#F5F5F5",
    "accent": "#1E88E5",
    "text": "#212121",
    "gradient": "linear-gradient(135deg, #1E88E5, #64B5F6)"
}

# CSS with improved organization and specificity
st.markdown("""
    <style>
        /* Base styles */
        :root {
            --bg-color: #F5F5F5;
            --text-color: #212121;
            --accent-color: #1E88E5;
            --sidebar-bg: #F5F5F5;
            --border-color: #DEE2E6;
            --input-bg: #F8F9FA;
            --card-bg: #F8F9FA;
            --card-hover-bg: #E9ECEF;
            --shadow-color: rgba(0, 0, 0, 0.1);
        }

        /* App container */
        .stApp {
            background-color: var(--bg-color) !important;
            color: var(--text-color) !important;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: var(--sidebar-bg) !important;
            border-right: 1px solid var(--border-color);
        }
        
        /* Typography */
        .stMarkdown, p, h1, h2, h3 {
            color: var(--text-color) !important;
        }
        
        h1 {
            text-align: center !important;
        }
        
        .main-header {
            text-align: center !important;
            padding: 1rem 0 !important;
            margin-bottom: 2rem !important;
        }
        
        .custom-title {
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            padding: 1rem 0;
            margin-bottom: 2rem;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            width: 100%;
        }
        
        /* Form elements */
        .stSelectbox > div > div,
        .stCheckbox > div > div > label {
            background-color: var(--input-bg) !important;
            color: var(--text-color) !important;
        }
        
        /* Cards */
        .section-card {
            background: var(--card-bg) !important;
            color: var(--text-color) !important;
            box-shadow: 0 4px 6px var(--shadow-color) !important;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            border-left: 5px solid var(--accent-color);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            animation: slideIn 0.5s ease-out;
        }
        
        .section-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
            background: var(--card-hover-bg) !important;
        }

        .section-header {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: var(--accent-color) !important;
        }
        
        /* List styling */
        .custom-bullet {
            margin-left: 20px;
            position: relative;
            color: var(--text-color) !important;
        }
        
        .custom-bullet::before {
            content: "•";
            color: var(--text-color);
            position: absolute;
            left: -15px;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(-20px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes scaleIn {
            from {
                transform: scale(0.95);
                opacity: 0;
            }
            to {
                transform: scale(1);
                opacity: 1;
            }
        }

        /* Particles.js container */
        #particles-js {
            position: fixed !important;
            width: 100vw !important;
            height: 100vh !important;
            top: 0 !important;
            left: 0 !important;
            z-index: -1 !important;
            pointer-events: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# Particles.js implementation
particles_js = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
</head>
<body>
    <div id="particles-js"></div>
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            particlesJS("particles-js", {
                particles: {
                    number: {
                        value: 80,
                        density: {
                            enable: true,
                            value_area: 800
                        }
                    },
                    color: {
                        value: "#1E88E5"
                    },
                    shape: {
                        type: "circle"
                    },
                    opacity: {
                        value: 0.5,
                        random: false,
                        anim: {
                            enable: false
                        }
                    },
                    size: {
                        value: 3,
                        random: true
                    },
                    line_linked: {
                        enable: true,
                        distance: 150,
                        color: "#1E88E5",
                        opacity: 0.4,
                        width: 1
                    },
                    move: {
                        enable: true,
                        speed: 2,
                        direction: "none",
                        random: false,
                        straight: false,
                        out_mode: "out",
                        bounce: false
                    }
                },
                interactivity: {
                    detect_on: "canvas",
                    events: {
                        onhover: {
                            enable: true,
                            mode: "grab"
                        },
                        onclick: {
                            enable: true,
                            mode: "push"
                        },
                        resize: true
                    },
                    modes: {
                        grab: {
                            distance: 140,
                            line_linked: {
                                opacity: 1
                            }
                        },
                        push: {
                            particles_nb: 4
                        }
                    }
                },
                retina_detect: true
            });
        });
    </script>
</body>
</html>
"""

# Inject particles.js into Streamlit
st.components.v1.html(particles_js, height=0)


# First load animations
if 'first_load' not in st.session_state:
    st.session_state.first_load = True

if st.session_state.first_load:
    st.balloons()
    st.snow()
    welcome_placeholder = st.empty()
    welcome_placeholder.success("Welcome to the Geospatial Analysis Tool! 🌍")
    time.sleep(3)
    welcome_placeholder.empty()
    st.session_state.first_load = False

# Set theme variables
st.markdown(f"""
    <style>
        :root {{
            --bg-color: {theme['bg']};
            --text-color: {theme['text']};
            --accent-color: {theme['accent']};
            --gradient: {theme['gradient']};
            --sidebar-bg: {theme['bg']};
            --card-bg: #F8F9FA;
            --card-hover-bg: #E9ECEF;
            --input-bg: #F8F9FA;
            --shadow-color: rgba(0, 0, 0, 0.1);
            --border-color: #DEE2E6;
        }}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>Automated Geospatial Analysis for Sub-National Tailoring of Malaria Interventions</h1>", unsafe_allow_html=True)

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

# Automatic periodic animations
def show_periodic_animations():
    while True:
        time.sleep(60)
        st.balloons()
        time.sleep(10)
        st.snow()

if not hasattr(st.session_state, 'animation_thread'):
    st.session_state.animation_thread = threading.Thread(target=show_periodic_animations)
    st.session_state.animation_thread.daemon = True
    st.session_state.animation_thread.start()
