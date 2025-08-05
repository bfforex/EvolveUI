from typing import List, Dict, Any, Optional
from services.chromadb_service import ChromaDBService
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, chromadb_service: ChromaDBService):
        """Initialize RAG service with ChromaDB"""
        self.chromadb_service = chromadb_service
        self.max_context_length = 4000  # Maximum characters for context
        
    def augment_prompt(self, user_message: str, conversation_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Augment user prompt with relevant context from knowledge base"""
        
        if not self.chromadb_service.is_available():
            return {
                "augmented_prompt": user_message,
                "context_used": [],
                "sources": [],
                "rag_available": False
            }
        
        try:
            # Search for relevant documents
            relevant_docs = self.chromadb_service.search_documents(user_message, limit=5)
            
            # Search conversation history for context
            conversation_context = []
            if conversation_history:
                conversation_context = self.chromadb_service.search_conversations(user_message, limit=3)
            
            # Filter and rank results by relevance (distance threshold)
            filtered_docs = [doc for doc in relevant_docs if doc['distance'] < 0.7]
            filtered_conversations = [conv for conv in conversation_context if conv['distance'] < 0.8]
            
            # Prepare context
            context_parts = []
            sources = []
            
            # Add document context
            for doc in filtered_docs[:3]:  # Limit to top 3 documents
                context_parts.append(f"Knowledge: {doc['content'][:500]}...")  # Truncate long content
                sources.append({
                    "type": "knowledge",
                    "id": doc['id'],
                    "metadata": doc['metadata'],
                    "relevance": 1 - doc['distance']
                })
            
            # Add conversation context
            for conv in filtered_conversations[:2]:  # Limit to top 2 conversations
                context_parts.append(f"Previous conversation: {conv['content'][:300]}...")
                sources.append({
                    "type": "conversation",
                    "id": conv['id'],
                    "metadata": conv['metadata'],
                    "relevance": 1 - conv['distance']
                })
            
            # Combine context
            context_text = "\n\n".join(context_parts)
            
            # Truncate if too long
            if len(context_text) > self.max_context_length:
                context_text = context_text[:self.max_context_length] + "..."
            
            # Create augmented prompt
            if context_text:
                augmented_prompt = f"""Context Information:
{context_text}

User Question: {user_message}

Please answer the user's question using the provided context when relevant. If the context doesn't contain relevant information, answer based on your general knowledge."""
            else:
                augmented_prompt = user_message
            
            return {
                "augmented_prompt": augmented_prompt,
                "context_used": context_parts,
                "sources": sources,
                "rag_available": True,
                "context_length": len(context_text)
            }
            
        except Exception as e:
            logger.error(f"Error in RAG augmentation: {e}")
            return {
                "augmented_prompt": user_message,
                "context_used": [],
                "sources": [],
                "rag_available": False,
                "error": str(e)
            }
    
    def evaluate_context_relevance(self, query: str, context: str) -> float:
        """Evaluate how relevant context is to the query (placeholder for more sophisticated scoring)"""
        # Simple keyword overlap scoring
        query_words = set(query.lower().split())
        context_words = set(context.lower().split())
        
        if len(query_words) == 0:
            return 0.0
        
        overlap = len(query_words.intersection(context_words))
        return overlap / len(query_words)
    
    def get_rag_status(self) -> Dict[str, Any]:
        """Get RAG service status"""
        if not self.chromadb_service.is_available():
            return {
                "available": False,
                "error": "ChromaDB not available"
            }
        
        try:
            stats = self.chromadb_service.get_collection_stats()
            return {
                "available": True,
                "knowledge_documents": stats.get("knowledge_documents", 0),
                "conversation_history": stats.get("conversations", 0),
                "max_context_length": self.max_context_length
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }