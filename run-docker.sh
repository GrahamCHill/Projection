#!/bin/bash

# CV Quality Scanner - Docker Run Script
# This script starts both the FastAPI backend and React frontend using Docker/Podman

# Set error handling
set -e

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print banner
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}   CV Quality Scanner Docker Startup    ${NC}"
echo -e "${GREEN}=========================================${NC}"

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check for Docker or Podman
if command_exists docker; then
  CONTAINER_ENGINE="docker"
elif command_exists podman; then
  CONTAINER_ENGINE="podman"
else
  echo -e "${YELLOW}Neither Docker nor Podman is installed. Please install one of them to continue.${NC}"
  exit 1
fi

echo -e "${GREEN}Using ${CONTAINER_ENGINE} as container engine${NC}"

# Check for docker-compose or podman-compose
if [ "$CONTAINER_ENGINE" = "docker" ] && command_exists docker-compose; then
  COMPOSE_CMD="docker-compose"
elif [ "$CONTAINER_ENGINE" = "podman" ] && command_exists podman-compose; then
  COMPOSE_CMD="podman-compose"
elif [ "$CONTAINER_ENGINE" = "podman" ] && command_exists podman; then
  echo -e "${YELLOW}podman-compose not found, falling back to 'podman play kube'${NC}"
  COMPOSE_CMD="podman-play"
else
  echo -e "${YELLOW}${CONTAINER_ENGINE}-compose not found. Please install it to continue.${NC}"
  exit 1
fi

# Check if .env file exists for GROQ_API_KEY
if [ ! -f "py_backend_logic/.env" ]; then
  echo -e "${YELLOW}.env file not found in py_backend_logic directory.${NC}"
  
  # Check if .env.example exists
  if [ -f "py_backend_logic/.env.example" ]; then
    echo -e "${YELLOW}Creating .env file from .env.example${NC}"
    cp py_backend_logic/.env.example py_backend_logic/.env
    echo -e "${YELLOW}Please edit py_backend_logic/.env to set your GROQ_API_KEY${NC}"
  else
    echo -e "${YELLOW}Creating empty .env file${NC}"
    echo "GROQ_API_KEY=" > py_backend_logic/.env
    echo -e "${YELLOW}Please edit py_backend_logic/.env to set your GROQ_API_KEY${NC}"
  fi
  
  # Give user a chance to edit the file
  read -p "Press Enter to continue after editing the .env file..."
fi

# Export environment variables from .env file
export $(grep -v '^#' py_backend_logic/.env | xargs)

# Start the containers
if [ "$COMPOSE_CMD" = "podman-play" ]; then
  echo -e "${GREEN}Converting docker-compose.yml to Kubernetes YAML...${NC}"
  $CONTAINER_ENGINE generate kube -f docker-compose.yml > pod.yaml
  echo -e "${GREEN}Starting containers with Podman...${NC}"
  $CONTAINER_ENGINE play kube pod.yaml
else
  echo -e "${GREEN}Building and starting containers...${NC}"
  $COMPOSE_CMD up --build -d
fi

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}   Containers are now running!          ${NC}"
echo -e "${GREEN}   Backend: http://localhost:5000       ${NC}"
echo -e "${GREEN}   Frontend: http://localhost:80        ${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}To stop the containers, run:            ${NC}"
if [ "$COMPOSE_CMD" = "podman-play" ]; then
  echo -e "${GREEN}   podman pod stop cv_scanner         ${NC}"
else
  echo -e "${GREEN}   ${COMPOSE_CMD} down                ${NC}"
fi
echo -e "${GREEN}=========================================${NC}"