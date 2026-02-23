from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./document_qa.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Many-to-many relationship table for chat sessions and documents
chat_documents = Table(
    'chat_documents',
    Base.metadata,
    Column('chat_session_id', Integer, ForeignKey('chat_sessions.id')),
    Column('document_id', Integer, ForeignKey('documents.id'))
)

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_size = Column(Integer)
    chunk_count = Column(Integer, default=0)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=True)
    
    # Relationships
    topic = relationship("Topic", back_populates="documents")
    chat_sessions = relationship("ChatSession", secondary=chat_documents, back_populates="documents")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="topic")
    papers = relationship("ResearchPaper", back_populates="topic")

class ResearchPaper(Base):
    __tablename__ = "research_papers"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    authors = Column(Text)
    abstract = Column(Text)
    year = Column(Integer)
    citations = Column(Integer, default=0)
    views = Column(Integer, default=0)
    pdf_link = Column(String, nullable=True)
    publisher_link = Column(String, nullable=True)
    saved_date = Column(DateTime, default=datetime.utcnow)
    topic_id = Column(Integer, ForeignKey('topics.id'))
    
    # Relationships
    topic = relationship("Topic", back_populates="papers")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", secondary=chat_documents, back_populates="chat_sessions")
    conversations = relationship("Conversation", back_populates="chat_session")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, ForeignKey('chat_sessions.id'))
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chat_session = relationship("ChatSession", back_populates="conversations")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()