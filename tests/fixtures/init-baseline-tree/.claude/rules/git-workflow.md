# Git Workflow

<!-- Rule file for tachi -->
<!-- This file is referenced from CLAUDE.md using @-syntax -->

## Overview

All development must use feature branches. Never commit to main directly.

**Auto-create branches**: When a workflow command (e.g., `/aod.plan`, `/aod.spec`) detects you are on `main`, automatically create the feature branch and switch to it. Do NOT ask the user for confirmation — feature branches are mandatory, not a choice.

---

## Branch Naming

**Format**: `NNN-descriptive-name`
- **NNN**: GitHub Issue number, zero-padded to 3 digits (e.g., `001`, `002`, `012`)
- **descriptive-name**: Kebab-case description (e.g., `initial-feature`, `user-auth`)

**Examples**:
- `001-initial-feature`
- `012-database-migration`
- `045-api-authentication`

---

## Commit Standards

- Write clear, descriptive commit messages
- Use conventional commits format when possible (feat:, fix:, docs:, etc.)
- Keep commits atomic and focused on single changes
- Reference GitHub Issue numbers in commit messages (e.g., "feat(021): add dark mode")

---

## PR Policies

**Always use feature branches**: `git checkout -b NNN-feature-name`
- Never commit to main directly
- Link PR to feature spec (`specs/NNN-feature-name/spec.md`)
- Ensure CI/CD passes before merge
- Require at least one approval (if team workflow)

### Draft PR Lifecycle

Open a **draft PR early** (at branch creation) and mark it ready at delivery:

1. **Plan stage**: `/aod.plan` creates the branch, pushes it, and opens a draft PR via `gh pr create --draft`
2. **Build stage**: Wave commits are pushed to the branch incrementally — the draft PR shows progress
3. **Deliver stage**: `/aod.deliver` marks the PR ready via `gh pr ready` — this signals "ready for review/merge"

**Why draft-first**: Provides remote backup during long builds, gives visibility into in-progress work, and enables early review comments. The squash-merge at delivery still produces a clean `main` history.

### Conventional Commit PR Titles (release-triggering)

PR titles MUST be Conventional-Commit-formatted because GitHub squash-merges use the PR title as the commit subject, and `release-please` only opens a release PR when it sees `feat:`, `fix:`, or `perf:` on `main`. A delivery without a release is invisible to adopters consuming via SemVer-pinned dependencies.

**Title format**:
- New feature or user-visible improvement: `feat(NNN): <short description>`
- Bug fix: `fix(NNN): <short description>`
- Performance improvement: `perf(NNN): <short description>`

**Default to `feat:`** for any `/aod.deliver` run that ships user-visible work — even "improve X" features count. Use `fix:` only when the change is genuinely a bug fix.

**Enforcement points** (two-step belt-and-suspenders):

1. **Plan stage** — `/aod.plan` opens the draft PR via `gh pr create --draft --title "feat(NNN): <name>"`. The title MUST start with `feat(NNN):`, `fix(NNN):`, or `perf(NNN):` from the moment the draft is created. Setting it correctly here means the squash-merge commit subject inherits the prefix automatically.

2. **Deliver stage** — `/aod.deliver` MUST do two checks:
   - **Pre-merge**: re-verify the PR title is Conventional-Commit-formatted before squash-merging. If a non-conventional title slipped through (e.g., `212: Improve X`), retitle BEFORE merge: `gh pr edit <PR> --title "feat(NNN): <name>"`.
   - **Post-merge**: after `gh pr merge --squash` and `git push origin main`, verify a release-please PR opened within ~30s:
     ```bash
     gh pr list --state open --search "release-please" --limit 3
     ```
     If empty, push an empty release-marker commit:
     ```bash
     git commit --allow-empty -m "feat(NNN): <description> — release marker"
     git push origin main
     ```

**Hidden-bump types** — `docs:`, `chore:`, `refactor:`, `test:`, `style:` are mapped to "hidden, no bump" in `release-please-config.json` and never trigger a release on their own. Post-delivery doc commits using these prefixes (e.g., `docs(NNN): close Feature NNN`) are correct and expected — they document but don't release. The release-triggering commit is the squash-merge of the feature PR itself.

**Reference incident**: F-212 close-out (2026-04-25) — PR #213 squash-merged with title `212: Improve Executive-Architecture Infographic (#213)` (no `feat:` prefix). Release-please silently skipped. Recovered via empty `feat(212):` marker commit; v4.22.0 release PR then opened correctly. Compare to F-2 PR #207 (`feat(206): misinformation threat agent`) → v4.21.0 released cleanly.
