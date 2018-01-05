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

test:
	py.test

test-all:
	tox

coverage:
	coverage erase
	coverage run -m py.test \
        --pg-image=postgres:alpine \
        --pg-reuse \
        --pg-name=db-cf2b8d1e-24d4-41a0-9e1e-88d2e4789a02 \
        -v tests
	coverage report -m
	coverage xml
	coverage html

build: clean-build
	python setup.py sdist

build-image: clean-image build
	docker build --build-arg app_version=`python setup.py --version` -t clayman74/wallet .
	docker tag clayman74/wallet clayman74/wallet:`python setup.py --version`

publish-image:
	docker login -u $(DOCKER_USER) -p $(DOCKER_PASS)
	docker push clayman74/wallet
