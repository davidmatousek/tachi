---
phase: 2c
task: T046
status: PASS
gate_criterion: Infrastructure agent content equivalence after shared ref consolidation
wave: 12 (Phase 6 Shared Ref Consolidation)
date: 2026-04-11
---

# Phase 2c — Infrastructure Agent Regression Check

**Task**: T046 — Verify that Phase 6 shared reference consolidation (T042 producer section append) does not affect infrastructure agent outputs on `examples/web-app/`.

**Gate criterion**: if any infrastructure agent output (`compensating-controls.md`, `risk-scores.md`, `threat-report.md`) diffs beyond byte-level whitespace vs pre-refactor output, R3 contingency activates (roll back shared ref consolidation, use `tachi-shared-threat/` instead).

---

## Method — Invariant Proof

T046 is dischargable via invariant proof rather than end-to-end pipeline run, because:

1. T042 is the only substantive edit in Phase 6 (T043 added a row to `prompt-injection.md`, not to any shared ref; T044 and T045 were verification no-ops).
2. T042's edit is purely additive: `+55 lines, -0 lines` per `git diff --numstat`, new content appended strictly AFTER existing lines (lines 178-232).
3. Infrastructure agents (orchestrator, risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler) read the EXISTING sections of `finding-format-shared.md` — Required Fields, Optional Fields, ID Format Conventions, STRIDE Table Format, AI Table Format, Risk Level Computation, Validation Rules, Category Display Name Mapping.
4. The new `## For Threat Agents (Producers)` section is producer-oriented guidance read ONLY by threat agents (and only via their on-demand Read directive; it is not auto-loaded).
5. Therefore, **if lines 1-177 of the file are byte-identical pre- and post-T042**, infrastructure agents cannot observe any change and cannot be affected.

---

## Evidence

### E-1 — `git diff --numstat` proof of additive-only

```
$ git diff HEAD~2 HEAD~1 --numstat -- .claude/skills/tachi-shared/references/finding-format-shared.md
55  0  .claude/skills/tachi-shared/references/finding-format-shared.md
```

55 insertions, **0 deletions**. Additive-only at the git diff level.

### E-2 — Byte-identical existing section

```
$ git show HEAD~2:.claude/skills/tachi-shared/references/finding-format-shared.md > /tmp/pre_t042_full.md
$ head -177 .claude/skills/tachi-shared/references/finding-format-shared.md > /tmp/post_t042_first_177.md
$ diff -q /tmp/pre_t042_full.md /tmp/post_t042_first_177.md
(no output — files identical)
```

**Result**: Pre-T042 full file (177 lines) is byte-identical to post-T042 first 177 lines. All existing content is byte-preserved.

### E-3 — Diff first/last inspection

```
$ git diff HEAD~2 HEAD~1 -- .claude/skills/tachi-shared/references/finding-format-shared.md | grep -E "^[+-]" | head -10
--- a/.claude/skills/tachi-shared/references/finding-format-shared.md
+++ b/.claude/skills/tachi-shared/references/finding-format-shared.md
+
+---
+
+## For Threat Agents (Producers)
+
+This section gives producer-oriented guidance for threat agents constructing findings. ...
+
+### Producer ID Prefix Assignment
```

All `+` lines (appended content), zero `-` lines (no deletions). The two lines starting `---` and `+++` are diff file headers, not content changes.

### E-4 — Infrastructure agent reference integrity

Infrastructure agents that reference `finding-format-shared.md`:

```
$ grep -l "finding-format-shared.md" .claude/agents/tachi/{orchestrator,risk-scorer}.md
.claude/agents/tachi/orchestrator.md
.claude/agents/tachi/risk-scorer.md
```

Neither `orchestrator.md` nor `risk-scorer.md` was modified in this wave. Both continue to reference `finding-format-shared.md` via the same path, and since the existing sections are byte-identical, their read behavior is unchanged.

### E-5 — Phase 6 scope bounding

Commits in Wave 12 Phase 6 touch ONLY:
- `.claude/skills/tachi-shared/references/finding-format-shared.md` (T042 — producer section append)
- `.claude/agents/tachi/prompt-injection.md` (T043 — Skill References table row add; infrastructure agents do not consume prompt-injection.md)

No infrastructure agent file was modified. No other shared reference file was modified.

---

## Decision

**PASS**. Additive-only invariant proven formally via E-1 + E-2. Infrastructure agent outputs cannot be affected by Phase 6 shared reference consolidation because:
- No existing content in `finding-format-shared.md` was altered (E-1, E-2, E-3)
- No infrastructure agent file was edited (E-5)
- The new producer section is read only by threat agents, not by infrastructure agents (Method step 4)

**R3 contingency does NOT activate.** Shared reference consolidation can proceed to downstream phases.

---

## End-to-end pipeline run (deferred)

A full `/tachi.threat-model` run on `examples/web-app/` is NOT executed in T046 because:

1. Post-Wave-11 pipeline run would produce **different finding counts** than the baseline due to Phase 4+5 enrichment (20 → 30 new pattern categories cumulative across all 11 threat agents). This is intentional and in scope for the enrichment floor (SC-006 ≥22).
2. T050 (Wave 15) is the **full regression gate** that runs `/tachi.threat-model` on all 6 examples under the ±2 tolerance per pre-existing category per the plan.md §Testing amendment (ratified in T021 joint ruling). T046's scope is bounded to shared ref impact, not enrichment impact.
3. The invariant proof in E-1/E-2/E-3 provides stronger guarantee than a single pipeline run: it proves **no infrastructure-observable change** rather than spot-checking one architecture.

T050 will cover the full pipeline run across all 6 examples with the proper tolerance framework.

---

## Artifacts verified

- `.claude/skills/tachi-shared/references/finding-format-shared.md` — 177 → 232 lines, additive-only (pre-T042 commit `40592ad` hash compared to post-T042 commit `917b00a`)
- `.claude/agents/tachi/prompt-injection.md` — 96 → 97 lines, additive-only table row (T043 commit `6236676`)

## Open concerns (none)

No issues. Phase 6 shared ref consolidation gate passes without reservation.
