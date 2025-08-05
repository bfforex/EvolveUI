# Monitoring and System Status Guide

EvolveUI provides comprehensive monitoring capabilities to help you track system health, performance, and troubleshoot issues. This guide covers all monitoring features, logging, and status endpoints.

## 🚦 System Status Overview

### Health Check Endpoints

#### Basic Health Check
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "api": "healthy",
    "database": "healthy"
  }
}
```

#### Comprehensive Status Check
```bash
curl http://localhost:8000/api/status
```

**Response:**
```json
{
  "system_health": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "ollama": {
      "status": "connected",
      "host": "localhost:11434",
      "models_available": 5,
      "last_check": "2024-01-15T10:29:55Z"
    },
    "chromadb": {
      "status": "connected",
      "host": "localhost:8001",
      "collections": 2,
      "documents": 150,
      "last_check": "2024-01-15T10:29:55Z"
    },
    "search_engines": {
      "status": "available",
      "active_engines": ["duckduckgo"],
      "total_engines": 4
    }
  },
  "metrics": {
    "uptime": "24h 15m 30s",
    "total_requests": 1250,
    "active_conversations": 8,
    "memory_usage": "245MB",
    "cpu_usage": "12%"
  }
}
```

### Search Service Status
```bash
curl http://localhost:8000/api/search/status
```

**Response:**
```json
{
  "chromadb_available": true,
  "web_search_available": true,
  "knowledge_documents": 45,
  "conversation_history": 120,
  "rag_service": {
    "status": "active",
    "last_index_update": "2024-01-15T09:45:00Z"
  },
  "services": {
    "chromadb": {
      "status": "connected",
      "collections": ["knowledge", "conversations"],
      "total_documents": 165
    },
    "web_search": {
      "available": true,
      "engines": {
        "duckduckgo": {"available": true},
        "google": {"available": false, "reason": "Not configured"},
        "bing": {"available": false, "reason": "Not configured"},
        "searxng": {"available": false, "reason": "Not configured"}
      }
    },
    "file_processing": {
      "status": "active",
      "supported_types": ["pdf", "txt", "docx"],
      "processed_files": 23
    },
    "code_execution": {
      "status": "active",
      "supported_languages": ["python", "javascript", "bash"],
      "sandboxed": true
    }
  }
}
```

## 📊 Metrics and Performance

### API Metrics
Monitor API performance and usage:

```bash
curl http://localhost:8000/api/metrics
```

**Response:**
```json
{
  "requests": {
    "total": 1250,
    "last_hour": 85,
    "last_24h": 890,
    "success_rate": 98.5
  },
  "response_times": {
    "average": "245ms",
    "p50": "180ms",
    "p95": "520ms",
    "p99": "1.2s"
  },
  "endpoints": {
    "/api/models/chat": {
      "requests": 450,
      "avg_response_time": "1.8s",
      "error_rate": 1.2
    },
    "/api/search/web": {
      "requests": 120,
      "avg_response_time": "650ms",
      "error_rate": 3.1
    },
    "/api/conversations/": {
      "requests": 380,
      "avg_response_time": "95ms",
      "error_rate": 0.5
    }
  }
}
```

### Model Performance
Track Ollama model performance:

```bash
curl http://localhost:8000/api/models/stats
```

**Response:**
```json
{
  "available_models": [
    {
      "name": "llama2:7b",
      "status": "loaded",
      "memory_usage": "4.2GB",
      "requests_served": 285,
      "avg_response_time": "1.6s"
    },
    {
      "name": "codellama:13b",
      "status": "available",
      "memory_usage": "0MB",
      "requests_served": 45,
      "avg_response_time": "2.8s"
    }
  ],
  "total_memory_usage": "4.2GB",
  "total_requests": 330,
  "success_rate": 97.8
}
```

## 📝 Logging

### Log Levels
EvolveUI uses structured logging with the following levels:

- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational messages
- **WARNING**: Warning messages for unusual events
- **ERROR**: Error messages for failed operations
- **CRITICAL**: Critical errors that may cause system failure

### Backend Logging

#### FastAPI Application Logs
```bash
# View real-time logs
tail -f /app/logs/app.log

# View specific log level
grep "ERROR" /app/logs/app.log

# View logs for specific service
grep "search" /app/logs/app.log
```

**Log Format:**
```
2024-01-15 10:30:15,123 [INFO] [main] Starting EvolveUI Backend v1.0.0
2024-01-15 10:30:16,245 [INFO] [chromadb] Connected to ChromaDB at localhost:8001
2024-01-15 10:30:17,356 [INFO] [ollama] Connected to Ollama at localhost:11434
2024-01-15 10:30:18,467 [INFO] [search] Initialized DuckDuckGo search engine
2024-01-15 10:35:22,789 [ERROR] [search] Google API error: Invalid API key
2024-01-15 10:36:15,901 [WARNING] [chromadb] Collection 'knowledge' is empty
```

#### Service-Specific Logs

**Search Service Logs:**
```bash
# Search operations
grep "search" /app/logs/app.log | tail -20

# Search errors
grep "search.*ERROR" /app/logs/app.log
```

**ChromaDB Service Logs:**
```bash
# Database operations
grep "chromadb" /app/logs/app.log | tail -20

# Database errors
grep "chromadb.*ERROR" /app/logs/app.log
```

**Model Service Logs:**
```bash
# Model operations
grep "models" /app/logs/app.log | tail -20

# Model errors
grep "models.*ERROR" /app/logs/app.log
```

### Frontend Logging

#### Browser Console Logs
Open browser developer tools to view frontend logs:

```javascript
// View all console logs
console.log("Application logs appear here");

// Filter by log level
console.error("Error messages");
console.warn("Warning messages");
console.info("Info messages");
```

#### Network Request Logging
Monitor API requests in browser developer tools:

1. Open Developer Tools (F12)
2. Go to Network tab
3. Filter by "XHR" or "Fetch" to see API calls
4. Check status codes, response times, and payloads

## 🔍 Debugging and Troubleshooting

### Common Issues and Solutions

#### Backend Service Issues

**1. Ollama Connection Failed**
```bash
# Check Ollama status
curl http://localhost:11434/api/version

# View Ollama logs
grep "ollama" /app/logs/app.log

# Restart Ollama service
ollama serve
```

**2. ChromaDB Connection Failed**
```bash
# Check ChromaDB status
curl http://localhost:8001/api/v1/heartbeat

# View ChromaDB logs
grep "chromadb" /app/logs/app.log

# Start ChromaDB manually
chroma run --host localhost --port 8001
```

**3. Search Engine Errors**
```bash
# Check search service status
curl http://localhost:8000/api/search/status

# View search logs
grep "search" /app/logs/app.log

# Test individual engines
curl "http://localhost:8000/api/search/web?q=test&engine=duckduckgo"
```

#### Frontend Issues

**1. API Connection Errors**
- Check if backend is running on port 8000
- Verify CORS configuration
- Check browser console for network errors

**2. UI Component Errors**
- Check browser console for React errors
- Verify component props and state
- Check Material-UI theme configuration

### Debug Mode

#### Enable Debug Logging
Set environment variables to enable detailed logging:

```bash
# Backend debug mode
export LOG_LEVEL=DEBUG
export PYTHONPATH=/app
uvicorn main:app --reload --log-level debug

# Frontend debug mode
export REACT_APP_DEBUG=true
npm start
```

#### API Debug Endpoints

**System Diagnostics:**
```bash
curl http://localhost:8000/api/debug/system
```

**Service Diagnostics:**
```bash
curl http://localhost:8000/api/debug/services
```

**Performance Diagnostics:**
```bash
curl http://localhost:8000/api/debug/performance
```

## 📈 Performance Monitoring

### Resource Usage Monitoring

#### Memory Usage
```bash
# Backend memory usage
curl http://localhost:8000/api/status | jq '.metrics.memory_usage'

# System memory usage
free -h

# Process memory usage
ps aux | grep uvicorn
```

#### CPU Usage
```bash
# Backend CPU usage
curl http://localhost:8000/api/status | jq '.metrics.cpu_usage'

# System CPU usage
top -p $(pgrep uvicorn)
```

#### Disk Usage
```bash
# Check disk space
df -h

# Check log file sizes
du -sh /app/logs/*

# Check database sizes
du -sh /app/chromadb_data/*
```

### Response Time Monitoring

#### API Endpoint Performance
```bash
# Test API response times
time curl http://localhost:8000/api/models/

# Load test with ab (Apache Bench)
ab -n 100 -c 10 http://localhost:8000/api/status

# Detailed timing with curl
curl -w "@curl-format.txt" -s -o /dev/null http://localhost:8000/api/status
```

**curl-format.txt:**
```
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
```

## 🚨 Alerting and Notifications

### Health Check Automation

#### Monitoring Script
Create a monitoring script to check system health:

```bash
#!/bin/bash
# health_monitor.sh

BACKEND_URL="http://localhost:8000"
LOG_FILE="/var/log/evolveui_monitor.log"

check_service() {
    local service=$1
    local url=$2
    
    if curl -s "$url" > /dev/null; then
        echo "$(date): $service is healthy" >> $LOG_FILE
        return 0
    else
        echo "$(date): $service is down!" >> $LOG_FILE
        return 1
    fi
}

# Check main API
check_service "Main API" "$BACKEND_URL/health"

# Check Ollama
check_service "Ollama" "$BACKEND_URL/api/models/"

# Check Search
check_service "Search" "$BACKEND_URL/api/search/status"
```

#### Cron Job Setup
```bash
# Add to crontab for monitoring every 5 minutes
*/5 * * * * /path/to/health_monitor.sh
```

### Log Rotation

#### Configure Log Rotation
```bash
# /etc/logrotate.d/evolveui
/app/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 app app
    postrotate
        systemctl reload evolveui-backend
    endscript
}
```

## 🔧 Configuration for Production

### Environment Variables
```bash
# Production monitoring configuration
export LOG_LEVEL=INFO
export METRICS_ENABLED=true
export HEALTH_CHECK_INTERVAL=30
export LOG_RETENTION_DAYS=30
export ENABLE_PERFORMANCE_METRICS=true
```

### Reverse Proxy Logging (Nginx)
```nginx
# /etc/nginx/sites-available/evolveui
server {
    listen 80;
    server_name your-domain.com;
    
    access_log /var/log/nginx/evolveui_access.log combined;
    error_log /var/log/nginx/evolveui_error.log warn;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 📱 Monitoring Dashboard

### Custom Dashboard
Create a simple monitoring dashboard using the API endpoints:

```html
<!DOCTYPE html>
<html>
<head>
    <title>EvolveUI Monitoring Dashboard</title>
    <meta http-equiv="refresh" content="30">
</head>
<body>
    <h1>EvolveUI System Status</h1>
    <div id="status"></div>
    
    <script>
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                document.getElementById('status').innerHTML = 
                    `<pre>${JSON.stringify(data, null, 2)}</pre>`;
            } catch (error) {
                document.getElementById('status').innerHTML = 
                    `<p style="color: red;">Error: ${error.message}</p>`;
            }
        }
        
        updateStatus();
        setInterval(updateStatus, 30000);
    </script>
</body>
</html>
```

## 🔗 Integration with Monitoring Tools

### Prometheus Integration
Add metrics export for Prometheus:

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

REQUEST_COUNT = Counter('evolveui_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('evolveui_request_duration_seconds', 'Request latency')
ACTIVE_USERS = Gauge('evolveui_active_users', 'Active users')

@app.middleware("http")
async def add_prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_LATENCY.observe(time.time() - start_time)
    return response
```

### Grafana Dashboard
Import EvolveUI metrics into Grafana for advanced visualization and alerting.

## 📚 Additional Resources

- [FastAPI Logging Documentation](https://fastapi.tiangolo.com/tutorial/logging/)
- [Prometheus Monitoring](https://prometheus.io/docs/introduction/overview/)
- [Grafana Dashboards](https://grafana.com/docs/)
- [EvolveUI API Documentation](http://localhost:8000/docs)