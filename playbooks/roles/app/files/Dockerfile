FROM python:3.4

# Update pip
RUN pip install --upgrade pip

# Copy application config
COPY config.yml /root/config.yml

# Copy application package
COPY wallet-*.tar.gz /root/

# Install application package
RUN pip install /root/wallet-*.tar.gz

EXPOSE 5000

CMD ["wallet", "--config=/root/config.yml", "run", "--host=0.0.0.0", "--port=5000"]
