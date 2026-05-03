---
name: tachi-threat-reporting
description: "Domain knowledge for narrative threat report generation — executive summary structure, architecture overview patterns, per-category narrative templates, attack tree construction rules with Mermaid syntax, and reference attack tree examples. Consumed by the threat-report agent during report generation."
---

# tachi-threat-reporting

Narrative threat report domain knowledge extracted from the tachi threat-report agent. This skill provides the templates, construction rules, and reference examples that the threat-report agent uses to transform structured threat model output into comprehensive narrative reports with Mermaid attack trees.

## Domain Overview

The threat report agent produces two output types:

1. **threat-report.md** -- A 7-section narrative report conforming to `schemas/report.yaml` containing executive summary, architecture overview, per-category threat analysis, cross-cutting themes, Mermaid attack trees, remediation roadmap, and finding reference appendix
2. **attack-trees/{finding-id}-attack-tree.md** -- Standalone Mermaid attack tree files for every Critical and High finding

Report generation applies three bodies of domain knowledge:

- **Narrative Templates** -- Structural patterns for each report section: executive summary elements, architecture overview layout, per-category subsection headers, per-finding narrative pattern, progressive depth rules, cross-cutting theme detection criteria, and language conventions
- **Attack Tree Construction** -- Rules for building Mermaid flowchart attack trees: tree structure (root/intermediate/leaf), minimum depth requirements, decomposition stopping rules, Mermaid syntax conventions, color styling, node naming, and validation checklist
- **Attack Tree Examples** -- Reference implementations demonstrating correct syntax, naming, gate logic, and decomposition depth for Critical and High severity patterns

## Loading Table

Reference files are loaded on-demand by the threat-report agent at specific workflow phases using the Read tool.

| Reference | File | Load When |
|-----------|------|-----------|
| Narrative Templates | `references/narrative-templates.md` | Generating Executive Summary (Section 1), Architecture Overview (Section 2), Threat Analysis (Section 3), Cross-Cutting Themes (Section 4), Remediation Roadmap (Section 6) |
| Attack Tree Construction | `references/attack-tree-construction.md` | Constructing Mermaid attack trees for Critical and High findings (Section 5) |
| Attack Tree Examples | `references/attack-tree-examples.md` | Before generating the first attack tree -- load once as reference patterns |
