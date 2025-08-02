#!/bin/bash
# Script to run the Projection with cross-platform support

# Source the architecture detection script
source ./set-arch.sh

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