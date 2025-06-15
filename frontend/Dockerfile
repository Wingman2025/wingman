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

# Create a script to replace environment variables in nginx config
RUN echo '#!/bin/sh \n\
set -e \n\
# Replace environment variables in nginx config \n\
envsubst ''\''$VITE_API_BASE_URL''\'' < /etc/nginx/conf.d/default.conf > /etc/nginx/conf.d/default.conf.tmp \n\
mv /etc/nginx/conf.d/default.conf.tmp /etc/nginx/conf.d/default.conf \n\
# Start Nginx \n\
exec nginx -g "daemon off;" \n' > /docker-entrypoint.sh \
    && chmod +x /docker-entrypoint.sh

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["/docker-entrypoint.sh"]
