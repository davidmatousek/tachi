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
//   )
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// Internal: Risk posture derivation
// ---------------------------------------------------------------------------
// Determines the overall risk posture label and color from severity counts.
// Logic: highest non-zero severity level determines the posture.
//   critical > 0  =>  "CRITICAL RISK"  (severity-critical color)
//   high > 0      =>  "HIGH RISK"      (severity-high color)
//   medium > 0    =>  "MODERATE RISK"  (severity-medium color)
//   otherwise     =>  "LOW RISK"       (severity-low color)

#let risk-posture(critical, high, medium, low) = {
  if critical > 0 {
    (label: "CRITICAL RISK", color: severity-critical)
  } else if high > 0 {
    (label: "HIGH RISK", color: severity-high)
  } else if medium > 0 {
    (label: "MODERATE RISK", color: severity-medium)
  } else {
    (label: "LOW RISK", color: severity-low)
  }
}


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
  has-logo-primary: false,
  logo-primary-path: none,
) = {
  // Derive risk posture from severity counts.
  let posture = risk-posture(critical-count, high-count, medium-count, low-count)

  page(
    width: page-width,
    height: page-height,
    margin: (
      top: margin-top,
      bottom: margin-bottom,
      left: margin-left,
      right: margin-right,
    ),
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
      // Primary logo (when available) above the decorative rule.
      #if has-logo-primary and logo-primary-path != none {
        image(logo-primary-path, width: 2.5in, format: logo-format)
        v(0.3in)
      }

      // Top decorative rule
      #line(length: 60%, stroke: 1.5pt + color-header-bg)
      #v(0.4in)

      // Project name — large sans-serif heading
      #text(
        font: font-heading,
        size: 28pt,
        weight: "bold",
        fill: color-header-bg,
        project-name,
      )

      #v(0.15in)

      // Subtitle
      #text(
        font: font-heading,
        size: 14pt,
        weight: "regular",
        fill: color-footer-text,
      )[Security Assessment Report]

      #v(0.1in)

      // Assessment date
      #text(
        font: font-body,
        size: 12pt,
        fill: color-footer-text,
        assessment-date,
      )

      #v(0.4in)

      // Bottom decorative rule
      #line(length: 60%, stroke: 0.75pt + color-rule)

      #v(0.4in)

      // --- Risk posture label ------------------------------------------------
      #block(
        inset: (x: 1.2em, y: 0.6em),
        radius: 4pt,
        fill: posture.color,
        text(
          font: font-heading,
          size: 16pt,
          weight: "bold",
          fill: white,
          tracking: 0.08em,
          posture.label,
        ),
      )

      #v(0.1in)

      // Total findings count below the posture badge
      #text(
        font: font-body,
        size: 11pt,
        fill: color-footer-text,
      )[#total-findings findings identified]

      #v(0.35in)

      // --- Severity breakdown ------------------------------------------------
      // Four colored count badges in a row: Critical, High, Medium, Low.
      #grid(
        columns: (auto, auto, auto, auto),
        column-gutter: 0.3in,
        // Critical
        block(
          inset: (x: 0.8em, y: 0.5em),
          radius: 3pt,
          fill: severity-critical.lighten(88%),
          [
            #text(font: font-heading, size: 20pt, weight: "bold", fill: severity-critical)[#critical-count]
            #v(0.05in)
            #text(font: font-heading, size: 8pt, weight: "semibold", fill: severity-critical, tracking: 0.05em)[CRITICAL]
          ],
        ),
        // High
        block(
          inset: (x: 0.8em, y: 0.5em),
          radius: 3pt,
          fill: severity-high.lighten(88%),
          [
            #text(font: font-heading, size: 20pt, weight: "bold", fill: severity-high)[#high-count]
            #v(0.05in)
            #text(font: font-heading, size: 8pt, weight: "semibold", fill: severity-high, tracking: 0.05em)[HIGH]
          ],
        ),
        // Medium
        block(
          inset: (x: 0.8em, y: 0.5em),
          radius: 3pt,
          fill: severity-medium.lighten(88%),
          [
            #text(font: font-heading, size: 20pt, weight: "bold", fill: severity-medium)[#medium-count]
            #v(0.05in)
            #text(font: font-heading, size: 8pt, weight: "semibold", fill: severity-medium, tracking: 0.05em)[MEDIUM]
          ],
        ),
        // Low
        block(
          inset: (x: 0.8em, y: 0.5em),
          radius: 3pt,
          fill: severity-low.lighten(88%),
          [
            #text(font: font-heading, size: 20pt, weight: "bold", fill: severity-low)[#low-count]
            #v(0.05in)
            #text(font: font-heading, size: 8pt, weight: "semibold", fill: severity-low, tracking: 0.05em)[LOW]
          ],
        ),
      )
    ]

    // --- tachi branding (bottom of page) ------------------------------------
    #place(bottom + center, dy: 0.0in)[
      #line(length: 30%, stroke: 0.5pt + color-rule)
      #v(0.15in)
      #if has-logo-primary and logo-primary-path != none {
        image(logo-primary-path, width: 1in, format: logo-format)
      } else {
        text(
          font: font-heading,
          size: 9pt,
          fill: color-footer-text,
        )[Generated by *tachi*]
      }
    ]
  ]
}
