---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-30
    status: APPROVED
    notes: "All 27 spec FRs covered. All 6 user stories addressed across 3 phases. No scope creep. Testing strategy covers determinism, all 3 tiers, validation, and E2E."
  architect_signoff:
    agent: architect
    date: 2026-03-30
    status: APPROVED_WITH_CONCERNS
    notes: "Architecturally sound. 2 minor concerns: (1) Tier 1 test fixture location underspecified — recommend examples/agentic-app/sample-report/compensating-controls.md. (2) report-config.typ copy behavior should remain in agent orchestration, not script. All 5 PRD concerns addressed. Typst variable contract verified."
  techlead_signoff: null
---

# Implementation Plan: Deterministic Report Data Extraction

**Branch**: `067-deterministic-report-data` | **Date**: 2026-03-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/067-deterministic-report-data/spec.md`

## Summary

Replace the LLM-based data extraction in the report-assembler agent (Steps 2-3) with a deterministic Python script that reads tachi pipeline markdown artifacts using regex and line parsing, validates internal consistency, and writes `report-data.typ`. The agent is reduced to orchestration: detect artifacts, invoke the script, compile with Typst.

## Technical Context

**Language/Version**: Python 3.9+ (standard library only: `re`, `pathlib`, `argparse`, `sys`, `os`)
**Primary Dependencies**: None (zero external dependencies)
**Storage**: File-based (markdown artifacts in → `report-data.typ` out)
**Testing**: Direct script execution against example datasets + `diff` for determinism verification
**Target Platform**: macOS, Linux, Windows (Python 3.9+ cross-platform)
**Project Type**: Single script + agent prompt update
**Performance Goals**: < 5 seconds for largest expected artifact set (64+ findings, 36 data flows)
**Constraints**: Byte-identical output from identical input (determinism); Python stdlib only
**Scale/Scope**: ~500-700 line Python script, ~100 line agent prompt delta

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Script is domain-specific to tachi report pipeline but does not modify core platform |
| III. Backward Compatibility | PASS | No changes to Typst templates or variable contract; script produces identical data structure |
| VI. Testing Excellence | PASS | Testing against two example datasets with all three tiers; determinism verified by diff |
| VII. Definition of Done | PASS | Measurable success criteria: byte-identical output, validation checks, performance target |
| IX. Git Workflow | PASS | Feature branch `067-deterministic-report-data`; PR required |
| X. Product-Spec Alignment | PASS | Spec approved by PM; plan requires PM + Architect sign-off |

No violations. All constitutional gates pass.

## Project Structure

### Documentation (this feature)

```
specs/067-deterministic-report-data/
├── plan.md              # This file
├── research.md          # Research phase output
├── data-model.md        # Typst variable contract and entity definitions
├── quickstart.md        # Developer quickstart guide
└── tasks.md             # Task breakdown (pending)
```

### Source Code (repository root)

```
scripts/
└── extract-report-data.py    # NEW: Deterministic parsing script

.claude/agents/tachi/
└── report-assembler.md        # MODIFIED: Steps 2-3 replaced with script invocation

examples/
├── agentic-app/sample-report/ # EXISTING: Tier 2 test fixture
│   ├── threats.md
│   ├── risk-scores.md
│   └── threat-report.md
└── openclaw/                  # VERIFY: May need Tier 1/3 test fixtures
```

**Structure Decision**: Single Python script at `scripts/extract-report-data.py`. No package, no `src/` directory — this is a standalone CLI tool invoked by the agent via `python3 scripts/extract-report-data.py`.

## Components

### Component 1: Parsing Script (`scripts/extract-report-data.py`)

**Purpose**: Deterministic extraction of structured data from markdown artifacts into Typst variable bindings.

**Architecture**: Sequential pipeline with independent parser functions:

```
CLI args → Artifact detection → Tier selection
  → Parse threats.md (frontmatter, project name, severity counts, scope, findings)
  → Parse risk-scores.md (severity distribution, scored findings) [if Tier 2+]
  → Parse compensating-controls.md (residual findings, coverage, controls) [if Tier 1]
  → Parse threat-report.md (executive narrative, remediation) [if available]
  → Detect brand assets
  → Validate internal consistency
  → Generate report-data.typ
```

**Key design decisions**:
- Each artifact parser is an independent function returning a data dict
- Parser functions take file content as string input (testable without filesystem)
- Validation runs after all parsing, before output generation
- Output generation is a single function that formats all data as Typst syntax
- String escaping is centralized in one utility function

### Component 2: Agent Prompt Update (`.claude/agents/tachi/report-assembler.md`)

**Purpose**: Replace Steps 2-3 (LLM-based extraction and generation) with script invocation.

**Changes**:
- **Step 2** (Data Extraction): Replaced entirely. New Step 2 invokes:
  ```bash
  python3 scripts/extract-report-data.py \
    --target-dir {target_dir} \
    --output templates/tachi/security-report/report-data.typ \
    --template-dir templates/tachi/security-report/ \
    [--title "{title_override}"]
  ```
- **Step 3** (Typst Data Generation): Removed — script handles this
- **Step 4** (Compilation): Unchanged — agent still invokes `typst compile`
- **Error handling**: Agent checks script exit code (0=proceed, 1=abort with message, 2=abort with validation details)

## Data Flow

```
Input Artifacts (target directory)           Parsing Script              Output
┌────────────────────────────┐     ┌──────────────────────────┐     ┌──────────────┐
│ threats.md        [required]│────▶│ parse_threats_md()       │────▶│              │
│ risk-scores.md   [optional]│────▶│ parse_risk_scores_md()   │────▶│ report-      │
│ compensating-    [optional]│────▶│ parse_comp_controls_md() │────▶│ data.typ     │
│   controls.md              │     │ parse_threat_report_md() │     │              │
│ threat-report.md [optional]│────▶│ detect_brand_assets()    │────▶│ (Typst #let  │
│ *.jpg images     [optional]│────▶│ validate()               │     │  bindings)   │
│ brand/final/*.png[optional]│────▶│ generate_typst()         │────▶│              │
└────────────────────────────┘     └──────────────────────────┘     └──────────────┘
                                            │                              │
                                            │ exit 0/1/2                   │
                                            ▼                              ▼
                                   Agent (report-assembler)        typst compile
                                   checks exit code                → security-report.pdf
```

## Tech Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Script | Python 3.9+ stdlib | Zero-dependency, cross-platform, regex support |
| Parsing | `re` module | Sufficient for markdown tables with known column layouts |
| CLI | `argparse` | Standard Python CLI argument parsing |
| File I/O | `pathlib` | Cross-platform path handling |
| Output | String formatting | Deterministic Typst syntax generation |
| Templates | Typst (unchanged) | Existing template system, no modifications |

## Script Internal Design

### Module Structure (single file)

```python
# 1. Constants and configuration
SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Note"]
STRIDE_PREFIXES = {"S-": "Spoofing", "T-": "Tampering", ...}

# 2. Utility functions
def escape_typst_string(s: str) -> str: ...
def strip_bold(s: str) -> str: ...
def parse_markdown_table(lines: list, expected_cols: int) -> list[dict]: ...

# 3. Frontmatter parser
def parse_frontmatter(content: str) -> dict: ...

# 4. Artifact parsers (one per artifact type)
def parse_threats_md(content: str, title_override: str | None) -> dict: ...
def parse_risk_scores_md(content: str) -> dict: ...
def parse_compensating_controls_md(content: str) -> dict: ...
def parse_threat_report_md(content: str) -> dict: ...

# 5. Brand asset detection
def detect_brand_assets(target_dir: Path, template_dir: Path) -> dict: ...

# 6. Image path detection
def detect_images(target_dir: Path, template_dir: Path) -> dict: ...

# 7. Tier selection
def determine_tier(target_dir: Path) -> int: ...

# 8. Validation
def validate(data: dict) -> list[str]: ...  # returns list of error messages

# 9. Typst generation
def generate_report_data_typ(data: dict) -> str: ...

# 10. CLI entry point
def main(): ...
```

### Markdown Table Parsing Strategy

Tables are identified by:
1. Finding a section header anchor (e.g., `## 6. Risk Summary`)
2. Scanning forward for the first `|`-delimited row (header row)
3. Skipping the separator row (`|---|---|`)
4. Reading subsequent `|`-delimited rows until a non-table line

Each row is split by `|`, stripped, and bold markers removed. Column values are mapped to named keys based on the expected column layout for that table.

### Severity Count Extraction by Tier

- **Tier 1**: Iterate findings from compensating-controls.md Section 2; count by `residual_severity` field
- **Tier 2**: Parse risk-scores.md Section 1 severity distribution table directly (Critical/High/Medium/Low/Total rows)
- **Tier 3**: Parse threats.md Section 6 Risk Summary table directly

For Tiers 2 and 3, the Total row may contain "N (M raw)" format. Regex: `r'\*{0,2}(\d+)(?:\s*\((\d+)\s*raw\))?\*{0,2}'` — use group 2 (raw) if present, else group 1.

### String Escaping

Centralized in `escape_typst_string()`:
```
" → \"
\ → \\
newline → \n
```

Applied to all string values before Typst output generation. Numeric values and keywords (`true`, `false`, `none`) are not escaped.

## Testing Strategy

### Determinism Verification
1. Run script on agentic-app example dataset → `report-data-1.typ`
2. Run script again on same dataset → `report-data-2.typ`
3. `diff report-data-1.typ report-data-2.typ` → zero differences

### Tier Coverage
| Tier | Test Dataset | Configuration |
|------|-------------|---------------|
| Tier 1 | Test fixture (to be created) | threats.md + risk-scores.md + compensating-controls.md |
| Tier 2 | agentic-app/sample-report/ | threats.md + risk-scores.md + threat-report.md |
| Tier 3 | Subset of agentic-app | threats.md only (rename/remove risk-scores.md temporarily) |

### Validation Testing
- Inject incorrect severity counts → verify exit code 2 with correct error message
- Inject duplicate finding IDs → verify exit code 2
- Remove threats.md → verify exit code 1

### End-to-End
- Run full `/security-report` on agentic-app dataset with updated agent
- Verify PDF is generated and severity counts match source data
- Run twice and verify byte-identical PDF output

## Error Handling

| Scenario | Exit Code | Behavior |
|----------|-----------|----------|
| threats.md missing | 1 | stderr: "Error: threats.md not found in {target_dir}" |
| threats.md unparseable | 1 | stderr: "Error: could not parse threats.md: {details}" |
| Optional artifact missing | 0 | Log warning to stderr, set flag false, continue |
| Optional artifact malformed | 0 | Log warning to stderr, set flag false, continue |
| Malformed table row | 0 | Log warning to stderr, skip row, continue |
| Image file 0 bytes | 0 | Log warning to stderr, set flag false, continue |
| Severity sum mismatch | 2 | stderr: "Validation error: severity sum {sum} != total {total}" |
| Duplicate finding IDs | 2 | stderr: "Validation error: duplicate finding ID: {id}" |
| Scope count mismatch | 2 | stderr: "Validation error: scope count mismatch: {details}" |

## Implementation Phases

### Phase 1: Core Parsing Script (P1 stories)
- Implement CLI argument parsing
- Implement artifact detection and tier selection
- Implement threats.md parser (frontmatter, project name, severity, scope, findings)
- Implement risk-scores.md parser (severity distribution, scored findings)
- Implement Typst output generation
- Test against agentic-app dataset (Tier 2)
- Verify determinism with diff

### Phase 2: Full Tier Support + Validation (P1 stories continued)
- Implement compensating-controls.md parser (Tier 1 findings, coverage, controls)
- Implement threat-report.md parser (executive narrative, remediation)
- Implement brand asset and image detection
- Implement validation rules
- Create Tier 1 test fixture
- Test all three tiers

### Phase 3: Agent Integration + End-to-End (P1-P2 stories)
- Update report-assembler.md (replace Steps 2-3 with script invocation)
- End-to-end test: `/security-report` → PDF
- Verify byte-identical PDF output
- Test error handling (missing artifacts, validation failures)

## Complexity Tracking

No constitution violations. No complexity justifications needed.

## Post-Design Constitution Re-Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Script is tachi-specific (report pipeline tool) |
| III. Backward Compatibility | PASS | Same Typst variable contract; templates unchanged |
| VI. Testing Excellence | PASS | 3 tiers tested, determinism verified, validation tested |
| VII. Definition of Done | PASS | SC-001 through SC-007 are measurable and verifiable |
| IX. Git Workflow | PASS | Feature branch; PR for review |
| X. Product-Spec Alignment | PASS | Plan covers all 27 FRs from spec |

All gates pass post-design.
