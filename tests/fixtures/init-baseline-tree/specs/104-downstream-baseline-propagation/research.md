# Research Summary: Downstream Baseline Propagation

## Knowledge Base Findings
- KB search unavailable (no Makefile target configured)
- No prior patterns documented for delta propagation to downstream consumers

## Codebase Analysis

### Target Files (10 components)

**Agent Instruction Files (3):**
- `agents/threat-report.md`
- `agents/threat-infographic.md`
- `.claude/agents/tachi/report-assembler.md`

**Extraction Scripts (2):**
- `scripts/extract-infographic-data.py`
- `scripts/extract-report-data.py`

**Command Files (2):**
- `.claude/commands/infographic.md`
- `.claude/commands/security-report.md`

**Output Schema Templates (2):**
- `templates/tachi/output-schemas/threats.md`
- `templates/tachi/output-schemas/threat-report.md`

**Shared Parser (1 - critical dependency):**
- `scripts/tachi_parsers.py` — `parse_threats_findings()` hardcodes field set excluding `delta_status` and `baseline_run_id`

### Upstream Delta Patterns (Feature 074 precedent)

**Risk-Scorer branching pattern:**
- UNCHANGED: Inherit all scores verbatim (`score_source: "inherited"`)
- UPDATED: Re-score fresh using full 4-dimensional model
- NEW: Score with bounded CVSS
- RESOLVED: Retain last-known scores from baseline

**Control-Analyzer branching pattern:**
- UNCHANGED: Carry forward control status (`control_carry_forward: true`)
- UPDATED: Re-scan with incremental scope
- NEW: Full scan
- RESOLVED: Skip entirely

**Backward compatibility guard pattern:**
```python
if "delta_status" in fields:
    # delta-aware logic
else:
    # stateless logic (current behavior)
```

### Shared Parser Gap

`parse_threats_findings()` (tachi_parsers.py) constructs a hardcoded dict: `id`, `component`, `threat`, `likelihood`, `impact`, `risk_level`, `mitigation`. Both extraction scripts call this function — fixing it here cascades to both downstream consumers.

## Architecture Constraints

### From ADR-018 (Baseline-Aware Pipeline)
- "All changes must be additive to existing schemas, templates, and SARIF output" — no breaking changes
- Baseline detection: Check frontmatter `baseline.source` for null (preferred over per-finding checks)
- Graceful degradation: Unparseable baselines fall back to stateless mode with warning

### Finding Schema v1.2 (`schemas/finding.yaml`)
- `delta_status`: enum [NEW, UNCHANGED, UPDATED, RESOLVED], defaults to NEW when no baseline
- `baseline_run_id`: string (nullable), format "YYYY-MM-DDTHH-MM-SS"
- Both fields `required_when: baseline_present`

### Shared Definitions Governance (ADR-019)
- All downstream consumers must reference `tachi-shared` definitions (severity-bands, stride-categories, finding-format)
- No embedded copies — prevents drift as baseline behavior evolves

### Backward Compatibility Rules
- Guard all delta logic behind presence checks
- Stateless mode (no baseline) must behave identically to pre-Feature-074
- Detection: `baseline.source` in frontmatter (not per-finding scanning)

## Industry Research

- Continuous benchmarking (real-time visibility into risk posture) preferred over static annual snapshots
- Temporal anomaly baselining: compare behavioral baselines across time slices (month-to-month, post-patch vs. pre-patch)
- Attack-path modeling maturing from static views to dynamic, decision-driving models
- Delta-based assessment aligns with industry trend toward continuous threat monitoring

## Recommendations for Spec

- Shared parser (`tachi_parsers.py`) must be updated first as both extraction scripts depend on it
- Follow the exact branching pattern established in Feature 074 (risk-scorer, control-analyzer) for consistency
- All delta logic guarded behind presence checks for backward compatibility
- RESOLVED findings separated (not deleted) for audit trail
- Section 8 (Delta Summary) structure needed in both output schema templates
- Validate with second-brain-mcp baseline comparison test case (April 8 vs March 31 runs)
- Include no-baseline regression test for backward compatibility validation
