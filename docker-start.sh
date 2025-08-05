#!/bin/bash

# EvolveUI Docker Startup Script
# This script provides an easy way to start EvolveUI with Docker

set -e

echo "🚀 Starting EvolveUI with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Please run this script from the EvolveUI root directory."
    exit 1
fi

# Create necessary files if they don't exist
echo "📋 Checking configuration files..."

if [ ! -f "backend/conversations.json" ]; then
    echo "Creating backend/conversations.json..."
    echo "[]" > backend/conversations.json
fi

if [ ! -d "backend/chromadb_data" ]; then
    echo "Creating backend/chromadb_data directory..."
    mkdir -p backend/chromadb_data
fi

# Check if Ollama is running
echo "🔍 Checking Ollama status..."
if ! curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "⚠️  Warning: Ollama is not running at localhost:11434"
    echo "   Please start Ollama with: ollama serve"
    echo "   You can continue without Ollama, but AI features will be limited."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. Please start Ollama and try again."
        exit 1
    fi
else
    echo "✅ Ollama is running"
fi

# Start services
echo "🐳 Starting Docker services..."
docker compose up --build -d

# Wait a moment for services to start
echo "⏳ Waiting for services to start..."
sleep 5

# Check service health
echo "🏥 Checking service health..."

# Check backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend may still be starting up"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "⚠️  Frontend may still be starting up"
fi

echo ""
echo "🎉 EvolveUI is starting up!"
echo ""
echo "📱 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker compose logs -f"
echo "   Stop services: docker compose down"
echo "   Restart services: docker compose restart"
echo ""
echo "📚 Documentation:"
echo "   Search Engines: docs/search_engines.md"
echo "   Monitoring: docs/monitoring.md"
echo "   Development: docs/DEVELOPMENT.md"
echo ""

# Offer to show logs
read -p "Would you like to view the logs? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker compose logs -f
fi