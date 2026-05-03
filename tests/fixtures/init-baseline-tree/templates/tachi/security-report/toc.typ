// =============================================================================
// Table of Contents Page: Security Assessment PDF Booklet
// =============================================================================
// Renders an auto-generated table of contents from all level-1 headings in the
// document. Typst's `outline()` function handles dot leaders, page numbers,
// and heading discovery automatically.
//
// Usage in main.typ:
//   #import "toc.typ": toc-page
//   #toc-page(classification: "CONFIDENTIAL")
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// Exported: toc-page
// ---------------------------------------------------------------------------
// Renders the Table of Contents page. The outline is auto-generated from all
// level-1 headings across the entire document using Typst's built-in outline()
// function, which provides dot leaders and page numbers automatically.
//
// Parameters:
//   classification — string or none; classification marking for header

#let toc-page(classification: none) = {
  page(
    width: page-width,
    height: page-height,
    margin: (
      top: margin-top,
      bottom: margin-bottom,
      left: margin-left,
      right: margin-right,
    ),
    header: report-header(classification: classification),
    footer: report-footer(),
  )[
    #heading(level: 1)[Table of Contents]
    #outline(title: none, indent: auto, depth: 1)
  ]
}
