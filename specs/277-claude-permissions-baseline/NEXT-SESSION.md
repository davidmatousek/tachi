# Session Continuation: F-4 Claude Code Permissions Baseline (BLP-02 Wave 4)

**Generated**: 2026-05-09 (third handoff this branch)
**Branch**: `277-claude-permissions-baseline`
**Last Commit**: pending — committed at end of this handoff (`docs(277): NEXT-SESSION.md handoff after W9-W11 — resume at T021 (Wave 12)`)
**Previous Commit**: `998a128 feat(277): claude permissions baseline — W9 (T017 CHANGELOG + T018 AC-7 probe)`
**Phase**: implement (20/30 tasks complete; resume at T021 in Wave 12)
**Draft PR**: [#278](https://github.com/davidmatousek/tachi/pull/278) — OPEN, isDraft=true, mergeable=MERGEABLE

---

## Completed This Session (W9-W11)

- **`998a128`** `feat(277): claude permissions baseline — W9 (T017 CHANGELOG + T018 AC-7 probe)` — pre-commit work closed
  - **W9 T017**: senior-backend-engineer agent appended `### Claude Code permissions baseline (BLP-02 F-4)` subsection to `CHANGELOG.md` (line 72; 60 LOC; sibling to F-2/F-3 entries directly under `## Unreleased`, matching established BLP-02 multi-line cadence — NOT nested under the older `### Features` heading at line 125 per architect plan-stage observation about CHANGELOG section heading deviation). Entry shape: subsection header + 2-paragraph body + 4-bullet artifact enumeration (`.claude/settings.json` + CLAUDE_PERMISSIONS.md + ADR-041 + `.gitignore` W7 patch) + adopter migration paragraph + ADR-041 cross-reference + "BLP-02 Wave 4 of 5" marker.
  - **W9 T018**: AC-7 manual probe via live `WebFetch(https://api.github.com/repos/davidmatousek/tachi)` in current Claude Code session (loaded with new `.claude/settings.json`). Auto-approved (no prompt), returned `default_branch=main, stargazers_count=65`. **Outcome classified as PROBE-INCONCLUSIVE-FOR-TRANSITIVITY** (third outcome beyond T018's binary PASS/ANOMALY mapping) because `.permissions.allow[]` contains BOTH `WebFetch(domain:github.com)` AND `WebFetch(domain:api.github.com)` explicitly — the auto-approve almost certainly matched the explicit `api.github.com` rule under "first match wins", NOT subdomain transitive collapse. The 19-domain explicit list is doing its defensive job; T018's binary-ANOMALY branch (which would imply list compaction) is NOT supported. **See "Open Decisions" below for disambiguation options before T021 PR-ready.**
  - **W10 T019**: `git add` + `git commit` of W9 outputs. Commit `998a128` with subject `feat(277): claude permissions baseline — W9 (T017 CHANGELOG + T018 AC-7 probe)`. **Deviation from T019 strict wording**: T019 specified a single combined commit staging all 5 files; actual flow staged only W9 outputs (CHANGELOG.md + tasks.md) because the other 4 files (`.claude/settings.json`, `docs/standards/CLAUDE_PERMISSIONS.md`, `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md`, `.gitignore`) were already committed in W2-W3 (`b4ac0fa`), W4 (`e368922`), and W7 (`381febe`). Branch now has 4 `feat(277):` commits; T022 squash-merge to main will collapse all into a single commit with the canonical PR title as the subject — release-please trigger preserved.
  - **W11 T020**: `git push -u origin 277-claude-permissions-baseline` (4 commits ahead of main pushed). `gh pr create --draft` opened **PR #278**. **PR body refinements vs T020 strict template**: (a) added ADR-041 LOC note to Summary per architect P1 Minor #3 acceptance ("195 LOC vs FR-008 ~150 advisory ceiling — accepted with this note; trim would degrade SecOps audit value"); (b) refined AC-7 verification line to "PROBE-INCONCLUSIVE-FOR-TRANSITIVITY — see *Side observations* below"; (c) added new "Side observations (non-blocking)" section documenting AC-7 INCONCLUSIVE finding with mechanism explanation + suggested future probe target (`gist.github.com`, unlisted github subdomain) for definitive transitivity test; (d) added "Files in this PR (5)" enumeration. Verified PR state: title=`feat(277): claude permissions baseline (BLP-02 F-4)`, isDraft=true, state=OPEN, mergeable=MERGEABLE, URL=https://github.com/davidmatousek/tachi/pull/278.

- **(this commit)** `docs(277): NEXT-SESSION.md handoff after W9-W11 — resume at T021 (Wave 12)` — handoff + W10/W11 build-stage captures on tasks.md.

---

## Current State

- **Phase**: implement
- **Tasks**: 20/30 complete (W1-W11). Remaining: T021-T028 (Waves 12-15) + T029-T030 (deferred to /aod.deliver).
- **Uncommitted**: clean (this commit closes W9-W11; tasks.md captures all included)
- **PR scope**: 5 files (`.claude/settings.json`, `docs/standards/CLAUDE_PERMISSIONS.md`, `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md`, `CHANGELOG.md`, `.gitignore`)
- **GitHub Issue**: #277 — already in `Build` board column from W1
- **Triad sign-offs**: PM ✓ + Architect ✓ + Team-Lead ⚠ APPROVED_WITH_CONCERNS (recorded in tasks.md frontmatter)
- **P1 architect checkpoint**: APPROVED_WITH_CONCERNS — all 3 Minor reconciled in `ec0b628`
- **Branch state**: 4 commits ahead of main (b4ac0fa W2-W3, e368922 W4-W5, 381febe W6-W8, 998a128 W9). Squash-merge will collapse all into one feat(277) commit on main.

---

## Next Actions

### Wave 12 — PR ready (T021)

Per Gate C blocking condition (all-pre-commit-verifications-green), confirm:

- [x] T008 AC-2 cross-check PASS (recorded in tasks.md; awk section-marker form per architect P1 Minor #2)
- [x] T009 AC-6b `git status` auto-approve PASS (live)
- [x] T010 AC-6c `git push --force` deny PASS (live; load-bearing US-2 cross-list precedence probe)
- [x] T011 Tier-3a deny enumeration PASS (static-presence + T010 runtime-equivalence)
- [x] T012 Tier-3b ask enumeration PASS (static-presence)
- [x] T013 FR-003 `.claude/settings.local.json` gitignored (project + branch) PASS-with-remediation (W7 .gitignore patch in PR)
- [x] T014 AC-12 cross-file deny precedence PASS (live with full fixture-and-cleanup)
- [x] T015 US-4 sections + precedence + built-ins + opt-outs + limitations PASS (5/5 sub-checks)
- [x] T016 US-5 external-review rubric PASS (3/3 sub-checks)
- [x] T018 AC-7 probe outcome captured (INCONCLUSIVE; see Open Decisions)

All 10 verification items green. Run:

```bash
gh pr ready 278
gh pr view 278 --json isDraft  # confirm isDraft=false
```

Per `.claude/rules/git-workflow.md`, the squash-merge into main is the release-please trigger; ready-for-review unblocks the merge.

### Wave 13 — Squash-merge (T022)

```bash
gh pr merge 278 --squash
```

Verify the squash-commit subject on `main` retains the `feat(277):` prefix:

```bash
git checkout main && git pull --ff-only && git log --oneline -1
```

**F-212 incident memory**: a non-conventional commit subject silently skips release-please. The PR title `feat(277): claude permissions baseline (BLP-02 F-4)` already preserves the prefix; verify GitHub squash-merge inherits it.

### Wave 14 — release-please verify + post-merge re-scan (T023-T024)

- **T023**: Within ~30s of squash-merge, run:
  ```bash
  gh pr list --state open --search "release-please" --limit 3
  ```
  - Expected: a release-please PR opens targeting v4.34.0 (F-3 PR #274 already merged 2026-05-08, so latest released tag is v4.33.0 → next bump is v4.34.0).
  - **If empty**: push empty release-marker commit per F-212 recovery flow:
    ```bash
    git commit --allow-empty -m "feat(277): claude permissions baseline — release marker"
    git push origin main
    ```
    Then re-check release-please within ~30s.

- **T024**: Run `/security` re-scan post-merge per FR-014. Confirm `.aod/results/security-scan.md` records PASSED with no new HIGH/MEDIUM findings. F-4 does NOT close any pre-existing `/security` finding (it is posture-gap-closure, not vuln-closure); the re-scan is regression-only.

### Wave 15 — Defense-in-depth + follow-up Issues (T025-T028)

- **T025-T026** `[MANUAL-ONLY]` `[P]`: Re-run AC-6b (`git status` auto-approve) and AC-6c (`Bash(rm -rf:*)` deny prompt) on a fresh post-merge clone in a new Claude Code session loaded with the merged `.claude/settings.json`. Defense-in-depth — guards against squash-merge regressions beyond pre-commit T009/T010.

- **T027** `[P]`: File AC-15 follow-up Issue:
  ```bash
  gh issue create --title "[chore] Pre-commit hook for .claude/settings.json + CLAUDE_PERMISSIONS.md AC-2 cross-check (post-F-4 follow-up)" --body "Pre-commit hook running 'jq empty .claude/settings.json' + AC-2 cross-check (every non-built-in rule documented in CLAUDE_PERMISSIONS.md per-rule table) on edits touching either file. Origin: F-4 (PRD AC-15 nice-to-have, deferred at /aod.spec). Captures JSON-validity regressions and orphan-rule regressions before commit. Hook should inherit the awk-section-marker AC-2 form codified in PR #278 (architect P1 Minor #2 reconciliation in ec0b628). ICE rough estimate: I:5 C:7 E:8."
  ```

- **T028** `[P]`: File AC-16 follow-up Issue (CI integration for verification recipe — see tasks.md T028 body for canonical text).

### Wave (deferred) — `/aod.deliver`-time governance closure (T029-T030)

- T029: flip `docs/product/02_PRD/INDEX.md` row 277 status `Approved` → `Delivered` + append squash-merge PR link.
- T030: update `~/.claude/projects/-Users-david-Projects-tachi/memory/project_blp02_enterprise_hardening.md` to reflect Wave 4 → DELIVERED 4-of-5 + append F-4 closure date and PR link.

---

## Context Files

- **PR**: [#278](https://github.com/davidmatousek/tachi/pull/278) — draft; refined body with Side observations section
- **Sign-off artifacts** (Triad triple-approved + reconciled): `specs/277-claude-permissions-baseline/{spec.md,plan.md,tasks.md,agent-assignments.md}`
- **Authored W2-W3** (committed `b4ac0fa`): `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md` (195 LOC), `docs/standards/CLAUDE_PERMISSIONS.md` (289 LOC)
- **Authored W4** (committed `e368922`): `.claude/settings.json` (93 rules)
- **Patched W7** (committed `381febe`): `.gitignore` (FR-003 enforcement fix at line 236)
- **Authored W9** (committed `998a128`): `CHANGELOG.md` F-4 subsection (60 LOC, line 72)
- **Build-stage notes**: tasks.md T001-T020 inline
- **PR body** (for re-edit if needed): `/tmp/pr-body-277.md` (transient — regenerate from tasks.md T020 if needed; final canonical source is the GitHub PR description)
- **W9 T017 author trace**: `.aod/results/senior-backend-engineer.md`
- **P1 architect review**: `.aod/results/architect.md` (APPROVED_WITH_CONCERNS, 3 Minor reconciled)

---

## Resume Command

```bash
claude "Resume F-4 Claude Code Permissions Baseline (branch: 277-claude-permissions-baseline). W1-W11 complete (20/30 tasks). PR #278 OPEN draft mergeable. Run /aod.build to continue from Wave 12 (T021 gh pr ready). Then W13 squash-merge, W14 release-please verify + /security re-scan, W15 defense-in-depth + follow-up Issues. **Decide AC-7 disambiguation strategy** before T021 — see NEXT-SESSION.md Open Decisions (3 options)."
```

Or simply:

```bash
/aod.build
```

— `/aod.build` will detect this NEXT-SESSION.md and confirm resume prerequisites before continuing.

---

## Open Decisions (NON-BLOCKING but please decide before T021)

### D-1: AC-7 disambiguation strategy

W9 T018 probed `WebFetch(api.github.com/repos/davidmatousek/tachi)` and got auto-approve. The classification is INCONCLUSIVE because `.permissions.allow[]` contains BOTH `WebFetch(domain:github.com)` AND `WebFetch(domain:api.github.com)` explicitly. The auto-approve mechanism is ambiguous between "first match wins" on the explicit subdomain rule (likely) and subdomain transitive collapse on the parent rule (unlikely per upstream Issues #15260, #11972, #1217 — but possible if upstream behavior changed since those Issues were filed).

**Three options to resolve before T021** (PR description currently records INCONCLUSIVE):

- **Option A — Run disambiguation probe pre-merge** (5 minutes; conclusive):
  In a fresh Claude Code session, attempt `WebFetch(https://gist.github.com/...)` (an UNLISTED github subdomain). Result:
  - If auto-approves → subdomain transitive collapse IS happening → AC-7 ANOMALY confirmed; 19-domain list could be compacted in a follow-up Issue (T028 family).
  - If prompts → subdomain non-transitive matching CONFIRMED → AC-7 PASS; the 19-domain list is correctly defensive; INCONCLUSIVE classification was an artifact of the api.github.com URL choice.
  Update tasks.md T018 + PR #278 body Side observations section with conclusive finding before T021.

- **Option B — Accept INCONCLUSIVE + file follow-up Issue** (current state; punts to future):
  Keep the INCONCLUSIVE classification in PR #278 body. File a follow-up Issue tracking the disambiguation probe as a future task. PR merges with INCONCLUSIVE recorded; the 19-domain list stays unchanged.

- **Option C — Accept INCONCLUSIVE + don't file follow-up** (lowest-overhead):
  Keep INCONCLUSIVE in PR #278 body without a follow-up Issue. The PR description note serves as institutional memory for future revisits.

**Recommendation**: Option A. The cost is one tool call; the value is conclusive AC-7 finding before merge. Option B is acceptable; Option C leaves a documentation gap.

### D-2: ADR-041 LOC overage (already accepted)

ADR-041 LOC = 195 vs FR-008 ~150 advisory ceiling. Architect P1 Minor #3 review accepted with PR-description note. PR #278 Summary section now contains this note. **No further action needed** — recorded for traceability only.

### D-3: T011/T012 partial live coverage (already accepted)

Per user "Spot-check T010 only" choice during /aod.build Wave 6, T011/T012 PASS via static-presence rather than full live enumeration. Architect P1 review treated T010 as the load-bearing US-2 probe; T011/T012 rules are categorically aligned. **No further action needed** — recorded for traceability only.

---

## Wave Continuation Rationale

This session executed 3 waves (W9, W10, W11) in standalone mode, hitting the `/aod.build` 3-wave ceiling per the build skill wave continuation rule. Resume at Wave 12 in next session. Build skill protocol: "Stop and hand off if `orchestrated == false` AND this conversation has executed 3 or more waves." Last wave exception (proceed past ceiling on final wave) does NOT apply because W11 is not the final wave (4 more waves to go: W12 PR ready + W13 squash-merge + W14 release-please verify + W15 defense-in-depth).
