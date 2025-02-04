import streamlit as st

# Set page config
st.set_page_config(page_title="Flying Mosquitoes", layout="wide")

# CSS and HTML for mosquito animation with sound
st.markdown("""
    <style>
    @keyframes fly1 {
        0% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(100px, -50px) rotate(10deg); }
        50% { transform: translate(200px, 0) rotate(-10deg); }
        75% { transform: translate(100px, 50px) rotate(10deg); }
        100% { transform: translate(0, 0) rotate(0deg); }
    }

    @keyframes fly2 {
        0% { transform: translate(50px, 20px) rotate(5deg); }
        33% { transform: translate(150px, -30px) rotate(-15deg); }
        66% { transform: translate(250px, 40px) rotate(15deg); }
        100% { transform: translate(50px, 20px) rotate(5deg); }
    }

    @keyframes fly3 {
        0% { transform: translate(-50px, -20px) rotate(-5deg); }
        33% { transform: translate(100px, 40px) rotate(20deg); }
        66% { transform: translate(180px, -40px) rotate(-20deg); }
        100% { transform: translate(-50px, -20px) rotate(-5deg); }
    }

    .mosquito-container {
        position: relative;
        height: 400px;
        width: 100%;
        overflow: hidden;
        background: rgba(240, 240, 240, 0.1);
        border-radius: 8px;
        margin: 20px 0;
    }

    .mosquito {
        position: absolute;
        font-size: 24px;
    }

    /* Generate 20 mosquitoes with different positions and animations */
    .mosquito:nth-child(1) { top: 5%; left: 10%; animation: fly1 4s infinite ease-in-out; }
    .mosquito:nth-child(2) { top: 15%; left: 20%; animation: fly2 5s infinite ease-in-out; }
    .mosquito:nth-child(3) { top: 25%; left: 15%; animation: fly3 4.5s infinite ease-in-out; }
    .mosquito:nth-child(4) { top: 35%; left: 25%; animation: fly1 5.5s infinite ease-in-out; }
    .mosquito:nth-child(5) { top: 45%; left: 30%; animation: fly2 4.8s infinite ease-in-out; }
    .mosquito:nth-child(6) { top: 55%; left: 35%; animation: fly3 5.2s infinite ease-in-out; }
    .mosquito:nth-child(7) { top: 65%; left: 40%; animation: fly1 4.2s infinite ease-in-out; }
    .mosquito:nth-child(8) { top: 75%; left: 45%; animation: fly2 5.8s infinite ease-in-out; }
    .mosquito:nth-child(9) { top: 85%; left: 50%; animation: fly3 4.7s infinite ease-in-out; }
    .mosquito:nth-child(10) { top: 10%; left: 55%; animation: fly1 5.3s infinite ease-in-out; }
    .mosquito:nth-child(11) { top: 20%; left: 60%; animation: fly2 4.6s infinite ease-in-out; }
    .mosquito:nth-child(12) { top: 30%; left: 65%; animation: fly3 5.4s infinite ease-in-out; }
    .mosquito:nth-child(13) { top: 40%; left: 70%; animation: fly1 4.9s infinite ease-in-out; }
    .mosquito:nth-child(14) { top: 50%; left: 75%; animation: fly2 5.1s infinite ease-in-out; }
    .mosquito:nth-child(15) { top: 60%; left: 80%; animation: fly3 4.4s infinite ease-in-out; }
    .mosquito:nth-child(16) { top: 70%; left: 85%; animation: fly1 5.6s infinite ease-in-out; }
    .mosquito:nth-child(17) { top: 80%; left: 90%; animation: fly2 4.3s infinite ease-in-out; }
    .mosquito:nth-child(18) { top: 90%; left: 95%; animation: fly3 5.7s infinite ease-in-out; }
    .mosquito:nth-child(19) { top: 15%; left: 40%; animation: fly1 4.1s infinite ease-in-out; }
    .mosquito:nth-child(20) { top: 25%; left: 50%; animation: fly2 5.9s infinite ease-in-out; }


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
    let audioCtx;
    let oscillator;
    let isPlaying = false;
    
    function playMosquitoSound() {
        if (isPlaying) return;
        
        try {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            oscillator = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();
            
            // Set up oscillator
            oscillator.type = 'sine';
            oscillator.frequency.setValueAtTime(600, audioCtx.currentTime);
            
            // Set volume
            gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
            
            // Create wing buzz effect
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
            
            // Add random variations
            const variationInterval = setInterval(() => {
                if (isPlaying) {
                    oscillator.frequency.setValueAtTime(
                        600 + Math.random() * 50,
                        audioCtx.currentTime
                    );
                }
            }, 100);
            
            // Stop after 1 minute
            setTimeout(() => {
                if (isPlaying) {
                    clearInterval(variationInterval);
                    stopSound();
                }
            }, 60000);  // 60 seconds
        } catch (error) {
            console.error('Audio error:', error);
        }
    }
    
    function stopSound() {
        if (!isPlaying) return;
        
        try {
            oscillator.stop();
            audioCtx.close();
            isPlaying = false;
        } catch (error) {
            console.error('Stop sound error:', error);
        }
    }

    // Auto-start sound on page interaction
    document.addEventListener('click', function initSound() {
        playMosquitoSound();
        document.removeEventListener('click', initSound);
    }, { once: true });
    </script>
    
    <div style="text-align: center; padding: 10px; background-color: #FFE0B2; border-radius: 4px; margin-bottom: 10px;">
        Click anywhere to start the mosquito sound! It will play for 1 minute.
    </div>
        
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
    
    <button class="sound-button" onclick="startMosquitoSound()">Start Buzzing</button>
    <button class="sound-button" onclick="stopMosquitoSound()">Stop Buzzing</button>
    """, unsafe_allow_html=True)

st.title("Flying Mosquitoes with Auto Sound")
st.write("A swarm of mosquitoes will buzz for 1 minute when you click anywhere on the page!")

# Add warning about sound
st.warning("👉 Click anywhere on the page to start the mosquito buzzing sound. The sound will automatically stop after 1 minute.")

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
