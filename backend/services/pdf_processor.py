from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def split_text_into_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    """Split text into chunks for embedding"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    return chunks