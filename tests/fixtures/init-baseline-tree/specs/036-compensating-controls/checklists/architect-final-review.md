# Architect Final Review: Feature 036 — Compensating Controls

**Reviewer**: Architect
**Date**: 2026-03-28
**Status**: APPROVED_WITH_CONCERNS
**Findings**: 8 total (0 High, 2 Medium, 6 Low)

---

## Review Scope

Reviewed the complete compensating controls pipeline for production readiness:

| File | Path | Lines |
|------|------|-------|
| Agent | `.claude/agents/tachi/control-analyzer.md` | ~1370 |
| Command | `.claude/commands/compensating-controls.md` | ~195 |
| Schema | `schemas/compensating-controls.yaml` | ~177 |
| MD Template | `templates/compensating-controls.md` | ~328 |
| SARIF Template | `templates/compensating-controls.sarif` | ~603 |

Reviewed against:
- `specs/036-compensating-controls/spec.md` (20 FRs, 9 SCs, 10 edge cases)
- `specs/036-compensating-controls/plan.md` (6-phase pipeline, SARIF chain, batching)

---

## Checklist Results

### 1. Does the 6-phase pipeline follow the established risk-scorer.md pattern?

**PASS**. The control-analyzer mirrors the risk-scorer's 6-phase sequential pipeline architecture:

| risk-scorer.md | control-analyzer.md |
|----------------|---------------------|
| Phase 1: Threat Parsing | Phase 1: Parse Input |
| Phase 2: Trust Zone Extraction | Phase 2: Discover Codebase |
| Phase 3: Dimensional Scoring | Phase 3: Detect Controls |
| Phase 4: Composite Calculation | Phase 4: Map & Classify |
| Phase 5: Governance Fields | Phase 5: Recommend & Calculate Residual Risk |
| Phase 6: Output Generation | Phase 6: Generate Output |

Structural conventions are preserved: metadata frontmatter, input boundary section, sequential phase headings, YAML intermediate representations, validation at each phase boundary, output declaration, and consistency verification.

### 2. Is the SARIF supersession chain properly designed?

**PASS**. The three-tier chain is correctly specified:

```
threats.sarif (static category severity)
  -> risk-scores.sarif (per-finding composite score)
    -> compensating-controls.sarif (per-finding RESIDUAL score)
```

The SARIF template correctly uses:
- `tool.driver.name: "tachi-control-analyzer"` (distinct from upstream tools)
- `security-severity` at result level reflects RESIDUAL score
- Rule-level `security-severity` reflects MAX residual score per rule
- `partialFingerprints` preservation is documented in both the agent (Phase 6c) and SARIF template comments

### 3. Are fingerprints preserved correctly through the pipeline?

**PASS**. Fingerprint handling is thorough:
- Phase 1 (Parse Input): Extracts all `partialFingerprints` from SARIF input (lines 176-180)
- Phase 1c (Finding Set): Preserves `findingId/v1`, `primaryLocationLineHash`, `correlationGroup` in IR
- Phase 6c (SARIF Output): Explicit rule that fingerprints MUST be identical to upstream (line 1272)
- SARIF template: All 5 examples include `partialFingerprints` with `findingId/v1`
- Validation step 2 (line 1300): Confirms all results have `findingId/v1`

### 4. Is the component-based batching strategy sound?

**PASS with concern** (see Finding M-1). The strategy is architecturally sound:
- Group threats by component, read component files once, scan all 8 categories
- 200-file budget with priority-based allocation
- Sub-batch splitting when component exceeds ~50K tokens
- Partial result emission on batch failure

### 5. Does the schema properly extend risk-scoring.yaml?

**PASS with concern** (see Finding M-2). The schema correctly:
- Declares `extends: scored_finding` inheriting all fields from finding.yaml + risk-scoring.yaml
- Adds 9 new fields specific to compensating controls
- Defines both P0 (binary) and P1 (effectiveness-aware) reduction factor tables
- Includes the canonical STRIDE-to-control mapping
- Specifies 8 validation rules

### 6. Are Phase 5 recommendation and residual risk calculations correct?

**PASS**. The calculations are mathematically correct:
- Formula: `residual_score = composite_score * (1 - reduction_factor)`
- Clamping: [0.0, 10.0]
- Rounding: One decimal place
- Worked examples verified: S-1=3.9, T-2=4.9, D-3=8.2, I-4=4.6
- Severity band thresholds match upstream risk-scoring.yaml
- Arithmetic verification step explicitly included (line 1069)
- Recommendations sorted by composite_score descending (highest risk first)

### 7. Is Phase 6 output generation consistent between MD and SARIF?

**PASS with concern** (see Finding M-2). Cross-format consistency verification is well designed (section 6d, lines 1311-1320). Four consistency checks: finding count, control status, residual score, fingerprint correspondence.

### 8. Are error handling and graceful degradation properly specified?

**PASS**. All 10 spec edge cases are addressed:

| Spec Edge Case | Coverage |
|----------------|----------|
| No risk score input | Command Step 1.2 + Agent Phase 1d halt |
| Target inaccessible | Command Step 1.4 halt |
| Partial analysis failures | Agent Phase 3f partial result emission |
| Empty target codebase | Agent Phase 2e unmapped component warning |
| Architecture input missing | Command Step 1.6 + Agent Phase 2b heuristic fallback |
| File read budget exceeded | Agent Phase 2c budget enforcement |
| Context window overflow | Agent Phase 3f sub-batch splitting |
| Multiple controls per threat | Agent Phase 4c multi-control resolution |
| Zero threats in input | Agent Phase 1d count check halt |
| Malformed risk score input | Agent Phase 1e malformed row handling |

Each error path includes a specific, user-facing diagnostic message.

### 9. Does the command properly validate prerequisites and handle flags?

**PASS**. The command correctly:
- Parses `--target`, `--output-dir`, and positional arguments (Step 0)
- Validates agent installation (Step 1.1)
- Validates risk score input with canonical/fallback ordering (Step 1.2-1.3)
- Validates target codebase existence (Step 1.4)
- Resolves output directory with create-if-missing (Step 1.5)
- Discovers optional architecture.md (Step 1.6)
- Reports comprehensive summary with next steps (Step 3)

### 10. Is the knowledge system pattern followed correctly?

**PASS**. The implementation contains zero application code:
- Agent: Markdown instructions only, no executable code
- Command: Markdown orchestration steps, no scripts
- Schema: YAML data model, not executable
- Templates: Structural scaffolds with placeholders
- All follow the exact pattern from `/risk-score` (Issue #35)

---

## Findings

### Medium Severity

#### M-1: SARIF Template P0/P1 Effectiveness Inconsistency

**File**: `templates/compensating-controls.sarif`
**Lines**: 514, 593

The agent (line 1280) explicitly defines P0 effectiveness as a deterministic mapping:
- `found` -> `"strong"`
- `partial` -> `"moderate"`
- `missing` -> `"none"`

However, the SARIF template examples are inconsistent with this P0 rule:
- Example 4 (line 514): control-status is `"found"` but control-effectiveness is `"moderate"` (P0 expects `"strong"`)
- Example 5 (line 593): control-status is `"partial"` but control-effectiveness is `"weak"` (P0 expects `"moderate"`)

Examples 1-3 correctly demonstrate P0 behavior. Examples 4-5 prematurely use P1 effectiveness values that would only be valid when User Story 6 (effectiveness assessment) is active.

**Impact**: When an LLM generates output using this template as a reference, it may produce inconsistent effectiveness values — sometimes using P0 deterministic mapping, sometimes using P1-style values. This directly undermines the cross-format consistency guarantee (Section 6d).

**Recommendation**: Fix Examples 4 and 5 to use P0-correct values, or add explicit `_comment` fields on each clarifying that Examples 4-5 illustrate P1 behavior and should be ignored until P1 is active.

#### M-2: Schema Producer Reference Points to Non-Existent File

**File**: `schemas/compensating-controls.yaml`
**Line**: 7

The schema's `Producers` comment references `agents/tachi/compensating-controls-scanner.md`, but the actual agent file is `agents/tachi/control-analyzer.md`. No file named `compensating-controls-scanner.md` exists in the repository.

**Impact**: Any consumer or maintainer following the producer reference to understand data flow will land on a non-existent file. Low functional impact (does not affect runtime behavior), but a documentation correctness issue that breaks the producer-consumer chain traceability established by `finding.yaml` and `risk-scoring.yaml`.

**Recommendation**: Change line 7 from `agents/tachi/compensating-controls-scanner.md` to `agents/tachi/control-analyzer.md`.

### Low Severity

#### L-1: relatedLocations Dual-Purpose Convention Needs Stronger Disambiguation

**File**: `templates/compensating-controls.sarif`, Example 5 (line 522)

The SARIF template uses `relatedLocations` for two purposes: control evidence (via `physicalLocation`) and correlated peer references (via `logicalLocations`). While comments explain the convention, the disambiguation relies on consumers checking whether each entry has `physicalLocation` vs `logicalLocations`.

The agent (lines 1258-1264) documents the evidence purpose but mentions correlated peers only in passing (line 1264). The two-purpose usage pattern is not reinforced in the schema.

**Impact**: Low. The SARIF spec allows flexible use of `relatedLocations`, and the comment-based convention is sufficient for template-guided generation. However, downstream SARIF consumers (e.g., GitHub Code Scanning viewers, custom dashboards) may not distinguish between the two entry types without the convention documented in their parsers.

**Recommendation**: No blocking change needed. Consider adding a `_type` property within the `relatedLocations` message text (e.g., prefix with `[evidence]` or `[correlation]`) for programmatic disambiguation in P2.

#### L-2: Sub-Batch Splitting Heuristic Remains Underspecified

**File**: `.claude/agents/tachi/control-analyzer.md`, Phase 3f (line 756)

The sub-batch splitting strategy says to "split by file priority" when a component exceeds ~50K tokens, but does not specify the exact token estimation method for file content or the splitting threshold precision. The plan.md architect review (medium concern) flagged this, and the implementation improved it with priority-based splitting and merge rules, but the token estimation is still described as approximate (`~50K tokens after truncation`).

**Impact**: Low. In practice, LLM agents estimate token counts heuristically (roughly 4 chars per token) and the approximate threshold is adequate for the P0 scope of <= 200 threats. Edge cases with very large components may produce inconsistent splitting behavior.

**Recommendation**: No blocking change needed. Document the token estimation heuristic (e.g., "approximately 4 characters per token") in a future refinement pass.

#### L-3: Coverage Percentage Rounding Adjustment May Produce Surprising Results

**File**: `.claude/agents/tachi/control-analyzer.md`, Phase 6a (lines 1126-1127)

The specification rounds each percentage independently, then adjusts by adding/subtracting 1% from the largest category if the total does not sum to 100%. For small finding counts (e.g., 3 threats: 1 found, 1 partial, 1 missing = 33.3% each), this results in one category showing 34% and two showing 33%. The adjustment is mathematically correct but the "largest category" tiebreaker is not defined when two or more categories have the same count.

**Impact**: Low. Purely cosmetic. The executive summary percentages may differ by 1% between runs if the tiebreaker resolves differently.

**Recommendation**: Add a tiebreaker: "When multiple categories share the largest count, apply the +1% adjustment to the first in this order: found, partial, missing."

#### L-4: Command Does Not Validate `--output-dir` Write Permission

**File**: `.claude/commands/compensating-controls.md`, Step 1.5 (line 79)

The command creates the output directory if it does not exist, but does not explicitly verify write permission. The agent (Phase 6, line 72) halts if the output directory does not exist but also does not check writability.

**Impact**: Low. In practice, LLM agents operating via Claude Code have the same filesystem permissions as the user. A non-writable directory will produce a file-write error at output time, which is a late-stage failure after all analysis work is complete.

**Recommendation**: No blocking change needed. Consider adding a write-permission check in the command's Step 1.5, or document that write failures at output time will lose the analysis results (suggesting `--output-dir` to a known-writable location).

#### L-5: Markdown Template Includes P1 Effectiveness Dimension Table

**File**: `templates/compensating-controls.md`, Section 3 (lines 130-136)

The markdown template includes a full effectiveness assessment dimension table (Coverage, Configuration, Currency, Completeness) in the control details section. The agent correctly instructs to replace this with a P1 placeholder note in P0 (line 1181), but the template itself does not mark these rows as P1-conditional. A template consumer not reading the agent's P0 instructions might populate the dimension table in P0 output.

**Impact**: Low. The agent's P0 instructions are clear, and the template is consumed exclusively through the agent. But the template alone does not self-document which sections are P0 vs P1.

**Recommendation**: Add a template comment above the dimension table: `<!-- P1 ONLY: Omit this table in P0. Replace with: "Detailed effectiveness assessment available in P1 (User Story 6)." -->`

#### L-6: Recommendation Field for "found" Threats Uses Inconsistent Null/Empty Convention

**Files**: Agent (line 1283) vs SARIF template (lines 347, 514)

The agent specifies that `recommendation` and `effort-estimate` should be null for `found` threats (line 875, 1283-1284). However, the SARIF template examples use empty strings `""` for these fields on `found` results (lines 347, 514). The schema allows `nullable: true` (lines 80-81, 88-89).

Null and empty string are semantically different: null means "not applicable" while empty string means "applicable but blank." For JSON/SARIF, empty string is the safer choice since JSON null can cause parsing issues in some SARIF consumers. The convention is consistent within the SARIF template but inconsistent between the agent's text description and the template's JSON examples.

**Impact**: Low. Both conventions work in practice. The LLM will follow the template examples (empty string) during SARIF generation and the agent instructions (null) during markdown generation, which is acceptable since markdown renders both the same way.

**Recommendation**: Harmonize by updating the agent's prose to say `empty string ""` instead of `null` for SARIF properties, matching the template examples.

---

## Plan.md Prior Concerns Resolution

The plan.md architect sign-off noted 3 Medium and 4 Low concerns. Assessing resolution:

| Prior Concern | Status |
|---------------|--------|
| M: relatedLocations dual-purpose ambiguity | Partially addressed — template Example 5 adds comments, but convention still relies on implicit type detection (see L-1) |
| M: Sub-batch splitting heuristic underspecified | Partially addressed — priority-based splitting added, but token estimation remains approximate (see L-2) |
| M: Cross-component control sharing unaddressed | Addressed — Phase 4d explicitly handles global/cross-component controls with conservative classification |

---

## Architecture Assessment

### Strengths

1. **Pipeline consistency**: The 6-phase architecture mirrors risk-scorer.md precisely, maintaining the established pattern for pipeline tools.

2. **Two-phase detection**: The Phase A (pattern) + Phase B (semantic) detection strategy is a sound approach. Pattern scanning is cheap and fast; semantic analysis provides accuracy. This avoids the monolithic approach of trying to do both simultaneously.

3. **Exhaustive validation gates**: Every phase boundary includes completeness checks and halt conditions with diagnostic messages. The Phase 6d cross-format consistency verification is particularly well designed.

4. **SARIF chain integrity**: Fingerprint preservation is documented at every pipeline stage, and the supersession semantics are clearly defined.

5. **Graceful degradation**: Partial result emission, per-component failure isolation, and the 200-file budget with priority allocation are production-quality patterns.

6. **Schema design**: The `controlled_finding` entity cleanly extends `scored_finding`, preserving the entity hierarchy. Both P0 and P1 reduction factor tables are pre-specified, enabling smooth upgrade.

7. **Lazy context loading**: Reference files are loaded on demand per phase, following the knowledge system convention and avoiding the eager-loading anti-pattern.

### Risks

1. **LLM consistency**: The detection accuracy depends on the LLM's ability to correctly apply the Phase A/B pattern-semantic analysis. The 8-category detection pattern library is comprehensive but cannot guarantee reproducible results across LLM versions or context sizes. The 75% accuracy target (SC-002) is reasonable for P0.

2. **Template-agent drift**: The SARIF template Examples 4-5 already show P0/P1 drift (Finding M-1). As P1 features are added, maintaining consistency between the template examples and agent instructions will require coordinated updates.

---

## Verdict

**APPROVED_WITH_CONCERNS**

The compensating controls pipeline is architecturally sound, follows the established risk-scorer pattern, correctly implements the SARIF supersession chain, and provides thorough error handling and validation. The 2 Medium findings (SARIF template effectiveness inconsistency and schema producer reference) should be fixed before delivery but do not block the architecture. The 6 Low findings are refinement items that can be addressed during or after delivery.

All 20 FRs from the spec are traceable to implementation, all 10 edge cases are handled, and the knowledge system pattern is correctly followed.
