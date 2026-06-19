#!/usr/bin/env bash
set -e

echo "Running database migrations..."

uv run --no-dev alembic -c app/alembic.ini upgrade head

echo "Migrations applied successfully!"
