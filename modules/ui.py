import streamlit as st
import streamlit.components.v1 as components
import base64

def render_custom_audio_player(audio_path, mime_type="audio/mp3"):
    """Renders a custom HTML5 audio player with speed controls."""
    try:
        with open(audio_path, "rb") as f:
            data = f.read()
        b64_data = base64.b64encode(data).decode()
        
        player_id = "audio_player_unique"
        
        html_code = f"""
        <div style="
            background: rgba(15, 23, 42, 0.6); 
            padding: 12px; 
            border-radius: 12px; 
            border: 1px solid rgba(255, 255, 255, 0.1); 
            display: flex; 
            align-items: center; 
            justify-content: space-between;
            gap: 15px; 
            font-family: sans-serif;
            color: white;
        ">
            <audio id="{player_id}" src="data:{mime_type};base64,{b64_data}"></audio>
            
            <div style="display:flex; gap: 10px; align-items: center;">
                <button onclick="document.getElementById('{player_id}').play()" style="
                    background: #a855f7; border:none; color:white; width: 36px; height: 36px; 
                    border-radius: 50%; cursor:pointer; font-size: 16px; display:flex; align-items:center; justify-content:center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                ">▶</button>
                <button onclick="document.getElementById('{player_id}').pause()" style="
                    background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.1); color:white; width: 36px; height: 36px; 
                    border-radius: 50%; cursor:pointer; font-size: 14px; display:flex; align-items:center; justify-content:center;
                ">❚❚</button>
            </div>

            <div style="display:flex; gap: 5px; align-items: center; background: rgba(0,0,0,0.2); padding: 4px; border-radius: 20px;">
                <span style="font-size: 10px; color: #94a3b8; margin: 0 5px; text-transform:uppercase;">Speed</span>
                <button onclick="document.getElementById('{player_id}').playbackRate = 1.0" style="background:transparent; border:none; color:#e2e8f0; font-size:11px; cursor:pointer; padding: 2px 6px;">1x</button>
                <button onclick="document.getElementById('{player_id}').playbackRate = 1.25" style="background:transparent; border:none; color:#e2e8f0; font-size:11px; cursor:pointer; padding: 2px 6px;">1.25x</button>
                <button onclick="document.getElementById('{player_id}').playbackRate = 1.5" style="background:transparent; border:none; color:#e2e8f0; font-size:11px; cursor:pointer; padding: 2px 6px;">1.5x</button>
                <button onclick="document.getElementById('{player_id}').playbackRate = 2.0" style="background:transparent; border:none; color:#e2e8f0; font-size:11px; cursor:pointer; padding: 2px 6px;">2x</button>
            </div>
        </div>
        """
        components.html(html_code, height=70)
    except Exception as e:
        st.error(f"Error loading audio player: {e}")

def load_css(file_path="assets/style.css"):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def card(content, title=None):
    """Renders a card with custom CSS wrapper."""
    html = f"""
    <div class="css-card fade-in">
        {f'<h3>{title}</h3>' if title else ''}
        <p>{content}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_premium_hero():
    """Renders a strikes premium hero section for the landing page."""
    st.markdown("""
    <div class="premium-hero">
        <div style="
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            width: 200px; height: 200px; background: var(--accent); opacity: 0.15; filter: blur(90px); z-index: -1;">
        </div>
        <h1 class="fade-in branding-title">RamXplain</h1>
        <p class="fade-in" style="font-size: 1.3rem; font-weight: 300;">Neural Wisdom & Infinite Mastery.</p>
    </div>
    """, unsafe_allow_html=True)

def render_header():
    """Renders the classy app header for logged-in view."""
    st.markdown("""
    <div style="padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 20px; text-align: left;">
        <h2 style="color: #a855f7; font-weight: 700; font-size: 2rem; margin: 0; letter-spacing: -1.5px;">RamXplain</h2>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    """Renders a minimalist footer."""
    st.markdown("""
    <div class="footer">
        <p>© 2025 RamXplain • Made By Moksha</p>
    </div>
    """, unsafe_allow_html=True)
