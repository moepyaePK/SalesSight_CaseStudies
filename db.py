from sqlalchemy import create_engine, text
import re
import datetime # For timestamp in feedback table

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
    """
    Creates the users table if it doesn't already exist.
    """
    with engine.connect() as conn:
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
    """
    Creates the feedback table if it doesn't already exist.
    This table stores user feedback on analysis sessions.
    """
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                analysis_session_id TEXT NOT NULL,
                rating INTEGER,
                feedback_text TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """))
        conn.commit()

def add_user(username: str, email: str, password: str):
    """
    Adds a new user to the database with email validation.

    Args:
        username (str): The unique username for the new user.
        email (str): The unique email address for the new user.
        password (str): The password for the new user.

    Raises:
        ValueError: If the email is invalid, or if username/email already exists.
        RuntimeError: For other database-related errors.
    """
    if not is_valid_email(email):
        raise ValueError("Invalid email address")
    with engine.connect() as conn:
        try:
            conn.execute(
                text("INSERT INTO users (username, email, password) VALUES (:u, :e, :p)"),
                {"u": username, "e": email, "p": password}
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            # Check for unique constraint violation
            if "UNIQUE constraint failed" in str(e):
                if "users.username" in str(e):
                    raise ValueError("Username already exists.")
                elif "users.email" in str(e):
                    raise ValueError("Email already exists.")
            raise RuntimeError(f"Failed to add user: {e}") from e

def get_user(email: str, password: str):
    """
    Verifies if a user exists by email and password.

    Args:
        email (str): The email address of the user.
        password (str): The password of the user.

    Returns:
        sqlalchemy.engine.row.Row or None: The user's row if found, otherwise None.
    """
    if not is_valid_email(email):
        return None
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM users WHERE email=:e AND password=:p"),
            {"e": email, "p": password}
        ).fetchone()
        return result

def add_feedback(user_id: int, analysis_session_id: str, rating: int, feedback_text: str):
    """
    Adds user feedback on an analysis session to the database.

    Args:
        user_id (int): The ID of the user providing feedback.
        analysis_session_id (str): A unique identifier for the specific analysis session.
        rating (int): The rating given by the user (e.g., 1-5).
        feedback_text (str): The detailed feedback text provided by the user.

    Raises:
        ValueError: If any input parameter is invalid.
        RuntimeError: For database-related errors during insertion.
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("Invalid user_id provided. Must be a positive integer.")
    if not isinstance(analysis_session_id, str) or not analysis_session_id.strip():
        raise ValueError("Invalid analysis_session_id provided. Must be a non-empty string.")
    if not isinstance(rating, int) or not (1 <= rating <= 5): # Assuming a 1-5 star rating
        raise ValueError("Rating must be an integer between 1 and 5.")
    if not isinstance(feedback_text, str):
        raise ValueError("Feedback text must be a string.")

    with engine.connect() as conn:
        try:
            conn.execute(
                text("""
                    INSERT INTO feedback (user_id, analysis_session_id, rating, feedback_text)
                    VALUES (:user_id, :analysis_session_id, :rating, :feedback_text)
                """),
                {
                    "user_id": user_id,
                    "analysis_session_id": analysis_session_id,
                    "rating": rating,
                    "feedback_text": feedback_text
                }
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Failed to add feedback to the database: {e}") from e

# Ensure tables are created when the module is imported
create_users_table()
create_feedback_table()