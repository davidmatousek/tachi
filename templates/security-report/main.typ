// =============================================================================
// Main Orchestrator: Security Assessment PDF Booklet
// =============================================================================
// Central assembly file that imports all page templates and report data, then
// conditionally includes each page based on data availability flags.
//
// This file is the Typst compilation entry point:
//   typst compile main.typ output.pdf
//
// All rendering logic lives in the individual page modules. This file is pure
// orchestration: apply global styles, then call each page function in sequence.
//
// Data contract: report-data.typ is generated at runtime by the report
// assembler agent. It exports boolean flags (has-*) and data variables that
// drive page inclusion and content rendering.
// =============================================================================


// ---------------------------------------------------------------------------
// 1. Imports
// ---------------------------------------------------------------------------

// Shared design tokens: colors, fonts, page geometry, header/footer functions.
#import "shared.typ": *

// Runtime-generated data file with all extracted report variables.
#import "report-data.typ": *

// Page templates — each exports a single page-rendering function.
#import "cover.typ": cover-page
#import "executive-summary.typ": executive-summary-page
#import "full-bleed.typ": full-bleed-page
#import "findings-detail.typ": findings-detail-page
#import "control-coverage.typ": control-coverage-page
#import "remediation-roadmap.typ": remediation-roadmap-page


// ---------------------------------------------------------------------------
// 2. Global Style Application
// ---------------------------------------------------------------------------
// Apply shared typography (fonts, heading styles) and default page geometry
// (US Letter portrait, standard margins) as document-level defaults.
// Individual page functions override these when needed (e.g., full-bleed
// pages switch to landscape with zero margins).

#show: apply-typography
#show: apply-page-setup


// ---------------------------------------------------------------------------
// 3. Page Sequence
// ---------------------------------------------------------------------------
// Pages are emitted in fixed order. Conditional pages are gated by boolean
// flags exported from report-data.typ. Each page function that wraps its own
// #page(...)[...] block automatically starts a new page. The findings-detail
// function renders inline content, so it is wrapped in an explicit page block.


// --- Page 1: Cover (always) ------------------------------------------------
// The cover page is always rendered — threats.md is a required input.
#cover-page(
  project-name: project-name,
  assessment-date: assessment-date,
  classification: classification,
  critical-count: critical-count,
  high-count: high-count,
  medium-count: medium-count,
  low-count: low-count,
  total-findings: total-findings,
)


// --- Page 2: Executive Summary (always) ------------------------------------
// Renders in rich mode when executive-narrative is available, otherwise
// falls back to minimal mode with severity counts and component distribution.
#executive-summary-page(
  classification: classification,
  critical-count: critical-count,
  high-count: high-count,
  medium-count: medium-count,
  low-count: low-count,
  total-findings: total-findings,
  executive-narrative: executive-narrative,
  component-distribution: component-distribution,
)


// --- Page 3: Risk Reduction Funnel (conditional) ---------------------------
// Full-bleed landscape infographic. Only included when the funnel image exists.
#if has-funnel-image {
  full-bleed-page(funnel-image-path)
}


// --- Page 4: Baseball Card (conditional) -----------------------------------
// Full-bleed landscape infographic. Only included when the baseball card image
// exists.
#if has-baseball-image {
  full-bleed-page(baseball-image-path)
}


// --- Page 5: System Architecture (conditional) -----------------------------
// Full-bleed landscape infographic. Only included when the architecture diagram
// image exists.
#if has-architecture-image {
  full-bleed-page(architecture-image-path)
}


// --- Page 6: Findings Detail (always) --------------------------------------
// The findings-detail-page function renders content directly (no internal page
// wrapper), so we provide the page block with standard geometry and footer.
// The function renders its own header via report-header() inline.
#page(
  width: page-width,
  height: page-height,
  margin: (
    top: margin-top,
    bottom: margin-bottom,
    left: margin-left,
    right: margin-right,
  ),
  footer: report-footer(),
)[
  #findings-detail-page(
    classification: classification,
    tier: data-source-tier,
    findings: findings,
  )
]


// --- Page 7: Control Coverage (conditional) --------------------------------
// Only rendered when compensating-controls.md data is available.
#if has-compensating-controls {
  control-coverage-page(
    classification: classification,
    coverage-matrix: coverage-matrix,
    controls: controls,
    summary: coverage-summary,
  )
}


// --- Page 8: Remediation Roadmap (conditional) -----------------------------
// Rendered when compensating-controls.md provides recommendations OR when
// threat-report.md contains remediation data.
#if has-compensating-controls or (has-threat-report and remediation-actions != none and remediation-actions.len() > 0) {
  remediation-roadmap-page(
    classification: classification,
    actions: remediation-actions,
  )
}
