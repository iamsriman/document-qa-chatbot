from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil

from models.database import (
    init_db, get_db, Document, Conversation, Topic, 
    ResearchPaper, ChatSession
)
from services.pdf_processor import extract_text_from_pdf, split_text_into_chunks
from services.embedding_service import EmbeddingService
from services.qa_service import QAService
from services.paper_search_service import PaperSearchService

app = FastAPI(title="Enhanced Document QA Chatbot API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
embedding_service = EmbeddingService()
qa_service = QAService()
paper_search_service = PaperSearchService()

# Initialize database
init_db()

# Request/Response models
class QuestionRequest(BaseModel):
    session_id: int
    question: str

class QuestionResponse(BaseModel):
    answer: str
    question: str

class PaperSearchRequest(BaseModel):
    query: str
    limit: int = 10
    offset: int = 0

class SavePaperRequest(BaseModel):
    paper: dict
    topic_name: str

class CreateSessionRequest(BaseModel):
    name: str
    document_ids: List[int]

@app.get("/")
def read_root():
    return {"message": "Enhanced Document QA Chatbot API"}

# ==================== SEARCH ENDPOINTS ====================

@app.post("/api/search/papers")
async def search_papers(request: PaperSearchRequest):
    """Search for research papers"""
    try:
        papers = paper_search_service.search_papers(
            query=request.query,
            limit=request.limit,
            offset=request.offset
        )
        return {
            "papers": papers,
            "total": len(papers),
            "query": request.query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/papers/save")
async def save_paper(request: SavePaperRequest, db: Session = Depends(get_db)):
    """Save a research paper to a topic"""
    try:
        # Get or create topic
        topic = db.query(Topic).filter(Topic.name == request.topic_name).first()
        if not topic:
            topic = Topic(name=request.topic_name)
            db.add(topic)
            db.commit()
            db.refresh(topic)
        
        # Check if paper already exists
        existing_paper = db.query(ResearchPaper).filter(
            ResearchPaper.title == request.paper['title'],
            ResearchPaper.topic_id == topic.id
        ).first()
        
        if existing_paper:
            return {"message": "Paper already saved", "paper_id": existing_paper.id}
        
        # Create new paper
        paper = ResearchPaper(
            title=request.paper['title'],
            authors=request.paper['authors'],
            abstract=request.paper['abstract'],
            year=request.paper['year'],
            citations=request.paper['citations'],
            views=request.paper['views'],
            pdf_link=request.paper.get('pdf_link'),
            publisher_link=request.paper.get('publisher_link'),
            topic_id=topic.id
        )
        
        db.add(paper)
        db.commit()
        db.refresh(paper)
        
        return {"message": "Paper saved successfully", "paper_id": paper.id}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/topics")
def get_topics(db: Session = Depends(get_db)):
    """Get all topics with paper counts"""
    topics = db.query(Topic).all()
    result = []
    for topic in topics:
        paper_count = db.query(ResearchPaper).filter(ResearchPaper.topic_id == topic.id).count()
        result.append({
            "id": topic.id,
            "name": topic.name,
            "paper_count": paper_count,
            "created_date": topic.created_date
        })
    return result

@app.get("/api/topics/{topic_id}/papers")
def get_topic_papers(topic_id: int, db: Session = Depends(get_db)):
    """Get all papers for a topic"""
    papers = db.query(ResearchPaper).filter(ResearchPaper.topic_id == topic_id).all()
    return papers

@app.delete("/api/papers/{paper_id}")
def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    """Delete a research paper"""
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    db.delete(paper)
    db.commit()
    return {"message": "Paper deleted successfully"}

# ==================== DOCUMENT ENDPOINTS ====================

@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    topic_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Upload and process PDF document"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save uploaded file
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    file_size = os.path.getsize(file_path)
    
    # Extract text from PDF
    text = extract_text_from_pdf(file_path)
    
    # Split into chunks
    chunks = split_text_into_chunks(text)
    
    # Create database entry
    db_document = Document(
        filename=file.filename,
        file_size=file_size,
        chunk_count=len(chunks),
        topic_id=topic_id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Create embeddings and vector store
    embedding_service.create_vector_store(chunks, str(db_document.id))
    
    return {
        "message": "Document uploaded successfully",
        "document_id": db_document.id,
        "filename": file.filename,
        "chunks": len(chunks)
    }

@app.get("/api/documents")
def get_documents(topic_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all documents, optionally filtered by topic"""
    query = db.query(Document)
    if topic_id:
        query = query.filter(Document.topic_id == topic_id)
    documents = query.all()
    return documents

@app.delete("/api/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully"}

# ==================== CHAT SESSION ENDPOINTS ====================

@app.post("/api/sessions/create")
async def create_session(request: CreateSessionRequest, db: Session = Depends(get_db)):
    """Create a new chat session with multiple documents"""
    try:
        # Validate documents exist
        documents = db.query(Document).filter(Document.id.in_(request.document_ids)).all()
        if len(documents) != len(request.document_ids):
            raise HTTPException(status_code=404, detail="Some documents not found")
        
        # Create session
        session = ChatSession(name=request.name)
        session.documents = documents
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Create combined vector store for all documents
        all_chunks = []
        for doc in documents:
            # Read document chunks (you'll need to store or retrieve these)
            upload_dir = "uploads"
            file_path = os.path.join(upload_dir, doc.filename)
            text = extract_text_from_pdf(file_path)
            chunks = split_text_into_chunks(text)
            all_chunks.append((chunks, str(doc.id)))
        
        embedding_service.create_multi_doc_vector_store(all_chunks, str(session.id))
        
        return {
            "message": "Session created successfully",
            "session_id": session.id,
            "document_count": len(documents)
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions")
def get_sessions(db: Session = Depends(get_db)):
    """Get all chat sessions"""
    sessions = db.query(ChatSession).all()
    result = []
    for session in sessions:
        result.append({
            "id": session.id,
            "name": session.name,
            "created_date": session.created_date,
            "document_count": len(session.documents)
        })
    return result

@app.get("/api/sessions/{session_id}")
def get_session_details(session_id: int, db: Session = Depends(get_db)):
    """Get session details with documents"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id": session.id,
        "name": session.name,
        "created_date": session.created_date,
        "documents": [{"id": doc.id, "filename": doc.filename} for doc in session.documents]
    }

@app.post("/api/query", response_model=QuestionResponse)
def query_documents(request: QuestionRequest, db: Session = Depends(get_db)):
    """Ask a question in a chat session"""
    
    # Check if session exists
    session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get session vector store
    vector_store = embedding_service.get_session_vector_store(str(request.session_id))
    
    # Get answer
    answer = qa_service.answer_question(vector_store, request.question)
    
    # Save conversation
    conversation = Conversation(
        chat_session_id=request.session_id,
        question=request.question,
        answer=answer
    )
    db.add(conversation)
    db.commit()
    
    return QuestionResponse(answer=answer, question=request.question)

@app.get("/api/sessions/{session_id}/conversations")
def get_session_conversations(session_id: int, db: Session = Depends(get_db)):
    """Get conversation history for a session"""
    conversations = db.query(Conversation).filter(
        Conversation.chat_session_id == session_id
    ).order_by(Conversation.timestamp).all()
    return conversations

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    """Delete a chat session"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
    return {"message": "Session deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)