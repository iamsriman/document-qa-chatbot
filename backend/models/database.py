import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    create_engine,
    inspect,
    text,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./document_qa.db")

if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

chat_documents = Table(
    "chat_documents",
    Base.metadata,
    Column("chat_session_id", Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE")),
    Column("document_id", Integer, ForeignKey("documents.id", ondelete="CASCADE")),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    topics = relationship("Topic", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    research_papers = relationship("ResearchPaper", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    auto_mail_users = relationship("AutoMailUser", back_populates="user", cascade="all, delete-orphan")
    mail_history = relationship("MailHistory", back_populates="user", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)

    user = relationship("User", back_populates="topics")
    documents = relationship("Document", back_populates="topic")
    papers = relationship("ResearchPaper", back_populates="topic")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    file_size = Column(Integer)
    chunk_count = Column(Integer, default=0)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)

    topic = relationship("Topic", back_populates="documents")
    user = relationship("User", back_populates="documents")
    chat_sessions = relationship("ChatSession", secondary=chat_documents, back_populates="documents")


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
    topic_id = Column(Integer, ForeignKey("topics.id"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)

    topic = relationship("Topic", back_populates="papers")
    user = relationship("User", back_populates="research_papers")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)

    user = relationship("User", back_populates="chat_sessions")
    documents = relationship("Document", secondary=chat_documents, back_populates="chat_sessions")
    conversations = relationship("Conversation", back_populates="chat_session", cascade="all, delete")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"))
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    chat_session = relationship("ChatSession", back_populates="conversations")


class AutoMailUser(Base):
    __tablename__ = "auto_mail_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    topic = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    send_time = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)

    user = relationship("User", back_populates="auto_mail_users")
    history = relationship("MailHistory", back_populates="auto_mail_subscription")


class MailHistory(Base):
    __tablename__ = "mail_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    auto_mail_user_id = Column(Integer, ForeignKey("auto_mail_users.id", ondelete="SET NULL"), nullable=True)
    topic = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    html_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="mail_history")
    auto_mail_subscription = relationship("AutoMailUser", back_populates="history")


def _add_column_if_missing(table_name: str, column_name: str, column_sql: str) -> None:
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    if column_name in columns:
        return

    statement = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_sql}"
    with engine.begin() as connection:
        connection.execute(text(statement))


def _run_lightweight_migrations() -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    if "topics" in tables:
        _add_column_if_missing("topics", "user_id", "INTEGER")
    if "documents" in tables:
        _add_column_if_missing("documents", "user_id", "INTEGER")
    if "research_papers" in tables:
        _add_column_if_missing("research_papers", "user_id", "INTEGER")
    if "chat_sessions" in tables:
        _add_column_if_missing("chat_sessions", "user_id", "INTEGER")
    if "auto_mail_users" in tables:
        _add_column_if_missing("auto_mail_users", "user_id", "INTEGER")
    if "mail_history" in tables:
        _add_column_if_missing("mail_history", "auto_mail_user_id", "INTEGER")


def init_db():
    Base.metadata.create_all(bind=engine)
    _run_lightweight_migrations()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
