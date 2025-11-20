import streamlit as st
import bcrypt
from db import create_users_table, add_user, get_user_by_email

# Ensure the users table exists when the module is imported.
# This is a simple way to handle DB initialization for this project.
create_users_table()


def _hash_password(password: str) -> bytes:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def _verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """Verifies a plain password against a hashed version."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)


def register_user(email: str, password: str) -> bool:
    """
    Registers a new user.
    Hashes the password and stores the user in the database.
    Returns False if the user already exists.
    """
    if get_user_by_email(email):
        st.error("An account with this email already exists.")
        return False

    hashed_password = _hash_password(password)
    try:
        add_user(email, hashed_password)
        return True
    except Exception as e:
        st.error(f"An error occurred during registration: {e}")
        return False


def login(email: str, password: str) -> bool:
    """
    Logs a user in.
    Verifies credentials and sets session state upon success.
    """
    user_data = get_user_by_email(email)
    if user_data:
        stored_hashed_password = user_data[2]  # Assuming (id, email, password_hash)
        if _verify_password(password, stored_hashed_password):
            st.session_state["logged_in"] = True
            st.session_state["email"] = email
            return True
    st.error("Invalid email or password.")
    return False


def is_logged_in() -> bool:
    """Checks if a user is currently logged in via session state."""
    return st.session_state.get("logged_in", False)


def logout():
    """Logs out the current user and clears relevant session state."""
    keys_to_clear = ["logged_in", "email", "save_path", "df"]
    for key in keys_to_clear:
        st.session_state.pop(key, None)


def get_current_user_email() -> str | None:
    """Returns the email of the currently logged-in user."""
    if is_logged_in():
        return st.session_state.get("email")
    return None
