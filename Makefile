.PHONY: clean clean-test clean-pyc clean-build
NAME	:= ghcr.io/clayman-micro/wallet
VERSION ?= latest
HOST ?= 0.0.0.0
PORT ?= 5000


clean: clean-build clean-image clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-image:
	docker images -qf dangling=true | xargs docker rmi

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

lint:
	poetry run flake8 src/wallet tests
	poetry run mypy src/wallet tests

run:
	poetry run python3 -m wallet --debug server run --host=$(HOST) --port=$(PORT) -t develop

test:
	py.test

tests:
	tox -- --pg-host=$(POSTGRES_HOST) --pg-database=wallet_tests

build:
	docker build -t ${NAME} .
	docker tag ${NAME} ${NAME}:$(VERSION)

publish:
	docker login -u $(DOCKER_USER) -p $(DOCKER_PASS) ghcr.io
	docker push ${NAME}
