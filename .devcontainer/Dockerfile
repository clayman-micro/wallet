ARG VARIANT="3"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

ENV TOX_WORK_DIR=/home/vscode/.tox

ENV CONSUL_HOST="consul.service.consul" \
    PASSPORT_HOST=https://passport.dev.clayman.pro \
    POSTGRES_HOST="postgres.service.consul" \
    POSTGRES_USER=wallet \
    POSTGRES_PASSWORD=wallet \
    POSTGRES_DATABASE=wallet

# Install required libraries
RUN python3 -m pip install -U pip && \
    python3 -m pip install poetry tox && \
    poetry config virtualenvs.create false

USER vscode

COPY pyproject.toml /home/vscode/pyproject.toml
COPY poetry.lock /home/vscode/poetry.lock

WORKDIR /home/vscode

# Preinstall required packages
RUN poetry config virtualenvs.create false && \
    sudo poetry install --no-root
