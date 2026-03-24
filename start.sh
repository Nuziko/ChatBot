#!/bin/bash
set -e 

echo "Starting Nginx..."
nginx 

echo "Starting Uvicorn..."
exec uvicorn server.main:app --host 127.0.0.1 --port 8000