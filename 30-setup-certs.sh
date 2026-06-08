#!/bin/sh
set -e

# Normalize variables (lowercase, remove spaces and quotes)
VAL_DISABLE_SSL=$(echo "$DISABLE_SSL" | tr '[:upper:]' '[:lower:]' | tr -d ' "\''')
VAL_HTTP_ONLY=$(echo "$HTTP_ONLY" | tr '[:upper:]' '[:lower:]' | tr -d ' "\''')

# Determine if we should use HTTP only
if [ "$VAL_DISABLE_SSL" = "true" ] || [ "$VAL_DISABLE_SSL" = "1" ] || [ "$VAL_HTTP_ONLY" = "true" ] || [ "$VAL_HTTP_ONLY" = "1" ]; then
    echo "DISABLE_SSL or HTTP_ONLY is enabled. Using HTTP-only Nginx configuration."
    cp /etc/nginx/nginx-http.conf /etc/nginx/conf.d/default.conf
    # Remove the SSL config template to ensure it's not accidentally loaded
    rm -f /etc/nginx/nginx-ssl.conf
else
    echo "SSL is enabled. Checking certificates..."
    mkdir -p /etc/nginx/ssl
    if [ ! -f /etc/nginx/ssl/fullchain.pem ] || [ ! -f /etc/nginx/ssl/privkey.pem ]; then
        echo "SSL certificates not found at /etc/nginx/ssl/. Generating self-signed certificates..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/nginx/ssl/privkey.pem \
            -out /etc/nginx/ssl/fullchain.pem \
            -subj "/C=PL/O=UP Poznan/CN=syllabus.up.poznan.pl"
    else
        echo "Using existing SSL certificates."
    fi
    cp /etc/nginx/nginx-ssl.conf /etc/nginx/conf.d/default.conf
fi
