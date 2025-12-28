# Build stage
FROM node:18-alpine AS build

WORKDIR /app

# Accept build argument for API URL (defaults to localhost for development)
ARG REACT_APP_API_BASE_URL=http://localhost:5000/api
ENV REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL

# Copy package files
COPY services/ui-service/package*.json ./

# Install dependencies
RUN npm ci --only=production=false

# Copy ui-service source code
COPY services/ui-service/ ./

# Build the React app
RUN npm run build

# Production stage - serve with nginx
FROM nginx:alpine

# Copy built files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration for client-side routing
COPY services/ui-service/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

