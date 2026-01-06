# 🧠 RamXplain: The Ultimate Offline AI Learning Ecosystem

**RamXplain** is a state-of-the-art, offline-first AI tutor designed to transform complex topics into deep, intuitiveknowledge. Powered by local LLMs (**Ollama**) , it offers a secure, private, and highly personalized learning experience wrapped in a stunning **Premium Dark UI**.

---

## 🌟 Key Features

### Premium User Experience
*   **Cinematic Interface**: A "Glassmorphism" design system with animated gradients and lucid transparency effects.
*   **Adaptive Theme**: High-contrast dark mode optimized for long study sessions.
*   **Responsive Layout**: Fully optimized single-screen view for focused learning without infinite scrolling.

### 🎓 Advanced Learning Modes

*   **Examiner POV**: Get feedback on your concepts from the perspective of an academic grader.
*   **Viva Trainer**: Interactive oral exam simulation to prepare you for interviews and presentations.
*   **Explain Like I'm...**: Tailor explanations for any audience—from a 10-year-old child to a technical interviewer.
*   **Forgetting Curve**: Content optimized for long-term retention and spaced repetition.
*   **Study Plan**: Generate custom 7-day learning schedules with specific sub-topics and time slots.

### ⚙️ Core Capabilities
*   **Hybrid AI Engine**: 
    *   **Primary**: Purely Local & Private using **Ollama (Llama 3 )**.
    *   **Fallback**: Seamless integration with **Google Gemini 2.0 Flash** for complex queries.
*   **Robust Educational Safguards**: Explicitly tuned to handle advanced topics like **Deep Learning**, **Ethical Hacking**, and **Cybersecurity** without false safety refusals.
*   **Professional PDF Export**: Save your learning sessions as professionally designed PDFs.
*   **Smart Audio Integration**: Listen to your explanations with variable speed controls (1x to 2.5x).
*   **Persistent Learning History**: Comprehensive chat history tracking with user authentication.

---

## 🚀 Quick Start

### 1. Install Ollama (Recommended)
For the full offline experience, install Ollama:
1.  Download from [ollama.com](https://ollama.com).
2.  Open your terminal and pull a model:
    ```bash
    ollama pull llama3.2:1b
    ```
3.  Ensure the Ollama server is running (`ollama serve`).

### 2. Clone and Install Dependencies
```bash
git clone (https://github.com/Moksha-132/Offline-AI-Tutor-.git)
cd AI-concept
pip install -r requirements.txt
```

### 3. Launch Application
Start the Streamlit interface:
```bash
streamlit run streamlit_app.py
```

---

## 🛠️ Project Structure

- `streamlit_app.py`: Main application entry point.
- `assets/`: Contains `style.css` for the custom design system.
- `modules/`:
    - `llm_manager.py`: AI logic Ollama with advanced prompt engineering.
    - `ui.py`: Custom HTML/CSS components (Hero section, Audio player).
    - `adaptive_logic.py`: Quiz parsing and scoring algorithms.
    - `db_manager.py`: SQLite persistence for history and users.
    - `export_manager.py`: PDF generation engine.
    - `tts_manager.py`: Text-to-speech functionality.

---

## ⚠️ Troubleshooting
- **"Ollama is not running"**: Ensure you have the Ollama desktop app open or run `ollama serve` in a terminal.
- **Safety Refusals**: The system is tuned for academic freedom. If you face a refusal, ensure your query is framed as a "Theoretical Concept".
- **Visual Glitches**: This app uses advanced CSS. Ensure you are using a modern browser (Chrome/Edge/Firefox).

---

## 📝 License
Built with ❤️ for rapid learning.

**Author:** [Lakshmi Moksha Boya](https://github.com/Moksha-132)
