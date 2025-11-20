"""
Configuration Management for the Sales Forecasting Application.

This module centralizes all configuration settings for the application,
making it easier to manage and modify settings without changing the core
application logic. It handles database connections, application secrets,
and other tunable parameters.

It is best practice to use environment variables for sensitive information
like secret keys and database credentials, especially in production. This
module is set up to read from a `.env` file for local development.

Attributes:
    BASE_DIR (str): The absolute path to the project's root directory.
    SECRET_KEY (str): A secret key for cryptographic signing (e.g., sessions).
                      Should be set via environment variables in production.
    DATABASE_URL (str): The connection string for the application's database.
    FORECASTING_CONFIG (dict): Configuration parameters for the forecasting model.
    DATA_UPLOAD_CONFIG (dict): Configuration for the data upload feature.
    PAGE_CONFIG (dict): Configuration for Streamlit page titles and icons.
"""

import os
import secrets
from dotenv import load_dotenv

# --- Project Root ---
# Determine the absolute path of the project's root directory.
# This is crucial for constructing reliable paths to files like databases,
# ensuring the application runs correctly regardless of the working directory.
# We assume this config.py file is located at the root of the project.
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # __file__ is not defined in some environments (e.g., interactive interpreter)
    BASE_DIR = os.getcwd()


# --- Environment Variables ---
# Load environment variables from a .env file if it exists. This allows for
# secure and flexible configuration management, especially for local development.
# The .env file should be included in .gitignore to prevent committing secrets.
dotenv_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


# --- Application Secrets ---
# SECRET_KEY is used for cryptographic signing, such as securing user sessions.
# It is critical that this is a long, random, and secret string.
# For production environments, this MUST be set as an environment variable.
# A default, insecure value is provided for development convenience, but a
# warning is issued if the environment variable is not found.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    print(
        "WARNING: SECRET_KEY environment variable not set. "
        "Using a default, insecure key for development. "
        "Please set a strong, random key in a .env file or environment variable for production."
    )
    # Generate a temporary key for development if none is provided.
    # This is more secure than a hardcoded default.
    SECRET_KEY = secrets.token_hex(16)


# --- Database Configuration ---
# The connection string for the application's database.
# By default, it uses a SQLite database file named 'users.db' located
# in the project's root directory. Using os.path.join ensures the path
# is constructed correctly across different operating systems.
DB_FILENAME = "users.db"
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, DB_FILENAME)}"


# --- Forecasting Engine Configuration ---
# Parameters for the sales forecasting model.
# Centralizing these settings makes it easy to tune the model's behavior
# without modifying the core forecasting logic.
FORECASTING_CONFIG = {
    "DEFAULT_PERIODS": 30,          # Default number of days to forecast.
    "DEFAULT_FREQ": "D",            # Default frequency of the forecast ('D' for daily).
    "MIN_TRAINING_DATA_POINTS": 50, # Minimum data points required to train a model.
    "DATE_COLUMN": "ds",            # Expected name for the date column.
    "TARGET_COLUMN": "y",           # Expected name for the target value column.
}


# --- Data Upload Configuration ---
# Configuration for the data upload feature, defining constraints and expectations
# for user-uploaded files.
DATA_UPLOAD_CONFIG = {
    "ALLOWED_EXTENSIONS": [".csv", ".xlsx"],
    "MAX_FILE_SIZE_MB": 10,         # Maximum allowed file size in megabytes.
    "REQUIRED_COLUMNS": [
        FORECASTING_CONFIG["DATE_COLUMN"],
        FORECASTING_CONFIG["TARGET_COLUMN"]
    ],
}


# --- Streamlit Page Configuration ---
# Centralized configuration for Streamlit page titles and icons.
# This helps maintain a consistent look and feel across the application.
PAGE_CONFIG = {
    "HOME": {"page_title": "Sales Forecasting App", "page_icon": "🏠"},
    "LOGIN": {"page_title": "Login", "page_icon": "🔑"},
    "REGISTER": {"page_title": "Register", "page_icon": "📝"},
    "DASHBOARD": {"page_title": "Sales Dashboard", "page_icon": "📊"},
    "DATA_UPLOAD": {"page_title": "Upload Data", "page_icon": "📤"},
    "SALES_FORECASTING": {"page_title": "Sales Forecasting", "page_icon": "📈"},
}