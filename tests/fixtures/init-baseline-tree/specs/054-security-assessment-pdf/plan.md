---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "All 23 spec FRs addressed. All 6 user stories trace to specific components and phases. No scope creep. Phase sequencing correctly prioritizes risk mitigation then core value."
  architect_signoff:
    agent: architect
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "Architecture sound — clean 3-layer decomposition, correct Typst selection, faithful pattern adherence. 4 moderate concerns: version pinning breadth, intermediate file path strategy, image path resolution, missing table-overflow in POC gate. All resolvable during implementation."
  techlead_signoff: null
---

# Implementation Plan: 054 — Security Assessment PDF Booklet

**Branch**: `054-security-assessment-pdf` | **Date**: 2026-03-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/054-security-assessment-pdf/spec.md`

## Summary

Add a `/security-report` command that auto-detects all available tachi pipeline artifacts in a directory and assembles them into a professionally designed, multi-page PDF booklet using Typst. The command follows established tachi patterns (4-step flow, 3-tier auto-detection, `--output-dir` flag) and introduces Typst as the first external rendering dependency. Deliverables are a command file, an agent file, a page assembly schema, and Typst template files for 8 page types including full-bleed infographic pages with mixed portrait/landscape orientation.

## Technical Context

**Language/Version**: Typst 0.11.x-0.12.x (template language), Markdown (command/agent specifications)
**Primary Dependencies**: Typst CLI (`typst compile`) — external, user-installed
**Storage**: Local filesystem — reads existing artifacts, writes `security-report.pdf`
**Testing**: Manual validation — generate PDFs from example artifacts, verify page inclusion and rendering
**Target Platform**: Any OS with Typst CLI (macOS, Linux, Windows)
**Project Type**: Methodology template — command file + agent file + Typst templates + schema (no application code)
**Performance Goals**: PDF generation <30 seconds for 34-finding report with 3 infographic images
**Constraints**: No network calls during generation; US Letter only (Phase 1); Typst pre-1.0 API instability
**Scale/Scope**: 8 page types, 7 artifact detection patterns, 3 data source tiers, ~6-8 Typst template files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Command follows established tachi pipeline pattern; no domain-specific logic in core |
| II. API-First Design | N/A | No API — local CLI command producing local file output |
| III. Backward Compatibility | PASS | New command; does not modify existing commands or artifacts |
| IV. Concurrency & Data Integrity | PASS | Read-only access to artifacts; single output file; no locking needed |
| V. Privacy & Data Isolation | PASS | All processing local; no network calls; classification markings preserved |
| VI. Testing Excellence | PASS | Manual validation using existing example artifacts; Typst POC validates rendering |
| VII. Definition of Done | PASS | Docs-only exception applies for methodology template; user validation via PDF review |
| VIII. Observability | PASS | Pre-generation artifact detection report; clear error messages for missing Typst |
| IX. Git Workflow | PASS | Feature branch `054-security-assessment-pdf` |
| X. Product-Spec Alignment | PASS | Spec approved by PM; plan under dual review |
| XI. SDLC Triad Collaboration | PASS | PRD Triad-approved; spec PM-approved; plan under dual review |

## Project Structure

### Documentation (this feature)

```
specs/054-security-assessment-pdf/
├── plan.md              # This file
├── research.md          # Research phase output (completed)
├── data-model.md        # Page assembly data model
├── quickstart.md        # Typst POC quickstart
└── tasks.md             # Task breakdown (/aod.tasks output)
```

### Source (repository root)

```
.claude/
├── commands/
│   └── security-report.md          # Command file (4-step: parse → validate → generate → report)
└── agents/
    └── tachi/
        └── report-assembler.md     # Agent file (artifact parsing + Typst data injection + compilation)

schemas/
└── security-report.yaml            # Page assembly schema (page types, sequence, tiers, columns)

templates/
├── README.md                        # Updated: distinguish reference vs rendering templates
└── security-report/
    ├── README.md                    # Typst template guide
    ├── main.typ                     # Master orchestrator (page sequencing, conditional inclusion)
    ├── cover.typ                    # Cover page (project name, date, classification, finding counts)
    ├── executive-summary.typ        # Executive summary (2-column metrics + narrative)
    ├── full-bleed.typ               # Full-bleed infographic page (16:9, zero margins)
    ├── findings-detail.typ          # Severity-sorted table (3-tier column sets)
    ├── control-coverage.typ         # Coverage matrix + status table
    ├── remediation-roadmap.typ      # Prioritized action table with SLAs
    └── shared.typ                   # Shared styles (colors, fonts, headers/footers, page numbering)
```

**Structure Decision**: This feature adds files to existing directories (`.claude/commands/`, `.claude/agents/tachi/`, `schemas/`, `templates/`) following established organizational patterns. The only new subdirectory is `templates/security-report/` for Typst rendering templates.

## Components

### Component 1: Command File (`security-report.md`)

**Purpose**: User-facing entry point following the 4-step command pattern.

**Responsibilities**:
- Step 0: Parse `--output-dir`, `--title` flags from `$ARGUMENTS`
- Step 1: Validate Typst installation (`which typst`); auto-detect artifacts in target directory using the 7-file detection matrix; require `threats.md` minimum; report detected artifacts and pages to be generated
- Step 2: Invoke report-assembler agent with detected artifacts, flags, and target directory
- Step 3: Report results — list generated PDF path, page count, and page types included

**Pattern**: Mirrors `.claude/commands/infographic.md` structure. Same flag conventions, same detection flow, same agent invocation pattern.

### Component 2: Agent File (`report-assembler.md`)

**Purpose**: Parses markdown artifacts, extracts structured data, generates Typst data file, and invokes Typst compilation.

**Responsibilities**:
- Parse YAML frontmatter from all detected markdown artifacts (project name, date, classification, schema version, finding counts)
- Parse markdown tables from artifacts (findings table, coverage matrix, remediation roadmap)
- Apply 3-tier data source preference for Findings Detail page columns
- Generate a Typst data file (`report-data.typ`) containing all extracted variables
- Determine page inclusion based on artifact availability
- Invoke `typst compile main.typ security-report.pdf` with the correct working directory
- Handle Typst compilation errors with clear messages
- Clean up intermediate data file after successful compilation

**Data Extraction Rules**:

| Source Artifact | Extracted Data | Target Page(s) |
|----------------|---------------|-----------------|
| `threats.md` frontmatter | project name, date, classification, schema version, finding counts | Cover, Executive Summary |
| `threats.md` Section 6 | Risk Summary (severity counts) | Executive Summary, Cover |
| `threats.md` Section 2 | Coverage Matrix (Tier 3 findings) | Findings Detail (fallback) |
| `threat-report.md` Section 1 | Executive Summary narrative | Executive Summary (enriched) |
| `threat-report.md` remediation section | Remediation items | Remediation Roadmap (enriched) |
| `risk-scores.md` Section 2 | Scored Threat Table (Tier 2 findings) | Findings Detail (scored) |
| `compensating-controls.md` Section 2 | Coverage Matrix with residual scores (Tier 1 findings) | Findings Detail (residual), Control Coverage |
| `compensating-controls.md` Section 3 | Recommendations with SLAs | Remediation Roadmap |
| `threat-risk-funnel.jpg` | Image file path | Risk Funnel page |
| `threat-baseball-card.jpg` | Image file path | Baseball Card page |
| `threat-system-architecture.jpg` | Image file path | System Architecture page |

### Component 3: Schema File (`security-report.yaml`)

**Purpose**: Declarative definition of page assembly rules, following existing schema conventions.

**Structure**:

```yaml
schema_version: "1.0"

security_report:
  output_file: security-report.pdf

  artifacts:
    # Detection matrix: file pattern, required/optional, pages enabled
    - pattern: threats.md
      required: true
      enables: [cover, executive-summary, findings-detail]
    - pattern: threat-report.md
      required: false
      enables: [executive-summary-enriched, remediation-roadmap-enriched]
    - pattern: risk-scores.md
      required: false
      enables: [findings-detail-scored]
    - pattern: compensating-controls.md
      required: false
      enables: [control-coverage, remediation-roadmap, findings-detail-residual]
    - pattern: threat-risk-funnel.jpg
      required: false
      enables: [risk-funnel]
    - pattern: threat-baseball-card.jpg
      required: false
      enables: [baseball-card]
    - pattern: threat-system-architecture.jpg
      required: false
      enables: [system-architecture]

  page_sequence:
    - type: cover
      layout: portrait
      size: us-letter
    - type: executive-summary
      layout: portrait
      size: us-letter
    - type: risk-funnel
      layout: landscape
      size: custom-16x9
    - type: baseball-card
      layout: landscape
      size: custom-16x9
    - type: system-architecture
      layout: landscape
      size: custom-16x9
    - type: findings-detail
      layout: portrait
      size: us-letter
      data_source_tiers:
        tier1:
          source: compensating-controls.md
          columns: [ID, Component, Threat, Residual Score, Residual Severity, Control Status, Recommendation]
        tier2:
          source: risk-scores.md
          columns: [ID, Component, Threat, Composite Score, Severity, CVSS, Exploitability]
        tier3:
          source: threats.md
          columns: [ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation]
    - type: control-coverage
      layout: portrait
      size: us-letter
    - type: remediation-roadmap
      layout: portrait
      size: us-letter

  page_dimensions:
    us-letter:
      width: "8.5in"
      height: "11in"
      margins: { top: "0.75in", bottom: "0.75in", left: "1in", right: "1in" }
    custom-16x9:
      width: "11in"
      height: "6.1875in"
      margins: { top: "0in", bottom: "0in", left: "0in", right: "0in" }
```

### Component 4: Typst Templates (`templates/security-report/`)

**Purpose**: Rendering templates that transform structured data into designed PDF pages.

**Architecture**: `main.typ` is the orchestrator that conditionally includes page modules based on data availability. Each page module is self-contained and receives data through shared Typst variables.

**Key Design Decisions**:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Template modularity | One `.typ` file per page type | Enables parallel development; follows PAT-011 numbered section pattern |
| Data injection | Typst data file (`report-data.typ`) imported by `main.typ` | Separates data extraction (agent) from rendering (Typst); mechanical mapping per PAT-004 |
| Page geometry switching | `#set page()` per page type | Typst natively supports per-page geometry changes |
| Full-bleed images | Custom page dimensions (11" x 6.1875") with zero margins | Avoids cropping/letterboxing; PRD-resolved approach |
| Shared styles | `shared.typ` with severity colors, fonts, headers/footers | Single source of truth for design consistency |
| Conditional pages | `#if` guards in `main.typ` checking data availability | Pages with no source data are simply not rendered |

**Typography**:
- Headings: Sans-serif (system default or Typst built-in)
- Body: Serif (system default or Typst built-in)
- Tables: Monospace for data columns, sans-serif for headers
- No custom font files required (uses Typst built-in font stack)

**Severity Color Palette** (from established tachi pattern):
- Critical: `#DC2626` (red)
- High: `#F97316` (orange)
- Medium: `#EAB308` (yellow)
- Low: `#4169E1` (blue)

## Data Flow

```mermaid
graph LR
    subgraph Input Artifacts
        T[threats.md]
        TR[threat-report.md]
        RS[risk-scores.md]
        CC[compensating-controls.md]
        I1[threat-risk-funnel.jpg]
        I2[threat-baseball-card.jpg]
        I3[threat-system-architecture.jpg]
    end

    subgraph Command
        CMD[/security-report]
    end

    subgraph Agent
        DET[Artifact Detection]
        PARSE[Markdown Parsing]
        DATA[report-data.typ]
    end

    subgraph Typst
        MAIN[main.typ]
        PAGES[Page Templates]
        PDF[security-report.pdf]
    end

    T --> CMD
    TR --> CMD
    RS --> CMD
    CC --> CMD
    I1 --> CMD
    I2 --> CMD
    I3 --> CMD

    CMD --> DET
    DET --> PARSE
    PARSE --> DATA
    DATA --> MAIN
    MAIN --> PAGES
    PAGES --> PDF
    I1 --> MAIN
    I2 --> MAIN
    I3 --> MAIN
```

## Tech Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Command | Markdown (tachi command spec) | — | User-facing entry point |
| Agent | Markdown (tachi agent spec) | — | Data extraction and Typst orchestration |
| Rendering | Typst | 0.11.x-0.12.x | PDF compilation from templates |
| Schema | YAML | — | Declarative page assembly rules |
| Input | Markdown + YAML frontmatter | v1.0/v1.1 | Upstream pipeline artifacts |
| Output | PDF | — | Final deliverable |

## Implementation Phases

### Phase 1: Typst POC + Command Scaffold (Wave 1 Gate)

**Purpose**: Validate Typst capabilities before full template authoring (team-lead requirement).

**POC Validates**:
1. Full-bleed image rendering with custom page dimensions (16:9)
2. Mixed orientation (portrait text pages + landscape image pages) in a single PDF
3. Conditional page inclusion via `#if` guards
4. Typst CLI invocation and compilation workflow

**Deliverables**:
- Minimal `main.typ` with one portrait text page and one full-bleed landscape image page
- `quickstart.md` documenting POC findings and Typst patterns
- Command file scaffold (`.claude/commands/security-report.md`) with argument parsing and Typst check
- Schema file (`schemas/security-report.yaml`) defining page assembly rules

**Gate**: POC must demonstrate all 3 rendering capabilities. If any fail, evaluate contingency approaches before proceeding.

### Phase 2: Text Page Templates

**Purpose**: Build all portrait-oriented text page templates.

**Deliverables**:
- `shared.typ` (severity colors, typography, headers/footers, page numbering)
- `cover.typ` (project name, date, classification, finding counts, tachi branding)
- `executive-summary.typ` (2-column metrics + narrative, adapts to available sources)
- `findings-detail.typ` (severity-sorted table with 3-tier column sets, multi-page flow)
- `control-coverage.typ` (coverage matrix + status table)
- `remediation-roadmap.typ` (prioritized action table with SLAs)

**Parallel Opportunity**: Once `shared.typ` is complete, all page templates can be authored in parallel (no cross-dependencies between page types).

### Phase 3: Full-Bleed Infographic Pages + Agent

**Purpose**: Build the full-bleed page template and the agent that drives everything.

**Deliverables**:
- `full-bleed.typ` (parameterized for all 3 infographic image types)
- Agent file (`.claude/agents/tachi/report-assembler.md`) with full artifact parsing, data extraction, 3-tier detection, Typst data file generation, and compilation invocation

### Phase 4: Integration + Graceful Degradation

**Purpose**: End-to-end integration testing across all artifact combinations.

**Deliverables**:
- Updated `main.typ` with full conditional page assembly
- Template README (`templates/security-report/README.md`)
- Updated `templates/README.md` distinguishing rendering vs reference templates
- Validation across artifact combinations: threats-only, threats+risk-scores, full pipeline, with/without infographic images

## Complexity Tracking

No constitution violations to justify.

## Risk Mitigation

| Risk | Mitigation | Contingency |
|------|-----------|-------------|
| Typst full-bleed rendering | POC in Phase 1 validates before full build | Zero-margin pages with image scaling to fit |
| Mixed page orientation | POC validates portrait+landscape in single PDF | All-landscape if mixed proves unreliable |
| Markdown table parsing complexity | Focus on known tachi schemas, not generic parsing | SARIF JSON as fallback data source |
| Typst version breaking changes | Pin to 0.11.x-0.12.x range; test with specific version | Document known-good version in README |
