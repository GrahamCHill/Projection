#!/usr/bin/env bash
set -euo pipefail

# Equivalent Podman orchestration for docker-compose.yml
# Usage:
#   ./run-podman.sh up       # build images (if needed) and start containers
#   ./run-podman.sh down     # stop and remove containers, keep named volumes
#   ./run-podman.sh logs [service]
#   ./run-podman.sh rebuild  # rebuild images
#
# Notes:
# - Requires Podman >= 4.x
# - Designed for rootless Podman; run as your normal user
# - Reads environment overrides from .env at project root if present

PROJECT_NAME="projection"
NETWORK_NAME="projection_network"

# Image tags
IMG_BACKEND="${PROJECT_NAME}_backend:local"
IMG_GO_BACKEND="${PROJECT_NAME}_go_backend:local"
IMG_FRONTEND="${PROJECT_NAME}_frontend:local"

# Container names (match docker-compose for familiarity)
CTR_BACKEND="projection_backend"
CTR_GO_BACKEND="projection_go_backend"
CTR_FRONTEND="projection_frontend"
CTR_POSTGRES="projection_postgres"
CTR_MINIO="projection_minio"
CTR_QDRANT="projection_qdrant"
CTR_REDIS="projection_redis"

# Named volumes (match docker-compose)
VOL_POSTGRES="postgres_data"
VOL_MINIO="minio_data"
VOL_QDRANT="qdrant_data"
VOL_REDIS="redis_data"

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Load .env if provided to supply variables similar to docker compose
load_env() {
  if [[ -f "$ROOT_DIR/.env" ]]; then
    echo "Loading environment from .env at project root"
    set -a
    # shellcheck disable=SC1091
    . "$ROOT_DIR/.env"
    set +a
  fi
}

ensure_podman() {
  if ! command -v podman >/dev/null 2>&1; then
    echo "Error: podman not found in PATH" >&2
    exit 1
  fi
}

ensure_network() {
  if ! podman network inspect "$NETWORK_NAME" >/dev/null 2>&1; then
    podman network create "$NETWORK_NAME" >/dev/null
    echo "Created network: $NETWORK_NAME"
  fi
}

ensure_volumes() {
  for v in "$VOL_POSTGRES" "$VOL_MINIO" "$VOL_QDRANT" "$VOL_REDIS"; do
    if ! podman volume inspect "$v" >/dev/null 2>&1; then
      podman volume create "$v" >/dev/null
      echo "Created volume: $v"
    fi
  done
}

build_images() {
  echo "Building backend image: $IMG_BACKEND"
  podman build -t "$IMG_BACKEND" -f "$ROOT_DIR/py_backend_logic/Dockerfile" "$ROOT_DIR/py_backend_logic"

  echo "Building Go backend image: $IMG_GO_BACKEND"
  # Pass through GOARCH if set in environment
  if [[ -n "${GOARCH:-}" ]]; then
    podman build --build-arg GOARCH="$GOARCH" -t "$IMG_GO_BACKEND" -f "$ROOT_DIR/go_backend/Dockerfile" "$ROOT_DIR/go_backend"
  else
    podman build -t "$IMG_GO_BACKEND" -f "$ROOT_DIR/go_backend/Dockerfile" "$ROOT_DIR/go_backend"
  fi

  echo "Building frontend image: $IMG_FRONTEND"
  podman build -t "$IMG_FRONTEND" -f "$ROOT_DIR/react_frontend/Dockerfile" "$ROOT_DIR/react_frontend"
}

stop_remove_if_exists() {
  local name=$1
  if podman ps -a --format '{{.Names}}' | grep -q "^${name}$"; then
    echo "Stopping $name (if running)"
    podman stop "$name" >/dev/null 2>&1 || true
    echo "Removing $name"
    podman rm "$name" >/dev/null 2>&1 || true
  fi
}

run_databases() {
  # Postgres
  stop_remove_if_exists "$CTR_POSTGRES"
  podman run -d \
    --name "$CTR_POSTGRES" \
    --network "$NETWORK_NAME" \
    --restart unless-stopped \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD="${DB_PASSWORD:-password}" \
    -e POSTGRES_USER="${DB_USER:-postgres}" \
    -e POSTGRES_DB="${DB_NAME:-projection}" \
    --volume "$VOL_POSTGRES:/var/lib/postgresql/data:Z" \
    --health-cmd 'pg_isready -U postgres' \
    --health-interval 10s \
    --health-timeout 5s \
    --health-retries 5 \
    docker.io/library/postgres:15

  # MinIO
  stop_remove_if_exists "$CTR_MINIO"
  podman run -d \
    --name "$CTR_MINIO" \
    --network "$NETWORK_NAME" \
    --restart unless-stopped \
    -p 9000:9000 \
    -p 9001:9001 \
    -e MINIO_ROOT_USER=minioadmin \
    -e MINIO_ROOT_PASSWORD=minioadmin \
    --volume "$VOL_MINIO:/data:Z" \
    --health-cmd "curl -f http://localhost:9000/minio/health/live || exit 1" \
    --health-interval 30s \
    --health-timeout 20s \
    --health-retries 3 \
    docker.io/minio/minio:latest \
    server /data --console-address ":9001"

  # Qdrant
  stop_remove_if_exists "$CTR_QDRANT"
  podman run -d \
    --name "$CTR_QDRANT" \
    --network "$NETWORK_NAME" \
    --restart unless-stopped \
    -p 6333:6333 \
    -p 6334:6334 \
    --volume "$VOL_QDRANT:/qdrant/storage:Z" \
    --health-cmd "curl -f http://localhost:6333/health || exit 1" \
    --health-interval 30s \
    --health-timeout 20s \
    --health-retries 3 \
    docker.io/qdrant/qdrant:latest

  # Redis
  stop_remove_if_exists "$CTR_REDIS"
  podman run -d \
    --name "$CTR_REDIS" \
    --network "$NETWORK_NAME" \
    --restart unless-stopped \
    -p 6379:6379 \
    --volume "$VOL_REDIS:/data:Z" \
    --health-cmd "redis-cli ping" \
    --health-interval 30s \
    --health-timeout 10s \
    --health-retries 3 \
    docker.io/library/redis:alpine
}

wait_for_health() {
  local name=$1
  local timeout=${2:-120}
  echo "Waiting for $name to be healthy (timeout ${timeout}s) ..."
  local start=$(date +%s)
  while true; do
    if podman healthcheck run "$name" >/dev/null 2>&1; then
      echo "$name is healthy"
      break
    fi
    sleep 2
    local now=$(date +%s)
    if (( now - start > timeout )); then
      echo "Timed out waiting for $name to be healthy" >&2
      podman logs "$name" || true
      exit 1
    fi
  done
}

run_backends_and_frontend() {
  # Go backend
  stop_remove_if_exists "$CTR_GO_BACKEND"
  podman run -d \
    --name "$CTR_GO_BACKEND" \
    --network "$NETWORK_NAME" \
    --restart unless-stopped \
    -p 8001:8001 \
    -e GITHUB_TOKEN="${GITHUB_TOKEN:-}" \
    "$IMG_GO_BACKEND"

  # Python backend
  stop_remove_if_exists "$CTR_BACKEND"
  podman run -d \
    --name "$CTR_BACKEND" \
    --network "$NETWORK_NAME" \
    --restart unless-stopped \
    -p 8000:8000 \
    -e GROQ_API_KEY="${GROQ_API_KEY:-}" \
    -e DB_HOST="${DB_HOST:-postgres}" \
    -e DB_PORT="${DB_PORT:-5432}" \
    -e DB_USER="${DB_USER:-postgres}" \
    -e DB_PASSWORD="${DB_PASSWORD:-password}" \
    -e DB_NAME="${DB_NAME:-projection}" \
    -e S3_ENDPOINT="${S3_ENDPOINT:-http://minio:9000}" \
    -e S3_ACCESS_KEY="${S3_ACCESS_KEY:-minioadmin}" \
    -e S3_SECRET_KEY="${S3_SECRET_KEY:-minioadmin}" \
    -e S3_BUCKET_NAME="${S3_BUCKET_NAME:-projection-documents}" \
    -e USE_MOCK_S3="${USE_MOCK_S3:-true}" \
    -e VECTOR_DB_URL="${VECTOR_DB_URL:-http://qdrant:6333}" \
    -e GO_BACKEND_URL="${GO_BACKEND_URL:-http://go_backend:8001}" \
    -e GITHUB_TOKEN="${GITHUB_TOKEN:-}" \
    -e REDIS_ENABLED="${REDIS_ENABLED:-false}" \
    -e REDIS_HOST="${REDIS_HOST:-redis}" \
    -e REDIS_PORT="${REDIS_PORT:-6379}" \
    -e REDIS_DB="${REDIS_DB:-0}" \
    -e REDIS_PASSWORD="${REDIS_PASSWORD:-}" \
    -e JWT_SECRET_KEY="${JWT_SECRET_KEY:-your-secret-key-for-jwt}" \
    -e ACCESS_TOKEN_EXPIRE_MINUTES="${ACCESS_TOKEN_EXPIRE_MINUTES:-30}" \
    -e LOG_LEVEL="${LOG_LEVEL:-INFO}" \
    -e CONSOLE_LOG_LEVEL="${CONSOLE_LOG_LEVEL:-INFO}" \
    -e FILE_LOG_LEVEL="${FILE_LOG_LEVEL:-DEBUG}" \
    -e LOG_DIR="${LOG_DIR:-logs}" \
    -e MAX_LOG_SIZE_MB="${MAX_LOG_SIZE_MB:-10}" \
    -e LOG_BACKUP_COUNT="${LOG_BACKUP_COUNT:-5}" \
    -e METRICS_ENABLED="${METRICS_ENABLED:-true}" \
    -e METRICS_RETENTION_MINUTES="${METRICS_RETENTION_MINUTES:-60}" \
    -e METRICS_SNAPSHOT_INTERVAL_SECONDS="${METRICS_SNAPSHOT_INTERVAL_SECONDS:-60}" \
    -e METRICS_DIR="${METRICS_DIR:-metrics}" \
    -e PLUGINS_ENABLED="${PLUGINS_ENABLED:-true}" \
    -e PLUGINS_DIR="${PLUGINS_DIR:-plugins}" \
    -e PLUGIN_CONFIG_FILE="${PLUGIN_CONFIG_FILE:-plugin_config.json}" \
    -v "$ROOT_DIR/py_backend_logic:/app:Z" \
    -v "$ROOT_DIR/logs:/app/logs:Z" \
    -v "$ROOT_DIR/metrics:/app/metrics:Z" \
    -v "$ROOT_DIR/plugins:/app/plugins:Z" \
    "$IMG_BACKEND"

  # Frontend
  stop_remove_if_exists "$CTR_FRONTEND"
  podman run -d \
    --name "$CTR_FRONTEND" \
    --network "$NETWORK_NAME" \
    --restart unless-stopped \
    -p 80:80 \
    "$IMG_FRONTEND"
}

cmd_up() {
  ensure_podman
  load_env
  ensure_network
  ensure_volumes
  # Build images only if missing
  if ! podman image exists "$IMG_BACKEND" || ! podman image exists "$IMG_GO_BACKEND" || ! podman image exists "$IMG_FRONTEND"; then
    build_images
  fi
  run_databases
  # Optionally wait for core deps
  wait_for_health "$CTR_POSTGRES" 120
  wait_for_health "$CTR_MINIO" 180
  wait_for_health "$CTR_QDRANT" 180
  wait_for_health "$CTR_REDIS" 120
  run_backends_and_frontend
  echo "All services started."
}

cmd_down() {
  ensure_podman
  for c in "$CTR_FRONTEND" "$CTR_BACKEND" "$CTR_GO_BACKEND" "$CTR_REDIS" "$CTR_QDRANT" "$CTR_MINIO" "$CTR_POSTGRES"; do
    if podman ps -a --format '{{.Names}}' | grep -q "^${c}$"; then
      podman stop "$c" >/dev/null 2>&1 || true
      podman rm "$c" >/dev/null 2>&1 || true
      echo "Removed $c"
    fi
  done
  echo "Containers removed. Volumes ($VOL_POSTGRES, $VOL_MINIO, $VOL_QDRANT, $VOL_REDIS) were kept."
}

cmd_logs() {
  ensure_podman
  local svc=${1:-}
  local name
  case "$svc" in
    backend) name="$CTR_BACKEND";;
    go_backend|go) name="$CTR_GO_BACKEND";;
    frontend) name="$CTR_FRONTEND";;
    postgres|db) name="$CTR_POSTGRES";;
    minio) name="$CTR_MINIO";;
    qdrant) name="$CTR_QDRANT";;
    redis) name="$CTR_REDIS";;
    "") echo "Specify a service (backend|go_backend|frontend|postgres|minio|qdrant|redis)"; return 1;;
    *) name="$svc";;
  esac
  podman logs -f "$name"
}

cmd_rebuild() {
  ensure_podman
  build_images
}

main() {
  case "${1:-up}" in
    up) shift || true; cmd_up "$@" ;;
    down) shift || true; cmd_down "$@" ;;
    logs) shift || true; cmd_logs "$@" ;;
    rebuild) shift || true; cmd_rebuild "$@" ;;
    *) echo "Usage: $0 {up|down|logs [service]|rebuild}"; exit 1 ;;
  esac
}

main "$@"
