"""Configuration and environment setup for the project."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables once when this module is imported
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"

if env_file.exists():
    load_dotenv(env_file)

class Config:
    """Configuration class with environment variables."""
    
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    
    # LangSmith Configuration
    LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT")
    LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "query-opt-agentic-ai")
    
    @classmethod
    def validate(cls):
        """Validate required environment variables."""
        required = ["GROQ_API_KEY", "OPENAI_API_KEY"]
        missing = [var for var in required if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")
        
        return True

# Auto-validate on import
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please check your .env file in the project root")
