from typing import Dict, Any, Optional, List
import os
import tempfile
import mimetypes
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FileProcessingService:
    def __init__(self, chromadb_service=None):
        """Initialize file processing service"""
        self.chromadb_service = chromadb_service
        self.supported_types = {
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.py': 'text/plain',
            '.js': 'text/plain',
            '.ts': 'text/plain',
            '.html': 'text/html',
            '.css': 'text/css',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.csv': 'text/csv'
        }
        
        # Create upload directory
        self.upload_dir = os.path.join(os.getcwd(), "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def get_file_type(self, filename: str) -> str:
        """Determine file type from filename"""
        file_ext = Path(filename).suffix.lower()
        return self.supported_types.get(file_ext, 'unknown')
    
    async def process_uploaded_file(self, file_content: bytes, filename: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process uploaded file and extract content"""
        try:
            file_type = self.get_file_type(filename)
            
            if file_type == 'unknown':
                return {
                    "success": False,
                    "error": f"Unsupported file type: {Path(filename).suffix}",
                    "supported_types": list(self.supported_types.keys())
                }
            
            # Save file temporarily
            file_path = os.path.join(self.upload_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Extract text content
            extracted_content = await self._extract_text_content(file_path, file_type)
            
            if not extracted_content:
                return {
                    "success": False,
                    "error": "Could not extract text content from file"
                }
            
            # Prepare metadata
            file_metadata = {
                "filename": filename,
                "file_type": file_type,
                "size_bytes": len(file_content),
                "source": "file_upload",
                **(metadata or {})
            }
            
            # Store in ChromaDB if available
            document_id = None
            if self.chromadb_service and self.chromadb_service.is_available():
                try:
                    document_id = self.chromadb_service.add_document(extracted_content, file_metadata)
                except Exception as e:
                    logger.warning(f"Could not store file in ChromaDB: {e}")
            
            # Clean up temporary file
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not remove temporary file: {e}")
            
            return {
                "success": True,
                "filename": filename,
                "file_type": file_type,
                "content": extracted_content,
                "metadata": file_metadata,
                "document_id": document_id,
                "stored_in_knowledge_base": document_id is not None,
                "content_length": len(extracted_content)
            }
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    async def _extract_text_content(self, file_path: str, file_type: str) -> Optional[str]:
        """Extract text content from file based on type"""
        try:
            if file_type in ['text/plain', 'text/markdown', 'text/html', 'text/css', 'application/json', 'application/xml', 'text/csv']:
                # For text-based files, read directly
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            
            # For other types, we'll need specialized parsers
            # This is a placeholder - real implementation would use libraries like:
            # - PyPDF2 for PDF files
            # - python-docx for DOCX files
            # - openpyxl for Excel files
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting content from {file_path}: {e}")
            return None
    
    def get_supported_file_types(self) -> List[str]:
        """Get list of supported file types"""
        return list(self.supported_types.keys())
    
    def validate_file(self, filename: str, max_size_mb: int = 10) -> Dict[str, Any]:
        """Validate file before processing"""
        file_ext = Path(filename).suffix.lower()
        
        if file_ext not in self.supported_types:
            return {
                "valid": False,
                "error": f"Unsupported file type: {file_ext}",
                "supported_types": list(self.supported_types.keys())
            }
        
        return {
            "valid": True,
            "file_type": self.supported_types[file_ext],
            "max_size_mb": max_size_mb
        }
    
    async def search_uploaded_files(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search through uploaded files using ChromaDB"""
        if not self.chromadb_service or not self.chromadb_service.is_available():
            return []
        
        try:
            # Search for documents with file metadata
            results = self.chromadb_service.search_documents(query, limit)
            
            # Filter for file uploads
            file_results = []
            for result in results:
                metadata = result.get('metadata', {})
                if metadata.get('source') == 'file_upload':
                    file_results.append({
                        'id': result['id'],
                        'filename': metadata.get('filename', 'Unknown'),
                        'file_type': metadata.get('file_type', 'Unknown'),
                        'content_snippet': result['content'][:300] + '...' if len(result['content']) > 300 else result['content'],
                        'relevance': 1 - result['distance'],
                        'metadata': metadata
                    })
            
            return file_results
            
        except Exception as e:
            logger.error(f"Error searching uploaded files: {e}")
            return []
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get file processing service status"""
        return {
            "available": True,
            "supported_file_types": list(self.supported_types.keys()),
            "upload_directory": self.upload_dir,
            "chromadb_integration": self.chromadb_service is not None and self.chromadb_service.is_available(),
            "features": {
                "text_extraction": True,
                "pdf_processing": False,  # Would be True with PyPDF2
                "docx_processing": False,  # Would be True with python-docx
                "knowledge_base_storage": self.chromadb_service is not None and self.chromadb_service.is_available()
            }
        }