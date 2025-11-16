from sqlalchemy import create_engine, text
import re
import datetime

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
    Creates the 'users' table if it doesn't already exist.
    This table stores user authentication information.
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
    Creates the 'feedback' table if it doesn't already exist.
    This table stores user feedback on the sales forecasting model.
    """
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS feedback(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                rating INTEGER,
                feedback_text TEXT,
                timestamp TEXT NOT NULL
            )
        """))
        conn.commit()

def add_user(username, email, password):
    """
    Adds a new user to the 'users' table after validating the email.

    Args:
        username (str): The unique username for the new user.
        email (str): The unique email address for the new user.
        password (str): The password for the new user.

    Raises:
        ValueError: If the provided email address is invalid.
        sqlalchemy.exc.IntegrityError: If username or email already exists.
    """
    if not is_valid_email(email):
        raise ValueError("Invalid email address")
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO users (username, email, password) VALUES (:u, :e, :p)"),
            {"u": username, "e": email, "p": password}
        )
        conn.commit()

def get_user(email, password):
    """
    Verifies if a user exists by email and password.

    Args:
        email (str): The email address of the user.
        password (str): The password of the user.

    Returns:
        sqlalchemy.engine.row.Row or None: The user's record if found, otherwise None.
    """
    if not is_valid_email(email):
        return None
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM users WHERE email=:e AND password=:p"),
            {"e": email, "p": password}
        ).fetchone()
        return result

def add_feedback(user_email, rating, feedback_text):
    """
    Stores user feedback into the 'feedback' table.

    Args:
        user_email (str): The email of the user providing feedback.
        rating (int): The rating given by the user (e.g., 1-5).
        feedback_text (str): The detailed feedback text from the user.

    Raises:
        ValueError: If user_email is invalid or if rating is out of expected range.
        sqlalchemy.exc.SQLAlchemyError: For other database-related errors.
    """
    if not is_valid_email(user_email):
        raise ValueError("Invalid user email provided for feedback.")
    if rating is not None and not (1 <= rating <= 5):
        raise ValueError("Rating must be an integer between 1 and 5.")

    timestamp = datetime.datetime.now().isoformat()
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO feedback (user_email, rating, feedback_text, timestamp) VALUES (:ue, :r, :ft, :ts)"),
            {"ue": user_email, "r": rating, "ft": feedback_text, "ts": timestamp}
        )
        conn.commit()

# Ensure tables are created when db.py is imported
create_users_table()
create_feedback_table()