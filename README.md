# EvolveUI - Enhanced Local Interface for Ollama Models

EvolveUI is a comprehensive local web interface for interacting with Ollama models, providing advanced features beyond basic chat functionality. It features a modern, professional design with intelligent conversation management, workpad functionality, and extensible architecture.

![EvolveUI Interface](https://github.com/user-attachments/assets/fe11e8b4-1236-4e01-901d-84bb8ce582bd)

## 🌟 Features

### Core Functionality
- **Three-Panel Layout**: Conversations (left), Chat (center), Workpad (right)
- **Model Management**: Auto-detect available Ollama models dynamically
- **Conversation Management**: Persistent conversations with auto-naming and time-based grouping
- **Real-time Chat**: Seamless communication with Ollama models
- **Workpad/Canvas**: Integrated code and document editor with file management

### Advanced Capabilities
- **Persistent Memory**: Knowledge database integration (ChromaDB)
- **RAG (Retrieval Augmented Generation)**: Context-aware responses
- **Auto Web Search**: Intelligent web search integration
- **File Processing**: PDF, DOCX, TXT upload and processing
- **Code Execution**: Safe code execution environment

### UI/UX Features
- **Dark Theme**: Professional dark blue color scheme with gold accents
- **Responsive Design**: Optimized for various screen sizes
- **Sliding Panels**: Smooth animations and intuitive navigation
- **Time-based Organization**: Conversations grouped by Today, Yesterday, This Week, etc.
- **Hover Actions**: Three-dot menus for conversation management

## 🚀 Quick Start

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8+
- Ollama installed and running locally

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/bfforex/EvolveUI.git
   cd EvolveUI
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Start Ollama** (in a separate terminal)
   ```bash
   ollama serve
   ```

5. **Start the backend server**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Start the frontend server**
   ```bash
   cd frontend
   npm start
   ```

7. **Open your browser**
   Navigate to `http://localhost:3000`

## 📁 Project Structure

```
EvolveUI/
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── chat/        # Chat interface components
│   │   │   ├── conversations/ # Conversation management
│   │   │   ├── layout/      # Layout components
│   │   │   ├── settings/    # Settings panel
│   │   │   └── workpad/     # Workpad/Canvas components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── utils/           # Utility functions
│   │   └── styles/          # CSS and styling
│   └── public/              # Static assets
├── backend/                 # Python FastAPI backend
│   ├── api/                 # API route handlers
│   │   ├── models.py        # Ollama model integration
│   │   ├── conversations.py # Conversation management
│   │   └── search.py        # Search functionality
│   ├── services/            # Business logic services
│   ├── models/              # Data models
│   └── utils/               # Backend utilities
├── docker/                  # Docker configuration
├── docs/                    # Documentation
└── README.md
```

## 🎨 Design System

### Color Scheme
- **Primary**: Deep Blue (#1976d2)
- **Secondary**: Gold (#ffd700)
- **Background**: Deep Dark Blue (#0a1929)
- **Surface**: Dark Blue (#1a2332)
- **Text**: White (#ffffff)
- **Text Secondary**: Grayish Blue (#b0bec5)

### Typography
- **Interface**: System fonts (-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto)
- **Code**: Monaco, Consolas, 'Courier New', monospace

## 🔧 Configuration

### Backend Configuration
The backend automatically connects to Ollama running on `localhost:11434`. Conversation data is stored in `conversations.json` in the backend directory.

### Frontend Configuration
The frontend is configured to connect to the backend at `localhost:8000`. CORS is properly configured for development.

## 🚦 API Endpoints

### Models API
- `GET /api/models/` - Get available Ollama models
- `POST /api/models/chat` - Send chat request to model

### Conversations API
- `GET /api/conversations/` - Get all conversations
- `POST /api/conversations/` - Create new conversation
- `GET /api/conversations/{id}` - Get specific conversation
- `POST /api/conversations/{id}/messages` - Add message to conversation
- `DELETE /api/conversations/{id}` - Delete conversation

### Search API
- `GET /api/search/web` - Web search
- `GET /api/search/knowledge` - Knowledge base search

## 🧪 Development

### Running Tests
```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
python -m pytest
```

### Building for Production
```bash
# Build frontend
cd frontend
npm run build

# The built files will be in frontend/build/
```

## 🛣️ Roadmap

### Phase 1: Core Features ✅
- [x] Basic UI layout and navigation
- [x] Ollama integration and model detection
- [x] Conversation management and persistence
- [x] Workpad/Canvas functionality

### Phase 2: Enhanced AI
- [x] ChromaDB integration for RAG
- [x] Web search integration
- [x] Settings panel and configuration
- [x] Document processing (PDF, DOCX, TXT)

### Phase 3: Advanced Features
- [ ] Code execution environment
- [ ] Voice input/output
- [ ] Multi-language support
- [ ] Collaboration features
- [ ] Plugin system
- [ ] Cloud backup and sync

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for the excellent local LLM serving
- [Material-UI](https://mui.com/) for the React components
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- GitHub Copilot for design inspiration

## 📞 Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Check the documentation in the `docs/` folder
- Review the API documentation at `http://localhost:8000/docs` when running the backend

---

**EvolveUI** - Evolving the way you interact with AI models locally.
