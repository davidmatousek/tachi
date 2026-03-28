# Quickstart: /compensating-controls

## Prerequisites

1. tachi installed with control analyzer agent
2. Scored threats from `/risk-score` (either `risk-scores.md` or `risk-scores.sarif`)
3. Target codebase accessible at a known path

## Basic Usage

```bash
# Analyze current directory (risk-scores in cwd, codebase in cwd)
/compensating-controls

# Specify target codebase
/compensating-controls --target ./my-app

# Specify output directory
/compensating-controls --target ./my-app --output-dir ./reports/

# Analyze the example app
/compensating-controls --target examples/agentic-app/ examples/agentic-app/sample-report/
```

## What It Does

1. **Reads** scored threats from `/risk-score` output
2. **Scans** the target codebase for 8 categories of security controls
3. **Classifies** each threat: Control Found / Partial Control / No Control Found
4. **Recommends** controls for unmitigated threats, prioritized by risk score
5. **Calculates** residual risk after accounting for existing controls
6. **Outputs** `compensating-controls.md` (report) + `compensating-controls.sarif` (for GitHub)

## Output Files

| File | Format | Audience |
|------|--------|----------|
| `compensating-controls.md` | Markdown | Security engineers, managers, developers |
| `compensating-controls.sarif` | SARIF 2.1.0 | GitHub Code Scanning, CI/CD pipelines |

## Pipeline Context

```
/threat-model → threats.md + threats.sarif
     ↓
/risk-score → risk-scores.md + risk-scores.sarif
     ↓
/compensating-controls → compensating-controls.md + compensating-controls.sarif
```

Upload `compensating-controls.sarif` to GitHub Code Scanning — it supersedes both prior SARIF files.

## Tips

- Provide `architecture.md` alongside risk scores for better component-to-code mapping
- Use `--target` when the codebase and risk scores are in different directories
- Review the Coverage Matrix section first for a quick posture overview
- Critical/High unmitigated threats appear at the top of the Recommendations section
