---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-18
    status: APPROVED_WITH_CONCERNS
    notes: "Plan faithfully translates spec.md (19 FRs, 12 SCs, 3 P1 user stories) into 5-6 wave structure with all 8 Triad fixes preserved (BLOCKING-1/2, HIGH-1/2/3/4, TL-H1/H2), all 11 out-of-scope items carried forward, Q1 Outcome B scope minimization sound, timeline fits PRD Outcome B 2-day envelope with 2026-04-23 buffer, backward-compat gate (mermaid-agentic-app break risk) addressed as plan-stage static-DFD verification before Wave 4 with TL-H1 escalation linkage. 0 BLOCKING / 0 HIGH / 3 MEDIUM / 2 LOW — all refinement-level (M1 Q2 keyword false-positive checkpoint to surface in Wave 4 of tasks.md; M2 Q1 justification to add Outcome A tradeoff sentence in tasks enumeration; M3 FR-017 server/client-side distinction to surface as explicit tasks.md acceptance predicate). None block sign-off. Full review at .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-04-18
    status: APPROVED_WITH_CONCERNS
    notes: "Plan is technically sound with 0 BLOCKING / 0 HIGH concerns. 2 MEDIUM: (a) schema 1.5→1.6 regex-prefix extension invokes ADR-026 Complex-Shape Clarifier but ADR-026/ADR-028 scope covers enum-typed field and list-of-RECORD field additions — recommend adding an explicit D8 Decision in ADR-030 codifying the rule extension to regex-alternation additions, same pattern as ADR-028 Decision 1 Complex-Shape Addition Clarifier (absorbed into tasks.md ADR-030 authoring task); (b) mermaid-agentic-app baseline-break risk mitigation to be a concrete Wave 1.1 pre-check task (static DFD inspection — grep triggers before Wave 4 regen) rather than continuous monitoring (absorbed into tasks.md Wave 1.1 enumeration). 3 LOW: absorb into tasks.md — D1-D7 + implicit regex-extension rule enumeration, ADR-020 cross-ref for MAESTRO lineage (Feature 084), ADR-022 cross-ref for mmdc pipeline prerequisite (Wave 4). ADR-023 lean-pattern conformance PASS; orchestrator-tier carve-out correctly precedent-backed by Feature 142; source_attribution contract correctly bound to validate_source_attribution at tachi_parsers.py:826; CWE substitutions CWE-94/CWE-22 correctly invoke F-A1 catalog closed-domain; Heuristic A Outcome B signal-class justification sound; keyword+structural determinism meets ADR-021; zero-dependency diff structurally confirmed; ADR-030 dual-commit lifecycle mirrors ADR-027/028/029 precedent. Concerns are refinements, not corrections — none block /aod.tasks progression. Full review: .aod/results/architect.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: `output-integrity` Threat Agent (OWASP LLM05:2025)

**Branch**: `201-output-integrity-threat-agent` | **Date**: 2026-04-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/201-output-integrity-threat-agent/spec.md`
**PRD**: [docs/product/02_PRD/201-output-integrity-threat-agent-2026-04-18.md](../../docs/product/02_PRD/201-output-integrity-threat-agent-2026-04-18.md)
**BLP-01 Phase**: Tier 1 F-1 — first downstream consumer of the F-A1 + F-A2 + F-B Foundation tier; first net-new threat detection agent under the BLP-01 governance umbrella

## Summary

Author one new AI-tier threat agent `output-integrity` and its companion skill directory to detect OWASP LLM05:2025 Improper Output Handling — XSS, SQLi, command injection, SSRF, template injection, and path traversal surfaces where LLM output flows unsanitized into downstream execution sinks. The agent emits findings with `OI-{N}` ID prefix and `category: llm`, every finding carrying a populated `source_attribution` array citing OWASP LLM05:2025 (primary) plus relevant CWEs (CWE-22/78/79/89/94/918). Structure conforms to the ADR-023 lean-agent detection variant established in Feature 082 for the 11 existing threat agents.

**Architectural approach**: Mirror the `prompt-injection` agent (closest AI-tier sibling) verbatim in shape: 5-section canonical layout, ≤150 lines, single `**MANDATORY**: Read` directive under `## Detection Workflow`, zero MAESTRO references. Two orchestrator-tier additive edits register the new agent in dispatch (`orchestrator.md` list + `dispatch-rules.md` LLM quartet). One additive edit to `finding-format-shared.md` `consumers:` frontmatter (tier-grouping placement: between `tool-abuse` and `risk-scorer`). One additive schema regex bump (`schemas/finding.yaml` 1.5 → 1.6 extending `id.pattern` to include `OI` prefix). One public per-feature ADR (ADR-030) under Proposed → Accepted dual-commit pattern. One example regeneration target (`agentic-app` per Q4 architect decision).

**Touch points**: 1 new agent file, 1 new companion skill directory (README + detection-patterns.md), 3 coordinated additive edits (orchestrator.md, dispatch-rules.md, finding-format-shared.md), 1 schema regex edit + version bump, 1 new ADR, 1 example regeneration. Zero edits to the 11 existing detection-tier agent files, zero edits to the 11 existing companion `detection-patterns.md` files, zero edits to infrastructure-tier consumers (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler), zero new runtime dependencies.

## Technical Context

**Language/Version**: Markdown + YAML + Python 3.11 (existing — stdlib + `pyyaml`); agents and skills are markdown/YAML content files, not executable code
**Primary Dependencies**: `pyyaml` (runtime, already declared), `pytest` (dev-only, already declared per Feature 128 precedent); no new runtime or dev dependencies
**Storage**: File-based; reads `schemas/finding.yaml` (v1.5 pre-edit, v1.6 post-edit), `schemas/taxonomy/{owasp,cwe}.yaml` (F-A1 catalogs for `source_attribution` validation); writes to `.claude/agents/tachi/`, `.claude/skills/tachi-output-integrity/`, `docs/architecture/02_ADRs/`, `examples/agentic-app/`
**Testing**: pytest (existing harness at `tests/scripts/`) + backward-compatibility test `tests/scripts/test_backward_compatibility.py` under `SOURCE_DATE_EPOCH=1700000000` (ADR-021) — 5 non-agentic baselines byte-identity; regex unit test for schema 1.6 `id.pattern`
**Target Platform**: Command-line Python tooling (macOS/Linux/WSL); orchestrator + threat agents invoked via `/tachi.threat-model` Claude command; PDF rendering via Typst + Mermaid CLI (unchanged)
**Project Type**: Single project (methodology toolkit — agents + skills + schemas + templates in a unified repo); no frontend/backend split
**Performance Goals**: Agent dispatch + pattern evaluation <5s on the regenerated example (informational floor, within existing `/tachi.threat-model` budget); no new performance regressions
**Constraints**: (a) SC-006 byte-identity on 5 non-agentic baselines under `SOURCE_DATE_EPOCH=1700000000` is a BLOCKER; (b) SC-009 22-file zero-edit invariant on 11 threat agents + 11 companion skill references is a BLOCKER; (c) FR-010 zero MAESTRO references in agent + companion is a grep-auditable invariant; (d) SC-010 F-A2 referential-integrity validation must pass on every emitted `OI-{N}` finding; (e) SC-008 zero new runtime or developer dependencies is a BLOCKER
**Scale/Scope**: 1 new agent file (~100-150 lines), 1 new companion README (~30-50 lines), 1 new detection-patterns.md (~150-250 lines), 5 pattern categories (6 if Heuristic A Outcome A), 8-12 trigger keywords (architect-curated), 2-3 example findings in agent file, 3-6 worked examples in detection-patterns.md. 5 coordinated edits total (2 orchestrator + 1 shared reference + 1 schema + 1 example regen).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.aod/memory/constitution.md`:

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | ✅ PASS | Agent detects a generic output-handling signal class (LLM output → downstream sink); no hardcoded project-type assumptions |
| II. API-First Design | N/A | No REST/GraphQL surface; threat agents are content files consumed by the orchestrator at invocation time |
| III. Backward Compatibility (NON-NEGOTIABLE) | ✅ PASS | `has-source-attribution` gate + zero-finding default on non-qualifying architectures → 5 non-agentic baselines byte-identical. Local `.aod/` workflows unaffected. Schema 1.5 → 1.6 is additive regex extension; existing IDs remain valid |
| IV. Concurrency & Data Integrity | N/A | F-1 is single-invocation content authoring; no concurrent state |
| V. Privacy & Data Isolation | ✅ PASS | Worked examples use anonymized scenarios (per FR-019 NFR-5); no PII, no adopter data, no network calls by the agent |
| VI. Testing Excellence (MANDATORY) | ✅ PASS | Regex unit test for schema 1.6 `id.pattern`; fixture-driven tests for `source_attribution` referential integrity on `OI-{N}` findings; backward-compat byte-identity gate on 5 baselines; structural-diff check on agent line-count + MANDATORY-Read count + zero MAESTRO grep |
| VII. Definition of Done (NON-NEGOTIABLE) | ✅ PASS | PRD-defined SCs (SC-001 through SC-012) map to testable predicates. SC-006 + SC-009 + SC-010 are BLOCKER-level gates |
| VIII. Product-Spec Alignment | ✅ PASS | Approved PRD 201 exists; spec.md has PM APPROVED_WITH_CONCERNS sign-off |
| IX. Git Workflow | ✅ PASS | Feature branch `201-output-integrity-threat-agent`; no main commits; Proposed → Accepted dual-commit ADR pattern |
| X. Zero-Edit Invariant (ADR-023 lineage) | ✅ PASS | FR-013 / SC-009 explicit; orchestrator-tier carve-out documented per Feature 142 precedent; grep audit at PR pre-merge |

**Gate verdict**: No violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```
specs/201-output-integrity-threat-agent/
├── plan.md                  # This file (/aod.project-plan output)
├── research.md              # Phase 0 output (populated by /aod.spec; Phase 0 additive research here)
├── data-model.md            # Phase 1 output — agent metadata shape + finding shape
├── contracts/
│   └── finding-contract.md  # Finding IR contract for OI-{N} findings (source_attribution + mitigation rules)
├── quickstart.md            # Phase 1 output — verification walkthrough
├── checklists/
│   └── requirements.md      # Spec quality checklist (populated)
├── spec.md                  # PM-approved spec
└── tasks.md                 # Task breakdown (/aod.tasks output)
```

### Source Code (repository root)

```
tachi/
├── .claude/
│   ├── agents/
│   │   └── tachi/
│   │       ├── output-integrity.md              # NEW — lean AI-tier agent, ≤150 lines (≤180 hard cap)
│   │       ├── orchestrator.md                  # MODIFY (additive) — add output-integrity.md to AI-tier dispatch list
│   │       ├── prompt-injection.md              # UNCHANGED (22-file invariant)
│   │       ├── data-poisoning.md                # UNCHANGED
│   │       ├── model-theft.md                   # UNCHANGED
│   │       ├── agent-autonomy.md                # UNCHANGED
│   │       ├── tool-abuse.md                    # UNCHANGED
│   │       ├── spoofing.md / tampering.md / repudiation.md / info-disclosure.md / denial-of-service.md / privilege-escalation.md  # UNCHANGED (6 STRIDE files)
│   │       ├── risk-scorer.md                   # UNCHANGED (FR-014 infrastructure-tier invariant)
│   │       ├── control-analyzer.md              # UNCHANGED
│   │       ├── threat-report.md                 # UNCHANGED
│   │       ├── threat-infographic.md            # UNCHANGED
│   │       └── report-assembler.md              # UNCHANGED
│   │
│   └── skills/
│       ├── tachi-output-integrity/              # NEW — companion skill directory
│       │   ├── README.md                         # NEW — consumers + purpose header
│       │   └── references/
│       │       └── detection-patterns.md         # NEW — 5 pattern categories (6 if Outcome A)
│       │
│       ├── tachi-orchestration/
│       │   └── references/
│       │       └── dispatch-rules.md             # MODIFY (additive) — LLM trio → quartet + output-integrity trigger rules
│       │
│       ├── tachi-shared/
│       │   └── references/
│       │       └── finding-format-shared.md     # MODIFY (additive) — consumers: list adds output-integrity between tool-abuse and risk-scorer
│       │
│       └── tachi-{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,tool-abuse,agent-autonomy}/
│           └── references/
│               └── detection-patterns.md         # UNCHANGED (11 files — 22-file invariant)
│
├── schemas/
│   ├── finding.yaml                             # MODIFY — schema_version 1.5 → 1.6; id.pattern regex adds OI prefix
│   └── taxonomy/                                # UNCHANGED — read-only source for source_attribution validation
│       ├── owasp.yaml
│       └── cwe.yaml
│
├── docs/
│   └── architecture/
│       └── 02_ADRs/
│           └── ADR-030-output-integrity-agent.md    # NEW — Proposed → Accepted dual-commit
│
├── tests/
│   └── scripts/
│       ├── test_output_integrity.py             # NEW — regex + source_attribution validation tests
│       ├── test_backward_compatibility.py        # UNCHANGED — 5 baselines byte-identity gate
│       └── fixtures/
│           └── output_integrity/                 # NEW — fixture findings for regex + source_attribution tests
│               ├── valid_oi_finding.yaml
│               └── invalid_attribution_finding.yaml
│
├── examples/
│   ├── web-app/                                  # UNCHANGED (SC-006 baseline)
│   ├── microservices/                            # UNCHANGED
│   ├── ascii-web-api/                            # UNCHANGED
│   ├── mermaid-agentic-app/                      # UNCHANGED (SC-006 baseline — verify pre-edit)
│   ├── free-text-microservice/                   # UNCHANGED
│   ├── maestro-reference/                        # UNCHANGED
│   └── agentic-app/                              # REGENERATE (Q4 architect decision — Features 084/142/145 precedent)
│
└── scripts/                                      # UNCHANGED — no parser/orchestrator script edits required
    └── tachi_parsers.py                          # UNCHANGED (F-A2 validate_source_attribution already handles OI prefix via regex)
```

**Structure Decision**: Single-project layout (existing tachi repo structure). No new top-level directories. All changes confined to `.claude/agents/`, `.claude/skills/`, `schemas/`, `docs/architecture/02_ADRs/`, `tests/scripts/`, `examples/agentic-app/`. Follows Feature 082 (lean-agent refactor) + Feature 142 (orchestrator-tier additive edits for new agent registration) precedent.

## System Design

### Components

**New components (F-1-owned)**:

1. **`output-integrity` Threat Agent** (`.claude/agents/tachi/output-integrity.md`)
   - 5-section canonical shape per ADR-023 (frontmatter → metadata YAML → `## Purpose` → `## Skill References` table → `## Detection Workflow`) with optional `## Example Findings`
   - Metadata: `category: llm`, `threat_class: LLM`, `dfd_targets: [Process]`, `owasp_references: [OWASP LLM05:2025, OWASP ML09:2023]`, `output_schema: ../../../schemas/finding.yaml`
   - **No `agentic_pattern` in metadata** — assigned downstream by orchestrator Phase 3.6 per ADR-026 (FR-016)
   - Detection Workflow has exactly one `**MANDATORY**: Read` directive loading the companion `detection-patterns.md`
   - Emits `OI-{N}` findings with `category: llm`, populated `source_attribution`, stack-specific mitigation text
   - Line count: ≤150 (AI tier cap per ADR-023), hard ceiling 180

2. **Pattern Catalog** (`.claude/skills/tachi-output-integrity/references/detection-patterns.md`)
   - Frontmatter: `name`, `description`, `consumers: [tachi-output-integrity]`, `last_updated: 2026-04-22` (or actual merge date)
   - `## Overview` paragraph explaining scope (output-side LLM handling; ML09 documentation-only bundle rationale)
   - `## Detection Scope` with Trigger Keywords (8-12, architect-curated) + Applicable DFD Element Types (`Process` only per Q3)
   - `## Detection Patterns` with ≥5 numbered categories: (1) Client-Side Execution Sinks (XSS/DOM — CWE-79), (2) Server-Side Execution Sinks (SQLi/OS Command/Code — CWE-89/78/94), (3) SSRF from LLM-Synthesized URLs (CWE-918), (4) Template/Expression Injection (CWE-94), (5) Path Traversal + Unsafe File Writes (CWE-22). Conditional 6th: Human-Trust Exploitation via LLM Output (OWASP ASI09:2026) iff Heuristic A Outcome A

3. **Companion Skill README** (`.claude/skills/tachi-output-integrity/README.md`)
   - Mirror `tachi-prompt-injection/README.md` shape: short description + consumers list header

4. **Public Per-Feature ADR** (`docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`)
   - Proposed → Accepted dual-commit (ADR-027 / ADR-028 / ADR-029 precedent)
   - Body: (a) new-agent decision, (b) Heuristic A scope resolution (Outcome B per Q1 architect decision — see Open Questions), (c) lean-agent shape conformance per ADR-023, (d) LLM05 + ML09 bundling rationale per BLP-01 §4, (e) cross-references to ADR-021/023/026/027/028/029, (f) 22-file zero-edit invariant proof with grep-auditable enumeration, (g) Revision History tracking Proposed → Accepted dates

**Modified components (additive edits only)**:

5. **Orchestrator Dispatch List** (`.claude/agents/tachi/orchestrator.md` — hardcoded dispatch around lines 31-45)
   - Insert `- output-integrity.md` after `tool-abuse.md` in the AI-tier section
   - Zero changes to STRIDE tier or infrastructure tier

6. **Dispatch Rules LLM Quartet** (`.claude/skills/tachi-orchestration/references/dispatch-rules.md` — around lines 63-73)
   - Extend the LLM dispatch trio to quartet: add `- output-integrity (OWASP LLM05:2025)` after `model-theft`
   - No new LLM keywords required (shared `"LLM"`, `"model"`, `"GPT"`, `"Claude"` keyword set)
   - Add trigger-keyword activation rule for output-integrity: requires the LLM Process component to have an output flow into a downstream execution sink (both conditions per FR-011)

7. **Shared Finding-Format Consumer List** (`.claude/skills/tachi-shared/references/finding-format-shared.md` — frontmatter lines 6-19)
   - Insert `- output-integrity` between `tool-abuse` (line 18) and `risk-scorer` (line 19) — tier-grouping placement (AI tier tail) per PRD FR-3 / H2 architect decision
   - Body content byte-identical pre/post edit per ADR-023 Decision 3

8. **Finding Schema Regex** (`schemas/finding.yaml`)
   - Line 13: `schema_version: "1.5"` → `schema_version: "1.6"` (minor bump per ADR-026 Complex-Shape Clarifier extended to regex prefix addition)
   - Line 18: `id.pattern: "^(S|T|R|I|D|E|AG|LLM|AGP)-\\d+$"` → `"^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\\d+$"`

9. **Example Regeneration Target** (`examples/agentic-app/`)
   - Run full `/tachi.threat-model` + `/tachi.risk-score` + `/tachi.compensating-controls` + `/tachi.infographic` + `/tachi.security-report` pipeline
   - Expected result: ≥1 new `OI-{N}` finding on LLM Agent Orchestrator or downstream sink components; updated `threats.md`, `threats.sarif`, `risk-scores.md`, `compensating-controls.md`, `threat-report.md`, attack trees, attack chains, infographics, security-report.pdf, security-report.pdf.baseline

### Data Flow

```
User invokes /tachi.threat-model examples/agentic-app/architecture.md
  │
  ▼
Orchestrator Phase 1 (classification) — existing behavior, no edits to orchestrator script
  │
  ├─► Classifies each Process component: LLM-bearing? downstream sink? inter-agent channel?
  │    MAESTRO layer (existing Feature 084 behavior); multi-agent gate (Feature 142)
  │
  ▼
Orchestrator Phase 2 (dispatch) — consumes dispatch-rules.md (MODIFIED)
  │
  ├─► For each LLM Process: dispatch prompt-injection + data-poisoning + model-theft + output-integrity (quartet)
  │    output-integrity activates iff both trigger keyword match AND structural downstream-sink indicator
  │
  ▼
output-integrity agent (NEW) reads detection-patterns.md, matches pattern categories, emits OI-{N} findings
  │
  ├─► Each OI-{N} finding carries:
  │     • id: "OI-N" (matches schema 1.6 regex)
  │     • category: "llm" (existing enum — unchanged)
  │     • source_attribution: [{taxonomy: owasp, id: LLM05, relationship: primary}, {taxonomy: cwe, id: CWE-XX, relationship: related}, ...]
  │     • mitigation: stack-specific (e.g., "parameterized queries", "HTML entity encoding")
  │     • references: ["OWASP LLM05:2025", "https://cwe.mitre.org/data/definitions/XX.html"]
  │
  ▼
Orchestrator Phase 3 (deduplication) — existing behavior
  │
  ▼
Orchestrator Phase 3.5 (cross-layer chains) — existing (Feature 141); OI-{N} findings participate automatically
  │
  ▼
Orchestrator Phase 3.6 (agentic pattern synthesis) — existing (Feature 142); OI-{N} findings receive agentic_pattern: none
  │
  ▼
Orchestrator Phase 4 (validation) — validate_source_attribution() at scripts/tachi_parsers.py:826
  │
  ├─► For each OI-{N} finding: resolve every (taxonomy, id) pair against schemas/taxonomy/{taxonomy}.yaml
  │    Fails loud on missing LLM05 or CWE-XX (SC-010 BLOCKER)
  │
  ▼
Orchestrator Phase 5 (assembly) — writes threats.md with OI-{N} rows + threats.sarif tags
  │
  ▼
Downstream consumers (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler)
  │  process category: llm findings — NO edits to these infrastructure-tier agents (FR-014)
  │
  ▼
F-B coverage-attestation renderer (Feature 194) — reads source_attribution on OI-{N} findings
  │  emits per-finding attribution table row + per-framework coverage matrix entries
  │  → fires has-source-attribution: true on agentic-app regeneration post-F-1
  │
  ▼
Final PDF security-report.pdf includes OI-{N} findings in all sections
```

### Tech Stack

- **Agent + skill files**: Markdown with YAML frontmatter — consumed by Claude Code at invocation time, no runtime compilation
- **Schema**: YAML 1.2 (`schemas/finding.yaml` v1.6) — validated by existing `scripts/tachi_parsers.py` functions
- **Source attribution validator**: `scripts/tachi_parsers.py:826` `validate_source_attribution()` (existing, no edits)
- **Orchestrator script**: no edits required — dispatch + validation already consume the modified `dispatch-rules.md` and `finding.yaml` at runtime
- **Typst templates**: no edits — PDF renderer reads `threats.md` / `risk-scores.md` / `compensating-controls.md` and the coverage-attestation section auto-renders from `source_attribution` post-regeneration
- **Test harness**: pytest + `tests/scripts/test_backward_compatibility.py` (existing) + new `tests/scripts/test_output_integrity.py`
- **Taxonomy catalogs**: `schemas/taxonomy/owasp.yaml` + `schemas/taxonomy/cwe.yaml` (F-A1, unchanged) — consumed read-only

## Phase 0: Research

**Status**: Populated by `/aod.spec` at [research.md](./research.md). Key grounding facts confirmed:

- `prompt-injection.md` (96 lines) is the authoritative 5-section AI-tier template; `output-integrity.md` will mirror its shape verbatim
- `schemas/finding.yaml:13` schema_version = `"1.5"`; line 18 `id.pattern` = `"^(S|T|R|I|D|E|AG|LLM|AGP)-\\d+$"`; `OI` prefix absent (confirming BLOCKING-2 bump requirement)
- `schemas/taxonomy/cwe.yaml` contains CWE-22, CWE-78, CWE-79, CWE-89, CWE-94, CWE-918; does NOT contain CWE-73 or CWE-1336 (confirming BLOCKING-1 substitution)
- `schemas/taxonomy/owasp.yaml` contains LLM05 record
- `orchestrator.md` lines 31-45 hardcode the 11-agent dispatch list; `dispatch-rules.md` lines 63-73 hardcode the LLM dispatch trio (HIGH-1 confirmed)
- `finding-format-shared.md` frontmatter `consumers:` lines 6-19 uses tier-grouping (not alphabetical); insertion point for `output-integrity` is between `tool-abuse` (line 18) and `risk-scorer` (line 19) per HIGH-2
- ADR-030 does NOT yet exist (no forward-dependency conflict)
- Feature 128 baselines include `mermaid-agentic-app` in the byte-identity set; `agentic-app` is excluded (Feature 145 regeneration target convention)

**Open research items resolved during /aod.project-plan** (see Open Questions section):
- Q1 (Heuristic A outcome) — resolved in plan; codified in ADR-030 body at Day 1 Wave 1.1
- Q2 (trigger keyword final set) — resolved in plan with 10-keyword baseline (refinable Day 2)
- Q3 (DFD target set) — resolved in plan: `Process` only
- Q4 (example regeneration target) — resolved in plan: `agentic-app`
- Q5 (ADR-030 sequencing) — resolved in plan: Proposed Day 1 Wave 1.1

## Phase 1: Design & Contracts

**Prerequisites**: research.md populated (Phase 0 complete)

### Finding IR Contract (`contracts/finding-contract.md`)

**Purpose**: Document the shape of `OI-{N}` findings emitted by the new agent, including `source_attribution` invariants and mitigation-text rules.

**Contract**:

```yaml
id: "OI-{N}"                          # monotonically increasing per run
category: "llm"                       # existing enum value — unchanged
title: "{sink_type}: {short_summary}" # e.g., "XSS: LLM output rendered as innerHTML without encoding"
severity: "low" | "medium" | "high" | "critical"  # OWASP 3×3 matrix via severity-bands-shared.md
component: "{DFD Process component name}"
description: "{2-4 sentence threat description distinguishing server-side vs client-side execution}"
mitigation: "{stack-specific named encoding/library/pattern}"  # e.g., "Use parameterized queries (psycopg2.execute(sql, params))"
references:
  - "OWASP LLM05:2025"
  - "https://cwe.mitre.org/data/definitions/{CWE_NUMBER}.html"
source_attribution:
  - {taxonomy: "owasp", id: "LLM05", relationship: "primary"}   # REQUIRED on every OI-{N} finding
  - {taxonomy: "cwe", id: "CWE-{NUMBER}", relationship: "related"}  # per applicable pattern category
maestro_layer: "L5"                   # assigned downstream by orchestrator Phase 1 (existing Feature 084)
agentic_pattern: "none"               # assigned downstream by orchestrator Phase 3.6 (existing Feature 142)
delta_status: null                    # assigned downstream if baseline present (existing Feature 104)
```

**Invariants**:
- Every `OI-{N}` finding MUST pass `validate_source_attribution()` at orchestrator Phase 4
- The `source_attribution` array MUST contain at minimum `{taxonomy: owasp, id: LLM05, relationship: primary}`
- CWE entries MUST use IDs present in `schemas/taxonomy/cwe.yaml`: CWE-22, CWE-78, CWE-79, CWE-89, CWE-94, CWE-918
- The `mitigation` field MUST name at least one specific encoding, library, or pattern (not generic "sanitize output")
- The `id` MUST match schema 1.6 `id.pattern` regex

### Data Model (`data-model.md`)

**Purpose**: Document the agent metadata YAML shape + pattern category structure + companion skill README shape.

See [data-model.md](./data-model.md) for full entity definitions.

### Quickstart (`quickstart.md`)

**Purpose**: Step-by-step verification walkthrough — given a regenerated `agentic-app`, confirm ≥1 `OI-{N}` finding with valid source_attribution, valid mitigation text, and passing referential validation.

See [quickstart.md](./quickstart.md) for the verification procedure.

### Agent Context Update

Run `.aod/scripts/bash/update-agent-context.sh claude` after plan approval to refresh `CLAUDE.md` / agent-specific context with the Feature 201 entry.

## Implementation Approach (Phased Waves)

Following TL-H1 team-lead-fix: **two effort envelopes** with calendar-verified dates (Day 1 = Monday 2026-04-20).

### Wave 1 — Day 1 AM (Monday 2026-04-20, 0.5d)

**Gate-critical, front-loaded to unblock parallel Day 1 PM authoring.**

- **Wave 1.0 (30-60 min)**: Architect resolves Q1 Heuristic A outcome. Authors ADR-030 skeleton (Proposed status).
- **Wave 1.1 (parallel)**:
  - **Schema-lock commit**: `schemas/finding.yaml` regex bump 1.5 → 1.6; `id.pattern` includes `OI` prefix. Unit test `test_output_integrity.py::test_regex_matches_oi_prefix`.
  - **ADR-030 Proposed commit**: ADR body with Heuristic A determination, LLM05+ML09 bundling rationale, cross-references, Revision History table.
  - **Agent file skeleton**: `.claude/agents/tachi/output-integrity.md` 5-section scaffold with metadata YAML, Purpose section stub, Skill References table.
  - **Tester fixture authoring**: `tests/scripts/fixtures/output_integrity/valid_oi_finding.yaml` + `invalid_attribution_finding.yaml`.
- **TL-H2 hard escalation gate**: If Wave 1.0 Heuristic A determination is NOT committed to ADR-030 Proposed by Day 1 EOD, `/aod.tasks` surfaces explicit user-tie-break before Day 2 AM.

### Wave 2 — Day 1 PM / Day 2 AM (0.5-1d)

**Pattern catalog authoring + Skill References + agent body.**

- `.claude/skills/tachi-output-integrity/references/detection-patterns.md`: 5 pattern categories (6 if Outcome A).
- `.claude/skills/tachi-output-integrity/README.md`: companion README (mirror `tachi-prompt-injection/README.md`).
- `.claude/agents/tachi/output-integrity.md`: fill out `## Purpose`, `## Detection Workflow` with `**MANDATORY**: Read`, optional `## Example Findings` (2-3 worked examples).
- Structural validation: `wc -l ≤ 150`, `grep -c '\*\*MANDATORY\*\*: Read' = 1`, `grep -i maestro` returns empty.

### Wave 3 — Day 2 PM / Day 3 AM (0.5d)

**Orchestrator registration + shared reference additive edits.**

- `.claude/agents/tachi/orchestrator.md`: insert `- output-integrity.md` in AI-tier dispatch list.
- `.claude/skills/tachi-orchestration/references/dispatch-rules.md`: extend LLM trio → quartet; add output-integrity activation rule (keyword + structural indicator).
- `.claude/skills/tachi-shared/references/finding-format-shared.md`: add `- output-integrity` between `tool-abuse` and `risk-scorer` in `consumers:` list.
- Structural-diff validation: `## ` headings in `finding-format-shared.md` byte-identical pre/post edit.

### Wave 4 — Day 2 PM / Day 3 (0.5-1d)

**Example regeneration + backward-compat verification.**

- Run `/tachi.threat-model examples/agentic-app/architecture.md`.
- Run full downstream pipeline (`/tachi.risk-score`, `/tachi.compensating-controls`, `/tachi.infographic all`, `/tachi.security-report`).
- Commit regenerated artifacts: `threats.md`, `threats.sarif`, `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md`, `compensating-controls.sarif`, `threat-report.md`, `attack-trees/`, `attack-chains.md`, 6 infographic JPEGs, `security-report.pdf`, `security-report.pdf.baseline`.
- Verify ≥1 `OI-{N}` finding present; verify F-A2 validation passes.
- Run `tests/scripts/test_backward_compatibility.py` — 5 non-agentic baselines MUST be byte-identical under `SOURCE_DATE_EPOCH=1700000000`. If `mermaid-agentic-app` breaks, escalate per TL-H1 re-baseline decision with architect + team-lead approval.

### Wave 5 — Day 3 (Outcome B) / Day 4 with buffer (Outcome A, 0.25-0.5d)

**ADR-030 Accepted transition + final validation + PR.**

- Transition ADR-030 Proposed → Accepted with provisional merge-date.
- Post-merge SHA fill recording squash commit (similar to ADR-027/028/029 precedent).
- Run full pytest suite; grep audit on 22-file zero-edit invariant; validate SC-001 through SC-012.
- Open PR; triple-review at merge.

### Wave 6 — Day 3 EOD (Outcome B) / Day 4 (Outcome A, buffer)

**Buffer for R5 regeneration-surface risk (if `agentic-app` surfaces unexpected interactions with Feature 142 agentic-pattern synthesis or Feature 141 cross-layer chains).**

## Touch Points Summary

| File | Change | Lines | Scope |
|------|--------|-------|-------|
| `.claude/agents/tachi/output-integrity.md` | NEW | ~100-150 | Agent file |
| `.claude/skills/tachi-output-integrity/README.md` | NEW | ~30-50 | Skill README |
| `.claude/skills/tachi-output-integrity/references/detection-patterns.md` | NEW | ~150-250 | Pattern catalog |
| `.claude/agents/tachi/orchestrator.md` | MODIFY (add 1 line) | ~45 | Dispatch list |
| `.claude/skills/tachi-orchestration/references/dispatch-rules.md` | MODIFY (add ~3-5 lines) | ~73 | LLM quartet + activation rule |
| `.claude/skills/tachi-shared/references/finding-format-shared.md` | MODIFY (add 1 line) | ~19 | Consumer list |
| `schemas/finding.yaml` | MODIFY (2 lines: version + regex) | ~13, ~18 | Schema bump |
| `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md` | NEW | ~200-300 | Public ADR |
| `tests/scripts/test_output_integrity.py` | NEW | ~100-150 | Regex + source_attribution tests |
| `tests/scripts/fixtures/output_integrity/*.yaml` | NEW | ~20-30 each | Test fixtures |
| `examples/agentic-app/*` | REGENERATE | — | Pipeline artifacts + PDF baseline |
| `.claude/agents/tachi/{11 existing}.md` + `.claude/skills/tachi-{11 existing}/references/detection-patterns.md` | ZERO CHANGES | — | 22-file invariant |
| `.claude/agents/tachi/{risk-scorer,control-analyzer,threat-report,threat-infographic,report-assembler}.md` | ZERO CHANGES | — | Infrastructure-tier invariant |
| `scripts/*.py` | ZERO CHANGES | — | Parser + orchestrator scripts |
| `templates/tachi/*` | ZERO CHANGES | — | Typst templates |
| `requirements*.txt`, `pyproject.toml`, `package.json` | ZERO CHANGES | — | No new dependencies |

## Risks & Mitigations

See spec.md Edge Cases + PRD §Risks & Mitigations for the full list. Plan-phase active risks:

- **R1 (Heuristic A ambiguity blocks pattern authoring)** — Mitigation: Wave 1.0 architect ruling, TL-H2 hard gate at Day 1 EOD.
- **R2 (Orchestrator dispatch-order drift)** — Mitigation: Wave 3 structural-diff verification on regenerated example.
- **R3 (Pattern false positives on non-qualifying LLM Process)** — Mitigation: FR-011 both-keyword-AND-structural-indicator rule enforced in `## Detection Workflow` step 3.
- **R4 (source_attribution validation failures)** — Mitigation: Pattern worked examples cite only verified-present IDs (CWE-22/78/79/89/94/918; absent CWE-73/1336 substituted).
- **R5 (Example regeneration surface larger than expected)** — Mitigation: Wave 4 structured pre-vs-post diff; Wave 6 buffer day.
- **R6 (consumers: frontmatter edit position)** — Mitigation: Wave 3 structural-diff validation on `## ` headings.
- **R7 (agentic-app cumulative-state cost)** — PM default retained per Q4; architect overrides in ADR-030 if cost exceeds benefit.
- **R8 (ML09 bundling scope confusion)** — Mitigation: FR-018 documentation-only scope; pattern primary remains LLM05.
- **R9 (Outcome A pattern category authoring time)** — Mitigation: R9-parallel-research note in Wave 2 if Outcome A leaning at Day 1 AM.
- **NEW: `mermaid-agentic-app` baseline break** — if the baseline example matches output-integrity triggers, coordinate re-baseline with architect + team-lead approval. Plan stage verifies via static DFD inspection before Wave 4.

## Open Questions (PRD Q-set — Architect Decisions)

Architect-owned per PRD §Architecture & Design Decisions. Resolved during `/aod.project-plan` per decision authority.

| # | Question | Architect Decision | Justification | Codified In |
|---|---|---|---|---|
| Q1 | ASI09 Heuristic A resolution — Outcome A (subsume) or Outcome B (split)? | **Outcome B (split)** | Psychology/linguistics primitives (human-trust exploitation — tone, authority signaling, manipulation detection) don't fit deterministic pattern-matching semantics. Output-integrity owns encoding/sanitization primitives (machine-victim output handling); `trust-exploitation` as F-4 owns psychology/linguistics (human-victim output handling). Signal-class distinction per GUIDE-threat-coverage-research §11. F-1 `## Purpose` forward-references F-4 explicitly. | ADR-030 Decision 2; agent `## Purpose` section; detection-patterns 5 categories (no 6th) |
| Q2 | Trigger keyword set final form (PRD proposes 7) | **10 keywords** (Wave 2 authoring, refinable Day 2): `LLM output`, `rendered HTML`, `model output to browser`, `model output to SQL`, `LLM-generated query`, `template engine`, `outbound HTTP from agent`, `LLM-synthesized URL`, `command construction`, `file path from model` | PRD's 7 + `LLM-generated query`, `model output to browser`, `LLM-synthesized URL` for coverage of query-synthesis + browser-rendering + SSRF boundary cases. 10 is within the "8-12" range the architect leaned to at PRD review; refinable during Wave 2 pattern authoring or Wave 4 example regeneration if false positives appear. | detection-patterns.md `## Detection Scope` Trigger Keywords subsection |
| Q3 | DFD target set: `Process` only, or also `Data Flow`? | **Process only** | Precedent-preserving across 11 existing AI agents. Data Flow targeting would be a precedent break; the rationale "threat surface is the boundary, not the producer" is not strong enough to diverge here. The downstream-sink structural indicator (FR-011) captures boundary information via the Process component's output edges without requiring Data Flow as a primary target. | agent metadata `dfd_targets: [Process]`; detection-patterns.md Applicable DFD Element Types |
| Q4 | Example regeneration target — `agentic-app` or alternative? | **`agentic-app`** | Features 084/142/145 precedent — `agentic-app` is the established "regeneration target for new AI agents". Using it preserves the convention and builds on Feature 142's multi-agent extension (Orchestrator → Specialist + Learning Loop + Inter-Agent Communication Channel) where LLM-output-to-downstream flow is already demonstrable. Cumulative-state cost (R7) is acknowledged but below re-targeting cost. | `examples/agentic-app/` regeneration in Wave 4 |
| Q5 | ADR-030 sequencing — Proposed Day 1 Wave 1.1 or only Day 3 EOD? | **Proposed Day 1 Wave 1.1** | BLP-01 default per ADR-027/028/029 precedent — dual-commit unblocks parallel pattern-catalog authoring downstream of the Heuristic A determination. Day 3 EOD Accepted transition mirrors ADR-029's provisional-merge-date pattern; post-merge SHA fill records squash commit. | ADR-030 Proposed commit at Wave 1.1; Accepted transition at Wave 5 |

## Success Criteria Mapping

| Spec SC | Implementation Phase | Deliverable |
|---|---|---|
| SC-001 | Wave 2 | `output-integrity.md` ≤150 lines, 1 MANDATORY Read; verified `wc -l` + `grep -c`|
| SC-002 | Wave 2 | `detection-patterns.md` ≥5 categories with worked examples, citations, triggers, DFD types |
| SC-003 | Wave 3 | `finding-format-shared.md` edit + structural-diff validation (headings byte-identical) |
| SC-004 | Wave 4 | Regenerated `agentic-app` emits ≥1 `OI-{N}` finding; non-qualifying baselines emit 0 |
| SC-005 | Wave 1.1 + Wave 5 | ADR-030 Proposed at Wave 1.1; Accepted at Wave 5 with all 7 required body items |
| SC-006 | Wave 4 | `test_backward_compatibility.py` passes on 5 non-agentic baselines under SOURCE_DATE_EPOCH |
| SC-007 | Wave 4 | `agentic-app` regeneration produces OI-{N} finding(s) with mitigations + LLM05 citation |
| SC-008 | All waves | Empty diff on dependency manifest files (verified at PR pre-merge) |
| SC-009 | All waves | Grep audit at PR pre-merge confirms zero edits to 22 detection-tier files |
| SC-010 | Wave 4 + Wave 5 | `validate_source_attribution` returns no errors on regenerated findings; fixture tests confirm |
| SC-011 | Wave 2 | `grep -i maestro` on agent file + companion returns empty |
| SC-012 | Wave 1.1 | `schemas/finding.yaml:13` reads `schema_version: "1.6"`; line 18 regex matches `OI-\d+`; regex unit test passes |

## PR Pre-Merge Checklist

- [ ] All Wave 2-5 structural validations green (line count, MANDATORY count, MAESTRO grep)
- [ ] 22-file zero-edit grep audit returns empty for 11 threat agents + 11 companion `detection-patterns.md` files
- [ ] Infrastructure-tier consumer files (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler) show zero diff
- [ ] `test_backward_compatibility.py` passes on 5 non-agentic baselines
- [ ] `test_output_integrity.py` passes (regex + source_attribution fixtures)
- [ ] `agentic-app` regeneration commits present including `security-report.pdf.baseline`
- [ ] ADR-030 transitioned Proposed → Accepted with Revision History entry
- [ ] Dependency manifest diff is empty (pyproject.toml, requirements*.txt, package.json)
- [ ] `schemas/finding.yaml` schema_version = "1.6" + `id.pattern` extended to include `OI`
- [ ] `consumers:` list on finding-format-shared.md: `output-integrity` inserted between `tool-abuse` and `risk-scorer`
- [ ] Triple sign-off in tasks.md frontmatter (PM + Architect + Team-Lead) — enforced in `/aod.tasks`

## References

- PRD: [201-output-integrity-threat-agent-2026-04-18.md](../../docs/product/02_PRD/201-output-integrity-threat-agent-2026-04-18.md)
- Spec: [spec.md](./spec.md)
- Research: [research.md](./research.md)
- Feature 082 precedent: [082-threat-agent-skill-references](../082-threat-agent-skill-references/)
- Feature 142 precedent (orchestrator-tier additive edits): [142-maestro-phase-3-agentic-patterns](../142-maestro-phase-3-agentic-patterns/)
- Feature 194 precedent (plan structure + F-B downstream consumer): [194-coverage-attestation-report-section](../194-coverage-attestation-report-section/)
- ADR-021 (SOURCE_DATE_EPOCH determinism): `docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md`
- ADR-023 (Lean-agent detection variant): `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md`
- ADR-026 (Minor-bump rule): `docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md`
- ADR-027 (Taxonomy crosswalk schema): `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md`
- ADR-028 (Source attribution schema extension): `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`
- ADR-029 (Coverage attestation report section): `docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md`
