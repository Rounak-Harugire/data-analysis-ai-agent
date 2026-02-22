import os
from dotenv import load_dotenv

load_dotenv()

# Groq API Key (used internally by CrewAI via environment)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# File size limit (default 5MB)
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 5))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024