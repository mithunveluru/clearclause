"""Seed demo data: render the sample-data documents to images and upload them.

Run inside the backend container (has Pillow + httpx + /sample-data mounted):
    docker compose exec backend python scripts/seed.py
Each upload auto-starts analysis, so the workspace fills with finished reports.
"""
import io
import os
from pathlib import Path

import httpx
import reportlab
from PIL import Image, ImageDraw, ImageFont

API = os.environ.get("SEED_API", "http://localhost:8000")
SAMPLES = os.environ.get("SAMPLE_DIR", "/sample-data")
EMAIL = os.environ.get("SEED_EMAIL", "demo@example.com")
PASSWORD = os.environ.get("SEED_PASSWORD", "supersecret1")


# Pillow's built-in bitmap font reads at 35% word error; this reads at 2%, which is
# the difference between a demo whose documents classify and one full of "unknown".
# Ships inside reportlab, so it cannot go missing the way a system font can.
FONT = ImageFont.truetype(str(Path(reportlab.__file__).parent / "fonts" / "Vera.ttf"), 30)


def _wrap(line: str, limit: int) -> list[str]:
    """Break a line to fit the page, measuring the font rather than counting characters.

    Without this a long clause runs off the canvas and is silently cropped mid-word, so
    OCR reads "on th" and the analyzer never sees the amount that followed. It looks
    exactly like a clean read: the confidence stays high because what remains is sharp.
    """
    wrapped: list[str] = []
    current = ""
    for word in line.split():
        candidate = f"{current} {word}".strip()
        if current and FONT.getlength(candidate) > limit:
            wrapped.append(current)
            current = word
        else:
            current = candidate
    wrapped.append(current)
    return wrapped


def render_png(text: str) -> io.BytesIO:
    width, line_h, pad = 1240, 52, 30
    lines = [
        out
        for ln in text.splitlines()
        if ln.strip()
        for out in _wrap(ln, width - pad * 2)
    ]
    img = Image.new("RGB", (width, pad * 2 + line_h * len(lines)), "white")
    draw = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        draw.text((pad, pad + i * line_h), line, fill="black", font=FONT)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return buf


def main() -> None:
    # Auth rides on httpOnly cookies, which the client jar keeps
    client = httpx.Client(base_url=API, timeout=60)
    client.post("/api/v1/auth/register", json={"email": EMAIL, "password": PASSWORD})
    login = client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})
    login.raise_for_status()

    # Only enforced when cookies are SameSite=None
    csrf = client.cookies.get("cc_csrf")
    headers = {"X-CSRF-Token": csrf} if csrf else {}

    # Re-seeding should replace the demo workspace, not stack another copy on it
    for existing in client.get("/api/v1/documents").json():
        client.delete(f"/api/v1/documents/{existing['id']}", headers=headers)

    names = sorted(n for n in os.listdir(SAMPLES) if n.endswith(".txt"))
    for name in names:
        text = open(os.path.join(SAMPLES, name)).read()
        png = render_png(text)
        resp = client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": (name.replace(".txt", ".png"), png, "image/png")},
        )
        if resp.status_code == 429:
            # Deleting documents deliberately does not refund the monthly quota
            raise SystemExit(
                f"\n{resp.json()['detail']}\n\n"
                "This is the upload quota, not a bug. For a demo environment set "
                "MONTHLY_UPLOAD_LIMIT=0 in .env and restart the backend."
            )
        resp.raise_for_status()
        print(f"  uploaded {name} -> document {resp.json()['id']} (analysis auto-started)")

    print(f"\nSeeded {len(names)} documents for {EMAIL}. Open http://localhost:3000")


if __name__ == "__main__":
    main()
