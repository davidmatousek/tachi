# Pre-commit Secret-Scanning Hooks

**Status**: Active (BLP-02 Wave 4+, F-5) | **Source of truth**: [`.pre-commit-config.yaml`](../../.pre-commit-config.yaml) + [`.gitleaks.toml`](../../.gitleaks.toml) | **Architecture decision**: [ADR-042](../architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md) | **Last updated**: 2026-05-10

---

## 1. Why this hook ships

Tachi's pre-F-5 commit surface had no automated credential-scanning gate: a maintainer or adopter could stage a real GitHub PAT, AWS access key, OpenAI key, or private key block and commit it without intervention. The only back-stop was reviewer attention at PR time, which fails on solo work, late-night commits, and first-time contributor PRs from forks. Public exposure of even a short-lived credential triggers immediate rotation cost, key-leak detection alerts on upstream services (GitHub, AWS, OpenAI all push automated revocation), and — for compliance-bound adopters — audit-log discovery obligations. The 2026-05-02 Daniel Wood LinkedIn thread named this gap as part of the BLP-02 enterprise-hardening rubric alongside F-2 (config-file parsing), F-3 (private disclosure), and F-4 (Claude Code permissions baseline). F-5 closes the gap with a default-secure pre-commit hook, an opt-out path that preserves adopter agency, and a CI parity workflow as a back-stop for `--no-verify` deliberate bypass.

The hook is **default-secure for new tachi adopters** (init.sh prompts at first-run with default `Y`) and **opt-in for existing adopters** (no auto-install on `git pull` per FR-010). Adopters who do not want the hook have three documented opt-out paths (§4). This document is **self-contained**: a SecOps reviewer auditing tachi's secret-scanning posture can read it end-to-end, cross-check the per-rule rationale catalog (§3) one-to-one against `.gitleaks.toml`, and produce an audit report without reverse-engineering rule names or maintainer intent.

---

## 2. Installation paths

The hook reaches an adopter's working tree via one of three paths. All three end in the same state: `.git/hooks/pre-commit` exists and runs the gitleaks wrapper on every `git commit`.

### Path 1 — First-time adopter via `scripts/init.sh` (default-Y prompt in TTY)

```text
$ scripts/init.sh
[init] Install pre-commit secret-scanning hook? [Y/n]: <Enter>
[init] Installing pre-commit hook...
[init] pre-commit installed at .git/hooks/pre-commit
```

`init.sh` prompts at the secret-scanning phase with default `Y`. Pressing `<Enter>` accepts the default; typing `n` skips. In non-TTY contexts (`</dev/null`, CI, scripted invocation), the prompt is skipped silently (no install). Two flag overrides bypass the prompt: `--precommit` forces install regardless of TTY/answer, `--no-precommit` forces skip. Both flags affect **first-run only** — see §7.

If `pre-commit` is not installed on the system, init.sh logs `WARN: pre-commit install failed; install pre-commit framework manually and run 'pre-commit install'` and continues (does NOT abort). The adopter follows Path 3 to recover.

### Path 2 — Existing adopter via `pre-commit install` after `git pull`

```bash
cd <your-tachi-clone>
git pull origin main             # F-5 update lands; .git/hooks/pre-commit unchanged
pre-commit install               # opts into the hook
```

The F-5 update is **opt-in** for existing adopters (FR-010): pulling the F-5 commit does NOT auto-install `.git/hooks/pre-commit`. The CHANGELOG entry and §6 of this document document the one-line opt-in command.

### Path 3 — Manual install on a system without pre-commit

If `pre-commit` is not yet installed system-wide:

```bash
pip install pre-commit           # or: brew install pre-commit
cd <your-tachi-clone>
pre-commit install
```

`pre-commit` is the upstream framework that runs `.pre-commit-config.yaml`. Tachi pins the gitleaks rev in `.pre-commit-config.yaml`; the framework itself is whatever version the adopter installs. **Minimum supported framework version: v3.5.0** — see §8.7.

---

## 3. What gets scanned

The hook runs `gitleaks git --pre-commit --redact --staged --verbose --config=.gitleaks.toml` against **staged content only** (not the working tree, not unstaged changes, not committed history). Staged-only scope is upstream gitleaks default behavior and is preserved verbatim by the wrapper script — see §5.

The ruleset is:

- **Upstream gitleaks default ruleset** (via `[extend] useDefault = true` in `.gitleaks.toml`): covers AWS access keys (`AKIA...`), GitHub PATs (`ghp_...`), OpenAI/Anthropic API keys (`sk-...`, `sk-ant-...`), generic high-entropy strings, RSA/SSH/PGP private key blocks, and ~150+ other credential patterns. The default ruleset is the canonical credential surface; tachi does not override or disable any default rule.
- **Three tachi allow-lists** (additive, scope down false-positives for tachi conventions): env-var placeholders, convention paths, vendored/generated/archived content.
- **Two tachi custom rules** (additive, both `warn-only`): `tachi-personalization-env` (defense-in-depth on `.aod/personalization.env` value leakage) and `tachi-security-exceptions-jsonl` (manual edits to auto-generated `.security/exceptions.jsonl`).

### Per-rule rationale catalog

Every additive entry in `.gitleaks.toml` appears below with its rationale. The catalog cross-checks one-to-one against `.gitleaks.toml` (AC-10 [MANUAL-ONLY] reviewer cross-check at /aod.deliver verifies catalog parity).

| `.gitleaks.toml` Entry | Type | Rationale |
|------------------------|------|-----------|
| `[extend] useDefault = true` | Default-ruleset import | Inherits upstream gitleaks credential patterns. Tachi adds — never overrides. |
| Allow-list 1 (`env-var placeholders and didactic stand-ins`) | Allow-list (regexes) | Suppresses default-rule firings on documentation/template content. Patterns: `$ENV_VAR` shell-style, `<placeholder>` angle-bracket, `PLACEHOLDER` literal, `your-api-key-here` tutorial, `sk-PLACEHOLDER...` OpenAI ellipsis, `sk-test-...` Stripe test-mode. Without this allow-list, every README code block with an `OPENAI_API_KEY=PLACEHOLDER` example would refuse the commit. |
| Allow-list 2 (`tachi convention paths where placeholder/fixture content lives`) | Allow-list (paths) | Paths where placeholder/fixture content lives intentionally. Covers `tests/fixtures/.*` (synthetic test fixtures including the F-5 rule-interaction set), `examples/.*` (adopter demo content), `docs/.*` (docs with placeholder values), `.aod/personalization.env.example` (the F-5 opt-in template). Suppresses false-positive flood (Risk R-1). |
| Allow-list 3 (`vendored, generated, or archived content not subject to scan`) | Allow-list (paths) | Trees not subject to scan — not authored content; may carry credentials from upstream sources we don't control. Covers `node_modules/.*`, `.git/.*`, `archive/.*`. |
| Custom rule `tachi-personalization-env` (warn-only) | Custom rule | Defense-in-depth: catches a copy of `.aod/personalization.env` content (populated, non-placeholder values) being committed somewhere outside the gitignored canonical path. `.aod/personalization.env` itself is in `.gitignore` (F-1 #248); this rule guards against accidental copies pasted into other locations. Tagged warn-only because the most likely false-positive is a legitimate `AOD_PERSONALIZATION_*` documentation reference. Tags: `warn-only`, `tachi-additive`. |
| Custom rule `tachi-security-exceptions-jsonl` (warn-only) | Custom rule | Defense-in-depth: `.security/exceptions.jsonl` is auto-generated by the tachi compensating-controls pipeline. Manual edits should be flagged for review (an entry without `"auto_generated":true` indicates a manual edit). Tagged warn-only because legitimate manual edits CAN occur (governance overrides). Tags: `warn-only`, `tachi-additive`. |

---

## 4. Bypass mechanisms

Four bypass paths cover the legitimate scenarios where a credential-shaped string is intentionally committed (placeholder fixtures, documentation, governance overrides) or the hook itself needs to be sidestepped.

### 4.1 `SKIP=gitleaks` — single-commit bypass (recommended)

```bash
SKIP=gitleaks git commit -m "docs: add OPENAI_API_KEY=sk-... example to tutorial"
```

The `SKIP` env var is honored by the pre-commit framework — only the named hook is skipped; other hooks still run. This is the recommended bypass for one-off commits where the maintainer has reviewed the staged content and confirmed the match is intentional (a placeholder value, a fixture file, a redacted log).

### 4.2 `# gitleaks:allow` — inline allow-list comment

```python
# gitleaks:allow
api_key = "sk-PLACEHOLDER1234567890abcdefghij"  # tutorial example
```

The `# gitleaks:allow` comment on the line preceding a credential-shaped string suppresses the match for that line only. Use sparingly — the comment lives in committed code permanently and is a long-term suppression rather than a one-time bypass.

### 4.3 `pre-commit uninstall` — full opt-out

```bash
pre-commit uninstall            # removes .git/hooks/pre-commit
```

Removes the hook from the working clone. Reinstall via `pre-commit install`. This is the post-init opt-out path — see §7 for the relationship to init.sh's `--no-precommit` / `--precommit` flags.

### 4.4 `git commit --no-verify` — honest disclosure

```bash
git commit --no-verify -m "..."  # bypasses ALL pre-commit hooks
```

`--no-verify` is a git-native flag that bypasses **all** pre-commit hooks, not just gitleaks. We disclose this honestly: a determined committer can sidestep the hook with one flag. Two reasons we do not pretend otherwise:

1. **Security by obscurity is anti-pattern**. Pretending `--no-verify` does not exist gives adopters false assurance.
2. **CI parity is the back-stop**. The `.github/workflows/gitleaks.yml` workflow re-runs gitleaks against full-repo content on every PR, so a `--no-verify` bypass at commit time still surfaces at PR time. See §6.

A maintainer who deliberately uses `--no-verify` and then deliberately bypasses the CI check is choosing to publish a credential — at that point the failure is policy / human, not tooling.

---

## 5. Refused-commit error message contract

When gitleaks finds a match, the wrapper script (`.aod/scripts/bash/precommit-wrap.sh`) augments the standard gitleaks output with a four-item structured stderr block (FR-008 contract):

```text
Finding:     ghp_REDACTED01234567890abcdefghijABCDEFGHIJ
Secret:      ghp_REDACTED01234567890abcdefghijABCDEFGHIJ
RuleID:      github-pat
Entropy:     4.5
File:        secrets.txt
Line:        1
Commit:      <staged>
Author:      <staged>
Email:       <staged>
Date:        <staged>
Fingerprint: secrets.txt:github-pat:1

──────────────────────────────────────────────────────────────
Commit refused: secret-scanning hook (gitleaks) found a match.

  Rule ID and file:line — see gitleaks output above.

  Bypass for a known-good case (e.g., a placeholder-only fixture):
      SKIP=gitleaks git commit ...

  Full bypass / opt-out / remediation guide:
      docs/standards/PRECOMMIT_HOOKS.md
──────────────────────────────────────────────────────────────
```

The four contract items are: **(a) rule ID** (`github-pat` above), **(b) file:line** (`secrets.txt:1`), **(c) `SKIP=gitleaks` bypass guidance**, **(d) docs link to this document**. Items (a) and (b) come from gitleaks default output; the wrapper adds (c) and (d). The wrapper preserves gitleaks' exit code verbatim — the augmentation block runs only on non-zero exit and never alters the rc that reaches the pre-commit framework (Pre-Mortem FM-5 pattern; reference `.aod/scripts/bash/init-input.sh` for the rejection-ladder precedent).

The wrapper is **LOCAL-ONLY**: the CI parity workflow (§6) invokes gitleaks directly, NOT through the wrapper, to preserve native SARIF output for GitHub Code Scanning compatibility.

---

## 6. CI parity

`.github/workflows/gitleaks.yml` runs gitleaks against **full-repo content** on every pull-request event as a back-stop for `--no-verify` deliberate bypass. The workflow:

1. Downloads the gitleaks v8.30.1 binary directly from the GitHub release tarball.
2. Verifies the binary against the upstream SHA256 checksum (`gitleaks_8.30.1_checksums.txt`).
3. Runs `gitleaks git --config=.gitleaks.toml --report-format sarif` against full history (`fetch-depth: 0`).
4. Uploads the SARIF report to GitHub Code Scanning via `github/codeql-action/upload-sarif@v3`. Findings appear inline on the PR Files-changed tab.

The workflow does NOT use the proprietary `gitleaks-action@v2` (which requires a paid `GITLEAKS_LICENSE` secret for org repos). Native binary invocation preserves SARIF compatibility, avoids the org-wide license trap, and keeps the supply chain auditable (one downloaded artifact verified by a published checksum).

**Scope difference from local hook**: the local hook scans **staged content only** at commit time; the CI workflow scans **full-repo history** at PR time. A pre-existing un-scanned credential in an older commit (predating F-5 adoption) would not trip the local hook on a fresh edit but would trip the CI workflow at next PR — by design (per Q5 resolution).

**Existing-adopter opt-in path**: existing adopters who pull the F-5 update do NOT auto-receive the local hook (FR-010). They DO receive the CI workflow (it lives in the repo, not the working clone). To enable the local hook, run `pre-commit install` from the repo root after `git pull`.

---

## 7. Re-init behavior

`scripts/init.sh` is a **first-run-only** template substitution script that self-deletes after successful execution (per F-1 #248). The init.sh prompt for the secret-scanning hook fires **once**, at first-run.

**Per PM-PLAN-2 carry-forward**: The `--no-precommit` and `--precommit` flags affect only the *first-run* init.sh invocation. To opt out post-init, run `pre-commit uninstall` from the repo root (§4.3). To opt back in post-init, run `pre-commit install`. The init.sh flags do not influence post-init state.

If init.sh is invoked a second time (e.g., re-cloned tree, accidental re-run), it hard-exits with the standard F-1 second-run error (`init.sh has already been executed; this is a one-shot script — see CHANGELOG.md for re-init semantics`). The pre-commit hook prompt does not re-fire.

---

## 8. Known limitations

The hook is calibrated against **the casual-typo case and the first-time-contributor case**, not adversarial bypass. The following limitations are disclosed honestly rather than papered over.

### 8.1 `git commit --no-verify` bypass

`--no-verify` is a one-flag git-native bypass for all pre-commit hooks. We disclose it in §4.4 because pretending otherwise gives false assurance. The CI parity workflow (§6) is the back-stop: a `--no-verify` bypass at commit time still surfaces as a CI failure at PR time. A committer who deliberately uses `--no-verify` AND deliberately ignores the CI check is choosing to publish — failure is policy, not tooling.

### 8.2 Pre-commit framework distribution risk

The `pre-commit` framework is a third-party Python package. Adopters install it via `pip install pre-commit` or `brew install pre-commit`; the framework itself is outside tachi's supply chain. A compromised upstream `pre-commit` package would compromise the hook's integrity. Mitigation: the framework is widely-used (12k+ GitHub stars, broad adoption), maintained at github.com/pre-commit/pre-commit, and pulled by name (PyPI) or formula (Homebrew) — both ecosystems carry their own integrity layers.

### 8.3 Custom rule limits

The two tachi-additive custom rules (`tachi-personalization-env`, `tachi-security-exceptions-jsonl`) are tagged `warn-only` because each has plausible legitimate firings (documentation references; governance overrides). `warn-only` is a tachi-internal convention — gitleaks itself treats all rules as blocking. The wrapper does NOT translate warn-only into non-blocking; a match in either custom rule still refuses the commit. Adopters who hit a legitimate firing should use `SKIP=gitleaks` (§4.1) per-commit OR add the path to allow-list 2 in `.gitleaks.toml`.

### 8.4 Staged-content-only scope

The hook scans **staged content only** at commit time. It does not scan the working tree, unstaged changes, committed history, or files outside `git status --porcelain` staged surface. A credential present in the working tree but not yet staged will NOT be caught by the hook. The CI parity workflow (§6) covers the full-repo history surface; for ad-hoc full-tree scans run `gitleaks dir --config=.gitleaks.toml .` manually.

### 8.5 Post-history-rewrite leaks

If a credential lands in a commit and is later removed via `git rebase -i` or `git filter-branch`, the rewritten history may still surface the credential in reflog or in remote-tracking branches that have not been force-pushed. The hook prevents commit-time leakage; it does NOT clean up post-leak history. Standard secret-rotation guidance applies: rotate the leaked credential immediately on upstream services regardless of history-rewrite outcome.

### 8.6 GitHub Actions secret-in-logs (out of scope)

Credentials accidentally echoed to GitHub Actions logs (e.g., `echo "$SECRET"` in a debug step, or a tool that prints the env var value on error) are out of F-5 scope. GitHub Actions has its own secret-redaction layer; tachi's hook does not extend to runtime log-scrubbing. CI workflow authors are responsible for not echoing secrets — see GitHub's [Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions) for the secret-redaction model.

### 8.7 Pre-commit framework version drift (Architect CONCERN-3)

**Minimum supported pre-commit framework version: v3.5.0.** Tachi's `.pre-commit-config.yaml` schema requires v3.5.0+ for stable hook resolution; below this version, hook installation may silently partial-install or runtime-crash on first invocation. `scripts/init.sh` checks the system `pre-commit --version` at install time and emits a `WARN` (not an abort) if the version is below the floor. Adopters who ignore the WARN proceed at their own risk. Bump cadence for the framework floor follows ADR-042 §Consequences: re-evaluated on each gitleaks minor release with empirical re-test against `tests/fixtures/gitleaks-rule-interaction/`.

---

## 9. Adopter customization

Tachi ships a default `.gitleaks.toml`; adopters may customize. The customization surface is wider than the F-4 permissions baseline because gitleaks rules are inherently context-specific (what is a placeholder in one project may be a real credential in another).

### 9.1 Per-rule additions

To add an adopter-specific rule (e.g., a custom internal-API-key pattern):

```toml
# Append to .gitleaks.toml
[[rules]]
id = "internal-api-key"
description = "Acme Corp internal API key (pre-prod tokens)"
regex = '''ACME_INTERNAL_[A-Z0-9]{32}'''
```

Adopter rules append after tachi's two custom rules (do NOT modify the upstream-default-import block at the top of `.gitleaks.toml`). To allow-list a specific path or pattern, append a new `[[allowlists]]` block.

### 9.2 Merge conflict guidance (Risk R-9)

On `make update` / `/aod.update`, an adopter who has customized `.gitleaks.toml` will see a merge conflict if tachi upstream has also modified the file (rare, but possible on gitleaks-pin bumps). Guidance:

1. Keep the upstream-default-import block (`[extend] useDefault = true`) as-is — it is the canonical credential surface.
2. Keep tachi's three allow-lists and two custom rules (the allow-list 2 path entries may have been updated; prefer upstream).
3. Re-apply adopter additions at the bottom of the file.
4. Re-run the synthetic-fixture test (`bash tests/fixtures/gitleaks-rule-interaction/run.sh`) to verify the merged file passes the 16-fixture interaction matrix.

### 9.3 Tool swap path (gitleaks ↔ trufflehog ↔ detect-secrets)

Adopters who prefer trufflehog or detect-secrets can swap the underlying scanner without abandoning the F-5 scaffolding:

1. Replace the `gitleaks` hook in `.pre-commit-config.yaml` with the upstream pre-commit hook for the chosen tool (trufflehog: `https://github.com/trufflesecurity/trufflehog`; detect-secrets: `https://github.com/Yelp/detect-secrets`).
2. Replace `.gitleaks.toml` with the chosen tool's config (trufflehog uses `.trufflehog.yaml`; detect-secrets uses `.secrets.baseline`).
3. Update `.aod/scripts/bash/precommit-wrap.sh` to call the chosen tool's CLI (the wrapper's exit-code-capture pattern is tool-agnostic).
4. Replace `.github/workflows/gitleaks.yml` with the equivalent CI workflow for the chosen tool.

The four-item refused-commit error contract (§5), the existing-adopter opt-in path (§2.2), and the bypass mechanisms (§4) are preserved across swaps because they live in the wrapper and the documentation, not in the scanner choice. ADR-042 §Alternatives-Considered enumerates the comparison matrix that drove the gitleaks default selection.

### 9.4 Directory rename considerations (Architect A-3)

If an adopter renames `tests/fixtures/`, `examples/`, `docs/`, or `.aod/` to a project-specific name, the path-based allow-lists (allow-list 2 and allow-list 3 in `.gitleaks.toml`) must be updated to match. Forgetting this step produces false positives on placeholder content under the renamed directory. The synthetic-fixture test (`tests/fixtures/gitleaks-rule-interaction/run.sh`) catches this at install time IF the test directory itself is also renamed accordingly (the test references its own path patterns).
