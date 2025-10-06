"""
Configuration loader từ environment variables.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    """Settings cho ứng dụng."""
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # LangSmith
    langsmith_api_key: str = os.getenv("LANGSMITH_API_KEY", "")
    langsmith_tracing: bool = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    langsmith_project: str = os.getenv("LANGSMITH_PROJECT", "ai-coaching-bot")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/coaching_bot.db")
    
    # Application
    app_name: str = os.getenv("APP_NAME", "AI Coaching Bot")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # FastAPI
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # Streamlit
    streamlit_port: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    data_dir: Path = base_dir / "data"
    docs_dir: Path = base_dir / "docs"
    faiss_index_dir: Path = base_dir / "faiss_index"
    logs_dir: Path = base_dir / "logs"
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


# Singleton instance
settings = Settings()

# Ensure directories exist
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.faiss_index_dir.mkdir(parents=True, exist_ok=True)
settings.logs_dir.mkdir(parents=True, exist_ok=True)
