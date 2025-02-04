import streamlit as st

# Set page config
st.set_page_config(page_title="Flying Mosquitoes", layout="wide")

# CSS and HTML for mosquito animation with sound
st.markdown("""
    <style>
    @keyframes fly {
        0% {
            transform: translate(0, 0) rotate(0deg);
            filter: volume(0.5);
        }
        25% {
            transform: translate(100px, -50px) rotate(10deg);
            filter: volume(1);
        }
        50% {
            transform: translate(200px, 0) rotate(-10deg);
            filter: volume(0.7);
        }
        75% {
            transform: translate(100px, 50px) rotate(10deg);
            filter: volume(0.9);
        }
        100% {
            transform: translate(0, 0) rotate(0deg);
            filter: volume(0.5);
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

    .mosquito:nth-child(1) { top: 20%; animation-delay: 0s; }
    .mosquito:nth-child(2) { top: 40%; animation-delay: -1s; animation-duration: 5s; }
    .mosquito:nth-child(3) { top: 60%; animation-delay: -2s; animation-duration: 6s; }
    .mosquito:nth-child(4) { top: 80%; animation-delay: -3s; animation-duration: 4.5s; }

    .sound-button {
        background-color: #FF7043;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        margin: 10px 0;
    }

    .sound-button:hover {
        background-color: #FFB74D;
    }
    </style>
    
    <script>
    // Create audio context and oscillator for mosquito sound
    let audioCtx;
    let oscillator;
    
    function startMosquitoSound() {
        // Initialize audio context
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        
        // Create oscillator for basic tone
        oscillator = audioCtx.createOscillator();
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(600, audioCtx.currentTime);
        
        // Create gain node for volume control
        const gainNode = audioCtx.createGain();
        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
        
        // Create LFO for frequency modulation (wing buzz)
        const lfo = audioCtx.createOscillator();
        lfo.type = 'sine';
        lfo.frequency.setValueAtTime(30, audioCtx.currentTime);
        
        const lfoGain = audioCtx.createGain();
        lfoGain.gain.setValueAtTime(20, audioCtx.currentTime);
        
        // Connect nodes
        lfo.connect(lfoGain);
        lfoGain.connect(oscillator.frequency);
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        
        // Start oscillators
        oscillator.start();
        lfo.start();
        
        // Add random frequency variations
        setInterval(() => {
            oscillator.frequency.setValueAtTime(
                600 + Math.random() * 50,
                audioCtx.currentTime
            );
        }, 100);
    }
    
    function stopMosquitoSound() {
        if (oscillator) {
            oscillator.stop();
            audioCtx.close();
        }
    }
    </script>
    
    <div class="mosquito-container">
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
        <div class="mosquito">🦟</div>
    </div>
    
    <button class="sound-button" onclick="startMosquitoSound()">Start Buzzing</button>
    <button class="sound-button" onclick="stopMosquitoSound()">Stop Buzzing</button>
    """, unsafe_allow_html=True)

st.title("Flying Mosquitoes with Sound")
st.write("Watch (and hear) these pesky mosquitoes! Click the button to start/stop the buzzing sound.")

# Add some interactive elements
if st.button("Add More Mosquitoes"):
    st.snow()
    st.markdown("""
        <div class="mosquito-container">
            <div class="mosquito">🦟</div>
            <div class="mosquito">🦟</div>
            <div class="mosquito">🦟</div>
            <div class="mosquito">🦟</div>
        </div>
    """, unsafe_allow_html=True)

st.warning("Make sure your sound is on and click 'Start Buzzing' to hear the mosquitoes!")
