import bcrypt
from supabase import create_client, Client
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from config import Config
import streamlit as st

# Initialize Supabase client
try:
    Config.validate_config()
    supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
except Exception as e:
    st.error(f"❌ Database configuration error: {e}")
    supabase = None


# ============================================
# Password Security Functions
# ============================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password to verify
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


# ============================================
# Rate Limiting Functions
# ============================================

def check_login_attempts(email: str) -> bool:
    """
    Check if user has exceeded login attempts limit.
    
    Args:
        email: User's email address
        
    Returns:
        True if attempts are within limit, False if exceeded
    """
    try:
        cutoff_time = datetime.now() - timedelta(minutes=Config.LOGIN_TIMEOUT_MINUTES)
        
        result = supabase.table('login_attempts').select('*').eq('email', email).gte('attempted_at', cutoff_time.isoformat()).execute()
        
        attempts = len(result.data) if result.data else 0
        
        return attempts < Config.MAX_LOGIN_ATTEMPTS
    except Exception as e:
        print(f"Error checking login attempts: {e}")
        return True  # Allow login on error to avoid blocking legitimate users


def record_login_attempt(email: str, success: bool):
    """
    Record a login attempt for rate limiting.
    
    Args:
        email: User's email address
        success: Whether the login was successful
    """
    try:
        supabase.table('login_attempts').insert({
            'email': email.lower(),
            'success': success,
            'attempted_at': datetime.now().isoformat()
        }).execute()
        
        # Clean up old attempts (older than timeout period)
        cutoff_time = datetime.now() - timedelta(minutes=Config.LOGIN_TIMEOUT_MINUTES * 2)
        supabase.table('login_attempts').delete().lt('attempted_at', cutoff_time.isoformat()).execute()
    except Exception as e:
        print(f"Error recording login attempt: {e}")


def clear_login_attempts(email: str):
    """
    Clear login attempts for a user after successful login.
    
    Args:
        email: User's email address
    """
    try:
        supabase.table('login_attempts').delete().eq('email', email.lower()).execute()
    except Exception as e:
        print(f"Error clearing login attempts: {e}")


# ============================================
# User Management Functions
# ============================================

def create_user(username: str, email: str, password: str) -> Dict[str, Any]:
    """
    Create a new user with hashed password.
    
    Args:
        username: Unique username
        email: User's email address
        password: Plain text password (will be hashed)
        
    Returns:
        Dictionary with success status and message
    """
    try:
        # Hash the password
        hashed_password = hash_password(password)
        
        # Insert user into database
        result = supabase.table('users').insert({
            'username': username.strip(),
            'email': email.lower().strip(),
            'password_hash': hashed_password,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        if result.data:
            return {
                'success': True,
                'message': 'User created successfully',
                'user_id': result.data[0]['id']
            }
        else:
            return {
                'success': False,
                'message': 'Failed to create user'
            }
            
    except Exception as e:
        error_msg = str(e).lower()
        
        if 'duplicate' in error_msg and 'username' in error_msg:
            return {
                'success': False,
                'message': 'Username already exists. Please choose another one.'
            }
        elif 'duplicate' in error_msg and 'email' in error_msg:
            return {
                'success': False,
                'message': 'Email already registered. Please login or use a different email.'
            }
        else:
            return {
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }


def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    """
    Authenticate a user with email and password.
    
    Args:
        email: User's email address
        password: Plain text password
        
    Returns:
        Dictionary with authentication result and user data
    """
    email = email.lower().strip()
    
    # Check rate limiting
    if not check_login_attempts(email):
        return {
            'success': False,
            'message': f'Too many login attempts. Please try again in {Config.LOGIN_TIMEOUT_MINUTES} minutes.'
        }
    
    try:
        # Fetch user from database
        result = supabase.table('users').select('*').eq('email', email).execute()
        
        if not result.data or len(result.data) == 0:
            record_login_attempt(email, False)
            return {
                'success': False,
                'message': 'Invalid email or password'
            }
        
        user = result.data[0]
        
        # Verify password
        if verify_password(password, user['password_hash']):
            # Successful login
            record_login_attempt(email, True)
            clear_login_attempts(email)
            
            # Update last login
            supabase.table('users').update({
                'last_login': datetime.now().isoformat()
            }).eq('id', user['id']).execute()
            
            return {
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email']
                }
            }
        else:
            record_login_attempt(email, False)
            return {
                'success': False,
                'message': 'Invalid email or password'
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Authentication error: {str(e)}'
        }


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve user information by user ID.
    
    Args:
        user_id: User's unique identifier
        
    Returns:
        User dictionary or None if not found
    """
    try:
        result = supabase.table('users').select('id, username, email, created_at, last_login').eq('id', user_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None


def update_user_profile(user_id: int, username: str = None, email: str = None) -> Dict[str, Any]:
    """
    Update user profile information.
    
    Args:
        user_id: User's unique identifier
        username: New username (optional)
        email: New email (optional)
        
    Returns:
        Dictionary with success status and message
    """
    try:
        update_data = {}
        
        if username:
            update_data['username'] = username.strip()
        if email:
            update_data['email'] = email.lower().strip()
        
        if not update_data:
            return {'success': False, 'message': 'No data to update'}
        
        result = supabase.table('users').update(update_data).eq('id', user_id).execute()
        
        if result.data:
            return {'success': True, 'message': 'Profile updated successfully'}
        else:
            return {'success': False, 'message': 'Failed to update profile'}
            
    except Exception as e:
        return {'success': False, 'message': f'Update failed: {str(e)}'}


def change_password(user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
    """
    Change user's password after verifying old password.
    
    Args:
        user_id: User's unique identifier
        old_password: Current password
        new_password: New password
        
    Returns:
        Dictionary with success status and message
    """
    try:
        # Get current user
        result = supabase.table('users').select('password_hash').eq('id', user_id).execute()
        
        if not result.data:
            return {'success': False, 'message': 'User not found'}
        
        user = result.data[0]
        
        # Verify old password
        if not verify_password(old_password, user['password_hash']):
            return {'success': False, 'message': 'Current password is incorrect'}
        
        # Hash and update new password
        new_hash = hash_password(new_password)
        supabase.table('users').update({
            'password_hash': new_hash
        }).eq('id', user_id).execute()
        
        return {'success': True, 'message': 'Password changed successfully'}
        
    except Exception as e:
        return {'success': False, 'message': f'Password change failed: {str(e)}'}


# ============================================
# Feedback Functions
# ============================================

def save_feedback(user_id: int, rating: int, comment: str = None) -> bool:
    """
    Save user feedback to database.
    
    Args:
        user_id: User's unique identifier
        rating: Rating value (1-5)
        comment: Optional feedback comment
        
    Returns:
        True if successful, False otherwise
    """
    print(f"\n=== save_feedback called ===")
    print(f"user_id: {user_id} (type: {type(user_id)})")
    print(f"rating: {rating} (type: {type(rating)})")
    print(f"comment: {comment} (type: {type(comment)})")
    
    try:
        data_to_insert = {
            'user_id': user_id,
            'rating': rating,
            'comment': comment,
            'created_at': datetime.now().isoformat()
        }
        
        print(f"Data to insert: {data_to_insert}")
        
        result = supabase.table('feedback').insert(data_to_insert).execute()
        
        print(f"Supabase result: {result}")
        print(f"Result data: {result.data}")
        print(f"Result count: {result.count if hasattr(result, 'count') else 'N/A'}")
        
        success = bool(result.data)
        print(f"Returning: {success}")
        
        return success
        
    except Exception as e:
        print(f"Error saving feedback: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

def get_user_feedback(user_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve all feedback submitted by a user.
    
    Args:
        user_id: User's unique identifier
        
    Returns:
        List of feedback dictionaries
    """
    try:
        result = supabase.table('feedback').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching feedback: {e}")
        return []


# ============================================
# Data Analytics Functions
# ============================================

def save_upload_metadata(user_id: int, filename: str, file_size: int, row_count: int) -> bool:
    """
    Save metadata about uploaded files for analytics.
    
    Args:
        user_id: User's unique identifier
        filename: Name of uploaded file
        file_size: Size of file in bytes
        row_count: Number of data rows in file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        result = supabase.table('upload_history').insert({
            'user_id': user_id,
            'filename': filename,
            'file_size': file_size,
            'row_count': row_count,
            'uploaded_at': datetime.now().isoformat()
        }).execute()
        
        return bool(result.data)
    except Exception as e:
        print(f"Error saving upload metadata: {e}")
        return False


def get_user_uploads(user_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve upload history for a user.
    
    Args:
        user_id: User's unique identifier
        
    Returns:
        List of upload metadata dictionaries
    """
    try:
        result = supabase.table('upload_history').select('*').eq('user_id', user_id).order('uploaded_at', desc=True).limit(10).execute()
        
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching uploads: {e}")
        return []


# ============================================
# Database Initialization
# ============================================

def initialize_database():
    """
    Initialize database tables if they don't exist.
    Note: In Supabase, tables should be created via the Supabase dashboard or SQL editor.
    This function is kept for reference and migration purposes.
    """
    # SQL schema is provided separately for Supabase setup
    pass

# ============================================
# Upload History Functions (UPDATED)
# ============================================

def save_upload_record(user_id: int, filename: str, file_path: str, file_size: int, row_count: int = None) -> Optional[int]:
    """
    Save upload metadata to database with file path.
    
    Args:
        user_id: User's unique identifier
        filename: Name of uploaded file
        file_path: Full path where file is stored
        file_size: Size of file in bytes
        row_count: Number of data rows in file
        
    Returns:
        Upload ID if successful, None otherwise
    """
    try:
        result = supabase.table('upload_history').insert({
            'user_id': user_id,
            'filename': filename,
            'file_path': file_path,
            'file_size': file_size,
            'row_count': row_count,
            'uploaded_at': datetime.now().isoformat()
        }).execute()
        
        if result.data:
            return result.data[0]['id']
        return None
    except Exception as e:
        print(f"Error saving upload record: {e}")
        return None


def get_latest_upload(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get the most recent upload for a user.
    
    Args:
        user_id: User's unique identifier
        
    Returns:
        Dictionary with upload details or None
    """
    try:
        result = supabase.table('upload_history').select('*').eq('user_id', user_id).order('uploaded_at', desc=True).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error fetching latest upload: {e}")
        return None


def get_user_uploads(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve upload history for a user.
    
    Args:
        user_id: User's unique identifier
        limit: Maximum number of uploads to return
        
    Returns:
        List of upload metadata dictionaries
    """
    try:
        result = supabase.table('upload_history').select('*').eq('user_id', user_id).order('uploaded_at', desc=True).limit(limit).execute()
        
        return result.data if result.data else []
    except Exception as e:
        print(f"Error fetching uploads: {e}")
        return []


# Update the old function to be deprecated
def save_upload_metadata(user_id: int, filename: str, file_size: int, row_count: int) -> bool:
    """
    DEPRECATED: Use save_upload_record() instead.
    Save metadata about uploaded files for analytics (without file_path).
    """
    try:
        result = supabase.table('upload_history').insert({
            'user_id': user_id,
            'filename': filename,
            'file_size': file_size,
            'row_count': row_count,
            'uploaded_at': datetime.now().isoformat()
        }).execute()
        
        return bool(result.data)
    except Exception as e:
        print(f"Error saving upload metadata: {e}")
        return False