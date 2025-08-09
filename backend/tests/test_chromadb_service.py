import pytest
import asyncio
import tempfile
import shutil
import os
from unittest.mock import patch, MagicMock, AsyncMock
import sys
sys.path.append('..')

from services.chromadb_service import ChromaDBService

class TestChromaDBService:
    """Test suite for ChromaDB service functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
    
    def teardown_method(self):
        """Clean up test environment"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch('services.chromadb_service.chromadb.HttpClient')
    def test_http_client_initialization_success(self, mock_http_client):
        """Test successful HTTP client initialization"""
        mock_client = MagicMock()
        mock_client.heartbeat.return_value = True
        mock_http_client.return_value = mock_client
        
        # Mock collections
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        
        service = ChromaDBService(host="localhost", port=8000)
        
        assert service.client is not None
        assert service.collection is not None
        assert service.conversations_collection is not None
        assert service.files_collection is not None
        mock_http_client.assert_called_once_with(host="localhost", port=8000)
    
    @patch('services.chromadb_service.chromadb.HttpClient')
    @patch('services.chromadb_service.chromadb.PersistentClient')
    @patch('os.makedirs')
    def test_fallback_to_embedded_client(self, mock_makedirs, mock_persistent_client, mock_http_client):
        """Test fallback to embedded client when HTTP fails"""
        # Make HTTP client fail
        mock_http_client.side_effect = Exception("Connection failed")
        
        # Mock embedded client success
        mock_embedded_client = MagicMock()
        mock_persistent_client.return_value = mock_embedded_client
        
        # Mock collections
        mock_collection = MagicMock()
        mock_embedded_client.get_or_create_collection.return_value = mock_collection
        
        service = ChromaDBService(host="localhost", port=8000)
        
        assert service.client is not None
        mock_persistent_client.assert_called_once_with(path="/data")
        mock_makedirs.assert_called_once_with("/data", exist_ok=True)
    
    @patch('services.chromadb_service.chromadb.HttpClient')
    @patch('services.chromadb_service.chromadb.PersistentClient')
    @patch('os.makedirs')
    def test_complete_initialization_failure(self, mock_makedirs, mock_persistent_client, mock_http_client):
        """Test when both HTTP and embedded clients fail"""
        # Make both clients fail
        mock_http_client.side_effect = Exception("HTTP failed")
        mock_persistent_client.side_effect = Exception("Embedded failed")
        
        service = ChromaDBService(host="localhost", port=8000)
        
        assert service.client is None
        assert service.collection is None
    
    @patch('services.chromadb_service.chromadb.HttpClient')
    def test_is_available_method(self, mock_http_client):
        """Test the is_available method"""
        mock_client = MagicMock()
        mock_client.heartbeat.return_value = True
        mock_http_client.return_value = mock_client
        
        # Mock collections
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        
        service = ChromaDBService()
        assert service.is_available() is True
        
        # Test when client is None
        service.client = None
        assert service.is_available() is False
    
    @patch('services.chromadb_service.chromadb.HttpClient')
    @pytest.mark.asyncio
    async def test_add_document_success(self, mock_http_client):
        """Test successful document addition"""
        mock_client = MagicMock()
        mock_client.heartbeat.return_value = True
        mock_http_client.return_value = mock_client
        
        # Mock collection
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        
        service = ChromaDBService()
        
        doc_id = await service.add_document("Test content", {"source": "test"})
        
        assert doc_id is not None
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        assert call_args[1]['documents'] == ["Test content"]
        assert call_args[1]['metadatas'][0]['source'] == "test"
    
    @patch('services.chromadb_service.chromadb.HttpClient')
    @pytest.mark.asyncio
    async def test_search_documents_success(self, mock_http_client):
        """Test successful document search"""
        mock_client = MagicMock()
        mock_client.heartbeat.return_value = True
        mock_http_client.return_value = mock_client
        
        # Mock collection with search results
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'documents': [["Document 1", "Document 2"]],
            'distances': [[0.1, 0.3]],
            'ids': [["doc1", "doc2"]],
            'metadatas': [[{"source": "test1"}, {"source": "test2"}]]
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        
        service = ChromaDBService()
        
        results = await service.search_documents("test query", limit=2)
        
        assert len(results) == 2
        assert results[0]['content'] == "Document 1"
        assert results[0]['id'] == "doc1"
        assert results[0]['metadata']['source'] == "test1"
        assert results[0]['distance'] == 0.1
        assert results[0]['relevance_score'] == 0.9  # 1.0 - 0.1
        
        # Check that results are sorted by relevance (highest first)
        assert results[0]['relevance_score'] > results[1]['relevance_score']
    
    @patch('services.chromadb_service.chromadb.HttpClient')
    @pytest.mark.asyncio
    async def test_search_documents_distance_filtering(self, mock_http_client):
        """Test distance threshold filtering in document search"""
        mock_client = MagicMock()
        mock_client.heartbeat.return_value = True
        mock_http_client.return_value = mock_client
        
        # Mock collection with results - some above threshold
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'documents': [["Good doc", "Bad doc"]],
            'distances': [[0.1, 0.9]],  # Second doc has high distance (low relevance)
            'ids': [["doc1", "doc2"]],
            'metadatas': [[{"source": "test1"}, {"source": "test2"}]]
        }
        mock_client.get_or_create_collection.return_value = mock_collection
        
        service = ChromaDBService()
        
        # Use default distance threshold of 0.8
        results = await service.search_documents("test query", limit=2, distance_threshold=0.8)
        
        # Should only return the first document (distance 0.1 <= 0.8)
        assert len(results) == 1
        assert results[0]['content'] == "Good doc"
        assert results[0]['distance'] == 0.1
    
    @patch('services.chromadb_service.chromadb.HttpClient')
    @pytest.mark.asyncio
    async def test_add_conversation_context(self, mock_http_client):
        """Test adding conversation context"""
        mock_client = MagicMock()
        mock_client.heartbeat.return_value = True
        mock_http_client.return_value = mock_client
        
        # Mock collections
        mock_collection = MagicMock()
        mock_conversations_collection = MagicMock()
        mock_client.get_or_create_collection.side_effect = [
            mock_collection,
            mock_conversations_collection,
            MagicMock()  # files collection
        ]
        
        service = ChromaDBService()
        
        messages = [
            {"role": "user", "content": "Hello", "timestamp": "2023-01-01T00:00:00"},
            {"role": "assistant", "content": "Hi there!", "timestamp": "2023-01-01T00:01:00"}
        ]
        
        await service.add_conversation_context("conv_123", messages)
        
        mock_conversations_collection.add.assert_called_once()
        call_args = mock_conversations_collection.add.call_args
        
        # Check that the conversation text was formatted correctly
        doc_content = call_args[1]['documents'][0]
        assert "Conversation conv_123:" in doc_content
        assert "user: Hello" in doc_content
        assert "assistant: Hi there!" in doc_content
        
        # Check metadata
        metadata = call_args[1]['metadatas'][0]
        assert metadata['type'] == 'conversation'
        assert metadata['conversation_id'] == 'conv_123'
        assert metadata['message_count'] == 2
    
    @patch('services.chromadb_service.chromadb.HttpClient')
    @pytest.mark.asyncio
    async def test_add_file_content(self, mock_http_client):
        """Test adding file content"""
        mock_client = MagicMock()
        mock_client.heartbeat.return_value = True
        mock_http_client.return_value = mock_client
        
        # Mock collections
        mock_collection = MagicMock()
        mock_conversations_collection = MagicMock()
        mock_files_collection = MagicMock()
        mock_client.get_or_create_collection.side_effect = [
            mock_collection,
            mock_conversations_collection,
            mock_files_collection
        ]
        
        service = ChromaDBService()
        
        file_id = await service.add_file_content(
            "document.txt", 
            "This is test file content", 
            "txt",
            {"author": "test"}
        )
        
        assert file_id is not None
        mock_files_collection.add.assert_called_once()
        call_args = mock_files_collection.add.call_args
        
        assert call_args[1]['documents'] == ["This is test file content"]
        metadata = call_args[1]['metadatas'][0]
        assert metadata['type'] == 'file'
        assert metadata['filename'] == 'document.txt'
        assert metadata['file_type'] == 'txt'
        assert metadata['author'] == 'test'
        assert 'upload_timestamp' in metadata
        assert metadata['content_length'] == len("This is test file content")
    
    @patch('services.chromadb_service.chromadb.HttpClient')
    @pytest.mark.asyncio
    async def test_search_files(self, mock_http_client):
        """Test searching files with type filtering"""
        mock_client = MagicMock()
        mock_client.heartbeat.return_value = True
        mock_http_client.return_value = mock_client
        
        # Mock collections
        mock_collection = MagicMock()
        mock_conversations_collection = MagicMock()
        mock_files_collection = MagicMock()
        mock_files_collection.query.return_value = {
            'documents': [["File content"]],
            'distances': [[0.2]],
            'ids': [["file1"]],
            'metadatas': [[{"filename": "test.txt", "file_type": "txt"}]]
        }
        mock_client.get_or_create_collection.side_effect = [
            mock_collection,
            mock_conversations_collection,
            mock_files_collection
        ]
        
        service = ChromaDBService()
        
        results = await service.search_files("test query", file_type="txt", limit=5)
        
        assert len(results) == 1
        assert results[0]['content'] == "File content"
        assert results[0]['metadata']['filename'] == "test.txt"
        
        # Verify that where clause was used for file type filtering
        call_args = mock_files_collection.query.call_args
        assert call_args[1]['where'] == {"file_type": "txt"}
    
    @patch('services.chromadb_service.chromadb.HttpClient')
    def test_get_collection_stats(self, mock_http_client):
        """Test getting collection statistics"""
        mock_client = MagicMock()
        mock_client.heartbeat.return_value = True
        mock_http_client.return_value = mock_client
        
        # Mock collections with different counts
        mock_collection = MagicMock()
        mock_collection.count.return_value = 5
        mock_conversations_collection = MagicMock()
        mock_conversations_collection.count.return_value = 3
        mock_files_collection = MagicMock()
        mock_files_collection.count.return_value = 2
        
        mock_client.get_or_create_collection.side_effect = [
            mock_collection,
            mock_conversations_collection,
            mock_files_collection
        ]
        
        service = ChromaDBService()
        stats = service.get_collection_stats()
        
        assert stats['available'] is True
        assert stats['knowledge_documents'] == 5
        assert stats['conversations'] == 3
        assert stats['files'] == 2
        assert stats['total_documents'] == 10
        assert len(stats['collections']) == 3
        
        # Check collection details
        knowledge_collection = next(c for c in stats['collections'] if c['name'] == 'evolveui_knowledge')
        assert knowledge_collection['count'] == 5
        assert knowledge_collection['type'] == 'knowledge_base'
    
    @patch('services.chromadb_service.chromadb.HttpClient')
    @pytest.mark.asyncio
    async def test_bulk_add_documents(self, mock_http_client):
        """Test bulk document addition"""
        mock_client = MagicMock()
        mock_client.heartbeat.return_value = True
        mock_http_client.return_value = mock_client
        
        # Mock collection
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        
        service = ChromaDBService()
        
        documents = [
            {"content": "Doc 1", "metadata": {"source": "test1"}},
            {"content": "Doc 2", "metadata": {"source": "test2"}},
            {"content": "", "metadata": {"source": "empty"}},  # Should be skipped
        ]
        
        result = await service.bulk_add_documents(documents)
        
        assert result['success'] is True
        assert result['added'] == 2  # Empty document should be skipped
        assert len(result['errors']) == 0
        
        mock_collection.add.assert_called_once()
        call_args = mock_collection.add.call_args
        assert len(call_args[1]['documents']) == 2
        assert "Doc 1" in call_args[1]['documents']
        assert "Doc 2" in call_args[1]['documents']
    
    @patch('services.chromadb_service.chromadb.HttpClient')
    @pytest.mark.asyncio
    async def test_connection_retry_logic(self, mock_http_client):
        """Test connection retry and reconnection logic"""
        mock_client = MagicMock()
        
        # First heartbeat fails, second succeeds (simulating temporary network issue)
        mock_client.heartbeat.side_effect = [Exception("Network error"), True]
        mock_http_client.return_value = mock_client
        
        # Mock collections
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        
        service = ChromaDBService(max_retries=2)
        
        # Should eventually succeed after retry
        assert service.client is not None
        
        # Test _check_connection method
        service._last_connection_check = 0  # Force connection check
        assert service._check_connection() is True
    
    @pytest.mark.asyncio
    async def test_service_unavailable_handling(self):
        """Test handling when ChromaDB service is completely unavailable"""
        # Create service with no client
        service = ChromaDBService()
        service.client = None
        service.collection = None
        
        # All operations should handle unavailable service gracefully
        assert service.is_available() is False
        
        # Test that search_documents returns empty list when service unavailable
        results = await service.search_documents("test")
        assert results == []
        
        stats = service.get_collection_stats()
        assert stats['available'] is False
        assert 'error' in stats

if __name__ == "__main__":
    pytest.main([__file__])