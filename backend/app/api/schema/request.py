from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.core.config.constants import APIConstants

class AskRequest(BaseModel):
    question: str = Field(description="The user's query", max_length=APIConstants.DEFAULT_QUESTION_MAX_LENGTH)
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional additional context")