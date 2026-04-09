---
description: Run quantitative risk scoring on threat model output — produces risk-scores.md and risk-scores.sarif with four-dimensional scores, composite ratings, and governance fields
---

## User Input

```text
$ARGUMENTS
```

Consider user input before proceeding (if not empty).

## Step 0: Parse Flags

1. If `$ARGUMENTS` contains `--output-dir <path>`:
   - Set `output_dir` to the specified path
   - Strip `--output-dir <path>` from `$ARGUMENTS` (trim extra whitespace)
2. Default: `output_dir = null` (outputs written to same directory as input)

3. Remaining `$ARGUMENTS` is treated as the input directory path.
4. Default input directory: current working directory (`.`)

## Overview

Single-command entry point for tachi quantitative risk scoring. Validates prerequisites, locates threat model output, invokes the risk-scorer agent, and writes scored output files.

**Flow**: Validate → Locate Input → Score → Report

**Output suite**:
- `risk-scores.md` — scored threat table, executive summary, dimensional breakdowns, governance fields, methodology
- `risk-scores.sarif` — SARIF 2.1.0 with per-finding composite scores in `security-severity` and scoring properties in result property bags

## Step 1: Validate Prerequisites

1. **Check tachi agents are installed**:
   - Verify `.claude/agents/tachi/risk-scorer.md` exists
   - If missing, display:
     ```
     TACHI RISK SCORER NOT INSTALLED
     Run: cp -r <tachi-repo>/adapters/claude-code/agents/risk-scorer.md .claude/agents/tachi/
     See: https://github.com/davidmatousek/tachi
     ```
   - Halt if missing.

2. **Check input files exist**:
   - Look for `threats.md` in the input directory
   - If not found, look for `threats.sarif` in the input directory
   - If neither exists, display:
     ```
     NO THREAT MODEL OUTPUT FOUND
     Neither threats.md nor threats.sarif found in: {input_dir}
     Run /threat-model first to generate threat model output.
     ```
   - Halt if neither exists.

3. **Determine input file and format**:
   - If `threats.md` exists: set `input_file = threats.md`, `input_format = markdown`
   - If only `threats.sarif` exists: set `input_file = threats.sarif`, `input_format = sarif`
   - `threats.md` is the canonical source; `threats.sarif` is the fallback
   - Display: `Input: {input_file} ({input_format} format)`

4. **Determine output directory**:
   - If `--output-dir` was specified: use that path
   - Otherwise: use the same directory as the input file
   - Create output directory if it does not exist
   - Display: `Output: {output_dir}`

5. **Check for optional architecture.md**:
   - Look for `architecture.md` in the input directory and its parent directory
   - If found: set `architecture_path` to the resolved path (used for reachability scoring)
   - If not found: set `architecture_path = null` (reachability will use trust zone data only, or default to 5.0)

## Step 2: Run Risk Scoring

**IMPORTANT**: Do NOT read or embed the input files in the agent prompt. The risk-scorer agent has Read tool access and will load files on-demand to manage its own context window. Pass file **paths**, not file **contents**.

1. Invoke the `tachi-risk-scorer` agent with the following prompt:

   ```
   Score the threat model output using your complete scoring pipeline
   (Threat Parsing → Trust Zone Extraction → Dimensional Scoring → Composite
   Calculation → Governance Fields → Output Generation).

   Input file: {absolute path to input_file}
   Input format: {input_format}
   Architecture file: {absolute path to architecture_path, or "none"}
   Output directory: {output_dir}
   Scoring date: {current date YYYY-MM-DD}

   Read the input file yourself using the Read tool. For large threat models,
   read in sections: parse finding tables (Sections 3, 4, 4a) and trust zones
   (Section 2) first. You do not need to load the full file at once.

   Write output files:
   - risk-scores.md
   - risk-scores.sarif
   ```

2. Wait for the risk-scorer agent to complete all 6 of its internal analysis phases.

## Step 3: Report Results

Display summary:

```
RISK SCORING COMPLETE
Input: {input_file} ({input_format} format)
Output: {output_dir}

Files generated:
  risk-scores.md    — Scored threat table + executive summary + methodology
  risk-scores.sarif — SARIF 2.1.0 with quantitative scores

Severity Distribution:
  Critical: {count}    High: {count}    Medium: {count}    Low: {count}
  Total findings scored: {total}

Highest-Risk Component: {component_name} (composite: {max_composite})

Next steps:
  1. Review Critical/High findings in risk-scores.md Section 2
  2. Assign risk owners in Section 4 (Governance Fields)
  3. Run /compensating-controls --target <codebase> to detect existing security controls and calculate residual risk
  4. Upload risk-scores.sarif to GitHub Code Scanning (supersedes threats.sarif)
```

## Usage Examples

```bash
# Minimal — score threats in current directory
/risk-score

# Specify input directory
/risk-score path/to/threat-model-output/

# Custom output directory
/risk-score path/to/threat-model-output/ --output-dir reports/risk/

# Score a specific example
/risk-score examples/agentic-app/sample-report/
```

## Quality Checklist

- [ ] Risk-scorer agent installed in `.claude/agents/tachi/`
- [ ] Input file exists (threats.md or threats.sarif)
- [ ] Input format correctly detected (markdown canonical, SARIF fallback)
- [ ] Architecture file located when available (improves reachability scoring)
- [ ] Both output files generated (risk-scores.md + risk-scores.sarif)
- [ ] All findings scored with four dimensions (CVSS, exploitability, scalability, reachability)
- [ ] Composite scores calculated using weighted formula
- [ ] Severity bands mapped correctly (Critical/High/Medium/Low)
- [ ] Governance fields populated (owner, SLA, disposition, review date)
- [ ] Scored threat table sorted by composite descending
- [ ] SARIF output validates against SARIF 2.1.0 schema
- [ ] SARIF fingerprints preserved from source threats.sarif
- [ ] Scores consistent between risk-scores.md and risk-scores.sarif
