#!/usr/bin/env bash
# stack-contract-lint.sh
#
# Validates the machine-readable test contract block in stack pack STACK.md
# files. Contract block lives between the HTML sentinels:
#
#   <!-- BEGIN: aod-test-contract -->
#   ```yaml
#   <keys and values>
#   ```
#   <!-- END: aod-test-contract -->
#
# See: docs/stacks/TEST_COMMAND_CONTRACT.md
# Contract: specs/130-e2e-hard-gate/contracts/stack-contract-lint.md
# Schema:   specs/130-e2e-hard-gate/data-model.md §1, §2, §5
#
# Invocation:
#   bash stack-contract-lint.sh <path-to-STACK.md>   # single-file mode
#   bash stack-contract-lint.sh --all                # repo-wide mode
#   bash stack-contract-lint.sh --help               # usage
#
# Exit codes (STABLE FOREVER — do not repurpose):
#   0  VALID
#   1  RUNTIME_ERROR
#   2  MISSING_TEST_COMMAND (or e2e_opt_out below minimum length)
#   3  XOR_VIOLATION
#   4  UNKNOWN_KEY
#   5  MISSING_BLOCK
#
# Constraints:
#   - Bash 3.2 compatible (macOS /bin/bash). No bash-4+ constructs.
#   - POSIX tools only: awk, grep, sed. No yq/jq/pcregrep/python/ruby/perl.
#   - Deterministic: same input => same output.
#   - No filesystem writes.

set -u

# -----------------------------------------------------------------------------
# Exit-code constants (stable forever — see header; also reflected in --help).
# Using names instead of raw digits makes grep of violation sites trivial.
# -----------------------------------------------------------------------------
readonly EXIT_VALID=0
readonly EXIT_RUNTIME=1
readonly EXIT_MISSING_CMD=2
readonly EXIT_XOR=3
readonly EXIT_UNKNOWN_KEY=4
readonly EXIT_MISSING_BLOCK=5

# -----------------------------------------------------------------------------
# Content-pack allowlist (data-model §5).
# Packs listed here are skipped in --all mode; single-file mode ignores the list.
# Bash-3.2 indexed array — no associative arrays available.
# -----------------------------------------------------------------------------
CONTENT_PACKS=("knowledge-system")

# -----------------------------------------------------------------------------
# Migration-doc anchor constants (stderr "See:" lines)
# -----------------------------------------------------------------------------
DOC_BASE="docs/stacks/TEST_COMMAND_CONTRACT.md"
ANCHOR_TEST_CMD="#test-command"
ANCHOR_XOR="#xor-rule"
ANCHOR_ALLOWED_KEYS="#allowed-keys"
ANCHOR_MISSING_BLOCK="#contract-block"
ANCHOR_OPT_OUT_LEN="#opt-out-minimum-length"
ANCHOR_METACHAR="#wrapper-scripts"
ANCHOR_OPT_OUT_TRACKING="#opt-out-tracking"

# -----------------------------------------------------------------------------
# usage — prints to stdout, exits 0 (per contract --help)
# -----------------------------------------------------------------------------
usage() {
  cat <<'USAGE'
Usage: stack-contract-lint.sh [--all | --help | <path-to-STACK.md>]

Validates the test contract block in stack pack STACK.md files.

Modes:
  <path>   Validate a single STACK.md file. Exits with the code for that file.
  --all    Iterate every stacks/*/STACK.md (skipping the content-pack allowlist).
           Exits with the numerically lowest code across all non-allowlisted packs.
  --help   Print this usage and exit 0.

Exit codes:
  0  VALID
  1  RUNTIME_ERROR
  2  MISSING_TEST_COMMAND (or e2e_opt_out below minimum length)
  3  XOR_VIOLATION
  4  UNKNOWN_KEY
  5  MISSING_BLOCK

Diagnostic format (stderr):
  [aod-stack-contract] <file>:<line>: ERROR|WARN: <message>
  See: docs/stacks/TEST_COMMAND_CONTRACT.md[#anchor]
USAGE
}

# -----------------------------------------------------------------------------
# emit_diag — prints a single diagnostic line followed by a "See:" pointer.
# All diagnostic output flows through this function for uniformity.
#
#   $1 file        (path passed on CLI or stacks/<pack>/STACK.md)
#   $2 line        (1-based; 0 if file-level, no specific line)
#   $3 severity    ERROR | WARN
#   $4 message     human-readable
#   $5 anchor      migration-doc anchor, e.g. "#test-command" (may be empty)
# -----------------------------------------------------------------------------
emit_diag() {
  local file="$1"
  local line="$2"
  local severity="$3"
  local message="$4"
  local anchor="$5"

  echo "[aod-stack-contract] ${file}:${line}: ${severity}: ${message}" >&2
  if [ -n "${anchor}" ]; then
    echo "See: ${DOC_BASE}${anchor}" >&2
  else
    echo "See: ${DOC_BASE}" >&2
  fi
}

# -----------------------------------------------------------------------------
# find_sentinel_lines — locate BEGIN and END sentinels in one awk pass.
#
#   $1 file
# Prints "<begin_line> <end_line>" (space-separated). Each field is either
# a 1-based line number or "0" if the sentinel was not found. Guaranteed
# bash-3.2-safe single-pass output for callers to parse with `read`.
# -----------------------------------------------------------------------------
find_sentinel_lines() {
  awk '
    BEGIN { begin = 0; end = 0 }
    begin == 0 && /<!-- BEGIN: aod-test-contract -->/ { begin = NR }
    end == 0   && /<!-- END: aod-test-contract -->/   { end = NR }
    END { print begin, end }
  ' "$1" 2>/dev/null
}

# -----------------------------------------------------------------------------
# detect_nested_comment
#
# Returns 0 (true) if the contract block is wrapped in an outer HTML comment:
# an outer `<!--` appears on a line at or before the BEGIN sentinel without an
# intervening `-->`, AND a `-->` appears at or after the END sentinel without
# an intervening `<!--`.
#
# This is heuristic pattern detection — HTML comments cannot legally nest, so
# the outer wrapper is the author's explicit intent to disable the block and
# MUST be treated as MISSING_BLOCK (exit 5).
#
#   $1 file
#   $2 begin_line (1-based; must be > 0)
#   $3 end_line   (1-based; must be > 0)
# Returns 0 if nested (treat as missing), 1 otherwise.
#
# Implementation: single awk pass over the file. Counts `<!--`/`-->` occurrences
# per line via gsub. Exits early if pre-scan concludes no wrapper present.
# -----------------------------------------------------------------------------
detect_nested_comment() {
  local file="$1"
  local begin_line="$2"
  local end_line="$3"

  if [ "${begin_line}" -eq 0 ] || [ "${end_line}" -eq 0 ]; then
    return 1
  fi

  awk -v begin_line="${begin_line}" -v end_line="${end_line}" '
    BEGIN { pre_depth = 0; seen_close_only = 0 }

    # Pre-block scan (lines 1..begin_line-1): accumulate comment depth.
    NR < begin_line {
      opens  = gsub(/<!--/, "&")
      closes = gsub(/-->/,  "&")
      pre_depth += opens - closes
      next
    }

    # At BEGIN or inside the block — skip. (BEGIN sentinel itself is balanced.)
    NR <= end_line { next }

    # Post-block scan (lines end_line+1..EOF). Only meaningful if pre_depth > 0.
    pre_depth <= 0 { exit }
    {
      opens  = gsub(/<!--/, "&")
      closes = gsub(/-->/,  "&")
      # Close without matching open on this line → outer wrapper closes here.
      if (closes > opens) { seen_close_only = 1; exit }
      # Open without matching close → wrapper was already broken by content.
      if (opens > 0 && closes == 0) { exit }
    }

    END { exit !seen_close_only }
  ' "${file}" 2>/dev/null
}

# -----------------------------------------------------------------------------
# extract_block — runs awk range-match between the sentinels and prints the
# block body (including fence lines) to stdout.
#
#   $1 file
# Prints: zero lines if sentinels not found; otherwise the lines from BEGIN
# through END inclusive.
# -----------------------------------------------------------------------------
extract_block() {
  local file="$1"
  awk '/<!-- BEGIN: aod-test-contract -->/,/<!-- END: aod-test-contract -->/' "${file}"
}

# -----------------------------------------------------------------------------
# detect_unbalanced_quote
#
# Pre-pass YAML quote-balance check on the contract block. Walks each
# `key: value` line and checks whether a value that starts with `"` or `'`
# also ends with the matching character (after trimming trailing whitespace
# and comments). An unterminated quoted scalar is a YAML syntax error that
# the downstream key-parser cannot represent faithfully, so we flag it here
# and exit 1 (RUNTIME_ERROR) per contract.
#
# Inputs:
#   $1 block          — the extracted block body (multi-line string)
#   $2 begin_line     — 1-based line number of the BEGIN sentinel in the file
#   $3 file           — file path (for diagnostic emission)
#
# Returns:
#   0 if all quoted values are balanced (or no quoted values present)
#   1 if an unterminated quoted value is detected — caller should return 1
#
# Emits a single diagnostic (file:line format) on the first offending line.
# -----------------------------------------------------------------------------
detect_unbalanced_quote() {
  local block="$1"
  local begin_line="$2"
  local file="$3"
  local raw_line
  local offset_in_block=-1
  local file_line
  local value_part
  local first_char
  local last_char
  local trimmed

  while IFS= read -r raw_line; do
    offset_in_block=$((offset_in_block + 1))
    file_line=$((begin_line + offset_in_block))

    # Skip sentinel / fence / blank / comment lines — only inspect YAML
    # key:value content.
    case "${raw_line}" in
      *'<!-- BEGIN: aod-test-contract -->'*) continue ;;
      *'<!-- END: aod-test-contract -->'*)   continue ;;
      '```yaml'|'```yml'|'```') continue ;;
    esac
    if [ -z "$(printf '%s' "${raw_line}" | tr -d '[:space:]')" ]; then
      continue
    fi
    trimmed=$(printf '%s' "${raw_line}" | sed -E 's/^[[:space:]]+//')
    case "${trimmed}" in
      '#'*) continue ;;
    esac
    # Require a colon — lines without `key:` are not key:value declarations.
    case "${raw_line}" in
      *:*) ;;
      *) continue ;;
    esac

    # Value = everything after the first `:`, with leading whitespace removed
    # and trailing whitespace trimmed. We intentionally do NOT strip inline
    # `#` comments here — YAML comments inside quoted strings are literal,
    # and outside quoted strings they would require space-delimited `#`
    # which our harness fixtures do not exercise.
    value_part=$(printf '%s' "${raw_line}" | sed -E 's/^[^:]*:[[:space:]]*//')
    value_part=$(printf '%s' "${value_part}" | sed -E 's/[[:space:]]+$//')

    # Empty value is fine (e.g., `key:` with no RHS).
    if [ -z "${value_part}" ]; then
      continue
    fi

    # Extract first and last characters.
    first_char=$(printf '%s' "${value_part}" | cut -c1)
    last_char=$(printf '%s' "${value_part}" | awk '{print substr($0, length($0), 1)}')

    case "${first_char}" in
      '"'|"'")
        # Value opens with a quote — require the same terminator. If the
        # entire value is a single character that happens to be a quote,
        # that is also unterminated.
        if [ "${#value_part}" -lt 2 ] || [ "${first_char}" != "${last_char}" ]; then
          emit_diag "${file}" "${file_line}" "ERROR" \
            "unterminated quoted value — YAML syntax error" \
            ""
          return 1
        fi
        ;;
    esac
  done <<< "${block}"

  return 0
}

# -----------------------------------------------------------------------------
# validate_test_paths (PRD 139 extension)
#
# Validates the optional `test_paths` key inside the contract block. The key
# MUST be either absent (no-op) or a YAML block-style array-of-strings:
#
#   test_paths:
#     - "tests/"
#     - "e2e/"
#
# Rules (per specs/139-.../contracts/stack-pack-test-paths.md §"Lint Contract"):
#   - Absent            → no violation
#   - Scalar value      → "contract: test_paths must be an array"
#   - Inline JSON array → "contract: test_paths must be an array" (block form required)
#   - Empty block       → no violation (caller applies default globset)
#   - Non-string elem   → "contract: test_paths[N] must be a string, got {TYPE}"
#
# All violations reuse EXIT_UNKNOWN_KEY (4) per the stable taxonomy: unknown or
# invalid schema elements → 4. Emits diagnostics via emit_diag; on each
# violation, appends EXIT_UNKNOWN_KEY to the caller-local VIOLATION_CODES array.
#
# Inputs:
#   $1 block       — the extracted block body (multi-line)
#   $2 begin_line  — 1-based file line of BEGIN sentinel
#   $3 file        — file path (diagnostic output)
#
# Side effects:
#   Appends to caller-local VIOLATION_CODES via array-of-names workaround —
#   we cannot `declare -n` in bash 3.2, so the caller passes VIOLATION_CODES
#   by scope (lint_file declares it) and we mutate it directly. This mirrors
#   how the main parse loop handles UNKNOWN_KEYS.
#
# Returns: always 0 (violations are reported via VIOLATION_CODES, not $?).
# -----------------------------------------------------------------------------
validate_test_paths() {
  local block="$1"
  local begin_line="$2"
  local file="$3"

  local offset_in_block=-1
  local raw_line
  local file_line
  local trimmed
  local indent_len
  local label_rest
  local label_line=0
  local in_block=0
  local parent_indent=-1
  local elem_index=0
  local stripped
  local quoted
  local type_name
  local had_elements=0

  while IFS= read -r raw_line; do
    offset_in_block=$((offset_in_block + 1))
    file_line=$((begin_line + offset_in_block))

    # Skip sentinel / fence lines entirely — they carry no YAML.
    case "${raw_line}" in
      *'<!-- BEGIN: aod-test-contract -->'*) continue ;;
      *'<!-- END: aod-test-contract -->'*)   continue ;;
      '```yaml'|'```yml'|'```') continue ;;
    esac

    if [ "${in_block}" -eq 0 ]; then
      # Looking for the `test_paths:` label at column 0 (top-level YAML key).
      # Allow leading whitespace = 0 only; nested occurrences are not this key.
      case "${raw_line}" in
        'test_paths:'*)
          label_line="${file_line}"
          # Everything after "test_paths:" on the same line.
          label_rest=$(printf '%s' "${raw_line}" | sed -E 's/^test_paths:[[:space:]]*//')
          # Strip trailing whitespace.
          label_rest=$(printf '%s' "${label_rest}" | sed -E 's/[[:space:]]+$//')
          # Strip YAML inline comment (`# ...` that starts at a whitespace boundary
          # or at the start of the remainder). Use a conservative rule: drop from
          # the first ` #` or leading `#` to end of line.
          label_rest=$(printf '%s' "${label_rest}" | sed -E 's/[[:space:]]+#.*$//; s/^#.*$//')
          label_rest=$(printf '%s' "${label_rest}" | sed -E 's/[[:space:]]+$//')

          if [ -n "${label_rest}" ]; then
            # Reject inline JSON array `[...]` explicitly — PRD 139 requires
            # block form only (our line-scanner does not expand inline arrays).
            # Also rejects any scalar value (string, number, quoted, etc.).
            emit_diag "${file}" "${file_line}" "ERROR" \
              "contract: test_paths must be an array" \
              "${ANCHOR_ALLOWED_KEYS}"
            VIOLATION_CODES[${#VIOLATION_CODES[@]}]=${EXIT_UNKNOWN_KEY}
            # Stop processing — the key is malformed; do not attempt element
            # parsing on whatever follows (it may belong to the next key).
            return 0
          fi
          # Bare `test_paths:` with nothing after → enter block-collection mode.
          in_block=1
          parent_indent=-1
          elem_index=0
          had_elements=0
          continue
          ;;
      esac
      continue
    fi

    # We are inside the test_paths block, collecting `- <value>` lines.

    # Compute leading-whitespace length of the current line.
    trimmed=$(printf '%s' "${raw_line}" | sed -E 's/^[[:space:]]+//')
    indent_len=$(( ${#raw_line} - ${#trimmed} ))

    # Blank line — tolerate; do not end the block.
    if [ -z "${trimmed}" ]; then
      continue
    fi

    # Comment-only line — tolerate.
    case "${trimmed}" in
      '#'*) continue ;;
    esac

    # A line whose first non-whitespace char is NOT `-` terminates the block:
    # either a new top-level key (indent_len == 0) or a non-list content line.
    case "${trimmed}" in
      '-'|'- '*|'-'[[:space:]]*) : ;;
      *)
        in_block=0
        # Fall through to the outer scan logic by re-dispatching this line.
        # Simpler: check for a new `test_paths:` label here too.
        case "${raw_line}" in
          'test_paths:'*)
            # Extremely unlikely (duplicate declaration) — treat as a second
            # malformed occurrence to stay deterministic.
            emit_diag "${file}" "${file_line}" "ERROR" \
              "contract: test_paths must be an array" \
              "${ANCHOR_ALLOWED_KEYS}"
            VIOLATION_CODES[${#VIOLATION_CODES[@]}]=${EXIT_UNKNOWN_KEY}
            return 0
            ;;
        esac
        continue
        ;;
    esac

    # Lock in the parent indent on first element encountered.
    if [ "${parent_indent}" -lt 0 ]; then
      parent_indent="${indent_len}"
    fi

    # If this `-` sits at shallower indent than the first element, the block
    # has ended (unusual YAML, but handle defensively).
    if [ "${indent_len}" -lt "${parent_indent}" ]; then
      in_block=0
      continue
    fi

    had_elements=1

    # Strip leading "-" and subsequent whitespace to isolate the element value.
    stripped=$(printf '%s' "${trimmed}" | sed -E 's/^-[[:space:]]*//')
    # Trim trailing whitespace.
    stripped=$(printf '%s' "${stripped}" | sed -E 's/[[:space:]]+$//')

    # Detect whether the element was originally surrounded by quotes (single
    # or double). This is the "raw" type signal: quoted → explicit string.
    quoted=0
    case "${stripped}" in
      '"'*'"'|"'"*"'")
        # Require at least the two quote chars + any content between.
        if [ "${#stripped}" -ge 2 ]; then
          quoted=1
        fi
        ;;
    esac

    if [ "${quoted}" -eq 1 ]; then
      # Strip the surrounding quotes. Value is definitionally a string;
      # an empty string ("" or '') is still a valid string per YAML.
      stripped=$(printf '%s' "${stripped}" | sed -E 's/^"(.*)"$/\1/; s/^'\''(.*)'\''$/\1/')
      elem_index=$((elem_index + 1))
      continue
    fi

    # Unquoted element — YAML type inference kicks in. Reject known non-string
    # scalar forms: booleans, numerics, nulls, nested mappings, nested lists.
    type_name=""
    # Empty element `- ` alone → treat as empty string (odd but accept).
    if [ -z "${stripped}" ]; then
      elem_index=$((elem_index + 1))
      continue
    fi

    # Nested mapping: `- key: value` → we do not support map elements here.
    case "${stripped}" in
      *:*[[:space:]]*|*:)
        # Heuristic: `key:` at start with anything after (or nothing) →
        # mapping-valued element. Disallow.
        type_name="mapping"
        ;;
    esac

    if [ -z "${type_name}" ]; then
      # Nested inline sequence: starts with `[`.
      case "${stripped}" in
        '['*)
          type_name="sequence"
          ;;
      esac
    fi

    if [ -z "${type_name}" ]; then
      # Boolean literals (YAML 1.1 set, case-insensitive). Use tr for lowercasing
      # since bash 3.2 lacks ${var,,}.
      local lowered
      lowered=$(printf '%s' "${stripped}" | tr '[:upper:]' '[:lower:]')
      case "${lowered}" in
        true|false|yes|no|on|off)
          type_name="boolean"
          ;;
        null|'~')
          type_name="null"
          ;;
      esac
    fi

    if [ -z "${type_name}" ]; then
      # Numeric literal: integer or decimal. Guard with grep -E so we do not
      # need bash-4 regex. Leading `-` / `+` allowed.
      if printf '%s' "${stripped}" | grep -qE '^[+-]?[0-9]+(\.[0-9]+)?$'; then
        type_name="number"
      fi
    fi

    if [ -n "${type_name}" ]; then
      emit_diag "${file}" "${file_line}" "ERROR" \
        "contract: test_paths[${elem_index}] must be a string, got ${type_name}" \
        "${ANCHOR_ALLOWED_KEYS}"
      VIOLATION_CODES[${#VIOLATION_CODES[@]}]=${EXIT_UNKNOWN_KEY}
    fi

    # Regardless of validity, advance the index so subsequent diagnostics
    # correctly reference the list position.
    elem_index=$((elem_index + 1))
  done <<< "${block}"

  # Silence unused-var warnings for bookkeeping fields not used after loop.
  : "${label_line}" "${had_elements}"

  return 0
}

# -----------------------------------------------------------------------------
# lint_file — validate a single STACK.md file. Emits diagnostics to stderr and
# exits (via caller) with the numerically lowest violation code, or 0 on VALID.
#
#   $1 file
# Returns the exit code (does not exit the script).
# -----------------------------------------------------------------------------
lint_file() {
  local file="$1"

  # ---- Precondition: file exists and is readable ----
  if [ ! -f "${file}" ]; then
    emit_diag "${file}" 0 "ERROR" "file not found or not a regular file" ""
    return 1
  fi
  if [ ! -r "${file}" ]; then
    emit_diag "${file}" 0 "ERROR" "file not readable" ""
    return 1
  fi

  # Multi-violation collection. Bash 3.2 indexed array.
  VIOLATION_CODES=()

  # ---- Single-pass sentinel line lookup (replaces 4 separate grep passes) ----
  local begin_line=0
  local end_line=0
  read -r begin_line end_line <<< "$(find_sentinel_lines "${file}")"
  begin_line="${begin_line:-0}"
  end_line="${end_line:-0}"

  # ---- Nested-comment detection runs first ----
  if detect_nested_comment "${file}" "${begin_line}" "${end_line}"; then
    emit_diag "${file}" "${begin_line}" "ERROR" \
      "contract block is wrapped in an outer HTML comment — treated as missing; nested-comment-wrapping is not supported as a disable mechanism" \
      "${ANCHOR_MISSING_BLOCK}"
    return ${EXIT_MISSING_BLOCK}
  fi

  # ---- Missing-block shortcut: either sentinel absent ----
  if [ "${begin_line}" -eq 0 ] || [ "${end_line}" -eq 0 ]; then
    emit_diag "${file}" 0 "ERROR" "no aod-test-contract block found (expected sentinel-bracketed YAML in Section 7)" "${ANCHOR_MISSING_BLOCK}"
    return ${EXIT_MISSING_BLOCK}
  fi

  # ---- Block extraction ----
  local block
  block=$(extract_block "${file}")
  if [ -z "${block}" ]; then
    emit_diag "${file}" 0 "ERROR" "no aod-test-contract block found (expected sentinel-bracketed YAML in Section 7)" "${ANCHOR_MISSING_BLOCK}"
    return ${EXIT_MISSING_BLOCK}
  fi

  # ---- Pre-pass: YAML quote-balance check ----
  # An unterminated quoted scalar (e.g., `test_command: "npm run test`) is a
  # YAML syntax error. The downstream key-parser cannot represent such a
  # value faithfully, so flag it here as RUNTIME_ERROR (exit 1) per the
  # stable exit-code taxonomy. Must run BEFORE key parsing so we short-
  # circuit with a truthful diagnostic rather than silently coercing a
  # malformed value through the allowlist check.
  if ! detect_unbalanced_quote "${block}" "${begin_line}" "${file}"; then
    return 1
  fi

  # ---- Parse key:value pairs ----
  local TEST_COMMAND=""
  local E2E_COMMAND=""
  local E2E_OPT_OUT=""
  # Indexed arrays for unknown-key tracking.
  local UNKNOWN_KEYS=()
  local UNKNOWN_KEY_LINES=()

  # Line number of each seen key, for diagnostic output.
  local TEST_COMMAND_LINE=0
  local E2E_COMMAND_LINE=0
  local E2E_OPT_OUT_LINE=0

  # Walk the extracted block. awk emits inclusive of sentinel lines; skip them
  # plus the fence lines. Track the true file-line-number by adding the offset
  # of begin_line.
  local offset_in_block=-1
  local raw_line
  local key
  local value
  local file_line
  # Read the block via process-free redirection: a here-string of the block.
  # Bash 3.2 supports `<<<`.
  while IFS= read -r raw_line; do
    offset_in_block=$((offset_in_block + 1))
    file_line=$((begin_line + offset_in_block))

    # Skip sentinel and fence lines.
    case "${raw_line}" in
      *'<!-- BEGIN: aod-test-contract -->'*) continue ;;
      *'<!-- END: aod-test-contract -->'*)   continue ;;
      '```yaml'|'```yml'|'```') continue ;;
    esac

    # Skip pure blank / whitespace-only lines.
    case "${raw_line}" in
      ''|*[!\ \	]*) : ;;
    esac
    # If the line is only whitespace, skip.
    if [ -z "$(printf '%s' "${raw_line}" | tr -d '[:space:]')" ]; then
      continue
    fi

    # Skip YAML comment lines (# ...) — not part of the schema.
    case "${raw_line}" in
      '#'*|*[[:space:]]'#'*) : ;;
    esac
    # Leading-# comment:
    local trimmed_lead
    trimmed_lead=$(printf '%s' "${raw_line}" | sed -E 's/^[[:space:]]+//')
    case "${trimmed_lead}" in
      '#'*) continue ;;
    esac

    # Parse `key: value` — key is everything up to first `:`; value is
    # everything after, with surrounding whitespace + optional quotes stripped.
    # Uses awk so we do not rely on bash's `${var%...}`/`${var#...}` with
    # colons in values.
    case "${raw_line}" in
      *:*) ;;
      *)
        # Line has no colon; treat as malformed / unknown-key fodder. Emit only
        # if line has non-whitespace content. Skip silently otherwise.
        continue
        ;;
    esac
    key=$(printf '%s' "${raw_line}" | awk -F: '{print $1}' | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')
    # Everything after the first colon is the value. Use sed to grab it.
    value=$(printf '%s' "${raw_line}" | sed -E 's/^[^:]*:[[:space:]]*//')
    # Strip a single pair of surrounding double or single quotes.
    value=$(printf '%s' "${value}" | sed -E 's/^"(.*)"$/\1/; s/^'\''(.*)'\''$/\1/')
    # Strip trailing whitespace.
    value=$(printf '%s' "${value}" | sed -E 's/[[:space:]]+$//')

    case "${key}" in
      test_command)
        TEST_COMMAND="${value}"
        TEST_COMMAND_LINE="${file_line}"
        ;;
      e2e_command)
        E2E_COMMAND="${value}"
        E2E_COMMAND_LINE="${file_line}"
        ;;
      e2e_opt_out)
        E2E_OPT_OUT="${value}"
        E2E_OPT_OUT_LINE="${file_line}"
        ;;
      test_paths)
        # PRD 139 extension: recognized key. Shape validation (array-of-
        # strings) is performed separately by validate_test_paths() after the
        # main parse loop, which needs to re-walk the block to collect
        # array elements. Here we simply claim the key to keep it out of the
        # UNKNOWN_KEYS bucket.
        :
        ;;
      '')
        # Empty key (line was ":" with no key). Ignore.
        :
        ;;
      *)
        UNKNOWN_KEYS[${#UNKNOWN_KEYS[@]}]="${key}"
        UNKNOWN_KEY_LINES[${#UNKNOWN_KEY_LINES[@]}]="${file_line}"
        ;;
    esac
  done <<< "${block}"

  # ---- PRD 139: validate optional `test_paths` array-of-strings ----
  # Must run against the raw block (not post-parsed scalars) because the main
  # loop collapses multi-line YAML structures. validate_test_paths mutates
  # VIOLATION_CODES directly when violations are found.
  validate_test_paths "${block}" "${begin_line}" "${file}"

  # ---- Validation rules ----

  # Rule: test_command required (non-empty)
  if [ -z "${TEST_COMMAND}" ]; then
    emit_diag "${file}" "${begin_line}" "ERROR" "test_command is required" "${ANCHOR_TEST_CMD}"
    VIOLATION_CODES[${#VIOLATION_CODES[@]}]=${EXIT_MISSING_CMD}
  fi

  # Rule: e2e_opt_out minimum length (>=10 chars) when declared.
  # Reuses code 2 as "minimum completeness" per data-model §1.
  if [ -n "${E2E_OPT_OUT}" ]; then
    if [ "${#E2E_OPT_OUT}" -lt 10 ]; then
      emit_diag "${file}" "${E2E_OPT_OUT_LINE}" "ERROR" \
        "e2e_opt_out must be at least 10 characters" \
        "${ANCHOR_OPT_OUT_LEN}"
      VIOLATION_CODES[${#VIOLATION_CODES[@]}]=${EXIT_MISSING_CMD}
    fi
  fi

  # Rule: XOR between e2e_command and e2e_opt_out
  if [ -n "${E2E_COMMAND}" ] && [ -n "${E2E_OPT_OUT}" ]; then
    emit_diag "${file}" "${E2E_COMMAND_LINE}" "ERROR" \
      "must declare exactly one of e2e_command or e2e_opt_out (both present)" \
      "${ANCHOR_XOR}"
    VIOLATION_CODES[${#VIOLATION_CODES[@]}]=${EXIT_XOR}
  elif [ -z "${E2E_COMMAND}" ] && [ -z "${E2E_OPT_OUT}" ]; then
    emit_diag "${file}" "${begin_line}" "ERROR" \
      "must declare exactly one of e2e_command or e2e_opt_out (neither present)" \
      "${ANCHOR_XOR}"
    VIOLATION_CODES[${#VIOLATION_CODES[@]}]=${EXIT_XOR}
  fi

  # Rule: no unknown keys. Emit one diagnostic per unknown key.
  local idx=0
  while [ "${idx}" -lt "${#UNKNOWN_KEYS[@]}" ]; do
    emit_diag "${file}" "${UNKNOWN_KEY_LINES[$idx]}" "ERROR" \
      "unknown key '${UNKNOWN_KEYS[$idx]}' — allowed keys: test_command, e2e_command, e2e_opt_out" \
      "${ANCHOR_ALLOWED_KEYS}"
    VIOLATION_CODES[${#VIOLATION_CODES[@]}]=${EXIT_UNKNOWN_KEY}
    idx=$((idx + 1))
  done

  # ---- Non-fatal WARN rules (data-model §1) ----
  # These emit to stderr but do not contribute to VIOLATION_CODES, so they
  # never affect the exit code.

  # WARN: shell-chaining metacharacters in test_command or e2e_command.
  # Patterns checked: ';', '&&', '||', '|', backtick, '$('.
  if [ -n "${TEST_COMMAND}" ]; then
    if printf '%s' "${TEST_COMMAND}" | grep -qE '(&&|\|\||[|;`]|\$\()'; then
      emit_diag "${file}" "${TEST_COMMAND_LINE}" "WARN" \
        "test_command contains shell-chaining metacharacter — prefer a wrapper script" \
        "${ANCHOR_METACHAR}"
    fi
  fi
  if [ -n "${E2E_COMMAND}" ]; then
    if printf '%s' "${E2E_COMMAND}" | grep -qE '(&&|\|\||[|;`]|\$\()'; then
      emit_diag "${file}" "${E2E_COMMAND_LINE}" "WARN" \
        "e2e_command contains shell-chaining metacharacter — prefer a wrapper script" \
        "${ANCHOR_METACHAR}"
    fi
  fi

  # WARN: e2e_opt_out present but missing #NNN issue reference.
  # Only emit when length check did not already fail (length failure is
  # already flagged as ERROR above — avoid double noise).
  if [ -n "${E2E_OPT_OUT}" ] && [ "${#E2E_OPT_OUT}" -ge 10 ]; then
    if ! printf '%s' "${E2E_OPT_OUT}" | grep -qE '#[0-9]+'; then
      emit_diag "${file}" "${E2E_OPT_OUT_LINE}" "WARN" \
        "e2e_opt_out does not reference a #NNN issue" \
        "${ANCHOR_OPT_OUT_TRACKING}"
    fi
  fi

  # ---- Resolve final exit code ----
  if [ "${#VIOLATION_CODES[@]}" -eq 0 ]; then
    return 0
  fi

  # Numerically lowest applicable code (multi-violation resolution; data-model §2).
  local min="${VIOLATION_CODES[0]}"
  local i=1
  while [ "${i}" -lt "${#VIOLATION_CODES[@]}" ]; do
    if [ "${VIOLATION_CODES[$i]}" -lt "${min}" ]; then
      min="${VIOLATION_CODES[$i]}"
    fi
    i=$((i + 1))
  done
  return "${min}"
}

# -----------------------------------------------------------------------------
# is_content_pack — returns 0 if $1 (a pack directory basename) is in
# CONTENT_PACKS, 1 otherwise.
# -----------------------------------------------------------------------------
is_content_pack() {
  local candidate="$1"
  local i=0
  while [ "${i}" -lt "${#CONTENT_PACKS[@]}" ]; do
    if [ "${CONTENT_PACKS[$i]}" = "${candidate}" ]; then
      return 0
    fi
    i=$((i + 1))
  done
  return 1
}

# -----------------------------------------------------------------------------
# lint_all — iterate every stacks/*/STACK.md skipping content packs. Returns
# the minimum (numerically lowest) exit code across all non-allowlisted packs.
# -----------------------------------------------------------------------------
lint_all() {
  local min_code=0
  local stack_md
  local pack_dir
  local pack_name
  local code
  local saw_any=0

  # Iterate in sorted order for determinism. `for f in stacks/*/STACK.md`
  # preserves shell glob order (alphabetical on macOS/Linux).
  for stack_md in stacks/*/STACK.md; do
    # Handle the case where the glob does not match anything.
    if [ ! -f "${stack_md}" ]; then
      continue
    fi
    pack_dir=$(dirname "${stack_md}")
    pack_name=$(basename "${pack_dir}")
    if is_content_pack "${pack_name}"; then
      continue
    fi
    saw_any=1
    lint_file "${stack_md}"
    code=$?
    if [ "${code}" -ne 0 ]; then
      if [ "${min_code}" -eq 0 ] || [ "${code}" -lt "${min_code}" ]; then
        min_code="${code}"
      fi
    fi
  done

  # If no packs were linted (e.g., run from a directory without stacks/), that
  # is not an error — matches the contract "Exit 0 iff every non-allowlisted
  # pack validates" (vacuously true with zero packs).
  if [ "${saw_any}" -eq 0 ]; then
    return 0
  fi
  return "${min_code}"
}

# -----------------------------------------------------------------------------
# main — argument dispatch
# -----------------------------------------------------------------------------
main() {
  if [ "$#" -eq 0 ]; then
    usage >&2
    return 1
  fi

  case "$1" in
    --help|-h)
      usage
      return 0
      ;;
    --all)
      if [ "$#" -gt 1 ]; then
        echo "[aod-stack-contract] --all takes no additional arguments" >&2
        return 1
      fi
      lint_all
      return $?
      ;;
    --*)
      echo "[aod-stack-contract] unknown flag: $1" >&2
      usage >&2
      return 1
      ;;
    *)
      if [ "$#" -gt 1 ]; then
        echo "[aod-stack-contract] single-file mode takes exactly one argument" >&2
        return 1
      fi
      lint_file "$1"
      return $?
      ;;
  esac
}

main "$@"
exit $?
