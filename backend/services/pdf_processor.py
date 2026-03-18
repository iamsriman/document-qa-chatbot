from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    reader = PdfReader(pdf_path)
    pages = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        pages.append(page_text.strip())

    return "\n\n".join(page for page in pages if page)


def _normalize_paragraphs(text: str) -> str:
    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n")]
    cleaned_paragraphs = [" ".join(paragraph.split()) for paragraph in paragraphs if paragraph.strip()]
    return "\n\n".join(cleaned_paragraphs)


def split_text_into_chunks(text: str, chunk_size: int = 700, chunk_overlap: int = 120):
    """Split text into paragraph-aware chunks for embedding."""
    normalized_text = _normalize_paragraphs(text)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return text_splitter.split_text(normalized_text)
