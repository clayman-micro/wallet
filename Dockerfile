FROM python:3.5

# Upgrade pip
RUN pip install --upgrade pip

# Copy application package
COPY dist/wallet-*.tar.gz /root/

# Copy application package
COPY config.yml /root/config.yml

# Install application package
RUN pip install /root/wallet-*.tar.gz

EXPOSE 5000

CMD ["wallet", "--config=/root/config.yml", "run", "--host=0.0.0.0", "--port=5000"]