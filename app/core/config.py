from dotenv import load_dotenv
import os
from pathlib import Path

# Set .env file path
env_path = Path(__file__).resolve().parent.parent.parent / '.env'

# Print the path to ensure it's correct
# print(f"Loading environment variables from: {env_path}")

# Load environment variables from .env file
load_dotenv(dotenv_path=env_path)

# Define configuration variables
class Settings:
    # Configure HuggingFace API Token
    HUGGINGFACE_API_TOKEN: str = os.getenv("HF_TOKEN") or ""

# print(f"HuggingFace API Token: {Settings.HUGGINGFACE_API_TOKEN}")