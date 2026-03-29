// =============================================================================
// Full-Bleed Infographic Page Template
// =============================================================================
// Renders a single image filling an entire 16:9 landscape page with zero
// margins and no header/footer chrome. Reused for all infographic types
// (risk-funnel, baseball-card, system-architecture).
//
// Usage from main.typ:
//
//   #import "full-bleed.typ": full-bleed-page
//   #full-bleed-page("assets/risk-funnel.jpg")
//
// The function emits a self-contained #page(...)[...] block that overrides the
// document's default US Letter geometry for exactly one page, then returns to
// the caller's page settings on the next content element.
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// Full-Bleed Page Function
// ---------------------------------------------------------------------------
// Parameters:
//   image-path    (string)       — relative or absolute path to the JPEG/PNG image file.
//   section-name  (content|none) — optional heading text for TOC inclusion.
//
// Behavior:
//   - Sets page dimensions to 11in x 6.1875in (16:9 landscape).
//   - Sets all margins to zero for edge-to-edge rendering.
//   - Suppresses header and footer (no page number, no classification bar).
//   - Renders the image at 100% width and 100% height using fit: "cover" so
//     the image fills the page completely without distortion.
//   - When section-name is provided, emits a phantom heading that is invisible
//     on the page but discoverable by outline() for TOC generation.

#let full-bleed-page(image-path, section-name: none) = {
  page(
    width: 11in,
    height: 6.1875in,
    margin: 0in,
    header: none,
    footer: none,
  )[
    // Phantom heading for TOC — invisible but discoverable by outline().
    // place() removes from layout flow; hide() prevents rendering;
    // text size 0pt prevents heading show rules from consuming space.
    #if section-name != none {
      place(top + left, {
        set text(size: 0pt)
        hide(heading(level: 1)[#section-name])
      })
    }
    #image(image-path, width: 100%, height: 100%, fit: "cover")
  ]
}
