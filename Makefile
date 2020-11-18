.PHONY: clean clean-test clean-pyc clean-build
NAME	:= ghcr.io/clayman-micro/wallet
VERSION ?= latest


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
	poetry run flake8 wallet tests
	poetry run mypy wallet tests

run:
	poetry run python3 -m wallet --debug server run -t develop

test:
	py.test

test-all:
	tox -- --pg-image=postgres:11-alpine

build:
	docker build -t ${NAME} .
	docker tag ${NAME} ${NAME}:$(VERSION)

publish:
	docker login -u $(DOCKER_USER) -p $(DOCKER_PASS) ghcr.io
	docker push ${NAME}
