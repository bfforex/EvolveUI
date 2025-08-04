from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.models import router as models_router
from api.conversations import router as conversations_router
from api.search import router as search_router

app = FastAPI(title="EvolveUI Backend", version="1.0.0")

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

@app.get("/")
def read_root():
    return {"message": "EvolveUI Backend API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}