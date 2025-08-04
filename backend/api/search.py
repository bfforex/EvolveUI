from fastapi import APIRouter, HTTPException
import requests
from typing import Optional
from services.chromadb_service import ChromaDBService

router = APIRouter()

# Initialize ChromaDB service
chromadb_service = ChromaDBService()

@router.get("/web")
async def search_web(q: str, limit: Optional[int] = 5):
    """Search the web using DuckDuckGo"""
    try:
        # For now, return a mock response since we don't have DuckDuckGo API
        # In a real implementation, you would integrate with a search API
        return {
            "query": q,
            "results": [
                {
                    "title": f"Search result for: {q}",
                    "url": "https://example.com",
                    "snippet": f"This is a mock search result for the query: {q}. In a real implementation, this would be replaced with actual web search results."
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get("/knowledge")
async def search_knowledge(q: str, limit: Optional[int] = 5):
    """Search the knowledge database using ChromaDB"""
    try:
        if chromadb_service.is_available():
            results = chromadb_service.search_documents(q, limit)
            return {
                "query": q,
                "results": results,
                "chromadb_available": True
            }
        else:
            return {
                "query": q,
                "results": [
                    {
                        "content": f"ChromaDB is not available. Mock knowledge result for: {q}",
                        "metadata": {
                            "source": "mock",
                            "confidence": 0.85
                        }
                    }
                ],
                "chromadb_available": False
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge search error: {str(e)}")

@router.post("/knowledge/add")
async def add_knowledge(request: dict):
    """Add content to the knowledge database"""
    try:
        content = request.get('content', '')
        metadata = request.get('metadata', {})
        
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        if chromadb_service.is_available():
            doc_id = chromadb_service.add_document(content, metadata)
            return {
                "success": True,
                "document_id": doc_id,
                "chromadb_available": True
            }
        else:
            return {
                "success": False,
                "error": "ChromaDB not available",
                "chromadb_available": False
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding knowledge: {str(e)}")

@router.get("/status")
async def get_search_status():
    """Get status of search services"""
    return {
        "chromadb_available": chromadb_service.is_available(),
        "web_search_available": False,  # Not implemented yet
        "knowledge_documents": chromadb_service.collection.count() if chromadb_service.is_available() else 0
    }