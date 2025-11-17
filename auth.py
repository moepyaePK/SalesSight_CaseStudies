import streamlit as st
from db import create_user, authenticate_user, get_user_by_id
from utils.validation import validate_email, validate_username, validate_password, sanitize_input
from datetime import datetime, timedelta
from config import Config

def register_user(username: str, email: str, password: str) -> dict:
    """
    Register a new user with validation.
    
    Args:
        username: Desired username
        email: User's email address
        password: User's password
        
    Returns:
        Dictionary with success status and message
    """
    # Sanitize inputs
    username = sanitize_input(username, 30)
    email = sanitize_input(email, 254)
    
    # Validate username
    valid, error = validate_username(username)
    if not valid:
        return {'success': False, 'message': error}
    
    # Validate email
    valid, error = validate_email(email)
    if not valid:
        return {'success': False, 'message': error}
    
    # Validate password
    valid, error = validate_password(password)
    if not valid:
        return {'success': False, 'message': error}
    
    # Create user in database
    result = create_user(username, email, password)
    return result


def login_user(email: str, password: str) -> dict:
    """
    Authenticate and login a user.
    
    Args:
        email: User's email address
        password: User's password
        
    Returns:
        Dictionary with authentication result
    """
    # Sanitize email
    email = sanitize_input(email, 254)
    
    # Basic validation
    if not email or not password:
        return {'success': False, 'message': 'Email and password are required'}
    
    # Authenticate
    result = authenticate_user(email, password)
    
    if result['success']:
        # Set session state
        st.session_state['logged_in'] = True
        st.session_state['user_id'] = result['user']['id']
        st.session_state['username'] = result['user']['username']
        st.session_state['email'] = result['user']['email']
        st.session_state['login_time'] = datetime.now()
    
    return result


def is_logged_in() -> bool:
    """
    Check if user is currently logged in.
    
    Returns:
        True if logged in, False otherwise
    """
    if not st.session_state.get('logged_in', False):
        return False
    
    # Check session timeout
    if 'login_time' in st.session_state:
        login_time = st.session_state['login_time']
        if datetime.now() - login_time > timedelta(seconds=Config.SESSION_TIMEOUT):
            logout()
            return False
    
    # Update last activity
    st.session_state['last_activity'] = datetime.now()
    
    return True


def logout():
    """
    Log out the current user and clear session state.
    """
    keys_to_clear = [
        'logged_in', 'user_id', 'username', 'email', 
        'login_time', 'last_activity', 'save_path', 
        'file_status', 'uploaded_files'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def require_auth(redirect_to: str = "Home.py"):
    """
    Decorator/function to require authentication for a page.
    Redirects to home if not logged in.
    
    Args:
        redirect_to: Page to redirect to if not authenticated
    """
    if not is_logged_in():
        st.warning("⚠️ Please log in to access this page.")
        st.switch_page(redirect_to)
        st.stop()


def get_current_user() -> dict:
    """
    Get current logged-in user information.
    
    Returns:
        Dictionary with user information or None if not logged in
    """
    if not is_logged_in():
        return None
    
    return {
        'id': st.session_state.get('user_id'),
        'username': st.session_state.get('username'),
        'email': st.session_state.get('email')
    }


def update_session_activity():
    """
    Update the last activity timestamp in session.
    Call this on user interactions to keep session alive.
    """
    if is_logged_in():
        st.session_state['last_activity'] = datetime.now()


def get_session_time_remaining() -> int:
    """
    Get remaining session time in seconds.
    
    Returns:
        Seconds remaining before session expires
    """
    if not is_logged_in() or 'login_time' not in st.session_state:
        return 0
    
    login_time = st.session_state['login_time']
    elapsed = (datetime.now() - login_time).total_seconds()
    remaining = Config.SESSION_TIMEOUT - elapsed
    
    return max(0, int(remaining))