// =============================================================================
// Attack Path Page: Security Assessment PDF Booklet
// =============================================================================
// Renders a single attack path analysis page with severity badge, diagram
// (rendered PNG image), narrative explanation, and remediation steps.
//
// Exported function:
//   attack-path-page(entry: (:), classification: none)
//
// Usage from main.typ:
//   #import "attack-path.typ": attack-path-page
//   #attack-path-page(entry: entry, classification: classification)
// =============================================================================

#import "shared.typ": *


// ---------------------------------------------------------------------------
// 1. Severity Badge
// ---------------------------------------------------------------------------
// Renders a compact colored badge for the finding ID + severity level.

#let _attack-severity-badge(id, level) = {
  let color = severity-color(level)
  box(
    fill: color,
    radius: 3pt,
    inset: (x: 0.5em, y: 0.2em),
    text(fill: white, size: 8pt, weight: "bold", tracking: 0.05em)[#upper(level) #id],
  )
}


// ---------------------------------------------------------------------------
// 2. Main Export: attack-path-page
// ---------------------------------------------------------------------------
// Parameters:
//   entry (dict) -- attack tree data with keys: id, component, severity,
//     title, has-image, image-path, narrative, remediation
//   classification (string or none) -- text for the classification header bar

#let attack-path-page(entry: (:), classification: none) = {
  // Page header.
  report-header(classification: classification, title: "Attack Path Analysis")

  // Finding heading with severity badge.
  let finding-id = str(entry.at("id", default: ""))
  let severity = str(entry.at("severity", default: ""))
  let title = str(entry.at("title", default: ""))

  v(0.15in)

  // Heading: badge + title
  {
    _attack-severity-badge(finding-id, severity)
    h(0.3em)
    text(font: font-heading, size: 14pt, weight: "bold")[ --- #title]
  }

  v(0.1in)

  // Component label
  let component = str(entry.at("component", default: ""))
  if component != "" {
    text(size: 9pt, fill: brand-muted)[*Component:* #component]
    v(0.1in)
  }

  let has-img = entry.at("has-image", default: false)
  let img-path = str(entry.at("image-path", default: ""))

  if has-img and img-path != "" {
    align(center,
      image(img-path, width: 100%, fit: "contain"),
    )
  }

  v(0.15in)

  // Narrative section.
  let narrative = str(entry.at("narrative", default: ""))
  if narrative != "" {
    text(size: 10pt)[#narrative]
    v(0.15in)
  }

  // Remediation section.
  // Coerce to array defensively: a bare string would iterate character-by-character.
  let remediation = entry.at("remediation", default: ())
  if type(remediation) == str {
    remediation = if remediation != "" { (remediation,) } else { () }
  }
  if remediation.len() > 0 {
    heading(level: 3, "Remediation Steps")
    for step in remediation {
      [- #text(size: 10pt)[#step]]
    }
  }
}
