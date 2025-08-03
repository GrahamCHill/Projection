from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import io
import json
import numpy as np
from typing import List, Optional
import logging

# Import our modules
from database import get_session, CVDocument
from storage import s3_storage
from vector_db import vector_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/integration", tags=["integration"])

# Helper function to generate a mock embedding
def generate_mock_embedding(text, dimension=1536):
    """
    Generate a mock embedding for demonstration purposes.
    In a real application, you would use a proper embedding model.
    """
    # Create a deterministic but unique embedding based on the text
    np.random.seed(hash(text) % 2**32)
    embedding = np.random.randn(dimension)
    # Normalize the embedding
    embedding = embedding / np.linalg.norm(embedding)
    return embedding.tolist()

@router.get("/status")
async def get_status():
    """
    Get the status of the integration services.
    """
    s3_status = "available" if s3_storage else "unavailable"
    vector_db_status = "available" if vector_db else "unavailable"
    
    return {
        "s3_storage": {
            "status": s3_status,
            "endpoint": s3_storage.endpoint_url if s3_storage else None,
            "mock_enabled": os.getenv("USE_MOCK_S3", "true").lower() == "true"
        },
        "vector_db": {
            "status": vector_db_status,
            "endpoint": os.getenv("VECTOR_DB_URL", "http://qdrant:6333") if vector_db else None,
            "document_count": vector_db.count_embeddings() if vector_db else 0
        }
    }

@router.post("/upload-cv")
async def upload_cv(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_session)
):
    """
    Upload a CV document, store it in S3, and create a vector embedding.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Store in database
        cv_doc = CVDocument(
            filename=file.filename,
            content=content.decode("utf-8") if isinstance(content, bytes) else content
        )
        db.add(cv_doc)
        db.commit()
        db.refresh(cv_doc)
        
        # Store in S3
        file_obj = io.BytesIO(content)
        object_name = f"cv_{cv_doc.id}_{file.filename}"
        s3_result = s3_storage.upload_fileobj(file_obj, object_name)
        
        if not s3_result:
            raise HTTPException(status_code=500, detail="Failed to upload file to S3")
        
        # Generate a presigned URL
        presigned_url = s3_storage.generate_presigned_url(object_name)
        
        # Create metadata
        metadata = {
            "id": cv_doc.id,
            "filename": file.filename,
            "title": title,
            "description": description,
            "s3_object_name": object_name,
            "created_at": cv_doc.created_at.isoformat() if hasattr(cv_doc.created_at, 'isoformat') else str(cv_doc.created_at)
        }
        
        # Generate mock embedding and store in vector database
        embedding = generate_mock_embedding(content.decode("utf-8") if isinstance(content, bytes) else content)
        vector_result = vector_db.store_embedding(str(cv_doc.id), embedding, metadata)
        
        if not vector_result:
            raise HTTPException(status_code=500, detail="Failed to store embedding in vector database")
        
        return {
            "message": "CV uploaded successfully",
            "document_id": cv_doc.id,
            "s3_object_name": object_name,
            "presigned_url": presigned_url,
            "vector_stored": True
        }
    
    except Exception as e:
        logger.error(f"Error uploading CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading CV: {str(e)}")

@router.get("/list-cvs")
async def list_cvs(limit: int = 100, offset: int = 0):
    """
    List CV documents stored in the vector database.
    """
    try:
        # Get documents from vector database
        documents = vector_db.list_embeddings(offset=offset, limit=limit)
        
        # Format the response
        result = []
        for doc in documents:
            metadata = doc.get('metadata', {})
            result.append({
                "id": doc.get('id'),
                "filename": metadata.get('filename'),
                "title": metadata.get('title'),
                "description": metadata.get('description'),
                "created_at": metadata.get('created_at')
            })
        
        return result
    
    except Exception as e:
        logger.error(f"Error listing CVs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing CVs: {str(e)}")

@router.get("/get-cv/{document_id}")
async def get_cv(document_id: str):
    """
    Get a CV document by ID.
    """
    try:
        # Get document from vector database
        doc = vector_db.get_embedding(document_id)
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        metadata = doc.get('metadata', {})
        s3_object_name = metadata.get('s3_object_name')
        
        # Generate a presigned URL
        presigned_url = s3_storage.generate_presigned_url(s3_object_name) if s3_object_name else None
        
        return {
            "id": doc.get('id'),
            "metadata": metadata,
            "presigned_url": presigned_url
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting CV: {str(e)}")

@router.post("/search-similar")
async def search_similar(query: str, limit: int = 10):
    """
    Search for similar CV documents based on a text query.
    """
    try:
        # Generate mock embedding for the query
        query_embedding = generate_mock_embedding(query)
        
        # Search for similar documents
        results = vector_db.search_similar(query_embedding, limit=limit)
        
        # Format the response
        formatted_results = []
        for result in results:
            metadata = result.get('metadata', {})
            s3_object_name = metadata.get('s3_object_name')
            
            # Generate a presigned URL
            presigned_url = s3_storage.generate_presigned_url(s3_object_name) if s3_object_name else None
            
            formatted_results.append({
                "id": result.get('id'),
                "score": result.get('score'),
                "metadata": metadata,
                "presigned_url": presigned_url
            })
        
        return formatted_results
    
    except Exception as e:
        logger.error(f"Error searching similar documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching similar documents: {str(e)}")

@router.delete("/delete-cv/{document_id}")
async def delete_cv(document_id: str, db: Session = Depends(get_session)):
    """
    Delete a CV document by ID.
    """
    try:
        # Get document from vector database
        doc = vector_db.get_embedding(document_id)
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        metadata = doc.get('metadata', {})
        s3_object_name = metadata.get('s3_object_name')
        
        # Delete from vector database
        vector_result = vector_db.delete_embedding(document_id)
        
        # Delete from S3
        s3_result = True
        if s3_object_name:
            s3_result = s3_storage.delete_object(s3_object_name)
        
        # Delete from database
        db_result = True
        try:
            db_id = int(document_id)
            db_doc = db.query(CVDocument).filter(CVDocument.id == db_id).first()
            if db_doc:
                db.delete(db_doc)
                db.commit()
        except:
            db_result = False
        
        return {
            "message": "CV deleted successfully",
            "vector_deleted": vector_result,
            "s3_deleted": s3_result,
            "db_deleted": db_result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting CV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting CV: {str(e)}")

@router.get("/toggle-mock-s3")
async def toggle_mock_s3():
    """
    Toggle between mock S3 and real S3.
    """
    try:
        current_value = os.getenv("USE_MOCK_S3", "true").lower() == "true"
        new_value = not current_value
        
        # In a real application, you would update the environment variable
        # and restart the application. For demonstration purposes, we'll
        # just return the current and new values.
        
        return {
            "current_value": current_value,
            "new_value": new_value,
            "message": "In a real application, you would need to update the .env file and restart the application to apply this change."
        }
    
    except Exception as e:
        logger.error(f"Error toggling mock S3: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error toggling mock S3: {str(e)}")