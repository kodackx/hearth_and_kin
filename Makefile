install:
	poetry install --no-root
build:
	docker build . -t hearthandkin.azurecr.io/hearthandkin
run:
	docker compose up --build
test:
	poetry run pytest
run: install
	poetry run gunicorn -c gunicorn_config.py -k uvicorn.workers.UvicornWorker src.main:app