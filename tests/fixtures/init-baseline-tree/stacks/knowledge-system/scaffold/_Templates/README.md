# Templates

Templates define output format structures — one subfolder per output format. Templates separate *what* your content says (master content, narratives, voice) from *how* it is structured for delivery.

## Template-per-Format Pattern

Each output format gets its own subfolder containing format-specific structure definitions:

```
_Templates/
  pdf-report/
    structure.md          # Section layout, page breaks, header/footer
    formatting.md         # Typography, spacing, margin rules
  email-brief/
    structure.md          # Subject line, greeting, body sections, sign-off
    formatting.md         # Length limits, link placement, CTA position
  web-article/
    structure.md          # Title, intro, body sections, conclusion, metadata
    formatting.md         # Heading hierarchy, image placement, SEO elements
```

## What Goes Here

- Structural blueprints for each output format
- Format-specific rules (length, sections, required elements)
- Delivery requirements (file type, metadata, packaging)

## What Does NOT Go Here

- Content (belongs in `_Global/MasterContent/` and `_Global/Narratives/`)
- Voice and style rules (belong in `_Global/VoiceProfile.md` and `_Global/StyleGuide.md`)
- Quality criteria (belongs in `_Config/ScoringRubric.md`)

## Guidelines

- **Format-agnostic approach** — define structure in markdown; the builder chooses tooling for final rendering
- **One subfolder per format** — keeps format definitions independent and loadable on demand
- **Templates are reusable** — the same template applies to every output of that format, with content varying per instance
- **Load during export phase** — templates load via `_Config/ContextLoading.yaml` during the export workflow phase
