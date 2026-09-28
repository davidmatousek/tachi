// =============================================================================
// Cover Page: Security Assessment PDF Booklet
// =============================================================================
// Renders the first page of the security report: project name, assessment date,
// classification level, finding count summary with severity colors, overall risk
// posture label, and tachi branding.
//
// Usage (from main.typ):
//   #import "cover.typ": cover-page
//   #cover-page(
//     project-name: "ACME Corp Platform",
//     assessment-date: "2026-03-28",
//     classification: "CONFIDENTIAL",   // or none to omit
//     critical-count: 2,
//     high-count: 5,
//     medium-count: 12,
//     low-count: 15,
//     total-findings: 34,
//     risk-posture-level: "high",
//     risk-posture-label: "HIGH RISK",
//   )
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// Exported: cover-page
// ---------------------------------------------------------------------------
// Renders the full cover page. Called once by main.typ.
// The page suppresses the standard report header/footer in favor of its own
// branded layout.

#let cover-page(
  project-name: "Security Assessment",
  assessment-date: "",
  classification: none,
  critical-count: 0,
  high-count: 0,
  medium-count: 0,
  low-count: 0,
  total-findings: 0,
  risk-posture-level: "low",
  risk-posture-label: "LOW RISK",
  has-logo-primary: false,
  logo-primary-path: none,
  logo-primary-dark-path: none,
) = {
  // Risk posture level and label come from report-data.typ (D-3 / F-373
  // K13-posture) — this function no longer derives them from severity
  // counts. Only the color still keys off the level, so the cover never
  // matches strings in Typst; the label itself is rendered verbatim.
  let posture-color = if risk-posture-level == "critical" {
    severity-critical
  } else if risk-posture-level == "high" {
    severity-high
  } else if risk-posture-level == "medium" {
    severity-medium
  } else {
    severity-low
  }

  page(
    width: page-width,
    height: page-height,
    margin: (
      top: margin-top,
      bottom: margin-bottom,
      left: margin-left,
      right: margin-right,
    ),
    fill: brand-primary,
    header: none,
    footer: none,
  )[
    // --- Classification banner (top of page, only if provided) ---------------
    #if classification != none {
      place(top + center, dy: -margin-top + 0.0in,
        block(
          width: page-width,
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
        ),
      )
    }

    // --- Vertically centered main content -----------------------------------
    #align(center + horizon)[
      // Primary logo (dark variant preferred on dark cover).
      #if has-logo-primary {
        let cover-logo = if logo-primary-dark-path != none { logo-primary-dark-path } else { logo-primary-path }
        if cover-logo != none {
          image(cover-logo, width: 2.5in, format: logo-format)
          v(0.3in)
        }
      }

      // Top decorative rule — gold accent
      #line(length: 60%, stroke: 1.5pt + brand-highlight)
      #v(0.4in)

      // Project name — large sans-serif heading, white on dark
      #text(
        font: font-heading,
        size: 28pt,
        weight: "bold",
        fill: white,
        project-name,
      )

      #v(0.15in)

      // Subtitle
      #text(
        font: font-heading,
        size: 14pt,
        weight: "regular",
        fill: white.darken(15%),
      )[Security Assessment Report]

      #v(0.1in)

      // Assessment date
      #text(
        font: font-body,
        size: 12pt,
        fill: white.darken(25%),
        assessment-date,
      )

      #v(0.4in)

      // Bottom decorative rule — gold accent
      #line(length: 60%, stroke: 0.75pt + brand-highlight)

      #v(0.4in)

      // --- Risk posture label ------------------------------------------------
      #block(
        inset: (x: 1.2em, y: 0.6em),
        radius: 4pt,
        fill: posture-color,
        text(
          font: font-heading,
          size: 16pt,
          weight: "bold",
          fill: white,
          tracking: 0.08em,
          risk-posture-label,
        ),
      )

      #v(0.1in)

      // Total findings count below the posture badge
      #text(
        font: font-body,
        size: 11pt,
        fill: white.darken(25%),
      )[#total-findings findings identified]

      #v(0.35in)

      // --- Severity breakdown ------------------------------------------------
      // Four colored count badges in a row on dark background.
      // Badges use severity colors directly — high contrast against dark navy.
      // Medium severity uses a slightly lightened yellow for readability.
      #grid(
        columns: (auto, auto, auto, auto),
        column-gutter: 0.3in,
        // Critical
        block(
          inset: (x: 0.8em, y: 0.5em),
          radius: 3pt,
          fill: severity-critical.transparentize(75%),
          [
            #text(font: font-heading, size: 20pt, weight: "bold", fill: severity-critical.lighten(30%))[#critical-count]
            #v(0.05in)
            #text(font: font-heading, size: 8pt, weight: "semibold", fill: severity-critical.lighten(30%), tracking: 0.05em)[CRITICAL]
          ],
        ),
        // High
        block(
          inset: (x: 0.8em, y: 0.5em),
          radius: 3pt,
          fill: severity-high.transparentize(75%),
          [
            #text(font: font-heading, size: 20pt, weight: "bold", fill: severity-high.lighten(20%))[#high-count]
            #v(0.05in)
            #text(font: font-heading, size: 8pt, weight: "semibold", fill: severity-high.lighten(20%), tracking: 0.05em)[HIGH]
          ],
        ),
        // Medium
        block(
          inset: (x: 0.8em, y: 0.5em),
          radius: 3pt,
          fill: severity-medium.transparentize(75%),
          [
            #text(font: font-heading, size: 20pt, weight: "bold", fill: severity-medium.lighten(10%))[#medium-count]
            #v(0.05in)
            #text(font: font-heading, size: 8pt, weight: "semibold", fill: severity-medium.lighten(10%), tracking: 0.05em)[MEDIUM]
          ],
        ),
        // Low
        block(
          inset: (x: 0.8em, y: 0.5em),
          radius: 3pt,
          fill: severity-low.transparentize(75%),
          [
            #text(font: font-heading, size: 20pt, weight: "bold", fill: severity-low.lighten(30%))[#low-count]
            #v(0.05in)
            #text(font: font-heading, size: 8pt, weight: "semibold", fill: severity-low.lighten(30%), tracking: 0.05em)[LOW]
          ],
        ),
      )
    ]

    // --- tachi branding (bottom of page) ------------------------------------
    // Offset into the bottom margin since the cover page has no footer.
    #place(bottom + center, dy: 0.5in)[
      #line(length: 30%, stroke: 0.5pt + brand-highlight.transparentize(50%))
      #v(0.1in)
      #text(
        font: font-heading,
        size: 9pt,
        fill: white.darken(35%),
      )[Generated by *tachi*]
    ]
  ]
}
