---
source_agent: orchestrator.md
loaded_at: Pipeline end (final validation)
extracted_from: Output Structural Validation Checklist lines 1138-1223
version: "1.0"
---

### Output Structural Validation Checklist

Before finalizing the output document, run the following validation checklist against the assembled `threats.md`. Every check must pass. If any check fails, correct the issue before producing the final output.

#### Section Completeness

- [ ] Section 1 (System Overview) is present and contains the Components, Data Flows, and Technologies tables.
- [ ] Section 2 (Trust Boundaries) is present and contains the Trust Zones and Boundary Crossings tables (or the "no trust boundaries identified" note with empty table headers).
- [ ] Section 3 (STRIDE Tables) is present and contains exactly 6 tables (S, T, R, I, D, E), each with a table header row even if no data rows exist.
- [ ] Section 4 (AI Threat Tables) is present and contains exactly 2 tables (AG, LLM), each with a table header row even if no data rows exist.
- [ ] Section 4a (Correlated Findings) is present and contains the correlation group table with correct columns (Group, Findings, Component, Threat Summary, Risk Level), or the "No cross-agent correlations detected" text with empty table header when zero correlations exist.
- [ ] Section 5 (Coverage Matrix) is present and contains one row per component plus a Total row. All cells use the three-state model: integer (deduplicated count), `---` (analyzed but clean), or `n/a` (not applicable).
- [ ] Section 5 (Coverage Matrix) footnote is present when correlation groups exist, stating "Counts reflect deduplicated findings. N correlation groups merged M individual findings." Footnote is absent when zero correlation groups exist.
- [ ] Section 6 (Risk Summary) is present and contains the Risk Calibration Matrix subsection followed by one row per risk level (Critical, High, Medium, Low, Note) plus a Total row.
- [ ] Section 7 (Recommended Actions) is present and contains one row per finding.

#### Frontmatter Validation

- [ ] `schema_version` is `"1.1"`.
- [ ] `date` is a valid ISO 8601 date in `YYYY-MM-DD` format.
- [ ] `input_format` is one of: `ascii`, `free-text`, `mermaid`, `plantuml`, `c4`.
- [ ] `classification` is `"confidential"`.

#### Finding ID Validation

- [ ] Every finding ID in the STRIDE tables matches the pattern `{S|T|R|I|D|E}-{N}` where N is a positive integer.
- [ ] Every finding ID in the AI tables matches the pattern `{AG|LLM}-{N}` where N is a positive integer.
- [ ] IDs are sequentially numbered within each category starting at 1, with no gaps.
- [ ] No duplicate IDs exist within any table or across tables of the same category.

#### Field Completeness

- [ ] Every finding row in the STRIDE tables has all 7 required fields populated: ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation.
- [ ] Every finding row in the AI tables has all 8 required fields populated: ID, Component, Threat, OWASP Reference, Likelihood, Impact, Risk Level, Mitigation.
- [ ] No field contains an empty value or placeholder text.

#### Risk Level Consistency

- [ ] Every finding's `risk_level` matches the OWASP 3x3 matrix computation for its `likelihood` and `impact` values.
- [ ] `likelihood` values are one of: `LOW`, `MEDIUM`, `HIGH`.
- [ ] `impact` values are one of: `LOW`, `MEDIUM`, `HIGH`.
- [ ] `risk_level` values are one of: `Critical`, `High`, `Medium`, `Low`, `Note`.

#### Cross-Section Consistency

- [ ] Coverage matrix cell counts reflect deduplicated counts: uncorrelated findings count individually, correlation group members contribute 1 collectively per component-category pair.
- [ ] Coverage matrix Total column values equal the sum of deduplicated finding counts in each component's row (`---` and `n/a` cells contribute 0).
- [ ] Coverage matrix Total row values equal the sum of deduplicated finding counts in each category's column.
- [ ] All correlation group member IDs (CG-N entries in Section 4a) reference finding IDs that exist in the STRIDE tables (Section 3) or AI tables (Section 4).
- [ ] Risk summary counts reflect deduplicated totals: each correlation group counts as 1 at its group risk level. When the deduplicated total differs from the raw total, counts include the parenthetical raw count (e.g., "5 (7 raw)").
- [ ] Risk summary Total equals the deduplicated grand total of all findings.
- [ ] Risk summary percentages are computed from the deduplicated total as denominator and sum to exactly 100%.
- [ ] Recommended actions list contains every finding from all 8 tables exactly once (raw count, not deduplicated -- each individual finding has its own mitigation).
- [ ] Recommended actions list row count equals the raw finding total (not the deduplicated total).

#### SARIF Output (`threats.sarif`)

- [ ] A `threats.sarif` file is produced in the same output directory as `threats.md`.
- [ ] The SARIF file is valid JSON with `$schema`, `version: "2.1.0"`, and `runs[]` at the top level.
- [ ] `tool.driver.name` is `"Tachi"` and `rules[]` contains only categories that produced findings.
- [ ] The number of SARIF `results[]` matches the deduplicated finding count in `threats.md`.
- [ ] Every result has `ruleId`, `message.text`, `level`, `locations[]`, and `partialFingerprints`.
- [ ] Every `ruleId` has a corresponding entry in `tool.driver.rules[]`.

#### Phase 5 Outputs (when Phase 5 is enabled)

- [ ] `threat-report.md` exists in the output directory
- [ ] `threat-report.md` contains YAML frontmatter with `schema_version: "1.0"`, `date`, `source_file`, `finding_count`, `risk_distribution`, `attack_tree_count`
- [ ] `threat-report.md` contains all 7 required sections (## 1. Executive Summary through ## 7. Appendix: Finding Reference)
- [ ] `attack-trees/` directory exists in the output directory
- [ ] `attack-trees/` contains one file per Critical and High finding, named `{finding-id}-attack-tree.md`
- [ ] Finding count in `threat-report.md` frontmatter matches the finding count in `threats.md`
- [ ] Appendix: Finding Reference in `threat-report.md` contains every finding ID from `threats.md`

#### Phase 6 Outputs (when Phase 6 is enabled)

- [ ] `threat-infographic-spec.md` exists in the output directory
- [ ] `threat-infographic-spec.md` contains all 6 required sections (Metadata, Risk Distribution, Coverage Heat Map, Top Critical Findings, Architecture Threat Overlay, Visual Design Directives)
- [ ] Risk distribution counts in `threat-infographic-spec.md` match `threats.md` Section 6 (Risk Summary)
- [ ] If `GEMINI_API_KEY` is set: `threat-infographic.jpg` exists in the output directory and is a valid JPEG file
- [ ] If `GEMINI_API_KEY` is not set: informational message logged ("Gemini API key not configured -- infographic image generation skipped. Specification saved."), no image file expected

If all checks pass, the `threats.md` output document is structurally valid, the `threats.sarif` file is consistent with it, (when Phase 5 is enabled) the `threat-report.md` and `attack-trees/` are complete, and (when Phase 6 is enabled) the `threat-infographic-spec.md` and optional `threat-infographic.jpg` are valid. Produce the final outputs.
