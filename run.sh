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

# Start the FastAPI server in the background
echo -e "${GREEN}Starting FastAPI server on http://localhost:5000${NC}"
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
echo -e "${GREEN}   Backend: http://localhost:5000${NC}"
echo -e "${GREEN}   Frontend: http://localhost:5173${NC}"
echo -e "${GREEN}   Press Ctrl+C to stop servers  ${NC}"
echo -e "${GREEN}=================================${NC}"

# Wait for user to press Ctrl+C
wait