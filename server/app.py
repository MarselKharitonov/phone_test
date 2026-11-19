"""Private LAN prototype. Do not expose directly to the internet."""
import base64
import binascii
import hmac
import io
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from server.jobs import JobStore, State
from stylist.catalog import connect, list_products

MAX_BODY = 24_000_000
MAX_PIXELS = 24_000_000
STORE = JobStore()
TOKEN = os.environ.get("STYLIST_SERVER_TOKEN", "")
DB = Path(os.environ.get("STYLIST_CATALOG", "catalog.sqlite3"))


def clean_image(encoded):
    if not isinstance(encoded, str):
        raise ValueError("Expected base64 image")
    try:
        data = base64.b64decode(encoded, validate=True)
        if not 0 < len(data) <= STORE.max_image_bytes:
            raise ValueError("Image is too large")
        with Image.open(io.BytesIO(data)) as image:
            if image.format not in ("JPEG", "PNG", "WEBP"):
                raise ValueError("Unsupported image format")
            if image.width * image.height > MAX_PIXELS or getattr(image, "n_frames", 1) != 1:
                raise ValueError("Unsupported image dimensions or animation")
            result = ImageOps.exif_transpose(image).convert("RGB")
            size = result.size
            buf = io.BytesIO()
            result.save(buf, format="PNG")
            if buf.tell() > STORE.max_image_bytes:
                raise ValueError("Decoded image is too large")
            return buf.getvalue(), size
    except (binascii.Error, UnidentifiedImageError, Image.DecompressionBombError, OSError) as exc:
        raise ValueError("Invalid image") from exc


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # Do not log photos, identifiers or authorization headers.

    def reply(self, status, body):
        data = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def authorized(self):
        value = self.headers.get("Authorization", "")
        return bool(TOKEN) and hmac.compare_digest(value, "Bearer " + TOKEN)

    def do_GET(self):
        if not self.authorized():
            return self.reply(401, {"error": "unauthorized"})
        if self.path == "/v1/health":
            return self.reply(200, {"status": "ok", "provider": "disabled"})
        if self.path == "/v1/products":
            with connect(DB) as db:
                products = list_products(db)
            for product in products:
                product.pop("image_path", None)
                product.pop("rights_note", None)
            return self.reply(200, {"products": products})
        if self.path.startswith("/v1/jobs/"):
            job = STORE.get(self.path.removeprefix("/v1/jobs/"))
            if not job:
                return self.reply(404, {"error": "not_found"})
            return self.reply(200, {"id": job.id, "state": job.state.value, "error": job.error})
        return self.reply(404, {"error": "not_found"})

    def do_POST(self):
        if not self.authorized():
            return self.reply(401, {"error": "unauthorized"})
        if self.path != "/v1/jobs":
            return self.reply(404, {"error": "not_found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BODY:
                return self.reply(413, {"error": "request_too_large"})
            payload = json.loads(self.rfile.read(length))
            person, _ = clean_image(payload["person"])
            garment, _ = clean_image(payload["garment"])
            job = STORE.create(person, garment, payload["frame"], payload["category"], payload["consent"])
            # Never return or advertise an unverified output as a try-on.
            job.state = State.FAILED
            job.error = "generation_provider_not_configured"
            job.person = b""
            job.garment = b""
            timer = threading.Timer(3600, STORE.delete, args=(job.id,))
            timer.daemon = True
            timer.start()
            return self.reply(202, {"id": job.id, "state": job.state.value, "error": job.error})
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            return self.reply(400, {"error": "invalid_request"})

    def do_DELETE(self):
        if not self.authorized():
            return self.reply(401, {"error": "unauthorized"})
        if not self.path.startswith("/v1/jobs/"):
            return self.reply(404, {"error": "not_found"})
        deleted = STORE.delete(self.path.removeprefix("/v1/jobs/"))
        return self.reply(200 if deleted else 404, {"deleted": deleted})


def main():
    if len(TOKEN) < 32:
        raise SystemExit("Set STYLIST_SERVER_TOKEN to a random token of at least 32 characters.")
    # Loopback only. A trusted, authenticated HTTPS reverse proxy is required for a phone.
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("Listening on 127.0.0.1:8765; generation disabled.")
    server.serve_forever()


if __name__ == "__main__":
    main()
