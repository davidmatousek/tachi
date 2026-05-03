# Research Summary: Project Skeleton & Interface Contract

## Knowledge Base Findings
- Institutional knowledge base (`docs/INSTITUTIONAL_KNOWLEDGE.md`) has zero entries — this is the first feature
- No `.kb/` or `knowledge/` directories exist
- Architecture patterns in `docs/architecture/03_patterns/README.md` cover AOD Kit operational patterns only (atomic file write, function library sourcing, template variable expansion) — none relate to project skeleton or interface contracts

## Codebase Analysis
- **Existing directories with READMEs**: `agents/`, `adapters/`, `templates/`, `examples/`, `docs/`
- **Existing scaffold files**:
  - `agents/VoiceProfile.md`, `agents/StyleGuide.md` (scaffold templates, not yet populated)
  - `agents/MasterContent/README.md`, `agents/Narratives/README.md`
  - `agents/stride/README.md`, `agents/ai/README.md`
  - `adapters/ContextLoading.yaml` (paths reference `_Global/` — needs correction to `agents/`)
  - `adapters/ProjectMeta.yaml` (scaffold template — needs tachi metadata)
  - `adapters/ScoringRubric.md` (scaffold template — needs OWASP 3x3 dimensions)
  - `adapters/Presets/README.md`, `adapters/Terms/README.md`
  - `templates/README.md`, `examples/README.md`
- **Missing (F-001 deliverables)**: `docs/INTERFACE-CONTRACT.md`, `templates/threats.md`, `schemas/` directory, `LICENSE`, example inputs
- **Naming conventions**: PascalCase for content directories/config files, kebab-case for agent/command/narrative files

## Architecture Constraints
- **Hub-and-spoke model**: `agents/` (hub, immutable) → `adapters/` (config) → `templates/` (format) → `examples/` (output)
- **Two-level architecture**: Build-time (AOD lifecycle) vs. run-time (product commands)
- **Content-as-data**: Master content never modified per-output; adaptations through presets and parameters
- **Lazy context loading**: `ContextLoading.yaml` defines per-phase content needs
- **Path corrections needed (FR-6)**: 7 paths in ContextLoading.yaml reference scaffold defaults (`_Global/`, `_Config/`, `_Templates/`)

## Industry Research
- **STRIDE methodology**: Microsoft (1999), stable and well-established. STRIDE-per-Element variant (MSDN 2006) maps threats to DFD element types
- **OWASP Risk Rating**: 3x3 likelihood × impact matrix producing 5 risk levels (Critical/High/Medium/Low/Note)
- **OWASP LLM Top 10 v2025**: Published, stable reference for LLM-specific threats
- **OWASP Agentic Top 10 (2026 draft)**: Early stage, may evolve — mitigated by schema versioning
- **OWASP MCP Top 10 v0.1 Beta**: Early draft — risk of significant changes
- **SARIF 2.1.0**: Standard for static analysis results; risk levels map to SARIF severity scores

## Recommendations for Spec
- Organize user stories around the three core deliverables: repository structure, interface contract, output template
- Include the schemas/ directory and IR schema as a fourth deliverable (critical for downstream F-002+)
- Ensure all cross-references between files resolve to actual paths
- Document the 5-agent-to-2-table mapping (AG/LLM) explicitly in acceptance criteria
- Use schema_version: "1.0" from day one for forward compatibility
- Keep spec technology-agnostic (markdown + YAML, no runtime)
- Flag LICENSE choice (Apache 2.0 vs MIT) and classification default as open questions from PRD
