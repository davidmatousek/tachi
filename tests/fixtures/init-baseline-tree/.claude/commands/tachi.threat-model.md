---
description: Run tachi threat analysis on an architecture description — produces threats.md, SARIF, narrative report, and attack trees
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
2. Default: `output_dir = docs/security/`

3. If `$ARGUMENTS` contains `--version <tag>`:
   - Set `version_tag` to the specified tag (e.g., `v1.0.0`)
   - Append `version_tag` to `output_dir` (e.g., `docs/security/v1.0.0/`)
   - Strip `--version <tag>` from `$ARGUMENTS` (trim extra whitespace)
4. Default: `version_tag = none` (outputs go directly to `output_dir`)

5. Remaining `$ARGUMENTS` is treated as the architecture file path.
6. Default architecture path: `docs/security/architecture.md`

7. Generate a unique run folder:
   - Compute timestamp: `YYYY-MM-DDTHH-MM-SS` (e.g., `2026-03-25T14-30-22`)
   - Set `parent_dir` to the current `output_dir` value (before appending timestamp)
   - Append to output_dir: `{output_dir}/{timestamp}/`
   - This ensures each run produces output in a unique subfolder
   - Example: `examples/agentic-app/test-output/2026-03-25T14-30-22/`

8. Auto-detect baseline from previous runs (unless `--baseline` was explicitly provided):
   - List all subdirectories in `parent_dir`
   - Exclude the current run's timestamp directory
   - Sort remaining directories lexicographically descending (ISO timestamps sort naturally)
   - Check each directory (most recent first) for a `threats.md` file
   - If found: set `baseline_path` to that file
   - If none found: `baseline_path = null` (first run — stateless mode)
   - Display when detected:
     ```
     Baseline detected: {baseline_path}
     ```

## Overview

Single-command entry point for tachi threat modeling. Validates prerequisites, invokes the tachi orchestrator agent against an architecture description, and writes the full output suite to the target directory.

**Flow**: Validate → Analyze → Report

**Output suite**:
- `threats.md` — structured threat model (7 sections + correlated findings)
- `threats.sarif` — SARIF 2.1.0 for CI/CD integration
- `threat-report.md` — narrative report with executive summary and remediation roadmap
- `attack-trees/` — Mermaid attack tree per Critical/High finding

## Step 1: Validate Prerequisites

1. **Check tachi agents are installed**:
   - Verify `.claude/agents/tachi/orchestrator.md` exists
   - If missing, display:
     ```
     TACHI NOT INSTALLED
     Run: cp -r <tachi-repo>/adapters/claude-code/agents/ .claude/agents/tachi/
     See: https://github.com/davidmatousek/tachi
     ```
   - Halt if missing.

2. **Check architecture file exists**:
   - Verify the architecture file path resolves to an existing file
   - If missing, display:
     ```
     ARCHITECTURE FILE NOT FOUND: {architecture_path}
     Create an architecture description at {architecture_path}
     Supported formats: Mermaid, free-text, ASCII, PlantUML, C4
     See examples: <tachi-repo>/examples/
     ```
   - Halt if missing.

3. **Check output directory**:
   - Create `output_dir` if it does not exist
   - If `version_tag` is set and the version directory already exists, warn:
     ```
     WARNING: {output_dir} already exists. Outputs will be overwritten.
     ```
   - Proceed.

## Step 1.4: Architecture Snapshot

1. If the architecture file exists at `{architecture_path}`:
   - Copy the file verbatim to `{output_dir}/{architecture_filename}` (e.g., `architecture.md`)
   - Preserve ALL content including any YAML frontmatter — this is a verbatim file copy, no modifications
   - Display:
     ```
     Architecture snapshot: {output_dir}/{architecture_filename}
     ```
2. If the architecture file does not exist: skip silently (Step 2 validation handles missing file errors).

> **Note**: The snapshot is informational only — a record of the architecture input at the time of analysis. The orchestrator in Step 2 still receives architecture content via `<architecture-input>` tags as before.

## Step 2: Run Threat Analysis

1. Read the architecture file at `{architecture_path}`.

2. Invoke the `tachi-orchestrator` agent with the following prompt:

   ```
   Analyze the following architecture for security threats. Follow your complete
   5-phase methodology (Scope, Determine Threats, Determine Countermeasures,
   Assess, Report).

   Write all output files to: {output_dir}
   - threats.md
   - threats.sarif
   - threat-report.md
   - attack-trees/ (one file per Critical/High finding)

   Baseline: {baseline_path or "none (first run — stateless mode)"}

   Architecture input:

   <architecture-input>
   {contents of architecture file}
   </architecture-input>
   ```

3. Wait for the orchestrator to complete all 5 phases.

## Step 3: Report Results

Display summary (output_dir now includes the timestamped subfolder):

```
THREAT MODEL COMPLETE
Architecture: {architecture_path}
Output: {output_dir}  ← includes timestamped subfolder
Version: {version_tag or "unversioned"}
Baseline: {baseline_path or "none (first run)"}

Files generated:
  architecture.md                     — Architecture snapshot (if source existed)
  threats.md                          — Primary threat model
  threats.sarif                       — SARIF 2.1.0 (CI/CD integration)
  threat-report.md                    — Narrative report
  attack-trees/                       — Mermaid attack trees ({count} files)

Risk Summary:
  Critical: {count}    High: {count}    Medium: {count}    Low: {count}

Delta Summary (when baseline present):
  New: {count}    Unchanged: {count}    Updated: {count}    Resolved: {count}

Next steps:
  1. Review Critical/High findings in {output_dir}/threats.md Section 7
  2. Run /risk-score to add quantitative risk scoring (CVSS, exploitability, scalability, reachability)
  3. Upload threats.sarif to GitHub Code Scanning
  4. Share threat-report.md with stakeholders
```

## Usage Examples

```bash
# Minimal — uses defaults
/threat-model

# Specify architecture file
/threat-model path/to/my-architecture.md

# Version-tagged output for a release
/threat-model docs/security/architecture.md --version v1.0.0

# Custom output directory
/threat-model docs/security/architecture.md --output-dir reports/security/q1-2026/
```

## Quality Checklist

- [ ] Tachi agents installed in `.claude/agents/tachi/` (14 files + templates/)
- [ ] Architecture file exists and contains identifiable components + data flows
- [ ] Output directory created and writable
- [ ] All output files generated (threats.md, threats.sarif, threat-report.md, attack-trees/)
- [ ] Finding IDs follow format: S-N, T-N, R-N, I-N, D-N, E-N, AG-N, LLM-N
- [ ] Coverage matrix includes all components from architecture input
- [ ] Risk levels follow OWASP 3x3 matrix (Critical, High, Medium, Low, Note)
- [ ] SARIF output validates against SARIF 2.1.0 schema
- [ ] Attack trees generated for every Critical and High finding
