# Production stage - uses pre-built dist folder
FROM nginx:alpine

# Copy pre-built files
COPY dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 5900

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
