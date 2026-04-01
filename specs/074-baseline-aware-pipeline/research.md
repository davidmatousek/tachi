# Research Summary: Baseline-Aware Pipeline

## Knowledge Base Findings

- **PAT-006 & PAT-007**: Schema-driven post-pipeline enrichment. `/threat-model` → `/risk-score` → `/compensating-controls` — each stage extends via dedicated YAML schema without modifying upstream agents. Key insight: baseline awareness must follow the same enrichment-chain pattern.
- **PAT-004**: STRIDE category-to-rule mapping translates directly to SARIF `reportingDescriptor`. Finding IR makes SARIF output mapping mechanical — fingerprints already deterministic.
- **PAT-014**: LLM-based parsing produces non-deterministic output. Replaced with deterministic Python scripts (regex/pathlib, no external deps) for data extraction. Produces byte-identical output every run.
- **PAT-015**: Determinism requires explicit choices: `json.dumps(sort_keys=True)`, deterministic tie-breaking (composite desc, ID asc), stable sort algorithms.
- **No existing baseline logic** — this is entirely new capability.

## Codebase Analysis

**Skills (domain knowledge)**:
- `tachi-orchestration`: SARIF 2.1.0 generation, STRIDE-per-Element dispatch, output schema validation
- `tachi-risk-scoring`: Four-dimensional scoring (CVSS 3.1, exploitability, scalability, reachability), composite calculation, governance fields
- `tachi-control-analysis`: 8 control categories, detection patterns, evidence criteria, residual risk formulas

**Agents (orchestration)**:
- `orchestrator.md`: 5-phase threat modeling pipeline (Scope, Determine Threats, Determine Countermeasures, Assess, Report). Dispatches 6 STRIDE + 5 AI agents.
- `risk-scorer.md`: Transforms threats.md → risk-scores.md with quantitative scoring
- `control-analyzer.md`: Scans codebase for controls, calculates residual risk

**Schemas**:
- `schemas/finding.yaml`: ID pattern `^(S|T|R|I|D|E|AG|LLM)-\d+$`, required fields: id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type
- `schemas/risk-scoring.yaml`: Category-default CVSS vectors per category, composite weights (35/30/15/20), severity bands (Critical 9.0-10.0 24h, High 7.0-8.9 7d, Medium 4.0-6.9 30d, Low 0.0-3.9 90d)
- `schemas/compensating-controls.yaml`: Control status (found/partial/missing), 8 categories, reduction factors, residual score formula

**SARIF fingerprints**:
- `partialFingerprints.findingId/v1` — stable finding ID (e.g., "S-3")
- `partialFingerprints.primaryLocationLineHash` — SHA-256(ruleId|component_name) truncated to 16 hex chars
- `partialFingerprints.correlationGroup` — group identifier for correlated peers

**Output templates** (threats.md, risk-scores.md, compensating-controls.md): Well-structured with YAML frontmatter, section-based markdown tables, SARIF companions.

## Architecture Constraints

- **File-based state only** — no external database (constitutional requirement for local-first)
- **Atomic write-then-rename** for state safety (ADR-001 pattern)
- **Deterministic deduplication** — fixed rule-based matching, non-destructive, auditable (ADR-012 correlation pattern)
- **Non-fatal observability** — coverage gate failures are warnings, not blocking errors (ADR-006 pattern)
- **Backward compatibility** — first run without baseline must operate identically to current stateless behavior
- **Score bounding** — new findings bounded within +/- 1.0 of category defaults (Phase 2 only; Phase 1 inherited scores unbounded)

## Industry Research

- **SARIF Multitool baseline comparison**: Microsoft's `sarif-multi-tool` supports baselining a SARIF file against an earlier run, annotating each issue as New, Unchanged, Updated, or Absent — directly analogous to tachi's `[NEW]`, `[UNCHANGED]`, `[UPDATED]`, `[RESOLVED]` delta annotations.
- **GitLab Advanced SAST deduplication**: Uses primary identifier matching to link findings across scanner transitions — validates the approach of using SARIF fingerprints as primary correlation key.
- **Harness STO**: Normalizes results across scanners, deduplicates within and across tools — confirms industry pattern of baseline + variant categorization.
- **Fingerprint strategy best practice**: Combine multiple fingerprint strategies (content hash + location hash) for robust cross-run correlation. Normalize paths since tools report differently.
- **Industry consensus**: Baseline-aware pipelines with delta annotations are standard practice in enterprise SAST toolchains.

## Recommendations for Spec

- Follow the existing enrichment-chain pattern (PAT-006/007) — baseline awareness extends pipeline stages, doesn't replace them
- Use SARIF `partialFingerprints.findingId/v1` as primary correlation key (already deterministic)
- Use `primaryLocationLineHash` as secondary signal for matching
- Coverage checklist schema should follow the same YAML-driven approach as existing schemas
- Delta annotations align with SARIF Multitool conventions (industry-validated pattern)
- Score inheritance for unchanged findings is the most impactful stability improvement
- Isolated discovery context (no full finding text) prevents anchoring bias — validated by PRD evidence
- Coverage gate as non-blocking floor aligns with existing non-fatal observability patterns
