#!/bin/bash

# EvolveUI Quick Start Script
echo "🚀 EvolveUI Quick Start"
echo "======================="

# Check system requirements
echo "📋 Checking system requirements..."

# Check Node.js
if command -v node >/dev/null 2>&1; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js: $NODE_VERSION"
else
    echo "❌ Node.js not found. Please install Node.js 16+ first."
    echo "   Download from: https://nodejs.org/"
    exit 1
fi

# Check Python
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found. Please install Python 3.8+ first."
    echo "   Download from: https://python.org/"
    exit 1
fi

# Check if in correct directory
if [ ! -f "README.md" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "❌ Please run this script from the EvolveUI root directory"
    exit 1
fi

echo ""
echo "🔧 Setting up EvolveUI..."

# Backend setup
echo "📦 Setting up backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "   Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "   Activating virtual environment and installing dependencies..."
# Check if running on Windows (git bash or similar)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "🪟 Detected Windows environment"
    source venv/Scripts/activate
    pip install -q -r requirements-windows.txt
else
    source venv/bin/activate
    pip install -q -r requirements.txt
fi
cd ..

# Frontend setup
echo "📦 Setting up frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "   Installing Node.js dependencies..."
    npm install --silent
fi
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start EvolveUI:"
echo ""
echo "1. 📡 Start Ollama (in a separate terminal):"
echo "   ollama serve"
echo ""
echo "2. 🖥️  Start the backend (in a separate terminal):"
echo "   # On Linux/macOS:"
echo "   cd backend && source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo "   # On Windows:"
echo "   cd backend && venv\\Scripts\\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "3. 🌐 Start the frontend:"
echo "   cd frontend && npm start"
echo ""
echo "4. 🎉 Open your browser to:"
echo "   http://localhost:3000"
echo ""
echo "📚 Additional Resources:"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • README: README.md"
echo "   • GitHub: https://github.com/bfforex/EvolveUI"
echo ""
echo "🎯 Optional: Install ChromaDB for advanced RAG features"
echo "   pip install chromadb && chroma run --host localhost --port 8001"