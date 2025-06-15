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
    # Replace other environment variables
    echo 'echo "Replacing environment variables in nginx config"' >> /docker-entrypoint.sh && \
    echo 'envsubst < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.sh && \
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
