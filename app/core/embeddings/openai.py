import asyncio
from typing import List
from openai import OpenAI

class OpenAIEmbedding:
    def __init__(self, api_key: str, model: str = "text-embedding-3-large"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def get_embeddings(self, documents) -> List[tuple]:
        """Get embeddings for documents"""
        texts = [doc.get_content() for doc in documents]
        
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            
            embeddings = [embedding.embedding for embedding in response.data]
            return list(zip(documents, embeddings))
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            raise
    
    async def get_embeddings_async(self, documents) -> List[tuple]:
        """Async version of get_embeddings"""
        return await asyncio.to_thread(self.get_embeddings, documents)
    
    def get_query_embedding(self, query: str) -> List[float]:
        """Get embedding for a single query"""
        try:
            response = self.client.embeddings.create(
                input=[query],
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting query embedding: {e}")
            raise