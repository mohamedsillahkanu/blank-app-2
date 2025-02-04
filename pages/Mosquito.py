import streamlit as st

# Set page config
st.set_page_config(page_title="Flying Mosquitoes", layout="wide")

# CSS for mosquito animation
st.markdown("""
    <style>
    @keyframes fly {
        0% {
            transform: translate(0, 0) rotate(0deg);
        }
        25% {
            transform: translate(100px, -50px) rotate(10deg);
        }
        50% {
            transform: translate(200px, 0) rotate(-10deg);
        }
        75% {
            transform: translate(100px, 50px) rotate(10deg);
        }
        100% {
            transform: translate(0, 0) rotate(0deg);
        }
    }

    @keyframes wings {
        0%, 100% { transform: scaleX(1); }
        50% { transform: scaleX(0.5); }
    }

    .mosquito-container {
        position: relative;
        height: 200px;
        width: 100%;
        overflow: hidden;
        background: rgba(240, 240, 240, 0.1);
        border-radius: 8px;
        margin: 20px 0;
    }

    .mosquito {
        position: absolute;
        font-size: 24px;
        animation: fly 4s infinite ease-in-out;
    }

    .wing {
        display: inline-block;
        animation: wings 0.2s infinite ease-in-out;
    }

    /* Multiple mosquitoes with different paths */
    .mosquito:nth-child(1) {
        top: 20%;
        animation-delay: 0s;
    }

    .mosquito:nth-child(2) {
        top: 40%;
        animation-delay: -1s;
        animation-duration: 5s;
    }

    .mosquito:nth-child(3) {
        top: 60%;
        animation-delay: -2s;
        animation-duration: 6s;
    }

    .mosquito:nth-child(4) {
        top: 80%;
        animation-delay: -3s;
        animation-duration: 4.5s;
    }
    </style>
    
    <div class="mosquito-container">
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
    </div>
    """, unsafe_allow_html=True)

st.title("Flying Mosquitoes Animation")
st.write("Watch out for these pesky mosquitoes!")


