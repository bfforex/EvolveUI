import pytest
import json
import os
import tempfile
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
sys.path.append('..')

from main import app
from api.conversations import load_conversations, save_conversations

class TestConversationsAPI:
    """Test suite for conversations API endpoints"""
    
    def setup_method(self):
        """Set up test client and temporary file"""
        self.client = TestClient(app)
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.original_conversations_file = 'conversations.json'
        
    def teardown_method(self):
        """Clean up after each test"""
        # Clean up temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        # Clean up test conversations file
        if os.path.exists('test_conversations.json'):
            os.remove('test_conversations.json')
        # Clean up any conversations.json that might be a directory
        if os.path.exists('conversations.json') and os.path.isdir('conversations.json'):
            shutil.rmtree('conversations.json')
    
    def test_get_conversations_empty(self):
        """Test getting conversations when none exist"""
        response = self.client.get("/api/conversations/")
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        assert isinstance(data["conversations"], list)
    
    def test_create_conversation(self):
        """Test creating a new conversation"""
        response = self.client.post(
            "/api/conversations/",
            json={"title": "Test Conversation"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "conversation" in data
        conv = data["conversation"]
        assert conv["title"] == "Test Conversation"
        assert "id" in conv
        assert "created_at" in conv
        assert "updated_at" in conv
        assert conv["messages"] == []
    
    def test_get_conversation_by_id(self):
        """Test getting a specific conversation by ID"""
        # First create a conversation
        create_response = self.client.post(
            "/api/conversations/",
            json={"title": "Test Conversation"}
        )
        conv_id = create_response.json()["conversation"]["id"]
        
        # Then get it by ID
        response = self.client.get(f"/api/conversations/{conv_id}")
        assert response.status_code == 200
        data = response.json()
        assert "conversation" in data
        assert data["conversation"]["id"] == conv_id
        assert data["conversation"]["title"] == "Test Conversation"
    
    def test_get_nonexistent_conversation(self):
        """Test getting a conversation that doesn't exist"""
        response = self.client.get("/api/conversations/nonexistent_id")
        assert response.status_code == 404
        assert "Conversation not found" in response.json()["detail"]
    
    def test_add_message_to_conversation(self):
        """Test adding a message to a conversation"""
        # Create a conversation
        create_response = self.client.post(
            "/api/conversations/",
            json={"title": "Test Conversation"}
        )
        conv_id = create_response.json()["conversation"]["id"]
        
        # Add a message
        message_response = self.client.post(
            f"/api/conversations/{conv_id}/messages",
            json={"role": "user", "content": "Hello, world!"}
        )
        assert message_response.status_code == 200
        message_data = message_response.json()
        assert "message" in message_data
        message = message_data["message"]
        assert message["role"] == "user"
        assert message["content"] == "Hello, world!"
        assert "timestamp" in message
        
        # Verify the message was added to the conversation
        conv_response = self.client.get(f"/api/conversations/{conv_id}")
        conv_data = conv_response.json()["conversation"]
        assert len(conv_data["messages"]) == 1
        assert conv_data["messages"][0]["content"] == "Hello, world!"
    
    def test_add_message_to_nonexistent_conversation(self):
        """Test adding a message to a conversation that doesn't exist"""
        response = self.client.post(
            "/api/conversations/nonexistent_id/messages",
            json={"role": "user", "content": "Hello"}
        )
        assert response.status_code == 404
        assert "Conversation not found" in response.json()["detail"]
    
    def test_delete_conversation(self):
        """Test deleting a conversation"""
        # Create a conversation
        create_response = self.client.post(
            "/api/conversations/",
            json={"title": "Test Conversation"}
        )
        conv_id = create_response.json()["conversation"]["id"]
        
        # Delete it
        delete_response = self.client.delete(f"/api/conversations/{conv_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["success"] is True
        
        # Verify it's gone
        get_response = self.client.get(f"/api/conversations/{conv_id}")
        assert get_response.status_code == 404
    
    def test_conversation_title_auto_generation(self):
        """Test that conversation title is auto-generated from first message"""
        # Create a conversation
        create_response = self.client.post(
            "/api/conversations/",
            json={"title": "New Conversation"}
        )
        conv_id = create_response.json()["conversation"]["id"]
        
        # Add first user message
        message_content = "This is a test message for title generation"
        self.client.post(
            f"/api/conversations/{conv_id}/messages",
            json={"role": "user", "content": message_content}
        )
        
        # Check that title was updated
        conv_response = self.client.get(f"/api/conversations/{conv_id}")
        conv_data = conv_response.json()["conversation"]
        assert conv_data["title"] == message_content  # Should be the full message since it's under 50 chars
    
    def test_conversation_title_truncation(self):
        """Test that long conversation titles are truncated"""
        # Create a conversation
        create_response = self.client.post(
            "/api/conversations/",
            json={"title": "New Conversation"}
        )
        conv_id = create_response.json()["conversation"]["id"]
        
        # Add a very long first user message
        long_message = "This is a very long message that should be truncated when used as a conversation title because it exceeds the fifty character limit"
        self.client.post(
            f"/api/conversations/{conv_id}/messages",
            json={"role": "user", "content": long_message}
        )
        
        # Check that title was updated and truncated
        conv_response = self.client.get(f"/api/conversations/{conv_id}")
        conv_data = conv_response.json()["conversation"]
        assert len(conv_data["title"]) == 53  # 50 chars + "..."
        assert conv_data["title"].endswith("...")
        assert conv_data["title"].startswith("This is a very long message")

class TestConversationsFileHandling:
    """Test suite for conversation file handling and directory issue prevention"""
    
    def setup_method(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def teardown_method(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_load_conversations_empty_file(self):
        """Test loading when no conversations file exists"""
        conversations = load_conversations()
        assert conversations == []
    
    def test_load_conversations_directory_instead_of_file(self):
        """Test handling when conversations.json is a directory"""
        # Create a directory named conversations.json
        os.makedirs('conversations.json')
        
        # Should handle this gracefully and return empty list
        conversations = load_conversations()
        assert conversations == []
        # Directory should be removed
        assert not os.path.exists('conversations.json')
    
    def test_save_conversations_removes_directory(self):
        """Test that save_conversations removes directory if it exists"""
        # Create a directory named conversations.json
        os.makedirs('conversations.json')
        
        # Try to save conversations
        test_conversations = [{
            'id': 'test_1',
            'title': 'Test',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'messages': []
        }]
        
        save_conversations(test_conversations)
        
        # Should have removed directory and created file
        assert os.path.isfile('conversations.json')
        assert not os.path.isdir('conversations.json')
        
        # Verify content
        with open('conversations.json', 'r') as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]['id'] == 'test_1'
    
    def test_load_and_save_conversation_data(self):
        """Test loading and saving conversation data maintains integrity"""
        # Create test data
        original_time = datetime.now()
        test_conversations = [{
            'id': 'test_conv_1',
            'title': 'Test Conversation',
            'created_at': original_time,
            'updated_at': original_time,
            'messages': [{
                'role': 'user',
                'content': 'Hello',
                'timestamp': original_time
            }]
        }]
        
        # Save and load
        save_conversations(test_conversations)
        loaded_conversations = load_conversations()
        
        # Verify data integrity
        assert len(loaded_conversations) == 1
        conv = loaded_conversations[0]
        assert conv['id'] == 'test_conv_1'
        assert conv['title'] == 'Test Conversation'
        assert isinstance(conv['created_at'], datetime)
        assert isinstance(conv['updated_at'], datetime)
        assert len(conv['messages']) == 1
        msg = conv['messages'][0]
        assert msg['role'] == 'user'
        assert msg['content'] == 'Hello'
        assert isinstance(msg['timestamp'], datetime)
    
    def test_save_conversations_error_handling(self):
        """Test error handling in save_conversations"""
        # Create a file with the conversations.json name to cause conflict
        with open('conversations.json', 'w') as f:
            f.write("not json content")
        
        # Make the file read-only
        os.chmod('conversations.json', 0o444)
        
        test_conversations = [{
            'id': 'test',
            'title': 'Test',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'messages': []
        }]
        
        try:
            # Should raise an exception due to permission error
            with pytest.raises(Exception):
                save_conversations(test_conversations)
        finally:
            # Clean up - restore permissions and remove file
            try:
                os.chmod('conversations.json', 0o644)
                os.remove('conversations.json')
            except:
                pass

if __name__ == "__main__":
    pytest.main([__file__])