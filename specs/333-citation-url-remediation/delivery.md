# Delivery Record — F-333 Citation-URL Remediation (BLP-06 Wave 1)

| Field | Value |
|-------|-------|
| Feature | #333 — Citation-URL Remediation |
| Branch | `333-citation-url-remediation` |
| PR | #339 (`feat(333): citation-URL remediation — close the link-rot the monitor opened`) |
| Delivered | 2026-06-29 |
| Acceptance gate | **#332 self-closed** 2026-06-29T19:12:02Z (run 28396258501) — see `test-results/acceptance.md` |
| Tasks | 20/20 (T001–T016 build; T017–T020 deliver-time) |

## What shipped

Resolved the 41 dead-citation findings the #183 link-rot monitor opened in tracker #332,
across three research-first fix-classes, so #332 self-closes on a `--no-cache` sweep without
introducing a "wrong-but-alive" redirect.

- **ATLAS (38 findings, 36 distinct IDs)** — host-scoped **re-classify**, **zero data edits**.
- **NIST AI 100-1 (1 DOI → 73 records)** — re-point to the NIST AI RMF 1.0 landing page.
- **OWASP (subset of 16 distinct)** — re-point 4 confirmed-dead `genai.owasp.org` URLs + normalize the `llm04` twin; `llm01-prompt-injection/` left byte-unchanged (SC-009 guard).
- **Monitor `no_cache` dispatch input** (T013) + **HEAD-404 GET-retry root-cause fix** (deliver-gate, owner-approved).

## Fork-resolution evidence (SC-004) — paths are not co-equal

Full adjudication in `test-results/fork-resolution.md` (architect-signed gate, commit `b11f0b4`).
Summary of which path each class took and why:

| Class | Path taken | Why (authoritative source) |
|-------|-----------|----------------------------|
| **ATLAS** | **Re-classify** (host-scoped `_HOST_STATUS_OVERRIDES`: `atlas.mitre.org` 404 → NEEDS_REVIEW). Citations unchanged; 0 data edits across 37 `url:` + ~96 `crosswalk` refs. | MITRE `atlas-data/techniques.yaml` confirms all 36 IDs valid; R7 anti-bot determination **upheld** — the 404s are SPA/anti-bot gating, not rot. Re-pointing to any `atlas.mitre.org` path still 404s the runner (non-starter); the flat `atlas-data` blob is the named wrong-but-2xx anti-pattern (rejected). |
| **NIST** | **Re-point** DOI → `https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10` (cascades to 73 records). | Verified canonical AI 100-1 (core RMF), confirmed distinct from AI 600-1 (GenAI Profile) by landing-content check (T018). |
| **OWASP** | **Re-point** 4 confirmed-dead crosswalk strings + normalize `llm04` non-year twin to the 2025 canonical (trailing-slash convention preserved, RULING B); `owasp.yaml` all-live (0 edits); `llm01` byte-unchanged in both files. | research-owasp.md restructured-site canonicals; dual-UA verified. |
| **#325 hygiene** | **OUT** (FR-005). | 31 `tachi-control-category → nist-ai-rmf` edges cite a local file, not the dead DOI — distinct defect class. Documented in `deferred-325.md` (T020). |

## Acceptance-gate finding & root-cause fix (the surprise)

The first acceptance run cleared all 41 in-scope citations but #332 held open on **one
confirmed-rot finding that was out of scope**: `doi.org/10.6028/NIST.AI.600-1` (NIST AI 600-1,
*previously healthy 2026-06-15* — not among the original 41). Adjudication showed it was a
**false positive**: `nvlpubs.nist.gov` returns **404 to HEAD but 2xx to GET**, and the checker
probed HEAD-only for 404. The document is alive; the monitor had a HEAD-hostile-origin blind
spot (which also affected the AI 100-1 DOI). Resolved at the root (owner-approved scope
expansion at the gate, FR-006 R1): `404` added to `_HEAD_RETRY_AS_GET` + synthetic tests. Re-run
→ #332 self-closed. Full evidence in `test-results/acceptance.md`.

## Definition of Done

| Requirement | Status |
|-------------|--------|
| FR-001 research-first (3 classes, authoritative sources) | ✅ research-{atlas,nist,owasp}.md + fork-resolution.md |
| FR-002 ATLAS host-scoped re-classify (not flat-blob/same-host) | ✅ `_HOST_STATUS_OVERRIDES`, status-scoped to 404 |
| FR-003 NIST DOI → canonical (73 records) | ✅ |
| FR-004 OWASP dead-set re-pointed; `llm01` untouched | ✅ |
| FR-005 #325 documented-deferred | ✅ `deferred-325.md` |
| FR-006 #332 self-close on `--no-cache` sweep + landing spot-check | ✅ run 28396258501; T018 |
| FR-007 rendering-exposure check (the #185 watch-out) | ✅ `test-results/fr7-exposure.md` — zero hits, no regen |
| FR-008 determinism boundary intact (offline tests, no PR-path network) | ✅ 26 offline tests green, synthetic-404 only |
| SC-001..003, SC-005..009 | ✅ (see acceptance.md roll-up) |

## Retrospective

| Metric | Value |
|--------|-------|
| Estimated | Single session (BLP-06 Wave 1; define → deliver same day) |
| Actual | ~6.4h same-day (branch 2026-06-29 13:08 → deliver 2026-06-29 ~19:30) |
| Tasks | 20/20 |
| Waves tested | W2 + W3 (W0 research/gate, no code) |

- **Surprise**: the acceptance gate surfaced a NEW *out-of-scope* confirmed-rot finding (AI 600-1)
  that first read as "fork resolved wrong?" but proved to be a **general monitor limitation** —
  HEAD-hostile origins (`nvlpubs.nist.gov`) return 404 to HEAD but 200 to GET. The scare became a
  one-line root-cause fix that also retro-validated the NIST documents were never dead.
- **Lesson (KB)**: A link-rot probe that trusts a HEAD 404 without a GET retry will false-flag any
  HEAD-hostile origin as dead. Probe HEAD→GET and only trust a 404 confirmed on both methods.
  Recorded in `docs/INSTITUTIONAL_KNOWLEDGE.md`.

### Build-Wave Test Results

| Wave | Tests | Passed | Failed | Status |
|------|-------|--------|--------|--------|
| wave-2 (apply) | 25 | 25 | 0 | pass |
| wave-3 (validate) | 25 | 25 | 0 | pass |
| deliver (HEAD-404 fix) | 26 | 26 | 0 | pass |

**Build Summary**: pass — 0 regressions across all waves; offline/network-free (NFR-001/ADR-021).
