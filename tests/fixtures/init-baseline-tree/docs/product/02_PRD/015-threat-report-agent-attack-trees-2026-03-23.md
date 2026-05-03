---
prd:
  number: "015"
  topic: threat-report-agent-attack-trees
  created: 2026-03-23
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-03-23, status: approved, notes: "PRD drafted by PM via ~aod-define skill with GitHub Issue #15 user stories, consumer guide F-007, and attack tree research as primary inputs"}
  architect_signoff: {agent: architect, date: 2026-03-23, status: approved_with_concerns, notes: "Technically feasible. 14 findings (0 critical, 1 high, 7 medium, 6 low). High: context window pressure — Phase 5 should run in fresh context with only threats.md as input, not accumulated pipeline context. Medium: add schemas/report.yaml, define Mermaid node naming conventions, add report validation checklist. All resolvable in spec phase."}
  techlead_signoff: {agent: team-lead, date: 2026-03-23, status: approved_with_concerns, notes: "Feasible in 1 sprint (80% confidence, 3.5-5.0h). Effort sizing L/L/M correct. 3-wave execution strategy. 3 concerns: elevate FR-6 to P0, resolve open questions 1-2 before task breakdown, include example attack trees in agent prompt spec."}
source:
  idea_id: 15
  story_id: null
---

# Threat Report Agent & Attack Trees - Product Requirements Document

**Status**: Approved
**Created**: 2026-03-23
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: Phase 2 (Reporting & Integration)
**Priority**: P1 (High)

---

## Executive Summary

### The One-Liner
Build a report agent that transforms the structured `threats.md` output into a narrative threat report with executive summary, Mermaid attack trees for Critical/High findings, and a prioritized remediation roadmap.

### Problem Statement
Developers using tachi generate a structured `threats.md` document containing threat findings from up to 11 agents (6 STRIDE + 5 AI). While this document is technically complete — with finding tables, risk ratings, coverage matrices, and recommended actions — it is optimized for security engineers who can interpret tabular threat data directly.

Three critical audiences are underserved by the current output:

1. **CISOs and management** need narrative context to present findings to boards and compliance teams. Raw finding tables require manual interpretation to extract cross-cutting themes, architectural risk patterns, and business impact summaries. Without a narrative report, CISOs must spend hours translating technical tables into executive-ready presentations.

2. **Security engineers** analyzing Critical and High findings need to visualize attack paths — the chain of preconditions, sub-goals, and branching strategies an attacker would follow. Flat finding tables show individual threats but not how they combine into multi-step attack scenarios. Attack trees (Schneier 1999) are the established methodology for this visualization, but no existing threat modeling tool generates them automatically from findings.

3. **Project managers** need a prioritized remediation roadmap with effort estimates to plan security work. The current "Recommended Actions" table lists mitigations by risk level but lacks effort sizing, dependency relationships, and the actionable format needed for backlog planning.

Without this reporting layer, tachi produces raw analytical output that requires significant manual effort to make actionable for non-security stakeholders.

### Proposed Solution
Add a report agent (`agents/threat-report.md`) that consumes the structured `threats.md` produced by the orchestrator and generates three deliverables:

1. **Narrative threat report** (`threat-report.md`) — Executive summary, agent-by-agent analysis with full reasoning, architecture risk annotations, cross-cutting theme identification, and compliance relevance notes. Written for a non-technical audience while preserving technical accuracy.

2. **Mermaid attack trees** — For each Critical and High finding, generate a Mermaid `flowchart TD` attack tree showing the attacker's goal (root), decomposed sub-goals (intermediate nodes with AND/OR gates), and concrete atomic attacks (leaf nodes). Trees are embedded inline in `threat-report.md` AND saved as standalone files in `attack-trees/` for reuse in presentations and security documentation.

3. **Prioritized remediation roadmap** — Ordered by risk level (Critical first), each mitigation includes effort estimate (low/medium/high), dependency notes, and is formatted as an actionable item directly convertible to development tasks or backlog items.

The report agent is a **markdown prompt file**, consistent with tachi's architecture where all agents are prompt files, not application code. The orchestrator invokes the report agent as a new Phase 5 (Report) after the existing Phase 4 (Assess) completes.

### Success Criteria
- Report agent produces a narrative `threat-report.md` from the sample `threats.md` in `examples/mermaid-agentic-app/`
- Report is comprehensible by a non-technical audience (CISO level) — validates against the Definition of Done
- Every Critical and High finding has a corresponding Mermaid attack tree with root goal, intermediate nodes, and leaf actions
- Attack trees are embedded in the report AND saved as standalone `.md` files in `attack-trees/`
- Remediation roadmap lists all mitigations in priority order with effort estimates
- All findings from `threats.md` are accounted for in the report — no findings lost in transformation
- Cross-cutting themes are identified when findings from different agents target the same component or attack vector

### Timeline
Phase 2 delivery — estimated 1 sprint

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: `docs/product/01_Product_Vision/product-vision.md`

The threat report agent directly supports tachi's mission as "the default threat modeling toolkit for any team building agentic AI applications." Raw threat tables serve security engineers but exclude the broader audience — CISOs, project managers, and compliance teams — who need narrative context to act on findings. By producing executive-ready reports with attack tree visualizations, tachi becomes a complete threat modeling solution, not just a threat identification tool.

Attack trees are a foundational security methodology (Schneier 1999, derived from Bell Labs fault tree analysis). No existing threat modeling tool generates Mermaid-format attack trees automatically from findings. This positions tachi as the first toolkit to bridge structured threat analysis with visual attack path modeling.

### Roadmap Fit
**Phase**: Phase 2 (Reporting & Integration)
**Dependencies**: F-001, F-003, F-005, F-007, F-010 (all delivered) — provides the complete `threats.md` with finding IR, risk ratings, and correlation groups
**Blocks**: Future dashboard/visualization features that consume the report format

---

## Target Users & Personas

### Primary Persona: CISO / Security Director
- **Role**: Security leadership, board reporting, compliance oversight
- **Experience**: Understands security concepts but does not interpret raw finding tables daily
- **Goals**: Present threat model findings to management and compliance teams without manual interpretation
- **Pain Points**: Must manually translate tabular threat data into narrative presentations; cross-cutting themes are invisible in flat tables

**Why This Matters**: CISOs are the primary decision-makers for security investment. A narrative report with executive summary enables them to present findings in board-ready format, accelerating security remediation budgets and compliance sign-offs.

### Secondary Persona: Security Engineer
- **Role**: Technical security analysis, penetration testing, architecture review
- **Experience**: Deep security expertise, familiar with attack trees and STRIDE methodology
- **Goals**: Visualize multi-step attack paths and preconditions for Critical/High findings
- **Pain Points**: Flat finding tables show individual threats but not how they chain together; must manually construct attack trees for presentations

### Tertiary Persona: Project Manager
- **Role**: Development planning, backlog management, sprint coordination
- **Experience**: Manages development teams, allocates resources to security work
- **Goals**: Convert threat findings into actionable backlog items with effort estimates
- **Pain Points**: Recommended Actions table lacks effort sizing and dependency information; must manually triage and estimate security work items

---

## User Stories

### US-1: Narrative Threat Report for Management
**When**: I have a completed threat model (`threats.md`) and need to present findings to management and compliance,
**I want to**: have findings transformed into a narrative report with executive summary,
**So I can**: present to boards and compliance teams without manually interpreting raw threat tables.

**Acceptance Criteria**:
- **Given** a completed `threats.md` with findings from STRIDE and AI agents, **when** the report agent runs, **then** it produces `threat-report.md` with an executive summary section
- **Given** the executive summary, **when** read by a non-technical audience, **then** it communicates the overall risk posture, top threats, and recommended actions without requiring knowledge of STRIDE methodology
- **Given** findings from multiple agents targeting the same component, **when** the report agent analyzes them, **then** it identifies and explains cross-cutting themes across agent boundaries
- **Given** findings with OWASP/CWE references, **when** included in the report, **then** compliance relevance notes are added where applicable (e.g., SOC2, ISO 27001 mapping)

**Priority**: P0
**Effort**: L

### US-2: Mermaid Attack Trees for Critical/High Findings
**When**: I need to understand and communicate attack paths for the most severe findings,
**I want to**: Mermaid-format attack trees generated for Critical and High findings,
**So I can**: visualize attack goals, preconditions, steps, and branching paths.

**Acceptance Criteria**:
- **Given** a Critical or High finding from `threats.md`, **when** the report agent processes it, **then** it generates a Mermaid `flowchart TD` attack tree with root goal, intermediate sub-goals, and leaf actions
- **Given** an attack tree, **when** rendered, **then** it uses Schneier's methodology: AND nodes require all children, OR nodes require any one child
- **Given** generated attack trees, **when** the report agent completes, **then** trees are embedded inline in `threat-report.md` AND saved as standalone `.md` files in `attack-trees/`
- **Given** a Medium or Low finding, **when** processed, **then** no attack tree is generated (attack trees are reserved for Critical/High severity only)

**Priority**: P0
**Effort**: L

### US-3: Prioritized Remediation Roadmap
**When**: I need to plan security remediation work based on threat model findings,
**I want to**: a prioritized remediation roadmap with effort estimates,
**So I can**: convert findings into development tasks and plan sprint work.

**Acceptance Criteria**:
- **Given** all findings from `threats.md`, **when** the remediation roadmap is generated, **then** mitigations are listed in priority order (Critical first, then High, Medium, Low)
- **Given** each mitigation item, **when** listed in the roadmap, **then** it includes an effort estimate (low/medium/high) and dependency notes
- **Given** the roadmap items, **when** reviewed by a project manager, **then** each item is directly convertible to a development task or backlog item without further interpretation

**Priority**: P1
**Effort**: M

---

## Functional Requirements

### FR-1: Report Agent Prompt Definition

**Description**: Create `agents/threat-report.md` as a markdown prompt file that defines the report agent's analysis methodology, output structure, and quality requirements.

**Agent Responsibilities**:
- Parse the structured `threats.md` input (YAML frontmatter + 7 required sections)
- Generate narrative analysis with executive-appropriate language
- Construct Mermaid attack trees following Schneier's methodology
- Produce prioritized remediation roadmap with effort estimates
- Identify cross-cutting themes across agent boundaries

**Agent Prompt Structure** (follows existing agent pattern):
- YAML header with agent metadata, input contract, output contract
- Analysis methodology section
- Output format specification
- Quality requirements and constraints

### FR-2: Narrative Report Structure

**Description**: Define the `threat-report.md` output structure with required sections.

**Required Sections**:

| Section | Content | Source |
|---------|---------|--------|
| **Executive Summary** | Overall risk posture, top threats, key recommendations | Derived from Section 6 (Risk Summary) and Section 7 (Recommended Actions) |
| **Architecture Overview** | System context and trust boundary summary | Derived from Sections 1-2 (System Overview, Trust Boundaries) |
| **Threat Analysis** | Agent-by-agent narrative with reasoning and component annotations | Derived from Sections 3-4 (STRIDE + AI tables) |
| **Cross-Cutting Themes** | Patterns spanning multiple agents or components | Computed from finding correlation and component overlap analysis |
| **Attack Trees** | Mermaid attack trees for Critical/High findings | Generated from Critical/High findings using Schneier methodology |
| **Remediation Roadmap** | Prioritized mitigations with effort estimates | Derived from Section 7 with effort sizing added |
| **Appendix: Finding Reference** | Mapping from report sections to original finding IDs | Cross-reference back to `threats.md` finding IDs |

### FR-3: Mermaid Attack Tree Generation

**Description**: Generate Mermaid-format attack trees for each Critical and High finding following Schneier's attack tree methodology.

**Attack Tree Structure**:
- **Root node**: Attacker's ultimate goal (derived from finding `threat` field)
- **Intermediate nodes**: Decomposed sub-goals with AND/OR gate logic
- **Leaf nodes**: Concrete atomic attack actions
- **Node annotations**: Risk level coloring per Mermaid styling

**Mermaid Rendering Conventions** (from research §7):
```
flowchart TD
    style root fill:#ff6b6b    %% Red for goals
    style and_gate fill:#ffa500 %% Orange for AND gates
    style or_branch fill:#4ecdc4 %% Blue/teal for OR branches
    style leaf fill:#95e1d3      %% Green for leaf actions
```

**Output Locations**:
- Inline in `threat-report.md` within the Attack Trees section
- Standalone files: `attack-trees/{finding-id}-attack-tree.md` (e.g., `attack-trees/AG-1-attack-tree.md`)

### FR-4: Remediation Roadmap Format

**Description**: Transform the Recommended Actions table from `threats.md` into an actionable remediation roadmap.

**Roadmap Item Format**:

| Field | Source | Description |
|-------|--------|-------------|
| Priority | `risk_level` from finding | Critical → Immediate, High → Short-term, Medium → Medium-term, Low → Backlog |
| Finding ID | `id` from finding | Cross-reference to `threats.md` |
| Component | `component` from finding | Target system component |
| Mitigation | `mitigation` from finding | Recommended countermeasure |
| Effort | Report agent assessment | Low / Medium / High based on mitigation complexity |
| Dependencies | Report agent analysis | Other mitigations or prerequisites |

**Ordering**: Critical findings first, then High, Medium, Low. Within same risk level, order by component to group related work.

### FR-5: Cross-Cutting Theme Identification

**Description**: Analyze findings across all agents to identify patterns that span multiple threat categories or components.

**Theme Detection Criteria**:
- Multiple findings from different agents targeting the same component
- Similar mitigation recommendations across different threat categories
- Findings that form an attack chain (one finding's impact enables another's precondition)
- Component clusters with disproportionately high finding counts

**Output**: Narrative section explaining each theme with references to contributing finding IDs.

### FR-6: Orchestrator Integration

**Description**: Integrate the report agent into the orchestrator pipeline as Phase 5 (Report).

**Integration Points**:
- Phase 5 runs after Phase 4 (Assess) completes and `threats.md` is generated
- Report agent receives the complete `threats.md` as input
- Output is written to the same output directory as `threats.md` and `threats.sarif`
- Phase 5 is optional — the orchestrator can be configured to skip report generation

**Output Directory Structure** (after Phase 5):
```
YYYY-MM-DD-{phase}/
├── threats.md           # Phase 4 output (existing)
├── threats.sarif         # Phase 4 output (existing, F-012)
├── threat-report.md      # Phase 5 output (new)
└── attack-trees/         # Phase 5 output (new)
    ├── AG-1-attack-tree.md
    ├── AG-2-attack-tree.md
    └── ...
```

### FR-7: Correlated Finding Handling

**Description**: Respect correlation groups from `threats.md` Section 4a when generating the report.

- Correlated findings are discussed as a group in the narrative, not individually repeated
- Attack trees for correlated findings reference the primary finding; correlated peers are noted as related attack vectors
- Remediation roadmap consolidates correlated findings into a single roadmap item with notes on the correlation scope

---

## Non-Functional Requirements

### Comprehensibility
- The executive summary MUST be understandable by a reader with no security training — no unexplained acronyms, no assumed STRIDE knowledge
- Technical depth increases progressively through the report: executive summary → architecture overview → detailed analysis → attack trees
- Mermaid attack trees MUST render correctly in standard Mermaid renderers (GitHub, VS Code, Mermaid Live Editor)

### Completeness
- Every finding in `threats.md` MUST appear in the narrative report — no findings lost in transformation
- Every Critical and High finding MUST have a corresponding attack tree
- The remediation roadmap MUST include all findings, not just Critical/High

### Traceability
- Every statement in the report MUST be traceable to a specific finding ID in `threats.md`
- The appendix MUST provide a complete mapping from report sections to finding IDs
- Attack tree file names MUST include the finding ID for cross-reference

### Consistency
- Risk level language in the report MUST match the risk levels in `threats.md` — no reinterpretation
- Component names MUST match exactly between `threats.md` and the report
- Mitigation recommendations MUST preserve the original mitigation text, with effort estimates added as supplementary information

---

## Success Metrics

### Primary Metrics

**Report Comprehensibility**: Executive summary passes non-technical audience review
- **Baseline**: N/A (no report output exists)
- **Target**: Report is comprehensible by a non-technical audience per the Definition of Done
- **Timeline**: At delivery

**Attack Tree Coverage**: 100% of Critical/High findings have attack trees
- **Baseline**: N/A
- **Target**: Every Critical and High finding has a Mermaid attack tree in both inline and standalone format
- **Timeline**: At delivery

**Finding Completeness**: 100% of `threats.md` findings represented in the report
- **Baseline**: N/A
- **Target**: Zero finding loss between `threats.md` and `threat-report.md`
- **Timeline**: At delivery

**Mermaid Validity**: 100% of attack trees render correctly in standard Mermaid renderers
- **Baseline**: N/A
- **Target**: All attack trees render in GitHub markdown preview and Mermaid Live Editor
- **Timeline**: At delivery

---

## Scope & Boundaries

### In Scope (MVP)

**Must Have (P0)**:
- Report agent prompt file (`agents/threat-report.md`)
- Narrative report generation with executive summary
- Mermaid attack trees for Critical and High findings
- Inline embedding and standalone attack tree files
- Cross-cutting theme identification
- Finding-to-report traceability

**Should Have (P1)**:
- Prioritized remediation roadmap with effort estimates
- Correlated finding group handling in narrative and roadmap
- Orchestrator integration as Phase 5 (Report)
- Compliance relevance annotations where applicable

### Out of Scope

**Won't Have**:
- Interactive attack tree visualization (use existing Mermaid renderers)
- PDF or HTML export of the report (markdown is the output format)
- Quantitative risk scoring or financial impact estimation
- Attack tree generation for Medium/Low findings (reserved for Critical/High)
- Custom report templates or branding (single standard format)
- Automated remediation ticket creation in issue trackers (roadmap items are manual)
- Report comparison across multiple threat model runs (single-run reports only)

### Assumptions
- `threats.md` is complete and valid (produced by the orchestrator with all phases complete)
- The finding IR schema (`schemas/finding.yaml`) remains stable
- Mermaid `flowchart TD` syntax is sufficient for attack tree representation
- Effort estimates are qualitative (low/medium/high), not quantitative time estimates
- The report agent runs within the same LLM context as the orchestrator

### Constraints
- **No application code**: Report generation is orchestrator prompt instructions, consistent with tachi's architecture
- **Mermaid compatibility**: Attack trees must use only standard Mermaid syntax (no plugins or extensions)
- **Dependency**: Requires complete `threats.md` output — report agent cannot run independently of the orchestrator pipeline

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Attack tree quality and depth consistency
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Define explicit attack tree construction guidelines in the agent prompt — minimum 3 levels of decomposition for Critical findings, minimum 2 levels for High findings. Include example attack trees in the prompt for pattern-following.
- **Contingency**: Provide a simplified attack tree format (goal → preconditions → actions) if full Schneier methodology proves inconsistent.

**Risk 2**: Mermaid syntax correctness in LLM-generated output
- **Likelihood**: Medium
- **Impact**: Low
- **Mitigation**: Include Mermaid syntax reference and common pitfalls in the agent prompt. Define strict node naming conventions to avoid syntax errors (alphanumeric IDs only, quoted labels for special characters).
- **Contingency**: Add Mermaid validation checklist to the agent prompt instructions.

**Risk 3**: Cross-cutting theme identification accuracy
- **Likelihood**: Medium
- **Impact**: Low
- **Mitigation**: Define explicit theme detection criteria in the agent prompt (component overlap, mitigation similarity, attack chain analysis). Require finding ID citations for every theme claim.
- **Contingency**: Limit cross-cutting themes to component-based grouping (most reliable heuristic) rather than semantic analysis.

**Risk 4**: Report length for large threat models
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: Define maximum section lengths in the agent prompt. For threat models with >30 findings, summarize Medium/Low findings by category rather than individual narrative.
- **Contingency**: Split report into executive summary (always concise) and detailed appendix.

### Dependencies

**Internal Dependencies**:
- **F-003 (Orchestrator)**: Delivered — provides the pipeline where Phase 5 (Report) is added
- **F-005 (STRIDE Agents)**: Delivered — produces STRIDE findings in `threats.md`
- **F-007 (AI Agents)**: Delivered — produces AI findings in `threats.md`
- **F-010 (Deduplication & Risk Rating)**: Delivered — provides correlation groups and calibrated risk levels
- **F-012 (SARIF Output)**: Delivered — co-exists in Phase 4; report agent runs after SARIF generation
- **`schemas/finding.yaml`**: Defines the finding IR that the report agent parses
- **`schemas/output.yaml`**: Defines the `threats.md` structure that the report agent consumes

**Dependency Graph**:
```
F-015 (Threat Report Agent)
  ├── Depends on: F-003 (Orchestrator) ✅ Delivered
  ├── Depends on: F-005 (STRIDE Agents) ✅ Delivered
  ├── Depends on: F-007 (AI Agents) ✅ Delivered
  ├── Depends on: F-010 (Dedup & Risk) ✅ Delivered
  ├── Depends on: F-012 (SARIF Output) ✅ Delivered
  └── Blocks: Future dashboard/visualization features
```

---

## Open Questions

- [ ] Should the report agent generate attack trees for correlated finding groups as a unified tree, or generate individual trees that reference each other? — architect — Decide in spec phase
- [ ] Should Phase 5 (Report) be opt-in or default-on in the orchestrator? — PM — Decide in spec phase
- [ ] Should the report include a risk trend section comparing against previous runs if available, or is single-run reporting sufficient for MVP? — PM — Deferred to future feature
- [ ] What is the maximum report length guideline for threat models with >50 findings? — architect — Decide in spec phase

---

## References

### Product Documentation
- Product Vision: `docs/product/01_Product_Vision/product-vision.md`
- Consumer Guide: `docs/guides/CONSUMER_GUIDE_TACHI.md` § F-007
- Research: `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md` § 7 (Attack Trees), § 8 (Risk Rating)

### Technical Documentation
- Output Schema: `schemas/output.yaml` (defines `threats.md` structure)
- Finding Schema: `schemas/finding.yaml` (finding IR)
- Orchestrator: `agents/orchestrator.md` (Phase 4 pipeline)
- Example Output: `examples/mermaid-agentic-app/threats.md` (sample threat model)
- SARIF PRD: `docs/product/02_PRD/012-sarif-output-generation-2026-03-22.md` (co-generation pattern)

### External Resources
- Schneier, B. (1999). "Attack Trees." Dr. Dobb's Journal, December 1999
- Mermaid Flowchart Syntax: mermaid.js.org
- OWASP Risk Rating Methodology: OWASP Risk Assessment Framework

---

## Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ Approved | 2026-03-23 | PRD drafted with GitHub Issue #15 stories, consumer guide F-007, and attack tree research |
| Architect | architect | 🟡 Approved with Concerns | 2026-03-23 | 1 high finding (context window pressure), 7 medium, 6 low — all resolvable in spec phase |
| Engineering Lead | team-lead | 🟡 Approved with Concerns | 2026-03-23 | 1 sprint feasible (80% confidence, 3.5-5.0h). Elevate FR-6 to P0; resolve open questions before tasks |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-23 | product-manager | Initial PRD |
