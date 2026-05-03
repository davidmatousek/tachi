# Delivery Hard-Gate Migration Guide

**Purpose**: Step-by-step guide for AOD template adopters migrating from the soft-gate `/aod.deliver` behavior (warn on test fail, autonomous override) to the hard-gate default introduced by Feature 139 — "Delivery Means Verified, Not Documented."

**Related**: [`AC_COVERAGE_MIGRATION.md`](./AC_COVERAGE_MIGRATION.md) — sibling guide covering the strict Given/When/Then AC retrofit path.
**Spec**: [`specs/139-delivery-verified-not-documented/spec.md`](../../specs/139-delivery-verified-not-documented/spec.md)
**ADR**: [`docs/architecture/02_ADRs/ADR-013-delivery-verification-first.md`](../architecture/02_ADRs/ADR-013-delivery-verification-first.md)

**Direction**: template release → your project — adapting to the new hard-gate behavior after `/aod.update` lands this feature.

---

## Who is this for?

You if:

- Your project runs `/aod.deliver` as part of its lifecycle, interactively or via `/aod.run` / `/aod.orchestrate`.
- You have relied on the pre-v2.x+1 soft-gate behavior where failing E2E tests produced a warning but delivery still proceeded.
- You invoke `/aod.deliver --autonomous` from CI pipelines or batch orchestration jobs.
- You currently pass `--require-tests` to force the hard gate explicitly.
- You customized `.aod/templates/delivery-template.md` at any point.

If you do not run `/aod.deliver` at all, or your features always ship with passing tests, this migration is effectively a no-op — but read §Behavior Change at a Glance anyway so future debugging is easier.

---

## What changed?

Constitution Principle III (NON-NEGOTIABLE) required a 2-release grace period for this behavior flip. That grace period has started with this release. Here is the full picture.

### Behavior Change at a Glance

| Dimension | Before (v2.x) | After (v2.x+1 — this release) |
|---|---|---|
| Default gate on test fail | Warn + proceed | HALT + require explicit opt-out |
| Autonomous mode override | Yes (gate skipped silently) | NO — halts identically to interactive |
| Skip mechanism | `--no-tests` flag (no reason) | `--no-tests=<reason>` (reason 10-500 chars, audit-logged) |
| `--require-tests` flag | Forced hard-gate | No-op + stderr deprecation (grace: 2 releases) |
| `/aod.deliver` on failing tests exit code | 0 (success with warning) | 10 (halted for review) |
| Concurrent invocation on same feature | Races / corrupts state | Second aborts with exit 11 |
| Abandoned heal loop (crash mid-flight) | Resumed silently, possibly corrupted | Halts with exit 12 + manual-cleanup prompt |
| Delivery doc "Test Evidence" section | Single block mixing intention and outcome | Three distinct subsections: Test Scenarios, Execution Evidence, Manual Validation |

The summary: delivery now carries a verification guarantee. Shipping with a failing suite requires a logged, reviewable opt-out with a written reason. Silent overrides are gone.

---

## Upgrade summary

1. Run `/aod.update` to pull the feature. This applies new skill code, templates, and contracts.
2. Review your CI jobs — any `/aod.deliver --autonomous` call that previously exited 0 on failing tests now exits 10. Update branch logic for exit codes 10, 11, 12.
3. If you customized `delivery-template.md`, perform a 3-way merge (details below). Budget 15-30 minutes.
4. If you currently pass `--require-tests`, remove it. The stderr deprecation notice will prompt you for two releases; after that, the flag errors out.
5. (Optional) Create `.aod/config.json` to tune the auto-fix heal budget or disable it entirely.
6. Run `/aod.deliver` on a pilot feature to confirm the new three-subsection delivery doc renders correctly and the exit codes match your CI expectations.

---

## `--require-tests` deprecation timeline

The `--require-tests` flag was the pre-v2.x+1 way to force the hard gate. Now that the hard gate is the default, the flag is redundant.

The deprecation runs for **two release cycles** per Constitution Principle III (Backward Compatibility, NON-NEGOTIABLE):

- **Release N (this release, v2.x+1)**: `--require-tests` is accepted as a no-op. Every invocation emits one stderr line:
  ```
  [deprecated] --require-tests is now default (v2.x+1); flag accepted but has no effect. Will be removed in v2.x+3.
  ```
  Delivery proceeds under the hard-gate default. Your existing CI pipelines and scripts continue to work unchanged.

- **Release N+1 (v2.x+2)**: Same behavior. Stderr notice continues to reference the same removal version. This is your second grace release.

- **Release N+2 (v2.x+3)**: Flag is REMOVED. Invoking `/aod.deliver --require-tests` fails at argument parsing with exit code 2 and this error:
  ```
  Error: --require-tests was removed in v2.x+3. The hard gate is now the default. See docs/guides/DELIVERY_HARD_GATE_MIGRATION.md.
  ```

### Version token resolution

The `{CURRENT}` and `{REMOVAL}` tokens in the stderr notice come from a single source of truth:

1. **Primary**: `git describe --tags --abbrev=0` on the installed template's `.aod/template-manifest.txt` commit. This resolves the active kit version from the repo's tags.
2. **Fallback**: `.aod/VERSION` file if present. Adopters who installed from a tarball without git history use this file; `scripts/init.sh` writes it on fresh installs.
3. **Removal version** is computed as `CURRENT + 2 patch releases` per the fixed grace window. Expressed as a plain SemVer bump.

If neither source is readable, the stderr notice falls back to `v? (unknown)` for the version fields but the deprecation message itself still appears — you will know the flag is deprecated, just not which release will remove it. Fix by re-running `/aod.update` or manually re-creating `.aod/VERSION` from the latest tag.

### What to do

Remove `--require-tests` from:

- Shell scripts that invoke `/aod.deliver`
- CI workflow files (`.github/workflows/*.yml`, `.gitlab-ci.yml`, etc.)
- Blueprint YAML files' `deliver_flags` arrays (if you migrated to orchestrator-based delivery per US-3)
- Internal runbooks and developer documentation
- Team wiki pages describing the release process

Replace nothing — the hard gate is now the default. If you WANT to skip the gate for a specific feature, see §Opt-Out Mechanism.

---

## `.aod/config.json` defaults

Feature 139 introduces an optional `.aod/config.json` for tuning auto-fix heal-loop behavior. The file is **not** created automatically when you run bare `/aod.deliver`.

### Default shape

```json
{
  "version": 1,
  "deliver": {
    "heal_attempts": 2,
    "heal_max_timeout_multiplier": 1.5
  }
}
```

### When to create it

- You want to **disable auto-fix entirely** (failures escalate directly to heal-PR). Set `heal_attempts: 0`.
- You want to **allow more heal attempts** (default is 2). Increase `heal_attempts`. Be aware each attempt runs the full E2E suite, so doubling this doubles worst-case wall-clock.
- You want to **allow larger timeout bumps** in healed diffs. Increase `heal_max_timeout_multiplier` above 1.5. The scope guard rejects any proposed timeout change that exceeds the multiplier; raising this lets more automated wait-condition fixes through.

### Creation

The kit ships `.aod/config.json.example`. To activate it:

```bash
cp .aod/config.json.example .aod/config.json
# Edit as needed.
```

Do **not** rely on the config file being auto-created on bare `/aod.deliver`. Without the file, all fields take defaults — this is intentional so adopters with zero configuration get a sensible hard-gate + 2-attempt-heal setup without extra setup steps.

### Reading semantics

Runtime uses a `jq // default` pattern: missing file, missing keys, and missing values all resolve to the defaults listed above. **Malformed JSON** (syntax error, not a legal object) is the one case that halts delivery with exit 1 — see §FAQ for the rationale.

### Schema versioning

The `version` key is mandatory for future-proofing. The kit currently only supports schema version 1. Future PRDs may add top-level sections (e.g., a `coverage` key, a `security` key) without breaking this PRD's parser. When those ship, this guide will be updated.

---

## Opt-out mechanism: `--no-tests=<reason>`

The only sanctioned way to skip the hard gate is `--no-tests=<reason>`. Every accepted opt-out is logged.

### Usage

```bash
/aod.deliver --no-tests="Manual UX review pending — external copy approval required before launch"
```

### Reason constraints

- **Minimum length**: 10 characters (trimmed). Single-word or empty reasons are rejected.
- **Maximum length**: 500 characters. Longer reasons are rejected at flag parse with a specific error.
- **Validation**: happens before the gate logic runs, so you can never "skip the gate and see if it works." Invalid reasons fail fast with exit 2.

### Audit trail

Every accepted opt-out appends one JSON line to `.aod/audit/deliver-opt-outs.jsonl`:

```json
{"timestamp":"2026-04-23T14:30:00Z","invoker":"jane@example.com","feature":"139-delivery-verified-not-documented","reason":"Manual UX review pending — external copy approval required","mode":"interactive"}
```

Fields:

| Field | Source | Notes |
|---|---|---|
| `timestamp` | ISO-8601 UTC `date -u +%FT%TZ` | UTC always, no local-time drift |
| `invoker` | `git config user.email` OR literal `"autonomous"` | Orchestrator sets mode=autonomous |
| `feature` | Current git branch `NNN-name` | Feature identifier from branch |
| `reason` | Verbatim from `--no-tests=<reason>` | 10-500 chars, unmodified |
| `mode` | `"interactive"` or `"autonomous"` | Set by invocation context |

### Audit log is tracked in git

The file lives at `.aod/audit/deliver-opt-outs.jsonl`. It is **intentionally tracked** in git — not listed in `.gitignore`. This gives your team a reviewable history of every time the gate was bypassed, with who/why/when.

`/aod.update` **will NOT rewrite or prune this file**. It is explicitly excluded from the template sync guard list. Migration runs preserve it byte-for-byte.

### Interactive session surfacing

When you run `/aod.deliver` with `--no-tests=<reason>`, the opt-out surfaces in the delivery document's "Manual Validation" subsection automatically. The reason is rendered alongside timestamp + invoker so a reviewer opening the delivery artifact sees exactly why the gate was skipped without having to grep the audit log.

### Combined with `--require-tests`

Don't. The parser rejects `--no-tests=<reason> --require-tests` as a conflicting flag combination before the gate runs. This is true during the grace period (when `--require-tests` is a no-op) — the mutual exclusion is about intent clarity, not semantic conflict.

---

## Delivery template merge guidance

Feature 139 rewrites `.aod/templates/delivery-template.md` to split the former single "Test Evidence" section into three distinct subsections:

| Subsection | Content | When it renders |
|---|---|---|
| Test Scenarios (Living Documentation) | AC → scenario mapping with collapsible full Gherkin | Always |
| Execution Evidence | Pass/fail/skipped counts, gate mode, duration, command used, artifact paths, Recovery Actions table | Always |
| Manual Validation | Opt-out reason + invoker + timestamp, and/or list of `[MANUAL-ONLY]` ACs with reasons | Conditional — when opt-out OR manual-only ACs exist |

If you never customized `delivery-template.md`, `/aod.update` applies the new template cleanly. Zero action required.

If you customized it (common reasons: added a stakeholder approval section, renamed headings, injected project-specific badges), `/aod.update` presents a 3-way merge prompt.

### Estimated cost

15-30 minutes per adopter, depending on depth of customization.

### Merge steps

1. **Back up current customizations**:
   ```bash
   cp .aod/templates/delivery-template.md .aod/templates/delivery-template.md.bak
   git add .aod/templates/delivery-template.md.bak  # preserve across merge
   ```

2. **Run `/aod.update` to apply upstream**:
   ```bash
   /aod.update
   ```
   The diff preview will show your current template replaced by the new three-subsection version. Accept the update.

3. **Re-merge custom fields into the new subsection shape**:
   - Re-attach custom stakeholder blocks to the "Manual Validation" subsection.
   - Re-attach project-specific badges to the top of "Execution Evidence."
   - Custom headings should be mapped into one of the three subsections based on intent (scenario documentation vs. execution outcome vs. human-only validation).

4. **Verify by running `/aod.deliver` on a pilot feature**:
   ```bash
   git checkout -b 999-template-merge-pilot
   # Make a trivial change.
   /aod.deliver
   # Inspect the rendered delivery document.
   ```

5. **Delete the backup** once you confirm the new template renders correctly:
   ```bash
   rm .aod/templates/delivery-template.md.bak
   git rm --cached .aod/templates/delivery-template.md.bak
   ```

If you discover your customizations don't cleanly map into the three-subsection shape, raise an issue requesting a template extension point. The new shape was chosen to separate intention (what scenarios exist) from outcome (what happened) from human-only signal (what can't be automated) — custom sections that don't fit one of those three buckets are a signal for a template extension mechanism, not a reason to reject this PRD.

---

## Release notes bullet template

Copy this into your own project's release notes, customer-facing changelog, or team wiki when you pull this upstream change:

```markdown
### Breaking: /aod.deliver hardened to verification-first

- Tests failing → delivery halts (previously warned + proceeded).
- Autonomous mode respects the gate (previously overrode).
- Opt out with `--no-tests="<reason>"`; reason is logged to `.aod/audit/deliver-opt-outs.jsonl`.
- `--require-tests` is now the default behavior; flag accepted as no-op for 2 releases.
- See: docs/guides/DELIVERY_HARD_GATE_MIGRATION.md
```

Adjust phrasing for your audience — the first four bullets are the load-bearing content.

---

## FAQ for adopters

### Q: My feature has flaky tests that auto-fix can't handle. What are my options?

A: You have three layered choices:

1. **Disable auto-fix entirely** for this project: set `heal_attempts: 0` in `.aod/config.json`. The heal loop is skipped; failing tests escalate directly to a heal-PR with the failure context, without trying to patch anything first. Best when your tests are reliable enough that auto-fix rarely helps.

2. **One-off skip with audit**: invoke `/aod.deliver --no-tests="<reason>"`. The gate is bypassed for this single run, reason is logged, delivery proceeds. Best when a specific feature has an unfixable transient test issue and you need to ship.

3. **Structural exemption per AC**: mark individual acceptance criteria `[MANUAL-ONLY] <reason>` (reason ≥10 chars) in `spec.md`. The AC-coverage gate permits those ACs to skip scenario coverage; they are surfaced in the delivery document's Manual Validation section alongside their reasons. Best when you know up-front that a specific AC is physically unautomatable (e.g., hardware-in-the-loop, external human review).

You can combine (1) and (3). Combining (1) and (2) is redundant but not harmful. Combining (2) and (3) is also fine — the opt-out covers the gate, the MANUAL-ONLY markers cover coverage, they don't fight.

### Q: Does the audit log contain secrets from my reason strings?

A: The kit does **not** parse or strip reason content. Whatever you pass to `--no-tests="..."` is stored verbatim (subject to length bounds). You are responsible for not pasting tokens, API keys, PII, or other secrets into reason strings.

The audit log is stored with 0644 permissions (owner write, world read) and tracked in git. Treat it like any other source-controlled text file: if you wouldn't put it in a commit message, don't put it in a reason string. If you accidentally commit a secret in a reason string, rotate the secret and use `git filter-repo` or the standard secret-scrubbing playbook.

### Q: Will CI pipelines that invoke `/aod.deliver --autonomous` break?

A: It depends on the state of your tests:

- **If your feature has passing tests**: no change. Delivery proceeds, exit code 0, your CI job moves to the next stage.
- **If your feature has failing tests**: previously, autonomous mode overrode the gate and exited 0 (silent pass with warning). Now, the job exits **10** (halt for review). CI branch logic that checks `exit_code == 0 || handle_as_success` will incorrectly mark the job successful when delivery was actually halted.

**What to do**: update your CI branch logic to explicitly handle exit code 10:

```yaml
# Example GitHub Actions step
- name: Deliver feature
  run: /aod.deliver --autonomous
  continue-on-error: true
  id: deliver
- name: Route halt-for-review
  if: steps.deliver.outcome == 'failure'
  run: |
    case "${{ steps.deliver.outputs.exit_code }}" in
      10) echo "Halted for review, see heal-PR"; gh issue create ... ;;
      11) echo "Concurrent delivery blocked, retry later" ;;
      12) echo "Abandoned heal detected, manual cleanup required"; exit 1 ;;
      *)  echo "Unexpected failure"; exit 1 ;;
    esac
```

Exit codes 10, 11, 12 are additive to PRD 130's 0-5. The full exit-code taxonomy is documented in ADR-013.

### Q: Can I opt out for an entire adopter-org across all features?

A: Not today. Opt-out is strictly per-invocation via `--no-tests=<reason>`. There is no org-level configuration key that disables the gate wholesale — and that absence is deliberate. Broad skips defeat the PRD's purpose (verification guarantee) and prevent audit-log meaningfulness.

If you need a broader skip capability (e.g., a monorepo where one sub-project legitimately can't run E2E tests in CI), raise a GitHub Issue against the upstream AOD-kit template with:

- The concrete scenario driving the need
- Why `[MANUAL-ONLY]` AC markers + `heal_attempts: 0` are insufficient
- What shape of org-config key you propose

The maintainers will evaluate whether a controlled-surface config extension (with auditable trace) is warranted. Until then, use per-invocation opt-outs with meaningful reasons.

### Q: What happens if `.aod/config.json` is malformed?

A: Delivery exits with code 1 (runtime error) and a parse-error message like:

```
Error reading .aod/config.json: parse error at line 4, column 17.
See docs/guides/DELIVERY_HARD_GATE_MIGRATION.md §Config defaults.
```

This is **safer than silently falling back to defaults**. A malformed config file means you intended to set something — perhaps a critical production value — and got it wrong. Silent fallback would ship defaults you didn't know applied.

To recover:

1. **Validate the file**:
   ```bash
   jq . .aod/config.json
   ```
   `jq` prints a specific parse-error line/column.

2. **Fix the syntax** (common culprits: trailing commas, unquoted keys, unescaped quotes inside reason strings).

3. **Or delete the file** if you no longer want the custom config:
   ```bash
   rm .aod/config.json
   ```
   Defaults (`heal_attempts: 2`, `heal_max_timeout_multiplier: 1.5`) will apply on the next run.

### Q: How do I disable the three-channel halt signal in autonomous mode?

A: You can't, and you shouldn't want to. The three channels (stdout line + halt record JSON + distinct exit code) are co-equal signals because different consumers (humans vs. log scrapers vs. CI shells) read different channels. Disabling any one breaks a consumer.

What you CAN do:

- **Ignore the stdout line**: if your CI tails the log, it's just one more line. Filter it out in your log-post-processor if it's noisy.
- **Ignore the halt record**: the file at `.aod/state/deliver-{NNN}.halt.json` is per-feature and overwritten on next run. If you don't read it, it's effectively inert. It's cleaned on clean exit; on halt, it persists until next run.
- **Map the exit code to success** (strongly discouraged): your CI can treat exit 10 as success, but you defeat the PRD's entire purpose. Don't.

---

## Troubleshooting

| Problem | Likely cause | Solution |
|---|---|---|
| "I see a new halt on a feature that passed yesterday" | Someone introduced a failing scenario on the feature branch between runs | `git log --since=yesterday -- specs/NNN-*/ tests/` — inspect changes to spec, acceptance criteria, or test files since yesterday |
| "Deprecation notice not appearing for `--require-tests`" | You're invoking a kit version that pre-dates this feature, OR `.aod/VERSION` / git tag lookup failed silently | Check `cat .aod/VERSION` (if present) and `git describe --tags --abbrev=0`. Both should report v2.x+1 or later. Re-run `/aod.update` if you're stale. |
| "Concurrent invocation blocked with exit 11" | Another `/aod.deliver` run holds the delivery lock for this feature | Inspect `ls -la .aod/locks/` for the lock file; `cat .aod/locks/deliver-{NNN}.lock` shows the holding PID + start timestamp + expected heal budget. If live, wait. If stale/zombied, the next invocation reaps automatically after 2× heal budget. If you know the PID is dead, manually remove the lock with `rm .aod/locks/deliver-{NNN}.lock` after confirming via `ps`. |
| "Exit 12 with `Abandoned heal in progress for feature NNN`" | Prior invocation crashed mid-auto-fix loop | Inspect the partial state displayed in the halt message (phase, attempt, last commit). Clear both files per the prompt: `rm .aod/state/deliver-NNN.state.json .aod/locks/deliver-NNN.lock`. Re-run `/aod.deliver`. |
| "Audit log line missing after a successful opt-out" | `.aod/audit/` directory unwritable, or line size exceeded 700-byte cap | Check permissions on `.aod/audit/`. The kit creates the dir on first write with `mkdir -p`; confirm no parent dir is read-only. If line exceeds 700 bytes (rare — requires near-max reason string), the pre-write size check logs to stderr and drops the append. Shorten the reason. |
| "Exit 2 on `/aod.deliver --no-tests="<reason>" --require-tests`" | Flag conflict rejection | These two flags are mutually exclusive. Remove `--require-tests` (it's a no-op anyway during the grace period). |
| "Exit 2 on `/aod.deliver --no-tests="x"`" | Reason below 10-char minimum | Expand the reason to at least 10 characters. The purpose is to force a meaningful human-readable explanation; "x" or "skip" are not meaningful and are rejected at parse. |
| "Heal-PR didn't open on exhaustion" | `gh` CLI missing in the environment | The skill falls back to writing heal artifacts to `.aod/results/heal-{NNN}-{timestamp}/`. Halt record notes `"heal-PR creation unavailable (no gh)"`. Install `gh` and re-run, or review artifacts manually. |

---

## Further reading

- [`docs/architecture/02_ADRs/ADR-013-delivery-verification-first.md`](../architecture/02_ADRs/ADR-013-delivery-verification-first.md) — Architectural rationale: hard-gate flip, scope-guard determinism, three-channel halt protocol, exit-code taxonomy 10/11/12 additive to PRD 130's 0-5.
- [`specs/139-delivery-verified-not-documented/spec.md`](../../specs/139-delivery-verified-not-documented/spec.md) — Feature specification with all nine user stories, acceptance criteria, and success criteria.
- [`docs/guides/AC_COVERAGE_MIGRATION.md`](./AC_COVERAGE_MIGRATION.md) — Sibling migration guide covering the strict Given/When/Then AC parser and `[MANUAL-ONLY]` marker retrofit for legacy prose specs.
- [`specs/139-delivery-verified-not-documented/contracts/audit-log.md`](../../specs/139-delivery-verified-not-documented/contracts/audit-log.md) — Opt-out audit log line schema, line-atomic write constraints, reader/writer patterns.
- [`specs/139-delivery-verified-not-documented/contracts/halt-record.md`](../../specs/139-delivery-verified-not-documented/contracts/halt-record.md) — Halt signal three-channel protocol + halt-record JSON schema.
- [`specs/139-delivery-verified-not-documented/plan.md`](../../specs/139-delivery-verified-not-documented/plan.md) §Migration & Adopter Impact — Plan-phase migration reasoning + 3-tier descope context.
- [`.aod/memory/constitution.md`](../../.aod/memory/constitution.md) Principle III — Backward Compatibility (NON-NEGOTIABLE), the 2-release grace period policy driving this migration timeline.
- [`docs/guides/DOWNSTREAM_UPDATE.md`](./DOWNSTREAM_UPDATE.md) — General template-update mechanism; this migration is delivered via the same `/aod.update` flow.

---

## Delivery Template Customization (`delivery-template.md` merge)

Adopters who customized `.aod/templates/delivery-template.md` will see a merge prompt on the next `/aod.update` sync. The Wave 4 rewrite introduced three new subsections under "Test Evidence":

1. **Test Scenarios (Living Documentation)** — AC-to-scenario mapping table + collapsible Gherkin
2. **Execution Evidence** — pass/fail table + invocation Command + artifact paths + Recovery Actions (conditional)
3. **Manual Validation** — opt-out reason block + manual-only AC list (conditional)

### Estimated merge cost
**~15-30 minutes** per adopter. The template changes are additive to the PRD 130 payload, so most custom content can be preserved by merging the new subsection headings into the existing "Test Evidence" section.

### Migration steps

1. Back up your current `delivery-template.md`: `cp .aod/templates/delivery-template.md .aod/templates/delivery-template.md.bak`
2. Run `/aod.update` — accept the delivery-template.md diff prompt
3. Open the merged file and verify:
   - All three subsection headings present under "Test Evidence"
   - Your custom sections outside "Test Evidence" preserved
   - Payload field references (`e2e_validation.*`) match the extended schema (`ac_coverage`, `recovery_status`, `recovery_actions`, `opt_out` blocks)
4. If you had custom rendering logic that references the old flat "Test Evidence" structure, migrate it into the most appropriate of the three new subsections:
   - Scenario-level content (names, Gherkin) → **Test Scenarios**
   - Runner output (pass/fail, logs, artifacts) → **Execution Evidence**
   - Human review blocks (opt-outs, manual-only ACs) → **Manual Validation**
5. Optionally commit the template back to your adopter repo to preserve customizations.

### Schema compatibility

The new `e2e_validation` payload fields are additive — PRD 130 renderers continue to work. Old fields that were present on PRD 130 (`scenarios[]`, `pass_count`, etc.) remain present and are now used inside the three new subsections.

---

### CI Integration: No-Auto-Merge Invariant

Feature 139 introduces FR-023 — "No AOD skill auto-merges any PR labeled `e2e-heal`." Heal-PRs, opened by `/aod.deliver` when the auto-fix loop exhausts its budget, MUST be reviewed by a human. To enforce this invariant inside the kit's own code, a static-check script ships at `.aod/scripts/bash/check-no-merge-heal.sh`.

The check scans `.claude/skills/**/*.md` and `.aod/scripts/bash/**/*.sh` for the pattern `gh pr merge.*e2e-heal` and exits non-zero if any violating line is found (excluding lines that intentionally document the ban via keywords like `banned`, `forbidden`, or `invariant.*no.*merge`).

#### Manual invocation

```bash
bash .aod/scripts/bash/check-no-merge-heal.sh
```

Run from repo root. Exit 0 with a single success line on stdout means the invariant holds. Exit 1 with a multi-line block on stderr names offending `file:line:content` tuples.

#### GitHub Actions integration

Drop this step into any workflow triggered on `pull_request` — recommended on PRs that touch `.claude/skills/` or `.aod/scripts/bash/`:

```yaml
- name: Verify heal-PR no-auto-merge invariant
  run: bash .aod/scripts/bash/check-no-merge-heal.sh
```

Equivalent snippets for other platforms (GitLab CI `script:` block, pre-commit hooks, Jenkins pipeline steps) are documented in the script's top-of-file adopter-usage comment block.

#### Scope boundary

Wiring this check into the default AOD Kit CI workflow is **OUT OF SCOPE for this PRD**. The kit provides the observability hook as an opt-in tool; adopters integrate per their platform based on where pre-merge enforcement makes sense in their pipeline. The rationale: adopters run different CI stacks (GitHub Actions, GitLab CI, Jenkins, Buildkite, pre-commit hooks) and a default wiring would force one choice over the others. The invariant itself is still enforced at the skill-code level (the skills simply do not contain any `gh pr merge` call targeting heal-PRs); the static check is belt-and-suspenders for adopters who want continuous assurance.

For the contract-level definition of FR-023 and the rationale for making this invariant non-negotiable, see [`specs/139-delivery-verified-not-documented/contracts/scope-guard-decision.md`](../../specs/139-delivery-verified-not-documented/contracts/scope-guard-decision.md).

---

### Release-Note Bullet Template

Adopters releasing a version that includes PRD 139 behavior can paste this bullet list into their changelog as-is. It covers the load-bearing user-visible changes: default gate flip, opt-out mechanism, autonomous parity, `--require-tests` deprecation, and heal-PR escalation. Customize wording for your audience; the five bullets below are the minimum required surface.

```markdown
### `/aod.deliver` Now Enforces Verification

- Delivery now halts by default when E2E tests fail (previously warn-only)
- Opt-out available via `--no-tests="<reason ≥10 chars>"` — reason is logged
- Autonomous mode halts identically; no autonomous-override exists
- `--require-tests` flag accepted silently for 2 release cycles (deprecation notice on stderr)
- Heal-PR opens on test failure with `e2e-heal` + `requires-review` labels
- See `docs/guides/DELIVERY_HARD_GATE_MIGRATION.md` for full migration
```

Use this alongside the longer [§Release notes bullet template](#release-notes-bullet-template) block above if you want both a concise user-facing note and a breaking-change banner.

---

### FAQ (Extended)

This expanded FAQ complements the [FAQ for adopters](#faq-for-adopters) section above with adopter-reported scenarios surfaced during rollout.

#### Q: My feature has flaky tests that auto-fix can't handle — what are my options?

A: You have three escape valves, listed here in recommended order (least-to-most drastic):

1. **Set `heal_attempts: 0`** in `.aod/config.json` — disables the auto-fix loop entirely. Failures escalate directly to a heal-PR without any automated patching attempts. Best when your flakes are transient and not worth the heal-loop wall-clock. Preserves the hard gate; the feature still halts and you still get a heal-PR, you just skip the 2-attempt auto-fix detour.

2. **Mark the specific AC(s) `[MANUAL-ONLY] <reason>`** in `spec.md` — most surgical. Only the flaky AC(s) skip scenario coverage; other ACs continue to gate normally. The `[MANUAL-ONLY]` ACs surface in the delivery document's Manual Validation section. Best when you know exactly which ACs have physically unautomatable parts.

3. **Opt out with `--no-tests="<reason ≥10 chars>"`** — most drastic. The gate is bypassed entirely for this single invocation, the reason is logged to `.aod/audit/deliver-opt-outs.jsonl`, delivery proceeds. Best when a whole feature has transient unfixable issues and you need to ship now. Use sparingly; each opt-out shows up in audit review.

Try option 1 first (preserves gate), then option 2 (most surgical), then option 3 (most drastic). Combining options is fine: `heal_attempts: 0` + per-AC `[MANUAL-ONLY]` is common for adopter projects with a known-flaky subsystem.

#### Q: What happens if I skip the migration and just keep using `--require-tests`?

A: Nothing breaks during the grace window. The flag is accepted as a silent no-op with a stderr deprecation notice on every invocation:

```
[deprecated] --require-tests is now default (v{CURRENT}); flag accepted but has no effect. Will be removed in v{REMOVAL}.
```

The grace window is **2 release cycles**. After that, the flag is removed entirely and passing it at invocation fails with exit code 2:

```
Error: --require-tests was removed in v{N+2}. The hard gate is now the default. See docs/guides/DELIVERY_HARD_GATE_MIGRATION.md.
```

So: no runtime break during the grace window. You have 2 release cycles to remove `--require-tests` from your scripts, CI workflows, and runbooks. After that, invocations that still pass it error out at argument parse (before any gate logic runs) with a pointer to this guide. No silent behavior change — the removal is a hard break with a clear error message.

#### Q: I have legacy prose ACs without Given/When/Then — do I need to rewrite my spec?

A: Yes. On the next `/aod.deliver` invocation, the strict AC parser fail-fasts with a pointer to [`docs/guides/AC_COVERAGE_MIGRATION.md`](./AC_COVERAGE_MIGRATION.md). The error message names the offending spec file and the first line that fails to parse.

Retrofit cost: ~5-15 minutes per spec depending on AC count. The sibling migration guide walks through the prose → Given/When/Then conversion pattern step-by-step with before/after examples.

Alternative: if you're delivering a feature right now and the retrofit is blocking, mark the whole feature `--no-tests="<reason: retrofitting AC parser, see docs/guides/AC_COVERAGE_MIGRATION.md>"` for one delivery. The opt-out is logged, delivery proceeds, and you retrofit the spec between this delivery and the next. Do not use the opt-out as a permanent workaround — the next `/aod.deliver` on the same feature will hit the same parse error.

#### Q: How do I track the grace period for `--require-tests` removal?

A: Two places tell you where you are in the grace window:

1. **The deprecation notice on stderr** — emitted on every invocation that passes `--require-tests`. It names the current version (`{CURRENT}`) and the removal version (`{REMOVAL}`). Run `/aod.deliver --require-tests` on any feature and inspect stderr:

   ```
   [deprecated] --require-tests is now default (v2.x+1); flag accepted but has no effect. Will be removed in v2.x+3.
   ```

   That line gives you both the current kit version and the planned removal version.

2. **Release notes for each AOD Kit release** — the kit's CHANGELOG records each release's behavior for the deprecation. Release N (this release) introduces the no-op; Release N+1 repeats the same behavior; Release N+2 removes the flag entirely.

The `{CURRENT}` and `{REMOVAL}` tokens resolve from `.aod/VERSION` (if present) or `git describe --tags --abbrev=0` as fallback. If neither source is readable, the notice prints `v? (unknown)` for the version fields but the deprecation message itself still appears. See [§Version token resolution](#version-token-resolution) above for the lookup chain.

Budget 2 releases of wall-clock time (not 2 of your own internal releases — the upstream kit's releases) to clean up `--require-tests` from your scripts.

#### Q: My team has CI that expects all tests to pass before merge. Does this change?

A: No. The PRD 139 change is **delivery-time enforcement**, not **merge-time enforcement**. Those are independent gates:

- **Merge-time gate** (your existing CI): runs on PR merge. Checks if tests pass before the branch merges to main. Unchanged by PRD 139.
- **Delivery-time gate** (PRD 139): runs when `/aod.deliver` is invoked on a completed feature. Checks if tests pass before the feature is marked Delivered in the lifecycle. New in PRD 139.

Both gates can exist simultaneously with no conflict. Your PR merge CI continues to work as before. `/aod.deliver` adds its own verification gate before transitioning the feature to Delivered status — this is independent of whether the underlying PR has merged yet.

Practical consequence: if your CI already enforces test passing at PR merge, you effectively have two independent verification checkpoints. Both must pass. This is additive, not a replacement. Adopters with strict merge-time CI still benefit from delivery-time enforcement because `/aod.deliver` also validates AC coverage, scope-guard compliance, and delivery-document completeness — none of which are typical merge-time CI checks.

---

**Last Updated**: 2026-04-23
**Maintained By**: Product Manager (delivery governance)
**Source**: Feature 139 — Delivery Means Verified, Not Documented
