---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-11
    status: APPROVED
    notes: "Plan 082 is faithful to PRD 082 and Spec 082. All 5 user stories preserved and traceable to plan phases/sections. All 8 spec Out-of-Scope items respected. Schedule matches PRD 32h realistic midpoint. Principles III and X explicitly covered. Known debt (VI) justified per predecessor precedent. 3 LOW non-blocking observations in .aod/results/product-manager-plan.md"
  architect_signoff:
    agent: architect
    date: 2026-04-11
    status: APPROVED_WITH_CONCERNS
    notes: "9 of 11 PRD concerns fully resolved; 2 partial (E-4 plan text, A4 plan citation — both LOW, resolved upstream in spec/data-model). 4 LOW non-blocking: echo E-4 exit criterion in plan body, cite A4, formalize BaselineThreatsFile as data-model entity 8, add ADR-023 Future Work clause. MAESTRO boundary has strongest enforcement (4 points). Phase sequencing matches team-lead widened budget. Components/Data Flow/Tech Stack ready for extraction. Full review: .aod/results/architect-plan.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Threat Agent Skill References

**Branch**: `082-threat-agent-skill` | **Date**: 2026-04-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from [spec.md](./spec.md) (PM APPROVED_WITH_CONCERNS, 4 low-severity non-blocking items)

## Summary

Restructure 11 threat detection agents (6 STRIDE + 5 AI) from the self-contained inline-pattern shape to a lean agent + skill references shape, as a **sibling variant** of the proven control-analyzer methodology pattern. Detection agents use a single-point load (not phase-gated) semantics — one `**MANDATORY**: Read` directive at the start of a `## Detection Workflow` section. Each agent gets a companion `.claude/skills/tachi-<agent-name>/references/` directory containing a `detection-patterns.md` file with its externalized (and opportunistically enriched) detection vocabulary. Shared content consolidates additively into existing `.claude/skills/tachi-shared/references/` files.

**Technical approach**: File-and-directory refactor across `.claude/agents/tachi/` and `.claude/skills/tachi-*/` with zero code, zero schema, zero runtime dependency changes. Validation is content-level regression on 6 example architectures + byte-deterministic PDF re-baseline for 5 examples per ADR-021 (Feature 136 precedent). Prototype-first gate on 2 agents (spoofing + prompt-injection) in two sub-phases (1a refactor-only, 1b enrichment) before touching the other 9.

**Outcome**: All 17 tachi agents follow a single lean + skill references architectural pattern. Threat agent files drop from 1,680 total lines to ≤1,650 aggregate (tier-specific: STRIDE ≤120 each, AI ≤150 each, hard ceiling 180). Aggregate ≥22 new detection pattern categories cite primary sources (OWASP Top 10, OWASP LLM Top 10 v2025, OWASP AI Exchange, MITRE ATT&CK v15+, MITRE ATLAS v5.1+ with Oct 2025 agent techniques, CWE Top 25 2024, NIST AI 600-1). ADR-023 documents the detection sibling variant as the second lean-agent shape in tachi.

## Technical Context

**Language/Version**: N/A — this feature modifies markdown (`.claude/agents/tachi/*.md`, `.claude/skills/tachi-*/references/*.md`) and creates one ADR (`docs/architecture/02_ADRs/ADR-023-*.md`). No code changes to `scripts/*.py` or anything else. Python scripts (`scripts/tachi_parsers.py`, `scripts/extract-*.py`) remain stdlib-only per PRD 128 convention.

**Primary Dependencies**: None added. Primary sources (OWASP, CWE, MITRE ATT&CK, MITRE ATLAS, NIST) are cited by canonical URL inside reference files — no runtime fetch, no new HTTP client, no new package.

**Storage**: File system. 11 threat agent markdown files, 11 new companion skill directories with ≥1 reference file each (22-33 new reference files expected), additive edits to up to 4 existing shared reference files, 1 new ADR.

**Testing**: Two regression gates. (1) **Content-level diff** of `threats.md` on 6 example architectures (Phase 1a gate, Phase 1b gate, Phase 3 final) — checks finding count per category ±2, severity distribution ±1 per level, zero dropped findings. **Tolerance semantics (interpretation b, ratified in T021 Phase 1b joint ruling)**: the ±2 tolerance applies to finding counts produced by *pre-existing categories* only; new categories added by enrichment are not bounded by this tolerance. This distinction is load-bearing for T049 (Wave 14 aggregate enrichment floor check) and T050 (Wave 15 full regression gate) — a gate that capped total category count at +2 would make the feature's ≥2-per-agent enrichment floor structurally incompatible with the regression gate. (2) **Byte-deterministic PDF re-baseline** on 5 examples with `SOURCE_DATE_EPOCH=1700000000` per ADR-021 (same mechanism as Feature 136). No new test framework; existing `tests/scripts/` pytest baseline stays as-is.

**Target Platform**: Developer workstations running `/tachi.threat-model`, `/tachi.security-report`, and related commands under the Claude Code harness. No production deployment in the traditional sense — tachi is a toolkit template, not a hosted service.

**Project Type**: Agent/skill refactor inside a documentation + tooling template. No frontend, no backend, no database. "Single project" template slot is closest fit but nothing about the template's default source tree (`src/`, `tests/`) applies — the real layout is `.claude/agents/tachi/`, `.claude/skills/tachi-*/`, `docs/architecture/`, `specs/082-*/`.

**Performance Goals**: Per-invocation agent context reduction is the target. Each threat agent's loaded file drops from 113-201 lines (baseline) to ≤120/≤150 lines (tier target). Skill reference files are loaded on-demand via `**MANDATORY**: Read` directive — detection pattern reference files are typically 60-300 lines each, loaded once per agent invocation. Per PRD 029, Chroma "Context Rot" study (July 2025) measured 30% instruction-following accuracy improvement from context reduction — this refactor extends that benefit to the threat agent tier.

**Constraints**:
- No new runtime dependencies (C1 in spec).
- No changes to agent invocation interface — orchestrator dispatch rules unchanged (C2).
- Reference files are markdown, not YAML/JSON (C3).
- `SOURCE_DATE_EPOCH=1700000000` byte-determinism for 5 non-agentic example PDFs (C4).
- Schema `finding.yaml` stays at v1.3 (C5).
- One directory per agent — `tachi-<agent-name>/`, no tier prefix (C6).
- Prototype-first gate is hard requirement — max 2 gate iterations before escalation (C7).
- Per-agent commit discipline (C8).
- Additive-only shared reference edits (C9).
- Parallel wave constraint: per-agent parallelizes, shared ref consolidation does not (C10).

**Scale/Scope**: 11 threat agents, 11 companion skill directories, 22-33 new reference files, additive edits to 1-4 existing shared reference files, 1 new ADR, regeneration of 6 example `threats.md` files + 5 byte-deterministic PDFs + 6 downstream artifacts per example (risk-scores, compensating-controls, threat-report, infographic, report.pdf). Total PRD estimate: 32h realistic midpoint (team-lead review bounds: 22h optimistic, 32h realistic, 45h pessimistic).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Principles applied from [.aod/memory/constitution.md](../../.aod/memory/constitution.md):

### Principle I — General-Purpose Architecture ✅ COMPLIANT

**Check**: Core components domain-agnostic, no hardcoded assumptions about project types.

**Analysis**: Detection pattern reference files contain security-specific content by definition (they describe how to detect threats) but the **architectural pattern** (lean agent + `**MANDATORY**: Read` + companion skill directory) is domain-agnostic. The same pattern could be used for any detection agent in any domain. Pattern content is domain-specific; pattern shape is not. Compliant.

### Principle III — Backward Compatibility ✅ COMPLIANT (with protected path)

**Check**: 100% backward compatibility with local `.aod/` file workflows; no forced migrations.

**Analysis**: Finding schema `v1.3` is unchanged (C5). Orchestrator dispatch rules are unchanged (C2). The agent-to-orchestrator interface is byte-identical post-refactor. The only backward-compat risk is shared reference consolidation affecting infrastructure agents (orchestrator, risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler). **Mitigation**: FR-5 enforces additive-only shared reference edits; R3 contingency (new `tachi-shared-threat/` directory) if a breaking conflict is found; FR-17 explicitly re-baselines the 5 byte-deterministic PDFs as an expected Phase 3 outcome. Compliant.

### Principle VI — Testing Excellence ⚠️ COMPLIANT WITH KNOWN DEBT

**Check**: Unit + integration + E2E + performance tests with ≥80% unit coverage.

**Analysis**: tachi has no automated test suite for threat agents today (acknowledged in spec "Out of Scope"). This feature does not introduce automated threat-agent tests — it relies on the content-level regression gate (6 example architectures, finding count delta) and manual reviewer checks. This is consistent with PRDs 029, 075, 078, 084, 091, 104, 128, 136 — all used the same example-regression approach. Adding a detection-pattern coverage test suite is deferred to a future PRD (out of scope per spec). **Justification**: Agent markdown is configuration, not executable code; the "test" is the pipeline running successfully on example architectures. Per-agent pytest tests would require mocking the Claude Code agent invocation layer, which doesn't exist. Declared as known debt in "Complexity Tracking" below.

### Principle VII — Definition of Done ✅ COMPLIANT

**Check**: All DoD steps verified before marking complete (pushed to production, tested, user-validated).

**Analysis**: DoD for this feature means (a) PR merged to main, (b) content-level regression passes on all 6 examples, (c) 5 byte-deterministic PDFs re-baseline cleanly. "User-validated" corresponds to confirming the refactored pipeline produces equivalent-or-better output on real architectures — the 6 examples are the validation surface. CHANGELOG entry generated via release-please on merge (Feature 086 precedent). Compliant.

### Principle VIII — Observability & Root Cause Analysis ✅ COMPLIANT (strengthened)

**Check**: Structured logging, clear error messages, graceful degradation.

**Analysis**: Edge case in spec explicitly requires that a missing/malformed skill reference file produces a **clear, actionable error message** (not silent fallback) — consistent with ADR-022 fail-loud CLI prerequisite posture. This is actually *strengthening* observability compared to the current inline-pattern state (where missing patterns are silent). Compliant and improving.

### Principle IX — Git Workflow & Feature Branching ✅ COMPLIANT

**Check**: Feature branches only, conventional commits, PR review, no force push.

**Analysis**: Working on branch `082-threat-agent-skill` (script created, script chose truncated name from long PRD topic — functionally equivalent to `082-threat-agent-skill-references`). Each of the 11 agent extractions will be a separate commit or commit cluster per FR-15 to enable per-agent revert. PR will pass through code review. Compliant.

### Principle X — Product-Spec Alignment & Architecture Review ✅ COMPLIANT

**Check**: PRD → spec → plan with PM + Architect + Team-Lead sign-offs at each artifact.

**Analysis**: PRD 082 approved 2026-04-11 with triple sign-off (PM APPROVED, architect + team-lead APPROVED_WITH_CONCERNS). Spec 082 PM-approved 2026-04-11 (this plan's prerequisite). Plan requires PM + Architect dual sign-off; tasks will require triple sign-off. All gates active. Compliant.

### Gate Verdict

**PASS WITH ONE KNOWN DEBT ITEM** — Principle VI (automated threat-agent test coverage) is declared debt, consistent with predecessor feature precedent, justified in Complexity Tracking below.

## Project Structure

### Documentation (this feature)

```
specs/082-threat-agent-skill/
├── spec.md                   # Feature specification (PM approved)
├── plan.md                   # This file (PM + Architect sign-off pending)
├── research.md               # Research phase output (already written during /aod.spec)
├── data-model.md             # File entity definitions (Phase 1)
├── quickstart.md             # Developer orientation guide (Phase 1)
├── checklists/
│   └── requirements.md       # Spec quality checklist
└── tasks.md                  # Task breakdown (/aod.tasks output — not yet created)
```

**Note**: This feature does NOT produce a `contracts/` directory because there are no API contracts to generate. The agent-to-orchestrator interface is a file-system contract (the output shape of `threats.md` findings), not an HTTP/RPC contract. It remains unchanged.

### Source Code (repository root — affected paths)

```
.claude/
├── agents/tachi/             # 11 threat agent files to restructure (in-place edits)
│   ├── spoofing.md           # STRIDE — Phase 1 prototype (113 → ≤120 lines)
│   ├── tampering.md          # STRIDE — Phase 2a (126 → ≤120 lines)
│   ├── repudiation.md        # STRIDE — Phase 2a (124 → ≤120 lines)
│   ├── info-disclosure.md    # STRIDE — Phase 2a (128 → ≤120 lines)
│   ├── denial-of-service.md  # STRIDE — Phase 2a (141 → ≤120 lines)
│   ├── privilege-escalation.md # STRIDE — Phase 2a (136 → ≤120 lines)
│   ├── prompt-injection.md   # AI — Phase 1 prototype (167 → ≤150 lines)
│   ├── data-poisoning.md     # AI — Phase 2b (171 → ≤150 lines)
│   ├── model-theft.md        # AI — Phase 2b (188 → ≤150 lines)
│   ├── tool-abuse.md         # AI — Phase 2b (185 → ≤150 lines)
│   └── agent-autonomy.md     # AI — Phase 2b (201 → ≤150 lines)
│
└── skills/                   # NEW: 11 companion skill directories + additive edits to shared
    ├── tachi-spoofing/references/          # NEW — Phase 1 prototype
    ├── tachi-tampering/references/         # NEW — Phase 2a
    ├── tachi-repudiation/references/       # NEW — Phase 2a
    ├── tachi-info-disclosure/references/   # NEW — Phase 2a
    ├── tachi-denial-of-service/references/ # NEW — Phase 2a
    ├── tachi-privilege-escalation/references/  # NEW — Phase 2a
    ├── tachi-prompt-injection/references/  # NEW — Phase 1 prototype
    ├── tachi-data-poisoning/references/    # NEW — Phase 2b
    ├── tachi-model-theft/references/       # NEW — Phase 2b
    ├── tachi-tool-abuse/references/        # NEW — Phase 2b
    ├── tachi-agent-autonomy/references/    # NEW — Phase 2b
    └── tachi-shared/references/            # EXISTING — additive edits in Phase 2c only
        ├── severity-bands-shared.md        # 110 lines — unchanged (already producer-oriented)
        ├── finding-format-shared.md        # 177 lines — APPEND producer section
        ├── stride-categories-shared.md     # 146 lines — append threat-agent Read registrations (consumers frontmatter + validated use)
        └── maestro-layers-shared.md        # 213 lines — unchanged (FR-9 boundary)

docs/architecture/
├── 00_Tech_Stack/README.md   # EDIT — agent inventory section updated to reference sibling variant
└── 02_ADRs/
    └── ADR-023-threat-agent-skill-references-pattern.md  # NEW — created by Phase 1

examples/                     # REGENERATED outputs (Phase 3)
├── web-app/threats.md + security-report.pdf.baseline     # content + byte re-baseline
├── microservices/threats.md + security-report.pdf.baseline
├── ascii-web-api/threats.md + security-report.pdf.baseline
├── mermaid-agentic-app/threats.md + security-report.pdf.baseline
├── free-text-microservice/threats.md + security-report.pdf.baseline
└── agentic-app/threats.md    # content regenerated; PDF NOT byte-deterministic (Feature 128 convention)
```

**Structure Decision**: This feature operates entirely within `.claude/agents/tachi/`, `.claude/skills/tachi-*/`, `docs/architecture/02_ADRs/`, and the regenerated `examples/*/` outputs. No changes to `scripts/`, `schemas/`, `templates/`, or `tests/`. The template's default source tree (`src/`, `tests/`) does not apply — this is an agent + documentation refactor, not application code.

## Phase 0 — Research (complete)

Phase 0 research was conducted during `/aod.spec` and persisted to [research.md](./research.md). Key decisions carried into this plan:

**Decision 1 — Sibling variant pattern (not phase-gated)**
- **Rationale**: Detection agents have a single-pass shape (match triggers → apply patterns → emit findings) unlike control-analyzer's 6-phase methodology pipeline. A `**MANDATORY**: Read` directive at detection start is the natural load point — forcing a multi-phase structure onto detection agents would be the wrong abstraction.
- **Alternatives considered**: (a) Full methodology pattern with 3-6 phases — rejected as inappropriate shape; (b) Frontmatter-only registration with no Read directive — rejected because it would rely on implicit tool loading unsupported by the current Claude Code harness.
- **Recorded in**: FR-1, FR-16 (ADR-023).

**Decision 2 — Tier-specific line targets (STRIDE ≤120, AI ≤150)**
- **Rationale**: Per architect review §3, a single 150-line target is too loose because STRIDE agents have smaller baselines (113-141) than AI agents (167-201). Tier-specific targets produce tighter outcomes and a better success metric story.
- **Alternatives considered**: (a) Flat 150 — too loose for STRIDE; (b) Flat 90 — too tight for AI; (c) No target — risk of token-cost drift.
- **Recorded in**: FR-10, SC-002.

**Decision 3 — Aggregate enrichment floor (≥22 total, de-scopable per agent)**
- **Rationale**: Per team-lead review §5, bundling refactor + enrichment creates timeline risk if enrichment research runs slow on any one agent. Aggregate floor protects the outcome metric while allowing per-agent flexibility.
- **Alternatives considered**: (a) Strict ≥2 per agent — blocks architectural refactor if any single agent's enrichment stalls; (b) No floor — dilutes the enrichment outcome to the point where M3 is meaningless.
- **Recorded in**: FR-7, User Story 5, SC-006.

**Decision 4 — Phase 1 sub-phasing (1a refactor-only, 1b enrichment)**
- **Rationale**: Per architect review C1, bundling refactor + enrichment into one prototype phase mixes two independent risk vectors (does the shape work? do the new patterns help?). Sub-phasing lets each risk be validated on its own signal.
- **Alternatives considered**: (a) Single-phase prototype — harder to diagnose failures; (b) No prototype — rejected outright (violates risk mitigation for R1).
- **Recorded in**: FR-12, FR-13, User Story 4.

**Decision 5 — Shared reference edits are additive-only (policy, not hope)**
- **Rationale**: Per architect review §4, `tachi-shared/references/` is in active production use by 6 infrastructure agents. Any modification to existing content risks silently breaking the infra tier. Declaring additive-only as a default posture (instead of a contingency) reduces R3 to near-zero.
- **Alternatives considered**: (a) Modify existing content freely and hope — rejected as fragile; (b) Create `tachi-shared-threat/` from scratch — rejected as premature (contingency path).
- **Recorded in**: FR-5, C9, C10.

**Decision 6 — Byte-deterministic PDF re-baseline is in-scope (R6)**
- **Rationale**: Per team-lead review §6, shared reference edits flow through to infra agents and therefore to the report pipeline. Per ADR-021 determinism, the 5 byte-identical PDFs will diff even if content is equivalent. Feature 136 set the precedent (re-baselined 5 PDFs without incident after `maestro-layers-shared.md` edit).
- **Alternatives considered**: (a) Leave baselines stale — breaks the byte-determinism test; (b) Skip shared ref consolidation to avoid re-baseline — defeats the refactor's purpose; (c) Create `tachi-shared-threat/` instead — contingency path only.
- **Recorded in**: FR-17, SC-008, Edge Cases.

**Decision 7 — Primary source set for enrichment**
- **Rationale**: Web-researcher confirmed (research.md §3) the approved primary source set (OWASP Top 10, OWASP LLM Top 10 v2025, OWASP AI Exchange CC0, MITRE ATT&CK v15+, MITRE ATLAS v5.1+ Oct 2025, CWE Top 25 2024, NIST AI 600-1) contains ≥33 candidate new categories — well above the ≥22 aggregate floor. Zero licensing friction.
- **Alternatives considered**: (a) SANS, ENISA, ISO 27000 series — rejected as less granular for detection-signature use; (b) Commercial TI vendors — rejected on licensing grounds.
- **Recorded in**: FR-8, research.md §3.

No NEEDS CLARIFICATION markers remain. Phase 0 is complete.

## Phase 1 — Design & Contracts

### 1.1 Agent file redesign (target structure)

Post-refactor, each threat agent file contains the following 5 sections in order (AI-tier agents append an inline `## Example Findings` section as a 6th section per Q7 default):

1. **YAML frontmatter** (5-10 lines) — `name:`, `description:`, `model: sonnet`, `tools: [Read, Glob, Grep]`. The `model:` field is already set on all 11 agents today; preserved per FR-11.
2. **Metadata YAML block** (~15 lines) — `category:`, `threat_class:`, `dfd_targets:`, `owasp_references:`, `output_schema:`. Unchanged from today.
3. **`## Purpose`** (3-5 lines) — Single-paragraph purpose statement. Shortened from today's 5-line purpose narrative.
4. **`## Skill References`** (10-15 lines) — Markdown table with columns: `Reference | File | Load When | Purpose`. At minimum two rows: (a) companion detection patterns `.claude/skills/tachi-<agent-name>/references/detection-patterns.md` loaded always at detection start, (b) shared finding format `.claude/skills/tachi-shared/references/finding-format-shared.md` loaded always at detection start. Additional rows may reference `severity-bands-shared.md`, `stride-categories-shared.md`, or other per-agent references as the agent's needs dictate.
5. **`## Detection Workflow`** (20-40 lines) — Starts with a single `**MANDATORY**: Read .claude/skills/tachi-<agent-name>/references/detection-patterns.md — load before applying patterns to components.` directive. Follows with step-by-step detection logic: (i) iterate dispatched components, (ii) match against loaded patterns, (iii) construct findings per shared format, (iv) emit to orchestrator. No inline pattern tables — those live in the reference file.

**Sections intentionally NOT in the canonical shape**: The pre-refactor source does not include dedicated `## Empty Results Handling` or `## Output Handoff` sections in any of the 11 threat agent files — a pre-refactor source audit (T015 Architect review, [.aod/results/architect-t015-phase-1a-gate.md](../../.aod/results/architect-t015-phase-1a-gate.md)) found neither section existed at level 2. Empty-results behavior is inherited from the Detection Workflow component-iteration step (zero components match → zero findings produced); handoff semantics are owned by the orchestrator Phase 3 Table Assembly contract per ADR-020 (agents are pulled from by the orchestrator, they do not push). An earlier draft of this plan listed these as "preserve as-is from today" sections; the "from today" claim was inaccurate and that item is retracted per T015 Option A ruling.

**Tier target enforcement**: STRIDE agents ≤120 lines total (stretch ≤90). AI agents ≤150 lines total (stretch ≤130). Hard ceiling 180 for any threat agent. AI agents retain in-agent example findings (Q7 default) for LLM comprehension; if this pushes an AI agent over tier target, Phase 1b revisits the decision.

### 1.2 Companion skill directory layout (target)

Each `.claude/skills/tachi-<agent-name>/references/` directory contains at minimum:

- **`detection-patterns.md`** — The agent's externalized detection vocabulary plus enrichment. Structure:
  - Frontmatter YAML: `name`, `description`, `consumers: [tachi-<agent-name>]`, `last_updated: 2026-04-11`
  - `## Overview` (3-5 lines) — What this reference describes and when the agent consumes it
  - `## Pattern Category 1: <name>` — First pattern category (existing or enriched) with indicators, primary source citation, example
  - `## Pattern Category 2: <name>` — Second pattern category
  - ...
  - `## Primary Sources` — Consolidated citation list (OWASP/CWE/MITRE/NIST with URLs)

- **Optional siblings per agent** (created only when needed):
  - `finding-field-guidance.md` — Agent-specific finding field construction hints (only if the shared producer section in `finding-format-shared.md` is insufficient)
  - `example-findings.md` — AI agents' example findings, migrated here only if the in-agent placement pushes the agent over tier target (Q7 contingency)

The detection pattern reference file **MUST be self-documenting per FR-4**: a first-time contributor reading `detection-patterns.md` alone (without the parent agent file) must understand the threat category, the patterns, and the rationale.

### 1.3 Shared reference additive edits (Phase 2c)

| Shared File | Current Line Count | Additive Edit | Expected Delta |
|-------------|--------------------|---------------| ---------------|
| `severity-bands-shared.md` | 110 | None (already producer-oriented; threat agents read it unchanged) | +0 |
| `finding-format-shared.md` | 177 | **APPEND** new section `## For Threat Agents (Producers)` with: ID prefix assignment table (producer view), field construction guidance, risk_level computation example, reference linking conventions | +40 to +60 |
| `stride-categories-shared.md` | 146 | None required — content is already category-definition and the frontmatter already lists 11 threat agents as consumers (aspirationally). Phase 2a/2b reads it, making the frontmatter match reality. | +0 |
| `maestro-layers-shared.md` | 213 | **FORBIDDEN** — FR-9 prohibits threat agents from referencing MAESTRO content. MAESTRO inheritance stays orchestrator-owned. | N/A |

Net shared reference delta: +40 to +60 lines in `finding-format-shared.md` only. One file, one serial wave (Phase 2c), single writer.

### 1.4 ADR-023 target outline

`docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` (NEW, ~150-200 lines):

- **Status**: Draft in Phase 1; Accepted by end of Phase 1 gate.
- **Context**: PRD 029/075/078 established the lean + skill references pattern on 6 infrastructure agents. The 11 threat detection agents remained on the self-contained inline pattern. This ADR records the decision to extend the lean pattern — as a sibling variant — to detection agents during PRD 082.
- **Decision 1 (Sibling variant)**: Detection agents use a **single-point load** at the start of a `## Detection Workflow` section. They do NOT have phase-gated loads because they do not have methodology phases. The section name `## Detection Workflow` (not `## Phase Workflow`) is mandatory to avoid implying multi-phase structure.
- **Decision 2 (MAESTRO boundary)**: MAESTRO layer inheritance runs entirely in orchestrator Phase 3 Table Assembly. Threat agents MUST remain MAESTRO-agnostic. A contributor who adds MAESTRO references to any threat agent reference file MUST have the change rejected in code review.
- **Decision 3 (Additive-only shared ref edits)**: Edits to `.claude/skills/tachi-shared/references/*.md` files are additive-only by default. Existing sections are byte-identical pre/post edit. New sections are appended with new `## ` headings. Escalation path: if existing content must change, create a new file alongside the existing one.
- **Decision 4 (Producer/consumer audience in shared refs)**: Shared reference files may have two audiences. `finding-format-shared.md` was originally a consumer-oriented validation spec (for orchestrator / risk-scorer); under this ADR it gains a `## For Threat Agents (Producers)` section for producer audience. The two audiences live in the same file via separate sections.
- **Consequences**: (a) Two lean-agent shapes now documented in tachi — methodology (phase-gated, control-analyzer variant) and detection (single-point, threat agent variant). (b) Future threat detection enrichment is a one-file edit in a reference file, not an agent edit. (c) Shared reference edits must be reviewed by infra agent owners (not just threat agent owners) because the blast radius spans both tiers.
- **References**: ADR-014 (optional external APIs), ADR-020 (deterministic MAESTRO classification), ADR-021 (SOURCE_DATE_EPOCH determinism), ADR-022 (first CLI prerequisite ADR precedent for the ADR-NNN sequence). PRD 082, Feature 075, Feature 078.

### 1.5 Data model (file entities)

Entity relationships for this refactor live in [data-model.md](./data-model.md) (generated in Phase 1). Summary:

```
ThreatAgentFile (1) ──owns──> (1) CompanionSkillDirectory
                                         │
                                         └──contains──> (1..N) ReferenceFile
                                                                  │
                                                                  └──has──> (0..N) EnrichmentCategory
                                                                                      │
                                                                                      └──cites──> (1..N) PrimarySource

ThreatAgentFile (11) ──reads──> (1..4) SharedReferenceFile
                                         │
                                         └──owned_by──> (1) tachi-shared skill directory
```

Key invariants enforced in validation:
- Each `ThreatAgentFile` has exactly one `CompanionSkillDirectory` (1:1).
- Each `CompanionSkillDirectory` contains ≥1 `ReferenceFile` (typically `detection-patterns.md`).
- Each `EnrichmentCategory` cites ≥1 `PrimarySource` (FR-8 / SC-007).
- Aggregate `EnrichmentCategory` count across all 11 agents ≥22 (FR-7 / SC-006).
- `ThreatAgentFile` NEVER references `maestro-layers-shared.md` (FR-9 / SC-010).

### 1.6 Contracts (N/A)

No API contracts. The agent-to-orchestrator interface is a finding list emitted via markdown/SARIF output, not an HTTP/RPC contract. The interface is defined by `schemas/finding.yaml` (v1.3) which stays unchanged (C5). No OpenAPI spec is produced.

### 1.7 Quickstart (developer orientation)

A [quickstart.md](./quickstart.md) is generated alongside this plan to give contributors a 10-minute orientation to the new pattern — useful for reviewers during Phase 1 gate, for the Phase 2 senior-backend-engineer implementing the rollout, and for future contributors adding new detection patterns.

### 1.8 Agent context update

Run `.aod/scripts/bash/update-agent-context.sh claude` to add Feature 082 context to `CLAUDE.md`'s "Recent Changes" section. Script detects Claude Code and updates the project CLAUDE.md with the new architectural variant.

## Components

*Component view of the refactored threat agent tier. This section is extracted by the `/aod.project-plan` skill into `docs/architecture/01_system_design/README.md` under heading `### Feature 082: threat-agent-skill`.*

### C1: Threat Agent File (11 instances)

- **Responsibility**: Orchestration-only markdown file invoked by orchestrator dispatch. Loads domain knowledge on-demand from companion skill directory; constructs findings in the shared format; emits findings to orchestrator.
- **Interface**: Input — component name + DFD element type from orchestrator. Output — finding list in `schemas/finding.yaml` v1.3 format.
- **Dependencies**: (a) Companion skill directory `tachi-<agent-name>/references/`; (b) shared skill directory `tachi-shared/references/` for finding format and severity bands; (c) orchestrator for invocation and finding aggregation.
- **Line target**: STRIDE ≤120, AI ≤150, hard ceiling 180.
- **Location**: `.claude/agents/tachi/<agent-name>.md`

### C2: Companion Skill Directory (11 instances)

- **Responsibility**: Per-agent domain knowledge store. Holds detection patterns, optional example findings, optional finding field guidance. Loaded on-demand by the parent agent file via `**MANDATORY**: Read` directive.
- **Interface**: File-system directory readable by the Claude Code `Read` tool. Reference files are markdown.
- **Dependencies**: Parent threat agent file reads from this directory; no other agent reads from it.
- **Line target**: 60-300 lines per reference file, typically 100-200. Total per directory: 150-500 lines.
- **Location**: `.claude/skills/tachi-<agent-name>/references/`

### C3: Shared Skill Directory (1 instance, already exists)

- **Responsibility**: Cross-agent shared content. Severity bands, finding format, STRIDE category definitions, MAESTRO layer taxonomy. Consumed by multiple agents — infrastructure tier (6 agents) already consumes it; threat tier (11 agents) starts consuming it in Phase 2c.
- **Interface**: File-system directory, markdown reference files. Consumed via `**MANDATORY**: Read` directives across the agent fleet.
- **Dependencies**: Read-only from any individual agent's perspective. Edits go through Phase 2c single-writer wave (C10) and are additive-only (C9).
- **Blast radius**: Any edit to a shared reference file can affect all 17 agents (threat + infra). Re-baseline of 5 byte-deterministic PDFs is the expected outcome of any edit (FR-17 / R6).
- **Location**: `.claude/skills/tachi-shared/references/` (existing: 4 files, 646 lines)

### C4: Orchestrator Dispatch (unchanged)

- **Responsibility**: Phase 1 component inventory; Phase 2 dispatch to threat agents; Phase 3 Table Assembly (including MAESTRO layer inheritance for each finding). Orchestrator is the only tachi agent that knows about MAESTRO; it remains so after this refactor (FR-9).
- **Interface**: Calls each threat agent with component + DFD element type; receives finding list; merges findings into master `threats.md`.
- **Dependencies**: Reads its own skill directory `tachi-orchestration/references/` (dispatch rules, classification rules, MAESTRO-layers-shared).
- **Impact of Feature 082**: Zero. Orchestrator dispatch logic and interface are unchanged (C2). The refactor is transparent to orchestrator.
- **Location**: `.claude/agents/tachi/orchestrator.md` (not touched by this feature)

### C5: ADR-023 (new architectural decision record)

- **Responsibility**: Document the detection sibling variant of the lean + skill references pattern. Record decisions on load-point semantics, MAESTRO boundary, additive-only shared-ref edits, and consumer/producer audience separation in shared files.
- **Interface**: Read by future contributors adding new threat detection patterns. Referenced from `docs/architecture/00_Tech_Stack/README.md` agent inventory section.
- **Location**: `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` (NEW, created in Phase 1)

## Data Flow

*This section is extracted into `docs/architecture/01_system_design/README.md`.*

### Pre-refactor data flow (baseline)

```
User
  │
  └──▶ /tachi.threat-model
        │
        └──▶ orchestrator.md
              │
              ├──▶ Reads dispatch-rules.md, classification-rules.md (from tachi-orchestration skill)
              │
              ├──▶ Phase 1: Component inventory + MAESTRO classification
              │
              ├──▶ Phase 2: Dispatch to 11 threat agents (in parallel per component)
              │      │
              │      ├──▶ spoofing.md (113 lines, inline patterns)
              │      │    └─▶ Detection patterns + finding template + OWASP 3x3 matrix (all inline)
              │      │    └─▶ Emit finding list
              │      ├──▶ tampering.md (126 lines, inline) → finding list
              │      ├──▶ ... (9 more threat agents, each with inline everything)
              │      └──▶ agent-autonomy.md (201 lines, inline) → finding list
              │
              └──▶ Phase 3: Table Assembly — merge findings, inherit MAESTRO layer per finding
                    │
                    └──▶ Write threats.md
```

### Post-refactor data flow (Feature 082 target)

```
User
  │
  └──▶ /tachi.threat-model
        │
        └──▶ orchestrator.md  (UNCHANGED — same file, same logic)
              │
              ├──▶ Reads dispatch-rules.md, classification-rules.md (UNCHANGED)
              │
              ├──▶ Phase 1: Component inventory + MAESTRO classification (UNCHANGED)
              │
              ├──▶ Phase 2: Dispatch to 11 threat agents (UNCHANGED interface)
              │      │
              │      ├──▶ spoofing.md (≤120 lines, LEAN)
              │      │    └─▶ **MANDATORY**: Read tachi-spoofing/references/detection-patterns.md
              │      │    └─▶ **MANDATORY**: Read tachi-shared/references/finding-format-shared.md
              │      │    └─▶ Apply patterns to component
              │      │    └─▶ Construct findings using shared format producer section
              │      │    └─▶ Emit finding list
              │      │
              │      ├──▶ tampering.md (≤120 lines, LEAN) → same pattern → finding list
              │      ├──▶ ... (9 more threat agents, each lean)
              │      └──▶ agent-autonomy.md (≤150 lines, LEAN) → same pattern → finding list
              │
              └──▶ Phase 3: Table Assembly — merge findings, inherit MAESTRO layer per finding
                    │                                          (UNCHANGED — MAESTRO still orchestrator-owned)
                    └──▶ Write threats.md
```

**Key observation**: The input (user command) and output (`threats.md`) are content-equivalent pre/post. The only change is the internal shape of each threat agent — where its detection vocabulary lives. This is why content-level regression on 6 example architectures (SC-005) is sufficient to validate the refactor, and why the orchestrator doesn't need any changes (C2).

### Shared reference consumption flow (Phase 2c edits propagate)

```
Phase 2c edit to finding-format-shared.md (APPEND "## For Threat Agents (Producers)" section)
                                              │
                ┌─────────────────────────────┴──────────────────────────────┐
                │                                                            │
                ▼                                                            ▼
     11 threat agents                                           6 infrastructure agents
     (NEW consumers, gain producer guidance)                    (EXISTING consumers, unchanged section)
                │                                                            │
                │                                                            │
     Same finding output shape                                     Same validation logic
     (schemas/finding.yaml v1.3)                                   (schemas/finding.yaml v1.3)
                │                                                            │
                ▼                                                            ▼
     Content equivalent to pre-refactor                           Content equivalent to pre-refactor
                │                                                            │
                └──────────────────┬─────────────────────────────────────────┘
                                   │
                                   ▼
                       threats.md content unchanged
                                   │
                                   ▼
                       BUT: PDFs diff at byte level (ADR-021 determinism)
                                   │
                                   ▼
                       Phase 3 re-baseline with SOURCE_DATE_EPOCH=1700000000
                                   │
                                   ▼
                       New byte-deterministic baselines committed (FR-17, SC-008)
```

## Tech Stack

*This section is extracted into `docs/architecture/01_system_design/README.md`.*

- **Agent runtime**: Claude Code (Anthropic) via the `.claude/agents/tachi/` markdown convention. No code, no framework, no language choice — agent files are configuration consumed by the Claude Code harness at invocation time.
- **Skill loading**: On-demand `Read` tool invocation from within agent files via `**MANDATORY**: Read <path>` directives. File-system reads only; no network, no daemon, no index.
- **Output format**: Finding list serialized to markdown (`threats.md`) and SARIF 2.1.0 (`threats.sarif`) by the orchestrator. Schema governed by `schemas/finding.yaml` v1.3 (unchanged by this feature).
- **Pipeline scripts**: `scripts/tachi_parsers.py`, `scripts/extract-*.py` — Python 3.11+ stdlib-only (PRD 128 convention). Unchanged by this feature.
- **PDF generation**: Typst + `@mermaid-js/mermaid-cli` (ADR-022 hard prerequisites). Unchanged by this feature, but 5 PDFs are re-baselined in Phase 3 (FR-17).
- **Byte-determinism**: `SOURCE_DATE_EPOCH=1700000000` environment variable per ADR-021. Applied to 5 non-agentic example PDF regenerations.
- **CI**: GitHub Actions workflow `.github/workflows/tachi.threat-model.yml` runs example regeneration smoke tests. Unchanged by this feature (validation continues to pass on 6 examples).
- **Release management**: release-please (Feature 086) auto-cuts a version tag on merge to main. CHANGELOG entry generated from commit messages and PR title.
- **Primary source citations** (referenced only, never runtime-fetched): OWASP Top 10 (CC BY 3.0), OWASP LLM Top 10 v2025 (CC BY-SA 4.0), OWASP AI Exchange (CC0), MITRE ATT&CK v15+ (free w/ attribution), MITRE ATLAS v5.1+ (free w/ attribution), CWE Top 25 2024 (royalty-free), NIST AI 600-1 (US Federal public domain).

## Re-evaluate Constitution Check (post-Phase 1)

After completing Phase 1 design (sections 1.1-1.8 above), re-check all principles:

- **Principle I (General-Purpose)**: ✅ COMPLIANT. Pattern shape remains domain-agnostic; content is security-specific by the nature of the refactor subject.
- **Principle III (Backward Compat)**: ✅ COMPLIANT. Section 1.3 confirms shared reference edits are additive-only with a single net change to one file. Orchestrator interface unchanged.
- **Principle VI (Testing)**: ⚠️ COMPLIANT WITH KNOWN DEBT (declared in Complexity Tracking). No regression in test posture — the 6-example content-level gate is the same surface PRDs 029/075/078/084/091/104/128/136 used.
- **Principle VII (DoD)**: ✅ COMPLIANT. DoD checklist in Phase 3 covers all 3 steps (deployed via PR merge, tested via regression gates, user-validated via example output review).
- **Principle VIII (Observability)**: ✅ COMPLIANT and strengthened — missing skill reference files now produce clear errors instead of silent fallback.
- **Principle IX (Git Workflow)**: ✅ COMPLIANT. Per-agent commit discipline in Section 1 and FR-15.
- **Principle X (Product-Spec Alignment)**: ✅ COMPLIANT. Dual sign-off gate operational.

**Gate verdict post-Phase 1**: PASS. No new violations introduced by Phase 1 design. One pre-existing known debt item carried forward from pre-Phase 1 (automated threat-agent test coverage — justified below).

## Complexity Tracking

*Filled to justify Principle VI debt carry-forward.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| No automated pytest coverage for threat agents (Principle VI) | Threat agents are markdown configuration consumed by the Claude Code harness at invocation time. They have no executable surface to unit-test. "Testing" the refactor means running the pipeline end-to-end on example architectures, which is what the content-level regression gate does. | (a) Mock the Claude Code agent invocation layer in pytest — rejected because no mock exists, building one is a multi-PRD undertaking, and it wouldn't validate the real LLM-driven behavior; (b) Skip this feature until threat agent tests exist — rejected because PRDs 029/075/078/084/091/104/128/136 all shipped under the same debt, and deferring would block the architectural consistency outcome indefinitely; (c) Write shell-based smoke tests — this is essentially what the 6-example regeneration gate already is. |

This debt is declared on every refactor-class PRD in tachi and is a known project-level position: threat agent automated testing requires a Claude Code mock layer that does not exist and is out of scope for any single feature PRD. It is **not** a new risk introduced by Feature 082.

## Phase Schedule (informational — mirrors spec Implementation Sequencing)

### Phase 0: Preparation (2-3h)

- Web-researcher produces per-agent enrichment briefs from primary source set (FR-8)
- Architect creates ADR-023 draft (FR-16)
- Pre-refactor baseline capture: commit pre-refactor `threats.md` for all 6 examples to enable Phase 1 and Phase 3 diffs

### Phase 1: Prototype (5-8h, team-lead widened)

- **Phase 1a** (2-3h): Extract spoofing + prompt-injection to lean agents + companion skill directories with pre-refactor patterns verbatim. Zero new pattern categories. Re-run pipeline on all 6 examples; gate: content-level regression passes with ±0 new findings.
- **Phase 1b** (2-4h): Add ≥2 new pattern categories per prototype agent citing primary sources. Re-run pipeline; gate: FR-13 exit criteria met; at least 1 new finding emerges on the prototype agents' example surface.
- **Phase 1 combined gate** (1h): team-lead + architect joint review; explicit approval required before Phase 2. Max 2 iterations before escalation.

### Phase 2: Rollout (14-20h)

- **Phase 2a** STRIDE extraction (parallel, 3 tracks, 6-8h): tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation (5 agents)
- **Phase 2b** AI extraction (parallel, 3 tracks, 6-8h): data-poisoning, model-theft, tool-abuse, agent-autonomy (4 agents)
- **Phase 2c** Shared reference consolidation (SERIAL single-writer, 1-2h): append producer section to `finding-format-shared.md`
- **Phase 2d** Cross-agent overlap audit (serial, architect-led, 1h): identify and assign canonical owners for overlapping categories (FR-19)
- **Phase 2e** Security-analyst enrichment review (serial, 1-2h): verify primary sources, taxonomy, false-positive risk (FR-20). Reject speculative patterns; remove them without affecting architectural refactor.

### Phase 3: Validation & Delivery (4-6h)

1. Full regression on all 6 example architectures (FR-18, SC-005)
2. Cross-agent grep audit for duplications (SC-004)
3. Byte-deterministic PDF re-baseline with `SOURCE_DATE_EPOCH=1700000000` (FR-17, SC-008)
4. Documentation sync: `docs/architecture/00_Tech_Stack/README.md` agent inventory; ADR-023 status → Accepted
5. CHANGELOG entry via release-please
6. devops: PR merge, release-please tag, issue close

**Total PRD estimate**: 22h optimistic, 32h realistic, 45h pessimistic (per team-lead review).

## Risk & Mitigation Summary

| Risk | Likelihood | Impact | Mitigation | Spec Ref |
|------|-----------|--------|------------|----------|
| R1: Sibling variant doesn't generalize | Low | High | Phase 1 prototype catches at 2 agents, fallback: ship STRIDE-only PRD 082 + AI-only PRD 083 | FR-12, FR-13 |
| R2: Enrichment introduces noisy findings | Medium | Medium | Security-analyst Phase 2e review; per-pattern revert without affecting refactor | FR-20 |
| R3: Shared ref edits break infra agents | Low | High | Additive-only discipline (FR-5, C9); fallback: `tachi-shared-threat/` | FR-5, FR-6 |
| R4: Example regeneration surfaces unrelated changes | Low | Medium | Compare findings diff pre/post each agent extraction, not just at Phase 3 | FR-18, SC-005 |
| R5: Longer timeline than PRD 078 suggests | Medium | Low | Parallel waves in Phase 2a/2b; prototype-first gate shrinks scope if needed; STRIDE-only fallback | FR-12 |
| R6: Shared ref edits invalidate byte-deterministic PDF baselines | **High** | **Low (expected)** | Re-baseline 5 PDFs with SOURCE_DATE_EPOCH per ADR-021; process mirrors Feature 136 | FR-17, SC-008 |

Note that R6 is HIGH likelihood / LOW impact — it is an **expected outcome** of Phase 3, not an incident. All other risks are Medium-or-Low likelihood.

## References

- **PRD**: [docs/product/02_PRD/082-threat-agent-skill-references-2026-04-11.md](../../docs/product/02_PRD/082-threat-agent-skill-references-2026-04-11.md)
- **Spec**: [spec.md](./spec.md) (PM APPROVED_WITH_CONCERNS)
- **Research**: [research.md](./research.md) (Phase 0 consolidated findings)
- **Data model**: [data-model.md](./data-model.md) (Phase 1 file entities)
- **Quickstart**: [quickstart.md](./quickstart.md) (Phase 1 developer orientation)
- **Architect PRD review**: `.aod/results/architect.md` (11 concerns, addressed in spec Appendix A)
- **Team-lead PRD review**: `.aod/results/team-lead.md` (8 concerns, addressed in spec Appendix A)
- **PM spec review**: `.aod/results/product-manager-spec.md` (4 low-severity concerns)
- **Feature 078 precedent** (T014 prototype gate): `specs/078-agent-context-optimization/tasks.md`
- **Feature 136 precedent** (5 PDF re-baseline): see CLAUDE.md Feature 136 recent changes section
- **ADR-021** (byte-determinism): `docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md`
- **ADR-022** (first CLI prereq ADR): `docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md`
- **Control-analyzer** (methodology variant reference): `.claude/agents/tachi/control-analyzer.md` (427 lines, 3 phase-gated loads)
- **Constitution**: `.aod/memory/constitution.md` Principles I, III, VI, VII, VIII, IX, X apply
