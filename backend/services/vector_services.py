import os
import sys
from typing import List, Dict, Optional
import logging
from openai import OpenAI
import pinecone

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Handle vector database operations for semantic search
    """
    
    def __init__(self):
        """Initialize Pinecone and OpenAI clients"""
        try:
            # Initialize OpenAI for embeddings
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Initialize Pinecone
            pinecone.init(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENVIRONMENT
            )
            
            # Get or create index
            if settings.PINECONE_INDEX_NAME not in pinecone.list_indexes():
                logger.warning(f"Index {settings.PINECONE_INDEX_NAME} not found. Please create it in Pinecone dashboard.")
                self.index = None
            else:
                self.index = pinecone.Index(settings.PINECONE_INDEX_NAME)
                logger.info(f"Connected to Pinecone index: {settings.PINECONE_INDEX_NAME}")
                
        except Exception as e:
            logger.error(f"Error initializing VectorStore: {str(e)}")
            raise
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding vector for text using OpenAI
        
        Args:
            text: Text to create embedding for
            
        Returns:
            List of floats representing the embedding
        """
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",  # Cheaper and faster
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            raise
    
    def add_document(
        self, 
        doc_id: str, 
        text: str, 
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Add document to vector database
        
        Args:
            doc_id: Unique identifier for the document
            text: Document text content
            metadata: Optional metadata to store with document
            
        Returns:
            True if successful
        """
        try:
            if not self.index:
                logger.error("Pinecone index not initialized")
                return False
            
            # Create embedding
            embedding = self.create_embedding(text)
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            metadata["text"] = text[:1000]  # Store first 1000 chars for reference
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[{
                    "id": doc_id,
                    "values": embedding,
                    "metadata": metadata
                }]
            )
            
            logger.info(f"Added document {doc_id} to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            return False
    
    def search(
        self, 
        query: str, 
        top_k: int = 3,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Semantic search in vector database
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of matching documents with scores
        """
        try:
            if not self.index:
                logger.error("Pinecone index not initialized")
                return []
            
            # Create query embedding
            query_embedding = self.create_embedding(query)
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_metadata
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "id": match.id,
                    "score": float(match.score),
                    "text": match.metadata.get("text", ""),
                    "metadata": match.metadata
                })
            
            logger.info(f"Found {len(formatted_results)} results for query: {query[:50]}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete document from vector store
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful
        """
        try:
            if not self.index:
                return False
            
            self.index.delete(ids=[doc_id])
            logger.info(f"Deleted document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store
        
        Returns:
            Dictionary with stats
        """
        try:
            if not self.index:
                return {"error": "Index not initialized"}
            
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {"error": str(e)}

# Create singleton instance
vector_store = VectorStore()