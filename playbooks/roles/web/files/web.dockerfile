FROM ubuntu:14.04.1

# Install nginx
RUN apt-get install -y --force-yes software-properties-common && \
    add-apt-repository ppa:nginx/stable && \
    apt-get update && \
    apt-get install -y --force-yes nginx

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Remove default site
RUN rm -f /etc/nginx/sites-enabled/default

EXPOSE 80 443

CMD ["/usr/sbin/nginx"]
