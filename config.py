"""
Configuration for deployment
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration - automatically detects environment
def get_api_url():
    """Get API URL based on environment"""
    # Check if running on Streamlit Cloud
    if os.getenv("STREAMLIT_SHARING_MODE"):
        # Production - use deployed API
        return os.getenv("API_URL", "https://pakistan-legal-api.onrender.com")
    else:
        # Local development
        return "http://localhost:8000"

API_BASE_URL = get_api_url()

# Other configurations
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
