---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-08
    status: APPROVED
    notes: "15/15 FRs covered, 10/10 files mapped, 6/6 success criteria validated, 0 scope creep."
  architect_signoff:
    agent: architect
    date: 2026-04-08
    status: APPROVED
    notes: "All 5 prior findings resolved: Section 7 Status column added (blocking fix), parse_resolved_findings() for Section 4b, parse_baseline_frontmatter() as new function, schema version verified, validation plan expanded."
  techlead_signoff: null
---

# Implementation Plan: Downstream Baseline Propagation

**Branch**: `104-downstream-baseline-propagation` | **Date**: 2026-04-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/104-downstream-baseline-propagation/spec.md`

## Summary

Propagate `delta_status` awareness (NEW, UNCHANGED, UPDATED, RESOLVED) to all downstream consumers in the tachi pipeline. Ten files are modified across four layers: shared parser, extraction scripts, agent instructions, and output schema templates. The approach follows the delta-driven branching pattern established in Feature 074 (risk-scorer, control-analyzer), guarding all new logic behind presence checks for backward compatibility.

## Technical Context

**Language/Version**: Python 3.11 (extraction scripts, shared parser); Markdown (agent instructions, schema templates, command files)
**Primary Dependencies**: `tachi_parsers.py` (shared parser module consumed by both extraction scripts)
**Storage**: File-based (markdown artifacts — threats.md, threat-report.md, infographic data JSON, report-data.typ)
**Testing**: Manual validation using second-brain-mcp baseline comparison (April 8 vs March 31 runs); no-baseline regression test
**Target Platform**: Local-first CLI (any platform with Python 3.11+)
**Project Type**: Methodology template — all deliverables are markdown and Python files, no compiled application code
**Constraints**: All changes must be additive (ADR-018); backward compatible when no baseline data present

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| III. Backward Compatibility | PASS | All delta logic guarded behind presence checks; no baseline = identical behavior to pre-104 |
| VII. Definition of Done | PASS | Validation via second-brain-mcp test case + no-baseline regression |
| IX. Git Workflow | PASS | Feature branch `104-downstream-baseline-propagation` created |
| X. Product-Spec Alignment | PASS | Spec has PM APPROVED sign-off; plan requires dual PM+Architect sign-off |

## Project Structure

### Documentation (this feature)

```
specs/104-downstream-baseline-propagation/
├── plan.md              # This file
├── research.md          # Research phase output (completed)
├── spec.md              # Feature specification (PM approved)
├── data-model.md        # Delta data model documentation
├── checklists/
│   └── requirements.md  # Quality checklist
└── tasks.md             # Task breakdown (pending)
```

### Source Code (repository root)

```
scripts/
├── tachi_parsers.py                 # MODIFY: add delta_status + baseline_run_id to parse_threats_findings()
├── extract-infographic-data.py      # MODIFY: delta-aware severity counts, delta breakdown output
└── extract-report-data.py           # MODIFY: delta_status in Typst data, RESOLVED separation

agents/
├── threat-report.md                 # MODIFY: delta branching for attack trees, Section 8, exec summary
└── threat-infographic.md            # MODIFY: delta context in infographic generation

.claude/agents/tachi/
└── report-assembler.md              # MODIFY: RESOLVED separation, NEW badge, delta counts

.claude/commands/
├── infographic.md                   # MODIFY: delta context in Gemini prompts
└── security-report.md               # MODIFY: delta column handling in PDF

templates/tachi/output-schemas/
├── threats.md                       # MODIFY: add Section 8 Delta Summary structure
└── threat-report.md                 # MODIFY: add Section 8, baseline handling guidance
```

**Structure Decision**: No new files created. All changes modify existing files in their current locations. The shared parser update cascades naturally to both extraction scripts through existing import paths.

## Components

### Component 1: Shared Parser Delta Support

**File**: `scripts/tachi_parsers.py`

#### 1a: Extend Section 7 table with Status column

**Function**: `parse_threats_findings()` (line 419)

**Current behavior**: Parses Section 7 (Recommended Actions) table with columns: `Finding ID | Component | Threat | Risk Level | Mitigation`. The Status column that carries `delta_status` exists only in Sections 3/4 STRIDE+AI tables, NOT in Section 7.

**Resolution (per Architect review)**: The threats.md output schema template (Component 9) must add a "Status" column to the Section 7 Recommended Actions table. The orchestrator already populates Section 7 from the same finding data used in Sections 3/4, so it will carry `delta_status` through to Section 7. This is the least disruptive approach — it keeps the parser reading the same table it always has.

**Parser change**: After the schema adds Status to Section 7, `parse_threats_findings()` adds delta fields:

```python
findings.append({
    "id": row.get("Finding ID", "").strip(),
    "component": row.get("Component", "").strip(),
    "threat": row.get("Threat", "").strip(),
    "likelihood": "\u2014",  # em dash — Section 7 omits Likelihood/Impact
    "impact": "\u2014",
    "risk_level": row.get("Risk Level", "").strip(),
    "mitigation": row.get("Mitigation", "").strip(),
})
# Delta fields: include only when present (backward compatible)
if "Status" in row and row["Status"].strip():
    findings[-1]["delta_status"] = row["Status"].strip()
```

**Backward compatibility**: When input threats.md Section 7 has no Status column (pre-104 output), `row.get("Status", "")` returns empty string and the field is skipped. Callers see identical output to pre-104.

#### 1b: New function `parse_resolved_findings()`

**Purpose**: Parse Section 4b (Resolved Findings) which has a DIFFERENT column schema than STRIDE/AI tables and Section 7.

**Section 4b columns**: `ID | Component | Threat | Last Risk Level | Resolution Reason`

This is a new function, NOT an extension of `parse_threats_findings()`:

```python
def parse_resolved_findings(content: str) -> list:
    """Parse Section 4b Resolved Findings table.

    Returns list of resolved finding dicts. Returns empty list
    when Section 4b is absent (first run, no baseline).
    """
    rows = parse_markdown_table(content, "## 4b. Resolved Findings")
    if not rows:
        return []
    findings = []
    for row in rows:
        findings.append({
            "id": row.get("ID", "").strip(),
            "component": row.get("Component", "").strip(),
            "threat": row.get("Threat", "").strip(),
            "risk_level": row.get("Last Risk Level", "").strip(),
            "resolution_reason": row.get("Resolution Reason", "").strip(),
            "delta_status": "RESOLVED",
        })
    return findings
```

**Backward compatibility**: When Section 4b is absent (first run), returns empty list.

#### 1c: New function `parse_baseline_frontmatter()`

**Purpose**: Extract nested `baseline.*` fields from threats.md YAML frontmatter.

**Important**: The existing `parse_frontmatter()` function (line 210) explicitly skips indented/nested lines. This new function is a SEPARATE function with its own nested-key parsing logic. The existing `parse_frontmatter()` must NOT be modified.

```python
def parse_baseline_frontmatter(content: str) -> dict:
    """Extract baseline metadata from threats.md frontmatter.

    Parses the nested baseline: block. Returns dict with keys:
    source, date, finding_count, run_id. All values are None
    when no baseline is present.
    """
    result = {"source": None, "date": None, "finding_count": None, "run_id": None}
    # Extract frontmatter text between --- delimiters
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return result
    fm = match.group(1)
    # Find baseline: block and parse nested keys
    in_baseline = False
    for line in fm.split("\n"):
        if line.strip().startswith("baseline:"):
            in_baseline = True
            continue
        if in_baseline:
            if not line.startswith(" ") and not line.startswith("\t"):
                break  # left the baseline block
            kv = re.match(r'^\s+(\w[\w_]*)\s*:\s*"?([^"]*?)"?\s*$', line)
            if kv:
                key, val = kv.group(1), kv.group(2).strip()
                if val.lower() in ("null", "~", ""):
                    val = None
                if key in result:
                    result[key] = val
    return result
```

Both extraction scripts must import and call this new function.

### Component 2: Infographic Extraction Script

**File**: `scripts/extract-infographic-data.py`

**Changes**:
1. **Import new functions**: Add `parse_baseline_frontmatter` and `parse_resolved_findings` to imports from `tachi_parsers`.
2. **Baseline detection**: Call `parse_baseline_frontmatter()` — if `source` is None, skip all delta logic (stateless mode).
3. **Delta-aware severity counts**: After parsing active findings via `parse_threats_findings()`, check for `delta_status` key. If present, compute severity distribution from active findings only (exclude any with `delta_status == "RESOLVED"` — though RESOLVED findings primarily come from Section 4b via `parse_resolved_findings()`).
4. **Resolved finding count**: Call `parse_resolved_findings()` to get Section 4b count for the delta breakdown.
5. **Delta breakdown fields**: Add `delta_counts` object to JSON output: `{"new": N, "unchanged": N, "updated": N, "resolved": N}`.
6. **Top findings delta annotation**: Include `delta_status` field per finding in the top findings list.

**Backward compatibility**: When no delta_status in findings (pre-074 input), severity counts computed as today. `delta_counts` omitted from JSON output.

### Component 3: Report Extraction Script

**File**: `scripts/extract-report-data.py`

**Changes**:
1. **Import new functions**: Add `parse_baseline_frontmatter` and `parse_resolved_findings` to imports from `tachi_parsers`.
2. **Baseline metadata**: Call `parse_baseline_frontmatter()` and include as Typst variables (`baseline_source`, `baseline_date`, `baseline_finding_count`, `baseline_run_id`).
3. **Per-finding delta_status**: Include `delta_status` field in Typst data variables for each active finding (from `parse_threats_findings()`).
4. **RESOLVED findings from Section 4b**: Call `parse_resolved_findings()` to get resolved findings with their distinct column schema (`id`, `component`, `threat`, `risk_level`, `resolution_reason`, `delta_status`). Write as `resolved_findings` list to report-data.typ.
5. **Delta-aware severity counts**: Active severity counts from `parse_threats_findings()` (all non-RESOLVED). Resolved count from `parse_resolved_findings()`. Include both active and total counts.

**Backward compatibility**: When no delta data present, `resolved_findings` is empty, active counts equal total counts, baseline variables are "none".

### Component 4: Threat-Report Agent Instructions

**File**: `agents/threat-report.md`

**Changes to Input Contract section**:
1. Add `delta_status` and `baseline_run_id` to the Finding IR Fields Consumed table
2. Add Section 4b (Resolved Findings) to Required Input Sections table
3. Add baseline frontmatter fields to the input contract

**Changes to Output Contract / Generation Instructions**:
1. **Executive Summary (Section 1)**: When delta data present, include delta counts in risk posture summary (e.g., "Of 22 findings, 5 are new, 12 unchanged, 2 updated, and 3 resolved")
2. **Threat Analysis (Section 3)**: Note delta status inline with finding narrative (e.g., "[NEW]" prefix for new findings, "[UNCHANGED — carried forward]" for stable findings)
3. **Attack Trees (Section 5)**: Branch by delta_status:
   - NEW: Generate fresh attack tree
   - UPDATED: Generate fresh attack tree with note "Context changed since baseline"
   - UNCHANGED: Skip tree generation, note "Attack tree carried forward from baseline — finding unchanged since {baseline_date}"
   - RESOLVED: Not applicable (excluded from Sections 3-5, appear only in Section 4b of input)
4. **Section 8 — Delta Summary** (new): When baseline data present, generate:
   - Finding lifecycle breakdown table (new/unchanged/updated/resolved counts)
   - Remediation progress narrative (resolved findings as proof of remediation)
   - Baseline reference (source file, date, run ID, original finding count)
5. **No-baseline behavior**: When `baseline.source` is null in frontmatter, omit Section 8 entirely, generate all attack trees fresh, no delta annotations in narrative

### Component 5: Infographic Agent Instructions

**File**: `agents/threat-infographic.md`

**Changes**:
1. **Input Contract**: Add delta_status to consumed fields, note that RESOLVED findings should be excluded from severity distribution
2. **Risk Distribution section**: When delta data present, note that severity counts reflect active findings only (RESOLVED excluded)
3. **Delta context**: When delta data present, emphasize new attack surfaces in visual design directives

### Component 6: Report-Assembler Agent Instructions

**File**: `.claude/agents/tachi/report-assembler.md`

**Changes**:
1. **Finding extraction**: When delta data present, separate findings into active and resolved lists
2. **Active findings table**: Annotate NEW findings with a visual indicator (e.g., bold or tag)
3. **Resolved Findings section**: When resolved findings exist, render a separate "Resolved Findings" section after the active findings table
4. **Executive summary**: Include delta counts when available
5. **No-baseline behavior**: When no delta data, render findings as today (no separation, no annotations)

### Component 7: Infographic Command

**File**: `.claude/commands/infographic.md`

**Changes**:
1. When orchestrating infographic generation, detect baseline presence in source threats.md
2. Pass delta context to the agent: note that delta_counts are available in extracted data
3. When constructing Gemini prompts, include delta emphasis directives (highlight new findings, note resolved count)

### Component 8: Security-Report Command

**File**: `.claude/commands/security-report.md`

**Changes**:
1. When orchestrating PDF generation, detect baseline presence in source threats.md
2. Pass delta context to the report-assembler agent: note that resolved findings should be separated
3. Include delta counts in the command's artifact detection summary

### Component 9: Threats.md Output Schema Template

**File**: `templates/tachi/output-schemas/threats.md`

**Changes**:

**9a: Add Status column to Section 7 Recommended Actions table** (resolves Architect Finding 1 — BLOCKING)

The current Section 7 table has columns: `Finding ID | Component | Threat | Risk Level | Mitigation`. Add a "Status" column to carry delta_status through to the table that `parse_threats_findings()` reads. Updated columns: `Finding ID | Status | Component | Threat | Risk Level | Mitigation`.

This is the critical change that enables the shared parser (Component 1a) to access delta_status. The orchestrator already has delta_status per finding — it just needs to emit it in Section 7 alongside the existing columns. When no baseline is present (first run), all Status values are "NEW".

**9b: Add Section 8: Delta Summary** after Section 7 with the following structure:

```markdown
## 8. Delta Summary

_Present only when a baseline was used for the current run. Omit entirely on first run (no baseline)._

### Finding Lifecycle

| Status | Count | Description |
|--------|-------|-------------|
| NEW | _{count}_ | Findings discovered in this run with no baseline match |
| UNCHANGED | _{count}_ | Findings identical to baseline (same component, threat, assessment) |
| UPDATED | _{count}_ | Findings with changed context since baseline |
| RESOLVED | _{count}_ | Baseline findings no longer applicable |
| **Total** | _{total}_ | Sum of all findings (active + resolved) |

### Baseline Reference

| Field | Value |
|-------|-------|
| Source | _{baseline file path}_ |
| Date | _{baseline date}_ |
| Baseline Findings | _{baseline finding count}_ |
| Run ID | _{baseline run ID}_ |
```

**Note**: Section 4b (Resolved Findings) already exists in the template. Section 8 provides the aggregate summary; Section 4b provides the individual resolved finding details.

### Component 10: Threat-Report.md Output Schema Template

**File**: `templates/tachi/output-schemas/threat-report.md`

**Changes**:
1. Update frontmatter field table: add `baseline_source`, `baseline_date`, `delta_counts` fields
2. Add **Section 8: Delta Summary** section after Section 7:
   - Finding lifecycle breakdown
   - Remediation progress narrative
   - Baseline reference
3. Add baseline handling guidance note to Section 5 (Attack Trees): "When delta_status is UNCHANGED, note carried forward from baseline instead of generating fresh tree"
4. Update schema_version from "1.0" to "1.1" — verified no downstream consumers gate on threat-report.md schema version (extract-report-data.py does not check schema_version)

## Data Flow

```
threats.md (with delta_status in Sections 3, 4, 4b, 8)
    │
    ├── tachi_parsers.py::parse_threats_findings()
    │   └── Returns findings with delta_status + baseline_run_id
    │
    ├── extract-infographic-data.py
    │   ├── Filters: active findings (severity counts) vs resolved
    │   ├── Adds: delta_counts to JSON output
    │   └── Output: infographic-data.json → infographic agent
    │
    ├── extract-report-data.py
    │   ├── Separates: active_findings vs resolved_findings
    │   ├── Adds: delta_status per finding, baseline metadata
    │   └── Output: report-data.typ → Typst PDF compilation
    │
    ├── threat-report agent
    │   ├── Reads: threats.md directly
    │   ├── Branches: attack tree generation by delta_status
    │   ├── Adds: Section 8 Delta Summary, exec summary delta counts
    │   └── Output: threat-report.md
    │
    ├── infographic agent + command
    │   ├── Reads: extracted JSON data
    │   ├── Uses: active-only severity counts, delta emphasis
    │   └── Output: infographic spec + optional JPEG
    │
    └── report-assembler agent + command
        ├── Reads: report-data.typ
        ├── Renders: active table + resolved section + delta badges
        └── Output: security-report.pdf
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Shared Parser | Python 3.11 | `tachi_parsers.py` — deterministic markdown table parsing |
| Extraction Scripts | Python 3.11 | `extract-infographic-data.py`, `extract-report-data.py` — structured data extraction |
| Agent Instructions | Markdown | `agents/threat-report.md`, `agents/threat-infographic.md`, `.claude/agents/tachi/report-assembler.md` |
| Command Files | Markdown | `.claude/commands/infographic.md`, `.claude/commands/security-report.md` |
| Schema Templates | Markdown | `templates/tachi/output-schemas/threats.md`, `templates/tachi/output-schemas/threat-report.md` |
| PDF Rendering | Typst | `templates/tachi/security-report/` — consumes report-data.typ variables |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Backward compatibility regression | Low | High | All delta logic guarded behind presence checks; no-baseline regression test |
| Parser field name mismatch | Medium | Medium | Confirmed: threats.md uses "Status" column header; parser maps to `delta_status` dict key |
| Section 8 ordering conflicts | Low | Low | Section 4b (Resolved Findings) already exists; Section 8 (Delta Summary) is additive aggregation |
| Extraction script JSON schema change | Low | Medium | New fields are additive; existing consumers that don't check delta_counts are unaffected |

## Validation Plan

1. **Primary test**: Run baseline-compared threat model on second-brain-mcp (April 8 vs March 31 runs)
   - Verify RESOLVED findings excluded from active counts in all output formats
   - Verify NEW findings highlighted/annotated in reports and infographics
   - Verify Section 8 Delta Summary present in threat-report.md
   - Verify delta counts in executive summaries

2. **Regression test**: Run threat model without baseline (first run on fresh architecture)
   - Verify output is identical to pre-Feature-104 behavior
   - Verify no Section 8, no delta annotations, no resolved sections
   - Verify severity counts include all findings

3. **Parser unit check**: Call `parse_threats_findings()` on both baseline-aware and pre-074 threats.md
   - Verify delta fields present when input has Status column in Section 7
   - Verify identical output when input lacks Status column

4. **Section 4b resolved findings test**: Call `parse_resolved_findings()` on threats.md with Section 4b
   - Verify resolved findings parsed with correct column mapping (ID, Component, Threat, Last Risk Level, Resolution Reason)
   - Verify `delta_status: "RESOLVED"` injected into each returned dict
   - Verify empty list returned when Section 4b is absent

5. **Baseline frontmatter test**: Call `parse_baseline_frontmatter()` on threats.md with and without baseline
   - Verify nested baseline fields extracted correctly (source, date, finding_count, run_id)
   - Verify all fields return None when baseline.source is null
