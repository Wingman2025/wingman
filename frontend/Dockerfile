# Use official Node.js image
FROM node:18-slim

# Set working directory
WORKDIR /app

# Show versions for debugging
RUN node -v && npm -v

# Copy package files
COPY package*.json ./

# Install dependencies with cache
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Use Nginx to serve the app
FROM nginx:alpine

# Copy built assets from builder
COPY --from=0 /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
