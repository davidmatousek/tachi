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
//   is-portrait    (bool)         — true for portrait-aspect images (e.g.,
//                                    executive-architecture 912×1168); false
//                                    (default) for landscape 16:9 infographics
//                                    (1376×768) like risk-funnel, baseball-card,
//                                    maestro-stack, maestro-heatmap, etc.
//                                    Landscape images are sized by content
//                                    width so the border hugs the image and
//                                    no dead whitespace surrounds it. Portrait
//                                    images are capped at 7.5in tall to avoid
//                                    page overflow.

#let infographic-page(
  image-path,
  section-name: none,
  classification: none,
  description: none,
  is-portrait: false,
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

    // Image block: orientation-aware sizing so the border hugs the image
    // without leaving dead whitespace above or below.
    //   - Landscape: block fills content width; height derives from image aspect
    //   - Portrait:  block capped at 7.5in tall; width derives from image aspect
    #if is-portrait {
      align(center,
        block(
          radius: 4pt,
          clip: true,
          stroke: 0.5pt + color-rule,
          inset: 0pt,
        )[
          #image(image-path, height: 7.5in)
        ],
      )
    } else {
      block(
        width: 100%,
        radius: 4pt,
        clip: true,
        stroke: 0.5pt + color-rule,
        inset: 0pt,
      )[
        #image(image-path, width: 100%)
      ]
    }

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
