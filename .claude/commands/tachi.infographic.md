---
description: Generate visual threat infographic specifications and images from threat model output — supports three-tier auto-detection of richest data source (compensating-controls.md > risk-scores.md > threats.md), explicit file override, and template selection
---

## User Input

```text
$ARGUMENTS
```

Consider user input before proceeding (if not empty).

## Step 0: Parse Arguments

1. If `$ARGUMENTS` contains `--template <value>`:
   - Set `template` to the specified value
   - Valid values: `baseball-card`, `system-architecture`, `risk-funnel`, `maestro-stack`, `maestro-heatmap`, `executive-architecture`, `all`, `maestro`, `corporate-white`, `exec`
   - If value is `corporate-white`: resolve alias to `baseball-card`
   - If value is `exec`: resolve alias to `executive-architecture`
   - If value is `maestro`: expand shorthand to `["maestro-stack", "maestro-heatmap"]` — generate both sequentially
   - If value is not in the valid list, display:
     ```
     INVALID TEMPLATE: {value}
     Valid templates: baseball-card, system-architecture, risk-funnel, maestro-stack, maestro-heatmap, executive-architecture, all, maestro
     Aliases: corporate-white → baseball-card, exec → executive-architecture, maestro → maestro-stack + maestro-heatmap
     ```
   - Halt if invalid.
   - Strip `--template <value>` from `$ARGUMENTS` (trim extra whitespace)
2. Default: `template = "all"`

3. If `$ARGUMENTS` contains `--output-dir <path>`:
   - Set `output_dir` to the specified path
   - Strip `--output-dir <path>` from `$ARGUMENTS` (trim extra whitespace)
4. Default: `output_dir = null` (resolved in Step 1 based on data source location)

5. Remaining `$ARGUMENTS` is treated as the explicit data source path.
6. Default: `data_source_path = null` (auto-detect in Step 1)

## Overview

Single-command entry point for tachi threat infographic generation — the visual layer in the pipeline: `/threat-model` -> `/risk-score` -> `/infographic`. Auto-detects the richest available data source, invokes the infographic agent in a fresh context, and produces specification files with optional Gemini-generated images.

**Flow**: Parse -> Validate -> Generate -> Report

**Output suite** (per template):
- `threat-{template-name}-spec.md` — structured infographic specification (6 sections per `schemas/infographic.yaml`)
- `threat-{template-name}.jpg` — presentation-ready image (only when GEMINI_API_KEY available and API succeeds)

## Step 1: Validate Prerequisites

1. **Check infographic agent is installed**:
   - Verify `.claude/agents/tachi/threat-infographic.md` exists
   - If missing, display:
     ```
     TACHI INFOGRAPHIC AGENT NOT INSTALLED
     Run: cp -r <tachi-repo>/adapters/claude-code/agents/threat-infographic.md .claude/agents/tachi/
     See: https://github.com/davidmatousek/tachi
     ```
   - Halt if missing.

2. **Detect data source**:

   **If explicit `data_source_path` was provided** (from Step 0):
   - Verify the file exists at the provided path
   - If not found, display:
     ```
     DATA SOURCE NOT FOUND: {data_source_path}
     Provide a valid path to a compensating-controls.md, risk-scores.md, or threats.md file.
     ```
   - Halt if not found.
   - Read the file content and detect type from structure:
     - Contains `## 2. Coverage Matrix` AND the first table beneath it has a `Residual Score` column -> type is `compensating-controls`
     - Contains `## 2. Scored Threat Table` AND the first table beneath it has a `Composite` column header -> type is `risk-scores`
     - Contains `## 6. Risk Summary` with severity count labels (Critical, High, Medium, Low) -> type is `threats`
     - No indicator found -> display:
       ```
       UNABLE TO DETECT DATA SOURCE TYPE: {data_source_path}
       Expected compensating-controls.md (Section 2: Coverage Matrix with Residual Score column)
       or risk-scores.md (Section 2: Scored Threat Table with Composite column)
       or threats.md (Section 6: Risk Summary with severity counts).
       ```
     - Halt if undetectable.
   - Set `primary_file` to the provided path
   - Set `data_source_dir` to the directory containing the file

   **If no explicit path** (auto-detect):
   - Scan current working directory for `compensating-controls.md`
     - If found: set `primary_file = compensating-controls.md`, type is `compensating-controls`
   - If `compensating-controls.md` not found, scan for `risk-scores.md`
     - If found: set `primary_file = risk-scores.md`, type is `risk-scores`
   - If `risk-scores.md` not found, scan for `threats.md`
     - If found: set `primary_file = threats.md`, type is `threats`
   - If none found, display:
     ```
     NO DATA SOURCE FILES FOUND
     Expected one of:
       - compensating-controls.md (preferred — residual risk after control analysis)
       - risk-scores.md (quantitative composite scores)
       - threats.md (fallback — qualitative severity counts)
     Run /threat-model first to generate threat model output.
     Then optionally: /risk-score → /compensating-controls for richer data.
     ```
   - Halt if none found.
   - Set `data_source_dir` to current working directory

3. **Co-located threats.md check** (when type is `risk-scores` or `compensating-controls`):
   - Verify `threats.md` exists in `data_source_dir`
   - If missing, display:
     ```
     CO-LOCATED threats.md NOT FOUND
     When using risk-scores.md or compensating-controls.md as primary data source,
     a co-located threats.md is required in the same directory for structural data
     (project metadata, trust zones, data flows).
     Expected at: {data_source_dir}/threats.md
     ```
   - Halt if missing.
   - Set `secondary_file` to `{data_source_dir}/threats.md`
   - Note: `risk-scores.md` is NOT required when `compensating-controls.md` is primary.

4. **Resolve output directory**:
   - If `--output-dir` was specified in Step 0: use that path
   - Otherwise: use `data_source_dir`
   - Create output directory if it does not exist

5. **Display detection summary**:
   ```
   Data source: {primary_file} ({type_label})
   {if type is risk-scores or compensating-controls: "Co-located: {secondary_file}"}
   Template: {template}
   Output: {output_dir}
   ```

   Where `{type_label}` is:
   - when type is `compensating-controls`: `residual risk (compensating-controls.md)`
   - when type is `risk-scores`: `quantitative (risk-scores.md)`
   - when type is `threats`: `qualitative (threats.md)`

## Step 2: Run Infographic Agent

1. Invoke the `tachi-threat-infographic` agent with the following prompt:

   ```
   Generate threat infographic specification(s) using the deterministic extraction script.

   CRITICAL: You MUST run the extraction script for data extraction. Do NOT parse
   markdown files manually or extract severity counts via LLM. The script ensures
   cross-output consistency with the security report (Feature 067/071).

   Target directory: {data_source_dir}
   Template: {template}
   Write all output files to: {output_dir}

   Output files per template:
   - threat-{template-name}-spec.md (always)
   - threat-{template-name}.jpg (when GEMINI_API_KEY available)

   Step 1: Run the extraction script (once per template, or 3x if template is "all", or 2x if template is "maestro"):
     python3 scripts/extract-infographic-data.py \
       --target-dir {data_source_dir} \
       --template {template_name} \
       --output /tmp/infographic-{template_name}.json

   Template expansion:
   - "all" expands to: baseball-card, system-architecture, risk-funnel, executive-architecture. Then check if data source contains MAESTRO layer data (grep for "MAESTRO Layer" or "maestro_layer" in the data source file) — if present, also append maestro-stack and maestro-heatmap (up to 6 runs total).
   - "maestro" expands to: maestro-stack, maestro-heatmap (2 runs, sequential)
   - "exec" resolves to: executive-architecture (alias, 1 run)
   - Individual templates (baseball-card, system-architecture, risk-funnel, maestro-stack, maestro-heatmap, executive-architecture): 1 run

   Step 2: Read the JSON output and generate the spec file per your methodology.
     - If the JSON contains a "delta" object (has_baseline: true), include delta context
       in the spec: note delta_counts (new/unchanged/updated/resolved), emphasize NEW
       findings in visual design, and note that severity distribution reflects active
       findings only (RESOLVED excluded). Pass delta emphasis directives to Gemini prompts
       when constructing image generation requests.
   Step 3: Generate images via Gemini if GEMINI_API_KEY is available.
   ```

2. Do NOT read or pass data source file contents to the agent. The agent reads
   files via the extraction script, which ensures deterministic, validated output.

3. Wait for the infographic agent to complete specification generation and image generation attempt.

## Step 3: Report Results

Display completion summary:

```
INFOGRAPHIC GENERATION COMPLETE
Data source: {primary_file}
Data source type: {type_label}
Output: {output_dir}

Templates generated:
{for each template generated:}
  {template_name}:
    Spec: {output_dir}/threat-{template-name}-spec.md
    Image: {output_dir}/threat-{template-name}.jpg — {image_status}
{end for}

{if type is "threats" AND no explicit data_source_path:}
💡 Tip: Run /risk-score to add quantitative risk scores to your infographic.
{end if}

{if type is "risk-scores" AND no explicit data_source_path:}
💡 Tip: Run /compensating-controls to visualize residual risk (actual exposure after defenses).
{end if}

{if type is "compensating-controls" AND no explicit data_source_path:}
✅ Full pipeline — visualizing residual risk (richest data available).
Run /security-report to generate the PDF assessment booklet (auto-includes infographic images).
{end if}
```

**Tip suppression**: When an explicit `data_source_path` was provided (from Step 0), skip enhancement tip display entirely. Rationale: explicit path = intentional choice, no second-guessing.

Where:
- `{type_label}` is `residual risk (compensating-controls.md)` when type is `compensating-controls`, `quantitative (risk-scores.md)` when type is `risk-scores`, or `qualitative (threats.md)` when type is `threats`
- `{image_status}` is one of:
  - `generated` — Gemini API call succeeded, image file written
  - `skipped (no GEMINI_API_KEY)` — environment variable not set
  - `skipped (API error)` — Gemini API returned an error
  - `skipped (rate limited)` — Gemini API returned 429
  - `skipped (content policy)` — Gemini rejected the prompt
  - `skipped (timeout)` — Gemini API call exceeded 60s timeout

## Usage Examples

```bash
# Auto-detect data source in current directory (uses richest available)
/infographic

# Use a specific file
/infographic path/to/risk-scores.md
/infographic path/to/threats.md

# Select a specific template
/infographic --template baseball-card
/infographic --template system-architecture

# Executive architecture template (Feature 128 — placed after Executive Summary in PDF)
/infographic --template executive-architecture
/infographic --template exec              # alias: resolves to executive-architecture

# MAESTRO templates (require MAESTRO layer data from Feature 084)
/infographic --template maestro-stack
/infographic --template maestro-heatmap
/infographic --template maestro          # shorthand: generates both maestro-stack + maestro-heatmap

# Custom output directory
/infographic --output-dir reports/infographics/

# Combine options
/infographic path/to/risk-scores.md --template baseball-card --output-dir reports/
```

## Quality Checklist

- [ ] Data source detection correct (compensating-controls.md > risk-scores.md > threats.md)
- [ ] Risk distribution counts match source file exactly (zero discrepancy)
- [ ] All requested templates generated (per --template flag)
- [ ] Spec files written to output directory
- [ ] Gemini image generation attempted if GEMINI_API_KEY available
- [ ] Error messages clear for: no files found, explicit path missing, co-located threats.md missing
- [ ] corporate-white alias resolves to baseball-card
- [ ] Idempotent: re-running overwrites previous output
