import streamlit as st
import time
import random
import threading

# Page configuration
st.set_page_config(page_title="Geospatial Analysis Tool", page_icon="🗺️", layout="wide")

# Theme definitions
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

# Combined CSS including mosquito animations
st.markdown("""
    <style>
    /* Base styles */
    .stApp {
        background-color: var(--bg-color, #0E1117) !important;
        color: var(--text-color, #E0E0E0) !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg, #1E1E1E) !important;
        border-right: 1px solid var(--border-color, #2E2E2E);
    }
    
    .stMarkdown, p, h1, h2, h3 {
        color: var(--text-color, #E0E0E0) !important;
    }
    
    /* Mosquito Scene */
    .mosquito-scene {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 1000;
        overflow: hidden;
    }

    .mosquito {
        position: absolute;
        font-size: 24px;
        opacity: 0;
        animation: appear 0.5s ease forwards;
    }

    @keyframes appear {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes fly1 {
        0% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(200px, -100px) rotate(10deg); }
        50% { transform: translate(400px, 0) rotate(-10deg); }
        75% { transform: translate(200px, 100px) rotate(10deg); }
        100% { transform: translate(0, 0) rotate(0deg); }
    }

    @keyframes fly2 {
        0% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(-100px, -50px) rotate(-15deg); }
        66% { transform: translate(100px, -100px) rotate(15deg); }
        100% { transform: translate(0, 0) rotate(0deg); }
    }

    @keyframes fly3 {
        0% { transform: translate(0, 0) rotate(0deg); }
        50% { transform: translate(300px, -50px) rotate(20deg); }
        100% { transform: translate(0, 0) rotate(0deg); }
    }

    @keyframes fly4 {
        0% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(-200px, 50px) rotate(-10deg); }
        50% { transform: translate(-400px, 0) rotate(10deg); }
        75% { transform: translate(-200px, -50px) rotate(-10deg); }
        100% { transform: translate(0, 0) rotate(0deg); }
    }

    /* Apply different flight patterns */
    .mosquito:nth-child(4n+1) {
        animation: appear 0.5s ease forwards, fly1 15s infinite ease-in-out;
    }
    .mosquito:nth-child(4n+2) {
        animation: appear 0.5s ease forwards, fly2 12s infinite ease-in-out;
    }
    .mosquito:nth-child(4n+3) {
        animation: appear 0.5s ease forwards, fly3 18s infinite ease-in-out;
    }
    .mosquito:nth-child(4n+4) {
        animation: appear 0.5s ease forwards, fly4 20s infinite ease-in-out;
    }
    
    /* Section and card styles */
    .custom-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
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

# Initialize session state
if 'last_animation' not in st.session_state:
    st.session_state.last_animation = time.time()
    st.session_state.theme_index = list(themes.keys()).index("Light Silver")
    st.session_state.first_load = True

# First load animations and mosquitoes
if st.session_state.first_load:
    # Create mosquito scene
    mosquito_scene = "<div class='mosquito-scene'>"
    for i in range(20):
        # Create distributed starting positions
        row = i // 5  # 4 rows
        col = i % 5   # 5 columns
        top = 15 + (row * 20) + random.randint(-5, 5)
        left = 15 + (col * 20) + random.randint(-5, 5)
        delay = random.uniform(0, 3)
        
        mosquito_scene += f"""
            <div class="mosquito" style="
                top: {top}vh;
                left: {left}vw;
                animation-delay: {delay}s, {delay}s;">
                🦟
            </div>
        """
    mosquito_scene += "</div>"
    
    # Show welcome animations
    st.balloons()
    st.snow()
    welcome_placeholder = st.empty()
    welcome_placeholder.success("Welcome to the Geospatial Analysis Tool! 🌍")
    st.markdown(mosquito_scene, unsafe_allow_html=True)
    time.sleep(3)
    welcome_placeholder.empty()
    st.session_state.first_load = False

# Theme selection
selected_theme = st.sidebar.selectbox(
    "🎨 Select Theme",
    list(themes.keys()),
    index=st.session_state.theme_index,
    key='theme_selector'
)

# Apply selected theme
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
            --input-bg: {'#F8F9FA' if is_light_theme else '#1E1E1E'};
            --shadow-color: {f'rgba(0, 0, 0, 0.1)' if is_light_theme else 'rgba(0, 0, 0, 0.3)'};
            --border-color: {'#DEE2E6' if is_light_theme else '#2E2E2E'};
        }}
    </style>
""", unsafe_allow_html=True)

# Main content
st.title("Automated Geospatial Analysis for Sub-National Tailoring of Malaria Interventions")

# Sierra Leone Map
st.markdown("""
    <div class="img-container" style="text-align: center;">
        <img src="https://github.com/mohamedsillahkanu/si/raw/b0706926bf09ba23d8e90c394fdbb17e864121d8/Sierra%20Leone%20Map.png" 
             style="width: 50%; max-width: 500px; margin: 20px auto;">
    </div>
""", unsafe_allow_html=True)

# Content sections
sections = {
    "Overview": """Before now, the Sub-National Tailoring (SNT) process took a considerable amount of time to complete analysis...""",
    "Objectives": """The main objectives of implementing automated systems for geospatial analysis and data management are...""",
    # ... rest of your sections ...
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

# Animation functions
def show_confetti():
    # ... confetti animation code ...
    pass

def show_sparkles():
    # ... sparkles animation code ...
    pass

def show_fireworks():
    animations = [st.balloons(), st.snow(), show_confetti(), show_sparkles()]
    random.choice(animations)

# Enable auto animations if checked
if st.sidebar.checkbox("Enable Auto Animations", value=True):
    def show_periodic_animations():
        while True:
            time.sleep(60)
            random.choice([st.balloons, st.snow])()
            time.sleep(10)
            random.choice([st.balloons, st.snow])()

    if not hasattr(st.session_state, 'animation_thread'):
        st.session_state.animation_thread = threading.Thread(target=show_periodic_animations)
        st.session_state.animation_thread.daemon = True
        st.session_state.animation_thread.start()
