# Quickstart: Citation-URL Remediation (F-333)

A runbook for applying and accepting the 41-citation remediation. Order matters: **research gates apply; the live monitor run is strictly last.**

## 0. Prereqs
- Branch `333-citation-url-remediation`, draft PR #339 open.
- `#332` is open with 41 confirmed-rot findings (the canonical list lives in the #332 body).

## 1. W0 — Research & adjudicate (gates W1)
For each class, confirm the fix against the authoritative source, verifying **runner-egress** reachability (the only thing that self-closes #332):
- **ATLAS**: confirm all 36 `AML.Txxxx` IDs exist in `https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/data/techniques.yaml`. Confirm `atlas.mitre.org/techniques/` 404s the runner client but renders in a browser → **re-classify** (D1). Flag any genuinely-retired ID for per-ID handling.
- **NIST**: find the current canonical AI 100-1 (core RMF) landing page; confirm it is AI 100-1, not AI 600-1.
- **OWASP**: probe the 16 distinct `genai.owasp.org` URLs; record the **actual** dead-set (non-year `llm02/03/05`, year-suffixed `llm0X2025`, 2 Agentic pages). Confirm `llm01-prompt-injection/` is **live** (do not touch).
- **Architect signs the fork resolution** before W1.

## 2. W1 — Apply (parallel)
- **NIST (FR-3)**: replace the shared dead DOI in `schemas/taxonomy/nist-ai-rmf.yaml` with the verified canonical → cascades to all 73 records.
- **OWASP (FR-4)**: re-point only the confirmed-dead `genai.owasp.org` citations in `crosswalk.yaml`; leave `llm01` byte-unchanged.
- **ATLAS (FR-2, likely re-classify)**: add the host-override (D2) in `scripts/check-citation-urls.py`; update the `mitre-atlas.yaml` R7/FR-033 header comment to record the resolution. (Re-point only if W0 overturned R7.)
- **FR-7 grep (D5)**: `grep -r` the in-scope strings across baselined render artifacts; expect zero hits → no regen.

## 3. W2 — Validate (offline) then gate (live)
- **Offline**: `pytest tests/schemas/test_taxonomy_integrity.py::test_citation_shape` green; run the new synthetic-404 verdict test (asserts `atlas.mitre.org`,404→NEEDS_REVIEW and other-host,404→LINK_ROT). No network.
- **Code review**: binding NFR-005 check — the override is host-scoped, documented, reversible; global frozensets untouched.
- **Acceptance (FR-6, last, async)**: dispatch the monitor as a full sweep —
  ```
  gh workflow run tachi-citation-linkrot.yml -f no_cache=true   # after the no_cache input is added
  ```
  Await the run; confirm **#332 self-closes** with its recovery comment and zero in-scope confirmed rot. Record the run URL + comment as delivery evidence. Open a sampled corrected URL in a browser and confirm it renders the **cited item** (landing-content spot-check).

## Done when
41/41 resolved or correctly re-classified · #332 self-closed on a `--no-cache` run · landing spot-check passes · `test_citation_shape()` green · synthetic-404 test green · zero new deps · fork resolution recorded.
