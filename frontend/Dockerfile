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

# Create a script to replace environment variables in nginx config
RUN echo -e '#!/bin/sh\n\
set -e\n\
# Replace environment variables in nginx config\nenvsubst < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf\n\
# Start Nginx\nexec nginx -g "daemon off;"' > /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh && \
    # Verify the script was created correctly\n    cat /docker-entrypoint.sh && \
    # Show file permissions\n    ls -la /docker-entrypoint.sh

# Copy nginx config template
COPY nginx.conf /etc/nginx/conf.d/default.conf.template

# Verify files are in place
RUN ls -la /etc/nginx/conf.d/

# Expose port for Railway
EXPOSE ${PORT:-80}

# Start Nginx
CMD ["/docker-entrypoint.sh"]
