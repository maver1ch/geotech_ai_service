"""
Vector Database Setup with Contextualization
Script to process markdown files, contextualize chunks and index into Qdrant
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add project root to Python path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config.settings import get_settings, get_rag_config, get_mongodb_config
from app.core.config.constants import RAGConstants
from app.core.storages.vectorstores.qdrant import QdrantVectorStore
from app.core.storages.docstores.mongodb import MongoDocumentStore
from app.core.embeddings.openai import OpenAIEmbedding
from app.core.loaders.markdown_reader import MarkdownReader
from app.core.loaders.contextualization_service import ContextualizationService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to setup vector database with contextualization"""
    try:
        
        # Initialize settings
        settings = get_settings()
        
        # Initialize services
        logger.info("Initializing services...")
        
        vector_store = QdrantVectorStore(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            collection_name=settings.QDRANT_COLLECTION_NAME
        )
        embedding_service = OpenAIEmbedding(api_key=settings.OPENAI_API_KEY)
        
        # Initialize MongoDB document store
        mongodb_config = get_mongodb_config()
        document_store = MongoDocumentStore(
            host=mongodb_config['host'],
            port=mongodb_config['port'],
            database_name=mongodb_config['database'],
            collection_name=mongodb_config['collection']
        )
        # Get chunk settings from environment
        chunk_config = get_rag_config()
        logger.info(f"Chunk configuration: size={chunk_config['chunk_size']}, overlap={chunk_config['chunk_overlap']}")
        
        markdown_reader = MarkdownReader(
            min_chunk_size=RAGConstants.MIN_CHUNK_SIZE,
            max_chunk_size=RAGConstants.MAX_CHUNK_SIZE,
            header_merge_threshold=RAGConstants.HEADER_MERGE_THRESHOLD
        )
        contextualization_service = ContextualizationService(
            add_context_header=True
        )
        
        # Setup collection
        collection_name = settings.QDRANT_COLLECTION_NAME
        logger.info(f"Setting up Qdrant collection: {collection_name}")
        
        # OpenAI text-embedding-3-large has 3072 dimensions
        EMBEDDING_DIMENSION = 3072
        vector_store.create_collection(vector_size=EMBEDDING_DIMENSION)
        
        # Process markdown files 
        # Path relative to project root
        project_root = Path(__file__).parent.parent
        knowledge_base_path = project_root / "data" / "markdown"
        
        if not knowledge_base_path.exists():
            raise FileNotFoundError(f"Knowledge base directory not found: {knowledge_base_path}")
        
        markdown_files = list(knowledge_base_path.glob("*.md"))
        logger.info(f"Found {len(markdown_files)} markdown files to process")
        
        total_chunks_processed = 0
        total_contextualized = 0
        total_processing_time = 0
        
        for md_file in markdown_files:
            logger.info(f"\\n{'='*60}")
            logger.info(f"Processing file: {md_file.name}")
            logger.info(f"{'='*60}")
            
            file_start_time = time.time()
            
            # Step 1: Read and chunk markdown
            logger.info("Step 1: Reading and chunking markdown...")
            chunks = markdown_reader.read_markdown_file(str(md_file))
            logger.info(f"Created {len(chunks)} initial chunks")
            
            # Step 2: Contextualize chunks with simple header-based context
            logger.info("Step 2: Contextualizing chunks...")
            contextualized_chunks = await contextualization_service.contextualize_chunks(
                chunks=chunks,
                filename=md_file.name
            )
            
            # Count successful contextualizations
            successful_contextualizations = sum(1 for c in contextualized_chunks if c.context_added)
            logger.info(f"Added context headers to: {successful_contextualizations}/{len(contextualized_chunks)} chunks")
            
            # Step 3: Generate embeddings and store
            logger.info("Step 3: Generating embeddings and storing...")
            
            if not contextualized_chunks:
                logger.warning(f"No chunks created from {md_file.name}, skipping storage")
                continue
            
            documents_with_embeddings = []
            documents_for_mongodb = []
            
            for i, ctx_chunk in enumerate(contextualized_chunks):
                doc = ctx_chunk.to_document()
                
                # Generate unique doc_id
                import uuid
                doc_id = str(uuid.uuid4())
                
                # Generate embedding for the content (contextualized or original)
                embedding = embedding_service.get_query_embedding(doc['content'])
                
                # Prepare for Qdrant (vector storage)
                class DocumentForStorage:
                    def __init__(self, content, metadata, doc_id):
                        self.content = content
                        self.metadata = metadata
                        self.doc_id = doc_id
                    
                    def get_content(self):
                        return self.content
                
                doc_obj = DocumentForStorage(doc['content'], doc['metadata'], doc_id)
                documents_with_embeddings.append((doc_obj, embedding))
                
                # Prepare for MongoDB (document storage)
                documents_for_mongodb.append({
                    'doc_id': doc_id,
                    'content': doc['content'],
                    'metadata': doc['metadata']
                })
            
            # Store documents in both databases
            if documents_with_embeddings:
                # Store in Qdrant (vectors)
                vector_store.add_documents(documents_with_embeddings)
                
                # Store in MongoDB (documents for keyword search)
                document_store.add_documents(documents_for_mongodb)
                
                logger.info(f"Stored {len(documents_with_embeddings)} documents in vector database")
                logger.info(f"Stored {len(documents_for_mongodb)} documents in MongoDB")
            else:
                logger.warning(f"No documents to store for {md_file.name}")
            
            file_processing_time = time.time() - file_start_time
            
            # Update counters
            total_chunks_processed += len(contextualized_chunks)
            total_contextualized += successful_contextualizations
            total_processing_time += file_processing_time
            
            logger.info(f"File processing completed in {file_processing_time:.2f}s")
            
            # Short pause between files
            await asyncio.sleep(2)
        
        # Final summary
        logger.info(f"\\n{'='*60}")
        logger.info("PROCESSING SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Files processed: {len(markdown_files)}")
        logger.info(f"Total chunks: {total_chunks_processed}")
        if total_chunks_processed > 0:
            percentage = total_contextualized/total_chunks_processed*100
            logger.info(f"Context headers added: {total_contextualized} ({percentage:.1f}%)")
        else:
            logger.info(f"Context headers added: {total_contextualized} (N/A - no chunks processed)")
        logger.info(f"Total processing time: {total_processing_time:.2f}s")
        logger.info(f"Average time per file: {total_processing_time/len(markdown_files):.2f}s")
        
        # Collection info
        collection_info = vector_store.get_collection_info()
        if collection_info:
            logger.info(f"Vector database status: {collection_info['vectors_count']} vectors stored")
        else:
            logger.warning("Could not retrieve collection info")
        
        # MongoDB stats
        try:
            mongo_stats = document_store.get_collection_stats()
            logger.info(f"MongoDB status: {mongo_stats['total_documents']} documents stored")
        except Exception as e:
            logger.warning(f"Could not retrieve MongoDB stats: {e}")
        
        logger.info("Vector database setup with contextualization completed successfully! 🎉")
        
    except Exception as e:
        logger.error(f"Error during vector database setup: {e}")
        raise


if __name__ == "__main__":
    print("🚀 Starting Vector Database Setup with Simple Contextualization...")
    print("This process will:")
    print("1. Read markdown files from knowledge_base/")  
    print("2. Chunk them intelligently based on headers")
    print("3. Add simple context headers to chunks")
    print("4. Generate embeddings and store in Qdrant")
    print()
    
    # Run main setup
    asyncio.run(main())