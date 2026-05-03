# Consumer Guide — Tachi (Markdown + YAML + Claude Code Orchestration)

**Purpose**: Automated threat modeling toolkit that extends STRIDE with AI-specific threat agents for the age of agentic applications.
**What you're building**: An open-source toolkit of 11 specialized markdown agent prompts that analyze system architecture diagrams through STRIDE + OWASP AI threat lenses in parallel, producing structured threat models (threats.md, SARIF 2.1.0, narrative reports with attack trees, and visual infographics). Platform-agnostic — works with any agentic coding tool or LLM backend.
**Target user**: Developers and security teams using agentic coding tools who need automated, architecture-specific threat modeling without specialized security expertise.
**Key constraints**:
- Agents are plain markdown prompt files — no platform dependencies, no API lock-in
- Platform-specific behaviors live exclusively in thin adapters, never in core agent prompts
- Each agent gets one constrained job — pattern-matching against known frameworks, not inventing threats
- Identical output regardless of invocation mode (AOD integration or standalone)

**How to use this guide**: Work through each seed feature in order using the AOD lifecycle. Copy each feature block into `/aod.discover` to create a GitHub Issue, then run `/aod.define` through `/aod.deliver` to implement it.

**Related documents**:
- [CONSUMER_GUIDE_TACHI_RESEARCH.md](CONSUMER_GUIDE_TACHI_RESEARCH.md) — Authoritative framework references (STRIDE, OWASP LLM/Agentic/MCP/API/Web Top 10, SARIF, CVSS, input-to-STRIDE crosswalk)
- [CONSUMER_GUIDE_TACHI_AOD_INTEGRATION.md](CONSUMER_GUIDE_TACHI_AOD_INTEGRATION.md) — Auxiliary guide for integrating Tachi into the AOD Kit (execute after F-009 ships)

## Prerequisites

- Claude Code installed (`claude` CLI)
- Git 2.30+ installed
- GitHub CLI (`gh`) installed and authenticated
- A GitHub account with repo creation permissions
- Gemini API key (optional — only needed for infographic generation in F-008)

---

## Phase 1: Clone & Initialize

Navigate to your projects directory (e.g., `~/Projects/` or `~/code/`) — the clone command will create a new subfolder here:

```bash
# Clone the public template
git clone https://github.com/davidmatousek/agentic-oriented-development-kit.git tachi
cd tachi

# Run interactive setup
make init
```

**When prompted, enter:**

| Prompt | Value |
|--------|-------|
| Project Name | `tachi` |
| Description | `Automated threat modeling toolkit extending STRIDE with AI-specific threat agents for agentic applications` |
| GitHub Org | `davidmatousek` |
| GitHub Repo | `tachi` |
| AI Agent | `1` (Claude Code) |
| Tech Stack | Select `knowledge-system` — "Markdown + YAML + Claude Code" |

> **Note**: The `knowledge-system` stack pack is the right fit — Tachi's agents are plain markdown prompt files with YAML configuration, orchestrated by Claude Code. No server, database, or cloud services required.

```bash
# Verify setup
make check
```

**Expected output:**
- All checks pass (green checkmarks)
- Stack packs available
- No pack active yet

### Post-Init Verification

Confirm that `make init` replaced all template placeholders:

```bash
# Should return NO results — all placeholders replaced
grep -rn '{{' .aod/memory/constitution.md
```

---

## Phase 2: Create GitHub Repo & Copy Tachi Guides

```bash
# Create a GitHub repo (needed for issue tracking)
gh repo create davidmatousek/tachi --public --source=. --push

# If you get "Unable to add remote origin" (origin exists from the clone), run:
git remote set-url origin https://github.com/davidmatousek/tachi.git
git push -u origin main
```

Copy the three Tachi guide files from the AOD Kit into the target repo's `docs/guides/` directory. These provide authoritative framework references that each feature epic links to during `/aod.discover` and `/aod.define`:

```bash
cp <aod-kit-path>/docs/guides/CONSUMER_GUIDE_TACHI.md             docs/guides/
cp <aod-kit-path>/docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md     docs/guides/
cp <aod-kit-path>/docs/guides/CONSUMER_GUIDE_TACHI_AOD_INTEGRATION.md docs/guides/
```

> **Note**: Replace `<aod-kit-path>` with the path to your local `agentic-oriented-development-kit` clone (e.g., `~/Projects/agentic-oriented-development-kit`).

---

## Phase 3: Activate Stack Pack & Scaffold

Open Claude Code in your project directory:

```bash
claude
```

Run these commands inside Claude Code:

```
# List available packs — verify knowledge-system shows up
/aod.stack list

# Activate the knowledge-system pack
/aod.stack use knowledge-system

# Scaffold the project structure
/aod.stack scaffold
```

### Verification Checklist

After activation:
- [ ] `.aod/stack-active.json` exists with `"pack": "knowledge-system"`
- [ ] `.claude/rules/stack/` contains conventions and persona-loader rules
- [ ] Activation summary shows loaded rules

After scaffold:
- [ ] Base directories created (`_Global/`, `_Config/`, `_Templates/`, `_Output/`, `_Archive/`)

---

## Phase 4: Adapt Scaffold to Tachi

The knowledge-system scaffold creates a generic hub-and-spoke structure. For Tachi, rename and adapt the directories to match the threat modeling domain:

| Scaffold Directory | Tachi Directory | Purpose |
|-------------------|-----------------|---------|
| `_Global/` | `agents/` | Core agent prompt definitions (orchestrator, STRIDE, +AI, report, infographic) |
| `_Config/` | `adapters/` | Platform-specific adapter configurations (Claude Code, Cursor, Copilot, GitHub Actions, Generic) |
| `_Templates/` | `templates/` | Output templates (threats.md schema, SARIF template) |
| `_Output/` | `examples/` | Example architecture inputs and generated threat model outputs |
| `_Archive/` | (remove) | Not needed — threat models use immutable `YYYY-MM-DD-{phase}/` output directories |

Type this into Claude Code to restructure:

```
Rename the scaffolded directories for the Tachi threat modeling toolkit:
- Rename _Global/ to agents/ (core agent prompt definitions)
- Rename _Config/ to adapters/ (platform-specific adapters)
- Rename _Templates/ to templates/ (output templates for threats.md, SARIF)
- Rename _Output/ to examples/ (example architecture inputs and outputs)
- Remove _Archive/ (not needed — outputs use immutable dated directories)
- Create agents/stride/ and agents/ai/ subdirectories
- Each directory should have a README explaining its purpose
```

### Verification Checklist

- [ ] `agents/` exists with `stride/` and `ai/` subdirectories
- [ ] `adapters/` exists
- [ ] `templates/` exists
- [ ] `examples/` exists
- [ ] `docs/` exists (from the AOD Kit template, for methodology docs)
- [ ] `_Archive/` is removed
- [ ] Each directory has a README

---

## Phase 5: AOD Lifecycle (Governance)

Start with F-001 (the foundation). Type this into Claude Code:

```
/aod.discover Project Skeleton & Interface Contract — Establish the repository structure, interface contract (input formats: ASCII, Mermaid, C4, PlantUML; output schema; side-effect guarantees), and threats.md output template that all agents depend on. Template covers system overview, trust boundaries, STRIDE tables, AI tables, coverage matrix, risk summary, and recommended actions. See docs/guides/CONSUMER_GUIDE_TACHI.md F-001 and docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md §1, §8, §11, §12.
```

Then run the full Triad workflow:

```
/aod.define
/aod.plan
/aod.build
/aod.deliver
```

### Subsequent Features

For each remaining feature (F-002 through F-010), copy the feature block from this guide (from `#### F-NNN:` to `---`) and paste it into `/aod.discover`. Then repeat the Triad workflow (`/aod.define` → `/aod.deliver`).

**Example for F-002:**
```
/aod.discover Orchestrator Agent — Build the central orchestrator that parses architecture input (Mermaid, C4, PlantUML, ASCII, free-text), dispatches to all 8 threat agents (6 STRIDE + 2 AI) in parallel, collects findings, and assembles the final structured threats.md. See docs/guides/CONSUMER_GUIDE_TACHI.md F-002 and docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md §1, §11, §12.
```

### Governance Verification

- [ ] `.aod/spec.md` contains PM sign-off block
- [ ] `.aod/plan.md` contains PM + Architect sign-off blocks
- [ ] `.aod/tasks.md` contains PM + Architect + Team-Lead sign-off blocks
- [ ] Feature branch follows `NNN-feature-name` format
- [ ] Each governance gate required approval before proceeding

---

## Requirements

### Functional Requirements
1. **STRIDE Analysis**: 6 specialized agents analyzing architecture through Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, and Elevation of Privilege lenses
2. **AI Threat Analysis**: 2 agents covering OWASP Top 10 for Agentic Applications + OWASP MCP Top 10 (2025) and OWASP Top 10 for LLM Applications
3. **Parallel Orchestration**: Orchestrator parses input, dispatches to 8 agents in parallel, collects findings, deduplicates, correlates, and rates risks
4. **Multi-Format Output**: threats.md (structured), threats.sarif (CI/CD), threat-report.md (narrative + attack trees), risk-scores.md/sarif (quantitative scoring via `/tachi.risk-score`), compensating-controls.md/sarif (control analysis via `/tachi.compensating-controls`), infographics (visual, via `/tachi.infographic`)
5. **Platform Portability**: Adapters for Claude Code, Cursor, Copilot, GitHub Actions, and generic prompt format

---

## Feature Summary

| ID | Feature | Group | Stories | Depends On |
|----|---------|-------|---------|------------|
| F-001 | Project Skeleton & Interface Contract | Foundation | 3 | — |
| F-002 | Orchestrator Agent | Foundation | 3 | F-001 |
| F-003 | STRIDE Threat Agents | Core | 4 | F-001, F-002 |
| F-004 | AI Threat Agents | Core | 3 | F-001, F-002 |
| F-005 | Deduplication & Risk Rating | Core | 3 | F-002, F-003, F-004 |
| F-006 | SARIF Output Generation | Core | 3 | F-005 |
| F-007 | Threat Report Agent & Attack Trees | User-Facing | 3 | F-005 |
| F-008 | Threat Infographic Agent | User-Facing | 3 | F-005 |
| F-009 | Platform Adapters | Polish | 4 | F-002, F-003, F-004 |
| F-010 | Example Threat Models | Polish | 3 | F-005, F-009 |

---

### Group 1: Foundation

#### F-001: Project Skeleton & Interface Contract

**Goal**: Establish the repository structure, interface contract, and output template that all agents depend on.

**Research** (see `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md`):
- §11 — Input Format Specifications (supported architecture input formats, Mermaid types, C4, PlantUML, ASCII)
- §12 — Input-to-STRIDE Crosswalk (the normalization table defining how input elements map to DFD types)
- §1 — Microsoft STRIDE (STRIDE-per-Element matrix for the output template's threat table structure)
- §8 — Risk Rating Matrices (OWASP 3x3 matrix for the output template's risk summary)

**Stories**:

1. **As a developer, I want a well-organized repository structure**, so that I can navigate agent definitions, adapters, templates, and documentation intuitively.
   - Repository follows the structure defined in the PRD (agents/, adapters/, templates/, examples/, docs/)
   - Each directory has a README explaining its purpose and conventions
   - LICENSE file present (Apache 2.0 or MIT — decision captured during define)

2. **As an integrator, I want a documented interface contract**, so that I can invoke Tachi from any orchestration framework without reading implementation details.
   - Interface contract specifies: input formats (ASCII diagrams, Mermaid, free-text, C4, PlantUML), invocation protocol, output schema, and side-effect guarantees (none beyond writing output files)
   - Contract includes machine-readable input/output schema (YAML or JSON)
   - Examples of valid inputs for each supported format included

3. **As a developer, I want an output template for threats.md**, so that all agents produce findings in a consistent, structured format.
   - `templates/tachi/output-schemas/threats.md` defines the complete output schema: system overview, trust boundaries, STRIDE tables, AI tables, coverage matrix, risk summary, recommended actions
   - Template includes field descriptions and example values for each section
   - Output naming convention documented: `YYYY-MM-DD-{phase}/` with immutable retention

**Interface Contract (produces)**:
- Repository structure with `agents/`, `adapters/`, `templates/`, `examples/`, `docs/`
- `docs/INTERFACE-CONTRACT.md` — input/output specification for standalone consumers
- `templates/tachi/output-schemas/threats.md` — output template for structured threat model

**Definition of Done**: Repository structure matches PRD Section 7, interface contract is testable against sample inputs, output template covers all required sections from PRD Section 4.5.

---

#### F-002: Orchestrator Agent

**Goal**: Build the central orchestrator that parses architecture input, dispatches to threat agents, and assembles the final structured threat model.

**Research** (see `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md`):
- §12 — Input-to-STRIDE Crosswalk (core orchestrator logic — element classification → DFD type → agent dispatch)
- §11 — Input Format Specifications (ASCII diagrams, Mermaid, C4, PlantUML parsing patterns)
- §1 — Microsoft STRIDE (STRIDE-per-Element matrix — which threats apply to which DFD elements)
- §1 — OWASP Threat Modeling Process (four-step process that structures the orchestrator workflow)

**Stories**:

1. **As a developer, I want the orchestrator to parse any supported architecture format**, so that I can provide my system diagram in Mermaid, free-text, C4, or PlantUML.
   - Orchestrator identifies components, data flows, and trust boundaries from any supported input format
   - Parsed architecture summary is included in output under "System Overview"
   - Trust boundaries between components/zones are identified and documented

2. **As a developer, I want the orchestrator to dispatch the parsed architecture to all threat agents in parallel**, so that analysis is comprehensive and efficient.
   - Orchestrator sends identical architecture context to all 8 threat agents (6 STRIDE + 2 AI)
   - Dispatch protocol documented for both parallel (agent framework) and sequential (manual) invocation
   - Orchestrator collects all agent outputs before proceeding to assembly

3. **As a developer, I want the orchestrator to assemble agent findings into a structured threats.md**, so that I get a single, actionable threat model.
   - Findings assembled into the template format from F-001
   - Coverage matrix generated showing threat count per component per category
   - Risk summary with Critical/High/Medium/Low counts included
   - Recommended actions listed in priority order based on risk ratings

**Interface Contract (produces)**:
- `agents/orchestrator.md` — the orchestrator agent prompt definition
- Assembled `threats.md` following the output template from F-001

**Definition of Done**: Orchestrator successfully parses a Mermaid diagram, dispatches to stub agents, and assembles a valid threats.md matching the output template.

---

### Group 2: Core

#### F-003: STRIDE Threat Agents

**Goal**: Build all 6 STRIDE agents, each analyzing architecture through exactly one threat lens with framework grounding and component-specific findings.

**Research** (see `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md`):
- §1 — Microsoft STRIDE (exact definitions from original 1999 paper + current Microsoft Learn, STRIDE-to-security-property mapping, STRIDE-per-Element matrix)
- §5 — OWASP API Security Top 10 (API-specific patterns to embed in STRIDE agents — Spoofing→API2, EoP→API1/API3/API5, DoS→API4)
- §9 — OWASP Top 10 Web (2025) (baseline web risks for cross-referencing — Injection=Tampering, Broken Access Control=EoP)
- §12 — Input-to-STRIDE Crosswalk (which STRIDE threats apply per element type)

**Stories**:

1. **As a security analyst, I want a Spoofing agent and a Tampering agent**, so that identity/authentication and data integrity threats are systematically identified.
   - Spoofing agent examines: authentication mechanisms, API keys, session management, service-to-service identity
   - Tampering agent examines: input validation, data flow integrity, message signing, database write controls
   - Every finding references a specific component from the input diagram — generic threats are rejected

2. **As a security analyst, I want a Repudiation agent and an Information Disclosure agent**, so that audit gaps and data exposure risks are identified.
   - Repudiation agent examines: logging coverage, audit trail completeness, log integrity, non-repudiation mechanisms
   - Info Disclosure agent examines: data classification, encryption (transit/rest), error messages, API response filtering, storage access controls
   - Findings include concrete mitigations tied to the system's technology stack

3. **As a security analyst, I want a Denial of Service agent and a Privilege Escalation agent**, so that availability and authorization threats are covered.
   - DoS agent examines: rate limiting, resource quotas, queue depths, circuit breakers, failover mechanisms
   - Privilege Escalation agent examines: RBAC/ABAC implementation, permission boundaries, default permissions, lateral movement paths
   - Each agent follows Microsoft STRIDE methodology — pattern-matching against known threats, not open-ended invention

4. **As a developer, I want each STRIDE agent to produce findings in a consistent table format**, so that the orchestrator can assemble them into a unified threat model.
   - Each agent outputs: ID, Component, Threat, Risk (likelihood + impact), Mitigation
   - IDs follow the convention: S-N, T-N, R-N, I-N, D-N, E-N
   - Quality guardrail: findings that don't reference specific components from the input are flagged for revision

**Interface Contract (produces)**:
- `agents/stride/spoofing.md`, `tampering.md`, `repudiation.md`, `info-disclosure.md`, `denial-of-service.md`, `privilege-escalation.md`
- Each agent produces a table of findings in the threats.md STRIDE format

**Definition of Done**: All 6 STRIDE agents produce specific, component-referencing findings when given a sample architecture diagram; no generic/untargeted threats in output.

---

#### F-004: AI Threat Agents

**Goal**: Build 2 AI-specific threat agents extending STRIDE with Agentic AI and LLM threat categories mapped to OWASP frameworks.

**Research** (see `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md`):
- §3 — OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10 — official IDs, names, descriptions; how agentic differs from LLM threats)
- §4 — OWASP MCP Top 10 2025 (MCP01–MCP10 — tool poisoning sub-techniques, real-world CVEs, MCP architecture overview)
- §2 — OWASP Top 10 for LLM Applications v2025 (LLM01–LLM10 — all categories with attack vectors and mitigations; v1.x→v2025 changes)
- §13 — Consumer Guide Corrections (§13.1 ID format mismatches, §13.2 outdated LLM category names, §13.5 coverage gaps vs official categories)

**Stories**:

1. **As a security analyst, I want an Agentic AI Threat Agent**, so that threats unique to systems with autonomous AI tool access are identified against OWASP Agentic Top 10 and OWASP MCP Top 10 (2025).
   - Examines: excessive agency, tool/function abuse, insecure plugin execution, agent-to-agent trust boundaries
   - Covers MCP-specific threats: server poisoning, tool poisoning, rug pulls via tool description manipulation
   - Covers multi-agent threats: orchestration attacks, uncontrolled autonomous actions, insufficient human oversight

2. **As a security analyst, I want an LLM Threat Agent**, so that threats specific to LLM integration are identified against OWASP LLM Top 10.
   - Examines: prompt injection (direct and indirect), training data poisoning, model denial of service
   - Covers: insecure output handling, supply chain vulnerabilities (model provenance, plugin trust)
   - Covers: sensitive information disclosure via model output, excessive reliance on LLM output without validation

3. **As a developer, I want AI agents to produce findings with OWASP reference IDs**, so that findings map directly to established vulnerability catalogs.
   - Agentic agent outputs: ID (AG-N), Component, Threat, OWASP Ref (OWASP-AG-xx or OWASP-MCP-xx), Risk, Mitigation
   - LLM agent outputs: ID (LLM-N), Component, Threat, OWASP Ref (OWASP-LLM-xx), Risk, Mitigation
   - AI agents produce findings only when the architecture contains AI/LLM/agent components; empty results for non-AI architectures

**Interface Contract (produces)**:
- `agents/ai/agentic-threats.md`, `agents/ai/llm-threats.md`
- Each agent produces a table of findings with OWASP reference IDs in the threats.md AI format

**Definition of Done**: Both AI agents produce OWASP-referenced findings when given an agentic architecture, and correctly produce empty results for purely traditional architectures.

---

#### F-005: Deduplication & Risk Rating

**Goal**: Enhance the orchestrator with cross-agent deduplication, correlation, and calibrated risk rating using a consistent likelihood × impact matrix.

**Research** (see `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md`):
- §8 — Risk Rating Matrices (OWASP 3x3 matrix, likelihood/impact factors, NIST SP 800-30 5-level alternative)
- §10 — CVSS (severity scale alignment — Tachi risk levels → SARIF scores → CVSS ratings → GitHub display)

**Stories**:

1. **As a developer, I want the orchestrator to deduplicate overlapping findings**, so that the same underlying issue flagged by multiple agents appears as one correlated finding rather than redundant entries.
   - When multiple agents flag the same component for related threats, they are correlated into a single finding
   - Correlated findings show all contributing agent perspectives (e.g., "Tampering + LLM: unvalidated LLM output")
   - Original individual findings preserved for audit; correlation shown in the assembled output

2. **As a security analyst, I want consistent risk ratings using a likelihood × impact matrix**, so that threat severity is calibrated across all agents.
   - Risk matrix applied: Likely × Critical = Critical, Possible × High = High, Unlikely × Medium = Medium, etc.
   - Each agent provides likelihood and impact assessments; orchestrator applies the calibration matrix
   - Risk summary with Critical/High/Medium/Low counts generated automatically

3. **As a developer, I want a coverage matrix**, so that I can see which components have been analyzed across all 8 threat categories.
   - Matrix shows: Component × [S, T, R, I, D, E, Agentic, LLM] with finding counts per cell
   - Zero-coverage cells highlighted as potential analysis blind spots
   - Matrix included in the output threats.md under "Coverage Matrix" section

**Interface Contract (produces)**:
- Enhanced `agents/orchestrator.md` with deduplication logic, risk matrix, and coverage matrix generation
- Coverage matrix and risk summary sections in threats.md output

**Definition of Done**: Orchestrator correctly deduplicates overlapping findings from different agents, applies consistent risk ratings via the matrix, and generates a complete coverage matrix.

---

#### F-006: SARIF Output Generation

**Goal**: Generate threats.sarif in SARIF 2.1.0 format for CI/CD pipeline integration — the first threat modeling tool to produce SARIF output.

**Research** (see `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md`):
- §6 — SARIF 2.1.0 (JSON structure, key objects, GitHub Code Scanning constraints and upload limits)
- §6 — SARIF severity mapping (`security-severity` float 0.0–10.0, GitHub Critical/High/Medium/Low thresholds)
- §10 — CVSS (end-to-end alignment table: Tachi risk level → SARIF score → CVSS rating → GitHub display)

**Stories**:

1. **As a DevOps engineer, I want threats exported as SARIF 2.1.0**, so that threat findings appear natively in GitHub Code Scanning, Azure DevOps, and other SARIF-consuming tools.
   - Each threat becomes a SARIF "result" with location, severity, and rule mapping
   - STRIDE categories and OWASP references map to SARIF rule IDs
   - Risk ratings map to SARIF severity levels (error, warning, note)

2. **As a CI engineer, I want SARIF output generated alongside threats.md**, so that both human-readable and machine-readable outputs are produced in a single run.
   - Orchestrator generates both `threats.md` and `threats.sarif` in the same output directory
   - SARIF output follows the same naming convention (`YYYY-MM-DD-{phase}/`)
   - Generated SARIF validates against the official SARIF 2.1.0 JSON schema

3. **As a developer, I want SARIF results linked to architecture components**, so that findings are navigable in code scanning UIs.
   - Each SARIF result references the component name and trust boundary as location
   - Results include the mitigation recommendation as a markdown message
   - SARIF tool metadata identifies Tachi version and the agent roster used

**Interface Contract (produces)**:
- SARIF generation logic added to orchestrator assembly phase
- `threats.sarif` output file conforming to SARIF 2.1.0 specification

**Definition of Done**: Generated SARIF validates against the SARIF 2.1.0 JSON schema and is consumable by GitHub Code Scanning; all findings from threats.md are represented.

---

### Group 3: User-Facing

#### F-007: Threat Report Agent & Attack Trees

**Goal**: Build the report agent that transforms structured threats.md into a narrative report with executive summary, Mermaid attack trees, and prioritized remediation roadmap.

**Research** (see `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md`):
- §7 — Attack Tree Methodology (Schneier 1999 — root/intermediate/leaf nodes, AND/OR logic, propagation rules, Mermaid rendering with `flowchart TD` and classDef styling)
- §8 — Risk Rating Matrices (OWASP risk methodology for prioritizing remediation roadmap items)

**Stories**:

1. **As a CISO, I want a narrative threat report**, so that I can present findings to management and compliance without interpreting raw tables.
   - Report includes: executive summary, agent-by-agent analysis with full reasoning, architecture risk annotations
   - Cross-cutting themes identified and explained across agent boundaries
   - Compliance relevance notes included where applicable

2. **As a security engineer, I want Mermaid attack trees for Critical and High findings**, so that I can visualize attack paths and preconditions.
   - Each Critical/High finding generates a Mermaid-format attack tree showing goal, preconditions, steps, and branching paths
   - Attack trees embedded in `threat-report.md` AND saved as standalone `.md` files in `attack-trees/`
   - Standalone files enable reuse in presentations and security documentation

3. **As a project manager, I want a prioritized remediation roadmap**, so that I can plan security work with effort estimates.
   - Remediation roadmap lists mitigations in priority order (Critical first)
   - Each mitigation includes effort estimate (low/medium/high) and dependency notes
   - Roadmap items are actionable — directly convertible to development tasks or backlog items

**Interface Contract (produces)**:
- `agents/threat-report.md` — the report agent prompt definition
- `threat-report.md` output with embedded Mermaid attack trees
- `attack-trees/*.md` — standalone Mermaid attack tree files for Critical/High findings

**Definition of Done**: Report agent produces a narrative report with attack trees from a sample threats.md; report is comprehensible by a non-technical audience.

---

#### F-008: Threat Infographic Agent

**Goal**: Build the infographic agent that generates a visual risk specification and produces a presentation-ready image via Gemini API.

**Research** (see `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md`):
- §8 — Risk Rating Matrices (OWASP risk levels and severity scales for visual risk distribution charts)
- §10 — CVSS (severity color conventions — Critical=red, High=orange, Medium=yellow, Low=blue)

**Stories**:

1. **As an executive, I want a visual threat infographic**, so that I can quickly understand the risk landscape without reading a full report.
   - Infographic shows: risk distribution chart, coverage heat map, top critical findings summary
   - Architecture threat overlay shows which components carry the most risk
   - Visual design is clean, professional, and presentation-ready

2. **As a developer, I want the infographic agent to produce a structured spec for Gemini image generation**, so that the visual is produced automatically from threat data.
   - Agent reads threats.md and generates a detailed infographic specification (layout, data points, color coding, text content)
   - Specification is fed to Gemini image generation API to produce `threat-infographic.jpg`
   - Spec is also saved as markdown for manual rendering when Gemini is unavailable

3. **As a developer, I want infographic generation to be optional and configurable**, so that projects without Gemini API access can still use all other Tachi features.
   - Controlled by `gemini_infographic: true/false` in configuration
   - When disabled, the infographic spec markdown is still generated (useful for manual rendering or alternative image tools)
   - Missing Gemini API key produces a warning, not a blocking error

**Interface Contract (produces)**:
- `agents/threat-infographic.md` — the infographic agent prompt definition
- `threat-infographic.jpg` output via Gemini API (or `.md` spec when Gemini unavailable)

**Definition of Done**: Infographic agent produces a visual specification from sample threats.md; Gemini integration generates a presentable image when API key is configured.

---

### Group 4: Polish

#### F-009: Platform Adapters

**Goal**: Create platform-specific adapters that translate core agent definitions into each tool's native format, enabling Tachi to work across the agentic coding ecosystem.

**Research** (see `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md`):
- §11 — Input Format Specifications (Mermaid diagram types, C4 tooling — Structurizr, C4-PlantUML, Mermaid C4 experimental status)
- §6 — SARIF 2.1.0 (GitHub Actions SARIF upload via `codeql/upload-sarif@v3` for the GitHub Actions adapter)

**Stories**:

1. **As a Claude Code user, I want a Claude Code adapter**, so that I can install Tachi into my project's `.claude/agents/` directory and invoke it natively.
   - Adapter maps agent prompts into `.claude/agents/tachi/` format
   - Orchestrator dispatch uses Claude Code's Agent tool for parallel execution
   - Installation is a single `cp -r` command with clear README instructions

2. **As a Cursor or Copilot user, I want adapters for my coding tool**, so that I can use Tachi without switching platforms.
   - Cursor adapter maps to `.cursor/rules/` format
   - Copilot adapter maps to `.github/copilot/` format
   - Each adapter preserves full agent prompt content with no lossy transformation

3. **As a CI engineer, I want a GitHub Actions adapter**, so that Tachi runs automatically on PRs that modify architecture documents.
   - GitHub Actions workflow YAML triggers on changes to architecture files
   - Workflow invokes orchestrator and threat agents via LLM API
   - SARIF output uploads to GitHub Code Scanning automatically

4. **As an integrator, I want a generic adapter**, so that I can invoke Tachi from any LLM backend or orchestration framework without platform-specific tooling.
   - Generic adapter provides standalone prompt files with clear invocation instructions
   - Instructions cover: sequential invocation (any chat UI) and programmatic invocation (any LLM API)
   - No dependencies beyond an LLM that accepts text prompts

**Interface Contract (produces)**:
- `adapters/claude-code/`, `adapters/cursor/`, `adapters/copilot/`, `adapters/github-actions/`, `adapters/generic/`
- Each adapter directory includes installation README and platform-specific configuration

**Definition of Done**: All 5 adapters install cleanly on their target platforms; generic adapter verified with copy-paste into a standalone LLM chat.

---

#### F-010: Example Threat Models

**Goal**: Create end-to-end examples showing Tachi input and output for three common architecture types, demonstrating value across AI and non-AI systems.

**Research** (see `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md`):
- §12 — Input-to-STRIDE Crosswalk (worked ASCII diagram example with full element extraction table — use as basis for example architectures)
- §9 — OWASP Top 10 Web 2025 (web app example should cross-reference A01–A10)
- §3 — OWASP Agentic Top 10 (agentic app example should demonstrate ASI01–ASI10 coverage)
- §4 — OWASP MCP Top 10 (agentic app example should demonstrate MCP01–MCP10 coverage)
- §13.6 — Framework Relationship Hierarchy (the layered model showing how all frameworks relate — document in examples README)

**Stories**:

1. **As a new user, I want a web application example**, so that I can see what Tachi produces for a traditional architecture before running it on my own system.
   - `examples/web-app/architecture.md` — Mermaid diagram of a typical web app (frontend, API, database, auth service)
   - `examples/web-app/threats.md` — complete generated threat model with all STRIDE categories populated
   - Example demonstrates full STRIDE coverage on a non-AI architecture (AI agents produce empty results)

2. **As an AI developer, I want an agentic application example**, so that I can see how the +AI agents add value beyond standard STRIDE.
   - `examples/agentic-app/architecture.md` — Mermaid diagram of an agentic app (LLM, MCP servers, tool access, multi-agent orchestration)
   - `examples/agentic-app/threats.md` — full threat model including Agentic + LLM findings with OWASP references
   - Example demonstrates the unique value of OWASP Agentic + MCP + LLM Top 10 coverage

3. **As a platform engineer, I want a microservices example**, so that I can see how Tachi handles complex multi-service architectures with many trust boundaries.
   - `examples/microservices/architecture.md` — Mermaid diagram of a microservices system (API gateway, services, message queue, databases)
   - `examples/microservices/threats.md` — full threat model showing cross-service threats and trust boundary analysis
   - Example demonstrates coverage matrix value across many components and service boundaries

**Interface Contract (produces)**:
- `examples/web-app/`, `examples/agentic-app/`, `examples/microservices/`
- Each directory includes `architecture.md` (input) and `threats.md` (generated output)

**Definition of Done**: All 3 examples contain valid Mermaid architecture diagrams and complete threat model outputs matching the output template; examples are referenced from the project README.

---

## How to Execute Each Feature

For each feature in dependency order:
1. Copy the feature block (from `#### F-NNN:` to `---`)
2. Run `/aod.discover` and paste the block as the idea description
3. Run `/aod.define` to create the PRD
4. Run `/aod.plan` to create spec, plan, and tasks
5. Run `/aod.build` to implement
6. Run `/aod.deliver` to close

## Feature Completion Tracker

| ID | Feature | Status |
|----|---------|--------|
| F-001 | Project Skeleton & Interface Contract | [ ] |
| F-002 | Orchestrator Agent | [ ] |
| F-003 | STRIDE Threat Agents | [ ] |
| F-004 | AI Threat Agents | [ ] |
| F-005 | Deduplication & Risk Rating | [ ] |
| F-006 | SARIF Output Generation | [ ] |
| F-007 | Threat Report Agent & Attack Trees | [ ] |
| F-008 | Threat Infographic Agent | [ ] |
| F-009 | Platform Adapters | [ ] |
| F-010 | Example Threat Models | [ ] |

## Success Criteria
- All 10 features implemented and delivered
- Each feature independently demonstrable
- Valid dependency chain maintained throughout
- Output parity verified: same input diagram produces identical threats.md regardless of adapter/invocation mode
- All 6 STRIDE agents produce component-specific findings (no generic threats)
- AI agents produce OWASP-referenced findings for agentic architectures and empty results for non-AI architectures
- Generated SARIF validates against the SARIF 2.1.0 JSON schema and is consumable by GitHub Code Scanning

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| `make init` fails | Ensure Git is installed (`git --version`) |
| `/aod.stack use` says pack not found | Verify `stacks/knowledge-system/STACK.md` exists |
| Scaffold conflicts with existing files | Choose overwrite/skip per-file when prompted |
| Governance sign-off loops | Address reviewer feedback, re-submit until APPROVED |
| `gh repo create` fails | Ensure `gh auth login` completed successfully |
| Gemini infographic generation fails | F-008 is optional — `gemini_infographic: false` skips it, spec markdown still generated |
| Agent produces generic threats | Quality guardrail failure — findings must reference specific components from the input diagram |

---

## Notes

- This guide uses the **public template** repo (`agentic-oriented-development-kit`)
- Agents are plain markdown files — no platform dependencies, no API lock-in
- The `knowledge-system` stack pack provides conventions for markdown + YAML + Claude Code projects
- Core governance agents (PM, Architect, Team-Lead) are **not** affected by stack packs — they remain stack-agnostic
- The Research guide (`CONSUMER_GUIDE_TACHI_RESEARCH.md`) is the authoritative reference for all OWASP/STRIDE framework details
- The AOD Integration guide (`CONSUMER_GUIDE_TACHI_AOD_INTEGRATION.md`) should be executed after F-009 ships
