from fastapi import APIRouter, HTTPException
import requests
from typing import Optional, List, Dict, Any
from services.chromadb_service import ChromaDBService
import logging

# Try to import duckduckgo search, fallback if not available
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    logging.warning("DuckDuckGo search not available. Install duckduckgo-search for web search functionality.")

router = APIRouter()

# Initialize ChromaDB service
chromadb_service = ChromaDBService()

@router.get("/web")
async def search_web(q: str, limit: Optional[int] = 5, engine: Optional[str] = "duckduckgo"):
    """Search the web using specified search engine"""
    try:
        if engine == "duckduckgo" and DDGS_AVAILABLE:
            return await _search_duckduckgo(q, limit)
        else:
            # Fallback to mock response
            return {
                "query": q,
                "results": [
                    {
                        "title": f"Search result for: {q}",
                        "url": "https://example.com",
                        "snippet": f"Mock search result for: {q}. Real web search requires proper search engine integration.",
                        "source": "mock"
                    }
                ],
                "engine": "mock",
                "available_engines": ["duckduckgo"] if DDGS_AVAILABLE else []
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

async def _search_duckduckgo(query: str, limit: int) -> Dict[str, Any]:
    """Search using DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            results = []
            search_results = ddgs.text(query, max_results=limit)
            
            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                    "source": "duckduckgo"
                })
            
            return {
                "query": query,
                "results": results,
                "engine": "duckduckgo",
                "total_results": len(results)
            }
    except Exception as e:
        logging.error(f"DuckDuckGo search error: {e}")
        # Fallback to mock
        return {
            "query": query,
            "results": [
                {
                    "title": f"Search failed for: {query}",
                    "url": "",
                    "snippet": f"DuckDuckGo search encountered an error: {str(e)}",
                    "source": "error"
                }
            ],
            "engine": "duckduckgo",
            "error": str(e)
        }

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