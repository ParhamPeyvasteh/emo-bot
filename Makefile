.PHONY: install install-dev run test lint format clean

install:
	pip install -r requirements/base.txt

install-dev:
	pip install -r requirements/dev.txt
	pre-commit install

run:
	python src/main.py

test:
	pytest tests/

lint:
	ruff check src/

format:
	black src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +