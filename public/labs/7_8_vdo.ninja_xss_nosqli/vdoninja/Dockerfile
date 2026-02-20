# Fonte: https://hub.docker.com/r/austinwenyz/vdo-ninja
# Specify the platform and use Alpine Linux
FROM --platform=linux/amd64 alpine:latest

# Install required packages: git, nginx
RUN apk add --no-cache git nginx

# Clone the VDO.Ninja source code
RUN git clone --branch v28.0 --single-branch https://github.com/steveseguin/vdo.ninja /usr/share/vdo.ninja

# Create nginx configuration directory
RUN mkdir -p /run/nginx

# Copy nginx configuration
COPY nginx.conf /etc/nginx/http.d/default.conf

# Set the working directory
WORKDIR /usr/share/vdo.ninja

# Expose HTTP port
EXPOSE 80

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]