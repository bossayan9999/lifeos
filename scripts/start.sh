#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "→ Starting LifeOS Backend..."
cd "$ROOT/backend"
if [ ! -d venv ]; then
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
else
  source venv/bin/activate
fi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "→ Starting LifeOS Frontend..."
cd "$ROOT/frontend"
if [ ! -d node_modules ]; then
  npm install
fi
npm run dev &
FRONTEND_PID=$!

echo ""
echo "LifeOS is running:"
echo "  Frontend → http://localhost:5173"
echo "  Backend  → http://localhost:8000"
echo "  API docs → http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
