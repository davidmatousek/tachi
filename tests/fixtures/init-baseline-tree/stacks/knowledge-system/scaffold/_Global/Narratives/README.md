# Narratives

Narratives are atomic story fragments — self-contained anecdotes, examples, case studies, or scenarios that commands embed into outputs. Each narrative is one file, enabling selective loading and composition.

## Atomic Narrative Pattern

- **One file per narrative** — each story fragment is self-contained
- **Selective embedding** — commands choose which narratives to include based on context (target audience, output type, relevance)
- **Composable** — multiple narratives can be combined in a single output
- **Lazy-loaded** — only narratives relevant to the current workflow phase are loaded (see `_Config/ContextLoading.yaml`)

## What Goes Here

- Personal or professional anecdotes that illustrate expertise
- Case studies and project examples
- Scenario descriptions that demonstrate capability
- Quantified achievement stories with context and impact

## File Format

Use kebab-case filenames that describe the narrative's theme:

```
Narratives/
  leadership-turnaround.md
  technical-migration.md
  customer-discovery.md
  team-scaling.md
```

Each file should include frontmatter for command filtering:

```yaml
---
theme: leadership
context: enterprise transformation
tags: [team-building, change-management]
---
```

## Guidelines

- **DO** keep each narrative focused on one story or example
- **DO** include concrete details (numbers, outcomes, context)
- **DO** write narratives as raw material — commands adapt tone and format for each output
- **DO NOT** duplicate content between Narratives and MasterContent — narratives are stories; master content is structured professional content
- **DO NOT** embed narrative text directly in command files — always reference by file path

## Security Note

Review narratives for sensitive personal stories, health information, legal matters, or financial details. Mark sensitive narratives with `sensitivity: high` in frontmatter so commands can filter them from bulk operations.
