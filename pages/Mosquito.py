import streamlit as st

# Page config
st.set_page_config(page_title="Flying Mosquitoes", layout="wide")

# CSS for flying mosquitoes
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

    /* Flying animations with different patterns */
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

    /* Apply different flight patterns to mosquitoes */
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
    </style>

    <div class="mosquito-scene">
""", unsafe_allow_html=True)

# Generate 20 mosquitoes with distributed starting positions
import random

for i in range(20):
    # Create distributed starting positions
    row = i // 5  # 4 rows
    col = i % 5   # 5 columns
    
    # Add some randomness to grid positions
    top = 15 + (row * 20) + random.randint(-5, 5)
    left = 15 + (col * 20) + random.randint(-5, 5)
    delay = random.uniform(0, 3)  # Random delay for more natural appearance
    
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
