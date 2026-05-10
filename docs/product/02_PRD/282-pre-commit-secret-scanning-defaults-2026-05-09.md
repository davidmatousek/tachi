---
prd:
  number: 282
  topic: pre-commit-secret-scanning-defaults
  created: 2026-05-09
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-05-09, status: APPROVED, notes: "v1.1 final. Authored as BLP-02 Wave 4+ — fifth and final feature in the 5-feature enterprise hardening initiative. F-1 (#248) DELIVERED 2026-05-04, F-2 (#256) DELIVERED 2026-05-05, F-3 (#272) DELIVERED 2026-05-08, F-4 (#277) DELIVERED 2026-05-09. F-5 originally planned as Wave 4 parallel co-ship with F-4; F-4 shipped solo so F-5 effectively becomes a post-Wave-4 next-day ship. Scope: gitleaks-via-pre-commit-framework default with pinned commit hash; tachi-tuned `.gitleaks.toml` (~50-80 LOC) with allow-list (env-var placeholders, fixture/docs/examples paths, `.aod/personalization.env.example` template) + 2 additive custom rules (`tachi-personalization-env`, `tachi-security-exceptions-jsonl`); init.sh opt-in prompt (default Y for first-time interactive, no auto-install on git pull); `docs/standards/PRECOMMIT_HOOKS.md` (~150-250 LOC); `ADR-042` (130-180 LOC final estimate); new `.github/workflows/gitleaks.yml` (~25-40 LOC) for CI parity; CHANGELOG; README pointer; new `.aod/personalization.env.example` template file. v1.0 surfaced 4 CHANGES from Architect (C-1 personalization.env.example missing, C-2 gitleaks formatter-override infeasible → wrapper-script reality, C-3 raw read-p vs F-1 helper waiver, C-4 false-positive prevention reactive not preventive) + 6 Architect advisories + 7 Team-Lead non-blocking advisories. v1.1 resolved all 4 Architect CHANGES + folded actionable advisories: C-1 added `.aod/personalization.env.example` template to in-scope file list, C-2 reframed AC-15 to wrapper-script approach with explicit Q9 (location decision at /aod.spec), C-3 added ADR-042 §Consequences explicit waiver for raw read-p (single-char Y/n below F-1 threshold), C-4 strengthened R-1 with /aod.spec entry-criteria synthetic-fixture test (preventive vs reactive). Team-Lead advisories folded: A-1 Phase 2 estimate updated to 9-13h floor, A-2 new `.github/workflows/gitleaks.yml` (~25-40 LOC) replaces 'extend existing' framing, A-3 AC-8 dropped (init.sh hard-exit + self-delete makes re-init prompt scenario impossible), A-5 milestone target anchored at 2026-05-10 with 2026-05-11 slack, A-6 AC-15 spike scope made explicit. Architect advisories folded: A-1 ADR-042 alternatives expanded with GitGuardian / SecretLint / git-secrets one-paragraph dismissals, A-2 pin-bump cadence policy added to ADR-042 §Consequences, A-6 R-9 (adopter `.gitleaks.toml` divergence) added, A-7 R-10 (pre-commit framework version drift) added. Architect A-3 / A-4 / A-9 / A-10 + Team-Lead A-4 + A-7 deferred to /aod.spec time per their framing. ICE 22 (I:8 C:7 E:7); ~9-13h active envelope / next-day wall-clock target (2026-05-10) with +1 day slack budget (2026-05-11)."}
  architect_signoff: {agent: architect, date: 2026-05-09, status: APPROVED_WITH_CONCERNS, notes: "v1.1 re-review APPROVED_WITH_CONCERNS. v1.0 surfaced 4 CHANGES (C-1 personalization.env.example missing, C-2 gitleaks formatter-override infeasible, C-3 init.sh raw read-p vs F-1 helper, C-4 false-positive prevention reactive) + 6 advisories (A-1 ADR-042 alternatives breadth, A-2 pin-bump cadence, A-3 directory-rename allow-list interaction, A-4 diff vs full-repo CI scan, A-5 dedicated gitleaks.yml workflow, A-6 R-9 missing, A-7 R-10 missing, A-8 covered under C-1, A-9 AC-3 fixture format, A-10 AC-12 cleanup discipline). v1.1 resolved all 4 CHANGES with technical accuracy: C-1 .aod/personalization.env.example template added to in-scope file inventory (5-10 LOC delta) — single template file documenting expected keys without values, addresses adopter onboarding friction; C-2 AC-15 reframed to wrapper-script approach with Q9 added to Open Questions for /aod.spec-time wrapper-script-location decision (precommit-wrap.sh under .aod/scripts/bash/ vs inline `entry: bash -c '...'` in .pre-commit-config.yaml) — gitleaks does NOT support stderr-message templating per architect verification, formatter override path is infeasible at the CLI level; C-3 ADR-042 §Consequences will document explicit waiver for single-character Y/n raw read-p pattern (below F-1's free-text input-validation threat threshold; documented decision so future reviewers do not re-litigate); C-4 R-1 contingency strengthened with /aod.spec entry-criteria synthetic-fixture rule-interaction test (preventive: enumerate adopter scenarios + run gitleaks against synthetic versions BEFORE merge, not reactive v4.34.x hot-patch). Of 6 advisories: A-1 GitGuardian/SecretLint/git-secrets folded into ADR-042 alternatives, A-2 pin-bump cadence policy folded into ADR-042 §Consequences (bump-on-each-gitleaks-minor-release with empirical re-verification), A-6 R-9 (adopter divergence on make update), A-7 R-10 (pre-commit framework version drift) added to risk catalog. A-3 directory-rename, A-4 diff-vs-full-repo CI scope, A-9 AC-3 fixture format, A-10 AC-12 cleanup deferred to /aod.spec time per their framing — all are spec-time refinements, not PRD revision blockers. Confidence: HIGH on technical claims; gitleaks formatter limitation independently verified. Plan readiness: APPROVED. Full v1.0 + v1.1 reviews: .aod/results/architect-prd-282.md."}
  techlead_signoff: {agent: team-lead, date: 2026-05-09, status: APPROVED_WITH_CONCERNS, notes: "v1.0 APPROVED_WITH_CONCERNS — feasibility, capacity, dependency soundness, AC count proportionality all validated. v1.0 surfaced 7 non-blocking advisories: A-1 Phase 2 floor ~10h not 8h with ADR-042 likely 130-180 LOC, A-2 NO existing security-scan GitHub Actions workflow exists (`.github/workflows/` contains only release-please.yml + tachi-mmdc-preflight.yml + tachi-pytest.yml; CI parity needs new gitleaks.yml ~25-40 LOC), A-3 AC-8 misframes current init.sh (hard-exits on re-run lines 65-70 + self-deletes after success — re-init double-prompt scenario cannot occur; recommend drop AC-8), A-4 F-1 dependency satisfied but should be made explicit at /aod.spec time, A-5 same-day delivery (2026-05-09) unrealistic given today's already-burned hours from F-4 delivery + PRD authoring; next-day (2026-05-10) is honest target, A-6 AC-15 gitleaks formatter has unbounded research risk requiring 30-min spike at /aod.spec time before envelope locks, A-7 +1-day slack budget for Sunday (2026-05-11) acceptable. v1.1 folded 5 of 7: A-1 Phase 2 estimate updated to 9-13h floor, A-2 dedicated gitleaks.yml workflow added to file surface (~25-40 LOC), A-3 AC-8 dropped + replaced with AC-8' documentation-only note in PRECOMMIT_HOOKS.md §Re-init-Behavior clarifying init.sh runs at most once per project, A-5 milestone targets anchored at 2026-05-10 with 2026-05-11 slack, A-6 AC-15 wrapper-script reframing handles spike-scope concern. A-4 (explicit Prior-Dependencies-Satisfied subsection) and A-7 (slack budget documentation) deferred to /aod.spec time as scope-appropriate refinements. Estimate-accuracy: HIGH probability ~10-12h Phase 2 envelope hit (~70%); HIGH probability next-day wall-clock hit (~80%) sensitive to AC-15 wrapper-script implementation discipline. Capacity: single-maintainer (davidmatousek), Saturday 2026-05-10 active per F-4 weekend-active precedent (F-3 Friday, F-4 Saturday). Zero concurrent-initiative blockers (BLP-03 PROPOSED only, F-260b file-disjoint). 16 mandatory ACs (after A-3 AC-8 drop) appropriately calibrated vs F-3 (12) / F-4 (14); +2-4 over F-4 justified by CI parity (AC-12) + idempotency (note in PRECOMMIT_HOOKS.md not AC) + refused-commit-error-message contract (AC-15) + existing-adopter no-surprise (AC-9) + TTY-skip (AC-7). Zero gold-plating. Full review: .aod/results/team-lead-prd-282.md."}
source:
  idea_id: 282
  story_id: null
---

# F-5 — Pre-commit Secret-Scanning Defaults: Product Requirements Document

**Status**: Approved (PM + Architect + Team-Lead sign-offs in)
**Created**: 2026-05-09
**Author**: product-manager
**Reviewers**: architect (APPROVED_WITH_CONCERNS v1.1; 4 of 4 v1.0 CHANGES resolved + 4 of 6 advisories folded), team-lead (APPROVED_WITH_CONCERNS v1.0; A-1, A-2, A-3, A-5, A-6 folded into v1.1; A-4 + A-7 deferred to /aod.spec)
**Phase**: BLP-02 Wave 4+ — fifth and final feature in the 5-feature enterprise hardening initiative; F-1 (#248) DELIVERED 2026-05-04, F-250 hot-fix DELIVERED 2026-05-04, F-2 (#256) DELIVERED 2026-05-05, F-3 (#272) DELIVERED 2026-05-08, F-4 (#277) DELIVERED 2026-05-09 (PR #278). F-5 originally planned as Wave 4 parallel co-ship with F-4; F-4 shipped solo so F-5 effectively becomes a post-Wave-4 next-day ship.
**Priority**: P1 (ICE 22 — I:8 C:7 E:7)

---

## 📋 Executive Summary

### The One-Liner

Ship a pre-commit hook configuration (`.pre-commit-config.yaml`) running `gitleaks` against the working tree by default — opt-in for new adopters via an `init.sh` prompt and opt-in (no auto-install) for existing adopters who pull the update — plus a tachi-tuned `.gitleaks.toml` that recognizes tachi's own conventions (env-var placeholders, fixture credentials, `.aod/personalization.env` deltas) so legitimate workflows don't trigger false positives, plus `docs/standards/PRECOMMIT_HOOKS.md` documenting installation / opt-out / bypass paths, plus `ADR-042` capturing the gitleaks-vs-trufflehog decision and the opt-in-vs-auto-install posture, plus a dedicated `.github/workflows/gitleaks.yml` providing CI parity, plus a new `.aod/personalization.env.example` template documenting expected keys.

### Problem Statement

The 2026-05-02 LinkedIn thread that grounded BLP-02 contained, alongside Daniel Wood's "pre-commit/secret-scanning defaults" recommendation, a load-bearing observation about *enterprise developer environments*: SecOps reviewers expect AI-coding-agent templates to ship with **default-deny posture on accidental credential exposure**, not just on destructive operations (which F-4 closed). The Daniel Wood thread enumerated three specific gaps tachi shipped without — disclosure channel (F-3 closed), permissions hardening (F-4 closed), and **secret-scanning defaults** (this feature, F-5).

The current tachi repository has no shipped pre-commit configuration:

1. **No `.pre-commit-config.yaml` at repo root.** A first-time adopter cloning tachi, configuring an OpenAI / Anthropic API key in `.aod/personalization.env`, and accidentally `git add`-ing the file (or pasting the key into a CHANGELOG draft, or copying it into a fixture file) has no defense-in-depth gate before the credential reaches the local commit history. From local commit history, the credential is one `git push` away from a public remote — and once on a public remote, GitHub's secret-scanning push protection may catch it, but only for vendor-recognized patterns, and only on the push-protection layer (not on the local commit). For non-recognized patterns (custom API keys, internal HMAC secrets, private keys without standard headers), there is no local gate at all.

2. **No `.gitleaks.toml` (or equivalent) tuned for tachi's conventions.** Even if an adopter installs gitleaks-via-pre-commit-framework themselves with default rules, tachi's own codebase contains patterns that out-of-the-box gitleaks rules flag as false positives:
   - `.aod/personalization.env.example` template files with **placeholder** API keys (`OPENAI_API_KEY=sk-PLACEHOLDER` or `OPENAI_API_KEY=$ENV_VAR`) — these look like leaked credentials to a default rule and would block the commit, training the adopter to disable the hook.
   - Fixture files (`tests/fixtures/`, `examples/`) containing **deliberately-fake** test PATs, AWS keys, and private keys for negative-case test coverage — necessary for the test suite, but blocked by default rules.
   - `.security/exceptions.jsonl` entries with TLDR-redacted-but-still-credential-shaped strings used to suppress known-false-positive findings — itself a tachi-specific convention an out-of-the-box rule cannot recognize.
   - Documentation examples (`docs/architecture/`, `docs/standards/`) with intentional placeholder credentials for instructional purposes (e.g., the CLAUDE_PERMISSIONS.md F-4 worked example referencing `Bash(gh secret set:*)`).
   The cost of a false-positive flood is not zero: an adopter who fights the hook 5 times in a row uninstalls it. The default ruleset must recognize tachi conventions or the feature ships dead-on-arrival.

3. **No documentation of what tachi expects adopters to scan for.** Adopters who *want* secret-scanning are left to choose between gitleaks, trufflehog, and detect-secrets without guidance on which integrates with tachi's testing-and-fixture conventions, which has acceptable license terms (gitleaks: MIT; trufflehog: AGPLv3 — material distribution-friction risk for adopters who redistribute tachi-derived templates), and which catches the threat surface tachi itself documents (the `.aod/personalization.env`, custom rule patterns from F-1's substitution-surface PRD, and the ADR-040 config-file-parsing finding all suggest the same threat: credentials embedded in adopter-customized config files).

4. **No `init.sh` prompt asking the adopter whether they want secret-scanning installed.** F-4 shipped `.claude/settings.json` baseline that was self-applying (Claude Code reads it without an install step). Pre-commit hooks are *not* self-applying — installing the framework requires `pre-commit install` (or equivalent) to write the actual hook script into `.git/hooks/pre-commit`. A new adopter completing `make init` today gets no scaffolding for this step; they must read documentation, install pre-commit, and wire it themselves — a friction surface that historically yields ~10-20% adoption rates for opt-in security tooling. An `init.sh` prompt with sensible default `[Y/n]` (default Y for new adopters, default N for existing adopters who pull the update) raises the adoption rate while preserving opt-out for adopters who maintain their own scanning setup.

5. **No `ADR-042` capturing the gitleaks-vs-trufflehog decision.** Tool selection in security tooling is rarely value-neutral: gitleaks (Go binary, MIT-licensed, faster scan, narrower default rule set) trades off against trufflehog (Python binary, AGPL-3.0-licensed, broader default rule set including verified-credential probing). For an opinionated default in an enterprise-facing template, the choice rationale must be documented so SecOps reviewers and adopters with conflicting tool preferences can engage with the trade-offs. F-1 / F-2 / F-3 / F-4 all shipped with ADRs (ADR-038, no-ADR-by-design for F-2/F-3 with rationale, ADR-040, ADR-041); F-5's choice of gitleaks-not-trufflehog warrants the same documentation discipline.

6. **No `.aod/personalization.env.example` template at repo root.** A first-time adopter cloning tachi has no on-disk template documenting which environment variables `init.sh` expects (project name, stack pack, brand name). Adopters must read `init.sh` source to discover the expected keys, or run init.sh and observe its prompts. A shipped `.example` template — placeholder values, comments documenting each key — gives adopters a starting reference and gives F-5's `.gitleaks.toml` a path-allow-listed location for placeholder content (the `.example` is in-tree, the populated `.aod/personalization.env` is gitignored per F-1).

The five user surfaces this gap leaves exposed:

1. **First-time adopters configuring tachi for production-adjacent use** who paste an API key into `.aod/personalization.env` (or a CHANGELOG draft, or a test fixture) and accidentally `git add` it. Today no local gate fires; the credential lands in `git log` and is one `git push` away from public exposure. Pre-commit secret-scanning closes the local gap.

2. **Security-conscious solo developers** who *want* a default-deny gate on accidental credential commits but should not have to design the configuration themselves. Today they either roll their own gitleaks setup (paying the design cost) or skip the protection (deferring it indefinitely). A shipped default with sensible custom rules removes the design friction.

3. **Existing adopters with their own pre-commit setup** (gitleaks, trufflehog, detect-secrets, internal company tooling) who pull the F-5 update on `make update`. They must NOT have a new `.git/hooks/pre-commit` written without their consent — that would silently override their existing setup or create dual-hook-execution surprises. The opt-in flow must be observable and reversible.

4. **SecOps reviewers auditing AI agent templates** who expect a documented secret-scanning posture (which scanner, which rules, which opt-out path, which bypass mechanism) as a baseline procurement-questionnaire line item. Today: absent. Tomorrow: `docs/standards/PRECOMMIT_HOOKS.md` + ADR-042.

5. **Future external reviewers** (the "future Daniel Wood" persona — community member spotting a posture concern in tachi during their own review). The 2026-05-02 thread enumerated three gaps; F-3 closed disclosure, F-4 closed permissions, F-5 closes secret-scanning. With F-5 shipped, the LinkedIn-thread punch list is fully retired and tachi's enterprise-readiness posture is procurement-questionnaire-aligned across the disclosure / permissions / secret-scanning triad.

The cross-cutting theme: **F-5 is the third and last LinkedIn-thread gap to close.** F-3 fixed *how* researchers report posture concerns. F-4 fixed *the permissions posture itself*. F-5 fixes *the credential-exposure-prevention posture* — the third leg of the enterprise-readiness stool. With F-5 delivered, BLP-02 closes 5/5 (already 4/5 delivered; F-5 is sole remaining).

### Proposed Solution

This feature ships as **one feature branch (`282-pre-commit-secret-scanning-defaults`), one squash-merged PR, one `feat(282):` commit subject** that triggers a release-please PR. Seven work items:

1. **`.pre-commit-config.yaml` at repo root (~30-50 LOC).** Pre-commit framework configuration referencing the `gitleaks/gitleaks` repo with a pinned commit hash (NOT a floating tag — supply-chain hygiene; pinned hash ensures the hook references a specific commit even if the upstream tag is force-moved or the repo deleted). The configuration runs gitleaks against staged files only (default pre-commit framework semantics — does not re-scan history every commit, which would be unworkably slow for large repos). Per AC-15 wrapper-script approach (see C-2 resolution below), the hook may invoke a small wrapper at `.aod/scripts/bash/precommit-wrap.sh` (or via inline `entry: bash -c '...'` — final location decided at /aod.spec per Q9) rather than gitleaks directly, so the wrapper can augment gitleaks' stderr with the `SKIP=` bypass guidance + docs link required by AC-15.

   Approximate shape (subject to /aod.spec-time refinement):
   ```yaml
   repos:
     - repo: https://github.com/gitleaks/gitleaks
       rev: <pinned-commit-hash>  # specific commit, not floating tag (verified at /aod.spec)
       hooks:
         - id: gitleaks
           args: ["--config=.gitleaks.toml"]
           # OR (per Q9 wrapper-script decision):
           # entry: ".aod/scripts/bash/precommit-wrap.sh"
   ```

   Per-hook tuning (`stages: [pre-commit]`, no autofix, exit-code-on-find behavior is gitleaks default) finalized at /aod.spec time after a quick gitleaks-CLI flag survey. The hook is **opt-in** — the framework is only invoked if the adopter has run `pre-commit install` (or used the init.sh prompt that runs it for them); the file's mere presence in the repo does NOT install hooks into `.git/hooks/`.

2. **`.gitleaks.toml` at repo root (~50-80 LOC).** Custom gitleaks configuration extending the default rule set with tachi-specific allow-listing for known-safe-but-credential-shaped patterns:

   - **Allow-list**: `\$[A-Z_]+` (env-var placeholders like `$OPENAI_API_KEY`), `<placeholder>`, `PLACEHOLDER`, `your-api-key-here` (common docs convention), `sk-PLACEHOLDER...`, `sk-test-...` (Stripe test-mode keys, recognized as test-only).
   - **Path allow-list**: `tests/fixtures/`, `examples/`, `.aod/personalization.env.example` (template file shipped by F-5 — not the adopter-populated `.aod/personalization.env` which is gitignored per F-1), `docs/` (instructional placeholders).
   - **Custom rules** (small, additive — NOT a wholesale replacement of gitleaks defaults):
     - `tachi-personalization-env`: warn when `git diff` of `.aod/personalization.env` shows non-placeholder values (catches accidental commits of populated config; guides adopter to F-1's gitignore).
     - `tachi-security-exceptions-jsonl`: warn when `.security/exceptions.jsonl` is manually edited (the file is normally auto-generated; manual edits suggest credential-suppression abuse).
   - **Excluded paths**: `node_modules/`, `.git/`, `archive/` (per CLAUDE.md context boundaries; these are not part of tachi's source surface).
   - **Documentation**: every allow-list entry and custom rule has an inline comment explaining *why* — same SecOps-audit-readiness pattern F-4's CLAUDE_PERMISSIONS.md established. Per-rule rationale lives in PRECOMMIT_HOOKS.md cross-referenced one-to-one with the rule names in `.gitleaks.toml`.

   The tuning is **calibrated to tachi's own `make test` and `/aod.build` execution** — the `.gitleaks.toml` MUST allow the existing test fixture and documentation surface to commit cleanly. AC-4 verifies this empirically: `pre-commit run --all-files` from a clean clone produces zero findings on the pre-F-5 baseline. Per C-4 resolution (architect concern): /aod.spec entry-criteria adds a synthetic-fixture rule-interaction test (preventive false-positive verification, not reactive hot-patch).

3. **`.aod/personalization.env.example` at repo root (~10-20 LOC, NEW per C-1 resolution).** Template file documenting expected keys without values:
   ```
   # Copy this file to `.aod/personalization.env` and fill in your values.
   # `.aod/personalization.env` is gitignored per F-1 (#248) substitution-surface hardening.
   AOD_PERSONALIZATION_PROJECT_NAME=
   AOD_PERSONALIZATION_STACK_PACK=
   AOD_PERSONALIZATION_BRAND_NAME=
   # ... additional keys as documented in scripts/init.sh
   ```

   This template serves three purposes: (a) documents adopter-expected configuration without requiring source-code reading, (b) gives F-5's `.gitleaks.toml` a path-allow-listed location for placeholder content, (c) closes a long-standing onboarding-friction gap — currently adopters discover the expected keys by running `init.sh` and observing prompts, or by reading the bash source. The `.example` template is in-tree; the populated `.aod/personalization.env` remains gitignored.

4. **`init.sh` opt-in prompt (~10-20 LOC delta).** Add a single prompt step to `scripts/init.sh` (existing file path; verified). Add interactive prompt with default Y, TTY check for non-interactive skip:

   ```bash
   if [ -t 0 ]; then  # TTY check: skip in non-interactive contexts (CI, expect, /dev/null pipe)
     read -p "Install pre-commit secret-scanning hook (gitleaks)? [Y/n] " response
     if [[ "${response:-Y}" =~ ^[Yy]$ ]]; then
       pre-commit install || echo "WARN: pre-commit install failed; install pre-commit framework manually and run 'pre-commit install'"
     fi
   fi
   ```

   **Default Y** for first-time adopters running `init.sh` interactively. **Default behavior for existing adopters** (those who already ran an older init.sh and now `git pull` the F-5 update): NO auto-install. The pre-commit hook is NOT written to `.git/hooks/` automatically on `git pull` — the adopter must explicitly run `pre-commit install` to opt in. A CHANGELOG entry (and a one-line README pointer per the F-3 / F-4 precedent) tells existing adopters how to opt in.

   **Re-init guard interaction (per Team-Lead A-3 finding)**: `scripts/init.sh` lines 65-70 hard-exit if `.aod/personalization.env` already exists ("init.sh self-deletes after a successful run") — meaning init.sh's prompt fires **at most once per project**. There is no "re-run init.sh and skip pre-commit prompt" scenario; the script either is the original-from-fresh-clone (prompt fires) or refuses to run (no prompt). The original PRD v1.0's AC-8 ("re-init no double-prompt") was misframed and has been dropped in v1.1; the equivalent guidance is documented in PRECOMMIT_HOOKS.md §Re-init-Behavior as a clarifying note ("init.sh runs at most once per project; the pre-commit prompt fires once at first init. To opt in post-init, run `pre-commit install`").

   **Raw `read -p` vs F-1 `aod_init_read_validated` helper (per Architect C-3 resolution)**: ADR-042 §Consequences documents an explicit waiver for the raw `read -p` pattern. The single-character Y/n input surface is below F-1's input-validation threat threshold (F-1 hardened free-text fields against shell-injection via substitution-surface attacks; Y/n with default-Y fallback has trivially-bounded input space — at most one character, defaulted). Raw `read -p` is acceptable and documented so future reviewers do not re-litigate.

5. **`docs/standards/PRECOMMIT_HOOKS.md` (~150-250 LOC).** Self-contained documentation covering:

   - **Why this hook ships.** One-paragraph framing: who it serves, what threat it defends against, what threats it does NOT defend against (compromised maintainer machine, post-merge credential exposure via PR history scrub failure, GitHub-token-in-CI-logs, compromised pre-commit framework distribution).

   - **Installation paths**:
     - **First-time adopter (recommended)**: run `init.sh`, accept the prompt default Y. Hook is installed and active.
     - **Existing adopter pulling F-5 update**: `git pull` does NOT install the hook. Run `pre-commit install` from the repo root.
     - **Manual install (no init.sh)**: `pip install pre-commit && pre-commit install` from the repo root.

   - **What gets scanned**. Pre-commit hooks scan **staged files only** (per pre-commit framework default semantics; `pre-commit run --all-files` scans the entire tree on demand). Default rules + custom rules in `.gitleaks.toml`. Documentation lists the rule categories enumerated in `.gitleaks.toml` with rationale per category.

   - **Bypass mechanisms**:
     - **Single-commit bypass**: `SKIP=gitleaks git commit -m "..."` (pre-commit framework standard).
     - **Per-line allow**: gitleaks supports inline `# gitleaks:allow` comment annotations adjacent to known-fake credentials.
     - **Full disable**: `pre-commit uninstall` removes the hook. Re-running `pre-commit install` restores it.
     - **Adversarial bypass**: `git commit --no-verify` skips ALL pre-commit hooks. Documented as a known limitation (defense-in-depth: pre-commit is local-only; CI parity exists for back-stop coverage — see Section "CI Parity" below).

   - **Refused-commit error message contract**. When gitleaks blocks a commit, the wrapper-script error output MUST include:
     - Which secret pattern fired (rule ID).
     - The file:line of the match.
     - The allow-list mechanism: `# gitleaks:allow` annotation or path allow-list addition to `.gitleaks.toml`.
     - The bypass mechanism for one-off cases: `SKIP=gitleaks git commit ...`.
     - Documentation link: `See docs/standards/PRECOMMIT_HOOKS.md` for rationale and full mechanism reference.

   This is a **hard requirement** (per Issue #282 §Definition-of-Done line: *"Refused-commit error message includes (a) which secret pattern fired, (b) the file:line, (c) 'to bypass for this commit only: SKIP=gitleaks' guidance"*). Per Architect C-2 resolution: gitleaks default error output already includes (a) and (b); items (c) and (d) require a small wrapper script (precommit-wrap.sh) that invokes gitleaks and augments stderr — formatter override at the gitleaks CLI level is infeasible (gitleaks does not support stderr-message templating).

   - **CI parity**. The same `.gitleaks.toml` runs as a dedicated GitHub Actions workflow (`.github/workflows/gitleaks.yml`) on every PR. This back-stops the local pre-commit hook (which can be bypassed with `--no-verify`) — credentials that slip past local pre-commit still get caught at the CI gate, before merge. The CI step uses the same `.gitleaks.toml`, ensuring local and CI scan results are identical (no "passes locally, fails in CI" surprise).

   - **Re-init behavior** (re-framed per Team-Lead A-3): `scripts/init.sh` runs at most once per project — the script hard-exits on subsequent invocations when `.aod/personalization.env` exists, and self-deletes after a successful run. The pre-commit prompt therefore fires at most once. To opt in post-init, run `pre-commit install` from the repo root.

   - **Known limitations**:
     - `git commit --no-verify` bypasses all pre-commit hooks.
     - Pre-commit-framework distribution itself is a supply-chain surface (gitleaks repo could be compromised; pinned hash in `.pre-commit-config.yaml` mitigates moderate risk, not catastrophic).
     - Custom rules cannot detect every secret format. Adopters with proprietary credential formats should add their own rules to `.gitleaks.toml`.
     - Pre-commit hooks scan staged content only; they do NOT scan untracked files or files modified-but-not-staged.
     - Compromised maintainer machines, post-history-rewrite leaks, and GitHub-Actions secret-in-log-output cases are out of scope.
     - Pre-commit framework version drift: minimum supported version `>= 3.5.0` (R-10).

   - **Adopter customization**. Adopters who want stricter scanning, different rules, or a different scanner can:
     - Edit `.gitleaks.toml` to add custom rules (changes survive `make update` if they are in adopter-managed paths; rule additions in `.gitleaks.toml` are subject to merge conflicts on `make update` — see R-9).
     - Replace gitleaks with trufflehog or detect-secrets by editing `.pre-commit-config.yaml` to reference a different hook repo.
     - Disable the hook entirely via `pre-commit uninstall` (no impact on the rest of tachi).
     - Adopter directory rename considerations: if an adopter renames `tests/fixtures/` to `samples/`, the `.gitleaks.toml` path allow-list must be updated to match (per Architect A-3).

6. **`ADR-042 — Pre-commit Secret-Scanning Default` (130-180 LOC; v1.1 estimate per Team-Lead A-1).** Architecture decision record covering:
   - **(a) The pre-commit-framework + gitleaks combination as the chosen design.** Why pre-commit-framework (de-facto standard, language-agnostic, widely-distributed); why gitleaks-as-the-scanner.
   - **(b) gitleaks vs trufflehog rationale.**
     - **License**: gitleaks is MIT; trufflehog is AGPL-3.0. AGPL has material redistribution friction for adopters who redistribute tachi-derived templates.
     - **Performance**: gitleaks is a Go binary; default-rule scan of tachi's working tree completes in <2s on a modern laptop. trufflehog is Python; default-rule scan is meaningfully slower.
     - **Default rule breadth**: trufflehog has broader default rules and supports verified-credential probing. gitleaks has narrower defaults and no probing. Narrower-and-faster + adopter-extensible is the calibrated default.
     - **Distribution**: gitleaks distributes a single Go binary; trufflehog requires Python runtime.
     - **Verified-credential probing trade-off**: trufflehog's active-validation feature is a privacy minus (active-validation requests outbound HTTP from adopter's machine). Gitleaks' inactive-pattern-match-only design avoids the privacy concern.
   - **(c) The opt-in install posture (init.sh prompt; no auto-install on `git pull`)** as the chosen distribution model.
   - **(d) The custom-rule scope.** Allow-listing only — no rule deletions. Tachi-specific rules (`tachi-personalization-env`, `tachi-security-exceptions-jsonl`) are additive.
   - **(e) Wrapper-script for refused-commit error message contract** (per Architect C-2 resolution). Gitleaks does not support stderr-message templating; a small wrapper at `.aod/scripts/bash/precommit-wrap.sh` (location confirmed at /aod.spec per Q9) augments gitleaks output with bypass guidance + docs link required by AC-15.
   - **(f) Raw `read -p` waiver** (per Architect C-3 resolution). Single-character Y/n input is below F-1's input-validation threat threshold; raw `read -p` is acceptable for the init.sh prompt without using the F-1 `aod_init_read_validated` helper.
   - **(g) Pin-bump cadence policy** (per Architect A-2). Tachi maintainer bumps the pinned gitleaks commit hash on each gitleaks minor release, with empirical re-verification (`pre-commit run --all-files` against tachi's tree, plus the synthetic-fixture rule-interaction test from C-4) before merging the bump.

   **Alternatives considered** (each with rejection rationale):
   1. **trufflehog over gitleaks** — Rejected per (b) above (license / performance / privacy).
   2. **detect-secrets over gitleaks** — Yelp's detect-secrets is Python, MIT-licensed, baseline-file-driven. Rejected because the baseline-file model conflicts with tachi's "no shipped per-adopter state" posture and verified-credential-probing model has same privacy concerns as trufflehog. Acknowledged as viable adopter-customization swap.
   3. **GitHub native push-protection only** — Rejected because (1) push-protection only fires at the push step, not at the commit step; (2) only covers vendor-recognized patterns (no custom-rule support); (3) requires a GitHub plan with the feature enabled; (4) is GitHub-vendor-locked (adopters mirroring tachi to GitLab / Gitea / Forgejo lose the protection entirely).
   4. **Custom regex pre-commit hook** (no gitleaks dependency) — Rejected because (1) recreating gitleaks' battle-tested rule set in tree is significant ongoing maintenance; (2) gitleaks is widely distributed and externally maintained; (3) the supply-chain risk of pinning a third-party hook is meaningfully smaller than the maintenance cost of a homegrown alternative.
   5. **Opt-out with `--no-precommit` flag** — Rejected per (c) above (surprise / dual-hook conflicts).
   6. **Tier the hooks** — Ship multiple pre-commit hooks (gitleaks + a markdown-linter + a YAML-linter + …) by default. Rejected as scope creep beyond F-5; if adopters want broader pre-commit coverage they extend `.pre-commit-config.yaml` themselves.
   7. **GitGuardian (commercial SaaS)** — GitGuardian's `ggshield` is the commercial-tier alternative. Rejected for tachi's open-template positioning: requires API key, free tier has rate-limits, sends pattern-match metadata to GitGuardian's servers (privacy concern parallel to trufflehog's verified-credential probing). Adopters with GitGuardian-licensed environments can swap via the documented customization path.
   8. **SecretLint (Node.js-based)** — `secretlint` is an alternative Node.js scanner with broader file-format support (JSON / YAML / XML / Markdown). Rejected because (1) Node.js runtime dependency conflicts with tachi's no-Python-no-Node-runtime distribution preference, (2) gitleaks already covers the file formats tachi uses (text-based config and source files), (3) gitleaks' regex-based detection is faster on tachi's tree.
   9. **git-secrets (AWS-Labs)** — `git-secrets` is the AWS-Labs maintained alternative with narrower scope (focused on AWS credentials + customizable patterns). Rejected because (1) narrower default rule set than gitleaks (only AWS-style patterns by default; OpenAI / Anthropic / GitHub PAT detection requires custom rules), (2) maintenance has slowed (sparse upstream activity vs gitleaks' active development), (3) gitleaks is the broader default for general-purpose secret scanning in 2026.

7. **CI parity workflow: `.github/workflows/gitleaks.yml` (~25-40 LOC, NEW per Team-Lead A-2 finding).** A dedicated single-purpose GitHub Actions workflow that runs gitleaks against PR diffs (or full repo per Architect A-4 — final scope decided at /aod.spec time) using the same `.gitleaks.toml` config. **Important calibration**: the v1.0 PRD framed this as an "extension to existing security-scan workflow"; v1.1 confirms NO existing security-scan workflow exists in `.github/workflows/` (only `release-please.yml`, `tachi-mmdc-preflight.yml`, `tachi-pytest.yml`). A new dedicated `gitleaks.yml` is the right host: single-purpose workflows are easier to disable / debug / replace; mixing security scans into test workflows risks coupling test-failures to security-failures and complicating triage.

8. **CHANGELOG entry under Unreleased → Added**: `Pre-commit secret-scanning default (gitleaks) shipped as opt-in via init.sh prompt; .gitleaks.toml tuned for tachi's fixture and personalization-env conventions; .aod/personalization.env.example template added; CI parity via dedicated .github/workflows/gitleaks.yml; ADR-042 accepted; existing adopters who pull this update do NOT have the hook auto-installed — to enable, run \`pre-commit install\` from the repo root after \`git pull\`.`

**Three things this feature is deliberately NOT:**

1. It is **not** a runtime credential vault, key-rotation tool, or credential-detection-as-a-service. The hook is static configuration scanning local commit content; it does not phone home, encrypt secrets, store rotation history, or emit per-commit decision events. Adopters needing managed credential infrastructure (vault, AWS Secrets Manager, HashiCorp Vault) layer their own — the pre-commit hook is a defense-in-depth gate, not a substitute for credential management.

2. It is **not** a `finding.yaml` / `taxonomy/*.yaml` schema change and **not** a tachi command/agent/skill behavior change. **Twelfth feature in a row with zero `finding.yaml` shape change** (continues BLP-01 detection-tier contract continuity past F-3 and F-4). The only files touched are `.pre-commit-config.yaml` (new), `.gitleaks.toml` (new), `.aod/personalization.env.example` (new template), `init.sh` (~10-20 LOC delta in `scripts/init.sh`), `docs/standards/PRECOMMIT_HOOKS.md` (new), `docs/architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md` (new), `.github/workflows/gitleaks.yml` (new), `CHANGELOG.md` (Unreleased entry), `README.md` (~1 LOC pointer), and optionally `.aod/scripts/bash/precommit-wrap.sh` (small wrapper, location decided at /aod.spec per Q9).

3. It is **not** a replacement for `git commit --no-verify` bypass protection. An adopter who actively wants to bypass the hook can; the local pre-commit framework offers no defense against intentional bypass. CI parity (gitleaks runs on every PR via `.github/workflows/gitleaks.yml`) provides back-stop coverage for accidental bypass, but a *deliberately* malicious commit-and-force-push that bypasses both is out of scope. PRECOMMIT_HOOKS.md documents this as a known limitation with managed-environment-policy-lock as the recommended mitigation for environments that need stronger guarantees.

---

## 🎯 Goals & Non-Goals

### Goals

- **G1**: First-time adopters running `init.sh` and accepting the prompt default get a working pre-commit secret-scanning hook installed and active. Verified by AC-1 + AC-2 + AC-6 below; reviewer can clone tachi, run `init.sh` accepting Y, attempt to commit a known-bad fixture, observe the commit blocked.
- **G2**: Each rule in `.gitleaks.toml` (custom additions and allow-list) has a documented rationale in `docs/standards/PRECOMMIT_HOOKS.md` cross-referenced one-to-one. Verified by reviewer cross-check.
- **G3**: Existing adopters who pull the F-5 update do NOT have a hook auto-installed in `.git/hooks/pre-commit`. Verified by AC-9 (snapshot test).
- **G4**: SecOps reviewer reading `PRECOMMIT_HOOKS.md` as their first introduction to tachi's secret-scanning posture can produce an audit-ready summary (which scanner, which rules, which opt-out, which bypass) without follow-up questions. Verified by PM walk-through.
- **G5**: Tachi's own `make test`, `pre-commit run --all-files`, and routine `/aod.build` workflows produce ZERO gitleaks false-positive findings on the pre-F-5 baseline. Verified by AC-4 (clean-clone smoke test) AND a /aod.spec entry-criteria synthetic-fixture rule-interaction test (per C-4 preventive resolution).
- **G6**: A known-bad fixture (test PAT, test AWS key, test private-key block, test OpenAI key) committed without the `# gitleaks:allow` annotation triggers the hook and blocks the commit with a refused-commit error message containing rule-ID + file:line + bypass guidance + docs pointer (via wrapper script per C-2). Verified by AC-3.
- **G7**: A legitimate placeholder pattern (`password = "$ENV_VAR"`, `OPENAI_API_KEY=$OPENAI_API_KEY`, the `.aod/personalization.env.example` template content) does NOT trigger the hook. Verified by AC-5.
- **G8**: ADR-042 lands in `docs/architecture/02_ADRs/` with status `Accepted` after PM + Architect sign-off.
- **G9**: BLP-02 closes 5/5. Verified by Initiative Tracker memory update referencing F-5 closure and the BLP-02 enterprise-hardening posture-summary.
- **G10**: Post-merge `/security` re-scan: zero new findings emerge on the surface this feature touched (init.sh, `.pre-commit-config.yaml`, `.gitleaks.toml`, etc.). Issue #282 §Definition-of-Done explicitly requires this.
- **G11**: CI parity in place — gitleaks runs on every PR via the new dedicated `.github/workflows/gitleaks.yml`, using the same `.gitleaks.toml`. Verified by AC-12.

### Non-Goals

- **NG1**: No runtime credential management (vault, rotation, encryption). Static-pattern-match scanning only.
- **NG2**: No `finding.yaml` / taxonomy schema changes.
- **NG3**: No tachi agent / command / skill behavior changes (other than init.sh delta and the new GitHub Actions workflow).
- **NG4**: No protection against `git commit --no-verify` deliberate bypass. Documented as known limitation.
- **NG5**: No verified-credential probing. Pattern-match-only detection.
- **NG6**: No multi-language secret detection beyond gitleaks defaults + tachi custom rules.
- **NG7**: No `.secrets.baseline`-style pre-existing-findings snapshot.
- **NG8**: No bug-bounty incentive for finding gaps in the rule set.
- **NG9**: No per-skill / per-agent secret-scanning scoping. The hook is repo-wide.
- **NG10**: No replacement for managed-environment policies that disable `--no-verify` or enforce signed commits.

---

## 👥 User Stories

(Adopted verbatim from Issue #282 §Stories; converted to Job Story format with acceptance criteria.)

### US-1: First-time adopter accidentally committing a credential
> **When** I, an adopter who has just configured tachi for production-adjacent use, paste a GitHub PAT into a commit by accident,
> **I want to** have pre-commit refuse the commit,
> **So I can** prevent the PAT from reaching the remote.

**Acceptance**: Cloning a fresh tachi repo, running `init.sh` and accepting the prompt default Y, configuring `.aod/personalization.env` with a real-format-but-fake PAT, and attempting `git commit -am "config update"` triggers gitleaks to refuse the commit. The error message includes the gitleaks rule ID for "GitHub Personal Access Token", the file path and line number, and the bypass instruction `SKIP=gitleaks git commit ...` (via wrapper-script augmentation per C-2).

### US-2: Security-conscious team wanting default-deny without per-repo design cost
> **When** I, a security-conscious team adopting tachi as our project template,
> **I want to** inherit a default secret-scanning configuration that catches common patterns without requiring per-repo configuration,
> **So I can** focus on building features rather than designing scanning rules from scratch.

**Acceptance**: An adopter team cloning tachi gets `.pre-commit-config.yaml` and `.gitleaks.toml` shipped at repo root with default rules that catch:
- AWS access keys (`AKIA...`)
- GitHub PATs (`ghp_...`)
- OpenAI API keys (`sk-...`)
- Anthropic API keys (`sk-ant-...`)
- Generic high-entropy strings exceeding configured threshold

Without modification of `.gitleaks.toml`, the hook catches all of the above patterns when they appear in a staged commit.

### US-3: Existing adopter not surprised by auto-installed hook
> **When** I, an existing adopter who pulls the F-5 update via `make update` or `git pull`,
> **I want to** NOT have the new pre-commit hook installed automatically without my consent,
> **So I can** preserve my existing commit flow without an unexpected gate.

**Acceptance**: Simulate an existing-adopter clone (one that ran an older init.sh and has no `.git/hooks/pre-commit`). Apply the F-5 update via `git pull`. Inspect `.git/hooks/pre-commit` — no file written by the update. The CHANGELOG and a one-line README pointer instruct: *"To enable pre-commit secret-scanning, run `pre-commit install` from the repo root."*

### US-4: Adopter not frustrated by false positives on legitimate placeholder content
> **When** I, an adopter who legitimately commits placeholder credentials in test fixtures or env-var references (e.g., `password = "$ENV_VAR"` or `OPENAI_API_KEY=PLACEHOLDER`),
> **I want to** have gitleaks defaults recognize tachi's own conventions,
> **So I can** avoid disabling the hook in frustration after a false positive.

**Acceptance**: Committing a file containing the following patterns does NOT trigger the hook:
- `password = "$ENV_VAR"` (env-var reference, not a credential)
- `OPENAI_API_KEY=PLACEHOLDER` (literal placeholder)
- Test fixture under `tests/fixtures/` containing a deliberately-fake AWS key (path-allow-listed)
- Documentation example under `docs/` containing `ghp_<placeholder>` (path-allow-listed)
- `.aod/personalization.env.example` template file with placeholder values (path-allow-listed; shipped by F-5)

The adopter can complete a routine `git commit -am "feature work"` containing the above patterns without manual SKIP-flag intervention. False-positive rate target: zero on tachi's own pre-F-5 tree (verified by AC-4 + /aod.spec synthetic-fixture test per C-4).

---

## ✅ Acceptance Criteria

(Adopted from Issue #282 §Definition-of-Done with v1.0 PRD additions; v1.1 dropped AC-8 per Team-Lead A-3.)

### Mandatory (blocks delivery)

- [ ] **AC-1**: `.pre-commit-config.yaml` lands at repo root, references `gitleaks/gitleaks` upstream repo with a pinned commit hash (NOT a floating tag), specifies `--config=.gitleaks.toml` arg or invokes wrapper script per Q9.
- [ ] **AC-2**: `.gitleaks.toml` lands at repo root, contains gitleaks default rules + tachi-specific allow-list (env-var placeholders, fixture paths, docs paths, `.aod/personalization.env.example`) + tachi-specific custom rules (`tachi-personalization-env`, `tachi-security-exceptions-jsonl`).
- [ ] **AC-3**: Hook fires on a known-bad fixture commit. Concrete test: stage a file containing `ghp_<random40chars>` (test fixture format clarified at /aod.spec per Architect A-9), attempt `git commit`, observe commit refused with error message containing (a) rule ID for "GitHub Personal Access Token" or equivalent, (b) the file:line of the match, (c) `SKIP=gitleaks git commit ...` bypass guidance (via wrapper-script per C-2), (d) docs link `See docs/standards/PRECOMMIT_HOOKS.md`.
- [ ] **AC-4**: `pre-commit run --all-files` from a clean clone with no adopter modifications produces ZERO gitleaks findings on tachi's pre-F-5 baseline tree. Pre-merge cross-check: clone the F-5 branch, install pre-commit, run `pre-commit run --all-files`, confirm zero findings. Findings on test fixture files (`tests/fixtures/`) MUST be zero. Findings on documentation files (`docs/`) MUST be zero.
- [ ] **AC-5**: Hook does NOT fire on legitimate placeholder content. Stage a file containing `password = "$ENV_VAR"` and `OPENAI_API_KEY=PLACEHOLDER`, attempt `git commit`, observe commit succeeds without hook intervention.
- [ ] **AC-6**: `init.sh` opt-in prompt works in interactive mode. Run `scripts/init.sh` from a fresh clone in a TTY context, observe prompt `Install pre-commit secret-scanning hook (gitleaks)? [Y/n]`. Accept default Y, verify `.git/hooks/pre-commit` is written and `pre-commit install` succeeded. (Note: re-running init.sh is not a meaningful test scenario — the script hard-exits when `.aod/personalization.env` exists per Team-Lead A-3.)
- [ ] **AC-7**: `init.sh` opt-in prompt is skipped in non-interactive contexts. Run `scripts/init.sh </dev/null` (no TTY), verify the prompt is skipped (default behavior: no hook install) and no error / no hang occurs. /aod.spec-time decision: TTY check vs explicit `--no-precommit` flag (PRD position: TTY check baseline + flag override per Q4).
- [ ] **AC-8** (NEW per C-1 resolution): `.aod/personalization.env.example` template file lands at the documented path with placeholder values for the keys `init.sh` expects. The file is path-allow-listed in `.gitleaks.toml`. Cross-check: `pre-commit run --all-files` does NOT flag the template file's content.
- [ ] **AC-9**: Existing-adopter no-surprise flow. Simulate: clone tachi, run an *older* init.sh (or skip init.sh entirely), confirm no `.git/hooks/pre-commit`. Apply the F-5 update via `git pull` from a feature branch / merged main. Inspect `.git/hooks/pre-commit` post-pull — no file written. To opt in, the adopter must explicitly run `pre-commit install` from the repo root.
- [ ] **AC-10**: `docs/standards/PRECOMMIT_HOOKS.md` lands and is self-contained. Sections present: Why this hook ships / Installation paths (3) / What gets scanned / Bypass mechanisms / Refused-commit error message contract / CI parity / Re-init behavior / Known limitations / Adopter customization. Reviewer cross-check: each rule and allow-list entry in `.gitleaks.toml` appears in `PRECOMMIT_HOOKS.md` with rationale.
- [ ] **AC-11**: ADR-042 lands at `docs/architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md` with status `Accepted` post-Architect sign-off. Sections present: Context / Decision / Consequences (including pin-bump cadence per A-2 + raw-read-p waiver per C-3) / Alternatives Considered (9 with rejection rationale) / References.
- [ ] **AC-12**: CI parity in place. New dedicated `.github/workflows/gitleaks.yml` workflow runs gitleaks against PR (diff or full-repo scope per Architect A-4 — decided at /aod.spec) using the same `.gitleaks.toml` config. Concrete test: open a feature branch with a deliberately-bad credential file, push, verify the GitHub Actions check fails with a gitleaks finding message that matches the local hook's output (same rule ID, same file:line). After deleting the bad file and pushing again, the CI check passes. Cleanup discipline: the bad-credential commit MUST be cleaned up before merge (per Architect A-10).
- [ ] **AC-13**: CHANGELOG entry under `Unreleased → Added` references the new pre-commit hook + `.gitleaks.toml` + `.aod/personalization.env.example` + ADR-042 + `.github/workflows/gitleaks.yml` + the existing-adopter opt-in path (`pre-commit install` instruction).
- [ ] **AC-14**: README.md gets a one-line pointer to `PRECOMMIT_HOOKS.md` (e.g., a "Security" subsection): *"For pre-commit secret-scanning setup, see [docs/standards/PRECOMMIT_HOOKS.md](docs/standards/PRECOMMIT_HOOKS.md)."* Same precedent as F-3's README pointer to SECURITY.md and F-4's README pointer to CLAUDE_PERMISSIONS.md.
- [ ] **AC-15** (REFRAMED per C-2): Refused-commit error message contract — when gitleaks blocks a commit, the wrapper-script error output includes (a) which secret pattern fired (rule ID), (b) the file:line of the match, (c) `SKIP=gitleaks git commit ...` bypass guidance, (d) a docs link to `PRECOMMIT_HOOKS.md`. Items (a) and (b) are gitleaks defaults; (c) and (d) require a small wrapper script (`.aod/scripts/bash/precommit-wrap.sh` — location confirmed at /aod.spec per Q9) — gitleaks does NOT support stderr-message templating at the CLI level. Verified empirically: stage a file with `ghp_<random40chars>`, attempt commit, capture stderr, confirm all four items present in wrapper-script output.
- [ ] **AC-16**: Post-merge `/security` re-scan: zero NEW findings on the file surfaces F-5 touches (`scripts/init.sh`, `.pre-commit-config.yaml`, `.gitleaks.toml`, `.aod/personalization.env.example`, `docs/standards/PRECOMMIT_HOOKS.md`, `ADR-042`, `.github/workflows/gitleaks.yml`, optional `.aod/scripts/bash/precommit-wrap.sh`).
- [ ] **AC-17**: Post-merge release-please verification. The squash-merge of PR #<F-5> with commit subject `feat(282): pre-commit secret-scanning defaults` triggers a release-please PR within ~30s (per `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles). If empty, push an empty `feat(282): … — release marker` commit per the documented recovery flow.

### /aod.spec Entry-Criteria Test (NEW per C-4 preventive resolution)

- [ ] **AC-SPEC-1** (entry-criteria for /aod.spec, not blocking PRD): synthetic-fixture rule-interaction test. /aod.spec MUST produce a `tests/fixtures/gitleaks-rule-interaction/` directory containing synthetic versions of every adopter scenario currently on file (placeholder env vars, populated env vars, fixture credentials, .security/exceptions.jsonl entries, docs placeholders, .aod/personalization.env.example) plus 10-20 expected-but-not-yet-tested adopter cases. Run `gitleaks --config=.gitleaks.toml` against the fixtures and verify the **expected** rule fires per case (or no rule fires for legitimate placeholder content). This is preventive false-positive verification, not a reactive v4.34.x hot-patch — enforced at /aod.spec entry, not at /aod.deliver time.

### Nice-to-have (post-merge follow-up; not blocking)

- [ ] **AC-18**: Open a follow-up backlog Issue for a **rule-coverage probe** that enumerates the gitleaks default rule IDs active for tachi and confirms tachi's documented threat surface (PAT / AWS / OpenAI / Anthropic / generic-high-entropy) is fully covered. Park as low-priority follow-on; logged at /aod.deliver time.
- [ ] **AC-19**: Open a follow-up backlog Issue for an **adopter-extensibility template**: a `.gitleaks.toml.adopter-template` documenting how adopters add their own custom rules (proprietary credential formats) without disrupting the upstream baseline.

---

## 🛠️ Technical Considerations

### File Surface (v1.1 updated per C-1 + Team-Lead A-2)

| File | Status | Approx LOC | Notes |
|------|--------|-----------|-------|
| `.pre-commit-config.yaml` | NEW | 30-50 | Pinned commit hash; potentially invokes wrapper script per Q9 |
| `.gitleaks.toml` | NEW | 50-80 | Default rules + tachi allow-list + 2 custom rules |
| `.aod/personalization.env.example` | NEW (per C-1) | 10-20 | Template file documenting expected keys |
| `scripts/init.sh` | DELTA | ~10-20 | Opt-in prompt + TTY check |
| `docs/standards/PRECOMMIT_HOOKS.md` | NEW | 150-250 | Self-contained docs |
| `docs/architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md` | NEW | 130-180 (per Team-Lead A-1) | Includes 9 alternatives + pin-bump cadence + raw-read-p waiver |
| `.github/workflows/gitleaks.yml` | NEW (per Team-Lead A-2) | 25-40 | Dedicated CI parity workflow (no existing security-scan workflow exists) |
| `.aod/scripts/bash/precommit-wrap.sh` | NEW (per C-2; optional inline alternative per Q9) | 30-60 | Wrapper script for refused-commit error message contract |
| `CHANGELOG.md` | DELTA | ~3-5 | Unreleased → Added entry |
| `README.md` | DELTA | ~1 | Pointer to PRECOMMIT_HOOKS.md |

**Total new + delta**: 8-9 files, ~440-685 LOC. Materially larger than F-3 (~100 LOC), comparable to F-4 (~430 LOC structured config + standards doc + ADR).

### Out-of-Tree Step

None. F-5 ships entirely in-tree (no GitHub repo settings to toggle; no manual steps required of the adopter beyond the optional `pre-commit install` for existing adopters).

### Cross-Reference: BLP-02 Wave Sequencing

| Wave | Feature | Issue | Status | Closure date |
|------|---------|-------|--------|--------------|
| 1 | F-1 Substitution Surface Hardening | #248 | Delivered | 2026-05-04 |
| 1 follow-on | F-250 Adversarial Unit Extraction Hot-Fix | #250 | Delivered | 2026-05-04 |
| 2 | F-2 Source-Pattern Hardening | #256 | Delivered | 2026-05-05 |
| 3 | F-3 SECURITY.md and Disclosure Channel | #272 | Delivered | 2026-05-08 |
| 4 | F-4 Claude Permissions Baseline | #277 | Delivered | 2026-05-09 |
| **4+** | **F-5 Pre-commit Secret-Scanning Defaults** | **#282** | **In Define** | **Target 2026-05-10; +1 day slack 2026-05-11** |

F-5 was originally planned to ship as a Wave 4 parallel co-ship with F-4. F-4 shipped solo on 2026-05-09 (PR #278); F-5 effectively becomes a post-Wave-4 next-day ship per Team-Lead A-5 (same-day delivery 2026-05-09 unrealistic given today's already-burned hours from F-4 delivery + PRD authoring). With F-5 delivered, BLP-02 closes 5/5 and the LinkedIn-thread punch list (disclosure, permissions, secret-scanning) is fully retired.

### Release-Please Trigger Posture

The PR title MUST be `feat(282): pre-commit secret-scanning defaults` (Conventional Commit format with `feat:` prefix). Post-merge verification at `/aod.deliver` time MUST confirm a release-please PR opens within ~30s of the squash-merge; if not, push an empty `feat(282): … — release marker` commit per the documented recovery flow.

Latest tag at PRD draft (2026-05-09): `v4.33.0`. Manifest at `4.33.0` (in sync; no manifest-vs-tag discrepancy at this draft point).

### Tool Selection: Gitleaks vs Alternatives (summary; full rationale in ADR-042)

| Dimension | gitleaks | trufflehog | detect-secrets | GitGuardian | SecretLint | git-secrets | Decision |
|-----------|----------|------------|----------------|-------------|------------|-------------|----------|
| License | MIT | AGPL-3.0 | MIT | Commercial | MIT | Apache-2.0 | gitleaks (no AGPL friction) |
| Runtime | Go binary | Python | Python | Cloud SaaS | Node.js | Bash + git | gitleaks (single-binary, no runtime) |
| Default scan time | <2s | 5-15s | varies | network-bound | varies | <1s | gitleaks (best dev-loop fit) |
| Default rule breadth | Narrow | Broad | Narrow | Broad | Medium | Narrow (AWS-focused) | trufflehog/GitGuardian win, gitleaks acceptable + extensible |
| Verified-credential probing | No | Yes | Yes | Yes | No | No | gitleaks (privacy-preserving) |
| Adopter swap effort | N/A (default) | Edit `.pre-commit-config.yaml` | Same | Same | Same | Same | gitleaks-default with documented swap path |

Default: gitleaks. Adopters with broader-rule needs swap to trufflehog or GitGuardian via the documented path in `PRECOMMIT_HOOKS.md` §Adopter-Customization.

### Cross-Reference: F-1 (#248) Substitution Surface

F-1 closed the substitution-surface failure mode where adopter-populated config files were committed by accident. F-5's `.gitleaks.toml` complements F-1's `.gitignore` recommendations:

- F-1 prevents `.aod/personalization.env` from being staged in the first place (via `.gitignore:226` — verified empirically).
- F-5 catches the case where F-1's `.gitignore` is not honored (e.g., adopter explicitly `git add -f`-s a file, or the `.gitignore` is locally modified) — gitleaks provides defense-in-depth.

The `tachi-personalization-env` custom rule in F-5's `.gitleaks.toml` is the explicit handoff point: F-1 = preventive (don't stage), F-5 = detective (catch staged anyway). Together they form a layered control. **Prior dependencies satisfied** (per Team-Lead A-4): F-1 #248 DELIVERED 2026-05-04 — `.aod/personalization.env` is gitignored on `main`. F-5 builds against that satisfied baseline.

### Cross-Reference: F-4 (#277) Claude Permissions Baseline

F-4 closed the destructive-operations gap. F-5 closes the credential-exposure gap. Both feature in the BLP-02 enterprise-readiness story; both ship as docs + small config + ADR; both follow the `feat(NNN):` Conventional Commit pattern with release-please verification.

A SecOps reviewer reading the trio (`SECURITY.md` + `CLAUDE_PERMISSIONS.md` + `PRECOMMIT_HOOKS.md`) gets a complete enterprise-readiness picture: how to disclose vulnerabilities, what permissions baseline ships, what credential-exposure gates fire. F-5 completes that triad.

### Security & Privacy

- **Privacy**: gitleaks performs pattern-match-only detection (no outbound HTTP requests). The hook does NOT phone home, does NOT report findings to a central server, does NOT emit telemetry.
- **Supply-chain**: `.pre-commit-config.yaml` references gitleaks via a pinned commit hash. Pin-bump cadence policy documented in ADR-042 §Consequences (per A-2).
- **Secrets in git history**: Hook scans staged content only; secrets already in `git log` are NOT scrubbed by F-5.
- **CI parity**: New `.github/workflows/gitleaks.yml` runs gitleaks on every PR.
- **Bypass mechanisms documented honestly**: PRECOMMIT_HOOKS.md enumerates all bypass paths.

---

## ⚠️ Risks & Mitigations

### R-1: False-positive flood on adopter codebases extending tachi
**Likelihood**: Medium. **Impact**: High (adopter disables hook in frustration → ships broken).
**Mitigation** (v1.1 strengthened per C-4): `.gitleaks.toml` ships with conservative allow-list calibrated against tachi's own tree (verified by AC-4); /aod.spec entry-criteria adds synthetic-fixture rule-interaction test (AC-SPEC-1) — **preventive** false-positive verification before merge, not reactive hot-patch; `PRECOMMIT_HOOKS.md` documents the `# gitleaks:allow` annotation pattern for adopter-specific false positives; AC-19 follow-up Issue captures the adopter-extensibility template work.
**Contingency**: If adopters report false-positive rates >5% on early F-5 deployments, roll out a v4.34.x hot-patch that further constrains the default rule set.

### R-2: Pre-commit framework distribution friction
**Likelihood**: Low-Medium. **Impact**: Medium (adopters on lighter dev environments without Python or brew may struggle).
**Mitigation**: `init.sh` prompt has fallback path: if `pre-commit install` fails, log a one-line WARN and continue init.sh. PRECOMMIT_HOOKS.md documents three install paths.

### R-3: gitleaks upstream tag force-move
**Likelihood**: Low. **Impact**: High (compromised hook would scan adopter trees with arbitrary code).
**Mitigation**: Pin to specific commit hash, not floating tag. Document the pinning policy in ADR-042 §Consequences. ADR-042 §Consequences also documents pin-bump cadence (per A-2): bump on each gitleaks minor release with empirical re-verification.

### R-4: Existing-adopter dual-hook conflict
**Likelihood**: Medium. **Impact**: Low.
**Mitigation**: F-5 ships with no-auto-install on `git pull`. Existing adopters with their own setup remain unchanged until they explicitly `pre-commit install`.

### R-5: `git commit --no-verify` bypass
**Likelihood**: High. **Impact**: Medium (defense-in-depth gate is bypassed; CI parity is the back-stop).
**Mitigation**: Documented as known limitation in PRECOMMIT_HOOKS.md §Known-Limitations. CI parity catches credentials at PR-merge time (verified by AC-12).

### R-6: gitleaks default rule set evolves and breaks tachi's allow-list assumptions
**Likelihood**: Medium. **Impact**: Medium.
**Mitigation**: Pinned commit hash freezes the rule set against tachi's allow-list at the time of pin. Pin-bump cadence policy (A-2) requires synthetic-fixture re-test (AC-SPEC-1) before merging the bump.

### R-7: Privacy concern — gitleaks scanning adopter-private codebase content
**Likelihood**: N/A (gitleaks is local-only; no outbound HTTP). **Impact**: N/A.
**Mitigation**: PRECOMMIT_HOOKS.md §Privacy documents pattern-match-only detection.

### R-8: PR/CI gate flakiness causing false PR-merge blocks
**Likelihood**: Low. **Impact**: Low.
**Mitigation**: gitleaks is deterministic; flakiness sources would be CI-environment-specific. Pinned commit hash mitigates upstream-distribution flakiness.

### R-9 (NEW per Architect A-6): Adopter `.gitleaks.toml` divergence on `make update`
**Likelihood**: High (adopters extending the rule set is the documented expected pattern). **Impact**: Medium (failed update or merge conflict).
**Mitigation**: PRECOMMIT_HOOKS.md §Adopter-Customization documents the merge pattern; the `.gitleaks.toml` structure separates `[allowlist]` (adopter-additive) from `[extend]` (tachi-baseline). Adopters review merge conflicts on `make update` for this file.
**Contingency**: Document the merge-conflict resolution pattern in PRECOMMIT_HOOKS.md.

### R-10 (NEW per Architect A-7): Pre-commit framework version drift
**Likelihood**: Low. **Impact**: Low.
**Mitigation**: PRECOMMIT_HOOKS.md §Known-Limitations documents the minimum pre-commit version supported (`>= 3.5.0`). The pinned `gitleaks` hash protects gitleaks; it does NOT protect against a pre-commit-framework regression.

---

## 📊 Success Metrics

### Primary Metrics (Leading Indicators)

**M1: Adoption rate of opt-in prompt among first-time adopters**
- Target: >70% (based on opt-in-default research).
- Measurement: Inferred via GitHub stars + community feedback (no telemetry by design).

**M2: False-positive rate on tachi's own tree**
- Target: 0 (verified by AC-4 + AC-SPEC-1 at /aod.spec entry).

### Secondary Metrics (Lagging Indicators)

**M3: Reported credential-exposure incidents in tachi-derived adopter projects**
- Target: Reduction over time post-F-5 deployment (qualitative).

**M4: BLP-02 closure**
- Baseline (pre-F-5): 4/5 delivered.
- Target: 5/5 post-F-5 merge.

---

## 🔍 Scope & Boundaries

### In Scope (F-5 / single feature branch)

**Must Have (P0)**:
- ✅ `.pre-commit-config.yaml` with gitleaks pinned to commit hash
- ✅ `.gitleaks.toml` with gitleaks defaults + tachi allow-list + 2 custom rules
- ✅ `.aod/personalization.env.example` template (NEW per C-1)
- ✅ `scripts/init.sh` opt-in prompt (default Y, TTY-skip)
- ✅ `docs/standards/PRECOMMIT_HOOKS.md`
- ✅ `ADR-042` (130-180 LOC per Team-Lead A-1)
- ✅ `.github/workflows/gitleaks.yml` (dedicated CI parity workflow per Team-Lead A-2)
- ✅ Optional `.aod/scripts/bash/precommit-wrap.sh` per Q9 (location decided at /aod.spec)
- ✅ CHANGELOG entry
- ✅ README pointer
- ✅ Refused-commit error message contract (rule ID + file:line + bypass + docs link via wrapper script per C-2)

**/aod.spec Entry-Criteria (P0 test gate, not blocking PRD)**:
- ✅ AC-SPEC-1 synthetic-fixture rule-interaction test (per C-4 preventive resolution)

### Out of Scope (Future Phases)

**Could Have (P2)** — not in F-5:
- 🔮 `.gitleaks.toml.adopter-template` (deferred per AC-19)
- 🔮 Rule-coverage-probe documentation (deferred per AC-18)
- 🔮 Multi-scanner support (gitleaks + trufflehog parallel)
- 🔮 PR auto-commenter for gitleaks findings

**Won't Have** — explicitly excluded:
- ❌ Runtime credential vault / rotation
- ❌ `finding.yaml` schema changes
- ❌ Tachi agent / command / skill behavior changes
- ❌ `--no-verify` bypass protection
- ❌ History-scan tooling
- ❌ Bug-bounty incentives for finding allow-list gaps

### Constraints

**Technical**:
- C1: gitleaks must be available as a pinned-hash repo on GitHub (verified — `https://github.com/gitleaks/gitleaks` is current).
- C2: Pre-commit framework's hook-installation semantics are fixed.
- C3: GitHub Actions step uses the same `.gitleaks.toml`.

**Business**:
- C4: Single-maintainer project. F-5 must be implementable in 1-2 days (~9-13h active envelope per Team-Lead A-1).
- C5: BLP-02 closure on F-5 merge.

**External**:
- D1: gitleaks upstream repo availability (mitigated by pinned hash).
- D2: pre-commit framework upstream availability.

---

## 🛣️ Timeline & Milestones

### Phase Breakdown (v1.1 updated per Team-Lead A-1 + A-5 + A-7)

**Phase 1: PRD + Spec + Tasks** (2026-05-09, residual hours)
- PRD draft + Triad reviews + sign-offs ~2-3h (mostly complete at this PRD write)
- /aod.spec → spec.md with PM sign-off (~1-2h) — includes AC-SPEC-1 fixture authoring
- /aod.project-plan → plan.md with PM + Architect sign-off (~1-2h)
- /aod.tasks → tasks.md with triple sign-off (~30-60min)
- **Day-1 budget**: 2-4h residual; spec/plan/tasks reasonably fit.

**Phase 2: Implementation + Verification** (2026-05-10, full day)
- `.pre-commit-config.yaml` + `.gitleaks.toml` (~1.5-2h)
- `.aod/personalization.env.example` (~30min)
- init.sh prompt + TTY check (~30-45min)
- PRECOMMIT_HOOKS.md authoring (~2-3h)
- ADR-042 authoring (~1.5-2h, expanded LOC)
- `.github/workflows/gitleaks.yml` authoring + smoke test (~30-60min)
- Optional precommit-wrap.sh + AC-15 verification (~1-1.5h depending on Q9 outcome)
- AC-3/AC-4/AC-5/AC-6/AC-7/AC-9/AC-12/AC-15 empirical verification (~1-2h)
- **Phase 2 envelope**: 9-13h (per Team-Lead A-1 calibration)

**Phase 3: Delivery** (2026-05-10 evening or 2026-05-11)
- /aod.deliver: PR ready, squash-merge, release-please verification, AC-17 (~30min)
- BLP-02 5/5 closure memory update
- AC-16 post-merge `/security` re-scan
- AC-18 / AC-19 follow-up Issues filed

### Key Milestones (updated per Team-Lead A-5)

| Milestone | Target Date | Slack Date | Owner | Status |
|-----------|-------------|-----------|-------|--------|
| PRD Approval | 2026-05-09 | — | product-manager | ✅ Approved (this PRD) |
| Spec Approval | 2026-05-09 | 2026-05-10 | architect | 📋 Pending |
| Plan Approval | 2026-05-09 | 2026-05-10 | architect | 📋 Pending |
| Tasks Approval | 2026-05-09 | 2026-05-10 | team-lead | 📋 Pending |
| Implementation Complete | 2026-05-10 | 2026-05-11 | senior-backend-engineer | 📋 Pending |
| Tests/CI Green | 2026-05-10 | 2026-05-11 | tester | 📋 Pending |
| /aod.deliver | 2026-05-10 | 2026-05-11 | devops | 📋 Pending |
| BLP-02 Closure | 2026-05-10 | 2026-05-11 | product-manager | 📋 Pending |

Legend: ✅ Complete | 🟢 On Track | 🟡 In Review | 📋 Pending | 🔴 Blocked

---

## ❓ Open Questions

### Product Questions
- [ ] Q1: Should `tachi-personalization-env` custom rule warn-only or block? — Owner: PM at /aod.spec time — PRD position: warn-only.
- [ ] Q2: Should `tachi-security-exceptions-jsonl` custom rule warn-only or block? — Owner: PM at /aod.spec time — PRD position: warn-only.
- [ ] Q3: Should AC-18 and AC-19 follow-up Issues be filed pre-merge or post-merge? — Owner: PM at /aod.deliver time — PRD position: post-merge.

### Technical Questions
- [ ] Q4: TTY check vs explicit `--no-precommit` flag for non-interactive opt-out? — Owner: Architect at /aod.spec time — PRD position: TTY check baseline + `--no-precommit` flag override + explicit `--precommit` flag for `expect`-style automation (per Architect Q4 expansion).
- [ ] Q5: Workflow file confirmed as new `.github/workflows/gitleaks.yml` (per Team-Lead A-2). /aod.spec confirms PR-diff vs full-repo scan scope (per Architect A-4; PRD position: full-repo scan on PRs).
- [ ] Q6: Refused-commit error message customization confirmed as wrapper-script approach (per Architect C-2; gitleaks formatter override is infeasible). /aod.spec finalizes wrapper script content.
- [ ] **Q9** (NEW per C-2): Wrapper script location — `.aod/scripts/bash/precommit-wrap.sh` (separate file, easier to test/version) vs inline `entry: bash -c '...'` in `.pre-commit-config.yaml` (no separate file, but harder to maintain)? — Owner: Architect at /aod.spec time — PRD position: separate file at `.aod/scripts/bash/precommit-wrap.sh` for testability.
- [ ] **Q10** (NEW per C-3): init.sh prompt validator — raw `read -p` (acceptable for single-char Y/n per ADR-042 §Consequences waiver) vs F-1's `aod_init_read_validated` helper (consistency with F-1 input-validation discipline)? — Owner: Architect at /aod.spec time — PRD position: raw `read -p` with explicit waiver in ADR-042.

### Design Questions
- [ ] Q7: README pointer placement — under "Installation" / under "Security" / new "Disclosure" subsection? — Owner: PM at /aod.spec time — PRD position: under existing "Security" subsection consistent with F-3 / F-4 README pointers.

### Business Questions
- [ ] Q8: Is next-day delivery target (2026-05-10) realistic given Triad-review-cycle plus implementation envelope? — Owner: Team-Lead — Status: Resolved at this PRD review per Team-Lead A-5; 2026-05-10 with 2026-05-11 slack.

---

## 📚 References

### Product Documentation
- Product Vision: `docs/product/01_Product_Vision/product-vision.md`
- BLP-02 Initiative Tracker: memory `project_blp02_enterprise_hardening.md`
- Issue #282: `https://github.com/davidmatousek/tachi/issues/282`

### Technical Documentation
- Constitution: `.aod/memory/constitution.md`
- Git Workflow: `.claude/rules/git-workflow.md`
- Design Quality: `.claude/rules/design-quality.md`
- F-3 PRD precedent: `docs/product/02_PRD/272-security-md-disclosure-2026-05-08.md`
- F-4 PRD precedent: `docs/product/02_PRD/277-claude-permissions-baseline-2026-05-08.md`

### External Resources
- Pre-commit framework: `https://pre-commit.com/`
- Gitleaks: `https://github.com/gitleaks/gitleaks`
- Trufflehog (alternative): `https://github.com/trufflesecurity/trufflehog`
- Detect-secrets (alternative): `https://github.com/Yelp/detect-secrets`
- Daniel Wood LinkedIn thread (2026-05-02): grounding context for BLP-02

### Triad Review Artifacts
- Architect review v1.0 + v1.1: `.aod/results/architect-prd-282.md`
- Team-Lead review v1.0: `.aod/results/team-lead-prd-282.md`
- PRD draft v1.0 (pre-review): `.aod/results/prd-draft-282.md`

---

## ✅ Approval & Sign-Off

### PRD Review Checklist

**Product Manager** (product-manager):
- [x] Problem statement is clear and user-focused
- [x] User stories have measurable acceptance criteria
- [x] Success metrics are defined and measurable
- [x] Scope is realistic for timeline (next-day target with +1 day slack per Team-Lead A-5)
- [x] Risks and dependencies identified (R-1 through R-10)
- [x] Aligns with product vision and BLP-02 closure

**Architect**:
- [x] Technical requirements are clear (gitleaks vs trufflehog rationale; pinned-hash supply-chain posture; CI parity design; custom-rule scope; wrapper-script for AC-15 per C-2; raw-read-p waiver per C-3)
- [x] Non-functional requirements are realistic
- [x] Dependencies are accurate (gitleaks repo availability; pre-commit framework distribution)
- [x] Technical risks are identified (R-1 through R-10)
- [x] Architecture approach is sound (additive custom rules; opt-in install posture; preventive synthetic-fixture test per C-4)

**Engineering Lead** (team-lead):
- [x] Requirements are implementable
- [x] Effort estimates are reasonable (9-13h active envelope per A-1; 8 file artifacts per A-2)
- [x] Team capacity is available (Saturday 2026-05-10 active per F-3 / F-4 weekend-active precedent)
- [x] Timeline is realistic (next-day target 2026-05-10 with 2026-05-11 slack per A-5 + A-7)

### Approval Status

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ APPROVED | 2026-05-09 | v1.1 final |
| Architect | architect | ✅ APPROVED_WITH_CONCERNS | 2026-05-09 | 4 of 4 v1.0 CHANGES resolved + 4 of 6 advisories folded |
| Engineering Lead | team-lead | ✅ APPROVED_WITH_CONCERNS | 2026-05-09 | 5 of 7 advisories folded into v1.1; A-4 + A-7 deferred to /aod.spec |

Legend: ✅ Approved | 🟡 Approved with Comments | ❌ Rejected | 📋 Pending

---

## 📝 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-09 | product-manager | Initial PRD draft. |
| 1.1 | 2026-05-09 | product-manager | C-1: added `.aod/personalization.env.example` template to in-scope. C-2: reframed AC-15 to wrapper-script approach (gitleaks formatter override infeasible) with new Q9. C-3: added ADR-042 §Consequences explicit waiver for raw `read -p` (single-char Y/n below F-1 threshold) with new Q10. C-4: added /aod.spec entry-criteria synthetic-fixture rule-interaction test (AC-SPEC-1) to strengthen R-1 mitigation preventively. Team-Lead advisories folded: A-1 Phase 2 estimate updated to 9-13h floor + ADR-042 to 130-180 LOC; A-2 added new dedicated `.github/workflows/gitleaks.yml` (~25-40 LOC) replacing 'extend existing workflow' framing (no existing security-scan workflow exists); A-3 dropped AC-8 (init.sh hard-exit + self-delete makes re-init double-prompt scenario impossible); A-5 anchored milestone targets at 2026-05-10 with 2026-05-11 slack; A-6 reframed AC-15 spike scope. Architect advisories folded: A-1 ADR-042 alternatives expanded with GitGuardian / SecretLint / git-secrets dismissals (alternatives 7-9); A-2 pin-bump cadence policy added to ADR-042 §Consequences; A-6 R-9 (adopter `.gitleaks.toml` divergence) added; A-7 R-10 (pre-commit framework version drift) added. Architect A-3 / A-4 / A-9 / A-10 + Team-Lead A-4 + A-7 deferred to /aod.spec time per their framing. |
