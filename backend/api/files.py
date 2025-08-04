from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional, List
import logging
from services.file_processor import FileProcessor
from services.chromadb_service import ChromaDBService
import json

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
file_processor = FileProcessor()
chromadb_service = ChromaDBService()

@router.get("/supported-types")
async def get_supported_file_types():
    """Get list of supported file types for upload"""
    supported_types = file_processor.get_supported_types()
    return {
        "supported_extensions": list(supported_types.keys()),
        "supported_mime_types": list(supported_types.values()),
        "details": supported_types
    }

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    add_to_knowledge: Optional[bool] = Form(False),
    knowledge_metadata: Optional[str] = Form(None)
):
    """Upload and process a file, optionally adding to knowledge base"""
    try:
        # Validate file type
        file_extension = None
        if file.filename:
            file_extension = '.' + file.filename.split('.')[-1].lower()
        
        supported_types = file_processor.get_supported_types()
        if file_extension not in supported_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}. Supported types: {list(supported_types.keys())}"
            )
        
        # Read file content
        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Save file temporarily
        file_path = file_processor.save_uploaded_file(file_content, file.filename)
        
        # Extract text content
        extraction_result = file_processor.extract_text_from_file(file_path, file.filename)
        
        # Add to knowledge base if requested
        knowledge_id = None
        if add_to_knowledge and extraction_result["success"] and extraction_result["content"]:
            try:
                # Parse metadata if provided
                metadata = {}
                if knowledge_metadata:
                    try:
                        metadata = json.loads(knowledge_metadata)
                    except json.JSONDecodeError:
                        logger.warning("Invalid metadata JSON provided")
                
                # Add file metadata
                metadata.update({
                    "type": "uploaded_file",
                    "filename": extraction_result["filename"],
                    "file_type": extraction_result["file_type"],
                    "mime_type": extraction_result["mime_type"],
                    "extraction_metadata": extraction_result["metadata"]
                })
                
                # Add to ChromaDB
                knowledge_id = chromadb_service.add_document(
                    extraction_result["content"],
                    metadata
                )
                
            except Exception as e:
                logger.error(f"Error adding file to knowledge base: {e}")
                # Don't fail the entire request if knowledge addition fails
        
        # Clean up temporary file
        file_processor.cleanup_file(file_path)
        
        return {
            "success": True,
            "file_info": {
                "filename": extraction_result["filename"],
                "file_type": extraction_result["file_type"],
                "mime_type": extraction_result["mime_type"],
                "size_bytes": len(file_content)
            },
            "extraction": {
                "success": extraction_result["success"],
                "content_length": len(extraction_result["content"]) if extraction_result["content"] else 0,
                "metadata": extraction_result["metadata"],
                "error": extraction_result.get("error")
            },
            "knowledge_base": {
                "added": knowledge_id is not None,
                "document_id": knowledge_id,
                "chromadb_available": chromadb_service.is_available()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

@router.post("/process-text")
async def process_text_content(
    content: str,
    filename: str = "text_input.txt",
    add_to_knowledge: bool = False,
    metadata: Optional[dict] = None
):
    """Process plain text content, optionally adding to knowledge base"""
    try:
        if not content.strip():
            raise HTTPException(status_code=400, detail="Empty content provided")
        
        # Create extraction result format
        extraction_result = {
            "filename": filename,
            "file_type": ".txt",
            "mime_type": "text/plain",
            "content": content,
            "metadata": {
                "size_bytes": len(content.encode('utf-8')),
                "line_count": content.count('\n') + 1,
                "char_count": len(content)
            },
            "success": True,
            "error": None
        }
        
        # Add to knowledge base if requested
        knowledge_id = None
        if add_to_knowledge:
            try:
                knowledge_metadata = metadata or {}
                knowledge_metadata.update({
                    "type": "text_input",
                    "filename": filename,
                    "file_type": ".txt",
                    "mime_type": "text/plain",
                    "extraction_metadata": extraction_result["metadata"]
                })
                
                knowledge_id = chromadb_service.add_document(content, knowledge_metadata)
                
            except Exception as e:
                logger.error(f"Error adding text to knowledge base: {e}")
        
        return {
            "success": True,
            "extraction": extraction_result,
            "knowledge_base": {
                "added": knowledge_id is not None,
                "document_id": knowledge_id,
                "chromadb_available": chromadb_service.is_available()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Text processing error: {str(e)}")

@router.get("/knowledge/documents")
async def list_knowledge_documents(limit: int = 20, offset: int = 0):
    """List documents in the knowledge base"""
    try:
        if not chromadb_service.is_available():
            return {
                "documents": [],
                "total": 0,
                "chromadb_available": False
            }
        
        # Get all documents (ChromaDB doesn't have built-in pagination)
        # This is a simple implementation - for production, you'd want proper pagination
        all_results = chromadb_service.search_documents("", limit=limit + offset)
        
        # Simple pagination simulation
        paginated_results = all_results[offset:offset + limit] if len(all_results) > offset else []
        
        return {
            "documents": paginated_results,
            "total": len(all_results),
            "limit": limit,
            "offset": offset,
            "chromadb_available": True
        }
        
    except Exception as e:
        logger.error(f"Error listing knowledge documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@router.delete("/knowledge/documents/{document_id}")
async def delete_knowledge_document(document_id: str):
    """Delete a document from the knowledge base"""
    try:
        if not chromadb_service.is_available():
            raise HTTPException(status_code=503, detail="ChromaDB not available")
        
        # ChromaDB delete implementation would go here
        # Note: The current ChromaDBService doesn't have a delete method
        # You would need to add this to the service
        
        return {
            "success": True,
            "message": f"Document {document_id} deletion requested",
            "note": "Delete functionality needs to be implemented in ChromaDBService"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")