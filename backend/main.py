from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.models import router as models_router
from api.conversations import router as conversations_router
from api.search import router as search_router
from utils.system_status import get_system_status

app = FastAPI(
    title="EvolveUI Backend API",
    version="1.0.0",
    description="Enhanced Local Interface for Ollama Models with RAG and Knowledge Management",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(models_router, prefix="/api/models", tags=["models"])
app.include_router(conversations_router, prefix="/api/conversations", tags=["conversations"])
app.include_router(search_router, prefix="/api/search", tags=["search"])

@app.get("/", tags=["system"])
def read_root():
    """API root endpoint"""
    return {
        "message": "EvolveUI Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "/api/status"
    }

@app.get("/health", tags=["system"])
def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy"}

@app.get("/api/status", tags=["system"])
async def get_api_status():
    """Get comprehensive system status including all services"""
    return await get_system_status()