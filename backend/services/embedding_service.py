from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

class EmbeddingService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        self.persist_directory = "./chroma_db"
        
    def create_vector_store(self, chunks: list, document_id: str):
        """Create and persist vector store from text chunks"""
        metadatas = [{"document_id": document_id, "chunk_id": i} for i in range(len(chunks))]
        
        vector_store = Chroma.from_texts(
            texts=chunks,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory=self.persist_directory,
            collection_name=f"doc_{document_id}"
        )
        return vector_store
    
    def get_vector_store(self, document_id: str):
        """Retrieve existing vector store"""
        vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=f"doc_{document_id}"
        )
        return vector_store
    
    def create_multi_doc_vector_store(self, all_chunks: list, session_id: str):
        """
        Create vector store for multiple documents
        all_chunks: List of tuples (chunks, document_id)
        """
        texts = []
        metadatas = []
        
        for chunks, doc_id in all_chunks:
            for i, chunk in enumerate(chunks):
                texts.append(chunk)
                metadatas.append({
                    "document_id": doc_id,
                    "chunk_id": i
                })
        
        vector_store = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory=self.persist_directory,
            collection_name=f"session_{session_id}"
        )
        return vector_store
    
    def get_session_vector_store(self, session_id: str):
        """Retrieve vector store for a chat session"""
        vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=f"session_{session_id}"
        )
        return vector_store