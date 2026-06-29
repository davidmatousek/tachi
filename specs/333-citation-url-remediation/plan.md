---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-29
    status: APPROVED
    notes: "Plan faithfully realizes the PM-approved spec + v1.1 PRD — all 8 FRs → explicit decisions (D1–D5 / Affected Components / Build Waves); research-first discipline structurally enforced by W0→W1→W2 gating; FR-006 monitor-driven #332 self-close + landing spot-check + --no-cache sweep all present and ordered strictly-last/async. Zero scope creep (#325 OUT; the no_cache dispatch input is FR-006-sanctioned, not creep; CI-wiring explicitly declined per YAGNI). All 3 PM carry-forwards resolved (edit-surface math 36-distinct/~133; offline-test placement; --no-cache mechanism). 5 findings, MINOR/observational, 0 blocking — carry to tasks: M2 add a confirm-deferred #325 no-op item (FR-005 AC-1 expects a documented-deferred artifact at deliver); M3 name the spot-check sample (1 NIST + 1 OWASP corrected URL — ATLAS re-classify changes no URL); M4 add a #332-non-close → re-adjudicate fallback note (R1 loop-back); M1 echo the feature-P0-vs-story-P1/P2 note; M5 (positive) keep classifier-verdict-contract.md + D5 grep targets. Full: .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-06-29
    status: APPROVED
    notes: "HOW-level review complete; resolves the PRD HIGH at the design level. D1/D2 make the ATLAS paths non-co-equal via a bounded host→status override inside _verdict_for_status (verified :447 already receives url → NO classify_one() refactor; global frozensets :288/:290 untouched → NFR-005 real-rot detection preserved). D3 --no-cache workflow_dispatch input stays inside the scheduled-only surface (ADR-021/NFR-3 intact; --no-cache→should_skip already plumbed :982, ~6-line YAML). D4 synthetic-404 offline test preserves ADR-021, no new PR-CI wiring (YAGNI-correct, #329 owns wiring). D5 render-exposure grep sound (extract-report-data.py:1140–1193 reads IDs/counts not citation strings; ORDERED_FRAMEWORKS :1077). classifier-verdict-contract.md guarantees correct incl. status-scoping (genuine 410/451 still flags on the anti-bot host). Constitution Check accurate; empty Complexity Tracking justified. Every spot-checked file:line EXACT (37 ATLAS / 73 NIST / 16 OWASP / F-338 disjoint). 0 blocking; 2 build-wave observational → carry to tasks: OBS-1 land _HOST_STATUS_OVERRIDES with a header comment cross-referencing the mitre-atlas.yaml:18–26 R7 tripwire (data↔code point at each other); OBS-2 the W0→W1 architect fork sign-off is load-bearing, must not be skipped. Full: .aod/results/architect.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Citation-URL Remediation (BLP-06 Wave 1)

**Branch**: `333-citation-url-remediation` | **Date**: 2026-06-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/333-citation-url-remediation/spec.md` (PM APPROVED)

## Summary

Remediate the 41 dead citation URLs the #183 monitor surfaced (#332 tracker) across `schemas/taxonomy/`, in three research-first fix-classes, so a subsequent `--no-cache` monitor run self-closes #332. **Technical approach**: research/adjudicate each class against its authoritative source (W0), then apply the evidence-supported fix (W1) — for ATLAS the **likely** fix is a **host-scoped re-classify** of the monitor's verdict logic (a stdlib-only change inside `_verdict_for_status`, which already receives the URL), *not* a data edit; NIST is a one-URL→73-record cascading data edit; OWASP is a bounded data edit over the adjudicated dead-set. Validate offline (synthetic-404 unit test + `test_citation_shape()` green) and gate on the live monitor run (W2). Zero new runtime dependencies; the ADR-021 determinism boundary is preserved (no network on any `pull_request`/`push` path).

## Technical Context

**Language/Version**: Python 3 (stdlib only — `urllib`, `re`; matches the existing `scripts/check-citation-urls.py`)
**Primary Dependencies**: None new. Existing: PyYAML (already in manifest) for the taxonomy catalogs; GitHub Actions for the scheduled monitor.
**Storage**: YAML taxonomy catalogs (`schemas/taxonomy/{mitre-atlas,nist-ai-rmf,crosswalk}.yaml`) — flat files, no DB.
**Testing**: pytest (offline). Existing `tests/schemas/test_taxonomy_integrity.py::test_citation_shape` (regex/file-only, no fetch) must stay green; a new synthetic-404 unit test for the verdict logic (no live fetch).
**Target Platform**: Local dev + GitHub Actions (the `tachi-citation-linkrot.yml` monitor, `runs-on: ubuntu-latest`, scheduled + `workflow_dispatch` only).
**Project Type**: single (data catalogs + one stdlib script + a scheduled workflow). No frontend/backend/API surface.
**Performance Goals**: N/A (a weekly monitor + one-time edits; no latency/throughput target).
**Constraints**: ADR-021 determinism boundary — **no network in any `pytest`/`pull_request`/`push` job**; reachability validation stays scheduled-only. Zero new runtime dependency. Re-classify change must be host-scoped + reversible (NFR-005). Acceptance is *runner-egress* 2xx, not local-client 2xx.
**Scale/Scope**: 41 findings = 36 distinct ATLAS IDs (~133 occurrences on the unlikely re-point path) + 1 NIST DOI → 73 records + a subset of 16 distinct OWASP URLs.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after design (below).*

| Principle | Applies? | Status | Notes |
|---|---|---|---|
| I. General-Purpose Architecture | Partial | ✅ PASS | Edits are to tachi's own taxonomy data + monitor; no new domain-coupling in core. |
| II. API-First Design | No | N/A | No API surface — data + scheduled script only. |
| III. Backward Compatibility (NON-NEG) | Yes | ✅ PASS | Citation **values** change; the record **schema/shape is unchanged** (FR out-of-scope bars schema/field changes). The re-classify is host-scoped + reversible. Local `.aod/` workflows untouched. |
| IV. Concurrency & Data Integrity | No | N/A | No state machine / locking surface. |
| V. Privacy & Data Isolation | No | N/A | Public citation URLs only; no PII, no secrets, no auth surface. |
| VI. Testing Excellence | Yes | ✅ PASS | New verdict-logic branch unit-tested over a **synthetic 404** (both the `atlas.mitre.org`→needs-review and other-host→rot cases); `test_citation_shape()` kept green; tests are offline (Test-First for the host-override branch). |
| VII. Definition of Done (NON-NEG) | Yes | ✅ PASS | The **monitor-driven #332 self-close** IS the "User Validated" DoD step (real-world confirmation on the live runner) + landing-content spot-check. Deliver-adjacent live run, per F-183 precedent (KB Entry 17). |
| VIII. Observability & RCA | Yes | ✅ PASS | Header-comment updates (R7 TRIPWIRE / FR-033) record what changed and why — load-bearing institutional memory (NFR-004); delivery record captures the fork-resolution evidence. |
| IX. Git Workflow (NON-NEG) | Yes | ✅ PASS | Feature branch `333-*` + draft PR #339 open; `feat(333):` title for release. |
| X. Product-Spec Alignment (NON-NEG) | Yes | ✅ PASS | Approved PRD → PM-approved spec → this plan. Scope bounded to spec; #325 + Waves 2–3 explicitly out. |
| Determinism boundary (ADR-021) | Yes | ✅ PASS | No network added to any PR/push job; classifier change stays inside the scheduled-only workflow; synthetic-404 test only. |

**Gate result: PASS** (no violations → Complexity Tracking empty).

## Technical Decisions (Phase 0)

Phase-0 grounding is in [research.md](./research.md) (KB + in-tree-verified codebase + architecture + web). The load-bearing technical decisions:

### D1 — ATLAS resolution = host-scoped re-classify (preferred path)
- **Decision**: Treat the ATLAS class as the **re-classify** path unless W0 evidence overturns the R7 determination. Keep all `atlas.mitre.org/techniques/AML.Txxxx` citations **as-is**; narrow the monitor so that host's 404s become NEEDS_REVIEW.
- **Rationale**: The R7 TRIPWIRE note (`mitre-atlas.yaml:18–26`) + both Triad reviewers (in-tree verified) establish the 404s are anti-bot gating, not rot; the IDs are valid (verified against `atlas-data`). The monitor runs on a GitHub runner, so #332 self-close needs *runner-egress* 2xx — and **any** `atlas.mitre.org` path 404s that runner, so re-pointing same-host is a non-starter; re-pointing to the flat `atlas-data` blob is a wrong-but-2xx anti-pattern (un-anchored 1.5MB dump, no per-technique fragment). Re-classify is smaller, reversible, preserves the correct human URL, and is the only path that both passes FR-6 *and* avoids the NFR-1 trap.
- **Alternatives considered**: (a) flat-blob re-point — REJECTED (anti-pattern, misleads analysts); (b) same-host re-point — REJECTED (still 404s the runner, FR-6 fails); (c) per-ID re-point — reserved for any individual ID W0 finds genuinely retired/moved.

### D2 — Classifier host-scoping = bounded host→status override inside `_verdict_for_status` (the "stay" side of the split valve)
- **Decision**: Add a small, documented, module-level host-override table consulted at the top of `_verdict_for_status(url, status, final_url, detail)` (`check-citation-urls.py:447`): if the URL's host is a known anti-bot host AND the status is in that host's override set, return `NEEDS_REVIEW` instead of falling through to the global `_HARD_ROT_STATUSES` check. Shape (illustrative): `_HOST_STATUS_OVERRIDES = {"atlas.mitre.org": {404: Verdict.NEEDS_REVIEW}}`. The global frozensets (`:288/:290`) are untouched → real-rot detection on every other host is preserved (NFR-005).
- **Rationale**: `_verdict_for_status` **already receives `url`** (verified in-tree), so host-scoping is a bounded, local addition — **no `classify_one()` control-flow refactor**. This keeps us on the Team-Lead's pre-authorized "stay" branch (bounded override map + one test), not the "split" branch.
- **Split-valve trigger (Team-Lead C2)**: IF host-scoping turns out to require restructuring `classify_one()`/the call graph (it should not, given the signature), THEN split the classifier work to a BLP-06 Wave 2 sibling and ship F-333 with NIST+OWASP data fixes only. Decision criterion recorded so the build wave can branch without re-planning.
- **Alternatives considered**: (a) broaden `_NEEDS_REVIEW_STATUSES` to include 404 globally — REJECTED (blinds the monitor to real rot everywhere, violates NFR-005); (b) exclude `atlas.mitre.org` from monitoring entirely — REJECTED (loses real-rot detection if ATLAS ever genuinely moves).

### D3 — `--no-cache` acceptance mechanism = add a `workflow_dispatch` boolean input
- **Decision**: Add a `no_cache` boolean `workflow_dispatch` input to `tachi-citation-linkrot.yml` wired to the script's existing `--no-cache` flag (`:923`), so the FR-6 acceptance run is a guaranteed full sweep.
- **Rationale**: The TTL ledger `should_skip` (default 21 days, `:568`) could otherwise skip an in-scope URL on a pre-rot `last_ok` and self-close on stale data. The workflow today exposes only `inject_sentinel_rot` — there is no `--no-cache` lever (verified). Benign for the dead-then-fixed URLs (no `last_ok`), but the gate must not depend on that subtlety. Adding the input is small, reusable, explicit, and **stays inside the scheduled-only/`workflow_dispatch` surface** (NFR-003 intact — not a PR trigger).
- **Alternatives considered**: clear the `actions/cache` ledger manually — REJECTED (a non-reproducible side effect, harder to audit than a declared input).

### D4 — Synthetic-404 unit test = offline, table-driven over `_verdict_for_status`; build-gate + local, no new PR-CI wiring
- **Decision**: Add an offline pytest exercising `_verdict_for_status` over synthetic statuses: assert `("https://atlas.mitre.org/techniques/AML.T0051", 404) → NEEDS_REVIEW` and `("https://example.org/x", 404) → LINK_ROT`. No network. **Extend the existing `tests/schemas/test_citation_linkrot_parity.py`** (reuse its importlib hyphenated-module loader + socket guard — Architect OBS-3) rather than a fresh file; it runs in the local suite + the `/aod.build` security/test gate.
- **Rationale**: Pure function, table-driven (the `--inject-sentinel-rot` precedent proves the offline-verdict pattern). Network-free, so it *could* be a PR gate — but the existing citation tests are **not** wired into CI today (verified), and wiring citation tests into the PR CI is a separate hardening concern (#329 / BLP-06 Wave 2). **This feature does not expand CI wiring** (YAGNI; spec deferred placement to plan → decision: add the offline test, run it in the build gate + locally, do not newly gate the PR). If F-338 (which edits `tachi-pytest.yml`) merges near-simultaneously, run F-333's test against post-338 `main` (INFO C6).
- **Alternatives considered**: a live-fetch integration test — REJECTED (breaches ADR-021); wiring all citation tests into PR CI now — DEFERRED (out of scope, #329).

### D5 — FR-7 rendering-exposure check = grep the baselined artifacts for the corrected strings
- **Decision**: Before/at apply time, grep the byte-baselined render artifacts (the `examples/*/security-report.pdf.baseline` text layer + any coverage/personalized-tree baseline docs) for the in-scope citation strings (`atlas.mitre.org/techniques`, `doi.org/10.6028/NIST.AI.100-1`, `genai.owasp.org`). Expected: **zero hits** (the report aggregator reads `record.get("id")`/counts, never citation strings — verified `extract-report-data.py:1140–1193`). If zero → no regen. If any hit (or if FR-2 ever adds/removes a *record*), run the ADR-037 D-9 baseline-regen lane and prove CA-only deltas.
- **Rationale**: `mitre-atlas` + `nist-ai-rmf` ∈ `ORDERED_FRAMEWORKS` (`:1077`), which is the #185 trap predicate — but that lesson couples to *record count*, not citation *strings*. Verify-not-assume (cheap grep) per the F-185 KB lesson.
- **Alternatives considered**: assume no exposure and skip the check — REJECTED (the #185 lesson is exactly "don't assume membership ⇒ safe"); regenerate baselines unconditionally — REJECTED (wasteful if no exposure, and would itself drift baselines).

## Affected Components & Edit Surface

*(Non-canonical heading — this feature introduces no new architecture, so the auto-system-design append to the byte-baselined `docs/architecture/01_system_design/README.md` is intentionally skipped.)*

| File | Class | Change (likely path) | Surface |
|---|---|---|---|
| `scripts/check-citation-urls.py` | ATLAS (FR-2) | Host-override table + `_verdict_for_status` guard (re-classify) | ~5–15 LOC + comment |
| `schemas/taxonomy/mitre-atlas.yaml` | ATLAS (FR-2) | **Re-classify path: header comment only** (R7/FR-033 note). Re-point path (unlikely): 37 `url:` fields | comment / ~37 lines |
| `schemas/taxonomy/crosswalk.yaml` | ATLAS + OWASP (FR-2/FR-4) | Re-classify ATLAS: untouched. OWASP: re-point confirmed-dead `genai.owasp.org` URLs (non-year + `llm0X2025` twins + 2 Agentic pages); **leave `llm01` live** | OWASP subset of 16 distinct |
| `schemas/taxonomy/owasp.yaml` | OWASP (FR-4) | Re-point the dead `genai.owasp.org` URLs here too (10 `llm0X2025` + 1 Agentic page); **leave `llm01` live** | 11 distinct (Team-Lead Concern 1) |
| `schemas/taxonomy/nist-ai-rmf.yaml` | NIST (FR-3) | Replace the shared DOI → verified AI 100-1 canonical (cascades to 73 records) | 73 records, 1 pattern |
| `.github/workflows/tachi-citation-linkrot.yml` | Acceptance (FR-6) | Add `no_cache` `workflow_dispatch` input | ~6 lines |
| `tests/schemas/test_citation_linkrot_parity.py` (extend) | Test (FR-8) | Synthetic-404 verdict unit test (offline; reuses the existing importlib loader + socket guard — Architect OBS-3) | +1 test case |

**Edit-surface math anchor (PM F4)**: the re-point surface is **36 distinct / ~133 occurrences**, not the ~38 finding count — relevant only on the unlikely ATLAS re-point path. The likely path edits zero ATLAS data.

## Remediation Flow (Build Waves)

Traces to `feasibility-check.md` (Team-Lead, 3.0 eng-day central):

- **W0 — Research & Adjudication (gates everything, ~1.0d)**: `web-researcher` fan-out over the 3 classes — verify 36 ATLAS IDs in `atlas-data/techniques.yaml` + **runner-egress** reachability; find NIST AI 100-1 canonical; adjudicate the real OWASP dead-set (incl. `llm0X2025` year-suffixed + 2 Agentic pages). **Architect signs the fork resolution** (a How decision) before W1.
- **W1 — Apply (~1.25d)**: `senior-backend-engineer` — FR-3 NIST cascade ∥ FR-4 OWASP re-point (leave `llm01`) ∥ FR-2 ATLAS (re-classify per D1/D2; re-point only if W0 overturns R7). D5 FR-7 grep. Update header comments.
- **W2 — Validation & Gate (~0.75d + ~0.5d wall-clock)**: `tester` (synthetic-404 unit test + `test_citation_shape()` green) → `code-reviewer` (binding; NFR-005 host-scoping discipline) → FR-6 **dispatch the monitor (`no_cache=true`) + await #332 self-close** (strictly last, async; the real DoD gate) + landing-content spot-check.

## Test Strategy

- **Offline, deterministic** (ADR-021): `test_citation_shape()` stays green (regex/file-only); new synthetic-404 unit test over `_verdict_for_status` (D4). No network in any PR/push job.
- **Live, deliver-adjacent (MANUAL-ONLY)**: the FR-6 monitor dispatch + #332 self-close + landing spot-check — gated out of CI by design; run during deliver (F-183 KB Entry 17 precedent: schedule the live validation INTO deliver, don't punt it).

## Re-Check: Constitution (post-design)

No new violations introduced by the design. The host-override table is bounded/documented/reversible (III, NFR-005); tests are offline (VI, ADR-021); zero new deps (NFR-002); acceptance is the live monitor (VII). **Gate result: PASS.**

## Complexity Tracking

*No constitutional violations — none to justify.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
