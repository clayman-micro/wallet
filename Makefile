.PHONY: build clean tests

NAME		:= ghcr.io/clayman-micro/wallet
VERSION		?= latest
HOST 		?= 0.0.0.0
PORT 		?= 5000

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr tests/coverage
	rm -f tests/coverage.xml

install: clean
	poetry install

format:
	poetry run ruff --select I --fix src/wallet tests
	poetry run ruff format src/wallet tests

check_mypy:
	@echo Check project with Mypy typechecker.
	poetry run mypy src/wallet tests

check_ruff:
	@echo Check project with Ruff linter.
	poetry run ruff --show-source --no-fix src/wallet tests

check_format:
	@echo Check formatting
	poetry run ruff format --check --diff src/wallet tests

lint: check_format check_ruff check_mypy

run:
	poetry run python3 -m wallet --debug server run --host=$(HOST) --port=$(PORT)

tests:
	poetry run pytest

build:
	docker build -t ${NAME} .
	docker tag ${NAME} ${NAME}:$(VERSION)

publish:
	docker login -u $(DOCKER_USER) -p $(DOCKER_PASS) ghcr.io
	docker push ${NAME}
