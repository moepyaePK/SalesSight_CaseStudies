from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine
import re


DB_PATH = "users.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

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

def create_feedback_table():
    """Create the feedback table in the database."""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS feedback(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                feedback_text TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
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

def add_feedback(user_id, feedback_text):
    """Add feedback from a user."""
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO feedback (user_id, feedback_text) VALUES (:user_id, :feedback_text)"),
            {"user_id": user_id, "feedback_text": feedback_text}
        )
        conn.commit()