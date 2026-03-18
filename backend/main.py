import os
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional

import requests
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session

from auth import create_access_token, get_current_user, hash_password, verify_password
from models.database import (
    AutoMailUser,
    ChatSession,
    Conversation,
    Document,
    MailHistory,
    ResearchPaper,
    Topic,
    User,
    get_db,
    init_db,
)
from services.embedding_service import EmbeddingService
from services.paper_search_service import PaperSearchService
from services.pdf_processor import extract_text_from_pdf, split_text_into_chunks
from services.qa_service import QAService

OUTSIDE_DOCUMENTS_ANSWER = (
    "Answer:\n"
    "This question is outside the provided documents."
)

app = FastAPI(title="Enhanced Document QA Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embedding_service = EmbeddingService()
qa_service = QAService(embedding_service)
paper_search_service = PaperSearchService()

init_db()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class QuestionRequest(BaseModel):
    session_id: int
    question: str


class QuestionResponse(BaseModel):
    answer: str
    question: str
    metrics: dict[str, float] = Field(default_factory=dict)
    sources: list[str] = Field(default_factory=list)
    warning: str = ""


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


class AutoMailEnableRequest(BaseModel):
    email: Optional[EmailStr] = None
    topic: str
    frequency: str
    send_time: str

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, value: str) -> str:
        if value not in {"daily", "weekly"}:
            raise ValueError("frequency must be daily or weekly")
        return value


class RunDigestRequest(BaseModel):
    email: Optional[EmailStr] = None
    topic: str
    user_id: Optional[int] = None


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
    }


def get_owned_topic(topic_id: int, user_id: int, db: Session) -> Topic:
    topic = db.query(Topic).filter(Topic.id == topic_id, Topic.user_id == user_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


def get_owned_session(session_id: int, user_id: int, db: Session) -> ChatSession:
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


def generate_research_digest(topic: str):
    url = (
        "http://export.arxiv.org/api/query"
        f"?search_query=all:{topic}&sortBy=submittedDate&sortOrder=descending&max_results=8"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    root = ET.fromstring(response.content)

    papers = []
    namespace = {"atom": "http://www.w3.org/2005/Atom"}

    for entry in root.findall("atom:entry", namespace):
        title = entry.find("atom:title", namespace).text.strip()
        summary = entry.find("atom:summary", namespace).text.strip()
        link = entry.find("atom:id", namespace).text.strip()

        authors = []
        for author in entry.findall("atom:author", namespace):
            authors.append(author.find("atom:name", namespace).text)

        short_summary = summary[:500] + "..." if len(summary) > 500 else summary
        papers.append(
            {
                "title": title,
                "authors": ", ".join(authors),
                "summary": short_summary,
                "link": link,
            }
        )

    return papers


def build_email_html(topic: str, papers: list):
    html = f"""
    <h2>AI Research Digest - {topic}</h2>
    <hr>
    """

    for index, paper in enumerate(papers, start=1):
        html += f"""
        <h3>{index}. {paper['title']}</h3>
        <p><strong>Authors:</strong> {paper['authors']}</p>
        <p>{paper['summary']}</p>
        <p><a href="{paper['link']}">Read Full Paper</a></p>
        <hr>
        """

    html += "<p>Generated by Your AI Research Assistant</p>"
    return html


def format_conversation_answer(answer: str, sources: list[str]) -> str:
    if not sources:
        return answer

    source_lines = "\n".join(f"* {source}" for source in sources)
    return f"{answer}\n\nSources:\n{source_lines}"


@app.get("/")
def read_root():
    return {"message": "Enhanced Document QA Chatbot API"}


@app.post("/api/auth/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email.lower()).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    user = User(
        email=request.email.lower(),
        password_hash=hash_password(request.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token, "token_type": "bearer", "user": serialize_user(user)}


@app.post("/api/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email.lower()).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token, "token_type": "bearer", "user": serialize_user(user)}


@app.get("/api/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return serialize_user(current_user)


@app.post("/api/search/papers")
async def search_papers(
    request: PaperSearchRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        papers = paper_search_service.search_papers(
            query=request.query,
            limit=request.limit,
            offset=request.offset,
        )
        return {
            "papers": papers,
            "total": len(papers),
            "query": request.query,
            "user_id": current_user.id,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/papers/save")
async def save_paper(
    request: SavePaperRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        topic = db.query(Topic).filter(
            Topic.name == request.topic_name,
            Topic.user_id == current_user.id,
        ).first()
        if not topic:
            topic = Topic(name=request.topic_name, user_id=current_user.id)
            db.add(topic)
            db.commit()
            db.refresh(topic)

        existing = db.query(ResearchPaper).filter(
            ResearchPaper.title == request.paper["title"],
            ResearchPaper.topic_id == topic.id,
            ResearchPaper.user_id == current_user.id,
        ).first()
        if existing:
            return {"message": "Paper already saved", "paper_id": existing.id}

        paper = ResearchPaper(
            title=request.paper["title"],
            authors=request.paper.get("authors", ""),
            abstract=request.paper.get("abstract", ""),
            year=request.paper.get("year", 0),
            citations=request.paper.get("citations", 0),
            views=request.paper.get("views", 0),
            pdf_link=request.paper.get("pdf_link"),
            publisher_link=request.paper.get("publisher_link"),
            topic_id=topic.id,
            user_id=current_user.id,
        )
        db.add(paper)
        db.commit()
        db.refresh(paper)
        return {"message": "Paper saved successfully", "paper_id": paper.id}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/topics")
def get_topics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    topics = db.query(Topic).filter(Topic.user_id == current_user.id).all()
    result = []
    for topic in topics:
        paper_count = db.query(ResearchPaper).filter(
            ResearchPaper.topic_id == topic.id,
            ResearchPaper.user_id == current_user.id,
        ).count()
        result.append(
            {
                "id": topic.id,
                "name": topic.name,
                "paper_count": paper_count,
                "created_date": topic.created_date,
            }
        )
    return result


@app.get("/api/topics/{topic_id}/papers")
def get_topic_papers(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_topic(topic_id, current_user.id, db)
    return db.query(ResearchPaper).filter(
        ResearchPaper.topic_id == topic_id,
        ResearchPaper.user_id == current_user.id,
    ).all()


@app.delete("/api/papers/{paper_id}")
def delete_paper(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paper = db.query(ResearchPaper).filter(
        ResearchPaper.id == paper_id,
        ResearchPaper.user_id == current_user.id,
    ).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    db.delete(paper)
    db.commit()
    return {"message": "Paper deleted successfully"}


@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    topic_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    if topic_id is not None:
        get_owned_topic(topic_id, current_user.id, db)

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)
    text = extract_text_from_pdf(file_path)
    chunks = split_text_into_chunks(text)

    db_document = Document(
        filename=file.filename,
        file_size=file_size,
        chunk_count=len(chunks),
        topic_id=topic_id,
        user_id=current_user.id,
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    embedding_service.create_vector_store(chunks, str(db_document.id))

    return {
        "message": "Document uploaded successfully",
        "document_id": db_document.id,
        "filename": file.filename,
        "chunks": len(chunks),
    }


@app.get("/api/documents")
def get_documents(
    topic_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Document).filter(Document.user_id == current_user.id)
    if topic_id:
        get_owned_topic(topic_id, current_user.id, db)
        query = query.filter(Document.topic_id == topic_id)
    return query.all()


@app.delete("/api/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully"}


@app.post("/api/sessions/create")
async def create_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        documents = db.query(Document).filter(
            Document.id.in_(request.document_ids),
            Document.user_id == current_user.id,
        ).all()
        if len(documents) != len(request.document_ids):
            raise HTTPException(status_code=404, detail="Some documents not found")

        session = ChatSession(name=request.name, user_id=current_user.id)
        session.documents = documents
        db.add(session)
        db.commit()
        db.refresh(session)

        all_chunks = []
        upload_dir = "uploads"
        for document in documents:
            file_path = os.path.join(upload_dir, document.filename)
            if os.path.exists(file_path):
                text = extract_text_from_pdf(file_path)
                chunks = split_text_into_chunks(text)
                all_chunks.append((chunks, str(document.id)))

        if all_chunks:
            embedding_service.create_multi_doc_vector_store(all_chunks, str(session.id))

        return {
            "message": "Session created successfully",
            "session_id": session.id,
            "document_count": len(documents),
        }
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/sessions")
def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).all()
    return [
        {
            "id": session.id,
            "name": session.name,
            "created_date": session.created_date,
            "document_count": len(session.documents),
        }
        for session in sessions
    ]


@app.get("/api/sessions/{session_id}")
def get_session_details(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = get_owned_session(session_id, current_user.id, db)
    return {
        "id": session.id,
        "name": session.name,
        "created_date": session.created_date,
        "documents": [{"id": doc.id, "filename": doc.filename} for doc in session.documents],
    }


@app.post("/api/query", response_model=QuestionResponse)
def query_documents(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(f"/api/query request started for session {request.session_id}")

    try:
        get_owned_session(request.session_id, current_user.id, db)

        vector_store = embedding_service.get_session_vector_store(str(request.session_id))
        result = qa_service.answer_question(vector_store, request.question)
        answer_text = result.get("answer") if isinstance(result, dict) else str(result)
        metrics = result.get("metrics", {}) if isinstance(result, dict) else {}
        sources = result.get("sources", []) if isinstance(result, dict) else []
        warning = result.get("warning", "") if isinstance(result, dict) else ""
        stored_answer = format_conversation_answer(answer_text or OUTSIDE_DOCUMENTS_ANSWER, sources)

        conversation = Conversation(
            chat_session_id=request.session_id,
            question=request.question,
            answer=stored_answer,
        )
        db.add(conversation)
        db.commit()

        print(f"/api/query response returned for session {request.session_id}")
        return QuestionResponse(
            answer=answer_text or OUTSIDE_DOCUMENTS_ANSWER,
            question=request.question,
            metrics=metrics or {},
            sources=sources or [],
            warning=warning or "",
        )
    except HTTPException as exc:
        db.rollback()
        print(f"/api/query request rejected for session {request.session_id}: {exc.detail}")
        return QuestionResponse(
            answer=OUTSIDE_DOCUMENTS_ANSWER,
            question=request.question,
            metrics={},
            sources=[],
            warning=str(exc.detail),
        )
    except Exception as exc:
        db.rollback()
        error_message = str(exc)
        print(f"/api/query failed for session {request.session_id}: {error_message}")
        return QuestionResponse(
            answer=OUTSIDE_DOCUMENTS_ANSWER,
            question=request.question,
            metrics={},
            sources=[],
            warning=f"Query failed: {error_message}",
        )


@app.get("/api/sessions/{session_id}/conversations")
def get_session_conversations(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_session(session_id, current_user.id, db)
    return db.query(Conversation).filter(
        Conversation.chat_session_id == session_id
    ).order_by(Conversation.timestamp).all()


@app.delete("/api/sessions/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = get_owned_session(session_id, current_user.id, db)
    db.delete(session)
    db.commit()
    return {"message": "Session deleted successfully"}


@app.post("/api/auto-mail/enable")
def enable_auto_mail(
    request: AutoMailEnableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_email = request.email or current_user.email

    subscription = db.query(AutoMailUser).filter(
        AutoMailUser.user_id == current_user.id
    ).first()

    if subscription:
        subscription.email = user_email
        subscription.topic = request.topic
        subscription.frequency = request.frequency
        subscription.send_time = request.send_time
        subscription.is_active = True
    else:
        subscription = AutoMailUser(
            user_id=current_user.id,
            email=user_email,
            topic=request.topic,
            frequency=request.frequency,
            send_time=request.send_time,
            is_active=True,
        )
        db.add(subscription)

    db.commit()
    return {"message": "Auto research mail enabled successfully"}


@app.get("/api/auto-mail/users")
def get_auto_mail_users(
    frequency: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(AutoMailUser).filter(
        AutoMailUser.user_id == current_user.id,
        AutoMailUser.frequency == frequency,
        AutoMailUser.is_active.is_(True),
    ).all()


@app.post("/api/auto-mail/run")
def run_auto_mail(
    request: RunDigestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subscription = db.query(AutoMailUser).filter(
        AutoMailUser.user_id == current_user.id
    ).first()

    papers = generate_research_digest(request.topic)
    subject = f"AI Research Digest - {request.topic}"
    html_content = build_email_html(request.topic, papers)

    history = MailHistory(
        user_id=current_user.id,
        auto_mail_user_id=subscription.id if subscription else None,
        topic=request.topic,
        subject=subject,
        html_content=html_content,
    )
    db.add(history)
    db.commit()

    return {
        "email": request.email or current_user.email,
        "subject": subject,
        "html_content": html_content,
    }


@app.get("/api/auto-mail/trigger")
def trigger_auto_mail(
    frequency: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_time = datetime.now().strftime("%H:%M")

    users = db.query(AutoMailUser).filter(
        AutoMailUser.user_id == current_user.id,
        AutoMailUser.frequency == frequency,
        AutoMailUser.is_active.is_(True),
        AutoMailUser.send_time.like(f"{current_time}%"),
    ).all()

    results = []

    for subscription in users:
        papers = generate_research_digest(subscription.topic)
        subject = f"AI Research Digest - {subscription.topic}"
        html_content = build_email_html(subscription.topic, papers)

        history = MailHistory(
            user_id=current_user.id,
            auto_mail_user_id=subscription.id,
            topic=subscription.topic,
            subject=subject,
            html_content=html_content,
        )
        db.add(history)
        db.commit()

        results.append(
            {
                "email": subscription.email,
                "subject": subject,
                "html_content": html_content,
            }
        )

    return {"current_time": current_time, "emails_to_send": results}


@app.get("/api/auto-mail/history/{email}")
def get_mail_history(
    email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if email.lower() != current_user.email.lower():
        raise HTTPException(status_code=403, detail="Access denied for requested email")

    return db.query(MailHistory).filter(
        MailHistory.user_id == current_user.id
    ).order_by(MailHistory.created_at.desc()).all()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
