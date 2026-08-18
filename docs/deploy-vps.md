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
`JWT_SECRET` is still the default, `COOKIE_SECURE` is false, any CORS origin is
plaintext `http://`, `PUBLIC_APP_URL` is not `https://`, or `SMTP_HOST` is blank.
That check lives in `Settings`, so it covers the API, the worker and migrations alike
— a misconfigured deploy fails loudly at boot rather than quietly serving auth
cookies over plain HTTP.

`SMTP_HOST` is in that list because password reset is the only way a user who forgot
their password gets back in, and a blank host makes the reset endpoint succeed while
mailing nothing — a failure with no error to report. Any SMTP provider works (Resend,
SES, Postmark, Mailgun); `PUBLIC_APP_URL` is what the reset links point at, so it must
be the domain the user's browser actually sees.

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

Monitoring only counts if it reaches a person who is not currently looking at a
dashboard. Three layers do that, in descending order of how much they are worth:

### Error reporting (set this up first)

Set `SENTRY_DSN` in `.env.production`. Unhandled exceptions from the API and the
worker then arrive with a stack trace, tagged by which one raised them. It is the only
layer here that works without running the observability stack, and it is the one that
catches the failures nobody wrote an alert rule for.

`send_default_pii` is off, so usernames, cookies and request bodies stay out of the
reports — this app handles loan agreements, and an error tracker is not somewhere any
of that should end up. Leave `SENTRY_DSN` blank and the SDK never initializes.

### Uptime

Point an external check at `https://api.<your-domain>/health` every minute
(UptimeRobot, BetterStack and Cronitor all have free tiers big enough). The route
returns **503** if Postgres or Redis is unreachable, and its body names which one, so
a plain status-code check is enough to page on.

The check has to be external. A monitor running on the same box as the thing it
watches goes down with it.

> Note for the Render deployment: `healthCheckPath: /health` means Render now restarts
> the service when a dependency is unreachable. That is usually what you want, but a
> long Postgres outage will look like a restart loop rather than a steady 503.

### Metrics and alert rules

- `/internal/metrics` — Prometheus, behind `X-Metrics-Token: $METRICS_TOKEN`. Returns
  404 without it, so it does not advertise itself.
- `infra/docker-compose.obs.yml` brings up Prometheus, Grafana, Loki, Tempo and
  Alertmanager.

`infra/prometheus/alerts.yml` covers the states where the product returns 200s while
doing the wrong thing — the rate limiter failing open, a spike of unreadable scans,
analyzer runs failing, the API not being scraped at all.

**Those rules deliver nothing until you edit `infra/alertmanager/alertmanager.yml`.**
It ships with placeholder addresses and credentials; fill in the SMTP account (the
same one the app sends password resets through works) and the address to notify.
Verify it with:

```bash
docker compose -f docker-compose.yml -f infra/docker-compose.obs.yml \
  exec alertmanager amtool check-config /etc/alertmanager/alertmanager.yml
```

Then confirm delivery end to end by firing a fake alert — an alert path you have never
seen work is not a monitored system:

```bash
docker compose -f docker-compose.yml -f infra/docker-compose.obs.yml \
  exec alertmanager amtool alert add test severity=page \
  --alertmanager.url=http://localhost:9093
```
