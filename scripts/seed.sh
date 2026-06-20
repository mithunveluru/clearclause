#!/usr/bin/env bash
# Seed the demo workspace with the 6 sample documents (renders them to images
# and uploads via the API — analysis starts automatically).
set -euo pipefail
docker compose exec -T backend python scripts/seed.py
