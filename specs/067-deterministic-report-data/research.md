# Research Summary: Deterministic Report Data Extraction

## Knowledge Base Findings
- No existing KB entries found for report generation, markdown parsing, or deterministic extraction patterns.

## Codebase Analysis

### Current Architecture (Being Replaced)
- **Report-Assembler Agent**: `.claude/agents/tachi/report-assembler.md` (687 lines) — 4-step process: Artifact Detection → Data Extraction (LLM) → Typst Data Generation (LLM) → Compilation
- **Security-Report Command**: `.claude/commands/security-report.md` (240 lines) — validates prerequisites, invokes agent, reports results
- **Steps 2-3 are the problem**: LLM parses markdown tables and generates `report-data.typ` non-deterministically

### Typst Template Data Contract
- **Location**: `templates/tachi/security-report/` (15 files)
- **Data file**: `report-data.typ` — ~25 variable categories with `#let` bindings
- **Variables**: metadata (project-name, date, classification), severity counts (4 levels + total), page flags (8 booleans), image paths, content vectors (findings, coverage, controls, scope, remediation), scope data (4 table types with counts)
- **Tier-specific findings keys**:
  - Tier 1: id, component, threat, residual_score, residual_severity, control_status, recommendation
  - Tier 2: id, component, threat, composite_score, severity, cvss, exploitability
  - Tier 3: id, component, threat, likelihood, impact, risk_level, mitigation

### Existing Python Scripts
- `.claude/skills/~aod-build/scripts/` contains 3 Python scripts (update_index.py, analyze_tasks.py, generate_checkpoint.py) — none related to markdown parsing
- No existing markdown-to-Typst parsing utilities in the repo

### Example Datasets
- **agentic-app**: `examples/agentic-app/sample-report/` — has threats.md (246 lines), risk-scores.md, threat-report.md. No compensating-controls.md example.
- **openclaw**: `examples/openclaw/` — needs verification for test fixtures

### Schemas (Machine-Readable Contracts)
- `schemas/output.yaml` (165 lines) — threats.md structure
- `schemas/risk-scoring.yaml` (103 lines) — risk-scores.md structure
- `schemas/compensating-controls.yaml` (177 lines) — compensating-controls.md structure
- `schemas/security-report.yaml` (179 lines) — page assembly contract

## Technical Decisions

### Decision 1: Script Location
- **Decision**: `scripts/extract-report-data.py`
- **Rationale**: Follows existing convention (`scripts/` directory at repo root). The `.claude/skills/` scripts are AOD lifecycle scripts; this is a product script.
- **Alternatives**: `.claude/scripts/` (rejected — not an AOD lifecycle tool), `templates/tachi/security-report/extract.py` (rejected — script is not a template)

### Decision 2: Python stdlib only (no PyYAML)
- **Decision**: Use regex-based frontmatter parsing, no external dependencies
- **Rationale**: Eliminates installation friction. tachi frontmatter is flat key-value pairs (date, classification, schema_version). risk-scores.md has nested `scoring_weights` but those values are not needed by the report.
- **Alternatives**: PyYAML (rejected — adds external dependency for simple parsing), ruamel.yaml (rejected — same dependency issue)

### Decision 3: Total findings count — use raw count
- **Decision**: When Total row shows "30 (34 raw)", extract raw count (34) as `total-findings`
- **Rationale**: Raw count matches the actual number of findings rows in the findings table. Deduplication count is for display; raw count is for structural integrity.
- **Alternatives**: Use dedup count (rejected — findings table has raw count rows, so validation would fail)

### Decision 4: Note severity handling
- **Decision**: Parse Note count from Risk Summary, expose as `note-count` variable, exclude from 4-level validation sum
- **Rationale**: Note is a valid severity level in tachi output but not rendered as a severity band in the PDF (no Note color in Typst templates). Including it in the sum would break the validation rule.
- **Alternatives**: Ignore Note entirely (rejected — loses data), include in sum (rejected — breaks validation against 4-level Typst rendering)

### Decision 5: Exit codes
- **Decision**: 0 = success, 1 = missing required artifact, 2 = validation failure
- **Rationale**: Standard Unix convention. Code 1 for "can't start" (missing input), code 2 for "ran but found problems" (data integrity). Agent can distinguish between "run /threat-model first" and "data is inconsistent."
- **Alternatives**: Single non-zero code (rejected — agent can't distinguish error types)

### Decision 6: Markdown table parsing approach
- **Decision**: Regex + line-by-line parsing with section header anchoring
- **Rationale**: Tables follow consistent `| col | col |` format. Section headers (`## N. Section Name`) anchor table location. No need for a markdown AST parser since all tables have known, stable column layouts.
- **Alternatives**: markdown-it or mistune (rejected — external dependency), full AST parsing (rejected — overkill for known table formats)

## Parsing Edge Cases

| Edge Case | Handling Strategy |
|-----------|-------------------|
| Bold markers `**text**` in cells | Strip `**` before parsing value |
| Total row "N (M raw)" format | Regex: extract parenthesized raw count, fallback to first number |
| Unicode (em dashes, smart quotes) | Pass through; Typst handles Unicode natively |
| Truncation `...` in threat text | Preserve as-is (content decision, not parsing decision) |
| Empty table (headers, no rows) | Return empty array `()` |
| Malformed row (wrong column count) | Log warning to stderr, skip row |
| Schema v1.0 (no Section 4a) | Check schema_version, skip Section 4a parsing |
| Nested YAML in frontmatter | Parse only top-level keys needed; skip nested blocks |
| Zero-byte image files | Set has-*-image = false, log warning |

## Recommendations for Plan
- Single-file Python script (~500-700 lines estimated)
- Structure as: argument parsing → artifact detection → per-artifact parsers → validation → Typst generation
- Each parser function is independent and testable
- Agent prompt update is a separate deliverable (modify report-assembler.md Steps 2-3)
- Test with both example datasets; create Tier 1 fixture for compensating-controls testing
