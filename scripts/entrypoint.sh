#!/usr/bin/env bash
set -e

echo "Initializing container..."

bash ./scripts/run_migrations.sh

echo "All startup scripts have been executed!"

exec "$@"