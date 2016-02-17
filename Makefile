clean:
	rm -rf dist
	find . -name '*.egg' -exec rm -f {} \;
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;

build:
	python setup.py sdist
	docker-compose build app

clean-web:
	rm -rf assets/build

dist-web:
	cd assets && NODE_ENV=production webpack -p
	tar -czvf web.tar.gz assets/build/*
	mv web.tar.gz dist

prepare-remote:
	docker-machine ssh $(machine) 'mkdir -p /etc/nginx/certs/wallet'
	docker-machine scp -r web/conf/certs $(machine):/etc/nginx/certs/wallet

run:
	DB_PASSWORD=wallet DEBUG=True wallet run --host=$(host)

tests:
	DB_NAME=wallet_test DB_PASSWORD=wallet py.test -vv --cov wallet tests
