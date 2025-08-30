"""
LangFuse Observability Client
Simple wrapper for LangFuse tracing integration with GeotechAgent workflow
"""

import logging
import uuid
from typing import Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime, timezone
from contextlib import contextmanager

if TYPE_CHECKING:
    from langfuse import Langfuse

try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    Langfuse = None

from ...core.config.settings import get_settings

logger = logging.getLogger(__name__)

class LangFuseClient:
    """Simple LangFuse client for agent workflow tracing"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional['Langfuse'] = None
        self.enabled = self._initialize_client()
        
    def _initialize_client(self) -> bool:
        """Initialize LangFuse client if configured"""
        if not LANGFUSE_AVAILABLE:
            logger.warning("LangFuse package not installed. Tracing disabled.")
            return False
            
        if not self.settings.has_langfuse():
            logger.info("LangFuse not configured. Tracing disabled.")
            return False
            
        try:
            self.client = Langfuse(
                public_key=self.settings.LANGFUSE_PUBLIC_KEY,
                secret_key=self.settings.LANGFUSE_SECRET_KEY,
                host=self.settings.LANGFUSE_HOST
            )
            logger.info("LangFuse client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LangFuse client: {e}")
            return False
    
    def start_trace(self, trace_name: str = "geotech_request") -> str:
        """Start a new trace and return trace_id"""
        trace_id = str(uuid.uuid4())
        
        if not self.enabled or not self.client:
            logger.debug(f"LangFuse disabled. Using mock trace_id: {trace_id}")
            return trace_id
            
        try:
            trace = self.client.trace(
                id=trace_id,
                name=trace_name,
                metadata={
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "service": "geotech_ai_service"
                }
            )
            logger.debug(f"Started LangFuse trace: {trace_id}")
            return trace_id
        except Exception as e:
            logger.error(f"Failed to start LangFuse trace: {e}")
            return trace_id
    
    def create_span(self, 
                   trace_id: str,
                   span_name: str,
                   span_type: str = "DEFAULT",
                   input_data: Optional[Dict[str, Any]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new span within a trace"""
        span_id = str(uuid.uuid4())
        
        if not self.enabled or not self.client:
            logger.debug(f"LangFuse disabled. Using mock span_id: {span_id}")
            return span_id
            
        try:
            span = self.client.span(
                id=span_id,
                trace_id=trace_id,
                name=span_name,
                metadata={
                    "span_type": span_type,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    **(metadata or {})
                },
                input=input_data
            )
            logger.debug(f"Created LangFuse span: {span_id} for trace: {trace_id}")
            return span_id
        except Exception as e:
            logger.error(f"Failed to create LangFuse span: {e}")
            return span_id
    
    def update_span(self,
                   span_id: str,
                   output_data: Optional[Dict[str, Any]] = None,
                   status: str = "SUCCESS",
                   end_time: Optional[datetime] = None) -> None:
        """Update span with results and end time"""
        if not self.enabled or not self.client:
            logger.debug(f"LangFuse disabled. Skipping span update: {span_id}")
            return
            
        try:
            # LangFuse API changed - skip span update for now
            if hasattr(self.client, 'get_span'):
                span = self.client.get_span(span_id)
            else:
                span = None
            if span:
                update_data = {
                    "status_message": status,
                    "end_time": end_time or datetime.now(timezone.utc)
                }
                if output_data:
                    update_data["output"] = output_data
                    
                span.update(**update_data)
                logger.debug(f"Updated LangFuse span: {span_id}")
        except Exception as e:
            logger.error(f"Failed to update LangFuse span {span_id}: {e}")
    
    def end_trace(self, trace_id: str, status: str = "SUCCESS") -> None:
        """End trace with final status"""
        if not self.enabled or not self.client:
            logger.debug(f"LangFuse disabled. Skipping trace end: {trace_id}")
            return
            
        try:
            # Skip trace operations if API is having issues
            if hasattr(self.client, 'get_trace'):
                trace = self.client.get_trace(trace_id)
                if trace:
                    trace.update(
                        output={"status": status},
                        end_time=datetime.now(timezone.utc)
                    )
                    logger.debug(f"Ended LangFuse trace: {trace_id}")
        except Exception as e:
            # Suppress LangFuse errors to avoid spam
            logger.debug(f"LangFuse trace end skipped {trace_id}: {e}")
    
    def flush(self) -> None:
        """Flush any pending traces"""
        if self.enabled and self.client:
            try:
                self.client.flush()
                logger.debug("Flushed LangFuse client")
            except Exception as e:
                logger.error(f"Failed to flush LangFuse client: {e}")

# Global client instance
_langfuse_client: Optional[LangFuseClient] = None

def get_langfuse_client() -> LangFuseClient:
    """Get global LangFuse client instance"""
    global _langfuse_client
    if _langfuse_client is None:
        _langfuse_client = LangFuseClient()
    return _langfuse_client

@contextmanager
def trace_agent_workflow(question: str):
    """Context manager for tracing complete agent workflow"""
    client = get_langfuse_client()
    trace_id = client.start_trace("agent_workflow")
    
    try:
        # Create initial span for the question
        span_id = client.create_span(
            trace_id=trace_id,
            span_name="agent_request",
            span_type="REQUEST",
            input_data={"question": question}
        )
        
        yield trace_id, client
        
        # Mark as successful
        client.update_span(span_id, status="SUCCESS")
        client.end_trace(trace_id, "SUCCESS")
        
    except Exception as e:
        # Mark as failed
        client.update_span(span_id, status="ERROR", output_data={"error": str(e)})
        client.end_trace(trace_id, "ERROR")
        raise
    finally:
        client.flush()