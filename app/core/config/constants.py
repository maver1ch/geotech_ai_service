"""
Application Constants
Centralized configuration constants to replace hard-coded values
"""

# RAG Configuration Constants
class RAGConstants:
    MIN_KEYWORDS_THRESHOLD = 3
    VECTOR_MAX_CHUNKS = 6
    HYBRID_VECTOR_CHUNKS = 4
    KEYWORD_CHUNKS = 3
    DEFAULT_TOP_K_RETRIEVAL = 3
    DEFAULT_SIMILARITY_THRESHOLD = 0.1
    
    # Markdown chunking constants
    MIN_CHUNK_SIZE = 600
    MAX_CHUNK_SIZE = 1200
    HEADER_MERGE_THRESHOLD = 200
    
    # Contextualization constants
    MIN_CONTEXTUALIZATION_WORD_COUNT = 20
    CODE_BLOCK_THRESHOLD = 2
    TABLE_PIPE_THRESHOLD = 10
    
    # PDF OCR constants
    MAX_PAGES_PER_CHUNK = 5
    CHUNKING_PAGE_THRESHOLD = 5
    OCR_MAX_RETRIES = 3
    OCR_MAX_OUTPUT_TOKENS = 32768
    OCR_TEMPERATURE = 0.1
    
    # PDF utilities constants
    PDF_TEXT_SAMPLE_MAX_PAGES = 2
    TOKEN_TO_CHAR_RATIO = 4

# Database Configuration Constants  
class DatabaseConstants:
    DEFAULT_QDRANT_HOST = "localhost"
    DEFAULT_QDRANT_PORT = 6333
    DEFAULT_MONGODB_HOST = "localhost"  
    DEFAULT_MONGODB_PORT = 27017
    DEFAULT_VECTOR_SIZE = 3072
    DEFAULT_QDRANT_COLLECTION = "geotech_knowledge"
    DEFAULT_MONGODB_DATABASE = "geotech_db"
    DEFAULT_MONGODB_COLLECTION = "documents"

# LLM Configuration Constants
class LLMConstants:
    DEFAULT_OPENAI_MODEL = "gpt-5-mini"
    DEFAULT_EMBEDDING_MODEL = "text-embedding-3-large"
    DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
    DEFAULT_GEMINI_VISION_MODEL = "gemini-1.5-pro"
    DEFAULT_TIMEOUT = 1
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_TEMPERATURE = 0.1
    DEFAULT_MAX_TOKENS = 8192
    DEFAULT_MAX_COMPLETION_TOKENS = 3000

# API Configuration Constants
class APIConstants:
    DEFAULT_HOST = "0.0.0.0"
    DEFAULT_PORT = 8000
    DEFAULT_QUESTION_MAX_LENGTH = 1000
    DEFAULT_API_DOCS_ENABLED = True

# Validation Constants
class ValidationConstants:
    MIN_TEMPERATURE = 0.0
    MAX_TEMPERATURE = 2.0
    MIN_SIMILARITY_THRESHOLD = 0.0
    MAX_SIMILARITY_THRESHOLD = 1.0
    MIN_PHI_ANGLE = 0
    MAX_PHI_ANGLE = 40

# Application Constants
class AppConstants:
    DEFAULT_APP_NAME = "Geotech AI Service"
    DEFAULT_APP_VERSION = "1.0.0"
    DEFAULT_LOG_LEVEL = "INFO"
    DEFAULT_ENVIRONMENT = "development"
    DEFAULT_LANGFUSE_HOST = "https://cloud.langfuse.com"

# Tool Constants
class ToolConstants:
    BEARING_CAPACITY_FACTORS = {
        0: (5.7, 1.0, 0.0),
        5: (7.3, 1.6, 0.5),
        10: (9.6, 2.7, 1.2),
        15: (12.9, 4.4, 2.5),
        20: (17.7, 7.4, 5.0),
        25: (25.1, 12.7, 9.7),
        30: (37.2, 22.5, 19.7),
        35: (57.8, 41.4, 42.4),
        40: (95.7, 81.3, 100.4)
    }