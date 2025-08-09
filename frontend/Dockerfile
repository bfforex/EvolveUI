FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache curl

# Copy package files first for better caching
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy nginx configuration
COPY --from=builder /app/build /usr/share/nginx/html

# Create directory structure and symlink for static files
RUN mkdir -p /etc/nginx/html && \
    ln -sf /usr/share/nginx/html/static /etc/nginx/html/static

# Create custom nginx config for better security and performance
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    \
    # Security headers \
    add_header X-Frame-Options DENY; \
    add_header X-Content-Type-Options nosniff; \
    add_header X-XSS-Protection "1; mode=block"; \
    \
    # Gzip compression \
    gzip on; \
    gzip_vary on; \
    gzip_min_length 1024; \
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json; \
    \
    # Static files with caching \
    location /static/ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
    \
    # Main application \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # Health check endpoint \
    location /health { \
        access_log off; \
        return 200 "healthy\n"; \
        add_header Content-Type text/plain; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]