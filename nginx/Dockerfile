# Nginx base image
FROM nginx:latest

# Context required for nginx.conf
ARG FRONTEND_VM_IP
ARG BACKEND_VM_IP

# Copy the Nginx configuration file
COPY nginx.conf.template /etc/nginx/nginx.conf.template

# Copy env variables to the conf file
RUN bash -c envsubst < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

# Expose HTTP port
EXPOSE 80

# Start Nginx with environment variables
CMD ["nginx", "-g", "daemon off;"]