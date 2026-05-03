# Code Review — Feature 024: Example Threat Models

**Reviewer**: code-reviewer
**Date**: 2026-03-23
**Branch**: `024-example-threat-models`
**Verdict**: APPROVED_WITH_CONCERNS

---

## Scope

Reviewed all files created/modified for Feature 024. This is a content-only feature where all deliverables are Markdown files. Review covers naming conventions, content consistency, internal references, schema compliance, markdown quality, and STRIDE-per-Element correctness.

### Files Reviewed

**New files (8):**
- `examples/web-app/architecture.md`
- `examples/web-app/threats.md`
- `examples/agentic-app/architecture.md`
- `examples/agentic-app/threats.md`
- `examples/microservices/architecture.md`
- `examples/microservices/threats.md`
- `examples/README.md` (rewritten)
- `docs/product/02_PRD/024-example-threat-models-2026-03-23.md`

**Modified files (2):**
- `README.md` (project root)
- `docs/product/02_PRD/INDEX.md`

---

## Findings

### CRITICAL

None.

### WARNING

#### W-1: Risk Summary count error in web-app/threats.md

**File**: `examples/web-app/threats.md`, line 203
**Issue**: The Risk Summary table reports Medium = 7 (43.8%), but manual count of all findings across STRIDE tables yields 8 Medium findings (S-3, T-1, T-2, R-1, R-2, I-3, D-2, E-2). The Recommended Actions table on lines 223-230 also lists 8 Medium findings, confirming the inconsistency. The current summary totals 2+5+7+1 = 15, but total findings is 16.
**Impact**: A consumer relying on the Risk Summary for a dashboard or report integration would get incorrect counts. The Recommended Actions table (Section 7) is correct, so the discrepancy is visible to anyone comparing sections.
**Fix**: Change line 203 from `| Medium | 7 | 43.8% |` to `| Medium | 8 | 50.0% |`. Adjust High percentage from 31.3% to 31.3% (unchanged), Low from 6.3% to 6.3% (unchanged), Critical from 12.5% to 12.5% (unchanged). Verify total line remains 16 / 100%.

Correct Risk Summary table:
```
| Critical | 2 | 12.5% |
| High | 5 | 31.3% |
| Medium | 8 | 50.0% |
| Low | 1 | 6.3% |
| Note | 0 | 0.0% |
| **Total** | **16** | **100%** |
```

Note: percentages sum to 100.1% due to rounding of individual values (2/16=12.5, 5/16=31.25, 8/16=50.0, 1/16=6.25). This is standard rounding behavior and acceptable.

#### W-2: Inconsistent Risk Summary presentation across examples

**File**: `examples/microservices/threats.md`, lines 222-231 vs `examples/web-app/threats.md`, lines 189-206 and `examples/agentic-app/threats.md`, lines 202-221
**Issue**: The Risk Summary section uses different formatting across the three examples:
- **web-app**: Uses `### Risk Calibration Matrix` subsection header with descriptive paragraph
- **agentic-app**: Uses `### Risk Calibration Matrix` subsection header with descriptive paragraph plus deduplication note
- **microservices**: Uses bold text `**OWASP 3x3 risk matrix reference:**` instead of a subsection header

All three present the same risk matrix, but the microservices version lacks the subsection header used by the other two. This is a structural inconsistency that breaks the otherwise uniform section pattern.
**Impact**: Minor presentation inconsistency. A consumer parsing section headers programmatically would find different structures across examples.
**Fix**: In `examples/microservices/threats.md`, replace the bold text line at line 224 with the same subsection header pattern used in the other two files:
```
### Risk Calibration Matrix

The following OWASP 3x3 risk matrix documents how risk levels are computed for every finding in this threat model. Impact (rows) and Likelihood (columns) determine the Risk Level at each intersection. All agents use this same matrix, ensuring consistent risk ratings across STRIDE and AI threat categories.
```

---

### SUGGESTION

#### S-1: Coverage Matrix legend inconsistency

**File**: `examples/web-app/threats.md` (Section 5, line 173) and `examples/agentic-app/threats.md` (Section 5, line 177) vs `examples/microservices/threats.md` (Section 5, line 198)
**Issue**: The microservices example includes a detailed cell legend explaining the three-state model (integer, em dash, n/a) below the coverage matrix at lines 214-218. The agentic-app example includes a similar legend as a preamble above the matrix at lines 179-183. The web-app example has no legend at all.
**Impact**: Minor usability inconsistency. Readers of the web-app example must infer cell meaning from context.
**Fix**: Add the three-state model legend to the web-app coverage matrix section, either as a preamble (matching agentic-app style) or as a footer (matching microservices style). Choose one style and apply consistently across all three.

#### S-2: STRIDE category descriptions present only in web-app example

**File**: `examples/web-app/threats.md` vs `examples/agentic-app/threats.md` and `examples/microservices/threats.md`
**Issue**: All three examples include brief category descriptions below each STRIDE subsection header (e.g., "Threats where an attacker pretends to be something or someone else" under 3.1 Spoofing). This is consistent across all three -- good. No action needed. This item is withdrawn upon verification.

#### S-3: OWASP cross-reference format variation

**File**: `examples/web-app/threats.md` (Appendix) vs `examples/microservices/threats.md` (Appendix)
**Issue**: The web-app appendix uses OWASP categories formatted as `A07:2025` with year suffix. The microservices appendix also uses `A07:2025` with year suffix. The agentic-app uses `A07` without year suffix for the Finding-to-Category table, but includes `ASI03` and `MCP10` for AI categories. The agentic-app OWASP cross-reference is less specific on the web OWASP category identifiers (no `:2025` suffix).
**Impact**: Minor. Both formats are readable and unambiguous since the framework version is stated in the appendix introduction.
**Fix**: For full consistency, add the `:2025` suffix to the agentic-app web OWASP categories (e.g., change `A07` to `A07:2025`).

#### S-4: Microservices OWASP coverage summary adds value

**File**: `examples/microservices/threats.md`, lines 305-316
**Issue**: The microservices example includes an OWASP coverage summary table at the end of the appendix showing finding count per OWASP category plus a coverage statistic ("8 of 10 categories referenced"). The other two examples lack this summary. This is actually a quality enhancement in the microservices example.
**Impact**: None negative. The summary is useful but its absence in other examples creates a minor inconsistency.
**Fix**: Consider adding the same coverage summary to web-app and agentic-app appendices for full parity.

---

## Verification Checklist

### 1. Naming Conventions
- [x] Directory names use kebab-case: `web-app/`, `agentic-app/`, `microservices/`
- [x] File names use kebab-case: `architecture.md`, `threats.md`
- [x] Existing test fixture directories retained: `ascii-web-api/`, `free-text-microservice/`, `mermaid-agentic-app/`

### 2. Content Consistency
- [x] All three `threats.md` files follow the same 7+1 section structure (1-7 plus 4a)
- [x] All three include YAML frontmatter with `schema_version: "1.1"`
- [x] All three use the same STRIDE subsection pattern (3.1-3.6)
- [x] All three include OWASP cross-reference appendix
- [x] AI sections correctly empty for web-app and microservices
- [x] AI sections correctly populated for agentic-app (AG and LLM)
- [x] Correlated findings present in agentic-app (CG-1, CG-2), correctly absent in others
- [ ] Risk Summary counts consistent with STRIDE table findings (FAIL: web-app Medium count is 7, should be 8)

### 3. Internal References
- [x] `examples/README.md` links to all three example directories with correct relative paths
- [x] `examples/README.md` links to all three legacy test fixture directories
- [x] Project `README.md` links to `examples/` with brief description
- [x] All referenced files exist on disk (verified programmatically)
- [x] `docs/product/02_PRD/INDEX.md` references Feature 024 PRD

### 4. Schema Compliance (v1.1)
- [x] Frontmatter: `schema_version`, `date`, `input_format`, `classification` present in all three
- [x] Section 1 (System Overview): Components, Data Flows, Technologies tables present
- [x] Section 2 (Trust Boundaries): Trust Zones and Boundary Crossings tables present
- [x] Section 3 (STRIDE Tables): All 6 categories with standard table columns (ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation)
- [x] Section 4 (AI Threat Tables): AG and LLM subsections with standard columns (adds OWASP Reference column)
- [x] Section 4a (Correlated Findings): Present in all three; populated in agentic-app, empty in others
- [x] Section 5 (Coverage Matrix): Three-state model (integer, dash, n/a) correctly applied
- [x] Section 6 (Risk Summary): Risk calibration matrix and count table present
- [x] Section 7 (Recommended Actions): All findings sorted by risk level descending

### 5. STRIDE-per-Element Dispatch Rules
- [x] External Entities (Web Client, User, Client Application, External API, External Payment Provider): Only S, R columns active; T, I, D, E marked n/a
- [x] Processes (all services, gateways): All 6 STRIDE columns active
- [x] Data Stores (databases, session store, message queue, knowledge base, audit logger): Only T, I, D columns active; S, R, E marked n/a
- [x] AG and LLM columns: Active only for AI-triggered components in agentic-app; n/a in web-app and microservices

### 6. Risk Level Computation (OWASP 3x3 Matrix)
- [x] Spot-checked all web-app findings: Likelihood x Impact -> Risk Level correct for each finding
- [x] Spot-checked all microservices findings: Risk counts match (Critical=3, High=11, Medium=9, Total=23)
- [x] Agentic-app deduplication logic correct: CG-1 (T-2+LLM-2 both Medium) and CG-2 (E-1+AG-1 both High) each reduce count by 1
- [ ] Web-app Risk Summary count: FAIL (Medium count 7 should be 8)

### 7. Markdown Quality
- [x] No broken tables detected (all tables render with correct column alignment)
- [x] Heading hierarchy clean: H1 -> H2 -> H3, no skipped levels
- [x] Mermaid diagrams use standard `flowchart TD` syntax compatible with GitHub renderer
- [x] Horizontal rules (`---`) used consistently as section separators
- [x] Frontmatter delimiters (`---`) properly formatted

### 8. Spec Requirement Coverage
- [x] FR-001: Three example directories with architecture.md + threats.md each
- [x] FR-002: Valid Mermaid flowcharts with 4+ components, trust boundaries, labeled flows
- [x] FR-003: Schema v1.1 with all 7+1 sections and YAML frontmatter
- [x] FR-004: Web-app STRIDE populated, AI sections present-but-empty
- [x] FR-005: Agentic-app STRIDE + AG + LLM populated, Section 4a has 2 correlation groups
- [x] FR-006: Microservices cross-service findings, coverage matrix spans 10 components
- [x] FR-007: OWASP appendix present in all three with correct framework mappings
- [x] FR-008: examples/README.md has overview, hierarchy diagram, mapping table, usage instructions
- [x] FR-009: Project README references examples directory
- [x] FR-010: Three legacy examples retained intact
- [x] FR-011: Risk levels computed via OWASP 3x3 matrix (one count error in summary, computations themselves correct)
- [x] FR-012: Coverage matrices use three-state model with correct STRIDE-per-Element dispatch

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Warning | 2 |
| Suggestion | 3 |
| **Total** | **5** |

The implementation is high quality overall. All 8 files are structurally sound, follow schema v1.1 correctly, and maintain consistent patterns across the three examples. The STRIDE-per-Element dispatch rules are applied correctly in all coverage matrices. Internal references are all valid. The two WARNING items are genuine but non-blocking: W-1 is a count error in one risk summary table, and W-2 is a formatting inconsistency in one section header.

**Verdict: APPROVED_WITH_CONCERNS** -- the count error in W-1 should be corrected before merge to maintain data integrity in the reference examples. W-2 and the suggestions are optional improvements.
