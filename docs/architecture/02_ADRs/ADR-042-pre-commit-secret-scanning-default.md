# ADR-042: Pre-commit Secret-Scanning Default — gitleaks-via-pre-commit + Wrapper-Augmented Refusal Contract + CI Parity Back-stop

**Status**: Proposed
**Date**: Proposed: 2026-05-10 (PRD v1.0 Approved); to be Accepted at squash-merge of feature 282 per /aod.deliver T034.
**Deciders**: PM (APPROVED 2026-05-10), Architect (APPROVED 2026-05-10), Team-Lead (APPROVED_WITH_CONCERNS 2026-05-10).
**Feature**: [282-pre-commit-secret-scanning-defaults](../../../specs/282-pre-commit-secret-scanning-defaults/spec.md)
**Initiative**: BLP-02 Wave 4+ (enterprise hardening — fifth and final feature in the 5-feature initiative; closes the 2026-05-02 Daniel Wood LinkedIn-thread enterprise-hardening rubric alongside F-2 / F-3 / F-4).
**Supersedes**: None
**Superseded by**: None
**Related ADRs**: [ADR-038](ADR-038-template-substitute-rewrite.md) (substitution model precedent for raw `read -p` waiver — see Decision Item 4); [ADR-040](ADR-040-config-file-parsing-hardening.md) (F-2 hardened config-file load; shared Wood-thread origin); [ADR-041](ADR-041-claude-permissions-baseline.md) (F-4 Claude Code permissions baseline; companion BLP-02 Wave-4 ADR; ADR-042 is its secret-scanning sibling).

---

## Context

Tachi's pre-F-5 commit surface had no automated credential-scanning gate. A maintainer or first-time contributor could stage a real GitHub Personal Access Token, AWS access key, OpenAI/Anthropic API key, RSA private key block, or Stripe live-mode key and complete `git commit` without any tooling intervention. The only back-stop was reviewer attention at PR time, which fails on solo work, late-night commits, automated tooling commits, and first-time contributor PRs from forks where reviewers have not yet established context. The PRD enumerated six concrete deficits: (1) **no automated commit-time gate** — credentials reach `origin` before any human review; (2) **no allow-list discipline** — even if a scanner were added ad-hoc, every documentation-placeholder credit would refuse the commit absent careful allow-list curation; (3) **no error-message contract** — generic gitleaks output does not tell a first-time contributor how to bypass for a known-good case; (4) **no CI back-stop** — `git commit --no-verify` is one flag; without a CI re-scan, the bypass succeeds silently; (5) **no opt-in posture for existing adopters** — auto-installing on `git pull` would surprise existing adopters mid-workflow; (6) **no per-rule rationale documentation** — SecOps reviewers have no audit-defensible artifact when asked "why this rule?"

The six gaps share a common root: tachi shipped the architecture description harness without shipping the secret-scanning gate that the harness itself recommends to adopters. The 2026-05-02 Daniel Wood LinkedIn thread named the resulting posture as a load-bearing gap for enterprise-developer adoption alongside F-2 (config-file parsing), F-3 (private disclosure), and F-4 (Claude Code permissions baseline). Closing the gap means shipping a default-secure scanner, an honest-disclosure error-message contract, an opt-out path that preserves adopter agency, a CI parity back-stop for `--no-verify` bypass, and an audit-defensible rationale catalog. F-5 is configuration files (`.gitleaks.toml`, `.pre-commit-config.yaml`) + a wrapper script + a CI workflow + the operator handbook (`docs/standards/PRECOMMIT_HOOKS.md`) + this ADR. Same shape as F-4 (documentation + settings + ADR) plus a synthetic-fixture rule-interaction test (`tests/fixtures/gitleaks-rule-interaction/`, 16 fixtures) added preventively per Architect C-4.

---

## Decision

We will ship a default-secure pre-commit secret-scanning hook using **gitleaks** as the scanner, invoked via the pre-commit framework, with a tachi-authored wrapper script that augments the refused-commit stderr to a four-item structured contract. Adopter-facing surfaces are governed by a self-contained operator handbook (`docs/standards/PRECOMMIT_HOOKS.md`) and this ADR. The seven decision items below are reciprocally documented in `PRECOMMIT_HOOKS.md` (the operator-facing surface) and `spec.md` FR-001..FR-015 (the behavior contract).

### Decision Item 1 — gitleaks (Go binary) as the scanner

The scanner is gitleaks v8.30.1+ (single-binary Go runtime, MIT-licensed, github.com/gitleaks/gitleaks). The selection is the result of a 9-alternative comparison (§Alternatives-Considered) on five axes: ruleset breadth, license posture, supply-chain auditability, ecosystem presence, and CI cost.

gitleaks wins on all five axes for tachi's adoption profile: ~150+ default credential patterns covering AWS / GitHub / OpenAI / Anthropic / Stripe / private keys; permissive MIT license; single-binary installation verifiable by upstream-published SHA256 checksum; pre-commit framework hook is canonical (gitleaks.com lists pre-commit as the primary local-hook integration); zero per-org licensing cost when the binary is invoked directly (the proprietary `gitleaks-action@v2` GitHub Action requires a paid `GITLEAKS_LICENSE` for org repos, which we avoid by downloading the binary directly in the CI workflow).

### Decision Item 2 — Pre-commit framework as the local-hook orchestrator

The hook is wired via `.pre-commit-config.yaml` at the repo root. The framework (`pre-commit`, by github.com/pre-commit/pre-commit) handles the `.git/hooks/pre-commit` shim, the `SKIP=` env-var bypass, the `# gitleaks:allow` inline comment honoring, and the per-hook stage selection. Tachi does not author its own pre-commit shim — the framework is upstream-canonical and the contract is well-documented for SecOps reviewers.

The framework's minimum supported version is **v3.5.0** (per Architect CONCERN-3): below this version, `.pre-commit-config.yaml` schema features used in tachi's config (notably the `repos[].rev` SHA-pin pattern produced by `pre-commit autoupdate --freeze`) may silently partial-install or runtime-crash on first invocation. `scripts/init.sh` checks the system `pre-commit --version` at install time and emits a `WARN` (not an abort) if the version is below the floor. The framework version floor is documented in `PRECOMMIT_HOOKS.md` §8.7 with explicit justification.

### Decision Item 3 — Wrapper script for refused-commit error-message contract (LOCAL-ONLY)

`.aod/scripts/bash/precommit-wrap.sh` (~50 LOC, bash 3.2 compatible) wraps the gitleaks invocation to augment the refused-commit stderr with a four-item structured contract (rule ID, file:line, `SKIP=gitleaks` bypass, docs link). Items (a) and (b) come from gitleaks default output; the wrapper adds (c) and (d). The wrapper preserves gitleaks' exit code verbatim — Pre-Mortem FM-5 pattern: capture rc BEFORE the augmentation block so a failure inside augmentation cannot mask the underlying gitleaks rc that reaches the pre-commit framework. Reference: `.aod/scripts/bash/init-input.sh` (rejection-ladder precedent).

The wrapper is **LOCAL-ONLY**. The CI parity workflow (`.github/workflows/gitleaks.yml`) invokes the gitleaks binary directly, NOT through the wrapper, to preserve native SARIF output for GitHub Code Scanning compatibility. PM-5 / Pre-Mortem FM-2 mandate this scope clarity: the wrapper exists to humanize commit-time error messages for first-time contributors; CI emits machine-readable SARIF for tooling consumption, which is a different output contract.

### Decision Item 4 — Raw `read -p` waiver for the init.sh prompt (per Q10)

`scripts/init.sh` prompts for hook installation with default `Y` in TTY contexts. The prompt uses raw `read -p` rather than the F-1 `aod_init_read_validated` library function. The waiver is justified because the install prompt is **boolean** (Y/n) — none of the metacharacter rejections (`$`, `\`, backtick) that `aod_init_read_validated` was authored to handle apply. Adding a wrapper invocation would inflate the F-5 surface without proportional safety value. The waiver is documented here as a one-time exemption; future bash input prompts in init.sh that accept free-form values MUST continue to use `aod_init_read_validated` per ADR-038 substitution model precedent.

### Decision Item 5 — Opt-in posture for existing adopters (FR-010)

The F-5 update does NOT auto-install `.git/hooks/pre-commit` on `git pull` for existing adopters. The CHANGELOG entry and `README.md` Security pointer document the one-line opt-in command (`pre-commit install`). New adopters via `scripts/init.sh` get the default-Y prompt at first-run. This split posture (default-secure for new adopters; opt-in for existing) preserves adopter agency: a maintainer who has already established a workflow does not get a surprise hook on `git pull`. The trade-off is that a fraction of existing adopters will skip the opt-in and the gap will remain open for them — accepted because the alternative (auto-install on pull) would violate the surprise-quotient principle that BLP-02 Wave 4 carries forward from F-3 / F-4.

### Decision Item 6 — Pin-bump cadence policy (per Architect A-2)

The gitleaks `rev` in `.pre-commit-config.yaml` starts as a tag (`v8.30.1`) for human readability and is replaced with a pinned commit SHA via `pre-commit autoupdate --freeze` at install time. The pin lifts on each gitleaks **minor** release with empirical re-test against `tests/fixtures/gitleaks-rule-interaction/` (the 16-fixture interaction matrix from FR-013) BEFORE merging the bump. Patch releases bump opportunistically on confirmed CVE / regression fixes. Major releases trigger ADR re-evaluation (the gitleaks v8 → v9 boundary in particular: schema changes like the `[allowlist]` → `[[allowlists]]` v8.25.0 transition are exactly the kind of break the synthetic-fixture re-test guards against).

Owner accountability for the pin-bump cadence lives in the BLP-02 closure memo as a recurring maintenance commitment — Architect CONCERN-4 (post-merge follow-up Issue T033) tracks the accountability surface explicitly.

### Decision Item 7 — Synthetic-fixture rule-interaction test as preventive false-positive verification (Architect C-4)

`tests/fixtures/gitleaks-rule-interaction/` ships 16 synthetic fixtures: 6 should-fire (real-format credentials) + 10 should-NOT-fire (placeholder values, allow-listed paths, excluded paths). The runner (`bash run.sh`) executes `gitleaks` against each fixture and verifies the expected outcome. The test is co-located with the fixtures (Architect CONCERN-1) and lock-step with the `tachi-pytest.yml` CI workflow (Architect CONCERN-2 / F-256 lock-step pattern via `tests/scripts/test_init_precommit_matrix.py`).

The test is preventive false-positive verification: it catches schema breaks at pin-bump time (§Decision Item 6) and catches accidental allow-list misconfigurations on adopter-driven `.gitleaks.toml` modifications. Without it, the first signal of a regression would be a refused-commit on a documentation placeholder — exactly the false-positive flood that Risk R-1 was authored to prevent.

---

## Alternatives Considered

### Alternative 1: trufflehog (Go binary)

**Pros**:
- Stronger entropy-based credential detection (claims higher recall on novel credential formats).
- Active development at github.com/trufflesecurity/trufflehog; trufflehog v3 is the modern incarnation.
- Native git-history scanning (full-repo + commit-by-commit walk) is first-class.

**Cons**:
- Slower than gitleaks at staged-content scope (entropy scoring on every line vs. gitleaks' regex-first approach with optional entropy gate).
- Smaller ecosystem of pre-existing pre-commit hook integrations; the trufflehog pre-commit recipe is community-maintained, not upstream-canonical.
- Harder allow-list authoring — trufflehog v3 uses verifiers + detectors (Go code), not a TOML allow-list. Adopter customization (PRECOMMIT_HOOKS.md §9.1) requires Go programming, raising the bar for customization.

**Why Not Chosen**: gitleaks' TOML allow-list authoring is the load-bearing adopter-customization surface; requiring adopters to write Go verifiers to add a single pattern fails the "low bar to opt-in" principle. **PRD comparison-matrix correction**: the PRD initially listed trufflehog runtime as Python (carry-forward from an outdated 2018-era trufflehog v2). **Trufflehog v3 runtime is Go**, same as gitleaks — so the runtime-difference axis does not differentiate. The decisive axis is allow-list ergonomics, not language runtime.

### Alternative 2: detect-secrets (Yelp, Python)

**Pros**:
- Long-standing reference implementation (Yelp's tooling, github.com/Yelp/detect-secrets); battle-tested at large-org scale.
- `.secrets.baseline` model is well-suited to incremental adoption: scan once, freeze a baseline, only flag NEW secrets after that. Reduces false-positive flood on legacy codebases.
- Pure Python — installs via `pip install detect-secrets`, no binary distribution to verify.

**Cons**:
- Smaller default ruleset than gitleaks (~30 plugin types vs. gitleaks' ~150+ patterns). Adopters add custom regexes to compensate.
- The `.secrets.baseline` model creates a checked-in snapshot that drifts; tachi prefers stateless rule definitions in `.gitleaks.toml`.
- Pure-Python runtime means startup latency (python interpreter cold-start on every commit). gitleaks' single-binary startup is sub-100ms.

**Why Not Chosen**: detect-secrets is well-suited to organizations adopting secret-scanning on a legacy codebase with a long credential-littered history. Tachi's adopters start with a clean tree (init.sh produces a minimal personalized clone), so the baseline-drift model is more friction than benefit. The smaller default ruleset would force more adopter-side rule authoring than gitleaks' useDefault inheritance.

### Alternative 3: GitHub native push-protection

**Pros**:
- Zero local install surface — push-protection is a GitHub-side feature toggled per-repo in Settings.
- Catches secrets at push time even without any local hook. Strongest "defense at the perimeter" posture.
- Maintained by GitHub; supply-chain trust is inherited from the platform.

**Cons**:
- Push-time only — secrets are already in local history when push-protection rejects. Cleanup (force-push of rewritten history, rotation of leaked credential) is mandatory.
- Coverage limited to GitHub's secret-types catalog; tachi-specific patterns (`AOD_PERSONALIZATION_*`, `.security/exceptions.jsonl`) are not covered.
- Push-protection is a settings-page toggle, not a checked-in artifact; SecOps reviewers cannot audit tachi's posture by reading the repo. Adopter-fork variance is invisible.

**Why Not Chosen**: push-protection is an excellent **complement** to a local hook (defense-in-depth), but a poor **replacement**. F-5 ships the local hook + CI parity workflow; adopters who additionally enable push-protection get a third defensive layer. The CHANGELOG note recommends push-protection as a complementary control.

### Alternative 4: Custom regex-only hook (no framework, no scanner)

**Pros**:
- Smallest possible dependency surface — just a bash script in `.git/hooks/pre-commit` invoking `grep -E` against staged content.
- Full control over false-positive calibration; no third-party heuristics.
- Zero supply-chain risk beyond bash itself.

**Cons**:
- Maintaining a custom regex catalog at parity with gitleaks' ~150+ patterns is full-time work — adopting a maintained scanner is the entire point of not authoring this in-house.
- No allow-list semantics, no entropy gating, no rule tagging — features adopters increasingly expect from a 2026-era scanner.
- Would force tachi maintainers into the "maintaining a credential-scanning ruleset" business, distracting from the actual product (architecture-description threat modeling).

**Why Not Chosen**: NIH (not-invented-here) on the credential-scanning surface where the upstream tooling is mature, well-maintained, and ecosystem-integrated.

### Alternative 5: Opt-out flag in init.sh (default-N) instead of default-Y

**Pros**:
- Maximum adopter agency — they make the explicit choice to opt in.
- Zero surprise quotient for adopters who skim init.sh and press Enter through every prompt.
- Lower risk of installer-perceived intrusion ("why is the project installing hooks I didn't ask for?").

**Cons**:
- Default-N undermines the BLP-02 enterprise-hardening goal: most adopters press Enter through prompts, so default-N effectively means "no scanner for the default adopter." The gap re-opens for the majority.
- "Default-secure beats default-permissive-with-opt-in" is the established BLP-02 pattern (F-4 ships the permissions baseline as the default; adopters fork-and-edit to opt out). Inverting the default for F-5 only would be inconsistent.
- Existing adopters are already opt-in (FR-010); making new adopters also opt-in means almost nobody gets the scanner.

**Why Not Chosen**: default-secure is the BLP-02 carry-forward principle. New adopters get the prompt with default-Y; pressing Enter accepts. Skipping is one keystroke (`n`) — opt-out cost is comparable to default-N's opt-in cost.

### Alternative 6: Tier the hooks (e.g., separate "essential" vs. "extended" rule sets)

**Pros**:
- Calibrates false-positive risk per-tier. Essential = high-confidence patterns (AWS / GitHub / OpenAI keys); extended = entropy-based generic-secret heuristics.
- Adopters can run essential-only on a high-throughput repo and extended on a low-throughput repo.

**Cons**:
- Tier authoring is itself maintenance burden — every new pattern needs a tier classification, and adopters' opinions on what should be "essential" vs. "extended" diverge.
- gitleaks' default ruleset is already calibrated by the upstream maintainers; second-guessing their calibration adds variance without clear value.
- Two tiers fragment the audit surface (SecOps reviewers must reason about which tier is active).

**Why Not Chosen**: a single default ruleset (gitleaks `useDefault = true`) plus tachi-additive allow-lists is simpler, audit-defensible, and inherits upstream calibration.

### Alternative 7: GitGuardian (commercial SaaS scanner)

**Pros**:
- Best-in-class detection (commercial product backed by dedicated security research team).
- Cross-repo dashboarding, organizational-policy enforcement, automated key-revocation integrations.
- Mature support for incident response (alert routing, severity tiers, escalation paths).

**Cons**:
- Requires paid subscription per developer/org — the open-source consumption model F-5 targets is incompatible with commercial-SaaS gating.
- Centralized dashboarding means tachi adopters must surface their internal repo content to GitGuardian's SaaS — a privacy/compliance posture many adopters cannot accept.
- Tachi's value proposition is local-first / no-telemetry (per `.claude/rules/scope.md`); shipping a SaaS-dependent default contradicts the project's core posture.

**Why Not Chosen**: wrong consumption model. GitGuardian is excellent for organizations adopting tachi internally and adding GitGuardian as a separate enterprise tool; tachi-the-default-shipped-scanner must be open-source, local-first, and free.

### Alternative 8: SecretLint (Node.js / pluggable rules)

**Pros**:
- Pluggable rule architecture — adopters install only the rules they want via npm packages.
- Strong JavaScript/TypeScript ecosystem integration; aligned with adopters whose toolchain is Node-centric.

**Cons**:
- Node.js runtime dependency excludes adopters whose tachi consumption is purely Python / Go / Rust — a substantial fraction.
- Smaller default rule catalog than gitleaks; adopters must compose multiple plugins to reach gitleaks-equivalent coverage.
- pre-commit framework support is community-maintained, not upstream-canonical.

**Why Not Chosen**: runtime-stack alignment with Node is too narrow for tachi's adopter profile. gitleaks' single-binary distribution is runtime-agnostic.

### Alternative 9: git-secrets (AWS Labs, bash)

**Pros**:
- Zero runtime dependency beyond bash — installs as a single shell script.
- AWS Labs provenance; long-running project (since 2015).
- Tight focus on AWS-specific patterns (the original use case).

**Cons**:
- Maintenance has slowed since 2020; rule catalog has not kept pace with the 2020-2026 explosion in API-key formats (LLM provider keys, modern OAuth-style PATs, Stripe live-mode key rotation).
- Bash-only allow-list authoring is brittle — the regex composition syntax is hard to author and audit.
- No SARIF output, no entropy gating, no integration with GitHub Code Scanning.

**Why Not Chosen**: maintenance staleness is the deciding factor. git-secrets was the right answer in 2018; gitleaks is the right answer in 2026.

---

## Consequences

### Positive

- **Default-secure commit gate** for new tachi adopters — the casual-typo case (committing a real credential by accident) is closed at first-run with a one-keystroke acceptance prompt.
- **Audit-defensible posture** for enterprise SecOps reviewers — `PRECOMMIT_HOOKS.md` §3 per-rule rationale catalog cross-checks one-to-one against `.gitleaks.toml` (AC-10 [MANUAL-ONLY] reviewer cross-check at /aod.deliver verifies parity).
- **CI parity back-stop** for `--no-verify` deliberate bypass — `.github/workflows/gitleaks.yml` re-runs gitleaks against full-repo content on every PR; SARIF upload surfaces findings inline on the GitHub PR Files-changed tab.
- **Honest disclosure** of bypass mechanisms (§4 of `PRECOMMIT_HOOKS.md`) — `--no-verify` is documented openly rather than papered over; the bypass + back-stop pair is the actual security model.
- **Adopter-customization preserved** — gitleaks TOML allow-list authoring is approachable; tool swap path (gitleaks ↔ trufflehog ↔ detect-secrets) preserves the four-item refused-commit contract via the wrapper script.
- **BLP-02 closure** — F-5 is the fifth and final feature in the BLP-02 enterprise-hardening initiative. Together with F-1 (init.sh substitution model), F-2 (config-file parsing hardening), F-3 (private disclosure channel), and F-4 (Claude Code permissions baseline), the initiative closes the 2026-05-02 Daniel Wood LinkedIn-thread enterprise-hardening rubric.

### Negative

- **Pre-commit framework adoption surface** — adopters who do not already have `pre-commit` installed must `pip install pre-commit` or `brew install pre-commit` before the local hook works. The `WARN` path in init.sh (Decision Item 2) lets the install proceed without aborting; recovery is one command. Documented in `PRECOMMIT_HOOKS.md` §2.3.
- **False-positive risk on adopter customization** — adopters who fork `.gitleaks.toml` to add internal-pattern rules without re-running the synthetic-fixture test (`tests/fixtures/gitleaks-rule-interaction/run.sh`) may introduce a rule that fires on legitimate fixture content. The synthetic-fixture suite is preventive (Architect C-4); adopters who skip it accept the risk.
- **Wrapper script LOCAL-ONLY scope split** — the local hook uses the wrapper for the four-item error contract; the CI workflow invokes gitleaks directly to preserve native SARIF. SecOps reviewers must understand the split: error-message formatting is local-only; CI emits machine-readable SARIF for tooling consumption. Documented in `PRECOMMIT_HOOKS.md` §5–§6 and PM-5 / Pre-Mortem FM-2.

### Mitigation

- The R-1 (false-positive flood), R-9 (`.gitleaks.toml` adopter-divergence on `make update`), and R-10 (pre-commit framework version drift) risks are **disclosed honestly** in `PRECOMMIT_HOOKS.md` §8 rather than papered over. The synthetic-fixture suite catches regressions on every pin bump (§Decision Item 6 cadence policy). The CI parity workflow back-stops `--no-verify` bypass at PR time. Post-merge `/security` re-scan (FR-014) is regression-only on the F-5 file surface — F-5 closes no `/security` finding directly because the gap was a posture-control absence, not a vuln pattern.

- **Pin-bump cadence policy**: each gitleaks minor release with empirical re-test against `tests/fixtures/gitleaks-rule-interaction/` BEFORE merging the bump. Patch releases bump opportunistically on confirmed CVE / regression fixes. Major releases trigger ADR re-evaluation (the gitleaks v8 → v9 boundary in particular: schema changes like the `[allowlist]` → `[[allowlists]]` v8.25.0 transition are exactly the kind of break the synthetic-fixture re-test guards against). Owner accountability for the cadence lives in the BLP-02 closure memo as a recurring maintenance commitment (Architect CONCERN-4 / T033 post-merge follow-up Issue).

---

## Related Findings

- **No `/security` finding directly closed** — F-5 is posture-control closure (a missing default), not vuln-closure. The post-merge `/security` re-scan (FR-014) is regression-only.
- **BLP-02 5/5 closure** — F-5 is the fifth and final feature in the BLP-02 initiative. The closure memo updates the BLP-02 project memory entry and the LinkedIn-thread accountability note (memory entry: `project_blp02_enterprise_hardening`).

---

## References

- Feature 282 PRD: [docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-10.md](../../product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-10.md)
- Feature 282 Spec: [specs/282-pre-commit-secret-scanning-defaults/spec.md](../../../specs/282-pre-commit-secret-scanning-defaults/spec.md) (FR-001..FR-015)
- Feature 282 Plan: [specs/282-pre-commit-secret-scanning-defaults/plan.md](../../../specs/282-pre-commit-secret-scanning-defaults/plan.md)
- Operator-facing handbook: [docs/standards/PRECOMMIT_HOOKS.md](../../standards/PRECOMMIT_HOOKS.md)
- Synthetic-fixture rule-interaction test: [tests/fixtures/gitleaks-rule-interaction/](../../../tests/fixtures/gitleaks-rule-interaction/)
- gitleaks upstream: `https://github.com/gitleaks/gitleaks`
- pre-commit framework upstream: `https://github.com/pre-commit/pre-commit`
- Companion BLP-02 Wave-4 ADR: [ADR-041](ADR-041-claude-permissions-baseline.md) (F-4 Claude Code permissions baseline; same Wood-thread origin)
- BLP-02 Wave-3 sibling (no ADR): [F-3 PRD #272](../../product/02_PRD/272-security-md-and-private-disclosure-channel-2026-05-07.md) (SECURITY.md + GitHub Private Disclosure)
- BLP-02 initiative trigger: 2026-05-02 Daniel Wood LinkedIn thread (web archive snapshot referenced in F-3 ADR-less PRD and F-2 ADR-040 §Discovery context).
