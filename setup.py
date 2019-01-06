import os

from setuptools import find_packages, setup


def static_files(path, prefix):
    for root, _, files in os.walk(path):
        paths = []
        for item in files:
            paths.append(os.path.join(root, item))
        yield (root.replace(path, prefix), paths)


project = "wallet"

setup(
    name=project,
    version="2.3.0",
    url="https://wallet.clayman.pro",
    license="MIT",
    author="Kirill Sumorokov",
    author_email="sumorokov.k@gmail.com",
    description="Personal finance service",
    packages=find_packages(exclude=["tests"]),
    zip_safe=True,
    include_package_data=True,
    data_files=[
        item
        for item in static_files("%s/storage/sql" % project, "usr/share/%s" % project)
    ],
    install_requires=[
        "aiodns==1.1.1",
        "aiohttp==3.5.1",
        "asyncpg==0.18.2",
        "attrs==18.2.0",
        "cchardet==2.1.4",
        "cerberus==1.2",
        "click==7.0",
        "pendulum==2.0.4",
        "prometheus_client==0.5.0",
        "pyyaml==4.2b4",
        "raven==6.10.0",
        "raven-aiohttp==0.7.0",
        "ujson==1.35",
        "uvloop==0.11.3",
    ],
    extras_require={
        "dev": [
            "flake8",
            "flake8-bugbear",
            "flake8-builtins-unleashed",
            "flake8-comprehensions",
            "flake8-import-order",
            "flake8-pytest",
            "flake8-print",
            "mypy",
            "faker",
            "pytest",
            "pytest-aiohttp",
            "pytest-postgres",
            "coverage",
            "coveralls",
            "requests",
        ]
    },
    entry_points="""
        [console_scripts]
        wallet=wallet.adapters.cli:cli
    """,
)
