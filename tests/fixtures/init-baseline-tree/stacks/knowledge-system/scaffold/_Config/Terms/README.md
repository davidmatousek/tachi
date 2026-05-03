# Terms

Terms are atomic domain terminology files — one markdown file per term. This atomic pattern enables lazy loading: commands load only the terms relevant to the current context instead of an entire glossary.

## Why Atomic Terms

Loading a full glossary forces every command invocation to pay the token cost of all terms, even when only a few are relevant. Atomic term files enable selective loading, achieving significant token savings on domains with large vocabularies.

## File Format

One file per term, kebab-case filename matching the term:

```
Terms/
  machine-learning.md
  agile-methodology.md
  stakeholder-analysis.md
```

Each term file contains:

```markdown
---
term: "Machine Learning"
aliases: ["ML", "machine-learning"]
category: "technology"
---

# Machine Learning

Definition and usage guidance for this term within your domain.

## Preferred Usage

How this term should be used in outputs.

## Avoid

Common misuses or conflations to watch for.
```

## Guidelines

- **One file per term** — never combine multiple terms in one file
- **Include aliases** — list abbreviations and alternate forms in frontmatter for command lookup
- **Define preferred usage** — tell commands how to use the term, not just what it means
- **Keep files short** — a term definition should be 10-30 lines; if longer, it may belong in MasterContent instead
- **Use categories** — frontmatter categories help commands filter terms by domain area

## Loading Pattern

Commands reference `_Config/ContextLoading.yaml` to determine when terms are loaded. Typically, terms load during the `analyze` phase when the command is understanding inputs and selecting content.
