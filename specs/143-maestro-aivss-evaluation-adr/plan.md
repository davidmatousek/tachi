---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-15
    status: APPROVED
    notes: "All 6 alignment criteria PASS — 20/20 checks green. Agent assignment verbatim with PRD Team-Lead Rec #1 (web-researcher FR-001, architect FR-002-006, product-manager FR-007, code-reviewer FR-008; senior-backend-engineer excluded). 2-hour canonical-home research timebox preserved at 4 locations. Conditional FR-007 logic (Option A/B → file Issue, Option C → skip) encoded at 6 locations. Zero constitutional violations. 3 non-blocking tasks.md polish observations recorded."
  architect_signoff:
    agent: architect
    date: 2026-04-15
    status: APPROVED
    notes: "Plan faithfully elaborates PRD+spec for documentation-only ADR spike. All 9 review dimensions PASS: invariants (ADR-021/023/019/020 + Constitution III) carried forward, 11-principle Constitution Check defensible, ADR-024 format matches ADR-019-023 precedent, three-surface rigor preserved with CVSS 3.1-vs-4.0 correctly flagged as Conflict row, zero-drift gate at PR review time owned by code-reviewer enumerating schemas/scripts/agents/examples, Related ADRs minimum (ADR-020+019+018), Re-Evaluate trigger aligned to AIVSS 1.0. Phase 1 artifact omission technically sound. 6 non-blocking observations recorded."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: MAESTRO Phase 4 — OWASP AIVSS Evaluation ADR

**Branch**: `143-maestro-aivss-evaluation-adr` | **Date**: 2026-04-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/143-maestro-aivss-evaluation-adr/spec.md`

## Summary

Documentation-only ADR spike. Evaluate OWASP AIVSS against tachi's four-dimensional composite risk score, commit the decision as **ADR-024** under `docs/architecture/02_ADRs/`, and add a 80-200 word AIVSS Relationship section to `.claude/skills/tachi-risk-scoring/SKILL.md`. Zero production code changes. If the decision is to adopt AIVSS (Options A or B), file a follow-on implementation Issue with `stage:discover` label; if the decision is divergence (Option C), no Issue is filed.

Two-wave delivery: **Wave 1** = AIVSS specification research (FR-001), **Wave 2** = ADR authorship + SKILL.md update + conditional Issue (FR-002 through FR-007) + zero-drift verification gate (FR-008). One-day wall-clock target.

## Technical Context

**Language/Version**: N/A — documentation-only; no code authoring, no new runtime dependencies
**Primary Dependencies**: None added. Existing stack remains: Python 3.11 (dev scripts), Typst (PDF), Mermaid CLI. No changes to `pyproject.toml`, `requirements*.txt`, or `package.json`
**Storage**: N/A — no data persistence changes
**Testing**: No new test files. One existing verification gate (`git diff` assertion for zero drift, per SC-006) runs during PR review. The existing backward-compatibility PDF baseline suite (`tests/scripts/test_backward_compatibility.py`) is trivially satisfied because no pipeline inputs change
**Target Platform**: Markdown + YAML files only. Primary surfaces: `docs/architecture/02_ADRs/` (new ADR-024), `.claude/skills/tachi-risk-scoring/SKILL.md` (updated), `github.com/davidmatousek/tachi/issues` (conditional new Issue)
**Project Type**: Documentation artifact — single-surface ADR + single-section skill update
**Performance Goals**: N/A (no runtime path)
**Constraints**: Zero-drift invariant on `schemas/`, `scripts/`, `.claude/agents/`, `examples/`; ADR Status must read `Accepted` at merge; FR-001 canonical-home research timeboxed to 2 hours before PM escalation
**Scale/Scope**: One new ADR file (~8-12KB), one updated SKILL.md section (~1KB addition), optionally one new GitHub Issue. Nothing else changes.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Applies? | Status | Notes |
|-----------|----------|--------|-------|
| I. General-Purpose Architecture | Yes (meta) | PASS | ADR-024 is generic to risk scoring posture; does not introduce domain-specific logic anywhere |
| II. API-First Design | No | N/A | No API changes; no endpoints affected |
| III. Backward Compatibility (NON-NEGOTIABLE) | Yes | PASS | Zero schema/script/agent/example changes; PDF baselines byte-identical under `SOURCE_DATE_EPOCH=1700000000` trivially satisfied |
| IV. Concurrency & Data Integrity | No | N/A | No state transitions affected |
| V. Privacy & Data Isolation | No | N/A | No user data handling changes |
| VI. Testing Excellence | Partial | PASS | No new test files required (no new code); SC-006 `git diff` assertion is the only new verification. Existing backward-compatibility suite trivially green |
| VII. Definition of Done (NON-NEGOTIABLE) | Yes | PASS with carry-forward | Production push / user-validation steps satisfied by a docs-only PR merged to main with architect approval (per ADR-022 and ADR-023 precedent); the "architect approval = Accepted attestation" rule is closed in PRD Open Questions |
| VIII. Observability & Root Cause Analysis | No | N/A | No runtime path to instrument |
| IX. Git Workflow & Feature Branching (NON-NEGOTIABLE) | Yes | PASS | Feature branch `143-maestro-aivss-evaluation-adr` active; commits follow Conventional Commits with `docs:` type (not `feat:`/`fix:`) |
| X. Product-Spec Alignment (NON-NEGOTIABLE) | Yes | PASS | PRD approved (Triad APPROVED_WITH_CONCERNS, all inline fixes landed); spec approved (PM APPROVED); plan awaits dual sign-off via this workflow; tasks.md awaits triple sign-off |
| XI. SDLC Triad Collaboration | Yes | PASS | Feature PRD followed parallel Triad review (PM draft → architect + tech-lead review → PM finalize). This plan continues the same pattern |

**No violations**. Complexity Tracking section is empty.

## Architectural Invariants (Carry-Forward)

| Invariant | Source | Application to Feature 143 |
|-----------|--------|----------------------------|
| Deterministic pipeline outputs | ADR-021 | Trivially satisfied — no pipeline inputs change |
| Shared-reference discipline | ADR-019 | Forward-looking only. If the ADR-024 decision adopts AIVSS, any follow-on shared ref must land under `.claude/skills/tachi-shared/references/`. No new shared refs in this feature. |
| Detection-variant agent shape | ADR-023 | Zero threat agent files touched |
| MAESTRO canonical layer names | ADR-020 / PRD 136 | Cross-referenced in ADR-024's Related ADRs; no new labels |
| Hard CLI prerequisite pattern | ADR-022 | Not invoked (no new CLI dep) |
| Baseline-aware pipeline correlation | ADR-018 | Scoring lineage — cross-referenced in ADR-024 Related ADRs |

## Components

This feature touches three surfaces; the canonical extraction for downstream system-design reference is listed below.

| Component | Type | File Path | Change Type | Rationale |
|-----------|------|-----------|-------------|-----------|
| ADR-024: OWASP AIVSS Evaluation and Tachi Composite Scoring Posture | New architecture decision record | `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` | Create | PRD FR-5, Spec FR-005 — the primary deliverable |
| tachi-risk-scoring skill: AIVSS Relationship section | Update to existing skill file | `.claude/skills/tachi-risk-scoring/SKILL.md` | Add new section | PRD FR-6, Spec FR-006 — cross-reference to ADR-024 for skill consumers |
| Follow-on implementation Issue (conditional) | New GitHub Issue | `github.com/davidmatousek/tachi/issues` | Create (only if decision = Option A or B) | PRD FR-7, Spec FR-007 — deferred adoption work with option-specific effort estimate copied verbatim from ADR-024 |

**Architectural posture**: additive-only. No existing agent, schema, script, or example file is modified. ADR-024 becomes the canonical source of truth for tachi's AIVSS stance; SKILL.md becomes the runtime-adjacent pointer; the conditional Issue becomes the discovery anchor for any future implementation work.

## Data Flow

**No runtime data flow changes.** The feature is purely authoritative-document work.

### Author-time flow (implementer's workflow)

```
Wave 1 (Research):
  web-researcher → aivss.owasp.org (read v0.8 spec end-to-end, 2-hour timebox)
                → captures: version, URL, dimensions, formula, bands (if any)
                → produces: internal notes for Wave 2 consumption

Wave 2 (Authorship):
  architect → synthesizes Wave 1 notes with schemas/risk-scoring.yaml + severity-bands-shared.md
           → writes: ADR-024 (Context with 3 surfaces, Decision, Rationale, Alternatives, Consequences)
           → writes: SKILL.md AIVSS Relationship section (80-200 words, relative link to ADR-024)
  product-manager → IF decision is Option A or B:
                    uses .aod/scripts/bash/create-issue.sh
                    creates Issue with stage:discover label, option-specific effort verbatim
                  → ELSE (Option C):
                    no Issue filed (correct behavior per FR-007 conditionality)
```

### Read-time flow (stakeholder's workflow — post-merge)

```
CISO / compliance officer / future maintainer / security engineer
  → opens ADR-024 → reads Decision → follows cross-reference to SKILL.md (or vice versa)
  → sees consistent decision across both surfaces (FR-006 single-source-of-truth rule)
```

### Verification flow (gate at PR review)

```
PR review → SC-001 file exists → SC-002 Status: Accepted grep → SC-003 three surfaces present
         → SC-004 ≥3 options with effort estimate → SC-005 SKILL.md section present + word count
         → SC-006 git diff returns empty for schemas/scripts/agents/examples
         → SC-007 decision-noun consistency between ADR and SKILL.md
         → SC-008 conditional Issue filed (only if A or B) → SC-009 Related ADRs list includes ADR-020, -019, -018
```

## Tech Stack

### New Dependencies

**None.** This feature introduces zero new runtime or development dependencies.

### Tools Used (all pre-existing)

| Tool | Purpose | Source |
|------|---------|--------|
| Markdown | ADR-024 + SKILL.md authorship | Native to repository |
| YAML | ADR-024 frontmatter | Matches existing ADR-020 through ADR-023 convention |
| `.aod/scripts/bash/create-issue.sh` | Conditional follow-on Issue filing (Wave 2) | Pre-existing at `.aod/scripts/bash/create-issue.sh` |
| `bash` + `grep` + `git diff` | Verification gates (SC-002, SC-005, SC-006, SC-007) | Standard shell |
| Existing backward-compat test suite | Trivial pass gate | `tests/scripts/test_backward_compatibility.py` |

### Cross-Reference Dependencies (must remain discoverable)

- [ADR-020 MAESTRO Layer Classification](../../docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md) — taxonomy context for ADR-024 Related ADRs
- [ADR-019 Shared Definitions and Model Field Governance](../../docs/architecture/02_ADRs/ADR-019-shared-definitions-and-model-field-governance.md) — forward-looking for any follow-on adoption
- [ADR-018 Baseline-Aware Pipeline Correlation](../../docs/architecture/02_ADRs/ADR-018-baseline-aware-pipeline-correlation.md) — scoring lineage context
- [schemas/risk-scoring.yaml](../../schemas/risk-scoring.yaml) — source of truth for tachi's four-dimensional composite (Surface A baseline for FR-002)
- [.claude/skills/tachi-shared/references/severity-bands-shared.md](../../.claude/skills/tachi-shared/references/severity-bands-shared.md) — source of truth for Surface C baseline
- [.claude/skills/tachi-risk-scoring/references/scoring-dimensions.md](../../.claude/skills/tachi-risk-scoring/references/scoring-dimensions.md) — detailed dimension definitions for Surface A

## Project Structure

### Documentation (this feature)

```
specs/143-maestro-aivss-evaluation-adr/
├── plan.md                    # This file (/aod.project-plan output)
├── research.md                # Research phase output (already written during /aod.spec Step 2)
├── spec.md                    # Feature specification (already approved by PM)
├── checklists/
│   └── requirements.md        # Spec quality checklist (validated PASS)
└── tasks.md                   # Task breakdown (/aod.tasks output — not yet created)
```

**Note on Phase 1 design artifacts**: `data-model.md`, `contracts/`, and `quickstart.md` are **not applicable** to this feature:
- No data entities to model (the "data" is the prose inside ADR-024 and a skill section — neither persists through a schema)
- No API contracts to author (no endpoints change)
- No quickstart guide to write (the deliverable *is* a discoverable ADR — "opening the ADR" is its own quickstart)

This omission is deliberate and disclosed. A plan.md template's suggestion to produce these three artifacts is advisory — concrete judgment applies, and for a pure-documentation feature they would be empty placeholders with no reader value.

### Source Code (repository root)

This feature does **not** add or modify any source code directories. The repository tree is unchanged except for the two new content surfaces:

```
docs/architecture/02_ADRs/
└── ADR-024-owasp-aivss-evaluation.md       # NEW — the primary deliverable

.claude/skills/tachi-risk-scoring/
└── SKILL.md                                 # MODIFIED — adds one new section between lines 19 and 21
```

No `src/`, `tests/`, `backend/`, `frontend/`, `api/`, `ios/`, or `android/` directories are touched. No new test files. No new scripts. No new templates.

**Structure Decision**: This is the **documentation-artifact** structure. The two file surfaces listed above are the complete blast radius.

## Implementation Waves

### Wave 1 — AIVSS Specification Research (parallel-capable, but waves sequenced due to data dependency)

| Task | Owner | FR | Output | Timebox |
|------|-------|-----|--------|---------|
| Confirm AIVSS canonical home and latest published version | web-researcher | FR-001 | Notes: URL, version number, publication date | ≤2h then escalate (PRD Risk R1) |
| Read v0.8 specification end-to-end (or latest observed version) | web-researcher | FR-001 | Notes: 10 AARFs, composite formula, severity bands (if defined), CVSS base version | Inline with above |
| Capture three research facts | web-researcher | FR-001 | Notes confirming: (a) AIVSS uses CVSS v4.0 (vs tachi CVSS 3.1 — a Conflict row), (b) AARS has no tachi analog (Gap row), (c) formula shape (AIVSS averaged, tachi weighted — Conflict row) | Inline |

**Wave 1 gate**: research notes exist and cover all four comparison axes (dimensions, formula, bands, CVSS version). If `gate === fail after 2 hours`, escalate to PM for PRD close-without-delivery (Risk R1 contingency).

### Wave 2 — ADR Authorship + SKILL.md Update + Conditional Issue

| Task | Owner | FR | Output |
|------|-------|-----|--------|
| Draft ADR-024 Context with three surfaces (A/B/C, each labeled Overlap/Gap/Conflict/No equivalent) | architect | FR-002 | ADR-024 Context section |
| Draft ADR-024 Alternatives Considered (≥3 options with Pros/Cons/effort/compliance value) | architect | FR-003 | ADR-024 Alternatives Considered section |
| Draft ADR-024 Decision + Rationale (five-criteria justification; worked examples if diverge) | architect | FR-004 | ADR-024 Decision + Rationale sections |
| Assemble ADR-024 file with frontmatter (Status: Accepted, Related ADRs: ADR-020, ADR-019, ADR-018) | architect | FR-005 | File committed at `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` |
| Add `## AIVSS Relationship` section to SKILL.md (80-200 words, between Domain Overview and Baseline-Aware Scoring Rules) | architect | FR-006 | SKILL.md modified |
| Verify decision-noun consistency between ADR and SKILL.md | architect | SC-007 | Grep check passes |
| File follow-on Issue (IF decision is Option A or B) with option-specific effort verbatim | product-manager | FR-007 | New Issue with `stage:discover` label and body referencing ADR-024 |
| Run zero-drift verification: `git diff main..feature-branch -- schemas/ scripts/ .claude/agents/ examples/` | code-reviewer | FR-008, SC-006 | Empty diff output |

**Wave 2 gate**: All SC-001 through SC-009 pass. If SC-006 (zero drift) fails, the offending files must be reverted — no file under `schemas/`, `scripts/`, `.claude/agents/`, or `examples/` may be modified.

## Agent Assignment Rationale

| Agent | Tasks | Rationale |
|-------|-------|-----------|
| **web-researcher** | FR-001 Wave 1 research | External-source discovery with authentication-posture handling for Risk R1; no tachi codebase knowledge required |
| **architect** | FR-002 through FR-006 | Trade-off analysis, ADR authorship, and skill update require deep understanding of tachi's existing scoring model and ADR precedents (ADR-019 through ADR-023). Architect is the canonical author for ADR artifacts in tachi |
| **product-manager** | FR-007 (conditional Issue filing) | Issue filing is a product-scoping activity — the PM determines ICE scope, title framing, and label. Not an engineering task |
| **code-reviewer** | FR-008 / SC-006 zero-drift verification at PR review | The `git diff` assertion is a code-review gate, not an authoring task |

**`senior-backend-engineer` is NOT assigned.** No task in this feature involves backend code changes. This is a deliberate exclusion reiterated from the PRD (Team-Lead Rec #1).

## Risk Posture

Inherited from PRD with plan-level notes:

| Risk | Plan-level mitigation |
|------|-----------------------|
| R1 AIVSS canonical home restructured | 2-hour timebox enforced in Wave 1 via a PM escalation checkpoint in tasks.md |
| R2 AIVSS is pre-1.0 | Already confirmed during `/aod.spec` research: v0.8 with public review period opening 2026-04-16. ADR-024 will explicitly document this and default toward Option C with a re-evaluation clause if the implementer's judgment points there |
| R3 Reviewer disagreement on recommended option | Up to 5 review iterations per review loop (Constitution-compatible); architect authority on technical decision; escalate to user if 5 iterations exhausted |
| R4 Mapping reveals a tachi composite bug | Out of scope — file a separate corrective Issue; no in-PRD fix |

## Post-Plan Deliverables

| Artifact | Location | Generated by | Status at plan completion |
|----------|----------|--------------|---------------------------|
| research.md | `specs/143-*/research.md` | `/aod.spec` Step 2 | Already created (pre-plan) |
| spec.md | `specs/143-*/spec.md` | `/aod.spec` Step 3 | Already approved (PM APPROVED) |
| checklists/requirements.md | `specs/143-*/checklists/` | `/aod.spec` Step 3.4 | Already PASS |
| plan.md | `specs/143-*/plan.md` | `/aod.project-plan` (this command) | Pending dual sign-off |
| tasks.md | `specs/143-*/tasks.md` | `/aod.tasks` (next command) | Not yet created |
| ADR-024 | `docs/architecture/02_ADRs/` | Wave 2 authorship | Deferred to `/aod.build` |
| SKILL.md update | `.claude/skills/tachi-risk-scoring/SKILL.md` | Wave 2 authorship | Deferred to `/aod.build` |
| Follow-on Issue (conditional) | GitHub Issues | Wave 2 product-manager task | Deferred to `/aod.build`; only filed if decision is Option A or B |

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

No constitutional violations. This section is intentionally empty.

---

**Plan status**: Ready for dual sign-off (PM + Architect) per Constitution Principle X.
