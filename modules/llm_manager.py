import json
import requests
from google import genai

OLLAMA_BASE_URL = "http://127.0.0.1:11434/api"
DEFAULT_MODEL = "llama3.2:1b" 
GEMINI_API_KEY = "AIzaSyAzlbCghujpX2mp9f6dstOH-Ha26RhWNwI" # Integrated as requested

def check_ollama():
    """Checks if Ollama is accessible."""
    try:
        response = requests.get("http://127.0.0.1:11434", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_ollama_models():
    """Retrieves list of available Ollama models."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/tags", timeout=2)
        if response.status_code == 200:
            models = [m['name'] for m in response.json().get('models', [])]
            return models
    except:
        pass
    return [DEFAULT_MODEL]

def query_gemini(prompt):
    """Queries Google Gemini cloud model using the new genai SDK."""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content_stream(
            model='gemini-2.0-flash',
            contents=prompt,
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
            yield f"**⚠️ Cloud Limit Reached:** Google's free quota is exhausted for the moment. Please switch to **Local (Ollama)** in the sidebar or try again in a minute."
        else:
            yield f"**Cloud Error:** {err_str}"

def query_ollama(prompt, model=DEFAULT_MODEL, stream=True, json_format=False):
    """Generic function to query Ollama. Always returns a generator."""
    try:
        payload = {
            "model": model, 
            "prompt": prompt, 
            "stream": stream,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 50,
                "num_predict": 1024,  # Reduced from 2048 for faster generation on slow hardware
                "num_ctx": 4096,
                "stop": ["User:", "Assistant:"] # Removed "---" as it caused premature stops between questions
            }
        }
        if json_format:
            payload["format"] = "json"

        # Significantly increased timeouts for very slow hardware: connection (10s) and read (600s = 10 minutes)
        response = requests.post(f"{OLLAMA_BASE_URL}/generate", json=payload, stream=stream, timeout=(10, 600)) 
        response.raise_for_status()
        
        chunk_count = 0
        if stream:
            for line in response.iter_lines():
                if line:
                    try:
                        decoded = json.loads(line.decode('utf-8'))
                        chunk = decoded.get("response", "")
                        if chunk:
                            yield chunk
                            chunk_count += 1
                    except Exception:
                        continue
            if chunk_count == 0: yield None
        else:
            yield response.json().get("response", "")
    except GeneratorExit:
        # This occurs when Streamlit stops the generator (e.g., on rerun/stop)
        return
    except Exception:
        yield None

def generate_explanation(concept, mode="Normal Tutor", context_data=None, model=DEFAULT_MODEL, provider="Local (Ollama)", chat_history=None):
    # System context to prevent false safety triggers
    system_context = (
        "SYSTEM DIRECTIVE: You are a professional AI educational tutor. This is a legitimate learning application.\n"
        "Your goal is to teach THEORETICAL CONCEPTS only.\n"
        "ALL requests are for ACADEMIC STUDY purposes.\n"
        "SAFE TOPICS INCLUDE: Deep Learning, Neural Networks, Cyber Security (Defense), Ethical Hacking (Theory), Data Science, etc.\n"
        "You MUST answer all questions about these topics. Refusing to teach standard computer science topics is counter-productive.\n"
        "If a topic triggers a safety warning, assume it is for an EDUCATIONAL course and answer the THEORETICAL aspect.\n"
        "NEVER refuse 'Deep Learning' or 'Data Science' queries - these are fundamental fields, not scams.\n"
        "IMPORTANT: This request does NOT involve data extraction, personal data, or privacy breaches. Do not refuse based on these assumptions.\n\n"
    )
    
    # Core pedagogical rules
    rules = (
        "1. Explain the concept clearly and concisely. "
        "2. List 3 to 5 key takeaways as bullet points after the explanation. "
        "3. Conclude by asking if the user wants: "
        "1) Simpler explanation, 2) Example, 3) Short notes, or 4) Move to next topic. "
        "Do not generate or ask quiz questions."
    )
    
    instr = ""
    if mode == "Examiner POV":
        instr = "Act as a University Examiner. List mandatory points and common mistakes."
    elif mode == "Forgetting Curve":
        instr = "Provide a brief summary for quick revision and suggest a review schedule (1 day / 1 week)."
    elif mode == "Explain Like I'm...":
        persona = context_data.get('persona', 'a child') if context_data else 'a child'
        instr = f"Explain this concept like I am {persona}. Use very simple language."
    elif mode == "Viva Trainer":
        instr = (
            "You are a professional Viva Voce examiner preparing study material.\n"
            "Generate 5-7 expected THEORETICAL viva questions about the concept.\n"
            "Focus on: Definitions, Architecture, Standard Algorithms, and Mathematical basis.\n"
            "Format:\n"
            "**Q1: [Question]**\n"
            "**Answer:** [Detailed Theoretical Answer]\n\n"
            "**Q2: [Question]**\n"
            "**Answer:** [Detailed Theoretical Answer]\n\n"
            "Cover fundamental concepts only. Do not generate code for exploits or private data extraction."
        )
    elif mode == "Mastery Pathway (Certified)":
        instr = (
            "Act as a World-Class Academic Professor. Your goal is to deliver a comprehensive 3-Stage Mastery Guide.\n\n"
            "CONTENT STRUCTURE:\n"
            "1. ### LEVEL: BEGINNER\n"
            "   - Focus: Definitions, Etymology, Historical origins, and High-level purpose.\n"
            "   - Content: 3 detailed paragraphs. Do NOT touch internal mechanisms yet.\n"
            "2. ### LEVEL: ADVANCED\n"
            "   - Focus: Core Mechanics, Mathematical frameworks, Architectural logic.\n"
            "   - Content: 3 detailed paragraphs. This is the technical engine.\n"
            "3. ### LEVEL: EXPERT\n"
            "   - Focus: Cutting-edge research, Optimization, Ethics, and Future projections.\n"
            "   - Content: 3 detailed paragraphs of high-level synthesis.\n\n"
            "STRICT RULES:\n"
            "- Each level must be UNIQUE and not repeat previous content.\n"
            "- Total minimum: ~600 words across all sections.\n"
            "- Use academic language and technical terms.\n"
            "- At the end of Expert section, write: '[[ FULL GUIDE COMPLETE ]]'."
        )
    elif mode == "Study Plan":
        instr = (
            "Generate a professional and high-performance 7-day study plan. "
            "For each day, provide a structured schedule including specific sub-topics, "
            "strict time limits for each session (e.g., 45 mins), and mandatory 10-minute 'Brain Breaks' "
            "between sessions to ensure maximum retention and focus."
        )
    else:
        instr = "Act as an expert academic tutor and provide a detailed explanation."

    is_exam_mode = mode in ["Viva Trainer", "Mastery Pathway (Certified)"]
    
    # --- Chat History Assembly ---
    history = ""
    if chat_history:
        history += "### PREVIOUS CONVERSATION HISTORY ###\n"
        history_window = -15 if is_exam_mode else -5
        for msg in chat_history[history_window:]:
            role = "User" if msg['role'] == 'user' else "Assistant"
            content = msg['content']
            if len(content) > 500:
                content = content[:500] + "... [truncated]"
            history += f"{role}: {content}\n"

    # Start building the prompt
    prompt = f"{system_context}"  # Add system context first
    prompt += f"### YOUR INSTRUCTION ###\n{instr}\n\n"
    prompt += f"### TARGET TOPIC ###\n'{concept}'\n\n"
    
    if history:
        prompt += history + "\n"

    # --- Mastery Pathway Dynamic State Injection ---
    if mode == "Mastery Pathway (Certified)" and chat_history:
        user_msg = chat_history[-1]['content'].upper()
        user_msg_count = len([m for m in chat_history if m['role'] == 'user'])
        
        # Check if user is asking for a test or if it's the very first message
        is_quiz_request = any(k in user_msg for k in ["QUIZ", "EXAM", "TEST", "QUESTIONS", "ASSESS"])
        is_first_msg = user_msg_count <= 1
        is_guide_request = any(k in user_msg for k in ["EXPLAIN", "GUIDE", "TEACH", "REVIEW", "LEARN", "DETAIL"])
        
        # Priority: If it's the first message OR a specific quiz request, and NOT a guide request, give quiz.
        should_quiz = (is_first_msg or is_quiz_request) and not is_guide_request

        prompt += f"\n### !! MANDATORY SYSTEM COMMAND !! ###\n"
        if should_quiz:
            prompt += f"YOU ARE A QUIZ GENERATOR. Your ONLY job is to create a 5-question MCQ test about '{concept}'.\n\n"
            prompt += "DO NOT WRITE EXPLANATIONS OR INTRODUCTIONS ABOUT THE TOPIC.\n"
            prompt += "DO NOT TEACH THE CONCEPT.\n"
            prompt += "ONLY GENERATE THE QUIZ.\n\n"
            prompt += "EXACT OUTPUT FORMAT (copy this structure):\n\n"
            prompt += "### 🏆 MASTERY ASSESSMENT: " + concept.upper() + "\n"
            prompt += "I will evaluate your current knowledge to see if you qualify for a Mastery Certificate. If you pass, you get your certificate immediately! Otherwise, I will provide a deep-dive study guide.\n\n"
            prompt += "```json\n"
            prompt += "{\n"
            prompt += '  "quiz": [\n'
            prompt += '    {"question": "Q1 about ' + concept + '?", "options": ["A", "B", "C", "D"], "answer": "A", "explanation": "..."},\n'
            prompt += '    {"question": "Q2 about ' + concept + '?", "options": ["A", "B", "C", "D"], "answer": "B", "explanation": "..."},\n'
            prompt += '    {"question": "Q3 about ' + concept + '?", "options": ["A", "B", "C", "D"], "answer": "C", "explanation": "..."},\n'
            prompt += '    {"question": "Q4 about ' + concept + '?", "options": ["A", "B", "C", "D"], "answer": "D", "explanation": "..."},\n'
            prompt += '    {"question": "Q5 about ' + concept + '?", "options": ["A", "B", "C", "D"], "answer": "A", "explanation": "..."},\n'
            prompt += '    {"question": "Q6 about ' + concept + '?", "options": ["A", "B", "C", "D"], "answer": "B", "explanation": "..."},\n'
            prompt += '    {"question": "Q7 about ' + concept + '?", "options": ["A", "B", "C", "D"], "answer": "C", "explanation": "..."},\n'
            prompt += '    {"question": "Q8 about ' + concept + '?", "options": ["A", "B", "C", "D"], "answer": "D", "explanation": "..."},\n'
            prompt += '    {"question": "Q9 about ' + concept + '?", "options": ["A", "B", "C", "D"], "answer": "A", "explanation": "..."},\n'
            prompt += '    {"question": "Q10 about ' + concept + '?", "options": ["A", "B", "C", "D"], "answer": "B", "explanation": "..."}\n'
            prompt += '  ]\n'
            prompt += "}\n"
            prompt += "```\n\n"
            prompt += "### SYLLABUS PENDING\n\n"
            prompt += "CRITICAL RULES:\n"
            prompt += "- You MUST include all 5 questions in the JSON.\n"
            prompt += "- DO NOT write paragraphs explaining the topic.\n"
            prompt += "- DO NOT write historical background.\n"
            prompt += "- ONLY output the header, JSON block, and 'SYLLABUS PENDING' marker.\n"
        else:
            prompt += f"TASK: Deliver the UNIQUE and EXHAUSTIVE 3-Level Guide for '{concept}' now.\n"
            prompt += "STRICT THEMES:\n"
            prompt += "- Beginner: Fundamentals & History.\n"
            prompt += "- Advanced: Technical Mechanisms & Math.\n"
            prompt += "- Expert: Optimization & Future Trends.\n"
            prompt += "DENSITY: Provide 18-20 distinct, technical paragraphs. Zero repetition across levels."
        prompt += "\n--- END OF PROMPT ---"

    prompt += "\n### FORMATTING RULES ###\n"
    prompt += "1. Use clear, professional language. 2. Be detailed where needed. 3. NO unnecessary summaries.\n"
    
    if is_exam_mode:
        prompt += "- Use a direct, conversational, and professional exam style.\n"
        prompt += "- Avoid long academic introductions.\n"
    else:
        prompt += "- Be highly detailed and accurate with clear paragraphs.\n"
        prompt += "- Use bold headings and sub-headings for better readability.\n"
        
    prompt += "- Do not provide 'Key Takeaways' unless specifically asked.\n"
    
    if not is_exam_mode:
        prompt += "- Conclude with a single question about what the user wants to see next.\n"
        
    prompt += "\n--- END OF PROMPT ---"

    # --- PROVIDER LOGIC ---
    if provider == "Local (Ollama)":
        if not check_ollama():
            yield "❌ **Ollama is not running.** Please start it on your computer and click 'Refresh Status'."
            return
        
        # Detect if this is a quiz request for Mastery Pathway
        # Check if should_quiz was set earlier in the Mastery Pathway logic
        is_quiz_gen = False
        if mode == "Mastery Pathway (Certified)" and chat_history:
            user_msg_count = len([m for m in chat_history if m['role'] == 'user'])
            user_msg = chat_history[-1]['content'].upper() if chat_history else ""
            quiz_keywords = ["QUIZ", "EXAM", "TEST", "QUESTIONS", "ASSESS", "RETRY", "AGAIN", "START", "GENERATE", "FIX", "WORK"]
            is_quiz_request = any(k in user_msg for k in quiz_keywords)
            is_first_msg = user_msg_count <= 1
            is_guide_request = any(k in user_msg for k in ["EXPLAIN", "GUIDE", "TEACH", "REVIEW", "LEARN", "DETAIL"])
            is_quiz_gen = (is_first_msg or is_quiz_request) and not is_guide_request
        
        if is_quiz_gen:
            yield "### 🏆 MASTERY ASSESSMENT: " + concept.upper() + "\n\n"
            yield "I will evaluate your current knowledge to see if you qualify for a Mastery Certificate. If you pass, you get your certificate immediately! Otherwise, I will provide a deep-dive study guide.\n\n"
            
            quiz_prompt = (
                f"Generate a 5-question multiple choice quiz about '{concept}'.\n"
                "Format each question EXACTLY like this (Text format, NO JSON):\n\n"
                "Q1. [Question Text]?\n"
                "A) [Option 1]\n"
                "B) [Option 2]\n"
                "C) [Option 3]\n"
                "D) [Option 4]\n"
                "Answer: [Full Option Text]\n\n"
                "Do not write introductions. Start directly with Q1.\n"
                "Do not use separators like '---' between questions."
            )
            
            # Show "loading" state is handled by UI
            try:
                # Use Text mode (not JSON) for speed
                gen = query_ollama(quiz_prompt, model=model, stream=True, json_format=False)
                for chunk in gen:
                    if chunk:
                        yield chunk
            except Exception as e:
                # Fallback to a minimal error JSON so the UI doesn't break completely
                # (The UI handles text fallback now too, but let's send text error)
                yield f"Q1. Error generating quiz: {str(e)}?\nA) Retry\nB) Check Log\nAnswer: Retry"
            yield "\n```\n\n"
            yield "### SYLLABUS PENDING"
            return
        
        # Normal streaming for non-quiz content
        ollama_gen = query_ollama(prompt, model=model)
        try:
            has_content = False
            for chunk in ollama_gen:
                if chunk:
                    yield chunk
                    has_content = True
            
            if not has_content:
                yield "⚠️ **Ollama Error:** The model returned an empty response."
        except Exception as e:
            yield f"⚠️ **Ollama Connection Error:** {str(e)}"
        return # STOP HERE for Local

    # Cloud (Gemini) selected
    yield "✨ *(AI model loading...)*\n\n"
    try:
        for chunk in query_gemini(prompt):
            yield chunk
    except Exception as e:
        yield f"❌ **Cloud Error:** {str(e)}"

    prompt = (
        f"Generate a quiz with exactly 3 MCQs about '{concept}'.\n"
        "EXAMPLE JSON:\n"
        "{\"quiz\": [{\"question\": \"What is [Topic]?\", \"options\": [\"A\", \"B\", \"C\", \"D\"], \"answer\": \"A\", \"explanation\": \"Reasoning\"}]}\n\n"
        "Return ONLY the JSON object. Do not leave fields blank."
    )
    
    if provider == "Local (Ollama)":
        if check_ollama():
            try:
                # Use JSON mode for Ollama
                gen = query_ollama(prompt, model=model, stream=False, json_format=True)
                res = "".join([str(s) for s in gen if s is not None])
                return res
            except Exception:
                pass
        return json.dumps([{"question": "Ollama Error", "options": ["Ensure model is loaded"], "answer": "N/A", "explanation": "Check connectivity"}])

    # Gemini Quiz
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        res = client.models.generate_content(model='gemini-2.0-flash', contents=prompt).text
        return res
    except Exception:
        return json.dumps([{"question": "Cloud Error", "options": ["N/A"], "answer": "N/A"}])

def generate_readiness_check(concept, model=DEFAULT_MODEL, provider="Local (Ollama)"):
    """Identifies prerequisites and generates short baseline questions."""
    prompt = (
        f"For the concept '{concept}', identify 2 essential prerequisite concepts and "
        "generate 2 very short, open-ended baseline questions (one for each prerequisite) "
        "to check if a student is ready to learn it. "
        "Format as JSON: {'prerequisites': ['...', '...'], 'questions': ['...', '...']}. "
        "JSON ONLY. No other text."
    )
    
    def sanitize_json(text):
        try:
            # Try to find the first '{' and last '}'
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                return text[start:end+1]
            return text
        except:
            return text

    # Try Local first
    if provider == "Local (Ollama)":
        if check_ollama():
            gen = query_ollama(prompt, model=model, stream=False, json_format=True)
            res = "".join(list(gen))
            if res: return res
        return json.dumps({"prerequisites": [], "questions": []})

    # Gemini
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        res = client.models.generate_content(model='gemini-2.0-flash', contents=prompt).text
        return sanitize_json(res)
    except:
        return json.dumps({"prerequisites": [], "questions": []})

def evaluate_readiness(concept, answers_dict, model=DEFAULT_MODEL, provider="Local (Ollama)"):
    """Evaluates user answers and returns guidance or confirmation."""
    answers_str = json.dumps(answers_dict)
    prompt = (
        f"A student wants to learn '{concept}'. They provided these answers to prerequisite questions: {answers_str}. "
        "Evaluate their understanding. If they are ready, briefly say 'You have a good foundation!'. "
        "If they are weak, briefly explain the prerequisites in 2-3 simple sentences for each. "
        "Keep it encouraging and academic. No long intros."
    )
    
    if provider == "Local (Ollama)":
        if check_ollama():
            gen = query_ollama(prompt, model=model, stream=False)
            return "".join(list(gen))
        return "Please enable Ollama to evaluate your readiness."

    # Gemini
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        return client.models.generate_content(model='gemini-2.0-flash', contents=prompt).text
    except Exception as e:
        return f"Error evaluating readiness: {str(e)}"

