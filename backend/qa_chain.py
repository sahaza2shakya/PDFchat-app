from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain.prompts import PromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from pymongo import MongoClient
from config import settings
from database import get_db_manager
from embeddings import embedding_service
from typing import List, Dict, Any, Optional
from pydantic import Field
import logging

logger = logging.getLogger(__name__)


class MongoDBAtlasRetriever(BaseRetriever):
    """Custom retriever for MongoDB Atlas Vector Search"""
    
    pdf_id: Optional[str] = Field(default=None, description="Optional PDF ID to filter results")
    k: int = Field(default=5, description="Number of documents to retrieve")
    
    class Config:
        arbitrary_types_allowed = True
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve relevant documents using vector search"""
        # Generate embedding for the query
        query_embedding = embedding_service.generate_embeddings([query])[0]
        
        # Perform vector search with optional pdf_id filter
        db_manager = get_db_manager()
        results = db_manager.vector_search(query_embedding, limit=self.k, pdf_id=self.pdf_id)
        
        # Convert to LangChain Documents
        documents = []
        for result in results:
            doc = Document(
                page_content=result.get("text", ""),
                metadata=result.get("metadata", {})
            )
            documents.append(doc)
        
        return documents
    
    async def aget_relevant_documents(self, query: str) -> List[Document]:
        """Async version of get_relevant_documents"""
        return self.get_relevant_documents(query)


class QAService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_chat_model,
            temperature=0,
            openai_api_key=settings.openai_api_key
        )
        self.embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # Initialize vector store
        db_manager = get_db_manager()
        self.vector_store = MongoDBAtlasVectorSearch(
            collection=db_manager.collection,
            embedding=self.embeddings,
            index_name="vector_index"
        )
        
        # Create custom prompt template
        self.prompt_template = PromptTemplate(
            template="""Use the following pieces of context from uploaded PDF documents to answer the question. 
If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.

Context: {context}

Question: {question}

Provide a detailed answer based only on the context provided:""",
            input_variables=["context", "question"]
        )
        
        # Initialize QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 5}
            ),
            chain_type_kwargs={"prompt": self.prompt_template},
            return_source_documents=True
        )
    
    def answer_question(self, question: str, pdf_id: str = None) -> Dict[str, Any]:
        """Answer a question using the retrieval QA chain"""
        try:
            # Use custom retriever for better MongoDB Atlas Vector Search compatibility
            retriever = MongoDBAtlasRetriever(pdf_id=pdf_id, k=5)
            
            # Create QA chain with custom retriever
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": self.prompt_template},
                return_source_documents=True
            )
            
            result = qa_chain.invoke({"query": question})
            
            return {
                "answer": result["result"],
                "source_documents": [
                    {
                        "text": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in result.get("source_documents", [])
                ]
            }
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise


# Global QA service instance (lazy initialization)
_qa_service = None

def get_qa_service():
    """Get or create QA service instance"""
    global _qa_service
    if _qa_service is None:
        try:
            _qa_service = QAService()
            logger.info("QA service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize QA service: {e}")
            raise
    return _qa_service

# Create a simple class to maintain backward compatibility
class QAServiceProxy:
    def __getattr__(self, name):
        return getattr(get_qa_service(), name)

qa_service = QAServiceProxy()

