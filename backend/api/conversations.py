from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import os
from services.chromadb_service import ChromaDBService
from services.file_processor import FileProcessor

router = APIRouter()

# Initialize services
chromadb_service = ChromaDBService()
file_processor = FileProcessor()

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = datetime.now()
    context_used: Optional[List[dict]] = None  # RAG context information

class Conversation(BaseModel):
    id: str
    title: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
    rag_enabled: Optional[bool] = False

# Simple file-based storage for now
CONVERSATIONS_FILE = "conversations.json"

def load_conversations():
    """Load conversations from file"""
    if os.path.exists(CONVERSATIONS_FILE):
        try:
            with open(CONVERSATIONS_FILE, 'r') as f:
                data = json.load(f)
                # Convert timestamp strings back to datetime objects
                for conv in data:
                    conv['created_at'] = datetime.fromisoformat(conv['created_at'])
                    conv['updated_at'] = datetime.fromisoformat(conv['updated_at'])
                    for msg in conv['messages']:
                        msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
                return data
        except:
            return []
    return []

def save_conversations(conversations):
    """Save conversations to file"""
    # Convert datetime objects to strings for JSON serialization
    data = []
    for conv in conversations:
        conv_data = {
            'id': conv['id'],
            'title': conv['title'],
            'created_at': conv['created_at'].isoformat(),
            'updated_at': conv['updated_at'].isoformat(),
            'messages': []
        }
        for msg in conv['messages']:
            conv_data['messages'].append({
                'role': msg['role'],
                'content': msg['content'],
                'timestamp': msg['timestamp'].isoformat()
            })
        data.append(conv_data)
    
    with open(CONVERSATIONS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@router.get("/")
async def get_conversations():
    """Get all conversations"""
    conversations = load_conversations()
    return {"conversations": conversations}

@router.post("/")
async def create_conversation(request: dict):
    """Create a new conversation"""
    conversations = load_conversations()
    
    # Generate a simple ID
    conversation_id = f"conv_{len(conversations) + 1}_{int(datetime.now().timestamp())}"
    
    new_conversation = {
        'id': conversation_id,
        'title': request.get('title', 'New Conversation'),
        'messages': [],
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    conversations.append(new_conversation)
    save_conversations(conversations)
    
    return {"conversation": new_conversation}

@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation"""
    conversations = load_conversations()
    conversation = next((conv for conv in conversations if conv['id'] == conversation_id), None)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"conversation": conversation}

@router.post("/{conversation_id}/messages")
async def add_message(conversation_id: str, request: dict):
    """Add a message to a conversation with optional RAG context"""
    conversations = load_conversations()
    conversation = next((conv for conv in conversations if conv['id'] == conversation_id), None)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    user_content = request.get('content', '')
    role = request.get('role', 'user')
    rag_enabled = request.get('rag_enabled', False)
    context_limit = request.get('context_limit', 3)
    
    # Get RAG context if enabled and this is a user message
    context_used = None
    if rag_enabled and role == 'user' and chromadb_service.is_available():
        try:
            context_docs = chromadb_service.search_documents(user_content, context_limit)
            if context_docs:
                context_used = [
                    {
                        "id": doc.get("id", ""),
                        "content": doc.get("content", "")[:500] + "..." if len(doc.get("content", "")) > 500 else doc.get("content", ""),
                        "metadata": doc.get("metadata", {}),
                        "relevance_score": 1 - doc.get("distance", 1)  # Convert distance to relevance
                    }
                    for doc in context_docs
                    if doc.get("distance", 1) < 0.8  # Only include relevant results
                ]
        except Exception as e:
            print(f"RAG context retrieval error: {e}")
    
    message = {
        'role': role,
        'content': user_content,
        'timestamp': datetime.now(),
        'context_used': context_used
    }
    
    conversation['messages'].append(message)
    conversation['updated_at'] = datetime.now()
    
    # Update conversation RAG setting
    if 'rag_enabled' in request:
        conversation['rag_enabled'] = rag_enabled
    
    # Auto-generate title if this is the first user message
    if len(conversation['messages']) == 1 and message['role'] == 'user':
        # Simple title generation from first message
        title = message['content'][:50] + "..." if len(message['content']) > 50 else message['content']
        conversation['title'] = title
    
    # Add conversation context to ChromaDB if it's available
    if chromadb_service.is_available() and len(conversation['messages']) >= 2:
        try:
            # Add recent conversation context to knowledge base
            recent_messages = conversation['messages'][-2:]  # Last 2 messages
            chromadb_service.add_conversation_context(conversation_id, recent_messages)
        except Exception as e:
            print(f"Error adding conversation context to ChromaDB: {e}")
    
    save_conversations(conversations)
    
    return {
        "message": message,
        "rag_context": {
            "enabled": rag_enabled,
            "context_found": len(context_used) if context_used else 0,
            "chromadb_available": chromadb_service.is_available()
        }
    }

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    conversations = load_conversations()
    conversations = [conv for conv in conversations if conv['id'] != conversation_id]
    save_conversations(conversations)
    
    return {"success": True}