---
prd:
  number: "183"
  topic: citation-url-link-rot-monitoring
  created: 2026-06-14
  status: Approved
  type: infrastructure
triad:
  pm_signoff: { agent: product-manager, date: 2026-06-14, status: APPROVED, notes: "Author sign-off. Scope = BLP-05 Wave 3 LAST open item (#183) + Feature-180 T034 follow-on: a weekly scheduled CI job that fetches taxonomy citation URLs and files ONE self-closing tracking issue on link-rot, closing the gap F-180 left by design (test_citation_shape() validates URL syntax, never reachability, per ADR-021 determinism). Monitoring-only, never a merge gate. v1.1 folds in all Triad corrections (Architect APPROVED + Team-Lead APPROVED_WITH_CONCERNS, zero blockers): NFR-1 scoped to 'no outbound/external fetch' (Architect INFO-1, avoids colliding with the legit hermetic loopback fixture tests/scripts/conftest.py:123); URL count softened to ~900 (≈893–902 by dedup pass; ≈93% MITRE either way — Architect INFO-2/3); effort 1.5–2.5 → 2.0–3.0d (Team-Lead TL-1); validation fixture pinned to a deterministic sentinel/dispatch-input not a live external 404 (TL-2); FR-8 parity guard sharpened to assert set-parity + the crosswalk-citation/catalog-url field rule (TL-3). Honors F-180 determinism discipline + source-of-truth positioning." }
  architect_signoff: { agent: architect, date: 2026-06-14, status: APPROVED, notes: "APPROVED — re-review NOT needed before /aod.plan. All 5 baseline concerns verified PASS against the draft: CONCERN-A (determinism invariant) hard-encoded in NFR-1, reinforced 6 places, offline guard verified network-free in codebase; CONCERN-B 403/401/429=needs-review (FR-4); CONCERN-C per-host 2–3 (FR-5), 93% MITRE re-verified at HEAD (830/893); CONCERN-D single sentinel-deduped self-closing issue (FR-7); CONCERN-E cache-miss=check-all + 4xx-never-cached (FR-6). Technical correctness PASS: glob discovery, HEAD→GET fallback, stdlib zero-dep (verified requirements-dev.txt), least-privilege perms, fetch-free parity guard, precedent + no-parser-reuse confirmed against live repo. 3 LOW/INFO notes (all folded into v1.1): INFO-1 NFR-1 wording vs loopback fixture; INFO-2/3 count rounding + catalog-count reconciliation (non-load-bearing — FR-3 globs at runtime). No technical blocker. Details: .aod/results/architect-183.md (baseline: .aod/results/architect-baseline-183.md)." }
  techlead_signoff: { agent: team-lead, date: 2026-06-14, status: APPROVED_WITH_CONCERNS, notes: "Feasible; zero CRITICAL/HIGH, zero blockers. Greenfield, exact CI precedent (tachi-maestro-coverage.yml verified), genuinely zero-new-dep (requirements-dev.txt confirmed), clean disjoint write-set (no collision; only in-flight branch 185-document-stage, disjoint). Revised effort 2.0–3.0 eng-days (plan to 3, expect 2 — LOW nudge above PRD floor to cover the gh dedup state machine + validation fixture, both under-counted in v1.0; folded into v1.1). No spike needed — all 7 architect open-decisions resolved in PRD; residual unknowns are build-then-dispatch-tune (workflow_dispatch exists for exactly this). 3 concerns (all fix-at-plan, folded): TL-1 estimate floor (LOW); TL-2 validation fixture must be a deterministic sentinel/dispatch-input, NOT a live external 404, or it self-flakes (MED); TL-3 FR-8 parity guard must assert set-parity + encode the crosswalk-citation/catalog-url field rule (MED). Build plan: W1-a senior-backend-engineer (script) ∥ W1-b devops (workflow+gh/cache/perms) → W2 tester (parity guard + rotted-URL fixture) → W3 code-reviewer ∥ security-analyst. Testability: deterministic FR-8 guard is flake-free PR-gate-eligible; rotted-URL→1-issue→self-close is dispatch-validated (2 sequential runs), correctly never a merge gate. Details: .aod/results/team-lead-183.md" }
source:
  idea_id: 183
  story_id: null
---

# Citation-URL Link-Rot Monitoring — Scheduled CI Check (F-A1 Follow-on)

**Status**: Approved (2026-06-14 — PM author sign-off + Architect APPROVED + Team-Lead APPROVED_WITH_CONCERNS; v1.1 folds in all Triad corrections)
**Created**: 2026-06-14
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P2 (Light) — BLP-05 Wave 3 (Crosswalk Integrity & Edges), last open item
**Evidence**: Issue [#183](https://github.com/davidmatousek/tachi/issues/183) (`follow-on-180`), filed at Feature 180 T034. Source scope: F-180 PRD §Out of Scope ("Citation URL link-rot monitoring: no CI check validates URL reachability") + spec.md edge case (line 147) + `schemas/taxonomy/README.md` link-rot note (line 224). Strategic home: `_internal/strategy/BLP-05-framework-mapping-and-output-fidelity.md` §Wave 3.

---

## Executive Summary

### The One-Liner
Add a **weekly scheduled GitHub Actions job** that fetches every URL-shaped citation in the taxonomy YAMLs and files **one self-updating, self-closing tracking issue** when a link rots — closing the gap left open by design in F-180, where the deterministic integrity suite validates citation URL *syntax* but never *reachability*, all **without ever putting a network call on the PR path** (preserving the ADR-021 determinism boundary).

### Problem Statement
Feature 180 (F-A1, Taxonomy Crosswalk Collection, PR #181) shipped canonical-URL conventions per framework (`schemas/taxonomy/README.md` FR-8) that *reduce* link-rot probability but do **not enforce periodic re-validation**. The reason is deliberate: the referential-integrity suite (`tests/schemas/test_taxonomy_integrity.py:286` `test_citation_shape()`, F-180 FR-031) validates citation URLs by **regex syntax only — no HTTP fetch** — to keep the `pytest` suite deterministic and offline (ADR-021). The consequence:

> A taxonomy citation URL can return **HTTP 404 indefinitely** and every CI run stays green. Nothing in the project detects a rotted citation.

The un-monitored surface is large and growing. Measured at HEAD across `schemas/taxonomy/*.yaml`:

| Metric | Value |
|---|---|
| Distinct URL-shaped citations | **≈900** (measured 893–902 by dedup pass) |
| `crosswalk.yaml` `citation:` (URL-shaped) | ≈556 |
| `crosswalk.yaml` `citation:` (internal file-path — already covered offline) | 89 |
| Catalog `url:` fields (8 catalogs) | balance |
| Distinct hosts | **7** |
| MITRE-hosted share (`attack`/`cwe`/`atlas.mitre.org`) | **≈93%** (~830–835 of ~900) |

Exact counts drift slightly with each catalog edit and dedup pass — the extractor globs at runtime (FR-3), so no count is hardcoded; the load-bearing fact is the **≈93% MITRE concentration**, which holds across measurements and forces per-host throttling (FR-5). The catalog count grew from 7 → 8 since #183 was filed (`nist-ai-600-1.yaml` added at #184) and continues to climb (BLP-05 Wave 2). Every new catalog and crosswalk edge enlarges the rot surface. Because tachi is positioned as the **upstream machine-readable contract that downstream AI-security tools consume**, a rotted citation silently erodes the evidentiary value of every edge that cites it — the analyst clicks through to a 404 and the crosswalk's authority degrades.

### Proposed Solution
A new dedicated single-concern workflow `.github/workflows/tachi-citation-linkrot.yml` (modeled on the project's `tachi-maestro-coverage.yml` precedent) runs **weekly on a cron schedule** (plus `workflow_dispatch`), invoking a new zero-dependency script `scripts/check-citation-urls.py` that:

1. **Glob-discovers** every `schemas/taxonomy/*.yaml`, extracts URL-shaped `citation:`/`url:` values, dedups to ~900, and keeps a URL → source-location back-reference map.
2. **Fetches each URL** with polite, per-host-throttled concurrency, classifying 404/410/hard-4xx as **link-rot**, 403/401/429 as **needs-review** (not auto-filed — bot-block guard), and 5xx/timeout as **transient** (retry-with-backoff, never reported).
3. **Maintains a single deduplicated tracking issue** — created on first rot, body-updated each run, **auto-closed when rot clears**.

The job is **scheduled-only and never `on: pull_request`** — the load-bearing architectural invariant that keeps all network non-determinism out of the deterministic test suite and off the merge path.

### Success Criteria
1. The scheduled workflow runs green weekly and on manual `workflow_dispatch`.
2. A deliberately-rotted URL (validation fixture) produces **exactly one** tracking issue naming the URL, its final HTTP status, and its source location(s).
3. When the rotted URL is fixed, the tracking issue **self-closes** on the next run.
4. The `pytest` suite and every `pull_request`-triggered job remain **network-free** (no HTTP import reachable from the test collection path).
5. The check **never blocks a PR merge**.

### Timeline
**Estimated effort: 2.0–3.0 days** (1 engineer; plan to 3, expect 2 — Team-Lead-revised from the v1.0 1.5–2.5 floor to cover the `gh` dedup state machine + validation fixture, both under-counted initially). Greenfield, zero new runtime dependencies, exact CI precedent to model on. Bulk of the effort is the polite-fetch/per-host-throttle logic and the issue-dedup lifecycle, not the extraction. No spike needed — all architect open-decisions are resolved here; residual unknowns are build-then-`workflow_dispatch`-tune.

**Build wave plan** (Team-Lead, for `/aod.plan` → tasks): **W1-a** `senior-backend-engineer` (the `check-citation-urls.py` script) ∥ **W1-b** `devops` (workflow + `gh`/cache/permissions wiring) → **W2** `tester` (offline parity guard + deterministic rotted-URL fixture) → **W3** `code-reviewer` ∥ `security-analyst`.

---

## Strategic Alignment

### Product Vision Alignment
The product vision positions tachi as "a new scanning column alongside SAST, SCA, and Secrets" whose authority rests on a **machine-readable taxonomy contract** that downstream tools consume. Citation integrity is foundational to that contract: a crosswalk edge's value is its *traceable, verifiable* mapping to an authoritative source. Link-rot monitoring protects the evidentiary chain that makes the taxonomy trustworthy.

### Roadmap Fit
This is the **last open item of BLP-05 Wave 3 (Crosswalk Integrity & Edges)**. Wave 3 sibling #182 (`related`/`superseded` edges) is DELIVERED; #183 completes the integrity wave and, with it, the BLP-05 framework-mapping initiative's integrity track. It is also the closing T034 follow-on from Feature 180.

### Predecessor Relationship
Directly continues Feature 180 (F-A1). F-180 established the canonical-URL conventions (FR-8) and the *synchronous, offline* citation-shape guard (FR-031); #183 adds the *asynchronous, networked* reachability guard that F-180 explicitly deferred as a follow-on Issue. The two are complementary and **must remain physically separate** (see NFR-1): F-180's guard stays in `pytest` (deterministic, offline); #183's guard lives only in the scheduled workflow.

---

## Target Users & Personas

### Primary Persona: Tachi Taxonomy Steward / Maintainer
Owns `schemas/taxonomy/`. Today has **no signal** when an external authority (MITRE, NIST, OWASP) reorganizes a URL and breaks a citation. Needs a low-noise, trustworthy weekly digest of *confirmed* rot — not a wall of bot-blocked false positives — so triage effort goes to real breakage (replace the URL, or mark the edge `confidence: low` + TODO).

### Secondary Persona: Downstream AI-Security Tool / Analyst Traversing the Crosswalk
Consumes the taxonomy as evidence. When they click a citation to verify a mapping, a 404 undermines trust in the entire crosswalk. Benefits indirectly: rot gets caught and fixed before it reaches them.

### Tertiary Persona: Contributor Opening a PR
Must **never** have their merge blocked by a transient network failure on an unrelated citation URL. Benefits from the strict scheduled-only / never-on-PR design.

---

## User Stories

### US-1: Weekly Confirmed-Rot Signal
**As a** taxonomy steward, **I want** a weekly automated check that fetches every taxonomy citation URL and reports the ones that return a permanent failure (404/410), **so that** I can replace a rotted citation before it erodes crosswalk trust — without manually clicking 900 links.

**Acceptance**: A scheduled run fetches all in-scope URLs and, for each confirmed-rot URL, records the final HTTP status and every source location (`<file>: <record-id>` or `crosswalk edge <src> → <dst>`) that cites it.

### US-2: Trustworthy Signal (No False Positives)
**As a** maintainer, **I want** transient failures (5xx, timeouts) and bot-blocks (403/401/429) excluded from the confirmed-rot report, **so that** the tracking issue stays high-signal and I don't waste triage time on live-but-blocked MITRE URLs.

**Acceptance**: 5xx/timeout are retried-with-backoff and never reported on residual failure; 403/401/429 are surfaced only under a clearly-labeled "needs manual verification" section, never as confirmed rot.

### US-3: Never Blocks a Merge
**As a** contributor, **I want** the link-rot check to run on a schedule and never on my PR, **so that** a network blip on an unrelated citation can never block my merge — and the deterministic test suite stays offline.

**Acceptance**: The workflow declares `schedule` + `workflow_dispatch` only (no `pull_request`/`push` trigger); no HTTP-making code is importable from the `pytest` collection path.

### US-4: One Self-Healing Tracking Issue
**As a** maintainer, **I want** all link-rot findings consolidated into a single tracking issue that updates in place and auto-closes when rot clears, **so that** I'm not buried under a new duplicate issue every week.

**Acceptance**: Across consecutive rot-positive runs exactly one open tracking issue exists (body reflects current state); when a run finds zero rot, an existing tracking issue is auto-closed with a recovery comment.

---

## Functional Requirements

### FR-1: Dedicated Scheduled Workflow
Add `.github/workflows/tachi-citation-linkrot.yml`, a single-concern job modeled on `tachi-maestro-coverage.yml` (single OS, single runner, `actions/checkout@v4` + `actions/setup-python@v5`, Python 3.11). Triggers: `schedule` (weekly cron, off-peak off-`:00` slot, e.g. `17 9 * * 1`) **and** `workflow_dispatch`. **MUST NOT** declare `on: pull_request` or `on: push`. `permissions:` MUST be least-privilege: `contents: read` + `issues: write`.

### FR-2: Zero-Dependency Checker Script
Add `scripts/check-citation-urls.py`, invoked directly by the workflow. Uses **stdlib `urllib.request` + `concurrent.futures`** and the already-pinned `pyyaml`. **No new runtime dependency.** (If ergonomic retry justifies `requests`, it MUST be added to `requirements-dev.txt` and the workflow `pip install` in the same commit per the F-250 lock-step rule — but stdlib is the chosen path.)

### FR-3: Glob-Based URL Extraction with Back-Reference Map
The script MUST **glob `schemas/taxonomy/*.yaml`** (never a hardcoded file list). For `crosswalk.yaml` it extracts each edge's `citation`; for every other (catalog) file it extracts each record's `url`. It filters to URL-shaped values (`^https?://`, reusing the integrity test's regex semantics for parity), **drops internal file-path citations** (already covered offline by `test_citation_shape()`), dedups to the distinct set, and retains a **URL → [(file, record-id / edge-endpoints)] back-reference map** so a rotted URL is reported with its source location(s) — a single shared URL maps to many records; report all.

### FR-4: HTTP Classification Semantics
For each in-scope URL:

| Response | Classification | Action |
|---|---|---|
| 2xx | healthy | pass |
| 3xx | redirect | follow (≤5 hops); classify on **final** status; loop/>5 hops = report |
| 404 / 410 / post-retry hard 4xx (400/451) | **link-rot** | REPORT as confirmed |
| 401 / 403 / 429 | **needs-review** | surface separately ("verify manually"); NOT confirmed rot |
| 5xx / timeout / DNS / conn-reset | transient | retry-with-backoff; if still failing, do NOT report |

Method: **HEAD-then-ranged-GET fallback** (`Range: bytes=0-0`) — many CDNs 405 on HEAD but 200 on GET; treating HEAD-405 as rot is the top false-positive source. Tuning (NFR-bound): 10 s connect / 15 s read timeout; 2 retries (3 attempts total) on transient only, exponential backoff (1→2→4 s) + jitter; **never retry a 4xx**.

### FR-5: Per-Host Rate Limiting & Politeness
Because 93% of URLs are MITRE-hosted, the script MUST throttle **per host** (≈2–3 concurrent connections per host) under a global cap (≈10 threads), with a small inter-request politeness delay (100–250 ms) within a host bucket. It MUST send a descriptive `User-Agent` (e.g. `tachi-linkrot-monitor/1.0 (+https://github.com/davidmatousek/tachi; citation integrity check)`) and an `Accept: text/html,*/*` header, and **honor `Retry-After`** on 429/503.

### FR-6: Last-Successful-Check Caching
Use `actions/cache@v4` to persist a per-URL last-2xx timestamp ledger (`{url: iso8601}`) in the cache (NOT committed to the repo). Skip re-fetching any URL whose last success was within the TTL (≈21 days / 3 weekly cycles). A **cache miss MUST mean "check everything," never "assume healthy."** Only a 2xx-final outcome writes a fresh timestamp; a 4xx URL is never cached as OK and is re-checked every run until fixed.

### FR-7: Single Deduplicated Tracking Issue (Auto-File / Auto-Close)
Use the native **`gh` CLI** (no marketplace action). Dedup via a **stable title sentinel** (e.g. `[link-rot] Taxonomy citation link-rot — open findings`):
- Confirmed rot found, no open tracking issue → `gh issue create` (sentinel title; reuse `follow-on-180` lineage label, optionally mint a `link-rot` label).
- Confirmed rot found, tracking issue already open → update it in place (rewrite a delimited machine block `<!--linkrot:start-->…<!--linkrot:end-->`) + post a short dated delta comment (newly-rotted / newly-recovered).
- Zero confirmed rot, tracking issue open → post a "all citations healthy as of `<date>`" comment and **`gh issue close`** it.

Issue body per rotted URL: the URL, final HTTP status, framework source (catalog name or `crosswalk`), and citing record-id / edge-endpoints — grouped by host. The job MUST NOT create per-run or per-URL issues.

### FR-8: Offline Structural-Parity Guard
Add a tiny **offline** assertion to the deterministic suite that the extractor's glob+filter recovers the **same** URL set the `test_citation_shape()` regex test sees — so a future catalog rename can't silently drop a file from monitoring. The guard MUST assert **set-parity** (same distinct URL set, both directions) **and** encode the field rule it relies on — `crosswalk.yaml` → `citation` field, all other `schemas/taxonomy/*.yaml` catalogs → `url` field — so a schema/field drift that moves URLs is caught, not silently mis-extracted. This guard performs **no network fetch** (preserves NFR-1); it validates set-parity only and is PR-gate-eligible (flake-free).

---

## Non-Functional Requirements

### NFR-1: Determinism Boundary (load-bearing)
**No outbound/external network call may ever be introduced into `tests/` or any `pull_request`/`push`-triggered job.** Link-rot validation — which fetches real external citation URLs — is **scheduled-only**. The checker script MUST NOT be importable from the `pytest` collection path (separate script, separate workflow, no shared import that pulls external HTTP into test collection). This preserves the ADR-021 determinism boundary that `test_citation_shape()` exists to protect. (Scoped precisely to *outbound/external* fetch: the existing hermetic loopback fixture at `tests/scripts/conftest.py:123` is a legitimate offline test construct and is explicitly **not** in conflict with this NFR — the constraint targets reaching the public internet, not in-process/loopback test scaffolding.) **This is the single hardest constraint in this PRD.**

### NFR-2: Zero New Runtime Dependency
stdlib `urllib` + already-pinned `pyyaml` only. Any new dependency requires the F-250 lock-step update (manifest + workflow in one commit) and is explicitly dispreferred.

### NFR-3: Politeness / No Throttle-Ban
Per-host concurrency cap (not just a global pool); a full uncached sweep completes within a minute-scale budget well inside a weekly job's time. Must not trigger a WAF ban from MITRE/NIST/OWASP.

### NFR-4: Signal Quality (Low False-Positive)
Only 404/410/post-retry-hard-4xx auto-file as confirmed rot. 403/401/429 are "needs-review." Transient failures never file. The maintainer must be able to trust that a "confirmed rot" entry is real.

### NFR-5: Least Privilege
Workflow token scope limited to `contents: read` + `issues: write`. No `pull-requests`, no `contents: write`.

### NFR-6: Idempotent Issue Lifecycle
Exactly one tracking issue across runs; self-updating body; self-closing on recovery. No issue spam.

### NFR-7: Supply-Chain Minimalism
Auto-issue via native `gh` (pre-installed on runners, ambient `GITHUB_TOKEN`), no third-party marketplace action — appropriate for a security-posture repo.

---

## Success Metrics

| Metric | Target |
|---|---|
| Scheduled workflow green-run rate | Runs weekly without infrastructure error |
| Manual `workflow_dispatch` | Works on demand |
| Confirmed-rot detection (validation fixture) | A **deterministic sentinel** rot fixture (not a live external 404) → exactly 1 tracking issue naming URL + status + source location |
| Self-close on recovery | Fixed URL → tracking issue auto-closed next run |
| Determinism preserved | `pytest` + all PR-triggered jobs remain network-free (verifiable: no HTTP import reachable from test collection) |
| PR-blocking incidents | **0** |
| False-positive rate | 403/401/429 never appear as confirmed rot |
| New runtime dependencies added | **0** |

---

## Scope & Boundaries

### In Scope (P0)
- New scheduled workflow `tachi-citation-linkrot.yml` (FR-1).
- New zero-dependency checker `scripts/check-citation-urls.py` (FR-2–FR-6).
- Single deduplicated auto-file/auto-close tracking issue via `gh` (FR-7).
- Offline structural-parity guard in the deterministic suite (FR-8).
- README note (`schemas/taxonomy/README.md`) updating the line-224 link-rot deferral to "now monitored by the scheduled job."

### Out of Scope
- ❌ **Internal file-path citation validation** — already covered synchronously/offline by `test_citation_shape()` (89 file-path citations).
- ❌ **On-PR / real-time URL validation** — would re-introduce network non-determinism on the merge path (violates NFR-1). Scheduled-only by design.
- ❌ **Auto-replacement of rotted URLs** — the job *reports*; a maintainer *triages* (replace URL, preferred; or `confidence: low` + TODO). No automated content mutation of taxonomy files.
- ❌ **General docs/markdown external-link checking** — scope is `schemas/taxonomy/*.yaml` citations only.
- ❌ **Wayback/archival snapshotting** of citations — possible future enhancement, not this Issue.
- ❌ **Blocking/gating CI behavior** — link-rot is a monitoring signal, never a merge gate.

### Assumptions
- `gh` CLI is available on GitHub-hosted runners with `GITHUB_TOKEN` (confirmed).
- External authorities (MITRE/NIST/OWASP) tolerate a polite, throttled weekly sweep with a descriptive UA.
- `pyyaml` remains pinned in `requirements-dev.txt`.

### Constraints
- Follow-on Issue; does NOT and never did block F-A1 (#181) merge.
- Link-rot monitoring is orthogonal to referential integrity — the synchronous `test_citation_shape()` already guards internal file paths; this adds asynchronous URL validation only.
- Must respect the architect baseline decisions (cron slot, stdlib lib, ~21d TTL, 403=needs-review, per-host cap 2–3, global cap 10).

---

## Risks & Dependencies

### Technical Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | **Bot-block false positives** — MITRE/Cloudflare returns 403/429 to non-browser UAs on live pages (835 MITRE URLs = dominant risk). | HIGH | Descriptive UA + `Accept` header (FR-5); HEAD→GET fallback (FR-4); **403/401/429 = needs-review, not auto-rot** (NFR-4). |
| R2 | **Transient flakiness** masquerading as rot (DNS, conn-reset, one-off 5xx). | MED | Retry-with-backoff (FR-4); 5xx/timeout never reported; scheduled-only → self-corrects next cycle. |
| R3 | **Rate-limit ban** from burst against single-origin MITRE. | MED | Per-host cap 2–3 + politeness delay + `Retry-After` honor + caching TTL cuts volume ~⅔ (FR-5/FR-6). |
| R4 | **HEAD-unsupported endpoints** (405/501 on HEAD). | MED | HEAD→ranged-GET fallback before classifying (FR-4). |
| R5 | **Hardcoded-file-list drift** — a new catalog silently escapes monitoring. | MED | Glob discovery (FR-3) + offline structural-parity guard (FR-8). |
| R6 | **Issue spam / token scope creep.** | LOW | Least-privilege `issues: write` (NFR-5); single deduped self-closing issue (FR-7). |
| R7 | **DOI redirect chains** (`doi.org` → publisher). | LOW | Follow ≤5 hops, classify on final status (FR-4); only 4 doi.org URLs. |
| R8 | **Determinism contamination** — a network call leaks into `pytest`/PR path. | HIGH (if it occurs) | Hard separation (NFR-1): script never imported by `tests/`; structural-parity guard is fetch-free. |

### Dependencies
- **Feature 180 (F-A1, DELIVERED)** — provides `crosswalk.yaml`, the catalog YAMLs, the canonical-URL conventions (FR-8), and `test_citation_shape()` (the offline guard this complements).
- **The 9 taxonomy YAMLs** under `schemas/taxonomy/` (glob-discovered; surface grows with BLP-05 Wave 2 catalogs — #184/#185 already merged).
- **GitHub Actions runtime** — `gh` CLI, `GITHUB_TOKEN`, `actions/cache@v4`, `actions/setup-python@v5`.
- No dependency on BLP-05 Wave 2 PRDs completing — extraction is glob-based and tolerates the evolving catalog set.

---

## Definition of Done

- [ ] `tachi-citation-linkrot.yml` added: `schedule` + `workflow_dispatch` only, least-privilege permissions, green on `workflow_dispatch`.
- [ ] `scripts/check-citation-urls.py` added: glob extraction, back-reference map, HTTP classification (FR-4), per-host throttling (FR-5), caching (FR-6) — stdlib only.
- [ ] Single deduplicated tracking issue lifecycle implemented and validated (create / update-in-place / self-close) via `gh` (FR-7).
- [ ] Offline structural-parity guard added to the deterministic suite (FR-8); `pytest` remains network-free.
- [ ] Validation: a deliberately-rotted URL fixture produces exactly one correct tracking issue; fixing it self-closes the issue.
- [ ] `schemas/taxonomy/README.md` line-224 deferral note updated to reference the live monitor.
- [ ] No new runtime dependency introduced (or, if `requests`, F-250 lock-step applied).
- [ ] Triad sign-off recorded; CHANGELOG / closure docs updated at deliver.

## Open Questions

### Resolved at Definition (architect baseline recommendations adopted)
- **Cron slot** → `17 9 * * 1` (Mon 09:17 UTC; off-peak, off-`:00` to dodge GitHub cron throttling).
- **HTTP library** → stdlib `urllib` (zero new dependency).
- **Cache TTL** → ~21 days (3 weekly cycles).
- **403/401/429 disposition** → needs-review, NOT confirmed rot.
- **Per-host concurrency** → 2–3 per host; **global cap** → ~10.
- **Label** → reuse `follow-on-180` + title-sentinel dedup (title sentinel is the load-bearing dedup; a dedicated `link-rot` label is optional convenience).

### Constraint Tightened at Definition (Team-Lead TL-2)
- The "confirmed-rot → exactly one issue → self-close" success criterion (Success Metrics) MUST be validated with a **deterministic sentinel** — a controlled injected fixture or `workflow_dispatch` input — **NOT a live external 404 URL**, which would self-flake on the network. The validation harness controls the rot signal so the assertion is reproducible. (Exact mechanism — injected sentinel record vs. dispatch input — is a plan-stage detail; determinism is the requirement.)

### Deferred to Plan
- Whether to additionally persist last-known-status (enables "previously healthy on `<date>`" context in the issue) — optional, lower priority.

---

## References

### Product Documentation
- `docs/product/01_Product_Vision/product-vision.md` — vision (taxonomy contract authority).
- `_internal/strategy/BLP-05-framework-mapping-and-output-fidelity.md` §Wave 3 — strategic home.

### Related PRDs / Features
- `docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md` — predecessor (F-A1); §Out of Scope defers link-rot monitoring; FR-8 canonical-URL conventions; FR-031 `test_citation_shape()`.
- `docs/product/02_PRD/182-crosswalk-related-superseded-edges-2026-06-07.md` — Wave 3 sibling (DELIVERED).

### Technical Documentation
- `schemas/taxonomy/README.md:224` — link-rot deferral note (to be updated).
- `tests/schemas/test_taxonomy_integrity.py:286` — `test_citation_shape()` (the offline guard).
- `.github/workflows/tachi-maestro-coverage.yml` — single-concern CI precedent to model on.
- `.aod/results/architect-baseline-183.md` — full architect technical baseline.

---

## Approval & Sign-Off

| Role | Agent | Status | Date |
|---|---|---|---|
| PM | product-manager | APPROVED (author) | 2026-06-14 |
| Architect | architect | APPROVED | 2026-06-14 |
| Team-Lead | team-lead | APPROVED_WITH_CONCERNS | 2026-06-14 |

---

## Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| v1.0 | 2026-06-14 | product-manager | Initial draft grounded in architect technical baseline (`.aod/results/architect-baseline-183.md`). Infrastructure workflow: architect baseline → PM draft → Team-Lead + Architect final reviews. |
| v1.1 | 2026-06-14 | product-manager | Folds in all Triad corrections (Architect APPROVED + Team-Lead APPROVED_WITH_CONCERNS, zero blockers): NFR-1 scoped to "no outbound/external fetch" + loopback-fixture carve-out (Architect INFO-1); URL count softened to ≈900 / ≈93% MITRE with runtime-glob note (Architect INFO-2/3); effort 1.5–2.5 → 2.0–3.0d + build wave plan (Team-Lead TL-1); validation fixture pinned to a deterministic sentinel, not a live external 404 (TL-2); FR-8 parity guard sharpened to set-parity + field rule (TL-3). Status → Approved. |
