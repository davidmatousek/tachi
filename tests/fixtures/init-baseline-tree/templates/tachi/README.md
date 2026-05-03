# templates/tachi/

All tachi template files in one place. Copy this folder into your project:

```bash
cp -r ~/Projects/tachi/templates/tachi/ your-project/templates/tachi/
```

## Structure

```
templates/tachi/
├── output-schemas/        # Reference schemas for agent output formats
│   ├── threats.md         # Human-readable threat report structure
│   ├── threats.sarif      # SARIF 2.1.0 for IDE/CI-CD integration
│   ├── threat-report.md   # Narrative report structure
│   ├── risk-scores.md     # Risk scoring output structure
│   ├── risk-scores.sarif  # Risk scoring SARIF format
│   ├── compensating-controls.md    # Control analysis structure
│   └── compensating-controls.sarif # Control analysis SARIF format
│
├── infographics/          # Infographic design specs (single source of truth)
│   ├── infographic-baseball-card.md         # Risk summary dashboard
│   ├── infographic-system-architecture.md   # Annotated architecture diagram
│   ├── infographic-risk-funnel.md           # Risk reduction funnel
│   └── INFOGRAPHIC_TEMPLATES.md             # Custom template guide
│
└── security-report/       # Typst rendering templates for PDF generation
    ├── main.typ           # Master orchestrator
    ├── theme.typ          # Brand colors, fonts, logo paths
    ├── shared.typ         # Layout utilities
    ├── report-config.typ  # Page visibility toggles, metadata
    └── *.typ              # Individual page templates
```

## Template Types

**Output schemas** define the structure of agent-generated deliverables. Agents produce raw findings; these templates control how findings are assembled into output files.

**Infographic templates** define visual layout, color palettes, typography, and Gemini API prompt structures for image generation. One template = one infographic style.

**Security report templates** are Typst source files compiled by `typst compile` into a professional PDF security assessment booklet. The report-assembler agent generates a data file that these templates consume at compile time.
