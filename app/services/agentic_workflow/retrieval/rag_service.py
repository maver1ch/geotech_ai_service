import os
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Set

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.embeddings.openai import OpenAIEmbedding
from app.core.storages.vectorstores.qdrant import QdrantVectorStore
from app.core.storages.docstores.mongodb import MongoDocumentStore
from app.core.llms.gemini import GeminiService
from app.api.schema.response import Citation
from app.core.config.constants import RAGConstants

class RAGService:
    def __init__(
        self,
        openai_api_key: str,
        gemini_api_key: str,
        settings
    ):
        self.settings = settings
        self.embedding_service = OpenAIEmbedding(api_key=openai_api_key)
        self.gemini_service = GeminiService(api_key=gemini_api_key)
        
        self.vector_store = QdrantVectorStore(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            collection_name=settings.QDRANT_COLLECTION_NAME
        )
        
        self.mongodb_store = MongoDocumentStore(
            host=settings.MONGODB_HOST,
            port=settings.MONGODB_PORT,
            database_name=settings.MONGODB_DATABASE,
            collection_name=settings.MONGODB_COLLECTION
        )
    
    def search(self, query: str, k: int, score_threshold: float) -> List[Citation]:
        """Smart hybrid search"""
        try:
            # Run smart hybrid search with new logic
            hybrid_results = asyncio.run(self.hybrid_search(
                query=query, 
                score_threshold=score_threshold
            ))
            
            # Convert to Citation objects
            citations = []
            for result in hybrid_results:
                metadata = result.get("metadata", {})
                
                citation = Citation(
                    source_name=metadata.get("source", "unknown"),
                    content=result.get("text", ""),
                    confidence_score=result.get("score", 0.0),
                    page_index=metadata.get("page_index")
                )
                citations.append(citation)
            
            return citations
            
        except Exception as e:
            print(f"Error in hybrid RAG search: {e}")
            return []
    
    async def hybrid_search(
        self, 
        query: str, 
        vector_k: int, 
        keyword_k: int, 
        score_threshold: float
    ) -> List[Dict[str, Any]]:
        """Smart hybrid search with keyword threshold logic"""
        try:
            # Always get top vector results first
            vector_results = await self._vector_search_async(query, vector_k, score_threshold)
            
            # Extract keywords with Gemini
            keywords = await self.gemini_service.extract_keywords(query)
            
            # Logic: if < threshold keywords, use only vector search
            if len(keywords) < RAGConstants.MIN_KEYWORDS_THRESHOLD:
                return vector_results
            
            # Hybrid mode: trim vector + add keyword results
            vector_results_trimmed = vector_results[:RAGConstants.HYBRID_VECTOR_CHUNKS]
            keyword_results = await self._keyword_search_with_list(keywords, keyword_k)
            
            combined_results = self._combine_and_deduplicate(
                vector_results_trimmed, keyword_results
            )
            
            return combined_results
            
        except Exception as e:
            print(f"Error in hybrid search: {e}")
            # Fallback to vector only
            return await self._vector_search_async(query, vector_k, score_threshold)
    
    async def _vector_search_async(self, query: str, k: int, score_threshold: float) -> List[Dict[str, Any]]:
        """Async wrapper for vector search"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._vector_search_sync, query, k, score_threshold)
    
    def _vector_search_sync(self, query: str, k: int, score_threshold: float) -> List[Dict[str, Any]]:
        """Synchronous vector search"""
        try:
            query_embedding = self.embedding_service.get_query_embedding(query)
            results = self.vector_store.search(
                query_vector=query_embedding,
                limit=k,
                score_threshold=score_threshold
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "text": result["text"],
                    "score": result["score"],
                    "metadata": result["metadata"],
                    "search_type": "vector"
                })
            
            return formatted_results
        except Exception as e:
            print(f"Vector search error: {e}")
            return []
    
    async def _keyword_search_with_list(self, keywords: List[str], k: int) -> List[Dict[str, Any]]:
        """Keyword search using pre-extracted keyword list"""
        try:
            if not keywords:
                return []
            
            query_string = " ".join(keywords)
            
            docs, scores = await self.mongodb_store.query(
                query=query_string,
                top_k=k,
                with_scores=True
            )
            
            formatted_results = []
            for doc, score in zip(docs, scores):
                formatted_results.append({
                    "text": doc["text"],
                    "score": score,
                    "metadata": doc["attributes"],
                    "search_type": "keyword"
                })
            
            return formatted_results
        except Exception as e:
            print(f"Keyword search error: {e}")
            return []
    
    
    def _combine_and_deduplicate(
        self, 
        vector_results: List[Dict[str, Any]], 
        keyword_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combine results from both searches and remove duplicates"""
        combined = []
        seen_texts: Set[str] = set()
        
        # Add vector results first (prioritize semantic similarity)
        for result in vector_results:
            text_key = result.get("text", "")[:100]  # Use first 100 chars as key
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                combined.append(result)
        
        # Add keyword results that weren't already found
        for result in keyword_results:
            text_key = result.get("text", "")[:100]
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                combined.append(result)
        
        # Sort by score (descending)
        combined.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return combined
    
    def get_collection_stats(self):
        """Get statistics about the knowledge base"""
        vector_stats = self.vector_store.get_collection_info()
        
        try:
            mongodb_count = asyncio.run(self.mongodb_store.count())
            vector_stats["mongodb_documents"] = mongodb_count
        except Exception as e:
            print(f"Error getting MongoDB stats: {e}")
            vector_stats["mongodb_documents"] = "unknown"
        
        return vector_stats