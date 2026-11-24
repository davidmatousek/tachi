"""Shared parser module for tachi pipeline artifacts.

Provides deterministic parsers for markdown tables, YAML frontmatter, severity
distributions, findings, scope data, and compensating controls extracted from
tachi pipeline outputs (threats.md, risk-scores.md, compensating-controls.md).

Used by extract-report-data.py and extract-infographic-data.py to ensure
consistent, cross-output-identical parsing of the same source artifacts.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, Iterator, Optional, Sequence, Tuple

# The reference-set reader below checks IDs against tachi_parts' allow-list. A sibling is found beside this file,
# whether this module is imported flat (`tachi_parsers`) or as `scripts.tachi_parsers` (ADR-050 D3, C1).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tachi_parts  # noqa: E402

# =============================================================================
# Shared Constants
# =============================================================================

# Exit codes
EXIT_SUCCESS = 0
EXIT_MISSING_ARTIFACT = 1
EXIT_VALIDATION_FAILURE = 2

# Severity ordering for deterministic output
SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Note"]

# STRIDE prefix mapping for coverage matrix derivation
STRIDE_PREFIXES = {
    "S-": "Spoofing",
    "T-": "Tampering",
    "R-": "Repudiation",
    "I-": "Information Disclosure",
    "D-": "Denial of Service",
    "E-": "Elevation of Privilege",
    "AG-": "Agentic Threats",
    "LLM-": "LLM Threats",
}

# Severity ordinal for numeric comparison (Critical highest)
SEVERITY_ORDINAL = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Note": 0}

# Canonical MAESTRO layer ordering (L1 through L7)
MAESTRO_LAYERS = ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]

# K10 (FR-K10.1): the "Risk by MAESTRO Layer" heading at level 3 or 4 (some inputs render "###", not "####").
MAESTRO_LAYER_HEADING = r"^#{3,4}\s+Risk by MAESTRO Layer"

# Canonical CSA MAESTRO agentic pattern enum values (Feature 142, schema 1.4).
# Ordering mirrors schemas/finding.yaml agentic_pattern.enum. The first six are
# the canonical CSA patterns; "none" is the sentinel for findings without
# pattern relevance (default per FR-017); "multiple" covers findings that
# exemplify two or more patterns with equal classification-rule priority.
# See ADR-026 for the classification mechanism and
# .claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md
# for the canonical definitions.
VALID_AGENTIC_PATTERNS = (
    "agent_collusion",
    "emergent_behavior",
    "temporal_attack",
    "trust_exploitation",
    "communication_vulnerability",
    "resource_competition",
    "none",
    "multiple",
)

# Closed asset-sensitivity tag enum consumed by the risk-scorer's CVSS impact-bit
# floor pass (see schemas/risk-scoring.yaml -> asset_modifiers and
# .claude/skills/tachi-risk-scoring/references/asset-modifiers.md). Tags are
# normalized to lowercase before comparison; unknown tags are dropped with a
# stderr warning and never reach the modifier table.
VALID_ASSET_TAGS = (
    "pii",
    "phi",
    "auth",
    "secrets",
    "financial",
    "safety",
)


# =============================================================================
# Utility Functions
# =============================================================================

def escape_typst_string(s: str) -> str:
    """Escape a string for Typst string literals.

    Handles: backslash -> \\, double quote -> \", newline -> \\n
    """
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    s = s.replace("\n", "\\n")
    return s


def strip_bold(s: str) -> str:
    """Strip markdown bold markers (**) from a string."""
    return s.replace("**", "")


# D3's one closed decoder (F-374, ADR-050). It is built from the constant that the escapers use, never from a
# second list, so it reverses exactly the references ``tachi_parts.escape_cell`` and ``escape_prose`` write. No
# reference is a prefix of another (each ends at its first ``;``), so the order of the alternatives doesn't matter.
_REFERENCE_PATTERN = re.compile("|".join(re.escape(reference) for reference in tachi_parts.ESCAPE_REFERENCES))


def decode_references(text: str) -> str:
    """Decode the references ``tachi_parts`` escapes, and nothing else (ADR-050 D3, "Output").

    The closed set is ``tachi_parts.ESCAPE_REFERENCES``: ``&amp;``, ``&lt;``, ``&gt;``, ``&#124;``, ``&#96;``,
    ``&#123;``, ``&#10;``, ``&#35;`` and ``&#126;``. It is one left-to-right pass, and replaced text is never scanned again, so
    ``&amp;lt;`` is ``&lt;`` and a second decode would be a bug. Anything else is left as written: another entity,
    a hex or zero-padded numeric reference, a bare ``&`` and GFM's ``\\|`` (which would change how today's examples
    parse, NFR-1).

    Run it once on a value, after the row it came from is split on raw ``|``. A row can't split on a reference,
    because no reference holds a ``|``. :func:`parse_markdown_table` and every other reader of rendered text decode
    each value they return, so a caller of those never decodes it again. ``decode_references(escape_cell(text))``
    and ``decode_references(escape_prose(text))`` are ``text``, with or without ``keep_slots``.
    """
    return _REFERENCE_PATTERN.sub(lambda match: tachi_parts.ESCAPE_REFERENCES[match.group(0)], text)


def _parse_int(s: str) -> int:
    """Safely parse an integer from a string, stripping non-numeric chars."""
    match = re.search(r"\d+", s)
    return int(match.group()) if match else 0


# =============================================================================
# K9/K11 Shared Score and Header Helpers (Feature 373)
# =============================================================================

def parse_score(s) -> "Decimal | None":
    """Parse a table-cell score string into a ``Decimal``, or ``None`` on failure.

    Catches ``decimal.InvalidOperation`` (NOT a ``ValueError`` subclass),
    ``ValueError``, ``TypeError`` and ``AttributeError``, and rejects
    non-finite results (``NaN``, ``Infinity``) even though
    ``Decimal("NaN")`` parses without raising. Used for every score in the
    controls and risk-scores parsers (data-model.md §3); a ``None`` return
    is the caller's cue to count the cell toward its own aggregated
    "unparseable score" warning class — this function never prints
    anything itself, and never raises: ``None`` or any other non-string
    input (T036 L-5 — ``s.strip()`` has no fallback on an object with no
    ``.strip()`` method) returns ``None`` exactly like an unparseable
    string, rather than propagating an ``AttributeError``.
    """
    try:
        d = Decimal(s.strip())
    except (InvalidOperation, ValueError, TypeError, AttributeError):
        return None
    if not d.is_finite():
        return None
    return d


def _warn_aggregated(ids, what, consequence):
    """One stderr line per warning class: the count plus the first five IDs (R-P6, data-model.md §3); silent when empty."""
    if ids:
        print(f"Warning: {len(ids)} {what} (first: {', '.join(ids[:5])}); {consequence}", file=sys.stderr)


# Alias table for Coverage Matrix headers (FR-K9.1, data-model.md §3). Built
# from ``normalize_header``'s output (casefold, strip one trailing '.',
# collapse whitespace) so both the long and short forms resolve to the same
# canonical field. "Inherent Score"/"Inherent" and "Control Status"/"Status"
# are consumed starting with K11 (T020); "Residual Score"/"Residual" and
# "Residual Severity"/"Residual Sev." are consumed from K9 (T016) on.
HEADER_ALIASES = {
    "residual score": "residual_score",
    "residual": "residual_score",
    "residual severity": "residual_severity",
    "residual sev": "residual_severity",
    "inherent score": "inherent_score",
    "inherent": "inherent_score",
    "control status": "control_status",
    "status": "control_status",
}


def normalize_header(h: str) -> str:
    """Normalize a markdown table header for :data:`HEADER_ALIASES` lookup.

    casefold, strip exactly one trailing '.', then collapse internal
    whitespace runs to a single space (data-model.md §3).
    """
    h = (h or "").strip().casefold()
    if h.endswith("."):
        h = h[:-1]
    return re.sub(r"\s+", " ", h).strip()


def _resolve_row_fields(row: dict) -> dict:
    """Resolve a Coverage Matrix row's header-aliased fields (data-model.md §3).

    Returns a dict keyed by canonical name (``residual_score``,
    ``residual_severity``, ``inherent_score``, ``control_status``), reading
    whichever spelling — long or short form — the row actually carries via
    :data:`HEADER_ALIASES`, plus ``inherent_severity`` (K11): the literal
    ``Inherent Severity`` fallback column, which has no short form and so is
    not in the alias table. A canonical field with no matching column in
    this row resolves to ``""``. ``Threat ID``, ``Component`` and ``Threat``
    are read directly by the caller.
    """
    resolved = {name: "" for name in set(HEADER_ALIASES.values())}
    resolved["inherent_severity"] = ""
    for key, value in row.items():
        normalized = normalize_header(key)
        canonical = HEADER_ALIASES.get(normalized)
        if canonical is not None:
            resolved[canonical] = value
        elif normalized == "inherent severity":
            resolved["inherent_severity"] = value
    return resolved


# K8's added Section 2 cells and the carried-forward marker (FR-K8.1, R-20), read by header name like every other column.
# The pre-fix format has CF but neither of the two others, and a drifted file can mix the two schemas between bands.
_K8_COLUMNS = {"maestro layer": "maestro_layer", "control category": "control_category", "cf": "cf"}


def _resolve_k8_fields(row: dict) -> dict:
    """The K8 cells of a Coverage Matrix row, by canonical name: ``maestro_layer``, ``control_category`` and ``cf``.

    A cell comes back as the table gives it (stripped and decoded), and ``""`` when the row's table has no such column,
    as the pre-fix format has none of the first two.
    """
    fields = {"maestro_layer": "", "control_category": "", "cf": ""}
    for key, value in row.items():
        canonical = _K8_COLUMNS.get(normalize_header(key))
        if canonical is not None:
            fields[canonical] = value.strip()
    return fields


_PLACEHOLDER_ID_RE = re.compile(r"[-–—]+")


def is_placeholder_id(s: str) -> bool:
    """Return True when ``s`` is an empty or dash-only placeholder ID.

    A placeholder is an empty string after stripping, or a run of one or
    more ASCII hyphen / en dash / em dash characters (data-model.md §3, §6;
    FR-K9.2, FR-K12.3). Placeholder rows are dropped before dedup.
    """
    stripped = (s or "").strip()
    return stripped == "" or bool(_PLACEHOLDER_ID_RE.fullmatch(stripped))


_HEADING_RE = re.compile(r"^(#{1,6})\s")


def _heading_level(line: str):
    """Return a stripped line's heading level (count of leading '#'), or None."""
    m = _HEADING_RE.match(line)
    return len(m.group(1)) if m else None


def _fence_marker(line: str):
    """``(character, run length, rest of the line)`` of the code-fence marker that starts ``line``, or ``None``.

    A marker is a run of three or more backticks or tildes after spaces and tabs only (no other whitespace character
    leads a fence, as in ``tachi_scoring_rules._outline``). The run is the whole run of that one character, and the rest
    is what follows it.
    """
    stripped = line.lstrip(" \t")
    char = stripped[:1]
    if char != "`" and char != "~":
        return None
    run = len(stripped) - len(stripped.lstrip(char))
    return (char, run, stripped[run:]) if run >= 3 else None


def _unfenced_lines(lines: Sequence[str]) -> Iterator[Tuple[int, str]]:
    """``(index, line)`` of each line that no fenced code block covers, in order. A fence line is covered, and so is every line up to
    the one that closes it. This is the one fence rule of :func:`match_heading` (``outside_fences=True``, whose docstring states it)
    and of :func:`parse_finding_layers`, so a section and a table are found outside a fence by the same reading."""
    fence = None  # (character, run length) of the fence that is open
    for index, line in enumerate(lines):
        marker = _fence_marker(line)
        if fence is not None:
            if marker is not None and marker[0] == fence[0] and marker[1] >= fence[1] and not marker[2].strip(" \t\r"):
                fence = None
            continue
        if marker is not None and not (marker[0] == "`" and "`" in marker[2]):
            fence = marker[:2]
            continue
        yield index, line


def match_heading(pattern: str, text: str, *, outside_fences: bool = False) -> Optional[int]:
    """Return the 0-indexed line number of the first line matching ``pattern``.

    ``pattern`` is matched with ``re.MULTILINE`` (``^``/``$`` anchor to each
    line), so it should itself be a line-anchored regex, e.g.
    ``r"^#{3,4}\\s+Risk by MAESTRO Layer"`` (K10) or
    ``r"^##\\s+4[bc]\\.\\s+Resolved Findings\\s*$"`` (K12). Returns ``None``
    when there is no match. The return value is a line index compatible with
    :func:`parse_markdown_table`'s ``start_line`` argument, not a character
    offset.

    ``outside_fences`` (F-374, ruled at W3 from T087's observation) is for a reader whose result a renderer's from-disk
    check or the next run relies on. A heading-like line in a fenced code block, such as an evidence snippet that quotes
    a tachi report, is then not a heading. The text is split on ``\\n`` only, and each line outside a fence is searched
    on its own, so ``^`` and ``$`` anchor to that line. Every line of a fenced block is skipped, the fence lines
    included:

    * a fence opens on a run of three or more backticks or tildes after spaces and tabs only, and a backtick run with
      another backtick later on its line opens none;
    * it closes only on a run of the same character that is at least as long as the opener's, followed by nothing but
      spaces, tabs or a carriage return;
    * a fence that nothing closes runs to the end of the text, so no heading after it is found.

    The default is the one search over the whole text that this function always was, so every caller that doesn't
    ask is unchanged.
    """
    if not outside_fences:
        m = re.search(pattern, text, re.MULTILINE)
        if not m:
            return None
        return text.count("\n", 0, m.start())
    wanted = re.compile(pattern)
    for index, line in _unfenced_lines(text.split("\n")):
        if wanted.search(line):
            return index
    return None


# K11's Control Status classifier (data-model.md §3; FR-K11.3, spec ruling
# S-5). Application order matters: a token starting "partial" wins first,
# then the recognized no-control set (silent), then "found" with no
# negation token, then anything else (including empty) warns.
_CONTROL_STATUS_SILENT_SET = frozenset({
    "no control found", "missing", "none", "not found",
})
_CONTROL_STATUS_NEGATION_TOKENS = frozenset({"no", "not", "none", "nothing"})


def classify_control_status(s: str):
    """Classify a Control Status cell into ("found"|"partial"|"none", warn).

    Whole-token, case-insensitive (data-model.md §3):
      1. a token starting "partial" (e.g. "partial", "partially") -> partial;
      2. the normalized status in the recognized no-control set ("no control
         found", "missing", "none", "not found") -> none, silently;
      3. a "found" token with no negation token ("no"/"not"/"none"/"nothing")
         -> found;
      4. anything else, including empty -> none, with a warning.

    Called once per row at parse time; the result replaces both copies of
    the row idiom (the STRIDE coverage matrix derivation and the coverage
    fallback). The Section 1 summary reader keeps its own matching.
    """
    normalized = (s or "").strip().casefold()
    tokens = normalized.split()

    if any(tok.startswith("partial") for tok in tokens):
        return "partial", False

    if normalized in _CONTROL_STATUS_SILENT_SET:
        return "none", False

    if "found" in tokens and not (set(tokens) & _CONTROL_STATUS_NEGATION_TOKENS):
        return "found", False

    return "none", True


def parse_finding_pattern(value) -> str:
    """Normalize an ``agentic_pattern`` cell value to a canonical enum string.

    Accepts string, None, or missing input and returns one of the values in
    ``VALID_AGENTIC_PATTERNS``. Null, whitespace, em-dash placeholder, ASCII
    dash, and unrecognized strings all collapse to ``"none"`` so pre-schema-1.4
    inputs without a Pattern column parse cleanly. Case-insensitive; canonical
    storage is always lowercase.
    """
    if value is None:
        return "none"
    normalized = str(value).strip().lower()
    if not normalized or normalized in ("\u2014", "-"):
        return "none"
    if normalized in VALID_AGENTIC_PATTERNS:
        return normalized
    return "none"


# Distinctive phrase signatures of the two MAESTRO zero-finding tokens (Feature
# 311, ADR-047 D1). Matched on the normalized phrase (dash + whitespace folded,
# lowercased) \u2014 NOT on punctuation: the markdown cell carries no trailing
# period, but the Typst prose literal appends one downstream, so keying on the
# phrase keeps the classifier stable across both surfaces (contract INV-2).
_MAESTRO_NA_SIGNATURE = "not applicable"
_MAESTRO_CLEAN_SIGNATURE = "analyzed"


def classify_maestro_coverage_state(finding_count: int, highest_severity: str) -> str:
    """Classify a MAESTRO layer row into its coverage state from the carried cell.

    Reads ONLY the already-authored Section-6 values (``Finding Count`` and the
    free-text ``Highest Severity`` token). Does NOT read Section 1 and does NOT
    decide applicability \u2014 it classifies the orchestrator's decision into the
    ``coverage_state`` enum both extractors emit (ADR-047 D2). Pure and
    side-effect-free.

    Mapping (contract ``coverage-state-classifier.contract.md``):
      * ``finding_count > 0`` \u2192 ``"findings"`` (regardless of severity);
      * ``finding_count == 0`` and the n/a phrase ``"Not applicable \u2014 no
        components map to this layer"`` \u2192 ``"not_applicable"``;
      * ``finding_count == 0`` and the clean phrase ``"Analyzed \u2014 no findings
        this scan"`` \u2192 ``"clean"``;
      * ``finding_count == 0`` and empty / unrecognized \u2192 ``"clean"`` (table-less
        backfill default; INV-4 \u2014 never silently ``"findings"``).

    Dash tolerance (INV-2): U+2014 (em) and U+2013 (en) and surrounding
    whitespace are folded before matching, mirroring the populator's read
    robustness; trailing punctuation is ignored.

    Returns exactly one of: ``"findings"`` | ``"clean"`` | ``"not_applicable"``.
    """
    if finding_count > 0:
        return "findings"
    # Fold em/en dash to a hyphen and collapse whitespace so the match keys on
    # the phrase, not the punctuation (INV-2). Mirrors _layer_id_of's dash
    # handling in populate-maestro-coverage.py.
    normalized = (highest_severity or "").replace("\u2014", "-").replace("\u2013", "-")
    normalized = re.sub(r"\s+", " ", normalized).strip().lower()
    if _MAESTRO_NA_SIGNATURE in normalized:
        return "not_applicable"
    # Clean is the explicit Model-A phrase AND the catch-all for empty /
    # unrecognized zero-finding cells (INV-4): a zero-finding layer is never
    # silently promoted to "findings".
    return "clean"


# =============================================================================
# Generic Table Parsers
# =============================================================================

def _escaped_pipe_cells(line: str) -> list:
    """The cells of a table ``line`` between its first and last ``|``, each as the line writes it (not stripped, not decoded), with GFM's
    escaped pipe read as GFM reads it: a ``|`` that an odd run of backslashes ends is a pipe inside its cell, and the backslash that
    escapes it is dropped (cmark-gfm's ``unescape_pipes``). A ``|`` that an even run ends, none included, still ends the cell, because a
    backslash that another backslash escapes escapes nothing.

    This is ``line.split("|")[1:-1]`` for a line with no ``\\|`` in it, so the two readings differ only where a cell holds one
    (``parse_markdown_table``'s ``escaped_pipes`` chooses between them, and its callers decode each cell, D3).

    The pipes are walked with ``str.find`` and each is checked by counting the backslashes before it, so the cost is one pass over the
    line and never a pattern that backtracks over a run of backslashes (a hostile row can be as long as the file allows).
    """
    cells = []
    start = at = 0
    while True:
        pipe = line.find("|", at)
        if pipe < 0:
            cells.append(line[start:])
            break
        run = 0
        while pipe - run > start and line[pipe - run - 1] == "\\":
            run += 1
        if run % 2:   # escaped: the pipe stays in its cell
            at = pipe + 1
            continue
        cells.append(line[start:pipe])
        start = at = pipe + 1
    return [cell.replace("\\|", "|") for cell in cells[1:-1]]


def parse_markdown_table(content: str, section_header: str = None, start_line: int = None, skipped: list = None,
                         row_lines: list = None, keep_bold: bool = False, overlong: list = None, escaped_pipes: bool = False) -> list:
    """Parse a markdown table found after a section header.

    Args:
        content: Full markdown file content.
        section_header: The section header to search for (e.g., "## 6. Risk Summary"),
            matched as a substring anywhere on a line. Ignored when ``start_line``
            is given.
        start_line: A 0-indexed line number to start scanning from directly —
            typically the return value of :func:`match_heading` — so a regex
            match never falls back to a substring re-search (data-model.md §3,
            rev. 1). Callers must pass ``section_header`` or ``start_line``;
            ``[]`` is returned when ``section_header`` matches nothing.
        skipped: An optional list. When given, the 1-based line number of each
            row dropped as malformed (fewer cells than the header) is appended
            to it, so a caller that can't afford to lose a row (the F-374
            reference set) can tell. The default leaves every caller unchanged.
        row_lines: An optional list. When given, the 1-based line number of each *returned* row is appended to
            it, in step with the returned rows, so a caller that reports a problem with one row (the Section 4a
            reader) can name its line. The default leaves every caller unchanged.
        keep_bold: When true, a data cell keeps its ``**`` markers. A cell holds a persisted value as written there
            (the controls ``recommendation_body`` is markdown with bold labels), so a reader of the persisted-inputs
            tables asks for them kept. The default strips them, as it always has.
        overlong: An optional list. When given, the 1-based line number of each *returned* row that has more cells than
            the header row is appended to it. Such a row keeps its first cells and loses the rest, as it always has,
            and a stray ``|`` (or GFM's ``\\|``, unless ``escaped_pipes``) has already shifted every value after it. A
            caller that can't afford a shifted value (the F-374 reference set) reads the list and refuses the file.
            The default leaves every caller unchanged.
        escaped_pipes: When true, a ``|`` that GFM escapes (``\\|``) is a pipe inside its cell and not the end of it, and the
            cell holds the pipe without the backslash, as GFM renders it. A ``|`` after an even run of backslashes still ends the
            cell. The header row is read by the same rule as the rows under it, so both count their cells alike. The default splits
            at every ``|``, as it always has (NFR-1), and the F-374 reference set's Section 7 reader alone asks for the other reading
            (P1-3, ADR-050 D3): the per-finding tables and every extractor keep the default.

    Returns:
        List of dicts, one per row, with keys from the header row.
        Returns empty list if table not found.

    Each header and data cell is stripped, loses its ``**`` markers (unless ``keep_bold``) and is then decoded with
    :func:`decode_references` (ADR-050 D3), after the row is split on raw ``|``. So the renderers' references
    (``&#124;`` for a ``|`` in a cell, ``&lt;``, ``&#10;`` and the rest) read back as the text they stand for, and
    decoding never changes a row's cell count. GFM's ``\\|`` is not decoded unless ``escaped_pipes`` asks for it: a row that
    holds one splits there, as it always has (NFR-1). A caller must not decode the returned values again.

    Stop rule (FR-K9.2; amended at P0, 2026-09-28, RC-3/architect finding
    F-1): scanning for the table stops at the next heading whose level
    (count of leading '#') is less than or equal to ``max(matched_level,
    2)`` — so an empty ``### Foo`` section correctly yields no rows instead
    of adopting a later ``###``/``####`` section's table (a level-3-or-
    deeper match gets this tighter, level-aware rule), while a level-1 or
    level-2 match keeps today's plain ``#``/``##`` stop. The literal "same
    as or higher than the matched line" rule — stopping only at
    ``level <= matched_level`` — would *loosen* a level-1 match instead of
    preserving it: a document TITLE (e.g. ``# Threat Model Risk Summary``)
    is itself a level-1 heading, so a bare-substring fallback that matches
    it (three callers can: "Risk Summary", "Severity Distribution",
    "Coverage Distribution") would then scan past the very next ``##``
    section and could adopt a *later* section's table — breaking
    FR-K9.2's "existing callers MUST be unaffected" for exactly the callers
    it exists to protect. When the matched line is not a heading (a
    handful of callers match bold paragraph text, e.g. "Coverage
    Distribution"), the stop rule is unchanged from before this fix: stop
    only at a literal ``## `` or ``# `` line.
    """
    lines = content.split("\n")

    if start_line is not None:
        header_idx = start_line
    else:
        # Find the section header
        header_idx = None
        for i, line in enumerate(lines):
            if section_header in line:
                header_idx = i
                break
        if header_idx is None:
            return []

    matched_level = _heading_level(lines[header_idx].strip()) if 0 <= header_idx < len(lines) else None

    # Scan forward for the first table row (starts with |)
    table_header_idx = None
    for i in range(header_idx + 1, len(lines)):
        line = lines[i].strip()
        if line.startswith("|") and "|" in line[1:]:
            table_header_idx = i
            break
        if matched_level is not None:
            # Stop at the next heading of level <= max(matched_level, 2)
            # (FR-K9.2; amended at P0, RC-3): a level-1-or-2 match keeps the
            # old "#"/"##" stop; only a level-3+ match gets the tighter,
            # level-aware rule.
            level = _heading_level(line)
            if level is not None and level <= max(matched_level, 2):
                break
        elif line.startswith("## ") or line.startswith("# "):
            # Non-heading match: today's rule, unchanged.
            break

    if table_header_idx is None:
        return []

    # Parse header row for column names
    header_line = lines[table_header_idx].strip()
    header_cells = [decode_references(strip_bold(c.strip()))
                    for c in (_escaped_pipe_cells(header_line) if escaped_pipes else header_line.split("|")[1:-1])]
    columns = [c for c in header_cells if c]

    if not columns:
        return []

    # Skip separator row (|---|---|...)
    data_start = table_header_idx + 1
    if data_start < len(lines):
        sep_line = lines[data_start].strip()
        if re.match(r"^\|[\s\-:|]+\|$", sep_line):
            data_start += 1

    # Parse data rows
    rows = []
    for i in range(data_start, len(lines)):
        line = lines[i].strip()
        if not line.startswith("|"):
            break
        cells = [decode_references(c.strip() if keep_bold else strip_bold(c.strip()))
                 for c in (_escaped_pipe_cells(line) if escaped_pipes else line.split("|")[1:-1])]
        if len(cells) < len(columns):
            print(f"Warning: skipping malformed row at line {i + 1}: expected {len(columns)} columns, got {len(cells)}", file=sys.stderr)
            if skipped is not None:
                skipped.append(i + 1)
            continue
        if overlong is not None and len(cells) > len(header_cells):
            overlong.append(i + 1)
        row = {}
        for j, col in enumerate(columns):
            row[col] = cells[j] if j < len(cells) else ""
        rows.append(row)
        if row_lines is not None:
            row_lines.append(i + 1)

    return rows


def _find_table_with_column(content: str, section_header: str, required_column: str) -> list:
    """Find a markdown table within a section that has a specific column header.

    Scans all tables after section_header and returns the first one
    whose header row contains required_column. Cells are decoded as
    :func:`parse_markdown_table` decodes them.
    """
    lines = content.split("\n")
    header_idx = None
    for i, line in enumerate(lines):
        if section_header in line:
            header_idx = i
            break
    if header_idx is None:
        return []

    section_end = len(lines)
    for i in range(header_idx + 1, len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith("## ") or stripped.startswith("# "):
            section_end = i
            break

    i = header_idx + 1
    while i < section_end:
        stripped = lines[i].strip()
        if stripped.startswith("|") and "|" in stripped[1:]:
            columns = [decode_references(strip_bold(c.strip())) for c in stripped.split("|")[1:-1]]
            columns = [c for c in columns if c]

            if columns and required_column in columns:
                # Found the right table -- parse it
                data_start = i + 1
                if data_start < section_end:
                    sep = lines[data_start].strip()
                    if re.match(r"^\|[\s\-:|]+\|$", sep):
                        data_start += 1

                rows = []
                for j in range(data_start, section_end):
                    row_line = lines[j].strip()
                    if not row_line.startswith("|"):
                        break
                    cells = [decode_references(strip_bold(c.strip())) for c in row_line.split("|")[1:-1]]
                    if len(cells) < len(columns):
                        continue
                    row = {}
                    for k, col in enumerate(columns):
                        row[col] = cells[k] if k < len(cells) else ""
                    rows.append(row)
                return rows

            # Wrong table -- skip past it
            i += 1
            while i < section_end and lines[i].strip().startswith("|"):
                i += 1
            continue

        i += 1

    return []


# =============================================================================
# Frontmatter Parser
# =============================================================================

def _extract_frontmatter_text(content: str):
    """Extract raw frontmatter text between --- delimiters.

    Handles both standard (--- ... ---) and code-fenced (```yaml ... ```) formats.
    Returns the text between delimiters, or None if no frontmatter found.
    """
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        match = re.search(r"```yaml\s*\n---\s*\n(.*?)\n---\s*\n```", content, re.DOTALL)
    return match.group(1) if match else None


def parse_frontmatter(content: str) -> dict:
    """Extract key-value pairs from YAML frontmatter between --- delimiters.

    Handles both standard frontmatter and code-fenced frontmatter (```yaml ... ```).
    Only extracts top-level scalar values needed for the report.
    """
    result = {"date": "Unknown", "classification": None, "schema_version": "1.0"}

    frontmatter_text = _extract_frontmatter_text(content)
    if not frontmatter_text:
        return result

    # Extract top-level key: value pairs (skip nested keys by checking indentation)
    for line in frontmatter_text.split("\n"):
        # Skip empty lines, comments, and indented (nested) lines
        if not line.strip() or line.strip().startswith("#") or line.startswith(" ") or line.startswith("\t"):
            continue
        kv_match = re.match(r'^(\w[\w_]*)\s*:\s*"?([^"]*?)"?\s*$', line)
        if kv_match:
            key = kv_match.group(1)
            value = kv_match.group(2).strip()
            if key == "date":
                result["date"] = value
            elif key == "classification":
                result["classification"] = value if value else None
            elif key == "schema_version":
                result["schema_version"] = value

    return result


def parse_baseline_frontmatter(content: str) -> dict:
    """Extract baseline metadata from threats.md frontmatter.

    Hand-parses the nested baseline: block to avoid PyYAML dependency
    (stdlib-only policy per PAT-014). Returns dict with keys:
    has_baseline, source, date, finding_count, run_id. All values are
    None when no baseline is present; has_baseline is False.
    """
    result = {"has_baseline": False, "source": None, "date": None, "finding_count": None, "run_id": None}
    fm = _extract_frontmatter_text(content)
    if not fm:
        return result
    # Find baseline: block and parse nested keys
    in_baseline = False
    for line in fm.split("\n"):
        if line.strip().startswith("baseline:"):
            in_baseline = True
            continue
        if in_baseline:
            if not line.startswith(" ") and not line.startswith("\t"):
                break  # left the baseline block
            kv = re.match(r'^\s+(\w[\w_]*)\s*:\s*"?([^"]*?)"?\s*$', line)
            if kv:
                key, val = kv.group(1), kv.group(2).strip()
                if val.lower() in ("null", "~", ""):
                    val = None
                if key in result and key != "has_baseline":
                    result[key] = val
    result["has_baseline"] = result["source"] is not None
    return result


# =============================================================================
# Project Name Parser
# =============================================================================

def parse_project_name(
    content: str,
    title_override: str = None,
    target_dir: Path = None,
) -> str:
    """Extract project name from threats.md H1, with architecture.md fallback.

    Precedence:
      1. ``title_override`` if provided (CLI --title wins)
      2. threats.md H1 in one of the two recognized formats
      3. architecture.md H1 in ``target_dir`` (snapshot from Feature 120)
      4. ``"Unknown Project"`` fallback

    Recognized threats.md H1 formats:
      - ``# {Name} Threat Model``
      - ``# Threat Model: {Name}``

    Recognized architecture.md H1 formats (em-dash separated):
      - ``# {Name} — Architecture`` (example convention)
      - ``# Security Architecture — {Name}`` / ``# Architecture — {Name}``

    The current orchestrator output template writes a literal
    ``# Threat Model Report`` H1, which matches neither threats.md format, so
    the architecture.md fallback recovers the name for real pipeline runs that
    snapshot architecture.md alongside threats.md.
    """
    if title_override:
        return title_override

    match = re.search(r"^#\s+(.+?)\s+Threat Model\s*$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()

    match = re.search(r"^#\s+Threat Model:\s*(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()

    if target_dir is not None:
        arch_name = _parse_architecture_project_name(target_dir)
        if arch_name:
            return arch_name

    return "Unknown Project"


def _parse_architecture_project_name(target_dir: Path):
    """Extract project name from architecture.md H1 in ``target_dir``.

    Returns None when architecture.md is absent, unreadable, or has no
    parseable H1 in the recognized em-dash formats.
    """
    arch_path = target_dir / "architecture.md"
    if not arch_path.is_file():
        return None

    try:
        arch_content = arch_path.read_text(encoding="utf-8")
    except OSError:
        return None

    match = re.search(r"^#\s+(.+)$", arch_content, re.MULTILINE)
    if not match:
        return None

    heading = match.group(1).strip()
    parts = [p.strip() for p in heading.split(" — ")]
    if len(parts) != 2:
        return None

    left, right = parts
    if left.lower() in ("architecture", "security architecture"):
        return right or None
    if right.lower() == "architecture":
        return left or None

    return None


# =============================================================================
# Artifact Detection
# =============================================================================

def detect_artifacts(target_dir: Path) -> dict:
    """Scan target directory for tachi pipeline artifacts.

    Returns dict with boolean flags for each artifact type.

    The ``has_agentic_patterns`` boolean (Feature 142) is ``True`` iff the
    threats.md at ``target_dir`` contains at least one finding with a
    non-``none`` ``agentic_pattern`` value after :func:`parse_threats_findings`
    processing. Mirrors the :data:`has_attack_chains` propagation path from
    Feature 141. Downstream consumers: the threat-report agent (conditional
    Agentic Pattern Analysis section gating), the threats.md output
    template (conditional Section 4b "Findings by Agentic Pattern"
    rendering), and the PDF security report pipeline
    (``extract-report-data.py`` conditional pattern data emission).
    """
    artifacts = {
        "threats_md": False,
        "risk_scores_md": False,
        "compensating_controls_md": False,
        "threat_report_md": False,
        "funnel_image": False,
        "baseball_image": False,
        "architecture_image": False,
    }

    files = {
        "threats_md": "threats.md",
        "risk_scores_md": "risk-scores.md",
        "compensating_controls_md": "compensating-controls.md",
        "threat_report_md": "threat-report.md",
        "funnel_image": "threat-risk-funnel.jpg",
        "baseball_image": "threat-baseball-card.jpg",
        "architecture_image": "threat-system-architecture.jpg",
    }

    for key, filename in files.items():
        filepath = target_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            if size > 0:
                artifacts[key] = True
            else:
                print(f"Warning: skipping {filename}: file is empty (0 bytes)", file=sys.stderr)

    # Directory-based artifact: attack-trees/
    attack_trees_dir = target_dir / "attack-trees"
    if attack_trees_dir.is_dir():
        artifacts["has_attack_trees"] = any(attack_trees_dir.glob("*-attack-tree.md"))
    else:
        artifacts["has_attack_trees"] = False

    # File-based artifact: attack-chains.md
    attack_chains_file = target_dir / "attack-chains.md"
    if attack_chains_file.exists() and attack_chains_file.stat().st_size > 0:
        artifacts["has_attack_chains"] = True
    else:
        artifacts["has_attack_chains"] = False

    # Feature 142: agentic pattern presence flag. True iff threats.md
    # contains at least one finding with agentic_pattern != "none" after
    # parse_threats_findings normalization. Pre-Feature-142 threats.md
    # files (no Pattern column) yield False here because every finding
    # defaults to "none" per FR-017.
    artifacts["has_agentic_patterns"] = False
    if artifacts["threats_md"]:
        try:
            threats_content = (target_dir / "threats.md").read_text(encoding="utf-8")
            for finding in parse_threats_findings(threats_content):
                if finding.get("agentic_pattern", "none") != "none":
                    artifacts["has_agentic_patterns"] = True
                    break
        except OSError:
            pass

    return artifacts


# =============================================================================
# Tier Selection
# =============================================================================

def determine_tier(artifacts: dict) -> int:
    """Determine data source tier from detected artifacts.

    Tier 1: compensating-controls.md exists
    Tier 2: risk-scores.md exists (no compensating-controls.md)
    Tier 3: threats.md only
    """
    if artifacts["compensating_controls_md"]:
        return 1
    elif artifacts["risk_scores_md"]:
        return 2
    else:
        return 3


# =============================================================================
# Severity Parsers
# =============================================================================

def parse_threats_severity(content: str) -> dict:
    """Parse Section 6 Risk Summary table from threats.md.

    Extracts Critical, High, Medium, Low, Note counts and total.
    Handles "N (M raw)" format in Total row -- uses raw count.
    Note: Section 6 may contain a calibration matrix before the severity table.
    """
    rows = parse_markdown_table(content, "## 6. Risk Summary")
    # Section 6 may have a calibration matrix before the severity table.
    # Check if the found table has "Risk Level" column; if not, find the right one.
    if rows and "Risk Level" not in rows[0]:
        rows = _find_table_with_column(content, "## 6. Risk Summary", "Risk Level")
    if not rows:
        rows = parse_markdown_table(content, "Risk Summary")
    if rows and "Risk Level" not in rows[0]:
        rows = []
    if not rows:
        print("Warning: could not find Risk Summary table in threats.md", file=sys.stderr)
        return _empty_severity()

    return _accumulate_severity_rows(rows, "Risk Level")


def parse_risk_scores_severity(content: str) -> dict:
    """Parse risk-scores.md Section 1 severity distribution table.

    Preferred over threats.md when Tier 2.
    """
    rows = parse_markdown_table(content, "Severity Distribution")
    if not rows:
        rows = parse_markdown_table(content, "## 1. Executive Summary")
    if not rows:
        print("Warning: could not find severity distribution in risk-scores.md", file=sys.stderr)
        return _empty_severity()

    return _accumulate_severity_rows(rows, "Severity")


def _empty_severity() -> dict:
    """Create a zeroed severity dict derived from SEVERITY_ORDER."""
    sev = {s.lower(): 0 for s in SEVERITY_ORDER}
    sev["total"] = 0
    return sev


def _accumulate_severity_rows(rows: list, level_column: str) -> dict:
    """Accumulate severity counts from parsed table rows.

    Args:
        rows: List of row dicts from parse_markdown_table().
        level_column: Column name containing severity level (e.g., "Risk Level", "Severity").
    """
    severity = _empty_severity()
    for row in rows:
        level = row.get(level_column, "").strip()
        count_str = row.get("Count", "").strip()

        if level.lower() == "total" or level.startswith("Total"):
            total_match = re.match(r"(\d+)(?:\s*\((\d+)\s*raw\))?", count_str)
            if total_match:
                raw = total_match.group(2)
                severity["total"] = int(raw) if raw else int(total_match.group(1))
        else:
            key = level.lower()
            if key in severity:
                severity[key] = _parse_int(count_str)
    return severity


# =============================================================================
# Findings Parsers
# =============================================================================

# =============================================================================
# K12 Delta Status (Feature 373, data-model.md §6)
# =============================================================================

_DELTA_STATUS_STRIP_CHARS = "`*_ "
_DELTA_STATUS_COUNTED_VALUES = frozenset({"NEW", "UPDATED", "UNCHANGED"})


def normalize_delta_status(s: str) -> str:
    """Normalize a Section 7 ``Status`` cell for delta-status matching.

    Strips a surrounding run of backticks, ``*``, ``_`` and whitespace; then
    one surrounding ``[...]`` pair; then the run again; then upper-cases.
    ``NEW``, ``[NEW]``, ``**[NEW]**`` and `` `[NEW]` `` all normalize to
    ``NEW`` (N6 order, data-model.md §6).
    """
    s = (s or "").strip(_DELTA_STATUS_STRIP_CHARS)
    if len(s) >= 2 and s[0] == "[" and s[-1] == "]":
        s = s[1:-1]
    s = s.strip(_DELTA_STATUS_STRIP_CHARS)
    return s.upper()


def delta_status_by_id(threats_md: str):
    """Read threats.md Section 7's Status column into a normalized map.

    Returns ``(status_by_id, has_status_column, row_count)`` (data-model.md
    §6): the normalized ``{finding_id: status}`` map with placeholder IDs
    excluded, whether Section 7's table has a Status column at all, and the
    table's row count (feeds the scoped empty-map check in
    :func:`warn_delta_scope`).
    """
    rows = parse_markdown_table(threats_md, "## 7. Recommended Actions")
    has_status_column = bool(rows) and "Status" in rows[0]
    status_by_id = {}
    if has_status_column:
        for row in rows:
            fid = row.get("Finding ID", "").strip()
            if is_placeholder_id(fid):
                continue
            status_by_id[fid] = normalize_delta_status(row.get("Status", ""))
    return status_by_id, has_status_column, len(rows)


def compute_delta_counts(status_by_id: dict, resolved: list) -> dict:
    """Count NEW/UPDATED/UNCHANGED from a normalized Section 7 status map.

    Counts over the normalized map only (FR-K12.1/K12.2, data-model.md §6),
    identically regardless of data tier — never over a tier's ``findings``
    list, which may have no ``delta_status`` key at all (Tier 1/2); the map
    also excludes placeholder and duplicate Section 7 rows and spans IDs
    outside the tier. ``resolved`` is the placeholder-filtered list
    from :func:`parse_resolved_findings`; its length becomes ``resolved``.
    A status that normalizes to anything other than NEW/UPDATED/UNCHANGED
    does not add to a bucket — the caller aggregates that as a warning via
    :func:`warn_delta_scope`.
    """
    counts = {"new": 0, "updated": 0, "unchanged": 0, "resolved": len(resolved)}
    for status in status_by_id.values():
        if status == "NEW":
            counts["new"] += 1
        elif status == "UPDATED":
            counts["updated"] += 1
        elif status == "UNCHANGED":
            counts["unchanged"] += 1
    return counts


def apply_delta_status(findings: list, status_by_id: dict) -> None:
    """Stamp normalized Section 7 statuses onto a tier's findings, in place.

    For the per-finding badges (report path) and ``top_findings[].delta_status``
    (infographic path) only — it plays no part in :func:`compute_delta_counts`
    (data-model.md §6). Findings whose id has no entry in ``status_by_id`` are
    left untouched.
    """
    for finding in findings:
        fid = finding.get("id", "")
        if fid in status_by_id:
            finding["delta_status"] = status_by_id[fid]


def warn_delta_scope(has_baseline, has_status_column, status_by_id, row_count, tier_ids) -> None:
    """Emit PD-16's scoped, aggregated delta-status warnings. Never raises.

    ``tier_ids`` is the tier's own finding-ID set. All checks are gated on
    ``has_baseline``; the empty-map and ID-set-mismatch checks additionally
    require ``has_status_column`` (data-model.md §6) — a legacy Status-less
    Section 7 on a non-baseline (or even baseline) run must never warn.
    """
    if not has_baseline:
        return

    if not has_status_column:
        print(
            "Warning: baseline run but threats.md Section 7 has no Status "
            "column; delta counts unavailable",
            file=sys.stderr,
        )
        return

    if not status_by_id:
        if row_count > 0:
            print(
                f"Warning: threats.md Section 7 has {row_count} rows but no "
                "readable Finding ID/Status pairs; delta counts are 0",
                file=sys.stderr,
            )
        return

    _warn_aggregated(
        [f"{fid}='{status}'" for fid, status in status_by_id.items()
         if status not in _DELTA_STATUS_COUNTED_VALUES],
        "Section 7 statuses are not NEW/UPDATED/UNCHANGED after normalization",
        "not counted",
    )

    map_ids = set(status_by_id.keys())
    tier_id_set = set(tier_ids or ())
    if map_ids != tier_id_set:
        only_in_map = len(map_ids - tier_id_set)
        only_in_tier = len(tier_id_set - map_ids)
        print(
            "Warning: Section 7 status IDs differ from tier finding IDs "
            f"({only_in_map} only-in-map, {only_in_tier} only-in-tier)",
            file=sys.stderr,
        )


# =============================================================================
# K13-posture (Feature 373, data-model.md §5)
# =============================================================================

_RISK_POSTURE_LABELS = {
    "critical": "CRITICAL RISK",
    "high": "HIGH RISK",
    "medium": "MODERATE RISK",
    "low": "LOW RISK",
}


def compute_risk_posture(counts: dict):
    """Compute the single risk-posture level/label from severity counts.

    ``counts`` is a severity-count dict with at least ``critical``, ``high``
    and ``medium`` keys (case-sensitive lowercase, e.g. the ``severity``
    dict returned by :func:`parse_compensating_controls_md` or
    :func:`parse_risk_scores_severity`/:func:`parse_threats_severity`). The
    level is the highest non-zero band — critical, else high, else medium,
    else low. Zero findings (or an all-zero dict) give ``low``/``LOW RISK``
    (D-3). The caller decides which counts dict to pass: residual severity
    (after K11's clamp) when a controls report exists, else the inherent
    composite, else qualitative (data-model.md §5) — this function only
    picks the highest band and its label.

    Returns (level, label).
    """
    if counts.get("critical", 0) > 0:
        level = "critical"
    elif counts.get("high", 0) > 0:
        level = "high"
    elif counts.get("medium", 0) > 0:
        level = "medium"
    else:
        level = "low"
    return level, _RISK_POSTURE_LABELS[level]


_RESOLVED_FINDINGS_HEADING = r"^##\s+4[bc]\.\s+Resolved Findings\s*$"


def parse_resolved_findings(content: str) -> list:
    """Parse the Resolved Findings table: the template's ``## 4c.`` heading,
    or the legacy ``## 4b.`` spelling (FR-K12.4) — one heading-class regex
    covers both, via :func:`match_heading`, so a renumbering never silently
    stops matching. Rows whose ID is a placeholder are skipped (FR-K12.3).

    Returns list of resolved finding dicts with delta_status="RESOLVED" injected.
    Returns empty list when neither heading is present (first run, no baseline).
    """
    start = match_heading(_RESOLVED_FINDINGS_HEADING, content)
    if start is None:
        return []
    rows = parse_markdown_table(content, start_line=start)
    findings = []
    for row in rows:
        fid = row.get("ID", "").strip()
        if is_placeholder_id(fid):
            continue
        findings.append({
            "id": fid,
            "component": row.get("Component", "").strip(),
            "threat": row.get("Threat", "").strip(),
            "risk_level": row.get("Last Risk Level", "").strip(),
            "resolution_reason": row.get("Resolution Reason", "").strip(),
            "delta_status": "RESOLVED",
        })
    return findings


# Source Attribution parser — optional "## 9. Source Attribution" YAML block
# with conditional-key emission (absent section => no key on finding dict).

VALID_SOURCE_ATTRIBUTION_TAXONOMIES = (
    "owasp",
    "mitre-attack",
    "mitre-atlas",
    "nist-ai-rmf",
    "cwe",
)

VALID_SOURCE_ATTRIBUTION_RELATIONSHIPS = ("primary", "related", "derived")

_SRC_ATTR_KEYS_2 = frozenset(("taxonomy", "id"))
_SRC_ATTR_KEYS_3 = frozenset(("taxonomy", "id", "relationship"))


_SRC_ATTR_KV_PATTERN = re.compile(r"\s*([a-zA-Z_][a-zA-Z_0-9]*)\s*:\s*(.*?)\s*$")


def _parse_source_attribution_flow_dict(body: str) -> dict:
    """Parse a flow-style YAML dict body (``key: value, ...``) into a Python dict.

    Restricted shape: no nested dicts, no quoted commas, no multiline values.
    Stdlib-only to keep scripts/ free of the pyyaml runtime dependency.
    """
    out: dict = {}
    for part in body.split(","):
        kv = _SRC_ATTR_KV_PATTERN.match(part)
        if kv:
            out[kv.group(1)] = kv.group(2).strip().strip("'\"")
    return out


def _extract_source_attribution_block(content: str):
    """Extract the ``## 9. Source Attribution`` YAML block as a dict.

    Returns:
        ``None`` when the Section 9 header is absent (V6 absent-key semantic).
        ``dict[finding_id, list[record]]`` when the header is present. The
        list may be empty when a finding_id is inline-declared as ``[]`` or
        when a block-style key has no list items below it.
    """
    header = re.search(r"^## 9\. Source Attribution\s*$", content, re.MULTILINE)
    if not header:
        return None
    rest = content[header.end():]
    fence = re.search(r"```yaml\s*\n(.*?)\n```", rest, re.DOTALL)
    if not fence:
        return {}
    text = fence.group(1)

    result: dict = {}
    current_id = None
    for line in text.split("\n"):
        empty_inline = re.match(r"^([A-Z]+-\d+)\s*:\s*\[\s*\]\s*$", line)
        if empty_inline:
            result[empty_inline.group(1)] = []
            current_id = None
            continue
        block_key = re.match(r"^([A-Z]+-\d+)\s*:\s*$", line)
        if block_key:
            current_id = block_key.group(1)
            result[current_id] = []
            continue
        list_item = re.match(r"^\s*-\s*\{(.+)\}\s*$", line)
        if list_item and current_id is not None:
            result[current_id].append(_parse_source_attribution_flow_dict(list_item.group(1)))
            continue
    return result


def _extract_source_attribution(finding_id: str, block):
    """Resolve source_attribution records for one finding from a pre-parsed block.

    Returns None when ``block`` is None or ``finding_id`` is not keyed — caller
    must not inject the ``source_attribution`` key (conditional-key semantic,
    distinguishing absent from explicitly-empty). Returns list[dict] (possibly
    empty) otherwise; missing ``relationship`` values default to ``"primary"``.
    """
    if block is None or finding_id not in block:
        return None
    emit: list = []
    for record in block[finding_id]:
        keys = frozenset(record.keys())
        if keys != _SRC_ATTR_KEYS_2 and keys != _SRC_ATTR_KEYS_3:
            extra = sorted(keys - _SRC_ATTR_KEYS_3)
            missing = sorted(_SRC_ATTR_KEYS_2 - keys)
            problem = f"unexpected key(s): {extra}" if extra else f"missing required key(s): {missing}"
            raise ValueError(
                f"Finding {finding_id}: {problem} in source_attribution record"
            )
        rec = dict(record)

        taxonomy = rec["taxonomy"]
        if taxonomy not in VALID_SOURCE_ATTRIBUTION_TAXONOMIES:
            raise ValueError(
                f"Finding {finding_id}: invalid taxonomy {taxonomy!r}. "
                f"Allowed: {set(VALID_SOURCE_ATTRIBUTION_TAXONOMIES)}"
            )

        id_value = rec.get("id", "")
        if not isinstance(id_value, str) or id_value == "":
            raise ValueError(
                f"Finding {finding_id}: empty or null id in source_attribution record"
            )

        rec.setdefault("relationship", "primary")
        relationship = rec["relationship"]
        if relationship not in VALID_SOURCE_ATTRIBUTION_RELATIONSHIPS:
            raise ValueError(
                f"Finding {finding_id}: invalid relationship {relationship!r}. "
                f"Allowed: {set(VALID_SOURCE_ATTRIBUTION_RELATIONSHIPS)}"
            )

        emit.append(rec)
    return emit


def parse_threats_findings(content: str) -> list:
    """Parse Section 7 Recommended Actions table for Tier 3 findings.

    Returns list of finding dicts with Tier 3 keys.

    The ``agentic_pattern`` key is always present; if the table has no
    ``Pattern`` / ``Agentic Pattern`` column (pre-1.4 threats.md), every
    finding defaults to ``'none'``. The ``source_attribution`` key is
    conditionally injected only when the finding's ID is keyed in a
    ``## 9. Source Attribution`` block.
    """
    rows = parse_markdown_table(content, "## 7. Recommended Actions")
    if not rows:
        print("Warning: could not find Recommended Actions table in threats.md", file=sys.stderr)
        return []
    return _findings_from_section_7_rows(rows, content)


def _findings_from_section_7_rows(rows: list, content: str) -> list:
    """The Tier 3 finding dicts of a Section 7 table's ``rows`` (the body of :func:`parse_threats_findings`).

    The reference-set wrapper calls it too, for a table under any of the heading forms it reads.
    """
    # Detect the Pattern column key (case-insensitive match on the table
    # header). FR-009 specifies the threats.md Section 3 / 4 tables render
    # the column as "Agentic Pattern"; the orchestrator MAY propagate the
    # same column into the Section 7 summary. Accept either spelling here
    # so a single parser handles both table shapes.
    pattern_key = None
    for col in rows[0].keys():
        if col.strip().lower() in ("pattern", "agentic pattern"):
            pattern_key = col
            break

    source_attribution_block = _extract_source_attribution_block(content)

    findings = []
    for row in rows:
        # Agentic pattern: always populated on every finding per FR-017.
        # Pre-Feature-142 threats.md (no Pattern column) → defaults to
        # 'none' via parse_finding_pattern's sentinel handling. The
        # em-dash placeholder ("—") rendered by FR-009 for findings with
        # agentic_pattern: none normalizes to 'none' as well.
        if pattern_key is not None:
            pattern_value = parse_finding_pattern(row.get(pattern_key, ""))
        else:
            pattern_value = "none"

        finding = {
            "id": row.get("Finding ID", "").strip(),
            "component": row.get("Component", "").strip(),
            "threat": row.get("Threat", "").strip(),
            "likelihood": "\u2014",  # em dash
            "impact": "\u2014",
            "risk_level": row.get("Risk Level", "").strip(),
            "mitigation": row.get("Mitigation", "").strip(),
            "agentic_pattern": pattern_value,
        }
        # Delta fields: include only when present (backward compatible).
        # K12 (T016 gap, data-model.md §6): normalize at parse, same as
        # delta_status_by_id's Section 7 map, so tier-3 badges and
        # top_findings[].delta_status never show a raw "[NEW]"-style value.
        status = row.get("Status", "").strip()
        if status:
            finding["delta_status"] = normalize_delta_status(status)
        attribution = _extract_source_attribution(finding["id"], source_attribution_block)
        if attribution is not None:
            finding["source_attribution"] = attribution
        findings.append(finding)
    return findings


# =============================================================================
# The reference finding set (F-374 S-12, FR-E.16): one reader for every stage
# =============================================================================

REFERENCE_SET_SECTION = "## 7. Recommended Actions"
REFERENCE_SET_FORM = ("a table whose header row has a 'Finding ID' column and one row for each open finding, "
                      "or a numbered list whose items each start with a bolded finding ID")
REFERENCE_SET_REMEDY = ("regenerate threats.md with /tachi.threat-model, or correct the section to the table form "
                        "or the numbered-list form")
# M1 (T067a): a row with more cells than its header holds a raw `|` in a cell. The renderers write a pipe as `&#124;`, which a
# reader decodes after it splits the row. GFM's `\|` is a pipe in its cell for this reader (P1-3, through `parse_markdown_table`'s
# `escaped_pipes`), so only a pipe that no backslash escapes is refused. The extractors and the per-finding tables still split at
# `\|` (NFR-1), so `&#124;` is the spelling that every reader of threats.md reads as a pipe.
REFERENCE_SET_PIPE_REMEDY = ("write each '|' inside a cell as '&#124;', the spelling that every reader of threats.md reads as a pipe, "
                             "or regenerate threats.md with /tachi.threat-model")
# S-12(b): the flag for a value that Section 7's form lacks, in the scorer's closed `<kind>:<field>:<cause>` vocabulary
# (contracts/module-signatures.md). `input` is the kind for what an input says, the field is the finding schema's name for
# the value (`component`, `threat`, `delta_status` or `risk_level`), and the cause is kebab-case, like `no-vector`.
FORM_LACKS_CAUSE = "not-in-form"
FORM_LACKS_FLAG = "input:%s:" + FORM_LACKS_CAUSE

# S-12(a): the drift forms that tachi's shipped samples show. The heading `## Section 7: Recommended Actions`, and a
# Section 7 that is a numbered list of bolded IDs under priority subheadings, with the bold text in one of three
# spellings: `**T-10**`, `**LLM-3 + LLM-4**` or `**T-2 through T-9**`, each followed by an optional dash and title. Anything
# else is unreadable (S-12(c)), so the list of forms stays closed.
#
# S7-1 (T068): the reader runs on a file that the scanned repository can write, so each pattern below is linear in the
# length of a whitespace run, whatever the line holds. The title separator is the one dash that has whitespace on both
# sides, found by lookaround (a pattern that wraps the dash in `\s+` rescans the run from every start position), and the
# first cell is anchored on the finding-ID allow-list instead of sitting lazily between two `\s*`.
_SECTION_7_DRIFT_HEADING = re.compile(r"^#{2,3}\s+Section\s+7[.:]\s+Recommended Actions")
_LIST_ITEM = re.compile(r"^ {0,3}[0-9]+[.)]\s+(?P<rest>.*)$")
_BOLD_LEAD = re.compile(r"^\*\*(?P<bold>.+?)\*\*(?P<tail>.*)$")
_TITLE_SEPARATOR = re.compile(r"(?<=\s)[\u2014\u2013-](?=\s)")
_ID_RANGE = re.compile(r"^(?P<first>\S+)\s+through\s+(?P<last>\S+)$")
_PRIORITY_BAND = re.compile(r"\b(critical|high|medium|low)\b", re.IGNORECASE)
_FIRST_CELL = re.compile(r"^\|\s*(?:\*\*)?(?P<cell>%s)(?:\*\*)?\s*\|" % tachi_parts.ID_PATTERNS["finding"])
_MAX_RANGE = 500


class ReferenceSetError(ValueError):
    """A ``threats.md`` whose findings can't serve as the reference finding set (S-12(c)).

    ``reason`` names the file, the section and the problem, ``expected`` is the form that is read, and
    ``remedy`` says what to do, so an entry can print the remedy on its own line (ADR-050 D4). ``str(error)``
    joins the three.
    """

    def __init__(self, source: str, section: str, problem: str, remedy: str = REFERENCE_SET_REMEDY):
        self.reason = "%s: %s %s" % (source, section, problem)
        self.expected = REFERENCE_SET_FORM
        self.remedy = remedy
        super().__init__("%s. Expected %s. Remedy: %s" % (self.reason, self.expected, self.remedy))


def _checked_findings(findings: list, section: str, source: str, seen: set, duplicates: set) -> list:
    """The findings whose IDs pass the allow-list, each canonical ID once (the first row wins), in S-2 order.

    A repeat is dropped and its canonical ID added to ``duplicates``, so the caller can warn: a finding appears
    once in the reference set (D-4), and a shipped example's Section 7 does list one twice.
    """
    kept = []
    for finding in findings:
        finding_id = finding["id"]
        if not tachi_parts.id_matches("finding", finding_id):
            raise ReferenceSetError(source, section, "names %r, which is not a finding ID" % finding_id[:40])
        canonical = tachi_parts.canonical_finding_id(finding_id)
        if canonical in seen:
            duplicates.add(canonical)
            continue
        seen.add(canonical)
        kept.append(finding)
    return sorted(kept, key=lambda finding: tachi_parts.finding_sort_key(finding["id"]))


def _reference_set_start(content: str) -> Optional[int]:
    """The 0-based line of Section 7's heading, in either spelling, or ``None``: ``## 7. Recommended Actions`` (found
    anywhere on a line, as it always was) or ``## Section 7: Recommended Actions``. The first one in the file wins."""
    for index, line in enumerate(content.split("\n")):
        if REFERENCE_SET_SECTION in line or _SECTION_7_DRIFT_HEADING.match(line):
            return index
    return None


def _finding_ids_in_tables(content: str) -> set:
    """The canonical IDs that open a table row anywhere in ``content``, less the resolved findings' (a table's first
    cell is the ID in every finding table). A range in a numbered Section 7 is checked against this set."""
    found = set()
    for line in content.split("\n"):
        cell = _FIRST_CELL.match(line.strip())
        if cell is not None:
            found.add(tachi_parts.canonical_finding_id(cell.group("cell")))
    for finding in parse_resolved_findings(content):
        if tachi_parts.id_matches("finding", finding["id"]):
            found.discard(tachi_parts.canonical_finding_id(finding["id"]))
    return found


def _priority_band(heading: str) -> str:
    """The risk level a priority subheading names (``Critical``, ``High``, ``Medium`` or ``Low``), or ``""`` when it
    names none or more than one, as ``### Medium / Low Priority`` does."""
    bands = {band.lower() for band in _PRIORITY_BAND.findall(heading)}
    return next(iter(bands)).capitalize() if len(bands) == 1 else ""


def _ids_of_a_bolded_lead(bold: str, at: int, content: str, source: str, section: str, known: list) -> list:
    """The finding IDs, as written, that one item's bold text names (S-12(a)'s three spellings).

    ``known`` holds the table IDs once a range needs them. A range is expanded, and kept only to the IDs that the
    file's tables list, so a range can't invent a finding. ``at`` is the item's 1-based line, for the messages.
    """
    head = _TITLE_SEPARATOR.split(bold, 1)[0].strip()
    span = _ID_RANGE.match(head)
    if span is None:
        tokens = [token.strip() for token in head.split("+")]
        for token in tokens:
            if not tachi_parts.id_matches("finding", token):
                raise ReferenceSetError(source, section, "names %r, which is not a finding ID (line %d)" % (token[:40], at))
        return tokens
    first, last = span.group("first"), span.group("last")
    for token in (first, last):
        if not tachi_parts.id_matches("finding", token):
            raise ReferenceSetError(source, section, "names %r, which is not a finding ID (line %d)" % (token[:40], at))
    (first_prefix, first_number), (last_prefix, last_number) = (
        tachi_parts.canonical_finding_id(token).split("-") for token in (first, last))
    if first_prefix != last_prefix or not 0 <= int(last_number) - int(first_number) < _MAX_RANGE:
        raise ReferenceSetError(source, section, "has a range that can't be read (line %d)" % at)
    if not known:
        known.append(_finding_ids_in_tables(content))
    if not known[0]:
        raise ReferenceSetError(source, section, "has a range, and the file has no finding tables to check it against (line %d)" % at)
    confirmed = ["%s-%d" % (first_prefix, number) for number in range(int(first_number), int(last_number) + 1)
                 if "%s-%d" % (first_prefix, number) in known[0]]
    if not confirmed:
        raise ReferenceSetError(source, section, "has a range that names no finding the file's tables list (line %d)" % at)
    return confirmed


def _numbered_list_findings(content: str, start: int, source: str, section: str) -> list:
    """The findings of a Section 7 written as a numbered list of bolded IDs (S-12(a)), or an empty list when it has
    no numbered item.

    The section runs from its heading to the next heading of the same or a higher level. A numbered item holds
    one or more IDs in bold, then its text; the nearest subheading above it names its priority. A numbered item
    that doesn't open with a bolded finding ID raises, so a finding is never lost without a word. The finding dicts
    have the keys :func:`parse_threats_findings` builds, with the values the form lacks (``component`` and
    ``threat``) empty and no ``delta_status``. The item's bolded title, if it has one, is dropped.
    """
    lines = content.split("\n")
    stop_level = max(_heading_level(lines[start].strip()) or 2, 2)
    block = _extract_source_attribution_block(content)
    known: list = []
    band = ""
    findings = []
    for index in range(start + 1, len(lines)):
        heading = _heading_level(lines[index].strip())
        if heading is not None:
            if heading <= stop_level:
                break
            band = _priority_band(lines[index])
            continue
        item = _LIST_ITEM.match(lines[index])
        if item is None:
            continue
        lead = _BOLD_LEAD.match(item.group("rest"))
        if lead is None:
            raise ReferenceSetError(source, section, "has a numbered item that doesn't start with a bolded finding ID (line %d)" % (index + 1))
        text = lead.group("tail").lstrip(" \t:").strip()
        for finding_id in _ids_of_a_bolded_lead(lead.group("bold"), index + 1, content, source, section, known):
            finding = {"id": finding_id, "component": "", "threat": "", "likelihood": "\u2014", "impact": "\u2014",
                       "risk_level": band, "mitigation": text, "agentic_pattern": "none"}
            attribution = _extract_source_attribution(finding_id, block)
            if attribution is not None:
                finding["source_attribution"] = attribution
            findings.append(finding)
    return findings


def parse_reference_set(content: str, source: str = "threats.md") -> dict:
    """The reference finding set of a ``threats.md``: ``{"open", "resolved", "duplicates", "form", "lacking", "flags"}``.

    ``open`` is one finding dict per Section 7 row, exactly as :func:`parse_threats_findings` builds it (``id``,
    ``component``, ``threat``, ``risk_level``, ``mitigation``, ``agentic_pattern`` and, when the table has a Status
    column, ``delta_status``). ``resolved`` is Section 4c's rows as :func:`parse_resolved_findings` builds them,
    and is empty when the file has none. Both are in S-2 order. ``id`` keeps the spelling the file uses
    (``AGP-01``), because ``findingId/v1`` prints it: compare IDs only through ``tachi_parts.canonical_finding_id``.

    Every ID passes ``tachi_parts``' finding allow-list, and each canonical ID appears once across both lists
    (D-4): the first row wins, an open finding beats a resolved one, and ``duplicates`` lists, in S-2 order, the
    canonical IDs that were repeated, so the caller can warn. Placeholder rows (an empty or dash-only ID) are
    dropped, as in the other Section 7 readers.

    **The forms (S-12(a)).** Section 7 is read under ``## 7. Recommended Actions`` or ``## Section 7: Recommended
    Actions``, as a table with a ``Finding ID`` column, or, when it has no table, as the numbered list of bolded IDs
    that two shipped samples show. An item names one ID (``**T-10**``), several (``**LLM-3 + LLM-4**``) or a range
    (``**T-2 through T-9**``), and may continue with a dash and a title. A range is expanded to the IDs of its span
    that the file's tables list, so it can't invent a finding. The nearest subheading names the item's ``risk_level``
    when it names one band. ``form`` is ``table`` or ``list``.

    **What the form lacks (S-12(b)).** ``lacking`` maps each canonical ID whose row lacks a value that a stage needs
    to the names of those values, from ``component``, ``threat``, ``delta_status`` and ``risk_level``. A list form
    lacks the first three on every row, a table with no Status or no Component or Threat column lacks that one,
    and the list form lacks ``risk_level`` where no subheading names a band. ``flags`` maps the same IDs to the
    sorted flags that name them, ``input:<field>:not-in-form`` (:data:`FORM_LACKS_FLAG`). The stage derives each value
    from the baseline where the baseline can supply it (D9's carried findings), scores the rest fresh, and puts the
    flags on the finding and lists it in the stage record. A row without ``delta_status`` is NEW until then.

    ``source`` names the file in error messages. It raises :class:`ReferenceSetError`, which ends a run before any
    agent is dispatched (S-12(c)), when Section 7 is missing, holds neither a table nor a numbered list, has a table
    with no ``Finding ID`` column, loses a malformed row, has a table row with more cells than its header (a raw ``|``
    in a cell, which would shift every value after it, so its remedy says to write ``&#124;``), has a
    numbered item that doesn't open with a bolded finding ID, has a range that can't be read, or names an ID that
    isn't a finding ID. The error names the file, the section, the expected forms and the remedy. An empty
    extraction is an error, never a pass (KB 22).

    **GFM's escaped pipe (P1-3, ADR-050 D3).** The table is read with ``escaped_pipes``: GFM, and GitHub's rendering of ``threats.md``,
    read ``\\|`` as a pipe inside its cell, and the threat-model contract never tells its writer to avoid one, so the cell holds the pipe
    and no value moves. Only a pipe that no backslash escapes splits a row, and a row that it makes too wide is still refused. This
    reader alone reads the pipe so (:func:`_section_7_layers` reads Section 7's layer cells by the same rule, so a row here is a row
    there): ``parse_threats_findings``, the extractors and the per-finding tables split at ``\\|`` as they always have (NFR-1).

    ``parse_threats_findings`` is unchanged, because the extractors rely on its ``[]``-with-a-warning behavior.
    """
    section = "Section 7 (Recommended Actions)"
    start = _reference_set_start(content)
    if start is None:
        raise ReferenceSetError(source, section, "is missing")
    skipped: list = []
    overlong: list = []
    rows = parse_markdown_table(content, start_line=start, skipped=skipped, overlong=overlong, escaped_pipes=True)
    if skipped:
        raise ReferenceSetError(source, section, "has a malformed row (line %s)" % ", ".join(str(n) for n in skipped[:5]))
    if overlong:
        raise ReferenceSetError(source, section, "has a row with more cells than its header (line %s): a '|' in a cell "
                                "splits it, and every value after the split would shift" % ", ".join(str(n) for n in overlong[:5]),
                                REFERENCE_SET_PIPE_REMEDY)
    if rows:
        if "Finding ID" not in rows[0]:
            raise ReferenceSetError(source, section, "has no 'Finding ID' column")
        form = "table"
        missing = [name for name, column in (("component", "Component"), ("threat", "Threat"), ("delta_status", "Status"))
                   if column not in rows[0]]
        findings = _findings_from_section_7_rows(rows, content)
    else:
        form = "list"
        missing = ["component", "threat", "delta_status"]
        findings = _numbered_list_findings(content, start, source, section)
        if not findings:
            raise ReferenceSetError(source, section, "holds no table rows and no numbered list of bolded finding IDs")
    listed = [finding for finding in findings if not is_placeholder_id(finding["id"])]
    if not listed:
        raise ReferenceSetError(source, section, "lists no findings")
    seen: set = set()
    repeated: set = set()
    open_rows = _checked_findings(listed, section, source, seen, repeated)
    resolved = _checked_findings(parse_resolved_findings(content), "Section 4c (Resolved Findings)", source, seen, repeated)
    lacking = {}
    for finding in open_rows:
        names = missing + (["risk_level"] if form == "list" and not finding["risk_level"] else [])
        if names:
            lacking[tachi_parts.canonical_finding_id(finding["id"])] = names
    flags = {finding_id: sorted(FORM_LACKS_FLAG % name for name in names) for finding_id, names in lacking.items()}
    return {"open": open_rows, "resolved": resolved, "duplicates": sorted(repeated, key=tachi_parts.finding_sort_key),
            "form": form, "lacking": lacking, "flags": flags}


# =============================================================================
# The MAESTRO layer of each finding (F-374 W4, from T066's group U-1; ADR-050 D2's layer chain, steps 1 and 2)
# =============================================================================

# The row under a table's header, as `parse_markdown_table` recognizes it.
_TABLE_SEPARATOR = re.compile(r"^\|[\s\-:|]+\|$")
# A per-finding table (the template's §3 and §4) opens with `ID`, and Section 7's table with `Finding ID`.
_PER_FINDING_ID_COLUMN = "ID"
_LAYER_COLUMN = "MAESTRO Layer"


def _section_7_layers(content: str) -> Dict[str, str]:
    """Section 7's ``MAESTRO Layer`` cell of each finding's first row, by canonical ID, blank or not.

    Section 7 is found where :func:`parse_reference_set` finds it, under either heading, and its table is read as that function reads
    it (GFM's ``\\|`` is a pipe in its cell, P1-3), so a row here is a row of the reference set and a pipe before the layer cell can't move
    it. A row with more cells than its header, from a raw pipe, is read by position, as :func:`parse_markdown_table` reads it: the
    reference set's refusal of one (M1) is its own and is not applied here. A section with no table (the list form), or a table with no
    ``Finding ID`` column, gives nothing.
    """
    layers: Dict[str, str] = {}
    start = _reference_set_start(content)
    if start is not None:
        for row in parse_markdown_table(content, start_line=start, escaped_pipes=True):
            finding_id = row.get("Finding ID", "").strip()
            if tachi_parts.id_matches("finding", finding_id):
                layers.setdefault(tachi_parts.canonical_finding_id(finding_id), row.get(_LAYER_COLUMN, "").strip())
    return layers


def _per_finding_layers(lines: Sequence[str]) -> Dict[str, str]:
    """The ``MAESTRO Layer`` cell of each finding's first row, by canonical ID, blank or not, over every per-finding table.

    A per-finding table is outside every code fence (:func:`_unfenced_lines`), has ``ID`` as its header's first cell and has a
    ``MAESTRO Layer`` column: the template's §3 and §4 tables, and any table under them, such as a bold-labelled sub-table in §4.2. A
    table is a run of lines that start with ``|``, begins after a line that does not, and has a separator row under its header. Its
    rows are read by the rules of :func:`parse_markdown_table`: each cell is stripped, loses its ``**`` and is decoded; a row with
    fewer cells than the header has columns is skipped; a longer row is read by the header's positions. The rows are read here, in one
    pass over ``lines``, and not by one :func:`parse_markdown_table` call per table, because each call splits the whole text again and
    a hostile file can hold as many tables as it has lines. A test pins the two readings together.
    """
    layers: Dict[str, str] = {}
    for index, line in _unfenced_lines(lines):
        stripped = line.strip()
        if not stripped.startswith("|") or (index > 0 and lines[index - 1].strip().startswith("|")):
            continue   # not the first line of a table
        if index + 1 >= len(lines) or not _TABLE_SEPARATOR.match(lines[index + 1].strip()):
            continue   # no separator row under it, so no table: the cheap test comes before the header's cells are read
        header = [decode_references(strip_bold(cell.strip())) for cell in stripped.split("|")[1:-1]]
        if header[:1] != [_PER_FINDING_ID_COLUMN] or _LAYER_COLUMN not in header:
            continue
        columns = [cell for cell in header if cell]
        number = index + 2
        while number < len(lines) and lines[number].strip().startswith("|"):
            cells = [decode_references(strip_bold(cell.strip())) for cell in lines[number].strip().split("|")[1:-1]]
            number += 1
            if len(cells) < len(columns):
                continue
            row = dict(zip(columns, cells))
            finding_id = row.get(_PER_FINDING_ID_COLUMN, "").strip()
            if tachi_parts.id_matches("finding", finding_id):
                layers.setdefault(tachi_parts.canonical_finding_id(finding_id), row.get(_LAYER_COLUMN, "").strip())
    return layers


def parse_finding_layers(content: str) -> Dict[str, str]:
    """Each finding's MAESTRO layer, by canonical ID: the two finding-level steps of ADR-050 D2's layer chain (ruled at W4, T066's U-1).

    A finding's layer is the first of these that holds one for it:

    1. **Section 7's** ``MAESTRO Layer`` cell, where :func:`parse_reference_set` finds Section 7, in the table form;
    2. **the finding's own row in a per-finding table**: a table outside code fences whose header's first cell is ``ID`` and that has a
       ``MAESTRO Layer`` column (the template's §3 and §4 tables, and any table under them). v4.48.x threat models hold the layer only
       there, and the scorer of that version read it there.

    A value is the cell as :func:`parse_markdown_table` gives it (stripped, unbolded and decoded), stripped once more as each caller did
    before this reader, so whitespace that a reference decodes to at its edge never reaches the caller's checks or an output. A caller never
    decodes it again. A blank cell gives nothing, so the next source is asked, and an ID that neither source gives has no entry. Within a source, the first row of an
    ID is the one that counts, in file order, and Section 7 comes first. Tables whose first header cell isn't ``ID`` are never read, such
    as the Phase 1 inventory (``Component``), §6's ``Risk by MAESTRO Layer`` (``MAESTRO Layer``) and §4b's tables (``Finding ID``),
    and a row whose first cell isn't an allow-listed finding ID is ignored.

    It raises nothing on content and flags nothing when the two sources disagree: Section 7 wins (ADR-050 D2). It never reads the
    component's layer or infers one from other findings, so the caller's chain goes on to the component's Section 1 cell, then
    ``Unclassified``. The caller checks every value it takes for a forbidden character (P0-4), as it checks each other value that
    ``threats.md`` gives it.

    The reference set's refusal of a row with more cells than its header (M1) is not applied: a long row is read by the header's
    positions, as the extractors read it (NFR-1). ``examples/agentic-app`` has such rows in §4.2, each with its GFM ``\\|`` after the layer cell.
    Section 7's own rows are read as the reference set reads them, with GFM's ``\\|`` as a pipe in its cell (P1-3). The per-finding tables keep
    the extractors' rule: a ``\\|`` there splits the row.

    The scorer renderer, the controls renderer and the planner's controls unit row each take the layer from here, so the chain's three
    copies can't drift (the controls file's ``maestro-layer`` is the scorer file's, gap B).
    """
    layers: Dict[str, str] = {}
    for found in (_section_7_layers(content), _per_finding_layers(content.split("\n"))):
        for finding_id, layer in found.items():
            if layer:
                layers.setdefault(finding_id, layer)
    return layers


# =============================================================================
# Correlation groups (F-374 D8, T048) and the SARIF fallback reader (T142)
# =============================================================================

# Section 4a at heading level 2 or 3, with or without "Section": `## 4a.`, `### 4a.` and `## Section 4a:` are the
# forms that tachi's shipped samples show.
_CORRELATION_SECTION = r"^#{2,3}\s+(?:Section\s+)?4a[.:]"


def _assign_correlation_groups(raw_groups, members) -> list:
    """D8's four rules, written once for both readers of correlation groups.

    ``raw_groups`` is ``(group ID, listed member IDs)`` in file order, every member ID canonical. ``members`` is the
    file's member set, or ``None`` for no filtering. Groups keep their order, and members their listed order. The
    first group that lists an ID claims it, even if that group then falls away (so a later group never takes the ID
    over). The primary is the first member left after filtering to ``members``. A group left with fewer than two
    members is omitted. ``sarif_common.correlation_assignments`` re-applies the same rules to what this returns, and
    one test runs the same edge cases through both.
    """
    claimed: set = set()
    groups = []
    for group_id, listed in raw_groups:
        own = []
        for member in listed:
            if member not in claimed:
                claimed.add(member)
                own.append(member)
        remaining = [member for member in own if members is None or member in members]
        if len(remaining) >= 2:
            groups.append({"group_id": group_id, "primary": remaining[0], "members": remaining})
    return groups


def _group_names(group_ids: Sequence[str]) -> str:
    """``CG-1``, ``CG-1 and CG-2`` or ``CG-1, CG-2 and CG-3``."""
    return group_ids[0] if len(group_ids) == 1 else "%s and %s" % (", ".join(group_ids[:-1]), group_ids[-1])


def _repeated_members(raw_groups, members, groups) -> list:
    """The findings that more than one group lists, with what D8's claim rule did to each (PM W4 ruling R-F: never silent).

    ``raw_groups`` and ``members`` are :func:`_assign_correlation_groups`'s, and ``groups`` is what it returned for them. One entry
    for each finding that two or more groups list, in S-2 order: ``id``, ``claimed_by`` (the first group that lists it, which claims it
    even if that group then falls away), ``also_in`` (the other groups that list it, in file order), ``falls_away`` (the groups among
    those that would have been a group of two or more but for what earlier groups claimed, so they emit nothing) and ``reason``, a
    sentence for Input Issues that names the ID and every group. A group's own repeat of an ID is no second group, so it isn't listed.
    """
    claimed_by: dict = {}
    also_in: dict = {}
    eligible: dict = {}
    for group_id, listed in raw_groups:
        unique = list(dict.fromkeys(listed))
        eligible[group_id] = sum(1 for member in unique if members is None or member in members)
        for member in unique:
            if member in claimed_by:
                also_in.setdefault(member, []).append(group_id)
            else:
                claimed_by[member] = group_id
    emitted = {group["group_id"] for group in groups}
    repeated = []
    for member in sorted(also_in, key=tachi_parts.finding_sort_key):
        first, later = claimed_by[member], also_in[member]
        reason = "%s is listed in %s. %s claims it, and %s %s not." % (
            member, _group_names([first] + later), first, _group_names(later), "does" if len(later) == 1 else "do")
        if members is not None and member not in members:
            # An ID outside the run's open findings is in no group at all, so no group falls away because of it (ADR-050 D8, W4).
            reason += " It is not one of the run's open findings, so no group holds it."
            repeated.append({"id": member, "claimed_by": first, "also_in": list(later), "falls_away": [], "reason": reason})
            continue
        falls = [group_id for group_id in later if group_id not in emitted and eligible[group_id] >= 2]
        if falls:
            reason += " %s %s left with fewer than two findings and emit%s no correlation." % (
                _group_names(falls), "is" if len(falls) == 1 else "are", "s" if len(falls) == 1 else "")
        if first not in emitted:
            reason += " %s emits no correlation either, so %s is in no group." % (first, member)
        repeated.append({"id": member, "claimed_by": first, "also_in": list(later), "falls_away": falls, "reason": reason})
    return repeated


def parse_correlation_groups(content: str, member_ids: Optional[Iterable[str]] = None) -> dict:
    """The correlation groups of a ``threats.md`` Section 4a, by D8's rules (ADR-050 D8).

    Returns ``{"groups": [{"group_id", "primary", "members"}], "errors": [{"line", "row", "reason"}],
    "repeated": [{"id", "claimed_by", "also_in", "falls_away", "reason"}]}``.

    * **Order.** Groups come in Section 4a's order. ``members`` are canonical IDs in listed order, the primary first.
    * **The claim.** The first group that lists an ID claims it, even if that group then falls away. So a later group
      never takes the ID over, and an ID claimed by a group that falls away stays uncorrelated.
    * **The primary** is the first member left after filtering to ``member_ids`` (no filtering when ``None``).
    * **A group left with fewer than two members** is omitted.

    This is the one authority for those four rules. The scorer's routing and peer inheritance and both renderers'
    SARIF correlation use its result, and ``sarif_common.correlation_assignments``, which re-applies the rules to the
    groups it is given, agrees with it.

    **Never silent (PM W4 ruling R-F).** ``repeated`` has one entry for each finding that two or more groups list, in S-2
    order, whether or not it is in ``member_ids``: the claim rule drops it from every group but the first, and a reader
    of the run would otherwise never learn of it. ``claimed_by`` is the first group that lists it, ``also_in`` the others in file
    order, ``falls_away`` those of them that the loss left with fewer than two members, and ``reason`` a sentence that
    names the ID and every group, for the renderers' Input Issues. A group's own repeat of an ID is no second group. The rules
    above are unchanged, and no group differs from what they gave before.

    A row is skipped and listed in ``errors`` (``line`` is 1-based, ``row`` is the row as written, cut at 200
    characters) when its group ID isn't ``CG-N`` (``CG-[0-9]{1,6}``), when any member isn't a finding ID, when it lists
    no findings, when it has fewer cells than the table's header, or when it repeats an earlier row's group ID, so
    that each group ID names one group and one primary. A skipped row claims nothing. An empty or dash-only
    placeholder row is dropped without a report. A missing Section 4a, one with no table, and an empty one all give
    ``{"groups": [], "errors": [], "repeated": []}``.

    The section is read from its first table: the first column is the group and the second holds the
    comma-separated findings, as in every shipped sample. Its cells are decoded as :func:`parse_markdown_table`
    decodes them. A ``member_ids`` entry that isn't a finding ID raises ``ValueError``, because the caller took it
    from the reference set.
    """
    result: dict = {"groups": [], "errors": [], "repeated": []}
    start = match_heading(_CORRELATION_SECTION, content) if isinstance(content, str) and content else None
    if start is None:
        return result
    members = None if member_ids is None else {tachi_parts.canonical_finding_id(member) for member in member_ids}
    skipped: list = []
    at: list = []
    rows = parse_markdown_table(content, start_line=start, skipped=skipped, row_lines=at)
    problems = [(line, "has fewer cells than the table's header") for line in skipped]
    raw_groups = []
    first_line: dict = {}
    for row, line in zip(rows, at):
        cells = list(row.values())
        if len(cells) < 2:
            problems.append((line, "has no Group and Findings cells"))
            continue
        group_cell, findings_cell = cells[0], cells[1]
        if is_placeholder_id(group_cell) and is_placeholder_id(findings_cell):
            continue
        if not tachi_parts.id_matches("group", group_cell):
            problems.append((line, "names %r, which is not a correlation group ID" % group_cell[:40]))
            continue
        if is_placeholder_id(findings_cell):
            problems.append((line, "lists no findings"))
            continue
        listed = [token.strip() for token in findings_cell.split(",")]
        bad = next((token for token in listed if not tachi_parts.id_matches("finding", token)), None)
        if bad is not None:
            problems.append((line, "names %r, which is not a finding ID" % bad[:40]))
            continue
        if group_cell in first_line:
            problems.append((line, "repeats group ID %s, first listed at line %d" % (group_cell, first_line[group_cell])))
            continue
        first_line[group_cell] = line
        raw_groups.append((group_cell, [tachi_parts.canonical_finding_id(token) for token in listed]))
    result["groups"] = _assign_correlation_groups(raw_groups, members)
    result["repeated"] = _repeated_members(raw_groups, members, result["groups"])
    if problems:
        text_lines = content.split("\n")
        result["errors"] = [{"line": line, "row": text_lines[line - 1].strip()[:200], "reason": reason}
                            for line, reason in sorted(problems)]
    return result


# A legacy peer reference: an allow-listed finding ID at the start of a relatedLocations entry's message text,
# followed by ": " (sarif-specification.md, "Correlated Finding Mapping").
_SARIF_PEER_REFERENCE = re.compile("(?P<id>%s): " % tachi_parts.ID_PATTERNS["finding"], re.ASCII)
# The property names that the shipped risk-scores.sarif files use for a result's composite score and its band. The
# generator writes `composite` and `severity_band`, the agent contract (risk-scorer.md section 10g) has
# `security-severity` and `severity-band`, and one older sample writes `severity`.
_SARIF_COMPOSITE_PROPERTIES = ("composite", "security-severity")
_SARIF_BAND_PROPERTIES = ("severity-band", "severity_band", "severity")
_SARIF_BANDS = {"critical": "Critical", "high": "High", "medium": "Medium", "low": "Low"}


def _refuse_json_constant(name: str):
    raise ValueError("%s is not allowed" % name)


def _bounded_json_int(text: str) -> int:
    if len(text.lstrip("-")) > tachi_parts.MAX_INT_DIGITS:
        raise ValueError("integer literal of more than %d digits" % tachi_parts.MAX_INT_DIGITS)
    return int(text)


def _load_sarif(sarif_text) -> object:
    """``json.loads`` with D3's hooks: no ``NaN`` or ``Infinity``, floats as ``Decimal``, integers bounded, and a
    size backstop. Every way it can fail is a ``ValueError`` that never echoes the text."""
    if not isinstance(sarif_text, str):
        raise ValueError("the SARIF is not text")
    if len(sarif_text) > tachi_parts.MAX_AGENT_INPUT_BYTES:
        raise ValueError("the SARIF is over the %d byte cap" % tachi_parts.MAX_AGENT_INPUT_BYTES)
    try:
        return json.loads(sarif_text, parse_float=Decimal, parse_int=_bounded_json_int, parse_constant=_refuse_json_constant)
    except (ValueError, ArithmeticError, RecursionError):
        raise ValueError("the SARIF is not valid JSON") from None


def _sarif_composite(properties: dict) -> Optional[Decimal]:
    """A result's composite score from the first property that holds a finite number from 0 to 10, else ``None``."""
    for name in _SARIF_COMPOSITE_PROPERTIES:
        value = properties.get(name)
        if isinstance(value, str):
            value = parse_score(value)
        elif isinstance(value, (int, Decimal)) and not isinstance(value, bool):
            value = Decimal(value)
        else:
            continue
        if value is not None and value.is_finite() and Decimal(0) <= value <= Decimal(10):
            return value
    return None


def _sarif_band(properties: dict) -> Optional[str]:
    """A result's band, as ``Critical``, ``High``, ``Medium`` or ``Low``, from the first property that names one."""
    for name in _SARIF_BAND_PROPERTIES:
        value = properties.get(name)
        if isinstance(value, str) and value.strip().lower() in _SARIF_BANDS:
            return _SARIF_BANDS[value.strip().lower()]
    return None


def _sarif_is_absent(result: dict, properties: dict) -> bool:
    """True for a RESOLVED result: ``absent`` as the result's own ``baselineState``, or as a ``baselineState`` or
    ``baseline-state`` property (R-30)."""
    return any(isinstance(source.get(key), str) and source[key].strip().lower() == "absent"
               for source, key in ((result, "baselineState"), (properties, "baselineState"), (properties, "baseline-state")))


def _sarif_entry(result: dict, properties: dict, fingerprints: dict, finding_id: str) -> dict:
    """What one kept result says about correlation: its group ID, its role, its primary and its legacy peer references."""
    group = properties.get("correlation-group")
    if not tachi_parts.id_matches("group", group):
        group = fingerprints.get("correlationGroup")  # the legacy spelling, in partialFingerprints
    role = properties.get("correlation-role")
    primary = properties.get("correlation-primary")
    references = []
    related = result.get("relatedLocations")
    for location in related if isinstance(related, list) else []:
        message = location.get("message") if isinstance(location, dict) else None
        text = message.get("text") if isinstance(message, dict) else None
        match = _SARIF_PEER_REFERENCE.match(text) if isinstance(text, str) else None
        if match is not None:
            references.append(tachi_parts.canonical_finding_id(match.group("id")))
    return {
        "id": finding_id,
        "group": group if tachi_parts.id_matches("group", group) else None,
        "role": role if role in ("primary", "peer") else None,
        "primary": tachi_parts.canonical_finding_id(primary) if tachi_parts.id_matches("finding", primary) else None,
        "references": [reference for reference in references if reference != finding_id],
        "composite": _sarif_composite(properties),
        "band": _sarif_band(properties),
    }


def _sarif_text(*values) -> Optional[str]:
    """The first of ``values`` that is a string with something in it, else ``None``. A missing key, an empty or blank
    string and a value of any other type all count as "the result holds none" (D8)."""
    return next((value for value in values if isinstance(value, str) and value.strip()), None)


def _sarif_logical_location(result: dict) -> dict:
    """The result's logical location, as an object: ``locations[0].logicalLocations[0]``, else the singular
    ``locations[0].logicalLocation`` that tachi's older scorer and controls SARIF write (ADR-050 D8, ruled at W3), else ``{}``.

    It is one object either way (``name``, ``fullyQualifiedName``, ``kind``). The plural form wins when its first entry is
    an object, so a result that carries both reads as its plural form says. A value that isn't an object doesn't count.
    """
    locations = result.get("locations")
    location = locations[0] if isinstance(locations, list) and locations else None
    if not isinstance(location, dict):
        return {}
    logical = location.get("logicalLocations")
    logical = logical[0] if isinstance(logical, list) and logical else None
    if not isinstance(logical, dict):
        logical = location.get("logicalLocation")
    return logical if isinstance(logical, dict) else {}


def _sarif_details(result: dict, properties: dict) -> dict:
    """D8's reading of what one result says about its own finding (P0-3), the same for either ID form.

    ``component`` is the logical location's ``name``, else ``properties.component``. ``threat`` is ``message.text`` and
    ``mitigation`` is ``message.markdown``. ``risk_level`` is ``properties.risk_level``, else ``properties.severity``,
    else ``security-severity``: a word before a score (ADR-050 D8, ruled at W3), and each as the file writes it, so a score
    is not turned into a band here. ``layer`` is ``maestro-layer``. ``kind`` is the logical location's ``kind``, which the
    renderer reads from the same result. The logical location is ``locations[0].logicalLocations[0]``, else the singular
    ``locations[0].logicalLocation`` (see :func:`_sarif_logical_location`). Each value is the string as written, or
    ``None``. Nothing here raises: a result of any other shape reads as holding none.
    """
    logical = _sarif_logical_location(result)
    message = result.get("message") if isinstance(result.get("message"), dict) else {}
    return {
        "component": _sarif_text(logical.get("name"), properties.get("component")),
        "threat": _sarif_text(message.get("text")),
        "mitigation": _sarif_text(message.get("markdown")),
        "risk_level": _sarif_text(properties.get("risk_level"), properties.get("severity"),
                                  properties.get("security-severity")),
        "layer": _sarif_text(properties.get("maestro-layer")),
        "kind": _sarif_text(logical.get("kind")),
    }


def parse_sarif_member_set(sarif_text: str, *, with_scores: bool = False, with_details: bool = False) -> dict:
    """D8's fallback reader: the member set, the groups, the scores (for ``risk-scores.sarif``) and each member's text.

    Returns ``{"members": [...], "groups": [...], "scores": {...}}``, and a fourth key, ``details``, only when
    ``with_details`` is true, so the default call returns what it always did.

    * ``members`` are canonical finding IDs, one per ``runs[0].results[]`` entry, in result order, each ID once. A
      result's ID is its ``partialFingerprints["findingId/v1"]``, or, when it has none, its ``properties.id`` (tachi's
      older samples carry the ID only there). ``findingId/v1`` wins when both are present, and a result whose ID isn't
      allow-listed is ignored. No hash is ever read. A legacy peer reference follows its result: an allow-listed ID at
      the start of a ``relatedLocations`` entry's ``message.text``, followed by ``: ``.
    * Results whose ``baselineState`` (as the result's own key or a property) or ``baseline-state`` property is
      ``absent`` are RESOLVED, and appear nowhere: not as members, not as references, not in a group, not in scores.
    * ``groups`` take the shape :func:`parse_correlation_groups` returns, from D8's one set of rules. A group comes
      from the ``correlation-group``, ``correlation-role`` and ``correlation-primary`` properties, from a result that
      has only ``correlation-primary`` (the form older samples show: a peer names its primary), or from a legacy
      primary and its peer references. ``group_id`` is the ``correlation-group`` property, or the legacy
      ``correlationGroup`` fingerprint, and is ``None`` where the file names none. One group ID names one group.
      Named groups come in group-number order (``CG-1`` before ``CG-2``, which is Section 4a's order, so an ID that
      two groups list goes to the same group as in the Section 4a reader), then the unnamed ones in the order their
      first result appears. An unnamed group has the same shape: its ``primary`` is the first result's ID and
      ``members`` lists it first, so a caller can route its peers. No ID names it, so a caller passes only the named
      groups to ``sarif_common.correlation_assignments``, which raises on a ``None`` group ID, and counts the others
      (D8, P0-3).
    * ``scores`` is ``{}`` unless ``with_scores``. Then each member that has a result maps to
      ``{"composite": Decimal or None, "band": str or None}``, from the first such result. The composite is read from
      ``composite`` or ``security-severity``, the band from ``severity-band``, ``severity_band`` or ``severity``. A
      value that isn't a number from 0 to 10, or a band name, is ``None``.
    * ``details`` is in the return only with ``with_details`` (P0-3). Then it maps each member that has a result of its
      own, with either ID form, to D8's reading of that result, from the first such result (see
      :func:`_sarif_details`): ``component``, ``threat``, ``mitigation``, ``risk_level``, ``layer`` and ``kind``, each a
      string as written or ``None``. A member that only a legacy peer reference names has no entry. Nothing is escaped
      or checked here: a caller that writes a value checks it where it takes it (P0-4).

    It raises ``ValueError`` on text that is not JSON (no ``NaN`` or ``Infinity``, an integer of over 20 digits, or
    nesting too deep) and on an empty extraction, so the stage stops before dispatch (KB 22). The error names the
    remedy: regenerate the markdown input. Nothing else raises: a result of any other shape is skipped.
    """
    document = _load_sarif(sarif_text)
    runs = document.get("runs") if isinstance(document, dict) else None
    run = runs[0] if isinstance(runs, list) and runs else None
    results = run.get("results") if isinstance(run, dict) else None
    entries = []
    kept: set = set()
    dropped: set = set()
    details: dict = {}
    for result in results if isinstance(results, list) else []:
        if not isinstance(result, dict):
            continue
        properties = result.get("properties") if isinstance(result.get("properties"), dict) else {}
        fingerprints = result.get("partialFingerprints") if isinstance(result.get("partialFingerprints"), dict) else {}
        identifier = fingerprints.get("findingId/v1")
        if identifier is None:  # tachi's older SARIF has no fingerprint and carries the ID as properties.id (D8, option b)
            identifier = properties.get("id")
        if not tachi_parts.id_matches("finding", identifier):
            continue
        finding_id = tachi_parts.canonical_finding_id(identifier)
        if _sarif_is_absent(result, properties):
            dropped.add(finding_id)
            continue
        kept.add(finding_id)
        entries.append(_sarif_entry(result, properties, fingerprints, finding_id))
        if with_details and finding_id not in details:
            details[finding_id] = _sarif_details(result, properties)
    resolved = dropped - kept
    members: list = []
    scores: dict = {}
    seen: set = set()
    for entry in entries:
        for member in [entry["id"]] + [reference for reference in entry["references"] if reference not in resolved]:
            if member not in seen:
                seen.add(member)
                members.append(member)
        if with_scores and entry["id"] not in scores:
            scores[entry["id"]] = {"composite": entry["composite"], "band": entry["band"]}
    if not members:
        raise ValueError("the SARIF holds no open finding: no result in runs[0] has a finding ID, in findingId/v1 or "
                         "properties.id, that isn't absent. Remedy: regenerate the markdown input")
    # One group per primary (or, where no primary is named, per group ID), in the order its first result appears.
    records: dict = {}
    for entry in entries:
        references = [reference for reference in entry["references"] if reference not in resolved]
        if references or entry["role"] == "primary" or entry["primary"] == entry["id"]:
            primary, peers = entry["id"], references
        elif entry["primary"] is not None:
            primary, peers = entry["primary"], [entry["id"]]
        elif entry["group"] is not None:
            primary, peers = None, [entry["id"]]
        else:
            continue
        key = ("primary", primary) if primary is not None else ("group", entry["group"])
        record = records.setdefault(key, {"group_id": None, "primary": primary, "members": []})
        if record["group_id"] is None:
            record["group_id"] = entry["group"]
        record["members"].extend(([primary] if primary is not None else []) + peers)
    named: dict = {}
    unnamed: list = []
    for record in records.values():
        ordered = [record["primary"]] if record["primary"] is not None else []
        ordered.extend(member for member in dict.fromkeys(record["members"]) if member != record["primary"])
        if record["group_id"] is None:
            unnamed.append((None, ordered))
        else:
            named.setdefault(record["group_id"], []).extend(ordered)  # one group ID names one group
    # Named groups in group-number order, which is Section 4a's order, so the claim goes where the Section 4a reader
    # gives it. Then the groups the file doesn't name, in the order their first result appears.
    raw_groups = [(group_id, list(dict.fromkeys(named[group_id]))) for group_id in sorted(named, key=lambda g: int(g[3:]))]
    found = {"members": members, "groups": _assign_correlation_groups(raw_groups + unnamed, set(members)), "scores": scores}
    if with_details:
        found["details"] = details
    return found


# =============================================================================
# The controls file's persisted inputs (F-374 AR-T3, T143)
# =============================================================================

_ASSESSMENT_INPUTS_HEADING = r"^###\s+Assessment Inputs\s*$"
_CONTROLS_SCALAR_FIELDS = ("control_status", "control_category", "confidence", "carried_forward", "matrix_row", "recommendation_body")
_EVIDENCE_FIELDS = ("file", "line", "language", "snippet", "summary")
_EVIDENCE_ADDRESS = re.compile(r"evidence\.(?P<index>0|[1-9][0-9]*)\.(?P<rest>[a-z_.]+)", re.ASCII)
_MAX_EVIDENCE_ENTRIES = 5


def _controls_input(field: str, value: str):
    """One persisted row's value, checked against its class: ``(path, parsed)``, or ``ValueError(reason)``.

    ``path`` is the value's place in the item: ``("control_status",)``, ``("evidence", 2, "summary")`` or
    ``("evidence", 0, "assessment", "currency", "rating")``. Closed values are checked against their enum or pattern,
    as the part validator checks them. Narrative and evidence-class text comes back as it is: it is re-validated, and
    its slots re-resolved, where it is used.
    """
    if field in _CONTROLS_SCALAR_FIELDS:
        path: tuple = (field,)
    else:
        address = _EVIDENCE_ADDRESS.fullmatch(field)
        if address is None or int(address.group("index")) >= _MAX_EVIDENCE_ENTRIES:
            raise ValueError("%r is not a field of a controls item" % field[:40])
        rest = address.group("rest").split(".")
        index = int(address.group("index"))
        if len(rest) == 1 and rest[0] in _EVIDENCE_FIELDS:
            path = ("evidence", index, rest[0])
        elif len(rest) == 3 and rest[0] == "assessment" and rest[1] in tachi_parts.ASSESSMENT_DIMENSIONS and rest[2] in ("rating", "rationale"):
            path = ("evidence", index, "assessment", rest[1], rest[2])
        else:
            raise ValueError("%r is not a field of a controls item" % field[:40])
    name = path[-1]
    if name == "control_status" and value not in tachi_parts.CONTROL_STATUSES:
        raise ValueError("control_status is not found, partial or missing")
    if name == "control_category" and value not in tachi_parts.CONTROL_CATEGORIES:
        raise ValueError("control_category is not one of the eight categories")
    if name in ("confidence", "rating") and value not in tachi_parts.CONFIDENCES:
        raise ValueError("%s is not High, Medium or Low" % name)
    if name == "carried_forward":
        if value not in ("true", "false"):
            raise ValueError("carried_forward is not true or false")
        return path, value == "true"
    if name == "file" and not (1 <= len(value) <= 300 and tachi_parts.path_problem(value) is None):
        raise ValueError("evidence.file breaks D7's relative path rule")
    if name == "line":
        if re.fullmatch(r"[1-9][0-9]{0,8}", value) is None:
            raise ValueError("evidence.line is not an integer of 1 or more")
        return path, int(value)
    if name == "language" and not tachi_parts.id_matches("language", value):
        raise ValueError("evidence.language does not match the language pattern")
    return path, value


def _controls_item(rows: list) -> dict:
    """One finding's persisted rows, ``[(path, value)]`` in file order, as a controls item; ``ValueError`` if it is incomplete.

    The item has the keys of ``contracts/part-files.md``'s controls payload, less ``finding_id``, in its order, with
    the null forms the format leaves unwritten (``confidence`` and ``recommendation_body`` as ``None``, ``evidence``
    as ``[]``). It is checked the way the part validator checks an item, so an item that comes back could be a part's.
    """
    item: dict = {}
    entries: dict = {}
    for path, value in rows:
        if path[0] == "evidence":
            entry = entries.setdefault(path[1], {})
            target, keys = (entry.setdefault("assessment", {}).setdefault(path[3], {}), path[4:]) if len(path) == 5 else (entry, path[2:])
            target[keys[0]] = value
        else:
            item[path[0]] = value
    for name in ("control_status", "control_category", "carried_forward", "matrix_row"):
        if name not in item:
            raise ValueError("it has no %s row" % name)
    status = item["control_status"]
    if (status == "missing") != ("confidence" not in item):
        raise ValueError("confidence is written exactly when the status isn't missing")
    if (status == "found") != ("recommendation_body" not in item):
        raise ValueError("recommendation_body is written exactly when the status isn't found")
    if (status == "missing") != (not entries):
        raise ValueError("evidence has 1 to %d entries for found or partial, and none for missing" % _MAX_EVIDENCE_ENTRIES)
    if sorted(entries) != list(range(len(entries))):
        raise ValueError("the evidence entries are not indexed from 0 without a gap")
    evidence = []
    for index in range(len(entries)):
        entry = entries[index]
        for name in _EVIDENCE_FIELDS:
            if name not in entry:
                raise ValueError("evidence entry %d has no %s row" % (index, name))
        assessment = entry.get("assessment")
        if assessment is not None and not all(set(assessment.get(dimension, ())) == {"rating", "rationale"} for dimension in tachi_parts.ASSESSMENT_DIMENSIONS):
            raise ValueError("evidence entry %d has an incomplete assessment" % index)
        ordered = {name: entry[name] for name in _EVIDENCE_FIELDS}
        if assessment is not None:
            ordered["assessment"] = {dimension: {"rating": assessment[dimension]["rating"], "rationale": assessment[dimension]["rationale"]}
                                     for dimension in tachi_parts.ASSESSMENT_DIMENSIONS}
        evidence.append(ordered)
    return {"control_status": status, "control_category": item["control_category"], "confidence": item.get("confidence"),
            "carried_forward": item["carried_forward"], "evidence": evidence, "matrix_row": item["matrix_row"],
            "recommendation_body": item.get("recommendation_body")}


def parse_controls_assessment_inputs(content: str) -> dict:
    """Each finding's persisted controls result, from a 1.1 ``compensating-controls.md``'s ``### Assessment Inputs`` (AR-T3).

    Returns ``{"inputs": {finding ID: item}, "errors": [{"line", "row", "reason"}]}``, the IDs canonical and in S-2 order.
    An item is the controls payload as ``contracts/part-files.md`` keys it, without ``finding_id``: ``control_status``,
    ``control_category``, ``confidence``, ``carried_forward`` (a ``bool``), ``evidence`` (a list of ``file``, ``line``
    (an ``int``), ``language``, ``snippet`` and ``summary``, and an optional ``assessment`` of the four dimensions, each
    a ``rating`` and a ``rationale``), ``matrix_row`` and ``recommendation_body``. It is read, decoded, from the
    format ``contracts/module-signatures.md`` fixes: a table of ``ID``, ``Field`` and ``Value``, one row for each
    value that exists, the field being the value's dotted address (``evidence.0.summary``). Narrative values keep their
    slot tokens, and evidence-class values come back as written, ``**`` markers included (``keep_bold``).
    ``parse_markdown_table`` decodes each cell, so nothing here decodes a value again: a carried value is escaped once
    per render and reads back the same bytes.

    Closed values are re-checked against their enum or pattern, and an item has to be complete and consistent, as the part
    validator requires of one. A row whose field isn't in the payload's closed key set, whose value fails its check, or
    whose ID or cell count is wrong goes to ``errors``, and the item it belongs to is left out, so no stage carries a
    result that it can't trust. An item that is incomplete is left out with an error at its first row. A file with no
    ``### Assessment Inputs`` (a pre-1.1 file) gives ``{"inputs": {}, "errors": []}``, as does one whose table has no
    row. A table without ``ID``, ``Field`` and ``Value`` columns is one error and no input.

    The heading is found outside code fences (ruled at W3). A §3 evidence snippet is written raw inside a fence, and a
    snippet that quotes a tachi report holds this heading and a table of its own, which must not stand in for §7.
    """
    result: dict = {"inputs": {}, "errors": []}
    start = (match_heading(_ASSESSMENT_INPUTS_HEADING, content, outside_fences=True)
             if isinstance(content, str) and content else None)
    if start is None:
        return result
    skipped: list = []
    at: list = []
    rows = parse_markdown_table(content, start_line=start, skipped=skipped, row_lines=at, keep_bold=True)
    text_lines = content.split("\n")
    problems = [(line, "has fewer cells than the table's header") for line in skipped]
    if rows and {"ID", "Field", "Value"} - set(rows[0]):
        problems = [(at[0], "the table has no ID, Field and Value columns")]
        rows = []
    collected: dict = {}
    spoiled: set = set()
    seen: set = set()
    for row, line in zip(rows, at):
        if not tachi_parts.id_matches("finding", row["ID"]):
            problems.append((line, "names %r, which is not a finding ID" % row["ID"][:40]))
            continue
        finding_id = tachi_parts.canonical_finding_id(row["ID"])
        try:
            path, value = _controls_input(row["Field"], row["Value"])
            if (finding_id, path) in seen:
                raise ValueError("%s repeats the value %s" % (finding_id, ".".join(str(part) for part in path)))
        except ValueError as exc:
            problems.append((line, str(exc)))
            spoiled.add(finding_id)
            continue
        seen.add((finding_id, path))
        collected.setdefault(finding_id, []).append((line, path, value))
    for finding_id in sorted(collected, key=tachi_parts.finding_sort_key):
        if finding_id in spoiled:
            continue
        try:
            result["inputs"][finding_id] = _controls_item([(path, value) for _, path, value in collected[finding_id]])
        except ValueError as exc:
            problems.append((collected[finding_id][0][0], "%s: %s" % (finding_id, exc)))
    result["errors"] = [{"line": line, "row": text_lines[line - 1].strip()[:200], "reason": reason} for line, reason in sorted(problems)]
    return result


# Tier 2 referential-integrity validator: resolves each record's id against
# the catalog YAMLs in schemas/taxonomy/. Stdlib-only (no pyyaml).

_CATALOG_ID_PATTERN = re.compile(r"^- id: (\S+)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class ValidationError:
    """Referential-integrity failure: a record's id did not resolve in its catalog."""

    finding_id: str
    record: dict
    target_yaml_path: str
    reason: str


def _load_catalog_ids(taxonomy: str, taxonomy_dir: Path) -> frozenset:
    """Return the set of top-level ``- id: <value>`` keys from a catalog YAML."""
    catalog_path = taxonomy_dir / f"{taxonomy}.yaml"
    text = catalog_path.read_text()
    return frozenset(_CATALOG_ID_PATTERN.findall(text))


def validate_source_attribution(
    findings: list,
    taxonomy_dir: Path = Path("schemas/taxonomy"),
) -> list:
    """Validate referential integrity of source_attribution records.

    For every finding with ``source_attribution``, resolve each record's ``id``
    against a top-level key in ``{taxonomy_dir}/{taxonomy}.yaml``. Returns a
    list of ValidationError (empty on success). Catalog YAMLs are read at
    most once per call via a local cache — no module-level state.
    """
    catalog_cache: dict = {}
    errors: list = []
    for finding in findings:
        if "source_attribution" not in finding:
            continue
        finding_id = finding.get("id", "")
        for record in finding["source_attribution"]:
            taxonomy = record["taxonomy"]
            if taxonomy not in catalog_cache:
                catalog_cache[taxonomy] = _load_catalog_ids(taxonomy, taxonomy_dir)
            record_id = record["id"]
            if record_id not in catalog_cache[taxonomy]:
                errors.append(
                    ValidationError(
                        finding_id=finding_id,
                        record=dict(record),
                        target_yaml_path=str(taxonomy_dir / f"{taxonomy}.yaml"),
                        reason=(
                            f"id {record_id!r} not found as a top-level "
                            f"'- id:' key in the catalog"
                        ),
                    )
                )
    return errors


def parse_risk_scores_findings(content: str) -> list:
    """Parse risk-scores.md Section 2 Scored Threat Table for Tier 2 findings."""
    rows = parse_markdown_table(content, "## 2. Scored Threat Table")
    if not rows:
        print("Warning: could not find Scored Threat Table in risk-scores.md", file=sys.stderr)
        return []

    findings = []
    for row in rows:
        findings.append({
            "id": row.get("ID", "").strip(),
            "component": row.get("Component", "").strip(),
            "threat": row.get("Threat", "").strip(),
            "composite_score": row.get("Composite", "").strip(),
            "severity": row.get("Severity", "").strip(),
            "cvss": row.get("CVSS", "").strip(),
            "exploitability": row.get("Exploit.", "").strip(),
        })
    return findings


def composite_scores_by_id(rs_findings):
    """K11 join map ``{id: Decimal | None}`` from :func:`parse_risk_scores_findings` rows (data-model.md §3)."""
    return {f["id"]: parse_score(f["composite_score"]) for f in rs_findings if f.get("id")}


# =============================================================================
# Component Distribution
# =============================================================================

def parse_component_distribution(findings: list) -> list:
    """Count findings per component, sorted by count descending."""
    counts = {}
    for f in findings:
        comp = f.get("component", "")
        if comp:
            counts[comp] = counts.get(comp, 0) + 1

    # Sort by count descending, then by name ascending for determinism
    return sorted(counts.items(), key=lambda x: (-x[1], x[0]))


# =============================================================================
# Scope Data Parser
# =============================================================================

def parse_scope_data(content: str) -> dict:
    """Parse scope data from threats.md Sections 1-2.

    Extracts components, data flows, trust zones, and boundary crossings.
    """
    result = {
        "components": [],
        "data_flows": [],
        "trust_boundaries": [],
        "boundary_crossings": [],
    }

    # Section 1: Components table
    comp_rows = parse_markdown_table(content, "### Components")
    for row in comp_rows:
        result["components"].append({
            "name": row.get("Component", "").strip(),
            "type": row.get("Type", "").strip(),
            "description": row.get("Description", "").strip(),
        })

    # Section 1: Data Flows table
    df_rows = parse_markdown_table(content, "### Data Flows")
    for row in df_rows:
        result["data_flows"].append({
            "source": row.get("Source", "").strip(),
            "destination": row.get("Destination", "").strip(),
            "data": row.get("Data", "").strip(),
            "protocol": row.get("Protocol", "").strip(),
        })

    # Section 2: Trust Zones table
    tz_rows = parse_markdown_table(content, "### Trust Zones")
    for row in tz_rows:
        result["trust_boundaries"].append({
            "zone": row.get("Zone", "").strip(),
            "trust-level": row.get("Trust Level", "").strip(),
            "components": row.get("Components", "").strip(),
        })

    # Section 2: Boundary Crossings table
    bc_rows = parse_markdown_table(content, "### Boundary Crossings")
    for row in bc_rows:
        result["boundary_crossings"].append({
            "crossing": row.get("Crossing", "").strip(),
            "from-zone": row.get("From Zone", "").strip(),
            "to-zone": row.get("To Zone", "").strip(),
            "components": row.get("Components", "").strip(),
            "controls": row.get("Controls", "").strip(),
        })

    if not result["components"] and not result["data_flows"]:
        print("Warning: scope data not found in threats.md — scope page will show limited data", file=sys.stderr)

    return result


# =============================================================================
# Compensating Controls Parser
# =============================================================================

_WHAT_TO_IMPLEMENT = "**What to Implement**:"
# A "What to Implement" text goes on over the lines that follow it until one of these starts a line (a `####` heading
# starts with `###`), or a line is blank.
_RECOMMENDATION_STOPS = ("**", "###", "---")


def _what_to_implement(block_lines: Sequence[str]) -> Optional[str]:
    """The decoded "What to Implement" text of one Section 4 block, or ``None`` when no line of ``block_lines`` opens
    one. It is the body of :func:`recommendation_text`, which maps ``None`` to ``""``. The controls reader keeps the
    difference, because a block whose marker has no text still replaces an earlier block's text for the same ID."""
    for at, raw in enumerate(block_lines):
        line = raw.strip()
        if not line.startswith(_WHAT_TO_IMPLEMENT):
            continue
        text = line.replace(_WHAT_TO_IMPLEMENT, "").strip()
        # Read continuation lines until the next marker
        for following in range(at + 1, len(block_lines)):
            next_line = block_lines[following].strip()
            if not next_line or next_line.startswith(_RECOMMENDATION_STOPS):
                break
            text += " " + next_line
        # D3: the text is decoded once, after the lines that bound it are found on the raw text.
        return decode_references(text.strip())
    return None


def recommendation_text(block_lines: Sequence[str]) -> str:
    """The "What to Implement" text of one Section 4 block of ``compensating-controls.md``, decoded, or ``""`` when
    the block has none (F-374 T146, T067b H1).

    ``block_lines`` are the lines of one block: the lines under its ``#### n. ID —`` heading, up to the line before the
    next such heading. The heading line itself may be included, because it is not a marker. This is the rule that
    :func:`parse_compensating_controls_md` has always applied to a block, which it now calls with its own bounds, so
    the controls readers and every shipped example read as they did (NFR-1). A renderer that checks its SARIF against
    its markdown finds a block by its own route and applies this same rule to it, so the check can't agree with a
    reader that lost the text.

    The first line that starts with ``**What to Implement**:``, after its edge whitespace is stripped, opens the text.
    The text is what follows the marker on that line, then each following line, stripped, joined with single spaces, up
    to the first blank line or the first line that starts with ``**``, ``###`` (so ``####`` too) or ``---``. A second
    marker in the block is ignored. :func:`decode_references` runs once on the joined text, after the lines that bound
    it are found on the raw text (D3), so text that was already decoded is decoded again.

    A ``str`` raises ``TypeError``: it would read as lines of one character each and return ``""`` without a word.
    """
    if isinstance(block_lines, str):
        raise TypeError("recommendation_text takes the lines of one block, not a string")
    text = _what_to_implement(block_lines)
    return "" if text is None else text


def parse_compensating_controls_md(content: str, composites_by_id: dict = None) -> dict:
    """Parse compensating-controls.md for Tier 1 data.

    Extracts:
    - Tier 1 findings from Section 2 Coverage Matrix (by residual severity)
    - STRIDE coverage matrix (derived from findings by threat ID prefix)
    - Coverage summary from Section 1 Coverage Distribution
    - Controls from Section 3 Control Details
    - Recommendations from Section 4 (merged into findings)
    - Severity counts from residual severity of findings

    Args:
        content: Full compensating-controls.md text.
        composites_by_id: Optional ``{threat_id: Decimal}`` map of risk-scores
            composite scores (K11, data-model.md §3), used to fill a row's
            ``inherent`` when the Coverage Matrix has no Inherent Score/
            Inherent column, or the cell is unparseable. Typically built by
            :func:`composite_scores_by_id` from
            :func:`parse_risk_scores_findings`'s rows.

    Each finding dict additionally carries (K11):
        status_class: "found" | "partial" | "none", from
            :func:`classify_control_status`.
        inherent: the row's inherent score as a ``Decimal``, or ``None`` when
            unavailable even after the join.
        inherent_severity: the inherent score's severity band (Title Case),
            falling back to the raw ``Inherent Severity`` column, or ``None``.
        residual_score / residual_severity: unchanged in shape, but now
            reflect the post-clamp value when a clamp applied.

    And (T057, FR-K8.2), read by header name from each band table, so K8's corrected
    schema and the pre-fix one give the same rows:
        maestro_layer / control_category: the row's ``MAESTRO Layer`` and
            ``Control Category`` cells, or ``""`` when its table has no such column.
        carried_forward: ``True`` when the row's ``CF`` cell is ``CF`` (the
            carried-forward marker, R-20), ``False`` for a dash (``—``), an empty cell
            or a table with no ``CF`` column.
    """
    result = {
        "findings": [],
        "coverage_matrix": [],
        "controls": [],
        "coverage_summary": {"total-found": 0, "total-partial": 0, "total-missing": 0},
        "severity": {"critical": 0, "high": 0, "medium": 0, "low": 0, "note": 0, "total": 0},
        "risk_reduction": None,      # e.g. 22.9
        "inherent_score": None,      # e.g. 270.3
        "residual_score": None,      # e.g. 208.5
        "control_coverage_pct": None, # e.g. 26.0 (Found percentage)
    }

    if not content or not content.strip():
        return result

    lines = content.split("\n")

    # ---- Section 1: Executive Summary risk metrics ----
    # Parse: **Risk Reduction**: 270.3 inherent -> 208.5 residual (**22.9%** reduction)
    rr_match = re.search(
        r"\*\*Risk Reduction\*\*:\s*([\d.]+)\s*inherent\s*->\s*([\d.]+)\s*residual\s*\(\*\*([\d.]+)%\*\*",
        content,
    )
    if rr_match:
        result["inherent_score"] = float(rr_match.group(1))
        result["residual_score"] = float(rr_match.group(2))
        result["risk_reduction"] = float(rr_match.group(3))

    # Parse: **Coverage**: 26% Found | 34% Partial | 40% Missing
    cov_match = re.search(
        r"\*\*Coverage\*\*:\s*([\d.]+)%\s*Found",
        content,
    )
    if cov_match:
        result["control_coverage_pct"] = float(cov_match.group(1))

    # ---- Section 4: Recommendations (parse first to merge into findings) ----
    recommendations = {}  # threat_id -> recommendation text
    sec4_start = None
    sec4_end = len(lines)
    for i, line in enumerate(lines):
        if re.match(r"^##\s+4\.\s+Recommendations", line):
            sec4_start = i + 1
        elif sec4_start is not None and re.match(r"^##\s+\d+\.", line):
            sec4_end = i
            break

    if sec4_start is not None:
        # One block per heading, up to the next heading (or the end of Section 4). A line before the first heading
        # belongs to no block, and a later block that has a marker replaces an earlier block's text for the same ID.
        headings = []  # (line index, threat ID)
        for i in range(sec4_start, sec4_end):
            # Match: #### 1. S-3 -- Component (Composite: 9.2, Critical)
            heading_match = re.match(r"^####\s+\d+\.\s+(\S+)\s+[—\-]", lines[i].strip())
            if heading_match:
                headings.append((i, heading_match.group(1)))
        for (at, threat_id), (block_end, _) in zip(headings, headings[1:] + [(sec4_end, None)]):
            rec_text = _what_to_implement(lines[at + 1:block_end])
            if rec_text is not None:
                recommendations[threat_id] = rec_text

    # ---- Section 2: Coverage Matrix findings ----
    # Severity band thresholds for score-based classification
    _BAND_THRESHOLDS = [(9.0, "Critical"), (7.0, "High"), (4.0, "Medium")]

    def _band_from_score(score):
        """Map a parsed Decimal score (or None) to its Title Case band, or None."""
        if score is None:
            return None
        for threshold, band in _BAND_THRESHOLDS:
            if score >= threshold:
                return band
        return "Low"

    # Aggregated-warning collectors (data-model.md §3; R-P6: one line per
    # class, count plus the first five IDs in first-seen order).
    _unrecognized_status_ids = []
    _unparseable_score_refs = []   # "id:Column Name" strings
    _missing_residual_ids = []
    _missing_inherent_ids = []
    _clamped_ids = []

    for severity_label in ["Critical", "High", "Medium", "Low"]:
        header = f"### {severity_label} Residual Severity"
        rows = parse_markdown_table(content, header)
        for row in rows:
            threat_id = row.get("Threat ID", "").strip()
            if is_placeholder_id(threat_id):
                # FR-K9.2: a placeholder Threat ID drops the row before dedup.
                continue
            aliased = _resolve_row_fields(row)
            residual_text = aliased["residual_score"].strip()
            inherent_text = aliased["inherent_score"].strip()
            control_status_raw = aliased["control_status"].strip()

            # Unparseable-score warnings fire only for non-empty garbage text
            # (em dash, trailing text, NaN) — a genuinely absent column or
            # blank cell is silently None here; its own consequence (missing
            # residual/inherent) warns on its own below.
            residual = parse_score(residual_text)
            if residual is None and residual_text:
                _unparseable_score_refs.append(f"{threat_id}:Residual Score")

            inherent = parse_score(inherent_text)
            if inherent is None and inherent_text:
                _unparseable_score_refs.append(f"{threat_id}:Inherent Score")
            if inherent is None and composites_by_id:
                inherent = composites_by_id.get(threat_id)
            if inherent is None:
                _missing_inherent_ids.append(threat_id)

            status_class, status_warn = classify_control_status(control_status_raw)
            if status_warn:
                _unrecognized_status_ids.append(threat_id)

            # Clamp once, at parse (data-model.md §3): residual can never
            # exceed inherent. A missing residual with an inherent present
            # means residual = inherent (no credit) — both need `inherent`.
            if residual is not None and inherent is not None and residual > inherent:
                _clamped_ids.append(threat_id)
                residual = inherent
            elif residual is None and inherent is not None:
                _missing_residual_ids.append(threat_id)
                residual = inherent

            residual_band = _band_from_score(residual)
            if residual_band is None:
                residual_band = aliased["residual_severity"].strip() or severity_label

            inherent_band = _band_from_score(inherent)
            if inherent_band is None:
                inherent_band = aliased["inherent_severity"].strip() or None

            residual_score_display = str(residual) if residual is not None else residual_text
            k8 = _resolve_k8_fields(row)

            result["findings"].append({
                "id": threat_id,
                "component": row.get("Component", "").strip(),
                "threat": row.get("Threat", "").strip(),
                "residual_score": residual_score_display,
                "residual_severity": residual_band,
                "control_status": control_status_raw,
                "status_class": status_class,
                "inherent": inherent,
                "inherent_severity": inherent_band,
                "recommendation": recommendations.get(threat_id, ""),
                "maestro_layer": k8["maestro_layer"],
                "control_category": k8["control_category"],
                "carried_forward": k8["cf"].upper() == "CF",
            })

    _warn_aggregated(_unrecognized_status_ids,
                     "controls rows have an unrecognized or empty status", "counted as no control")
    _warn_aggregated(_unparseable_score_refs, "unparseable scores", "treated as missing")
    _warn_aggregated(_clamped_ids,
                     "controls rows have a residual above the inherent score", "clamped")
    _warn_aggregated(_missing_residual_ids, "controls rows have no residual score",
                     "defaulted to the inherent score (no credit)")
    _warn_aggregated(_missing_inherent_ids, "controls rows have no inherent score",
                     "excluded from funnel volumes")

    # ---- Dedupe cross-listed findings by threat ID ----
    # control-analyzer cross-lists findings under both their original band and
    # their score-derived band so residual reclassification is traceable. The
    # score-derived band (applied above) makes every duplicate's residual_severity
    # identical, so keep the first occurrence and drop the rest.
    seen_ids = set()
    deduped = []
    for f in result["findings"]:
        fid = f["id"]
        if fid and fid in seen_ids:
            continue
        if fid:
            seen_ids.add(fid)
        deduped.append(f)
    result["findings"] = deduped

    # ---- Compute Tier 1 severity counts from residual severity ----
    for f in result["findings"]:
        key = f["residual_severity"].lower()
        if key in result["severity"]:
            result["severity"][key] += 1
    result["severity"]["total"] = len(result["findings"])

    # ---- Derive STRIDE coverage matrix from findings ----
    stride_counts = {}
    for f in result["findings"]:
        fid = f["id"]
        category = None
        for prefix, cat_name in STRIDE_PREFIXES.items():
            if fid.startswith(prefix):
                category = cat_name
                break
        if category is None:
            category = "Other"

        if category not in stride_counts:
            stride_counts[category] = {"found": 0, "partial": 0, "missing": 0}

        # K11: classify_control_status's stored result (data-model.md §3),
        # replacing this row idiom's own substring matching.
        if f["status_class"] == "partial":
            stride_counts[category]["partial"] += 1
        elif f["status_class"] == "found":
            stride_counts[category]["found"] += 1
        else:
            stride_counts[category]["missing"] += 1

    stride_order = [
        "Spoofing", "Tampering", "Repudiation", "Information Disclosure",
        "Denial of Service", "Elevation of Privilege", "Agentic Threats", "LLM Threats",
    ]
    for cat in stride_order:
        if cat in stride_counts:
            result["coverage_matrix"].append({
                "category": cat,
                "found": stride_counts[cat]["found"],
                "partial": stride_counts[cat]["partial"],
                "missing": stride_counts[cat]["missing"],
            })
    if "Other" in stride_counts:
        result["coverage_matrix"].append({
            "category": "Other",
            "found": stride_counts["Other"]["found"],
            "partial": stride_counts["Other"]["partial"],
            "missing": stride_counts["Other"]["missing"],
        })

    # ---- Coverage Summary from Section 1 Coverage Distribution ----
    found_summary = False
    cov_rows = parse_markdown_table(content, "Coverage Distribution")
    if not cov_rows:
        cov_rows = parse_markdown_table(content, "## 1. Executive Summary")

    for row in cov_rows:
        status = row.get("Status", "").strip()
        count_str = row.get("Count", "").strip()
        count = _parse_int(count_str)

        if "Partial" in status:
            result["coverage_summary"]["total-partial"] = count
            found_summary = True
        elif "No Control" in status or "Missing" in status:
            result["coverage_summary"]["total-missing"] = count
            found_summary = True
        elif "Found" in status:
            result["coverage_summary"]["total-found"] = count
            found_summary = True

    # Fallback: derive from findings if table not found. K11: uses the
    # stored status_class (data-model.md §3), replacing this row idiom's own
    # substring matching. The Section 1 table reader above keeps its own.
    if not found_summary and result["findings"]:
        for f in result["findings"]:
            if f["status_class"] == "partial":
                result["coverage_summary"]["total-partial"] += 1
            elif f["status_class"] == "found":
                result["coverage_summary"]["total-found"] += 1
            else:
                result["coverage_summary"]["total-missing"] += 1

    # ---- Section 3: Control Details ----
    sec3_start = None
    sec3_end = len(lines)
    for i, line in enumerate(lines):
        if re.match(r"^##\s+3\.\s+Control Details", line):
            sec3_start = i + 1
        elif sec3_start is not None and re.match(r"^##\s+\d+\.", line):
            sec3_end = i
            break

    if sec3_start is not None:
        current_category = ""
        i = sec3_start
        while i < sec3_end:
            line = lines[i].strip()

            # Category heading (### level)
            cat_match = re.match(r"^###\s+(.+)", line)
            if cat_match:
                current_category = cat_match.group(1).strip()
                i += 1
                continue

            # Control metadata: **Category**: X | **Status**: Y | **Effectiveness**: Z
            if "**Status**:" in line and "**Effectiveness**:" in line:
                status_match = re.search(r"\*\*Status\*\*:\s*([\w\s]+?)(?:\s*\||\s*$)", line)
                eff_match = re.search(r"\*\*Effectiveness\*\*:\s*(\w+)", line)
                cat_match2 = re.search(r"\*\*Category\*\*:\s*([\w\s/]+?)(?:\s*\||\s*$)", line)

                status = status_match.group(1).strip() if status_match else ""
                effectiveness = eff_match.group(1).strip() if eff_match else ""
                category = cat_match2.group(1).strip() if cat_match2 else current_category

                # Look ahead for evidence and component
                evidence = ""
                component = ""
                for j in range(i + 1, min(i + 30, sec3_end)):
                    next_line = lines[j].strip()
                    if next_line.startswith("####") or next_line.startswith("### "):
                        break
                    if "**Detected in**:" in next_line:
                        ev_match = re.search(r"\*\*Detected in\*\*:\s*`([^`]+)`", next_line)
                        if ev_match:
                            evidence = decode_references(ev_match.group(1))
                    # Get component from first row of Threats Mitigated table
                    if "Threats Mitigated" in next_line:
                        k = j + 1
                        while k < sec3_end and not lines[k].strip().startswith("|"):
                            k += 1
                        # Skip header + separator (with bounds check)
                        if k + 2 < sec3_end:
                            k += 2
                        if k < sec3_end and lines[k].strip().startswith("|"):
                            cells = [decode_references(strip_bold(c.strip())) for c in lines[k].split("|")[1:-1]]
                            if len(cells) >= 2:
                                component = cells[1]

                result["controls"].append({
                    "component": component,
                    "category": category,
                    "status": status,
                    "evidence": evidence,
                    "effectiveness": effectiveness,
                })

            i += 1

    return result


# =============================================================================
# Attack Chain Parser
# =============================================================================

def parse_attack_chains(content: str) -> list:
    """Parse attack-chains.md artifact into a list of chain dicts.

    Each chain dict contains:
        chain_id: str (e.g., "CHAIN-001")
        title: str
        layers: list[str] (e.g., ["L2", "L3", "L7"])
        max_severity: str (Critical, High, Medium, Low)
        findings: list[dict] with keys: finding_id, maestro_layer, role,
                  component, category, severity
        narrative: str (attack progression text)
        chain_breaking_controls: list[dict] with keys: target_finding_id,
                                 target_layer, rationale, recommendation
        surfaced: bool

    The text values (title, narrative, rationale, recommendation and the member table's cells) are decoded with
    :func:`decode_references`, as a renderer escapes them (ADR-050 D3).

    Returns empty list if content is empty or unparseable.
    """
    if not content or not content.strip():
        return []

    chains = []
    lines = content.split("\n")

    # Find all chain detail subsections (### CHAIN-NNN: Title)
    chain_starts = []
    for i, line in enumerate(lines):
        match = re.match(r"^###\s+(CHAIN-\d{3}):\s+(.+)$", line.strip())
        if match:
            chain_starts.append((i, match.group(1), decode_references(match.group(2).strip())))

    if not chain_starts:
        return []

    for idx, (start_line, chain_id, title) in enumerate(chain_starts):
        # Determine section end (next chain or end of file)
        if idx + 1 < len(chain_starts):
            end_line = chain_starts[idx + 1][0]
        else:
            end_line = len(lines)

        section_lines = lines[start_line:end_line]
        section_text = "\n".join(section_lines)

        # Parse layers from **Layers**: L2 → L3 → L7
        layers = []
        layers_match = re.search(r"\*\*Layers\*\*:\s*(.+)", section_text)
        if layers_match:
            layers_str = layers_match.group(1).strip()
            layer_parts = re.split(r"\s*(?:→|->|—>)\s*", layers_str)
            layers = [p.strip() for p in layer_parts if p.strip()]

        # Parse max severity from **Max Severity**: Critical
        max_severity = ""
        sev_match = re.search(r"\*\*Max Severity\*\*:\s*(\w+)", section_text)
        if sev_match:
            max_severity = sev_match.group(1).strip()

        # Parse surfaced from **Surfaced**: Yes/No
        surfaced = False
        surf_match = re.search(r"\*\*Surfaced\*\*:\s*(\w+)", section_text)
        if surf_match:
            surfaced = surf_match.group(1).strip().lower() in ("yes", "true")

        # Parse member findings table
        findings = _parse_chain_member_findings(section_text)

        # Parse narrative
        narrative = _parse_chain_narrative(section_lines)

        # Parse chain-breaking controls
        controls = _parse_chain_breaking_controls(section_text)

        chains.append({
            "chain_id": chain_id,
            "title": title,
            "layers": layers,
            "max_severity": max_severity,
            "findings": findings,
            "narrative": narrative,
            "chain_breaking_controls": controls,
            "surfaced": surfaced,
        })

    return chains


def _parse_chain_member_findings(section_text: str) -> list:
    """Parse the Member Findings table from a chain detail section."""
    rows = parse_markdown_table(section_text, "#### Member Findings")
    findings = []
    for row in rows:
        findings.append({
            "finding_id": row.get("Finding ID", "").strip(),
            "maestro_layer": row.get("MAESTRO Layer", "").strip(),
            "role": row.get("Role", "").strip(),
            "component": row.get("Component", "").strip(),
            "category": row.get("Category", "").strip(),
            "severity": row.get("Severity", "").strip(),
        })
    return findings


def _parse_chain_narrative(section_lines: list) -> str:
    """Extract prose text from the Attack Progression subsection."""
    text_start = None
    for i, line in enumerate(section_lines):
        if line.strip().startswith("#### Attack Progression"):
            text_start = i + 1
            break

    if text_start is None:
        return ""

    text_lines = []
    for i in range(text_start, len(section_lines)):
        line = section_lines[i].strip()
        if line.startswith("####") or line.startswith("###"):
            break
        if line:
            text_lines.append(line)

    return decode_references(" ".join(text_lines))


def _parse_chain_breaking_controls(section_text: str) -> list:
    """Parse chain-breaking controls from a chain detail section.

    Controls follow the pattern:
        **Target**: finding_id (layer)
        **Rationale**: text
        **Recommendation**: text
    """
    controls = []
    lines = section_text.split("\n")

    ctrl_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("#### Chain-Breaking Controls"):
            ctrl_start = i + 1
            break

    if ctrl_start is None:
        return controls

    current = {}
    for i in range(ctrl_start, len(lines)):
        line = lines[i].strip()
        if line.startswith("###") and not line.startswith("#### Chain-Breaking"):
            break
        if line.startswith("####") and not line.startswith("#### Chain-Breaking"):
            break

        target_match = re.match(r"\*\*Target\*\*:\s*(\S+)\s*(?:\(([^)]+)\))?", line)
        if target_match:
            if current:
                controls.append(current)
            current = {
                "target_finding_id": target_match.group(1).strip(),
                "target_layer": target_match.group(2).strip() if target_match.group(2) else "",
                "rationale": "",
                "recommendation": "",
            }
            continue

        rationale_match = re.match(r"\*\*Rationale\*\*:\s*(.+)", line)
        if rationale_match and current:
            current["rationale"] = decode_references(rationale_match.group(1).strip())
            continue

        rec_match = re.match(r"\*\*Recommendation\*\*:\s*(.+)", line)
        if rec_match and current:
            current["recommendation"] = decode_references(rec_match.group(1).strip())
            continue

    if current:
        controls.append(current)

    return controls


# =============================================================================
# Asset-Sensitivity Tag Parser (Issue #260 prototype)
# =============================================================================
#
# Extracts inline [asset:tag1,tag2] annotations from Mermaid node labels in an
# architecture description, producing a component-to-asset-tag mapping
# consumed by the risk-scorer's CVSS impact-bit floor pass. Mirrors the
# component_zone_map shape produced by Trust Zone Extraction so the modifier
# pass can join the two on display name.
#
# Recognized syntax (the asset block lives inside a quoted Mermaid label):
#
#     PostgresDB[("Postgres DB<br/>[asset:pii,auth]")]
#     SecretsVault["Secrets Vault<br/>[asset:secrets]"]
#
# Unknown tags are dropped with a stderr warning. Components without tags are
# omitted from the result entirely (absent == default behavior, no modifier).

_ASSET_BLOCK_PATTERN = re.compile(r"\[asset:\s*([^\]]+?)\s*\]", re.IGNORECASE)
_QUOTED_NODE_WITH_ASSET_PATTERN = re.compile(
    r'\b([A-Za-z_]\w*)\s*[\[\(\{]+\s*"([^"]*\[asset:[^\]]+\][^"]*)"',
    re.IGNORECASE,
)
_BR_TAG_PATTERN = re.compile(r"<br\s*/?>", re.IGNORECASE)


def parse_component_asset_map(content: str) -> dict:
    """Extract component-to-asset-tag mapping from a Mermaid architecture file.

    Scans Mermaid node declarations inside `````mermaid`` fenced
    blocks (or the whole content when no fence is present) for the
    ``[asset:tag1,tag2]`` pattern embedded in a quoted node label. Returns a
    dict keyed by the component's display name (label content with the asset
    block and ``<br/>`` removed) mapping to a sorted list of valid tag
    strings drawn from :data:`VALID_ASSET_TAGS`.

    Parsing is intentionally permissive about Mermaid bracket shape (rectangle,
    rounded, cylinder, subroutine all accepted) and case-insensitive on tag
    names. Asset tags MUST be embedded inside quoted labels — unquoted labels
    with bracket-style asset blocks are not parsed because Mermaid's bracket
    grammar already uses ``[`` / ``]`` and disambiguating without a full
    parser is fragile.

    Returns an empty dict when ``content`` is empty, when no ``[asset:...]``
    block is present, or when every tag is unknown. Unknown tags produce a
    stderr warning per occurrence; valid tags from the same node are still
    retained.
    """
    result: dict = {}
    if not content:
        return result

    scan_blocks = _select_mermaid_scan_blocks(content)

    for block in scan_blocks:
        for match in _QUOTED_NODE_WITH_ASSET_PATTERN.finditer(block):
            node_id = match.group(1)
            label_content = match.group(2)

            asset_match = _ASSET_BLOCK_PATTERN.search(label_content)
            if asset_match is None:
                continue

            tags = _normalize_asset_tags(asset_match.group(1), node_id)
            if not tags:
                continue

            display_name = _extract_display_name(label_content)
            if not display_name:
                display_name = node_id

            existing = result.get(display_name)
            if existing is None:
                result[display_name] = tags
                continue

            merged = sorted(set(existing) | set(tags))
            if merged != existing:
                print(
                    f"Warning: component {display_name!r} has multiple asset "
                    f"declarations; merged tags: {merged}",
                    file=sys.stderr,
                )
            result[display_name] = merged

    return result


def _select_mermaid_scan_blocks(content: str) -> list:
    """Return the substrings of ``content`` that should be scanned for nodes.

    When at least one fenced `````mermaid`` block is present,
    only those blocks are scanned (avoiding false matches on prose that
    happens to contain ``[asset:...]``). When no fence is present, the entire
    content is scanned as-is so callers passing raw Mermaid still work.
    """
    fences = re.findall(r"```mermaid\s*\n(.*?)\n```", content, re.DOTALL)
    if fences:
        return fences
    return [content]


def _normalize_asset_tags(raw: str, node_id: str) -> list:
    """Split a raw ``[asset:...]`` body into a sorted list of valid tags.

    Tags are lowercased and stripped. Unknown tags (not in
    :data:`VALID_ASSET_TAGS`) are dropped with a per-occurrence stderr warning.
    Empty tag lists collapse to ``[]``.
    """
    candidates = [t.strip().lower() for t in raw.split(",")]
    candidates = [t for t in candidates if t]

    valid: list = []
    for tag in candidates:
        if tag in VALID_ASSET_TAGS:
            valid.append(tag)
        else:
            print(
                f"Warning: unknown asset tag {tag!r} on node {node_id!r}; "
                f"valid tags: {list(VALID_ASSET_TAGS)}",
                file=sys.stderr,
            )

    return sorted(set(valid))


def _extract_display_name(label_content: str) -> str:
    """Return the human-readable component name from a quoted Mermaid label.

    Strips the ``[asset:...]`` block, ``<br/>`` line breaks, and surrounding
    whitespace so the result joins cleanly against the component_zone_map
    keys produced from threats.md Section 2 (which also uses display names).
    """
    cleaned = _ASSET_BLOCK_PATTERN.sub("", label_content)
    cleaned = _BR_TAG_PATTERN.sub(" ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()
