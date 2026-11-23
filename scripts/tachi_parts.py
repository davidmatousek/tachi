"""Part-file loader, validator and guards for the F-374 pipeline (ADR-050 D3).

Every agent-written file the shipped scripts read is untrusted input (NFR-10). This
helper is the one place that decides what such a file may contain. It is imported,
never run, and it is stdlib-only. It imports neither ``sarif_common`` nor
``tachi_parsers`` (C1), so both of them can import it without a cycle.

Written in two slices (T012, T013). **Slice 1, below, is the identifier module:**

* ``ID_PATTERNS``: the source text of every allow-list, as the contracts spell it.
  Each is matched as an ASCII ``re.fullmatch`` with ``[0-9]``, never ``\\d`` or ``$``
  (KB 24: ``\\d`` admits non-ASCII digits and ``$`` admits a trailing newline).
* ``id_matches(kind, value)``: the allow-list test. ``kind`` is a key of ``ID_PATTERNS``:
  ``finding``, ``plan``, ``batch``, ``dispatch``, ``group``, ``chain`` or ``language``.
* ``FINDING_PREFIXES``, ``canonical_finding_id(value)`` and ``finding_sort_key(value)``:
  the canonical spelling (``AGP-01`` is ``AGP-1``) and S-2's total order.
* ``PATH_MAX_BYTES``, ``path_problem(value, allow_absolute=False)`` and
  ``path_parts(value, allow_absolute=False)``: ADR-050 D7's syntactic path rule, for
  evidence ``file`` values (relative) and, with ``allow_absolute=True``, for the URI
  resolver's candidates. The filesystem checks (lstat walk, spelling) are not here.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from typing import Dict, Optional, Tuple

# Turn bytecode writing off before anything else loads (feature 391, FR-007; ADR-049 D8).
# This helper is already compiled when this line runs and imports no local module itself,
# so the line protects the local modules that an importer loads after it.
sys.dont_write_bytecode = True


# =============================================================================
# Identifier allow-lists (ADR-050 D3, "Identifiers"; S-2)
# =============================================================================

# S-2's prefix rank: the order of this tuple is the order of finding IDs.
FINDING_PREFIXES = ("S", "T", "R", "I", "D", "E", "AG", "AGP", "LLM", "OI", "MI", "TE")

# The source text of each allow-list, exactly as contracts/part-files.md and
# contracts/threat-model-records.md spell it, so a drift test can compare the text.
ID_PATTERNS: Dict[str, str] = {
    "finding": "(S|T|R|I|D|E|AG|AGP|LLM|OI|MI|TE)-[0-9]{1,6}",
    "plan": "[0-9]{8}T[0-9]{6}Z-[0-9a-f]{12}",
    "batch": "B[0-9]{3}(-[12]){0,2}",
    "dispatch": "dsp-[0-9]{3,4}",
    "group": "CG-[0-9]{1,6}",
    "chain": "CHAIN-[0-9]{3,6}",
    "language": "[a-z0-9+#-]{1,20}",
}

_COMPILED = {kind: re.compile(source, re.ASCII) for kind, source in ID_PATTERNS.items()}


def id_matches(kind: str, value: object) -> bool:
    """True when ``value`` is a ``str`` that fully matches the ``kind`` allow-list.

    An unknown ``kind`` raises ``KeyError``, so a typo fails loudly.
    """
    pattern = _COMPILED[kind]
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def canonical_finding_id(value: object) -> str:
    """The canonical spelling ``{PREFIX}-{N}``, leading zeros dropped: ``AGP-01`` -> ``AGP-1``.

    Raises ``ValueError`` when ``value`` is not an allow-listed finding ID.
    """
    if not id_matches("finding", value):
        raise ValueError("not a finding ID: %r" % (value,))
    prefix, _, number = value.partition("-")  # type: ignore[union-attr]
    return "%s-%d" % (prefix, int(number))


def finding_sort_key(value: object) -> Tuple[int, int]:
    """S-2's total order: prefix rank, then the numeric suffix as an integer (``T-9`` < ``T-10``).

    Two spellings of one canonical ID have one key. Raises ``ValueError`` on a non-ID.
    """
    prefix, _, number = canonical_finding_id(value).partition("-")
    return (FINDING_PREFIXES.index(prefix), int(number))


# =============================================================================
# D7's syntactic path rule (evidence ``file`` values and URI candidates)
# =============================================================================

PATH_MAX_BYTES = 4096


def path_problem(value: object, allow_absolute: bool = False) -> Optional[str]:
    """ADR-050 D7's syntactic checks on a path. ``None`` when it passes, else the check's name.

    The checks run in this order, and the first failure names the problem:
    ``type``, ``empty``, ``encoding``, ``too-long`` (over ``PATH_MAX_BYTES`` bytes of UTF-8),
    ``control-char`` (any Cc character), ``backslash``, ``backtick``, ``leading-slash``
    (unless ``allow_absolute``), ``drive-letter``, ``scheme``, ``parent-reference`` (a ``..``
    component) and ``empty`` again when no component is left after dropping ``.`` and empty ones.

    A relative path whose first component holds a colon is refused as a drive letter
    (``C:``) or a scheme (``https:``), as RFC 3986 section 4.2 requires of a relative reference.
    An absolute path (``allow_absolute``) skips the drive-letter and scheme checks, because its
    leading slash already settles how it parses. This function never touches the filesystem.
    """
    if not isinstance(value, str):
        return "type"
    if value == "":
        return "empty"
    try:
        size = len(value.encode("utf-8"))
    except UnicodeEncodeError:
        return "encoding"
    if size > PATH_MAX_BYTES:
        return "too-long"
    if any(unicodedata.category(ch) == "Cc" for ch in value):
        return "control-char"
    if "\\" in value:
        return "backslash"
    if "`" in value:
        return "backtick"
    if value.startswith("/"):
        if not allow_absolute:
            return "leading-slash"
    else:
        first = value.split("/", 1)[0]
        if ":" in first:
            letter = len(first) >= 2 and first[1] == ":" and first[0].isascii() and first[0].isalpha()
            return "drive-letter" if letter else "scheme"
    parts = [part for part in value.split("/") if part not in ("", ".")]
    if ".." in parts:
        return "parent-reference"
    if not parts:
        return "empty"
    return None


def path_parts(value: object, allow_absolute: bool = False) -> Tuple[str, ...]:
    """The path's components with ``.`` and empty ones dropped (D7).

    Raises ``ValueError`` carrying ``path_problem``'s name when the path fails the rule.
    """
    problem = path_problem(value, allow_absolute=allow_absolute)
    if problem is not None:
        raise ValueError(problem)
    return tuple(part for part in value.split("/") if part not in ("", "."))  # type: ignore[union-attr]
