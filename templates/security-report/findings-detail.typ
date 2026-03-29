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
      tier-num: 1,
      title: "Findings Detail — Residual Risk",
      headers: ("ID", "Component", "Threat", "Residual Score", "Residual Severity", "Control Status", "Recommendation"),
      keys: ("id", "component", "threat", "residual_score", "residual_severity", "control_status", "recommendation"),
      widths: (0.5in, 0.9in, 1fr, 0.7in, 0.8in, 0.7in, 1.2fr),
      severity-key: "residual_severity",
    )
  } else if tier == 2 {
    (
      tier-num: 2,
      title: "Findings Detail — Inherent Risk",
      headers: ("ID", "Component", "Threat", "Composite Score", "Severity", "CVSS", "Exploitability"),
      keys: ("id", "component", "threat", "composite_score", "severity", "cvss", "exploitability"),
      widths: (0.5in, 0.9in, 1fr, 0.7in, 0.7in, 0.55in, 0.8in),
      severity-key: "severity",
    )
  } else {
    // Tier 3 (default / fallback)
    (
      tier-num: 3,
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
// 3. Finding Card Rendering
// ---------------------------------------------------------------------------
// Renders a single finding as a styled card with severity badge, threat ID,
// component, description, and recommendation/mitigation. For Tier 1, includes
// residual risk score and control status. For Tier 2, includes CVSS and
// composite score.

#let _finding-card(row, config) = {
  let sev-value = str(row.at(config.severity-key, default: ""))
  let sev-fill = severity-color(sev-value)
  let id = str(row.at("id", default: "—"))
  let component = str(row.at("component", default: "—"))
  let threat = str(row.at("threat", default: "—"))

  // Determine recommendation/mitigation text based on available keys.
  let rec-text = str(row.at("recommendation", default: row.at("mitigation", default: "—")))

  block(
    width: 100%,
    breakable: false,
    inset: 0.6em,
    radius: 4pt,
    fill: brand-light,
    stroke: 0.5pt + brand-primary,
    {
      // -- Header: severity badge + ID + component --------------------------
      grid(
        columns: (auto, auto, 1fr),
        column-gutter: 0.5em,
        align: (left + horizon, left + horizon, right + horizon),
        box(
          fill: sev-fill,
          radius: 3pt,
          inset: (x: 0.5em, y: 0.2em),
          text(fill: white, size: 7pt, weight: "bold", tracking: 0.05em)[#upper(sev-value)],
        ),
        text(font: font-mono, size: 9pt, weight: "bold", fill: brand-primary)[#id],
        text(size: 9pt, fill: brand-muted)[#component],
      )

      v(0.4em)

      // -- Threat description -----------------------------------------------
      text(size: 10pt)[#threat]

      v(0.3em)

      // -- Recommendation/mitigation ----------------------------------------
      block(
        width: 100%,
        inset: (left: 0.4em),
        stroke: (left: 2pt + brand-secondary),
        text(size: 9pt, fill: brand-secondary)[#rec-text],
      )

      // -- Tier-specific metadata -------------------------------------------
      v(0.3em)
      {
        let meta-items = ()
        if config.at("tier-num", default: 3) == 1 {
          meta-items.push("Residual: " + str(row.at("residual_score", default: "—")))
          meta-items.push("Control: " + str(row.at("control_status", default: "—")))
        } else if config.at("tier-num", default: 3) == 2 {
          meta-items.push("CVSS: " + str(row.at("cvss", default: "—")))
          meta-items.push("Composite: " + str(row.at("composite_score", default: "—")))
          meta-items.push("Exploit.: " + str(row.at("exploitability", default: "—")))
        } else {
          let lk = str(row.at("likelihood", default: "—"))
          let im = str(row.at("impact", default: "—"))
          if lk != "—" or im != "—" {
            meta-items.push("Likelihood: " + lk)
            meta-items.push("Impact: " + im)
          }
        }
        if meta-items.len() > 0 {
          text(
            font: font-mono,
            size: 8pt,
            fill: brand-muted,
          )[#meta-items.join("  |  ")]
        }
      }
    },
  )
}


// ---------------------------------------------------------------------------
// 4. Main Export: findings-detail-page
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

  // Page heading — uses heading element for TOC outline() discovery.
  heading(level: 1, config.title)

  // -- Empty state ------------------------------------------------------------
  if findings.len() == 0 {
    v(1in)
    align(center,
      text(
        font: font-heading,
        size: 14pt,
        fill: brand-muted,
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

  // -- Render finding cards ---------------------------------------------------
  for row in sorted-findings {
    _finding-card(row, config)
    v(0.25em)
  }

  v(0.15in)

  // -- Card legend ------------------------------------------------------------
  align(right,
    text(
      font: font-body,
      size: 7pt,
      fill: color-footer-text,
    )[
      #sorted-findings.len() finding#if sorted-findings.len() != 1 [s] |
      Sorted by #if tier == 1 [residual severity] else if tier == 2 [severity] else [risk level] (critical first)
    ],
  )
}
