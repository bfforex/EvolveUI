from fastapi import APIRouter, HTTPException
import requests
import json
from services.chromadb_service import ChromaDBService
from services.rag_service import RAGService
from services.web_search_service import WebSearchService

router = APIRouter()

# Initialize services
chromadb_service = ChromaDBService()
rag_service = RAGService(chromadb_service)
web_search_service = WebSearchService()

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
    """Send chat request to Ollama model with optional RAG enhancement and auto-search"""
    try:
        model = request.get("model", "llama3.2")
        messages = request.get("messages", [])
        use_rag = request.get("use_rag", True)  # Enable RAG by default
        auto_search = request.get("auto_search", True)  # Enable auto-search by default
        conversation_id = request.get("conversation_id", "default")
        
        # Get the latest user message
        latest_message = messages[-1] if messages else None
        enhanced_messages = messages.copy()
        context_sources = []
        
        if latest_message and latest_message.get('role') == 'user':
            user_query = latest_message.get('content', '')
            
            # Check if auto web search should be performed
            search_results = None
            if auto_search:
                try:
                    search_results = await web_search_service.auto_search(user_query)
                    if search_results and search_results.get("search_performed"):
                        # Add search results to context
                        search_context = []
                        for result in search_results.get("results", [])[:3]:  # Top 3 results
                            search_context.append(f"Web result: {result.get('title', '')} - {result.get('snippet', '')}")
                            context_sources.append({
                                "type": "web_search",
                                "title": result.get('title', ''),
                                "url": result.get('url', ''),
                                "snippet": result.get('snippet', '')
                            })
                        
                        if search_context:
                            search_text = "\n".join(search_context)
                            user_query = f"""Web search results for reference:
{search_text}

User question: {user_query}"""
                            
                except Exception as e:
                    print(f"Auto search failed: {e}")
            
            # Apply RAG enhancement if enabled
            if use_rag and rag_service.chromadb_service.is_available():
                try:
                    rag_result = rag_service.augment_prompt(user_query, messages[:-1])  # Exclude current message
                    
                    if rag_result.get("rag_available") and rag_result.get("sources"):
                        enhanced_messages[-1] = {
                            **latest_message,
                            'content': rag_result["augmented_prompt"]
                        }
                        
                        # Add RAG sources to context sources
                        context_sources.extend(rag_result["sources"])
                        
                except Exception as e:
                    print(f"RAG enhancement failed: {e}")
                    # Continue without RAG if it fails
            elif user_query != latest_message.get('content', ''):
                # Update message with search context even if RAG is disabled
                enhanced_messages[-1] = {
                    **latest_message,
                    'content': user_query
                }
        
        # Send request to Ollama
        ollama_request = {
            "model": model,
            "messages": enhanced_messages,
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/chat",
            json=ollama_request,
            timeout=120  # 2 minute timeout for model response
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Add context information to response
            result["context_sources"] = context_sources
            result["rag_used"] = use_rag and len([s for s in context_sources if s["type"] in ["knowledge", "conversation"]]) > 0
            result["search_used"] = auto_search and len([s for s in context_sources if s["type"] == "web_search"]) > 0
            
            # Store conversation in knowledge base for future RAG
            if chromadb_service.is_available() and len(messages) >= 1:
                try:
                    # Add the assistant response to messages for storage
                    complete_messages = messages + [result.get("message", {})]
                    chromadb_service.add_conversation_context(conversation_id, complete_messages[-2:])
                except Exception as e:
                    print(f"Failed to store conversation context: {e}")
            
            return result
        else:
            raise HTTPException(status_code=response.status_code, detail="Ollama request failed")
            
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama service")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Ollama request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat request: {str(e)}")

@router.get("/rag/status")
async def get_rag_status():
    """Get RAG system status"""
    rag_status = rag_service.get_rag_status()
    search_status = web_search_service.get_service_status()
    
    return {
        "rag_service": rag_status,
        "web_search_service": search_status,
        "chromadb_available": chromadb_service.is_available(),
        "features": {
            "knowledge_retrieval": rag_status.get("available", False),
            "conversation_context": rag_status.get("available", False),
            "auto_web_search": search_status.get("available", False),
            "context_augmentation": rag_status.get("available", False)
        }
    }