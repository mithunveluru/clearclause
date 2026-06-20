"""Seed demo data: render the sample-data documents to images and upload them.

Run inside the backend container (has Pillow + httpx + /sample-data mounted):
    docker compose exec backend python scripts/seed.py
Each upload auto-starts analysis, so the workspace fills with finished reports.
"""
import io
import os

import httpx
from PIL import Image, ImageDraw

API = os.environ.get("SEED_API", "http://localhost:8000")
SAMPLES = os.environ.get("SAMPLE_DIR", "/sample-data")
EMAIL = os.environ.get("SEED_EMAIL", "demo@example.com")
PASSWORD = os.environ.get("SEED_PASSWORD", "supersecret1")


def render_png(text: str) -> io.BytesIO:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    width, line_h, pad = 1240, 52, 30
    img = Image.new("RGB", (width, pad * 2 + line_h * len(lines)), "white")
    draw = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        draw.text((pad, pad + i * line_h), line, fill="black")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return buf


def main() -> None:
    client = httpx.Client(base_url=API, timeout=60)
    client.post("/api/v1/auth/register", json={"email": EMAIL, "password": PASSWORD})
    login = client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    login.raise_for_status()
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    names = sorted(n for n in os.listdir(SAMPLES) if n.endswith(".txt"))
    for name in names:
        text = open(os.path.join(SAMPLES, name)).read()
        png = render_png(text)
        resp = client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": (name.replace(".txt", ".png"), png, "image/png")},
        )
        resp.raise_for_status()
        print(f"  uploaded {name} -> document {resp.json()['id']} (analysis auto-started)")

    print(f"\nSeeded {len(names)} documents for {EMAIL}. Open http://localhost:3000")


if __name__ == "__main__":
    main()
