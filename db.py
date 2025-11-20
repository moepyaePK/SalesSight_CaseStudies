from sqlalchemy import create_engine, text

# Import the database URL from the central configuration file.
# This decouples the database connection details from the code and removes hardcoded values.
from config import DATABASE_URL

# The database engine is the central point of contact for the application
# with the database. It's configured once here using the URL from config.py.
engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """
    Initializes the database by creating all necessary tables.
    This function serves as a single entry point for setting up the DB schema,
    making it easy to manage database creation from the main application entry point.
    """
    create_users_table()


def create_users_table() -> None:
    """
    Creates the 'users' table in the database if it doesn't already exist.
    This table is essential for the authentication system, storing user credentials.

    Note: All user management logic (e.g., adding users, verifying credentials)
    has been moved to the `auth.py` module to adhere to the Single Responsibility
    Principle. This module, `db.py`, is now only concerned with schema and connection.
    """
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """))
        conn.commit()


# User-related functions (add_user, get_user, is_valid_email) have been removed
# from this file and moved to `auth.py`. This refactoring centralizes all
# authentication and user management logic, making the system more modular,
# secure, and maintainable. `auth.py` now acts as the single source of truth
# for user management, and this `db.py` module is solely responsible for
# database connection and schema setup.