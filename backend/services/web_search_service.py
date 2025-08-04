from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        """Initialize web search service"""
        self.ddgs = DDGS()
        self.executor = ThreadPoolExecutor(max_workers=3)
        
    def _clean_search_query(self, query: str) -> str:
        """Clean and optimize search query"""
        # Remove special characters and clean up
        query = re.sub(r'[^\w\s\-\+]', ' ', query)
        # Remove extra whitespace
        query = ' '.join(query.split())
        return query.strip()
    
    def _determine_search_intent(self, message: str) -> Dict[str, Any]:
        """Determine if a message would benefit from web search"""
        
        # Keywords that suggest web search would be helpful
        search_indicators = [
            'current', 'latest', 'recent', 'news', 'today', 'now',
            'what is', 'who is', 'where is', 'when did', 'how to',
            'price of', 'cost of', 'weather', 'stock price',
            'definition of', 'meaning of', 'search for', 'find',
            'lookup', 'google', 'research'
        ]
        
        # Topics that often need current information
        current_topics = [
            'weather', 'news', 'stock', 'cryptocurrency', 'bitcoin',
            'election', 'sports', 'market', 'breaking', 'update'
        ]
        
        message_lower = message.lower()
        
        # Check for search indicators
        search_score = 0
        for indicator in search_indicators:
            if indicator in message_lower:
                search_score += 1
        
        # Check for current topics
        for topic in current_topics:
            if topic in message_lower:
                search_score += 2
        
        # Question patterns
        question_patterns = [
            r'\bwhat\s+is\b',
            r'\bwho\s+is\b',
            r'\bwhere\s+is\b',
            r'\bwhen\s+did\b',
            r'\bhow\s+to\b',
            r'\bhow\s+much\b',
            r'\bwhy\s+is\b'
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, message_lower):
                search_score += 1
        
        should_search = search_score >= 1
        
        return {
            "should_search": should_search,
            "confidence": min(search_score / 3.0, 1.0),
            "indicators_found": search_score,
            "suggested_query": self._clean_search_query(message) if should_search else None
        }
    
    async def search_web(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search the web using DuckDuckGo"""
        try:
            cleaned_query = self._clean_search_query(query)
            
            # Run search in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                self.executor,
                self._perform_search,
                cleaned_query,
                max_results
            )
            
            return {
                "query": query,
                "cleaned_query": cleaned_query,
                "results": results,
                "success": True,
                "source": "duckduckgo"
            }
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return {
                "query": query,
                "results": [],
                "success": False,
                "error": str(e),
                "source": "duckduckgo"
            }
    
    def _perform_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform the actual search (blocking operation)"""
        try:
            # Search for web results
            web_results = list(self.ddgs.text(
                keywords=query,
                max_results=max_results,
                region='wt-wt',
                safesearch='moderate'
            ))
            
            formatted_results = []
            for result in web_results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                    "source": "web"
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search execution error: {e}")
            return []
    
    async def search_news(self, query: str, max_results: int = 3) -> Dict[str, Any]:
        """Search for news using DuckDuckGo"""
        try:
            cleaned_query = self._clean_search_query(query)
            
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                self.executor,
                self._perform_news_search,
                cleaned_query,
                max_results
            )
            
            return {
                "query": query,
                "results": results,
                "success": True,
                "source": "duckduckgo_news"
            }
            
        except Exception as e:
            logger.error(f"News search error: {e}")
            return {
                "query": query,
                "results": [],
                "success": False,
                "error": str(e),
                "source": "duckduckgo_news"
            }
    
    def _perform_news_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform news search (blocking operation)"""
        try:
            news_results = list(self.ddgs.news(
                keywords=query,
                max_results=max_results,
                region='wt-wt',
                safesearch='moderate'
            ))
            
            formatted_results = []
            for result in news_results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("body", ""),
                    "date": result.get("date", ""),
                    "source": "news"
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"News search execution error: {e}")
            return []
    
    async def auto_search(self, user_message: str) -> Optional[Dict[str, Any]]:
        """Automatically determine if search is needed and perform it"""
        intent = self._determine_search_intent(user_message)
        
        if not intent["should_search"]:
            return None
        
        # Perform web search
        search_results = await self.search_web(intent["suggested_query"], max_results=3)
        
        # Add intent information
        search_results["search_intent"] = intent
        
        return search_results
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get web search service status"""
        try:
            # Test a simple search to verify service availability
            test_results = list(self.ddgs.text(
                keywords="test",
                max_results=1,
                region='wt-wt'
            ))
            
            return {
                "available": True,
                "service": "duckduckgo",
                "features": ["web_search", "news_search", "auto_search"]
            }
            
        except Exception as e:
            return {
                "available": False,
                "service": "duckduckgo",
                "error": str(e)
            }