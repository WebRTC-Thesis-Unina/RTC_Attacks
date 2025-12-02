# Fonte: https://hub.docker.com/r/austinwenyz/vdo-ninja
# Specify the platform and use Alpine Linux
FROM --platform=linux/amd64 alpine:latest

# Install required packages: git, nginx, and openssl
RUN apk add --no-cache git nginx openssl

# Clone the VDO.Ninja source code
RUN git clone --branch v28.0 --single-branch https://github.com/steveseguin/vdo.ninja /usr/share/vdo.ninja

# Create directory for SSL certificates
RUN mkdir -p /etc/nginx/ssl

# Generate self-signed certificate
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=IT/ST=Lombardy/L=Milan/O=Dev/CN=localhost"

# Create nginx configuration directory
RUN mkdir -p /run/nginx

# Copy nginx configuration
COPY nginx.conf /etc/nginx/http.d/default.conf

# Set the working directory
WORKDIR /usr/share/vdo.ninja

# Expose HTTPS port
EXPOSE 8080

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]