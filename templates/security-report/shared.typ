// =============================================================================
// Shared Styles: Security Assessment PDF Booklet
// =============================================================================
// Single source of truth for design consistency across all page templates.
// Every other .typ file in this directory should import this module:
//
//   #import "shared.typ": *
//
// Exports:
//   Colors    — severity-critical, severity-high, severity-medium, severity-low
//   Functions — severity-color(level), report-header(..),  report-footer()
//   Rules     — apply-page-setup(), apply-typography()
// =============================================================================


// ---------------------------------------------------------------------------
// 1. Severity Color Constants
// ---------------------------------------------------------------------------
// Canonical severity palette used across cover page finding counts, findings
// detail table cells, executive summary metrics, and remediation roadmap
// priority indicators.

/// Critical severity — red.
#let severity-critical = rgb("#DC2626")

/// High severity — orange.
#let severity-high = rgb("#F97316")

/// Medium severity — yellow.
#let severity-medium = rgb("#EAB308")

/// Low severity — blue.
#let severity-low = rgb("#4169E1")

// Neutral tones for structural elements (headers, rules, backgrounds).
#let color-header-bg = rgb("#1E293B")
#let color-header-text = white
#let color-classification-bg = rgb("#991B1B")
#let color-classification-text = white
#let color-footer-text = rgb("#64748B")
#let color-rule = rgb("#CBD5E1")


// ---------------------------------------------------------------------------
// 2. Severity-to-Color Mapping Function
// ---------------------------------------------------------------------------
// Takes a severity string and returns the matching color constant.
// Case-insensitive comparison. Returns gray for unrecognized values.
//
// Usage:
//   #let fill = severity-color("Critical")  // => rgb("#DC2626")
//   #table.cell(fill: severity-color(row.severity))[...]

#let severity-color(level) = {
  let normalized = lower(level)
  if normalized == "critical" { severity-critical }
  else if normalized == "high" { severity-high }
  else if normalized == "medium" { severity-medium }
  else if normalized == "low" { severity-low }
  else { rgb("#9CA3AF") }
}


// ---------------------------------------------------------------------------
// 3. Typography Rules
// ---------------------------------------------------------------------------
// Sans-serif for headings, serif for body, monospace for table data.
// Uses Typst built-in font families so no custom font files are required.
//
// Usage — call once at the top of main.typ after importing shared.typ:
//   #show: apply-typography

// Fallback chains: Typst tries each font in order and uses the first one
// found. "New Computer Modern" is bundled with Typst and always available.
// macOS provides Helvetica Neue, Menlo, etc. Linux/Windows fall through to
// the Typst-bundled or system defaults at the end of each chain.
#let font-heading = ("Helvetica Neue", "Helvetica", "Arial", "New Computer Modern")
#let font-body = ("New Computer Modern", "Charter", "Georgia", "Times New Roman")
#let font-mono = ("Menlo", "Courier New", "Courier")

#let apply-typography(body) = {
  // Base: serif body text at 11pt.
  set text(font: font-body, size: 11pt)

  // Headings: sans-serif, heavier weight.
  show heading.where(level: 1): set text(font: font-heading, size: 18pt, weight: "bold")
  show heading.where(level: 2): set text(font: font-heading, size: 14pt, weight: "bold")
  show heading.where(level: 3): set text(font: font-heading, size: 12pt, weight: "semibold")

  // Heading spacing.
  show heading.where(level: 1): it => { v(0.3in); it; v(0.15in) }
  show heading.where(level: 2): it => { v(0.2in); it; v(0.1in) }
  show heading.where(level: 3): it => { v(0.15in); it; v(0.08in) }

  // Raw/code text: monospace.
  show raw: set text(font: font-mono, size: 9pt)

  body
}


// ---------------------------------------------------------------------------
// 4. US Letter Page Setup
// ---------------------------------------------------------------------------
// Standard portrait page geometry for all text pages.
// Full-bleed pages (infographics) override this per-page in full-bleed.typ.
//
// Usage — call once at the top of main.typ after apply-typography:
//   #show: apply-page-setup

#let page-width = 8.5in
#let page-height = 11in
#let margin-top = 0.75in
#let margin-bottom = 0.75in
#let margin-left = 1in
#let margin-right = 1in

#let apply-page-setup(body) = {
  set page(
    width: page-width,
    height: page-height,
    margin: (
      top: margin-top,
      bottom: margin-bottom,
      left: margin-left,
      right: margin-right,
    ),
  )

  body
}


// ---------------------------------------------------------------------------
// 5. Header Function
// ---------------------------------------------------------------------------
// Renders at the top of each text page. Two optional elements:
//   - classification: if not none, displays a centered colored bar with the
//     classification marking (e.g., "CONFIDENTIAL").
//   - title: page title rendered left-aligned below the classification bar.
//
// Usage in a page's header parameter:
//   header: report-header(classification: "CONFIDENTIAL", title: "Executive Summary")
//   header: report-header(title: "Findings Detail")
//   header: report-header()

#let report-header(classification: none, title: none) = {
  // Classification marking bar.
  if classification != none {
    block(
      width: 100%,
      inset: (x: 0.3em, y: 0.25em),
      fill: color-classification-bg,
      align(center,
        text(
          fill: color-classification-text,
          size: 8pt,
          weight: "bold",
          tracking: 0.1em,
          upper(classification),
        ),
      ),
    )
    v(0.15in)
  }

  // Page title.
  if title != none {
    text(
      font: font-heading,
      size: 9pt,
      fill: color-header-bg,
      weight: "semibold",
      title,
    )
    v(0.05in)
    line(length: 100%, stroke: 0.5pt + color-rule)
  }
}


// ---------------------------------------------------------------------------
// 6. Footer Function
// ---------------------------------------------------------------------------
// Renders at the bottom of each text page:
//   - Left: (empty, reserved for future use)
//   - Center: "Page X" with dynamic page counter
//   - Right: "Generated by tachi"
//
// Must be placed inside a `context` block for page counter access.
//
// Usage in a page's footer parameter:
//   footer: report-footer()

#let report-footer() = {
  line(length: 100%, stroke: 0.5pt + color-rule)
  v(0.05in)
  context {
    let page-num = counter(page).display()
    grid(
      columns: (1fr, 1fr, 1fr),
      align: (left, center, right),
      text(size: 8pt, fill: color-footer-text)[],
      text(size: 8pt, fill: color-footer-text)[Page #page-num],
      text(size: 8pt, fill: color-footer-text)[Generated by tachi],
    )
  }
}
