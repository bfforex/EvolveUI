# Search Engine Integration Guide

EvolveUI provides comprehensive web search capabilities through multiple search engine integrations. This guide covers configuration, usage, and API examples for all supported search engines.

## 🔍 Supported Search Engines

### DuckDuckGo (Default)
- **Type**: Free, no API key required
- **Features**: Web search, news search, auto search detection
- **Privacy**: No tracking, anonymous searches
- **Rate Limit**: 2 seconds between requests
- **Status**: ✅ Active by default

### SearXNG
- **Type**: Self-hosted search aggregator
- **Features**: Web search, privacy-focused
- **Requirements**: Instance URL
- **Rate Limit**: 1 second between requests
- **Status**: ⚠️ Requires configuration

### Google Custom Search
- **Type**: Commercial API
- **Features**: High-quality web search results
- **Requirements**: API key, Custom Search Engine ID (CX)
- **Rate Limit**: 1 second between requests
- **Status**: ⚠️ Requires API credentials

### Bing Search API
- **Type**: Commercial API
- **Features**: Microsoft's search results
- **Requirements**: Azure Cognitive Services API key
- **Rate Limit**: 1 second between requests
- **Status**: ⚠️ Requires API credentials

## ⚙️ Configuration

### Basic Configuration
Search engines are configured through the backend API. The default configuration enables DuckDuckGo:

```json
{
  "default_engine": "duckduckgo",
  "engines": {
    "duckduckgo": {
      "enabled": true
    },
    "searxng": {
      "enabled": false,
      "instance_url": "https://searx.be"
    },
    "google": {
      "enabled": false,
      "api_key": null,
      "cx": null
    },
    "bing": {
      "enabled": false,
      "api_key": null
    }
  }
}
```

### Environment Variables
You can configure search engines using environment variables:

```bash
# Backend .env file
SEARCH_DEFAULT_ENGINE=duckduckgo
SEARXNG_INSTANCE_URL=https://your-searxng-instance.com
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CX=your_custom_search_engine_id
BING_API_KEY=your_bing_api_key
```

## 🚀 API Usage Examples

### Get Search Engine Status
```bash
curl http://localhost:8000/api/search/engines
```

**Response:**
```json
{
  "engines": [
    {
      "name": "duckduckgo",
      "display_name": "DuckDuckGo",
      "requires_api_key": false,
      "features": ["web_search", "news_search"],
      "free": true
    }
  ],
  "current_status": {
    "available": true,
    "engines": {
      "duckduckgo": {
        "available": true,
        "requires_api_key": false,
        "features": ["web_search", "news_search"]
      }
    }
  },
  "default_engine": "duckduckgo"
}
```

### Perform Web Search
```bash
# Basic search
curl "http://localhost:8000/api/search/web?q=artificial+intelligence&limit=5"

# Search with specific engine
curl "http://localhost:8000/api/search/web?q=machine+learning&limit=3&engine=duckduckgo"
```

**Response:**
```json
{
  "query": "artificial intelligence",
  "cleaned_query": "artificial intelligence",
  "results": [
    {
      "title": "Artificial Intelligence - Wikipedia",
      "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
      "snippet": "Artificial intelligence (AI) is intelligence demonstrated by machines...",
      "source": "web"
    }
  ],
  "success": true,
  "source": "duckduckgo"
}
```

### News Search
```bash
curl "http://localhost:8000/api/search/news?q=technology&limit=3"
```

**Response:**
```json
{
  "query": "technology",
  "results": [
    {
      "title": "Latest Technology News",
      "url": "https://example.com/tech-news",
      "snippet": "Breaking technology news and updates...",
      "date": "2024-01-15",
      "source": "news"
    }
  ],
  "success": true,
  "source": "duckduckgo_news"
}
```

### Auto Search Detection
The system can automatically determine if a user query would benefit from web search:

```bash
curl "http://localhost:8000/api/search/auto?q=what+is+the+current+weather+in+New+York"
```

**Response:**
```json
{
  "search_performed": true,
  "query": "current weather New York",
  "results": [...],
  "search_intent": {
    "should_search": true,
    "confidence": 0.8,
    "indicators_found": 3,
    "suggested_query": "current weather New York"
  }
}
```

## 🛠️ Setting Up Commercial APIs

### Google Custom Search Setup

1. **Create a Google Cloud Project**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Custom Search API**
   - Go to APIs & Services > Library
   - Search for "Custom Search API"
   - Click "Enable"

3. **Create API Key**
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "API Key"
   - Copy the API key

4. **Create Custom Search Engine**
   - Visit [Google Custom Search](https://cse.google.com/)
   - Click "Add" to create new search engine
   - Enter `*.com` as the site to search
   - Copy the Search Engine ID (CX)

5. **Configure EvolveUI**
   ```bash
   curl -X POST http://localhost:8000/api/search/config \
     -H "Content-Type: application/json" \
     -d '{
       "engines": {
         "google": {
           "enabled": true,
           "api_key": "your_api_key",
           "cx": "your_search_engine_id"
         }
       }
     }'
   ```

### Bing Search API Setup

1. **Create Azure Account**
   - Visit [Azure Portal](https://portal.azure.com/)
   - Sign up or sign in

2. **Create Cognitive Services Resource**
   - Search for "Cognitive Services"
   - Create new "Bing Search v7" resource
   - Choose pricing tier (F1 for free tier)

3. **Get API Key**
   - Go to your Bing Search resource
   - Click "Keys and Endpoint"
   - Copy one of the API keys

4. **Configure EvolveUI**
   ```bash
   curl -X POST http://localhost:8000/api/search/config \
     -H "Content-Type: application/json" \
     -d '{
       "engines": {
         "bing": {
           "enabled": true,
           "api_key": "your_bing_api_key"
         }
       }
     }'
   ```

### SearXNG Setup

1. **Find SearXNG Instance**
   - Visit [SearXNG Instances](https://searx.space/)
   - Choose a public instance or host your own

2. **Configure EvolveUI**
   ```bash
   curl -X POST http://localhost:8000/api/search/config \
     -H "Content-Type: application/json" \
     -d '{
       "engines": {
         "searxng": {
           "enabled": true,
           "instance_url": "https://your-searxng-instance.com"
         }
       }
     }'
   ```

## 📊 Search Features

### Auto Search Detection
The system automatically detects when user queries would benefit from web search based on:

- **Keywords**: "current", "latest", "news", "weather", "price"
- **Question patterns**: "what is", "who is", "where is", "how to"
- **Topics**: Stock prices, cryptocurrency, breaking news, weather
- **Time indicators**: "today", "now", "recent"

### Rate Limiting
All search engines have built-in rate limiting to prevent API abuse:

- **DuckDuckGo**: 2 seconds between requests
- **SearXNG**: 1 second between requests
- **Google/Bing**: 1 second between requests

### Error Handling
The system includes comprehensive error handling:

- **Graceful degradation**: Falls back to mock results if services unavailable
- **Retry logic**: Automatic retries with exponential backoff
- **API limits**: Respects API quotas and rate limits
- **Timeout handling**: 10-second timeout for all requests

### Search Result Processing
All search results are processed and normalized:

- **Content cleaning**: Removes special characters and extra whitespace
- **Relevance scoring**: Orders results by relevance
- **Metadata extraction**: Includes titles, URLs, snippets, and dates
- **Source attribution**: Clearly identifies search engine used

## 🔧 Advanced Configuration

### Custom Search Logic
You can customize search behavior by modifying the search intent detection:

```python
# Example: Add custom search indicators
search_indicators = [
    'current', 'latest', 'recent', 'news', 'today', 'now',
    'what is', 'who is', 'where is', 'when did', 'how to',
    'your_custom_keyword'
]
```

### Multiple Engine Strategy
Configure fallback engines for better reliability:

```json
{
  "default_engine": "duckduckgo",
  "fallback_engines": ["searxng", "google"],
  "engines": {
    "duckduckgo": {"enabled": true},
    "searxng": {"enabled": true, "instance_url": "https://searx.be"},
    "google": {"enabled": true, "api_key": "...", "cx": "..."}
  }
}
```

## 📈 Performance Optimization

### Caching
Search results are cached to improve performance:

- **Result caching**: 5-minute cache for search results
- **Intent caching**: 1-hour cache for search intent detection
- **Status caching**: 30-second cache for service status

### Monitoring
Monitor search performance through the API:

```bash
curl http://localhost:8000/api/search/status
```

This returns detailed metrics about search service health, response times, and error rates.

## 🔒 Privacy and Security

### Data Protection
- **No logging**: Search queries are not permanently stored
- **Anonymous requests**: DuckDuckGo provides anonymous searching
- **API key security**: Keys are stored securely and not exposed in logs

### Content Filtering
- **Safe search**: Enabled by default on all engines
- **Content moderation**: Inappropriate content is filtered
- **Region settings**: Configurable region preferences

## 🐛 Troubleshooting

### Common Issues

1. **DuckDuckGo not working**
   - Check internet connectivity
   - Verify `duckduckgo-search` package is installed
   - Check for rate limiting (wait 2 seconds between requests)

2. **API keys not working**
   - Verify API keys are correctly configured
   - Check API quotas and billing status
   - Ensure proper permissions are set

3. **SearXNG instance unavailable**
   - Try different public instances
   - Verify instance URL is correct
   - Check if instance supports JSON API

4. **Search results empty**
   - Check query formatting
   - Verify search engine is enabled
   - Check service status endpoint

### Debug Mode
Enable debug logging to troubleshoot issues:

```bash
# Backend logs
tail -f backend/logs/search.log

# Check service status
curl http://localhost:8000/api/search/status
```

## 📚 Additional Resources

- [DuckDuckGo Search API](https://pypi.org/project/duckduckgo-search/)
- [SearXNG Documentation](https://docs.searxng.org/)
- [Google Custom Search API](https://developers.google.com/custom-search/v1/overview)
- [Bing Search API Documentation](https://docs.microsoft.com/en-us/bing/search-apis/)
- [EvolveUI API Documentation](http://localhost:8000/docs)