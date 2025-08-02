# Dockerfile
FROM golang:1.20-alpine

# Accept GOARCH as build argument
ARG GOARCH
ENV GOARCH=${GOARCH}
ENV GOOS=linux
ENV CGO_ENABLED=0

# Install tools
RUN apk add --no-cache git git-lfs && git lfs install

WORKDIR /app

COPY go.mod ./
COPY . .

# Build the binary
RUN go build -o main .

EXPOSE 8001

CMD ["./main"]
