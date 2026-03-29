// =============================================================================
// Findings Detail: Security Assessment PDF Booklet
// =============================================================================
// Renders a severity-sorted findings table with column sets determined by the
// data source tier (1 = compensating-controls, 2 = risk-scores, 3 = threats).
//
// Exported function:
//   findings-detail-page(classification, tier, findings)
//
// Usage from main.typ:
//   #import "findings-detail.typ": findings-detail-page
//   #findings-detail-page(
//     classification: "CONFIDENTIAL",
//     tier: 2,
//     findings: report-data.findings-rows,
//   )
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// 1. Tier Configuration
// ---------------------------------------------------------------------------
// Each tier defines its column headers, dictionary key names that map to those
// headers, the column widths, and which key holds the severity/risk value for
// color coding.  The "text" column (Threat, Recommendation, Mitigation) gets
// a 1fr flex width; numeric and status columns stay narrow.

#let tier-config(tier) = {
  if tier == 1 {
    (
      title: "Findings Detail — Residual Risk",
      headers: ("ID", "Component", "Threat", "Residual Score", "Residual Severity", "Control Status", "Recommendation"),
      keys: ("id", "component", "threat", "residual_score", "residual_severity", "control_status", "recommendation"),
      widths: (0.5in, 0.9in, 1fr, 0.7in, 0.8in, 0.7in, 1.2fr),
      severity-key: "residual_severity",
    )
  } else if tier == 2 {
    (
      title: "Findings Detail — Inherent Risk",
      headers: ("ID", "Component", "Threat", "Composite Score", "Severity", "CVSS", "Exploitability"),
      keys: ("id", "component", "threat", "composite_score", "severity", "cvss", "exploitability"),
      widths: (0.5in, 0.9in, 1fr, 0.7in, 0.7in, 0.55in, 0.8in),
      severity-key: "severity",
    )
  } else {
    // Tier 3 (default / fallback)
    (
      title: "Findings Detail — Severity",
      headers: ("ID", "Component", "Threat", "Likelihood", "Impact", "Risk Level", "Mitigation"),
      keys: ("id", "component", "threat", "likelihood", "impact", "risk_level", "mitigation"),
      widths: (0.5in, 0.9in, 1fr, 0.7in, 0.6in, 0.7in, 1.2fr),
      severity-key: "risk_level",
    )
  }
}


// ---------------------------------------------------------------------------
// 2. Severity Sort Order
// ---------------------------------------------------------------------------
// Returns a numeric rank for severity-based sorting. Lower rank sorts first
// so Critical appears at the top of the table.

#let severity-rank(level) = {
  let normalized = lower(level)
  if normalized == "critical" { 0 }
  else if normalized == "high" { 1 }
  else if normalized == "medium" { 2 }
  else if normalized == "low" { 3 }
  else { 4 }
}


// ---------------------------------------------------------------------------
// 3. Main Export: findings-detail-page
// ---------------------------------------------------------------------------
// Parameters:
//   classification (string or none) — text for the classification header bar
//   tier (integer: 1, 2, or 3) — selects column set per DataSourceTier
//   findings (array of dictionaries) — row data; keys must match tier's keys
//
// Behavior:
//   - Sorts findings by severity (Critical > High > Medium > Low)
//   - Applies severity background color to the severity/risk column cells
//   - Uses monospace font for data cells, sans-serif for header cells
//   - Repeats header row on continuation pages via repeat: true
//   - Shows "No findings to display." when findings array is empty

#let findings-detail-page(classification: none, tier: 3, findings: ()) = {
  let config = tier-config(tier)

  // -- Page header and footer -------------------------------------------------
  report-header(classification: classification, title: config.title)
  v(0.2in)

  // -- Empty state ------------------------------------------------------------
  if findings.len() == 0 {
    v(1in)
    align(center,
      text(
        font: font-heading,
        size: 14pt,
        fill: rgb("#64748B"),
        weight: "semibold",
      )[No findings to display.],
    )
    return
  }

  // -- Sort findings by severity (Critical first) -----------------------------
  let sorted-findings = findings.sorted(key: row => {
    let sev-value = row.at(config.severity-key, default: "")
    severity-rank(sev-value)
  })

  // -- Build header cells -----------------------------------------------------
  let header-cells = config.headers.map(h =>
    table.cell(
      fill: color-header-bg,
      text(
        font: font-heading,
        size: 8pt,
        fill: color-header-text,
        weight: "bold",
      )[#h],
    )
  )

  // -- Build data rows --------------------------------------------------------
  let data-cells = ()
  for row in sorted-findings {
    for (col-idx, key) in config.keys.enumerate() {
      let value = str(row.at(key, default: "—"))

      if key == config.severity-key {
        // Severity/risk column: colored background with white text
        let sev-fill = severity-color(value)
        data-cells.push(
          table.cell(
            fill: sev-fill,
            text(
              font: font-mono,
              size: 8pt,
              fill: white,
              weight: "bold",
            )[#value],
          )
        )
      } else {
        // Standard data column: monospace
        data-cells.push(
          table.cell(
            text(
              font: font-mono,
              size: 8pt,
            )[#value],
          )
        )
      }
    }
  }

  // -- Render table -----------------------------------------------------------
  table(
    columns: config.widths,
    align: (col, _row) => {
      // Left-align text-heavy columns (Threat, Recommendation/Mitigation),
      // center narrow columns (ID, scores, status).
      if col == 0 { center }          // ID
      else if col == 2 { left }       // Threat (long text)
      else if col == 6 { left }       // Last column (Recommendation/Mitigation/Exploitability)
      else { center }                 // Score, Severity, Status columns
    },
    inset: (x: 0.3em, y: 0.4em),
    stroke: 0.5pt + color-rule,
    table.header(
      repeat: true,
      ..header-cells,
    ),
    ..data-cells,
  )

  v(0.15in)

  // -- Table legend -----------------------------------------------------------
  align(right,
    text(
      font: font-body,
      size: 7pt,
      fill: color-footer-text,
    )[
      #config.headers.len() columns |
      #sorted-findings.len() finding#if sorted-findings.len() != 1 [s] |
      Sorted by #if tier == 1 [residual severity] else if tier == 2 [severity] else [risk level] (critical first)
    ],
  )
}
