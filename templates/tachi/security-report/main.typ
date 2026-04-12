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
#import "full-bleed.typ": infographic-page, full-bleed-page
#import "findings-detail.typ": findings-detail-page
#import "maestro-findings.typ": maestro-findings-page
#import "control-coverage.typ": control-coverage-page
#import "remediation-roadmap.typ": remediation-roadmap-page
#import "attack-path.typ": attack-path-page
#import "attack-chain.typ": attack-chain-page


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

// Dark logo variant for cover page.
// Imported from theme.typ via shared.typ wildcard import.
// The report assembler may override this in report-data.typ with a resolved path.

// MAESTRO data defaults (empty = graceful degradation).
#let has-maestro-data = if has-maestro-data != none { has-maestro-data } else { false }
#let maestro-findings-by-layer = if maestro-findings-by-layer != none { maestro-findings-by-layer } else { () }
#let most-exposed-layer = if most-exposed-layer != none { most-exposed-layer } else { "" }
#let has-maestro-stack-image = if has-maestro-stack-image != none { has-maestro-stack-image } else { false }
#let maestro-stack-image-path = if maestro-stack-image-path != none { maestro-stack-image-path } else { "" }
#let has-maestro-heatmap-image = if has-maestro-heatmap-image != none { has-maestro-heatmap-image } else { false }
#let maestro-heatmap-image-path = if maestro-heatmap-image-path != none { maestro-heatmap-image-path } else { "" }
#let maestro-layer-distribution = if maestro-layer-distribution != none { maestro-layer-distribution } else { () }

// Attack tree defaults (empty = no attack path pages).
#let has-attack-trees = if has-attack-trees != none { has-attack-trees } else { false }
#let attack-trees = if attack-trees != none { attack-trees } else { () }

// Attack chain defaults (empty = no attack chain pages, Feature 141).
#let has-attack-chains = if has-attack-chains != none { has-attack-chains } else { false }
#let attack-chains = if attack-chains != none { attack-chains } else { () }

// Executive threat architecture defaults (F-128 — false = no executive architecture page).
#let has-executive-architecture = if has-executive-architecture != none { has-executive-architecture } else { false }
#let executive-architecture-image-path = if executive-architecture-image-path != none { executive-architecture-image-path } else { "" }

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
  logo-primary-dark-path: logo-primary-dark-path,
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


// --- Section Divider: Assessment Overview -----------------------------------
#section-divider("Assessment Overview", classification: classification)


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


// --- Executive Threat Architecture (conditional) ---------------------------
// Portrait infographic with layered architecture and narrative threat callouts
// for critical/high severity findings. Only when executive-architecture image
// exists (F-128).
#if has-executive-architecture {
  infographic-page(
    executive-architecture-image-path,
    section-name: "Executive Threat Architecture",
    classification: classification,
    is-portrait: true,
    description: [
      Layered system architecture with critical and high severity threats annotated as narrative callouts. This visualization highlights where the most exposed components sit in the system and what kind of attack each layer is most vulnerable to.
    ],
  )
}


// --- Attack Path Analysis (conditional) -------------------------------------
// One page per Critical/High finding with attack tree. Section divider +
// individual pages, gated by has-attack-trees boolean.
#if has-attack-trees and attack-trees.len() > 0 {
  section-divider("Attack Path Analysis", classification: classification)
  for entry in attack-trees {
    page(
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
      #attack-path-page(entry: entry, classification: classification)
    ]
  }
}


// --- Cross-Layer Attack Chain Analysis (conditional) ------------------------
// One page per surfaced (Critical/High) cross-layer attack chain. Section
// divider + individual pages, gated by has-attack-chains boolean (Feature 141).
#if has-attack-chains and attack-chains.len() > 0 {
  section-divider("Cross-Layer Attack Chain Analysis", classification: classification)
  for entry in attack-chains {
    page(
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
      #attack-chain-page(entry: entry, classification: classification)
    ]
  }
}


// --- Page 7: Risk Reduction Funnel (conditional) ---------------------------
// Portrait infographic with explanatory text. Only when funnel image exists.
#if has-funnel-image {
  infographic-page(
    funnel-image-path,
    section-name: "Risk Reduction Funnel",
    classification: classification,
    description: [
      The Risk Reduction Funnel illustrates how the overall risk profile transforms through each stage of the assessment pipeline. The top tier shows all threats identified during the initial STRIDE and AI-specific threat analysis. The second tier reflects severity recalibration after quantitative scoring, where composite scores incorporating CVSS, exploitability, scalability, and reachability may shift initial severity ratings.

      The third tier shows the impact of compensating controls detected in the codebase --- existing mitigations that reduce effective risk. The bottom tier presents the final residual risk posture, representing the organization's actual exposure after accounting for all identified defenses. The sidebar provides key metrics at a glance, including the total risk reduction percentage, control coverage rate, and the highest-residual-risk finding requiring priority attention.
    ],
  )
}


// --- Page 8: Risk Summary Dashboard (conditional) -------------------------
// Portrait infographic with explanatory text. Only when baseball card exists.
#if has-baseball-image {
  infographic-page(
    baseball-image-path,
    section-name: "Risk Summary Dashboard",
    classification: classification,
    description: [
      The Risk Summary Dashboard consolidates assessment results into three complementary views. The left panel displays the residual risk distribution across severity levels, showing how findings are distributed after compensating controls are applied.

      The center panel presents a component-by-threat-category heat map, where each cell indicates the highest residual severity for that intersection of system component and STRIDE or AI threat category. This enables rapid identification of which components carry the highest concentration of risk. The right panel highlights the top findings by residual risk score, listing the specific threats that require the most immediate attention with their affected components and residual scores.
    ],
  )
}


// --- Page 9: System Architecture (conditional) ----------------------------
// Portrait infographic with explanatory text. Only when architecture image exists.
#if has-architecture-image {
  infographic-page(
    architecture-image-path,
    section-name: "System Architecture",
    classification: classification,
    description: [
      The System Architecture diagram maps identified threats directly onto the assessed system's component topology. Components are grouped within their trust boundaries --- external/untrusted, application layer, and infrastructure/platform zones --- with color coding reflecting the concentration and severity of findings at each location.

      Threat badges on each component show the specific threat identifiers and their severity classifications. Data flow arrows illustrate the assessed communication paths between components, with trust boundary crossings highlighted as key attack surface areas where threats are most likely to be exploited. This spatial view complements the tabular findings detail by showing how threats cluster around specific architectural chokepoints.
    ],
  )
}


// --- MAESTRO Layer Risk Distribution (conditional) -----------------------
// Portrait infographic with explanatory text. Only when maestro-stack image exists.
#if has-maestro-stack-image {
  infographic-page(
    maestro-stack-image-path,
    section-name: "MAESTRO Layer Risk Distribution",
    classification: classification,
    description: [
      The MAESTRO Layer Risk Distribution diagram maps identified threats onto the seven-layer CSA MAESTRO framework for agentic AI systems. Each horizontal band represents an architectural layer from Foundation Model (L1) through Agent Ecosystem (L7), showing the finding count and highest severity at each layer. The most-exposed layer is visually highlighted.

      This view enables security leaders to quickly identify which architectural layers of the AI stack carry the most risk exposure and prioritize remediation efforts accordingly.
    ],
  )
}


// --- MAESTRO Component-Layer Heatmap (conditional) -----------------------
// Portrait infographic with explanatory text. Only when maestro-heatmap image exists.
#if has-maestro-heatmap-image {
  infographic-page(
    maestro-heatmap-image-path,
    section-name: "MAESTRO Component-Layer Heatmap",
    classification: classification,
    description: [
      The MAESTRO Component-Layer Heatmap provides a granular view of how threats intersect specific system components with MAESTRO architectural layers. Each cell represents the highest-severity finding at the intersection of a component (row) and a MAESTRO layer (column).

      This cross-tabulation identifies specific component-layer hotspots that require targeted remediation, complementing the aggregate layer view in the MAESTRO Stack diagram.
    ],
  )
}


// --- MAESTRO Findings by Layer (conditional) -----------------------------
// Findings regrouped by MAESTRO layer for architectural-layer-oriented review.
#if has-maestro-data {
  page(
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
    #maestro-findings-page(
      classification: classification,
      maestro-findings-by-layer: maestro-findings-by-layer,
      has-maestro-data: has-maestro-data,
    )
  ]
}


// --- Section Divider: Detailed Findings -------------------------------------
#section-divider("Detailed Findings", classification: classification)


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
