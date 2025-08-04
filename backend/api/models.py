from fastapi import APIRouter, HTTPException
import requests
import json

router = APIRouter()

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
    """Send chat request to Ollama model"""
    try:
        model = request.get("model", "llama3.2")
        messages = request.get("messages", [])
        
        ollama_request = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/chat",
            json=ollama_request
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Ollama request failed")
            
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat request: {str(e)}")