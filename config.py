import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Centralized configuration management for SalesSight application.
    All sensitive data should be stored in environment variables.
    """
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Groq API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Application Settings
    APP_NAME = "SalesSight"
    APP_VERSION = "2.0.0"
    
    # Security Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    SESSION_TIMEOUT = 3600  # 1 hour in seconds
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_TIMEOUT_MINUTES = 15
    
    # Password Requirements
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL_CHAR = True
    
    # File Upload Settings
    UPLOAD_FOLDER = "tmp"
    MAX_FILE_SIZE_MB = 200
    ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
    
    # Database Settings
    DB_POOL_SIZE = 10
    DB_MAX_OVERFLOW = 20
    
    # Forecast Settings
    DEFAULT_FORECAST_DAYS = 30
    MAX_FORECAST_DAYS = 365
    FORECAST_MODELS = ['llama-3.3-70b-versatile']
    
    # Feature Flags
    ENABLE_EMAIL_NOTIFICATIONS = False
    ENABLE_EXPORT_REPORTS = True
    ENABLE_COLLABORATIVE_FEATURES = False
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        errors = []
        
        if not cls.SUPABASE_URL:
            errors.append("SUPABASE_URL is not set")
        if not cls.SUPABASE_KEY:
            errors.append("SUPABASE_KEY is not set")
        if not cls.GROQ_API_KEY:
            errors.append("GROQ_API_KEY is not set")
            
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
    
    @classmethod
    def get_database_url(cls):
        """Construct database URL from Supabase credentials"""
        if not cls.SUPABASE_URL:
            return None
        # Extract database URL from Supabase URL
        # Format: https://xxx.supabase.co -> postgresql://...
        return f"{cls.SUPABASE_URL}/rest/v1/"