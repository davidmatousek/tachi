// =============================================================================
// Risk Methodology Page: Security Assessment PDF Booklet
// =============================================================================
// Renders the risk methodology explanation with up to four sections:
//
//   1. Threat Identification    (always) — STRIDE + AI-specific categories
//   2. Probability x Impact     (always) — 5x5 severity matrix with color coding
//   3. Quantitative Scoring     (conditional: has-risk-scores) — 4D methodology
//   4. Compensating Controls    (conditional: has-compensating-controls) — control analysis
//
// Sections 3 and 4 are conditionally rendered based on which pipeline artifacts
// were available when the report was assembled. This lets the methodology page
// accurately describe only the techniques whose results appear in the report.
//
// Usage in main.typ:
//   #import "methodology.typ": methodology-page
//   #methodology-page(
//     classification: "CONFIDENTIAL",
//     has-risk-scores: true,
//     has-compensating-controls: false,
//   )
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// Internal: Category list item
// ---------------------------------------------------------------------------
// Renders a single threat category as a bold name followed by a description.
// Used by both the STRIDE and AI-specific category lists.

#let _category-item(name, description) = {
  text(size: 10pt)[
    #text(weight: "bold")[#name] --- #description
  ]
}


// ---------------------------------------------------------------------------
// Internal: Section 1 — Threat Identification
// ---------------------------------------------------------------------------
// Static content explaining STRIDE and AI-specific threat categories.

#let _threat-identification() = {
  heading(level: 2)[Threat Identification]

  text(size: 10pt)[
    This assessment uses STRIDE threat modeling combined with AI-specific threat categories to provide comprehensive coverage of both traditional and emerging attack vectors.
  ]

  v(0.15in)

  // STRIDE categories.
  text(
    font: font-heading,
    size: 11pt,
    weight: "bold",
    fill: brand-primary,
  )[STRIDE Categories]
  v(0.3em)

  _category-item("Spoofing", "Impersonating a user, component, or system to gain unauthorized access.")
  v(0.2em)
  _category-item("Tampering", "Unauthorized modification of data in transit, at rest, or in processing.")
  v(0.2em)
  _category-item("Repudiation", "Performing actions without adequate logging or accountability trails.")
  v(0.2em)
  _category-item("Information Disclosure", "Exposing sensitive data to unauthorized parties through leaks or side channels.")
  v(0.2em)
  _category-item("Denial of Service", "Degrading or disrupting system availability through resource exhaustion or abuse.")
  v(0.2em)
  _category-item("Elevation of Privilege", "Gaining higher access rights than authorized through exploitation of trust boundaries.")

  v(0.2in)

  // AI-specific categories.
  text(
    font: font-heading,
    size: 11pt,
    weight: "bold",
    fill: brand-primary,
  )[AI-Specific Categories]
  v(0.3em)

  _category-item("Prompt Injection", "Manipulating AI model behavior through crafted inputs that override system instructions.")
  v(0.2em)
  _category-item("Tool Abuse", "Exploiting AI agent tool access to perform unintended or unauthorized operations.")
  v(0.2em)
  _category-item("Agent Autonomy", "Risks from AI agents acting beyond their intended scope without adequate human oversight.")
  v(0.2em)
  _category-item("Data Poisoning", "Corrupting training data or context to degrade model accuracy or introduce bias.")
  v(0.2em)
  _category-item("Model Theft", "Unauthorized extraction or replication of proprietary model weights or behavior.")
}


// ---------------------------------------------------------------------------
// Internal: Section 2 — Probability x Impact Matrix
// ---------------------------------------------------------------------------
// Renders a 5x5 risk matrix mapping probability (columns) to impact (rows).
// Each cell is colored by the resulting severity level and labeled with the
// severity abbreviation (C, H, M, L).
//
// Matrix mapping follows standard risk assessment practice:
//   - Critical: highest impact + highest probability intersections
//   - Low: lowest impact + lowest probability intersections
//   - Medium/High: diagonal gradation between extremes

#let _risk-matrix() = {
  heading(level: 2)[Probability x Impact Matrix]

  text(size: 10pt)[
    Each identified threat is assessed for probability of occurrence and potential impact. The intersection determines the overall severity rating used throughout this report.
  ]

  v(0.15in)

  // Matrix data: rows are Impact levels (bottom to top: Negligible → Critical),
  // columns are Probability levels (left to right: Rare → Almost Certain).
  // Each cell is (abbreviation, color).
  let L = ("L", severity-low)
  let M = ("M", severity-medium)
  let H = ("H", severity-high)
  let C = ("C", severity-critical)

  // Rows ordered top-to-bottom: Critical impact first (top row).
  let matrix-data = (
    // Impact: Critical
    ("Critical",      (H, H, C, C, C)),
    // Impact: High
    ("High",          (M, M, H, C, C)),
    // Impact: Moderate
    ("Moderate",      (L, M, M, H, H)),
    // Impact: Low
    ("Low",           (L, L, M, M, H)),
    // Impact: Negligible
    ("Negligible",    (L, L, L, M, M)),
  )

  let prob-headers = ("Rare", "Unlikely", "Possible", "Likely", "Almost Certain")

  // Cell dimensions.
  let cell-size = 0.65in
  let label-width = 0.9in

  // Build the table.
  table(
    columns: (label-width, ..prob-headers.map(_ => cell-size)),
    align: center + horizon,
    inset: 0.35em,
    stroke: 0.5pt + white,

    // Top-left corner cell (empty).
    table.cell(fill: color-header-bg)[
      #text(
        fill: color-header-text,
        size: 7pt,
        weight: "bold",
      )[Impact / Probability]
    ],

    // Probability header cells.
    ..prob-headers.map(h =>
      table.cell(fill: color-header-bg)[
        #text(
          fill: color-header-text,
          size: 8pt,
          weight: "bold",
        )[#h]
      ]
    ),

    // Matrix rows (Impact levels, Critical at top).
    ..matrix-data.map(row => {
      let (impact-label, cells) = row
      (
        // Impact label cell.
        table.cell(fill: color-header-bg)[
          #text(
            fill: color-header-text,
            size: 8pt,
            weight: "bold",
          )[#impact-label]
        ],
        // Severity cells.
        ..cells.map(cell => {
          let (abbrev, color) = cell
          table.cell(fill: color)[
            #text(
              fill: white,
              size: 11pt,
              weight: "bold",
            )[#abbrev]
          ]
        }),
      )
    }).flatten(),
  )

  v(0.1in)

  // Legend.
  grid(
    columns: (auto, auto, auto, auto),
    column-gutter: 0.5in,
    align: left + horizon,
    {
      box(width: 0.5em, height: 0.5em, fill: severity-critical, radius: 1pt)
      h(0.25em)
      text(size: 8pt, weight: "semibold")[C = Critical]
    },
    {
      box(width: 0.5em, height: 0.5em, fill: severity-high, radius: 1pt)
      h(0.25em)
      text(size: 8pt, weight: "semibold")[H = High]
    },
    {
      box(width: 0.5em, height: 0.5em, fill: severity-medium, radius: 1pt)
      h(0.25em)
      text(size: 8pt, weight: "semibold")[M = Medium]
    },
    {
      box(width: 0.5em, height: 0.5em, fill: severity-low, radius: 1pt)
      h(0.25em)
      text(size: 8pt, weight: "semibold")[L = Low]
    },
  )
}


// ---------------------------------------------------------------------------
// Internal: Section 3 — Quantitative Risk Scoring (conditional)
// ---------------------------------------------------------------------------
// Explains the 4-dimensional scoring methodology. Only rendered when
// risk-scores.md data was available during report assembly.

#let _quantitative-scoring() = {
  heading(level: 2)[Quantitative Risk Scoring]

  text(size: 10pt)[
    When quantitative data is available, each threat receives a composite risk score derived from four independent dimensions. This provides a more granular risk ranking than severity alone.
  ]

  v(0.15in)

  // Scoring dimensions table.
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
      )[Scoring Dimensions]
      v(0.5em)

      table(
        columns: (1.2in, 0.7in, 1fr),
        align: (left, center, left),
        stroke: 0.5pt + color-rule,
        inset: 0.45em,

        table.header(
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Dimension]
          ],
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Range]
          ],
          table.cell(fill: color-header-bg)[
            #text(fill: color-header-text, size: 9pt, weight: "bold")[Description]
          ],
        ),

        text(size: 9pt, weight: "semibold")[CVSS 3.1 Base Score],
        text(size: 9pt)[0 -- 10],
        text(size: 9pt)[Industry-standard vulnerability severity rating based on attack vector, complexity, and impact.],

        text(size: 9pt, weight: "semibold")[Exploitability],
        text(size: 9pt)[0 -- 10],
        text(size: 9pt)[Ease of exploitation considering required skills, tooling availability, and attack complexity.],

        text(size: 9pt, weight: "semibold")[Scalability],
        text(size: 9pt)[0 -- 10],
        text(size: 9pt)[Potential for automated or mass exploitation across multiple targets or instances.],

        text(size: 9pt, weight: "semibold")[Reachability],
        text(size: 9pt)[0 -- 10],
        text(size: 9pt)[Network accessibility of the vulnerable component from the attacker's perspective.],
      )
    },
  )

  v(0.15in)

  // Composite formula.
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
      )[Composite Score Formula]
      v(0.5em)

      text(size: 10pt)[
        The composite risk score is a weighted average of the four dimensions:
      ]

      v(0.4em)

      align(center,
        text(
          font: font-mono,
          size: 10pt,
          weight: "bold",
        )[Composite = (CVSS × 0.40) + (Exploitability × 0.25) + (Scalability × 0.20) + (Reachability × 0.15)]
      )

      v(0.4em)

      text(size: 9pt, fill: color-footer-text)[
        Weights reflect the relative importance of each dimension: CVSS captures inherent severity (40%), exploitability measures practical attack feasibility (25%), scalability accounts for blast radius (20%), and reachability assesses network exposure (15%).
      ]
    },
  )
}


// ---------------------------------------------------------------------------
// Internal: Section 4 — Compensating Control Analysis (conditional)
// ---------------------------------------------------------------------------
// Explains the control detection and residual risk methodology. Only rendered
// when compensating-controls.md data was available during report assembly.

#let _control-analysis() = {
  heading(level: 2)[Compensating Control Analysis]

  text(size: 10pt)[
    When codebase analysis is available, existing security controls are detected, mapped to identified threats, and evaluated for effectiveness. This provides a residual risk assessment that accounts for defenses already in place.
  ]

  v(0.15in)

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
      )[Analysis Process]
      v(0.5em)

      // Step descriptions.
      grid(
        columns: (auto, 1fr),
        column-gutter: 0.5em,
        row-gutter: 0.5em,
        align: (right + top, left + top),

        text(size: 10pt, weight: "bold", fill: brand-secondary)[1.],
        text(size: 10pt)[
          #text(weight: "semibold")[Control Detection] --- Existing security controls are identified in the codebase through pattern matching, dependency analysis, and configuration review.
        ],

        text(size: 10pt, weight: "bold", fill: brand-secondary)[2.],
        text(size: 10pt)[
          #text(weight: "semibold")[Threat Mapping] --- Detected controls are mapped to specific threats to determine which vulnerabilities have existing mitigations.
        ],

        text(size: 10pt, weight: "bold", fill: brand-secondary)[3.],
        text(size: 10pt)[
          #text(weight: "semibold")[Effectiveness Classification] --- Each control is classified as Found (fully implemented), Partial (incomplete implementation), or Missing (no control detected).
        ],

        text(size: 10pt, weight: "bold", fill: brand-secondary)[4.],
        text(size: 10pt)[
          #text(weight: "semibold")[Residual Risk Calculation] --- Inherent risk scores are adjusted based on control effectiveness to produce residual risk ratings that reflect the actual security posture.
        ],
      )
    },
  )
}


// ---------------------------------------------------------------------------
// Exported: methodology-page
// ---------------------------------------------------------------------------
// Renders the full risk methodology page. Sections 3 (Quantitative Scoring)
// and 4 (Control Analysis) are conditionally included based on data
// availability flags from report-data.typ.
//
// Parameters:
//   classification            — string or none; classification marking for header
//   has-risk-scores           — boolean; true when risk-scores.md was available
//   has-compensating-controls — boolean; true when compensating-controls.md was available

#let methodology-page(
  classification: none,
  has-risk-scores: false,
  has-compensating-controls: false,
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
    ),
    footer: report-footer(),
  )[
    // Page heading — uses heading element for TOC outline() discovery.
    #heading(level: 1)[Risk Methodology]

    // Section 1: Threat Identification (always).
    #_threat-identification()

    #v(0.1in)

    // Section 2: Probability x Impact Matrix (always).
    // Keep the entire matrix together — push to next page if it doesn't fit.
    #block(breakable: false)[
      #_risk-matrix()
    ]

    // Section 3: Quantitative Scoring (conditional).
    #if has-risk-scores {
      v(0.1in)
      _quantitative-scoring()
    }

    // Section 4: Control Analysis (conditional).
    #if has-compensating-controls {
      v(0.1in)
      _control-analysis()
    }
  ]
}
