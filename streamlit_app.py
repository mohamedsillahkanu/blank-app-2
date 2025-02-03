import streamlit as st
import time
import random
import threading

# Set page config first
st.set_page_config(page_title="Geospatial Analysis Tool", page_icon="🗺️", layout="wide")

# Add light theme to the themes dictionary
themes = {
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

# Modified CSS to support both light and dark themes
st.markdown("""
    <style>
        /* Theme-based styling */
        .stApp {
            background-color: var(--bg-color, #0E1117) !important;
            color: var(--text-color, #E0E0E0) !important;
        }
        
        /* Sidebar theming */
        [data-testid="stSidebar"] {
            background-color: var(--sidebar-bg, #1E1E1E) !important;
            border-right: 1px solid var(--border-color, #2E2E2E);
        }
        
        /* Text theming */
        .stMarkdown, p, h1, h2, h3 {
            color: var(--text-color, #E0E0E0) !important;
        }
        
        /* Custom title with theme support */
        .custom-title {
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            padding: 1rem 0;
            margin-bottom: 2rem;
            color: var(--text-color, #E0E0E0) !important;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: block;
            width: 100%;
        }
        
        /* Selectbox theming */
        .stSelectbox > div > div {
            background-color: var(--input-bg, #1E1E1E) !important;
            color: var(--text-color, #E0E0E0) !important;
        }
        
        /* Checkbox theming */
        .stCheckbox > div > div > label {
            color: var(--text-color, #E0E0E0) !important;
        }
        
        /* Section cards with theme support */
        .section-card {
            background: var(--card-bg, #1E1E1E) !important;
            color: var(--text-color, #E0E0E0) !important;
            box-shadow: 0 4px 6px var(--shadow-color, rgba(0, 0, 0, 0.3)) !important;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            border-left: 5px solid var(--accent-color, #3498db);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            animation: slideIn 0.5s ease-out;
        }
        
        .section-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px var(--shadow-color, rgba(0, 0, 0, 0.5));
            background: var(--card-hover-bg, #2E2E2E) !important;
        }

        /* Section header with theme support */
        .section-header {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: var(--accent-color, #3498db) !important;
        }
        
        /* Bullet points with theme support */
        .custom-bullet {
            margin-left: 20px;
            position: relative;
            color: var(--text-color, #E0E0E0) !important;
        }
        .custom-bullet::before {
            content: "•";
            color: var(--text-color, #E0E0E0);
            position: absolute;
            left: -15px;
        }
        
        /* Content text with theme support */
        .content-text {
            color: var(--text-color, #E0E0E0) !important;
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

# Initialize session states
if 'last_animation' not in st.session_state:
    st.session_state.last_animation = time.time()
    st.session_state.theme_index = 0
    st.session_state.first_load = True

# Get selected theme
selected_theme = st.sidebar.selectbox(
    "🎨 Select Theme",
    list(themes.keys()),
    index=st.session_state.theme_index,
    key='theme_selector'
)

# Apply theme
theme = themes[selected_theme]
is_light_theme = "Light" in selected_theme

# Apply theme-specific CSS variables
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

# Rest of your existing code...
# (Welcome animation, content sections, etc. remain the same)

# Title
st.title("Automated Geospatial Analysis for Sub-National Tailoring of Malaria Interventions")

# Image container
st.markdown("""
    <div class="img-container" style="text-align: center;">
        <img src="https://github.com/mohamedsillahkanu/si/raw/b0706926bf09ba23d8e90c394fdbb17e864121d8/Sierra%20Leone%20Map.png" 
             style="width: 50%; max-width: 500px; margin: 20px auto;">
    </div>
""", unsafe_allow_html=True)

# Content Sections
sections = {
    "Overview": """Before now, the Sub-National Tailoring (SNT) process took a considerable amount of time to complete analysis...""",
    "Objectives": """The main objectives of implementing automated systems for geospatial analysis and data management are:...""",
    "Scope": """...""",
    "Target Audience": """...""",
    "Conclusion": """..."""
}

# Display sections with animation delay
for i, (title, content) in enumerate(sections.items()):
    time.sleep(0.2)
    st.markdown(f"""
        <div class="section-card">
            <div class="section-header">{title}</div>
            <div class="content-text">{content}</div>
        </div>
    """, unsafe_allow_html=True)

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
