# Research Summary: Compensating Controls Analysis

## Knowledge Base Findings
- **PAT-006: Post-Pipeline Enrichment via Schema-Driven Scoring** — KB pattern from Feature 035 that names compensating controls as a future enrichment use case. Design as a separate command consuming existing output, use a dedicated schema, preserve source identifiers for traceability.
- **PAT-004: SARIF 2.1.0 Maps Naturally to STRIDE Threat Models** — STRIDE category-to-rule mapping and severity-to-CVSS alignment translate directly into SARIF objects. "When the IR is well-structured, adding new output formats is straightforward."
- **Feature 035 spec** references compensating controls as the next pipeline stage after risk scoring.
- No existing KB patterns for coverage matrices, control detection, or residual risk — these concepts are new to tachi.

## Codebase Analysis
- **Command pattern**: `/threat-model.md` (1,261 lines) and `/risk-score.md` (162 lines) in `.claude/commands/` — create `/compensating-controls.md` following same flag parsing and prerequisite validation pattern.
- **Agent pattern**: `tachi/orchestrator.md` (73KB, 6-phase) and `tachi/risk-scorer.md` (87KB, 6-phase pipeline) — create `tachi/compensating-controls-analyzer.md`.
- **Schemas**: `finding.yaml` (base), `risk-scoring.yaml` (scoring extension), `output.yaml` (structure) — create `compensating-controls.yaml` extending scored_finding.
- **Templates**: `templates/threats.md`, `templates/risk-scores.md`, `templates/risk-scores.sarif` — create `templates/compensating-controls.md` and `templates/compensating-controls.sarif`.
- **SARIF reference**: `adapters/claude-code/agents/references/sarif-generation.md` — 300+ lines of mapping rules; fingerprint computation uses SHA-256 of `{ruleId}|{component_name}`.
- **Examples**: `examples/agentic-app/` has 34 scored threats for validation against.

## Architecture Constraints
- **ADR-013**: SARIF 2.1.0 output format adoption — compensating-controls.sarif must extend supersession chain.
- **ADR-006**: Non-fatal observability — graceful handling of unreadable files, partial results always emitted.
- **ADR-010**: Minimal-return architecture — subagent returns essentials only.
- **ADR-002**: On-demand reference loading — agents load references when needed.
- **Context window**: ~80K token budget per analysis pass; max 200 file reads; component-based batching.
- **Severity bands**: Critical >= 9.0, High 7.0-8.9, Medium 4.0-6.9, Low < 4.0 (from `risk-scoring.yaml`).

## Industry Research
- **Residual risk formula validated**: `Residual = Inherent * (1 - Reduction Factor)` is NIST SP 800-30 aligned.
- **Three-tier effectiveness** (Strong/Moderate/Weak) matches NIST, OWASP, and GRC platforms.
- **Binary P0 factors** (0.50/0.25/0.00) are conservative and defensible per industry benchmarks.
- **Two-phase detection** recommended: fast pattern scan → targeted LLM analysis on candidates (token-efficient).
- **SARIF property bags** are the correct extensibility mechanism per SARIF 2.1.0 spec.
- **`relatedLocations`** should map control evidence to SARIF for viewer navigation.
- **STRIDE-to-control mapping** validated against NIST 800-53 control families.
- **OWASP ASVS v5.0** provides concrete effectiveness benchmarks for detection patterns.
- **Multiple controls per threat**: Use highest single effectiveness (not additive).
- **Residual score clamping**: Must clamp to [0.0, 10.0] to match scoring schema range.

## Recommendations for Spec
- Follow PAT-006 enrichment pattern: separate command consuming /risk-score output, dedicated schema, preserve findingId/v1
- Create `schemas/compensating-controls.yaml` extending scored_finding with control fields
- Define STRIDE-to-control-category canonical mapping table in agent instructions
- Use two-phase detection: pattern scan then LLM semantic analysis (maximizes 200-file budget)
- Map control evidence to SARIF `relatedLocations` for navigability
- Codify fallback heuristic directories: `middleware/`, `auth/`, `security/`, `validators/`, `guards/`, `interceptors/`, `filters/`, `policies/`, `config/`
- Hardcode reduction factors in Phase 1 (consistent with /risk-score precedent)
- Reference OWASP ASVS for effectiveness thresholds where applicable
