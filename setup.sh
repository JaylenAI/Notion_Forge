#!/usr/bin/env bash
set -e

echo "========================================"
echo "  NotionForge Setup"
echo "========================================"
echo ""

# 1. Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[OK] .env created from .env.example"
    echo ""
    echo ">> Please edit .env and set your API keys:"
    echo "   - NOTION_TOKEN (required)"
    echo "   - NOTION_PARENT_PAGE_ID (required)"
    echo "   - GEMINI_API_KEY or OPENAI_API_KEY (at least one)"
    echo ""
    read -p "Press Enter after editing .env, or Ctrl+C to exit..."
else
    echo "[OK] .env already exists"
fi

# 2. Check Docker
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "[ERROR] Docker Compose is not available."
    exit 1
fi

echo "[OK] Docker detected"

# 3. Build and start
echo ""
echo "Building and starting NotionForge..."
docker compose up --build -d

# 4. Wait for backend health
echo "Waiting for backend to be ready..."
for i in $(seq 1 30); do
    if curl -s http://localhost:9500/health > /dev/null 2>&1; then
        echo "[OK] Backend is ready!"
        break
    fi
    sleep 2
done

echo ""
echo "========================================"
echo "  NotionForge is running!"
echo "  Frontend: http://localhost:9501"
echo "  Backend:  http://localhost:9500"
echo "========================================"

# 5. Open browser if possible
if command -v open &> /dev/null; then
    open http://localhost:9501
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:9501
fi
