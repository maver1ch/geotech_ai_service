"""
Gemini LLM Service for keyword extraction
"""

import json
import asyncio
from typing import List

import google.genai as genai

class GeminiService:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
    
    async def extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query for search optimization"""
        
        prompt = f"""
Extract the most important keywords from this query for document search. Focus on:
- Proper nouns (names, software, standards)
- Technical terms and jargon  
- Key concepts that define user intention
- Domain-specific terminology

Query: "{query}"

Return only a JSON list of keywords (truely important ones):
["keyword1", "keyword2", ...]

Keywords:"""

        try:
            # Use google.genai client API - simple format
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt
            )
            
            # Extract JSON from response
            content = response.text.strip()
            if content.startswith('```json'):
                content = content.replace('```json', '').replace('```', '').strip()
            
            keywords = json.loads(content)
            
            # Validate and filter keywords
            if isinstance(keywords, list):
                filtered_keywords = [kw.strip().lower() for kw in keywords if isinstance(kw, str) and len(kw.strip()) > 1]
                return filtered_keywords[:8]
            
            return []
            
        except Exception as e:
            print(f"Gemini keyword extraction error: {e}")
            return []