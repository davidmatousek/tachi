#!/usr/bin/env bash
# LIBRARY — source before calling functions
# Heal-PR escalation for /aod.deliver. Creates draft PR on e2e-heal branch when
# auto-fix attempts exhaust. Idempotent across re-invocations.
# Bash 3.2 compatible.
#
# Canonical contracts:
#   specs/139-delivery-verified-not-documented/contracts/heal-pr-body.md
#   specs/139-delivery-verified-not-documented/plan.md §Research R-2 (+ architect M-1 patch)
#   specs/139-delivery-verified-not-documented/spec.md US-5 (FR-018..FR-023)
#
# Public functions:
#   compute_idem_key              — sha256(sorted scenario names)[0:16] + "-" + branch_sha[0:12]
#   find_existing_heal_pr         — locate open e2e-heal PR by idempotency-key HTML comment
#   create_heal_pr                — open draft heal-PR with rich body + labels
#   comment_on_existing           — post follow-up comment on existing heal-PR
#   post_create_uniqueness_check  — race-condition sanity check after creation
#   render_heal_pr_body           — render PR body per heal-pr-body.md contract
#
# Exit/return codes:
#   0   success
#   1   runtime error (jq/sha/gh missing, network, auth, etc.)
#   10  branch-deleted halt path (matches canonical halt exit from halt-signal.sh)
#
# IMPLEMENTATION NOTES (architect-mandated per plan M-1 patch):
#   find_existing_heal_pr uses `gh pr list --label ... --json ... | jq contains()` —
#   NOT `gh pr list --search`. The search API tokenizes word boundaries and strips
#   HTML, so it will not reliably match the `<!-- heal-pr-idem-key: ... -->` marker.
#
# Marker format (canonical per contracts/heal-pr-body.md):
#   <!-- heal-pr-idem-key: {16HEX}-{12HEX} -->
# The `heal-pr-` prefix disambiguates from any other idempotency-key comment
# style used elsewhere in AOD. Keep the library + contract + tests in lockstep.
#
# No-auto-merge invariant: this library NEVER invokes `gh pr merge` on any PR.
# Enforced externally by .aod/scripts/bash/check-no-merge-heal.sh (T035).

# Guard against re-source to avoid redefining globals in long-running shells.
if [[ -n "${AOD_HEAL_PR_SH_LOADED:-}" ]]; then
    return 0 2>/dev/null || true
fi
AOD_HEAL_PR_SH_LOADED=1

# Default heal-artifact fallback root (used when gh unavailable / branch deleted).
AOD_HEAL_RESULTS_DIR="${AOD_HEAL_RESULTS_DIR:-.aod/results}"

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

# Ensure jq is on PATH. Returns 0 if present, 1 otherwise (stderr: error msg).
_require_jq() {
    if ! command -v jq >/dev/null 2>&1; then
        echo "heal-pr.sh: jq not found on PATH" >&2
        return 1
    fi
    return 0
}

# Ensure shasum is on PATH. Returns 0 if present, 1 otherwise.
_require_shasum() {
    if ! command -v shasum >/dev/null 2>&1; then
        echo "heal-pr.sh: shasum not found on PATH" >&2
        return 1
    fi
    return 0
}

# Ensure gh is on PATH. Returns 0 if present, 1 otherwise.
_require_gh() {
    if ! command -v gh >/dev/null 2>&1; then
        echo "heal-pr.sh: gh CLI not found on PATH" >&2
        return 1
    fi
    return 0
}

# Extract NNN prefix from feature id. Example: "139-foo" -> "139".
_heal_feature_nnn() {
    local feature="${1:-}"
    printf '%s' "${feature%%-*}"
}

# Compact UTC timestamp for directory names (e.g., 20260423T143000Z).
_compact_utc_ts() {
    date -u +"%Y%m%dT%H%M%SZ"
}

# ISO-8601 UTC timestamp (e.g., 2026-04-23T14:30:00Z).
_iso_utc_ts() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# ---------------------------------------------------------------------------
# compute_idem_key
# ---------------------------------------------------------------------------
# Compute the idempotency key for a heal-PR.
#   IDEM_KEY = sha256( join("\n", sort(FAILING_SCENARIO_NAMES)) )[0:16]
#              + "-" + FEATURE_BRANCH_SHA[0:12]
#
# Args:
#   $1 scenarios_json     JSON array of scenario name strings (e.g., '["A","B"]')
#                         If omitted, reads from stdin.
#   $2 feature_branch_sha git SHA (any length >= 12)
#
# Outputs (stdout):
#   29-char key: 16 hex + "-" + 12 hex
#
# Returns:
#   0 on success
#   1 on jq/shasum missing, invalid JSON, or invalid branch SHA
compute_idem_key() {
    local scenarios_json="${1:-}"
    local branch_sha="${2:-}"

    _require_jq || return 1
    _require_shasum || return 1

    if [ -z "$branch_sha" ]; then
        echo "compute_idem_key: feature_branch_sha is required (second arg)" >&2
        return 1
    fi
    # Branch SHA must be >=12 chars so we can slice the prefix.
    if [ "${#branch_sha}" -lt 12 ]; then
        echo "compute_idem_key: feature_branch_sha must be >=12 chars (got ${#branch_sha})" >&2
        return 1
    fi

    # If no scenarios arg, read from stdin.
    if [ -z "$scenarios_json" ]; then
        scenarios_json=$(cat)
    fi

    # Validate + sort + join. jq fails loudly on invalid JSON.
    local joined
    joined=$(printf '%s' "$scenarios_json" | jq -r '. | sort | join("\n")' 2>/dev/null) || {
        echo "compute_idem_key: invalid JSON or non-array input" >&2
        return 1
    }

    # sha256 the joined string; take first 16 hex chars.
    local digest
    digest=$(printf '%s' "$joined" | shasum -a 256 | awk '{print $1}')
    if [ -z "$digest" ]; then
        echo "compute_idem_key: shasum produced no output" >&2
        return 1
    fi

    local hash_prefix="${digest:0:16}"
    local sha_prefix="${branch_sha:0:12}"

    printf '%s-%s' "$hash_prefix" "$sha_prefix"
    return 0
}

# ---------------------------------------------------------------------------
# find_existing_heal_pr
# ---------------------------------------------------------------------------
# Locate an open e2e-heal PR whose body contains the idempotency-key marker.
# Uses `gh pr list --label e2e-heal --state open --json number,url,body` then
# local jq contains() — per plan R-2 + architect M-1 patch. DO NOT use
# `gh pr list --search` (token boundaries strip HTML comments, breaking match).
#
# Args:
#   $1 idem_key  29-char idempotency key from compute_idem_key
#
# Outputs (stdout):
#   "<number> <url>" string if a match is found, else nothing. Format matches
#   contracts/heal-pr-body.md §Idempotency Lookup reference implementation.
#
# Returns:
#   0 on success (whether match found or not)
#   1 on gh missing, auth/network failure, or jq error
find_existing_heal_pr() {
    local idem_key="${1:-}"

    if [ -z "$idem_key" ]; then
        echo "find_existing_heal_pr: idem_key is required" >&2
        return 1
    fi
    _require_jq || return 1
    _require_gh || return 1

    local marker="<!-- heal-pr-idem-key: ${idem_key} -->"

    # Fetch open e2e-heal PRs. Bounded set; --limit 50 is a safety ceiling.
    local raw
    raw=$(gh pr list --state open --label e2e-heal --json number,url,body --limit 50 2>/dev/null) || {
        echo "find_existing_heal_pr: gh pr list failed (auth/network?)" >&2
        return 1
    }

    # jq: select PRs whose body contains the marker; emit first match as
    # "<number> <url>". Empty stdout means no match.
    local match
    match=$(printf '%s' "$raw" | jq -r --arg marker "$marker" '
        map(select(.body != null and (.body | contains($marker))))
        | if length > 0 then "\(.[0].number) \(.[0].url)" else empty end
    ' 2>/dev/null) || {
        echo "find_existing_heal_pr: jq failed to parse gh output" >&2
        return 1
    }

    if [ -n "$match" ]; then
        printf '%s\n' "$match"
    fi
    return 0
}

# ---------------------------------------------------------------------------
# render_heal_pr_body  (T033)
# ---------------------------------------------------------------------------
# Render a heal-PR body per contracts/heal-pr-body.md. Accepts a JSON object
# with fields per the contract and emits markdown to stdout.
#
# Args:
#   $1 body_fields_json  JSON object (stdin if omitted)
#
# Fields consumed:
#   .idem_key             (string, required)
#   .summary              (string, required)
#   .failing_scenarios[]  (array of {name, file, error})
#   .runner_log_tail      (string, may be empty)
#   .attempted_fixes[]    (array of {attempt, commit, description, outcome}; may be empty)
#   .scope_guard_rejection (object or null)
#   .artifacts[]          (array of path strings)
#   .invocation_context   (object {feature, invoker, timestamp, aod_version})
#
# Outputs:
#   Markdown body (stdout)
#
# Returns:
#   0 on success, 1 on jq missing / invalid JSON.
render_heal_pr_body() {
    local body_json="${1:-}"

    _require_jq || return 1

    if [ -z "$body_json" ]; then
        body_json=$(cat)
    fi

    # Extract scalar fields via jq. Use `// ""` / `// null` to tolerate missing keys.
    local idem_key summary runner_log_tail
    idem_key=$(printf '%s' "$body_json" | jq -r '.idem_key // ""') || return 1
    summary=$(printf '%s' "$body_json" | jq -r '.summary // ""') || return 1
    runner_log_tail=$(printf '%s' "$body_json" | jq -r '.runner_log_tail // ""') || return 1

    # Derive counts for Summary line.
    local n_failing n_attempts
    n_failing=$(printf '%s' "$body_json" | jq -r '(.failing_scenarios // []) | length')
    n_attempts=$(printf '%s' "$body_json" | jq -r '(.attempted_fixes // []) | length')

    # Failing Scenarios table rows.
    local scenarios_rows
    scenarios_rows=$(printf '%s' "$body_json" | jq -r '
        (.failing_scenarios // [])
        | map("| " + (.name // "") + " | " + (.file // "") + " | " + ((.error // "") | gsub("\n"; " ")) + " |")
        | .[]
    ' 2>/dev/null)

    # Attempted Fixes table rows (only when attempts exist).
    local attempts_rows
    attempts_rows=$(printf '%s' "$body_json" | jq -r '
        (.attempted_fixes // [])
        | map("| " + ((.attempt // 0) | tostring) + " | " + (.commit // "") + " | " + (.description // "") + " | " + (.outcome // "") + " |")
        | .[]
    ' 2>/dev/null)

    # Artifacts bullet list.
    local artifacts_bullets
    artifacts_bullets=$(printf '%s' "$body_json" | jq -r '
        (.artifacts // [])
        | map("- `" + . + "`")
        | .[]
    ' 2>/dev/null)

    # Scope-guard rejection (may be null/absent).
    local has_rejection rej_reason rej_rule rej_lines
    has_rejection=$(printf '%s' "$body_json" | jq -r 'if (.scope_guard_rejection // null) == null then "false" else "true" end')
    if [ "$has_rejection" = "true" ]; then
        rej_reason=$(printf '%s' "$body_json" | jq -r '.scope_guard_rejection.reason // ""')
        rej_rule=$(printf '%s' "$body_json" | jq -r '.scope_guard_rejection.rule // ""')
        rej_lines=$(printf '%s' "$body_json" | jq -r '(.scope_guard_rejection.violating_lines // []) | join("\n")')
    fi

    # Invocation context fields.
    local ic_feature ic_invoker ic_timestamp ic_aod_version
    ic_feature=$(printf '%s' "$body_json" | jq -r '.invocation_context.feature // ""')
    ic_invoker=$(printf '%s' "$body_json" | jq -r '.invocation_context.invoker // ""')
    ic_timestamp=$(printf '%s' "$body_json" | jq -r '.invocation_context.timestamp // ""')
    ic_aod_version=$(printf '%s' "$body_json" | jq -r '.invocation_context.aod_version // ""')

    # ---- Compose the body ----
    # 1. Idempotency-key HTML comment at the very top (canonical form per
    #    contracts/heal-pr-body.md: `<!-- heal-pr-idem-key: {KEY} -->`).
    printf '<!-- heal-pr-idem-key: %s -->\n\n' "$idem_key"

    # 2. Summary.
    printf '## Summary\n\n%s\n\n' "$summary"

    # 3. Failing Scenarios table.
    printf '## Failing Scenarios\n\n'
    printf '%s scenario(s) failed after %s auto-fix attempt(s):\n\n' "$n_failing" "$n_attempts"
    printf '| Scenario | File | Error |\n'
    printf '|----------|------|-------|\n'
    if [ -n "$scenarios_rows" ]; then
        printf '%s\n' "$scenarios_rows"
    fi
    printf '\n'

    # 4. Runner Log Tail.
    printf '## Runner Log Tail\n\n'
    printf '<details>\n<summary>Runner log (last 50 lines)</summary>\n\n'
    printf '```\n%s\n```\n\n</details>\n\n' "$runner_log_tail"

    # 5. Attempted Fixes (conditional).
    if [ -n "$attempts_rows" ]; then
        printf '## Attempted Fixes\n\n'
        printf '| Attempt | Commit | Description | Outcome |\n'
        printf '|---------|--------|-------------|---------|\n'
        printf '%s\n\n' "$attempts_rows"
    fi

    # 6. Scope Guard Rejection (conditional).
    if [ "$has_rejection" = "true" ]; then
        printf '## Scope Guard Rejection\n\n'
        printf 'The scope guard rejected a proposed fix.\n\n'
        if [ -n "$rej_rule" ]; then
            # Use `printf '%s\n' "..."` form: literal dash in the argument, not
            # the format string, avoids printf's `-` option parsing on bash 3.2.
            printf '%s\n' "- **Rule violated**: \`${rej_rule}\`"
        fi
        if [ -n "$rej_reason" ]; then
            printf '%s\n' "- **Reason**: ${rej_reason}"
        fi
        if [ -n "$rej_lines" ]; then
            printf '\n<details>\n<summary>Violating lines</summary>\n\n'
            printf '```\n%s\n```\n\n</details>\n' "$rej_lines"
        fi
        printf '\n'
    fi

    # 7. Test Artifacts bullet list.
    printf '## Test Artifacts\n\n'
    if [ -n "$artifacts_bullets" ]; then
        printf '%s\n\n' "$artifacts_bullets"
    else
        printf '_(no artifacts recorded)_\n\n'
    fi

    # 8. Next Steps — includes the verbatim no-auto-merge reminder.
    printf '## Next Steps\n\n'
    printf '1. Review the failing scenarios against the feature spec.\n'
    printf '2. Check each attempted fix — did auto-fix move in the right direction? Was the scope guard correct to reject?\n'
    printf '3. Resolve one of three ways:\n'
    printf '   - Fix the tests manually, push to this branch, re-run `/aod.deliver` on the feature branch.\n'
    printf '   - Fix the production code, push to the feature branch, then re-run.\n'
    printf '   - Mark the affected ACs `[MANUAL-ONLY] <reason>` in spec.md if the failure reveals a non-automatable acceptance criterion, then re-run.\n'
    printf '4. \xe2\x9a\xa0\xef\xb8\x8f Do NOT merge this PR with `gh pr merge`. Review fixes and either squash into feature branch manually or close.\n\n'

    # 9. Invocation Context table.
    printf '## Invocation Context\n\n'
    printf '| Field | Value |\n'
    printf '|-------|-------|\n'
    printf '| Feature | `%s` |\n' "$ic_feature"
    printf '| Invoker | `%s` |\n' "$ic_invoker"
    printf '| Timestamp | `%s` |\n' "$ic_timestamp"
    printf '| AOD version | `%s` |\n' "$ic_aod_version"
    printf '\n'

    return 0
}

# ---------------------------------------------------------------------------
# _compose_body_fields_from_env
# ---------------------------------------------------------------------------
# Compose the body_fields JSON consumed by render_heal_pr_body from the
# HEAL_PR_* environment variables. This is the shell-idiomatic interface for
# create_heal_pr: callers export the HEAL_PR_* names and invoke with just the
# 3 positional args (feature_branch, heal_branch, title).
#
# Required env vars:
#   HEAL_PR_SCENARIOS_JSON     JSON array of scenario-name strings or
#                              {name, file, error} objects. May be "[]".
#   HEAL_PR_RUNNER_LOG_TAIL    Runner log tail (may be empty string).
#   HEAL_PR_RECOVERY_STATUS    exhausted | recovered | escalated_to_heal_pr |
#                              scope_guard_escalated
#   HEAL_PR_INVOKER            email@host or "autonomous"
#
# Optional env vars (defaulted):
#   HEAL_PR_IDEM_KEY           Precomputed idempotency key. If unset, compute
#                              from HEAL_PR_SCENARIOS_JSON + HEAL_PR_FEATURE_BRANCH_SHA.
#   HEAL_PR_MODE               interactive (default) | autonomous
#   HEAL_PR_N_ATTEMPTS         "0"
#   HEAL_PR_TIMESTAMP          ISO-8601 UTC; defaulted to now
#   HEAL_PR_E2E_COMMAND        ""
#   HEAL_PR_MULTIPLIER         "1.0"
#   HEAL_PR_FEATURE_NAME       ""
#   HEAL_PR_ISSUE_NUMBER       ""
#   HEAL_PR_FEATURE_BRANCH     ""
#   HEAL_PR_FEATURE_BRANCH_SHA ""
#   HEAL_PR_HEAL_BRANCH        ""
#
# Outputs (stdout): compact JSON body_fields suitable for render_heal_pr_body.
# Returns: 0 on success, 1 on missing-required or jq error.
_compose_body_fields_from_env() {
    _require_jq || return 1

    # Required fields.
    local scenarios_json="${HEAL_PR_SCENARIOS_JSON:-}"
    local runner_log_tail="${HEAL_PR_RUNNER_LOG_TAIL:-}"
    local recovery_status="${HEAL_PR_RECOVERY_STATUS:-}"
    local invoker="${HEAL_PR_INVOKER:-}"
    local feature_branch="${HEAL_PR_FEATURE_BRANCH:-}"
    local branch_sha="${HEAL_PR_FEATURE_BRANCH_SHA:-}"

    if [ -z "$scenarios_json" ]; then
        echo "_compose_body_fields_from_env: HEAL_PR_SCENARIOS_JSON is required" >&2
        return 1
    fi
    if [ -z "$recovery_status" ]; then
        echo "_compose_body_fields_from_env: HEAL_PR_RECOVERY_STATUS is required" >&2
        return 1
    fi
    if [ -z "$invoker" ]; then
        echo "_compose_body_fields_from_env: HEAL_PR_INVOKER is required" >&2
        return 1
    fi

    # Optional / defaulted fields.
    local idem_key="${HEAL_PR_IDEM_KEY:-}"
    local mode="${HEAL_PR_MODE:-interactive}"
    local n_attempts="${HEAL_PR_N_ATTEMPTS:-0}"
    local timestamp="${HEAL_PR_TIMESTAMP:-$(_iso_utc_ts)}"
    local e2e_command="${HEAL_PR_E2E_COMMAND:-}"
    local multiplier="${HEAL_PR_MULTIPLIER:-1.0}"
    local feature_name="${HEAL_PR_FEATURE_NAME:-}"
    local issue_number="${HEAL_PR_ISSUE_NUMBER:-}"
    local heal_branch="${HEAL_PR_HEAL_BRANCH:-}"

    # Backfill idem_key if unset: compute from scenarios + branch_sha.
    if [ -z "$idem_key" ]; then
        if [ -n "$branch_sha" ]; then
            idem_key=$(compute_idem_key "$scenarios_json" "$branch_sha" 2>/dev/null) || {
                echo "_compose_body_fields_from_env: HEAL_PR_IDEM_KEY unset and compute_idem_key failed" >&2
                return 1
            }
        else
            echo "_compose_body_fields_from_env: HEAL_PR_IDEM_KEY unset and HEAL_PR_FEATURE_BRANCH_SHA unavailable to compute one" >&2
            return 1
        fi
    fi

    # Normalize failing_scenarios: accept either array-of-strings or
    # array-of-objects. Render objects verbatim; wrap strings into
    # {name, file, error} with empty file/error.
    local failing_scenarios_json
    failing_scenarios_json=$(printf '%s' "$scenarios_json" | jq -c '
        if type == "array" then
            map(
                if type == "string" then {name: ., file: "", error: ""}
                elif type == "object" then {
                    name: (.name // ""),
                    file: (.file // ""),
                    error: (.error // "")
                }
                else {name: (tostring), file: "", error: ""} end
            )
        else [] end
    ' 2>/dev/null) || {
        echo "_compose_body_fields_from_env: malformed HEAL_PR_SCENARIOS_JSON" >&2
        return 1
    }

    # Summary line — concise human prose; render_heal_pr_body composes the
    # surrounding header/sections.
    local n_failing
    n_failing=$(printf '%s' "$failing_scenarios_json" | jq -r 'length')
    local summary="Auto-fix loop for feature \`${feature_name}\` could not recover from test failures. Status: \`${recovery_status}\`. ${n_failing} scenario(s) failing after ${n_attempts} attempt(s). Invoked by \`${invoker}\` at \`${timestamp}\` (${mode} mode)."

    jq -c -n \
        --arg idem_key "$idem_key" \
        --arg summary "$summary" \
        --argjson failing_scenarios "$failing_scenarios_json" \
        --arg runner_log_tail "$runner_log_tail" \
        --arg feature "$feature_branch" \
        --arg feature_name "$feature_name" \
        --arg issue_number "$issue_number" \
        --arg heal_branch "$heal_branch" \
        --arg branch_sha "$branch_sha" \
        --arg invoker "$invoker" \
        --arg timestamp "$timestamp" \
        --arg mode "$mode" \
        --arg n_attempts "$n_attempts" \
        --arg e2e_command "$e2e_command" \
        --arg multiplier "$multiplier" \
        --arg recovery_status "$recovery_status" \
        '{
            idem_key: $idem_key,
            summary: $summary,
            failing_scenarios: $failing_scenarios,
            runner_log_tail: $runner_log_tail,
            attempted_fixes: [],
            scope_guard_rejection: null,
            artifacts: [],
            recovery_status: $recovery_status,
            invocation_context: {
                feature: $feature,
                feature_name: $feature_name,
                issue_number: $issue_number,
                heal_branch: $heal_branch,
                branch_sha: $branch_sha,
                invoker: $invoker,
                timestamp: $timestamp,
                mode: $mode,
                n_attempts: $n_attempts,
                e2e_command: $e2e_command,
                multiplier: $multiplier,
                aod_version: ""
            }
        }' || {
        echo "_compose_body_fields_from_env: jq failed to compose body fields" >&2
        return 1
    }
    return 0
}

# ---------------------------------------------------------------------------
# create_heal_pr
# ---------------------------------------------------------------------------
# Open a draft heal-PR on `heal_branch` based on `feature_branch`. Renders
# the body from HEAL_PR_* env vars (via _compose_body_fields_from_env) and
# invokes `gh pr create` with labels `e2e-heal,requires-review`.
#
# This is the shell-idiomatic interface: many body-rendering inputs (idem
# key, scenarios, runner log, invocation context) are passed via the
# HEAL_PR_* environment so the positional signature stays narrow.
#
# Fallback modes (both return non-zero with a local artifact dir):
#   - `gh` CLI not on PATH: write artifact dir, return 1
#   - feature_branch deleted on remote: write artifact dir, return 10
#
# Args:
#   $1 feature_branch    e.g., "139-delivery-verified-not-documented"
#   $2 heal_branch       e.g., "139-.....-heal-20260423T143000Z"
#   $3 title             PR title
#
# Env vars consumed: HEAL_PR_* (see _compose_body_fields_from_env)
#
# Outputs (stdout):
#   JSON object {"number": N, "url": "...", "mode": "created"} on success.
#   JSON object {"mode": "local_fallback", "artifact_dir": "..."} on any
#   fallback path (gh absent OR branch deleted).
#
# Returns:
#   0 on successful create
#   1 on gh missing (fallback) OR other unrelated gh failure
#   10 on branch-deleted halt path (caller propagates via halt-signal.sh)
create_heal_pr() {
    local feature_branch="${1:-}"
    local heal_branch="${2:-}"
    local title="${3:-}"

    _require_jq || return 1

    if [ -z "$feature_branch" ] || [ -z "$heal_branch" ] || [ -z "$title" ]; then
        echo "create_heal_pr: feature_branch, heal_branch, and title are required" >&2
        return 1
    fi

    # Compose body_fields from HEAL_PR_* env vars. Any required-var violation
    # surfaces here, before we touch git or gh.
    local body_fields_json
    body_fields_json=$(_compose_body_fields_from_env) || {
        echo "create_heal_pr: failed to compose body_fields from HEAL_PR_* env" >&2
        return 1
    }

    # Render the body once — used by both happy path and every fallback.
    local body
    body=$(render_heal_pr_body "$body_fields_json") || {
        echo "create_heal_pr: failed to render body" >&2
        return 1
    }

    # --- gh-absent fallback -------------------------------------------------
    # If `gh` is not on PATH we persist the artifact locally so the human can
    # still recover context, then return 1. This is NOT the branch-deleted
    # halt path — it's a degraded creation mode.
    if ! command -v gh >/dev/null 2>&1; then
        local nnn ts artifact_dir
        nnn=$(_heal_feature_nnn "$feature_branch")
        ts=$(_compact_utc_ts)
        artifact_dir="${AOD_HEAL_RESULTS_DIR}/heal-${nnn}-${ts}-$$"

        if ! mkdir -p "$artifact_dir" 2>/dev/null; then
            echo "create_heal_pr: gh CLI unavailable AND local artifact dir uncreatable at ${artifact_dir}" >&2
            return 1
        fi

        printf '%s\n' "$body" > "${artifact_dir}/heal-pr-body.md" 2>/dev/null || {
            echo "create_heal_pr: cannot write heal-pr-body.md to ${artifact_dir}" >&2
            return 1
        }
        printf '%s\n' "$body_fields_json" > "${artifact_dir}/heal-pr-fields.json" 2>/dev/null

        jq -c -n --arg dir "$artifact_dir" '{mode: "local_fallback", artifact_dir: $dir}'
        echo "create_heal_pr: gh CLI not on PATH; artifact written to ${artifact_dir}" >&2
        return 1
    fi

    # --- branch-deleted fallback -------------------------------------------
    # Verify feature_branch exists on remote. If not, fall back to local
    # artifact and signal halt-for-review (exit 10).
    if ! git ls-remote --exit-code --heads origin "$feature_branch" >/dev/null 2>&1; then
        local nnn ts artifact_dir
        nnn=$(_heal_feature_nnn "$feature_branch")
        ts=$(_compact_utc_ts)
        artifact_dir="${AOD_HEAL_RESULTS_DIR}/heal-${nnn}-${ts}-$$"

        if ! mkdir -p "$artifact_dir" 2>/dev/null; then
            echo "create_heal_pr: feature branch '${feature_branch}' missing on remote AND local artifact dir uncreatable at ${artifact_dir}" >&2
            return 1
        fi

        printf '%s\n' "$body" > "${artifact_dir}/heal-pr-body.md" 2>/dev/null || {
            echo "create_heal_pr: cannot write heal-pr-body.md to ${artifact_dir}" >&2
            return 1
        }
        printf '%s\n' "$body_fields_json" > "${artifact_dir}/heal-pr-fields.json" 2>/dev/null

        jq -c -n --arg dir "$artifact_dir" '{mode: "local_fallback", artifact_dir: $dir}'
        echo "create_heal_pr: feature branch '${feature_branch}' deleted on remote; artifact written to ${artifact_dir}" >&2
        return 10
    fi

    # --- happy path --------------------------------------------------------
    # Create the draft PR. `gh pr create` reads --head and --base against the
    # checked-out repo; the heal_branch must already be pushed to origin.
    # We do NOT do the push here — caller (SKILL.md Step 9c.5) owns commit+push.
    local create_out
    create_out=$(gh pr create \
        --draft \
        --base "$feature_branch" \
        --head "$heal_branch" \
        --title "$title" \
        --body "$body" \
        --label "e2e-heal" \
        --label "requires-review" \
        2>&1) || {
        echo "create_heal_pr: gh pr create failed: ${create_out}" >&2
        return 1
    }

    # gh pr create prints the URL on success. Fetch the PR number via gh pr view.
    local pr_url pr_number
    pr_url=$(printf '%s' "$create_out" | awk '/^https:\/\//{print; exit}')
    if [ -z "$pr_url" ]; then
        echo "create_heal_pr: could not extract PR url from gh output" >&2
        return 1
    fi

    pr_number=$(gh pr view "$pr_url" --json number --jq '.number' 2>/dev/null) || pr_number=""

    jq -c -n \
        --arg url "$pr_url" \
        --argjson number "${pr_number:-0}" \
        '{number: $number, url: $url, mode: "created"}'

    return 0
}

# ---------------------------------------------------------------------------
# comment_on_existing
# ---------------------------------------------------------------------------
# Post a follow-up comment on an existing heal-PR when a subsequent invocation
# surfaces the same failing state (idempotency match).
#
# Args:
#   $1 pr_number     GitHub PR number
#   $2 comment_body  Markdown string (should already include timestamp + context)
#
# Outputs (stdout):
#   JSON object {"number": N, "url": "..."} on success.
#
# Returns:
#   0 on success
#   1 on gh missing / gh failure
comment_on_existing() {
    local pr_number="${1:-}"
    local comment_body="${2:-}"

    _require_jq || return 1
    _require_gh || return 1

    if [ -z "$pr_number" ] || [ -z "$comment_body" ]; then
        echo "comment_on_existing: pr_number and comment_body are required" >&2
        return 1
    fi

    gh pr comment "$pr_number" --body "$comment_body" >/dev/null 2>&1 || {
        echo "comment_on_existing: gh pr comment failed for PR #${pr_number}" >&2
        return 1
    }

    # Resolve URL for the caller's convenience.
    local pr_url
    pr_url=$(gh pr view "$pr_number" --json url --jq '.url' 2>/dev/null) || pr_url=""

    jq -c -n \
        --argjson number "$pr_number" \
        --arg url "$pr_url" \
        '{number: $number, url: $url}'

    return 0
}

# ---------------------------------------------------------------------------
# post_create_uniqueness_check
# ---------------------------------------------------------------------------
# Post-hoc sanity check: re-query for PRs matching idem_key after a create.
# If >1 match, a concurrent heal attempt raced. Emits a warning on stderr
# naming every matching PR number. Never fails — this is advisory.
#
# Args:
#   $1 idem_key        29-char idempotency key
#   $2 new_pr_number   The PR we just created (for context in the warning)
#
# Outputs: (none on stdout; stderr warning if race detected)
#
# Returns: 0 always (advisory check)
post_create_uniqueness_check() {
    local idem_key="${1:-}"
    local new_pr_number="${2:-}"

    _require_jq || return 0
    _require_gh || return 0

    if [ -z "$idem_key" ]; then
        return 0
    fi

    local marker="<!-- heal-pr-idem-key: ${idem_key} -->"
    local raw
    raw=$(gh pr list --state open --label e2e-heal --json number,url,body --limit 50 2>/dev/null) || return 0

    local matches
    matches=$(printf '%s' "$raw" | jq -r --arg marker "$marker" '
        map(select(.body != null and (.body | contains($marker))))
        | map(.number | tostring)
        | join(", ")
    ' 2>/dev/null)

    # Count commas to infer match count (0-1 matches → no warning needed).
    if [ -z "$matches" ]; then
        return 0
    fi

    # If we see more than one number in the join, warn.
    case "$matches" in
        *,*)
            echo "WARN: heal-PR uniqueness check found multiple PRs for idem_key=${idem_key}: PRs [${matches}] (we just created #${new_pr_number}). Concurrent heal attempts likely raced; review and close duplicates." >&2
            ;;
    esac

    return 0
}

# ---------------------------------------------------------------------------
# Smoke-test crib (do not invoke in library load):
#   bash -c 'source .aod/scripts/bash/heal-pr.sh && compute_idem_key "[\"scenario1\",\"scenario2\"]" "abc123def456"'
#   expected: 29-char key (16 hex + "-" + 12 hex)
# ---------------------------------------------------------------------------
