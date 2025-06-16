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
    echo '{"status":502,"error":"Bad Gateway","message":"The server received an invalid response from the upstream server"}' > /usr/share/nginx/html/502.json && \
    chmod 644 /usr/share/nginx/html/502.json

# Copy built assets and Nginx config template
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf.template

# Create and set up entrypoint script
RUN \
    printf '#!/bin/sh\nset -e\nexport VITE_API_BASE_URL=${VITE_API_BASE_URL:-https://wingman-dev.up.railway.app}\necho "Starting container with VITE_API_BASE_URL=${VITE_API_BASE_URL}"\nenvsubst '\''${VITE_API_BASE_URL}'\'' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf\necho "--- Final Nginx config ---"\ncat /etc/nginx/conf.d/default.conf\necho "--------------------------"\necho "Starting Nginx..."\nexec nginx -g "daemon off;"\n' > /usr/local/bin/entrypoint.sh && \
    dos2unix /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

# Document the default port
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
