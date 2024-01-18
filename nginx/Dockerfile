# Nginx base image
FROM nginx:latest

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Expose HTTP port (currently 8080 for testing)
EXPOSE 8080

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]