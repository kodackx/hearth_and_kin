install:
	poetry install --no-root
build:
	docker build . -t hearthandkin.azurecr.io/hearthandkin
run:
	docker compose up --build
test:
	poetry run pytest
push: 
	test
	build
	docker push hearthandkin.azurecr.io/hearthandkin
