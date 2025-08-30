"""
Application Configuration Settings
Pydantic-based settings management with environment variable validation
"""

import os
from pathlib import Path
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

from .constants import (
    RAGConstants, DatabaseConstants, LLMConstants, 
    APIConstants, AppConstants, ValidationConstants
)

class GeotechSettings(BaseSettings):
    """Main application settings with environment variable binding"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key for LLM services")
    OPENAI_MODEL: str = Field(default=LLMConstants.DEFAULT_OPENAI_MODEL, description="OpenAI model to use")
    OPENAI_EMBEDDING_MODEL: str = Field(default=LLMConstants.DEFAULT_EMBEDDING_MODEL, description="OpenAI embedding model")
    
    # Google GenAI Configuration (for advanced OCR)
    GOOGLE_GENAI_API_KEY: str = Field(..., description="Google GenAI API key for multimodal processing")
    GOOGLE_GENAI_MODEL: str = Field(default=LLMConstants.DEFAULT_GEMINI_MODEL, description="Google GenAI model for text tasks")
    GOOGLE_GENAI_MODEL_VISION: str = Field(default=LLMConstants.DEFAULT_GEMINI_VISION_MODEL, description="Google GenAI model for vision tasks")
    LLM_MAX_TOKENS: int = Field(default=LLMConstants.DEFAULT_MAX_TOKENS, description="Maximum tokens for LLM responses")
    
    # Qdrant Configuration  
    QDRANT_HOST: str = Field(default=DatabaseConstants.DEFAULT_QDRANT_HOST, description="Qdrant server host")
    QDRANT_PORT: int = Field(default=DatabaseConstants.DEFAULT_QDRANT_PORT, description="Qdrant server port")
    QDRANT_COLLECTION_NAME: str = Field(default=DatabaseConstants.DEFAULT_QDRANT_COLLECTION, description="Qdrant collection name")
    
    # MongoDB Configuration
    MONGODB_HOST: str = Field(default=DatabaseConstants.DEFAULT_MONGODB_HOST, description="MongoDB server host")
    MONGODB_PORT: int = Field(default=DatabaseConstants.DEFAULT_MONGODB_PORT, description="MongoDB server port")
    MONGODB_DATABASE: str = Field(default=DatabaseConstants.DEFAULT_MONGODB_DATABASE, description="MongoDB database name")
    MONGODB_COLLECTION: str = Field(default=DatabaseConstants.DEFAULT_MONGODB_COLLECTION, description="MongoDB collection name")
    
    # LangFuse Configuration (Optional)
    LANGFUSE_PUBLIC_KEY: Optional[str] = Field(default=None, description="LangFuse public key for observability")
    LANGFUSE_SECRET_KEY: Optional[str] = Field(default=None, description="LangFuse secret key")
    LANGFUSE_HOST: str = Field(default=AppConstants.DEFAULT_LANGFUSE_HOST, description="LangFuse host URL")
    
    # Application Configuration
    APP_NAME: str = Field(default=AppConstants.DEFAULT_APP_NAME, description="Application name")
    APP_VERSION: str = Field(default=AppConstants.DEFAULT_APP_VERSION, description="Application version")
    LOG_LEVEL: str = Field(default=AppConstants.DEFAULT_LOG_LEVEL, description="Logging level")
    ENVIRONMENT: str = Field(default=AppConstants.DEFAULT_ENVIRONMENT, description="Environment (development/staging/production)")
    
    # API Configuration
    API_HOST: str = Field(default=APIConstants.DEFAULT_HOST, description="API server host")
    API_PORT: int = Field(default=APIConstants.DEFAULT_PORT, description="API server port") 
    API_DOCS_ENABLED: bool = Field(default=APIConstants.DEFAULT_API_DOCS_ENABLED, description="Enable API documentation")
    
    # RAG Configuration
    CHUNK_SIZE: int = Field(default=RAGConstants.DEFAULT_CHUNK_SIZE, description="Text chunk size for document processing")
    CHUNK_OVERLAP: int = Field(default=RAGConstants.DEFAULT_CHUNK_OVERLAP, description="Text chunk overlap")
    TOP_K_RETRIEVAL: int = Field(default=RAGConstants.DEFAULT_TOP_K_RETRIEVAL, description="Number of documents to retrieve")
    SIMILARITY_THRESHOLD: float = Field(default=RAGConstants.DEFAULT_SIMILARITY_THRESHOLD, description="Minimum similarity score for retrieval")
    
    # LLM Configuration
    LLM_TIMEOUT: int = Field(default=LLMConstants.DEFAULT_TIMEOUT, description="LLM API timeout in seconds")
    LLM_MAX_RETRIES: int = Field(default=LLMConstants.DEFAULT_MAX_RETRIES, description="Maximum LLM API retry attempts")
    LLM_TEMPERATURE: float = Field(default=LLMConstants.DEFAULT_TEMPERATURE, description="LLM temperature for responses")
    LLM_MAX_COMPLETION_TOKENS: int = Field(default=LLMConstants.DEFAULT_MAX_COMPLETION_TOKENS, description="Maximum completion tokens in LLM response")
    
    # Agent Configuration  
    AGENT_CONFIG_PATH: str = Field(default="app/core/config/agents/geotech_agent.yaml", description="Path to agent configuration file")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {valid_levels}")
        return v.upper()
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v):
        valid_envs = ["development", "staging", "production", "testing"]
        if v.lower() not in valid_envs:
            raise ValueError(f"ENVIRONMENT must be one of: {valid_envs}")
        return v.lower()
    
    @field_validator("SIMILARITY_THRESHOLD")
    @classmethod
    def validate_similarity_threshold(cls, v):
        if not ValidationConstants.MIN_SIMILARITY_THRESHOLD <= v <= ValidationConstants.MAX_SIMILARITY_THRESHOLD:
            raise ValueError(f"SIMILARITY_THRESHOLD must be between {ValidationConstants.MIN_SIMILARITY_THRESHOLD} and {ValidationConstants.MAX_SIMILARITY_THRESHOLD}")
        return v
    
    @field_validator("LLM_TEMPERATURE")
    @classmethod
    def validate_temperature(cls, v):
        if not ValidationConstants.MIN_TEMPERATURE <= v <= ValidationConstants.MAX_TEMPERATURE:
            raise ValueError(f"LLM_TEMPERATURE must be between {ValidationConstants.MIN_TEMPERATURE} and {ValidationConstants.MAX_TEMPERATURE}")
        return v
    
    def get_agent_config_path(self) -> Path:
        """Get absolute path to agent configuration file"""
        base_path = Path(__file__).parent.parent.parent.parent  # Go to project root
        return base_path / self.AGENT_CONFIG_PATH
    
    def get_logs_directory(self) -> Path:
        """Get logs directory path"""
        base_path = Path(__file__).parent.parent.parent.parent
        logs_dir = base_path / "logs"
        logs_dir.mkdir(exist_ok=True)
        return logs_dir
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT == "development"
    
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.ENVIRONMENT == "testing"
    
    def has_langfuse(self) -> bool:
        """Check if LangFuse is configured"""
        return bool(self.LANGFUSE_PUBLIC_KEY and self.LANGFUSE_SECRET_KEY)

def get_settings() -> GeotechSettings:
    """Get application settings"""
    return GeotechSettings()

# Convenience function for common settings
def get_openai_config() -> dict:
    """Get OpenAI configuration as dictionary"""
    settings = get_settings()
    return {
        "api_key": settings.OPENAI_API_KEY,
        "model": settings.OPENAI_MODEL,
        "timeout": settings.LLM_TIMEOUT,
        "max_retries": settings.LLM_MAX_RETRIES,
        "temperature": settings.LLM_TEMPERATURE,
        "max_completion_tokens": settings.LLM_MAX_COMPLETION_TOKENS
    }

def get_qdrant_config() -> dict:
    """Get Qdrant configuration as dictionary"""
    settings = get_settings()
    return {
        "host": settings.QDRANT_HOST,
        "port": settings.QDRANT_PORT,
        "collection_name": settings.QDRANT_COLLECTION_NAME
    }

def get_rag_config() -> dict:
    """Get RAG configuration as dictionary"""
    settings = get_settings()
    return {
        "chunk_size": settings.CHUNK_SIZE,
        "chunk_overlap": settings.CHUNK_OVERLAP,
        "top_k": settings.TOP_K_RETRIEVAL,
        "similarity_threshold": settings.SIMILARITY_THRESHOLD
    }

def get_mongodb_config() -> dict:
    """Get MongoDB configuration as dictionary"""
    settings = get_settings()
    return {
        "host": settings.MONGODB_HOST,
        "port": settings.MONGODB_PORT,
        "database": settings.MONGODB_DATABASE,
        "collection": settings.MONGODB_COLLECTION
    }