---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-15
    status: APPROVED
    notes: "0 CRITICAL / 0 HIGH / 0 MEDIUM / 3 LOW (all informational, deferred). Plan respects spec scope airtight, covers all 8 FRs with explicit component ownership, addresses all 5 user story acceptance criteria, honors the 3-hour Wave 1 timebox with 3 contingency options, does NOT prejudge Option A/B/C, handles FR-008 conditionality correctly, and makes the Wave 1 to Wave 2 sequence dependency (SKILL.md references FINAL ADR text) explicit in Data Flow. Full review at .aod/results/plan-pm-review-144.md."
  architect_signoff:
    agent: architect
    date: 2026-04-15
    status: APPROVED_WITH_CONCERNS
    notes: "0 CRITICAL / 0 HIGH / 2 MEDIUM / 4 LOW. C2 (MEDIUM, inline-fixable) addressed: spec SC-007 promoted to include the [-n non-empty guard from quickstart, preventing both-empty false-PASS. C1 (MEDIUM, deferred to tasks.md): encode FR-008 Issue-filing dependency on finalized ADR Alternatives effort string as task-level dependency. C3-C6 (LOW): plan line estimate, mapping naming variant (PRD-specified), runtime-component prose tightening, ADR-022 exclusion implicit — all deferred or cosmetic. Plan faithfully mirrors PRD 143 / ADR-024 architectural structure with appropriate tightening (3h timebox, byte-equality SC, docs: prefix, git-diff zero-drift). Five-layer scope discipline preserved. Documentation-only constraint fully preserved across all 11 Constitution principles. Full review at .aod/results/plan-architect-review-144.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: NIST AI RMF Integration Evaluation ADR

**Branch**: `144-nist-ai-rmf-evaluation-adr` | **Date**: 2026-04-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/144-nist-ai-rmf-evaluation-adr/spec.md`

## Summary

A documentation-only ADR-025 spike evaluating NIST AI Risk Management Framework (NIST AI 100-1, AI RMF 1.0 + NIST AI 600-1 Generative AI Profile) against tachi's compensating controls analyzer. Closes the regulated-adopter half of the MAESTRO companion-framework decision space (the AIVSS half closed via Feature 143 / ADR-024 on 2026-04-15).

**Three deliverables, two waves**:
1. **Wave 1 — Research (web-researcher, 3-hour timebox)**: confirm NIST AI RMF 1.0 + NIST AI 600-1 versions/URLs/hierarchy; append findings to `specs/144-nist-ai-rmf-evaluation-adr/research.md` under `## Wave 1 — NIST AI RMF Spec Notes`
2. **Wave 2 — ADR Authorship (architect, sequential)**: draft ADR-025 (Context with Surface A/B/C tables → Decision → Alternatives → Rationale → Consequences → Re-Evaluation Triggers → References) → create `nist-ai-rmf-mapping.md` artifact (content shape conditional on chosen option) → append SKILL.md NIST AI RMF Relationship section → conditionally file follow-on Issue (FR-008, only if Option B/C) → append back-reference to ADR-024 Related ADRs line

**Technical approach**: zero production code changes. All edits are Markdown content additions or single-line edits. No schema bumps. No agent file changes. No script changes. No example regen. Backward-compatibility guaranteed by SC-006 (git diff zero-drift on `schemas/`, `scripts/`, `.claude/agents/`, `examples/`) and SC-010 (`pytest tests/scripts/test_backward_compatibility.py` 5/5 byte-identical under `SOURCE_DATE_EPOCH=1700000000` per ADR-021).

**Decision-noun discipline**: implementer chooses Option A (docs-only) / B (shallow wired) / C (deep wired) **after** Wave 1 research completes — spec does not prejudge. Decision-noun in ADR-025 Decision section MUST equal decision-noun in SKILL.md NIST AI RMF Relationship section (case-insensitive byte-equality, SC-007).

## Technical Context

**Language/Version**: N/A — documentation-only (Markdown). No code authored or modified.

**Primary Dependencies**: None added. Existing tachi pipeline dependencies (Python 3.11+, Typst, mmdc) remain unchanged. Documentation references NIST canonical specifications via stable URLs (no fetched-at-runtime dependency).

**Storage**: Git repository only. ADR-025 stored at `docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md`. Mapping reference at `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`. SKILL.md edit at `.claude/skills/tachi-control-analysis/SKILL.md`. ADR-024 back-reference at `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md`.

**Testing**:
- `pytest tests/scripts/test_backward_compatibility.py` (must pass 5/5 byte-identical under `SOURCE_DATE_EPOCH=1700000000`)
- Shell verifier scripts for SC-001 through SC-013 (`grep`, `awk`, `wc -w`, `git diff`, `git log`, `gh issue list`, `[ -f ... ]`)
- Manual reviewer inspection for SC-004 (relationship label coverage in Surface tables) and SC-008 (Mapping reference content shape)

**Target Platform**: Documentation rendered on GitHub `main` (Markdown standard, no GFM extensions required) and locally via `cat`/IDE.

**Project Type**: Documentation spike — single-feature, no source structure changes.

**Performance Goals**: N/A — no runtime impact.

**Constraints**:
- 3-hour Wave 1 timebox (PRD Risk R1 mitigation; Edge Case 1 + SC-013)
- 1 working day implementation (research + authorship) + brief PR cycle (per PRD Timeline)
- 5-iteration governance budget (per `/aod.define` rules)
- Zero changes outside the 5-surface allow-list (SC-006)
- All commits MUST use `docs:` conventional commit prefix per Constitution IX (SC-012)
- ADR Status field MUST read exactly `Accepted` at merge (not Proposed) per SC-002

**Scale/Scope**: 3 net-new artifacts (ADR-025, mapping reference, conditional follow-on Issue) + 2 single-line/single-section edits to existing files (SKILL.md, ADR-024). Estimated 200-280 lines for ADR-025 (longer than ADR-024's 247 lines because NIST AI RMF has 4 Functions × Categories × Subcategories + 12 GAI risks vs AIVSS's single spec).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Applies? | Compliance | Notes |
|-----------|----------|------------|-------|
| **I. General-Purpose Architecture** | Yes | PASS | ADR documents framework alignment posture; doesn't add domain-specific code. NIST AI RMF mapping is documentation, not runtime logic. |
| **II. API-First Design** | No | N/A | No API surface; documentation-only. |
| **III. Backward Compatibility (NON-NEGOTIABLE)** | Yes | PASS | SC-006 enforces zero-drift on schemas/scripts/agents/examples. SC-010 enforces 5/5 byte-identical PDF baselines under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. Local `.aod/` workflows unaffected. |
| **IV. Concurrency & Data Integrity** | No | N/A | No state transitions; documentation-only. |
| **V. Privacy & Data Isolation** | No | N/A | Public ADR; no user data. |
| **VI. Testing Excellence** | Partial | PASS | Existing `pytest tests/scripts/test_backward_compatibility.py` covers post-merge regression (SC-010). New shell verifiers (SC-001 through SC-013) constitute the test surface for documentation correctness. No new code → no new unit/integration test surface. |
| **VII. Definition of Done (NON-NEGOTIABLE)** | Yes | PASS | DoD applies: (1) merged to `main` (PR via team-lead per PRD Timeline); (2) tested (backward-compatibility 5/5 + 13 SCs verified); (3) user-validated (architect approval = "Accepted at merge" attestation per Closed Q2). Exception: Documentation-only changes do not require production deployment per Constitution VII Exceptions. |
| **VIII. Observability & Root Cause Analysis** | No | N/A | No runtime path to observe. |
| **IX. Git Workflow & Feature Branching (NON-NEGOTIABLE)** | Yes | PASS | Feature branch `144-nist-ai-rmf-evaluation-adr` already in use. SC-012 enforces `docs:` conventional commit prefix (not `feat:` or `fix:`). PR review required before merge. |
| **X. Product-Spec Alignment & Architecture Review (NON-NEGOTIABLE)** | Yes | IN PROGRESS | PRD 144 has triple Triad sign-off (PM + Architect + Team-Lead, all APPROVED_WITH_CONCERNS, 2026-04-15). Spec has PM sign-off (APPROVED, 2026-04-15). This plan.md is being submitted for PM + Architect dual sign-off. tasks.md will require triple sign-off. |
| **XI. SDLC Triad Collaboration** | Yes | PASS | Triad workflow active. PRD ratified 2026-04-15 with all three Triad sign-offs. Plan stage chains spec → project-plan → tasks via `/aod.plan` orchestrator. |

**Constitution Gate Result**: PASS — no violations requiring justification.

## Project Structure

### Documentation (this feature)

```
specs/144-nist-ai-rmf-evaluation-adr/
├── spec.md                     # Feature specification (PM-approved 2026-04-15)
├── plan.md                     # This file (/aod.project-plan output)
├── research.md                 # Pre-spec research + Wave 1 NIST AI RMF Spec Notes (Phase 0)
├── tasks.md                    # Task breakdown (/aod.tasks output, pending)
├── checklists/
│   └── requirements.md         # Spec quality checklist
├── data-model.md               # Lightweight artifact map (Phase 1, see below)
└── quickstart.md               # Implementer quickstart (Phase 1, see below)
```

### Source Code (repository root)

This is a documentation-only feature. **No source code is created or modified.** Files touched are:

```
docs/architecture/02_ADRs/
├── ADR-024-owasp-aivss-evaluation.md   # Single-line edit: append "ADR-025" to Related ADRs line (FR-005 cross-ref + SC-011 + Closed Q4)
└── ADR-025-nist-ai-rmf-evaluation.md   # NEW (FR-005 primary deliverable)

.claude/skills/tachi-control-analysis/
└── SKILL.md                            # Append "## NIST AI RMF Relationship" section (80-200 words, FR-006 + SC-005 + SC-007)

.claude/skills/tachi-shared/references/
└── nist-ai-rmf-mapping.md              # NEW (content shape conditional on chosen option, FR-007 + SC-008)
```

**Structure Decision**: Documentation spike. No source structure (`src/`, `tests/`, `backend/`, `frontend/`) changes. The spec's Out-of-Scope section explicitly excludes all schema, agent, script, and example modifications. Repository remains in single-project layout (current default).

## Components

This feature does not add or modify runtime components. Components touched are documentation surfaces:

### Component 1 — ADR-025 (new)

**Location**: `docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md`

**Owner**: architect (Wave 2 author)

**Sections**:
- YAML-style header: `**Status**: Accepted` | `**Date**: YYYY-MM-DD` | `**Deciders**: Architect, Product Manager, Team-Lead` | `**Feature**: 144 (MAESTRO Companion: NIST AI RMF)` | `**Related ADRs**: [ADR-024](...) (companion AIVSS), [ADR-020](...) (MAESTRO classification), [ADR-019](...) (shared definitions), [ADR-018](...) (baseline lineage), [ADR-021](...) (SOURCE_DATE_EPOCH determinism), [ADR-023](...) (skill-references pattern)`
- `## Context` — NIST AI RMF spec summary (versions/URLs from FR-001), tachi compensating controls recap, three Surface subsections with explicit anchors:
  - `<a id="surface-a"></a>` Surface A — NIST AI RMF Functions × tachi pipeline phases
  - `<a id="surface-b"></a>` Surface B — NIST AI RMF Subcategories × tachi compensating control categories
  - `<a id="surface-c"></a>` Surface C — NIST AI 600-1 Generative AI Profile risks × tachi STRIDE+AI categories
- `## Decision` — first paragraph contains canonical decision-noun (Option A/B/C/Hybrid B+C)
- `## Rationale` — five-criteria justification (maturity, adoption, compatibility, effort, compliance value); explicit comparison to ADR-024 reasoning; sector-specific compliance value (SOC 2, FedRAMP, HIPAA, FFIEC, EU AI Act)
- `## Alternatives Considered` — three options with Pros/Cons/Effort/Compliance Value/Determinism Impact/Why-Chosen|Not
- `## Consequences` — Positive/Negative/Mitigation/Follow-on (Option B/C: link to follow-on Issue per FR-008; Option A: name artifact location and maintenance commitment)
- `## When to Re-Evaluate` — concrete trigger (e.g., "≥3 regulated-industry adopter inquiries" OR "NIST AI RMF 2.0 publication" OR "SP 800-53 AI overlay GA")
- `## References` — internal (tachi PRDs, ADRs, files) + external (NIST canonical URLs)

### Component 2 — `nist-ai-rmf-mapping.md` (new)

**Location**: `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`

**Owner**: architect (Wave 2)

**Content shape** (conditional on chosen option):
- **Option A**: Complete mapping table (8 tachi compensating-control categories → NIST AI RMF Subcategory equivalents) + Surface C crosswalk (12 GAI risks → 11 STRIDE+AI categories) + back-link to ADR-025
- **Option B/C**: One-paragraph relationship-only stub naming the wired-integration site (controls schema for B; new analyzer agent for C) + forward link to follow-on Issue + back-link to ADR-025

**Constraints**: additive only (does NOT modify any existing tachi-shared reference). Renderable in standard Markdown (no GFM extensions).

### Component 3 — SKILL.md NIST AI RMF Relationship Section (additive edit)

**Location**: `.claude/skills/tachi-control-analysis/SKILL.md`

**Owner**: architect (Wave 2, after ADR-025 Decision text is finalized)

**Insertion point**: After existing `## Domain Overview` section, before existing `## Baseline-Aware Control Analysis Rules` section (mirrors ADR-024 → tachi-risk-scoring/SKILL.md placement)

**Contents**:
- New `## NIST AI RMF Relationship` section
- 80-200 words (verified by `awk` extraction + `wc -w`, SC-005)
- Decision-noun phrase byte-identical (case-insensitive) to ADR-025 Decision section first paragraph (SC-007)
- Relative link to ADR-025: `../../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md`

### Component 4 — ADR-024 Back-Reference (single-line edit)

**Location**: `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md`

**Owner**: architect (Wave 2, ships in same PR as ADR-025)

**Edit**: Append `[ADR-025](ADR-025-nist-ai-rmf-evaluation.md) (companion NIST AI RMF evaluation)` to the existing Related ADRs line. Does NOT change ADR-024's Status field (housekeeping edit per existing tachi convention).

### Component 5 — Follow-On GitHub Issue (conditional)

**Location**: GitHub Issues (filed via `bash .aod/scripts/bash/create-issue.sh`)

**Owner**: product-manager (Wave 2 cleanup, only if Option B or C chosen)

**Contents** (per FR-008): `stage:discover` label, concrete title, body links back to ADR-025, names surfaces that would change, includes effort estimate copied verbatim from ADR-025 Alternatives, names "non-disruptive"/"opt-in" constraint.

**Skipped if Option A chosen.**

## Data Flow

This feature does not add data flow. Documentation flows from authoring (Wave 1 + Wave 2) to publication (PR merge to `main`):

```
Wave 1 (3-hour timebox)
  web-researcher reads NIST AI RMF 1.0 + NIST AI 600-1 (canonical URLs from spec Assumptions)
  → appends findings to specs/144-*/research.md ## Wave 1 — NIST AI RMF Spec Notes section
  → escalates to PM if 3-hour budget exceeded (3 contingency options per Edge Case 1)

Wave 2 (sequential authorship)
  architect drafts ADR-025 skeleton
  → fills Surface A/B/C tables from research.md Wave 1 notes + tachi compensating controls reference
  → drafts Decision (canonical noun) → Rationale (five criteria + ADR-024 comparison) → Alternatives → Consequences → Re-Evaluation Triggers → References
  → creates .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md (content shape per chosen option)
  → appends ## NIST AI RMF Relationship section to .claude/skills/tachi-control-analysis/SKILL.md (decision-noun byte-identical to ADR-025)
  → appends ADR-025 back-reference to docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md Related ADRs line
  → product-manager files follow-on Issue if Option B/C chosen (FR-008)

PR Cycle (~half-day)
  Open PR with docs: prefix conventional commit
  → 13 SCs verified (shell + awk + grep + pytest + manual inspection)
  → architect reviews PR (= "Accepted at merge" attestation per Closed Q2)
  → squash-merge to main
```

## Tech Stack

No tech stack changes. Reference lineage unchanged from current state:

- **Documentation format**: Markdown (CommonMark, no GFM extensions required)
- **ADR conventions**: Match ADR-022, ADR-023, ADR-024 structural template (header block + Decision + Rationale + Alternatives Considered + Consequences + References sections)
- **Verifiers**: shell (`grep`, `awk`, `wc -w`, `tr`), Python (`pytest tests/scripts/test_backward_compatibility.py`), git (`git diff`, `git log`)
- **Determinism baseline**: `SOURCE_DATE_EPOCH=1700000000` for byte-identical PDF comparison (per ADR-021)
- **Conventional commits**: `docs:` prefix only (per Constitution IX + SC-012)
- **GitHub CLI**: `bash .aod/scripts/bash/create-issue.sh` for FR-008 conditional Issue filing

**Zero new runtime dependencies**: empty diff on `requirements*.txt`, `pyproject.toml`, `package.json` per spec Constraints. Zero new CLI prerequisites (no precedent like ADR-022's mmdc requirement).

## Phase 0: Outline & Research

**Status**: Pre-spec research complete. Findings in `specs/144-nist-ai-rmf-evaluation-adr/research.md` sections 1-5 (KB precedent, codebase analysis, architecture constraints, industry/external research, recommendations for spec).

**Phase 0 Decisions**:

| Decision | Rationale | Alternatives Considered |
|----------|-----------|-------------------------|
| Mirror PRD 143 / ADR-024 structure | Direct precedent — same documentation-only ADR shape, same closing-companion-framework purpose, same five-layer scope discipline | Authoring from scratch — rejected because PRD 143 just shipped (2026-04-15) and reviewer-validated patterns reduce risk and review iterations |
| Two-wave delivery (Wave 1 research + Wave 2 authorship) | Same as PRD 143 timeline; provides clear escalation point if NIST research surface exceeds budget | Single-wave (architect does both research + authorship) — rejected because web-researcher is the assigned agent for FR-001 per PRD Agent Assignment Rationale (line 476) |
| 3-hour Wave 1 timebox (vs PRD 143's 2-hour) | NIST surface area is larger (AI RMF 1.0 + NIST AI 600-1 + Function/Category/Subcategory hierarchy + 12 GAI risks) per PRD R1 | 2-hour timebox — rejected as inadequate per PRD architect signoff C3; 4-hour — rejected as too lax per PRD team-lead HIGH-1 |
| Decision-noun byte-equality verifier (SC-007) | Tightens PRD 143 lesson — "any noun in both" was insufficient; byte-equality with case-normalization prevents synonym drift | Presence-only check — rejected per PRD 143 reviewer findings; full string equality (no case normalization) — rejected as overly strict (markdown conventions vary on Title Case vs lowercase) |
| Conditional FR-007 always creates the file (full mapping for A; stub for B/C) | Per PRD discovery item: "Shared reference (`tachi-shared/references/`) updated with a one-paragraph NIST AI RMF relationship statement regardless of chosen option" | File creation only for Option A — rejected per PRD discovery item explicit requirement; file content fully identical across options — rejected because Option B/C should defer mapping to follow-on |
| Don't prejudge Option A/B/C in spec | Spec must specify acceptance criteria for each option's downstream effects, NOT recommend an option (implementer chooses after Wave 1 read) | Recommend Option A in spec — rejected per PRD FR-4 "reasoned afresh" clause and Assumption #5 ("Pre-1.0 maturity does not auto-default to diverge") |

**Wave 1 (FR-001) outputs** will be appended to `research.md` under `## Wave 1 — NIST AI RMF Spec Notes` heading. Pre-spec research sections 1-5 are forward-looking guidance; Wave 1 implementer corrects assumptions (e.g., PRD's "12-13 GAI risks" → exactly 12 per pre-spec research §4) inline if needed.

**Output**: `research.md` (already exists with pre-spec sections 1-5; Wave 1 will append section 6+).

## Phase 1: Design & Contracts

**Prerequisites**: research.md complete (pre-spec sections done; Wave 1 will append during implementation).

### 1a. Data Model

This feature does not introduce or modify runtime data structures. The "data model" for this feature is the artifact map already enumerated in spec.md Key Entities and plan.md Components sections:

- **ADR-025** (new Markdown file)
- **Surface A / B / C tables** (Markdown tables embedded in ADR-025 Context)
- **NIST AI RMF Mapping Reference** (new Markdown file, conditional shape)
- **SKILL.md NIST AI RMF Relationship Section** (new Markdown section appended to existing SKILL.md)
- **ADR-024 Back-Reference** (single-line edit to existing ADR)
- **Follow-On Issue** (new GitHub Issue, conditional)

A separate `data-model.md` artifact is omitted — there is no schema, data structure, or relational model to document. The spec.md Key Entities section + this plan.md Components section serve as the artifact map.

### 1b. API Contracts

This feature does not add or modify any API surface. No `/contracts/` directory is generated.

### 1c. Quickstart

A lightweight `quickstart.md` will be generated to onboard the implementer:

```
specs/144-nist-ai-rmf-evaluation-adr/quickstart.md
```

Contents (high-level):
- Wave 1: web-researcher reads NIST AI 100-1 + NIST AI 600-1 (URLs from spec Assumptions); appends to research.md `## Wave 1 — NIST AI RMF Spec Notes`; respects 3-hour timebox; escalates per Edge Case 1 if overrun
- Wave 2: architect drafts ADR-025 → creates mapping reference → appends SKILL.md section → appends ADR-024 back-ref; product-manager files follow-on Issue if Option B/C
- 13 SCs verified by shell scripts (run before opening PR)
- Conventional commit: `docs(144): ...` prefix only

### 1d. Agent Context Update

This feature does not change tachi pipeline agent context. The `.claude/agents/tachi/*.md` files are explicitly off-limits per spec Out-of-Scope. The SKILL.md edit (FR-006) to `.claude/skills/tachi-control-analysis/SKILL.md` is a skill file (consumed by control-analyzer agent), not an agent file.

The `update-agent-context.sh claude` script is **not** invoked because:
1. No new technologies are added to the project
2. No agent-discoverable conventions change

### Post-Design Constitution Re-Check

Re-checked after Phase 1 design above. Result: **PASS** — same as pre-Phase 0 check. No new violations introduced by lightweight artifact map design. Documentation-only constraint preserved.

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

No constitutional violations to justify. All gates PASS.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | (none) | (none) |
