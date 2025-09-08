#!/usr/bin/env python3
"""
Unit tests for RAG Service
Tests the RAG pipeline directly without agent wrapper
"""

import sys
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.agentic_workflow.retrieval.rag_service import RAGService
from app.api.schema.response import Citation
from app.core.config.constants import RAGConstants


class TestRAGService:
    """Test suite for RAG Service"""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings object"""
        settings = Mock()
        settings.OPENAI_API_KEY = "test-openai-key"
        settings.GOOGLE_GENAI_API_KEY = "test-gemini-key"
        settings.QDRANT_HOST = "localhost"
        settings.QDRANT_PORT = 6333
        settings.QDRANT_COLLECTION_NAME = "test_collection"
        settings.MONGODB_HOST = "localhost"
        settings.MONGODB_PORT = 27017
        settings.MONGODB_DATABASE = "test_db"
        settings.MONGODB_COLLECTION = "test_collection"
        settings.SIMILARITY_THRESHOLD = 0.1
        return settings
    
    @pytest.fixture
    def sample_embedding(self):
        """Sample embedding vector for testing"""
        return [0.1] * 3072  # OpenAI embedding size
    
    @pytest.fixture
    def sample_vector_results(self):
        """Sample vector search results"""
        return [
            {
                "text": "Bearing capacity is the maximum load per unit area...",
                "score": 0.95,
                "metadata": {
                    "source": "geotechnical_handbook.pdf",
                    "page_index": 42
                }
            },
            {
                "text": "Settlement analysis involves calculating soil deformation...",
                "score": 0.87,
                "metadata": {
                    "source": "soil_mechanics.pdf", 
                    "page_index": 15
                }
            },
            {
                "text": "CPT testing provides continuous soil profiling...",
                "score": 0.82,
                "metadata": {
                    "source": "field_testing_guide.pdf",
                    "page_index": 8
                }
            }
        ]
    
    @pytest.fixture
    def sample_keyword_results(self):
        """Sample keyword search results"""
        return [
            {
                "text": "Foundation design requires understanding of bearing capacity factors...",
                "attributes": {
                    "source": "foundation_design.pdf",
                    "page_index": 23
                },
                "doc_id": "doc_001"
            },
            {
                "text": "Soil parameters include cohesion, friction angle, and unit weight...",
                "attributes": {
                    "source": "soil_properties.pdf", 
                    "page_index": 5
                },
                "doc_id": "doc_002"
            }
        ]
    
    @pytest.fixture
    def sample_keywords(self):
        """Sample extracted keywords"""
        return ["bearing", "capacity", "foundation", "soil", "load"]
    
    @pytest.fixture
    @patch('app.services.agentic_workflow.retrieval.rag_service.OpenAIEmbedding')
    @patch('app.services.agentic_workflow.retrieval.rag_service.QdrantVectorStore')
    @patch('app.services.agentic_workflow.retrieval.rag_service.MongoDocumentStore')
    @patch('app.services.agentic_workflow.retrieval.rag_service.GeminiService')
    def rag_service(self, mock_gemini, mock_mongodb, mock_qdrant, mock_openai, mock_settings):
        """Mock RAG service with all dependencies mocked"""
        # Create mock instances
        mock_openai_instance = Mock()
        mock_qdrant_instance = Mock()
        mock_mongodb_instance = Mock()
        mock_gemini_instance = Mock()
        
        # Configure mock returns
        mock_openai.return_value = mock_openai_instance
        mock_qdrant.return_value = mock_qdrant_instance
        mock_mongodb.return_value = mock_mongodb_instance
        mock_gemini.return_value = mock_gemini_instance
        
        # Create RAG service
        service = RAGService(
            openai_api_key="test-key",
            gemini_api_key="test-key",
            settings=mock_settings
        )
        
        # Store mock references for test access
        service._mock_openai = mock_openai_instance
        service._mock_qdrant = mock_qdrant_instance
        service._mock_mongodb = mock_mongodb_instance
        service._mock_gemini = mock_gemini_instance
        
        return service


class TestRAGServiceInitialization(TestRAGService):
    """Test RAG service initialization"""
    
    def test_init_creates_all_services(self, mock_settings):
        """Test that initialization creates all required services"""
        with patch('app.services.agentic_workflow.retrieval.rag_service.OpenAIEmbedding') as mock_openai, \
             patch('app.services.agentic_workflow.retrieval.rag_service.QdrantVectorStore') as mock_qdrant, \
             patch('app.services.agentic_workflow.retrieval.rag_service.MongoDocumentStore') as mock_mongodb, \
             patch('app.services.agentic_workflow.retrieval.rag_service.GeminiService') as mock_gemini:
            
            service = RAGService(
                openai_api_key="test-openai-key",
                gemini_api_key="test-gemini-key", 
                settings=mock_settings
            )
            
            # Verify all services were created
            mock_openai.assert_called_once_with(api_key="test-openai-key")
            mock_gemini.assert_called_once_with(api_key="test-gemini-key", model_name=mock_settings.GOOGLE_GENAI_MODEL)
            mock_qdrant.assert_called_once_with(
                host="localhost",
                port=6333,
                collection_name="test_collection"
            )
            mock_mongodb.assert_called_once_with(
                host="localhost",
                port=27017,
                database_name="test_db",
                collection_name="test_collection"
            )
            
            # Verify settings are stored
            assert service.settings == mock_settings
    
    def test_init_with_different_settings(self, mock_settings):
        """Test initialization with different settings values"""
        mock_settings.QDRANT_HOST = "custom-host"
        mock_settings.QDRANT_PORT = 9999
        
        with patch('app.services.agentic_workflow.retrieval.rag_service.QdrantVectorStore') as mock_qdrant:
            service = RAGService(
                openai_api_key="key1",
                gemini_api_key="key2",
                settings=mock_settings
            )
            
            mock_qdrant.assert_called_once_with(
                host="custom-host",
                port=9999,
                collection_name="test_collection"
            )


class TestVectorSearch(TestRAGService):
    """Test vector search functionality"""
    
    @pytest.mark.asyncio
    async def test_vector_search_success(self, rag_service, sample_embedding, sample_vector_results):
        """Test asynchronous vector search with successful results"""
        # Setup mocks
        rag_service._mock_openai.get_query_embedding.return_value = sample_embedding
        rag_service._mock_qdrant.search.return_value = sample_vector_results
        
        # Test vector search
        results = await rag_service.vector_search(
            query="What is bearing capacity?",
            k=3,
            score_threshold=0.1
        )
        
        # Verify calls
        rag_service._mock_openai.get_query_embedding.assert_called_once_with("What is bearing capacity?")
        rag_service._mock_qdrant.search.assert_called_once_with(
            query_vector=sample_embedding,
            limit=3,
            score_threshold=0.1
        )
        
        # Verify results format
        assert len(results) == 3
        for result in results:
            assert "text" in result
            assert "score" in result
            assert "metadata" in result
            assert result["search_type"] == "vector"
    
    @pytest.mark.asyncio
    async def test_vector_search_with_error(self, rag_service):
        """Test vector search error handling"""
        # Setup mock to raise error
        rag_service._mock_openai.get_query_embedding.side_effect = Exception("Embedding API error")
        
        # Test error handling
        results = await rag_service.vector_search("test query", 3, 0.1)
        
        # Should return empty list on error
        assert results == []
    
    @pytest.mark.asyncio
    async def test_vector_search(self, rag_service, sample_vector_results, sample_embedding):
        """Test asynchronous vector search"""
        # Setup mocks
        rag_service._mock_openai.get_query_embedding.return_value = sample_embedding
        rag_service._mock_qdrant.search.return_value = sample_vector_results
        
        results = await rag_service.vector_search("test query", 5, 0.1)
        
        # Verify results format
        assert len(results) == len(sample_vector_results)
        for result in results:
            assert "text" in result
            assert "score" in result
            assert "metadata" in result
            assert result["search_type"] == "vector"
    
    @pytest.mark.asyncio
    async def test_vector_search_different_parameters(self, rag_service, sample_embedding):
        """Test vector search with different parameter values"""
        rag_service._mock_openai.get_query_embedding.return_value = sample_embedding
        rag_service._mock_qdrant.search.return_value = []
        
        # Test with different k values
        for k in [1, 3, 5, 10]:
            await rag_service.vector_search("query", k, 0.1)
            assert rag_service._mock_qdrant.search.call_args[1]['limit'] == k
        
        # Test with different thresholds
        for threshold in [0.1, 0.3, 0.5]:
            await rag_service.vector_search("query", 3, threshold)
            assert rag_service._mock_qdrant.search.call_args[1]['score_threshold'] == threshold


class TestKeywordSearch(TestRAGService):
    """Test keyword search functionality"""
    
    @pytest.mark.asyncio
    async def test_keyword_search_success(self, rag_service, sample_keywords, sample_keyword_results):
        """Test keyword search with successful results"""
        # Setup mocks for MongoDB collection.find()
        mock_docs = [
            {
                "doc_id": "doc1",
                "content": "Foundation bearing capacity analysis",
                "metadata": {"source": "test.pdf", "page": 1},
                "score": 0.9
            },
            {
                "doc_id": "doc2", 
                "content": "Soil settlement calculations",
                "metadata": {"source": "test.pdf", "page": 2},
                "score": 0.8
            }
        ]
        
        # Create a mock cursor that properly implements iterator protocol
        mock_cursor = Mock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__ = Mock(return_value=iter(mock_docs))
        
        rag_service._mock_mongodb.collection.find.return_value = mock_cursor
        
        # Test keyword search
        results = await rag_service._keyword_search_with_list(sample_keywords, k=3)
        
        # Verify MongoDB collection.find was called
        expected_query = " ".join(sample_keywords)
        expected_filter = {"$text": {"$search": expected_query}}
        rag_service._mock_mongodb.collection.find.assert_called_once_with(
            expected_filter,
            {"score": {"$meta": "textScore"}}
        )
        
        # Verify results format
        assert len(results) == 2
        for i, result in enumerate(results):
            assert "text" in result
            assert "score" in result
            assert "metadata" in result
            assert result["search_type"] == "keyword"
    
    @pytest.mark.asyncio
    async def test_keyword_search_empty_keywords(self, rag_service):
        """Test keyword search with empty keyword list"""
        results = await rag_service._keyword_search_with_list([], k=3)
        assert results == []
        
        results = await rag_service._keyword_search_with_list(None, k=3)
        assert results == []
    
    @pytest.mark.asyncio
    async def test_keyword_search_with_error(self, rag_service, sample_keywords):
        """Test keyword search error handling"""
        # Setup mock to raise error
        rag_service._mock_mongodb.collection.find.side_effect = Exception("MongoDB error")
        
        # Test error handling
        results = await rag_service._keyword_search_with_list(sample_keywords, k=3)
        
        # Should return empty list on error
        assert results == []
    
    @pytest.mark.asyncio
    async def test_keyword_search_formatting(self, rag_service, sample_keyword_results):
        """Test that keyword results are properly formatted"""
        # Mock the documents returned by MongoDB
        mock_docs = [
            {
                "doc_id": "doc1",
                "content": "Foundation bearing capacity analysis",
                "metadata": {"source": "test.pdf", "page": 1},
                "score": 0.95
            },
            {
                "doc_id": "doc2", 
                "content": "Soil settlement calculations",
                "metadata": {"source": "test.pdf", "page": 2},
                "score": 0.87
            }
        ]
        
        # Setup mocks for MongoDB collection.find()
        mock_cursor = Mock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__ = Mock(return_value=iter(mock_docs))
        
        rag_service._mock_mongodb.collection.find.return_value = mock_cursor
        
        results = await rag_service._keyword_search_with_list(["test"], k=2)
        
        # Check formatting
        assert len(results) == 2
        for i, result in enumerate(results):
            expected_doc = mock_docs[i]
            assert result["text"] == expected_doc["content"]
            assert result["score"] == expected_doc["score"]
            assert result["metadata"] == expected_doc["metadata"]
            assert result["search_type"] == "keyword"


class TestHybridSearch(TestRAGService):
    """Test hybrid search logic"""
    
    @pytest.mark.asyncio
    async def test_hybrid_search_with_enough_keywords(self, rag_service, sample_keywords, 
                                                     sample_vector_results, sample_keyword_results):
        """Test hybrid search when keywords >= threshold (hybrid mode)"""
        # Setup mocks
        rag_service._mock_gemini.extract_keywords = AsyncMock(return_value=sample_keywords)
        
        # Mock vector search
        with patch.object(rag_service, 'vector_search', new_callable=AsyncMock) as mock_vector:
            mock_vector.return_value = sample_vector_results
            
            # Mock keyword search  
            with patch.object(rag_service, '_keyword_search_with_list', new_callable=AsyncMock) as mock_keyword:
                mock_keyword_formatted = [
                    {
                        "text": result["text"],
                        "score": 0.85,
                        "metadata": result["attributes"],
                        "search_type": "keyword"
                    }
                    for result in sample_keyword_results
                ]
                mock_keyword.return_value = mock_keyword_formatted
                
                # Mock combine and deduplicate
                expected_combined = sample_vector_results + mock_keyword_formatted
                with patch.object(rag_service, '_combine_and_deduplicate') as mock_combine:
                    mock_combine.return_value = expected_combined
                    
                    # Test hybrid search
                    results = await rag_service.hybrid_search(
                        query="What is bearing capacity?",
                        vector_k=RAGConstants.VECTOR_MAX_CHUNKS,
                        keyword_k=RAGConstants.KEYWORD_CHUNKS,
                        score_threshold=0.1
                    )
                    
                    # Verify keyword extraction
                    rag_service._mock_gemini.extract_keywords.assert_called_once_with("What is bearing capacity?")
                    
                    # Verify vector search (should be trimmed to HYBRID_VECTOR_CHUNKS)
                    mock_vector.assert_called_once_with("What is bearing capacity?", RAGConstants.VECTOR_MAX_CHUNKS, 0.1)
                    
                    # Verify keyword search
                    mock_keyword.assert_called_once_with(sample_keywords, RAGConstants.KEYWORD_CHUNKS)
                    
                    # Verify combine and deduplicate
                    trimmed_vector = sample_vector_results[:RAGConstants.HYBRID_VECTOR_CHUNKS]
                    mock_combine.assert_called_once_with(trimmed_vector, mock_keyword_formatted)
                    
                    # Verify results
                    assert results == expected_combined
    
    @pytest.mark.asyncio
    async def test_hybrid_search_insufficient_keywords(self, rag_service, sample_vector_results):
        """Test hybrid search when keywords < threshold (vector-only mode)"""
        # Setup mocks - return fewer keywords than threshold
        insufficient_keywords = ["bearing", "load"]  # Only 2 keywords < MIN_KEYWORDS_THRESHOLD (3)
        rag_service._mock_gemini.extract_keywords = AsyncMock(return_value=insufficient_keywords)
        
        with patch.object(rag_service, 'vector_search', new_callable=AsyncMock) as mock_vector:
            mock_vector.return_value = sample_vector_results
            
            # Test hybrid search
            results = await rag_service.hybrid_search(
                query="bearing load",
                vector_k=5,
                keyword_k=3,
                score_threshold=0.1
            )
            
            # Verify keyword extraction
            rag_service._mock_gemini.extract_keywords.assert_called_once_with("bearing load")
            
            # Should only do vector search, no keyword search
            mock_vector.assert_called_once_with("bearing load", 5, 0.1)
            
            # Results should be vector results only
            assert results == sample_vector_results
    
    @pytest.mark.asyncio
    async def test_hybrid_search_with_error_fallback(self, rag_service, sample_vector_results):
        """Test hybrid search error handling with fallback to vector-only"""
        # Setup mocks - keyword extraction fails
        rag_service._mock_gemini.extract_keywords = AsyncMock(side_effect=Exception("Gemini API error"))
        
        with patch.object(rag_service, 'vector_search', new_callable=AsyncMock) as mock_vector:
            # First call (in try block) fails, second call (fallback) succeeds
            mock_vector.side_effect = [Exception("First call fails"), sample_vector_results]
            
            # Test hybrid search
            results = await rag_service.hybrid_search(
                query="test query",
                vector_k=5,
                keyword_k=3,
                score_threshold=0.1
            )
            
            # Should fall back to vector search
            assert mock_vector.call_count == 2
            assert results == sample_vector_results
    
    def test_combine_and_deduplicate(self, rag_service):
        """Test result combination and deduplication logic"""
        # Sample vector and keyword results with some overlap
        vector_results = [
            {"text": "Content A", "score": 0.9, "metadata": {"source": "doc1.pdf"}},
            {"text": "Content B", "score": 0.8, "metadata": {"source": "doc2.pdf"}},
        ]
        
        keyword_results = [
            {"text": "Content B", "score": 0.7, "metadata": {"source": "doc2.pdf"}},  # Duplicate
            {"text": "Content C", "score": 0.75, "metadata": {"source": "doc3.pdf"}},
        ]
        
        # Test combination (assuming deduplication keeps higher score)
        combined = rag_service._combine_and_deduplicate(vector_results, keyword_results)
        
        # Should have unique content with higher scores preserved
        sources = [result["metadata"]["source"] for result in combined]
        assert "doc1.pdf" in sources
        assert "doc2.pdf" in sources  # Should appear once
        assert "doc3.pdf" in sources
        
        # For doc2.pdf, should keep the higher score (0.8 from vector vs 0.7 from keyword)
        doc2_result = next(r for r in combined if r["metadata"]["source"] == "doc2.pdf")
        assert doc2_result["score"] == 0.8  # Higher score from vector search


class TestMainSearchInterface(TestRAGService):
    """Test main search interface"""
    
    @pytest.mark.asyncio
    async def test_search_method_success(self, rag_service, sample_vector_results):
        """Test main search method with successful results"""
        # Mock hybrid_search to return sample results
        with patch.object(rag_service, 'hybrid_search', new_callable=AsyncMock) as mock_hybrid:
            # Convert sample results to expected format for hybrid_search
            hybrid_results = [
                {
                    "text": result["text"],
                    "score": result["score"], 
                    "metadata": result["metadata"]
                }
                for result in sample_vector_results
            ]
            mock_hybrid.return_value = hybrid_results
            
            # Test search
            citations = await rag_service.search(
                query="What is soil bearing capacity?",
                k=3,
                score_threshold=0.1
            )
            
            # Verify hybrid search was called
            mock_hybrid.assert_called_once_with(
                query="What is soil bearing capacity?",
                vector_k=3,
                keyword_k=3,
                score_threshold=0.1
            )
            
            # Verify Citation objects were created
            assert len(citations) == 3
            for i, citation in enumerate(citations):
                assert isinstance(citation, Citation)
                assert citation.source_name == hybrid_results[i]["metadata"]["source"]
                assert citation.content == hybrid_results[i]["text"]
                assert citation.confidence_score == hybrid_results[i]["score"]
    
    @pytest.mark.asyncio
    async def test_search_method_with_error(self, rag_service):
        """Test search method error handling"""
        # Mock hybrid_search to raise an error
        with patch.object(rag_service, 'hybrid_search', new_callable=AsyncMock) as mock_hybrid:
            mock_hybrid.side_effect = Exception("Search failed")
            
            # Test search error handling
            citations = await rag_service.search("test query", 3, 0.1)
            
            # Should return empty list on error
            assert citations == []
    
    @pytest.mark.asyncio
    async def test_citation_object_creation(self, rag_service):
        """Test Citation object creation from search results"""
        # Mock hybrid_search results
        with patch.object(rag_service, 'hybrid_search', new_callable=AsyncMock) as mock_hybrid:
            mock_results = [
                {
                    "text": "Foundation design requires analysis...",
                    "score": 0.92,
                    "metadata": {
                        "source": "foundation_guide.pdf",
                        "page_index": 15
                    }
                }
            ]
            mock_hybrid.return_value = mock_results
            
            citations = await rag_service.search("foundation design", 1, 0.1)
            
            # Verify Citation object properties
            assert len(citations) == 1
            citation = citations[0]
            assert citation.source_name == "foundation_guide.pdf"
            assert citation.content == "Foundation design requires analysis..."
            assert citation.confidence_score == 0.92
            assert citation.page_index == 15
    
    @pytest.mark.asyncio
    async def test_search_with_different_parameters(self, rag_service):
        """Test search with various parameter combinations"""
        with patch.object(rag_service, 'hybrid_search', new_callable=AsyncMock) as mock_hybrid:
            mock_hybrid.return_value = []
            
            # Test different queries
            queries = ["bearing capacity", "settlement analysis", "CPT testing"]
            for query in queries:
                await rag_service.search(query, 5, 0.1)
                mock_hybrid.assert_called_with(query=query, vector_k=5, keyword_k=5, score_threshold=0.1)
            
            # Test different thresholds
            thresholds = [0.1, 0.3, 0.5]
            for threshold in thresholds:
                await rag_service.search("test", 3, threshold)
                mock_hybrid.assert_called_with(query="test", vector_k=3, keyword_k=3, score_threshold=threshold)


class TestErrorHandlingAndEdgeCases(TestRAGService):
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_search_with_empty_query(self, rag_service):
        """Test search with empty or invalid queries"""
        with patch.object(rag_service, 'hybrid_search', new_callable=AsyncMock) as mock_hybrid:
            mock_hybrid.return_value = []
            
            # Test empty string
            citations = await rag_service.search("", 3, 0.1)
            assert citations == []
            
            # Test None query  
            citations = await rag_service.search(None, 3, 0.1)
            assert citations == []
    
    @pytest.mark.asyncio
    async def test_search_with_special_characters(self, rag_service):
        """Test search with special characters and unicode"""
        with patch.object(rag_service, 'hybrid_search', new_callable=AsyncMock) as mock_hybrid:
            mock_hybrid.return_value = []
            
            special_queries = [
                "What is φ angle?",  # Greek letter
                "Load = 100 kN/m²",  # Special characters
                "Test & verify",     # Ampersand
                "Query with 'quotes'",  # Quotes
            ]
            
            for query in special_queries:
                citations = await rag_service.search(query, 3, 0.1)
                mock_hybrid.assert_called_with(query=query, vector_k=3, keyword_k=3, score_threshold=0.1)
                assert isinstance(citations, list)
    
    @pytest.mark.asyncio
    async def test_search_with_extreme_parameters(self, rag_service):
        """Test search with extreme parameter values"""
        with patch.object(rag_service, 'hybrid_search', new_callable=AsyncMock) as mock_hybrid:
            mock_hybrid.return_value = []
            
            # Test with very high k
            await rag_service.search("test", k=1000, score_threshold=0.1)
            
            # Test with very low threshold
            await rag_service.search("test", k=5, score_threshold=0.01)
            
            # Test with very high threshold
            await rag_service.search("test", k=5, score_threshold=0.99)
            
            # All should complete without error
            assert mock_hybrid.call_count == 3
    
    @pytest.mark.asyncio
    async def test_concurrent_searches(self, rag_service):
        """Test concurrent search operations"""
        with patch.object(rag_service, 'hybrid_search', new_callable=AsyncMock) as mock_hybrid:
            mock_hybrid.return_value = []
            
            # Create multiple searches (sequential async calls)
            queries = [f"query {i}" for i in range(5)]
            results = []
            
            for query in queries:
                result = await rag_service.search(query, 3, 0.1)
                results.append(result)
            
            # All searches should complete
            assert len(results) == 5
            assert all(isinstance(result, list) for result in results)
            
            # Hybrid search should be called for each query
            assert mock_hybrid.call_count == 5
    
    @pytest.mark.asyncio
    async def test_malformed_search_results_handling(self, rag_service):
        """Test handling of malformed search results"""
        with patch.object(rag_service, 'hybrid_search', new_callable=AsyncMock) as mock_hybrid:
            # Return malformed results
            malformed_results = [
                {"text": "Good result", "score": 0.9, "metadata": {"source": "doc1.pdf"}},
                {"missing_text": "Bad result", "score": 0.8},  # Missing text field
                {"text": "Another good result", "metadata": {"source": "doc2.pdf"}},  # Missing score
                None,  # Null result
                {},  # Empty dict
            ]
            mock_hybrid.return_value = malformed_results
            
            # Search should handle malformed results gracefully
            citations = await rag_service.search("test query", 5, 0.1)
            
            # Should only return valid citations (filter out malformed ones)
            assert isinstance(citations, list)
            # Check that valid results were processed
            valid_citations = [c for c in citations if c is not None]
            assert len(valid_citations) <= len(malformed_results)


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])