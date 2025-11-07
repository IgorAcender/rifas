#!/bin/bash
set -e

echo "Waiting for database..."
python << END
import sys
import time
import psycopg2
from urllib.parse import urlparse
import os

db_url = os.environ.get('DATABASE_URL', '')

if db_url and db_url.startswith('postgres'):
    result = urlparse(db_url)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port or 5432

    max_retries = 30
    retry = 0
    while retry < max_retries:
        try:
            conn = psycopg2.connect(
                dbname=database,
                user=username,
                password=password,
                host=hostname,
                port=port
            )
            conn.close()
            print("Database is ready!")
            sys.exit(0)
        except psycopg2.OperationalError:
            retry += 1
            print(f"Database not ready yet... ({retry}/{max_retries})")
            time.sleep(1)

    print("Could not connect to database!")
    sys.exit(1)
else:
    print("Using SQLite, skipping wait")
    sys.exit(0)
END

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Creating superuser if needed..."
python manage.py create_admin

echo "Starting Gunicorn..."
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    config.wsgi:application
