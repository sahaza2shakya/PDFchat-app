from pydantic_settings import BaseSettings
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    openai_api_key: str
    mongodb_uri: str
    mongodb_database_name: str = "pdfchat"
    mongodb_collection_name: str = "pdf_embeddings"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4-turbo-preview"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Check if .env file exists before loading settings
_env_file = os.path.join(os.path.dirname(__file__), ".env")
if not os.path.exists(_env_file):
    logger.warning(f".env file not found at {_env_file}")
    logger.warning("Please create a .env file with your configuration. See env.example for reference.")
    # Try to create from env.example
    _env_example = os.path.join(os.path.dirname(__file__), "env.example")
    if os.path.exists(_env_example):
        logger.info("Found env.example, you can copy it to .env and update with your credentials")

try:
    settings = Settings()
except Exception as e:
    logger.error(f"Failed to load settings: {e}")
    logger.error("Please ensure .env file exists and contains all required variables")
    raise

