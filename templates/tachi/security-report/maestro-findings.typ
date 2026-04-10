// =============================================================================
// MAESTRO Findings by Layer: Security Assessment PDF Booklet
// =============================================================================
// Renders findings grouped by CSA MAESTRO architectural layer (L1-L7, then
// Unclassified). Each layer section shows a heading with finding count and a
// table of findings sorted by severity (Critical first).
//
// Exported function:
//   maestro-findings-page(classification, maestro-findings-by-layer, has-maestro-data)
//
// Usage from main.typ:
//   #import "maestro-findings.typ": maestro-findings-page
//   #maestro-findings-page(
//     classification: "CONFIDENTIAL",
//     maestro-findings-by-layer: report-data.maestro-findings-by-layer,
//     has-maestro-data: report-data.has-maestro-data,
//   )
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// 1. Severity Sort Order
// ---------------------------------------------------------------------------
// Returns a numeric rank for severity-based sorting. Lower rank sorts first
// so Critical appears at the top of the table.

#let _maestro-severity-rank(level) = {
  let normalized = lower(level)
  if normalized == "critical" { 0 }
  else if normalized == "high" { 1 }
  else if normalized == "medium" { 2 }
  else if normalized == "low" { 3 }
  else { 4 }
}


// ---------------------------------------------------------------------------
// 2. Severity Badge
// ---------------------------------------------------------------------------
// Renders a compact colored badge for the severity value.

#let _severity-badge(level) = {
  let color = severity-color(level)
  box(
    fill: color,
    radius: 3pt,
    inset: (x: 0.5em, y: 0.2em),
    text(fill: white, size: 7pt, weight: "bold", tracking: 0.05em)[#upper(level)],
  )
}


// ---------------------------------------------------------------------------
// 3. Layer Findings Table
// ---------------------------------------------------------------------------
// Renders findings for a single MAESTRO layer as a zebra-striped table.

#let _layer-table(findings) = {
  let sorted-findings = findings.sorted(key: f => _maestro-severity-rank(str(f.at("severity", default: ""))))

  table(
    columns: (0.5in, 1fr, 0.8in, 1.5fr),
    align: (left, left, center, left),
    inset: 0.4em,
    stroke: 0.5pt + color-rule,

    // Header row
    table.cell(fill: brand-primary)[#text(size: 8pt, fill: white, weight: "bold")[ID]],
    table.cell(fill: brand-primary)[#text(size: 8pt, fill: white, weight: "bold")[Component]],
    table.cell(fill: brand-primary)[#text(size: 8pt, fill: white, weight: "bold")[Severity]],
    table.cell(fill: brand-primary)[#text(size: 8pt, fill: white, weight: "bold")[Threat]],

    // Data rows with zebra striping
    ..sorted-findings.enumerate().map(((idx, row)) => {
      let fill = if calc.rem(idx, 2) == 0 { white } else { brand-light }
      let id = str(row.at("id", default: "---"))
      let component = str(row.at("component", default: "---"))
      let severity = str(row.at("severity", default: "---"))
      let threat = str(row.at("threat", default: "---"))

      (
        table.cell(fill: fill)[#text(font: font-mono, size: 8pt)[#id]],
        table.cell(fill: fill)[#text(size: 8pt)[#component]],
        table.cell(fill: fill)[#_severity-badge(severity)],
        table.cell(fill: fill)[#text(size: 8pt)[#threat]],
      )
    }).flatten(),
  )
}


// ---------------------------------------------------------------------------
// 4. Main Export: maestro-findings-page
// ---------------------------------------------------------------------------
// Parameters:
//   classification (string or none) -- text for the classification header bar
//   maestro-findings-by-layer (array of dicts) -- layer groups with findings
//   has-maestro-data (boolean) -- whether MAESTRO data is present
//
// Behavior:
//   - Guard: renders nothing if has-maestro-data is false or array is empty
//   - Renders page header and level-1 heading
//   - Iterates layers in order (L1-L7, then Unclassified)
//   - Each layer gets a level-2 heading and findings table

#let maestro-findings-page(classification: none, maestro-findings-by-layer: (), has-maestro-data: false) = {
  // Guard: no data, no output.
  if not has-maestro-data or maestro-findings-by-layer.len() == 0 {
    return
  }

  // Page header and title.
  report-header(classification: classification, title: "MAESTRO Layer Analysis")

  heading(level: 1, "MAESTRO Layer Analysis")

  // Introductory paragraph.
  text(size: 10pt)[
    The following findings are grouped by their CSA MAESTRO framework architectural layer, providing a layer-oriented view of the threat landscape. Each layer represents a distinct level of the agentic AI system stack, from Foundation Model (L1) through Agent Ecosystem (L7). Findings within each layer are sorted by severity.
  ]

  v(0.15in)

  // Canonical MAESTRO layer names — fallback when layer-name is empty.
  let _maestro-names = (
    "L1": "Foundation Model",
    "L2": "Data Operations",
    "L3": "Agent Framework",
    "L4": "Deployment Infrastructure",
    "L5": "Evaluation and Observability",
    "L6": "Security and Compliance",
    "L7": "Agent Ecosystem",
  )

  // Iterate layers in provided order (expected L1-L7, then Unclassified).
  for layer-group in maestro-findings-by-layer {
    let layer-id = str(layer-group.at("layer-id", default: ""))
    let layer-name = str(layer-group.at("layer-name", default: ""))
    // Fallback: resolve from canonical names if layer-name is empty.
    if layer-name == "" {
      layer-name = _maestro-names.at(layer-id, default: layer-id)
    }
    let layer-findings = layer-group.at("findings", default: ())
    let count = layer-findings.len()

    // Layer heading with finding count.
    heading(level: 2)[#layer-id --- #layer-name #text(size: 10pt, fill: brand-muted, weight: "regular")[(#count finding#if count != 1 [s])]]

    if count > 0 {
      _layer-table(layer-findings)
    } else {
      text(size: 10pt, fill: brand-muted, style: "italic")[No findings mapped to this layer.]
    }
  }

  v(0.15in)

  // Footer legend.
  align(right,
    text(
      font: font-body,
      size: 7pt,
      fill: color-footer-text,
    )[
      #maestro-findings-by-layer.map(g => g.at("findings", default: ()).len()).sum() findings across #maestro-findings-by-layer.len() MAESTRO layers |
      Sorted by severity (critical first)
    ],
  )
}
