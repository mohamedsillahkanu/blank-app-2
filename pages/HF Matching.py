import streamlit as st
import time
import random
import threading

st.set_page_config(page_title="Geospatial Analysis Tool", page_icon="🗺️", layout="wide")

themes = {
    "Black Modern": {
        "bg": "#000000",
        "accent": "#3498db",
        "text": "#FFFFFF",
        "gradient": "linear-gradient(135deg, #3498db, #2ecc71)"
    },
    "Light Silver": {
        "bg": "#F5F5F5",
        "accent": "#1E88E5",
        "text": "#212121",
        "gradient": "linear-gradient(135deg, #1E88E5, #64B5F6)"
    },
    "Light Sand": {
        "bg": "#FAFAFA",
        "accent": "#FF7043",
        "text": "#424242",
        "gradient": "linear-gradient(135deg, #FF7043, #FFB74D)"
    },
    "Light Modern": {
        "bg": "#FFFFFF",
        "accent": "#3498db",
        "text": "#333333",
        "gradient": "linear-gradient(135deg, #3498db, #2ecc71)"
    },
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

def get_base_styles():
    return """
        <style>
            @keyframes mosquito-flight {
                0% { transform: translate(0, 0) rotate(0deg) scale(1); }
                25% { transform: translate(100px, -50px) rotate(45deg) scale(1.2); }
                50% { transform: translate(200px, 0) rotate(90deg) scale(1); }
                75% { transform: translate(100px, 50px) rotate(180deg) scale(0.8); }
                100% { transform: translate(0, 0) rotate(360deg) scale(1); }
            }

            @keyframes star-twinkle {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.5); opacity: 0.3; }
                100% { transform: scale(1); opacity: 1; }
            }

            @keyframes rainfall {
                0% { transform: translateY(-10vh) translateX(0); opacity: 0; }
                10% { opacity: 1; }
                90% { opacity: 1; }
                100% { transform: translateY(110vh) translateX(-20px); opacity: 0; }
            }

            .mosquito {
                position: fixed;
                width: 15px !important;
                height: 15px !important;
                background-color: var(--text-color) !important;
                border-radius: 50%;
                animation: mosquito-flight 8s infinite;
                z-index: 9999;
                opacity: 0.8;
                box-shadow: 0 0 5px rgba(0,0,0,0.5);
                pointer-events: none;
            }

            .mosquito::before,
            .mosquito::after {
                content: '';
                position: absolute;
                width: 12px;
                height: 4px;
                background: var(--text-color);
                opacity: 0.6;
                top: 50%;
                left: 50%;
                transform-origin: left center;
            }

            .mosquito::before {
                transform: translateY(-50%) rotate(45deg);
            }

            .mosquito::after {
                transform: translateY(-50%) rotate(-45deg);
            }

            .star {
                position: fixed;
                width: 3px;
                height: 3px;
                background-color: #FFD700;
                border-radius: 50%;
                animation: star-twinkle 2s infinite;
                z-index: 9998;
                box-shadow: 0 0 5px #FFD700;
                pointer-events: none;
            }

            .raindrop {
                position: fixed;
                width: 2px;
                height: 15px;
                background: linear-gradient(transparent, rgba(135, 206, 235, 0.8));
                animation: rainfall 1.5s linear infinite;
                z-index: 9997;
                pointer-events: none;
            }

            @keyframes confetti {
                0% { transform: translateY(0) rotate(0deg); }
                100% { transform: translateY(100vh) rotate(360deg); }
            }

            .confetti {
                position: fixed;
                animation: confetti 4s linear;
                z-index: 9999;
                pointer-events: none;
            }

            @keyframes sparkle {
                0% { transform: scale(0); opacity: 0; }
                50% { transform: scale(1); opacity: 1; }
                100% { transform: scale(0); opacity: 0; }
            }

            .sparkle {
                position: fixed;
                animation: sparkle 2s infinite;
                z-index: 9999;
                pointer-events: none;
            }

            /* Page Layout Styles */
            .stApp {
                background-color: var(--bg-color) !important;
                color: var(--text-color) !important;
            }

            [data-testid="stSidebar"] {
                background-color: var(--sidebar-bg) !important;
                border-right: 1px solid var(--border-color);
            }

            .stMarkdown, p, h1, h2, h3 {
                color: var(--text-color) !important;
            }

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
                box-shadow: 0 8px 15px var(--shadow-color);
                background: var(--card-hover-bg) !important;
            }

            .section-header {
                font-size: 1.5rem;
                font-weight: bold;
                margin-bottom: 1rem;
                color: var(--accent-color) !important;
            }
        </style>
    """

def create_mosquitoes(count=10):
    for i in range(count):
        left = random.randint(0, 100)
        top = random.randint(20, 80)
        delay = i * 0.5
        st.markdown(f"""
            <div class="mosquito" style="
                left: {left}vw;
                top: {top}vh;
                animation-delay: {delay}s;
                animation-duration: {random.uniform(5, 8)}s;
            "></div>
        """, unsafe_allow_html=True)

def create_stars(count=20):
    for i in range(count):
        left = random.randint(0, 100)
        top = random.randint(0, 40)
        delay = random.uniform(0, 2)
        size = random.uniform(2, 4)
        st.markdown(f"""
            <div class="star" style="
                left: {left}vw;
                top: {top}vh;
                width: {size}px;
                height: {size}px;
                animation-delay: {delay}s;
                animation-duration: {random.uniform(1.5, 3)}s;
            "></div>
        """, unsafe_allow_html=True)

def create_rainfall(count=30):
    for i in range(count):
        left = random.randint(0, 100)
        delay = random.uniform(0, 2)
        st.markdown(f"""
            <div class="raindrop" style="
                left: {left}vw;
                animation-delay: {delay}s;
                animation-duration: {random.uniform(1, 1.5)}s;
            "></div>
        """, unsafe_allow_html=True)

def trigger_all_animations():
    st.balloons()
    st.snow()
    create_mosquitoes()
    create_stars()
    create_rainfall()

def cleanup_animations():
    st.markdown("""
        <style>
            .mosquito, .star, .raindrop {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)
    time.sleep(0.1)

# Initialize session state
if 'animations_initialized' not in st.session_state:
    st.session_state.animations_initialized = False
    st.session_state.theme_index = list(themes.keys()).index("Black Modern")
    st.session_state.first_load = True

# Apply base styles
st.markdown(get_base_styles(), unsafe_allow_html=True)

# Theme selection
selected_theme = st.sidebar.selectbox(
    "🎨 Select Theme",
    list(themes.keys()),
    index=st.session_state.theme_index,
    key='theme_selector'
)

# Theme change handler
if 'previous_theme' not in st.session_state:
    st.session_state.previous_theme = selected_theme

if st.session_state.previous_theme != selected_theme:
    cleanup_animations()
    trigger_all_animations()
    st.session_state.previous_theme = selected_theme

theme = themes[selected_theme]
is_light_theme = "Light" in selected_theme

# Apply theme
st.markdown(f"""
    <style>
        :root {{
            --bg-color: {theme['bg']};
            --text-color: {theme['text']};
            --accent-color: {theme['accent']};
            --gradient: {theme['gradient']};
            --sidebar-bg: {theme['bg']};
            --card-bg: {'#F8F9FA' if is_light_theme else '#1E1E1E'};
            --card-hover-bg: {'#E9ECEF' if is_light_theme else '#2E2E2E'};
            --input-bg: {'#F8F9FA' if is_light_theme else '#1E1E1E'};
            --shadow-color: {f'rgba(0, 0, 0, 0.1)' if is_light_theme else 'rgba(0, 0, 0, 0.3)'};
            --border-color: {'#DEE2E6' if is_light_theme else '#2E2E2E'};
        }}
    </style>
""", unsafe_allow_html=True)

# First load animations
if st.session_state.first_load:
    trigger_all_animations()
    welcome_placeholder = st.empty()
    welcome_placeholder.success("Welcome to the Geospatial Analysis Tool! 🌍")
    time.sleep(3)
    welcome_placeholder.empty()
    st.session_state.first_load = False

# Main content
st.title("Automated Geospatial Analysis for Sub-National Tailoring of Malaria Interventions")

# Map image
st.markdown("""
    <div style="text-align: center;">
        <img src="https://github.com/mohamedsillahkanu/si/raw/b0706926bf09ba23d8e90c394fdbb17e864121d8/Sierra%20Leone%20Map.png" 
             style="width: 50%; max-width: 500px; margin: 20px auto;">
    </div>
""", unsafe_allow_html=True)

# Content sections
sections = {
    "Overview": """Before now, the Sub-National Tailoring (SNT) process took a considerable amount of time to complete analysis. Based on the experience of the 2023 SNT implementation, we have developed an automated tool using the same validated codes with additional enhanced features. This innovation aims to build the capacity of National Malaria Control Program (NMCP) to conduct SNT easily on a yearly basis and monitor activities effectively using this tool.""",
    
    "Objectives": """
    <div class='content-text'>
        The main objectives of implementing automated systems for geospatial analysis and data management are:
        <ul>
            <li>Reduce Time and Effort: Significantly decrease the time required to create maps and analyze data.</li>
            <li>Enhance Skill Accessibility: Provide tools that can be used effectively without extensive training.</li>
            <li>Improve Data Management Efficiency: Streamline processes that currently take days to complete.</li>
            <li>Facilitate Rapid Analysis: Enable automated analysis of datasets within minutes.</li>
        </ul>
    </div>
    """,
    
    "Implementation": """
    <div class='content-text'>
        Key implementation aspects include:
        <ul>
            <li>Development of automated system for simplified geospatial visualizations</li>
            <li>Comprehensive data analysis tools for quick insights</li>
            <li>Training and support for users to maximize tool benefits</li>
        </ul>
    </div>
    """
}

# Render sections
for title, content in sections.items():
    st.markdown(f"""
        <div class="section-card">
            <div class="section-header">{title}</div>
            <div class="content-text">{content}</div>
        </div>
    """, unsafe_allow_html=True)

# Periodic animation handler
def show_periodic_animations():
    while True:
        time.sleep(random.uniform(15, 30))
        if st.session_state.previous_theme == selected_theme:
            random.choice([
                create_mosquitoes,
                create_stars,
                create_rainfall
            ])()

# Start animation thread
if not hasattr(st.session_state, 'animation_thread'):
    st.session_state.animation_thread = threading.Thread(target=show_periodic_animations)
    st.session_state.animation_thread.daemon = True
    st.session_state.animation_thread.start()

# Footer with animation controls
st.markdown("""
    <div style='position: fixed; bottom: 0; left: 0; right: 0; background: var(--bg-color); padding: 10px; text-align: center; border-top: 1px solid var(--border-color);'>
        <p>© 2024 Geospatial Analysis Tool. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)

# Add animation settings to sidebar
with st.sidebar:
    st.markdown("### 🎬 Animation Settings")
    
    # Animation controls
    if st.button("🎯 Trigger New Animations"):
        cleanup_animations()
        trigger_all_animations()
    
    # Animation density controls
    mosquito_count = st.slider("🦟 Mosquito Count", 5, 30, 10)
    star_count = st.slider("⭐ Star Count", 10, 50, 20)
    rain_count = st.slider("🌧️ Rain Density", 10, 50, 30)
    
    # Animation speed
    animation_speed = st.slider("🚀 Animation Speed", 0.5, 2.0, 1.0, 0.1)
    
    # Apply animation settings
    st.markdown(f"""
        <style>
            .mosquito {{
                animation-duration: {8/animation_speed}s !important;
            }}
            .star {{
                animation-duration: {2/animation_speed}s !important;
            }}
            .raindrop {{
                animation-duration: {1.5/animation_speed}s !important;
            }}
        </style>
    """, unsafe_allow_html=True)
    
    # Apply new counts when button is clicked
    if st.button("📱 Apply Settings"):
        cleanup_animations()
        create_mosquitoes(mosquito_count)
        create_stars(star_count)
        create_rainfall(rain_count)

# Theme-specific adjustments
if is_light_theme:
    st.markdown("""
        <style>
            .mosquito {
                background-color: rgba(0, 0, 0, 0.7) !important;
            }
            .mosquito::before,
            .mosquito::after {
                background: rgba(0, 0, 0, 0.7);
            }
            .star {
                box-shadow: 0 0 3px #FFD700;
            }
            .raindrop {
                background: linear-gradient(transparent, rgba(0, 0, 100, 0.4));
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            .mosquito {
                background-color: rgba(255, 255, 255, 0.8) !important;
            }
            .mosquito::before,
            .mosquito::after {
                background: rgba(255, 255, 255, 0.8);
            }
            .star {
                box-shadow: 0 0 5px #FFD700;
            }
            .raindrop {
                background: linear-gradient(transparent, rgba(135, 206, 235, 0.8));
            }
        </style>
    """, unsafe_allow_html=True)

# Dynamic animation adjustments based on theme
def adjust_animations_for_theme(theme_name):
    is_dark = "Dark" in theme_name
    st.markdown(f"""
        <style>
            .mosquito {{
                opacity: {0.8 if is_dark else 0.6};
                box-shadow: 0 0 {8 if is_dark else 5}px rgba({255 if is_dark else 0},
                                                           {255 if is_dark else 0},
                                                           {255 if is_dark else 0},
                                                           0.3);
            }}
            
            .star {{
                opacity: {0.9 if is_dark else 0.7};
            }}
            
            .raindrop {{
                opacity: {0.7 if is_dark else 0.5};
                height: {15 if is_dark else 12}px;
            }}
        </style>
    """, unsafe_allow_html=True)

# Apply theme-specific adjustments
adjust_animations_for_theme(selected_theme)

# Add help tooltip
if st.sidebar.checkbox("Show Help"):
    st.sidebar.markdown("""
        ### 💡 Tips:
        - Use the sliders to adjust animation density
        - Change animation speed to control movement
        - Click 'Trigger New Animations' for fresh effects
        - Switch themes to see different styles
        - Animations will continue automatically
    """)

# Performance optimization
if st.sidebar.checkbox("🚀 Performance Mode", value=False):
    st.markdown("""
        <style>
            .mosquito, .star, .raindrop {
                will-change: transform;
                transform: translateZ(0);
            }
        </style>
    """, unsafe_allow_html=True)
