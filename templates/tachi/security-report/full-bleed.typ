// =============================================================================
// Infographic Page Templates: Security Assessment PDF Booklet
// =============================================================================
// Two rendering modes for infographic images:
//
//   1. infographic-page  — Portrait US Letter page with the image sized to fit,
//      standard header/footer chrome, a visible heading for the TOC, and
//      explanatory text filling the remaining space below the image.
//
//   2. full-bleed-page   — Legacy 16:9 landscape page with zero margins and no
//      chrome. Retained for backward compatibility but no longer used by the
//      default page sequence.
//
// Usage from main.typ:
//
//   #import "full-bleed.typ": infographic-page, full-bleed-page
//   #infographic-page(
//     "assets/risk-funnel.jpg",
//     section-name: "Risk Reduction Funnel",
//     classification: "CONFIDENTIAL",
//     description: [Explanatory text about the visualization...],
//   )
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// Portrait Infographic Page (preferred)
// ---------------------------------------------------------------------------
// Renders the infographic image on a standard portrait page with header,
// footer, TOC-visible heading, and explanatory description text.
//
// Parameters:
//   image-path     (string)       — path to the JPEG/PNG image file.
//   section-name   (content|none) — heading text for the page and TOC.
//   classification (string|none)  — classification marking for header bar.
//   description    (content|none) — explanatory text rendered below the image.

#let infographic-page(
  image-path,
  section-name: none,
  classification: none,
  description: none,
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
    // Section heading — visible on page and discoverable by outline() for TOC.
    #if section-name != none {
      heading(level: 1)[#section-name]
    }

    // Image with rounded corners and subtle border, proportionally scaled.
    // Height is constrained so portrait-aspect images (e.g., executive-architecture)
    // don't overflow onto subsequent pages. `fit: "contain"` preserves aspect ratio
    // within the 100% x 7.5in bounding box.
    #block(
      width: 100%,
      height: 7.5in,
      radius: 4pt,
      clip: true,
      stroke: 0.5pt + color-rule,
    )[
      #image(image-path, width: 100%, height: 100%, fit: "contain")
    ]

    // Explanatory text below the image.
    #if description != none {
      v(0.2in)
      block(
        width: 100%,
        inset: (x: 0.4em, y: 0.3em),
      )[
        #text(size: 10pt)[#description]
      ]
    }
  ]
}


// ---------------------------------------------------------------------------
// Full-Bleed Page Function (legacy)
// ---------------------------------------------------------------------------
// Retained for backward compatibility. Renders a 16:9 landscape page with
// zero margins and no header/footer chrome.

#let full-bleed-page(image-path, section-name: none) = {
  page(
    width: 11in,
    height: 6.1875in,
    margin: 0in,
    header: none,
    footer: none,
  )[
    // Phantom heading for TOC — invisible but discoverable by outline().
    #if section-name != none {
      place(top + left, {
        set text(size: 0pt)
        hide(heading(level: 1)[#section-name])
      })
    }
    #image(image-path, width: 100%, height: 100%, fit: "cover")
  ]
}
