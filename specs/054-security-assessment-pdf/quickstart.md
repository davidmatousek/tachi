# Quickstart: Typst POC for Security Report PDF

## Prerequisites

Install Typst CLI:
```bash
# macOS
brew install typst

# Linux
cargo install typst-cli

# Windows
winget install typst
```

Verify installation:
```bash
typst --version
# Expected: typst 0.11.x or 0.12.x
```

## POC Objectives

This proof-of-concept validates three critical Typst capabilities before full template authoring:

1. **Full-bleed image rendering** — Custom page dimensions (11" x 6.1875") with zero margins
2. **Mixed orientation** — Portrait text pages and landscape image pages in a single PDF
3. **Conditional page inclusion** — Pages omitted when data/images are not available

## POC Test: Minimal Two-Page PDF

Create a minimal Typst file that produces one portrait text page and one landscape full-bleed image page:

```typst
// poc-test.typ — Validates full-bleed + mixed orientation

// Page 1: Portrait text page (US Letter)
#set page(width: 8.5in, height: 11in, margin: (top: 0.75in, bottom: 0.75in, left: 1in, right: 1in))

= Security Assessment Report
*Project*: POC Test \
*Date*: 2026-03-28 \
*Classification*: CONFIDENTIAL

#pagebreak()

// Page 2: Landscape full-bleed image (16:9)
#set page(width: 11in, height: 6.1875in, margin: 0in)

#image("threat-risk-funnel.jpg", width: 100%, height: 100%)
```

Compile:
```bash
typst compile poc-test.typ poc-test.pdf
```

## Validation Checklist

- [ ] Portrait page renders at US Letter dimensions with margins
- [ ] Landscape page renders at 16:9 custom dimensions
- [ ] Image fills entire landscape page (no borders, no letterboxing)
- [ ] Both pages coexist in a single PDF without artifacts
- [ ] Page numbering works across orientation changes

## Conditional Page Test

```typst
// poc-conditional.typ — Validates conditional page inclusion

#let has_funnel = true
#let has_baseball = false
#let has_architecture = true

#set page(width: 8.5in, height: 11in, margin: 0.75in)
= Cover Page

#if has_funnel {
  pagebreak()
  set page(width: 11in, height: 6.1875in, margin: 0in)
  [Risk Funnel Page]
}

#if has_baseball {
  pagebreak()
  set page(width: 11in, height: 6.1875in, margin: 0in)
  [Baseball Card Page — should NOT appear]
}

#if has_architecture {
  pagebreak()
  set page(width: 11in, height: 6.1875in, margin: 0in)
  [Architecture Page]
}
```

Expected: 3 pages (Cover, Risk Funnel, Architecture). Baseball Card page omitted.

## Findings

POC executed 2026-03-28:

- **Full-bleed rendering**: PASS — Custom 16:9 page (11in x 6.1875in) with zero margins renders correctly. Dark blue rectangle fills entire page edge-to-edge with centered white text overlay. No borders or letterboxing.
- **Mixed orientation**: PASS — Portrait US Letter (page 1) and landscape 16:9 (page 2) coexist in a single 2-page PDF without artifacts. `#page(...)[]` syntax switches page geometry mid-document.
- **Conditional pages**: PASS — `#if has_control_coverage` with flag=false produces 2 pages; flag=true produces 3 pages. Entire page block is excluded when condition is false.
- **Page numbering**: PASS — `counter(page).display()` tracks correctly across orientation changes (Page 1 on portrait, Page 2 on landscape).
- **Typst version tested**: 0.14.2 (via Homebrew on macOS)
- **Contingency needed**: No — all 3 critical capabilities validated successfully.

### Key Typst Patterns Discovered

1. **Page geometry switching**: Use `#page(width: ..., height: ..., margin: ...)[content]` for per-page geometry. This is a content function that wraps its body in a new page.
2. **Full-bleed backgrounds**: Use `#place(top + left, rect(width: 100%, height: 100%, fill: ...))` to fill a zero-margin page.
3. **Suppressing headers/footers**: Set `header: none, footer: none` in the `#page()` call for full-bleed pages.
4. **Conditional content**: Standard `#if condition { page(...)[...] }` blocks — excluded pages leave no trace in output.
5. **Context-aware counters**: Use `#context counter(page).display()` for page numbers (context keyword required in Typst 0.14+).
