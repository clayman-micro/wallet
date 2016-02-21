Wallet
==========

[![Circle CI](https://circleci.com/gh/clayman74/wallet/tree/master.svg?style=svg)](https://circleci.com/gh/clayman74/wallet/tree/master) [![Coverage Status](https://coveralls.io/repos/clayman74/wallet/badge.svg?branch=master&service=github)](https://coveralls.io/github/clayman74/wallet?branch=master)

Experimental project to learn how to use `asyncio`, `aiohttp` and some other stuffs.
Local development and production uses [Docker Toolbox](https://docs.docker.com/engine/installation/mac/)

Development
-----------

### Prepare virtual machine

    $ docker-machine create -d virtualbox default

### Prepare enviromnents
Create python virtual enviromnent and install dependencies

    $ pyvenv venv
    $ source venv/bin/activate
    (env) $ python setup.py install

### Development config
Before start develop, create `config.yml` in the root folder

    ---

    secret_key: 'secret'
    token_expire: '3600'
    access_log: '%a %s %Tf %b "%{Referrer}i" "%{User-Agent}i"'

    consul:
      host: 'consul'
      port: '8500'

    postgres:
      name: 'wallet'
      user: 'wallet'
      password: 'wallet'
      host: 'postgresql'
      port: '5432'

    sentry:
      dsn: ''

    logging:
      version: 1
      formatters:
        simple:
          format: '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
          datefmt: '%Y-%m-%d %H:%M:%S'
      handlers:
        console:
          class: logging.StreamHandler
          formatter: simple
          level: INFO
          stream: ext://sys.stdout
      loggers:
        aiohttp:
          handlers:
            - console
          level: INFO
        wallet:
          handlers:
            - console
          level: INFO

### Generate development ssl certificate

    $ cd web/conf/certs/develop && openssl req -newkey rsa:2048 -nodes -keyout wallet.key -x509 -days 365 -out wallet.crt -subj "/C=/ST=/L=/O=/CN=wallet.clayman.pro"

### Run app

    (env) $ APP_ADDRESS=<host address> CONSUL_HOST=<machine address> DB_HOST=<machine address> wallet --config=config.yml run --host=0.0.0.0

### Apply database migrations

    (env) $ DB_HOST=<machine address> wallet --config=config.yml db upgrade head

### Run tests

    (env) $ DB_HOST=<machine address> DB_NAME=wallet_tests python setup.py test -a "-vv tests"

Deploy
------
Before deploy, create `docker-compose.production.yml` in the root folder like this:

    version: '2'

    networks:
      backend:
        driver: bridge

    services:
      consul:
        image: progrium/consul
        container_name: consul
        networks:
          - backend
        command: -server -bootstrap
        restart: always

      web:
        image: clayman74/nginx
        container_name: web
        links:
          - consul
        networks:
          - backend
        ports:
          - "80:80"
          - "443:443"
        restart: 'no'
        volumes:
          - /etc/supervisor/conf.d:/etc/supervisor/conf.d
          - /etc/consul-templates:/etc/consul-templates
          - /etc/nginx/certs:/etc/nginx/certs
          - /var/www/:/var/www/

      postgres-data:
        restart: 'no'
        container_name: postgres-data
        image: postgres:9.4
        volumes:
          - /var/lib/postgres
        command: 'true'

      postgresql:
        container_name: postgresql
        image: postgres:9.4
        environment:
          POSTGRES_DB: wallet
          POSTGRES_USER: wallet
          POSTGRES_PASSWORD: 230101
          PGPASSWORD: 230101
        networks:
          - backend
        restart: always
        volumes_from:
          - postgres-data

      app:
        build: ./
        depends_on:
          - consul
          - web
          - postgresql
        environment:
          DB_HOST: postgresql
          DB_USER: wallet
          DB_PASSWORD: 230101
          DB_NAME: wallet
        networks:
          - backend
        stop_signal: SIGINT
        restart: 'no'

Put production ssl certificate and key into `web/conf/certs/production`
Then create remote machine and configure

    $ docker-machine create -d digitalocean --digitalocean-access-token=$DO_TOKEN production
    $ make prepare-remote machine=production
    $ make bootstrap
    $ make deploy-web machine=production

To deploy new application version

    $ make deploy

To backup database

    $ make backup

