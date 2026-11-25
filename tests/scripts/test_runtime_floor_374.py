"""S-11's runtime floor, enforced on every new shipped script (F-374 T149; FR-E.15; ADR-050 D16).

Every new shipped script runs on Python 3.9 and later. F-373's S-13 import gate sees only load-time
imports, so this module checks what it can't:

1. **Grammar.** ``ast.parse(..., feature_version=(3, 9))`` accepts the source, and the module opens
   with ``from __future__ import annotations``, so ``X | None`` and ``list[int]`` in an annotation
   never run on 3.9.
2. **Standard-library API.** No name from the deny-lists below is used: what 3.10 to 3.12 added,
   plus the keyword arguments that arrived later (``zip(strict=)``, ``Path.write_text(newline=)``
   and so on). It is a static net. The ``f374-py39-floor`` job's real 3.9 interpreter, which runs
   this whole module list, is the other half.
3. **Optional dependency.** The core path of each entry runs in a fresh interpreter whose import
   machinery refuses ``yaml``, and its output must equal an unblocked run's, byte for byte once the
   fresh plan ID, the clock and the digests that hash them are masked. S-13 can't see a
   function-level ``import yaml``. This can. Gated tests drive entries in-process, but a process
   alone shows a clean ``sys.modules``, so this module uses subprocesses (ADR-050 D16, H15).

   PR 2's four entries (T150) take one small synthetic world each. The SARIF generator and the chain
   script read a threat model (the chain script also an inventory), and the joiner and the assembler
   take plans, batch inputs and parts, which ``_batch_stage`` writes in place of the planner of PR 2's
   batch stages, because that planner is another lane's. A run that exits 0 and writes nothing, or
   whose slots fell back to a fixed sentence, fails ``OUTPUTS`` and ``FALLBACK_WORDS`` here, so the
   comparison can't pass over two empty runs. The worlds hold the clean first run of each entry and,
   for the generator and the joiner, a run beside it that has a baseline. They leave out the error
   paths, the assembler's baseline, pattern and chain sections, and the chain script's fixed text. The
   unit modules cover those, in process.

Extending it in a later wave (W2's renderer and scoring-rules module, W3's controls renderer, PR 2's
scripts and T150's rewritten ``generate-threats-sarif.py``):

* Move a script from ``PLANNED`` to ``REQUIRED_NOW`` in the wave that lands it. Until then its checks
  skip with the reason in ``PLANNED``. Once the file exists they run, and they never skip silently.
* Give each new **entry** (a hyphenated script) a driver in ``CORE_PATH_DRIVERS``.
  ``test_every_entry_script_has_a_core_path_driver`` fails until it has one.
* Add a deny-list row when a review finds a post-3.9 API this net missed, with a case in
  ``FLAGGED`` or ``CLEAN`` so the checker keeps its own regression test.

Standard library and, in this process only, the shipped helpers ``tachi_parts`` and ``tachi_parsers`` (the stand-in
planner takes their layout, schemas and digest from them). Python 3.9 syntax: this module itself runs in the 3.9 job.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"

SUBPROCESS_TIMEOUT = 120

# --------------------------------------------------------------------------- the script lists
# W1's, W2's and W3's scripts, and PR 2's W2' four. A missing file is a failure: T012, T013, T014, T015, T016, T018, T140, T028, T042 and T035
# write the first group, and T100, T106, T116, T117, T108 and T109 the second.
REQUIRED_NOW = (
    "tachi_parts.py",
    "tachi_scoring.py",
    "sarif_common.py",  # exists today; W1 rewrites it as the shared emitter and installs it
    "tachi-stage.py",
    "tachi_scoring_rules.py",  # W2 (lane R1b): T042 to T044
    "render-risk-scores.py",  # W2 (lane R1): T028, T045, T046 and T050
    "render-compensating-controls.py",  # W3 (lane R2): T035, T053 and T059; its core-path driver is T036's
    # PR 2, W2' (T150). generate-threats-sarif.py exists today, so it is not "new" until PR 2 rewrites it on the shared emitter (T100).
    "generate-threats-sarif.py",  # lane R3b: T099 and T100
    "join-threats-md.py",  # lane HL: T106 and T107
    "attack-chains.py",  # lane OC: T115 to T117
    "assemble-report.py",  # lane T: T108 and T109
)

# Scripts a later wave adds, with the wave that lands each. While one is missing its checks skip with
# this reason. Once it exists the checks run on it, and the move to REQUIRED_NOW is the wave's own
# one-line edit. W3' adds check-threat-model.py (T096), and T098 wires it.
PLANNED = {
    "check-threat-model.py": "PR 2, W3' (lane OC)",
}

ALL_SCRIPTS = tuple(REQUIRED_NOW) + tuple(sorted(PLANNED))


def _resolve(name):
    """The script's path, or a skip (planned and not yet written) or a failure (required and missing)."""
    path = SCRIPTS_DIR / name
    if path.is_file():
        return path
    if name in PLANNED:
        pytest.skip("scripts/%s is planned for %s and does not exist yet" % (name, PLANNED[name]))
    pytest.fail("scripts/%s is a required script and must exist (S-11, T149)" % name, pytrace=False)


# --------------------------------------------------------------------------- 1. grammar


@pytest.mark.parametrize("name", ALL_SCRIPTS)
def test_script_parses_with_the_python_39_grammar(name):
    path = _resolve(name)
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path), feature_version=(3, 9))


@pytest.mark.parametrize(
    "source",
    [
        "match command:\n    case 1:\n        pass\n",
        "try:\n    pass\nexcept* ValueError:\n    pass\n",
    ],
    ids=["match-statement-3.10", "except-star-3.11"],
)
def test_the_grammar_check_rejects_syntax_newer_than_39(source):
    """The canary: if feature_version stopped gating syntax, the check above would pass vacuously."""
    with pytest.raises(SyntaxError):
        ast.parse(source, feature_version=(3, 9))


def _leads_with_future_annotations(tree):
    """True when ``from __future__ import annotations`` comes before every non-future statement."""
    for position, node in enumerate(tree.body):
        if position == 0 and isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant):
            if isinstance(node.value.value, str):
                continue  # the module docstring
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            if any(alias.name == "annotations" for alias in node.names):
                return True
            continue
        return False
    return False


@pytest.mark.parametrize("name", ALL_SCRIPTS)
def test_script_opens_with_the_required_future_import(name):
    path = _resolve(name)
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    assert _leads_with_future_annotations(tree), (
        "scripts/%s must open (after its docstring) with `from __future__ import annotations`" % name
    )


def test_the_future_import_check_is_not_vacuous():
    ok = ast.parse('"""doc"""\nfrom __future__ import annotations\nimport sys\n')
    late = ast.parse('"""doc"""\nimport sys\nfrom __future__ import annotations\n')
    absent = ast.parse('"""doc"""\nimport sys\n')
    assert _leads_with_future_annotations(ok)
    assert not _leads_with_future_annotations(late)
    assert not _leads_with_future_annotations(absent)


# --------------------------------------------------------------------------- 2. standard-library API

# dotted name -> the version that introduced it. Add a row when a review finds a name this net missed.
POST_39_NAMES = {
    "sys.stdlib_module_names": "3.10",
    "sys.orig_argv": "3.10",
    "itertools.pairwise": "3.10",
    "itertools.batched": "3.12",
    "math.cbrt": "3.11",
    "math.exp2": "3.11",
    "math.sumprod": "3.12",
    "datetime.UTC": "3.11",
    "enum.StrEnum": "3.11",
    "enum.ReprEnum": "3.11",
    "enum.verify": "3.11",
    "hashlib.file_digest": "3.11",
    "contextlib.chdir": "3.11",
    "contextlib.aclosing": "3.10",
    "inspect.get_annotations": "3.10",
    "types.NoneType": "3.10",
    "types.EllipsisType": "3.10",
    "types.NotImplementedType": "3.10",
    "types.UnionType": "3.10",
    "operator.call": "3.11",
    "logging.getLevelNamesMapping": "3.11",
    "re.NOFLAG": "3.11",
    "random.binomialvariate": "3.12",
    "asyncio.TaskGroup": "3.11",
    "asyncio.timeout": "3.11",
    "asyncio.Runner": "3.11",
    "os.path.isjunction": "3.12",
}
_TYPING_AFTER_39 = {
    "TypeAlias": "3.10", "ParamSpec": "3.10", "ParamSpecArgs": "3.10", "ParamSpecKwargs": "3.10",
    "Concatenate": "3.10", "TypeGuard": "3.10", "is_typeddict": "3.10",
    "Self": "3.11", "Never": "3.11", "LiteralString": "3.11", "Required": "3.11", "NotRequired": "3.11",
    "Unpack": "3.11", "TypeVarTuple": "3.11", "assert_never": "3.11", "assert_type": "3.11",
    "reveal_type": "3.11", "dataclass_transform": "3.11", "get_overloads": "3.11", "clear_overloads": "3.11",
    "override": "3.12", "TypeAliasType": "3.12",
}
for _name, _since in _TYPING_AFTER_39.items():
    POST_39_NAMES["typing." + _name] = _since

POST_39_MODULES = {"tomllib": "3.11"}

# (callable's last name, keyword) -> version. The call may be a plain name or an attribute.
POST_39_KEYWORDS = {
    ("zip", "strict"): "3.10",
    ("dataclass", "slots"): "3.10",
    ("dataclass", "kw_only"): "3.10",
    ("dataclass", "match_args"): "3.10",
    ("rmtree", "onexc"): "3.12",
    ("bisect", "key"): "3.10",
    ("bisect_left", "key"): "3.10",
    ("bisect_right", "key"): "3.10",
    ("insort", "key"): "3.10",
    ("write_text", "newline"): "3.10",
    ("read_text", "newline"): "3.13",
}

# Method names with no 3.9 spelling. A receiver's type is invisible to a static check, so a clash
# with a project method of the same name is a false positive: rename the project method.
POST_39_METHODS = {"bit_count": "3.10", "hardlink_to": "3.10", "is_junction": "3.12"}


def _dotted(node):
    """``a.b.c`` for a Name/Attribute chain, else None."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


# The one escape hatch: a ``datetime.fromisoformat(value)`` whose value the author has already stripped of a
# ``Z`` suffix, in a way the AST can't show, carries this marker in a comment on the same line.
Z_NORMALIZED_MARKER = "S-11: Z normalized"


def post_39_findings(source):
    """Every use of a post-3.9 name in ``source``, as ``"line N: <what> (3.x)"`` strings."""
    tree = ast.parse(source)
    lines = source.splitlines()
    aliases = {}  # local name -> the module or dotted name it stands for
    findings = []

    def flag(node, what, since):
        findings.append("line %d: %s (%s)" % (getattr(node, "lineno", 0), what, since))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                aliases[alias.asname or alias.name.split(".")[0]] = alias.name if alias.asname else alias.name.split(".")[0]
                if alias.name in POST_39_MODULES:
                    flag(node, "import " + alias.name, POST_39_MODULES[alias.name])
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            if node.module in POST_39_MODULES:
                flag(node, "from " + node.module + " import ...", POST_39_MODULES[node.module])
            for alias in node.names:
                dotted = node.module + "." + alias.name
                aliases[alias.asname or alias.name] = dotted
                if dotted in POST_39_NAMES:
                    flag(node, dotted, POST_39_NAMES[dotted])

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            dotted = _dotted(node)
            if dotted:
                head, _, rest = dotted.partition(".")
                full = aliases.get(head, head) + ("." + rest if rest else "")
                if full in POST_39_NAMES:
                    flag(node, full, POST_39_NAMES[full])
            if node.attr in POST_39_METHODS and isinstance(getattr(node, "ctx", None), ast.Load):
                flag(node, "." + node.attr + "()", POST_39_METHODS[node.attr])
        if isinstance(node, ast.Call):
            last = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", None)
            for keyword in node.keywords:
                since = POST_39_KEYWORDS.get((last, keyword.arg))
                if since:
                    flag(node, "%s(%s=)" % (last, keyword.arg), since)
            if last in ("isinstance", "issubclass") and len(node.args) == 2:
                second = node.args[1]
                if isinstance(second, ast.BinOp) and isinstance(second.op, ast.BitOr):
                    flag(node, "%s(x, A | B)" % last, "3.10")
            if last == "fromisoformat" and isinstance(node.func, ast.Attribute):
                receiver = (_dotted(node.func.value) or "").split(".")[-1]
                first = node.args[0] if node.args else None
                normalized = isinstance(first, ast.Call) and isinstance(first.func, ast.Attribute) and first.func.attr == "replace"
                marked = Z_NORMALIZED_MARKER in lines[node.lineno - 1]
                if receiver == "datetime" and not normalized and not marked:
                    flag(node, "datetime.fromisoformat (a 'Z' suffix parses only from 3.11; use strptime, or mark a "
                               "value you normalized with '# %s')" % Z_NORMALIZED_MARKER, "3.11")
    return findings


# Each case: (source, a fragment the finding must contain).
FLAGGED = [
    ("import sys\nx = sys.stdlib_module_names\n", "sys.stdlib_module_names"),
    ("from typing import TypeAlias\n", "typing.TypeAlias"),
    ("import typing\nx: typing.TypeGuard\n", "typing.TypeGuard"),
    ("import datetime\nnow = datetime.UTC\n", "datetime.UTC"),
    ("from datetime import UTC\n", "datetime.UTC"),
    ("import itertools as it\nit.pairwise([])\n", "itertools.pairwise"),
    ("zip([], [], strict=True)\n", "zip(strict=)"),
    ("from dataclasses import dataclass\n@dataclass(slots=True)\nclass C: pass\n", "dataclass(slots=)"),
    ("from pathlib import Path\nPath('x').write_text('a', newline='')\n", "write_text(newline=)"),
    ("isinstance(1, int | str)\n", "isinstance(x, A | B)"),
    ("import datetime\ndatetime.datetime.fromisoformat('2026-11-22T00:00:00Z')\n", "fromisoformat"),
    ("from datetime import datetime\ndatetime.fromisoformat(value)\n", "fromisoformat"),
    ("import tomllib\n", "import tomllib"),
    ("(5).bit_count()\n", ".bit_count()"),
    ("import shutil\nshutil.rmtree('x', onexc=print)\n", "rmtree(onexc=)"),
]
CLEAN = [
    "from datetime import date\ndate.fromisoformat('2026-11-22')\n",
    "import datetime\ndatetime.datetime.strptime('2026-11-22T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')\n",
    "from datetime import datetime\ndatetime.fromisoformat(value.replace('Z', '+00:00'))\n",
    "import datetime\nparsed = datetime.datetime.fromisoformat(text)  # S-11: Z normalized above\n",
    "'abc'.removeprefix('a')\n",
    "from functools import cache\n",
    "from pathlib import Path\nPath('x').is_relative_to('y')\n",
    "import itertools\nlist(itertools.chain([1], [2]))\n",
    "def f(x: 'int | None' = None) -> 'list[int]':\n    return []\n",
]


@pytest.mark.parametrize("source,fragment", FLAGGED, ids=[f[1] for f in FLAGGED])
def test_the_api_check_flags_each_known_post_39_use(source, fragment):
    findings = post_39_findings(source)
    assert any(fragment in finding for finding in findings), (fragment, findings)


@pytest.mark.parametrize("source", CLEAN, ids=["clean-%d" % i for i in range(len(CLEAN))])
def test_the_api_check_passes_code_that_runs_on_39(source):
    assert post_39_findings(source) == []


@pytest.mark.parametrize("name", ALL_SCRIPTS)
def test_script_uses_no_post_39_standard_library_api(name):
    path = _resolve(name)
    findings = post_39_findings(path.read_text(encoding="utf-8"))
    assert findings == [], "scripts/%s uses an API newer than Python 3.9:\n  %s" % (name, "\n  ".join(findings))


# --------------------------------------------------------------------------- 3. yaml unimportable

# Runs one script in a fresh interpreter: `shim.py MODE SCRIPT ARGS...`. MODE "block" first installs a
# meta-path finder that refuses `yaml`, as on an adopter machine without PyYAML, and proves it works
# before running the script. The script is exec'd, not run through runpy, so `sys.modules` holds
# only what the script itself imported (the guard test below reads it).
SHIM = '''\
import collections
import json
import sys

mode, script = sys.argv[1], sys.argv[2]
sys.argv = [script] + sys.argv[3:]

if mode == "block":
    class NoYaml(object):
        def find_spec(self, name, path=None, target=None):
            if name.split(".")[0] in ("yaml", "_yaml"):
                raise ImportError("PyYAML is blocked by tests/scripts/test_runtime_floor_374.py (S-11)")
            return None

    sys.meta_path.insert(0, NoYaml())
    for loaded in list(sys.modules):
        if loaded.split(".")[0] in ("yaml", "_yaml"):
            del sys.modules[loaded]
    try:
        import yaml
    except ImportError:
        pass
    else:
        sys.stderr.write("the yaml import hook is not in force\\n")
        sys.exit(97)

if mode == "old-python":
    # A real 3.8 interpreter is not available in CI, so show the guard on this one pretending to be 3.8.
    version_info = collections.namedtuple("version_info", "major minor micro releaselevel serial")
    sys.version_info = version_info(3, 8, 18, "final", 0)
    sys.version = "3.8.18 (default, Jan  1 2024, 00:00:00) \\n[GCC 12.2.0]"
    import builtins

    requested = []
    real_import = builtins.__import__

    def recording_import(name, globals=None, locals=None, fromlist=(), level=0):
        if globals is not None and globals.get("__file__") == script:
            requested.append(name)  # an import statement the script itself executed, loaded already or not
        return real_import(name, globals, locals, fromlist, level)

    builtins.__import__ = recording_import
    before = set(sys.modules)
    code = None
    try:
        with open(script, encoding="utf-8") as handle:
            source = handle.read()
        exec(compile(source, script, "exec"), {"__name__": "__main__", "__file__": script})
    except SystemExit as exc:
        code = exc.code
    builtins.__import__ = real_import
    sys.stdout.write(json.dumps({"code": code, "imports": requested, "new_modules": sorted(set(sys.modules) - before)}))
    sys.exit(0)

with open(script, encoding="utf-8") as handle:
    source = handle.read()
exec(compile(source, script, "exec"), {"__name__": "__main__", "__file__": script})
'''

_PLAN_ID = re.compile(r"[0-9]{8}T[0-9]{6}Z-[0-9a-f]{12}")
# A digest or timestamp that hashes or records the fresh plan ID, or the clock.
_VOLATILE_VALUE = re.compile(r'("(?:plan_digest|input_sha256|created_utc|started_utc|finished_utc)"\s*:\s*)"[^"]*"')
_VOLATILE_ARGUMENT = re.compile(r"(--plan-digest\s+)[0-9a-f]{64}")  # the same digest, passed back on a command line
_NANOSECONDS = re.compile(r"\b[0-9]{17,}\b")


def _normalize(text):
    """Mask only what is fresh on every run, so any other difference still shows."""
    text = _PLAN_ID.sub("<PLAN>", text)
    text = _VOLATILE_VALUE.sub(r'\1"<VOLATILE>"', text)
    text = _VOLATILE_ARGUMENT.sub(r"\1<VOLATILE>", text)
    return _NANOSECONDS.sub("<NS>", text)


class Interpreter(object):
    """Runs scripts through the shim, in a fresh interpreter each time."""

    def __init__(self, shim, blocked):
        self.shim = shim
        self.mode = "block" if blocked else "plain"

    def run(self, script, args, cwd, mode=None):
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(self.shim), mode or self.mode, str(script)] + [str(a) for a in args],
            cwd=str(cwd),
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=SUBPROCESS_TIMEOUT,
        )
        return proc


@pytest.fixture
def shim(tmp_path):
    path = tmp_path / "shim" / "floor_shim.py"
    path.parent.mkdir()
    path.write_text(SHIM, encoding="utf-8")
    return path


def test_the_yaml_block_really_blocks_yaml(shim, tmp_path):
    """The canary: with the hook in force, ``import yaml`` fails in the child, whatever is installed."""
    probe = tmp_path / "probe.py"
    probe.write_text("import sys\ntry:\n    import yaml\nexcept ImportError:\n    sys.exit(0)\nsys.exit(5)\n", encoding="utf-8")
    assert Interpreter(shim, blocked=True).run(probe, [], tmp_path).returncode == 0


# ---- the part-writing a driver needs. Duplicated in test_tachi_stage.py on purpose: a test module
# ---- imports no other test module, and this one adds no shared file in W1.

def _scorer_item(finding_id):
    return {
        "finding_id": finding_id,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "exploitability": {"known_techniques": 5, "attack_complexity": 5, "tooling_availability": 5, "skill_level": 5},
        "scalability": {"scriptability": 5, "target_scope": 5, "resource_requirements": 5, "detection_difficulty": 5},
        "reachability": {"zone": None, "trust_level": None, "auth_barriers": 5, "network_boundaries": 5},
        "rationale": {
            "cvss": "Remote and unauthenticated.",
            "exploitability": "Public techniques exist.",
            "scalability": "Easy to repeat.",
            "reachability": "Exposed to the edge.",
        },
    }


def _write_valid_part(batch_input_path, make_item=None):
    make_item = _scorer_item if make_item is None else make_item
    batch_input = json.loads(Path(batch_input_path).read_text(encoding="utf-8"))
    part = {
        "schema": "tachi.part/1",
        "plan_id": batch_input["plan_id"],
        "batch_id": batch_input["batch_id"],
        "stage": batch_input["stage"],
        "agent_type": batch_input["agent_type"],
        "finding_ids": list(batch_input["finding_ids"]),
        "items": [make_item(fid) for fid in batch_input["finding_ids"]],
        "fragments": [],
    }
    target = Path(batch_input["part_path"])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(part), encoding="utf-8")


_FINDINGS = ["S-1", "T-9", "T-10", "R-2", "I-3", "D-1", "E-4", "AG-1", "LLM-2"]


def _threats_md():
    rows = "\n".join(
        "| %s | NEW | Category | \u2014 | Gateway %d | L4 | Threat text for %s | High | Mitigation for %s |" % (fid, n, fid, fid)
        for n, fid in enumerate(reversed(_FINDINGS), 1)
    )
    return (
        '---\nschema_version: "1.4"\ndate: "2026-11-22"\nbaseline:\n  source: null\n---\n\n'
        "# Threat Model: Floor Fixture\n\n## 1. System Overview\n\nSynthetic.\n\n## 7. Recommended Actions\n\n"
        "| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |\n"
        "|---|---|---|---|---|---|---|---|---|\n" + rows + "\n"
    )


def _seed(workdir, threats=None):
    """A fresh working tree: byte-identical inputs and fixed mtimes, so out_snapshot repeats too."""
    if workdir.exists():
        shutil.rmtree(str(workdir))
    (workdir / "run").mkdir(parents=True)
    (workdir / "docs" / "security").mkdir(parents=True)
    files = {
        workdir / "run" / "threats.md": (_threats_md() if threats is None else threats).encode("utf-8"),
        workdir / "run" / "risk-scores.md": b"# earlier run\n",
        workdir / "run" / "risk-scores.sarif": b'{"earlier": true}\n',
        workdir / "docs" / "security" / "architecture.md": b"# Architecture\n",
    }
    for path, data in files.items():
        path.write_bytes(data)
        os.utime(str(path), ns=(1700000000 * 10 ** 9, 1700000000 * 10 ** 9))


def _tree(root):
    """{normalized relative path: normalized text} for every file under ``root``."""
    state = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            state[_normalize(path.relative_to(root).as_posix())] = _normalize(path.read_bytes().decode("utf-8"))
    return state


def _drive_tachi_stage(interp, workdir):
    """plan -> reconcile (halves) -> reconcile (complete) -> fail -> architecture-source.

    Returns the steps and the final tree, normalized. Each step's exit code is checked by the caller
    against EXPECTED_CODES, so that two identical crashes can't pass for byte-identical output.
    """
    _seed(workdir)
    script = SCRIPTS_DIR / "tachi-stage.py"
    out = workdir / "run"
    steps = []

    def step(args, cwd=workdir):
        proc = interp.run(script, args, cwd)
        steps.append({"args": _normalize(" ".join(str(a) for a in args)), "code": proc.returncode,
                      "stdout": _normalize(proc.stdout), "stderr": _normalize(proc.stderr)})
        return proc

    step(["--version"])
    planned = json.loads(step(["plan", "--stage", "risk-score", "--out", out, "--date", "2026-11-22",
                               "--threats", out / "threats.md"]).stdout)
    plan_id, digest = planned["plan_id"], planned["plan_digest"]

    def plan_args():
        return ["--stage", "risk-score", "--out", out, "--plan", plan_id, "--plan-digest", digest]

    first = step(["reconcile"] + plan_args())  # nothing written: the one batch is missing, so it halves
    halved = json.loads(first.stdout)
    digest = halved["plan_digest"]
    for wave in halved["waves"]:
        for batch in wave:
            _write_valid_part(batch["input_path"])
    final = step(["reconcile"] + plan_args())
    digest = json.loads(final.stdout)["plan_digest"]

    (out / "risk-scores.md").write_bytes(b"# a render that failed half way\n")
    step(["fail"] + plan_args() + ["--reason", "render-failed", "--detail", "floor test"])

    step(["architecture-source", "--threats", out / "threats.md", "--architecture", "docs/security/architecture.md"])
    return steps, _tree(workdir)


# ---- render-risk-scores.py (T050): the reference set gets a trust zone and an Affected Assets block, so a clean run
# ---- exits 0 and the two runs compare on a whole render, the SARIF and the stage record included.

_FLOOR_ZONE = "Edge DMZ"


def _floor_threats_md():
    zones = (
        "## 2. Trust Boundaries\n\n### Trust Zones\n\n| Zone | Trust Level | Components |\n|------|-------------|------------|\n"
        "| %s | Semi-Trusted | %s |\n\n" % (_FLOOR_ZONE, ", ".join("Gateway %d" % n for n in range(1, len(_FINDINGS) + 1))))
    assets = ("\n## Affected Assets\n\n| Finding ID | Affected Assets |\n|------------|-----------------|\n"
              + "\n".join("| %s | [] |" % fid for fid in _FINDINGS) + "\n")
    return _threats_md().replace("## 7. Recommended Actions", zones + "## 7. Recommended Actions") + assets


def _floor_item(finding_id):
    """A scorer item that names the zone, and whose prose uses a slot, so the renderer's resolver runs in the child."""
    item = _scorer_item(finding_id)
    item["reachability"] = {"zone": _FLOOR_ZONE, "trust_level": "Semi-Trusted", "auth_barriers": 1, "network_boundaries": 1}
    item["rationale"]["cvss"] = "The base score is {{score:cvss_base}} for {{name:component}}."
    return item


def _carry_threats_md():
    """The first run's threat model with every finding UNCHANGED, and one NEW finding (S-2) beside them."""
    new_row = "| S-2 | NEW | Category | \u2014 | Gateway 1 | L4 | Threat text for S-2 | High | Mitigation for S-2 |\n"
    text = _floor_threats_md().replace("| NEW |", "| UNCHANGED |")
    return text.replace("|\n\n## Affected Assets", "|\n" + new_row + "\n## Affected Assets") + "| S-2 | [] |\n"


def _drive_render_risk_scores(interp, workdir):
    """--version -> plan -> reconcile (complete) -> render, then the same three steps again beside it as a baseline-aware run.

    The render replaces the seeded earlier outputs. The second run reads the first's own ``risk-scores.md``, so the tolerant
    reader, the vector check, the recompute and the governance of a carried finding run under the same block (T045, T046),
    and one NEW finding gives the agent a unit to score.
    """
    _seed(workdir, _floor_threats_md())
    stage, render = SCRIPTS_DIR / "tachi-stage.py", SCRIPTS_DIR / "render-risk-scores.py"
    out = workdir / "run"
    steps = []

    def step(script, args):
        proc = interp.run(script, args, workdir)
        steps.append({"args": _normalize(" ".join(str(a) for a in args)), "code": proc.returncode,
                      "stdout": _normalize(proc.stdout), "stderr": _normalize(proc.stderr)})
        return proc

    def run_stage(directory, date, extra):
        planned = json.loads(step(stage, ["plan", "--stage", "risk-score", "--out", directory, "--date", date, "--threats", directory / "threats.md",
                                          "--architecture", "docs/security/architecture.md"] + extra).stdout)
        for wave in planned["waves"]:
            for batch in wave:
                _write_valid_part(batch["input_path"], _floor_item)
        reconciled = step(stage, ["reconcile", "--stage", "risk-score", "--out", directory, "--plan", planned["plan_id"],
                                  "--plan-digest", planned["plan_digest"]])
        step(render, ["--out", directory, "--plan", planned["plan_id"], "--plan-digest", json.loads(reconciled.stdout)["plan_digest"]])

    step(render, ["--version"])
    run_stage(out, "2026-11-22", [])
    second = workdir / "run2"
    second.mkdir()
    (second / "threats.md").write_bytes(_carry_threats_md().encode("utf-8"))
    os.utime(str(second / "threats.md"), ns=(1700000000 * 10 ** 9, 1700000000 * 10 ** 9))
    run_stage(second, "2026-11-23", ["--baseline-dir", out])
    return steps, _tree(workdir)


# ---- render-compensating-controls.py (T036, for T035): the controls stage over the scorer's own risk-scores.md. The planner's
# ---- two readers (risk-scores.md through its source_file, and the baseline's persisted results) run in the blocked interpreter too.

_FLOOR_CATEGORIES = ("authentication", "input-validation", "rate-limiting", "encryption", "logging-audit", "csrf-protection",
                     "csp-security-headers", "access-control")
_FLOOR_CARRIED = ("control_status", "control_category", "confidence", "evidence", "matrix_row", "recommendation_body")


def _floor_controls_item(finding_id, row):
    """What the controls agent writes for one unit row: an UNCHANGED finding's result, copied from its row, or a fresh judgment.

    The fresh one follows the readings of ``test_sarif_identity.py`` for the shapes the contract leaves to the agent: a
    pipe-bordered ``matrix_row`` of 11 cells in the K8 order with slot tokens in the four computed ones, and a body of the
    four keys. Its evidence cites ``src/gateway.py``, which the driver makes under the scanned directory.
    """
    if row.get("delta_status") == "UNCHANGED" and all(key in row for key in _FLOOR_CARRIED):
        return dict({key: row[key] for key in _FLOOR_CARRIED}, finding_id=finding_id, carried_forward=True)
    seed = sum(ord(char) for char in finding_id)
    status = ("found", "partial", "missing")[seed % 3]
    category = _FLOOR_CATEGORIES[seed % len(_FLOOR_CATEGORIES)]
    display = {"found": "Control Found", "partial": "Partial Control", "missing": "No Control Found"}[status]
    cells = [finding_id, "\u2014", row.get("component", "Gateway"), "L4", "A synthetic threat to the component.", "{{score:inherent}}",
             "{{band:inherent}}", display, category.replace("-", " ").title(), "{{score:residual}}", "{{band:residual}}"]
    return {
        "finding_id": finding_id, "control_status": status, "control_category": category, "carried_forward": False,
        "confidence": None if status == "missing" else "High",
        "evidence": [] if status == "missing" else [{
            "file": "src/gateway.py", "line": 3, "language": "python",
            "snippet": "def check(request):\n    return verify(request.token)  # a < b & c",
            "summary": "The handler verifies the caller before it runs."}],
        "matrix_row": "| " + " | ".join(cells) + " |",
        "recommendation_body": None if status == "found" else (
            "**What to Implement**: Add a check in front of every handler.\n\n**Where to Implement**: src/gateway.py\n\n"
            "**Reference Patterns**: One shared middleware that every route passes through.\n\n"
            "**Effort Estimate**: Medium \u2014 one new module."),
    }


def _write_controls_part(batch_input_path):
    batch_input = json.loads(Path(batch_input_path).read_text(encoding="utf-8"))
    rows = {row["finding_id"]: row for row in batch_input["units"]}
    part = {
        "schema": "tachi.part/1", "plan_id": batch_input["plan_id"], "batch_id": batch_input["batch_id"], "stage": batch_input["stage"],
        "agent_type": batch_input["agent_type"], "finding_ids": list(batch_input["finding_ids"]),
        "items": [_floor_controls_item(fid, rows[fid]) for fid in batch_input["finding_ids"]], "fragments": [],
    }
    target = Path(batch_input["part_path"])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(part), encoding="utf-8")


def _drive_render_compensating_controls(interp, workdir):
    """--version, then for a first run and again for a second run that carries the first's findings: the scorer (plan, reconcile,
    render), then the controls stage (plan, reconcile, render) over the risk-scores.md it wrote.

    The second run names the first as its baseline, so the controls planner reads the first run's persisted results from its
    ``compensating-controls.md`` (T143's reader) and puts each UNCHANGED finding's result in its unit row, where the agent copies it.
    What this assumes of ``render-compensating-controls.py`` (T035's) is the clean case: it exits 0 on both runs, because the
    architecture file is named and valid, every evidence file exists under the scanned directory, and the first run persisted
    its results. If a reading of T035's differs, change the item here and not the planner.
    """
    _seed(workdir, _floor_threats_md())
    (workdir / "app" / "src").mkdir(parents=True)
    (workdir / "app" / "src" / "gateway.py").write_text("# a synthetic module of the scanned codebase\n", encoding="utf-8")
    stage, scorer, render = SCRIPTS_DIR / "tachi-stage.py", SCRIPTS_DIR / "render-risk-scores.py", SCRIPTS_DIR / "render-compensating-controls.py"
    out = workdir / "run"
    steps = []

    def step(script, args):
        proc = interp.run(script, args, workdir)
        steps.append({"args": _normalize(" ".join(str(a) for a in args)), "code": proc.returncode,
                      "stdout": _normalize(proc.stdout), "stderr": _normalize(proc.stderr)})
        return proc

    def run_stage(name, script, directory, date, pointers, write_part):
        planned = json.loads(step(stage, ["plan", "--stage", name, "--out", directory, "--date", date, "--architecture", "docs/security/architecture.md"]
                                  + pointers).stdout)
        for wave in planned["waves"]:
            for batch in wave:
                write_part(batch["input_path"])
        reconciled = step(stage, ["reconcile", "--stage", name, "--out", directory, "--plan", planned["plan_id"], "--plan-digest", planned["plan_digest"]])
        step(script, ["--out", directory, "--plan", planned["plan_id"], "--plan-digest", json.loads(reconciled.stdout)["plan_digest"]])

    def run_both(directory, date, baseline):
        extra = ["--baseline-dir", baseline] if baseline is not None else []
        run_stage("risk-score", scorer, directory, date, ["--threats", directory / "threats.md"] + extra,
                  lambda path: _write_valid_part(path, _floor_item))
        run_stage("compensating-controls", render, directory, date, ["--risk-scores", directory / "risk-scores.md", "--target", workdir / "app"] + extra,
                  _write_controls_part)

    step(render, ["--version"])
    run_both(out, "2026-11-22", None)
    second = workdir / "run2"
    second.mkdir()
    (second / "threats.md").write_bytes(_carry_threats_md().encode("utf-8"))
    os.utime(str(second / "threats.md"), ns=(1700000000 * 10 ** 9, 1700000000 * 10 ** 9))
    run_both(second, "2026-11-23", out)
    return steps, _tree(workdir)


# ---- PR 2's four entries (T150). Each runs one small synthetic world, written byte for byte the same for both interpreters. The SARIF generator
# ---- and the chain script read a threat model (the chain script also an inventory), and the joiner and the assembler take plans, batch inputs
# ---- and parts. None of them reads the clock, a random source or a file's mtime, so a difference between the two runs can only be what an
# ---- unimportable ``yaml`` changed. The planner of PR 2's batch stages (``tachi-stage.py plan --stage threats-md|trees|report``) is another lane's
# ---- and lands in its own wave, so a stand-in writes those plans, as the entries' own test modules do: this module then waits on no planner, and
# ---- what a stand-in gets wrong an entry refuses in its own words, which the failing assertion prints.


def _shipped():
    """``tachi_parts`` and ``tachi_parsers``, imported in this process only. The stand-in planners take the document layout, the schemas, the version and
    the reference digest from them, so that a stand-in can't drift from what an entry reads. The entries run in the children above, which import what they
    import themselves."""
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    import tachi_parsers
    import tachi_parts

    return tachi_parts, tachi_parsers


class _Steps(object):
    """One driver's steps in one interpreter: each one's arguments, exit code and streams, normalized, in the order run."""

    def __init__(self, interp, cwd):
        self.interp, self.cwd, self.steps = interp, cwd, []

    def __call__(self, script, args):
        proc = self.interp.run(script, args, self.cwd)
        self.steps.append({"args": _normalize(" ".join(str(a) for a in args)), "code": proc.returncode,
                           "stdout": _normalize(proc.stdout), "stderr": _normalize(proc.stderr)})
        return proc


def _fresh(workdir):
    """An empty ``workdir``. Both interpreters run in this one path, so the absolute paths that the files and the streams record are alike."""
    if workdir.exists():
        shutil.rmtree(str(workdir))
    workdir.mkdir(parents=True)


def _put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


def _put_json(path, document):
    """``document`` as the planner writes one (sorted keys, a two-space indent). Returns the SHA-256 of what it wrote."""
    data = (json.dumps(document, indent=2, sort_keys=True) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def _plan_input(path):
    data = path.read_bytes()
    return {"path": str(path), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def _batch_stage(out, stage, agent, plan_id, batches, params, inputs, batch_size):
    """A batch stage's plan, its pointer, and each batch's input and part, as ``plan`` and the agents leave them once every batch is ``done`` at its first
    attempt. Returns the plan's digest, which the entry takes as ``--plan-digest``.

    A batch is ``{"units": [...], "items": [...], "fragments": [...], "trees": {finding ID: path}}``, the last three optional, and its finding IDs are the
    ones that its units name. The layout, the schemas and the version are the shipped helpers', so only the contents are written here.
    """
    tp = _shipped()[0]
    entries = []
    for number, batch in enumerate(batches, 1):
        units, batch_id = batch["units"], "B%03d" % number
        finding_ids = [unit["finding_id"] for unit in units if "finding_id" in unit]
        part = tp.part_path(str(out), stage, plan_id, batch_id, 1)
        digest = _put_json(Path(tp.input_path(str(out), stage, plan_id, batch_id)), {
            "schema": tp.BATCH_INPUT_SCHEMA, "plan_id": plan_id, "batch_id": batch_id, "stage": stage, "agent_type": agent, "finding_ids": finding_ids,
            "attempt": 1, "part_path": part, "tree_paths": batch.get("trees", {}), "units": units, "refs": {}, "params": params})
        _put_json(Path(part), {"schema": tp.PART_SCHEMA, "plan_id": plan_id, "batch_id": batch_id, "stage": stage, "agent_type": agent,
                               "finding_ids": finding_ids, "items": batch.get("items", []), "fragments": batch.get("fragments", [])})
        entries.append({"batch_id": batch_id, "parent": None, "attempt": 1, "finding_ids": finding_ids, "input_sha256": digest, "state": "done"})
    digest = _put_json(Path(tp.plan_path(str(out), stage, plan_id)), {
        "schema": tp.PLAN_SCHEMA, "plan_id": plan_id, "stage": stage, "agent_type": agent, "created_utc": "2026-11-25T09:00:00Z", "tachi_version": tp.VERSION,
        "inputs": inputs, "refs": {}, "architecture_warning": None, "params": params, "batch_size": batch_size,
        "unit_count": sum(len(batch["units"]) for batch in batches), "preimage": {}, "out_snapshot": None,
        "retry_budget": {"limit": 2 * len(entries), "used": 0}, "batches": entries})
    _put_json(Path(tp.pointer_path(str(out), stage)), {"schema": tp.POINTER_SCHEMA, "plan_id": plan_id})
    return digest


# ---- generate-threats-sarif.py (T100): one threat model, with and without a baseline. The first is the reference set that the scorer's driver uses
# ---- (nine findings, a zone, an Affected Assets block). The second carries those findings beside a new one, names its baseline run, groups two
# ---- findings (Section 4a) and lists one as resolved (Section 4c), so the baseline state, the correlation properties and the resolved check run too.

def _aware_threats_md():
    text = _carry_threats_md().replace(
        "  source: null", '  source: "run/threats.md"\n  date: "2026-11-22"\n  finding_count: 9\n  run_id: "2026-11-22T10-15-00"', 1)
    groups = ("## 4a. Correlated Findings\n\n| Group | Findings | Component | Threat Summary | Risk Level |\n|---|---|---|---|---|\n"
              "| CG-1 | S-1, T-9 | Gateway 9 | Related weaknesses at the edge | High |\n\n")
    resolved = ("## 4c. Resolved Findings\n\n| ID | Component | Threat | Last Risk Level | Resolution Reason |\n|---|---|---|---|---|\n"
                "| I-7 | Legacy Cache | Stale entries leak data | Medium | Component removed from the architecture |\n\n")
    return text.replace("## 7. Recommended Actions", groups + resolved + "## 7. Recommended Actions")


def _drive_generate_threats_sarif(interp, workdir):
    """--version, then ``--threats FILE --out DIR --architecture PATH`` over the first threat model and again over the baseline-aware one."""
    _seed(workdir, _floor_threats_md())
    script, step = SCRIPTS_DIR / "generate-threats-sarif.py", _Steps(interp, workdir)
    architecture = "docs/security/architecture.md"
    step(script, ["--version"])
    step(script, ["--threats", workdir / "run" / "threats.md", "--out", workdir / "run", "--architecture", architecture])
    _put(workdir / "run2" / "threats.md", _aware_threats_md())
    step(script, ["--threats", workdir / "run2" / "threats.md", "--out", workdir / "run2", "--architecture", architecture])
    return step.steps, _tree(workdir)


# ---- join-threats-md.py (T106): the ``threats-md`` stage over a section manifest. The first world is a first run of three findings (a STRIDE, an
# ---- Agentic and an LLM one) and a row in each of Section 1's two tables. The second has a baseline: a resolved finding, and a row in each of
# ---- Section 8's tables.

_JOIN_PLAN = "20261125T090000Z-0a1b2c3d4e5f"
_JOIN_LAYER = "L4 \u2014 Deployment Infrastructure"
# In S-2 order: (ID, component, risk level, pattern, OWASP reference, status in a baseline-aware run).
_JOIN_FINDINGS = (("S-1", "Gateway", "Critical", "\u2014", "ASI-01", "NEW"),
                  ("AG-1", "Planner Agent", "High", "temporal_attack", "ASI-06", "UNCHANGED"),
                  ("LLM-1", "Planner Agent", "Medium", "\u2014", "LLM01:2026", "UPDATED"))
_JOIN_RESOLVED = {"finding_id": "I-7", "component": "Legacy Cache", "threat": "Stale entries leak data", "last_risk_level": "Medium",
                  "resolution_reason": "Component removed from the architecture"}
_JOIN_MATRIX = {"Critical": ("HIGH", "HIGH"), "High": ("MEDIUM", "HIGH"), "Medium": ("MEDIUM", "MEDIUM")}  # likelihood and impact of a risk level


def _join_values(finding, baseline):
    """Every value that a finding's rows can hold, under the key names of ``tachi_parts.THREATS_MD_SECTIONS``."""
    finding_id, component, risk, pattern, owasp, status = finding
    likelihood, impact = _JOIN_MATRIX[risk]
    return {"finding_id": finding_id, "status": status if baseline else "NEW", "component": component, "maestro_layer": _JOIN_LAYER,
            "threat": "Threat %s against %s" % (finding_id, component), "likelihood": likelihood, "impact": impact, "risk_level": risk,
            "mitigation": "Mitigation for %s" % finding_id, "owasp_reference": owasp, "pattern": pattern}


def _join_world(out, baseline):
    """The section manifest, and a ``threats-md`` plan with a part for every table that has a row. Returns the plan's digest."""
    tp = _shipped()[0]
    rows = {section.key: 0 for section in tp.THREATS_MD_SECTIONS if section.keyed == "row"}
    rows.update(components=1, data_flows=1, lifecycle=int(baseline), baseline_reference=int(baseline))
    batches = []
    for section in tp.THREATS_MD_SECTIONS:
        if section.keyed == "row":
            units = [{"section": section.key, "row": number} for number in range(1, rows[section.key] + 1)]
            items = [{name: "%s %d" % (name, unit["row"]) for name in section.keys} for unit in units]
        elif section.keyed == "resolved":
            units = [{"section": section.key, "finding_id": _JOIN_RESOLVED["finding_id"]}] if baseline else []
            items = [dict(_JOIN_RESOLVED)] if baseline else []
        else:
            chosen = [f for f in _JOIN_FINDINGS if section.keyed == "open" or f[0].partition("-")[0] in section.prefixes]
            units = [{"section": section.key, "finding_id": f[0]} for f in chosen]
            items = [{name: _join_values(f, baseline)[name] for name in section.keys} for f in chosen]
        if units:
            batches.append({"units": units, "items": items})
    front_baseline = ({"source": "baseline/threats.md", "date": "2026-11-18", "finding_count": 4, "run_id": "2026-11-18T09-00-00"} if baseline
                      else {"source": None, "date": None, "finding_count": None, "run_id": None})
    manifest = out / tp.BUILD_DIR / "sections.json"  # the manifest's fixed place, which the plan records among its inputs
    _put_json(manifest, {
        "schema": tp.SECTIONS_SCHEMA,
        "frontmatter": {"date": "2026-11-25", "input_format": "mermaid", "classification": "confidential", "run_id": "2026-11-25T09-00-00",
                        "baseline": front_baseline, "coverage_gate": {"status": "pass", "gaps": []}},
        "open": [f[0] for f in _JOIN_FINDINGS], "resolved": [_JOIN_RESOLVED["finding_id"]] if baseline else None, "rows": rows})
    return _batch_stage(out, "threats-md", "tachi-orchestrator", _JOIN_PLAN, batches, {"scoring_date": "2026-11-25"},
                        {"sections": _plan_input(manifest)}, None)


def _drive_join_threats_md(interp, workdir):
    """--version, then ``--out DIR PLAN`` for the first world and again for the baseline-aware one."""
    _fresh(workdir)
    script, step = SCRIPTS_DIR / "join-threats-md.py", _Steps(interp, workdir)
    step(script, ["--version"])
    for name, baseline in (("run", False), ("run2", True)):
        step(script, ["--out", workdir / name, "--plan", _JOIN_PLAN, "--plan-digest", _join_world(workdir / name, baseline)])
    return step.steps, _tree(workdir)


# ---- assemble-report.py (T108, T109): the ``trees`` stage, then the ``report`` stage that pins it. Two findings, a Critical one with a tree and a
# ---- Medium one without; a first run with no chain, so Section 6 prints the outcome and the report holds no chain part.

_ASM_TREES, _ASM_REPORT = "20261125T100000Z-aaaaaaaaaaaa", "20261125T110000Z-bbbbbbbbbbbb"
# (ID, the Section 7 category, the report's category key, risk level, component, threat, mitigation)
_ASM_FINDINGS = (("S-1", "Spoofing", "spoofing", "Critical", "Gateway", "Session token replay", "Bind each token to its client"),
                 ("T-1", "Tampering", "tampering", "Medium", "Order Service", "Order payload tampering", "Sign every order payload"))


def _asm_threats_md():
    rows = "\n".join("| %s | NEW | %s | \u2014 | %s | L4 | %s | %s | %s |" % (fid, title, component, threat, risk, mitigation)
                     for fid, title, _key, risk, component, threat, mitigation in _ASM_FINDINGS)
    return ('---\nschema_version: "1.4"\ndate: "2026-11-25"\ninput_format: "mermaid"\nclassification: "confidential"\nrun_id: "2026-11-25T09-00-00"\n'
            'baseline:\n  source: null\n  date: null\n  finding_count: null\n  run_id: null\ncoverage_gate:\n  status: "pass"\n  gaps: []\n---\n\n'
            "# Threat Model Report\n\n## 7. Recommended Actions\n\n"
            "| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |\n"
            "|---|---|---|---|---|---|---|---|---|\n" + rows + "\n\n"
            "## Attack Chain Outcome\n\n**Attack chain outcome**: 0 chains passed filter (no candidate links); candidates 0\n")


def _asm_tree_text(finding_id):
    """A standalone tree file as the tree agent writes it: a header, then one fenced Mermaid block with a non-ASCII label, so a copy is shown byte for byte."""
    return ("# Attack Tree: %s\n\n**Risk Level**: Critical\n**Component**: Gateway\n**Threat**: Session token replay\n\n```mermaid\ngraph TD\n"
            '    Goal["[GOAL] Attack on %s"]\n    Goal --> A["[OR] First route"]\n    A --> A1["Caf\u00e9 leaf"]\n```\n' % (finding_id, finding_id))


def _asm_trees_world(out):
    """threats.md and a ``trees`` plan with one batch, whose agent wrote the tree of S-1. Returns the plan's digest and the reference digest (the report's too)."""
    tp, parsers = _shipped()
    threats = _put(out / "threats.md", _asm_threats_md())
    reference = tp.reference_digest(parsers.parse_reference_set(threats.read_text(encoding="utf-8")))
    tree = Path(tp.plan_dir(str(out), "trees", _ASM_TREES)) / "trees" / "s-1-attack-tree.md"
    _put(tree, _asm_tree_text("S-1"))
    unit = {"finding_id": "S-1", "delta_status": "NEW", "action": "generated_fresh"}
    params = {"scoring_date": "2026-11-25", "rule_applied": "no-baseline", "reference_digest": reference}
    digest = _batch_stage(out, "trees", "tachi-attack-tree-delta", _ASM_TREES, [{"units": [unit], "items": [dict(unit)], "trees": {"S-1": str(tree)}}],
                          params, {"threats": _plan_input(threats)}, 12)
    return digest, reference


def _asm_report_world(out, reference):
    """A ``report`` plan that pins the trees plan and the manifest that ``trees`` wrote: one part for each required section, then the findings'. Returns its digest."""
    tp = _shipped()[0]

    def sentence(name):
        return "A fixed sentence for the %s." % name.replace(".", " ").replace("_", " ")

    def section(name, keys, texts=None):
        return {"units": [{"section": name, "key": key} for key in keys],
                "fragments": [{"slot_key": key, "text": (texts or {}).get(key) or sentence(key)} for key in keys]}

    def row(name, finding):
        return {"section": name, "finding_id": finding[0], "component": finding[4], "threat": finding[5], "risk_level": finding[3],
                "mitigation": finding[6], "agentic_pattern": "none", "delta_status": "NEW"}

    themes = {"units": [{"section": "cross_cutting_themes", "key": "themes"}],
              "fragments": [{"slot_key": "theme.1.title", "text": "A shared weakness in identity handling"},
                            {"slot_key": "theme.1.body", "text": "Both findings come from one missing check between the gateway and the services behind it."}]}
    analysis = {"units": [dict(row("threat_analysis", f), tree=f[3] == "Critical") for f in _ASM_FINDINGS],
                "items": [{"finding_id": f[0], "narrative": "A fixed account of {{finding:%s}}." % f[0],
                           "tree_summary": ("A fixed summary of the tree of {{finding:%s}}." % f[0]) if f[3] == "Critical" else None} for f in _ASM_FINDINGS]}
    roadmap = {"units": [row("remediation_roadmap", f) for f in _ASM_FINDINGS],
               "items": [{"finding_id": "S-1", "effort": "Medium", "dependencies": None},
                         {"finding_id": "T-1", "effort": "Low", "dependencies": "Follows the fix for {{finding:S-1}}."}]}
    slots = {"risk_posture": "The model holds {{count:open}} open findings, and {{pct:critical}} percent of them are Critical.",  # the slots resolve at assembly
             "top_threats": "The top threat is {{finding:S-1}} on {{name:component:S-1}}, rated {{band:risk:S-1}}."}
    batches = [section("exec_summary", ["risk_posture", "top_threats", "key_recommendations"], slots),
               section("architecture_overview", ["system_context", "trust_boundaries"]),
               section("threat_categories", ["category." + f[2] for f in _ASM_FINDINGS]), themes, analysis, roadmap]
    inputs = {"threats": _plan_input(out / "threats.md"), "trees_plan": _plan_input(Path(tp.plan_path(str(out), "trees", _ASM_TREES))),
              "tree_manifest": _plan_input(out / "attack-trees" / ".manifest.json")}
    params = {"scoring_date": "2026-11-25", "reference_digest": reference, "trees_plan_id": _ASM_TREES}
    return _batch_stage(out, "report", "tachi-threat-report", _ASM_REPORT, batches, params, inputs, None)


def _drive_assemble_report(interp, workdir):
    """--version, ``trees`` over the trees plan, then ``report`` over a report plan that pins the trees plan and the manifest that ``trees`` wrote."""
    _fresh(workdir)
    script, step, out = SCRIPTS_DIR / "assemble-report.py", _Steps(interp, workdir), workdir / "run"
    step(script, ["--version"])
    digest, reference = _asm_trees_world(out)
    trees = step(script, ["trees", "--run-dir", out, "--plan", _ASM_TREES, "--plan-digest", digest])
    if trees.returncode != 0:  # the report plan pins the manifest that ``trees`` writes. The caller's check of the codes then names this step, with its stderr
        return step.steps, _tree(workdir)
    step(script, ["report", "--run-dir", out, "--plan", _ASM_REPORT, "--plan-digest", _asm_report_world(out, reference)])
    return step.steps, _tree(workdir)


# ---- attack-chains.py (T116, T117): Phase 3.5's three modes over one run. T-1 (layer 5, High), T-2 (layer 6, Medium) and E-1 (layer 3, Critical) lie
# ---- along two flows, which gives one chain of three. ``plan`` forms it and prints it, the driver writes the title and narrative that the orchestrator
# ---- would, ``render`` writes attack-chains.md and the outcome record, and ``check`` finds the two in agreement.

_CHAIN_PLAN = "20261125T120000Z-0123456789ab"  # the run-level plan, for check's hand-off file
# (ID, the Section 7 category, component, MAESTRO layer, risk level)
_CHAIN_FINDINGS = (("T-1", "Tampering", "ingest-gateway", 5, "High"), ("T-2", "Tampering", "policy-checker", 6, "Medium"),
                   ("E-1", "Elevation of Privilege", "agent-core", 3, "Critical"))
_CHAIN_LAYERS = {3: "Agent Framework", 5: "Evaluation and Observability", 6: "Security and Compliance"}
_CHAIN_FLOWS = (("ingest-gateway", "policy-checker"), ("policy-checker", "agent-core"))
_CHAIN_ID = re.compile(r"CHAIN-[0-9]{3,6}")


def _chain_threats_md():
    rows = "\n".join("| %s | NEW | %s | \u2014 | %s | L%d \u2014 %s | A synthetic weakness of %s. | %s | Close the gap behind %s. |"
                     % (fid, title, component, layer, _CHAIN_LAYERS[layer], component, risk, fid) for fid, title, component, layer, risk in _CHAIN_FINDINGS)
    return ('---\nschema_version: "1.4"\ndate: "2026-11-25"\ninput_format: "free-text"\nclassification: "confidential"\nrun_id: "2026-11-25T09-00-00"\n'
            'baseline:\n  source: null\n  date: null\n  finding_count: null\n  run_id: null\ncoverage_gate:\n  status: "pass"\n  gaps: []\n---\n\n'
            "# Threat Model Report\n\n## 5. Coverage Matrix\n\nThe coverage tables are left out of this file.\n\n## 7. Recommended Actions\n\n"
            "| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |\n"
            "|---|---|---|---|---|---|---|---|---|\n" + rows + "\n\n## Affected Assets\n\n| Finding ID | Affected Assets |\n|---|---|\n"
            + "\n".join("| %s | [] |" % f[0] for f in _CHAIN_FINDINGS) + "\n")


def _chain_inventory():
    components = [{"name": component, "dfd_type": "Process", "maestro_layer": "L%d" % layer, "description": "A synthetic component."}
                  for _fid, _title, component, layer, _risk in _CHAIN_FINDINGS]
    return {"schema": _shipped()[0].INVENTORY_SCHEMA, "components": components,
            "data_flows": [{"source": a, "destination": b, "data": "Task requests", "protocol": "HTTPS"} for a, b in _CHAIN_FLOWS],
            "trust_zones": [{"name": "Test Zone", "components": [c["name"] for c in components]}]}


def _drive_attack_chains(interp, workdir):
    _fresh(workdir)
    tp = _shipped()[0]
    script, step, run = SCRIPTS_DIR / "attack-chains.py", _Steps(interp, workdir), workdir / "run"
    _put(run / "threats.md", _chain_threats_md())
    _put_json(run / tp.BUILD_DIR / "phase1" / "inventory.json", _chain_inventory())
    step(script, ["--version"])
    planned = step(script, ["plan", "--run-dir", run])
    texts = {chain_id: {"title": "A path from an exposed weakness to its final impact",
                        "narrative": "The attacker starts at {{finding:T-1}} on {{name:component:T-1}} and reaches {{count:members}} findings across "
                                     "{{count:layers}} layers, so each step prepares the one after it."}  # the slots resolve at render
             for chain_id in dict.fromkeys(_CHAIN_ID.findall(planned.stdout))}
    _put_json(run / tp.BUILD_DIR / "chains" / "narratives.json", {"schema": tp.CHAIN_NARRATIVES_SCHEMA, "narratives": texts})
    step(script, ["render", "--run-dir", run])
    (run / tp.BUILD_DIR / "threat-model" / _CHAIN_PLAN / "checks").mkdir(parents=True)  # as the run-level plan leaves it
    step(script, ["check", "--run-dir", run, "--plan", _CHAIN_PLAN])
    return step.steps, _tree(workdir)


# Exit codes of the steps above. tachi-stage.py: --version, plan, reconcile (halves), reconcile (complete), fail,
# architecture-source. render-risk-scores.py: --version, then plan, reconcile (complete) and render for a first run and again
# for a second run that carries the first's findings. render-compensating-controls.py: --version, then for each of those two
# runs the scorer's three steps and the controls stage's three. PR 2's: generate-threats-sarif.py: --version, then a first run
# and a baseline-aware one. join-threats-md.py: --version, then a first run and a baseline-aware one. assemble-report.py:
# --version, trees, report. attack-chains.py: --version, plan, render, check.
EXPECTED_CODES = {"tachi-stage.py": [0, 0, 3, 0, 0, 0], "render-risk-scores.py": [0, 0, 0, 0, 0, 0, 0],
                  "render-compensating-controls.py": [0] + [0] * 6 + [0] * 6,
                  "generate-threats-sarif.py": [0, 0, 0], "join-threats-md.py": [0, 0, 0], "assemble-report.py": [0, 0, 0],
                  "attack-chains.py": [0, 0, 0, 0]}

# What each PR 2 entry's clean run writes, as paths in the working tree. No driver seeds any of them, so a run that exits 0 and writes none (a world that
# drifted into a path with nothing to do) fails here, and can't pass by comparing two runs of the same nothing.
OUTPUTS = {"generate-threats-sarif.py": ("run/threats.sarif", "run2/threats.sarif"), "join-threats-md.py": ("run/threats.md", "run2/threats.md"),
           "assemble-report.py": ("run/attack-trees/.manifest.json", "run/attack-trees/s-1-attack-tree.md", "run/threat-report.md"),
           "attack-chains.py": ("run/attack-chains.md",)}
# The words that every fixed sentence of the two narrative stages shares (``tachi_parts.REPORT_FALLBACKS`` and ``attack-chains.py``'s fixed narrative). A clean
# world's outputs hold none: a slot that failed to resolve would leave one, and the lookup behind it would then not run in this module's children.
FALLBACK_WORDS = "broke the narrative rules"

# One driver per entry script, each `(Interpreter, workdir) -> (steps, tree)`. A later wave adds its entry's
# driver here. The controls renderer's driver (T036) was written first and skipped while the script was
# PLANNED and missing. W3 (T039) moved the script to REQUIRED_NOW, so the driver runs and a missing script fails.
# T150 added PR 2's four, and W3's `check-threat-model.py` (T096, wired by T098) takes its driver here when it lands.
CORE_PATH_DRIVERS = {"tachi-stage.py": _drive_tachi_stage, "render-risk-scores.py": _drive_render_risk_scores,
                     "render-compensating-controls.py": _drive_render_compensating_controls,
                     "generate-threats-sarif.py": _drive_generate_threats_sarif, "join-threats-md.py": _drive_join_threats_md,
                     "assemble-report.py": _drive_assemble_report, "attack-chains.py": _drive_attack_chains}


def _entry_scripts():
    return [name for name in ALL_SCRIPTS if "-" in name]


@pytest.mark.parametrize("name", _entry_scripts())
def test_every_entry_script_has_a_core_path_driver(name):
    _resolve(name)
    assert name in CORE_PATH_DRIVERS, (
        "scripts/%s is an entry and exists, so add its driver to CORE_PATH_DRIVERS and its codes to EXPECTED_CODES" % name
    )


@pytest.mark.parametrize("name", sorted(CORE_PATH_DRIVERS))
def test_core_path_output_is_byte_identical_with_yaml_unimportable(name, shim, tmp_path):
    _resolve(name)
    driver = CORE_PATH_DRIVERS[name]
    workdir = tmp_path / "work"  # one path for both runs, so absolute paths in the output match

    plain_steps, plain_tree = driver(Interpreter(shim, blocked=False), workdir)
    blocked_steps, blocked_tree = driver(Interpreter(shim, blocked=True), workdir)

    for label, steps in (("unblocked", plain_steps), ("blocked", blocked_steps)):
        codes = [s["code"] for s in steps]
        assert codes == EXPECTED_CODES[name], "%s run of %s exited %s:\n%s" % (label, name, codes, json.dumps(steps, indent=1))
    assert blocked_steps == plain_steps
    assert blocked_tree == plain_tree
    assert plain_tree, "the run wrote nothing, so the comparison proves nothing"
    unwritten = [path for path in OUTPUTS.get(name, ()) if path not in plain_tree]
    assert not unwritten, "the run did not write %s, so the comparison did not cover the entry's work" % ", ".join(unwritten)
    fell_back = [path for path in OUTPUTS.get(name, ()) if FALLBACK_WORDS in plain_tree[path]]
    assert not fell_back, "a fixed sentence replaced the text of the world in %s: one of its slots did not resolve" % ", ".join(fell_back)


def test_the_normalizer_masks_only_what_is_fresh_on_every_run():
    plan = "20261122T101500Z-0123456789ab"
    text = '{"plan_id": "%s", "plan_digest": "%s", "sha256": "%s", "x": 1700000000123456789}' % (plan, "a" * 64, "b" * 64)
    masked = _normalize(text)
    assert plan not in masked and "a" * 64 not in masked and "<NS>" in masked
    assert "<VOLATILE>" in _normalize("reconcile --plan-digest " + "c" * 64) and "c" * 64 not in _normalize("--plan-digest " + "c" * 64)
    assert "b" * 64 in masked, "a digest of stable input must stay visible, or a real difference could hide"


# --------------------------------------------------------------------------- the 3.9 guard, on the runtime floor

@pytest.mark.parametrize("name", _entry_scripts())
def test_entry_scripts_refuse_python_below_39_before_importing_anything(name, shim, tmp_path):
    """Contract: each entry refuses Python below 3.9 before any import, with exit 2 (contracts/cli.md).

    A 3.8 interpreter isn't available to CI, so the child pretends to be one. A fresh interpreter
    shows the half only a process can. Every import statement the script executed is recorded, loaded
    already or not, and only ``__future__`` (a compile-time directive that must lead the file) and
    ``sys`` (the guard's own subject) may precede the refusal.
    """
    path = _resolve(name)
    proc = Interpreter(shim, blocked=False).run(path, ["--version"], tmp_path, mode="old-python")
    assert proc.returncode == 0, proc.stderr
    report = json.loads(proc.stdout.strip().splitlines()[-1])
    assert report["code"] == 2, (report, proc.stderr)
    assert "3.8.18" in proc.stderr, "the refusal must name the version it found: %r" % proc.stderr
    assert sorted(set(report["imports"]) - {"__future__", "sys"}) == [], "an import ran before the guard: %s" % report["imports"]
    assert sorted(set(report["new_modules"]) - {"__future__"}) == [], report["new_modules"]
