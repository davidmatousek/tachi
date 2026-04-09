# Data Model: Downstream Baseline Propagation

## Delta Status Enum

The `delta_status` field classifies each finding's lifecycle relative to the baseline run.

| Value | Description | Downstream Behavior |
|-------|-------------|---------------------|
| `NEW` | First appearance — no baseline match | Generate fresh content; highlight in output |
| `UNCHANGED` | Identical to baseline finding | Carry forward; note as stable |
| `UPDATED` | Same finding with changed context | Generate fresh content; note context change |
| `RESOLVED` | Baseline finding no longer applicable | Exclude from active counts; separate section |

**Default**: When no baseline is present, all findings implicitly have `delta_status: NEW`.

## Baseline Frontmatter Fields

Extracted from threats.md YAML frontmatter `baseline:` block.

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `baseline.source` | string | yes | File path of baseline used. Null on first run. |
| `baseline.date` | string | yes | ISO date of baseline run. |
| `baseline.finding_count` | integer | yes | Total findings in baseline. |
| `baseline.run_id` | string | yes | Unique baseline run identifier (YYYY-MM-DDTHH-MM-SS). |

**Baseline detection**: `baseline.source != null` indicates a baseline-compared run. All downstream consumers use this as the primary gate for delta-aware behavior.

## Finding Dict (parse_threats_findings output)

| Key | Type | Always Present | Source Column |
|-----|------|---------------|---------------|
| `id` | string | yes | "Finding ID" |
| `component` | string | yes | "Component" |
| `threat` | string | yes | "Threat" |
| `likelihood` | string | yes | "Likelihood" (default: em dash) |
| `impact` | string | yes | "Impact" (default: em dash) |
| `risk_level` | string | yes | "Risk Level" |
| `mitigation` | string | yes | "Mitigation" |
| `delta_status` | string | only when present | "Status" |

**Note**: `baseline_run_id` is NOT a per-finding field in Section 7. It is extracted from frontmatter via `parse_baseline_frontmatter()` and available as `result["run_id"]`. Downstream consumers that need the baseline run ID should call `parse_baseline_frontmatter()` separately.

## Delta Counts Object (infographic extraction output)

| Key | Type | Description |
|-----|------|-------------|
| `new` | integer | Count of findings with delta_status NEW |
| `unchanged` | integer | Count of findings with delta_status UNCHANGED |
| `updated` | integer | Count of findings with delta_status UPDATED |
| `resolved` | integer | Count of findings with delta_status RESOLVED |

Only present in JSON output when baseline data is detected.

## Typst Data Variables (report extraction output)

New variables added to report-data.typ:

| Variable | Type | Description |
|----------|------|-------------|
| `has-baseline` | boolean | Whether baseline data is present |
| `baseline-source` | string | Baseline file path (or "none") |
| `baseline-date` | string | Baseline date (or "none") |
| `baseline-finding-count` | integer | Baseline finding count (or 0) |
| `baseline-run-id` | string | Baseline run ID (or "none") |
| `delta-new-count` | integer | Count of NEW findings |
| `delta-unchanged-count` | integer | Count of UNCHANGED findings |
| `delta-updated-count` | integer | Count of UPDATED findings |
| `delta-resolved-count` | integer | Count of RESOLVED findings |
| `resolved-findings` | array | List of RESOLVED finding objects |
