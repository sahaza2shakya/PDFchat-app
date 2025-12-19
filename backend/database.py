from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import settings
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MongoDBManager:
    def __init__(self):
        try:
            self.client = MongoClient(
                settings.mongodb_uri,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                tlsAllowInvalidCertificates=False,
                tlsCAFile=None  # Use system CA certificates
            )
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[settings.mongodb_database_name]
            self.collection: Collection = self.db[settings.mongodb_collection_name]
            self._ensure_vector_index()
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection error: {e}")
            # Try with SSL certificate verification disabled for development
            logger.warning("Retrying MongoDB connection with relaxed SSL settings...")
            try:
                self.client = MongoClient(
                    settings.mongodb_uri,
                    serverSelectionTimeoutMS=10000,
                    tlsAllowInvalidCertificates=True  # Allow invalid certs for development
                )
                self.client.admin.command('ping')
                self.db = self.client[settings.mongodb_database_name]
                self.collection: Collection = self.db[settings.mongodb_collection_name]
                self._ensure_vector_index()
                logger.info("MongoDB connected with relaxed SSL settings")
            except Exception as e2:
                logger.error(f"MongoDB connection failed even with relaxed SSL: {e2}")
                raise ConnectionError(f"Failed to connect to MongoDB: {e2}")
        except Exception as e:
            logger.error(f"Error initializing MongoDB: {e}")
            raise
    
    def _ensure_vector_index(self):
        """Create vector search index if it doesn't exist"""
        try:
            # Check if index exists
            indexes = self.collection.list_indexes()
            index_names = [idx['name'] for idx in indexes]
            
            if 'vector_index' not in index_names:
                # Create vector search index
                self.db.command({
                    "createSearchIndexes": settings.mongodb_collection_name,
                    "indexes": [
                        {
                            "name": "vector_index",
                            "definition": {
                              "fields": [
                        {
                            "type": "vector",
                            "path": "embedding",
                            "numDimensions": 1536,
                            "similarity": "cosine"
                        }
                    ]
                            }
                        }
                    ]
                })
                
                logger.info("Vector search index created")
        except Exception as e:
            logger.warning(f"Index creation may have failed (might already exist): {e}")
    
    def insert_documents(self, documents: List[Dict[str, Any]]):
        """Insert multiple document chunks with embeddings"""
        if documents:
            result = self.collection.insert_many(documents)
            logger.info(f"Inserted {len(result.inserted_ids)} documents")
            return result.inserted_ids
        return []
    
    def vector_search(self, query_embedding: List[float], limit: int = 5, pdf_id: str = None) -> List[Dict[str, Any]]:
        """Perform vector similarity search with optional PDF filtering"""
        # Build vector search stage without filter (filters need indexed fields)
        vector_search_stage = {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": query_embedding,
            "numCandidates": limit * 20 if pdf_id else limit * 10,  # Get more candidates if filtering
            "limit": limit * 3 if pdf_id else limit  # Get more results if we need to filter
        }
        
        pipeline = [
            {
                "$vectorSearch": vector_search_stage
            },
            {
                "$project": {
                    "text": 1,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        # If pdf_id is provided, filter after vector search
        if pdf_id:
            pipeline.append({
                "$match": {
                    "metadata.pdf_id": pdf_id
                }
            })
            # Limit again after filtering
            pipeline.append({
                "$limit": limit
            })
        
        results = list(self.collection.aggregate(pipeline))
        return results
    
    def get_documents_by_pdf_id(self, pdf_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific PDF"""
        return list(self.collection.find({"metadata.pdf_id": pdf_id}))
    
    def delete_documents_by_pdf_id(self, pdf_id: str):
        """Delete all chunks for a specific PDF"""
        result = self.collection.delete_many({"metadata.pdf_id": pdf_id})
        logger.info(f"Deleted {result.deleted_count} documents for PDF {pdf_id}")
        return result.deleted_count


# Global database manager instance (lazy initialization)
_db_manager = None

def get_db_manager():
    """Get or create database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = MongoDBManager()
    return _db_manager

# Create a simple class to maintain backward compatibility
class DBManagerProxy:
    def __getattr__(self, name):
        return getattr(get_db_manager(), name)

db_manager = DBManagerProxy()

