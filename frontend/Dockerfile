# Build stage
FROM node:18-slim as build
WORKDIR /app

# 1. Copy package files and lock file
COPY package*.json ./


# 2. Install dependencies
RUN npm ci

# 3. Copy all source files
COPY . .

# 4. Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install gettext for envsubst and create necessary files in one layer
RUN apk add --no-cache gettext && \
    # Create log directory and files
    mkdir -p /var/log/nginx && \
    touch /var/log/nginx/access.log /var/log/nginx/error.log \
          /var/log/nginx/api_access.log /var/log/nginx/api_error.log && \
    chmod 666 /var/log/nginx/*.log && \
    # Create custom 502 error page
    echo '{"status":502,"error":"Bad Gateway","message":"The server received an invalid response from the upstream server"}' > /usr/share/nginx/html/502.json && \
    chmod 644 /usr/share/nginx/html/502.json

# Copy built assets and configs
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf.template

# Create and set up entrypoint in a single layer
RUN echo '#!/bin/sh\n\
set -e\n\
echo "Setting up Nginx configuration..."\n\
export PORT=${PORT:-8080}\n\
# Copy template to actual config\ncp /etc/nginx/conf.d/default.conf.template /etc/nginx/conf.d/default.conf\n\
# Update port in config\nsed -i "s/listen 8080/listen $PORT/g" /etc/nginx/conf.d/default.conf\n\
# Update backend URL if VITE_API_BASE_URL is set\nif [ -n "$VITE_API_BASE_URL" ]; then\n  echo "Setting backend URL to $VITE_API_BASE_URL"\n  sed -i "s|proxy_pass https://wingman-dev.up.railway.app;|proxy_pass $VITE_API_BASE_URL;|g" /etc/nginx/conf.d/default.conf\nfi\n\
echo "Starting Nginx on port $PORT..."\nexec nginx -g "daemon off;"' > /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

EXPOSE ${PORT:-80}
CMD ["/docker-entrypoint.sh"]
