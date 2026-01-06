import json
import re

def parse_quiz_json(llm_output):
    """
    Attempts to parse the output from LLM.
    Supports both JSON format (legacy/advanced) and Structured Text format (fast/robust).
    """
    if not llm_output:
        return []

    data = None

    # --- 1. Try JSON Parsing First ---
    try:
        cleaned = str(llm_output)
        # Remove markdown code blocks if present
        if "```" in cleaned:
             cleaned = re.sub(r'```json', '', cleaned, flags=re.IGNORECASE)
             cleaned = re.sub(r'```', '', cleaned).strip()

        # Find potential JSON start
        start_idx = -1
        if '[' in cleaned: start_idx = cleaned.find('[')
        elif '{' in cleaned: start_idx = cleaned.find('{')

        if start_idx != -1:
            json_str = cleaned[start_idx:]
            # Find probable end
            end_idx = max(json_str.rfind(']'), json_str.rfind('}'))
            if end_idx != -1:
                json_str = json_str[:end_idx+1]
                # Fix trailing commas
                json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
                
                try:
                    data = json.loads(json_str)
                except:
                    # Simple fix for truncated JSON
                    try:
                        if json_str.startswith('{'): data = json.loads(json_str + ']}')
                        elif json_str.startswith('['): data = json.loads(json_str + ']')
                    except:
                        pass
    except:
        pass

    # --- 2. If JSON Parsed, Normalize and Return ---
    if data:
        raw_list = []
        if isinstance(data, list):
            raw_list = data
        elif isinstance(data, dict):
            # Check common keys
            for key in ['quiz', 'questions', 'mcqs']:
                if key in data and isinstance(data[key], list):
                    raw_list = data[key]
                    break
            # Single question dict
            if not raw_list and ('question' in data or 'q' in data):
                raw_list = [data]
        
        normalized_data = []
        for item in raw_list:
            if not isinstance(item, dict): continue
            q = item.get('question', item.get('q', ''))
            opts = item.get('options', item.get('choices', []))
            ans = item.get('answer', item.get('correct', ''))
            exp = item.get('explanation', '')
            
            # Ensure opts is a list
            if isinstance(opts, dict): opts = list(opts.values())
            
            if q and isinstance(opts, list) and len(opts) > 0:
                normalized_data.append({
                    'question': str(q),
                    'options': [str(o) for o in opts][:4],
                    'answer': str(ans),
                    'explanation': str(exp)
                })
        
        if normalized_data:
            return normalized_data

    # --- 3. Fallback: Text-Based Parsing (New Fast Mode) ---
    text_questions = []
    
    # Pre-process: split " A) ", " B) " if they are inline
    # parsing line-by-line is strict, let's normalize the blob first
    raw_text = str(llm_output)
    
    # Force newlines before options A-D and Answer if they are preceded by spaces
    # matches " A) ", " A. "
    raw_text = re.sub(r'\s+([A-D][\)\.])\s+', r'\n\1 ', raw_text)
    # matches " Answer: ", " Correct: "
    raw_text = re.sub(r'\s+(Answer:|Correct:)', r'\n\1', raw_text, flags=re.IGNORECASE)
    
    lines = raw_text.split('\n')
    current_q = {}
    
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Detect Question (e.g., "Q1.", "1.", "Question:")
        # Regex: Starts with Q+Number or Number+Dot or "Question", is at least 5 chars long to avoid noise
        if (re.match(r'^(?:Q\d+|Question)', line, re.IGNORECASE) or re.match(r'^\d+\.', line)) and len(line) > 5:
            # If we were building a question, save it
            if current_q.get('question') and current_q.get('options'):
                text_questions.append(current_q)
            current_q = {'question': line, 'options': [], 'answer': '', 'explanation': 'See answer key.'}
            
        # Detect Options (e.g., "A)", "A.", "a)")
        elif re.match(r'^[A-D][\)\.]\s+', line) and current_q:
            opt_val = re.sub(r'^[A-D][\)\.]\s+', '', line).strip()
            # Avoid re-adding if duplicate (some models hallucinate repetitions)
            if opt_val not in current_q['options']:
                current_q['options'].append(opt_val)
            
        # Detect Answer (e.g., "Answer: Option Text")
        elif (line.lower().startswith('answer:') or line.lower().startswith('correct:')):
            if current_q:
                ans_val = line.split(':', 1)[1].strip()
                # If answer is just "A" or "Option A", try to map it to the option text
                clean_ans = ans_val.lower().replace('option', '').strip()
                # Remove trailing punctuation
                clean_ans = re.sub(r'[\.\)]$', '', clean_ans)
                
                if len(clean_ans) == 1 and clean_ans in 'abcd' and current_q['options']:
                     idx = {'a':0, 'b':1, 'c':2, 'd':3}.get(clean_ans, -1)
                     if idx != -1 and idx < len(current_q['options']):
                         current_q['answer'] = current_q['options'][idx]
                     else:
                         current_q['answer'] = ans_val
                else:
                    current_q['answer'] = ans_val

    # Save last question
    if current_q.get('question') and current_q.get('options'):
        text_questions.append(current_q)
        
    return text_questions

def clean_text(text):
    import re
    # Remove punctuation and extra whitespace for fairer comparison
    text = re.sub(r'[^\w\s]', '', str(text).lower())
    return " ".join(text.split())

def evaluate_quiz(user_answers, quiz_data):
    """
    Returns score (percentage) and a list of feedback objects.
    Handles semantic matching for local models.
    """
    score = 0
    results = []
    total = len(quiz_data)
    
    if total == 0:
        return 0, []
        
    for i, q in enumerate(quiz_data):
        raw_correct = str(q.get('answer', '')).strip()
        options = q.get('options', [])
        user_ans = str(user_answers.get(i, '')).strip()
        
        # Cleaned versions for matching
        c_user = clean_text(user_ans)
        c_correct = clean_text(raw_correct)
        
        # 1. Direct or Cleaned match
        is_correct = (user_ans.lower() == raw_correct.lower()) or (c_user == c_correct)
        
        # 2. Letter/Index fallback
        letter_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, '1': 0, '2': 1, '3': 2, '4': 3}
        if not is_correct and raw_correct.lower() in letter_map:
            idx = letter_map[raw_correct.lower()]
            if idx < len(options):
                if c_user == clean_text(options[idx]):
                    is_correct = True

        if is_correct:
            score += 1
            
        # Display the full original text of the correct choice
        display_correct = raw_correct
        if raw_correct.lower() in letter_map:
            idx = letter_map[raw_correct.lower()]
            if idx < len(options):
                display_correct = options[idx]

        results.append({
            "question": q.get('question'),
            "user_answer": user_ans,
            "correct_answer": display_correct,
            "is_correct": is_correct,
            "explanation": q.get('explanation', 'No explanation provided.')
        })
            
    percentage = (score / total) * 100
    return percentage, results
