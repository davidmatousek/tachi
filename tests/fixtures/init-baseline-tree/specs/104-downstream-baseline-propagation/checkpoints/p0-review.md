# P0 Checkpoint Review: Downstream Baseline Propagation

**Reviewer**: Architect
**Date**: 2026-04-08
**Status**: APPROVED_WITH_CONCERNS
**Scope**: Waves 1-2 (T001-T009), QG1 validation

---

## Summary

Waves 1-2 deliver the foundational schema and parser layer plus the threat-report agent delta instructions. The implementation is architecturally sound: the delta-driven branching pattern is consistent with Feature 074, backward compatibility is properly guarded, and the component boundaries are clean. Three concerns are noted -- one medium that should be resolved before Wave 5 integration, two low that can be addressed during validation.

---

## Findings

### Finding 1 (MEDIUM): baseline_run_id not extracted by parse_threats_findings -- data-model inconsistency

**Location**: `scripts/tachi_parsers.py` (parse_threats_findings), `specs/104-downstream-baseline-propagation/data-model.md` line 41

**Issue**: The data-model.md documents `baseline_run_id` as a key in the `parse_threats_findings()` output dict (sourced from a "Baseline Run ID" column). However:
- The Section 7 table in `templates/tachi/output-schemas/threats.md` does NOT include a "Baseline Run ID" column -- it only has `Finding ID | Status | Component | Threat | Risk Level | Mitigation`.
- The parser does NOT extract `baseline_run_id`.
- The threat-report agent input contract (line 89) lists `baseline_run_id` as a per-finding field consumed from the STRIDE/AI tables.

The tasks.md Architect sign-off noted this as a "medium concern: baseline_run_id source path inconsistency between data-model and tasks -- resolve during T004/T006 implementation." The implementation correctly chose NOT to add a Baseline Run ID column to Section 7 (which would have been wasteful since the run_id is constant across all findings and available from frontmatter). However, the data-model.md was not updated to reflect this decision.

**Impact**: The data-model.md states a contract that the parser does not fulfill. If a downstream consumer in Waves 3-5 codes against the data-model expecting `baseline_run_id` per finding, they will get KeyError or silent omission. The threat-report agent references `baseline_run_id` per finding but correctly sources it from frontmatter rather than per-finding parsing.

**Resolution**: Update `data-model.md` to remove `baseline_run_id` from the "Finding Dict" table (or mark it as "not extracted -- use parse_baseline_frontmatter().run_id instead"). This should be resolved before Waves 3-5 begin, as the extraction scripts will code against this data model.

**Severity**: MEDIUM -- downstream consumers may implement against incorrect contract.

---

### Finding 2 (LOW): Threat-report agent Section 8 sub-headings differ between schema template and agent instructions

**Location**: `templates/tachi/output-schemas/threat-report.md` Section 8, `agents/threat-report.md` Section 8 generation methodology

**Issue**: Minor heading inconsistency:
- Schema template uses: `### Finding Lifecycle Breakdown`, `### Remediation Progress`, `### Baseline Reference`
- Agent instructions use: `**8.1 Finding Lifecycle Breakdown**`, `**8.2 Remediation Progress**`, `**8.3 Baseline Reference**`

The agent uses numbered bold text (8.1, 8.2, 8.3) while the schema template uses H3 headings without numbering. Both the threats.md schema template (Section 8) and the threat-report.md schema template use unnumbered H3 headings.

**Impact**: The agent may produce output with numbered sub-headings (8.1, 8.2, 8.3) that do not match the canonical schema template structure. This is cosmetic but could cause confusion for automated parsers that look for exact heading text.

**Resolution**: Align the agent instructions to use the same heading format as the schema template (unnumbered H3 headings). Minor fix during T009 refinement or Wave 4 polish.

**Severity**: LOW -- cosmetic inconsistency, no functional impact.

---

### Finding 3 (LOW): attack_tree_count in threat-report frontmatter may not account for UNCHANGED findings skipped

**Location**: `templates/tachi/output-schemas/threat-report.md` frontmatter field table

**Issue**: The `attack_tree_count` field is defined as "Number of Mermaid attack trees generated (one per Critical and High finding)." With delta-aware behavior, UNCHANGED Critical/High findings do NOT get attack trees generated (they get a carry-forward note instead). The field description does not clarify whether `attack_tree_count` reflects:
- (a) Total Critical+High findings (potential trees), or
- (b) Actually generated trees (excluding UNCHANGED carry-forwards)

**Impact**: Minor ambiguity. The threat-report agent may produce inconsistent counts depending on interpretation. If `attack_tree_count = 8` but only 5 trees were actually generated (3 UNCHANGED), a consumer checking tree file count against frontmatter would see a mismatch.

**Resolution**: Clarify the field description in the threat-report.md schema template. Recommend interpretation (b): "Number of attack trees actually generated (excludes UNCHANGED findings with carry-forward notes)." This aligns with the physical artifact count.

**Severity**: LOW -- ambiguity that can cause minor confusion, not a blocking issue.

---

## Architecture Assessment

### Backward Compatibility: PASS

All delta logic in `tachi_parsers.py` is properly guarded:
- `parse_threats_findings()`: Status column extraction uses `row.get("Status", "").strip()` with an `if status:` guard -- findings without the Status column produce identical output to pre-104 behavior.
- `parse_resolved_findings()`: Returns empty list when Section 4b is absent.
- `parse_baseline_frontmatter()`: Returns all-None dict when no baseline block exists.
- Code-fenced frontmatter support added to `parse_baseline_frontmatter()` (matching `parse_frontmatter()` pattern) -- good defensive coding.

### Schema Template Design: PASS

- Section 7 Status column placement is correct (`Finding ID | Status | Component | ...`) -- Status is the second column, which reads naturally and keeps Finding ID as the primary key.
- Section 8 structure in threats.md schema matches the threat-report.md schema (Finding Lifecycle table + Baseline Reference table).
- Status column documentation includes the "baseline-aware mode only" qualifier and explains that RESOLVED findings do not appear in Section 7.
- Schema version bumped correctly (threat-report.md 1.0 -> 1.1; threats.md stays at 1.2 since it was already updated by Feature 074).

### Delta Pattern Consistency with Feature 074: PASS

- The same four delta_status values (NEW, UNCHANGED, UPDATED, RESOLVED) are used consistently with `schemas/finding.yaml` v1.2.
- Baseline presence detection uses `baseline.source != null` as the primary gate, matching the ADR-018 pattern.
- Backward compatibility approach (additive fields, presence checks) matches the Feature 074 pattern in risk-scorer and control-analyzer.

### Threat-Report Agent Instructions: PASS

- Input contract correctly documents Section 4b, Status column in Sections 3/4/7, and baseline frontmatter fields.
- Output instructions cover all four delta branching paths (NEW, UPDATED, UNCHANGED, RESOLVED) for attack trees, executive summary, threat analysis narrative, and Section 8.
- No-baseline guard is explicitly documented: "When baseline.source is null, omit Section 8 entirely, generate all attack trees fresh, no delta annotations."
- Validation checklist updated to include Section 8 presence/absence check.

### Readiness for Waves 3-5: PASS WITH CAVEAT

The parser functions provide a clean API for downstream consumers:
- `parse_threats_findings()` -> findings with optional `delta_status`
- `parse_resolved_findings()` -> resolved findings from Section 4b
- `parse_baseline_frontmatter()` -> baseline metadata dict

**Caveat**: Finding 1 (baseline_run_id data-model inconsistency) should be resolved before extraction script work begins to prevent misimplementation.

---

## Verdict

**STATUS: APPROVED_WITH_CONCERNS**

The Waves 1-2 implementation is architecturally sound and ready for downstream consumer work. The medium-severity data-model inconsistency (Finding 1) should be resolved before Waves 3-5 extraction script implementation begins. The two low-severity findings can be addressed during validation or polish.
