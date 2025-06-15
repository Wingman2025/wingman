# Build stage
FROM node:18-slim as build

# Set working directory
WORKDIR /app

# Copy all files first
COPY . .

# Show versions for debugging
RUN node -v && npm -v

# Install dependencies
RUN npm install

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
