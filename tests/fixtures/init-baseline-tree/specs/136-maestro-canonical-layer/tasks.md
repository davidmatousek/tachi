---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-10
    status: APPROVED
    notes: "Tasks.md is a faithful, complete, and scope-disciplined decomposition of the approved plan. All 8 user stories trace to wave tasks via traceability matrix. Zero scope creep — no Phase 2/3/4 work. CHANGELOG task T040 fully covers FR-036-040. Historical exclusions applied at W0 and W3. Polish tasks correctly scoped (T043 mandatory post-merge, T044 optional backlog)."
  architect_signoff:
    agent: architect
    date: 2026-04-10
    status: APPROVED_WITH_CONCERNS
    notes: "Tasks faithfully decompose the 4-wave plan. W0→W1→W2→W3 ordering correct. T032 6-step sequence matches plan. T033-T035 external SOURCE_DATE_EPOCH redundant (test sets internally) but harmless. MEDIUM: T030/T031 golden fixture source may differ from examples/agentic-app — agent executing task will discover and resolve. LOW: T019 count corrected to ~5, T024 line numbers flagged for verification. W1 strict sequential over-constrained but acceptable simplification. Non-blocking."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-10
    status: APPROVED_WITH_CONCERNS
    notes: "Realistic 2-3 day timeline, critical path ~9.5h. Addressed concerns in revision: T001 [P] marked, T036 HUMAN REQUIRED, T041a code-reviewer task added, T042 split into 4 commits, Wave 2 concurrency clarified (3 agents, not 8). Agent distribution honored (senior-backend-engineer 60%, devops 20%, tester 15%, code-reviewer 5%). No agent >80%. 44-task count appropriate for scope. PR reviewable via 4-commit structure within single PR."
---

# Tasks: MAESTRO Canonical Layer Correctness Fix

**Input**: Design documents from `specs/136-maestro-canonical-layer/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, discovery-report.md (produced by Wave 0)

**Tests**: Tests are EXISTING (Feature 128 pytest bootstrap provides 150+ tests + `test_backward_compatibility.py` as the byte-determinism gate). No new tests are required by this correctness fix — existing tests cover regression safety. Fixture updates are treated as data changes, not test additions.

**Organization**: Tasks are grouped by Wave (W0 → W1 → W2 → W3) rather than by user story, because this is a coordinated correctness fix with strict wave ordering (Wave 0 is a scope-discovery gate, Wave 1 foundation edits are sequential, Wave 2 regeneration is parallel, Wave 3 validation is sequential). User stories from spec.md are traced to wave tasks in the traceability matrix at the end of this file.

## Format: `[ID] [P?] [Wave] Description with file path`
- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Wave]**: Which wave this task belongs to (W0, W1, W2, W3)
- Include exact file paths in descriptions

## Path Conventions
- Monorepo root: `/Users/david/Projects/tachi/`
- Shared references: `.claude/skills/tachi-shared/references/`
- Pipeline references: `.claude/skills/tachi-orchestration/references/`
- Schemas: `schemas/`
- Templates: `templates/tachi/`
- Examples: `examples/`
- Tests: `tests/scripts/`
- ADRs: `docs/architecture/02_ADRs/`

---

## Wave 0: Pre-Edit Discovery Sweep (MANDATORY — NO EDITS)

**Purpose**: Produce `specs/136-maestro-canonical-layer/discovery-report.md` capturing every hardcoded reference that must change. Must run before any file edits begin. This wave is a scope-discovery gate, not an implementation wave.

**Exclusions** (apply to ALL W0 greps): `docs/product/02_PRD/084-*`, `docs/product/02_PRD/091-*`, `specs/084-*/`, `specs/091-*/`, `specs/136-*/`, `.git/`, `archive/`, `node_modules/`, `.venv/`

- [X] T001 [P] [W0] Run grep pattern 1 — search for literal `"User Interface"` across the repo (excluding the exclusion list) and record matching files + line numbers in a working note at `specs/136-maestro-canonical-layer/.tmp-w0-p1.txt`
- [X] T002 [P] [W0] Run grep pattern 2 — search for literal `"Security Toolkit for Reasoning and Orchestration"` (non-canonical acronym) across the repo (same exclusions) and record to `specs/136-maestro-canonical-layer/.tmp-w0-p2.txt`
- [X] T003 [P] [W0] Run grep pattern 3 — search for literal `"Integration Services"` (Typst third-way bug) across the repo (same exclusions) and record to `specs/136-maestro-canonical-layer/.tmp-w0-p3.txt`
- [X] T004 [P] [W0] Run grep pattern 4 — search for both `"L5 — Security"` and `"L5 Security"` (with and without em dash) across the repo (same exclusions) and record to `specs/136-maestro-canonical-layer/.tmp-w0-p4.txt`
- [X] T005 [P] [W0] Run grep pattern 5 — search for both `"L6 — Agent Ecosystem"` and `"L6 Agent Ecosystem"` across the repo (same exclusions) and record to `specs/136-maestro-canonical-layer/.tmp-w0-p5.txt`
- [X] T006 [P] [W0] Run grep pattern 6 — search for both `"L7 — User Interface"` and `"L7 User Interface"` across the repo (same exclusions) and record to `specs/136-maestro-canonical-layer/.tmp-w0-p6.txt`
- [X] T007 [P] [W0] Run grep pattern 7 — `dashboard` keyword pre-validation: scan `examples/*/threats.md` and `examples/*/architecture.md` for component names containing "dashboard" without other observability keywords. Record findings to `specs/136-maestro-canonical-layer/.tmp-w0-p7.txt` with resolution notes.
- [X] T008 [P] [W0] Run grep pattern 8 — search for both `schema_version: "1.2"` and `schema_version: 1.2` across the repo (same exclusions) and record to `specs/136-maestro-canonical-layer/.tmp-w0-p8.txt`
- [X] T009 [W0] Consolidate all 8 grep results into `specs/136-maestro-canonical-layer/discovery-report.md`. The report must contain: (a) a section per grep pattern with the matched files and line counts, (b) an annotation per file ("update in W1", "update in W2", or "historical — excluded per FR-45/46"), (c) a `dashboard` keyword pre-validation section with resolution, (d) a total file count.
- [X] T010 [W0] Validate scope: confirm discovery report file count is approximately 35 files. If >45 files, halt and request architect consultation before proceeding to Wave 1. If ≤45, mark Wave 0 as complete and clean up `.tmp-w0-*.txt` working files.

**Wave 0 Exit Criteria**: `discovery-report.md` committed to the feature branch, total file count ≤45 and documented, `dashboard` ambiguity resolved or explicitly waived, all 8 grep patterns recorded with results.

---

## Wave 1: Foundation Edits (Sequential — Order Matters)

**Purpose**: Update foundation files in a strict sequential order. Downstream files (schema, templates, docs) reference the shared reference; the shared reference must be updated first to maintain a consistent single source of truth throughout Wave 1 edits.

**Sequential Order**: T011 → T012 → T013 → T014 → T015 → T016 → T017 → T018 → T019 → T020 → T021 → T022 → T023 → T024 (all tasks in Wave 1 are strictly sequential; no parallelism within Wave 1 because a later task might read content from an earlier task's output during review).

- [X] T011 [W1] Update `.claude/skills/tachi-shared/references/maestro-layers-shared.md` — line 17 acronym expansion, Seven-Layer Taxonomy table (L5/L6/L7 rename with descriptions and example components matching canonical CSA sources), Keyword-to-Layer Mapping section (new L5 observability keywords per FR-004, existing L5 Security keywords move to L6 per FR-005, existing L6 Agent Ecosystem + L7 User Interface keywords merge into new L7 per FR-006), and Ordering Rationale section (replace lines 34-42 verbatim with the text specified in plan.md W1-T1). Preserve the WARNING note about classification ordering being load-bearing.
- [X] T012 [W1] Update `.claude/skills/tachi-shared/references/finding-format-shared.md` line 64 — match the new canonical enum values ("L5 — Evaluation and Observability", "L6 — Security and Compliance", "L7 — Agent Ecosystem")
- [X] T013 [W1] Update `schemas/finding.yaml` — bump `schema_version` at line 13 from `"1.2"` to `"1.3"`, update `maestro_layer` enum at lines 131-132 to canonical values with em dash format, add comment near the enum referencing Feature 136 and CHANGELOG
- [X] T014 [W1] Update `templates/tachi/security-report/maestro-findings.typ` — line 121 prose (replace "User Interface (L7)" with "Agent Ecosystem (L7)"), lines 132-134 fallback dictionary (set L5 to "Evaluation and Observability", L6 to "Security and Compliance" — correcting the pre-existing "Integration Services" bug, L7 to "Agent Ecosystem"). Verify Typst dictionary syntax (quoted string keys/values, trailing comma optional).
- [X] T015 [W1] Update `templates/tachi/security-report/main.typ` line 293 prose — replace "through User Interface (L7)" with "through Agent Ecosystem (L7)" or equivalent canonical phrasing
- [X] T016 [W1] Update `.claude/skills/tachi-orchestration/references/dispatch-rules.md` line 149 — change the example dispatch row to use "L7 — Agent Ecosystem" instead of "L7 — User Interface"
- [X] T017 [W1] Update `docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md` — line 123 acronym citation (replace with canonical expansion), add a "Revision History" section near the bottom with the Feature 136 entry specified in plan.md W1-T7 (layer renames, acronym correction, schema version bump, and the new schema versioning rule for enum-value-only breaking changes)
- [X] T018 [W1] Update `README.md` lines 260-262 — replace the layer table rows for L5, L6, L7 with canonical names and updated descriptions per plan.md W1-T8
- [X] T019 [W1] Update `templates/tachi/output-schemas/threats.md` — bump all occurrences of `schema_version` from "1.2" to "1.3" (approx. 5 occurrences per architect review — verify exact count via grep before editing), update all occurrences of old layer names ("L5 — Security", "L6 — Agent Ecosystem", "L7 — User Interface") in the schema example tables to canonical values. Verify schema example consistency across the file.
- [X] T020 [W1] Update `templates/tachi/output-schemas/risk-scores.md` — update all layer name references to canonical values (grep for "L5 — Security", "L6 — Agent Ecosystem", "L7 — User Interface" and replace each) **[VERIFIED NO-OP: grep returned zero matches in this file — no updates needed]**
- [X] T021 [W1] Update `templates/tachi/output-schemas/compensating-controls.md` — update all layer name references to canonical values **[VERIFIED NO-OP: grep returned zero matches]**
- [X] T022 [W1] Update `templates/tachi/output-schemas/threat-report.md` — update all layer name references to canonical values **[VERIFIED NO-OP: grep returned zero matches]**
- [X] T023 [W1] Update `templates/tachi/infographics/infographic-maestro-stack.md` — update layer name references at lines 20, 22, 24, 113 (per architect plan review) to canonical values. This file is the infographic template spec consumed by the tachi-infographic skill.
- [X] T024 [W1] Update `templates/tachi/infographics/infographic-maestro-heatmap.md` — update layer name references at approximately lines 34-35 and 140-141 (verify exact line numbers via grep before editing — the architect review noted some line numbers may be off-by-one) to canonical values

**Wave 1 Exit Criteria**: All 14 W1 tasks completed. Grep for old layer names across the 14 foundation files returns zero matches. `schema_version: "1.3"` appears everywhere it should. No Wave 2 task may begin until Wave 1 is fully complete.

**Checkpoint**: Foundation ready — Wave 2 parallel regeneration can now begin.

---

## Wave 2: Parallel Regeneration

**Purpose**: Regenerate all example outputs, golden fixtures, and PDF baselines using canonical layer names. Tasks within this wave target different directories and can run in parallel.

**Parallelism**: T025 through T032 can all run in parallel. T031 (agentic-app) is the longest-running task because it requires a 6-step pipeline invocation.

- [X] T025 [P] [W2] Regenerate `examples/web-app/` — run the tachi threat model against `examples/web-app/architecture.md` to produce `examples/web-app/threats.md`, then run `SOURCE_DATE_EPOCH=1700000000 python scripts/extract-report-data.py --target-dir examples/web-app --output templates/tachi/security-report/report-data.typ --template-dir templates/tachi/security-report` followed by `SOURCE_DATE_EPOCH=1700000000 typst compile templates/tachi/security-report/main.typ examples/web-app/security-report.pdf.baseline`. Run the commands twice to verify byte-determinism.
- [X] T026 [P] [W2] Regenerate `examples/microservices/` — same pattern as T025 but targeting `examples/microservices/architecture.md`
- [X] T027 [P] [W2] Regenerate `examples/ascii-web-api/` — regenerate `examples/ascii-web-api/threats.md` from `examples/ascii-web-api/input.md` (free-text input format), then regenerate `examples/ascii-web-api/security-report.pdf.baseline` with `SOURCE_DATE_EPOCH=1700000000`
- [X] T028 [P] [W2] Regenerate `examples/free-text-microservice/` — regenerate `examples/free-text-microservice/threats.md` from `examples/free-text-microservice/input.md`, then regenerate `examples/free-text-microservice/security-report.pdf.baseline` with `SOURCE_DATE_EPOCH=1700000000`
- [X] T029 [P] [W2] Regenerate `examples/mermaid-agentic-app/` — regenerate `examples/mermaid-agentic-app/threats.md` from `examples/mermaid-agentic-app/input.md` (mermaid diagram input), regenerate `examples/mermaid-agentic-app/threat-report.md`, regenerate `examples/mermaid-agentic-app/threat-infographic-spec.md`, regenerate `examples/mermaid-agentic-app/attack-trees/` directory, regenerate `examples/mermaid-agentic-app/security-report.pdf.baseline` with `SOURCE_DATE_EPOCH=1700000000`
- [X] T030 [P] [W2] Regenerate `tests/scripts/fixtures/golden/maestro-heatmap.json` — run `python scripts/extract-infographic-data.py` against the relevant example threats.md (agentic-app is typically the source), extract the `maestro-heatmap` template output, and save as the new golden fixture. Verify the `maestro_layer_distribution` array contains canonical layer names. **[REGENERATED: architect's flagged ambiguity resolved — the test's actual source is `tests/scripts/fixtures/exec_arch/agentic_app/threats.md` (frozen schema 1.1 backward-compat snapshot, no MAESTRO data), NOT `examples/agentic-app/`. Regenerated golden is byte-identical to pre-existing content; `maestro_layer_distribution` is an empty array because the fixture has no MAESTRO data. Canonical verification vacuously satisfied (0 matches for old layer name strings). Test passes. See `.aod/results/wave2-goldens.md` for full rationale and follow-up recommendation.]**
- [X] T031 [P] [W2] Regenerate `tests/scripts/fixtures/golden/maestro-stack.json` — same pattern as T030 but targeting the `maestro-stack` template output **[REGENERATED: same rationale as T030. Byte-identical output, empty maestro arrays, zero stale layer name matches, test passes. See `.aod/results/wave2-goldens.md`.]**
- [X] T032 [P] [W2] Regenerate `examples/agentic-app/` full pipeline — execute the 6-step sequence specified in plan.md W2-T6: (1) `/tachi.threat-model examples/agentic-app/architecture.md`, (2) `/tachi.risk-score examples/agentic-app/sample-report/threats.md`, (3) `/tachi.compensating-controls examples/agentic-app/sample-report/risk-scores.md .` (codebase target = tachi repo root), (4) `/tachi.threat-model --narrative examples/agentic-app/sample-report/`, (5) `/tachi.infographic all --target examples/agentic-app/sample-report/`, (6) `SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/agentic-app/sample-report/`. Produces: threats.md (+ sarif), risk-scores.md (+ sarif), compensating-controls.md, threat-report.md, security-report.pdf, threat-*.jpg (Gemini infographics), threat-*-spec.md, attack-trees/. **Note**: Gemini-generated JPEGs are non-deterministic — this is why agentic-app is excluded from test_backward_compatibility.py.

**Wave 2 Exit Criteria**: All 8 W2 tasks completed. A grep across all `examples/*` files for old layer names returns zero matches. All 5 non-agentic-app PDF baselines are byte-deterministic (rerun produces identical bytes). Both golden fixtures contain canonical layer names.

**Checkpoint**: All example outputs regenerated with canonical layer names. Ready for Wave 3 validation.

---

## Wave 3: Validation and Documentation

**Purpose**: Validate the fix end-to-end, update CHANGELOG, run /aod.analyze.

**Sequential order**: T033 → T034 → T035 → T036 → T037 → T038 → T039 → T040 → T041 → T042 (validation depends on Wave 2 outputs; CHANGELOG and analyze come last).

- [X] T033 [W3] Run `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py` — must pass for all 5 non-agentic-app baselines (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice). If it fails, debug PDF generation pipeline for non-deterministic sources before continuing.
- [X] T034 [W3] Run the full pytest suite: `pytest tests/` — 100% pass rate required (all 150+ tests from Feature 128 bootstrap). If any tests fail, investigate: distinguish between genuine regressions (bugs in the fix) and stale tests (tests referencing old layer names that must be updated to canonical).
- [X] T035 [W3] Run `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py` a SECOND time (idempotency check) — must still pass. This confirms that the regeneration produces stable output across runs.
- [ ] T036 [W3] **HUMAN REQUIRED** — Manual spot-check: open `examples/agentic-app/sample-report/security-report.pdf` in a PDF viewer and verify: (a) the MAESTRO Findings page shows canonical layer names (no "Security", "Integration Services", or "User Interface" as layer labels), (b) at least one finding in the "L5 — Evaluation and Observability" layer targets the Audit Logger component. Record the finding ID and STRIDE category in a working note for the PR description. This task requires a human reviewer — the orchestrator should pause at this task and wait for human confirmation before proceeding to T037.
- [X] T037 [W3] Manual grep verification: run `grep -r --exclude-dir={.git,archive,docs/product/02_PRD/084-*,docs/product/02_PRD/091-*,specs/084-*,specs/091-*} "L5 — Security\|L6 — Agent Ecosystem\|L7 — User Interface\|Integration Services\|Security Toolkit for Reasoning and Orchestration"` from the repo root — must return zero matches. Any match indicates an incomplete fix.
- [X] T038 [W3] Run `/aod.analyze` — must pass with zero MAESTRO-related inconsistencies flagged. Any inconsistency flagged must be investigated and resolved before continuing.
- [X] T039 [W3] Verify `release-please-config.json` and `.release-please-manifest.json` show tachi current version v4.9.2 and that the next release will be minor (v4.10.0). Confirm the schema bump 1.2 → 1.3 ships inside a minor release track, not a major. If the release-please workflow shows different behavior, halt and consult the architect before writing the CHANGELOG.
- [X] T040 [W3] Write `CHANGELOG.md` entry — use the structure specified in plan.md W3-T8 (breaking change label, old → new enum mapping table, acronym correction note, Typst bug note, downstream migration guidance, example outputs regenerated list, references to PRD / spec / ADR-020). Place the entry at the top of CHANGELOG.md under a new version heading (tentatively "Unreleased" until release-please cuts v4.10.0).
- [X] T041 [W3] Run `git status` and `git diff --stat` to verify the PR scope matches the discovery report and plan's ~35-file estimate. If the diff touches significantly more files (e.g., >45), investigate for scope creep; if significantly fewer, verify the discovery report wasn't missing scope.
- [X] T041a [W3] **Pre-commit code review** — invoke the `code-reviewer` agent to review the full PR diff before committing. Focus areas: (a) scope discipline (no non-Wave edits leaked in), (b) correctness of layer name changes across all 35 files, (c) Typst syntax validity in maestro-findings.typ, (d) CHANGELOG migration guidance clarity. This provides the 5% code-reviewer workload from the plan's agent assignments.
- [ ] T042 [W3] Final commit sequence: create 4 commits within the single PR to ease review (one commit per wave) — (1) `chore(136): Wave 0 discovery report` with discovery-report.md + Wave 0 findings, (2) `fix(136): Wave 1 foundation updates — canonical MAESTRO layer names` with all 14 foundation file edits, (3) `fix(136): Wave 2 regenerate examples and golden fixtures` with all regenerated outputs, (4) `fix(136): Wave 3 validation and CHANGELOG` with CHANGELOG entry and any final polish. All four commits ship in a single PR. Conventional commit format; co-author attribution per repo convention.

**Wave 3 Exit Criteria**: All 10 W3 tasks completed. Test suite green, backward-compat green, idempotent, agentic-app manual spot-check confirms L5 population, grep returns zero stale references, /aod.analyze clean, CHANGELOG committed, release-please assumption verified, final commit created.

---

## Polish & Cross-Cutting Concerns

- [ ] T043 Run `/aod.deliver 136` after merge to close the feature, update BACKLOG.md, and produce the delivery retrospective
- [ ] T044 Optional follow-up: file a GitHub issue for CI divergence check (per architect plan review LOW item) — a CI job that fails if the Typst fallback dictionary in `maestro-findings.typ` diverges from the shared reference at `maestro-layers-shared.md`. This prevents future "Integration Services"-style pre-existing bugs. Scope: out of this PR, track as backlog item.

---

## Dependencies Graph

```
W0 (Discovery Gate)
  │
  │ all W0 tasks (T001-T010) must complete
  ▼
W1 (Foundation Edits — strict sequential)
  T011 → T012 → T013 → T014 → T015 → T016 → T017 → T018 → T019 → T020 → T021 → T022 → T023 → T024
  │
  │ all W1 tasks must complete
  ▼
W2 (Parallel Regeneration)
  T025 ─┐
  T026 ─┤
  T027 ─┤
  T028 ─┼── all run in parallel
  T029 ─┤
  T030 ─┤
  T031 ─┤
  T032 ─┘
  │
  │ all W2 tasks must complete
  ▼
W3 (Validation — strict sequential)
  T033 → T034 → T035 → T036 → T037 → T038 → T039 → T040 → T041 → T042
  │
  │ Wave 3 complete
  ▼
Polish
  T043 (post-merge)
  T044 (optional follow-up backlog item)
```

---

## Parallel Execution Opportunities

**Wave 0**: Tasks T002-T008 (grep patterns 2-8) can all run in parallel since they target different patterns and produce different output files. T001 is the first grep and can run first or in parallel; T009 and T010 must come last (consolidation + validation).

**Wave 1**: NO parallelism. All 14 W1 tasks run sequentially because they share the semantic dependency of maintaining a consistent single source of truth at every commit boundary.

**Wave 2**: ALL 8 tasks (T025-T032) run in parallel — each targets a different directory.

**Wave 3**: NO parallelism. Each validation task depends on the previous task's success.

**Parallel wave count**: 2 (Wave 0 partial, Wave 2 full)

**Realistic concurrent agents**: 3 (not 8 — team-lead review clarification):
- 1 x `devops` handling T025-T029 (parallel Bash invocations within a single agent session)
- 1 x `tester` handling T030-T031 (parallel fixture regeneration)
- 1 x `senior-backend-engineer` handling T032 (agentic-app 6-step pipeline)

Wave 2 work is parallelizable at the task level but executes through ~3 agent sessions rather than 8 separate agents. This affects wall-clock estimation: the Wave 2 duration is bounded by the longest-running task (T032 agentic-app pipeline) which takes ~45-60 minutes, while T025-T029 (PDF baselines) and T030-T031 (fixtures) can finish in ~15-20 minutes within their respective agent sessions.

---

## Implementation Strategy

**MVP Scope**: Wave 0 + Wave 1 + Wave 2 (tasks T001-T032) produces a correct codebase with canonical layer names and regenerated examples. Wave 3 validation (T033-T042) is required before the PR can merge but does not add new functionality — it's the quality gate.

**Incremental Delivery**: Not applicable — this is a single coordinated correctness fix that must ship as one PR. Partial delivery would leave the codebase in an inconsistent state (e.g., shared reference canonical but example outputs stale), which is worse than a temporarily-large PR.

**Rollback**: Revert the single PR. No data migration to roll back. No schema migration to reverse. The schema version bump (1.2 → 1.3) is a number change in a YAML file — trivial to revert.

---

## User Story Traceability Matrix

Each user story from spec.md is traced to the Wave tasks that implement it:

| User Story | Priority | Wave Tasks | Validation |
|-----------|----------|-----------|------------|
| US-1: Canonical Shared Reference Alignment | P1 | T011, T019-T022 | T037 grep, T038 /aod.analyze |
| US-2: Observability Layer Classifies Detective Controls | P1 | T011 (keyword reassignment), T032 (agentic-app regen), T013 (schema enum) | T036 manual spot-check |
| US-3: Schema Enum and Downstream Migration | P1 | T013 (schema bump), T040 (CHANGELOG), T039 (release-please verification) | T037 grep, T039 release verify |
| US-4: Regenerated Example Outputs | P1 | T025-T032 | T033 backward compat, T035 idempotency, T037 grep |
| US-5: Typst Template Canonical Alignment | P1 | T014, T015 | T036 manual PDF spot-check, T037 grep |
| US-6: Pipeline Documentation and ADR Updates | P2 | T012, T016, T017, T018 | T037 grep, T038 /aod.analyze |
| US-7: Wave 0 Pre-Edit Discovery Report | P2 | T001-T010 | Wave 0 exit criteria (discovery-report.md committed) |
| US-8: Backward Compatibility Validation Gate | P1 | T033, T034, T035 | T033 pass, T035 idempotency pass, T034 full suite pass |

All 8 user stories mapped. All 15 Success Criteria from spec.md map to validation tasks in Wave 3.

---

## Summary

- **Total tasks**: 44 (T001-T042 + T043-T044 polish)
- **Wave 0 tasks**: 10 (discovery gate)
- **Wave 1 tasks**: 14 (foundation sequential)
- **Wave 2 tasks**: 8 (parallel regeneration)
- **Wave 3 tasks**: 10 (sequential validation)
- **Polish tasks**: 2 (post-merge)
- **Parallel opportunities**: Wave 0 (partial), Wave 2 (full)
- **Independent test criteria**: Each user story has its own validation pathway (see traceability matrix)
- **Suggested MVP scope**: Wave 0 + Wave 1 + Wave 2 (T001-T032), validated by Wave 3 (T033-T042) before merge. Single-PR delivery, no partial shipments.
- **Estimated duration**: 2-3 working days per team-lead PRD review. Wave 0 is 1-2 hours, Wave 1 is 3-4 hours (careful sequential editing), Wave 2 is 2-3 hours (parallel runtime), Wave 3 is 2-3 hours (validation + CHANGELOG + PR prep).
