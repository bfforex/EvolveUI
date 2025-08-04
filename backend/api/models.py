from fastapi import APIRouter, HTTPException
import requests
import json
from services.chromadb_service import ChromaDBService

router = APIRouter()

# Initialize ChromaDB service
chromadb_service = ChromaDBService()

@router.get("/")
async def get_ollama_models():
    """Get list of available Ollama models"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            return {"models": models.get("models", [])}
        else:
            return {"models": [], "error": "Ollama service not available"}
    except requests.exceptions.ConnectionError:
        return {"models": [], "error": "Cannot connect to Ollama service"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")

@router.post("/chat")
async def chat_with_model(request: dict):
    """Send chat request to Ollama model with optional RAG enhancement"""
    try:
        model = request.get("model", "llama3.2")
        messages = request.get("messages", [])
        use_rag = request.get("use_rag", False)
        
        # Get the latest user message for RAG context
        latest_message = messages[-1] if messages else None
        enhanced_messages = messages.copy()
        
        # Add RAG context if enabled and available
        if use_rag and latest_message and latest_message.get('role') == 'user':
            try:
                user_query = latest_message.get('content', '')
                relevant_context = chromadb_service.get_relevant_context(user_query, limit=3)
                
                if relevant_context:
                    context_text = "\n".join([f"Context: {ctx}" for ctx in relevant_context])
                    
                    # Modify the user message to include context
                    enhanced_content = f"""Based on the following context information:

{context_text}

User question: {user_query}

Please answer the user's question using the provided context when relevant, but also use your general knowledge if the context doesn't contain sufficient information."""
                    
                    enhanced_messages[-1] = {
                        **latest_message,
                        'content': enhanced_content
                    }
            except Exception as e:
                print(f"RAG enhancement failed: {e}")
                # Continue without RAG if it fails
        
        ollama_request = {
            "model": model,
            "messages": enhanced_messages,
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/chat",
            json=ollama_request
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Store conversation in knowledge base for future RAG
            if chromadb_service.is_available() and len(messages) >= 2:
                try:
                    chromadb_service.add_conversation_context("current", messages[-2:])
                except Exception as e:
                    print(f"Failed to store conversation context: {e}")
            
            return result
        else:
            raise HTTPException(status_code=response.status_code, detail="Ollama request failed")
            
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat request: {str(e)}")

@router.get("/rag/status")
async def get_rag_status():
    """Get RAG system status"""
    return {
        "chromadb_available": chromadb_service.is_available(),
        "knowledge_documents": chromadb_service.collection.count() if chromadb_service.is_available() else 0
    }