Autonomous Research Chatbot with Daily Research Updates

An AI-powered research intelligence platform that enables users to search academic papers, organize them by topics, interact with multiple research documents using Retrieval-Augmented Generation (RAG), and receive automated daily or weekly research updates via email.

The system integrates research discovery, document-based AI question answering, and automated research monitoring into a single platform.

Project Overview

Researchers often face challenges in discovering relevant papers, organizing research materials, and staying updated with the latest developments in their domain.

This project addresses these problems by building an intelligent system that:

Searches research papers from academic APIs

Allows users to organize papers under specific topics

Enables AI-powered conversations with multiple research PDFs

Uses vector databases for semantic document retrieval

Sends automated research digest emails containing latest papers

Stores and displays email history for tracking research updates

The platform combines AI, Retrieval-Augmented Generation (RAG), Natural Language Processing, and automation workflows to create an autonomous research assistant.

Key Features
Research Paper Search

Users can search academic papers using external research APIs.

Features:

Search papers using arXiv API and Semantic Scholar API

Display results in structured format

Highlight important research results

Pagination support for large search results

Save papers under specific research topics

Each search result displays:

Paper title

Authors

Abstract summary

Publication year

Links to PDF and publisher page

Topic-Based Research Organization

The system allows researchers to organize saved papers into topic-based collections.

Features:

Create and manage research topics

Save research papers under topics

View papers belonging to each topic

Delete papers when no longer needed

This helps researchers maintain a structured research workspace.

Multi-Document RAG Chat

Users can interact with multiple research documents simultaneously using Retrieval-Augmented Generation.

Workflow:

Upload research PDFs under a selected topic

Extract text from uploaded documents

Split the text into smaller chunks

Generate embeddings for each chunk

Store embeddings in a vector database

Retrieve relevant document chunks when a user asks a question

Send retrieved context to the LLM for answer generation

Features:

Chat with multiple research documents

Session-based chat interface

Conversation history storage

Context-aware responses grounded in documents

This enables deep research exploration across multiple papers.

PDF Upload and Processing

The system processes uploaded PDFs through a structured pipeline.

Processing Steps:

Upload research PDF

Extract text using PyPDF

Split extracted text into chunks using LangChain Text Splitter

Generate embeddings using HuggingFace embedding models

Store embeddings in ChromaDB vector database

This pipeline allows semantic search and intelligent document retrieval.

Automated Research Email Updates

One of the major innovations of this system is automated research monitoring.

Users can subscribe to topics and receive periodic email updates.

User configuration:

Enter email address

Select research topic

Choose frequency (Daily or Weekly)

Select preferred time

System workflow:

Automation scheduler triggers backend API

Backend identifies users whose scheduled time matches

System fetches latest research papers for the selected topic

A structured research digest email is generated

Email is sent via Gmail integration

Sent digest is stored in database for history tracking

Each email digest includes:

Top 6–8 latest research papers

Paper title

Authors

Short summary

Link to full paper

Technology Stack
Backend

FastAPI

SQLAlchemy

Python

LangChain

Google Gemini AI

HuggingFace Embeddings

ChromaDB (Vector Database)

PyPDF

Frontend

React.js (Vite)

Tailwind CSS

Axios

Database

SQLite (development)

PostgreSQL (production)

Automation

Make.com (scheduler)

Gmail integration

External APIs

arXiv API

Semantic Scholar API

Retrieval-Augmented Generation (RAG) Pipeline

The system uses a multi-document RAG architecture to answer research questions.

Steps:

Extract text from uploaded PDFs

Split text into smaller chunks

Generate embeddings for each chunk

Store embeddings in ChromaDB vector database

Convert user question into embedding

Perform similarity search to retrieve relevant document chunks

Send retrieved context to Google Gemini LLM

Gemini generates a context-aware answer

This approach ensures answers are grounded in actual research documents rather than relying only on model memory.

Email Automation Workflow

The automated research update system works as follows:

Users subscribe to research topics and scheduling preferences

Automation scheduler periodically triggers backend API

Backend checks users whose scheduled time matches

Latest research papers are fetched from arXiv

A structured research digest is generated

Emails are sent using Gmail automation

Email history is stored in the database

This allows researchers to continuously receive the latest papers without manual searching.

API Endpoints
Research Search

POST /api/search/papers
Search research papers

POST /api/papers/save
Save paper under a topic

GET /api/topics
Retrieve all research topics

GET /api/topics/{topic_id}/papers
Retrieve papers under a topic

Document Management

POST /api/upload
Upload research PDF

GET /api/documents
Retrieve uploaded documents

DELETE /api/documents/{id}
Delete document

Chat Sessions

POST /api/sessions/create
Create chat session

GET /api/sessions
Retrieve chat sessions

POST /api/query
Ask question to research documents

GET /api/sessions/{id}/conversations
Retrieve chat history

Email Automation

POST /api/auto-mail/enable
Enable automated research updates

GET /api/auto-mail/trigger
Trigger scheduled email generation

GET /api/auto-mail/history/{email}
Retrieve sent email history

Future Enhancements

Integration of Agentic RAG architecture

Conversational memory for long-term research tracking

Advanced research summarization

Research trend analysis dashboard

Multi-user authentication system

Citation export support (BibTeX, APA, MLA)

Conclusion

This project demonstrates how modern AI technologies such as Large Language Models, vector databases, and automation workflows can be integrated to build an intelligent research assistant.

The system enables researchers to:

Discover relevant academic papers

Organize research knowledge

Interact with research documents using AI

Receive automated research updates

By combining research discovery, document analysis, conversational AI, and automated monitoring, the platform evolves from a simple chatbot into an Autonomous Research Intelligence System.
