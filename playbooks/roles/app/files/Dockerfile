FROM python:3.4

# Install required packages
# RUN apg-get update -qq && apt-get -y install curl supervisor

# Copy application package
COPY wallet-*.tar.gz /root/

# Install application package
RUN pip install /root/wallet-*.tar.gz

EXPOSE 5000

CMD ["wallet", "run", "--host=0.0.0.0", "--port=5000"]
