# T009 — Iteration 1 — Regenerated Executive-Architecture Infographic

**Feature**: 212-improve-executive-architecture-infographic
**Phase**: 3 (US1 — OpenClaw-style rendering)
**Task**: T009
**Iteration**: 1 (of up to 3 — Risk R1 budget)
**Date**: 2026-04-25 (UTC 15:36:36Z)
**Reference dataset**: `~/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/`

---

## Summary

Regenerated `threat-executive-architecture.jpg` for the second-brain-mcp
reference dataset using the new VERBATIM-locked Gemini prompt landed in
T007 (`.claude/skills/tachi-infographics/references/executive-architecture.md`)
and the F-212 producer-side US2 callout-selection rewrite (T016/T017,
commit `c575894`).

This is the first regeneration after the F-212 producer-and-prompt rewrites.
The image is the input artifact for T010 (PM/visual review against the
OpenClaw reference) — T010 is currently blocked on the OpenClaw reference
asset, which is not present on the local filesystem.

---

## Invocation

The skill/agent dispatcher path was not invocable from this subagent
context (the `/tachi.infographic` slash command requires the main
conversation harness). The verbatim-lock contract (FR-212-6) was honored
by reading the locked block from
`.claude/skills/tachi-infographics/references/executive-architecture.md`
between the `=== BEGIN VERBATIM PROMPT BLOCK (FR-212-6 LOCKED) ===` and
`=== END VERBATIM PROMPT BLOCK (FR-212-6 LOCKED) ===` markers, substituting
ONLY the bracketed `<<...>>` data slots from the producer payload, and
sending the result to the live Gemini Image API.

### Step 1 — Producer extraction (deterministic)

```bash
python3 scripts/extract-infographic-data.py \
  --target-dir ~/Projects/second-brain-mcp/docs/security/2026-04-23T23-02-25/ \
  --template executive-architecture \
  --output specs/212-improve-executive-architecture-infographic/artifacts/iteration-1/spec.json
```

Producer summary:
- 9 qualifying Critical/High findings (0 Critical, 9 High)
- 3 layers (`Supabase Platform`, `Application Layer`, `External / Untrusted`)
- 5 callouts after F-212 US2 LRM allocation (mechanically derived; the
  qualifying findings concentrate in 2 of 3 layers, so the LRM produces
  5 entries — within the ≤8 cap and respecting per-layer floor invariant)

Saved as `iteration-1/spec.json`.

### Step 2 — Prompt construction (verbatim-lock compliant)

```bash
python3 specs/212-improve-executive-architecture-infographic/artifacts/iteration-1/build_prompt.py
```

Reads `iteration-1/spec.json` + the locked block from
`.claude/skills/tachi-infographics/references/executive-architecture.md`,
substitutes the 5 `<<...>>` slots, and writes `iteration-1/prompt.txt`
(8,058 characters).

Slot map applied:
- `<<project_name>>` → `second-brain-mcp` (derived from dataset path)
- `<<layer_block>>` → 3 layer stanzas with components per `layers[]`
- `<<callout_block>>` → 5 callout entries from `callouts[]`
- `<<empty_layer_block>>` → 1 entry (Supabase Platform — no qualifying findings)
- `<<single_zone_caption>>` → empty (multi-zone fallback inactive)

### Step 3 — Gemini API call

```bash
python3 specs/212-improve-executive-architecture-infographic/artifacts/iteration-1/call_gemini.py
```

POSTed to `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
using fallback chain (`gemini-3-pro-image-preview` -> `gemini-3.1-flash-image-preview`
-> `gemini-2.5-flash-image`). Succeeded on first model:

| Field | Value |
|-------|-------|
| Model used | `gemini-3-pro-image-preview` |
| HTTP status | 200 OK |
| Wall-clock | 26.9s |
| Response MIME | `image/jpeg` |

#### Mechanical iteration note (within iteration-1 budget)

The first request body included `aspectRatio: "2:3"` and `imageSize: "2K"`
in `generationConfig` (per `gemini-prompt-construction.md` §Gemini API
Configuration). The v1beta `generateContent` endpoint rejected these as
`UNKNOWN_FIELD` (HTTP 400). Removed both fields and retried — succeeded.
The orientation directive ("Orientation: portrait, 8.5:11 page aspect
ratio") inside the verbatim block conveys aspect ratio to the model
without the explicit config field. This is a **request-envelope** fix,
NOT a verbatim-prompt edit — FR-212-6 lock is preserved untouched. The
rejection is logged in `api-response.txt` (excerpt) and `call_gemini.py`
carries an inline comment explaining the workaround for future runs.

---

## Output

| File | Purpose | Notes |
|------|---------|-------|
| `spec.json` | Producer payload (input to prompt) | 110 lines, 5 callouts |
| `prompt.txt` | Substituted verbatim Gemini prompt | 8,058 chars |
| `build_prompt.py` | Helper that performed slot substitution | Reusable for future iterations |
| `call_gemini.py` | Helper that POSTed to Gemini API | Records audit trail in api-response.txt |
| `api-response.txt` | Gemini response audit trail | HTTP status, model, MIME, byte count |
| `threat-executive-architecture.jpg` | **Regenerated infographic** | 626,155 bytes |

### threat-executive-architecture.jpg

| Attribute | Value |
|-----------|-------|
| Path | `specs/212-improve-executive-architecture-infographic/artifacts/iteration-1/threat-executive-architecture.jpg` |
| Size | 626,155 bytes (611 KiB) |
| Format | JPEG (JFIF 1.01, baseline, precision 8, 3 components) |
| Dimensions | 912 × 1168 px (portrait, ≈ 8.5:11 ratio) |
| Density | 300×300 DPI |
| SHA-256 | `6b22aee4187c56da4287d71c4c86fffbe61bf447ef922327a062c141b1211acb` |

---

## Mechanical PASS/FAIL gates

| Gate | Target | Actual | Result |
|------|--------|--------|--------|
| File exists | `iteration-1/threat-executive-architecture.jpg` | exists | PASS |
| Non-zero size | > 0 bytes | 626,155 bytes | PASS |
| Valid JPEG | `file` reports JPEG | JPEG image data, JFIF standard 1.01 | PASS |
| Size in sensible range | baseline 572,237 B ± 50% (≈ 286 KB – 858 KB) | 626,155 bytes (+9.4% vs baseline) | PASS |
| Portrait orientation | aspect ratio < 1 | 912×1168, ratio 0.78 | PASS |
| Verbatim-lock preserved | locked block unmodified | substitution only on `<<...>>` slots | PASS |

All mechanical gates PASS — no further iterations required for this task.

---

## What is NOT validated by T009

Per task description ("Do NOT iterate based on visual quality — that's
T010's scope"), this task does NOT validate:

- SC-212-1 (4 structural visual criteria): nodes-vs-text rendering;
  arrows-with-arrowheads; leader-lined callouts; ≥5 callouts visible
- SC-212-2 (empty-layer page-height waste ≤15%)
- Visual side-by-side comparison vs. the OpenClaw reference asset

T010 (PM visual review) is the gate for those criteria. T010 is currently
**blocked** on the OpenClaw reference asset
(`openclaw-agent-threat-model-infographic.jpg`), which is not present on
the local filesystem.

---

## Iteration discipline

Risk R1 budget: up to 3 iterations.
This run: **iteration 1 of 3 used.** Stop condition met (mechanical PASS
with valid JPEG of sensible size).

Future iterations (if invoked by T010 visual review feedback) will use
this directory's `build_prompt.py` and `call_gemini.py` as the canonical
toolchain, writing into `iteration-2/`, `iteration-3/` subdirectories of
`specs/212-improve-executive-architecture-infographic/artifacts/`.
