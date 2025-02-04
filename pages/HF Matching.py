import streamlit as st
import time
import random
import threading

st.set_page_config(page_title="Geospatial Analysis Tool", page_icon="🗺️", layout="wide")

# Define themes
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
    }
}

# Base styles and animations
st.markdown("""
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
            position: fixed !important;
            width: 20px !important;
            height: 20px !important;
            background-color: black !important;
            border-radius: 50%;
            animation: mosquito-flight 8s infinite;
            z-index: 9999 !important;
            opacity: 0.8 !important;
            box-shadow: 0 0 5px rgba(0,0,0,0.5);
            pointer-events: none;
            display: block !important;
            visibility: visible !important;
        }

        .mosquito::before,
        .mosquito::after {
            content: '';
            position: absolute;
            width: 16px !important;
            height: 6px !important;
            background: black !important;
            opacity: 0.8 !important;
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
            position: fixed !important;
            width: 4px !important;
            height: 4px !important;
            background-color: #FFD700 !important;
            border-radius: 50%;
            animation: star-twinkle 2s infinite;
            z-index: 9998 !important;
            box-shadow: 0 0 8px #FFD700 !important;
            pointer-events: none;
            display: block !important;
            visibility: visible !important;
        }

        .raindrop {
            position: fixed !important;
            width: 3px !important;
            height: 20px !important;
            background: linear-gradient(transparent, rgba(135, 206, 235, 0.9)) !important;
            animation: rainfall 1.5s linear infinite;
            z-index: 9997 !important;
            pointer-events: none;
            display: block !important;
            visibility: visible !important;
        }

        /* Page styles */
        .stApp {
            background-color: var(--bg-color) !important;
            color: var(--text-color) !important;
        }

        [data-testid="stSidebar"] {
            background-color: var(--sidebar-bg) !important;
            border-right: 1px solid var(--border-color);
        }

        .section-card {
            background: var(--card-bg) !important;
            color: var(--text-color) !important;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            border-left: 5px solid var(--accent-color);
            transition: transform 0.3s ease;
        }
    </style>
""", unsafe_allow_html=True)

# Animation creation functions
def create_mosquitoes(count=15):
    for i in range(count):
        left = random.randint(0, 100)
        top = random.randint(20, 80)
        delay = i * 0.2
        st.markdown(f"""
            <div class="mosquito" style="
                left: {left}vw;
                top: {top}vh;
                animation-delay: {delay}s;
                animation-duration: {random.uniform(3, 5)}s;
            "></div>
        """, unsafe_allow_html=True)

def create_stars(count=25):
    for i in range(count):
        left = random.randint(0, 100)
        top = random.randint(0, 40)
        delay = random.uniform(0, 1)
        size = random.uniform(3, 5)
        st.markdown(f"""
            <div class="star" style="
                left: {left}vw;
                top: {top}vh;
                width: {size}px;
                height: {size}px;
                animation-delay: {delay}s;
                animation-duration: {random.uniform(1, 2)}s;
            "></div>
        """, unsafe_allow_html=True)

def create_rainfall(count=35):
    for i in range(count):
        left = random.randint(0, 100)
        delay = random.uniform(0, 1)
        st.markdown(f"""
            <div class="raindrop" style="
                left: {left}vw;
                animation-delay: {delay}s;
                animation-duration: {random.uniform(0.8, 1.2)}s;
            "></div>
        """, unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.theme_index = 0

# Start animations immediately
if not st.session_state.initialized:
    create_mosquitoes()
    create_stars()
    create_rainfall()
    st.session_state.initialized = True

# Theme selection
selected_theme = st.sidebar.selectbox(
    "🎨 Select Theme",
    list(themes.keys()),
    index=st.session_state.theme_index
)

if 'previous_theme' not in st.session_state:
    st.session_state.previous_theme = selected_theme

# Theme change handler
if st.session_state.previous_theme != selected_theme:
    create_mosquitoes()
    create_stars()
    create_rainfall()
    st.session_state.previous_theme = selected_theme

# Apply theme
theme = themes[selected_theme]
is_light_theme = "Light" in selected_theme

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
            --shadow-color: {f'rgba(0, 0, 0, 0.1)' if is_light_theme else 'rgba(0, 0, 0, 0.3)'};
            --border-color: {'#DEE2E6' if is_light_theme else '#2E2E2E'};
        }}
    </style>
""", unsafe_allow_html=True)

# Periodic animation thread
def show_periodic_animations():
    while True:
        try:
            time.sleep(15)
            create_mosquitoes()
            time.sleep(5)
            create_stars()
            time.sleep(5)
            create_rainfall()
        except:
            pass

# Start animation thread
if 'animation_thread' not in st.session_state:
    st.session_state.animation_thread = threading.Thread(target=show_periodic_animations)
    st.session_state.animation_thread.daemon = True
    st.session_state.animation_thread.start()

# Main content
st.title("Automated Geospatial Analysis Tool")

# Content sections
sections = {
    "Overview": """This tool provides automated geospatial analysis capabilities.""",
    "Features": """
    <ul>
        <li>Automated data processing</li>
        <li>Interactive visualizations</li>
        <li>Real-time analysis</li>
    </ul>
    """,
    "Benefits": """
    <ul>
        <li>Faster decision making</li>
        <li>Improved accuracy</li>
        <li>Better insights</li>
    </ul>
    """
}

# Render sections
for title, content in sections.items():
    st.markdown(f"""
        <div class="section-card">
            <h2>{title}</h2>
            <div>{content}</div>
        </div>
    """, unsafe_allow_html=True)
