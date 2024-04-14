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
	poetry run gunicorn -c gunicorn_config.py -k uvicorn.workers.UvicornWorker src.main:app