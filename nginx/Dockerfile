# Nginx base image
FROM nginx:latest

# ARG variables are available during build
ARG FRONTEND_VM_IP
ARG BACKEND_VM_IP

# Copy the .env file
COPY .env /etc/nginx/.env

# Copy the Nginx configuration file
COPY nginx.conf.template /etc/nginx/nginx.conf.template

# Expose HTTP port (currently 8080 for testing)
EXPOSE 80

# Start Nginx with environment variables
CMD ["bash", "-c", "envsubst < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && nginx -g 'daemon off;'"]