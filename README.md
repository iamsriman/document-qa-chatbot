Autonomous Research Chatbot with Daily Research Updates
--------------------------------------------------------
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
