# Research Summary: Infographic Tiered Pipeline Auto-Detection & Residual Risk

## Knowledge Base Findings

- **PRD-039 (Standalone /infographic)**: Delivered. Provides the command, auto-detection framework (risk-scores.md > threats.md), template selection (`--template`), and explicit file override. Open Question #1 deferred compensating-controls visualization — PRD-048 answers it.
- **PRD-036 (Compensating Controls)**: Delivered. Provides `compensating-controls.md` output with residual risk fields (residual_score, residual_severity_band, reduction_factor, control_status). Coverage Matrix uses 4 sub-tables grouped by residual severity band.
- **PRD-035 (Risk Scoring)**: Delivered. Provides `risk-scores.md` with composite scores (0-10 scale), 4-dimensional scoring (CVSS, exploitability, scalability, reachability).
- **PRD-018 (Threat Infographic Agent)**: Delivered. Provides the visualization agent and both templates (baseball-card, system-architecture).
- **Detection/extraction failure distinction**: PRD-048 architect sign-off confirmed: detection-level failures fall through to next tier (graceful); extraction-level failures halt with warning (prevent misrepresentation).

## Codebase Analysis

### Key Files
- **Command**: `.claude/commands/infographic.md` — Entry point with current 2-tier auto-detection (risk-scores > threats), `--template` flag, `--output-dir` flag, explicit path override
- **Agent**: `.claude/agents/tachi/threat-infographic.md` — Data extraction logic with dual-path (risk-scores quantitative vs. threats qualitative), co-location enforcement, 6-section spec output
- **Templates**: `.claude/agents/tachi/templates/infographic-baseball-card.md` (dark dashboard, donut + heat map + finding cards) and `infographic-system-architecture.md` (white theme, trust zone layout)
- **Schema**: `schemas/compensating-controls.yaml` — Extends scored_finding with control_status, reduction_factor, residual_score, residual_severity_band
- **Schema**: `schemas/infographic.yaml` — 6 required sections, YAML frontmatter, count accuracy invariant

### Current Auto-Detection Logic (infographic.md)
1. Scan for `risk-scores.md` → detect by `## 2. Scored Threat Table` + `Composite` column
2. Scan for `threats.md` → detect by `## 6. Risk Summary` + severity labels
3. Content-based type detection (not filename-based) when explicit path provided
4. Co-located `threats.md` required when risk-scores is primary (metadata + spatial data)

### Extension Points
- Detection hierarchy: Insert compensating-controls.md as new Tier 1 before risk-scores.md
- Detection marker: `## 2. Coverage Matrix` header + `Residual Score` column
- Data extraction: Iterate 4 sub-tables (Critical/High/Medium/Low) in Coverage Matrix
- Co-location: Require `threats.md` (same pattern as risk-scores); `risk-scores.md` NOT required (residual scores are self-contained)
- Templates: Same structural layout, different data values and labels

### Compensating Controls Coverage Matrix Structure
- 4 sub-tables grouped by residual severity band (Critical, High, Medium, Low)
- Columns: Threat ID, Component, Threat, Inherent Score, Inherent Severity, Control Status, Residual Score, Residual Severity
- Summary section with aggregate risk reduction percentage

## Architecture Constraints

- **ADR-010 (Fresh Context Isolation)**: Infographic agent runs in isolated context — only data source files passed as input. All needed data must come from the file(s).
- **ADR-014 (Spec-First / Gemini Optional)**: Markdown spec is always generated; image generation via Gemini is best-effort with 6 graceful degradation conditions.
- **ADR-016 (Infographic Decoupling)**: Standalone command pattern with auto-detection hierarchy. No post-pipeline hints from `/threat-model`.
- **Schema versioning**: Output schemas at 1.0 — adding optional `source_type` field does not require version bump.
- **No breaking changes**: All existing `/infographic` invocations must continue to work identically.
- **Pipeline dependency chain**: `/threat-model` → `/risk-score` → `/compensating-controls` → `/infographic`

## Industry Research

### Tiered Detection (Prettier/ESLint pattern)
- Fixed precedence order, first match wins, deterministic and documented
- Each tier produces complete valid output at its richness level (graceful degradation)
- Content-based type detection alongside filename detection

### Residual Risk Visualization (Hyperproof, Aryza, Safe Security)
- Dual-assessment heat maps: inherent as baseline, residual as primary display
- Explicit labeling of risk type is mandatory (title-level, not footnote)
- Control effectiveness communicated as delta between inherent and residual
- Consistent color coding across tiers (same severity band colors)

### Progressive Enhancement (Nielsen Norman Group, gh CLI)
- Single-line contextual hints after output (not blocking)
- Suppressed on explicit user intent (explicit path = no tip)
- Never more than one level of progressive disclosure at a time

## Recommendations for Spec

- Extend the 2-tier detection to 3-tier: compensating-controls.md > risk-scores.md > threats.md
- Detection markers must be content-based (headers + columns), not filename-based
- Require co-located `threats.md` when compensating-controls.md is primary (same pattern as risk-scores)
- Do NOT require co-located `risk-scores.md` (residual scores are self-contained)
- Both templates (baseball-card, system-architecture) adapt data values and labels, not structural layout
- Enhancement tips: single-line, after detection, suppressed on explicit path
- Risk labels: "Residual Risk" / "Inherent Risk" / "Severity" depending on source
- Handle 4 sub-tables in Coverage Matrix extraction (not a flat table)
- Distinguish detection-level failures (graceful fallthrough) from extraction-level failures (halt with warning)
- No new templates — structural layout unchanged, only data and labels change
