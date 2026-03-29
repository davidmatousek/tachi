// =============================================================================
// Control Coverage Page: Security Assessment PDF Booklet
// =============================================================================
// Renders the control coverage analysis from compensating-controls.md data:
//
//   1. Control status matrix — summary counts of found/partial/missing controls
//      per STRIDE category, displayed as a compact table with color-coded status.
//
//   2. Detailed control table — per-control rows with Component, Control Category,
//      Status, Evidence, and Effectiveness columns. Status cells are color-coded:
//      "Found" = green, "Partial" = yellow, "Missing" = red.
//
//   3. Summary statistics — total controls found, partial, missing with counts
//      and percentages.
//
// This page is only rendered when compensating-controls.md data is available.
// The report assembler agent sets a boolean flag to include/exclude this page.
//
// Usage in main.typ:
//   #import "control-coverage.typ": control-coverage-page
//   #control-coverage-page(
//     classification: "CONFIDENTIAL",   // or none to omit
//     coverage-matrix: (
//       (category: "Spoofing",             found: 2, partial: 1, missing: 0),
//       (category: "Tampering",            found: 1, partial: 0, missing: 1),
//       (category: "Repudiation",          found: 0, partial: 1, missing: 0),
//       (category: "Information Disclosure", found: 1, partial: 0, missing: 0),
//       (category: "Denial of Service",    found: 0, partial: 0, missing: 1),
//       (category: "Elevation of Privilege", found: 1, partial: 1, missing: 0),
//     ),
//     controls: (
//       (
//         component: "API Gateway",
//         category: "Authentication",
//         status: "Found",
//         evidence: "src/auth/jwt.ts:42",
//         effectiveness: "Strong",
//       ),
//       (
//         component: "API Gateway",
//         category: "Rate Limiting",
//         status: "Partial",
//         evidence: "src/middleware/rate-limit.ts:15",
//         effectiveness: "Moderate",
//       ),
//     ),
//     summary: (
//       total-found: 5,
//       total-partial: 3,
//       total-missing: 2,
//     ),
//   )
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// Internal: Status color mapping
// ---------------------------------------------------------------------------
// Maps control status strings to colors for table cell backgrounds.
// "Found" = green, "Partial" = yellow/amber, "Missing" = red.
// Returns a light-tinted fill for table cells and a saturated color for text.

#let _status-colors(status) = {
  let normalized = lower(status)
  if normalized == "found" or normalized == "control found" {
    (fill: rgb("#16A34A").lighten(85%), text-color: rgb("#16A34A"))
  } else if normalized == "partial" or normalized == "partial control" {
    (fill: rgb("#D97706").lighten(85%), text-color: rgb("#D97706"))
  } else if normalized == "missing" or normalized == "no control found" {
    (fill: rgb("#DC2626").lighten(85%), text-color: rgb("#DC2626"))
  } else {
    (fill: rgb("#9CA3AF").lighten(85%), text-color: rgb("#9CA3AF"))
  }
}


// ---------------------------------------------------------------------------
// Internal: Status display label
// ---------------------------------------------------------------------------
// Normalizes status strings to consistent short labels for display.

#let _status-label(status) = {
  let normalized = lower(status)
  if normalized == "found" or normalized == "control found" { "Found" }
  else if normalized == "partial" or normalized == "partial control" { "Partial" }
  else if normalized == "missing" or normalized == "no control found" { "Missing" }
  else { status }
}


// ---------------------------------------------------------------------------
// Internal: Section 1 — Control status matrix
// ---------------------------------------------------------------------------
// Renders a table of STRIDE categories with found/partial/missing counts.
// Each row shows one STRIDE category; count cells are color-coded when > 0.

#let _status-matrix(coverage-matrix) = {
  block(
    width: 100%,
    inset: 0.6em,
    radius: 4pt,
    stroke: 0.5pt + color-rule,
    {
      text(
        font: font-heading,
        size: 12pt,
        weight: "bold",
        fill: brand-primary,
      )[Control Status by STRIDE Category]
      v(0.5em)

      table(
        columns: (1fr, auto, auto, auto, auto),
        align: (left, center, center, center, center),
        stroke: 0.5pt + color-rule,
        inset: 0.5em,

        // Header row.
        table.header(
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[STRIDE Category]
          ],
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Found]
          ],
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Partial]
          ],
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Missing]
          ],
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Total]
          ],
        ),

        // Data rows — one per STRIDE category.
        ..coverage-matrix.map(row => {
          let row-total = row.found + row.partial + row.missing
          let found-colors = _status-colors("Found")
          let partial-colors = _status-colors("Partial")
          let missing-colors = _status-colors("Missing")
          (
            text(size: 10pt, weight: "semibold")[#row.category],
            // Found count — green tint when > 0.
            if row.found > 0 {
              table.cell(fill: found-colors.fill)[
                #text(size: 10pt, weight: "bold", fill: found-colors.text-color)[#row.found]
              ]
            } else {
              text(size: 10pt, fill: color-footer-text)[#row.found]
            },
            // Partial count — yellow tint when > 0.
            if row.partial > 0 {
              table.cell(fill: partial-colors.fill)[
                #text(size: 10pt, weight: "bold", fill: partial-colors.text-color)[#row.partial]
              ]
            } else {
              text(size: 10pt, fill: color-footer-text)[#row.partial]
            },
            // Missing count — red tint when > 0.
            if row.missing > 0 {
              table.cell(fill: missing-colors.fill)[
                #text(size: 10pt, weight: "bold", fill: missing-colors.text-color)[#row.missing]
              ]
            } else {
              text(size: 10pt, fill: color-footer-text)[#row.missing]
            },
            // Row total.
            text(size: 10pt, weight: "semibold")[#row-total],
          )
        }).flatten(),
      )
    },
  )
}


// ---------------------------------------------------------------------------
// Internal: Section 2 — Detailed control table
// ---------------------------------------------------------------------------
// Renders every detected control with component, category, status (color-coded),
// evidence location, and effectiveness rating. Table headers repeat on
// continuation pages when the table exceeds one page.

#let _control-table(controls) = {
  if controls.len() == 0 {
    return
  }

  block(
    width: 100%,
    {
      text(
        font: font-heading,
        size: 12pt,
        weight: "bold",
        fill: brand-primary,
      )[Detailed Control Assessment]
      v(0.3em)

      table(
        columns: (1.2fr, 1fr, 0.7fr, 1.5fr, 0.8fr),
        align: (left, left, center, left, center),
        stroke: 0.5pt + color-rule,
        inset: 0.45em,

        // Header row — repeats on continuation pages.
        table.header(
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Component]
          ],
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Control Category]
          ],
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Status]
          ],
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Evidence]
          ],
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Effectiveness]
          ],
        ),

        // Data rows — one per control.
        ..controls.map(ctrl => {
          let colors = _status-colors(ctrl.status)
          let label = _status-label(ctrl.status)
          (
            text(size: 9pt)[#ctrl.component],
            text(size: 9pt)[#ctrl.category],
            table.cell(fill: colors.fill)[
              #text(size: 9pt, weight: "bold", fill: colors.text-color)[#label]
            ],
            // Evidence rendered in monospace for file paths.
            text(font: font-mono, size: 8pt)[#ctrl.evidence],
            text(size: 9pt)[#ctrl.effectiveness],
          )
        }).flatten(),
      )
    },
  )
}


// ---------------------------------------------------------------------------
// Internal: Section 3 — Summary statistics
// ---------------------------------------------------------------------------
// Renders total found/partial/missing counts with percentages as a compact
// summary panel. Includes a visual bar showing the proportion of each status.

#let _summary-stats(summary) = {
  let total = summary.total-found + summary.total-partial + summary.total-missing

  // Guard against division by zero when no controls exist.
  let pct-found = if total > 0 { calc.round(summary.total-found / total * 100, digits: 1) } else { 0 }
  let pct-partial = if total > 0 { calc.round(summary.total-partial / total * 100, digits: 1) } else { 0 }
  let pct-missing = if total > 0 { calc.round(summary.total-missing / total * 100, digits: 1) } else { 0 }

  let found-colors = _status-colors("Found")
  let partial-colors = _status-colors("Partial")
  let missing-colors = _status-colors("Missing")

  block(
    width: 100%,
    inset: 0.6em,
    radius: 4pt,
    stroke: 0.5pt + color-rule,
    {
      text(
        font: font-heading,
        size: 12pt,
        weight: "bold",
        fill: brand-primary,
      )[Coverage Summary]
      v(0.5em)

      // --- Stacked proportion bar -------------------------------------------
      // Visual indicator showing the relative proportion of found/partial/missing.
      let bar-height = 0.6em
      if total > 0 {
        box(
          width: 100%,
          height: bar-height,
          radius: 3pt,
          clip: true,
          {
            // Found segment (green).
            place(top + left,
              box(
                width: pct-found * 1%,
                height: 100%,
                fill: found-colors.text-color,
              ),
            )
            // Partial segment (yellow) — offset by found width.
            place(top + left, dx: pct-found * 1%,
              box(
                width: pct-partial * 1%,
                height: 100%,
                fill: partial-colors.text-color,
              ),
            )
            // Missing segment (red) — offset by found + partial width.
            place(top + left, dx: (pct-found + pct-partial) * 1%,
              box(
                width: pct-missing * 1%,
                height: 100%,
                fill: missing-colors.text-color,
              ),
            )
          },
        )
        v(0.5em)
      }

      // --- Summary table ----------------------------------------------------
      table(
        columns: (1fr, auto, auto),
        align: (left, center, right),
        stroke: 0.5pt + color-rule,
        inset: 0.5em,

        // Header.
        table.header(
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Control Status]
          ],
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Count]
          ],
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Percentage]
          ],
        ),

        // Found row.
        table.cell(fill: found-colors.fill)[
          #text(size: 10pt, weight: "semibold", fill: found-colors.text-color)[Control Found]
        ],
        text(size: 10pt, weight: "bold")[#summary.total-found],
        text(size: 10pt)[#str(pct-found)%],

        // Partial row.
        table.cell(fill: partial-colors.fill)[
          #text(size: 10pt, weight: "semibold", fill: partial-colors.text-color)[Partial Control]
        ],
        text(size: 10pt, weight: "bold")[#summary.total-partial],
        text(size: 10pt)[#str(pct-partial)%],

        // Missing row.
        table.cell(fill: missing-colors.fill)[
          #text(size: 10pt, weight: "semibold", fill: missing-colors.text-color)[No Control Found]
        ],
        text(size: 10pt, weight: "bold")[#summary.total-missing],
        text(size: 10pt)[#str(pct-missing)%],

        // Total row.
        table.cell(fill: color-header-bg.lighten(85%))[
          #text(size: 10pt, weight: "bold")[Total]
        ],
        text(size: 10pt, weight: "bold")[#total],
        text(size: 10pt, weight: "bold")[100%],
      )
    },
  )
}


// ---------------------------------------------------------------------------
// Exported: control-coverage-page
// ---------------------------------------------------------------------------
// Renders the full control coverage page. Called by main.typ only when
// compensating-controls.md data is available.
//
// Parameters:
//   classification    — string or none; classification marking for header
//   coverage-matrix   — array of dictionaries with keys:
//                        category (string), found (int), partial (int), missing (int)
//   controls          — array of dictionaries with keys:
//                        component (string), category (string), status (string),
//                        evidence (string), effectiveness (string)
//   summary           — dictionary with keys:
//                        total-found (int), total-partial (int), total-missing (int)

#let control-coverage-page(
  classification: none,
  coverage-matrix: (),
  controls: (),
  summary: (total-found: 0, total-partial: 0, total-missing: 0),
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
      title: "Control Coverage",
    ),
    footer: report-footer(),
  )[
    // Page heading — uses heading element for TOC outline() discovery.
    #heading(level: 1)[Control Coverage]

    // Section 1: Status matrix — STRIDE category breakdown.
    #_status-matrix(coverage-matrix)

    #v(0.3in)

    // Section 2: Detailed control table.
    #_control-table(controls)

    #v(0.3in)

    // Section 3: Summary statistics with proportion bar.
    #_summary-stats(summary)
  ]
}
