from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os
import tempfile
import logging
from pdf_processor import pdf_processor
from embeddings import embedding_service
from database import get_db_manager
from qa_chain import get_qa_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF Chat API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    question: str
    pdf_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    source_documents: List[dict]


@app.get("/")
async def root():
    return {"message": "PDF Chat API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        db_manager = get_db_manager()
        # Test MongoDB connection
        db_manager.client.admin.command('ping')
        return {
            "status": "healthy",
            "mongodb": "connected",
            "openai": "configured"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }, 503


@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF file"""
    if not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    pdf_id = str(uuid.uuid4())
    tmp_file_path = None
    
    try:
        # Read file content
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        if len(content) > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Extract text from PDF
            logger.info(f"Extracting text from PDF: {file.filename}")
            text = pdf_processor.extract_text_from_bytes(content)
            
            if not text or len(text.strip()) == 0:
                raise HTTPException(status_code=400, detail="PDF appears to be empty or contains no extractable text")
            
            # Chunk the text
            logger.info(f"Chunking text into documents")
            documents = pdf_processor.chunk_text(text, pdf_id, file.filename)
            
            if not documents or len(documents) == 0:
                raise HTTPException(status_code=400, detail="Failed to create document chunks")
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(documents)} chunks")
            documents_with_embeddings = embedding_service.add_embeddings_to_documents(documents)
            
            # Store in MongoDB
            logger.info(f"Storing documents in MongoDB")
            db_manager = get_db_manager()
            db_manager.insert_documents(documents_with_embeddings)
            
            logger.info(f"PDF processed successfully: {file.filename} ({len(documents)} chunks)")
            return {
                "pdf_id": pdf_id,
                "filename": file.filename,
                "chunks": len(documents),
                "message": "PDF processed and stored successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing PDF: {e}", exc_info=True)
            error_msg = str(e)
            if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                raise HTTPException(status_code=503, detail=f"Database connection error: {error_msg}")
            elif "api" in error_msg.lower() or "openai" in error_msg.lower():
                raise HTTPException(status_code=503, detail=f"OpenAI API error: {error_msg}")
            else:
                raise HTTPException(status_code=500, detail=f"Error processing PDF: {error_msg}")
        finally:
            # Clean up temporary file
            if tmp_file_path and os.path.exists(tmp_file_path):
                try:
                    os.unlink(tmp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {e}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_pdf: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Handle chat messages and return answers"""
    try:
        qa_service = get_qa_service()
        result = qa_service.answer_question(message.question, message.pdf_id)
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@app.get("/api/pdfs")
async def list_pdfs():
    """List all uploaded PDFs"""
    try:
        db_manager = get_db_manager()
        # Get unique PDFs from the collection
        pipeline = [
            {
                "$group": {
                    "_id": "$metadata.pdf_id",
                    "pdf_name": {"$first": "$metadata.pdf_name"},
                    "total_chunks": {"$max": "$metadata.total_chunks"},
                    "uploaded_at": {"$min": "$_id"}  # Use ObjectId timestamp as proxy
                }
            },
            {
                "$project": {
                    "pdf_id": "$_id",
                    "pdf_name": 1,
                    "total_chunks": 1,
                    "_id": 0
                }
            }
        ]
        
        pdfs = list(db_manager.collection.aggregate(pipeline))
        return {"pdfs": pdfs}
    except Exception as e:
        logger.error(f"Error listing PDFs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing PDFs: {str(e)}")


@app.delete("/api/pdfs/{pdf_id}")
async def delete_pdf(pdf_id: str):
    """Delete a PDF and all its chunks"""
    try:
        db_manager = get_db_manager()
        deleted_count = db_manager.delete_documents_by_pdf_id(pdf_id)
        return {
            "pdf_id": pdf_id,
            "deleted_chunks": deleted_count,
            "message": "PDF deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting PDF: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

