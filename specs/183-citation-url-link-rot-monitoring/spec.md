---
prd_reference: docs/product/02_PRD/183-citation-url-link-rot-monitoring-2026-06-14.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-14
    status: APPROVED
    notes: "Faithful translation of v1.1 PRD — 4/4 user stories, 8/8 PRD FRs (+FR-009 README note correctly promoted from latent PRD DoD/scope, not creep), 7/7 NFRs traced 1:1. Both load-bearing Team-Lead concerns preserved: TL-2 (validation via deterministic sentinel, not live external 404 — SC-002/Edge Case/US-1 test) and TL-3 (FR-008 parity guard asserts set-parity both directions + encodes field rule crosswalk→citation/catalogs→url). No scope creep or loss; 6 exclusions mirror PRD. SCs measurable + technology-agnostic (infra-feature structural-fact exception applies). Load-bearing codebase claims independently verified at HEAD. 2 informational concerns (FR-009 promotion, US-2↔US-3 renumbering with traceability annotations) — no action needed. Details: .aod/results/product-manager-183.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Citation-URL Link-Rot Monitoring — Scheduled CI Check

**Feature Branch**: `183-citation-url-link-rot-monitoring`
**Created**: 2026-06-14
**Status**: Draft
**Input**: PRD #183 — "Add a weekly scheduled GitHub Actions job that fetches every URL-shaped citation in the taxonomy YAMLs and files one self-updating, self-closing tracking issue when a link rots — closing the reachability gap F-180 left by design, without ever putting a network call on the PR path."

## User Scenarios & Testing *(mandatory)*

This feature gives the taxonomy steward a trustworthy weekly signal of *confirmed* citation link-rot, delivered as a single self-healing tracking issue, while guaranteeing the deterministic test suite and PR merge path stay network-free. User stories are numbered for this spec; the PRD-story mapping is noted for traceability.

### User Story 1 - Weekly Confirmed-Rot Signal (Priority: P1)

*(PRD US-1)* As a taxonomy steward, I want a weekly automated check that fetches every taxonomy citation URL and reports the ones that return a permanent failure (404/410), so that I can replace a rotted citation before it erodes crosswalk trust — without manually clicking ~900 links.

**Why this priority**: This is the core capability and the MVP. Without automated detection of confirmed rot, the feature delivers nothing. Every other story refines or constrains this one.

**Independent Test**: Trigger the scheduled workflow via manual dispatch against a controlled set containing one deterministically-rotted citation; verify the run completes and the rotted URL is identified with its final HTTP status and every source location that cites it.

**Acceptance Scenarios**:

1. **Given** the taxonomy YAMLs contain in-scope citation URLs, **When** a scheduled run executes, **Then** every in-scope URL-shaped citation is fetched and evaluated for reachability.
2. **Given** a URL returns a confirmed-rot status (404/410/post-retry hard-4xx), **When** the run completes, **Then** that URL is reported with its final HTTP status and every source location (`<file>: <record-id>` or `crosswalk edge <src> → <dst>`) that cites it.
3. **Given** a single URL is cited by multiple records, **When** it is reported, **Then** all citing source locations are listed, not just the first.

---

### User Story 2 - Never Blocks a Merge & Determinism Preserved (Priority: P1)

*(PRD US-3)* As a contributor, I want the link-rot check to run on a schedule and never on my PR, so that a network blip on an unrelated citation can never block my merge — and the deterministic test suite stays offline.

**Why this priority**: This is the single hardest, load-bearing architectural invariant (PRD NFR-1). A network call leaking into the test suite or PR path would re-introduce exactly the non-determinism `test_citation_shape()` was written to exclude. Co-equal P1 with US-1 because violating it would make the feature net-negative.

**Independent Test**: Statically inspect the new workflow's triggers and the pytest collection import graph; verify no `pull_request`/`push` trigger exists and no HTTP-making module is reachable from test collection.

**Acceptance Scenarios**:

1. **Given** the new workflow, **When** its triggers are inspected, **Then** only `schedule` and `workflow_dispatch` are declared and neither `on: pull_request` nor `on: push` is present.
2. **Given** the checker script, **When** the pytest collection path is analyzed, **Then** the script is not importable from any test module (no shared import pulls outbound HTTP into test collection).
3. **Given** a contributor opens a PR that touches a citation URL, **When** CI runs, **Then** no job fetches that URL and the merge is never gated on URL reachability.
4. **Given** the existing hermetic loopback fixture (`tests/scripts/conftest.py` `hanging_upstream`), **When** the determinism boundary is evaluated, **Then** that fixture remains valid (loopback/in-process is not an outbound/external fetch).

---

### User Story 3 - Trustworthy, Low-False-Positive Signal (Priority: P2)

*(PRD US-2)* As a maintainer, I want transient failures (5xx, timeouts) and bot-blocks (403/401/429) excluded from the confirmed-rot report, so that the tracking issue stays high-signal and I don't waste triage time on live-but-blocked MITRE URLs.

**Why this priority**: A signal full of false positives is worthless, but the false-positive policy is a refinement layered on US-1's detection. Given ~93% of URLs are MITRE-hosted, bot-blocking is the dominant false-positive risk.

**Independent Test**: Feed the classifier controlled responses (404, 410, 403, 429, 500, timeout, HEAD-405-then-GET-200) and assert each maps to the correct disposition without any network fetch.

**Acceptance Scenarios**:

1. **Given** a URL returns 401/403/429, **When** it is classified, **Then** it is recorded as "needs-review" and never as confirmed rot.
2. **Given** a URL returns 5xx, a timeout, a DNS failure, or a connection reset, **When** the checker retries with backoff and the failure persists, **Then** it is treated as transient and not reported.
3. **Given** a host that returns 405/403/501 to HEAD but 200 to GET, **When** the checker classifies it, **Then** it falls back to a ranged GET and records the URL as healthy (not rot).
4. **Given** a 3xx redirect, **When** the checker follows it (≤5 hops), **Then** classification is on the final status; a redirect loop or >5 hops is reported as broken.

---

### User Story 4 - One Self-Healing Tracking Issue (Priority: P2)

*(PRD US-4)* As a maintainer, I want all link-rot findings consolidated into a single tracking issue that updates in place and auto-closes when rot clears, so that I'm not buried under a new duplicate issue every week.

**Why this priority**: The idempotent issue lifecycle is the delivery vehicle for US-1's signal. It is P2 because detection (US-1) is the prerequisite value; the lifecycle is how that value is surfaced without noise.

**Independent Test**: Run the issue-lifecycle logic across the three states (rot+no-issue, rot+open-issue, no-rot+open-issue) against a controlled finding set and assert exactly one tracking issue is created/updated/closed accordingly.

**Acceptance Scenarios**:

1. **Given** confirmed rot exists and no open tracking issue is present, **When** the run completes, **Then** exactly one tracking issue is created with the stable sentinel title.
2. **Given** confirmed rot exists and a tracking issue is already open, **When** the run completes, **Then** the existing issue is updated in place (body reflects current state) and no duplicate issue is created.
3. **Given** zero confirmed rot and an open tracking issue, **When** the run completes, **Then** the issue is auto-closed with a recovery comment.
4. **Given** a rotted URL in the issue body, **When** it is read, **Then** it shows the URL, final HTTP status, framework source (catalog name or `crosswalk`), and citing record-id / edge-endpoints, grouped by host.

---

### Edge Cases

- **HEAD-unsupported endpoint**: a host that 405s on HEAD must be re-checked with a ranged GET before any rot classification (top false-positive source).
- **Shared URL across many records**: one URL (e.g. a shared OWASP Agentic document spanning ASI01–ASI10) maps to many source locations — all must be reported.
- **Cache miss / eviction**: `actions/cache` is evictable; a cache miss must mean "check everything," never "assume healthy."
- **Recovered-then-re-rotted URL**: a URL that flips 200→404→200 across runs must move into and back out of the single tracking issue without spawning duplicates.
- **New catalog added later**: a future `schemas/taxonomy/*.yaml` file must be auto-discovered by glob and covered without code changes; the offline parity guard must fail if a file silently escapes monitoring.
- **DOI redirect chains**: `doi.org` URLs may redirect to a publisher; follow ≤5 hops and classify on final status.
- **Validation must not self-flake**: the "confirmed-rot → one issue → self-close" success path must be exercised with a deterministic sentinel (injected fixture or dispatch input), never a live external 404 URL.

## Requirements *(mandatory)*

### Functional Requirements

> Each AC begins with **Given** and follows Given/When/Then. `[MANUAL-ONLY] <reason>` marks ACs that cannot be fully automated.

- **FR-001 (Dedicated scheduled workflow)**: The system MUST add a single-concern workflow that runs on a weekly off-`:00` cron and on manual dispatch, with least-privilege permissions, and MUST NOT run on PR or push.
  - **Given** the new workflow, **When** its triggers are inspected, **Then** only `schedule` (weekly, off-`:00` minute) and `workflow_dispatch` are declared.
  - **Given** the new workflow, **When** its permissions are inspected, **Then** they are exactly `contents: read` and `issues: write` (no `pull-requests`, no `contents: write`).
  - **Given** a maintainer, **When** they invoke the workflow manually, **Then** the job runs to a green completion on demand. `[MANUAL-ONLY] requires a live GitHub Actions dispatch run`

- **FR-002 (Zero-dependency checker script)**: The system MUST add a checker script invoked directly by the workflow, using only the Python standard library plus the already-pinned YAML parser.
  - **Given** the checker script, **When** its imports are inspected, **Then** it uses only stdlib modules and the already-pinned `pyyaml`, adding no new runtime dependency.
  - **Given** the dependency manifest, **When** compared before and after, **Then** `requirements-dev.txt` gains no new package (unless an opt-in `requests` path applies the F-250 lock-step in the same commit).

- **FR-003 (Glob extraction with back-reference map)**: The system MUST discover taxonomy files by glob (never a hardcoded list), extract the correct URL-bearing field per file type, filter to URL-shaped values, drop internal file-paths, dedup, and retain a URL→source-location(s) map.
  - **Given** `schemas/taxonomy/*.yaml`, **When** the checker runs, **Then** all matching files are discovered by glob with no hardcoded filename list.
  - **Given** a crosswalk edge, **When** extracted, **Then** its `citation` field is read; **Given** a catalog record, **When** extracted, **Then** its `url` field is read.
  - **Given** the extracted values, **When** filtered, **Then** only `^https?://` values are kept and internal file-path citations are dropped (already covered offline).
  - **Given** the deduplicated URL set, **When** a URL is later reported, **Then** the retained map resolves it to every citing source location.

- **FR-004 (HTTP classification semantics)**: The system MUST classify each fetch as healthy, link-rot, needs-review, or transient per defined status rules, using a HEAD-then-ranged-GET method with bounded redirects and retries.
  - **Given** a URL whose final status is 404/410/post-retry hard-4xx (e.g. 400/451), **When** classified, **Then** it is confirmed link-rot.
  - **Given** a URL returning 401/403/429, **When** classified, **Then** it is needs-review, never confirmed rot.
  - **Given** a URL returning 5xx/timeout/DNS/conn-reset, **When** retried (2 retries, exponential backoff) and still failing, **Then** it is transient and not reported; a 4xx is never retried.
  - **Given** a HEAD response of 405/403/501, **When** the checker proceeds, **Then** it falls back to a ranged `GET` (`Range: bytes=0-0`) before classifying.
  - **Given** a 3xx response, **When** followed up to 5 hops, **Then** classification uses the final status; a loop or >5 hops is reported.

- **FR-005 (Per-host rate limiting & politeness)**: The system MUST throttle per host (not just globally), send a descriptive User-Agent and Accept header, and honor `Retry-After`.
  - **Given** the ~93% MITRE host concentration, **When** the checker fetches, **Then** in-flight connections are capped per host (≈2–3) under a global cap (≈10) with an inter-request politeness delay.
  - **Given** any request, **When** it is sent, **Then** it carries a descriptive contactable `User-Agent` and an `Accept: text/html,*/*` header.
  - **Given** a 429/503 with a `Retry-After` header, **When** received, **Then** the checker waits the indicated interval before retrying.
  - **Given** a full uncached sweep, **When** it runs, **Then** it completes within a minute-scale budget without triggering a host ban. `[MANUAL-ONLY] ban-avoidance is validated by live dispatch runs, not unit tests`

- **FR-006 (Last-successful-check caching)**: The system MUST cache a per-URL last-2xx timestamp ledger (not committed to the repo), treating a cache miss as "check everything" and never caching a 4xx as OK.
  - **Given** a per-URL last-success ledger in the Actions cache, **When** a URL's last 2xx was within the TTL (~21 days), **Then** it is skipped this run.
  - **Given** a cache miss or eviction, **When** the run starts, **Then** all URLs are checked (never assumed healthy).
  - **Given** a URL that returns 4xx, **When** the run completes, **Then** it is not written to the ledger as OK and is re-checked every run until fixed.
  - **Given** a URL with a 2xx-final outcome, **When** the run completes, **Then** a fresh success timestamp is written.

- **FR-007 (Single deduplicated tracking issue)**: The system MUST maintain exactly one tracking issue via the native `gh` CLI — created on first rot, updated in place on subsequent rot, auto-closed on recovery — never per-run or per-URL issues.
  - **Given** confirmed rot and no open tracking issue (matched by stable title sentinel), **When** the run completes, **Then** exactly one issue is created.
  - **Given** confirmed rot and an open tracking issue, **When** the run completes, **Then** the existing issue's machine-block body is rewritten to current state and a dated delta comment is posted — no duplicate issue.
  - **Given** zero confirmed rot and an open tracking issue, **When** the run completes, **Then** the issue is auto-closed with an "all citations healthy as of `<date>`" comment.
  - **Given** the issue body, **When** read, **Then** each rotted URL shows URL, final status, framework source, and citing record-id/edge-endpoints, grouped by host.

- **FR-008 (Offline structural-parity guard)**: The system MUST add a fetch-free assertion to the deterministic suite that the extractor's glob+filter recovers the same URL set as `test_citation_shape()`, and encodes the per-file field rule.
  - **Given** the deterministic suite, **When** the parity guard runs, **Then** it asserts set-parity in both directions between the extractor's URL set and the integrity test's URL set.
  - **Given** the field rule, **When** asserted, **Then** the guard encodes "crosswalk → `citation` field; all other `schemas/taxonomy/*.yaml` catalogs → `url` field" so schema/field drift is caught.
  - **Given** the parity guard, **When** it executes, **Then** it performs no network fetch and is eligible to run on the PR gate (flake-free).

- **FR-009 (README deferral note update)**: The system MUST update the link-rot deferral note in the taxonomy README to reference the live scheduled monitor.
  - **Given** `schemas/taxonomy/README.md` line ~224, **When** the feature ships, **Then** the "out of F-A1 scope" deferral text is replaced with a reference to the live scheduled link-rot monitor.

### Non-Functional Requirements

- **NFR-001 (Determinism boundary — load-bearing)**: No outbound/external network call may ever be introduced into `tests/` or any `pull_request`/`push`-triggered job. Link-rot validation is scheduled-only; the checker MUST NOT be importable from the pytest collection path. The existing hermetic loopback fixture is explicitly not in conflict (it targets the public internet, not loopback scaffolding).
- **NFR-002 (Zero new runtime dependency)**: stdlib `urllib` + already-pinned `pyyaml` only; any new dependency requires the F-250 lock-step (manifest + workflow in one commit) and is dispreferred.
- **NFR-003 (Politeness / no throttle-ban)**: per-host concurrency cap (not just global), politeness delay, descriptive UA, `Retry-After` honored; a full uncached sweep stays within a weekly job's time budget and must not trigger a WAF ban.
- **NFR-004 (Signal quality / low false-positive)**: only 404/410/post-retry-hard-4xx auto-file as confirmed rot; 403/401/429 are needs-review; transient failures never file.
- **NFR-005 (Least privilege)**: workflow token scope limited to `contents: read` + `issues: write`.
- **NFR-006 (Idempotent issue lifecycle)**: exactly one tracking issue across runs; self-updating body; self-closing on recovery; no issue spam.
- **NFR-007 (Supply-chain minimalism)**: auto-issue via native `gh` (ambient `GITHUB_TOKEN`), no third-party marketplace action.

### Key Entities

- **In-scope citation URL**: a `^https?://` value extracted from a taxonomy YAML (`citation` in crosswalk edges, `url` in catalog records); internal file-path citations are excluded.
- **Source-location back-reference**: the mapping from a distinct URL to the list of records/edges that cite it (`<file>: <record-id>` or `crosswalk edge <src> → <dst>`).
- **Classification outcome**: one of healthy / link-rot / needs-review / transient, derived from the final HTTP status after redirects and retries.
- **Last-successful-check ledger**: a `{url: iso8601_last_ok}` map persisted in the Actions cache (never the repo); only 2xx-final outcomes write entries.
- **Tracking issue**: the single sentinel-titled GitHub issue holding current open findings; created/updated/closed idempotently.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The scheduled workflow runs green weekly and on manual dispatch (no infrastructure error).
- **SC-002**: A deterministic sentinel rot fixture (not a live external 404) produces **exactly one** tracking issue naming the URL, its final HTTP status, and its source location(s).
- **SC-003**: When the rotted URL is fixed, the tracking issue **self-closes** on the next run.
- **SC-004**: The `pytest` suite and every `pull_request`-triggered job remain **network-free** — verifiable that no HTTP-making module is reachable from the test collection path.
- **SC-005**: **Zero** PR-blocking incidents are attributable to the link-rot check.
- **SC-006**: 403/401/429 responses **never** appear as confirmed rot in the tracking issue.
- **SC-007**: **Zero** new runtime dependencies are added (stdlib + already-pinned `pyyaml` only).
- **SC-008**: The offline structural-parity guard passes on the PR gate and fails if a taxonomy file or field-rule drift would drop a URL from monitoring.

## Assumptions

- `gh` CLI is available on GitHub-hosted runners with an ambient `GITHUB_TOKEN` (confirmed).
- External authorities (MITRE/NIST/OWASP) tolerate a polite, throttled weekly sweep with a descriptive UA.
- `pyyaml` remains pinned in `requirements-dev.txt`.
- Architect baseline decisions are adopted as defaults: cron `17 9 * * 1`; stdlib `urllib`; cache TTL ~21 days; per-host cap 2–3 / global 10; 403/401/429 = needs-review.

## Dependencies

- **Feature 180 (F-A1, DELIVERED)** — provides `crosswalk.yaml`, the catalog YAMLs, the canonical-URL conventions, and `test_citation_shape()` (the offline guard this complements).
- **The taxonomy YAMLs** under `schemas/taxonomy/` (glob-discovered; surface grows with BLP-05 Wave 2 catalogs).
- **GitHub Actions runtime** — `gh` CLI, `GITHUB_TOKEN`, `actions/cache@v4`, `actions/setup-python@v5`.

## Out of Scope

- Internal file-path citation validation (already covered offline by `test_citation_shape()`).
- On-PR / real-time URL validation (violates NFR-001; scheduled-only by design).
- Auto-replacement of rotted URLs (the job reports; a maintainer triages).
- General docs/markdown external-link checking (scope is `schemas/taxonomy/*.yaml` only).
- Wayback/archival snapshotting (possible future enhancement).
- Any blocking/gating CI behavior (monitoring signal, never a merge gate).
