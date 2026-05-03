---
description: Apply upstream template updates to this adopter project
---

## Purpose

Run the downstream template update pipeline: fetch the latest AOD-kit template from the pinned upstream, compute a categorized diff, preview what will change, and apply the approved set of changes atomically.

**Update direction is always**: `upstream → downstream`

## When to Use

- Periodic check for upstream template improvements (new commands, skills, docs).
- After a notable upstream release — confirm whether anything safe-to-adopt has landed.
- Before running `/aod.deliver` on a large feature if you want the latest tooling.

## When NOT to Use

- During an in-flight feature branch if you're worried about merge noise — do it between features.
- On a dirty working tree with uncommitted changes you care about — commit or stash first.

## Input

```
$ARGUMENTS
```

Common flag combinations:
- (no flags) — interactive TTY: preview, then confirm-to-apply.
- `--dry-run` — preview only; never writes.
- `--yes` — skip the confirmation prompt; still applies.
- `--edge` — fetch upstream `main` HEAD instead of latest tag (not recommended for production use).
- `--force-retag` — proceed even if the pinned tag has been retagged upstream (supply-chain override; logs a warning).
- `--upstream-url=<url>` — override the recorded upstream URL (must be `https://`).

## Step 1: Verify Bootstrap State

Check that the adopter project has been bootstrapped:

```bash
test -f .aod/aod-kit-version || { echo "Missing .aod/aod-kit-version — run scripts/init.sh first." ; exit 3; }
test -f .aod/personalization.env || { echo "Missing .aod/personalization.env — run scripts/init.sh first." ; exit 3; }
```

**If either file is missing**: Display setup instructions pointing at `scripts/init.sh` and **stop execution**.

## Step 2: Run the Update Pipeline

Invoke the CLI with the provided arguments:

```bash
scripts/update.sh $ARGUMENTS
```

Display the full output to the user so they can see the preview, confirmation prompt (if interactive), and per-operation apply log.

## Step 3: Interpret Exit Codes

The pipeline uses a stable exit-code contract (see `specs/129-downstream-template-update/contracts/cli-contract.md`):

| Code | Meaning | What to Report |
|------|---------|----------------|
| 0    | Success (or dry-run completed) | "Update complete" |
| 1    | Generic failure | Display stderr; suggest inspecting `.aod/update-tmp/` |
| 2    | Lock contention (another /aod.update is running) | "Another update in progress — wait or inspect holder PID" |
| 3    | Missing prerequisites | Point at `scripts/init.sh` bootstrap |
| 4    | Cross-filesystem staging | Suggest unsetting `AOD_UPDATE_TMP_DIR` |
| 5    | Manifest coverage violation | Upstream bug — escalate to upstream maintainers |
| 6    | Guard-list violation | Likely malicious manifest; review diff carefully |
| 7    | Retag detected without --force-retag | Review upstream tag history; re-run with --force-retag if intentional |
| 8    | Residual placeholder | Upstream introduced new `{{KEY}}`; escalate or edit personalization.env |
| 9    | Network failure | Suggest retry with network check |
| 10   | User declined preview | "Update cancelled; no changes applied." |

## Step 4: Show Final State (success only)

On exit code 0, show the updated version pin so the user can confirm:

```bash
cat .aod/aod-kit-version
```

## Step 5: Completion Report

Display a brief summary:

```
UPDATE COMPLETE

Direction: upstream → downstream
Mode:      <apply | dry-run>
Outcome:   <success | already up to date | declined | failed>
```

## Error Handling

| Scenario | Action |
|----------|--------|
| Missing `.aod/aod-kit-version` | Display bootstrap instructions, stop |
| Lock contention (exit 2) | Show holder PID from stderr, suggest retry |
| Cross-filesystem (exit 4) | Suggest `unset AOD_UPDATE_TMP_DIR` |
| Retag mismatch (exit 7) | Explain the supply-chain tripwire, offer `--force-retag` |
| Residual placeholder (exit 8) | Preserve staging for forensics; show `.aod/update-tmp/<uuid>/` |
| Network failure (exit 9) | Suggest checking connectivity and retrying |
| User declined (exit 10) | "Update cancelled; no changes applied." |

## References

- Full CLI contract: `specs/129-downstream-template-update/contracts/cli-contract.md`
- Manifest schema: `specs/129-downstream-template-update/contracts/manifest-schema.md`
- Version pin schema: `specs/129-downstream-template-update/contracts/version-schema.md`
- Adopter walkthrough: `docs/guides/DOWNSTREAM_UPDATE.md` (Wave 6)
