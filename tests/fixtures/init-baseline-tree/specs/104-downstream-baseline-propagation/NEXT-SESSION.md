# Session Continuation: Downstream Baseline Propagation

**Generated**: 2026-04-08 (mid-session)
**Branch**: 104-downstream-baseline-propagation
**Last Commit**: 4cda425 chore(main): release 4.3.4 (#106) (no feature commits yet — all changes uncommitted)

## Completed This Session

- **Wave 1 (T001-T003)**: Schema templates updated — Status column in Section 7, Section 8 Delta Summary in threats.md; schema v1.1 with baseline/delta fields in threat-report.md
- **Wave 2 (T004-T006, T008-T009)**: Shared parser extended with 3 functions (`parse_baseline_frontmatter`, `parse_resolved_findings`, delta_status in `parse_threats_findings`); threat-report agent v1.1 with delta-aware input/output contracts and Section 8 generation
- **QG1 (T007)**: Parser validation PASS — backward compatibility confirmed, delta-aware parsing confirmed
- **P0 Checkpoint**: Architect APPROVED_WITH_CONCERNS — 3 findings resolved (data-model baseline_run_id fix, Section 8 heading alignment, attack_tree_count clarification)
- **Wave 3 (T010-T015)**: Both extraction scripts import and use new parsers; infographic JSON includes delta_counts; report-data.typ includes baseline variables and resolved-findings; agent instructions and commands updated for delta context

## Current State

- **Phase**: implement
- **Uncommitted**: 12 modified files, 3 untracked (PRD, spec directory, run-state.json)
- **Tasks**: 15/18 complete

## Remaining Tasks (Wave 4 + Wave 5)

### Wave 4: End-to-End Validation (T016, T017 — parallel)
- [ ] T016: Primary validation — run baseline-compared threat model on second-brain-mcp (April 8 vs March 31 runs). Verify RESOLVED excluded from active counts, NEW highlighted, Section 8 present, delta counts in exec summaries across all three formats.
- [ ] T017: Regression validation — run threat model without baseline (first run on fresh architecture). Verify output identical to pre-104 behavior. No Section 8, no delta annotations, no resolved sections.

### Wave 5: Example Regeneration (T018)
- [ ] T018: Regenerate all 6 example outputs in `examples/` directory with delta-aware pipeline. Update Section 7 Status column, add Section 8 Delta Summary (where applicable), update threat-report.md to schema v1.1.

### Post-Wave: Final Validation + Security Scan
- Final validation (Step 5): architect + code-reviewer + security-analyst reviews
- Security scan (Step 6): `/security` skill on changed code files
- Completion report (Step 7)

## Files Changed (10 modified files)

### Python Scripts (3)
- `scripts/tachi_parsers.py` — 3 new/updated functions (parse_baseline_frontmatter, parse_resolved_findings, delta_status in parse_threats_findings)
- `scripts/extract-infographic-data.py` — imports + baseline detection + delta_counts + top_findings delta_status
- `scripts/extract-report-data.py` — imports + baseline/resolved parsing + delta Typst variables + delta_status in findings

### Agent Instructions (3)
- `agents/threat-report.md` — v1.1, input contract (Section 4b, baseline fields, delta_status), output (exec summary, annotations, attack trees, Section 8)
- `agents/threat-infographic.md` — delta_status in finding IR fields, baseline context, delta emphasis directives
- `.claude/agents/tachi/report-assembler.md` — delta/baseline awareness, rendering rules, resolved section

### Schema Templates (2)
- `templates/tachi/output-schemas/threats.md` — Section 7 Status column, Section 8 Delta Summary
- `templates/tachi/output-schemas/threat-report.md` — v1.1, baseline/delta_counts frontmatter, Section 5 guidance, Section 8

### Command Files (2)
- `.claude/commands/infographic.md` — delta context in agent prompt
- `.claude/commands/security-report.md` — delta counts in detection summary, baseline note in agent prompt

## Resume Command

```bash
claude "Resume Feature 104 (Downstream Baseline Propagation) implementation (branch: 104-downstream-baseline-propagation). Waves 1-3 complete (15/18 tasks). Run /aod.build to continue with Wave 4 (validation)."
```
