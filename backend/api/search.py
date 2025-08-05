from fastapi import APIRouter, HTTPException, UploadFile, File
import requests
from typing import Optional, List
from services.chromadb_service import ChromaDBService
from services.rag_service import RAGService
from services.web_search_service import WebSearchService
from services.file_processing_service import FileProcessingService
from services.code_execution_service import CodeExecutionService

router = APIRouter()

# Initialize services with default configuration
search_config = {
    'default_engine': 'duckduckgo',
    'engines': {
        'duckduckgo': {'enabled': True},
        'searxng': {'enabled': False, 'instance_url': 'https://searx.be'},
        'google': {'enabled': False, 'api_key': None, 'cx': None},
        'bing': {'enabled': False, 'api_key': None}
    }
}

chromadb_service = ChromaDBService()
rag_service = RAGService(chromadb_service)
web_search_service = WebSearchService(search_config)
file_processing_service = FileProcessingService(chromadb_service)
code_execution_service = CodeExecutionService()

@router.get("/web")
async def search_web(q: str, limit: Optional[int] = 5, engine: Optional[str] = None):
    """Search the web using the specified search engine"""
    try:
        result = await web_search_service.search_web(q, limit, engine)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get("/news")
async def search_news(q: str, limit: Optional[int] = 3, engine: Optional[str] = None):
    """Search for news using the specified search engine"""
    try:
        result = await web_search_service.search_news(q, limit, engine)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News search error: {str(e)}")

@router.get("/auto")
async def auto_search(q: str, engine: Optional[str] = None):
    """Automatically determine if search is needed and perform it"""
    try:
        result = await web_search_service.auto_search(q, engine)
        if result is None:
            return {
                "search_performed": False,
                "reason": "Query does not require web search",
                "query": q
            }
        return {
            "search_performed": True,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto search error: {str(e)}")

@router.get("/engines")
async def get_search_engines():
    """Get list of supported search engines and their configuration requirements"""
    try:
        engines = web_search_service.get_supported_engines()
        status = web_search_service.get_service_status()
        
        return {
            "engines": engines,
            "current_status": status,
            "default_engine": search_config.get('default_engine', 'duckduckgo')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting engines: {str(e)}")

@router.post("/config")
async def update_search_config(config: dict):
    """Update search engine configuration"""
    try:
        global search_config, web_search_service
        
        # Validate configuration
        if 'engines' in config:
            for engine_name, engine_config in config['engines'].items():
                if engine_name not in ['duckduckgo', 'searxng', 'google', 'bing']:
                    raise HTTPException(status_code=400, detail=f"Unsupported engine: {engine_name}")
        
        # Update configuration
        search_config.update(config)
        
        # Reinitialize web search service with new config
        web_search_service = WebSearchService(search_config)
        
        return {
            "success": True,
            "message": "Search configuration updated successfully",
            "config": search_config
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating config: {str(e)}")

@router.get("/config")
async def get_search_config():
    """Get current search engine configuration"""
    try:
        return {
            "config": search_config,
            "status": web_search_service.get_service_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting config: {str(e)}")

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
    chromadb_stats = chromadb_service.get_collection_stats()
    web_search_status = web_search_service.get_service_status()
    
    return {
        "chromadb_available": chromadb_service.is_available(),
        "web_search_available": web_search_status.get("available", False),
        "knowledge_documents": chromadb_stats.get("knowledge_documents", 0),
        "conversation_history": chromadb_stats.get("conversations", 0),
        "rag_service": rag_service.get_rag_status(),
        "services": {
            "chromadb": chromadb_stats,
            "web_search": web_search_status,
            "file_processing": file_processing_service.get_service_status(),
            "code_execution": code_execution_service.get_service_status()
        }
    }

# RAG endpoints
@router.post("/rag/augment")
async def augment_prompt(request: dict):
    """Augment a prompt with relevant context using RAG"""
    try:
        user_message = request.get('message', '')
        conversation_history = request.get('conversation_history', [])
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        result = rag_service.augment_prompt(user_message, conversation_history)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG augmentation error: {str(e)}")

# File processing endpoints
@router.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a file"""
    try:
        # Validate file
        validation = file_processing_service.validate_file(file.filename)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["error"])
        
        # Read file content
        file_content = await file.read()
        
        # Process file
        result = await file_processing_service.process_uploaded_file(
            file_content, 
            file.filename,
            metadata={"upload_timestamp": __import__("datetime").datetime.now().isoformat()}
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload error: {str(e)}")

@router.get("/files/search")
async def search_files(q: str, limit: Optional[int] = 5):
    """Search through uploaded files"""
    try:
        results = await file_processing_service.search_uploaded_files(q, limit)
        return {
            "query": q,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File search error: {str(e)}")

@router.get("/files/types")
async def get_supported_file_types():
    """Get list of supported file types"""
    return {
        "supported_types": file_processing_service.get_supported_file_types(),
        "service_status": file_processing_service.get_service_status()
    }

# Code execution endpoints
@router.post("/code/execute")
async def execute_code(request: dict):
    """Execute code safely"""
    try:
        code = request.get('code', '')
        language = request.get('language')
        timeout = request.get('timeout', 30)
        
        if not code:
            raise HTTPException(status_code=400, detail="Code is required")
        
        result = await code_execution_service.execute_code(code, language, timeout)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code execution error: {str(e)}")

@router.get("/code/detect")
async def detect_language(code: str):
    """Detect programming language from code"""
    try:
        language = code_execution_service.detect_language(code)
        lang_info = code_execution_service.get_language_info(language)
        
        return {
            "detected_language": language,
            "language_info": lang_info,
            "confidence": "high" if lang_info and lang_info.get("available") else "low"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Language detection error: {str(e)}")

@router.get("/code/languages")
async def get_supported_languages():
    """Get list of supported programming languages"""
    service_status = code_execution_service.get_service_status()
    return {
        "supported_languages": service_status["supported_languages"],
        "language_availability": service_status["language_availability"],
        "service_status": service_status
    }