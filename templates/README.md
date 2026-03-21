# templates/

Output templates defining the structure of threat model deliverables. Each template specifies the format, required sections, and rendering rules for a specific output type.

## Template Types

| Template | Output | Purpose |
|----------|--------|---------|
| `threats-md/` | `threats.md` | Human-readable threat report in markdown |
| `sarif/` | `.sarif` | SARIF 2.1.0 format for IDE and CI/CD integration |
| `summary/` | Executive summary | High-level risk overview for non-technical stakeholders |

## How Templates Work

Templates separate structure from content. Agents produce raw threat findings; templates control how those findings are assembled into deliverables. The same set of findings can produce multiple output formats by applying different templates.
