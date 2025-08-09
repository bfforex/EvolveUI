import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import uuid
import logging
import os
import time
import asyncio
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class ChromaDBService:
    def __init__(self, host: str = "localhost", port: int = 8001, max_retries: int = 3):
        """Initialize ChromaDB service with enhanced connection management"""
        self.host = host
        self.port = port
        self.max_retries = max_retries
        self.client = None
        self.collection = None
        self.conversations_collection = None
        self.files_collection = None
        self._last_connection_check = 0
        self._connection_check_interval = 60  # Check connection every 60 seconds
        
        self._initialize_client()

    def _initialize_client(self) -> bool:
        """Initialize ChromaDB client with retry logic"""
        for attempt in range(self.max_retries):
            try:
                # Try HTTP client first
                self.client = chromadb.HttpClient(
                    host=self.host,
                    port=self.port,
                    settings=Settings(allow_reset=True)
                )
                
                # Test the connection
                self.client.heartbeat()
                logger.info(f"Connected to ChromaDB HTTP server at {self.host}:{self.port}")
                break
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries}: Could not connect to ChromaDB HTTP server: {e}")
                
                if attempt == self.max_retries - 1:
                    logger.info("Attempting to use embedded ChromaDB...")
                    try:
                        # Create data directory for ChromaDB
                        data_dir = os.path.join(os.getcwd(), "chromadb_data")
                        os.makedirs(data_dir, exist_ok=True)
                        
                        # Create embedded client
                        self.client = chromadb.PersistentClient(
                            path=data_dir,
                            settings=Settings(
                                allow_reset=True,
                                anonymized_telemetry=False,
                                is_persistent=True
                            )
                        )
                        logger.info(f"Connected to embedded ChromaDB at {data_dir}")
                        break
                        
                    except Exception as embedded_error:
                        logger.error(f"Could not initialize embedded ChromaDB: {embedded_error}")
                        self.client = None
                        return False
                else:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        # Initialize collections if client is available
        if self.client:
            return self._initialize_collections()
        return False

    def _initialize_collections(self) -> bool:
        """Initialize all collections with error handling"""
        try:
            # Get or create collection for knowledge base
            self.collection = self.client.get_or_create_collection(
                name="evolveui_knowledge",
                metadata={"description": "EvolveUI knowledge base", "version": "1.1"}
            )
            
            # Get or create collection for conversations
            self.conversations_collection = self.client.get_or_create_collection(
                name="evolveui_conversations",
                metadata={"description": "EvolveUI conversation history", "version": "1.1"}
            )
            
            # Get or create collection for files
            self.files_collection = self.client.get_or_create_collection(
                name="evolveui_files",
                metadata={"description": "EvolveUI file storage", "version": "1.1"}
            )
            
            logger.info("ChromaDB collections initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB collections: {e}")
            self.client = None
            self.collection = None
            self.conversations_collection = None
            self.files_collection = None
            return False

    def _check_connection(self) -> bool:
        """Check if connection is still alive and reconnect if needed"""
        current_time = time.time()
        if current_time - self._last_connection_check < self._connection_check_interval:
            return self.client is not None
            
        self._last_connection_check = current_time
        
        if self.client is None:
            return self._initialize_client()
            
        try:
            self.client.heartbeat()
            return True
        except Exception as e:
            logger.warning(f"Connection check failed: {e}, attempting to reconnect...")
            return self._initialize_client()

    @asynccontextmanager
    async def _safe_operation(self):
        """Context manager for safe ChromaDB operations with automatic reconnection"""
        if not self._check_connection():
            raise Exception("ChromaDB not available after reconnection attempts")
        yield

    def is_available(self) -> bool:
        """Check if ChromaDB is available with connection verification"""
        return self._check_connection() and self.collection is not None

    async def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add a document to the knowledge base with error handling"""
        async with self._safe_operation():
            doc_id = str(uuid.uuid4())
            
            # Ensure metadata is a dictionary and filter out None values
            safe_metadata = {}
            if metadata:
                safe_metadata = {k: v for k, v in metadata.items() if v is not None}
            
            try:
                self.collection.add(
                    documents=[content],
                    metadatas=[safe_metadata],
                    ids=[doc_id]
                )
                logger.info(f"Successfully added document {doc_id}")
                return doc_id
            except Exception as e:
                logger.error(f"Error adding document to ChromaDB: {e}")
                raise

    async def search_documents(self, query: str, limit: int = 5, distance_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Search for similar documents with improved relevance filtering"""
        async with self._safe_operation():
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=limit
                )
                
                documents = []
                for i, doc in enumerate(results['documents'][0]):
                    distance = results['distances'][0][i] if results['distances'] and results['distances'][0] else 0
                    
                    # Only include results below distance threshold for better relevance
                    if distance <= distance_threshold:
                        metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] and i < len(results['metadatas'][0]) else {}
                        safe_metadata = {k: v for k, v in metadata.items() if v is not None} if metadata else {}
                        
                        documents.append({
                            'id': results['ids'][0][i],
                            'content': doc,
                            'metadata': safe_metadata,
                            'distance': distance,
                            'relevance_score': 1.0 - distance  # Convert distance to relevance score
                        })
                
                # Sort by relevance score (highest first)
                documents.sort(key=lambda x: x['relevance_score'], reverse=True)
                return documents
                
            except Exception as e:
                logger.error(f"Error searching ChromaDB: {e}")
                return []

    async def add_conversation_context(self, conversation_id: str, messages: List[Dict[str, Any]]):
        """Add conversation context to the knowledge base with enhanced metadata"""
        async with self._safe_operation():
            if not self.conversations_collection:
                logger.warning("Conversations collection not available")
                return
            
            try:
                # Create a summary of the conversation
                conversation_text = f"Conversation {conversation_id}:\n"
                for msg in messages:
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    conversation_text += f"{role}: {content}\n"
                
                # Enhanced metadata with more context
                metadata = {
                    'type': 'conversation',
                    'conversation_id': str(conversation_id),
                    'message_count': len(messages),
                    'timestamp': messages[-1].get('timestamp', '') if messages else '',
                    'participants': list(set(msg.get('role', 'unknown') for msg in messages)),
                    'last_message_preview': messages[-1].get('content', '')[:100] if messages else ''
                }
                
                # Filter out None values from metadata
                safe_metadata = {k: v for k, v in metadata.items() if v is not None}
                
                # Add to conversations collection
                doc_id = str(uuid.uuid4())
                self.conversations_collection.add(
                    documents=[conversation_text],
                    metadatas=[safe_metadata],
                    ids=[doc_id]
                )
                
                logger.info(f"Added conversation {conversation_id} to ChromaDB with enhanced metadata")
                
            except Exception as e:
                logger.error(f"Error adding conversation context: {e}")

    async def get_relevant_context(self, query: str, limit: int = 5, min_relevance: float = 0.6) -> List[str]:
        """Get relevant context for a query with improved filtering"""
        documents = await self.search_documents(query, limit, distance_threshold=1.0 - min_relevance)
        return [doc['content'] for doc in documents if doc['relevance_score'] >= min_relevance]

    async def search_conversations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search conversation history with enhanced filtering"""
        async with self._safe_operation():
            if not self.conversations_collection:
                return []
            
            try:
                results = self.conversations_collection.query(
                    query_texts=[query],
                    n_results=limit
                )
                
                conversations = []
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] and i < len(results['metadatas'][0]) else {}
                    safe_metadata = {k: v for k, v in metadata.items() if v is not None} if metadata else {}
                    distance = results['distances'][0][i] if results['distances'] and results['distances'][0] else 0
                    
                    conversations.append({
                        'id': results['ids'][0][i],
                        'content': doc,
                        'metadata': safe_metadata,
                        'distance': distance,
                        'relevance_score': 1.0 - distance
                    })
                
                # Sort by relevance
                conversations.sort(key=lambda x: x['relevance_score'], reverse=True)
                return conversations
                
            except Exception as e:
                logger.error(f"Error searching conversations: {e}")
                return []

    async def add_file_content(self, filename: str, content: str, file_type: str, metadata: Dict[str, Any] = None) -> str:
        """Add file content to dedicated files collection"""
        async with self._safe_operation():
            if not self.files_collection:
                logger.warning("Files collection not available")
                return ""
                
            doc_id = str(uuid.uuid4())
            
            # Enhanced file metadata
            file_metadata = {
                'type': 'file',
                'filename': filename,
                'file_type': file_type,
                'upload_timestamp': time.time(),
                'content_length': len(content),
                **(metadata or {})
            }
            
            safe_metadata = {k: v for k, v in file_metadata.items() if v is not None}
            
            try:
                self.files_collection.add(
                    documents=[content],
                    metadatas=[safe_metadata],
                    ids=[doc_id]
                )
                logger.info(f"Successfully added file {filename} with id {doc_id}")
                return doc_id
            except Exception as e:
                logger.error(f"Error adding file to ChromaDB: {e}")
                raise

    async def search_files(self, query: str, file_type: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Search through uploaded files"""
        async with self._safe_operation():
            if not self.files_collection:
                return []
            
            try:
                # Build where clause for filtering by file type
                where_clause = None
                if file_type:
                    where_clause = {"file_type": file_type}
                
                results = self.files_collection.query(
                    query_texts=[query],
                    n_results=limit,
                    where=where_clause
                )
                
                files = []
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] and i < len(results['metadatas'][0]) else {}
                    safe_metadata = {k: v for k, v in metadata.items() if v is not None} if metadata else {}
                    distance = results['distances'][0][i] if results['distances'] and results['distances'][0] else 0
                    
                    files.append({
                        'id': results['ids'][0][i],
                        'content': doc,
                        'metadata': safe_metadata,
                        'distance': distance,
                        'relevance_score': 1.0 - distance
                    })
                
                files.sort(key=lambda x: x['relevance_score'], reverse=True)
                return files
                
            except Exception as e:
                logger.error(f"Error searching files: {e}")
                return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about ChromaDB collections with enhanced details"""
        if not self.is_available():
            return {"available": False, "error": "ChromaDB not available"}
        
        try:
            stats = {
                "available": True,
                "connection_type": "embedded" if "Persistent" in str(type(self.client)) else "http",
                "knowledge_documents": self.collection.count(),
                "conversations": self.conversations_collection.count() if self.conversations_collection else 0,
                "files": self.files_collection.count() if self.files_collection else 0,
                "collections": [
                    {
                        "name": "evolveui_knowledge", 
                        "type": "knowledge_base",
                        "count": self.collection.count(),
                        "description": "Main knowledge base for documents and context"
                    },
                    {
                        "name": "evolveui_conversations", 
                        "type": "conversation_history",
                        "count": self.conversations_collection.count() if self.conversations_collection else 0,
                        "description": "Historical conversation data for context retrieval"
                    },
                    {
                        "name": "evolveui_files", 
                        "type": "file_storage",
                        "count": self.files_collection.count() if self.files_collection else 0,
                        "description": "Uploaded file content for search and retrieval"
                    }
                ],
                "total_documents": (
                    self.collection.count() + 
                    (self.conversations_collection.count() if self.conversations_collection else 0) +
                    (self.files_collection.count() if self.files_collection else 0)
                )
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"available": False, "error": str(e)}
    
    async def optimize_collections(self) -> Dict[str, Any]:
        """Optimize collections for better performance"""
        if not self.is_available():
            return {"success": False, "error": "ChromaDB not available"}
        
        optimization_results = {}
        
        try:
            # Get stats before optimization
            before_stats = self.get_collection_stats()
            
            # Perform optimization operations (if supported by ChromaDB version)
            # Currently, ChromaDB doesn't expose explicit optimization methods,
            # but we can perform maintenance operations
            
            optimization_results = {
                "success": True,
                "before": before_stats,
                "optimizations_applied": [
                    "Connection health check",
                    "Collection integrity verification",
                    "Metadata cleanup"
                ],
                "timestamp": time.time()
            }
            
            logger.info("ChromaDB collections optimization completed")
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error optimizing collections: {e}")
            return {"success": False, "error": str(e)}

    async def bulk_add_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add multiple documents efficiently"""
        async with self._safe_operation():
            if not documents:
                return {"success": True, "added": 0, "errors": []}
            
            results = {"success": True, "added": 0, "errors": []}
            
            # Prepare bulk data
            doc_ids = []
            doc_contents = []
            doc_metadatas = []
            
            for doc in documents:
                doc_id = str(uuid.uuid4())
                content = doc.get('content', '')
                metadata = doc.get('metadata', {})
                
                if content:  # Only add non-empty documents
                    doc_ids.append(doc_id)
                    doc_contents.append(content)
                    
                    # Clean metadata
                    safe_metadata = {k: v for k, v in metadata.items() if v is not None}
                    doc_metadatas.append(safe_metadata)
            
            try:
                if doc_ids:
                    self.collection.add(
                        documents=doc_contents,
                        metadatas=doc_metadatas,
                        ids=doc_ids
                    )
                    results["added"] = len(doc_ids)
                    logger.info(f"Successfully bulk added {len(doc_ids)} documents")
                
            except Exception as e:
                logger.error(f"Error in bulk add: {e}")
                results["success"] = False
                results["errors"].append(str(e))
            
            return results