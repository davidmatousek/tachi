#!/usr/bin/env bash
# LIBRARY — source before calling functions
# AC-coverage parser for /aod.deliver. Binds spec Given/When/Then ACs to E2E scenarios.
# Bash 3.2 compatible — no associative arrays, no readarray.
#
# Feature 139 — US-4 core library (task T026).
# Canonical contracts:
#   specs/139-delivery-verified-not-documented/spec.md US-4 (FR-006..FR-011)
#   specs/139-delivery-verified-not-documented/data-model.md §3 Acceptance Criterion Record
#   docs/guides/AC_COVERAGE_MIGRATION.md (legacy prose retrofit guidance)
#
# Public functions:
#   parse_acs_strict         — parse spec.md, emit JSON array of AC records
#   build_ac_scenario_map    — scan scenarios dir for @US-NN-AC-N tags, emit coverage map
#   emit_coverage_json       — pass-through compact JSON emitter
#
# Exit codes (library functions return, do NOT call exit):
#   0  success
#   2  spec path not found / unreadable
#   3  legacy prose ACs detected (non-empty spec with numbered AC items, zero strict)
#   4  [MANUAL-ONLY] marker has invalid reason (<10 chars or empty)
#   1  runtime error (jq missing, awk failure)

# Canonical AC identifier format: US-{NN}-AC-{N}
#   NN = zero-padded 2-digit user-story number (01, 02, ..., 99)
#   N  = 1-indexed AC ordinal within the enclosing user story
# Tag form (used in Gherkin @-tags and test-case tags): @US-NN-AC-N

# -----------------------------------------------------------------------------
# Environment overrides (for tests; production callers should leave alone)
# -----------------------------------------------------------------------------
# AOD_AC_MIGRATION_DOC — relative path surfaced in legacy-prose fail-fast
AOD_AC_MIGRATION_DOC="${AOD_AC_MIGRATION_DOC:-docs/guides/AC_COVERAGE_MIGRATION.md}"

# -----------------------------------------------------------------------------
# _ac_require_jq — defensive check; emits stderr hint + returns 1 if jq missing.
# -----------------------------------------------------------------------------
_ac_require_jq() {
    if ! command -v jq >/dev/null 2>&1; then
        echo "Error: jq is required for ac-coverage-parse" >&2
        return 1
    fi
    return 0
}

# -----------------------------------------------------------------------------
# _ac_awk_extract — single awk pass over spec.md.
#
# Emits US-separated (ASCII 0x1F, "Unit Separator") records of the form:
#   R<US>story<US>ac_idx<US>line<US>manual_flag<US>reason<US>given<US>when<US>then
# or:
#   M<US>strict_count<US>candidate_count                 (summary, always last)
#
# Why US and not TAB: bash `read` with IFS containing only whitespace
# characters (tab, space, newline) compresses consecutive separators into one,
# which would collapse empty fields (absent [MANUAL-ONLY] reason) and shift
# subsequent clause columns. US is non-whitespace and safe.
#
# Why one pass: keeps bash glue simple and deterministic; clause extraction
# runs entirely inside awk so per-AC overhead is negligible.
#
# Args:
#   $1 spec_md_path
# Stdout: see record format above.
# Stderr: nothing (caller composes error messages).
# Returns awk exit status.
# -----------------------------------------------------------------------------
_ac_awk_extract() {
    local spec_md="$1"
    awk '
    # extract_clause — helper that returns the text immediately following the
    # bold marker `**KEY**`, truncated at the next `**When**` / `**Then**`
    # keyword, with leading/trailing whitespace and leading comma/colon
    # trimmed. Empty string when the marker is absent.
    function extract_clause(line, marker,   i, rest, sep, cut) {
        i = index(line, "**" marker "**")
        if (i == 0) return ""
        rest = substr(line, i + length(marker) + 4)
        # Truncate at next bold clause marker (When or Then).
        if (marker != "Then") {
            sep = index(rest, "**Then**")
            if (sep > 0) rest = substr(rest, 1, sep - 1)
        }
        if (marker == "Given") {
            sep = index(rest, "**When**")
            if (sep > 0) rest = substr(rest, 1, sep - 1)
        }
        # Trim leading [,:\s]
        sub(/^[ \t]*[,:]?[ \t]*/, "", rest)
        # Trim trailing [., \t]+
        sub(/[ \t]*[,.]*[ \t]*$/, "", rest)
        return rest
    }

    # detect_manual — strip backtick-wrapped text first, then look for
    # [MANUAL-ONLY]. Returns the extracted reason (trimmed) or empty.
    function detect_manual(line,   stripped, i, rest, sep) {
        # Strip code spans so `[MANUAL-ONLY]` inside backticks is ignored.
        stripped = line
        gsub(/`[^`]*`/, "", stripped)
        i = index(stripped, "[MANUAL-ONLY]")
        if (i == 0) return ""
        rest = substr(stripped, i + 13)
        # Terminate at next bold clause keyword.
        sep = match(rest, /\*\*(Given|When|Then)\*\*/)
        if (sep > 0) rest = substr(rest, 1, sep - 1)
        # Terminate at first ". " sentence break.
        sep = match(rest, /\.[ \t]+/)
        if (sep > 0) rest = substr(rest, 1, sep - 1)
        # Trim leading [:,\s] and trailing [,.\s]+
        sub(/^[ \t]*[:,]?[ \t]*/, "", rest)
        sub(/[ \t]*[.,]*[ \t]*$/, "", rest)
        return rest
    }

    # strip_marker_from_clause — remove leading or trailing [MANUAL-ONLY]
    # metadata occurrences from clause prose (preserving backtick-wrapped
    # literals). Caller passes an already-extracted clause.
    function strip_marker(clause,   out) {
        out = clause
        # Leading: ^[MANUAL-ONLY] <reason>[.,]? <rest>  → strip
        sub(/^\[MANUAL-ONLY\][^.`]*\.[ \t]*/, "", out)
        # Trailing: <prose>[ \t]+[MANUAL-ONLY] <reason>$  → strip
        sub(/[ \t]+\[MANUAL-ONLY\][^`]*$/, "", out)
        return out
    }

    BEGIN {
        story_num = 0
        ac_index = 0
        strict_count = 0
        candidate_count = 0
    }

    # Track user-story heading transitions. Accept both `## User Story N` and
    # `### User Story N` variants.
    /^#+[[:space:]]+User Story[[:space:]]+[0-9]+/ {
        match($0, /User Story[[:space:]]+[0-9]+/)
        seg = substr($0, RSTART, RLENGTH)
        sub(/^User Story[[:space:]]+/, "", seg)
        story_num = seg + 0
        ac_index = 0
        next
    }

    # Strict AC line: starts with numbered list item AND **Given**.
    /^[0-9]+\.[[:space:]]+\*\*Given\*\*/ {
        ac_index += 1
        strict_count += 1
        given_text = strip_marker(extract_clause($0, "Given"))
        when_text  = strip_marker(extract_clause($0, "When"))
        then_text  = strip_marker(extract_clause($0, "Then"))
        reason = detect_manual($0)
        manual_flag = (reason == "") ? "false" : "true"
        # Emit compact record. Fields: R, story, ac_idx, line, manual_flag,
        # reason, given, when, then. Nine fields TAB-separated.
        print "R\037" story_num "\037" ac_index "\037" NR "\037" manual_flag "\037" reason "\037" given_text "\037" when_text "\037" then_text
        next
    }

    # [MANUAL-ONLY] Placement A at list start, with Given later on same line.
    /^[0-9]+\.[[:space:]]+\[MANUAL-ONLY\]/ {
        if (index($0, "**Given**") > 0) {
            ac_index += 1
            strict_count += 1
            given_text = strip_marker(extract_clause($0, "Given"))
            when_text  = strip_marker(extract_clause($0, "When"))
            then_text  = strip_marker(extract_clause($0, "Then"))
            reason = detect_manual($0)
            manual_flag = (reason == "") ? "false" : "true"
            print "R\037" story_num "\037" ac_index "\037" NR "\037" manual_flag "\037" reason "\037" given_text "\037" when_text "\037" then_text
            next
        }
        candidate_count += 1
        next
    }

    # Candidate legacy prose — numbered list item without Given.
    /^[0-9]+\.[[:space:]]/ {
        candidate_count += 1
        next
    }

    END {
        print "M\037" strict_count "\037" candidate_count
    }
    ' "$spec_md"
}

# -----------------------------------------------------------------------------
# _ac_extract_clause — pull the text following a bold-literal marker on an AC
# line. Returns the clause text trimmed of leading/trailing whitespace and any
# trailing comma that separated it from the next clause.
#
# Strategy (sed-based, bash-3.2-safe):
#   1. Strip everything up to and including the marker (e.g., `**Given**`).
#   2. Truncate at the first subsequent bold-literal marker token
#      (`**When**`, `**Then**`, `**And**`, `**But**`).
#   3. Trim surrounding whitespace, leading optional comma/colon, and trailing
#      punctuation like a final period.
#
# Args:
#   $1 ac_line   — raw AC body
#   $2 marker    — "Given" | "When" | "Then"
# Stdout: extracted clause (may be empty if the marker is missing).
# -----------------------------------------------------------------------------
_ac_extract_clause() {
    local line="$1"
    local marker="$2"

    # Drop everything up to and including the opening marker. If marker absent,
    # return empty — the caller's `case` check elsewhere handles per-clause
    # validity warnings. Combine all four edits (prefix strip, suffix truncate,
    # leading trim, trailing trim) in a single sed invocation to cut subshell
    # overhead (perf: this function runs 3x per AC; spec.md has 44 ACs).
    case "$line" in
        *"**${marker}**"*) ;;
        *)
            printf '%s' ""
            return 0
            ;;
    esac

    printf '%s' "$line" | sed -E \
        -e "s/^.*\\*\\*${marker}\\*\\*//" \
        -e 's/\*\*(When|Then)\*\*.*$//' \
        -e 's/^[[:space:]]*[,:]?[[:space:]]*//' \
        -e 's/[[:space:]]*[,.]*[[:space:]]*$//'
}

# -----------------------------------------------------------------------------
# _ac_detect_manual_only — inspect a raw AC line for the [MANUAL-ONLY] marker
# in either placement. Returns the reason (≥1 char, pre-validation) via stdout
# when present; empty stdout signals "not manual-only".
#
# Placement A: `1. [MANUAL-ONLY] <reason>. **Given** ...`
# Placement B: `1. **Given** [MANUAL-ONLY] <reason>. ..., **When** ...`
#
# For Placement A the reason runs from after `[MANUAL-ONLY]` up to but not
# including `**Given**`. For Placement B the reason runs from after
# `[MANUAL-ONLY]` up to the first `,` or `.` (reason terminator) within the
# Given clause — we extract until first sentence terminator OR the closing
# `**When**` boundary, whichever is earlier.
#
# Returns:
#   Prints the trimmed reason to stdout (may be empty or <10 chars; caller
#   validates).
# -----------------------------------------------------------------------------
_ac_detect_manual_only() {
    local line="$1"
    local stripped

    case "$line" in
        *"[MANUAL-ONLY]"*) ;;
        *)
            printf '%s' ""
            return 0
            ;;
    esac

    # Strip backtick-wrapped code spans so `[MANUAL-ONLY]` appearing as code
    # literal documentation (e.g. spec prose describing the feature) is
    # ignored. A real marker is bare text, not a code literal.
    stripped=$(printf '%s' "$line" | sed -E 's/`[^`]*`//g')

    case "$stripped" in
        *"[MANUAL-ONLY]"*) ;;
        *)
            printf '%s' ""
            return 0
            ;;
    esac

    # Reason extraction heuristic in a single sed pass — terminate at the
    # EARLIEST of:
    #   (a) the first `**Given**` / `**When**` / `**Then**` bold clause boundary
    #       (Placement A: marker precedes the Given line; Placement B: marker
    #       sits inside a clause)
    #   (b) the first `. ` sentence break followed by prose continuation
    #       (reason ends; subsequent prose is AC content)
    # The two trims strip leading punctuation/whitespace and trailing period/
    # comma/whitespace so the reason compares fairly against the 10-char floor.
    printf '%s' "$stripped" | sed -E \
        -e 's/^.*\[MANUAL-ONLY\]//' \
        -e 's/\*\*(Given|When|Then)\*\*.*$//' \
        -e 's/\.[[:space:]]+.*$//' \
        -e 's/^[[:space:]]*[:,]?[[:space:]]*//' \
        -e 's/[[:space:]]*[.,]*[[:space:]]*$//'
}

# -----------------------------------------------------------------------------
# parse_acs_strict — parse spec.md into a JSON array of AC records.
#
# Strict pattern: awk regex `^[0-9]+\. \*\*Given\*\*` matches AC list items.
# Each match is paired with the enclosing `## User Story N` / `### User Story N`
# heading's number (zero-padded to 2 digits) and its position within that
# story's AC list.
#
# Each AC record JSON shape:
#   {
#     "id": "US-01-AC-1",
#     "given": "<text>",
#     "when": "<text>",
#     "then": "<text>",
#     "manual_only": false,
#     "manual_reason": null
#   }
#
# Manual-only ACs set `manual_only: true` and `manual_reason` to the extracted
# reason string. Reasons shorter than 10 characters cause the function to emit
# an error to stderr naming the AC id and return exit code 4.
#
# Legacy prose fail-fast: if the spec contains numbered AC-like list items but
# zero match the strict Given/When/Then pattern, emit a migration pointer to
# stderr and return exit code 3.
#
# Args:
#   $1 spec_md_path
# Stdout: compact JSON array (possibly empty for specs with no ACs).
# Stderr: error messages on failure.
# Returns:
#   0  success (array emitted, even if empty)
#   1  runtime error (jq missing, awk failed, io error)
#   2  spec path missing / unreadable
#   3  legacy prose detected
#   4  [MANUAL-ONLY] reason invalid (<10 chars)
# -----------------------------------------------------------------------------
parse_acs_strict() {
    local spec_md="${1:-}"

    if [ -z "$spec_md" ]; then
        echo "Error: parse_acs_strict requires a spec path" >&2
        return 2
    fi

    if [ ! -f "$spec_md" ] || [ ! -r "$spec_md" ]; then
        echo "Error: spec file not found: ${spec_md}" >&2
        return 2
    fi

    _ac_require_jq || return 1

    # Accumulators. Bash 3.2 — parallel indexed arrays only.
    local ids=()
    local givens=()
    local whens=()
    local thens=()
    local manual_flags=()
    local manual_reasons=()

    local strict_count=0
    local candidate_count=0

    local extract_out
    extract_out=$(_ac_awk_extract "$spec_md" 2>/dev/null) || {
        echo "Error: awk parse failed for ${spec_md}" >&2
        return 1
    }

    # Walk the US-separated (ASCII 0x1F) record stream produced by
    # _ac_awk_extract. We use US rather than TAB because bash treats whitespace
    # IFS specially and compresses consecutive whitespace separators, which
    # would collapse empty fields (e.g., an absent [MANUAL-ONLY] reason) and
    # shift subsequent columns. US is non-whitespace so consecutive US
    # characters produce the correct number of empty fields.
    #
    # Record shape (9 fields, R-type):
    #   R<US>story<US>ac_idx<US>line<US>manual_flag<US>reason<US>given<US>when<US>then
    local record_type
    local story_num ac_index line_no manual_flag manual_reason
    local given_text when_text then_text
    local nn_padded id manual_len

    while IFS=$'\037' read -r record_type story_num ac_index line_no manual_flag manual_reason given_text when_text then_text; do
        case "$record_type" in
            R)
                # Guard against orphan ACs (strict match before any story
                # heading seen). Use story 00 to surface the anomaly loudly
                # rather than silently pretending it belonged to story 1.
                if [ "$story_num" -eq 0 ]; then
                    nn_padded="00"
                else
                    nn_padded=$(printf '%02d' "$story_num")
                fi
                id="US-${nn_padded}-AC-${ac_index}"

                # Validate [MANUAL-ONLY] reason length when a reason was
                # extracted. Empty reason + manual_flag=false is the normal
                # path; any non-empty reason must meet the 10-char floor.
                if [ "$manual_flag" = "true" ]; then
                    manual_len=${#manual_reason}
                    if [ "$manual_len" -lt 10 ]; then
                        echo "Error: ${id} has [MANUAL-ONLY] marker but reason is empty or <10 chars (got ${manual_len})" >&2
                        return 4
                    fi
                fi

                # An AC marked MANUAL-ONLY still lists Given/When/Then for
                # documentation; missing When or Then on a non-manual AC is a
                # parser-level warning but not a hard error here (data-model §3
                # says parse-error at AC level, not whole-spec).
                if [ "$manual_flag" = "false" ]; then
                    if [ -z "$when_text" ]; then
                        echo "Warning: ${id} has **Given** but no **When** (spec line ${line_no})" >&2
                    fi
                    if [ -z "$then_text" ]; then
                        echo "Warning: ${id} has **Given** but no **Then** (spec line ${line_no})" >&2
                    fi
                fi

                ids[${#ids[@]}]="$id"
                givens[${#givens[@]}]="$given_text"
                whens[${#whens[@]}]="$when_text"
                thens[${#thens[@]}]="$then_text"
                manual_flags[${#manual_flags[@]}]="$manual_flag"
                manual_reasons[${#manual_reasons[@]}]="$manual_reason"
                ;;
            M)
                # Summary record: fields 2 and 3 of the TSV carry strict_count
                # and candidate_count. Given the field rename (story_num,
                # ac_index), reuse those names here — semantics are per-type.
                strict_count="$story_num"
                candidate_count="$ac_index"
                ;;
            *)
                # Unknown record type — ignore defensively.
                :
                ;;
        esac
    done <<EOF
$extract_out
EOF

    # Legacy prose fail-fast: only trigger when candidate numbered items exist
    # AND the strict parser matched none of them. A spec with zero numbered
    # items (no AC section at all) is vacuously legal; a spec with 100%
    # strict-compliant items is the happy path.
    if [ "$strict_count" -eq 0 ] && [ "$candidate_count" -gt 0 ]; then
        echo "halt: ${spec_md} contains ${candidate_count} numbered acceptance-criterion items" >&2
        echo "      but 0 parse in strict Given/When/Then format." >&2
        echo "      This is a legacy spec requiring retrofit." >&2
        echo "      See: ${AOD_AC_MIGRATION_DOC}" >&2
        return 3
    fi

    # Build compact JSON array. To keep per-AC overhead low, emit all records
    # as a single US-separated stream and pipe once into jq. jq splits rows by
    # newline and each row by US (0x1F) — one subshell total rather than one
    # per AC (SC-005: 50 ACs in <500ms target).
    local n=${#ids[@]}
    local i=0

    if [ "$n" -eq 0 ]; then
        printf '[]\n'
        return 0
    fi

    # Produce rows of the form:
    #   id<US>given<US>when<US>then<US>manual_flag<US>reason
    # US (0x1F) is safe because AC text is plain prose; no well-formed markdown
    # spec contains the US control character.
    local us
    us=$(printf '\037')
    local tsv=""
    while [ "$i" -lt "$n" ]; do
        if [ -z "$tsv" ]; then
            tsv="${ids[$i]}${us}${givens[$i]}${us}${whens[$i]}${us}${thens[$i]}${us}${manual_flags[$i]}${us}${manual_reasons[$i]}"
        else
            tsv="${tsv}
${ids[$i]}${us}${givens[$i]}${us}${whens[$i]}${us}${thens[$i]}${us}${manual_flags[$i]}${us}${manual_reasons[$i]}"
        fi
        i=$((i + 1))
    done

    # jq -R reads raw rows, splits by US (), and builds one object per
    # row. `manual_reason` becomes JSON null when `manual_flag` is literal
    # "false"; otherwise it is a non-empty string by construction.
    printf '%s\n' "$tsv" | jq -R -s -c '
        split("\n")
        | map(select(length > 0))
        | map(split(""))
        | map({
            id: .[0],
            given: .[1],
            when: .[2],
            then: .[3],
            manual_only: (.[4] == "true"),
            manual_reason: (if .[4] == "true" then .[5] else null end)
        })
    ' || {
        echo "Error: jq failed to build AC JSON array" >&2
        return 1
    }

    return 0
}

# -----------------------------------------------------------------------------
# _ac_scan_all_tags — single-pass scan of a scenarios directory for every
# `@US-NN-AC-N` tag occurrence across `.feature`, `.test.{ts,tsx,js,jsx}`,
# `.spec.{ts,tsx,js,jsx}` files.
#
# Emits TAB-separated records to stdout:
#   <ac_id><TAB><path>:<line_no>
# One record per (tag, file, line). Records are sorted by ac_id then by path.
# Callers filter by ac_id with `awk -F\t -v id=...` or grep.
#
# Why one pass: individual per-AC scans cost one find+grep invocation each —
# cumulative cost grows O(ACs × files). A single walk costs O(files) and
# scales flat with AC count (SC-005: sub-500ms for 50 ACs).
#
# Args:
#   $1 scenarios_dir
# Returns: 0 always (empty stdout signals no tags anywhere).
# -----------------------------------------------------------------------------
_ac_scan_all_tags() {
    local dir="$1"
    if [ -z "$dir" ] || [ ! -d "$dir" ]; then
        return 0
    fi

    # Single find → grep -rn for the prefix `@US-`. Then awk parses each line
    # to extract `ac_id`, validate the tag terminator (no prefix collision
    # between AC-1 and AC-10), and emit `ac_id<TAB>path:line` records.
    find "$dir" -type f \
        \( -name '*.feature' \
        -o -name '*.test.ts' \
        -o -name '*.test.tsx' \
        -o -name '*.test.js' \
        -o -name '*.test.jsx' \
        -o -name '*.spec.ts' \
        -o -name '*.spec.tsx' \
        -o -name '*.spec.js' \
        -o -name '*.spec.jsx' \) \
        -print0 2>/dev/null \
    | xargs -0 grep -n -H -F '@US-' 2>/dev/null \
    | awk '
        # Input format: path:lineno:content
        # Extract ac_ids matching the canonical form @US-NN-AC-N, bounded by
        # a non-identifier character (or end of line) to avoid prefix
        # collisions between AC-1 and AC-10.
        {
            # Parse leading "path:lineno:" — allow colons inside path if awk
            # pattern finds them. Conservatively split on the first two
            # colons from the right by parsing back from the first match
            # position.
            line = $0
            n = 0
            # Find all @US-XX-AC-N occurrences with non-identifier boundary.
            while (match(line, /@US-[0-9]+-AC-[0-9]+/)) {
                token = substr(line, RSTART, RLENGTH)
                after = substr(line, RSTART + RLENGTH, 1)
                if (after == "" || after !~ /[A-Za-z0-9_-]/) {
                    # Extract ac_id (drop leading "@").
                    ac_id = substr(token, 2)
                    # Reconstruct file:line prefix. grep -H prints
                    # "file:lineno:content"; take the part before the second
                    # colon.
                    prefix = ""
                    first_colon = index($0, ":")
                    if (first_colon > 0) {
                        rest = substr($0, first_colon + 1)
                        second_colon = index(rest, ":")
                        if (second_colon > 0) {
                            prefix = substr($0, 1, first_colon + second_colon - 1)
                        }
                    }
                    if (prefix != "") {
                        print ac_id "\t" prefix
                    }
                }
                # Advance past this match.
                line = substr(line, RSTART + RLENGTH)
            }
        }
    ' \
    | sort -u
}

# -----------------------------------------------------------------------------
# build_ac_scenario_map — walk AC array JSON and build a coverage map.
#
# Output JSON shape:
#   {
#     "total_acs": <int>,
#     "covered_count": <int>,
#     "uncovered_acs": [<id>, ...],
#     "manual_only_acs": [<id>, ...],
#     "coverage_by_ac": [
#       {"ac_id": "<id>", "scenarios": ["<path:line>", ...], "manual_only": <bool>}
#     ]
#   }
#
# `covered_count` counts ACs with ≥1 scenario match OR `manual_only: true`.
#
# Args:
#   $1 acs_json       — JSON array (stdout format of parse_acs_strict). Pass
#                       `-` to read from stdin.
#   $2 scenarios_dir  — root directory to scan for tagged scenario files.
# Stdout: compact JSON map.
# Returns:
#   0 success
#   1 runtime error (jq missing, malformed acs_json)
# -----------------------------------------------------------------------------
build_ac_scenario_map() {
    local acs_json_arg="${1:-}"
    local scenarios_dir="${2:-}"

    _ac_require_jq || return 1

    # Resolve acs_json source — literal value or stdin.
    local acs_json
    if [ "$acs_json_arg" = "-" ] || [ -z "$acs_json_arg" ]; then
        acs_json=$(cat)
    else
        acs_json="$acs_json_arg"
    fi

    # Validate input is a JSON array.
    if ! printf '%s' "$acs_json" | jq -e 'type == "array"' >/dev/null 2>&1; then
        echo "Error: build_ac_scenario_map requires a JSON array as acs_json" >&2
        return 1
    fi

    # Scan the scenarios directory once, producing a tag→file:line index.
    local tags_index=""
    if [ -n "$scenarios_dir" ] && [ -d "$scenarios_dir" ]; then
        tags_index=$(_ac_scan_all_tags "$scenarios_dir")
    fi

    # Delegate map construction to a single jq program. jq receives:
    #   - acs_json as stdin
    #   - tags_index as --arg (multi-line string, TAB-separated rows)
    # and emits the canonical coverage object. Performing everything in jq
    # eliminates the per-AC shell loop (was O(ACs) jq invocations).
    printf '%s' "$acs_json" | jq -c \
        --arg tags_index "$tags_index" \
        '
        # Parse tags_index into {ac_id: [scenarios...]} map.
        ($tags_index
         | split("\n")
         | map(select(length > 0))
         | map(split("\t"))
         | map({key: .[0], value: .[1]})
         | group_by(.key)
         | map({key: .[0].key, value: [.[].value]})
         | from_entries
        ) as $by_id
        | map(
            . as $ac
            | {
                ac_id: $ac.id,
                scenarios: ($by_id[$ac.id] // []),
                manual_only: $ac.manual_only
              }
          )
        | {
            total_acs: length,
            covered_count: map(select(.manual_only == true or (.scenarios | length) > 0)) | length,
            uncovered_acs: map(select(.manual_only == false and (.scenarios | length) == 0) | .ac_id),
            manual_only_acs: map(select(.manual_only == true) | .ac_id),
            coverage_by_ac: .
          }
        ' || {
        echo "Error: jq failed to build coverage map" >&2
        return 1
    }

    return 0
}

# -----------------------------------------------------------------------------
# emit_coverage_json — pass-through emitter. Reads a coverage map (arg or
# stdin) and prints it as compact JSON. Callers pipe this to a gate-decision
# script in SKILL Step 9a.5.
#
# Args:
#   $1 map_json   — JSON object (or `-` / empty to read stdin)
# Stdout: compact JSON on success.
# Returns:
#   0 success
#   1 malformed input
# -----------------------------------------------------------------------------
emit_coverage_json() {
    local map_arg="${1:-}"
    local map

    _ac_require_jq || return 1

    if [ "$map_arg" = "-" ] || [ -z "$map_arg" ]; then
        map=$(cat)
    else
        map="$map_arg"
    fi

    if ! printf '%s' "$map" | jq -c -e '.' >/dev/null 2>&1; then
        echo "Error: emit_coverage_json received malformed JSON" >&2
        return 1
    fi

    printf '%s' "$map" | jq -c '.'
    return 0
}
