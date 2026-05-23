#!/bin/bash
# AETHER AI — Start all services
# Run this from the AetherAI directory

echo "=== AETHER AI Launch ==="
echo ""

# 1. Check ComfyUI
if curl -s http://127.0.0.1:8188/queue > /dev/null 2>&1; then
  echo "[OK] ComfyUI is running on port 8188"
else
  echo "[WARN] ComfyUI is not running. Start it with:"
  echo "  cd ~/Documents/comfy/ComfyUI && PYTHONHOME=\"\" PYTHONPATH=\"\" .venv/Scripts/python.exe main.py --listen 127.0.0.1 --port 8188 --lowvram"
  echo ""
fi

# 2. Start the backend API
echo "[STARTING] Aether API on port 8111..."
PYTHONHOME="" PYTHONPATH="" python app/backend/main.py &
API_PID=$!
echo "[API PID: $API_PID]"
sleep 2

# 3. Start the frontend dev server
echo "[STARTING] Aether Dashboard on port 3111..."
cd app/frontend
npm run dev &
FRONTEND_PID=$!
echo "[FRONTEND PID: $FRONTEND_PID]"

echo ""
echo "=== Ready ==="
echo "  Dashboard: http://localhost:3111"
echo "  API:       http://localhost:8111/docs"
echo "  ComfyUI:   http://localhost:8188"
echo ""
echo "Press Ctrl+C to stop all services"
trap "kill $API_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
