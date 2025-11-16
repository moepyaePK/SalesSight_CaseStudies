from sqlalchemy import create_engine, text
import re
from datetime import datetime


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
    Creates the 'users' table if it does not already exist.
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
    Creates the 'feedback' table if it does not already exist.
    This table stores user feedback on the sales forecasting model.
    """
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS feedback(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                rating INTEGER NOT NULL,
                comment TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()

def add_user(username, email, password):
    """
    Adds a new user to the database after validating the email.

    Args:
        username (str): The unique username for the new user.
        email (str): The unique email address for the new user.
        password (str): The password for the new user.

    Raises:
        ValueError: If the provided email address is invalid.
        Exception: For any database-related errors during insertion.
    """
    if not is_valid_email(email):
        raise ValueError("Invalid email address")
    try:
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO users (username, email, password) VALUES (:u, :e, :p)"),
                {"u": username, "e": email, "p": password}
            )
            conn.commit()
    except Exception as e:
        raise Exception(f"Error adding user: {e}")

def get_user(email, password):
    """
    Verifies if a user exists in the database based on email and password.

    Args:
        email (str): The email address of the user.
        password (str): The password of the user.

    Returns:
        sqlalchemy.engine.row.Row or None: The user's record if found, otherwise None.
    """
    if not is_valid_email(email):
        return None
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM users WHERE email=:e AND password=:p"),
                {"e": email, "p": password}
            ).fetchone()
            return result
    except Exception as e:
        print(f"Error retrieving user: {e}")
        return None

def add_feedback(user_email, rating, comment):
    """
    Stores user feedback into the 'feedback' table.

    Args:
        user_email (str): The email of the user providing feedback. Can be None or empty if anonymous.
        rating (int): The rating given by the user (e.g., 1 to 5).
        comment (str): The textual feedback provided by the user.

    Raises:
        ValueError: If the rating is not within the valid range (e.g., 1-5).
        Exception: For any database-related errors during insertion.
    """
    if not isinstance(rating, int) or not (1 <= rating <= 5):
        raise ValueError("Rating must be an integer between 1 and 5.")
    
    try:
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO feedback (user_email, rating, comment) VALUES (:ue, :r, :c)"),
                {"ue": user_email, "r": rating, "c": comment}
            )
            conn.commit()
    except Exception as e:
        raise Exception(f"Error adding feedback: {e}")

# Ensure all necessary tables are created when db.py is imported or run
create_users_table()
create_feedback_table()