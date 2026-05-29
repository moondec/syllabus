#!/bin/sh
set -e

# Determine if we should use HTTP only
if [ "$DISABLE_SSL" = "true" ] || [ "$HTTP_ONLY" = "true" ]; then
    echo "DISABLE_SSL or HTTP_ONLY is enabled. Using HTTP-only Nginx configuration."
    cp /etc/nginx/nginx-http.conf /etc/nginx/conf.d/default.conf
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
