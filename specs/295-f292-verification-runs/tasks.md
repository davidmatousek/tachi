---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-07-03
    status: APPROVED
    notes: "All 21 FRs trace to concrete tasks; three stories with goal/independent-test/checkpoint; zero scope creep (T020 fence, T016 files-not-builds, US3 purpose-built); #295 closure reachable with honest-failure paths intact; MVP framing correct. 2 non-blocking advisories. Details: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-07-03
    status: APPROVED_WITH_CONCERNS
    notes: "0H/0M/3L. Ordering, contract fidelity (D-1 gate fields incl. logicalLocations[].name, 6-path anchor), and pattern fidelity (importlib, ADR-046 tier, L-a semantics) all verify clean. L-1 (T014 explicit regen-mismatch disposition), L-2 (T020 content-diff fence), L-3 (count-pin co-update) — all three folded into tasks post-review. Details: .aod/results/architect.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-07-03
    status: APPROVED_WITH_CONCERNS
    notes: "0H/0M/4L. Task graph realizes the 1-serial-wave plan; 20 tasks right-sized; M-1/M-2 folded beyond ask; US-3 BASELINE_EXAMPLES→purpose-built supersession ACCEPTED; 0.5/1.0/2.0 estimate holds (L-1: bounded adds consume snag buffer — steeper central→ceiling glide). Veto not exercised. Details: .aod/results/team-lead.md"
---

# Tasks: F-292 Post-Merge Verification Runs (T017 + T026)

**Input**: Design documents from `/specs/295-f292-verification-runs/`
**Prerequisites**: plan.md (dual-APPROVED 2026-07-03), spec.md (PM APPROVED), research.md (D-A..D-E), data-model.md, contracts/ (2), quickstart.md
**Feature**: #295 | **Draft PR**: #353 | **Estimate**: 0.5/1.0/2.0 eng-days (Team-Lead feasibility)

**Tests**: US-3 IS a test deliverable (spec FR-015/FR-016); FR-014 ships with its covering assertion (spec requirement). No other test tasks — live-run ACs are `[MANUAL-ONLY]`.

**Organization**: Tasks grouped by user story. **SERIAL EXECUTION IS MANDATORY** (FR-021): US1 → US2 → US3; no concurrent tachi pipeline runs (shared orchestrator context). The template's parallel-team strategy does NOT apply — Team-Lead wave plan is 1 serial wave, roster of 2 (security-analyst LEAD, tester).

> **Definition of Done** (canonical bar = constitution VII):
> 1. ✅ Pushed to Production — feature deployed and operational.
> 2. ✅ Tested — all automated tests pass (unit, integration, E2E, performance)
> 3. ✅ User Validated — real-world usage confirmed by actual users/stakeholders.

<!-- DOD-ACK -->

> **Naming collision note**: "F-292 T017/T026" in descriptions refer to the *historic* deferred tasks from `specs/292-*/tasks.md` (this feature's subject matter). Task IDs T001–T020 below are THIS feature's tasks — this file's own T017 is unrelated to F-292's T017.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies) — deliberately sparse (feasibility L-3: serial chain)
- **[Story]**: US1 (F-292 T017/SC-003), US2 (F-292 T026/SC-015), US3 (regen check)
- Fail-closed rule for every gate task: empty extraction / missing artifact / tool exception = ERROR-stop, never a pass (contracts/oi-extraction-contract.md §2, regen contract §1.4)

## Phase 1: Setup

**Purpose**: Precondition sanity — verify the pre-verified facts still hold at execution time

- [X] T001 Verify preconditions: `git show 0629fa2~1:examples/agentic-app/sample-report/threats.sarif` piped through the corrected filter yields exactly 4 findingIds (OI-1..OI-4); `jq`, `pytest>=8` available; branch `295-f292-verification-runs` current with origin. Record outputs for the SC-003 record preamble. (quickstart.md Stage 1.1)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: FR-019 pre-state — BLOCKS every subsequent commit (KB Entry 15 inherited-vs-own discipline)

- [X] T002 Run the D-E pre-state suite set and commit `specs/295-f292-verification-runs/test-results/pre-state.md` with literal pass/skip/fail totals (`test_backward_compatibility.py` incl. slow, maestro pair, `test_catalog_drift_guard.py`, `test_affected_assets_wiring.py`), the `examples/**` corpus-glob/count-pin sweep results, and dispositions for any inherited reds (quickstart.md Stage 0)

**Checkpoint**: pre-state committed — artifact/enabler commits may now proceed

---

## Phase 3: User Story 1 — F-292 T017 / SC-003 OI no-emission verification (Priority: P0) MVP

**Goal**: Empirically verify the F-292 cross-link prose added no OI emissions on `examples/agentic-app/`, with the corrected (working) extraction procedure, committed evidence, and pre-decided failure dispositions.

**Independent Test**: `sc-003-verification-record.md` committed with non-empty 4-findingId extractions both sides, D-1 gate verdict, full attribution table; #295 T017 checkbox checked; contract dual-defect Issue filed.

**Owner**: security-analyst (LEAD) | Attempt cap: 2 live runs, then M-1 escape hatch (file tooling defect, close on staged-partial record)

- [X] T003 [US1] Extract anchor OI subset: `git show 0629fa2~1:...threats.sarif` → corrected filter → `specs/295-f292-verification-runs/test-results/anchor-oi-subset.json`; false-pass guard: non-empty AND cardinality exactly 4, else gate ERROR-stop (contracts/oi-extraction-contract.md §2)
- [X] T004 [US1] Fresh run (primary path): dispatch `tachi-output-integrity` single-agent with orchestrator-shaped context (component set + full `examples/agentic-app/architecture.md` + OI analysis scope); persist raw YAML verbatim to `specs/295-f292-verification-runs/test-results/t017-fresh-findings.yaml`. Fallback (attempt 2 only): scoped-full run with `report: false`, use its native `threats.sarif` (plan D-A)
- [X] T005 [P] [US1] Author assembler tool `specs/295-f292-verification-runs/tools/assemble_oi_sarif.py`: YAML finding blocks → comparison SARIF reusing `scripts/sarif_common.py::build_sarif_envelope` (+ `generate-threats-sarif.py::build_result` where mapping is clean) via importlib (`tests/scripts/test_affected_assets_wiring.py:520-536` pattern); MUST emit `partialFingerprints["findingId/v1"]`, `locations[].logicalLocations[].name`, `message.text` per finding (parallel-safe: depends only on schema shape, not T004 output)
- [X] T006 [US1] Assemble `test-results/fresh-oi.sarif` from T004 YAML via T005 tool; corrected-filter extraction → `test-results/fresh-oi-subset.json`; non-empty guard (expected 4), else ERROR-stop
- [X] T007 [US1] Evaluate D-1 hard gate: count + findingId set (jq-deterministic) + per-finding sink/flow identity table (primary = `logicalLocations[].name`, secondary = quoted flow names; both sides' verbatim text in table); attribute every non-gate delta to a named class (F-260b / F-098-#311 / #184-#186 / assembler-envelope) via bounded `git log -p 0629fa2..HEAD -- <surfaces>` walk; unattributable ⇒ gate FAIL (contracts/oi-extraction-contract.md §4–§5)
- [X] T008 [US1] Commit `specs/295-f292-verification-runs/sc-003-verification-record.md` (ALL required sections per data-model.md entity 3: commands, SHAs, filter, both subsets, identity table, diff, attribution, verdict); link record from Issue #295 and check the F-292 T017 checkbox (`gh issue comment` + edit)
- [X] T009 [US1] File the contract-§3 dual-defect Issue (ALWAYS, FR-008): broken `ruleId` filter + non-executable stdout-JSON invocation, corrected procedure documented, OQ-4 disposition delegated to that Issue; ADDITIONALLY file FR-007 defect Issue with evidence ONLY if T007 verdict = FAIL

**Checkpoint**: US1 independently complete — SC-003 closed on evidence (PASS or honest FAIL)

---

## Phase 4: User Story 2 — F-292 T026 / SC-015 Cat 6 evidence baseline (Priority: P0)

**Goal**: `examples/multi-tenant-rag-app/` honors the README pairing contract: committed 5-artifact set with ≥1 Cat 6 finding, script-regenerable `threats.sarif`, MAESTRO-shape CI gate green.

**Independent Test**: 5 artifacts at example root; `cmp` regen byte-identity passes; ≥1 `OI-*` CWE-943 finding in committed `threats.md`; maestro-coverage workflow green; #295 T026 checkbox checked.

**Owner**: security-analyst (LEAD) | Starts ONLY after Phase 3 concludes (FR-021 serialization) | Attempt cap 2 + staged per-skill fallback

- [X] T010 [US2] URI enabler (FR-014): change `scripts/generate-threats-sarif.py::build_result` (`:481`) to derive `artifactLocation.uri` from the input path; capture L-a proof BEFORE/AFTER: `python3 scripts/generate-threats-sarif.py examples/agentic-app/sample-report/threats.md /tmp/{before,after}.sarif` around the change, `cmp` MUST report identical (script-tier vs script-tier, same input — plan L-a)
- [X] T011 [US2] Same commit as T010 (lock-step, ADR-039 D-6): covering assertion for input-path-derived URI in `tests/scripts/test_affected_assets_wiring.py`; add `scripts/generate-threats-sarif.py` to `.github/workflows/tachi-pytest.yml` `&hardening_paths` anchor; run the module locally green
- [X] T012 [US2] Full pipeline run: `/tachi.threat-model examples/multi-tenant-rag-app/architecture.md --output-dir examples/multi-tenant-rag-app/test-output/` with `SOURCE_DATE_EPOCH=1700000000` exported (convention-uniformity; SARIF determinism structural), Phase 5 ON; on overflow: staged per-skill fallback (`/tachi.risk-score` etc.); record provenance (command, run dir, populator confirmation) for the SC-015 record
- [X] T013 [US2] Cat 6 gate: run-output `threats.md` MUST contain ≥1 `OI-*` finding on the Cat 6 surface (CWE-943 primary; Pinecone `tenant_id`-omission shape per `examples/multi-tenant-rag-app/architecture.md:92`); on zero ⇒ file defect Issue with run evidence, STOP Phase 4 (no baseline commit) and mark US3 deferred to that Issue (FR-018) — **GATE FAIL** (0/0/0 on all three checks); Cat 6 surface detected but compiled as `LLM-10`/`LLM-11` (missing `OI-` prefix + CWE-943); defect Issue #356 filed with full evidence; Phase 4 stopped, no baseline commit; US-3 deferred to #356 per FR-018. See `sc-015-verification-record.md`.
- [DEFER #356] T014 [US2] Copy exactly `threats.md threat-report.md risk-scores.md risk-scores.sarif` from the timestamped run dir to `examples/multi-tenant-rag-app/` root; generate `threats.sarif` via the URI-corrected generator; verify: FR-011 regen byte-identity (`cmp` fresh regen vs generated file), FR-012 MAESTRO all-7-row table shape, SARIF `uri` = `examples/multi-tenant-rag-app/threats.md` (quickstart.md Stage 2.3 commands). On regen MISMATCH ⇒ file FR-007 defect Issue with evidence, STOP (no baseline commit; US3 defers per FR-018) — explicit disposition per Architect L-1 — NOT EXECUTED: T013 gate FAIL stopped Phase 4 before the copy/regen step (see sc-015-verification-record.md)
- [X] T015 [US2] Verify `examples/README.md:15` row accuracy (7 components, Cat 6 trigger — FR-013; edit ONLY if evidence contradicts); co-update any `examples/**` count-pinned tests identified by T002's sweep IN THE SAME COMMIT as the artifacts (Architect L-3); commit exactly the 5 artifacts + `specs/295-f292-verification-runs/sc-015-verification-record.md` (provenance, gate outcomes, regen proof); link from #295 and check the F-292 T026 checkbox — **ADAPTED (record-only, T013 gate FAIL disposition)**: no artifacts landed (5-artifact commit N/A), README row confirmed accurate as-is (no edit, nothing changed), no count-pin co-update needed (T002 sweep already found 0 at-risk tests); `sc-015-verification-record.md` committed with full provenance + gate evidence + disposition; #295 linked, F-292 T026 checkbox checked (disposition-complete, gate FAIL honestly recorded)
- [X] T016 [P] [US2] File `generate-risk-scores-sarif.py` parameterization enhancement Issue (ALWAYS, FR-011: no CLI, hardcoded paths `:38-42`, `>=80` gate `:535` — out-of-scope generator work) — Issue #357 filed

**Checkpoint**: US2 independently complete — SC-015 clauses a+b closed on evidence (or honest defect-filed stop)

---

## Phase 5: User Story 3 — Durable SARIF-regen byte-identity check (Priority: P1)

**Goal**: SC-015 clause b becomes CI-enforced instead of a one-time claim.

**Independent Test**: new module green locally + in the dedicated workflow; lock-step paths verified; PR body carries the coverage-boundary statement.

**Owner**: tester (alt: senior-backend-engineer for the Python edit) | **STRUCTURAL GATE (FR-018)**: proceed ONLY if T014's regen byte-identity passed; on T013/T014 failure this phase defers to the defect Issue WITHOUT counting as a US3 failure

> **GATE OUTCOME (2026-07-03)**: T013 Cat 6 gate FAILED (orchestrator compilation dropped the OI- prefix carve-out + CWE-943 — Issue #356). Phase 4 stopped before T014; this phase is DEFERRED to #356 per FR-018 — not a US3 failure. See sc-015-verification-record.md.

- [DEFER #356] T017 [US3] Author `tests/scripts/test_sarif_regen_identity.py` per contracts/regen-byte-identity-contract.md §1: importlib-load generator, regen from committed `examples/multi-tenant-rag-app/threats.md`, `read_bytes()` equality vs committed `threats.sarif`; fail-closed (missing file / zero findings / exception ⇒ FAIL, never skip); NO `SOURCE_DATE_EPOCH` dependency or claim; local run green
- [DEFER #356] T018 [US3] Same commit as T017 (lock-step): author `.github/workflows/tachi-sarif-regen.yml` per contract §3 — single `ubuntu-latest`, `permissions: contents: read`, PR + `push:[main]` via ONE shared paths anchor containing exactly the 6 listed paths, direct pytest invocation of the new module
- [DEFER #356] T019 [P] [US3] Update draft PR #353 body with the FR-017 coverage-boundary statement (covers: this baseline's SARIF-regen byte-identity; deliberately not: PDF byte-identity, `BASELINE_EXAMPLES` membership, `risk-scores.sarif` regen)

**Checkpoint**: US3 complete — reproducibility claim CI-enforced

---

## Phase 6: Polish & Cross-Cutting

- [X] T020 Closure cross-check: PR CI green (tachi-pytest, maestro-coverage, gitleaks, + tachi-sarif-regen if US3 landed); post-state suite totals vs `test-results/pre-state.md` — every flip attributed (no silent absorption); #295 both F-292 checkboxes checked with record links; all pre-decided Issues filed (contract dual-defect, risk-scores enhancement, + conditional defect/tooling Issues); FR-020 fence audit — `git diff main --stat` shows NO detection-tier / archived-contract edits AND `git diff main -- scripts/generate-threats-sarif.py` content-reviewed to confirm the FR-014 URI derivation is the SOLE generator change (Architect L-2: --stat alone under-covers this clause) — **DONE**: gitleaks + gitleaks-full-repo-scan + tachi-pytest ubuntu-latest all PASS; tachi-pytest macos-latest still queued/pending at write-time (reported honestly, not a failure — see `sc-015-verification-record.md` §T020); maestro-coverage + tachi-sarif-regen correctly did not fire (no `examples/**/threats.md` committed, no sarif-regen workflow file exists); post-state 78/3/0 vs pre-state 74/3/0, sole flip (+4 `test_affected_assets_wiring.py`) attributed to commit `995359f`; #295 both checkboxes confirmed `[x]` with record-links present; Issues #354/#355/#356/#357 all confirmed OPEN with expected subjects; fence audit clean on the named 3 product files + one benign PRD-index self-registration row (flagged, not a violation — see record). Full detail: `.aod/results/security-analyst.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (T001)**: none — start immediately
- **Phase 2 (T002)**: after T001 — BLOCKS all commits (pre-state must predate artifacts in git history)
- **Phase 3 (US1)**: after T002. Internal: T003 → T004 → T006 → T007 → T008 → T009; T005 [P] may run alongside T004 (depends on schema shape only)
- **Phase 4 (US2)**: after Phase 3 CONCLUDES (FR-021 — never concurrent tachi runs). Internal: T010+T011 one commit, before T014's generation step; T012 → T013 → T014 → T015; T016 [P] anytime after T013
- **Phase 5 (US3)**: after T014 regen check PASSES (FR-018 structural gate). Internal: T017+T018 one commit; T019 [P]
- **Phase 6 (T020)**: after all landed phases

### Story Dependency Notes

- US1 and US2 are logically independent (different fixtures) but MUST serialize per FR-021 (shared orchestrator context) — this overrides the template's parallel-team strategy
- US3 structurally depends on US2's committed pair (FR-018); a US2 gate failure re-routes US3 to the follow-up defect Issue, not to failure
- T010/T011 (URI enabler) are P0 and land regardless of T013's gate outcome (enabler ≠ verification-failure fix)

### Parallel Opportunities (deliberately sparse — feasibility L-3)

- T005 (assembler authoring) alongside T004 (live run wall-clock)
- T016 (enhancement Issue) alongside T014/T015
- T019 (PR body) alongside T017/T018

## Implementation Strategy

**MVP = Phase 1–3 (US1)**: SC-003 closed on evidence — half of #295. **Increment 2 = Phase 4 (US2)**: SC-015 evidence baseline — #295 fully closeable. **Increment 3 = Phase 5 (US3)**: durability (defer-able per FR-018 without breaking issue closure). Escape hatches at every live-run task (M-1: 2 attempts → tooling defect + staged-partial record). The deliverable is the verification record — a FAIL outcome with honest evidence still completes the feature (KB Entry 17).
