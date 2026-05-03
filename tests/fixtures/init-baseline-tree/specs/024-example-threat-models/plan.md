---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-23
    status: APPROVED
    notes: "All 12 FRs addressed, 4-wave strategy matches PRD timeline, no scope creep, all user stories covered, existing examples retained"
  architect_signoff:
    agent: architect
    date: 2026-03-23
    status: APPROVED_WITH_CONCERNS
    notes: "Schema v1.1 approach correct, all 8 evaluation criteria passed. Concern: coverage matrix analyzed-but-clean indicator must use em dash U+2014 not ASCII hyphens — corrected in validation checklist"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Example Threat Models

**Branch**: `024-example-threat-models` | **Date**: 2026-03-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/024-example-threat-models/spec.md`

## Summary

Create three polished, externally-facing example threat models (web-app, agentic-app, microservices) with standardized Mermaid architecture diagrams, schema v1.1 compliant threat model outputs, OWASP framework cross-reference appendices, and a comprehensive examples README with framework relationship hierarchy. All content is hand-authored Markdown/YAML — no application code.

## Technical Context

**Language/Version**: Markdown + YAML (content authoring, no compiled code)
**Primary Dependencies**: Mermaid flowchart syntax (GitHub-rendered), output schema v1.1 (`schemas/output.yaml`), canonical template (`templates/threats.md`)
**Storage**: File system — `examples/` directory at repository root
**Testing**: Manual validation: Mermaid rendering in GitHub, schema v1.1 section compliance, OWASP cross-reference accuracy, STRIDE-per-Element correctness, risk level consistency via OWASP 3x3 matrix
**Target Platform**: GitHub repository (Markdown rendered by GitHub's built-in Mermaid renderer)
**Project Type**: Content/documentation — no source code structure required
**Constraints**: All examples must be self-contained, renderable in GitHub markdown, and conformant to the existing output schema without modifications to `schemas/output.yaml`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Examples demonstrate tachi across AI and non-AI systems — domain-agnostic |
| III. Backward Compatibility | PASS | No modifications to existing schemas, templates, or interfaces. Existing examples retained (FR-010) |
| VII. Definition of Done | PASS | Validation via schema compliance, Mermaid rendering, OWASP accuracy |
| IX. Git Workflow | PASS | Feature branch `024-example-threat-models` created |
| X. Product-Spec Alignment | PASS | Spec PM-approved, plan undergoing dual review |

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```
specs/024-example-threat-models/
├── plan.md              # This file
├── research.md          # Research phase output (completed during spec)
├── data-model.md        # Content entity relationships
├── quickstart.md        # Example usage guide
└── tasks.md             # Task breakdown (/aod.tasks output)
```

### Content (repository root)

```
examples/
├── README.md                    # Rewritten: overview, framework hierarchy, usage
├── web-app/
│   ├── architecture.md          # Mermaid flowchart: frontend, API, auth, DB
│   └── threats.md               # Schema v1.1, STRIDE-only, OWASP Web appendix
├── agentic-app/
│   ├── architecture.md          # Mermaid flowchart: LLM, MCP, agents, KB
│   └── threats.md               # Schema v1.1, STRIDE+AI, OWASP Agentic+MCP appendix
├── microservices/
│   ├── architecture.md          # Mermaid flowchart: gateway, services, MQ, DBs
│   └── threats.md               # Schema v1.1, STRIDE-only, OWASP Web appendix
├── ascii-web-api/               # Retained as-is (format test fixture)
├── free-text-microservice/      # Retained as-is (format test fixture)
└── mermaid-agentic-app/         # Retained as-is (format test fixture)
```

**Structure Decision**: Content-only feature — no `src/`, `tests/`, or `backend/` directories needed. All deliverables are Markdown files under `examples/`.

## Components

### Architecture Diagrams (3 files)

Each `architecture.md` contains a Mermaid `flowchart TD` with:
- Labeled components using shape indicators (`[]` for processes, `[()]` for data stores, `[]` for external entities)
- `subgraph` blocks defining trust zones
- Labeled arrows showing data flows with protocols

**Web-app components** (minimum 4): Web Client, API Gateway, Auth Service, User Database
**Agentic-app components** (minimum 5): User, LLM Agent Orchestrator, MCP Tool Server, Knowledge Base, External API
**Microservices components** (minimum 7): API Gateway, Order Service, Payment Service, Notification Service, Inventory Database, Message Queue, External Payment Provider

### Threat Model Outputs (3 files)

Each `threats.md` conforms to output schema v1.1 with all 8 sections:

| Section | Web-App | Agentic-App | Microservices |
|---------|---------|-------------|---------------|
| 1. System Overview | 4+ components | 5+ components | 7+ components |
| 2. Trust Boundaries | 3 zones | 3 zones | 4 zones |
| 3. STRIDE Tables (6) | All populated | All populated | All populated |
| 4. AI Threat Tables (2) | "No AI components detected" | AG + LLM populated | "No AI components detected" |
| 4a. Correlated Findings | "No cross-agent correlations" | 1+ correlation groups | "No cross-agent correlations" |
| 5. Coverage Matrix | STRIDE only, AG/LLM = n/a | Full 8-column | STRIDE only, AG/LLM = n/a |
| 6. Risk Summary | Deduplicated counts | With raw/dedup notation | Deduplicated counts |
| 7. Recommended Actions | Sorted by risk desc | Sorted by risk desc | Sorted by risk desc |

### OWASP Cross-Reference Appendices (3 appendix sections)

Added as `## Appendix: OWASP Framework Cross-References` at the end of each `threats.md`. Format:

| Finding ID | OWASP Category | Category Name | Notes |
|------------|----------------|---------------|-------|

**Web-app**: Maps to OWASP Top 10 Web 2025 (A01–A10). Target: 5+ distinct categories.
**Agentic-app**: Maps to OWASP Web 2025 + Agentic Top 10 (ASI01–ASI10) + MCP Top 10 (MCP01–MCP10). Target: 3+ ASI, 2+ MCP categories.
**Microservices**: Maps to OWASP Top 10 Web 2025 (A01–A10). Target: 5+ distinct categories.

### Examples README

Replaces the current minimal `examples/README.md` with:
1. **Overview**: Purpose and audience for the three examples
2. **Framework Relationship Hierarchy**: Mermaid diagram showing STRIDE as base methodology, OWASP frameworks as classification overlays
3. **Example-to-Framework Mapping Table**: Which examples exercise which frameworks
4. **Usage Instructions**: How to run tachi against example `architecture.md` files and compare results
5. **Existing Examples Note**: Brief mention of format-specific test fixtures (ascii-web-api, free-text-microservice, mermaid-agentic-app)

### Project README Update

Add or update the examples section in `README.md` to link to `examples/README.md` and describe the three standardized examples.

## Data Flow

```
architecture.md (Mermaid input)
        │
        ▼
  [tachi analysis]  ← agents/stride/ (6 agents)
        │              agents/ai/ (5 agents, dispatched by keyword)
        ▼
  threats.md (schema v1.1 output)
        │
        ▼
  OWASP appendix (mapping table, example-specific)
```

For the examples feature, this flow is simulated — the `threats.md` files are hand-authored to match what tachi would produce, using the canonical template as the structural reference.

## Tech Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| Content | Markdown | All deliverables |
| Diagrams | Mermaid flowchart | Architecture diagrams + framework hierarchy |
| Schema | YAML (output.yaml v1.1) | Structural validation reference |
| Template | templates/threats.md | Canonical output format |
| Rendering | GitHub Mermaid renderer | Diagram visualization |

## Implementation Approach

### Wave Strategy (from PRD)

| Wave | Tasks | Duration | Parallelism |
|------|-------|----------|-------------|
| 1 | Directory scaffold + 3 Mermaid architecture diagrams | 0.5 days | All 3 diagrams in parallel |
| 2 | 3 threat model outputs (schema v1.1) + OWASP appendices | 1–1.5 days | All 3 in parallel |
| 3 | Examples README + Project README update | 0.5 days | Sequential (README depends on examples) |
| 4 | Quality validation (schema compliance, Mermaid rendering, OWASP accuracy) | 0.5 days | Per-example validation |

### Key Design Decisions

1. **Fresh examples over migration**: Creating new examples from scratch rather than migrating existing v1.0 examples. Rationale: format conversion (ASCII/free-text → Mermaid) + schema migration (v1.0 → v1.1) + OWASP appendices is more effort than fresh authoring, and fresh examples ensure clean, consistent quality.

2. **Existing examples retained**: The three existing directories (`ascii-web-api`, `free-text-microservice`, `mermaid-agentic-app`) stay as format-specific test fixtures validating ASCII and free-text input handling.

3. **OWASP appendix as mapping table**: Cross-references implemented as an appendix section within each `threats.md`, not as schema field additions. This avoids global impact on `output.yaml` while demonstrating coverage.

4. **Agentic-app exercises correlation rules**: The agentic-app example is designed so that at least one STRIDE finding and one AI finding target the same component, triggering the correlation rules (CR-1 through CR-5) to populate Section 4a.

5. **Component names trigger correct dispatch**: Architecture diagram component names use keywords that match the interface contract's AI dispatch rules (e.g., "LLM Agent Orchestrator" triggers both LLM and AG dispatch).

### Validation Checklist (Wave 4)

For each example:
- [ ] `architecture.md` renders valid Mermaid in GitHub
- [ ] `threats.md` YAML frontmatter has `schema_version: "1.1"`
- [ ] All 8 sections present in correct order
- [ ] STRIDE-per-Element rules applied correctly in coverage matrix
- [ ] Risk levels match OWASP 3x3 matrix (no Likelihood/Impact/Risk inconsistencies)
- [ ] Finding IDs use correct prefixes (S, T, R, I, D, E, AG, LLM)
- [ ] AI sections show correct behavior (populated for agentic-app, empty for others)
- [ ] OWASP appendix maps to correct framework categories
- [ ] Coverage matrix uses three-state model correctly (count, `—` em dash U+2014, `n/a`)

## Complexity Tracking

No constitution violations. No complexity justifications needed.
