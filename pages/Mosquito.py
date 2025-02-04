import streamlit as st

# Page config
st.set_page_config(page_title="Flying Mosquitoes", layout="wide")

# CSS for bouncing mosquitoes
st.markdown("""
    <style>
    /* Container for mosquitoes */
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

    /* Individual mosquito styling */
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

    /* Bounce animations with different patterns */
    @keyframes bounce1 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(100px, -150px) rotate(15deg); }
        50% { transform: translate(200px, 0) rotate(-15deg); }
        75% { transform: translate(100px, 150px) rotate(15deg); }
    }

    @keyframes bounce2 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        33% { transform: translate(-120px, -100px) rotate(-20deg); }
        66% { transform: translate(120px, -100px) rotate(20deg); }
    }

    @keyframes bounce3 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        50% { transform: translate(150px, -200px) rotate(30deg); }
    }

    @keyframes bounce4 {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(-100px, -100px) rotate(-25deg); }
        50% { transform: translate(0, -200px) rotate(0deg); }
        75% { transform: translate(100px, -100px) rotate(25deg); }
    }

    /* Apply different bounce patterns to mosquitoes */
    .mosquito:nth-child(4n+1) {
        animation: appear 0.5s ease forwards, bounce1 4s infinite ease-in-out;
    }
    .mosquito:nth-child(4n+2) {
        animation: appear 0.5s ease forwards, bounce2 5s infinite ease-in-out;
    }
    .mosquito:nth-child(4n+3) {
        animation: appear 0.5s ease forwards, bounce3 6s infinite ease-in-out;
    }
    .mosquito:nth-child(4n+4) {
        animation: appear 0.5s ease forwards, bounce4 7s infinite ease-in-out;
    }
    </style>

    <div class="mosquito-scene">
""", unsafe_allow_html=True)

# Generate 20 mosquitoes with random starting positions
import random

for i in range(20):
    # Randomize starting positions while ensuring good distribution
    top = random.randint(10, 80)
    left = random.randint(10, 80)
    delay = random.uniform(0, 2)  # Random delay for more natural appearance
    
    st.markdown(f"""
        <div class="mosquito" style="
            top: {top}vh;
            left: {left}vw;
            animation-delay: {delay}s, {delay}s;">
            🦟
        </div>
    """, unsafe_allow_html=True)

# Close the mosquito scene div
st.markdown("</div>", unsafe_allow_html=True)

# Page title (optional - can be removed if you want just mosquitoes)
st.title("Bouncing Mosquitoes")
