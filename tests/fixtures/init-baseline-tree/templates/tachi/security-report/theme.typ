// =============================================================================
// Theme Tokens: Security Assessment PDF Booklet
// =============================================================================
// Single source of brand identity. Customize this file to rebrand the report.
// All page templates consume these tokens via shared.typ — no other file should
// contain hardcoded structural colors.
//
// See: specs/060-professional-pdf-security/quickstart.md for customization guide
// =============================================================================


// ---------------------------------------------------------------------------
// 1. Brand Color Tokens
// ---------------------------------------------------------------------------

/// Tachi Indigo — headers, primary surfaces, cover title.
/// Matched to tachi-logo-primary-dark.png background (#18223B).
#let brand-primary = rgb("#18223B")

/// Steel Blue — secondary/supporting elements.
#let brand-secondary = rgb("#2D4A6F")

/// Vermillion — classification banners, accent lines, emphasis.
#let brand-accent = rgb("#C93A40")

/// Muted Gold — premium accent touches (use sparingly).
#let brand-highlight = rgb("#B8963E")

/// Lacquer Black — body text on dark backgrounds.
#let brand-dark = rgb("#0D0D0D")

/// Washi White — page backgrounds, card fills.
#let brand-light = rgb("#F5F2EB")

/// Ash Gray — secondary text, captions, footers.
#let brand-muted = rgb("#64748B")


// ---------------------------------------------------------------------------
// 2. Logo Path Tokens
// ---------------------------------------------------------------------------
// Defaults point to the standard brand directory. The report assembler
// overrides these in report-data.typ at runtime with resolved relative paths.

/// Vertical lockup — used on cover page (light background variant).
#let logo-primary-path = "../../brand/final/tachi-logo-primary.png"

/// Vertical lockup — dark background variant for dark cover page.
#let logo-primary-dark-path = "../../brand/final/tachi-logo-primary-dark.png"

/// Horizontal lockup — used in page headers.
#let logo-horizontal-path = "../../brand/final/tachi-logo-horizontal.png"

/// Image format hint — brand assets are JPEG with .png extension.
/// Typst requires explicit format when extension doesn't match content.
#let logo-format = "jpg"


// ---------------------------------------------------------------------------
// 3. Font Stack Tokens
// ---------------------------------------------------------------------------
// Sans-serif for headings, serif for body, monospace for data.
// Typst tries each font in order; "New Computer Modern" is always available.

/// Headings: sans-serif stack.
#let font-heading = ("Helvetica Neue", "Helvetica", "Arial", "New Computer Modern")

/// Body text: serif stack.
#let font-body = ("New Computer Modern", "Charter", "Georgia", "Times New Roman")

/// Code/data: monospace stack.
#let font-mono = ("Menlo", "Courier New", "Courier")
