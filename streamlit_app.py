import streamlit as st
import time
import json
import os
import tempfile
from modules import ui, llm_manager, tts_manager, db_manager, adaptive_logic, auth_manager, export_manager

# Page Config
st.set_page_config(
    page_title="RamXplain",
    layout="wide"
)

# Load CSS (Top level for speed)
ui.load_css()

# Initialize DB
db_manager.init_db()

# --- Authentication & Session State Initialization ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'waiting_for_name' not in st.session_state:
    st.session_state.waiting_for_name = False
if 'cert_name' not in st.session_state:
    st.session_state.cert_name = ""
if 'history' not in st.session_state:
    st.session_state.history = []

# Reload history when project changes
def load_history():
    if st.session_state.logged_in:
        st.session_state.history = db_manager.get_recent_history(
            project_name=st.session_state.current_project, 
            username=st.session_state.username
        )

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    ui.render_premium_hero()
    
    # Tight center layout
    col_auth1, col_auth2, col_auth3 = st.columns([1.2, 2, 1.2])
    
    with col_auth2:
        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
        
        with tab_login:
            with st.form("login_form", border=False):
                login_id = st.text_input("Username")
                login_pass = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Sign In")
                
                if submit_login:
                    success, username = auth_manager.login_user(login_id, login_pass)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success(f"Welcome back, {username}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid Credentials.")

        with tab_signup:
            with st.form("signup_form", border=False):
                new_user = st.text_input("New Username")
                new_email = st.text_input("Email Address")
                new_pass = st.text_input("New Password", type="password")
                submit_signup = st.form_submit_button("Create Account")
                
                if submit_signup:
                    success, msg = auth_manager.signup_user(new_user, new_pass, new_email)
                    if success:
                        st.success(msg + " Please switch to Login tab.")
                    else:
                        st.error(msg)
    
    ui.render_footer()
    st.stop() # Stop execution here if not logged in

# --- MAIN APP (Only runs if logged in) ---

# Verify Project State
if 'projects' not in st.session_state:
    st.session_state.projects = db_manager.get_all_projects(username=st.session_state.username)
if 'current_project' not in st.session_state:
    st.session_state.current_project = "Default"

# Ensure history is loaded
if 'history' not in st.session_state:
    load_history()

if 'messages' not in st.session_state:
    st.session_state.messages = []
# Sidebar
with st.sidebar:
    st.markdown("### 💬 Conversations")
    
    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.session_state.current_concept = None
        st.session_state.cert_name = ""
        st.session_state.waiting_for_name = False
        st.rerun()

    st.markdown("---")
    
    # Render History as Buttons
    if st.session_state.history:
        for hist_id, concept, timestamp, explanation in st.session_state.history:
            col_hist1, col_hist2 = st.columns([4, 1])
            with col_hist1:
                if st.button(f" {concept[:20]}...", key=f"hist_{hist_id}", use_container_width=True):
                    st.session_state.messages = [
                        {"role": "user", "content": concept},
                        {"role": "assistant", "content": explanation}
                    ]
                    st.rerun()
            with col_hist2:
                if st.button(" ✖ ", key=f"del_{hist_id}", help="Delete Chat"):
                    db_manager.delete_history_item(hist_id)
                    load_history()
                    st.rerun()
    else:
        st.caption("No previous chats yet.")

    st.markdown("---")
    # Quick Status in Sidebar (optional, keeping history primarily here)
    if st.session_state.logged_in:
         st.caption(f"🟢 Online: {st.session_state.username}")


# --- MAIN HEADER & OPTIONS ---
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    ui.render_header()
with col_head2:
    # Smaller User Account UI with Dropdown Logout
    # Moved to main view for visibility
    if st.button(f"👤 {st.session_state.username} (Logout)", key="logout_btn", help="Click to Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.projects = []
        st.session_state.history = None
        st.rerun()

# --- CONTROL PANEL (Moved from Sidebar) ---
with st.container():
    st.markdown("#### 🧠 Learning Controls")
    c_mode, c_opts, c_voice = st.columns([1.5, 2, 1])
    
    with c_mode:
        ai_mode = st.selectbox(
            "Select Mode",
            [
                "Normal Tutor",
                "Examiner POV",
                "Forgetting Curve",
                "Explain Like I'm...",
                "Viva Trainer",
                "Study Plan"
            ],
            label_visibility="collapsed"
        )
        st.caption(f"Current: **{ai_mode}**")

    # Dynamic Context Inputs
    context_data = {}
    with c_opts:
        if ai_mode == "Explain Like I'm...":
            persona = st.selectbox("Audience", ["a 10-year-old", "a college student", "an interviewer", "a teacher"])
            context_data['persona'] = persona
        elif ai_mode == "Viva Trainer":
             st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(185, 28, 28, 0.1) 100%); padding: 10px; border-radius: 10px; border: 1px solid rgba(239, 68, 68, 0.3); margin-bottom: 5px;">
                    <div style="font-weight: 700; color: #ef4444; font-size: 0.9rem;">🎙️ VIVA SESSION</div>
                    <div style="font-size: 0.8rem; color: #94a3b8;">Face the examiner's questions! 🔥</div>
                </div>
            """, unsafe_allow_html=True)
             st.session_state.timer_active = False
        else:
            st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.03); padding: 10px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 5px;">
                    <div style="font-weight: 600; color: #94a3b8; font-size: 0.85rem;">⚡ {ai_mode.upper()}</div>
                </div>
            """, unsafe_allow_html=True)
            st.session_state.timer_active = False 

    with c_voice:
        voice_enabled = st.toggle("🔊 Voice", value=False)
        if voice_enabled:
            voice_speed = st.slider("Speed", 100, 250, 150, label_visibility="collapsed")
        else:
            voice_speed = 150

    # Silent defaults (UI controls removed as requested)
    ollama_running = llm_manager.check_ollama()
    ai_provider = "Local (Ollama)"
    selected_model = llm_manager.DEFAULT_MODEL # Dynamically use the model defined in manager
    
    if not ollama_running:
        st.error("🔴 **Local AI (Ollama) is not running.** Please start it to use this app.")
        if st.button("🔄 Retry Connection"):
            st.rerun()
        st.stop()


# --- MAIN INTERFACE: CHATGPT-LIKE UI ---

# Display Chat History
for msg_idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        # Show mode badge for assistant messages
        if message["role"] == "assistant" and "mode" in message:
            st.caption(f"🛡️ Mode: **{message['mode']}**")
        
        # Check if this message contains a quiz - if so, render quiz instead of markdown
        # Check if this message contains a quiz - if so, render quiz instead of markdown
        # Updated: removed has_json check since we now support Text Mode quizzes
        has_quiz_marker = "SYLLABUS PENDING" in message["content"] or "MASTERY ASSESSMENT" in message["content"]
        is_quiz_message = message["role"] ==  "assistant" and has_quiz_marker
        
        if is_quiz_message:
            quiz_items = adaptive_logic.parse_quiz_json(message["content"])
            if quiz_items:
                # Show just the header, not the raw JSON
                if "MASTERY ASSESSMENT:" in message["content"]:
                    # Find the end of the intro text to avoid showing raw Q1 text
                    intro_marker = "study guide."
                    header_end = message["content"].find(intro_marker)
                    if header_end > 0:
                        # Slice exactly at the end of the intro
                        st.markdown(message["content"][:header_end + len(intro_marker)])
                    else:
                        # Fallback if marker not found, show reasonable header
                        st.markdown("### 🏆 MASTERY ASSESSMENT")
                
                st.write("---")
                st.subheader("🏆 Mastery Exam - 5 Questions")
                st.info("Select the best answer for each question below, then submit to get your score!")
                
                user_answers = {}
                for i, q in enumerate(quiz_items):
                    st.write(f"**Q{i+1}: {q['question']}**")
                    user_answers[i] = st.radio(
                        f"Select your answer for Question {i+1}:", 
                        q['options'], 
                        key=f"q_{msg_idx}_{i}",
                        label_visibility="collapsed"
                    )
                    st.write("")  # Add spacing
                
                if st.button("📝 Submit Mastery Exam", key=f"submit_{msg_idx}", type="primary", use_container_width=True):
                    score, results = adaptive_logic.evaluate_quiz(user_answers, quiz_items)
                    st.session_state.quiz_score = score
                    
                    if score >= 60: # Pass threshold
                        success_msg = (
                            f"🎊 **CONGRATULATIONS! YOU HAVE EARNED YOUR CERTIFICATE!** 🎊\n\n"
                            f"You scored **{score:.0f}%** on the Mastery Exam. Your understanding of '{st.session_state.current_concept}' is outstanding.\n\n"
                            "To claim your official certificate, please **type your FULL NAME** in the chat box below."
                        )
                        st.session_state.messages.append({"role": "assistant", "content": success_msg, "mode": ai_mode})
                        st.rerun()
                    else:
                        st.error(f"You scored {score:.0f}%. Don't worry! Knowledge is a journey.")
                        fail_msg = (
                            f"You scored **{score:.0f}%**. To help you reach 100% and earn your certificate, "
                            "I have prepared a comprehensive **3-Level Mastery Guide**. Let's dive deep into the foundations!"
                        )
                        st.session_state.messages.append({"role": "assistant", "content": fail_msg, "mode": ai_mode})
                        
                        # Automatically trigger the guide by adding a hidden-ish user request
                        st.session_state.messages.append({
                            "role": "user", 
                            "content": f"I need to prepare more. Please provide the full EXHAUSTIVE 3-Level Mastery Guide for {st.session_state.current_concept}."
                        })
                        st.rerun()
            else:
                # Quiz message but JSON parsing failed or incomplete
                if "SYLLABUS PENDING" in message["content"]:
                     # Generation finished but parsing failed -> Show error and raw content
                     st.error("⚠️ Error: The AI generated a quiz, but the format could not be parsed. Showing raw output below:")
                     st.text(message["content"])
                else:
                    # Generation in progress -> Show loading state instead of raw JSON
                    st.info("🧠 Generating Quiz Questions... (Please wait)")
                    # Show partial intro if available
                    if "MASTERY ASSESSMENT:" in message["content"]:
                         header_end = message["content"].find("I will evaluate")
                         if header_end > 0:
                             st.markdown(message["content"][:header_end + 200])
        else:
            # Normal message, not a quiz
            st.markdown(message["content"])
        
        if message["role"] == "assistant" and "**Foundation Check:**" not in message["content"] and "### 🎓 Readiness Check" not in message["content"]:
            # Use current concept name
            concept_name = st.session_state.get('current_concept', 'Concept')[:30]

            # Use the mode stored with the message for the PDF
            msg_mode = message.get("mode", ai_mode)
            pdf_data = export_manager.generate_concept_pdf(concept_name, message["content"], mode=msg_mode)
            st.download_button(
                label="📥 Download PDF",
                data=pdf_data,
                file_name=f"RamXplain_{concept_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                key=f"dl_pdf_{hash(message['content'] + msg_mode)}"
            )

        # Certificate Claim Logic
        if message["role"] == "assistant" and "CONGRATULATIONS! YOU HAVE EARNED YOUR CERTIFICATE!" in message["content"]:
            # Check if we should ask for name
            if "type your FULL NAME" in message["content"] and not st.session_state.cert_name:
                st.session_state.waiting_for_name = True
                st.info("✍️ **Almost there!** Please type your **Full Name** in the chat box below to generate your certificate.")
            
            if st.session_state.cert_name:
                st.success(f"🎉 **MASTER ACHIEVED!** Certificate ready for **{st.session_state.cert_name}**")
                
                # Determine topic for certificate
                cert_topic = st.session_state.get('current_concept', 'Advanced Mastery').title()
                cert_pdf = export_manager.generate_certificate_pdf(st.session_state.cert_name, cert_topic)
                
                # Glowing button container
                st.markdown("""
                    <style>
                    @keyframes pulse-gold {
                        0% { box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.7); }
                        70% { box-shadow: 0 0 0 15px rgba(251, 191, 36, 0); }
                        100% { box-shadow: 0 0 0 0 rgba(251, 191, 36, 0); }
                    }
                    .glow-btn button {
                        animation: pulse-gold 2s infinite;
                        border: 2px solid #fbbf24 !important;
                        background: linear-gradient(135deg, #fbbf24, #d97706) !important;
                        color: black !important;
                        font-weight: 800 !important;
                        padding: 15px 30px !important;
                        font-size: 1.1rem !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="glow-btn">', unsafe_allow_html=True)
                st.download_button(
                    label="🎓 CLAIM MY OFFICIAL CERTIFICATE",
                    data=cert_pdf,
                    file_name=f"Mastery_Certificate_{st.session_state.cert_name.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    key=f"cert_btn_{hash(message['content'] + st.session_state.cert_name)}"
                )
                st.markdown('</div>', unsafe_allow_html=True)
                st.balloons()

# Mastery Pathway Interactive Controls (Removed duplicate, now handled inside chat loop)

# Chat Input
input_placeholder = "Ask about any concept..."
if ai_mode == "Viva Trainer":
    input_placeholder = "Answer the viva question..."

if prompt := st.chat_input(input_placeholder):
    # Handle Certificate Name Capture
    if st.session_state.waiting_for_name:
        st.session_state.cert_name = prompt
        st.session_state.waiting_for_name = False
        st.rerun()

    # Set current concept if not set
    if 'current_concept' not in st.session_state or not st.session_state.current_concept:
        st.session_state.current_concept = prompt

    # Add User Message to History
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant Response
    with st.chat_message("assistant"):
        # Default Settings (since selectors are removed)
        eff_difficulty = "Information Dense" # Still saved to DB but mostly legacy now
        eff_marks = ai_mode # Saving mode as 'marks' column for context in history

        
        # Pre-append empty assistant message for live updates
        st.session_state.messages.append({"role": "assistant", "content": "", "mode": ai_mode})
        assistant_msg_idx = len(st.session_state.messages) - 1
        
        response_placeholder = st.empty()
        full_response = ""
        
        # Generation Placeholder with STOP button
        status_container = st.empty()
        with status_container.container():
            col_stat, col_stop = st.columns([3, 1])
            col_stat.write("✨ *Generating explanation...*")
            if col_stop.button("⏹ Stop", key=f"stop_{assistant_msg_idx}"):
                # Save partial response before stopping
                if full_response:
                    db_manager.save_learning_history(
                        prompt, eff_marks, eff_difficulty, full_response, 
                        st.session_state.current_project, st.session_state.username
                    )
                st.rerun()
        
        # Error handling during generation
        try:
            # Create the streaming generator with chat history
            explanation_generator = llm_manager.generate_explanation(
                st.session_state.get('current_concept', prompt), 
                mode=ai_mode, 
                context_data=context_data, 
                model=selected_model, 
                provider=ai_provider,
                chat_history=st.session_state.messages # Pass full history including the current prompt
            )
            
            # Stream the response
            for chunk in explanation_generator:
                full_response += chunk
                # Live update the message in session state so it persists if stopped
                st.session_state.messages[assistant_msg_idx]["content"] = full_response
                
                # Intelligent Streaming Logic
                is_quiz_stream = "MASTERY ASSESSMENT:" in full_response
                if is_quiz_stream and "SYLLABUS PENDING" not in full_response:
                    # While generating quiz, do not show raw JSON
                    # Robustly find the end of the intro text
                    if "```" in full_response:
                        safe_view = full_response.split("```")[0]
                    else:
                        header_end = full_response.find("study guide.")
                        if header_end != -1:
                             safe_view = full_response[:header_end + 12] # Include "study guide."
                        else:
                             safe_view = full_response # Fallback
                    
                    # Add a simple activity indicator based on length
                    indicator = ["🌑", "qc", "🌕", "🌗"]
                    anim_idx = (len(full_response) // 10) % 4
                    response_placeholder.markdown(safe_view + f"\n\n🚀 _Generating Quiz... {indicator[anim_idx]}_")
                else:
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            status_container.empty() # Remove generating status and stop button
            
            # If this was a quiz, we MUST rerun to parse the text and show buttons
            if "MASTERY ASSESSMENT:" in full_response and "SYLLABUS PENDING" in full_response:
                st.rerun()
                
            if not full_response:
                st.error("AI returned an empty response. Please check if your Ollama model is fully loaded and responding.")
                st.session_state.messages.pop() # Remove the empty message if failed
            else:
                # Already added to session state during stream
                pass
                
                # Save to DB
                db_manager.save_learning_history(
                    prompt, eff_marks, eff_difficulty, full_response, 
                    st.session_state.current_project, st.session_state.username
                )
                load_history() # Refresh sidebar
                
                # Voice Trigger (Optional)
                if voice_enabled:
                    with st.spinner("Preparing Audio..."):
                        tts = tts_manager.TTSManager()
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                            tmp_path = f.name
                        if tts.save_to_file(full_response, tmp_path, rate=voice_speed):
                             ui.render_custom_audio_player(tmp_path)
                             os.unlink(tmp_path)

        except Exception as e:
            st.error(f"Generation Error: {str(e)}")


# AI continues to support clarity and retention after each response


# Render Footer
ui.render_footer()
