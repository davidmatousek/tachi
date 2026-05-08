---
prd:
  number: 277
  topic: claude-permissions-baseline
  created: 2026-05-08
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-05-08, status: APPROVED, notes: "v1.1 final. Authored as BLP-02 Wave 4 — Claude permissions baseline counterpart to F-3 (#272) disclosure-channel work from the same Daniel Wood 2026-05-02 LinkedIn thread. Scope: curated .claude/settings.json baseline (~80 LOC after Cat-1 dedup; categorized rules read-only / local-state / destructive deny+ask / network host-allowlist), CLAUDE_PERMISSIONS.md ~250 LOC per-rule rationale + audit-ready policy decision log, ADR-041 ~100 LOC with 6 alternatives-considered, CHANGELOG. Cross-list deny→ask→allow precedence honored honestly. Settings-merge precedence (settings.local.json > settings.json) preserves adopter customizations on git pull. v1.0 surfaced 2 BLOCKING (Architect §1.1 schema precedence misclaim, §5.2 missing code.claude.com) + 9 CHANGES_REQUESTED items + 5 Team-Lead non-blocking advisories. v1.1 resolved all 11 Architect items via: schema-reference rewrite to actual cross-list ordering, Category 4 expansion to 18 domains with command-surface egress audit, Category 1 deduplication (built-in read-only commands no longer listed as no-op allow rules — documented in CLAUDE_PERMISSIONS.md §Built-in-Read-Only-Set), Category 3 destructive-operation surface review (dd / mkfs / curl|sh / git filter-branch / npm install -g / etc. with deny-vs-ask placement rationale), AC-7 subdomain-matching verification, ADR-041 alternatives 5+6 (PreToolUse hooks, managed-settings layer), R-3 reframe (two-layer cross-list vs cross-file interaction), new R-8/R-9/R-10 (Bash fragility / wrapper bypass / built-in shadow), JSONC tolerance claim dropped (strict JSON committed), CLAUDE_PERMISSIONS.md §Settings-Precedence worked-example commitment for the git push:* allow + git push --force:* deny case, AC-13 amended with release-please verification (folds Team-Lead A-3), AC-6 sub-checks (JSON validity + git status auto-approve regression — folds Team-Lead A-4). Team-Lead A-1/A-2/A-5 deferred to /aod.spec and /aod.tasks per their framing. ICE 22 (I:8 C:7 E:7); ~8-9h active envelope / next-day wall-clock target."}
  architect_signoff: {agent: architect, date: 2026-05-08, status: APPROVED_WITH_CONCERNS, notes: "v1.1 re-review APPROVED_WITH_CONCERNS. v1.0 surfaced 2 BLOCKING-tier (§1.1 schema precedence misclaim, §5.2 missing code.claude.com) + 9 CHANGES_REQUESTED items. v1.1 resolved 11 of 11 with technical accuracy: schema-reference rewritten to honest cross-list `deny → ask → allow` ordering with worked-example commitment, Category 4 expanded from 7 to 19 domains via tachi command-surface egress audit (GitHub/Anthropic/OWASP/MITRE/NIST), Category 1 deduplicated to ~10 non-built-in rules (Option A; built-ins documented in CLAUDE_PERMISSIONS.md §Built-in-Read-Only-Set), Category 3 destructive-operation surface review added (dd / mkfs / curl|sh / wget|sh / git filter-branch / npm install -g / pip install / eval / chmod -R 000 with deny-vs-ask placement rationale + two excluded with rationale), AC-7 subdomain-matching probe added, ADR-041 alternatives expanded to 6 (PreToolUse hooks + managed-settings layer with rejection rationale), R-3 reframed as Layer 1 cross-list vs Layer 2 cross-file two-layer interaction, R-8/R-9/R-10 added (Bash pattern fragility / process-wrapper bypass via npx-docker-devbox-mise / read-only built-in shadow), JSONC tolerance claim dropped (strict JSON committed; per-rule rationale in CLAUDE_PERMISSIONS.md only via AC-2 cross-check script). Both Team-Lead A-3 (release-please verification merger into AC-13) and A-4 (AC-6 sub-checks: jq JSON validity + git status auto-approve regression + rm -rf deny prompt) folded as claimed. Three minor advisories surface (N-1 cosmetic Category 2 dedup, N-2 R-9 docker-exec explicit-vs-implicit, N-3 Category 4 sub-grouping question for CLAUDE_PERMISSIONS.md) — all /aod.spec-time refinements, not PRD revision blockers. Confidence: HIGH on technical claims; cascade verification clean. Plan readiness: APPROVED. Full v1.0 + v1.1 reviews: .aod/results/architect.md."}
  techlead_signoff: {agent: team-lead, date: 2026-05-08, status: APPROVED_WITH_CONCERNS, notes: "v1.0 APPROVED_WITH_CONCERNS — feasibility, capacity, timeline, dependencies, Wave-4 sequencing all validated. ~8-9h active envelope realistic vs F-3 baseline (3-4h same-day); 2x F-3 to F-4 scaling justified by ADR-041 + settings.json rewrite + CLAUDE_PERMISSIONS.md ~250 LOC dominant cost. Estimate-accuracy: HIGH probability ≤9h envelope hit (~75%); MEDIUM probability next-day wall-clock hit (~60%) sensitive to CLAUDE_PERMISSIONS.md scope discipline. Zero blocking deps; F-260b reviewer-engagement concurrency LOW risk (review-time not implementation-time). 14 mandatory ACs appropriate (matches F-3 count for ~4.5x LOC, calibrated). Five non-blocking advisories: A-1 AC-5 fixture path/contents named at /aod.spec, A-2 CLAUDE_PERMISSIONS.md per-row LOC budget set at /aod.spec, A-3 release-please verification merger into AC-13 (folded into v1.1), A-4 JSON-validity + git-status regression sub-checks into AC-6 (folded into v1.1), A-5 smoke-test parallel scheduling at /aod.tasks. Full review: .aod/results/team-lead.md."}
source:
  idea_id: 277
  story_id: null
---

# F-4 — Claude Permissions Baseline: Product Requirements Document

**Status**: Approved (PM + Architect + Team-Lead sign-offs in)
**Created**: 2026-05-08
**Author**: product-manager
**Reviewers**: architect (APPROVED_WITH_CONCERNS v1.1; 11 of 11 v1.0 items resolved), team-lead (APPROVED_WITH_CONCERNS v1.0; A-3 + A-4 folded into v1.1; A-1/A-2/A-5 deferred to /aod.spec time)
**Phase**: BLP-02 Wave 4 — fourth feature in the 5-feature enterprise hardening initiative; F-1 (#248) Substitution Surface DELIVERED 2026-05-04, F-250 hot-fix DELIVERED 2026-05-04, F-2 (#256) Source-Pattern Hardening DELIVERED 2026-05-05, F-3 (#272) SECURITY.md and Disclosure Channel DELIVERED 2026-05-08
**Priority**: P1 (ICE 22 — I:8 C:7 E:7)

---

## 📋 Executive Summary

### The One-Liner

Replace tachi's current 26-rule allow-only `.claude/settings.json` with a curated, categorized, fully-documented permissions baseline (read-only auto-approve / local-state auto-approve / destructive require-approval / network host-allowlist) plus a self-contained `docs/standards/CLAUDE_PERMISSIONS.md` rule rationale catalog and `ADR-041`, so adopters in managed enterprise developer environments inherit a safe-by-default policy without designing one from scratch — and so existing adopter customizations in `.claude/settings.local.json` survive the upgrade unchanged.

### Problem Statement

The 2026-05-02 LinkedIn thread that triggered BLP-02 contained a load-bearing recommendation from Daniel Wood (the same external reviewer whose thread triggered F-3): *"I would not deploy this into an enterprise developer environment without a hardened Claude permissions profile…"*. F-3 closed the *disclosure-channel* half of that gap (private vulnerability reporting). F-4 closes the *deployment-readiness* half: enterprise developer environments routinely ship with default-deny permissioning policy, and tachi today does not provide one.

The current `.claude/settings.json` shipped with tachi is a 26-rule allow-only file (`/Users/david/Projects/tachi/.claude/settings.json`, last modified 2026-04-19) with these properties:

1. **No `deny` rules.** Truly destructive operations (`rm -rf`, `git push --force`, `git reset --hard`, `gh release delete`, `gh repo delete`) are not blocked. They fall through to Claude Code's default behavior, which prompts the user — but a user under time pressure or unfamiliar with the destructive-vs-recoverable distinction can approve them with one click. An enterprise developer environment expects these to be **default-deny**, not "default-prompt".

2. **No `ask` rules.** Operations that should always prompt (e.g., destructive git, public-state-mutation `gh release create`, network egress to non-allowlisted hosts) are not surfaced as a distinct policy tier. Today the file is binary: in-allow (auto-approve) or not-in-allow (default behavior, which is prompt-on-most-tools but not consistent across tool surfaces).

3. **No network host allowlist.** `WebFetch(domain:*)` is not constrained. Claude Code's default behavior is to prompt on `WebFetch`, but in agentic-mode pipelines under `--dangerously-skip-permissions` (a flag enterprise environments may have policy-locked off but small adopters routinely use), there is no defense-in-depth host filter. An adopter running a tachi command that a third-party MCP server has subverted into making outbound HTTP requests has no host-based safety net beyond Claude Code's built-in defaults.

4. **No per-rule documentation.** Each of the 26 allow rules is a one-line pattern with no rationale comment. A SecOps reviewer auditing the file cannot answer the question "why is `gh pr create:*` auto-approved while `gh release create:*` is not?" without reverse-engineering the maintainer's intent. This is a blocking concern for compliance contexts that require an audit-ready policy decision log per inherited rule.

5. **`Edit` and `Write` are unconditionally auto-approved.** This is correct for a development context but warrants explicit documentation — adopters who deploy tachi into a sandboxed reviewer environment may want `Write` constrained to specific path globs, and the current file gives them no scaffolding to do so.

6. **No bash-pattern destructive denials.** `Bash(git push:*)` is auto-approved without distinguishing `git push` from `git push --force` or `git push --force-with-lease`. The shipped pattern matches both. Enterprise environments expect `--force` variants gated behind explicit approval, not auto-approved alongside their safe siblings.

The five user surfaces this gap leaves exposed:

1. **Enterprise developers adopting tachi in a managed environment** expect a default-deny baseline they can ship as-is into a SecOps-reviewed environment. Today they must design the policy from scratch — either inheriting tachi's permissive default (failing SecOps review) or writing their own ruleset (paying the design cost themselves and risking gaps tachi already encountered).

2. **Security-conscious solo developers** running tachi commands in a fresh repo today get a permissions surface that is broad enough to support all built-in commands but does not block accidental destructive operations. A typo'd `git push --force origin main` from an LLM-driven session has no defense-in-depth gate.

3. **Existing adopters with `.claude/settings.local.json` customizations** need a guarantee that the new baseline does not break their workflow on `git pull`. Claude Code's native settings precedence (`settings.local.json` > `settings.json`) already provides this *mechanically*, but the precedence is not documented in tachi's standards docs, and adopters cannot confirm their customizations survive without manual testing.

4. **SecOps reviewers auditing AI agent permissions** in an organization adopting tachi expect each rule to be documented with its rationale (rule → why → category). Today they get a 26-line allow-list with no rationale, no category breakdown, and no audit trail.

5. **Future external reviewers** (the "future Daniel Wood" persona — community member spotting a posture concern in tachi during their own review) need a documented permissions posture that demonstrates tachi takes managed-environment deployment seriously. The current settings.json + absence of CLAUDE_PERMISSIONS.md surfaces as a posture gap on first contact.

The cross-cutting theme: **F-4 is to permissions posture what F-3 is to disclosure posture.** Both close gaps surfaced by the same Daniel Wood thread; both ship as documentation + small config-file changes; both close enterprise-procurement red flags before the next external-review cycle. F-3 fixed *how* researchers report posture concerns; F-4 fixes *the posture itself* on the most-visible AI-agent surface tachi exposes.

### Proposed Solution

This feature ships as **one feature branch (`277-claude-permissions-baseline`), one squash-merged PR, one `feat(277):` commit subject** that triggers a release-please PR. Four work items:

1. **Curated `.claude/settings.json` baseline (~80 LOC after Category 1 deduplication; was ~120 LOC pre-revision).** Replace the existing 26-rule allow-only file with a four-category structure. The Claude Code `settings.json` schema is **strict JSON** — no `//` comments tolerated (verified against the existing `.claude/settings.json` which is comment-free, and against the Claude Code permissions documentation which does not document JSONC tolerance). Per-rule rationale therefore lives **exclusively in `CLAUDE_PERMISSIONS.md`**, cross-referenced one-to-one with the rules in `.claude/settings.json` via the AC-2 cross-check script.

   - **Category 1: Auto-approve (read-only) — non-redundant rules only** — Inspecting state, reading files, listing resources. No mutation, no network egress, no shell-out to mutating commands. **Important built-in note (per Claude Code permissions docs)**: Claude Code recognizes a built-in read-only set — `ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `diff`, `stat`, `du`, `cd`, and read-only forms of `git` — that runs without a permission prompt in every mode. **Listing built-in-read-only commands in `allow` is no-op.** Category 1 therefore contains only rules that are **not** in the built-in set: `Bash(rg:*)` (ripgrep is not built-in), `Bash(gh issue view:*)`, `Bash(gh issue list:*)`, `Bash(gh pr view:*)`, `Bash(gh pr list:*)`, `Bash(gh pr checks:*)`, `Bash(gh pr diff:*)`, `Bash(gh repo view:*)`, `Bash(gh release view:*)`, `Bash(gh release list:*)`, `Bash(gh search:*)` (gh-* surfaces are not in the built-in read-only set; explicit allow needed). Tier-1 read-only tools (`Read`, `Glob`, `Grep`, `LS`) are auto-approved by Claude Code's built-in tool tiering and do **not** require an `allow` rule. Verified-safe count: **~10 rules** (down from ~25 in v1.0). CLAUDE_PERMISSIONS.md §Built-in-Read-Only-Set documents the redundancy decision, lists the built-in commands that are deliberately omitted, and provides the SecOps-reviewer answer to "why is `Bash(ls:*)` not in this allow list?"

   - **Category 2: Auto-approve (write / local-state)** — Mutates only the local working tree, the local git database, or the local filesystem. Recoverable. No remote-state mutation, no network egress beyond the GitHub API for write operations to *this* repo. Rules: `Edit`, `Write`, `NotebookEdit`, `Bash(mkdir:*)`, `Bash(touch:*)`, `Bash(cp:*)`, `Bash(mv:*)` (qualified — `mv` is recoverable when target is local; cross-tree `mv` outside the project is gated; documented in CLAUDE_PERMISSIONS.md), `Bash(git add:*)`, `Bash(git commit:*)`, `Bash(git checkout:*)` (read-only on main; mutates working tree on branch-switch; recoverable via reflog), `Bash(git stash:*)`, `Bash(git pull:*)` (network-touching but mutates only local working tree; pull-with-rebase failures abort cleanly), `Bash(git push:*)` (network-touching and remote-state-mutating, but the destructive variant `--force` is denied at Category 3; default `git push` is recoverable on remote via reflog and warning systems — auto-approved per current tachi behavior), `Bash(git fetch:*)`, `Bash(make:*)`, `Bash(npm test:*)`, `Bash(npm run:*)`, `Bash(.aod/scripts/bash/*)`, `Bash(source .aod/scripts/bash/*)`, `Bash(gh issue create:*)`, `Bash(gh issue comment:*)`, `Bash(gh issue edit:*)`, `Bash(gh pr create:*)`, `Bash(gh pr comment:*)`, `Bash(gh pr edit:*)`, `Bash(gh pr ready:*)`, `Bash(gh pr review:*)`, `Bash(gh issue edit:*)`. Verified-safe count: ~30 rules. `git push --force` is **not** auto-approved (Category 3).

   - **Category 3: Require approval (destructive / public-state mutation)** — Operations that are irreversible, broadly destructive, or mutate public state in ways that cannot be undone via reflog / local recovery. Implemented as a **two-tier split**: `deny` for catastrophic-irreversible, `ask` for "usually safe but warrants confirmation".

     **Tier 3a — `deny` (catastrophic-irreversible)**: `Bash(rm -rf:*)`, `Bash(rm -fr:*)`, `Bash(rm -Rf:*)`, `Bash(rm --recursive:*)`, `Bash(git push --force:*)`, `Bash(git push -f:*)` (alias), `Bash(git reset --hard:*)`, `Bash(git clean -f:*)`, `Bash(git clean -fd:*)`, `Bash(git branch -D:*)` (force-delete unmerged branch), `Bash(gh release delete:*)`, `Bash(gh repo delete:*)`, `Bash(gh repo archive:*)`, `Bash(gh secret set:*)`, `Bash(gh secret remove:*)`, `Bash(npm publish:*)`, `Bash(dd:*)` (disk-destructive utility), `Bash(mkfs:*)` (filesystem creation), `Bash(curl * | sh)` (pipe-to-shell pattern; documented as bypassable per R-8 but still meaningful for casual-typo case), `Bash(curl * | bash)`, `Bash(wget * | sh)`, `Bash(wget * | bash)`, `Bash(sudo:*)` (privilege escalation never auto-approved).

     **Tier 3b — `ask` (legitimate but warrants confirmation)**: `Bash(git push --force-with-lease:*)` (safer-than-`--force` alternative routinely used in legitimate rebasing flows; `deny` would force per-rebase override and trigger alert fatigue per R-1), `Bash(gh release create:*)` (release publication is reversible-via-deletion but warrants confirmation in semver-pinned-adopter context), `Bash(gh release edit:*)`, `Bash(gh repo edit:*)` (settings mutation), `Bash(gh actions:*)` (workflow modification), `Bash(brew install:*)` (system-level mutation outside repo), `Bash(brew uninstall:*)`, `Bash(npm install -g:*)` (global package install with privilege-escalation potential), `Bash(pip install:*)` (system-wide installs without venv warrant confirmation; in-venv installs are caught at Category 2 via project-local `pip install` patterns), `Bash(git filter-branch:*)` (history rewrite), `Bash(git filter-repo:*)` (modern history rewrite), `Bash(eval:*)` (string evaluation can hide arbitrary commands; ask-tier is calibrated against the alert-fatigue cost of full deny), `Bash(chmod -R 000:*)` (recursive permission lockout — edge case; ask preserves the rare legitimate use).

     **Destructive operation surface review (SecOps audit-ready)**: The deny+ask enumeration above includes every destructive-operation candidate surfaced during PRD review. Two excluded with rationale:
     - `Bash(rm -i:*)` — interactive flag is safe; not in deny.
     - `Bash(git rebase -i:*)` — interactive rebase pattern is workflow-routine; not in deny or ask (Claude Code does not currently invoke it autonomously, and a non-autonomous prompt is the right tier — falls through to default).

     **Verified-safe count**: ~20 deny rules + ~12 ask rules = ~32 Category 3 rules total. **Cross-list precedence**: per Claude Code documentation (https://code.claude.com/docs/en/permissions), permission rules are evaluated **`deny → ask → allow`; first matching rule wins, so deny rules always take precedence**. The baseline relies on this cross-list ordering for cases like `Bash(git push --force:*)` (deny) overriding `Bash(git push:*)` (allow at Category 2) — **not** on a "more-specific-wins-within-a-list" mechanism. CLAUDE_PERMISSIONS.md §Settings-Precedence walks a SecOps reviewer through the deny→ask→allow ordering using the `git push:*` allow + `git push --force:*` deny case as the worked example.

   - **Category 4: Network — Host allowlist (`WebFetch` and `WebSearch`)** — Default-deny on outbound network egress; allowlist host patterns covering tachi's documented network dependencies after a tachi command-surface egress audit.

     **Tachi command-surface egress audit** — Domains observed across `/aod.*` and `/tachi.*` agent invocations (cited from agent files and skill references during PRD review):
     - **GitHub ecosystem (CRITICAL)**: `github.com`, `api.github.com`, `raw.githubusercontent.com`, `githubusercontent.com`, `objects.githubusercontent.com` (release artifact downloads), `codeload.github.com` (archive downloads), `github.io` (used for OpenSSF, MITRE ATLAS, supply-chain reference docs)
     - **Claude / Anthropic ecosystem (CRITICAL)**: `code.claude.com` (Claude Code documentation; tachi agents fetching Claude Code docs would otherwise be blocked or prompt-flooded), `docs.anthropic.com`, `anthropic.com`, `claude.com`, `platform.claude.com`
     - **OWASP reference content (used by tachi threat agents)**: `owasp.org`, `cheatsheetseries.owasp.org`, `genai.owasp.org` (LLM/GenAI top-10 references)
     - **MITRE / ATT&CK reference content (used by STRIDE+AI threat agents)**: `mitre.org`, `attack.mitre.org`, `atlas.mitre.org`
     - **Other reference content**: `csrc.nist.gov` (NIST CSF and AI RMF citations used in compensating-controls agent)

     **Allowlist rules**: `WebFetch(domain:github.com)`, `WebFetch(domain:api.github.com)`, `WebFetch(domain:raw.githubusercontent.com)`, `WebFetch(domain:githubusercontent.com)`, `WebFetch(domain:objects.githubusercontent.com)`, `WebFetch(domain:codeload.github.com)`, `WebFetch(domain:github.io)`, `WebFetch(domain:code.claude.com)`, `WebFetch(domain:docs.anthropic.com)`, `WebFetch(domain:anthropic.com)`, `WebFetch(domain:claude.com)`, `WebFetch(domain:platform.claude.com)`, `WebFetch(domain:owasp.org)`, `WebFetch(domain:cheatsheetseries.owasp.org)`, `WebFetch(domain:genai.owasp.org)`, `WebFetch(domain:mitre.org)`, `WebFetch(domain:attack.mitre.org)`, `WebFetch(domain:atlas.mitre.org)`, `WebFetch(domain:csrc.nist.gov)`. **Subdomain-matching semantics — to be verified by AC-7 smoke-test and documented in CLAUDE_PERMISSIONS.md**: Claude Code's `WebFetch(domain:<host>)` rule is documented as matching fetches to `<host>`, but subdomain-matching semantics are not unambiguously specified in upstream docs. AC-7 explicitly verifies whether `WebFetch(domain:github.com)` matches subdomains (`api.github.com`, `raw.githubusercontent.com`); if it does, the allowlist can collapse to root domains. If not, the explicit per-subdomain entries above are required (current PRD posture).

     All other domains fall through to `ask` (Claude Code default for `WebFetch`), preserving the user-prompt safety net for unanticipated egress. `WebSearch` is left at default (`ask` in Claude Code built-in behavior); allowlisting `WebSearch` to specific query patterns is not feasible at the schema level. **Adopter customization**: adopters whose workflows fetch from non-allowlisted domains (PyPI, npmjs, internal company domains, Stripe/Slack/etc.) add their domains to `.claude/settings.local.json` `allow` per CLAUDE_PERMISSIONS.md §Adopter-Customization — narrow-default-plus-easy-override is the calibrated posture.

2. **`docs/standards/CLAUDE_PERMISSIONS.md` (~250 LOC).** Self-contained policy decision log. Sections:

   - **Why this baseline exists.** One-paragraph framing: who it serves (enterprise SecOps reviewers, security-conscious solo adopters), what tier it sits at (default-deny on destructive, allowlist on network, auto-approve on read-only and recoverable-local-state), and how it is meant to be customized (`.claude/settings.local.json` overrides — see Settings Precedence section).

   - **The four categories.** Description of each category, the safety promise (or absence) of each, and the explicit failure modes the category is meant to prevent.

   - **Settings precedence (load-bearing for AC-3).** Documents Claude Code's native precedence: `.claude/settings.local.json` > `.claude/settings.json` > Claude Code default. Worked example: an adopter's `settings.local.json` containing `Bash(git push --force:*)` in `allow` overrides the baseline's `deny` on the same rule for that adopter's local environment. SecOps reviewers can detect such overrides by diffing `settings.local.json` against the baseline. Reverse direction: an adopter who wants the baseline more strictly can add additional `deny` rules to `settings.local.json` without touching the shipped file.

   - **Rule-by-rule rationale.** Tabular: Rule | Category | Rationale | Failure mode if this rule were missing. ~80 rules total across the four categories.

   - **Opt-out paths.** Three documented paths for adopters who want pre-baseline behavior: (a) rename `.claude/settings.json` → `.claude/settings.json.disabled` (full disable), (b) override specific rules in `.claude/settings.local.json` (surgical override), (c) fork tachi and modify the baseline directly (full takeover). Each path documents the trade-off (loss of upstream updates vs surgical control vs maintenance overhead).

   - **Audit trail and policy decision log.** A SecOps reviewer should be able to read CLAUDE_PERMISSIONS.md as a complete policy decision log without external context. This is a hard requirement (per Issue #277 §Definition-of-Done line: *"a reader unfamiliar with tachi can understand each rule's rationale without external context"*).

   - **Known limitations.** Pattern-matching limitations (e.g., `Bash(git branch:*)` matches both safe and destructive variants — mitigation via reflog), Claude Code version compatibility (minimum supported version documented), and what the baseline does **not** protect against (out-of-Claude-Code shell access, third-party MCP servers with their own permission scopes, the `--dangerously-skip-permissions` flag).

3. **`ADR-041 — Claude Code Permissions Baseline` (~100 LOC; was ~80 LOC pre-revision).** Architecture decision record covering:
   - (a) The four-category structure as the chosen design.
   - (b) The cross-list `deny → ask → allow` precedence reliance (per Claude Code permissions docs) and what breaks if a future Claude Code version changes precedence semantics.
   - (c) The opt-out posture (`settings.json.disabled` rename, settings.local.json override, fork) as the supported customization paths.
   - (d) Why network egress uses `WebFetch(domain:*)` allowlisting rather than a separate egress proxy or per-skill explicit allow.

   **Alternatives considered** (each with rejection rationale):
   1. **Two-tier flat allow/deny** — collapses Category 1+2 into one allow list, Category 3 into one deny list. Rejected: loses the calibrated `ask` tier, forcing alert-fatigue trade-off (R-1) on operations like `git push --force-with-lease` and `gh release create`.
   2. **Four-tier as proposed** (deny / ask / allow read-only / allow local-state) — chosen design. The "four categories" framing is a CLAUDE_PERMISSIONS.md documentation construct over the underlying three-list (`deny`/`ask`/`allow`) Claude Code schema.
   3. **Tag-based per-rule annotation** — per-rule metadata (e.g., `category: read-only`, `risk-tier: low`) embedded in the schema. Rejected: not supported by Claude Code's schema; would require upstream change.
   4. **Separate per-skill files** (e.g., `.claude/permissions/{tachi-agent}.json` partial files) — Rejected: not supported by Claude Code's schema; would require upstream change. The shipped `.claude/settings.json` is project-wide.
   5. **PreToolUse hook-based deny** — Claude Code docs explicitly recommend PreToolUse hooks for argument-pattern constraints (e.g., URL-filtering on `curl`, tighter `git push --force` matching). Rejected: hooks add code surface and review burden inconsistent with the BLP-02 docs-only-no-code posture; hook-based defenses are documented in CLAUDE_PERMISSIONS.md §Defense-in-Depth as adopter-implementable extensions but are out of scope for the shipped baseline.
   6. **Managed-settings layer** (`allowManagedPermissionRulesOnly: true` in MDM/OS-policy settings) — distribute the baseline via Claude Code's managed-settings deployment mechanism instead of `.claude/settings.json` checked into the repo. Rejected: managed-settings is a deployment option for *adopters' enterprise environments*, not for tachi-the-shipped-template; tachi targets solo-and-team adopters who do not run managed-settings infrastructure. CLAUDE_PERMISSIONS.md §Defense-in-Depth documents managed-settings as an adopter-implementable extension for environments that already run MDM/OS-policy.

4. **CHANGELOG entry under Unreleased → Changed**: `.claude/settings.json restructured to four-category permissions baseline (read-only auto-approve / local-state auto-approve / destructive deny+ask / network host-allowlist); CLAUDE_PERMISSIONS.md added as audit-ready policy decision log; ADR-041 accepted; existing settings.local.json customizations preserved via Claude Code native precedence.`

**Three things this feature is deliberately NOT:**

1. It is **not** an external authorization service or per-rule audit-log emitter. The baseline is static configuration; it does not phone home, log to a remote service, or emit per-rule decision events. SecOps environments that require runtime permission audit logging must layer their own observability on top of Claude Code's built-in transcript logs.

2. It is **not** a `finding.yaml` / taxonomy schema change and **not** a tachi command/agent/skill/script behavior change. **Eleventh feature in a row with zero `finding.yaml` shape change** (continues BLP-01 detection-tier contract continuity past F-3). The only files touched are `.claude/settings.json` (rewrite), `docs/standards/CLAUDE_PERMISSIONS.md` (new), `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md` (new), and `CHANGELOG.md` (Unreleased entry). Optional README pointer (~1 LOC) in line with the F-3 precedent.

3. It is **not** a replacement for Claude Code's `--dangerously-skip-permissions` flag protection. An adopter who runs tachi commands under `--dangerously-skip-permissions` bypasses the entire `permissions` block; CLAUDE_PERMISSIONS.md documents this as a known limitation and recommends managed environments policy-lock the flag off (typically via `claude.json` `defaultMode` setting or wrapper-script enforcement). The baseline operates at the `permissions:` schema layer; the unsafe-mode flag operates at a higher precedence layer outside this PRD's scope.

---

## 🎯 Goals & Non-Goals

### Goals

- **G1**: Adopters cloning tachi into a managed enterprise developer environment inherit a default-deny posture on destructive operations, default-ask on calibrated-risky operations, default-allow on read-only and recoverable-local-state operations, and host-allowlisted network egress. Verified by reviewer diff-inspection of the four-category file structure and reviewer behavior smoke-test (Section "Regression Protection Plan" verification).
- **G2**: Each rule in the baseline has a documented rationale in CLAUDE_PERMISSIONS.md. Verified by reviewer cross-check: every rule in `.claude/settings.json` appears in the CLAUDE_PERMISSIONS.md rule-by-rule table with category, rationale, and failure-mode-if-missing entries.
- **G3**: Existing adopter customizations in `.claude/settings.local.json` survive the baseline upgrade unchanged. Verified by snapshot test: snapshot a representative `.claude/settings.local.json` (e.g., the founder's own); after the baseline lands, run `claude --check-config` (or equivalent dry-run) and confirm none of the baseline's rules override more-specific local rules. Per Claude Code's documented precedence (`settings.local.json` > `settings.json`), this is mechanically true; the verification step exists to defend against subtle path-glob ambiguities.
- **G4**: SecOps reviewer reading CLAUDE_PERMISSIONS.md as their first introduction to tachi can produce an audit-ready policy decision log without further questions. Verified by PM walk-through of CLAUDE_PERMISSIONS.md as a SecOps-reviewer-persona; rationale must be self-contained per Issue #277 §Definition-of-Done.
- **G5**: Common AOD/tachi commands continue to operate without unexpected approval prompts when run against a fresh clone of tachi with the baseline active. Verified by behavior smoke-test against `/aod.discover`, `/aod.spec`, `/aod.build`, `/tachi.architecture`, `/tachi.threat-model`, `/tachi.risk-score`, `/tachi.compensating-controls`, `/tachi.infographic`, `/tachi.security-report`. Approval gates fire on `git push --force` and other Category 3 rules (expected); read-only and recoverable-local-state operations proceed without prompt.
- **G6**: Opt-out path verified by smoke test: rename `.claude/settings.json` → `.claude/settings.json.disabled`; confirm Claude Code reverts to its default permissions behavior; confirm tachi commands still run (with default-prompt cadence).
- **G7**: ADR-041 lands in `docs/architecture/02_ADRs/` with status `Accepted` after PM + Architect sign-off.
- **G8**: BLP-02 Wave 4 closed. Verified by Initiative Tracker memory update and the BLP-02 enterprise-hardening posture-summary referencing F-4 closure.
- **G9**: Post-merge `/security` re-scan: zero new findings emerge in the `.claude/settings.json` surface. Issue #277 §Definition-of-Done explicitly requires this. (Note: F-4 does not close any pre-existing `/security` finding because the 2026-05-02 scan did not surface a permissions-config finding — F-4 is a *posture-strengthening* feature, not a *finding-closure* feature, distinct from F-1/F-2/F-3.)

### Non-Goals

- **NG1**: No external authorization service or runtime permission-audit-log emitter. The baseline is static configuration.
- **NG2**: No `finding.yaml` / taxonomy schema changes.
- **NG3**: No tachi agent / command / skill / script behavior changes — the only behavior change is that more operations now require approval (Category 3).
- **NG4**: No protection against `--dangerously-skip-permissions` flag bypass. Documented as a known limitation in CLAUDE_PERMISSIONS.md with recommended mitigation (managed-environment policy-lock).
- **NG5**: No per-skill or per-agent permission scoping. The baseline is project-level; per-skill overrides are not a Claude Code schema feature today and would require an upstream Claude Code change to support.
- **NG6**: No protection for adopter-modified `stacks/*/scaffold/` output (post-`make scaffold` customizations). Adopters retain ownership of their post-scaffold permissions surfaces; the baseline applies only to the tachi-shipped `.claude/settings.json`.
- **NG7**: No bug-bounty incentive for finding gaps in the baseline. Researchers reporting baseline gaps follow the F-3-shipped private vulnerability reporting flow.

---

## 👥 User Stories

(Adopted verbatim from Issue #277 §Stories.)

### US-1: Enterprise developer in a managed environment
> As an enterprise developer adopting tachi in a managed environment, I want to inherit a permissions baseline that auto-approves safe operations and gates risky ones, so that I don't have to design the policy from scratch.

**Acceptance**: `.claude/settings.json` ships with the four-category structure; `CLAUDE_PERMISSIONS.md` documents every rule's rationale; SecOps review of the file produces no follow-on policy questions before adoption.

### US-2: Security-conscious solo developer
> As a security-conscious solo developer, I want safe-by-default permissions, so that running tachi commands in a fresh repo doesn't accidentally execute unexpected operations.

**Acceptance**: Cloning tachi and running `/aod.discover`, `/aod.spec`, `/aod.build` produces no destructive operations without approval prompt. `git push --force` triggers an explicit deny + confirmation; `rm -rf` triggers an explicit deny + confirmation; default `git push`, `git commit`, `gh pr create` proceed without prompt.

### US-3: Existing adopter with local customizations
> As an existing adopter with my own `.claude/settings.local.json` customizations, I want my customizations preserved when the baseline lands, so that my workflow doesn't break on `git pull`.

**Acceptance**: Adopters who already have `.claude/settings.local.json` overrides — e.g., a custom `Bash(my-deploy-tool:*)` allow rule — retain those overrides after pulling the baseline. Documented in CLAUDE_PERMISSIONS.md §Settings-Precedence with worked example. Smoke-tested against the founder's actual `settings.local.json`.

### US-4: SecOps reviewer auditing AI agent permissions
> As a SecOps reviewer auditing AI agent permissions in our org, I want each tachi-shipped permission rule to be documented with its rationale (rule → why), so that I can produce an audit-ready policy decision log.

**Acceptance**: `docs/standards/CLAUDE_PERMISSIONS.md` table maps every rule in `.claude/settings.json` to its category, rationale, and failure-mode-if-missing. Reading CLAUDE_PERMISSIONS.md alone (no other tachi docs) is sufficient for the reviewer to produce their org's policy decision log. Verified by PM persona-test (PM reads CLAUDE_PERMISSIONS.md as a SecOps reviewer; no follow-on questions surface).

### US-5: Future external reviewer (Daniel Wood persona)
> As a future Daniel Wood (an external reviewer who would have flagged tachi's lack of a hardened Claude permissions profile), I want a documented permissions posture so that absence-of-baseline doesn't surface as an enterprise-deployment red flag.

**Acceptance**: External reviewer scanning tachi's repo finds `.claude/settings.json` with category-grouped rules and `CLAUDE_PERMISSIONS.md` as the audit-ready rationale catalog. The 2026-05-02-style "I would not deploy this without a hardened profile" gap is closed at the file-existence-and-content level.

---

## ✅ Acceptance Criteria

(Adopted from Issue #277 §Definition-of-Done with v1.0 PRD additions.)

### Mandatory (blocks delivery)

- [ ] **AC-1**: `.claude/settings.json` lands with four-category structure (read-only / local-state / destructive / network). Each category is a contiguous block; rules are sorted alphabetically within categories for diff stability.
- [ ] **AC-2**: Each rule in `.claude/settings.json` has a corresponding row in the `docs/standards/CLAUDE_PERMISSIONS.md` rule-by-rule table. Cross-reference verified by AC-2 operational check: `python3 .aod/scripts/python/permissions-cross-check.py` (or equivalent shell script that parses both files and reports unmatched rules) passes with zero unmatched rules.
- [ ] **AC-3**: `docs/standards/CLAUDE_PERMISSIONS.md` is self-contained — a reader unfamiliar with tachi can understand each rule's rationale without external context. Verified by PM persona-test (PM reads as SecOps reviewer; no follow-on questions surface).
- [ ] **AC-4**: Settings precedence is documented in CLAUDE_PERMISSIONS.md §Settings-Precedence with a worked example showing how `settings.local.json` overrides `settings.json` for a specific rule.
- [ ] **AC-5**: Existing-customization preservation verified via snapshot test — snapshot the founder's actual `.claude/settings.local.json` (or, if absent, a representative adopter `settings.local.json`), apply the baseline, confirm none of the baseline's rules override more-specific local rules. Document the test artifact (snapshot file path or inline diff) in the delivery PR description.
- [ ] **AC-6**: Behavior smoke-test for AOD lifecycle commands — fresh-clone tachi, run `/aod.discover` and `/aod.spec` end-to-end (full execution; both are short-running and idempotent for smoke purposes), and run `/aod.build` in **abbreviated mode** (i.e., interrupt after Step 2 or run only `/aod.spec` portion of the chain — `/aod.build` does not have a documented `--dry-run` flag, so the operational smoke-test path is "start `/aod.build` → confirm no unexpected approval prompts fire on the first 2-3 tool invocations → interrupt before Wave-1 delegate kicks off"). Verify expected approval gates fire (`git push --force` → deny prompt; `git status` → no prompt — validates that the existing AOD agent reliance on `git status` auto-approval is preserved). **Sub-checks**: (a) `jq . .claude/settings.json` exits 0 (settings.json is valid JSON); (b) `Bash(git status)` auto-approves with no prompt during smoke-test (verifies pattern-overlap regression doesn't sneak in); (c) `Bash(rm -rf:*)` triggers a deny prompt when invoked through Bash. Document smoke-test result in delivery PR description.
- [ ] **AC-7**: Behavior smoke-test for tachi commands — fresh-clone tachi, run `/tachi.architecture`, `/tachi.threat-model`, `/tachi.risk-score`, `/tachi.compensating-controls` against an example architecture. Verify each command runs end-to-end without being blocked by the new baseline. **Subdomain-matching verification**: explicitly probe whether `WebFetch(domain:github.com)` matches subdomain `api.github.com` and `raw.githubusercontent.com` during the smoke-test (e.g., by observing whether per-subdomain entries are required for tachi agents fetching from `raw.githubusercontent.com`). If subdomain-matching IS supported, the allowlist can collapse to root domains and CLAUDE_PERMISSIONS.md §Network-Allowlist documents the collapsed form. If NOT supported, the explicit per-subdomain rules in Category 4 are required and documented as such. Document smoke-test result and subdomain-semantics finding in delivery PR description.
- [ ] **AC-8**: Cross-version compatibility — document the minimum Claude Code version supported by the baseline in CLAUDE_PERMISSIONS.md §Known-Limitations. Test against current Claude Code (v2.1.x). The minimum is the lowest version that supports the `permissions.deny` and `permissions.ask` keys; documented as a citation to Claude Code release notes.
- [ ] **AC-9**: Opt-out smoke test — rename `.claude/settings.json` → `.claude/settings.json.disabled` in the working tree (do not commit), verify Claude Code reverts to default permissions behavior, verify a representative tachi command (`/tachi.architecture`) still completes (with default-prompt cadence). Document result in delivery PR description.
- [ ] **AC-10**: ADR-041 lands at `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md` with status `Accepted` after PM + Architect sign-off.
- [ ] **AC-11**: All Regression Protection Plan checks pass (per Issue #277 §Regression-Protection-Plan). Mapped to AC-5 through AC-9 above; AC-11 acts as the umbrella check.
- [ ] **AC-12**: CHANGELOG entry under `Unreleased → Changed` references the baseline restructure, CLAUDE_PERMISSIONS.md, and ADR-041.
- [ ] **AC-13**: Post-merge verification — both **(a)** post-merge `/security` re-scan: zero new findings emerge in the `.claude/settings.json` surface this feature touched (LOW or INFO findings on unrelated surfaces are acceptable side-effect findings); **and (b)** release-please PR opens within ~30s of squash-merge per `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles. If release-please PR is absent at the 30s mark, push an empty `feat(277): claude permissions baseline — release marker` commit per the F-212-incident recovery flow. Both checks land in the delivery PR description as confirmation evidence.
- [ ] **AC-14**: README.md gets a one-line pointer to CLAUDE_PERMISSIONS.md (e.g., a "Security" or "Permissions" subsection): *"For permissions configuration, see [CLAUDE_PERMISSIONS.md](docs/standards/CLAUDE_PERMISSIONS.md)."* Promoted from deferred per F-3 precedent (one-line README delta carries zero scope-creep risk and eliminates a stale follow-on Issue).

### Nice-to-have (post-merge follow-up; not blocking)

- [ ] **AC-15**: Open a follow-up backlog Issue for a **CI workflow that validates the cross-reference between `.claude/settings.json` and `CLAUDE_PERMISSIONS.md`** on every PR. Concrete probe: GitHub Actions job runs the AC-2 cross-check script and fails the build if rules drift. Park as low-priority follow-on; not in F-4 scope.
- [ ] **AC-16**: Open a follow-up backlog Issue for a **`make permissions-audit` target** that prints the diff between `.claude/settings.json` and `.claude/settings.local.json` for adopter SecOps reviewers. Park as low-priority follow-on; not in F-4 scope.

---

## 🛠️ Technical Considerations

### File Surface

- **`.claude/settings.json`** (rewrite, ~80 LOC after Category 1 deduplication). Replaces the existing 26-rule allow-only file (`/Users/david/Projects/tachi/.claude/settings.json`, last modified 2026-04-19). Structure: top-level `permissions: { allow: [...], ask: [...], deny: [...] }` plus the existing `hooks:` block (preserved verbatim). Rules sorted alphabetically within each list for diff stability. **Strict JSON, no comments** — per-rule rationale lives in CLAUDE_PERMISSIONS.md only.
- **`docs/standards/CLAUDE_PERMISSIONS.md`** (new, ~250 LOC). Self-contained policy decision log. Located alongside other standards docs (`DEFINITION_OF_DONE.md`, `GIT_WORKFLOW.md`, `NAMING_GUIDELINES.md`, etc.).
- **`docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md`** (new, ~100 LOC). ADR template (`docs/architecture/02_ADRs/ADR-000-template.md`) instantiated with the four-category structure decision and six alternatives-considered (two-tier flat / four-tier as proposed / tag-based annotation / per-skill files / PreToolUse hook-based deny / managed-settings layer). Status: `Accepted` after PM + Architect sign-off at delivery.
- **`CHANGELOG.md`** (~3 LOC). New entry under existing `## Unreleased → ### Changed` block. No new heading.
- **`README.md`** (~1 LOC). One-line pointer to CLAUDE_PERMISSIONS.md per AC-14. Inserted under existing "Standards" or top-level "Security" subsection — exact insertion point chosen at /aod.spec time.
- **No code changes.** No agent / command / skill / script / contract / schema modifications.

### Schema Reference

The Claude Code `.claude/settings.json` schema supports three rule lists at `permissions.{allow|ask|deny}`. Each list contains string patterns of the form `<Tool>` (matches all uses of that tool) or `<Tool>(<arg-pattern>)` where `<arg-pattern>` is tool-specific:

- For `Bash`: `Bash(<command>:*)` matches any invocation of `<command>` with any arguments (`:*` is documented as an equivalent way to write a trailing wildcard, usable only at end-of-pattern). `Bash(<full-command-including-flag>:*)` matches more specifically.
- For `WebFetch`: `WebFetch(domain:<host>)` matches outbound HTTP to `<host>`. Subdomain-matching semantics are not unambiguously specified in upstream Claude Code documentation; the baseline allowlists per-subdomain explicitly until AC-7 smoke-test verifies whether root-domain rules cover subdomains.
- For `Edit` / `Write` / `NotebookEdit`: bare tool name matches all uses. Note: `Read` / `Glob` / `Grep` / `LS` are tier-1 read-only Claude Code tools auto-approved by built-in tool tiering — they do **not** require `allow` rules.

**Rule precedence** (per Claude Code permissions documentation at https://code.claude.com/docs/en/permissions):
- *Within a settings file*: rules are evaluated `deny → ask → allow`; **first matching rule wins, so deny rules always take precedence**. This is **cross-list ordering**, not "more-specific-wins-within-a-list."
- *Across settings files*: managed > CLI args > settings.local.json > settings.json > user-global. **If a tool is denied at any level, no other level can allow it** (managed-deny > project-deny > local-allow).
- The `Bash(git push --force:*)` deny case overrides `Bash(git push:*)` allow because `deny` is checked first in the merged ruleset, **not** because the deny pattern is more specific. CLAUDE_PERMISSIONS.md §Settings-Precedence walks a SecOps reviewer through this with the exact `git push:*` allow + `git push --force:*` deny worked example.

**Bash pattern fragility (per upstream Claude Code documentation)**: *"Bash permission patterns that try to constrain command arguments are fragile."* Documented bypass surfaces include flag variations (`-f` vs `--force`), extra whitespace, shell variables, redirects, command substitution, and process wrappers. The baseline's `Bash(git push --force:*)` deny is **meaningful for the casual-typo case** but **not a guarantee against determined bypass**. CLAUDE_PERMISSIONS.md §Known-Limitations enumerates the bypass surface and documents PreToolUse hooks (out of F-4 scope; adopter-implementable) as the recommended defense-in-depth for environments that require strict guarantees.

**Process-wrapper handling (per upstream Claude Code documentation)**: Claude Code strips a documented set of process-wrapping commands (`timeout`, `time`, `nice`, `nohup`, `stdbuf`) before pattern matching. Modern dev-environment runners — `npx`, `docker exec`, `devbox run`, `mise exec`, `direnv exec` — are **NOT** stripped. Adopters running tachi commands inside a Docker container or devbox/mise environment may bypass the destructive-operation deny baseline. R-9 documents this risk; CLAUDE_PERMISSIONS.md §Known-Limitations documents the wrapper-bypass surface for managed-environment adopters.

Schema citation: Claude Code documentation for `.claude/settings.json` (https://code.claude.com/docs/en/permissions). Minimum version supported by the baseline (per AC-8): the lowest Claude Code version that supports both `ask` and `deny` keys — documented in CLAUDE_PERMISSIONS.md §Known-Limitations as a citation to Claude Code release notes at PR-merge time.

### Cross-Reference: BLP-02 Wave Sequencing

| Wave | Feature | Issue | Status | Closure date |
|------|---------|-------|--------|--------------|
| 1 | F-1 Substitution Surface Hardening | #248 | Delivered | 2026-05-04 |
| 1 follow-on | F-250 Adversarial Unit Extraction Hot-Fix | #250 | Delivered | 2026-05-04 |
| 2 | F-2 Source-Pattern Hardening | #256 | Delivered | 2026-05-05 |
| 3 | F-3 SECURITY.md and Private Disclosure Channel | #272 | Delivered | 2026-05-08 |
| **4** | **F-4 Claude Permissions Baseline** | **#277** | **In review (this PRD)** | **target 2026-05-09 / 2026-05-10** |
| 5 | F-constitution-sed migration | TBD | Backlog | TBD |

F-4 is **independent of F-1/F-2/F-3** — Issue #277 §Dependencies is explicit on this. Could ship in parallel with F-5 if F-5 is scoped before F-4 lands. Wave 4 sequencing chosen because F-4 is the natural follow-on to F-3 (both close gaps from the Daniel Wood thread) and F-5 is still TBD.

### Release-Please Trigger Posture

The PR title MUST be `feat(277): claude permissions baseline` (Conventional Commit format with `feat:` prefix per `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles). Per the F-212 close-out incident reference in that file and the F-3 (#272) precedent, post-merge verification at `/aod.deliver` time MUST confirm a release-please PR opens within ~30s of the squash-merge; if not, push an empty `feat(277): … — release marker` commit per the documented recovery flow. This feature is configuration + documentation + ADR; the `.claude/settings.json` surface is **adopter-visible** (every adopter inherits the baseline) and meets the `feat:` threshold per the rule's "Default to feat:" guidance for any user-visible work.

### Security & Privacy

- **No new code paths.** The baseline is static configuration; no runtime behavior changes in tachi commands, agents, or skills.
- **Defense-in-depth.** The baseline does not replace Claude Code's built-in permission prompts; it strengthens them by moving destructive operations from the default-prompt tier to the explicit-deny tier and by adding a network host allowlist.
- **Reversible.** Adopters can opt out via three documented paths (file rename, `settings.local.json` override, fork). No irreversible repo-state mutation.
- **Settings.local.json precedence preserved.** Adopters' personalization data in `settings.local.json` continues to override the baseline; the baseline does not introduce a new precedence layer.
- **No telemetry or remote inference.** Configuration stays local; no phone-home behavior introduced.
- **Out-of-scope for adopters' personalization data.** Adopter-modified `.claude/settings.local.json` content remains adopter-owned; the F-3-shipped SECURITY.md scope explicitly excludes adopter personalization, which transitively applies to F-4.

### Regression Protection Plan (mapped from Issue #277)

| Check | AC mapping | Verification command |
|-------|-----------|---------------------|
| Existing-customization preservation | AC-5 | Snapshot adopter `settings.local.json`; apply baseline; diff post-state |
| Behavior smoke-test (AOD commands) | AC-6 | Fresh-clone + `/aod.discover` + `/aod.spec` end-to-end + `/aod.build` abbreviated (interrupt before Wave-1 delegate kicks off; `/aod.build` lacks a `--dry-run` flag) |
| Behavior smoke-test (tachi commands) | AC-7 | Fresh-clone + `/tachi.architecture` + `/tachi.threat-model` + `/tachi.risk-score` |
| Cross-version compatibility | AC-8 | Test against Claude Code v2.1.x; document min-version in CLAUDE_PERMISSIONS.md |
| Opt-out smoke test | AC-9 | Rename `.claude/settings.json` → `.disabled`; run `/tachi.architecture` |
| No-regress on tachi's own commands | AC-7 | Subset of AC-7; each `/tachi.*` runs end-to-end |

---

## ⚠️ Risks & Mitigations

### R-1: Approval-fatigue from over-broad Category 3 deny list (HIGH likelihood absent calibration; LOW residual after design)

**Risk**: A Category 3 deny list that catches too many legitimate workflows triggers approval prompts for routine operations, training adopters to click-through approvals reflexively — the same "alert fatigue" failure mode that erodes SecOps team responsiveness in over-tuned IDS/IPS rules. Concrete failure mode: an adopter doing legitimate `git push --force-with-lease` rebases sees 5+ approval prompts per session, develops muscle-memory click-approve behavior, and then approves an actual destructive `git reset --hard` without reading.

**Mitigation**: Baseline calibrates Category 3 into two tiers — **`deny` for catastrophic-irreversible** (`rm -rf`, `git push --force` (without `-with-lease`), `git reset --hard`, `gh secret set/remove`, `npm publish`, `sudo`) and **`ask` for usually-safe-but-warrants-confirmation** (`git push --force-with-lease`, `gh release create`, `gh release edit`, `gh repo edit`, `brew install`). The two-tier split keeps deny narrow enough to remain meaningful (deny rules fire rarely; when they fire, the user pays attention) and uses `ask` for the broader gray-zone. CLAUDE_PERMISSIONS.md §Calibration documents the deny-vs-ask placement decision per rule with the alert-fatigue rationale. Reviewer-validation of calibration at PRD review and at code-review time.

### R-2: Regression on built-in tachi commands due to over-restrictive baseline (MEDIUM)

**Risk**: A baseline rule unexpectedly blocks a tachi command that was previously working under the permissive default. Concrete failure mode: a `/tachi.threat-model` invocation needs to fetch an OWASP reference page from a domain not in the Category 4 allowlist, the request gets prompted, and the command blocks until the user notices.

**Mitigation**: AC-7 mandates a fresh-clone behavior smoke-test against every shipped `/tachi.*` command end-to-end. AC-6 covers AOD lifecycle commands. The Category 4 host allowlist is explicit about which OWASP / Anthropic / GitHub domains are permitted; if an unexpected domain surfaces during smoke-test, the baseline gets updated before merge, not after. Residual risk: a less-frequent command (e.g., `/tachi.security-report` exotic Typst-fetch path) might use a domain not exercised in smoke-test; mitigated by the AC-15 follow-on CI cross-check job that catches drift on every PR post-merge.

### R-3: settings.local.json + cross-list precedence interaction may surprise adopters (LOW)

**Risk**: Claude Code's documented precedence has two layers that interact non-obviously. **Layer 1 — within-merged-ruleset**: `deny → ask → allow`, first match wins. **Layer 2 — across files**: managed > CLI args > settings.local.json > settings.json > user-global, and **deny at any layer cannot be overridden by allow at a lower layer**. An adopter who has `Bash(git push --force-with-lease:*)` in `settings.local.json` `allow` (intending to whitelist their workflow) may expect their local allow to override the project's `ask` rule on the same pattern. Per Layer 1, the merged ruleset evaluates `deny → ask → allow` first-match-wins, so the project's `ask` fires first and the local `allow` never applies. The "local wins" intuition holds for cross-file *priority resolution* but does not bypass cross-list *evaluation order*.

**Mitigation**: CLAUDE_PERMISSIONS.md §Settings-Precedence walks adopters through both layers with two worked examples: (a) the `git push:*` allow + `git push --force:*` deny case (cross-list ordering — deny wins because it's evaluated first); (b) the local-allow + project-ask case (Layer 2 priority sets local-allow above project-ask in *file priority*, but Layer 1 ordering still evaluates the project's `ask` before `allow` within the merged set). Adopters who want broader local override must move the rule to an even-higher-priority file (managed settings) or remove the conflicting project rule via fork. Residual risk: low; the documented behavior is the safer default (deny preserves safety; ask preserves prompt; allow is only checked last).

### R-4: Adopter customization survival depends on Claude Code precedence implementation (LOW)

**Risk**: A future Claude Code version changes the precedence semantics between `settings.local.json` and `settings.json` (e.g., flips order, introduces a third tier, requires explicit opt-in for local overrides). Adopters' customizations break silently on Claude Code upgrade.

**Mitigation**: Claude Code is a stable supported product with a documented migration policy; precedence changes would arrive with deprecation warnings and version-gated behavior. CLAUDE_PERMISSIONS.md §Cross-Version-Compatibility documents the minimum Claude Code version supported by the baseline; adopters running older versions are aware of the floor. ADR-041 §Decision documents the precedence reliance as a load-bearing assumption; if it breaks, the baseline gets updated in a follow-on PRD.

### R-5: --dangerously-skip-permissions and other Claude Code modes bypass the baseline (LOW residual; documented limitation)

**Risk**: An adopter (or automation pipeline) running tachi commands under modes that bypass or relax the `permissions:` block invalidates the baseline. Affected modes per Claude Code permissions documentation:
- `--dangerously-skip-permissions` flag — full bypass.
- `bypassPermissions` settings-file mode — equivalent to the flag, persisted.
- `auto` mode — auto-approves with safety classifier (research preview).
- `acceptEdits` mode — auto-accepts file edits and common filesystem commands (the user's own `~/.claude/settings.json` already runs `"defaultMode": "acceptEdits"` with `"skipDangerousModePermissionPrompt": true` — would partially neutralize F-4 for the user's dev environment).
- `dontAsk` mode — auto-denies unless pre-approved (this one *strengthens* the baseline; included for completeness).

SecOps reviewers may not anticipate the mode landscape.

**Mitigation**: CLAUDE_PERMISSIONS.md §Known-Limitations enumerates each mode and its bypass scope. Recommended mitigations for managed environments: (a) policy-lock the flag off via Claude Code's `disableBypassPermissionsMode: "disable"` and `disableAutoMode: "disable"` managed-settings keys; (b) wrap `claude` in a managed-environment wrapper script that strips the flag; (c) treat presence of the flag as a SecOps-policy violation and audit accordingly; (d) deploy the baseline as managed-settings (alternative #6 in ADR-041) rather than as `.claude/settings.json` for environments that already run MDM/OS-policy. The baseline operates at the schema layer; mode-bypass operates at a higher precedence layer outside this PRD's scope (NG4).

### R-6: Calibrated network allowlist may surprise adopters relying on undocumented hosts (MEDIUM)

**Risk**: Adopters whose workflows currently fetch from hosts not in the Category 4 allowlist (e.g., `pypi.org` for Python skill dependencies, `npmjs.com` for npm registry checks, internal company domains for internal-skill extension) experience a new approval prompt on every fetch. The friction is reasonable from a security perspective (adopter explicitly approves the unanticipated egress) but surfaces as workflow drag in low-stakes development.

**Mitigation**: The host allowlist starts narrow on purpose (GitHub + Anthropic + OWASP). CLAUDE_PERMISSIONS.md §Network-Allowlist documents the rationale and the customization path: adopters add their domains to `settings.local.json` `allow` (e.g., `WebFetch(domain:pypi.org)`) without modifying the shipped baseline. The narrow-default-plus-easy-override pattern matches the broader baseline philosophy (default-deny on uncertain surfaces; surgical opt-in via local override). Residual risk: medium-low; the approval prompt is the right behavior the first time an adopter encounters an unallowlisted host, and the customization path is documented.

### R-7: ADR-041 number conflicts with future ADR allocation (LOW)

**Risk**: Per memory record (BLP-02 ADR allocation), ADR-041 is reserved for F-4 (this PRD), ADR-042 is reserved for F-5, ADR-043 is reserved for BLP-03 signed-updates. If F-5's ADR slips or BLP-03 ADRs reorder, ADR-041 number becomes ambiguous.

**Mitigation**: Issue #277 §Detail explicitly reserves ADR-041 with the rationale: *"Renumbered from originally-planned ADR-040 after F-250 took ADR-039 and F-2 slipped to ADR-040."* The number is locked in at PRD time; future ADR allocations (F-5 → 042, BLP-03 → 043+) are documented in the BLP-02 enterprise-hardening memory record. Residual risk: low; ADR numbers are append-only and the project memory record is the single source of truth.

### R-8: Bash pattern argument-constraint fragility (MEDIUM)

**Risk**: Per Claude Code permissions documentation, *"Bash permission patterns that try to constrain command arguments are fragile."* The baseline's `Bash(git push --force:*)` deny rule does not catch every legitimate "I'm trying to force-push" variant. Documented and inferred bypass surfaces:
- `git push -f origin main` — caught by separate `Bash(git push -f:*)` deny rule (ok).
- `git push  --force` (double space) — depends on Bash command normalization in Claude Code; not documented; likely-bypass.
- `git push --force-with-lease` — caught by separate ask rule (ok; intentional).
- `git -c push.default=current push --force` — git config injection; NOT caught.
- `eval "git push --force"` — eval invocation caught at separate ask tier; recursive-eval-escape may bypass; partial caught.
- Shell variables: `CMD="git push --force"; $CMD` — NOT caught.
- Redirects / heredocs: rare in legitimate workflow, not reliably caught.

SecOps reviewers may treat the deny rule as a guarantee when upstream documents it as fragile.

**Mitigation**: CLAUDE_PERMISSIONS.md §Known-Limitations quotes the upstream "Bash permission patterns that try to constrain command arguments are fragile" warning verbatim and enumerates the bypass surface. Defense-in-depth for environments requiring strict guarantees: (a) PreToolUse hooks for high-rigor argument-pattern constraints (out of F-4 scope; documented as adopter-implementable extension and ADR-041 alternative #5); (b) git server-side branch protection rules denying force-push at the remote; (c) wrapper scripts that lint Bash command strings before invocation. Adopters who require strict no-force-push guarantee must layer at least one defense-in-depth measure beyond the schema-level baseline. **Residual risk: medium** for the determined-bypass case; **low** for the casual-typo case that the baseline meaningfully addresses.

### R-9: Process-wrapper bypass via npx / docker exec / devbox / mise (MEDIUM)

**Risk**: Claude Code's documented stripped-process-wrapper list is `timeout, time, nice, nohup, stdbuf` only. Modern dev-environment runners — `npx`, `docker exec`, `devbox run`, `mise exec`, `direnv exec` — are **NOT** stripped. Concrete bypass: `Bash(docker exec my-container rm -rf /workspace)` matches the broader `Bash(docker exec:*)` (Category 2 ask if added; allow if not) and bypasses `Bash(rm -rf:*)` (Category 3 deny). An adopter running tachi commands inside a Docker container or devbox/mise environment loses the destructive-operation deny baseline. BLP-02 explicitly targets enterprise developers who often DO use Docker/devbox in their workflow, so this risk is more material than the wrapper-list might suggest.

**Mitigation**: CLAUDE_PERMISSIONS.md §Known-Limitations documents the wrapper-bypass surface explicitly with the docker-exec example. Recommended for managed environments: (a) do not run Claude Code under non-stripped wrappers; (b) layer a PreToolUse hook that recursively unwraps wrapped commands before pattern matching (alternative #5 in ADR-041; out of F-4 scope); (c) use container-level seccomp/AppArmor profiles to enforce destructive-operation policy at the kernel layer rather than the Claude Code layer. The baseline is **honest about the wrapper boundary** — adopters wrapping the agent in container/dev-env runners must layer their own defense. **Residual risk: medium** for affected adopters; **none** for adopters running Claude Code natively.

### R-10: Read-only built-in shadow makes Category 1 partially documentary-only (LOW)

**Risk**: Per Claude Code permissions documentation, `ls`, `cat`, `grep`, `find`, `head`, `tail`, `wc`, `diff`, `stat`, `du`, `cd`, and read-only forms of `git` are auto-approved by built-in behavior in every mode. A v1.0 PRD listing these commands in `allow` would create documentary-only rules that don't change behavior. A SecOps reviewer comparing the policy file to actual behavior would notice the redundancy and lose confidence in the policy's accuracy.

**Mitigation**: v1.1 PRD drops the redundant rules from `.claude/settings.json` Category 1 (per Architect §2 Option A); only non-built-in commands (`rg`, `gh issue view`, etc.) remain. CLAUDE_PERMISSIONS.md §Built-in-Read-Only-Set documents the redundancy decision, lists the built-in commands deliberately omitted, and provides the SecOps-reviewer answer to "why is `Bash(ls:*)` not in this allow list?" before they ask the question. **Residual risk: low**; the documentary-redundancy concern is closed.

---

## 🔗 Dependencies

### Blocking Dependencies

**None.** Per Issue #277 §Dependencies. F-4 is independent of F-1, F-2, F-3, F-5 — could ship in parallel with any of them. The independence is what made BLP-02 Wave 4 sequencing trivially decidable: F-4 ships when the maintainer has 1-2 days of design bandwidth.

### Loosely-Coupled Dependencies

- **Existing `.claude/settings.json`** — the file being rewritten. Verified existence and shape at PRD draft time (2026-05-08): 47-line file with 26 allow rules and a hooks block.
- **CHANGELOG.md `## Unreleased` block** — new entry lands here; assumes the standard release-please flow is operational (verified by F-3 #273 release-please PR #274 which opened cleanly post-merge 2026-05-08).
- **ADR-000 template** — `docs/architecture/02_ADRs/ADR-000-template.md` exists; ADR-041 instantiates it.
- **Claude Code v2.1.x** — minimum supported version verified by AC-8 (cross-version compatibility test).
- **F-3 (#272) SECURITY.md** — F-4's CLAUDE_PERMISSIONS.md references the F-3-shipped private vulnerability reporting flow as the channel for reporting baseline gaps. F-3 must be live (it is, as of 2026-05-08) for the cross-reference to be honest. Soft dependency only; the cross-reference works regardless of F-3 status.

### Downstream Effects

- **README.md pointer** — promoted into F-4 scope per AC-14 (one-line addition; F-3 precedent).
- **Periodic `.claude/settings.json` ↔ CLAUDE_PERMISSIONS.md cross-check CI workflow** — committed to as AC-15 follow-up Issue (post-merge); not in F-4 implementation scope.
- **`make permissions-audit` target** — committed to as AC-16 follow-up Issue (post-merge); not in F-4 implementation scope.
- **BLP-02 Initiative Tracker** — closes Wave 4; updates the project memory record to reflect 4-of-5 Waves complete post-delivery.
- **Adopter `make update` flow** — adopters running `make update` after F-4 lands receive the new baseline; their `settings.local.json` overrides survive per AC-3 / AC-5. No migration runbook required (the change is mechanically additive: new rules in the shipped file; existing local customizations unchanged).

---

## ⏱️ Estimate & Timeline

### Effort

- **Spec → PR open**: ~6-8 hours of focused work (PRD draft → Triad review → branch → settings.json rewrite → CLAUDE_PERMISSIONS.md authoring → ADR-041 authoring → CHANGELOG → smoke-tests → push → draft PR). Bulk of the time is in CLAUDE_PERMISSIONS.md authoring (~4 hours for the rule-by-rule rationale catalog; this is the dominant cost).
- **PR review → merge**: ~1 hour (one substantial markdown PR + one settings.json rewrite + one ADR; reviewer reads diff, validates AC-2 cross-check, reads CLAUDE_PERMISSIONS.md as SecOps persona, confirms AC-6/AC-7 smoke-test screenshots).
- **Post-merge verification**: ~30 minutes (`/security` re-scan + AC-13 confirmation).
- **Total active**: ~8-9 hours of maintainer time.
- **Wall-clock buffer**: same-day delivery feasible if started morning-of, but next-day cap is more realistic given the CLAUDE_PERMISSIONS.md authoring cost. Issue #277 §Format estimates *"~1-2 days of design work"*; PRD aligns with the 1-2-day envelope.

### Comparison to Prior BLP-02 Waves

| Wave | LOC | Effort (active) | Wall-clock | ADR? |
|------|-----|-----------------|------------|------|
| F-1 | ~250 | 6.5d active | 7d | 038 |
| F-250 hot-fix | ~150 | 1d active | 1d | 039 |
| F-2 | ~600 | 9.5d active | 24h actual | 040 |
| F-3 | ~100 | 3-4h active | same-day | none |
| **F-4 (this)** | **~430** (settings.json ~80 after Cat-1 dedup + CLAUDE_PERMISSIONS.md ~250 + ADR-041 ~100) | **~8-9h active** | **next-day target** | **041** |

F-4 is mid-range in BLP-02 effort: heavier than F-3 (ADR-041 + 6 alternatives-considered + larger network-allowlist surface) and lighter than F-1/F-2 (no code paths, no test surface). The dominant cost is rule-by-rule rationale authoring in CLAUDE_PERMISSIONS.md — load-bearing for the AC-3 self-contained-policy-decision-log promise. The v1.1 revision shifted ~40 LOC from `.claude/settings.json` (Category 1 deduplication; built-in-read-only commands no longer listed as no-op allow rules) to ADR-041 (alternatives #5 PreToolUse hooks + #6 managed-settings expansion) and to CLAUDE_PERMISSIONS.md (Built-in-Read-Only-Set section + expanded Known-Limitations covering Bash fragility, wrapper-bypass, mode-bypass).

### Concurrency Risk

- **F-260b reviewer-engagement** (per memory record): Active F-260b follow-on may consume reviewer attention during F-4 review window. Mitigation: F-4 is independent and small enough that a 1-2-day slip absorbs the concurrent review load.
- **F-5 parallelization opportunity**: Issue #277 §Dependencies notes *"Could ship in parallel with F-5"* — if F-5 PRD lands before F-4 implementation completes, both can land in adjacent waves without sequencing concerns.

---

## 🧭 Governance

### Triad

- **Workflow**: Feature (parallel reviews — Architect + Team-Lead in parallel after PM draft).
- **PM**: davidmatousek (project owner, single-maintainer)
- **Architect review focus**: schema soundness (Claude Code permissions schema correctness — `deny`/`ask`/`allow` precedence usage, pattern syntax), category-tier calibration realism (does the deny-vs-ask split match enterprise SecOps expectations?), settings-precedence reliance load-bearing-ness, network-allowlist completeness (does the seven-domain initial allowlist cover all tachi command surfaces?), and ADR-041 alternatives-considered rigor.
- **Team-Lead review focus**: timeline realism for ~8-9h active work (single-maintainer cadence), dependencies (none blocking), Wave-4 sequencing alignment with prior BLP-02 waves, AC enumeration completeness (14 mandatory ACs is high — does each one warrant blocking-tier? are any nice-to-have-misclassified-as-mandatory?), CLAUDE_PERMISSIONS.md authoring cost-vs-value (~250 LOC rule-by-rule catalog is the dominant cost; is the policy-decision-log promise worth it?).

### ADR

**Yes — ADR-041.** This is a configuration-design choice with multiple plausible alternatives (two-tier flat allow/deny, four-tier as proposed, tag-based per-rule annotation, separate per-skill files), a load-bearing precedence reliance (`deny > ask > allow`), and a documented opt-out posture. ADR-041 captures the decision in the standard ADR template, with status `Accepted` after PM + Architect sign-off at delivery.

The ADR is **public** per Issue #277 §Detail line: *"Public ADR-041: Claude Code Permissions Baseline (rule categories, alternatives considered, opt-out path)."*

### Sign-off Gates

- spec.md sign-offs: PM (auto via `/aod.spec`)
- plan.md sign-offs: PM + Architect (auto via `/aod.project-plan`)
- tasks.md sign-offs: PM + Architect + Team-Lead (auto via `/aod.tasks`)

---

## 📌 Open Questions

(None at v1.1 final — v1.0 surfaced 2 BLOCKING-tier Architect concerns (schema precedence misclaim §1.1, missing `code.claude.com` in Category 4 allowlist §5.2) plus 9 lower-tier items (Bash pattern fragility, Category 1 redundancy, destructive-operation surface review, subdomain-matching verification, ADR-041 alternatives #5 + #6, R-3 reframe, R-8/R-9/R-10 additions, JSONC tolerance claim drop, CLAUDE_PERMISSIONS.md §Settings-Precedence worked example). Team-Lead surfaced 5 non-blocking advisories. v1.1 resolved all 11 Architect items — schema precedence rewritten to honest cross-list `deny → ask → allow` ordering with worked example commitment, `code.claude.com` plus 13 other Category 4 domains added via Tachi command-surface egress audit, Category 1 deduplicated from ~25 rules to ~10 (built-ins documented in CLAUDE_PERMISSIONS.md §Built-in-Read-Only-Set), Category 3 destructive-operation surface review enumerated (dd / mkfs / git filter-branch / npm install -g / curl|sh / etc.), AC-7 subdomain-matching verification added, ADR-041 alternatives expanded to six with rejection rationale, R-3 reframed as cross-list-vs-cross-file two-layer interaction, R-8/R-9/R-10 added (Bash fragility / wrapper bypass / built-in shadow), JSONC claim dropped (strict JSON committed; per-rule rationale in CLAUDE_PERMISSIONS.md only), AC-13 amended with release-please verification, AC-6 sub-checks added (JSON validity + git-status auto-approve regression). v1.1 also folded Team-Lead A-3 (release-please AC merger) and A-4 (AC-6 sub-checks) advisories. Team-Lead A-1 (AC-5 fixture path), A-2 (CLAUDE_PERMISSIONS.md per-row LOC budget), A-5 (smoke-test scheduling) deferred to `/aod.spec` and `/aod.tasks` time per Team-Lead's own framing.)

---

## 📎 References

- **GitHub Issue**: #277 — `https://github.com/davidmatousek/tachi/issues/277`
- **Trigger**: Daniel Wood LinkedIn thread 2026-05-02 (same trigger as F-3); see F-3 PRD §Problem-Statement for full thread context.
- **BLP-02 Initiative Tracker**: project memory record `project_blp02_enterprise_hardening`
- **Existing `.claude/settings.json`**: `/Users/david/Projects/tachi/.claude/settings.json` (47 LOC, last modified 2026-04-19)
- **Prior BLP-02 PRDs**: #248 (F-1 Substitution Surface), #250 (F-1 hot-fix), #256 (F-2 Source-Pattern), #272 (F-3 SECURITY.md)
- **ADR template**: `docs/architecture/02_ADRs/ADR-000-template.md`
- **Conventional Commit PR title rule**: `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles
- **F-3 SECURITY.md (cross-reference for baseline-gap reporting)**: `SECURITY.md`
- **Claude Code permissions schema**: Claude Code official documentation (cited at PR-merge time with version-locked URL in CLAUDE_PERMISSIONS.md §Schema-Reference)
- **Settings precedence documentation target**: `docs/standards/CLAUDE_PERMISSIONS.md` §Settings-Precedence (created in this PRD)
- **Triad reviews**: `.aod/results/architect.md` and `.aod/results/team-lead.md` (populated by Architect + Team-Lead reviews invoked at this PRD's Step 4)
