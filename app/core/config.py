from dotenv import load_dotenv
import os

# Set .env file path
env_path = ".env"
if not os.path.exists(env_path):
    raise FileNotFoundError(f".env file not found at {env_path}")

# Load environment variables from .env file
load_dotenv(dotenv_path=env_path)

# Define configuration variables
class Settings:
    # Configure HuggingFace API Token
    HUGGINGFACE_API_TOKEN: str = os.getenv("HF_TOKEN") or ""
    GOOGLE_GENAI_API: str = os.getenv("GEMINI_API") or ""