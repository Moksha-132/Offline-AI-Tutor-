# 🧠 RamXplain: The Ultimate Offline AI Learning Ecosystem

**RamXplain** is a state-of-the-art, offline-first AI tutor designed to transform complex topics into deep, intuitive knowledge. Powered by local LLMs (Ollama) and a premium Streamlit interface, it offers a secure, private, and highly personalized learning experience.

---

## 🌟 Key Features

### 🎓 Advanced Learning Modes
*   **Mastery Pathway (Certified)**: A rigorous 3-stage (Beginner → Advanced → Expert) exhaustive guide that ends with a **Mastery Exam** and a **Shareable Certificate**.
*   **Examiner POV**: Get feedback on your concepts from the perspective of an academic grader.
*   **Viva Trainer**: Interactive oral exam simulation to prepare you for interviews and presentations.
*   **Explain Like I'm...**: Tailor explanations for any audience—from a 10-year-old child to a technical interviewer.
*   **Forgetting Curve**: Content optimized for long-term retention and spaced repetition.
*   **Study Plan**: Generate custom 7-day learning schedules with specific sub-topics and time slots.

### �️ Core Capabilities
*   **Purely Local & Private**: No data leaves your machine. Uses **Ollama (TinyLlama/Llama3)** for high-speed, offline intelligence.
*   **Interactive Quizzes**: Test your knowledge with dynamically generated exams and instant scoring.
*   **Professional PDF Export**: Save your learning sessions or your earned **Mastery Certificates** as sleek, professionally designed PDFs.
*   **Smart Audio Integration**: Listen to your explanations with variable speed controls (1x to 2.5x).
*   **Persistent Learning History**: Comprehensive chat history tracking with user authentication for a personalized journey.
*   **Premium UI/UX**: A modern, responsive design with "Glassmorphism" aesthetics and intuitive navigation.

---

## 🚀 Quick Start

### 1. Install Ollama
RamXplain requires **Ollama** to be installed on your system.
1.  Download from [ollama.com](https://ollama.com).
2.  Open your terminal and pull the default model:
    ```bash
    ollama pull tinyllama
    ```
3.  Ensure the Ollama server is running.

### 2. Clone and Install Dependencies
```bash
git clone <your-repo-url>
cd AI-concept
pip install -r requirements.txt
```

### 3. Launch Management
Start the application with:
```bash
streamlit run streamlit_app.py
```

---

## 🛠️ Project Structure

- `app.py`: Main entry point and orchestration.
- `modules/`:
    - `llm_manager.py`: Logic for prompt engineering and LLM streaming.
    - `ui.py`: Custom CSS and premium UI components.
    - `adaptive_logic.py`: Quiz generation and evaluation algorithms.
    - `db_manager.py`: SQLite persistence for history and users.
    - `export_manager.py`: PDF generation for notes and certificates.
    - `tts_manager.py`: Text-to-speech engine.

---

## Troubleshooting
- **Local AI Connection**: If you see "Ollama is not running," ensure you've run `ollama serve` or opened the Ollama application.
- **Model Loading**: First-time generation might take a few seconds as the model loads into RAM.
- **Audio Issues**: Ensure your system's default TTS engine is functional.

---

## 📝 License
Built with ❤️ for rapid learning.

**Author:** [Lakshmi Moksha Boya](https://github.com/Moksha-132)

