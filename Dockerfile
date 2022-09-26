FROM python:3.10-slim as build

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update && apt-get install -y -qq \
      build-essential python3-dev libffi-dev git > /dev/null && \
    python3 -m pip install --no-cache-dir --quiet -U pip && \
    python3 -m pip install --no-cache-dir --quiet poetry

ADD . /app

WORKDIR /app

RUN poetry build


FROM python:3.10-slim

COPY --from=build /app/dist/*.whl .

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update && apt-get install -y -qq \
      build-essential python3-dev libffi-dev git curl > /dev/null && \
    python3 -m pip install --no-cache-dir --quiet -U pip && \
    python3 -m pip install --no-cache-dir --quiet *.whl && \
    rm -f *.whl && \
    apt autoremove -y -qq > /dev/null

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=3s \
  CMD curl -f http://localhost:5000/-/health || exit 1

ENTRYPOINT ["python3", "-m", "wallet"]

CMD [ "server", "run", '--host=0.0.0.0' ]
