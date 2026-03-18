
Autonomous Research Chatbot with Daily Research Updates

An AI-powered research intelligence platform that enables users to discover academic papers, organize knowledge by topics, interact with multiple research documents using Retrieval-Augmented Generation (RAG), and receive automated research updates via email.

This system combines research discovery, document understanding, and automated monitoring into a single unified platform — transforming how researchers interact with information.

🚀 Project Overview

Researchers often struggle with:

Finding relevant and up-to-date papers

Managing large volumes of research documents

Extracting insights across multiple papers

Staying consistently updated in fast-moving domains

This project solves these challenges by building an end-to-end intelligent research system that:

Searches papers from academic APIs

Organizes research into topic-based collections

Enables AI-powered interaction with multiple PDFs

Uses vector databases for semantic retrieval

Automatically sends curated research updates via email

👉 In simple terms:
It acts as a personal AI research assistant that learns, organizes, and keeps you updated automatically.

🧠 Core Capabilities
🔍 Research Paper Search

Integrated with arXiv API and Semantic Scholar API

Structured display of:

Title

Authors

Abstract

Year

PDF links

Supports pagination and large-scale search

Allows saving papers into topics

📂 Topic-Based Research Organization

Create and manage research topics

Save and group papers under topics

View and manage collections

Delete irrelevant papers

👉 Helps maintain a clean and structured research workspace

🤖 Multi-Document RAG Chat

The system supports chatting with multiple research papers simultaneously.

Workflow:

Upload PDFs

Extract text

Chunk the text

Generate embeddings

Store in vector database

Retrieve relevant chunks for queries

Generate grounded answers using LLM

Features:

Multi-document understanding

Context-aware responses

Conversation history

Session-based chat

👉 Enables deep cross-paper exploration

📄 PDF Processing Pipeline

Each uploaded document goes through:

Text extraction (PyPDF)

Chunking (LangChain)

Embedding generation (HuggingFace)

Storage (ChromaDB)

👉 This enables semantic search instead of keyword search

📧 Automated Research Email Updates (Key Innovation)

This system includes a fully automated research monitoring feature.

User Configuration:

Email address

Research topic

Frequency (Daily / Weekly)

Preferred time

System Workflow:

Scheduler triggers backend

Fetch latest papers from APIs

Generate structured digest

Summarize papers using LLM

Send email via Gmail

Store history in database

Each Email Contains:

Latest research paper links

Key highlights

AI-generated summaries

Overall insights for the topic

👉 This turns the system into a continuous learning and monitoring engine

🧩 System Architecture (Simplified)
User → Frontend → Backend API
                ↓
        Research APIs (arXiv, Semantic Scholar)
                ↓
        Vector Database (ChromaDB)
                ↓
        LLM (Gemini)
                ↓
        Email Scheduler → Gmail
⚙️ Technology Stack
Backend

FastAPI

Python

SQLAlchemy

LangChain

Google Gemini AI

HuggingFace Embeddings

ChromaDB

PyPDF

Frontend

React.js (Vite)

Tailwind CSS

Axios

Database

SQLite (Development)

PostgreSQL (Production)

Automation

Scheduler (Backend / Make.com)

Gmail Integration

External APIs

arXiv API

Semantic Scholar API

🧠 RAG Pipeline (How AI Answers Questions)
PDF → Text → Chunks → Embeddings → Vector DB
        ↓
User Query → Embedding → Similarity Search
        ↓
Relevant Context → Gemini LLM → Answer

👉 Ensures:

Answers are grounded in documents

Reduces hallucination

Improves accuracy

📬 Email Automation Workflow
User Subscription
        ↓
Scheduler Trigger
        ↓
Fetch Latest Papers
        ↓
Generate Summary (LLM)
        ↓
Send Email (Gmail)
        ↓
Store History (DB)
🔌 API Endpoints
Research

POST /api/search/papers

POST /api/papers/save

GET /api/topics

GET /api/topics/{id}/papers

Documents

POST /api/upload

GET /api/documents

DELETE /api/documents/{id}

Chat

POST /api/sessions/create

POST /api/query

GET /api/sessions/{id}

Automation

POST /api/auto-mail/enable

GET /api/auto-mail/trigger

GET /api/auto-mail/history/{email}

🎯 System Classification (Interview-Ready)

👉 This system is:

✅ Multi-Document RAG System

✅ AI Research Assistant

✅ Automated Knowledge Monitoring System

👉 It is NOT yet:

GraphRAG

Agentic RAG

Self-RAG

🔥 Key Strengths (What Makes This Stand Out)

Combines search + RAG + automation in one system

Supports multi-document reasoning

Provides real-time research updates

Reduces manual research effort

Designed as a continuous learning system

🚧 Current Limitations

Limited cross-document reasoning

No reranking or advanced retrieval optimization

No knowledge graph integration

Basic summarization (can be improved)

🚀 Future Enhancements

Agentic RAG architecture

GraphRAG integration

Research trend analysis dashboard

Advanced summarization & comparison

Citation export (BibTeX, APA)

Multi-user authentication

🧠 Conclusion

This project demonstrates how modern AI technologies — including LLMs, vector databases, and automation workflows — can be integrated to build a powerful research assistant.

It enables users to:

Discover academic knowledge

Organize research efficiently

Interact with documents intelligently

Stay continuously updated

👉 Ultimately, this system evolves from a simple chatbot into an:

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
