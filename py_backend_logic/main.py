import json
from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from groq import Groq
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn
from sqlalchemy.orm import Session

# Import database module
from database import init_db, get_session, get_db_type, CVDocument
# Import API key manager
from api_key_manager import GroqApiKeyManager
# Import integration API
try:
    from integration_api import router as integration_router
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False

# Import GitHub API
try:
    from github_api import router as github_router
    GITHUB_AVAILABLE = True
    # Try to import scheduler if available
    try:
        from github_scheduler import github_scheduler
        GITHUB_SCHEDULER_AVAILABLE = True
    except ImportError:
        GITHUB_SCHEDULER_AVAILABLE = False
except ImportError:
    GITHUB_AVAILABLE = False
    GITHUB_SCHEDULER_AVAILABLE = False

# Import Git LFS API
try:
    from git_lfs_api import router as git_lfs_router
    GIT_LFS_AVAILABLE = True
except ImportError:
    GIT_LFS_AVAILABLE = False

# Import Auth API
try:
    from auth_api import router as auth_router
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

# Load the .env file
load_dotenv()

# Initialize database
engine = init_db()
print(f"Database initialized with type: {get_db_type()}")

# Create FastAPI app
app = FastAPI(title="Projection API")
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the API key manager
api_key_manager = GroqApiKeyManager()
api_key = api_key_manager.get_api_key()

# Create the Groq client
client = Groq(api_key=api_key)

# Include integration router if available
if INTEGRATION_AVAILABLE:
    app.include_router(integration_router)
    print("Integration API routes loaded")

# Include GitHub router if available
if GITHUB_AVAILABLE:
    app.include_router(github_router)
    print("GitHub API routes loaded")
    
    # Start the GitHub polling scheduler if available
    if GITHUB_SCHEDULER_AVAILABLE:
        github_scheduler.start_polling()
        print("GitHub polling scheduler started")

# Include Git LFS router if available
if GIT_LFS_AVAILABLE:
    app.include_router(git_lfs_router)
    print("Git LFS API routes loaded")

# Include Auth router if available
if AUTH_AVAILABLE:
    app.include_router(auth_router)
    print("Authentication API routes loaded")

@app.get("/")
async def root():
    return {"message": "Projection API is running"}

@app.get("/api/test")
async def test_groq():
    # Use the API
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain why Groq is so fast."}
        ],
        model="llama3-70b-8192"
    )
    
    return {"response": response.choices[0].message.content}

@app.post("/save-json/{filename}")
async def save_json(filename: str, request: Request):
    data = await request.json()
    file_path = DATA_DIR / f"{filename}.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    return {"message": f"Saved {filename}.json"}

@app.get("/load-json/{filename}")
def load_json(filename: str):
    file_path = DATA_DIR / f"{filename}.json"
    if not file_path.exists():
        return JSONResponse(status_code=404, content={"error": "File not found"})
    with open(file_path) as f:
        data = json.load(f)
    return data

@app.get("/list-json")
def list_json_files():
    files = [f.name for f in DATA_DIR.glob("*.json")]
    return {"files": files}

# Import auth dependencies if available
if AUTH_AVAILABLE:
    from auth import get_current_user, has_permission, PermissionType, User

# Database API endpoints
@app.get("/api/db/info")
def get_db_info():
    """Get information about the current database configuration"""
    return {
        "db_type": get_db_type(),
        "status": "connected"
    }

@app.get("/api/groq/status")
def get_groq_api_status():
    """Get the status of the GROQ API key"""
    return {
        "api_key_defined": api_key_manager.is_api_key_defined()
    }

@app.post("/api/groq/reload")
def reload_groq_api_key():
    """Reload the GROQ API key from environment variables"""
    is_defined = api_key_manager.reload_api_key()
    global api_key, client
    api_key = api_key_manager.get_api_key()
    client = Groq(api_key=api_key)
    return {
        "api_key_defined": is_defined,
        "message": "GROQ API key reloaded and client updated"
    }

# CV Document endpoints with role-based access control
if AUTH_AVAILABLE:
    # Protected endpoints requiring authentication
    @app.post("/api/db/documents")
    def create_document(
        filename: str, 
        content: str, 
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        _: bool = Depends(has_permission("cv_document", PermissionType.ADD))
    ):
        """Create a new CV document in the database (requires cv_document add permission)"""
        doc = CVDocument(filename=filename, content=content, user_id=current_user.id)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @app.get("/api/db/documents")
    def list_documents(
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        _: bool = Depends(has_permission("cv_document", PermissionType.VIEW))
    ):
        """List all CV documents in the database (requires cv_document view permission)"""
        docs = db.query(CVDocument).all()
        return docs

    @app.get("/api/db/documents/{doc_id}")
    def get_document(
        doc_id: int, 
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        _: bool = Depends(has_permission("cv_document", PermissionType.VIEW))
    ):
        """Get a specific CV document by ID (requires cv_document view permission)"""
        doc = db.query(CVDocument).filter(CVDocument.id == doc_id).first()
        if not doc:
            return JSONResponse(status_code=404, content={"error": "Document not found"})
        return doc

    @app.delete("/api/db/documents/{doc_id}")
    def delete_document(
        doc_id: int, 
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
        _: bool = Depends(has_permission("cv_document", PermissionType.DELETE))
    ):
        """Delete a CV document by ID (requires cv_document delete permission)"""
        doc = db.query(CVDocument).filter(CVDocument.id == doc_id).first()
        if not doc:
            return JSONResponse(status_code=404, content={"error": "Document not found"})
        
        # Only allow users to delete their own documents unless they're an admin
        admin_roles = [role.name for role in current_user.user_roles]
        if doc.user_id != current_user.id and "admin" not in admin_roles:
            return JSONResponse(
                status_code=403, 
                content={"error": "You can only delete your own documents"}
            )
            
        db.delete(doc)
        db.commit()
        return {"message": f"Document {doc_id} deleted"}
else:
    # Unprotected endpoints if auth is not available
    @app.post("/api/db/documents")
    def create_document(filename: str, content: str, db: Session = Depends(get_session)):
        """Create a new CV document in the database"""
        doc = CVDocument(filename=filename, content=content)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @app.get("/api/db/documents")
    def list_documents(db: Session = Depends(get_session)):
        """List all CV documents in the database"""
        docs = db.query(CVDocument).all()
        return docs

    @app.get("/api/db/documents/{doc_id}")
    def get_document(doc_id: int, db: Session = Depends(get_session)):
        """Get a specific CV document by ID"""
        doc = db.query(CVDocument).filter(CVDocument.id == doc_id).first()
        if not doc:
            return JSONResponse(status_code=404, content={"error": "Document not found"})
        return doc

    @app.delete("/api/db/documents/{doc_id}")
    def delete_document(doc_id: int, db: Session = Depends(get_session)):
        """Delete a CV document by ID"""
        doc = db.query(CVDocument).filter(CVDocument.id == doc_id).first()
        if not doc:
            return JSONResponse(status_code=404, content={"error": "Document not found"})
        db.delete(doc)
        db.commit()
        return {"message": f"Document {doc_id} deleted"}

# This allows the file to be run directly with python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
