import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_PUBLISHABLE_KEY: str = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    SUPABASE_SECRET_KEY: str = os.getenv("SUPABASE_SECRET_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    JINA_API_KEY: str = os.getenv("JINA_API_KEY", "")
    LANGSEARCH_API_KEY: str = os.getenv("LANGSEARCH_API_KEY", "")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

settings = Settings()