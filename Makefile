install:
	poetry install --no-root
build:
	docker build . -t sjoeborg/hearthandkin:latest
test:
	poetry run pytest
push: 
	make install
	make test
	make build
	docker push sjoeborg/hearthandkin:latest
docker-run:
	make install
	make test
	make build
	docker compose up
teardown:
	docker compose down
run:
	poetry run uvicorn --host 127.0.0.1 src.main:app --reload