# --- MODIFIED FILE: app/core/llms/openai.py ---

import logging
from typing import List, Dict, Any
from openai import AsyncOpenAI, RateLimitError, APIError, APITimeoutError

logger = logging.getLogger(__name__)

class OpenAIService:
    """
    Async-first wrapper for OpenAI API calls.
    """
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout: int,
        max_retries: int,
        max_completion_tokens: int
    ):
        # CHANGED: Use the async client
        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries
        )
        self.model = model
        self.max_completion_tokens = max_completion_tokens
        self.request_count = 0
        self.error_count = 0

    def create_conversation(
        self,
        system_prompt: str,
        user_message: str
    ) -> List[Dict[str, str]]:
        """Creates a standard conversation structure."""
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

    # CHANGED: Converted to async def
    async def call_llm(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Asynchronously calls the OpenAI Chat Completions API.
        """
        self.request_count += 1
        try:
            # CHANGED: Added await for the async client call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_completion_tokens=self.max_completion_tokens
            )
            
            content = response.choices[0].message.content
            if not content or content.strip() == "":
                # Handle empty content gracefully with retry mechanism
                logger.warning("LLM returned empty content, treating as error for retry")
                raise ValueError("LLM returned empty content.")
                
            return {"status": "success", "content": content}

        except (RateLimitError, APITimeoutError, APIError) as e:
            self.error_count += 1
            logger.error(f"OpenAI API error: {type(e).__name__} - {e}")
            return {"status": "error", "error": f"API Error: {str(e)}"}
        except Exception as e:
            self.error_count += 1
            logger.error(f"An unexpected error occurred in call_llm: {e}", exc_info=True)
            return {"status": "error", "error": f"Unexpected Error: {str(e)}"}

    def reset_statistics(self):
        """Resets request and error counters."""
        self.request_count = 0
        self.error_count = 0