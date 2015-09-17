.PHONY: run tests dist

deps:
	python setup.py install

clean:
	rm -rf dist
	find . -name '*.egg' -exec rm -f {} \;
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;

dist:
	python setup.py sdist

clean-web:
	rm -rf assets/build

dist-web:
	cd assets && NODE_ENV=production webpack -p
	tar -czvf web.tar.gz assets/index.html assets/build/*
	mv web.tar.gz dist

run:
	wallet run --host=$(host)

tests:
	py.test -vv --cov wallet --cov-report html --cov-report xml tests
