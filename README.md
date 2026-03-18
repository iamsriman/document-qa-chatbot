# 🚀 Autonomous Research Chatbot with Daily Research Updates

==========================================================

An AI-powered research intelligence platform that enables users to discover academic papers, organize knowledge by topics, interact with multiple research documents using Retrieval-Augmented Generation (RAG), and receive automated research updates via email.

This system combines research discovery, document understanding, and automated monitoring into a single unified platform — transforming how researchers interact with information.

---

## 🚀 Project Overview

---

Researchers often struggle with:

* Finding relevant and up-to-date papers
* Managing large volumes of research documents
* Extracting insights across multiple papers
* Staying consistently updated in fast-moving domains

### 💡 Solution

This project solves these challenges by building an end-to-end intelligent research system that:

* Searches papers from academic APIs
* Organizes research into topic-based collections
* Enables AI-powered interaction with multiple PDFs
* Uses vector databases for semantic retrieval
* Automatically sends curated research updates via email

👉 **In simple terms:**
It acts as a personal AI research assistant that learns, organizes, and keeps you updated automatically.

---

## 🧠 Core Capabilities

---

### 🔍 Research Paper Search

---

* Integrated with arXiv API and Semantic Scholar API
* Displays:

  * Title
  * Authors
  * Abstract
  * Year
  * PDF links
* Supports pagination and large-scale search
* Allows saving papers into topics

---

### 📂 Topic-Based Research Organization

---

* Create and manage research topics
* Save and group papers under topics
* View and manage collections
* Delete irrelevant papers

👉 Keeps research clean, structured, and scalable

---

### 🤖 Multi-Document RAG Chat

---

Chat with multiple research papers simultaneously.

### Workflow

* Upload PDFs
* Extract text
* Chunk text
* Generate embeddings
* Store in vector DB
* Retrieve relevant chunks
* Generate answers using LLM

### Features

* Multi-document understanding
* Context-aware responses
* Conversation history
* Session-based chat

👉 Enables deep cross-paper insights

---

### 📄 PDF Processing Pipeline

---

Each document goes through:

* Text extraction (PyPDF)
* Chunking (LangChain)
* Embeddings (HuggingFace)
* Storage (ChromaDB)

👉 Enables **semantic search over keyword search**

---

### 📧 Automated Research Email Updates (Key Innovation)

---

A fully automated research monitoring system.

### User Config

* Email
* Topic
* Frequency (Daily / Weekly)
* Preferred time

### Workflow

* Scheduler triggers backend
* Fetch latest papers
* Generate summaries
* Send email via Gmail
* Store history

### Email Includes

* Latest papers
* Key highlights
* AI summaries
* Insights

👉 Converts system into a **continuous learning engine**

---

## 🧩 System Architecture

---

```
User → Frontend → Backend API
                ↓
        Research APIs (arXiv, Semantic Scholar)
                ↓
        Vector Database (ChromaDB)
                ↓
        LLM (Gemini)
                ↓
        Email Scheduler → Gmail
```

---

## ⚙️ Technology Stack

---

### 🖥 Backend

* FastAPI
* Python
* SQLAlchemy
* LangChain
* Google Gemini AI
* HuggingFace Embeddings
* ChromaDB
* PyPDF

### 🎨 Frontend

* React.js (Vite)
* Tailwind CSS
* Axios

### 🗄 Database

* SQLite (Development)
* PostgreSQL (Production)

### 🔄 Automation

* Scheduler / Make.com
* Gmail Integration

### 🌐 APIs

* arXiv API
* Semantic Scholar API

---

## 🧠 RAG Pipeline

---

```
PDF → Text → Chunks → Embeddings → Vector DB
        ↓
User Query → Embedding → Similarity Search
        ↓
Relevant Context → Gemini LLM → Answer
```

### ✅ Benefits

* Grounded answers
* Reduced hallucination
* Improved accuracy

---

## 📬 Email Automation Workflow

---

```
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
```

---

## 🔌 API Endpoints

---

### 📚 Research

* POST `/api/search/papers`
* POST `/api/papers/save`
* GET `/api/topics`
* GET `/api/topics/{id}/papers`

### 📄 Documents

* POST `/api/upload`
* GET `/api/documents`
* DELETE `/api/documents/{id}`

### 💬 Chat

* POST `/api/sessions/create`
* POST `/api/query`
* GET `/api/sessions/{id}`

### ⚙️ Automation

* POST `/api/auto-mail/enable`
* GET `/api/auto-mail/trigger`
* GET `/api/auto-mail/history/{email}`

---

## 🎯 System Classification (Interview-Ready)

---

### ✅ This System Is

* Multi-Document RAG System
* AI Research Assistant
* Automated Knowledge Monitoring System

### ❌ Not Yet

* GraphRAG
* Agentic RAG
* Self-RAG

---

## 🔥 Key Strengths

---

* Combines **search + RAG + automation**
* Multi-document reasoning
* Real-time research updates
* Reduces manual effort
* Continuous learning system

---

## 🚧 Current Limitations

---

* Limited cross-document reasoning
* No reranking / advanced retrieval
* No knowledge graph
* Basic summarization

---

## 🚀 Future Enhancements

---

* Agentic RAG architecture
* GraphRAG integration
* Research trend dashboard
* Advanced summarization & comparison
* Citation export (BibTeX, APA)
* Multi-user authentication

---

## 🧠 Conclusion

---

This project demonstrates how modern AI systems — combining LLMs, vector databases, and automation — can transform research workflows.

### 🎯 Enables Users To

* Discover knowledge
* Organize research
* Interact intelligently
* Stay continuously updated

👉 Evolves beyond a chatbot into an:

# ⚡ Autonomous Research Intelligence System

==========================================

---

If you want next level: I can convert this into a **top 1% GitHub README (badges + diagrams + recruiter hooks)**.
