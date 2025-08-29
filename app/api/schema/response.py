from typing import List, Optional
from pydantic import BaseModel, Field

class Citation(BaseModel):
    source_name: str = Field(description="Name of the source file")
    content: str = Field(description="The retrieved text content")
    confidence_score: float = Field(description="Similarity score from vector search")
    page_index: Optional[int] = Field(default=None, description="Page number in source document")
    thumbnail: Optional[str] = Field(default=None, description="Base64 encoded thumbnail of the page")
    embedded_images: Optional[List[str]] = Field(default=None, description="Base64 encoded embedded images")

class AskResponse(BaseModel):
    answer: str = Field(description="The final answer from the agent")
    citations: List[Citation] = Field(description="List of source citations")
    trace_id: str = Field(description="Unique identifier for tracing this request")

class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Service health status")

class MetricsResponse(BaseModel):
    total_requests: int = Field(description="Total number of requests processed")
    tool_calls: int = Field(description="Number of tool calls made")
    retrieval_calls: int = Field(description="Number of retrieval operations performed")
    successful_requests: int = Field(description="Number of successful requests")
    failed_requests: int = Field(description="Number of failed requests")
    average_response_time: float = Field(description="Average response time in milliseconds")
    uptime_seconds: float = Field(description="Service uptime in seconds")
    requests_per_minute: float = Field(description="Requests per minute rate")
    success_rate: float = Field(description="Success rate percentage")
    start_time: str = Field(description="Service start time in ISO format")
    last_request_time: Optional[str] = Field(default=None, description="Last request time in ISO format")