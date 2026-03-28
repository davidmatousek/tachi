# Pipeline Validation Checklist (T017)

**Feature**: 036 - Compensating Controls
**Date**: 2026-03-28
**Validator**: BDD Testing Agent
**Scope**: Validate all prerequisites for `/compensating-controls` pipeline execution against `examples/agentic-app/sample-report/` with `--target examples/agentic-app/`

---

## 1. Agent Exists

**File**: `.claude/agents/tachi/control-analyzer.md`

- [x] **PASS** -- File exists (1073+ lines)
- [x] **PASS** -- Phase 1: Parse Input (line 94)
- [x] **PASS** -- Phase 2: Discover Codebase (line 229)
- [x] **PASS** -- Phase 3: Detect Controls (line 335)
- [x] **PASS** -- Phase 4: Map & Classify (line 769)
- [x] **PASS** -- Phase 5: Recommend & Calculate Residual Risk (line 869)
- [x] **PASS** -- Phase 6: Generate Output (line 1073)
- [x] **PASS** -- All 6 phases present and sequentially numbered

**Metadata verified**: `name: tachi-control-analyzer`, `version: "1.0"`, `status: active`, `category: security-analysis`. References `schemas/compensating-controls.yaml`, `templates/compensating-controls.md`, and `templates/compensating-controls.sarif`.

---

## 2. Command Exists

**File**: `.claude/commands/compensating-controls.md`

- [x] **PASS** -- File exists (196 lines)
- [x] **PASS** -- Step 0: Parse Flags (line 13) -- handles `--target` and `--output-dir` flags
- [x] **PASS** -- Step 1: Validate Prerequisites (line 38) -- checks agent install, risk score input, target codebase, output directory, optional architecture.md
- [x] **PASS** -- Step 2: Run Control Analysis (line 89) -- invokes `tachi-control-analyzer` agent with all 6 phases
- [x] **PASS** -- Step 3: Report Results (line 125) -- displays coverage, risk reduction, residual severity distribution, next steps
- [x] **PASS** -- All 3 operational steps present (plus Step 0 flag parsing)
- [x] **PASS** -- Usage example includes exact invocation: `/compensating-controls --target examples/agentic-app/ examples/agentic-app/sample-report/`

---

## 3. Input Exists

**Directory**: `examples/agentic-app/sample-report/`

- [x] **PASS** -- `risk-scores.md` exists (canonical input, scored 2026-03-27)
- [x] **PASS** -- `risk-scores.sarif` exists (fallback input, 69,657 bytes)

Both input formats are available. Per command logic, `risk-scores.md` is canonical and will be used.

---

## 4. Target Codebase Exists

**Directory**: `examples/agentic-app/`

- [x] **PASS** -- Directory exists
- [x] **PASS** -- Contains analyzable files: `architecture.md`, `threats.md`
- [x] **PASS** -- `architecture.md` exists (3,104 bytes) -- enables architecture-aware component-to-file mapping (Step 1, item 6 of command)

**Note**: The target codebase is a sample/example directory containing architecture and threat model documentation rather than application source code. The control-analyzer agent will use heuristic discovery and architecture-based mapping to scan for controls. For a documentation-only target, the agent is expected to classify most threats as "No Control Found" since there are no code files implementing security controls.

---

## 5. Templates Exist

**Directory**: `templates/`

- [x] **PASS** -- `templates/compensating-controls.md` exists (326 lines) -- contains all 6 sections: Executive Summary, Coverage Matrix, Control Details, Recommendations, Residual Risk Summary, Methodology
- [x] **PASS** -- `templates/compensating-controls.sarif` exists (603 lines) -- SARIF 2.1.0 template with 8 rule definitions (6 STRIDE + 2 AI), 5 example result patterns (found, partial, missing, AI agentic, correlated group), supersession chain documentation

---

## 6. Schema Exists

**File**: `schemas/compensating-controls.yaml`

- [x] **PASS** -- File exists (177 lines), `schema_version: "1.0"`
- [x] **PASS** -- Defines `controlled_finding` extending `scored_finding`
- [x] **PASS** -- Contains all required fields: `control_status`, `control_evidence`, `control_category`, `control_effectiveness`, `reduction_factor`, `residual_score`, `residual_severity_band`, `recommendation`, `effort_estimate`
- [x] **PASS** -- Includes P0 reduction factors (found=0.50, partial=0.25, missing=0.00)
- [x] **PASS** -- Includes P1 effectiveness-aware reduction factors (7-level table)
- [x] **PASS** -- Includes STRIDE-to-control category mapping (8 STRIDE categories mapped)
- [x] **PASS** -- Includes severity band thresholds aligned with risk-scoring.yaml

---

## 7. Threat Count in Input

**Source**: `examples/agentic-app/sample-report/risk-scores.md`, Section 2 (Scored Threat Table)

- [x] **PASS** -- **34 scored threats found** (matches spec expectation of ~34)

**Severity distribution** (from Executive Summary):

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 0 | 0.0% |
| High | 10 | 29.4% |
| Medium | 24 | 70.6% |
| Low | 0 | 0.0% |
| **Total** | **34** | **100%** |

**Threat ID breakdown** (34 unique IDs in Scored Threat Table, lines 53-86):
- S-1 through S-4 (4 Spoofing)
- T-1 through T-5 (5 Tampering)
- R-1 through R-5 (5 Repudiation)
- I-1 through I-5 (5 Information Disclosure)
- D-1 through D-5 (5 Denial of Service)
- E-1 through E-3 (3 Elevation of Privilege)
- AG-1 through AG-4 (4 Agentic Threats)
- LLM-1 through LLM-3 (3 LLM Threats)

**Correlation groups preserved**: CG-1 (T-4/LLM-2), CG-2 (E-2/AG-1), CG-3 (R-3/AG-2), CG-4 (D-3/AG-4)

---

## Summary

| Check | Status | Details |
|-------|--------|---------|
| 1. Agent exists (6 phases) | **PASS** | All 6 phases present at expected line numbers |
| 2. Command exists (3 steps) | **PASS** | Steps 0-3 present with flag parsing, validation, analysis, reporting |
| 3. Input exists | **PASS** | Both risk-scores.md (canonical) and risk-scores.sarif (fallback) present |
| 4. Target codebase exists | **PASS** | Directory exists with architecture.md for component mapping |
| 5. Templates exist | **PASS** | Both compensating-controls.md and compensating-controls.sarif templates present |
| 6. Schema exists | **PASS** | compensating-controls.yaml with controlled_finding schema, reduction factors, STRIDE mapping |
| 7. Threat count | **PASS** | 34 scored threats (10 High, 24 Medium, 0 Critical, 0 Low) |

**Overall**: **7/7 PASS** -- All prerequisites for `/compensating-controls` pipeline execution are in place.

**Expected output files** (when pipeline runs):
- `examples/agentic-app/sample-report/compensating-controls.md`
- `examples/agentic-app/sample-report/compensating-controls.sarif`
