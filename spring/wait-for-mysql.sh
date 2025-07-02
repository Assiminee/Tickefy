#!/bin/bash
HOST="$1"
PORT="$2"
shift 2

echo "Waiting for MySQL at $HOST:$PORT..."

while ! nc -z "$HOST" "$PORT"; do
  sleep 1
done

echo "MySQL is up - executing command"
exec "$@"
