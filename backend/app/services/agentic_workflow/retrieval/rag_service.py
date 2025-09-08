# rag_service.py - Fixed version
import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Set
from fastapi import HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.embeddings.openai import OpenAIEmbedding
from app.core.storages.vectorstores.qdrant import QdrantVectorStore, QdrantConnectionError
from app.core.storages.docstores.mongodb import MongoDocumentStore, MongoConnectionError
from app.core.llms.gemini import GeminiService
from app.api.schema.response import Citation
from app.core.config.constants import RAGConstants

logger = logging.getLogger(__name__)

class RAGServiceError(Exception):
    """Custom exception for RAG Service errors"""
    pass

class RAGService:
    def __init__(self, openai_api_key: str, gemini_api_key: str, settings):
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

    async def search(self, query: str, k: int, score_threshold: float) -> List[Citation]:
        import time
        start_time = time.time()
        
        try:
            logger.info(f"--- RAGService.search ENTRY --- Query: '{query}', k={k}, threshold={score_threshold}")
            
            # Health check connections before search
            await self._health_check()
            
            hybrid_results = await self.hybrid_search(
                query=query, vector_k=k, keyword_k=k, score_threshold=score_threshold
            )
            
            logger.info(f"Hybrid search returned {len(hybrid_results)} final results.")
            
            # DETAILED DEBUG: Print each result to terminal
            print(f"\n=== RAG DEBUG: Processing {len(hybrid_results)} hybrid results ===", flush=True)
            for i, res in enumerate(hybrid_results):
                print(f"Result {i+1}:", flush=True)
                print(f"  - Text: {res.get('text', '')[:100]}...", flush=True)
                print(f"  - Score: {res.get('score', 0.0)}", flush=True)
                print(f"  - Metadata: {res.get('metadata', {})}", flush=True)
                print(f"  - Search Type: {res.get('search_type', 'unknown')}", flush=True)
            
            if not hybrid_results:
                logger.warning("No results found from hybrid search - check data availability and query relevance")
                print("=== RAG DEBUG: No hybrid_results found! ===", flush=True)
                return []
            
            citations = []
            for i, res in enumerate(hybrid_results):
                source_name = res.get("metadata", {}).get("source", "unknown")
                content = res.get("text", "")
                confidence_score = res.get("score", 0.0)
                page_index = res.get("metadata", {}).get("page_index")
                
                print(f"\n=== Citation {i+1} Debug ===")
                print(f"Source: {source_name}")
                print(f"Content length: {len(content)}")
                print(f"Score: {confidence_score}")
                print(f"Page index: {page_index}")
                
                citation = Citation(
                    source_name=source_name,
                    content=content,
                    confidence_score=confidence_score,
                    page_index=page_index,
                )
                citations.append(citation)
                print(f"Citation created successfully: {type(citation)}")
            
            print(f"=== RAG DEBUG: Created {len(citations)} Citation objects ===\n")
            
            duration = (time.time() - start_time) * 1000
            logger.info(f"RAG Search completed in {duration:.2f}ms. Converted to {len(citations)} Citation objects.")
            
            return citations
            
        except (QdrantConnectionError, MongoConnectionError) as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"RAG Service connection error after {duration:.2f}ms: {e}")
            
            # Try to reconnect once before failing
            try:
                logger.info("Attempting to reconnect RAG Service connections...")
                await self._reconnect()
                
                # Retry search once after reconnection
                logger.info("Retrying search after reconnection...")
                hybrid_results = await self.hybrid_search(
                    query=query, vector_k=k, keyword_k=k, score_threshold=score_threshold
                )
                
                citations = [
                    Citation(
                        source_name=res.get("metadata", {}).get("source", "unknown"),
                        content=res.get("text", ""),
                        confidence_score=res.get("score", 0.0),
                        page_index=res.get("metadata", {}).get("page_index"),
                    )
                    for res in hybrid_results
                ]
                
                duration = (time.time() - start_time) * 1000
                logger.info(f"RAG Search successful after reconnection in {duration:.2f}ms")
                return citations
                
            except Exception as retry_error:
                logger.error(f"Reconnection and retry failed: {retry_error}")
                raise HTTPException(
                    status_code=503,
                    detail=f"RAG Service unavailable after reconnection attempt: {str(e)}"
                )
                
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"RAG Service error after {duration:.2f}ms: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"RAG Service internal error: {str(e)}"
            )
    
    async def _reconnect(self):
        """Attempt to reconnect all RAG Service connections"""
        try:
            logger.info("Reconnecting Qdrant...")
            self.vector_store._reconnect()
            
            logger.info("Reconnecting MongoDB...")
            self.mongodb_store._reconnect()
            
            # Verify reconnection
            await self._health_check()
            logger.info("RAG Service reconnection successful")
            
        except Exception as e:
            logger.error(f"RAG Service reconnection failed: {e}")
            raise RAGServiceError(f"Failed to reconnect RAG Service: {e}")
    
    async def _health_check(self):
        """Comprehensive health check for RAG Service before operations"""
        try:
            # Check Qdrant health
            qdrant_health = self.vector_store._health_check()
            if qdrant_health["status"] != "healthy":
                raise QdrantConnectionError(f"Qdrant unhealthy: {qdrant_health.get('error', 'Unknown error')}")
            
            # Check MongoDB health
            mongodb_health = self.mongodb_store._health_check()
            if mongodb_health["status"] != "healthy":
                raise MongoConnectionError(f"MongoDB unhealthy: {mongodb_health.get('error', 'Unknown error')}")
            
            logger.debug("RAG Service health check passed")
            
        except (QdrantConnectionError, MongoConnectionError):
            raise  # Re-raise connection errors
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise RAGServiceError(f"RAG Service health check failed: {e}")

    async def hybrid_search(self, query: str, vector_k: int, keyword_k: int, score_threshold: float) -> List[Dict[str, Any]]:
        logger.info("--- RAGService.hybrid_search ENTRY ---")
        print(f"\n=== HYBRID SEARCH DEBUG ===")
        print(f"Query: '{query}'")
        print(f"Vector k: {vector_k}, Keyword k: {keyword_k}")
        print(f"Score threshold: {score_threshold}")
        
        try:
            logger.info("Step 1: Performing vector search...")
            print("Step 1: Performing vector search...")
            vector_results = await self.vector_search(query, vector_k, score_threshold)
            logger.info(f"Vector search found {len(vector_results)} results.")
            print(f"Vector search found {len(vector_results)} results.")

            logger.info("Step 2: Extracting keywords...")
            print("Step 2: Extracting keywords...")
            keywords = await self.gemini_service.extract_keywords(query)
            logger.info(f"Extracted keywords: {keywords} (Count: {len(keywords)})")
            print(f"Extracted keywords: {keywords} (Count: {len(keywords)})")
            
            min_keywords = RAGConstants.MIN_KEYWORDS_THRESHOLD
            if len(keywords) < min_keywords:
                logger.info(f"Keyword count < {min_keywords}. Using VECTOR-ONLY results.")
                print(f"Keyword count < {min_keywords}. Using VECTOR-ONLY results.")
                print(f"Returning {len(vector_results)} vector results")
                return vector_results
            
            logger.info("Proceeding with HYBRID search.")
            print("Proceeding with HYBRID search.")
            vector_results_trimmed = vector_results[:RAGConstants.HYBRID_VECTOR_CHUNKS]
            print(f"Trimmed vector results to {len(vector_results_trimmed)}")
            
            logger.info("Step 5: Performing keyword search...")
            print("Step 5: Performing keyword search...")
            keyword_results = await self._keyword_search_with_list(keywords, keyword_k)
            logger.info(f"Keyword search found {len(keyword_results)} results.")
            print(f"Keyword search found {len(keyword_results)} results.")
            
            combined_results = self._combine_and_deduplicate(vector_results_trimmed, keyword_results)
            logger.info(f"Final combined/deduplicated count: {len(combined_results)}.")
            print(f"Final combined/deduplicated count: {len(combined_results)}.")
            return combined_results
            
        except Exception as e:
            logger.error(f"Error in hybrid_search, falling back to vector-only. Error: {e}", exc_info=True)
            return await self.vector_search(query, vector_k, score_threshold)

    async def vector_search(self, query: str, k: int, score_threshold: float) -> List[Dict[str, Any]]:
        """Perform vector search with proper async handling."""
        import time
        start_time = time.time()
        
        logger.info(f"--- RAGService.vector_search ENTRY --- k={k}, threshold={score_threshold}")
        try:
            # Python 3.7+ compatible approach using run_in_executor
            loop = asyncio.get_event_loop()
            
            def sync_blocking_code():
                logger.info("Creating query embedding...")
                query_embedding = self.embedding_service.get_query_embedding(query)
                logger.info(f"Embedding created (dim: {len(query_embedding)}).")
                
                logger.info("Searching Qdrant...")
                results = self.vector_store.search(
                    query_vector=query_embedding, limit=k, score_threshold=score_threshold
                )
                logger.info(f"Qdrant returned {len(results)} raw results.")
                
                if not results:
                    logger.warning("No vector search results found - check Qdrant data availability")
                    print("=== VECTOR SEARCH DEBUG: No results from Qdrant! ===")
                    return []
                
                print(f"=== VECTOR SEARCH DEBUG: Raw Qdrant results ===")
                for i, r in enumerate(results):
                    print(f"Raw result {i+1}:")
                    print(f"  - Keys: {list(r.keys())}")
                    print(f"  - Text: {r.get('text', '')[:100]}...")
                    print(f"  - Score: {r.get('score', 0.0)}")
                    print(f"  - Metadata: {r.get('metadata', {})}")
                
                formatted = [
                    {"text": r["text"], "score": r["score"], "metadata": r["metadata"], "search_type": "vector"}
                    for r in results
                ]
                logger.info(f"Formatted {len(formatted)} vector results.")
                print(f"=== VECTOR SEARCH DEBUG: Formatted {len(formatted)} results ===")
                return formatted

            # Use run_in_executor for compatibility with Python 3.7+
            results = await loop.run_in_executor(None, sync_blocking_code)
            
            duration = (time.time() - start_time) * 1000
            logger.info(f"Vector search completed in {duration:.2f}ms with {len(results)} results")
            return results

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Error in vector_search after {duration:.2f}ms: {e}", exc_info=True)
            return []

    async def _keyword_search_with_list(self, keywords: List[str], k: int) -> List[Dict[str, Any]]:
        """Keyword search using pre-extracted keyword list with proper async handling."""
        import time
        start_time = time.time()
        
        logger.info(f"--- RAGService._keyword_search_with_list ENTRY --- k={k}, keywords={keywords}")
        try:
            if not keywords:
                logger.warning("No keywords provided for search")
                return []
            
            query_string = " ".join(keywords)
            logger.info(f"MongoDB query string: '{query_string}'")
            
            async def async_mongodb_query():
                logger.info(f"[MONGODB DEBUG] Executing async query with: '{query_string}'")
                # Use async MongoDB method with proper parameters
                documents, scores = await self.mongodb_store.query(
                    query=query_string,
                    top_k=k,
                    doc_ids=None,  # Search all documents for now
                    with_scores=True
                )
                logger.info(f"[MONGODB DEBUG] Found {len(documents)} documents with scores")
                
                if not documents:
                    logger.warning("MongoDB returned no results - check data availability and text indexes")
                
                return documents, scores
            
            # Execute async MongoDB query directly
            docs, scores = await async_mongodb_query()
            
            duration = (time.time() - start_time) * 1000
            logger.info(f"MongoDB keyword search completed in {duration:.2f}ms. Returned {len(docs)} documents.")
            
            return [
                {"text": doc["text"], "score": score, "metadata": doc["attributes"], "search_type": "keyword"}
                for doc, score in zip(docs, scores)
            ]
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"Error in _keyword_search_with_list after {duration:.2f}ms: {e}", exc_info=True)
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