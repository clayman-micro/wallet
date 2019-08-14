.PHONY: clean clean-test clean-pyc clean-build

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
	pipenv install --dev -e .

lint:
	pipenv run flake8 wallet tests
	pipenv run mypy wallet tests

test:
	py.test

test-all:
	tox -- --pg-image=postgres:11-alpine

build:
	docker build -t $(DOCKER_USER)/wallet .
	docker tag $(DOCKER_USER)/wallet $(DOCKER_USER)/wallet:$(TRAVIS_TAG)

publish:
	docker login -u $(DOCKER_USER) -p $(DOCKER_PASS)
	docker push $(DOCKER_USER)/wallet
