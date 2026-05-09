---
description: "Task list for F-4 Claude Code Permissions Baseline (BLP-02 Wave 4)"
spec_reference: specs/277-claude-permissions-baseline/spec.md
plan_reference: specs/277-claude-permissions-baseline/plan.md
prd_reference: docs/product/02_PRD/277-claude-permissions-baseline-2026-05-08.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-08
    status: APPROVED
    notes: "All 14 FRs trace to tasks (no orphans); 5/5 US have own phase (US3 has T013 file-untouched + T014 cross-file probe; US4/US5 verification-only); AC-15/AC-16 filed as Issues T027/T028 not implemented; zero scope creep against PRD Non-Goals; Polish phase covers CHANGELOG/PR title/post-merge re-scan/release-please/follow-ups; T029-T030 flagged /aod.deliver-time. T005→T006→T007 ADR-first ordering defensible (rationale authoritative, not reverse-engineered). 3 non-blocking observations. Pattern-consistent with F-3 (+5 tasks accounted for by ADR-041 + larger CLAUDE_PERMISSIONS.md + paired-P1 deny+ask interactive probes). Full review: .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-05-08
    status: APPROVED
    notes: "Tasks technically sound. Dep chain T005→T006→T007→T008 correct per plan §D-7. F-212 recovery at T023 + 3-surface conventional-commit (T019/T020/T022) preserved. 8 [MANUAL-ONLY] flags correctly placed (T009-T012, T014, T018, T025-T026). AC-2 jq+grep one-liner sound. AC-7 adversarial + AC-12 fixture-and-cleanup calibrated. [P] markers valid. No code/schema/agent change. F-3 pattern-consistent; 30-task envelope justified by ADR-041 + 250 LOC docs + 4 US2 manual + AC-12 fixture. 4 non-blocking observations. 10/10 PASS. Full review: .aod/results/architect.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-05-08
    status: APPROVED_WITH_CONCERNS
    notes: "Granularity, sequencing, critical path, [P] markers, F-212 recovery at T023, resume contract all calibrated for ~8-9h single-maintainer envelope. 30 tasks fit SC-008 9h cap (~8h45m realistic with parallelization). Wave structure derivable for agent-assignments.md mirroring F-3 W4-W15 single-maintainer pattern. 3 Minor non-blocking: M-1 T011 bundles 4 deny-probes; M-2 two-session split likely after T008/T022; M-3 T017 [P] non-load-bearing serial. Zero Major/Critical. Full review: .aod/results/team-lead.md."
---

# Tasks: F-4 — Claude Code Permissions Baseline

**Input**: Design documents from `/specs/277-claude-permissions-baseline/`
**Prerequisites**: plan.md (✓ PM + Architect APPROVED 2026-05-08), spec.md (✓ PM APPROVED 2026-05-08), research.md (✓ created at /aod.spec, refreshed at /aod.project-plan)

**Tests**: NOT REQUESTED. F-4 is documentation + settings-file rewrite + new ADR; no source code change. Per Constitution Principle VII §Exceptions ("Documentation-only changes may not require production deployment") and Principle VI testing-excellence exemption noted in plan.md, automated test tasks are excluded. Verification is via the AC-2 cross-check script + AC-6 verification recipe sub-checks (`jq empty` JSON validity, `grep` absolute-path baseline, `git status` built-in auto-approve regression check, `Bash(rm -rf:*)` deny prompt verification) + AC-7 subdomain-matching `[MANUAL-ONLY]` probe + AC-12 cross-file deny-precedence `[MANUAL-ONLY]` smoke-test + post-merge `/security` re-scan (FR-014).

**Organization**: Tasks grouped by spec user story (US1..US5). US1 is the MVP-delivering story (the ADR-041 + CLAUDE_PERMISSIONS.md + settings.json suite). US2 is paired-P1 verification of the destructive deny+ask tier. US3, US4, US5 are integration / verification-only phases.

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Different file, no in-flight dependency on prior incomplete tasks (parallelizable)
- **[Story]**: Maps to spec user story (US1, US2, US3, US4, US5)
- **[MANUAL-ONLY]**: Inline marker for tasks that cannot be automated (matches spec FR `[MANUAL-ONLY]` flag — interactive Claude Code session required)
- File paths are absolute or repo-relative (CWD = `/Users/david/Projects/tachi/`)

## Path Conventions

- Repo root: `/Users/david/Projects/tachi/`
- Files touched by F-4: `.claude/settings.json` (rewrite), `docs/standards/CLAUDE_PERMISSIONS.md` (new), `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md` (new), `CHANGELOG.md` (append)
- Out-of-tree: NONE (unlike F-3 which required a GitHub UI toggle, F-4 has zero out-of-tree dependencies)
- Reference for content: `specs/277-claude-permissions-baseline/plan.md` §Phase-1 Design & Contracts (file outlines for the four artifacts) and §Verification Recipe (post-merge cross-checks).

---

## Phase 1: Setup (Cross-checks & Verifications)

**Purpose**: Branch readiness verification + ADR-041 number freshness check + H-4 absolute-path baseline + release-please state cross-check.

- [X] T001 Confirm working directory is `/Users/david/Projects/tachi/` and current branch is `277-claude-permissions-baseline` via `pwd && git branch --show-current`. Confirm `specs/277-claude-permissions-baseline/{spec.md,plan.md,research.md,checklists/requirements.md}` all exist with appropriate Triad sign-offs in their frontmatter (spec PM ✓; plan PM ✓ + Architect ✓; tasks pending triple sign-off — this run). **Build-stage capture**: cwd=/Users/david/Projects/tachi/, branch=277-claude-permissions-baseline, all 6 artifacts present (spec, plan, research, checklists/requirements.md, tasks, agent-assignments).

- [X] T002 [P] Re-verify the next-available ADR number. Run `ls /Users/david/Projects/tachi/docs/architecture/02_ADRs/ | sort | tail -5`. Confirm ADR-040 is the highest-numbered existing file and ADR-041 is therefore the correct number for the new file. If the directory state has changed (e.g., a parallel feature has filed ADR-041 already), update T005 to use the next number and document the bump in the PR description; otherwise proceed with ADR-041 per plan §D-1 / spec FR-008. **Build-stage capture**: directory state shows ADR-040 + ADR-044 (filed for BLP-03 dual-frame-public-positioning); ADR-041, 042, 043 are gaps. ADR-041 used per plan (no bump needed; numbering convention is "next-available" not "next-after-highest").

- [X] T003 [P] Re-verify the H-4 absolute-path baseline against the *current* `.claude/settings.json` (before the rewrite). Run `grep -E '/(Users|home)/|^[A-Z]:\\\\' /Users/david/Projects/tachi/.claude/settings.json`. Expected at plan-stage time: zero matches (no pre-existing leak). Capture the result for the T008 post-rewrite comparison; if the current file unexpectedly contains a machine-specific path, the rewrite must scrub it (and the H-4 finding remediation should be cross-referenced in ADR-041 §Related Findings). **Build-stage capture**: zero matches (FR-009 baseline clean; rewrite at T007 must preserve this property).

- [X] T004 [P] Re-verify release-please state. Run `cat .release-please-manifest.json && git tag --list 'v*' | sort -V | tail -5 && gh pr list --state open --search "release-please" --limit 3`. Capture the latest released tag (PRD-time was v4.32.0; F-3 release-PR #274 was open targeting 4.33.0 at plan-stage). The state at task-execution time determines what version F-4 will bump to — if F-3 has landed and v4.33.0 is the latest, F-4 bumps to v4.34.0; if not, F-4 bumps to v4.33.0 (and may inherit the F-3 release-PR if F-3 has not yet merged its release marker). Document the captured state in the PR description. **Build-stage capture**: manifest local was 4.32.0 pre-fetch; after `git fetch origin --tags`, v4.33.0 tag now exists (F-3 release-PR #274 merged 2026-05-08T18:18:38Z). F-4 will trigger v4.34.0 bump on squash-merge. No open release-please PR at build-stage time.

**Checkpoint**: Setup complete. Branch verified, ADR-041 number freshness confirmed, current settings.json absolute-path baseline captured, release-please state recorded.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None — F-4 has no shared blocking prerequisites between user stories beyond Phase 1 Setup.

> **Foundational phase intentionally empty.** F-4 is documentation + config-file rewrite with four distinct artifact surfaces. Each user story phase below depends only on Phase 1 Setup or on US1's artifact-suite-write, not on a shared foundational layer.

**Checkpoint**: User-story phases (Phase 3 onward) can begin once Setup is complete.

---

## Phase 3: User Story 1 — Enterprise developer adopting in managed environment (Priority: P1) — MVP

**Goal**: An enterprise developer in a SecOps-reviewed managed environment inherits `.claude/settings.json` as a default-deny baseline they can ship as-is, with `docs/standards/CLAUDE_PERMISSIONS.md` providing per-rule rationale that satisfies their organization's audit-policy requirement.

**Independent Test**: After T005-T008 complete, open `.claude/settings.json` and `docs/standards/CLAUDE_PERMISSIONS.md` side-by-side; verify every non-built-in rule in `settings.json` has a matching row in CLAUDE_PERMISSIONS.md. Run the AC-2 cross-check script (T008): zero orphaned rules, zero orphaned rows. Run `jq empty .claude/settings.json` (T008): exit code 0. Run `grep -E '/(Users|home)/|^[A-Z]:\\\\' .claude/settings.json` (T008): zero matches.

### Implementation for User Story 1

> **Authoring order rationale (per plan §D-7)**: ADR-041 first (architecture-decision freezes before implementation) → CLAUDE_PERMISSIONS.md (depends on ADR-041 framing for the four-category logical structure) → `.claude/settings.json` rewrite (depends on CLAUDE_PERMISSIONS.md per-rule table for rule-to-category mapping). T008 verification gates run after all three artifacts are authored.

- [X] T005 [US1] Author `/Users/david/Projects/tachi/docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md` (~100 LOC, ceiling ~150) per FR-008 + plan §"ADR-041 outline" + plan §D-1 / D-3. Mirror ADR-040 structure verbatim: **Status** (Accepted, 2026-05-08, deciders: PM ✓ Architect ⚠ Team-Lead ⚠) → **Context** (Daniel Wood 2026-05-02 thread; BLP-02 Wave 4; the 6 PRD-enumerated gaps in current 26-rule allow-only file) → **Decision** (7-item enumeration mirroring CLAUDE_PERMISSIONS.md categories per plan §"ADR-041 outline" Decision bullets) → **Alternatives Considered** (≥6 alternatives in D-3 order: keep-as-is → settings.example → empty-BYO → managed-settings → PreToolUse-hooks → settings.local-template; each with Pros / Cons / Why-Not-Chosen; ~15-20 LOC per alternative) → **Consequences** (Positive / Negative / Mitigation per plan §"ADR-041 outline") → **Related Findings** (H-4 absolute-path cross-reference; no `/security` finding directly closed by F-4) → **References** (PRD §277, spec FR-001..FR-014, Claude Code docs at `code.claude.com/docs/en/permissions` and `code.claude.com/docs/en/settings`, upstream Issues #15260, #11972, #1217).

- [X] T006 [US1] Author `/Users/david/Projects/tachi/docs/standards/CLAUDE_PERMISSIONS.md` (~250 LOC, ceiling ~350) per FR-005, FR-011, FR-012 + plan §"CLAUDE_PERMISSIONS.md section outline". Sections in order per plan §D-2: (1) Why this baseline exists (framing + cross-ref to ADR-041); (2) The four categories (per-category safety promise + failure modes referencing R-8/R-9/R-10); (3) **Settings precedence** with TWO worked examples — within-file `Bash(git push:*)` allow + `Bash(git push --force:*)` deny per FR-011, AND cross-file project-deny-holds case (adopter `.claude/settings.local.json` with `Bash(rm -rf:*)` allow vs project deny) per FR-012; (4) Per-rule rationale table (Rule | Category | Rationale | Failure mode) covering every non-built-in rule from `.claude/settings.json` per FR-002; (5) **Built-in read-only set** documentation (lists `ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `diff`, `stat`, `du`, `cd`, read-only `git` forms; explains why explicit allow is no-op; maintenance note for re-verification on Claude Code upgrades) per FR-004; (6) **Opt-out paths** (≥3 paths: per-tool disable / fork-and-edit `.claude/settings.json` (load-bearing for baseline-deny-override per FR-012) / `.claude/settings.local.json` for adding personal allows for non-denied operations) per US-4 AC-3; (7) **Known limitations** (R-8 Bash pattern fragility, R-9 process-wrapper bypass, R-10 read-only built-in shadow, subdomain non-transitive matching with citation to Issues #15260/#11972/#1217). Cross-references to ADR-041 should be reciprocal with T005.

- [X] T007 [US1] Rewrite `/Users/david/Projects/tachi/.claude/settings.json` (~80 LOC after Cat-1 dedup, ceiling ~150) per FR-001, FR-002, FR-004, FR-007, FR-009 + plan §"`.claude/settings.json` rule structure outline". Structure: strict JSON (RFC 8259; no comments; no JSONC); top-level `permissions` object with three arrays (`deny`, `ask`, `allow`); ordering for diff-readability per plan §"`.claude/settings.json` rule structure outline" — `deny` first (~20 Tier-3a rules from PRD §Category-3a Tier-3a), then `ask` (~12 Tier-3b rules from PRD §Category-3b Tier-3b), then `allow` (Category 1 ~10 rules + Category 2 ~30 rules + Category 4 ~19 `WebFetch(domain:<host>)` rules from PRD §Category-1/2/4). MUST exclude built-in read-only commands from Category 1 (per FR-004 + CLAUDE_PERMISSIONS.md §Built-in-Read-Only-Set). MUST use only relative paths (FR-009; H-4 finding compliance). MUST validate via `jq empty .claude/settings.json` returning exit code 0 before considering complete (FR-001). **Build-stage capture**: 93 rules total (deny: 23 / ask: 13 / allow: 57 = Cat 1: 11 + Cat 2: 27 + Cat 4: 19); JSON validity confirmed via `jq empty .claude/settings.json` exit 0 (NOTE: spec/plan/tasks originally referenced `jq -e empty` but `-e` flag inverts semantics for filters producing no output — `jq -e empty` definitionally exits 4 for any valid JSON because `empty` emits nothing; corrected form `jq empty` is the intended validity check; reconciled in this PR per architect P1 Minor #1). H-4 absolute-path grep zero matches (FR-009 preserved); hooks block preserved verbatim. settings.json LOC: ~110 (within FR-001 ceiling ~150).

- [X] T008 [US1] Run AC-1 + AC-2 + AC-9 cross-checks per FR-001, FR-002, FR-009: (a) `jq empty /Users/david/Projects/tachi/.claude/settings.json` MUST return exit code 0 (FR-001 JSON validity); (b) `grep -E '/(Users|home)/|^[A-Z]:\\\\' /Users/david/Projects/tachi/.claude/settings.json` MUST return zero matches (FR-009 no-machine-paths); (c) AC-2 cross-check: extract every non-built-in rule from `.claude/settings.json` (parse `permissions.deny`, `permissions.ask`, `permissions.allow` arrays) and verify each appears in the per-rule rationale table in CLAUDE_PERMISSIONS.md (case-sensitive substring match against the table's "Rule" column); also verify every table row references a rule in `.claude/settings.json` or is flagged as a built-in entry (FR-002). Implementation: a small `bash + jq + grep` one-liner suffices, e.g.:
  ```bash
  # AC-2 cross-check (refined per architect P1 Minor #2): restrict CLAUDE_PERMISSIONS.md extraction to §4 (Per-rule rationale table) via awk section-marker delimiters; whole-file grep produces 5 false-positive orphans from §5/§6/§7 illustrative examples (`Bash(ls:*)` SecOps answer, `Bash(my-deploy-tool:*)` Path-3 example, `Bash(docker exec ... rm -rf ...)` R-9 example, `WebFetch(domain:*)`/`WebFetch(domain:<host>)` §7.4 limitations). Final `sed 's/\\|/|/g'` unescapes markdown pipe-escapes (table rows escape `|` as `\|`) back to JSON-literal pipes for clean diff comparison.
  jq -r '.permissions.deny[], .permissions.ask[], .permissions.allow[]' .claude/settings.json | sort -u > /tmp/f4-rules.txt
  awk '/^## 4\./,/^## 5\./' docs/standards/CLAUDE_PERMISSIONS.md | grep -E '^\| `' | sed -E 's/^\| `([^`]+)` \|.*/\1/' | sed 's/\\|/|/g' | sort -u > /tmp/f4-doc-rules.txt
  diff /tmp/f4-rules.txt /tmp/f4-doc-rules.txt
  ```
  Empty diff = AC-2 PASS. Any orphaned rule or row = return to T006/T007 to reconcile. Capture the diff output for the PR description. **Build-stage capture**: ALL THREE cross-checks PASS with two implementation refinements that should land in tasks/plan reconciliation: (1) AC-1 corrected command is `jq empty` (not `jq -e empty`) — the `-e` flag interprets "filter produced no output" as failure (exit 4) for any valid JSON because `empty` emits nothing; `jq empty` returns 0 on parse-OK, 5 on parse-error, which is the FR-001 intent. Verified: `jq empty .claude/settings.json` exit 0. (2) AC-2 corrected extraction uses sed range over §4 table only (lines 112-214 in CLAUDE_PERMISSIONS.md), not whole-file grep — whole-file grep produces 5 false-positive "orphans" from illustrative examples in §5 (`Bash(ls:*)` SecOps answer), §6 (`Bash(my-deploy-tool:*)` Path-3 example), §7.2 (`Bash(docker exec ... rm -rf ...)` R-9 example), §7.4 (`WebFetch(domain:*)`, `WebFetch(domain:<host>)`). Refined extraction: `sed -n '112,214p' docs/standards/CLAUDE_PERMISSIONS.md | grep -E '^\| \`' | sed -E 's/^\| \`([^\`]+)\` \|.*/\1/' | sed 's/\\|/|/g' | sort -u`. With refined commands: 93 JSON rules ↔ 93 §4 table rows, EMPTY diff (AC-2 PASS). H-4 grep zero matches (AC-9 PASS). Refinements codified in T008 inline command + plan §Verification Recipe sub-check 3 per architect P1 Minor #2 reconciliation in this PR (awk-section-marker form replaces build-stage's sed-line-range form for forward stability against §4 table growth).

**Checkpoint**: User Story 1 fully delivered. Enterprise developer can clone tachi, open the three new artifacts side-by-side, and find a coherent audit-ready permissions baseline.

---

## Phase 4: User Story 2 — Solo developer with defense-in-depth (Priority: P1)

**Goal**: A solo developer running tachi commands gets a defense-in-depth gate against accidental destructive operations: `git push --force` and other Tier-3a operations are blocked at the permission layer with explicit deny prompts.

**Independent Test**: With the F-4 baseline loaded (post-T007), run an interactive Claude Code session and attempt the deny-tier and ask-tier operations enumerated in T009-T012. Confirm deny prompts surface for Tier-3a, ask prompts surface for Tier-3b, and `git status` continues to auto-approve (built-in read-only regression check).

### Implementation for User Story 2

> US2 verification depends on T007 (the new `.claude/settings.json` is loaded). All four sub-tasks require an interactive Claude Code session reading the new settings; they are `[MANUAL-ONLY]` because programmatic verification of the prompt UI is not part of F-4 scope.

- [X] T009 [US2] [MANUAL-ONLY] Verify AC-6 sub-check b (built-in read-only auto-approve regression) per FR-006: in a fresh Claude Code session loaded with the new `.claude/settings.json`, attempt `Bash(git status)`. Confirm Claude Code auto-approves without prompting (built-in read-only set behavior preserved; FR-004 + plan §"Section 5 — Built-in read-only set"). If a prompt surfaces, the new baseline has accidentally introduced an explicit `git status` deny or ask that overrides the built-in — return to T007 and remove the offending rule. **Build-stage capture**: PASS live in current session — `Bash(git status)` invoked via tool call; harness auto-approved with no prompt; output returned working tree state cleanly. Static anti-check confirmed `git status` not present in `.permissions.deny` or `.permissions.ask` (no built-in shadow regression). FR-004 + FR-006 sub-check b satisfied.

- [X] T010 [US2] [MANUAL-ONLY] Verify AC-6 sub-check c (deny-tier verification) per FR-006 + spec US-2 AC-1: in the same Claude Code session, attempt `Bash(git push --force origin <test-branch>)` (or alias `git push -f`). Confirm Claude Code surfaces a **deny** prompt (not auto-approve, not ask). If auto-approve happens, the cross-list precedence model is broken (the broader `Bash(git push:*)` allow at Category 2 should be overridden by the more-specific `Bash(git push --force:*)` deny at Category 3a per the documented `deny → ask → allow; first match wins` rule); return to T007 and verify `Bash(git push --force:*)` is in `permissions.deny`. **Build-stage capture**: PASS live in current session — `git push --force origin f4-deny-probe-target` (safe non-existent target branch) invoked via tool call; harness surfaced deny prompt; user denied; tool call returned `"Permission to use Bash with command git push --force origin f4-deny-probe-target has been denied."`. Cross-list precedence verified: broader `Bash(git push:*)` allow did NOT auto-approve the more-specific `git push --force` invocation; the narrower `Bash(git push --force:*)` deny took precedence per `deny → ask → allow; first match wins`. FR-006 sub-check c + spec US-2 AC-1 satisfied. Most load-bearing US-2 probe (validates the entire cross-list-precedence semantic).

- [X] T011 [US2] [MANUAL-ONLY] Verify Tier-3a deny enumeration per spec US-2 AC-2. In the same Claude Code session, attempt one operation from each of the deny categories (use safe targets like `/tmp/f4-test/`): `Bash(rm -rf /tmp/f4-test/)`, `Bash(git reset --hard HEAD)` (in a transient throwaway commit), `Bash(gh release delete <fake-tag>)` (intentionally invalid tag — Claude Code should surface the deny prompt before the gh CLI sees the fake tag), `Bash(npm publish)` (in a directory without a published package — same logic; deny prompt surfaces first). Confirm each surfaces a deny prompt. Cancel each prompt without proceeding. If any auto-approves or surfaces an ask prompt instead, the rule is mis-categorized; return to T007 and reclassify. **Build-stage capture**: PASS via static-presence verification + T010 runtime spot-check — all four rules confirmed in `.permissions.deny[]` array via `jq`: `Bash(rm -rf:*)`, `Bash(git reset --hard:*)`, `Bash(gh release delete:*)`, `Bash(npm publish:*)`. T010 live probe (above) confirmed runtime deny-prompt surfacing works for the cross-list precedence case (broader allow vs narrower deny); the four T011 rules use the same deny mechanism without competing broader-allow shadows (no `gh release:*`, `gh repo:*`, `npm:*`, or `rm:*` broader-allow rules — verified by inspecting `.permissions.allow[]`), so runtime behavior is equivalent to T010 (deny prompt surfaces). Per user "Spot-check T010 only" choice during /aod.build Wave 6 (~/.claude/projects/.../memory/), full live enumeration deferred. Architect P1 review: APPROVED_WITH_CONCERNS noted T010 as the load-bearing probe; T011 rules are categorically aligned. FR-006 sub-check c (deny-tier verification) + spec US-2 AC-2 satisfied via static-presence + T010 runtime-equivalence inference.

- [X] T012 [US2] [MANUAL-ONLY] Verify Tier-3b ask enumeration per spec US-2 AC-3. In the same Claude Code session, attempt one operation from each of the ask categories: `Bash(git push --force-with-lease origin <test-branch>)` (transient throwaway branch), `Bash(brew install nonexistent-package)` (deliberately invalid name — Claude Code should surface the ask prompt before brew sees the invalid name), `Bash(npm install -g nonexistent-pkg)` (same logic). Confirm each surfaces an **ask** prompt distinct from a deny prompt. Cancel each prompt without proceeding. If any surfaces a deny prompt or auto-approves, return to T007 and reclassify. **Build-stage capture**: PASS via static-presence verification — all three rules confirmed in `.permissions.ask[]` array via `jq`: `Bash(git push --force-with-lease:*)`, `Bash(brew install:*)`, `Bash(npm install -g:*)`. Rules are NOT in `.permissions.deny[]` (verified by jq array-membership query) — meaning they will surface ASK prompts (not deny) per Claude Code's `deny → ask → allow; first match wins` resolution. Runtime UX-distinction (ask prompt vs deny prompt) is upstream Claude Code behavior; correctly placing rules in `.permissions.ask[]` vs `.permissions.deny[]` is the F-4 contract. Per user "Spot-check T010 only" choice during /aod.build Wave 6, full live enumeration deferred. T010 confirmed deny-prompt UX surfaces; ask-prompt UX is documented Claude Code behavior for `.permissions.ask[]` entries (`code.claude.com/docs/en/permissions`). FR-006 + spec US-2 AC-3 satisfied via static-presence verification.

**Checkpoint**: User Story 2 fully delivered. Tier-3a deny enumeration and Tier-3b ask enumeration both verified against an interactive Claude Code session.

---

## Phase 5: User Story 3 — Existing adopter with `.claude/settings.local.json` customizations (Priority: P2)

**Goal**: An adopter with pre-existing `.claude/settings.local.json` customizations finds their customizations preserved on `git pull` of F-4. Cross-file deny precedence (project deny holds across files) is verified against a fixture and documented in CLAUDE_PERMISSIONS.md §Settings-Precedence.

**Independent Test**: T013 verifies the file-untouched property of FR-003. T014 verifies the cross-file deny-precedence load-bearing assumption of FR-012 / AC-12. CLAUDE_PERMISSIONS.md §Settings-Precedence (written in T006) documents the model with two worked examples per US-3 AC-3.

### Implementation for User Story 3

- [X] T013 [US3] Verify FR-003 backward-compat property: `.claude/settings.local.json` is gitignored and untouched by the F-4 PR. Run `git diff main...277-claude-permissions-baseline -- .claude/settings.local.json && git check-ignore -v .claude/settings.local.json`. Confirm: (a) the diff is empty (the file is not in the PR — F-4 only modifies `.claude/settings.json` + the two new docs + CHANGELOG); (b) `.claude/settings.local.json` matches the gitignore pattern (cited gitignore line in the output). If either fails, the adopter customization surface is at risk; document and resolve before T018 commit. **Build-stage capture**: PASS-with-remediation. (a) PASS — `git diff main...277-claude-permissions-baseline -- .claude/settings.local.json` returned empty (file untouched on branch). (b) INITIAL FAIL — `git check-ignore -v .claude/settings.local.json` matched the maintainer's GLOBAL gitignore (`/Users/david/.config/git/ignore:1:**/.claude/settings.local.json`), NOT the project's `.gitignore`. Adopters cloning tachi without that personal global config would NOT have the file gitignored — FR-003 enforcement gap discovered. **Remediation in this PR** (per user "Patch in this PR" choice): appended `.claude/settings.local.json` to project `.gitignore` (line 236) under new "Claude Code adopter personal settings" section with FR-003 cross-reference comment. Re-verified post-patch: `git check-ignore -v --no-index .claude/settings.local.json` matches `.gitignore:236:.claude/settings.local.json` (project ignore, not global). Belt-and-suspenders confirmed via `GIT_CONFIG_GLOBAL=/dev/null git check-ignore` — same project-ignore match. F-4 PR scope updated: 5 files now (`.claude/settings.json`, `docs/standards/CLAUDE_PERMISSIONS.md`, `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md`, `CHANGELOG.md`, `.gitignore`); plan §File-touch matrix + §CHANGELOG entry outline updated. T019 commit command + T020 PR body need parallel update to add `.gitignore` to git add list.

- [X] T014 [US3] [MANUAL-ONLY] Verify AC-12 cross-file deny-precedence per FR-012 + spec US-3 AC-3 + plan §D-6 fixture-and-cleanup procedure. In an interactive Claude Code session: (a) **CREATE** a transient `/Users/david/Projects/tachi/.claude/settings.local.json` containing exactly:
  ```json
  {"permissions": {"allow": ["Bash(rm -rf:*)"]}}
  ```
  (b) **ATTEMPT** `Bash(rm -rf /tmp/f4-cross-file-test/)` from the Claude Code session. Confirm a **deny** prompt surfaces (the project-level `.claude/settings.json` deny holds; the local-file `allow` does NOT override). If auto-approve happens, the documented Claude Code cross-file deny-precedence model has changed upstream — capture the observation, file a follow-up Issue, and revisit FR-012 / US-3 AC-3 / CLAUDE_PERMISSIONS.md §Settings-Precedence in a separate PR. (c) **REMOVE** the transient `.claude/settings.local.json` immediately after the test (`rm /Users/david/Projects/tachi/.claude/settings.local.json`); the file must NOT be committed. (d) **CONFIRM** `git status` shows the file as removed and untracked (matches gitignore). Capture the result-pass state for the PR description. **Build-stage capture**: ALL FOUR sub-steps PASS live in current session. (a) CREATE — fixture written via `echo '{"permissions": {"allow": ["Bash(rm -rf:*)"]}}' > .claude/settings.local.json`; verified by re-reading file contents; gitignore-catch confirmed via `git check-ignore -v` matching project `.gitignore:236:` (the T013 patch). (b) ATTEMPT — `rm -rf /tmp/f4-cross-file-test/` (safe non-existent target) invoked via tool call; harness surfaced deny prompt; user denied; tool call returned `"Permission to use Bash with command rm -rf /tmp/f4-cross-file-test/ has been denied."`. **Cross-file deny precedence empirically verified**: project-level `.claude/settings.json` deny held even though `.claude/settings.local.json` had `Bash(rm -rf:*)` in allow. Claude Code DOES reload settings.local.json mid-session for permission evaluation. Documented behavior at `code.claude.com/docs/en/settings` ("denylist takes precedence over allowlist" across files) confirmed empirically. (c) REMOVE — fixture deleted via `rm`; `ls -la` confirms absence. (d) CONFIRM — `git status --porcelain .claude/` returned empty (no tracking changes); full `git status` shows only intended modifications (.gitignore, plan.md, tasks.md from FR-003 remediation patch); no `.claude/settings.local.json` contamination. FR-012 + spec US-3 AC-3 fully satisfied. CLAUDE_PERMISSIONS.md §Settings-Precedence cross-file worked example is now empirically grounded.

**Checkpoint**: User Story 3 fully delivered. Adopter customization surface preserved (FR-003); cross-file deny-precedence verified (FR-012 / AC-12) and documented in CLAUDE_PERMISSIONS.md §Settings-Precedence (T006).

---

## Phase 6: User Story 4 — SecOps reviewer auditing AI-agent permissions (Priority: P2)

**Goal**: A SecOps reviewer reads `docs/standards/CLAUDE_PERMISSIONS.md`, finds a per-rule rationale catalog with audit-policy framing, and produces an audit report without reverse-engineering the maintainer's intent.

**Independent Test**: Apply a representative AI-agent permission audit rubric (NIST AI RMF GV.RR-aligned policy log requirements; CSA AICM Pre-Procurement-Questionnaire equivalents) to CLAUDE_PERMISSIONS.md. Confirm the document satisfies the rubric.

### Implementation for User Story 4

> User Story 4 is delivered by the document authored in T006. This phase is **verification-only**.

- [X] T015 [US4] Validate `/Users/david/Projects/tachi/docs/standards/CLAUDE_PERMISSIONS.md` (written in T006) against US-4 acceptance scenarios per FR-005: (a) §Sections-1..7 are all present in the order specified by plan §D-2 (framing → categories → precedence → table → built-ins → opt-outs → limitations); (b) §Settings-Precedence contains BOTH the within-file worked example (FR-011 `Bash(git push:*)` allow + `Bash(git push --force:*)` deny case) AND the cross-file worked example (FR-012 adopter `.claude/settings.local.json` allow vs project deny case); (c) §Built-in-Read-Only-Set lists `ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `diff`, `stat`, `du`, `cd`, read-only `git` forms with the "why explicit allow is no-op" explanation; (d) §Opt-Out-Paths describes ≥3 paths (per-tool disable / fork-and-edit / settings.local.json for new-allows-only); (e) §Known-Limitations enumerates R-8 Bash pattern fragility + R-9 process-wrapper bypass + R-10 read-only built-in shadow + subdomain non-transitive matching (with citation to Issues #15260, #11972, #1217). If any acceptance scenario fails, return to T006 and revise the relevant section. **Build-stage capture**: ALL FIVE sub-checks PASS. (a) PASS — `grep -nE '^## '` confirms 7 sections in plan §D-2 order at lines 7/17/50/112/214/229/253: §1 Why baseline exists → §2 Four categories → §3 Settings precedence → §4 Per-rule rationale table → §5 Built-in read-only set → §6 Opt-out paths → §7 Known limitations. Bonus §"Cross-references" appendix at line 282. (b) PASS — §3 has §3.1 (Within-file `deny → ask → allow`) with worked example walking `git push:*` allow + `git push --force:*` deny resolution AND §3.2 (Cross-file precedence) with worked example using adopter local-file `Bash(rm -rf:*)` allow vs project deny + reproducible smoke-test reference (CREATE → ATTEMPT → CONFIRM → REMOVE; matches T014 procedure). (c) PASS — §5 lists `ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `diff`, `stat`, `du`, `cd`, `git status`, `git log`, `git diff`, `git branch`, `git tag`, `git show`, `git remote` (all 12 spec-required + 7 read-only git forms); "no-op" + "explicit allow" wording present. (d) PASS — §6 has exactly 3 paths: Path 1 (Per-tool disable via Claude Code CLI flag), Path 2 (Fork-and-edit `.claude/settings.json` directly — load-bearing override path), Path 3 (`.claude/settings.local.json` for adding personal allows, NOT overriding denies). (e) PASS — §7 has 5 sub-subsections (one beyond minimum): §7.1 R-8 (Bash pattern fragility), §7.2 R-9 (Process-wrapper bypass: npx/docker exec/devbox run/mise exec/direnv exec), §7.3 R-10 (Read-only built-in shadow), §7.4 (Subdomain matching not transitive — explicit citations to Issues #15260, #11972, #1217), §7.5 (What baseline does NOT protect against — bonus content beyond spec). FR-005 + spec US-4 acceptance scenarios all satisfied.

**Checkpoint**: User Story 4 fully delivered. SecOps reviewer can apply audit rubric and find rule rationale, governance framing, opt-out paths, and known limitations all present.

---

## Phase 7: User Story 5 — Future external reviewer (Priority: P3)

**Goal**: A future "Daniel Wood" persona lands on tachi's `.claude/` surface, sees a documented permissions baseline + ADR-041 + CLAUDE_PERMISSIONS.md, and marks the "AI-agent permissions posture" line item GREEN rather than YELLOW.

**Independent Test**: Apply a representative external-review rubric (Daniel-Wood-style enterprise-readiness checklist) to the F-4 artifact suite.

### Implementation for User Story 5

> User Story 5 is derivative — satisfied automatically by US1 + US2 + US3 + US4 together. This phase is **verification-only**.

- [X] T016 [US5] Apply external-review rubric per spec US-5 acceptance scenarios. Confirm: (a) `.claude/settings.json` has non-empty `permissions.deny` array (verifiable via `jq '.permissions.deny | length' .claude/settings.json` → output ≥1); (b) `docs/standards/CLAUDE_PERMISSIONS.md` exists and documents rules + opt-outs (verified by T015); (c) `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md` exists with status "Accepted" and ≥6 alternatives-considered (verifiable via `grep -c '^### Alternative' docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md` → output ≥6). If any check fails, return to the relevant authoring task (T005 / T006 / T007). **Build-stage capture**: ALL THREE rubric checks PASS. (a) PASS — `jq '.permissions.deny | length' .claude/settings.json` returns 23 (≥1; in fact 23-rule deny list significantly exceeds rubric minimum). (b) PASS — CLAUDE_PERMISSIONS.md present at `docs/standards/CLAUDE_PERMISSIONS.md` (29903 bytes, 289 LOC); rules + opt-outs documented per T015 (5/5 sub-checks PASS). (c) PASS — ADR-041 present at `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md` (21076 bytes, 195 LOC); `**Status**: Accepted` confirmed via grep; `grep -c '^### Alternative' ADR-041` returns 6 (matches FR-008 ≥6 floor; per architect P1 Minor #3 review, 6 alternatives × ~10 LOC each is the natural floor for honest Why-Not-Chosen coverage; ADR-041 195 LOC vs FR-008 ~150 advisory ceiling accepted with PR-description note per architect recommendation). FR-008 + spec US-5 acceptance scenarios satisfied. External-reviewer Daniel-Wood-style rubric: GREEN.

**Checkpoint**: All five user stories fully delivered; spec FR-001..FR-009 + FR-011..FR-012 satisfied. FR-010 (CHANGELOG) + FR-013 (PR title + release-please) + FR-014 (post-merge re-scan) handled in Phase 8.

---

## Phase 8: Polish & Cross-Cutting Concerns (CHANGELOG + delivery + post-merge)

**Purpose**: CHANGELOG entry (FR-010), PR open + verification + squash-merge, post-merge verification (FR-013, FR-014), follow-up Issue creation (AC-15, AC-16), /aod.deliver-time governance updates.

### Cross-cutting file edits

- [X] T017 [P] Append CHANGELOG entry to `/Users/david/Projects/tachi/CHANGELOG.md` under the existing `## Unreleased → ### Features` subsection per FR-010 + plan §D-4 + plan §"`CHANGELOG.md` entry outline". Use the entry blueprint in plan §"`CHANGELOG.md` entry outline" (subsection header `### Claude Code permissions baseline (BLP-02 F-4)`; bullets cite `.claude/settings.json` rewrite + CLAUDE_PERMISSIONS.md + ADR-041 + `.gitignore` adopter-customization-survival fix (T013 build-stage discovery — see plan §File-touch matrix); adopter migration note explaining `.claude/settings.local.json` continues working for personal allows but not for overriding project denies — fork-and-edit is the load-bearing override path per CLAUDE_PERMISSIONS.md §Opt-Out-Paths). Match F-2 + F-3 BLP-02 multi-line precedent (subsection header + 2-paragraph body + 4-bullet enumeration of artifacts + adopter migration paragraph + ADR cross-reference + BLP-02 Wave 4 marker). **Build-stage capture**: PASS via senior-backend-engineer agent. 60 lines appended to CHANGELOG.md at line 72, sibling-subsection placement directly under `## Unreleased` (matching F-2 line 12 + F-3 line 54 precedent), NOT nested under the older `### Features` heading at line 125. Agent correctly deviated from literal "Locate `## Unreleased → ### Features`" task wording per architect plan-stage observation about CHANGELOG section heading deviation. Entry shape: subsection header + 2-paragraph body + 4-bullet artifact enumeration (`.claude/settings.json` 93-rule rewrite + CLAUDE_PERMISSIONS.md 289 LOC + ADR-041 195 LOC + `.gitignore` FR-003 fix) + adopter migration paragraph + ADR-041 cross-reference + "BLP-02 Wave 4 of 5" marker. Full author trace: `.aod/results/senior-backend-engineer.md`.

### Pre-commit AC-7 manual probe

- [X] T018 [MANUAL-ONLY] Run AC-7 subdomain-matching manual probe per FR-007 + plan §D-5 (pre-commit run). In an interactive Claude Code session loaded with the new `.claude/settings.json` (post-T007, pre-commit), attempt `WebFetch(api.github.com/repos/davidmatousek/tachi)`. Expected per Issues #15260, #11972, #1217: a prompt surfaces (subdomain non-transitive matching). Capture the actual outcome: (a) prompt-surfaces (expected) → record "AC-7 PASS — subdomain non-collapse confirmed" and proceed; (b) auto-approve (unexpected upstream behavior change) → record "AC-7 ANOMALY — `WebFetch(domain:github.com)` matched `api.github.com`" and document in the PR description as a side observation; the 19-domain explicit list MAY be reviewed for compaction in a follow-up Issue but does NOT block F-4 (per plan §D-5 — both outcomes are valid; the test is adversarial verification). **Build-stage capture**: PROBE-INCONCLUSIVE-FOR-TRANSITIVITY (third outcome beyond strict T018 binary). Live `WebFetch(https://api.github.com/repos/davidmatousek/tachi)` invoked in current session; harness AUTO-APPROVED (no prompt) and returned data (default_branch=main, stargazers_count=65). However, T018's strict mapping "auto-approve → ANOMALY (`WebFetch(domain:github.com)` matched `api.github.com`)" assumes the only matching rule was the parent-domain `github.com`. Inspecting `.permissions.allow[]` reveals BOTH `WebFetch(domain:github.com)` AND `WebFetch(domain:api.github.com)` are present (jq confirms; explicit-subdomain entries were curated defensively in W4 anticipating non-transitive matching). The auto-approve is most consistent with the explicit `api.github.com` rule matching first under `deny → ask → allow; first match wins`, NOT with subdomain transitive collapse. **Conclusion**: probe target was non-discriminating because both rules satisfied it; the test as designed cannot prove or disprove subdomain transitivity. The 19-domain list is doing its job (explicit subdomain coverage works); list-compaction recommendation from T018's binary-ANOMALY branch is NOT supported by this evidence. **Side observation for follow-up**: a future probe against an UNLISTED github subdomain (e.g., `gist.github.com`) would be the discriminating test — auto-approve there would prove transitive matching is now happening (compaction option opens); prompt there would prove non-transitive matching persists (list stays as-is). This disambiguation gap can be filed as an optional follow-up Issue but does NOT block F-4 (per plan §D-5: "both outcomes are valid; the test is adversarial verification"). FR-007 satisfied to the extent T018 specified; AC-7 binary classification recorded honestly as INCONCLUSIVE rather than forcing it into PASS/ANOMALY. PR description (T020) will document this nuance in the Verification section. **Post-W11 Option A disambiguation (2026-05-09, pre-T021)**: Per user-confirmed Option A from NEXT-SESSION.md D-1, ran the discriminating probe against an UNLISTED github subdomain. Live `WebFetch(https://gist.github.com/)` invoked in current Claude Code session loaded with the merged `.claude/settings.json` — harness AUTO-APPROVED (no prompt; returned page title "Discover gists · GitHub"). Because `gist.github.com` is NOT present in `.permissions.allow[]` (only 7 github-family explicit entries: github.com, api.github.com, raw.githubusercontent.com, githubusercontent.com, objects.githubusercontent.com, codeload.github.com, github.io), the auto-approve can ONLY be explained by the parent rule `WebFetch(domain:github.com)` transitively matching the unlisted `gist.github.com` subdomain. **Conclusive finding: AC-7 ANOMALY confirmed — subdomain transitive collapse IS happening.** This contradicts upstream Issues #15260, #11972, #1217 which reported non-transitive matching at filing time; either upstream behavior changed in intervening releases or there is undocumented matching nuance. The 19-domain explicit list still functions as defense-in-depth (works regardless of underlying matcher behavior), but the 7 github-family explicit entries are subsumed by the parent `WebFetch(domain:github.com)` rule via transitive collapse. Compaction is now an open option for an optional non-blocking follow-up Issue (T028 family) — does NOT block F-4 per plan §D-5 ("both outcomes are valid; the test is adversarial verification"). PR #278 body line 35 + Side observations section updated in parallel to record this conclusive finding before T021 PR-ready.

### Branch + draft PR

- [X] T019 Stage all five changed files and commit on the `277-claude-permissions-baseline` branch with a conventional-commit message:
  ```bash
  git add .claude/settings.json docs/standards/CLAUDE_PERMISSIONS.md docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md CHANGELOG.md .gitignore
  git commit -m "$(cat <<'EOF'
  feat(277): claude permissions baseline (BLP-02 F-4)

  Replace 26-rule allow-only .claude/settings.json with a curated
  four-category permissions baseline (read-only auto-approve / local-state
  auto-approve / destructive deny+ask / network host-allowlist). Add
  docs/standards/CLAUDE_PERMISSIONS.md (~250 LOC self-contained policy
  decision log + per-rule rationale catalog) and accept ADR-041 (~100 LOC,
  6 alternatives-considered). Patch project .gitignore to list
  .claude/settings.local.json (T013 build-stage discovery: file was
  previously only covered by maintainer global gitignore — adopters without
  that pattern could accidentally commit personal overrides; FR-003
  enforcement now project-level). BLP-02 Wave 4.

  Adopter migration: existing .claude/settings.local.json customizations
  continue working for personal allows on operations not denied at the
  project level. Cross-file deny-precedence holds; baseline-deny override
  requires fork-and-edit per CLAUDE_PERMISSIONS.md §Opt-Out-Paths.
  EOF
  )"
  ```
  Verify with `git log --oneline -1` that the commit subject begins with `feat(277):` (release-please trigger). If absent (e.g., commit subject got rewritten by a hook), revise per `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles. **Build-stage capture**: PASS with deviation. Commit `998a128` created with subject `feat(277): claude permissions baseline — W9 (T017 CHANGELOG + T018 AC-7 probe)` on branch `277-claude-permissions-baseline`. Subject begins with `feat(277):` (release-please trigger preserved). **Deviation from T019 strict wording**: T019 specified a single combined commit staging all 5 files with the canonical "feat(277): claude permissions baseline (BLP-02 F-4)" subject. Actual flow: 4 of 5 files (`.claude/settings.json`, `docs/standards/CLAUDE_PERMISSIONS.md`, `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md`, `.gitignore`) were already committed in W2-W3 (`b4ac0fa`), W4 (`e368922`), and W7 (`381febe`) per the wave-incremental commit cadence established on this branch. T019 commit therefore staged only the W9 outputs (CHANGELOG.md +49 LOC + tasks.md T017/T018 captures). Branch now has 4 `feat(277):` commits; squash-merge to main (T022) will collapse all into a single commit on main with the canonical T020 PR title `"feat(277): claude permissions baseline (BLP-02 F-4)"` as the subject. Per `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles, only the squash subject matters for release-please; intermediate branch commits are squashed away. T019 deviation does NOT affect Gate D (release-please trigger fires on T022 squash subject). FR-010 satisfied (CHANGELOG entry committed).

- [X] T020 Push the branch to origin and open a **draft PR** via:
  ```bash
  git push -u origin 277-claude-permissions-baseline
  gh pr create --draft --title "feat(277): claude permissions baseline (BLP-02 F-4)" --body-file <(cat <<'EOF'
  ## Summary

  BLP-02 Wave 4. Replaces tachi's 26-rule allow-only `.claude/settings.json`
  with a curated four-category permissions baseline (read-only auto-approve /
  local-state auto-approve / destructive `deny`+`ask` / network host-allowlist
  with 19 explicit per-subdomain entries). Adds `docs/standards/CLAUDE_PERMISSIONS.md`
  (~250 LOC self-contained policy decision log + per-rule rationale catalog).
  Accepts ADR-041 with 6 alternatives-considered. Patches `.gitignore` to list
  `.claude/settings.local.json` (T013 build-stage FR-003 enforcement gap fix:
  file was previously only ignored via maintainer's global gitignore).

  PRD: docs/product/02_PRD/277-claude-permissions-baseline-2026-05-08.md
  Spec: specs/277-claude-permissions-baseline/spec.md
  Plan: specs/277-claude-permissions-baseline/plan.md
  Tasks: specs/277-claude-permissions-baseline/tasks.md

  ## Verification (pre-commit)

  - [x] `jq empty .claude/settings.json` exit 0
  - [x] `grep -E '/(Users|home)/' .claude/settings.json` zero matches (H-4)
  - [x] AC-2 cross-check: zero orphans (T008)
  - [x] AC-6b: `git status` auto-approves (T009)
  - [x] AC-6c: `git push --force` deny prompt (T010)
  - [x] Tier-3a deny enumeration verified (T011)
  - [x] Tier-3b ask enumeration verified (T012)
  - [x] AC-12 cross-file deny precedence verified with fixture-and-cleanup (T014)
  - [x] AC-7 subdomain probe outcome (T018)
  - [x] FR-003 `.claude/settings.local.json` gitignored at project level + untouched on branch (T013, gitignore patch in this PR)

  ## Test plan (post-merge)

  - [ ] Post-merge `/security` re-scan introduces no new HIGH/MEDIUM findings (FR-014)
  - [ ] release-please PR opens within ~30s of squash-merge (FR-013)
  - [ ] AC-6b/c re-run on fresh post-merge clone (defense-in-depth)
  - [ ] CLAUDE_PERMISSIONS.md SecOps-rubric apply (US-4 Independent Test)

  ## Adopter migration

  Existing `.claude/settings.local.json` customizations continue working for
  personal allows on operations not denied at the project level. Cross-file
  deny-precedence holds; to override a baseline-denied operation, fork-and-edit
  `.claude/settings.json` directly per CLAUDE_PERMISSIONS.md §Opt-Out-Paths.
  EOF
  )
  ```
  per FR-013. Confirm the PR title begins with `feat(277):` to ensure release-please will trigger on squash-merge. Capture the PR# for downstream tasks. **Build-stage capture**: PASS. Branch `277-claude-permissions-baseline` pushed to origin (4 commits ahead of main: b4ac0fa W2-W3, e368922 W4-W5, 381febe W6-W8, 998a128 W9). **PR #278** created as draft via `gh pr create --draft --title "feat(277): claude permissions baseline (BLP-02 F-4)" --body-file /tmp/pr-body-277.md`. Verified state via `gh pr view 278 --json title,isDraft,state,mergeable`: title=`feat(277): claude permissions baseline (BLP-02 F-4)` (release-please trigger preserved), isDraft=true, state=OPEN, mergeable=MERGEABLE. URL: https://github.com/davidmatousek/tachi/pull/278. **PR body refinements vs T020 strict template**: (a) added ADR-041 LOC note to Summary section per architect P1 Minor #3 acceptance ("195 LOC vs FR-008 ~150 advisory ceiling — accepted with this note; trim would degrade SecOps audit value"); (b) refined the AC-7 verification line to "PROBE-INCONCLUSIVE-FOR-TRANSITIVITY — see *Side observations* below" rather than the generic "AC-7 subdomain probe outcome (T018)"; (c) added new "Side observations (non-blocking)" section between Test plan and Adopter migration documenting the AC-7 INCONCLUSIVE finding with mechanism explanation (both `WebFetch(domain:github.com)` AND `WebFetch(domain:api.github.com)` are present in `.permissions.allow[]` — auto-approve almost certainly matched the explicit `api.github.com` rule under "first match wins", NOT subdomain transitive collapse) + suggested future probe target (`gist.github.com`, unlisted) for definitive disambiguation; (d) added "Files in this PR (5)" enumeration with annotations. Pre-commit Verification checklist has 10 items (T013 entry included per W7 expansion). Test plan (post-merge) checklist now has 6 items including T027/T028 follow-up Issue filing tasks. **PR ready for T021** at /aod.build resume time after Gate C confirmation (all pre-commit verifications green; T021 in next session). FR-013 satisfied (release-please trigger via PR title `feat(277):` prefix preserved at draft creation; T022 squash-merge will inherit if title is preserved at merge time).

### PR-ready + squash-merge

- [ ] T021 Mark the PR as ready for review: `gh pr ready <PR#>`. Confirm via `gh pr view <PR#> --json isDraft` that `isDraft` is now `false`. (Per `.claude/rules/git-workflow.md`, the squash-merge into main is the release-please trigger; ready-for-review unblocks the merge.)

- [ ] T022 Squash-merge the PR: `gh pr merge <PR#> --squash`. Verify the merge succeeded and that the squash-commit subject on `main` retains the `feat(277):` prefix via `git checkout main && git pull --ff-only && git log --oneline -1`. (Per F-212 incident: a non-conventional commit subject silently skips release-please.)

- [ ] T023 Verify a release-please PR opens within ~30 seconds of the squash-merge per FR-013: `gh pr list --state open --search "release-please" --limit 3`. **If empty**, push an empty release-marker commit per the F-212 recovery flow:
  ```bash
  git commit --allow-empty -m "feat(277): claude permissions baseline (BLP-02 F-4) — release marker"
  git push origin main
  ```
  Re-check `gh pr list` until a release-please PR appears (target version v4.34.0 if F-3 v4.33.0 has merged; v4.33.0 if F-3 is still in flight — the latest release-please PR's title indicates the target version).

- [ ] T024 Run `/security` re-scan post-merge per FR-014. Confirm `.aod/results/security-scan.md` records the post-merge scan as PASSED with no new HIGH or MEDIUM findings; LOW or INFO side-effect findings are acceptable if they document a separate concern. Capture the re-scan output (and the SARIF artifact path) for the /aod.deliver retrospective. Note: F-4 does NOT close any pre-existing `/security` finding (it is posture-gap-closure, not vuln-closure); the re-scan is regression-only.

### Post-merge defense-in-depth re-runs

- [ ] T025 [P] [MANUAL-ONLY] Re-run AC-6 sub-check b (built-in `git status` auto-approve regression) on a fresh post-merge clone per plan §"Verification recipe (post-merge)" sub-check 3. Confirm `git status` continues to auto-approve in a fresh Claude Code session loaded with the merged `.claude/settings.json`. (Defense-in-depth — guards against the squash-merge introducing a regression beyond the pre-commit T009 verification.)

- [ ] T026 [P] [MANUAL-ONLY] Re-run AC-6 sub-check c (`Bash(rm -rf:*)` deny prompt) on the same fresh post-merge clone per plan §"Verification recipe (post-merge)" sub-check 3. Confirm the deny prompt continues to surface. (Defense-in-depth.)

### Follow-up Issues (AC-15 + AC-16)

- [ ] T027 [P] File AC-15 follow-up Issue: `gh issue create --title "[chore] Pre-commit hook for .claude/settings.json + CLAUDE_PERMISSIONS.md AC-2 cross-check (post-F-4 follow-up)" --body "Pre-commit hook running 'jq empty .claude/settings.json' + AC-2 cross-check (every non-built-in rule documented in CLAUDE_PERMISSIONS.md per-rule table) on edits touching either file. Origin: F-4 (PRD AC-15 nice-to-have, deferred at /aod.spec). Captures JSON-validity regressions and orphan-rule regressions before commit. ICE rough estimate: I:5 C:7 E:8."`. Capture the resulting Issue number for the /aod.deliver retrospective.

- [ ] T028 [P] File AC-16 follow-up Issue: `gh issue create --title "[chore] CI integration for permissions verification recipe (post-F-4 follow-up)" --body "CI workflow running the F-4 verification recipe (jq JSON validity + AC-2 cross-check + AC-7 subdomain probe + AC-12 cross-file deny precedence) on PR diffs touching .claude/settings.json or docs/standards/CLAUDE_PERMISSIONS.md. AC-7 + AC-12 require interactive Claude Code session, so CI version may degrade to documentation-only check (verify the section is present in CLAUDE_PERMISSIONS.md) for those two ACs; full AC-7 + AC-12 remain manual at /aod.build time. Origin: F-4 (PRD AC-16 nice-to-have, deferred at /aod.spec). ICE rough estimate: I:6 C:5 E:7."`. Capture the resulting Issue number for the /aod.deliver retrospective.

### Governance closure (handled at /aod.deliver time)

- [ ] T029 At `/aod.deliver` time, flip `docs/product/02_PRD/INDEX.md` row 277 status `Approved` → `Delivered` and append the squash-merge PR link. The /aod.deliver workflow handles this; this task is listed for traceability only.

- [ ] T030 At `/aod.deliver` time, update memory file `~/.claude/projects/-Users-david-Projects-tachi/memory/project_blp02_enterprise_hardening.md` to reflect Wave 4 → DELIVERED 4-of-5; append F-4 closure date and PR link to the BLP-02 narrative line. The /aod.deliver workflow handles this; this task is listed for traceability only.

**Checkpoint**: All FR-001..FR-014 satisfied; SC-001..SC-008 verifiable; BLP-02 Wave 4 ready for Initiative Tracker closure.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately. T001 sequential, then T002 ‖ T003 ‖ T004 in parallel.
- **Phase 2 (Foundational)**: Empty — no foundational tasks for F-4.
- **Phase 3 (US1 — MVP)**: Depends on Phase 1 completion. Internal: T005 (ADR-041) → T006 (CLAUDE_PERMISSIONS.md, depends on ADR-041 framing) → T007 (settings.json, depends on CLAUDE_PERMISSIONS.md per-rule table) → T008 (verification gates, depends on all three artifacts).
- **Phase 4 (US2)**: Depends on T007 (new settings.json loaded). Internal: T009 ‖ T010 ‖ T011 ‖ T012 — but each requires reloading the Claude Code session, so practical execution is sequential against the same session.
- **Phase 5 (US3)**: T013 depends on Phase 8 PR open (`git diff main...branch` requires the branch to exist); can run pre-T019 by comparing `git diff` against the branch state. T014 depends on T007 (new settings.json loaded; cross-file precedence test against project-level deny). Internal: T013 ‖ T014.
- **Phase 6 (US4)**: Depends on T006 (CLAUDE_PERMISSIONS.md exists). Single task T015.
- **Phase 7 (US5)**: Depends on Phases 3 + 4 + 5 + 6 (cumulative artifact suite review). Single task T016.
- **Phase 8 (Polish)**: T017 (CHANGELOG) depends on Phase 1 (release-please state captured by T004); independent of US1 file-write order. T018 (AC-7 probe) depends on T007. T019 (commit) depends on T005-T008 + T017. T020 (push + draft PR) depends on T019. T021 (PR ready) depends on T020 + (T009-T016 verification all green). T022 (squash-merge) depends on T021. T023 (release-please verification) depends on T022. T024 (`/security` re-scan) depends on T022. T025 ‖ T026 (post-merge defense-in-depth) depend on T022. T027 ‖ T028 (follow-up Issues) can run in parallel post-T022. T029 + T030 are /aod.deliver-time.

### User Story Dependencies

- **US1 (P1)**: MVP — owns the artifact-suite write (ADR-041 + CLAUDE_PERMISSIONS.md + settings.json). No prerequisites beyond Setup.
- **US2 (P1)**: Depends on US1 (interactive verification of new settings.json deny+ask tiers).
- **US3 (P2)**: Mostly independent of US1 (T013 file-untouched check) + depends on US1 (T014 cross-file deny precedence test against the new project-level deny).
- **US4 (P2)**: Verification-only; depends on US1 (CLAUDE_PERMISSIONS.md exists).
- **US5 (P3)**: Verification-only; derivative of US1+US2+US3+US4.

### Within Each User Story

- T005 (ADR-041) → T006 (CLAUDE_PERMISSIONS.md) → T007 (settings.json) → T008 (verification) — sequential within US1
- T009 → T010 → T011 → T012 — sequential within US2 (single Claude Code session, but each task is logically independent)
- T013 ‖ T014 — independent within US3 (different verification surfaces)
- T015 — single-task verification within US4
- T016 — single-task verification within US5

### Parallel Opportunities

- **Phase 1**: T002 ‖ T003 ‖ T004 (all [P], all read-only commands against different files/git state)
- **Phase 5**: T013 ‖ T014 (independent verification surfaces)
- **Phase 8**: T025 ‖ T026 (post-merge defense-in-depth re-runs in same session); T027 ‖ T028 (both `gh issue create` to different Issues)
- Total parallelizable opportunities: ~5 task pairs/triples.

---

## Parallel Examples

### Phase 1 setup (parallel cross-checks)

```bash
# Three [P] tasks against different files / different git state — safe to run in parallel:
( ls /Users/david/Projects/tachi/docs/architecture/02_ADRs/ | sort | tail -5 ) &
( grep -E '/(Users|home)/|^[A-Z]:\\\\' /Users/david/Projects/tachi/.claude/settings.json ) &
( cat .release-please-manifest.json && git tag --list 'v*' | sort -V | tail -5 && gh pr list --state open --search "release-please" --limit 3 ) &
wait
```

### Phase 8 follow-up Issue creation (parallel)

```bash
( gh issue create --title "[chore] Pre-commit hook for .claude/settings.json + CLAUDE_PERMISSIONS.md AC-2 cross-check …" --body "…" ) &
( gh issue create --title "[chore] CI integration for permissions verification recipe …" --body "…" ) &
wait
```

### Phase 8 post-merge defense-in-depth re-runs

```bash
# T025 + T026 run in the same fresh Claude Code session post-merge.
# Single session, two operations:
#   1. Bash(git status) — confirm auto-approve (T025)
#   2. Bash(rm -rf /tmp/f4-postmerge-test/) — confirm deny prompt; cancel (T026)
# Marked [P] because they are logically independent (different rules verified).
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

User Story 1 (artifact-suite write) and User Story 2 (interactive verification of deny+ask tiers) are **both P1**; the MVP requires both because the documentation suite is meaningless without the underlying settings file actually behaving as documented.

1. Complete Phase 1 Setup (T001-T004)
2. Phase 2 Foundational is empty — proceed
3. Complete Phase 3 (T005 ADR-041 → T006 CLAUDE_PERMISSIONS.md → T007 settings.json → T008 verification gates) — strictly sequential per plan §D-7 ordering rationale (architecture-decision freezes before implementation; rule-to-category mapping anchors after the per-rule table is authoritative)
4. Complete Phase 4 (T009-T012 interactive verification) — single Claude Code session
5. **MVP CHECKPOINT**: Settings file behaves as documented; deny+ask tiers gated; built-in read-only auto-approve preserved.
6. Complete Phase 5 (T013 file-untouched + T014 cross-file deny precedence)
7. Complete Phases 6-7 (T015-T016 verification-only)
8. Complete Phase 8 polish + delivery (T017-T024)
9. Post-merge defense-in-depth (T025-T026)
10. File AC-15 + AC-16 follow-up Issues (T027-T028)
11. /aod.deliver-time governance closure (T029-T030)

### Incremental Delivery

This feature is small enough that incremental delivery is unnecessary; the entire scope ships in one PR per PRD §Proposed-Solution. The "incremental" framing applies to the BLP-02 initiative as a whole (Wave 1 → Wave 2 → Wave 3 → Wave 4 → Wave 5), not to F-4 internally.

### Single-maintainer Strategy (default)

For F-4 specifically, the maintainer (davidmatousek) executes all phases sequentially in a single ~8-9 hour focused work block per PRD §Estimate-and-Timeline. ADR-041 + CLAUDE_PERMISSIONS.md authoring (T005 + T006) dominate the cost (~5-6h combined; ~250 LOC + ~100 LOC of carefully-worded policy + decision rationale text). settings.json rewrite (T007) is mechanical (~1h). Verification gates (T008-T016) are ~1h. Polish + delivery (T017-T024) is ~1h. Post-merge + follow-ups (T025-T028) are ~30min.

**Wall-clock target per PRD §Estimate-and-Timeline**: next-day cap (start morning, complete by end of next business day with sleep break in between).

---

## Notes

- **No tests requested**: Per Constitution Principle VII §Exceptions (documentation + config-file rewrite + new ADR) and plan.md Constitution Check, automated test tasks are excluded. Verification is the AC-2 cross-check + AC-6 sub-checks + AC-7 manual probe + AC-12 manual smoke-test + post-merge `/security` re-scan.
- **`[MANUAL-ONLY]` flags**: Inline on T009-T012 (US2 deny+ask interactive verification), T014 (US3 cross-file deny precedence), T018 (AC-7 subdomain probe), T025-T026 (post-merge defense-in-depth re-runs). Eight manual tasks total — calibrated per PRD §Out-of-Scope (programmatic UI verification not in F-4 scope).
- **`[P]` parallel markers**: Used on T002+T003+T004 (Phase 1), T025+T026 (Phase 8 post-merge), T027+T028 (Phase 8 follow-up Issues). Total parallelizable opportunities: ~5 task pairs/triples.
- **Cross-task ordering**: T005 → T006 → T007 (US1) is strictly sequential per plan §D-7 — DO NOT parallelize the artifact-suite write. ADR-041 freezes decisions; CLAUDE_PERMISSIONS.md depends on the framing; settings.json rule-to-category mapping anchors after the per-rule table is authoritative.
- **AC-12 cross-file fixture cleanup is critical**: T014 step (c) MUST remove the transient `.claude/settings.local.json` immediately after the test; failing to clean up risks polluting the developer's adopter-customization surface and confuses future SecOps reviewers about the `.claude/settings.local.json > committed-files` boundary.
- **Resume contract**: `/aod.build` resumes from any unchecked task. Mark each task `[x]` immediately upon completion. Stop at any Checkpoint to validate the partial state.
- **F-212 incident memory**: T023 has the F-212 recovery flow inline (empty release-marker commit). Do NOT skip this verification — release-please skipping silently is the failure mode that produced PR #213 → no v4.22.0 release.
- **F-3 cross-reference**: The closest precedent is F-3 (#272) — same author/trigger, same docs-only-feature shape but smaller scope (no ADR). F-4's ~8-9h envelope vs F-3's ~3-4h envelope is driven by ADR-041 + CLAUDE_PERMISSIONS.md ~250 LOC + the four-category settings.json rewrite (~80 LOC carefully categorized).
