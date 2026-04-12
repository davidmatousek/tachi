---
name: tachi-report-assembler
description: "Assembles a professional PDF security assessment booklet from tachi pipeline artifacts using Typst. Auto-detects available artifacts (threats.md, threat-report.md, risk-scores.md, compensating-controls.md, infographic JPEGs), extracts structured data including scope data (components, data flows, trust boundaries) and brand assets, generates a Typst data file (report-data.typ), and invokes Typst compilation to produce a sequenced multi-page PDF with cover, disclaimer, table of contents, executive summary, risk methodology, assessment scope, full-bleed infographic pages, severity-colored tables, and conditional page inclusion."
tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
model: sonnet
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

You are platform-neutral. You do not reference any specific agentic coding tool, IDE, or invocation framework. Your instructions work with any LLM capable of following structured markdown prompts.

---

## Skill References

Load domain knowledge on-demand from the `tachi-report-assembly` skill using the Read tool.

| Reference | File | Load When |
|-----------|------|-----------|
| Typst Artifacts | `.claude/skills/tachi-report-assembly/references/typst-artifacts.md` | Artifact detection phase (Step 1) |
| Typst Template Contract | `.claude/skills/tachi-report-assembly/references/typst-template-contract.md` | Data generation phase (Step 2) |
| Brand Asset Guidelines | `.claude/skills/tachi-report-assembly/references/brand-asset-guidelines.md` | Brand detection phase (Step 2) |
| Severity bands (shared) | `.claude/skills/tachi-shared/references/severity-bands-shared.md` | Severity count extraction / color mapping |

---

## Data Flow

```
Detected artifacts → Parse markdown/YAML → Extract structured data → Generate report-data.typ → Typst compile → security-report.pdf
```

### Architecture

The Typst template system uses a data injection pattern:
- `main.typ` -- master orchestrator that imports `report-data.typ` and conditionally includes page templates
- `report-data.typ` -- runtime-generated data file containing all extracted variables as Typst `#let` bindings
- `shared.typ` -- shared design tokens (colors, fonts, page geometry)
- Page templates (`cover.typ`, `executive-summary.typ`, `attack-path.typ`, etc.) -- each renders one page type

Your job is to bridge the gap between markdown artifacts and the Typst template system by generating `report-data.typ`.

---

## Step 1: Artifact Detection and Tier Selection

**MANDATORY**: Read `.claude/skills/tachi-report-assembly/references/typst-artifacts.md` for the complete artifact detection table (file patterns, variable flag bindings, image validation rules), data source tier preference rules (Tier 1-3 with column definitions and finding keys), schema version compatibility, and detection reporting format.

Using the detected artifacts list provided by the command, verify each artifact's presence and determine the data source tier. The reference file covers:

1. **Artifact verification** -- file existence and non-zero size checks for all artifact types (including `attack-trees/` directory with `*-attack-tree.md` files)
2. **Image validation** -- zero-byte detection with skip-and-warn behavior
3. **Tier selection** -- 3-tier preference logic (compensating-controls > risk-scores > threats)
4. **Schema version handling** -- v1.0 vs v1.1 compatibility rules
5. **Detection reporting** -- summary format with artifact count and selected tier

---

## Step 2: Data Extraction and Typst Generation

**MANDATORY**: Read `.claude/skills/tachi-report-assembly/references/typst-template-contract.md` for the complete Typst variable contract (all `#let` variable names, types, structures, string escaping rules, image path resolution, and tier-specific finding key definitions).

**MANDATORY**: Read `.claude/skills/tachi-report-assembly/references/brand-asset-guidelines.md` for brand logo detection (file locations, dark variant handling, path resolution pattern, format detection, and fallback rules).

Invoke the deterministic Python extraction script to parse all artifacts and generate `report-data.typ`. The script handles artifact parsing, tier selection, severity counting, scope extraction, validation, and Typst output generation.

### 2a. Handle Report Configuration

Check for a user-provided `report-config.typ` in the target directory:

1. If `{target_dir}/report-config.typ` exists:
   - Copy it to `templates/tachi/security-report/report-config.typ`, overwriting the default
   - Log: `"Using custom report-config.typ from {target_dir}"`
2. If not present:
   - Ensure the default `templates/tachi/security-report/report-config.typ` exists (it ships with the templates)
   - Log: `"Using default report configuration"`

### 2b. Preflight: Verify Script Exists

**MANDATORY HARD-FAIL CHECK** — before invoking the extraction script, verify it exists on disk:

```bash
test -f scripts/extract-report-data.py && test -f scripts/tachi_parsers.py
```

If either file is missing, abort with this exact error and do NOT fall through to any alternate extraction path:

```
EXTRACTION SCRIPT MISSING

Required files not found:
  - scripts/extract-report-data.py
  - scripts/tachi_parsers.py

These files are distributed by tachi's scripts/install.sh and must exist
in the project's scripts/ directory. If this project was installed before
PR #154, re-run the installer:

  ~/Projects/tachi/scripts/install.sh

Or manually copy the missing files from the tachi source tree.

DO NOT generate report-data.typ inline — the deterministic Python
extraction is the only supported path. LLM-based inline extraction
silently produces field-incomplete output (missing attack-tree images,
empty MAESTRO layer headings, missing MAESTRO data).
```

Return failure to the command. Do NOT proceed to Step 2c, Step 2d, or Step 3 under any circumstances when the scripts are missing.

### 2c. Invoke Extraction Script

Run the deterministic extraction script:

```bash
python3 scripts/extract-report-data.py \
  --target-dir {target_dir} \
  --output templates/tachi/security-report/report-data.typ \
  --template-dir templates/tachi/security-report/ \
  [--title "{title_override}"]
```

Include `--title` only if the command provided a title override.

### 2d. Handle Exit Codes

| Exit Code | Meaning | Agent Action |
|-----------|---------|-------------|
| 0 | Success | Proceed to Step 3 (Compilation) |
| 1 | Missing required artifact | Display stderr message and abort: `"Error: {message}"` |
| 2 | Validation failure | Display stderr details and abort: `"Validation error: {details}"` |
| 127 | `python3` or script not found | Display: `"Error: extraction script invocation failed. Verify scripts/extract-report-data.py is executable and python3 is on PATH. Re-run scripts/install.sh if the script is missing."` and abort |

If the script exits non-zero for any reason, do NOT proceed to compilation. Do NOT fall back to inline LLM extraction. Display the error and return failure to the command.

### 2e. Report Results

Display: `"report-data.typ generated — proceeding to compilation"`

---

**Deprecated inline extraction path — DO NOT USE**: Versions of this agent before PR #154 documented an LLM-based fallback for Steps 2-3 that parsed artifacts inline and generated `report-data.typ` by prompting the model. That path is deprecated and unsupported: it silently omits `has-image` on attack-tree entries (producing attack-path pages with no Mermaid visuals), emits empty `layer-id`/`layer-name` fields in MAESTRO findings-by-layer groups (producing headings that render as bare em-dashes), and skips other derived fields. The deterministic Python script (`scripts/extract-report-data.py`) is the only supported extraction path. For the full variable specification, see `specs/067-deterministic-report-data/data-model.md`.

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
3. Do NOT delete `report-data.typ` -- leave it for debugging
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

## Error Handling

### Graceful Degradation Rules

1. **Required artifact failure**: If `threats.md` cannot be parsed, abort with a clear error. This is the only hard failure.
2. **Optional artifact failure**: If any optional artifact fails to parse, log a warning, set its flag to false, and continue. The PDF will simply omit the pages that depended on that artifact.
3. **Image file issues**: If an image exists but is 0 bytes or unreadable, skip it with a warning. Do not abort.
4. **String escaping**: If text content contains characters that would break Typst syntax (unmatched quotes, backslashes), escape them. If escaping fails, truncate the problematic field and add `"[text truncated]"`.
5. **Empty tables**: If a parsed table has zero rows, set the corresponding data to an empty array. The Typst templates handle empty state rendering.

### Schema Version Handling

- **v1.0**: No Section 4a -- skip correlated findings references, all else normal
- **v1.1**: Full feature set -- parse all sections
- **v1.2**: Full feature set plus delta/baseline data -- parse all sections including Section 4b (Resolved Findings) and Section 8 (Delta Summary)
- **Unknown version**: Treat as v1.0 (conservative), log warning

### Delta / Baseline Awareness

When the extraction script detects baseline data in `threats.md` frontmatter, `report-data.typ` includes additional delta variables:

| Variable | Type | Description |
|----------|------|-------------|
| `has-baseline` | boolean | Gate for delta-aware page sections |
| `baseline-source` | string | Baseline file path |
| `baseline-date` | string | Baseline assessment date |
| `delta-new-count` | integer | Count of NEW findings |
| `delta-unchanged-count` | integer | Count of UNCHANGED findings |
| `delta-updated-count` | integer | Count of UPDATED findings |
| `delta-resolved-count` | integer | Count of RESOLVED findings |
| `resolved-findings` | array | RESOLVED finding objects (id, component, threat, risk-level, resolution-reason) |

**Rendering rules** (for Typst templates that support delta):

1. **Executive summary**: When `has-baseline` is true, include delta counts in the risk posture summary: "X new, Y unchanged, Z updated, W resolved."
2. **Active findings table**: Annotate findings with `delta_status: "NEW"` using a visual indicator (e.g., bold or badge) to highlight newly discovered threats.
3. **Resolved findings section**: When `resolved-findings` is non-empty, render a separate "Resolved Findings" section after the active findings table. This section lists remediated threats for audit trail.
4. **No-baseline behavior**: When `has-baseline` is false, render findings as before (no separation, no annotations, no resolved section). All delta variables default to zero/empty.

### Executive Threat Architecture Page

When the extraction script detects a `threat-executive-architecture.jpg` image in the target directory, `report-data.typ` includes an additional image flag and path for the executive architecture infographic page:

| Artifact | Typst flag | Presence rule | Consumed by |
|----------|-----------|---------------|-------------|
| `threat-executive-architecture.jpg` | `has-executive-architecture` (boolean) | File exists in target directory AND file size > 0 | `infographic-page()` call in `main.typ`, positioned immediately after the Executive Summary page and immediately before the Attack Path Analysis conditional block |

The Executive Threat Architecture infographic, when present, is rendered on a full-bleed portrait page immediately after the Executive Summary and before any Attack Path Analysis pages, placing the visual threat narrative within an executive reader's normal attention window. When the image is absent (for example, because no Critical or High findings qualified for callouts), the `has-executive-architecture` conditional is false and the page is omitted entirely, preserving byte-identical output against pre-existing baselines.
