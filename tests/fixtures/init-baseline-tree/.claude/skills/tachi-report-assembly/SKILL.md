---
name: tachi-report-assembly
description: "Domain knowledge for PDF security report assembly — artifact detection patterns with tier selection rules, Typst data variable contract with type specifications and image path resolution, and brand asset handling with logo location and fallback rules. Consumed by the report-assembler agent during report generation."
---

# tachi-report-assembly

PDF security report assembly domain knowledge extracted from the tachi report-assembler agent. This skill provides the artifact detection tables, Typst template interface contract, and brand asset guidelines that the report-assembler uses to transform pipeline artifacts into a professional PDF security assessment booklet.

## Domain Overview

The report assembly pipeline bridges tachi pipeline artifacts (markdown and image files) with a Typst template system to produce a multi-page PDF:

1. **Artifact Detection** -- Identify which pipeline outputs are available in the target directory and select the richest data source tier for findings presentation
2. **Data Extraction** -- Parse markdown artifacts and extract structured data via deterministic Python script
3. **Typst Data Generation** -- Generate a `report-data.typ` file containing all extracted variables as Typst `#let` bindings that the template system imports at compile time
4. **Brand Asset Resolution** -- Locate logo files with dark variant support and compute relative paths for Typst image inclusion

The Typst template system uses a data injection pattern: `main.typ` imports `report-data.typ` and conditionally includes page templates based on artifact availability flags. The agent's responsibility is generating `report-data.typ` with correct variable names, types, and values.

## Loading Table

Reference files are loaded on-demand by the report-assembler agent at specific workflow phases using the Read tool.

| Reference | File | Load When |
|-----------|------|-----------|
| Typst Artifacts | `references/typst-artifacts.md` | Artifact detection phase (Step 1) — determining which pipeline outputs exist and selecting data source tier |
| Typst Template Contract | `references/typst-template-contract.md` | Data generation phase (Step 2) — generating report-data.typ with correct variable bindings |
| Brand Asset Guidelines | `references/brand-asset-guidelines.md` | Brand detection phase (Step 2) — locating and resolving logo paths for cover and footer |
