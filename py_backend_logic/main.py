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

# Load the .env file
load_dotenv()

# Initialize database
engine = init_db()
print(f"Database initialized with type: {get_db_type()}")

# Create FastAPI app
app = FastAPI(title="CV Quality Scanner API")
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

# Retrieve the API key
api_key = os.getenv("GROQ_API_KEY")

# Create the Groq client
client = Groq(api_key=api_key)

@app.get("/")
async def root():
    return {"message": "CV Quality Scanner API is running"}

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

# Database API endpoints
@app.get("/api/db/info")
def get_db_info():
    """Get information about the current database configuration"""
    return {
        "db_type": get_db_type(),
        "status": "connected"
    }

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
