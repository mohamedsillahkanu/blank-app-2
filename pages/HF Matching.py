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

st.markdown("""
    <style>
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
        
        .stSelectbox > div > div {
            background-color: var(--input-bg, #1E1E1E) !important;
            color: var(--text-color, #E0E0E0) !important;
        }
        
        .stCheckbox > div > div > label {
            color: var(--text-color, #E0E0E0) !important;
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
            background: var(--card-hover-bg, #2E2E2E) !important;
        }

        .section-header {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: var(--accent-color, #3498db) !important;
        }
        
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
        
        .content-text {
            color: var(--text-color, #E0E0E0) !important;
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

        /* New Animation Styles */
        @keyframes mosquito-flight {
            0% { transform: translate(0, 0) rotate(0deg); }
            25% { transform: translate(10px, 10px) rotate(90deg); }
            50% { transform: translate(0, 20px) rotate(180deg); }
            75% { transform: translate(-10px, 10px) rotate(270deg); }
            100% { transform: translate(0, 0) rotate(360deg); }
        }
        
        @keyframes star-twinkle {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.3; transform: scale(0.8); }
        }
        
        @keyframes rainfall {
            0% { transform: translateY(-100vh); }
            100% { transform: translateY(100vh); }
        }
        
        .mosquito {
            position: fixed;
            width: 8px;
            height: 8px;
            background-color: rgba(0, 0, 0, 0.6);
            border-radius: 50%;
            animation: mosquito-flight 4s infinite;
            z-index: 9999;
        }
        
        .star {
            position: fixed;
            width: 4px;
            height: 4px;
            background-color: #FFD700;
            border-radius: 50%;
            animation: star-twinkle 2s infinite;
            z-index: 9999;
        }
        
        .raindrop {
            position: fixed;
            width: 2px;
            height: 10px;
            background: linear-gradient(transparent, rgba(135, 206, 235, 0.5));
            animation: rainfall 1s linear infinite;
            z-index: 9999;
        }

        @keyframes confetti {
            0% { transform: translateY(0) rotate(0deg); }
            100% { transform: translateY(100vh) rotate(360deg); }
        }
        
        .confetti {
            position: fixed;
            animation: confetti 4s linear;
            z-index: 9999;
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
        }
    </style>
""", unsafe_allow_html=True)

# Animation Functions
def show_mosquitoes():
    for i in range(15):
        left = random.randint(0, 100)
        top = random.randint(0, 100)
        delay = random.random() * 4
        st.markdown(f"""
            <div class="mosquito" style="left: {left}vw; top: {top}vh; 
            animation-delay: {delay}s;"></div>
        """, unsafe_allow_html=True)

def show_stars():
    for i in range(30):
        left = random.randint(0, 100)
        top = random.randint(0, 30)
        delay = random.random() * 2
        st.markdown(f"""
            <div class="star" style="left: {left}vw; top: {top}vh; 
            animation-delay: {delay}s;"></div>
        """, unsafe_allow_html=True)

def show_rainfall():
    for i in range(50):
        left = random.randint(0, 100)
        delay = random.random()
        st.markdown(f"""
            <div class="raindrop" style="left: {left}vw; 
            animation-delay: {delay}s;"></div>
        """, unsafe_allow_html=True)

def show_confetti():
    for i in range(50):
        color = f"hsl({random.randint(0, 360)}, 100%, 50%)"
        left = random.randint(0, 100)
        st.markdown(f"""
            <div class="confetti" style="left: {left}vw; background: {color}; 
            width: 10px; height: 10px; border-radius: 50%;"></div>
        """, unsafe_allow_html=True)

def show_sparkles():
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

# Initialize session state
if 'last_animation' not in st.session_state:
    st.session_state.last_animation = time.time()
    st.session_state.theme_index = list(themes.keys()).index("Black Modern")
    st.session_state.first_load = True

# First load animations
if st.session_state.first_load:
    st.balloons()
    st.snow()
    show_mosquitoes()
    show_stars()
    welcome_placeholder = st.empty()
    welcome_placeholder.success("Welcome to the Geospatial Analysis Tool! 🌍")
    time.sleep(3)
    welcome_placeholder.empty()
    st.session_state.first_load = False

# Theme selection and animation
current_time = time.time()
if current_time - st.session_state.last_animation >= 30:
    st.session_state.last_animation = current_time
    theme_keys = list(themes.keys())
    st.session_state.theme_index = (st.session_state.theme_index + 1) % len(theme_keys)
    random.choice([st.balloons, st.snow, show_mosquitoes, show_stars, show_rainfall])()

selected_theme = st.sidebar.selectbox(
    "🎨 Select Theme",
    list(themes.keys()),
    index=st.session_state.theme_index,
    key='theme_selector'
)

# Updated animations list
animations_list = [
    st.balloons,
    st.snow,
    show_confetti,
    show_sparkles,
    show_fireworks,
    show_mosquitoes,
    show_stars,
    show_rainfall,
    lambda: [st.balloons(), show_mosquitoes()],
    lambda: [st.snow(), show_stars()],
    lambda: [show_rainfall(), show_mosquitoes()],
    lambda: [show_stars(), show_sparkles()],
    lambda: [show_mosquitoes(), show_rainfall(), show_stars()]
]

# Theme change animation
if 'previous_theme' not in st.session_state:
    st.session_state.previous_theme = selected_theme
if st.session_state.previous_theme != selected_theme:
    random.choice(animations_list)()
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

# Main content
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

# Render sections with animations
for i, (title, content) in enumerate(sections.items()):
    time.sleep(0.2)  # Slight delay for animation effect
    st.markdown(f"""
        <div class="section-card">
            <div class="section-header">{title}</div>
            <div class="content-text">{content}</div>
        </div>
    """, unsafe_allow_html=True)

# Periodic animations
if st.sidebar.checkbox("Enable Auto Animations", value=True):
    def show_periodic_animations():
        while True:
            time.sleep(60)  # Wait for 60 seconds
            random.choice(animations_list)()
            time.sleep(10)  # Short delay between animations
            random.choice(animations_list)()  # Show another animation

    # Start animation thread if not already running
    if not hasattr(st.session_state, 'animation_thread'):
        st.session_state.animation_thread = threading.Thread(target=show_periodic_animations)
        st.session_state.animation_thread.daemon = True  # Set as daemon thread
        st.session_state.animation_thread.start()

# Add sidebar controls for animation settings
with st.sidebar:
    st.markdown("### 🎬 Animation Controls")
    if st.button("Trigger Random Animation"):
        random.choice(animations_list)()
    
    animation_speed = st.slider("Animation Speed", 0.5, 2.0, 1.0, 0.1)
    st.markdown(f"""
        <style>
            .mosquito, .star, .raindrop {{
                animation-duration: {1/animation_speed}s !important;
            }}
        </style>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
    <div style='text-align: center; margin-top: 50px; padding: 20px;'>
        <p>© 2024 Geospatial Analysis Tool. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)
