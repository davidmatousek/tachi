# Session Continuation: F-4 Claude Code Permissions Baseline (BLP-02 Wave 4)

**Generated**: 2026-05-09 (second handoff this branch)
**Branch**: `277-claude-permissions-baseline`
**Last Commit**: `381febe feat(277): claude permissions baseline — W6-W8 (T009-T016) + FR-003 .gitignore fix`
**Phase**: implement (16/30 tasks complete; resume at T017 in Wave 9)

---

## Completed This Session

- **`6f51c4a`** `chore(277): checkpoint before build resume` — auto-committed prior NEXT-SESSION.md handoff at /aod.build pre-flight
- **`ec0b628`** `docs(277): patch architect P1 Minor #1 + #2 — spec/plan/tasks reconciliation` — applied architect-recommended patches in this PR (eliminates contract↔implementation drift)
  - Minor #1: 13 surfaces of `jq -e empty` → `jq empty` across spec/plan/tasks. Rationale: `-e` flag inverts exit-code semantics for filters producing no output; `jq empty` is the correct JSON-validity gate.
  - Minor #2: codified refined AC-2 cross-check. Replaced whole-file grep (5 false-positive orphans from §5/§6/§7 illustrative examples) with awk section-marker extraction restricted to §4 + markdown-pipe unescape. Awk form chosen over sed line-range for forward stability against §4 table growth. Verified equivalent: 93↔93 EMPTY diff.
  - Minor #3 (ADR-041 195 LOC vs ~150 advisory) — accepted with PR-description note per architect recommendation.
- **`381febe`** `feat(277): claude permissions baseline — W6-W8 (T009-T016) + FR-003 .gitignore fix` — Waves 6-8 complete + new finding remediated in-PR
  - **W6 (US2 paired-P1 deny+ask interactive verification)**: T009 PASS live (`git status` auto-approved), T010 PASS live (`git push --force` deny — load-bearing cross-list precedence test), T011 + T012 PASS via static-presence (per user "spot-check T010 only" choice; full live enumeration deferred).
  - **W7 (US3 verification)**: T013 PASS-with-remediation — discovered FR-003 enforcement gap (project `.gitignore` did not list `.claude/settings.local.json`; only maintainer's global `~/.config/git/ignore` covered it; adopters without that pattern could accidentally commit personal overrides). Patched in-PR per user choice: appended `.claude/settings.local.json` to project `.gitignore:236` under "Claude Code adopter personal settings" section. PR scope expanded from 4 → 5 files. Plan §File-touch matrix + §CHANGELOG entry outline + tasks T017/T019/T020 updated. T014 PASS live — full 4-step CREATE → ATTEMPT → CONFIRM → REMOVE procedure; cross-file deny precedence empirically verified (project deny held despite competing local allow).
  - **W8 (US4 + US5 verification)**: T015 PASS (5/5 sub-checks: 7 sections in plan §D-2 order; §3 has both within-file + cross-file worked examples; §5 lists 12 built-ins + 7 read-only git forms; §6 has 3 paths; §7 has 5 sub-subsections including bonus §7.5). T016 PASS (deny=23, CLAUDE_PERMISSIONS.md present, ADR-041 Accepted with 6 alternatives).

---

## Current State

- **Phase**: implement
- **Tasks**: 16/30 complete (W1-W8). Remaining: T017-T028 (Waves 9-15) + T029-T030 (deferred to /aod.deliver).
- **Uncommitted**: clean (all committed)
- **PR scope**: 5 files (`.claude/settings.json`, `docs/standards/CLAUDE_PERMISSIONS.md`, `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md`, `CHANGELOG.md` (pending T017), `.gitignore` (FR-003 fix))
- **GitHub Issue**: #277 — should already be in `Build` board column from prior session
- **Triad sign-offs**: PM ✓ + Architect ✓ + Team-Lead ⚠ APPROVED_WITH_CONCERNS (recorded in tasks.md frontmatter)
- **P1 architect checkpoint**: APPROVED_WITH_CONCERNS — all 3 Minor reconciled in `ec0b628`

---

## Next Actions

### Wave 9 — Polish: CHANGELOG + AC-7 manual probe (T017-T018)

Both tasks marked `[P]` (independent surfaces). Execute in either order.

**T017** (automatable; senior-backend-engineer): Append CHANGELOG entry to `CHANGELOG.md` under `## Unreleased → ### Features` per FR-010 + plan §"`CHANGELOG.md` entry outline" + plan §D-4. Use the entry blueprint in plan §"`CHANGELOG.md` entry outline":
- Subsection header: `### Claude Code permissions baseline (BLP-02 F-4)`
- 4-bullet enumeration of artifacts (now 4, was 3 — `.gitignore` added in W7 remediation)
- Adopter migration paragraph (settings.local.json continues working for personal allows; baseline-deny override requires fork-and-edit)
- ADR-041 cross-reference + BLP-02 Wave 4 marker

**T018** (`[MANUAL-ONLY]`; tester): AC-7 subdomain-matching probe per FR-007 + plan §D-5. Pre-commit run. In current Claude Code session loaded with new `.claude/settings.json` (already loaded via `e368922` commit, verified by W6/W7 probes), attempt `WebFetch(api.github.com/repos/davidmatousek/tachi)`. Expected per Issues #15260/#11972/#1217: prompt surfaces (subdomain non-transitive matching). Both outcomes valid:
- (a) Prompt surfaces → record "AC-7 PASS — subdomain non-collapse confirmed"
- (b) Auto-approve → record "AC-7 ANOMALY — `WebFetch(domain:github.com)` matched `api.github.com`" + document in PR description as side observation; 19-domain explicit list MAY be reviewed for compaction in a follow-up Issue but does NOT block F-4

### Wave 10 — Stage + commit (T019)

Stage 5 files (now includes `.gitignore`) and commit on the branch with conventional-commit message starting `feat(277):`. Updated commit body in `tasks.md` T019 mentions the `.gitignore` patch + T013 build-stage discovery rationale. Verify via `git log --oneline -1` that the subject begins with `feat(277):` (release-please trigger).

### Wave 11 — Push + draft PR (T020)

`git push -u origin 277-claude-permissions-baseline && gh pr create --draft --title "feat(277): claude permissions baseline (BLP-02 F-4)" --body-file <heredoc>`. PR body now mentions `.gitignore` patch in Summary section. PR body Verification (pre-commit) checklist now has 10 items including new T013 entry. Capture PR# for downstream tasks.

### Wave 12 — PR ready (T021)

`gh pr ready <PR#>` once W6-W8 verifications + T017 CHANGELOG + T018 AC-7 probe outcome all green. Confirms `isDraft=false`. Gate C (all-pre-commit-verifications-green): blocking condition.

### Wave 13 — Squash-merge (T022)

`gh pr merge <PR#> --squash`. Verify squash subject retains `feat(277):` prefix per `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles (F-212 incident memory: a non-conventional subject silently skips release-please).

### Wave 14 — release-please verify + post-merge re-scan (T023-T024)

- T023: `gh pr list --state open --search "release-please" --limit 3` within ~30s of squash-merge. If empty, push empty release-marker commit per F-212 recovery flow inline (target version v4.34.0 if F-3 v4.33.0 has merged; v4.33.0 if F-3 still in flight).
- T024: `/security` re-scan post-merge (regression-only — no /security finding closed by F-4). Confirm `.aod/results/security-scan.md` records PASSED with no new HIGH/MEDIUM findings.

### Wave 15 — Defense-in-depth + follow-up Issues (T025-T028)

- T025-T026 `[MANUAL-ONLY]` `[P]`: re-run AC-6b (`git status` auto-approve) and AC-6c (`rm -rf` deny) on a fresh post-merge clone. Same Claude Code session, two operations.
- T027-T028 `[P]`: file AC-15 follow-up Issue (pre-commit hook for `jq empty` + AC-2 cross-check) and AC-16 follow-up Issue (CI integration for verification recipe). Note: T027 body already updated to reference `jq empty` (Minor #1 fix); T027 may also reference the awk-section-marker AC-2 form codified in this PR for the future hook to inherit.

### Wave (deferred) — `/aod.deliver`-time governance closure (T029-T030)

- T029: flip `docs/product/02_PRD/INDEX.md` row 277 status `Approved` → `Delivered` + append squash-merge PR link.
- T030: update `~/.claude/projects/-Users-david-Projects-tachi/memory/project_blp02_enterprise_hardening.md` to reflect Wave 4 → DELIVERED 4-of-5 + append F-4 closure date and PR link.

---

## Context Files

- **Sign-off artifacts** (Triad triple-approved + reconciled): `specs/277-claude-permissions-baseline/{spec.md,plan.md,tasks.md,agent-assignments.md}` — Minor #1 + #2 fixes applied in `ec0b628`; T009-T016 build-stage captures applied in `381febe`
- **Authored W2-W3 (committed `b4ac0fa`)**: `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md` (195 LOC, FR-008 advisory ceiling exceeded — accept with PR-description note per architect recommendation), `docs/standards/CLAUDE_PERMISSIONS.md` (289 LOC, within ceiling)
- **Authored W4 (committed `e368922`)**: `.claude/settings.json` rewrite (93 rules: 23 deny / 13 ask / 57 allow [Cat 1: 11 + Cat 2: 27 + Cat 4: 19])
- **Patched W7 (committed `381febe`)**: `.gitignore` (+6 LOC; line 236 adds `.claude/settings.local.json` for FR-003 enforcement)
- **Build-stage notes** (in tasks.md T001-T016 inline)
- **P1 architect review**: `.aod/results/architect.md` (APPROVED_WITH_CONCERNS, 3 Minor reconciled in this PR)

---

## Resume Command

```bash
claude "Resume F-4 Claude Code Permissions Baseline (branch: 277-claude-permissions-baseline). W1-W8 complete (16/30 tasks). Architect P1 Minor #1+#2 reconciled in PR (ec0b628); FR-003 enforcement gap fixed in PR (.gitignore patch — 381febe). Run /aod.build to continue from Wave 9 (T017 CHANGELOG entry + T018 [MANUAL-ONLY] AC-7 subdomain probe). Then W10 commit, W11 push+draft-PR, W12 PR ready, W13 squash-merge, W14 release-please verify + /security re-scan, W15 defense-in-depth + follow-up Issues."
```

Or simply:

```bash
/aod.build
```

— `/aod.build` will detect this NEXT-SESSION.md and confirm resume prerequisites before continuing.

---

## Known State of Open Decisions (none blocking)

- ADR-041 LOC (195 vs ~150 advisory) — accept with PR-description note per architect Minor #3 recommendation; not blocking. Trim would degrade SecOps audit value.
- T011/T012 partial live coverage — per user spot-check choice (T010 only ran live; T011/T012 PASS via static-presence). Architect P1 review treated T010 as load-bearing; T011/T012 rules are categorically aligned. Acceptable for Gate C; deferred full live enumeration NOT blocking merge.
- Nothing else open.
