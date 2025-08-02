import os
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Vector DB Configuration
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL", "http://qdrant:6333")
VECTOR_DIMENSION = 1536  # Default dimension for embeddings (e.g., OpenAI's text-embedding-ada-002)
COLLECTION_NAME = "cv_embeddings"

class VectorDatabase:
    """
    A class to handle vector database operations using Qdrant.
    """
    
    def __init__(self):
        """
        Initialize the Qdrant client and ensure the collection exists.
        """
        self.client = QdrantClient(url=VECTOR_DB_URL)
        self._ensure_collection_exists()
        logger.info(f"Connected to vector database at {VECTOR_DB_URL}")
    
    def _ensure_collection_exists(self):
        """
        Ensure the collection exists, creating it if necessary.
        """
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if COLLECTION_NAME not in collection_names:
            # Create the collection
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=VECTOR_DIMENSION,
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created collection {COLLECTION_NAME}")
        else:
            logger.info(f"Collection {COLLECTION_NAME} already exists")
    
    def store_embedding(self, document_id, embedding, metadata=None):
        """
        Store a document embedding in the vector database.
        
        Args:
            document_id (str): Unique identifier for the document
            embedding (list or numpy.ndarray): Vector embedding of the document
            metadata (dict, optional): Additional metadata for the document
            
        Returns:
            bool: True if embedding was stored successfully, else False
        """
        try:
            if metadata is None:
                metadata = {}
                
            # Convert embedding to list if it's a numpy array
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
                
            # Store the embedding
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    models.PointStruct(
                        id=document_id,
                        vector=embedding,
                        payload=metadata
                    )
                ]
            )
            logger.info(f"Stored embedding for document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing embedding: {str(e)}")
            return False
    
    def search_similar(self, query_embedding, limit=10, score_threshold=0.7):
        """
        Search for similar documents based on embedding.
        
        Args:
            query_embedding (list or numpy.ndarray): Query vector embedding
            limit (int, optional): Maximum number of results to return
            score_threshold (float, optional): Minimum similarity score threshold
            
        Returns:
            list: List of search results with document IDs, scores, and metadata
        """
        try:
            # Convert embedding to list if it's a numpy array
            if isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.tolist()
                
            # Search for similar embeddings
            search_results = self.client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format the results
            results = []
            for result in search_results:
                results.append({
                    'id': result.id,
                    'score': result.score,
                    'metadata': result.payload
                })
            
            return results
        except Exception as e:
            logger.error(f"Error searching similar documents: {str(e)}")
            return []
    
    def get_embedding(self, document_id):
        """
        Get a document embedding by ID.
        
        Args:
            document_id (str): Document ID
            
        Returns:
            dict: Document embedding and metadata
        """
        try:
            points = self.client.retrieve(
                collection_name=COLLECTION_NAME,
                ids=[document_id],
                with_vectors=True
            )
            
            if not points:
                return None
                
            point = points[0]
            return {
                'id': point.id,
                'embedding': point.vector,
                'metadata': point.payload
            }
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            return None
    
    def delete_embedding(self, document_id):
        """
        Delete a document embedding by ID.
        
        Args:
            document_id (str): Document ID
            
        Returns:
            bool: True if embedding was deleted successfully, else False
        """
        try:
            self.client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=models.PointIdsList(
                    points=[document_id]
                )
            )
            logger.info(f"Deleted embedding for document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting embedding: {str(e)}")
            return False
    
    def list_embeddings(self, offset=0, limit=100):
        """
        List document embeddings.
        
        Args:
            offset (int, optional): Pagination offset
            limit (int, optional): Maximum number of results to return
            
        Returns:
            list: List of document IDs and metadata
        """
        try:
            # Scroll through the collection
            scroll_results = self.client.scroll(
                collection_name=COLLECTION_NAME,
                limit=limit,
                offset=offset,
                with_vectors=False  # Don't include vectors to reduce payload size
            )
            
            # Format the results
            results = []
            for point in scroll_results[0]:
                results.append({
                    'id': point.id,
                    'metadata': point.payload
                })
            
            return results
        except Exception as e:
            logger.error(f"Error listing embeddings: {str(e)}")
            return []
    
    def count_embeddings(self):
        """
        Count the number of document embeddings.
        
        Returns:
            int: Number of document embeddings
        """
        try:
            collection_info = self.client.get_collection(collection_name=COLLECTION_NAME)
            return collection_info.vectors_count
        except Exception as e:
            logger.error(f"Error counting embeddings: {str(e)}")
            return 0

# Create a singleton instance
vector_db = VectorDatabase()