// =============================================================================
// Attack Chain Page: Security Assessment PDF Booklet
// =============================================================================
// Renders a single cross-layer attack chain page with severity badge, MAESTRO
// layer progression, rendered chain diagram (PNG image), condensed narrative,
// and impacted finding IDs footer.
//
// Exported function:
//   attack-chain-page(entry: (:), classification: none)
//
// Usage from main.typ:
//   #import "attack-chain.typ": attack-chain-page
//   #attack-chain-page(entry: entry, classification: classification)
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// 1. Severity Badge (chain-level)
// ---------------------------------------------------------------------------
// Renders a compact colored badge for the chain max severity level.

#let _chain-severity-badge(chain-id, level) = {
  let color = severity-color(level)
  box(
    fill: color,
    radius: 3pt,
    inset: (x: 0.5em, y: 0.2em),
    text(fill: white, size: 8pt, weight: "bold", tracking: 0.05em)[#upper(level) #chain-id],
  )
}


// ---------------------------------------------------------------------------
// 2. Layer Progression Tag
// ---------------------------------------------------------------------------
// Renders the MAESTRO layer progression as a compact inline tag.

#let _layer-progression(layers-str) = {
  if layers-str != "" {
    box(
      fill: luma(240),
      radius: 3pt,
      inset: (x: 0.5em, y: 0.2em),
      text(size: 8pt, weight: "bold", fill: luma(60))[#layers-str],
    )
  }
}


// ---------------------------------------------------------------------------
// 3. Main Export: attack-chain-page
// ---------------------------------------------------------------------------
// Parameters:
//   entry (dict) -- attack chain data with keys: id, title, layers,
//     max-severity, has-image, image-path, narrative, finding-ids
//   classification (string or none) -- text for the classification header bar

#let attack-chain-page(entry: (:), classification: none) = {
  // Page header.
  report-header(classification: classification, title: "Cross-Layer Attack Chain Analysis")

  // Chain heading with severity badge.
  let chain-id = str(entry.at("id", default: ""))
  let max-severity = str(entry.at("max-severity", default: ""))
  let title = str(entry.at("title", default: ""))
  let layers-str = str(entry.at("layers", default: ""))

  v(0.15in)

  // Heading: badge + layer progression + title
  {
    _chain-severity-badge(chain-id, max-severity)
    h(0.3em)
    _layer-progression(layers-str)
    h(0.3em)
    text(font: font-heading, size: 13pt, weight: "bold")[#title]
  }

  v(0.15in)

  // Diagram section — rendered Mermaid PNG showing vertical MAESTRO layer stack.
  let has-img = entry.at("has-image", default: false)
  let img-path = str(entry.at("image-path", default: ""))

  if has-img and img-path != "" {
    align(center,
      image(img-path, height: 3.5in, fit: "contain"),
    )
    v(0.1in)
  }

  // Narrative section — condensed chain walkthrough.
  let narrative = str(entry.at("narrative", default: ""))
  if narrative != "" {
    heading(level: 3, "Attack Progression")
    text(size: 10pt)[#narrative]
    v(0.15in)
  }

  // Impacted finding IDs footer.
  let finding-ids = entry.at("finding-ids", default: ())
  if type(finding-ids) == str {
    finding-ids = if finding-ids != "" { (finding-ids,) } else { () }
  }
  if finding-ids.len() > 0 {
    v(0.1in)
    line(length: 100%, stroke: 0.5pt + luma(200))
    v(0.05in)
    text(size: 8pt, fill: brand-muted)[
      *Impacted Findings:* #finding-ids.join(", ")
    ]
  }
}
