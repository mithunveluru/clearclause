#!/usr/bin/env bash
# Render the sample docs to images and upload them
set -euo pipefail
docker compose exec -T backend python scripts/seed.py
