FROM python:3.4

# Install required packages
RUN apt-get update -qq && apt-get -y install curl supervisor

# Update pip
RUN pip install --upgrade pip

# Install Consul-Template
ENV CT_URL https://github.com/hashicorp/consul-template/releases/download/v0.9.0/consul-template_0.9.0_linux_amd64.tar.gz
RUN curl -L $CT_URL | tar -C /usr/local/bin --strip-components 1 -zxf -

# Copy supervisor config
COPY supervisor.conf /etc/supervisor/conf.d/supervisord.conf

# Copy application config template
ADD config.yml /etc/consul-templates/config.yml

# Copy application package
COPY wallet-*.tar.gz /root/

# Install application package
RUN pip install /root/wallet-*.tar.gz

EXPOSE 5000

CMD ["/usr/bin/supervisord"]
