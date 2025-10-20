#!/bin/bash
# Script to run the Projection with cross-platform support

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Source the architecture detection script
source "$ROOT_DIR/set-arch.sh"

# Load env vars from project root .env to mirror Compose and Podman behavior
if [ -f "$ROOT_DIR/.env" ]; then
  echo "Loading environment from .env at project root"
  set -a
  # shellcheck disable=SC1091
  . "$ROOT_DIR/.env"
  set +a
else
  echo ".env not found at project root. Using shell environment and defaults from docker-compose.yml."
fi

# Print banner
echo "====================================="
echo "Projection - Cross-Platform"
echo "====================================="
echo "Detected architecture: $ARCH"
echo "Using GOARCH=$GOARCH"
echo "====================================="

# Run docker-compose with the detected architecture
docker-compose up -d

echo "====================================="
echo "Services started successfully!"
echo "Frontend available at: http://localhost"
echo "Backend API available at: http://localhost:8000"
echo "Go Backend available at: http://localhost:8001"
echo "====================================="