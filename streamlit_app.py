import streamlit as st
import time
import random
import threading

st.set_page_config(page_title="Geospatial Analysis Tool", page_icon="🗺️", layout="wide")

# [Previous themes dictionary remains unchanged]
themes = {
    "Black Modern": {
        "bg": "#000000",
        "accent": "#3498db",
        "text": "#FFFFFF",
        "gradient": "linear-gradient(135deg, #3498db, #2ecc71)"
    },
    # ... [rest of the themes remain the same]
}

# Define animation functions properly
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
                z-index: 9999;
            }
        </style>
    """, unsafe_allow_html=True)
    for i in range(20):
        left = random.randint(0, 100)
        top = random.randint(0, 100)
        color = f"hsl({random.randint(0, 360)}, 100%, 50%)"
        st.markdown(f"""
            <div class="sparkle" style="left: {left}vw; top: {top}vh; 
            background: {color}; width: 5px; height: 5px; border-radius: 50%;"></div>
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

def show_fireworks():
    animations = [st.balloons, st.snow, show_confetti, show_sparkles]
    random.choice(animations)()

# Initialize session state
if 'last_animation' not in st.session_state:
    st.session_state.last_animation = time.time()
    st.session_state.theme_index = list(themes.keys()).index("Black Modern")
    st.session_state.first_load = True

# [Rest of the CSS styles and main content remain unchanged]
st.markdown("""
    <style>
        /* Main content area styles */
        .stApp {
            background-color: var(--bg-color, #0E1117) !important;
            color: var(--text-color, #E0E0E0) !important;
        }
        /* ... [rest of the styles remain the same] ... */
    </style>
""", unsafe_allow_html=True)

# Animation handling
animations_list = [
    st.balloons,
    st.snow,
    show_confetti,
    show_sparkles,
    show_fireworks,
    lambda: (st.balloons(), st.snow()),
    lambda: (show_confetti(), show_sparkles()),
    lambda: (st.balloons(), show_confetti()),
    lambda: (st.snow(), show_sparkles()),
    lambda: (show_confetti(), st.snow())
]

# Periodic animation thread
if st.sidebar.checkbox("Enable Auto Animations", value=True):
    def show_periodic_animations():
        while True:
            time.sleep(60)  # Wait for 60 seconds
            random.choice(animations_list)()
            time.sleep(10)  # Short delay between animations
            random.choice(animations_list)()

    if not hasattr(st.session_state, 'animation_thread'):
        st.session_state.animation_thread = threading.Thread(
            target=show_periodic_animations, 
            daemon=True
        )
        st.session_state.animation_thread.start()

# Main application content
if st.session_state.first_load:
    st.balloons()
    st.snow()
    welcome_placeholder = st.empty()
    welcome_placeholder.success("Welcome to the Geospatial Analysis Tool! 🌍")
    time.sleep(3)
    welcome_placeholder.empty()
    st.session_state.first_load = False

# Theme selector
selected_theme = st.sidebar.selectbox(
    "🎨 Select Theme",
    list(themes.keys()),
    index=st.session_state.theme_index,
    key='theme_selector'
)

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
            --card-bg: {'#F8F9FA' if is_light_theme else '#1E1E1E'};
            --card-hover-bg: {'#E9ECEF' if is_light_theme else '#2E2E2E'};
            --input-bg: {'#F8F9FA' if is_light_theme else '#1E1E1E'};
            --shadow-color: {f'rgba(0, 0, 0, 0.1)' if is_light_theme else 'rgba(0, 0, 0, 0.3)'};
            --border-color: {'#DEE2E6' if is_light_theme else '#2E2E2E'};
        }}
    </style>
""", unsafe_allow_html=True)

# Main title and description
st.title("Automated Geospatial Analysis for Sub-National Tailoring of Malaria Interventions")

# Map image
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
    "Scope": """The scope includes the development and implementation of an automated system...""",
    "Target Audience": """The target audience includes public health officials and analysts...""",
    "Conclusion": """The adoption of this automated system for SNT analysis represents a transformative opportunity..."""
}

# Render sections with animation delay
for i, (title, content) in enumerate(sections.items()):
    time.sleep(0.2)  # Slight delay for animation effect
    st.markdown(f"""
        <div class="section-card">
            <div class="section-header">{title}</div>
            <div class="content-text">{content}</div>
        </div>
    """, unsafe_allow_html=True)

# Sidebar additional controls
st.sidebar.markdown("### Additional Controls")
if st.sidebar.button("Trigger Animation"):
    random.choice(animations_list)()

# Footer
st.markdown("""
    <div style='text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid var(--border-color);'>
        <p>Developed for National Malaria Control Program (NMCP)</p>
    </div>
""", unsafe_allow_html=True)
