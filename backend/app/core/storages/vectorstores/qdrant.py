import uuid
import logging
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse

logger = logging.getLogger(__name__)

class QdrantConnectionError(Exception):
    """Custom exception for Qdrant connection issues"""
    pass

class QdrantVectorStore:
    def __init__(
        self,
        host: str,
        port: int,
        collection_name: str,
        validate_on_init: bool = True
    ):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.client = QdrantClient(host=host, port=port)
        
        # Validate connection if requested (skip for setup scenarios)
        if validate_on_init:
            self._validate_connection()
            logger.info(f"Qdrant VectorStore initialized successfully: {host}:{port}/{collection_name}")
        else:
            logger.info(f"Qdrant VectorStore initialized (validation skipped): {host}:{port}/{collection_name}")
    
    def _validate_connection(self):
        """Test connection and collection availability"""
        try:
            # Test basic connection to Qdrant server
            collections_response = self.client.get_collections()
            logger.debug(f"Qdrant connection test successful, found {len(collections_response.collections)} collections")
            
            # Check if our collection exists
            collection_names = [col.name for col in collections_response.collections]
            if self.collection_name not in collection_names:
                raise QdrantConnectionError(
                    f"Collection '{self.collection_name}' not found. Available collections: {collection_names}"
                )
            
            # Test collection access
            collection_info = self.client.get_collection(self.collection_name)
            logger.debug(f"Collection '{self.collection_name}' validated: {collection_info.points_count} points")
            
        except UnexpectedResponse as e:
            raise QdrantConnectionError(f"Qdrant server error: {e}")
        except Exception as e:
            raise QdrantConnectionError(f"Qdrant connection validation failed: {e}")
    
    def _health_check(self) -> Dict[str, Any]:
        """Quick health check for Qdrant connection"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "status": "healthy",
                "points_count": collection_info.points_count,
                "collection_name": self.collection_name
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "collection_name": self.collection_name
            }
    
    def _reconnect(self):
        """Attempt to reconnect to Qdrant"""
        try:
            logger.info("Attempting to reconnect to Qdrant...")
            self.client = QdrantClient(host=self.host, port=self.port)
            self._validate_connection()
            logger.info("Qdrant reconnection successful")
        except Exception as e:
            logger.error(f"Qdrant reconnection failed: {e}")
            raise QdrantConnectionError(f"Failed to reconnect to Qdrant: {e}")
    
    def create_collection(self, vector_size: int):
        """Create collection if not exists"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )
                print(f"Created collection: {self.collection_name}")
            else:
                print(f"Collection {self.collection_name} already exists")
        except Exception as e:
            print(f"Error creating collection: {e}")
            raise
    
    def delete_collection(self):
        """Delete collection if exists"""
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            print(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            print(f"Error deleting collection: {e}")
    
    def add_documents(self, documents_with_embeddings: List[tuple]):
        """Add documents with their embeddings to Qdrant"""
        points = []
        
        for doc, embedding in documents_with_embeddings:
            point_id = str(uuid.uuid4())
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": doc.get_content(),
                    "metadata": doc.metadata
                }
            )
            points.append(point)
        
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            print(f"Added {len(points)} documents to Qdrant")
        except Exception as e:
            print(f"Error adding documents: {e}")
            raise
    
    def search(
        self,
        query_vector: List[float],
        limit: int,
        score_threshold: float
    ) -> List[Dict[str, Any]]:
        """Search for similar documents with connection validation"""
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )
            
            results = []
            for scored_point in search_result:
                result = {
                    "id": scored_point.id,
                    "score": scored_point.score,
                    "text": scored_point.payload["text"],
                    "metadata": scored_point.payload["metadata"]
                }
                results.append(result)
            
            logger.debug(f"Qdrant search completed: {len(results)} results found")
            return results
            
        except UnexpectedResponse as e:
            logger.error(f"Qdrant server error during search: {e}")
            raise QdrantConnectionError(f"Qdrant server error: {e}")
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise QdrantConnectionError(f"Qdrant search failed: {e}")
    
    def get_collection_info(self):
        """Get collection information"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
                "status": info.status
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return None