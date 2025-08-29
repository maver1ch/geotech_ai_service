import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class QdrantVectorStore:
    def __init__(
        self,
        host: str,
        port: int,
        collection_name: str
    ):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
    
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
        """Search for similar documents"""
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
            
            return results
        except Exception as e:
            print(f"Error searching documents: {e}")
            raise
    
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