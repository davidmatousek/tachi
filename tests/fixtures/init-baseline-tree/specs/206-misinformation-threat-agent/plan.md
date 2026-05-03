---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-23
    status: APPROVED
    notes: "Plan faithfully operationalizes spec.md (19 FRs, 14 SCs, 3 P1 user stories) into 6-wave structure with all 6 Triad-resolved HIGH/MEDIUM fixes preserved (H1 AML.T0042 CLOSED, HIGH-1 buffer-day budget model, HIGH-2 delivery retrospective slotting, MEDIUM-2 R8 concurrency hedge, MEDIUM-3 FR-7 three-callsite reconciliation, MEDIUM-4 architect FR-7 edit ownership). Success Criteria Mapping table covers all 14 spec SCs (SC-001 through SC-014) with Wave assignments. Out-of-Scope items preserved. PRD Q1-Q5 architect-owned decisions resolved in Open Questions table with justification. Timeline fits PRD envelope (2 working days + 1 buffer) with HIGH-1 buffer-day budget model codified (R5 polish at Wave 2.2 PM does NOT consume buffer; buffer reserved for R2 with advisory-app 0.5-day fallback). All 4 PM verification checks PASS — SC-001..SC-014 mapped, R3 CLOSED, Wave 6 covers retrospective + SC-013, R2 names advisory-app fallback. 0 BLOCKING / 0 HIGH / 0 MEDIUM / 0 LOW. PM APPROVED for /aod.tasks. Full review at .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-04-23
    status: APPROVED_WITH_CONCERNS
    notes: "Plan is technically sound on all 10 review dimensions: (1) ADR-023 lean-agent conformance (≤150 lines, single MANDATORY Read, zero MAESTRO) PASS; (2) schema bump 1.6→1.7 as 2nd Decision 8 application PASS; (3) 5-callsite F-1 carry-over reconciliation (orchestrator.md:296, :370; dispatch-rules.md LLM list, :120, trigger rules) correctly scoped with architect edit ownership per MEDIUM-4; (4) 24-file zero-edit invariant (22 original + F-1's 2) grep-auditable; (5) source_attribution contract correct — CWE-345/CWE-223 catalog-verified, AML.T0042 prose-only per F-A2 referential-integrity; (6) Heuristic A three-way scope resolution (distinct from prompt-injection / distinct from output-integrity per ADR-030 Decision 1 / scoped to factual-integrity) with ADR-030 Decision 1 + Decision 8 cross-refs captured; (7) two-part emission gate FR-011 correct (dispatch happens, emission self-gates); (8) 5-category pattern catalog with anti-indicator discipline per MEDIUM-5 + CWE-1039 exclusion per MEDIUM-3 captured; (9) byte-identity preservation on 5 non-factual baselines guaranteed by two-part emission gate; (10) dependencies satisfied (F-A1, F-A2, F-B, F-1) with zero new deps. 0 BLOCKING / 0 HIGH / 2 MEDIUM / 3 LOW — concerns are tasks.md enumeration refinements only and do not block /aod.tasks progression. Full review at .aod/results/architect.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: `misinformation` Threat Agent (OWASP LLM09:2025)

**Branch**: `206-misinformation-threat-agent` | **Date**: 2026-04-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/206-misinformation-threat-agent/spec.md`
**PRD**: [docs/product/02_PRD/206-misinformation-threat-agent-2026-04-23.md](../../docs/product/02_PRD/206-misinformation-threat-agent-2026-04-23.md)
**BLP-01 Phase**: Tier 1 F-2 — second net-new threat detection agent under the BLP-01 governance umbrella; follows F-1 Feature 201 (`output-integrity`) merged 2026-04-19; closes LLM09:2025 on the Coverage Matrix

## Summary

Author one new AI-tier threat agent `misinformation` and its companion skill directory to detect OWASP LLM09:2025 Misinformation — the factual-integrity signal class covering ungrounded factual emission, citation fabrication, overreliance / missing HITL on decision-critical output, retrieval-grounding gaps, and confidence-calibration absence. The agent emits findings with `MI-{N}` ID prefix and `category: llm`, every finding carrying a populated `source_attribution` array citing OWASP LLM09:2025 (primary) plus applicable CWEs (CWE-345 and/or CWE-223). Structure conforms to the ADR-023 lean-agent detection variant established in Feature 082 for the 11 existing threat agents and extended by F-1 for `output-integrity`.

**Architectural approach**: Mirror F-1 (`output-integrity.md`) verbatim in shape — it is the closest sibling and the immediate precedent for "new AI-tier threat agent under ADR-023 lean pattern": 5-section canonical layout, ≤150 lines, single `**MANDATORY**: Read` directive under `## Detection Workflow`, zero MAESTRO references. Two orchestrator-tier additive edits register the new agent in dispatch (`orchestrator.md` list + lines 296/370 F-1 carry-over reconciliation; `dispatch-rules.md` LLM quartet → quintet + line 120 F-1 carry-over reconciliation + trigger-keyword rules). One additive edit to `finding-format-shared.md` `consumers:` frontmatter (tier-grouping placement: between `output-integrity` and `risk-scorer`). One additive schema regex bump (`schemas/finding.yaml` 1.6 → 1.7 extending `id.pattern` to include `MI` prefix — second recorded application of ADR-030 Decision 8 regex-alternation minor-bump rule). One public per-feature ADR (ADR-031) under Proposed → Accepted dual-commit pattern. One example regeneration target (`agentic-app` per Q4 PM leaning / architect adjudication).

**Touch points**: 1 new agent file, 1 new companion skill directory (README + detection-patterns.md), 3 coordinated additive edits (orchestrator.md with 3 callsite reconciliation, dispatch-rules.md with 2 callsite reconciliation, finding-format-shared.md), 1 schema regex edit + version bump, 1 new ADR, 1 example regeneration. Zero edits to the 24 existing detection-tier files (12 threat agents + 12 companion `detection-patterns.md`; 22 original + F-1's 2), zero edits to infrastructure-tier consumers (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler), zero new runtime dependencies.

## Technical Context

**Language/Version**: Markdown + YAML + Python 3.11 (existing — stdlib + `pyyaml`); agents and skills are markdown/YAML content files, not executable code
**Primary Dependencies**: `pyyaml` (runtime, already declared), `pytest` (dev-only, already declared per Feature 128 precedent); no new runtime or dev dependencies
**Storage**: File-based; reads `schemas/finding.yaml` (v1.6 pre-edit, v1.7 post-edit), `schemas/taxonomy/{owasp,cwe,mitre-atlas,nist-ai-rmf}.yaml` (F-A1 catalogs for `source_attribution` validation); writes to `.claude/agents/tachi/`, `.claude/skills/tachi-misinformation/`, `docs/architecture/02_ADRs/`, `examples/agentic-app/`
**Testing**: pytest (existing harness at `tests/scripts/`) + backward-compatibility test `tests/scripts/test_backward_compatibility.py` under `SOURCE_DATE_EPOCH=1700000000` (ADR-021) — 5 non-factual-output baselines byte-identity; regex unit test for schema 1.7 `id.pattern`; referential-integrity fixtures for `MI-{N}` source_attribution
**Target Platform**: Command-line Python tooling (macOS/Linux/WSL); orchestrator + threat agents invoked via `/tachi.threat-model` Claude command; PDF rendering via Typst + Mermaid CLI (unchanged)
**Project Type**: Single project (methodology toolkit — agents + skills + schemas + templates in a unified repo); no frontend/backend split
**Performance Goals**: Agent dispatch + pattern evaluation <5s on the regenerated example (informational floor, within existing `/tachi.threat-model` budget); no new performance regressions
**Constraints**: (a) SC-006 byte-identity on 5 non-factual-output baselines under `SOURCE_DATE_EPOCH=1700000000` is a BLOCKER; (b) SC-009 24-file zero-edit invariant on 12 threat agents + 12 companion skill references (22 original + F-1's 2) is a BLOCKER; (c) FR-010 zero MAESTRO references in agent + companion is a grep-auditable invariant; (d) SC-010 F-A2 referential-integrity validation must pass on every emitted `MI-{N}` finding; (e) SC-008 zero new runtime or developer dependencies is a BLOCKER; (f) FR-011 two-part emission gate (LLM keyword AND factual-output indicator) is a correctness BLOCKER — keyword match alone MUST NOT emit
**Scale/Scope**: 1 new agent file (~100-150 lines), 1 new companion README (~30-50 lines), 1 new detection-patterns.md (~200-300 lines), 5 pattern categories (6 if architect elects Q1 expansion), 12 trigger keywords (architect-curated per Q2 leaning; architect may refine to 8-16 range), 2-3 example findings in agent file, 5 worked examples in detection-patterns.md (one per pattern category). 5 coordinated edits total (2 orchestrator-tier with 5 callsite reconciliations + 1 shared reference + 1 schema + 1 example regen).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.aod/memory/constitution.md`:

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Agent detects a generic factual-integrity signal class (LLM factual-output emission without grounding/verification); no hardcoded project-type assumptions |
| II. API-First Design | N/A | No REST/GraphQL surface; threat agents are content files consumed by the orchestrator at invocation time |
| III. Backward Compatibility (NON-NEGOTIABLE) | PASS | Two-part emission gate (FR-011) + zero-finding default on non-qualifying architectures → 5 non-factual-output baselines byte-identical. Local `.aod/` workflows unaffected. Schema 1.6 → 1.7 is additive regex extension; existing IDs remain valid |
| IV. Concurrency & Data Integrity | N/A | F-2 is single-invocation content authoring; no concurrent state |
| V. Privacy & Data Isolation | PASS | Worked examples use clearly-fictional scenarios per NFR-6 (healthcare/legal/finance domains explicitly anonymized); no PII, no adopter data, no network calls by the agent |
| VI. Testing Excellence (MANDATORY) | PASS | Regex unit test for schema 1.7 `id.pattern`; fixture-driven tests for `source_attribution` referential integrity on `MI-{N}` findings; backward-compat byte-identity gate on 5 baselines; structural-diff check on agent line-count + MANDATORY-Read count + zero MAESTRO grep; F-1 carry-over reconciliation grep-check on 5 callsites |
| VII. Definition of Done (NON-NEGOTIABLE) | PASS | Spec-defined SCs (SC-001 through SC-014) map to testable predicates. SC-006 + SC-009 + SC-010 are BLOCKER-level gates; DoD bullet 12 (delivery retrospective) carried via HIGH-2 Wave 2.3 PM / buffer-day slotting |
| VIII. Product-Spec Alignment | PASS | Approved PRD 206 exists (PM APPROVED, Architect APPROVED_WITH_CONCERNS, Team-Lead APPROVED_WITH_CONCERNS with all 6 HIGH/MEDIUM fixes resolved inline); spec.md has PM APPROVED_WITH_CONCERNS sign-off |
| IX. Git Workflow | PASS | Feature branch `206-misinformation-threat-agent`; no main commits; Proposed → Accepted dual-commit ADR pattern |
| X. Zero-Edit Invariant (ADR-023 lineage) | PASS | FR-013 / SC-009 explicit; orchestrator-tier carve-out documented per F-1 + Feature 142 precedent; grep audit at PR pre-merge; invariant now 24 files (22 original + F-1's 2) |

**Gate verdict**: No violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```
specs/206-misinformation-threat-agent/
├── plan.md                  # This file (/aod.project-plan output)
├── research.md              # Phase 0 output (populated by /aod.spec)
├── data-model.md            # Phase 1 output — agent metadata shape + finding shape + pattern category shape
├── contracts/
│   └── finding-contract.md  # Finding IR contract for MI-{N} findings (source_attribution + mitigation rules)
├── quickstart.md            # Phase 1 output — verification walkthrough
├── checklists/
│   └── requirements.md      # Spec quality checklist (populated by /aod.spec)
├── spec.md                  # PM-approved spec
└── tasks.md                 # Task breakdown (/aod.tasks output)
```

### Source Code (repository root)

```
tachi/
├── .claude/
│   ├── agents/
│   │   └── tachi/
│   │       ├── misinformation.md                  # NEW — lean AI-tier agent, ≤150 lines (≤180 hard cap)
│   │       ├── orchestrator.md                    # MODIFY (additive) — add misinformation + reconcile lines 296, 370
│   │       ├── output-integrity.md                # UNCHANGED (24-file invariant; F-1's agent)
│   │       ├── prompt-injection.md                # UNCHANGED
│   │       ├── data-poisoning.md                  # UNCHANGED
│   │       ├── model-theft.md                     # UNCHANGED
│   │       ├── agent-autonomy.md                  # UNCHANGED
│   │       ├── tool-abuse.md                      # UNCHANGED
│   │       ├── spoofing / tampering / repudiation / info-disclosure / denial-of-service / privilege-escalation.md  # UNCHANGED (6 STRIDE)
│   │       ├── risk-scorer.md                     # UNCHANGED (FR-014 infrastructure-tier invariant)
│   │       ├── control-analyzer.md                # UNCHANGED
│   │       ├── threat-report.md                   # UNCHANGED
│   │       ├── threat-infographic.md              # UNCHANGED
│   │       └── report-assembler.md                # UNCHANGED
│   │
│   └── skills/
│       ├── tachi-misinformation/                  # NEW — companion skill directory
│       │   ├── README.md                           # NEW — consumers + purpose header
│       │   └── references/
│       │       └── detection-patterns.md           # NEW — 5 pattern categories
│       │
│       ├── tachi-orchestration/
│       │   └── references/
│       │       └── dispatch-rules.md               # MODIFY (additive) — LLM quartet → quintet + reconcile line 120
│       │
│       ├── tachi-shared/
│       │   └── references/
│       │       └── finding-format-shared.md       # MODIFY (additive) — consumers: list adds misinformation
│       │
│       ├── tachi-output-integrity/                 # UNCHANGED — F-1's companion skill
│       └── tachi-{11 original AI + STRIDE skills}/ # UNCHANGED (24-file invariant)
│
├── schemas/
│   ├── finding.yaml                                # MODIFY — schema_version 1.6 → 1.7; id.pattern regex adds MI prefix
│   └── taxonomy/                                   # UNCHANGED — read-only source for source_attribution validation
│       ├── owasp.yaml                              # LLM09 entry present (verified PRD-time)
│       ├── cwe.yaml                                # CWE-345, CWE-223 entries present (verified PRD-time)
│       └── mitre-atlas.yaml                        # AML.T0042 CONFIRMED ABSENT — prose-only in pattern catalog
│
├── docs/
│   └── architecture/
│       └── 02_ADRs/
│           └── ADR-031-misinformation-agent.md     # NEW — Proposed → Accepted dual-commit
│
├── tests/
│   └── scripts/
│       ├── test_misinformation.py                  # NEW — regex + source_attribution validation tests
│       ├── test_backward_compatibility.py          # UNCHANGED — 5 baselines byte-identity gate
│       └── fixtures/
│           └── misinformation/                     # NEW — fixture findings
│               ├── valid_mi_finding.yaml
│               └── invalid_attribution_finding.yaml
│
├── examples/
│   ├── web-app / microservices / ascii-web-api / mermaid-agentic-app / free-text-microservice / maestro-reference/  # UNCHANGED (SC-006 baselines)
│   └── agentic-app/                                # REGENERATE (Q4 PM leaning; architect adjudicates)
│
└── scripts/
    └── tachi_parsers.py                            # UNCHANGED (F-A2 validate_source_attribution already accepts MI via regex)
```

**Structure Decision**: Single-project layout (existing tachi repo structure). No new top-level directories. All changes confined to `.claude/agents/`, `.claude/skills/`, `schemas/`, `docs/architecture/02_ADRs/`, `tests/scripts/`, `examples/agentic-app/`. Follows Feature 082 (lean-agent refactor) + Feature 142 (orchestrator-tier additive edits) + Feature 201 F-1 (second-agent authoring) precedent.

## System Design

### Components

**New components (F-2-owned)**:

1. **`misinformation` Threat Agent** (`.claude/agents/tachi/misinformation.md`)
   - 5-section canonical shape per ADR-023 (frontmatter → metadata YAML → `## Purpose` → `## Skill References` table → `## Detection Workflow`) with optional `## Example Findings`
   - Metadata: `category: llm`, `threat_class: LLM`, `dfd_targets: [Process]`, `owasp_references: [OWASP LLM09:2025]`, `output_schema: ../../../schemas/finding.yaml`
   - **No `agentic_pattern` in metadata** — assigned downstream by orchestrator Phase 3.6 per ADR-026 (FR-016)
   - Detection Workflow has exactly one `**MANDATORY**: Read` directive loading the companion `detection-patterns.md`
   - Two-part emission gate (FR-011) explicit in workflow step: LLM keyword match AND factual-output indicator both required
   - Emits `MI-{N}` findings with `category: llm`, populated `source_attribution`, grounding/verification-specific mitigation text
   - Line count: ≤150 (AI tier cap per ADR-023), hard ceiling 180

2. **Pattern Catalog** (`.claude/skills/tachi-misinformation/references/detection-patterns.md`)
   - Frontmatter: `name`, `description`, `consumers: [tachi-misinformation]`, `last_updated: 2026-04-27` (or actual merge date)
   - `## Overview` paragraph explaining scope (factual-integrity signal class; distinct from prompt-injection input-side and output-integrity output-sanitization per ADR-031 Heuristic A analysis; OWASP LLM09:2025 canonical surface)
   - `## Detection Scope` with Trigger Keywords (12, architect-curated per Q2) + Applicable DFD Element Types (`Process` only per Q3 default)
   - `## Detection Patterns` with 5 numbered categories: (1) **Ungrounded Factual Emission** (primary OWASP LLM09:2025, related CWE-345), (2) **Citation Fabrication** (primary OWASP LLM09:2025, related CWE-345), (3) **Overreliance / Missing HITL on Decision-Critical Output** (primary OWASP LLM09:2025, related CWE-223 + optional CWE-345), (4) **Retrieval-Grounding Gaps** (primary OWASP LLM09:2025, related CWE-345), (5) **Confidence-Calibration Absence** (primary OWASP LLM09:2025, related CWE-345). Each category carries indicators (3-6 bullets), ≥1 worked example (clearly-fictional framing per NFR-6), primary-source citation, trigger keywords, applicable DFD element types
   - **Anti-indicator discipline** per architect MEDIUM-5: each pattern enumerates at least one anti-indicator (structural feature whose presence MUST NOT trigger the pattern) to bound false-positive surface on LLM Processes with declared grounding/verification mechanisms
   - **Primary Sources section** cites OWASP LLM09:2025 (catalog-resolvable), CWE-345 and CWE-223 (catalog-resolvable), AML.T0042 Verify Attack (prose-only — catalog absent), NIST AI 600-1 §2.4 Hallucination (prose-only — section IDs not catalogued)

3. **Companion Skill README** (`.claude/skills/tachi-misinformation/README.md`)
   - Mirror `tachi-output-integrity/README.md` shape: short description + consumers list header + layout overview

4. **Public Per-Feature ADR** (`docs/architecture/02_ADRs/ADR-031-misinformation-agent.md`)
   - Proposed → Accepted dual-commit (ADR-027 / ADR-028 / ADR-029 / ADR-030 precedent)
   - Body: (a) new-agent decision, (b) Heuristic A signal-class rationale with three-way scope resolution (distinct from prompt-injection input-side; distinct from output-integrity output-sanitization per ADR-030 Decision 1; scoped to factual-integrity grounding/verification/HITL/calibration), (c) lean-agent shape conformance per ADR-023, (d) cross-references to ADR-021/023/026/027/028/029/030 (explicit callout to ADR-030 Decision 1 scope bounds and ADR-030 Decision 8 regex-alternation minor-bump rule — F-2 is the second recorded application), (e) 24-file zero-edit invariant proof with grep-auditable enumeration, (f) Revision History tracking Proposed → Accepted dates, (g) zero commercial framing, (h) CWE-1039 deliberate-exclusion note (model-evasion CWE out of scope; pattern catalog focuses on factual-content primitives, not model-robustness primitives)

**Modified components (additive edits only)**:

5. **Orchestrator Dispatch List** (`.claude/agents/tachi/orchestrator.md` — hardcoded dispatch around the AI-tier section + F-1 carry-over reconciliation at lines 296, 370)
   - Insert `- misinformation` in the AI-tier dispatch block after `output-integrity`
   - **Line 296 F-1 carry-over reconciliation**: `(prompt-injection then data-poisoning then model-theft)` → `(prompt-injection then data-poisoning then model-theft then output-integrity then misinformation)` — extends the pre-F-1 three-agent text to the full five-agent quintet, reconciling F-1's quartet skip and registering F-2's addition in the same edit
   - **Line 370 F-1 carry-over reconciliation**: `LLM Threats row: prompt-injection, data-poisoning, model-theft` → `prompt-injection, data-poisoning, model-theft, output-integrity, misinformation` — identical quintet reconciliation

6. **Dispatch Rules LLM Quintet** (`.claude/skills/tachi-orchestration/references/dispatch-rules.md` — LLM dispatch list at lines 71-74 and table row at line 120)
   - Extend the LLM dispatch list (post-F-1 quartet) to quintet: add `- misinformation (OWASP LLM09:2025)` after `output-integrity` with FR-011-style activation rule (two-part gate — LLM keyword AND factual-output indicator)
   - **Line 120 F-1 carry-over reconciliation**: `LLM (LLM Threats) | ... | prompt-injection, data-poisoning, model-theft | OWASP LLM Top 10 v2025` → `prompt-injection, data-poisoning, model-theft, output-integrity, misinformation` — identical quintet reconciliation as orchestrator.md:370
   - Add trigger-keyword rules section extension for misinformation's 12-keyword activation set per Q2 decision
   - **Architect MEDIUM-4 dispatch-table FP dry-run** at Wave 2.0: grep existing 6 baseline architectures for the 12 trigger keywords; verify none of the 5 non-factual baselines contain factual-output indicators (expected zero matches); confirm `agentic-app` at post-F-1 state contains the regeneration-candidate indicators

7. **Shared Finding-Format Consumer List** (`.claude/skills/tachi-shared/references/finding-format-shared.md` — frontmatter `consumers:` list post-F-1)
   - Insert `- misinformation` between `output-integrity` and `risk-scorer` — tier-grouping placement (AI-LLM-new tier tail) per FR-5; architect adjudicates final position per PRD MEDIUM-1
   - Body content byte-identical pre/post edit per ADR-023 Decision 3 (F-1 precedent already validated this invariant)

8. **Finding Schema Regex** (`schemas/finding.yaml`)
   - Line 13: `schema_version: "1.6"` → `schema_version: "1.7"` (minor bump per ADR-026 Complex-Shape Clarifier extended by ADR-030 Decision 8 to regex-alternation prefix addition — F-2 is the second recorded application of Decision 8)
   - Line 18: `id.pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\\d+$"` → `"^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\\d+$"`
   - `examples:` list gains an `MI-1` entry for completeness (per PRD FR-4)

### Data Flow

Given a DFD architecture description, the orchestrator dispatches the `misinformation` agent when any Process component matches an LLM trigger keyword. The agent reads the companion `detection-patterns.md` via the single `**MANDATORY**: Read` directive, evaluates the two-part emission gate on each dispatched Process (LLM keyword AND factual-output indicator), and emits zero or more `MI-{N}` findings with populated `source_attribution` per applicable pattern category. Findings flow through orchestrator Phase 3 (MAESTRO assignment, agentic_pattern assignment), Phase 4 (referential validation), and Phase 5 (deduplication) identically to existing `LLM-{N}` and `OI-{N}` findings — no consumer-tier changes required. Report-tier rendering (`threat-report.md`, `threats.md`) groups `MI-{N}` findings in the `category: llm` section alongside `LLM-{N}` and `OI-{N}` findings, preserving the three-signal-class discipline without prose synthesis.

### Tech Stack

- **Agent / skill files**: Markdown + YAML (ADR-023 lean-agent pattern)
- **Schema**: `schemas/finding.yaml` v1.7 post-edit (regex alternation extension, backward-compatible)
- **Taxonomy catalogs**: `schemas/taxonomy/{owasp,cwe}.yaml` (F-A1, unchanged) — consumed read-only for `source_attribution` validation
- **Orchestrator dispatch**: `.claude/agents/tachi/orchestrator.md` + `.claude/skills/tachi-orchestration/references/dispatch-rules.md` (additive edits)
- **Parser**: `scripts/tachi_parsers.py` (unchanged — `validate_source_attribution` already accepts any ID prefix matching the regex)
- **Test harness**: pytest + `tests/scripts/test_backward_compatibility.py` (existing) + new `tests/scripts/test_misinformation.py`
- **Example regeneration pipeline**: `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report` (existing pipeline, unchanged)
- **Typst templates**: no edits — PDF renderer reads `threats.md` / `risk-scores.md` / `compensating-controls.md` and the coverage-attestation section auto-renders from `source_attribution` post-regeneration
- **ADR dual-commit**: standard Proposed → Accepted lifecycle via `gh pr` + squash merge (ADR-027/028/029/030 precedent)

## Phase 0: Research

**Status**: Populated by `/aod.spec` at [research.md](./research.md). Key grounding facts confirmed at PRD/spec time:

- F-1 (`output-integrity.md`) is 120 lines — the authoritative 5-section AI-tier template F-2 mirrors verbatim
- `schemas/finding.yaml:13` schema_version = `"1.6"` post-F-1; line 18 `id.pattern` = `"^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\\d+$"`; `MI` prefix absent (confirming FR-4 bump requirement)
- `schemas/taxonomy/owasp.yaml` contains LLM09 record with `name: Misinformation`, `cwe_refs: []` (confirmed)
- `schemas/taxonomy/cwe.yaml` contains CWE-345 (Insufficient Verification of Data Authenticity) and CWE-223 (Omission of Security-relevant Information) (confirmed)
- `schemas/taxonomy/mitre-atlas.yaml` contains 12 AML techniques; `AML.T0042` CONFIRMED ABSENT → prose-only citation in pattern catalog, MUST NOT appear in `source_attribution`
- `orchestrator.md` line 296 (sequential-mode text) and line 370 (LLM Threats row) currently reference the pre-F-1 three-agent list → F-1 carry-over requires reconciliation to the five-agent quintet in the F-2 edit
- `dispatch-rules.md` lines 71-74 list the post-F-1 LLM quartet; line 120 (table row) currently references the pre-F-1 three-agent list → F-1 carry-over reconciliation required
- `finding-format-shared.md` `consumers:` list post-F-1 places `output-integrity` as the last AI-LLM-new entry; insertion point for `misinformation` is between `output-integrity` and `risk-scorer` per FR-5
- ADR-031 does NOT yet exist (no forward-dependency conflict)
- Feature 201 F-1 regenerated `agentic-app` on 2026-04-19; current agentic-app carries `LLM-{N}` + `OI-{N}` findings; `agentic-app` selected as F-2 regeneration candidate per Q4 PM leaning requires extension with factual-output sub-component

**Open research items resolved during /aod.project-plan** (see Open Questions section):
- Q1 (Pattern category count) — resolved: **5 categories** (architect may override at Wave 1.2 if a compelling signal-class differentiator surfaces)
- Q2 (Trigger keyword final set) — resolved: **12 keywords** per Q2 architect leaning at PRD review
- Q3 (DFD target set) — resolved: **Process only** (mirror F-1)
- Q4 (Example regeneration target) — resolved: **`agentic-app` extended with factual-output sub-component** (PM leaning; R2 fallback `advisory-app` at 0.5 day buffer consumption)
- Q5 (ADR-031 sequencing) — resolved: **Proposed Day 1 Wave 1.1** (mirror F-1)

## Phase 1: Design & Contracts

**Prerequisites**: research.md populated (Phase 0 complete)

### Finding IR Contract (`contracts/finding-contract.md`)

**Purpose**: Document the shape of `MI-{N}` findings emitted by the new agent, including `source_attribution` invariants and mitigation-text rules.

**Contract**:

```yaml
id: "MI-{N}"                          # monotonically increasing per run, MI prefix new in schema 1.7
category: "llm"                       # existing enum value — unchanged
title: "{pattern_category}: {short_summary}" # e.g., "Ungrounded Factual Emission: medical summarizer emits clinical claims without RAG"
severity: "low" | "medium" | "high" | "critical"  # OWASP 3×3 matrix via severity-bands-shared.md
component: "{DFD Process component name}"
description: "{2-4 sentence threat description distinguishing factual-emission vs citation-integrity vs decision-overreliance}"
mitigation: "{grounding/verification/HITL/calibration mechanism}"  # e.g., "Mandatory RAG grounding with per-claim source attribution"
references:
  - "OWASP LLM09:2025"
  - "https://cwe.mitre.org/data/definitions/{CWE_NUMBER}.html"
source_attribution:
  - {taxonomy: "owasp", id: "LLM09", relationship: "primary"}   # REQUIRED on every MI-{N} finding
  - {taxonomy: "cwe", id: "CWE-{NUMBER}", relationship: "related"}  # per applicable pattern category (CWE-345 and/or CWE-223)
maestro_layer: "L5"                   # assigned downstream by orchestrator Phase 1 (existing Feature 084)
agentic_pattern: "none" | "multi-agent"  # assigned downstream by orchestrator Phase 3.6 (existing Feature 142)
delta_status: null                    # assigned downstream if baseline present (existing Feature 104)
```

**Invariants**:
- Every `MI-{N}` finding MUST pass `validate_source_attribution()` at orchestrator Phase 4
- The `source_attribution` array MUST contain at minimum `{taxonomy: owasp, id: LLM09, relationship: primary}`
- CWE entries MUST use IDs present in `schemas/taxonomy/cwe.yaml`: CWE-345 (all pattern categories), CWE-223 (overreliance / missing HITL category)
- AML.T0042 MUST NOT appear in `source_attribution` (confirmed absent from catalog)
- The `mitigation` field MUST name at least one specific grounding, verification, HITL, or calibration mechanism (not generic "ground the LLM")
- The `id` MUST match schema 1.7 `id.pattern` regex
- The agent MUST enforce the two-part emission gate (FR-011): finding emission requires BOTH LLM keyword match AND factual-output indicator

### Data Model (`data-model.md`)

**Purpose**: Document the agent metadata YAML shape + pattern category structure + companion skill README shape.

See [data-model.md](./data-model.md) for full entity definitions.

### Quickstart (`quickstart.md`)

**Purpose**: Step-by-step verification walkthrough — given a regenerated `agentic-app` extended with a factual-output sub-component, confirm ≥1 `MI-{N}` finding with valid source_attribution, valid mitigation text, and passing referential validation.

See [quickstart.md](./quickstart.md) for the verification procedure.

### Agent Context Update

Run `.aod/scripts/bash/update-agent-context.sh claude` after plan approval to refresh `CLAUDE.md` / agent-specific context with the Feature 206 entry.

## Implementation Approach (Phased Waves)

Calendar-verified against `cal 4 2026`: 2026-04-27 Monday (Day 1), 2026-04-28 Tuesday (Day 2), 2026-04-29 Wednesday (Buffer).

### Wave 1 — Day 1 AM (Monday 2026-04-27, 0.5d)

**Gate-critical, front-loaded to unblock parallel Day 1 PM authoring.**

- **Wave 1.0 (30-60 min)**: Architect verifies Heuristic A signal-class intact (ADR-030 Decision 1 bounds F-1 scope to downstream-execution-sanitization; F-2 inherits factual-integrity scope carve-out). If a subsume-into-output-integrity signal surfaces, escalate to architect per PRD R1 Day 1 gate before Wave 1.1.
- **Wave 1.1 (parallel)**:
  - **Schema-lock commit**: `schemas/finding.yaml` regex bump 1.6 → 1.7; `id.pattern` includes `MI` prefix; `examples:` list gains `MI-1`. Unit test `test_misinformation.py::test_regex_matches_mi_prefix`.
  - **ADR-031 Proposed commit**: ADR body with Heuristic A three-way scope resolution (distinct from prompt-injection input-side; distinct from output-integrity output-sanitization per ADR-030 Decision 1 explicit cross-ref; scoped to factual-integrity), lean-agent shape conformance, cross-references to ADR-021/023/026/027/028/029/030 (Decision 1 + Decision 8 callouts), 24-file zero-edit invariant, CWE-1039 deliberate-exclusion note, Revision History table.
  - **Agent file skeleton**: `.claude/agents/tachi/misinformation.md` 5-section scaffold with metadata YAML, Purpose section stub, Skill References table.
  - **Tester fixture authoring**: `tests/scripts/fixtures/misinformation/valid_mi_finding.yaml` + `invalid_attribution_finding.yaml`.
- **Escalation gate**: If Wave 1.0 Heuristic A verification surfaces a subsume signal, halt Wave 1.1 ADR work until architect + team-lead ruling recorded; affect Wave 2.3 delivery retrospective slotting (HIGH-2).

### Wave 2 — Day 1 PM (Monday 2026-04-27, 0.5d)

**Pattern catalog authoring + Skill References + agent body.**

- `.claude/skills/tachi-misinformation/references/detection-patterns.md`: 5 pattern categories with indicators, worked examples (clearly-fictional framing per NFR-6), primary-source citations, trigger keywords, applicable DFD element types. Anti-indicator discipline per architect MEDIUM-5 (each pattern enumerates at least one anti-indicator).
- `.claude/skills/tachi-misinformation/README.md`: companion README (mirror `tachi-output-integrity/README.md`).
- `.claude/agents/tachi/misinformation.md`: fill out `## Purpose` (distinct-from-prompt-injection + distinct-from-output-integrity + scoped-to-factual-integrity prose), `## Detection Workflow` with single `**MANDATORY**: Read` and explicit two-part emission gate step, optional `## Example Findings` (2-3 worked examples across pattern categories).
- **Structural validation**: `wc -l ≤ 150`, `grep -c '\*\*MANDATORY\*\*: Read' = 1`, `grep -i maestro` returns empty on both agent file AND companion `detection-patterns.md`.

### Wave 3 — Day 2 AM (Tuesday 2026-04-28, 0.3d)

**Orchestrator registration + shared reference additive edits + F-1 carry-over reconciliation.**

- `.claude/agents/tachi/orchestrator.md`: insert `- misinformation` in AI-tier dispatch list; reconcile line 296 sequential-mode text (quartet → quintet); reconcile line 370 LLM Threats row (quartet → quintet). Edit owner: architect (MEDIUM-4 resolution).
- `.claude/skills/tachi-orchestration/references/dispatch-rules.md`: extend LLM quartet → quintet at lines 71-74; add misinformation activation rule (two-part gate); reconcile line 120 table row (quartet → quintet); extend trigger-keyword rules section with misinformation's 12-keyword set.
- `.claude/skills/tachi-shared/references/finding-format-shared.md`: add `- misinformation` between `output-integrity` and `risk-scorer` in `consumers:` list.
- **Structural-diff validation**: `## ` headings in `finding-format-shared.md` byte-identical pre/post edit; grep-check confirms quintet is consistent across all 5 reconciled callsites.
- **Architect MEDIUM-4 dispatch-table FP dry-run**: grep all 6 baseline architectures for the 12 misinformation trigger keywords; verify zero matches on 5 non-factual baselines; confirm `agentic-app` post-F-1 state is the regeneration candidate (factual-output extension required for emission).

### Wave 4 — Day 2 AM/PM (Tuesday 2026-04-28, 0.5d)

**Example regeneration + backward-compat verification.**

- Architect decides at Wave 3 EOD whether to extend `agentic-app` in-place or fall back to new `advisory-app` (R2 0.5-day buffer consumption). PM default: extend `agentic-app` per Q4 leaning.
- Run `/tachi.threat-model examples/agentic-app/architecture.md` (post-extension) to confirm dispatch emits `MI-{N}` findings.
- Run full downstream pipeline (`/tachi.risk-score`, `/tachi.compensating-controls`, `/tachi.infographic all`, `/tachi.security-report`).
- Commit regenerated artifacts: `threats.md`, `threats.sarif`, `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md`, `compensating-controls.sarif`, `threat-report.md`, `attack-trees/`, `attack-chains.md`, 6 infographic JPEGs, `security-report.pdf`, `security-report.pdf.baseline`.
- Verify ≥1 `MI-{N}` finding present; verify F-A2 referential validation passes (`validate_source_attribution` returns no errors); verify three-signal-class discipline (LLM-{N}, OI-{N}, MI-{N} findings adjacent in category: llm section without prose synthesis).
- Run `tests/scripts/test_backward_compatibility.py` — 5 non-factual-output baselines MUST be byte-identical under `SOURCE_DATE_EPOCH=1700000000`.

### Wave 5 — Day 2 PM (Tuesday 2026-04-28, 0.3d)

**Code review + ADR-031 Accepted transition + PR.**

- Senior-backend-engineer + code-reviewer double-check pattern catalog worked examples for NFR-6 compliance (clearly-fictional framing on healthcare/legal/finance; no real institutional/clinician/lawyer/advisor identities) — absorbs R5 polish per HIGH-1 buffer-day budget model.
- Transition ADR-031 Proposed → Accepted with provisional merge-date.
- Run full pytest suite; grep audit on 24-file zero-edit invariant (12 threat agents + 12 companion `detection-patterns.md` files); validate SC-001 through SC-014.
- Open PR ready for merge (draft PR opened at plan stage is marked ready here).
- Triple-review + merge (squash commit).
- **Post-merge SHA fill** on ADR-031 Revision History.

### Wave 6 — Day 2 PM / Day 3 Buffer (2026-04-29 Wednesday)

**Delivery retrospective + post-merge follow-through + contingent buffer-day work.**

- **Delivery retrospective slotting** (HIGH-2): `specs/206-misinformation-threat-agent/delivery.md` authored Wave 2.3 PM if merge completes with ≥1 hour residual capacity; otherwise authored 2026-04-29 Wed (buffer day) as the primary buffer-day activity. Mirrors F-1 same-day-as-delivery at ~1-2 hours pattern.
- **BLP-01 Coverage Matrix update** (SC-013): LLM09:2025 transitions Planned → Covered with F-2 (Feature 206) named as closure feature. Post-merge documentation commit to `_internal/strategy/BLP-01-threat-coverage.md`.
- **Contingent buffer-day work** (if R2 materializes): extend the buffer-day capacity to absorb regeneration friction on `agentic-app` or, if needed, fall back to `advisory-app` authoring (~0.5 day consumption). If R2 does not materialize, buffer-day capacity redirects to delivery-retrospective authoring.

## Touch Points Summary

| File | Change | Lines | Scope |
|------|--------|-------|-------|
| `.claude/agents/tachi/misinformation.md` | NEW | ~100-150 | Agent file |
| `.claude/skills/tachi-misinformation/README.md` | NEW | ~30-50 | Skill README |
| `.claude/skills/tachi-misinformation/references/detection-patterns.md` | NEW | ~200-300 | Pattern catalog (5 categories) |
| `.claude/agents/tachi/orchestrator.md` | MODIFY (add 1 line + 2 callsite reconciliations at 296, 370) | 3 edits | Dispatch list + F-1 carry-over |
| `.claude/skills/tachi-orchestration/references/dispatch-rules.md` | MODIFY (add ~4-6 lines + 1 callsite reconciliation at 120) | 4-6 edits | LLM quintet + activation rule + F-1 carry-over |
| `.claude/skills/tachi-shared/references/finding-format-shared.md` | MODIFY (add 1 line) | ~1 | Consumer list |
| `schemas/finding.yaml` | MODIFY (2 lines: version + regex; +1 examples entry) | ~13, ~18 | Schema bump |
| `docs/architecture/02_ADRs/ADR-031-misinformation-agent.md` | NEW | ~250-350 | Public ADR |
| `tests/scripts/test_misinformation.py` | NEW | ~100-150 | Regex + source_attribution tests |
| `tests/scripts/fixtures/misinformation/*.yaml` | NEW | ~20-30 each | Test fixtures |
| `examples/agentic-app/*` | REGENERATE | — | Pipeline artifacts + PDF baseline (post-extension with factual-output sub-component) |
| `.claude/agents/tachi/{12 existing}.md` + `.claude/skills/tachi-{12 existing}/references/detection-patterns.md` | ZERO CHANGES | — | 24-file invariant |
| `.claude/agents/tachi/{risk-scorer,control-analyzer,threat-report,threat-infographic,report-assembler}.md` | ZERO CHANGES | — | Infrastructure-tier invariant |
| `scripts/*.py` | ZERO CHANGES | — | Parser + orchestrator scripts |
| `templates/tachi/*` | ZERO CHANGES | — | Typst templates |
| `requirements*.txt`, `pyproject.toml`, `package.json` | ZERO CHANGES | — | No new dependencies |

## Risks & Mitigations

See spec.md Edge Cases + PRD §Risks & Mitigations for the full list. Plan-phase active risks:

- **R1 (Heuristic A signal-class re-adjudication)** — Mitigation: Wave 1.0 architect verification; escalation gate before Wave 1.1 ADR commit if subsume signal surfaces. Status: LOW likelihood per ADR-030 Decision 1 bounds.
- **R2 (Regeneration friction on `agentic-app`)** — Mitigation: Wave 4 structured pre-vs-post diff; Wave 6 buffer-day reserved; fallback to `advisory-app` (0.5 day consumption) if `agentic-app` cumulative-state cost exceeds convention-preservation benefit.
- **R3 (MITRE ATLAS AML.T0042 absent from catalog)** — CLOSED: architect verified absent at PRD time; pattern catalog prose-only; `source_attribution` anchors on LLM09 + CWE-345 + CWE-223.
- **R4 (Schema bump 1.6 → 1.7 collision with concurrent features)** — Mitigation: F-2 ships solo in 2026-04-27 → 2026-04-29 window (verified at PRD time); `git pull` verification before FR-4 commit.
- **R5 (Pattern-catalog prose quality on healthcare/legal/finance worked examples)** — Mitigation: NFR-6 enforcement at Wave 2.2 PM code review; senior-backend-engineer + code-reviewer double-check. Buffer-day budget model per HIGH-1 — R5 polishes at Wave 2.2 PM, NOT consuming buffer-day capacity.
- **R6 (Orchestrator dispatch-rules LLM quintet ordering drift)** — Mitigation: FR-7 specifies "extend quartet to quintet" preserving F-1 ordering; grep-check at Wave 3 EOD confirms quintet consistent across 5 callsites.
- **R7 (Finding-format-shared consumer list placement drift)** — Mitigation: FR-3 specifies placement between `output-integrity` and `risk-scorer`; architect adjudicates at plan time per PRD MEDIUM-1. Plan decision: architect confirms placement in Wave 3.
- **R8 (F-3/F-4/F-5 concurrent-build 4-surface additive-edit conflict)** — Mitigation: F-2 ships solo per team-lead backlog audit; serialization discipline enforced by team-lead at plan time if calendar shifts.
- **R9 (Agent line count drift above 150 cap)** — Mitigation: Wave 2 `wc -l` validation at draft and final states; if >150, trim Purpose prose or move example findings to companion catalog; hard ceiling 180.

## Open Questions (PRD Q-set — Architect Decisions)

Architect-owned per PRD §Architecture & Design Decisions. Resolved during `/aod.project-plan` per decision authority.

| # | Question | Architect Decision | Justification | Codified In |
|---|---|---|---|---|
| Q1 | Pattern category count — 5 or 6 (with 6th candidate Model-Specific Hallucination or Feedback-Loop Overreliance)? | **5 categories** | F-1's 5-category floor validated in production use; adding a 6th without a compelling signal-class differentiator risks scope creep and catalog dilution. The "Model-Specific" candidate introduces model-family coupling that ages poorly. The "Feedback-Loop" candidate overlaps with F-3 ASI07 scope. Both better authored as catalog enrichments in follow-on features (F-2.1 or F-3/F-6 scope). | `detection-patterns.md` 5 numbered categories; ADR-031 decision record |
| Q2 | Trigger keyword count — 8, 12, or 16+? | **12 keywords** | Covers primary LLM09 vocabulary (`factual output`, `citation generation`, `recommendation engine`, `decision support`, `RAG`, `grounding`, `hallucination`, `advisory`) plus high-stakes domain signals (`medical`, `legal`, `financial`, `clinical`). Domain signals are meaningful risk-profile delta. F-1 adopted 12; F-2 matches for pattern-continuity. Refinable during Wave 2 pattern authoring or Wave 4 example regeneration if false positives surface. | `detection-patterns.md` `## Detection Scope` Trigger Keywords subsection; `dispatch-rules.md` trigger-keyword rules |
| Q3 | DFD target set — Process only, or Process + Data Flow? | **Process only** | Precedent-preserving across 12 existing AI agents (11 original + F-1). Data Flow targeting would be a precedent break; the RAG-ingest boundary rationale is captured indirectly via Process-level indicators (RAG component declared adjacent to LLM Process). Starting narrower preserves F-1 pattern-continuity and keeps PRD scope bounded. Data Flow extension best deferred to F-2.1 if production feedback surfaces the need. | Agent metadata `dfd_targets: [Process]`; detection-patterns.md Applicable DFD Element Types |
| Q4 | Example regeneration target — extend `agentic-app` or author new `advisory-app`? | **Extend `agentic-app`** (PM default) with R2 fallback to new `advisory-app` at 0.5-day buffer consumption | Leverages existing F-1 baseline; adds one factual-output sub-component (e.g., LLM-backed advisory sub-agent emitting medical/legal summaries); demonstrates three-signal-class discipline cohesively on a single regenerated example. If cumulative-state cost on `agentic-app` exceeds convention-preservation benefit during Wave 4, architect invokes Q4 fallback. | `examples/agentic-app/` extended + regenerated in Wave 4 |
| Q5 | ADR-031 sequencing — Proposed Day 1 Wave 1.1 or Day 2 AM? | **Proposed Day 1 Wave 1.1** | BLP-01 default per ADR-027/028/029/030 precedent — dual-commit unblocks parallel pattern-catalog authoring downstream of the Heuristic A signal-class verification. Day 2 PM Accepted transition mirrors ADR-030's provisional-merge-date pattern; post-merge SHA fill records squash commit. | ADR-031 Proposed commit at Wave 1.1; Accepted transition at Wave 5 |

## Success Criteria Mapping

| Spec SC | Implementation Phase | Deliverable |
|---|---|---|
| SC-001 | Wave 2 | `misinformation.md` ≤150 lines, 1 MANDATORY Read; verified `wc -l` + `grep -c` |
| SC-002 | Wave 2 | `detection-patterns.md` ≥5 categories with worked examples, citations, triggers, DFD types, anti-indicators |
| SC-003 | Wave 3 | `finding-format-shared.md` edit + structural-diff validation (headings byte-identical) |
| SC-004 | Wave 4 | Regenerated `agentic-app` emits ≥1 `MI-{N}` finding; non-qualifying baselines emit 0 (two-part emission gate enforces FR-011) |
| SC-005 | Wave 1.1 + Wave 5 | ADR-031 Proposed at Wave 1.1; Accepted at Wave 5 with all 8 required body items (including CWE-1039 exclusion note) |
| SC-006 | Wave 4 | `test_backward_compatibility.py` passes on 5 non-factual-output baselines under SOURCE_DATE_EPOCH |
| SC-007 | Wave 4 | `agentic-app` regeneration produces MI-{N} finding(s) with grounding/verification mitigations + LLM09 citation |
| SC-008 | All waves | Empty diff on dependency manifest files (verified at PR pre-merge) |
| SC-009 | All waves | Grep audit at PR pre-merge confirms zero edits to 24 detection-tier files (22 original + F-1's 2) |
| SC-010 | Wave 4 + Wave 5 | `validate_source_attribution` returns no errors on regenerated findings; fixture tests confirm |
| SC-011 | Wave 2 | `grep -i maestro` on agent file + companion returns empty |
| SC-012 | Wave 1.1 | `schemas/finding.yaml:13` reads `schema_version: "1.7"`; line 18 regex matches `MI-\d+`; regex unit test passes |
| SC-013 | Wave 6 | BLP-01 Coverage Matrix updated: LLM09:2025 Planned → Covered with F-2 named as closure feature |
| SC-014 | Wave 4 | Three-signal-class discipline verified: LLM-{N}, OI-{N}, MI-{N} findings adjacent in category: llm section without prose synthesis |

## PR Pre-Merge Checklist

- [ ] All Wave 2-5 structural validations green (line count, MANDATORY count, MAESTRO grep)
- [ ] 24-file zero-edit grep audit returns empty for 12 threat agents + 12 companion `detection-patterns.md` files
- [ ] Infrastructure-tier consumer files (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler) show zero diff
- [ ] `test_backward_compatibility.py` passes on 5 non-factual-output baselines
- [ ] `test_misinformation.py` passes (regex + source_attribution fixtures)
- [ ] `agentic-app` regeneration commits present including `security-report.pdf.baseline`
- [ ] ADR-031 transitioned Proposed → Accepted with Revision History entry; CWE-1039 exclusion note present
- [ ] Dependency manifest diff is empty (pyproject.toml, requirements*.txt, package.json)
- [ ] `schemas/finding.yaml` schema_version = "1.7" + `id.pattern` extended to include `MI`; examples entry for `MI-1` present
- [ ] `consumers:` list on finding-format-shared.md: `misinformation` inserted between `output-integrity` and `risk-scorer`
- [ ] F-1 carry-over reconciliation: 5 callsites (orchestrator.md:296, :370; dispatch-rules.md:120 + LLM list; trigger-keyword rules) consistent at five-agent quintet
- [ ] Three-signal-class discipline verified on regenerated example (LLM-{N}, OI-{N}, MI-{N} adjacent in threat-report.md category: llm section)
- [ ] Triple sign-off in tasks.md frontmatter (PM + Architect + Team-Lead) — enforced in `/aod.tasks`

## References

- PRD: [206-misinformation-threat-agent-2026-04-23.md](../../docs/product/02_PRD/206-misinformation-threat-agent-2026-04-23.md)
- Spec: [spec.md](./spec.md)
- Research: [research.md](./research.md)
- Feature 082 precedent: [082-threat-agent-skill-references](../082-threat-agent-skill/)
- Feature 142 precedent (orchestrator-tier additive edits): [142-maestro-phase-2](../142-maestro-phase-2/)
- Feature 201 F-1 precedent (second-net-new AI-tier agent under ADR-023): [201-output-integrity-threat-agent](../201-output-integrity-threat-agent/)
- ADR-021 (SOURCE_DATE_EPOCH determinism): `docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md`
- ADR-023 (Lean-agent detection variant): `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md`
- ADR-026 (Minor-bump rule): `docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md`
- ADR-027 (Taxonomy crosswalk schema): `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md`
- ADR-028 (Source attribution schema extension): `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`
- ADR-029 (Coverage attestation report section): `docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md`
- ADR-030 (F-1 output-integrity agent, Decision 1 F-1 scope bounds + Decision 8 regex-alternation minor-bump rule): `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`
