"""Isolated-operation session profile contract (feature 391, T017; AR-15 to AR-21).

``docs/guides/ISOLATED_OPERATION_TACHI.md`` ships the session profile as one fenced
JSON block between ``<!-- BEGIN TACHI SESSION PROFILE -->`` and ``<!-- END TACHI SESSION
PROFILE -->``. Adopters save it and start Claude Code with ``claude --settings <file>``,
so the block is the isolation guarantee: a key added to it, or a value flipped in it,
silently widens what a tachi session may do. This module pins the block to the contract
(``specs/391-isolated-auditable-operation/contracts/session-profile.md``, final at AR-15
to AR-20, amended at AR-21). The contract's key paths, values and lists are the constants
below, so the test does not depend on the spec workspace.

Inputs (read-only; nothing is written; no network):

- ``docs/guides/ISOLATED_OPERATION_TACHI.md``: the block, and the matrix-link line.
- ``docs/standards/CLAUDE_PERMISSIONS.md``: the section 8 heading the link anchors to.
- ``docs/product/02_PRD/391-isolated-auditable-operation-2026-11-16.md``: FR-6, the wording
  the ``hard_deny`` sentence and the audiences list are compared with.

What each group proves:

- extraction: exactly one BEGIN and one END marker, exactly one ``json`` fence between
  them, strict JSON (a duplicated key is refused, because ``json.loads`` would keep the
  last one and hide the first).
- closed key set: exactly the 19 contract key paths (objects only; array members are
  pinned by value), the seven scalars as shown, and the three security lists
  (``permissions.deny``, ``sandbox.credentials.files``, ``sandbox.credentials.envVars``)
  as order-free lists without duplicates.
- invariants: one allowed host and it is the Gemini host; every ``injectHosts`` entry is
  in ``allowedDomains``; ``"$defaults"`` is in every ``autoMode`` list; ``tlsTerminate`` is
  present whenever a ``mask`` entry exists; the ``hard_deny`` sentence and the audiences
  list are byte-exact against PRD FR-6; AR-15 (Read denies and the login-file entry),
  AR-16 (``autoAllowBashIfSandboxed`` is ``false``), AR-17 (``mcp__*`` denied) and AR-21
  (the eight built-in tools that reach past the sandbox are denied by bare name, each
  exactly as written: a scoped form or a different case does not count).
- named negatives (AR-19): 21 weakening or forbidden key paths are absent, whatever their
  value (the closed key set rejects every other path too).
- release-please marker, matrix link and anchor: the matrix-link line is the only
  ``x-release-please-version`` line and carries one version string; its URL targets
  ``CLAUDE_PERMISSIONS.md`` at ``#8-agent-and-command-privilege-matrix``; and that
  anchor is what GitHub generates from the section 8 heading (GitHub's slug rule is
  ported below, with its suffix for repeated headings).
- negative controls: every check is also run on in-memory mutated copies of its input (a
  flipped scalar, an injected key, one changed character, a moved marker) and must report
  each of them. A mutation that changes nothing, or a check that is already red on the
  unmutated input, fails the control instead of passing it, and a check without a control
  fails the registry test.

Stdlib and pytest only; Python 3.9 syntax; ASCII source (the two non-ASCII characters
the controls need are built with chr(), so no invisible character sits in the file).
"""

import copy
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Dict, FrozenSet, List, NamedTuple, Optional, Tuple
from urllib.parse import urlsplit

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = REPO_ROOT / "docs" / "guides" / "ISOLATED_OPERATION_TACHI.md"
PERMISSIONS = REPO_ROOT / "docs" / "standards" / "CLAUDE_PERMISSIONS.md"
PRD = REPO_ROOT / "docs" / "product" / "02_PRD" / "391-isolated-auditable-operation-2026-11-16.md"

BEGIN_MARKER = "<!-- BEGIN TACHI SESSION PROFILE -->"
END_MARKER = "<!-- END TACHI SESSION PROFILE -->"
VERSION_MARKER = "x-release-please-version"
VERSION_COMMENT = "<!-- x-release-please-version -->"

GEMINI_HOST = "generativelanguage.googleapis.com"
MATRIX_FRAGMENT = "8-agent-and-command-privilege-matrix"
MATRIX_HEADING = "8. Agent and command privilege matrix"

EM_DASH = chr(0x2014)
NO_BREAK_SPACE = chr(0xA0)

KeyPath = Tuple[str, ...]
Check = Callable[[Any], List[str]]
ProfileMutation = Callable[[Dict[str, Any]], None]
TextMutation = Callable[[str], str]


# =============================================================================
# The contract (contracts/session-profile.md, final at AR-15 to AR-20, amended at AR-21)
# =============================================================================

# 19 key paths. Objects only: the members of the three lists below are pinned by value.
EXPECTED_KEY_PATHS: FrozenSet[KeyPath] = frozenset(
    tuple(dotted.split("."))
    for dotted in (
        "env",
        "env.CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
        "permissions",
        "permissions.deny",
        "sandbox",
        "sandbox.enabled",
        "sandbox.failIfUnavailable",
        "sandbox.allowUnsandboxedCommands",
        "sandbox.autoAllowBashIfSandboxed",
        "sandbox.network",
        "sandbox.network.allowedDomains",
        "sandbox.network.strictAllowlist",
        "sandbox.network.tlsTerminate",
        "sandbox.credentials",
        "sandbox.credentials.envVars",
        "sandbox.credentials.files",
        "autoMode",
        "autoMode.environment",
        "autoMode.hard_deny",
    )
)

# The seven scalars, compared type-exactly (so 1 is not true and "true" is not true).
EXPECTED_SCALARS: Tuple[Tuple[str, Any], ...] = (
    ("env.CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC", "1"),
    ("sandbox.enabled", True),
    ("sandbox.failIfUnavailable", True),
    ("sandbox.allowUnsandboxedCommands", False),
    ("sandbox.autoAllowBashIfSandboxed", False),
    ("sandbox.network.strictAllowlist", True),
    ("sandbox.network.tlsTerminate", {}),
)

EXPECTED_DENY: Tuple[str, ...] = (
    "WebFetch",
    "WebSearch",
    "mcp__*",
    "ListMcpResourcesTool",
    "ReadMcpResourceTool",
    "ReadMcpResourceDirTool",
    "SendMessage",
    "ListAgents",
    "Monitor",
    "RemoteTrigger",
    "ShareOnboardingGuide",
    "Read(~/.ssh/**)",
    "Read(~/.aws/**)",
    "Read(~/.claude/.credentials.json)",
    "Read(//proc/**)",
    "Read(.env*)",
)
EXPECTED_CREDENTIAL_FILES: Tuple[Dict[str, Any], ...] = (
    {"path": "~/.ssh", "mode": "deny"},
    {"path": "~/.aws", "mode": "deny"},
    {"path": "~/.claude/.credentials.json", "mode": "deny"},
)
EXPECTED_ENV_VARS: Tuple[Dict[str, Any], ...] = (
    {"name": "GEMINI_API_KEY", "mode": "mask", "injectHosts": [GEMINI_HOST]},
)
EXPECTED_LISTS: Tuple[Tuple[str, Tuple[Any, ...]], ...] = (
    ("permissions.deny", EXPECTED_DENY),
    ("sandbox.credentials.files", EXPECTED_CREDENTIAL_FILES),
    ("sandbox.credentials.envVars", EXPECTED_ENV_VARS),
)

# AR-15: the SEC-A rules that joined the baseline.
AR15_READ_DENIES: Tuple[str, ...] = ("Read(//proc/**)", "Read(~/.claude/.credentials.json)")
AR15_CREDENTIAL_FILE: Dict[str, Any] = {"path": "~/.claude/.credentials.json", "mode": "deny"}

# AR-19: 21 key paths the profile must never carry: the keys that the sandboxing page lists
# as weakening or loosening the sandbox (including allowAppleEvents, the one gap in the
# page's own list of six), sandbox.credentials.allowPlaintextInject, and the profile's own
# forbidden permissions and autoMode keys.
NAMED_NEGATIVES: Tuple[str, ...] = (
    "sandbox.excludedCommands",
    "sandbox.ignoreViolations",
    "sandbox.allowNestedUserNamespaces",
    "sandbox.allowAppleEvents",
    "sandbox.enableWeakerNestedSandbox",
    "sandbox.enableWeakerNetworkIsolation",
    "sandbox.filesystem.allowWrite",
    "sandbox.filesystem.allowRead",
    "sandbox.filesystem.disabled",
    "sandbox.network.allowAllUnixSockets",
    "sandbox.network.allowUnixSockets",
    "sandbox.network.allowLocalBinding",
    "sandbox.network.allowMachLookup",
    "sandbox.network.httpProxyPort",
    "sandbox.network.socksProxyPort",
    "sandbox.credentials.allowPlaintextInject",
    "permissions.allow",
    "permissions.additionalDirectories",
    "permissions.defaultMode",
    "autoMode.allow",
    "autoMode.soft_deny",
)

# AR-21: the eight built-in tools whose paths reach past the sandbox, denied by bare name
# (a member list only: no key path was added). Each must be in permissions.deny exactly
# as written, so a scoped form such as Monitor(*) or a different case does not count.
AR21_TOOL_DENIES: Tuple[str, ...] = (
    "ListMcpResourcesTool",
    "ReadMcpResourceTool",
    "ReadMcpResourceDirTool",
    "SendMessage",
    "ListAgents",
    "Monitor",
    "RemoteTrigger",
    "ShareOnboardingGuide",
)

# The block's audiences entry (PM ruling, field-list.md section 10.3): its frame is
# pinned here and the list inside the parentheses is compared with PRD FR-6.
AUDIENCES_PREFIX = "Sensitive data locations & audiences:"
_AUDIENCES_ENTRY = re.compile(
    re.escape(AUDIENCES_PREFIX)
    + r" .+? Audiences: the security team; Google's Gemini API for the derived"
    + r" infographic prompt only \((.+)\)\.",
    re.S,
)
_PRD_HARD_DENY = re.compile(r'`hard_deny`, one tool-scoped prohibition: "([^"\n]+)"')
_PRD_AUDIENCES = re.compile(
    r"meaning the content D-3 lists: "
    r"(the project name and assessment date;.*?a one-line system description)\)"
)


# =============================================================================
# Reading the inputs
# =============================================================================


def _read(path: Path) -> str:
    if not path.is_file():
        pytest.fail(f"contract input missing: {path.relative_to(REPO_ROOT)}", pytrace=False)
    return path.read_text(encoding="utf-8")


def _reject_duplicate_keys(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    obj: Dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"duplicate key {key!r}")
        obj[key] = value
    return obj


def _reject_constant(name: str) -> Any:
    raise ValueError(f"non-standard JSON constant {name}")


def extract_block(runbook: str) -> Tuple[Optional[str], List[str]]:
    """The JSON text of the one ``json`` fence between the markers, with any problems."""
    problems = []
    for marker in (BEGIN_MARKER, END_MARKER):
        count = runbook.count(marker)
        if count != 1:
            problems.append(f"expected exactly one {marker}, found {count}")
    if problems:
        return None, problems
    start = runbook.index(BEGIN_MARKER) + len(BEGIN_MARKER)
    end = runbook.index(END_MARKER)
    if end < start:
        return None, ["the END marker comes before the BEGIN marker"]
    fenced = re.fullmatch(r"\s*```json\n(.*)\n```\s*", runbook[start:end], re.S)
    if fenced is None or "```" in fenced.group(1):
        return None, ["between the markers there must be exactly one json fence and nothing else"]
    return fenced.group(1), []


def parse_profile(block: str) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    try:
        data = json.loads(
            block, object_pairs_hook=_reject_duplicate_keys, parse_constant=_reject_constant
        )
    except ValueError as exc:
        return None, [f"the block is not strict JSON: {exc}"]
    if not isinstance(data, dict):
        return None, ["the block's top level must be a JSON object"]
    return data, []


def check_block(runbook: str) -> List[str]:
    block, problems = extract_block(runbook)
    return problems if block is None else parse_profile(block)[1]


# =============================================================================
# Profile checks: each takes the parsed profile and returns a list of violations
# =============================================================================


class _Absent:
    def __repr__(self) -> str:
        return "<absent>"


ABSENT = _Absent()


def _get(node: Any, dotted: str) -> Any:
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return ABSENT
        node = node[part]
    return node


def _same(actual: Any, expected: Any) -> bool:
    """Equality that keeps True apart from 1 (``True == 1`` in Python)."""
    return type(actual) is type(expected) and actual == expected


def _canonical(items: Any) -> Optional[List[str]]:
    """An order-free, duplicate-keeping form of a list: its members as sorted JSON."""
    if not isinstance(items, list):
        return None
    return sorted(json.dumps(item, sort_keys=True) for item in items)


def _first_difference(a: str, b: str) -> str:
    for index, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return f"character {index}: {x!r} (U+{ord(x):04X}) against {y!r} (U+{ord(y):04X})"
    return f"length {len(a)} against {len(b)}"


def key_paths(node: Any, prefix: KeyPath = ()) -> FrozenSet[KeyPath]:
    """Every object key path. Paths are tuples, so a key named "a.b" is not path a -> b."""
    found = set()
    if isinstance(node, dict):
        for key, value in node.items():
            path = prefix + (key,)
            found.add(path)
            found |= key_paths(value, path)
    return frozenset(found)


def check_closed_key_set(profile: Any) -> List[str]:
    actual = key_paths(profile)
    problems = []
    extra = sorted(".".join(path) for path in actual - EXPECTED_KEY_PATHS)
    missing = sorted(".".join(path) for path in EXPECTED_KEY_PATHS - actual)
    if extra:
        problems.append("key paths outside the contract: " + ", ".join(extra))
    if missing:
        problems.append("contract key paths missing: " + ", ".join(missing))
    return problems


def check_scalars(profile: Any) -> List[str]:
    problems = []
    for dotted, expected in EXPECTED_SCALARS:
        actual = _get(profile, dotted)
        if not _same(actual, expected):
            problems.append(f"{dotted}: expected {expected!r}, found {actual!r}")
    return problems


def check_member_lists(profile: Any) -> List[str]:
    problems = []
    for dotted, expected in EXPECTED_LISTS:
        actual = _get(profile, dotted)
        got, want = _canonical(actual), _canonical(list(expected))
        if got is None:
            problems.append(f"{dotted}: expected a list, found {actual!r}")
        elif got != want:
            unexpected = sorted((Counter(got) - Counter(want)).elements())
            missing = sorted((Counter(want) - Counter(got)).elements())
            problems.append(f"{dotted}: unexpected {unexpected}, missing {missing}")
    return problems


def check_one_host(profile: Any) -> List[str]:
    domains = _get(profile, "sandbox.network.allowedDomains")
    if not isinstance(domains, list):
        return [f"sandbox.network.allowedDomains must be a list, found {domains!r}"]
    if len(domains) != 1:
        return [f"allowedDomains must hold exactly one host, found {len(domains)}: {domains!r}"]
    if domains[0] != GEMINI_HOST:
        return [f"the one allowed host must be {GEMINI_HOST}, found {domains[0]!r}"]
    return []


def check_inject_hosts_subset(profile: Any) -> List[str]:
    entries = _get(profile, "sandbox.credentials.envVars")
    allowed = _get(profile, "sandbox.network.allowedDomains")
    if not isinstance(entries, list):
        return [f"sandbox.credentials.envVars must be a list, found {entries!r}"]
    allowed = allowed if isinstance(allowed, list) else []
    problems = []
    for index, entry in enumerate(entries):
        hosts = entry.get("injectHosts") if isinstance(entry, dict) else None
        if not isinstance(hosts, list):
            problems.append(f"envVars[{index}] has no injectHosts list")
            continue
        stray = [host for host in hosts if host not in allowed]
        if stray:
            problems.append(f"envVars[{index}].injectHosts not in allowedDomains: {stray!r}")
    return problems


def check_defaults_in_every_list(profile: Any) -> List[str]:
    auto = _get(profile, "autoMode")
    if not isinstance(auto, dict) or not auto:
        return [f"autoMode must be a non-empty object, found {auto!r}"]
    problems = []
    for key, value in auto.items():
        if not isinstance(value, list):
            problems.append(f'autoMode.{key} must be a list that keeps "$defaults"')
        elif "$defaults" not in value:
            problems.append(f'autoMode.{key} lacks "$defaults"')
    return problems


def check_tls_with_mask(profile: Any) -> List[str]:
    entries = _get(profile, "sandbox.credentials.envVars")
    masked = []
    if isinstance(entries, list):
        masked = [e.get("name") for e in entries if isinstance(e, dict) and e.get("mode") == "mask"]
    if masked and _get(profile, "sandbox.network.tlsTerminate") is ABSENT:
        return [f"mask entries {masked!r} need sandbox.network.tlsTerminate"]
    return []


def check_hard_deny(profile: Any, prd_sentence: str) -> List[str]:
    entries = _get(profile, "autoMode.hard_deny")
    if not isinstance(entries, list):
        return [f"autoMode.hard_deny must be a list, found {entries!r}"]
    prohibitions = [entry for entry in entries if entry != "$defaults"]
    if len(prohibitions) != 1 or not isinstance(prohibitions[0], str):
        return [f'hard_deny must hold "$defaults" and one sentence, found {entries!r}']
    if prohibitions[0].encode("utf-8") != prd_sentence.encode("utf-8"):
        return ["hard_deny differs from PRD FR-6 at " + _first_difference(prohibitions[0], prd_sentence)]
    return []


def check_audiences(profile: Any, prd_list: str) -> List[str]:
    entries = _get(profile, "autoMode.environment")
    if not isinstance(entries, list):
        return [f"autoMode.environment must be a list, found {entries!r}"]
    audiences = [e for e in entries if isinstance(e, str) and e.startswith(AUDIENCES_PREFIX)]
    if len(audiences) != 1:
        return [f"expected exactly one {AUDIENCES_PREFIX!r} entry, found {len(audiences)}"]
    framed = _AUDIENCES_ENTRY.fullmatch(audiences[0])
    if framed is None:
        return ["the audiences entry has lost the PM-ruled frame (field-list.md section 10.3)"]
    if framed.group(1).encode("utf-8") != prd_list.encode("utf-8"):
        return ["the audiences list differs from PRD FR-6 at " + _first_difference(framed.group(1), prd_list)]
    return []


def check_ar15(profile: Any) -> List[str]:
    deny = _get(profile, "permissions.deny")
    files = _get(profile, "sandbox.credentials.files")
    problems = [
        f"permissions.deny lacks {rule!r}"
        for rule in AR15_READ_DENIES
        if not isinstance(deny, list) or rule not in deny
    ]
    if not isinstance(files, list) or AR15_CREDENTIAL_FILE not in files:
        problems.append(f"sandbox.credentials.files lacks {AR15_CREDENTIAL_FILE!r}")
    return problems


def check_ar16(profile: Any) -> List[str]:
    value = _get(profile, "sandbox.autoAllowBashIfSandboxed")
    return [] if value is False else [f"autoAllowBashIfSandboxed must be false, found {value!r}"]


def check_ar17(profile: Any) -> List[str]:
    deny = _get(profile, "permissions.deny")
    if isinstance(deny, list) and "mcp__*" in deny:
        return []
    return ['permissions.deny must contain "mcp__*"']


def check_named_negatives(profile: Any) -> List[str]:
    return [
        f"{dotted}: forbidden key present"
        for dotted in NAMED_NEGATIVES
        if _get(profile, dotted) is not ABSENT
    ]


def check_ar21(profile: Any) -> List[str]:
    deny = _get(profile, "permissions.deny")
    return [
        f"permissions.deny lacks {name!r}"
        for name in AR21_TOOL_DENIES
        if not isinstance(deny, list) or name not in deny
    ]


# =============================================================================
# PRD FR-6 sources
# =============================================================================


def _single(pattern: "re.Pattern[str]", prd: str, what: str) -> Tuple[Optional[str], List[str]]:
    found = pattern.findall(prd)
    if len(found) != 1:
        return None, [f"PRD FR-6: expected exactly one {what}, found {len(found)}"]
    if len(found[0]) < 100:
        return None, [f"PRD FR-6: the {what} looks truncated ({len(found[0])} characters)"]
    return found[0], []


def prd_hard_deny(prd: str) -> Tuple[Optional[str], List[str]]:
    return _single(_PRD_HARD_DENY, prd, "hard_deny sentence")


def prd_audiences(prd: str) -> Tuple[Optional[str], List[str]]:
    return _single(_PRD_AUDIENCES, prd, "audiences list")


def check_prd_sources(prd: str) -> List[str]:
    return prd_hard_deny(prd)[1] + prd_audiences(prd)[1]


PROFILE_CHECK_IDS = (
    "closed_key_set",
    "scalar_values",
    "member_lists",
    "one_host",
    "inject_hosts_subset",
    "defaults_in_every_list",
    "tls_with_mask",
    "hard_deny_byte_exact",
    "audiences_match_prd",
    "ar15_read_denies",
    "ar16_classifier_coverage",
    "ar17_mcp_denied",
    "named_negatives_absent",
    "ar21_tool_denies",
)


def profile_checks(prd_sentence: str, prd_list: str) -> Dict[str, Check]:
    return {
        "closed_key_set": check_closed_key_set,
        "scalar_values": check_scalars,
        "member_lists": check_member_lists,
        "one_host": check_one_host,
        "inject_hosts_subset": check_inject_hosts_subset,
        "defaults_in_every_list": check_defaults_in_every_list,
        "tls_with_mask": check_tls_with_mask,
        "hard_deny_byte_exact": lambda profile: check_hard_deny(profile, prd_sentence),
        "audiences_match_prd": lambda profile: check_audiences(profile, prd_list),
        "ar15_read_denies": check_ar15,
        "ar16_classifier_coverage": check_ar16,
        "ar17_mcp_denied": check_ar17,
        "named_negatives_absent": check_named_negatives,
        "ar21_tool_denies": check_ar21,
    }


# =============================================================================
# Text checks: the release-please marker, the matrix link and GitHub's anchor rule
# =============================================================================

# Release-please's generic updater changes the first semver-looking string on a line that
# carries the marker (w3-sweeps.md, "Marker rule for the runbook line").
_VERSION_STRING = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
_MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_MATRIX_URL_PATH = re.compile(
    r"/[^/]+/[^/]+/blob/v[0-9]+\.[0-9]+\.[0-9]+/docs/standards/CLAUDE_PERMISSIONS\.md"
)
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_ATX_HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")


def _marker_lines(runbook: str) -> List[str]:
    return [line for line in runbook.split("\n") if VERSION_MARKER in line]


def check_marker_line(runbook: str) -> List[str]:
    lines = _marker_lines(runbook)
    if len(lines) != 1:
        return [f"expected exactly one line with {VERSION_MARKER}, found {len(lines)}"]
    line = lines[0]
    problems = []
    if runbook.count(VERSION_MARKER) != 1:
        problems.append(f"{VERSION_MARKER} occurs more than once on its line")
    if line.count(VERSION_COMMENT) != 1:
        problems.append(f"the marker must be the HTML comment {VERSION_COMMENT}")
    versions = _VERSION_STRING.findall(line)
    if len(versions) != 1:
        problems.append(f"the marker line must carry exactly one version string, found {versions!r}")
    return problems


def check_matrix_link(runbook: str) -> List[str]:
    lines = _marker_lines(runbook)
    if len(lines) != 1:
        return [f"no single marker line to hold the matrix link (found {len(lines)})"]
    urls = _MARKDOWN_LINK.findall(lines[0])
    if len(urls) != 1:
        return [f"the marker line must hold exactly one Markdown link, found {len(urls)}"]
    parts = urlsplit(urls[0])
    problems = []
    if (parts.scheme, parts.netloc) != ("https", "github.com"):
        problems.append(f"the matrix link must be an https://github.com URL, found {urls[0]!r}")
    if not _MATRIX_URL_PATH.fullmatch(parts.path):
        problems.append(
            "the link path must be /<owner>/<repo>/blob/v<semver>/docs/standards/"
            f"CLAUDE_PERMISSIONS.md, found {parts.path!r}"
        )
    if parts.fragment != MATRIX_FRAGMENT:
        problems.append(f"the link fragment must be #{MATRIX_FRAGMENT}, found #{parts.fragment}")
    return problems


def atx_headings(text: str) -> List[Tuple[int, str]]:
    """ATX headings outside fenced code blocks, as (level, text)."""
    headings = []
    fence = None
    for line in text.split("\n"):
        opened = _FENCE.match(line)
        if opened:
            mark, rest = opened.group(1), opened.group(2)
            if fence is None:
                fence = mark
            elif mark[0] == fence[0] and len(mark) >= len(fence) and not rest.strip():
                fence = None
            continue
        heading = _ATX_HEADING.match(line) if fence is None else None
        if heading:
            headings.append((len(heading.group(1)), heading.group(2)))
    return headings


def github_slug(heading: str) -> str:
    """GitHub's anchor for one heading: keep the text of inline links, lowercase, drop
    everything except word characters, hyphens and spaces, then turn each space into a
    hyphen. Other inline markup is not interpreted; the section 8 heading has none."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading).lower()
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def github_slugs(headings: List[str]) -> List[str]:
    """Anchors for a document's headings in order; a repeat gets -1, -2, ... (github-slugger)."""
    occurrences: Dict[str, int] = {}
    slugs = []
    for heading in headings:
        base = github_slug(heading)
        slug = base
        while slug in occurrences:
            occurrences[base] += 1
            slug = f"{base}-{occurrences[base]}"
        occurrences[slug] = 0
        slugs.append(slug)
    return slugs


def check_section8_slug(permissions: str, fragment: str = MATRIX_FRAGMENT) -> List[str]:
    headings = atx_headings(permissions)
    hits = [
        index
        for index, (level, text) in enumerate(headings)
        if level == 2 and re.match(r"8\.(\s|$)", text)
    ]
    if len(hits) != 1:
        return [f"expected exactly one level-2 section 8 heading outside code fences, found {len(hits)}"]
    slug = github_slugs([text for _, text in headings])[hits[0]]
    if slug != fragment:
        return [f"GitHub generates #{slug} from '## {headings[hits[0]][1]}', but the runbook links #{fragment}"]
    return []


TEXT_CHECKS: Dict[str, Tuple[str, Callable[[str], List[str]]]] = {
    "block_extraction": ("runbook", check_block),
    "marker_line": ("runbook", check_marker_line),
    "matrix_link": ("runbook", check_matrix_link),
    "section8_slug": ("permissions", check_section8_slug),
    "prd_sources": ("prd", check_prd_sources),
}


# =============================================================================
# Negative controls
# =============================================================================


class ProfileControl(NamedTuple):
    check: str
    name: str
    mutate: ProfileMutation


class TextControl(NamedTuple):
    check: str
    name: str
    mutate: TextMutation


def _parent(profile: Dict[str, Any], dotted: str) -> Tuple[Dict[str, Any], str]:
    parts = dotted.split(".")
    node = profile
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    return node, parts[-1]


def put(dotted: str, value: Any) -> ProfileMutation:
    def mutate(profile: Dict[str, Any]) -> None:
        node, key = _parent(profile, dotted)
        node[key] = value

    return mutate


def drop(dotted: str) -> ProfileMutation:
    def mutate(profile: Dict[str, Any]) -> None:
        node, key = _parent(profile, dotted)
        del node[key]

    return mutate


def append(dotted: str, item: Any) -> ProfileMutation:
    return lambda profile: _get(profile, dotted).append(item)


def remove(dotted: str, item: Any) -> ProfileMutation:
    return lambda profile: _get(profile, dotted).remove(item)


def replace(dotted: str, old: Any, new: Any) -> ProfileMutation:
    def mutate(profile: Dict[str, Any]) -> None:
        members = _get(profile, dotted)
        members[members.index(old)] = new

    return mutate


def edit_member(dotted: str, index: int, edit: Callable[[str], str]) -> ProfileMutation:
    def mutate(profile: Dict[str, Any]) -> None:
        members = _get(profile, dotted)
        members[index] = edit(members[index])

    return mutate


def edit_audiences(edit: Callable[[str], str]) -> ProfileMutation:
    def mutate(profile: Dict[str, Any]) -> None:
        members = profile["autoMode"]["environment"]
        index = next(i for i, entry in enumerate(members) if entry.startswith(AUDIENCES_PREFIX))
        members[index] = edit(members[index])

    return mutate


def _env_var(**changes: Any) -> Dict[str, Any]:
    entry = copy.deepcopy(EXPECTED_ENV_VARS[0])
    entry.update(changes)
    return entry


def _first_env_var(profile: Dict[str, Any]) -> Dict[str, Any]:
    return profile["sandbox"]["credentials"]["envVars"][0]


_ENV_VARS = "sandbox.credentials.envVars"
_FILES = "sandbox.credentials.files"
_DENY = "permissions.deny"
_DOMAINS = "sandbox.network.allowedDomains"
_TRAFFIC = "env.CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"
_HARD_DENY = "autoMode.hard_deny"
_ENVIRONMENT = "autoMode.environment"
_AUTO_ALLOW_BASH = "sandbox.autoAllowBashIfSandboxed"
_PROC_DENY, _LOGIN_DENY = AR15_READ_DENIES
_AUDIENCES_CLAUSE = "; and, if a template cannot be loaded, a one-line system description"

# AR-19: each named key, injected with an arbitrary value, is reported by name and by the
# closed key set.
_INJECTIONS = tuple(("inject-" + dotted, put(dotted, True)) for dotted in NAMED_NEGATIVES)

# AR-21: each of the eight tool names, taken out of permissions.deny, is reported by name.
_TOOL_REMOVALS = tuple((name + "-deny-removed", remove(_DENY, name)) for name in AR21_TOOL_DENIES)

ProfileRows = Tuple[Tuple[str, ProfileMutation], ...]
PROFILE_GROUPS: Dict[str, ProfileRows] = {
    "closed_key_set": (
        ("extra-top-level-key", put("hooks", {})),
        ("extra-nested-key", put("sandbox.network.proxy", "x")),
        ("key-dropped", drop("sandbox.network.strictAllowlist")),
        (
            "key-renamed",
            lambda p: p["autoMode"].update(hardDeny=p["autoMode"].pop("hard_deny")),
        ),
        ("dotted-key-spoof", lambda p: p.update({"sandbox.enabled": True})),
    )
    + _INJECTIONS,
    "scalar_values": (
        ("sandbox-disabled", put("sandbox.enabled", False)),
        ("sandbox-optional", put("sandbox.failIfUnavailable", False)),
        ("unsandboxed-allowed", put("sandbox.allowUnsandboxedCommands", True)),
        ("classifier-bypass-on", put(_AUTO_ALLOW_BASH, True)),
        ("allowlist-not-strict", put("sandbox.network.strictAllowlist", False)),
        ("tls-terminate-configured", put("sandbox.network.tlsTerminate", {"mask": True})),
        ("traffic-flag-zero", put(_TRAFFIC, "0")),
        ("traffic-flag-int", put(_TRAFFIC, 1)),
        ("bool-as-string", put("sandbox.enabled", "true")),
        ("bool-as-int", put("sandbox.enabled", 1)),
        ("scalar-removed", drop("sandbox.failIfUnavailable")),
    ),
    "member_lists": (
        ("deny-rule-added", append(_DENY, "Read(~/**)")),
        ("deny-rule-removed", remove(_DENY, "WebSearch")),
        ("deny-rule-narrowed", replace(_DENY, "Read(.env*)", "Read(.env)")),
        ("deny-rule-duplicated", append(_DENY, "WebFetch")),
        ("deny-not-a-list", put(_DENY, "WebFetch")),
        ("credential-file-removed", remove(_FILES, {"path": "~/.aws", "mode": "deny"})),
        (
            "credential-file-mode-changed",
            replace(_FILES, {"path": "~/.ssh", "mode": "deny"}, {"path": "~/.ssh", "mode": "mask"}),
        ),
        ("credential-file-added", append(_FILES, {"path": "~/.kube", "mode": "deny"})),
        ("env-var-mode-changed", put(_ENV_VARS, [_env_var(mode="passthrough")])),
        ("env-var-added", append(_ENV_VARS, _env_var(name="ANTHROPIC_API_KEY"))),
        ("env-var-gains-a-key", lambda p: _first_env_var(p).update(allowPlaintextInject=True)),
    ),
    "one_host": (
        ("second-host-allowed", append(_DOMAINS, "example.com")),
        ("wildcard-host", put(_DOMAINS, ["*.googleapis.com"])),
        ("other-single-host", put(_DOMAINS, ["example.com"])),
        ("allowlist-empty", put(_DOMAINS, [])),
        ("allowlist-is-a-string", put(_DOMAINS, GEMINI_HOST)),
    ),
    "inject_hosts_subset": (
        ("inject-host-outside-allowlist", lambda p: _first_env_var(p)["injectHosts"].append("example.com")),
        ("inject-hosts-missing", lambda p: _first_env_var(p).pop("injectHosts")),
        ("allowlist-without-the-inject-host", put(_DOMAINS, [])),
    ),
    "defaults_in_every_list": (
        ("environment-without-defaults", remove(_ENVIRONMENT, "$defaults")),
        ("hard-deny-without-defaults", remove(_HARD_DENY, "$defaults")),
        ("defaults-misspelled", replace(_HARD_DENY, "$defaults", "$default")),
        ("extra-list-without-defaults", put("autoMode.allow", ["Bash(*)"])),
        ("environment-not-a-list", put(_ENVIRONMENT, "text")),
    ),
    "tls_with_mask": (
        ("tls-terminate-removed-while-masking", drop("sandbox.network.tlsTerminate")),
    ),
    "hard_deny_byte_exact": (
        ("case-changed", edit_member(_HARD_DENY, 1, lambda s: s.replace("Never", "never", 1))),
        ("trailing-space", edit_member(_HARD_DENY, 1, lambda s: s + " ")),
        ("no-break-space", edit_member(_HARD_DENY, 1, lambda s: s.replace(" ", NO_BREAK_SPACE, 1))),
        ("second-sentence-cut", edit_member(_HARD_DENY, 1, lambda s: s.split(" Requests to that host")[0])),
        ("host-swapped", edit_member(_HARD_DENY, 1, lambda s: s.replace(GEMINI_HOST, "example.com", 1))),
        ("second-prohibition", append(_HARD_DENY, "Also block uploads.")),
        ("only-defaults", put(_HARD_DENY, ["$defaults"])),
        ("not-a-string", put(_HARD_DENY, ["$defaults", 5])),
    ),
    "audiences_match_prd": (
        ("clause-dropped", edit_audiences(lambda s: s.replace(_AUDIENCES_CLAUSE, "", 1))),
        (
            "word-changed",
            edit_audiences(lambda s: s.replace("finding IDs, descriptions", "finding IDs, one-line descriptions", 1)),
        ),
        ("frame-changed", edit_audiences(lambda s: s.replace("Google's Gemini API", "any provider", 1))),
        (
            "entry-removed",
            lambda p: p["autoMode"].update(
                environment=[e for e in p["autoMode"]["environment"] if not e.startswith(AUDIENCES_PREFIX)]
            ),
        ),
        (
            "entry-duplicated",
            lambda p: p["autoMode"]["environment"].append(
                next(e for e in p["autoMode"]["environment"] if e.startswith(AUDIENCES_PREFIX))
            ),
        ),
    ),
    "ar15_read_denies": (
        ("proc-deny-removed", remove(_DENY, _PROC_DENY)),
        # a rule path that starts with a single slash anchors at the profile's directory
        ("proc-deny-single-slash", replace(_DENY, _PROC_DENY, _PROC_DENY.replace("//", "/", 1))),
        ("login-file-deny-removed", remove(_DENY, _LOGIN_DENY)),
        ("login-file-entry-removed", remove(_FILES, AR15_CREDENTIAL_FILE)),
    ),
    "ar16_classifier_coverage": (
        ("classifier-bypass-on", put(_AUTO_ALLOW_BASH, True)),
        ("flag-removed", drop(_AUTO_ALLOW_BASH)),
        ("flag-as-string", put(_AUTO_ALLOW_BASH, "false")),
    ),
    "ar17_mcp_denied": (
        ("mcp-deny-removed", remove(_DENY, "mcp__*")),
        ("mcp-deny-narrowed", replace(_DENY, "mcp__*", "mcp__github__*")),
    ),
    "named_negatives_absent": _INJECTIONS,
    "ar21_tool_denies": _TOOL_REMOVALS
    + (
        # a scoped form is not the bare name the contract pins
        ("Monitor-deny-scoped", replace(_DENY, "Monitor", "Monitor(*)")),
        # the check compares exactly, so a different case is not the pinned name
        ("SendMessage-deny-case-changed", replace(_DENY, "SendMessage", "sendMessage")),
    ),
}
PROFILE_CONTROLS: Tuple[ProfileControl, ...] = tuple(
    ProfileControl(check, name, mutate)
    for check, rows in PROFILE_GROUPS.items()
    for name, mutate in rows
)


def _replace_once(old: str, new: str) -> TextMutation:
    return lambda text: text.replace(old, new, 1)


def _edit_block(edit: TextMutation) -> TextMutation:
    """Apply an edit to the runbook's JSON block only."""

    def mutate(text: str) -> str:
        block = extract_block(text)[0]
        assert block is not None
        return text.replace(block, edit(block), 1)

    return mutate


def _edit_marker_line(edit: TextMutation) -> TextMutation:
    """Apply an edit to the runbook's x-release-please-version line only."""

    def mutate(text: str) -> str:
        line = _marker_lines(text)[0]
        return text.replace(line, edit(line), 1)

    return mutate


def _swap_markers(text: str) -> str:
    placeholder = "<<marker-swap-placeholder>>"
    swapped = text.replace(BEGIN_MARKER, placeholder, 1).replace(END_MARKER, BEGIN_MARKER, 1)
    return swapped.replace(placeholder, END_MARKER, 1)


def _branch_instead_of_release(line: str) -> str:
    return re.sub(r"/blob/v[0-9.]+/", "/blob/main/", line)


_SECTION8_LINE = "## " + MATRIX_HEADING

TextRows = Tuple[Tuple[str, TextMutation], ...]
TEXT_GROUPS: Dict[str, TextRows] = {
    "block_extraction": (
        ("begin-marker-twice", _replace_once(END_MARKER, BEGIN_MARKER + "\n" + END_MARKER)),
        ("end-marker-twice", _replace_once(END_MARKER, END_MARKER + "\n" + END_MARKER)),
        ("end-marker-missing", _replace_once(END_MARKER, "")),
        ("markers-swapped", _swap_markers),
        ("second-fence-between-markers", _replace_once(END_MARKER, "```json\n{}\n```\n" + END_MARKER)),
        ("fence-language-changed", _replace_once("```json", "```jsonc")),
        ("prose-between-markers", _replace_once(BEGIN_MARKER, BEGIN_MARKER + "\nstray prose")),
        ("json-syntax-error", _edit_block(_replace_once('"enabled": true,', '"enabled": true,,'))),
        (
            "json-duplicate-key",
            _edit_block(_replace_once('"enabled": true,', '"enabled": true, "enabled": false,')),
        ),
        ("json-not-an-object", _edit_block(lambda block: "[" + block + "]")),
    ),
    "marker_line": (
        ("marker-comment-removed", _replace_once(VERSION_COMMENT, "")),
        ("second-marker-line", lambda text: text + "\n" + VERSION_COMMENT + "\n"),
        ("marker-twice-on-its-line", _replace_once(VERSION_COMMENT, VERSION_COMMENT + " " + VERSION_COMMENT)),
        ("marker-as-bare-text", _replace_once(VERSION_COMMENT, VERSION_MARKER)),
        (
            "second-version-on-the-line",
            _edit_marker_line(_replace_once(VERSION_COMMENT, "(needs v2.1.285) " + VERSION_COMMENT)),
        ),
        ("no-version-on-the-line", _edit_marker_line(_branch_instead_of_release)),
    ),
    "matrix_link": (
        (
            "fragment-without-the-number",
            _edit_marker_line(_replace_once("#" + MATRIX_FRAGMENT, "#agent-and-command-privilege-matrix")),
        ),
        (
            "fragment-with-a-double-hyphen",
            _edit_marker_line(_replace_once("#8-agent-and", "#8-agent--and")),
        ),
        ("wrong-file", _edit_marker_line(_replace_once("CLAUDE_PERMISSIONS.md#", "CLAUDE_PERMISSION.md#"))),
        ("branch-instead-of-release", _edit_marker_line(_branch_instead_of_release)),
        ("plain-http", _edit_marker_line(_replace_once("https://", "http://"))),
        ("other-host", _edit_marker_line(_replace_once("https://github.com/", "https://example.com/"))),
        (
            "second-link-on-the-line",
            _edit_marker_line(_replace_once(VERSION_COMMENT, "[x](https://example.com) " + VERSION_COMMENT)),
        ),
    ),
    "section8_slug": (
        (
            "em-dash-in-the-heading",
            _replace_once(_SECTION8_LINE, "## 8. Agent and command " + EM_DASH + " privilege matrix"),
        ),
        ("heading-renamed", _replace_once(_SECTION8_LINE, "## 8. Privilege matrix")),
        (
            "earlier-heading-with-the-same-slug",
            lambda text: "### 8 Agent and command privilege matrix\n\n" + text,
        ),
        (
            "heading-only-inside-a-code-fence",
            _replace_once(_SECTION8_LINE, MATRIX_HEADING + "\n\n```\n" + _SECTION8_LINE + "\n```"),
        ),
        ("heading-without-a-space", _replace_once(_SECTION8_LINE, "##" + MATRIX_HEADING)),
    ),
    "prd_sources": (
        (
            "hard-deny-sentence-twice",
            lambda text: text + '\n- `hard_deny`, one tool-scoped prohibition: "Another sentence."\n',
        ),
        (
            "hard-deny-quote-dropped",
            _replace_once('one tool-scoped prohibition: "', "one tool-scoped prohibition: "),
        ),
        (
            "audiences-lead-in-reworded",
            _replace_once("meaning the content D-3 lists:", "meaning the D-3 content:"),
        ),
    ),
}
TEXT_CONTROLS: Tuple[TextControl, ...] = tuple(
    TextControl(check, name, mutate)
    for check, rows in TEXT_GROUPS.items()
    for name, mutate in rows
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def texts() -> Dict[str, str]:
    return {"runbook": _read(RUNBOOK), "permissions": _read(PERMISSIONS), "prd": _read(PRD)}


@pytest.fixture(scope="module")
def profile(texts: Dict[str, str]) -> Dict[str, Any]:
    block, problems = extract_block(texts["runbook"])
    data = None
    if block is not None:
        data, problems = parse_profile(block)
    if data is None:
        pytest.fail("the session profile block cannot be used: " + "; ".join(problems), pytrace=False)
    return data


@pytest.fixture(scope="module")
def checks(texts: Dict[str, str]) -> Dict[str, Check]:
    sentence, problems = prd_hard_deny(texts["prd"])
    audiences, more = prd_audiences(texts["prd"])
    if sentence is None or audiences is None:
        pytest.fail("PRD FR-6 cannot be used: " + "; ".join(problems + more), pytrace=False)
    return profile_checks(sentence, audiences)


def _control_id(control: Any) -> str:
    return f"{control.check}:{control.name}"


def _fingerprint(profile: Dict[str, Any]) -> str:
    """A type-exact form of a profile (JSON keeps true apart from 1; == does not)."""
    return json.dumps(profile, sort_keys=True)


# =============================================================================
# The contract itself
# =============================================================================


def test_contract_constants_match_the_contract_counts() -> None:
    assert len(EXPECTED_KEY_PATHS) == 19
    assert len(EXPECTED_SCALARS) == 7
    assert [len(members) for _, members in EXPECTED_LISTS] == [16, 3, 1]
    assert len(AR21_TOOL_DENIES) == 8 == len(set(AR21_TOOL_DENIES))
    assert set(AR21_TOOL_DENIES) <= set(EXPECTED_DENY), "an AR-21 tool is not in the deny list"
    assert len(NAMED_NEGATIVES) == 21 == len(set(NAMED_NEGATIVES))
    allowed = {".".join(path) for path in EXPECTED_KEY_PATHS}
    assert not allowed & set(NAMED_NEGATIVES), "a named negative is also an allowed key path"
    assert {dotted.split(".")[0] for dotted in NAMED_NEGATIVES} <= {"sandbox", "permissions", "autoMode"}


# --- extraction ---------------------------------------------------------------


def test_exactly_one_begin_and_one_end_marker(texts: Dict[str, str]) -> None:
    assert texts["runbook"].count(BEGIN_MARKER) == 1
    assert texts["runbook"].count(END_MARKER) == 1


def test_markers_enclose_one_json_fence_of_strict_json(texts: Dict[str, str]) -> None:
    assert check_block(texts["runbook"]) == []


# --- the closed key set, the values and the invariants ------------------------


@pytest.mark.parametrize("check_id", PROFILE_CHECK_IDS)
def test_profile_satisfies_the_contract(
    check_id: str, checks: Dict[str, Check], profile: Dict[str, Any]
) -> None:
    problems = checks[check_id](profile)
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("dotted", NAMED_NEGATIVES)
def test_named_negative_key_is_absent(dotted: str, profile: Dict[str, Any]) -> None:
    assert _get(profile, dotted) is ABSENT, f"{dotted} must not appear in the session profile (AR-19)"


def test_prd_fr6_sources_are_unambiguous(texts: Dict[str, str]) -> None:
    assert check_prd_sources(texts["prd"]) == []


# --- the release-please marker, the matrix link and GitHub's anchor rule ------


def test_matrix_link_line_is_the_only_release_please_marker_and_has_one_version(
    texts: Dict[str, str],
) -> None:
    assert check_marker_line(texts["runbook"]) == []


def test_matrix_link_points_at_section_8_of_the_permissions_standard(texts: Dict[str, str]) -> None:
    assert check_matrix_link(texts["runbook"]) == []


def test_the_link_anchor_is_what_github_generates_from_the_section_8_heading(
    texts: Dict[str, str],
) -> None:
    assert check_section8_slug(texts["permissions"]) == []


# Headings and the anchors GitHub gives them. The punctuation and double-hyphen cases are
# anchors this repository's own documents link to (DEVELOPER_GUIDE_TACHI.md, the taxonomy
# README, the case-study template, the define skill). The em dash follows the same rule,
# which is why the section 8 heading carries none.
SLUG_VECTORS = (
    ("8. Agent and command privilege matrix", "8-agent-and-command-privilege-matrix"),
    ("Section 9 -- Running `/tachi.risk-score`", "section-9----running-tachirisk-score"),
    ("Full Template (Infrastructure / `--full`)", "full-template-infrastructure----full"),
    ("Consent & publication", "consent--publication"),
    ("4.1 `related` / `superseded` calibration", "41-related--superseded-calibration"),
    ("8. Agent and command " + EM_DASH + " privilege matrix", "8-agent-and-command--privilege-matrix"),
    ("[Linked](https://example.com) heading, with: punctuation!", "linked-heading-with-punctuation"),
    ("snake_case stays", "snake_case-stays"),
)


@pytest.mark.parametrize("heading,anchor", SLUG_VECTORS, ids=[anchor for _, anchor in SLUG_VECTORS])
def test_github_slug_rule(heading: str, anchor: str) -> None:
    assert github_slug(heading) == anchor


def test_github_slugs_number_repeated_headings() -> None:
    assert github_slugs(["Foo", "Bar", "Foo", "Foo"]) == ["foo", "bar", "foo-1", "foo-2"]


# =============================================================================
# Negative controls: each check goes red on a mutated copy of its input
# =============================================================================


@pytest.mark.parametrize("control", PROFILE_CONTROLS, ids=_control_id)
def test_profile_check_goes_red_on_a_mutated_copy(
    control: ProfileControl, checks: Dict[str, Check], profile: Dict[str, Any]
) -> None:
    check = checks[control.check]
    assert check(profile) == [], "the control starts from a profile that passes the check"
    mutated = copy.deepcopy(profile)
    control.mutate(mutated)
    assert _fingerprint(mutated) != _fingerprint(profile), "the mutation changed nothing"
    assert check(mutated), f"{control.check} did not notice the mutation {control.name}"


@pytest.mark.parametrize("control", TEXT_CONTROLS, ids=_control_id)
def test_text_check_goes_red_on_a_mutated_copy(control: TextControl, texts: Dict[str, str]) -> None:
    source, check = TEXT_CHECKS[control.check]
    assert check(texts[source]) == [], "the control starts from a document that passes the check"
    mutated = control.mutate(texts[source])
    assert mutated != texts[source], "the mutation changed nothing"
    assert check(mutated), f"{control.check} did not notice the mutation {control.name}"


def test_every_check_has_a_negative_control(checks: Dict[str, Check]) -> None:
    assert set(checks) == set(PROFILE_CHECK_IDS)
    assert {control.check for control in PROFILE_CONTROLS} == set(PROFILE_CHECK_IDS)
    assert {control.check for control in TEXT_CONTROLS} == set(TEXT_CHECKS)
    names = [_control_id(control) for control in PROFILE_CONTROLS + TEXT_CONTROLS]
    assert len(names) == len(set(names)), "control names must be unique"
