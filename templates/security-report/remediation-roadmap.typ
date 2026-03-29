// =============================================================================
// Remediation Roadmap Page: Security Assessment PDF Booklet
// =============================================================================
// Renders a prioritized action table grouped by severity (Critical first, then
// High, Medium, Low). Each group has a colored severity header row followed by
// the findings in that group. The table supports multi-page overflow with
// repeated column headers.
//
// Data sources (in order of preference):
//   1. compensating-controls.md Section 3 — recommendations with SLAs
//   2. threat-report.md remediation section — narrative remediation items
//
// Usage in main.typ:
//   #import "remediation-roadmap.typ": remediation-roadmap-page
//   #remediation-roadmap-page(
//     classification: "CONFIDENTIAL",
//     actions: (
//       (severity: "Critical", finding-id: "T-001", finding-name: "SQL Injection in Auth", recommendation: "Parameterize all queries", sla: "7 days", status: "Not Started"),
//       (severity: "High", finding-id: "T-005", finding-name: "Weak JWT Signing", recommendation: "Rotate to RS256", sla: "14 days", status: "In Progress"),
//       (severity: "Medium", finding-id: "T-012", finding-name: "Verbose Error Messages", recommendation: "Sanitize error responses", sla: "30 days", status: "Not Started"),
//       (severity: "Low", finding-id: "T-020", finding-name: "Missing CSP Header", recommendation: "Add Content-Security-Policy", sla: "90 days", status: "Not Started"),
//     ),
//   )
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// Internal: Severity ordering
// ---------------------------------------------------------------------------
// Maps a severity string to a numeric sort key so that actions can be grouped
// and ordered: Critical (0) -> High (1) -> Medium (2) -> Low (3).
// Unknown severity values sort last (4).

#let _severity-order(level) = {
  let normalized = lower(level)
  if normalized == "critical" { 0 }
  else if normalized == "high" { 1 }
  else if normalized == "medium" { 2 }
  else if normalized == "low" { 3 }
  else { 4 }
}


// ---------------------------------------------------------------------------
// Internal: Group actions by severity
// ---------------------------------------------------------------------------
// Takes the flat actions array and returns an array of (severity, items)
// tuples sorted by severity order. Only groups with at least one item are
// included.

#let _group-by-severity(actions) = {
  let groups = (
    ("Critical", ()),
    ("High", ()),
    ("Medium", ()),
    ("Low", ()),
  )

  // Distribute actions into groups.
  let critical = ()
  let high = ()
  let medium = ()
  let low = ()
  let other = ()

  for action in actions {
    let normalized = lower(action.at("severity", default: ""))
    if normalized == "critical" { critical.push(action) }
    else if normalized == "high" { high.push(action) }
    else if normalized == "medium" { medium.push(action) }
    else if normalized == "low" { low.push(action) }
    else { other.push(action) }
  }

  // Build result with non-empty groups only.
  let result = ()
  if critical.len() > 0 { result.push(("Critical", critical)) }
  if high.len() > 0 { result.push(("High", high)) }
  if medium.len() > 0 { result.push(("Medium", medium)) }
  if low.len() > 0 { result.push(("Low", low)) }
  if other.len() > 0 { result.push(("Other", other)) }

  result
}


// ---------------------------------------------------------------------------
// Internal: Severity badge
// ---------------------------------------------------------------------------
// Renders a small colored badge for the severity group header rows.

#let _severity-badge(level) = {
  let color = severity-color(level)
  block(
    inset: (x: 0.5em, y: 0.25em),
    radius: 3pt,
    fill: color,
    text(
      font: font-heading,
      size: 9pt,
      weight: "bold",
      fill: white,
      tracking: 0.05em,
      upper(level),
    ),
  )
}


// ---------------------------------------------------------------------------
// Internal: Status indicator
// ---------------------------------------------------------------------------
// Renders the status text with appropriate styling:
//   "Implemented" / "Complete" — green
//   "In Progress" / "Partial"  — amber
//   "Not Started" / "None"     — gray

#let _status-indicator(status) = {
  let normalized = lower(status)
  let color = if normalized in ("implemented", "complete", "done") {
    rgb("#16A34A")
  } else if normalized in ("in progress", "partial", "in-progress") {
    rgb("#D97706")
  } else {
    rgb("#6B7280")
  }

  text(
    size: 9pt,
    weight: "semibold",
    fill: color,
    status,
  )
}


// ---------------------------------------------------------------------------
// Internal: Summary counts bar
// ---------------------------------------------------------------------------
// Renders a row of severity count badges above the table, giving a quick
// overview of how many actions fall in each priority tier.

#let _summary-bar(actions) = {
  let critical = actions.filter(a => lower(a.at("severity", default: "")) == "critical").len()
  let high = actions.filter(a => lower(a.at("severity", default: "")) == "high").len()
  let medium = actions.filter(a => lower(a.at("severity", default: "")) == "medium").len()
  let low = actions.filter(a => lower(a.at("severity", default: "")) == "low").len()

  grid(
    columns: (auto, auto, auto, auto, 1fr, auto),
    column-gutter: 0.3in,
    align: horizon,

    // Critical count
    {
      box(width: 0.5em, height: 0.5em, fill: severity-critical, radius: 1pt)
      h(0.25em)
      text(size: 9pt, weight: "semibold")[Critical: #critical]
    },
    // High count
    {
      box(width: 0.5em, height: 0.5em, fill: severity-high, radius: 1pt)
      h(0.25em)
      text(size: 9pt, weight: "semibold")[High: #high]
    },
    // Medium count
    {
      box(width: 0.5em, height: 0.5em, fill: severity-medium, radius: 1pt)
      h(0.25em)
      text(size: 9pt, weight: "semibold")[Medium: #medium]
    },
    // Low count
    {
      box(width: 0.5em, height: 0.5em, fill: severity-low, radius: 1pt)
      h(0.25em)
      text(size: 9pt, weight: "semibold")[Low: #low]
    },
    // Spacer
    [],
    // Total
    text(size: 9pt, fill: color-footer-text)[#actions.len() total actions],
  )
}


// ---------------------------------------------------------------------------
// Exported: remediation-roadmap-page
// ---------------------------------------------------------------------------
// Renders the full remediation roadmap page (or pages, if the table overflows).
//
// Parameters:
//   classification  — string or none; classification marking for page header
//   actions         — array of dictionaries, each with keys:
//                       severity      (string) — "Critical", "High", "Medium", or "Low"
//                       finding-id    (string) — finding identifier (e.g., "T-001")
//                       finding-name  (string) — short finding title
//                       recommendation (string) — remediation action text
//                       sla           (string) — target timeline (e.g., "7 days")
//                       status        (string) — current status (e.g., "Not Started")
//
// Behavior:
//   - Groups actions by severity: Critical first, then High, Medium, Low.
//   - Within each group, renders a colored severity header row spanning the
//     full table width, followed by the individual action rows.
//   - The table repeats column headers on each continuation page.
//   - If actions is empty, displays a "No remediation actions identified"
//     placeholder message.

#let remediation-roadmap-page(
  classification: none,
  actions: (),
) = {
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
      title: "Remediation Roadmap",
    ),
    footer: report-footer(),
  )[
    // Page heading — uses heading element for TOC outline() discovery.
    #heading(level: 1)[Remediation Roadmap]

    // ---------------------------------------------------------------------
    // Empty state
    // ---------------------------------------------------------------------
    #if actions.len() == 0 {
      v(0.5in)
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
              fill: brand-secondary,
            )[No remediation actions identified]
            v(0.4em)
            text(
              size: 10pt,
              fill: brand-muted,
            )[All findings have been addressed or no recommendations were generated.]
          },
        ),
      )
    } else {
      // -------------------------------------------------------------------
      // Summary counts bar
      // -------------------------------------------------------------------
      _summary-bar(actions)
      v(0.2in)

      // -------------------------------------------------------------------
      // Grouped action table
      // -------------------------------------------------------------------
      // Build table rows: for each severity group, emit a full-width colored
      // header row followed by the individual action rows.
      let groups = _group-by-severity(actions)

      // Column widths: Priority | Finding | Recommendation | SLA | Status
      //                0.8in      1.4in     2.6in           0.7in  0.9in
      // Total: ~6.4in content width within 6.5in printable area.

      let rows = ()
      for (severity, items) in groups {
        let sev-color = severity-color(severity)

        // Severity group header row (spans all 5 columns).
        rows.push(
          table.cell(
            colspan: 5,
            fill: sev-color.lighten(85%),
            inset: (x: 0.5em, y: 0.4em),
          )[
            #_severity-badge(severity)
            #h(0.3em)
            #text(size: 9pt, fill: color-footer-text)[#items.len() action#if items.len() != 1 [s]]
          ]
        )

        // Individual action rows within this group.
        for action in items {
          rows.push(
            table.cell(inset: 0.4em)[
              #text(size: 9pt, fill: sev-color, weight: "bold")[#action.at("finding-id", default: "--")]
            ]
          )
          rows.push(
            table.cell(inset: 0.4em)[
              #text(size: 9pt)[#action.at("finding-name", default: "--")]
            ]
          )
          rows.push(
            table.cell(inset: 0.4em)[
              #text(size: 9pt)[#action.at("recommendation", default: "--")]
            ]
          )
          rows.push(
            table.cell(inset: 0.4em)[
              #text(size: 9pt, weight: "semibold")[#action.at("sla", default: "--")]
            ]
          )
          rows.push(
            table.cell(inset: 0.4em)[
              #_status-indicator(action.at("status", default: "Not Started"))
            ]
          )
        }
      }

      table(
        columns: (0.65in, 1.4in, 2.6in, 0.65in, 0.85in),
        align: (center, left, left, center, center),
        stroke: 0.5pt + color-rule,

        // Repeated column headers for multi-page overflow.
        table.header(
          table.cell(fill: color-header-bg, inset: 0.4em)[
            #text(fill: color-header-text, size: 8pt, weight: "bold")[Priority]
          ],
          table.cell(fill: color-header-bg, inset: 0.4em)[
            #text(fill: color-header-text, size: 8pt, weight: "bold")[Finding]
          ],
          table.cell(fill: color-header-bg, inset: 0.4em)[
            #text(fill: color-header-text, size: 8pt, weight: "bold")[Recommendation]
          ],
          table.cell(fill: color-header-bg, inset: 0.4em)[
            #text(fill: color-header-text, size: 8pt, weight: "bold")[SLA]
          ],
          table.cell(fill: color-header-bg, inset: 0.4em)[
            #text(fill: color-header-text, size: 8pt, weight: "bold")[Status]
          ],
        ),

        // Grouped action rows.
        ..rows,
      )
    }
  ]
}
