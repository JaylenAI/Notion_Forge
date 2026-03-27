.PHONY: dev dev-local test lint format build clean

# ========================================
# Docker 환경
# ========================================

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-build:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

build:
	docker compose build

down:
	docker compose down

# ========================================
# 로컬 환경 (uv + npm)
# ========================================

dev-backend:
	cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 9500 --reload

dev-frontend:
	cd frontend && npm run dev

install:
	cd backend && uv sync
	cd frontend && npm install

# ========================================
# 테스트
# ========================================

test:
	cd backend && uv run pytest -v

test-unit:
	cd backend && uv run pytest tests/unit/ -v

test-integration:
	cd backend && uv run pytest tests/integration/ -v --timeout=30

test-cov:
	cd backend && uv run pytest --cov=app --cov-report=html
	@echo "커버리지 리포트: backend/htmlcov/index.html"

# ========================================
# 린트 & 포맷
# ========================================

lint:
	cd backend && uv run ruff check .
	cd frontend && npm run lint

format:
	cd backend && uv run ruff format .

# ========================================
# 정리
# ========================================

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage
