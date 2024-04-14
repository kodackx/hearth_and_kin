install:
	poetry install --no-root
build:
	docker build . -t hearthandkin.azurecr.io/hearthandkin
docker-run: build
	docker compose up
push: build
	docker push hearthandkin.azurecr.io/hearthandkin
test:
	poetry run pytest
run: install
	gunicorn --bind 127.0.0.1:8000 -k uvicorn.workers.UvicornWorker src.main:app --reload