# Dockerfile
FROM golang:1.20-alpine

# Accept GOARCH as build argument with fallback to the build container's architecture
ARG GOARCH
ENV GOARCH=${GOARCH}
ENV GOOS=linux
# Disable CGO for better cross-platform compatibility
ENV CGO_ENABLED=0

# Print build information for debugging
RUN echo "Building for GOARCH=${GOARCH} GOOS=${GOOS}"

# Install tools
RUN apk add --no-cache git git-lfs && git lfs install

WORKDIR /app

COPY go.mod ./
COPY . .

# Build the binary
RUN go build -o main .

EXPOSE 8001

CMD ["./main"]
