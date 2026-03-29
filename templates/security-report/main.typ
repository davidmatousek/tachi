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

// User-configurable overrides (page visibility, custom text).
// Import with renamed bindings to avoid conflicts with report-data.typ's
// show-disclaimer and show-methodology variables.
#import "report-config.typ": show-disclaimer as cfg-show-disclaimer, show-methodology as cfg-show-methodology, custom-disclaimer-text, custom-footer-text

// Page templates — each exports a single page-rendering function.
#import "cover.typ": cover-page
#import "disclaimer.typ": disclaimer-page
#import "toc.typ": toc-page
#import "methodology.typ": methodology-page
#import "scope.typ": scope-page
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
// 2b. Default Values for New Variables (backward compatibility)
// ---------------------------------------------------------------------------
// Variables added in PRD-060 that may be absent in older report-data.typ files.
// The report assembler always generates these, but defaults ensure compilation
// if an older data file is used manually.

// Scope data defaults (empty = graceful degradation in scope.typ).
#let scope-components = if scope-components != none { scope-components } else { () }
#let scope-data-flows = if scope-data-flows != none { scope-data-flows } else { () }
#let scope-trust-boundaries = if scope-trust-boundaries != none { scope-trust-boundaries } else { () }
#let scope-boundary-crossings = if scope-boundary-crossings != none { scope-boundary-crossings } else { () }
#let scope-component-count = if scope-component-count != none { scope-component-count } else { 0 }
#let scope-data-flow-count = if scope-data-flow-count != none { scope-data-flow-count } else { 0 }
#let scope-trust-boundary-count = if scope-trust-boundary-count != none { scope-trust-boundary-count } else { 0 }

// Brand asset defaults (false = text-only fallback).
#let has-logo-primary = if has-logo-primary != none { has-logo-primary } else { false }
#let has-logo-horizontal = if has-logo-horizontal != none { has-logo-horizontal } else { false }
#let logo-primary-path = if logo-primary-path != none { logo-primary-path } else { none }
#let logo-horizontal-path = if logo-horizontal-path != none { logo-horizontal-path } else { none }

// Page visibility — config overrides take precedence over report-data.typ defaults.
#let show-disclaimer = cfg-show-disclaimer
#let show-methodology = cfg-show-methodology

// Set custom footer text state (read by report-footer() in shared.typ).
#if custom-footer-text != none {
  footer-custom-text.update(custom-footer-text)
}


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
  has-logo-primary: has-logo-primary,
  logo-primary-path: logo-primary-path,
)


// --- Page 2: Disclaimer (always, unless show-disclaimer == false) ----------
// Legal disclaimer page with assessment caveats and confidentiality notice.
#if show-disclaimer {
  disclaimer-page(classification: classification, custom-text: custom-disclaimer-text)
}


// --- Page 3: Table of Contents (always) ------------------------------------
// Auto-generated from all level-1 heading elements across all page templates.
#toc-page(classification: classification)


// --- Page 4: Risk Methodology (always, unless show-methodology == false) ---
// Explains STRIDE + AI threat categories, visual risk matrix, and optional
// quantitative scoring / control analysis methodology sections.
#if show-methodology {
  methodology-page(
    classification: classification,
    has-risk-scores: has-risk-scores,
    has-compensating-controls: has-compensating-controls,
  )
}


// --- Page 5: Assessment Scope (always) -------------------------------------
// Components, data flows, and trust boundaries extracted from threats.md.
#scope-page(
  classification: classification,
  components: scope-components,
  data-flows: scope-data-flows,
  trust-boundaries: scope-trust-boundaries,
  boundary-crossings: scope-boundary-crossings,
  component-count: scope-component-count,
  data-flow-count: scope-data-flow-count,
  trust-boundary-count: scope-trust-boundary-count,
)


// --- Page 6: Executive Summary (always) ------------------------------------
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
  full-bleed-page(funnel-image-path, section-name: "Risk Reduction Funnel")
}


// --- Page 4: Baseball Card (conditional) -----------------------------------
// Full-bleed landscape infographic. Only included when the baseball card image
// exists.
#if has-baseball-image {
  full-bleed-page(baseball-image-path, section-name: "Risk Summary Dashboard")
}


// --- Page 5: System Architecture (conditional) -----------------------------
// Full-bleed landscape infographic. Only included when the architecture diagram
// image exists.
#if has-architecture-image {
  full-bleed-page(architecture-image-path, section-name: "System Architecture")
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
