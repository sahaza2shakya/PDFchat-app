# PDF Chat Application

A modern web application that allows users to upload PDFs and interact with them through a conversational chat interface. The system uses OpenAI embeddings, MongoDB Atlas Vector Search, and LangChain for intelligent question-answering.

## Features

- 📄 **PDF Upload**: Upload and process PDF documents
- 🔍 **Intelligent Chunking**: Automatic text extraction and smart chunking
- 🧠 **AI Embeddings**: OpenAI embeddings for semantic search
- 💾 **Vector Storage**: MongoDB Atlas Vector Search for efficient retrieval
- 💬 **Conversational Chat**: LangChain-powered RetrievalQA for natural Q&A
- 🎨 **Modern UI**: Beautiful, responsive React frontend

## Architecture

### Backend
- **FastAPI**: RESTful API server
- **LangChain**: LLM orchestration and RetrievalQA chain
- **OpenAI**: Embeddings and chat completions
- **MongoDB Atlas**: Vector search database
- **PyPDF**: PDF text extraction

### Frontend
- **React**: Modern UI framework
- **Vite**: Fast build tool
- **Axios**: HTTP client

## Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB Atlas account with Vector Search enabled
- OpenAI API key

## Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp env.example .env

# Edit .env with your credentials
# OPENAI_API_KEY=your_key_here
# MONGODB_URI=your_mongodb_connection_string
```

### 2. MongoDB Atlas Vector Search Setup

1. Create a MongoDB Atlas cluster (free tier available)
2. Create a database named `pdfchat` (or update in `.env`)
3. Create a collection named `pdf_embeddings` (or update in `.env`)
4. Create a Vector Search Index:
   - Go to Atlas Search → Create Index
   - Select JSON Editor
   - Use this configuration:

```json
{
  "mappings": {
    "dynamic": true,
    "fields": {
      "embedding": {
        "type": "knnVector",
        "dimensions": 1536,
        "similarity": "cosine"
      }
    }
  }
}
```

5. Name the index: `vector_index`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 4. Run the Application

**Terminal 1 - Backend:**

**Option A: Use the startup script (Recommended)**
```bash
cd backend
./start_server.sh  # Mac/Linux
# Or
start_server.bat   # Windows
```

**Option B: Manual start**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Verify Backend is Running:**
```bash
# Check server status
cd backend
python3 check_server.py

# Or manually
curl http://localhost:8000/health
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Usage

1. **Upload a PDF**: Click "Upload PDF" in the sidebar and select a PDF file
2. **Wait for Processing**: The system will extract, chunk, and embed the content
3. **Start Chatting**: Select the PDF and ask questions about its content
4. **View Sources**: Each answer includes source document references

## API Endpoints

- `POST /api/upload-pdf` - Upload and process a PDF
- `POST /api/chat` - Send a chat message and get an answer
- `GET /api/pdfs` - List all uploaded PDFs
- `DELETE /api/pdfs/{pdf_id}` - Delete a PDF and its chunks

## Configuration

Edit `backend/.env` to customize:

- `OPENAI_EMBEDDING_MODEL`: Embedding model (default: `text-embedding-3-small`)
- `OPENAI_CHAT_MODEL`: Chat model (default: `gpt-4-turbo-preview`)
- `MONGODB_DATABASE_NAME`: Database name (default: `pdfchat`)
- `MONGODB_COLLECTION_NAME`: Collection name (default: `pdf_embeddings`)

## Project Structure

```
PDFchat-app/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py           # Configuration management
│   ├── database.py         # MongoDB operations
│   ├── pdf_processor.py    # PDF extraction and chunking
│   ├── embeddings.py       # OpenAI embeddings
│   ├── qa_chain.py         # LangChain QA chain
│   ├── requirements.txt    # Python dependencies
│   └── env.example         # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── App.css         # Styles
│   │   ├── main.jsx        # Entry point
│   │   └── index.css       # Global styles
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
└── README.md
```

## Troubleshooting

### MongoDB Vector Search Index
If you get errors about the vector index, ensure:
- The index is named exactly `vector_index`
- The index has 1536 dimensions (for `text-embedding-3-small`)
- The index is fully created (may take a few minutes)

### OpenAI API Errors
- Verify your API key is correct
- Check your OpenAI account has sufficient credits
- Ensure you have access to the specified models

### PDF Processing Errors
- Ensure PDFs are not password-protected
- Check PDFs are valid and not corrupted
- Large PDFs may take longer to process

## License

MIT
