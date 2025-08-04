import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)

class ChromaDBService:
    def __init__(self, host: str = "localhost", port: int = 8001):
        """Initialize ChromaDB service"""
        try:
            # Create ChromaDB client
            self.client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=Settings(allow_reset=True)
            )
            
            # Get or create collection for conversations
            self.collection = self.client.get_or_create_collection(
                name="evolveui_knowledge",
                metadata={"description": "EvolveUI knowledge base"}
            )
            
            logger.info(f"Connected to ChromaDB at {host}:{port}")
            
        except Exception as e:
            logger.warning(f"Could not connect to ChromaDB: {e}")
            self.client = None
            self.collection = None

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
        if not self.is_available():
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
            
            self.add_document(conversation_text, metadata)
            
        except Exception as e:
            logger.error(f"Error adding conversation context: {e}")

    def get_relevant_context(self, query: str, limit: int = 3) -> List[str]:
        """Get relevant context for a query"""
        documents = self.search_documents(query, limit)
        return [doc['content'] for doc in documents if doc['distance'] < 0.8]  # Filter by similarity threshold