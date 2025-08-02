# Use an official Go runtime as a parent image
FROM golang:1.20-alpine

# Install git and git-lfs
RUN apk add --no-cache git git-lfs

# Initialize git-lfs
RUN git lfs install

# Set working directory
WORKDIR /app

# Copy go.mod and go.sum
COPY go.mod ./

# Copy the source code
COPY . .

# Build the Go app with CGO disabled for better compatibility
ENV CGO_ENABLED=0
# Build for the same architecture as the container
ENV GOOS=linux
RUN go build -o main .

# Expose the port the app runs on
EXPOSE 8001

# Command to run the application
CMD ["./main"]