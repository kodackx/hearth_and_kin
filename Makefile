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
run:
	docker compose up --build
teardown:
	docker compose down