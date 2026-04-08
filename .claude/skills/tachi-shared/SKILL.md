---
name: tachi-shared
description: "Shared reference files consumed by multiple tachi agents. Contains canonical definitions for severity bands, STRIDE+AI categories, and finding format that serve as the single source of truth across the pipeline. Agents Read individual reference files on-demand rather than maintaining inline copies."
---

# Tachi Shared References

Cross-cutting domain knowledge consumed by multiple tachi agents. These reference files are the canonical source of truth for definitions that appear across the pipeline -- severity bands, STRIDE+AI threat categories, and finding format conventions. Individual agents load specific references on-demand using the Read tool rather than duplicating definitions inline.

## Domain Coverage

This skill contains four shared reference files:

1. **Severity Bands** -- Composite score thresholds, severity band boundaries, color codes, SLA mappings, disposition defaults, and review date calculations. Used everywhere severity classification drives decisions.

2. **STRIDE+AI Categories** -- All 11 threat categories (6 STRIDE + 5 AI) with descriptions, ID prefixes, OWASP references, and the DFD element-to-category applicability matrix that determines which categories apply to which component types.

3. **Finding Format** -- The finding intermediate representation (IR) specification: required fields, optional fields, ID format conventions, validation rules, and table output format. Defines the contract between threat agents (producers) and downstream consumers.

4. **MAESTRO Layers** -- CSA MAESTRO seven-layer taxonomy definitions for agentic AI architectures: layer identifiers (L1-L7), descriptions, keyword-to-layer mappings, and the classification algorithm (first-match-wins, "Unclassified" default). Used during Phase 1 to classify components by architectural layer.

## Loading Table

| Reference File | Consumers | Load When |
|----------------|-----------|-----------|
| `references/severity-bands-shared.md` | orchestrator, risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler | When severity classification, SLA computation, governance field derivation, or severity-based formatting is needed |
| `references/stride-categories-shared.md` | orchestrator, spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse | When category definitions, DFD applicability rules, or category-to-agent mapping is needed |
| `references/finding-format-shared.md` | orchestrator, spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse, risk-scorer | When producing or consuming finding records, validating finding structure, or assembling output tables |
| `references/maestro-layers-shared.md` | orchestrator, risk-scorer, control-analyzer, threat-report | When classifying components by MAESTRO layer (Phase 1), propagating layer tags through findings, or including layer metadata in output |

## Loading Mechanism

Agents use the Read tool to load individual reference files on-demand at the workflow phase where the content is needed. Each reference file is self-contained and can be loaded independently. Content is evictable from context after the relevant phase completes.

```markdown
# Example loading instruction in an agent body:
Read `.claude/skills/tachi-shared/references/severity-bands-shared.md`
when entering severity classification or governance field generation.
```
