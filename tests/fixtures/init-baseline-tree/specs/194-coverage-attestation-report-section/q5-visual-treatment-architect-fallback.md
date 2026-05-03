# Q5 Visual Treatment Architect Fallback — Coverage Attestation

**Status**: Pre-approved fallback (activates if ux-ui-designer memo absent Day 2 AM)
**Author**: Architect
**Date**: 2026-04-18 (Day 1 Wave 1.0)
**Feature**: 194 (F-B Coverage Attestation Report Section)
**Scope**: Visual treatment for Covered / Partial / Gap framework items on the per-framework coverage-matrix pages (FR-010)
**Supersedes / superseded-by**: This memo **supersedes no prior decision** and is **superseded by the ux-ui-designer Q5 memo if that memo lands Day 2 AM**. If the ux-ui-designer memo slips, this fallback is the authoritative visual-treatment spec for T029 (Typst template authoring).

---

## Scope

This memo specifies the per-item-cell visual treatment on the per-framework coverage-matrix pages added by Feature 194. The headline typography (Partial count rendered at equal visual weight with Covered and Gap counts) is governed by ADR-029 Decision 7 and is independent of this memo.

---

## Visual-Treatment Recommendations

### Covered
- **Icon**: Green check mark (`✓`)
- **Background fill**: Light green (`#E8F5E9`, WCAG AA-compliant luminance against dark foreground text)
- **Text weight**: Plain (not bold, not italic)

### Partial
- **Icon**: Yellow half-circle (`◐` or a Typst-rendered equivalent half-filled circle glyph — distinct shape from both the Covered check and the Gap X)
- **Background fill**: Light amber (`#FFF8E1`, WCAG AA-compliant luminance against dark foreground text)
- **Text weight**: Plain (not bold, not italic)
- **Note**: Must be visually distinct from both Covered and Gap — the half-circle shape achieves this independently of the color.

### Gap
- **Icon**: Red X mark (`✗`)
- **Background fill**: Light red (`#FFEBEE`, WCAG AA-compliant luminance against dark foreground text)
- **Text weight**: Plain (not bold, not italic)

---

## WCAG AA Color-Blind Accessibility Justification

The color-plus-icon combination is **redundantly encoded** (dual-encoding principle): every classification is distinguishable by icon shape alone, independent of color. A reader with any form of color vision deficiency (deuteranopia, protanopia, tritanopia, or full monochromacy) can distinguish all three classifications by the icon shapes `✓` / `◐` / `✗`, which are visually distinct across the entire color-vision spectrum.

The color channel adds a secondary cue that reinforces the icon shape but is NOT the only distinguishing signal. Hue selections (green / yellow / red) are the conventional traffic-light mapping familiar to every adopter and use sufficient luminance contrast against dark foreground text to satisfy WCAG AA contrast ratios.

**Checklist**:
- Color is NOT the only distinguishing cue (icon shapes are independently distinct)
- Icons are distinguishable in grayscale (shape differences: check / half-circle / X)
- Background fills use light tints that maintain readable text contrast
- Icon + background-fill combination is redundant, not conflicting

---

## Escalation Note

If the ux-ui-designer Q5 memo lands Day 2 AM, that memo supersedes this fallback. The architect fallback is pre-approved as a safety net to prevent T029 (Typst template authoring) from blocking on the Q5 question.

If the ux-ui-designer memo does not land by Day 2 AM, this fallback is the authoritative spec for T029. The Typst template author SHOULD implement the recommendations above verbatim and flag any rendering-implementation questions (e.g., Typst glyph availability for `◐`) back to the architect for resolution.

If the ux-ui-designer memo lands partially (e.g., icon recommendations but no color recommendations), the gap is filled from this fallback on a per-element basis.
