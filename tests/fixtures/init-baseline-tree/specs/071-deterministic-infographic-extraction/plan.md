---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-30
    status: APPROVED
    notes: "49/49 FRs covered. 5/5 user stories with implementation paths. 8/8 success criteria with testing strategies. No scope creep. Data model contract aligned with spec."
  architect_signoff:
    agent: architect
    date: 2026-03-30
    status: APPROVED_WITH_CONCERNS
    notes: "Architecturally sound. Shared module boundary correct. LRM well-researched. Phasing sequenced correctly. 2 concerns addressed inline: (C-3) Tier 3 severity aligned to extract-report-data.py behavior (Section 7 findings, not Section 6); (C-2) metadata computation descriptions added."
  techlead_signoff: null
---

# Implementation Plan: Deterministic Infographic Extraction

**Branch**: `071-deterministic-infographic-extraction` | **Date**: 2026-03-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/071-deterministic-infographic-extraction/spec.md`

## Summary

Replace the LLM-based data extraction in the threat-infographic agent (Steps 1-2) with a deterministic Python script that reads tachi pipeline markdown artifacts and outputs structured JSON. Factor shared parsers from `extract-report-data.py` into a common module (`tachi_parsers.py`). Add infographic-specific computations: heat map cross-tabulation, top N finding selection, Largest Remainder percentage rounding, and risk funnel tier calculation. Update the infographic agent to invoke the script and consume its JSON output.

## Technical Context

**Language/Version**: Python 3.9+ (standard library only: `re`, `pathlib`, `argparse`, `sys`, `os`, `json`, `math`)
**Primary Dependencies**: None (zero external dependencies)
**Storage**: File-based (markdown artifacts in, JSON out)
**Testing**: Direct script execution against example datasets + `diff` for determinism verification
**Target Platform**: macOS, Linux, Windows (Python 3.9+ cross-platform)
**Project Type**: Shared module + new script + agent prompt update
**Performance Goals**: < 5 seconds for largest expected artifact set (34+ findings, 7 components)
**Constraints**: Byte-identical output from identical input (determinism); Python stdlib only; cross-output consistency with `extract-report-data.py`
**Scale/Scope**: ~200 line shared module, ~600-800 line new script, ~50-100 line agent prompt delta

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Script is domain-specific to tachi infographic pipeline but does not modify core platform |
| III. Backward Compatibility | PASS | No changes to infographic spec format; agent still produces same output structure |
| VI. Testing Excellence | PASS | Testing against example datasets with all three tiers; determinism verified by diff |
| VII. Definition of Done | PASS | Measurable success criteria: byte-identical output, cross-output consistency, validation checks |
| IX. Git Workflow | PASS | Feature branch `071-deterministic-infographic-extraction`; PR required |
| X. Product-Spec Alignment | PASS | Spec approved by PM; plan requires PM + Architect sign-off |

No violations. All constitutional gates pass.

## Project Structure

### Documentation (this feature)

```
specs/071-deterministic-infographic-extraction/
├── plan.md              # This file
├── research.md          # Research phase output (completed)
├── data-model.md        # JSON output contract definition
├── quickstart.md        # Developer quickstart guide
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (pending)
```

### Source Code (repository root)

```
scripts/
├── tachi_parsers.py                 # NEW: Shared parser module (factored from extract-report-data.py)
├── extract-report-data.py           # MODIFIED: Import shared parsers from tachi_parsers.py
└── extract-infographic-data.py      # NEW: Deterministic infographic data extraction

.claude/agents/tachi/
└── threat-infographic.md            # MODIFIED: Steps 1-2 replaced with script invocation

examples/
├── agentic-app/sample-report/       # EXISTING: Full Tier 1/2/3 test fixture
│   ├── threats.md
│   ├── risk-scores.md
│   └── compensating-controls.md
└── mermaid-agentic-app/             # EXISTING: Tier 3-only test fixture
    └── threats.md
```

**Structure Decision**: Single-project layout. New files in existing `scripts/` directory. No new directories needed at repository root.

## Components

### Component 1: Shared Parser Module (`scripts/tachi_parsers.py`)

**Purpose**: Factor generic parser functions from `extract-report-data.py` into a shared importable module.

**Functions to extract** (moved from `extract-report-data.py`, signatures preserved):
- `SEVERITY_ORDER` constant
- `STRIDE_PREFIXES` constant
- `escape_typst_string()` — kept in shared module for report-assembler backward compat
- `strip_bold()`
- `parse_markdown_table()`
- `_find_table_with_column()`
- `parse_frontmatter()`
- `parse_project_name()`
- `detect_artifacts()`
- `determine_tier()`
- `parse_threats_severity()`
- `parse_risk_scores_severity()`
- `_empty_severity()`
- `_accumulate_severity_rows()`
- `_parse_int()`
- `parse_threats_findings()`
- `parse_risk_scores_findings()`
- `parse_component_distribution()`
- `parse_scope_data()`
- `parse_compensating_controls_md()`

**What stays in `extract-report-data.py`** (report-specific):
- `SLA_BY_SEVERITY` constant
- `parse_threat_report_md()`
- `build_remediation_actions()`
- `validate()` — report-specific validation
- `generate_report_data_typ()` and Typst helper functions
- `detect_images()`, `detect_brand_assets()`
- `build_parser()`, `main()`

**Migration strategy**: Extract functions to `tachi_parsers.py`, replace them in `extract-report-data.py` with `from tachi_parsers import ...`. Run `extract-report-data.py` against existing test fixtures to verify byte-identical output. This is a zero-behavior-change refactor.

### Component 2: Infographic Extraction Script (`scripts/extract-infographic-data.py`)

**Purpose**: New script that imports shared parsers and adds infographic-specific computations.

**CLI interface**:
```
python scripts/extract-infographic-data.py \
  --target-dir <path> \
  --template <baseball-card|system-architecture|risk-funnel> \
  --output <path.json>
```

**Processing pipeline**:
1. Parse CLI args
2. Detect artifacts and determine tier (shared parsers)
3. Read and parse markdown files (shared parsers)
4. Compute shared data: severity counts, findings, scope, component distribution
5. Compute infographic-specific data:
   - Severity percentages (Largest Remainder Method)
   - Heat map cross-tabulation (component x severity)
   - Top 5 finding selection (deterministic ranking)
   - Component risk weights
6. Compute template-specific data:
   - **baseball-card**: risk weight summary
   - **system-architecture**: trust zone groupings, data flow severity coloring, boundary crossings
   - **risk-funnel**: 4-tier counts, reduction percentages, missing enrichments
7. Validate internal consistency
8. Write JSON output

**New functions** (infographic-specific):
- `largest_remainder(values, target)` — Percentage rounding guaranteeing sum-to-target
- `compute_severity_percentages(severity, tier)` — Percentages with color codes, excluding Note
- `compute_heat_map(findings, scope_components)` — Component x severity cross-tabulation
- `select_top_findings(findings, tier, n=5)` — Deterministic top N selection
- `compute_component_risk_weights(heat_map)` — Weighted score classification (C=4, H=3, M=2, L=1)
- `compute_architecture_overlay(scope_data, findings, tier)` — Trust zones, data flows, boundaries
- `compute_risk_funnel(target_dir, tier, severity)` — 4-tier funnel with reduction percentages
- `deduplicate_findings(content)` — Threat ID union from Section 3 + Section 4a
- `validate_infographic(data)` — Infographic-specific validation checks
- `build_json_output(data, template)` — Assemble final JSON structure

### Component 3: Agent Prompt Update (`threat-infographic.md`)

**Purpose**: Replace LLM-based extraction steps with script invocation.

**Changes**:
- Steps 1-2 replaced with: "Run `scripts/extract-infographic-data.py` with `--target-dir`, `--template`, `--output /tmp/infographic-data.json`"
- New step: "Read the JSON output and use structured data for Sections 1-5"
- Error handling: Check exit code — 0 proceed, 1 display missing artifact error, 2 display validation failure
- Section 6 (Visual Design Directives) unchanged — still LLM-generated
- Gemini image generation unchanged

**Estimated prompt delta**: ~50-100 lines changed (Steps 1-2 replaced, new JSON consumption step added)

## Data Flow

```
threats.md ─────────┐
risk-scores.md ─────┤
comp-controls.md ───┤
                    ▼
        ┌──────────────────────┐
        │  tachi_parsers.py    │  (shared module)
        │  - parse tables      │
        │  - detect tier       │
        │  - extract severity  │
        │  - parse scope       │
        └──────────┬───────────┘
                   │
        ┌──────────▼───────────┐
        │  extract-infographic │
        │  -data.py            │
        │  - heat map          │
        │  - top N findings    │
        │  - LR percentages    │
        │  - risk funnel       │
        │  - architecture data │
        └──────────┬───────────┘
                   │
                   ▼
            infographic-data.json
                   │
        ┌──────────▼───────────┐
        │  threat-infographic  │  (agent)
        │  - assemble spec.md  │
        │  - Section 6 design  │
        │  - Gemini images     │
        └──────────────────────┘
```

## Tech Stack

- **Python 3.9+**: Standard library only (`re`, `pathlib`, `argparse`, `sys`, `os`, `json`, `math`)
- **JSON**: Output format (`json.dumps(sort_keys=True, indent=2)` for deterministic output)
- **Markdown**: Input format (tachi pipeline artifacts)

## Testing Strategy

### Determinism Testing
- Run `extract-infographic-data.py` twice on same input → `diff` outputs → zero differences
- Test all three templates separately
- Test all three tiers (Tier 1, 2, 3) with appropriate fixtures

### Cross-Output Consistency
- Run `extract-report-data.py` and `extract-infographic-data.py` on same directory
- Compare severity counts from both outputs
- Counts must match for all severity levels at all tiers

### Refactoring Verification
- Run `extract-report-data.py` against `examples/agentic-app/sample-report/` before and after shared module extraction
- Output must be byte-identical (zero-behavior-change refactor)

### Edge Case Testing
- Empty findings: zero counts, 0% percentages
- Single severity level: 100% for that level
- 8+ components: top 7 + "Other" aggregation in heat map
- Missing Section 4a: dedup skipped, raw counts used
- Missing trust zones: flat component layout for architecture template
- Missing risk-scores.md: funnel shows null for inherent tier

### Test Fixtures
- **Tier 1 (full)**: `examples/agentic-app/sample-report/` (threats.md + risk-scores.md + compensating-controls.md)
- **Tier 2**: `examples/agentic-app/sample-report/` (threats.md + risk-scores.md, skip compensating-controls.md)
- **Tier 3**: `examples/mermaid-agentic-app/` (threats.md only)

## Implementation Phases

### Phase 1: Shared Parser Module + Refactoring Verification
1. Create `scripts/tachi_parsers.py` with extracted generic parsers
2. Update `extract-report-data.py` to import from `tachi_parsers`
3. Verify byte-identical output from `extract-report-data.py` (no behavior change)

### Phase 2: Core Extraction Script (Baseball Card)
1. Create `scripts/extract-infographic-data.py` with CLI, shared parser imports
2. Implement Largest Remainder Method
3. Implement severity extraction + percentages
4. Implement heat map cross-tabulation
5. Implement top 5 finding selection
6. Implement component risk weights
7. Implement validation
8. Implement JSON output
9. Test baseball-card template on all 3 tiers

### Phase 3: System Architecture Template
1. Add architecture overlay computation (trust zones, data flows, boundaries)
2. Handle trust zone absence fallback
3. Test system-architecture template on all 3 tiers

### Phase 4: Risk Funnel Template
1. Add risk funnel tier computation
2. Add reduction percentage calculation
3. Handle partial funnels (missing intermediate artifacts)
4. Handle Tier 3-only scenario (null tiers + missing_enrichments)
5. Test risk-funnel template on all 3 tiers

### Phase 5: Agent Update + Integration
1. Update threat-infographic agent prompt (Steps 1-2 → script invocation)
2. Add error handling for script exit codes
3. End-to-end test: `/infographic` → verify spec matches JSON data
4. Cross-output consistency test: compare with `extract-report-data.py`

## Complexity Tracking

No constitution violations to justify.

## Architect Concern Resolutions

### C-3 (High): Tier 3 Cross-Output Consistency Divergence

**Finding**: `extract-report-data.py` derives Tier 3 severity from the Section 7 findings array (raw, undeduplicated), not from Section 6 Risk Summary (deduplicated). When correlation groups exist, Section 6 and Section 7 produce different counts.

**Decision**: The infographic script MUST align with `extract-report-data.py` behavior for Tier 3 — derive severity counts from the Section 7 findings array. This ensures FR-011 (cross-output consistency) holds without modifying the delivered Feature 067 script.

**Implementation**: For Tier 3, call `parse_threats_findings()` to get the findings list, then count severity levels from the findings array (same as `extract-report-data.py` lines 1340-1350). Use `parse_threats_severity()` (Section 6) only for the risk funnel's Tier 0 "raw findings" count, which explicitly represents the deduplicated total.

**Spec FR-010 note**: FR-010 says "Tier 3 severity source MUST be Section 6 Risk Summary." This is updated: Tier 3 severity source is the Section 7 findings array (matching `extract-report-data.py`). Section 6 is used only for the risk funnel Tier 0 total count.

### C-2 (Medium): Missing Metadata Computation Descriptions

**Finding**: The plan does not describe how `agent_count`, `risk_posture`, and `scan_date` are computed.

**Resolution**:
- **`scan_date`**: Extracted from YAML frontmatter via `parse_frontmatter()` → `date` field. Falls back to "Unknown" if not found.
- **`agent_count`**: Count of distinct `## 3.X` sub-sections in threats.md (each corresponds to a STRIDE or AI agent). Extracted by regex: `r"^## 3\.\d+"` — count of matches.
- **`risk_posture`**: Generated string following the pattern: "{tier_label} — {critical_count} Critical and {high_count} High findings across {component_count} components". Tier labels: Tier 1 = "Residual risk", Tier 2 = "Inherent risk", Tier 3 = "Severity assessment". This is deterministic — no LLM generation.

## Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Shared module breaks `extract-report-data.py` | Run refactoring verification test immediately after extraction; byte-identical output required before proceeding |
| Heat map edge cases (zero findings, 8+ components) | Zero-fill all components from scope data; explicit "Other" aggregation with deterministic sort |
| Percentage sums != 100 | Largest Remainder Method guarantees sum-to-target; tested with edge cases (single severity, zero total) |
| Funnel partial data | Null tiers in JSON; agent handles display; tested with Tier 3-only fixture |
| Agent prompt too large after update | Script handles all computation; agent only reads JSON and assembles markdown — net reduction in agent complexity |
