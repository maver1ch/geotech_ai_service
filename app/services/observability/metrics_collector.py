"""
Metrics Collection Service
Simple in-memory metrics tracking for GeotechAgent operations
"""

import logging
import time
from typing import Dict, Any
from datetime import datetime, timezone
from threading import Lock

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Simple metrics collector for tracking agent operations"""
    
    def __init__(self):
        self._lock = Lock()
        self._metrics = {
            "total_requests": 0,
            "tool_calls": 0,
            "retrieval_calls": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0
        }
        self._start_time = datetime.now(timezone.utc)
        self._response_times = []
        logger.info("Metrics collector initialized")
    
    def increment_requests(self) -> None:
        """Increment total request counter"""
        with self._lock:
            self._metrics["total_requests"] += 1
            logger.debug("Incremented total_requests")
    
    def increment_tool_calls(self) -> None:
        """Increment tool call counter"""
        with self._lock:
            self._metrics["tool_calls"] += 1
            logger.debug("Incremented tool_calls")
    
    def increment_retrieval_calls(self) -> None:
        """Increment retrieval call counter"""
        with self._lock:
            self._metrics["retrieval_calls"] += 1
            logger.debug("Incremented retrieval_calls")
    
    def increment_successful_requests(self) -> None:
        """Increment successful request counter"""
        with self._lock:
            self._metrics["successful_requests"] += 1
            logger.debug("Incremented successful_requests")
    
    def increment_failed_requests(self) -> None:
        """Increment failed request counter"""
        with self._lock:
            self._metrics["failed_requests"] += 1
            logger.debug("Incremented failed_requests")
    
    def record_response_time(self, response_time_ms: float) -> None:
        """Record response time and update average"""
        with self._lock:
            self._response_times.append(response_time_ms)
            # Keep only last 100 response times for moving average
            if len(self._response_times) > 100:
                self._response_times = self._response_times[-100:]
            
            # Calculate average
            if self._response_times:
                self._metrics["average_response_time"] = sum(self._response_times) / len(self._response_times)
            
            logger.debug(f"Recorded response time: {response_time_ms}ms")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        with self._lock:
            uptime_seconds = (datetime.now(timezone.utc) - self._start_time).total_seconds()
            
            metrics_snapshot = {
                **self._metrics,
                "uptime_seconds": round(uptime_seconds, 2),
                "requests_per_minute": self._calculate_rpm()
            }
            
            logger.debug("Generated metrics snapshot")
            return metrics_snapshot
    
    def _calculate_rpm(self) -> float:
        """Calculate requests per minute"""
        uptime_minutes = (datetime.now(timezone.utc) - self._start_time).total_seconds() / 60
        
        if uptime_minutes == 0:
            return 0.0
            
        return round(self._metrics["total_requests"] / uptime_minutes, 2)
    
    
    def reset_metrics(self) -> None:
        """Reset all metrics (useful for testing)"""
        with self._lock:
            self._metrics = {
                "total_requests": 0,
                "tool_calls": 0,
                "retrieval_calls": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0.0
            }
            self._start_time = datetime.now(timezone.utc)
            self._response_times = []
            logger.info("Metrics reset")

class RequestTimer:
    """Context manager for timing requests"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.metrics_collector.increment_requests()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            response_time_ms = (time.time() - self.start_time) * 1000
            self.metrics_collector.record_response_time(response_time_ms)
            
            # Record success or failure
            if exc_type is None:
                self.metrics_collector.increment_successful_requests()
            else:
                self.metrics_collector.increment_failed_requests()

# Global metrics collector instance
_metrics_collector: MetricsCollector = None

def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector

def time_request():
    """Get request timer context manager"""
    return RequestTimer(get_metrics_collector())