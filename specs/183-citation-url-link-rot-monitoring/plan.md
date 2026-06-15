---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-14
    status: APPROVED
    notes: "Full product alignment — plan is a faithful, complete translation of the PM-approved spec/PRD: 9/9 FRs, 7/7 NFRs, 4/4 user stories each map to a concrete plan element; all 8 SCs validatable (SC-002/003 sentinel via dispatch, SC-004/005 structurally guaranteed). Both plan-stage deferrals resolved strictly within PRD latitude — zero scope creep: TL-2 sentinel (dispatch-input → pre-classified finding, the PRD's own option-menu choice) and last-known-status persistence (explicitly-offered optional PRD enhancement, one JSON field). MVP (weekly confirmed-rot signal + never-blocks-merge) delivered coherently. 3 informational notes, no action. Details: .aod/results/product-manager-183-plan.md"
  architect_signoff:
    agent: architect
    date: 2026-06-14
    status: APPROVED_WITH_CONCERNS
    notes: "Technically sound + fully baseline-faithful (every resolved baseline decision honored 1:1; codebase claims verified at HEAD). NFR-001 determinism boundary genuinely enforced by file layout + transport-boundary stubbing + import-time no-socket self-test; loopback carve-out correct; TL-2 sentinel genuinely deterministic (pre-classified, no fetch, RFC-2606 example.invalid); exit-code discipline (0 even on rot) + least-privilege + cache strategy all correct. 5 items, all folded into plan/contracts before tasks: CONCERN-1 (MED) FR-008 parity must cover BOTH surfaces — crosswalk citation (test_citation_shape) AND catalog url (test_framework_yamls_load), else ~700-URL catalog slice unguarded against field drift [encoded into plan Component 3 + Testing Strategy + W2]; CONCERN-2 (LOW) uniform ^https?:// filter for pseudo-taxonomy file-path url: [encoded]; MINOR-1 (LOW) pin combined actions/cache@v4 not restore-only [workflow contract]; MINOR-2 (LOW) devops validate cache accumulation first 2 runs [noted]; MINOR-3 (INFO) 9-files-on-disk vs 8-URL-bearing wording, no action. No redesign. Details: .aod/results/architect-183-plan.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Citation-URL Link-Rot Monitoring — Scheduled CI Check

**Branch**: `183-citation-url-link-rot-monitoring` | **Date**: 2026-06-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/183-citation-url-link-rot-monitoring/spec.md`

## Summary

Add a **weekly scheduled** GitHub Actions workflow (`.github/workflows/tachi-citation-linkrot.yml`) that invokes a **zero-dependency** Python checker (`scripts/check-citation-urls.py`). The checker glob-discovers `schemas/taxonomy/*.yaml`, extracts ~900 distinct URL-shaped citations (93% MITRE-hosted), fetches each with per-host-throttled politeness, classifies the result (healthy / link-rot / needs-review / transient), and maintains **one self-updating, self-closing tracking issue** via the native `gh` CLI. An **offline structural-parity guard** added to the deterministic `pytest` suite ensures the extractor and the existing `test_citation_shape()` see the same URL set — without any network fetch. The load-bearing invariant: **no outbound/external network call ever enters `tests/` or any PR/push-triggered job** (NFR-001).

Technical approach is fully grounded by the architect baseline (`.aod/results/architect-baseline-183.md`); all open decisions were resolved before drafting. This plan resolves the two plan-stage deferrals: the **TL-2 deterministic-sentinel mechanism** (a `workflow_dispatch` input that injects a *pre-classified* synthetic rot finding, bypassing the network) and **last-known-status persistence** (adopted — low-cost, improves issue context).

## Technical Context

**Language/Version**: Python 3.11 (matches `tachi-maestro-coverage.yml` precedent); GitHub Actions YAML; minimal bash glue in the workflow.
**Primary Dependencies**: Python **standard library only** — `urllib.request`, `concurrent.futures`, `http.client`, `json`, `re`, `glob`, `pathlib`, `argparse`, `time`, `email.utils` (for `Retry-After` parsing) — plus the already-pinned **`pyyaml>=6.0`**. **No new runtime dependency** (NFR-002). Native **`gh` CLI** (pre-installed on runners) for issue I/O (NFR-007).
**Storage**: `actions/cache@v4` holds a per-URL last-success ledger JSON (`{url: {last_ok: iso8601, last_status: int}}`) in the runner workspace — **never committed to the repo** (FR-006). No database.
**Testing**: `pytest` (offline parity guard FR-008, classifier unit tests with mocked responses); live `workflow_dispatch` validation for the issue lifecycle (FR-001/FR-007). Test-first for the classifier and parity guard.
**Target Platform**: GitHub-hosted `ubuntu-latest` runner; Python via `actions/setup-python@v5`.
**Project Type**: single — CI tooling/script (no app, no frontend, no API service).
**Performance Goals**: a full uncached sweep of ~900 URLs at per-host concurrency 2–3 / global 10 + politeness delay completes in **minute-scale** (well inside a weekly job budget); steady-state load cut ~⅔ by the ~21-day cache TTL.
**Constraints**: **NFR-001 determinism boundary** (no outbound fetch in `tests/`/PR/push path; checker not importable from pytest collection) — the single hardest constraint; zero new runtime dependency; least-privilege token (`contents: read` + `issues: write`); polite per-host throttling (no WAF ban); low false-positive signal (403/401/429 = needs-review).
**Scale/Scope**: ~900 distinct URLs across **7 hosts** (MITRE 835/93%), 9 taxonomy YAMLs (glob-discovered; surface grows with each catalog). One new workflow + one new script (~150–250 LOC) + one pytest module + one README line edit.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle / Standard | Assessment | Status |
|---|---|---|
| **I. General-Purpose Architecture** | The checker is generic URL-health logic operating on data files; it adds no domain/security reasoning to core scanner components. Standalone CI tool, cleanly separable. | ✅ PASS |
| **VI. Testing Excellence** | FR-008 offline parity guard + classifier unit tests (mocked responses, no network) added to the deterministic suite; lifecycle validated by dispatch. Test-first for classifier + guard. | ✅ PASS |
| **VII. Definition of Done** | Satisfied at deliver (CHANGELOG, closure docs, sign-offs). | ⏳ deferred to deliver |
| **IX. Git Workflow & Feature Branching** | On `183-citation-url-link-rot-monitoring`; draft PR #330 open; no direct main commits. | ✅ PASS |
| **X. Product-Spec Alignment & Dual Sign-off** | spec.md PM-APPROVED; this command supplies PM + Architect dual sign-off on plan.md. | ✅ PASS (in progress) |
| **Security Standards** | No secrets in code (ambient `GITHUB_TOKEN`); least-privilege scope; supply-chain minimalism (native `gh`, no marketplace action); input is repo-owned YAML. | ✅ PASS |
| **Code Quality (Type Safety, no silent failures)** | Python type hints on the checker; explicit classification + graceful degradation (transient never reported, cache-miss = check-all). | ✅ PASS |

**No violations.** Complexity Tracking table is intentionally empty. The inherited DB/frontend/MCP/vector-search constraints in the constitution do not apply to a CI/tooling feature.

## Tech Stack

- **Runtime**: Python 3.11 standard library (`urllib.request`, `concurrent.futures.ThreadPoolExecutor`, `http.client`, `json`, `re`, `glob`, `pathlib`, `argparse`, `time`, `threading.Semaphore`, `email.utils.parsedate_to_datetime`).
- **Parsing**: `pyyaml>=6.0` (already pinned in `requirements-dev.txt`) via `yaml.safe_load`.
- **CI**: GitHub Actions — `actions/checkout@v4`, `actions/setup-python@v5` (3.11), `actions/cache@v4`.
- **Issue I/O**: native `gh` CLI with ambient `GITHUB_TOKEN` (`issues: write`).
- **Tests**: `pytest>=8.0` (offline parity + classifier unit tests).
- **Zero new runtime dependency** — the deliberate stdlib path (NFR-002).

## Components

1. **`scripts/check-citation-urls.py`** (new, ~150–250 LOC) — the checker. Subcomponents:
   - `discover_urls()` — glob `schemas/taxonomy/*.yaml`, `yaml.safe_load`, extract `citation` (crosswalk) / `url` (catalogs), filter `^https?://`, drop file-paths, dedup, build `url → [source-location]` back-reference map.
   - `classify_url()` — HEAD→ranged-GET fallback, ≤5 redirects, 2 retries (exp backoff + jitter) on transient only, never retry 4xx; returns a `Classification`.
   - `HostThrottler` — per-host `Semaphore` (cap 2–3) under a global pool (10) + per-host politeness delay; descriptive UA + `Accept`; honors `Retry-After`.
   - `Ledger` — load/save the `actions/cache` JSON; TTL skip (~21d); cache-miss = check-all; only 2xx writes; 4xx never cached OK; records `last_status` for "previously healthy" context.
   - `render_issue_body()` — group rot by host; per URL: URL, final status, framework source, citing record-id/edge-endpoints; delimited machine block `<!--linkrot:start--> … <!--linkrot:end-->`.
   - `manage_tracking_issue()` — `gh issue list/create/edit/comment/close` keyed by stable title sentinel; the 3-state lifecycle.
   - **Sentinel injection** (TL-2) — when `--inject-sentinel-rot` is passed, append a *pre-classified* synthetic rot finding (no fetch) so the issue lifecycle is validated deterministically.
2. **`.github/workflows/tachi-citation-linkrot.yml`** (new) — `schedule` (`17 9 * * 1`) + `workflow_dispatch` (with `inject_sentinel_rot` boolean input wiring to the CLI flag); `permissions: contents: read, issues: write`; checkout → setup-python 3.11 → restore cache → run checker → save cache. **No `on: pull_request`/`push`.**
3. **`tests/schemas/test_citation_linkrot_parity.py`** (new) — the FR-008 offline parity guard **plus** classifier unit tests driven by mocked/stubbed responses (no socket). Importing this module pulls **no** outbound-HTTP code (NFR-001).
   - **Parity must cover BOTH extraction surfaces** (architect CONCERN-1): the extractor monitors crosswalk `citation:` **and** every catalog's `url:` (each `^https?://`-filtered). `test_citation_shape()` validates only the **crosswalk `citation`** slice (~556 URLs); the catalog `url:` slice (~the bulk — `mitre-attack.yaml` alone ≈700) is validated by the *separate* `test_framework_yamls_load()` (`record["url"]` via `_is_url_or_existing_file`). The guard MUST assert set-parity (both directions) against the **union** of both surfaces — equivalently, re-derive the extractor's per-file field rule independently and assert set-equality both ways — so a catalog `url:`→`link:` rename can't silently drop ~700 URLs while the guard still passes.
   - **Field rule encoded**: crosswalk → `citation`; all other `schemas/taxonomy/*.yaml` → `url`. Apply the `^https?://` filter **uniformly** across both surfaces (architect CONCERN-2) so the pseudo-taxonomy file-path `url:` values in `tachi-control-category.yaml` (8) and `tachi-stride-ai-category.yaml` (11) are dropped identically by extractor and guard (baseline §0 shows both at 0 in-scope URLs — confirm parity doesn't regress on them).
4. **`schemas/taxonomy/README.md`** (edit, ~line 224) — deferral note → live-monitor reference (FR-009).
5. *(No change to)* `tests/schemas/test_taxonomy_integrity.py` — the existing `test_citation_shape()` stays regex-only; the parity guard reads alongside it without modifying it.

## Data Flow

```
weekly cron (17 9 * * 1)  ──┐
workflow_dispatch ──────────┴─► tachi-citation-linkrot.yml
   │
   ├─ actions/checkout@v4 ─► repo tree (schemas/taxonomy/*.yaml)
   ├─ actions/setup-python@v5 (3.11)
   ├─ actions/cache@v4 (restore) ─► ledger.json {url:{last_ok,last_status}}
   │
   └─ python scripts/check-citation-urls.py
        1. discover_urls()  ── glob+safe_load+filter+dedup ─► {url → [sources]}
        2. ledger TTL skip (last_ok < 21d ⇒ skip; miss ⇒ check)
        3. classify_url() per URL  ── HostThrottler (per-host sem) ─► external hosts
              HEAD → (405/403/501) → ranged GET ; ≤5 redirects ; retry transient
        4. partition → {link-rot | needs-review | transient | healthy}
           (+ injected sentinel rot, if --inject-sentinel-rot, bypasses fetch)
        5. ledger update (2xx ⇒ write last_ok; 4xx ⇒ never cache OK)
        6. manage_tracking_issue() via gh:
              rot>0 & no issue   ─► gh issue create  (sentinel title + follow-on-180)
              rot>0 & issue open ─► gh issue edit (machine block) + dated delta comment
              rot==0 & issue open─► gh issue comment "healthy" + gh issue close
   │
   └─ actions/cache@v4 (save) ─► updated ledger.json
```

**Determinism boundary**: the only network egress is inside `classify_url()` / `HostThrottler`, reachable **only** from the script invoked by the scheduled workflow. The pytest collection path never imports it; the parity guard + classifier tests use stubs (NFR-001).

## Project Structure

### Documentation (this feature)

```
specs/183-citation-url-link-rot-monitoring/
├── plan.md              # This file
├── spec.md              # PM-APPROVED
├── research.md          # Phase 0 (complete — all decisions resolved)
├── data-model.md        # Phase 1 — data structures (URL record, classification, ledger, issue body)
├── quickstart.md        # Phase 1 — run/validate locally + via dispatch
├── contracts/           # Phase 1 — CLI, workflow, tracking-issue, cache-ledger contracts
│   ├── checker-cli.md
│   ├── workflow.md
│   ├── tracking-issue.md
│   └── cache-ledger.schema.json
├── checklists/requirements.md
└── tasks.md             # /aod.tasks output (next)
```

### Source Code (repository root)

```
.github/workflows/
└── tachi-citation-linkrot.yml      # NEW — scheduled + dispatch, least-privilege

scripts/
└── check-citation-urls.py          # NEW — zero-dep checker (~150–250 LOC)

tests/schemas/
├── test_taxonomy_integrity.py      # UNCHANGED — test_citation_shape() stays regex-only
└── test_citation_linkrot_parity.py # NEW — offline parity guard + classifier unit tests

schemas/taxonomy/
└── README.md                       # EDIT line ~224 — deferral note → live monitor
```

**Structure Decision**: Single-project CI tooling. New files live beside their established peers — workflow in `.github/workflows/`, script in `scripts/`, tests in `tests/schemas/`. Write-set is **disjoint** from any in-flight branch (Team-Lead-verified). No existing parser is reused (`tachi_parsers._load_catalog_ids()` discards `url:`/`citation:`) — a standalone script is the lowest-coupling call and keeps the network surface isolated from the test path.

## Phase 0: Outline & Research

**Status: COMPLETE** — see [research.md](./research.md). The architect technical baseline resolved every open decision; there are **no `NEEDS CLARIFICATION` markers**. Key decisions consolidated:

- **Decision**: stdlib `urllib` + `concurrent.futures` (not `requests`). **Rationale**: zero new dependency in a security-posture repo; F-250 lock-step avoided. **Alternatives**: `requests`/`httpx` (rejected — adds runtime dep for marginal ergonomics).
- **Decision**: dedicated scheduled workflow modeled on `tachi-maestro-coverage.yml`, cron `17 9 * * 1` + dispatch, never `on: pull_request`. **Rationale**: monitoring is async/eventually-consistent and must never gate a merge (NFR-001). **Alternatives**: PR-triggered check (rejected — re-introduces non-determinism), reusing an existing workflow (rejected — single-concern precedent).
- **Decision**: HEAD→ranged-GET fallback; 404/410/hard-4xx = rot, 403/401/429 = needs-review, 5xx/timeout = transient. **Rationale**: 93% MITRE means bot-blocking is the dominant false-positive risk. **Alternatives**: GET-only (rejected — wasteful), treat-all-4xx-as-rot (rejected — false positives).
- **Decision**: per-host Semaphore (2–3) under global 10 + politeness delay + descriptive UA + `Retry-After`. **Rationale**: single-origin concentration would otherwise trigger a WAF ban.
- **Decision**: `actions/cache` last-success ledger, ~21d TTL, cache-miss = check-all, 4xx never cached OK; **persist `last_status` too** (resolves the deferred "previously-healthy context" question — adopted, low-cost). **Rationale**: cuts MITRE egress ~⅔ while keeping correctness independent of the evictable cache.
- **Decision**: single sentinel-titled tracking issue via `gh`; create/update-in-place/self-close; reuse `follow-on-180` label + best-effort `link-rot` label. **Rationale**: title-sentinel dedup is load-bearing; no issue spam (NFR-006).
- **Decision (TL-2)**: validate the lifecycle with a `workflow_dispatch` boolean input `inject_sentinel_rot` that appends a **pre-classified** synthetic rot finding (no fetch). **Rationale**: makes "exactly one issue → self-close" reproducible and offline-of-the-real-internet; a live external 404 would self-flake. **Alternatives**: injected sentinel YAML record (rejected — would still be fetched / mutates a tracked file), live always-404 service (rejected — network-dependent, flaky).

## Phase 1: Design & Contracts

**Prerequisites**: research.md complete ✅. Artifacts generated alongside this plan:

- **[data-model.md](./data-model.md)** — `UrlCitation`, `SourceLocation`, `Classification` (enum + final status), `LedgerEntry`, `TrackingIssueBody` structures, validation rules, and state transitions for the issue lifecycle.
- **[contracts/checker-cli.md](./contracts/checker-cli.md)** — `check-citation-urls.py` CLI: flags (`--dry-run`, `--inject-sentinel-rot`, `--no-cache`, `--max-host-concurrency`, `--global-concurrency`), exit codes (0 ok / non-zero = infra error, **never** non-zero for "rot found" so the job stays a monitor), stdout JSON summary shape.
- **[contracts/workflow.md](./contracts/workflow.md)** — triggers, `inputs.inject_sentinel_rot`, permissions, step sequence, cache keys.
- **[contracts/tracking-issue.md](./contracts/tracking-issue.md)** — sentinel title, machine-block delimiters, per-URL body schema, delta-comment format, the 3 lifecycle transitions.
- **[contracts/cache-ledger.schema.json](./contracts/cache-ledger.schema.json)** — JSON Schema for the ledger.
- **[quickstart.md](./quickstart.md)** — run the parity guard + classifier tests offline; dry-run the checker locally (no issue I/O); dispatch the workflow with/without the sentinel to validate the two-run lifecycle.

**Agent context update**: `.aod/scripts/bash/update-agent-context.sh` is **absent** in this repo (known) — skipped gracefully; CLAUDE.md already carries the needed context.

**Post-design Constitution re-check**: still ✅ — no new violations introduced by the design; network surface remains isolated to the scheduled-only script.

## Implementation Phases (build sequencing — for /aod.tasks)

Per the Team-Lead build-wave plan:

- **W1-a** `senior-backend-engineer` — `scripts/check-citation-urls.py` (discover/classify/throttle/ledger/render; sentinel injection; type hints; exit-code discipline). ∥
- **W1-b** `devops` — `tachi-citation-linkrot.yml` (triggers, dispatch input, permissions, cache wiring, gh invocation).
- **W2** `tester` — `test_citation_linkrot_parity.py`: offline set-parity guard covering **both** extraction surfaces (crosswalk `citation` vs `test_citation_shape()` **and** catalog `url` vs `test_framework_yamls_load()`), both directions + field-rule encoding + uniform `^https?://` filter (CONCERN-1/CONCERN-2) + classifier unit tests (mocked HEAD-405→GET-200, 404, 410, 403, 429, 5xx, redirect-chain, loop). Deterministic, PR-gate-eligible.
- **W3** `code-reviewer` ∥ `security-analyst` — review zero-dep/least-privilege/no-network-in-tests; confirm NFR-001 by inspecting the pytest import graph; verify supply-chain minimalism.
- **Validation** (deliver-adjacent) — 2 sequential `workflow_dispatch` runs: (1) `inject_sentinel_rot=true` → exactly one tracking issue; (2) `inject_sentinel_rot=false` → issue self-closes.

## Testing Strategy

- **Offline parity guard (FR-008, PR-gate-eligible)**: assert the extractor's glob+filter URL set == the **union of both integrity surfaces** — crosswalk `citation` (`test_citation_shape()`) **and** catalog `url` (`test_framework_yamls_load()`) — both directions; assert the field rule (crosswalk→`citation`, catalogs→`url`) with a uniform `^https?://` filter. No network. (Parity against `test_citation_shape()` alone would leave the ~700-URL catalog `url:` slice unguarded — architect CONCERN-1.)
- **Classifier unit tests (offline)**: feed stubbed responses — 200, 301→200, 404, 410, 403, 429, 500, timeout, HEAD-405-then-GET-200, redirect-loop, >5-hops — assert the correct `Classification`. Stub at the `urllib`/transport boundary so no socket opens; module import pulls no outbound HTTP into collection (NFR-001 self-check).
- **Lifecycle validation (live dispatch, not unit)**: the `inject_sentinel_rot` two-run sequence (SC-002 → SC-003). `[MANUAL-ONLY]` — requires a real Actions run.
- **NFR-001 structural assertion**: a test that statically confirms the checker module is not reachable from the pytest collection import graph (or that importing the test module performs no DNS/socket).

## Risks & Mitigations

Carried from spec/PRD (R1–R8). Plan-level emphasis:
- **R1 bot-block false positives (HIGH)** → descriptive UA + Accept + HEAD→GET + 403/401/429=needs-review.
- **R8 determinism contamination (HIGH if it occurs)** → hard separation: script never imported by `tests/`; parity guard + classifier tests are stub-only; an explicit NFR-001 structural test guards the boundary.
- **R3 rate-limit ban (MED)** → per-host Semaphore + politeness delay + `Retry-After` + cache TTL.
- **R5 hardcoded-list drift (MED)** → glob discovery + parity guard fails if a file/field silently drops URLs.

## Complexity Tracking

*No constitution violations — table intentionally empty.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
