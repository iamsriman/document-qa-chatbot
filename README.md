
Autonomous Research Intelligence System
=======
# Enhanced Document Q&A Chatbot with Research Paper Search

A full-stack application that allows users to search for research papers, save them by topics, and chat with multiple PDFs using RAG (Retrieval-Augmented Generation).

## 🚀 Features

### Research Paper Search
- Search papers from Semantic Scholar and arXiv
- Display results in Wikipedia-style format
- Save papers organized by topics
- Pagination support (10 papers per page)
- Highlight important/top results

### Multi-PDF RAG Chat
- Upload PDFs to specific topics
- Create chat sessions with 2-5 documents
- Ask questions across multiple documents
- Conversation history saved per session
- Powered by Google Gemini AI

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLite/PostgreSQL
- **AI/ML**: 
  - LangChain
  - Google Gemini AI
  - HuggingFace Embeddings
  - ChromaDB (Vector Database)
- **PDF Processing**: PyPDF

### Frontend
- **Framework**: React.js (Vite)
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios

## Prerequisites

- Python 3.8+
- Node.js 16+
- Google Gemini API Key

## Installation

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install fastapi uvicorn python-multipart
pip install sqlalchemy python-dotenv pydantic pydantic-settings
pip install pypdf
pip install langchain langchain-community langchain-core langchain-google-genai langchain-text-splitters
pip install chromadb sentence-transformers
pip install requests
pip install google-genai
```

4. Create `.env` file:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

5. Run backend:
```bash
python main.py
```

Backend runs on: http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run frontend:
```bash
npm run dev
```

Frontend runs on: http://localhost:5173

## 📖 Usage Guide

### Search Papers
1. Click "🔍 Search Papers" tab
2. Enter search query (e.g., "Large Language Models")
3. Browse results (top 3 highlighted)
4. Click "💾 Save" to save paper to a topic
5. Navigate through pages for more results

### View Saved Papers
1. Click "📚 Saved Papers" button
2. Select a topic to view saved papers
3. Click PDF/Publisher links to access papers
4. Delete papers if needed

### Create Chat Session
1. Click "💬 RAG Chat" tab
2. Click "➕ New Session"
3. Select a topic from saved topics
4. Upload PDFs to the topic (optional)
5. Select 2-5 documents
6. Click "Create Chat Session"
7. Enter session name

### Chat with Documents
1. Click "💬 My Sessions"
2. Select a session
3. Ask questions in the chat
4. AI will answer based on ALL selected documents

## Project Structure
```
project-root/
├── backend/
│   ├── models/
│   │   └── database.py
│   ├── services/
│   │   ├── pdf_processor.py
│   │   ├── embedding_service.py
│   │   ├── qa_service.py
│   │   └── paper_search_service.py
│   ├── main.py
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Search/
│   │   │   │   ├── PaperSearchBar.jsx
│   │   │   │   ├── PaperCard.jsx
│   │   │   │   ├── SearchResults.jsx
│   │   │   │   ├── SavedTopics.jsx
│   │   │   │   └── SearchPage.jsx
│   │   │   └── Chat/
│   │   │       ├── TopicSelector.jsx
│   │   │       ├── DocumentUploader.jsx
│   │   │       ├── DocumentList.jsx
│   │   │       ├── SessionManager.jsx
│   │   │       ├── MultiDocChat.jsx
│   │   │       └── ChatPage.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
└── README.md
```

## 🔑 API Endpoints

### Search
- `POST /api/search/papers` - Search papers
- `POST /api/papers/save` - Save paper to topic
- `GET /api/topics` - Get all topics
- `GET /api/topics/{topic_id}/papers` - Get papers in topic

### Documents
- `POST /api/upload` - Upload PDF
- `GET /api/documents` - Get documents
- `DELETE /api/documents/{id}` - Delete document

### Chat Sessions
- `POST /api/sessions/create` - Create session
- `GET /api/sessions` - Get all sessions
- `POST /api/query` - Ask question
- `GET /api/sessions/{id}/conversations` - Get chat history

## 🐛 Troubleshooting

### Backend Issues

**Import errors:**
```bash
pip install --upgrade <package-name>
```

**Database errors:**
```bash
# Delete database and restart
rm document_qa.db
python main.py
```

**API key errors:**
- Verify `.env` file exists
- Check API key is correct
- No quotes around API key

### Frontend Issues

**Module not found:**
```bash
npm install
```

**CORS errors:**
- Check backend is running
- Verify CORS settings in `main.py`

## 📝 Notes

- Maximum 5 documents per chat session
- Minimum 2 documents per chat session
- 10 papers per search page
- Top 3 results highlighted as important

## 🎯 Future Enhancements

- [ ] Export chat history
- [ ] Advanced search filters
- [ ] Citation management
- [ ] Collaborative sessions
- [ ] Mobile app support

## 📄 License

MIT License

## 👥 Contributors

Your Name

## 🙏 Acknowledgments

- Semantic Scholar API
- arXiv API
- Google Gemini AI
- LangChain
- HuggingFace

>>>>>>> 2099274 (Clean repo and apply gitignore)
