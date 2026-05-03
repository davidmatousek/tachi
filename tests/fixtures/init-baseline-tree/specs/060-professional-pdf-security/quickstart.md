# Quickstart: Customizing the tachi PDF Report Theme

## Changing Brand Colors

Edit `templates/security-report/theme.typ`:

```typst
// Change the primary color (headers, cover title)
#let brand-primary = rgb("#1B2A4A")  // ← Replace with your color

// Change the accent color (classification banners, emphasis)
#let brand-accent = rgb("#C93A40")   // ← Replace with your color
```

Recompile:
```bash
typst compile templates/security-report/main.typ output.pdf --root .
```

All pages automatically reflect the new colors.

## Changing Logos

Replace the PNG files in `brand/final/`:
- `tachi-logo-primary.png` — Vertical logo for cover page
- `tachi-logo-horizontal.png` — Horizontal logo for page headers

The report assembler auto-detects and injects paths. If files are missing, text-only branding is used.

## Customizing Disclaimer Text

Create or edit `report-config.typ` in the target directory before running `/security-report`:

```typst
#let custom-disclaimer-text = "Your custom legal disclaimer text here."
```

## Hiding Pages

In `report-config.typ`:

```typst
#let show-methodology = false  // Hide methodology page
#let show-disclaimer = false   // Hide disclaimer page
```

## Severity Colors

Severity colors (Critical red, High orange, Medium yellow, Low blue) are functional constants and are intentionally NOT customizable via theme.typ. They are consistent across all tachi outputs.
