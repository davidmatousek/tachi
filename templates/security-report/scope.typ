// =============================================================================
// Assessment Scope Page: Security Assessment PDF Booklet
// =============================================================================
// Renders the assessment scope with component, data flow, and trust boundary
// tables extracted from threats.md Sections 1-2.
//
// Two rendering paths:
//
//   1. Rich mode  — when at least one scope array is non-empty:
//      Metric badges at top, followed by conditional sections for Components
//      Analyzed, Data Flows, and Trust Boundaries.
//
//   2. Graceful degradation — when ALL arrays are empty:
//      Centered notice block with available metadata (counts from the
//      report-data.typ frontmatter) and a "Limited scope documentation"
//      message.
//
// Usage in main.typ:
//   #import "scope.typ": scope-page
//   #scope-page(
//     classification: "CONFIDENTIAL",
//     components: (
//       (name: "API Gateway", type: "Process", description: "Routes API requests"),
//       (name: "Auth Service", type: "Process", description: "Handles authentication"),
//     ),
//     data-flows: (
//       (source: "Client", destination: "API Gateway", data: "API Requests", protocol: "HTTPS"),
//     ),
//     trust-boundaries: (
//       (zone: "Public Internet", trust-level: "Untrusted", components: "Client App"),
//     ),
//     boundary-crossings: (
//       (crossing: "Internet to DMZ", from-zone: "Public", to-zone: "DMZ", components: "API Gateway", controls: "WAF, TLS"),
//     ),
//     component-count: 5,
//     data-flow-count: 8,
//     trust-boundary-count: 3,
//   )
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// Internal: Metric badge
// ---------------------------------------------------------------------------
// Renders a single metric badge with a count and label. Uses brand-primary
// background with white text, matching the executive summary badge style.

#let _metric-badge(count, label) = {
  box(
    inset: (x: 0.6em, y: 0.3em),
    radius: 3pt,
    fill: brand-primary,
    text(
      font: font-heading,
      size: 9pt,
      weight: "bold",
      fill: white,
    )[#count #label],
  )
}


// ---------------------------------------------------------------------------
// Internal: Metric badges row
// ---------------------------------------------------------------------------
// Renders three inline badges: Components, Data Flows, Trust Boundaries.

#let _metric-badges(component-count, data-flow-count, trust-boundary-count) = {
  grid(
    columns: (auto, auto, auto, 1fr),
    column-gutter: 0.3em,
    align: horizon,
    _metric-badge(component-count, [Component#if component-count != 1 [s]]),
    _metric-badge(data-flow-count, [Data Flow#if data-flow-count != 1 [s]]),
    _metric-badge(trust-boundary-count, [Trust Boundar#if trust-boundary-count != 1 [ies] else [y]]),
    [],
  )
}


// ---------------------------------------------------------------------------
// Internal: Section 1 — Components Analyzed
// ---------------------------------------------------------------------------
// Renders a table of assessed components with Name, Type, and Description
// columns. Only rendered when the components array is non-empty.

#let _components-table(components) = {
  if components.len() == 0 {
    return
  }

  text(
    font: font-heading,
    size: 12pt,
    weight: "bold",
  )[Components Analyzed]
  v(0.3em)

  table(
    columns: (1.2in, 0.9in, 1fr),
    align: (left, left, left),
    stroke: 0.5pt + color-rule,
    inset: 0.45em,

    // Header row.
    table.header(
      table.cell(fill: color-header-bg)[
        #text(fill: color-header-text, size: 9pt, weight: "bold")[Name]
      ],
      table.cell(fill: color-header-bg)[
        #text(fill: color-header-text, size: 9pt, weight: "bold")[Type]
      ],
      table.cell(fill: color-header-bg)[
        #text(fill: color-header-text, size: 9pt, weight: "bold")[Description]
      ],
    ),

    // Data rows.
    ..components.map(comp => (
      text(size: 9pt, weight: "semibold")[#comp.name],
      text(size: 9pt)[#comp.type],
      text(size: 9pt)[#comp.description],
    )).flatten(),
  )
}


// ---------------------------------------------------------------------------
// Internal: Section 2 — Data Flows
// ---------------------------------------------------------------------------
// Renders a table of data flows with Source, Destination, Data, and Protocol
// columns. Only rendered when the data-flows array is non-empty.

#let _data-flows-table(data-flows) = {
  if data-flows.len() == 0 {
    return
  }

  text(
    font: font-heading,
    size: 12pt,
    weight: "bold",
  )[Data Flows]
  v(0.3em)

  table(
    columns: (1.1in, 1.1in, 1fr, 0.9in),
    align: (left, left, left, left),
    stroke: 0.5pt + color-rule,
    inset: 0.45em,

    // Header row.
    table.header(
      table.cell(fill: color-header-bg)[
        #text(fill: color-header-text, size: 9pt, weight: "bold")[Source]
      ],
      table.cell(fill: color-header-bg)[
        #text(fill: color-header-text, size: 9pt, weight: "bold")[Destination]
      ],
      table.cell(fill: color-header-bg)[
        #text(fill: color-header-text, size: 9pt, weight: "bold")[Data]
      ],
      table.cell(fill: color-header-bg)[
        #text(fill: color-header-text, size: 9pt, weight: "bold")[Protocol]
      ],
    ),

    // Data rows.
    ..data-flows.map(flow => (
      text(size: 9pt)[#flow.source],
      text(size: 9pt)[#flow.destination],
      text(size: 9pt)[#flow.data],
      text(font: font-mono, size: 8pt)[#flow.protocol],
    )).flatten(),
  )
}


// ---------------------------------------------------------------------------
// Internal: Section 3 — Trust Boundaries
// ---------------------------------------------------------------------------
// Renders a table of trust boundaries with Zone, Trust Level, and Components
// columns. Only rendered when the trust-boundaries array is non-empty.

#let _trust-boundaries-table(trust-boundaries) = {
  if trust-boundaries.len() == 0 {
    return
  }

  text(
    font: font-heading,
    size: 12pt,
    weight: "bold",
  )[Trust Boundaries]
  v(0.3em)

  table(
    columns: (1.2in, 0.9in, 1fr),
    align: (left, left, left),
    stroke: 0.5pt + color-rule,
    inset: 0.45em,

    // Header row.
    table.header(
      table.cell(fill: color-header-bg)[
        #text(fill: color-header-text, size: 9pt, weight: "bold")[Zone]
      ],
      table.cell(fill: color-header-bg)[
        #text(fill: color-header-text, size: 9pt, weight: "bold")[Trust Level]
      ],
      table.cell(fill: color-header-bg)[
        #text(fill: color-header-text, size: 9pt, weight: "bold")[Components]
      ],
    ),

    // Data rows.
    ..trust-boundaries.map(boundary => (
      text(size: 9pt, weight: "semibold")[#boundary.zone],
      text(size: 9pt)[#boundary.trust-level],
      text(size: 9pt)[#boundary.components],
    )).flatten(),
  )
}


// ---------------------------------------------------------------------------
// Internal: Graceful degradation notice
// ---------------------------------------------------------------------------
// Renders when ALL scope arrays are empty. Displays a centered notice block
// with available metadata from the report-data.typ frontmatter counts.

#let _empty-scope-notice(component-count, data-flow-count, trust-boundary-count) = {
  v(0.8in)
  align(center,
    block(
      width: 80%,
      inset: 1.2em,
      radius: 4pt,
      stroke: 0.5pt + color-rule,
      fill: brand-light,
      {
        text(
          font: font-heading,
          size: 12pt,
          weight: "semibold",
          fill: color-footer-text,
        )[Limited scope documentation available for this assessment.]
        v(0.6em)
        text(
          size: 10pt,
          fill: color-footer-text,
        )[
          The assessed system contains #component-count component#if component-count != 1 [s]
          with #data-flow-count data flow#if data-flow-count != 1 [s]
          across #trust-boundary-count trust boundar#if trust-boundary-count != 1 [ies] else [y].
        ]
      },
    ),
  )
}


// ---------------------------------------------------------------------------
// Exported: scope-page
// ---------------------------------------------------------------------------
// Renders the full assessment scope page. Auto-detects rich vs. degraded
// mode based on whether any scope arrays contain data.
//
// Parameters:
//   classification          — string or none; classification marking for header
//   components              — array of dicts: {name, type, description}
//   data-flows              — array of dicts: {source, destination, data, protocol}
//   trust-boundaries        — array of dicts: {zone, trust-level, components}
//   boundary-crossings      — array of dicts: {crossing, from-zone, to-zone, components, controls}
//   component-count         — int; total component count for badges and fallback
//   data-flow-count         — int; total data flow count for badges and fallback
//   trust-boundary-count    — int; total trust boundary count for badges and fallback

#let scope-page(
  classification: none,
  components: (),
  data-flows: (),
  trust-boundaries: (),
  boundary-crossings: (),
  component-count: 0,
  data-flow-count: 0,
  trust-boundary-count: 0,
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
      title: "Assessment Scope",
    ),
    footer: report-footer(),
  )[
    // Page heading — uses heading element for TOC outline() discovery.
    #heading(level: 1)[Assessment Scope]

    // -------------------------------------------------------------------
    // Detect whether any scope data is available for rich rendering.
    // -------------------------------------------------------------------
    #if components.len() == 0 and data-flows.len() == 0 and trust-boundaries.len() == 0 {
      // ---------------------------------------------------------------
      // Graceful degradation: no scope arrays populated.
      // ---------------------------------------------------------------
      _empty-scope-notice(component-count, data-flow-count, trust-boundary-count)
    } else {
      // ---------------------------------------------------------------
      // Rich mode: metric badges + conditional section tables.
      // ---------------------------------------------------------------

      // Metric badges row.
      _metric-badges(component-count, data-flow-count, trust-boundary-count)
      v(0.25in)

      // Section 1: Components Analyzed.
      _components-table(components)

      if components.len() > 0 and (data-flows.len() > 0 or trust-boundaries.len() > 0) {
        v(0.2in)
      }

      // Section 2: Data Flows.
      _data-flows-table(data-flows)

      if data-flows.len() > 0 and trust-boundaries.len() > 0 {
        v(0.2in)
      }

      // Section 3: Trust Boundaries.
      _trust-boundaries-table(trust-boundaries)
    }
  ]
}
