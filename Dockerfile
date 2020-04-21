FROM python:3.8-alpine3.11 as build

RUN apk add --update --no-cache --quiet make libc-dev python3-dev libffi-dev linux-headers gcc g++ git postgresql-dev && \
    python3 -m pip install --no-cache-dir --quiet -U pip && \
    python3 -m pip install --no-cache-dir --quiet poetry

ADD . /app

WORKDIR /app

RUN poetry build


FROM python:3.8-alpine3.11

COPY --from=build /app/dist/*.whl .

RUN apk add --update --no-cache --quiet make libc-dev python3-dev libffi-dev linux-headers gcc g++ git postgresql-client && \
    python3 -m pip install --no-cache-dir --quiet -U pip && \
    python3 -m pip install --no-cache-dir --quiet *.whl && \
    mkdir -p /usr/share/wallet && \
    rm -f *.whl && \
    apk del --quiet make libc-dev libffi-dev python3-dev linux-headers gcc g++ git

ADD ./src/wallet/storage/sql /usr/share/wallet

EXPOSE 5000

ENTRYPOINT ["python3", "-m", "wallet"]

CMD ["--conf-dir", "/etc/wallet", "server", "run"]
