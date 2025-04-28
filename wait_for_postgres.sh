#!/bin/bash
# wait_for_postgres.sh

set -e

host="$DB_HOST"
port="$DB_PORT"

echo "⏳ Waiting for Postgres at $host:$port..."

until pg_isready -h "$host" -p "$port" > /dev/null 2>&1; do
  sleep 1
done

echo "✅ Postgres is ready! Running ETL..."
exec "$@"
