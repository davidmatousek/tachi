# Research Summary: MAESTRO Phase 2 — Cross-Layer Attack Chain Analysis

## Knowledge Base Findings

- **PAT-006/PAT-007** (Pipeline Extension Patterns): Add new pipeline stages as separate commands consuming prior-stage output. Use a dedicated schema file for the new stage; extend finding.yaml with optional fields only. Never modify upstream agents/schemas — add optional extension references.
- **KB-023** (Parser Centralization): Add new extraction logic to `scripts/tachi_parsers.py` first. Both `extract-report-data.py` and `extract-infographic-data.py` consume from it — one change point propagates to all consumers.
- **KB-021** (Taxonomy Overlay): MAESTRO is implemented as optional fields with passive downstream propagation — no agent-specific logic changes needed. 95.2% keyword-classification accuracy.
- **KB-028** (Taxonomy Renames): When taxonomy renames change keyword rules (not just labels), text substitution on existing outputs is unsafe — always re-invoke the producer skill.
- **KB-029** (Attack Trees): Delete, don't preserve dead-code fallbacks. Fail-loud pattern per ADR-022.

## Codebase Analysis

### Pipeline Phase Structure
Current orchestrator pipeline (`.claude/agents/tachi/orchestrator.md`):
- Phase 0: Baseline Detection (optional)
- Phase 1: Scope (format detection, DFD + MAESTRO classification, trust boundaries)
- Phase 2: Determine Threats (agent dispatch)
- Phase 3: Determine Countermeasures (collect, merge/dedup, coverage gate, table assembly, **correlation detection → Section 4a**)
- Phase 4: Assess (coverage matrix, risk summary, SARIF output)
- Phase 5: Report (optional, default-on; invokes threat-report.md)

**Phase 3.5 insertion point**: After Phase 3 correlation detection (orchestrator.md line 383), before Phase 4 Assess. The existing Section 4a pattern is the direct template for wiring in cross-layer chain correlation.

### MAESTRO Layer Implementation
- `schemas/finding.yaml` v1.3: `maestro_layer` field, enum of L1-L7 + "Unclassified"
- Assignment: keyword-based classification in Phase 1, inheritance to findings in Phase 3 table assembly
- Shared reference: `.claude/skills/tachi-shared/references/maestro-layers-shared.md`
- Cross-layer analysis is entirely absent — the gap this feature fills

### Attack Tree Infrastructure (Feature 112, reusable)
- `scripts/extract-report-data.py`: `parse_attack_trees()` (line 416), `render_mermaid_to_png()` (line 767) — concurrent rendering via `as_completed`
- `templates/tachi/security-report/attack-path.typ`: portrait page with severity badge, PNG image, narrative, remediation
- mmdc two-gate enforcement: shell-level `command -v mmdc` + Python-level `shutil.which("mmdc")` raise
- Gate fires only when `attack-trees/` contains Critical/High findings

### Schemas
- 9 schema files in `schemas/`: finding.yaml (v1.3), infographic.yaml (v1.0), risk-scoring.yaml, compensating-controls.yaml, etc.
- New schema files follow infographic.yaml pattern: YAML with `schema_version`, producer/consumer comment block
- Enum-value-only changes = minor bump (x.y+1); shape/required-field changes = major bump

### Examples
- 6 examples: agentic-app, ascii-web-api, free-text-microservice, mermaid-agentic-app, microservices, web-app
- mermaid-agentic-app has `attack-trees/` (13 files) and MAESTRO layers L1/L2/L3/L7
- agentic-app identified as best chain demonstration candidate (6-layer MAESTRO coverage)

### Threat Report Agent Pattern
- `.claude/agents/tachi/threat-report.md`: Section 4 (Cross-Cutting Themes) is the closest structural parallel
- Pattern: load reference file on-demand → scan findings for patterns → synthesize grouped narrative
- New Attack Chains section would follow same pattern

### Shared References
- `.claude/skills/tachi-shared/references/`: 4 files (stride-categories, maestro-layers, finding-format, severity-bands)
- Cross-layer chain patterns would need a new shared reference (`attack-chain-patterns-shared.md`) or could extend `maestro-layers-shared.md`

## Architecture Constraints

- **ADR-020** (MAESTRO Classification): Keyword-based, Phase 1 classification. Enum-value-only minor-bump rule established in Feature 136.
- **ADR-021** (Determinism): `SOURCE_DATE_EPOCH=1700000000` for test/baseline paths only. New Python extraction must produce byte-identical output for identical inputs. No LLM-based classification for structural data.
- **ADR-022** (mmdc Hard Prerequisite): Two-gate enforcement for any new Mermaid rendering. A third CLI prerequisite would trigger the `require_cli` helper refactoring threshold.
- **Output-schemas reference**: New artifacts must be declared in the validation checklist with conditional emission for backward compatibility.

## Industry Research

### CSA MAESTRO Canonical Format
- Cross-layer analysis produces **causal narratives** connecting individually acceptable findings into end-to-end compromise paths
- Chain expression format: "Input -> Retrieval bias -> Planning goal shift -> Tool invocation -> Aggregated exfiltration"
- Two propagation patterns: **vertical** (down/up the stack, e.g., L2 data poisoning -> L3 planning corruption -> L7 unauthorized action) and **horizontal/lateral** (within a layer across shared infrastructure)
- Causal language uses "enables," "shifts," "triggers," and "manifests as" to link layer transitions

### Visualization
- Mermaid flowcharts (top-down) are the dominant practitioner format for attack chains
- Mermaid sequence diagrams recommended for multi-agent interaction flows
- Attack trees remain common for single-layer goal decomposition but don't capture cross-layer propagation

### Key References
- CSA Blog: Agentic AI Threat Modeling Framework, MAESTRO (Feb 2025)
- CSA Blog: Applying MAESTRO to Real-World Agentic AI Threat Models (Feb 2026)
- CSA Blog: Threat Modeling OpenAI's Responses API with MAESTRO (Mar 2025)
- GitHub: CloudSecurityAlliance/MAESTRO
- Snyk Labs: MAESTRO, Layered Threat Modeling for Agentic AI Ecosystems

## Recommendations for Spec

- **Follow Section 4a pattern**: Cross-layer chain correlation is structurally analogous to the existing correlation detection — insert as Phase 3.5 post-dedup, pre-assess
- **New schema file**: `schemas/attack-chain.yaml` at v1.0 (chains are cross-finding aggregates, not finding-level properties — per PRD architect resolution)
- **Reuse Python rendering**: `render_mermaid_to_png()` is reusable; new Typst template needed for chain layout (vertical MAESTRO layer stack, not branching trees)
- **Conditional emission**: All new artifacts gated by `has-attack-chains` boolean for backward compatibility
- **Shared reference**: New `attack-chain-patterns-shared.md` for deterministic correlation rules
- **agentic-app as demo**: Richest MAESTRO coverage (6 layers); extend with 1-2 components for stronger cross-layer data flows
- **Causal language**: Use CSA canonical transition vocabulary ("enables/triggers/manifests as") for chain narratives
