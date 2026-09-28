"""Shared parser module for tachi pipeline artifacts.

Provides deterministic parsers for markdown tables, YAML frontmatter, severity
distributions, findings, scope data, and compensating controls extracted from
tachi pipeline outputs (threats.md, risk-scores.md, compensating-controls.md).

Used by extract-report-data.py and extract-infographic-data.py to ensure
consistent, cross-output-identical parsing of the same source artifacts.
"""

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import re
import sys
from pathlib import Path

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
    ``ValueError`` and ``TypeError``, and rejects non-finite results
    (``NaN``, ``Infinity``) even though ``Decimal("NaN")`` parses without
    raising. Used for every score in the controls and risk-scores parsers
    (data-model.md §3); a ``None`` return is the caller's cue to count the
    cell toward its own aggregated "unparseable score" warning class — this
    function never prints anything itself.
    """
    try:
        d = Decimal(s.strip())
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not d.is_finite():
        return None
    return d


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


def match_heading(pattern: str, text: str):
    """Return the 0-indexed line number of the first line matching ``pattern``.

    ``pattern`` is matched with ``re.MULTILINE`` (``^``/``$`` anchor to each
    line), so it should itself be a line-anchored regex, e.g.
    ``r"^#{3,4}\\s+Risk by MAESTRO Layer"`` (K10) or
    ``r"^##\\s+4[bc]\\.\\s+Resolved Findings\\s*$"`` (K12). Returns ``None``
    when there is no match. The return value is a line index compatible with
    :func:`parse_markdown_table`'s ``start_line`` argument, not a character
    offset.
    """
    m = re.search(pattern, text, re.MULTILINE)
    if not m:
        return None
    return text.count("\n", 0, m.start())


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

def parse_markdown_table(content: str, section_header: str = None, start_line: int = None) -> list:
    """Parse a markdown table found after a section header.

    Args:
        content: Full markdown file content.
        section_header: The section header to search for (e.g., "## 6. Risk Summary"),
            matched as a substring anywhere on a line. Ignored when ``start_line``
            is given.
        start_line: A 0-indexed line number to start scanning from directly —
            typically the return value of :func:`match_heading` — so a regex
            match never falls back to a substring re-search (data-model.md §3,
            rev. 1). Exactly one of ``section_header`` or ``start_line`` must
            be usable; when both are omitted or ``section_header`` matches
            nothing, an empty list is returned.

    Returns:
        List of dicts, one per row, with keys from the header row.
        Returns empty list if table not found.

    Stop rule (FR-K9.2): scanning for the table stops at the next heading
    whose level (count of leading '#') is the same as or higher (numerically
    lower or equal) than the level of the matched line itself — so an empty
    ``### Foo`` section correctly yields no rows instead of adopting a later
    ``###``/``####`` section's table. When the matched line is not a heading
    (a handful of callers match bold paragraph text, e.g. "Coverage
    Distribution"), the stop rule is unchanged from before this fix: stop
    only at a literal ``## `` or ``# `` line. This means every pre-existing
    ``##``-heading caller is unaffected by construction, because for a
    level-1-or-2 match, "same or higher level" reduces exactly to "the next
    ``##`` or ``#`` line" — the old, hardcoded rule.
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
            # Stop at the next heading of the same or higher level (FR-K9.2).
            level = _heading_level(line)
            if level is not None and level <= matched_level:
                break
        elif line.startswith("## ") or line.startswith("# "):
            # Non-heading match: today's rule, unchanged.
            break

    if table_header_idx is None:
        return []

    # Parse header row for column names
    header_line = lines[table_header_idx].strip()
    columns = [strip_bold(c.strip()) for c in header_line.split("|")[1:-1]]
    columns = [c for c in columns if c]

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
        cells = [strip_bold(c.strip()) for c in line.split("|")[1:-1]]
        if len(cells) < len(columns):
            print(f"Warning: skipping malformed row at line {i + 1}: expected {len(columns)} columns, got {len(cells)}", file=sys.stderr)
            continue
        row = {}
        for j, col in enumerate(columns):
            row[col] = cells[j] if j < len(cells) else ""
        rows.append(row)

    return rows


def _find_table_with_column(content: str, section_header: str, required_column: str) -> list:
    """Find a markdown table within a section that has a specific column header.

    Scans all tables after section_header and returns the first one
    whose header row contains required_column.
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
            columns = [strip_bold(c.strip()) for c in stripped.split("|")[1:-1]]
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
                    cells = [strip_bold(c.strip()) for c in row_line.split("|")[1:-1]]
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
    list, which may have no ``delta_status`` key at all (Tier 1/2) or an
    unnormalized one (Tier 3). ``resolved`` is the placeholder-filtered list
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

    unknown = [(fid, status) for fid, status in status_by_id.items()
               if status not in _DELTA_STATUS_COUNTED_VALUES]
    if unknown:
        first_five = ", ".join(f"{fid}='{status}'" for fid, status in unknown[:5])
        print(
            f"Warning: {len(unknown)} Section 7 statuses are not "
            f"NEW/UPDATED/UNCHANGED after normalization (first: {first_five}); "
            "not counted",
            file=sys.stderr,
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
        # Delta fields: include only when present (backward compatible)
        status = row.get("Status", "").strip()
        if status:
            finding["delta_status"] = status
        attribution = _extract_source_attribution(finding["id"], source_attribution_block)
        if attribution is not None:
            finding["source_attribution"] = attribution
        findings.append(finding)
    return findings


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
            the caller from ``parse_risk_scores_findings``'s
            ``composite_score`` through :func:`parse_score`.

    Each finding dict additionally carries (K11):
        status_class: "found" | "partial" | "none", from
            :func:`classify_control_status`.
        inherent: the row's inherent score as a ``Decimal``, or ``None`` when
            unavailable even after the join.
        inherent_severity: the inherent score's severity band (Title Case),
            falling back to the raw ``Inherent Severity`` column, or ``None``.
        residual_score / residual_severity: unchanged in shape, but now
            reflect the post-clamp value when a clamp applied.
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
        current_threat_id = None
        for i in range(sec4_start, sec4_end):
            line = lines[i].strip()
            # Match: #### 1. S-3 -- Component (Composite: 9.2, Critical)
            heading_match = re.match(r"^####\s+\d+\.\s+(\S+)\s+[—\-]", line)
            if heading_match:
                current_threat_id = heading_match.group(1)
                continue
            # Match: **What to Implement**: text
            if current_threat_id and line.startswith("**What to Implement**:"):
                rec_text = line.replace("**What to Implement**:", "").strip()
                # Read continuation lines until next marker
                for j in range(i + 1, sec4_end):
                    next_line = lines[j].strip()
                    if not next_line or next_line.startswith("**") or next_line.startswith("####") or next_line.startswith("###") or next_line.startswith("---"):
                        break
                    rec_text += " " + next_line
                recommendations[current_threat_id] = rec_text.strip()
                current_threat_id = None

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

    def _score_to_band(score_str):
        """Map a residual score string to its severity band, or None if unparseable.

        Delegates parsing to the shared :func:`parse_score` (K9), which
        rejects non-finite values (``NaN``, ``Infinity``) that ``float()``
        would otherwise have silently let fall through to "Low".
        """
        return _band_from_score(parse_score(score_str))

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
                joined = composites_by_id.get(threat_id)
                if joined is not None:
                    inherent = joined
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
            })

    def _warn_aggregated(ids, stem_fn):
        if not ids:
            return
        print(stem_fn(len(ids), ", ".join(ids[:5])), file=sys.stderr)

    _warn_aggregated(_unrecognized_status_ids, lambda n, ids: (
        f"Warning: {n} controls rows have an unrecognized or empty status "
        f"(first: {ids}); counted as no control"
    ))
    if _unparseable_score_refs:
        print(
            f"Warning: {len(_unparseable_score_refs)} unparseable scores "
            f"(first: {', '.join(_unparseable_score_refs[:5])}); treated as missing",
            file=sys.stderr,
        )
    _warn_aggregated(_clamped_ids, lambda n, ids: (
        f"Warning: {n} controls rows have a residual above the inherent score "
        f"(first: {ids}); clamped"
    ))
    _warn_aggregated(_missing_residual_ids, lambda n, ids: (
        f"Warning: {n} controls rows have no residual score (first: {ids}); "
        f"defaulted to the inherent score (no credit)"
    ))
    _warn_aggregated(_missing_inherent_ids, lambda n, ids: (
        f"Warning: {n} controls rows have no inherent score (first: {ids}); "
        f"excluded from funnel volumes"
    ))

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
                            evidence = ev_match.group(1)
                    # Get component from first row of Threats Mitigated table
                    if "Threats Mitigated" in next_line:
                        k = j + 1
                        while k < sec3_end and not lines[k].strip().startswith("|"):
                            k += 1
                        # Skip header + separator (with bounds check)
                        if k + 2 < sec3_end:
                            k += 2
                        if k < sec3_end and lines[k].strip().startswith("|"):
                            cells = [c.strip() for c in lines[k].split("|")[1:-1]]
                            if len(cells) >= 2:
                                component = strip_bold(cells[1])

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
            chain_starts.append((i, match.group(1), match.group(2).strip()))

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

    return " ".join(text_lines)


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
            current["rationale"] = rationale_match.group(1).strip()
            continue

        rec_match = re.match(r"\*\*Recommendation\*\*:\s*(.+)", line)
        if rec_match and current:
            current["recommendation"] = rec_match.group(1).strip()
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
