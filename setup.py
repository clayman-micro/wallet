import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


project = 'wallet'
assets = '{project}/assets/build'.format(project=project)
package_assets = 'var/lib/{project}/assets'.format(project=project)
package_conf = 'usr/share/{project}'.format(project=project)


def static_files(path, prefix):
    for root, dir, files in os.walk(path):
        paths = []
        for item in files:
            paths.append(os.path.join(root, item))
        yield (root.replace(path, prefix), paths)

data_files = [item for item in static_files(assets, package_assets)]
data_files.extend([item for item in static_files('conf', package_conf)])


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name=project,
    version='0.0.1',
    url='',
    license='MIT',
    author='Kirill Sumorokov',
    author_email='clayman74@gmail.com',
    description='Aiohttp boilerplate project',

    zip_safe=False,
    include_package_data=True,

    packages=find_packages(exclude=['tests', ]),

    install_requires=[
        'Click==4.0',
        'aiohttp==0.16.3',
        'aiopg==0.7.0',
        'alembic==0.7.6',
        'aioredis==0.2.0',
        'cerberus==0.9.1',
        'itsdangerous==0.24',
        'marshmallow==2.0.0b4',
        'passlib == 1.6.2',
        'psycopg2==2.6',
        'raven==5.3.1',
        'ujson==1.33'
    ],

    data_files=data_files,

    tests_require=[
        'pytest==2.7.1',
        'pytest-cov==1.8.1'
    ],

    cmdclass={'test': PyTest},

    entry_points='''
        [console_scripts]
        wallet=wallet.cli:cli
    '''
)
