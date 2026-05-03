---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-21
    status: APPROVED
    notes: "All 20 FRs addressed. All 5 user stories covered by 4-phase implementation. No scope creep. 3 non-blocking: section count clarification, prior concerns tracking, edge case references."
  architect_signoff:
    agent: architect
    date: 2026-03-21
    status: APPROVED_WITH_CONCERNS
    notes: "Architecture sound. Hub-and-spoke model followed. 3 low-severity concerns: IR field count (10 vs 11), ContextLoading path count (9 vs 7), agent frontmatter schema alignment with README. All addressable during task creation."
  techlead_signoff: null
---

# Implementation Plan: Project Skeleton & Interface Contract

**Branch**: `001-project-skeleton-interface` | **Date**: 2026-03-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-project-skeleton-interface/spec.md`

## Summary

Deliver the foundational artifacts for tachi: a canonical repository structure with READMEs, a machine-readable interface contract (`docs/INTERFACE-CONTRACT.md`), an output template (`templates/threats.md`), three YAML schemas (`schemas/`), configuration updates, and three example inputs. All deliverables are markdown and YAML files — no runtime code. The approach follows the knowledge system hub-and-spoke pattern where `agents/` is the immutable content hub, `adapters/` provides configuration, `templates/` defines output formats, and `schemas/` defines machine-readable contracts.

## Technical Context

**Language/Version**: N/A — knowledge system (markdown + YAML files only, no compiled code)
**Primary Dependencies**: None — no runtime dependencies; all deliverables are static content files
**Storage**: Local filesystem (git repository) — markdown and YAML files
**Testing**: Validation-by-example — sample inputs validate against schemas; cross-reference integrity checks
**Target Platform**: Any operating system with git — platform-agnostic content files
**Project Type**: Knowledge system — hub-and-spoke content architecture
**Performance Goals**: N/A — no runtime performance targets for static content
**Constraints**: All deliverables must be markdown or YAML; no executable code; follow knowledge system naming conventions (PascalCase for directories/config, kebab-case for agent/narrative files)
**Scale/Scope**: ~40 files to create or update across 7 directories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | tachi is domain-specific (threat modeling) by design — the toolkit structure follows general-purpose content patterns |
| II. API-First Design | N/A | No API — F-001 produces static files. API-first applies to F-002+ when runtime features are built |
| III. Backward Compatibility | PASS | F-001 is the first feature — no existing contracts to break |
| IV. Concurrency & Data Integrity | N/A | Static files, no concurrent state mutations |
| V. Privacy & Data Isolation | PASS | No PII in reference content; `classification: confidential` header on outputs |
| VI. Testing Excellence | PASS (adapted) | Testing = validation-by-example: sample inputs validate against schemas, cross-references resolve, template sections complete |
| VII. Definition of Done | PASS | DoD = push to branch + validation-by-example + developer walkthrough |
| VIII. Observability | N/A | No runtime system — observability applies to F-002+ |
| IX. Git Workflow | PASS | On feature branch `001-project-skeleton-interface` |
| X. Product-Spec Alignment | PASS | PM sign-off obtained (APPROVED_WITH_CONCERNS) |
| XI. SDLC Triad | PASS | Triad workflow in progress |

**No violations requiring justification.**

## Components

The deliverables are organized into 7 logical components following the knowledge system hub-and-spoke architecture:

### Component 1: Agent Prompt Files (Hub)

**Location**: `agents/`
**Purpose**: Immutable threat agent definitions — the content hub that all outputs derive from
**Files**:
- `agents/stride/spoofing.md` — Spoofing threat agent prompt
- `agents/stride/tampering.md` — Tampering threat agent prompt
- `agents/stride/repudiation.md` — Repudiation threat agent prompt
- `agents/stride/info-disclosure.md` — Information Disclosure threat agent prompt
- `agents/stride/denial-of-service.md` — Denial of Service threat agent prompt
- `agents/stride/privilege-escalation.md` — Elevation of Privilege threat agent prompt
- `agents/ai/prompt-injection.md` — Prompt Injection threat agent prompt (LLM category)
- `agents/ai/tool-abuse.md` — Tool Abuse threat agent prompt (AG category)
- `agents/ai/data-poisoning.md` — Data Poisoning threat agent prompt (LLM category)
- `agents/ai/model-theft.md` — Model Theft threat agent prompt (LLM category)
- `agents/ai/agent-autonomy.md` — Agent Autonomy threat agent prompt (AG category)
- `agents/ai/README.md` — Updated with 5-agent-to-2-table mapping (AG/LLM)
- `agents/orchestrator.md` — Orchestrator placeholder (content authored in F-002)

**Agent Prompt File Format** (each agent file follows this structure):
```yaml
---
agent_name: {threat-category}
category: {stride | agentic | llm}
threat_class: {STRIDE letter or AI class}
dfd_targets: [{element types this agent analyzes}]
owasp_references: [{applicable OWASP references}]
output_schema: schemas/finding.yaml
---

# {Agent Name} Threat Agent

## Purpose
{What this agent detects and why it matters}

## Detection Scope
{DFD element types, keywords, and patterns this agent looks for}

## Finding Template
{Structure matching the IR schema fields}

## References
{OWASP, MITRE, or framework citations}
```

### Component 2: Machine-Readable Schemas

**Location**: `schemas/`
**Purpose**: Define the data contracts between agents, templates, and downstream features
**Files**:
- `schemas/README.md` — Directory purpose, schema relationships, versioning
- `schemas/finding.yaml` — Intermediate Representation (IR) schema (11 fields)
- `schemas/input.yaml` — Input validation schema (5 formats with recognition patterns)
- `schemas/output.yaml` — Output structure validation (7 sections matching template)

**Key Design Decisions**:
- YAML format (consistent with project, human-readable)
- Schema version `1.0` from day one for forward compatibility
- IR schema is the single contract point between agents and all output formats

### Component 3: Interface Contract

**Location**: `docs/INTERFACE-CONTRACT.md`
**Purpose**: Single document specifying everything an integrator needs to invoke tachi
**Sections**:
1. Input Specification — 5 formats with recognition patterns and examples
2. STRIDE-per-Element Normalization Table — DFD type → STRIDE categories (YAML)
3. AI Extension Dispatch Rules — keyword → agent category mapping
4. Output Specification — reference to template and schema, `schema_version: "1.0"`
5. Invocation Protocol — input/output/side-effect contract
6. Input Sanitization Guidance — data-not-instructions principle
7. Error Conditions — unsupported format, no components, minimum input requirements

### Component 4: Output Template

**Location**: `templates/threats.md`
**Purpose**: Canonical template defining the structure of every threat model output
**Sections** (7 required):
1. YAML Frontmatter — `schema_version`, date, input_format, classification
2. System Overview — parsed architecture summary
3. Trust Boundaries — identified trust zones and boundary crossings
4. STRIDE Tables (6) — one per category (S/T/R/I/D/E)
5. AI Threat Tables (2) — AG (Agentic) and LLM groupings
6. Coverage Matrix — components × threat categories
7. Risk Summary — counts by severity level
8. Recommended Actions — prioritized by risk level descending

**Finding Row Fields** (STRIDE): ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation
**Finding Row Fields** (AI): ID, Component, Threat, OWASP Reference, Likelihood, Impact, Risk Level, Mitigation

### Component 5: Configuration Updates (Spoke)

**Location**: `adapters/`
**Purpose**: Correct scaffold paths and populate domain-specific configuration
**Files**:
- `adapters/ContextLoading.yaml` — 7 path corrections (`_Global/` → `agents/`, `_Config/` → `adapters/`, `_Templates/` → `templates/`)
- `adapters/ScoringRubric.md` — Populated with OWASP 3x3 risk scoring dimensions (8 likelihood + 8 impact factors)
- `adapters/ProjectMeta.yaml` — Populated with tachi metadata (name, description, version, domain, status)

### Component 6: Examples

**Location**: `examples/`
**Purpose**: Self-contained input/output pairs for validation and documentation
**Directories**:
- `examples/ascii-web-api/` — ASCII diagram of a web API with trust boundaries
- `examples/mermaid-agentic-app/` — Mermaid diagram of an agentic AI application
- `examples/free-text-microservice/` — Free-text description of a microservice architecture

Each example contains:
- `input.md` — Architecture description in the stated format
- `threats.md` — Expected output following the template structure (all 7 sections populated)

### Component 7: Root Files

**Location**: Repository root
**Files**:
- `LICENSE` — Apache 2.0 (chosen for broader patent protection appropriate for a security tool)
- `README.md` — Updated project overview with quickstart pointing to INTERFACE-CONTRACT.md

## Data Flow

```
Architecture Input (5 formats)
        │
        ▼
┌─────────────────────┐
│  Input Validation    │ ◄── schemas/input.yaml
│  (format detection)  │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  STRIDE-per-Element  │ ◄── INTERFACE-CONTRACT.md
│  Normalization       │     (normalization table)
│  + AI Dispatch       │
└────────┬────────────┘
         │
    ┌────┴─────────┐
    ▼              ▼
┌────────┐   ┌──────────┐
│ STRIDE  │   │ AI Threat │
│ Agents  │   │ Agents    │
│ (6)     │   │ (5)       │
└────┬───┘   └────┬─────┘
     │             │
     ▼             ▼
┌─────────────────────┐
│  Intermediate        │ ◄── schemas/finding.yaml
│  Representation (IR) │     (agent output contract)
│  [Finding objects]   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Template Engine     │ ◄── templates/threats.md
│  (IR → Output)       │     schemas/output.yaml
└────────┬────────────┘
         │
         ▼
   Threat Model Output
   (threats.md)
```

## Tech Stack

| Technology | Purpose | Rationale |
|-----------|---------|-----------|
| Markdown | Content format for all documents | Platform-agnostic, no runtime dependencies, works with any agentic coding tool |
| YAML | Schema and configuration format | Human-readable, consistent with project conventions, frontmatter-compatible |
| OWASP 3x3 Matrix | Risk rating standard | Human-interpretable, developer-friendly, maps to SARIF severity |
| STRIDE-per-Element | Threat methodology | DFD element mapping, O(n) scaling per element |
| OWASP LLM Top 10 v2025 | LLM threat references | Published November 2024, stable |
| OWASP Agentic Top 10 2026 | Agentic threat references | Draft — mitigated by schema versioning |

## Project Structure

### Documentation (this feature)

```
specs/001-project-skeleton-interface/
├── plan.md              # This file
├── research.md          # Research phase output (completed during spec)
├── data-model.md        # IR finding schema documentation
├── quickstart.md        # Implementation quickstart guide
├── contracts/           # Schema contract documentation
│   ├── finding-ir.md    # IR schema contract details
│   ├── input-format.md  # Input format contract details
│   └── output-schema.md # Output schema contract details
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (generated by /aod.tasks)
```

### Source Code (repository root)

```
tachi/
├── agents/                         # Hub: Threat agent prompt definitions
│   ├── README.md                   # [exists] Directory purpose and conventions
│   ├── orchestrator.md             # [CREATE] Orchestrator placeholder
│   ├── VoiceProfile.md             # [exists] Scaffold template
│   ├── StyleGuide.md               # [exists] Scaffold template
│   ├── MasterContent/              # [exists] Shared reference content
│   │   └── README.md               # [exists]
│   ├── Narratives/                 # [exists] Reusable threat narrative fragments
│   │   └── README.md               # [exists]
│   ├── stride/                     # [exists] 6 STRIDE threat agents
│   │   ├── README.md               # [exists]
│   │   ├── spoofing.md             # [CREATE]
│   │   ├── tampering.md            # [CREATE]
│   │   ├── repudiation.md          # [CREATE]
│   │   ├── info-disclosure.md      # [CREATE]
│   │   ├── denial-of-service.md    # [CREATE]
│   │   └── privilege-escalation.md # [CREATE]
│   └── ai/                         # [exists] AI-specific threat agents
│       ├── README.md               # [UPDATE] Add 5-to-2 table mapping
│       ├── prompt-injection.md     # [CREATE]
│       ├── tool-abuse.md           # [CREATE]
│       ├── data-poisoning.md       # [CREATE]
│       ├── model-theft.md          # [CREATE]
│       └── agent-autonomy.md       # [CREATE]
├── adapters/                       # Spoke: Configuration
│   ├── README.md                   # [exists]
│   ├── ContextLoading.yaml         # [UPDATE] 7 path corrections
│   ├── ScoringRubric.md            # [UPDATE] OWASP 3x3 dimensions
│   ├── ProjectMeta.yaml            # [UPDATE] tachi metadata
│   ├── Terms/                      # [exists]
│   │   └── README.md               # [exists]
│   └── Presets/                    # [exists]
│       └── README.md               # [exists]
├── templates/                      # Output format definitions
│   ├── README.md                   # [exists]
│   └── threats.md                  # [CREATE] Master output template
├── schemas/                        # [CREATE] Machine-readable schemas
│   ├── README.md                   # [CREATE]
│   ├── finding.yaml                # [CREATE] IR schema
│   ├── input.yaml                  # [CREATE] Input validation schema
│   └── output.yaml                 # [CREATE] Output structure schema
├── examples/                       # Sample inputs and expected outputs
│   ├── README.md                   # [exists]
│   ├── ascii-web-api/              # [CREATE]
│   │   ├── input.md                # [CREATE] ASCII diagram
│   │   └── threats.md              # [CREATE] Expected output
│   ├── mermaid-agentic-app/        # [CREATE]
│   │   ├── input.md                # [CREATE] Mermaid diagram
│   │   └── threats.md              # [CREATE] Expected output
│   └── free-text-microservice/     # [CREATE]
│       ├── input.md                # [CREATE] Free-text description
│       └── threats.md              # [CREATE] Expected output
├── docs/
│   ├── INTERFACE-CONTRACT.md       # [CREATE] Core deliverable
│   └── ...
├── LICENSE                         # [CREATE] Apache 2.0
└── README.md                       # [UPDATE] Add quickstart
```

**Structure Decision**: Knowledge system pattern — no `src/`, `tests/`, or runtime code directories. All deliverables are content files organized by the hub-and-spoke model. Create = 30 new files, Update = 5 existing files.

## Implementation Phases

### Phase 1: Foundation (Schemas + Configuration)

Create the machine-readable contracts and update configuration first — these are the contracts that all other files reference.

**Deliverables**:
1. `schemas/` directory with `README.md`, `finding.yaml`, `input.yaml`, `output.yaml`
2. `adapters/ContextLoading.yaml` path corrections
3. `adapters/ProjectMeta.yaml` populated
4. `adapters/ScoringRubric.md` populated with OWASP 3x3 dimensions
5. `LICENSE` file (Apache 2.0)

**Rationale**: Schemas define the IR contract that agent files and templates must conform to. Configuration updates ensure ContextLoading.yaml references resolve correctly. These must exist before writing content that references them.

### Phase 2: Agent Prompt Files (Hub Content)

Create all 11 agent prompt files plus the orchestrator placeholder.

**Deliverables**:
1. 6 STRIDE agent files in `agents/stride/`
2. 5 AI agent files in `agents/ai/`
3. `agents/ai/README.md` updated with 5-to-2 table mapping
4. `agents/orchestrator.md` placeholder

**Rationale**: Agent files reference schemas (via `output_schema: schemas/finding.yaml`) and must conform to the IR contract. They are authored after schemas exist.

### Phase 3: Interface Contract + Output Template

Create the two core user-facing documents.

**Deliverables**:
1. `docs/INTERFACE-CONTRACT.md` — complete with all 7 sections
2. `templates/threats.md` — complete with all 7 output sections plus field descriptions and examples

**Rationale**: These documents reference schemas (for validation) and agents (for dispatch rules). They synthesize the contracts into user-facing documentation.

### Phase 4: Examples + Root Files

Create the validation examples and update root README.

**Deliverables**:
1. 3 example directories (`ascii-web-api/`, `mermaid-agentic-app/`, `free-text-microservice/`) each with `input.md` and `threats.md`
2. `README.md` updated with quickstart pointing to INTERFACE-CONTRACT.md

**Rationale**: Examples depend on all preceding artifacts (schemas for validation, template for output structure, interface contract for input format). They are the final validation layer.

## Validation Strategy

Since F-001 produces no runtime code, validation is by inspection and cross-reference integrity:

1. **Cross-Reference Check**: Every path referenced in ContextLoading.yaml, interface contract, and schemas resolves to an existing file
2. **Template Completeness**: `templates/threats.md` contains all 7 required sections with field descriptions and examples
3. **Schema Coverage**: `schemas/finding.yaml` defines all 11 fields with types and allowed values
4. **Agent File Compliance**: Each agent file follows the standard frontmatter format and references `schemas/finding.yaml`
5. **Example Validation**: Each example `threats.md` follows the template structure with all 7 sections populated
6. **README Coverage**: Every top-level directory contains a README explaining purpose and conventions
7. **Naming Convention Check**: PascalCase for directories/config files, kebab-case for agent/narrative files

## Complexity Tracking

No Constitution violations requiring justification. All principles either pass or are explicitly N/A for a knowledge system with no runtime code.
