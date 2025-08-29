"""
OpenAI LLM Service
Wrapper for OpenAI API with retry logic and error handling
Pattern adapted from HG ChatBot
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Union
from openai import OpenAI
from openai.types.chat import ChatCompletion
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

logger = logging.getLogger(__name__)

class OpenAIServiceError(Exception):
    """Custom exception for OpenAI service errors"""
    pass

class OpenAIService:
    """
    OpenAI LLM Service with retry logic and configuration management
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        timeout: int = 30,
        max_retries: int = 3,
        max_completion_tokens: int = 2000,
        temperature: float = 0.1
    ):
        self.client = OpenAI(api_key=api_key, timeout=timeout)
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_completion_tokens = max_completion_tokens
        self.temperature = temperature
        
        # Track usage statistics
        self.request_count = 0
        self.error_count = 0
        self.total_tokens_used = 0
    
    def _prepare_messages(self, messages: Union[str, List[Dict[str, str]]]) -> List[Dict[str, str]]:
        """Prepare messages for OpenAI API call"""
        if isinstance(messages, str):
            return [{"role": "user", "content": messages}]
        elif isinstance(messages, list):
            # Validate message format
            for msg in messages:
                if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                    raise OpenAIServiceError("Invalid message format. Each message must have 'role' and 'content'")
            return messages
        else:
            raise OpenAIServiceError("Messages must be a string or list of message dictionaries")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((
            Exception,  # Retry on most exceptions  
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _call_openai_with_retry(self, messages: List[Dict[str, str]], **kwargs) -> ChatCompletion:
        """Make OpenAI API call with retry logic"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_completion_tokens=self.max_completion_tokens,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise
    
    def call_llm(
        self, 
        messages: Union[str, List[Dict[str, str]]], 
        timeout: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call OpenAI LLM with retry logic and error handling
        
        Args:
            messages: Either a string or list of message dictionaries
            timeout: Override default timeout
            **kwargs: Additional OpenAI API parameters
            
        Returns:
            Dict containing response and metadata
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Prepare messages
            formatted_messages = self._prepare_messages(messages)
            
            # Override timeout if specified
            if timeout:
                original_timeout = self.client.timeout
                self.client.timeout = timeout
            
            # Make API call with retry
            response = self._call_openai_with_retry(formatted_messages, **kwargs)
            
            # Restore original timeout
            if timeout:
                self.client.timeout = original_timeout
            
            # Track token usage
            if response.usage:
                self.total_tokens_used += response.usage.total_tokens
            
            # Calculate response time
            response_time = time.time() - start_time
            
            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                "response_time": round(response_time, 2),
                "status": "success"
            }
            
        except Exception as e:
            self.error_count += 1
            error_time = time.time() - start_time
            
            logger.error(f"LLM call failed after {error_time:.2f}s: {str(e)}")
            
            return {
                "content": None,
                "error": str(e),
                "error_type": type(e).__name__,
                "response_time": round(error_time, 2),
                "status": "error"
            }
    
    async def call_llm_async(
        self, 
        messages: Union[str, List[Dict[str, str]]], 
        timeout: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Async version of call_llm"""
        return await asyncio.to_thread(self.call_llm, messages, timeout, **kwargs)
    
    def create_system_message(self, content: str) -> Dict[str, str]:
        """Create a system message dictionary"""
        return {"role": "system", "content": content}
    
    def create_user_message(self, content: str) -> Dict[str, str]:
        """Create a user message dictionary"""
        return {"role": "user", "content": content}
    
    def create_assistant_message(self, content: str) -> Dict[str, str]:
        """Create an assistant message dictionary"""
        return {"role": "assistant", "content": content}
    
    def create_conversation(
        self, 
        system_prompt: str, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """Create a conversation with system prompt and history"""
        messages = [self.create_system_message(system_prompt)]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append(self.create_user_message(user_message))
        return messages
    
    def get_statistics(self) -> Dict[str, Union[int, float]]:
        """Get service usage statistics"""
        return {
            "total_requests": self.request_count,
            "successful_requests": self.request_count - self.error_count,
            "failed_requests": self.error_count,
            "success_rate": round((self.request_count - self.error_count) / max(self.request_count, 1) * 100, 2),
            "total_tokens_used": self.total_tokens_used,
            "average_tokens_per_request": round(self.total_tokens_used / max(self.request_count, 1), 2)
        }
    
    def reset_statistics(self):
        """Reset usage statistics"""
        self.request_count = 0
        self.error_count = 0
        self.total_tokens_used = 0