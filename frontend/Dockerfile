# Build stage
FROM node:18-slim as build
WORKDIR /app

# 1. Copy package.json and lock file for caching
COPY package*.json ./

# 2. Install dependencies without running lifecycle scripts (avoids postinstall build)
RUN npm ci --ignore-scripts

# 3. Copy the rest of the application source
COPY . .

# 4. Now run build explicitly (all files available)
RUN npm run build

# Production stage
FROM nginx:alpine

# Install utilities, create log directory/files, and custom error page
RUN apk add --no-cache gettext dos2unix && \
    mkdir -p /var/log/nginx && \
    touch /var/log/nginx/access.log /var/log/nginx/error.log \
          /var/log/nginx/api_access.log /var/log/nginx/api_error.log && \
    chmod 666 /var/log/nginx/*.log && \
    echo '{"status":502,"error":"Bad Gateway","message":"The server received an invalid response from the upstream server"}' > /usr/share/nginx/html/502.json && \
    chmod 644 /usr/share/nginx/html/502.json

# Copy built assets and Nginx config template
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf.template

# Create and set up entrypoint script
RUN \
    printf '#!/bin/sh\nset -e\n\necho "Setting up Nginx configuration..."\n\nPORT=${PORT:-8080}\n\n# Copy template to actual config\ncp /etc/nginx/conf.d/default.conf.template /etc/nginx/conf.d/default.conf\n\n# Update port in config\nsed -i "s/listen 8080/listen ${PORT}/g" /etc/nginx/conf.d/default.conf\n\n# Update backend URL if VITE_API_BASE_URL is set\nif [ -n "${VITE_API_BASE_URL}" ]; then\n  echo "Setting backend URL to ${VITE_API_BASE_URL}"\n  sed -i "s|proxy_pass https://wingman-dev.up.railway.app;|proxy_pass ${VITE_API_BASE_URL};|g" /etc/nginx/conf.d/default.conf\nfi\n\necho "Final Nginx config:"\ncat /etc/nginx/conf.d/default.conf\necho "Starting Nginx on port ${PORT}..."\nexec nginx -g "daemon off;"\n' > /usr/local/bin/entrypoint.sh && \
    dos2unix /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

# Document the default port
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
