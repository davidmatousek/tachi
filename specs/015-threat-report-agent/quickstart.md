# Quickstart: Threat Report Agent & Attack Trees

**Feature**: 015 | **Date**: 2026-03-23

## What Gets Built

| File | Purpose |
|------|---------|
| `agents/threat-report.md` | Report agent prompt — analysis methodology and output rules |
| `schemas/report.yaml` | Output validation schema for threat-report.md |
| `templates/threat-report.md` | Canonical template for report output structure |
| `agents/orchestrator.md` | Modified — Phase 5 (Report) dispatch added |

## How It Works

1. User runs the tachi threat modeling pipeline (Phases 1–4 produce `threats.md`)
2. Orchestrator dispatches Phase 5 (Report) with `threats.md` as input
3. Report agent (running in fresh LLM context) generates:
   - `threat-report.md` — Narrative report with 7 sections
   - `attack-trees/{finding-id}-attack-tree.md` — Standalone Mermaid attack trees
4. All outputs land in the same `YYYY-MM-DD-{phase}/` directory

## Validation

Test against sample data:
```
examples/mermaid-agentic-app/threats.md    → Input (19 findings: 3 Critical, 9 High, 7 Medium)
examples/mermaid-agentic-app/threat-report.md → Expected output
examples/mermaid-agentic-app/attack-trees/    → Expected attack trees (12 trees: 3 Critical + 9 High)
```

## Integration Points

- **Input**: `threats.md` following `schemas/output.yaml` (v1.1)
- **Output**: `threat-report.md` following `schemas/report.yaml` (v1.0)
- **Orchestrator**: Phase 5 dispatch in `agents/orchestrator.md`
- **Opt-out**: Phase 5 can be skipped via orchestrator configuration

## Key Conventions

- Mermaid node IDs: `{FindingID}_{type}{N}` (e.g., `AG1_root`)
- Always quote Mermaid labels: `["Label text"]`
- Attack trees only for Critical/High findings
- Executive summary ≤500 words, no jargon
- Correlation groups from Section 4a treated as logical units
