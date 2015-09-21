Wallet
==========

[![Circle CI](https://circleci.com/gh/clayman74/wallet/tree/master.svg?style=svg)](https://circleci.com/gh/clayman74/wallet/tree/master) [![Coverage Status](https://coveralls.io/repos/clayman74/wallet/badge.svg?branch=master&service=github)](https://coveralls.io/github/clayman74/wallet?branch=master)

Experimental project to learn how to use `asyncio`, `aiohttp` and some other stuffs.

Development
-----------

### Prepare virtual machine

    $ vagrant up

### Prepare enviromnents
Create python virtual enviromnent and install dependencies

    $ pyvenv venv
    $ source venv/bin/activate
    (env) $ python setup.py install

### Development config
Before start develop, create `config.yml` in the root folder

    ---

    project_name: <project_name>
    project_domain: <project_domain>

    secret_key: 'top-secret'
    token_expires: 3600

    sqlalchemy_dsn: 'postgres://<user>:<password>@<host>:<port>/<name>'

Similar `testing.yml` config should be created before running tests

### Run app

    (env) $ wallet --config=config.yml run

### Apply database migrations

    (env) $ wallet --config=config.yml db upgrade head

### Run tests

    (env) $ python setup.py test -a "-vv tests"

Deploy
------
Create inventory file for ansible `playbooks/inventory` before deploy to production

    [wallet]
    wallet ansible_ssh_host=clayman.pro ansible_ssh_user=clayman

    [wallet:vars]
    common_user=clayman
    common_user_password=<common user password>

    project_branch=master
    project_user=clayman
    project_socket=127.0.0.1:5000

    project_db_password='<top secret password>'

    secret_key='<top secret key>'

    cluster_environment=False

After that, execute

    ansible-playbook -i playbooks/inventory playbooks/bootstrap.yml --ask-sudo
