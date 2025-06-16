# Build stage
FROM node:18-slim as build

# Set working directory
WORKDIR /app

# Copy package files and lock file
COPY package*.json ./

# Copy source files
COPY src/ ./src

# Copy index.html and config files
COPY index.html .
COPY vite.config.js .
COPY tailwind.config.js .
COPY postcss.config.js .

# Install dependencies and build
RUN npm install
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Install gettext for envsubst
RUN apk add --no-cache gettext

# Create log directory and ensure it's writable
RUN mkdir -p /var/log/nginx && \
    touch /var/log/nginx/access.log /var/log/nginx/error.log /var/log/nginx/api_access.log /var/log/nginx/api_error.log && \
    chmod 666 /var/log/nginx/*.log

# Create a custom 502 error page
RUN echo '{"status":502,"error":"Bad Gateway","message":"The server received an invalid response from the upstream server"}' > /usr/share/nginx/html/502.json && \
    chmod 644 /usr/share/nginx/html/502.json

# Copy nginx config template
COPY nginx.conf /etc/nginx/conf.d/default.conf.template

# Create a simple entrypoint script
RUN echo '#!/bin/sh' > /docker-entrypoint.sh && \
    echo 'set -e' >> /docker-entrypoint.sh && \
    echo 'echo "Setting up Nginx configuration..."' >> /docker-entrypoint.sh && \
    # Set default port to 8080 if not provided
    echo 'export PORT=${PORT:-8080}' >> /docker-entrypoint.sh && \
    # Replace the port in nginx config
    echo 'sed -i "s/listen 8080/listen $PORT/g" /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.sh && \
    # Replace backend URL if VITE_API_BASE_URL is set
    echo 'if [ -n "$VITE_API_BASE_URL" ]; then' >> /docker-entrypoint.sh && \
    echo '  echo "Setting backend URL to $VITE_API_BASE_URL"' >> /docker-entrypoint.sh && \
    echo '  sed -i "s|proxy_pass https://wingman-dev.up.railway.app;|proxy_pass $VITE_API_BASE_URL;|g" /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.sh && \
    echo 'fi' >> /docker-entrypoint.sh && \
    echo 'echo "Starting Nginx on port $PORT..."' >> /docker-entrypoint.sh && \
    echo 'exec nginx -g "daemon off;"' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh && \
    # Verify the script
    cat /docker-entrypoint.sh && \
    ls -la /docker-entrypoint.sh

# Expose port for Railway
EXPOSE ${PORT:-80}

# Start Nginx
CMD ["/docker-entrypoint.sh"]
