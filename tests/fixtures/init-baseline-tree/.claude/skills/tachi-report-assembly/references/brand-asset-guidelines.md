---
source_agent: report-assembler
extracted_from: .claude/agents/tachi/report-assembler.md
version: 1.0.0
---

# Brand Asset Guidelines — Logo Detection and Resolution

Domain reference for the tachi report-assembler agent. Covers brand logo file locations, format detection, dark variant handling, path resolution for Typst, and fallback rules.

---

## Logo File Locations

Check for tachi brand logo files at these paths relative to the project root:

| Asset | Path | Purpose |
|-------|------|---------|
| Primary logo | `brand/final/tachi-logo-primary.png` | Standard logo for headers and footers |
| Primary dark variant | `brand/final/tachi-logo-primary-dark.png` | Dark-background variant for cover page |
| Horizontal logo | `brand/final/tachi-logo-horizontal.png` | Wide-format logo for horizontal layouts |

---

## Detection Procedure

For each logo file:

1. Check if the file exists at the expected path
2. Verify the file is non-zero size
3. If found and non-zero: set the corresponding flag to `true`
4. If not found or zero bytes: set the flag to `false`, path to `none`

### Flag-to-Path Mapping

| Flag | Path Variable | Source File |
|------|--------------|-------------|
| `has-logo-primary` | `logo-primary-path` | `brand/final/tachi-logo-primary.png` |
| `has-logo-primary` | `logo-primary-dark-path` | `brand/final/tachi-logo-primary-dark.png` |
| `has-logo-horizontal` | `logo-horizontal-path` | `brand/final/tachi-logo-horizontal.png` |

Note: `logo-primary-dark-path` shares the `has-logo-primary` flag. If the primary logo exists but the dark variant does not, set `logo-primary-dark-path` to `none` -- the template falls back to the standard primary logo on dark backgrounds.

---

## Path Resolution for Typst

Compute relative paths using the `../../brand/final/` pattern. This follows the same relative path strategy as infographic images -- relative from `templates/tachi/security-report/`.

### Why Relative Paths

Typst resolves `#image()` paths relative to the `.typ` file that calls it, NOT relative to the `--root` flag. Since logo images are referenced from template files in `templates/tachi/security-report/`, paths must navigate up to the project root first.

### Path Examples

```typst
#let logo-primary-path = "../../brand/final/tachi-logo-primary.png"
#let logo-primary-dark-path = "../../brand/final/tachi-logo-primary-dark.png"
#let logo-horizontal-path = "../../brand/final/tachi-logo-horizontal.png"
```

When a logo is not found, set its path to `none` (Typst keyword, not a string):

```typst
#let logo-primary-dark-path = none
```

---

## Dark Variant Handling

The dark variant (`tachi-logo-primary-dark.png`) is specifically designed for the cover page, which uses a dark background. Using the standard primary logo on a dark background can produce white-box artifacts around the logo.

### Selection Logic

```
if dark variant exists and is non-zero:
    logo-primary-dark-path = "../../brand/final/tachi-logo-primary-dark.png"
else:
    logo-primary-dark-path = none
    # Template falls back to primary logo or text-only branding
```

---

## Format Detection

Brand asset files have `.png` extensions but may contain JPEG-encoded data. The Typst templates handle format detection via the `logo-format` token in `theme.typ`. The agent does not need to detect or convert image formats -- this is a template-layer concern.

---

## Fallback Behavior

When no brand assets are found in any of the expected locations:

1. Set all flags to `false`
2. Set all paths to `none`
3. Log informational message: `"Brand assets not found — report will use text-only branding"`

The Typst templates are designed to degrade gracefully -- when logo flags are `false`, the cover page and headers render with text-only branding (project name in styled typography instead of a logo).

---

## Typst Variable Summary

Complete brand asset variable block for `report-data.typ`:

```typst
// --- Brand Assets -----------------------------------------------------------
#let has-logo-primary = {true/false}
#let has-logo-horizontal = {true/false}
#let logo-primary-path = {path_or_none}
#let logo-primary-dark-path = {path_or_none}
#let logo-horizontal-path = {path_or_none}
```

All flags are Typst booleans (unquoted). All paths are either quoted strings or `none`.
