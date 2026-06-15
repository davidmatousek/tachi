# Agent Assignments: Feature #183 — Citation-URL Link-Rot Monitoring

**Feature**: Citation-URL Link-Rot Monitoring — Scheduled CI Check
**Source of truth**: `specs/183-citation-url-link-rot-monitoring/tasks.md` (21 tasks T001–T021, triple-approved)
**Plan**: `specs/183-citation-url-link-rot-monitoring/plan.md`
**Triad sign-off**: PM ✓ · Architect ✓ · Team-Lead ✓ (all APPROVED 2026-06-14)
**Feasibility**: APPROVED — 2.0–3.0 eng-days (plan to 3, expect 2)
**Initiative**: BLP-05 Wave 3 (final remaining item; #182 already delivered)

All `subagent_type` values below are exact names from `.claude/agents/_README.md` — no generic labels.

---

## 1. Agent Assignment Matrix

Every task T001–T021 maps to exactly one owning agent and the file it touches. The two largest deliverables are **single cohesive files**: `scripts/check-citation-urls.py` (built sequentially by `senior-backend-engineer`) and `tests/schemas/test_citation_linkrot_parity.py` (built sequentially by `tester`). Within each single file there is **no `[P]` parallelism** — same-file edits serialize.

| Task | Phase | Story | Agent (`subagent_type`) | File(s) touched |
|------|-------|-------|-------------------------|-----------------|
| T001 | 1 Setup | — | `senior-backend-engineer` | `scripts/check-citation-urls.py` (create + docstring + exit-code legend); reads `requirements-dev.txt` |
| T002 | 2 Foundational | — | `senior-backend-engineer` | `scripts/check-citation-urls.py` (argparse CLI + `main()` skeleton) |
| T003 | 2 Foundational | — | `senior-backend-engineer` | `scripts/check-citation-urls.py` (`discover_urls()` + back-ref map); reads `schemas/taxonomy/*.yaml` |
| T004 | 3 US1 (MVP) | US1 | `senior-backend-engineer` | `scripts/check-citation-urls.py` (`HostThrottler`) |
| T005 | 3 US1 (MVP) | US1 | `senior-backend-engineer` | `scripts/check-citation-urls.py` (`classify_url()` core fetch) |
| T006 | 3 US1 (MVP) | US1 | `senior-backend-engineer` | `scripts/check-citation-urls.py` (`render_issue_body()` confirmed-rot section) |
| T007 | 3 US1 (MVP) | US1 | `senior-backend-engineer` | `scripts/check-citation-urls.py` (detection flow in `main()`) |
| T008 | 4 US2 | US2 | `devops` | `.github/workflows/tachi-citation-linkrot.yml` (create) |
| T009 | 4 US2 | US2 | `tester` | `tests/schemas/test_citation_linkrot_parity.py` (NFR-001 no-socket boundary test) |
| T010 | 4 US2 | US2 | `tester` | `tests/schemas/test_citation_linkrot_parity.py` (FR-008 dual-surface parity guard) |
| T011 | 5 US3 | US3 | `senior-backend-engineer` | `scripts/check-citation-urls.py` (`classify_url()` full semantics + retries) |
| T012 | 5 US3 | US3 | `senior-backend-engineer` | `scripts/check-citation-urls.py` (`render_issue_body()` needs-review section) |
| T013 | 5 US3 | US3 | `tester` | `tests/schemas/test_citation_linkrot_parity.py` (classifier matrix unit tests) |
| T014 | 6 US4 | US4 | `senior-backend-engineer` | `scripts/check-citation-urls.py` (`Ledger` TTL cache) |
| T015 | 6 US4 | US4 | `senior-backend-engineer` | `scripts/check-citation-urls.py` (`manage_tracking_issue()` via `gh` CLI) |
| T016 | 6 US4 | US4 | `senior-backend-engineer` | `scripts/check-citation-urls.py` (sentinel injection, pre-classified/no-fetch) |
| T017 | 7 Polish | — | `senior-backend-engineer` | `schemas/taxonomy/README.md` (~line 224, replace deferral with live-monitor reference) |
| T018 | 7 Polish | — | `senior-backend-engineer` | `scripts/check-citation-urls.py` (type hints + docstrings + no-silent-failure) |
| T019 | 7 Polish | — | `tester` | Run `tests/schemas/test_citation_linkrot_parity.py` + `tests/schemas/test_taxonomy_integrity.py` (regression) |
| T020 | 7 Polish | — | `code-reviewer` ∥ `security-analyst` | Review-only (whole feature branch); writes `.aod/results/code-reviewer.md` + `.aod/results/security-analyst.md` |
| T021 | 7 Polish | — | `devops` + `tester` | **[MANUAL-ONLY / deliver-adjacent]** Live two-run `gh workflow run` dispatch validation per `quickstart.md` §4 |

**Agent load summary** (eng tasks only, T021 excluded as MANUAL):

| Agent | Tasks owned | Notes |
|-------|-------------|-------|
| `senior-backend-engineer` | T001–T007, T011–T012, T014–T016, T017, T018 (14) | Single-file script chain = the critical path / long pole. README (T017) is the only off-script task. |
| `tester` | T009, T010, T013, T019 (4) | Single-file test module + run. All offline / network-free. |
| `devops` | T008 (1 build) + T021 (manual) | Workflow YAML in W1; live dispatch at delivery. |
| `code-reviewer` | T020 (½ of review) | Concurrent with security-analyst. |
| `security-analyst` | T020 (½ of review) | Concurrent with code-reviewer. |

No agent is overloaded: the script chain is inherently sequential (one file, one author), so concentrating it on `senior-backend-engineer` is correct rather than an imbalance — splitting one file across agents would create same-file races, not parallelism.

---

## 2. Parallel Execution Waves

```
            ┌──────────────────────────── Wave 1 ────────────────────────────┐
            │                                                                 │
 W1-a  senior-backend-engineer  T001→T002→T003→T004→T005→T006→T007  (script, SEQUENTIAL — one file)
            │                                                                 │
 W1-b  devops                   T008  (.github/workflows/...yml — PARALLEL, separate file)
            │                                                                 │
            └─────────────────────────────────┬───────────────────────────────┘
                                               │  [Gate G1]
                                               ▼
            ┌──────────────────────────── Wave 2 ────────────────────────────┐
 W2    tester  T009→T010→T013  (test module, SEQUENTIAL — one file) → T019 (run suite)
       (T017 README [P] by senior-backend-engineer may run any time after T008)
            └─────────────────────────────────┬───────────────────────────────┘
       (note: script polish T011/T012/T014/T015/T016/T018 continues on W1-a in parallel
        with W2 authoring — T013 needs T011, T010 needs T003)
                                               │  [Gate G2]
                                               ▼
            ┌──────────────────────────── Wave 3 ────────────────────────────┐
 W3    code-reviewer  ∥  security-analyst   T020  (review, CONCURRENT — read-only)
            └─────────────────────────────────┬───────────────────────────────┘
                                               │  [Gate G3]
                                               ▼
       ┌──────────────── Deliver-adjacent (MANUAL-ONLY) ─────────────────┐
       │  devops + tester   T021  (live two-run gh workflow dispatch)     │
       │  NEVER a PR gate · requires real GitHub Actions runs             │
       └──────────────────────────────────────────────────────────────────┘
```

### Wave 1 — Script ∥ Workflow (the runnable MVP)
- **W1-a `senior-backend-engineer`** (sequential, single file `scripts/check-citation-urls.py`): T001 → T002 → T003 → T004 → T005 → T006 → T007. This is the critical path. **No `[P]` inside this chain** — every task edits the same file.
- **W1-b `devops`** (parallel, separate file `.github/workflows/tachi-citation-linkrot.yml`): T008. Genuinely independent of the script chain — different file, no dependency. Starts at the same moment as T001.
- **MVP boundary**: T001–T007 (script) + T008 (workflow) together = a runnable scheduled confirmed-rot monitor.

### Wave 2 — Offline Tests (PR-gate-eligible)
- **W2 `tester`** (sequential, single file `tests/schemas/test_citation_linkrot_parity.py`): T009 → T010 → T013, then T019 runs the suite. **No `[P]` inside this chain** — same file.
  - Dependency notes: T010 (parity) needs T003 (`discover_urls`); T013 (classifier matrix) needs T011 (`classify_url` full semantics); T009 (boundary) needs only the module to exist.
- **Overlap with continuing script work**: while `tester` authors the test module, `senior-backend-engineer` continues the remaining script tasks (T011, T012, T014, T015, T016, T018) on W1-a. These are different files, so the two agents run concurrently — this is the real Wave-1/Wave-2 overlap.
- **T017 README `[P]`** (`senior-backend-engineer`, file `schemas/taxonomy/README.md`): independent file; schedulable any time after the workflow filename is fixed by T008.

### Wave 3 — Review ∥ Security (read-only, concurrent)
- **W3 `code-reviewer` and `security-analyst`** run **simultaneously** on the completed feature branch (T020). Both are read-only and write to their own `.aod/results/*.md`, so there is no file contention. Launch in a single message with two Agent calls.

### Deliver-adjacent — Live Dispatch Validation (MANUAL-ONLY)
- **`devops` + `tester`** jointly run T021: two real `gh workflow run` dispatches (sentinel-on then sentinel-off) verifying the issue create→self-close lifecycle per `quickstart.md` §4.
- This is **deliver-adjacent and MANUAL-ONLY** — it requires real GitHub Actions runs and is **never a PR/merge gate** (SC-002/SC-003 are deterministic-sentinel-driven by design).

### Same-file-sequential constraints (explicit)
| Single file | Owning agent | Sequential task chain | Why no `[P]` |
|-------------|--------------|-----------------------|--------------|
| `scripts/check-citation-urls.py` | `senior-backend-engineer` | T001→T002→T003→T004→T005→T006→T007→T011→T012→T014→T015→T016→T018 | One cohesive file; concurrent edits would race. |
| `tests/schemas/test_citation_linkrot_parity.py` | `tester` | T009→T010→T013 (T019 runs it) | One cohesive file; concurrent edits would race. |
| `.github/workflows/tachi-citation-linkrot.yml` | `devops` | T008 | Separate file → genuinely parallel to the script. |
| `schemas/taxonomy/README.md` | `senior-backend-engineer` | T017 | Separate file → `[P]`, schedulable after T008. |

---

## 3. Quality Gates Between Waves

| Gate | After Wave | Owner | Pass criteria (must all hold to advance) |
|------|-----------|-------|------------------------------------------|
| **G1** | Wave 1 | `senior-backend-engineer` + `devops` | **Dry-run MVP works**: `python scripts/check-citation-urls.py --dry-run --json` fetches all in-scope URLs and prints the confirmed-rot list (URL + final status + source location[s]) with **no `gh` I/O**, **exit 0 even when rot is found**. Workflow YAML is `on.schedule` + `on.workflow_dispatch` only — **no `pull_request`/`push`** triggers; permissions are `contents: read` + `issues: write` only. |
| **G2** | Wave 2 | `tester` | **pytest green & network-free**: `python3 -m pytest tests/schemas/test_citation_linkrot_parity.py -v` passes with **no socket opened** (NFR-001 boundary test green); FR-008 parity guard covers **both surfaces** (crosswalk `citation` + catalog `url`) in **both directions** and fails on a dropped file or `url:`→`link:` rename; classifier matrix maps every status correctly; `tests/schemas/test_taxonomy_integrity.py` shows **zero regression**. |
| **G3** | Wave 3 | `code-reviewer` + `security-analyst` | **Reviews pass**: both return APPROVED. Verified: zero new runtime dependency (stdlib only), least-privilege perms (`contents: read` + `issues: write`), no-network-in-tests (import-graph inspection), exit-code discipline, supply-chain minimalism (native `gh`, no marketplace action), and `--inject-sentinel-rot` cannot leak into a scheduled (non-dispatch) run. CHANGES_REQUESTED → fix on the owning agent's file and re-review. |
| **G-deliver** | Deliver-adjacent | `devops` + `tester` | **Live lifecycle confirmed** (MANUAL, not a merge gate): Run 1 (`-f inject_sentinel_rot=true`) creates exactly one open sentinel-titled tracking issue naming the sentinel URL + 404 + source; Run 2 (`-f inject_sentinel_rot=false`) self-closes it with a recovery comment. |

**Gate discipline**: Do not start Wave 2 test authoring for a given function before its source lands (T010 after T003; T013 after T011). Do not start Wave 3 until all code (through T018) and T019 are complete. G3 must be APPROVED before `/aod.deliver`. G-deliver is post-merge and never blocks the PR.

---

## 4. Time Estimates Per Wave

Total: **2.0–3.0 eng-days** (Team-Lead feasibility; **plan to 3, expect 2**). Wall-clock is shorter than eng-days because W1-b (devops) and the W1/W2 overlap run in parallel.

| Wave | Tasks | Optimistic | Realistic | Pessimistic | Parallelism note |
|------|-------|-----------|-----------|-------------|------------------|
| **Wave 1** | T001–T007 (script MVP) ∥ T008 (workflow) | 0.7d | 1.0d | 1.3d | W1-b (devops, ~0.3d) fully overlaps the W1-a script chain — does not add to wall-clock. |
| **Wave 2** | T009, T010, T013 + T011/T012/T014/T015/T016/T018 (continuing script) + T017, T019 | 0.7d | 1.0d | 1.3d | Test authoring (tester) overlaps remaining script polish (senior-backend-engineer); T017 [P] absorbed. |
| **Wave 3** | T020 (review ∥ security) | 0.2d | 0.3d | 0.4d | code-reviewer and security-analyst run concurrently → counts once. |
| **Subtotal (merge-blocking)** | T001–T020 | **1.6d** | **2.3d** | **3.0d** | Eng-days; plan to 3, expect ~2. |
| **Deliver-adjacent** | T021 (MANUAL live dispatch) | — | ~0.2d | — | Wall-clock only (waits on two real Actions runs); not counted toward the 2.0–3.0 eng-day envelope. |

**Critical path (the long pole)**: the single-file script chain
`T001 → T002 → T003 → T004 → T005 → T006 → T007 → T011 → T012 → T014 → T015 → T016 → T018 → T019 → T020`.
Because the script is one file owned by one agent, this chain sets the floor; devops and tester work in parallel against it but cannot shorten it below ~2 eng-days.

---

## Handoff to Orchestrator

- **Feasibility**: APPROVED (2.0–3.0 eng-days; plan to 3, expect 2).
- **tasks.md**: `specs/183-citation-url-link-rot-monitoring/tasks.md` (triple-approved).
- **Wave strategy**: W1 (`senior-backend-engineer` script ∥ `devops` workflow) → W2 (`tester` offline tests, overlapping continuing script) → W3 (`code-reviewer` ∥ `security-analyst`) → deliver-adjacent T021 (`devops` + `tester`, MANUAL).
- **Gates**: G1 dry-run MVP → G2 pytest green & network-free → G3 reviews APPROVED → G-deliver live lifecycle (non-blocking).
- **Constraints**: two single-file chains serialize (script, test module); never wire link-rot as a PR/merge gate; tests stay network-free (NFR-001); commit per task and keep draft PR #330 current.

---

**End of Agent Assignments — Feature #183**
