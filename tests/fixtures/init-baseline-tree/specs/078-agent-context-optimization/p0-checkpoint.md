# P0 Checkpoint: Architect Review -- Feature 078 Agent Context Optimization

**Reviewer**: Architect
**Date**: 2026-04-01
**Status**: APPROVED_WITH_CONCERNS
**Scope**: Waves 1-2 (T001-T011) -- Baseline, model fields, best practices, risk-scorer reference file creation

---

## Review Summary

Waves 1-2 deliver solid foundational work. The three new reference files (trust-zones, reachability-analysis, output-formatting) are thorough, well-structured, and contain the correct domain knowledge. The content extraction quality is high -- domain data was cleanly separated from orchestration logic. The baseline capture is adequate for regression testing. Two non-blocking concerns require action before T012 (agent trimming) proceeds.

**Decision**: APPROVED_WITH_CONCERNS -- proceed to T012 with the two concerns addressed.

---

## 1. Reference File Completeness

### trust-zones.md (173 lines) -- PASS

Completeness is excellent. The file covers the full trust zone extraction lifecycle:

- Section 2a: Table location procedure (3-step: find heading, find subsection, identify table)
- Section 2b: Row parsing with extraction rules and examples
- Section 2c: Trust level normalization (3-step cascade: exact match, keyword classification, default)
- Section 2d: Zone name normalization (case-insensitive matching, no renaming)
- Section 2e: Component-to-zone mapping dictionary with construction rules and example output
- Section 2f: Cross-reference with Section 1 components (bidirectional coverage check)
- Section 2g: Fallback behavior (4 fallback cases with specific warning messages)
- Section 2h: Error handling (malformed rows, empty components, empty zones, duplicates, boundary crossings disambiguation)

Content verified against the risk-scorer agent Section 2 (lines 227-394). The extraction is a faithful, complete copy of all domain knowledge. The Section 2 numbering convention (2a-2h) is preserved, which will make the agent's Read instruction unambiguous.

**Finding**: The Boundary Crossings disambiguation note (Section 2h, line 173) is a valuable inclusion that prevents a real parsing error. Good extraction judgment.

### reachability-analysis.md (180 lines) -- PASS

The file covers the complete reachability pipeline:

- Input dependencies (component_zone_map + architecture.md)
- Zone-to-reachability baseline mapping table (Untrusted/Semi-Trusted/Trusted with score ranges)
- Per-finding baseline refinement (zone name keyword adjustments with examples)
- Architecture adjustments (authentication barriers at -1.5 each, network segmentation at -1.0 each, combined calculation with examples)
- Final score clamping
- Default behavior when trust zone data is unavailable (including architecture.md-only case)
- Component name fuzzy matching (4-step cascade: exact, substring, word overlap, no match)
- Scoring summary (6-step sequence)

Content verified against risk-scorer Section 6 (lines 461-476 in the trimmed agent body, and the full Section 6 content that currently spans hundreds of lines in the agent). Extraction is complete.

**Observation on baseline values**: The task description T008 cited baseline values of "Untrusted=8.5, Semi-Trusted=6.0, Trusted=3.0", but the actual reference file uses "Untrusted=9.0, Semi-Trusted=5.5, Trusted=2.5" -- which matches the risk-scorer agent's actual content. The reference file is correct; the task description was inaccurate. No action needed since the file content is authoritative.

### output-formatting.md (155 lines) -- PASS

The file covers all output formatting specifications:

- Scored threat table column definitions (11 columns with source fields and formats)
- Sort order rules (composite descending, secondary by ID)
- Truncation rules (30-char component, 60-char threat, with truncation math)
- Numeric formatting (one decimal place, trailing zeros preserved)
- Correlation group display in table
- Dimensional breakdown format with per-finding subsection template
- Field rules for breakdown (12 fields with generation rules)
- Correlation group display in breakdown
- Category display name mapping (8 IR categories to display names)
- Governance fields table format (7 columns)
- Scoring methodology section (6 required content blocks)

Content verified against risk-scorer Sections 9a-9f (lines 534-739). The extraction captures formatting specifications without including the SARIF output generation (Section 10), which correctly remains in the agent as output orchestration logic.

---

## 2. Extraction Quality

### Content that was correctly extracted (domain data)

| Content Type | Reference File | Lines | Assessment |
|---|---|---|---|
| Trust zone parsing rules | trust-zones.md | 173 | Domain knowledge -- correct extraction |
| Reachability scoring model | reachability-analysis.md | 180 | Domain knowledge -- correct extraction |
| Markdown formatting specs | output-formatting.md | 155 | Format specifications -- correct extraction |
| Bounded scoring for NEW findings | cvss-vectors.md (+32) | 106 | Domain rule -- correct extraction |
| OWASP 3x3 risk matrix | severity-bands.md (+16) | 211 | Reference table -- correct extraction |

### Content that correctly remains in agent (orchestration logic)

- Section 1: Threat parsing (input branching, table extraction, SARIF parsing) -- orchestration
- Section 2 header: "Trust Zone Extraction" section heading and Read instruction -- orchestration
- Sections 3-8: Phase headers with "Domain knowledge: Load..." instructions -- orchestration
- Section 9: Output generation structure (frontmatter rules, executive summary generation, file placement, consistency requirements) -- orchestration
- Section 10: SARIF output generation (tool driver, rule definitions, result generation, fingerprints, taxonomy passthrough, property bag mapping, consistency checks) -- orchestration
- Baseline-aware scoring decisions (inheritance, carry-forward, score source) -- orchestration

### CONCERN-1: SARIF output generation (Sections 10a-10j) should be partially extracted

The risk-scorer agent currently contains 332 lines of SARIF output specification (lines 763-1094). While SARIF generation is technically output orchestration, sections 10b (rule definitions with static rule-to-category tables), 10d (SARIF level mapping), 10f (taxonomy passthrough with default JSON blocks), and 10g (property bag field mapping with static field tables) contain significant static reference data that could be extracted.

This is NOT blocking for the P0 checkpoint. However, when T012 executes the trimming, the agent will need to reach <=500 lines. With the current extraction plan (Sections 2, 6 extracted to references; Sections 3-5 pointing to existing references; 9c/9d partially extracted to output-formatting), the remaining content is:

- Lines 1-226: Frontmatter + pipeline overview + threat parsing (~226 lines)
- Lines 397-460: Sections 3-5 headers with Read pointers (~64 lines)
- Lines 461-476: Section 6 header with Read pointer (~16 lines)
- Lines 479-533: Sections 7-8 composite + governance (~55 lines)
- Lines 534-762: Section 9 output generation (~229 lines)
- Lines 763-1094: Section 10 SARIF output (~332 lines)

Estimated total after extraction: ~550-600 lines, which exceeds the 500-line cap.

**Recommendation**: When executing T012, the SARIF static reference tables (Section 10b rule-to-category mapping, 10d level mapping, 10f default taxonomy JSON, 10g property bag field mapping) should be extracted to output-formatting.md or a new sarif-formatting.md reference file. This will reduce Section 10 from ~332 to ~150 lines (removal of ~180 lines of static tables/JSON blocks), bringing the agent within cap.

**Severity**: Non-blocking for P0. Must be addressed during T012 execution.

### CONCERN-2: SKILL.md loading table is not updated for new reference files

The SKILL.md at `.claude/skills/tachi-risk-scoring/SKILL.md` currently has a loading table with only 3 entries:

```
| Reference | File | Load When |
|-----------|------|-----------|
| Scoring Dimensions | references/scoring-dimensions.md | Entering exploitability, scalability, or reachability assessment phases (Sections 4-6) |
| CVSS Vectors | references/cvss-vectors.md | Entering CVSS 3.1 base scoring phase (Section 3) |
| Severity Bands | references/severity-bands.md | Entering composite calculation or governance field generation phases (Sections 7-8) |
```

The 3 new reference files (trust-zones.md, reachability-analysis.md, output-formatting.md) are missing from this table. Task T013 ("Update SKILL.md...add navigation entries for new reference files") is marked as not yet complete, which is correct -- it depends on T012. However, the risk-scorer agent's own navigation table (lines 24-30) also only lists 3 references.

**Impact**: Until both the SKILL.md and agent navigation tables are updated, the agent has no instruction to load the new reference files. The reference files exist but are not discoverable by the agent.

**Recommendation**: T013 must update both:
1. SKILL.md loading table -- add entries for trust-zones.md, reachability-analysis.md, output-formatting.md
2. Risk-scorer agent navigation table -- add the same 3 entries with load-when conditions

**Severity**: Non-blocking for P0 (T012/T013 are the next tasks). Must be addressed when T012/T013 execute.

---

## 3. Architecture Soundness

### Skill reference file organization -- PASS

The 6 reference files in `tachi-risk-scoring/references/` follow the pattern established by Feature 075:

| File | Lines | Purpose | Pattern Match |
|---|---|---|---|
| scoring-dimensions.md | 84 | Exploitability + scalability assessment | Existing (075) |
| cvss-vectors.md | 106 | CVSS base scoring + bounded scoring | Existing (075), enhanced |
| severity-bands.md | 211 | Composite formula + severity mapping + governance | Existing (075), enhanced |
| trust-zones.md | 173 | Trust zone extraction rules | New -- follows same pattern |
| reachability-analysis.md | 180 | Reachability scoring pipeline | New -- follows same pattern |
| output-formatting.md | 155 | Markdown output formatting specs | New -- follows same pattern |

Total: 909 lines across 6 reference files.

All files include consistent YAML frontmatter with `source_agent`, `extracted_from`, and `version` fields. The heading structure follows the agent's section numbering convention, which enables unambiguous cross-referencing.

### scoring-dimensions.md trim verification -- PASS

The file was correctly trimmed from 256 lines (pre-078) to 84 lines. The trimmed content:

- Retains: Exploitability assessment (sub-dimensions, AI-specific guidance) -- lines 13-43
- Retains: Scalability assessment (sub-dimensions, scoring examples) -- lines 47-79
- Removed: Full reachability analysis pipeline (relocated to reachability-analysis.md)
- Added: Line 83 -- pointer note: "Reachability analysis has been extracted to its own reference file: `reachability-analysis.md`"

The pointer note is good practice -- it prevents confusion if someone reads scoring-dimensions.md and expects to find reachability content there.

### YAML frontmatter consistency -- PASS

All 6 reference files use identical frontmatter structure:

```yaml
---
source_agent: risk-scorer
extracted_from: [origin file]
version: 1.0.0
---
```

The `extracted_from` field correctly distinguishes between files extracted from the agent itself vs. files extracted from the scoring-dimensions reference (reachability-analysis.md). This supports traceability per FR-011.

### Lazy loading pattern adherence -- PASS

The reference files are designed for on-demand loading via Read tool, consistent with the ADR-002 validated pattern from Feature 075. No file is auto-loaded; each is loaded at a specific workflow branch point. The loading table (once updated per CONCERN-2) will make load-when conditions explicit.

---

## 4. Baseline Adequacy

### Captured artifacts -- PASS

The baseline directory contains all required artifacts:

| Artifact | Present | Size |
|---|---|---|
| threats.md | Yes | 37,998 bytes |
| threats.sarif | Yes | 41,273 bytes |
| risk-scores.md | Yes | 75,837 bytes |
| risk-scores.sarif | Yes | 69,657 bytes |
| compensating-controls.md | Yes | 17,344 bytes |
| baseline-metrics.md | Yes | 4,052 bytes |
| line-counts.txt | Yes | 1,271 bytes |

### Metrics coverage -- PASS

The baseline-metrics.md captures:

- Finding count by STRIDE+AI category (8 categories, 38 raw findings)
- Severity distribution (Critical: 7, High: 15, Medium: 10, Low: 1)
- Deduplication accounting (38 raw to 33 deduplicated via 5 correlation groups)
- Section presence verification (all 7 standard sections)
- Correlation group details (5 groups with specific finding IDs)
- SARIF metrics (version, run count, results by rule and level)
- Regression comparison rules (5 specific criteria with tolerance bands)

### Regression comparison rules -- PASS

The 5 comparison rules in baseline-metrics.md are well-defined:

1. Finding count: >= 38 raw across 8 categories
2. Severity distribution: Critical + High >= 22
3. Section completeness: All 7 sections present
4. Correlation groups: >= 5 groups
5. SARIF compliance: Valid SARIF 2.1.0 with >= 33 results and 1 run

These criteria match the tolerances specified in spec.md SC-004 (within +/-2 for finding count, +/-1 per severity level).

**Observation**: The baseline includes risk-scores.md and compensating-controls.md, which are Phase 4 regression artifacts (T051-T053). Capturing them now alongside the threat model output is proactive and eliminates the need to regenerate later. Good planning.

---

## 5. Best Practices Alignment

### Tier caps -- PASS

The updated `_TACHI_AGENT_BEST_PRACTICES.md` correctly reflects:

| Tier | Target | Hard Cap | Previous Cap |
|---|---|---|---|
| Leaf | 100-150 | 200 | 300 |
| Report | 200-250 | 300 | 800 |
| Methodology | 350-450 | 500 | 1,000 |

### Compliance table accuracy -- PASS

All 17 agent line counts in the compliance table match the actual `wc -l` output captured in `line-counts.txt`. The +1 annotations for model field additions are correct. The "EXCEEDS" status for the 6 restructuring targets is accurate with current line counts.

### MEMORY.md clarification -- PASS

Section 2 (Hard Caps) includes the corrected note:

> The 200-line context limit cited in earlier research applies specifically to Claude Code's MEMORY.md index file, not to agent definition files.

This resolves the potential confusion identified in the spec.

### Lazy loading recommendation -- PASS

Section 4 (Skill Extraction Pattern) includes the loading strategy:

> Use lazy loading (Read tool on-demand at workflow branch points) rather than eager loading (skills: frontmatter auto-load). Lazy loading was validated in Feature 075 with 78% context reduction per ADR-002.

### Extracted Skills table -- NEEDS UPDATE (non-blocking)

The "Extracted Skills" table in Section 5 shows pre-Wave-2 line counts:

```
| tachi-risk-scoring | scoring-dimensions (256), cvss-vectors (74), severity-bands (195) | 525 | risk-scorer |
```

After Wave 2, the actual state is:

```
| tachi-risk-scoring | scoring-dimensions (84), cvss-vectors (106), severity-bands (211), trust-zones (173), reachability-analysis (180), output-formatting (155) | 909 | risk-scorer |
```

The table shows the pre-extraction file set. T006 updated the caps and research findings but did not update the Extracted Skills table to reflect T007-T011 additions.

**Recommendation**: Update the Extracted Skills table in _TACHI_AGENT_BEST_PRACTICES.md to include all 6 reference files with current line counts when T012/T013 complete. This is a documentation accuracy issue, not a functional concern.

**Severity**: Non-blocking. Can be addressed as part of T012/T013 or a separate documentation task.

---

## 6. Finding Summary

### Non-Blocking Concerns (2)

| # | Finding | Impact | Recommended Action | When |
|---|---|---|---|---|
| C-1 | SARIF output sections (10a-10j) contain ~180 lines of static reference tables that may prevent reaching 500-line cap | T012 may not achieve target without additional extraction | Extract SARIF static tables (rule mapping, level mapping, taxonomy JSON, property bag fields) to reference file during T012 | T012 execution |
| C-2 | SKILL.md and agent navigation table not yet updated for new reference files | Agent cannot discover new reference files until update | Update both tables in T013 (already planned but dependency noted) | T013 execution |

### Observations (non-actionable, informational)

| # | Observation |
|---|---|
| O-1 | T008 task description baseline values (8.5/6.0/3.0) differ from actual reference file values (9.0/5.5/2.5) -- reference file is correct |
| O-2 | Extracted Skills table in best practices shows pre-Wave-2 state -- will need update post-T012 |
| O-3 | agent-autonomy.md is at 201 lines (1 over cap) per architect-approved exception -- confirmed correct |
| O-4 | Baseline proactively includes risk-scores and compensating-controls files for Phase 4 regression |

---

## Decision

**STATUS: APPROVED_WITH_CONCERNS**

The Wave 1-2 deliverables are architecturally sound and the extraction quality is high. The 3 new reference files contain complete, accurate domain knowledge that will support the risk-scorer after restructuring. The baseline capture is comprehensive and the regression comparison rules are well-defined.

The two concerns (C-1 and C-2) are non-blocking for the P0 checkpoint but must be addressed during T012/T013 execution. C-1 in particular should be planned for proactively -- the SARIF static reference extraction is likely necessary to reach the 500-line target.

**Proceed to T012** (risk-scorer agent trimming) with awareness of CONCERN-1 (SARIF extraction may be needed) and CONCERN-2 (navigation table updates in T013).

---

**End of P0 Checkpoint Review**
