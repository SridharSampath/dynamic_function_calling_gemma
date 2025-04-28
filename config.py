import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

# Model name
MODEL_NAME = "gemma3:1b"

if not SERPER_API_KEY:
    raise ValueError("Serper API key not found. Please set SERPER_API_KEY in your .env file.")