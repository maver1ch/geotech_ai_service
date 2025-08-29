"""
Simple MongoDB Document Store for Keyword Search
Simplified version based on HG ChatBot pattern
"""

import logging
from typing import List, Dict, Any, Optional, Union
from pymongo import MongoClient, TEXT, ASCENDING
from pymongo.collection import Collection
from pymongo.database import Database

logger = logging.getLogger(__name__)

class MongoDocumentStore:
    """Simple MongoDB document store for keyword search"""
    
    def __init__(
        self,
        host: str,
        port: int,
        database_name: str,
        collection_name: str
    ):
        try:
            import pymongo
        except ImportError:
            raise ImportError(
                "Please install pymongo: 'pip install pymongo'"
            )
        
        self.connection_string = f"mongodb://{host}:{port}/"
        self.database_name = database_name
        self.collection_name = collection_name
        
        # Initialize MongoDB client
        self.client = MongoClient(self.connection_string)
        self.db: Database = self.client[database_name]
        self.collection: Collection = self.db[collection_name]
        
        # Initialize indexes
        self._init_indexes()
        
        logger.info(f"MongoDB DocumentStore initialized: {database_name}.{collection_name}")
    
    def _init_indexes(self):
        """Initialize MongoDB indexes for text search"""
        existing_indexes = list(self.collection.list_indexes())
        index_names = [idx["name"] for idx in existing_indexes]
        
        # Text search index for content
        if "text_search_idx" not in index_names:
            self.collection.create_index(
                [("content", TEXT)],
                name="text_search_idx"
            )
            logger.info("Created text search index")
        
        # Document ID index
        if "doc_id_idx" not in index_names:
            self.collection.create_index(
                [("doc_id", ASCENDING)],
                name="doc_id_idx",
                unique=True
            )
            logger.info("Created document ID index")
        
        # Source file index
        if "source_idx" not in index_names:
            self.collection.create_index(
                [("metadata.source", ASCENDING)],
                name="source_idx"
            )
            logger.info("Created source file index")
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to MongoDB with upsert
        
        Args:
            documents: List of document dicts with structure:
                {
                    'doc_id': str,
                    'content': str, 
                    'metadata': dict
                }
        """
        if not documents:
            return
        
        operations = []
        for doc in documents:
            doc_id = doc.get('doc_id')
            if not doc_id:
                # Generate doc_id if not provided
                import uuid
                doc_id = str(uuid.uuid4())
                doc['doc_id'] = doc_id
            
            # Prepare document for MongoDB
            mongo_doc = {
                "doc_id": doc_id,
                "content": doc['content'],
                "metadata": doc.get('metadata', {})
            }
            
            operations.append({
                "filter": {"doc_id": doc_id},
                "update": {"$set": mongo_doc},
                "upsert": True
            })
        
        # Use bulk write for efficiency
        from pymongo import UpdateOne
        bulk_ops = [
            UpdateOne(op["filter"], op["update"], upsert=op["upsert"])
            for op in operations
        ]
        
        result = self.collection.bulk_write(bulk_ops, ordered=False)
        logger.info(f"MongoDB: Upserted {result.upserted_count + result.modified_count} documents")
    
    def search_documents(
        self,
        query: str,
        top_k: int,
        source_filter: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Search documents using MongoDB text search
        
        Args:
            query: Search query string
            top_k: Maximum number of results
            source_filter: Optional source file filter
            
        Returns:
            List of documents with scores
        """
        try:
            # Build search filter
            search_filter = {"$text": {"$search": query}}
            
            # Add source filter if provided
            if source_filter:
                search_filter = {
                    "$and": [
                        search_filter,
                        {"metadata.source": {"$regex": source_filter, "$options": "i"}}
                    ]
                }
            
            # Execute search with text score
            cursor = self.collection.find(
                search_filter,
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(top_k)
        
            results = []
            for doc in cursor:
                results.append({
                    "doc_id": doc["doc_id"],
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "score": doc.get("score", 0.0)
                })
            
            logger.info(f"MongoDB search: '{query}' returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error in MongoDB search: {e}")
            return []
    
    async def query(
        self,
        query: str,
        top_k: int,
        with_scores: bool = True
    ) -> tuple:
        """
        Async query method compatible with RAGService
        
        Args:
            query: Search query string
            top_k: Maximum number of results
            with_scores: Return scores along with documents
            
        Returns:
            Tuple of (documents, scores) if with_scores=True, else just documents
        """
        try:
            # Build search filter
            search_filter = {"$text": {"$search": query}}
            
            # Execute search with text score
            cursor = self.collection.find(
                search_filter,
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(top_k)
            
            docs = list(cursor)
            
            if with_scores:
                documents = []
                scores = []
                
                for doc in docs:
                    documents.append({
                        "id": doc["doc_id"],
                        "text": doc["content"], 
                        "attributes": doc["metadata"]
                    })
                    scores.append(doc.get("score", 0.0))
                
                logger.info(f"MongoDB async query: '{query}' returned {len(documents)} results")
                return documents, scores
            else:
                documents = []
                for doc in docs:
                    documents.append({
                        "id": doc["doc_id"],
                        "text": doc["content"],
                        "attributes": doc["metadata"]
                    })
                    
                logger.info(f"MongoDB async query: '{query}' returned {len(documents)} results")  
                return documents
                
        except Exception as e:
            logger.error(f"Error in MongoDB query: {e}")
            if with_scores:
                return [], []
            else:
                return []
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        doc = self.collection.find_one({"doc_id": doc_id})
        if doc:
            return {
                "doc_id": doc["doc_id"],
                "content": doc["content"], 
                "metadata": doc["metadata"]
            }
        return None
    
    def get_documents_by_source(self, source: str) -> List[Dict[str, Any]]:
        """Get all documents from a specific source file"""
        cursor = self.collection.find({"metadata.source": source})
        return [
            {
                "doc_id": doc["doc_id"],
                "content": doc["content"],
                "metadata": doc["metadata"]
            }
            for doc in cursor
        ]
    
    def delete_documents_by_source(self, source: str) -> int:
        """Delete all documents from a specific source file"""
        result = self.collection.delete_many({"metadata.source": source})
        logger.info(f"Deleted {result.deleted_count} documents from source: {source}")
        return result.deleted_count
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        stats = self.db.command("collStats", self.collection_name)
        return {
            "total_documents": stats.get("count", 0),
            "storage_size": stats.get("storageSize", 0),
            "index_count": stats.get("nindexes", 0)
        }
    
    def close(self):
        """Close MongoDB connection"""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("MongoDB connection closed")