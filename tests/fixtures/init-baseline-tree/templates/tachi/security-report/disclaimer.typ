// =============================================================================
// Disclaimer Page: Security Assessment PDF Booklet
// =============================================================================
// Renders a legal disclaimer page with four standard notice sections:
//
//   1. Assessment Notice  — Automated methodology caveat
//   2. Scope Limitation   — Boundary and coverage limitations
//   3. Recommendation     — Complement with manual review
//   4. Confidentiality    — Distribution restrictions
//
// If `custom-text` is provided, all four default sections are replaced with
// the custom content. This supports organizational legal requirements without
// modifying the template file itself.
//
// Usage in main.typ:
//   #import "disclaimer.typ": disclaimer-page
//   #disclaimer-page(
//     classification: "CONFIDENTIAL",
//     custom-text: none,  // none = use 4 default sections
//   )
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// Internal: Notice section block
// ---------------------------------------------------------------------------
// Renders a single notice section with a Vermillion left border accent,
// Tachi Indigo title, and body text. Uses brand-accent (Vermillion) via
// color-classification-bg for the left border and brand-primary (Tachi Indigo)
// for the heading.
//
// Parameters:
//   title — string; the notice section heading
//   body  — content; the notice body text

#let _notice-section(title, body) = {
  block(
    width: 100%,
    inset: (left: 0.8em, top: 0.6em, bottom: 0.6em, right: 0.6em),
    stroke: (left: 3pt + color-classification-bg),
    {
      text(
        font: font-heading,
        size: 12pt,
        weight: "bold",
        fill: brand-primary,
      )[#title]
      v(0.4em)
      text(size: 10pt)[#body]
    },
  )
}


// ---------------------------------------------------------------------------
// Internal: Default disclaimer sections
// ---------------------------------------------------------------------------
// Renders the four standard notice sections when no custom text is provided.

#let _default-sections() = {
  _notice-section(
    "Assessment Notice",
    [This security assessment was generated using tachi, an automated threat modeling toolkit. The analysis applies STRIDE methodology and AI-specific threat categories to the provided architecture description. Results reflect the automated analysis and should be validated by qualified security professionals.],
  )

  v(0.15in)

  _notice-section(
    "Scope Limitation",
    [This assessment is limited to the architecture description provided at the time of analysis. It does not cover runtime behavior, implementation-level vulnerabilities, or threats arising from future system changes. The assessment scope is defined in the Assessment Scope section of this report.],
  )

  v(0.15in)

  _notice-section(
    "Recommendation",
    [This automated assessment should complement, not replace, manual security review by qualified professionals. Organizations should conduct periodic penetration testing, code review, and architecture review in addition to automated threat modeling.],
  )

  v(0.15in)

  _notice-section(
    "Confidentiality",
    [This document contains sensitive security assessment information. Distribution should be limited to authorized personnel with a legitimate need to review the security posture of the assessed system. Do not share externally without appropriate authorization.],
  )
}


// ---------------------------------------------------------------------------
// Exported: disclaimer-page
// ---------------------------------------------------------------------------
// Renders the full disclaimer page.
//
// Parameters:
//   classification — string or none; classification marking for page header
//   custom-text    — string/content or none; if not none, replaces all four
//                    default notice sections with the provided content

#let disclaimer-page(
  classification: none,
  custom-text: none,
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
    ),
    footer: report-footer(),
  )[
    // Page heading — uses heading element for TOC outline() discovery.
    #heading(level: 1)[Disclaimer]

    // -------------------------------------------------------------------
    // Custom text override: replaces all default sections
    // -------------------------------------------------------------------
    #if custom-text != none {
      _notice-section("Disclaimer", custom-text)
    } else {
      // -----------------------------------------------------------------
      // Default: four standard notice sections
      // -----------------------------------------------------------------
      _default-sections()
    }
  ]
}
