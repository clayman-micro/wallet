FROM python:3.7-alpine3.8

ARG app_version

# Copy application distribution package
COPY dist/wallet-${app_version}.tar.gz /root/

# Install required packages
RUN apk add --update --no-cache make libc-dev python3-dev linux-headers gcc g++ postgresql-client && \
    pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir /root/wallet-${app_version}.tar.gz && \
    rm /root/wallet-${app_version}.tar.gz && \
    apk del make libc-dev python3-dev linux-headers gcc g++

RUN mkdir -p /usr/share/wallet && cp /usr/local/lib/python3.7/site-packages/wallet/storage/sql/* /usr/share/wallet

EXPOSE 5000

CMD ["wallet", "--config=/root/config.yml", "server", "run", "--host=0.0.0.0", "--consul"]
