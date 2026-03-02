#!/bin/sh
set -e

echo "🚀 Starting Code Audit API..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until pg_isready -h db -U postgres -d codeaudit; do
  echo "  PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "✅ PostgreSQL is ready!"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
until redis-cli -h redis ping >/dev/null 2>&1; do
  echo "  Redis is unavailable - sleeping"
  sleep 2
done
echo "✅ Redis is ready!"

# Run database migrations
echo "📊 Running database migrations..."
alembic upgrade head
echo "✅ Migrations complete!"

# Start the application
echo "🌟 Starting application..."
exec "$@"
