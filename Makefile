.PHONY: dev test lint format typecheck install docker-up docker-down clean

dev:
	uvicorn chiron.main:app --reload --port 8080

test:
	pytest tests/ -v --cov=chiron

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

typecheck:
	mypy src/chiron/

install:
	pip install -e '.[dev]'

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
