from dotenv import load_dotenv
import os
from groq import Groq
import fastapi

# Load the .env file
load_dotenv()

# Retrieve the API key
api_key = os.getenv("GROQ_API_KEY")

# Create the Groq client
client = Groq(api_key=api_key)

# Use the API
response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain why Groq is so fast."}
    ],
    model="llama3-70b-8192"
)

print(response.choices[0].message.content)
