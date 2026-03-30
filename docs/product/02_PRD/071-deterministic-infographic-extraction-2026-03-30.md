---
prd:
  number: "071"
  topic: deterministic-infographic-extraction
  created: 2026-03-30
  status: Approved
  type: feature
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-30
    status: APPROVED
    notes: "PRD authored by PM. P1 quality fix extending Feature 067 deterministic extraction pattern to infographic pipeline. Root cause well-evidenced, user stories preserve GitHub Issue detail, scope cleanly bounded to Layer 1 (spec generation). All reviewer concerns are spec-level items."
  architect_signoff:
    agent: architect
    date: 2026-03-30
    status: APPROVED_WITH_CONCERNS
    notes: "Architecturally sound. 13 items for spec: (1) define parser sharing mechanism (common module recommended), (2) specify Tier 3 secondary sort key for top-N, (3) enumerate exact funnel reduction percentage formulas per tier mode, (4) define full deduplication algorithm for Section 4a correlation groups, (5) clarify which metrics use deduplicated vs raw counts, (6) define fallback when Section 4a absent, (7) specify structured output format (JSON recommended), (8) confirm script outputs data only, (9) define Note severity handling, (10) decide rounding strategy for 100% sum, (11) resolve OpenClaw dataset existence or amend success criteria, (12) define trust zone absence fallback, (13) specify inherent score recalculation when risk-scores.md absent in funnel."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-30
    status: APPROVED_WITH_CONCERNS
    notes: "Feasible with wave strategy adjustment. Single-phase underestimates 3x3 matrix (3 templates x 3 tiers). Recommend 3-wave strategy: Wave 1 (core script + baseball card, 2 sessions), Wave 2 (system-architecture + risk-funnel, 2 sessions), Wave 3 (agent rewrite + integration, 1-2 sessions). Realistic estimate: 5-6 sessions. Risk funnel is highest-complexity template. 3 items for spec: parser sharing architecture, output format, Tier 1 test fixture availability."
source:
  idea_id: 71
  story_id: null
---

# Deterministic Infographic Extraction — Product Requirements Document

**Status**: Approved
**Created**: 2026-03-30
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1
**Source**: GitHub Issue #71

---

## Executive Summary

### The One-Liner
Replace the LLM-based data extraction in the threat-infographic agent with a deterministic parsing script so that infographic specifications contain consistent severity counts, finding rankings, and component heat maps across runs on identical input.

### Problem Statement
The threat-infographic agent (`.claude/agents/tachi/threat-infographic.md`, ~1000 lines) performs all data extraction via LLM parsing of markdown tables. Steps 1-2 of the agent instruct the LLM to parse severity counts, individual findings, component distributions, heat map values, severity bands, and percentages from markdown artifacts. All of these operations are described in natural language prose, not deterministic code. The LLM interprets these instructions differently across runs, producing different infographic specifications from identical input.

This is the same root cause as Feature 067 (report-assembler non-determinism), confirmed by 5 Whys analysis. Feature 067 proved the fix pattern: `scripts/extract-report-data.py` eliminated variance for the report-assembler by replacing LLM-as-parser with deterministic Python.

**Impact**: A user generating infographics for an executive briefing must see the same severity distribution every time. If the baseball card shows "5 Critical" in one run and "0 Critical" in the next (same input), the tool cannot be trusted for communication.

### Proposed Solution
Create a deterministic data extraction script (Python) for infographic specifications. The script reuses existing parsers from `scripts/extract-report-data.py` (generic markdown table parsing, severity extraction, scope data, component distribution) and adds infographic-specific computations: heat map cross-tabulation, top N finding selection with deterministic ranking, and percentage calculation with consistent rounding. The infographic agent is updated to invoke the script instead of LLM-based extraction.

### Success Criteria
- Running `/infographic` twice on identical input produces byte-identical spec files (all three templates)
- Infographic severity counts match `/security-report` severity counts for the same input and tier
- Tested against both OpenClaw and agentic-app example datasets

### Timeline
Single-phase implementation. Reuses proven parser infrastructure from Feature 067, adding infographic-specific extraction logic.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

tachi's mission is to be the default threat modeling toolkit for agentic AI applications. Pipeline outputs that vary on identical input erode trust and block professional use cases. Feature 067 established the principle: structured data extraction from well-defined markdown must be deterministic. This feature extends that principle to the infographic pipeline, ensuring all tachi outputs are trustworthy for executive communication, audit trails, and CI/CD integration.

### Roadmap Fit
This is a P1 quality fix for the delivered `/infographic` capability (PRD-018, PRD-039, PRD-048, PRD-053). It extends the deterministic output guarantee established by Feature 067 to the second tachi pipeline that uses LLM-based markdown parsing. Completing this feature means all tachi extraction pipelines produce deterministic specifications.

---

## Target Users & Personas

### Primary Persona: Security Engineer
- **Role**: Runs threat models and generates infographics for stakeholder communication
- **Pain Point**: Generated a baseball card infographic for a board meeting, then regenerated it to adjust formatting — the severity distribution changed from "5 High, 36 Medium" to "17 High, 47 Medium" from the same input
- **Need**: Identical inputs must produce identical infographic specifications, every time

### Secondary Persona: CISO / Security Manager
- **Role**: Reviews and distributes security assessment materials including infographics
- **Pain Point**: Cannot use tachi infographics alongside security reports because the severity counts may not match between `/security-report` and `/infographic` on the same data
- **Need**: Cross-output consistency — infographic numbers must match report numbers

---

## User Stories

### US-071-1: Deterministic Baseball Card Specification
**When** I run `/infographic --template baseball-card` on a directory containing threat model artifacts,
**I want to** get the same severity counts, heat map values, and top findings every time I run it on the same inputs,
**So I can** trust the data for executive communication.

**Acceptance Criteria**:
- **Given** a directory with unchanged threat model artifacts, **when** I run `/infographic --template baseball-card` twice, **then** both `threat-baseball-card-spec.md` files are byte-identical
- **Given** severity counts in the spec, **when** compared to `scripts/extract-report-data.py` output for the same tier, **then** the counts match exactly

### US-071-2: Deterministic System Architecture Specification
**When** I run `/infographic --template system-architecture` on a directory containing threat model artifacts,
**I want to** get the same component annotations, data flow severity coloring, and finding overlays every time,
**So I can** trust the architecture diagram accurately reflects the threat model.

**Acceptance Criteria**:
- **Given** a directory with unchanged threat model artifacts, **when** I run `/infographic --template system-architecture` twice, **then** both `threat-system-architecture-spec.md` files are byte-identical

### US-071-3: Deterministic Risk Funnel Specification
**When** I run `/infographic --template risk-funnel` on a directory containing threat model artifacts,
**I want to** get the same tier counts and reduction percentages every time,
**So I can** trust the funnel accurately represents the pipeline's risk reduction.

**Acceptance Criteria**:
- **Given** a directory with unchanged threat model artifacts, **when** I run `/infographic --template risk-funnel` twice, **then** both `threat-risk-funnel-spec.md` files are byte-identical

### US-071-4: Cross-Output Consistency
**When** I generate both a security report and an infographic from the same threat model artifacts,
**I want to** see identical severity counts in both outputs,
**So I can** use them together in a briefing without contradictions.

**Acceptance Criteria**:
- **Given** the same directory with threat model artifacts, **when** I run `/security-report` and `/infographic`, **then** the severity distribution in the infographic spec matches the `report-data.typ` severity counts
- **Given** both outputs use the same tier detection logic, **when** both extract severity counts, **then** critical + high + medium + low totals are identical

---

## Functional Requirements

### FR-1: Deterministic Infographic Data Extraction Script

**Description**: A Python script that reads tachi pipeline markdown artifacts and outputs structured data for infographic specification generation. Reuses parsers from `scripts/extract-report-data.py`.

**Inputs**:
- `--target-dir`: Directory containing markdown artifacts
- `--template`: Template type (`baseball-card`, `system-architecture`, `risk-funnel`)
- `--output`: Path for structured data output (JSON or structured text)

**Processing**:
1. Detect artifacts and determine tier (reuse existing tier detection logic)
2. Parse each artifact using shared parsers from `extract-report-data.py`
3. Compute template-specific data:
   - **Baseball card**: Severity donut percentages, top 5 findings (composite score desc, ID asc), component heat map (component x severity cross-tabulation)
   - **System architecture**: Component risk weights, data flow severity coloring, finding overlay positions
   - **Risk funnel**: Tier counts per stage (raw findings → scored → residual), reduction percentages between tiers
4. Validate internal consistency
5. Write structured output

**Outputs**: Deterministic structured data that the infographic agent consumes for spec generation.

**Reused Parsers** (from `scripts/extract-report-data.py`):
- `parse_markdown_table()` — generic markdown table parser
- `_find_table_with_column()` — table finder by column header
- `parse_frontmatter()` — YAML frontmatter extraction
- `parse_threats_severity()` — Section 6 Risk Summary parsing
- `parse_risk_scores_severity()` — risk-scores.md severity distribution
- `parse_risk_scores_findings()` — Scored Threat Table parsing
- `parse_compensating_controls_md()` — full Tier 1 parsing with residual severity
- `parse_scope_data()` — components, data flows, trust zones
- `parse_component_distribution()` — findings per component

**New Computations** (infographic-specific):
- Heat map cross-tabulation (component x severity matrix)
- Top N finding selection with deterministic ranking (composite score descending, then threat ID ascending for ties)
- Percentage calculation with consistent rounding (Python `round()`)
- Risk funnel reduction percentages between pipeline stages
- Architecture overlay data (component risk weights)

### FR-2: Tier-Based Severity Source Selection

**Description**: Same tier logic as Feature 067, shared or identical implementation.

| Tier | Condition | Severity Source |
|------|-----------|----------------|
| Tier 1 | `compensating-controls.md` exists | Residual severity from compensating-controls.md |
| Tier 2 | `risk-scores.md` exists, no compensating-controls | Scored severity from risk-scores.md |
| Tier 3 | Only `threats.md` | Section 6 Risk Summary from threats.md |

### FR-3: Deduplication Logic

**Description**: For the threats.md path (Tier 3), findings must not be double-counted between individual agent tables and correlation groups. The script implements deterministic deduplication using threat IDs, not LLM interpretation.

### FR-4: Agent Prompt Update

**Description**: The threat-infographic agent instructions are updated to invoke the extraction script instead of LLM-based parsing for Steps 1-2.

**Changes**:
- Data extraction steps replaced with script invocation
- Agent retains responsibility for spec file formatting and Gemini image generation
- Error handling updated to capture script exit codes and stderr

---

## Non-Functional Requirements

### Determinism
- **Requirement**: Given identical input files, the script produces byte-identical output across runs
- **Verification**: Run script twice, diff the outputs — zero differences
- **Scope**: Applies to the specification file only. Gemini image generation (layer 2) remains inherently variable by design.

### Performance
- **Parsing time**: < 5 seconds for the largest expected artifact set
- **No external dependencies beyond Python standard library** (consistent with Feature 067)

### Compatibility
- **Python 3.9+**: Must run on macOS, Linux, and Windows
- **Parser reuse**: Shared parsers imported from or factored alongside `scripts/extract-report-data.py` — no duplicated table parsing logic

### Error Handling
- **Missing required artifact**: Exit with code 1 and clear error message
- **Malformed markdown table**: Log warning, extract what's parseable, continue
- **Validation failure**: Exit with code 2, display which check failed

---

## Non-Determinism Layers

This PRD addresses **layer 1 only**:

| Layer | What | Fixable? | This PRD? |
|-------|------|----------|-----------|
| 1. Data extraction | Specification generation from markdown | Yes — deterministic script | **In scope** |
| 2. Image generation | Gemini API rendering from spec | No — inherently variable | Out of scope (by design) |

The specification file is the data contract between extraction and rendering. It must be deterministic. The rendered image is a best-effort visual deliverable and is expected to vary.

---

## Scope & Boundaries

### In Scope (P1)

**Must Have (P0)**:
- Deterministic extraction script created (reads markdown, writes structured data for infographic agent)
- Script reuses parsers from `scripts/extract-report-data.py` (no duplicated table parsing logic)
- Heat map computation is deterministic (component x severity cross-tabulation)
- Top N finding selection uses deterministic ranking (composite score desc, then ID asc)
- Percentage calculations use consistent rounding (Python `round()`)
- Infographic agent prompt updated to invoke script instead of LLM-based extraction
- All three data source paths tested (threats.md, risk-scores.md, compensating-controls.md)
- All three templates produce deterministic specs (baseball-card, system-architecture, risk-funnel)
- Running `/infographic` twice on identical input produces byte-identical spec files
- Infographic severity counts match `/security-report` severity counts for same input and tier
- Tested against OpenClaw and agentic-app example datasets

### Out of Scope

- **Gemini image generation changes**: Inherently non-deterministic, by design
- **Template design changes**: No new templates or template modifications
- **New infographic types**: Existing three templates only
- **Changes to upstream pipeline agents**: Threat agents, risk scorer, control analyzer unaffected
- **CI/CD integration**: Deterministic output enables it, but pipeline setup is future work

### Assumptions
- Python 3.9+ is available on all target platforms
- Markdown artifact formats are stable (consistent with Feature 067 assumption)
- Parsers from `scripts/extract-report-data.py` can be imported or shared without major refactoring

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Parser reuse complexity
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Feature 067 parsers are already modular functions. If direct import is impractical, factor shared parsers into a common module. Architect to determine best approach during spec.

**Risk 2**: Heat map computation edge cases
- **Likelihood**: Medium
- **Impact**: Low
- **Mitigation**: Heat map is a cross-tabulation of existing parsed data (components x severity). Edge cases: components with zero findings, severity levels not present. Handle with explicit zero-filling.

**Risk 3**: Deduplication logic for threats.md path
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Feature 067 already handles threats.md parsing. The deduplication rule (don't double-count between individual tables and correlation groups) must be implemented deterministically using threat IDs.

**Risk 4**: Template-specific data requirements diverge more than expected
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: All three templates consume the same underlying data (severity counts, findings, components). Template-specific computations (heat map, funnel percentages, architecture overlays) are derived from the same parsed base.

### Dependencies

**Internal Dependencies**:
- **Feature 067 (Delivered)**: `scripts/extract-report-data.py` provides shared parser infrastructure
- **Example datasets**: OpenClaw and agentic-app examples must contain all artifact types for testing
- **Infographic agent**: Current agent prompt (`.claude/agents/tachi/threat-infographic.md`) is the modification target

**No external dependencies**: Script uses Python standard library only.

---

## Open Questions

- [ ] Should the infographic script be a separate file or extend `extract-report-data.py`? — Architect to determine during spec (separate file with shared imports recommended for SRP)
- [ ] What structured output format works best for the agent to consume? (JSON, YAML, or inline markdown) — Architect to determine during spec
- [ ] Should the extraction script generate the full spec markdown, or just the data portion that the agent assembles into the spec? — Architect to determine during spec

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- PRD-067 (Deterministic Report Data Extraction): [067-deterministic-report-data-extraction-2026-03-30.md](067-deterministic-report-data-extraction-2026-03-30.md)
- PRD-018 (Threat Infographic Agent): [018-threat-infographic-agent-2026-03-23.md](018-threat-infographic-agent-2026-03-23.md)
- PRD-039 (Standalone Infographic Command): [039-standalone-infographic-command-2026-03-28.md](039-standalone-infographic-command-2026-03-28.md)
- PRD-048 (Infographic Tiered Detection): [048-infographic-tiered-detection-residual-risk-2026-03-28.md](048-infographic-tiered-detection-residual-risk-2026-03-28.md)
- PRD-053 (Risk Reduction Funnel): [053-risk-reduction-funnel-2026-03-28.md](053-risk-reduction-funnel-2026-03-28.md)

### Technical Documentation
- Infographic Agent: `.claude/agents/tachi/threat-infographic.md`
- Infographic Command: `.claude/commands/infographic.md`
- Extract Report Data Script: `scripts/extract-report-data.py`
- Constitution: `.aod/memory/constitution.md`

### Issue & Evidence
- GitHub Issue #71: Full problem statement with non-determinism risk points table, reuse analysis, and 2-layer non-determinism model
- Feature 067 evidence: 4-report comparison proving LLM-as-parser non-determinism on identical input
