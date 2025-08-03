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

# Import logging and metrics systems
from core.logging_manager import get_logger, logging_manager
from core.metrics_manager import metrics_manager
from core.middleware import LoggingMiddleware, MetricsMiddleware
from plugins.plugin_system import plugin_manager

# Import database module
from core.database import init_db, get_session, get_db_type, CVDocument, User, Role, Permission, UserRole, RolePermission
# Import API key manager
from core.api_key_manager import GroqApiKeyManager

# Create logger
logger = get_logger("main")
# Import integration API
try:
    from api.integration_api import router as integration_router
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False

# Import GitHub API
try:
    from api.github_api import router as github_router
    GITHUB_AVAILABLE = True
    # Try to import scheduler if available
    try:
        from github.scheduler import github_scheduler
        GITHUB_SCHEDULER_AVAILABLE = True
    except ImportError:
        GITHUB_SCHEDULER_AVAILABLE = False
except ImportError:
    GITHUB_AVAILABLE = False
    GITHUB_SCHEDULER_AVAILABLE = False

# Import Git LFS API
try:
    from api.git_lfs_api import router as git_lfs_router
    GIT_LFS_AVAILABLE = True
except ImportError:
    GIT_LFS_AVAILABLE = False

# Import Auth API
try:
    from api.auth_api import router as auth_router
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

# Import Metrics API
try:
    from api.metrics_api import router as metrics_router
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

# Load the .env file
load_dotenv()

# Initialize database
engine = init_db()
logger.info(f"Database initialized with type: {get_db_type()}")

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

# Add logging middleware
app.add_middleware(
    LoggingMiddleware,
    exclude_paths=["/api/health", "/api/metrics"]
)

# Add metrics middleware
app.add_middleware(
    MetricsMiddleware,
    metrics_manager=metrics_manager,
    exclude_paths=["/api/health", "/api/metrics"]
)

# Initialize plugin system
logger.info("Initializing plugin system")
plugin_count = plugin_manager.load_and_initialize_plugins(app)
logger.info(f"Initialized {plugin_count} plugins")

# Initialize the API key manager
api_key_manager = GroqApiKeyManager()
api_key = api_key_manager.get_api_key()

# Create the Groq client
client = Groq(api_key=api_key)

# Include integration router if available
if INTEGRATION_AVAILABLE:
    app.include_router(integration_router)
    logger.info("Integration API routes loaded")

# Include GitHub router if available
if GITHUB_AVAILABLE:
    app.include_router(github_router)
    logger.info("GitHub API routes loaded")
    
    # Start the GitHub polling scheduler if available
    if GITHUB_SCHEDULER_AVAILABLE:
        github_scheduler.start_polling()
        logger.info("GitHub polling scheduler started")

# Include Git LFS router if available
if GIT_LFS_AVAILABLE:
    app.include_router(git_lfs_router)
    logger.info("Git LFS API routes loaded")

# Include Auth router if available
if AUTH_AVAILABLE:
    app.include_router(auth_router)
    logger.info("Authentication API routes loaded")

# Include Metrics router if available
if METRICS_AVAILABLE:
    app.include_router(metrics_router)
    logger.info("Metrics API routes loaded")

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
    from core.auth import get_current_user, has_permission, PermissionType, User

# Database API endpoints
@app.get("/api/db/info")
def get_db_info():
    """Get information about the current database configuration"""
    return {
        "db_type": get_db_type(),
        "status": "connected"
    }

@app.get("/api/db/query/{table_name}")
def query_database(
    request: Request,
    table_name: str,
    db: Session = Depends(get_session),
    limit: int = 100,
    offset: int = 0
):
    """
    Query the database with a simple filtering mechanism.
    
    Parameters:
    - table_name: The name of the table to query (users, roles, permissions, cv_documents)
    - limit: Maximum number of records to return (default: 100)
    - offset: Number of records to skip (default: 0)
    - Additional query parameters will be used as filters (e.g., ?id=1&name=test)
    
    Returns:
    - List of records matching the query
    - Metadata including total count and available filters
    """
    # Map table names to SQLAlchemy models
    table_map = {
        "users": User,
        "roles": Role,
        "permissions": Permission,
        "user_roles": UserRole,
        "role_permissions": RolePermission,
        "cv_documents": CVDocument
    }
    
    # Check if the requested table exists
    if table_name not in table_map:
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid table name. Available tables: {', '.join(table_map.keys())}"}
        )
    
    # Get the model class for the requested table
    model = table_map[table_name]
    
    # Start building the query
    query = db.query(model)
    
    # Get query parameters for filtering
    query_params = dict(request.query_params)
    
    # Remove pagination parameters from filters
    if 'limit' in query_params:
        del query_params['limit']
    if 'offset' in query_params:
        del query_params['offset']
    
    # Apply filters based on query parameters
    for key, value in query_params.items():
        # Check if the model has this attribute
        if hasattr(model, key):
            # Handle different filter types
            if value.lower() == 'null':
                query = query.filter(getattr(model, key) == None)
            elif value.lower() == 'not_null':
                query = query.filter(getattr(model, key) != None)
            elif value.startswith('like:'):
                # Support LIKE queries with like:pattern
                pattern = value[5:]
                query = query.filter(getattr(model, key).like(f"%{pattern}%"))
            elif value.startswith('gt:'):
                # Support greater than with gt:value
                try:
                    val = float(value[3:])
                    query = query.filter(getattr(model, key) > val)
                except ValueError:
                    pass
            elif value.startswith('lt:'):
                # Support less than with lt:value
                try:
                    val = float(value[3:])
                    query = query.filter(getattr(model, key) < val)
                except ValueError:
                    pass
            else:
                # Default exact match
                query = query.filter(getattr(model, key) == value)
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    # Execute the query and return results
    try:
        results = query.all()
        
        # Get column names for the model
        columns = [column.name for column in model.__table__.columns]
        
        return {
            "data": results,
            "metadata": {
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "available_filters": columns
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Database query error: {str(e)}"}
        )

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
