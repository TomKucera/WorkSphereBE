#!/usr/bin/env bash

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$PROJECT_DIR"

echo "Activating virtual environment..."
source .venv/bin/activate

# Load .env variables if exists
if [ -f ".env" ]; then
  echo "Loading environment variables from .env..."
  export $(grep -v '^#' .env | xargs)
fi

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
APP_MODULE=${APP_MODULE:-app.main:app}

echo "Starting FastAPI app..."
echo "URL: http://$HOST:$PORT"
echo ""

exec uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT" --reload
