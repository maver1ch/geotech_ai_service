"""
Logging Configuration
Structured logging setup with trace_id support for observability
"""

import logging
import logging.config
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from .settings import get_settings

class TraceFormatter(logging.Formatter):
    """Custom formatter that includes trace_id in log records"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Add trace_id from context if available
        trace_id = getattr(record, 'trace_id', None)
        if trace_id:
            record.trace_id = trace_id
        else:
            record.trace_id = 'no-trace'
        
        # Add timestamp in ISO format
        record.timestamp = datetime.now(timezone.utc).isoformat()
        
        # Format the message
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "trace_id": getattr(record, 'trace_id', 'no-trace')
        }
        
        # Add extra fields if present
        if hasattr(record, 'agent_step'):
            log_data["agent_step"] = record.agent_step
        if hasattr(record, 'duration_ms'):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, 'tool_name'):
            log_data["tool_name"] = record.tool_name
        if hasattr(record, 'retrieval_count'):
            log_data["retrieval_count"] = record.retrieval_count
            
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)

class TraceAdapter(logging.LoggerAdapter):
    """Logger adapter that automatically adds trace_id to log records"""
    
    def __init__(self, logger: logging.Logger, trace_id: str):
        super().__init__(logger, {"trace_id": trace_id})
        self.trace_id = trace_id
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Add trace_id to extra fields"""
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"]["trace_id"] = self.trace_id
        return msg, kwargs
    
    def log_agent_step(self, step: str, message: str, duration_ms: Optional[float] = None, **extra) -> None:
        """Log agent workflow step with structured data"""
        log_extra = {
            "trace_id": self.trace_id,
            "agent_step": step,
            **extra
        }
        if duration_ms is not None:
            log_extra["duration_ms"] = duration_ms
            
        self.info(message, extra=log_extra)

def setup_logging() -> None:
    """Setup application logging configuration"""
    settings = get_settings()
    logs_dir = settings.get_logs_directory()
    
    # Create logs directory if it doesn't exist
    logs_dir.mkdir(exist_ok=True)
    
    # Logging configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": TraceFormatter,
                "format": "[{timestamp}] {levelname:8} | {trace_id:12} | {name:25} | {message}",
                "style": "{"
            },
            "json": {
                "()": JSONFormatter
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": settings.LOG_LEVEL,
                "stream": sys.stdout
            },
            "file_info": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "level": "INFO",
                "filename": str(logs_dir / "info.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8"
            },
            "file_error": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "level": "ERROR", 
                "filename": str(logs_dir / "error.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8"
            }
        },
        "loggers": {
            "app": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file_info", "file_error"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "file_error"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console"]
        }
    }
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Log setup completion
    logger = logging.getLogger("app.config")
    logger.info(f"Logging configured - Level: {settings.LOG_LEVEL}, Logs dir: {logs_dir}")

def get_trace_logger(trace_id: str, logger_name: str = "app") -> TraceAdapter:
    """Get a logger adapter with trace_id context"""
    base_logger = logging.getLogger(logger_name)
    return TraceAdapter(base_logger, trace_id)

# Initialize logging when module is imported
if not logging.getLogger().hasHandlers():
    setup_logging()