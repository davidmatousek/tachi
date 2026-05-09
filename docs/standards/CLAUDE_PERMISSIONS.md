# Claude Code Permissions Baseline

**Status**: Active (BLP-02 Wave 4, F-4) | **Source of truth**: [`.claude/settings.json`](../../.claude/settings.json) | **Architecture decision**: [ADR-041](../architecture/02_ADRs/ADR-041-claude-permissions-baseline.md) | **Last updated**: 2026-05-08

---

## 1. Why this baseline exists

Tachi's pre-F-4 `.claude/settings.json` was a 26-rule allow-only file accumulated organically over the project's lifetime. The 2026-05-02 Daniel Wood LinkedIn thread named the resulting posture as a load-bearing gap for enterprise-developer adoption: the file lacked `deny` rules for catastrophic-irreversible operations, lacked `ask` rules for the gray zone, lacked a network host allowlist, lacked per-rule rationale, and matched both `git push` and `git push --force` under a single `Bash(git push:*)` allow rule.

F-4 replaces that file with a curated four-category baseline (this document is its policy decision log) and accepts [ADR-041](../architecture/02_ADRs/ADR-041-claude-permissions-baseline.md) as the architecture-decision artifact. The baseline is **default-secure** for tachi's own development AND for adopters consuming tachi as a scanner. Adopters who need to override a rule have three documented paths (§6).

This document is **self-contained** — a SecOps reviewer auditing tachi's AI-agent permission posture can read this single file end-to-end and produce an audit report without reverse-engineering rule names or maintainer intent. Per-rule rationale lives in §4 and is one-to-one cross-checked against `.claude/settings.json` via the AC-2 verification script (FR-002 in the F-4 spec).

---

## 2. The four categories

The baseline organizes rules into four logical categories. The committed JSON has only the three Claude-Code-native arrays (`permissions.deny`, `permissions.ask`, `permissions.allow`); the four-category framing is a documentation convention used here and in ADR-041.

### Category 1 — Read-only auto-approve

**Safety promise**: non-mutating, no network egress, no shell-out to mutating commands.
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

**Safety promise**: default-deny on outbound network egress; allowlist covers tachi's documented network dependencies after a command-surface egress audit (GitHub family + Anthropic family + OWASP family + MITRE family + NIST).
**JSON array**: `permissions.allow` (`WebFetch(domain:<host>)` patterns).
**Scope**: 19 explicit per-subdomain entries — see §4 table.
**Failure mode**: subdomain matching is **not transitive**. `WebFetch(domain:github.com)` does NOT match `api.github.com`; `WebFetch(domain:*)` wildcard does NOT work as a permissive default. Citations: Claude Code Issues [#15260](https://github.com/anthropics/claude-code/issues/15260), [#11972](https://github.com/anthropics/claude-code/issues/11972), [#1217](https://github.com/anthropics/claude-code/issues/1217). The 19-domain list is the correct posture given upstream behavior. AC-7 retains a manual probe as adversarial verification (FR-007).

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

Adopters who need behavior different from the baseline have three documented override paths. Every legitimate adopter scenario maps to one of these three.

### Path 1 — Per-tool disable via Claude Code CLI flag

For short-term sandbox sessions where the adopter does not want any Bash invocations (or any specific tool surface), use the Claude Code CLI flag where applicable. Example: `claude --deny-tool Bash` for fully disabling Bash within the session. Use case: one-shot sandbox where the operation set is intentionally narrow.

### Path 2 — Fork-and-edit `.claude/settings.json` directly (the load-bearing override path)

For adopters wishing to permit a baseline-denied operation, the **only** working override path is to edit `.claude/settings.json` directly — either by modifying their fork of tachi or by removing the deny rule from their copy of the file. Per §3.2 cross-file deny precedence, adding the same pattern to `.claude/settings.local.json` `permissions.allow` does NOT override the project-level deny.

**Use case**: a personal-fork workflow where the adopter accepts the risk of the denied operation in their controlled environment. The editing should be deliberate and reviewed; commit messages should cite the rationale.

**This is the path the SecOps reviewer asks about** when they ask "what overrides this baseline?" — Path 2 is the answer for permissive-override-of-deny.

### Path 3 — `.claude/settings.local.json` for *adding* personal allows (NOT overriding denies)

For adopters who want to add personal allow rules for operations not denied at the project level — e.g., `Bash(my-deploy-tool:*)` for an internal-only tool — `.claude/settings.local.json` is the supported surface. The file is gitignored by Claude Code convention; it survives `git pull` of baseline updates without manual reconciliation (FR-003).

**Path 3 cannot override a project-level deny** — for that, use Path 2. Path 3 is for the additive permissive-extension case only.

---

## 7. Known limitations

The baseline is calibrated against the casual-typo case. The following limitations are disclosed honestly per ADR-041 §Consequences; adopters requiring stronger guarantees should layer additional defenses (PreToolUse hooks; managed-settings deployment; CI policy gates).

### 7.1 R-8 — Bash pattern fragility

Per Claude Code documentation: *"Bash permission patterns that try to constrain command arguments are fragile."* The baseline's `Bash(rm -rf:*)` deny does not match `bash -c 'rm -rf /tmp/x'` because the `bash -c` wrapper changes the matched string. Documented bypass surfaces include flag variations, extra whitespace, shell variables, redirects, and command substitution. **Calibration: deny rules are casual-typo, not adversarial.** Adversarial bypass is out of F-4 scope.

### 7.2 R-9 — Process-wrapper bypass

Modern dev-environment runners — `npx`, `docker exec`, `devbox run`, `mise exec`, `direnv exec` — re-shell-out commands; the literal-string match against `Bash(rm -rf:*)` does not transit the wrapper. An adopter running `Bash(docker exec my-container rm -rf /workspace)` matches the broader docker-exec invocation but bypasses the inner `Bash(rm -rf:*)` deny. Same calibration as R-8 (casual-typo, not adversarial). Adopters running tachi inside Docker/devbox/mise environments lose the destructive-deny baseline for wrapper-issued commands.

### 7.3 R-10 — Read-only built-in shadow

A future Claude Code update may add a new built-in command that shadows an existing explicit allow rule, making the rule silently no-op. Mitigation: §5 maintenance note instructs re-verification of the built-in set on each `/aod.update` cycle; the AC-2 cross-check catches orphaned rule + table-row pairs.

### 7.4 Subdomain matching is not transitive

`WebFetch(domain:github.com)` does NOT match `api.github.com`; `WebFetch(domain:*)` wildcard does NOT work. Citations: Claude Code Issues [#15260](https://github.com/anthropics/claude-code/issues/15260), [#11972](https://github.com/anthropics/claude-code/issues/11972), [#1217](https://github.com/anthropics/claude-code/issues/1217). The 19-domain explicit list (§4 Category 4 rows) is the correct posture given upstream behavior. If upstream behavior changes to support subdomain collapse, the list MAY be reviewed for compaction in a follow-up Issue (no behavior regression occurs from the explicit-list-too-long case; the regression direction is the explicit-list-too-short case).

### 7.5 What this baseline does NOT protect against

- **Out-of-Claude-Code shell access** — operations performed in a normal terminal outside Claude Code are not subject to these rules.
- **Third-party MCP servers with their own permission scopes** — MCP server permissions are governed by the MCP server's own configuration, not by `.claude/settings.json`.
- **The `--dangerously-skip-permissions` flag** — when invoked with this flag, Claude Code bypasses the entire permissions surface. The flag is an explicit opt-out at the session level; baseline rules do not apply.
- **Adversarial bypass via R-8/R-9** — see §7.1, §7.2.

---

## Cross-references

- Architecture decision: [ADR-041 — Claude Code Permissions Baseline](../architecture/02_ADRs/ADR-041-claude-permissions-baseline.md)
- Source of truth: [`.claude/settings.json`](../../.claude/settings.json)
- Feature spec: [specs/277-claude-permissions-baseline/spec.md](../../specs/277-claude-permissions-baseline/spec.md) (FR-001..FR-014)
- Companion BLP-02 Wave 4 docs feature: [specs/272-security-md-and-private-disclosure-channel/spec.md](../../specs/272-security-md-and-private-disclosure-channel/spec.md) (F-3 — disclosure-channel half of the same Daniel Wood thread)
- Claude Code permissions docs: `https://code.claude.com/docs/en/permissions`
- Claude Code settings docs (cross-file precedence): `https://code.claude.com/docs/en/settings`
