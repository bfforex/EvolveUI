from typing import List, Dict, Any, Optional
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re
import aiohttp
import time

try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        DDGS_AVAILABLE = True
    except ImportError:
        DDGS_AVAILABLE = False
        DDGS = None

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize web search service with configuration"""
        self.config = config or {}
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Initialize DuckDuckGo search if available
        self.ddgs = None
        if DDGS_AVAILABLE:
            try:
                self.ddgs = DDGS()
            except Exception as e:
                logger.error(f"Failed to initialize DDGS: {e}")
                
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 2.0  # Minimum seconds between requests per service
        
    def _get_search_config(self, engine: str = None) -> Dict[str, Any]:
        """Get configuration for a specific search engine"""
        engine = engine or self.config.get('default_engine', 'duckduckgo')
        
        default_configs = {
            'duckduckgo': {
                'enabled': True,
                'requires_api_key': False,
                'rate_limit': 2.0
            },
            'searxng': {
                'enabled': False,
                'requires_api_key': False,
                'instance_url': 'https://searx.be',
                'rate_limit': 1.0
            },
            'bfforexseaxng': {
                'enabled': True,
                'requires_api_key': False,
                'instance_url': 'http://localhost:8081',
                'rate_limit': 1.0,
                'description': 'Local bfforex SearXNG instance'
            },
            'google': {
                'enabled': False,
                'requires_api_key': True,
                'api_key': None,
                'cx': None,
                'rate_limit': 1.0
            },
            'bing': {
                'enabled': False,
                'requires_api_key': True,
                'api_key': None,
                'rate_limit': 1.0
            }
        }
        
        # Merge with user configuration
        engine_config = default_configs.get(engine, {})
        user_config = self.config.get('engines', {}).get(engine, {})
        engine_config.update(user_config)
        
        return engine_config
        
    async def _rate_limit_check(self, service: str):
        """Check and enforce rate limiting"""
        now = time.time()
        if service in self.last_request_time:
            time_since_last = now - self.last_request_time[service]
            if time_since_last < self.min_request_interval:
                wait_time = self.min_request_interval - time_since_last
                await asyncio.sleep(wait_time)
        self.last_request_time[service] = time.time()
        
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results and rank by relevance"""
        if not results:
            return results
        
        seen_urls = set()
        seen_content = set()
        deduplicated = []
        
        for result in results:
            url = result.get('url', '').lower().strip()
            content = result.get('snippet', '').lower().strip()
            title = result.get('title', '').lower().strip()
            
            # Create content hash for deduplication
            content_hash = hash(content + title)
            
            # Skip if we've seen this URL or very similar content
            if url not in seen_urls and content_hash not in seen_content:
                seen_urls.add(url)
                seen_content.add(content_hash)
                
                # Add quality score based on multiple factors
                quality_score = self._calculate_quality_score(result)
                result['quality_score'] = quality_score
                
                deduplicated.append(result)
        
        # Sort by quality score (highest first)
        deduplicated.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        return deduplicated
    
    def _calculate_quality_score(self, result: Dict[str, Any]) -> float:
        """Calculate quality score for search result ranking"""
        score = 0.5  # Base score
        
        title = result.get('title', '')
        snippet = result.get('snippet', '')
        url = result.get('url', '')
        
        # Title quality (length, informativeness)
        if title:
            if 10 <= len(title) <= 100:  # Good title length
                score += 0.1
            if not any(word in title.lower() for word in ['404', 'error', 'not found']):
                score += 0.1
        
        # Snippet quality (length, informativeness)
        if snippet:
            if 50 <= len(snippet) <= 300:  # Good snippet length
                score += 0.15
            if snippet.count('.') >= 1:  # Has sentences
                score += 0.05
        
        # URL quality
        if url:
            # Prefer https
            if url.startswith('https://'):
                score += 0.05
            
            # Prefer well-known domains
            trusted_domains = ['wikipedia.org', 'github.com', 'stackoverflow.com', 
                             'docs.python.org', 'developer.mozilla.org']
            if any(domain in url for domain in trusted_domains):
                score += 0.15
            
            # Penalize very long URLs (might be auto-generated)
            if len(url) > 150:
                score -= 0.05
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))
    
    def _clean_search_query(self, query: str) -> str:
        """Clean and optimize search query"""
        # Remove special characters and clean up
        query = re.sub(r'[^\w\s\-\+]', ' ', query)
        # Remove extra whitespace
        query = ' '.join(query.split())
        return query.strip()
    
    def _enhance_search_intent(self, message: str) -> Dict[str, Any]:
        """Enhanced search intent detection with improved accuracy"""
        
        # Explicit search commands
        explicit_search = [
            'search for', 'find information about', 'look up', 'google',
            'search', 'find', 'lookup', 'research'
        ]
        
        # Current/time-sensitive indicators
        current_indicators = [
            'current', 'latest', 'recent', 'today', 'now', 'this year',
            'update', 'news', 'breaking', 'live', 'real-time'
        ]
        
        # Question words that often need web search
        question_indicators = [
            'what is', 'who is', 'where is', 'when did', 'how to',
            'how much', 'why is', 'which', 'define', 'explain'
        ]
        
        # Topics that frequently need current information
        dynamic_topics = [
            'weather', 'stock price', 'cryptocurrency', 'bitcoin', 'news',
            'sports score', 'election', 'market', 'price', 'cost'
        ]
        
        message_lower = message.lower()
        search_score = 0
        indicators_found = []
        
        # Check for explicit search commands (high weight)
        for indicator in explicit_search:
            if indicator in message_lower:
                search_score += 3
                indicators_found.append(f"explicit: {indicator}")
        
        # Check for current/time-sensitive indicators (high weight)
        for indicator in current_indicators:
            if indicator in message_lower:
                search_score += 2
                indicators_found.append(f"current: {indicator}")
        
        # Check for question patterns (medium weight)
        for indicator in question_indicators:
            if indicator in message_lower:
                search_score += 1.5
                indicators_found.append(f"question: {indicator}")
        
        # Check for dynamic topics (medium weight)
        for topic in dynamic_topics:
            if topic in message_lower:
                search_score += 2
                indicators_found.append(f"dynamic: {topic}")
        
        # URL or domain mentions (low weight, might be referential)
        if re.search(r'https?://|www\.|\.com|\.org|\.net', message_lower):
            search_score += 0.5
            indicators_found.append("url_mention")
        
        # Length-based heuristics
        if len(message.split()) <= 5:  # Short queries often benefit from search
            search_score += 0.5
            indicators_found.append("short_query")
        
        # Calculate confidence based on score
        confidence = min(search_score / 5.0, 1.0)  # Normalize to 0-1
        should_search = search_score >= 2.0  # Threshold for search decision
        
        return {
            "should_search": should_search,
            "confidence": confidence,
            "search_score": search_score,
            "indicators_found": indicators_found,
            "suggested_query": self._clean_search_query(message) if should_search else None,
            "query_type": self._classify_query_type(message_lower)
        }
    
    def _classify_query_type(self, message: str) -> str:
        """Classify the type of query for better search strategy"""
        if any(word in message for word in ['weather', 'temperature', 'forecast']):
            return 'weather'
        elif any(word in message for word in ['news', 'breaking', 'report']):
            return 'news'
        elif any(word in message for word in ['price', 'cost', 'buy', 'sell', 'stock']):
            return 'price'
        elif any(word in message for word in ['how to', 'tutorial', 'guide', 'instructions']):
            return 'tutorial'
        elif any(word in message for word in ['define', 'meaning', 'what is', 'definition']):
            return 'definition'
        else:
            return 'general'
    
    async def search_web(self, query: str, max_results: int = 5, engine: str = None) -> Dict[str, Any]:
        """Search the web using the specified engine with enhanced result processing"""
        engine = engine or self.config.get('default_engine', 'duckduckgo')
        engine_config = self._get_search_config(engine)
        
        if not engine_config.get('enabled', False):
            return {
                "query": query,
                "results": [],
                "success": False,
                "error": f"Search engine {engine} is not enabled",
                "source": engine
            }
        
        try:
            await self._rate_limit_check(engine)
            cleaned_query = self._clean_search_query(query)
            
            # Get raw results from engine
            raw_results = None
            if engine == 'duckduckgo':
                raw_results = await self._search_duckduckgo(cleaned_query, max_results * 2)  # Get more for deduplication
            elif engine == 'searxng' or engine == 'bfforexseaxng':
                raw_results = await self._search_searxng(cleaned_query, max_results * 2, engine_config)
            elif engine == 'google':
                raw_results = await self._search_google(cleaned_query, max_results, engine_config)
            elif engine == 'bing':
                raw_results = await self._search_bing(cleaned_query, max_results, engine_config)
            else:
                return {
                    "query": query,
                    "results": [],
                    "success": False,
                    "error": f"Unsupported search engine: {engine}",
                    "source": engine
                }
            
            if raw_results and raw_results.get('success'):
                # Apply deduplication and ranking
                processed_results = self._deduplicate_results(raw_results['results'])
                
                # Limit to requested number after processing
                final_results = processed_results[:max_results]
                
                return {
                    "query": query,
                    "cleaned_query": cleaned_query,
                    "results": final_results,
                    "total_found": len(raw_results['results']),
                    "after_deduplication": len(processed_results),
                    "success": True,
                    "source": engine
                }
            else:
                return raw_results or {
                    "query": query,
                    "results": [],
                    "success": False,
                    "error": "No results from search engine",
                    "source": engine
                }
                
        except Exception as e:
            logger.error(f"Web search error for {engine}: {e}")
            return {
                "query": query,
                "results": [],
                "success": False,
                "error": str(e),
                "source": engine
            }

    async def _search_duckduckgo(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search using DuckDuckGo"""
        if not self.ddgs:
            raise Exception("DuckDuckGo search not available")
            
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            self.executor,
            self._perform_ddg_search,
            query,
            max_results
        )
        
        return {
            "query": query,
            "cleaned_query": query,
            "results": results,
            "success": True,
            "source": "duckduckgo"
        }

    async def _search_searxng(self, query: str, max_results: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Search using SearXNG instance"""
        instance_url = config.get('instance_url', 'https://searx.be')
        
        # Remove trailing slash
        instance_url = instance_url.rstrip('/')
        
        search_url = f"{instance_url}/search"
        params = {
            'q': query,
            'format': 'json',
            'pageno': 1,
            'categories': 'general'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for item in data.get('results', [])[:max_results]:
                        results.append({
                            "title": item.get('title', ''),
                            "url": item.get('url', ''),
                            "snippet": item.get('content', ''),
                            "source": "web"
                        })
                    
                    return {
                        "query": query,
                        "cleaned_query": query,
                        "results": results,
                        "success": True,
                        "source": "searxng",
                        "instance": instance_url
                    }
                else:
                    raise Exception(f"SearXNG request failed with status {response.status}")

    async def _search_google(self, query: str, max_results: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Search using Google Custom Search API"""
        api_key = config.get('api_key')
        cx = config.get('cx')
        
        if not api_key or not cx:
            raise Exception("Google search requires API key and Custom Search Engine ID (CX)")
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': cx,
            'q': query,
            'num': min(max_results, 10)  # Google API max is 10
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for item in data.get('items', []):
                        results.append({
                            "title": item.get('title', ''),
                            "url": item.get('link', ''),
                            "snippet": item.get('snippet', ''),
                            "source": "web"
                        })
                    
                    return {
                        "query": query,
                        "cleaned_query": query,
                        "results": results,
                        "success": True,
                        "source": "google"
                    }
                else:
                    error_data = await response.json()
                    raise Exception(f"Google API error: {error_data.get('error', {}).get('message', 'Unknown error')}")

    async def _search_bing(self, query: str, max_results: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """Search using Bing Search API"""
        api_key = config.get('api_key')
        
        if not api_key:
            raise Exception("Bing search requires API key")
        
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {'Ocp-Apim-Subscription-Key': api_key}
        params = {
            'q': query,
            'count': max_results,
            'responseFilter': 'Webpages'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    results = []
                    
                    for item in data.get('webPages', {}).get('value', []):
                        results.append({
                            "title": item.get('name', ''),
                            "url": item.get('url', ''),
                            "snippet": item.get('snippet', ''),
                            "source": "web"
                        })
                    
                    return {
                        "query": query,
                        "cleaned_query": query,
                        "results": results,
                        "success": True,
                        "source": "bing"
                    }
                else:
                    error_data = await response.json()
                    raise Exception(f"Bing API error: {error_data.get('message', 'Unknown error')}")
    
    def _perform_ddg_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform the actual DuckDuckGo search (blocking operation)"""
        try:
            if not self.ddgs:
                return []
                
            # Search for web results using new DDGS API
            web_results = list(self.ddgs.text(
                query=query,
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
            logger.error(f"DuckDuckGo search execution error: {e}")
            return []
    
    async def search_news(self, query: str, max_results: int = 3, engine: str = None) -> Dict[str, Any]:
        """Search for news using the specified engine"""
        engine = engine or self.config.get('default_engine', 'duckduckgo')
        
        try:
            await self._rate_limit_check(f"{engine}_news")
            cleaned_query = self._clean_search_query(query)
            
            if engine == 'duckduckgo':
                return await self._search_ddg_news(cleaned_query, max_results)
            else:
                # For other engines, fall back to regular search with news query modification
                news_query = f"{cleaned_query} news"
                return await self.search_web(news_query, max_results, engine)
                
        except Exception as e:
            logger.error(f"News search error for {engine}: {e}")
            return {
                "query": query,
                "results": [],
                "success": False,
                "error": str(e),
                "source": f"{engine}_news"
            }

    async def _search_ddg_news(self, query: str, max_results: int) -> Dict[str, Any]:
        """Search for news using DuckDuckGo"""
        if not self.ddgs:
            raise Exception("DuckDuckGo search not available")
            
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            self.executor,
            self._perform_ddg_news_search,
            query,
            max_results
        )
        
        return {
            "query": query,
            "results": results,
            "success": True,
            "source": "duckduckgo_news"
        }
    
    def _perform_ddg_news_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform news search using DuckDuckGo (blocking operation)"""
        try:
            if not self.ddgs:
                return []
                
            news_results = list(self.ddgs.news(
                query=query,
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
            logger.error(f"DuckDuckGo news search execution error: {e}")
            return []
    
    async def auto_search(self, user_message: str, engine: str = None) -> Optional[Dict[str, Any]]:
        """Automatically determine if search is needed and perform it with enhanced intent detection"""
        intent = self._enhance_search_intent(user_message)
        
        if not intent["should_search"]:
            return None
        
        # Determine optimal number of results based on query type
        max_results = 5
        if intent["query_type"] == "news":
            max_results = 3
        elif intent["query_type"] in ["tutorial", "definition"]:
            max_results = 7
        
        # Perform web search with retry logic
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                search_results = await self.search_web(
                    intent["suggested_query"], 
                    max_results=max_results, 
                    engine=engine
                )
                
                if search_results["success"]:
                    # Add intent information and enhanced metadata
                    search_results["search_intent"] = intent
                    search_results["auto_search"] = True
                    search_results["attempt"] = attempt + 1
                    return search_results
                else:
                    last_error = search_results.get("error", "Unknown error")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1.0 * (attempt + 1))  # Exponential backoff
                        
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    await asyncio.sleep(1.0 * (attempt + 1))  # Exponential backoff
        
        # If all retries failed, return error result
        return {
            "query": intent["suggested_query"],
            "results": [],
            "success": False,
            "error": f"Auto search failed after {max_retries} attempts: {last_error}",
            "source": engine or self.config.get('default_engine', 'duckduckgo'),
            "search_intent": intent,
            "auto_search": True
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get web search service status"""
        try:
            engines_status = {}
            
            # Check DuckDuckGo
            engines_status['duckduckgo'] = {
                'available': DDGS_AVAILABLE and self.ddgs is not None,
                'requires_api_key': False,
                'features': ['web_search', 'news_search']
            }
            
            # Check configured engines
            for engine_name in ['searxng', 'bfforexseaxng', 'google', 'bing']:
                config = self._get_search_config(engine_name)
                engines_status[engine_name] = {
                    'available': config.get('enabled', False),
                    'requires_api_key': config.get('requires_api_key', False),
                    'configured': self._is_engine_configured(engine_name, config),
                    'features': ['web_search'],
                    'description': config.get('description', '')
                }
            
            return {
                "available": any(status['available'] for status in engines_status.values()),
                "engines": engines_status,
                "default_engine": self.config.get('default_engine', 'duckduckgo'),
                "features": ["web_search", "news_search", "auto_search", "multi_engine"]
            }
            
        except Exception as e:
            return {
                "available": False,
                "error": str(e),
                "engines": {}
            }
    
    def _is_engine_configured(self, engine: str, config: Dict[str, Any]) -> bool:
        """Check if an engine is properly configured"""
        if not config.get('enabled', False):
            return False
            
        if engine == 'duckduckgo':
            return DDGS_AVAILABLE and self.ddgs is not None
        elif engine == 'searxng' or engine == 'bfforexseaxng':
            return bool(config.get('instance_url'))
        elif engine == 'google':
            return bool(config.get('api_key') and config.get('cx'))
        elif engine == 'bing':
            return bool(config.get('api_key'))
        
        return False
    
    def get_supported_engines(self) -> List[Dict[str, Any]]:
        """Get list of supported search engines with their requirements"""
        return [
            {
                'name': 'duckduckgo',
                'display_name': 'DuckDuckGo',
                'requires_api_key': False,
                'requires_instance_url': False,
                'features': ['web_search', 'news_search'],
                'free': True
            },
            {
                'name': 'searxng',
                'display_name': 'SearXNG',
                'requires_api_key': False,
                'requires_instance_url': True,
                'features': ['web_search'],
                'free': True,
                'description': 'Self-hosted search engine aggregator'
            },
            {
                'name': 'bfforexseaxng',
                'display_name': 'bfforex SearXNG',
                'requires_api_key': False,
                'requires_instance_url': False,
                'features': ['web_search'],
                'free': True,
                'description': 'Local bfforex SearXNG instance at localhost:8081'
            },
            {
                'name': 'google',
                'display_name': 'Google Custom Search',
                'requires_api_key': True,
                'requires_cx': True,
                'features': ['web_search'],
                'free': False,
                'description': 'Requires Google Cloud API key and Custom Search Engine ID'
            },
            {
                'name': 'bing',
                'display_name': 'Bing Search',
                'requires_api_key': True,
                'features': ['web_search'],
                'free': False,
                'description': 'Requires Microsoft Azure Cognitive Services API key'
            }
        ]