from openai import OpenAI
from config import settings
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def add_embeddings_to_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add embeddings to document chunks"""
        texts = [doc["text"] for doc in documents]
        embeddings = self.generate_embeddings(texts)
        
        for doc, embedding in zip(documents, embeddings):
            doc["embedding"] = embedding
        
        return documents


embedding_service = EmbeddingService()

