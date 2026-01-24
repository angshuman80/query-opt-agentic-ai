"""Load environment variables for the project."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the project root directory
project_root = Path(__file__).parent
env_file = project_root / ".env"

# Load environment variables
if env_file.exists():
    load_dotenv(env_file)
    print(f"Loaded environment variables from {env_file}")
else:
    print(f"No .env file found at {env_file}")

# Verify key variables are loaded
required_vars = ["GROQ_API_KEY", "OPENAI_API_KEY", "LANGSMITH_API_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"Warning: Missing environment variables: {missing_vars}")
else:
    print("All required environment variables are loaded")
