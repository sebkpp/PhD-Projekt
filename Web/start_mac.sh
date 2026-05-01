#!/bin/bash

echo "============================================"
echo " VR Study Management - Starting App"
echo "============================================"
echo ""

if [ ! -f "Backend/.env" ]; then
    echo "[ERROR] Backend/.env not found. Run ./setup_mac.sh first."
    exit 1
fi

cleanup() {
    echo ""
    echo "Shutting down..."
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
    wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
    echo "Done."
}
trap cleanup EXIT INT TERM

echo "Starting backend on http://localhost:5000 ..."
uv run fastapi dev Backend/app.py &
BACKEND_PID=$!

echo "Starting frontend on http://localhost:5173 ..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Both services are running. Open http://localhost:5173 in your browser."
echo "Press Ctrl+C to stop."
echo ""

wait "$BACKEND_PID" "$FRONTEND_PID"
