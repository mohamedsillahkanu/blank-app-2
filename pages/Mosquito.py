import streamlit as st
import time

# Page config
st.set_page_config(page_title="Flying Mosquitoes", layout="wide")

# CSS for mosquito animation and styling
st.markdown("""
    <style>
    /* Mosquito container */
    .mosquito-scene {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 1000;
    }

    /* Individual mosquito styling and animations */
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

    /* Define multiple flight paths */
    @keyframes flight1 {
        0% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(100px, -50px) rotate(10deg); }
        50% { transform: translate(200px, 0) rotate(-10deg); }
        75% { transform: translate(100px, 50px) rotate(10deg); }
        100% { transform: translate(0, 0) rotate(0deg); }
    }

    @keyframes flight2 {
        0% { transform: translate(50px, 50px) rotate(5deg); }
        33% { transform: translate(-50px, -30px) rotate(-15deg); }
        66% { transform: translate(100px, 20px) rotate(15deg); }
        100% { transform: translate(50px, 50px) rotate(5deg); }
    }

    @keyframes flight3 {
        0% { transform: translate(-30px, 30px) rotate(-5deg); }
        50% { transform: translate(150px, -60px) rotate(20deg); }
        100% { transform: translate(-30px, 30px) rotate(-5deg); }
    }

    /* Generate multiple mosquitoes with varied animations */
    .mosquito:nth-child(4n+1) {
        animation: appear 0.5s ease forwards, flight1 5s infinite ease-in-out;
    }
    .mosquito:nth-child(4n+2) {
        animation: appear 0.5s ease forwards, flight2 6s infinite ease-in-out;
    }
    .mosquito:nth-child(4n+3) {
        animation: appear 0.5s ease forwards, flight3 4s infinite ease-in-out;
    }
    .mosquito:nth-child(4n+4) {
        animation: appear 0.5s ease forwards, flight1 7s infinite ease-in-out;
    }
    </style>

    <div class="mosquito-scene">
""", unsafe_allow_html=True)

# Generate 20 mosquitoes with random starting positions
for i in range(20):
    st.markdown(f"""
        <div class="mosquito" style="
            top: {5 + (i * 4.5)}vh;
            left: {(i * 5) % 90}vw;
            animation-delay: {i * 0.1}s, {i * 0.2}s;">
            🦟
        </div>
    """, unsafe_allow_html=True)

# Close the mosquito scene div
st.markdown("</div>", unsafe_allow_html=True)

# Add sound controls
st.markdown("""
    <div style="text-align: center; padding: 20px; background: rgba(255,255,255,0.9); border-radius: 10px; margin: 20px;">
        <h2 style="color: #333;">Mosquito Sound Controls</h2>
        <div style="margin: 20px 0;">
            <button onclick="playMosquitoSound('single')" class="sound-button">
                Single Mosquito 🦟
            </button>
            <button onclick="playMosquitoSound('swarm')" class="sound-button">
                Mosquito Swarm 🦟🦟🦟
            </button>
            <button onclick="stopSound()" class="sound-button">
                Stop Sound ⏹️
            </button>
        </div>
        <div id="soundStatus" style="margin-top: 10px;">Click to start sound</div>
    </div>

    <script>
        let audioCtx;
        let oscillator;
        let isPlaying = false;

        async function playMosquitoSound(type) {
            if (isPlaying) stopSound();
            
            try {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                await audioCtx.resume();
                
                oscillator = audioCtx.createOscillator();
                const gainNode = audioCtx.createGain();
                
                // Configure sound based on type
                const baseFreq = type === 'swarm' ? 700 : 600;
                const volume = type === 'swarm' ? 0.3 : 0.2;
                
                oscillator.type = 'sine';
                oscillator.frequency.setValueAtTime(baseFreq, audioCtx.currentTime);
                gainNode.gain.setValueAtTime(volume, audioCtx.currentTime);
                
                // Wing buzz effect
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
                
                // Start sound
                oscillator.start();
                lfo.start();
                isPlaying = true;
                
                // Add variations
                setInterval(() => {
                    if (isPlaying) {
                        const variation = type === 'swarm' ? Math.random() * 100 : Math.random() * 50;
                        oscillator.frequency.setValueAtTime(baseFreq + variation, audioCtx.currentTime);
                    }
                }, 100);
                
                // Update status
                document.getElementById('soundStatus').textContent = 'Sound playing 🔊';
                
            } catch (error) {
                console.error('Audio error:', error);
                document.getElementById('soundStatus').textContent = 'Error playing sound';
            }
        }

        function stopSound() {
            if (!isPlaying) return;
            
            try {
                oscillator.stop();
                audioCtx.close();
                isPlaying = false;
                document.getElementById('soundStatus').textContent = 'Sound stopped 🔇';
            } catch (error) {
                console.error('Stop sound error:', error);
            }
        }
    </script>
""", unsafe_allow_html=True)

# Main title and description
st.title("Mosquito Swarm Simulator")
st.write("Watch the mosquitoes fly around! Click the buttons below to control the sound.")
