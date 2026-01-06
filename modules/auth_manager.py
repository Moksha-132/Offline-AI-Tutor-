import hashlib
from modules import db_manager

def hash_password(password):
    """Returns SHA-256 hash of the password."""
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(identifier, password):
    """Verifies username/email and password. Returns (success, username)."""
    if identifier: identifier = identifier.strip()
    if password: password = password.strip()
    
    stored_hash, actual_username = db_manager.verify_user(identifier)
    if stored_hash and stored_hash == hash_password(password):
        return True, actual_username
    return False, None

def signup_user(username, password, email):
    """Creates a new user."""
    if not username or not password or not email:
        return False, "All fields (Username, Password, Email) are required."
    
    if db_manager.create_user(username, hash_password(password), email):
        return True, "Account created successfully!"
    else:
        return False, "Username already exists."
