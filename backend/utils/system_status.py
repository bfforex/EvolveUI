from typing import Dict, Any
import requests
from services.chromadb_service import ChromaDBService
import os
import json

async def get_system_status() -> Dict[str, Any]:
    """Get comprehensive system status"""
    status = {
        "overall": "healthy",
        "services": {},
        "features": {},
        "version": "1.0.0",
        "timestamp": None
    }
    
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            status["services"]["ollama"] = {
                "status": "available",
                "models_count": len(models),
                "models": [model.get("name", "") for model in models[:5]]  # First 5 models
            }
        else:
            status["services"]["ollama"] = {
                "status": "error",
                "error": f"HTTP {response.status_code}"
            }
    except Exception as e:
        status["services"]["ollama"] = {
            "status": "unavailable",
            "error": str(e)
        }
        status["overall"] = "degraded"
    
    # Check ChromaDB
    chromadb_service = ChromaDBService()
    if chromadb_service.is_available():
        try:
            doc_count = chromadb_service.collection.count()
            status["services"]["chromadb"] = {
                "status": "available",
                "documents_count": doc_count,
                "host": "localhost:8001"
            }
        except Exception as e:
            status["services"]["chromadb"] = {
                "status": "error",
                "error": str(e)
            }
    else:
        status["services"]["chromadb"] = {
            "status": "unavailable",
            "error": "Cannot connect to ChromaDB"
        }
        if status["overall"] == "healthy":
            status["overall"] = "degraded"
    
    # Check conversation storage
    try:
        conversations_file = "conversations.json"
        if os.path.exists(conversations_file):
            with open(conversations_file, 'r') as f:
                conversations = json.load(f)
                status["services"]["conversations"] = {
                    "status": "available",
                    "count": len(conversations),
                    "storage": "file_based"
                }
        else:
            status["services"]["conversations"] = {
                "status": "available",
                "count": 0,
                "storage": "file_based"
            }
    except Exception as e:
        status["services"]["conversations"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Feature availability
    status["features"] = {
        "chat": status["services"]["ollama"]["status"] == "available",
        "conversations": status["services"]["conversations"]["status"] == "available",
        "rag": status["services"]["chromadb"]["status"] == "available",
        "knowledge_base": status["services"]["chromadb"]["status"] == "available",
        "web_search": False,  # Not implemented
        "workpad": True,
        "settings": True
    }
    
    # Set timestamp
    from datetime import datetime
    status["timestamp"] = datetime.now().isoformat()
    
    return status