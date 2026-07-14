#!/usr/bin/env bash
# Seed the demo workspace: render the sample docs to images and upload them.
set -euo pipefail
docker compose exec -T backend python scripts/seed.py
