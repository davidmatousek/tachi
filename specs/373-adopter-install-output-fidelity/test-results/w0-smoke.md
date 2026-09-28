# W0 Smoke Render (T002)

**Task**: T002 (Phase 1 / W0, `/aod.build` wave 1) · **Feature**: 373-adopter-install-output-fidelity
**Date (UTC)**: 2026-09-28
**Endpoint**: `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
**Prompt** (trivial, all eight calls): "a simple flat blue square centered on a white background"
**Wall-clock**: start 2026-09-28T01:46:12Z · end 2026-09-28T01:50:12Z

Per NFR-5, the key was loaded from 1Password (`op://yuwrq3e5bzxyzhgivu3meagtlq/Gemini API Key/credential`) fresh for each of the eight calls, exported only into the child `sh -c` process, sent only as an `x-goog-api-key` header read from stdin (`-H @-`). No `-v`/`--trace*`, no `?key=`, no echo, no write of the key to disk, no environment dump. Both `aspectRatio` and `imageSize` were sent inside `generationConfig.imageConfig`, with `generationConfig.responseModalities: ["TEXT","IMAGE"]`, per `contracts/gemini-request-and-scaffold.md`.

All bodies, responses and decoded images stayed under the session scratchpad (`w0-smoke/`) and were never written into the repo.

## Results

| # | Model | Ratio | Size | HTTP | Image? | Dimensions (W×H) | Long edge | Response time (s) | Retried | Key casing | MIME type | Magic bytes match |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `gemini-3-pro-image` | 16:9 | default | 200 | yes | 1376×768 | 1376 | 13.15 | no | camelCase (`inlineData`/`mimeType`) | image/jpeg | yes |
| 2 | `gemini-3-pro-image` | 16:9 | `2K` | 200 | yes | 2752×1536 | 2752 | 17.91 | no | camelCase (`inlineData`/`mimeType`) | image/jpeg | yes |
| 3 | `gemini-3-pro-image` | 3:4 | default | 200 | yes | 896×1200 | 1200 | 14.29 | no | camelCase (`inlineData`/`mimeType`) | image/jpeg | yes |
| 4 | `gemini-3-pro-image` | 3:4 | `2K` | 200 | yes | 1792×2400 | 2400 | 19.67 | no | camelCase (`inlineData`/`mimeType`) | image/jpeg | yes |
| 5 | `gemini-3.1-flash-image` | 16:9 | default | 200 | yes | 1376×768 | 1376 | 7.94 | no | camelCase (`inlineData`/`mimeType`) | image/jpeg | yes |
| 6 | `gemini-3.1-flash-image` | 16:9 | `2K` | 200 | yes | 2752×1536 | 2752 | 12.72 | no | camelCase (`inlineData`/`mimeType`) | image/jpeg | yes |
| 7 | `gemini-3.1-flash-image` | 3:4 | default | 200 | yes | 896×1200 | 1200 | 6.85 | no | camelCase (`inlineData`/`mimeType`) | image/jpeg | yes |
| 8 | `gemini-3.1-flash-image` | 3:4 | `2K` | 200 | yes | 1792×2400 | 2400 | 10.93 | no | camelCase (`inlineData`/`mimeType`) | image/jpeg | yes |

Every call returned HTTP 200 with an image part on the first attempt; no 429/5xx transient occurred, so no retry fired. Every response used the camelCase REST keys (`inlineData`, `mimeType`) — the SDK snake_case spelling never appeared. Every response's MIME type (`image/jpeg`) matched its magic bytes (`\xFF\xD8\xFF`), so the `.jpg` extension rule applies to all eight.

## Decisions

### 1. `IMAGE_SIZE_RESTORED`

Per-pair comparison (same model × ratio, 2K long edge vs. default long edge):

| Model | Ratio | Default long edge | 2K long edge | 2K exceeds default? |
|---|---|---|---|---|
| `gemini-3-pro-image` | 16:9 | 1376 | 2752 | yes |
| `gemini-3-pro-image` | 3:4 | 1200 | 2400 | yes |
| `gemini-3.1-flash-image` | 16:9 | 1376 | 2752 | yes |
| `gemini-3.1-flash-image` | 3:4 | 1200 | 2400 | yes |

All four 2K calls returned an image whose long edge exceeds its default variant's (exactly 2×, in every pair).

**`IMAGE_SIZE_RESTORED = true`.**

### 2. 3:4 check (blocking only for T013's executive-architecture configuration, per AR-2)

3:4 at the default size succeeded on both models (row 3: `gemini-3-pro-image` 200 + image; row 7: `gemini-3.1-flash-image` 200 + image).

**Result: PASS.**

### 3. Other refusal statuses (non-404/403, for the architect under AR-2)

None. All eight calls returned HTTP 200 on the first attempt. There is nothing to escalate under AR-2 from this smoke; no 400/429/403/404/5xx occurred at any point in the matrix.

### 4. Blocked or unreachable models (P-10.1)

None. Both `gemini-3-pro-image` and `gemini-3.1-flash-image` were reachable for every ratio × size combination on the first attempt. No diagnosis (key scope, entitlement, quota) or extra retry was needed, and W1 is not held on this account.

## Provenance for T012

- **Endpoint**: `models/{model}:generateContent` at `https://generativelanguage.googleapis.com/v1beta/`
- **Models verified**: `gemini-3-pro-image`, `gemini-3.1-flash-image`
- **Ratios verified**: `16:9`, `3:4` (both models × both ratios)
- **Date**: 2026-09-28
- **`imageSize`**: `2K` live-verified honored at every shipped model × ratio combination (see Decision 1) → `IMAGE_SIZE_RESTORED = true`
- **Observed response key casing**: camelCase REST keys (`inlineData` with `mimeType`) at every call; the snake_case SDK spelling (`inline_data`/`mime_type`) was never observed but the parser accepts both per the contract
- **Reference provenance line form** (`gemini-prompt-construction.md`), one per chain model × ratio:
  - `Verified: models/gemini-3-pro-image:generateContent · gemini-3-pro-image · 2026-09-28 · aspectRatio 16:9 · imageSize 2K`
  - `Verified: models/gemini-3-pro-image:generateContent · gemini-3-pro-image · 2026-09-28 · aspectRatio 3:4 · imageSize 2K`
  - `Verified: models/gemini-3.1-flash-image:generateContent · gemini-3.1-flash-image · 2026-09-28 · aspectRatio 16:9 · imageSize 2K`
  - `Verified: models/gemini-3.1-flash-image:generateContent · gemini-3.1-flash-image · 2026-09-28 · aspectRatio 3:4 · imageSize 2K`

Lane C1 copies this block into the reference per `quickstart.md` §4.

## Notes for W3 (P-10.3(d) latency check)

This smoke used a trivial prompt against a blank canvas, not a real template, so its response times are not a substitute for the W3 real-template latency check — they are recorded for completeness only. All eight fell well inside the 60 s single-attempt timeout (slowest: 19.67 s, `gemini-3-pro-image` 3:4 `2K`), with no combination near the ~45 s W3 drop threshold. W3 must still time real-template 2K renders before merge.
