# Master Content

Master content is the core reusable material that your knowledge system draws from when producing outputs. This directory holds structured professional content that commands reference, select from, and adapt — but never modify.

## Content-as-Data Principle

Master content is **immutable source data**. Outputs derive FROM master content; they never modify it.

- Each file in this directory is a self-contained content unit
- Commands select and combine content units to produce outputs
- Output-specific adaptations happen in command logic using presets, not by editing files here
- Changes to master content propagate to all future outputs automatically

## What Goes Here

- Structured professional content organized by topic or category
- Reusable content blocks that appear across multiple outputs
- Factual or reference material that outputs draw from
- Domain expertise captured in a format commands can process

## What Does NOT Go Here

- Output-specific content (belongs in `_Output/`)
- Story fragments and anecdotes (belong in `Narratives/`)
- Configuration and metadata (belong in `_Config/`)
- Templates and format definitions (belong in `_Templates/`)

## File Organization

- One file per content unit or topic
- Use kebab-case filenames (e.g., `technical-skills.md`, `project-history.md`)
- Include frontmatter with metadata (category, last updated, tags) for command filtering
- Keep files focused — a content unit that serves multiple unrelated purposes should be split

## Security Note

Audit files for PII before committing. Master content should contain reusable professional content, not personal contact details or government identifiers.
