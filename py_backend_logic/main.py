from dotenv import load_dotenv
import os
from groq import Groq
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load the .env file
load_dotenv()

# Create FastAPI app
app = FastAPI(title="CV Quality Scanner API")

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

# This allows the file to be run directly with python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
