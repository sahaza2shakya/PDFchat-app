import pypdf
from typing import List, Dict, Any
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def extract_text_from_pdf(self, pdf_file_path: str) -> str:
        """Extract all text from a PDF file"""
        text = ""
        try:
            with open(pdf_file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            logger.info(f"Extracted text from PDF: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def extract_text_from_bytes(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes"""
        text = ""
        try:
            from io import BytesIO
            pdf_file = BytesIO(pdf_bytes)
            pdf_reader = pypdf.PdfReader(pdf_file)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            logger.info(f"Extracted text from PDF bytes: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF bytes: {e}")
            raise
    
    def chunk_text(self, text: str, pdf_id: str, pdf_name: str) -> List[Dict[str, Any]]:
        """Split text into chunks and prepare for embedding"""
        chunks = self.text_splitter.split_text(text)
        
        documents = []
        for idx, chunk in enumerate(chunks):
            doc = {
                "text": chunk,
                "metadata": {
                    "pdf_id": pdf_id,
                    "pdf_name": pdf_name,
                    "chunk_index": idx,
                    "total_chunks": len(chunks)
                }
            }
            documents.append(doc)
        
        logger.info(f"Created {len(documents)} chunks from PDF {pdf_name}")
        return documents


pdf_processor = PDFProcessor()

