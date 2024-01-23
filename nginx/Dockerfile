# Nginx base image
FROM nginx:latest

# Copy the Nginx configuration file
COPY nginx.conf.template /etc/nginx/nginx.conf.template

# Expose HTTP port (currently 8080 for testing)
EXPOSE 80

# Start Nginx with environment variables
CMD ["bash", "-c", "envsubst < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf && nginx -g 'daemon off;'"]