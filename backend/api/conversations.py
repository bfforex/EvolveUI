from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import os

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = datetime.now()

class Conversation(BaseModel):
    id: str
    title: str
    messages: List[Message]
    created_at: datetime
    updated_at: datetime

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
        # Handle both datetime objects and ISO strings
        created_at = conv['created_at']
        if hasattr(created_at, 'isoformat'):
            created_at = created_at.isoformat()
        
        updated_at = conv['updated_at']
        if hasattr(updated_at, 'isoformat'):
            updated_at = updated_at.isoformat()
        
        conv_data = {
            'id': conv['id'],
            'title': conv['title'],
            'created_at': created_at,
            'updated_at': updated_at,
            'messages': []
        }
        for msg in conv['messages']:
            # Handle both datetime objects and ISO strings for message timestamps
            timestamp = msg['timestamp']
            if hasattr(timestamp, 'isoformat'):
                timestamp = timestamp.isoformat()
            
            conv_data['messages'].append({
                'role': msg['role'],
                'content': msg['content'],
                'timestamp': timestamp
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
    """Add a message to a conversation"""
    conversations = load_conversations()
    conversation = next((conv for conv in conversations if conv['id'] == conversation_id), None)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    message = {
        'role': request.get('role', 'user'),
        'content': request.get('content', ''),
        'timestamp': datetime.now()
    }
    
    conversation['messages'].append(message)
    conversation['updated_at'] = datetime.now()
    
    # Auto-generate title if this is the first user message
    if len(conversation['messages']) == 1 and message['role'] == 'user':
        # Simple title generation from first message
        title = message['content'][:50] + "..." if len(message['content']) > 50 else message['content']
        conversation['title'] = title
    
    save_conversations(conversations)
    
    return {"message": message}

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    conversations = load_conversations()
    conversations = [conv for conv in conversations if conv['id'] != conversation_id]
    save_conversations(conversations)
    
    return {"success": True}