#!/bin/bash
# Helper script to detect system architecture and set appropriate GOARCH environment variable

# Detect system architecture
ARCH=$(uname -m)

# Convert architecture to Go naming convention
if [ "$ARCH" = "x86_64" ]; then
    export GOARCH="amd64"
elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
    export GOARCH="arm64"
else
    echo "Warning: Unrecognized architecture: $ARCH"
    echo "Defaulting to amd64"
    export GOARCH="amd64"
fi

echo "Detected architecture: $ARCH"
echo "Set GOARCH=$GOARCH"

# Execute the command passed as arguments with the GOARCH environment variable set
exec "$@"