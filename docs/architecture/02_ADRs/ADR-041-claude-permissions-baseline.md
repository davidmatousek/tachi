# ADR-041: Claude Code Permissions Baseline — Four-Category `.claude/settings.json` + Self-Contained Policy Decision Log

**Status**: Accepted
**Date**: Proposed: 2026-05-08 (PRD v1.1 Approved); Accepted: 2026-05-08 (squash-merge of feature 277).
**Deciders**: PM (APPROVED 2026-05-08), Architect (APPROVED 2026-05-08), Team-Lead (APPROVED_WITH_CONCERNS 2026-05-08).
**Feature**: [277-claude-permissions-baseline](../../../specs/277-claude-permissions-baseline/spec.md)
**Initiative**: BLP-02 Wave 4 (enterprise hardening — fourth feature in the 5-feature initiative; Daniel Wood 2026-05-02 LinkedIn-thread trigger shared with F-3).
**Supersedes**: None
**Superseded by**: None
**Related ADRs**: None directly. ADR-040 (F-2 config-file parsing hardening) shares the same Wood-thread origin but addresses a separate code-path attack surface; ADR-041 is the first ADR to govern the AI-agent permissions surface.

---

## Context

Tachi's pre-F-4 `.claude/settings.json` was a 26-rule allow-only file accumulated organically. The 2026-05-02 Daniel Wood LinkedIn thread named the resulting posture as a load-bearing gap for enterprise-developer adoption. The PRD enumerated six concrete deficits: (1) no `deny` rules — destructive operations (`rm -rf`, `git push --force`, `gh release delete`, `npm publish`, `dd`, `mkfs`) had no project-level safety net; (2) no `ask` rules — operations between "trivially safe" and "catastrophically destructive" (`git push --force-with-lease`, `gh release create`, `brew install`, `eval`) had no calibrated gate for the gray zone; (3) no network host allowlist — `WebFetch` was unconstrained; (4) no per-rule documentation — SecOps reviewers reverse-engineered maintainer intent; (5) `Edit` / `Write` unconditionally auto-approved without read/write distinction in the audit log; (6) no bash-pattern destructive denials — `Bash(git push:*)` matched both `git push` and `git push --force`.

The six gaps share a common root: the file was a **convenience artifact**, not a **policy decision log**. Closing the gap means re-framing the file as a posture surface, grounding every rule in audit-defensible rationale, and shipping that rationale as a first-class policy document. F-4 is documentation + settings-file rewrite + this ADR — no agent / command / skill / script code change, no schema delta, no test surface. Same docs-only shape as F-3 (#272) but with an explicit ADR — F-4 is itself the Constitution Principle X §Architecture Review artifact.

---

## Decision

We will replace `.claude/settings.json` with a curated, four-category permissions baseline accompanied by a self-contained policy decision log (`docs/standards/CLAUDE_PERMISSIONS.md`) and this ADR. The seven decision items below are reciprocally documented in `CLAUDE_PERMISSIONS.md` (the operator-facing surface) and `spec.md` FR-001..FR-014 (the behavior contract).

### Decision Item 1 — Four-category logical framing (read-only / local-state / destructive / network)

The baseline organizes rules into four logical categories:

- **Category 1 — Read-only auto-approve** (~10 non-built-in rules): `Bash(rg:*)`, `Bash(gh issue view:*)`, `Bash(gh pr view:*)`, etc. Built-in read-only commands (`ls`, `cat`, `head`, `tail`, `grep`, `find`, `wc`, `diff`, `stat`, `du`, `cd`, read-only `git` forms) are deliberately omitted — listing them is no-op.
- **Category 2 — Local-state auto-approve** (~30 rules): recoverable mutations (`Edit`, `Write`, `Bash(git add:*)`, `Bash(git commit:*)`, `Bash(npm test:*)`, `Bash(make:*)`, etc.). Network-touching writes (`Bash(git push:*)`, `Bash(git pull:*)`, `Bash(gh issue create:*)`) live here when the destructive variant is denied at Category 3a.
- **Category 3 — Destructive deny+ask** (~20 deny + ~12 ask = ~32 rules total): catastrophic-irreversible at `permissions.deny` (e.g., `Bash(rm -rf:*)`, `Bash(git push --force:*)`, `Bash(git reset --hard:*)`, `Bash(gh release delete:*)`, `Bash(npm publish:*)`, `Bash(dd:*)`, `Bash(sudo:*)`); usually-safe-but-warrants-confirmation at `permissions.ask` (e.g., `Bash(git push --force-with-lease:*)`, `Bash(gh release create:*)`, `Bash(brew install:*)`, `Bash(eval:*)`).
- **Category 4 — Network host-allowlist** (19 explicit per-subdomain `WebFetch(domain:<host>)` rules): GitHub family, Anthropic family, OWASP family, MITRE family, NIST. Per-subdomain explicit because subdomain matching is not transitive (Issues #15260, #11972, #1217).

The four-category framing is a CLAUDE_PERMISSIONS.md convention; the JSON committed to disk has only the three Claude-Code-native arrays (`deny`, `ask`, `allow`).

### Decision Item 2 — Strict JSON commit; per-rule rationale lives only in CLAUDE_PERMISSIONS.md

Claude Code's `settings.json` schema is strict JSON (RFC 8259) — no `//` comments, no JSONC. Per-rule rationale therefore lives **exclusively in** `CLAUDE_PERMISSIONS.md`, cross-linked one-to-one with the rules in `.claude/settings.json` via the AC-2 cross-check script (every non-built-in rule appears in the per-rule table; every table row references a rule or is flagged as built-in).

### Decision Item 3 — Honest cross-list `deny → ask → allow` precedence; documented with worked examples

Per Claude Code documentation (`code.claude.com/docs/en/permissions`), permission rules are evaluated `deny → ask → allow`; first matching rule wins. The baseline relies on this cross-list ordering for cases like `Bash(git push --force:*)` (deny) overriding `Bash(git push:*)` (allow at Category 2) — **not** on a "more-specific-pattern-wins-within-a-list" mechanism, which Claude Code does not implement.

CLAUDE_PERMISSIONS.md §Settings-Precedence walks SecOps reviewers through the ordering with two worked examples: (a) the within-file `Bash(git push:*)` allow + `Bash(git push --force:*)` deny case, and (b) the cross-file case where adopter `.claude/settings.local.json` `Bash(rm -rf:*)` allow does NOT override the project-level deny (denylist always takes precedence over allowlist across files per `code.claude.com/docs/en/settings`).

### Decision Item 4 — Nineteen explicit per-subdomain Category 4 entries (no root-domain collapse)

Claude Code Issues #15260, #11972, #1217 confirm `WebFetch(domain:github.com)` does NOT match `api.github.com` and `WebFetch(domain:*)` wildcard does NOT work. The 19-domain list is the result of a tachi command-surface egress audit covering: `github.com`, `api.github.com`, `raw.githubusercontent.com`, `githubusercontent.com`, `objects.githubusercontent.com`, `codeload.github.com`, `github.io` (GitHub family); `code.claude.com`, `docs.anthropic.com`, `anthropic.com`, `claude.com`, `platform.claude.com` (Anthropic family); `owasp.org`, `cheatsheetseries.owasp.org`, `genai.owasp.org` (OWASP family); `mitre.org`, `attack.mitre.org`, `atlas.mitre.org` (MITRE family); `csrc.nist.gov` (NIST). AC-7 retains a manual probe as adversarial verification — if Claude Code semantics ever changes to support subdomain collapse, the list MAY be reviewed for compaction in a follow-up Issue.

### Decision Item 5 — `.claude/settings.local.json` cross-file precedence preserved + clarified

`.claude/settings.local.json` remains the adopter-customization surface for **adding personal allows** for operations not denied at the project level. It does NOT override project-level denies (cross-file deny precedence per Claude Code documentation). Adopters wishing to permit a baseline-denied operation MUST fork-and-edit `.claude/settings.json` directly per CLAUDE_PERMISSIONS.md §Opt-Out-Paths Path 2. AC-12 verifies this experimentally with a transient fixture (CREATE → ATTEMPT → REMOVE); FR-003 verifies the file-untouched property at git-pull time.

### Decision Item 6 — Three documented opt-out paths

CLAUDE_PERMISSIONS.md §Opt-Out-Paths enumerates three override paths with calibrated use-cases: (Path 1) per-tool disable via Claude Code CLI flag, for short-term sandbox sessions; (Path 2) fork-and-edit `.claude/settings.json` — the load-bearing path for permitting a baseline-denied operation given cross-file deny precedence; (Path 3) `.claude/settings.local.json` for *adding* personal allows for operations not denied at the project level. Every legitimate adopter scenario maps to one of the three paths — the procurement-defensible answer to "how does this baseline handle our edge case?"

### Decision Item 7 — Verification recipe as the structural integrity surface

The verification recipe (`plan.md` §Verification-Recipe) is the structural integrity test for the baseline. Programmatic: AC-1 (`jq -e empty` JSON validity), AC-2 (rule-vs-doc cross-check), AC-9 (no-machine-paths grep). Interactive: AC-6 sub-checks (built-in `git status` auto-approve regression + `Bash(rm -rf)` deny prompt), AC-7 (subdomain probe), AC-12 (cross-file fixture). Post-merge `/security` re-scan (FR-014) is regression-only — F-4 closes no `/security` finding directly (posture-gap-closure, not vuln-closure). The recipe is reproducible by future maintainers; CLAUDE_PERMISSIONS.md §Settings-Precedence documents the AC-12 fixture-and-cleanup procedure as a reference smoke-test.

---

## Alternatives Considered

### Alternative 1: Keep current 26-rule allow-only file (do nothing)

**Pros**:
- Zero implementation cost; ~9h envelope reclaimed for other BLP-02 work.
- No risk of introducing a regression (current file is known-working).
- Adopters with established `.claude/settings.local.json` workflows experience zero friction.

**Cons**:
- Fails the BLP-02 enterprise-hardening rubric (the explicit motivating test).
- SecOps reviewers reverse-engineer 26 rules to answer audit-policy questions.
- No defense-in-depth gate against destructive operations; `git push --force` auto-approves alongside regular `git push`.
- Network egress is unconstrained.

**Why Not Chosen**: The do-nothing alternative is the strongest counterfactual — it is what the project shipped pre-F-4 and what the 2026-05-02 Daniel Wood thread explicitly named as the gap. Closing the gap is the feature; "no" is functionally PRD-rejection.

### Alternative 2: Ship `.claude/settings.example.json` template; let adopters copy

**Pros**:
- Adopter-respect framing — they make the explicit choice to opt in to the baseline.
- Avoids any backward-compat concern (existing `.claude/settings.json` files are untouched).
- Lower maintenance burden if the baseline drifts from upstream Claude Code semantics.

**Cons**:
- Adopters who don't opt in get the unhardened default — the gap re-opens for the majority who treat templates as inspiration, not requirement.
- Bifurcates the audit surface: SecOps reviewers must check `.claude/settings.json` content AND verify the adopter copied the example.
- The "ship the safe default; let adopters opt out" pattern is the established norm for project-level security baselines (cf. `.editorconfig`, `.prettierrc`, `.gitignore`).

**Why Not Chosen**: Default-secure beats default-permissive-with-template-available. The gap closes only when the baseline is the active default, not the optional inspiration.

### Alternative 3: Ship empty `.claude/settings.json` (BYO permissions)

**Pros**:
- Maximum adopter control — they author every rule from scratch.
- Zero risk of the baseline being miscalibrated for an adopter's specific environment.
- Simple shipped artifact (one-line file, no maintenance burden).

**Cons**:
- Worse than Alternative 1 — empty settings means fall-through to Claude Code default, which prompts on most operations and trains adopters to click-through approvals.
- Adopters without security-engineering capacity get no help; the baseline is most valuable for them.
- Defeats the BLP-02 enterprise-hardening goal (the entire point is to ship an audit-ready default).

**Why Not Chosen**: BYO is the wrong default for a security-baseline question. The default should encode the project's considered judgment; advanced adopters customize via the documented opt-out paths.

### Alternative 4: Ship enterprise managed-settings.json artifact

**Pros**:
- Managed-settings is the Claude Code mechanism for IT-deployed organization-wide policy.
- Highest-priority precedence layer (overrides user-settings, settings.local.json, settings.json).
- Makes the baseline tamper-resistant for adopters who lock down the managed-settings path via deployment automation.

**Cons**:
- Managed-settings.json is an **enterprise IT deployment artifact**, not a project-level open-source surface. Tachi has no IT-deployment relationship with adopters.
- Shipping a managed-settings.json template would require adopters to copy it to `/Library/Application Support/Claude/` (macOS) or analogous Windows/Linux paths — an out-of-band install step that does not survive a `git pull`.
- Mismatches the open-source consumption model. Tachi is consumed via clone-and-update; managed-settings assumes a centrally-administered deployment.

**Why Not Chosen**: Wrong layer. Project `.claude/settings.json` is the correct surface for tachi-the-open-source-project; managed-settings is the correct surface for individual organizations adopting tachi internally (and they author it themselves per their IT policy).

### Alternative 5: PreToolUse hooks as the destructive-operation gate

**Pros**:
- Hooks run arbitrary code; can implement smarter pattern matching than Claude Code's literal-string Bash patterns (closes R-8 Bash pattern fragility).
- Can inspect the resolved command after process-wrapper expansion (closes R-9 wrapper bypass).
- Composable with a permissions baseline (a hook can supplement deny rules, not replace them).

**Cons**:
- Hooks are implementation code (bash scripts, etc.) — adding them inflates the F-4 surface from "documentation + settings rewrite" to "documentation + settings + new shell scripts + per-script test surface."
- The hook audit surface is harder for SecOps reviewers to reason about than declarative rules — every hook is a code-review obligation.
- F-4's deny rules are calibrated against the **casual-typo case**, not the adversarial-bypass case. Hooks would address adversarial bypass — a separate threat model out of F-4 scope.
- Adding hooks here would conflate two concerns: declarative-policy (settings.json) and procedural-defense-in-depth (hooks). They're better solved as separate features.

**Why Not Chosen**: Out of F-4 scope; the right solution for adopters who require strict guarantees beyond casual-typo defense, but a separate feature with its own threat model and PRD. CLAUDE_PERMISSIONS.md §Known-Limitations notes hooks as the recommended defense-in-depth path for environments that need it.

### Alternative 6: Explicit `.claude/settings.local.json` template shipped alongside `.claude/settings.json`

**Pros**:
- Gives adopters a "starter kit" for their personal customizations.
- Documents the override path by example, not just by reference in CLAUDE_PERMISSIONS.md.

**Cons**:
- `.claude/settings.local.json` is gitignored by Claude Code convention — committing a template file fights that convention and risks adopters checking it in by accident.
- Adopters' personal customizations are intrinsically per-adopter; a one-size-fits-all template is either too narrow (rarely useful) or too broad (overrides the baseline's intent).
- Adds a fourth surface to the cross-check problem (every rule that appears in the template must be reasoned about: does it override the baseline? does it contradict CLAUDE_PERMISSIONS.md?).
- The override path is well-documented in CLAUDE_PERMISSIONS.md §Opt-Out-Paths without requiring a checked-in template.

**Why Not Chosen**: A template fights Claude Code's gitignore convention and inflates the cross-check surface without proportional value. CLAUDE_PERMISSIONS.md documentation is the right level of override-path support.

---

## Consequences

### Positive

- **Audit-ready posture** for enterprise SecOps reviewers — per-rule rationale + governance framing + opt-out paths + known limitations satisfy NIST AI RMF GV.RR-aligned and CSA AICM Pre-Procurement-Questionnaire-style rubrics.
- **Defense-in-depth gate** on destructive operations — `git push --force`, `rm -rf`, `git reset --hard`, `gh release delete`, `npm publish`, `dd`, `mkfs`, `sudo` are explicit denies; `git push --force-with-lease`, `gh release create`, `brew install`, `eval` are explicit asks. The casual-typo case is closed.
- **Backward-compatible** with adopter `.claude/settings.local.json` customizations for permissive overrides of operations not denied at the project level (Constitution Principle III preserved by Claude Code native cross-file precedence; FR-003 fixture verifies experimentally).
- **Documented cross-file deny precedence** — CLAUDE_PERMISSIONS.md §Settings-Precedence clarifies the override path (fork-and-edit) for adopters wishing to permit a baseline-denied operation, closing the surprise-quotient gap before the first adopter encounters it.
- **Network egress audited** — 19 explicit per-subdomain entries cover the tachi command surface (GitHub + Anthropic + OWASP + MITRE + NIST families); third-party MCP-server egress to undocumented domains surfaces a prompt rather than silently auto-approving.

### Negative

- **`.claude/settings.json` is more verbose** (~80 LOC vs 26 LOC pre-F-4) — accepted in exchange for safety + auditability. CLAUDE_PERMISSIONS.md absorbs the rationale; the JSON itself stays minimal (rule strings only, no inline comments per strict-JSON commit decision).
- **Bash pattern fragility (R-8)** — deny rules pattern-match the literal command-line string. `bash -c 'rm -rf /tmp/x'` does NOT match `Bash(rm -rf:*)` because the wrapper changes the matched string. Calibration: deny rules are casual-typo, not adversarial. Documented in CLAUDE_PERMISSIONS.md §Known-Limitations.
- **Process-wrapper bypass (R-9)** — `npx`, `docker exec`, `devbox run`, `mise exec`, `direnv exec` re-shell-out commands; deny does not transit the wrapper. Same calibration as R-8. Adopters running tachi inside Docker/devbox/mise environments lose the destructive-deny baseline for wrapper-issued commands. Hooks (Alternative 5) are the path forward for environments requiring this guarantee.
- **Read-only built-in shadow (R-10)** — a future Claude Code update may add a built-in command that shadows an explicit allow rule, making it no-op. CLAUDE_PERMISSIONS.md §Built-in-Read-Only-Set documents the maintenance contract: re-verify the built-in set against the latest Claude Code release on each `/aod.update` cycle.

### Mitigation

The R-8/R-9/R-10 limitations are **disclosed honestly** in CLAUDE_PERMISSIONS.md §Known-Limitations rather than papered over. The verification recipe + manual probes catch baseline regressions on every rewrite; the AC-2 cross-check guards against rule/doc drift; CHANGELOG migration guidance documents the adopter-impact of every baseline change. Post-merge `/security` re-scans on every cycle are regression-only — F-4 closes no `/security` finding directly because the gap was a posture-document absence, not a vuln pattern.

---

## Related Findings

- **H-4 (`docs/security/OPEN_SOURCE_READINESS.md`)** — absolute-path audit finding for `.claude/settings.json`. Pre-F-4 `.claude/settings.json` was clean (FR-009 grep returned zero matches at plan-stage cross-check); F-4 verifies the rewrite does not regress this property via FR-009 / AC-9 grep. Cross-referenced for traceability — F-4 is not closing the H-4 finding (it was already clean) but is guarding against re-introduction.
- **No `/security` finding directly closed** — F-4 is posture-gap-closure, not vuln-closure. The post-merge `/security` re-scan (FR-014) is regression-only.

---

## References

- Feature 277 PRD: [docs/product/02_PRD/277-claude-permissions-baseline-2026-05-08.md](../../product/02_PRD/277-claude-permissions-baseline-2026-05-08.md)
- Feature 277 Spec: [specs/277-claude-permissions-baseline/spec.md](../../../specs/277-claude-permissions-baseline/spec.md) (FR-001..FR-014)
- Feature 277 Plan: [specs/277-claude-permissions-baseline/plan.md](../../../specs/277-claude-permissions-baseline/plan.md)
- Operator-facing policy decision log: [docs/standards/CLAUDE_PERMISSIONS.md](../../standards/CLAUDE_PERMISSIONS.md)
- Claude Code permissions documentation: `https://code.claude.com/docs/en/permissions`
- Claude Code settings documentation (cross-file precedence): `https://code.claude.com/docs/en/settings`
- Upstream subdomain-matching Issues: `https://github.com/anthropics/claude-code/issues/15260`, `https://github.com/anthropics/claude-code/issues/11972`, `https://github.com/anthropics/claude-code/issues/1217`
- BLP-02 initiative trigger: 2026-05-02 Daniel Wood LinkedIn thread (web archive snapshot referenced in F-3 ADR-less PRD and F-2 ADR-040 §Discovery context).
- Companion Wave-4 ADR-less feature for context: [F-3 PRD #272](../../product/02_PRD/272-security-md-and-private-disclosure-channel-2026-05-07.md) (closed 2026-05-08; SECURITY.md + GitHub Private Disclosure toggle).
