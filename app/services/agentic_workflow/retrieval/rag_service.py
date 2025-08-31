# rag_service.py - Fixed version
import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Set

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.embeddings.openai import OpenAIEmbedding
from app.core.storages.vectorstores.qdrant import QdrantVectorStore
from app.core.storages.docstores.mongodb import MongoDocumentStore
from app.core.llms.gemini import GeminiService
from app.api.schema.response import Citation
from app.core.config.constants import RAGConstants

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, openai_api_key: str, gemini_api_key: str, settings):
        self.settings = settings
        self.embedding_service = OpenAIEmbedding(api_key=openai_api_key)
        self.gemini_service = GeminiService(api_key=gemini_api_key, model_name=settings.GOOGLE_GENAI_MODEL)
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

    async def search(self, query: str, k: int, score_threshold: float) -> List[Citation]:
        try:
            logger.info("--- RAGService.search ENTRY ---")
            hybrid_results = await self.hybrid_search(
                query=query, vector_k=k, keyword_k=k, score_threshold=score_threshold
            )
            logger.info(f"Hybrid search returned {len(hybrid_results)} final results.")
            citations = [
                Citation(
                    source_name=res.get("metadata", {}).get("source", "unknown"),
                    content=res.get("text", ""),
                    confidence_score=res.get("score", 0.0),
                    page_index=res.get("metadata", {}).get("page_index"),
                )
                for res in hybrid_results
            ]
            logger.info(f"Converted to {len(citations)} Citation objects. --- RAGService.search EXIT ---")
            return citations
        except Exception as e:
            logger.error(f"FATAL ERROR in RAGService.search: {e}", exc_info=True)
            return []

    async def hybrid_search(self, query: str, vector_k: int, keyword_k: int, score_threshold: float) -> List[Dict[str, Any]]:
        logger.info("--- RAGService.hybrid_search ENTRY ---")
        try:
            logger.info("Step 1: Performing vector search...")
            vector_results = await self.vector_search(query, vector_k, score_threshold)
            logger.info(f"Vector search found {len(vector_results)} results.")

            logger.info("Step 2: Extracting keywords...")
            keywords = await self.gemini_service.extract_keywords(query)
            logger.info(f"Extracted keywords: {keywords} (Count: {len(keywords)})")
            
            min_keywords = RAGConstants.MIN_KEYWORDS_THRESHOLD
            if len(keywords) < min_keywords:
                logger.info(f"Keyword count < {min_keywords}. Using VECTOR-ONLY results.")
                return vector_results
            
            logger.info("Proceeding with HYBRID search.")
            vector_results_trimmed = vector_results[:RAGConstants.HYBRID_VECTOR_CHUNKS]
            
            logger.info("Step 3: Performing keyword search...")
            keyword_results = await self._keyword_search_with_list(keywords, keyword_k)
            logger.info(f"Keyword search found {len(keyword_results)} results.")
            
            combined_results = self._combine_and_deduplicate(vector_results_trimmed, keyword_results)
            logger.info(f"Final combined/deduplicated count: {len(combined_results)}.")
            return combined_results
            
        except Exception as e:
            logger.error(f"Error in hybrid_search, falling back to vector-only. Error: {e}", exc_info=True)
            return await self.vector_search(query, vector_k, score_threshold)

    async def vector_search(self, query: str, k: int, score_threshold: float) -> List[Dict[str, Any]]:
        """Perform vector search with proper async handling."""
        logger.info(f"--- RAGService.vector_search (async) ENTRY ---")
        try:
            # Python 3.7+ compatible approach using run_in_executor
            loop = asyncio.get_event_loop()
            
            def sync_blocking_code():
                logger.info("Executing sync_blocking_code...")
                query_embedding = self.embedding_service.get_query_embedding(query)
                logger.info(f"Embedding created for query (dim: {len(query_embedding)}).")
                results = self.vector_store.search(
                    query_vector=query_embedding, limit=k, score_threshold=score_threshold
                )
                logger.info(f"Qdrant client returned {len(results)} raw results.")
                formatted = [
                    {"text": r["text"], "score": r["score"], "metadata": r["metadata"], "search_type": "vector"}
                    for r in results
                ]
                logger.info(f"Formatted {len(formatted)} vector results.")
                return formatted

            # Use run_in_executor for compatibility with Python 3.7+
            results = await loop.run_in_executor(None, sync_blocking_code)
            return results

        except Exception as e:
            logger.error(f"Error in vector_search: {e}", exc_info=True)
            return []

    async def _keyword_search_with_list(self, keywords: List[str], k: int) -> List[Dict[str, Any]]:
        """Keyword search using pre-extracted keyword list with proper async handling."""
        logger.info(f"--- RAGService._keyword_search_with_list ENTRY ---")
        try:
            if not keywords:
                return []
            
            query_string = " ".join(keywords)
            
            # Run MongoDB sync operation in executor to avoid blocking
            loop = asyncio.get_event_loop()
            
            def sync_mongodb_query():
                logger.info(f"[MONGODB DEBUG] Executing sync query with: '{query_string}'")
                # Use sync MongoDB methods directly
                search_filter = {"$text": {"$search": query_string}}
                cursor = self.mongodb_store.collection.find(
                    search_filter,
                    {"score": {"$meta": "textScore"}}
                ).sort([("score", {"$meta": "textScore"})]).limit(k)
                
                docs_list = list(cursor)
                logger.info(f"[MONGODB DEBUG] Found {len(docs_list)} documents")
                
                documents = []
                scores = []
                
                for doc in docs_list:
                    documents.append({
                        "id": doc.get("doc_id", "unknown"),
                        "text": doc.get("content", ""),
                        "attributes": doc.get("metadata", {})
                    })
                    scores.append(doc.get("score", 0.0))
                
                return documents, scores
            
            # Execute in thread pool to avoid blocking
            docs, scores = await loop.run_in_executor(None, sync_mongodb_query)
            
            logger.info(f"MongoDB returned {len(docs)} documents.")
            return [
                {"text": doc["text"], "score": score, "metadata": doc["attributes"], "search_type": "keyword"}
                for doc, score in zip(docs, scores)
            ]
        except Exception as e:
            logger.error(f"Error in _keyword_search_with_list: {e}", exc_info=True)
            return []

    def _combine_and_deduplicate(self, vector_results: List[Dict[str, Any]], keyword_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info(f"--- Combining {len(vector_results)} vector and {len(keyword_results)} keyword results ---")
        combined = []
        seen_texts: Set[str] = set()
        for result in vector_results:
            text_key = result.get("text", "")[:100]
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                combined.append(result)
        for result in keyword_results:
            text_key = result.get("text", "")[:100]
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                combined.append(result)
        combined.sort(key=lambda x: x.get("score", 0), reverse=True)
        return combined
    
    def get_collection_stats(self):
        """Get statistics about the knowledge base"""
        vector_stats = self.vector_store.get_collection_info()
        
        try:
            # Use sync version since this is not async
            search_filter = {}
            mongodb_count = self.mongodb_store.collection.count_documents(search_filter)
            vector_stats["mongodb_documents"] = mongodb_count
        except Exception as e:
            logger.error(f"Error getting MongoDB stats: {e}")
            vector_stats["mongodb_documents"] = "unknown"
        
        return vector_stats