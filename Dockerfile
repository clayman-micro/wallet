FROM python:3.5

# Upgrade pip
RUN pip install --upgrade pip

# Copy application package
COPY dist/wallet-*.tar.gz /root/

# Copy application config
COPY conf/config.yml /root/config.yml

# Install application package
RUN pip install /root/wallet-*.tar.gz

EXPOSE 5000

ENTRYPOINT ["wallet", "--config=/root/config.yml"]

CMD ["run", "--host=0.0.0.0", "--port=5000"]