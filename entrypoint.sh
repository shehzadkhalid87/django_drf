#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Wait for the database to be ready
until python -c "import psycopg2; psycopg2.connect('${DATABASE_URL}')" 2>/dev/null; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing..."

# Run database migrations
python manage.py migrate
python manage.py fixture

# Start the Celery worker
celery --app asm_project worker --loglevel=info &

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn --workers 1 --bind 0.0.0.0:8000 --timeout 600 --access-logfile - asm_project.wsgi:application
