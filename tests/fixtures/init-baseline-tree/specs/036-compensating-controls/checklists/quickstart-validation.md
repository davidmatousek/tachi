# Quickstart Validation — T021

**Validated by**: tester agent
**Date**: 2026-03-28
**Source**: `specs/036-compensating-controls/quickstart.md`
**Reference**: `.claude/commands/compensating-controls.md`, `.claude/agents/tachi/control-analyzer.md`

---

## Usage Examples

| # | Example | Flags Parsed Correctly | Behavior Matches Command | Result |
|---|---------|----------------------|--------------------------|--------|
| 1 | `/compensating-controls` (no args) | `target_path=.`, `output_dir=null`, `input_dir=.` — all defaults | Quickstart: "risk-scores in cwd, codebase in cwd" matches defaults | PASS |
| 2 | `/compensating-controls --target ./my-app` | `target_path=./my-app`, `output_dir=null`, `input_dir=.` | Quickstart: "Specify target codebase" — correct, risk-scores still read from cwd | PASS |
| 3 | `/compensating-controls --target ./my-app --output-dir ./reports/` | `target_path=./my-app`, `output_dir=./reports/`, `input_dir=.` | Quickstart: "Specify output directory" — both flags parsed, input from cwd | PASS |
| 4 | `/compensating-controls --target examples/agentic-app/ examples/agentic-app/sample-report/` | `target_path=examples/agentic-app/`, remaining arg `examples/agentic-app/sample-report/` becomes input dir | Quickstart: "Analyze the example app" — input dir is the sample-report path, target is the app dir | PASS |

**All 4 usage examples match the command's Step 0 flag parsing and Step 1 validation logic.**

---

## Pipeline Diagram

```
/threat-model → threats.md + threats.sarif
     ↓
/risk-score → risk-scores.md + risk-scores.sarif
     ↓
/compensating-controls → compensating-controls.md + compensating-controls.sarif
```

| Check | Evidence | Result |
|-------|----------|--------|
| `/threat-model` output files | `threat-model.md` lines 49-50: `threats.md` and `threats.sarif` | PASS |
| `/risk-score` output files | `risk-score.md` description: "produces risk-scores.md and risk-scores.sarif" | PASS |
| `/compensating-controls` output files | `compensating-controls.md` line 36: both files listed in Output suite | PASS |
| Pipeline ordering (threat-model -> risk-score -> compensating-controls) | Command overview: "third link in the pipeline: /threat-model -> /risk-score -> /compensating-controls" | PASS |
| SARIF supersession claim ("supersedes both prior SARIF files") | Command Step 3 says "supersedes risk-scores.sarif"; agent preserves fingerprints for alert continuity. Factually accurate that the most downstream SARIF supersedes all upstream SARIF files | PASS |

---

## Output Files Table

| Quickstart Claim | Verification | Result |
|-----------------|--------------|--------|
| `compensating-controls.md` — Markdown format | Command Output suite and agent Phase 6b confirm markdown output | PASS |
| `compensating-controls.sarif` — SARIF 2.1.0 format | Command Output suite and agent Phase 6c confirm SARIF 2.1.0 output | PASS |
| MD audience: "Security engineers, managers, developers" | Agent Phase 6b sections include executive summary, coverage matrix, control details, recommendations — serves all three audiences | PASS |
| SARIF audience: "GitHub Code Scanning, CI/CD pipelines" | Agent Phase 6c produces valid SARIF 2.1.0 with fingerprint preservation for GitHub alert tracking | PASS |

---

## "What It Does" Section

| Step | Quickstart Claim | Verification | Result |
|------|-----------------|--------------|--------|
| 1 | "Reads scored threats from /risk-score output" | Command Step 1.2-1.3: reads `risk-scores.md` (canonical) or `risk-scores.sarif` (fallback) | PASS |
| 2 | "Scans the target codebase for 8 categories of security controls" | Agent Phase 3: 8 categories — authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control | PASS |
| 3 | "Classifies each threat: Control Found / Partial Control / No Control Found" | Agent Phase 4: exactly these three classifications with exhaustive classification requirement | PASS |
| 4 | "Recommends controls for unmitigated threats, prioritized by risk score" | Agent Phase 5a: recommendations for partial/missing threats, sorted by `composite_score` descending | PASS |
| 5 | "Calculates residual risk after accounting for existing controls" | Agent Phase 5: `residual_score = composite_score * (1 - reduction_factor)` | PASS |
| 6 | "Outputs compensating-controls.md + compensating-controls.sarif" | Command Step 3 and agent Phase 6 confirm both output files | PASS |

---

## Tips

| # | Tip | Verification | Result |
|---|-----|--------------|--------|
| 1 | "Provide architecture.md alongside risk scores for better component-to-code mapping" | Command Step 1.6: looks for `architecture.md` in input dir and parent dir. Agent Input Boundary: "enables architecture-aware component-to-file mapping instead of heuristic-only discovery" | PASS |
| 2 | "Use --target when the codebase and risk scores are in different directories" | Command Step 0: `--target` sets `target_path` independently from input dir (remaining positional arg). Correct use case description | PASS |
| 3 | "Review the Coverage Matrix section first for a quick posture overview" | Agent Phase 6b Section 2: Coverage Matrix contains per-threat status table grouped by severity with summary statistics — suitable as a posture overview | PASS |
| 4 | "Critical/High unmitigated threats appear at the top of the Recommendations section" | Agent Phase 5a: sorted by `composite_score` descending. Agent Phase 6b Section 4: "grouped by inherent severity band (Critical/High first, then Medium, then Low)" | PASS |

---

## Prerequisites

| Quickstart Prerequisite | Command Validation Step | Result |
|------------------------|------------------------|--------|
| "tachi installed with control analyzer agent" | Step 1.1: checks `.claude/agents/tachi/control-analyzer.md` exists, halts if missing | PASS |
| "Scored threats from /risk-score (either risk-scores.md or risk-scores.sarif)" | Step 1.2: looks for `risk-scores.md` then `risk-scores.sarif` in input dir, halts if neither exists | PASS |
| "Target codebase accessible at a known path" | Step 1.4: validates `target_path` is existing directory with at least one file, halts if invalid | PASS |

---

## Summary

| Category | Checks | Passed | Failed |
|----------|--------|--------|--------|
| Usage examples | 4 | 4 | 0 |
| Pipeline diagram | 5 | 5 | 0 |
| Output files table | 4 | 4 | 0 |
| "What It Does" steps | 6 | 6 | 0 |
| Tips | 4 | 4 | 0 |
| Prerequisites | 3 | 3 | 0 |
| **Total** | **26** | **26** | **0** |

**Overall Result: PASS** -- All quickstart content is consistent with the command's flag parsing, validation logic, and the agent's behavior.

---

## Discrepancies Found

None. The quickstart guide accurately reflects the command and agent behavior across all checked dimensions.
