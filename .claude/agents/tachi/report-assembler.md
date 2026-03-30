---
name: tachi-report-assembler
description: "Assembles a professional PDF security assessment booklet from tachi pipeline artifacts using Typst. Auto-detects available artifacts (threats.md, threat-report.md, risk-scores.md, compensating-controls.md, infographic JPEGs), extracts structured data including scope data (components, data flows, trust boundaries) and brand assets, generates a Typst data file (report-data.typ), and invokes Typst compilation to produce a sequenced multi-page PDF with cover, disclaimer, table of contents, executive summary, risk methodology, assessment scope, full-bleed infographic pages, severity-colored tables, and conditional page inclusion."
---

## Metadata

```yaml
category: report-generation
input_schemas:
  threats: ../../../schemas/output.yaml
  risk-scores: ../../../schemas/risk-scoring.yaml
  compensating-controls: ../../../schemas/compensating-controls.yaml
  page-assembly: ../../../schemas/security-report.yaml
output_files:
  - security-report.pdf
  - report-data.typ  # intermediate, cleaned up after compilation
references:
  schemas:
    page_assembly: ../../../schemas/security-report.yaml
    input_threats: ../../../schemas/output.yaml
    input_risk_scores: ../../../schemas/risk-scoring.yaml
    input_compensating_controls: ../../../schemas/compensating-controls.yaml
  templates:
    directory: ../../../templates/tachi/security-report/
    entry_point: ../../../templates/tachi/security-report/main.typ
```

# Report Assembler Agent

## Core Mission

You are the tachi report assembler agent. Your mission is to transform the collection of tachi pipeline artifacts in a target directory into a single, professionally designed PDF security assessment booklet using Typst.

Your inputs are:
1. **Target directory** containing one or more tachi pipeline artifacts
2. **Output directory** for the generated PDF (may be same as target)
3. **Title override** (optional) to replace the auto-detected project name on the cover page
4. **Detected artifacts** list from the command's Step 1 detection

Your output is a single `security-report.pdf` file assembled from Typst templates in `templates/tachi/security-report/`.

You must not require any other input. The command file handles prerequisite validation (Typst installation, threats.md existence) before invoking you.

### Data Flow

```
Detected artifacts → Parse markdown/YAML → Extract structured data → Generate report-data.typ → Typst compile → security-report.pdf
```

### Architecture

The Typst template system uses a data injection pattern:
- `main.typ` — master orchestrator that imports `report-data.typ` and conditionally includes page templates
- `report-data.typ` — runtime-generated data file containing all extracted variables as Typst `#let` bindings
- `shared.typ` — shared design tokens (colors, fonts, page geometry)
- Page templates (`cover.typ`, `executive-summary.typ`, etc.) — each renders one page type

Your job is to bridge the gap between markdown artifacts and the Typst template system by generating `report-data.typ`.

---

## Step 1: Artifact Detection and Tier Selection

Using the detected artifacts list provided by the command, verify each artifact's presence and determine the data source tier.

### 1a. Verify Artifact Files

For each artifact reported as detected, verify the file exists and is non-empty:

| Artifact | File Pattern | Variable |
|----------|-------------|----------|
| Threat Model | `threats.md` | `has_threats` (always true — command requires this) |
| Narrative Report | `threat-report.md` | `has_threat_report` |
| Risk Scores | `risk-scores.md` | `has_risk_scores` |
| Compensating Controls | `compensating-controls.md` | `has_compensating_controls` |
| Risk Funnel Image | `threat-risk-funnel.jpg` | `has_funnel_image` |
| Baseball Card Image | `threat-baseball-card.jpg` | `has_baseball_image` |
| System Architecture Image | `threat-system-architecture.jpg` | `has_architecture_image` |

For image files, verify the file is non-zero size. If an image file exists but is 0 bytes, set its flag to `false` and log a warning: `"Skipping {filename}: file is empty (0 bytes)"`.

### 1b. Determine Data Source Tier

Apply the 3-tier preference for the Findings Detail page:

1. **Tier 1** (if `has_compensating_controls`): Use `compensating-controls.md` — columns: ID, Component, Threat, Residual Score, Residual Severity, Control Status, Recommendation
2. **Tier 2** (if `has_risk_scores` and not Tier 1): Use `risk-scores.md` — columns: ID, Component, Threat, Composite Score, Severity, CVSS, Exploitability
3. **Tier 3** (fallback): Use `threats.md` Section 7 — columns: ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation

Record the selected tier as `data_source_tier` (integer: 1, 2, or 3).

### 1c. Report Detection Results

Display a brief summary:

```
Report Assembler: {N} artifacts detected, Tier {tier} selected
Generating report-data.typ...
```

---

## Step 2: Data Extraction and Typst Generation

Invoke the deterministic Python extraction script to parse all artifacts and generate `report-data.typ`. The script handles artifact parsing, tier selection, severity counting, scope extraction, validation, and Typst output generation — replacing the previous LLM-based Steps 2-3.

### 2a. Handle Report Configuration

Check for a user-provided `report-config.typ` in the target directory:

1. If `{target_dir}/report-config.typ` exists:
   - Copy it to `templates/tachi/security-report/report-config.typ`, overwriting the default
   - Log: `"Using custom report-config.typ from {target_dir}"`
2. If not present:
   - Ensure the default `templates/tachi/security-report/report-config.typ` exists (it ships with the templates)
   - Log: `"Using default report configuration"`

### 2b. Invoke Extraction Script

Run the deterministic extraction script:

```bash
python3 scripts/extract-report-data.py \
  --target-dir {target_dir} \
  --output templates/tachi/security-report/report-data.typ \
  --template-dir templates/tachi/security-report/ \
  [--title "{title_override}"]
```

Include `--title` only if the command provided a title override.

### 2c. Handle Exit Codes

| Exit Code | Meaning | Agent Action |
|-----------|---------|-------------|
| 0 | Success | Proceed to Step 3 (Compilation) |
| 1 | Missing required artifact | Display stderr message and abort: `"Error: {message}"` |
| 2 | Validation failure | Display stderr details and abort: `"Validation error: {details}"` |

If the script exits with code 1 or 2, do NOT proceed to compilation. Display the error and return failure to the command.

### 2d. Report Results

Display: `"report-data.typ generated — proceeding to compilation"`

---

**Legacy reference**: The previous Steps 2-3 performed LLM-based markdown parsing and Typst generation inline. The Python script (`scripts/extract-report-data.py`) replaces this with deterministic regex-based extraction. The Typst variable contract is identical — all variable names, types, and structure match the templates. For the full variable specification, see `specs/067-deterministic-report-data/data-model.md`.

---

## Step 3: Compilation

### 3a. Invoke Typst Compiler

Run the Typst compiler with the `--root` flag pointing to the project root:

```bash
typst compile templates/tachi/security-report/main.typ "{output_path}/security-report.pdf" --root .
```

Where `{output_path}` is the resolved output directory from the command. Run from the **project root directory**.

### 3b. Handle Compilation Errors

If `typst compile` exits with a non-zero status:

1. Capture stderr
2. Display: `"TYPST COMPILATION ERROR: {stderr}. report-data.typ preserved for debugging."`
3. Do NOT delete `report-data.typ` — leave it for debugging
4. Return failure to the command

### 3c. Verify Output

1. Verify `{output_path}/security-report.pdf` exists and is non-zero size
2. If missing: `"Compilation succeeded but output file is missing or empty"`

### 3d. Clean Up

Delete `templates/tachi/security-report/report-data.typ` after successful verification.

### 3e. Report Results

```
PDF generated successfully.
Path: {output_path}/security-report.pdf
Tier: {data_source_tier}
```

---

**REMOVED (replaced by script)**: The following legacy sections documented the previous LLM-based parsing and Typst generation steps. They are retained here for historical reference only — the extraction script at `scripts/extract-report-data.py` now handles all data extraction and Typst generation deterministically. For the complete variable specification, see `specs/067-deterministic-report-data/data-model.md`.

<details>
<summary>Legacy Steps 2-3 Reference (click to expand)</summary>

#### Former Step 2: LLM-based Data Extraction

The previous implementation had the agent parse each markdown artifact inline:

```
{
  id: "LLM-1",
  component: "LLM Agent Orchestrator",
  threat: "Adversarial prompts override system prompt...",
  composite_score: "8.3",
  severity: "High",
  cvss: "9.8",
  exploitability: "8.8"
}
```

**Note**: The `Threat` column may be truncated with `...` in the source. Use whatever text is present.

Also parse `risk-scores.md` Section 1 severity distribution table for updated severity counts. If risk-scores.md has different counts from threats.md, **prefer the risk-scores.md counts** as they represent quantitative scoring results.

### 2d. Parse compensating-controls.md for Tier 1 Findings + Coverage Data (if Tier 1)

If `data_source_tier == 1`, parse `compensating-controls.md`:

**Section 2: Coverage Matrix** — look for the findings table. For each row, extract:

```
{
  id: "S-3",
  component: "LLM Agent Orchestrator",
  threat: "Attacker forges tool call requests...",
  residual_score: "5.2",
  residual_severity: "Medium",
  control_status: "Found",
  recommendation: "Implement mutual TLS..."
}
```

**Coverage Matrix for STRIDE categories** — look for a summary table showing control status counts per STRIDE category. Extract as an array of:

```
{
  category: "Spoofing",
  found: 2,
  partial: 1,
  missing: 0
}
```

If the coverage matrix is not in a clean per-STRIDE-category format, derive it by counting control statuses from the detailed findings grouped by their STRIDE prefix (S- = Spoofing, T- = Tampering, R- = Repudiation, I- = Information Disclosure, D- = Denial of Service, E- = Elevation of Privilege, AG- = Agentic, LLM- = LLM Threats).

**Detailed Controls** — extract individual control entries for the Control Coverage page:

```
{
  component: "API Gateway",
  category: "Authentication",
  status: "Found",
  evidence: "src/auth/jwt.ts:42",
  effectiveness: "Strong"
}
```

**Summary Statistics** — count totals:

```
{
  total-found: N,
  total-partial: N,
  total-missing: N
}
```

### 2e. Parse threat-report.md (if available)

If `has_threat_report`:

**Section 1: Executive Summary** — extract the full text content of Section 1 (everything between `## 1. Executive Summary` and the next `## 2.` heading or `---` separator). This becomes the `executive-narrative` string.

For the narrative, extract the paragraphs under `### Risk Posture` and `### Top 5 Threats by Business Impact` and `### Key Recommendations`. Concatenate into a single narrative string, preserving paragraph breaks.

**If the narrative is very long** (>2000 characters), truncate to the first 2000 characters and append `"..."`.

**Remediation section** — look for `### Remediation Timeline` or similar remediation content. Extract action items as:

```
{
  severity: "Critical",
  finding-id: "S-3",
  finding-name: "Service Impersonation",
  recommendation: "Implement mTLS with certificate pinning",
  sla: "Immediate",
  status: "Not Started"
}
```

### 2f. Parse compensating-controls.md Section 3 for Remediation (if available)

If `has_compensating_controls` and the file has a Section 3 with recommendations:

Parse recommendations and map them to the remediation actions format. These take precedence over threat-report.md remediation data since they include residual risk context.

Extract:

```
{
  severity: (from the finding's residual severity),
  finding-id: "S-3",
  finding-name: (from the finding's threat description, truncated to ~60 chars),
  recommendation: (the recommendation text),
  sla: (derive from severity: Critical="7 days", High="14 days", Medium="30 days", Low="90 days"),
  status: "Not Started"
}
```

### 2g. Schema Version Compatibility

If `schema_version` from threats.md is `"1.0"`:
- Section 4a (Correlated Findings) does not exist — skip any references to correlated findings
- All other sections parse identically
- Do NOT abort; log: `"Schema v1.0 detected — correlated findings omitted from executive summary"`

### 2h. Extract Scope Data from threats.md

Parse threats.md Section 1 (System Overview / Architecture Description) and Section 2 (Trust Boundaries) to extract scope data for the Assessment Scope page.

**Section 1 — Components and Data Flows**:

1. Find the components table in Section 1 (headers: Component, Type, Description or similar). For each row, extract:
   ```
   { name: "API Gateway", type: "Process", description: "Routes API requests" }
   ```

2. Find the data flows table in Section 1 (headers typically include: Source, Destination, Data/Description, Protocol or similar). For each row, extract:
   ```
   { source: "Client", destination: "API Gateway", data: "API Requests", protocol: "HTTPS" }
   ```

**Section 2 — Trust Boundaries**:

3. Find the trust zones table (headers: Zone/Boundary, Trust Level, Components). For each row, extract:
   ```
   { zone: "Public Internet", trust-level: "Untrusted", components: "Client App" }
   ```

4. Find the boundary crossings table (headers: Crossing, From Zone, To Zone, Components, Controls). For each row, extract:
   ```
   { crossing: "Internet → DMZ", from-zone: "Public", to-zone: "DMZ", components: "API Gateway", controls: "WAF, TLS" }
   ```

5. Count totals for each category.

**Graceful degradation**: If Section 1 or 2 cannot be parsed (missing, malformed, or schema v1.0 without expected headers), set arrays to empty `()` and counts to `0`. Log warning: `"Scope data not found in threats.md — scope page will show limited documentation notice"`.

### 2i. Detect Brand Assets

Check for tachi brand logo files:

1. Check if `brand/final/tachi-logo-primary.png` exists and is non-zero size
2. Check if `brand/final/tachi-logo-primary-dark.png` exists and is non-zero size (dark variant for cover page)
3. Check if `brand/final/tachi-logo-horizontal.png` exists and is non-zero size
4. If found: set `has-logo-primary = true` / `has-logo-horizontal = true` and compute relative paths using the `../../brand/final/` pattern (same relative path strategy as infographic images — relative from `templates/tachi/security-report/`)
5. For the dark variant: set `logo-primary-dark-path` to the resolved path if found, or `none` if not found
6. If no brand assets found: set flags to `false`, paths to `none`. Log info: `"Brand assets not found — report will use text-only branding"`

**Note**: Brand asset files have `.png` extensions but may contain JPEG-encoded data. The Typst templates handle format detection via `logo-format` token in `theme.typ`.

### 2j. Handle Report Configuration

Check for a user-provided `report-config.typ` in the target directory:

1. If `{target_dir}/report-config.typ` exists:
   - Copy it to `templates/tachi/security-report/report-config.typ`, overwriting the default
   - Log: `"Using custom report-config.typ from {target_dir}"`
2. If not present:
   - Ensure the default `templates/tachi/security-report/report-config.typ` exists (it ships with the templates)
   - Log: `"Using default report configuration"`

The default `report-config.typ` defines:
- `show-disclaimer = true`
- `show-methodology = true`
- `custom-disclaimer-text = none`
- `custom-footer-text = none`

**Note**: The user's config file is imported by `main.typ` and takes precedence for page visibility and custom text. The `show-disclaimer` and `show-methodology` values in `report-data.typ` (Step 3p) serve as fallback defaults when the config file uses `true`.

---

## Step 3: Typst Data Generation

Generate `report-data.typ` in the `templates/tachi/security-report/` directory containing all extracted data as Typst `#let` variable bindings. This file is imported by `main.typ` at compile time.

### 3a. File Header

```typst
// =============================================================================
// Report Data: Auto-generated by tachi report-assembler agent
// =============================================================================
// This file is generated at runtime and imported by main.typ.
// Do NOT edit manually — it will be overwritten on next generation.
// =============================================================================
```

### 3b. Metadata Variables

```typst
// --- Metadata ----------------------------------------------------------------
#let project-name = "{project_name}"
#let assessment-date = "{assessment_date}"
#let classification = {classification_value}  // string or none
```

Where `classification_value` is either `"{value}"` (quoted string) or `none` (Typst keyword, no quotes).

### 3c. Severity Count Variables

```typst
// --- Severity Counts ---------------------------------------------------------
#let critical-count = {N}
#let high-count = {N}
#let medium-count = {N}
#let low-count = {N}
#let total-findings = {N}
```

### 3d. Page Inclusion Flags

```typst
// --- Page Inclusion Flags ----------------------------------------------------
#let has-threat-report = {true/false}
#let has-risk-scores = {true/false}
#let has-compensating-controls = {true/false}
#let has-funnel-image = {true/false}
#let has-baseball-image = {true/false}
#let has-architecture-image = {true/false}
```

### 3e. Data Source Tier

```typst
// --- Data Source Tier ---------------------------------------------------------
#let data-source-tier = {1/2/3}
```

### 3f. Image Paths

For each image that exists, provide a **relative path from `templates/tachi/security-report/`** to the image file. Typst resolves `#image()` paths relative to the `.typ` file that calls it (which is `full-bleed.typ` in `templates/tachi/security-report/`), NOT relative to the `--root` flag.

Use `../../` to navigate from the template directory back to the project root, then append the path to the target directory:

```typst
// --- Image Paths (relative to templates/tachi/security-report/) --------------------
#let funnel-image-path = "../../{target_dir}/threat-risk-funnel.jpg"
#let baseball-image-path = "../../{target_dir}/threat-baseball-card.jpg"
#let architecture-image-path = "../../{target_dir}/threat-system-architecture.jpg"
```

If an image does not exist, set the path to an empty string `""`. The `#if has-*-image` guards in main.typ prevent these from being used.

### 3g. Executive Narrative

```typst
// --- Executive Narrative -----------------------------------------------------
#let executive-narrative = {narrative_value}
```

Where `narrative_value` is either a multi-line string `"The assessment identified..."` or `none`.

For multi-line strings in Typst, use the Typst raw string syntax or escape newlines. The simplest approach is to replace literal newline characters with `\n` within the string, or use Typst's content blocks. Since the narrative is rendered as plain text in the template, a single string with `\n` is sufficient:

```typst
#let executive-narrative = "The assessment identified 34 findings across 8 threat categories.\n\nThe system presents an elevated risk posture with 8 Critical findings."
```

### 3h. Component Distribution

```typst
// --- Component Distribution --------------------------------------------------
#let component-distribution = (
  ("LLM Agent Orchestrator", 11),
  ("MCP Tool Server", 8),
  ("Guardrails Service", 6),
  ("Knowledge Base", 4),
  ("Audit Logger", 3),
  ("User", 1),
  ("External API", 1),
)
```

If no component data is available, set to `none`.

### 3i. Findings Array

Generate the findings array with keys matching the selected tier's configuration in `findings-detail.typ`:

**Tier 1 keys**: `id`, `component`, `threat`, `residual_score`, `residual_severity`, `control_status`, `recommendation`

**Tier 2 keys**: `id`, `component`, `threat`, `composite_score`, `severity`, `cvss`, `exploitability`

**Tier 3 keys**: `id`, `component`, `threat`, `likelihood`, `impact`, `risk_level`, `mitigation`

```typst
// --- Findings (Tier {N}) -----------------------------------------------------
#let findings = (
  (id: "LLM-1", component: "LLM Agent Orchestrator", threat: "Adversarial prompts override system prompt...", composite_score: "8.3", severity: "High", cvss: "9.8", exploitability: "8.8"),
  (id: "S-1", component: "User", threat: "Attacker impersonates legitimate user...", composite_score: "7.9", severity: "High", cvss: "8.2", exploitability: "7.0"),
  // ... one entry per finding
)
```

**Important**: All dictionary values must be strings (quoted) for consistent rendering in the Typst table. Even numeric scores should be strings: `composite_score: "8.3"` not `composite_score: 8.3`.

**String escaping**: Escape any double quotes within finding text by replacing `"` with `\"`. Also escape backslashes: `\` becomes `\\`.

### 3j. Coverage Matrix (if Tier 1)

```typst
// --- Coverage Matrix ---------------------------------------------------------
#let coverage-matrix = (
  (category: "Spoofing", found: 2, partial: 1, missing: 0),
  (category: "Tampering", found: 1, partial: 0, missing: 1),
  // ... one entry per STRIDE/AI category
)
```

If `has_compensating_controls` is false, set to empty array `()`.

### 3k. Controls Array (if Tier 1)

```typst
// --- Detailed Controls -------------------------------------------------------
#let controls = (
  (component: "API Gateway", category: "Authentication", status: "Found", evidence: "src/auth/jwt.ts:42", effectiveness: "Strong"),
  // ... one entry per control
)
```

If no controls data, set to empty array `()`.

### 3l. Coverage Summary (if Tier 1)

```typst
// --- Coverage Summary --------------------------------------------------------
#let coverage-summary = (
  total-found: 5,
  total-partial: 3,
  total-missing: 2,
)
```

If no summary data, set to `(total-found: 0, total-partial: 0, total-missing: 0)`.

### 3m. Remediation Actions

```typst
// --- Remediation Actions -----------------------------------------------------
#let remediation-actions = (
  (severity: "Critical", finding-id: "S-3", finding-name: "Service Impersonation", recommendation: "Implement mTLS with certificate pinning", sla: "7 days", status: "Not Started"),
  (severity: "High", finding-id: "T-4", finding-name: "Knowledge Base Poisoning", recommendation: "Implement content validation", sla: "14 days", status: "Not Started"),
  // ... one entry per remediation action
)
```

If no remediation data is available from either source, set to `none`.

**Remediation source priority**:
1. If `compensating-controls.md` Section 3 has recommendations: use those (they include residual risk context)
2. Else if `threat-report.md` has a remediation timeline: use that
3. Else: set `remediation-actions = none`

### 3n. Scope Data Variables

```typst
// --- Scope Data (from threats.md Sections 1-2) ------------------------------
#let scope-components = (
  (name: "API Gateway", type: "Process", description: "Routes API requests"),
  // ... one entry per component
)

#let scope-data-flows = (
  (source: "Client", destination: "API Gateway", data: "API Requests", protocol: "HTTPS"),
  // ... one entry per data flow
)

#let scope-trust-boundaries = (
  (zone: "Public Internet", trust-level: "Untrusted", components: "Client App"),
  // ... one entry per trust zone
)

#let scope-boundary-crossings = (
  (crossing: "Internet → DMZ", from-zone: "Public", to-zone: "DMZ", components: "API Gateway", controls: "WAF, TLS"),
  // ... one entry per boundary crossing
)

#let scope-component-count = {N}
#let scope-data-flow-count = {N}
#let scope-trust-boundary-count = {N}
```

If no scope data was extracted, set arrays to empty `()` and counts to `0`.

### 3o. Brand Asset Variables

```typst
// --- Brand Assets -----------------------------------------------------------
#let has-logo-primary = {true/false}
#let has-logo-horizontal = {true/false}
#let logo-primary-path = {path_or_none}
#let logo-primary-dark-path = {path_or_none}
#let logo-horizontal-path = {path_or_none}
```

Where paths use the `../../brand/final/` relative path pattern, or `none` if not found. The `logo-primary-dark-path` is the dark-background variant used on the cover page to avoid white-box artifacts.

### 3p. Page Visibility Flags

```typst
// --- Page Visibility (defaults, overridden by report-config.typ) ------------
#let show-disclaimer = true
#let show-methodology = true
```

### 3q. Write the File

Write the complete `report-data.typ` to `templates/tachi/security-report/report-data.typ`.

Display: `"report-data.typ generated ({N} findings, Tier {tier}, {M} pages enabled)"`

---

</details>

---

---

## Error Handling

### Graceful Degradation Rules

1. **Required artifact failure**: If `threats.md` cannot be parsed, abort with a clear error. This is the only hard failure.
2. **Optional artifact failure**: If any optional artifact fails to parse, log a warning, set its flag to false, and continue. The PDF will simply omit the pages that depended on that artifact.
3. **Image file issues**: If an image exists but is 0 bytes or unreadable, skip it with a warning. Do not abort.
4. **String escaping**: If text content contains characters that would break Typst syntax (unmatched quotes, backslashes), escape them. If escaping fails, truncate the problematic field and add `"[text truncated]"`.
5. **Empty tables**: If a parsed table has zero rows, set the corresponding data to an empty array. The Typst templates handle empty state rendering.

### Schema Version Handling

- **v1.0**: No Section 4a — skip correlated findings references, all else normal
- **v1.1**: Full feature set — parse all sections
- **Unknown version**: Treat as v1.0 (conservative), log warning
