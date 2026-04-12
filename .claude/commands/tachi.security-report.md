---
description: Generate a professional PDF security assessment booklet from tachi pipeline artifacts — auto-detects threats.md (required), threat-report.md, risk-scores.md, compensating-controls.md, and infographic JPEG images, assembles them into a sequenced multi-page PDF using Typst with branded cover, disclaimer, TOC, risk methodology, assessment scope, full-bleed infographic pages, and 3-tier data source detection
---

## User Input

```text
$ARGUMENTS
```

Consider user input before proceeding (if not empty).

## Step 0: Parse Arguments

1. If `$ARGUMENTS` contains `--output-dir <path>`:
   - Set `output_dir` to the specified path
   - Strip `--output-dir <path>` from `$ARGUMENTS` (trim extra whitespace)
2. Default: `output_dir = null` (resolved in Step 1 based on target directory)

3. If `$ARGUMENTS` contains `--title <value>`:
   - Set `title_override` to the specified value (may be quoted: `--title "Custom Project Name"`)
   - Strip `--title <value>` from `$ARGUMENTS` (trim extra whitespace)
4. Default: `title_override = null` (auto-detected from `threats.md` frontmatter in agent)

5. Remaining `$ARGUMENTS` is treated as the target directory path.
6. Default: `target_dir = current working directory`

## Overview

Single-command entry point for tachi security assessment PDF generation — the final stage in the pipeline: `/threat-model` -> `/risk-score` -> `/compensating-controls` -> `/infographic` -> `/security-report`. Auto-detects all available tachi artifacts in the target directory, determines which pages to include based on artifact availability, and produces a professional multi-page PDF booklet via Typst.

**Flow**: Parse -> Validate + Detect -> Generate -> Report

**Output**:
- `security-report.pdf` — multi-page PDF booklet with up to 8 page types, mixed portrait/landscape orientation, full-bleed infographic pages

## Step 1: Validate Prerequisites + Detect Artifacts

1. **Check Typst is installed**:
   - Run `which typst` to verify Typst CLI is available
   - If not found, display:
     ```
     TYPST NOT INSTALLED

     Typst is a modern typesetting system required for PDF generation.
     Install it for your platform:

       macOS:    brew install typst
       Linux:    cargo install typst-cli
       Windows:  winget install typst

     Then re-run /security-report.
     ```
   - Halt if not installed.

2. **Check mmdc is installed when attack trees or attack chains are present**:
   - Detect attack-tree presence: `ls "$target_dir"/attack-trees/*.md 2>/dev/null | head -n 1`. If the result is non-empty, the target project has at least one attack-tree file.
   - Detect attack-chain presence: `test -f "$target_dir/attack-chains.md"`. If the file exists, the target project has attack chain data requiring chain diagram rendering.
   - If attack trees OR attack chains are present, run `command -v mmdc >/dev/null 2>&1` to verify mmdc CLI is available.
   - If mmdc is not found, display to stderr:
     ```
     Attack path/chain rendering requires @mermaid-js/mermaid-cli (mmdc).
     Install with: npm install -g @mermaid-js/mermaid-cli
     Then re-run /tachi.security-report.
     ```
   - Halt (exit non-zero) if mmdc is not installed. Skip this check entirely when the target has no attack trees and no attack chains — projects without Mermaid-based output do not need mmdc.

3. **Auto-detect artifacts in target directory**:

   Scan `target_dir` for the following 7 artifact types:

   | Artifact | File Pattern | Required | Pages Enabled |
   |----------|-------------|----------|---------------|
   | Threat Model | `threats.md` | REQUIRED | Cover, Executive Summary, Findings Detail |
   | Narrative Report | `threat-report.md` | optional | Executive Summary (enriched), Remediation Roadmap (enriched) |
   | Risk Scores | `risk-scores.md` | optional | Findings Detail (Tier 2 scored) |
   | Compensating Controls | `compensating-controls.md` | optional | Findings Detail (Tier 1 residual), Control Coverage, Remediation Roadmap |
   | Risk Funnel Infographic | `threat-risk-funnel.jpg` | optional | Risk Funnel page (full-bleed) |
   | Baseball Card Infographic | `threat-baseball-card.jpg` | optional | Baseball Card page (full-bleed) |
   | System Architecture Infographic | `threat-system-architecture.jpg` | optional | System Architecture page (full-bleed) |
   | MAESTRO Stack Infographic | `threat-maestro-stack.jpg` | optional | MAESTRO Stack page (full-bleed) |
   | MAESTRO Heatmap Infographic | `threat-maestro-heatmap.jpg` | optional | MAESTRO Heatmap page (full-bleed) |
   | Attack Trees | `attack-trees/*.md` | optional | Attack Path pages (portrait) |
   | Attack Chains | `attack-chains.md` | optional | Attack Chain pages (portrait, Feature 141) |
   | Brand Assets | `brand/final/tachi-logo-*.png` | optional | Cover (branded), Headers (branded) |

3. **Require `threats.md` minimum**:
   - If `threats.md` is not found in `target_dir`, display:
     ```
     REQUIRED ARTIFACT NOT FOUND: threats.md

     The /security-report command requires threats.md as the minimum input artifact.
     Run /threat-model first to generate a threat model.

     Expected at: {target_dir}/threats.md
     ```
   - Halt if missing.

4. **Determine data source tier for Findings Detail**:
   - If `compensating-controls.md` found: **Tier 1** — residual risk columns (ID, Component, Threat, Residual Score, Residual Severity, Control Status, Recommendation)
   - Else if `risk-scores.md` found: **Tier 2** — quantitative columns (ID, Component, Threat, Composite Score, Severity, CVSS, Exploitability)
   - Else: **Tier 3** — qualitative columns from `threats.md` (ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation)

5. **Resolve output directory**:
   - If `--output-dir` was specified in Step 0: use that path
   - Otherwise: use `target_dir`
   - Create output directory if it does not exist

6. **Report detected artifacts and pages to be generated**:

   Display detection summary:
   ```
   ARTIFACT DETECTION RESULTS
   Target: {target_dir}
   Output: {output_dir}
   {if title_override: "Title: {title_override}"}

   Artifacts detected:
     threats.md .................. FOUND (required)
     threat-report.md ........... {FOUND | not found}
     risk-scores.md ............. {FOUND | not found}
     compensating-controls.md ... {FOUND | not found}
     threat-risk-funnel.jpg ..... {FOUND | not found}
     threat-baseball-card.jpg ... {FOUND | not found}
     threat-system-architecture.jpg {FOUND | not found}
     threat-maestro-stack.jpg ... {FOUND | not found}
     threat-maestro-heatmap.jpg . {FOUND | not found}
     attack-trees/ ................. {FOUND (N files) | not found}
     attack-chains.md .............. {FOUND | not found}
     brand/final/*.png .............. {FOUND (N files) | not found}

   Data source tier: {Tier 1 — residual risk | Tier 2 — quantitative | Tier 3 — qualitative}
   {if threats.md has baseline.source != null: "Baseline: {source} ({date}) — delta counts will appear in report"}

   Pages to generate:
     1. Cover ..................... portrait (US Letter)
     2. Disclaimer ............... portrait (US Letter)
     3. Table of Contents ........ portrait (US Letter)
     4. Risk Methodology ......... portrait (US Letter)
     5. Assessment Scope ......... portrait (US Letter)
     6. Executive Summary ......... portrait (US Letter)
     {if attack-trees found: "N. Attack Path Analysis ...... portrait (US Letter)"}
     {if attack-chains found: "N. Attack Chain Analysis ..... portrait (US Letter)"}
     {if risk-funnel found:  "N. Risk Funnel .............. landscape (full-bleed 16:9)"}
     {if baseball-card found: "N. Baseball Card ............ landscape (full-bleed 16:9)"}
     {if architecture found:  "N. System Architecture ...... landscape (full-bleed 16:9)"}
     N. Findings Detail .......... portrait (US Letter) — {tier label}
     {if compensating-controls found: "N. Control Coverage ......... portrait (US Letter)"}
     {if compensating-controls OR threat-report found: "N. Remediation Roadmap ...... portrait (US Letter)"}

   Total pages: {count}
   ```

   Where page numbers (N) are assigned dynamically based on which pages are included.

## Step 2: Generate Report

Invoke the report-assembler agent to parse artifacts, generate Typst data, and compile the PDF.

1. **Invoke agent**: Use the Agent tool with `subagent_type: "senior-backend-engineer"` and the following prompt:

   ```
   You are the tachi report-assembler agent. Read your full instructions at `.claude/agents/tachi/report-assembler.md` and execute all 4 steps.

   Inputs:
   - Target directory: {target_dir}
   - Output directory: {output_dir}
   - Title override: {title_override or "none"}
   - Detected artifacts: {list of FOUND artifacts from Step 1}
   - Data source tier: {tier from Step 1}

   Execute Steps 1-4 of the agent instructions:
   1. Verify artifacts and confirm tier selection
   2. Extract structured data from all detected markdown artifacts (the extraction script
      now detects baseline data from threats.md frontmatter and includes delta variables:
      has-baseline, delta counts, and resolved-findings in report-data.typ)
   3. Generate report-data.typ with all Typst variable bindings
   4. Compile main.typ to security-report.pdf using typst compile

   Note: When baseline data is present in threats.md, the extraction script automatically
   includes delta-aware variables (has-baseline, baseline-source, delta-*-count,
   resolved-findings). Typst templates that support delta will render resolved findings
   in a separate section and annotate NEW findings.

   Return: PDF path, page count, tier used, and any warnings.
   ```

2. **Handle agent result**:
   - If agent reports success: proceed to Step 3
   - If agent reports compilation error: display the error and halt
   - If agent reports missing required artifact: display the error and halt

## Step 3: Report Results

Display the generation results to the user.

1. **Success report**:

   ```
   SECURITY REPORT GENERATED

   PDF: {output_dir}/security-report.pdf
   Pages: {page_count} ({page_type_list})
   Data tier: Tier {N} — {tier_label}
   Artifacts used: {count}/{total_detected}

   Page sequence:
     1. Cover ..................... portrait
     2. Disclaimer ............... portrait
     3. Table of Contents ........ portrait
     4. Risk Methodology ......... portrait
     5. Assessment Scope ......... portrait
     6. Executive Summary ......... portrait
     {conditional pages with dynamic numbering}
     N. Findings Detail .......... portrait ({tier_label})
     {conditional pages}

   {if any warnings from agent: display them here}
   ```

   Where `tier_label` is:
   - Tier 1: "Residual Risk (compensating-controls.md)"
   - Tier 2: "Inherent Risk (risk-scores.md)"
   - Tier 3: "Severity (threats.md)"

2. **Page type list** — comma-separated list of included page types:
   - Always: "cover, disclaimer, toc, methodology, scope, executive-summary, findings-detail"
   - Conditional: "risk-funnel", "baseball-card", "system-architecture", "control-coverage", "remediation-roadmap"

3. **Next steps suggestion**:

   ```
   Next steps:
   - Open the PDF to review: open {output_dir}/security-report.pdf
   - Regenerate with different options: /security-report --title "Custom Title" --output-dir path/
   ```

## Usage Examples

```bash
# Auto-detect artifacts in current directory
/security-report

# Specify target directory containing artifacts
/security-report path/to/threat-model-output/

# Custom output directory
/security-report --output-dir reports/pdf/

# Custom title on cover page
/security-report --title "Q1 2026 Security Assessment"

# Combine all options
/security-report path/to/artifacts/ --output-dir reports/ --title "Project Alpha Security Review"
```

## Quality Checklist

- [ ] Typst installation check triggers clear error with platform-specific instructions
- [ ] All 7 artifact types detected correctly when present
- [ ] Missing `threats.md` triggers clear error with path and remediation guidance
- [ ] Data source tier correctly determined (compensating-controls > risk-scores > threats)
- [ ] Artifact detection table displays accurately (FOUND / not found)
- [ ] Page list dynamically adjusts based on detected artifacts
- [ ] `--output-dir` flag correctly overrides output location
- [ ] `--title` flag correctly sets title override
- [ ] Default target directory is current working directory
- [ ] Default output directory matches target directory
- [ ] Idempotent: re-running produces identical output
