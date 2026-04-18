// =============================================================================
// Coverage Attestation Section: Security Assessment PDF Booklet
// =============================================================================
// Renders the F-B coverage attestation section — the downstream consumer of the
// F-A1 taxonomy catalogs and the F-A2 per-finding source_attribution contract.
// Produces 5 per-framework matrix pages (Phase 4: owasp, mitre-attack,
// mitre-atlas, nist-ai-rmf, cwe) classifying each catalog item as
// Covered / Partial / Gap, followed by a single paginated per-finding
// attribution table (Phase 5).
//
// Feature reference: F-B / Feature 194 (Coverage Attestation Report Section).
// Data contract: consumes the `per-finding-rows` and `per-framework-aggregates`
// arrays declared in report-data.typ by scripts/extract-report-data.py — see
// specs/194-coverage-attestation-report-section/contracts/typst-data-contract.md
// for the full producer/consumer obligations.
//
// Gating: main.typ includes this page only when `has-source-attribution == true`
// AND `per-finding-rows.len() > 0` (belt-and-suspenders gate mirroring the
// Feature 141 `has-attack-chains` precedent at main.typ:246).
//
// Visual treatment: per the architect fallback memo at
// specs/194-coverage-attestation-report-section/q5-visual-treatment-architect-fallback.md,
// Covered / Partial / Gap classifications are redundantly encoded via both
// icon shape (✓ / ◐ / ✗) and background fill (#E8F5E9 / #FFF8E1 / #FFEBEE)
// to remain distinguishable under any color-vision deficiency (WCAG AA).
//
// Exported function:
//   coverage-attestation-page(per-finding-rows: (), per-framework-aggregates: ())
//
// Usage from main.typ:
//   #import "coverage-attestation.typ": coverage-attestation-page
//   #coverage-attestation-page(
//     per-finding-rows: per-finding-rows,
//     per-framework-aggregates: per-framework-aggregates,
//   )
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// 1. Framework Display Names
// ---------------------------------------------------------------------------
// Maps the framework enum value (kebab-case, matches schemas/taxonomy/*.yaml
// file stem) to a human-readable display title shown in page headers.

#let _framework-display-name(framework) = {
  if framework == "owasp" { "OWASP LLM Top 10" }
  else if framework == "mitre-attack" { "MITRE ATT&CK" }
  else if framework == "mitre-atlas" { "MITRE ATLAS" }
  else if framework == "nist-ai-rmf" { "NIST AI RMF" }
  else if framework == "cwe" { "CWE Top 25" }
  else { framework }
}


// ---------------------------------------------------------------------------
// 2. Classification Visual Tokens (WCAG AA — architect fallback memo)
// ---------------------------------------------------------------------------
// Redundant icon + background-fill encoding keeps each classification
// distinguishable in grayscale and under color-vision deficiency.
//   Covered — green check  ✓ + light green fill  #E8F5E9
//   Partial — yellow half  ◐ + light amber fill  #FFF8E1
//   Gap     — red X mark   ✗ + light red fill    #FFEBEE
// Plain text weight (no bold, no italic) per memo section "Visual-Treatment
// Recommendations".

#let _classification-style(classification) = {
  if classification == "covered" {
    (
      icon: "✓",
      fill: rgb("#E8F5E9"),
      icon-color: rgb("#1B5E20"),  // dark green — accessible against light fill
    )
  } else if classification == "partial" {
    (
      icon: "◐",
      fill: rgb("#FFF8E1"),
      icon-color: rgb("#795548"),  // dark amber — accessible against light fill
    )
  } else {
    // Default: gap
    (
      icon: "✗",
      fill: rgb("#FFEBEE"),
      icon-color: rgb("#B71C1C"),  // dark red — accessible against light fill
    )
  }
}


// ---------------------------------------------------------------------------
// 3. Item Badge
// ---------------------------------------------------------------------------
// Renders a single framework item as a pill-shaped badge: icon prefix + id,
// with classification-specific fill. Plain text weight. Flown inline with
// small h() separators by the caller.

#let _item-badge(item) = {
  let classification = str(item.at("classification", default: "gap"))
  let id = str(item.at("id", default: ""))
  let style = _classification-style(classification)

  box(
    fill: style.fill,
    radius: 3pt,
    inset: (x: 0.4em, y: 0.2em),
    text(size: 8pt, weight: "regular", fill: brand-dark)[
      #text(fill: style.icon-color, weight: "bold")[#style.icon] #id
    ],
  )
}


// ---------------------------------------------------------------------------
// 4. Item Group
// ---------------------------------------------------------------------------
// Renders a subheading ("Covered (K)" / "Partial (P)" / "Gap (G)") followed
// by a flowing wrap of item badges. Typst `wrap` naturally flows inline
// elements to the next line when the line width is exceeded.

#let _item-group(classification-label, items, count) = {
  text(
    font: font-heading,
    size: 11pt,
    weight: "semibold",
    fill: brand-primary,
  )[#classification-label (#count)]
  v(0.2em)

  if count == 0 {
    text(size: 9pt, fill: brand-muted, style: "italic")[
      No #lower(classification-label) items on this framework.
    ]
  } else {
    // Inline flow: render each badge with a small horizontal separator.
    // Typst wraps to next line when line width exceeded.
    let rendered = items.map(item => _item-badge(item))
    for (idx, badge) in rendered.enumerate() {
      badge
      if idx < rendered.len() - 1 {
        h(0.3em)
      }
    }
  }
  v(0.25in)
}


// ---------------------------------------------------------------------------
// 5. Per-Framework Page Body
// ---------------------------------------------------------------------------
// Renders the body of a single per-framework matrix page:
//   - Heading (framework display name)
//   - Coverage summary line (FR-008 — equal visual weight for all 3 counts)
//   - 3 item groups (Covered / Partial / Gap) with flowing badge wrap
//
// Called inside a page() wrapper from the main coverage-attestation-page
// function so each framework gets its own full page (5 pages total, always
// rendered when the gate is true per Q4 resolution / US2 AC-1).

#let _framework-page-body(aggregate) = {
  let framework = str(aggregate.at("framework", default: ""))
  let yaml-count = int(aggregate.at("yaml-record-count", default: 0))
  let covered-count = int(aggregate.at("covered-count", default: 0))
  let partial-count = int(aggregate.at("partial-count", default: 0))
  let gap-count = int(aggregate.at("gap-count", default: 0))
  let coverage-pct = str(aggregate.at("coverage-percentage", default: "N/A"))
  let items = aggregate.at("items", default: ())

  let display-name = _framework-display-name(framework)

  // Page heading — uses heading element for TOC outline() discovery.
  heading(level: 1, "Coverage Attestation — " + display-name)

  v(0.1in)

  // Coverage summary line — FR-008: equal visual weight for Partial count.
  // All three counts and the percentage share the same 10pt size and
  // regular weight; only the numeric values differ. Separator is U+00B7
  // MIDDLE DOT "·" per spec.
  text(size: 10pt)[
    *Covered:* #covered-count / #yaml-count = #coverage-pct
    #h(0.4em) · #h(0.4em)
    *Partial:* #partial-count
    #h(0.4em) · #h(0.4em)
    *Gap:* #gap-count
  ]

  v(0.25in)

  // Partition: split items into 3 groups by classification. Preserves
  // YAML iteration order within each group.
  let covered-items = items.filter(it => str(it.at("classification", default: "gap")) == "covered")
  let partial-items = items.filter(it => str(it.at("classification", default: "gap")) == "partial")
  let gap-items = items.filter(it => str(it.at("classification", default: "gap")) == "gap")

  _item-group("Covered", covered-items, covered-count)
  _item-group("Partial", partial-items, partial-count)
  _item-group("Gap", gap-items, gap-count)
}


// ---------------------------------------------------------------------------
// 6. Per-Finding Attribution Table (Phase 5 / US1)
// ---------------------------------------------------------------------------
// Renders the per-finding attribution table as a single paginated table with
// 7 columns and a bold repeating header. Typst native row-break on `table`
// combined with `table.header(repeat: true)` paginates the long table across
// multiple pages while keeping the header visible on each.
//
// Per FR-006: every finding produces one row, including findings with all
// 4 ref arrays empty (row renders with blank ref cells).
// Per FR-005 + architect L-2: mitre-attack + mitre-atlas merge into the MITRE
// column with per-ref prefix — the aggregator (extract-report-data.py) has
// already applied the prefix, so this template just renders the prefixed IDs.
// Per spec: `primary` refs render bold; `related` / `derived` render plain.

#let _ref-cell(refs) = {
  // Render a list of {id, relationship} refs inline, separated by small gaps.
  // Empty array renders as blank cell.
  if type(refs) != array or refs.len() == 0 {
    // Blank cell — still visible per FR-006 (row renders) but contains no ink.
    return text(size: 8pt, fill: brand-muted)[—]
  }

  // Build the per-cell content: each ref is its id, bold when primary,
  // plain when related or derived. Refs are separated by a comma + small
  // space to allow the cell to wrap naturally.
  let parts = refs.map(ref => {
    let id = str(ref.at("id", default: ""))
    let relationship = str(ref.at("relationship", default: "primary"))
    if relationship == "primary" {
      text(font: font-mono, size: 7pt, weight: "bold", fill: brand-dark)[#id]
    } else {
      text(font: font-mono, size: 7pt, weight: "regular", fill: brand-dark)[#id]
    }
  })

  // Join with linebreaks so multiple refs stack vertically inside the cell —
  // better pagination behavior than horizontal wrapping in narrow columns.
  for (idx, part) in parts.enumerate() {
    part
    if idx < parts.len() - 1 {
      linebreak()
    }
  }
}


#let _severity-badge-compact(level) = {
  // Compact severity badge for the per-finding table.
  let color = severity-color(level)
  box(
    fill: color,
    radius: 3pt,
    inset: (x: 0.4em, y: 0.1em),
    text(fill: white, size: 7pt, weight: "bold", tracking: 0.05em)[#upper(level)],
  )
}


#let _per-finding-table(per-finding-rows) = {
  // Column widths sum to 6.5in (portrait US Letter content width).
  //   Finding ID : 0.8in (monospace, 8pt, stable)
  //   Title      : 1.6in (serif, 9pt, wraps)
  //   Severity   : 0.7in (badge)
  //   OWASP refs : 0.9in
  //   MITRE refs : 1.1in (wider — carries ATT&CK: / ATLAS: prefix)
  //   NIST refs  : 0.8in
  //   CWE refs   : 0.6in
  table(
    columns: (0.8in, 1.6in, 0.7in, 0.9in, 1.1in, 0.8in, 0.6in),
    align: (left + horizon, left + horizon, center + horizon, left + horizon, left + horizon, left + horizon, left + horizon),
    stroke: 0.5pt + color-rule,
    inset: 0.4em,

    // Header row — repeats on continuation pages.
    table.header(
      table.cell(fill: brand-primary)[#text(font: font-heading, size: 9pt, fill: white, weight: "bold")[Finding ID]],
      table.cell(fill: brand-primary)[#text(font: font-heading, size: 9pt, fill: white, weight: "bold")[Title]],
      table.cell(fill: brand-primary)[#text(font: font-heading, size: 9pt, fill: white, weight: "bold")[Severity]],
      table.cell(fill: brand-primary)[#text(font: font-heading, size: 9pt, fill: white, weight: "bold")[OWASP]],
      table.cell(fill: brand-primary)[#text(font: font-heading, size: 9pt, fill: white, weight: "bold")[MITRE]],
      table.cell(fill: brand-primary)[#text(font: font-heading, size: 9pt, fill: white, weight: "bold")[NIST]],
      table.cell(fill: brand-primary)[#text(font: font-heading, size: 9pt, fill: white, weight: "bold")[CWE]],
    ),

    // Data rows — one per finding in input order (no re-sort; preserves the
    // aggregator's input-order contract from build_per_finding_rows).
    ..per-finding-rows.map(row => {
      let id = str(row.at("id", default: "—"))
      let title = str(row.at("title", default: ""))
      let severity = str(row.at("severity", default: ""))
      let owasp = row.at("owasp-refs", default: ())
      let mitre = row.at("mitre-refs", default: ())
      let nist = row.at("nist-refs", default: ())
      let cwe = row.at("cwe-refs", default: ())

      (
        text(font: font-mono, size: 8pt)[#id],
        text(size: 9pt)[#title],
        _severity-badge-compact(severity),
        _ref-cell(owasp),
        _ref-cell(mitre),
        _ref-cell(nist),
        _ref-cell(cwe),
      )
    }).flatten(),
  )
}


// ---------------------------------------------------------------------------
// 7. Main Export: coverage-attestation-page
// ---------------------------------------------------------------------------
// Parameters:
//   per-finding-rows (array of dicts) -- one record per finding with id, title,
//     severity, owasp-refs, mitre-refs, nist-refs, cwe-refs (each a list of
//     {id, relationship} dicts). Contract Declaration 2.
//   per-framework-aggregates (array of dicts) -- exactly 5 records in fixed
//     order (owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe) with framework,
//     yaml-record-count, covered-count, partial-count, gap-count,
//     coverage-percentage, items. Contract Declaration 3.
//
// Behavior:
//   Phase 4 (T028-T030): Iterates per-framework-aggregates and renders one
//   page per framework (5 pages, always rendered when the gate is true per
//   Q4 / US2 AC-1). MITRE split preserved: mitre-attack and mitre-atlas
//   render as 2 SEPARATE pages (architect L-2 — merge applies to per-finding
//   column only).
//
//   Phase 5 (T037): Renders the per-finding attribution table on its own
//   page after the 5 framework pages. Typst native row-break paginates long
//   tables; table.header(repeat: true) keeps the column header visible on
//   continuation pages.

#let coverage-attestation-page(per-finding-rows: (), per-framework-aggregates: ()) = {
  // Phase 4: One page per framework in per-framework-aggregates.
  // Always 5 pages when invoked (gated by main.typ's conditional block).
  for aggregate in per-framework-aggregates {
    page(
      width: page-width,
      height: page-height,
      margin: (
        top: margin-top,
        bottom: margin-bottom,
        left: margin-left,
        right: margin-right,
      ),
      header: report-header(title: "Coverage Attestation — " + _framework-display-name(str(aggregate.at("framework", default: "")))),
      footer: report-footer(),
    )[
      #_framework-page-body(aggregate)
    ]
  }

  // Phase 5: Per-finding attribution table on its own page(s).
  // Only render when there is at least one row (belt-and-suspenders —
  // main.typ already gates on per-finding-rows.len() > 0).
  if per-finding-rows.len() > 0 {
    page(
      width: page-width,
      height: page-height,
      margin: (
        top: margin-top,
        bottom: margin-bottom,
        left: margin-left,
        right: margin-right,
      ),
      header: report-header(title: "Per-Finding Source Attribution"),
      footer: report-footer(),
    )[
      #heading(level: 1, "Per-Finding Source Attribution")

      #text(size: 10pt)[
        The following table lists every finding in input order alongside its
        cited framework references. Primary citations render in *bold*; related
        and derived citations render in plain weight. MITRE references are
        prefixed with #raw("ATT&CK:") or #raw("ATLAS:") to distinguish the
        originating taxonomy within the merged MITRE column. Empty cells
        indicate the finding carries no citations for that framework.
      ]

      #v(0.2in)

      #_per-finding-table(per-finding-rows)

      #v(0.15in)

      #align(right,
        text(
          font: font-body,
          size: 7pt,
          fill: color-footer-text,
        )[
          #per-finding-rows.len() finding#if per-finding-rows.len() != 1 [s] |
          Input order preserved
        ],
      )
    ]
  }
}
