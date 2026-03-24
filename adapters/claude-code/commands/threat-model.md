---
description: Run tachi threat analysis on an architecture description — produces threats.md, SARIF, narrative report, attack trees, and infographic
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

## Overview

Single-command entry point for tachi threat modeling. Validates prerequisites, invokes the tachi orchestrator agent against an architecture description, and writes the full output suite to the target directory.

**Flow**: Validate → Analyze → Report

**Output suite**:
- `threats.md` — structured threat model (7 sections + correlated findings)
- `threats.sarif` — SARIF 2.1.0 for CI/CD integration
- `threat-report.md` — narrative report with executive summary and remediation roadmap
- `attack-trees/` — Mermaid attack tree per Critical/High finding
- `threat-infographic-spec.md` — visual risk specification (6 sections)
- `threat-infographic.jpg` — presentation-ready infographic (requires `GEMINI_API_KEY` env var)

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

4. **Check Gemini API key** (informational, not blocking):
   - If `GEMINI_API_KEY` environment variable is not set, display:
     ```
     NOTE: GEMINI_API_KEY not set. Infographic image (threat-infographic.jpg) will be skipped.
     All other outputs will be generated normally.
     Set GEMINI_API_KEY in your environment or .env file to enable image generation.
     ```
   - Proceed regardless.

## Step 2: Run Threat Analysis

1. Read the architecture file at `{architecture_path}`.

2. Invoke the `tachi-orchestrator` agent with the following prompt:

   ```
   Analyze the following architecture for security threats. Follow your complete
   6-phase methodology (Scope, Determine Threats, Determine Countermeasures,
   Assess, Report, Infographic).

   Write all output files to: {output_dir}
   - threats.md
   - threats.sarif
   - threat-report.md
   - attack-trees/ (one file per Critical/High finding)
   - threat-infographic-spec.md
   - threat-infographic.jpg (if GEMINI_API_KEY is available)

   Architecture input:

   <architecture-input>
   {contents of architecture file}
   </architecture-input>
   ```

3. Wait for the orchestrator to complete all 6 phases.

## Step 3: Report Results

Display summary:

```
THREAT MODEL COMPLETE
Architecture: {architecture_path}
Output: {output_dir}
Version: {version_tag or "unversioned"}

Files generated:
  threats.md                    — Primary threat model
  threats.sarif                 — SARIF 2.1.0 (CI/CD integration)
  threat-report.md              — Narrative report
  attack-trees/                 — Mermaid attack trees ({count} files)
  threat-infographic-spec.md    — Infographic specification
  threat-infographic.jpg        — Infographic image {generated | skipped (no API key)}

Risk Summary:
  Critical: {count}    High: {count}    Medium: {count}    Low: {count}

Next steps:
  1. Review Critical/High findings in {output_dir}/threats.md Section 7
  2. Upload threats.sarif to GitHub Code Scanning
  3. Share threat-report.md with stakeholders
```

## Usage Examples

```bash
# Minimal — uses defaults (docs/security/architecture.md → docs/security/)
/threat-model

# Specify architecture file
/threat-model path/to/my-architecture.md

# Version-tagged output for a release
/threat-model docs/security/architecture.md --version v1.0.0

# Custom output directory
/threat-model docs/security/architecture.md --output-dir reports/security/q1-2026/

# Both version and custom base directory
/threat-model docs/security/architecture.md --output-dir reports/security/ --version v2.0.0
```

## Quality Checklist

- [ ] Tachi agents installed in `.claude/agents/tachi/` (14 files)
- [ ] Architecture file exists and contains identifiable components + data flows
- [ ] Output directory created and writable
- [ ] All 6 output files generated (5 mandatory + 1 conditional on API key)
- [ ] Finding IDs follow format: S-N, T-N, R-N, I-N, D-N, E-N, AG-N, LLM-N
- [ ] Coverage matrix includes all components from architecture input
- [ ] Risk levels follow OWASP 3x3 matrix (Critical, High, Medium, Low, Note)
- [ ] SARIF output validates against SARIF 2.1.0 schema
- [ ] Attack trees generated for every Critical and High finding
