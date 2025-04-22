setup:
	@echo "Setting up the environment..."
	python3 -m venv venv
	@echo "Activating the virtual environment..."
	. venv/bin/activate
	@echo "Installing dependencies..."
	pip install -r requirements.txt

run:
	@echo "Starting FastAPI app..."
	uvicorn main:app --reload

migrate:
	@echo "Running DB migration (manual create_all)..."
	python3 -c 'from db import engine; from models import metadata; metadata.create_all(bind=engine)'