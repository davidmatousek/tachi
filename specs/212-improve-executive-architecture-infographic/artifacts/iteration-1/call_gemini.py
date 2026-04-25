#!/usr/bin/env python3
"""T009 iteration-1 — call the Gemini Image API directly.

Reads the verbatim-substituted prompt from prompt.txt and POSTs it to the
Gemini generateContent endpoint. The fallback chain matches the spec in
.claude/skills/tachi-infographics/references/gemini-prompt-construction.md
(Gemini API Configuration section).

Output:
  - threat-executive-architecture.jpg (or .png) in iteration-1/
  - api-response.txt (raw model + status for the audit trail)
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ITER = Path("/Users/david/Projects/tachi/specs/212-improve-executive-architecture-infographic/artifacts/iteration-1")

# Fallback chain per gemini-prompt-construction.md.
MODELS = [
    "gemini-3-pro-image-preview",
    "gemini-3.1-flash-image-preview",
    "gemini-2.5-flash-image",
]

API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
TIMEOUT_SECONDS = 120  # Bumped from spec's 60s — image gen + verbatim 8KB prompt is slower.


def call_one_model(model_id: str, prompt: str, api_key: str) -> tuple[bool, str, dict | None]:
    """Returns (success, status_message, response_json)."""
    url = f"{API_BASE}/{model_id}:generateContent"
    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                ],
            },
        ],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            # Note: the v1beta generateContent endpoint rejects aspectRatio
            # and imageSize as unknown generationConfig fields — those are
            # documented in gemini-prompt-construction.md but not yet
            # accepted by the live API. Aspect ratio is conveyed instead by
            # the "Orientation: portrait, 8.5:11 page aspect ratio"
            # directive inside the verbatim prompt block. (Iteration-1
            # mechanical fix; see api-response.txt for rejection details.)
        },
    }
    encoded_body = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=encoded_body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
    )
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            elapsed = time.time() - started
            raw = resp.read()
            data = json.loads(raw.decode("utf-8"))
            return True, f"HTTP {resp.status} OK in {elapsed:.1f}s", data
    except urllib.error.HTTPError as e:
        elapsed = time.time() - started
        body_bytes = e.read() if hasattr(e, "read") else b""
        body_text = body_bytes.decode("utf-8", errors="replace")[:1000]
        return False, f"HTTP {e.code} {e.reason} after {elapsed:.1f}s: {body_text}", None
    except urllib.error.URLError as e:
        elapsed = time.time() - started
        return False, f"URLError after {elapsed:.1f}s: {e.reason}", None
    except Exception as e:  # noqa: BLE001 — catch-all is desired here
        elapsed = time.time() - started
        return False, f"{type(e).__name__} after {elapsed:.1f}s: {e}", None


def extract_image_from_response(data: dict) -> tuple[bytes | None, str | None]:
    """Returns (image_bytes, mime_type) — or (None, None) if not present."""
    candidates = data.get("candidates", [])
    if not candidates:
        return None, None
    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        inline = part.get("inline_data") or part.get("inlineData")
        if not inline:
            continue
        mime = inline.get("mime_type") or inline.get("mimeType", "")
        b64 = inline.get("data")
        if mime.startswith("image/") and b64:
            return base64.b64decode(b64), mime
    return None, None


def mime_to_ext(mime: str) -> str:
    if mime in {"image/jpeg", "image/jpg"}:
        return "jpg"
    if mime == "image/png":
        return "png"
    return mime.split("/", 1)[1] if "/" in mime else "bin"


def main() -> int:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set", file=sys.stderr)
        return 2

    prompt = (ITER / "prompt.txt").read_text(encoding="utf-8")
    audit = ITER / "api-response.txt"
    audit_lines: list[str] = [f"Prompt length: {len(prompt)} chars\n"]

    for model_id in MODELS:
        print(f"=> Trying model: {model_id}")
        ok, status, data = call_one_model(model_id, prompt, api_key)
        audit_lines.append(f"\n--- {model_id} ---\nStatus: {status}\n")
        if not ok:
            print(f"   FAILED: {status}")
            continue
        # Parse for image part.
        image_bytes, mime = extract_image_from_response(data or {})
        if not image_bytes:
            # No image part — record the full response shape for audit.
            text_parts = []
            for cand in (data or {}).get("candidates", []):
                for part in cand.get("content", {}).get("parts", []):
                    if "text" in part:
                        text_parts.append(part["text"][:500])
            audit_lines.append(
                "No image part. Text excerpts: "
                + json.dumps(text_parts)[:1000]
                + "\n"
            )
            audit_lines.append(
                "Response keys: "
                + json.dumps(list((data or {}).keys()))
                + "\n"
            )
            print(f"   No image in response — will try next model.")
            continue
        ext = mime_to_ext(mime or "image/jpeg")
        # Per F-212 contract: filename is threat-executive-architecture.jpg
        # (skill reference says "threat-executive-architecture.{jpg|png}" and
        # gemini-prompt-construction.md says use the actual MIME-derived
        # extension to avoid mismatched magic bytes/extension). Save under
        # the actual MIME-derived extension; if PNG, also write a .jpg
        # alias only if the user explicitly wanted .jpg — but the simpler
        # contract is to honor the MIME. Use the MIME-derived name.
        out_path = ITER / f"threat-executive-architecture.{ext}"
        out_path.write_bytes(image_bytes)
        size = out_path.stat().st_size
        audit_lines.append(
            f"Image saved: {out_path}\n"
            f"MIME: {mime}\n"
            f"Size: {size} bytes\n"
            f"Model used: {model_id}\n"
        )
        audit.write_text("".join(audit_lines), encoding="utf-8")
        print(f"   SUCCESS — wrote {size} bytes to {out_path} (MIME {mime})")
        return 0

    audit.write_text("".join(audit_lines), encoding="utf-8")
    print("ERROR: all models in fallback chain failed", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
