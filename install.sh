#!/bin/bash

echo "🚀 Setting up EvolveUI..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed. Please install Ollama first:"
    echo "   Visit: https://ollama.ai/"
    echo "   After installation, run: ollama serve"
fi

echo "📦 Installing backend dependencies..."
cd backend
python3 -m venv venv

# Check if running on Windows (git bash or similar)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "🪟 Detected Windows environment"
    source venv/Scripts/activate
    echo "📦 Installing Windows-compatible dependencies..."
    pip install -r requirements-windows.txt
else
    source venv/bin/activate
    pip install -r requirements.txt
fi
cd ..

echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "✅ Installation complete!"
echo ""
echo "🏃 To start EvolveUI:"
echo "1. Start Ollama: ollama serve"
echo "2. Start backend:"
echo "   # On Linux/macOS:"
echo "   cd backend && source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo "   # On Windows:"
echo "   cd backend && venv\\Scripts\\activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo "3. Start frontend: cd frontend && npm start"
echo "4. Open http://localhost:3000"
echo ""
echo "📚 For more information, see README.md"