# Acceptance Evidence — F-333 Citation-URL Remediation (US4 / FR-006 / SC-002–SC-003)

> **Result: PASS.** #332 self-closed on a `--no-cache` full-sweep monitor run with
> zero confirmed link-rot. Captured at `/aod.deliver` (T017/T018), 2026-06-29.

## T017 — Monitor-driven acceptance (#332 self-close)

The acceptance gate is a live GitHub Actions run (network + `gh` issue lifecycle),
gated out of CI by the ADR-021 determinism boundary, so it is run/awaited at deliver
(per F-183 KB Entry 17). Both runs were dispatched on the feature branch ref with the
new `no_cache=true` full-sweep input (T013).

### Run 1 — surfaced an out-of-scope false positive (adjudication)

| Field | Value |
|-------|-------|
| Run URL | https://github.com/davidmatousek/tachi/actions/runs/28395064052 |
| Dispatch | 2026-06-29T18:48Z · `workflow_dispatch` · `no_cache=true` · ref `333-citation-url-remediation` |
| Conclusion | `success` (monitor is a watch, not a gate — green even when rot is found) |
| #332 | **stayed OPEN** — `1 confirmed link-rot finding` |
| Finding | `https://doi.org/10.6028/NIST.AI.600-1` (NIST **AI 600-1** GenAI Profile, `nist-ai-600-1.yaml`, 12 records) — *previously healthy 2026-06-15* |

**In-scope verdict (all 41 cleared):** ATLAS → 38 `needs-review` (host override working,
not confirmed rot); NIST **AI 100-1** (73 records) → not reported; OWASP re-points → not
reported. The sole confirmed-rot finding was **out of F-333's scope** (AI 600-1 is a
distinct catalog the spec explicitly scoped out — US2 AC-2, FR-003).

**Adjudication (spec edge case "anti-bot 404 vs. genuine rot"):** AI 600-1 is **not dead**.
Replicating the monitor's exact probe showed `nvlpubs.nist.gov` (the doi.org redirect
target) returns **HTTP 404 to HEAD but 2xx to GET** for its PDFs. The checker probed
HEAD-first and did not retry 404 as GET (404 ∉ `_HEAD_RETRY_AS_GET`), so it false-flagged
a live document as confirmed rot. The same behavior affects the AI 100-1 DOI.

```
HEAD https://doi.org/10.6028/NIST.AI.600-1  -L → 404  (final nvlpubs…/NIST.AI.600-1.pdf)
GET  https://doi.org/10.6028/NIST.AI.600-1  -L → 200  (final nvlpubs…/NIST.AI.600-1.pdf)
HEAD nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf       → 404
GET (ranged) nvlpubs.nist.gov/…/NIST.AI.600-1.pdf         → 206  ← document is alive
```

**Resolution (owner-approved root-cause fix at the gate):** add `404` to
`_HEAD_RETRY_AS_GET` so a HEAD 404 is re-issued as a ranged GET before classification; a
genuinely dead URL (404 on both methods) still classifies as LINK_ROT. Synthetic unit
tests added (HEAD 404 → GET 206 → HEALTHY; HEAD 404 → GET 404 → LINK_ROT). Offline suite
green (26), no network. See commit `fix(333): GET-retry HEAD 404 …`.

### Run 2 — acceptance PASS (#332 self-closed)

| Field | Value |
|-------|-------|
| Run URL | https://github.com/davidmatousek/tachi/actions/runs/28396258501 |
| Dispatch | 2026-06-29T19:10Z · `workflow_dispatch` · `no_cache=true` · ref `333-citation-url-remediation` |
| Conclusion | `success` |
| #332 | **CLOSED** @ 2026-06-29T19:12:02Z |
| Self-close comment | `All citations healthy as of 2026-06-29T19:12Z. Closing.` |
| In-scope confirmed rot | **0** |

✅ **SC-002 met** — the end-to-end acceptance gate (a green #332) confirms every fix reaches
the monitor's runner egress, not just a local edit that looks right.

## T018 — Landing-content spot-check (SC-003)

Sampled corrected URLs were fetched and confirmed to render the specific cited item (not a
generic/un-anchored page). The ATLAS re-classify path changes no URL, so no ATLAS sample
(per PM-M3). *Method: content-fetch verification of the live landing page.*

| Class | URL | Renders | Verdict |
|-------|-----|---------|---------|
| NIST | `https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10` | "Artificial Intelligence Risk Management Framework (AI RMF 1.0)" — **AI 100-1 core RMF**, correctly *not* AI 600-1 | ✅ (US2 AC-2) |
| OWASP | `https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/` | "LLM02:2025 Sensitive Information Disclosure" | ✅ (US3 AC-3) |

✅ **SC-003 met** — no wrong-but-2xx landing; each URL lands on the cited content.

## Success-criteria roll-up

| SC | Statement | Status |
|----|-----------|--------|
| SC-001 | 41/41 in-scope citations resolved or correctly re-classified | ✅ (Run 2: 0 in-scope confirmed rot) |
| SC-002 | #332 self-closes on a `--no-cache` sweep | ✅ (Run 2, closed 19:12:02Z) |
| SC-003 | Landing spot-check passes | ✅ (NIST + OWASP) |
| SC-009 | `llm01-prompt-injection/` byte-unchanged | ✅ (regression guard; untouched both files) |

**Out-of-scope follow-through:** the AI 600-1 false positive exposed a general monitor
limitation (HEAD-hostile origins). Fixed at the root in F-333 (owner-approved), so no
separate follow-up is needed; the lesson is captured in the delivery record + KB.
