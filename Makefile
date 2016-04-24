clean:
	rm -rf dist
	find . -name '*.egg' -exec rm -f {} \;
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;

build:
	python setup.py sdist
	docker-compose build app
	rm -rf dist

build-web:
	cd web && rm -R build && npm run-script build

run:
	DB_PASSWORD=wallet DEBUG=True wallet run --host=$(host)

tests:
	DB_NAME=wallet_test DB_PASSWORD=wallet py.test -vv --cov wallet tests

prepare-remote:
	docker-machine ssh $(machine) 'mkdir -p /etc/supervisor/conf.d'
	docker-machine scp conf/supervisor/wallet.conf $(machine):/etc/supervisor/conf.d

	docker-machine ssh $(machine) 'mkdir -p /etc/consul-templates'
	docker-machine scp conf/consul-templates/wallet.conf $(machine):/etc/consul-templates

	docker-machine ssh $(machine) 'mkdir -p /etc/nginx/certs/wallet'
	docker-machine scp conf/certs/production/wallet.crt $(machine):/etc/nginx/certs/wallet
	docker-machine scp conf/certs/production/wallet.key $(machine):/etc/nginx/certs/wallet

	docker-machine ssh $(machine) 'mkdir -p /var/www/wallet'

bootstrap:
	docker-compose -f docker-compose.production.yml up -d consul web postgresql
	docker-compose -f docker-compose.production.yml up -d app
	docker-compose -f docker-compose.production.yml run --rm app db upgrade head

deploy:
	docker-compose -f docker-compose.production.yml up -d --force-recreate --no-deps app

deploy-web:
	docker-machine ssh $(machine) 'rm -R /var/www/wallet/build'
	docker-machine scp -r web/build/ $(machine):/var/www/wallet

backup:
	docker-compose -f docker-compose.production.yml run --rm postgresql pg_dump -h postgresql -d wallet -U wallet | gzip > backups/`date +"%m-%d-%y"`.gz