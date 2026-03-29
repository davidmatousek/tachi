# templates/

Output templates defining the structure of threat model deliverables. Each template specifies the format, required sections, and rendering rules for a specific output type.

## Template Types

### Reference Templates (Markdown)

Output structure examples used as documentation for agent output schemas.

| Template | Output | Purpose |
|----------|--------|---------|
| `threats-md/` | `threats.md` | Human-readable threat report in markdown |
| `sarif/` | `.sarif` | SARIF 2.1.0 format for IDE and CI/CD integration |
| `summary/` | Executive summary | High-level risk overview for non-technical stakeholders |

### Rendering Templates (Typst)

Compiled by the Typst CLI to produce PDF output. Used by the report-assembler agent.

| Template | Output | Purpose |
|----------|--------|---------|
| `security-report/` | `security-report.pdf` | Professional PDF booklet assembled from pipeline artifacts via Typst |

## How Templates Work

**Reference templates** separate structure from content. Agents produce raw threat findings; templates control how those findings are assembled into deliverables. The same set of findings can produce multiple output formats by applying different templates.

**Rendering templates** are compiled by external tools (Typst) into final output files. The report-assembler agent generates a data file that the Typst templates consume during compilation.
