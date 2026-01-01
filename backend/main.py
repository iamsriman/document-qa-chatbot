from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import shutil

from models.database import init_db, get_db, Document, Conversation
from services.pdf_processor import extract_text_from_pdf, split_text_into_chunks
from services.embedding_service import EmbeddingService
from services.qa_service import QAService

app = FastAPI(title="Document QA Chatbot API")

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

# Initialize database
init_db()

# Request/Response models
class QuestionRequest(BaseModel):
    document_id: int
    question: str

class QuestionResponse(BaseModel):
    answer: str
    question: str

@app.get("/")
def read_root():
    return {"message": "Document QA Chatbot API"}

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process PDF document"""
    
    # Check if file is PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save uploaded file
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Extract text from PDF
    text = extract_text_from_pdf(file_path)
    
    # Split into chunks
    chunks = split_text_into_chunks(text)
    
    # Create database entry
    db_document = Document(
        filename=file.filename,
        file_size=file_size,
        chunk_count=len(chunks)
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
def get_documents(db: Session = Depends(get_db)):
    """Get all uploaded documents"""
    documents = db.query(Document).all()
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

@app.post("/api/query", response_model=QuestionResponse)
def query_document(request: QuestionRequest, db: Session = Depends(get_db)):
    """Ask a question about a document"""
    
    # Check if document exists
    document = db.query(Document).filter(Document.id == request.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get vector store
    vector_store = embedding_service.get_vector_store(str(request.document_id))
    
    # Get answer
    answer = qa_service.answer_question(vector_store, request.question)
    
    # Save conversation
    conversation = Conversation(
        document_id=request.document_id,
        question=request.question,
        answer=answer
    )
    db.add(conversation)
    db.commit()
    
    return QuestionResponse(answer=answer, question=request.question)

@app.get("/api/conversations/{document_id}")
def get_conversations(document_id: int, db: Session = Depends(get_db)):
    """Get conversation history for a document"""
    conversations = db.query(Conversation).filter(
        Conversation.document_id == document_id
    ).order_by(Conversation.timestamp).all()
    return conversations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)