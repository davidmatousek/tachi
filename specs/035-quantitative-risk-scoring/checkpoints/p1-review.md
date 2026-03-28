# P1 Checkpoint Review: Quantitative Risk Scoring

**Feature**: #035 Quantitative Risk Scoring
**Checkpoint**: P1 -- Core Functionality (Production Cutover)
**Reviewer**: Architect
**Date**: 2026-03-27
**Status**: APPROVED_WITH_CONCERNS

---

## Review Scope

Validated Waves 1-4b deliverables (T001-T019, 19/29 tasks) against spec.md (5 user stories, 17 FRs, 9 success criteria) and plan.md (6-phase architecture, schema design, data flow).

**Deliverables reviewed**:
- `schemas/risk-scoring.yaml` -- scored finding extension schema
- `.claude/agents/tachi/risk-scorer.md` -- primary scoring agent (1,407 lines)
- `templates/risk-scores.md` -- markdown output template (253 lines)
- `templates/risk-scores.sarif` -- SARIF output template (439 lines)

---

## Findings

| ID | Severity | Category | Description | Resolution |
|----|----------|----------|-------------|------------|
| P1-001 | Medium | Edge Case | **Empty threat model and missing input file handling not defined in agent.** Spec edge cases require: (1) zero findings exits with "No threat findings to score" and (2) missing input files exits with "No threat model output found. Run `/threat-model` first." The agent defines parsing rules and fallback for trust zones exhaustively but does not include explicit pre-scoring validation for these two terminal conditions. The command definition (T020, Wave 5) is the natural location for input existence checks, but the agent itself should define the zero-findings exit since the agent performs the parsing. | Add a post-parsing gate in the agent between Section 1 (Threat Parsing) and Section 2 (Trust Zone Extraction): if parsed findings count is zero after parsing completes, halt scoring and emit "No threat findings to score." This is agent-level logic, not command-level. The missing-input-file check belongs in the command (T020) and is out of scope for this checkpoint. |
| P1-002 | Medium | Spec Coverage | **Large threat model handling (>100 findings, up to 200) lacks guidance in agent.** Spec edge case and SC-006 require scoring up to 200 threats within 5 minutes, with batching strategies if needed. The plan (Risk Mitigations table) mentions "Batch scoring into per-category sub-invocations if single-pass exceeds limits." The agent contains no batching strategy, chunking guidance, or performance considerations for large input sets. | Add a subsection to the Scoring Pipeline Overview (or as a note in Section 7 Composite Calculation) addressing large threat model processing: state that the scoring pipeline processes findings sequentially in a single pass; if context window pressure arises with >100 findings, the command layer (T020) may batch invocations by category. This positions the batching decision correctly (command orchestration, not agent internals) while documenting the expectation. |
| P1-003 | Low | Template-Agent Mismatch | **Governance Fields table column mismatch between template and agent.** The template (`templates/risk-scores.md` Section 4) defines a 6-column table: `ID | Severity | Owner | SLA | Disposition | Review Date`. The agent (Section 9e) defines a 7-column table adding `Component`: `ID | Component | Severity | Owner | SLA | Disposition | Review Date`. The agent output specification is more informative (Component column aids triage), but the template and agent are inconsistent. | Align the template to match the agent's 7-column definition by adding the `Component` column to `templates/risk-scores.md` Section 4. The agent's version is the better design since Component context is essential for triage without cross-referencing Section 2. |
| P1-004 | Low | Template Structure | **Markdown template Section 3 (Dimensional Breakdown) structure differs from agent specification.** The template defines per-finding breakdowns with separate subsection tables for each CVSS metric (AV, AC, PR, UI, S, C, I, A with Rationale columns) and separate Exploitability/Scalability sub-dimension tables. The agent Section 9d defines a simpler consolidated format with a single 4-row dimension table and bullet-point rationale. Both are valid, but they are different formats -- the template is more detailed, the agent is more concise. | Resolve by aligning to a single format. Recommendation: adopt the agent's concise format (Section 9d) as canonical since it produces output that is easier to scan at scale (20+ findings). The template's detailed CVSS metric table and sub-dimension tables can be documented as an optional "verbose" mode in a Phase 2 enhancement. Update `templates/risk-scores.md` Section 3 to match the agent's Section 9d format. |
| P1-005 | Low | Plan Concern Tracking | **T023 security-severity semantic shift documentation -- flagged correctly in plan.md architect sign-off, addressed in agent.** The architect concern from the plan review (tasks.md architect_signoff notes) stated that T023 should document the security-severity semantic shift between threats.sarif and risk-scores.sarif. The agent (Section 10, opening paragraph) explicitly documents this shift: "In threats.sarif, the rule-level security-severity is a static category value... In risk-scores.sarif, the result-level security-severity is the per-finding composite score and the rule-level security-severity is the MAX composite score." T023 is Wave 5 work (SARIF reference guide update), but the agent already carries the architectural intent. This concern is tracked, not blocking. | No action needed at this checkpoint. T023 will propagate this documentation to `adapters/claude-code/agents/references/sarif-generation.md` during Wave 5. Verified that the agent already embeds the correct semantic description. |
| P1-006 | Low | SARIF Compliance | **SARIF template uses placeholder strings for security-severity at rule level.** `templates/risk-scores.sarif` uses `<max-composite-score-for-spoofing-findings>` style placeholders in rule-level `security-severity` fields. This is correct template behavior (populated at generation time), but the placeholder format uses angle brackets which are not valid JSON string content. The template is a reference document, not a parseable JSON file, so this is cosmetic rather than functional. | No action required. The template is correctly documented as a structural reference. The agent (Section 10b) defines the actual generation logic. If the template is ever used for JSON validation, the placeholders would need to be replaced with example values. |
| P1-007 | Low | Dual-Format Parity | **Markdown/SARIF result count asymmetry for correlation groups is documented but warrants validation emphasis.** Agent Section 10h correctly states that peer findings do NOT appear as separate SARIF results (they appear in relatedLocations), while the markdown Scored Threat Table lists peers as separate rows. This means `risk-scores.md` row count may differ from `risk-scores.sarif` results array length. This is architecturally correct (SARIF best practice) but the SC-005 dual-format parity success criterion ("All scores and governance fields are consistent between formats") needs to account for this structural difference during validation (T028). | Flag for T028 (Wave 6): the parity check must compare *logical* finding coverage (primaries + peers accounted for in both formats), not raw result counts. The agent documents this in Sections 10h and 10j. No change needed to the agent -- this is a validation task concern. |

---

## Review Criteria Assessment

### 1. Architecture Alignment

**PASS.** The agent pipeline faithfully implements the 6-phase flow from plan.md:
1. Threat Parsing (Section 1) -- threats.md canonical, threats.sarif fallback
2. Trust Zone Extraction (Section 2) -- component-to-zone mapping dictionary
3. Dimensional Scoring (Sections 3-6) -- CVSS, exploitability, scalability, reachability
4. Composite Calculation (Section 7) -- weighted formula, severity band mapping
5. Governance Fields (Section 8) -- severity-driven defaults
6. Output Generation (Sections 9-10) -- dual markdown and SARIF output

The pipeline phases map 1:1 to the plan's agent pipeline definition (plan.md lines 117-128).

### 2. Spec Coverage

**PASS with concerns (P1-001, P1-002).** All 5 user stories and 17 functional requirements are addressed:

| Requirement | Agent Section | Status |
|-------------|--------------|--------|
| FR-001 (parse threats.md + threats.sarif) | Sections 1a, 1b | Covered |
| FR-002 (CVSS 3.1 base score) | Section 3 | Covered |
| FR-003 (CVSS vector string) | Section 3 | Covered |
| FR-004 (exploitability) | Section 4 | Covered |
| FR-005 (scalability) | Section 5 | Covered |
| FR-006 (reachability from trust zones) | Sections 2, 6 | Covered |
| FR-007 (composite formula) | Section 7 | Covered |
| FR-008 (severity bands) | Section 7 | Covered |
| FR-009 (governance fields) | Section 8 | Covered |
| FR-010 (risk-scores.md generation) | Section 9 | Covered |
| FR-011 (risk-scores.sarif generation) | Section 10 | Covered |
| FR-012 (preserve original metadata) | Section 1 | Covered |
| FR-013 (preserve SARIF fingerprints) | Section 10e | Covered |
| FR-014 (default reachability 5.0) | Section 6e | Covered |
| FR-015 (graceful malformed handling) | Section 1 (Error Handling) | Covered |
| FR-016 (input validation) | Not in agent (command-layer) | Deferred to T020 |
| FR-017 (output co-location) | Sections 9g, 10i | Covered |

Gaps: empty threat model exit (P1-001) and large model batching guidance (P1-002) are Medium severity but addressable before Wave 5.

### 3. Schema Consistency

**PASS.** `schemas/risk-scoring.yaml` matches plan.md Section "Schema Design" exactly:
- All 12 scored_finding fields present with correct types and ranges
- 8 category_defaults vectors match plan.md (including the architect-requested PR:L for agentic)
- Weights (0.35/0.30/0.15/0.20) match plan and agent
- Severity bands (Critical 9.0-10.0, High 7.0-8.9, Medium 4.0-6.9, Low 0.0-3.9) align with output.yaml
- Note-to-Low consolidation documented in schema description

### 4. Template Completeness

**PASS with minor concerns (P1-003, P1-004).** Both templates cover all required output sections:

- `templates/risk-scores.md`: Frontmatter, Executive Summary, Scored Threat Table, Dimensional Breakdown, Governance Fields, Scoring Methodology -- all present with field definitions and format specifications
- `templates/risk-scores.sarif`: SARIF 2.1.0 skeleton with $schema, version, tool.driver, 8 rule definitions (6 STRIDE + 2 AI), taxonomy declarations, results with property bags, correlation group example with relatedLocations

Two minor inconsistencies between template and agent (P1-003 governance column count, P1-004 dimensional breakdown format) -- neither blocks functionality.

### 5. SARIF Compliance

**PASS.** The SARIF template and agent Section 10 demonstrate correct SARIF 2.1.0 compliance:
- `$schema` points to the official OASIS SARIF 2.1.0 schema URI
- `version: "2.1.0"` at document root
- `tool.driver` with name, version, semanticVersion, informationUri, rules, supportedTaxonomies
- Results include ruleId, message (text + markdown), level, locations (physical + logical), partialFingerprints, properties
- Taxonomy declarations (OWASP 2021, CWE 4.13) preserved with correct structure
- Rule relationships map to taxonomy entries with correct target format
- Fingerprint preservation rules (findingId/v1, primaryLocationLineHash, correlationGroup) are explicit
- Correlation groups use relatedLocations pattern (SARIF-compliant, peers not duplicated as top-level results)

### 6. Scoring Methodology

**PASS.** All scoring components correctly implemented:
- **CVSS defaults**: 8 category vectors with computed base scores (spoofing 8.2, tampering 7.1, repudiation 4.3, info-disclosure 6.5, DoS 7.5, privesc 9.9, agentic 9.1, llm 9.3). The agentic PR:L (architect review concern from plan.md) is correctly applied.
- **Exploitability**: 4 sub-dimensions (known techniques, attack complexity, tooling, skill level) averaged. AI-specific guidance for 6 AI threat subtypes with baseline scores. Inversion note for complexity/skill correctly documented.
- **Scalability**: 4 sub-dimensions (scriptability, target scope, resource requirements, detection difficulty) averaged. Resource requirements inversion correctly documented.
- **Reachability**: 3-tier trust zone mapping (Untrusted 8.0-10.0, Semi-Trusted 4.0-7.0, Trusted 1.0-4.0) with zone name keyword refinement, architecture adjustments (-1.5/auth, -1.0/network, caps at -7.5 total), fuzzy matching, and proper fallback to 5.0.
- **Composite formula**: `(0.35 x CVSS) + (0.30 x Exploitability) + (0.15 x Scalability) + (0.20 x Reachability)` matches spec FR-007 exactly.
- **Severity bands**: Boundary precision rule (7.0 = High, 4.0 = Medium, 9.0 = Critical) matches spec edge case.

### 7. Governance Fields

**PASS.** SLA defaults, disposition mapping, and review date calculation all correctly defined:
- Critical: 24h SLA, Mitigate, scoring_date + 1 day
- High: 7d SLA, Mitigate, scoring_date + 7 days
- Medium: 30d SLA, Review, scoring_date + 30 days
- Low: 90d SLA, Review, scoring_date + 90 days
- Owner defaults to "Unassigned"
- Accept/Transfer documented as human-override-only values
- Month/year boundary handling noted
- Correlation group governance inheritance documented

### 8. Edge Cases

**PARTIAL (P1-001, P1-002).** Coverage assessment:

| Edge Case (from spec) | Agent Coverage | Status |
|------------------------|---------------|--------|
| Malformed threat input | Section 1 Error Handling: skip + report + continue | Covered |
| Empty threat model (zero findings) | **Not explicitly handled** -- no post-parsing zero-check | Gap (P1-001) |
| Missing input files | Command-layer concern (T020) | Deferred appropriately |
| Correlated findings | Section 7 Correlation Group Handling + Section 10h SARIF handling | Covered |
| Score boundary precision | Section 7: "7.0 = High, 4.0 = Medium, 9.0 = Critical" | Covered |
| Large threat models (>100) | **No batching/performance guidance** | Gap (P1-002) |
| AI-specific CVSS mappings | Section 3 AI-Specific CVSS Guidance + category defaults | Covered |
| Missing trust zones | Section 2g Fallback Behavior: default 5.0 with warning | Covered |

### 9. T023 Semantic Shift Documentation

**TRACKED.** The semantic shift between threats.sarif and risk-scores.sarif security-severity values is:
- Documented in agent Section 10 (opening paragraph)
- Documented in agent Section 10b (Rule-level security-severity calculation)
- Referenced in tasks.md T023 description
- Will be propagated to SARIF reference guide in Wave 5

No blocking issues. The agent carries the architectural intent correctly.

---

## Summary

The core scoring functionality is architecturally sound. The agent implements the full 6-phase pipeline with faithful adherence to the plan.md architecture, complete FR coverage (16 of 17 FRs covered in agent; FR-016 appropriately deferred to command layer), and correct SARIF 2.1.0 compliance. The schema, templates, and agent are internally consistent with two minor template-agent alignment issues (P1-003, P1-004) that are Low severity.

Two Medium findings (P1-001 empty threat model exit, P1-002 large model guidance) should be addressed before Wave 5 (Command + Integration) begins, as they represent gaps between spec edge cases and agent behavior. Both are straightforward additions that do not require architectural changes.

**Recommendation**: Proceed to Wave 5 after addressing P1-001 and P1-002. The five Low findings are non-blocking and can be resolved during Wave 5 work or as part of T020/T028 implementation.
