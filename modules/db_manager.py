import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "offline_ai.db")

def init_db():
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT,
                    email TEXT
                )''')
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except sqlite3.OperationalError: pass

    # User Progress / History - Added project_name and username
    c.execute('''CREATE TABLE IF NOT EXISTS learning_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    concept TEXT,
                    marks_mode TEXT,
                    difficulty TEXT,
                    timestamp DATETIME,
                    explanation TEXT,
                    project_name TEXT DEFAULT 'Default',
                    username TEXT DEFAULT 'guest'
                )''')
    
    # Migrations for existing tables
    try:
        c.execute("ALTER TABLE learning_history ADD COLUMN project_name TEXT DEFAULT 'Default'")
    except sqlite3.OperationalError: pass
    
    try:
        c.execute("ALTER TABLE learning_history ADD COLUMN username TEXT DEFAULT 'guest'")
    except sqlite3.OperationalError: pass

    # Quiz Results
    c.execute('''CREATE TABLE IF NOT EXISTS quiz_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    concept TEXT,
                    score INTEGER,
                    total_questions INTEGER,
                    timestamp DATETIME,
                    username TEXT DEFAULT 'guest'
                )''')
                
    try:
        c.execute("ALTER TABLE quiz_results ADD COLUMN username TEXT DEFAULT 'guest'")
    except sqlite3.OperationalError: pass
    
    conn.commit()
    conn.close()

# --- Auth Functions ---
def create_user(username, password_hash, email):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)", (username, password_hash, email))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False # Username (primary key) exists

def verify_user(identifier):
    """Identifier can be username or email."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Check if identifier matches username OR email (Case Insensitive for username/email lookup)
    # We fetch the actual stored case-sensitive username to return proper session data
    c.execute("SELECT password_hash, username FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)", (identifier, identifier))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0], row[1] # Return (hash, actual_username) 
    return None, None

# --- History Functions ---

def save_learning_history(concept, marks_mode, difficulty, explanation, project_name="Default", username="guest"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO learning_history (concept, marks_mode, difficulty, timestamp, explanation, project_name, username) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (concept, marks_mode, difficulty, datetime.now(), explanation, project_name, username))
    conn.commit()
    conn.close()

def save_quiz_result(concept, score, total_questions, username="guest"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO quiz_results (concept, score, total_questions, timestamp, username) VALUES (?, ?, ?, ?, ?)",
              (concept, score, total_questions, datetime.now(), username))
    conn.commit()
    conn.close()

def get_recent_history(limit=10, project_name="Default", username="guest"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, concept, timestamp, explanation FROM learning_history WHERE project_name = ? AND username = ? ORDER BY timestamp DESC LIMIT ?", (project_name, username, limit))
    rows = c.fetchall()
    conn.close()
    return rows

def delete_history_item(item_id):
    """Deletes a specific history record."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM learning_history WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def get_all_projects(username="guest"):
    """Returns a list of unique project names for a user."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT DISTINCT project_name FROM learning_history WHERE username = ? ORDER BY project_name", (username,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows] if rows else ["Default"]
