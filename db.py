from sqlalchemy import create_engine, text
import re


DB_PATH = "users.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

def is_valid_email(email):
    """
    Check if the provided email is valid.
    Returns True if valid, False otherwise.
    """
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def create_users_table():
    with engine.connect() as conn:
        # Drop existing table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """))
        conn.commit()

def add_user(username, email, password):
    """Add a new user with email validation"""
    if not is_valid_email(email):
        raise ValueError("Invalid email address")
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO users (username, email, password) VALUES (:u, :e, :p)"),
            {"u": username, "e": email, "p": password}
        )
        conn.commit()

def get_user(email, password):
    """Verify if user exists by email and password"""
    if not is_valid_email(email):
        return None  
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM users WHERE email=:e AND password=:p"),
            {"e": email, "p": password}
        ).fetchone()
        return result