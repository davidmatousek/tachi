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

Extending it in a later wave (W2's renderer and scoring-rules module, W3's controls renderer, PR 2's
scripts and T150's rewritten ``generate-threats-sarif.py``):

* Move a script from ``PLANNED`` to ``REQUIRED_NOW`` in the wave that lands it. Until then its checks
  skip with the reason in ``PLANNED``. Once the file exists they run, and they never skip silently.
* Give each new **entry** (a hyphenated script) a driver in ``CORE_PATH_DRIVERS``.
  ``test_every_entry_script_has_a_core_path_driver`` fails until it has one.
* Add a deny-list row when a review finds a post-3.9 API this net missed, with a case in
  ``FLAGGED`` or ``CLEAN`` so the checker keeps its own regression test.

Standard library only, and Python 3.9 syntax (this module itself runs in the 3.9 job).
"""

from __future__ import annotations

import ast
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
# W1's scripts. A missing file is a failure: T012, T013, T014, T015, T016, T018 and T140 write them.
REQUIRED_NOW = (
    "tachi_parts.py",
    "tachi_scoring.py",
    "sarif_common.py",  # exists today; W1 rewrites it as the shared emitter and installs it
    "tachi-stage.py",
)

# Scripts a later wave adds, with the wave that lands each. While one is missing its checks skip with
# this reason. Once it exists the checks run on it, and the move to REQUIRED_NOW is the wave's own
# one-line edit. T150 (PR 2) adds scripts/generate-threats-sarif.py to REQUIRED_NOW, because that
# file exists today and is not "new" until PR 2 rewrites it on the shared emitter.
PLANNED = {
    "tachi_scoring_rules.py": "W2 (lane R1b)",
    "render-risk-scores.py": "W2 (lane R1)",
    "render-compensating-controls.py": "W3 (lane R2)",
    "join-threats-md.py": "PR 2, W2' (lane OS)",
    "attack-chains.py": "PR 2, W2' (lane OC)",
    "assemble-report.py": "PR 2, W2' (lane T)",
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
    pytest.fail("scripts/%s is a W1 script and must exist (S-11, T149)" % name, pytrace=False)


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


def _write_valid_part(batch_input_path):
    batch_input = json.loads(Path(batch_input_path).read_text(encoding="utf-8"))
    part = {
        "schema": "tachi.part/1",
        "plan_id": batch_input["plan_id"],
        "batch_id": batch_input["batch_id"],
        "stage": batch_input["stage"],
        "agent_type": batch_input["agent_type"],
        "finding_ids": list(batch_input["finding_ids"]),
        "items": [_scorer_item(fid) for fid in batch_input["finding_ids"]],
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


def _seed(workdir):
    """A fresh working tree: byte-identical inputs and fixed mtimes, so out_snapshot repeats too."""
    if workdir.exists():
        shutil.rmtree(str(workdir))
    (workdir / "run").mkdir(parents=True)
    (workdir / "docs" / "security").mkdir(parents=True)
    files = {
        workdir / "run" / "threats.md": _threats_md().encode("utf-8"),
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


# Exit codes of the steps above: --version, plan, reconcile (halves), reconcile (complete), fail, architecture-source.
EXPECTED_CODES = {"tachi-stage.py": [0, 0, 3, 0, 0, 0]}

# One driver per entry script, each `(Interpreter, workdir) -> (steps, tree)`. A later wave adds its entry's
# driver here: render-risk-scores.py (W2), render-compensating-controls.py (W3), and PR 2's entries.
CORE_PATH_DRIVERS = {"tachi-stage.py": _drive_tachi_stage}


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
