# Agent Assignments: Restore F-248/F-256 Substitution Hardening (#338)

**Feature**: #338 · BLP-06 Wave 2, F-2 · Branch `338-restore-substitution-hardening`
**Source**: team-lead feasibility plan (`feasibility-check.md`) + triple-sign-off review (`.aod/results/team-lead-tasks.md`).
**Wave model**: **single wave, no cross-agent parallelism** — one shared-context reconciliation against one CI oracle (team-lead). `[P]` markers below are intra-wave, disjoint-file parallelism only. Agent names are exact `subagent_type` values from the `.claude/agents/` roster.

## Agent Assignment Matrix

| Task | Description | Agent (`subagent_type`) | Rationale |
|------|-------------|-------------------------|-----------|
| T001 | Confirm restore preconditions + 5b64f68 SHA-content check | `senior-backend-engineer` | shell/git preconditions; same hand that performs the restore |
| T002 | Install pytest deps for local verification | `tester` | owns the test harness/runtime |
| T003 | Restore the 3 file bodies (`git checkout 5b64f68 -- …`) | `senior-backend-engineer` | bash hardening / shell tooling — core implementer |
| T004 | Restore canonical `defaults.env` key surface (FR-009, surgical) | `senior-backend-engineer` | same restore context; disjoint files from T003 (∥) |
| T005 | Verify restore (markers + exact-5-key set) | `senior-backend-engineer` | committer self-checks the restored tree before suite |
| T006 | Run F-248/F-256 gated suite (both-leg-equivalent) | `tester` | pytest execution + behavioral verification is the test surface |
| T007 | W-1 byte spot-check vs `5b64f68` `[MANUAL-ONLY]` | `tester` | independent parity verification of the restored bodies |
| T008 | SC-004 scope-fence audit `[MANUAL-ONLY]` | `senior-backend-engineer` | **commit-holder** does the restore-commit diff audit (team-lead OBS-1) |
| T009 | Deliver gate S-1 + merge to `main` (Conventional-Commit title) | `devops` | all merges-to-main go through devops (deployment policy) |
| T010 | Post-merge release-please verification | `devops` | release/CI ownership |

> **Architect**: discharged at `/aod.plan` (cut-line ratification OQ-1/2/3, MEDIUM-3, LOW-3). Not assigned a build task.

## Execution Wave (single wave — ordered handoffs)

```
Wave 1 (the only wave)
  ├─ Setup        : T001 (SBE) ∥ T002 (tester)
  ├─ Restore      : T003 (SBE) ∥ T004 (SBE)        ← disjoint files
  ├─ Verify       : T005 (SBE) → T006 (tester)
  ├─ Acceptance   : T007 (tester) ∥ T008 (SBE)
  └─ Deliver      : T009 (devops) → T010 (devops)
```

**Critical path**: T001/T002 → T003∥T004 → T005 → T006 → T007∥T008 → T009 → T010.

## Quality Gates (within the wave)

| Gate | After | Condition to pass |
|------|-------|-------------------|
| G1 — restore integrity | T005 | hardening markers present; every pack's `defaults.env` key set == canonical 5 |
| G2 — behavioral green | T006 | gated suite green both legs (canary, defaults_env 5/5, clone-timeout, adversarial); baseline xfail |
| G3 — parity + scope | T007, T008 | 3 bodies byte-match `5b64f68`; restore commit touches only the 8 in-scope paths; out-of-scope deltas (incl. package.json #336) named in FR-008 |
| G4 — deliver (S-1) | T009 | **no push/PR until G2 green locally**; merge via devops; Conventional-Commit title |
| G5 — release | T010 | release-please PR opened (or empty release-marker pushed) |

## Time Estimate

| Band | Eng-days | Scenario |
|------|----------|----------|
| Floor | 1 | clean revert, suite green first try, no surprises |
| Plan (realistic) | 2 | one CI iteration to converge both legs + W-1/SC-004 audits |
| Ceiling | 3 | bash-3.2 surprise or SC-004 accounting forces a second iteration |

Single Plan→Build→Deliver cycle; do not split (team-lead). No agent overload — sequential handoffs, no contention.
