# Deploying ClearClause

Docker Compose on a single VPS, TLS terminated by Caddy, documents in S3-compatible
object storage.

The dev `docker-compose.yml` is **not** deployable: it bind-mounts `./backend` over
`/app` (so the image's contents are never actually run), uses `--reload` and
`next dev`, and exposes Postgres to the host. Use `docker-compose.prod.yml`.

---

## 1. Prerequisites

- A VPS with Docker and the Compose plugin. 2 vCPU / 4 GB is a sane floor — OCR is
  CPU-bound and each worker process rasterizes a page at a time.
- Two DNS A records pointing at the box: `clearclause.example.com` and
  `api.clearclause.example.com`. Caddy provisions certificates for both on first boot,
  which **requires ports 80 and 443 to be reachable**.
- An S3-compatible bucket (AWS S3, Cloudflare R2, DigitalOcean Spaces).

## 2. The bucket

Documents are people's loan agreements and property deeds. The bucket must be:

- **Private.** Block all public access. Nothing reads it directly — the app issues
  5-minute signed URLs for report downloads.
- **Encrypted at rest.** The app sets `ServerSideEncryption: AES256` on every write;
  enable default bucket encryption too so nothing can bypass it.
- **Versioned**, with a lifecycle rule expiring noncurrent versions after ~30 days.
  This is the undo button for an accidental delete.
- Reachable by an **IAM user scoped to this bucket alone** —
  `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject` on `arn:aws:s3:::<bucket>/*`.
  Do not deploy with root credentials.

`FILE_RETENTION_DAYS` (default 7) deletes documents on a schedule regardless. That's
a feature: the less of this data you hold, the less there is to lose.

## 3. Configure

```bash
cp .env.production.example .env.production
openssl rand -hex 32     # JWT_SECRET
openssl rand -base64 32  # POSTGRES_PASSWORD
openssl rand -hex 16     # METRICS_TOKEN
```

Fill in every blank. The app **refuses to start** with `ENV=production` if
`JWT_SECRET` is still the default, `COOKIE_SECURE` is false, or any CORS origin is
plaintext `http://`. That check lives in `Settings`, so it covers the API, the worker
and migrations alike — a misconfigured deploy fails loudly at boot rather than
quietly serving auth cookies over plain HTTP.

`TRUSTED_PROXY_DEPTH=1` matters: exactly one proxy (Caddy) sits in front. Set it to 0
and every request appears to come from Caddy's IP, so one user's traffic rate-limits
everyone.

## 4. Deploy

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

`migrate` runs `alembic upgrade head` once and exits; `backend` and `worker` wait for
it to complete successfully. Beat runs as its own service — with `--beat` embedded in
the worker, every worker replica would fire the daily cleanup job.

Check it came up:

```bash
docker compose -f docker-compose.prod.yml ps          # all healthy, migrate exited 0
curl https://api.clearclause.example.com/health       # {"status":"ok","database":true}
```

Then actually exercise it: register, upload a PDF, confirm the report renders. A green
health check only proves the database is reachable.

## 5. Rollback

Images are tagged by the commit they were built from. To go back:

```bash
git checkout <previous-good-sha>
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

**Migrations do not roll back automatically.** Every migration to date is additive
(new nullable columns), so an older image runs fine against a newer schema — that is
what makes this safe. If you ever write a destructive migration, that stops being
true, and the rollback becomes `alembic downgrade -1` *plus* a restore. Take a
database snapshot before deploying one.

## 6. Backups

Nothing here is backed up by default. Two things hold state:

- **Postgres** — users, documents metadata, findings, reports. Snapshot the `pgdata`
  volume, or run a nightly `pg_dump` off-box:
  ```bash
  docker compose -f docker-compose.prod.yml exec -T db \
    pg_dump -U clearclause clearclause | gzip > cc-$(date +%F).sql.gz
  ```
- **The bucket** — versioning (step 2) is the backup.

Redis holds only rate-limit counters and the revocation deny-list. Losing it logs
people out; it is not worth backing up.

### Restoring

**A backup you have not restored is not a backup.** This procedure has been run
end-to-end against a real dump (200 users / 56 documents / 2,701 findings restored
exactly, `alembic_version` intact). Do it once yourself into a scratch database
before you ever need it under pressure:

```bash
# into a scratch database first — never straight over the live one
docker compose -f docker-compose.prod.yml exec -T db \
  psql -U clearclause -d postgres -c "create database cc_restore_test;"

gunzip -c cc-2026-07-12.sql.gz | docker compose -f docker-compose.prod.yml exec -T db \
  psql -U clearclause -d cc_restore_test

# confirm it actually came back
docker compose -f docker-compose.prod.yml exec -T db psql -U clearclause -d cc_restore_test \
  -c "select count(*) from users; select count(*) from documents; select version_num from alembic_version;"
```

The dump restores the **database only**. Documents live in the bucket, and the two
are restored independently — a database rolled back to a point before an upload will
reference an object that still exists, which is harmless, but a bucket rolled back
without the database leaves rows pointing at objects that are gone. Restore the
database *first*, then the bucket, if you ever have to do both.

## 7. Monitoring

- `/health` — liveness plus database connectivity. Point an uptime check at it.
- `/internal/metrics` — Prometheus, behind `X-Metrics-Token: $METRICS_TOKEN`. Returns
  404 without it, so it does not advertise itself.
- `infra/docker-compose.obs.yml` brings up Prometheus, Grafana, Loki and Tempo if you
  want the full stack.

Two log lines are worth alerting on, because both mean the system is quietly degraded
rather than down:

- `rate limiter unavailable` — Redis is gone; requests are being allowed through
  **unlimited**. Brute-force protection is off until it returns.
- `low OCR confidence` — a document was too poor to read reliably. The user is warned
  in the UI, but a spike means something upstream is wrong.
