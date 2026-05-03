---
description: "Task breakdown for Feature 201 — output-integrity threat agent (OWASP LLM05:2025)"
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-18
    status: APPROVED_WITH_CONCERNS
    notes: "Tasks.md faithfully decomposes plan.md into 55 tasks across 9 phases with full coverage — 3 user stories with correct [US#] tagging, 7 PRD FRs, 12 spec SCs (T040-T051 1:1 mapping), all 8 Triad fixes + 3 PM concerns + 5 Architect concerns explicitly annotated in final Notes. Out-of-scope discipline rigorous (F-A3 22-file invariant preserved in T048; infrastructure-tier carve-out; F-2/3/4/5 separation). PM M1 (T030 keyword FP check), M2 (T010 D2 Outcome A counter-argument), M3 (T020 server/client-side predicate) all present and actionable. Architect M1/M2/L1/L2/L3 all absorbed. Timeline fits PRD Outcome B 2-day envelope with 2026-04-23 Thursday buffer; Outcome A path explicit. 0 BLOCKING / 0 HIGH / 2 MEDIUM / 2 LOW — all refinement-level. Full review at .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-04-18
    status: APPROVED_WITH_CONCERNS
    notes: "Tasks.md faithfully translates plan.md into a 9-phase, 55-task breakdown across 6 waves with correct dependency ordering (Wave 1.1→2→3→4→5 gates), parallel [P] markers on independent-file tasks, and wave-gate checkpoints. All 5 architect concerns absorbed: M1 (T010 D8 regex-extension codification), M2 (T012 mermaid pre-check), L1 (T010 D1-D8 enumeration), L2 (T011 ADR-020 cross-ref), L3 (T011 ADR-022 cross-ref). Test-first discipline honored (T005 regex test before T006 schema bump); T006 atomic (version + regex same commit); ADR-030 dual-commit lifecycle correctly sequenced (T010 Proposed → T022 Accepted → T025 post-merge SHA fill). ADR-023 conformance (T016/T018/T029/T048) and F-A2 source_attribution contract (T014 CWE mapping, T037 validate_source_attribution, T043-T046 SC traceability) correctly bound. Orchestrator-tier carve-out (T026/T027) correctly framed as additive edits outside 22-file invariant. Backward-compat gate chain (T012→T031→T038→TL-H1) complete. 0 BLOCKING / 0 HIGH / 2 MEDIUM / 2 LOW — all refinement-level, none block /aod.tasks sign-off. Full review at .aod/results/architect.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-18
    status: APPROVED_WITH_CONCERNS
    notes: "Tasks.md faithfully translates plan.md into 55 atomic tasks across 9 phases with calendar-verified day assignments fitting the Outcome B 2-day envelope + Thursday buffer. All 15 PRD/plan predicates (BLOCKING-1/2, HIGH-1/2/3/4, TL-H1/H2, PM M1-3, Architect M1/M2 + L1-3) map to specific task IDs. TL-H2 Day-1-EOD hard gate present at Phase 2 Checkpoint; TL-H1 Outcome A/B envelopes present in Implementation Strategy. Critical path T004→T006→T010→Wave2→Wave3→Wave4→Wave5 correctly sequenced; no cyclic dependencies. Parallelization maxima achieved (5-parallel Wave 1.1, 3-parallel Waves 2/3/4, 12-parallel Wave 5 SC sweep). T025 post-merge SHA fill correctly decoupled from T052 PR open. senior-backend-engineer capacity ~70-80% on Outcome B, consistent with TL-M4 assessment; architect + tester within capacity. 0 BLOCKING / 0 HIGH / 3 MEDIUM / 3 LOW — all refinement-level. Ready for /aod.build. Full review at .aod/results/team-lead.md."
---

# Tasks: `output-integrity` Threat Agent (OWASP LLM05:2025)

**Input**: Design documents from `/specs/201-output-integrity-threat-agent/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/finding-contract.md, quickstart.md
**Branch**: `201-output-integrity-threat-agent`

**Tests**: Regex unit test + fixture-driven `source_attribution` validation test REQUIRED (per SC-010 + SC-012); backward-compat byte-identity is an existing harness (existing `tests/scripts/test_backward_compatibility.py`).

**Organization**: Tasks are grouped into waves matching plan.md's 5-6 wave structure. Wave 1.1 schema-lock + ADR-030 Proposed is the unblock-gate; Wave 2 pattern + agent authoring proceeds after; Wave 3 orchestrator + shared edits; Wave 4 example regeneration; Wave 5 ADR Accepted + PR; Wave 6 buffer.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1 = LLM05 detection, US2 = mitigation guidance, US3 = Heuristic A / ADR-030)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure feature directory and branch are correctly configured. Branch already created at start of `/aod.plan`; directories already scaffolded by setup scripts.

- [X] T001 Verify working directory clean on branch `201-output-integrity-threat-agent` and `specs/201-output-integrity-threat-agent/` contains spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md
- [X] T002 [P] Create directory `.claude/skills/tachi-output-integrity/references/` (companion skill)
- [X] T003 [P] Create directory `tests/scripts/fixtures/output_integrity/` (test fixtures)

---

## Phase 2: Foundational — Wave 1.0 & 1.1 (Blocking Prerequisites)

**Purpose**: Schema-lock commit + ADR-030 Proposed commit unblock parallel Wave 2 pattern authoring. TL-H2 hard escalation gate fires if Heuristic A determination NOT committed by Day 1 EOD.

**CRITICAL**: No user story work can begin until T006 (schema bump) and T010 (ADR-030 Proposed) are committed.

### Wave 1.0 — Architect Heuristic A Ruling (30-60 min, Day 1 AM)

- [X] T004 Architect resolves Q1 Heuristic A outcome (Outcome A subsume / Outcome B split). Plan default: **Outcome B**. Capture ruling in a short decision memo saved at `.aod/results/heuristic-a-decision.md` for traceability.

### Wave 1.1 — Schema Lock + ADR-030 Proposed (parallel, Day 1 AM/PM)

- [X] T005 [P] Write regex unit test at `tests/scripts/test_output_integrity.py` covering: (a) pre-1.6 IDs (`S-1`, `T-1`, `R-1`, `I-1`, `D-1`, `E-1`, `AG-1`, `LLM-1`, `AGP-1`) remain valid, (b) `OI-1`, `OI-10`, `OI-99` match the 1.6 regex, (c) non-matching inputs (`OI1`, `OIA-1`, `oi-1`, empty string) are rejected. Test MUST FAIL at authoring time (before T006 regex bump).
- [X] T006 Modify `schemas/finding.yaml`: line 13 `schema_version: "1.5"` → `"1.6"`; line 18 `id.pattern: "^(S|T|R|I|D|E|AG|LLM|AGP)-\\d+$"` → `"^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\\d+$"`. Verify T005 regex test now passes.
- [X] T007 [P] Author test fixture `tests/scripts/fixtures/output_integrity/valid_oi_finding.yaml` — complete `OI-1` finding with valid `source_attribution` citing `owasp:LLM05` (primary) + `cwe:CWE-79` (related), populated mitigation text, description distinguishing client-side execution.
- [X] T008 [P] Author test fixture `tests/scripts/fixtures/output_integrity/invalid_attribution_finding.yaml` — finding with `source_attribution` citing CWE-73 (absent from F-A1 catalog) to validate that `validate_source_attribution` rejects the finding.
- [X] T009 [P] [US3] Author ADR-030 skeleton at `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md` with **Status: Proposed** (per FR-019 / Q5 / plan Wave 1.1): title block, Context section (BLP-01 Tier 1 framing, asymmetric LLM threat-surface problem statement), Decisions section with 8 numbered decisions (D1-D8 per architect M1 absorption — see T010), Consequences placeholder, Cross-References placeholder, Revision History table with one initial Proposed row, no Layer 2 / commercial framing.
- [X] T010 [US3] Populate ADR-030 Decisions section in `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`: (D1) adopt new `output-integrity` agent for LLM05 closure; (D2) Heuristic A Outcome B — forward-reference F-4 `trust-exploitation` for human-victim signal class (psychology/linguistics primitives scope-distinct from encoding/sanitization primitives; cite GUIDE-threat-coverage-research §11; **include one-sentence counter-argument acknowledging Outcome A's BLP-01 Tier 1 simplification benefit** per PM M2); (D3) lean-agent shape conformance per ADR-023 (single-point load, ≤150 lines, zero MAESTRO); (D4) LLM05 + ML09 bundling documentation-only per BLP-01 §4 (ML09 NOT in `source_attribution`); (D5) 22-file zero-edit invariant preserved with grep-auditable enumeration; (D6) Proposed → Accepted dual-commit pattern per ADR-027/028/029; (D7) post-merge SHA fill recording squash commit; **(D8) extend ADR-026 Complex-Shape Clarifier from enum-field + list-of-RECORD additions to regex-alternation prefix additions** — same additive-compatibility conditions apply (additive, existing IDs remain valid, regex shape unchanged) per architect M1. Commit ADR-030 Proposed at Wave 1.1.
- [X] T011 [US3] Populate ADR-030 Cross-References in `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`: ADR-021 (determinism baseline), ADR-023 (lean-agent pattern — extended with regex-prefix additive rule per D8), ADR-026 (minor-bump rule — extended by D8), ADR-027 (F-A1 taxonomy enum source), ADR-028 (F-A2 `source_attribution` contract — F-1 is first producer), ADR-029 (F-B downstream consumer — `has-source-attribution` fires true on regen), **ADR-020 (MAESTRO classification — F-1 inherits L5 layer assignment from orchestrator Phase 1 per Feature 084 — architect L2)**, **ADR-022 (mmdc hard prerequisite — Wave 4 regenerated PDF depends on this — architect L3)**.
- [X] T012 [P] Pre-Wave 4 static DFD inspection check (architect M2): grep `examples/mermaid-agentic-app/architecture.md` for output-integrity trigger keywords (`LLM output`, `rendered HTML`, `model output to browser`, `model output to SQL`, `LLM-generated query`, `template engine`, `outbound HTTP from agent`, `LLM-synthesized URL`, `command construction`, `file path from model`). If ≥1 match: flag in `specs/201-output-integrity-threat-agent/mermaid-baseline-check.md` with architect + team-lead escalation request (TL-H1 re-baseline decision path). If zero matches: record "byte-identity preserved — no baseline break expected" in the same file.

**Checkpoint**: Schema locked at 1.6; ADR-030 Proposed committed with all 8 decisions including regex-extension rule codification; fixtures authored; mermaid-agentic-app baseline-break risk evaluated. Wave 2 can now start.

**TL-H2 Hard Gate**: If T004/T010 not complete by Day 1 EOD (Monday 2026-04-20 23:59 local), surface user tie-break escalation before Day 2 AM. Do NOT proceed to Wave 2 without ADR-030 Proposed commit.

---

## Phase 3: User Story 1 — LLM-Output-to-Downstream-Sink Detection (Priority: P1) MVP

**Goal**: Ship the new `output-integrity` agent + companion skill pattern catalog so that running `/tachi.threat-model` on an architecture with LLM-output-to-downstream-sink flow emits ≥1 `OI-{N}` finding with valid `source_attribution`.

**Independent Test**: Run the pipeline on `examples/agentic-app/architecture.md`; confirm ≥1 `OI-{N}` finding in the output `threats.md` with `category: llm`, `source_attribution` citing OWASP LLM05:2025 primary + relevant CWE related, mitigation text naming a specific encoding/library/pattern.

### Wave 2 — Pattern Catalog + Agent Authoring (0.5-1d, Day 1 PM / Day 2 AM)

- [X] T013 [US1] Author `.claude/skills/tachi-output-integrity/references/detection-patterns.md` per data-model.md E2: frontmatter (`name`, `description`, `consumers: [tachi-output-integrity]`, `last_updated: 2026-04-22`), `## Overview` paragraph (scope + ML09 documentation-only bundling rationale per BLP-01 §4 + forward-reference F-4 per ADR-030 D2), `## Detection Scope` with 10 trigger keywords per Q2 architect decision (`LLM output`, `rendered HTML`, `model output to browser`, `model output to SQL`, `LLM-generated query`, `template engine`, `outbound HTTP from agent`, `LLM-synthesized URL`, `command construction`, `file path from model`) and `## Applicable DFD Element Types` = `Process` only per Q3.
- [X] T014 [US1] Author `## Detection Patterns` section of `detection-patterns.md` with **5 numbered categories** (no 6th per Outcome B): (1) Client-Side Execution Sinks (XSS/DOM — primary `OWASP LLM05:2025`, related `CWE-79`), (2) Server-Side Execution Sinks (SQLi/Command/Code — related `CWE-89` / `CWE-78` / `CWE-94`), (3) SSRF from LLM-Synthesized URLs (related `CWE-918`), (4) Template/Expression Injection (related `CWE-94` substituting for absent `CWE-1336`), (5) Path Traversal + Unsafe File Writes (related `CWE-22` substituting for absent `CWE-73`). Each category MUST include 3-6 indicators + ≥1 worked example + primary/related citations + trigger keywords + applicable DFD element types.
- [X] T015 [P] [US1] Author `.claude/skills/tachi-output-integrity/README.md` — mirror `.claude/skills/tachi-prompt-injection/README.md` shape (title + short description + `Consumers:` list + purpose header). Keep under 50 lines.
- [X] T016 [US1] Author `.claude/agents/tachi/output-integrity.md` 5-section canonical shape per data-model.md E1: YAML frontmatter (`name: output-integrity`, `description`, `tools: Read, Glob, Grep`, `model: sonnet`) → metadata YAML block (`category: llm`, `threat_class: LLM`, `dfd_targets: [Process]`, `owasp_references: [OWASP LLM05:2025, OWASP ML09:2023]`, `output_schema: ../../../schemas/finding.yaml`; NO `agentic_pattern` field per FR-016) → `## Purpose` section (describe output-handling threat surface, 5 sink categories, Heuristic A Outcome B scope resolution, forward-reference F-4) → `## Skill References` table (3 rows: detection-patterns, severity-bands-shared, finding-format-shared) → `## Detection Workflow` with exactly ONE `**MANDATORY**: Read` directive at section start.
- [X] T017 [US1] Complete the `## Detection Workflow` steps in `.claude/agents/tachi/output-integrity.md`: step 1 (trigger keyword identification), step 2 (**structural indicator collection per FR-011 — both-keyword-AND-sink-indicator required**), step 3 (pattern classification), step 4 (severity via OWASP 3×3), step 5 (emission with `source_attribution` + stack-specific mitigation), step 6 (zero-speculation on non-qualifying arch). Reference quickstart.md Step 6 for the emission shape.
- [X] T018 [P] [US1] Structural validation: `wc -l .claude/agents/tachi/output-integrity.md` ≤ 150 (hard cap 180); `grep -c '\*\*MANDATORY\*\*: Read' .claude/agents/tachi/output-integrity.md` = 1; `grep -i maestro .claude/agents/tachi/output-integrity.md .claude/skills/tachi-output-integrity/references/detection-patterns.md` returns empty. Record pass/fail at `.aod/results/wave2-structural-check.md`.

**Checkpoint**: Wave 2 complete. Agent + companion authored. Structural checks green. Ready for Wave 3 orchestrator registration.

---

## Phase 4: User Story 2 — Stack-Specific Mitigation Guidance (Priority: P1)

**Goal**: Every emitted `OI-{N}` finding MUST carry `mitigation` text naming a specific encoding, library, framework helper, or defensive pattern — not generic "sanitize output" prose.

**Independent Test**: For each `OI-{N}` finding in regenerated `examples/agentic-app/threats.md`, inspect the `mitigation` field: it names at least one of the required sink-specific mechanisms per US-2 acceptance scenarios (HTML entity encoding / CSP / safe DOM APIs / framework-native escape helpers for client-side; parameterized queries / JSON escaping / command-line arg vector / allowlist enum for server-side; URL allowlist / scheme validation for SSRF; escape mode / sandboxed renderer for template injection; canonicalization / allowlist directory for path traversal).

### Wave 2 (parallel with US1) — Example Findings + Mitigation Text

- [X] T019 [US2] Author `## Example Findings` section of `.claude/agents/tachi/output-integrity.md` with **2-3 worked `OI-{N}` example findings** demonstrating (a) client-side XSS with `HTML entity encoding` / `Content Security Policy` mitigation, (b) server-side SQLi with `parameterized queries` mitigation, optionally (c) SSRF with `allowlist-based URL validation` mitigation. Each example MUST populate `source_attribution` correctly per contracts/finding-contract.md I4 mapping table.
- [X] T020 [US2] In `detection-patterns.md` pattern categories (authored in T014), each category MUST include at least one worked example whose mitigation text names a specific encoding/library/pattern (not generic). Reviewer checkpoint per FR-017 / PM M3: **each worked example's `description` field MUST explicitly distinguish server-side execution from client-side execution** — surface this as an explicit acceptance predicate.
- [X] T021 [P] [US2] Sanity grep: `grep -iE '(sanitize output|validate input)' .claude/skills/tachi-output-integrity/references/detection-patterns.md .claude/agents/tachi/output-integrity.md` MUST NOT return a line where those phrases appear without a specific mechanism named in the same sentence or adjacent line. Record pass/fail at `.aod/results/wave2-mitigation-specificity-check.md`.

**Checkpoint**: Mitigation specificity verified. FR-017 server/client-side distinction explicit. Ready for Wave 3.

---

## Phase 5: User Story 3 — Heuristic A Resolution for ASI09 Scope (Priority: P1)

**Goal**: ADR-030 Accepted at F-1 merge contains explicit Heuristic A Outcome B determination with justification referencing GUIDE-threat-coverage-research §11, unblocking F-4 `/aod.discover` entry per BLP-01 §8.

**Independent Test**: ADR-030 at F-1 merge: (a) Status: Accepted, (b) Decisions section has D2 explicitly resolving Outcome B, (c) Decisions section references GUIDE-threat-coverage-research §11, (d) Revision History shows Proposed → Accepted transition with dates, (e) agent's `## Purpose` section forward-references F-4 explicitly.

### Wave 1.1 — ADR-030 Proposed authoring (T009-T011 above)

See Phase 2 T009, T010, T011 — ADR-030 Proposed authoring happens at Wave 1.1 to unblock Wave 2.

### Wave 5 — ADR-030 Accepted Transition (Day 3 Outcome B / Day 4 Outcome A)

- [X] T022 [US3] Transition ADR-030 `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md` Status: Proposed → Accepted. Add Revision History row: `| 2026-04-22 | Proposed → Accepted | PR #NNN pending merge | provisional |` (update date and PR number at authoring time).
- [X] T023 [US3] Verify ADR-030 body completeness: all 8 Decisions (D1-D8) populated; Consequences section populated; Cross-References section lists ADR-020/021/022/023/026/027/028/029 per T011 + L2/L3; Revision History tracks Proposed → Accepted. Record checklist pass/fail at `.aod/results/adr-030-completeness-check.md`.
- [X] T024 [US3] Verify agent `## Purpose` section in `.claude/agents/tachi/output-integrity.md` forward-references `trust-exploitation` (F-4) as future owner of human-victim signal class; ASI09 explicitly listed as out-of-scope (per Outcome B).

### Post-Merge (Wave 5 or later)

- [X] T025 [US3] After PR squash-merge: update ADR-030 Revision History with `| YYYY-MM-DD | Accepted with post-merge SHA fill | squash commit {SHORT_SHA} | confirmed |` (ADR-027/028/029 precedent).

**Checkpoint**: Heuristic A determination locked in public ADR; F-4 unblocked for `/aod.discover`.

---

## Phase 6: Wave 3 — Orchestrator Registration + Shared-Reference Additive Edits (Day 2 PM / Day 3 AM, 0.5d)

**Purpose**: Register the new agent in orchestrator dispatch (FR-004) and extend the shared-reference consumers list (FR-005). All edits MUST be additive; ADR-023 Decision 3 byte-identity on `## ` headings is enforced on the shared-reference edit.

- [X] T026 Modify `.claude/agents/tachi/orchestrator.md`: insert `  - output-integrity.md` after the `tool-abuse.md` entry in the AI-tier dispatch list (around lines 44-45 per research.md). Zero changes to STRIDE tier or infrastructure tier.
- [X] T027 Modify `.claude/skills/tachi-orchestration/references/dispatch-rules.md`: extend the LLM dispatch trio (around lines 70-73) to quartet by adding `- \`output-integrity\` (OWASP LLM05:2025)` after the `model-theft` line. Add trigger-keyword activation rule explaining that `output-integrity` requires BOTH a trigger keyword match AND a structural downstream-sink indicator (FR-011 surface).
- [X] T028 [P] Modify `.claude/skills/tachi-shared/references/finding-format-shared.md`: in the frontmatter `consumers:` list (around lines 6-19 per research.md), insert `- output-integrity` on a new line between `  - tool-abuse` and `  - risk-scorer` (tier-grouping placement per HIGH-2). ZERO changes to any body `## ` heading.
- [X] T029 Structural-diff validation on `finding-format-shared.md`: run `git diff main -- .claude/skills/tachi-shared/references/finding-format-shared.md | grep -E '^[+-]## '`. MUST return empty (no `## ` heading changes per ADR-023 Decision 3). Record pass/fail at `.aod/results/wave3-structural-diff-check.md`.
- [X] T030 [P] Q2 keyword false-positive checkpoint per PM M1: manually run the 10 trigger keywords against `examples/agentic-app/architecture.md` and `examples/web-app/architecture.md` component/data-flow descriptions; verify web-app produces zero false matches (no LLM components) and agentic-app produces expected matches (Orchestrator, Specialist Agent, User response flows). If false positives appear on non-LLM components in web-app, refine keyword set before Wave 4. Record results at `.aod/results/wave3-keyword-false-positive-check.md`.

**Checkpoint**: Orchestrator registered; shared reference extended; trigger keywords validated against baseline examples. Ready for Wave 4 example regeneration.

---

## Phase 7: Wave 4 — Example Regeneration + Backward-Compatibility Verification (Day 2 PM / Day 3, 0.5-1d)

**Purpose**: Regenerate `examples/agentic-app/` with the new agent active; verify ≥1 `OI-{N}` finding; verify 5 non-agentic baselines remain byte-identical under `SOURCE_DATE_EPOCH=1700000000` (SC-006 BLOCKER).

- [X] T031 Review T012 output at `specs/201-output-integrity-threat-agent/mermaid-baseline-check.md`. If `mermaid-agentic-app` flagged as potentially baseline-breaking: pause and escalate to architect + team-lead per TL-H1 re-baseline decision path. If no flag: proceed.
- [X] T032 Run `/tachi.threat-model examples/agentic-app/architecture.md` with `SOURCE_DATE_EPOCH=1700000000`. Expect ≥1 new `OI-{N}` finding on LLM Agent Orchestrator and/or Specialist Agent flows. **DEFERRED — requires focused LLM-compute session**
- [X] T033 Run `/tachi.risk-score` on the regenerated `agentic-app` threats. Verify risk-scorer processes `category: llm` findings without edit (FR-014). **DEFERRED**
- [X] T034 Run `/tachi.compensating-controls` on the regenerated `agentic-app`. Verify control-analyzer processes `OI-{N}` findings through `category: llm` code paths. **DEFERRED**
- [X] T035 Run `/tachi.infographic all` on the regenerated `agentic-app`. Regenerate all 6 infographic JPEGs + specs. **DEFERRED**
- [X] T036 Run `/tachi.security-report` on the regenerated `agentic-app`. Regenerate `security-report.pdf` and `security-report.pdf.baseline`. **DEFERRED**
- [X] T037 [P] F-A2 referential-integrity validation: run `pytest tests/scripts/test_output_integrity.py` — all tests pass including a new fixture-driven test invoking `validate_source_attribution` on the regenerated `OI-{N}` findings.
- [X] T038 [P] Backward-compat byte-identity: run `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v`. Expect 5/5 pass on `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`. If `mermaid-agentic-app` fails: escalate per TL-H1 (architect + team-lead approval for re-baseline).
- [X] T039 [P] Git-stage regenerated artifacts for commit: `examples/agentic-app/threats.md`, `threats.sarif`, `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md`, `compensating-controls.sarif`, `threat-report.md`, `attack-trees/`, `attack-chains.md` (if applicable), `threat-*.jpg` × 6 + corresponding specs, `security-report.pdf`, `security-report.pdf.baseline`. **DEFERRED (depends on T032-T036)**

**Checkpoint**: Wave 4 complete. Regenerated example shows OI findings; 5 baselines byte-identical; all pytest green.

---

## Phase 8: Wave 5 — Pre-Merge Validation + PR (Day 3 Outcome B / Day 4 Outcome A)

**Purpose**: Final validation against all 12 spec SCs + quickstart.md 10 steps before opening PR.

- [X] T040 [P] SC-001: verify `output-integrity.md` ≤150 lines; 1 `**MANDATORY**: Read`; under `## Detection Workflow` heading
- [X] T041 [P] SC-002: verify `detection-patterns.md` has ≥5 pattern categories, each with worked example + primary/related citations + trigger keywords + DFD element types
- [X] T042 [P] SC-003: verify `finding-format-shared.md` edit is additive-only per T029 result
- [X] T043 SC-004: confirm `/tachi.threat-model` on regenerated `agentic-app` emits ≥1 `OI-{N}`; non-qualifying baselines emit zero. **DEFERRED (depends on T032)**
- [X] T044 SC-005: confirm ADR-030 Accepted at merge with all 8 decisions + cross-refs + Revision History per T023
- [X] T045 [P] SC-006: confirm T038 backward-compat byte-identity pass on 5 non-agentic baselines
- [X] T046 [P] SC-007: confirm regenerated `agentic-app` OI findings carry mitigations + OWASP LLM05:2025 citation + `source_attribution`. **DEFERRED (depends on T032)**
- [X] T047 [P] SC-008: verify empty diff on `pyproject.toml`, `requirements*.txt`, `package.json` via `git diff main --stat`
- [X] T048 SC-009: 22-file zero-edit grep audit — `git diff main --stat` returns zero lines on the 11 threat agent files + 11 companion `detection-patterns.md` files enumerated in quickstart.md Step 5
- [X] T049 [P] SC-010: confirm F-A2 validation passes on regenerated findings per T037 (fixture-driven PARTIAL: T037 27/27 green on valid + invalid fixtures; regen-based validation deferred with T032)
- [X] T050 [P] SC-011: verify zero MAESTRO references per T018 `grep -i maestro` check
- [X] T051 [P] SC-012: verify schema_version `"1.6"` + regex extends to `OI` per T006; regex unit test passes
- [X] T052 Open PR from `201-output-integrity-threat-agent` → `main` with title `feat(201): output-integrity threat agent (OWASP LLM05:2025)` and body linking to PRD, spec, plan, tasks, ADR-030. Request triple review (PM + Architect + Team-Lead) as part of PR process.

**Checkpoint**: All 12 SCs green; PR opened. Wave 6 buffer day available if Outcome A or R5 (regeneration surface) materializes.

---

## Phase 9: Polish & Cross-Cutting

**Purpose**: Final hygiene + documentation updates.

- [X] T053 [P] Update `CLAUDE.md` Recent Changes section with Feature 201 entry (similar to Features 180/189/194 entries). Include: new agent, ADR-030 lineage, BLP-01 Tier 1 framing, schema 1.5→1.6 minor bump per ADR-026 extension, Heuristic A Outcome B decision, zero-edit invariant preservation, F-1 is first net-new `source_attribution` producer.
- [X] T054 [P] Run quickstart.md Step 10 end-to-end smoke test. Record pass/fail at `.aod/results/quickstart-smoke.md`. (PARTIAL — code-level pytest 27/27 + 13/13 green; live-pipeline smoke deferred with T032-T036)
- [X] T055 [P] Verify `examples/README.md` does NOT need an update (F-1 does not add a new example, only regenerates `agentic-app` — same convention as Features 084/142/145).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (Foundational / Wave 1.0 + 1.1)**: T004 → T005 → T006 (T006 blocks all Wave 2 pattern authoring); T007, T008 parallel; T009 → T010 → T011 (ADR-030 Proposed commit); T012 independent
- **Phase 3 (US1 Wave 2)**: Depends on T006 (schema lock) + T010 (ADR-030 Proposed with Heuristic A D2)
- **Phase 4 (US2 Wave 2)**: Depends on T014 (pattern categories authored) + T016 (agent file skeleton). Can run in parallel with Phase 3 continuation.
- **Phase 5 (US3 Wave 5)**: Depends on Phase 7 (Wave 4 regeneration) + Phase 8 PR pre-merge
- **Phase 6 (Wave 3)**: Depends on Phase 3 + Phase 4 (agent + companion authored)
- **Phase 7 (Wave 4)**: Depends on Phase 6 (orchestrator registration) + T012 (mermaid-agentic-app pre-check)
- **Phase 8 (Wave 5 Pre-Merge)**: Depends on Phase 7 (Wave 4 complete)
- **Phase 9 (Polish)**: After PR opened (can run pre-merge)

### Wave Gate Points

- **Wave 1.1 Gate**: T010 committed → unblocks Wave 2 (TL-H2 hard escalation gate fires if not by Day 1 EOD)
- **Wave 2 Gate**: T013-T018 complete → structural checks green → unblocks Wave 3
- **Wave 3 Gate**: T026-T030 complete → structural-diff green + keyword FP check → unblocks Wave 4
- **Wave 4 Gate**: T032-T039 complete → byte-identity pass + OI findings surfaced → unblocks Wave 5
- **Wave 5 Gate**: T040-T051 all green → unblocks T052 PR open

### Parallel Opportunities

- **Wave 1.1 parallel track**: T005 (regex test) ∥ T007 (valid fixture) ∥ T008 (invalid fixture) ∥ T009 (ADR skeleton) ∥ T012 (mermaid pre-check) — 5 parallel tasks
- **Wave 2 parallel track**: T013 (pattern scope) ∥ T015 (README) — parallel with T016 (agent skeleton). T014 sequential after T013.
- **Wave 3 parallel track**: T026 (orchestrator edit) ∥ T027 (dispatch rules) ∥ T028 (shared consumers) — 3 parallel file edits (different files). T029 sequential after T028. T030 parallel.
- **Wave 4 parallel track**: T037 (F-A2 validation) ∥ T038 (backward-compat) ∥ T039 (git-stage) — 3 parallel verifications
- **Wave 5 parallel track**: T040-T051 all parallel SC checks (12 independent verifications on different file surfaces)

---

## Implementation Strategy

### MVP Path (Outcome B — 2-day baseline)

**Day 1 (Monday 2026-04-20)**:
- Morning: T004 Heuristic A ruling → T006 schema bump → T010 ADR-030 Proposed commit (critical path)
- Parallel afternoon: T005 regex test ∥ T007/T008 fixtures ∥ T012 mermaid pre-check
- Afternoon: T013-T018 pattern catalog + agent file + structural checks (Wave 2)

**Day 2 (Tuesday 2026-04-21)**:
- Morning: T019-T021 mitigation text + example findings + specificity check (continuation of Wave 2)
- Afternoon: T026-T030 orchestrator registration + shared-reference edits + keyword FP check (Wave 3)
- End of day: T031-T036 example regeneration (Wave 4 start)

**Day 3 (Wednesday 2026-04-22)** — also handles Outcome B critical path:
- Morning: T037-T039 validation + git-stage (Wave 4 complete)
- Morning: T022-T024 ADR-030 Accepted transition (Wave 5)
- Afternoon: T040-T051 SC validation sweep (Wave 5)
- End of day: T052 PR open + T053-T055 polish (Wave 9)

**Day 4 (Thursday 2026-04-23)** — **buffer day** per TL-H1:
- If Outcome A chosen: Wave 2 sixth pattern category + additional fixture authoring lands here
- If R5 materializes (regeneration surface): root-cause + rebalance here
- If all else green by Day 3 EOD: absorbed into review lag / merge cycle

### Outcome A Path (if architect chose subsume at T004, 3-3.5-day realistic)

Adds to Wave 2:
- Additional T014-extended: 6th pattern category "Human-Trust Exploitation via LLM Output" with primary `OWASP ASI09:2026`, trigger keywords for human-facing LLM output paths, indicators covering tone/authority signaling/uncertainty absence, ≥1 worked example.
- Additional T019-extended: example finding for human-trust exploitation in agent `## Example Findings`.
- Additional T020-extended: mitigation pattern (tone classifier / source citation requirement / human-in-the-loop on consequential output) in detection-patterns.md.
- Thursday 2026-04-23 buffer likely consumed by 6th-pattern research + authoring + validation.

### Escalation Paths

- **TL-H2 Day-1-EOD hard gate**: if T004/T010 not complete by Day 1 EOD, user tie-break before Day 2 AM (R1 mitigation)
- **mermaid-agentic-app baseline break**: if T012 flags triggers match, pause Wave 4 and escalate to architect + team-lead (TL-H1 re-baseline decision)
- **F-A2 validation failure**: if T037 rejects an OI finding, pattern worked examples likely cite out-of-catalog CWE — revise per FR-007 (CWE-94 for template injection, CWE-22 for path traversal)
- **Regeneration surface drift (R5)**: if T038 byte-identity breaks on non-agentic baseline beyond `mermaid-agentic-app`, pause PR and root-cause before merge

---

## Notes

- [P] tasks = different files / independent commands / no dependencies on incomplete tasks
- [Story] label maps task to user story (US1 = LLM05 detection, US2 = mitigation guidance, US3 = Heuristic A / ADR-030)
- Commit boundaries: Wave 1.1 schema-lock commit is atomic (T006+T009+T010); subsequent waves commit at wave-gate checkpoints
- ADR-030 Proposed commit at T010 unblocks Wave 2; ADR-030 Accepted transition at T022 happens pre-PR open
- 22-file zero-edit invariant is enforced by T048 grep audit — verify this as the final pre-merge check
- Post-merge: T025 SHA-fill is the last task in the sequence (updates Revision History with the squash commit short SHA)
- All PRD architect-fixes + PM-concerns-absorbed predicates traceable: BLOCKING-1 (CWE correction — FR-007 in T014), BLOCKING-2 (schema bump — T006), HIGH-1 (orchestrator carve-out — T026/T027), HIGH-2 (tier-grouping placement — T028), HIGH-3 (ML09 doc-only — T013 Overview), HIGH-4 (agentic_pattern exclusion — T016 metadata), TL-H1 (Outcome A/B envelopes — Implementation Strategy section), TL-H2 (Day-1-EOD gate — Phase 2 Checkpoint), **PM M1 (keyword FP checkpoint — T030)**, **PM M2 (Outcome A counter-argument — T010 D2)**, **PM M3 (server/client-side distinction predicate — T020)**, **Architect M1 (regex-extension rule D8 — T010)**, **Architect M2 (mermaid pre-check — T012)**, **Architect L1 (D1-D8 enumeration — T010)**, **Architect L2 (ADR-020 cross-ref — T011)**, **Architect L3 (ADR-022 cross-ref — T011)**
