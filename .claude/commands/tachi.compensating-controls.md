---
description: Scan a target codebase against scored threats to detect existing security controls, recommend missing controls, calculate residual risk, and output dual-format results (compensating-controls.md + compensating-controls.sarif)
---

## User Input

```text
$ARGUMENTS
```

Consider user input before proceeding (if not empty).

## Step 0: Parse Flags

1. If `$ARGUMENTS` contains `--target <path>`:
   - Set `target_path` to the specified path
   - Strip `--target <path>` from `$ARGUMENTS` (trim extra whitespace)
2. Default: `target_path = "."` (current working directory)

3. If `$ARGUMENTS` contains `--output-dir <path>`:
   - Set `output_dir` to the specified path
   - Strip `--output-dir <path>` from `$ARGUMENTS` (trim extra whitespace)
4. Default: `output_dir = null` (outputs written to same directory as input risk-scores)

5. Remaining `$ARGUMENTS` is treated as the risk-score input directory path.
6. Default input directory: current working directory (`.`)

## Overview

Single-command entry point for tachi compensating controls analysis — the third link in the pipeline: `/threat-model` → `/risk-score` → `/compensating-controls`. Validates prerequisites, locates risk score input and target codebase, invokes the control-analyzer agent, and writes dual-format output files.

**Flow**: Validate → Locate Input → Analyze Controls → Report

**Output suite**:
- `compensating-controls.md` — Coverage matrix, control details with file:line evidence, recommendations, residual risk summary
- `compensating-controls.sarif` — SARIF 2.1.0 with per-finding residual scores, control properties, and preserved fingerprints

## Step 1: Validate Prerequisites

1. **Check tachi agents are installed**:
   - Verify `.claude/agents/tachi/control-analyzer.md` exists
   - If missing, display:
     ```
     TACHI CONTROL ANALYZER NOT INSTALLED
     Run: cp -r <tachi-repo>/adapters/claude-code/agents/control-analyzer.md .claude/agents/tachi/
     See: https://github.com/davidmatousek/tachi
     ```
   - Halt if missing.

2. **Check risk score input exists**:
   - Look for `risk-scores.md` in the input directory
   - If not found, look for `risk-scores.sarif` in the input directory
   - If neither exists, display:
     ```
     NO RISK SCORE OUTPUT FOUND
     Neither risk-scores.md nor risk-scores.sarif found in: {input_dir}
     Run /risk-score first to generate scored threat output.
     ```
   - Halt if neither exists.

3. **Determine input file and format**:
   - If `risk-scores.md` exists: set `input_file = risk-scores.md`, `input_format = markdown`
   - If only `risk-scores.sarif` exists: set `input_file = risk-scores.sarif`, `input_format = sarif`
   - `risk-scores.md` is the canonical source; `risk-scores.sarif` is the fallback
   - Display: `Input: {input_file} ({input_format} format)`

4. **Validate target codebase**:
   - Verify `target_path` is an existing directory with at least one file
   - If directory does not exist, display:
     ```
     TARGET CODEBASE NOT FOUND
     Directory does not exist: {target_path}
     Provide a valid project path via --target.
     ```
   - Halt if invalid.
   - Display: `Target: {target_path}`

5. **Determine output directory**:
   - If `--output-dir` was specified: use that path
   - Otherwise: use the same directory as the input file
   - Create output directory if it does not exist
   - Display: `Output: {output_dir}`

6. **Check for optional architecture.md**:
   - Look for `architecture.md` in the input directory and its parent directory
   - If found: set `architecture_path` to the resolved path (enables architecture-aware component-to-file mapping)
   - If not found: set `architecture_path = null` (agent will fall back to heuristic discovery)

## Step 2: Run Control Analysis

**IMPORTANT**: Do NOT read or embed the input files in the agent prompt. The control-analyzer agent has Read tool access and will load files on-demand to manage its own context window. Pass file **paths**, not file **contents**.

1. Invoke the `tachi-control-analyzer` agent with the following prompt:

   ```
   Analyze scored threat findings against the target codebase to detect existing
   security controls, classify each threat, recommend remediation for gaps, and
   calculate residual risk. Execute your complete 6-phase analysis pipeline:
   Phase 1 (Parse Input) → Phase 2 (Discover Codebase) → Phase 3 (Detect Controls) →
   Phase 4 (Map & Classify) → Phase 5 (Recommend & Calculate Residual Risk) →
   Phase 6 (Generate Output).

   Input file: {absolute path to input_file}
   Input format: {input_format}
   Architecture file: {absolute path to architecture_path, or "none"}
   Target codebase: {target_path}
   Output directory: {output_dir}
   Analysis date: {current date YYYY-MM-DD}

   Read the input file yourself using the Read tool. For large inputs,
   read in sections to manage context.

   Write output files:
   - compensating-controls.md
   - compensating-controls.sarif
   ```

2. Wait for the control-analyzer agent to complete all 6 pipeline phases.

## Step 3: Report Results

Display summary:

```
COMPENSATING CONTROLS ANALYSIS COMPLETE
Input: {input_file} ({input_format} format)
Target: {target_path}
Output: {output_dir}

Files generated:
  compensating-controls.md    — Coverage matrix + control details + recommendations + residual risk
  compensating-controls.sarif — SARIF 2.1.0 with residual scores + control properties

Coverage:
  Control Found:    {found_count} ({found_pct}%)
  Partial Control:  {partial_count} ({partial_pct}%)
  No Control Found: {missing_count} ({missing_pct}%)
  Total:            {total_count}

Risk Reduction:
  Total Inherent:  {total_inherent}
  Total Residual:  {total_residual}
  Reduction:       {risk_reduction_pct}%

Residual Severity Distribution:
  Critical: {count}    High: {count}    Medium: {count}    Low: {count}

Highest-Risk Unmitigated: {id} — {component} — Composite {score} ({severity})

Next steps:
  1. Review Critical/High unmitigated findings in compensating-controls.md Section 4
  2. Implement recommended controls starting from highest-risk gaps
  3. Upload compensating-controls.sarif to GitHub Code Scanning (supersedes risk-scores.sarif)
  4. Run /infographic to generate visual threat infographics (uses compensating-controls.md as richest data source)
  5. Run /security-report to generate the PDF assessment booklet (auto-includes infographic images)
  6. Re-run /compensating-controls after implementing controls to measure improvement
```

## Usage Examples

```bash
# Minimal — analyze codebase in current directory using risk-scores in cwd
/compensating-controls

# Specify target codebase
/compensating-controls --target ./my-app

# Specify both target and output
/compensating-controls --target ./my-app --output-dir ./reports/

# Analyze the example app
/compensating-controls --target examples/agentic-app/ examples/agentic-app/sample-report/
```

## Quality Checklist

- [ ] Control-analyzer agent installed in `.claude/agents/tachi/`
- [ ] Risk score input exists (risk-scores.md or risk-scores.sarif)
- [ ] Input format correctly detected (markdown canonical, SARIF fallback)
- [ ] Target codebase validated (directory exists with files)
- [ ] Architecture file located when available (improves component-to-file mapping)
- [ ] Both output files generated (compensating-controls.md + compensating-controls.sarif)
- [ ] Every scored threat classified (Control Found / Partial / No Control Found)
- [ ] File:line evidence provided for all detected controls
- [ ] Recommendations generated for all partial and missing threats
- [ ] Recommendations sorted by composite score descending
- [ ] Residual risk calculated for all threats (Inherent * (1 - Factor))
- [ ] Coverage matrix complete with summary statistics
- [ ] SARIF output validates against SARIF 2.1.0 schema
- [ ] SARIF fingerprints preserved from source risk-scores.sarif
- [ ] Scores consistent between compensating-controls.md and compensating-controls.sarif
