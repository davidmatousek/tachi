"""Tests for ``scripts/tachi_parts.py``, written first (F-374 T011; ADR-050 D3 and D16).

``tachi_parts`` is the one place that decides what an agent-written file may contain
(NFR-10). This module is D16's hostile-input matrix for it. It is a helper, so the tests
import it; there is no entry to drive. Every fixture is synthetic.

The module is written in slices. The cases in sections 1 to 3 (identifiers, canonical IDs
and S-2's order, D7's path rule, module hygiene) belong to T012's identifier slice. The rest
reach the later slices through ``_api()``, which fails a case with a clear message while the
name is not written yet, so those cases are red until T012's second slice and T013 land.

Sections
--------
1. Identifier allow-lists (ASCII full match; Unicode digits, trailing newline)
2. Canonical finding IDs and S-2's order
3. D7's syntactic path rule (evidence ``file`` values)
4. Module hygiene (C1, Python 3.9 floor, bytecode guard)
5. Strict loader: the file and the JSON text (steps 1 to 4)
6. Envelope: schema first, closed keys, overflow (steps 5 to 8)
7. IDs: batch membership, duplicates, spellings (step 8)
8. Strings: control, bidi and separator characters (step 10)
9. Scorer and controls payloads (steps 6 and 9, RR2's cut-and-flag)
10. Narrative fields: slots, numeral ban, per-field fallback (step 11)
11. Evidence fields and ``file`` values
12. Per-sink escaping
13. Guards, atomic write, digest, stamp and VERSION
"""
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import tachi_parts  # noqa: E402  -- after the sys.path mutation


def _api(name: str):
    """The ``tachi_parts`` name, or a clear failure while a later slice has not written it."""
    if not hasattr(tachi_parts, name):
        pytest.fail("tachi_parts.%s is not written yet (T012 second slice or T013)" % name, pytrace=False)
    return getattr(tachi_parts, name)


# =============================================================================
# 1. Identifier allow-lists
# =============================================================================

# The contracts' own spelling of each pattern (contracts/part-files.md and
# contracts/threat-model-records.md). A change here is a contract change.
CONTRACT_PATTERNS = {
    "finding": "(S|T|R|I|D|E|AG|AGP|LLM|OI|MI|TE)-[0-9]{1,6}",
    "plan": "[0-9]{8}T[0-9]{6}Z-[0-9a-f]{12}",
    "batch": "B[0-9]{3}(-[12]){0,2}",
    "dispatch": "dsp-[0-9]{3,4}",
    "group": "CG-[0-9]{1,6}",
    "chain": "CHAIN-[0-9]{3,6}",
    "language": "[a-z0-9+#-]{1,20}",
}

VALID_IDS = {
    "finding": ["S-1", "T-10", "R-7", "I-3", "D-2", "E-9", "AG-1", "AGP-12", "LLM-1", "OI-3",
                "MI-9", "TE-2", "E-999999", "AGP-01", "S-0", "S-000001"],
    "plan": ["20261122T101500Z-0123456789ab", "20000101T000000Z-ffffffffffff"],
    "batch": ["B001", "B999", "B003-1", "B003-2", "B003-1-2", "B003-2-1"],
    "dispatch": ["dsp-001", "dsp-0001", "dsp-1234"],
    "group": ["CG-1", "CG-12", "CG-123456"],
    "chain": ["CHAIN-001", "CHAIN-0001", "CHAIN-123456"],
    "language": ["python", "c++", "c#", "objective-c", "x86-64", "a", "a" * 20],
}

INVALID_IDS = {
    "finding": ["", "S-", "S-1234567", "s-1", "X-1", "S1", "-1", "SS-1", "AGPX-1", "LLM01-1", "S--1",
                "S-+1", "S-1 ", " S-1", "S-1\n", "S-1\r", "S-\u0661", "S-\uff11", "S-\u0966",
                "S\u2010 1", "S\u2011\u0031", "AGP-\u0661\u0662", "\u0053-1\u200b"],
    "plan": ["", "20261122T101500Z-0123456789AB", "20261122T101500Z-0123456789a", "20261122T101500Z-0123456789abc",
             "20261122T101500Z-0123456789ab\n", "20261122 101500Z-0123456789ab", "2026112T101500Z-0123456789ab",
             "\u0662\u0660261122T101500Z-0123456789ab", "20261122T101500-0123456789ab"],
    "batch": ["", "B01", "B0001", "B001-3", "B001-1-1-1", "b001", "B001\n", "B\uff10\uff10\uff11", "B001-", "B001--1"],
    "dispatch": ["", "dsp-01", "dsp-12345", "DSP-001", "dsp-001\n", "dsp-\u0661\u0662\u0663"],
    "group": ["", "CG-", "CG-1234567", "cg-1", "CG-1\n", "CG-\u0661"],
    "chain": ["", "CHAIN-01", "CHAIN-1234567", "chain-001", "CHAIN-001\n", "CHAIN-\u0661\u0662\u0663"],
    "language": ["", "a" * 21, "Python", "py thon", "py\n", "c\u00e9", "\u65e5\u672c", "c/c", "py_thon", "x.y"],
}

NON_STRINGS = [None, 1, 1.5, b"S-1", ["S-1"], {"S-1": 1}, True]


@pytest.mark.parametrize("kind", sorted(CONTRACT_PATTERNS))
def test_pattern_source_is_the_contracts_text_and_has_no_unsafe_construct(kind):
    source = tachi_parts.ID_PATTERNS[kind]
    assert source == CONTRACT_PATTERNS[kind]
    # KB 24: \d admits non-ASCII digits, \w and \s admit more than ASCII, and $ admits a trailing newline.
    for unsafe in ("\\d", "\\w", "\\s", "$", "^"):
        assert unsafe not in source, "%s pattern holds %r" % (kind, unsafe)


def test_the_allow_list_table_names_exactly_the_contracts_kinds():
    assert set(tachi_parts.ID_PATTERNS) == set(CONTRACT_PATTERNS)


@pytest.mark.parametrize("kind,value", [(k, v) for k, vs in VALID_IDS.items() for v in vs])
def test_valid_identifiers_match(kind, value):
    assert tachi_parts.id_matches(kind, value) is True


@pytest.mark.parametrize("kind,value", [(k, v) for k, vs in INVALID_IDS.items() for v in vs])
def test_invalid_identifiers_are_refused(kind, value):
    assert tachi_parts.id_matches(kind, value) is False


@pytest.mark.parametrize("kind", sorted(CONTRACT_PATTERNS))
@pytest.mark.parametrize("value", NON_STRINGS)
def test_a_non_string_never_matches(kind, value):
    assert tachi_parts.id_matches(kind, value) is False


def test_an_unknown_kind_raises_so_a_typo_fails_loudly():
    with pytest.raises(KeyError):
        tachi_parts.id_matches("findings", "S-1")


@pytest.mark.parametrize("kind,sample", [(k, VALID_IDS[k][0]) for k in sorted(VALID_IDS)])
def test_a_trailing_newline_is_refused_for_every_kind(kind, sample):
    """KB 24: ``$`` would let ``"S-1\\n"`` through; ``fullmatch`` with no ``$`` must not."""
    assert tachi_parts.id_matches(kind, sample) is True
    assert tachi_parts.id_matches(kind, sample + "\n") is False


# =============================================================================
# 2. Canonical finding IDs and S-2's order
# =============================================================================

def test_the_prefix_rank_is_s2s_order():
    assert tachi_parts.FINDING_PREFIXES == ("S", "T", "R", "I", "D", "E", "AG", "AGP", "LLM", "OI", "MI", "TE")


def test_the_finding_pattern_is_built_from_the_same_prefixes():
    assert tachi_parts.ID_PATTERNS["finding"] == "(" + "|".join(tachi_parts.FINDING_PREFIXES) + ")-[0-9]{1,6}"


@pytest.mark.parametrize("spelled,canonical", [
    ("S-1", "S-1"), ("AGP-01", "AGP-1"), ("AGP-1", "AGP-1"), ("S-000001", "S-1"), ("T-10", "T-10"),
    ("T-010", "T-10"), ("S-0", "S-0"), ("S-000", "S-0"), ("E-999999", "E-999999"), ("TE-007", "TE-7"),
])
def test_canonical_finding_id_drops_leading_zeros(spelled, canonical):
    assert tachi_parts.canonical_finding_id(spelled) == canonical


@pytest.mark.parametrize("bad", ["", "S-", "s-1", "S-1\n", "S-\u0661", "S-1234567", None, 7, b"S-1"])
def test_canonical_finding_id_refuses_a_non_id(bad):
    with pytest.raises(ValueError):
        tachi_parts.canonical_finding_id(bad)


def test_two_spellings_of_one_id_have_one_canonical_form_and_one_sort_key():
    assert tachi_parts.canonical_finding_id("AGP-01") == tachi_parts.canonical_finding_id("AGP-001")
    assert tachi_parts.finding_sort_key("AGP-01") == tachi_parts.finding_sort_key("AGP-1")


def test_s2_orders_by_prefix_rank_then_by_the_suffix_as_an_integer():
    shuffled = ["TE-1", "MI-1", "OI-1", "LLM-1", "AGP-1", "AG-1", "E-1", "D-1", "I-1", "R-1", "T-1", "S-1"]
    assert sorted(shuffled, key=tachi_parts.finding_sort_key) == [
        "S-1", "T-1", "R-1", "I-1", "D-1", "E-1", "AG-1", "AGP-1", "LLM-1", "OI-1", "MI-1", "TE-1"]


def test_s2_compares_suffixes_as_integers_not_as_text():
    ids = ["T-100", "T-9", "T-10", "T-1", "T-099"]
    assert sorted(ids, key=tachi_parts.finding_sort_key) == ["T-1", "T-9", "T-10", "T-099", "T-100"]


def test_s2_puts_a_high_number_of_an_earlier_prefix_before_a_low_number_of_a_later_one():
    assert tachi_parts.finding_sort_key("S-999999") < tachi_parts.finding_sort_key("T-1")
    assert tachi_parts.finding_sort_key("AG-999999") < tachi_parts.finding_sort_key("AGP-1")
    assert tachi_parts.finding_sort_key("AGP-999999") < tachi_parts.finding_sort_key("LLM-1")


def test_s2_ties_only_between_spellings_of_one_id():
    keys = {tachi_parts.finding_sort_key(i) for i in ("S-1", "S-01", "S-001", "S-2")}
    assert len(keys) == 2


@pytest.mark.parametrize("bad", ["", "X-1", "S-1\n", "S-\u0661", None])
def test_finding_sort_key_refuses_a_non_id(bad):
    with pytest.raises(ValueError):
        tachi_parts.finding_sort_key(bad)


# =============================================================================
# 3. D7's syntactic path rule
# =============================================================================

PATHS_THAT_PASS = [
    "src/app/main.py", "a.py", "docs/security/architecture.md", "./src//a.py", "src/a:b.py", "a b/c.py",
    "src/\u00fcn\u00ef.py", "...", "..a/b", "a/.../b", "src/", "a/./b/./c", "%2e%2e/x", "~/x", "C" + "x" * 280 + ".py",
]

PATHS_REFUSED = [
    ("", "empty"), (".", "empty"), ("./", "empty"), ("././.", "empty"),
    ("/etc/passwd", "leading-slash"), ("//host/share/x", "leading-slash"), ("/", "leading-slash"),
    ("C:/Windows/x", "drive-letter"), ("c:rel", "drive-letter"), ("Z:", "drive-letter"),
    ("https://example.test/x", "scheme"), ("file:///etc/passwd", "scheme"), ("javascript:alert", "scheme"),
    ("a:b/c", "drive-letter"), ("1:x", "scheme"), (":x", "scheme"), ("ab:c", "scheme"),
    ("a\\b.py", "backslash"), ("C:\\Windows\\x", "backslash"), ("\\\\host\\share", "backslash"),
    ("a`b", "backtick"), ("`cmd`", "backtick"),
    ("a\x00b", "control-char"), ("a\nb", "control-char"), ("a\tb", "control-char"), ("a\rb", "control-char"),
    ("a\x7fb", "control-char"), ("a\x85b", "control-char"), ("a\x9fb", "control-char"), ("a\x1bb", "control-char"),
    ("../x", "parent-reference"), ("a/../b", "parent-reference"), ("a/..", "parent-reference"),
    ("a/b/../../..", "parent-reference"), ("./../x", "parent-reference"),
    ("a/" + "b" * 4095, "too-long"), ("\u00e9" * 2100, "too-long"),
    ("a\udc80b", "encoding"),
]


@pytest.mark.parametrize("value", PATHS_THAT_PASS)
def test_a_relative_path_that_follows_the_rule_passes(value):
    assert tachi_parts.path_problem(value) is None


@pytest.mark.parametrize("value,problem", PATHS_REFUSED)
def test_a_path_that_breaks_the_rule_is_refused_with_the_failed_checks_name(value, problem):
    assert tachi_parts.path_problem(value) == problem


@pytest.mark.parametrize("value", [None, 1, b"a/b", ["a"], {"a": 1}])
def test_a_non_string_path_is_refused_as_a_type_problem(value):
    assert tachi_parts.path_problem(value) == "type"


def test_the_length_limit_is_in_bytes_and_inclusive():
    assert tachi_parts.PATH_MAX_BYTES == 4096
    assert tachi_parts.path_problem("a" * 4096) is None
    assert tachi_parts.path_problem("a" * 4097) == "too-long"
    assert tachi_parts.path_problem("\u00e9" * 2048) is None  # 4096 bytes
    assert tachi_parts.path_problem("\u00e9" * 2049) == "too-long"


@pytest.mark.parametrize("value", ["/a/b/c.md", "//a", "/work/proj/docs/architecture.md", "a/b.md"])
def test_an_absolute_candidate_passes_only_when_the_caller_allows_it(value):
    assert tachi_parts.path_problem(value, allow_absolute=True) is None
    if value.startswith("/"):
        assert tachi_parts.path_problem(value) == "leading-slash"


@pytest.mark.parametrize("value,problem", [
    ("/", "empty"), ("/a/../b", "parent-reference"), ("/a\\b", "backslash"), ("/a`b", "backtick"),
    ("/a\nb", "control-char"), ("C:/x", "drive-letter"), ("https://x/y", "scheme"), ("", "empty"),
])
def test_allowing_an_absolute_path_relaxes_only_the_leading_slash(value, problem):
    assert tachi_parts.path_problem(value, allow_absolute=True) == problem


def test_path_parts_drops_dot_and_empty_components():
    assert tachi_parts.path_parts("./src//a.py") == ("src", "a.py")
    assert tachi_parts.path_parts("a/./b/") == ("a", "b")
    assert tachi_parts.path_parts("/a/b", allow_absolute=True) == ("a", "b")
    assert tachi_parts.path_parts("src/a:b.py") == ("src", "a:b.py")


@pytest.mark.parametrize("value,problem", [("../x", "parent-reference"), ("/a", "leading-slash"), ("C:/x", "drive-letter"), ("", "empty")])
def test_path_parts_raises_with_the_problems_name(value, problem):
    with pytest.raises(ValueError) as excinfo:
        tachi_parts.path_parts(value)
    assert str(excinfo.value) == problem


# =============================================================================
# 4. Module hygiene
# =============================================================================

TACHI_PARTS_PATH = SCRIPTS_DIR / "tachi_parts.py"


def _imported_modules(tree):
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def test_tachi_parts_imports_neither_sarif_common_nor_tachi_parsers():
    """C1: both import ``tachi_parts``, so it must import neither (no cycle)."""
    tree = ast.parse(TACHI_PARTS_PATH.read_text(encoding="utf-8"))
    imported = _imported_modules(tree)
    assert not {"sarif_common", "tachi_parsers"} & imported, imported


def _is_standard_library(name):
    """True for a built-in or a module that lives in the interpreter's own library directory."""
    import importlib.util
    import sysconfig
    if name in getattr(sys, "stdlib_module_names", ()):
        return True
    spec = importlib.util.find_spec(name)
    if spec is None:
        return False
    origin = spec.origin or ""
    stdlib = sysconfig.get_paths()["stdlib"]
    return origin in ("built-in", "frozen") or (origin.startswith(stdlib) and "site-packages" not in origin)


def test_tachi_parts_is_standard_library_only():
    tree = ast.parse(TACHI_PARTS_PATH.read_text(encoding="utf-8"))
    outside = sorted(name for name in _imported_modules(tree) if not _is_standard_library(name))
    assert outside == [], outside


def test_tachi_parts_parses_at_the_python_39_floor_and_defers_annotations():
    source = TACHI_PARTS_PATH.read_text(encoding="utf-8")
    ast.parse(source, feature_version=(3, 9))
    assert "from __future__ import annotations" in source


def test_importing_tachi_parts_turns_bytecode_writing_off(tmp_path):
    """T012: the module sets ``sys.dont_write_bytecode`` before any local import.

    A process alone shows it, so this runs a clean interpreter (``-I`` ignores the
    environment) whose cache goes to a test-owned prefix.
    """
    code = "import sys; sys.path.insert(0, %r); import tachi_parts; print(sys.dont_write_bytecode)" % str(SCRIPTS_DIR)
    proc = subprocess.run(
        [sys.executable, "-I", "-X", "pycache_prefix=%s" % (tmp_path / "pyc"), "-c", code],
        capture_output=True, encoding="utf-8", timeout=60)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "True"


# =============================================================================
# Fixtures for the later slices: a valid part, and where it lives
#
# The API these sections expect (T012's second slice and T013 write it to match):
#   PartError(kind, detail)            kind: "missing" | "unparseable" | "invalid"
#   load_json(path, out, max_bytes=524288) -> object                   steps 1 to 4
#   read_part(path, out, plan_id, batch_id, stage, agent_type, finding_ids) -> PartResult
#   classify_part(obj, plan_id, batch_id, stage, agent_type, finding_ids) -> PartResult
#   PartResult.state: "done" | "missing" | "overflow" | "unparseable" | "invalid"
#   PartResult.detail (str), .part (the validated part, IDs canonical), .flags
#   ({canonical ID: [flag, ...]}), .counts ({"narrative_fallbacks": n, "truncations": n})
# =============================================================================

PLAN = "20261122T101500Z-0123456789ab"
OTHER_PLAN = "20261122T101500Z-ba9876543210"
SCORER = {"stage": "risk-score", "agent_type": "tachi-risk-scorer"}
CONTROLS = {"stage": "compensating-controls", "agent_type": "tachi-control-analyzer"}
VECTOR = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
STATES = ("done", "missing", "overflow", "unparseable", "invalid")


def scorer_item(fid="S-1"):
    return {
        "finding_id": fid,
        "cvss_vector": VECTOR,
        "exploitability": {"known_techniques": 7, "attack_complexity": 6, "tooling_availability": 5, "skill_level": 4},
        "scalability": {"scriptability": 3, "target_scope": 4, "resource_requirements": 5, "detection_difficulty": 6},
        "reachability": {"zone": "Public Zone", "trust_level": "Untrusted", "auth_barriers": 1, "network_boundaries": 2},
        "rationale": {
            "cvss": "Network reachable with no privileges, so the base score is {{score:cvss_base}}.",
            "exploitability": "Public techniques exist and tooling is common.",
            "scalability": "A script can repeat the attack against every instance.",
            "reachability": "The component sits in {{name:zone}} behind {{count:auth_barriers}} barriers.",
        },
    }


def controls_item(fid="S-1", status="found"):
    entry = {"file": "src/auth/login.py", "line": 42, "language": "python",
             "snippet": "def login(user):\n    check(user)", "summary": "Login path calls the check at line 42."}
    item = {
        "finding_id": fid, "control_status": status, "control_category": "authentication",
        "confidence": "High", "carried_forward": False, "evidence": [entry],
        "matrix_row": "| " + fid + " | Spoofing | found |",
        "recommendation_body": None,
    }
    if status == "partial":
        item["recommendation_body"] = "What: add the missing check. Where: the login path. Effort: Low."
    if status == "missing":
        item.update(confidence=None, evidence=[], recommendation_body="What: add a control. Effort: Medium.")
    return item


def make_part(ids=("S-1", "T-2"), kind=SCORER, batch="B001", items=None, **override):
    build = scorer_item if kind is SCORER else controls_item
    part = {
        "schema": "tachi.part/1", "plan_id": PLAN, "batch_id": batch, "stage": kind["stage"],
        "agent_type": kind["agent_type"], "finding_ids": list(ids),
        "items": items if items is not None else [build(i) for i in ids], "fragments": [],
    }
    part.update(override)
    return part


def expect(ids=("S-1", "T-2"), kind=SCORER, batch="B001", plan_id=PLAN):
    return dict(plan_id=plan_id, batch_id=batch, stage=kind["stage"], agent_type=kind["agent_type"], finding_ids=list(ids))


def classify(obj, ids=("S-1", "T-2"), kind=SCORER, **kw):
    return _api("classify_part")(obj, **dict(expect(ids, kind), **kw))


def lay_out(tmp_path, kind=SCORER, batch="B001", attempt=1):
    out = tmp_path / "out"
    parts = out / ".tachi-build" / kind["stage"] / PLAN / "parts"
    parts.mkdir(parents=True, exist_ok=True)
    return out, parts / ("%s.a%d.json" % (batch, attempt))


def write_part(tmp_path, content, kind=SCORER):
    out, path = lay_out(tmp_path, kind)
    if isinstance(content, (dict, list)):
        content = json.dumps(content)
    path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
    return out, path


def read(tmp_path, content, ids=("S-1", "T-2"), kind=SCORER):
    out, path = write_part(tmp_path, content, kind)
    return _api("read_part")(path, out=out, **expect(ids, kind))


def inject(text, field, raw):
    """Replace the JSON text of one top-level scalar key's value with ``raw`` (hostile literals)."""
    return re.sub(r'("%s": )[^,}]+' % field, lambda m: m.group(1) + raw, text, count=1)


# =============================================================================
# 5. Strict loader: the file and the JSON text (steps 1 to 4)
# =============================================================================

def test_a_valid_part_is_done_and_its_ids_are_canonical(tmp_path):
    result = read(tmp_path, make_part(ids=("S-01", "T-2")), ids=("S-1", "T-2"))
    assert result.state == "done", result.detail
    assert result.part["finding_ids"] == ["S-1", "T-2"]
    assert [item["finding_id"] for item in result.part["items"]] == ["S-1", "T-2"]


def test_a_missing_part_is_missing(tmp_path):
    out, path = lay_out(tmp_path)
    assert _api("read_part")(path, out=out, **expect()).state == "missing"


def test_a_symlinked_part_is_invalid(tmp_path):
    out, path = lay_out(tmp_path)
    real = tmp_path / "elsewhere.json"
    real.write_text(json.dumps(make_part()), encoding="utf-8")
    path.symlink_to(real)
    assert _api("read_part")(path, out=out, **expect()).state == "invalid"


def test_a_symlinked_directory_below_out_is_invalid(tmp_path):
    out = tmp_path / "out"
    (out / ".tachi-build" / "risk-score").mkdir(parents=True)
    elsewhere = tmp_path / "elsewhere" / "parts"
    elsewhere.mkdir(parents=True)
    (elsewhere / "B001.a1.json").write_text(json.dumps(make_part()), encoding="utf-8")
    (out / ".tachi-build" / "risk-score" / PLAN).symlink_to(elsewhere.parent)
    path = out / ".tachi-build" / "risk-score" / PLAN / "parts" / "B001.a1.json"
    assert _api("read_part")(path, out=out, **expect()).state == "invalid"


def test_a_part_outside_out_is_invalid(tmp_path):
    out, _ = lay_out(tmp_path)
    stray = tmp_path / "stray.json"
    stray.write_text(json.dumps(make_part()), encoding="utf-8")
    assert _api("read_part")(stray, out=out, **expect()).state == "invalid"


def test_a_directory_at_the_part_path_is_invalid(tmp_path):
    out, path = lay_out(tmp_path)
    path.mkdir()
    assert _api("read_part")(path, out=out, **expect()).state == "invalid"


def test_an_oversized_part_is_unparseable(tmp_path):
    pad = " " * (512 * 1024)
    assert read(tmp_path, json.dumps(make_part()) + pad).state == "unparseable"


@pytest.mark.parametrize("raw", [
    b"", b"   ", b"{", b'{"schema": ', b"[]", b'"x"', b"1", b"null", b"true",
    b"\xef\xbb\xbf" + json.dumps(make_part()).encode("utf-8"),
    b'{"a": "\xff"}', b'{"a": "\xed\xa0\x80"}', b'{"a": "\\ud800"}', b'{"a": "\\udfff"}',
], ids=["empty", "blank", "truncated", "cut-mid-key", "array-top", "string-top", "number-top", "null-top",
        "true-top", "bom", "invalid-utf8", "encoded-surrogate", "escaped-high-surrogate", "escaped-low-surrogate"])
def test_text_that_is_not_one_strict_utf8_json_object_is_unparseable(tmp_path, raw):
    assert read(tmp_path, raw).state == "unparseable"


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_nan_and_infinity_are_unparseable(tmp_path, constant):
    text = inject(json.dumps(make_part()), "schema", constant)
    assert read(tmp_path, text).state == "unparseable"
    text = json.dumps(make_part()).replace('"known_techniques": 7', '"known_techniques": ' + constant)
    assert read(tmp_path, text).state == "unparseable"


@pytest.mark.parametrize("literal", ["1e400", "1E400", "-1e400", "1e999", "1e-400", "7.0", "0.5", "1e1"])
def test_a_float_or_an_overflowing_exponent_never_becomes_a_number_the_checks_accept(tmp_path, literal):
    """``parse_float=Decimal``: ``1e400`` arrives as a Decimal that the range check rejects, never ``inf``."""
    text = json.dumps(make_part()).replace('"known_techniques": 7', '"known_techniques": ' + literal)
    assert read(tmp_path, text).state == "invalid"


def test_an_integer_literal_of_more_than_twenty_digits_is_unparseable(tmp_path):
    base = json.dumps(make_part())
    twenty, twenty_one, thirty = "1" * 20, "1" * 21, "1" * 30
    assert read(tmp_path, base.replace('"known_techniques": 7', '"known_techniques": ' + twenty)).state == "invalid"
    assert read(tmp_path, base.replace('"known_techniques": 7', '"known_techniques": ' + twenty_one)).state == "unparseable"
    assert read(tmp_path, base.replace('"known_techniques": 7', '"known_techniques": ' + thirty)).state == "unparseable"
    assert read(tmp_path, base.replace('"known_techniques": 7', '"known_techniques": -' + twenty_one)).state == "unparseable"


def test_duplicate_keys_are_unparseable_at_any_depth(tmp_path):
    top = json.dumps(make_part())[:-1] + ', "plan_id": "' + PLAN + '"}'
    assert read(tmp_path, top).state == "unparseable"
    nested = json.dumps(make_part()).replace('"known_techniques": 7,', '"known_techniques": 7, "known_techniques": 8,')
    assert read(tmp_path, nested).state == "unparseable"


def test_nesting_deeper_than_eight_levels_is_unparseable_and_a_recursion_bomb_never_crashes(tmp_path):
    load = _api("load_json")
    out, path = lay_out(tmp_path)
    for depth, ok in ((8, True), (9, False)):
        doc = "[" * (depth - 1) + "]" * (depth - 1)
        path.write_text('{"a": ' + doc + "}", encoding="utf-8")
        if ok:
            assert isinstance(load(path, out=out), dict)
        else:
            with pytest.raises(_api("PartError")) as excinfo:
                load(path, out=out)
            assert excinfo.value.kind == "unparseable"
    path.write_text('{"a": ' + "[" * 100000 + "]" * 100000 + "}", encoding="utf-8")
    with pytest.raises(_api("PartError")) as excinfo:
        load(path, out=out)
    assert excinfo.value.kind == "unparseable"


def test_load_json_reports_the_kind_for_each_early_failure(tmp_path):
    load, error = _api("load_json"), _api("PartError")
    out, path = lay_out(tmp_path)
    with pytest.raises(error) as missing:
        load(path, out=out)
    assert missing.value.kind == "missing"
    path.write_bytes(b'{"a": 1' + b" " * 600)
    with pytest.raises(error) as small:
        load(path, out=out, max_bytes=100)
    assert small.value.kind == "unparseable"
    path.write_text('{"a": 1}', encoding="utf-8")
    assert load(path, out=out) == {"a": 1}


def test_a_stale_part_from_an_earlier_plan_never_counts(tmp_path):
    result = read(tmp_path, make_part(plan_id=OTHER_PLAN))
    assert result.state == "invalid"
    assert result.part is None


def put(obj, path, value):
    """Set ``obj[path[0]][path[1]]...`` to ``value`` and return ``obj``."""
    cur = obj
    for key in path[:-1]:
        cur = cur[key]
    cur[path[-1]] = value
    return obj


# =============================================================================
# 6. Envelope: schema first, closed keys, overflow (steps 5 to 8)
# =============================================================================

ENVELOPE_KEYS = ("schema", "plan_id", "batch_id", "stage", "agent_type", "finding_ids", "items", "fragments")


def test_a_part_that_follows_the_contract_is_done_for_both_pr1_stages():
    assert classify(make_part()).state == "done"
    assert classify(make_part(kind=CONTROLS), kind=CONTROLS).state == "done"


@pytest.mark.parametrize("schema", ["tachi.part/2", "tachi.part/0", "tachi.plan/1", "TACHI.PART/1", "tachi.part/1 ",
                                    "tachi.part/1\n", "", None, 1, ["tachi.part/1"]])
def test_any_schema_other_than_tachi_part_1_is_invalid(schema):
    assert classify(make_part(schema=schema)).state == "invalid"


@pytest.mark.parametrize("key", ENVELOPE_KEYS)
def test_each_of_the_eight_envelope_keys_is_required(key):
    part = make_part()
    del part[key]
    assert classify(part).state == "invalid"


@pytest.mark.parametrize("extra", ["extra", "Items", "notes", "cvss_base", "", "schema "])
def test_an_unknown_envelope_key_is_invalid(extra):
    assert classify(make_part(**{extra: 1})).state == "invalid"


@pytest.mark.parametrize("field,value", [
    ("batch_id", "B002"), ("batch_id", "B001\n"), ("batch_id", "B01"), ("stage", "compensating-controls"),
    ("stage", "trees"), ("stage", "bogus"), ("agent_type", "tachi-control-analyzer"), ("agent_type", "general-purpose"),
    ("plan_id", PLAN + "\n"), ("plan_id", "20261122T101500Z-0123456789AB"), ("plan_id", None), ("batch_id", 1),
])
def test_the_plan_batch_stage_and_agent_must_equal_the_planned_batchs(field, value):
    assert classify(make_part(**{field: value})).state == "invalid"


@pytest.mark.parametrize("field,value", [
    ("finding_ids", []), ("finding_ids", "S-1"), ("finding_ids", [1, 2]), ("finding_ids", None),
    ("items", {}), ("items", "x"), ("items", None), ("items", ["S-1", "T-2"]), ("items", [[], []]),
    ("fragments", [{"slot_key": "intro", "text": "x"}]), ("fragments", None), ("fragments", {}),
])
def test_envelope_values_have_the_contracts_types_and_pr1_stages_carry_no_fragments(field, value):
    part = make_part()
    part[field] = value
    assert classify(part).state == "invalid"


def test_a_part_names_between_one_and_five_hundred_ids():
    ids = ["S-%d" % n for n in range(1, 502)]
    assert classify(make_part(ids=ids), ids=ids).state == "invalid"
    ids = ids[:500]
    assert classify(make_part(ids=ids), ids=ids).state == "done"


def overflow_object(reason="output-budget", **override):
    obj = {"schema": "tachi.overflow/1", "plan_id": PLAN, "batch_id": "B001", "stage": "risk-score",
           "agent_type": "tachi-risk-scorer", "reason": reason}
    obj.update(override)
    return obj


@pytest.mark.parametrize("reason", ["output-budget", "input-too-large", "other"])
def test_a_six_key_overflow_object_is_classified_overflow_never_invalid(reason):
    result = classify(overflow_object(reason))
    assert result.state == "overflow"
    assert result.detail == reason
    assert result.part is None


def test_an_overflow_object_is_classified_overflow_when_read_from_disk(tmp_path):
    assert read(tmp_path, overflow_object()).state == "overflow"


@pytest.mark.parametrize("bad", [
    {"reason": "bogus"}, {"reason": None}, {"reason": 1}, {"reason": ""}, {"schema": "tachi.overflow/2"},
    {"extra": 1}, {"plan_id": OTHER_PLAN}, {"batch_id": "B002"}, {"batch_id": "B001\n"},
    {"stage": "compensating-controls"}, {"agent_type": "tachi-control-analyzer"},
])
def test_an_overflow_object_that_is_not_well_formed_for_its_batch_is_invalid(bad):
    assert classify(overflow_object(**bad)).state == "invalid"


def test_an_overflow_object_with_a_missing_key_is_invalid():
    obj = overflow_object()
    del obj["reason"]
    assert classify(obj).state == "invalid"


def test_the_overflow_schema_does_not_license_the_parts_eight_keys():
    obj = make_part(schema="tachi.overflow/1")
    obj["reason"] = "other"
    assert classify(obj).state == "invalid"


# =============================================================================
# 7. IDs: batch membership, duplicates, spellings (step 8)
# =============================================================================

def test_ids_outside_the_batch_are_invalid():
    assert classify(make_part(ids=("S-1", "T-3")), ids=("S-1", "T-2")).state == "invalid"
    assert classify(make_part(ids=("S-1",)), ids=("S-1", "T-2")).state == "invalid"
    assert classify(make_part(ids=("S-1", "T-2", "R-3")), ids=("S-1", "T-2")).state == "invalid"


def test_an_item_for_an_id_outside_the_list_or_a_second_item_for_one_id_is_invalid():
    part = make_part()
    part["items"][1] = scorer_item("R-9")
    assert classify(part).state == "invalid"
    part = make_part()
    part["items"][1] = scorer_item("S-1")
    assert classify(part).state == "invalid"
    part = make_part()
    part["items"].append(scorer_item("S-1"))
    assert classify(part).state == "invalid"
    part = make_part()
    part["items"].pop()
    assert classify(part).state == "invalid"


def test_a_duplicate_id_is_invalid():
    assert classify(make_part(ids=("S-1", "S-1")), ids=("S-1", "S-1")).state == "invalid"
    assert classify(make_part(ids=("S-1", "S-1")), ids=("S-1", "T-2")).state == "invalid"


@pytest.mark.parametrize("pair", [("S-1", "S-01"), ("AGP-1", "AGP-001"), ("T-10", "T-010")])
def test_two_spellings_of_one_canonical_id_are_a_duplicate(pair):
    ids = (pair[0], pair[1])
    assert classify(make_part(ids=ids), ids=(pair[0], "R-9")).state == "invalid"
    part = make_part(ids=(pair[0], "R-9"))
    part["items"][1] = scorer_item(pair[1])
    assert classify(part, ids=(pair[0], "R-9")).state == "invalid"


@pytest.mark.parametrize("bad", ["S-١", "S-１", "S-1\n", "S-1 ", "s-1", "S-", "S-1234567", "X-1", "S-1​"])
def test_a_hostile_id_is_invalid_wherever_it_appears(bad):
    assert classify(make_part(ids=(bad, "T-2")), ids=("S-1", "T-2")).state == "invalid"
    part = make_part()
    part["items"][0]["finding_id"] = bad
    result = classify(part)
    assert result.state == "invalid"
    assert result.part is None


def test_a_planned_spelling_and_a_canonical_equal_spelling_in_the_part_agree():
    result = classify(make_part(ids=("AGP-01", "T-2")), ids=("AGP-1", "T-2"))
    assert result.state == "done", result.detail
    assert result.part["finding_ids"] == ["AGP-1", "T-2"]


# =============================================================================
# 8. Strings: control, bidi and separator characters (step 10)
# =============================================================================

HOSTILE_CHARS = [
    "\x00", "\x01", "\x07", "\x08", "\x0b", "\x0c", "\r", "\x1b", "\x1f", "\x7f",
    "\x80", "\x85", "\x9b", "\x9f",
    " ", " ",
    "‎", "‏", "؜", "‪", "‫", "‬", "‭", "‮",
    "⁦", "⁧", "⁨", "⁩",
]


@pytest.mark.parametrize("char", HOSTILE_CHARS, ids=["U+%04X" % ord(c) for c in HOSTILE_CHARS])
def test_a_hostile_character_in_any_string_class_is_invalid(char):
    narrative = put(make_part(), ("items", 0, "rationale", "exploitability"), "Public tooling" + char + " exists.")
    assert classify(narrative).state == "invalid"
    closed = put(make_part(), ("items", 0, "reachability", "zone"), "Public" + char + "Zone")
    assert classify(closed).state == "invalid"
    evidence = put(make_part(kind=CONTROLS), ("items", 0, "evidence", 0, "summary"), "Check" + char + "here.")
    assert classify(evidence, kind=CONTROLS).state == "invalid"


def test_newline_and_tab_are_the_only_control_characters_prose_may_hold():
    part = put(make_part(), ("items", 0, "rationale", "exploitability"), "Public tooling\texists.\nSecond line.")
    assert classify(part).state == "done"
    part = put(make_part(kind=CONTROLS), ("items", 0, "evidence", 0, "summary"), "Check\there.\nMore.")
    assert classify(part, kind=CONTROLS).state == "done"


def test_a_closed_value_over_sixteen_thousand_characters_is_invalid():
    part = put(make_part(), ("items", 0, "reachability", "zone"), "z" * 16385)
    assert classify(part).state == "invalid"


# =============================================================================
# 9. Scorer and controls payloads (steps 6 and 9, RR2's cut-and-flag)
# =============================================================================

def drop(path):
    def mutate(item):
        cur = item
        for key in path[:-1]:
            cur = cur[key]
        del cur[path[-1]]
    return mutate


def setter(path, value):
    def mutate(item):
        put(item, path, value)
    return mutate


SCORER_VIOLATIONS = {
    "renderer-computed cvss_base": setter(("cvss_base",), 7.5),
    "renderer-computed composite": setter(("composite",), 5),
    "renderer-computed severity": setter(("severity",), "High"),
    "renderer-computed flags": setter(("flags",), []),
    "unknown key": setter(("extra",), 1),
    **{"missing %s" % key: drop((key,)) for key in
       ("finding_id", "cvss_vector", "exploitability", "scalability", "reachability", "rationale")},
    "vector 3.0": setter(("cvss_vector",), VECTOR.replace("3.1", "3.0")),
    "vector trailing newline": setter(("cvss_vector",), VECTOR + "\n"),
    "vector lowercase": setter(("cvss_vector",), VECTOR.lower()),
    "vector missing A": setter(("cvss_vector",), VECTOR.rsplit("/", 1)[0]),
    "vector bad metric": setter(("cvss_vector",), VECTOR.replace("AV:N", "AV:X")),
    "vector null": setter(("cvss_vector",), None),
    "vector empty": setter(("cvss_vector",), ""),
    "exploitability not an object": setter(("exploitability",), [7, 6, 5, 4]),
    "exploitability missing key": drop(("exploitability", "skill_level")),
    "exploitability extra key": setter(("exploitability", "stealth"), 3),
    "scalability missing key": drop(("scalability", "target_scope")),
    "scalability extra key": setter(("scalability", "reach"), 3),
    "sub-score below 0": setter(("exploitability", "known_techniques"), -1),
    "sub-score above 10": setter(("scalability", "scriptability"), 11),
    "sub-score boolean": setter(("exploitability", "attack_complexity"), True),
    "sub-score float": setter(("exploitability", "tooling_availability"), 7.5),
    "sub-score text": setter(("scalability", "detection_difficulty"), "7"),
    "sub-score null": setter(("scalability", "resource_requirements"), None),
    "reachability extra key": setter(("reachability", "score"), 5),
    "reachability missing key": drop(("reachability", "network_boundaries")),
    "zone empty": setter(("reachability", "zone"), ""),
    "zone over 120": setter(("reachability", "zone"), "z" * 121),
    "zone null with a trust level": setter(("reachability", "zone"), None),
    "trust level null with a zone": setter(("reachability", "trust_level"), None),
    "trust level unknown": setter(("reachability", "trust_level"), "trusted"),
    "auth barriers below 0": setter(("reachability", "auth_barriers"), -1),
    "auth barriers above 10": setter(("reachability", "auth_barriers"), 11),
    "network boundaries float": setter(("reachability", "network_boundaries"), 1.5),
    "rationale missing key": drop(("rationale", "scalability")),
    "rationale extra key": setter(("rationale", "composite"), "x"),
    "rationale empty": setter(("rationale", "cvss"), ""),
    "rationale not text": setter(("rationale", "cvss"), 7),
    "metric_rationale unknown metric": setter(("metric_rationale",), {"Z": "x"}),
    "metric_rationale not an object": setter(("metric_rationale",), ["AV"]),
    "metric_rationale value not text": setter(("metric_rationale",), {"AV": 7}),
    "subscore_rationale unknown name": setter(("subscore_rationale",), {"stealth": "x"}),
}


@pytest.mark.parametrize("label", sorted(SCORER_VIOLATIONS))
def test_a_scorer_item_that_breaks_the_closed_payload_rejects_the_part(label):
    part = make_part()
    SCORER_VIOLATIONS[label](part["items"][0])
    result = classify(part)
    assert result.state == "invalid", label


def test_a_scorer_item_with_the_optional_keys_and_a_null_zone_is_done():
    part = make_part()
    part["items"][0]["metric_rationale"] = {"AV": "Reachable over the network.", "PR": "No privileges needed."}
    part["items"][0]["subscore_rationale"] = {"known_techniques": "Well documented.", "skill_level": "Low skill."}
    part["items"][1]["reachability"].update(zone=None, trust_level=None)
    assert classify(part).state == "done"


@pytest.mark.parametrize("trust", ["Untrusted", "Semi-Trusted", "Trusted"])
def test_each_trust_level_the_contract_names_is_accepted(trust):
    part = put(make_part(), ("items", 0, "reachability", "trust_level"), trust)
    assert classify(part).state == "done"


CONTROL_CATEGORIES = ["authentication", "input-validation", "rate-limiting", "encryption", "logging-audit",
                      "csrf-protection", "csp-security-headers", "access-control"]


@pytest.mark.parametrize("category", CONTROL_CATEGORIES)
def test_each_of_the_eight_control_categories_is_accepted(category):
    part = put(make_part(kind=CONTROLS), ("items", 0, "control_category"), category)
    assert classify(part, kind=CONTROLS).state == "done"


CONTROLS_VIOLATIONS = {
    "unknown key": setter(("residual_score",), 3),
    "renderer-computed inherent": setter(("inherent_score",), 3),
    **{"missing %s" % key: drop((key,)) for key in
       ("finding_id", "control_status", "control_category", "confidence", "carried_forward", "evidence",
        "matrix_row", "recommendation_body")},
    "status unknown": setter(("control_status",), "absent"),
    "category outside the eight": setter(("control_category",), "network-segmentation"),
    "category in the wrong case": setter(("control_category",), "Authentication"),
    "confidence unknown": setter(("confidence",), "Certain"),
    "confidence null for found": setter(("confidence",), None),
    "carried_forward as a number": setter(("carried_forward",), 1),
    "carried_forward as text": setter(("carried_forward",), "false"),
    "carried_forward null": setter(("carried_forward",), None),
    "evidence empty for found": setter(("evidence",), []),
    "evidence over five entries": setter(("evidence",), [dict(controls_item()["evidence"][0]) for _ in range(6)]),
    "evidence not a list": setter(("evidence",), {}),
    "evidence entry unknown key": setter(("evidence", 0, "score"), 5),
    **{"evidence entry missing %s" % key: drop(("evidence", 0, key)) for key in
       ("file", "line", "language", "snippet", "summary")},
    "line zero": setter(("evidence", 0, "line"), 0),
    "line negative": setter(("evidence", 0, "line"), -3),
    "line float": setter(("evidence", 0, "line"), 4.5),
    "line boolean": setter(("evidence", 0, "line"), True),
    "line text": setter(("evidence", 0, "line"), "42"),
    "language upper case": setter(("evidence", 0, "language"), "Python"),
    "language with a space": setter(("evidence", 0, "language"), "py thon"),
    "language empty": setter(("evidence", 0, "language"), ""),
    "language over 20": setter(("evidence", 0, "language"), "a" * 21),
    "file over 300": setter(("evidence", 0, "file"), "a" * 301),
    "file empty": setter(("evidence", 0, "file"), ""),
    "recommendation on a found result": setter(("recommendation_body",), "What: nothing."),
    "assessment unknown dimension": setter(("evidence", 0, "assessment"), {"strength": {"rating": "High", "rationale": "x"}}),
    "assessment rating unknown": setter(("evidence", 0, "assessment"), {
        d: {"rating": "Critical", "rationale": "x"} for d in ("coverage", "configuration", "currency", "completeness")}),
}


@pytest.mark.parametrize("label", sorted(CONTROLS_VIOLATIONS))
def test_a_controls_item_that_breaks_the_closed_payload_rejects_the_part(label):
    part = make_part(kind=CONTROLS)
    CONTROLS_VIOLATIONS[label](part["items"][0])
    assert classify(part, kind=CONTROLS).state == "invalid", label


@pytest.mark.parametrize("status,change,label", [
    ("partial", {"recommendation_body": None}, "partial without a recommendation"),
    ("missing", {"recommendation_body": None}, "missing without a recommendation"),
    ("missing", {"confidence": "High"}, "missing with a confidence"),
    ("missing", {"evidence": [controls_item()["evidence"][0]]}, "missing with evidence"),
    ("partial", {"evidence": []}, "partial without evidence"),
])
def test_status_decides_which_controls_keys_must_be_empty_or_present(status, change, label):
    part = make_part(kind=CONTROLS, items=[dict(controls_item("S-1", status), **change), controls_item("T-2")])
    assert classify(part, kind=CONTROLS).state == "invalid", label


def test_a_partial_and_a_missing_controls_result_that_follow_the_contract_are_done():
    part = make_part(kind=CONTROLS, items=[controls_item("S-1", "partial"), controls_item("T-2", "missing")])
    assert classify(part, kind=CONTROLS).state == "done"


def test_an_evidence_assessment_with_the_four_dimensions_is_accepted():
    assessment = {d: {"rating": "Medium", "rationale": "Covers the main path."}
                  for d in ("coverage", "configuration", "currency", "completeness")}
    part = put(make_part(kind=CONTROLS), ("items", 0, "evidence", 0, "assessment"), assessment)
    assert classify(part, kind=CONTROLS).state == "done"


def test_five_evidence_entries_and_a_three_hundred_character_file_are_the_limits():
    entries = [dict(controls_item()["evidence"][0], file="d/" + "f" * 298) for _ in range(5)]
    part = put(make_part(kind=CONTROLS), ("items", 0, "evidence"), entries)
    assert classify(part, kind=CONTROLS).state == "done"


# --- RR2: over-limit prose is cut at its limit and flagged; it never rejects the part ---

def truncation_cases():
    return [
        (SCORER, ("rationale", "cvss"), 400, "rationale.cvss"),
        (SCORER, ("rationale", "reachability"), 400, "rationale.reachability"),
        (SCORER, ("metric_rationale", "AV"), 160, "metric_rationale.AV"),
        (SCORER, ("subscore_rationale", "known_techniques"), 160, "subscore_rationale.known_techniques"),
        (CONTROLS, ("evidence", 0, "summary"), 160, "evidence.summary"),
        (CONTROLS, ("evidence", 0, "snippet"), 600, "evidence.snippet"),
        (CONTROLS, ("matrix_row",), 1200, "matrix_row"),
        (CONTROLS, ("recommendation_body",), 2000, "recommendation_body"),
    ]


def with_text(kind, path, text):
    item = scorer_item("S-1") if kind is SCORER else controls_item("S-1", "partial")
    part = make_part(kind=kind, items=[item], ids=("S-1",))
    if path[0] in ("metric_rationale", "subscore_rationale"):
        item[path[0]] = {path[1]: text}
    else:
        put(item, path, text)
    return part


@pytest.mark.parametrize("kind,path,limit,field", truncation_cases(), ids=[c[3] for c in truncation_cases()])
def test_prose_over_its_limit_is_cut_flagged_and_counted_never_rejected(kind, path, limit, field):
    result = classify(with_text(kind, path, "a" * (limit + 50)), ids=("S-1",), kind=kind)
    assert result.state == "done", result.detail
    assert "input:%s:truncated" % field in result.flags["S-1"]
    assert result.counts["truncations"] == 1
    item = result.part["items"][0]
    cur = item
    for key in path:
        cur = cur[key]
    assert cur == "a" * limit


@pytest.mark.parametrize("kind,path,limit,field", truncation_cases(), ids=[c[3] for c in truncation_cases()])
def test_prose_at_exactly_its_limit_is_kept_unflagged(kind, path, limit, field):
    result = classify(with_text(kind, path, "a" * limit), ids=("S-1",), kind=kind)
    assert result.state == "done", result.detail
    assert result.flags.get("S-1", []) == []
    assert result.counts["truncations"] == 0


def test_the_limit_counts_characters_not_bytes():
    result = classify(with_text(SCORER, ("rationale", "cvss"), "é" * 400), ids=("S-1",))
    assert result.state == "done"
    assert result.flags.get("S-1", []) == []


def test_a_snippet_over_five_lines_is_cut_to_five_lines_and_flagged():
    snippet = "\n".join("line %d" % n for n in range(1, 9))
    result = classify(with_text(CONTROLS, ("evidence", 0, "snippet"), snippet), ids=("S-1",), kind=CONTROLS)
    assert result.state == "done"
    assert result.part["items"][0]["evidence"][0]["snippet"] == "\n".join("line %d" % n for n in range(1, 6))
    assert "input:evidence.snippet:truncated" in result.flags["S-1"]


def test_a_cut_never_leaves_a_broken_slot_in_a_narrative_field():
    """The cut lands right after ``{{score:``, so step 11 must run on the cut text and fall back."""
    text = "x" * 392 + "{{score:cvss_base}}"
    result = classify(with_text(SCORER, ("rationale", "cvss"), text), ids=("S-1",))
    assert result.state == "done"
    stored = result.part["items"][0]["rationale"]["cvss"]
    assert _api("narrative_problem")(stored, "risk-score") is None
    assert stored == _api("narrative_fallback")("rationale.cvss")
    assert sorted(result.flags["S-1"]) == ["input:rationale.cvss:narrative-fallback", "input:rationale.cvss:truncated"]


def test_prose_over_a_limit_but_a_structural_slip_elsewhere_still_rejects():
    part = with_text(SCORER, ("rationale", "cvss"), "a" * 900)
    part["items"][0]["extra"] = 1
    assert classify(part, ids=("S-1",)).state == "invalid"


# =============================================================================
# 10. Narrative fields: slots, numeral ban, per-field fallback (step 11)
# =============================================================================

SUB_SCORES = ["known_techniques", "attack_complexity", "tooling_availability", "skill_level",
              "scriptability", "target_scope", "resource_requirements", "detection_difficulty"]
SCORER_STAGE, CONTROLS_STAGE = "risk-score", "compensating-controls"


def test_the_slot_table_gives_each_pr1_stage_its_closed_kinds_and_arguments():
    table = _api("SLOT_TABLE")
    assert set(table[SCORER_STAGE]) == {"score", "count", "band", "date", "finding", "ref", "name"}
    assert set(table[CONTROLS_STAGE]) == {"score", "count", "band", "pct", "finding", "ref", "name"}
    assert set(table[SCORER_STAGE]["score"]) == {"cvss_base", "exploitability", "scalability", "reachability",
                                                 "composite", *SUB_SCORES}
    assert set(table[SCORER_STAGE]["count"]) == {"auth_barriers", "network_boundaries"}
    assert set(table[SCORER_STAGE]["band"]) == {"severity"}
    assert set(table[SCORER_STAGE]["date"]) == {"scored", "review"}
    assert set(table[SCORER_STAGE]["name"]) == {"component", "zone"}
    assert set(table[CONTROLS_STAGE]["score"]) == {"inherent", "residual"}
    assert set(table[CONTROLS_STAGE]["count"]) == {"evidence"}
    assert set(table[CONTROLS_STAGE]["band"]) == {"inherent", "residual"}
    assert set(table[CONTROLS_STAGE]["pct"]) == {"reduction"}
    assert set(table[CONTROLS_STAGE]["name"]) == {"component"}


NARRATIVE_THAT_PASSES = {
    SCORER_STAGE: [
        "Plain prose with no numbers at all.",
        "Two-factor sign-in and third-party tools are in play.",
        "Score {{score:cvss_base}} in band {{band:severity}}.",
        "{{name:component}} sits in {{name:zone}}.",
        "See {{ref:CWE-89}}, {{ref:LLM01:2026}}, {{ref:AML.T0051}}, {{ref:L3}} and {{ref:T1190}}.",
        "Related to {{finding:S-1}} and {{finding:AGP-12}}.",
        "{{count:auth_barriers}} barriers and {{count:network_boundaries}} boundaries.",
        "Scored on {{date:scored}}, review by {{date:review}}.",
        "Literal {{ braces }} and a lone { brace } stay plain text.",
        "An unknown kind such as {{foo:bar}} is plain text, not a slot.",
        "Twelve findings in words pass the ban, because only the contract text forbids them.",
    ] + ["Sub-score {{score:%s}} drives it." % name for name in SUB_SCORES],
    CONTROLS_STAGE: [
        "{{score:inherent}} falls to {{score:residual}}.",
        "Band {{band:inherent}} becomes {{band:residual}}, a {{pct:reduction}} reduction.",
        "{{count:evidence}} entries support it for {{name:component}}.",
        "See {{ref:CWE-306}} and {{finding:T-2}}.",
    ],
}

NARRATIVE_THAT_FAILS = {
    SCORER_STAGE: [
        "CVSS 7.5 is high", "Uses OAuth2", "The S3 bucket", "TLS 1.3 only", "Listens on port 8080", "{{7*7}}", "a1",
        "x\u00b2", "half \u00bd", "Roman \u2167", "Arabic-Indic \u0663", "Fullwidth \uff11", "Circled \u2460", "\u32bf",
        "{{score:cvss_base", "{{score:cvss_base}", "{{score:cvss base}}", "{{score:}}", "{{score:" + "a" * 65 + "}}",
        "{{score:{{score:cvss_base}}}}", "{{ref:CWE/89}}", "{{ref:}}", "{{finding:}}", "{{score:bogus}}",
        "{{band:inherent}}", "{{score:inherent}}", "{{pct:reduction}}", "{{count:evidence}}", "{{name:component:S-1}}",
        "{{date:today}}", "{{name:owner}}",
    ],
    CONTROLS_STAGE: [
        "{{score:cvss_base}}", "{{name:zone}}", "{{date:scored}}", "{{count:auth_barriers}}", "{{band:severity}}",
        "Found at line 42", "{{score:inherent", "{{pct:bogus}}",
    ],
}


@pytest.mark.parametrize("stage,text", [(s, t) for s, ts in NARRATIVE_THAT_PASSES.items() for t in ts])
def test_narrative_text_that_follows_the_slot_grammar_and_the_numeral_ban_passes(stage, text):
    assert _api("narrative_problem")(text, stage) is None


@pytest.mark.parametrize("stage,text", [(s, t) for s, ts in NARRATIVE_THAT_FAILS.items() for t in ts])
def test_digits_outside_a_slot_and_a_bad_slot_are_problems(stage, text):
    assert _api("narrative_problem")(text, stage) is not None


def test_a_digit_inside_a_slot_argument_is_not_a_digit_outside_a_slot():
    assert _api("narrative_problem")("See {{ref:CWE-89}} only.", SCORER_STAGE) is None
    assert _api("narrative_problem")("See CWE-89 only.", SCORER_STAGE) is not None


NARRATIVE_FIELDS = ["rationale.cvss", "rationale.exploitability", "rationale.scalability", "rationale.reachability",
                    "metric_rationale.AV", "metric_rationale.AC", "metric_rationale.PR", "metric_rationale.UI",
                    "metric_rationale.S", "metric_rationale.C", "metric_rationale.I", "metric_rationale.A",
                    *["subscore_rationale.%s" % name for name in SUB_SCORES],
                    *["evidence.assessment.%s" % d for d in ("coverage", "configuration", "currency", "completeness")]]


@pytest.mark.parametrize("field", NARRATIVE_FIELDS)
def test_each_narrative_field_has_a_fixed_digit_free_fallback_sentence(field):
    sentence = _api("narrative_fallback")(field)
    assert isinstance(sentence, str) and sentence.strip()
    assert not any(ch.isnumeric() for ch in sentence)
    assert "{{" not in sentence
    assert sentence == _api("narrative_fallback")(field)


def test_a_fallback_for_a_name_that_is_not_a_narrative_field_is_refused():
    for field in ("finding_id", "cvss_vector", "evidence.summary", "evidence.0.summary", "matrix_row", "recommendation_body",
                  "evidence.0.assessment.coverage.rationale", "evidence.assessment", "bogus"):
        with pytest.raises((KeyError, ValueError)):
            _api("narrative_fallback")(field)


def part_with_narrative(text, field=("rationale", "exploitability"), ids=("S-1",)):
    return put(make_part(ids=ids), ("items", 0) + field, text)


@pytest.mark.parametrize("text", [
    "Public tooling exists for CVE-2024-1234.",       # digits outside a slot
    "The {{score:bogus}} value is high.",             # a slot whose argument does not resolve
    "Broken {{score:cvss_base and no end.",           # an unterminated slot
    "Reached through the OAuth2 gateway.",            # a digit-bearing component name written out
    "Uses TLS 1.3 on port 8080.",                     # a version and a port
])
def test_a_narrative_field_that_fails_step_11_takes_the_fixed_sentence_and_never_rejects_the_part(text):
    result = classify(part_with_narrative(text), ids=("S-1",))
    assert result.state == "done", result.detail
    stored = result.part["items"][0]["rationale"]["exploitability"]
    assert stored == _api("narrative_fallback")("rationale.exploitability")
    assert stored != text
    assert result.flags["S-1"] == ["input:rationale.exploitability:narrative-fallback"]
    assert result.counts["narrative_fallbacks"] == 1


def test_fields_that_pass_step_11_are_stored_with_their_slots_intact():
    part = part_with_narrative("Base {{score:cvss_base}}, band {{band:severity}}.")
    result = classify(part, ids=("S-1",))
    assert result.state == "done"
    assert result.part["items"][0]["rationale"]["exploitability"] == "Base {{score:cvss_base}}, band {{band:severity}}."
    assert result.flags.get("S-1", []) == []
    assert result.counts["narrative_fallbacks"] == 0


def test_each_failing_field_is_replaced_and_counted_on_its_own():
    part = make_part(ids=("S-1",))
    item = part["items"][0]
    item["rationale"]["cvss"] = "Score 9.8 is high."
    item["rationale"]["scalability"] = "Reaches {{score:nope}} hosts."
    item["metric_rationale"] = {"AV": "Over TLS 1.2.", "AC": "Simple to repeat."}
    item["subscore_rationale"] = {"skill_level": "Needs 2 years of practice."}
    result = classify(part, ids=("S-1",))
    assert result.state == "done"
    assert sorted(result.flags["S-1"]) == sorted([
        "input:rationale.cvss:narrative-fallback", "input:rationale.scalability:narrative-fallback",
        "input:metric_rationale.AV:narrative-fallback", "input:subscore_rationale.skill_level:narrative-fallback"])
    assert result.counts["narrative_fallbacks"] == 4
    assert result.part["items"][0]["metric_rationale"]["AC"] == "Simple to repeat."


def test_a_controls_assessment_rationale_is_narrative_and_takes_the_fallback():
    assessment = {d: {"rating": "High", "rationale": "Covers the main path."}
                  for d in ("coverage", "configuration", "currency", "completeness")}
    assessment["currency"]["rationale"] = "Patched in release 4."
    part = put(make_part(kind=CONTROLS, ids=("S-1",)), ("items", 0, "evidence", 0, "assessment"), assessment)
    result = classify(part, ids=("S-1",), kind=CONTROLS)
    assert result.state == "done"
    assert result.flags["S-1"] == ["input:evidence.assessment.currency:narrative-fallback"]


def test_a_structural_failure_still_rejects_even_when_a_narrative_field_would_fall_back():
    part = part_with_narrative("Score 9.8 is high.")
    part["items"][0]["extra"] = 1
    assert classify(part, ids=("S-1",)).state == "invalid"
    part = part_with_narrative("Score 9.8 is high.")
    part["items"][0]["exploitability"]["known_techniques"] = 11
    assert classify(part, ids=("S-1",)).state == "invalid"


def test_the_slot_kinds_of_the_other_stage_fall_back_in_this_stage():
    part = put(make_part(kind=CONTROLS, ids=("S-1",)), ("items", 0, "evidence", 0, "assessment"), {
        d: {"rating": "High", "rationale": "Ok {{name:zone}}."} for d in ("coverage", "configuration", "currency", "completeness")})
    result = classify(part, ids=("S-1",), kind=CONTROLS)
    assert result.state == "done"
    assert result.counts["narrative_fallbacks"] == 4


# --- the resolver: slots filled from computed values, never from the agent's text ---

def lookup_from(values):
    return lambda kind, arg: values.get((kind, arg))


def test_the_resolver_fills_each_slot_from_the_lookup_and_escapes_the_rest():
    values = {("score", "cvss_base"): "7.5", ("band", "severity"): "High"}
    text = "Base {{score:cvss_base}} puts it in {{band:severity}} <now> | later."
    out = _api("resolve_narrative")(text, SCORER_STAGE, lookup_from(values))
    assert out == "Base 7.5 puts it in High &lt;now&gt; &#124; later."


def test_a_slot_that_does_not_resolve_makes_the_whole_field_unresolved():
    assert _api("resolve_narrative")("Base {{score:cvss_base}}.", SCORER_STAGE, lookup_from({})) is None


def test_text_that_breaks_the_grammar_is_unresolved_and_never_raises():
    values = {("score", "cvss_base"): "7.5"}
    for text in ("Base {{score:cvss_base", "Port 8080", "{{pct:reduction}}"):
        assert _api("resolve_narrative")(text, SCORER_STAGE, lookup_from(values)) is None


def test_a_resolved_value_is_untrusted_text_and_is_escaped_and_never_resolved_again():
    values = {("name", "component"): "A|B <x> `y` {{score:cvss_base}}", ("score", "cvss_base"): "7.5"}
    out = _api("resolve_narrative")("Host {{name:component}}.", SCORER_STAGE, lookup_from(values))
    assert out == "Host A&#124;B &lt;x&gt; &#96;y&#96; &#123;&#123;score:cvss_base}}."
    assert "{{" not in out


def test_a_brace_pair_that_is_not_a_slot_is_escaped_on_output():
    out = _api("resolve_narrative")("Keep {{ braces }} plain.", SCORER_STAGE, lookup_from({}))
    assert out == "Keep &#123;&#123; braces }} plain."


# =============================================================================
# 11. Evidence fields and ``file`` values
# =============================================================================

def test_digits_and_any_text_are_allowed_in_evidence_fields_and_never_flagged():
    part = make_part(kind=CONTROLS, ids=("S-1",), items=[controls_item("S-1", "partial")])
    entry = part["items"][0]["evidence"][0]
    entry.update(summary="Line 42 of auth.py calls check() 3 times.", snippet="x = 1\nreturn 0x2A")
    part["items"][0]["matrix_row"] = "| S-1 | 9.8 | Critical |"
    result = classify(part, ids=("S-1",), kind=CONTROLS)
    assert result.state == "done"
    assert result.flags.get("S-1", []) == []
    assert result.counts["narrative_fallbacks"] == 0
    assert result.part["items"][0]["evidence"][0]["summary"] == "Line 42 of auth.py calls check() 3 times."


@pytest.mark.parametrize("field", ["summary", "snippet"])
def test_a_literal_double_brace_in_an_evidence_field_is_kept_as_text_for_the_renderer_to_escape(field):
    part = put(make_part(kind=CONTROLS, ids=("S-1",), items=[controls_item("S-1", "partial")]),
               ("items", 0, "evidence", 0, field), "{{7*7}} and {{score:inherent}}")
    result = classify(part, ids=("S-1",), kind=CONTROLS)
    assert result.state == "done"
    assert result.part["items"][0]["evidence"][0][field] == "{{7*7}} and {{score:inherent}}"
    assert result.counts["narrative_fallbacks"] == 0


EVIDENCE_FILES_REFUSED = [
    "https://example.test/x", "file:///etc/passwd", "javascript:alert", "/etc/passwd", "//host/x", "a\\b.py",
    "C:/Windows/x", "c:rel", "C:\\Windows\\x", "../x", "a/../b", "a/b/..", "a`b`", "a\x00b", "a\nb", "", ".",
]
EVIDENCE_FILES_ACCEPTED = ["src/a.py", "./src//a.py", "src/a:b.py", "docs/security/architecture.md", "src/\u00fcn\u00ef.py"]


@pytest.mark.parametrize("path", EVIDENCE_FILES_REFUSED)
def test_an_evidence_file_with_a_scheme_a_leading_slash_a_backslash_or_a_drive_letter_is_refused(path):
    part = put(make_part(kind=CONTROLS, ids=("S-1",)), ("items", 0, "evidence", 0, "file"), path)
    assert classify(part, ids=("S-1",), kind=CONTROLS).state == "invalid"


@pytest.mark.parametrize("path", EVIDENCE_FILES_ACCEPTED)
def test_a_relative_evidence_file_is_accepted_and_kept_as_written(path):
    part = put(make_part(kind=CONTROLS, ids=("S-1",)), ("items", 0, "evidence", 0, "file"), path)
    result = classify(part, ids=("S-1",), kind=CONTROLS)
    assert result.state == "done", result.detail
    assert result.part["items"][0]["evidence"][0]["file"] == path


def test_the_evidence_file_rule_is_the_identifier_slices_rule_not_a_second_copy():
    source = TACHI_PARTS_PATH.read_text(encoding="utf-8")
    assert source.count("def path_problem") == 1
    for path in EVIDENCE_FILES_REFUSED + EVIDENCE_FILES_ACCEPTED:
        refused = tachi_parts.path_problem(path) is not None
        part = put(make_part(kind=CONTROLS, ids=("S-1",)), ("items", 0, "evidence", 0, "file"), path)
        assert (classify(part, ids=("S-1",), kind=CONTROLS).state == "invalid") == refused, path


# =============================================================================
# 12. Per-sink escaping (ADR-050 D3, "Output")
#
# Markdown cells and prose use a closed set of numeric and named references that
# ``tachi_parsers`` decodes (F3). Code snippets are unescaped inside a longer fence.
# SARIF strings go through ``json.dumps`` only, so no helper here escapes them.
# =============================================================================

REFERENCES = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&#124;": "|", "&#96;": "`", "&#123;": "{", "&#10;": "\n", "&#35;": "#"}


def decode_references(text):
    """A test-local closed decoder: one pass, exactly the eight references."""
    return re.sub("|".join(re.escape(ref) for ref in REFERENCES), lambda m: REFERENCES[m.group(0)], text)


def test_the_escape_reference_set_is_closed():
    assert dict(_api("ESCAPE_REFERENCES")) == REFERENCES


@pytest.mark.parametrize("raw,escaped", [
    ("a & b", "a &amp; b"), ("<b>", "&lt;b&gt;"), ("a | b", "a &#124; b"), ("`code`", "&#96;code&#96;"),
    ("line one\nline two", "line one&#10;line two"), ("tab\there", "tab\there"), ("{{7*7}}", "&#123;&#123;7*7}}"),
    ("a { b } c", "a { b } c"), ("{{ x }}", "&#123;&#123; x }}"), ("{{{x}}}", "&#123;&#123;&#123;x}}}"), ("", ""),
    ("plain text 42", "plain text 42"),
])
def test_a_table_cell_escapes_the_closed_set(raw, escaped):
    assert _api("escape_cell")(raw) == escaped


def test_a_cell_never_holds_a_raw_pipe_backtick_angle_bracket_or_newline():
    hostile = "| x |\n# h\n```\n<script>&lt;</script>`|`"
    out = _api("escape_cell")(hostile)
    assert not any(ch in out for ch in "|`<>\n")
    assert decode_references(out) == hostile


def test_a_literal_reference_in_agent_text_survives_one_decode():
    """The round trip includes a literal ``&lt;``, so a double decode would fail it."""
    for raw in ("&lt;", "&amp;lt;", "&#124;", "&amp;#35;", "&#10;"):
        assert decode_references(_api("escape_cell")(raw)) == raw
        assert decode_references(_api("escape_prose")(raw)) == raw


def test_kept_slots_stay_literal_while_everything_else_is_escaped():
    text = "{{score:cvss_base}} {{ref:CWE-89}} {{7*7}} <b>"
    assert _api("escape_cell")(text, keep_slots=True) == "{{score:cvss_base}} {{ref:CWE-89}} &#123;&#123;7*7}} &lt;b&gt;"
    assert _api("escape_cell")(text) == "&#123;&#123;score:cvss_base}} &#123;&#123;ref:CWE-89}} &#123;&#123;7*7}} &lt;b&gt;"


@pytest.mark.parametrize("raw,escaped", [
    ("# Heading", "&#35; Heading"), ("## Two", "&#35;# Two"), ("   # indented", "   &#35; indented"),
    ("\t# tabbed", "\t&#35; tabbed"), ("issue #5 stays", "issue #5 stays"), ("| a | b |", "&#124; a &#124; b &#124;"),
    ("first\n# second\nthird", "first\n&#35; second\nthird"), ("```\n# h\n```", "&#96;&#96;&#96;\n&#35; h\n&#96;&#96;&#96;"),
    ("a\n\n# b", "a\n\n&#35; b"),
])
def test_prose_keeps_its_line_breaks_and_never_starts_a_line_with_a_hash_or_a_pipe(raw, escaped):
    assert _api("escape_prose")(raw) == escaped


def test_prose_cannot_forge_a_provenance_stamp_or_a_heading():
    forged = "<!-- tachi-provenance: renderer=x; version=1.0.0; input-digest=sha256:" + "0" * 64 + " -->\n# Forged"
    out = _api("escape_prose")(forged)
    assert _api("read_stamp")(out) is None
    assert not re.search(r"(?m)^\s*#", out)
    assert decode_references(out) == forged


def max_backtick_run(text):
    runs = re.findall(r"`+", text)
    return max((len(run) for run in runs), default=0)


@pytest.mark.parametrize("snippet,length", [
    ("no backticks", 3), ("one ` tick", 3), ("two `` ticks", 3), ("three ``` ticks", 4), ("four ```` ticks", 5),
    ("a ``` b ````` c `` d", 6), ("", 3), ("~~~ tildes ~~~", 3),
])
def test_a_snippet_fence_is_longer_than_its_longest_backtick_run(snippet, length):
    fence = _api("fence_for")(snippet)
    assert fence == "`" * length
    assert len(fence) > max_backtick_run(snippet)


def test_a_fenced_snippet_cannot_close_its_own_fence_early():
    snippet = "```\n## Forged\n| a | b |\n````\n`````"
    fence = _api("fence_for")(snippet)
    block = "%spython\n%s\n%s\n" % (fence, snippet, fence)
    closers = [line for line in block.splitlines() if line.strip() and set(line.strip()) == {"`"} and len(line.strip()) >= len(fence)]
    assert closers == [fence]


# =============================================================================
# 13. Guards, atomic write, digest, stamp and VERSION
# =============================================================================

def test_under_decides_containment_by_identity_not_by_spelling(tmp_path):
    under = _api("under")
    base = tmp_path / "out"
    (base / "a" / "b").mkdir(parents=True)
    alias = tmp_path / "alias"
    alias.symlink_to(base)
    assert under(base, base) is True
    assert under(base, base / "a" / "b") is True
    assert under(base, base / "a" / "new" / "deep" / "file.json") is True   # the tail does not exist yet
    assert under(alias, base / "a") is True                                  # a spelling of the same directory
    assert under(base, alias / "a") is True
    assert under(base, tmp_path) is False
    assert under(base, tmp_path / "other" / "f") is False
    assert under(base, tmp_path / "out-evil" / "f") is False                 # a string prefix is not containment
    assert under(base, base / ".." / "other") is False                       # a dot-dot component is never inside


def test_the_path_guard_names_the_first_problem_with_a_planned_part_path(tmp_path):
    problem = _api("path_guard_problem")
    out = tmp_path / "out"
    parts = out / ".tachi-build" / "risk-score" / PLAN / "parts"
    parts.mkdir(parents=True)
    good = parts / "B001.a1.json"
    assert problem(good, out) == "missing"
    good.write_text("{}", encoding="utf-8")
    assert problem(good, out) is None
    link = parts / "B001.a2.json"
    link.symlink_to(good)
    assert problem(link, out) == "symlink"
    (parts / "B002.a1.json").mkdir()
    assert problem(parts / "B002.a1.json", out) == "not-regular"
    assert problem(tmp_path / "stray.json", out) == "outside"
    real_parent = tmp_path / "real-parts"
    real_parent.mkdir()
    (real_parent / "B003.a1.json").write_text("{}", encoding="utf-8")
    (out / "linked").symlink_to(real_parent)
    assert problem(out / "linked" / "B003.a1.json", out) == "symlink"


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="needs POSIX named pipes")
def test_a_named_pipe_is_not_a_regular_file(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    os.mkfifo(str(out / "pipe.json"))
    assert _api("path_guard_problem")(out / "pipe.json", out) == "not-regular"


def test_the_path_guard_accepts_an_out_directory_that_is_itself_a_symlink(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    (real / "f.json").write_text("{}", encoding="utf-8")
    alias = tmp_path / "alias"
    alias.symlink_to(real)
    assert _api("path_guard_problem")(alias / "f.json", alias) is None


def test_atomic_write_replaces_the_file_whole_and_leaves_nothing_behind(tmp_path):
    write = _api("atomic_write")
    target = tmp_path / "risk-scores.md"
    target.write_text("old", encoding="utf-8")
    write(target, "new\nline\né")
    assert target.read_bytes() == "new\nline\né".encode("utf-8")
    write(target, b"\x00\x01bytes")
    assert target.read_bytes() == b"\x00\x01bytes"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["risk-scores.md"]


def test_atomic_write_stages_in_the_target_directory_and_cleans_up_when_the_replace_fails(tmp_path, monkeypatch):
    write = _api("atomic_write")
    target = tmp_path / "out.md"
    seen = []
    real_replace = os.replace

    def failing_replace(src, dst):
        seen.append((os.path.dirname(os.path.abspath(src)), os.path.dirname(os.path.abspath(dst))))
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", failing_replace)
    with pytest.raises(OSError):
        write(target, "data")
    monkeypatch.setattr(os, "replace", real_replace)
    assert seen and seen[0][0] == seen[0][1] == str(tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_atomic_write_fails_when_the_directory_is_missing_and_creates_nothing(tmp_path):
    with pytest.raises(OSError):
        _api("atomic_write")(tmp_path / "missing" / "f.md", "x")
    assert list(tmp_path.iterdir()) == []


def test_atomic_write_replaces_a_symlink_at_the_destination_without_following_it(tmp_path):
    victim = tmp_path / "victim.txt"
    victim.write_text("keep", encoding="utf-8")
    target = tmp_path / "out.md"
    target.symlink_to(victim)
    _api("atomic_write")(target, "new")
    assert victim.read_text(encoding="utf-8") == "keep"
    assert not target.is_symlink() and target.read_text(encoding="utf-8") == "new"


@pytest.mark.skipif(os.name != "posix", reason="POSIX permission bits")
def test_a_written_file_gets_the_modes_an_ordinary_write_would(tmp_path):
    previous = os.umask(0o022)
    try:
        _api("atomic_write")(tmp_path / "f.md", "x")
    finally:
        os.umask(previous)
    assert (tmp_path / "f.md").stat().st_mode & 0o777 == 0o644


def test_digests_are_lowercase_sha256_hex(tmp_path):
    abc = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert _api("sha256_hex")(b"abc") == abc
    path = tmp_path / "f"
    path.write_bytes(b"abc")
    assert _api("file_digest")(path) == abc
    path.write_bytes(b"abc" * 100000)
    assert _api("file_digest")(path) == _api("sha256_hex")(b"abc" * 100000)


def test_the_input_digest_is_the_sha256_of_canonical_json_and_ignores_key_order():
    digest = _api("input_digest")
    assert digest({"b": [1, 2], "a": 1}) == digest({"a": 1, "b": [1, 2]})
    assert digest({"a": 1, "b": [1, 2]}) == "sha256:" + _api("sha256_hex")(b'{"a":1,"b":[1,2]}')
    assert digest({"a": "é"}) == "sha256:" + _api("sha256_hex")(b'{"a":"\\u00e9"}')
    assert digest({"a": 1}) != digest({"a": 2})
    assert digest([1, 2]) != digest([2, 1])
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", digest({}))


DIGEST = "sha256:" + "ab" * 32


def test_the_stamp_has_d4s_exact_form_and_the_shipped_version():
    stamp = _api("stamp_comment")("render-risk-scores", DIGEST)
    assert stamp == "<!-- tachi-provenance: renderer=render-risk-scores; version=%s; input-digest=%s -->" % (
        _api("VERSION"), DIGEST)


@pytest.mark.parametrize("renderer,digest", [
    ("x --> <b>", DIGEST), ("", DIGEST), ("a" * 65, DIGEST), ("a b", DIGEST), ("r\n", DIGEST),
    ("render", "sha256:" + "AB" * 32), ("render", "sha256:" + "ab" * 31), ("render", "md5:" + "ab" * 16),
    ("render", DIGEST + "\n"), ("render", "-->"),
])
def test_a_stamp_cannot_carry_text_that_would_end_the_comment_or_break_the_form(renderer, digest):
    with pytest.raises(ValueError):
        _api("stamp_comment")(renderer, digest)


def test_the_last_provenance_comment_wins():
    stamp = _api("stamp_comment")
    first, second = stamp("render-risk-scores", DIGEST), stamp("populate-affected-assets", "sha256:" + "cd" * 32)
    read = _api("read_stamp")
    assert read("body\n" + first + "\n") == {"renderer": "render-risk-scores", "version": _api("VERSION"), "input_digest": DIGEST}
    assert read(first + "\nmore text\n" + second + "\n## Affected Assets\n")["renderer"] == "populate-affected-assets"
    assert read("no stamp here") is None
    assert read("") is None


def test_a_malformed_last_comment_is_no_stamp_and_never_falls_back_to_an_earlier_one():
    good = _api("stamp_comment")("render-risk-scores", DIGEST)
    assert _api("read_stamp")(good + "\n<!-- tachi-provenance: renderer=x; version=1.0; input-digest=nope -->\n") is None
    assert _api("read_stamp")(good + "\n<!-- tachi-provenance: renderer=x; version=%s; input-digest=%s" % (_api("VERSION"), DIGEST)) is None


def test_a_forged_stamp_in_a_fenced_snippet_before_the_real_stamp_does_not_win():
    forged = "<!-- tachi-provenance: renderer=evil; version=9.9.9; input-digest=sha256:" + "00" * 32 + " -->"
    real = _api("stamp_comment")("render-compensating-controls", DIGEST)
    text = "```text\n" + forged + "\n```\n\n" + real + "\n"
    assert _api("read_stamp")(text)["renderer"] == "render-compensating-controls"


def test_version_is_a_plain_release_triple_on_a_line_release_please_can_bump():
    version = _api("VERSION")
    assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version)
    source = TACHI_PARTS_PATH.read_text(encoding="utf-8")
    assert re.search(r'(?m)^VERSION = "[0-9]+\.[0-9]+\.[0-9]+"  # x-release-please-version$', source)
    assert len(re.findall(r"x-release-please-version", source)) == 1


# =============================================================================
# 14. Key sets, flag fields and the batch-plan documents (aligned with T006's
#     shared reference: part-file-contract-shared.md)
# =============================================================================

PART_KEYS = ["schema", "plan_id", "batch_id", "stage", "agent_type", "finding_ids", "items", "fragments"]
OVERFLOW_KEYS = ["schema", "plan_id", "batch_id", "stage", "agent_type", "reason"]
BATCH_INPUT_KEYS = ["schema", "plan_id", "batch_id", "stage", "agent_type", "finding_ids", "attempt", "part_path",
                    "tree_paths", "units", "refs", "params"]
PLAN_KEYS = ["schema", "plan_id", "stage", "agent_type", "created_utc", "tachi_version", "inputs", "refs",
             "architecture_warning", "params", "batch_size", "unit_count", "preimage", "out_snapshot", "retry_budget",
             "batches"]
POINTER_KEYS = ["schema", "plan_id"]
STAGE_RECORD_KEYS = ["schema", "stage", "plan_id", "status", "tachi_version", "started_utc", "finished_utc", "input_digest",
                     "counts", "batches", "overflow_events", "retries", "warnings", "undeclared_paths", "outputs", "error"]
PLAN_BATCH_KEYS = ["batch_id", "parent", "attempt", "finding_ids", "input_sha256", "state"]
ASSESSMENT_DIMENSIONS = ["coverage", "configuration", "currency", "completeness"]
METRICS = ["AV", "AC", "PR", "UI", "S", "C", "I", "A"]
COUNT_KEYS = {"units", "open", "resolved", "rendered", "parse_errors", "narrative_fallbacks", "truncations",
              "corrected", "unverifiable", "unchecked", "divergent", "override", "retagged", "reused-id", "input"}
EXPECTED_KEY_SETS = {
    "part": (PART_KEYS, []), "overflow": (OVERFLOW_KEYS, []), "batch-input": (BATCH_INPUT_KEYS, []),
    "plan": (PLAN_KEYS, []), "plan-pointer": (POINTER_KEYS, []), "stage-record": (STAGE_RECORD_KEYS, []),
    "scorer-item": (["finding_id", "cvss_vector", "exploitability", "scalability", "reachability", "rationale"],
                    ["metric_rationale", "subscore_rationale"]),
    "controls-item": (["finding_id", "control_status", "control_category", "confidence", "carried_forward", "evidence",
                       "matrix_row", "recommendation_body"], []),
    "exploitability": (SUB_SCORES[:4], []), "scalability": (SUB_SCORES[4:], []),
    "reachability": (["zone", "trust_level", "auth_barriers", "network_boundaries"], []),
    "rationale": (["cvss", "exploitability", "scalability", "reachability"], []),
    "evidence-entry": (["file", "line", "language", "snippet", "summary"], ["assessment"]),
    "assessment": (ASSESSMENT_DIMENSIONS, []), "assessment-dimension": (["rating", "rationale"], []),
    "plan-input": (["path", "sha256", "bytes"], []), "plan-batch": (PLAN_BATCH_KEYS, []),
    "retry-budget": (["limit", "used"], []),
    "stage-batches": (["planned", "dispatched", "done", "retried", "split", "exhausted"], []),
    "overflow-event": (["batch_id", "attempt", "kind"], []), "retry-entry": (["batch_id", "attempt", "cause", "children"], []),
    "warning": (["code", "detail"], []), "output": (["path", "sha256"], []),
    "error": (["code", "message", "batch_id", "finding_ids", "remedy"], []),
}


@pytest.mark.parametrize("name", sorted(EXPECTED_KEY_SETS))
def test_each_closed_key_set_is_the_contracts_table_in_the_contracts_order(name):
    required, optional = _api("KEY_SETS")[name]
    assert (list(required), list(optional)) == (EXPECTED_KEY_SETS[name][0], EXPECTED_KEY_SETS[name][1])


def test_the_key_set_table_names_nothing_else():
    assert set(_api("KEY_SETS")) == set(EXPECTED_KEY_SETS)


def test_the_enumerations_and_the_stage_table_match_the_contract():
    assert list(_api("SUBSCORE_NAMES")) == SUB_SCORES
    assert list(_api("METRIC_NAMES")) == METRICS
    assert list(_api("CONTROL_CATEGORIES")) == CONTROL_CATEGORIES
    assert set(_api("COUNT_KEYS")) == COUNT_KEYS
    assert dict(_api("STAGE_AGENTS")) == {"risk-score": "tachi-risk-scorer", "compensating-controls": "tachi-control-analyzer"}
    assert _api("MAX_PART_BYTES") == 512 * 1024
    assert _api("MAX_AGENT_INPUT_BYTES") == 16 * 1024 * 1024


def test_the_flag_fields_are_t006s_24_dotted_names_with_no_list_index():
    fields = list(_api("NARRATIVE_FIELDS"))
    assert fields == NARRATIVE_FIELDS
    assert len(fields) == len(set(fields)) == 24
    assert not any("[" in f or any(part.isdigit() for part in f.split(".")) for f in fields)


def test_a_flag_names_its_field_without_an_index_so_entries_share_one_flag_and_each_cut_is_counted():
    entries = [dict(controls_item()["evidence"][0], summary="s" * 200) for _ in range(2)]
    part = put(make_part(kind=CONTROLS, ids=("S-1",)), ("items", 0, "evidence"), entries)
    result = classify(part, ids=("S-1",), kind=CONTROLS)
    assert result.state == "done"
    assert result.flags["S-1"] == ["input:evidence.summary:truncated"]
    assert result.counts["truncations"] == 2


def test_items_come_back_in_the_planned_order_whatever_order_the_agent_wrote_them():
    part = make_part(ids=("T-2", "S-1"))
    result = classify(part, ids=("S-1", "T-2"))
    assert result.state == "done"
    assert result.part["finding_ids"] == ["S-1", "T-2"]
    assert [item["finding_id"] for item in result.part["items"]] == ["S-1", "T-2"]


def test_classifying_a_part_never_changes_the_object_it_was_given():
    part = make_part(ids=("S-01", "T-2"))
    before = json.dumps(part, sort_keys=True)
    result = classify(part, ids=("S-1", "T-2"))
    assert result.state == "done"
    assert json.dumps(part, sort_keys=True) == before


def test_a_planned_set_that_is_itself_hostile_is_invalid_not_a_crash():
    assert classify(make_part(), ids=("S-١", "T-2")).state == "invalid"
    assert classify(make_part(), ids=("S-1", "S-01")).state == "invalid"


HEX = "ab" * 32


def raises_invalid(validator, obj):
    with pytest.raises(_api("PartError")) as excinfo:
        validator(obj)
    assert excinfo.value.kind == "invalid"


def valid_plan():
    return {"schema": "tachi.plan/1", "plan_id": PLAN, "stage": "risk-score", "agent_type": "tachi-risk-scorer",
            "created_utc": "2026-11-22T10:15:00Z", "tachi_version": "4.48.4",
            "inputs": {"threats": {"path": "/work/run/threats.md", "sha256": HEX, "bytes": 1234}},
            "refs": {"threats": "/work/run/threats.md", "architecture": "/work/docs/architecture.md"},
            "architecture_warning": None,
            "params": {"scoring_date": "2026-11-22"}, "batch_size": 40, "unit_count": 3,
            "preimage": {"risk-scores.md": None, "risk-scores.sarif": HEX},
            "out_snapshot": {"threats.md": [1234, 1700000000000000000]}, "retry_budget": {"limit": 2, "used": 0},
            "batches": [{"batch_id": "B001", "parent": None, "attempt": 1, "finding_ids": ["S-1", "T-2", "R-3"],
                         "input_sha256": HEX, "state": "pending"}]}


PLAN_VIOLATIONS = {
    "unknown key": setter(("extra",), 1),
    **{"missing %s" % key: drop((key,)) for key in PLAN_KEYS},
    "schema version": setter(("schema",), "tachi.plan/2"),
    "plan id with a trailing newline": setter(("plan_id",), PLAN + "\n"),
    "stage unknown": setter(("stage",), "bogus"),
    "agent of the other stage": setter(("agent_type",), "tachi-control-analyzer"),
    "created not UTC": setter(("created_utc",), "2026-11-22T10:15:00+00:00"),
    "created with a space": setter(("created_utc",), "2026-11-22 10:15:00Z"),
    "created impossible month": setter(("created_utc",), "2026-13-01T00:00:00Z"),
    "created with a trailing newline": setter(("created_utc",), "2026-11-22T10:15:00Z\n"),
    "version short": setter(("tachi_version",), "4.48"),
    "version prefixed": setter(("tachi_version",), "v4.48.4"),
    "input entry unknown key": setter(("inputs", "threats", "mtime"), 1),
    "input entry missing digest": drop(("inputs", "threats", "sha256")),
    "input digest upper case": setter(("inputs", "threats", "sha256"), "AB" * 32),
    "input digest short": setter(("inputs", "threats", "sha256"), "ab" * 31),
    "input digest prefixed": setter(("inputs", "threats", "sha256"), "sha256:" + HEX),
    "input bytes negative": setter(("inputs", "threats", "bytes"), -1),
    "input bytes boolean": setter(("inputs", "threats", "bytes"), True),
    "input bytes float": setter(("inputs", "threats", "bytes"), 1.5),
    "input path with a backtick": setter(("inputs", "threats", "path"), "/work/`x`"),
    "input path with a dot-dot": setter(("inputs", "threats", "path"), "/work/../x"),
    "input path with a newline": setter(("inputs", "threats", "path"), "/work/a\nb"),
    "input name with a space": setter(("inputs",), {"a b": {"path": "/x", "sha256": HEX, "bytes": 1}}),
    # `refs` is the plan's own copy of the stage's pointers (ruled at W2): the batch input's rule, once more.
    "refs not an object": setter(("refs",), []), "refs null": setter(("refs",), None),
    "refs over 20 names": setter(("refs",), {"r%d" % n: "/work/x%d.md" % n for n in range(21)}),
    "refs name with a capital": setter(("refs",), {"Threats": "/work/run/threats.md"}),
    "refs name with a space": setter(("refs",), {"a b": "/work/run/threats.md"}),
    "ref relative": setter(("refs", "threats"), "run/threats.md"),
    "ref with a dot-dot": setter(("refs", "threats"), "/work/../x"),
    "ref with a backslash": setter(("refs", "threats"), "/work/a\\b"),
    "ref with a backtick": setter(("refs", "threats"), "/work/`x`"),
    "ref with a newline": setter(("refs", "threats"), "/work/a\nb"),
    "ref empty": setter(("refs", "threats"), ""), "ref not text": setter(("refs", "threats"), 7),
    # `architecture_warning` is null, or one warning under a stage record's entry rules.
    "warning a string": setter(("architecture_warning",), "architecture-path:explicit:missing"),
    "warning a list": setter(("architecture_warning",), []),
    "warning unknown key": setter(("architecture_warning",), {"code": "architecture-path:explicit:missing", "detail": "d", "level": 1}),
    "warning missing detail": setter(("architecture_warning",), {"code": "architecture-path:explicit:missing"}),
    "warning missing code": setter(("architecture_warning",), {"detail": "d"}),
    "warning code empty": setter(("architecture_warning",), {"code": "", "detail": "d"}),
    "warning code with a capital": setter(("architecture_warning",), {"code": "Architecture-path", "detail": "d"}),
    "warning code with a space": setter(("architecture_warning",), {"code": "architecture path", "detail": "d"}),
    "warning code over 64": setter(("architecture_warning",), {"code": "a" * 65, "detail": "d"}),
    "warning code with a trailing newline": setter(("architecture_warning",), {"code": "architecture-path:explicit:missing\n", "detail": "d"}),
    "warning code not text": setter(("architecture_warning",), {"code": 7, "detail": "d"}),
    "warning detail not text": setter(("architecture_warning",), {"code": "architecture-path:explicit:missing", "detail": None}),
    "warning detail over 500": setter(("architecture_warning",), {"code": "architecture-path:explicit:missing", "detail": "d" * 501}),
    "warning detail with a control character": setter(("architecture_warning",), {"code": "architecture-path:explicit:missing", "detail": "a\x00b"}),
    "warning detail with a bidi control": setter(("architecture_warning",), {"code": "architecture-path:explicit:missing", "detail": "a\u202eb"}),
    "params nested object": setter(("params", "scoring_date"), {"a": 1}),
    "params list": setter(("params", "extra"), [1]),
    "params key with a capital": setter(("params", "Bad"), 1),
    "scoring date impossible": setter(("params", "scoring_date"), "2026-02-30"),
    "scoring date with a newline": setter(("params", "scoring_date"), "2026-11-22\n"),
    "batch size zero": setter(("batch_size",), 0), "batch size 501": setter(("batch_size",), 501),
    "batch size boolean": setter(("batch_size",), True), "batch size float": setter(("batch_size",), 1.5),
    "batch size text": setter(("batch_size",), "40"),
    "unit count negative": setter(("unit_count",), -1), "unit count float": setter(("unit_count",), 1.5),
    "preimage digest bad": setter(("preimage", "risk-scores.md"), "xyz"),
    "preimage name with a dot-dot": setter(("preimage",), {"../x": None}),
    "preimage missing a canonical output": setter(("preimage",), {"risk-scores.md": None}),
    "preimage with another stage's output": setter(("preimage",), {"risk-scores.md": None, "risk-scores.sarif": None,
                                                                   "compensating-controls.md": None}),
    "preimage empty": setter(("preimage",), {}),
    "snapshot entry short": setter(("out_snapshot", "threats.md"), [1]),
    "snapshot entry long": setter(("out_snapshot", "threats.md"), [1, 2, 3]),
    "snapshot entry text": setter(("out_snapshot", "threats.md"), ["a", 1]),
    "snapshot entry negative": setter(("out_snapshot", "threats.md"), [-1, 1]),
    "snapshot key with a dot-dot": setter(("out_snapshot",), {"../x": [1, 1]}),
    "snapshot key absolute": setter(("out_snapshot",), {"/x": [1, 1]}),
    "snapshot over 20000 entries": setter(("out_snapshot",), {"f%d" % n: [1, 1] for n in range(20001)}),
    "budget unknown key": setter(("retry_budget", "spent"), 1),
    "budget missing used": drop(("retry_budget", "used")),
    "budget negative": setter(("retry_budget", "limit"), -1),
    "budget float": setter(("retry_budget", "used"), 0.5),
    "batches not a list": setter(("batches",), {}),
    "batch unknown key": setter(("batches", 0, "extra"), 1),
    **{"batch missing %s" % key: drop(("batches", 0, key)) for key in PLAN_BATCH_KEYS},
    "batch id short": setter(("batches", 0, "batch_id"), "B01"),
    "batch id with a newline": setter(("batches", 0, "batch_id"), "B001\n"),
    "batch parent on a root": setter(("batches", 0, "parent"), "B000"),
    "batch attempt zero": setter(("batches", 0, "attempt"), 0), "batch attempt four": setter(("batches", 0, "attempt"), 4),
    "batch attempt boolean": setter(("batches", 0, "attempt"), True),
    "batch state unknown": setter(("batches", 0, "state"), "running"),
    "batch ids empty": setter(("batches", 0, "finding_ids"), []),
    "batch ids duplicate": setter(("batches", 0, "finding_ids"), ["S-1", "S-1"]),
    "batch ids two spellings": setter(("batches", 0, "finding_ids"), ["S-1", "S-01"]),
    "batch id hostile": setter(("batches", 0, "finding_ids"), ["S-١"]),
    "batch ids over 500": setter(("batches", 0, "finding_ids"), ["S-%d" % n for n in range(1, 502)]),
    "batch digest bad": setter(("batches", 0, "input_sha256"), "ab"),
}


def test_a_plan_that_follows_the_contract_validates_and_comes_back_as_it_was():
    plan = valid_plan()
    assert _api("validate_plan")(plan) is plan
    plan.update(out_snapshot=None, batch_size=None, unit_count=0, batches=[])   # a plan with no units
    assert _api("validate_plan")(plan) is plan


def test_a_plan_with_no_units_keeps_its_pointers_and_may_carry_the_architecture_warning():
    """Ruled at W2: ``refs`` and ``architecture_warning`` are plan-level, so an all-carried run (no batch input) still has them."""
    plan = valid_plan()
    plan.update(out_snapshot=None, batch_size=None, unit_count=0, batches=[],
                refs={name: "/work/%s" % name for name in ("threats", "risk_scores", "baseline_dir", "architecture", "target")},
                architecture_warning={"code": "architecture-path:explicit:outside-root", "detail": "d" * 500})
    assert _api("validate_plan")(plan) is plan


def test_the_pointers_and_the_warning_of_a_plan_have_the_limits_of_a_batch_input_and_a_stage_record():
    plan = valid_plan()
    plan["refs"] = {"r%d" % n: "/work/x%d.md" % n for n in range(20)}
    assert _api("validate_plan")(plan) is plan, "twenty pointer names is the limit"
    plan["refs"] = {}
    assert _api("validate_plan")(plan) is plan, "which names the planner writes is the planner's rule, not the schema's"
    plan["architecture_warning"] = {"code": "a" * 64, "detail": ""}
    assert _api("validate_plan")(plan) is plan, "a code of 1 to 64 characters, and a detail of 0 to 500"


@pytest.mark.parametrize("refs,valid", [
    ({"threats": "/work/run/threats.md", "architecture": "/work/docs/a.md"}, True), ({}, True),
    ({"threats": "run/threats.md"}, False), ({"threats": "/work/../x"}, False), ({"Threats": "/work/x"}, False),
    ({"threats": "/work/a\\b"}, False), ({"threats": 7}, False), (["/work/x"], False),
], ids=["good", "empty", "relative", "dot-dot", "capital", "backslash", "not-text", "not-an-object"])
def test_a_plan_and_its_batch_inputs_apply_one_rule_to_refs(refs, valid):
    plan, batch_input = valid_plan(), valid_batch_input()
    plan["refs"] = batch_input["refs"] = refs
    for validator, document in ((_api("validate_plan"), plan), (_api("validate_batch_input"), batch_input)):
        if valid:
            assert validator(document) is document
        else:
            raises_invalid(validator, document)


@pytest.mark.parametrize("label", sorted(PLAN_VIOLATIONS))
def test_a_plan_that_breaks_the_closed_schema_is_invalid(label):
    plan = valid_plan()
    PLAN_VIOLATIONS[label](plan)
    raises_invalid(_api("validate_plan"), plan)


def test_a_split_batch_and_its_children_are_one_valid_lineage():
    plan = valid_plan()
    root = dict(plan["batches"][0], state="split")
    plan["batches"] = [root, dict(root, batch_id="B001-1", parent="B001", state="pending", finding_ids=["S-1"]),
                       dict(root, batch_id="B001-2", parent="B001", state="pending", finding_ids=["T-2", "R-3"]),
                       dict(root, batch_id="B001-1-1", parent="B001-1", state="done", finding_ids=["S-1"], attempt=3)]
    assert _api("validate_plan")(plan) is plan


@pytest.mark.parametrize("label,batches", [
    ("duplicate batch ids", lambda b: [b, dict(b)]),
    ("a child whose parent is absent", lambda b: [dict(b, batch_id="B001-1", parent="B001")]),
    ("a child naming the wrong parent", lambda b: [b, dict(b, batch_id="B002"), dict(b, batch_id="B001-1", parent="B002")]),
    ("a child with no parent", lambda b: [b, dict(b, batch_id="B001-1", parent=None)]),
])
def test_the_batches_of_a_plan_must_agree_about_their_lineage(label, batches):
    plan = valid_plan()
    plan["batches"] = batches(plan["batches"][0])
    raises_invalid(_api("validate_plan"), plan)


def test_the_plan_pointer_has_two_keys():
    pointer = {"schema": "tachi.plan-pointer/1", "plan_id": PLAN}
    assert _api("validate_pointer")(pointer) is pointer
    for bad in ({"schema": "tachi.plan-pointer/1"}, {"plan_id": PLAN}, dict(pointer, extra=1),
                dict(pointer, schema="tachi.plan-pointer/2"), dict(pointer, plan_id=PLAN + "\n"),
                dict(pointer, plan_id="20261122T101500Z-0123456789AB"), dict(pointer, plan_id=None), {}):
        raises_invalid(_api("validate_pointer"), bad)


def valid_batch_input(kind=SCORER, batch="B001", attempt=1, ids=("S-1", "T-2")):
    return {"schema": "tachi.batch-input/1", "plan_id": PLAN, "batch_id": batch, "stage": kind["stage"],
            "agent_type": kind["agent_type"], "finding_ids": list(ids), "attempt": attempt,
            "part_path": "/work/out/.tachi-build/%s/%s/parts/%s.a%d.json" % (kind["stage"], PLAN, batch, attempt),
            "tree_paths": {}, "units": [{"finding_id": i, "component": "API Gateway"} for i in ids],
            "refs": {"threats": "/work/run/threats.md"}, "params": {"scoring_date": "2026-11-22"}}


BATCH_INPUT_VIOLATIONS = {
    "unknown key": setter(("extra",), 1),
    **{"missing %s" % key: drop((key,)) for key in BATCH_INPUT_KEYS},
    "schema version": setter(("schema",), "tachi.batch-input/2"),
    "plan id bad": setter(("plan_id",), "x"), "batch id bad": setter(("batch_id",), "B1"),
    "stage unknown": setter(("stage",), "bogus"),
    "agent of the other stage": setter(("agent_type",), "tachi-control-analyzer"),
    "ids empty": setter(("finding_ids",), []), "ids duplicate": setter(("finding_ids",), ["S-1", "S-1"]),
    "ids two spellings": setter(("finding_ids",), ["S-1", "S-01"]), "id hostile": setter(("finding_ids",), ["S-1\n"]),
    "attempt zero": setter(("attempt",), 0), "attempt four": setter(("attempt",), 4), "attempt boolean": setter(("attempt",), True),
    "part path relative": setter(("part_path",), "out/parts/B001.a1.json"),
    "part path of another plan": setter(("part_path",), "/work/out/.tachi-build/risk-score/%s/parts/B001.a1.json" % OTHER_PLAN),
    "part path of another batch": setter(("part_path",), "/work/out/.tachi-build/risk-score/%s/parts/B002.a1.json" % PLAN),
    "part path of another attempt": setter(("part_path",), "/work/out/.tachi-build/risk-score/%s/parts/B001.a2.json" % PLAN),
    "part path outside the parts directory": setter(("part_path",), "/work/out/.tachi-build/risk-score/%s/inputs/B001.a1.json" % PLAN),
    "part path with a dot-dot": setter(("part_path",), "/work/../out/.tachi-build/risk-score/%s/parts/B001.a1.json" % PLAN),
    "part path with a newline": setter(("part_path",), "/work/out/\n/%s/parts/B001.a1.json" % PLAN),
    "part path not text": setter(("part_path",), None),
    "tree paths filled outside the trees stage": setter(("tree_paths",), {"S-1": "/work/out/trees/S-1.md"}),
    "units not a list": setter(("units",), {}), "unit not an object": setter(("units",), ["S-1"]),
    "units over 500": setter(("units",), [{}] * 501),
    "ref relative": setter(("refs", "threats"), "run/threats.md"), "ref with a dot-dot": setter(("refs", "threats"), "/work/../x"),
    "ref name with a capital": setter(("refs",), {"Threats": "/work/run/threats.md"}),
    "ref not text": setter(("refs", "threats"), 7), "refs not an object": setter(("refs",), []),
    "params nested object": setter(("params", "scoring_date"), {}), "scoring date impossible": setter(("params", "scoring_date"), "2026-00-10"),
}


def test_a_batch_input_that_follows_the_contract_validates_for_both_stages_and_every_attempt():
    for kind in (SCORER, CONTROLS):
        for attempt in (1, 2, 3):
            data = valid_batch_input(kind, attempt=attempt)
            assert _api("validate_batch_input")(data) is data
    data = valid_batch_input(batch="B003-1-2")
    assert _api("validate_batch_input")(data) is data


@pytest.mark.parametrize("label", sorted(BATCH_INPUT_VIOLATIONS))
def test_a_batch_input_that_breaks_the_closed_schema_is_invalid(label):
    data = valid_batch_input()
    BATCH_INPUT_VIOLATIONS[label](data)
    raises_invalid(_api("validate_batch_input"), data)


def valid_stage_record():
    return {"schema": "tachi.stage-record/1", "stage": "risk-score", "plan_id": PLAN, "status": "success",
            "tachi_version": "4.48.4", "started_utc": "2026-11-22T10:15:00Z", "finished_utc": "2026-11-22T10:16:30Z",
            "input_digest": "sha256:" + HEX,
            "counts": {"units": 3, "open": 3, "resolved": 0, "rendered": 3, "parse_errors": 0, "narrative_fallbacks": 1,
                       "truncations": 0, "retagged": 0, "reused-id": 0},
            "batches": {"planned": 1, "dispatched": 1, "done": 1, "retried": 0, "split": 0, "exhausted": 0},
            "overflow_events": [{"batch_id": "B001", "attempt": 1, "kind": "missing"}],
            "retries": [{"batch_id": "B001", "attempt": 1, "cause": "missing", "children": ["B001-1", "B001-2"]}],
            "warnings": [{"code": "undeclared-paths", "detail": "one path"}], "undeclared_paths": ["gen.py"],
            "outputs": [{"path": "risk-scores.md", "sha256": HEX}], "error": None}


STAGE_RECORD_VIOLATIONS = {
    "unknown key": setter(("extra",), 1),
    **{"missing %s" % key: drop((key,)) for key in STAGE_RECORD_KEYS},
    "schema version": setter(("schema",), "tachi.stage-record/2"), "stage unknown": setter(("stage",), "bogus"),
    "plan id bad": setter(("plan_id",), "x"), "status unknown": setter(("status",), "ok"),
    "version bad": setter(("tachi_version",), "4.48"), "start not UTC": setter(("started_utc",), "2026-11-22T10:15:00+00:00"),
    "finish impossible": setter(("finished_utc",), "2026-11-31T10:15:00Z"),
    "digest unprefixed": setter(("input_digest",), HEX), "digest upper case": setter(("input_digest",), "sha256:" + HEX.upper()),
    "digest with a newline": setter(("input_digest",), "sha256:" + HEX + "\n"),
    "count key unknown": setter(("counts", "widgets"), 1), "count negative": setter(("counts", "units"), -1),
    "count float": setter(("counts", "units"), 1.5), "count boolean": setter(("counts", "units"), True),
    "count text": setter(("counts", "units"), "3"), "counts not an object": setter(("counts",), [3]),
    "batches unknown key": setter(("batches", "failed"), 0), "batches missing key": drop(("batches", "split")),
    "batches negative": setter(("batches", "planned"), -1),
    "overflow event unknown kind": setter(("overflow_events", 0, "kind"), "stalled"),
    "overflow event attempt zero": setter(("overflow_events", 0, "attempt"), 0),
    "overflow event batch id bad": setter(("overflow_events", 0, "batch_id"), "B1"),
    "overflow event unknown key": setter(("overflow_events", 0, "note"), "x"),
    "retry children not a list": setter(("retries", 0, "children"), "B001-1"),
    "retry child id bad": setter(("retries", 0, "children"), ["B1"]),
    "retry over two children": setter(("retries", 0, "children"), ["B001-1", "B001-2", "B001-1"]),
    "retry cause with a space": setter(("retries", 0, "cause"), "not found"),
    "warning detail over 500": setter(("warnings", 0, "detail"), "d" * 501),
    "warning detail with a control character": setter(("warnings", 0, "detail"), "a\x00b"),
    "warning unknown key": setter(("warnings", 0, "level"), "high"),
    "warning code with a capital": setter(("warnings", 0, "code"), "Undeclared-paths"),
    "warning code empty": setter(("warnings", 0, "code"), ""), "warning code over 64": setter(("warnings", 0, "code"), "a" * 65),
    "undeclared path with a dot-dot": setter(("undeclared_paths",), ["../x"]),
    "undeclared paths over 1000": setter(("undeclared_paths",), ["f%d.py" % n for n in range(1001)]),
    "undeclared path absolute": setter(("undeclared_paths",), ["/etc/x"]),
    "output digest bad": setter(("outputs", 0, "sha256"), "zz"),
    "output path with a dot-dot": setter(("outputs", 0, "path"), "../x"),
    "error not null or an object": setter(("error",), "failed"),
    "error unknown key": setter(("error",), {"code": "x", "message": "m", "batch_id": None, "finding_ids": [], "remedy": "r", "extra": 1}),
    "error missing key": setter(("error",), {"code": "x", "message": "m", "batch_id": None, "finding_ids": []}),
    "error batch id bad": setter(("error",), {"code": "x", "message": "m", "batch_id": "B1", "finding_ids": [], "remedy": "r"}),
    "error id hostile": setter(("error",), {"code": "x", "message": "m", "batch_id": None, "finding_ids": ["S-١"], "remedy": "r"}),
    "error message with a bidi control": setter(("error",), {"code": "x", "message": "a‮b", "batch_id": None, "finding_ids": [], "remedy": "r"}),
}


def test_a_stage_record_that_follows_the_contract_validates_for_every_status():
    for stage in ("risk-score", "compensating-controls"):
        record = dict(valid_stage_record(), stage=stage)
        assert _api("validate_stage_record")(record) is record
    failed = dict(valid_stage_record(), status="failed", error={
        "code": "unrecoverable-batch", "message": "Batch B001 ran out of retries.", "batch_id": "B001",
        "finding_ids": ["S-1", "T-2"], "remedy": "Re-run the command.", })
    assert _api("validate_stage_record")(failed) is failed
    warned = dict(valid_stage_record(), status="success-with-warnings")
    assert _api("validate_stage_record")(warned) is warned


@pytest.mark.parametrize("kind", sorted(COUNT_KEYS))
def test_every_count_key_the_contract_names_is_accepted(kind):
    record = valid_stage_record()
    record["counts"] = {kind: 2}
    assert _api("validate_stage_record")(record) is record


@pytest.mark.parametrize("label", sorted(STAGE_RECORD_VIOLATIONS))
def test_a_stage_record_that_breaks_the_closed_schema_is_invalid(label):
    record = valid_stage_record()
    STAGE_RECORD_VIOLATIONS[label](record)
    raises_invalid(_api("validate_stage_record"), record)


# --- reading a document from disk: the same loader as a part, then the schema's own key set ---

DOCUMENTS = [
    ("tachi.plan/1", "validate_plan", valid_plan),
    ("tachi.plan-pointer/1", "validate_pointer", lambda: {"schema": "tachi.plan-pointer/1", "plan_id": PLAN}),
    ("tachi.batch-input/1", "validate_batch_input", valid_batch_input),
    ("tachi.stage-record/1", "validate_stage_record", valid_stage_record),
]


def document_path(tmp_path, name="doc.json"):
    out = tmp_path / "out"
    build = out / ".tachi-build" / "risk-score"
    build.mkdir(parents=True, exist_ok=True)
    return out, build / name


@pytest.mark.parametrize("schema,validator,build", DOCUMENTS, ids=[d[0] for d in DOCUMENTS])
def test_a_document_is_read_through_the_loader_and_its_own_validator(tmp_path, schema, validator, build):
    out, path = document_path(tmp_path)
    path.write_text(json.dumps(build()), encoding="utf-8")
    assert _api("read_document")(path, out, schema) == build()
    other = next(d[0] for d in DOCUMENTS if d[0] != schema)
    with pytest.raises(_api("PartError")) as excinfo:
        _api("read_document")(path, out, other)
    assert excinfo.value.kind == "invalid"


@pytest.mark.parametrize("schema,validator,build", DOCUMENTS, ids=[d[0] for d in DOCUMENTS])
def test_a_document_that_fails_the_loader_reports_the_loaders_kind(tmp_path, schema, validator, build):
    read, error = _api("read_document"), _api("PartError")
    out, path = document_path(tmp_path)
    with pytest.raises(error) as missing:
        read(path, out, schema)
    assert missing.value.kind == "missing"
    text = json.dumps(build())
    path.write_text(text[:-1] + ', "schema": "x"}', encoding="utf-8")   # a duplicate key
    with pytest.raises(error) as duplicate:
        read(path, out, schema)
    assert duplicate.value.kind == "unparseable"
    real = tmp_path / "real.json"
    real.write_text(json.dumps(build()), encoding="utf-8")
    path.unlink()
    path.symlink_to(real)
    with pytest.raises(error) as linked:
        read(path, out, schema)
    assert linked.value.kind == "invalid"


def test_the_pointer_has_a_small_size_cap_and_the_plan_a_large_one(tmp_path):
    read, error = _api("read_document"), _api("PartError")
    out, path = document_path(tmp_path)
    pointer = json.dumps({"schema": "tachi.plan-pointer/1", "plan_id": PLAN}) + " " * 5000
    path.write_text(pointer, encoding="utf-8")
    with pytest.raises(error) as excinfo:
        read(path, out, "tachi.plan-pointer/1")
    assert excinfo.value.kind == "unparseable"
    plan = valid_plan()
    plan["out_snapshot"] = {"dir/file-%05d.txt" % n: [1, 1] for n in range(20000)}
    path.write_text(json.dumps(plan), encoding="utf-8")
    assert read(path, out, "tachi.plan/1")["unit_count"] == 3


def test_a_document_schema_that_is_not_one_of_the_four_is_refused(tmp_path):
    out, path = document_path(tmp_path)
    path.write_text("{}", encoding="utf-8")
    for schema in ("tachi.part/1", "tachi.overflow/1", "tachi.unknown/1", None):
        with pytest.raises((ValueError, KeyError)):
            _api("read_document")(path, out, schema)


# =============================================================================
# 15. Two cases the mutation check showed were not pinned
# =============================================================================

def test_a_spare_duplicate_in_finding_ids_is_invalid_even_when_the_items_are_one_per_planned_id():
    part = make_part(ids=("S-1", "T-2"))
    part["finding_ids"] = ["S-1", "S-01", "T-2"]
    assert classify(part, ids=("S-1", "T-2")).state == "invalid"
    part["finding_ids"] = ["S-1", "T-2", "T-2"]
    assert classify(part, ids=("S-1", "T-2")).state == "invalid"


def test_step_10_judges_the_text_that_is_left_after_step_9s_cut():
    """Decision for the architect (ADR-050 D3 lists the cut as step 9 and the characters as step 10).

    A hostile character beyond the cut is cut away with the rest of the over-limit prose, and one inside
    the kept text rejects the part. Run in the other order, the first would reject a part that RR2 says
    to cut.
    """
    beyond = "a" * 400 + "‮" + "b" * 50
    result = classify(with_text(SCORER, ("rationale", "cvss"), beyond), ids=("S-1",))
    assert result.state == "done"
    assert result.part["items"][0]["rationale"]["cvss"] == "a" * 400
    inside = "a" * 399 + "‮" + "b" * 50
    assert classify(with_text(SCORER, ("rationale", "cvss"), inside), ids=("S-1",)).state == "invalid"


# =============================================================================
# 16. D3's layout (P-6): the path builders every script shares
#
# Only the planner and the reconciler compute paths, and each recomputes them from --out, the stage, and
# plan and batch IDs that pass the allow-lists. Builders return absolute paths as text and raise
# ValueError for an argument that is not allow-listed, so no hostile ID ever becomes part of a path.
# =============================================================================

LAYOUT_NAMES = ["stage_dir", "pointer_path", "plan_dir", "plan_subdir", "plan_path", "input_path", "part_path",
                "stage_record_path", "preimage_path", "staged_path", "failed_path"]


def test_the_layout_builders_follow_d3s_table(tmp_path):
    out = str(tmp_path / "out")
    stage_base = os.path.join(out, ".tachi-build", "risk-score")
    plan = os.path.join(stage_base, PLAN)
    assert _api("BUILD_DIR") == ".tachi-build"
    assert _api("stage_dir")(out, "risk-score") == stage_base
    assert _api("pointer_path")(out, "risk-score") == os.path.join(stage_base, "current.json")
    assert _api("plan_dir")(out, "risk-score", PLAN) == plan
    assert _api("plan_path")(out, "risk-score", PLAN) == os.path.join(plan, "plan.json")
    assert _api("stage_record_path")(out, "risk-score", PLAN) == os.path.join(plan, "stage-record.json")
    assert _api("input_path")(out, "risk-score", PLAN, "B003-1") == os.path.join(plan, "inputs", "B003-1.json")
    assert _api("part_path")(out, "risk-score", PLAN, "B003-1", 2) == os.path.join(plan, "parts", "B003-1.a2.json")
    assert _api("preimage_path")(out, "risk-score", PLAN, "risk-scores.md") == os.path.join(plan, "preimage", "risk-scores.md")
    assert _api("staged_path")(out, "risk-score", PLAN, "risk-scores.sarif") == os.path.join(plan, "staged", "risk-scores.sarif")
    assert _api("failed_path")(out, "risk-score", PLAN, "risk-scores.md") == os.path.join(plan, "failed", "risk-scores.md")


def test_the_subdirectories_are_a_closed_list_and_the_file_builders_sit_in_them(tmp_path):
    out = str(tmp_path / "out")
    assert tuple(_api("PLAN_SUBDIRS")) == ("inputs", "parts", "preimage", "staged", "failed")
    plan = os.path.join(out, ".tachi-build", "compensating-controls", PLAN)
    for name in _api("PLAN_SUBDIRS"):
        assert _api("plan_subdir")(out, "compensating-controls", PLAN, name) == os.path.join(plan, name)
    for bad in ("checks", "trees", "..", "", "parts/..", "Parts", None, 1):
        with pytest.raises(ValueError):
            _api("plan_subdir")(out, "compensating-controls", PLAN, bad)


def test_the_controls_stage_uses_its_own_directory_and_canonical_names(tmp_path):
    out = str(tmp_path / "out")
    plan = os.path.join(out, ".tachi-build", "compensating-controls", PLAN)
    assert _api("plan_path")(out, "compensating-controls", PLAN) == os.path.join(plan, "plan.json")
    assert _api("staged_path")(out, "compensating-controls", PLAN, "compensating-controls.md") == \
        os.path.join(plan, "staged", "compensating-controls.md")
    assert _api("failed_path")(out, "compensating-controls", PLAN, "compensating-controls.sarif") == \
        os.path.join(plan, "failed", "compensating-controls.sarif")


def test_builders_return_absolute_text_whatever_form_out_arrives_in(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    expected = os.path.join(str(tmp_path), "out", ".tachi-build", "risk-score", PLAN, "parts", "B001.a1.json")
    for out in ("out", "./out", str(tmp_path / "out"), tmp_path / "out", Path("out")):
        built = _api("part_path")(out, "risk-score", PLAN, "B001", 1)
        assert isinstance(built, str) and os.path.isabs(built)
        assert os.path.realpath(built) == os.path.realpath(expected)


@pytest.mark.parametrize("label,call", [
    ("plan id with a trailing newline", lambda f: f("out", "risk-score", PLAN + "\n")),
    ("plan id in upper case", lambda f: f("out", "risk-score", "20261122T101500Z-0123456789AB")),
    ("plan id that climbs", lambda f: f("out", "risk-score", "../" + PLAN)),
    ("plan id empty", lambda f: f("out", "risk-score", "")),
    ("plan id not text", lambda f: f("out", "risk-score", None)),
    ("stage unknown", lambda f: f("out", "bogus", PLAN)),
    ("stage that climbs", lambda f: f("out", "../risk-score", PLAN)),
    ("stage not shipped yet", lambda f: f("out", "trees", PLAN)),
    ("stage not text", lambda f: f("out", None, PLAN)),
])
@pytest.mark.parametrize("name", ["plan_dir", "plan_path", "stage_record_path"])
def test_a_builder_refuses_a_plan_or_stage_that_is_not_allow_listed(label, call, name):
    with pytest.raises(ValueError):
        call(_api(name))


@pytest.mark.parametrize("batch", ["B1", "B001\n", "../B001", "B001/../B002", "b001", "", None, 1, "B001-3", "B００１"])
def test_a_builder_refuses_a_batch_id_that_is_not_allow_listed(batch):
    with pytest.raises(ValueError):
        _api("input_path")("out", "risk-score", PLAN, batch)
    with pytest.raises(ValueError):
        _api("part_path")("out", "risk-score", PLAN, batch, 1)


@pytest.mark.parametrize("attempt", [0, 4, -1, True, False, "1", 1.0, None, 2.5])
def test_a_builder_refuses_an_attempt_outside_one_to_three(attempt):
    with pytest.raises(ValueError):
        _api("part_path")("out", "risk-score", PLAN, "B001", attempt)


@pytest.mark.parametrize("name", ["../risk-scores.md", "risk-scores.md\n", "threats.md", "other.md", "risk-scores.md/..",
                                  "compensating-controls.md", "", None, "/etc/passwd", "RISK-SCORES.MD"])
@pytest.mark.parametrize("builder", ["preimage_path", "staged_path", "failed_path"])
def test_a_file_builder_takes_only_the_stages_canonical_output_names(builder, name):
    with pytest.raises(ValueError):
        _api(builder)("out", "risk-score", PLAN, name)


def test_an_empty_or_unusable_out_is_refused_rather_than_read_as_the_working_directory():
    for out in ("", None, 5, "bad\x00out"):
        with pytest.raises((ValueError, TypeError)):
            _api("plan_path")(out, "risk-score", PLAN)


def test_the_builders_agree_with_the_validators_about_the_layout():
    """A batch input written with ``part_path`` passes ``validate_batch_input``, for every batch shape and attempt."""
    for batch in ("B001", "B012", "B003-1", "B003-2-1"):
        for attempt in (1, 2, 3):
            data = valid_batch_input(batch=batch, attempt=attempt)
            data["part_path"] = _api("part_path")("/work/out", "risk-score", PLAN, batch, attempt)
            assert _api("validate_batch_input")(data) is data
    assert _api("part_path")("/work/out", "risk-score", PLAN, "B001", 1) == valid_batch_input()["part_path"]


def test_every_file_the_builders_name_round_trips_through_the_loader_and_the_readers(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    for sub in _api("PLAN_SUBDIRS"):
        os.makedirs(_api("plan_subdir")(out, "risk-score", PLAN, sub))
    write = _api("atomic_write")
    documents = [
        (_api("pointer_path")(out, "risk-score"), "tachi.plan-pointer/1", {"schema": "tachi.plan-pointer/1", "plan_id": PLAN}),
        (_api("plan_path")(out, "risk-score", PLAN), "tachi.plan/1", valid_plan()),
        (_api("input_path")(out, "risk-score", PLAN, "B001"), "tachi.batch-input/1",
         dict(valid_batch_input(), part_path=_api("part_path")(out, "risk-score", PLAN, "B001", 1))),
        (_api("stage_record_path")(out, "risk-score", PLAN), "tachi.stage-record/1", valid_stage_record()),
    ]
    for path, schema, document in documents:
        write(path, json.dumps(document))
        assert _api("read_document")(path, out, schema) == document, schema
    part = make_part()
    write(_api("part_path")(out, "risk-score", PLAN, "B001", 1), json.dumps(part))
    result = _api("read_part")(_api("part_path")(out, "risk-score", PLAN, "B001", 1), out, **expect())
    assert result.state == "done", result.detail


def test_the_module_docstring_names_every_builder_and_every_io_helper():
    doc = tachi_parts.__doc__
    for name in LAYOUT_NAMES + ["atomic_write", "sha256_hex", "file_digest", "input_digest", "stamp_comment", "read_stamp",
                                "VERSION", "BUILD_DIR", "PLAN_SUBDIRS"]:
        assert name in doc, name


# =============================================================================
# 17. Slice 2's extras: KB 24's guard for a path read from a file, F16's walk for an evidence path,
#     the resolver's edges and the fixed sentences
# =============================================================================

def test_a_path_read_from_a_file_must_be_a_regular_file_inside_base_with_an_expected_name(tmp_path, monkeypatch):
    problem = _api("expected_file_problem")
    base = tmp_path / "proj"
    (base / "run").mkdir(parents=True)
    good = base / "run" / "threats.md"
    good.write_text("x", encoding="utf-8")
    assert problem(good, base) is None
    assert problem(str(good), str(base), ("threats.md",)) is None
    assert problem(good, base, {"threats.md", "risk-scores.md"}) is None
    assert problem(good, base, ["risk-scores.md"]) == "unexpected-name"
    assert problem(base / "run" / "absent.md", base) == "missing"
    other = tmp_path / "other.md"
    other.write_text("x", encoding="utf-8")
    assert problem(other, base) == "outside"
    (base / "run" / "linked.md").symlink_to(good)
    assert problem(base / "run" / "linked.md", base) == "symlink"
    (base / "alias").symlink_to(base / "run")
    assert problem(base / "alias" / "threats.md", base) == "symlink"
    (base / "run" / "dir.md").mkdir()
    assert problem(base / "run" / "dir.md", base) == "not-regular"
    monkeypatch.chdir(base)
    assert problem("run/threats.md", base) is None                      # a relative path means the working directory
    alias = tmp_path / "base-alias"
    alias.symlink_to(base)
    assert problem(good, alias) is None                                  # a spelling of the same base


@pytest.mark.parametrize("raw,reason", [
    ("run/thr\nats.md", "control-char"), ("run/thr\tats.md", "control-char"), ("run\\threats.md", "backslash"),
    ("run/`threats`.md", "backtick"), ("run/../run/threats.md", "parent-reference"), ("", "empty"),
    ("a" * 5000, "too-long"), ("https://example.test/threats.md", "scheme"),
])
def test_a_path_read_from_a_file_is_checked_for_delimiter_bytes_before_the_filesystem(tmp_path, raw, reason):
    base = tmp_path / "proj"
    base.mkdir()
    assert _api("expected_file_problem")(raw, base) == reason


def test_an_evidence_file_is_walked_down_from_the_target_without_following_a_link(tmp_path):
    problem = _api("evidence_path_problem")
    target = tmp_path / "target"
    (target / "src" / "auth").mkdir(parents=True)
    (target / "src" / "auth" / "login.py").write_text("x", encoding="utf-8")
    outside = tmp_path / "secret.txt"
    outside.write_text("x", encoding="utf-8")
    (target / "src" / "escape.py").symlink_to(outside)
    (target / "leak").symlink_to(tmp_path)
    assert problem("src/auth/login.py", target) is None
    assert problem("./src//auth/login.py", target) is None
    assert problem("src/auth/absent.py", target) == "missing"
    assert problem("absent/dir/file.py", target) == "missing"
    assert problem("src/auth", target) == "not-regular"
    assert problem("src/", target) == "not-regular"
    assert problem("src/escape.py", target) == "symlink"
    assert problem("leak/secret.txt", target) == "symlink"
    assert problem("src/auth/login.py/extra", target) in ("missing", "not-regular")
    alias = tmp_path / "target-alias"
    alias.symlink_to(target)
    assert problem("src/auth/login.py", alias) is None                   # the target may be a link; what is below it may not


@pytest.mark.parametrize("raw,reason", [
    ("../secret.txt", "parent-reference"), ("src/../../secret.txt", "parent-reference"), ("/etc/passwd", "leading-slash"),
    ("a\\b.py", "backslash"), ("C:/Windows/x", "drive-letter"), ("https://example.test/x", "scheme"),
    ("src/a\nb.py", "control-char"), ("src/`x`.py", "backtick"), ("", "empty"), (".", "empty"),
])
def test_an_evidence_file_that_breaks_d7s_rule_never_reaches_the_filesystem(tmp_path, raw, reason):
    assert _api("evidence_path_problem")(raw, tmp_path) == reason


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="needs POSIX named pipes")
def test_an_evidence_file_that_is_a_named_pipe_is_not_a_regular_file(tmp_path):
    os.mkfifo(str(tmp_path / "pipe"))
    assert _api("evidence_path_problem")("pipe", tmp_path) == "not-regular"


def test_the_resolver_canonicalizes_a_finding_id_before_it_asks_the_lookup():
    asked = []

    def lookup(kind, arg):
        asked.append((kind, arg))
        return arg

    out = _api("resolve_narrative")("Related to {{finding:AGP-01}} and {{finding:S-1}}.", SCORER_STAGE, lookup)
    assert out == "Related to AGP-1 and S-1."
    assert asked == [("finding", "AGP-1"), ("finding", "S-1")]


def test_a_finding_slot_names_an_allow_listed_id_or_the_field_falls_back():
    problem = _api("narrative_problem")
    assert problem("See {{finding:T-9}}.", SCORER_STAGE) is None
    for bad in ("{{finding:foo}}", "{{finding:S-1\u0661}}", "{{finding:S-}}", "{{finding:s-1}}"):
        assert problem(bad, SCORER_STAGE) is not None, bad


def test_a_lookup_that_returns_something_other_than_text_or_none_is_a_bug_that_fails_loudly():
    with pytest.raises(TypeError):
        _api("resolve_narrative")("Base {{score:cvss_base}}.", SCORER_STAGE, lambda kind, arg: 7.5)


def test_the_prose_sink_keeps_line_breaks_and_guards_a_line_that_a_value_would_turn_into_a_heading():
    lookup = lookup_from({("name", "component"): "# Evil | <b>"})
    text = "First line.\n# Second line.\n{{name:component}} sits here."
    prose = _api("resolve_narrative")(text, SCORER_STAGE, lookup, sink="prose")
    assert prose == "First line.\n&#35; Second line.\n&#35; Evil &#124; &lt;b&gt; sits here."
    cell = _api("resolve_narrative")(text, SCORER_STAGE, lookup)
    assert cell == "First line.&#10;# Second line.&#10;# Evil &#124; &lt;b&gt; sits here."
    with pytest.raises(ValueError):
        _api("resolve_narrative")(text, SCORER_STAGE, lookup, sink="sarif")


def test_the_fixed_sentences_are_one_per_flag_field_and_follow_t006s_shape():
    sentences = _api("FALLBACK_SENTENCES")
    assert list(sentences) == NARRATIVE_FIELDS
    assert len(set(sentences.values())) == 24
    for field, sentence in sentences.items():
        assert re.fullmatch(r"No [A-Za-z -]+ is shown because the text the agent wrote broke the narrative rules\.", sentence), field
        assert _api("narrative_fallback")(field) == sentence
        assert _api("narrative_problem")(sentence, SCORER_STAGE) is None
        assert _api("narrative_problem")(sentence, CONTROLS_STAGE) is None


def test_the_module_docstring_names_slice_twos_api():
    for name in ("SLOT_TABLE", "narrative_problem", "narrative_fallback", "FALLBACK_SENTENCES", "resolve_narrative",
                 "ESCAPE_REFERENCES", "escape_cell", "escape_prose", "fence_for", "expected_file_problem",
                 "evidence_path_problem"):
        assert name in tachi_parts.__doc__, name


# =============================================================================
# 18. The architect's rulings (T023, commit cc45993) folded into slice 2
# =============================================================================

def test_a_stage_record_keeps_at_most_1000_undeclared_paths_and_may_carry_the_truncation_warning():
    record = valid_stage_record()
    record["undeclared_paths"] = ["gen-%04d.py" % n for n in range(1000)]
    record["warnings"] = [{"code": "undeclared-paths-truncated", "detail": "1523 undeclared paths; 1000 are listed"}]
    assert _api("validate_stage_record")(record) is record
    record["undeclared_paths"].append("one-more.py")
    raises_invalid(_api("validate_stage_record"), record)


def test_a_plan_records_a_pre_image_for_every_canonical_output_of_its_stage_and_for_nothing_else():
    plan = valid_plan()
    assert set(plan["preimage"]) == set(_api("CANONICAL_OUTPUTS")["risk-score"])
    assert _api("validate_plan")(plan) is plan
    controls = dict(valid_plan(), stage="compensating-controls", agent_type="tachi-control-analyzer",
                    preimage={"compensating-controls.md": HEX, "compensating-controls.sarif": None})
    assert _api("validate_plan")(controls) is controls
    controls["preimage"] = {"risk-scores.md": None, "risk-scores.sarif": None}
    raises_invalid(_api("validate_plan"), controls)


def test_the_flag_fields_are_the_28_names_of_the_contract():
    fields = list(_api("FLAG_FIELDS"))
    assert fields == NARRATIVE_FIELDS + ["evidence.snippet", "evidence.summary", "matrix_row", "recommendation_body"]
    assert len(set(fields)) == 28
    assert {case[3] for case in truncation_cases()} <= set(fields)


def test_prose_of_any_length_is_cut_and_flagged_even_above_the_16384_character_string_limit():
    result = classify(with_text(SCORER, ("rationale", "cvss"), "a" * 20000), ids=("S-1",))
    assert result.state == "done", result.detail
    assert result.part["items"][0]["rationale"]["cvss"] == "a" * 400
    assert result.flags["S-1"] == ["input:rationale.cvss:truncated"]


@pytest.mark.parametrize("stage", [SCORER_STAGE, CONTROLS_STAGE])
@pytest.mark.parametrize("slot", ["{{count:members}}", "{{count:layers}}", "{{count:converging}}", "{{count:open}}",
                                  "{{count:resolved}}", "{{count:Critical}}", "{{pct:Critical}}", "{{name:component:S-1}}"])
def test_the_slots_reserved_for_later_stages_are_not_accepted_yet(stage, slot):
    assert _api("narrative_problem")("Held in %s." % slot, stage) is not None


def test_a_cut_inside_a_slot_token_is_flagged_both_truncated_and_narrative_fallback_and_never_rejects():
    text = "x" * 388 + "{{score:cvss_base}}"   # the cut at 400 leaves "{{score:cvss", an unterminated slot
    result = classify(with_text(SCORER, ("rationale", "cvss"), text), ids=("S-1",))
    assert result.state == "done"
    assert sorted(result.flags["S-1"]) == ["input:rationale.cvss:narrative-fallback", "input:rationale.cvss:truncated"]
    assert result.counts == {"narrative_fallbacks": 1, "truncations": 1}


# =============================================================================
# 19. The architect's ruling on gaps 19 to 22: a `{` just before a slot is escaped
#
# Together with the slot's first brace it forms a `{{` that isn't a slot, which D3 says must be escaped. A
# resolved value that starts or ends with `{` must not join its neighbour into a `{{` either.
# =============================================================================

@pytest.mark.parametrize("text,escaped", [
    ("{{{score:cvss_base}}", "&#123;{{score:cvss_base}}"),
    ("a{{{ref:CWE-89}} b", "a&#123;{{ref:CWE-89}} b"),
    ("{{score:inherent}}{{{score:residual}}", "{{score:inherent}}&#123;{{score:residual}}"),
    ("{{{{score:cvss_base}}", "&#123;&#123;{{score:cvss_base}}"),        # four braces: two are the slot's, two are a pair
    ("x{ {{score:cvss_base}}", "x{ {{score:cvss_base}}"),                 # a space between: no `{{` forms
    ("{{score:cvss_base}}{y", "{{score:cvss_base}}{y"),                   # after a slot a lone `{` joins nothing
])
@pytest.mark.parametrize("name", ["escape_cell", "escape_prose"])
def test_a_brace_just_before_a_kept_slot_is_escaped(name, text, escaped):
    assert _api(name)(text, keep_slots=True) == escaped


@pytest.mark.parametrize("text", [
    "{{{score:cvss_base}}", "a{{{ref:CWE-89}} b", "{{score:inherent}}{{{score:residual}}", "{{{{score:cvss_base}}",
    "{{7*7}} and {{{band:severity}}", "plain {text} only", "{{{{{{", "x{{{score:cvss_base}}{{{score:cvss_base}}y",
])
@pytest.mark.parametrize("name", ["escape_cell", "escape_prose"])
def test_escaping_kept_slots_decodes_and_re_renders_to_the_same_bytes_on_the_next_run(name, text):
    once = _api(name)(text, keep_slots=True)
    assert decode_references(once) == text
    assert _api(name)(decode_references(once), keep_slots=True) == once


def test_a_brace_just_before_a_slot_is_escaped_when_the_slots_are_resolved_too():
    resolve = _api("resolve_narrative")
    assert resolve("{{{name:component}}", SCORER_STAGE, lookup_from({("name", "component"): "Foo"})) == "&#123;Foo"
    assert resolve("a{{{name:component}} b", SCORER_STAGE, lookup_from({("name", "component"): "{foo"})) == "a&#123;{foo b"


@pytest.mark.parametrize("text,value,expected", [
    ("{{{name:component}}", "{x", "&#123;{x"),
    ("{{name:component}}{y", "x{", "x&#123;&#123;y"),
    ("{{name:component}}{{name:component}}", "{", "&#123;&#123;"),
    ("{{name:component}}{{name:component}}", "a{", "a{a{"),               # `{` then `a`: no pair forms
    ("{{name:component}} {z}", "x{", "x{ {z}"),
])
@pytest.mark.parametrize("sink", ["cell", "prose"])
def test_a_resolved_value_never_joins_its_neighbours_into_a_brace_pair(sink, text, value, expected):
    out = _api("resolve_narrative")(text, SCORER_STAGE, lookup_from({("name", "component"): value}), sink=sink)
    assert out == expected
    assert "{{" not in out


def test_resolved_output_never_holds_a_brace_pair_whatever_the_text_and_values():
    resolve = _api("resolve_narrative")
    texts = ["{{{name:component}}", "{ {{name:component}}{", "{{name:component}}{{{name:zone}}{", "{{{{name:component}}"]
    values = ["", "{", "{{", "}{", "x{", "{y", "{{score:cvss_base}}"]
    for text in texts:
        for first in values:
            for second in values:
                lookup = lookup_from({("name", "component"): first, ("name", "zone"): second})
                assert "{{" not in (resolve(text, SCORER_STAGE, lookup) or ""), (text, first, second)


@pytest.mark.parametrize("bad", [7.5, 7, True, ["x"], b"x", {"a": 1}])
def test_a_lookup_result_that_is_neither_text_nor_none_raises_while_none_takes_the_fallback(bad):
    with pytest.raises(TypeError):
        _api("resolve_narrative")("Base {{score:cvss_base}}.", SCORER_STAGE, lambda kind, arg: bad)
    assert _api("resolve_narrative")("Base {{score:cvss_base}}.", SCORER_STAGE, lambda kind, arg: None) is None


def test_an_id_outside_the_reference_set_takes_the_fallback_and_one_inside_is_canonical():
    reference = {"S-1", "AGP-1"}
    lookup = lambda kind, arg: arg if arg in reference else None          # noqa: E731 -- the caller's reference-set test
    assert _api("resolve_narrative")("See {{finding:AGP-01}}.", SCORER_STAGE, lookup) == "See AGP-1."
    assert _api("resolve_narrative")("See {{finding:T-9}}.", SCORER_STAGE, lookup) is None


# =============================================================================
# 20. Logic that `tachi-stage.py` and both renderers share, moved here (W1 addendum, from R0c's T018)
#
# `closed_string` is the one string check (it was private, `_closed`), `is_declared_path` is D4's declared-paths
# grammar, and `retry_history` derives a plan's overflow events and retries from the files on disk (NFR-5).
# Behaviour is byte-identical to the versions in `tachi-stage.py` at 67ea515.
# =============================================================================

def test_closed_string_is_the_published_name_and_the_old_private_name_still_works():
    assert _api("_closed") is _api("closed_string")
    check = _api("closed_string")
    assert check("a prose-free closed value", "--detail", 0, 500) == "a prose-free closed value"
    assert check("", "--detail", 0, 500) == ""
    assert check("x" * 500, "--detail", 0, 500) == "x" * 500
    assert check("tab\tand\nnewline", "--detail", 0, 500) == "tab\tand\nnewline"
    assert check("a", "what") == "a"                        # the defaults: at least one character, no upper limit but 16,384
    assert tachi_parts.closed_string.__doc__


@pytest.mark.parametrize("value,low,high", [
    (None, 0, 500), (7, 0, 500), (b"x", 0, 500), (["x"], 0, 500), ("x" * 501, 0, 500), ("", 1, 500), ("a", 2, 500),
    ("x" * 16385, 0, None), ("a\x00b", 0, 500), ("a\x1fb", 0, 500), ("a\rb", 0, 500), ("a\x7fb", 0, 500), ("a\x85b", 0, 500),
    ("a b", 0, 500), ("a b", 0, 500), ("a‎b", 0, 500), ("a‏b", 0, 500), ("a؜b", 0, 500),
    ("a‮b", 0, 500), ("a⁦b", 0, 500), ("a⁩b", 0, 500),
])
def test_closed_string_rejects_what_the_contract_forbids_and_never_echoes_the_value(value, low, high):
    with pytest.raises(_api("PartError")) as excinfo:
        _api("closed_string")(value, "--detail", low, high)
    assert excinfo.value.kind == "invalid"
    assert "--detail" in excinfo.value.detail
    assert "‮" not in excinfo.value.detail and "x" * 20 not in excinfo.value.detail


DECLARED_PATHS = [
    "risk-scores.md", "risk-scores.sarif",
    ".tachi-build/risk-score/current.json",
    ".tachi-build/risk-score/%s/plan.json" % PLAN, ".tachi-build/risk-score/%s/stage-record.json" % PLAN,
    ".tachi-build/risk-score/%s/inputs/B001.json" % PLAN, ".tachi-build/risk-score/%s/inputs/B003-1-2.json" % PLAN,
    ".tachi-build/risk-score/%s/parts/B001.a1.json" % PLAN, ".tachi-build/risk-score/%s/parts/B003-2.a2.json" % PLAN,
    ".tachi-build/risk-score/%s/parts/B001.a3.json" % PLAN,
    ".tachi-build/risk-score/%s/preimage/risk-scores.md" % PLAN, ".tachi-build/risk-score/%s/staged/risk-scores.sarif" % PLAN,
    ".tachi-build/risk-score/%s/failed/risk-scores.md" % PLAN,
]

UNDECLARED_PATHS = [
    "gen.py", "threats.md", "compensating-controls.md", "risk-scores.md.bak", "docs/risk-scores.md", "risk-scores.md/x", "",
    ".tachi-build", ".tachi-build/risk-score", ".tachi-build/compensating-controls/current.json",
    ".tachi-build/risk-score/current.json/x", ".tachi-build/risk-score/%s" % PLAN, ".tachi-build/risk-score/%s/" % PLAN,
    ".tachi-build/risk-score/%s/plan.json" % OTHER_PLAN, ".tachi-build/risk-score/%s/gen.py" % PLAN,
    ".tachi-build/risk-score/%s/plan.json.bak" % PLAN, ".tachi-build/risk-score/%s/plan.json/x" % PLAN,
    ".tachi-build/risk-score/%s/inputs/B1.json" % PLAN, ".tachi-build/risk-score/%s/inputs/B001.txt" % PLAN,
    ".tachi-build/risk-score/%s/inputs/B001.json.bak" % PLAN, ".tachi-build/risk-score/%s/inputs/B001.json/x" % PLAN,
    ".tachi-build/risk-score/%s/inputs/b001.json" % PLAN, ".tachi-build/risk-score/%s/inputs/B001-3.json" % PLAN,
    ".tachi-build/risk-score/%s/parts/B001.a4.json" % PLAN, ".tachi-build/risk-score/%s/parts/B001.a0.json" % PLAN,
    ".tachi-build/risk-score/%s/parts/B001.json" % PLAN, ".tachi-build/risk-score/%s/parts/B001.a1.json.tmp" % PLAN,
    ".tachi-build/risk-score/%s/parts/B01.a1.json" % PLAN, ".tachi-build/risk-score/%s/parts/.tmp-abc123" % PLAN,
    ".tachi-build/risk-score/%s/preimage/other.md" % PLAN, ".tachi-build/risk-score/%s/preimage/risk-scores.md/x" % PLAN,
    ".tachi-build/risk-score/%s/staged/compensating-controls.md" % PLAN, ".tachi-build/risk-score/%s/failed/../x" % PLAN,
    ".tachi-build/risk-score/%s/checks/x.json" % PLAN, ".tachi-build/risk-score/%s/trees/x.md" % PLAN,
    ".tachi-build/risk-score/%s/parts/sub/B001.a1.json" % PLAN, ".tachi-build/risk-score/%s/inputs" % PLAN,
]


@pytest.mark.parametrize("relpath", DECLARED_PATHS)
def test_the_stages_own_files_and_d3s_exact_layout_are_declared(relpath):
    assert _api("is_declared_path")(relpath, "risk-score", PLAN) is True


@pytest.mark.parametrize("relpath", UNDECLARED_PATHS)
def test_anything_else_is_undeclared(relpath):
    assert _api("is_declared_path")(relpath, "risk-score", PLAN) is False


def test_the_controls_stage_declares_its_own_outputs_and_not_the_scorers():
    declared = _api("is_declared_path")
    base = ".tachi-build/compensating-controls/%s" % PLAN
    for relpath in ("compensating-controls.md", "compensating-controls.sarif", base + "/plan.json", base + "/inputs/B002.json",
                    base + "/parts/B002.a2.json", base + "/staged/compensating-controls.sarif",
                    ".tachi-build/compensating-controls/current.json"):
        assert declared(relpath, "compensating-controls", PLAN) is True, relpath
    for relpath in ("risk-scores.md", ".tachi-build/risk-score/current.json", base + "/staged/risk-scores.md"):
        assert declared(relpath, "compensating-controls", PLAN) is False, relpath


def test_every_path_the_layout_builders_make_is_declared_by_the_grammar(tmp_path):
    out = str(tmp_path / "out")
    built = [_api("pointer_path")(out, "risk-score"), _api("plan_path")(out, "risk-score", PLAN),
             _api("stage_record_path")(out, "risk-score", PLAN)]
    for batch in ("B001", "B012", "B003-1", "B003-2-1"):
        built.append(_api("input_path")(out, "risk-score", PLAN, batch))
        built += [_api("part_path")(out, "risk-score", PLAN, batch, attempt) for attempt in (1, 2, 3)]
    for name in _api("CANONICAL_OUTPUTS")["risk-score"]:
        built += [_api(builder)(out, "risk-score", PLAN, name) for builder in ("preimage_path", "staged_path", "failed_path")]
    for path in built:
        assert _api("is_declared_path")(os.path.relpath(path, out).replace(os.sep, "/"), "risk-score", PLAN) is True, path


def history_entry(batch_id, attempt, state, parent=None, ids=("S-1", "T-2")):
    return {"batch_id": batch_id, "parent": parent, "attempt": attempt, "finding_ids": list(ids), "input_sha256": HEX, "state": state}


def history_of(tmp_path, batches, parts, stage="risk-score"):
    """Lay out ``parts`` ({(batch_id, attempt): state}) under a throwaway out directory and derive the history."""
    out = tmp_path / "out"
    plan = valid_plan()
    plan.update(stage=stage, agent_type=_api("STAGE_AGENTS")[stage], batches=batches)
    kind = SCORER if stage == "risk-score" else CONTROLS
    for (batch_id, attempt), state in parts.items():
        path = _api("part_path")(out, stage, PLAN, batch_id, attempt)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        entry = next(b for b in batches if b["batch_id"] == batch_id)
        content = {"missing": None, "unparseable": "{", "invalid": {"schema": "tachi.part/1"},
                   "overflow": dict(overflow_object(batch_id=batch_id), stage=stage, agent_type=kind["agent_type"]),
                   "done": make_part(ids=entry["finding_ids"], kind=kind, batch=batch_id)}[state]
        if content is not None:
            _api("atomic_write")(path, content if isinstance(content, str) else json.dumps(content))
    return _api("retry_history")(stage, out, plan)


def test_a_batch_retried_as_it_was_leaves_one_event_and_one_retry_per_failed_attempt(tmp_path):
    events, retries = history_of(tmp_path, [history_entry("B001", 2, "pending")], {("B001", 1): "invalid"})
    assert events == [{"batch_id": "B001", "attempt": 1, "kind": "invalid"}]
    assert retries == [{"batch_id": "B001", "attempt": 1, "cause": "invalid", "children": []}]


def test_a_halved_batch_names_its_children_on_the_attempt_that_was_halved(tmp_path):
    batches = [history_entry("B001", 1, "split"), history_entry("B001-1", 2, "pending", "B001", ["S-1"]),
               history_entry("B001-2", 2, "pending", "B001", ["T-2"])]
    events, retries = history_of(tmp_path, batches, {("B001", 1): "missing"})
    assert events == [{"batch_id": "B001", "attempt": 1, "kind": "missing"}]
    assert retries == [{"batch_id": "B001", "attempt": 1, "cause": "missing", "children": ["B001-1", "B001-2"]}]


def test_a_batch_that_ran_out_of_retries_leaves_an_event_for_its_last_attempt_and_no_retry(tmp_path):
    parts = {("B001", 1): "invalid", ("B001", 2): "overflow", ("B001", 3): "unparseable"}
    events, retries = history_of(tmp_path, [history_entry("B001", 3, "failed")], parts)
    assert [(e["attempt"], e["kind"]) for e in events] == [(1, "invalid"), (2, "overflow-reported"), (3, "unparseable")]
    assert [(r["attempt"], r["cause"], r["children"]) for r in retries] == [(1, "invalid", []), (2, "overflow", [])]


def test_an_overflow_object_is_reported_as_overflow_reported_and_its_retry_cause_is_overflow(tmp_path):
    events, retries = history_of(tmp_path, [history_entry("B001", 2, "pending")], {("B001", 1): "overflow"})
    assert events[0]["kind"] == "overflow-reported"
    assert retries[0]["cause"] == "overflow"


def test_a_part_that_turned_valid_after_its_attempt_was_given_up_was_still_not_counted(tmp_path):
    events, retries = history_of(tmp_path, [history_entry("B001", 2, "pending")], {("B001", 1): "done"})
    assert events == [{"batch_id": "B001", "attempt": 1, "kind": "missing"}]
    assert retries[0]["cause"] == "missing"


def test_a_child_counts_its_failed_attempts_from_the_attempt_after_its_parents(tmp_path):
    batches = [history_entry("B001", 1, "split"), history_entry("B001-1", 3, "pending", "B001", ["S-1"]),
               history_entry("B001-2", 2, "pending", "B001", ["T-2"])]
    events, retries = history_of(tmp_path, batches, {("B001", 1): "missing", ("B001-1", 2): "unparseable"})
    assert events == [{"batch_id": "B001", "attempt": 1, "kind": "missing"},
                      {"batch_id": "B001-1", "attempt": 2, "kind": "unparseable"}]
    assert retries == [{"batch_id": "B001", "attempt": 1, "cause": "missing", "children": ["B001-1", "B001-2"]},
                       {"batch_id": "B001-1", "attempt": 2, "cause": "unparseable", "children": []}]


def test_a_plan_with_no_failed_attempt_has_no_history(tmp_path):
    assert history_of(tmp_path, [history_entry("B001", 1, "done"), history_entry("B002", 1, "pending")], {}) == ([], [])
    assert history_of(tmp_path, [], {}) == ([], [])


def test_the_controls_stage_reads_its_own_parts(tmp_path):
    batches = [history_entry("B001", 2, "pending")]
    events, retries = history_of(tmp_path, batches, {("B001", 1): "invalid"}, stage="compensating-controls")
    assert events == [{"batch_id": "B001", "attempt": 1, "kind": "invalid"}]
    assert retries[0]["cause"] == "invalid"


def test_the_derived_history_is_a_valid_stage_record_body(tmp_path):
    batches = [history_entry("B001", 1, "split"), history_entry("B001-1", 3, "failed", "B001", ["S-1"]),
               history_entry("B001-2", 2, "pending", "B001", ["T-2"])]
    parts = {("B001", 1): "overflow", ("B001-1", 2): "invalid", ("B001-1", 3): "missing"}
    events, retries = history_of(tmp_path, batches, parts)
    record = dict(valid_stage_record(), overflow_events=events, retries=retries)
    assert _api("validate_stage_record")(record) is record


# =============================================================================
# 21. Edge whitespace is removed at intake (ruled at W1, from T033; contracts/part-files.md, "Validation order")
#
# Lane P's decoder reads a table cell with its edges stripped, so a carried value that kept edge whitespace would
# come back different on its second run, and T056 needs carried values byte-identical. In step 9, after any cut,
# every narrative and evidence-class string is `strip()`ped, a snippet is `textwrap.dedent`ed first, no flag is
# raised, and a required field that is empty afterwards still rejects the part. Closed values are left as written.
# =============================================================================

def stored_at(result, *path):
    value = result.part["items"][0]
    for key in path:
        value = value[key]
    return value


PROSE_FIELDS = [
    ("rationale.cvss", SCORER, ("rationale", "cvss")),
    ("rationale.reachability", SCORER, ("rationale", "reachability")),
    ("metric_rationale.AV", SCORER, ("metric_rationale", "AV")),
    ("subscore_rationale.known_techniques", SCORER, ("subscore_rationale", "known_techniques")),
    ("evidence.summary", CONTROLS, ("evidence", 0, "summary")),
    ("matrix_row", CONTROLS, ("matrix_row",)),
    ("recommendation_body", CONTROLS, ("recommendation_body",)),
]


def assessment_part(text):
    part = make_part(kind=CONTROLS, ids=("S-1",), items=[controls_item("S-1", "partial")])
    part["items"][0]["evidence"][0]["assessment"] = {
        d: {"rating": "High", "rationale": text} for d in ("coverage", "configuration", "currency", "completeness")}
    return part


@pytest.mark.parametrize("raw", [" \t x \n ", "\n\n  x", "x\t\t", " x ", "　x　", "   x", "x   ", "\tx\n", "x\n\n\n"])
@pytest.mark.parametrize("field,kind,path", PROSE_FIELDS, ids=[f[0] for f in PROSE_FIELDS])
def test_a_prose_string_loses_its_edge_whitespace_and_raises_no_flag(field, kind, path, raw):
    result = classify(with_text(kind, path, raw), ids=("S-1",), kind=kind)
    assert result.state == "done", result.detail
    assert stored_at(result, *path) == "x"
    assert result.flags.get("S-1", []) == []
    assert result.counts == {"narrative_fallbacks": 0, "truncations": 0}


def test_an_assessment_rationale_loses_its_edge_whitespace_too():
    result = classify(assessment_part("  \t Covers the main path.\n "), ids=("S-1",), kind=CONTROLS)
    assert result.state == "done", result.detail
    assessment = stored_at(result, "evidence", 0, "assessment")
    assert {cell["rationale"] for cell in assessment.values()} == {"Covers the main path."}
    assert result.flags.get("S-1", []) == []


def test_slots_at_the_edges_survive_the_strip_and_the_field_is_still_checked_as_narrative():
    result = classify(with_text(SCORER, ("rationale", "cvss"), "  {{score:cvss_base}} is {{band:severity}}.  "), ids=("S-1",))
    assert stored_at(result, "rationale", "cvss") == "{{score:cvss_base}} is {{band:severity}}."
    broken = classify(with_text(SCORER, ("rationale", "cvss"), "  Score 9.8 is high.  "), ids=("S-1",))
    assert stored_at(broken, "rationale", "cvss") == _api("narrative_fallback")("rationale.cvss")


def test_whitespace_inside_the_text_is_left_alone():
    for text in ("a  b\t c", "line one\n  line two\n\nline four", "x   y"):
        result = classify(with_text(SCORER, ("rationale", "exploitability"), text), ids=("S-1",))
        assert stored_at(result, "rationale", "exploitability") == text


def test_the_strip_follows_the_cut_and_the_cut_is_still_flagged():
    text = "a" * 399 + " " + "b" * 50          # the cut at 400 ends on the space
    result = classify(with_text(SCORER, ("rationale", "cvss"), text), ids=("S-1",))
    assert stored_at(result, "rationale", "cvss") == "a" * 399
    assert result.flags["S-1"] == ["input:rationale.cvss:truncated"]
    assert result.counts["truncations"] == 1


def test_a_required_field_that_is_empty_after_the_strip_rejects_the_part_and_an_optional_one_may_be_empty():
    for blank in ("   ", "\t\n ", " 　"):
        assert classify(with_text(SCORER, ("rationale", "cvss"), blank), ids=("S-1",)).state == "invalid", repr(blank)
        for kind, path in ((CONTROLS, ("evidence", 0, "summary")), (CONTROLS, ("matrix_row",)), (CONTROLS, ("recommendation_body",)),
                           (SCORER, ("metric_rationale", "AV"))):
            result = classify(with_text(kind, path, blank), ids=("S-1",), kind=kind)
            assert result.state == "done", (path, result.detail)
            assert stored_at(result, *path) == ""


def test_closed_values_are_checked_and_never_stripped():
    part = with_text(SCORER, ("reachability", "zone"), " Public Zone ")
    assert stored_at(classify(part, ids=("S-1",)), "reachability", "zone") == " Public Zone "
    part = put(make_part(kind=CONTROLS, ids=("S-1",)), ("items", 0, "evidence", 0, "file"), " src/a.py ")
    result = classify(part, ids=("S-1",), kind=CONTROLS)
    assert result.state == "done" and stored_at(result, "evidence", 0, "file") == " src/a.py "


@pytest.mark.parametrize("raw,expected", [
    ("    def f():\n        return 1\n", "def f():\n    return 1"),
    ("\tfoo\n\t\tbar", "foo\n\tbar"),
    ("\n    x\n      y\n", "x\n  y"),
    ("  a\n\tb", "a\n\tb"),                                       # no common margin: only the edges go
    ("    a\n        \n    b", "a\n\nb"),                           # textwrap.dedent empties a whitespace-only line
    ("  one\n  two  \n  three", "one\ntwo  \nthree"),               # trailing spaces inside the text stay
    ("x = 1", "x = 1"),
])
def test_a_snippet_is_dedented_so_its_lines_keep_their_relative_indentation_and_then_stripped(raw, expected):
    result = classify(with_text(CONTROLS, ("evidence", 0, "snippet"), raw), ids=("S-1",), kind=CONTROLS)
    assert result.state == "done", result.detail
    assert stored_at(result, "evidence", 0, "snippet") == expected
    assert result.flags.get("S-1", []) == []


def test_a_snippet_is_cut_first_and_the_lines_that_are_kept_are_the_ones_dedented():
    lines = ["        kept %s" % name for name in "abcde"] + ["    cut %s" % name for name in "fgh"]
    result = classify(with_text(CONTROLS, ("evidence", 0, "snippet"), "\n".join(lines)), ids=("S-1",), kind=CONTROLS)
    assert stored_at(result, "evidence", 0, "snippet") == "\n".join("kept %s" % name for name in "abcde")
    assert result.flags["S-1"] == ["input:evidence.snippet:truncated"]


@pytest.mark.parametrize("char", [chr(code) for code in range(0x110000) if chr(code).isspace()])
def test_every_character_that_str_strip_removes_is_removed_from_the_edges(char):
    """The predicate is the table readers' own, so no stored value can lose an edge on the next read.

    A separator or control that D3 forbids is stripped at the edge, before step 10 looks, and one inside still rejects.
    """
    result = classify(with_text(SCORER, ("rationale", "cvss"), char + "x" + char), ids=("S-1",))
    assert result.state == "done", (hex(ord(char)), result.detail)
    assert stored_at(result, "rationale", "cvss") == "x"


@pytest.mark.parametrize("raw", [" \t x \n ", "\n\n  Network reachable, so {{score:cvss_base}}.  \t", "a  b \n c"])
@pytest.mark.parametrize("field,kind,path", PROSE_FIELDS, ids=[f[0] for f in PROSE_FIELDS])
def test_normalizing_a_normalized_value_changes_nothing(field, kind, path, raw):
    first = classify(with_text(kind, path, raw), ids=("S-1",), kind=kind)
    if first.state != "done":
        pytest.skip("not a valid value for this field")
    again = classify(with_text(kind, path, stored_at(first, *path)), ids=("S-1",), kind=kind)
    assert stored_at(again, *path) == stored_at(first, *path)


def read_back(cell_text):
    """What lane P's reader does with a persisted row: split on raw `|`, strip the cell's edges, decode the references."""
    row = "| %s |" % cell_text
    return decode_references(row.split("|")[1].strip())


MESSY_PROSE = [" \t Network reachable with no privileges.\n ", "\n\n  A | pipe, a `tick`, <b>, & {{braces}}  \t", "x "]
MESSY_SNIPPETS = ["    def login(user):\n        check(user)\n\n    return 1\n", "\n\n\tfoo()\n\t\tbar()\t\n", "  a | b `c` <d> & {{e}}  "]


@pytest.mark.parametrize("raw", MESSY_PROSE)
@pytest.mark.parametrize("field,kind,path", PROSE_FIELDS, ids=[f[0] for f in PROSE_FIELDS])
def test_a_carried_value_is_byte_identical_across_two_write_and_read_round_trips(field, kind, path, raw):
    """T056: write a value as the renderer does, read it back as the next run does, and validate it again, twice over."""
    first = classify(with_text(kind, path, raw), ids=("S-1",), kind=kind)
    assert first.state == "done", first.detail
    first_value = stored_at(first, *path)
    first_cell = _api("escape_cell")(first_value, keep_slots=True)
    value = first_value
    for _ in range(2):
        value = read_back(_api("escape_cell")(value, keep_slots=True))
        assert value == first_value
        again = classify(with_text(kind, path, value), ids=("S-1",), kind=kind)
        assert stored_at(again, *path) == first_value
        assert _api("escape_cell")(stored_at(again, *path), keep_slots=True) == first_cell


def test_without_the_strip_an_edge_would_not_survive_the_read():
    """The failure this rule prevents: a value written with edge spaces comes back without them."""
    assert read_back(_api("escape_cell")(" x ")) == "x"


@pytest.mark.parametrize("raw", MESSY_SNIPPETS)
def test_an_indented_snippet_is_byte_identical_across_two_write_and_read_round_trips(raw):
    path = ("evidence", 0, "snippet")
    first_value = stored_at(classify(with_text(CONTROLS, path, raw), ids=("S-1",), kind=CONTROLS), *path)
    assert first_value == first_value.strip()
    value = first_value
    for _ in range(2):
        value = read_back(_api("escape_cell")(value))
        assert value == first_value
        assert stored_at(classify(with_text(CONTROLS, path, value), ids=("S-1",), kind=CONTROLS), *path) == first_value


def test_a_narrative_with_edge_whitespace_and_slots_round_trips_byte_for_byte():
    raw = "\t\n  {{name:component}} sits in {{name:zone}}, behind {{count:auth_barriers}} barriers.  \n "
    first_value = stored_at(classify(with_text(SCORER, ("rationale", "reachability"), raw), ids=("S-1",)), "rationale", "reachability")
    assert first_value == "{{name:component}} sits in {{name:zone}}, behind {{count:auth_barriers}} barriers."
    value = first_value
    for _ in range(2):
        cell = _api("escape_cell")(value, keep_slots=True)
        assert cell == first_value                              # nothing to escape, and the slots are kept
        value = read_back(cell)
        assert value == first_value
        again = classify(with_text(SCORER, ("rationale", "reachability"), value), ids=("S-1",))
        assert stored_at(again, "rationale", "reachability") == first_value
