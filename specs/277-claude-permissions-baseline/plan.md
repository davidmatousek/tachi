---
spec_reference: specs/277-claude-permissions-baseline/spec.md
prd_reference: docs/product/02_PRD/277-claude-permissions-baseline-2026-05-08.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-08
    status: APPROVED
    notes: "Plan faithful to PRD v1.1 + spec PM-APPROVED. 14/14 FRs traced to artifacts + verification recipes. File-touch matrix matches spec scope (4 in-tree, 0 out-of-tree — tighter than F-3). Out-of-scope items (AC-15/16/PII/managed-settings/WebSearch) correctly framed. D-1..D-7 defensible from product-scope angle. BLP-02 Wave 4 framing accurate (4-of-5). ADR-041 correctly recognized as Principle-X Architecture-Review artifact (F-4-specific addition). Cross-file deny-precedence integrated at 4 plan touch-points. 3 non-blocking observations. Full review: .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-05-08
    status: APPROVED
    notes: "Plan technically sound. Constitution Check correct (Principle VII §Exceptions properly invoked for docs-only-with-ADR). D-1..D-7 all defensible. ADR-041 outline mirrors ADR-040 structure; 6 alternatives ordered defensibly per D-3. File-touch matrix complete. Verification recipe calibrated correctly (jq/grep/interactive AC-7+AC-12 probes). Cross-list precedence two-layer distinction technically accurate; both worked examples sound. AC-7 correctly framed as adversarial verification. R-8/R-9/R-10 correctly framed as known limitations. 3 non-blocking advisories for tasks.md (AC-12 fixture cleanup, AC-14 README decision, CHANGELOG section heading deviation). Full review: .aod/results/architect.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: F-4 — Claude Permissions Baseline

**Branch**: `277-claude-permissions-baseline` | **Date**: 2026-05-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/277-claude-permissions-baseline/spec.md`
**PRD**: `docs/product/02_PRD/277-claude-permissions-baseline-2026-05-08.md` (v1.1, Approved)
**Initiative**: BLP-02 Wave 4

## Summary

Replace tachi's current 26-rule allow-only `.claude/settings.json` with a curated four-category permissions baseline (read-only auto-approve / local-state auto-approve / destructive `deny`+`ask` / network host-allowlist with 19 explicit per-subdomain entries), add `docs/standards/CLAUDE_PERMISSIONS.md` (~250 LOC self-contained policy decision log + per-rule rationale catalog), accept ADR-041 (~100 LOC, ≥6 alternatives-considered), and append a `## Unreleased → ### Features` entry to `CHANGELOG.md`. **Pure documentation + settings file rewrite + new ADR; no agent / command / skill / script code change, no `finding.yaml` or schema delta, no test infrastructure change.** Scoped per spec FR-001..FR-014; deferred AC-15 (pre-commit hook) and AC-16 (CI integration) are post-merge backlog Issues, not in F-4 implementation scope.

**Technical approach**: Single feature branch `277-claude-permissions-baseline` (already created at `/aod.spec` time); single squash-merged PR titled `feat(277): claude permissions baseline (BLP-02 F-4)`; release-please auto-triggers on `feat(277):` squash-merge with the F-212 empty-marker recovery flow held in reserve. Manual interactive smoke-tests for AC-7 subdomain-matching probe and AC-12 cross-file deny-precedence verification are captured as `[MANUAL-ONLY]` tasks at `/aod.tasks` time.

## Technical Context

> **F-4 is a documentation + settings-file feature.** The technical-context fields below are filled with minimum-applicable values — most are N/A for a doc-touch + JSON-config-rewrite + new-ADR change.

**Language/Version**: Strict JSON (RFC 8259) for `.claude/settings.json` (no JSONC; no comments). Markdown (CommonMark) for `docs/standards/CLAUDE_PERMISSIONS.md`, `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md`, `CHANGELOG.md`. No source code added or modified.
**Primary Dependencies**: Bash 3.2-compatible only for the AC-2 cross-check command and AC-6 verification sub-checks (`jq`, `grep`, `git status` invocation). All already required by the existing tachi tooling baseline. Claude Code itself is the runtime that consumes the baseline (out-of-tree dependency; documented behavior cited from `code.claude.com/docs/en/settings` and `code.claude.com/docs/en/permissions`).
**Storage**: Files in repo (markdown + strict JSON). No database, no persistent state introduced. `.claude/settings.local.json` is referenced as the adopter-customization surface but is gitignored and not modified by F-4.
**Testing**: N/A — no source code change; no automated tests required by the spec. Verification is the AC-6 verification recipe (JSON validity + git-status auto-approve regression + `rm -rf` deny prompt + AC-2 cross-check), the AC-7 subdomain-matching manual probe, the AC-12 cross-file deny-precedence manual smoke-test, and post-merge `/security` re-scan (FR-014). Per Principle VII §Exceptions: "Documentation-only changes may not require production deployment" — this exemption applies to the absence of a CI deployment target; constitution-mandated test coverage thresholds (Principle VI) do not bind for documentation files. Per Principle VII §Non-Negotiable Validation Steps, F-4 still satisfies DoD via: ✅ Pushed to main (squash-merge); ✅ Tested (verification recipe + manual probes + post-merge re-scan); ✅ User-validated (PR review + post-merge SecOps-rubric inspection per US-4 Independent Test).
**Target Platform**: GitHub-hosted repo (`github.com/davidmatousek/tachi`); read by Claude Code at session startup for permission resolution; read by humans (CLAUDE_PERMISSIONS.md + ADR-041) for policy review; consumed via `git pull` / `make update`.
**Project Type**: single (documentation + settings-file change to existing tachi repo). No new project structure introduced.
**Performance Goals**: N/A — Claude Code's settings load is O(rules); ~80-rule baseline is well within established working envelopes (existing 26-rule file already loads with no observable latency).
**Constraints**: ≤ 9 hours active maintainer time (SC-008 from spec); next-day wall-clock target (PRD §Estimate-and-Timeline). Cross-file deny-precedence model (per Claude Code documentation `code.claude.com/docs/en/settings`) is the load-bearing assumption for AC-12 + CLAUDE_PERMISSIONS.md §Settings-Precedence; if it changes upstream, FR-012 and US-3 AC-3 require revision. Subdomain matching is documented as not-transitive per upstream Issues #15260, #11972, #1217 — the 19-domain explicit list is the correct posture.
**Scale/Scope**: `.claude/settings.json` rewrite ~80 LOC (down from existing 26 rules; ceiling ~150 LOC per FR-001 to allow rationale-row growth); CLAUDE_PERMISSIONS.md new file ~250 LOC (ceiling ~350 per FR-005); ADR-041 new file ~100 LOC (ceiling ~150 per FR-008); CHANGELOG.md ~10 LOC delta. Total: ~440 LOC PR + zero out-of-tree settings (no GitHub UI toggle required, in contrast to F-3).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle-by-principle (only applicable principles enumerated)

| Principle | Applicability | Status | Note |
|-----------|---------------|--------|------|
| I. General-Purpose Architecture | N/A | PASS | Documentation + settings; no domain-specific logic added |
| II. API-First Design | N/A | PASS | No API change |
| III. Backward Compatibility (NON-NEGOTIABLE) | APPLIES | PASS | Adopter `.claude/settings.local.json` customizations preserved by Claude Code native cross-file precedence (verified mechanically by FR-003 fixture smoke-test). No breaking change to local Triad `.aod/` file workflows. |
| IV. Concurrency & Data Integrity | N/A | PASS | No state transitions |
| V. Privacy & Data Isolation | N/A | PASS | No data handling; no telemetry; no remote inference touched |
| VI. Testing Excellence | EXEMPTED | PASS | Per Principle VII §Exceptions for documentation + config-file changes; verification is via AC-2 cross-check + AC-6 sub-checks + AC-7 manual probe + AC-12 manual smoke-test + post-merge `/security` re-scan (FR-006/FR-007/FR-012/FR-014) |
| VII. Definition of Done (NON-NEGOTIABLE) | APPLIES | PASS | DoD steps satisfied: (1) Pushed via squash-merge to main; (2) Tested via AC-6 verification recipe + AC-7 manual probe + AC-12 manual smoke-test + post-merge `/security` re-scan; (3) User-validated via PR review + post-merge SecOps-rubric application per US-4 Independent Test. Documentation-only exception applies to the production-deployment step (no production deployment target — settings file is loaded in-place by Claude Code on next session). |
| VIII. Observability & Root Cause Analysis | N/A | PASS | No code paths instrumented; settings load happens in Claude Code, not in tachi |
| IX. Git Workflow & Feature Branching (NON-NEGOTIABLE) | APPLIES | PASS | Feature branch `277-claude-permissions-baseline` exists (per /aod.spec setup); conventional-commit PR title `feat(277): claude permissions baseline (BLP-02 F-4)` planned per FR-013; F-212 incident recovery flow on standby |
| X. Product-Spec Alignment & Architecture Review (NON-NEGOTIABLE) | APPLIES | PASS | PRD approved 2026-05-08 (PM ✓, Architect ⚠, Team-Lead ⚠); spec PM-signed APPROVED 2026-05-08; plan dual-signoff this gate; ADR-041 is the architecture review artifact (Status: Accepted at merge time per FR-008) |
| XI. SDLC Triad Collaboration | APPLIES | PASS | Triad reviewed PRD; PM authored spec and signed off; Architect + Team-Lead reviewing plan and tasks per /aod.plan and /aod.tasks |

### Gate verdict

**Constitution Check: PASS — no violations to track.** F-4's documentation + settings-file profile means most principles either don't apply or are exempted by Principle VII §Exceptions. The mandatory-applicable principles (III, VII, IX, X, XI) all have clear satisfaction paths via the spec's FR-001..FR-014. ADR-041 is *the* architecture-review deliverable (vs F-3 which had no ADR) — it is itself the Principle X §Architecture Review artifact for F-4.

### Complexity Tracking

*Empty — no Constitution Check violations to justify.*

## Project Structure

### Documentation (this feature)

```
specs/277-claude-permissions-baseline/
├── plan.md              # This file (/aod.project-plan output)
├── research.md          # Research phase output (already created at /aod.spec time; updated below)
├── spec.md              # Feature specification (PM ✓ APPROVED 2026-05-08)
├── checklists/
│   └── requirements.md  # Spec quality checklist (created at /aod.spec time, all items pass)
└── tasks.md             # Task breakdown (/aod.tasks output — pending)
```

> **No `data-model.md`, `contracts/`, or `quickstart.md` Phase-1 design artifacts**: F-4 has no API contracts to specify, no entities with state transitions to model, and no source-code quickstart to author. The Phase-1 deliverable surface is captured in plan.md §Phase-1 Design & Contracts below as a file-touch matrix + four file-content outlines (`.claude/settings.json` rule structure, `CLAUDE_PERMISSIONS.md` section list with content sketch, `ADR-041` structure with alternatives list, `CHANGELOG.md` entry style).

### Source Code (repository root)

```
# tachi repo root — files touched by F-4
.claude/settings.json                                                # REWRITE: 26-rule allow-only → ~80 LOC categorized deny+ask+allow (FR-001..FR-004, FR-007, FR-009)
docs/standards/CLAUDE_PERMISSIONS.md                                 # CREATE: new ~250 LOC self-contained policy decision log (FR-005, FR-011, FR-012)
docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md     # CREATE: new ~100 LOC ADR with ≥6 alternatives-considered (FR-008)
CHANGELOG.md                                                         # APPEND: ~10 LOC under ## Unreleased → ### Features subsection (FR-010)
```

```
# Out-of-tree (none)
# Unlike F-3 (which required a GitHub repo-settings UI toggle), F-4 has zero out-of-tree dependencies.
# The new baseline is loaded by Claude Code automatically on the next session start; no UI toggle, no repo settings change.
```

**Structure Decision**: Single-project documentation + config-file overlay onto the existing tachi repo. No new directories introduced (CLAUDE_PERMISSIONS.md slots into existing `docs/standards/`; ADR-041 slots into existing `docs/architecture/02_ADRs/`). No agent / command / skill / script / contract / schema modifications (per PRD §Non-Goals). Spec §Assumptions explicitly restates these absences-of-action. PR title `feat(277): claude permissions baseline (BLP-02 F-4)` enforced per `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles to ensure release-please trigger (per FR-013; F-212 incident recovery flow on standby if release-please skips).

## Phase 0 — Research (Already Complete)

`research.md` was authored during /aod.spec on 2026-05-08 with three research streams (codebase scan via Explore agent, architecture/governance scan via Explore agent, web research via WebSearch with Claude Code-doc + GitHub-issues domain filter). KB lookup attempted but returned empty (`docs/kb/` does not exist in tachi). Key plan-stage-relevant findings re-confirmed at `/aod.project-plan` time:

### Plan-stage re-cross-check (R-1: ADR-041 number is the next available number)

ADR numbering re-checked at plan-stage time (2026-05-08, just now):

```
$ ls docs/architecture/02_ADRs/ | sort | tail -5
ADR-037-*.md
ADR-038-*.md
ADR-039-*.md
ADR-040-config-file-parsing-hardening.md
README.md  (or directory listing only — no ADR-041 yet)
```

**State unchanged from PRD draft**: ADR-040 is the highest-numbered existing ADR; ADR-041 is the correct next number for F-4.

### Plan-stage re-cross-check (R-2: cross-file deny precedence)

Cross-file precedence model is the load-bearing claim for FR-012 and CLAUDE_PERMISSIONS.md §Settings-Precedence second worked example. Re-verified against Claude Code documentation citation in research.md:

> *"if a permission is allowed in user settings but denied in project settings, the project setting takes precedence and the permission is blocked"* — `code.claude.com/docs/en/settings`
>
> *"Denylist takes precedence over allowlist"* — `code.claude.com/docs/en/settings`

**State unchanged from research.md**: cross-file deny precedence is the documented Claude Code behavior. AC-12 verifies it experimentally with a fixture `.claude/settings.local.json` containing `Bash(rm -rf:*)` in `allow` against the project-level deny.

### Plan-stage re-cross-check (R-3: subdomain non-collapse)

Per upstream Issues #15260, #11972, #1217 (all open at PRD draft time and re-checked at plan-stage time): `WebFetch(domain:github.com)` does NOT match `api.github.com`; `WebFetch(domain:*)` wildcard does NOT work. AC-7 expected outcome documented as "no collapse — explicit per-subdomain required". The 19 explicit per-subdomain entries in Category 4 are the correct posture.

### Plan-stage re-cross-check (R-4: H-4 absolute-path finding)

Per `docs/security/OPEN_SOURCE_READINESS.md` §H-4: existing `.claude/settings.json` was flagged for potentially containing machine-specific paths. Re-grepped the *current* file at plan-stage:

```
$ grep -E '/(Users|home)/|^[A-Z]:\\\\' .claude/settings.json
(empty — no matches)
```

**Current settings.json contains no machine-specific absolute paths**, so the rewrite is a clean refactor (no pre-existing leak to clean up). FR-009 cross-check at delivery time guards against the rewrite re-introducing absolute paths.

### Plan-stage re-cross-check (R-5: release version)

Re-checked release-please state at plan-stage:

```
$ cat .release-please-manifest.json
{ ".": "4.32.0" }

$ gh pr list --state open --search "release-please" --limit 3
chore(main): release 4.33.0  (PR #274 — F-3 in flight)
```

**F-3 release-PR is open and unmerged at F-4 plan time**. F-4 will trigger v4.34.0 bump on squash-merge assuming F-3 v4.33.0 lands first. If F-3 lands during F-4 implementation, F-4 inherits the new manifest baseline naturally. AC-13 (release-please verification) holds the F-212 empty-marker recovery flow in reserve for F-4 squash-merge.

### Open decisions resolved at plan stage

| Decision | Choice | Rationale | Alternatives rejected |
|----------|--------|-----------|-----------------------|
| **D-1**: `.claude/settings.json` JSON structure | Three top-level arrays under `permissions`: `allow`, `deny`, `ask`. No nesting beyond what Claude Code's documented schema requires. | Strict JSON schema per Claude Code documentation; matches the existing file's shape (which only has `allow` populated); minimizes deviation from upstream-canonical structure | (A) Add tachi-specific top-level keys for category-tagging (rejected: violates strict-JSON schema; Claude Code would reject the file). (B) Comment per rule (rejected: PRD explicitly drops JSONC tolerance — strict JSON committed). |
| **D-2**: CLAUDE_PERMISSIONS.md section order | Framing → Categories → §Settings-Precedence → Per-rule rationale table → §Built-in-Read-Only-Set → §Opt-Out-Paths → §Known-Limitations | Reader journey: *"why exists"* (framing) → *"how organized"* (categories) → *"how rules resolve"* (precedence) → *"every rule documented"* (table) → *"why ls/cat aren't listed"* (built-ins) → *"how I customize"* (opt-outs) → *"what to watch"* (limitations). Matches the SecOps-reviewer audit flow of US-4. | (A) Per-rule table first (rejected: reviewers need framing before they can interpret the table). (B) Settings-precedence after rationale table (rejected: precedence is foundational; readers must understand `deny → ask → allow` before reading individual rule rows). |
| **D-3**: ADR-041 alternatives ordering | (1) keep current 26-rule allow-only → (2) ship `.claude/settings.example.json` as template → (3) ship empty `.claude/settings.json` (BYO) → (4) ship managed-settings.json → (5) PreToolUse hooks → (6) explicit `.claude/settings.local.json` template | Lowest-effort first (do-nothing), then increasing-investment alternatives, then orthogonal-mechanism alternatives (hooks, managed-settings). Reader follows escalating-design-cost path; chosen approach is justified against each step. | (A) Reverse order (rejected: most-different alternatives first hides the do-nothing case which is the strongest counterfactual — the SecOps-reviewer reading the ADR may already think "why don't you just leave this alone?" and the do-nothing alternative addresses that question first). |
| **D-4**: CHANGELOG entry style | Match F-2 + F-3 precedent: subsection under `## Unreleased → ### Features` titled `### Claude Code permissions baseline (BLP-02 F-4)`; bullets cite `.claude/settings.json` rewrite + CLAUDE_PERMISSIONS.md + ADR-041 + adopter-customization-survival migration note | F-2 PR #257 + F-3 PR #273 are the two most recent BLP-02 successful release-trigger patterns; matching them ensures release-please picks up the entry consistently | (A) One-liner under `### Changed` (rejected: F-2 + F-3 multi-line precedent is the BLP-02 cadence-norm). (B) Standalone `### Security` subsection (rejected: not a CHANGELOG-keepachangelog convention used in this repo). |
| **D-5**: AC-7 subdomain-matching probe — when to run | Run interactively at /aod.build time *before* committing settings.json; re-run post-merge as part of verification recipe | Pre-commit run catches an unexpected upstream-behavior-change before merge; post-merge run verifies the fresh-session load matches the in-flight verification | (A) Post-merge only (rejected: misses pre-commit gate; if AC-7 surfaces unexpected auto-approve, F-4 should adjust the allowlist before merge). (B) Pre-commit only (rejected: post-merge verification is a documentation contract per US-3/US-5). |
| **D-6**: AC-12 cross-file deny-precedence smoke-test fixture | Create a transient `.claude/settings.local.json` containing `Bash(rm -rf:*)` in `allow`; verify deny prompt surfaces; remove the fixture (do NOT commit it). Document the fixture-and-cleanup procedure in CLAUDE_PERMISSIONS.md §Settings-Precedence as a reproducible smoke-test reference. | Adversarial verification of the load-bearing assumption; cleanup avoids polluting the developer's adopter-customization surface. Documenting the procedure makes the test reproducible by future SecOps reviewers. | (A) Skip the fixture (rejected: AC-12 cannot be verified without an active conflict). (B) Commit the fixture under `specs/277-*/fixtures/` (rejected: settings.local.json is gitignored by convention; committing it confuses adopters about the `.claude/settings.local.json > committed-files` boundary). |
| **D-7**: Order of operations at delivery time | (1) Re-grep current settings.json for absolute paths (FR-009 baseline); (2) Author ADR-041 first (architecture-decision freezes before implementation); (3) Author CLAUDE_PERMISSIONS.md (depends on ADR-041 framing); (4) Rewrite `.claude/settings.json` (depends on CLAUDE_PERMISSIONS.md per-rule table for category mapping); (5) Run AC-2 cross-check script (verifies 3↔4 alignment); (6) Run AC-6 verification sub-checks (jq + git status auto-approve + rm -rf deny prompt); (7) Run AC-7 subdomain-matching manual probe; (8) Run AC-12 cross-file deny-precedence manual smoke-test; (9) Append CHANGELOG entry; (10) Push branch + open PR (draft); (11) Mark PR ready for merge; (12) Squash-merge; (13) Verify release-please PR opens (FR-013 recovery flow on standby); (14) Post-merge `/security` re-scan (FR-014). | ADR-first sequencing (steps 2-3) freezes architecture decisions before implementation; settings.json is last-in-trio (step 4) because rule-to-category mapping depends on the CLAUDE_PERMISSIONS.md table being authoritative; verification recipe (steps 5-8) gates merge readiness; post-merge `/security` re-scan (step 14) is the final BLP-02 completion gate. | (A) settings.json first (rejected: rule-to-category mapping has no anchor without CLAUDE_PERMISSIONS.md). (B) ADR last (rejected: ADRs are decision-freezes — they belong before implementation, not after). |

**No NEEDS CLARIFICATION markers remain.** All plan-stage decisions are resolved.

## Phase 1 — Design & Contracts

**This feature has no API contracts, data model entities, or quickstart-style script artifact.** Phase 1 design output is the file-touch matrix + four file-content outlines + verification recipe below.

### File-touch matrix

| Artifact | Action | LOC delta | Spec FR | Verification |
|----------|--------|-----------|---------|--------------|
| `.claude/settings.json` | Rewrite (26-rule allow-only → ~80 LOC categorized) | +50 net | FR-001, FR-002, FR-004, FR-007, FR-009 | `jq empty` JSON validity; AC-2 cross-check; FR-009 absolute-path grep; AC-6 git-status auto-approve + rm -rf deny prompt smoke-tests; AC-7 subdomain-matching probe; AC-12 cross-file deny-precedence smoke-test |
| `.gitignore` | Append `.claude/settings.local.json` to ensure adopter-customization-survival per FR-003 (build-stage discovery: project .gitignore previously did not list the file; only maintainer's global gitignore covered it) | +6 (5 LOC + section comment) | FR-003 | `git check-ignore -v --no-index .claude/settings.local.json` returns project `.gitignore:NNN:` match (not global ignore); adopters cloning tachi inherit the gitignore without needing personal global config |
| `docs/standards/CLAUDE_PERMISSIONS.md` | Create (new file ~250 LOC) | +250 | FR-005, FR-011, FR-012 | Reviewer diff inspection; section presence check (framing / categories / precedence / table / built-ins / opt-outs / limitations); two worked examples present (within-file + cross-file); ≥3 opt-out paths documented |
| `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md` | Create (new file ~100 LOC) | +100 | FR-008 | Reviewer diff; ADR-040 structure parity (Status / Context / Decision / Alternatives Considered / Consequences / Related Findings / References); ≥6 alternatives with Pros/Cons/Why-Not-Chosen sections; status set to "Accepted" with date 2026-05-08 |
| `CHANGELOG.md` | Append entry to `## Unreleased → ### Features` | +10 | FR-010 | Reviewer diff; entry style matches F-2 + F-3 precedent (subsection header + bullet body + ADR cross-reference + adopter migration note) |
| `.aod/results/security-scan.md` | Re-scan post-merge | (autogenerated) | FR-014 | No new HIGH/MEDIUM findings; LOW/INFO side-effect findings acceptable if they document a separate concern |
| GitHub PR title | Set to `feat(277): claude permissions baseline (BLP-02 F-4)` | (PR metadata) | FR-013 | `gh pr view <PR>` confirms title; release-please PR opens within ~30s post-merge |

### `.claude/settings.json` rule structure outline (drafted; final wording at /aod.tasks step + implementation)

The new file has three top-level arrays under `permissions`: `deny`, `ask`, `allow`. The four-category framing in CLAUDE_PERMISSIONS.md maps to these three JSON arrays as follows:

- **Category 1 (read-only auto-approve)** → `permissions.allow` (subset: non-built-in read-only commands only; `rg`, `gh issue view`, `gh pr view`, etc. — ~10 rules per PRD §Category-1)
- **Category 2 (local-state auto-approve)** → `permissions.allow` (subset: write/local-state mutations; `Edit`, `Write`, `Bash(git add:*)`, `Bash(npm test:*)`, etc. — ~30 rules per PRD §Category-2)
- **Category 3a (destructive deny)** → `permissions.deny` (`Bash(rm -rf:*)`, `Bash(git push --force:*)`, `Bash(git reset --hard:*)`, `Bash(gh release delete:*)`, etc. — ~20 rules per PRD §Category-3a)
- **Category 3b (destructive ask)** → `permissions.ask` (`Bash(git push --force-with-lease:*)`, `Bash(gh release create:*)`, `Bash(brew install:*)`, `Bash(eval:*)`, etc. — ~12 rules per PRD §Category-3b)
- **Category 4 (network host-allowlist)** → `permissions.allow` (`WebFetch(domain:<host>)` for the 19 PRD-enumerated domains)

**Total ~80 LOC** across ~70-80 rules. JSON keys order in Claude Code is non-significant; commit-time order matches PRD enumeration for diff-readability (deny first, then ask, then allow Categories 1/2/4).

### `docs/standards/CLAUDE_PERMISSIONS.md` section outline (drafted; final wording at /aod.tasks step + implementation)

**H1**: `# Claude Code Permissions Baseline`

**Section 1 — Why this baseline exists** (FR-005 framing paragraph):
- Brief framing: F-4 origin (Daniel Wood 2026-05-02 thread); BLP-02 enterprise-hardening initiative; replacement of 26-rule allow-only with categorized baseline.
- Cross-reference to ADR-041 for the architecture-decision rationale and alternatives-considered.

**Section 2 — The four categories** (FR-004, FR-005):
- Category 1 (read-only auto-approve) — safety promise: non-mutating; failure mode: built-in shadow (R-10).
- Category 2 (local-state auto-approve) — safety promise: recoverable mutations; failure mode: cross-tree `mv` boundary (documented inline).
- Category 3 (destructive deny+ask) — safety promise: explicit-prompt for irreversibles; failure mode: Bash pattern fragility (R-8) + process-wrapper bypass (R-9). Calibration note: deny rules are calibrated against casual-typo case, not adversarial-bypass case.
- Category 4 (network host-allowlist) — safety promise: default-deny on outbound network; failure mode: subdomain non-transitive matching (citation: Issues #15260, #11972, #1217).

**Section 3 — Settings precedence** (FR-005, FR-011, FR-012):
- **Within-file rule** (one paragraph + worked example): `deny → ask → allow; first matching rule wins`. Worked example: `Bash(git push:*)` allow + `Bash(git push --force:*)` deny → `git push origin main` auto-approves; `git push --force origin main` denies. Cross-reference to Claude Code `code.claude.com/docs/en/permissions`.
- **Cross-file rule** (one paragraph + worked example): denylist always takes precedence over allowlist *across files*; project `.claude/settings.json` deny rules hold even if user-settings or `.claude/settings.local.json` contain a competing allow. Worked example: adopter wants to permit `Bash(rm -rf:*)` for a personal-fork workflow → MUST use Path 2 (fork-and-edit `.claude/settings.json`) or remove the deny rule from project settings; adding `Bash(rm -rf:*)` to `.claude/settings.local.json` `allow` does NOT override the project deny. Cross-reference to Claude Code `code.claude.com/docs/en/settings`.
- Reproducible smoke-test reference (per D-6): create transient `.claude/settings.local.json` with `Bash(rm -rf:*)` in `allow`; attempt the operation; verify deny prompt; remove the fixture.

**Section 4 — Per-rule rationale table** (FR-002, FR-005):
- Markdown table with columns: Rule | Category | Rationale | Failure mode.
- Every non-built-in rule from `.claude/settings.json` appears at least once. Built-ins (per Section 5) are explicitly omitted with a forward reference.
- Rule grouping: by category, then alphabetical within category for diff-readability.
- Rationale wording: 1-2 sentence per row; cites the destructive-vs-recoverable axis or the network-egress-audit finding for Category 4.

**Section 5 — Built-in read-only set** (FR-004, AC-2 cross-check anchor):
- Documented list: `ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `diff`, `stat`, `du`, `cd`, read-only forms of `git` (`git status`, `git log`, `git diff`, `git branch`, `git tag`, `git show`, `git remote`, `git config --get`).
- Explanation of why explicit `allow` for these is no-op.
- Maintenance note: re-verify the built-in set against the latest Claude Code release on each `/aod.update` cycle.
- SecOps-reviewer answer to "why is `Bash(ls:*)` not listed in `permissions.allow`?".

**Section 6 — Opt-out paths** (FR-005, US-4 AC-3):
- **Path 1**: Per-tool disable via Claude Code CLI flag where applicable (e.g., `--deny-tool Bash` for fully disabling Bash within a session). Use case: short-term sandbox where the adopter does not want any Bash invocations.
- **Path 2**: Fork-and-edit `.claude/settings.json` (the load-bearing path for adopters wishing to permit a baseline-denied operation). Cross-references the cross-file deny-precedence rule from Section 3.
- **Path 3**: `.claude/settings.local.json` for *adding* personal allows for operations not denied at the project level. NOT for overriding denies.

**Section 7 — Known limitations** (FR-005):
- **R-8**: Bash pattern fragility. Pattern matches the literal command-line string; `bash -c 'rm -rf /tmp/x'` does not match `Bash(rm -rf:*)` because the wrapper changes the string. Calibration: deny rules are casual-typo, not adversarial.
- **R-9**: Process-wrapper bypass. `npx`, `docker exec`, `devbox run`, `mise exec`, etc. re-shell-out commands; deny does not transit the wrapper. Same calibration as R-8.
- **R-10**: Read-only built-in shadow. A future Claude Code update may add a built-in command that shadows an explicit allow rule, making it no-op. Maintenance note: re-verify Category 1 against the latest Claude Code release on each `/aod.update` cycle.
- **Subdomain matching not transitive**: `WebFetch(domain:github.com)` does NOT match `api.github.com` per Issues #15260, #11972, #1217. The 19 explicit per-subdomain entries are the correct posture; if upstream behavior changes, the list may be reviewed for compaction.

### `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md` outline (drafted; final wording at /aod.tasks step + implementation)

ADR follows ADR-040 structure verbatim (per research.md §Codebase findings):

- **Status**: `Accepted` (date 2026-05-08); deciders: PM ✓, Architect ⚠, Team-Lead ⚠.
- **Context**: Daniel Wood 2026-05-02 thread; BLP-02 Wave 4; the 6 PRD-enumerated gaps in current 26-rule allow-only file (no deny rules / no ask rules / no network host allowlist / no per-rule documentation / `Edit`+`Write` unconditionally auto-approved / no bash-pattern destructive denials).
- **Decision**: 7-item enumeration mirroring CLAUDE_PERMISSIONS.md categories: (1) Adopt four-category framing (read-only / local-state / destructive deny+ask / network); (2) Strict JSON commit (no JSONC; rationale lives in CLAUDE_PERMISSIONS.md); (3) Cross-list `deny → ask → allow` precedence is documented honestly; (4) 19-domain explicit per-subdomain Category 4 list; (5) `.claude/settings.local.json` cross-file precedence preserved + clarified; (6) Three opt-out paths documented (per-tool disable / fork-and-edit / local-allow-add); (7) AC-2 cross-check + AC-6 verification recipe + AC-7 subdomain probe + AC-12 cross-file smoke-test as the verification surface.
- **Alternatives Considered**: 6 alternatives per D-3 ordering, each with Pros / Cons / Why-Not-Chosen sections (~15-20 LOC per alternative).
- **Consequences**: Positive (audit-ready, defense-in-depth, backward-compatible); Negative (~80 LOC settings file is more verbose than 26-rule allow-only — accepted in exchange for safety + auditability); Mitigation (CLAUDE_PERMISSIONS.md absorbs the rationale; settings.json stays minimal).
- **Related Findings**: H-4 absolute-path finding (cross-checked clean per FR-009); no `/security` finding directly closed by F-4 (posture-gap, not vuln-closure).
- **References**: PRD §277, spec FR-001..FR-014, Claude Code docs (`code.claude.com/docs/en/permissions`, `code.claude.com/docs/en/settings`), upstream Issues #15260, #11972, #1217.

### `CHANGELOG.md` entry outline (FR-010)

```markdown
## Unreleased

### Features

### Claude Code permissions baseline (BLP-02 F-4)

Replaced tachi's 26-rule allow-only `.claude/settings.json` with a curated,
categorized, fully-documented permissions baseline. Added
`docs/standards/CLAUDE_PERMISSIONS.md` (rule rationale + opt-out paths) and
accepted `ADR-041`.

- **`.claude/settings.json` baseline (~80 LOC)**: four-category structure
  (read-only auto-approve / local-state auto-approve / destructive `deny`+`ask`
  / network host-allowlist with 19 explicit per-subdomain entries).
- **`docs/standards/CLAUDE_PERMISSIONS.md` (~250 LOC)**: self-contained policy
  decision log with per-rule rationale table, settings precedence (within-file
  + cross-file worked examples), built-in read-only set documentation, opt-out
  paths, known limitations.
- **`docs/architecture/02_ADRs/ADR-041`** (~100 LOC, Accepted): six
  alternatives-considered with Pros / Cons / Why-Not-Chosen sections.
- **`.gitignore`** (+6 LOC): append `.claude/settings.local.json` to ensure
  FR-003 adopter-customization-survival is enforced by project gitignore (build-
  stage T013 discovery: file was previously only covered by maintainer global
  gitignore, not by project; adopters without that global pattern could
  accidentally commit personal allows/denies).

**Adopter migration note**: Existing `.claude/settings.local.json` customizations
continue to work for adding personal allows for operations not denied at the
project level. To override a baseline-denied operation, fork-and-edit
`.claude/settings.json` directly per CLAUDE_PERMISSIONS.md §Opt-Out-Paths
(cross-file deny precedence holds; local-allow does not override project-deny).

Reference: ADR-041 (claude permissions baseline). BLP-02 Wave 4.
```

### Verification recipe (pre-commit + post-merge)

1. **Pre-commit at /aod.build implementation time**:
   1. `jq empty .claude/settings.json` returns exit 0 (FR-001 / AC-6 sub-check a)
   2. `grep -E '/(Users|home)/|^[A-Z]:\\\\' .claude/settings.json` returns zero matches (FR-009)
   3. AC-2 cross-check script (refined per architect P1 Minor #2): every non-built-in rule in `.claude/settings.json` appears in CLAUDE_PERMISSIONS.md per-rule table; every table row references a rule in `.claude/settings.json` or is flagged as a built-in (FR-002 / AC-2). Extraction restricted to §4 (Per-rule rationale table) via awk section-marker delimiters to avoid §5/§6/§7 illustrative-example false positives; final markdown-pipe unescape ensures clean diff against JSON-literal rules. Reference command:
      ```bash
      jq -r '.permissions.deny[], .permissions.ask[], .permissions.allow[]' .claude/settings.json | sort -u > /tmp/f4-rules.txt
      awk '/^## 4\./,/^## 5\./' docs/standards/CLAUDE_PERMISSIONS.md | grep -E '^\| `' | sed -E 's/^\| `([^`]+)` \|.*/\1/' | sed 's/\\|/|/g' | sort -u > /tmp/f4-doc-rules.txt
      diff /tmp/f4-rules.txt /tmp/f4-doc-rules.txt
      ```
      Empty diff = AC-2 PASS.
   4. AC-6 sub-check b: Claude Code in a fresh session auto-approves `git status` (built-in read-only regression check)
   5. AC-6 sub-check c: Claude Code in a fresh session presents a deny prompt for `Bash(rm -rf <transient-test-path>)` (deny-tier verification)
   6. AC-7 subdomain-matching manual probe: `WebFetch(api.github.com/repos/davidmatousek/tachi)` surfaces a prompt (per Issues #15260 / #11972 / #1217 expected outcome)
   7. AC-12 cross-file deny-precedence manual smoke-test: create transient `.claude/settings.local.json` with `Bash(rm -rf:*)` in `allow`; attempt the operation; verify deny prompt surfaces; remove the fixture
2. **Post-merge**:
   1. `/security` re-scan recorded in `.aod/results/security-scan.md` — no new HIGH/MEDIUM findings (FR-014)
   2. release-please PR opens within ~30s of squash-merge: `gh pr list --state open --search "release-please" --limit 3` (FR-013); F-212 empty-marker recovery flow on standby
   3. Re-run AC-6 sub-check b (git status auto-approve regression) and AC-6 sub-check c (rm -rf deny prompt) on a fresh post-merge clone (defense-in-depth)
   4. Update PRD INDEX.md status flip Approved → Delivered with PR link; BLP-02 memory record Wave 4 → DELIVERED at /aod.deliver time

### Agent context update

Per /aod.project-plan Step 2c, update agent context for the active stack. Run `.aod/scripts/bash/update-agent-context.sh claude` at the implementation time to refresh any agent-specific context that depends on the spec/plan deliverables. For F-4 specifically, expected delta is minimal because no new code, agent, command, skill, or schema is introduced — but the `.claude/settings.json` rewrite is itself a change to Claude Code's session-startup state, which any agent context generator that snapshots the current ruleset would need to refresh.

## Constitution Re-check (post-Phase-1 design)

| Principle | Status post-design | Note |
|-----------|---------------------|------|
| III. Backward Compatibility | PASS | `.claude/settings.local.json` cross-file precedence preserved by Claude Code native behavior; FR-003 fixture smoke-test verifies; CLAUDE_PERMISSIONS.md §Settings-Precedence documents the cross-file deny-precedence boundary so adopters understand the override path |
| VII. Definition of Done | PASS | All three DoD steps mapped: ✅ Pushed (squash-merge); ✅ Tested (AC-6 verification recipe + AC-7 manual probe + AC-12 manual smoke-test + post-merge `/security` re-scan); ✅ User-validated (PR review + post-merge SecOps-rubric application per US-4 Independent Test) |
| IX. Git Workflow | PASS | Feature branch ready; PR title `feat(277): claude permissions baseline (BLP-02 F-4)` per FR-013; F-212 recovery on standby |
| X. Product-Spec Alignment | PASS | PRD ✓ Approved, spec ✓ PM-signed; this plan dual-signoff via /aod.project-plan; ADR-041 is the explicit Architecture Review artifact for F-4 (vs F-3 which was no-ADR per the doc-only PRD scope) |
| XI. SDLC Triad Collaboration | PASS | Triad reviewed PRD; PM authored spec; Architect + Team-Lead review at plan and tasks stages |

**Verdict: PASS — no new violations introduced by the Phase-1 design.**

## Complexity Tracking

*Empty — no Constitution Check violations to justify.*
