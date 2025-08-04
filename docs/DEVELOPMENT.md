# EvolveUI Development Guide

This guide provides detailed information for developers working with EvolveUI.

## 🏗️ Architecture Overview

### Frontend Architecture
```
frontend/src/
├── components/
│   ├── chat/              # Chat interface components
│   ├── conversations/     # Conversation management
│   ├── layout/           # Layout components (TopBar, etc.)
│   ├── settings/         # Settings and configuration
│   └── workpad/          # Code/document editor
├── hooks/                # Custom React hooks
├── utils/                # Utility functions
└── styles/               # CSS and styling
```

### Backend Architecture
```
backend/
├── api/                  # FastAPI route handlers
│   ├── models.py        # Ollama integration
│   ├── conversations.py # Conversation management
│   └── search.py        # Search and RAG functionality
├── services/            # Business logic services
│   └── chromadb_service.py # ChromaDB integration
├── models/              # Data models
└── utils/               # Backend utilities
```

## 🔧 Development Setup

### Prerequisites
- Node.js 16+
- Python 3.8+
- Ollama (for AI models)
- ChromaDB (optional, for RAG features)

### Quick Setup
```bash
# Use the automated setup script
./start.sh

# Or manual setup:
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Running in Development Mode

1. **Start Ollama**:
   ```bash
   ollama serve
   ```

2. **Start Backend**:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Start Frontend**:
   ```bash
   cd frontend
   npm start
   ```

4. **Optional: Start ChromaDB**:
   ```bash
   pip install chromadb
   chroma run --host localhost --port 8001
   ```

## 📡 API Reference

### Base URL
- Development: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

### Core Endpoints

#### Models API
```
GET  /api/models/                    # Get available Ollama models
POST /api/models/chat               # Send chat request to model
GET  /api/models/rag/status         # Get RAG system status
```

#### Conversations API
```
GET    /api/conversations/          # Get all conversations
POST   /api/conversations/          # Create new conversation
GET    /api/conversations/{id}      # Get specific conversation
POST   /api/conversations/{id}/messages  # Add message to conversation
DELETE /api/conversations/{id}      # Delete conversation
```

#### Search API
```
GET  /api/search/web               # Web search (mock)
GET  /api/search/knowledge         # Knowledge base search
POST /api/search/knowledge/add     # Add content to knowledge base
GET  /api/search/status            # Search services status
```

#### System API
```
GET /                              # API root
GET /health                        # Health check
GET /api/status                    # Full system status
```

## 🎨 Component Development

### Creating New Components

1. **React Components**:
   ```typescript
   // frontend/src/components/example/ExampleComponent.tsx
   import React from 'react';
   import { Box, Typography } from '@mui/material';

   interface ExampleComponentProps {
     title: string;
   }

   export const ExampleComponent: React.FC<ExampleComponentProps> = ({ title }) => {
     return (
       <Box sx={{ p: 2 }}>
         <Typography variant="h6">{title}</Typography>
       </Box>
     );
   };
   ```

2. **FastAPI Endpoints**:
   ```python
   # backend/api/example.py
   from fastapi import APIRouter, HTTPException

   router = APIRouter()

   @router.get("/")
   async def get_examples():
       return {"examples": []}

   @router.post("/")
   async def create_example(request: dict):
       return {"success": True}
   ```

### Styling Guidelines

- Use Material-UI (MUI) components
- Follow the dark theme color scheme:
  - Primary: Deep Blue (#1976d2)
  - Secondary: Gold (#ffd700)
  - Background: Deep Dark Blue (#0a1929)
  - Surface: Dark Blue (#1a2332)
- Maintain consistent spacing and typography

## 🧪 Testing

### Frontend Testing
```bash
cd frontend
npm test                    # Run tests
npm test -- --coverage     # Run tests with coverage
```

### Backend Testing
```bash
cd backend
source venv/bin/activate
python -m pytest          # Run tests
python -m pytest --cov    # Run tests with coverage
```

## 🐳 Docker Development

### Building Images
```bash
# Backend
cd backend
docker build -t evolveui-backend .

# Frontend
cd frontend
docker build -t evolveui-frontend .
```

### Using Docker Compose
```bash
cd docker
docker-compose up --build
```

## 🔍 Debugging

### Backend Debugging
- API logs are available in the console where uvicorn is running
- Access interactive API docs at `http://localhost:8000/docs`
- Use FastAPI's automatic validation and error handling

### Frontend Debugging
- Use React Developer Tools browser extension
- Check console for Material-UI warnings and errors
- Use browser developer tools for network debugging

### Common Issues

1. **CORS Errors**: Ensure backend CORS is configured for `http://localhost:3000`
2. **Model Selection Warnings**: Check that Ollama models are properly loaded
3. **ChromaDB Connection**: Verify ChromaDB is running on port 8001

## 📦 Building for Production

### Frontend Build
```bash
cd frontend
npm run build
```

### Backend Deployment
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Environment Variables
Create `.env` files for configuration:

Backend `.env`:
```
OLLAMA_HOST=http://localhost:11434
CHROMADB_HOST=localhost
CHROMADB_PORT=8001
```

Frontend `.env`:
```
REACT_APP_BACKEND_URL=http://localhost:8000
```

## 🤝 Contributing

### Code Style
- **Backend**: Follow PEP 8 Python style guidelines
- **Frontend**: Use TypeScript strict mode
- **Git**: Use conventional commit messages

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

### Development Workflow
1. Create issue for new features/bugs
2. Create branch from main
3. Develop and test locally
4. Create pull request
5. Code review and merge

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Material-UI Documentation](https://mui.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Ollama Documentation](https://ollama.ai/)