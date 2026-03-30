# Research Summary: Deterministic Infographic Extraction

## Knowledge Base Findings
- No existing KB patterns found for deterministic extraction or infographic parsing.
- Feature 067 established the pattern but was not captured as a KB entry.

## Codebase Analysis

### Parser Functions Available for Reuse (from `scripts/extract-report-data.py`, 1410 lines)

**Generic Parsers**:
- `parse_markdown_table(content, section_header)` — Extract markdown table rows as dicts
- `_find_table_with_column(content, section, column_header)` — Locate table by required column
- `strip_bold(text)` — Remove markdown `**` markers
- `_parse_int(value)` — Safe integer extraction from strings

**Tier Detection & Severity**:
- `detect_artifacts(directory)` — Scan for tachi pipeline files, check non-zero size
- `determine_tier(artifacts)` — 3-tier hierarchy: Tier 1 (compensating-controls) > Tier 2 (risk-scores) > Tier 3 (threats)
- `parse_threats_severity()` — Section 6 Risk Summary table
- `parse_risk_scores_severity()` — Section 1 Severity Distribution
- `parse_compensating_controls_md()` — Sections 1-4 comprehensive extraction
- `_accumulate_severity_rows()` / `_empty_severity()` — Severity count utilities

**Findings Parsers**:
- `parse_threats_findings()` — Section 7 Recommended Actions (Tier 3)
- `parse_risk_scores_findings()` — Section 2 Scored Threat Table (Tier 2)

**Scope & Metadata**:
- `parse_frontmatter()` — YAML frontmatter extraction (regex-based, no external library)
- `parse_project_name()` — Extract from `# Threat Model:` heading
- `parse_scope_data()` — Components, data flows, trust zones, boundary crossings
- `parse_component_distribution()` — Findings per component, sorted descending

**Validation**:
- `validate()` — Severity sum check (critical+high+medium+low == total-note), finding ID uniqueness

### Current Infographic Agent (`threat-infographic.md`, ~2000 lines)

**Data Extraction Steps (LLM-based, to be replaced)**:
- Step 1: Parse metadata — frontmatter, project name, agent count from Section 1
- Step 2: Extract severity counts — source-specific (threats.md Section 6, risk-scores.md Section 1, compensating-controls.md Section 2)
- Step 3: Cross-tabulate component x severity for heat map
- Step 4: Select top 5 findings — rank by severity/composite/residual score
- Step 5: Aggregate per-component risk weights (C=4, H=3, M=2, L=1)
- Step 5b: Spatial layout (system-architecture only) — trust zones, flows, boundaries

**Three Templates**:
1. **baseball-card** — Donut chart, STRIDE+AI heat map, critical finding cards, overlay strip (16:9)
2. **system-architecture** — Trust zones, component badges, data flow severity arrows, finding overlays
3. **risk-funnel** — 4-tier vertical funnel: identified → scored → controls → residual

**Output per template**: `threat-{template}-spec.md` (6 sections + YAML frontmatter)

### Feature 067 Patterns Established
- Python 3.9+ stdlib only (re, pathlib, argparse, sys, os)
- Exit codes: 0 (success), 1 (missing artifact), 2 (validation failure)
- Malformed rows: log warning, skip, continue
- Bold markers stripped before comparison
- `SEVERITY_ORDER` constant for canonical ordering
- Deterministic sort: primary by count descending, secondary by name ascending

### Example Datasets Available
- `examples/agentic-app/sample-report/` — Complete Tier 1/2/3 artifacts + all 3 infographic specs
- `examples/mermaid-agentic-app/` — threats.md only (Tier 3)
- `examples/free-text-microservice/` — threats.md only (Tier 3)
- `examples/ascii-web-api/` — threats.md only (Tier 3)

## Architecture Constraints

**Relevant ADRs**:
- ADR-016: Infographic pipeline decoupled as standalone `/infographic` command; spec-first with optional Gemini images
- ADR-014: Gemini API optional; 6-condition graceful degradation preserves spec
- ADR-012: Deterministic cross-agent correlation via fixed rule-based matching
- ADR-003: STRIDE-per-Element dispatch uses static lookup tables (deterministic)

**Key Constraints**:
- Spec-first design: specification is primary deliverable, image is optional
- Zero external dependencies for core value delivery
- Same input must always produce identical output
- Idempotent re-execution (overwrite outputs, no state accumulation)

## Industry Research

### Markdown Table Parsing
- Stdlib regex parsing (existing approach) is correct for well-defined GFM tables
- Section-anchored table lookup prevents wrong-table parsing
- Always `.strip()` cell values; normalize severity casing before counting

### Cross-Tabulation (Heat Map)
- Nested dict with pre-initialized zero counts for all severity columns
- Deterministic sort: total count descending, component name ascending for ties
- Iterate `SEVERITY_ORDER` constant for column output, never dict keys directly
- Zero-fill components with no findings for completeness

### Percentage Rounding (Critical Refinement)
- **PRD says**: "Python `round()`" — but bare `round()` uses banker's rounding, which does NOT guarantee sum-to-100%
- **Recommendation**: Use **Largest Remainder Method** (Hamilton/Hare-Niemeyer) for percentage sets that must sum to 100% (donut charts, funnel reduction)
- Tie-breaking: fractional part descending, then label ascending
- ~15 lines of stdlib Python; no external dependency
- Python `round()` acceptable for isolated numeric displays only

## Technical Decisions (Phase 0 Resolved)

### TD-1: Parser Sharing Mechanism
- **Decision**: Factor shared parsers into `scripts/tachi_parsers.py` as a common module. Both `extract-report-data.py` and `extract-infographic-data.py` import from it.
- **Rationale**: Direct import is simplest. Both scripts are in `scripts/`, so relative imports work. The shared module contains generic parsers (table parsing, frontmatter, severity, scope, artifacts, tier detection). Report-specific and infographic-specific logic stay in their respective scripts.
- **Alternatives considered**: (a) Inline copy-paste — rejected, violates DRY and creates maintenance burden. (b) Symlink — rejected, fragile on Windows. (c) `sys.path` manipulation — rejected, unnecessary since both scripts are co-located.

### TD-2: Structured Output Format
- **Decision**: JSON output via `json.dumps()` with `sort_keys=True`, `indent=2` for deterministic byte-for-byte output.
- **Rationale**: JSON is stdlib (`json` module), unambiguous, parseable by the agent via `json.loads()`, and human-readable. `sort_keys=True` ensures key ordering is deterministic across Python versions.
- **Alternatives considered**: (a) YAML — rejected, no stdlib parser without PyYAML. (b) Inline markdown — rejected, ambiguous parsing.

### TD-3: Percentage Rounding
- **Decision**: Largest Remainder Method for all distribution percentages (donut chart, funnel tier-to-tier). Python `round()` for isolated single-value percentages.
- **Rationale**: Research confirmed bare `round()` does not guarantee sum-to-100%. Largest Remainder is the standard algorithm for apportioning integer percentages.
- **Alternatives considered**: (a) Bare `round()` everywhere — rejected, sums can deviate from 100. (b) `math.floor()` + manual adjustment — rejected, reinvents the algorithm poorly.

### TD-4: Deduplication Strategy
- **Decision**: Build a set of all unique threat IDs from Section 3 agent tables and Section 4a correlation groups (if present). Count each ID once.
- **Rationale**: Threat IDs are unique identifiers assigned by individual agents. Correlation groups reference the same IDs. Union-set approach is simple and deterministic.
- **Alternatives considered**: (a) LLM-based dedup — rejected, non-deterministic. (b) Ignore Section 4a — rejected, would over-count findings.
