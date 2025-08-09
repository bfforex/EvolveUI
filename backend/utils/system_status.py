from typing import Dict, Any
import requests
import psutil
import time
from services.chromadb_service import ChromaDBService
from services.web_search_service import WebSearchService
import os
import json
import asyncio
from datetime import datetime

async def get_system_status() -> Dict[str, Any]:
    """Get comprehensive system status with enhanced monitoring"""
    status = {
        "overall": "healthy",
        "services": {},
        "features": {},
        "system_resources": {},
        "version": "1.1.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": get_process_uptime()
    }
    
    # Check Ollama
    ollama_status = await check_ollama_service()
    status["services"]["ollama"] = ollama_status
    
    # Check ChromaDB
    chromadb_status = await check_chromadb_service()
    status["services"]["chromadb"] = chromadb_status
    
    # Check Web Search Services
    web_search_status = await check_web_search_service()
    status["services"]["web_search"] = web_search_status
    
    # Check conversation storage
    conversations_status = check_conversations_service()
    status["services"]["conversations"] = conversations_status
    
    # Get system resources
    status["system_resources"] = get_system_resources()
    
    # Determine overall health
    service_healths = [service.get("status", "error") for service in status["services"].values()]
    if all(health == "available" for health in service_healths):
        status["overall"] = "healthy"
    elif any(health == "available" for health in service_healths):
        status["overall"] = "degraded"
    else:
        status["overall"] = "critical"
    
    # Feature availability
    status["features"] = {
        "chat": status["services"]["ollama"]["status"] == "available",
        "conversations": status["services"]["conversations"]["status"] == "available",
        "rag": status["services"]["chromadb"]["status"] == "available",
        "knowledge_base": status["services"]["chromadb"]["status"] == "available",
        "web_search": status["services"]["web_search"]["status"] == "available",
        "workpad": True,
        "settings": True,
        "file_upload": status["services"]["chromadb"]["status"] == "available"
    }
    
    return status

async def check_ollama_service() -> Dict[str, Any]:
    """Check Ollama service with detailed information"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return {
                "status": "available",
                "models_count": len(models),
                "models": [model.get("name", "") for model in models[:10]],  # First 10 models
                "api_endpoint": "http://localhost:11434",
                "response_time": response.elapsed.total_seconds()
            }
        else:
            return {
                "status": "error",
                "error": f"HTTP {response.status_code}",
                "api_endpoint": "http://localhost:11434"
            }
    except requests.exceptions.Timeout:
        return {
            "status": "timeout",
            "error": "Request timed out after 5 seconds",
            "api_endpoint": "http://localhost:11434"
        }
    except Exception as e:
        return {
            "status": "unavailable",
            "error": str(e),
            "api_endpoint": "http://localhost:11434"
        }

async def check_chromadb_service() -> Dict[str, Any]:
    """Check ChromaDB service with detailed statistics"""
    try:
        chromadb_service = ChromaDBService()
        if chromadb_service.is_available():
            stats = chromadb_service.get_collection_stats()
            return {
                "status": "available",
                "connection_type": stats.get("connection_type", "unknown"),
                "collections": stats.get("collections", []),
                "total_documents": stats.get("total_documents", 0),
                "knowledge_documents": stats.get("knowledge_documents", 0),
                "conversations": stats.get("conversations", 0),
                "files": stats.get("files", 0)
            }
        else:
            return {
                "status": "unavailable",
                "error": "Cannot connect to ChromaDB"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

async def check_web_search_service() -> Dict[str, Any]:
    """Check web search service status"""
    try:
        web_search_service = WebSearchService()
        service_status = web_search_service.get_service_status()
        
        return {
            "status": "available" if service_status.get("available", False) else "unavailable",
            "engines": service_status.get("engines", {}),
            "default_engine": service_status.get("default_engine", "duckduckgo"),
            "features": service_status.get("features", [])
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def check_conversations_service() -> Dict[str, Any]:
    """Check conversation storage service"""
    try:
        conversations_file = "conversations.json"
        if os.path.exists(conversations_file):
            with open(conversations_file, 'r') as f:
                conversations = json.load(f)
                file_stats = os.stat(conversations_file)
                return {
                    "status": "available",
                    "count": len(conversations),
                    "storage": "file_based",
                    "file_size": file_stats.st_size,
                    "last_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                }
        else:
            return {
                "status": "available",
                "count": 0,
                "storage": "file_based",
                "file_size": 0,
                "note": "New installation - no conversations yet"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

def get_system_resources() -> Dict[str, Any]:
    """Get system resource information"""
    try:
        # CPU information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory information
        memory = psutil.virtual_memory()
        
        # Disk information
        disk = psutil.disk_usage('/')
        
        # Network information (basic)
        network = psutil.net_io_counters()
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        }
    except Exception as e:
        return {
            "error": str(e),
            "available": False
        }

def get_process_uptime() -> float:
    """Get process uptime in seconds"""
    try:
        process = psutil.Process(os.getpid())
        return time.time() - process.create_time()
    except Exception:
        return 0.0

async def get_performance_metrics() -> Dict[str, Any]:
    """Get detailed performance metrics"""
    try:
        # Test response times for key services
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "response_times": {},
            "throughput": {},
            "error_rates": {}
        }
        
        # Test Ollama response time
        try:
            start_time = time.time()
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            end_time = time.time()
            if response.status_code == 200:
                metrics["response_times"]["ollama"] = end_time - start_time
            else:
                metrics["response_times"]["ollama"] = None
        except Exception:
            metrics["response_times"]["ollama"] = None
        
        # Test ChromaDB response time
        try:
            start_time = time.time()
            chromadb_service = ChromaDBService()
            stats = chromadb_service.get_collection_stats()
            end_time = time.time()
            if stats.get("available", False):
                metrics["response_times"]["chromadb"] = end_time - start_time
            else:
                metrics["response_times"]["chromadb"] = None
        except Exception:
            metrics["response_times"]["chromadb"] = None
        
        # System performance
        metrics["system_load"] = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
        }
        
        return metrics
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }