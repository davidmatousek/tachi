# Claude Code Permissions Baseline

**Status**: Active (BLP-02 Wave 4, F-4; §8 added by Feature 391) | **Source of truth**: [`.claude/settings.json`](../../.claude/settings.json) (§1–§7) and the agent and command files (§8) | **Architecture decision**: [ADR-041](../architecture/02_ADRs/ADR-041-claude-permissions-baseline.md) | **Last updated**: 2026-11-19

**Scope.** §1–§7 describe the development-time settings of this repository (`.claude/settings.json`). Those settings are not installed: the installer (`scripts/install.sh`) copies no `.claude/settings.json` (see the component list in [`INSTALL_MANIFEST.md`](../../INSTALL_MANIFEST.md)), so an adopter who installs tachi receives no settings from this project. [§8](#8-agent-and-command-privilege-matrix) is the adopter-facing matrix: what each tachi agent and command can do, which parts Claude Code enforces, and which parts are declarations.

**Two coverage gaps.** Both hold for the baseline described in §1–§7. They were checked against `.claude/settings.json` and the [Claude Code permissions documentation](https://code.claude.com/docs/en/permissions) on 2026-11-19.

1. **A web fetch outside the allow list is not denied.** The 19 `WebFetch(domain:<host>)` rules (Category 4 in §2, rows in §4) only pre-approve hosts. A fetch to any other host, apart from Claude Code's built-in set of preapproved documentation domains, falls to "ask" in the `default` permission mode (labeled Manual in the CLI), not to "deny". Other modes decide differently: `dontAsk` denies, and in `auto` mode, the built-in starting mode of an interactive session on Claude Code v2.1.283 or later, a classifier reviews the action instead of a prompt ([permission modes](https://code.claude.com/docs/en/permission-modes)).
2. **Shell `curl` is not covered.** Apart from the four pipe-to-shell deny patterns in §4, no rule allows, asks about or denies `curl` or `wget`, and a `WebFetch` allow list does not govern a command that runs through Bash. The documentation says so: "Note that using WebFetch alone doesn't prevent network access. If Bash is allowed, Claude can still use `curl`, `wget`, or other tools to reach any URL."

---

## 1. Why this baseline exists

Tachi's pre-F-4 `.claude/settings.json` was a 26-rule allow-only file accumulated organically over the project's lifetime. The 2026-05-02 Daniel Wood LinkedIn thread named the resulting posture as a load-bearing gap for enterprise-developer adoption: the file lacked `deny` rules for catastrophic-irreversible operations, lacked `ask` rules for the gray zone, lacked a network host allowlist, lacked per-rule rationale, and matched both `git push` and `git push --force` under a single `Bash(git push:*)` allow rule.

F-4 replaces that file with a curated four-category baseline (this document is its policy decision log) and accepts [ADR-041](../architecture/02_ADRs/ADR-041-claude-permissions-baseline.md) as the architecture-decision artifact. The baseline governs tachi's own development and is calibrated against the casual-typo case (§7); the two coverage gaps stated at the top of this document apply to it. It is not installed, so it does not protect an adopter's project; [§8](#8-agent-and-command-privilege-matrix) is the section written for adopters. Anyone working in a checkout of this repository who needs to override a rule has three documented paths (§6).

This document is **self-contained** — a SecOps reviewer auditing tachi's AI-agent permission posture can read this single file end-to-end and produce an audit report without reverse-engineering rule names or maintainer intent. Per-rule rationale lives in §4 and is one-to-one cross-checked against `.claude/settings.json` via the AC-2 verification script (FR-002 in the F-4 spec).

---

## 2. The four categories

The baseline organizes rules into four logical categories. The committed JSON has only the three Claude-Code-native arrays (`permissions.deny`, `permissions.ask`, `permissions.allow`); the four-category framing is a documentation convention used here and in ADR-041.

### Category 1 — Read-only auto-approve

**Safety promise**: non-mutating, no shell-out to mutating commands. Read-only does not mean offline: the `gh` query rules in this category (`gh issue view`, `gh pr list` and the other `gh` rows in §4) call the GitHub API.
**JSON array**: `permissions.allow`.
**Scope**: only **non-built-in** read-only commands appear here. Claude Code's built-in read-only set (`ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `diff`, `stat`, `du`, `cd`, read-only `git` forms — see §5) runs without prompt regardless of `permissions.allow` content; listing those commands here is no-op.
**Failure mode (R-10)**: a future Claude Code update may add a new built-in that shadows an explicit allow rule, making it silently no-op. Mitigation: §5 maintenance note; re-verify the built-in set on each `/aod.update` cycle.

### Category 2 — Local-state auto-approve

**Safety promise**: mutates only the local working tree, local git database, or local filesystem; recoverable via `git reflog`, file-system undo, or local backups; no remote-state mutation beyond same-repo GitHub API operations whose destructive variants are denied at Category 3a.
**JSON array**: `permissions.allow`.
**Scope**: file edits (`Edit`, `Write`, `NotebookEdit`), filesystem mutations (`mkdir`, `touch`, `cp`, `mv`), local-git operations (`git add`, `git commit`, `git checkout`, `git stash`, `git pull`, `git fetch`), network-touching git/gh writes whose destructive variants are denied at Category 3a (`git push:*`, `gh issue create:*`, `gh pr create:*`), build/test runners (`make`, `npm test`, `npm run`), and tachi's own scripts (`.aod/scripts/bash/*`).
**Failure mode**: cross-tree `mv` outside the project surface is technically recoverable but inconvenient; calibration accepts the risk for the per-prompt fatigue trade-off.

### Category 3 — Destructive deny + ask

**Safety promise**: explicit-prompt for irreversibles (deny tier) or warrants-confirmation (ask tier). Two-tier split per ADR-041 Decision Item 1: `deny` is calibrated against the **casual-typo case** (clear-cut catastrophic-irreversible operations); `ask` is calibrated for the legitimate-but-elevated-risk gray zone where blanket-deny would force per-operation override and trigger alert fatigue.
**JSON arrays**: `permissions.deny` (Tier-3a, ~23 rules) and `permissions.ask` (Tier-3b, ~13 rules).
**Failure modes (R-8, R-9)**: Bash patterns match the literal command-line string. `bash -c 'rm -rf /tmp/x'` does NOT match `Bash(rm -rf:*)` because the wrapper changes the matched string (R-8). Process wrappers like `npx`, `docker exec`, `devbox run`, `mise exec`, `direnv exec` re-shell-out commands and similarly bypass the deny (R-9). **Calibration: deny rules are casual-typo, not adversarial.** Adversarial bypass surfaces are out of F-4 scope (PreToolUse hooks are the recommended defense-in-depth path — see ADR-041 §Alternative 5).

### Category 4 — Network host-allowlist

**Safety promise**: pre-approves `WebFetch` for tachi's documented network dependencies, chosen after a command-surface egress audit (GitHub family + Anthropic family + OWASP family + MITRE family + NIST), so routine fetches of those hosts do not prompt. This is an allow list, not a default-deny egress control: a fetch to any other host falls to "ask" in the `default` permission mode, and shell `curl` is not covered (the two coverage gaps stated at the top of this document).
**JSON array**: `permissions.allow` (`WebFetch(domain:<host>)` patterns).
**Scope**: 19 explicit per-subdomain entries — see §4 table.
**Failure mode**: subdomain matching is **not transitive**. `WebFetch(domain:github.com)` does NOT match `api.github.com`. §7.4 records what the current Claude Code documentation says about wildcards, which this baseline originally assumed did not work. The 19-domain list stays explicit and unchanged. AC-7 retains a manual probe as adversarial verification (FR-007).

---

## 3. Settings precedence

Claude Code's permission resolution operates in two independent layers — within-file (cross-list) and cross-file. SecOps reviewers must understand both to interpret an audit log.

### 3.1 Within-file (cross-list) precedence: `deny → ask → allow`; first matching rule wins

Per Claude Code documentation (`https://code.claude.com/docs/en/permissions`), permission rules are evaluated **`deny → ask → allow`; first matching rule wins**. There is **no** "more-specific-pattern-wins-within-a-list" mechanism. The deny list is checked first; if any deny rule matches, the operation is denied regardless of allow rules. Otherwise the ask list is checked; if any ask rule matches, the user is prompted. Otherwise the allow list is checked; if any allow rule matches, the operation is auto-approved. Otherwise Claude Code's default (typically: prompt) applies.

#### Worked example — `Bash(git push:*)` allow + `Bash(git push --force:*)` deny

The baseline includes both `Bash(git push:*)` in `permissions.allow` (Category 2 — recoverable network mutation; rebase/standard pushes auto-approve) AND `Bash(git push --force:*)` in `permissions.deny` (Category 3a — force-push is non-recoverable on remote).

When Claude Code attempts `git push origin main`:
1. Deny check: `Bash(git push --force:*)` does NOT match `git push origin main`. **No deny match.**
2. Ask check: no rule matches.
3. Allow check: `Bash(git push:*)` matches. **Auto-approve.**

When Claude Code attempts `git push --force origin main`:
1. Deny check: `Bash(git push --force:*)` matches `git push --force origin main`. **Deny prompt surfaces.**
2. (Subsequent checks skipped — first match wins; `Bash(git push:*)` allow at Category 2 never evaluates.)

**Reviewer takeaway**: the broader allow at Category 2 does NOT auto-approve the force-push variant because the deny list is checked first. The same pattern applies to every Category-2 allow whose destructive variant is denied at Category 3a (e.g., `gh release:*` → `gh release delete:*` deny; `git reset:*` → `git reset --hard:*` deny).

### 3.2 Cross-file precedence: project deny holds across files

Per Claude Code documentation (`https://code.claude.com/docs/en/settings`):

> *"if a permission is allowed in user settings but denied in project settings, the project setting takes precedence and the permission is blocked"*
> *"Denylist takes precedence over allowlist"*

**Denylist always takes precedence over allowlist across files.** A project-level `permissions.deny` rule cannot be overridden by adding the same pattern to `permissions.allow` in any higher-precedence file (`.claude/settings.local.json`, user-settings, managed-settings).

#### Worked example — adopter local-allow does NOT override project-deny

Suppose an adopter wants to permit `Bash(rm -rf:*)` in their personal-fork workflow. They create `.claude/settings.local.json` containing:

```json
{ "permissions": { "allow": ["Bash(rm -rf:*)"] } }
```

When Claude Code attempts `rm -rf /tmp/test-dir`:
1. Cross-file precedence: project `.claude/settings.json` `permissions.deny` is checked first. `Bash(rm -rf:*)` matches. **Deny prompt surfaces.**
2. The local-file `permissions.allow` rule for the same pattern never applies — denylist takes precedence across files.

**The override path is not local-allow. It is fork-and-edit `.claude/settings.json` directly (Path 2 in §6) or removal of the deny rule from project settings.** Adopters wishing to permit a baseline-denied operation MUST use Path 2; the local-file allow approach is a misconception that this section exists to dispel.

#### Reproducible smoke-test (AC-12 fixture-and-cleanup procedure)

To verify the cross-file deny precedence experimentally:

```text
1. CREATE   .claude/settings.local.json containing:
            { "permissions": { "allow": ["Bash(rm -rf:*)"] } }
2. ATTEMPT  Bash(rm -rf /tmp/f4-test-dir) in an interactive Claude Code session.
3. CONFIRM  the deny prompt surfaces (project-level deny holds despite local allow).
4. REMOVE   .claude/settings.local.json (do NOT commit; the file is gitignored).
```

Future SecOps reviewers may re-run this procedure to verify the baseline behavior has not regressed.

---

## 4. Per-rule rationale table

Every non-built-in rule from `.claude/settings.json` appears at least once in the table below. Built-in read-only commands (§5) are deliberately omitted with a forward reference. The AC-2 cross-check script (FR-002) verifies this catalog matches `.claude/settings.json` rule-for-rule.

| Rule | Category | Rationale | Failure mode if missing |
|------|----------|-----------|--------------------------|
| `Bash(rm -rf:*)` | 3a (deny) | Catastrophic-irreversible; recursive forced delete. | Casual-typo recursive delete proceeds without prompt. |
| `Bash(rm -fr:*)` | 3a (deny) | Flag-order alias of `rm -rf`. | Same as `rm -rf:*`. |
| `Bash(rm -Rf:*)` | 3a (deny) | Capital-R alias of `rm -rf`. | Same as `rm -rf:*`. |
| `Bash(rm --recursive:*)` | 3a (deny) | Long-form flag alias of `rm -rf`. | Same as `rm -rf:*`. |
| `Bash(git push --force:*)` | 3a (deny) | Force-push rewrites remote ref non-recoverably; corrupts colleagues' working trees. | Force-push proceeds under `Bash(git push:*)` allow at Category 2. |
| `Bash(git push -f:*)` | 3a (deny) | Short-flag alias of `git push --force`. | Same as `git push --force:*`. |
| `Bash(git reset --hard:*)` | 3a (deny) | Discards working-tree + index changes; non-recoverable for unstashed work. | Casual reset destroys uncommitted edits without prompt. |
| `Bash(git clean -f:*)` | 3a (deny) | Forced delete of untracked files; non-recoverable. | Casual clean destroys untracked work without prompt. |
| `Bash(git clean -fd:*)` | 3a (deny) | Forced delete of untracked files + directories. | Same as `git clean -f:*`. |
| `Bash(git branch -D:*)` | 3a (deny) | Force-delete unmerged branch; loses commits not on another branch. | Casual branch-D destroys local-only work without prompt. |
| `Bash(gh release delete:*)` | 3a (deny) | Public release deletion; breaks SemVer-pinned consumers. | Release deletion ships without confirmation. |
| `Bash(gh repo delete:*)` | 3a (deny) | Repository deletion; obliterates entire surface. | Repo deletion proceeds without prompt. |
| `Bash(gh repo archive:*)` | 3a (deny) | Repository archival; signals project death to consumers. | Archive proceeds without confirmation. |
| `Bash(gh secret set:*)` | 3a (deny) | Secret mutation in CI/CD environment; affects deployment. | Secret rotation/leak proceeds without prompt. |
| `Bash(gh secret remove:*)` | 3a (deny) | Secret deletion; breaks CI/CD pipelines. | Secret removal proceeds without prompt. |
| `Bash(npm publish:*)` | 3a (deny) | Public package publication; SemVer-pinned consumers see new version immediately. | Accidental publish proceeds without confirmation. |
| `Bash(dd:*)` | 3a (deny) | Disk-destructive utility; can overwrite raw devices. | Casual dd proceeds without prompt. |
| `Bash(mkfs:*)` | 3a (deny) | Filesystem creation overwrites partitions. | Casual mkfs destroys partition without prompt. |
| `Bash(curl * \| sh)` | 3a (deny) | Pipe-to-shell pattern executes remote untrusted code. | Pipe-to-shell auto-approves under broader curl allow. |
| `Bash(curl * \| bash)` | 3a (deny) | Bash variant of pipe-to-shell. | Same as `curl * \| sh`. |
| `Bash(wget * \| sh)` | 3a (deny) | wget variant of pipe-to-shell. | Same as `curl * \| sh`. |
| `Bash(wget * \| bash)` | 3a (deny) | wget+bash variant. | Same as `curl * \| sh`. |
| `Bash(sudo:*)` | 3a (deny) | Privilege escalation never auto-approved. | Privileged operation proceeds without prompt. |
| `Bash(git push --force-with-lease:*)` | 3b (ask) | Safer-than-`--force` alternative; routine in legitimate rebase flows. Deny would trigger alert fatigue (R-1). | Force-with-lease proceeds without per-rebase confirmation (calibration trade-off accepted). |
| `Bash(gh release create:*)` | 3b (ask) | Release publication is reversible-via-deletion but warrants confirmation in semver-pinned-adopter context. | Release publication ships without per-release confirmation. |
| `Bash(gh release edit:*)` | 3b (ask) | Release notes/asset edits affect consumers. | Edits ship without confirmation. |
| `Bash(gh repo edit:*)` | 3b (ask) | Repository settings mutation (visibility, default branch). | Settings change ships without confirmation. |
| `Bash(gh actions:*)` | 3b (ask) | Workflow modification; CI/CD impact. | Workflow change ships without confirmation. |
| `Bash(brew install:*)` | 3b (ask) | System-level mutation outside repo. | Casual brew install proceeds without confirmation. |
| `Bash(brew uninstall:*)` | 3b (ask) | System-level mutation outside repo. | Same as `brew install:*`. |
| `Bash(npm install -g:*)` | 3b (ask) | Global package install with privilege-escalation potential; affects all node projects. | Global install proceeds without confirmation. |
| `Bash(pip install:*)` | 3b (ask) | System-wide installs without venv warrant confirmation. | System pip install proceeds without confirmation. |
| `Bash(git filter-branch:*)` | 3b (ask) | History rewrite; potentially non-recoverable for collaborators. | History rewrite proceeds without confirmation. |
| `Bash(git filter-repo:*)` | 3b (ask) | Modern history-rewrite tool. | Same as `git filter-branch:*`. |
| `Bash(eval:*)` | 3b (ask) | String evaluation can hide arbitrary commands. Calibrated against alert-fatigue cost of full deny. | Evaluation of dynamic strings auto-approves. |
| `Bash(chmod -R 000:*)` | 3b (ask) | Recursive permission lockout; edge case but legitimate uses exist. | Lockout proceeds without prompt. |
| `Bash(rg:*)` | 1 (allow) | Ripgrep is not in the built-in read-only set; explicit allow needed. | Ripgrep prompts on every invocation. |
| `Bash(gh issue view:*)` | 1 (allow) | gh-* surfaces are not in the built-in read-only set. | Issue inspection prompts on every invocation. |
| `Bash(gh issue list:*)` | 1 (allow) | Same as `gh issue view:*`. | Same. |
| `Bash(gh pr view:*)` | 1 (allow) | Same as `gh issue view:*`. | Same. |
| `Bash(gh pr list:*)` | 1 (allow) | Same as `gh issue view:*`. | Same. |
| `Bash(gh pr checks:*)` | 1 (allow) | Same as `gh issue view:*`. | Same. |
| `Bash(gh pr diff:*)` | 1 (allow) | Same as `gh issue view:*`. | Same. |
| `Bash(gh repo view:*)` | 1 (allow) | Same as `gh issue view:*`. | Same. |
| `Bash(gh release view:*)` | 1 (allow) | Same as `gh issue view:*`. | Same. |
| `Bash(gh release list:*)` | 1 (allow) | Same as `gh issue view:*`. | Same. |
| `Bash(gh search:*)` | 1 (allow) | Same as `gh issue view:*`. | Same. |
| `Edit` | 2 (allow) | File edit; recoverable via git reflog or local backups. | Edit prompts on every invocation. |
| `Write` | 2 (allow) | File write; same recoverability as Edit. | Write prompts on every invocation. |
| `NotebookEdit` | 2 (allow) | Jupyter notebook edit; same recoverability. | Notebook edit prompts on every invocation. |
| `Bash(mkdir:*)` | 2 (allow) | Local directory creation; recoverable. | mkdir prompts on every invocation. |
| `Bash(touch:*)` | 2 (allow) | Empty file creation; recoverable. | touch prompts on every invocation. |
| `Bash(cp:*)` | 2 (allow) | File copy; non-destructive. | cp prompts on every invocation. |
| `Bash(mv:*)` | 2 (allow) | File move; recoverable when target is local. Cross-tree `mv` outside project warrants reviewer attention but is calibrated as recoverable. | mv prompts on every invocation. |
| `Bash(git add:*)` | 2 (allow) | Stage changes; recoverable via reflog. | git add prompts on every invocation. |
| `Bash(git commit:*)` | 2 (allow) | Local commit; recoverable via reflog. | git commit prompts on every invocation. |
| `Bash(git checkout:*)` | 2 (allow) | Branch switch; recoverable via reflog. | git checkout prompts on every invocation. |
| `Bash(git stash:*)` | 2 (allow) | Local stash; recoverable. | git stash prompts on every invocation. |
| `Bash(git pull:*)` | 2 (allow) | Network-touching but mutates only local working tree; pull-with-rebase failures abort cleanly. | git pull prompts on every invocation. |
| `Bash(git push:*)` | 2 (allow) | Network-touching and remote-state-mutating, but destructive variant `--force` is denied at 3a; default `git push` is recoverable on remote via reflog. | git push prompts on every invocation. |
| `Bash(git fetch:*)` | 2 (allow) | Network-touching read; never mutates remote. | git fetch prompts on every invocation. |
| `Bash(make:*)` | 2 (allow) | Makefile target invocation; project-local build. | make prompts on every invocation. |
| `Bash(npm test:*)` | 2 (allow) | Test runner; non-destructive. | npm test prompts on every invocation. |
| `Bash(npm run:*)` | 2 (allow) | npm script runner; project-local. | npm run prompts on every invocation. |
| `Bash(.aod/scripts/bash/*)` | 2 (allow) | Tachi's own script suite; vetted in-tree. | tachi scripts prompt on every invocation. |
| `Bash(source .aod/scripts/bash/*)` | 2 (allow) | Sourcing tachi's own scripts; same in-tree vetting. | Source-pattern prompts on every invocation. |
| `Bash(gh issue create:*)` | 2 (allow) | Issue creation; reversible via close. | gh issue create prompts on every invocation. |
| `Bash(gh issue comment:*)` | 2 (allow) | Issue comment; reversible via delete. | gh issue comment prompts on every invocation. |
| `Bash(gh issue edit:*)` | 2 (allow) | Issue edit; reversible via re-edit. | gh issue edit prompts on every invocation. |
| `Bash(gh pr create:*)` | 2 (allow) | PR creation; reversible via close. | gh pr create prompts on every invocation. |
| `Bash(gh pr comment:*)` | 2 (allow) | PR comment; reversible via delete. | gh pr comment prompts on every invocation. |
| `Bash(gh pr edit:*)` | 2 (allow) | PR edit; reversible via re-edit. | gh pr edit prompts on every invocation. |
| `Bash(gh pr ready:*)` | 2 (allow) | Mark PR ready-for-review; reversible via convert-to-draft. | gh pr ready prompts on every invocation. |
| `Bash(gh pr review:*)` | 2 (allow) | PR review submission; reversible via dismiss. | gh pr review prompts on every invocation. |
| `WebFetch(domain:github.com)` | 4 (allow) | GitHub root domain — repo, releases, issues, PRs UI. | github.com fetches prompt on every invocation. |
| `WebFetch(domain:api.github.com)` | 4 (allow) | GitHub REST/GraphQL API — gh CLI, automation. | api.github.com fetches prompt on every invocation. |
| `WebFetch(domain:raw.githubusercontent.com)` | 4 (allow) | Raw file content — markdown rendering, doc fetches. | Raw GitHub fetches prompt on every invocation. |
| `WebFetch(domain:githubusercontent.com)` | 4 (allow) | GitHub user-content surface. | User-content fetches prompt on every invocation. |
| `WebFetch(domain:objects.githubusercontent.com)` | 4 (allow) | GitHub release-asset object storage. | Release-asset fetches prompt on every invocation. |
| `WebFetch(domain:codeload.github.com)` | 4 (allow) | GitHub archive (zip/tar) downloads. | codeload fetches prompt on every invocation. |
| `WebFetch(domain:github.io)` | 4 (allow) | GitHub Pages — adopter doc sites, project pages. | github.io fetches prompt on every invocation. |
| `WebFetch(domain:code.claude.com)` | 4 (allow) | Claude Code documentation — permissions, settings, hooks. | Claude Code doc fetches prompt on every invocation. |
| `WebFetch(domain:docs.anthropic.com)` | 4 (allow) | Anthropic documentation. | Anthropic doc fetches prompt on every invocation. |
| `WebFetch(domain:anthropic.com)` | 4 (allow) | Anthropic root domain. | Anthropic fetches prompt on every invocation. |
| `WebFetch(domain:claude.com)` | 4 (allow) | Claude root domain. | Claude fetches prompt on every invocation. |
| `WebFetch(domain:platform.claude.com)` | 4 (allow) | Claude API platform documentation. | Platform doc fetches prompt on every invocation. |
| `WebFetch(domain:owasp.org)` | 4 (allow) | OWASP root — Top 10, threat references for tachi agents. | OWASP fetches prompt on every invocation. |
| `WebFetch(domain:cheatsheetseries.owasp.org)` | 4 (allow) | OWASP Cheat Sheets — security pattern references. | Cheat Sheet fetches prompt on every invocation. |
| `WebFetch(domain:genai.owasp.org)` | 4 (allow) | OWASP GenAI Security project — LLM Top 10. | GenAI fetches prompt on every invocation. |
| `WebFetch(domain:mitre.org)` | 4 (allow) | MITRE root — ATT&CK / ATLAS framework references. | MITRE fetches prompt on every invocation. |
| `WebFetch(domain:attack.mitre.org)` | 4 (allow) | MITRE ATT&CK — adversary tactics/techniques. | ATT&CK fetches prompt on every invocation. |
| `WebFetch(domain:atlas.mitre.org)` | 4 (allow) | MITRE ATLAS — AI/ML adversary framework. | ATLAS fetches prompt on every invocation. |
| `WebFetch(domain:csrc.nist.gov)` | 4 (allow) | NIST cybersecurity references — AI RMF, frameworks. | NIST fetches prompt on every invocation. |

---

## 5. Built-in read-only set

Claude Code recognizes a built-in read-only command set that runs without permission prompt regardless of `permissions.allow` content. **Listing these commands explicitly in `permissions.allow` is no-op.** They are deliberately omitted from Category 1 in the baseline.

The current built-in set (verified at the F-4 merge SHA via Claude Code documentation):

- `ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `diff`, `stat`, `du`, `cd`
- Read-only forms of `git`: `git status`, `git log`, `git diff`, `git branch` (without `-D`/`-d`/`-m` flags), `git tag` (read-only invocation), `git show`, `git remote`, `git config --get`

**SecOps reviewer answer to "why is `Bash(ls:*)` not in the allow list?"** — Because Claude Code auto-approves `ls` in every mode regardless of settings.json content; explicit allow is no-op. The same applies to all built-in read-only commands. This section IS the audit answer.

**Maintenance note**: re-verify the built-in set against the latest Claude Code release on each `/aod.update` cycle. A future release may add a new built-in (e.g., `Bash(rg:*)` becoming built-in) that shadows an existing Category 1 explicit allow rule (R-10). The AC-2 cross-check script catches the orphaned rule + table-row case but does not detect the shadow case directly — manual review at `/aod.update` time is the safety net.

---

## 6. Opt-out paths

The baseline (`.claude/settings.json`) exists only in a checkout of this repository, such as a fork or a clone. An adopter who installs tachi with `scripts/install.sh` does not receive that file (see the scope statement at the top of this document), so an installed project has no tachi baseline to override: its own user, project, local or managed settings and the CLI flags govern it, and [§8](#8-agent-and-command-privilege-matrix) lists what tachi's agents and commands need.

Three override paths exist for the repository baseline. Every legitimate scenario maps to one of these three. Path 1 is a CLI flag and works in any session.

### Path 1 — Per-tool disable via Claude Code CLI flag

For short-term sandbox sessions where the adopter does not want any Bash invocations (or any specific tool surface), use the Claude Code CLI flag where applicable. Example: `claude --disallowedTools "Bash"` for fully disabling Bash within the session; a bare tool name in `--disallowedTools` removes the tool from Claude's context ([CLI reference](https://code.claude.com/docs/en/cli-reference#cli-flags)). Use case: one-shot sandbox where the operation set is intentionally narrow.

### Path 2 — Fork-and-edit `.claude/settings.json` directly (the load-bearing override path)

For anyone working in a fork or clone who wants to permit a baseline-denied operation, the **only** working override path is to edit `.claude/settings.json` directly — either by modifying the fork or by removing the deny rule from the local copy of the file. Per §3.2 cross-file deny precedence, adding the same pattern to `.claude/settings.local.json` `permissions.allow` does NOT override the project-level deny.

**Use case**: a personal-fork workflow where the person editing the file accepts the risk of the denied operation in a controlled environment. The editing should be deliberate and reviewed; commit messages should cite the rationale.

**This is the path the SecOps reviewer asks about** when they ask "what overrides this baseline?" — Path 2 is the answer for permissive-override-of-deny.

### Path 3 — `.claude/settings.local.json` for *adding* personal allows (NOT overriding denies)

For anyone who wants to add personal allow rules for operations not denied at the project level — e.g., `Bash(my-deploy-tool:*)` for an internal-only tool — `.claude/settings.local.json` is the supported surface. The file is gitignored by Claude Code convention; it survives `git pull` of baseline updates without manual reconciliation (FR-003).

**Path 3 cannot override a project-level deny** — for that, use Path 2. Path 3 is for the additive permissive-extension case only.

---

## 7. Known limitations

The baseline is calibrated against the casual-typo case. The following limitations are disclosed honestly per ADR-041 §Consequences; adopters requiring stronger guarantees should layer additional defenses (PreToolUse hooks; managed-settings deployment; CI policy gates).

### 7.1 R-8 — Bash pattern fragility

Per Claude Code documentation: *"Bash permission patterns that try to constrain command arguments are fragile."* The baseline's `Bash(rm -rf:*)` deny does not match `bash -c 'rm -rf /tmp/x'` because the `bash -c` wrapper changes the matched string. Documented bypass surfaces include flag variations, extra whitespace, shell variables, redirects, and command substitution. **Calibration: deny rules are casual-typo, not adversarial.** Adversarial bypass is out of F-4 scope.

### 7.2 R-9 — Process-wrapper bypass

Modern dev-environment runners — `npx`, `docker exec`, `devbox run`, `mise exec`, `direnv exec` — re-shell-out commands; the literal-string match against `Bash(rm -rf:*)` does not transit the wrapper. An adopter running `Bash(docker exec my-container rm -rf /workspace)` matches the broader docker-exec invocation but bypasses the inner `Bash(rm -rf:*)` deny. Same calibration as R-8 (casual-typo, not adversarial). Anyone working in a checkout of this repository inside Docker/devbox/mise environments loses the destructive-deny baseline for wrapper-issued commands.

### 7.3 R-10 — Read-only built-in shadow

A future Claude Code update may add a new built-in command that shadows an existing explicit allow rule, making the rule silently no-op. Mitigation: §5 maintenance note instructs re-verification of the built-in set on each `/aod.update` cycle; the AC-2 cross-check catches orphaned rule + table-row pairs.

### 7.4 Subdomain matching is not transitive

`WebFetch(domain:github.com)` does NOT match `api.github.com`: a rule without a wildcard matches the named host only. This section was re-checked against the current Claude Code documentation on 2026-11-19 ([permissions: WebFetch](https://code.claude.com/docs/en/permissions#webfetch); [sandboxing: network isolation](https://code.claude.com/docs/en/sandboxing#network-isolation)). Its earlier claim that the `WebFetch(domain:*)` wildcard does not work is out of date for Claude Code v2.1.172 and later. What the documentation confirms:

- `WebFetch` rules match the hostname of the requested URL, case-insensitively, and support `*` wildcards; wildcards in these rules need Claude Code v2.1.172 or later.
- `WebFetch(domain:example.com)` matches requests to `example.com` only. `WebFetch(domain:*.example.com)` matches a subdomain at any depth but not `example.com` itself, so covering both takes two rules.
- `WebFetch(domain:*)` matches every domain. It differs from a bare `WebFetch` rule: as an allow rule it also lets sandboxed commands reach any host, and as a deny rule it refuses each fetch and blocks every host for sandboxed commands. This baseline uses neither form.
- The sandbox honors two wildcard forms in a `WebFetch(domain:<host>)` rule, a leading `*.` and a bare `*`; the bare `*` form needs Claude Code v2.1.186 or later. A wildcard in any other position still matches fetches but has no effect on sandboxed commands.
- A bare `*` in the tool-name position of a `deny` or `ask` rule matches every tool; an unanchored `*` in an `allow` rule is skipped and approves nothing ([permissions: tool name wildcards](https://code.claude.com/docs/en/permissions#tool-name-wildcards)). `Bash(*)` is equivalent to `Bash` ([permissions: match all uses of a tool](https://code.claude.com/docs/en/permissions#match-all-uses-of-a-tool)).

This section previously cited Claude Code Issues [#15260](https://github.com/anthropics/claude-code/issues/15260), [#11972](https://github.com/anthropics/claude-code/issues/11972) and [#1217](https://github.com/anthropics/claude-code/issues/1217) for the wildcard claim; the documentation above supersedes it. The 19-domain explicit list (§4 Category 4 rows) is unchanged by this re-check. Because subdomain wildcards now exist, the list MAY be reviewed for compaction in a follow-up Issue; a wildcard pre-approves more hosts than the entries it replaces, so that review would weigh the wider allowance (no behavior regression occurs from the explicit-list-too-long case; the regression direction is the explicit-list-too-short case).

### 7.5 What this baseline does NOT protect against

- **Out-of-Claude-Code shell access** — operations performed in a normal terminal outside Claude Code are not subject to these rules.
- **Third-party MCP servers with their own permission scopes** — MCP server permissions are governed by the MCP server's own configuration, not by `.claude/settings.json`.
- **The `--dangerously-skip-permissions` flag** — when invoked with this flag, Claude Code bypasses the entire permissions surface. The flag is an explicit opt-out at the session level; baseline rules do not apply.
- **Adversarial bypass via R-8/R-9** — see §7.1, §7.2.

---

## 8. Agent and command privilege matrix

This section is the adopter-facing matrix. For the 21 tachi agents and the 6 tachi commands it lists the tier, tools, model, shell command families, paths written, hosts reached, child processes and dispatches. It describes what `scripts/install.sh` installs into a project; it is not a settings file and it changes no permission. This file is not installed with tachi: the installed isolated-operation runbook ([`docs/guides/ISOLATED_OPERATION_TACHI.md`](../guides/ISOLATED_OPERATION_TACHI.md)) links to this section at a URL pinned to the release.

### 8.1 Enforced and declared

**Enforced by Claude Code at runtime**

- **Tools.** `tools:` in an agent's frontmatter is an allowlist that Claude Code applies to the subagent ([subagents: restrict which tools a subagent can use](https://code.claude.com/docs/en/sub-agents#restrict-which-tools-a-subagent-can-use)). An agent that holds only `Read`, `Glob` and `Grep` can neither write a file nor run a command.
- **Model.** `model:` applies unless the invocation passes a `model` parameter, which takes precedence; no tachi command, agent or skill text passes one. `CLAUDE_CODE_SUBAGENT_MODEL` ranks below the `model:` field and below a passed `model` parameter, so setting it alone does not change a tachi agent's model; only `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (Claude Code v2.1.257 or later) overrides them ([subagents: choose a model](https://code.claude.com/docs/en/sub-agents#choose-a-model); [model configuration: environment variables](https://code.claude.com/docs/en/model-config#environment-variables)). `ANTHROPIC_DEFAULT_SONNET_MODEL` sets which model the `sonnet` alias resolves to; a subagent pinned to a family alias runs on its parent conversation's model when that model is in the same family ([subagents: which version a model alias selects](https://code.claude.com/docs/en/sub-agents#which-version-a-model-alias-selects)). The Model column records the pin, not the model that served a request: an organization's model allowlist and Claude Code's model fallback can run a request on another model ([subagents: when an allowlist blocks a subagent model](https://code.claude.com/docs/en/sub-agents#when-an-allowlist-blocks-a-subagent-model); [model configuration: fallback model chains](https://code.claude.com/docs/en/model-config#fallback-model-chains)). Claude Code's session transcripts record the model that served each turn.

**Declared, not enforced by Claude Code**

- **Bash families, Writes and Hosts** declare what an agent's instructions do; they do not bound a run. A Bash-capable agent can run any command its session allows: in the live validation on macOS, `tachi-report-assembler` ran commands from families outside its Bash families cell, and `tachi-threat-infographic` ran many commands outside its fenced recipes ([run record](../../specs/391-isolated-auditable-operation/test-results/w2-live.md)). The adopter's sandbox bounds where any command can write and connect, not which commands run; the Tools column bounds only which tools an agent holds, as described above.
- **Commands.** A tachi command declares no `allowed-tools`, so it runs in the main session with that session's tools and permission rules. In the commands table, Frontmatter keys records what each command file declares; Dispatches, Bash it instructs, Writes and Child processes record what the command text instructs, which Claude Code does not enforce.

**Tier.** The highest capability the Tools cell grants: `read-only` (`Read`, `Glob`, `Grep`), `writer` (adds `Write`) or `Bash` (adds `Bash`). `Agent` does not change the tier; see Dispatch.

**Dispatch.** `Agent` is transitive. An agent that holds it can start any subagent type available in the session, not only the tachi agents it names, so its Tools cell understates what its run can do. A started subagent has the tools its own definition gives it, not the dispatcher's; its model follows the Model rules above. Declared targets: `tachi-orchestrator` starts the 14 threat agents and `tachi-threat-report`; `tachi-threat-report` starts `tachi-attack-tree-delta`. Observed: in a recorded run, `tachi-threat-report` also started built-in `general-purpose` subagents, which ran Bash and Write; no tachi file instructs this ([run record](../../specs/391-isolated-auditable-operation/test-results/w0-spike.md)). Claude Code limits nesting to three layers below the main conversation by default ([subagents: let subagents spawn their own subagents](https://code.claude.com/docs/en/sub-agents#let-subagents-spawn-their-own-subagents)). The guard pins which agents hold `Agent`; it does not check which types they start, and tachi does not restrict them. The commands' own dispatches are in the Dispatches column of the commands table.

**Hosts.** `model-provider` is the provider Claude Code is configured to use; every agent's turns go there. `generativelanguage.googleapis.com` is Google's Gemini API, which only `tachi-threat-infographic` reaches, and only when `GEMINI_API_KEY` is set and an image is requested through `/tachi.infographic`. The column is a declaration: Claude Code does not enforce it, and an adopter's sandbox network allow list and permission rules do. What the two hosts receive:

> Your Claude Code model provider receives the architecture description, the files tachi reads and the findings on every run. If you set `GEMINI_API_KEY` and run `/tachi.infographic`, Google's Gemini API (`generativelanguage.googleapis.com`) also receives image prompts made of tachi's fixed layout instructions and derived threat-model content, including names and descriptions taken from your architecture (the project name and assessment date; the names, types and short descriptions of components, trust zones, trust boundaries and data flows; finding IDs, descriptions, severities and risk scores; correlation groups of related findings and their descriptions; finding counts, severities and analysis coverage, overall and by component, zone, boundary, flow, threat category and MAESTRO layer; the overall risk posture; control-coverage and risk-reduction figures from compensating-control runs; counts of new, updated, unchanged and resolved findings since a baseline, with new findings marked; and, if a template cannot be loaded, a one-line system description). By design, tachi sends nothing else, but an AI agent following tachi's templates writes each prompt, and no code checks it against this list before it is sent. Claude Code's own operational traffic, such as usage metrics, error reports and feature-flag fetches, is separate from tachi; it is governed by Claude Code's [privacy and telemetry settings](https://code.claude.com/docs/en/data-usage#telemetry-services), and setting `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` turns these off.

### 8.2 Cell syntax

The guard reads the tables in this section, and the runbook's write-locations table must match them, so the cells follow one syntax.

- **Set-valued cells** are the Tools, Bash families, Writes and Hosts cells of the agents table and the Frontmatter keys, Dispatches, Bash it instructs, Writes and Child processes cells of the commands table. A set-valued cell lists backticked tokens separated by a comma and a space, as in `` `Read`, `Glob`, `Grep` ``. A set with no members is a single em dash, `—`. Nothing else appears in the cell, and a token contains no backtick and no pipe.
- **Single-token cells** are the Agent and Model cells, the Command cell and the Path cell of the write-locations table. Each holds exactly one backticked token. The Tier cell is one plain word.
- **Tokens are opaque strings.** The guard compares them exactly and expands nothing: the braces in `{out}/threat-{template}.{jpg,png}` are notation, not two tokens.
- **Order.** Tools are written in the order Read, Glob, Grep, Write, Bash, Agent. The guard compares them as sets, so order is not checked.
- **Row identity.** An Agent cell is the agent's `name:` value. A Command cell `/tachi.<x>` stands for `.claude/commands/tachi.<x>.md`.
- **Table identity.** The guard finds each table by its header row, copied exactly from the tables below. The runbook's table uses the header row of section 8.5.
- **Path notation** (a closed set; the runbook uses the same tokens):
  - `{out}` is the run's output directory, the command's `output_dir` (the report assembler calls it `{output_path}`). For `/tachi.threat-model` it is `{output_dir}/{timestamp}/`, by default `docs/security/{timestamp}/`. `/tachi.security-report` requires it to lie under the working directory, because the report build directory is created there.
  - `$TMPDIR` is the sandbox's per-user temporary directory.
  - `{arch_path}` is the file `/tachi.architecture` writes (by default `docs/security/architecture.md`, or the `--output` path) and `{arch_dir}` is the directory that contains it.
  - `{template}`, `{stem}`, `{finding-id}`, `{chain-id}`, `{plan-id}` and `{N}` are placeholders filled in at run time. `{plan-id}` is the ID of one run's batch plan: a UTC timestamp and a random 12-character hex suffix, such as `20261122T120000Z-0123456789ab`. `/tachi.risk-score` and `/tachi.compensating-controls` make a new one on each run, so each stage directory (`risk-score` or `compensating-controls`) under `{out}/.tachi-build/` gains one subdirectory for every run.
- **Host tokens** are `model-provider` and `generativelanguage.googleapis.com`. **Child-process tokens** are program names as run; a token in capitals is an environment variable that configures a child process.

### 8.3 Agents

| Agent | Tier | Tools | Model | Bash families | Writes | Hosts |
|---|---|---|---|---|---|---|
| `tachi-agent-autonomy` | read-only | `Read`, `Glob`, `Grep` | `sonnet` | — | — | `model-provider` |
| `tachi-attack-tree-delta` | writer | `Read`, `Glob`, `Grep`, `Write` | `sonnet` | — | `{out}/attack-trees/` | `model-provider` |
| `tachi-control-analyzer` | writer | `Read`, `Glob`, `Grep`, `Write` | `sonnet` | — | `{out}/.tachi-build/compensating-controls/{plan-id}/parts/` | `model-provider` |
| `tachi-data-poisoning` | read-only | `Read`, `Glob`, `Grep` | `sonnet` | — | — | `model-provider` |
| `tachi-denial-of-service` | read-only | `Read`, `Glob`, `Grep` | `sonnet` | — | — | `model-provider` |
| `tachi-human-trust-exploitation` | read-only | `Read`, `Glob`, `Grep` | `sonnet` | — | — | `model-provider` |
| `tachi-info-disclosure` | read-only | `Read`, `Glob`, `Grep` | `sonnet` | — | — | `model-provider` |
| `tachi-misinformation` | read-only | `Read`, `Glob`, `Grep` | `sonnet` | — | — | `model-provider` |
| `tachi-model-theft` | read-only | `Read`, `Glob`, `Grep` | `sonnet` | — | — | `model-provider` |
| `tachi-orchestrator` | Bash | `Read`, `Glob`, `Grep`, `Write`, `Bash`, `Agent` | `sonnet` | `python3` | `{out}/threats.md`, `{out}/threats.sarif`, `{out}/attack-chains.md` | `model-provider` |
| `tachi-output-integrity` | read-only | `Read`, `Glob`, `Grep` | `sonnet` | — | — | `model-provider` |
| `tachi-privilege-escalation` | read-only | `Read`, `Glob`, `Grep` | `sonnet` | — | — | `model-provider` |
| `tachi-prompt-injection` | read-only | `Read`, `Glob`, `Grep` | `sonnet` | — | — | `model-provider` |
| `tachi-report-assembler` | Bash | `Read`, `Glob`, `Grep`, `Write`, `Bash` | `sonnet` | `python3`, `test`, `typst` | `{out}/security-report.pdf`, `{out}/.tachi-build/security-report/`, `{out}/attack-trees/`, `{out}/attack-chains/`, `{out}/threat-{stem}.{jpg,png}`, `$TMPDIR` | `model-provider` |
| `tachi-repudiation` | read-only | `Read`, `Glob`, `Grep` | `sonnet` | — | — | `model-provider` |
| `tachi-risk-scorer` | writer | `Read`, `Glob`, `Grep`, `Write` | `sonnet` | — | `{out}/.tachi-build/risk-score/{plan-id}/parts/` | `model-provider` |
| `tachi-spoofing` | read-only | `Read`, `Glob`, `Grep` | `sonnet` | — | — | `model-provider` |
| `tachi-tampering` | read-only | `Read`, `Glob`, `Grep` | `sonnet` | — | — | `model-provider` |
| `tachi-threat-infographic` | Bash | `Read`, `Glob`, `Grep`, `Write`, `Bash` | `sonnet` | `[`, `echo`, `python3`, `test` | `{out}/threat-{template}-spec.md`, `{out}/threat-{template}.{jpg,png}`, `{out}/.tachi-build/infographic-{template}.json`, `{out}/.tachi-build/gemini-{template}-request.json`, `{out}/.tachi-build/gemini-{template}-response.json` | `model-provider`, `generativelanguage.googleapis.com` |
| `tachi-threat-report` | writer | `Read`, `Glob`, `Grep`, `Write`, `Agent` | `sonnet` | — | `{out}/threat-report.md` | `model-provider` |
| `tachi-tool-abuse` | read-only | `Read`, `Glob`, `Grep` | `sonnet` | — | — | `model-provider` |

- **Bash families are the fenced ones.** The column holds only the command families that the guard extracts from labeled shell fences in the agent files, and only the three Bash-capable agents (`tachi-orchestrator`, `tachi-report-assembler`, `tachi-threat-infographic`) have any. A command that a model builds at run time is not visible to the guard. Four items sit outside the fences and are declared here instead:
  - `tachi-threat-infographic`'s `curl` request to the Gemini host, in the pinned form of [`gemini-prompt-construction.md`](../../.claude/skills/tachi-infographics/references/gemini-prompt-construction.md) (the key is read from the environment and delivered through `--config -`, never on the command line), and its decode of the response with `python3` using the standard library.
  - The extractor cleanup recipe in [`typst-artifacts.md`](../../.claude/skills/tachi-report-assembly/references/typst-artifacts.md) (`--cleanup-mislabeled-images`, then `--remove-build-dir`), which treats the target directory as `{out}`.
  - `tachi-report-assembler`'s check that the PDF exists and is not empty (Step 3c), which names no command.
  - Searches that run as `find` and `grep` through the Bash tool. On macOS, Linux and WSL the documentation says Claude Code leaves the Glob and Grep tools out of the default tool set and brings them back for a subagent that lists them and leaves out `Bash` ([tools reference: Glob tool behavior](https://code.claude.com/docs/en/tools-reference#glob-tool-behavior)), so searches by the three Bash-capable agents can appear as Bash calls that this column does not list.
- **Writes.** Every Writes token in this table is under `{out}` or is `$TMPDIR`. The only paths outside those two locations are the two `/tachi.architecture` entries in the commands table. The risk scorer and the control analyzer write only part files, one for each dispatch, under `{plan-id}/parts/` in their stage directory. Shipped scripts write the rest of each stage directory and the rendered files, `risk-scores.{md,sarif}` and `compensating-controls.{md,sarif}` (section 8.4). Section 8.5 gives the writer and the condition for each path.

### 8.4 Commands

| Command | Frontmatter keys | Dispatches | Bash it instructs | Writes | Child processes |
|---|---|---|---|---|---|
| `/tachi.threat-model` | `description` | `tachi-orchestrator` | `python3` | `{out}/`, `{out}/architecture.md`, `{out}/threats.md`, `{out}/threats.sarif`, `{out}/attack-chains.md`, `{out}/threat-report.md`, `{out}/attack-trees/` | `python3` |
| `/tachi.risk-score` | `description` | `tachi-risk-scorer` | `python3` | `{out}/`, `{out}/threats.md`, `{out}/risk-scores.{md,sarif}`, `{out}/.tachi-build/risk-score/`, `{out}/.tachi-build/risk-score/{plan-id}/parts/` | `python3` |
| `/tachi.compensating-controls` | `description` | `tachi-control-analyzer` | `python3` | `{out}/`, `{out}/compensating-controls.{md,sarif}`, `{out}/.tachi-build/compensating-controls/`, `{out}/.tachi-build/compensating-controls/{plan-id}/parts/` | `python3` |
| `/tachi.infographic` | `description` | `tachi-threat-infographic` | `python3`, `grep` | `{out}/`, `{out}/threat-{template}-spec.md`, `{out}/threat-{template}.{jpg,png}`, `{out}/.tachi-build/infographic-{template}.json`, `{out}/.tachi-build/gemini-{template}-request.json`, `{out}/.tachi-build/gemini-{template}-response.json` | `python3`, `curl` |
| `/tachi.security-report` | `description` | `tachi-report-assembler` | `which`, `ls`, `head`, `test`, `command` | `{out}/`, `{out}/security-report.pdf`, `{out}/.tachi-build/security-report/`, `{out}/attack-trees/`, `{out}/attack-chains/`, `{out}/threat-{stem}.{jpg,png}`, `$TMPDIR` | `python3`, `typst`, `mmdc`, `chromium`, `TACHI_MMDC_PUPPETEER_CONFIG` |
| `/tachi.architecture` | `description` | — | `mkdir`, `shasum` | `{arch_path}`, `{arch_dir}/.archive/v{N}/` | — |

- **Frontmatter keys.** Each command declares only `description`: no `allowed-tools` and no `model`. A value for either key is recorded here when it is set.
- **Dispatches** lists the tachi agent the command starts. `/tachi.threat-model` starts `tachi-orchestrator`, which starts the 14 threat agents and `tachi-threat-report` one level down (see Dispatch). `/tachi.architecture` runs in the main session and starts no agent.
- **Bash it instructs** is declared only. The commands also tell the main session, in prose that names no command, to create `{out}/`; `/tachi.threat-model` tells it to copy the architecture file into `{out}/`, and `/tachi.architecture` tells it to copy the previous file into its archive directory. Those writes are listed under Writes.
- **Writes** is the command's whole footprint: its own writes plus those of the agents it starts. `/tachi.risk-score` runs the populate script on its input file only when `{out}` is the input directory; with `--output-dir` set to another directory, the input directory stays read-only.
- **Stage directories.** In the main session, `/tachi.risk-score` and `/tachi.compensating-controls` run `scripts/tachi-stage.py` and their renderer (`scripts/render-risk-scores.py` or `scripts/render-compensating-controls.py`) through `python3`. The scripts write the command's stage directory, `{out}/.tachi-build/risk-score/` or `{out}/.tachi-build/compensating-controls/`: the current-plan pointer, the batch plan, the batch inputs, copies of the earlier outputs, the staged output files and the stage record. The agent writes only the part files, under `{plan-id}/parts/`. The renderer moves the staged files onto the command's output files in `{out}` once its checks pass.

### 8.5 Write locations (canonical list)

The runbook states the same write set in its section 5. The table below is the source: the runbook copies it exactly, and the guard fails when the set of paths in the runbook's table differs from the set of tokens in the Writes cells of the two tables above.

- **Heading.** The runbook heading is `## 5. Write locations`.
- **Table.** One table under that heading has the header row shown below, which is how the guard finds it, and one row per distinct path token. The Path cell holds exactly one backticked token in the notation of section 8.2; the other two cells are free text.

| Path | Written by | Condition |
|---|---|---|
| `{out}/` | the main session of each run command (`/tachi.threat-model`, `/tachi.risk-score`, `/tachi.compensating-controls`, `/tachi.infographic`, `/tachi.security-report`) | the directory does not exist yet |
| `{out}/architecture.md` | the main session of `/tachi.threat-model` (verbatim copy of the architecture file) | the architecture file exists |
| `{out}/threats.md` | `tachi-orchestrator`; updated in place by `scripts/populate-affected-assets.py`, which the orchestrator and `/tachi.threat-model` run and which `/tachi.risk-score` runs on its input file; the one `**Architecture source**` body line (FR-E.18) by `scripts/tachi-stage.py architecture-source`, run by the main session of `/tachi.threat-model` | always for `/tachi.threat-model`; for `/tachi.risk-score` only when the input is markdown, an architecture file is found and `{out}` is the input directory |
| `{out}/threats.sarif` | `tachi-orchestrator` | always |
| `{out}/attack-chains.md` | `tachi-orchestrator` | at least one cross-layer chain passes the filter |
| `{out}/threat-report.md` | `tachi-threat-report` | the report phase runs (the default; the orchestrator's `--skip-report` opt-out skips it) |
| `{out}/attack-trees/` | `tachi-attack-tree-delta` (`{finding-id}-attack-tree.md` and `.manifest.json`); `scripts/extract-report-data.py` (`{finding-id}-attack-tree.png`) | Critical or High findings exist (the manifest is written either way); the PNGs only when `mmdc` is on `PATH` |
| `{out}/attack-chains/` | `scripts/extract-report-data.py` (`{chain-id}-attack-chain.png`) | an attack chain is surfaced and `mmdc` is on `PATH` |
| `{out}/risk-scores.{md,sarif}` | `scripts/render-risk-scores.py`, run by the main session of `/tachi.risk-score`: it renders both files into the plan's `staged/` directory, checks them, then moves them onto these names | the render succeeds; a failed run leaves the earlier files in place |
| `{out}/.tachi-build/risk-score/` | `scripts/tachi-stage.py` and `scripts/render-risk-scores.py`, run by the main session of `/tachi.risk-score`: `current.json` and, in a new `{plan-id}/` directory, the plan, the batch inputs, copies of the earlier outputs, the staged outputs and the stage record; a failed run moves any output it changed into `failed/` | the command reaches its planning step; kept (tachi never removes a plan directory). It holds absolute local paths and copies of earlier outputs, so it is as sensitive as `{out}` |
| `{out}/.tachi-build/risk-score/{plan-id}/parts/` | `tachi-risk-scorer` (Write tool): one part file for each dispatch, at the path its batch input names | a batch is dispatched; kept |
| `{out}/compensating-controls.{md,sarif}` | `scripts/render-compensating-controls.py`, run by the main session of `/tachi.compensating-controls`: it renders both files into the plan's `staged/` directory, checks them, then moves them onto these names | the render succeeds; a failed run leaves the earlier files in place |
| `{out}/.tachi-build/compensating-controls/` | `scripts/tachi-stage.py` and `scripts/render-compensating-controls.py`, run by the main session of `/tachi.compensating-controls`: `current.json` and, in a new `{plan-id}/` directory, the plan, the batch inputs, copies of the earlier outputs, the staged outputs and the stage record; a failed run moves any output it changed into `failed/` | the command reaches its planning step; kept (tachi never removes a plan directory). It holds absolute local paths and copies of earlier outputs, so it is as sensitive as `{out}` |
| `{out}/.tachi-build/compensating-controls/{plan-id}/parts/` | `tachi-control-analyzer` (Write tool): one part file for each dispatch, at the path its batch input names | a batch is dispatched; kept |
| `{out}/threat-{template}-spec.md` | `tachi-threat-infographic` | each requested template |
| `{out}/threat-{template}.{jpg,png}` | `tachi-threat-infographic`, decoding the response with `python3` | `GEMINI_API_KEY` is set and the API returns an image |
| `{out}/.tachi-build/infographic-{template}.json` | `scripts/extract-infographic-data.py --output` | each template extraction; kept |
| `{out}/.tachi-build/gemini-{template}-request.json` | `tachi-threat-infographic` (Write tool) | `GEMINI_API_KEY` is set; kept (it is the exact payload sent to the Gemini host) |
| `{out}/.tachi-build/gemini-{template}-response.json` | `curl --output`, run by `tachi-threat-infographic` | `GEMINI_API_KEY` is set; kept |
| `{out}/security-report.pdf` | `typst compile`, run by `tachi-report-assembler` | the compile succeeds |
| `{out}/.tachi-build/security-report/` | `scripts/extract-report-data.py --build-dir` (a copy of `templates/tachi/security-report/`, a custom `report-config.typ` when one exists, and `report-data.typ`); removed by `--remove-build-dir` | every report run; removed after a successful compile and kept after a failed one (the parent `{out}/.tachi-build/` stays) |
| `{out}/threat-{stem}.{jpg,png}` | `scripts/extract-report-data.py`: a corrected copy of an infographic image whose bytes do not match its extension; with `--cleanup-mislabeled-images`, which no run recipe passes, it also deletes a redundant file that lies in `{out}` | such an image exists |
| `$TMPDIR` | `scripts/extract-report-data.py` (Python `tempfile`: Mermaid sources and rendered PNGs, removed on exit); headless Chromium started by `mmdc` (profile and caches) | attack trees or attack chains are rendered |
| `{arch_path}` | the main session of `/tachi.architecture` | always, unless a guided update ends with no changes |
| `{arch_dir}/.archive/v{N}/` | the main session of `/tachi.architecture` | an existing architecture file was found |

### 8.6 Child processes, checks and scope

**Child processes.** `mmdc` and headless Chromium are spawned by `scripts/extract-report-data.py` when the report assembler renders attack trees and attack chains. They are invisible to session transcripts and to permission rules. Python's `tempfile` and Chromium write to `$TMPDIR`. When `TACHI_MMDC_PUPPETEER_CONFIG` is set, it must be the absolute path of an existing regular file; the extractor then passes it to both `mmdc` invocations as `-p <path>`, and any other value stops the run with an error. The variable exists for sandboxed Linux and WSL2 sessions, where Chromium needs a launch flag that only a puppeteer config file can carry; the runbook covers its use.

**What CI checks.** The guard (`scripts/check-agent-privileges.py`, run by the `tachi-permissions-verify.yml` workflow on pull requests and on pushes to the default branch) fails when:

- an agent's `tools:` or `model:` differs from its row, or its frontmatter has a key outside `name`, `description`, `tools` and `model`;
- a command's frontmatter keys differ from its row;
- a fenced shell block in one of the three Bash-capable agents uses a command family that is not in that agent's Bash families cell;
- a file in `.claude/agents/tachi/` is neither a listed agent nor an allow-listed non-agent document;
- the runbook's write-locations table differs from the Writes cells.

It does not check Tier, Hosts, Dispatches, Bash it instructs or Child processes.

**Scope.** The guard covers `.claude/agents/tachi/**` and `.claude/commands/tachi.*.md`. It does not cover the copies under `adapters/claude-code/agents/`: their 15 files carry no `tools:` and no `model:` key, and by the Claude Code documentation a subagent definition without `tools` inherits every tool available to subagents, while one without `model` runs on the model of the conversation that starts it unless `CLAUDE_CODE_SUBAGENT_MODEL` is set ([subagents: supported frontmatter fields](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields)). Six agents have no adapter copy: `tachi-attack-tree-delta`, `tachi-control-analyzer`, `tachi-human-trust-exploitation`, `tachi-misinformation`, `tachi-output-integrity` and `tachi-report-assembler`. To install or repair agents, re-run `scripts/install.sh`; do not copy files from the adapter directory. Refreshing the adapter roster is tracked separately (#369). The guard does not cover the skills (`.claude/skills/tachi-*/SKILL.md`) either; none of them sets `allowed-tools`, `model` or `tools` at the time of writing.

---

## Cross-references

- Architecture decision: [ADR-041 — Claude Code Permissions Baseline](../architecture/02_ADRs/ADR-041-claude-permissions-baseline.md)
- Source of truth: [`.claude/settings.json`](../../.claude/settings.json)
- Feature spec: [specs/277-claude-permissions-baseline/spec.md](../../specs/277-claude-permissions-baseline/spec.md) (FR-001..FR-014)
- Companion BLP-02 Wave 4 docs feature: [specs/272-security-md-and-private-disclosure-channel/spec.md](../../specs/272-security-md-and-private-disclosure-channel/spec.md) (F-3 — disclosure-channel half of the same Daniel Wood thread)
- Claude Code permissions docs: `https://code.claude.com/docs/en/permissions`
- Claude Code settings docs (cross-file precedence): `https://code.claude.com/docs/en/settings`
- Claude Code subagents docs (`tools:`, model order, nesting): `https://code.claude.com/docs/en/sub-agents`
- Claude Code model configuration docs (alias and subagent model variables): `https://code.claude.com/docs/en/model-config`
- Claude Code permission modes docs: `https://code.claude.com/docs/en/permission-modes`
- Claude Code sandboxing docs (network isolation): `https://code.claude.com/docs/en/sandboxing`
- Claude Code CLI reference (`--disallowedTools`): `https://code.claude.com/docs/en/cli-reference`
- Claude Code tools reference (Glob and Grep availability): `https://code.claude.com/docs/en/tools-reference`
- Header corrections and §8: [specs/391-isolated-auditable-operation/spec.md](../../specs/391-isolated-auditable-operation/spec.md) (FR-003, FR-011, FR-012)
