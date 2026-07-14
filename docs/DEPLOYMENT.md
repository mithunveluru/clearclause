# Deploying ClearClause — Vercel + Render (free tier)

Frontend on Vercel, API + worker on Render, Postgres and Redis managed by Render,
documents in Cloudflare R2.

> **Read this first.** The free tier runs this app, but it does not run it *well*, and
> some of the limits are not tuneable. They are listed under
> [What the free tier costs you](#what-the-free-tier-costs-you). Read that section before
> you promise this URL to anyone.

For a real deployment, `docker-compose.prod.yml` on a small VPS is both cheaper and
better — see [DEPLOY.md](DEPLOY.md).

---

## Architecture on Render

```
Vercel (Next.js)  ──HTTPS──►  Render web service  ──►  Render Postgres
  clearclause.vercel.app        uvicorn + Celery         Render Key Value (Redis)
                                (one container)      ──►  Cloudflare R2 (documents)
```

Render's free tier has **no background-worker service type**, so the Celery worker runs
inside the web container (`backend/start-render.sh`). The API and the worker share one
512 MB instance. This is the main compromise of this setup.

---

## 1. Object storage (required, do this first)

Free Render instances have **no persistent disk**. With `STORAGE_BACKEND=local`, every
upload and generated PDF is destroyed on each restart and each spin-down. Object storage
is mandatory, not optional.

[Cloudflare R2](https://dash.cloudflare.com) has a free tier (10 GB) and is S3-compatible:

1. Create a bucket, e.g. `clearclause`. Keep it **private** — nothing reads it directly;
   the app issues 5-minute signed URLs for report downloads.
2. Create an **API token** scoped to that bucket with read/write.
3. Note the **Access Key ID**, **Secret Access Key**, and the **S3 endpoint**
   (`https://<account-id>.r2.cloudflarestorage.com`).

These documents are people's loan agreements and property deeds. Do not make the bucket
public, and do not reuse an existing bucket that is.

## 2. Backend (Render)

### Option A — Blueprint (recommended)

The repo ships [`render.yaml`](../render.yaml), which declares the web service, Postgres,
and Key Value store together.

1. Render Dashboard → **New** → **Blueprint** → connect this GitHub repo → select branch `main`.
2. Render reads `render.yaml` and prompts for the values marked `sync: false`.
   Fill in the storage ones now; leave `CORS_ORIGINS` blank until the frontend exists (step 4).
3. **Apply**. The first build takes ~5 minutes (the image installs Tesseract and Poppler).

### Option B — Manual

Render Dashboard → **New** → **Web Service** → connect the repo, then:

| Setting | Value |
|---|---|
| Runtime | **Docker** |
| Root Directory | `backend` |
| Dockerfile Path | `./Dockerfile` |
| Docker Command | `./start-render.sh` |
| Health Check Path | `/health` |
| Instance Type | Free |

Then create a **Postgres** instance and a **Key Value** instance (both free) and wire their
connection strings into `DATABASE_URL` and `REDIS_URL`.

### Migrations

`start-render.sh` runs `alembic upgrade head` on every boot before serving. There is no
separate migration step and no manual shell command to remember.

### Backend environment variables

Set on the Render service. Secrets are entered in the dashboard and never committed.

| Variable | Value | Notes |
|---|---|---|
| `DATABASE_URL` | *(from Render Postgres)* | Render's `postgresql://` URL is upgraded to `+asyncpg` automatically |
| `REDIS_URL` | *(from Render Key Value)* | Celery broker, rate limits, token revocation |
| `JWT_SECRET` | *(generate)* | Render can generate it. Rotating it logs everyone out. |
| `ENV` | `production` | Activates the startup invariant checks |
| `COOKIE_SECURE` | `true` | Required over HTTPS |
| `COOKIE_SAMESITE` | `none` | **Required.** Vercel and Render are different sites; a `Lax` cookie is never sent cross-site and login would silently fail on every subsequent request. Setting `none` activates the CSRF guard. |
| `TRUSTED_PROXY_DEPTH` | `1` | Render terminates TLS at a proxy. Leave at `0` and every request looks like it came from the proxy, so one user's traffic rate-limits everyone. |
| `CORS_ORIGINS` | `https://<your-app>.vercel.app` | Your Vercel production domain. Fill in after step 4. |
| `CORS_ORIGIN_REGEX` | `^https://<project>-.*\.vercel\.app$` | Optional — only if you want preview deploys to reach the API |
| `STORAGE_BACKEND` | `s3` | **Required.** `local` loses every document on redeploy. |
| `S3_BUCKET` | `clearclause` | |
| `S3_ENDPOINT_URL` | `https://<account>.r2.cloudflarestorage.com` | Blank for AWS S3 |
| `S3_REGION` | `auto` | `auto` for R2 |
| `AWS_ACCESS_KEY_ID` | *(secret)* | Read by boto3 from the environment |
| `AWS_SECRET_ACCESS_KEY` | *(secret)* | |
| `MAX_UPLOAD_MB` | `5` | Lowered from 10: OCR shares 512 MB with the API |
| `MAX_PDF_PAGES` | `10` | Lowered from 50: OCR rasterizes ~26 MB per page |
| `AI_MODE` | `off` | See [AI layer](#5-ai-layer-optional) |

## 3. Frontend (Vercel)

Vercel → **Add New** → **Project** → import the repo.

| Setting | Value |
|---|---|
| Framework Preset | Next.js *(auto-detected)* |
| Root Directory | `frontend` |
| Build Command | *(default — `next build`)* |
| Output Directory | *(default)* |
| Install Command | *(default — `npm install`)* |

### Frontend environment variables

| Variable | Value | Notes |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | `https://<your-api>.onrender.com` | Your Render URL, **no trailing slash** |

> `NEXT_PUBLIC_*` is **inlined into the client bundle at build time**, not read at runtime.
> Changing it requires a redeploy, not just a restart. It is also compiled into the CSP's
> `connect-src`, so a stale value produces a browser that silently refuses to call the API.

Set it for **Production**, and for **Preview** too if you want preview deploys to work.

## 4. Close the loop

Deployment order matters, because each side needs the other's URL:

1. Deploy the **backend** first — you get `https://clearclause-api.onrender.com`.
2. Deploy the **frontend** with `NEXT_PUBLIC_API_BASE_URL` set to it.
3. Go back to Render and set `CORS_ORIGINS` to your Vercel domain. **Save** — this restarts
   the API.

Skip step 3 and every browser request fails CORS, while `curl` works fine. That mismatch is
the single most common way this deployment "mysteriously" breaks.

## 5. AI layer (optional)

`AI_MODE=off` by default; everything except summaries and Q&A works without it.

To enable: get a [Groq](https://console.groq.com) key (LLM) and a [Jina](https://jina.ai)
key (embeddings), then set `AI_MODE=summary_only` for summaries only.

`AI_MODE=full` (Q&A) additionally needs Qdrant, which Render does not offer — use
[Qdrant Cloud](https://cloud.qdrant.io)'s free 1 GB tier and set `QDRANT_URL` and
`QDRANT_API_KEY` to it. Embedding a document costs a Jina API call per chunk.

---

## What the free tier costs you

These are properties of the platform, not bugs to fix:

| Limit | Consequence |
|---|---|
| **Spin-down after ~15 min idle** | First request takes ~50 s while the container boots. Worse: **a spun-down instance runs no background jobs** — an upload that lands as the service sleeps is not processed until something wakes it. |
| **512 MB RAM, shared** | The API and the Celery worker are one process tree. A large scan can OOM the worker *and take the API down with it*. `MAX_PDF_PAGES=10` exists to make this less likely, not impossible. |
| **Free Postgres expires after 30 days** | Render deletes it. Every account and document is gone. This deployment has a shelf life. |
| **No persistent disk** | Enforced above by requiring R2. |
| **Cold-start + no worker** | "Q&A available immediately after upload" does not hold. Expect a minute or more on a cold instance. |

If any of that is unacceptable, the cheapest real fix is a **Render Background Worker**
($7/mo) running the same Celery command, which separates OCR from the API. The next is a
$5 VPS with `docker-compose.prod.yml`, which removes every limit in this table.

---

## Verifying the deployment

Run these in order. Each one fails distinctively when the step before it is misconfigured.

```bash
API=https://<your-api>.onrender.com

# 1. The service is up and can reach Postgres.
curl -s $API/health
# {"status":"ok","database":true}   — "degraded" means DATABASE_URL is wrong

# 2. CORS is configured for your frontend (not a wildcard).
curl -si -X OPTIONS $API/api/v1/documents \
  -H "Origin: https://<your-app>.vercel.app" \
  -H "Access-Control-Request-Method: GET" | grep -i access-control-allow-origin
# echoes your origin — no header at all means CORS_ORIGINS is unset or wrong

# 3. Auth cookies are cross-site capable.
curl -si -X POST $API/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"correct horse battery"}' >/dev/null
curl -si -X POST $API/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"correct horse battery"}' | grep -i set-cookie
# every cookie must show `SameSite=none; Secure`. If it says SameSite=lax,
# COOKIE_SAMESITE is not set and the browser will drop your session.
```

Then in the browser, with devtools open:

- [ ] Landing page loads; no CSP or mixed-content errors in the console.
- [ ] Register, then log in. **Application → Cookies** shows `cc_token`, `cc_refresh`, `cc_csrf`.
- [ ] Dashboard loads (this is the first authenticated call — a 401 here means the cookie
      was not sent, i.e. `COOKIE_SAMESITE` is wrong).
- [ ] Upload a small PDF. Status advances past `uploaded` (if it never does, the Celery
      worker is not running — check the Render logs for `celery@... ready`).
- [ ] Explorer renders findings; the PDF report downloads.
- [ ] Log out; the cookies are cleared and the dashboard 401s.

## Troubleshooting

| Symptom | Cause |
|---|---|
| Login succeeds, every later call 401s | `COOKIE_SAMESITE` is not `none`. The browser is dropping a Lax cookie on a cross-site request. |
| Browser calls fail, `curl` works | `CORS_ORIGINS` does not match your Vercel domain exactly (scheme, no trailing slash). |
| `403 CSRF token missing or invalid` | The `cc_csrf` cookie was not set (log in again) or a request is being made from outside the app. |
| Document stuck at `uploaded` forever | The worker is not running, or the instance spun down. Check Render logs. |
| Uploads vanish after a redeploy | `STORAGE_BACKEND` is still `local`. |
| App won't boot, "Refusing to start" | An `ENV=production` invariant failed — the log names it (default JWT secret, insecure cookies, or an `http://` CORS origin). |
| First request takes ~50s | Free-tier cold start. Expected. |
