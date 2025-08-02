#!/bin/bash

# CV Quality Scanner - Run Script
# This script starts both the FastAPI backend and React frontend

# Set error handling
set -e

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print banner
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}   CV Quality Scanner Startup   ${NC}"
echo -e "${GREEN}=================================${NC}"

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check for required commands
if ! command_exists node; then
  echo -e "${YELLOW}Node.js is not installed. Please install Node.js to run the frontend.${NC}"
  exit 1
fi

if ! command_exists python3; then
  echo -e "${YELLOW}Python 3 is not installed. Please install Python 3 to run the backend.${NC}"
  exit 1
fi

# Start the backend server
echo -e "${GREEN}Starting FastAPI backend server...${NC}"
cd py_backend_logic

# Check if virtual environment exists, if not create it
if [ ! -d ".venv" ]; then
  echo -e "${YELLOW}Creating Python virtual environment...${NC}"
  python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
echo -e "${GREEN}Installing/updating Python dependencies...${NC}"
pip install -r requirements.txt

# Check if MinIO client is installed (for S3 storage)
if command_exists mc; then
  echo -e "${GREEN}MinIO client found. S3 storage will be available.${NC}"
else
  echo -e "${YELLOW}MinIO client not found. S3 storage features may not work properly.${NC}"
  echo -e "${YELLOW}Install MinIO client for full S3 functionality: https://min.io/docs/minio/linux/reference/minio-mc.html${NC}"
fi

# Check if Qdrant client dependencies are installed
if python3 -c "import qdrant_client" &>/dev/null; then
  echo -e "${GREEN}Qdrant client found. Vector database will be available.${NC}"
else
  echo -e "${YELLOW}Qdrant client not found. Vector database features may not work properly.${NC}"
  echo -e "${YELLOW}Install Qdrant client for full vector database functionality: pip install qdrant-client${NC}"
fi

# Check if GitHub API dependencies are installed
if python3 -c "import requests" &>/dev/null; then
  echo -e "${GREEN}GitHub API dependencies found. GitHub integration will be available.${NC}"
else
  echo -e "${YELLOW}GitHub API dependencies not found. GitHub integration may not work properly.${NC}"
  echo -e "${YELLOW}Install requests for full GitHub functionality: pip install requests${NC}"
fi

# Start the FastAPI server in the background
echo -e "${GREEN}Starting FastAPI server on http://localhost:8000${NC}"
python main.py &
BACKEND_PID=$!

# Go back to the root directory
cd ..

# Start the frontend
echo -e "${GREEN}Starting React frontend...${NC}"
cd react_frontend

# Install dependencies if needed
echo -e "${GREEN}Installing/updating Node.js dependencies...${NC}"
npm install

# Start the React development server
echo -e "${GREEN}Starting React development server on http://localhost:5173${NC}"
npm run dev &
FRONTEND_PID=$!

# Go back to the root directory
cd ..

# Function to handle script termination
cleanup() {
  echo -e "${GREEN}Shutting down servers...${NC}"
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  exit 0
}

# Register the cleanup function for script termination
trap cleanup SIGINT SIGTERM

echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}   Servers are now running!      ${NC}"
echo -e "${GREEN}   Backend: http://localhost:8000${NC}"
echo -e "${GREEN}   Frontend: http://localhost:5173${NC}"
echo -e "${GREEN}   Press Ctrl+C to stop servers  ${NC}"
echo -e "${GREEN}=================================${NC}"

# Wait for user to press Ctrl+C
wait