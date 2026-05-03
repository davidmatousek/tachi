# Architect Review: Feature 029 — Agent Refactoring (Right-Size)

**Reviewer**: Architect
**Date**: 2026-03-25
**Status**: APPROVED
**Feature Branch**: `029-agent-refactoring-right`

---

## Review Scope

Architecture review of the completed lazy-load reference extraction across three agent files (orchestrator, threat-report, threat-infographic), covering:

1. Reference loading instruction clarity and correctness
2. Specification content preservation (no accidental removal)
3. Self-containment rule: no cross-references between reference documents
4. Error-on-missing instruction presence in each agent
5. Defensive specification content retained in orchestrator core

---

## 1. Reference Loading Instructions — PASS

All three refactored agents follow a consistent, well-defined loading pattern.

### Pattern Structure

Each agent contains a `## Reference Documents` section near the top of the file (orchestrator line 82, threat-report line 38, threat-infographic line 63) with:

1. A preamble: "This agent loads reference documents on-demand [during X]. Use the Read tool to load each reference when the specified condition is met."
2. A table with columns: Reference | Path | Load When
3. An error-on-missing instruction (see Finding 4 below)

### Loading Trigger Points

Each extracted section in the agent body contains an inline pointer back to the Reference Documents table:

- **Orchestrator**: Two inline pointers at lines 1067 and 1073 using blockquote format:
  - `> **Reference document**: Load adapters/claude-code/agents/references/validation-checklist.md at pipeline end.`
  - `> **Reference document**: Load adapters/claude-code/agents/references/sarif-generation.md at Phase 4 completion.`
  - Error templates: Referenced in error handling section (lines 1167, 1173, 1179) with "Load error template from" phrasing
- **Threat-report**: One inline pointer at line 337 for report-templates.md during attack tree generation
- **Threat-infographic**: Two inline pointers at lines 406 and 412 for Gemini API and error handling references

### Assessment

The dual-anchor approach (table at top + inline pointer at usage site) is architecturally sound. An LLM processing the agent prompt encounters the reference path at the exact pipeline phase where loading is needed, and can also consult the centralized table for a complete manifest. The "Load When" column in the table aligns precisely with the inline trigger conditions.

---

## 2. Specification Content Preservation — PASS

### Orchestrator (2,085 -> 1,273 lines, -38.9%)

The orchestrator retains all specification content that governs pipeline execution:

- **Phase 1-4 complete**: Format detection (lines 302-356), component extraction and DFD classification (lines 359-421), trust boundary identification (lines 424-447), STRIDE-per-Element normalization (lines 545-590), AI keyword dispatch (lines 593-647), agent invocation protocol (lines 650-667), dispatch modes (lines 670-736), Phase 3 collection and validation (lines 740-799), STRIDE/AI table assembly (lines 801-868), correlation detection algorithm and rules (lines 871-935), Phase 4 coverage matrix and risk summary (lines 939-1062)
- **Output format specification**: Complete section structure, frontmatter, all 7+4a section definitions (lines 98-282)
- **Input sanitization boundary**: Preserved at lines 60-78
- **Error handling summary**: Retained at lines 1159-1191 with pointers to error-templates.md for the verbose YAML templates only

Extracted to references (verified present and complete):
- `sarif-generation.md`: 499 lines — full SARIF 2.1.0 mapping tables, fingerprint computation, taxonomy declarations, correlated finding mapping, JSON structure, self-check
- `validation-checklist.md`: 90 lines — all section completeness, frontmatter, finding ID, field, risk level, cross-section, SARIF, Phase 5, Phase 6 validation checks
- `error-templates.md`: 131 lines — three YAML error templates (UNSUPPORTED_FORMAT, NO_COMPONENTS, INVALID_FORMAT_VALUE) with trigger conditions, responses, and guidance

### Threat-Report (801 -> 472 lines, -41.1%)

The report agent retains all generation methodology:

- Input contract with required sections and finding IR fields (lines 52-100)
- Quality standards and output validation checklist (lines 104-161)
- Report generation methodology: executive summary, architecture overview, threat analysis, cross-cutting themes, correlation handling, appendix (lines 162-332)
- Dual output location (inline + standalone) for attack trees (lines 341-388)
- Remediation roadmap generation with effort estimation and correlation consolidation (lines 391-472)

Extracted to references (verified present and complete):
- `report-templates.md`: 298 lines — attack tree construction rules, Mermaid conventions (node IDs, shapes, labels, edges, styling), Mermaid validation checklist, two complete example trees (AG-1 Critical, LLM-2 High)

### Threat-Infographic (592 -> 414 lines, -30.1%)

The infographic agent retains all data extraction and specification format:

- Input contract with required sections and finding IR fields (lines 79-114)
- Data extraction methodology: 5 steps + Step 5b (lines 117-198)
- Infographic specification format: all 6 sections with table schemas (lines 200-354)
- Quality standards and validation checklist (lines 357-401)
- Template loading instructions (lines 306-313)

Extracted to references (verified present and complete):
- `infographic-gemini-api.md`: 148 lines — prompt construction, design philosophy, API configuration, key check, request format, response parsing, fallback model
- `infographic-error-handling.md`: 67 lines — all 6 failure conditions (missing key, rate limit, timeout, content policy, missing Section 6, empty model) with degradation summary table

### Line Count Verification Against Spec Targets

| Agent | Spec Target | Actual | Status |
|-------|-------------|--------|--------|
| Orchestrator | ~1,100-1,200 | 1,273 | Slightly above range |
| Threat-report | ~300-400 | 472 | Above range |
| Threat-infographic | ~300-400 | 414 | Slightly above range |

**Assessment**: All three agents exceed their spec target ranges. However, this is a non-blocking observation. The spec targets (SC-001 through SC-003) used approximate ranges with `~` prefix, and the overages are modest. The orchestrator at 1,273 is 6% above the upper bound of 1,200. The report agent at 472 is 18% above 400. The infographic agent at 414 is 3.5% above 400. The critical architectural goal — extracting consultation-only content to reduce always-loaded context — is achieved. Further compression would risk removing specification content (which the spec explicitly prohibits in FR-015). The reduction percentages (38.9%, 41.1%, 30.1%) represent substantial context savings.

---

## 3. Self-Containment Rule — PASS

Verified via grep that zero reference documents contain paths to other reference documents. Each reference is a leaf node in the loading graph:

```
orchestrator.md -> sarif-generation.md         (no outbound refs)
orchestrator.md -> validation-checklist.md     (no outbound refs)
orchestrator.md -> error-templates.md          (no outbound refs)
threat-report.md -> report-templates.md        (no outbound refs)
threat-infographic.md -> infographic-gemini-api.md       (no outbound refs)
threat-infographic.md -> infographic-error-handling.md   (no outbound refs)
```

The loading graph is a strict one-level tree: each agent loads its own references, references never load other references, and no agent loads another agent's references. This ensures that a Read tool call for any reference resolves in a single hop with no cascading dependencies.

---

## 4. Error-on-Missing Instruction — PASS

All three agents contain the identical error-on-missing pattern immediately after their Reference Documents table:

```
If any reference document is missing, STOP and report the error:
"ERROR: Required reference document not found: {path}"
```

Verified at:
- `orchestrator.md`: lines 93-94
- `threat-report.md`: lines 47-48
- `threat-infographic.md`: lines 73-74

The instruction is clear, actionable, and uses a consistent error message format across all agents. The `{path}` placeholder enables the LLM to report exactly which file is missing.

---

## 5. Defensive Specification Content — PASS

The spec (FR-008) requires that defensive specification content remain in the orchestrator core. Verified present:

| Content | Location | Status |
|---------|----------|--------|
| DFD Element Types (classification rules) | Lines 363-399 | Retained |
| Ambiguous Classification (default-to-Process) | Lines 401-408 | Retained |
| Non-Conforming Finding Handling | Lines 1230-1260 | Retained |
| Three-State Cell Model | Lines 1263-1273 | Retained |
| AI Keyword Ambiguity handling | Lines 1214-1226 | Retained |

All five defensive blocks are present in the core orchestrator. They were correctly identified as always-needed during pipeline execution (not consultation-only) and excluded from extraction.

---

## 6. Reference Document Frontmatter — PASS

All 6 reference documents include YAML frontmatter with the three metadata fields required by FR-004:

| Reference | source_agent | loaded_at | version |
|-----------|-------------|-----------|---------|
| sarif-generation.md | orchestrator.md | Phase 4 completion | 1.0 |
| validation-checklist.md | orchestrator.md | Pipeline end | 1.0 |
| error-templates.md | orchestrator.md | Error condition | 1.0 |
| report-templates.md | threat-report.md | Attack tree generation | 1.0 |
| infographic-gemini-api.md | threat-infographic.md | Image generation | 1.0 |
| infographic-error-handling.md | threat-infographic.md | Error condition | 1.0 |

All also include an `extracted_from` field documenting the source section and line range, which aids traceability back to the pre-refactoring content.

---

## 7. Verification Results Assessment

The reported verification results are consistent with the architectural constraints:

- **11 threat agents byte-identical**: Confirms FR-008 / US-4 constraint boundary
- **2 infographic templates unchanged**: Confirms template isolation
- **6 schemas unchanged**: Confirms no schema drift
- **SARIF 2.1.0 validation passed**: Confirms SARIF specification was extracted without corruption
- **All 6 reference documents loadable with frontmatter**: Confirms Read tool compatibility

---

## 8. Security Posture

- **Input sanitization boundary**: Preserved in orchestrator core (lines 60-78). The `<architecture-input>` parsing boundary and anti-injection instructions were not extracted. This is correct — they are always-needed security controls.
- **Classification: confidential**: Frontmatter rule retained in core (line 76, line 129)
- **No secrets in reference documents**: All 6 references contain specification content only (mapping tables, templates, checklists). No API keys, credentials, or PII.
- **GEMINI_API_KEY handling**: The key-check logic in `infographic-gemini-api.md` reads from environment variables only, with `.env` fallback. No hardcoded keys.

---

## 9. Observations (Non-Blocking)

### 9a. Line count targets exceeded

As noted in Section 2, all three agents exceed their spec target ranges. The report agent at 472 lines (vs. 300-400 target) has the largest overage. This is likely because the report generation methodology (executive summary rules, threat analysis section structure, remediation roadmap effort estimation) is genuinely always-needed during report generation and cannot be further extracted without fragmenting the generation flow. Non-blocking because the spec acknowledges approximate targets and prohibits removing specification content.

### 9b. Error templates loading pattern

The orchestrator's error handling section (lines 1165-1179) uses a slightly different phrasing for its error template references compared to the SARIF and validation references. The SARIF and validation references use blockquote format (`> **Reference document**: Load...`), while the error templates use inline text ("Load error template from `adapters/claude-code/agents/references/error-templates.md`."). Both are clear and functional, but the inconsistency is worth noting for future style standardization.

---

## Summary

| Check | Result |
|-------|--------|
| Reference loading instructions clear and correct | PASS |
| No specification content accidentally removed | PASS |
| Self-containment: no cross-references between references | PASS |
| Error-on-missing instruction in each agent | PASS |
| Defensive specification content retained in orchestrator | PASS |
| Reference document frontmatter complete | PASS |
| Verification results consistent | PASS |
| Security posture maintained | PASS |

**Verdict**: The lazy-load reference extraction is architecturally sound. The loading graph is a strict one-level tree with no cascading dependencies. Specification content is fully preserved. Defensive content is correctly retained in core agent files. The extraction achieves the primary goal of reducing always-loaded context to improve instruction-following fidelity.

---

**APPROVED**

Architect sign-off granted for Feature 029 implementation.
