---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-14
    status: APPROVED
    notes: "Faithful, bounded translation of the approved spec. User stories 4/4 (US1→Phase3, US2→Phase4, US3→Phase5, US4→Phase6, every AC mapped); FR traceability 9/9; SC traceability 8/8 (SC-002/003 correctly MANUAL-ONLY in T021 per TL-2 deterministic sentinel). Zero scope creep — all 6 out-of-scope items absent; never-blocks-merge reinforced in T002/T007/T008. MVP (Phases 1–3 + T008) delivers the weekly confirmed-rot signal on a scheduled-only trigger. 2 informational notes, no action. Details: .aod/results/product-manager-183-tasks.md"
  architect_signoff:
    agent: architect
    date: 2026-06-14
    status: APPROVED
    notes: "Technically correct, dependency-ordered, contract-faithful. CONCERN-1 (FR-008 dual-surface parity — crosswalk citation [test_citation_shape] AND catalog url [test_framework_yamls_load], both directions) correctly encoded in T010 with the uniform ^https?:// filter (CONCERN-2). NFR-001 no-network-in-tests structurally enforced (T009 + file layout). No false [P] parallelism / no broken prerequisites; critical path (single-file script chain) accurate; exit-code/cache/HEAD→GET/sentinel/least-privilege contracts honored. 4 LOW/INFO findings, no tasks.md edit required. Details: .aod/results/architect-183-tasks.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-06-14
    status: APPROVED
    notes: "Feasible; correctly granular (21 tasks / 2.0–3.0 eng-days); critical path accurate (single-file script chain is the long pole); parallelization matches the W1-a script ∥ W1-b workflow → W2 tester → W3 reviewer∥security wave plan without same-file races. All 3 PRD concerns honored: TL-1 (effort 2.0–3.0d), TL-2 (T016 sentinel pre-classified/no-fetch, deterministic), TL-3 (T010 set-parity + field rule, now both-surfaces). T021 validation correctly deliver-adjacent / MANUAL-ONLY / never-a-PR-gate. 2 INFO/cosmetic notes, zero blockers, no veto. Details: .aod/results/team-lead-183-tasks.md"
---

# Tasks: Citation-URL Link-Rot Monitoring — Scheduled CI Check

**Input**: Design documents from `specs/183-citation-url-link-rot-monitoring/`
**Prerequisites**: plan.md ✓ (dual-approved), spec.md ✓ (PM-approved), research.md, data-model.md, contracts/ (checker-cli, workflow, tracking-issue, cache-ledger.schema.json), quickstart.md

**Tests**: REQUIRED (not optional) — FR-008 (offline structural-parity guard) and the classifier dispositions (SC-006) are spec'd functional requirements, and Constitution Principle VI mandates test coverage. All tests are **offline / network-free** (NFR-001).

**Organization**: by user story (spec ordering; PRD-story map noted). Build waves follow the Team-Lead plan: **W1-a** `senior-backend-engineer` (script) ∥ **W1-b** `devops` (workflow) → **W2** `tester` (offline tests) → **W3** `code-reviewer` ∥ `security-analyst` → live dispatch validation.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: can run in parallel (different file, no incomplete dependency)
- **[Story]**: US1–US4 (user-story phases only)
- All paths are repo-root-relative.

**File-sharing note**: `scripts/check-citation-urls.py` is one cohesive file built by a single agent (W1-a) — its tasks are sequential (no `[P]` among them). `tests/schemas/test_citation_linkrot_parity.py` is likewise one file (W2) — its test tasks are sequential. The workflow YAML and README are separate files (genuinely parallel).

---

## Phase 1: Setup

**Purpose**: Establish the zero-dependency posture and the script file.

- [ ] T001 Verify runtime prerequisites and zero-dep posture: confirm `requirements-dev.txt` pins `pyyaml>=6.0` and that the design needs **no new runtime dependency** (stdlib `urllib`/`concurrent.futures` only, NFR-002); create `scripts/check-citation-urls.py` with `#!/usr/bin/env python3`, module docstring (purpose + exit-code legend: `0` ok incl. rot-found, `2` infra error), and `from __future__ import annotations`.

**Checkpoint**: script file exists; no dependency changes required.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The script's non-network core — the CLI surface and URL extraction every story depends on.

**CRITICAL**: No user-story work can begin until this phase is complete.

- [ ] T002 Implement the argparse CLI surface + `main()` skeleton in `scripts/check-citation-urls.py` per `contracts/checker-cli.md` — all flags (`--taxonomy-glob`, `--ledger-path`, `--no-cache`, `--ttl-days`, `--max-host-concurrency`, `--global-concurrency`, `--politeness-ms`, `--connect-timeout`, `--read-timeout`, `--inject-sentinel-rot`, `--dry-run`, `--json`), exit-code discipline (return `0` even when link-rot is found; non-zero `2` only on genuine infra error — never wire rot as a gate).
- [ ] T003 Implement `discover_urls()` in `scripts/check-citation-urls.py` (FR-003): glob `schemas/taxonomy/*.yaml` (never a hardcoded list); `yaml.safe_load` each; apply the field rule (crosswalk edges → `citation`; all other catalogs → `url`); filter to `^https?://` (drop internal file-path citations + the pseudo-taxonomy file-path `url:` values); dedup; build the `url → [SourceLocation]` back-reference map (`SourceLocation{file, kind, record_ref}` per `data-model.md`).

**Checkpoint**: `discover_urls()` returns the deduped in-scope URL set with source back-references; extractor ready for both detection and the parity guard.

---

## Phase 3: User Story 1 — Weekly Confirmed-Rot Signal (Priority: P1) MVP

**Goal** *(PRD US-1)*: A scheduled run fetches every taxonomy citation URL and reports confirmed rot (404/410) with each citing source location.

**Independent Test**: `python scripts/check-citation-urls.py --dry-run --json` fetches all in-scope URLs and prints the confirmed-rot list (URL + final status + source location(s)) without any `gh` I/O.

- [ ] T004 [US1] Implement `HostThrottler` in `scripts/check-citation-urls.py` (FR-005, NFR-003): per-host `threading.Semaphore` (`--max-host-concurrency`, default 3) under a global `ThreadPoolExecutor` cap (`--global-concurrency`, default 10); per-host politeness delay (`--politeness-ms`); descriptive `User-Agent` (`tachi-linkrot-monitor/1.0 (+https://github.com/davidmatousek/tachi; citation integrity check)`) + `Accept: text/html,*/*`; honor `Retry-After`.
- [ ] T005 [US1] Implement `classify_url()` core fetch path in `scripts/check-citation-urls.py` (FR-004 detection half): HEAD → ranged-`GET` (`Range: bytes=0-0`) fallback on 405/403/501; follow ≤5 redirects and classify on the **final** status; `2xx`→`HEALTHY`, `404/410/`post-retry-hard-4xx (400/451)→`LINK_ROT`; return `Classification{url, verdict, final_status, final_url, detail}`.
- [ ] T006 [US1] Implement `render_issue_body()` confirmed-rot section in `scripts/check-citation-urls.py` (FR-007 body; `data-model.md` `TrackingIssueBody`): group confirmed rot by host; per URL emit URL + final status + every `SourceLocation` display form (`<file>: <record-id>` / `crosswalk edge <src> → <dst>`); wrap in the delimited machine block `<!--linkrot:start-->…<!--linkrot:end-->`.
- [ ] T007 [US1] Wire the detection flow in `main()` (FR-001 invocation): `discover_urls()` → throttled `classify_url()` over all URLs → partition by verdict → render confirmed rot; support `--dry-run` (no `gh`) and `--json` summary; exit `0` even when rot is found.

**Checkpoint**: MVP — a dry-run sweep identifies 404/410 citations with their sources. Delivers the core taxonomy-steward value.

---

## Phase 4: User Story 2 — Never Blocks a Merge & Determinism Preserved (Priority: P1)

**Goal** *(PRD US-3)*: The monitor runs scheduled-only (never on PR), and offline guards keep the pytest/PR path network-free and the monitored URL set drift-proof.

**Independent Test**: Inspect the workflow triggers (no `pull_request`/`push`) and run the new pytest module — it passes with no socket opened and fails if a taxonomy file/field would drop URLs from monitoring.

- [ ] T008 [P] [US2] Create `.github/workflows/tachi-citation-linkrot.yml` per `contracts/workflow.md` (FR-001, NFR-001, NFR-005): `on.schedule` `"17 9 * * 1"` + `on.workflow_dispatch` with boolean input `inject_sentinel_rot`; `permissions: contents: read` + `issues: write` (nothing else); steps `actions/checkout@v4` → `actions/setup-python@v5` (3.11) → **combined** `actions/cache@v4` (restore+save, `key: linkrot-ledger-v1-${{ github.run_id }}`, `restore-keys: linkrot-ledger-v1-`) → run `scripts/check-citation-urls.py --json` (passing `--inject-sentinel-rot` when the input is true) with `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}`; **MUST NOT** declare `on.pull_request`/`on.push`. *(devops, W1-b)*
- [ ] T009 [US2] Add the NFR-001 determinism-boundary test to `tests/schemas/test_citation_linkrot_parity.py` (SC-004): assert that importing the test/checker module performs no DNS resolution and opens no outbound socket (stub/guard `socket.socket`/`socket.getaddrinfo` and assert un-called on import-time code paths), documenting that the checker's network surface is reachable only from the scheduled-workflow invocation, never from pytest collection. *(tester, W2)*
- [ ] T010 [US2] Add the FR-008 offline structural-parity guard to `tests/schemas/test_citation_linkrot_parity.py` (SC-008; architect CONCERN-1/CONCERN-2): assert set-parity **both directions** between `discover_urls()`'s URL set and the **union** of (a) the crosswalk `citation` surface that `test_citation_shape()` validates **and** (b) the catalog `url` surface that `test_framework_yamls_load()` validates; encode the field rule (crosswalk→`citation`; all other catalogs→`url`) with a **uniform** `^https?://` filter so the pseudo-taxonomy file-path `url:` values drop identically; **no network fetch** (PR-gate-eligible). *(tester, W2)*

**Checkpoint**: workflow is scheduled-only; pytest stays offline; a catalog `url:`→`link:` rename (or a dropped file) fails the parity guard.

---

## Phase 5: User Story 3 — Trustworthy, Low-False-Positive Signal (Priority: P2)

**Goal** *(PRD US-2)*: Refine classification so bot-blocks (403/401/429) are needs-review and transient failures (5xx/timeout) are never reported.

**Independent Test**: Drive `classify_url()` with stubbed responses and assert each status maps to the correct verdict, with no socket opened.

- [ ] T011 [US3] Extend `classify_url()` in `scripts/check-citation-urls.py` (FR-004 full semantics, NFR-004): `401/403/429`→`NEEDS_REVIEW` (never confirmed rot); `5xx/timeout/DNS/conn-reset`→`TRANSIENT` with 2 retries (exponential backoff 1→2→4 s + jitter), **never retry a 4xx**; a redirect loop or >5 hops → report as broken.
- [ ] T012 [US3] Extend `render_issue_body()` in `scripts/check-citation-urls.py` (FR-007, NFR-004): add a separate "Needs manual verification (possibly bot-blocked)" section for `NEEDS_REVIEW`; ensure `TRANSIENT` is never rendered/reported; confirmed-rot count (the open/close driver) excludes needs-review.
- [ ] T013 [US3] Add classifier unit tests to `tests/schemas/test_citation_linkrot_parity.py` (SC-006, offline, stub the transport): `200`, `301→200`, `404`, `410`, `403`, `429`, `500`, timeout, `HEAD 405→GET 200`, redirect-loop, `>5 hops` → assert the correct `Verdict`; assert no real socket is opened. *(tester, W2)*

**Checkpoint**: every status classifies correctly; 403/401/429 never appear as confirmed rot; transient never files.

---

## Phase 6: User Story 4 — One Self-Healing Tracking Issue (Priority: P2)

**Goal** *(PRD US-4)*: Consolidate findings into a single sentinel-titled issue that updates in place and self-closes on recovery; validate the lifecycle deterministically.

**Independent Test**: With `--dry-run --inject-sentinel-rot`, the rendered output shows a `would-create` action for the synthetic finding (no network); lifecycle branches exercised against controlled finding sets.

- [ ] T014 [US4] Implement `Ledger` in `scripts/check-citation-urls.py` (FR-006; `contracts/cache-ledger.schema.json`): load/save the JSON ledger; TTL `--ttl-days` (default 21) skip; **cache-miss = check-all** (never assume healthy); only a `2xx`-final outcome writes/refreshes `last_ok`; a `4xx` is **never** cached OK and is re-checked every run; persist `last_status` for "previously healthy `<date>`" context; honor `--no-cache`.
- [ ] T015 [US4] Implement `manage_tracking_issue()` in `scripts/check-citation-urls.py` via the native `gh` CLI (FR-007, NFR-006/NFR-007; `contracts/tracking-issue.md`): look up by stable title sentinel `[link-rot] Taxonomy citation link-rot — open findings`; `rot>0 & no issue`→`gh issue create` (sentinel title + `follow-on-180` label, best-effort `link-rot` label); `rot>0 & open`→`gh issue edit` (rewrite machine block) + dated delta comment; `rot==0 & open`→comment "all citations healthy as of `<date>`" + `gh issue close`; confirmed rot is the **sole** open/close driver (needs-review never opens an issue); never create per-run/per-URL issues.
- [ ] T016 [US4] Implement sentinel injection in `scripts/check-citation-urls.py` (TL-2; `data-model.md` §Sentinel Injection): when `--inject-sentinel-rot` is set, append a **pre-classified** `Classification("https://example.invalid/tachi-linkrot-sentinel", LINK_ROT, 404, detail="injected sentinel")` + synthetic `SourceLocation` directly into the confirmed-rot set **with no fetch**; this is the input the workflow wires from `inject_sentinel_rot` to make SC-002/SC-003 reproducible.

**Checkpoint**: issue lifecycle complete; `--dry-run --inject-sentinel-rot` deterministically shows the create path.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T017 [P] Update `schemas/taxonomy/README.md` (~line 224) (FR-009): replace the "Link-rot monitoring … out of F-A1 scope (follow-on Issue filed …)" deferral with a reference to the live scheduled monitor (`.github/workflows/tachi-citation-linkrot.yml`). *(senior-backend-engineer)*
- [ ] T018 Type-hint + docstring + no-silent-failure pass over `scripts/check-citation-urls.py` (Constitution Code Quality): full type hints, explicit error handling, graceful degradation (transient never reported, cache-miss = check-all, `gh` comment failure non-fatal but logged). *(senior-backend-engineer)*
- [ ] T019 Run the offline suite `python3 -m pytest tests/schemas/test_citation_linkrot_parity.py -v` — parity (both surfaces, both directions) + NFR-001 boundary + full classifier matrix all green, **network-free**; also run the existing `tests/schemas/test_taxonomy_integrity.py` to confirm zero regression. *(tester)*
- [ ] T020 W3 review — `code-reviewer` ∥ `security-analyst`: verify zero new runtime dependency, least-privilege permissions (`contents: read` + `issues: write` only), no-network-in-tests (inspect the pytest collection import graph for NFR-001), exit-code discipline, supply-chain minimalism (native `gh`, no marketplace action), and that `--inject-sentinel-rot` cannot leak into a scheduled (non-dispatch) run.
- [ ] T021 Live dispatch validation (deliver-adjacent) `[MANUAL-ONLY] requires real GitHub Actions runs` (SC-001/SC-002/SC-003): per `quickstart.md` §4 — Run 1 `gh workflow run tachi-citation-linkrot.yml -f inject_sentinel_rot=true` → exactly one open sentinel-titled tracking issue naming the sentinel URL + 404 + source; Run 2 `-f inject_sentinel_rot=false` → the issue self-closes with a recovery comment. *(devops + tester)*

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (P1)** → no deps.
- **Foundational (P2)** → after Setup; **blocks all user stories** (T003 `discover_urls` is needed by detection AND the parity guard).
- **US-1 (P3)** → after Foundational. The MVP.
- **US-2 (P4)** → after Foundational. T008 (workflow) is independent of the script chain; T010 (parity) depends on T003; T009 depends only on the module existing.
- **US-3 (P5)** → extends US-1's `classify_url`/`render` (T011 after T005; T012 after T006); T013 after T011.
- **US-4 (P6)** → script-internal; T015 (issue I/O) after T006/T012 (body render); T016 after T015.
- **Polish (P7)** → after the stories it touches; T019 after the test tasks (T009/T010/T013); T020 after all code; T021 last (post-merge).

### Critical Path
T001 → T002 → T003 → T004 → T005 → T006 → T007 → T011 → T012 → T014 → T015 → T016 → T018 → T019 → T020 → T021. (The script chain is the long pole — one file, one agent.)

### Parallel Opportunities
- **W1**: T008 (workflow, devops) runs fully in parallel with the entire T002→T007 script chain (senior-backend-engineer).
- **W2**: once T003 lands, T010 (parity guard) can start; once T005/T011 land, T009 + T013 can be authored — all by the tester, parallel to remaining script polish.
- **Polish**: T017 (README) is `[P]` — independent file, any time after the workflow name is fixed (T008).
- **W3**: T020's `code-reviewer` and `security-analyst` run concurrently.

---

## Parallel Example: Wave 1

```bash
# W1-a (senior-backend-engineer) builds the script sequentially: T001→T002→T003→T004→T005→T006→T007
# W1-b (devops) builds the workflow in parallel:
Task: "Create .github/workflows/tachi-citation-linkrot.yml per contracts/workflow.md (T008)"
```

## Parallel Example: Wave 3

```bash
Task: "code-reviewer: review zero-dep / exit-code / no-network-in-tests (T020)"
Task: "security-analyst: review least-privilege perms / supply-chain / NFR-001 boundary (T020)"
```

---

## Implementation Strategy

### MVP First (US-1)
1. Phase 1 Setup → Phase 2 Foundational → Phase 3 US-1.
2. **STOP & VALIDATE**: `python scripts/check-citation-urls.py --dry-run --json` finds 404/410 with sources.
3. US-1 + the US-2 workflow (T008) together give a runnable scheduled monitor.

### Incremental Delivery
- US-1 (detect + report) → US-2 (scheduled-only + offline guards) → US-3 (trustworthy signal) → US-4 (self-healing issue) → Polish.
- Each story adds value without breaking the prior; the offline test surface (US-2/US-3 tests) is PR-gate-eligible and grows with the script.

### Validation Gate (deliver-adjacent)
- T021 two-run dispatch is the SC-002/SC-003 acceptance; it is correctly **never** a PR gate.

---

## Notes
- `[P]` = different file, no incomplete dependency. The script and the test module are each single files → their tasks are sequential within their owning agent.
- Tests are network-free by mandate (NFR-001); the only live network is the scheduled checker and the deliver-adjacent dispatch validation (T021, MANUAL-ONLY).
- Commit after each task or logical group; push to keep draft PR #330 current.
- Architect CONCERN-1 is encoded in T010 (parity must cover both crosswalk-citation AND catalog-url surfaces).

## Summary
- **Total tasks**: 21 (T001–T021).
- **Per story**: Setup 1 · Foundational 2 · US-1 4 · US-2 3 · US-3 3 · US-4 3 · Polish 5.
- **Tests**: 4 task-slots (T009 boundary, T010 parity, T013 classifier, T019 run) — all offline.
- **Parallel**: T008 ∥ script chain; T017 [P]; T020 two reviewers concurrent.
- **MVP scope**: Phases 1–3 (T001–T007) + workflow T008 = a runnable scheduled confirmed-rot monitor.
- **Effort**: 2.0–3.0 eng-days (Team-Lead; plan to 3, expect 2).
