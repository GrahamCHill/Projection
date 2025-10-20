#!/bin/bash

# Projection - Docker Run Script
# This script starts the application using Docker Compose

# Set error handling
set -e

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Print banner
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}        Projection Docker        ${NC}"
echo -e "${GREEN}=================================${NC}"

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check for required commands
if ! command_exists docker; then
  echo -e "${YELLOW}Docker is not installed. Please install Docker to run the application.${NC}"
  exit 1
fi

if ! command_exists docker-compose; then
  echo -e "${YELLOW}Docker Compose is not installed. Please install Docker Compose to run the application.${NC}"
  exit 1
fi

# Load env vars from project root .env to mirror Compose and Podman behavior
if [ -f "$ROOT_DIR/.env" ]; then
  echo -e "${GREEN}Loading environment from .env at project root${NC}"
  set -a
  # shellcheck disable=SC1091
  . "$ROOT_DIR/.env"
  set +a
else
  echo -e "${YELLOW}.env not found at project root. Using shell environment and defaults from docker-compose.yml.${NC}"
fi

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
  echo -e "${YELLOW}No GitHub token found in environment. GitHub operations may be limited.${NC}"
  echo -e "${YELLOW}Set the GITHUB_TOKEN environment variable for full GitHub functionality.${NC}"
else
  echo -e "${GREEN}GitHub token found in environment. GitHub operations will be available.${NC}"
fi

# Start the Docker containers
echo -e "${GREEN}Starting Docker containers...${NC}"
docker-compose up -d

# Show container status
echo -e "${GREEN}Container status:${NC}"
docker-compose ps

echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}   Servers are now running!      ${NC}"
echo -e "${GREEN}   Backend: http://localhost:8000${NC}"
echo -e "${GREEN}   Git LFS: http://localhost:8001${NC}"
echo -e "${GREEN}   Frontend: http://localhost:80 ${NC}"
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}To stop the containers, run:     ${NC}"
echo -e "${GREEN}   docker-compose down           ${NC}"
echo -e "${GREEN}=================================${NC}"