# tachi Security Posture — 2026Q2 Hardening Cycle

**Assessment Window**: 2026-05-02 → 2026-05-10
**Audit-Eligible State**: post-`v4.35.0`
**Document Author**: tachi maintainers
**Last Updated**: 2026-05-10

---

## Audience

This document serves three readers:

- **Adopter SecOps reviewer** evaluating tachi as a security-aware AI-coding harness for a managed environment.
- **Procurement reviewer** requesting evidence of recent posture work for vendor due diligence.
- **Future contributor** needing context on what was hardened in 2026Q2 and why.

Every claim below links to a public artifact (ADR, PR, file, or docs page) on this repository. No private context is required to validate any claim.

---

## Executive summary

Between 2026-05-02 and 2026-05-10, tachi shipped a five-feature enterprise hardening cycle that:

- **Closed 11 internal `/security` findings** against the substitution, config-loading, and disclosure surfaces (zero CRITICAL, three HIGH, four MEDIUM, three LOW, one INFO).
- **Closed 3 external-community-review checklist items** named in a public 2026-05-02 review: private vulnerability disclosure channel, Claude Code permission baseline, and pre-commit secret-scanning.
- **Released as `v4.28.0` → `v4.35.0`** across multiple `release-please` cycles (including one operational hot-fix at `v4.28.1`).

The cycle did not increase tachi's command surface and did not change its operational mode. All changes are posture-defensive: harder substitution semantics, stricter config parsing, a documented private disclosure channel, a self-contained Claude Code permission baseline, and an opt-in pre-commit secret-scanning hook.

Public Architecture Decision Records governing the cycle: **ADR-038**, **ADR-040**, **ADR-041**, **ADR-042**. (ADR-039 is operational test architecture, not part of the posture cycle.)

---

## Per-feature posture map

The cycle organized work into five sub-features (F-1 through F-5). Each row below is procurement-defensible: rationale, controls, and remediation are all in the public artifacts cited.

### F-1 — Substitution Surface Hardening

**ADR**: [ADR-038](../architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md)
**Release**: `v4.28.0` (PR [#249](https://github.com/davidmatousek/tachi/pull/249))
**Hot-fix follow-on**: `v4.28.1` (operational test-architecture stabilization, PR [#253](https://github.com/davidmatousek/tachi/pull/253))

**Posture change**: replaced `sed`-based substitution in [scripts/init.sh](../../scripts/init.sh) with a Bash-3.2-compatible string-replacement primitive. Eliminated the multi-hop execution chain pattern in which adversarially-crafted project paths could influence subsequent shell invocations. Tightened `PROJECT_PATH` validation, `read -p` input handling, personalization gitignore semantics, and constitution path migration.

**Adopter-visible change**: `scripts/init.sh` now refuses paths containing characters that would alter substitution semantics. No legitimate adopter path is rejected.

**Findings closed**: 5 (sed swap, `PROJECT_PATH` disposition, `read -p` validation, personalization gitignore, constitution sed migration).

---

### F-2 — Source-Pattern Hardening

**ADR**: [ADR-040](../architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md)
**Release**: bundled into the `v4.29.0`+ release cadence (PR [#257](https://github.com/davidmatousek/tachi/pull/257))

**Posture change**: introduced a canonical KV-load primitive `aod_template_load_kv_file` in [.aod/scripts/bash/template-config-load.sh](../../.aod/scripts/bash/template-config-load.sh). The primitive uses a read-buffer → strict-KV-regex → `printf -v` pattern, replacing four legacy `source` and `eval` call sites. New environment variable `AOD_FETCH_TIMEOUT` (default `60s`) bounds remote fetches. Adds a follow-on file-size cap and regular-file check on the KV loader.

**Adopter-visible change**: malformed or oversized config files now fail loudly at load time instead of silently injecting unintended shell semantics.

**Findings closed**: 5 (`defaults.env` source, `aod-kit-version` source, `eval` call, TOCTOU on config read, clone timeout).

---

### F-3 — SECURITY.md and Private Disclosure Channel

**Public docs**: [SECURITY.md](../../SECURITY.md), [README.md `## Community`](../../README.md)
**Release**: `v4.33.0` (PR [#273](https://github.com/davidmatousek/tachi/pull/273))

**Posture change**: rewrote [SECURITY.md](../../SECURITY.md) to the GitHub-canonical five-section structure (Supported Versions / Reporting a Vulnerability / What to expect / Scope / Out-of-scope) and enabled GitHub **Private Vulnerability Reporting** on the repository. Researchers can now coordinate disclosure through the upstream GitHub flow without relying on email triage.

**Adopter-visible change**: a documented disclosure channel is in place. Verified continuously via the dedicated GitHub API endpoint.

**Findings closed**: 1 (`A05:2021 Security Misconfiguration` — missing private disclosure channel).

**Governance**: F-3 is a documentation-only change; per the project Constitution Principle VII §Exceptions, no automated test coverage was added. Verification is via post-merge `/security` re-scan + manual UI inspections.

---

### F-4 — Claude Code Permission Baseline

**ADR**: [ADR-041](../architecture/02_ADRs/ADR-041-claude-permissions-baseline.md)
**Public docs**: [docs/standards/CLAUDE_PERMISSIONS.md](../standards/CLAUDE_PERMISSIONS.md)
**Configuration**: [.claude/settings.json](../../.claude/settings.json)
**Release**: `v4.34.0` (PR [#278](https://github.com/davidmatousek/tachi/pull/278))

**Posture change**: introduced a curated `~80 LOC` [.claude/settings.json](../../.claude/settings.json) baseline organized into four categories — read-only auto-approve, local-state auto-approve, destructive deny + ask, and network host-allowlist. The companion [CLAUDE_PERMISSIONS.md](../standards/CLAUDE_PERMISSIONS.md) is **self-contained** (`~250 LOC`): a SecOps reviewer can read it end-to-end and produce an audit report without reverse-engineering rule names or maintainer intent. Per-rule rationale is one-to-one cross-checked against `settings.json` via the AC-2 verification recipe (FR-002).

The baseline includes a 19-domain WebFetch host-allowlist spanning the GitHub, Anthropic, OWASP, MITRE, and NIST families, each domain motivated by a documented network dependency.

**Adopter-visible change**: SecOps-reviewed managed environments can ship the baseline as-is and audit it against this document. Three documented opt-out paths (per-tool CLI flag / fork-and-edit / managed-settings layer) cover legitimate override scenarios.

**Findings closed**: 0 vulnerability IDs (this is posture-gap closure, not vulnerability remediation), but addresses the second item on the public 2026-05-02 community review checklist.

**Calibration trade-offs** documented in CLAUDE_PERMISSIONS.md §Known-Limitations:
- `Bash(rm -rf:*)` matches literal command-line strings; `bash -c 'rm -rf …'` does not match. Calibration: **deny rules are casual-typo, not adversarial**. Adversarial bypass surface is out-of-scope and addressed via PreToolUse hooks (defense-in-depth) per ADR-041.
- Process wrappers (`npx`, `docker exec`, `devbox run`, `mise exec`, `direnv exec`) re-shell-out commands and similarly bypass the deny tier. Same calibration applies.
- Subdomain matching is **not transitive** (Claude Code Issues [#15260](https://github.com/anthropics/claude-code/issues/15260), [#11972](https://github.com/anthropics/claude-code/issues/11972), [#1217](https://github.com/anthropics/claude-code/issues/1217)). The 19-domain explicit list is the correct posture given upstream behavior.

---

### F-5 — Pre-commit Secret-Scanning Defaults

**ADR**: [ADR-042](../architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md)
**Public docs**: [docs/standards/PRECOMMIT_HOOKS.md](../standards/PRECOMMIT_HOOKS.md)
**Configuration**: [.pre-commit-config.yaml](../../.pre-commit-config.yaml), [.gitleaks.toml](../../.gitleaks.toml)
**CI parity**: [.github/workflows/gitleaks.yml](../../.github/workflows/gitleaks.yml)
**Release**: `v4.35.0` (PR [#283](https://github.com/davidmatousek/tachi/pull/283))

**Posture change**: ships an opt-in pre-commit secret-scanning hook (gitleaks `v8.30.1` pinned). The hook runs through a stderr-augmenting wrapper at [.aod/scripts/bash/precommit-wrap.sh](../../.aod/scripts/bash/precommit-wrap.sh) that adds a four-item structured refusal contract (rule ID + file:line + bypass guidance + docs link). The CI parity workflow runs full-repo scans on PRs with binary-direct download and SHA256 verification — explicitly avoiding the proprietary gitleaks-action license trap. Both the local and CI variants emit SARIF for GitHub Code Scanning compatibility.

**Adopter-visible change**: at `init.sh` time, adopters are prompted (default Y in TTY contexts; skipped in non-TTY; flag overrides `--no-precommit` / `--precommit`) to install the pre-commit hook. Existing adopters can opt-in via `pre-commit install` after a `git pull`. There is no auto-install on `git pull`.

**Adopter extensibility**: the [.gitleaks.toml](../../.gitleaks.toml) configuration is tachi-tuned and can be extended by adopters. Two custom warn-only rules (`tachi-personalization-env`, `tachi-security-exceptions-jsonl`) document tachi-specific signal patterns.

**Findings closed**: 0 vulnerability IDs (posture-gap closure for the third community review item).

**Maintenance cadence**: each gitleaks minor release triggers a child Issue under follow-on-282 with empirical re-test against fixtures at [tests/fixtures/gitleaks-rule-interaction/](../../tests/fixtures/gitleaks-rule-interaction/).

---

## Adopter action checklist

If you are deploying tachi into a managed environment, the following checklist captures the procurement-defensible verifications you can run today:

- [ ] **Substitution surface**: read [scripts/init.sh](../../scripts/init.sh) and confirm the F-1 substitution primitive matches your shell-injection threat model. Run `bash scripts/init.sh --help` to see the supported invocation flags.
- [ ] **Config loader**: read [.aod/scripts/bash/template-config-load.sh](../../.aod/scripts/bash/template-config-load.sh) for the F-2 KV-load primitive. Confirm `AOD_FETCH_TIMEOUT` default of `60s` matches your operational tolerance.
- [ ] **Disclosure channel**: confirm the GitHub Private Vulnerability Reporting toggle is enabled on your fork via `gh api repos/<owner>/<fork>/private-vulnerability-reporting`. Expected response: `{"enabled":true}`.
- [ ] **Claude Code permissions**: read [docs/standards/CLAUDE_PERMISSIONS.md](../standards/CLAUDE_PERMISSIONS.md) end-to-end and decide whether the baseline matches your audit-policy requirements. The four-category framing maps cleanly to typical SecOps review questions.
- [ ] **Pre-commit secret-scanning**: from your fork, run `pre-commit install` and validate the hook fires on a deliberately-injected secret. Read [docs/standards/PRECOMMIT_HOOKS.md](../standards/PRECOMMIT_HOOKS.md) for the bypass contract.
- [ ] **CI parity**: confirm `.github/workflows/gitleaks.yml` is in your fork and that PRs trigger the workflow. Verify SARIF artifacts upload to GitHub Code Scanning.
- [ ] **Re-scan**: from a fresh clone of the cycle-closing tag (`v4.35.0`), run the project's `/security` scan and compare against the public ADR-cited baseline. Zero new findings expected on the F-1 → F-5 surfaces.

---

## Known limitations & calibration trade-offs

The cycle accepts the following calibration trade-offs explicitly, in line with each cited ADR's Decision section:

- **Adversarial bypass is out of scope.** Deny rules in F-4's permission baseline are calibrated against the casual-typo case. Adversarial bypass paths (`bash -c`, process wrappers) are documented and remediated via defense-in-depth (PreToolUse hooks) outside the F-4 surface.
- **Subdomain matching is not transitive.** F-4's 19-domain WebFetch list is the correct posture given upstream Claude Code semantics. Compaction options are tracked separately and gated on upstream behavior change.
- **Pre-commit hooks are opt-in.** F-5 does not auto-install on `git pull`. Adopters with airgapped or restricted-network developer environments can decline the hook without losing other tachi capabilities.
- **The internal /security tool is logic-level.** F-1 through F-5 close logic-level findings; they do not replace SAST, SCA, or secrets-only scanners. tachi's complementary positioning is documented in [.claude/rules/scope.md](../../.claude/rules/scope.md).

---

## Out-of-scope (deferred to future cycles)

The following items were deliberately out of scope for the 2026Q2 cycle and are tracked separately:

- **Cryptographic signature verification of tachi releases.** Deferred pending procurement-driven trigger. Current SHA-pin tripwire in `.aod/aod-kit-version` is the documented sufficient defense against the actively-exploitable supply-chain threat surface. Sigstore / cosign / minisign infrastructure will be evaluated when an enterprise procurement signal warrants the multi-day investment.
- **Adversarial bypass remediation.** PreToolUse hook scaffolding is the documented defense-in-depth path; F-4 is the calibration baseline, not the adversarial layer.
- **Enterprise managed-settings.json packaging.** Rejected in ADR-041 §Alternatives-Considered #4 — tachi is a project-level open-source tool, and managed-settings packaging is an enterprise IT deployment artifact rather than an upstream concern.

---

## Re-assessment cadence

- **Every adopter `/aod.update` cycle**: re-read the §Built-in-Read-Only-Set maintenance note in [CLAUDE_PERMISSIONS.md](../standards/CLAUDE_PERMISSIONS.md) and verify against the latest Claude Code release.
- **Every gitleaks minor release**: re-test against [tests/fixtures/gitleaks-rule-interaction/](../../tests/fixtures/gitleaks-rule-interaction/) before bumping the pin in [.pre-commit-config.yaml](../../.pre-commit-config.yaml). Cadence accountability is tracked under Issue [#287](https://github.com/davidmatousek/tachi/issues/287).
- **Every quarter**: re-scan the F-1 → F-5 surfaces with the project's `/security` tool and confirm zero regression. The next quarterly review is documented in this folder as `SECURITY_POSTURE_<YYYY>Q<N>.md`.

---

## Cross-references

| Public artifact | Purpose |
|---|---|
| [SECURITY.md](../../SECURITY.md) | Disclosure channel + supported versions (F-3) |
| [docs/standards/CLAUDE_PERMISSIONS.md](../standards/CLAUDE_PERMISSIONS.md) | Per-rule rationale + four-category framing (F-4) |
| [docs/standards/PRECOMMIT_HOOKS.md](../standards/PRECOMMIT_HOOKS.md) | Operator handbook for the pre-commit hook (F-5) |
| [docs/architecture/02_ADRs/ADR-038-…](../architecture/02_ADRs/) | F-1 substitution decision |
| [docs/architecture/02_ADRs/ADR-040-…](../architecture/02_ADRs/) | F-2 config-parsing decision |
| [docs/architecture/02_ADRs/ADR-041-…](../architecture/02_ADRs/) | F-4 permissions decision |
| [docs/architecture/02_ADRs/ADR-042-…](../architecture/02_ADRs/) | F-5 secret-scanning decision |
| [.claude/rules/scope.md](../../.claude/rules/scope.md) | tachi's complementary scanning-column positioning |
| [CHANGELOG.md](../../CHANGELOG.md) | Release-level change history (`v4.28.0` through `v4.35.0`) |

---

*This document is an as-of-`v4.35.0` snapshot. Future cycle posture documents follow the same template and live in this folder. For questions about adopter validation or to coordinate a vendor security review, please open a GitHub Issue or use the private disclosure channel documented in [SECURITY.md](../../SECURITY.md).*
