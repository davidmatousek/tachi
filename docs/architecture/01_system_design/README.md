# System Design

Auto-generated from approved plan.md files. Each feature section captures component architecture and data flow at the time of planning approval.

---

### Feature 091: Delivery Document Generation

## Components

### Component 1: Delivery Document Template

**File**: `.aod/templates/delivery-template.md`
**Type**: New file
**Purpose**: Standardized template for consistent delivery document generation across all features.

The template defines the mandatory document structure:
- Header: Feature number, name, date, branch, PR
- What Was Delivered: Bullet list of accomplishments
- How to See & Test: Numbered verification steps
- Delivery Metrics: Estimated/actual/variance table
- Surprise Log: Captured during retrospective
- Lessons Learned: Category, text, KB entry reference
- Feedback Loop: New ideas or "None"
- Source Artifacts: Links to spec, plan, tasks, PRD
- Documentation Updates: Agent update summary table
- Cleanup: Checklist of closure steps

### Component 2: Skill Step 9 — Generate delivery.md

**File**: `.claude/skills/~aod-deliver/SKILL.md`
**Type**: Modify existing Step 9
**Purpose**: Replace terminal-only display with file generation + terminal display.

1. Re-read `.aod/templates/delivery-template.md` before generating
2. Resolve specs directory from branch name; create if missing
3. Populate template from retrospective data (Steps 1-8)
4. Write to `specs/{NNN}-*/delivery.md`
5. Fallback: display in terminal if write fails

### Component 3: Command Step 12 — Redirect Closure Report

**File**: `.claude/commands/aod.deliver.md`
**Type**: Modify existing Step 12
**Purpose**: Change closure report target from `.aod/closures/` to `specs/{NNN}-*/delivery.md`.

### Component 4: Command Step 10 — GitHub Closing Comment Update

**File**: `.claude/commands/aod.deliver.md`
**Type**: Modify existing Step 10
**Purpose**: Include delivery document path in GitHub Issue closing comment.

## Data Flow

```
Steps 1-8 (retrospective data collection)
         │
         ▼
   Skill Step 9: Generate delivery.md
         │
         ├── Read .aod/templates/delivery-template.md (re-ground)
         ├── Populate from collected data (accomplishments, metrics, etc.)
         ├── Write to specs/{NNN}-*/delivery.md
         │         │
         │         └── [on failure] Display in terminal as fallback
         ▼
   Command Step 10: Close GitHub Issue
         │
         └── Comment includes: "See: specs/{NNN}-*/delivery.md"
         ▼
   Command Step 12: Verify delivery.md exists (no longer generates closure file)
```

---

### Feature 001: Project Skeleton & Interface Contract

## Components

### Component 1: Agent Prompt Files (Hub)

**Location**: `agents/`
**Type**: New files (11 agent prompts + 1 placeholder)
**Purpose**: Immutable threat agent definitions — the content hub that all outputs derive from.

- `agents/stride/` — 6 STRIDE agents (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation)
- `agents/ai/` — 5 AI agents (prompt-injection, tool-abuse, data-poisoning, model-theft, agent-autonomy)
- `agents/ai/README.md` — 5-agent-to-2-table mapping: AG (agent-autonomy, tool-abuse) and LLM (prompt-injection, data-poisoning, model-theft)
- `agents/orchestrator.md` — Placeholder for F-002

### Component 2: Machine-Readable Schemas

**Location**: `schemas/`
**Type**: New directory with 3 YAML schema files
**Purpose**: Data contracts between agents, templates, and downstream features.

- `schemas/finding.yaml` — IR schema (id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type)
- `schemas/input.yaml` — Input validation (5 formats: ASCII, free-text, Mermaid, PlantUML, C4)
- `schemas/output.yaml` — Output structure (7 sections matching threats.md template)

### Component 3: Interface Contract

**Location**: `docs/INTERFACE-CONTRACT.md`
**Type**: New file
**Purpose**: Single document specifying input formats, STRIDE-per-Element normalization, AI dispatch rules, invocation protocol, and side-effect guarantees.

### Component 4: Output Template

**Location**: `templates/tachi/output-schemas/threats.md`
**Type**: New file
**Purpose**: Canonical template for threat model output with 7 sections: System Overview, Trust Boundaries, STRIDE Tables (6), AI Threat Tables (2), Coverage Matrix, Risk Summary, Recommended Actions.

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
│  Template Engine     │ ◄── templates/tachi/output-schemas/threats.md
│  (IR → Output)       │     schemas/output.yaml
└────────┬────────────┘
         │
         ▼
   Threat Model Output
   (threats.md)
```

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| Markdown + YAML | Content format — platform-agnostic, no runtime dependencies |
| OWASP 3x3 Matrix | Risk rating standard — human-interpretable |
| STRIDE-per-Element | Threat methodology — DFD element mapping, O(n) scaling |

---

### Feature 003: Orchestrator Agent

## Components

### Component 1: Orchestrator Prompt File

**File**: `agents/orchestrator.md`
**Type**: Replace placeholder (Feature 001 placeholder replaced with full implementation)
**Purpose**: Central prompt implementing OWASP 4-step threat modeling workflow — parse, classify, dispatch, assemble.

**Internal Structure** (prompt sections):

| Section | OWASP Phase | Responsibility |
|---------|-------------|----------------|
| Frontmatter | — | Agent metadata (agent_name, category, status, version) with explicit references to all schemas, templates, and agent files |
| Role & Purpose | — | Establish orchestrator identity, platform-neutrality, and output constraints |
| Input Sanitization Boundary | — | Mark architecture input as data, not instructions; reject prompt injection attempts within `<architecture-input>` tags |
| Output Format Specification | — | Define 7-section structure (System Overview, Trust Boundaries, STRIDE Tables x6, AI Tables x2, Coverage Matrix, Risk Summary, Recommended Actions) with YAML frontmatter |
| Phase 1: Scope | Scope | Format detection (5 formats with heuristic priority), component extraction with format-specific parsers, DFD classification (4 element types with ambiguous-default-to-Process rule), trust boundary identification, System Overview assembly, **Component Inventory intermediate output with self-check** |
| Phase 2: Determine Threats | Determine Threats | STRIDE-per-Element normalization table (DFD type to applicable categories), AI keyword dispatch rules (LLM keywords, AG keywords, dual-dispatch), agent invocation protocol (parallel + sequential modes with full architecture context payload), **Dispatch Table intermediate output with self-check** |
| Phase 3: Determine Countermeasures | Determine Countermeasures | Agent finding collection, risk_level validation against OWASP 3x3 matrix with correction protocol, STRIDE table assembly (6 tables), AI table assembly (2 tables via 5-agent-to-2-table mapping) |
| Phase 4: Assess | Assess | Coverage matrix generation (finding counts, dash for analyzed-but-clean, empty for not-applicable), risk summary computation (percentages rounded to 1 decimal), recommended actions list (sorted by risk descending, then table order) |
| Error Handling | — | Three terminal errors: UNSUPPORTED_FORMAT (auto-detection fails), NO_COMPONENTS (parsing finds no components or data flows), INVALID_FORMAT_VALUE (format field not in allowed enum); two non-terminal handlers: ambiguous classification annotation, non-conforming finding correction |
| Output Validation | — | Structural integrity checklist: 7 sections present, frontmatter valid, finding IDs sequential, all fields populated, risk levels consistent with OWASP 3x3, cross-section counts match |

## Data Flow

```mermaid
flowchart TD
    A[Architecture Input] --> B{Format Detection}
    B -->|auto| C[Heuristic Priority: ASCII, Free-text, Mermaid, PlantUML, C4]
    B -->|explicit| D[Use Declared Format]
    C --> E[Component Extraction and DFD Classification]
    D --> E
    E --> F[Trust Boundary Identification]
    F --> G[System Overview Assembly]
    G --> H{STRIDE-per-Element Dispatch}
    H --> I[External Entity: S, R]
    H --> J[Process: S, T, R, I, D, E]
    H --> K[Data Store: T, I, D]
    H --> L[Data Flow: T, I, D]
    I & J & K & L --> M{AI Keyword Dispatch}
    M -->|LLM keywords| N[+ prompt-injection, data-poisoning, model-theft]
    M -->|AG keywords| O[+ agent-autonomy, tool-abuse]
    M -->|Both| P[Dual-dispatch: LLM + AG]
    M -->|None| Q[STRIDE only]
    N & O & P & Q --> R[Agent Invocation with Full Context]
    R --> S[Finding Collection and Risk Validation]
    S --> T[STRIDE Tables x6 + AI Tables x2]
    T --> U[Coverage Matrix]
    U --> V[Risk Summary]
    V --> W[Recommended Actions]
    W --> X[threats.md Output]
```

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| Markdown prompt file | Platform-agnostic deliverable — works with any LLM |
| OWASP 4-step process | Industry-standard threat modeling methodology |
| STRIDE-per-Element + AI keywords | Deterministic dispatch rules embedded in prompt |

---

### Feature 005: STRIDE Threat Agents

**Status**: Delivered (2026-03-22) | PR #6 | 41/41 tasks complete

## Components

### Component 1: 6 STRIDE Threat Agent Definitions

**Location**: `agents/stride/`
**Type**: Enhanced existing files (Feature 001 skeleton refined and validated)
**Purpose**: Each agent analyzes architecture input through exactly one STRIDE threat lens, producing component-specific findings conforming to `schemas/finding.yaml`.

| Agent File | Threat Class | DFD Targets | ID Prefix | Key Detection Patterns |
|-----------|-------------|-------------|-----------|----------------------|
| `spoofing.md` | Spoofing (S) | External Entity, Process | S-N | Authentication bypass, credential theft/replay, session hijacking, service impersonation, federated identity attacks |
| `tampering.md` | Tampering (T) | Process, Data Store, Data Flow | T-N | Input validation bypass, data integrity violations, message/payload manipulation, storage tampering, configuration tampering |
| `repudiation.md` | Repudiation (R) | External Entity, Process | R-N | Audit logging gaps, log integrity failures, non-repudiation mechanism absence, timestamp manipulation |
| `info-disclosure.md` | Information Disclosure (I) | Process, Data Store, Data Flow | I-N | Data leaks via error messages, excessive API responses, side-channel exposure, storage access control gaps, transit encryption gaps |
| `denial-of-service.md` | Denial of Service (D) | Process, Data Store, Data Flow | D-N | Resource exhaustion, queue/connection pool saturation, storage flooding, algorithmic complexity attacks, cascading failures |
| `privilege-escalation.md` | Elevation of Privilege (E) | Process | E-N | RBAC/ABAC bypass, horizontal/vertical escalation, default permission over-grants, parameter tampering for privilege gain |

**Agent structure** (canonical per-agent organization):
- YAML frontmatter: `agent_name`, `category`, `threat_class`, `dfd_targets`, `owasp_references`, `output_schema`
- Purpose section: Threat class definition and DFD targeting rationale
- Detection Scope: Targeted DFD element types with patterns and indicators (4-6 subcategories)
- AI-Specific Threat Patterns: Agentic application extensions per STRIDE category
- Finding Template: Concrete example demonstrating component-specific findings
- Risk Computation: OWASP 3x3 matrix application with likelihood/impact guidance
- References: OWASP Top 10 2021, OWASP API Security 2023, CWE, MITRE ATT&CK identifiers

### Component 2: AI-Specific Threat Pattern Extensions

**Location**: Within each `agents/stride/*.md` agent file
**Type**: New sections within existing agents
**Purpose**: Extend classic STRIDE patterns with threats specific to agentic AI applications.

Each STRIDE agent includes an "AI-Specific Threat Patterns" section covering:
- **Spoofing**: LLM API key theft, model identity spoofing, prompt-based identity assumption
- **Tampering**: Training data poisoning, RAG context manipulation, tool response modification
- **Repudiation**: Agentic action audit gaps, tool call logging, autonomous decision accountability
- **Info Disclosure**: Model inversion attacks, embedding leakage, context window data exposure
- **DoS**: LLM token exhaustion, recursive agent loops, unbounded tool execution chains
- **Privilege Escalation**: Agent capability boundary violations, tool permission escalation, MCP server scope creep

### Component 3: OWASP API Security 2023 Cross-References

**Location**: YAML frontmatter `owasp_references` field in each agent file
**Type**: Enhanced metadata
**Purpose**: Cross-reference STRIDE findings with OWASP API Security Top 10 2023 (API1-API10) alongside existing OWASP Top 10 2021, CWE, and MITRE ATT&CK references.

### Agent Validation Framework

The validation approach (used during Feature 005 delivery) has three layers:

**Layer 1: Structural Audit** (per agent)
- Frontmatter fields present and correct (`agent_name`, `category`, `threat_class`, `dfd_targets`, `owasp_references`, `output_schema`)
- Section structure matches canonical organization (purpose, detection scope, patterns, finding template, risk computation, references)
- `dfd_targets` matches STRIDE-per-Element matrix row for this category

**Layer 2: Content Quality** (per agent)
- Detection patterns cover all attack subcategories from PRD FR-7
- Finding template examples demonstrate component-specific threats (not generic)
- Mitigation examples are actionable with specific technology references
- Framework references include OWASP, CWE, and MITRE ATT&CK identifiers

**Layer 3: Integration Validation** (all agents together)
- Run orchestrator against `examples/mermaid-agentic-app/input.md`
- Verify all 6 STRIDE tables have findings in assembled `threats.md`
- Verify coverage matrix shows correct STRIDE-per-Element targeting
- Verify 100% component specificity (zero generic findings)

### STRIDE-per-Element Validation Matrix

| DFD Element | S | T | R | I | D | E |
|-------------|---|---|---|---|---|---|
| **Processes** | X | X | X | X | X | X |
| **Data Flows** | | X | | X | X | |
| **Data Stores** | | X | | X | X | |
| **External Entities** | X | | X | | | |

## Data Flow

```
Architecture Input (any format)
         │
         ▼
┌─────────────────────────────┐
│ Orchestrator (F-003)        │
│  Phase 1: Scope             │
│  - Format detection         │
│  - Component classification │
│  - DFD element assignment   │
└─────────┬───────────────────┘
          │ dispatch per STRIDE-per-Element
          ▼
┌─────────────────────────────┐
│ 6 STRIDE Agents (F-005)     │
│  Each agent:                │
│  1. Receives full arch      │
│  2. Filters by dfd_targets  │
│  3. Applies classic STRIDE  │
│     detection patterns      │
│  4. Applies AI-specific     │
│     threat patterns         │
│  5. Produces findings       │
│     (IR schema)             │
└─────────┬───────────────────┘
          │ findings per schemas/finding.yaml
          ▼
┌─────────────────────────────┐
│ Orchestrator (F-003)        │
│  Phase 3-4: Assemble        │
│  - Validate risk_level      │
│  - Build STRIDE tables      │
│  - Generate coverage matrix │
│  - Compute risk summary     │
└─────────┬───────────────────┘
          │
          ▼
    threats.md output
```

## Tech Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Agent files | Markdown with YAML frontmatter | Platform-neutral, LLM-agnostic prompt format |
| Schema | YAML | Machine-readable validation contract |
| Reference frameworks | OWASP Top 10 2021, OWASP API Security 2023, CWE, MITRE ATT&CK | Industry-standard cross-references for threat findings |
| Validation | Manual review + orchestrator integration run | No automated test framework needed for prompt files |

---

### Feature 007: AI Threat Agents

**Status**: Delivered (2026-03-22) | PR #8 | 48/48 tasks complete

## Components

### Agent Validation Framework

The validation approach follows the three-layer framework proven in F-005 (STRIDE agents):

**Layer 1: Structural Audit** (per agent)
- Frontmatter fields present and correct (`agent_name`, `category`, `threat_class`, `dfd_targets`, `owasp_references`, `output_schema`)
- Section structure matches canonical organization (purpose, detection scope, patterns, finding template, risk computation, references)
- `dfd_targets` matches interface contract AI extension dispatch rules

**Layer 2: Content Quality** (per agent)
- Detection patterns cover all attack subcategories from PRD FR-8
- Finding template examples demonstrate component-specific threats (not generic)
- Mitigation examples are actionable with specific technology references
- Framework references include OWASP AI framework IDs (LLM0x:2025, ASI-xx, MCP-xx:2025)

**Layer 3: Integration Validation** (all agents together)
- Run orchestrator against `examples/mermaid-agentic-app/input.md`
- Verify AG and LLM tables have findings in assembled `threats.md`
- Verify two-layer keyword dispatch and dual-dispatch behavior
- Verify 100% component specificity (zero generic findings)

### AI Agent DFD Targeting Matrix

| Agent | category | threat_class | dfd_targets | OWASP Framework |
|-------|----------|-------------|-------------|-----------------|
| prompt-injection.md | llm | LLM | [Process] | LLM Top 10 v2025 (LLM01) |
| data-poisoning.md | llm | LLM | [Data Store, Data Flow] | LLM Top 10 v2025 (LLM03, LLM04) |
| model-theft.md | llm | LLM | [Data Store, Process] | LLM Top 10 v2025 (LLM10) |
| agent-autonomy.md | agentic | AG | [Process] | Agentic Top 10 (ASI01, ASI06, ASI08, ASI09, ASI10) |
| tool-abuse.md | agentic | AG | [Process] | Agentic Top 10 (ASI02, ASI04), MCP Top 10 (MCP03) |

## Data Flow

```
Architecture Input (any format)
         │
         ▼
┌─────────────────────────────┐
│ Orchestrator (F-003)        │
│  Phase 1: Scope             │
│  - Format detection         │
│  - Component classification │
│  - DFD element assignment   │
└─────────┬───────────────────┘
          │ dispatch per STRIDE-per-Element
          │ + AI keyword dispatch (Layer 1)
          ▼
┌──────────────────┐    ┌──────────────────┐
│ 6 STRIDE Agents  │    │ 5 AI Agents      │
│ (F-005 validated)│    │ (F-007 — this)   │
│                  │    │                  │
│ Each agent:      │    │ Each agent:      │
│ 1. Receives arch │    │ 1. Receives arch │
│ 2. Filters by    │    │ 2. Filters by    │
│    dfd_targets   │    │    dfd_targets   │
│ 3. Applies       │    │ 3. Applies Layer │
│    patterns      │    │    2 keywords    │
│ 4. Produces      │    │ 4. Applies       │
│    findings (IR) │    │    patterns      │
│                  │    │ 5. Produces      │
│                  │    │    findings (IR) │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     │ all findings per schemas/finding.yaml
                     ▼
┌─────────────────────────────┐
│ Orchestrator (F-003)        │
│  Phase 3-4: Assemble        │
│  - Build 6 STRIDE tables    │
│  - Build 2 AI tables        │
│    (AG table + LLM table)   │
│  - Generate coverage matrix │
│  - Compute risk summary     │
└─────────┬───────────────────┘
          │
          ▼
    threats.md output
    (8 threat tables total)
```

## Tech Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Agent files | Markdown with YAML frontmatter | Platform-neutral, LLM-agnostic prompt format; matches F-005 STRIDE pattern |
| Schema | YAML (`schemas/finding.yaml` v1.0) | Machine-readable validation contract; read-only for this feature |
| OWASP references | LLM Top 10 v2025, Agentic Top 10 2026, MCP Top 10 2025 | Three complementary AI security frameworks |
| Validation | Manual review + orchestrator integration run | No automated test framework needed for prompt files |

---

### Feature 010: Deduplication & Risk Rating

**Status**: Delivered (2026-03-22) | PR #11 | 24/24 tasks complete

## Components

### Component 1: Orchestrator Prompt — Correlation Detection Phase

**File**: `agents/orchestrator.md`
**Type**: Extend existing Phase 3 (Determine Countermeasures)
**Purpose**: Add correlation detection logic after all agent findings are collected and risk-validated, before coverage matrix generation.

Five deterministic correlation rules map STRIDE-to-AI category pairs:

| Rule | STRIDE Category | AI Category | Correlation Basis |
|------|----------------|-------------|-------------------|
| CR-1 | Tampering (T) | Data-Poisoning (LLM) | Data integrity |
| CR-2 | Privilege-Escalation (E) | Agent-Autonomy (AG) | Excessive permissions |
| CR-3 | Info-Disclosure (I) | Prompt-Injection (LLM) | Information leakage |
| CR-4 | Repudiation (R) | Agent-Autonomy (AG) | Accountability gaps |
| CR-5 | Denial-of-Service (D) | Tool-Abuse (AG) | Resource exhaustion |

### Component 2: Output Template — Correlated Findings Section (4a)

**File**: `templates/tachi/output-schemas/threats.md`
**Type**: New Section 4a between AI Threat Tables and Coverage Matrix

### Component 3: Output Template — Enhanced Coverage Matrix

**File**: `templates/tachi/output-schemas/threats.md` (Section 5)
**Type**: Modify existing — deduplicated counts, "—" for gaps, "n/a" for not-applicable

### Component 4: Output Template — Risk Calibration Matrix + Deduplicated Risk Summary

**File**: `templates/tachi/output-schemas/threats.md` (Section 6)
**Type**: Add subsection + modify existing counts

### Component 5: Output Schema Update

**File**: `schemas/output.yaml`
**Type**: Add Correlated Findings section schema

### Component 6: Interface Contract Update

**File**: `docs/INTERFACE-CONTRACT.md`
**Type**: Formalize deduplication in Sections 3 + 4

## Data Flow

```
Architecture Input
        │
        ▼
┌─────────────────────────────┐
│ Orchestrator Phase 1-2      │
│ (unchanged)                 │
└────────┬────────────────────┘
         │
    ┌────┴────────┐
    ▼             ▼
┌─────────┐  ┌──────────┐
│ STRIDE   │  │ AI       │
│ Agents   │  │ Agents   │
│ (6)      │  │ (5)      │
└────┬────┘  └────┬─────┘
     └─────┬──────┘
           │ all findings (IR schema)
           ▼
┌─────────────────────────────┐
│ Phase 3 (extended)          │
│ 1. Collect + validate       │
│ 2. Assemble tables          │
│ 3. NEW: Correlation detect  │
│ 4. NEW: Assemble Section 4a │
└────────┬────────────────────┘
         ▼
┌─────────────────────────────┐
│ Phase 4 (modified)          │
│ 1. Coverage matrix (dedup)  │
│ 2. Risk Calibration Matrix  │
│ 3. Risk summary (dedup)     │
│ 4. Recommended actions      │
│ 5. Structural validation    │
└────────┬────────────────────┘
         ▼
   threats.md output
   (7 sections + Section 4a)
```

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| Markdown prompt | Orchestrator prompt extension — platform-agnostic |
| YAML schema | Output validation contract update |
| Markdown template | Output format specification |
| OWASP 3×3 Matrix | Risk calibration documentation (already implemented) |

---

### Feature 012: SARIF Output Generation

**Status**: Delivered (2026-03-22) | PR #13 | 20/20 tasks complete

## Components

### Component 1: Orchestrator Phase 4 Extension

**File**: `agents/orchestrator.md`
**Type**: Extend existing Phase 4 (Assess)
**Purpose**: Add SARIF generation instructions after Output Structural Validation. The orchestrator produces `threats.sarif` alongside `threats.md` using the same finding data collected in Phase 3.

10 sub-sections added:
1. SARIF Generation Instructions
2. Finding IR → SARIF Result Mapping Table (FR-003)
3. Category → Rule ID Mapping Table (FR-004, resolves `info-disclosure` → `information-disclosure`)
4. Severity Mapping Table (FR-005, Note-level fix: `note`/`"0.1"`)
5. SARIF Tool Metadata Template (FR-006)
6. Rule Definition Templates (8 categories with shortDescription, fullDescription, help.text, help.markdown, tags)
7. Correlated Finding Instructions (FR-007, `relatedLocations[]`)
8. Fingerprint Computation (FR-008, SHA-256 of ruleId + component_name)
9. Dual-Location Instructions (FR-011, physicalLocation + logicalLocations)
10. JSON Structural Self-Check (FR-010)

### Component 2: Output Schema Note-Level Fix

**File**: `schemas/output.yaml`
**Type**: Modify existing SARIF Severity Mapping comment block
**Purpose**: Fix Note-level mapping from `none`/`0.0` to `note`/`0.1` per Architect review.

### Component 3: SARIF Reference Template

**File**: `templates/tachi/output-schemas/threats.sarif`
**Type**: New file
**Purpose**: Complete SARIF 2.1.0 reference structure with placeholder values for documentation and structural reference.

## Data Flow

```
Architecture Input (5 formats)
        ↓
Phase 1: Scope (extract components, trust boundaries)
        ↓
Phase 2: Determine Threats (dispatch to STRIDE + AI agents)
        ↓
Phase 3: Countermeasures (collect findings, validate, correlate)
        ↓
Phase 4: Assess
  ├── Coverage Matrix (Section 5)
  ├── Risk Summary (Section 6)
  ├── Recommended Actions (Section 7)
  ├── Output Structural Validation
  └── *** SARIF Generation (NEW) ***
        ├── Map findings → SARIF results
        ├── Map categories → SARIF rules
        ├── Map severity → SARIF levels
        ├── Populate tool metadata
        ├── Map correlations → relatedLocations
        ├── Compute partialFingerprints
        ├── Add dual locations
        └── Run JSON structural self-check
        ↓
Output: threats.md + threats.sarif (same directory)
```

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| Markdown prompt | Orchestrator prompt extension — SARIF generation instructions |
| YAML schema | Output validation contract — Note-level severity fix |
| JSON reference | SARIF 2.1.0 template for structural documentation |
| SARIF 2.1.0 | OASIS standard for static analysis results interchange |

---

### Feature 015: Threat Report Agent & Attack Trees

**Status**: Delivered (2026-03-23) | PR #16 | 29/29 tasks complete

## Components

### Component 1: Report Agent Prompt (`agents/threat-report.md`)

**Type**: New file
**Purpose**: Markdown prompt file defining the report agent's analysis methodology, output structure, and quality requirements. Transforms `threats.md` into a narrative report with Mermaid attack trees and remediation roadmap.

**YAML Frontmatter**: `agent_name: threat-report`, `category: report`, `input_schema: schemas/output.yaml`, `output_schema: schemas/report.yaml`

**8-Section Structure**: Core Mission → Input Contract → Report Generation Methodology → Attack Tree Construction Rules → Mermaid Conventions → Executive Summary Template → Correlation Group Handling → Quality Standards / Validation Checklist

### Component 2: Report Output Schema (`schemas/report.yaml`)

**Type**: New file
**Purpose**: Structural validation contract for `threat-report.md`. Defines 7 required sections, finding reference completeness rules, and attack tree file naming conventions.

### Component 3: Report Template (`templates/tachi/output-schemas/threat-report.md`)

**Type**: New file
**Purpose**: Canonical template for report output with section headings, field placeholders, and structural guidance.

### Component 4: Orchestrator Phase 5 Integration

**File**: `agents/orchestrator.md`
**Type**: Extend existing — add Phase 5 (Report) dispatch
**Purpose**: After Phase 4 (Assess) completes, dispatch report agent with `threats.md` as input in fresh context. Default-on with opt-out configuration.

## Data Flow

```mermaid
flowchart TD
    TM["threats.md<br/>(Phase 4 Output)"] --> RA["Report Agent<br/>(agents/threat-report.md)"]
    RA --> TR["threat-report.md<br/>(7 Sections)"]
    RA --> AT["attack-trees/<br/>(Standalone Files)"]

    subgraph Report Agent Processing
        Parse["Parse threats.md<br/>Sections 1-7 + 4a"] --> Exec["Executive Summary<br/>(~500 words)"]
        Parse --> Narr["Threat Analysis<br/>(Agent-by-Agent)"]
        Parse --> Cross["Cross-Cutting<br/>Theme Detection"]
        Parse --> Trees["Attack Tree<br/>Generation"]
        Parse --> Road["Remediation<br/>Roadmap"]
        Parse --> App["Appendix:<br/>Finding Reference"]
    end

    RA --> Val["Validation<br/>(schemas/report.yaml)"]
```

## Tech Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Report Agent | Markdown prompt file | Consistent with tachi agent architecture |
| Output Schema | YAML | Matches existing schema patterns |
| Attack Trees | Mermaid `flowchart TD` | Standard, GitHub-renderable |
| Template | Markdown | Same format as `templates/tachi/output-schemas/threats.md` |

---

### Feature 018: Threat Infographic Agent

**Status**: Delivered (2026-03-23) | PR #19 | 18/18 tasks complete

## Components

### Component 1: Infographic Agent Prompt (`agents/threat-infographic.md`)

**Purpose**: Markdown prompt file that defines the infographic agent's data extraction methodology, specification format, Gemini API prompt construction, and graceful fallback behavior. Invoked via the standalone `/tachi.infographic` command (Feature 039); no longer dispatched by the orchestrator pipeline. Supports three data source extraction paths (Feature 048): `compensating-controls.md` (residual risk from Coverage Matrix sub-tables + co-located `threats.md`), `risk-scores.md` (inherent risk composite scores + co-located `threats.md`), or `threats.md` standalone (qualitative severity counts). Risk labels adapt to source type: "Residual Risk", "Inherent Risk", or "Severity".

**Follows Existing Pattern**: 8-section YAML+Markdown structure matching `agents/threat-report.md` (F-015).

### Component 2: Infographic Output Schema (`schemas/infographic.yaml`)

**Purpose**: Defines the structural validation contract for `threat-infographic-spec.md`, enabling automated completeness checks. Covers 6 required sections: Metadata, Risk Distribution, Coverage Heat Map, Top Critical Findings, Architecture Threat Overlay, and Visual Design Directives.

### Component 3: Standalone `/tachi.infographic` Command (Feature 039)

**Purpose**: Infographic generation extracted from the orchestrator pipeline into a standalone `/tachi.infographic` command (Feature 039). The command auto-detects the richest available data source using a three-tier hierarchy: `compensating-controls.md` > `risk-scores.md` > `threats.md` (Feature 048). Supports explicit file override with content-based type detection and template selection. Enhancement tips guide users toward richer pipeline tiers. The orchestrator pipeline now runs 5 phases only (Phases 1-5). See Feature 039 section below for the standalone command architecture.

## Data Flow

```mermaid
flowchart TD
    CC["compensating-controls.md<br/>(Tier 1: Residual Risk)"] --> DET["Three-Tier<br/>Auto-Detection"]
    RS["risk-scores.md<br/>(Tier 2: Inherent Risk)"] --> DET
    TM["threats.md<br/>(Tier 3: Severity)"] --> DET
    DET --> IA["Infographic Agent<br/>(agents/threat-infographic.md)"]
    TM -.->|"co-located structural data"| IA
    IA --> IS["threat-{template}-spec.md<br/>(6 Sections)"]
    IA -->|"GEMINI_API_KEY set"| IMG["threat-{template}.jpg<br/>(Optional)"]
    IA -->|"No API key or error"| SKIP["Spec saved as<br/>standalone deliverable"]

    subgraph Infographic Agent Processing
        Parse["Parse data source<br/>+ co-located threats.md"] --> Meta["1. Metadata<br/>(Project, Date, Counts)"]
        Parse --> Risk["2. Risk Distribution<br/>(Residual/Inherent/Severity)"]
        Parse --> Heat["3. Coverage Heat Map<br/>(Component × Severity)"]
        Parse --> Top["4. Top Critical Findings<br/>(Up to 5)"]
        Parse --> Arch["5. Architecture<br/>Threat Overlay"]
        Meta & Risk & Heat & Top & Arch --> Design["6. Visual Design<br/>Directives"]
        Design --> Prompt["Gemini API<br/>Prompt Construction"]
    end

    IA --> Val["Validation<br/>(schemas/infographic.yaml)"]
```

## Tech Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Infographic Agent | Markdown prompt file | Consistent with tachi agent architecture |
| Output Schema | YAML | Matches existing schema patterns |
| Image Generation | Google Gemini API (`gemini-3-pro-image-preview`) | Best-in-class text rendering for data-dense infographics |
| Specification Format | Markdown (6 sections) | Human-readable, designer-consumable, Gemini-promptable |

---

### Feature 021: Platform Adapters

**Status**: Delivered (2026-03-23) | PR #22 | 40/40 tasks complete

## Architecture Pattern: Hub-and-Spoke Distribution

Feature 021 introduces a **platform adapter layer** that extends tachi's existing hub-and-spoke content model to multi-platform distribution. The core agents (`agents/`) remain the immutable hub -- the single source of truth for all 14 threat agent prompts. Each adapter is a spoke that transforms hub content into a platform-native format without modifying source agent logic.

**Key architectural principles**:
- **Content preservation**: All file-transformation adapters preserve 100% of prompt content. Only metadata format, file extensions, and internal path references change during transformation.
- **Two adapter categories**: File-transformation adapters (Claude Code, Generic, Cursor, Copilot) produce static files for installation into target platform directories. The CI integration adapter (GitHub Actions) invokes agents at runtime via LLM API -- no file transformation occurs.
- **Metadata translation**: Platform-specific frontmatter replaces tachi YAML frontmatter. Tachi-specific metadata (category, threat_class, dfd_targets, owasp_references, output_schema) is preserved in a `## Metadata` body section for file-transformation adapters that support frontmatter (Claude Code, Cursor, Copilot). The generic adapter strips all metadata for self-contained prompts.
- **Path rewriting**: Internal references (schemas, templates, sibling agents) are rewritten based on installation depth from project root. See `specs/021-platform-adapters/conventions.md` for the complete rule set.
- **Drift detection**: Each adapter includes a `VERSION` manifest (source commit SHA, generation timestamp, per-agent SHA-256 checksums) generated by `scripts/generate-adapter-version.sh`.
- **Size-aware splitting**: Copilot enforces a ~30K character limit per agent file. Oversized agents (orchestrator at ~120K chars, threat-report at ~43K chars) are split into a compact `.agent.md` file plus a `.github/instructions/` companion file with the full context.

See [ADR-015](../02_ADRs/ADR-015-platform-adapter-hub-and-spoke-distribution.md) for the formal architectural decision record.

## Components

### Component 1: Adapter Directory Structure

**Location**: `adapters/{platform-name}/` (5 subdirectories under existing `adapters/`)
**Type**: New subdirectories
**Purpose**: Platform-specific transformations of core agents into native formats for Claude Code, Cursor, Copilot, GitHub Actions, and generic LLM usage.

Each adapter contains: platform-specific agent files, installation README, VERSION manifest.

### Component 2: Claude Code Adapter (P0)

**Location**: `adapters/claude-code/`
**Purpose**: Maps 14 agents into `.claude/agents/tachi/` format with Claude Code frontmatter (`name`, `description`). Tachi metadata relocated to `## Metadata` body section. Supports parallel dispatch via Agent tool. Single `cp -r` installation.

### Component 3: Generic Adapter (P0)

**Location**: `adapters/generic/`
**Purpose**: Self-contained numbered prompt files (`00-orchestrator.md` through `13-threat-infographic.md`). Frontmatter stripped, `{{ARCHITECTURE_INPUT}}` placeholders added. Orchestrator converted to sequential workflow guide (justified FR-002 exception). Two usage modes: chat UI copy-paste and programmatic API invocation.

### Component 4: Cursor Adapter (P1)

**Location**: `adapters/cursor/`
**Purpose**: Maps agents to `.cursor/rules/tachi/` as `.mdc` rule files. Orchestrator is `alwaysApply: true`; threat agents are Agent Requested. Behavioral difference: passive context injection, not active dispatch.

### Component 5: Copilot Adapter (P1)

**Location**: `adapters/copilot/`
**Purpose**: Maps agents to `.github/agents/tachi/` as `.agent.md` files. Size constraint handling: orchestrator (120K chars) and threat-report (43K chars) split into compact agent + `.github/instructions/` file. All other agents (5-13K) fit within 30K limit.

### Component 6: GitHub Actions Adapter (P1)

**Location**: `adapters/github-actions/`
**Purpose**: CI workflow (`tachi-threat-model.yml`) triggering on architecture file changes. Invokes orchestrator via LLM API, generates `threats.md` + `threats.sarif`, uploads SARIF to GitHub Code Scanning. Architecturally distinct from file-transformation adapters.

### Component 7: VERSION File

**Location**: `adapters/{platform}/VERSION`
**Purpose**: Drift detection manifest with source commit SHA, generation date, and per-agent SHA-256 checksums.

## Data Flow

```mermaid
graph LR
    subgraph "Source of Truth (Hub)"
        A[agents/] --> |14 agents| T[Transformation Layer]
        S[schemas/] --> |5 schemas| T
        TM[templates/] --> |4 templates| T
    end

    subgraph "File-Transformation Adapters (Spokes)"
        T --> CC[adapters/claude-code/]
        T --> GN[adapters/generic/]
        T --> CU[adapters/cursor/]
        T --> CP[adapters/copilot/]
    end

    subgraph "CI Integration Adapter"
        A --> |Runtime invocation| GA[adapters/github-actions/]
        GA --> |LLM API| LLM[LLM Provider]
        LLM --> |findings| SARIF[threats.sarif]
        LLM --> |findings| MD[threats.md]
    end
```

## Tech Stack

| Technology | Purpose | Justification |
|------------|---------|---------------|
| Markdown | Agent prompt files | Native format for all target platforms |
| YAML | Frontmatter metadata, VERSION manifest | Standard for config in all target platforms |
| Bash | VERSION file generation script | Lightweight, no runtime dependencies |
| GitHub Actions YAML | CI workflow definition | Standard for GitHub CI/CD |
| `codeql/upload-sarif@v3` | SARIF upload to Code Scanning | GitHub's official SARIF upload action |

---

### Feature 035: Quantitative Risk Scoring

## Components

### Component 1: Risk Score Command

**File**: `.claude/commands/tachi.risk-score.md`
**Type**: New file
**Purpose**: `/tachi.risk-score` command definition — flag parsing, input validation, agent invocation, output summary. Follows the `/tachi.threat-model` command pattern.

### Component 2: Risk Scorer Agent

**File**: `.claude/agents/tachi/risk-scorer.md`
**Type**: New file
**Purpose**: Core scoring agent — parses threat findings, assesses 4 dimensions (CVSS 3.1, exploitability, scalability, reachability), calculates weighted composite, attaches governance fields, generates dual output.

### Component 3: Risk Scoring Schema

**File**: `schemas/risk-scoring.yaml`
**Type**: New file
**Purpose**: Scored finding schema extending `finding.yaml` with scoring dimensions, composite weights, category-level CVSS defaults, and severity band definitions aligned with `output.yaml`.

### Component 4: Output Templates

**Files**: `templates/tachi/output-schemas/risk-scores.md`, `templates/tachi/output-schemas/risk-scores.sarif`
**Type**: New files
**Purpose**: Markdown template (executive summary, scored threat table, methodology section) and SARIF template (extended property bag with per-finding composite scores and governance fields).

### Component 5: Adapter Distribution

**Files**: `adapters/claude-code/commands/tachi.risk-score.md`, `adapters/claude-code/agents/risk-scorer.md`
**Type**: New files
**Purpose**: Adapter copies for Claude Code distribution, following existing adapter pattern.

## Data Flow

```mermaid
graph LR
    A["/tachi.threat-model output<br>threats.md + threats.sarif"] --> B["/tachi.risk-score command"]
    C["architecture.md<br>(optional)"] --> B
    B --> D["risk-scorer agent"]
    D --> E["risk-scores.md"]
    D --> F["risk-scores.sarif"]
```

Pipeline: Parse threats → Extract trust zones → Score 4 dimensions per finding → Calculate composite + governance → Generate dual output. Input precedence: `threats.md` canonical, `threats.sarif` fallback.

## Tech Stack

| Technology | Purpose | Justification |
|------------|---------|---------------|
| Markdown | Command and agent prompt files | Follows existing tachi agent pattern |
| YAML | Scoring schema, category defaults, weights | Consistent with `finding.yaml`/`output.yaml` |
| SARIF 2.1.0 JSON | Machine-readable scored output | Extends existing `threats.sarif` with scoring properties |
| CVSS 3.1 | Base scoring standard | Industry standard, NVD/GitHub Advisory Database compatible |

---

### Feature 036: Compensating Controls Analysis

**Source**: `specs/036-compensating-controls/plan.md` (approved 2026-03-27)

#### Components

| Artifact | Path | Purpose |
|----------|------|---------|
| Command | `.claude/commands/tachi.compensating-controls.md` | User-facing command orchestrator |
| Agent | `.claude/agents/tachi/control-analyzer.md` | 6-phase analysis agent |
| Schema | `schemas/compensating-controls.yaml` | Control finding IR extension |
| MD Template | `templates/tachi/output-schemas/compensating-controls.md` | Markdown output structure |
| SARIF Template | `templates/tachi/output-schemas/compensating-controls.sarif` | SARIF 2.1.0 output structure |

#### Data Flow

```
risk-scores.md/sarif → Parse → Group by Component → Detect Controls (per-component batch)
     → Map & Classify → Recommend + Residual Risk → Output (MD + SARIF)
```

#### Tech Stack

| Technology | Purpose | Justification |
|------------|---------|---------------|
| Markdown | Command and agent prompt files | Follows `/tachi.risk-score` pattern |
| YAML | Control finding schema | Extends `risk-scoring.yaml` |
| SARIF 2.1.0 JSON | Machine-readable control analysis | Supersedes `risk-scores.sarif` in alert chain |

---

### Feature 039: Standalone Infographic Command

## Components

### Component 1: `/tachi.infographic` Command (NEW)

**File**: `.claude/commands/tachi.infographic.md`
**Pattern**: Follows `/tachi.risk-score` command structure (Step 0 → Step 1 → Step 2 → Step 3)

Steps: Parse flags (`--template`, `--output-dir`) → Detect richest data source via three-tier hierarchy (`compensating-controls.md` > `risk-scores.md` > `threats.md`) → Display enhancement tip for next tier → Invoke infographic agent in fresh context → Report results.

### Component 2: Infographic Agent Enhancement (MODIFY)

**File**: `.claude/agents/tachi/threat-infographic.md`
**Change**: Three-path data extraction (Feature 048) — supports `compensating-controls.md` (residual risk from Coverage Matrix sub-tables), `risk-scores.md` (inherent risk composite scores), or `threats.md` (qualitative severity). When `compensating-controls.md` or `risk-scores.md` is primary, reads co-located `threats.md` for structural/spatial data. Risk labels adapt to source type ("Residual Risk" / "Inherent Risk" / "Severity").

### Component 3: /tachi.threat-model Pipeline Cleanup (MODIFY)

**File**: `.claude/commands/tachi.threat-model.md`
**Change**: Remove Phase 6 (infographic generation), associated flags (`--infographic-template`, `--skip-infographic`), and `TACHI_SKIP_INFOGRAPHIC` env var. Add post-pipeline hint directing users to `/tachi.infographic`.

### Component 4: Orchestrator Phase 6 Removal (MODIFY)

**File**: `.claude/agents/tachi/orchestrator.md`
**Change**: Remove Phase 6 dispatch section, update pipeline phase count from 6 to 5.

### Component 5: Platform Adapter Updates (MODIFY)

Update all adapter variants (Claude Code, Copilot, Cursor, Generic) for orchestrator, threat-model command, and infographic agent to reflect 5-phase pipeline and dual-path extraction.

## Data Flow

```
User → /tachi.infographic → Parse flags → Three-Tier Auto-Detection
         │
    ┌────┼────────────┐
    ▼    ▼            ▼
 compensating-   risk-scores.md   threats.md
 controls.md     + threats.md     (standalone)
 + threats.md        │                │
    │                │                │
    └────────┬───────┘                │
             └────────┬───────────────┘
                      ▼
  Enhancement Tip (next tier suggestion, suppressed for explicit paths)
                      ▼
  Infographic Agent (fresh context)
  → Extract data (residual/inherent/severity) → Apply template → Generate spec → Attempt Gemini image
                      ▼
  threat-{name}-spec.md (labels: Residual Risk / Inherent Risk / Severity)
  + threat-{name}.jpg (optional)
```

#### Tech Stack

| Technology | Purpose | Justification |
|------------|---------|---------------|
| Markdown | Command and agent prompt files | Follows `/tachi.risk-score` command pattern |
| YAML | Infographic schema | Existing `schemas/infographic.yaml` unchanged |
| Gemini API | Optional image generation | Existing integration preserved (ADR-014) |

---

### Feature 048: Infographic Tiered Pipeline Auto-Detection & Residual Risk

**Status**: Delivered (2026-03-28) | PR #49 | 27/27 tasks complete

## Components

### Component 1: `/tachi.infographic` Command — Three-Tier Detection (MODIFY)

**File**: `.claude/commands/tachi.infographic.md`
**Change**: Extended two-tier auto-detection to three-tier hierarchy (`compensating-controls.md` > `risk-scores.md` > `threats.md`). Added content-based type detection for explicit paths (Coverage Matrix header + Residual Score column). Added tiered enhancement tips guiding users toward richer pipeline tiers. Updated error messages to list all three expected file formats. Extended co-location check to trigger for `compensating-controls.md` (same pattern as `risk-scores.md`). Detection-level failures fall through gracefully; extraction-level failures halt with warning.

### Component 2: Infographic Agent — Compensating Controls Extraction Path (MODIFY)

**File**: `.claude/agents/tachi/threat-infographic.md`
**Change**: Added third data source extraction path for `compensating-controls.md`. Residual risk scores extracted from Coverage Matrix sub-tables (Critical, High, Medium, Low severity bands). Risk labels adapt to source type: "Residual Risk" (compensating-controls), "Inherent Risk" (risk-scores), "Severity" (threats). Baseball-card template includes risk reduction percentage in summary zone when compensating-controls is the source. Agent metadata updated with `compensating-controls` data source type declaration.

## Data Flow

```
User → /tachi.infographic [--template] [--output-dir] [explicit-path]
         │
         ▼
  Three-Tier Auto-Detection (or content-based detection for explicit paths)
  Priority: compensating-controls.md > risk-scores.md > threats.md
         │
         ├── Tier 1: compensating-controls.md → residual risk from Coverage Matrix
         ├── Tier 2: risk-scores.md → inherent risk composite scores
         └── Tier 3: threats.md → qualitative severity counts
         │
         ▼
  Enhancement Tip (auto-detect only, suppressed for explicit paths)
  - Tier 3 → "Run /tachi.risk-score for quantitative scores"
  - Tier 2 → "Run /tachi.compensating-controls for residual risk"
  - Tier 1 → "Full pipeline detected — visualizing residual risk"
         │
         ▼
  Co-location check (Tier 1 & 2: threats.md required for structural data)
         │
         ▼
  Infographic Agent (fresh context, primary + secondary files)
  → Extract data → Apply risk labels → Apply template → Generate spec → Attempt Gemini image
         │
         ▼
  threat-{template}-spec.md (labels match source tier)
  + threat-{template}.jpg (optional, Gemini API)
```

#### Tech Stack

| Technology | Purpose | Justification |
|------------|---------|---------------|
| Markdown | Command and agent prompt files | No new technologies; extends existing prompt files |
| Content-based detection | Three-tier hierarchy with header/column markers | Enables explicit path type detection without filename dependency |

---

### Feature 053: Risk Reduction Funnel

## Components

### Component 1: Design Template (`infographic-risk-funnel.md`)

**File**: `templates/tachi/infographics/infographic-risk-funnel.md`
**Type**: New file
**Purpose**: Complete visual specification for 4-tier risk reduction funnel — layout, colors, typography, zone specs, Gemini prompt.

Follows the established 9-section template pattern:
1. Frontmatter comment with purpose statement
2. ASCII layout diagram (16:9 landscape, header + funnel zone + metrics sidebar + footer)
3. Style table (dark theme #1E293B, consistent with baseball-card)
4. Color palette (standard severity colors + ghost tier styling)
5. Typography table
6. Zone specifications (Header, Funnel with 4 tiers, Metrics Sidebar, Footer)
7. Gemini Prompt Template (photorealistic 3D funnel, aesthetic-first)
8. Gemini API Configuration
9. Accessibility section

### Component 2: Agent Registry Update

**File**: `.claude/agents/tachi/threat-infographic.md`
**Type**: Update
**Purpose**: Register risk-funnel template and add funnel-specific data extraction instructions.

Changes: template registry entry, description update, Available Templates table row, `all` behavior (2→3 templates), Section 5 funnel-tier format, graceful degradation logic.

### Component 3: Command Registry Update

**File**: `.claude/commands/tachi.infographic.md`
**Type**: Update
**Purpose**: Add `risk-funnel` as valid `--template` value.

Changes: valid template list, invalid template error message, `all` description.

## Data Flow

```mermaid
graph TD
    A["/tachi.infographic --template risk-funnel"] --> B[Command: Parse Args]
    B --> C[Auto-detect Data Source]
    C --> D{Data Source Type?}
    D -->|compensating-controls.md| E[4-tier mode]
    D -->|risk-scores.md| F[3-tier mode]
    D -->|threats.md| G[1-tier mode]
    E --> H[Agent: Load risk-funnel template]
    F --> H
    G --> H
    H --> I[Extract tier data per source]
    I --> J[Generate 6-section spec]
    J --> K{GEMINI_API_KEY?}
    K -->|Yes| L[Generate 3D funnel image]
    K -->|No| M[Spec only]
    L --> N[Output: threat-risk-funnel-spec.md + .jpg]
    M --> O[Output: threat-risk-funnel-spec.md]
```

## Tech Stack

| Technology | Purpose | Justification |
|------------|---------|---------------|
| Markdown | Design template, agent prompt, command prompt | Extends existing markdown-based template system |
| YAML | Schema validation, API configuration | Consistent with infographic.yaml v1.0 |
| Gemini API | Photorealistic 3D funnel image rendering | Same pipeline as existing templates (best-effort) |

---

### Feature 054: Security Assessment PDF Booklet

## Components

### Component 1: Command File (`security-report.md`)

User-facing entry point following the 4-step command pattern (parse → validate → generate → report). Handles `--output-dir` and `--title` flags, validates Typst installation, auto-detects 8 artifact types in target directory (including `attack-trees/` directory, Feature 112), and invokes the report-assembler agent.

### Component 2: Agent File (`report-assembler.md`)

Orchestrates the report generation pipeline: invokes `scripts/extract-report-data.py` for deterministic markdown-to-Typst data extraction (Feature 067 replaced inline LLM parsing), then invokes `typst compile` to produce `security-report.pdf`. The Python script handles all artifact parsing (YAML frontmatter, markdown tables, section content), 3-tier data source preference for Findings Detail, severity counting, scope extraction, and internal consistency validation.

### Component 3: Schema File (`security-report.yaml`)

Declarative page assembly rules defining artifact detection patterns, page sequence, page dimensions (US Letter portrait + custom 16:9 landscape), data source tiers with tier-specific columns, and conditional inclusion rules.

### Component 4: Typst Templates (`templates/tachi/security-report/`)

Modular rendering templates: `main.typ` (orchestrator with conditional page inclusion), `shared.typ` (severity colors, typography, headers/footers), and per-page modules (`cover.typ`, `executive-summary.typ`, `full-bleed.typ`, `findings-detail.typ`, `control-coverage.typ`, `remediation-roadmap.typ`, `attack-path.typ` -- Feature 112).

## Data Flow

```mermaid
graph LR
    subgraph Input Artifacts
        T[threats.md]
        TR[threat-report.md]
        RS[risk-scores.md]
        CC[compensating-controls.md]
        AT[attack-trees/*.md]
        I1[threat-risk-funnel.jpg]
        I2[threat-baseball-card.jpg]
        I3[threat-system-architecture.jpg]
    end

    subgraph Command
        CMD[/tachi.security-report]
    end

    subgraph Agent
        DET[Artifact Detection]
    end

    subgraph Script["Python Script (deterministic)"]
        PARSE["extract-report-data.py"]
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
    AT --> CMD
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

| Technology | Purpose | Justification |
|------------|---------|---------------|
| Typst 0.11.x-0.12.x | PDF compilation from templates | No browser dependency, reproducible, portable, native image embedding |
| Markdown | Command and agent specifications | Extends existing tachi command/agent pattern |
| YAML | Page assembly schema | Consistent with existing schemas (output.yaml, infographic.yaml) |

---

### Feature 060: Professional PDF Security Assessment Report with tachi Branding

## Components

### Component 1: Theme Token System
- `theme.typ` — new file centralizing 7 brand colors, 2 logo paths, 3 font stacks
- `shared.typ` — refactored to import theme.typ; retains color aliases (`color-header-bg` → `brand-primary`)
- Severity colors remain as functional constants in shared.typ (not brand tokens)

### Component 2: Heading Migration
- All section titles migrated from `text()` to `heading()` elements across 9 templates
- Enables Typst `outline()` for auto-generated TOC
- Full-bleed pages use `hide(heading(...))` for phantom TOC entries

### Component 3: New Page Templates
- `disclaimer.typ` — legal disclaimer with 4 standard notice sections
- `toc.typ` — auto-generated table of contents via Typst `outline()`
- `methodology.typ` — STRIDE + AI threat categories, visual probability x impact matrix, conditional 4D scoring
- `scope.typ` — component inventory, data flows, trust boundaries from threats.md Sections 1-2

### Component 4: Report Assembler Updates
- New parsing: threats.md Section 1 (components, data flows) and Section 2 (trust boundaries)
- Brand asset detection: `brand/final/*.png` logo files
- Config generation: `report-config.typ` with user overrides
- New report-data.typ variables: scope data arrays, logo paths, visibility flags

### Component 5: Schema Update
- `security-report.yaml` v1.0 → v1.1
- New page types, scope data contract, theme token contract, config variables

## Data Flow

```
threats.md + brand/*.png + optional artifacts
    → Report Assembler (detects artifacts)
    → python3 scripts/extract-report-data.py (deterministic parsing, Feature 067)
    → report-data.typ + report-config.typ
    → Typst compile (main.typ orchestrates 13 page types)
    → security-report.pdf
```

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Typst | 0.11+ | PDF rendering with `outline()`, `image()`, `hide()` |
| PNG | N/A | Brand logo assets (Typst auto-detects PNG vs JPEG from headers); attack tree diagram images rendered by `mmdc` (Feature 112) |
| YAML | N/A | Schema definitions (security-report.yaml v1.1) |

---

### Feature 067: Deterministic Report Data Extraction

## Components

### Component 1: Python Extraction Script (`scripts/extract-report-data.py`)

**Type**: New file
**Purpose**: Deterministic, stdlib-only Python 3.9+ script that replaces LLM-based markdown parsing in the report-assembler agent. Parses all 4 pipeline markdown artifacts (threats.md, risk-scores.md, compensating-controls.md, threat-report.md) using regex-based extraction and writes a complete Typst data file (report-data.typ) with all variable bindings.

Key properties:
- **Byte-identical output**: Same inputs always produce the same report-data.typ (no LLM variance)
- **3-tier severity source**: Tier 1 compensating-controls.md, Tier 2 risk-scores.md, Tier 3 threats.md
- **Internal consistency validation**: Severity sum checks, scope count checks, unique finding ID checks
- **Exit codes**: 0 success, 1 missing required artifact, 2 validation failure

### Component 2: Report Assembler Agent Update (`report-assembler.md`)

**Type**: Modified
**Purpose**: Updated to invoke the Python script instead of performing inline LLM parsing. The agent now handles artifact detection, script invocation, and Typst compilation, while all data extraction is delegated to the deterministic script.

## Data Flow

```
threats.md + optional artifacts (risk-scores.md, compensating-controls.md, threat-report.md)
    → Report Assembler (artifact detection)
    → python3 scripts/extract-report-data.py --target-dir <dir> --output-dir <dir>
    → report-data.typ (deterministic, byte-identical on same inputs)
    → Typst compile (main.typ orchestrates page types)
    → security-report.pdf
```

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.9+ (stdlib only) | Deterministic markdown parsing and Typst data generation; zero external dependencies |

---

### Feature 071: Deterministic Infographic Data Extraction

## Components

### Component 1: Shared Parser Module (`scripts/tachi_parsers.py`)

**Type**: New file (extracted from Feature 067's `extract-report-data.py`)
**Purpose**: Shared parser module (~750 lines) providing deterministic parsers for markdown tables, YAML frontmatter, severity distributions, findings, scope data, and compensating controls. Both `extract-report-data.py` and `extract-infographic-data.py` import the same parsing functions, guaranteeing identical interpretation of the same source artifacts across report and infographic pipelines.

Key exports:
- **Table parsing**: `parse_markdown_table()`, `_find_table_with_column()`
- **Frontmatter**: `parse_frontmatter()`, `parse_project_name()`
- **Artifact detection**: `detect_artifacts()`, `determine_tier()`
- **Severity**: `parse_threats_severity()`, `parse_risk_scores_severity()`
- **Findings**: `parse_threats_findings()`, `parse_risk_scores_findings()`
- **Scope/controls**: `parse_scope_data()`, `parse_compensating_controls_md()`, `parse_component_distribution()`
- **Constants**: `SEVERITY_ORDER`, `STRIDE_PREFIXES`, exit codes

### Component 2: Infographic Extraction Script (`scripts/extract-infographic-data.py`)

**Type**: New file (~1,060 lines)
**Purpose**: Deterministic, stdlib-only Python 3.9+ script that replaces LLM-based data extraction in the threat-infographic agent. Parses pipeline markdown artifacts and writes JSON data files with all variable bindings needed by infographic templates (baseball-card, system-architecture, risk-funnel).

Key properties:
- **Byte-identical output**: Same inputs always produce the same JSON (no LLM variance)
- **3-tier data source auto-detection**: Tier 1 compensating-controls.md, Tier 2 risk-scores.md, Tier 3 threats.md
- **Largest Remainder Method**: Integer percentage rounding guaranteeing sums equal exactly 100, with deterministic tie-breaking (lexicographic label order)
- **Per-template data**: Generates template-specific `template_data` object (risk weights for baseball-card, architecture overlay for system-architecture, funnel stages for risk-funnel)
- **Internal consistency validation**: Severity sum checks, finding ID cross-checks, heat map total consistency
- **Exit codes**: 0 success, 1 missing required artifact, 2 validation failure

### Component 3: Threat-Infographic Agent Update (`agents/threat-infographic.md`)

**Type**: Modified
**Purpose**: Updated to invoke the Python extraction script instead of performing inline LLM-based data extraction. The agent now runs `scripts/extract-infographic-data.py`, reads the resulting JSON, and generates the infographic specification. No manual fallback is permitted on script failure (exit code 1 or 2).

### Component 4: Refactored Report Extraction Script (`scripts/extract-report-data.py`)

**Type**: Modified
**Purpose**: Refactored to import shared parsers from `tachi_parsers.py` instead of containing inline implementations. All parsing logic moved to the shared module; the script retains only Typst-specific output formatting.

## Data Flow

```
threats.md + optional artifacts (risk-scores.md, compensating-controls.md)
    → Infographic Agent (template selection)
    → python3 scripts/extract-infographic-data.py --target-dir <dir> --template <name> --output <path>
        → tachi_parsers.py (shared parsing: frontmatter, tables, severity, findings, scope)
    → infographic-data.json (deterministic, byte-identical on same inputs)
    → Agent reads JSON and generates specification
    → threat-{template-name}-spec.md + optional threat-{template-name}.jpg (Gemini API)
```

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.9+ (stdlib only) | Deterministic markdown parsing and JSON data generation; zero external dependencies |
| JSON | N/A | Structured data interchange between extraction script and infographic agent |

---

### Feature 074: Baseline-Aware Pipeline

**Status**: Delivered (2026-04-01) | PR #79 | 36/36 tasks complete

## Components

### Component 1: Schema Extensions

**Files modified**: `schemas/finding.yaml`, `schemas/risk-scoring.yaml`, `schemas/compensating-controls.yaml`
**Type**: Extended existing schemas with baseline-aware fields
**Purpose**: Extend the finding IR chain (finding -> scored_finding -> controlled_finding) with delta tracking and score inheritance fields.

| Schema | New Fields | Purpose |
|--------|-----------|---------|
| `finding.yaml` | `delta_status` (NEW/UNCHANGED/UPDATED/RESOLVED), `baseline_run_id` (nullable string) | Finding lifecycle tracking relative to baseline |
| `risk-scoring.yaml` | `score_source` (inherited/fresh), `score_bounds` (min/max object, nullable) | Score inheritance for stable findings, bounded scoring for new findings |
| `compensating-controls.yaml` | `control_carry_forward` (boolean), `rescan_scope` (full/incremental) | Control status inheritance and incremental re-scan scoping |

### Component 2: Coverage Checklists Schema

**File**: `schemas/coverage-checklists.yaml`
**Type**: New file
**Purpose**: Static configuration defining minimum required threat categories per DFD element type. Consumed by the orchestrator's coverage gate (Phase 4) to verify that all required threat categories have been evaluated for each component.

6 component types:
- **Standard DFD types** (4): external_entity (S, R), process (all 6 STRIDE), data_store (T, I, D), data_flow (T, I, D)
- **AI subtypes** (2): llm_process (all STRIDE + llm, detected via keywords: llm, language model, gpt, claude, ai model, inference), mcp_server (all STRIDE + agentic, detected via keywords: mcp, model context protocol, tool server, plugin host)

AI subtype detection takes precedence over standard type when keywords match.

### Component 3: Orchestrator Agent Enhancement

**File modified**: `.claude/agents/tachi/orchestrator.md`
**Type**: Extended existing agent with 4-phase baseline pipeline
**Purpose**: Transform the stateless OWASP pipeline into a baseline-aware pipeline with finding stability, delta annotations, and coverage assurance.

New/modified phases:
- **Phase 0 (new)**: Baseline Detection -- detect baseline from `--baseline` flag or auto-detect existing `threats.md` in output directory. Parse finding registry with fingerprint extraction. Graceful degradation to stateless mode on invalid baseline.
- **Phase 1 (modified)**: Carry-Forward -- verify each baseline finding against current architecture, classify as UNCHANGED/UPDATED/RESOLVED. Build coverage summary (component -> covered categories).
- **Phase 2 (modified)**: Isolated Discovery -- spawn discovery context with architecture + coverage summary only (no full finding text, preventing anchoring bias). Discover uncovered component-category pairs.
- **Phase 3 (new)**: Merge + Dedup -- match Phase 2 findings against baseline by (component, threat_category, primaryLocationLineHash). Duplicate findings discarded (baseline version wins). New findings assigned sequential IDs continuing from highest existing per category.
- **Phase 4 (new)**: Coverage Gate -- load `schemas/coverage-checklists.yaml`, check merged findings against required categories per component type. Flag gaps as warnings, trigger targeted re-analysis for missing categories (single pass, no retry loop).

### Component 4: Risk Scorer Agent Enhancement

**File modified**: `.claude/agents/tachi/risk-scorer.md`
**Type**: Extended existing agent with delta-aware scoring
**Purpose**: Support score inheritance for stable findings and bounded scoring for new findings.

Delta-aware scoring rules:
- **UNCHANGED**: Inherit all scores (composite, CVSS vector, governance fields) verbatim from baseline. `score_source: inherited`.
- **UPDATED**: Re-score fresh using full 4-dimensional model. `score_source: fresh`.
- **NEW**: Score fresh with CVSS base bounded within +/-1.0 of category defaults from `schemas/risk-scoring.yaml`. `score_source: fresh`.
- **RESOLVED**: Retain last-known scores for historical reference.

### Component 5: Control Analyzer Agent Enhancement

**File modified**: `.claude/agents/tachi/control-analyzer.md`
**Type**: Extended existing agent with incremental re-scan
**Purpose**: Support control status carry-forward for stable findings and incremental re-scanning for changed findings.

Carry-forward rules:
- **UNCHANGED**: Carry forward control_status, control_evidence, reduction_factor, and residual_score from baseline. `control_carry_forward: true`.
- **NEW/UPDATED**: Full re-scan against target codebase. `control_carry_forward: false`.
- **Incremental scope**: When `rescan_scope: incremental`, only NEW and UPDATED findings trigger codebase scanning.

### Component 6: Orchestration Skill Domain Knowledge

**Files modified**: `.claude/skills/tachi-orchestration/SKILL.md`, `.claude/skills/tachi-risk-scoring/SKILL.md`, `.claude/skills/tachi-control-analysis/SKILL.md`
**New file**: `.claude/skills/tachi-orchestration/references/baseline-correlation.md`
**Type**: Extended existing skills + new reference file
**Purpose**: Add baseline-aware domain knowledge to the three tachi methodology skills.

| Skill | Updates | New Reference |
|-------|---------|---------------|
| `tachi-orchestration` | Baseline detection rules, finding registry format, coverage gate specification in SKILL.md | `references/baseline-correlation.md` -- file detection priority, finding registry extraction, fingerprint computation, matching algorithm with tie-breaking, delta classification rules, sequential ID assignment, baseline metadata extraction |
| `tachi-risk-scoring` | Score inheritance rules, bounded scoring specification, score_source field derivation | None (rules added to SKILL.md) |
| `tachi-control-analysis` | Carry-forward rules, incremental re-scan specification, rescan_scope derivation | None (rules added to SKILL.md) |

### Component 7: Output Template Updates

**Files modified**: All 6 output templates (3 markdown + 3 SARIF)
**Type**: Extended with baseline-aware sections and properties
**Purpose**: Surface delta annotations, score provenance, and control inheritance in pipeline outputs.

| Template | Baseline Extensions |
|----------|-------------------|
| `threats.md` | Baseline frontmatter block (source, date, finding_count), delta_status column in threat tables, RESOLVED findings section, coverage gate results section |
| `risk-scores.md` | score_source column (inherited/fresh), baseline reference in frontmatter |
| `compensating-controls.md` | control_carry_forward column, rescan_scope in frontmatter |
| `threats.sarif` | `baselineRunId` in partialFingerprints, `baselineState` property per result (new/unchanged/updated/absent) |
| `risk-scores.sarif` | `score_source` property per result |
| `compensating-controls.sarif` | `carry_forward` property per result |

## Data Flow

```mermaid
flowchart TD
    A[Architecture Input] --> B{Baseline Exists?}
    B -->|No| C[Stateless Mode<br>Current behavior]
    B -->|Yes| D[Phase 0: Baseline Detection]
    
    D --> D1[Parse baseline threats.md]
    D1 --> D2[Extract finding registry<br>with fingerprints]
    
    D2 --> E[Phase 1: Carry-Forward]
    E --> E1[Verify each finding<br>against current architecture]
    E1 --> E2[Classify: UNCHANGED<br>UPDATED / RESOLVED]
    E2 --> E3[Build coverage summary]
    
    E3 --> F[Phase 2: Isolated Discovery]
    F --> F1[Architecture + coverage<br>summary ONLY]
    F1 --> F2[Discover uncovered<br>component-category pairs]
    
    F2 --> G[Phase 3: Merge + Dedup]
    G --> G1[Match by fingerprint]
    G1 --> G2{Duplicate?}
    G2 -->|Yes| G3[Discard — baseline wins]
    G2 -->|No| G4[Assign sequential ID<br>Mark as NEW]
    G3 --> G5[Merged Finding Set]
    G4 --> G5
    E2 --> G5
    
    G5 --> H[Phase 4: Coverage Gate]
    H --> H1[Load coverage-checklists.yaml]
    H1 --> H2[Check required categories<br>per component type]
    H2 --> H3{All covered?}
    H3 -->|Yes| H4[Pass]
    H3 -->|No| H5[Targeted re-analysis]
    H5 --> H4
    
    H4 --> I[Output Generation]
    I --> I1[threats.md + threats.sarif<br>with delta annotations]
    I --> I2[risk-scores.md + .sarif<br>with score inheritance]
    I --> I3[compensating-controls.md + .sarif<br>with carry-forward]
    
    C --> I
```

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| Markdown + YAML | Agent definitions, skill domain knowledge, schema contracts, output templates -- no compiled code |
| SARIF 2.1.0 `partialFingerprints` | Cross-run finding correlation via deterministic SHA-256 fingerprints |
| YAML schema (`coverage-checklists.yaml`) | Static coverage gate configuration -- required categories per component type |

---

### Feature 078: Agent Context Optimization

## Components

### Component 1: Agent Definitions (6 files restructured)

**Files**: `.claude/agents/tachi/{orchestrator,risk-scorer,control-analyzer,threat-report,threat-infographic,report-assembler}.md`
**Type**: Restructured existing files
**Purpose**: Convert 6 monolithic agent prompts to lean definitions containing only orchestration logic, with domain knowledge loaded on-demand from skill references.

Each restructured agent retains: role identity (2-3 lines), workflow skeleton (phases, decision points), skill loading instructions (navigation table + MANDATORY Read at branch points), output format summary, constraints and error handling. Domain-specific content (scoring tables, template specifications, detection patterns, formatting rules) moved to skill reference files.

| Agent | Before | After | Reduction | Skill Target |
|-------|--------|-------|-----------|--------------|
| orchestrator | 1,286 lines | ~500 lines | ~61% | tachi-orchestration |
| risk-scorer | 1,093 lines | ~500 lines | ~54% | tachi-risk-scoring |
| control-analyzer | 973 lines | ~500 lines | ~49% | tachi-control-analysis |
| threat-report | 800 lines | ~300 lines | ~63% | tachi-threat-reporting |
| threat-infographic | 775 lines | ~300 lines | ~61% | tachi-infographics |
| report-assembler | 654 lines | ~300 lines | ~54% | tachi-report-assembly |

### Component 2: Skill Reference Files (15 new + 6 enhanced)

**Directories**: `.claude/skills/tachi-*/references/`
**Type**: New reference files in 4 new skill directories + enhanced references in 2 existing skill directories
**Purpose**: Domain knowledge loaded on-demand via Read tool at specific pipeline phases, following the [On-Demand Reference File Segmentation](../03_patterns/README.md#pattern-on-demand-reference-file-segmentation) pattern.

New skill directories (Feature 078):
- `tachi-report-assembly/references/` -- 3 files: brand-asset-guidelines.md, typst-artifacts.md, typst-template-contract.md
- `tachi-threat-reporting/references/` -- 3 files: narrative-templates.md, attack-tree-construction.md, attack-tree-examples.md
- `tachi-infographics/references/` -- 4 files: infographic-specifications.md, template-specific-formats.md, gemini-prompt-construction.md, visual-design-system.md
- `tachi-shared/references/` -- 3 files: severity-bands-shared.md, stride-categories-shared.md, finding-format-shared.md

Enhanced existing skill directories (Feature 078):
- `tachi-orchestration/references/` -- 5 new files added: format-detection.md, dfd-classification.md, trust-boundaries.md, coverage-requirements.md, coverage-matrix-model.md
- `tachi-risk-scoring/references/` -- 3 new files added: output-formatting.md, reachability-analysis.md, trust-zones.md

### Component 3: Shared Definitions (tachi-shared)

**Directory**: `.claude/skills/tachi-shared/`
**Type**: New skill directory
**Purpose**: Single-source-of-truth reference files consumed by multiple agents, preventing cross-agent drift in severity thresholds, category definitions, and finding format specifications.

| Reference | Consumers | Content |
|-----------|-----------|---------|
| `severity-bands-shared.md` | orchestrator, risk-scorer, control-analyzer | Severity band thresholds, SLA mapping, risk disposition rules |
| `stride-categories-shared.md` | orchestrator, all 6 STRIDE agents | STRIDE+AI category definitions (8 categories), DFD element applicability matrix |
| `finding-format-shared.md` | all 17 agents | Finding IR format specification, required/optional fields, validation rules |

### Component 4: Model Field Governance (17 agents)

**Files**: All `.claude/agents/tachi/*.md` YAML frontmatter
**Type**: Modified existing files (additive)
**Purpose**: Explicit `model: sonnet` field in YAML frontmatter of all 17 agent definitions, enabling intentional model-to-task matching, cost tracking, and reproducibility.

Applies to: 6 STRIDE agents, 5 AI agents, orchestrator, risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler.

### Component 5: Best Practices Document

**File**: `.claude/agents/tachi/_TACHI_AGENT_BEST_PRACTICES.md`
**Type**: New file
**Purpose**: Codified conventions for agent definition structure, skill reference organization, shared definition governance, and model field assignment. Serves as contributor guide for future agent authoring.

## Data Flow

```
Architecture Description
        |
        v
 Orchestrator Agent (<=500 lines)
  -- Read --> tachi-orchestration/references/   (9 files)
  -- Read --> tachi-shared/references/          (3 files)
        |
        v (dispatches)
 11 Leaf Agents (<=200 lines, unchanged behavior)
  -- Read --> tachi-shared/references/          (finding format, categories)
        |
        v (findings)
 Risk-Scorer Agent (<=500 lines)
  -- Read --> tachi-risk-scoring/references/    (6 files)
  -- Read --> tachi-shared/references/          (severity bands)
        |
        v (scored findings)
 Control-Analyzer Agent (<=500 lines)
  -- Read --> tachi-control-analysis/references/ (3 files)
  -- Read --> tachi-shared/references/          (severity bands)
        |
        v (controls + residual risk)
 Threat-Report Agent (<=300 lines)
  -- Read --> tachi-threat-reporting/references/ (3 files)
        |
 Threat-Infographic Agent (<=300 lines)
  -- Read --> tachi-infographics/references/    (4 files)
        |
 Report-Assembler Agent (<=300 lines)
  -- Read --> tachi-report-assembly/references/ (3 files)
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Agent definitions | Markdown + YAML frontmatter (with `model:` field) | Orchestration logic, workflow skeletons, model governance |
| Skill references | Markdown | Domain knowledge, templates, patterns |
| Shared references | Markdown | Deduplicated cross-agent definitions (severity, categories, format) |
| Regression testing | Pipeline output comparison | Structural equivalence verification |

---

### Feature 066: Install Script and Version Tagging

## Components

### C1: Install Script (`scripts/install.sh`)

Bash 3.2+ script (~200 lines) that copies all distributable files from a tachi source directory to the target project. Auto-detects source from script location using `${BASH_SOURCE[0]}` pattern (matching `generate-adapter-version.sh`). Supports `--source`, `--version`, and `--help` flags via manual `while/case` parsing.

Key mechanisms:
- Manifest parsing: extracts paths between `<!-- BEGIN MANIFEST -->` / `<!-- END MANIFEST -->` markers
- Version checkout: dirty tree check → record branch → trap EXIT → checkout tag → copy → restore
- File copy: `mkdir -p` + `cp -r` for each manifest path; additive only (never deletes)

### C2: Machine-Parseable Manifest Section

HTML comment-delimited section in `INSTALL_MANIFEST.md` with one distributable path per line. Directories end with `/`, individual files do not. Parsed by the install script instead of the human-readable markdown tables.

### C3: README Quick Start Update

Updated Step 2 with single install command as primary path. Manual `cp -r` commands preserved in collapsible `<details>` block.

### C4: Developer Guide Update

`docs/guides/DEVELOPER_GUIDE_TACHI.md` install section updated to match README.

### C5: Version Tagging

First annotated tag `v4.0.0` on main after PR merge. Enables `git describe --tags --always` for version reporting.

## Data Flow

```
User runs install.sh from target project root
  │
  ├─ 1. Auto-detect SOURCE_DIR from BASH_SOURCE (or --source override)
  ├─ 2. If --version: dirty tree check → record branch → trap EXIT → checkout tag
  ├─ 3. Parse INSTALL_MANIFEST.md (machine-parseable section)
  ├─ 4. For each path: mkdir -p + cp -r → target directory
  ├─ 5. Report: version, file count, source path
  └─ 6. If --version: trap restores original branch on EXIT
```

## Tech Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Script | Bash 3.2+ | macOS default, matches existing tachi scripts |
| File copy | `cp -r`, `mkdir -p` | Standard coreutils, no external deps |
| Version detection | `git describe --tags --always` | Version string from nearest tag |
| Dirty tree check | `git status --porcelain` | Machine-parseable, catches all change types |
| Branch restore | `trap cleanup EXIT` | Guaranteed execution on all exit paths |
| Manifest parsing | `sed`/`awk` between HTML comment markers | No external parser, Bash 3.2 compatible |

---

### Feature 086: Automated Release Tagging

## Components

### Component 1: GitHub Actions Workflow (`.github/workflows/release-please.yml`)

**Purpose**: Triggers release-please on every push to `main` branch.

**Configuration**:
- Trigger: `on: push: branches: [main]`
- Permissions: `contents: write`, `pull-requests: write`
- Action: `googleapis/release-please-action@v4`
- Release type: `simple`

### Component 2: Release Configuration (`release-please-config.json`)

**Purpose**: Controls release-please behavior — release type, CHANGELOG grouping, versioning.

### Component 3: Version Manifest (`.release-please-manifest.json`)

**Purpose**: Tracks current released version. Initial value: `{"." : "4.0.0"}`.

## Data Flow

```
Developer merges PR to main
         │
         ▼
GitHub Actions triggers release-please.yml
         │
         ▼
release-please reads .release-please-manifest.json (current: 4.0.0)
         │
         ▼
Analyzes conventional commits since v4.0.0
         │
         ├─ No releasable commits → Exit (no action)
         │
         └─ Releasable commits found
              │
              ▼
         Creates/updates Release PR
         (PR body = grouped CHANGELOG entries)
              │
              ├─ Maintainer does NOT merge → PR stays open, accumulates
              │
              └─ Maintainer merges Release PR
                   │
                   ▼
              release-please creates:
              1. Git tag (e.g., v4.1.0)
              2. GitHub Release with notes
              3. Updates CHANGELOG.md
              4. Updates .release-please-manifest.json
```

## Tech Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| CI/CD | GitHub Actions | Already the platform; zero additional infrastructure |
| Release Automation | release-please v4 | Industry standard (40k+ stars), maintained by Google |
| Configuration | JSON | release-please's native config format |
| Versioning | Semantic Versioning | Matches existing v4.0.0 convention |

---

### Feature 084: MAESTRO Layer Mapping

## Components

### Component 1: MAESTRO Shared Reference File
**File**: `.claude/skills/tachi-shared/references/maestro-layers-shared.md`
**Type**: New file
**Purpose**: Shared reference defining the CSA MAESTRO seven-layer taxonomy with keyword-to-layer mappings for component classification during Phase 1.

### Component 2: Finding IR Schema Extension
**File**: `schemas/finding.yaml`
**Type**: Modification
**Purpose**: Add optional `maestro_layer` field (string enum L1-L7 or "Unclassified", default "Unclassified") to the finding intermediate representation.

### Component 3: Orchestrator Phase 1 Extension
**File**: `.claude/agents/tachi/orchestrator.md`
**Type**: Modification
**Purpose**: Add MAESTRO layer keyword classification after DFD classification in Phase 1. Add MAESTRO Layer column to Component Inventory and Dispatch Table. Add MAESTRO Layer column to STRIDE and AI output tables. Add "Risk by MAESTRO Layer" subsection in Section 6 (Risk Summary).

### Component 4-7: Pipeline Reference Updates
**Files**: `dispatch-rules.md`, `output-schemas.md`, `finding-format-shared.md`, `sarif-specification.md`
**Type**: Modifications
**Purpose**: Update dispatch table format, output table formats, finding IR documentation, and SARIF specification to include MAESTRO layer fields.

### Component 8: Downstream Agent Propagation
**Files**: `risk-scorer.md`, `control-analyzer.md`
**Type**: Modifications
**Purpose**: Add passive `maestro_layer` field propagation (read if present, include in output, default to "Unclassified" if absent).

## Data Flow

```
Architecture Input
       │
       ▼
  Phase 1: Scope
  ├─ Extract components
  ├─ Classify DFD types
  ├─ Classify MAESTRO layers (NEW — keyword matching from shared reference)
  ├─ Produce Component Inventory with MAESTRO Layer column (NEW)
  └─ Produce Dispatch Table with MAESTRO Layer column (NEW)
       │
       ▼
  Phase 2: Determine Threats (UNCHANGED)
       │
       ▼
  Phase 3: Determine Countermeasures
  ├─ Each finding inherits maestro_layer from its target component (NEW)
  └─ Assemble tables with MAESTRO Layer column (NEW)
       │
       ▼
  Phase 4: Assess & Output
  ├─ Risk summary with "Risk by MAESTRO Layer" subsection (NEW)
  └─ SARIF output with maestro-layer tags and properties (NEW)
       │
       ▼
  Downstream: risk-scores.md, compensating-controls.md (passive propagation)
```

## Tech Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Content format | Markdown | Consistent with all existing agent definitions and references |
| Schema format | YAML | Consistent with existing finding.yaml |
| Classification | Keyword matching | Reuses established AI dispatch pattern (case-insensitive substring) |
| Reference framework | CSA MAESTRO | Industry-standard seven-layer taxonomy for agentic AI |

---

### Feature 104: Downstream Baseline Propagation

**Status**: Delivered (2026-04-08) | PR #107 | 18/18 tasks complete

## Components

### Component 1: Shared Parser Extensions

**File modified**: `scripts/tachi_parsers.py`
**Type**: Extended existing module with 3 new/updated functions
**Purpose**: Provide shared baseline metadata and delta lifecycle extraction for all downstream consumers (report and infographic extraction scripts).

| Function | Purpose |
|----------|---------|
| `parse_baseline_frontmatter()` | Extract baseline metadata (source, date, finding_count, run_id) from nested YAML frontmatter block in threats.md. Handles both standard and code-fenced frontmatter delimiters. Returns None values when no baseline is present. |
| `parse_resolved_findings()` | Parse Section 4b Resolved Findings table. Returns list of resolved finding dicts with `delta_status: "RESOLVED"` injected. Returns empty list when Section 4b is absent (first run, no baseline). |
| `parse_threats_findings()` (updated) | Extended to extract optional `delta_status` field from Status column in Section 7 Recommended Actions table. Backward compatible -- omits field when Status column is absent. |

### Component 2: Output Schema Updates

**Files modified**: `templates/tachi/output-schemas/threats.md`, `templates/tachi/output-schemas/threat-report.md`
**Type**: Extended existing output schemas
**Purpose**: Surface baseline lifecycle data in standardized output formats for downstream consumption.

| Template | Changes |
|----------|---------|
| `threats.md` | Section 7 Recommended Actions gains Status column carrying `delta_status` (NEW/UNCHANGED/UPDATED); new Section 8 Delta Summary with finding lifecycle counts, remediation proof, and baseline reference table |
| `threat-report.md` | Schema version bumped 1.0 to 1.1; frontmatter gains `baseline_source`, `baseline_date`, `delta_counts` (new/unchanged/updated/resolved) fields; new Section 8 Delta Summary |

### Component 3: Threat Report Agent Enhancement

**File modified**: `agents/threat-report.md`
**Type**: Extended existing agent with delta-aware narrative generation
**Purpose**: Adapt executive summary, threat analysis, and remediation roadmap narratives to highlight changes since baseline.

Delta-aware narrative rules:
- Executive summary includes baseline comparison paragraph when baseline data is present
- Threat analysis sections annotate individual findings with lifecycle status
- New Section 8 Delta Summary generated with lifecycle breakdown and baseline reference
- Attack tree generation scoped to NEW and UPDATED Critical/High findings (UNCHANGED findings carried from baseline)
- Frontmatter populated with baseline metadata and delta counts from source threats.md

### Component 4: Extraction Script Updates

**Files modified**: `scripts/extract-report-data.py`, `scripts/extract-infographic-data.py`
**Type**: Extended existing extraction scripts with baseline data support
**Purpose**: Propagate baseline metadata and delta lifecycle counts to Typst and JSON data formats for report and infographic rendering.

| Script | Changes |
|--------|---------|
| `extract-report-data.py` | Emits baseline metadata Typst variables (source, date, finding count, run ID), delta lifecycle count variables, and `has-baseline-data` boolean flag for conditional report section inclusion |
| `extract-infographic-data.py` | Emits baseline metadata and delta lifecycle fields in JSON output when baseline data is present in source artifacts |

### Component 5: Command Updates

**Files modified**: `.claude/commands/tachi.infographic.md`, `.claude/commands/tachi.security-report.md`
**Type**: Extended existing commands with baseline data display
**Purpose**: Surface baseline comparison data in infographic specifications and PDF security reports.

| Command | Changes |
|---------|---------|
| `/tachi.infographic` | Baseline metadata passed to infographic templates for delta annotation display |
| `/tachi.security-report` | Baseline data variables available for conditional page inclusion in Typst report |

### Component 6: Report Assembler Agent Enhancement

**File modified**: `.claude/agents/tachi/report-assembler.md`
**Type**: Extended existing agent with baseline data assembly
**Purpose**: Include baseline metadata and delta lifecycle data in PDF security report assembly.

### Component 7: Example Output Regeneration

**Files modified**: All 6 example `threats.md` files, 2 example `threat-report.md` files
**Type**: Regenerated with baseline columns
**Purpose**: Reference implementations updated to demonstrate Section 7 Status column and Section 8 Delta Summary format.

## Data Flow

```
threats.md (with baseline data from Feature 074)
       │
       ├── Section 7: Status column (delta_status per finding)
       ├── Section 8: Delta Summary (lifecycle counts + baseline reference)
       └── Frontmatter: baseline metadata block
       │
       ▼
  ┌────────────────────────────────────────────────────────┐
  │                    tachi_parsers.py                     │
  │  parse_baseline_frontmatter() → baseline metadata      │
  │  parse_resolved_findings()    → resolved finding list   │
  │  parse_threats_findings()     → findings + delta_status │
  └────────────────────────────────────────────────────────┘
       │                                    │
       ▼                                    ▼
  extract-report-data.py            extract-infographic-data.py
  (Typst variables)                 (JSON fields)
       │                                    │
       ▼                                    ▼
  /tachi.security-report                  /tachi.infographic
  (PDF with baseline data)          (spec with delta annotations)
       │
       ▼
  threat-report.md (schema 1.1)
  ├── Frontmatter: baseline_source, baseline_date, delta_counts
  ├── Executive summary: baseline comparison paragraph
  ├── Threat analysis: per-finding lifecycle annotations
  └── Section 8: Delta Summary with lifecycle table
```

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| Python 3.9+ (stdlib only) | Shared parser module and extraction scripts -- no external dependencies |
| Markdown tables | Status column and Delta Summary section as structured data carriers |
| YAML frontmatter | Baseline metadata block in threats.md and threat-report.md |
| Typst data variables | Conditional baseline section inclusion in PDF security reports |
| JSON | Baseline fields in infographic extraction output |

---

### Feature 112: Attack Path Pages in Security Report PDF

**Status**: Delivered (2026-04-09) | PR #115 | 18/18 tasks complete

## Components

### Component 1: Attack Tree Data Extraction

**File modified**: `scripts/extract-report-data.py`
**Type**: Extended existing script with 2 new functions
**Purpose**: Parse attack tree Mermaid files, render to PNG via `mmdc` subprocess, and emit structured data for Typst page rendering.

| Function | Purpose |
|----------|---------|
| `parse_attack_trees()` | Scans `attack-trees/` directory for `*-attack-tree.md` files, extracts finding ID, component, severity from metadata table, extracts Mermaid code block, cross-references finding ID with parsed findings data for authoritative severity and mitigation text, filters to Critical and High findings, orders by severity then finding ID. Constructs narrative from attack tree metadata and node labels, sources remediation from finding mitigation field. |
| `render_mermaid_to_png()` | Checks `mmdc` availability via `shutil.which()`, creates `tempfile.TemporaryDirectory()` for intermediate files, invokes `mmdc -i {id}.mmd -o {id}.png -s 2 -b transparent` per entry, copies PNGs to `attack-trees/` directory for Typst consumption. Graceful fallback: sets `has_image = false` per entry when `mmdc` unavailable or rendering fails; raw Mermaid text displayed instead. |

**Output to `report-data.typ`**: `has-attack-trees` (boolean), `attack-trees` (array of dicts with: id, component, severity, title, image-path, has-image, mermaid-text, narrative, remediation).

### Component 2: Artifact Detection Extension

**File modified**: `scripts/tachi_parsers.py`
**Type**: Extended existing function
**Purpose**: Add `attack-trees/` directory detection to the canonical `detect_artifacts()` entry point, returning `has_attack_trees` boolean and directory path.

### Component 3: Attack Path Typst Page Template

**New file**: `templates/tachi/security-report/attack-path.typ`
**Type**: New file
**Purpose**: Renders one portrait page per attack path entry with severity badge, rendered diagram (or raw Mermaid fallback), narrative explanation, and remediation steps.

Exports `attack-path-page(entry, classification)` function rendering:
- Header with classification bar via `report-header()`
- Severity-colored finding badge (using `severity-color()`) with finding ID and title
- Diagram section (~60% page height): `#image()` if `has-image` is true, `#raw()` monospace block otherwise
- Narrative section: 2-4 sentence attack chain explanation
- Remediation section: Bulleted list of remediation steps
- Standard footer via `report-footer()`

Follows patterns from `maestro-findings.typ`: imports `shared.typ`, exports single function, severity badge helper.

### Component 4: Main Orchestrator Update

**File modified**: `templates/tachi/security-report/main.typ`
**Type**: Modified
**Purpose**: Import `attack-path.typ`, add backward-compatible defaults for `has-attack-trees` and `attack-trees` variables, insert conditional attack path page section after Executive Summary (before infographic pages).

Conditional inclusion:
```typst
#if has-attack-trees and attack-trees.len() > 0 {
  section-divider("Attack Path Analysis", classification: classification)
  for entry in attack-trees {
    page(...)[#attack-path-page(entry: entry, classification: classification)]
  }
}
```

### Component 5: Command and Agent Updates

**Files modified**: `.claude/commands/tachi.security-report.md`, `.claude/agents/tachi/report-assembler.md`
**Type**: Extended existing files
**Purpose**: Add `attack-trees/` directory to artifact detection tables and attack path pages to page listing display.

### Component 6: Example Output Validation

**Files validated**: All 6 example `sample-report/` directories
**Type**: End-to-end pipeline validation
**Purpose**: 2 examples with attack trees (attack path pages rendered), 4 examples without (backward compatible, no attack path pages).

## Data Flow

```
attack-trees/*.md ──┐
                     ├──> extract-report-data.py ──> mmdc (PNG) ──> report-data.typ ──> main.typ ──> PDF
threat-report.md ───┘                                                                    |
                                                                              attack-path.typ
```

1. **Input**: `attack-trees/{id}-attack-tree.md` files (primary) or `threat-report.md` Section 5 (fallback)
2. **Extraction**: `parse_attack_trees()` reads metadata tables + Mermaid code blocks
3. **Rendering**: `render_mermaid_to_png()` converts Mermaid to PNG via `mmdc` subprocess (optional, graceful fallback)
4. **Data binding**: Attack tree entries written to `report-data.typ` as Typst array with `has-attack-trees` boolean gate
5. **Template**: `attack-path.typ` renders each entry as a portrait page with severity badge, diagram, narrative, remediation
6. **Orchestration**: `main.typ` conditionally includes section divider + pages after Executive Summary

## Tech Stack

| Technology | Purpose | Justification |
|-----------|---------|---------------|
| Python 3.9+ (stdlib only) | Attack tree parsing and data extraction | Extends existing `extract-report-data.py` pattern; `shutil.which()` and `subprocess` for mmdc invocation |
| `mmdc` (Mermaid CLI, optional) | Mermaid-to-PNG rendering for diagram embedding | Standard tool for Mermaid rendering; graceful fallback to raw text when unavailable |
| Typst | Attack path page template | Extends existing PDF report template system via hub-first architecture |
| PNG @ 2x scale | Rendered diagram images | Consistent with existing infographic image handling in Typst report |

---

### Feature 121: Rename Tachi Commands to tachi.* Namespace

## Components

### Component 1: Command File Renames

**Purpose**: Rename the 5 primary command files and create 1 new command
**Files**: `.claude/commands/`

| Current File | New File | Action |
|-------------|----------|--------|
| `threat-model.md` | `tachi.threat-model.md` | Rename (git mv) |
| `risk-score.md` | `tachi.risk-score.md` | Rename (git mv) |
| `compensating-controls.md` | `tachi.compensating-controls.md` | Rename (git mv) |
| `infographic.md` | `tachi.infographic.md` | Rename (git mv) |
| `security-report.md` | `tachi.security-report.md` | Rename (git mv) |
| *(new)* | `tachi.architecture.md` | Create (Issue #120) |

### Component 2: Adapter Renames

| Directory | Current File | New File |
|-----------|-------------|----------|
| `adapters/claude-code/commands/` | `threat-model.md` | `tachi.threat-model.md` |
| `adapters/claude-code/commands/` | `infographic.md` | `tachi.infographic.md` |
| `adapters/claude-code/commands/` | `risk-score.md` | `tachi.risk-score.md` |
| `adapters/github-actions/` | `tachi-threat-model.yml` | `tachi.threat-model.yml` |

### Component 3: Cross-Reference Updates

~344 files, ~2,207 references. Three-tier pattern strategy: Tier 1 (slash invocations), Tier 2 (path-qualified file refs), Tier 3 (manual review for bare filenames).

### Component 4: Install Script Cleanup

Deprecated-file removal in `scripts/install.sh` before manifest copy loop. Removes 5 old unprefixed command files from consumer projects on upgrade.

### Component 5: Manifest Update

`INSTALL_MANIFEST.md` updated with 6 `tachi.*` command filenames in both human-readable and machine-parseable sections.

## Data Flow

```
User invokes /tachi.threat-model → threats.md
User invokes /tachi.risk-score → risk-scores.md
User invokes /tachi.compensating-controls → compensating-controls.md
User invokes /tachi.infographic → infographic images
User invokes /tachi.security-report → PDF security report
User invokes /tachi.architecture → architecture.md (pipeline input)
```

Data flow unchanged — only command invocation names change from unprefixed to `tachi.*` prefixed.

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Command definitions | Markdown (`.md`) | Slash command behavior |
| Agent definitions | Markdown (`.md`) | AI agent instructions |
| Schemas | YAML (`.yaml`) | Input/output contracts |
| Templates | Typst (`.typ`) + Markdown | PDF report + output format |
| Install script | Bash | File distribution to consumer projects |
| Manifest | Markdown with HTML comments | Machine-parseable file list |

---

### Feature 120: Architecture Lifecycle Command

**Status**: Delivered (2026-04-09) | PR #124 | 23/23 tasks complete

## Components

| Component | Type | Description |
|-----------|------|-------------|
| `/tachi.architecture` command | Markdown command file | Enhanced with lifecycle management: frontmatter generation, version archive, guided update mode |
| `/tachi.threat-model` command | Markdown command file | Extended with architecture snapshot step (Step 1.4) |
| Architecture File | Markdown + YAML frontmatter | Version-tracked architecture description with integrity checksum |
| Archive Directory | Local filesystem | `.archive/vN/` structure preserving previous architecture versions |
| Architecture Snapshot | File copy | Verbatim copy in threat model output folders for traceability |

## Data Flow

```mermaid
flowchart TD
    A[User runs /tachi.architecture] --> B{Existing file?}
    B -->|No| C[Generate architecture v1]
    B -->|Yes| D{Has frontmatter?}
    D -->|No| E[Archive as v0]
    D -->|Yes| F[Archive as vN]
    E --> G[Guided update P1]
    F --> G
    G -->|Changes| H[Generate updated architecture]
    G -->|No changes| Z[Abort — file untouched]
    C --> I[Write body to file]
    H --> I
    I --> J[Compute SHA-256 checksum on file]
    J --> K[Prepend frontmatter with checksum]
    K --> L[Report]

    M[User runs /tachi.threat-model] --> N[Create timestamped output dir]
    N --> O[Step 1.4 NEW: Snapshot architecture]
    O --> P[Step 2: Invoke orchestrator]
    P --> Q[Output: threats.md + architecture.md snapshot]
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Command files | Markdown (Claude Code) | Agent instruction format |
| Archive copy | Bash `cp` via tool | File preservation |
| Directory creation | Bash `mkdir -p` via tool | Archive/output folder setup |
| Checksum | Bash `shasum -a 256` via tool | Content integrity hash |
| Frontmatter | YAML | Version metadata format |

---

### Feature 128: Executive Threat Architecture Infographic

## Components

The feature touches the following logical components of the tachi pipeline:

### Extraction Layer
- **`extract-infographic-data.py`**: Receives `--template executive-architecture`; reads threats.md (with optional risk-scores or compensating-controls for tier upgrade); parses scope data via shared `tachi_parsers.parse_scope_data()`; groups components into architectural layers via existing `_compute_trust_zones()`; filters findings to Critical/High; selects one callout per layer (severity desc → composite score desc → finding ID asc); outputs JSON payload to stdout.
- **`extract-report-data.py`**: Adds new entry in `detect_images()` for `threat-executive-architecture.jpg`; writes `has-executive-architecture` boolean and `executive-architecture-image-path` string into the generated `report-data.typ` file.

### Spec Generation Layer
- **`tachi-threat-infographic` agent (`.claude/agents/tachi/threat-infographic.md`)**: Receives the JSON payload from extraction; renders the six-section markdown spec; constructs the Gemini prompt with portrait orientation, layer ordering, pastel fills, red dashed-border callouts, warning icons, and ≤25-word plain-English narrative instructions.

### Image Generation Layer
- **Existing Gemini integration**: Reused as-is. The agent invokes Gemini with the constructed prompt; on success writes `threat-executive-architecture.jpg` to the output folder; on failure leaves the spec file in place (spec-first per ADR-014).

### PDF Assembly Layer
- **`main.typ`**: Imports `report-data.typ`; conditionally renders the executive architecture page using existing `infographic-page()` (already portrait), gated by `has-executive-architecture`, positioned immediately after Executive Summary and immediately before Attack Path Analysis.
- **`report-assembler` agent**: Documentation update only — adds the new artifact to its detection table.

### Schema and Command Layer
- **`schemas/infographic.yaml`**: Adds `executive-architecture` to the template enumeration with section structure and visual directive constants.
- **`.claude/commands/tachi.infographic.md`**: Adds new template to argparse choices, adds `exec` alias, includes in `all` expansion before MAESTRO additions.
- **`.claude/skills/tachi-infographics/references/`**: New reference doc describing the template, its outputs, and expected behavior.

## Data Flow

```
threats.md (+ optional risk-scores.md / compensating-controls.md)
        │
        ▼
scripts/tachi_parsers.py
   - parse_scope_data() → components, trust_boundaries, data_flows
   - parse_threats_findings() → Critical/High findings with metadata
        │
        ▼
scripts/extract-infographic-data.py (--template executive-architecture)
   1. Detect tier (compensating > risk-scores > threats)
   2. Group components into ArchitecturalLayers via _compute_trust_zones
      OR fall back to DFD type grouping if no zones
   3. Filter findings to Critical/High
   4. Select one callout per layer (severity → score → ID)
   5. Build ExecutiveArchitecturePayload JSON
   6. Emit JSON to stdout
        │
        ▼
.claude/agents/tachi/threat-infographic.md
   1. Read JSON payload
   2. Render threat-executive-architecture-spec.md (6 sections)
   3. Construct Gemini prompt (portrait, layers, callouts, ≤25 words)
   4. Invoke Gemini API
   5. Write threat-executive-architecture.jpg (best-effort)
        │
        ▼
Output folder contents:
   - threat-executive-architecture-spec.md  (always)
   - threat-executive-architecture.jpg      (if Gemini succeeds)
        │
        ▼
scripts/extract-report-data.py
   - detect_images() finds threat-executive-architecture.jpg
   - Writes has-executive-architecture: true and image path
     into report-data.typ
        │
        ▼
Typst compilation (templates/tachi/security-report/main.typ)
   - Imports report-data.typ
   - On encountering `if has-executive-architecture { ... }` after the
     Executive Summary block, calls infographic-page() (portrait)
   - Otherwise skips the page entirely (backward compatibility)
        │
        ▼
Final PDF: pages 1 (cover), 2 (TOC), 3 (Methodology),
4 (Scope), 5 (Executive Summary),
→ 6 (NEW: Executive Threat Architecture)
→ 7+ (Attack Path Analysis, existing infographics, findings, etc.)
```

## Tech Stack

| Layer | Technology | Version | Role in F-128 |
|-------|------------|---------|---------------|
| Extraction | Python | 3.11 | Modify `extract-infographic-data.py` and `extract-report-data.py` |
| Parsing | `tachi_parsers.py` | existing | Reuse for scope data and finding parsing — NO modifications |
| Schema | YAML | 1.2 | Modify `schemas/infographic.yaml` |
| Agent | Markdown | n/a | Modify `.claude/agents/tachi/threat-infographic.md` and `report-assembler.md` |
| Command | Markdown | n/a | Modify `.claude/commands/tachi.infographic.md` |
| Image generation | Gemini API | existing integration | Reuse via agent — NO new API calls or dependencies |
| PDF compilation | Typst | 0.11+ | Modify `main.typ`; reuse `infographic-page()` (no new template function) |
| Testing | pytest | existing | Add unit tests in `tests/scripts/` |

**No new dependencies introduced.**

---

### Feature 136: MAESTRO Canonical Layer Correctness Fix

**Status**: Delivered (2026-04-10) | PR #146 (squash commit 31356fb) | Release v4.10.0

## Components

No new components. This is a data/template refresh feature operating on existing MAESTRO taxonomy infrastructure introduced in Feature 084 and Feature 091. The pipeline is fully data-driven — scripts/extract-*.py have no hardcoded layer name matching, so the fix is pure content replacement across foundation files, templates, and example outputs.

### Component 1: MAESTRO Shared Reference File — Canonical Rename
**File**: `.claude/skills/tachi-shared/references/maestro-layers-shared.md`
**Type**: Modification
**Purpose**: Rename L5/L6/L7 to canonical CSA MAESTRO layer names per the Ken Huang authoritative definition — L5 "Security" → "Evaluation and Observability", L6 "Agent Ecosystem" → "Security and Compliance", L7 "User Interface" → "Agent Ecosystem". Correct the MAESTRO acronym expansion to "Multi-Agent Environment, Security, Threat, Risk, and Outcome". Reassign keyword tables accordingly (add new L5 observability keywords, move legacy L5 security keywords to L6, merge legacy L6/L7 into new L7). Add verbatim Ordering Rationale section explaining L5-before-L6 specificity gradient (load-bearing for detective-vs-preventive control classification).

### Component 2: Finding IR Schema Enum Update
**File**: `schemas/finding.yaml`
**Type**: Modification
**Purpose**: Update `maestro_layer` enum to canonical L5/L6/L7 names. Bump `schema_version` from "1.2" to "1.3" to signal the breaking enum-value change. Establishes the **enum-value-only minor-bump rule**: enum-value-only breaking changes to `schemas/finding.yaml` warrant a minor schema bump (x.y+1), not a major bump, provided the schema shape and required fields are unchanged. Rule documented in ADR-020 Revision History.

### Component 3: Typst Security Report Template — Layer Prose and Fallback Dictionary
**File**: `templates/tachi/security-report/maestro-findings.typ`
**Type**: Modification
**Purpose**: Update MAESTRO Findings page layer prose (line 121 "User Interface (L7)" → "Agent Ecosystem (L7)") and fix pre-existing third-way divergence bug in the fallback dictionary (lines 132-134) where "Integration Services" had crept in as neither the old Feature 084 name nor the canonical CSA name. Fallback dict now matches canonical CSA names exactly.

### Component 4: Typst Full-Bleed Infographic Layout Fix
**File**: `templates/tachi/security-report/full-bleed.typ`
**Type**: Modification
**Purpose**: Constrain image height in `infographic-page()` function to 7.5in with `fit: "contain"` to handle portrait-aspect infographics that would otherwise overflow the page. Fixes a **latent Feature 128 bug** that surfaced when the executive-architecture portrait JPEG was added without height constraint. Scope expansion inside the Feature 136 PR; not a planned deliverable.

### Component 5: ADR-020 Revision History
**File**: `docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md`
**Type**: Modification
**Purpose**: Add Revision History section documenting the Feature 136 canonical rename and establishing the enum-value-only minor-bump schema versioning rule as an enduring precedent for future enum corrections. References `schemas/finding.yaml` v1.3.

### Component 6: Additional Foundation Files
**Files**: `.claude/skills/tachi-shared/references/finding-format-shared.md`, `.claude/skills/tachi-orchestration/references/dispatch-rules.md`, `.claude/skills/tachi-orchestration/references/output-schemas.md`, `docs/architecture/00_Tech_Stack/README.md`, `templates/tachi/output-schemas/threats.md`, `templates/tachi/infographics/infographic-maestro-stack.md`, `templates/tachi/infographics/infographic-maestro-heatmap.md`, `templates/tachi/security-report/main.typ`, `README.md`, `docs/product/02_PRD/INDEX.md`, `docs/product/_backlog/BACKLOG.md`, `schemas/finding.yaml` — 14 foundation files updated total
**Type**: Modifications
**Purpose**: Propagate canonical layer names across all pipeline documentation, output schemas, infographic templates, and product-facing indices. No runtime pipeline changes required — all updates are content replacement in docs, templates, and references.

### Component 7: Example Output Regeneration
**Files**: `examples/{web-app,microservices,agentic-app,ascii-web-api,mermaid-agentic-app,free-text-microservice}/**` — 6 example architectures regenerated
**Type**: Regeneration
**Purpose**: Regenerate all 6 example threat models and downstream outputs with canonical layer names. 5 example PDFs regenerated byte-deterministically via `SOURCE_DATE_EPOCH=1700000000` (per ADR-021) for backward-compatibility baseline validation. 1 example (agentic-app) intentionally excluded from byte-determinism test per Feature 128 convention.

### Component 8: Golden Test Fixtures
**Files**: `tests/scripts/fixtures/golden/maestro-heatmap.json`, `tests/scripts/fixtures/golden/maestro-stack.json`
**Type**: Frozen (no regeneration required)
**Purpose**: Confirmed that both MAESTRO golden fixtures are frozen pre-MAESTRO schema — they do NOT contain layer name references. No regeneration needed; existing fixtures remain valid.

## Data Flow

```
Canonical CSA MAESTRO (Ken Huang authoritative definition)
       │
       ▼
maestro-layers-shared.md (Tachi Taxonomy Layer — single source of truth)
       │ (defines keywords + layer names)
       ▼
schemas/finding.yaml (Schema Layer — v1.3 enum)
       │ (validates threats.md findings)
       ▼
Phase 1 classifier (runtime, reads shared reference via Read tool)
       │ (keyword-match → maestro_layer assignment)
       ▼
Pipeline Documentation Layer (reference docs show canonical names)
  ├─ dispatch-rules.md (orchestrator dispatch example row)
  ├─ output-schemas.md (output format specs)
  └─ finding-format-shared.md (finding IR documentation)
       │
       ▼
Output Schema Layer (templates reference canonical names)
  ├─ threats.md template
  └─ infographic templates (maestro-stack, maestro-heatmap)
       │
       ▼
PDF Rendering Layer
  ├─ maestro-findings.typ (prose + fallback dictionary — canonical names)
  ├─ main.typ (executive summary prose — canonical names)
  └─ full-bleed.typ (infographic-page function — portrait height fix)
       │
       ▼
Example Outputs (6 architectures regenerated)
  ├─ threats.md / risk-scores.md / compensating-controls.md
  ├─ threat-report.md / threat-infographic-spec.md
  └─ security-report.pdf (5 byte-deterministic baselines)
```

**Data flow change**: None structurally. The same pipeline carries new canonical layer name strings from the shared reference through to the PDF output. The only runtime-active change is the `maestro-findings.typ` fallback dictionary — a safety net for when `layer-name` data is missing in `report-data.typ` (should never happen in the normal flow but now matches canonical names if invoked).

## Tech Stack

No stack changes. Reuses existing infrastructure:

| Layer | Technology | Version | Role in F-136 |
|-------|------------|---------|---------------|
| Taxonomy reference | Markdown | n/a | Content update in `.claude/skills/tachi-shared/references/maestro-layers-shared.md` |
| Schema | YAML | 1.3 | Enum value rename + schema_version bump in `schemas/finding.yaml` |
| PDF templates | Typst | 0.11+ | Content update in `maestro-findings.typ`, `main.typ`; layout fix in `full-bleed.typ` |
| Infographic templates | Markdown | n/a | Content update in `infographic-maestro-stack.md`, `infographic-maestro-heatmap.md` |
| Byte-determinism | `SOURCE_DATE_EPOCH=1700000000` | Feature 128 convention | Baseline PDF regeneration (per ADR-021) |
| Testing | pytest + test_backward_compatibility.py | existing | 150+ tests pass post-regeneration; golden fixtures frozen |
| Release | release-please | v4.10.0 | Minor bump auto-cut by release-please workflow on merge to main |

**No new dependencies introduced.**

## Architecture Decisions

1. **Enum-value-only minor-bump rule** (new, established for this feature): Enum-value-only breaking changes to `schemas/finding.yaml` warrant a minor schema bump (x.y+1), not a major bump, provided the schema shape and required fields are unchanged. The CHANGELOG migration note is the accountability mechanism for downstream consumers. This rule is documented in ADR-020 Revision History and applies to future enum-value corrections.

2. **Canonical CSA MAESTRO authoritative source**: Ken Huang's published CSA definition is the single source of truth for MAESTRO layer names, keywords, and taxonomy ordering. Any future divergence must be explicitly justified in ADR-020 with linked source references.

3. **Pipeline is data-driven** (pre-existing, validated): The fix required zero Python script changes. `scripts/extract-*.py` have no hardcoded layer name matching — they read layer values from source artifact frontmatter/tables. This confirmed ADR-017's determinism claim and the Feature 084 "passive propagation" design.

## Known Deferred Items

Follow-up issues recommended (not blocking Feature 136 closure):

1. **Agentic-app sample-report JPEG regeneration**: Three infographic JPEGs in `examples/agentic-app/sample-report/` need re-rendering via Gemini API. Deferred because Gemini API calls are non-deterministic and cannot be gated by `SOURCE_DATE_EPOCH`. Manual regeneration planned in a follow-up housekeeping PR.

2. **Infographic extract tier-selection bug**: When source is `compensating-controls.md`, the extraction script's tier-detection logic has a subtle misclassification bug (observed during Feature 136 validation, not in scope for correctness fix). Planned as a follow-up bug fix issue.

---

### Feature 130: Fix Attack Path Mermaid Rendering When mmdc Is Not Installed

## Components

### Preflight Gate (shell-level)
- **Location**: `.claude/commands/tachi.security-report.md` Step 1
- **Role**: First-line enforcement of mmdc availability at command entry, gated on attack-tree detection
- **Pattern**: mirrors the existing Typst `which typst` check in the same file
- **Failure mode**: non-zero exit with canonical error message

### Preflight Gate (Python-level)
- **Location**: `scripts/extract-report-data.py::render_mermaid_to_png()` line 725
- **Role**: Defense-in-depth for direct Python invocations (tests, tooling)
- **Pattern**: existing `shutil.which("mmdc")` check, converted from silent `return` to `raise RuntimeError(...)`
- **Failure mode**: exception propagates up and exits the pipeline non-zero

### Mid-Render Failure Aggregator (new behavior)
- **Location**: `scripts/extract-report-data.py::render_mermaid_to_png()` after the `as_completed` loop
- **Role**: Collects per-finding rendering failures into a list, then raises `RuntimeError("Attack path rendering failed for N findings: [...]")` if the list is non-empty
- **Failure mode**: exception propagates, pipeline exits non-zero, stderr shows per-finding detail

### CI Workflow
- **Location**: `.github/workflows/tachi-mmdc-preflight.yml` (new file)
- **Trigger**: `pull_request` on 5 file paths listed in FR-130.7
- **Role**: CI-level enforcement that the loud-failure path works on a machine without mmdc
- **Platform**: `ubuntu-latest` (no custom Docker image)

### Docs Sync Cluster
- `README.md` Prerequisites section (new)
- `scripts/install.sh` mmdc check (new code block)
- `docs/architecture/00_Tech_Stack/README.md` line 279 (update mmdc from optional to hard prereq)
- `specs/112-attack-path-pages/spec.md` SC-004 inversion, line 135 deletion
- `specs/112-attack-path-pages/research.md` line 80 correction, lines 91-93 rationale block
- `docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md` (new — first ADR governing CLI prerequisite transitions)

## Data Flow

```
user runs /tachi.security-report on project with attack-trees/
            │
            ▼
.claude/commands/tachi.security-report.md Step 1
            │
            ├── which typst? ──No──> abort with Typst install guidance (existing behavior)
            │
            Yes
            │
            ├── attack-trees/*.md present? ──No──> skip mmdc check, proceed
            │
            Yes
            │
            ├── which mmdc? ──No──> abort with canonical error message (NEW, FR-130.1)
            │
            Yes
            │
            ▼
report-assembler agent invokes scripts/extract-report-data.py
            │
            ▼
render_mermaid_to_png(attack_trees, target_dir, template_dir)
            │
            ├── attack_trees empty? ──Yes──> return (existing behavior)
            │
            No
            │
            ├── shutil.which("mmdc")? ──No──> raise RuntimeError with canonical message (NEW, FR-130.2)
            │
            Yes
            │
            ▼
        ThreadPoolExecutor(max_workers=4) rendering loop
            │
            ▼
        Collect per-finding success/failure results
            │
            ├── any failures? ──Yes──> raise RuntimeError(per-finding list) (NEW, FR-130.4; aborts pipeline)
            │
            No
            │
            ▼
        All entries have has_image=True, image_path=<path>
            │
            ▼
        Typst template renders with has_img branch only (else-if branch deleted, FR-130.3)
            │
            ▼
        PDF ships with 100% rendered diagrams
```

## Tech Stack

| Layer | Choice | Rationale | New in this feature? |
|---|---|---|---|
| Runtime language | Python 3.11+ | Matches existing `scripts/*.py` constraint | No |
| Runtime Python deps | stdlib only (`shutil`, `subprocess`, `concurrent.futures`, `tempfile`, `pathlib`) | Tech Stack doc hard rule | No |
| External CLI (hard prereq, always) | Typst 0.12+ | PDF compilation | No |
| External CLI (hard prereq, gated) | `@mermaid-js/mermaid-cli` v11+ (npm install) | Attack path rendering | **Yes** (was optional, now hard) |
| Dev-time test framework | pytest 8.0+ | Feature 128 precedent | No |
| CI runner | GitHub Actions `ubuntu-latest` | Standard, no mmdc preinstalled | No (workflow file is new) |
| PDF template engine | Typst with `attack-path.typ` component | Existing Feature 112 pipeline | No |
| Determinism harness | `SOURCE_DATE_EPOCH=1700000000` + `tests/scripts/test_backward_compatibility.py` | ADR-021 | No (reused) |
| Architecture Decision Records | `docs/architecture/02_ADRs/` | Existing pattern | **Yes** (ADR-022 is new) |

**No new technology introduced.**

---

### Feature 082: threat-agent-skill

## Components

### C1: Threat Agent File (11 instances)

- **Responsibility**: Orchestration-only markdown file invoked by orchestrator dispatch. Loads domain knowledge on-demand from companion skill directory; constructs findings in the shared format; emits findings to orchestrator.
- **Interface**: Input — component name + DFD element type from orchestrator. Output — finding list in `schemas/finding.yaml` v1.3 format.
- **Dependencies**: (a) Companion skill directory `tachi-<agent-name>/references/`; (b) shared skill directory `tachi-shared/references/` for finding format and severity bands; (c) orchestrator for invocation and finding aggregation.
- **Line target**: STRIDE ≤120, AI ≤150, hard ceiling 180.
- **Location**: `.claude/agents/tachi/<agent-name>.md`

### C2: Companion Skill Directory (11 instances)

- **Responsibility**: Per-agent domain knowledge store. Holds detection patterns, optional example findings, optional finding field guidance. Loaded on-demand by the parent agent file via `**MANDATORY**: Read` directive.
- **Interface**: File-system directory readable by the Claude Code `Read` tool. Reference files are markdown.
- **Dependencies**: Parent threat agent file reads from this directory; no other agent reads from it.
- **Line target**: 60-300 lines per reference file, typically 100-200. Total per directory: 150-500 lines.
- **Location**: `.claude/skills/tachi-<agent-name>/references/`

### C3: Shared Skill Directory (1 instance, already exists)

- **Responsibility**: Cross-agent shared content. Severity bands, finding format, STRIDE category definitions, MAESTRO layer taxonomy. Consumed by multiple agents — infrastructure tier (6 agents) already consumes it; threat tier (11 agents) starts consuming it in Phase 2c.
- **Interface**: File-system directory, markdown reference files. Consumed via `**MANDATORY**: Read` directives across the agent fleet.
- **Dependencies**: Read-only from any individual agent's perspective. Edits go through Phase 2c single-writer wave and are additive-only.
- **Blast radius**: Any edit to a shared reference file can affect all 17 agents (threat + infra). Re-baseline of 5 byte-deterministic PDFs is the expected outcome of any edit (FR-17 / R6).
- **Location**: `.claude/skills/tachi-shared/references/` (existing: 4 files, 646 lines)

### C4: Orchestrator Dispatch (unchanged)

- **Responsibility**: Phase 1 component inventory; Phase 2 dispatch to threat agents; Phase 3 Table Assembly (including MAESTRO layer inheritance for each finding). Orchestrator is the only tachi agent that knows about MAESTRO; it remains so after this refactor (FR-9).
- **Interface**: Calls each threat agent with component + DFD element type; receives finding list; merges findings into master `threats.md`.
- **Dependencies**: Reads its own skill directory `tachi-orchestration/references/` (dispatch rules, classification rules, MAESTRO-layers-shared).
- **Impact of Feature 082**: Zero. Orchestrator dispatch logic and interface are unchanged (C2). The refactor is transparent to orchestrator.
- **Location**: `.claude/agents/tachi/orchestrator.md` (not touched by this feature)

### C5: ADR-023 (new architectural decision record)

- **Responsibility**: Document the detection sibling variant of the lean + skill references pattern. Record decisions on load-point semantics, MAESTRO boundary, additive-only shared-ref edits, and consumer/producer audience separation in shared files.
- **Interface**: Read by future contributors adding new threat detection patterns. Referenced from `docs/architecture/00_Tech_Stack/README.md` agent inventory section.
- **Location**: `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` (NEW, created in Phase 1)

## Data Flow

### Post-refactor data flow (Feature 082 target)

```
User
  │
  └──▶ /tachi.threat-model
        │
        └──▶ orchestrator.md  (UNCHANGED — same file, same logic)
              │
              ├──▶ Reads dispatch-rules.md, classification-rules.md (UNCHANGED)
              │
              ├──▶ Phase 1: Component inventory + MAESTRO classification (UNCHANGED)
              │
              ├──▶ Phase 2: Dispatch to 11 threat agents (UNCHANGED interface)
              │      │
              │      ├──▶ spoofing.md (≤120 lines, LEAN)
              │      │    └─▶ **MANDATORY**: Read tachi-spoofing/references/detection-patterns.md
              │      │    └─▶ **MANDATORY**: Read tachi-shared/references/finding-format-shared.md
              │      │    └─▶ Apply patterns to component
              │      │    └─▶ Construct findings using shared format producer section
              │      │    └─▶ Emit finding list
              │      │
              │      ├──▶ tampering.md (≤120 lines, LEAN) → same pattern → finding list
              │      ├──▶ ... (9 more threat agents, each lean)
              │      └──▶ agent-autonomy.md (≤150 lines, LEAN) → same pattern → finding list
              │
              └──▶ Phase 3: Table Assembly — merge findings, inherit MAESTRO layer per finding
                    │                                          (UNCHANGED — MAESTRO still orchestrator-owned)
                    └──▶ Write threats.md
```

**Key observation**: The input (user command) and output (`threats.md`) are content-equivalent pre/post. The only change is the internal shape of each threat agent — where its detection vocabulary lives. Content-level regression on 6 example architectures is sufficient to validate the refactor; the orchestrator doesn't need any changes.

### Shared reference consumption flow (Phase 2c edits propagate)

```
Phase 2c edit to finding-format-shared.md (APPEND "## For Threat Agents (Producers)" section)
                                              │
                ┌─────────────────────────────┴──────────────────────────────┐
                │                                                            │
                ▼                                                            ▼
     11 threat agents                                           6 infrastructure agents
     (NEW consumers, gain producer guidance)                    (EXISTING consumers, unchanged section)
                │                                                            │
                ▼                                                            ▼
     Same finding output shape                                     Same validation logic
     (schemas/finding.yaml v1.3)                                   (schemas/finding.yaml v1.3)
                │                                                            │
                └──────────────────┬─────────────────────────────────────────┘
                                   │
                                   ▼
                       threats.md content unchanged
                                   │
                                   ▼
                       BUT: PDFs diff at byte level (ADR-021 determinism)
                                   │
                                   ▼
                       Phase 3 re-baseline with SOURCE_DATE_EPOCH=1700000000
```

## Tech Stack

- **Agent runtime**: Claude Code (Anthropic) via the `.claude/agents/tachi/` markdown convention. No code, no framework, no language choice — agent files are configuration consumed by the Claude Code harness at invocation time.
- **Skill loading**: On-demand `Read` tool invocation from within agent files via `**MANDATORY**: Read <path>` directives. File-system reads only; no network, no daemon, no index.
- **Output format**: Finding list serialized to markdown (`threats.md`) and SARIF 2.1.0 (`threats.sarif`) by the orchestrator. Schema governed by `schemas/finding.yaml` v1.3 (unchanged by this feature).
- **Pipeline scripts**: `scripts/tachi_parsers.py`, `scripts/extract-*.py` — Python 3.11+ stdlib-only (PRD 128 convention). Unchanged by this feature.
- **PDF generation**: Typst + `@mermaid-js/mermaid-cli` (ADR-022 hard prerequisites). Unchanged by this feature, but 5 PDFs are re-baselined in Phase 3 (FR-17).
- **Byte-determinism**: `SOURCE_DATE_EPOCH=1700000000` environment variable per ADR-021. Applied to 5 non-agentic example PDF regenerations.
- **CI**: GitHub Actions workflow `.github/workflows/tachi.threat-model.yml` runs example regeneration smoke tests. Unchanged by this feature.
- **Release management**: release-please (Feature 086) auto-cuts a version tag on merge to main.
- **Primary source citations** (referenced only, never runtime-fetched): OWASP Top 10 (CC BY 3.0), OWASP LLM Top 10 v2025 (CC BY-SA 4.0), OWASP AI Exchange (CC0), MITRE ATT&CK v15+ (free w/ attribution), MITRE ATLAS v5.1+ (free w/ attribution), CWE Top 25 2024 (royalty-free), NIST AI 600-1 (US Federal public domain).

**No new technology introduced.** The refactor modifies markdown configuration and creates one new ADR. No new runtime dependencies, no new test frameworks, no schema changes.

---

### Feature 143: MAESTRO Phase 4 — OWASP AIVSS Evaluation ADR

## Components

This feature touches three surfaces; the canonical extraction for downstream system-design reference is listed below.

| Component | Type | File Path | Change Type | Rationale |
|-----------|------|-----------|-------------|-----------|
| ADR-024: OWASP AIVSS Evaluation and Tachi Composite Scoring Posture | New architecture decision record | `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md` | Create | PRD FR-5, Spec FR-005 — the primary deliverable |
| tachi-risk-scoring skill: AIVSS Relationship section | Update to existing skill file | `.claude/skills/tachi-risk-scoring/SKILL.md` | Add new section | PRD FR-6, Spec FR-006 — cross-reference to ADR-024 for skill consumers |
| Follow-on implementation Issue (conditional) | New GitHub Issue | `github.com/davidmatousek/tachi/issues` | Create (only if decision = Option A or B) | PRD FR-7, Spec FR-007 — deferred adoption work with option-specific effort estimate copied verbatim from ADR-024 |

**Architectural posture**: additive-only. No existing agent, schema, script, or example file is modified. ADR-024 becomes the canonical source of truth for tachi's AIVSS stance; SKILL.md becomes the runtime-adjacent pointer; the conditional Issue becomes the discovery anchor for any future implementation work.

## Data Flow

**No runtime data flow changes.** The feature is purely authoritative-document work.

### Author-time flow (implementer's workflow)

```
Wave 1 (Research):
  web-researcher → aivss.owasp.org (read v0.8 spec end-to-end, 2-hour timebox)
                → captures: version, URL, dimensions, formula, bands (if any)
                → produces: internal notes for Wave 2 consumption

Wave 2 (Authorship):
  architect → synthesizes Wave 1 notes with schemas/risk-scoring.yaml + severity-bands-shared.md
           → writes: ADR-024 (Context with 3 surfaces, Decision, Rationale, Alternatives, Consequences)
           → writes: SKILL.md AIVSS Relationship section (80-200 words, relative link to ADR-024)
  product-manager → IF decision is Option A or B:
                    uses .aod/scripts/bash/create-issue.sh
                    creates Issue with stage:discover label, option-specific effort verbatim
                  → ELSE (Option C):
                    no Issue filed (correct behavior per FR-007 conditionality)
```

### Read-time flow (stakeholder's workflow — post-merge)

```
CISO / compliance officer / future maintainer / security engineer
  → opens ADR-024 → reads Decision → follows cross-reference to SKILL.md (or vice versa)
  → sees consistent decision across both surfaces (FR-006 single-source-of-truth rule)
```

### Verification flow (gate at PR review)

```
PR review → SC-001 file exists → SC-002 Status: Accepted grep → SC-003 three surfaces present
         → SC-004 ≥3 options with effort estimate → SC-005 SKILL.md section present + word count
         → SC-006 git diff returns empty for schemas/scripts/agents/examples
         → SC-007 decision-noun consistency between ADR and SKILL.md
         → SC-008 conditional Issue filed (only if A or B) → SC-009 Related ADRs list includes ADR-020, -019, -018
```

## Tech Stack

### New Dependencies

**None.** This feature introduces zero new runtime or development dependencies.

### Tools Used (all pre-existing)

| Tool | Purpose | Source |
|------|---------|--------|
| Markdown | ADR-024 + SKILL.md authorship | Native to repository |
| YAML | ADR-024 frontmatter | Matches existing ADR-020 through ADR-023 convention |
| `.aod/scripts/bash/create-issue.sh` | Conditional follow-on Issue filing (Wave 2) | Pre-existing at `.aod/scripts/bash/create-issue.sh` |
| `bash` + `grep` + `git diff` | Verification gates (SC-002, SC-005, SC-006, SC-007) | Standard shell |
| Existing backward-compat test suite | Trivial pass gate | `tests/scripts/test_backward_compatibility.py` |

**No new technology introduced.** Documentation-only feature. Zero schema changes, zero script changes, zero agent changes, zero example regenerations.

---

### Feature 144: NIST AI RMF Integration Evaluation ADR

## Components

This feature does not add or modify runtime components. Components touched are documentation surfaces:

### Component 1 — ADR-025 (new)

**File**: `docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md`
**Owner**: architect (Wave 2 author)

Sections: Header (Status: Accepted, Date, Deciders, Feature 144, Related ADRs cross-referencing ADR-024 + ADR-020 + ADR-019 + ADR-018 + ADR-021 + ADR-023); Context with three Surface subsections using explicit anchors `<a id="surface-{a,b,c}"></a>`; Decision (canonical noun in first paragraph); Rationale (five-criteria justification); Alternatives Considered (Options A/B/C); Consequences (Positive/Negative/Mitigation/Follow-on); When to Re-Evaluate; References. Length expected 200-280 lines.

### Component 2 — `nist-ai-rmf-mapping.md` (new)

**File**: `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`
**Owner**: architect (Wave 2)

Content shape conditional on chosen option: Option A → complete mapping table (8 control categories → NIST Subcategories) + Surface C crosswalk; Option B/C → relationship-only stub naming wired-integration site + forward link to follow-on Issue + back-link to ADR-025. Additive only; renderable in standard Markdown.

### Component 3 — SKILL.md NIST AI RMF Relationship Section (additive edit)

**File**: `.claude/skills/tachi-control-analysis/SKILL.md`
**Owner**: architect (Wave 2, after ADR-025 Decision text is finalized)

Insertion point: After existing `## Domain Overview`, before existing `## Baseline-Aware Control Analysis Rules`. 80-200 words. Decision-noun byte-identical (case-insensitive) to ADR-025 Decision section. Relative link to ADR-025.

### Component 4 — ADR-024 Back-Reference (single-line edit)

**File**: `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md`
**Owner**: architect (Wave 2, ships in same PR as ADR-025)

Append `[ADR-025](ADR-025-nist-ai-rmf-evaluation.md) (companion NIST AI RMF evaluation)` to the existing Related ADRs line. Housekeeping edit — does NOT change ADR-024 Status field.

### Component 5 — Follow-On GitHub Issue (conditional)

**File**: GitHub Issues (filed via `bash .aod/scripts/bash/create-issue.sh`)
**Owner**: product-manager (Wave 2 cleanup, only if Option B or C chosen)

`stage:discover` label, concrete title, body links back to ADR-025, names surfaces that would change, includes effort estimate copied verbatim from ADR-025 Alternatives, names "non-disruptive"/"opt-in" constraint. **Skipped if Option A chosen** (FR-008 N/A).

## Data Flow

Documentation flows from authoring (Wave 1 + Wave 2) to publication (PR merge to `main`):

```
Wave 1 (3-hour timebox)
  web-researcher reads NIST AI RMF 1.0 + NIST AI 600-1 (canonical URLs from spec Assumptions)
  → appends findings to specs/144-*/research.md ## Wave 1 — NIST AI RMF Spec Notes section
  → escalates to PM if 3-hour budget exceeded (3 contingency options per Edge Case 1)

Wave 2 (sequential authorship)
  architect drafts ADR-025 skeleton
  → fills Surface A/B/C tables from research.md Wave 1 notes + tachi compensating controls reference
  → drafts Decision (canonical noun) → Rationale → Alternatives → Consequences → Re-Evaluation Triggers → References
  → creates .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md (content shape per chosen option)
  → appends ## NIST AI RMF Relationship section to .claude/skills/tachi-control-analysis/SKILL.md
  → appends ADR-025 back-reference to docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md Related ADRs line
  → product-manager files follow-on Issue if Option B/C chosen (FR-008)

PR Cycle (~half-day)
  Open PR with docs: prefix conventional commit
  → 13 SCs verified (shell + awk + grep + pytest + manual inspection)
  → architect reviews PR (= "Accepted at merge" attestation per Closed Q2)
  → squash-merge to main
```

## Tech Stack

No tech stack changes. Reference lineage unchanged from current state:

- **Documentation format**: Markdown (CommonMark, no GFM extensions required)
- **ADR conventions**: Match ADR-022/023/024 structural template
- **Verifiers**: shell (`grep`, `awk`, `wc -w`, `tr`), Python (`pytest tests/scripts/test_backward_compatibility.py`), git (`git diff`, `git log`)
- **Determinism baseline**: `SOURCE_DATE_EPOCH=1700000000` for byte-identical PDF comparison (per ADR-021)
- **Conventional commits**: `docs:` prefix only (per Constitution IX + SC-012)
- **GitHub CLI**: `bash .aod/scripts/bash/create-issue.sh` for FR-008 conditional Issue filing

**Zero new runtime dependencies**: empty diff on `requirements*.txt`, `pyproject.toml`, `package.json`. Zero new CLI prerequisites.

---

### Feature 142: MAESTRO Phase 3 — Agentic Threat Pattern Expansion

## Components

### Component 1: Pattern Synthesis Engine (Orchestrator Phase 3.6)

**Location**: `.claude/agents/tachi/orchestrator.md` (Phase 3.6 insertion **after** Feature 141's Phase 3.5 cross-layer correlation, **before** Phase 4 assessment)

**Responsibility**: After Phase 3.5 cross-layer chain correlation completes, synthesize the `agentic_pattern` value for each deduplicated finding using a deterministic rule-based classification engine. The engine MAY also generate net-new findings for the three previously-uncovered patterns (Agent Collusion, Emergent Behavior, Temporal Attack) when the architecture meets the multi-agent gate predicate AND the rule table indicates a pattern that no existing finding represents.

**Independence Invariants**:
- vs. Feature 141 Phase 3.5: Pattern synthesis runs AFTER cross-layer chain correlation; chains and patterns are independent grouping mechanisms
- vs. Section 4a intra-component correlation: Pattern field is finding-level metadata; Section 4a is a presentation-time grouping mechanism — orthogonal
- vs. existing 11 agents: Phase 3.6 reads the deduplicated finding IR but does NOT invoke or modify any threat-detection agent — zero-edit invariant

**Architectural Divergence from Feature 141**: Phase 3.5 produces an aggregate artifact (`attack-chains.md`) WITHOUT modifying the finding IR. Phase 3.6 modifies the finding IR in-place (write-back). Documented in ADR-026 with formal Governance Rule for Future Post-Hoc Synthesis Phases.

### Component 2: Shared Reference — Agentic Patterns

**Location**: `.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md` (NEW)

**Content**: Six canonical pattern definitions (Section 1), coverage mapping table with Coverage Strength constrained to Full/Partial/None — Coverage Required (Section 2), classification rule table R-01 through R-06+ (Section 3), multi-agent gate predicate spec with worked examples on the 6 example architectures (Section 4), explicit component_type and topology indicator token lists (canonical finite enumerations).

**Consumed by**: Orchestrator Phase 3.6 synthesis, threat-report agent Agentic Pattern Analysis section narrative.

### Component 3: Finding Schema Extension

**Location**: `schemas/finding.yaml` (UPDATE; version 1.3 → 1.4)

**Schema change**: Adds `agentic_pattern` enum field (8 values: 6 canonical + `none` + `multiple`, default `none`). Also extends `id.pattern` regex to accept `AGP-` prefix for net-new generated findings.

**Versioning rationale (ADR-026)**: Minor bump 1.3 → 1.4 under the extended enum-typed-field-addition rule (additive + has default + shape unchanged).

### Component 4: threats.md Output Extension

**Location**: `templates/tachi/output-schemas/threats.md`

**Changes**: New Pattern column in Section 7 findings table (after Category, before Component); new conditional Section 4b "Findings by Agentic Pattern" rendered iff `has-agentic-patterns: true`.

### Component 5: Threat Report Agentic Pattern Analysis Section

**Location**: `.claude/agents/tachi/threat-report.md` + `.claude/skills/tachi-threat-reporting/references/narrative-templates.md`

**Design**: New conditional section "Agentic Pattern Analysis" placed after Cross-Layer Attack Chains (Feature 141), section number grep-determined at code time. Per pattern subsection: definition + severity counts + 100-200 word narrative + impacted finding IDs. Subsections ordered by max severity descending then finding count descending. Zero-finding subsections suppressed.

### Component 6: SARIF Pattern Tag Propagation

**Location**: `.claude/agents/tachi/orchestrator.md` (SARIF emission step extension)

**Design**: Per finding with non-`none` pattern, append `maestro-pattern:<pattern_name>` to `result.properties.tags`. Format matches existing `maestro-layer:<L#>` convention exactly (lowercase, colon-separator). Findings with `agentic_pattern: none` receive no pattern tag.

### Component 7: Example Architecture Extension (agentic-app)

**Location**: `examples/agentic-app/architecture.md`

**Path Decision**: Path 1 (extend agentic-app) selected. Adds Second LLM Agent (Specialist Agent), Long-running Learning Loop, Inter-agent Communication Channel. Surfaces ≥3 of the 6 canonical patterns end-to-end. 1-2h budget per PRD planned scope.

## Data Flow

```
Architecture Description + Components + Data Flows (Phase 1 output)
    │
    ▼
[Phase 1: MAESTRO Layer Classification] (existing, unchanged)
    │
    ▼
[Phase 2: Threat Agent Dispatch] (existing — 6 STRIDE + 5 AI agents, all UNCHANGED)
    │
    ▼
[Phase 3: Deduplication + Section 4a Correlation] (existing, unchanged)
    │
    ▼
[Phase 3.5: Cross-Layer Chain Correlation] (Feature 141, unchanged)
    │ Output: attack-chains.md (conditional)
    │
    ▼
[Phase 3.6: Pattern Synthesis Engine] (NEW — Feature 142)
    │ Reads: maestro-agentic-patterns-shared.md (rule table + multi-agent gate predicate)
    │ Reads: deduplicated finding IR (post-Phase 3.5)
    │ Reads: Phase 1 component inventory + data flow graph + agentic/llm category counts
    │
    │ Step 1: Evaluate multi-agent gate predicate (FR-006 conditions a/b/c)
    │   ├─ FALSE → assign agentic_pattern: none to all findings → exit
    │   └─ TRUE  → continue
    │
    │ Step 2: For each finding in IR:
    │   ├─ Evaluate classification rule table in priority order
    │   ├─ Assign first matching pattern (or 'multiple' on equal-priority match)
    │   └─ Default to 'none' if no rule matches
    │
    │ Step 3: For each rule with generates_finding_when_no_match: true:
    │   ├─ Check if any existing finding now carries this pattern
    │   ├─ If not AND architectural context matches → emit net-new finding
    │   └─ Append net-new findings to IR (with id prefix AGP-)
    │
    │ Step 4: Set has-agentic-patterns boolean (true iff any non-'none' pattern)
    │
    ▼
[Phase 4: Coverage Matrix + Risk Summary] (existing, unchanged — passively reads new pattern field)
    │
    ▼
[Phase 5: threat-report Agent + SARIF Emission] (UPDATED)
    │
    ├──► threats.md (NEW Pattern column, conditional Section 4b)
    │
    ├──► threat-report.md (NEW conditional Agentic Pattern Analysis section)
    │      │ Loads: maestro-agentic-patterns-shared.md (canonical definitions)
    │      │ Reads: deduplicated finding IR with agentic_pattern populated
    │      │ Conditional on: has-agentic-patterns boolean
    │
    └──► SARIF (NEW maestro-pattern:<name> tags on result.properties.tags)
           Conditional per finding: only when agentic_pattern != 'none'
```

## Tech Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Pattern Synthesis Engine | Orchestrator agent (markdown instructions) | Matches existing pipeline phase pattern (Phase 3.5 precedent in Feature 141); no new runtime dependency |
| Pattern Storage | Shared reference file (markdown) | Matches existing tachi-shared pattern (maestro-layers-shared.md, attack-chain-patterns-shared.md, severity-bands-shared.md); ADR-019 governance |
| Schema | YAML (finding.yaml v1.4) | Matches existing finding schema convention; minor bump per ADR-026 extending Feature 136 precedent |
| Pattern Parsing | Python 3.11 stdlib | Matches existing tachi_parsers.py pattern; zero-dependency constraint per Feature 128/136 |
| Output Templates | Markdown (threats.md, threat-report.md) | Matches existing output-schemas convention |
| SARIF Emission | Existing orchestrator SARIF step | Reuses existing maestro-layer:<L#> tagging code path; format parity verified by unit test |
| Testing | pytest >= 8.0 | Established in Feature 128; backward-compat baselines per ADR-021 |
| Example Architecture | Markdown (agentic-app extension) | Matches existing examples/ convention; 1-2h architectural extension budget |

**Zero new runtime dependencies**: empty diff on `requirements*.txt`, `pyproject.toml`, `package.json`. Zero new CLI prerequisites.
