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
	pip install -e .

lint:
	flake8 wallet tests
	mypy wallet tests

test:
	py.test

test-all:
	tox -- --pg-image=postgres:alpine

build: clean-build
	python setup.py sdist

build-image: build
	docker build --build-arg app_version=`python setup.py --version` -t registry.clayman.pro/wallet .
	docker tag registry.clayman.pro/wallet registry.clayman.pro/wallet:`python setup.py --version`

publish-image:
	docker login -u $(DOCKER_USER) -p $(DOCKER_PASS) registry.clayman.pro
	docker push registry.clayman.pro/wallet
