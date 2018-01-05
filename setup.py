import os
from setuptools import find_packages, setup


def static_files(path, prefix):
    for root, _, files in os.walk(path):
        paths = []
        for item in files:
            paths.append(os.path.join(root, item))
        yield (root.replace(path, prefix), paths)


project = 'wallet'

setup(
    name=project,
    version='2.0.0',
    url='https://wallet.clayman.pro',
    license='MIT',
    author='Kirill Sumorokov',
    author_email='sumorokov.k@gmail.com',
    description='Personal finance service',

    packages=find_packages(exclude=['tests']),

    zip_safe=True,
    include_package_data=True,

    data_files=[item for item in static_files(
        '%s/repositories/sql' % project, 'usr/share/%s' % project
    )],

    install_requires=[
        'aiohttp',
        'asyncpg',
        'cerberus',
        'click',
        'passlib',
        'pyjwt',
        'pyyaml',
        'raven',
        'raven-aiohttp',
        'ujson',
        'uvloop',
    ],

    extras_require={
        'develop': [
            'flake8',
            'flake8-builtins-unleashed',
            'flake8-bugbear',
            'flake8-comprehensions',
            'flake8-import-order',
            'flake8-mypy',
            'flake8-pytest'
        ]
    },

    entry_points='''
        [console_scripts]
        wallet=wallet.management.cli:cli
    '''
)
