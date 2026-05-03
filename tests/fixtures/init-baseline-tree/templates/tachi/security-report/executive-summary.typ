// =============================================================================
// Executive Summary Page: Security Assessment PDF Booklet
// =============================================================================
// Renders the executive summary with two rendering paths:
//
//   1. Rich mode  — when threat-report.md narrative is available:
//      2-column layout with severity distribution metrics (left) and
//      narrative summary text (right).
//
//   2. Minimal mode — using threats.md risk summary only:
//      Single-column layout with severity counts and component distribution.
//
// Mode is auto-detected: if `executive-narrative` is not none, rich mode
// is used; otherwise minimal mode renders.
//
// Usage in main.typ:
//   #import "executive-summary.typ": executive-summary-page
//   #executive-summary-page(
//     classification: "CONFIDENTIAL",
//     critical-count: 3,
//     high-count: 8,
//     medium-count: 12,
//     low-count: 5,
//     total-findings: 28,
//     executive-narrative: "The assessment identified...",
//     component-distribution: (("API Gateway", 7), ("Auth Service", 5)),
//   )
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// Internal: Severity metric row
// ---------------------------------------------------------------------------
// Renders a single severity level as a colored indicator + label + count +
// percentage bar. Used by both rich and minimal modes.

#let _severity-row(label, count, total, color) = {
  let pct = if total > 0 { calc.round(count / total * 100, digits: 1) } else { 0 }
  let bar-width = if total > 0 { calc.round(count / total * 100, digits: 0) } else { 0 }

  grid(
    columns: (auto, 1fr, auto),
    column-gutter: 0.4em,
    align: (left + horizon, left + horizon, right + horizon),

    // Colored square + label.
    {
      box(
        width: 0.5em,
        height: 0.5em,
        fill: color,
        radius: 1pt,
      )
      h(0.35em)
      text(size: 10pt, weight: "semibold")[#label]
    },

    // Percentage bar.
    {
      box(
        width: 100%,
        height: 0.6em,
        radius: 2pt,
        clip: true,
        fill: color.lighten(80%),
        {
          place(
            top + left,
            box(
              width: calc.max(2, bar-width) * 1%,
              height: 100%,
              fill: color,
              radius: 2pt,
            ),
          )
        },
      )
    },

    // Count and percentage.
    text(
      size: 10pt,
      weight: "bold",
      fill: color,
    )[#count #text(weight: "regular", fill: color-footer-text)[(#str(pct)%)]],
  )
}


// ---------------------------------------------------------------------------
// Internal: Severity distribution panel
// ---------------------------------------------------------------------------
// Renders all four severity levels with a total header. Used by both modes.

#let _severity-panel(critical, high, medium, low, total) = {
  block(
    width: 100%,
    inset: 0.6em,
    radius: 4pt,
    stroke: 0.5pt + color-rule,
    {
      text(
        font: font-heading,
        size: 11pt,
        weight: "bold",
        fill: brand-primary,
      )[Severity Distribution]
      h(1fr)
      text(
        size: 10pt,
        fill: brand-secondary,
      )[#total findings total]
      v(0.5em)
      _severity-row("Critical", critical, total, severity-critical)
      v(0.35em)
      _severity-row("High", high, total, severity-high)
      v(0.35em)
      _severity-row("Medium", medium, total, severity-medium)
      v(0.35em)
      _severity-row("Low", low, total, severity-low)
    },
  )
}


// ---------------------------------------------------------------------------
// Internal: Component distribution panel (minimal mode only)
// ---------------------------------------------------------------------------
// Renders a table of components and their finding counts when no narrative
// text is available. Gives stakeholders a quick view of where findings
// concentrate.

#let _component-panel(components) = {
  if components == none or components.len() == 0 {
    return
  }

  v(0.4em)

  block(
    width: 100%,
    inset: 0.6em,
    radius: 4pt,
    stroke: 0.5pt + color-rule,
    {
      text(
        font: font-heading,
        size: 11pt,
        weight: "bold",
        fill: brand-primary,
      )[Component Distribution]
      v(0.5em)

      table(
        columns: (1fr, auto),
        align: (left, right),
        stroke: 0.5pt + color-rule,
        inset: 0.4em,

        table.header(
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Component]
          ],
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Findings]
          ],
        ),

        // Flatten the array of (name, count) tuples into positional cell args.
        ..components.map(entry => {
          let (name, count) = entry
          (
            text(size: 10pt)[#name],
            text(size: 10pt, weight: "semibold")[#count],
          )
        }).flatten(),
      )
    },
  )
}


// ---------------------------------------------------------------------------
// Internal: Narrative panel (rich mode only)
// ---------------------------------------------------------------------------
// Renders the executive narrative text from threat-report.md Section 1.

#let _narrative-panel(narrative) = {
  block(
    width: 100%,
    inset: 0.6em,
    radius: 4pt,
    stroke: 0.5pt + color-rule,
    {
      text(
        font: font-heading,
        size: 11pt,
        weight: "bold",
        fill: brand-primary,
      )[Assessment Summary]
      v(0.5em)
      set par(leading: 0.55em)
      text(size: 9pt)[#narrative]
    },
  )
}


// ---------------------------------------------------------------------------
// Exported: executive-summary-page
// ---------------------------------------------------------------------------
// Renders the full executive summary page. Auto-detects rich vs. minimal
// mode based on whether executive-narrative is provided.
//
// Parameters:
//   classification          — string or none; classification marking for header
//   critical-count          — int; number of critical findings
//   high-count              — int; number of high findings
//   medium-count            — int; number of medium findings
//   low-count               — int; number of low findings
//   total-findings          — int; total finding count
//   executive-narrative     — string or none; if not none, renders rich mode
//   component-distribution  — array of (name, count) tuples or none

#let executive-summary-page(
  classification: none,
  critical-count: 0,
  high-count: 0,
  medium-count: 0,
  low-count: 0,
  total-findings: 0,
  executive-narrative: none,
  component-distribution: none,
) = {
  // Page with consistent header/footer chrome from shared.typ.
  page(
    width: page-width,
    height: page-height,
    margin: (
      top: margin-top,
      bottom: margin-bottom,
      left: margin-left,
      right: margin-right,
    ),
    header: report-header(
      classification: classification,
      title: "Executive Summary",
    ),
    footer: report-footer(),
  )[
    // Page heading — uses heading element for TOC outline() discovery.
    #heading(level: 1)[Executive Summary]

    // -----------------------------------------------------------------------
    // Rich mode: 2-column layout (metrics left, narrative right)
    // -----------------------------------------------------------------------
    #if executive-narrative != none {
      grid(
        columns: (45%, 55%),
        column-gutter: 0.3in,

        // Left column: severity distribution + component breakdown.
        {
          _severity-panel(
            critical-count,
            high-count,
            medium-count,
            low-count,
            total-findings,
          )
          if component-distribution != none and component-distribution.len() > 0 {
            _component-panel(component-distribution)
          }
        },

        // Right column: narrative summary.
        {
          _narrative-panel(executive-narrative)
        },
      )
    } else {
      // -------------------------------------------------------------------
      // Minimal mode: single-column (severity counts + component distribution)
      // -------------------------------------------------------------------
      _severity-panel(
        critical-count,
        high-count,
        medium-count,
        low-count,
        total-findings,
      )
      _component-panel(component-distribution)
    }
  ]
}
