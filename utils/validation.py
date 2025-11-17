import re
import pandas as pd
from typing import Tuple, Optional
from config import Config

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email or not email.strip():
        return False, "Email address is required"
    
    email = email.strip().lower()
    
    # RFC 5322 simplified regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Please enter a valid email address (e.g., user@example.com)"
    
    if len(email) > 254:  # RFC 5321
        return False, "Email address is too long"
    
    return True, None


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username format.
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username or not username.strip():
        return False, "Username is required"
    
    username = username.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 30:
        return False, "Username must be less than 30 characters"
    
    # Allow alphanumeric, underscore, and hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    if username[0] in '_-' or username[-1] in '_-':
        return False, "Username cannot start or end with underscore or hyphen"
    
    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength based on configuration requirements.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < Config.MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {Config.MIN_PASSWORD_LENGTH} characters long"
    
    if len(password) > 128:
        return False, "Password is too long (max 128 characters)"
    
    errors = []
    
    if Config.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        errors.append("one uppercase letter")
    
    if Config.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        errors.append("one lowercase letter")
    
    if Config.REQUIRE_DIGIT and not re.search(r'\d', password):
        errors.append("one number")
    
    if Config.REQUIRE_SPECIAL_CHAR and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("one special character (!@#$%^&* etc.)")
    
    if errors:
        return False, f"Password must contain at least {', '.join(errors)}"
    
    return True, None


def validate_csv_structure(df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
    """
    Validate that uploaded CSV has required columns and valid data.
    
    Args:
        df: Pandas DataFrame to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "File is empty or could not be read"
    
    # Check required columns
    required_columns = ['Date', 'Sales']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Check for minimum number of rows
    if len(df) < 2:
        return False, "File must contain at least 2 rows of data"
    
    # Validate Date column
    try:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        if df['Date'].isna().all():
            return False, "Date column contains no valid dates. Expected format: YYYY-MM-DD or MM/DD/YYYY"
    except Exception as e:
        return False, f"Error parsing Date column: {str(e)}"
    
    # Validate Sales column
    try:
        df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
        if df['Sales'].isna().all():
            return False, "Sales column contains no valid numeric values"
    except Exception as e:
        return False, f"Error parsing Sales column: {str(e)}"
    
    # Check for too many NaN values
    nan_percentage = (df[['Date', 'Sales']].isna().sum().sum() / (len(df) * 2)) * 100
    if nan_percentage > 50:
        return False, f"Too many missing values ({nan_percentage:.1f}%). Please clean your data before uploading"
    
    return True, None


def validate_file_upload(uploaded_file) -> Tuple[bool, Optional[str]]:
    """
    Validate file upload before processing.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Check file extension
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension not in Config.ALLOWED_EXTENSIONS:
        return False, f"File type '.{file_extension}' not allowed. Please upload: {', '.join(Config.ALLOWED_EXTENSIONS)}"
    
    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > Config.MAX_FILE_SIZE_MB:
        return False, f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({Config.MAX_FILE_SIZE_MB}MB)"
    
    if file_size_mb < 0.001:  # Less than 1KB
        return False, "File appears to be empty or corrupted"
    
    return True, None


def validate_feedback(rating: int, comment: str) -> Tuple[bool, Optional[str]]:
    """
    Validate feedback submission.
    
    Args:
        rating: Rating value (1-5)
        comment: Feedback comment
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(rating, int) or not (1 <= rating <= 5):
        return False, "Rating must be between 1 and 5 stars"
    
    if comment and len(comment) > 1000:
        return False, "Comment is too long (maximum 1000 characters)"
    
    return True, None


def sanitize_input(text: str, max_length: int = 255) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Limit length
    text = text[:max_length]
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    return text