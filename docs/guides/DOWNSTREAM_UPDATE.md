# Downstream Update Guide

**Purpose**: Step-by-step guide for AOD template adopters to safely pull upstream AOD-kit template updates into their customized projects.

**Script**: `scripts/update.sh`
**Slash command**: `/aod.update`
**Make target**: `make update`

**Direction**: `upstream → your project` — pulling the latest AOD-kit template changes into your local repo.

---

## Release Notes — Stack Pack Test Contract

This release introduces a **stack pack test contract requirement**: every app-stack pack's `STACK.md` must declare a machine-readable contract block under Section 7 (Testing Conventions) so `/aod.deliver` can validate E2E tests deterministically. See [`docs/stacks/TEST_COMMAND_CONTRACT.md`](../stacks/TEST_COMMAND_CONTRACT.md) for the canonical schema, examples, and lint exit codes.

A **one-release grace period** existed in the release prior to this one and has been removed (Feature 142 — Issue #142). Stack packs missing a contract block now fail delivery with an explicit error — migrate per [`docs/stacks/TEST_COMMAND_CONTRACT.md`](../stacks/TEST_COMMAND_CONTRACT.md).

> **Historical note**: The grace-period implicit-opt-out behavior was removed by Feature 142 (Issue #142). The prior release warned adopters that contract blocks would become mandatory; this release enforces that requirement. Adopters without contract blocks will see `e2e_validation.status = "error"` during `/aod.deliver`.

Run `bash .aod/scripts/bash/stack-contract-lint.sh stacks/<pack>/STACK.md` against each active pack to verify compliance before the next upstream update.

---

## What is this?

`/aod.update` applies the latest AOD-kit template updates to your project. It protects your customizations — product docs, architecture, brands, constitution, feature specs — and re-applies your placeholder values to personalized files so nothing leaks.

Running it regularly keeps your project aligned with new commands, skills, agents, governance rules, and security patches from upstream without manual merge work.

---

## When to run it

- **After a new AOD-kit release** — upstream tag changes trigger new `owned` + `personalized` file updates
- **Periodically** — a monthly cadence is typical; catches incremental improvements between major releases
- **Before starting a major new feature** — make sure your commands, skills, and rules reflect the latest best practices

Not required for routine daily development. AOD-kit releases are versioned, so you decide when to adopt.

---

## Prerequisites

- **git** >= 2.30 installed
- **bash** (macOS 3.2+ or Linux 4+)
- `.aod/aod-kit-version` exists (created by `scripts/init.sh` on fresh install)
- `.aod/personalization.env` exists (created by `scripts/init.sh`)
- `flock` is optional — a PID+nonce+timestamp fallback is used on macOS

If you installed AOD-kit before this mechanism shipped, you are a "pre-mechanism adopter" — `.aod/aod-kit-version` and `.aod/personalization.env` will be absent. See the [Bootstrap (pre-F129 adopters)](#bootstrap-pre-f129-adopters) section below for the one-command on-ramp that auto-discovers most values and writes both files atomically.

---

## Quick start

```bash
make update
```

That's it. The script will:

1. Acquire a lock to prevent concurrent runs
2. Verify staging dir is on the same filesystem (atomicity requirement)
3. Fetch the latest upstream tag into a temp dir
4. Download and hash the upstream `.aod/template-manifest.txt`
5. Categorize every file in the upstream repo (owned / personalized / user / scaffold / merge / ignore)
6. Validate operations (guard list, symlinks, path traversal)
7. Stage files, running placeholder substitution on personalized files
8. Show a preview grouped by category
9. Prompt for confirmation (skip with `--yes`)
10. Apply atomically: each file is `mv`'d into place, `.aod/aod-kit-version` is updated last
11. Clean up staging on success; preserve it on failure for inspection

Expect the run to complete in under a minute for typical adopter projects (100-500 tracked files).

---

## Flags

| Flag | Default | Description |
|---|---|---|
| `--dry-run`, `-n` | false | Fetch + preview only. No writes outside the staging dir. Wins over `--apply`. |
| `--yes`, `-y` | false | Skip the confirmation prompt (still applies). |
| `--json` | false | Emit structured JSON (schema_version 1.0). No colors or progress. |
| `--edge` | false | Fetch upstream `main` HEAD instead of the latest tag. |
| `--force-retag` | false | Proceed even if the upstream tag SHA changed (supply-chain tripwire override; logs a warning). |
| `--upstream-url=<url>` | read from pin | Override the recorded upstream URL. Must be `https://` unless `--force-retag` is also passed. |
| `--apply` | context-dependent | Explicit apply flag. Default in interactive TTY when `CI` env is unset. `--dry-run` wins if both are passed. |
| `--help`, `-h` | — | Print help and exit. |

### Default behavior (when no explicit `--apply` / `--dry-run`)

- **Interactive TTY, `CI` env unset**: interactive confirm-then-apply (preview, prompt, user approves or declines)
- **`CI` env set**: `--dry-run` (automation safety net — pass `--apply` to override)
- **`--yes` passed**: skip the prompt but still apply (unless `--dry-run` is also passed)
- **stdin is NOT a TTY** (piped, redirected, cron): treat as `--dry-run` (fail-safe)

### Flag precedence

1. `--dry-run` ALWAYS wins: `--dry-run` + `--apply` = dry-run
2. `--yes` is orthogonal: it suppresses the confirmation prompt but does not force apply
3. `CI` env set + no explicit `--apply` / `--dry-run` → treat as `--dry-run`
4. Non-TTY stdin + no `--yes` / `--dry-run` → treat as `--dry-run` (cannot prompt)

---

## Exit codes

| Code | Meaning | What to do |
|---|---|---|
| 0 | Success (or dry-run completed) | Nothing — you're done |
| 1 | Generic failure | Read the error message; re-run with `--dry-run` to investigate |
| 2 | Lock contention | Another `/aod.update` is running, or a stale lock could not be cleared. Wait and retry, or remove `.aod/update.lock` manually if stale |
| 3 | Missing prerequisites | `.aod/aod-kit-version` or `.aod/personalization.env` absent. See the [Bootstrap (pre-F129 adopters)](#bootstrap-pre-f129-adopters) section |
| 4 | Cross-filesystem staging | Staging dir is on a different filesystem than project root. Override with `AOD_UPDATE_TMP_DIR=<path-on-same-fs>` |
| 5 | Manifest coverage violation | Upstream has an uncategorized file. stderr lists each uncategorized path under `[aod] ERROR: manifest coverage violation — N upstream file(s) not categorized:` — this is the restored F132 diagnostic, not a new failure. File a bug report against AOD-kit upstream with the listed paths |
| 6 | Guard-list violation | Upstream manifest tried to write a user-owned path (e.g., `docs/product/**`). Supply-chain red flag — inspect upstream before retrying |
| 7 | Retag detected | Upstream tag SHA differs from recorded SHA (possible adversarial retag). Inspect, then retry with `--force-retag` if benign |
| 8 | Residual placeholder | Personalized file has `{{VAR}}` left after substitution. Add the missing placeholder to `.aod/personalization.env` and retry |
| 9 | Network failure | Check your network and upstream URL. Run with `--upstream-url=<url>` to override |
| 10 | User declined preview | Not an error — you said no at the prompt. Nothing written |

---

## Safety guarantees

- **Zero user-owned file writes**: files under `docs/product/**`, `docs/architecture/**`, `brands/**`, `.aod/memory/**`, `specs/**`, and `roadmap.md` / `okrs.md` / `CHANGELOG.md` are protected by a hardcoded guard list embedded directly in `scripts/update.sh`. Even a malicious or buggy upstream manifest cannot override this — the script halts with exit 6 if it tries.
- **Atomic version pin**: `.aod/aod-kit-version` is written last, via temp + `mv` on the same filesystem. Any mid-run failure leaves the pin either pre-update or post-update — never partial.
- **Lock contention safety**: primary concurrency path uses PID + nonce + timestamp (works without `flock`, which is absent on macOS). Nonce re-verify before lock removal prevents zombie-PID-reuse from deleting another runner's lock. Liveness probe (`kill -0`) + >1h staleness window handles crash recovery.
- **No symlinks**: neither the fetched upstream tree nor the staged tree may contain symlinks. Rejected at validate phase.
- **No path traversal**: `..`, `~`, and absolute paths are rejected in manifest entries at parse time.
- **Retag detection**: upstream tag SHA is recorded in `.aod/aod-kit-version`. If the resolved SHA changes, the run halts (supply-chain defense against adversarial retagging) unless `--force-retag` is passed.
- **Staging preserved on failure**: `.aod/update-tmp/<uuid>/` is kept for inspection when any phase after fetch fails. Clean it manually after you've investigated.
- **Fail-safe automation**: non-TTY stdin or `CI` env set defaults to `--dry-run`. You cannot accidentally write from a cron job or piped script.

---

## FAQ

### Can I roll back an update?

Yes — `.aod/aod-kit-version` records the previous tag + SHA before each update. To roll back:

1. Use `git` to revert the files that were changed (your repo is a git repo, right?)
2. Restore the previous `.aod/aod-kit-version` from git history

Because every update advances the pin atomically, a roll-back is just a git revert of the commits the update produced.

### What if my local changes conflict with upstream?

`/aod.update` NEVER touches files in the user-owned guard list (product docs, architecture, brands, constitution, specs, roadmap/OKRs/CHANGELOG). So your personal customizations are safe by construction.

For `owned` files (commands, skills, agents, scripts), upstream wins — if you've locally customized a file marked `owned`, your changes are overwritten. If you want to keep customizations, fork the file to a different path or discuss with AOD-kit maintainers about marking it `personalized` or `merge`.

For `personalized` files, the upstream template ships with `{{PLACEHOLDER}}` tokens and your `.aod/personalization.env` values are re-applied on each update — so your project-specific content survives intact.

### Where does it download upstream from?

The recorded URL in `.aod/aod-kit-version` is the canonical source. By default, `scripts/init.sh` points it at the public AOD-kit repo on GitHub. Override per-run with `--upstream-url=<url>` (must be `https://`; add `--force-retag` to change the recorded URL).

### How does it know which files are mine vs the template's?

Upstream ships a `.aod/template-manifest.txt` that categorizes every file in the AOD-kit template repo (`owned`, `personalized`, `user`, `scaffold`, `merge`, `ignore`). `/aod.update` fetches this manifest fresh on every run, hashes it, and compares to the hash recorded in `.aod/aod-kit-version`. Any `user → owned|personalized|scaffold|merge` transitions (which would expand what upstream owns) are flagged as security warnings in the preview.

On top of the manifest, the hardcoded guard list in `scripts/update.sh` unconditionally protects your most sensitive paths — the manifest cannot override it.

### Can I run it in CI?

Yes. `CI` env set defaults to `--dry-run`, which is the automation-safe mode. If you want to auto-apply in CI (e.g., a scheduled bot), pass `--apply --yes`. Use `--json` for machine-readable output.

### What's the `merge` category?

Files marked `merge` (e.g., `Makefile`, `.gitignore`) require human judgment when they change — P0 behavior is "warn and skip" (the preview lists the change, the apply phase leaves your local copy alone). A future release will add interactive merge assistance; for now, after each update run, inspect merge-category files with `git diff upstream/main` (via `/aod.sync-upstream`) and apply changes manually.

### How long does a typical run take?

Under 1 minute for 100-500 tracked files (SC-001 target: <5 minutes). Preview renders in under 30 seconds. The staging + apply phase is dominated by filesystem `mv` calls, which are fast on local disks.

---

## README Lifecycle

The root `README.md` and `.aod/scaffold/README.md` have distinct lifecycle roles. Understanding the split helps when customizing your project's README and when running `/aod.update`.

### The two files

| File | Role | Manifest category | Owner |
|---|---|---|---|
| `README.md` (root) | Your project's hand-edited README. Public-facing on your repo's GitHub landing page. | `user|` (silent skip on update) | You — edit freely. |
| `.aod/scaffold/README.md` | Token-bearing seed used by `init.sh` during bootstrap. Never rendered to a public surface; lives buried under `.aod/`. | `owned|` (refreshed verbatim on update) | Upstream — do not hand-edit. |

### What happens at each lifecycle moment

**Clone** — When you `git clone` AOD Kit (or the consumer-facing template repo), GitHub renders the root `README.md` as a polished marketing landing page describing AOD itself. The scaffold under `.aod/scaffold/` is not rendered anywhere — it's just a file waiting for `init.sh`.

**`make init` (one-shot bootstrap)** — `scripts/init.sh` copies `.aod/scaffold/README.md` over the root `README.md`, then `replace_in_files()` substitutes all `{{PROJECT_NAME}}` and other tokens with the values you provided at the prompts. The result: your root `README.md` describes *your* project, with your project name baked in.

> **`make init` is one-shot per project.** Re-running it overwrites your customized root `README.md` with the scaffold (then re-substitutes tokens). If you want to refresh tokens after init, edit `README.md` directly — do not re-run `init.sh`. This matches the existing init.sh behavior; the scaffold copy step (Feature 169) does not change it.

**`/aod.update` (periodic upstream sync)** — Because root `README.md` is classified `user|`, `/aod.update` **silently skips it** — no preview, no warning, no overwrite. Your customizations are safe forever after init. `.aod/scaffold/README.md` is `owned|`, so upstream improvements to the scaffold flow through automatically (you'll see it as `update` or `skip` in the preview).

### Why the scaffold persists after init

After `make init` runs, `.aod/scaffold/README.md` remains in your repo. This is intentional: future `/aod.update` runs may refresh it from upstream so a *fresh re-clone* of the AOD template still has the latest scaffold. The scaffold is never re-substituted on your side (that would defeat its purpose as a seed for re-clone scenarios). You can leave it alone — it is `owned|` and managed by upstream.

If you don't expect to re-init or re-clone, deleting `.aod/scaffold/` is harmless. `init.sh` will still run for fresh installs because it has a defensive existence check on the file. But removing it offers no upside, and `/aod.update` would re-add it on the next run.

---

## Bootstrap (pre-F129 adopters)

If you installed AOD-kit before Feature 129 (the `/aod.update` mechanism) shipped, your repo is missing two prerequisite files that `make update` expects: `.aod/aod-kit-version` and `.aod/personalization.env`. Running `make update` in this state exits with code 3 ("missing prerequisites"). This section walks you end-to-end from "error" to "updated" without external references.

The bootstrap command auto-discovers 8 of the 12 canonical placeholder values from your repo state (manifest files, git config, `gh` metadata) and prompts you for 4 architecture values (database, vector store, auth provider, cloud provider). After a confirmation summary, it writes both prerequisite files atomically using the F129-delivered helpers. You stay in control — no file is touched until you confirm, and the overwrite-guard refuses to clobber an existing bootstrap.

### Dual-repo model

This template spans two repositories: `product-led-spec-kit` (PLSK) is the meta-template repo where the methodology, governance, and helper scripts are authored; `agentic-oriented-development-kit` (AOD-kit) is the downstream-facing upstream that adopters track via `/aod.update`. PLSK syncs its deliverables into AOD-kit; your adopter project pulls from AOD-kit. The bootstrap command always targets AOD-kit as the upstream — never PLSK. A dedicated PLSK-fingerprint guard (FR-002-b) refuses to bootstrap if the working tree looks like PLSK itself, preventing a confused-deputy scenario where you accidentally run bootstrap inside the meta-template.

### Walkthrough

1. **Verify you are a pre-F129 adopter.** From your project root:

   ```bash
   ls -la .aod/aod-kit-version .aod/personalization.env
   # Both files should be absent (ls will report "No such file or directory")
   ```

   If either file exists, you are already bootstrapped — do not run bootstrap; run `make update` directly.

2. **Set the 4 always-prompt env vars** (only required for `--yes` mode; interactive mode will prompt):

   ```bash
   export AOD_BOOTSTRAP_TECH_STACK_DATABASE=Postgres
   export AOD_BOOTSTRAP_TECH_STACK_VECTOR=pgvector
   export AOD_BOOTSTRAP_TECH_STACK_AUTH=JWT
   export AOD_BOOTSTRAP_CLOUD_PROVIDER=Vercel
   ```

   Substitute your own values. See the troubleshooting table below for what happens if any of these are unset in `--yes` mode.

3. **Run the bootstrap**. For interactive mode (recommended for first-time adopters):

   ```bash
   make update-bootstrap
   ```

   For unattended / CI usage:

   ```bash
   make update-bootstrap YES=1
   ```

4. **Review the summary table**. Interactive mode displays all 12 canonical values with confidence markers (`high` / `prompt` / `low`) before writing. Expected format:

   ```
   Resolving upstream URL... https://github.com/davidmatousek/agentic-oriented-development-kit.git
   Fetching upstream (shallow clone)... done
   Computing manifest SHA-256... done
   Auto-discovering 8 canonical values... done

   +------------------------------+-----------------+------------+
   | Field                        | Value           | Confidence |
   +------------------------------+-----------------+------------+
   | PROJECT_NAME                 | my-project      | high       |
   | PROJECT_DESCRIPTION          | (none found)    | low        |
   | GITHUB_ORG                   | my-org          | high       |
   | GITHUB_REPO                  | my-project      | high       |
   | AI_AGENT                     | Claude Code     | prompt     |
   | TECH_STACK                   | Python          | high       |
   | TECH_STACK_DATABASE          | Postgres        | prompt     |
   | TECH_STACK_VECTOR            | pgvector        | prompt     |
   | TECH_STACK_AUTH              | JWT             | prompt     |
   | RATIFICATION_DATE            | 2025-11-01      | high       |
   | CURRENT_DATE                 | 2026-04-24      | high       |
   | CLOUD_PROVIDER               | Vercel          | prompt     |
   +------------------------------+-----------------+------------+

   Confirm and write? [y/N]: y
   Writing .aod/personalization.env... done
   Writing .aod/aod-kit-version... done

   Bootstrap complete. Next: make update --check-placeholders && make update --dry-run
   ```

   Answer `y` to write both files, or `n` to decline cleanly (exit 0, no writes, staging dir cleaned up).

5. **Verify the writes succeeded**:

   ```bash
   cat .aod/aod-kit-version
   cat .aod/personalization.env
   bash -c 'set -e; source .aod/personalization.env; echo "sourced OK, PROJECT_NAME=$PROJECT_NAME"'
   ```

   The `source` command must succeed with zero parse errors — this proves the conditional-quoting contract is intact.

### Conditional-quoting convention

The `aod_template_init_personalization` helper applies a conditional-quoting rule when writing `.aod/personalization.env`: values matching the regex `^[A-Za-z0-9._/:@+=-]+$` are written **bare** (unquoted), and all other values are written **double-quoted**. This rule exists so that routine values (hostnames, project names, semantic versions, simple paths) stay readable while values containing shell metacharacters (spaces, quotes, `$`, `;`, `&`, etc.) stay safe under `source`. An external F129 adopter review (2026-04-19) surfaced this requirement as previously undocumented — adopters hand-crafting the file before bootstrap shipped hit silent shell-injection / source failures because the rule was implicit. If you hand-edit `.aod/personalization.env` after bootstrap, apply the same rule: bare for simple values matching `^[A-Za-z0-9._/:@+=-]+$`, double-quoted otherwise.

### Troubleshooting

| Symptom / exit code | Likely cause | Fix |
|---|---|---|
| Exit 2 immediately, stderr `refusing to overwrite existing .aod/aod-kit-version` | The repo is already bootstrapped (file exists with any content) | This is the overwrite-guard working as designed. Either you are not a pre-F129 adopter (skip bootstrap, run `make update` directly), or you want to re-bootstrap — in which case move the existing file aside first: `mv .aod/aod-kit-version .aod/aod-kit-version.bak` |
| Exit 2 immediately, stderr `refusing to bootstrap from within PLSK itself` | PLSK-fingerprint guard triggered because you are running from inside the `product-led-spec-kit` meta-template, not from a downstream adopter project | Change directory to your actual adopter project (the repo that tracks AOD-kit as upstream) and retry |
| Exit 9 | Upstream URL unreachable (no network, DNS failure, GitHub outage, firewall) | Check connectivity; optionally set `AOD_UPSTREAM_URL=file:///path/to/local/clone` to bootstrap from a local clone for air-gapped testing |
| Error about `gh: command not found` during auto-discovery | `gh` CLI is not installed; auto-discovery for `GITHUB_ORG` / `GITHUB_REPO` / `PROJECT_DESCRIPTION` degrades | In interactive mode, the command prompts for those fields. In `--yes` mode, set `AOD_BOOTSTRAP_GITHUB_ORG` / `AOD_BOOTSTRAP_GITHUB_REPO` / `AOD_BOOTSTRAP_PROJECT_DESCRIPTION` explicitly, OR install `gh` from https://cli.github.com/ |
| `bash: declare: -A: invalid option` or similar | You are running on macOS system bash (3.2), but a newer bash feature slipped into the code path | File a bug report — all code in this project is bash 3.2 compatible per the CLAUDE.md constraint. Meanwhile, install a newer bash (`brew install bash`) and invoke explicitly: `/opt/homebrew/bin/bash scripts/update.sh --bootstrap` |
| Exit 1 in `--yes` mode, stderr names a specific `AOD_BOOTSTRAP_*` variable | `--yes` mode refuses to proceed when any always-prompt field (database / vector / auth / cloud) or low-confidence auto-discovered field lacks an env var override | Export the named variable and retry. There is no global `--accept-all-defaults` escape hatch by design — each field is addressable individually |

### Next steps

Once bootstrap succeeds, run these two follow-up commands in order to clean up any legacy placeholder drift and preview the first real update:

```bash
make update --check-placeholders   # Detect any legacy {{PLACEHOLDER}} names not in the canonical 12 (per FR-010 scanner behavior)
make update --dry-run              # Preview the first upstream update without writing
```

`make update --check-placeholders` is the drift detector. It scans every git-tracked file (excluding documentation-literal paths like PRDs, specs, `.claude/`, and `CHANGELOG.md`) and reports occurrences of legacy names like `{{DATABASE_TYPE}}` or `{{VECTOR_DB}}` with a version-stamped migration table. Exit code 13 signals drift found; exit 0 means clean. `make update --dry-run` then shows you exactly what the first real update would change, with no writes outside the staging directory — safe to run multiple times. Once both commands are clean and the preview looks right, run `make update` to apply.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| "Missing .aod/aod-kit-version" | You're a pre-mechanism adopter. See the [Bootstrap (pre-F129 adopters)](#bootstrap-pre-f129-adopters) section for the one-command on-ramp |
| "Cross-filesystem staging" (exit 4) | Set `AOD_UPDATE_TMP_DIR=<path-on-same-fs-as-project-root>` and retry |
| "Lock contention" (exit 2) | Another run is active, or a stale lock exists. Check `cat .aod/update.lock` for holder PID; remove the lock if stale |
| "Manifest coverage violation" (exit 5) | Expected adopter-visible diagnostic restored by Feature 132 (Issue #132, PR #152). stderr header is `[aod] ERROR: manifest coverage violation — N upstream file(s) not categorized:` followed by a hyphen-prefixed list. **This is not a new failure** — it is the safety net becoming visible. Copy the listed paths into a bug report against AOD-kit upstream |
| "Guard-list violation" (exit 6) | Upstream is trying to write a user-owned path. Inspect the manifest, report to AOD-kit upstream, retry once resolved |
| "Retag detected" (exit 7) | Upstream tag SHA changed. Investigate first (`git log` on upstream); retry with `--force-retag` if benign |
| "Residual placeholder" (exit 8) | Upstream introduced a new placeholder. Add it to `.aod/personalization.env` and retry |
| "Network failure" (exit 9) | Check network; verify upstream URL is reachable; retry |
| Preview shows unexpected changes | Run `make update --dry-run --json | jq` for full detail; inspect staging dir under `.aod/update-tmp/<uuid>/` |

---

## Full walkthrough example

```bash
# Fresh adopter, ran init.sh a week ago; new AOD-kit tag released yesterday.
cd my-project
cat .aod/aod-kit-version           # pins v2.0.0

make update --dry-run              # preview v2.0.0 -> v2.1.0
# See 8 changes: 6 owned (new commands), 2 personalized (rule updates).

make update                        # interactive: preview, confirm, apply
# [apply] .claude/commands/aod.foo.md         (copy)
# [apply] .claude/rules/scope.md              (substitute)
# [skip ] CLAUDE.md                           (merge category, P0 defer)
# [apply] .aod/aod-kit-version                (atomic write)
# [done ] Update complete in 23 seconds.

cat .aod/aod-kit-version           # now pins v2.1.0
git diff .claude/commands/         # inspect what changed
git commit -am "chore: update AOD-kit template to v2.1.0"
```

---

## Recommended update cadence

- **Monthly**: Check for upstream changes on the first week of each month (`make update --dry-run`)
- **On-demand**: When upstream releases important bug fixes or new features
- **Before new features**: Update before starting major new feature work

---

## Reference

- **Script source**: `scripts/update.sh`
- **Slash command**: `.claude/commands/aod.update.md`
- **Make target**: `Makefile` (search for `update:`)
- **CLI contract**: [`specs/129-downstream-template-update/contracts/cli-contract.md`](../../specs/129-downstream-template-update/contracts/cli-contract.md)
- **Manifest schema**: [`specs/129-downstream-template-update/contracts/manifest-schema.md`](../../specs/129-downstream-template-update/contracts/manifest-schema.md)
- **Version pin schema**: [`specs/129-downstream-template-update/contracts/version-schema.md`](../../specs/129-downstream-template-update/contracts/version-schema.md)
- **JSON output schema**: [`specs/129-downstream-template-update/contracts/json-output-schema.md`](../../specs/129-downstream-template-update/contracts/json-output-schema.md)
- **Predecessor (archived)**: [`archive/UPSTREAM_SYNC.md`](archive/UPSTREAM_SYNC.md) — the older `scripts/sync-upstream.sh` walkthrough, superseded by this guide
