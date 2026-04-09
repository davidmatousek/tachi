# Research Summary: Attack Path Pages in Security Report PDF

## Knowledge Base Findings

No KB index available (no `make kb-search` target). No prior patterns or bug fixes documented for attack tree rendering or Mermaid-to-image conversion.

## Codebase Analysis

### Existing PDF Pipeline Patterns

The PDF report pipeline follows a 5-stage deterministic architecture:
1. **Artifact Detection** — `.md` and `.jpg` files in target directory
2. **Deterministic Parsing** — `scripts/extract-report-data.py` (Python, regex/line parsing)
3. **Data Contract Generation** — `report-data.typ` (Typst variable file)
4. **Typst Compilation** — `.typ` templates compile to PDF
5. **Output** — Single `security-report.pdf`

### Conditional Page Pattern (established)

All optional pages use boolean flags in `report-data.typ`:
```typst
#if has-maestro-data {
  page(...)[#maestro-findings-page(...)]
}
```

Existing flags: `has-threat-report`, `has-risk-scores`, `has-compensating-controls`, `has-funnel-image`, `has-baseball-image`, `has-architecture-image`, `has-maestro-data`, `has-maestro-stack-image`, `has-maestro-heatmap-image`.

### Attack Tree File Format (existing)

Location: `examples/agentic-app/sample-report/attack-trees/`
Files: `{finding-id}-attack-tree.md` (e.g., `t-1-attack-tree.md`)

Structure:
- Metadata table: Finding ID, Component, Risk Level, Threat, Correlation
- Mermaid flowchart code block with established color scheme:
  - `goal` (red), `andGate` (orange), `orGate` (teal), `subGoal` (gray), `leaf` (green)
  - Node IDs: `{FindingID}_{type}{N}` pattern

### Key Files to Extend

| File | Purpose | Extension Needed |
|------|---------|-----------------|
| `scripts/extract-report-data.py` | Data extraction | Attack tree parsing + mmdc invocation |
| `templates/tachi/security-report/main.typ` | Page orchestration | Insert attack path pages in sequence |
| `templates/tachi/security-report/shared.typ` | Design tokens | Severity colors already exist (reuse) |
| `.claude/agents/tachi/report-assembler.md` | Artifact detection | Add attack-trees/ to detection |
| `.claude/commands/security-report.md` | Command definition | Add attack-trees/ to artifact table |

### Patterns to Reuse

- `severity-color()` function from `shared.typ` — color-coded severity badges
- `section-divider()` function — section header pages
- `report-header()` / `report-footer()` — consistent page framing
- Array iteration pattern from `maestro-findings.typ` — looping through data arrays
- Shared parser module `scripts/tachi_parsers.py` — markdown table parsing

### Current Page Sequence in main.typ

1. Cover → 2. Disclaimer → 3. TOC → 4. Risk Methodology → 5. Scope → 6. Executive Summary → 7. Infographic pages → 8. MAESTRO Findings → 9. Findings Detail → 10. Control Coverage → 11. Remediation Roadmap

Attack path pages insert after Executive Summary (position 6), before infographic pages.

## Architecture Constraints

- **Determinism**: All extraction is programmatic — no LLM fallback
- **Page orientation**: US Letter portrait (8.5" x 11") for text pages
- **Typst image support**: PNG, JPEG, SVG, GIF, WebP, PDF formats
- **Compilation time**: <30s for typical report
- **Schema compatibility**: Must handle reports with and without attack trees gracefully
- **Mermaid rendering**: Typst cannot render Mermaid natively — requires pre-rendering to PNG

## Industry Research

### Mermaid CLI (mmdc)
- Standard tool: `@mermaid-js/mermaid-cli` (npm package)
- Python subprocess pattern: `subprocess.run(['mmdc', '-i', input, '-o', output, '-s', '2'], capture_output=True, check=True)`
- Scale flag `-s 2` for 2x resolution (recommended for print)
- Pre-check availability: `subprocess.run(['mmdc', '--version'], capture_output=True)`
- Pure Python alternative: `pymmdc` package (no Node.js dependency)

### Typst Image Embedding
- `#image(path)` function for PNG/JPEG embedding
- Supports `width` and `height` parameters for scaling
- Path resolution relative to `--root` flag in compilation

## Recommendations for Spec

- Follow the established `has-X` boolean flag pattern for conditional inclusion
- Reuse `severity-color()` and `section-divider()` from shared.typ
- Place mmdc invocation inside `extract-report-data.py` (per Architect guidance)
- Use PNG at 2x resolution for diagram rendering (per PRD architect sign-off)
- Implement graceful fallback to raw Mermaid code as preformatted text when mmdc unavailable
- Order pages by severity (Critical first) then finding ID (matches threat-report agent ordering)
- Use one page per finding with proportional diagram scaling
- Add `attack-trees/` to artifact detection in security-report command
