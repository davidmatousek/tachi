---
source_agent: report-assembler
extracted_from: .claude/agents/tachi/report-assembler.md
version: 1.0.0
---

# Typst Artifacts — Detection and Tier Selection

Domain reference for the tachi report-assembler agent. Covers artifact file detection patterns, variable flag bindings, data source tier preference rules, and detection reporting.

---

## Artifact Detection Table

For each artifact reported as detected by the command, verify the file exists and is non-empty in the target directory.

| Artifact | File Pattern | Variable | Notes |
|----------|-------------|----------|-------|
| Threat Model | `threats.md` | `has_threats` | Always true -- command requires this as prerequisite |
| Narrative Report | `threat-report.md` | `has_threat_report` | Optional -- enables executive narrative and remediation timeline |
| Risk Scores | `risk-scores.md` | `has_risk_scores` | Optional -- enables Tier 2 quantitative findings display |
| Compensating Controls | `compensating-controls.md` | `has_compensating_controls` | Optional -- enables Tier 1 with residual risk and control status |
| Risk Funnel Image | `threat-risk-funnel.jpg` | `has_funnel_image` | Optional -- full-bleed infographic page |
| Baseball Card Image | `threat-baseball-card.jpg` | `has_baseball_image` | Optional -- full-bleed infographic page |
| System Architecture Image | `threat-system-architecture.jpg` | `has_architecture_image` | Optional -- full-bleed infographic page |
| MAESTRO Stack Image | `threat-maestro-stack.jpg` | `has_maestro_stack_image` | Optional -- full-bleed infographic page |
| MAESTRO Heatmap Image | `threat-maestro-heatmap.jpg` | `has_maestro_heatmap_image` | Optional -- full-bleed infographic page |
| Attack Trees | `attack-trees/*.md` | `has_attack_trees` | Optional -- attack path portrait pages. Directory-based detection: requires at least one `*-attack-tree.md` file. Falls back to inline trees in `threat-report.md` Section 5 |

### Image File Validation

For image files, verify the file is non-zero size. If an image file exists but is 0 bytes, set its flag to `false` and log a warning:

```
"Skipping {filename}: file is empty (0 bytes)"
```

---

## Data Source Tier Selection

The Findings Detail page uses a 3-tier preference system. Apply the highest available tier.

### Tier 1 — Compensating Controls (Richest)

**Condition**: `has_compensating_controls` is true

**Source**: `compensating-controls.md`

**Columns**: ID, Component, Threat, Residual Score, Residual Severity, Control Status, Recommendation

**Finding keys**: `id`, `component`, `threat`, `residual_score`, `residual_severity`, `control_status`, `recommendation`

### Tier 2 — Risk Scores

**Condition**: `has_risk_scores` is true AND Tier 1 not available

**Source**: `risk-scores.md`

**Columns**: ID, Component, Threat, Composite Score, Severity, CVSS, Exploitability

**Finding keys**: `id`, `component`, `threat`, `composite_score`, `severity`, `cvss`, `exploitability`

### Tier 3 — Threats Only (Fallback)

**Condition**: Default when neither Tier 1 nor Tier 2 available

**Source**: `threats.md` Section 7

**Columns**: ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation

**Finding keys**: `id`, `component`, `threat`, `likelihood`, `impact`, `risk_level`, `mitigation`

### Tier Selection Logic

```
if has_compensating_controls:
    data_source_tier = 1
elif has_risk_scores:
    data_source_tier = 2
else:
    data_source_tier = 3
```

Record the selected tier as `data_source_tier` (integer: 1, 2, or 3).

---

## Detection Reporting

After artifact verification and tier selection, display a brief summary:

```
Report Assembler: {N} artifacts detected, Tier {tier} selected
Generating report-data.typ...
```

Where `{N}` is the count of artifacts with their flag set to `true` (including `threats.md`).

---

## Schema Version Compatibility

| Schema Version | Behavior |
|---------------|----------|
| `v1.0` | Section 4a (Correlated Findings) does not exist -- skip correlated findings references. All other sections parse identically. Log: `"Schema v1.0 detected — correlated findings omitted from executive summary"` |
| `v1.1` | Full feature set -- parse all sections |
| Unknown | Treat as v1.0 (conservative), log warning |

---

## Legacy Data Extraction Reference

The extraction script (`scripts/extract-report-data.py`) handles all artifact parsing deterministically. The following describes what the script extracts from each source for reference.

### From threats.md

- **Section 1 (System Overview)**: Components table, data flows table, project name
- **Section 2 (Trust Boundaries)**: Trust zones table, boundary crossings table
- **Section 7 (Findings Summary)**: Tier 3 findings with severity counts
- **Severity distribution**: Critical/High/Medium/Low counts
- **Component distribution**: Finding counts per component

### From risk-scores.md

- **Section 1 (Executive Summary)**: Updated severity counts (preferred over threats.md counts)
- **Section 2 (Scored Threat Table)**: Tier 2 findings with composite scores

### From compensating-controls.md

- **Section 2 (Coverage Matrix)**: Tier 1 findings with residual scores and control status
- **Coverage summary**: Per-STRIDE-category control status counts (Found/Partial/Missing)
- **Detailed controls**: Individual control entries with evidence and effectiveness
- **Section 3 (Recommendations)**: Remediation actions with SLA derivation

### From threat-report.md

- **Section 1 (Executive Summary)**: Executive narrative text (Risk Posture, Top 5 Threats, Key Recommendations)
- **Remediation Timeline**: Action items with severity, finding ID, recommendation, SLA, status

### Remediation Source Priority

1. `compensating-controls.md` Section 3 recommendations (includes residual risk context)
2. `threat-report.md` remediation timeline
3. None -- set `remediation-actions = none`
