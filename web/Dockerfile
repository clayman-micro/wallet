FROM ubuntu:14.04.1

ENV CT_VERSION=0.10.0
ENV CT_URL https://github.com/hashicorp/consul-template/releases/download/v${CT_VERSION}/consul-template_${CT_VERSION}_linux_amd64.tar.gz

# Install nginx
RUN apt-get install -y --force-yes software-properties-common && \
    add-apt-repository ppa:nginx/stable && \
    apt-get update && \
    apt-get install -y --force-yes nginx curl runit

# Copy nginx config
COPY conf/nginx.conf /etc/nginx/nginx.conf

COPY conf/nginx.service /etc/service/nginx/run
COPY conf/consul-template.service /etc/service/consul-template/run

COPY conf/wallet.conf /etc/consul-templates/wallet.conf

RUN curl -L $CT_URL | tar -C /usr/local/bin --strip-components 1 -zxf -

# Remove default site
RUN rm -f /etc/nginx/sites-enabled/default

EXPOSE 80 443

CMD ["/usr/bin/runsvdir", "/etc/service"]
