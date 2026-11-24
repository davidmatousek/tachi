"""Tests for F-374's synthetic fixture and the generator that writes it (T020; spec S-4, ADR-050 D16).

What they pin, in the order S-4 gives it:

* **Byte identity.** The generator, run in-process into a temporary directory, writes exactly the files of
  the committed copy under ``tests/scripts/fixtures/large_arch/``, byte for byte. No test writes into the
  tree, and one proves that a run leaves the committed copy as it was. To refresh the copy after a deliberate
  generator change, run ``python3 tests/scripts/generate_large_arch_fixture.py --out
  tests/scripts/fixtures/large_arch`` and commit the result.
* **Sizing.** Each targeted single-response output is at least twice the 64k output cap, by UTF-8 bytes / 4.
  Every batched path (``risk-score``, ``compensating-controls`` and ``trees``) gets two or more batches at the
  planner's sizes. The sizes are the constants of ``scripts/tachi-stage.py`` (T018), read through
  ``tests/conftest.py``'s ``_load_hyphenated_script`` and never restated here (see ``read_stage_sizes``).
* **The determinism contract** in the generator's docstring, as far as source text can show it: an AST ban on
  every ``random`` method except ``random()`` and ``seed()``, none of the other sources of drift (``hash()``,
  the clock, the environment, the locale, directory order), canonical text, JSON from the generator's own
  serializer, and parts that regenerate alone to the bytes they have in the whole tree.
* **The base set's shape** (S-4's list), and the property that makes it a clean baseline: its scores carry no
  seeded error, no rounding tie and no band boundary.
* **A fixed point of the populator.** Step 1.5 of ``/tachi.risk-score`` runs ``populate-affected-assets.py`` on
  the input ``threats.md`` in place. It must change nothing, or the stage's input digest moves under it (T021(a)).

* **The PR 1 variants (T040, at the end of this module).** Each scenario's expected-outcomes.json is well formed and
  points at committed files; its flag vocabulary is closed; every expected value follows from the shipped arithmetic
  (``scripts/tachi_scoring.py``) and from a second coding of ADR-050 D10 that is separate from the generator's; each
  seeded case is what its name says; the committed baselines and run files hold what the outcomes assume; the Affected
  Assets blocks fit the S-13 branch they stand for, checked against the shipped populator; and the base set is
  byte-for-byte what T021 and the gated subset were taken from, by W1's tree digest.

Not here: chain formation on the fixture's chain material, which T115 and T116 test with the real script, and the
parts that T148 and T103 fill (they extend this module as their parts land). No renderer exists yet, so none of the
variants is run through one: T041 writes SC-4's goldens on them.

How they run (H15): the generator is imported and driven through ``main(argv)``, in-process. Standard library
and pytest only, and Python 3.9 syntax.
"""

from __future__ import annotations

import ast
import json
import math
import re
import sys
import types
from decimal import Decimal
from pathlib import Path

import pytest

from ..conftest import _load_hyphenated_script
from . import generate_large_arch_fixture as gen

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "large_arch"
GENERATOR = HERE / "generate_large_arch_fixture.py"

_keep_bytecode_flag = sys.dont_write_bytecode
sys.dont_write_bytecode = True  # a .pyc under scripts/ would dirty the tree under test (ADR-049 D8)
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
try:
    import tachi_parts  # noqa: E402  -- the shipped stamp reader, for the renderer-form baseline
    import tachi_scoring as ts  # noqa: E402  -- the shipped arithmetic, for the variants' independent checks
finally:
    sys.dont_write_bytecode = _keep_bytecode_flag

# The 64k is the response cap that Runs A and B ran under (spec S-1, S-4): a historical figure, kept so that the
# fixture stays large enough to reproduce those runs. The cap itself depends on the environment (T021(a)'s clean
# environment carried max_tokens 128,000), and S-1's design budget is 32,000 tokens per batch.
OUTPUT_CAP_TOKENS = 64_000
SIZING_FLOOR_TOKENS = 2 * OUTPUT_CAP_TOKENS  # S-4's floor: twice the historical figure, whatever the cap is today
TARGETED_OUTPUTS = tuple(
    "baseline/" + name
    for name in ("threats.md", "threats.sarif", "risk-scores.md", "risk-scores.sarif",
                 "compensating-controls.md", "compensating-controls.sarif")
)
STAGES = ("risk-score", "compensating-controls", "trees")
GATED_MAX_TEST_SIZE = 7  # T017 and T027 pass small sizes of up to this; the gated subset must still run each path twice
PREFIXES = ("S", "T", "R", "I", "D", "E", "AG", "AGP", "LLM", "OI", "MI", "TE")
STRIDE = ("S", "T", "R", "I", "D", "E")
RISK_MATRIX = {
    ("LOW", "HIGH"): "Medium", ("MEDIUM", "HIGH"): "High", ("HIGH", "HIGH"): "Critical",
    ("LOW", "MEDIUM"): "Low", ("MEDIUM", "MEDIUM"): "Medium", ("HIGH", "MEDIUM"): "High",
    ("LOW", "LOW"): "Note", ("MEDIUM", "LOW"): "Low", ("HIGH", "LOW"): "Medium",
}
RISK_RANK = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Note": 0}
REDUCTION_PCT = {"Control Found": 50, "Partial Control": 25, "No Control Found": 0}


# --------------------------------------------------------------------------- helpers
def read_tree(root: Path) -> dict:
    """{relative POSIX path: bytes} of every file under root."""
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def cells(line: str) -> list:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def table_after(text: str, heading: str) -> list:
    """The rows (dicts keyed by the header cells) of the first pipe table after a heading line."""
    lines = text.split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith(heading))
    i = start + 1
    while i < len(lines) and not lines[i].startswith("|"):
        if lines[i].startswith("#") and i > start:
            return []
        i += 1
    header = cells(lines[i])
    rows, i = [], i + 2
    while i < len(lines) and lines[i].startswith("|"):
        rows.append(dict(zip(header, (c.strip("*") for c in cells(lines[i])))))
        i += 1
    return rows


def tenths(value: str) -> int:
    whole, _, fraction = value.partition(".")
    return int(whole) * 10 + int(fraction or "0")


def half_up(numerator: int, denominator: int) -> int:
    return (2 * numerator + denominator) // (2 * denominator)


def band(composite_tenths: int) -> str:
    return "Critical" if composite_tenths >= 90 else "High" if composite_tenths >= 70 else "Medium" if composite_tenths >= 40 else "Low"


def prefix_of(finding_id: str) -> str:
    return finding_id.rpartition("-")[0]


def number_of(finding_id: str) -> int:
    return int(finding_id.rpartition("-")[2])


def sarif_results(committed: dict, name: str) -> list:
    return json.loads(committed[name].decode("utf-8"))["runs"][0]["results"]


# --------------------------------------------------------------------------- fixtures
@pytest.fixture(scope="module")
def committed() -> dict:
    assert FIXTURE.is_dir(), "the committed copy is missing: run the generator into tests/scripts/fixtures/large_arch"
    return read_tree(FIXTURE)


@pytest.fixture(scope="module")
def regen(tmp_path_factory, committed) -> dict:
    """The whole tree, regenerated in-process into a temporary directory. It depends on ``committed`` so
    that the committed copy is read first and any write into it would show afterwards."""
    out = tmp_path_factory.mktemp("large_arch_regen") / "tree"
    assert gen.main(["--out", str(out)]) == 0
    return read_tree(out)


@pytest.fixture(scope="module")
def base(committed) -> types.SimpleNamespace:
    """The baseline run directory, read once: the tables the shape tests share."""
    threats = committed["baseline/threats.md"].decode("utf-8")
    actions = table_after(threats, "## 7. Recommended Actions")
    sections = {}
    for heading in ("### 3.1", "### 3.2", "### 3.3", "### 3.4", "### 3.5", "### 3.6", "### 4.1", "### 4.2"):
        sections[heading] = table_after(threats, heading)
    return types.SimpleNamespace(
        threats=threats, actions=actions, ids=[row["Finding ID"] for row in actions],
        by_id={row["Finding ID"]: row for row in actions}, sections=sections,
        components=table_after(threats, "### Components"), zones=table_after(threats, "### Trust Zones"),
        groups=table_after(threats, "## 4a. Correlated Findings"), resolved=table_after(threats, "## 4c. Resolved Findings"),
        lifecycle=table_after(threats, "### Finding Lifecycle"),
    )


# --------------------------------------------------------------------------- byte identity
def test_regeneration_matches_the_committed_copy_byte_for_byte(regen, committed):
    missing = sorted(set(committed) - set(regen))
    extra = sorted(set(regen) - set(committed))
    differ = sorted(path for path in set(regen) & set(committed) if regen[path] != committed[path])
    assert not (missing or extra or differ), (
        "the generator and the committed copy disagree: %d missing from the run (first: %s), %d not committed (first: %s), "
        "%d differing (first: %s). If the change is deliberate, regenerate into tests/scripts/fixtures/large_arch and commit it."
        % (len(missing), missing[:3], len(extra), extra[:3], len(differ), differ[:3]))


def test_a_run_leaves_the_committed_copy_as_it_was(regen, committed):
    after = read_tree(FIXTURE)
    changed = sorted(path for path in set(after) | set(committed) if after.get(path) != committed.get(path))
    assert not changed, "the test run changed tracked files: %s" % changed[:5]


@pytest.mark.parametrize("part", list(gen.PARTS))
def test_a_part_regenerates_alone_to_the_bytes_it_has_in_the_whole_tree(regen, part):
    """Adding or removing a part never moves another part's bytes, and a part writes only under its own name."""
    alone = gen.build(part)
    assert all(path.startswith(part + "/") for path in alone), "part %s writes outside its own directory" % part
    whole = {path: data for path, data in regen.items() if path.startswith(part + "/")}
    assert alone == whole


def test_unknown_variants_and_bad_output_paths_are_refused(tmp_path):
    assert gen.main(["--out", str(tmp_path / "x"), "--variant", "no-such-part"]) == 2
    occupied = tmp_path / "file"
    occupied.write_text("not a directory")
    assert gen.main(["--out", str(occupied)]) == 2


# --------------------------------------------------------------------------- sizing
@pytest.mark.parametrize("name", TARGETED_OUTPUTS)
def test_each_targeted_output_is_at_least_twice_the_output_cap(committed, name):
    assert name in committed, "%s is missing from the committed copy" % name
    tokens = len(committed[name]) / 4  # S-4's stated estimator: UTF-8 bytes / 4
    # The cap in the message is the historical 64k of Runs A and B (see OUTPUT_CAP_TOKENS), not a claim about today's.
    assert tokens >= SIZING_FLOOR_TOKENS, "%s is %d bytes, about %d tokens, under twice the %d-token cap" % (
        name, len(committed[name]), tokens, OUTPUT_CAP_TOKENS)


def _size_of(value):
    """An int, or the int a spec-like value carries under size or batch_size (a dict entry or an attribute)."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    for key in ("size", "batch_size"):
        inner = value.get(key) if isinstance(value, dict) else getattr(value, key, None)
        if isinstance(inner, int) and not isinstance(inner, bool):
            return inner
    return None


STAGE_ALIASES = {  # what a constant's name may hold to name a stage, after lower-casing and dropping separators
    "risk-score": ("riskscore", "scorer"),
    "compensating-controls": ("compensatingcontrols", "controls"),
    "trees": ("trees", "tree"),
}


def _squash(name: str) -> str:
    return re.sub(r"[^a-z]+", "", name.lower())


def read_stage_sizes(module) -> dict:
    """The planner's batch size per stage, read from the module's constants, never restated here.

    ADR-050 D6 says the sizes are constants in ``tachi-stage.py`` and doesn't name them, so two shapes are
    accepted: one module-level mapping keyed by the stage names (``risk-score``, ``compensating-controls``,
    ``trees``; underscores allowed), whose values are ints or carry a ``size``; or one upper-case int per
    stage whose name holds the stage and either SIZE or BATCH. The single place to change if T018 picks another.
    """
    for attr, value in vars(module).items():
        if attr.startswith("__") or not isinstance(value, dict):
            continue
        keyed = {_squash(str(key)): _size_of(item) for key, item in value.items()}
        sizes = {stage: keyed.get(_squash(stage)) for stage in STAGES}
        if all(isinstance(size, int) for size in sizes.values()):
            return sizes
    sizes = {}
    for stage in STAGES:
        hits = [value for attr, value in vars(module).items()
                if attr.isupper() and _size_of(value) is not None and ("SIZE" in attr or "BATCH" in attr)
                and any(alias in _squash(attr) for alias in STAGE_ALIASES[stage])]
        if len(hits) == 1:
            sizes[stage] = _size_of(hits[0])
    if len(sizes) != len(STAGES):
        pytest.fail("tachi-stage.py exposes no batch-size constant for %s: expected one module-level mapping keyed by the stage "
                    "names, or one UPPER_CASE int per stage whose name holds the stage and SIZE or BATCH"
                    % [stage for stage in STAGES if stage not in sizes])
    return sizes


@pytest.fixture(scope="module")
def stage_sizes() -> dict:
    sizes = read_stage_sizes(_load_hyphenated_script("tachi_stage_for_sizing", "tachi-stage.py"))
    assert all(1 <= size <= 500 for size in sizes.values()), "a size is outside part-files.md's 1 to 500: %s" % sizes
    return sizes


def units_per_path(rows: list) -> dict:
    """The units each batched path plans over: open findings for the two part stages, the Critical and High
    findings whose trees are generated for the trees (the baseline's manifest holds all of them, under Rule 2)."""
    return {"risk-score": len(rows), "compensating-controls": len(rows),
            "trees": sum(1 for row in rows if row["Risk Level"] in ("Critical", "High"))}


@pytest.mark.parametrize("stage", STAGES)
def test_every_batched_path_gets_two_or_more_batches_at_the_planners_sizes(base, stage_sizes, stage):
    units = units_per_path(base.actions)[stage]
    batches = math.ceil(units / stage_sizes[stage])  # D3: balanced contiguous runs, so the count is the ceiling
    assert batches >= 2, "%s: %d units at size %d plan %d batch(es); S-4 needs two or more" % (stage, units, stage_sizes[stage], batches)


def test_the_gated_subset_runs_every_batched_path_twice_at_a_small_size(committed):
    rows = table_after(committed["gated-subset/baseline/threats.md"].decode("utf-8"), "## 7. Recommended Actions")
    for stage, units in units_per_path(rows).items():
        assert units >= 2 * GATED_MAX_TEST_SIZE, "gated subset: %s has %d units, too few for a batch size of %d to run twice" % (
            stage, units, GATED_MAX_TEST_SIZE)


@pytest.mark.parametrize("shape,expected", [
    ("mapping of ints", {"risk-score": 16, "compensating-controls": 13, "trees": 12}),
    ("mapping of dicts", {"risk-score": 16, "compensating-controls": 13, "trees": 12}),
    ("mapping of objects", {"risk-score": 16, "compensating-controls": 13, "trees": 12}),
    ("one constant per stage", {"risk-score": 16, "compensating-controls": 13, "trees": 12}),
])
def test_the_size_reader_accepts_each_shape_the_constants_may_take(shape, expected):
    modules = {
        "mapping of ints": {"BATCH_SIZES": {"risk-score": 16, "compensating-controls": 13, "trees": 12}, "OTHER": {"a": 1}},
        "mapping of dicts": {"STAGES": {"risk_score": {"size": 16}, "compensating_controls": {"size": 13}, "trees": {"size": 12}}},
        "mapping of objects": {"SPECS": {"risk-score": types.SimpleNamespace(batch_size=16),
                                         "compensating-controls": types.SimpleNamespace(batch_size=13),
                                         "trees": types.SimpleNamespace(batch_size=12)}},
        "one constant per stage": {"RISK_SCORE_BATCH_SIZE": 16, "CONTROLS_SIZE": 13, "TREES_BATCH_SIZE": 12, "MAX_RETRIES": 2},
    }
    assert read_stage_sizes(types.SimpleNamespace(**modules[shape])) == expected


def test_the_size_reader_refuses_a_module_without_the_constants():
    with pytest.raises(pytest.fail.Exception):
        read_stage_sizes(types.SimpleNamespace(VERSION="1.0.0", MAX_RETRIES=2))
    with pytest.raises(pytest.fail.Exception):
        read_stage_sizes(types.SimpleNamespace(BATCH_SIZES={"risk-score": 16, "trees": 12}))  # a stage is missing


# --------------------------------------------------------------------------- the determinism contract
# Names a stream may be asked for besides random() and seed(). The union of the 3.9 to 3.14 module, plus what
# the running interpreter adds, so a new method is banned before anyone has met it.
STATIC_BANNED = {
    "betavariate", "binomialvariate", "choice", "choices", "expovariate", "gammavariate", "gauss", "getrandbits",
    "getstate", "lognormvariate", "normalvariate", "paretovariate", "randbytes", "randint", "randrange", "sample",
    "setstate", "shuffle", "triangular", "uniform", "vonmisesvariate", "weibullvariate", "SystemRandom",
}


def banned_random_names() -> set:
    import random
    dynamic = {name for owner in (random, random.Random) for name in dir(owner)
               if not name.startswith("_") and callable(getattr(owner, name, None))}
    return (STATIC_BANNED | dynamic) - {"random", "seed", "Random"}


def random_violations(source: str) -> list:
    """Every use of a banned random method, or of the module's global stream, found by AST."""
    banned = banned_random_names()
    tree = ast.parse(source)
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "random":
            for alias in node.names:
                if alias.name != "Random":
                    found.append("line %d: from random import %s" % (node.lineno, alias.name))
        elif isinstance(node, ast.Attribute):
            if node.attr in banned:
                found.append("line %d: .%s" % (node.lineno, node.attr))
            elif node.attr in ("random", "seed") and isinstance(node.value, ast.Name) and node.value.id == "random":
                found.append("line %d: random.%s() seeds or draws on the module's global stream" % (node.lineno, node.attr))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "getattr":
            if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and node.args[1].value in banned:
                found.append("line %d: getattr(..., %r)" % (node.lineno, node.args[1].value))
    return found


def test_the_generator_uses_no_random_method_but_random_and_seed():
    assert random_violations(GENERATOR.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize("snippet", [
    "import random\nrandom.choice([1, 2])",
    "import random\nr = random.Random()\nr.randint(0, 3)",
    "import random\nr = random.Random()\nr.sample([1, 2], 1)",
    "from random import choice",
    "from random import shuffle as mix",
    "import random\nrandom.seed(3)",
    "import random\nrandom.random()",
    "import random\nr = random.SystemRandom()",
    "import random\nr = random.Random()\ngetattr(r, 'uniform')(0, 1)",
    "import random\nr = random.Random()\nr.getstate()",
])
def test_the_random_ban_catches_each_banned_form(snippet):
    assert random_violations(snippet), "the ban missed: %s" % snippet


@pytest.mark.parametrize("snippet", [
    "import random\nr = random.Random()\nr.seed(5)\nr.random()",
    "import random\nclass Rng:\n    def __init__(self):\n        self._s = random.Random()\n        self._s.seed(1)\n    def unit(self):\n        return self._s.random()",
])
def test_the_random_ban_allows_a_seeded_stream_drawn_with_random(snippet):
    assert random_violations(snippet) == []


FORBIDDEN_MODULES = {"time", "locale", "secrets", "uuid", "platform", "tempfile", "glob", "getpass", "socket"}
FORBIDDEN_ATTRIBUTES = {
    "now", "today", "utcnow", "fromtimestamp", "time_ns", "monotonic", "perf_counter", "environ", "getenv",
    "getlocale", "setlocale", "listdir", "scandir", "iterdir", "rglob", "urandom", "getpid", "gethostname",
}


def drift_violations(source: str) -> list:
    """The other sources of drift the docstring rules out: hash(), the clock, the environment, the locale, directory order."""
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "hash":
            found.append("line %d: hash()" % node.lineno)
        elif isinstance(node, ast.Import):
            found += ["line %d: import %s" % (node.lineno, a.name) for a in node.names if a.name.split(".")[0] in FORBIDDEN_MODULES]
        elif isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] in FORBIDDEN_MODULES:
            found.append("line %d: from %s import ..." % (node.lineno, node.module))
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_ATTRIBUTES:
            found.append("line %d: .%s" % (node.lineno, node.attr))
    return found


def test_the_generator_reads_neither_hash_nor_the_clock_nor_the_environment():
    assert drift_violations(GENERATOR.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize("snippet", [
    "x = hash('a')", "import time", "from locale import setlocale", "import os\nos.environ['A']",
    "import os\nos.listdir('.')", "import datetime\ndatetime.datetime.now()", "import datetime\ndatetime.date.today()",
])
def test_the_drift_check_catches_each_forbidden_form(snippet):
    assert drift_violations(snippet), "the check missed: %s" % snippet


def test_the_generator_source_is_ascii_and_parses_as_python_3_9():
    source = GENERATOR.read_text(encoding="utf-8")
    assert source.isascii(), "non-ASCII text in the generator source"
    ast.parse(source, feature_version=(3, 9))
    assert "from __future__ import annotations" in source


def test_every_file_is_canonical_text(committed):
    for path, data in committed.items():
        text = data.decode("utf-8")  # strict: a file that is not UTF-8 fails here
        assert "\r" not in text, "%s holds a carriage return" % path
        assert text.endswith("\n") and not text.endswith("\n\n"), "%s must end with exactly one newline" % path


def test_json_comes_from_the_generators_serializer(committed):
    """JSON is written by dumps() (ASCII escapes, two-space indent), never by json.dumps."""
    checked = 0
    for path, data in committed.items():
        if path.endswith((".json", ".sarif")):
            text = data.decode("utf-8")
            assert text.isascii(), "%s holds non-ASCII characters" % path
            assert gen.dumps(json.loads(text), indent=2, sort_keys=False) + "\n" == text, "%s was not written by dumps()" % path
            checked += 1
    assert checked >= 8, "expected the canary probe, three SARIF files, the manifest and the gated subset's files"


@pytest.mark.parametrize("run,architecture", [("baseline", "architecture"), ("gated-subset/baseline", "gated-subset/architecture")],
                         ids=["base", "gated"])
def test_each_threats_file_is_a_fixed_point_of_the_affected_assets_populator(committed, tmp_path, run, architecture):
    """The populator runs exactly as /tachi.risk-score's Step 1.5 invokes it, on a copy, and leaves every byte alone:
    it renders the block with no introduction and its rows in Section 7's order, and the fixture must already do so."""
    populator = _load_hyphenated_script("populate_affected_assets_for_fixture", "populate-affected-assets.py")
    original = committed[run + "/threats.md"]
    threats, arch = tmp_path / "threats.md", tmp_path / "architecture.md"
    threats.write_bytes(original)
    arch.write_bytes(committed[architecture + "/architecture.md"])
    assert populator.main(["--architecture", str(arch), "--threats", str(threats)]) == 0
    assert threats.read_bytes() == original, "the populator rewrote %s/threats.md: emit the Affected Assets block in its own form" % run
    assert populator.main(["--architecture", str(arch), "--threats", str(threats), "--check"]) == 0


def test_no_file_holds_a_local_path(committed):
    """H8 and NFR-6: the fixture is synthetic, so it names no local or absolute user path."""
    roots = ("Us" + "ers", "ho" + "me", "pri" + "vate", "t" + "mp", "var/fol" + "ders")  # built in pieces: this file holds no path itself
    pattern = re.compile("/(%s)/|(?<![A-Za-z0-9])[A-Za-z]:\\\\[A-Za-z]" % "|".join(roots))
    hits = [(path, match.group(0)) for path, data in committed.items() for match in [pattern.search(data.decode("utf-8"))] if match]
    assert not hits, "local path in: %s" % hits[:3]


def test_the_gated_subset_is_a_smaller_copy_with_no_mermaid_and_no_trees(committed):
    mermaid = re.compile(r"mermaid|flowchart|graph\s+(TD|LR|TB|RL)|sequenceDiagram|classDef", re.IGNORECASE)
    gated = {path: data for path, data in committed.items() if path.startswith("gated-subset/")}
    assert gated, "the gated subset is missing"
    assert not [path for path in gated if "attack-trees" in path], "the gated subset holds attack trees"
    assert not [path for path, data in gated.items() if mermaid.search(data.decode("utf-8"))], "Mermaid text in the gated subset"
    small = table_after(gated["gated-subset/baseline/threats.md"].decode("utf-8"), "## 7. Recommended Actions")
    large = table_after(committed["baseline/threats.md"].decode("utf-8"), "## 7. Recommended Actions")
    assert {prefix_of(row["Finding ID"]) for row in small} == set(PREFIXES), "the gated subset must still cover all 12 prefixes"
    assert len(small) * 5 < len(large)
    assert sum(len(data) for data in gated.values()) < 1_000_000


# --------------------------------------------------------------------------- the base set's shape (S-4)
def test_the_architecture_has_25_components_over_four_zones_and_all_seven_layers(base):
    names = [row["Component"] for row in base.components]
    assert len(names) == 25 and len(set(names)) == 25
    assert sum(1 for name in names if any(ch.isdigit() for ch in name)) >= 3, "digit-bearing names exercise the numeral rules"
    assert {int(re.match(r"L(\d)", row["MAESTRO Layer"]).group(1)) for row in base.components} == set(range(1, 8))
    assert len(base.zones) >= 4
    placed = [name.strip() for row in base.zones for name in row["Components"].split(",")]
    assert sorted(placed) == sorted(names), "every component sits in exactly one zone"


def test_at_least_two_llm_components_and_two_agentic_components_carry_findings(base):
    agentic = {row["Component"] for row in base.sections["### 4.1"]}
    llm = {row["Component"] for row in base.sections["### 4.2"]}
    assert len(agentic) >= 2 and len(llm) >= 2


def test_the_findings_meet_the_shape_s4_gives(base):
    assert 390 <= len(base.ids) <= 450 and len(set(base.ids)) == len(base.ids)
    assert {prefix_of(fid) for fid in base.ids} == set(PREFIXES), "all 12 prefixes"
    assert sum(1 for row in base.actions if row["Risk Level"] == "Critical") >= 40
    in_tables = [row["ID"] for rows in base.sections.values() for row in rows]
    assert sorted(in_tables) == sorted(base.ids), "Sections 3 and 4 hold exactly the findings of Section 7"
    for rows in base.sections.values():
        for row in rows:
            assert RISK_MATRIX[(row["Likelihood"], row["Impact"])] == row["Risk Level"] == base.by_id[row["ID"]]["Risk Level"]


def test_the_correlation_groups_meet_s4_and_follow_the_algorithm(base):
    assert len(base.groups) >= 20
    seen, widest = [], 0
    for group in base.groups:
        members = [m.strip() for m in group["Findings"].split(",")]
        assert len(members) >= 2 and all(m in base.by_id for m in members)
        assert {base.by_id[m]["Component"] for m in members} == {group["Component"]}, "one group per component"
        kinds = [prefix_of(m) in STRIDE for m in members]
        assert kinds == sorted(kinds, reverse=True) and True in kinds and False in kinds, "STRIDE members first, then AI, both present"
        assert group["Risk Level"] == max((base.by_id[m]["Risk Level"] for m in members), key=RISK_RANK.get)
        widest = max(widest, len({prefix_of(m) for m in members}))
        seen += members
    assert len(seen) == len(set(seen)), "a finding belongs to at most one group"
    assert widest >= 3, "one group must span three or more categories"
    assert len({g["Component"] for g in base.groups}) == len(base.groups)


def test_the_resolved_findings_and_the_delta_summary_agree(base):
    assert len(base.resolved) >= 5
    resolved_ids = [row["ID"] for row in base.resolved]
    assert not set(resolved_ids) & set(base.ids)
    for fid in resolved_ids:  # never the highest number of its prefix, so no high-water-mark case arises by accident
        assert number_of(fid) < max(number_of(i) for i in base.ids if prefix_of(i) == prefix_of(fid)), fid
    counts = {status: sum(1 for row in base.actions if row["Status"] == status) for status in ("NEW", "UNCHANGED", "UPDATED")}
    assert all(counts.values()), "every status occurs: %s" % counts
    lifecycle = {row["Status"]: int(row["Count"]) for row in base.lifecycle}
    assert {k: lifecycle[k] for k in counts} == counts and lifecycle["RESOLVED"] == len(resolved_ids)
    frontmatter = re.search(r"^  finding_count: (\d+)$", base.threats, re.MULTILINE)
    assert int(frontmatter.group(1)) == counts["UNCHANGED"] + counts["UPDATED"] + len(resolved_ids)


def test_the_companion_files_cover_every_open_finding(base, committed):
    open_ids = set(base.ids)
    scores = table_after(committed["baseline/risk-scores.md"].decode("utf-8"), "## 2. Scored Threat Table")
    assert {row["ID"] for row in scores} == open_ids and len(scores) == len(open_ids)
    controls_text = committed["baseline/compensating-controls.md"].decode("utf-8")
    matrix = [row["Threat ID"] for severity in ("Critical", "High", "Medium", "Low")
              for row in (table_after(controls_text, "### %s Residual Severity" % severity) if "### %s Residual Severity" % severity in controls_text else [])]
    assert sorted(matrix) == sorted(open_ids)
    peers = {m.strip() for group in base.groups for m in group["Findings"].split(",")[1:]}
    listed = {}
    for name, expected in (("threats", open_ids - peers), ("risk-scores", open_ids), ("compensating-controls", open_ids)):
        document = json.loads(committed["baseline/%s.sarif" % name].decode("utf-8"))
        results = document["runs"][0]["results"]
        ids = [r["partialFingerprints"]["findingId/v1"] for r in results]
        assert sorted(ids) == sorted(expected), "%s.sarif holds the wrong findings" % name
        declared = {rule["id"] for rule in document["runs"][0]["tool"]["driver"]["rules"]}
        assert {r["ruleId"] for r in results} <= declared
        assert all(re.fullmatch(r"[0-9a-f]{16}", r["partialFingerprints"]["primaryLocationLineHash"]) for r in results)
        listed[name] = results
    related = {loc["message"]["text"].split(":")[0] for r in listed["threats"] for loc in r.get("relatedLocations", [])}
    assert related == peers, "pre-fix threats.sarif lists each correlated peer in its primary's relatedLocations"


def test_the_attack_trees_cover_the_critical_and_high_findings(base, committed):
    manifest = json.loads(committed["baseline/attack-trees/.manifest.json"].decode("utf-8"))
    wanted = sorted(row["Finding ID"] for row in base.actions if row["Risk Level"] in ("Critical", "High"))
    assert sorted(entry["finding_id"] for entry in manifest["trees"]) == wanted
    assert manifest["attack_tree_count"] == len(wanted) == units_per_path(base.actions)["trees"]
    summary = manifest["summary"]
    assert summary["fresh"] + summary["carried_forward"] + summary["regenerated"] == len(wanted)
    files = sorted(path for path in committed if path.startswith("baseline/attack-trees/") and path.endswith(".md"))
    assert files == sorted("baseline/" + entry["file_path"] for entry in manifest["trees"])
    for entry in manifest["trees"]:
        text = committed["baseline/" + entry["file_path"]].decode("utf-8")
        assert text.startswith("# %s:" % entry["finding_id"]) and "```mermaid" in text


def test_scores_are_internally_consistent_so_the_base_set_carries_no_seeded_error(base, committed):
    """Composite, band and residual recompute from the printed values, and none is a rounding tie or a band boundary."""
    scores = table_after(committed["baseline/risk-scores.md"].decode("utf-8"), "## 2. Scored Threat Table")
    composite = {}
    for row in scores:
        c, e, s, r = (tenths(row[key]) for key in ("CVSS", "Exploit.", "Scale.", "Reach."))
        total = 35 * c + 30 * e + 15 * s + 20 * r
        assert total % 100 != 50, "%s: a composite rounding tie" % row["ID"]
        composite[row["ID"]] = half_up(total, 100)
        assert composite[row["ID"]] == tenths(row["Composite"]), "%s: composite does not recompute" % row["ID"]
        assert composite[row["ID"]] not in (40, 70, 90), "%s: a composite on a band boundary" % row["ID"]
        assert band(composite[row["ID"]]) == row["Severity"], "%s: band does not match the composite" % row["ID"]
    controls_text = committed["baseline/compensating-controls.md"].decode("utf-8")
    for severity in ("Critical", "High", "Medium", "Low"):
        heading = "### %s Residual Severity" % severity
        for row in table_after(controls_text, heading) if heading in controls_text else []:
            inherent, factor = composite[row["Threat ID"]], REDUCTION_PCT[row["Control Status"]]
            assert inherent * (100 - factor) % 100 != 50, "%s: a residual rounding tie" % row["Threat ID"]
            assert half_up(inherent * (100 - factor), 100) == tenths(row["Residual Score"]), "%s: residual does not recompute" % row["Threat ID"]
            assert band(tenths(row["Residual Score"])) == severity


def test_control_evidence_points_at_real_lines_of_the_stub_codebase(committed):
    locations = {}
    for result in sarif_results(committed, "baseline/compensating-controls.sarif"):
        for evidence in result["properties"]["control-evidence"]:
            locations[(evidence["file"], evidence["line"])] = evidence["snippet"]
    assert len(locations) >= 8, "the stub codebase should give evidence for several controls"
    for (name, line), snippet in locations.items():
        lines = committed["stub-codebase/" + name].decode("utf-8").split("\n")
        want = snippet.split("\n")
        assert lines[line - 1:line - 1 + len(want)] == want, "%s:%d does not hold the quoted snippet" % (name, line)
    quoted = set(re.findall(r"\*\*Detected in\*\*: `([^`]+):(\d+)`", committed["baseline/compensating-controls.md"].decode("utf-8")))
    assert quoted and quoted <= {(name, str(line)) for name, line in locations}


# =========================================================================== the PR 1 variants (T040; S-4, SC-4)
# Each variant is a directory of scenarios, and each scenario carries expected-outcomes.json: what the scorer renderer must correct,
# flag or leave alone, worked out by the generator from first principles. No renderer exists yet, so these tests do not run one. They
# check that the files are well formed, that every expected value follows from the shipped arithmetic and from a second, separate
# coding of ADR-050 D10, that each seeded case is what its name says, and that the committed inputs hold what the outcomes assume.
VARIANT_SCENARIOS = (
    "seeded-error/main", "legacy-format/main", "legacy-format/no-baseline-date", "tagged/renderer-form", "tagged/legacy-form",
    "tagged/s13-block-equal", "tagged/s13-stale-block", "tagged/s13-no-architecture", "tagged/s13-neither-source", "tagged/s13-drift-form",
    "id-reuse/pr1", "ties/scorer", "ties/controls", "regroup-pair/main",
)
RISK_SCORE_SCENARIOS = tuple(name for name in VARIANT_SCENARIOS if name != "ties/controls")
FLAG_KINDS = {"corrected", "unverifiable", "unchecked", "divergent", "override", "resolved", "retagged", "reused-id", "input"}
CLOSED_VOCABULARY = tuple(re.compile(pattern) for pattern in (  # the scorer's closed flag vocabulary, contracts/module-signatures.md (W1)
    r"corrected:cvss_base:vector",
    r"corrected:(composite_score|exploitability|scalability|reachability):arithmetic",
    r"corrected:severity_band:(band-mapping|rounding)",
    r"corrected:(remediation_sla|risk_disposition|review_date):follows-band",
    r"corrected:review_date:(baseline-date|clock-restarted)",
    r"retagged:(cvss_base|composite_score|severity_band|remediation_sla|risk_disposition|review_date):asset-tags",
    r"unverifiable:cvss_base:no-vector",
    r"unchecked:cvss_base:(assessed-unrecorded|bound-n17c)",
    r"unchecked:reachability:compound-trust-label",
    r"unchecked:review_date:scoring-date-unknown",
    r"divergent:composite_score:primary=[A-Z]+-[0-9]+",
    r"override:(remediation_sla|risk_disposition):human",
    r"reused-id:finding_id:baseline",
    r"input:cvss_vector:sources-disagree",
    r"input:reachability:out-of-range",
    r"input:[a-z_.]+:(narrative-fallback|truncated)",
    r"resolved",
))
TEMPLATE = HERE.parents[1] / "templates" / "tachi" / "output-schemas" / "risk-scores.md"
TEMPLATE_SARIF = HERE.parents[1] / "templates" / "tachi" / "output-schemas" / "risk-scores.sarif"
BAND_RANK = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
BASE_SET_DIRECTORIES = ("canary", "architecture", "baseline", "stub-codebase", "gated-subset")
BASE_SET_DIGEST = "d35f160950e1c8459c3d4bca"  # W1's tree digest of the base set; T021's baselines and the gated subset were taken from it
prefix_rank = gen.prefix_rank
D = Decimal
REACH_RANGES = {"Untrusted": (D("8.0"), D("10.0")), "Semi-trusted": (D("4.0"), D("7.0")), "Trusted": (D("1.0"), D("4.0"))}
SCORED = re.compile(r"^## (?:\d+\.|Section \d+:) Scored Threat Table", re.MULTILINE)
BREAKDOWN = re.compile(r"^## (?:\d+\.|Section \d+:) Dimensional Breakdown", re.MULTILINE)
GOVERNANCE = re.compile(r"^## (?:\d+\.|Section \d+:) Governance Fields", re.MULTILINE)


@pytest.fixture(scope="module")
def docs(committed) -> dict:
    return {name: json.loads(committed["%s/expected-outcomes.json" % name].decode("utf-8")) for name in VARIANT_SCENARIOS}


def text_of(committed: dict, name: str, rel: str) -> str:
    return committed["%s/%s" % (name, rel)].decode("utf-8")


def sections_of(doc: dict) -> list:
    """(run name, section) pairs: a multi-run document holds its runs, any other is its own single section."""
    return list(doc["runs"].items()) if "runs" in doc else [("main", doc)]


def records_of(doc: dict):
    for run_name, section in sections_of(doc):
        for fid, record in section.get("findings", {}).items():
            yield run_name, fid, record


def first(row: dict, *keys: str) -> str:
    return next(row[key] for key in keys if key in row)


def none_if_dash(value: str):
    return None if value == "—" else value


def baseline_scores(text: str) -> dict:
    """Section 2 and Section 4 of a risk-scores.md, whichever heading and header spelling it uses: id -> its stored values."""
    out = {}
    for row in table_after(text, SCORED.search(text).group(0)):
        out[row["ID"]] = {
            "cvss_base": row["CVSS"], "exploitability": first(row, "Exploit.", "Exploit", "Exploitability"),
            "scalability": first(row, "Scale.", "Scale", "Scalability"), "reachability": first(row, "Reach.", "Reach", "Reachability"),
            "composite_score": row["Composite"], "severity_band": row["Severity"], "remediation_sla": none_if_dash(row["SLA"]),
            "risk_disposition": first(row, "Disposition", "Disp")}
    for row in table_after(text, GOVERNANCE.search(text).group(0)):
        assert out[row["ID"]]["severity_band"] == row["Severity"], "Sections 2 and 4 agree on the band"
        out[row["ID"]].update({"risk_owner": row["Owner"], "review_date": none_if_dash(row["Review Date"])})
    return out


def markdown_vectors(text: str) -> dict:
    """The vector that Section 3 gives each finding, or None: the '**CVSS Vector**:' line, or the one after '**Vector**:'."""
    body = text[BREAKDOWN.search(text).end():GOVERNANCE.search(text).start()]
    vectors = {}
    for block in re.split(r"^### ", body, flags=re.MULTILINE)[1:]:
        found = re.search(r"\*\*(?:CVSS )?Vector\*\*: `(CVSS:3\.1/[^`]+)`", block)
        vectors[re.match(r"([A-Z]+-\d+)", block).group(1)] = found.group(1) if found else None
    return vectors


def sarif_vectors(committed: dict, name: str) -> dict:
    results = json.loads(text_of(committed, name, "baseline/risk-scores.sarif"))["runs"][0]["results"]
    return {r["partialFingerprints"]["findingId/v1"]: r["properties"].get("cvss-vector") for r in results}


def zone_table(threats: str) -> dict:
    """component -> (zone, trust-level label) from Section 2 of a threats.md."""
    out = {}
    for row in table_after(threats, "### Trust Zones"):
        for comp in row["Components"].split(","):
            out[comp.strip()] = (row["Zone"], row["Trust Level"])
    return out


def level_of(label: str):
    """The canonical level that a Section 2 label names, or None when it names none or more than one."""
    return {"untrusted": "Untrusted", "semi-trusted": "Semi-trusted", "trusted": "Trusted"}.get(label.lower())


def section7(threats: str) -> dict:
    return {row["Finding ID"]: row for row in table_after(threats, "## 7. Recommended Actions")}


def affected_block(threats: str):
    if "\n## Affected Assets" not in threats:
        return None
    return {row["Finding ID"]: row["Affected Assets"] for row in table_after(threats, "## Affected Assets")}


def tags_of(doc: dict, record: dict) -> tuple:
    return tuple(doc["tag_source"]["tags"].get(record["component"], ()))


def kinds_of(record: dict) -> set:
    return {":".join(part for part in (flag["kind"], flag["field"]) if part) for flag in record["flags"] if flag["basis"] != "optional"}


def scoring_inputs(committed: dict, name: str) -> dict:
    out = {}
    for row in table_after(text_of(committed, name, "baseline/risk-scores.md"), "### Scoring Inputs"):
        out.setdefault(row["ID"], {})[row["Field"]] = row["Value"]
    return out


# --------------------------------------------------------------------------- a second coding of ADR-050 D10, on the shipped arithmetic
def d10_vector_outcome(stored: D, vector, prefix: str, tags: tuple):
    """D10's legacy list over tachi_scoring: (rendered score, (kind, field, cause) or None, step). Written apart from the generator's."""
    if vector is None:
        return stored, ("unverifiable", "cvss_base", "no-vector"), 1
    category = ts.category_for_prefix(prefix)
    base = ts.base_score(vector)
    low, high = ts.bounds(ts.default_score(category))
    own = min(max(base, low), high)
    forcing = bool(tags)
    elevated = ts.base_score(ts.elevate(vector, tags)) if forcing else base
    carries = forcing and ts.elevate(vector, tags) == vector

    def result(assessed: D) -> D:
        return max(assessed, min(elevated, ts.MODIFIER_CEILING)) if forcing else assessed

    if carries and ts.MODIFIER_CEILING < stored <= base:
        return stored, ("unchecked", "cvss_base", "assessed-unrecorded"), 2
    if stored in (result(base), result(own)) or (forcing and stored == ts.MODIFIER_CEILING and elevated > ts.MODIFIER_CEILING):
        return stored, None, 3
    if forcing:
        for assessed in (base, own):
            if stored == assessed < result(assessed):
                return result(assessed), ("retagged", "cvss_base", "asset-tags"), 4
    for other in sorted(ts.CATEGORY_DEFAULT_VECTORS):
        if other != category and stored == min(max(base, ts.bounds(ts.default_score(other))[0]), ts.bounds(ts.default_score(other))[1]):
            return stored, ("unchecked", "cvss_base", "bound-n17c"), 5
    if forcing and ts.MODIFIER_CEILING < stored < elevated:
        return stored, ("unchecked", "cvss_base", "assessed-unrecorded"), 5
    return result(base), ("corrected", "cvss_base", "vector"), 6


def renderer_chain(vector: str, tags: tuple, bounds) -> D:
    assessed = ts.base_score(vector)
    if bounds is not None:
        assessed = min(max(assessed, bounds[0]), bounds[1])
    if tags:
        assessed = max(assessed, min(ts.base_score(ts.elevate(vector, tags)), ts.MODIFIER_CEILING))
    return assessed


# --------------------------------------------------------------------------- structure
def test_every_variant_scenario_of_t040_is_committed(committed):
    missing = [name for name in VARIANT_SCENARIOS if "%s/expected-outcomes.json" % name not in committed]
    assert not missing, "scenarios missing from the committed copy: %s" % missing
    assert {path.split("/")[0] for path in committed if path.endswith("/expected-outcomes.json")} >= {
        "seeded-error", "legacy-format", "tagged", "id-reuse", "ties", "regroup-pair"}, "S-4's six PR 1 variants"


@pytest.mark.parametrize("name", VARIANT_SCENARIOS)
def test_expected_outcomes_are_well_formed_and_point_at_real_files(committed, docs, name):
    doc = docs[name]
    assert doc["schema"] == "tachi.fixture-expected/1"
    assert "%s/%s" % (doc["variant"], doc["scenario"]) == name
    for key in ("stage", "summary", "run", "notes", "flag_reading"):
        assert doc[key], key
    assert doc["run"]["date"] == gen.RUN_DATE
    paths = [doc["run"].get(key) for key in ("threats", "architecture", "risk_scores")]
    paths += [run["threats"] for run in doc.get("runs", {}).values()]
    for rel in filter(None, paths):
        assert "%s/%s" % (name, rel) in committed, "%s names %s, which is not committed" % (name, rel)
    for rel in doc.get("baseline", {}).get("files", ()):
        assert "%s/baseline/%s" % (name, rel) in committed, rel
    if doc["stage"] == "risk-score":
        for _, section in sections_of(doc):
            routing = section["routing"]
            assert set(routing) == {"to_agent", "carried", "copy_primary", "carried_peers"}
            routed = list(routing["to_agent"]) + list(routing["carried"]) + list(routing["copy_primary"])
            open_ids = [fid for fid, record in section["findings"].items() if record["treatment"] != "resolved"]
            assert sorted(routed, key=prefix_rank) == sorted(open_ids, key=prefix_rank), (
                "every open finding is carried, copied from a primary, or routed to the agent, once")


def test_the_flag_vocabulary_is_the_architects_closed_one_with_one_flag_per_kind_and_field(docs):
    checked = 0
    for name, doc in docs.items():
        for _, fid, record in records_of(doc):
            seen = set()
            for flag in record["flags"]:
                parts = [flag[key] for key in ("kind", "field", "cause") if flag[key] is not None]
                assert flag["flag"] == ":".join(parts), (name, fid, flag)
                assert flag["kind"] in FLAG_KINDS and flag["basis"] in ("pinned", "optional"), (name, fid, flag)
                assert any(pattern.fullmatch(flag["flag"]) for pattern in CLOSED_VOCABULARY), (
                    "%s %s: %s is not in the closed vocabulary of contracts/module-signatures.md" % (name, fid, flag["flag"]))
                if flag["basis"] == "optional":  # the one open string: a value that the input's form lacks (S-12(b))
                    assert flag["flag"] == "corrected:remediation_sla:follows-band" and flag["stored"] is None, (name, fid, flag)
                assert (flag["kind"], flag["field"]) not in seen, "%s %s: two %s flags on %s" % (name, fid, flag["kind"], flag["field"])
                seen.add((flag["kind"], flag["field"]))
                checked += 1
    assert checked > 200
    every = {flag["flag"] for doc in docs.values() for _, _, record in records_of(doc) for flag in record["flags"]}
    assert "corrected:composite_score:rounding" not in every, "a rounding-only composite difference is normalized, and only the band is flagged"
    assert not any("cvss_vector:no-vector" in text or "baseline-id-reused" in text for text in every)


# --------------------------------------------------------------------------- the arithmetic behind every expected value
@pytest.mark.parametrize("name", RISK_SCORE_SCENARIOS)
def test_each_rendered_record_follows_from_the_shipped_arithmetic(docs, name):
    checked = 0
    for _, fid, record in records_of(docs[name]):
        if record["treatment"] == "resolved":
            assert record["rendered"] == record["stored"] and [f["kind"] for f in record["flags"]] == ["resolved"], fid
            continue
        got = record["rendered"]
        composite = ts.composite(D(got["cvss_base"]), D(got["exploitability"]), D(got["scalability"]), D(got["reachability"]))
        assert D(got["composite_score"]) == composite, "%s %s: composite %s is not %s" % (name, fid, got["composite_score"], composite)
        assert got["severity_band"] == ts.band(composite), (name, fid)
        overridden = {flag["field"] for flag in record["flags"] if flag["kind"] == "override"}
        defaults = ts.SEVERITY_BANDS[got["severity_band"]]
        if "remediation_sla" not in overridden:
            assert got["remediation_sla"] == defaults["sla"], (name, fid)
        if "risk_disposition" not in overridden:
            assert got["risk_disposition"] == defaults["disposition"], (name, fid)
        for key in ("cvss_base", "exploitability", "scalability", "reachability", "composite_score"):
            assert D(got[key]) == D(got[key]).quantize(D("0.1")), (name, fid, key)
        ts.parse_date(got["review_date"])
        checked += 1
    assert checked >= 4


@pytest.mark.parametrize("name", RISK_SCORE_SCENARIOS)
def test_the_cvss_chain_agrees_with_a_separate_coding_of_d10(docs, name):
    doc = docs[name]
    checked = 0
    for run_name, fid, record in records_of(doc):
        if record["treatment"] != "carried" or run_name in ("run2", "run3"):
            continue
        tags, vector = tags_of(doc, record), record["stored"]["cvss_vector"]
        flag = next(((f["kind"], f["field"], f["cause"]) for f in record["flags"]
                     if f["field"] in ("cvss_base", "cvss_vector") and f["kind"] in ("corrected", "retagged", "unchecked", "unverifiable")), None)
        if record["form"] == "legacy":
            rendered, expect, step = d10_vector_outcome(D(record["stored"]["cvss_base"]), vector, record["prefix"], tags)
            assert record["d10_step"] == step, (name, fid, "D10 step")
            assert flag == expect, (name, fid, flag, expect)
            assert D(record["rendered"]["cvss_base"]) == rendered, (name, fid)
        else:
            bounds = record["stored_inputs"]["score_bounds"]
            bounds = None if bounds is None else (D(bounds[0]), D(bounds[1]))
            now = renderer_chain(vector, tags, bounds)
            then = renderer_chain(vector, tuple(record["stored_inputs"]["tags_used"]), bounds)
            assert D(record["rendered"]["cvss_base"]) == now, (name, fid)
            if now != D(record["stored"]["cvss_base"]):
                assert flag == (("retagged", "cvss_base", "asset-tags") if then == D(record["stored"]["cvss_base"])
                                else ("corrected", "cvss_base", "vector")), (name, fid, flag)
            else:
                assert flag is None, (name, fid)
        checked += 1
    assert checked >= 4


# --------------------------------------------------------------------------- the cases are what their names say
def zone_label(committed: dict, name: str, doc: dict, component: str) -> tuple:
    zone, label = zone_table(text_of(committed, name, doc["run"]["threats"]))[component]
    return zone, label, level_of(label)


def check_case(committed: dict, name: str, doc: dict, fid: str, record: dict) -> None:
    case, stored = record["case"], record["stored"]
    if stored is None:
        return
    kinds = kinds_of(record)
    c, e, s, r, comp = (D(stored[key]) for key in ("cvss_base", "exploitability", "scalability", "reachability", "composite_score"))
    exact = ts.composite(c, e, s, r)
    total = D("0.35") * c + D("0.30") * e + D("0.15") * s + D("0.20") * r
    vector, prefix = stored["cvss_vector"], record["prefix"]
    if case == "wrong-composite":
        assert comp != exact and ts.band(comp) == ts.band(exact) == stored["severity_band"], fid
        assert D(record["rendered"]["composite_score"]) == exact and "corrected:composite_score" in kinds
    elif case == "wrong-band":
        assert stored["severity_band"] != ts.band(comp), fid
        assert record["rendered"]["severity_band"] == ts.band(comp) and "corrected:severity_band" in kinds
        assert stored["remediation_sla"] == ts.SEVERITY_BANDS[stored["severity_band"]]["sla"], "no override: the SLA follows the wrong band"
    elif case in ("bad-vector", "bad-vector-sarif-only"):
        base = ts.base_score(vector)
        assert c != base and D(record["rendered"]["cvss_base"]) == base and "corrected:cvss_base" in kinds, fid
        assert abs(c - base) >= D("1.2"), "a slip well outside any clamp"
        assert comp == ts.composite(base, e, s, r), "the stored composite is the right score's"
    elif case in ("cascade-composite", "cascade-band"):
        base = ts.base_score(vector)
        assert c != base and comp == exact, "the composite follows the wrong cell"
        assert (ts.band(ts.composite(base, e, s, r)) != ts.band(comp)) == (case == "cascade-band"), fid
    elif case == "reach-out-of-range":
        _, _, level = zone_label(committed, name, doc, record["component"])
        assert not REACH_RANGES[level][0] <= r <= REACH_RANGES[level][1] and "input:reachability" in kinds and comp == exact, fid
    elif case == "compound-label":
        _, label, level = zone_label(committed, name, doc, record["component"])
        assert level is None and "/" in label, "a label that names two trust levels"
        assert "unchecked:reachability" in kinds
    elif case == "missing-vector":
        assert vector is None and "unverifiable:cvss_base" in kinds and record["rendered"]["cvss_base"] == stored["cvss_base"], fid
    elif case == "clamp-control":
        base = ts.base_score(vector)
        low, high = ts.bounds(ts.default_score(ts.category_for_prefix(prefix)))
        assert c != base and c == min(max(base, low), high) and not record["flags"], fid
    elif case == "n17-bound":
        base, category = ts.base_score(vector), ts.category_for_prefix(prefix)
        low, high = ts.bounds(ts.default_score(category))
        others = {min(max(base, lo), hi) for cat in ts.CATEGORY_DEFAULT_VECTORS if cat != category
                  for lo, hi in [ts.bounds(ts.default_score(cat))]}
        assert c not in (base, min(max(base, low), high)) and c in others and "unchecked:cvss_base" in kinds, fid
    elif case in ("rounding-only", "tie-rounding-only"):
        assert total * 100 % 10 == 5, "the weighted sum ends in exactly .x5"
        assert comp == exact - D("0.1") and ts.band(comp) == ts.band(exact) and record["normalized"] and not record["flags"], fid
    elif case.startswith("tie-band-moves"):
        assert total * 100 % 10 == 5 and comp == exact - D("0.1") and ts.band(comp) != ts.band(exact), fid
        assert exact in (D("4.0"), D("7.0"), D("9.0")) and any(f["flag"] == "corrected:severity_band:rounding" for f in record["flags"])
        assert not any(f["field"] == "composite_score" for f in record["flags"]), "the composite's rounding is normalized, never flagged"
    elif case == "tie-stored-as-half-up":
        assert total * 100 % 10 == 5 and comp == exact and not record["flags"], fid
    elif case.startswith("boundary-exact"):
        assert total == exact == comp and comp in (D("4.0"), D("7.0"), D("9.0")) and not record["flags"], fid
        assert stored["severity_band"] == ts.band(comp)
    elif case in ("override-sla", "override-disposition"):
        field = "remediation_sla" if case == "override-sla" else "risk_disposition"
        assert ("override:" + field) in kinds and record["rendered"][field] == stored[field], fid
        assert stored["risk_owner"] != "Unassigned" and record["rendered"]["review_date"] == stored["review_date"]


@pytest.mark.parametrize("name", ["seeded-error/main", "legacy-format/main", "legacy-format/no-baseline-date", "ties/scorer"])
def test_each_seeded_case_is_what_its_name_says(committed, docs, name):
    seen = set()
    for _, fid, record in records_of(docs[name]):
        check_case(committed, name, docs[name], fid, record)
        seen.add(record["case"])
    assert len(seen) >= 3


def test_the_seeded_error_variant_has_every_kind_for_every_prefix(docs):
    doc = docs["seeded-error/main"]
    cases = {}
    for _, fid, record in records_of(doc):
        cases.setdefault(record["prefix"], []).append(record["case"])
    assert set(cases) == set(PREFIXES), "all 12 prefixes"
    for prefix in PREFIXES:
        for case in ("wrong-composite", "wrong-band", "bad-vector", "reach-out-of-range", "missing-vector", "clamp-control", "n17-bound"):
            assert case in cases[prefix], "%s has no %s" % (prefix, case)
    every = [case for found in cases.values() for case in found]
    for case in ("rounding-only", "override-sla", "override-disposition", "cascade-composite", "cascade-band", "compound-label"):
        assert case in every, case
    assert every.count("rounding-only") >= 3 and every.count("resolved-wrong-composite") == 2
    counts = doc["counts"]
    assert counts["flags_by_kind"]["unverifiable"] == 12, "one missing vector for each prefix"
    assert counts["flags_by_kind"]["input"] == 12, "one out-of-range reachability for each prefix"
    assert counts["normalized"] >= 3 and counts["findings"] == 110 and len(doc["unflagged"]) >= 20


def test_the_d10_legacy_list_has_all_three_outcomes_for_all_twelve_prefixes(docs):
    steps = {}
    for _, fid, record in records_of(docs["seeded-error/main"]):
        steps.setdefault(record["prefix"], set()).add(record["d10_step"])
    for prefix in PREFIXES:
        assert {3, 5, 6} <= steps[prefix], "%s needs a passed clamp (step 3), an unchecked bound (step 5) and a correction (step 6)" % prefix


# --------------------------------------------------------------------------- the committed inputs hold what the outcomes assume
@pytest.mark.parametrize("name", [n for n in RISK_SCORE_SCENARIOS if n != "regroup-pair/main"])
def test_the_baseline_files_hold_the_stored_values(committed, docs, name):
    doc = docs[name]
    text = text_of(committed, name, "baseline/risk-scores.md")
    rows, vectors = baseline_scores(text), markdown_vectors(text)
    sarif = sarif_vectors(committed, name) if "%s/baseline/risk-scores.sarif" % name in committed else {}
    checked = 0
    for _, fid, record in records_of(doc):
        if record["stored"] is None or record["treatment"] not in ("carried", "resolved"):
            continue
        for key, value in record["stored"].items():
            if key != "cvss_vector":
                assert rows[fid][key] == value, "%s %s: the baseline's %s is %r, not %r" % (name, fid, key, rows[fid][key], value)
        assert vectors[fid] == record["vector_sources"]["markdown"], (name, fid, "markdown vector")
        if sarif:
            assert sarif[fid] == record["vector_sources"]["sarif"], (name, fid, "SARIF vector")
        checked += 1
    assert checked >= 4


def test_the_regroup_pairs_baseline_holds_run_ones_stored_values(committed, docs):
    name = "regroup-pair/main"
    rows = baseline_scores(text_of(committed, name, "baseline/risk-scores.md"))
    for fid, record in docs[name]["runs"]["run1"]["findings"].items():
        assert all(rows[fid][key] == value for key, value in record["stored"].items() if key != "cvss_vector"), fid
    assert set(rows) == set(docs[name]["runs"]["run1"]["findings"])
    assert sarif_vectors(committed, name) == {fid: r["stored"]["cvss_vector"] for fid, r in docs[name]["runs"]["run1"]["findings"].items()}


@pytest.mark.parametrize("name", RISK_SCORE_SCENARIOS)
def test_the_stub_baseline_threats_file_lists_the_findings_its_scores_cover(committed, name):
    rows = baseline_scores(text_of(committed, name, "baseline/risk-scores.md"))
    stub = text_of(committed, name, "baseline/threats.md")
    assert set(section7(stub)) == set(rows), "Section 7 of the baseline's threats.md lists exactly the scored findings"
    assert "## 4c. Resolved Findings" in stub and "## 2. Trust Boundaries" in stub


@pytest.mark.parametrize("name", [n for n in RISK_SCORE_SCENARIOS if n not in ("regroup-pair/main", "tagged/s13-drift-form")])
def test_the_run_files_carry_the_statuses_and_front_matter_the_routing_assumes(committed, docs, name):
    doc = docs[name]
    threats = text_of(committed, name, doc["run"]["threats"])
    rows, routing = section7(threats), doc["routing"]
    assert set(rows) == set(routing["carried"]) | set(routing["to_agent"]) | set(routing["copy_primary"]), "Section 7 lists the open findings"
    assert all(rows[fid]["Status"] == "NEW" for fid in routing["to_agent"]), name
    assert all(rows[fid]["Status"] == "UNCHANGED" for fid in routing["carried"]), name
    assert re.search(r'^  source: "%s"$' % re.escape(doc["run"]["baseline_source"]), threats, re.MULTILINE)
    resolved = {row["ID"] for row in table_after(threats, "## 4c. Resolved Findings")}
    assert resolved == {fid for _, fid, record in records_of(doc) if record["treatment"] == "resolved"}, "Section 4c lists the RESOLVED rows"
    assert not table_after(threats, "## 4a. Correlated Findings"), "no correlation groups in this scenario"


# --------------------------------------------------------------------------- tags: R-25, ruling A and S-13
TAG_SCENARIOS = [n for n in RISK_SCORE_SCENARIOS if n.startswith("tagged/") or n in ("seeded-error/main", "id-reuse/pr1", "ties/scorer", "legacy-format/main")]


@pytest.mark.parametrize("name", TAG_SCENARIOS)
def test_the_affected_assets_block_is_what_the_tag_source_case_says(committed, docs, name):
    populator = _load_hyphenated_script("populate_affected_assets_for_variants", "populate-affected-assets.py")
    doc = docs[name]
    source = doc["tag_source"]
    threats = text_of(committed, name, doc["run"]["threats"])
    block = affected_block(threats)
    if not doc["run"]["architecture"]:
        assert "%s/architecture/architecture.md" % name not in committed and doc["populator_fixed_point"] is None
        assert source["architecture_present"] is False and source["source"] in ("block-unverified", "none")
        assert (block is not None) == source["block_present"]
        if source["source"] == "none":
            assert block is None and source["tags"] == {}
        else:
            assert any(value != "[]" for value in block.values()), "an unverified block that carries a tag to apply"
        return
    architecture = text_of(committed, name, doc["run"]["architecture"])
    recomputed = {fid: "[%s]" % ", ".join(tags) for fid, tags in populator.compute_affected_assets(architecture, threats)}
    assert {comp: tuple(tags) for comp, tags in populator.parse_component_asset_map(architecture).items()} == {
        comp: tuple(tags) for comp, tags in source["tags"].items()}, "the tags the outcomes apply are the architecture's"
    assert (block == recomputed) is doc["populator_fixed_point"], "the block is the populator's own exactly when the record says so"
    assert source["block_equals_recomputation"] in (None, True) or doc["scenario"] in ("s13-stale-block", "s13-drift-form")
    if doc["scenario"] == "s13-stale-block":
        assert source["source"] == "recomputed" and source["warning"] is True and block and block != recomputed
        assert any(block[fid] != recomputed[fid] for fid in recomputed), "it misses a tag or invents one"
    if doc["scenario"] == "s13-drift-form":
        assert recomputed == {} and block == {} and source["source"] == "recomputed", "the populator reads no finding from a drift form"
    if doc["scenario"] == "s13-block-equal":
        assert source["source"] == "block" and block == recomputed and any(v != "[]" for v in block.values())


def test_the_five_s13_branches_use_different_sources_over_one_world(docs):
    branches = {n: d for n, d in docs.items() if n.startswith("tagged/s13-")}
    assert {n: d["tag_source"]["source"] for n, d in branches.items()} == {
        "tagged/s13-block-equal": "block", "tagged/s13-stale-block": "recomputed", "tagged/s13-no-architecture": "block-unverified",
        "tagged/s13-neither-source": "none", "tagged/s13-drift-form": "recomputed"}
    assert all(d["tag_source"]["warning"] is (d["tag_source"]["source"] != "block") for d in branches.values())
    worlds = {tuple(sorted((fid, r["case"]) for fid, r in d["findings"].items())) for d in branches.values()}
    assert len(worlds) == 1, "the same six findings in every branch"
    moved = {n: {fid for fid, r in d["findings"].items() if r["flags"]} for n, d in branches.items()}
    assert moved["tagged/s13-neither-source"] == set(), "no source: nothing is elevated"
    assert moved["tagged/s13-block-equal"] == moved["tagged/s13-stale-block"] == moved["tagged/s13-drift-form"]
    assert moved["tagged/s13-no-architecture"] > moved["tagged/s13-block-equal"], "the unverified block's auth tag moves two more rows"
    for fid, record in branches["tagged/s13-stale-block"]["findings"].items():
        if record["case"] in ("spoofing-on-untagged", "dos-on-untagged"):
            assert not record["flags"] and branches["tagged/s13-no-architecture"]["findings"][fid]["flags"], (
                "a run that took the stale block's auth tag would have elevated %s" % fid)


def test_ruling_a_covers_both_directions_the_legacy_case_and_the_band_that_holds(docs):
    doc = docs["tagged/renderer-form"]
    by_case = {r["case"]: r for _, _, r in records_of(doc)}
    run_date = doc["run"]["date"]
    up = by_case["up-band-review-later"]
    assert BAND_RANK[up["rendered"]["severity_band"]] > BAND_RANK[up["stored"]["severity_band"]] and all(f["kind"] == "retagged" for f in up["flags"])
    assert up["rendered"]["review_date"] == ts.review_date(run_date, up["rendered"]["remediation_sla"]) < up["stored"]["review_date"], (
        "this run's date plus the new SLA, and earlier than the stored date: a higher band never gets more time")
    earlier = by_case["up-band-review-earlier"]
    assert earlier["rendered"]["review_date"] == earlier["stored"]["review_date"] < run_date, "the stored date is earlier, so it is kept"
    assert not any(f["field"] == "review_date" for f in earlier["flags"])
    override = by_case["up-band-sla-override"]
    assert override["rendered"]["remediation_sla"] == override["stored"]["remediation_sla"] == "14d"
    assert override["rendered"]["review_date"] == override["stored"]["review_date"] and "override:remediation_sla" in kinds_of(override)
    down = by_case["down-band"]
    assert BAND_RANK[down["rendered"]["severity_band"]] < BAND_RANK[down["stored"]["severity_band"]]
    assert down["rendered"]["review_date"] == ts.review_date(down["stored_inputs"]["scored_on"], down["rendered"]["remediation_sla"]), (
        "a lowering keeps the original scoring date")
    for case in ("band-holds-tag-added", "band-holds-tag-removed"):
        holds = by_case[case]
        assert holds["rendered"]["severity_band"] == holds["stored"]["severity_band"]
        assert sorted(f["field"] for f in holds["flags"]) == ["composite_score", "cvss_base"] and all(f["kind"] == "retagged" for f in holds["flags"])
    for case in ("r25-assessed-above-ceiling", "r25-ceiling-binds", "r25-tag-is-no-op", "tag-unchanged-elevated", "untagged", "clamped-new-finding"):
        assert by_case[case]["flags"] == [] and by_case[case]["rendered"] == by_case[case]["stored"], case
    assert D(by_case["r25-assessed-above-ceiling"]["stored"]["cvss_base"]) > ts.MODIFIER_CEILING
    assert D(by_case["r25-ceiling-binds"]["stored"]["cvss_base"]) == ts.MODIFIER_CEILING
    legacy = {r["case"]: r for _, _, r in records_of(docs["tagged/legacy-form"])}
    assert legacy["up-band-review-later"]["d10_step"] == legacy["up-band-review-earlier"]["d10_step"] == 4
    assert legacy["assessed-unrecorded"]["d10_step"] == 2 and legacy["assessed-unrecorded"]["rendered"] == legacy["assessed-unrecorded"]["stored"]
    assert D(legacy["assessed-unrecorded"]["stored"]["cvss_base"]) > ts.MODIFIER_CEILING, "a carried legacy score above 9.2 that only the elevation explains"
    assert legacy["n17-assessed-unrecorded"]["d10_step"] == 5
    assert legacy["documented-pass"]["flags"] == legacy["ceiling-pass"]["flags"] == legacy["untagged"]["flags"] == []


def test_the_renderer_form_baseline_records_the_inputs_that_ruling_a_reads(committed, docs):
    name = "tagged/renderer-form"
    text = text_of(committed, name, "baseline/risk-scores.md")
    assert 'schema_version: "1.1"' in text and "## 6. Score Integrity" in text
    inputs = scoring_inputs(committed, name)
    fields = [row["Field"] for row in table_after(text, "### Scoring Inputs")]
    assert fields[:3] == ["cvss_vector", "exploitability.known_techniques", "exploitability.attack_complexity"]
    assert all("Flags" in row for row in table_after(text, SCORED.search(text).group(0)))
    for _, fid, record in records_of(docs[name]):
        rows, recorded = inputs[fid], record["stored_inputs"]
        assert rows["cvss_vector"] == record["stored"]["cvss_vector"]
        assert rows["tags"] == ",".join(recorded["tags_used"]) and rows["scored_on"] == recorded["scored_on"]
        assert ("score_bounds" in rows) == (recorded["score_bounds"] is not None)
        expl = [D(rows["exploitability." + key]) for key in ("known_techniques", "attack_complexity", "tooling_availability", "skill_level")]
        scale = [D(rows["scalability." + key]) for key in ("scriptability", "target_scope", "resource_requirements", "detection_difficulty")]
        assert ts.sub_score_mean(expl) == D(record["stored"]["exploitability"]) and ts.sub_score_mean(scale) == D(record["stored"]["scalability"]), fid
        assert rows["reachability.auth_barriers"] == rows["reachability.network_boundaries"] == "0"
        assert D(record["stored"]["reachability"]) == D("2.5"), "a trusted zone with no barriers"
        for key in ("rationale.cvss", "rationale.exploitability", "rationale.scalability", "rationale.reachability"):
            assert not re.search(r"[0-9]|\{\{", rows[key]), "narrative rows hold no numeral and no slot"
    assert set(inputs) == {fid for _, fid, _ in records_of(docs[name])}


def test_a_review_date_that_a_fallback_set_carries_that_flag_alone(docs):
    main = docs["legacy-format/main"]
    by_case = {r["case"]: r for _, _, r in records_of(main)}
    for case in ("rung-review-missing", "rung-sla-missing"):
        record = by_case[case]
        assert [f["flag"] for f in record["flags"] if f["field"] == "review_date"] == ["corrected:review_date:baseline-date"], case
        assert record["rendered"]["review_date"] == ts.review_date(main["baseline"]["frontmatter_date"], record["rendered"]["remediation_sla"])
    undated = {r["case"]: r for _, _, r in records_of(docs["legacy-format/no-baseline-date"])}
    assert docs["legacy-format/no-baseline-date"]["baseline"]["frontmatter_date"] is None
    kept = undated["rung-no-date-sla"]
    assert [f["flag"] for f in kept["flags"] if f["field"] == "review_date"] == ["unchecked:review_date:scoring-date-unknown"]
    assert kept["rendered"]["review_date"] == kept["stored"]["review_date"], "the stored review date is kept"
    restarted = undated["rung-no-date-both"]
    assert [f["flag"] for f in restarted["flags"] if f["field"] == "review_date"] == ["corrected:review_date:clock-restarted"]
    assert restarted["rendered"]["review_date"] == ts.review_date(docs["legacy-format/no-baseline-date"]["run"]["date"],
                                                                  restarted["rendered"]["remediation_sla"])


def template_pairs(text: str) -> set:
    """Every table's header line with the separator line under it."""
    lines = text.split("\n")
    return {(lines[i], lines[i + 1]) for i in range(len(lines) - 1) if lines[i].startswith("| ") and re.fullmatch(r"\|[-|]+\|", lines[i + 1])}


def line_shape(template_line: str):
    """A regular expression for a template line, with each {placeholder} standing for any text."""
    return re.compile(re.sub(r"\\\{[a-z_]+\\\}", ".+?", re.escape(template_line)))


def test_the_renderer_form_baseline_follows_the_1_1_template(committed):
    """T031's template is the authority for the 1.1 layout. The baseline's headings, table headers, static prose and Section 5 are the
    template's, and Section 2a is omitted because no finding is RESOLVED."""
    template = TEMPLATE.read_text(encoding="utf-8")
    assert "Schema version : 1.1" in template, "T031's template (schema 1.1) is what the renderer-form fixture follows"
    text = text_of(committed, "tagged/renderer-form", "baseline/risk-scores.md")
    own_h2, template_h2 = re.findall(r"^## (.+)$", text, re.MULTILINE), re.findall(r"^## (.+)$", template, re.MULTILINE)
    assert "2a. Resolved Findings" in template_h2 and own_h2 == [h for h in template_h2 if h != "2a. Resolved Findings"], (
        "the same sections in the same order, and Section 2a only when a finding is RESOLVED")
    assert re.findall(r"^### (.+)$", text.split("## 6. Score Integrity")[1], re.MULTILINE) == re.findall(
        r"^### (.+)$", template.split("## 6. Score Integrity")[1], re.MULTILINE), "Section 6's four subsections"
    assert set(re.findall(r"^#### (.+)$", text, re.MULTILINE)) <= set(re.findall(r"^#### (.+)$", template, re.MULTILINE))
    own_keys = re.findall(r"^( *[a-z_]+):", text.split("---\n")[1], re.MULTILINE)
    assert own_keys == re.findall(r"^( *[a-z_]+):", re.search(r"```yaml\n---\n(.*?)\n---\n```", template, re.DOTALL).group(1), re.MULTILINE)
    missing = [pair for pair in template_pairs(text) if pair not in template_pairs(template)]
    assert not missing, "tables whose header or separator is not the template's: %s" % missing[:3]
    assert len(template_pairs(text)) >= 11
    own5 = text[text.index("## 5. Scoring Methodology"):text.index("\n---\n\n## 6. Score Integrity")]
    assert own5.rstrip("\n") == template[template.index("## 5. Scoring Methodology"):template.index("---\n\n## 6. Score Integrity")].rstrip("\n")
    for static in (
            "Findings sorted by Composite score descending (highest risk first), and by finding ID within equal scores. Boundary values map "
            "to the higher severity band (e.g., 7.0 = High, 9.0 = Critical).",
            "Per-finding detail showing the full scoring rationale for each dimension. One subsection per open finding, ordered by composite "
            "score descending (matching Section 2 sort order).",
            "Remediation tracking metadata for each scored finding. Default values are severity-driven and intended for manual override by "
            "security managers during risk review.",
            "What the renderer checked, corrected or could not check, and the inputs it scored from. A first run with no baseline has "
            "nothing to correct, so its Score Flags table is empty.",
            "> **Correlated findings**: For correlation groups (Section 4a of the source threat model), the primary finding is scored "
            "independently. A NEW or UPDATED peer takes its primary's assessment and is scored with its own asset tags. An UNCHANGED peer keeps "
            "its own score, and is flagged `divergent` when that score differs from its primary's.",
            "**Resolved findings** (Section 2a, outside the distribution below):", "**Severity Distribution:**",
            "**Normalized (rounding only)**:", "**Baseline source**:", "**Tag source**:"):
        assert static in text and static in template, static
    for template_line in (line for line in template.split("\n") if line.startswith(
            ("{total_findings} open findings", "**Highest-Risk Component**", "**Category**", "**Score**: {cvss_base}", "**Score**: {exploitability}",
             "**Score**: {scalability}", "**Score**: {reachability} | **Trust Zone**"))):
        shape = line_shape(template_line)
        assert any(shape.fullmatch(line) for line in text.split("\n")), "no line has the shape of: %s" % template_line
    sentence = re.search(r"^(\d+) open findings were scored on (\d{4}-\d{2}-\d{2}): (\d+) Critical, (\d+) High, (\d+) Medium and (\d+) Low\.$", text, re.MULTILINE)
    rows = table_after(text, "**Severity Distribution:**")
    assert sentence and [int(sentence.group(i)) for i in (3, 4, 5, 6)] == [int(row["Count"]) for row in rows[:4]], "the open count, then four bands in order"
    assert [row["Severity"] for row in rows] == ["Critical", "High", "Medium", "Low", "Total"] and sum(int(r["Percentage"].rstrip("%")) for r in rows[:4]) == 100
    assert int(sentence.group(1)) == len(table_after(text, SCORED.search(text).group(0))) == int(rows[4]["Count"])
    assert "## 2a." not in text and "**Integrity**:" not in text, "no RESOLVED finding and no flagged finding in this baseline"
    breakdown = text[text.index("## 3. Dimensional Breakdown"):text.index("## 4. Governance Fields")]
    inputs = {}
    for row in table_after(text, "### Scoring Inputs"):
        inputs.setdefault(row["ID"], {})[row["Field"]] = row["Value"]
    assert not any(field.startswith(("metric_rationale.", "subscore_rationale.")) for rows in inputs.values() for field in rows)
    labels = ("Attack Vector (AV)", "Attack Complexity (AC)", "Privileges Required (PR)", "User Interaction (UI)", "Scope (S)",
              "Confidentiality (C)", "Integrity (I)", "Availability (A)", "Known Techniques", "Attack Complexity", "Tooling Availability",
              "Skill Level", "Scriptability", "Target Scope", "Resource Requirements", "Detection Difficulty")
    metric_rows = [row for row in (cells(line) for line in breakdown.split("\n") if line.startswith("| ")) if row[0] in labels]
    assert len(metric_rows) == 16 * len(inputs) and all(row[2] == "\u2014" for row in metric_rows), (
        "a per-metric rationale reads the dash when the scorer wrote none")
    for block in re.split(r"^### ", breakdown, flags=re.MULTILINE)[1:]:
        fid = re.match(r"([A-Z]+-\d+)", block).group(1)
        for key in ("rationale.cvss", "rationale.exploitability", "rationale.scalability", "rationale.reachability"):
            assert inputs[fid][key] in block, "%s: Section 3 holds the rationale that Section 6 keeps (%s)" % (fid, key)
    assert {row["Flags"] for row in table_after(text, SCORED.search(text).group(0))} == {"\u2014"}
    stamp = tachi_parts.read_stamp(text)
    assert stamp and stamp["renderer"] == "render-risk-scores.py" and "renderer=render-risk-scores.py" in template
    assert text.rstrip("\n").split("\n")[-1].startswith("<!-- tachi-provenance:")


def test_the_legacy_baseline_sarif_files_are_1_0_and_their_messages_hold_text_and_markdown(committed):
    template = json.loads(TEMPLATE_SARIF.read_text(encoding="utf-8"))
    assert all(set(result["message"]) == {"text", "markdown"} for result in template["runs"][0]["results"])
    for name in ("legacy-format/main", "regroup-pair/main"):
        results = json.loads(text_of(committed, name, "baseline/risk-scores.sarif"))["runs"][0]["results"]
        assert results and all(set(result["message"]) == {"text", "markdown"} for result in results), name
        assert all("score-flags" not in result["properties"] and "baseline-state" in result["properties"] for result in results), (
            "a pre-fix file: 1.1 drops baseline-state and adds score-flags")


# --------------------------------------------------------------------------- id-reuse, ties, regroup, drift
def test_the_id_reuse_case_gives_a_new_finding_an_id_that_the_baseline_used(committed, docs):
    name, doc = "id-reuse/pr1", docs["id-reuse/pr1"]
    rows = baseline_scores(text_of(committed, name, "baseline/risk-scores.md"))
    status = {fid: row["Status"] for fid, row in section7(text_of(committed, name, "run/threats.md")).items()}
    assert status["T-4"] == "NEW" and "T-4" in rows, "a NEW finding whose ID the baseline's risk-scores.md used"
    assert status["T-5"] == "NEW" and "T-5" not in rows, "the control: a NEW finding with a fresh ID"
    assert doc["routing"]["to_agent"] == ["T-4", "T-5"] and "T-4" not in doc["routing"]["carried"]
    old = doc["findings"]["T-4"]["baseline_row_not_inherited"]
    assert rows["T-4"]["risk_owner"] == old["risk_owner"] == "platform-team" and rows["T-4"]["risk_disposition"] == "Accept"
    new = doc["findings"]["T-4"]["rendered"]
    for key in ("cvss_vector", "composite_score", "risk_owner", "risk_disposition"):
        assert new[key] != old[key], "nothing of the old row reaches the new finding: %s" % key
    assert [f["kind"] for f in doc["findings"]["T-4"]["flags"]] == ["reused-id"] and doc["findings"]["T-5"]["flags"] == []
    low, high = ts.bounds(ts.default_score(ts.category_for_prefix("T")))
    for fid in ("T-4", "T-5"):  # the fresh chain, from the agent's inputs, on the shipped arithmetic
        payload, got = doc["agent_inputs"][fid], doc["findings"][fid]["rendered"]
        cvss = min(max(ts.base_score(payload["cvss_vector"]), low), high)
        expl = ts.sub_score_mean([D(v) for v in payload["exploitability"].values()])
        scale = ts.sub_score_mean([D(v) for v in payload["scalability"].values()])
        assert D(got["cvss_base"]) == cvss and D(got["exploitability"]) == expl and D(got["scalability"]) == scale, fid
        assert got["score_bounds"] == [str(low), str(high)] and got["risk_owner"] == "Unassigned" and got["scored_on"] == doc["run"]["date"]
        assert D(got["composite_score"]) == ts.composite(cvss, expl, scale, D(got["reachability"]))
        assert got["review_date"] == ts.review_date(doc["run"]["date"], got["remediation_sla"])
        assert set(payload) == {"cvss_vector", "exploitability", "scalability", "reachability", "rationale"}
        assert not any(re.search(r"[0-9]", text) for text in payload["rationale"].values()), "narrative prose holds no numeral"
    assert ts.base_score(doc["agent_inputs"]["T-4"]["cvss_vector"]) > high, "T-4 is held at the category bound"


def test_the_ties_variant_covers_a_band_moving_tie_a_rounding_only_tie_and_a_residual_tie(committed, docs):
    doc = docs["ties/scorer"]
    cases = [r["case"] for _, _, r in records_of(doc)]
    assert sum(c.startswith("tie-band-moves") for c in cases) == 3 and cases.count("tie-rounding-only") == 2
    assert {"tie-stored-as-half-up", "boundary-exact-70", "boundary-exact-90", "boundary-exact-40"} <= set(cases)
    assert doc["counts"]["normalized"] == 2 and doc["counts"]["flags_by_kind"] == {"corrected": 10}, "an optional flag never counts"
    controls = docs["ties/controls"]
    assert controls["stage"] == "compensating-controls" and len(controls["controls_cases"]) == 6
    scored = baseline_scores(text_of(committed, "ties/controls", "run/risk-scores.md"))
    for case in controls["controls_cases"]:
        inherent = D(case["inherent"])
        assert D(scored[case["finding"]]["composite_score"]) == inherent
        residual = ts.residual_score(inherent, D(case["reduction_factor"]))
        assert str(residual) == case["residual"] and ts.band(residual) == case["residual_band"] and ts.band(inherent) == case["inherent_band"]
        assert D(case["residual_exact"]) == inherent * (1 - D(case["reduction_factor"]))
    assert sum(c["is_tie"] for c in controls["controls_cases"]) == 4
    assert {c["finding"]: c["residual"] for c in controls["controls_cases"]}["S-1"] == "4.6", "4.55 gives 4.6 (residual-risk.md)"
    assert any(c["float_round_would_give"] != c["residual"] for c in controls["controls_cases"]), "a case that float round() gets wrong"
    assert any(c["half_even_would_give"] != c["residual"] for c in controls["controls_cases"]), "a case that round-half-even gets wrong"


def test_the_regroup_pair_changes_a_primary_and_keeps_every_carried_score(committed, docs):
    name, runs = "regroup-pair/main", docs["regroup-pair/main"]["runs"]
    baseline = baseline_scores(text_of(committed, name, "baseline/risk-scores.md"))
    texts = {run: text_of(committed, name, runs[run]["threats"]) for run in runs}
    status = {run: {fid: row["Status"] for fid, row in section7(texts[run]).items()} for run in runs}
    assert {fid: s for fid, s in status["run2"].items() if s != "UNCHANGED"} == {"D-1": "NEW", "E-1": "UPDATED"}
    assert set(status["run3"].values()) == set(status["run1"].values()) == {"UNCHANGED"} and "D-1" not in status["run1"]
    for run in runs:
        listed = [[m.strip() for m in row["Findings"].split(",")] for row in table_after(texts[run], "## 4a. Correlated Findings")]
        assert listed == [g["members"] for g in runs[run]["groups"]], run
        assert all(g["primary"] == g["members"][0] for g in runs[run]["groups"])
    assert runs["run1"]["groups"][0]["primary"] == "I-1" and runs["run2"]["groups"][0]["primary"] == "T-1", "the primary changes"
    for run, source in (("run1", "baseline/threats.md"), ("run2", "run1/threats.md"), ("run3", "run2/threats.md")):
        assert re.search(r'^  source: "%s"$' % re.escape(source), texts[run], re.MULTILINE), run
    assert baseline["LLM-1"]["composite_score"] == baseline["I-1"]["composite_score"] and baseline["AG-1"]["composite_score"] == baseline["R-1"]["composite_score"]
    assert baseline["T-1"]["severity_band"] == "Medium" and baseline["I-1"]["severity_band"] == "High"
    run2 = runs["run2"]["findings"]
    for fid in ("I-1", "LLM-1"):
        assert run2[fid]["rendered"] == run2[fid]["stored"], "no score changes because of the regroup alone"
        assert [f["flag"] for f in run2[fid]["flags"]] == ["divergent:composite_score:primary=T-1"]
        assert D(run2[fid]["stored"]["composite_score"]) > D(run2["T-1"]["rendered"]["composite_score"])
    for fid in ("S-1", "S-2", "T-1", "T-2", "R-1", "AG-1"):
        assert run2[fid]["rendered"] == run2[fid]["stored"] and run2[fid]["flags"] == [], fid
    for fid in ("D-1", "E-1"):
        for key in ("cvss_vector", "cvss_base", "exploitability", "scalability", "reachability", "composite_score", "severity_band"):
            assert run2[fid]["rendered"][key] == run2["T-1"]["rendered"][key], (fid, key)
    assert run2["D-1"]["rendered"]["risk_owner"] == "Unassigned"
    assert run2["E-1"]["rendered"]["risk_owner"] == "appsec-team" == run2["E-1"]["stored"]["risk_owner"], "an UPDATED peer keeps its owner"
    assert runs["run2"]["routing"]["copy_primary"] == {"D-1": "T-1", "E-1": "T-1"} and runs["run2"]["routing"]["to_agent"] == []
    run3 = runs["run3"]["findings"]
    assert all(run3[fid]["rendered"] == run2[fid]["rendered"] for fid in run3), "the unchanged re-run keeps every value"
    assert sorted(fid for fid, r in run3.items() if r["flags"]) == ["I-1", "LLM-1"]


def test_the_drift_form_file_is_a_drift_form_that_the_populator_cannot_read(committed, docs):
    name = "tagged/s13-drift-form"
    text = text_of(committed, name, "run/threats.md")
    assert re.search(r"^## Section 7: Recommended Actions", text, re.MULTILINE) and "## 7. Recommended Actions" not in text
    ids = re.findall(r"^\d+\. \*\*([A-Z]+-\d+) ", text, re.MULTILINE)
    assert sorted(ids, key=prefix_rank) == sorted(docs[name]["findings"], key=prefix_rank), "Section 7 is a numbered list of bolded IDs"
    assert all("| **id** | %s |" % fid in text for fid in ids) and text.count("| **component** |") == len(ids)
    assert "Status" not in text.split("## Section 7")[1].split("## Affected Assets")[0], "no Status column to read"


# --------------------------------------------------------------------------- the base set stays as T021 and the gated subset took it
def _walk_order(path: str) -> tuple:
    """os.walk's order with sorted directories: a directory's own files first, then its subdirectories by name."""
    parts = path.split("/")
    return tuple((0 if index == len(parts) - 1 else 1, part) for index, part in enumerate(parts))


def test_the_base_set_is_byte_for_byte_what_t021_and_the_gated_subset_were_taken_from(committed):
    """W1's digest, over the base parts only: sha256 over each (relative path, file sha256) in os.walk order. The variants sit beside
    the base set and must never move a byte of it. A deliberate change re-baselines T021 and the gated subset."""
    import hashlib
    entries = sorted((p for p in committed if p.split("/")[0] in BASE_SET_DIRECTORIES), key=_walk_order)
    outer, total = hashlib.sha256(), 0
    for path in entries:
        outer.update(path.encode("utf-8") + b"\0" + hashlib.sha256(committed[path]).digest())
        total += len(committed[path])
    assert (outer.hexdigest()[:24], len(entries), total) == (BASE_SET_DIGEST, 212, 5387654)
