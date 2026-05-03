# Research Summary: Threat Report Agent & Attack Trees (F-015)

**Date**: 2026-03-23
**PRD**: `docs/product/02_PRD/015-threat-report-agent-attack-trees-2026-03-23.md`

## Knowledge Base Findings

- **PAT-001 (Wave-Based Parallelism)**: Content-heavy features have high parallelism potential. F-015 outputs (narrative, attack trees, roadmap) can be parallelized by section.
- **PAT-002 (Parallel Agent Validation)**: Structure user stories around artifact subsets. The three deliverables (report, trees, roadmap) map to partially independent user stories.
- **PAT-003 (Phased Delivery)**: Per-story checkpoints provide partial value at each phase. Report generation can break into: parse → narrative → trees → roadmap.
- **PAT-004 (SARIF Mapping)**: When intermediate representation (finding IR) is well-structured, adding new output formats is straightforward prompt engineering. F-015 follows the same pattern — `threats.md` IR → `threat-report.md`.

## Codebase Analysis

### Agent Prompt Pattern
All agents follow an 8-section YAML+Markdown structure:
1. YAML frontmatter (name, description, version, changelog, boundaries)
2. Core Mission
3. Role Definition
4. When to Use
5. Workflow Steps
6. Quality Standards
7. Triad Governance
8. Success Criteria

**Reference files**: `agents/stride/spoofing.md`, `agents/orchestrator.md`, `agents/security-analyst.md`

### Finding IR Schema (`schemas/finding.yaml`)
Key fields the report agent consumes:
- `id`: `{CATEGORY}-{N}` pattern (S-1, AG-1, LLM-3)
- `category`: One of 8 values (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, agentic, llm)
- `component`, `threat`, `likelihood`, `impact`, `risk_level`, `mitigation`
- `references`: OWASP/CWE IDs (required for AI categories)
- `dfd_element_type`: DFD classification

### Output Schema (`schemas/output.yaml`)
`threats.md` has 7 required sections + 4a:
1. System Overview
2. Trust Boundaries
3. STRIDE Tables (6 category tables)
4. AI Threat Tables (2 category tables)
4a. Correlated Findings (from F-010)
5. Coverage Matrix
6. Risk Summary
7. Recommended Actions

### Example Data (`examples/mermaid-agentic-app/threats.md`)
- 19 total findings: 3 Critical, 9 High, 7 Medium
- 8 threat categories active
- 5 components analyzed
- Correlation groups present in Section 4a

### SARIF Co-Generation Pattern (F-012)
- `threats.sarif` generated alongside `threats.md` in Phase 4
- Finding IR → SARIF mapping is mechanical once IR is well-defined
- Same pattern applies: Finding IR → threat-report.md

## Architecture Constraints

- **Phase 5 context isolation** (Architect high-severity finding): Report agent MUST run in fresh LLM context with only `threats.md` as input — not accumulated orchestrator context
- **P0 orchestrator integration** (Team Lead condition): FR-6 must be P0; without it, feature is non-functional
- **Output co-location**: Phase 5 outputs go in same `YYYY-MM-DD-{phase}/` directory as `threats.md`
- **No application code**: Report agent is a prompt file, consistent with tachi architecture
- **Mermaid `flowchart TD` only**: Standard syntax, no plugins or extensions
- **Correlation group handling** (ADR-012): Respect F-010 correlation groups — discuss as units, not individually repeated

## Industry Research

### Schneier Attack Tree Methodology
- Root-to-leaf decomposition: root = attacker goal, intermediates = sub-goals (AND/OR), leaves = atomic actions
- AND gates: all children required; OR gates: any one child sufficient
- Asymmetry expected — different paths have different depths
- Multi-attribute analysis: cost, skill, time, special equipment
- Reusable subtrees across threat models

### Mermaid Attack Tree Best Practices
- Use `flowchart TD` (top-down orientation)
- AND/OR gates via explicit diamond/hexagon nodes: `{{"AND"}}`, `{{"OR"}}`
- Prefix node IDs with finding ID to prevent collisions: `AG1_root`, `AG1_leaf1`
- Always quote labels: `["Label text"]`
- Reserved words to avoid: `end`, `default`; avoid `o`/`x` as first character after edges
- Use `classDef` for reusable styling, not inline styles
- Keep trees under ~20 nodes for readability

### Executive Summary Best Practices (CISO Audience)
- Lead with business impact, not technical findings
- Five essential elements: risk posture, top threats, recommendations, compliance relevance, remediation timeline
- No unexplained jargon — define every acronym on first use
- Maximum 1-2 pages / ~500 words
- Note what IS working, not just problems

### STRIDE-GPT Lessons (Closest Existing Tool)
- LLM-generated Mermaid is a known reliability concern — STRIDE-GPT v0.4 specifically overhauled attack tree generation to "minimize syntax errors"
- Initial prompts produce shallow analysis — v0.6 updated prompts for "more comprehensive outputs"
- Cross-layer threat analysis pattern validates tachi's cross-cutting theme identification (FR-5)
- Markdown download format validates tachi's markdown-first approach

## Recommendations for Spec

- **Mandate Mermaid node ID convention**: `{FindingID}_{nodeType}{N}` (e.g., `AG1_root`, `AG1_and1`, `AG1_leaf1`)
- **Require explicit AND/OR gate nodes**: Diamond shapes with `{{"AND"}}`/`{{"OR"}}` labels — not implicit branching
- **Include Mermaid validation checklist in agent prompt**: Reserved words, quoting rules, node ID restrictions
- **Define 5-element executive summary template**: Risk posture, top threats, recommendations, compliance, timeline (~500 words max)
- **Add decomposition stopping rule**: Decompose until leaf nodes are concrete attacker actions requiring specific resources; stop before implementation-level detail
- **Resolve open questions**: Correlated findings → individual trees with cross-references (recommended); Phase 5 → default-on with skip option (precedent: SARIF)
- **Elevate FR-6 to P0**: Orchestrator integration is non-functional without it (Team Lead condition)
- **Add `schemas/report.yaml`** for output validation (Architect medium-severity finding)
