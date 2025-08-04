import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import uuid
import logging
import os

logger = logging.getLogger(__name__)

class ChromaDBService:
    def __init__(self, host: str = "localhost", port: int = 8001):
        """Initialize ChromaDB service"""
        self.client = None
        self.collection = None
        self.conversations_collection = None
        
        # Try HTTP client first, then fall back to embedded mode
        try:
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=Settings(allow_reset=True)
            )
            
            # Test the connection
            self.client.heartbeat()
            logger.info(f"Connected to ChromaDB HTTP server at {host}:{port}")
            
        except Exception as e:
            logger.warning(f"Could not connect to ChromaDB HTTP server: {e}")
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
                
            except Exception as embedded_error:
                logger.error(f"Could not initialize embedded ChromaDB: {embedded_error}")
                self.client = None
                
        # Initialize collections if client is available
        if self.client:
            try:
                # Get or create collection for knowledge base
                self.collection = self.client.get_or_create_collection(
                    name="evolveui_knowledge",
                    metadata={"description": "EvolveUI knowledge base"}
                )
                
                # Get or create collection for conversations
                self.conversations_collection = self.client.get_or_create_collection(
                    name="evolveui_conversations",
                    metadata={"description": "EvolveUI conversation history"}
                )
                
                logger.info("ChromaDB collections initialized successfully")
                
            except Exception as e:
                logger.error(f"Error initializing ChromaDB collections: {e}")
                self.client = None
                self.collection = None
                self.conversations_collection = None

    def is_available(self) -> bool:
        """Check if ChromaDB is available"""
        return self.client is not None and self.collection is not None

    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Add a document to the knowledge base"""
        if not self.is_available():
            raise Exception("ChromaDB not available")
        
        doc_id = str(uuid.uuid4())
        
        try:
            self.collection.add(
                documents=[content],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )
            return doc_id
        except Exception as e:
            logger.error(f"Error adding document to ChromaDB: {e}")
            raise

    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if not self.is_available():
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            documents = []
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'id': results['ids'][0][i],
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'][0] else {},
                    'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else 0
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            return []

    def add_conversation_context(self, conversation_id: str, messages: List[Dict[str, Any]]):
        """Add conversation context to the knowledge base"""
        if not self.is_available() or not self.conversations_collection:
            return
        
        try:
            # Create a summary of the conversation
            conversation_text = f"Conversation {conversation_id}:\n"
            for msg in messages:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                conversation_text += f"{role}: {content}\n"
            
            metadata = {
                'type': 'conversation',
                'conversation_id': conversation_id,
                'message_count': len(messages),
                'timestamp': messages[-1].get('timestamp') if messages else ''
            }
            
            # Add to conversations collection
            doc_id = str(uuid.uuid4())
            self.conversations_collection.add(
                documents=[conversation_text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Added conversation {conversation_id} to ChromaDB")
            
        except Exception as e:
            logger.error(f"Error adding conversation context: {e}")

    def get_relevant_context(self, query: str, limit: int = 3) -> List[str]:
        """Get relevant context for a query"""
        documents = self.search_documents(query, limit)
        return [doc['content'] for doc in documents if doc['distance'] < 0.8]  # Filter by similarity threshold
    
    def search_conversations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search conversation history"""
        if not self.is_available() or not self.conversations_collection:
            return []
        
        try:
            results = self.conversations_collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            conversations = []
            for i, doc in enumerate(results['documents'][0]):
                conversations.append({
                    'id': results['ids'][0][i],
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'][0] else {},
                    'distance': results['distances'][0][i] if results['distances'] and results['distances'][0] else 0
                })
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error searching conversations: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about ChromaDB collections"""
        if not self.is_available():
            return {"available": False}
        
        try:
            stats = {
                "available": True,
                "knowledge_documents": self.collection.count(),
                "conversations": self.conversations_collection.count() if self.conversations_collection else 0,
                "collections": [
                    {"name": "evolveui_knowledge", "type": "knowledge_base"},
                    {"name": "evolveui_conversations", "type": "conversation_history"}
                ]
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"available": False, "error": str(e)}