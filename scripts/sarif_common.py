"""Shared SARIF helpers, and the shared SARIF emitter, for the tachi pipeline.

This module has two layers.

**The legacy helpers.** The canonical `PREFIX_TO_RULE` mapping (rule URIs for
`generate-threats-sarif.py` and `generate-risk-scores-sarif.py`), the severity-to-SARIF-level
mapping, finding-ID prefix extraction, a threats.md -> component metadata parser and the SARIF
envelope. Per-script emit shape (logicalLocations array vs logicalLocation object, kind label
vocabulary) remains in each generator to preserve byte-identity (ADR-021). They keep their
names, values and behavior while those generators exist. `PREFIX_TO_RULE`'s AI values are the
short forms those generators emit (`tachi/ai/agentic`); the shared emitter below never emits them.

**The shared emitter** (ADR-050 D7 and D8). It implements the rules in
`.claude/skills/tachi-shared/references/sarif-identity-shared.md`, and a drift test keeps the two
in step. It holds:

* the URI resolver (D7): `resolve_architecture`, `resolve_explicit` (its first step, which
  `tachi-stage.py plan` runs too), `resolve_file` and the body-line reader. One shared resolver
  sets `artifactLocation.uri`, and no script takes a finished URI;
* identity (D7): `RULE_ID_BY_PREFIX` (twelve prefixes, eight rule IDs), the `tachi-plh/1` hash
  and the two partial fingerprints;
* membership and correlation (D8): `correlation_assignments`, ruling C's sentence and the
  self-check that runs before any write;
* the result, the run and the document, in one key order, with the real `informationUri` and the
  `tachi_provenance` stamp;
* the OWASP-LLM, OWASP-ASI and CWE taxa that the scorer and controls files carry, embedded so
  the core path needs no PyYAML;
* the eight rules those two files share, each with its taxonomy `relationships` (`RULES` and
  `build_rules`), so the two renderers emit one table (PM W3 ruling 2, gap A).

Standard library plus the local helpers `tachi_parsers`, `tachi_parts` and `tachi_scoring`. The
module sets `sys.dont_write_bytecode` before any of them loads (ADR-049 D8).
"""
from __future__ import annotations

import hashlib
import json
import os
import posixpath
import re
import stat
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, NamedTuple, Optional, Sequence, Tuple

# Turn bytecode writing off before any local module loads (feature 391, FR-007; ADR-049 D8).
# The guarantee lives in the module, so it holds for a paraphrased command and for a person
# running a script by hand.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import tachi_parts  # noqa: E402
import tachi_scoring  # noqa: E402
from tachi_parsers import parse_scope_data  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parent.parent


SARIF_SCHEMA_URI = (
    "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/"
    "schema/sarif-schema-2.1.0.json"
)


PREFIX_TO_RULE = {
    "S": "tachi/stride/spoofing",
    "T": "tachi/stride/tampering",
    "R": "tachi/stride/repudiation",
    "I": "tachi/stride/information-disclosure",
    "D": "tachi/stride/denial-of-service",
    "E": "tachi/stride/elevation-of-privilege",
    "AG": "tachi/ai/agentic",
    "AGP": "tachi/ai/agentic",
    "LLM": "tachi/ai/llm",
    "OI": "tachi/ai/llm",
    "MI": "tachi/ai/llm",
    "TE": "tachi/ai/agentic",
}


SEVERITY_TO_LEVEL = {
    "Critical": "error",
    "High": "error",
    "Medium": "warning",
    "Low": "note",
    "Note": "note",
}


def prefix_for(finding_id: str) -> str:
    return finding_id.rsplit("-", 1)[0] if "-" in finding_id else finding_id


def level_for_band(band: str) -> str:
    return SEVERITY_TO_LEVEL.get(band, "warning")


def parse_component_metadata(threats_md: str) -> dict[str, dict[str, str]]:
    """Map component name → {'zone': <trust zone>, 'dfd_type': <DFD type>}.

    Single canonical traversal of threats.md Sections 1 (Components) and 2
    (Trust Zones) via `tachi_parsers.parse_scope_data`. Replaces the
    hardcoded `COMPONENT_ZONE` dict in `generate-threats-sarif.py` (which
    silently desynced from threats.md when components changed) and the
    bespoke regex parsers `parse_trust_zones` + `parse_component_kinds` in
    `generate-risk-scores-sarif.py`. Caller is responsible for translating
    `dfd_type` (e.g. "Data Store") into its emit-specific kind label
    ("data" vs "data-store") to preserve per-script SARIF byte-identity.
    """
    scope = parse_scope_data(threats_md)
    out: dict[str, dict[str, str]] = {}
    for comp in scope["components"]:
        name = comp["name"]
        if not name:
            continue
        out[name] = {"zone": "Application Zone", "dfd_type": comp["type"]}
    for tb in scope["trust_boundaries"]:
        zone = tb["zone"]
        if not zone:
            continue
        for member in (m.strip() for m in tb["components"].split(",")):
            if member and member in out:
                out[member]["zone"] = zone
    return out


# Header cell of the populator's "## Affected Assets" table, byte-matching
# `populate-affected-assets.py` (`_COL_FINDING_ID`). Used to skip the header
# row during the inverse parse; kept local so this module stays self-contained.
_COL_FINDING_ID = "Finding ID"

_AFFECTED_ASSETS_BLOCK_PATTERN = re.compile(
    r"^##[ \t]+Affected Assets[ \t]*$(?P<body>.*?)(?=^#{1,2}[ \t]|\Z)",
    re.MULTILINE | re.DOTALL,
)
_AFFECTED_ASSETS_ROW_PATTERN = re.compile(r"^\|(?P<id>[^|]*)\|(?P<assets>[^|]*)\|")


def parse_affected_assets(threats_content: str) -> dict[str, list[str]]:
    """Map finding ID → list of asset tags from the threats.md block.

    The inverse of the deterministic populator
    (`scripts/populate-affected-assets.py` → `render_affected_assets_block`):
    it parses the always-present `## Affected Assets` markdown table back into
    `{finding_id: [tags]}`, the exact round-trip of the block the populator
    emits (`| S-1 | [phi, pii] |` → `{"S-1": ["phi", "pii"]}`; `| T-2 | [] |`
    → `{"T-2": []}`). This is the single canonical extractor the SARIF
    regeneration scripts (`generate-threats-sarif.py`,
    `generate-risk-scores-sarif.py`) and the cross-format test consume, so the
    verification tier reads one value source instead of independently
    re-deriving from `component_asset_map` (mirrors the `parse_component_metadata`
    desync-fix precedent above). Order is preserved verbatim from the block
    (already sorted ascending by the populator — this does NOT re-sort or dedup).
    Returns `{}` when no `## Affected Assets` block is present (graceful).
    """
    match = _AFFECTED_ASSETS_BLOCK_PATTERN.search(threats_content)
    if not match:
        return {}
    out: dict[str, list[str]] = {}
    for line in match.group("body").splitlines():
        row = _AFFECTED_ASSETS_ROW_PATTERN.match(line.strip())
        if not row:
            continue
        finding_id = row.group("id").replace("**", "").strip()
        # Skip the header row ("Finding ID" / "Affected Assets") and the
        # separator row ("|---|---|"); neither is a real finding.
        if not finding_id or finding_id == _COL_FINDING_ID or set(finding_id) <= {"-", ":"}:
            continue
        inner = row.group("assets").replace("**", "").strip()
        inner = inner[1:-1] if inner.startswith("[") and inner.endswith("]") else inner
        out[finding_id] = [tag.strip() for tag in inner.split(",") if tag.strip()]
    return out


def build_sarif_envelope(
    driver: dict,
    taxonomies: list[dict],
    results: list[dict],
    *,
    schema_first: bool = False,
) -> dict:
    """Assemble the SARIF 2.1.0 root document.

    `schema_first=True` emits `$schema` before `version` (threats.sarif
    legacy ordering); default emits `version` before `$schema`
    (risk-scores.sarif ordering). Field order matters for byte-identity
    under stable JSON serialization.
    """
    if schema_first:
        envelope = {
            "$schema": SARIF_SCHEMA_URI,
            "version": "2.1.0",
        }
    else:
        envelope = {
            "version": "2.1.0",
            "$schema": SARIF_SCHEMA_URI,
        }
    envelope["runs"] = [
        {
            "tool": {"driver": driver},
            "taxonomies": taxonomies,
            "results": results,
        }
    ]
    return envelope


# =============================================================================
# D7: the URI resolver (T016)
# =============================================================================
#
# `artifactLocation.uri` is the user's architecture file: repo-relative, in one canonical
# spelling, and identical on every result of a run chain. One resolver sets it, and no script
# takes a finished URI. The syntactic path rule is `tachi_parts.path_problem`'s (ADR-050 D7);
# this section adds the filesystem checks and the spelling. Every "is this the same file, or
# inside it" question is answered by file identity, never by spelling (KB 24): `(st_dev, st_ino)`
# and `samefile`, because a string comparison after `resolve()` is not an identity check on a
# case-insensitive volume.

DEFAULT_ARCHITECTURE_PATH = "docs/security/architecture.md"
MAX_PATH_BYTES = tachi_parts.PATH_MAX_BYTES
ARCHITECTURE_FLAG = "--architecture-path"

# D4's canonical output names. The body line may not name one of them (D7 item 4).
CANONICAL_OUTPUT_NAMES = (
    "threats.md",
    "threats.sarif",
    "threat-report.md",
    "attack-chains.md",
    "risk-scores.md",
    "risk-scores.sarif",
    "compensating-controls.md",
    "compensating-controls.sarif",
)
_CANONICAL_OUTPUT_FOLDED = frozenset(name.casefold() for name in CANONICAL_OUTPUT_NAMES)

_UNRESERVED = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~")


class OsFilesystem:
    """The four filesystem calls the resolver makes. A test passes a fake with the same four."""

    def getcwd(self) -> str:
        return os.getcwd()

    def lstat(self, path: str) -> Any:
        return os.lstat(path)

    def stat(self, path: str) -> Any:
        return os.stat(path)

    def listdir(self, path: str) -> List[str]:
        return os.listdir(path)


OS_FILESYSTEM = OsFilesystem()


class PathCheckError(ValueError):
    """A candidate path failed a D7 check. ``check`` is the failed check's name.

    The names are ``tachi_parts.path_problem``'s (``empty``, ``too-long``, ``control-char``,
    ``backslash``, ``backtick``, ``leading-slash``, ``drive-letter``, ``scheme``,
    ``parent-reference``, ``encoding``, ``type``) and this module's: ``outside-root``,
    ``missing``, ``unreadable``, ``symlink``, ``not-a-directory``, ``not-a-regular-file``,
    ``spelling``, ``canonical-name``, ``no-snapshot``, ``snapshot-not-regular`` and
    ``is-snapshot``.
    """

    def __init__(self, check: str, detail: str = "") -> None:
        super().__init__("%s: %s" % (check, detail) if detail else check)
        self.check = check
        self.detail = detail


class ResolvedPath(NamedTuple):
    """A validated file. ``path`` is the canonical spelling, ``uri`` its RFC 3986 form."""

    path: str
    uri: str


def _short(value: object) -> str:
    """A short, escaped form of a refused value, safe to put in a message."""
    return repr(value)[:80]


def percent_encode(component: str) -> str:
    """Percent-encode one path component per RFC 3986, keeping only the unreserved characters.

    ``a b#c%`` becomes ``a%20b%23c%25``, and e-acute (U+00E9) becomes ``%C3%A9``. A component
    that isn't valid Unicode (a lone surrogate) raises ``UnicodeEncodeError``.
    """
    out = []
    for byte in component.encode("utf-8"):
        char = chr(byte)
        out.append(char if char in _UNRESERVED else "%%%02X" % byte)
    return "".join(out)


def _same_file(fs: Any, first: str, second: str) -> bool:
    """``os.path.samefile`` over the filesystem adapter; an unreadable path is not the same."""
    try:
        one, two = fs.stat(first), fs.stat(second)
    except OSError:
        return False
    return (one.st_dev, one.st_ino) == (two.st_dev, two.st_ino)


def _below_root(parts: Sequence[str], root: str, fs: Any) -> List[str]:
    """The components of an absolute path below the working directory.

    An absolute candidate counts only if one of its ancestors *is* the working directory by
    ``samefile`` (KB 24). The deepest such ancestor wins.
    """
    for cut in range(len(parts), -1, -1):
        if _same_file(fs, "/" + "/".join(parts[:cut]), root):
            rest = list(parts[cut:])
            if not rest:
                raise PathCheckError("not-a-regular-file", "the path is the working directory")
            return rest
    raise PathCheckError("outside-root", "no ancestor is the working directory")


def _spelled(fs: Any, parent: str, typed: str, identity: Tuple[Any, Any]) -> str:
    """The name the parent directory gives the entry with this ``(st_dev, st_ino)``.

    The typed name wins a tie, then the lowest code point. So a case variant of a path, or an
    NFC spelling on a volume that stores NFD, gives the same name as the canonical spelling.
    """
    try:
        names = set(fs.listdir(parent))
    except OSError as exc:
        raise PathCheckError("unreadable", "%s: %s" % (_short(parent), exc.strerror or exc)) from None
    if typed in names:
        return typed
    matches = []
    for name in names:
        try:
            entry = fs.lstat(posixpath.join(parent, name))
        except OSError:
            continue
        if (entry.st_dev, entry.st_ino) == identity:
            matches.append(name)
    if not matches:
        raise PathCheckError(
            "spelling", "no entry of %s has the identity of %s" % (_short(parent), _short(typed))
        )
    return min(matches)


def resolve_file(
    path: object,
    *,
    root: Optional[str] = None,
    allow_absolute: bool = False,
    fs: Any = None,
) -> ResolvedPath:
    """Validate ``path`` as a regular file below ``root`` and return its canonical spelling.

    ``root`` defaults to the working directory. The checks run in D7's order, and the first
    failure raises ``PathCheckError`` with its name:

    1. the syntactic rule (``tachi_parts.path_problem``): non-empty, at most 4,096 bytes, no
       control byte, backslash or backtick, no scheme, drive letter or ``..``, and no leading
       ``/`` unless ``allow_absolute``;
    2. an absolute path counts only if an ancestor is ``root`` by ``samefile``, and is made
       relative;
    3. an ``lstat`` walk from ``root``: every component exists, none is a symlink, every one
       but the last is a directory, and the last is a regular file;
    4. the spelling: each component takes the parent directory's own name for the entry with
       the same ``(st_dev, st_ino)`` (``_spelled``).

    The URI is the canonical path percent-encoded (``percent_encode``). Controls evidence
    ``file`` values use this with ``allow_absolute=False`` and the target directory as ``root``.
    """
    fs = OS_FILESYSTEM if fs is None else fs
    root = fs.getcwd() if root is None else root
    if not isinstance(root, str) or not posixpath.isabs(root):
        raise ValueError("root must be an absolute path, not %s" % _short(root))
    problem = tachi_parts.path_problem(path, allow_absolute=allow_absolute)
    if problem is not None:
        raise PathCheckError(problem)
    parts = list(tachi_parts.path_parts(path, allow_absolute=allow_absolute))
    if path.startswith("/"):  # type: ignore[union-attr]  -- path_problem refused every non-str
        parts = _below_root(parts, root, fs)
    current = root
    spelled: List[str] = []
    for index, typed in enumerate(parts):
        candidate = posixpath.join(current, typed)
        try:
            entry = fs.lstat(candidate)
        except FileNotFoundError:
            raise PathCheckError("missing", _short(typed)) from None
        except OSError as exc:
            raise PathCheckError("unreadable", "%s: %s" % (_short(typed), exc.strerror or exc)) from None
        if stat.S_ISLNK(entry.st_mode):
            raise PathCheckError("symlink", _short(typed))
        if index < len(parts) - 1:
            if not stat.S_ISDIR(entry.st_mode):
                raise PathCheckError("not-a-directory", _short(typed))
        elif not stat.S_ISREG(entry.st_mode):
            raise PathCheckError("not-a-regular-file", _short(typed))
        name = _spelled(fs, current, typed, (entry.st_dev, entry.st_ino))
        spelled.append(name)
        current = posixpath.join(current, name)
    try:
        uri = "/".join(percent_encode(name) for name in spelled)
    except UnicodeEncodeError:
        raise PathCheckError("encoding", "a component is not valid Unicode") from None
    return ResolvedPath("/".join(spelled), uri)


# --- the body line ------------------------------------------------------------

_FENCE_OPEN = re.compile(r" {0,3}(`{3,}|~{3,})")
_H2 = re.compile(r" {0,3}## ")
_SOURCE_LINE = re.compile(r"\*\*Architecture source\*\*: `([^`]+)`[ \t]*")


def _line_spans(text: str) -> List[Tuple[int, int, str]]:
    """``(start, end, line)`` for each line, split on ``\\n`` only (``end`` includes it).

    ``str.splitlines()`` also splits on U+2028, ``\\x0b`` and ``\\x85``. A prose line holding one
    of them would then show a forged line, so only ``\\n`` ends a line here (NFR-10).
    """
    spans = []
    pos = 0
    while pos < len(text):
        newline = text.find("\n", pos)
        stop = len(text) if newline == -1 else newline
        end = len(text) if newline == -1 else newline + 1
        spans.append((pos, end, text[pos:stop]))
        pos = end
    return spans


def _closes_fence(line: str, fence: str) -> bool:
    """True when ``line`` closes a code fence opened with ``fence`` (CommonMark's rule)."""
    opened = _FENCE_OPEN.match(line)
    return (
        opened is not None
        and opened.group(1)[0] == fence[0]
        and len(opened.group(1)) >= len(fence)
        and not line.strip(fence[0] + " ")
    )


def _anchor_scan(text: str) -> Tuple[int, int, List[Tuple[int, int, str]]]:
    """The anchor region's span, and every architecture-source line inside it (one pass)."""
    spans = _line_spans(text)
    first = 0
    if spans and spans[0][2].rstrip("\r") == "---":
        for index in range(1, len(spans)):
            if spans[index][2].rstrip("\r") == "---":
                first = index + 1
                break
    start = spans[first][0] if first < len(spans) else len(text)
    found: List[Tuple[int, int, str]] = []
    fence = ""
    for begin, end, raw in spans[first:]:
        line = raw.rstrip("\r")
        if fence:
            if _closes_fence(line, fence):
                fence = ""
            continue
        opened = _FENCE_OPEN.match(line)
        if opened:
            fence = opened.group(1)
            continue
        if _H2.match(line):
            return start, begin, found
        match = _SOURCE_LINE.fullmatch(line)
        if match:
            found.append((begin, end, match.group(1)))
    return start, len(text), found


def architecture_source_region(text: str) -> Tuple[int, int]:
    """The character span between the frontmatter and the first ``## `` heading (D7 item 6).

    The span starts after a leading ``---`` frontmatter block, if there is one, and stops at
    the first level-2 heading outside a code fence, or at the end of the text. The shipped upsert
    inserts the line at the span's end.
    """
    start, stop, _found = _anchor_scan(text)
    return start, stop


def find_architecture_source_lines(text: str) -> List[Tuple[int, int, str]]:
    """``(start, end, path)`` for each architecture-source line in the anchor region.

    A line is ``**Architecture source**: `<path>` `` starting at column 0, outside code fences,
    between the frontmatter and the first ``## `` heading. ``end`` includes the newline, so the
    span can be cut or replaced by the shipped upsert.
    """
    return _anchor_scan(text)[2]


def read_architecture_source(text: str) -> Optional[str]:
    """The body line's path, or ``None``. Zero matches, or several, read as absent."""
    lines = find_architecture_source_lines(text)
    return lines[0][2] if len(lines) == 1 else None


def format_architecture_source_line(path: str) -> str:
    """The body line for a canonical path. A path the line couldn't carry raises ``ValueError``."""
    problem = tachi_parts.path_problem(path, allow_absolute=True)
    if problem is not None:
        raise ValueError("a path the body line can't carry (%s): %s" % (problem, _short(path)))
    return "**Architecture source**: `%s`" % path


# --- the three candidates -----------------------------------------------------


class ArchitectureResolution(NamedTuple):
    """The architecture path a run uses, where it came from, and every warning on the way.

    ``source`` is ``explicit``, ``body-line``, ``default`` or ``default-literal`` (the constant,
    emitted as written because it did not validate). Each warning is a ``{code, detail}`` dict,
    ready for the stage record's ``warnings`` array.
    """

    path: str
    uri: str
    source: str
    warnings: Tuple[Dict[str, str], ...]


_LABELS = {
    "explicit": "the --architecture path",
    "body-line": "the architecture-source line",
    "default": "the default path",
}


def _warning(candidate: str, check: str, value: object, then: str) -> Dict[str, str]:
    """A fallback warning. It names the candidate, the failed check and the override flag."""
    if check == "absent":
        what = "the architecture-source line is absent from threats.md" if value is None else value
    else:
        what = "%s %s failed the %s check" % (_LABELS[candidate], _short(value), check)
    return {
        "code": "architecture-path:%s:%s" % (candidate, check),
        "detail": "%s; %s. Pass %s with the repo-relative path of the architecture file."
        % (what, then, ARCHITECTURE_FLAG),
    }


def _check_snapshot(run_dir: Optional[str], resolved: ResolvedPath, root: str, fs: Any) -> None:
    """NFR-10's name check on a body-line candidate (D7 item 4).

    ``run_dir`` is the directory of the ``threats.md`` that was read, and the candidate's last
    component is the snapshot's name. The snapshot ``{run_dir}/{basename}`` must be a regular
    file that isn't a symlink. The basename may not be one of D4's canonical output names, and
    by ``samefile`` the snapshot may not be the candidate itself. With no snapshot the line
    fails closed: it is untrusted content with no anchor.
    """
    basename = posixpath.basename(resolved.path)
    if basename.casefold() in _CANONICAL_OUTPUT_FOLDED:
        raise PathCheckError("canonical-name", _short(basename))
    if not run_dir:
        raise PathCheckError("no-snapshot", "no run directory to look in")
    run = run_dir if posixpath.isabs(run_dir) else posixpath.join(root, run_dir)
    snapshot = posixpath.join(run, basename)
    try:
        entry = fs.lstat(snapshot)
    except OSError:
        raise PathCheckError("no-snapshot", "%s has no %s" % (_short(run_dir), _short(basename))) from None
    if stat.S_ISLNK(entry.st_mode) or not stat.S_ISREG(entry.st_mode):
        raise PathCheckError("snapshot-not-regular", _short(basename))
    if _same_file(fs, snapshot, posixpath.join(root, resolved.path)):
        raise PathCheckError("is-snapshot", _short(basename))


def resolve_explicit(
    candidate: object,
    *,
    root: Optional[str] = None,
    fs: Any = None,
) -> Tuple[Optional[ResolvedPath], Optional[Dict[str, str]]]:
    """D7's first candidate, the explicit ``--architecture-path``, checked as the resolver checks it.

    It is the first step of ``resolve_architecture``, split out so that ``tachi-stage.py plan`` runs the same
    step, and so ``plan`` and the renderer agree on every check and on the warning's code and text (ruled at W2).
    Returns ``(resolved, None)`` when ``resolve_file(candidate, root=root, allow_absolute=True, fs=fs)`` passes.
    Otherwise it returns ``(None, warning)``, the ``{code, detail}`` that ``resolve_architecture`` lists for that
    failure: the code is ``architecture-path:explicit:<check>``, so the failed check's name is its last part, and
    the detail names the candidate in its escaped short form (``_short``), the check and ``--architecture-path``.
    Every check refuses alike, the syntactic ones (a control character, backslash or backtick) included.

    A candidate that isn't text fails the ``type`` check. ``None`` means "the flag was not given" to
    ``resolve_architecture``, which never asks here in that case. A ``root`` that isn't absolute is a caller's
    bug and raises ``ValueError``, as it does in ``resolve_file``.
    """
    try:
        return resolve_file(candidate, root=root, allow_absolute=True, fs=fs), None
    except PathCheckError as failure:
        return None, _warning("explicit", failure.check, candidate, "trying the architecture-source line")


def resolve_architecture(
    explicit: Optional[str] = None,
    *,
    threats_text: Optional[str] = None,
    run_dir: Optional[str] = None,
    root: Optional[str] = None,
    fs: Any = None,
) -> ArchitectureResolution:
    """Choose the architecture path for a run, in D7's order. Nothing here stops a run.

    1. ``explicit``: the ``--architecture-path`` flag, which reaches a script as
       ``--architecture PATH``, checked by ``resolve_explicit``. ``None`` means the flag was not given.
    2. The body line of ``threats_text``, the ``threats.md`` that was read, if it passes the
       checks and NFR-10's name check against the snapshot in ``run_dir``.
    3. ``DEFAULT_ARCHITECTURE_PATH``, in its canonical spelling if it validates, otherwise
       literally.

    A candidate that is absent or fails a check passes to the next with a warning that names
    it, the failed check and the flag. The constant is last, so a run always gets a path.
    """
    fs = OS_FILESYSTEM if fs is None else fs
    root = fs.getcwd() if root is None else root
    warnings: List[Dict[str, str]] = []

    if explicit is not None:
        resolved, refusal = resolve_explicit(explicit, root=root, fs=fs)
        if resolved is not None:
            return ArchitectureResolution(resolved.path, resolved.uri, "explicit", tuple(warnings))
        if refusal is not None:  # a refusal always comes with its warning
            warnings.append(refusal)

    line = read_architecture_source(threats_text) if threats_text is not None else None
    if line is None:
        what = (
            "no threats.md was read, so there is no architecture-source line"
            if threats_text is None
            else None
        )
        warnings.append(_warning("body-line", "absent", what, "trying the default path"))
    else:
        try:
            resolved = resolve_file(line, root=root, allow_absolute=True, fs=fs)
            _check_snapshot(run_dir, resolved, root, fs)
            return ArchitectureResolution(resolved.path, resolved.uri, "body-line", tuple(warnings))
        except PathCheckError as failure:
            warnings.append(_warning("body-line", failure.check, line, "trying the default path"))

    try:
        resolved = resolve_file(DEFAULT_ARCHITECTURE_PATH, root=root, allow_absolute=False, fs=fs)
        return ArchitectureResolution(resolved.path, resolved.uri, "default", tuple(warnings))
    except PathCheckError as failure:
        warnings.append(
            _warning("default", failure.check, DEFAULT_ARCHITECTURE_PATH, "emitting it as written")
        )
    return ArchitectureResolution(
        DEFAULT_ARCHITECTURE_PATH,
        "/".join(percent_encode(part) for part in DEFAULT_ARCHITECTURE_PATH.split("/")),
        "default-literal",
        tuple(warnings),
    )


# =============================================================================
# D7: identity (T015): tools, categories, rule IDs, the hash and the fingerprints
# =============================================================================
#
# GitHub matches an alert on four parts: the tool and upload category, the `ruleId`,
# `primaryLocationLineHash` and `artifactLocation.uri`. This section pins the first three; the
# resolver above pins the fourth. Nothing else is identity (the shared reference says so).
# The constants below are the "Emitter Constants" and tables of
# `.claude/skills/tachi-shared/references/sarif-identity-shared.md`; a test compares them.

# `tool.driver.name` and the upload `category` of each file. A tool name is a hash input, so a
# different spelling re-keys every alert in the file: `Tachi` has a capital T.
TOOL_NAMES = {
    "threats.sarif": "Tachi",
    "risk-scores.sarif": "tachi-risk-scorer",
    "compensating-controls.sarif": "tachi-control-analyzer",
}
UPLOAD_CATEGORIES = {
    "threats.sarif": "threat-model",
    "risk-scores.sarif": "risk-score",
    "compensating-controls.sarif": "compensating-controls",
}
INFORMATION_URI = "https://github.com/davidmatousek/tachi"

# Eight rule IDs, one for each category, and twelve prefixes that reach them. `AG`, `AGP` and
# `TE` are agentic; `LLM`, `OI` and `MI` are llm. The prefix-to-category step is the one resolver
# in `tachi_scoring` (D10), so a finding is scored and keyed the same whichever prefix it has.
# The legacy short forms (`tachi/ai/agentic`, `tachi/ai/llm`) are never emitted.
RULE_ID_BY_CATEGORY = {
    "spoofing": "tachi/stride/spoofing",
    "tampering": "tachi/stride/tampering",
    "repudiation": "tachi/stride/repudiation",
    "info-disclosure": "tachi/stride/information-disclosure",
    "denial-of-service": "tachi/stride/denial-of-service",
    "privilege-escalation": "tachi/stride/elevation-of-privilege",
    "agentic": "tachi/ai/agentic-threats",
    "llm": "tachi/ai/llm-threats",
}
RULE_ID_BY_PREFIX = {
    prefix: RULE_ID_BY_CATEGORY[category] for prefix, category in tachi_scoring.PREFIX_CATEGORY.items()
}

HASH_RECIPE_TAG = "tachi-plh/1"
HASH_HEX_DIGITS = 16
HASH_SUFFIX = ":1"
REGION = {"startLine": 1}
FINGERPRINT_KEYS = ("primaryLocationLineHash", "findingId/v1")
FLAG_PROPERTIES = {"risk-scores.sarif": "score-flags", "compensating-controls.sarif": "integrity-flags"}
EVIDENCE_MESSAGE = "Control evidence: {category} detected in {file}"
LEVELS = ("error", "warning", "note", "none")
FORBIDDEN_RESULT_KEYS = ("guid", "correlationGuid", "fingerprints", "baselineState")
STAMP_KEYS = ("renderer", "version", "input_digest")


def _tool(tool: object) -> str:
    """``tool`` if it is one of the three driver names, else ``ValueError`` (a typo would re-key)."""
    if tool not in TOOL_NAMES.values():
        raise ValueError(
            "not a tachi tool name: %s; expected one of %s" % (_short(tool), sorted(TOOL_NAMES.values()))
        )
    return tool  # type: ignore[return-value]


def rule_id_for(finding_id: str) -> str:
    """The ``ruleId`` of a finding: its prefix selects the category, and the category the rule."""
    prefix = tachi_parts.canonical_finding_id(finding_id).partition("-")[0]
    return RULE_ID_BY_PREFIX[prefix]


def primary_location_line_hash(tool: str, finding_id: str) -> str:
    """tachi's own ``primaryLocationLineHash``: ``sha256("tachi-plh/1|" + tool + "|" + id)``.

    Over UTF-8, the first 16 lowercase hex digits, then ``:1``. ``tool`` is the file's driver
    name and ``id`` the canonical finding ID, so ``AGP-01`` hashes as ``AGP-1``. A function of the
    tool and the ID alone: a regroup, a re-score or an upgrade can't move it, and no model prose
    goes in. An ID outside the allow-list, or a tool name that isn't one of the three, raises
    ``ValueError`` (NFR-10).
    """
    canonical = tachi_parts.canonical_finding_id(finding_id)
    key = "%s|%s|%s" % (HASH_RECIPE_TAG, _tool(tool), canonical)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:HASH_HEX_DIGITS] + HASH_SUFFIX


def partial_fingerprints(tool: str, finding_id: str) -> Dict[str, str]:
    """Exactly two keys, in order: the hash and ``findingId/v1`` (the ID as Section 7 writes it).

    SARIF counts every partial fingerprint toward identity, so nothing that changes on a regroup
    or a re-assessment goes here (``correlationGroup`` and ``baselineRunId`` are properties).
    """
    return {
        FINGERPRINT_KEYS[0]: primary_location_line_hash(tool, finding_id),
        FINGERPRINT_KEYS[1]: finding_id,
    }


# =============================================================================
# D8: membership and correlation
# =============================================================================

CORRELATION_KEYS = ("correlation-group", "correlation-role", "correlation-primary")
CORRELATION_ROLES = ("primary", "peer")
PEER_CAP = 10
PEER_SENTENCE = "Correlated in {group}; primary {id}."
PRIMARY_SENTENCE = "Correlated in {group}; peers {ids}."
PRIMARY_SENTENCE_OVER_CAP = "Correlated in {group}; peers {ids} and {n} more."
_SENTENCE_TAIL = re.compile(r"(?:^| )Correlated in CG-[0-9]{1,6}; (?:primary|peers) ")


class Correlation(NamedTuple):
    """A correlated finding's place in its group: ``role`` is ``primary`` or ``peer``.

    ``primary`` is the primary's ID (its own, on the primary). ``peers`` is the other members in
    the group's listed order, and is empty on a peer.
    """

    group: str
    role: str
    primary: str
    peers: Tuple[str, ...]


def correlation_assignments(
    groups: Iterable[Tuple[str, Sequence[str]]],
    member_ids: Iterable[str],
) -> Dict[str, Correlation]:
    """Each correlated finding's group, role and primary, keyed by canonical finding ID (D8).

    ``groups`` is Section 4a's ``(group ID, member IDs)`` rows in file order, as
    ``tachi_parsers.parse_correlation_groups`` reads them. ``member_ids`` is the file's member
    set. The rules:

    * groups keep their order, and members their listed order, filtered to the member set;
    * an ID listed in two groups stays in the first, even if that group then falls away;
    * the primary is the first remaining member;
    * a group left with fewer than two members emits nothing.

    A group ID outside ``CG-[0-9]{1,6}``, or a member outside the finding-ID allow-list, raises
    ``ValueError``: the parser skips such rows, so one that arrives here is a bug.
    """
    members = {tachi_parts.canonical_finding_id(member) for member in member_ids}
    claimed = set()
    out: Dict[str, Correlation] = {}
    for group, listed in groups:
        if not tachi_parts.id_matches("group", group):
            raise ValueError("not a correlation group ID: %s" % _short(group))
        own = []
        for member in listed:
            canonical = tachi_parts.canonical_finding_id(member)
            if canonical not in claimed:
                claimed.add(canonical)
                own.append(canonical)
        remaining = [member for member in own if member in members]
        if len(remaining) < 2:
            continue
        primary, peers = remaining[0], tuple(remaining[1:])
        out[primary] = Correlation(group, "primary", primary, peers)
        for peer in peers:
            out[peer] = Correlation(group, "peer", primary, ())
    return out


def correlation_sentence(correlation: Correlation) -> str:
    """Ruling C's sentence for one correlated result.

    ``Correlated in CG-3; primary S-1.`` on a peer; ``Correlated in CG-3; peers T-2, I-4.`` on a
    primary, which names its first ``PEER_CAP`` peers and adds `` and N more`` only when there are
    more than that. It names only the file's members, so no RESOLVED ID appears.
    """
    if correlation.role == "peer":
        return PEER_SENTENCE.format(group=correlation.group, id=correlation.primary)
    if correlation.role != "primary":
        raise ValueError("not a correlation role: %s" % _short(correlation.role))
    named = correlation.peers[:PEER_CAP]
    ids = ", ".join(named)
    if len(correlation.peers) > PEER_CAP:
        return PRIMARY_SENTENCE_OVER_CAP.format(
            group=correlation.group, ids=ids, n=len(correlation.peers) - PEER_CAP
        )
    return PRIMARY_SENTENCE.format(group=correlation.group, ids=ids)


def correlated_message(text: str, correlation: Optional[Correlation]) -> str:
    """The file's own message text, plus ruling C's sentence after one space when correlated."""
    if not isinstance(text, str) or not text:
        raise ValueError("a result's message text must be a non-empty string")
    return text if correlation is None else "%s %s" % (text, correlation_sentence(correlation))


# =============================================================================
# The result, the run and the document (one shape, one key order)
# =============================================================================


def evidence_location(index: int, category: str, evidence: ResolvedPath, line: int) -> Dict[str, Any]:
    """One controls ``relatedLocations`` entry: code evidence with a ``physicalLocation``.

    ``evidence`` comes from ``resolve_file`` (relative to the target directory, so it passed the
    relative-path checks). An entry never names a finding (D8).
    """
    if isinstance(line, bool) or not isinstance(line, int) or line < 1:
        raise ValueError("an evidence line is a positive integer, not %s" % _short(line))
    if not isinstance(category, str) or not category:
        raise ValueError("an evidence category is a non-empty string")
    return {
        "id": index,
        "message": {"text": EVIDENCE_MESSAGE.format(category=category, file=evidence.path)},
        "physicalLocation": {"artifactLocation": {"uri": evidence.uri}, "region": {"startLine": line}},
    }


def build_result(
    *,
    tool: str,
    finding_id: str,
    message: str,
    level: str,
    uri: str,
    component: str,
    zone: str,
    kind: str,
    properties: Optional[Mapping[str, Any]] = None,
    correlation: Optional[Correlation] = None,
    related_locations: Sequence[Mapping[str, Any]] = (),
    markdown: Optional[str] = None,
) -> Dict[str, Any]:
    """One SARIF result, in the shared shape and key order (ADR-050 D7, D8).

    ``ruleId``, ``message``, ``level``, ``locations``, ``relatedLocations`` (only when there are
    any), ``partialFingerprints``, ``properties``. ``uri`` is the resolver's one URI for the run.
    ``message`` is the file's own text; ruling C's sentence is added after one space when
    ``correlation`` is given, and the three ``correlation-*`` properties follow ``properties``.
    No result carries ``guid``, ``correlationGuid``, ``fingerprints`` or SARIF's own
    ``baselineState``. ``properties`` may not hold a ``correlation-*`` key: the emitter owns them.

    ``markdown`` is the optional ``message.markdown`` that a file whose contract maps it keeps
    (the scorer's mitigation text; NFR-1 keeps adopter fields). Given, the message is
    ``{text, markdown}`` in that order, and ruling C's sentence is added to ``text`` alone. Not
    given, the message is ``{text}`` and the result is byte-for-byte what it was without the
    parameter. Any string is accepted, an empty one included: shipped scorer files carry empty
    mitigations. ``self_check`` refuses a local path in it.
    """
    for name, value in (("uri", uri), ("component", component), ("zone", zone), ("kind", kind)):
        if not isinstance(value, str) or not value:
            raise ValueError("%s must be a non-empty string, not %s" % (name, _short(value)))
    if level not in LEVELS:
        raise ValueError("not a SARIF level: %s" % _short(level))
    if markdown is not None and not isinstance(markdown, str):
        raise ValueError("markdown must be a string, not %s" % _short(markdown))
    props: Dict[str, Any] = dict(properties or {})
    clash = [key for key in CORRELATION_KEYS if key in props]
    if clash:
        raise ValueError("properties may not hold %s: the emitter writes them" % clash)
    if correlation is not None:
        props["correlation-group"] = correlation.group
        props["correlation-role"] = correlation.role
        props["correlation-primary"] = correlation.primary
    message_object: Dict[str, str] = {"text": correlated_message(message, correlation)}
    if markdown is not None:
        message_object["markdown"] = markdown
    result: Dict[str, Any] = {
        "ruleId": rule_id_for(finding_id),
        "message": message_object,
        "level": level,
        "locations": [
            {
                "physicalLocation": {"artifactLocation": {"uri": uri}, "region": dict(REGION)},
                "logicalLocations": [
                    {"name": component, "fullyQualifiedName": "%s/%s" % (zone, component), "kind": kind}
                ],
            }
        ],
    }
    if related_locations:
        result["relatedLocations"] = [dict(entry) for entry in related_locations]
    result["partialFingerprints"] = partial_fingerprints(tool, finding_id)
    result["properties"] = props
    return result


def provenance_stamp(renderer: str, version: str, input_digest: str) -> Dict[str, str]:
    """``runs[0].properties.tachi_provenance``: the renderer, its version and the input digest.

    ``version`` is ``X.Y.Z`` (``tachi_parts.VERSION``) and ``input_digest`` is ``sha256:<64 hex>``,
    the same digest the stage record and the markdown stamp carry (ADR-050 D4). The plan ID is
    not in it, so the output stays byte-stable.
    """
    patterns = (
        ("renderer", renderer, re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")),
        ("version", version, re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")),
        ("input_digest", input_digest, re.compile(r"sha256:[0-9a-f]{64}")),
    )
    for name, value, pattern in patterns:
        if not isinstance(value, str) or pattern.fullmatch(value) is None:
            raise ValueError("not a valid provenance %s: %s" % (name, _short(value)))
    return {"renderer": renderer, "version": version, "input_digest": input_digest}


def build_driver(
    sarif_file: str,
    *,
    semantic_version: str,
    rules: Sequence[Mapping[str, Any]],
    supported: Optional[Sequence[Mapping[str, Any]]] = None,
    version: Optional[str] = None,
) -> Dict[str, Any]:
    """The ``tool.driver`` of a file: its verbatim tool name and the real ``informationUri``.

    ``version`` is optional (PM W3 ruling 2, gap C). Given, ``"version"`` is written right after
    ``"name"``, where the 1.1 templates put it, and the two PR 1 renderers pass the same
    ``tachi_parts.VERSION`` that ``semantic_version`` holds. Not given, there is no ``"version"`` key:
    ``threats.sarif``'s driver passes none, and its bytes don't move.
    """
    if sarif_file not in TOOL_NAMES:
        raise ValueError(
            "not a tachi SARIF file: %s; expected one of %s" % (_short(sarif_file), sorted(TOOL_NAMES))
        )
    if version is not None and not _is_text(version):
        raise ValueError("version must be a non-empty string, not %s" % _short(version))
    driver: Dict[str, Any] = {"name": TOOL_NAMES[sarif_file]}
    if version is not None:
        driver["version"] = version
    driver["semanticVersion"] = semantic_version
    driver["informationUri"] = INFORMATION_URI
    if supported is not None:
        driver["supportedTaxonomies"] = [dict(entry) for entry in supported]
    driver["rules"] = [dict(rule) for rule in rules]
    return driver


def build_document(
    driver: Mapping[str, Any],
    taxonomies: Sequence[Mapping[str, Any]],
    results: Sequence[Mapping[str, Any]],
    stamp: Mapping[str, str],
    *,
    schema_first: bool = False,
) -> Dict[str, Any]:
    """The SARIF 2.1.0 document: the legacy envelope plus ``runs[0].properties.tachi_provenance``.

    The driver's name must be one of the three tool names and its ``informationUri`` the real
    one, never a placeholder (FR-E.9). No file carries ``runs[].automationDetails``: the upload
    step's ``category`` input governs, so tachi recommends a category and never writes one.
    """
    _tool(driver.get("name"))
    if driver.get("informationUri") != INFORMATION_URI:
        raise ValueError(
            "tool.driver.informationUri must be %s, not %s"
            % (INFORMATION_URI, _short(driver.get("informationUri")))
        )
    if list(stamp) != list(STAMP_KEYS):
        raise ValueError("the provenance stamp has the keys %s, in that order" % list(STAMP_KEYS))
    document = build_sarif_envelope(dict(driver), list(taxonomies), list(results), schema_first=schema_first)
    document["runs"][0]["properties"] = {"tachi_provenance": dict(stamp)}
    return document


def to_json(document: Mapping[str, Any]) -> str:
    """The document as two-space JSON with a final newline, in the order it was built.

    ASCII only: every non-ASCII character is written as a ``\\uXXXX`` escape, so a bidi,
    zero-width or U+2028 character in a name can't forge structure in the file. The bytes depend
    on the document alone, so an unchanged re-run writes the same bytes.
    """
    return json.dumps(document, indent=2, ensure_ascii=True) + "\n"


# =============================================================================
# The self-check (D7, D8): it runs on the finished result list, before any write
# =============================================================================


class SelfCheckError(ValueError):
    """The finished results break a D7 or D8 rule. ``problems`` holds every one found."""

    def __init__(self, problems: Sequence[str]) -> None:
        shown = list(problems)[:20]
        more = len(problems) - len(shown)
        tail = "; and %d more" % more if more else ""
        super().__init__("SARIF self-check failed: " + "; ".join(shown) + tail)
        self.problems = list(problems)


_HASH_FORM = re.compile(r"[0-9a-f]{16}:1")
_LEGACY_PEER_REFERENCE = re.compile(r"([A-Za-z]+-[0-9]+): ")

# A local path: an absolute path that starts at one of H8's roots (NFR-6's list, as in
# ``test_fixture_374.py``), or a Windows drive path. The root must start the path, so a relative path or a
# URL path with a segment of that name is not a hit, and a ``file:`` URL on a root is. Built in pieces, so
# this file holds no path itself.
_LOCAL_PATH_ROOTS = ("Us" + "ers", "ho" + "me", "pri" + "vate", "t" + "mp", "var/fol" + "ders")
_LOCAL_PATH = re.compile(
    "(?<![A-Za-z0-9_.~-])/(%s)/|(?<![A-Za-z0-9])[A-Za-z]:\\\\[A-Za-z]" % "|".join(_LOCAL_PATH_ROOTS)
)


def _is_text(value: object) -> bool:
    return isinstance(value, str) and value != ""


def _shape_problems(result: object) -> List[str]:
    """What is wrong with a result's shape, key order or forbidden keys (D7's result shape)."""
    if not isinstance(result, dict):
        return ["a result is not an object"]
    out: List[str] = []
    expected = ["ruleId", "message", "level", "locations"]
    if "relatedLocations" in result:
        expected.append("relatedLocations")
    expected += ["partialFingerprints", "properties"]
    if list(result) != expected:
        out.append("its keys are %s, not %s" % (list(result), expected))
    out += ["it carries %s" % key for key in FORBIDDEN_RESULT_KEYS if key in result]
    message = result.get("message")
    if not (
        isinstance(message, dict)
        and list(message) in (["text"], ["text", "markdown"])
        and _is_text(message["text"])
    ):
        out.append("message is not {text: <non-empty string>} or {text, markdown}, in that order")
    elif "markdown" in message:
        if not isinstance(message["markdown"], str):
            out.append("message.markdown is not a string")
        else:
            local = _LOCAL_PATH.search(message["markdown"])
            if local:
                out.append("message.markdown holds a local path (%s)" % _short(local.group(0)))
    if result.get("level") not in LEVELS:
        out.append("level is not a SARIF level")
    locations = result.get("locations")
    if not (isinstance(locations, list) and len(locations) == 1 and isinstance(locations[0], dict)):
        out.append("locations is not a one-element list")
    else:
        location = locations[0]
        physical = location.get("physicalLocation")
        artifact = physical.get("artifactLocation") if isinstance(physical, dict) else None
        if not (
            list(location) == ["physicalLocation", "logicalLocations"]
            and isinstance(artifact, dict)
            and list(artifact) == ["uri"]
            and _is_text(artifact["uri"])
            and list(physical) == ["artifactLocation", "region"]
            and physical["region"] == REGION
        ):
            out.append("the location is not {physicalLocation: {artifactLocation, region}, logicalLocations}")
        logical = location.get("logicalLocations")
        if not (
            isinstance(logical, list)
            and len(logical) == 1
            and isinstance(logical[0], dict)
            and list(logical[0]) == ["name", "fullyQualifiedName", "kind"]
            and all(_is_text(value) for value in logical[0].values())
        ):
            out.append("logicalLocations is not one {name, fullyQualifiedName, kind}")
    if "relatedLocations" in result:
        related = result["relatedLocations"]
        if not (isinstance(related, list) and related):
            out.append("relatedLocations is present but empty")
        else:
            for entry in related:
                physical = entry.get("physicalLocation") if isinstance(entry, dict) else None
                region = physical.get("region") if isinstance(physical, dict) else None
                if not (
                    list(entry) == ["id", "message", "physicalLocation"]
                    and isinstance(entry["message"], dict)
                    and _is_text(entry["message"].get("text"))
                    and isinstance(physical, dict)
                    and isinstance(physical.get("artifactLocation"), dict)
                    and _is_text(physical["artifactLocation"].get("uri"))
                    and isinstance(region, dict)
                    and list(region) == ["startLine"]
                    and isinstance(region["startLine"], int)
                    and region["startLine"] >= 1
                ):
                    out.append("a relatedLocations entry is not code evidence with a physicalLocation")
    fingerprints = result.get("partialFingerprints")
    if not (isinstance(fingerprints, dict) and list(fingerprints) == list(FINGERPRINT_KEYS)):
        out.append("partialFingerprints is not exactly %s" % list(FINGERPRINT_KEYS))
    else:
        line_hash = fingerprints[FINGERPRINT_KEYS[0]]
        if not (isinstance(line_hash, str) and _HASH_FORM.fullmatch(line_hash)):
            out.append("primaryLocationLineHash is not <16 lowercase hex>:1")
    if not isinstance(result.get("properties"), dict):
        out.append("properties is not an object")
    return out


def _strings_that_name_findings(result: Mapping[str, Any]) -> Iterable[Tuple[str, str]]:
    """``(where, text)`` for every place a result may name a finding: message, properties, evidence."""
    yield "message", result["message"]["text"]
    if "markdown" in result["message"]:
        yield "message.markdown", result["message"]["markdown"]
    yield "findingId/v1", result["partialFingerprints"][FINGERPRINT_KEYS[1]]
    stack: List[Tuple[str, Any]] = [("properties", result["properties"])]
    while stack:
        where, value = stack.pop()
        if isinstance(value, str):
            yield where, value
        elif isinstance(value, Mapping):
            stack.extend(("%s.%s" % (where, key), item) for key, item in value.items())
        elif isinstance(value, (list, tuple)):
            stack.extend(("%s[%d]" % (where, index), item) for index, item in enumerate(value))
    for entry in result.get("relatedLocations", ()):
        yield "relatedLocations", entry["message"]["text"]


def _id_token_pattern(ids: Iterable[str]) -> "re.Pattern[str]":
    """A pattern for any of these finding IDs as a whole token, zero-padded spellings included."""
    spellings = []
    for finding_id in sorted(ids):
        prefix, _, number = finding_id.partition("-")
        spellings.append("%s-0*%s" % (re.escape(prefix), number))
    return re.compile(r"(?<![A-Za-z0-9-])(?:%s)(?![A-Za-z0-9-])" % "|".join(spellings))


def self_check(
    results: Sequence[Mapping[str, Any]],
    *,
    tool: str,
    member_ids: Iterable[str],
    assignments: Optional[Mapping[str, Correlation]] = None,
    resolved_ids: Iterable[str] = (),
    uri: Optional[str] = None,
) -> None:
    """Check a file's finished results against D7 and D8 before anything is written.

    Raises ``SelfCheckError`` listing every problem. It asserts that:

    * each result has the shared shape and key order, and no ``guid``, ``correlationGuid``,
      ``fingerprints`` or ``baselineState``; its message is ``{text}`` or ``{text, markdown}``,
      and a ``markdown`` is a string (an empty one passes) that holds no local path;
    * the result count equals the number of distinct finding IDs, which equals the member set;
    * every ``primaryLocationLineHash`` is tachi's own for ``tool`` and the ID, and no two
      present results share one (the error names both IDs); every ``ruleId`` is the ID's rule;
    * every result has the one ``uri`` (``uri``, when given);
    * no RESOLVED ID (``resolved_ids`` less the member set) appears in a message (its markdown
      included), a property or a ``relatedLocations`` entry, and no ``relatedLocations`` entry
      names a finding or sits outside the controls file, and every ``relatedLocations`` uri
      passes ``tachi_parts.path_problem``, the resolver's own relative-path rule (the error names
      the finding and the failed check);
    * every ``correlation-primary`` and every group member is a result, with one primary per
      group, every correlated result's message ends with ruling C's sentence, and an
      uncorrelated result carries neither the keys nor the sentence.

    ``assignments`` is ``correlation_assignments``' output for the same member set.
    """
    _tool(tool)
    problems: List[str] = []

    def canonical_set(ids: Iterable[str], what: str) -> set:
        out = set()
        for finding_id in ids:
            try:
                out.add(tachi_parts.canonical_finding_id(finding_id))
            except ValueError:
                problems.append("%s %s is not a finding ID" % (what, _short(finding_id)))
        return out

    members = canonical_set(member_ids, "member")
    resolved = canonical_set(resolved_ids, "RESOLVED") - members
    correlated = dict(assignments or {})

    by_id: Dict[str, Mapping[str, Any]] = {}
    hash_owners: Dict[str, List[str]] = {}
    uris = set()
    for position, result in enumerate(results):
        shape = _shape_problems(result)
        if shape:
            problems.extend("result %d: %s" % (position, problem) for problem in shape)
            continue
        written = result["partialFingerprints"][FINGERPRINT_KEYS[1]]
        try:
            canonical = tachi_parts.canonical_finding_id(written)
        except ValueError:
            problems.append("result %d: findingId/v1 %s is not a finding ID" % (position, _short(written)))
            continue
        if canonical in by_id:
            problems.append("two results are for %s" % canonical)
        by_id[canonical] = result
        found = result["partialFingerprints"][FINGERPRINT_KEYS[0]]
        hash_owners.setdefault(found, []).append(written)
        if found != primary_location_line_hash(tool, written):
            problems.append("%s: primaryLocationLineHash %s is not tachi's own" % (written, found))
        if result["ruleId"] != rule_id_for(written):
            problems.append(
                "%s: ruleId %s is not %s" % (written, _short(result["ruleId"]), rule_id_for(written))
            )
        uris.add(result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"])

    for value, owners in hash_owners.items():
        if len(owners) > 1:
            problems.append("%s share primaryLocationLineHash %s" % (" and ".join(owners), value))
    if len(uris) > 1:
        problems.append("artifactLocation.uri differs between results: %s" % sorted(uris)[:3])
    elif uri is not None and uris and uris != {uri}:
        problems.append(
            "artifactLocation.uri is %s, not the run's %s" % (_short(next(iter(uris))), _short(uri))
        )

    ordered = tachi_parts.finding_sort_key
    missing = sorted(members - set(by_id), key=ordered)
    extra = sorted(set(by_id) - members, key=ordered)
    if missing:
        problems.append("member findings with no result: %s" % ", ".join(missing[:20]))
    if extra:
        problems.append("results for findings outside the member set: %s" % ", ".join(extra[:20]))

    if resolved:
        pattern = _id_token_pattern(resolved)
        for finding_id, result in by_id.items():
            for where, text in _strings_that_name_findings(result):
                hit = pattern.search(text)
                if hit:
                    problems.append(
                        "%s: the RESOLVED finding %s appears in %s" % (finding_id, hit.group(0), where)
                    )

    for finding_id, result in by_id.items():
        for entry in result.get("relatedLocations", ()):
            if tool != TOOL_NAMES["compensating-controls.sarif"]:
                problems.append("%s: relatedLocations appear in the controls file only" % finding_id)
                break
            lead = _LEGACY_PEER_REFERENCE.match(entry["message"]["text"])
            if lead and tachi_parts.id_matches("finding", lead.group(1)):
                problems.append(
                    "%s: a relatedLocations entry names the finding %s" % (finding_id, lead.group(1))
                )
            # D7: an evidence URI is relative to the target. The test is the resolver's own syntactic
            # rule, `tachi_parts.path_problem` (a leading slash, scheme, drive letter, backslash and
            # `..` among its checks), called here and never restated.
            # AOD-SIMPLIFICATION: checks the URI as written, not percent-decoded (the emitter encodes "%", so it never writes %2E) — upgrade: unquote first
            evidence_uri = entry["physicalLocation"]["artifactLocation"]["uri"]
            failed = tachi_parts.path_problem(evidence_uri)
            if failed is not None:
                problems.append(
                    "%s: a relatedLocations uri %s fails the resolver's %s check"
                    % (finding_id, _short(evidence_uri), failed)
                )

    primaries: Dict[str, List[str]] = {}
    for finding_id, result in by_id.items():
        properties, text = result["properties"], result["message"]["text"]
        correlation = correlated.get(finding_id)
        if correlation is None:
            carried = [key for key in CORRELATION_KEYS if key in properties]
            if carried:
                problems.append("%s: not correlated, but carries %s" % (finding_id, carried))
            if _SENTENCE_TAIL.search(text):
                problems.append("%s: not correlated, but its message holds the sentence" % finding_id)
            continue
        wanted = dict(zip(CORRELATION_KEYS, (correlation.group, correlation.role, correlation.primary)))
        for key in CORRELATION_KEYS:
            if properties.get(key) != wanted[key]:
                problems.append(
                    "%s: %s is %s, not %s" % (finding_id, key, _short(properties.get(key)), wanted[key])
                )
        if not text.endswith(" " + correlation_sentence(correlation)):
            problems.append("%s: the message does not end with ruling C's sentence" % finding_id)
        elif len(_SENTENCE_TAIL.findall(text)) != 1:
            problems.append("%s: the message holds ruling C's sentence more than once" % finding_id)
        if correlation.role == "primary":
            primaries.setdefault(correlation.group, []).append(finding_id)
        for named in (correlation.primary,) + tuple(correlation.peers):
            if named not in by_id:
                problems.append(
                    "%s: %s, in its group %s, is not a result" % (finding_id, named, correlation.group)
                )
    for finding_id in correlated:
        if finding_id not in by_id:
            problems.append("%s: correlated, but has no result" % finding_id)
    for group in sorted({c.group for c in correlated.values()}):
        if len(primaries.get(group, [])) != 1:
            problems.append("group %s has %d primaries, not one" % (group, len(primaries.get(group, []))))

    if problems:
        raise SelfCheckError(problems)


# =============================================================================
# The taxa (embedded, so the core path needs no PyYAML)
# =============================================================================
#
# What the scorer and controls files carry under `taxonomies`, and the driver's
# `supportedTaxonomies` derived from it. The OWASP-LLM entry is the 2026 catalog
# (`schemas/taxonomy/owasp.yaml`: ids, names, one URL, one edition), and
# `tests/scripts/test_sarif_identity.py` compares every value with the catalog, so a catalog
# bump that isn't copied here fails CI. The OWASP-ASI and CWE entries keep the display names the
# scorer's generator used; the test checks that each of their IDs is in its catalog.

LLM_EDITION = "2026"
LLM_INFORMATION_URI = "https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/"

TAXONOMIES = [
    {
        "name": "OWASP-LLM",
        "version": LLM_EDITION,
        "guid": "b4da3eca-0deb-4f4e-8c3c-1c0e2d3f4a5b",
        "informationUri": LLM_INFORMATION_URI,
        "taxa": [
            {"id": "LLM01", "name": "Prompt Injection"},
            {"id": "LLM02", "name": "Sensitive Information Disclosure"},
            {"id": "LLM03", "name": "Excessive Agency"},
            {"id": "LLM04", "name": "Supply Chain"},
            {"id": "LLM05", "name": "Data and Model Poisoning"},
            {"id": "LLM06", "name": "Unbounded Consumption"},
            {"id": "LLM07", "name": "Misinformation"},
            {"id": "LLM08", "name": "Hidden Context Exposure"},
            {"id": "LLM09", "name": "Vector and Embedding Weaknesses"},
            {"id": "LLM10", "name": "Improper Output Handling"},
        ],
    },
    {
        "name": "OWASP-ASI",
        "version": "2026",
        "guid": "c4da3eca-0deb-4f4e-8c3c-1c0e2d3f4a5b",
        "informationUri": "https://owasp.org/",
        "taxa": [
            {"id": "ASI01", "name": "Agent Autonomy Abuse"},
            {"id": "ASI07", "name": "Insecure Inter-Agent Communication"},
        ],
    },
    {
        "name": "CWE",
        "version": "4.13",
        "guid": "a4da3eca-0deb-4f4e-8c3c-1c0e2d3f4a5b",
        "informationUri": "https://cwe.mitre.org/",
        "taxa": [
            {"id": "CWE-78", "name": "OS Command Injection"},
            {"id": "CWE-79", "name": "Cross-site Scripting"},
            {"id": "CWE-89", "name": "SQL Injection"},
            {"id": "CWE-223", "name": "Omission of Security-relevant Information"},
            {"id": "CWE-287", "name": "Improper Authentication"},
            {"id": "CWE-345", "name": "Insufficient Verification of Data Authenticity"},
            {"id": "CWE-918", "name": "Server-Side Request Forgery (SSRF)"},
        ],
    },
]


def supported_taxonomies() -> List[Dict[str, Any]]:
    """The driver's ``supportedTaxonomies``, derived from ``TAXONOMIES`` (name, index, guid, ...)."""
    return [
        {
            "name": taxonomy["name"],
            "index": index,
            "guid": taxonomy["guid"],
            "version": taxonomy["version"],
            "informationUri": taxonomy["informationUri"],
        }
        for index, taxonomy in enumerate(TAXONOMIES)
    ]


# =============================================================================
# The rules (one table for risk-scores.sarif and compensating-controls.sarif)
# =============================================================================
#
# What each rule says, in the 1.1 templates' order (`templates/tachi/output-schemas/`): (category, short
# description, full description, tags, taxonomy IDs the rule relates to). Both renderers write their rules from
# here, so the two files can't drift apart, and `tests/scripts/test_sarif_identity.py` pins every field to both
# templates. The IDs are what a `{{ref:...}}` slot may cite for a finding of that category (ADR-050 D3's table),
# and each rule writes them as its `relationships` (PM W3 ruling 2, gap A).
RULES = (
    ("spoofing", "Identity spoofing threats",
     "Threats where an attacker pretends to be something or someone else, such as forging authentication credentials, "
     "replaying tokens, or impersonating trusted components to gain unauthorized access.",
     ("security", "stride", "spoofing", "authentication", "owasp", "cwe"), ("A07", "CWE-287")),
    ("tampering", "Data tampering threats",
     "Threats where an attacker modifies data, code, or configuration without authorization, violating integrity "
     "guarantees and causing systems to operate on corrupted inputs or persist falsified records.",
     ("security", "stride", "tampering", "data-integrity", "owasp", "cwe"), ("A08", "CWE-345")),
    ("repudiation", "Repudiation threats",
     "Threats where a user or system can deny having performed an action, and the system lacks sufficient evidence to "
     "prove otherwise, undermining accountability and forensic investigation.",
     ("security", "stride", "repudiation", "logging", "accountability", "owasp", "cwe"), ("A09", "CWE-778")),
    ("info-disclosure", "Information disclosure threats",
     "Threats where sensitive information is exposed to unauthorized parties through direct data leaks, verbose error "
     "messages, side-channel observations, or insufficient access controls on stored data.",
     ("security", "stride", "information-disclosure", "data-exposure", "owasp", "cwe"), ("A01", "CWE-200")),
    ("denial-of-service", "Denial of service threats",
     "Threats where an attacker degrades or eliminates system availability through resource exhaustion, flooding, "
     "algorithmic complexity exploitation, or cascading dependency failures.",
     ("security", "stride", "denial-of-service", "availability", "owasp", "cwe"), ("A05", "CWE-400")),
    ("privilege-escalation", "Privilege escalation threats",
     "Threats where an attacker gains higher privileges than authorized, performing actions reserved for "
     "administrators, accessing other users' resources, or bypassing access control boundaries.",
     ("security", "stride", "elevation-of-privilege", "access-control", "owasp", "cwe"), ("A01", "CWE-269")),
    ("agentic", "AI agent autonomy and misuse threats",
     "Threats arising from autonomous agent behavior, including uncontrolled tool use, excessive autonomy, "
     "agent-to-agent trust violations, and lack of human oversight in high-impact operations.",
     ("security", "ai", "agentic", "autonomy", "tool-use", "mcp"), ("CWE-693",)),
    ("llm", "LLM-specific threats",
     "Threats from prompt injection vulnerabilities, data poisoning risks, and model theft in LLM-integrated "
     "components, covering direct and indirect injection, RAG pipeline manipulation, and model extraction.",
     ("security", "ai", "llm", "prompt-injection", "data-poisoning", "model-theft"), ("CWE-74",)),
)

_CWE_TAXON = re.compile(r"CWE-[1-9][0-9]*")
_OWASP_TAXON = re.compile(r"A(?:0[1-9]|10)")


def taxonomy_name_for(taxon_id: str) -> str:
    """The ``toolComponent`` name of a rule's relationship to this taxonomy ID: ``CWE`` or ``OWASP``.

    The map is closed: ``CWE-<n>`` is ``CWE`` and ``A01`` to ``A10`` is ``OWASP``. Any other ID is a
    defect in shipped code and raises ``ValueError``. ``OWASP`` is the 1.0 files' name-only form, and
    no ``taxonomies`` entry carries it, so these links don't resolve inside the file; aligning them is
    a follow-up (T080).
    """
    if isinstance(taxon_id, str):
        if _CWE_TAXON.fullmatch(taxon_id):
            return "CWE"
        if _OWASP_TAXON.fullmatch(taxon_id):
            return "OWASP"
    raise ValueError(
        "not a taxonomy ID that a rule may relate to: %s; expected CWE-<n> or A01 to A10" % _short(taxon_id)
    )


def build_rules(highest: Mapping[str, Decimal]) -> List[Dict[str, Any]]:
    """The driver's ``rules``: one for each category in ``highest``, in ``RULES``' order.

    ``highest`` maps a category to the highest score among that category's results in the file: the
    composite in ``risk-scores.sarif``, the residual in ``compensating-controls.sarif``. That score is
    the rule's ``security-severity``, rounded half-up to one decimal and written as text. A category with
    no results has no rule, and a key that isn't one of the eight categories raises ``ValueError``.

    A rule is ``id``, ``shortDescription``, ``fullDescription``, ``properties`` (``tags``, then
    ``security-severity``) and ``relationships``, the keys and the order the 1.1 templates use. There is
    one ``relationships`` entry for each taxonomy ID in the rule's ``RULES`` row, in that row's order.
    Every list and object is new on each call.
    """
    unknown = [category for category in highest if category not in RULE_ID_BY_CATEGORY]
    if unknown:
        raise ValueError(
            "not a rule category: %s; expected some of %s"
            % (", ".join(_short(category) for category in unknown[:5]), list(RULE_ID_BY_CATEGORY))
        )
    return [
        {
            "id": RULE_ID_BY_CATEGORY[category],
            "shortDescription": {"text": short},
            "fullDescription": {"text": full},
            "properties": {"tags": list(tags), "security-severity": str(tachi_scoring.q1(highest[category]))},
            "relationships": [
                {"target": {"id": taxon_id, "toolComponent": {"name": taxonomy_name_for(taxon_id)}},
                 "kinds": ["relevant"]}
                for taxon_id in taxon_ids
            ],
        }
        for category, short, full, tags, taxon_ids in RULES
        if category in highest
    ]
