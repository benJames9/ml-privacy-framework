# Nginx base image
FROM nginx:latest

# Context required for nginx.conf
ARG FRONTEND_VM_IP
ARG BACKEND_VM_IP

RUN echo "FRONTEND IP: $FRONTEND_VM_IP" && \
    echo "BACKEND_IP: $BACKEND_VM_IP"

# Copy the Nginx configuration file
COPY nginx.conf.template /etc/nginx/nginx.conf.template

# Expose HTTP port (currently 8080 for testing)
EXPOSE 80

# Start Nginx with environment variables
CMD ["bash", "-c", "envsubst < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && nginx -g 'daemon off;'"]