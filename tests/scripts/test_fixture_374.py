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

* **PR 2's cases (T148, then T103; the sections that start "PR 2's cases" and "PR 2's run directories").** T148's chain-cap and
  id-reuse variants are re-derived from their files with a separate coding of S-3 and ruling B. T103's six scenarios under
  ``pr2-runs/`` are read back through the shipped validators (``tachi_parts``) and the shipped reference-set reader: the records, briefs,
  ID map and Phase 1 tables of four provenance runs, with each finding's provenance and Phase 2's lineages worked out again from the
  files; the trees stage under Rule 2 and the report stage, with their plans, batch inputs, parts and merged manifest. A materialized copy
  (``gen.materialize``) is checked by D3's plan guard, which the committed copy cannot satisfy (its digests bind a root that exists nowhere).

Not here: chain formation on the fixture's chain material, which T115 and T116 test with the real script, and what the check and the
assemblers do with the PR 2 scenarios, which T095, T096, T108 and T109 test. No renderer exists yet, so none of the
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


# =========================================================================== PR 2's cases (T148; S-4, S-3, ADR-050 D7, D12, D13)
# Three scenarios that wait on no ruling: chain-cap/main (more than 105 consolidated chains, for S-3(g)'s bound and FR-K4.1b's check),
# id-reuse/pr2 (a baseline whose high-water mark sits above its live IDs) and id-reuse/pr2-no-mark (a baseline with no mark, as every
# pre-PR 2 baseline). No chain script and no reissue check exists yet, so these tests run neither. Each derives its values from the
# committed files with its own coding of the rules and compares them with expected-outcomes.json. The generator declares the chains by
# construction and these tests re-derive them, so a mistake on either side shows. T115 and T095 then run the real scripts on the same files.
# Every name here starts pr2_ or PR2_, so that T040's tests, merged in beside this section, can't meet them.
PR2_SCENARIOS = ("chain-cap/main", "id-reuse/pr2", "id-reuse/pr2-no-mark")
PR2_TABLE = HERE.parents[1] / ".claude" / "skills" / "tachi-shared" / "references" / "attack-chain-patterns-shared.md"
PR2_CATEGORY = {"Spoofing": "S", "Tampering": "T", "Repudiation": "R", "Info-Disclosure": "I", "Denial-of-Service": "D",
                "Privilege-Escalation": "E"}
PR2_OUTCOME = re.compile(r"chains written \([1-9][0-9]{0,5}\); candidates [0-9]{1,6}; surfaced [1-5]")
PR2_ROW = re.compile(r"\| CHAIN-[0-9]{3,6} \| L[1-7]( \u2192 L[1-7])+ \| [A-Z]+-[0-9]+( \u2192 [A-Z]+-[0-9]+)+ \| (Critical|High|Medium|Low) \| [A-Z]+-[0-9]+ \|")
PR2_MARK_LINE = re.compile(r"\*\*ID high-water mark\*\*: ")
PR2_MARKS = re.compile(r"\*\*ID high-water mark\*\*: `((?:S|T|R|I|D|E|AG|AGP|LLM|OI|MI|TE)-[1-9][0-9]*(?:, (?:S|T|R|I|D|E|AG|AGP|LLM|OI|MI|TE)-[1-9][0-9]*)*)`")


@pytest.fixture(scope="module")
def pr2_docs(committed) -> dict:
    return {name: json.loads(committed["%s/expected-outcomes.json" % name].decode("utf-8")) for name in PR2_SCENARIOS}


@pytest.fixture(scope="module")
def pr2_parsers():
    """scripts/tachi_parsers.py, the reference-set reader that every chain and check script reads Section 7 through."""
    import sys  # a local import: the module's own import lines belong to other tasks
    keep = sys.dont_write_bytecode
    sys.dont_write_bytecode = True  # a .pyc under scripts/ would dirty the tree under test (ADR-049 D8)
    sys.path.insert(0, str(HERE.parents[1] / "scripts"))
    try:
        import tachi_parsers
    finally:
        sys.dont_write_bytecode = keep
    return tachi_parsers


def pr2_text(committed: dict, name: str, rel: str) -> str:
    return committed["%s/%s" % (name, rel)].decode("utf-8")


def pr2_s2(finding_id: str) -> tuple:
    """S-2's total order: the prefix's rank, then the number as an integer."""
    return (PREFIXES.index(prefix_of(finding_id)), number_of(finding_id))


def pr2_norm(name: str) -> str:
    """D13: component names are compared after casefolding and collapsing whitespace."""
    return " ".join(name.casefold().split())


def pr2_transitions() -> set:
    """attack-chain-patterns-shared.md's transition lookup table, read from the file: {((category, layer), (category, layer))}."""
    pairs, layer = set(), None
    for line in PR2_TABLE.read_text(encoding="utf-8").split("\n"):
        heading = re.match(r"### Source: L([1-7]) ", line)
        if heading:
            layer = int(heading.group(1))
            continue
        row = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if layer and line.startswith("|") and len(row) == 5 and re.fullmatch(r"L[1-7]", row[1]):
            pairs.add(((PR2_CATEGORY[row[0]], layer), (PR2_CATEGORY[row[2]], int(row[1][1:]))))
    return pairs


def pr2_breaking(ids: list, risks: list) -> str:
    """Step 4 of orchestrator.md's Phase 3.5, coded from its words."""
    size = len(ids)
    if size == 2:
        return ids[1] if RISK_RANK[risks[1]] > RISK_RANK[risks[0]] else ids[0]
    if size == 3:
        return ids[1]
    scored = [(i * (size - 1 - i), RISK_RANK[risks[i]], -i) for i in range(1, size - 1)]
    return ids[1 + scored.index(max(scored))]


def pr2_derive_chains(threats: str, inventory: dict) -> dict:
    """S-3 and ADR-050 D13 over the committed files: finding set, links, assembly, deduplication, filter, folding, rank, surfacing."""
    table = pr2_transitions()
    layer_of = {pr2_norm(c["name"]): c["maestro_layer"] for c in inventory["components"]}
    nodes = []
    for row in table_after(threats, "## 7. Recommended Actions"):
        layer = re.match(r"L([1-7])\b", row["MAESTRO Layer"]) or re.fullmatch(r"L([1-7])", layer_of.get(pr2_norm(row["Component"]), ""))
        if prefix_of(row["Finding ID"]) in STRIDE and layer:  # STRIDE prefixes only, and a layer from L1 to L7
            nodes.append({"id": row["Finding ID"], "prefix": prefix_of(row["Finding ID"]), "layer": int(layer.group(1)),
                          "comp": pr2_norm(row["Component"]), "risk": row["Risk Level"]})
    ahead: dict = {}
    for flow in inventory["data_flows"]:
        ahead.setdefault(pr2_norm(flow["source"]), []).append(pr2_norm(flow["destination"]))

    def reach(start: str) -> set:
        seen, stack = set(), list(ahead.get(start, ()))
        while stack:
            name = stack.pop()
            if name not in seen:
                seen.add(name)
                stack.extend(ahead.get(name, ()))
        return seen

    reachable = {comp: reach(comp) for comp in {node["comp"] for node in nodes}}
    order = sorted(nodes, key=lambda n: (-RISK_RANK[n["risk"]], pr2_s2(n["id"])))  # S-3(c): severity, highest first, then S-2

    def links(a: dict, b: dict) -> bool:
        return (a["layer"] != b["layer"] and (b["comp"] in reachable[a["comp"]] or a["comp"] in reachable[b["comp"]])
                and ((a["prefix"], a["layer"]), (b["prefix"], b["layer"])) in table)

    onward = {a["id"]: [b for b in order if b is not a and links(a, b)] for a in order}
    assembled = []
    for start in order:
        if not onward[start["id"]]:
            continue
        chain = [start]
        while True:  # greedy: the first candidate, in that order, on a layer the chain does not have yet
            nxt = next((b for b in onward[chain[-1]["id"]] if b["layer"] not in {m["layer"] for m in chain}), None)
            if nxt is None:
                break
            chain.append(nxt)
        assembled.append(chain)

    def rank_key(chain: list) -> tuple:  # S-3(e)
        return (-max(RISK_RANK[m["risk"]] for m in chain), -len({m["layer"] for m in chain}), tuple(pr2_s2(m["id"]) for m in chain))

    best: dict = {}
    for chain in assembled:  # identical finding sets: the higher-ranked chain stays
        key = frozenset(m["id"] for m in chain)
        if key not in best or rank_key(chain) < rank_key(best[key]):
            best[key] = chain
    unique = list(best.values())
    passing = [c for c in unique if len({m["layer"] for m in c}) >= 2 and max(RISK_RANK[m["risk"]] for m in c) >= RISK_RANK["High"]]

    def inside(short: list, long: list) -> bool:
        a, b = [m["id"] for m in short], [m["id"] for m in long]
        return len(b) > len(a) and any(b[i:i + len(a)] == a for i in range(len(b) - len(a) + 1))

    kept = sorted((c for c in passing if not any(inside(c, other) for other in passing)), key=rank_key)
    chains, shown = [], []
    for position, chain in enumerate(kept, start=1):
        ids, risks = [m["id"] for m in chain], [m["risk"] for m in chain]
        chains.append({"id": "CHAIN-%03d" % position, "members": ids, "layers": ["L%d" % m["layer"] for m in chain], "risks": risks,
                       "max_severity": max(risks, key=RISK_RANK.get), "breaking_target": pr2_breaking(ids, risks), "surfaced": False,
                       "against_flow": any(b["comp"] not in reachable[a["comp"]] for a, b in zip(chain, chain[1:]))})  # reachable only the other way
    for chain in chains:  # S-3(f)
        if len(shown) < 5 and not any(other["members"][-1] == chain["members"][-1] for other in shown):
            chain["surfaced"] = True
            chain["converging"] = sum(1 for other in chains if other is not chain and other["members"][-1] == chain["members"][-1])
            shown.append(chain)
    rest = [c for c in chains if not c["surfaced"]]
    arrow = " \u2192 "
    return {"candidates": len(assembled), "dropped": {"deduplicated": len(assembled) - len(unique), "filtered": len(unique) - len(passing),
                                                       "folded": len(passing) - len(kept)},
            "chains": chains, "surfaced": [c["id"] for c in shown], "not_listed": max(len(rest) - 100, 0),
            "rows": ["| %s | %s | %s | %s | %s |" % (c["id"], arrow.join(c["layers"]), arrow.join(c["members"]), c["max_severity"], c["breaking_target"])
                     for c in rest[:100]]}


@pytest.fixture(scope="module")
def pr2_chain_cap(committed, pr2_docs) -> types.SimpleNamespace:
    threats = pr2_text(committed, "chain-cap/main", "run/threats.md")
    inventory = json.loads(pr2_text(committed, "chain-cap/main", "run/tachi-build/phase1/inventory.json"))
    return types.SimpleNamespace(threats=threats, inventory=inventory, doc=pr2_docs["chain-cap/main"],
                                 derived=pr2_derive_chains(threats, inventory), rows=table_after(threats, "## 7. Recommended Actions"))


# --------------------------------------------------------------------------- structure
def test_pr2_every_scenario_is_committed_and_its_outcome_file_points_at_real_files(committed, pr2_docs):
    assert {path.split("/")[0] for path in committed if path.endswith("/expected-outcomes.json")} >= {"chain-cap", "id-reuse"}
    for name, doc in pr2_docs.items():
        assert doc["schema"] == "tachi.fixture-expected/1"
        assert "%s/%s" % (doc["variant"], doc["scenario"]) == name
        assert doc["stage"] and doc["summary"] and doc["notes"], name
        assert doc["run"]["date"] == "2026-11-23"
        for rel in filter(None, (doc["run"].get(key) for key in ("threats", "inventory"))):
            assert "%s/%s" % (name, rel) in committed, "%s names %s, which is not committed" % (name, rel)
    assert "id-reuse/pr2/baseline/threats.md" in committed and "id-reuse/pr2-no-mark/baseline/threats.md" in committed


# --------------------------------------------------------------------------- chain-cap
def test_pr2_the_chain_material_is_read_by_the_shipped_reference_set_reader(pr2_chain_cap, pr2_parsers):
    reference = pr2_parsers.parse_reference_set(pr2_chain_cap.threats, "chain-cap threats.md")
    assert len(reference["open"]) == pr2_chain_cap.doc["counts"]["findings_in_section_7"] and not reference["resolved"]
    assert not reference["duplicates"]
    headings = [line for line in pr2_chain_cap.threats.split("\n") if line.startswith("## ")]
    assert headings == ["## 5. Coverage Matrix", "## 6. Risk Summary", "## 7. Recommended Actions", "## 8. Delta Summary", "## Affected Assets"], (
        "the outcome record lands before Section 5, or before Affected Assets: both must be there")
    assert "Attack chain outcome" not in pr2_chain_cap.threats and "Attack Chain Outcome" not in pr2_chain_cap.threats, "the script writes the record"


def test_pr2_the_inventory_follows_the_phase1_contract(committed, pr2_chain_cap):
    """contracts/threat-model-records.md, 'Persisted Phase 1 tables': keys, sizes, enums, and every name a component."""
    inventory = pr2_chain_cap.inventory
    assert set(inventory) == {"schema", "components", "data_flows", "trust_zones"} and inventory["schema"] == "tachi.phase1-inventory/1"
    assert len(committed["chain-cap/main/run/tachi-build/phase1/inventory.json"]) <= 512 * 1024
    components = inventory["components"]
    assert 1 <= len(components) <= 500 and len(inventory["data_flows"]) <= 5000 and len(inventory["trust_zones"]) <= 200
    names = [pr2_norm(c["name"]) for c in components]
    assert len(set(names)) == len(names), "names are unique after casefolding and collapsing whitespace"
    for component in components:
        assert set(component) == {"name", "dfd_type", "maestro_layer", "description"}
        assert component["dfd_type"] in {"External Entity", "Process", "Data Store", "Data Flow"}
        assert re.fullmatch(r"L[1-7]|Unclassified", component["maestro_layer"]) and len(component["description"]) <= 500
        assert 1 <= len(component["name"]) <= 200 and not re.search(r"[\x00-\x1f]", component["name"])
    for flow in inventory["data_flows"]:
        assert set(flow) == {"source", "destination", "data", "protocol"} and len(flow["data"]) <= 200 and len(flow["protocol"]) <= 100
        assert pr2_norm(flow["source"]) in names and pr2_norm(flow["destination"]) in names
    listed = [name for zone in inventory["trust_zones"] for name in zone["components"]]
    assert sorted(listed) == sorted(c["name"] for c in components), "every component sits in one zone"


def test_pr2_every_finding_names_a_component_of_the_inventory_and_its_layer(pr2_chain_cap):
    layer_of = {pr2_norm(c["name"]): c["maestro_layer"] for c in pr2_chain_cap.inventory["components"]}
    for row in pr2_chain_cap.rows:
        layer = layer_of[pr2_norm(row["Component"])]
        assert row["MAESTRO Layer"].startswith(layer) if layer != "Unclassified" else row["MAESTRO Layer"] == "Unclassified", row["Finding ID"]
    assert {r["Status"] for r in pr2_chain_cap.rows} == {"NEW"}


def test_pr2_no_flow_joins_two_islands(pr2_chain_cap):
    """The counts add up island by island only if the islands are separate: the undirected flow graph has as many parts as islands."""
    parent = {pr2_norm(c["name"]): pr2_norm(c["name"]) for c in pr2_chain_cap.inventory["components"]}

    def find(name: str) -> str:
        while parent[name] != name:
            parent[name] = parent[parent[name]]
            name = parent[name]
        return name

    for flow in pr2_chain_cap.inventory["data_flows"]:
        parent[find(pr2_norm(flow["source"]))] = find(pr2_norm(flow["destination"]))
    assert len({find(name) for name in parent}) == pr2_chain_cap.doc["counts"]["islands"]


def test_pr2_an_independent_coding_of_s3_gives_the_declared_chains(pr2_chain_cap):
    derived, doc = pr2_chain_cap.derived, pr2_chain_cap.doc
    counts = doc["counts"]
    assert derived["candidates"] == counts["candidates"] and derived["dropped"] == counts["dropped"]
    assert len(derived["chains"]) == counts["consolidated"] and derived["surfaced"] == doc["surfaced"]
    assert derived["not_listed"] == counts["not_listed"] and derived["rows"] == doc["compact_rows"]
    keys = ("id", "members", "layers", "max_severity", "breaking_target", "surfaced", "converging", "against_flow")
    assert [{k: c[k] for k in keys if k in c} for c in derived["chains"]] == [{k: c[k] for k in keys if k in c} for c in doc["chains"]]
    assert sum(1 for c in derived["chains"] if c["against_flow"]) == counts["against_flow"]
    assert [c["id"] for c in derived["chains"] if not c["surfaced"] and any(
        s["surfaced"] and s["members"][-1] == c["members"][-1] for s in derived["chains"])] == doc["skipped_for_a_shared_terminal"]


def test_pr2_the_bound_has_something_to_cut_and_a_remainder_to_state(pr2_chain_cap):
    """S-3(g) and FR-K4.1b: more than 105 consolidated chains, five in full, 100 compact rows and a last line for the rest."""
    doc = pr2_chain_cap.doc
    consolidated, shown, rows = doc["counts"]["consolidated"], len(doc["surfaced"]), doc["compact_rows"]
    assert consolidated > 105 and shown == 5 and len(rows) == min(100, consolidated - shown) == 100
    remainder = consolidated - shown - len(rows)
    assert remainder >= 1 and doc["counts"]["not_listed"] == remainder
    assert doc["remainder_line"] == "**Consolidated chains not listed**: %d" % remainder
    assert PR2_OUTCOME.fullmatch(doc["outcome_record"]) and doc["outcome_record"] == "chains written (%d); candidates %d; surfaced %d" % (
        consolidated, doc["counts"]["candidates"], shown)
    assert doc["frontmatter_counts"] == {"chain_count": consolidated, "surfaced_count": shown, "candidate_count": doc["counts"]["candidates"]}
    assert doc["counts"]["candidates"] >= consolidated
    assert all(PR2_ROW.fullmatch(row) for row in rows)
    listed = [row.split(" | ")[0].lstrip("| ") for row in rows]
    assert listed == sorted(listed) and not set(listed) & set(doc["surfaced"]), "rank order, and nothing shown in full is listed again"


def test_pr2_the_case_holds_each_rule_the_script_must_apply(pr2_chain_cap):
    """The variant is only worth having if it reaches every branch of S-3: the generator's choice of islands must stay that way."""
    derived, doc = pr2_chain_cap.derived, pr2_chain_cap.doc
    assert all(derived["dropped"][kind] >= 1 for kind in ("deduplicated", "filtered", "folded")), derived["dropped"]
    kinds = {c["kind"] for c in doc["chains"]}
    assert {"v-arms", "path-4", "path-3", "mutual", "closure-2", "closure-3", "plain"} <= kinds
    assert any(c["surfaced"] and c["converging"] >= 1 for c in doc["chains"]), "a surfaced chain shares its terminal finding with another"
    against = [c for c in doc["chains"] if c["against_flow"]]
    assert against and len(against) < len(doc["chains"]) and {"plain", "closure-3"} <= {c["kind"] for c in against}, (
        "chains that need reachability against a link's direction (orchestrator.md: 'or vice versa'), and chains that do not")
    positions = [i for i, c in enumerate(doc["chains"]) if c["id"] in doc["skipped_for_a_shared_terminal"]]
    assert positions and min(positions) < 6, "a chain is passed over for surfacing, and within the first places of the ranking"
    assert max(len(c["members"]) for c in doc["chains"]) == 4 and {len(c["members"]) for c in doc["chains"]} == {2, 3, 4}
    in_chains = {i for c in doc["chains"] for i in c["members"]}
    left_out = [r["Finding ID"] for r in pr2_chain_cap.rows if prefix_of(r["Finding ID"]) in ("AG", "LLM") or r["MAESTRO Layer"] == "Unclassified"]
    assert len(left_out) == 6 and not set(left_out) & in_chains, "findings that the chain script must leave out are in Section 7 and in no chain"
    arms = {tuple(c["layers"]): c for c in doc["chains"] if c["kind"] == "v-arms"}
    first, second = arms[("L5", "L6", "L3", "L7")], arms[("L4", "L6", "L3", "L7")]
    assert first["breaking_target"] == first["members"][2] and second["breaking_target"] == second["members"][1], (
        "the two arms of the V use both tie-breaks of the four-finding rule: the higher severity, then the earlier position")


# --------------------------------------------------------------------------- id-reuse, PR 2
def pr2_mark_lines(text: str) -> list:
    """The lines that read as the mark: after the front matter, before the first ## heading, outside code fences (the shipped rule)."""
    lines = text.split("\n")
    start = lines.index("---", 1) + 1
    end = next(i for i, line in enumerate(lines) if i >= start and line.startswith("## "))
    found, fenced = [], False
    for line in lines[start:end]:
        if line.startswith("```"):
            fenced = not fenced
        elif not fenced and PR2_MARK_LINE.match(line):
            found.append(line)
    return found


def pr2_highest(ids: list) -> dict:
    top: dict = {}
    for finding_id in ids:
        top[prefix_of(finding_id)] = max(top.get(prefix_of(finding_id), 0), number_of(finding_id))
    return {prefix: top[prefix] for prefix in PREFIXES if prefix in top}


def pr2_read_case(committed: dict, name: str) -> types.SimpleNamespace:
    baseline, run = (pr2_text(committed, name, "%s/threats.md" % part) for part in ("baseline", "run"))
    marks = pr2_mark_lines(baseline)
    mark = None
    if len(marks) == 1:  # zero or several read as absent
        entries = PR2_MARKS.fullmatch(marks[0]).group(1).split(", ")
        mark = {prefix_of(entry): number_of(entry) for entry in entries}
        assert [prefix_of(entry) for entry in entries] == [p for p in PREFIXES if p in mark], "one entry for each prefix, in S-2's order"
    live = [row["Finding ID"] for row in table_after(baseline, "## 7. Recommended Actions")]
    earlier = [row["ID"] for row in table_after(baseline, "## 4c. Resolved Findings")]
    rows = table_after(run, "## 7. Recommended Actions")
    return types.SimpleNamespace(baseline=baseline, run=run, marks=marks, mark=mark, live=live, earlier=earlier, rows=rows,
                                 new=[r["Finding ID"] for r in rows if r["Status"] == "NEW"], open=[r["Finding ID"] for r in rows],
                                 run_resolved=[r["ID"] for r in table_after(run, "## 4c. Resolved Findings")])


@pytest.mark.parametrize("name", ["id-reuse/pr2", "id-reuse/pr2-no-mark"])
def test_pr2_the_reissue_rule_and_the_run_mark_follow_from_the_files(committed, pr2_docs, name):
    case, doc = pr2_read_case(committed, name), pr2_docs[name]
    seed = pr2_highest(case.live + case.earlier)  # where the baseline has no mark: its highest live or Section 4c ID
    reference = case.mark if case.mark is not None else seed
    flagged = {}
    for finding_id in case.new:
        why = (["baseline-open"] if finding_id in case.live else []) + (["baseline-resolved"] if finding_id in case.earlier else [])
        if case.mark is not None and number_of(finding_id) <= case.mark[prefix_of(finding_id)]:
            why.append("at-or-below-mark")
        if case.mark is None:  # whether a seeded mark is read as a mark is not ruled, so no NEW ID may depend on it
            assert why or number_of(finding_id) > seed.get(prefix_of(finding_id), 0), "%s sits under the seed, unused" % finding_id
        flagged[finding_id] = why
    reissue = doc["reissue"]
    assert sorted((fid for fid, why in flagged.items() if why), key=pr2_s2) == reissue["flagged"] and reissue["count"] == len(reissue["flagged"])
    assert {fid: j["reasons"] for fid, j in reissue["new_findings"].items()} == flagged
    assert sorted((fid for fid, why in flagged.items() if not why), key=pr2_s2) == reissue["unflagged_new"]
    assert reissue["exit_code"] == (5 if reissue["flagged"] else 0)
    run_highest = pr2_highest(case.open)
    result = {p: max(run_highest.get(p, 0), reference.get(p, 0)) for p in PREFIXES if p in run_highest or p in reference}
    assert result == doc["id_mark"]["result"]
    assert result == {p: max(pr2_highest(case.open + case.run_resolved).get(p, 0), reference.get(p, 0)) for p in result}, (
        "the run's own Section 4c must not decide the mark: the case would then depend on how 'highest' is read")
    assert doc["id_mark"]["line"] == "**ID high-water mark**: `%s`" % ", ".join("%s-%d" % (p, result[p]) for p in PREFIXES if p in result)
    assert doc["id_mark"]["moved"] == [p for p in result if result[p] > reference.get(p, 0)] and doc["id_mark"]["run_highest"] == run_highest
    assert doc["baseline"]["seed"] == seed and doc["baseline"]["mark"] == case.mark and doc["baseline"]["mark_present"] == (case.mark is not None)


def test_pr2_the_baseline_mark_sits_above_its_live_ids(committed):
    case = pr2_read_case(committed, "id-reuse/pr2")
    assert len(case.marks) == 1 and "```" not in case.baseline
    seed, live = pr2_highest(case.live + case.earlier), pr2_highest(case.live)
    assert set(case.mark) == set(live) == set(PREFIXES), "a mark entry for every prefix in use"
    assert all(case.mark[p] >= seed[p] for p in case.mark), "a mark never sits under an ID that the baseline used"
    above = [p for p in case.mark if case.mark[p] > live[p]]
    assert len(above) >= 5, "the case: the mark sits above the live IDs for several prefixes"
    assert [p for p in case.mark if case.mark[p] > seed[p]], "and above what a seed from live IDs and Section 4c would give"
    assert [p for p in case.mark if case.mark[p] == live[p]], "and equals them for some, so a mark without a gap is covered too"
    # S-2's prefix order is not the order of the tables: TE comes last in the mark, and AGP between AG and LLM
    assert list(case.mark)[-1] == "TE" and list(case.mark).index("AGP") == list(case.mark).index("AG") + 1


def test_pr2_the_no_mark_baseline_has_no_mark_and_the_seed_needs_section_4c(committed, pr2_docs):
    case = pr2_read_case(committed, "id-reuse/pr2-no-mark")
    assert case.marks == [] and case.mark is None and not PR2_MARK_LINE.search(case.baseline)
    assert pr2_docs["id-reuse/pr2-no-mark"]["baseline"]["mark_line"] is None
    assert pr2_highest(case.live) != pr2_highest(case.live + case.earlier), "a seed from the live IDs alone would miss Section 4c's IDs"
    assert any(finding_id in case.earlier for finding_id in case.new), "and a NEW finding takes one of them"


def test_pr2_the_mark_case_holds_each_kind_of_new_finding(committed, pr2_docs):
    case, doc = pr2_read_case(committed, "id-reuse/pr2"), pr2_docs["id-reuse/pr2"]
    judged = doc["reissue"]["new_findings"]
    assert [fid for fid, j in judged.items() if j["reasons"] == ["at-or-below-mark"] and number_of(fid) > pr2_highest(case.earlier + case.live)[prefix_of(fid)]], (
        "an ID above everything that the baseline's lists hold, which only the mark catches")
    assert [fid for fid, j in judged.items() if j["reasons"] == ["at-or-below-mark"]], "and one that no list holds at all"
    assert [fid for fid, j in judged.items() if "baseline-resolved" in j["reasons"]], "an ID that Section 4c holds"
    assert [fid for fid, j in judged.items() if j["boundary"] and j["flagged"]], "an ID equal to the mark"
    above = [fid for fid, j in judged.items() if not j["flagged"] and number_of(fid) == case.mark[prefix_of(fid)] + 1]
    skipped = [fid for fid, j in judged.items() if not j["flagged"] and number_of(fid) > pr2_highest(case.live)[prefix_of(fid)] + 1]
    assert above and skipped, "numbers just above the mark, and numbers that skip some live IDs (PR 2 says numbering can skip)"
    carried = [r for r in case.rows if r["Status"] != "NEW"]
    assert carried and all(r["Finding ID"] in case.live for r in carried), "every carried finding is in the baseline"
    assert [r for r in carried if number_of(r["Finding ID"]) < case.mark[prefix_of(r["Finding ID"])]], "carried findings under the mark are never flagged"
    assert set(case.live) <= set(case.open) | set(case.run_resolved), "the run loses no baseline finding silently"


@pytest.mark.parametrize("name", ["id-reuse/pr2", "id-reuse/pr2-no-mark"])
def test_pr2_the_run_and_its_baseline_agree_and_both_pass_the_shipped_reader(committed, pr2_parsers, name):
    case = pr2_read_case(committed, name)
    run_set = pr2_parsers.parse_reference_set(case.run, "run threats.md")
    assert [f["id"] for f in run_set["open"]] == sorted(case.open, key=pr2_s2) and not run_set["duplicates"]
    base_set = pr2_parsers.parse_reference_set(case.baseline, "baseline threats.md")
    assert sorted(f["id"] for f in base_set["open"]) == sorted(case.live) and sorted(r["id"] for r in base_set["resolved"]) == sorted(case.earlier)
    front = case.run.split("---")[1]
    assert re.search(r'^  source: "baseline/threats.md"$', front, re.MULTILINE)
    assert re.search(r"^  finding_count: %d$" % len(case.live), front, re.MULTILINE), "the run counts the baseline's live findings"
    assert not set(case.earlier) & set(case.run_resolved), "Section 4c of the baseline is not the run's"
    assert not PR2_MARK_LINE.search(case.run), "id-mark writes the run's mark, so the run comes without one"
    token = re.compile(r"\b(?:S|T|R|I|D|E|AG|AGP|LLM|OI|MI|TE)-[0-9]+\b")
    assert set(token.findall(case.run)) == set(case.open) | set(case.run_resolved), "the renumbering left no ID of the gated world behind"
    body = "\n".join(line for line in case.baseline.split("\n") if not PR2_MARK_LINE.match(line))  # the mark names numbers, not findings
    assert set(token.findall(body)) == set(case.live) | set(case.earlier)


# =========================================================================== PR 2's run directories (T103; S-4, ADR-050 D11 to D14)
# Six scenarios under pr2-runs/ (the generator's docstring lists them): four of provenance, for check-threat-model.py (D12), and the trees and report
# stages of one run, for assemble-report.py (D14). Every value that a scenario's expected-outcomes.json states is re-derived here from the committed
# files by a separate coding of the contracts, as T148's tests do for theirs, and each record, brief, table, plan, batch input and part is read back
# through the shipped validators. No check script and no assembler exists yet: T095 and T096, T108 and T109 are the first to run one on these files.
# What the committed copy cannot show is checked on a materialized copy (a real directory, built by gen.materialize): the digests that bind a plan hold
# only for the root they were built for. Every name here starts pr2r_ or PR2R_.
PR2R_NAMES = ("forms", "truncation", "reissue-mark", "reissue-no-mark", "trees", "report")
PR2R_PROVENANCE = PR2R_NAMES[:4]
PR2R_ROSTER_FILE = HERE.parents[1] / ".claude" / "skills" / "tachi-shared" / "references" / "agent-roster-shared.md"
PR2R_T148 = ("bc2e20d69ea8670a6ddfd2c4", 14, 469244)  # the digest, file count and size of chain-cap/ and id-reuse/, as T148 committed them
PR2R_BUILD = "run/tachi-build/"
PR2R_KEY_OF_PREFIX = {"S": "S", "T": "T", "R": "R", "I": "I", "D": "D", "E": "E", "AG": "AG", "AGP": "AG", "TE": "AG", "LLM": "LLM", "OI": "LLM", "MI": "LLM"}
PR2R_KEY_ORDER = ("S", "T", "R", "I", "D", "E", "AG", "LLM")
PR2R_REASONS = ("no_end_marker", "overflow_error", "agent_failed", "timed_out")


def pr2r_path(name: str, rel: str) -> str:
    return "pr2-runs/%s/%s" % (name, rel)


def pr2r_text(committed: dict, name: str, rel: str) -> str:
    return committed[pr2r_path(name, rel)].decode("utf-8")


def pr2r_json(committed: dict, name: str, rel: str):
    return json.loads(pr2r_text(committed, name, rel))


def pr2r_files_under(committed: dict, name: str, prefix: str) -> dict:
    """{file name below prefix: parsed JSON} for every file of a scenario under a directory prefix, in path order."""
    base = pr2r_path(name, prefix)
    return {path[len(base):]: json.loads(data.decode("utf-8")) for path, data in sorted(committed.items()) if path.startswith(base)}


def pr2r_strings(value):
    """Every string in a parsed JSON value, the keys of an object included."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from pr2r_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from pr2r_strings(item)


def pr2r_sha(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def pr2r_roster() -> list:
    """The Phase 2 roster table of agent-roster-shared.md: [(agent, dispatch key, the prefix it emits, the prefix Phase 3 files it under)]."""
    text = PR2R_ROSTER_FILE.read_text(encoding="utf-8")
    section = text.split("## Phase 2 Roster", 1)[1].split("## Stage and Helper Agents", 1)[0]
    rows = []
    for line in section.split("\n"):
        row = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if line.startswith("| `tachi-") and len(row) == 5:
            rows.append((row[0], row[1], row[3], row[3] if row[4] == chr(0x2014) else row[4]))  # an em dash in the Folds into column: no fold
    return rows


def pr2r_planned_set(table: dict) -> list:
    """D12 and item O-alpha's planned set: one dispatch for each roster agent whose key some component's row carries, with those components."""
    planned = []
    for agent, key, _, _ in pr2r_roster():
        scope = [row["component"] for row in table["rows"] if key in row["stride"] or key in row["ai"]]
        if scope:
            planned.append((agent, scope))
    return planned


def pr2r_derive(committed: dict, parsers, name: str) -> types.SimpleNamespace:
    """Everything a provenance scenario holds, read back with the shipped reference-set reader and no help from the generator."""
    canon = tachi_parts.canonical_finding_id
    reference = parsers.parse_reference_set(pr2r_text(committed, name, "run/threats.md"), name)
    base = None
    if pr2r_path(name, "baseline/threats.md") in committed:
        base = parsers.parse_reference_set(pr2r_text(committed, name, "baseline/threats.md"), name + " baseline")
    records = {r["dispatch_id"]: r for r in pr2r_files_under(committed, name, PR2R_BUILD + "records/").values()}
    briefs = {b["dispatch_id"]: b for b in pr2r_files_under(committed, name, PR2R_BUILD + "briefs/").values()}
    return types.SimpleNamespace(
        name=name, reference=reference, open={canon(r["id"]): r for r in reference["open"]}, resolved=[canon(r["id"]) for r in reference["resolved"]],
        base_open={canon(r["id"]) for r in base["open"]} if base else None, records=records, briefs=briefs,
        idmap=pr2r_json(committed, name, PR2R_BUILD + "idmap.json")["records"], inventory=pr2r_json(committed, name, PR2R_BUILD + "phase1/inventory.json"),
        table=pr2r_json(committed, name, PR2R_BUILD + "phase1/dispatch.json"), threats=pr2r_text(committed, name, "run/threats.md"))


def pr2r_attempt(records: dict, record: dict) -> int:
    attempt = 1
    while record["supersedes"] is not None:
        record, attempt = records[record["supersedes"]], attempt + 1
    return attempt


def pr2r_lineage_problems(records: dict, planned: list) -> list:
    """Item O-alpha's rules over the records alone: IDs, the planned set, supersession in both directions, a split and a repeat, three attempts at
    most, a reason and its count, and each planned (agent, component) pair in exactly one complete record of its lineage."""
    problems = []
    ids = sorted(records)
    if ids != ["dsp-%03d" % n for n in range(1, len(ids) + 1)]:
        problems.append("dispatch IDs are not consecutive from dsp-001")
    first = sorted((r for r in records.values() if r["origin"] == "planned"), key=lambda r: r["dispatch_id"])
    if [(r["agent_type"], r["scope"]["components"]) for r in first] != planned:
        problems.append("the planned records are not the planned set, in the roster's order")
    for r in records.values():
        name, live = r["dispatch_id"], r["status"] == "complete"
        if live != (r["reason"] is None) or live != r["end_marker"] or r["reason"] not in PR2R_REASONS + (None,):
            problems.append("%s: status, reason and end marker disagree" % name)
        if r["reason"] in ("agent_failed", "timed_out") and (r["count"] != 0 or r["local_ids"]):
            problems.append("%s: a record with no report lists findings" % name)
        if len(r["local_ids"]) != r["count"]:
            problems.append("%s: count and local_ids differ" % name)
        if r["status"] == "unrecovered":
            problems.append("%s: a lineage ends unrecovered" % name)
        if pr2r_attempt(records, r) > 3 or (r["status"] == "superseded" and pr2r_attempt(records, r) == 3):
            problems.append("%s: past three attempts" % name)
        if bool(r["superseded_by"]) != (r["status"] == "superseded"):
            problems.append("%s: superseded_by and status disagree" % name)
        for child in r["superseded_by"]:
            if child not in records or records[child]["supersedes"] != name or records[child]["agent_type"] != r["agent_type"]:
                problems.append("%s: a replacement does not name it" % name)
        if r["supersedes"] is not None and (r["supersedes"] not in records or records[r["supersedes"]]["status"] != "superseded"
                                            or name not in records[r["supersedes"]]["superseded_by"] or r["origin"] != "redispatch"):
            problems.append("%s: its parent does not name it" % name)
        if r["status"] == "superseded":
            scope, children = r["scope"]["components"], [records[c] for c in r["superseded_by"] if c in records]
            numbers = [int(c["dispatch_id"][4:]) for c in children]
            if pr2r_attempt(records, r) == 1 and len(scope) >= 2:  # the split: one replacement for each component, in scope order, on consecutive IDs
                if [c["scope"]["components"] for c in children] != [[x] for x in scope] or numbers != list(range(numbers[0], numbers[0] + len(scope))):
                    problems.append("%s: its replacements are not its split" % name)
            elif len(children) != 1 or children[0]["scope"]["components"] != scope:  # the repeat
                problems.append("%s: its replacement is not its repeat" % name)
    for agent, scope in planned:
        for component in scope:
            covering = [r for r in records.values() if r["agent_type"] == agent and r["status"] == "complete" and component in r["scope"]["components"]]
            if len(covering) != 1:
                problems.append("%s on %s is in %d complete records" % (agent, component, len(covering)))
    return problems


def pr2r_classify(ns: types.SimpleNamespace, roster: list) -> dict:
    """FR-N4.5 for every open finding: the classes that hold (D12: 1 a kept disposition in a live record of an agent allowed the prefix, 2 a baseline
    carry-forward, 3 a pattern finding that no disposition names), and what FR-N4.6 needs: where each disposition points."""
    canon = tachi_parts.canonical_finding_id
    allowed = {agent: {emits, files} for agent, _, emits, files in roster}
    kept, named = {}, {}
    for record_id, dispositions in ns.idmap.items():
        for local, disposition in zip(ns.records[record_id]["local_ids"], dispositions):
            target = canon(disposition.lstrip("=~>"))
            named.setdefault(target, []).append((record_id, local, disposition))
            if disposition[0] not in "=~>":
                kept.setdefault(target, []).append((record_id, local))
    out = {}
    for finding_id, row in ns.open.items():
        prefix, classes = finding_id.partition("-")[0], []
        if len(kept.get(finding_id, ())) == 1 and row["delta_status"] == "NEW" and prefix in allowed[ns.records[kept[finding_id][0][0]]["agent_type"]]:
            classes.append(1)
        if row["delta_status"] in ("UNCHANGED", "UPDATED") and ns.base_open is not None and finding_id in ns.base_open and finding_id not in kept:
            classes.append(2)
        if prefix == "AGP" and row["delta_status"] == "NEW" and finding_id not in named:
            classes.append(3)
        out[finding_id] = {"classes": classes, "kept": kept.get(finding_id)}
    return out


@pytest.fixture(scope="module")
def pr2r_docs(committed) -> dict:
    return {name: pr2r_json(committed, name, "expected-outcomes.json") for name in PR2R_NAMES}


@pytest.fixture(scope="module")
def pr2r_runs(committed, pr2_parsers) -> dict:
    return {name: pr2r_derive(committed, pr2_parsers, name) for name in PR2R_PROVENANCE}


# --------------------------------------------------------------------------- structure and hygiene
def test_pr2r_every_scenario_is_committed_with_its_files_and_an_outcome_file_that_points_at_them(committed, pr2r_docs):
    assert {path.split("/")[1] for path in committed if path.startswith("pr2-runs/")} == set(PR2R_NAMES)
    for name in PR2R_NAMES:
        doc = pr2r_docs[name]
        assert doc["schema"] == "tachi.fixture-expected/1" and doc["variant"] == "pr2-runs" and doc["scenario"] == name
        assert doc["stage"] and doc["summary"] and len(doc["notes"]) >= 3 and doc["run"]["date"] == "2026-11-23"
        tops = {path.split("/")[2] for path in committed if path.startswith("pr2-runs/%s/" % name)}
        assert tops == ({"run", "expected-outcomes.json"} if name == "truncation" else {"run", "baseline", "expected-outcomes.json"}), (name, tops)
        for rel in filter(None, (doc["run"].get(key) for key in ("threats", "baseline", "architecture"))):
            assert pr2r_path(name, rel) in committed, "%s names %s, which is not committed" % (name, rel)
    assert pr2r_docs["truncation"]["run"]["baseline"] is None


def test_pr2r_the_committed_copy_names_one_placeholder_root_and_no_dotted_build_directory(committed):
    """Each absolute path is under the placeholder root. tachi-build/ is written without its dot, because .gitignore excludes .tachi-build/."""
    checked = 0
    for path, data in committed.items():
        if not path.startswith("pr2-runs/"):
            continue
        assert ".tachi-build" not in path.split("/"), path
        if path.endswith(".json"):
            for text in pr2r_strings(json.loads(data.decode("utf-8"))):
                if text.startswith("/"):
                    assert text.startswith(gen.PR2R_ROOT + "/"), "%s holds an absolute path outside the placeholder root: %s" % (path, text)
                    checked += 1
    assert gen.PR2R_ROOT == "/synthetic-case" and checked > 250, "the records, briefs, plans and batch inputs carry the root"


def test_pr2r_t148s_cases_are_byte_for_byte_what_t148_committed(committed):
    """T103 adds beside chain-cap/ and id-reuse/ and never moves a byte of them (W1's digest, over those two directories)."""
    import hashlib
    entries = sorted((p for p in committed if p.split("/")[0] in ("chain-cap", "id-reuse")), key=_walk_order)
    outer, total = hashlib.sha256(), 0
    for path in entries:
        outer.update(path.encode("utf-8") + b"\0" + hashlib.sha256(committed[path]).digest())
        total += len(committed[path])
    assert (outer.hexdigest()[:24], len(entries), total) == PR2R_T148


# --------------------------------------------------------------------------- the generator's tables are the contracts'
def test_pr2r_the_roster_and_its_fold_table_are_the_shared_references(committed):
    roster = pr2r_roster()
    assert len(roster) == 14 and [row[0] for row in roster] == list(tachi_parts.ROSTER)
    assert [(a, k, e, f) for a, k, e, f in gen.PR2R_ROSTER] == roster, "the generator's roster differs from agent-roster-shared.md"
    folds = {agent: files for agent, _, emits, files in roster if files != emits}
    assert folds == {"tachi-human-trust-exploitation": "AG", "tachi-output-integrity": "LLM", "tachi-misinformation": "LLM"}, (
        "#356's fold table: OI and MI into LLM, TE into AG")


# --------------------------------------------------------------------------- the files read back through the shipped validators
@pytest.mark.parametrize("name", PR2R_PROVENANCE)
def test_pr2r_every_record_brief_and_table_passes_its_validator_and_agrees_with_its_pair(committed, pr2r_runs, name):
    ns = pr2r_runs[name]
    records = pr2r_files_under(committed, name, PR2R_BUILD + "records/")
    briefs = pr2r_files_under(committed, name, PR2R_BUILD + "briefs/")
    assert records and sorted(records) == sorted(briefs), "a record and its brief come as a pair"
    tachi_parts.validate_idmap(pr2r_json(committed, name, PR2R_BUILD + "idmap.json"))
    tachi_parts.validate_phase1_inventory(ns.inventory)
    tachi_parts.validate_phase1_dispatch(ns.table)
    snapshot = gen.PR2R_ROOT + "/run/architecture.md"
    assert pr2r_path(name, "run/architecture.md") in committed
    build = gen.PR2R_ROOT + "/run/.tachi-build/"
    fold = lambda text: " ".join(text.casefold().split())  # noqa: E731
    known = {fold(c["name"]) for c in ns.inventory["components"]}
    for file_name, record in records.items():
        tachi_parts.validate_dispatch_record(record)
        brief = briefs[file_name]
        tachi_parts.validate_brief(brief)
        assert file_name == record["dispatch_id"] + ".json" and brief["dispatch_id"] == record["dispatch_id"] and brief["agent_type"] == record["agent_type"]
        assert record["brief"] == build + "briefs/" + file_name and record["prompt"] == "Read and follow the brief at %s." % record["brief"]
        assert brief["targets"] == record["scope"]["components"] and {fold(c) for c in brief["targets"]} <= known
        assert brief["inputs"] == {"architecture": snapshot, "inventory": build + "phase1/inventory.json", "dispatch_table": build + "phase1/dispatch.json"}
        assert set(brief) == {"schema", "dispatch_id", "agent_type", "targets", "inputs", "baseline_focus"}
    assert [row["component"] for row in ns.table["rows"]] == [c["name"] for c in ns.inventory["components"]], "one dispatch row for each component, in order"
    listed = [name for zone in ns.inventory["trust_zones"] for name in zone["components"]]
    assert sorted(listed) == sorted(c["name"] for c in ns.inventory["components"]), "every component is in one zone"
    flows = {fold(f["source"]) for f in ns.inventory["data_flows"]} | {fold(f["destination"]) for f in ns.inventory["data_flows"]}
    assert flows <= known and len(ns.inventory["data_flows"]) >= 5


@pytest.mark.parametrize("name", PR2R_PROVENANCE)
def test_pr2r_the_phase_1_inventory_agrees_with_the_threat_model(pr2r_runs, committed, name):
    """Section 1's components, with their layers, are the inventory's: the dispatch table and the chain script read the one, the check the other."""
    ns = pr2r_runs[name]
    rows = {row["Component"]: row for row in table_after(ns.threats, "### Components")}
    assert set(rows) == {c["name"] for c in ns.inventory["components"]}
    for component in ns.inventory["components"]:
        row = rows[component["name"]]
        assert row["Type"] == component["dfd_type"] and row["MAESTRO Layer"].startswith(component["maestro_layer"] + " ")
    zones = {row["Zone"]: [c.strip() for c in row["Components"].split(",")] for row in table_after(ns.threats, "### Trust Zones")}
    assert zones == {zone["name"]: zone["components"] for zone in ns.inventory["trust_zones"]}


# --------------------------------------------------------------------------- provenance (FR-N4.5, FR-N4.6, P-11)
@pytest.mark.parametrize("name", PR2R_PROVENANCE)
def test_pr2r_the_planned_set_and_the_lineages_follow_the_rules_of_item_o_alpha(pr2r_runs, pr2r_docs, name):
    ns, expected = pr2r_runs[name], pr2r_docs[name]["provenance"]
    planned = pr2r_planned_set(ns.table)
    assert 1 <= len(planned) <= 14
    assert pr2r_lineage_problems(ns.records, planned) == []
    assert [(p["agent_type"], p["scope"]) for p in expected["planned"]] == planned
    assert [r["dispatch_id"] for r in expected["records"]] == sorted(ns.records), "every record is listed, in ID order"
    for entry in expected["records"]:
        record = ns.records[entry["dispatch_id"]]
        assert {k: record[k] for k in ("agent_type", "origin", "status", "reason", "supersedes", "superseded_by", "count")} == {
            k: entry[k] for k in ("agent_type", "origin", "status", "reason", "supersedes", "superseded_by", "count")}
        assert entry["attempt"] == pr2r_attempt(ns.records, record)
    live = {r for r, record in ns.records.items() if record["status"] == "complete"}
    assert set(ns.idmap) == live, "the ID map's keys are exactly the complete records (FR-N4.6)"
    assert all(len(ns.idmap[r]) == ns.records[r]["count"] for r in live)
    lineage = list(ns.records.values())  # no coverage-gap record in any scenario, so every record is in a lineage
    planned_n, retried = sum(r["origin"] == "planned" for r in lineage), sum(r["origin"] == "redispatch" for r in lineage)
    assert expected["batches"] == {"planned": planned_n, "dispatched": planned_n + retried, "done": len(live), "retried": retried,
                                   "split": sum(r["status"] == "superseded" for r in lineage), "exhausted": 0}


@pytest.mark.parametrize("name", PR2R_PROVENANCE)
def test_pr2r_every_finding_has_exactly_one_provenance_entry_and_every_disposition_has_a_target(pr2r_runs, pr2r_docs, name):
    ns, expected = pr2r_runs[name], pr2r_docs[name]["provenance"]
    roster = pr2r_roster()
    verdict = pr2r_classify(ns, roster)
    assert sorted(verdict) == sorted(ns.open) and all(len(v["classes"]) == 1 for v in verdict.values()), {
        fid: v["classes"] for fid, v in verdict.items() if len(v["classes"]) != 1}
    canon = tachi_parts.canonical_finding_id  # the files spell AGP-01, and the readers compare AGP-1
    assert {fid: v["classes"][0] for fid, v in verdict.items()} == {canon(fid): e["class"] for fid, e in expected["findings"].items()}
    assert sorted(canon(fid) for fid in expected["findings"]) == sorted(ns.open), "an object's keys come out sorted, so its order says nothing"
    assert [canon(fid) for fid in expected["open_ids"]] == list(ns.open), "S-2 order, as the reference-set reader gives it"
    assert [canon(fid) for fid in expected["resolved_ids"]] == ns.resolved
    carried = {fid for fid, row in ns.open.items() if row["delta_status"] != "NEW"}
    for record_id, dispositions in ns.idmap.items():
        for disposition in dispositions:
            target = tachi_parts.canonical_finding_id(disposition.lstrip("=~>"))
            assert target in ns.open, "a kept or merged target is in the reference set, and so is a matched one"
            if disposition[0] in "=~":
                assert target in carried, "a matched target is a carried finding"
    counts = {"open": len(ns.open), "resolved": len(ns.resolved), "recorded": 0, "carried": 0, "rule": 0, "renumbered": 0, "folded": 0}
    emits = {agent: e for agent, _, e, _ in roster}
    for finding_id, v in verdict.items():
        counts[("recorded", "carried", "rule")[v["classes"][0] - 1]] += 1
        if v["classes"][0] == 1:  # the check's two counts: a fold re-prefixes the ID, a renumbering keeps its prefix and changes the number
            (record_id, local), prefix = v["kept"][0], finding_id.partition("-")[0]
            if emits[ns.records[record_id]["agent_type"]] != prefix:
                counts["folded"] += 1
            elif local != finding_id:
                counts["renumbered"] += 1
    assert counts == {k: v for k, v in expected["counts"].items() if k != "reused-id"}


# --------------------------------------------------------------------------- the scenarios' own content
def test_pr2r_forms_holds_each_form_of_provenance_once_or_more(committed, pr2r_runs, pr2r_docs):
    ns, roster = pr2r_runs["forms"], pr2r_roster()
    held = {p[len("pr2-runs/forms/"):]: d for p, d in committed.items() if p.startswith("pr2-runs/forms/baseline/attack-trees/")}
    assert held and held == {p[len("pr2-runs/trees/"):]: d for p, d in committed.items() if p.startswith("pr2-runs/trees/baseline/attack-trees/")}, (
        "the forms baseline holds the trees scenario's baseline trees, so one run can start a whole offline pass")
    verdict = pr2r_classify(ns, roster)
    emits = {agent: e for agent, _, e, _ in roster}
    kept_as_is, renumbered, folded = [], [], []
    for finding_id, v in verdict.items():
        if v["classes"] == [1]:
            (record_id, local), agent = v["kept"][0], ns.records[v["kept"][0][0]]["agent_type"]
            (folded if emits[agent] != finding_id.partition("-")[0] else kept_as_is if local == finding_id else renumbered).append((finding_id, agent))
    assert kept_as_is and renumbered, "a finding that its agent numbered as it is final, and ones that it did not"
    assert {agent for _, agent in folded} == {"tachi-output-integrity", "tachi-misinformation", "tachi-human-trust-exploitation"}, "each fold of #356's table"
    assert {fid.partition("-")[0] for fid, _ in folded} == {"LLM", "AG"}
    forms = {d[0] for dispositions in ns.idmap.values() for d in dispositions if d[0] in "=~>"}
    assert forms == {"=", "~", ">"}, "matched exactly, matched by similarity and merged"
    carried_status = {row["delta_status"] for fid, row in ns.open.items() if verdict[fid]["classes"] == [2]}
    assert carried_status == {"UNCHANGED", "UPDATED"}
    assert [fid for fid, v in verdict.items() if v["classes"] == [3]] == ["AGP-1"], "the pattern finding (AGP-01 in the file) is named by no disposition"
    # a local ID that is another finding's final ID is the case a check must not confuse
    assert any(local in ns.open and verdict[local]["classes"] == [2] for r in ns.records.values() for local in r["local_ids"])
    covered = {}
    for fid, row in ns.open.items():
        if row["delta_status"] != "NEW":
            covered.setdefault(row["component"], set()).add(PR2R_KEY_OF_PREFIX[fid.partition("-")[0]])
    for brief in ns.briefs.values():
        assert brief["baseline_focus"] is not None, "a baseline run"
        assert [(e["component"], e["covered"]) for e in brief["baseline_focus"]] == [
            (c, [k for k in PR2R_KEY_ORDER if k in covered.get(c, ())]) for c in brief["targets"]]


def test_pr2r_truncation_is_a_stateless_run_with_a_split_a_repeat_and_all_four_reasons(pr2r_runs, committed, pr2_parsers):
    ns = pr2r_runs["truncation"]
    assert ns.base_open is None and pr2r_path("truncation", "baseline/threats.md") not in committed
    assert all(brief["baseline_focus"] is None for brief in ns.briefs.values()), "a stateless run's briefs"
    parsed = pr2_parsers.parse_baseline_frontmatter(ns.threats)
    assert parsed["has_baseline"] is False and {row["delta_status"] for row in ns.reference["open"]} == {"NEW"} and not ns.reference["resolved"]
    assert "## 4c." not in ns.threats and "## 8. Delta Summary" not in ns.threats
    cut = [r for r in ns.records.values() if r["status"] == "superseded"]
    assert {r["reason"] for r in cut} == set(PR2R_REASONS)
    assert {pr2r_attempt(ns.records, r) for r in cut} == {1, 2}, "a first attempt that is split and a replacement that is repeated"
    assert any(len(r["superseded_by"]) >= 2 for r in cut) and any(len(r["superseded_by"]) == 1 for r in cut)
    assert any(r["count"] > 0 for r in cut if r["reason"] in ("no_end_marker", "overflow_error")), "a cut report that listed findings"
    assert max(pr2r_attempt(ns.records, r) for r in ns.records.values()) == 3
    for record in cut:  # a superseded record's findings leave the completeness set: nothing of it is in the ID map
        assert record["dispatch_id"] not in ns.idmap
    verdict = pr2r_classify(ns, pr2r_roster())
    assert {v["classes"][0] for v in verdict.values()} == {1, 3}
    lost = {a: [c for r in ns.records.values() if r["agent_type"] == a and r["status"] == "complete" for c in r["scope"]["components"]]
            for a in ("tachi-agent-autonomy", "tachi-human-trust-exploitation")}
    assert all(len(set(v)) == len(v) == 4 for v in lost.values()), "the four components of each cut-short agent are covered, once"


@pytest.mark.parametrize("name,scenario", [("reissue-mark", "id-reuse/pr2"), ("reissue-no-mark", "id-reuse/pr2-no-mark")])
def test_pr2r_the_reissue_scenarios_are_t148s_runs_with_records_that_make_their_provenance_whole(committed, pr2r_runs, pr2r_docs, pr2_docs, name, scenario):
    ns = pr2r_runs[name]
    for part in ("run", "baseline"):
        assert committed[pr2r_path(name, part + "/threats.md")] == committed["%s/%s/threats.md" % (scenario, part)], "T148's own file, byte for byte"
    verdict = pr2r_classify(ns, pr2r_roster())
    assert all(len(v["classes"]) == 1 for v in verdict.values())
    case = pr2_read_case(committed, scenario)
    recorded = sorted((fid for fid, v in verdict.items() if v["classes"] == [1]), key=pr2_s2)
    assert recorded == sorted(case.new, key=pr2_s2), "a record keeps each NEW finding, and nothing else is kept"
    flagged = pr2r_docs[name]["provenance"]["check"]
    assert flagged["reissued"] == pr2_docs[scenario]["reissue"]["flagged"], "the findings that ruling B's check reports are T148's"
    assert (flagged["exit_code"], flagged["status"], flagged["warnings"]) == (5, "warn", ["id:reissued"])
    assert pr2r_docs[name]["provenance"]["counts"]["reused-id"] == len(flagged["reissued"])
    assert pr2r_docs[name]["provenance"]["counts"]["carried"] == len(ns.open) - len(case.new), "every other finding is carried"


# --------------------------------------------------------------------------- the readers above are not vacuous: each break they name is caught
def pr2r_copy(ns: types.SimpleNamespace) -> types.SimpleNamespace:
    import copy
    return types.SimpleNamespace(**{key: copy.deepcopy(value) for key, value in vars(ns).items()})


@pytest.mark.parametrize("label,mutate", [
    ("a planned record is gone", lambda r: r.pop("dsp-003")),
    ("a replacement does not name its parent", lambda r: r["dsp-015"].update(supersedes=None)),
    ("a parent leaves a replacement out", lambda r: r["dsp-007"].update(superseded_by=r["dsp-007"]["superseded_by"][:-1])),
    ("a split is not one replacement for each component", lambda r: r["dsp-018"].update(scope={"components": ["tool-server-1", "worker-2"]})),
    ("a repeat covers another scope", lambda r: r["dsp-023"].update(scope={"components": ["worker-2"]})),
    ("a lineage ends unrecovered", lambda r: r["dsp-024"].update(status="unrecovered", end_marker=False, reason="no_end_marker")),
    ("a fourth attempt", lambda r: (r["dsp-023"].update(status="superseded", end_marker=False, reason="no_end_marker", superseded_by=["dsp-025"]),
                                    r.update({"dsp-025": dict(r["dsp-023"], dispatch_id="dsp-025", supersedes="dsp-023", superseded_by=[], status="complete",
                                                              end_marker=True, reason=None)}))),
    ("a record with no report lists a finding", lambda r: r["dsp-016"].update(count=1, local_ids=["AG-1"])),
    ("a reason outside the four", lambda r: r["dsp-007"].update(reason="other")),
    ("a complete record with a reason", lambda r: r["dsp-001"].update(reason="timed_out")),
    ("an ID is skipped", lambda r: r.update({"dsp-030": dict(r.pop("dsp-024"), dispatch_id="dsp-030")})),
    ("an agent is dispatched twice", lambda r: r["dsp-002"].update(agent_type="tachi-spoofing")),
])
def test_pr2r_the_lineage_rules_catch_each_way_that_a_set_of_records_can_break(pr2r_runs, label, mutate):
    ns = pr2r_copy(pr2r_runs["truncation"])
    planned = pr2r_planned_set(ns.table)
    assert pr2r_lineage_problems(ns.records, planned) == []
    mutate(ns.records)
    assert pr2r_lineage_problems(ns.records, planned), "the rules did not catch: %s" % label


@pytest.mark.parametrize("label,mutate", [
    ("a NEW finding that no disposition keeps", lambda ns: ns.idmap["dsp-001"].remove("S-5")),
    ("a NEW finding that two records keep", lambda ns: ns.idmap["dsp-003"].append("S-5") or ns.records["dsp-003"].update(count=1, local_ids=["R-1"])),
    ("a kept finding in a record of an agent that is not allowed its prefix", lambda ns: ns.records["dsp-001"].update(agent_type="tachi-tampering")),
    ("a pattern finding that a disposition names", lambda ns: ns.idmap["dsp-003"].append("=AGP-01") or ns.records["dsp-003"].update(count=1, local_ids=["R-1"])),
])
def test_pr2r_the_classification_catches_each_way_that_a_finding_can_lose_or_double_its_provenance(pr2r_runs, label, mutate):
    ns = pr2r_copy(pr2r_runs["forms"])
    roster = pr2r_roster()
    assert all(len(v["classes"]) == 1 for v in pr2r_classify(ns, roster).values())
    mutate(ns)
    assert any(len(v["classes"]) != 1 for v in pr2r_classify(ns, roster).values()), "the classification did not catch: %s" % label


def test_pr2r_every_json_document_is_within_the_size_cap_of_its_schema(committed):
    checked = 0
    for path, data in committed.items():
        if path.startswith("pr2-runs/") and path.endswith(".json") and "/expected-outcomes.json" not in path and not path.endswith("/.manifest.json"):
            document = json.loads(data.decode("utf-8"))  # the merged tree manifest is schema 1.0 and has no cap of its own
            if "/parts/" in path:
                assert len(data) <= tachi_parts.MAX_PART_BYTES, path
            elif document.get("schema") in tachi_parts.MAX_DOCUMENT_BYTES:
                assert len(data) <= tachi_parts.MAX_DOCUMENT_BYTES[document["schema"]], path
            else:
                raise AssertionError("%s names no schema that tachi_parts caps" % path)
            checked += 1
    assert checked > 150


def test_pr2r_a_regeneration_writes_the_committed_scenarios_byte_for_byte(regen, committed):
    """The whole-tree and per-part tests above cover this; the point here is the placeholder root: the committed copy is the build for gen.PR2R_ROOT."""
    built = {"pr2-runs/%s/%s" % (name, rel): text for name in gen.PR2R_SCENARIOS for rel, text in gen.pr2r_scenario_files(name, gen.PR2R_ROOT).items()}
    assert sorted(built) == sorted(p for p in committed if p.startswith("pr2-runs/")) == sorted(p for p in regen if p.startswith("pr2-runs/"))
    assert all(gen._canonical_text(text) == committed[path] for path, text in built.items())


# --------------------------------------------------------------------------- the trees stage (D14, S1P-A43: Rule 2 and Rule 3)
def pr2r_stage_dir(committed: dict, name: str, stage: str) -> types.SimpleNamespace:
    pointer = pr2r_json(committed, name, PR2R_BUILD + "%s/current.json" % stage)
    base = PR2R_BUILD + "%s/%s/" % (stage, pointer["plan_id"])
    return types.SimpleNamespace(
        plan_id=pointer["plan_id"], base=base, pointer=pointer, plan=pr2r_json(committed, name, base + "plan.json"),
        plan_bytes=committed[pr2r_path(name, base + "plan.json")], inputs=pr2r_files_under(committed, name, base + "inputs/"),
        parts=pr2r_files_under(committed, name, base + "parts/"))


def pr2r_one_mermaid_block(text: str) -> bool:
    """D14: one fenced code block, and it is a Mermaid block."""
    lines = text.split("\n")
    fences = [i for i, line in enumerate(lines) if line.startswith("```")]
    return len(fences) == 2 and lines[fences[0]] == "```mermaid" and lines[fences[1]] == "```" and fences[1] - fences[0] > 1


def pr2r_rule2(committed: dict, parsers, name: str, size: int = 12) -> types.SimpleNamespace:
    """The trees stage as the contracts plan it, from the run's threats.md and the baseline's attack-trees/ listing alone. ``size`` is the planner's
    batch size for the stage, which the one test that reads ``tachi-stage.py`` passes (12 is the contracts' figure, S1P-A57)."""
    canon = tachi_parts.canonical_finding_id
    stage = pr2r_stage_dir(committed, name, "trees")
    reference = parsers.parse_reference_set(pr2r_text(committed, name, "run/threats.md"), name)
    rows = {canon(r["id"]): r for r in reference["open"]}
    chosen = sorted((f for f, r in rows.items() if r["risk_level"] in ("Critical", "High")), key=tachi_parts.finding_sort_key)
    listing = pr2r_path(name, "baseline/attack-trees/")
    held = {canon(path[len(listing):].rpartition("-attack-tree.md")[0].upper()) for path in committed if path.startswith(listing) and path.endswith(".md")}
    delta = any(r["delta_status"] in ("NEW", "UPDATED") for r in rows.values()) or bool(reference["resolved"])
    planned = {}
    for finding_id in chosen:
        status = rows[finding_id]["delta_status"]
        planned[finding_id] = "regenerated" if status == "UNCHANGED" and finding_id in held else "generated_fresh"  # Rule 2 (S1P-A43)
    return types.SimpleNamespace(stage=stage, reference=reference, rows=rows, chosen=chosen, held=held, rule="Rule 2" if delta else "Rule 1", planned=planned,
                                 chunks=[chosen[i:i + size] for i in range(0, len(chosen), size)])


def test_pr2r_the_trees_plan_follows_rule_2_and_its_batch_inputs_and_parts_validate(committed, pr2_parsers, pr2r_docs, stage_sizes):
    assert stage_sizes["trees"] == 12 == gen.PR2R_TREES_BATCH, "the planner's own constant for the stage: the fixture's plan holds what plan would write"
    t = pr2r_rule2(committed, pr2_parsers, "trees", stage_sizes["trees"])
    plan, expected = t.stage.plan, pr2r_docs["trees"]["trees"]
    tachi_parts.validate_plan(plan)
    tachi_parts.validate_pointer(t.stage.pointer)
    assert t.rule == "Rule 2" == plan["params"]["rule_applied"] and plan["stage"] == "trees" and plan["agent_type"] == "tachi-attack-tree-delta"
    assert plan["batch_size"] == 12 and plan["unit_count"] == len(t.chosen) == expected["unit_count"] and plan["preimage"] == {} and plan["out_snapshot"] is None
    assert plan["params"]["reference_digest"] == tachi_parts.reference_digest(t.reference) == expected["reference_digest"]
    assert plan["params"]["scoring_date"] == "2026-11-23" and plan["refs"] == {"baseline_dir": gen.PR2R_ROOT + "/baseline"}
    assert plan["retry_budget"] == {"limit": 2 * len(t.chunks), "used": 0}
    assert [b["finding_ids"] for b in plan["batches"]] == t.chunks and len(t.chunks) >= 2, "S-2 order, 12 to a batch, and more than one batch"
    assert len(t.chosen) > 12 and {len(t.chunks[0]), len(t.chunks[-1])} == {12, len(t.chosen) - 12}
    out = gen.PR2R_ROOT + "/run"
    threats = committed[pr2r_path("trees", "run/threats.md")]
    assert plan["inputs"] == {"threats": {"path": out + "/threats.md", "sha256": pr2r_sha(threats), "bytes": len(threats)}}
    for entry, chunk in zip(plan["batches"], t.chunks):
        batch_id = entry["batch_id"]
        raw = committed[pr2r_path("trees", t.stage.base + "inputs/%s.json" % batch_id)]
        assert entry["input_sha256"] == pr2r_sha(raw) and (entry["parent"], entry["attempt"], entry["state"]) == (None, 1, "done")
        batch = tachi_parts.validate_batch_input(t.stage.inputs[batch_id + ".json"])
        base = "%s/.tachi-build/trees/%s" % (out, t.stage.plan_id)
        assert batch["finding_ids"] == chunk and batch["attempt"] == 1 and batch["part_path"] == "%s/parts/%s.a1.json" % (base, batch_id)
        assert batch["tree_paths"] == {f: "%s/trees/%s-attack-tree.md" % (base, f.lower()) for f in chunk}
        assert [(u["finding_id"], u["delta_status"], u["action"]) for u in batch["units"]] == [
            (f, t.rows[f]["delta_status"], t.planned[f]) for f in chunk], "the planner's units: Rule 2 plans regenerated for an UNCHANGED finding whose baseline has a tree"
        part = t.stage.parts[batch_id + ".a1.json"]
        result = tachi_parts.classify_part(part, t.stage.plan_id, batch_id, "trees", "tachi-attack-tree-delta", chunk, batch["units"])
        assert result.state == "done", (batch_id, result.detail)
        for item, unit in zip(result.part["items"], batch["units"]):
            if unit["action"] == "regenerated":  # Rule 3's decision is the agent's: the one value in which a part may differ from its batch input
                assert item["action"] in ("regenerated", "carried_forward") and 0 <= item["similarity_score"] <= 1
            else:
                assert item["action"] == unit["action"] and "similarity_score" not in item


def test_pr2r_the_trees_scenario_has_every_unit_kind_and_its_files_follow_the_plan(committed, pr2_parsers, pr2r_docs):
    t = pr2r_rule2(committed, pr2_parsers, "trees")
    expected = pr2r_docs["trees"]["trees"]
    items = {tachi_parts.canonical_finding_id(i["finding_id"]): i for part in t.stage.parts.values() for i in part["items"]}
    kinds = {(t.rows[f]["delta_status"], t.planned[f], items[f]["action"]) for f in t.chosen}
    assert kinds == {("NEW", "generated_fresh", "generated_fresh"), ("UPDATED", "generated_fresh", "generated_fresh"),
                     ("UNCHANGED", "generated_fresh", "generated_fresh"),  # the isolated fallback: a carried finding with no baseline tree
                     ("UNCHANGED", "regenerated", "carried_forward"), ("UNCHANGED", "regenerated", "regenerated")}, kinds
    assert t.held and any(t.rows[f]["delta_status"] == "UPDATED" and f in t.held for f in t.chosen), "an UPDATED finding's baseline tree is not carried"
    assert [f for f in t.chosen if t.rows[f]["delta_status"] == "UNCHANGED" and f not in t.held] == expected["unchanged_without_baseline_tree"]
    sources = {}
    for finding_id in t.chosen:
        stem = t.rows[finding_id]["id"].lower()  # the file spelling: agp-01 for AGP-01
        fresh = committed[pr2r_path("trees", t.stage.base + "trees/%s-attack-tree.md" % stem)].decode("utf-8")
        assert pr2r_one_mermaid_block(fresh) and fresh.startswith("# %s: " % t.rows[finding_id]["id"]), finding_id
        assert tachi_parts.forbidden_character(fresh) is None
        sources[finding_id] = fresh
        held_path = pr2r_path("trees", "baseline/attack-trees/%s-attack-tree.md" % stem)
        assert (held_path in committed) == (finding_id in t.held)
        if finding_id in t.held:  # the baseline's file differs from the fresh one by one line, so a copy shows which it came from
            base_text = committed[held_path].decode("utf-8")
            assert pr2r_one_mermaid_block(base_text) and base_text.replace("\n\n" + gen.PR2R_BASELINE_TREE_NOTE + "\n\n", "\n\n", 1) == fresh != base_text
    assert sorted(path for path in committed if path.startswith(pr2r_path("trees", t.stage.base + "trees/"))) == sorted(
        pr2r_path("trees", t.stage.base + "trees/%s-attack-tree.md" % t.rows[f]["id"].lower()) for f in t.chosen), "a tree for every unit and no other"
    # the merge (D14; threat-model-records.md): Critical first, then High, each in S-2 order; the action is the part's, the score only a Rule 3 unit's
    order = sorted(t.chosen, key=lambda f: (t.rows[f]["risk_level"] != "Critical", tachi_parts.finding_sort_key(f)))
    entries = []
    for f in order:
        entry = {"finding_id": t.rows[f]["id"], "delta_status": t.rows[f]["delta_status"], "action": items[f]["action"]}
        if "similarity_score" in items[f]:
            entry["similarity_score"] = items[f]["similarity_score"]
        entry["file_path"] = "attack-trees/%s-attack-tree.md" % t.rows[f]["id"].lower()
        entries.append(entry)
    actions = [e["action"] for e in entries]
    merged = {"schema_version": "1.0", "rule_applied": "Rule 2", "attack_tree_count": len(entries), "trees": entries,
              "summary": {"fresh": actions.count("generated_fresh"), "carried_forward": actions.count("carried_forward"), "regenerated": actions.count("regenerated")}}
    assert merged == expected["merged_manifest"] and sum(merged["summary"].values()) == merged["attack_tree_count"]
    assert expected["stage_record_counts"] == {"units": len(t.chosen), "carried": merged["summary"]["carried_forward"], "rendered": len(entries)}
    assert {u["finding_id"]: u["final_tree_comes_from"] for u in expected["units"]} == {
        t.rows[f]["id"]: "baseline" if items[f]["action"] == "carried_forward" else "plan" for f in t.chosen}
    assert expected["plan_digest"] == pr2r_sha(t.stage.plan_bytes), "plan_digest is what plan prints: the SHA-256 of plan.json"


# --------------------------------------------------------------------------- the report stage (D14, items O-beta and O-gamma)
def test_pr2r_the_report_plan_pins_the_trees_plan_the_manifest_and_the_reference_set(committed, pr2_parsers, pr2r_docs):
    rep = pr2r_stage_dir(committed, "report", "report")
    trees = pr2r_stage_dir(committed, "report", "trees")
    reference = pr2_parsers.parse_reference_set(pr2r_text(committed, "report", "run/threats.md"), "report")
    expected = pr2r_docs["report"]["report"]
    plan = tachi_parts.validate_plan(rep.plan)
    tachi_parts.validate_plan(trees.plan)
    assert plan["stage"] == "report" and plan["agent_type"] == "tachi-threat-report" and plan["batch_size"] is None and plan["refs"] == {}
    assert plan["preimage"] == {} and plan["out_snapshot"] is None and set(plan["inputs"]) == {"threats", "trees_plan", "tree_manifest"}
    assert plan["params"] == {"scoring_date": "2026-11-23", "reference_digest": tachi_parts.reference_digest(reference), "trees_plan_id": trees.plan_id}
    assert trees.plan["params"]["reference_digest"] == plan["params"]["reference_digest"], "both plans hold the one reference set's digest"
    out = gen.PR2R_ROOT + "/run"
    for name, path, rel in (("threats", out + "/threats.md", "run/threats.md"), ("tree_manifest", out + "/attack-trees/.manifest.json", "run/attack-trees/.manifest.json"),
                            ("trees_plan", "%s/.tachi-build/trees/%s/plan.json" % (out, trees.plan_id), "run/tachi-build/trees/%s/plan.json" % trees.plan_id)):
        data = committed[pr2r_path("report", rel)]
        assert plan["inputs"][name] == {"path": path, "sha256": pr2r_sha(data), "bytes": len(data)}, name
    assert pr2r_sha(trees.plan_bytes) == expected["trees_plan_digest"] and pr2r_sha(rep.plan_bytes) == expected["plan_digest"]
    assert plan["unit_count"] == expected["unit_count"] == sum(len(b["units"]) for b in rep.inputs.values())
    assert "attack_chains" not in plan["inputs"], "threats.md holds no outcome record, so no attack_chains part is planned (S1P-A58)"
    assert not re.search(r"(?m)^\*\*Attack chain outcome\*\*: ", pr2r_text(committed, "report", "run/threats.md")), "the outcome record's absence, read by its label alone"


def test_pr2r_the_report_plan_plans_the_sections_the_contract_gives_and_every_part_validates(committed, pr2_parsers, pr2r_docs):
    canon = tachi_parts.canonical_finding_id
    rep = pr2r_stage_dir(committed, "report", "report")
    threats = pr2r_text(committed, "report", "run/threats.md")
    reference = pr2_parsers.parse_reference_set(threats, "report")
    rows = {canon(r["id"]): r for r in reference["open"]}
    expected = pr2r_docs["report"]["report"]
    summarized = {f for f, r in rows.items() if len(rows) > 30 and r["risk_level"] in ("Medium", "Low", "Note")}
    narrated = [f for f in rows if f not in summarized]
    category = lambda f: tachi_parts.REPORT_CATEGORY_KEYS[("S", "T", "R", "I", "D", "E", "AG", "LLM").index(  # noqa: E731
        {"AGP": "AG", "TE": "AG", "OI": "LLM", "MI": "LLM"}.get(f.partition("-")[0], f.partition("-")[0]))]
    categories = [c for c in tachi_parts.REPORT_CATEGORY_KEYS if any(category(f) == c for f in rows)]
    patterns = [p for p in tachi_parts.REPORT_PATTERNS if any(r["agentic_pattern"] == p for r in rows.values())]
    groups = pr2_parsers.parse_correlation_groups(threats, list(rows))
    peers = {m for g in groups["groups"] for m in g["members"][1:]}
    roadmap = [f for f in rows if f not in peers]
    assert not groups["repeated"] and len(rows) > 30 and summarized and narrated
    plan_units = {
        "exec_summary": ["risk_posture", "top_threats", "key_recommendations", "compliance"], "architecture_overview": ["system_context", "trust_boundaries"],
        "threat_categories": ["overview"] + ["category." + c for c in categories] + ["summary." + c for c in categories if any(category(f) == c for f in summarized)],
        "threat_analysis": narrated, "cross_cutting_themes": ["themes"], "agentic_patterns": ["pattern." + p for p in patterns],
        "remediation_roadmap": roadmap, "delta_summary": ["progress"]}
    planned = [section for section, _ in tachi_parts.REPORT_PARTS if section in plan_units]  # the template's order, and no attack_chains
    assert [(b["batch_id"], b["section"]) for b in expected["batches"]] == [("B%03d" % n, s) for n, s in enumerate(planned, start=1)]
    counts = {"narrative_fallbacks": 0, "truncations": 0}
    plan = rep.plan
    assert [b["batch_id"] for b in plan["batches"]] == [b["batch_id"] for b in expected["batches"]]
    for entry, section in zip(plan["batches"], planned):
        batch_id = entry["batch_id"]
        raw = committed[pr2r_path("report", rep.base + "inputs/%s.json" % batch_id)]
        batch = tachi_parts.validate_batch_input(rep.inputs[batch_id + ".json"])
        assert entry["input_sha256"] == pr2r_sha(raw) and entry["state"] == "done" and batch["tree_paths"] == {} and batch["refs"] == {}
        assert batch["params"] == plan["params"] and batch["part_path"] == "%s/.tachi-build/report/%s/parts/%s.a1.json" % (gen.PR2R_ROOT + "/run", rep.plan_id, batch_id)
        unit_names = [u.get("key") or canon(u["finding_id"]) for u in batch["units"]]
        assert unit_names == plan_units[section] and {u["section"] for u in batch["units"]} == {section}, section
        assert [canon(f) for f in entry["finding_ids"]] == (plan_units[section] if dict(tachi_parts.REPORT_PARTS)[section] == "findings" else [])
        result =tachi_parts.classify_part(rep.parts[batch_id + ".a1.json"], rep.plan_id, batch_id, "report", "tachi-threat-report", entry["finding_ids"], batch["units"])
        assert result.state == "done", (batch_id, result.detail)
        for key in counts:
            counts[key] += result.counts[key]
    assert counts == {"narrative_fallbacks": 1, "truncations": 1} == {k: expected["stage_record_counts"][k] for k in counts}, "the two edge cases, and no other"
    assert expected["narrated"] == [rows[f]["id"] for f in narrated] and expected["roadmap"] == [rows[f]["id"] for f in roadmap]
    assert expected["roadmap_peers"] == sorted((rows[f]["id"] for f in peers), key=pr2_s2) and expected["patterns"] == patterns
    assert sorted(expected["summarized"], key=pr2_s2) == sorted((rows[f]["id"] for f in summarized), key=pr2_s2)
    # a findings part has one item for each finding and a section part none; only a Critical or High finding has a tree summary
    analysis = [b for b in rep.parts.values() if b["items"] and "narrative" in b["items"][0]][0]
    assert all((item["tree_summary"] is not None) == (rows[canon(item["finding_id"])]["risk_level"] in ("Critical", "High")) for item in analysis["items"])
    assert {part["stage"] for part in rep.parts.values()} == {"report"} and all(not p["finding_ids"] for p in rep.parts.values() if not p["items"])


def test_pr2r_the_report_runs_attack_trees_are_what_the_trees_stage_leaves(committed, pr2_parsers, pr2r_docs):
    """FR-K5.3, FR-K5.5 and FR-K5.7 over the committed files: the manifest, the tree files and Section 7's Critical and High findings are one set, every
    tree is listed, a carried_forward tree is the baseline's file byte for byte and every other is the plan's."""
    t = pr2r_rule2(committed, pr2_parsers, "report")
    manifest = pr2r_json(committed, "report", "run/attack-trees/.manifest.json")
    assert manifest == pr2r_docs["trees"]["trees"]["merged_manifest"], "the report scenario holds the merge that the trees scenario's plan must give"
    listed = [e["file_path"] for e in manifest["trees"]]
    on_disk = sorted(p[len(pr2r_path("report", "run/")):] for p in committed if p.startswith(pr2r_path("report", "run/attack-trees/")) and p.endswith("-attack-tree.md"))
    assert sorted(listed) == on_disk and len(set(listed)) == manifest["attack_tree_count"] == len(t.chosen), "FR-K5.7: every .md file is listed"
    assert sorted(tachi_parts.canonical_finding_id(e["finding_id"]) for e in manifest["trees"]) == sorted(t.chosen), "FR-K5.5: Section 7, the manifest and the files"
    assert [e["finding_id"] for e in manifest["trees"]][: sum(1 for f in t.chosen if t.rows[f]["risk_level"] == "Critical")] == [
        t.rows[f]["id"] for f in sorted((f for f in t.chosen if t.rows[f]["risk_level"] == "Critical"), key=tachi_parts.finding_sort_key)], "Critical first"
    for entry in manifest["trees"]:
        final = committed[pr2r_path("report", "run/" + entry["file_path"])]
        stem = entry["file_path"].rpartition("/")[2]
        if entry["action"] == "carried_forward":
            assert final == committed[pr2r_path("report", "baseline/attack-trees/" + stem)], "FR-K5.3: a carried tree equals its baseline file"
        else:
            assert final == committed[pr2r_path("report", t.stage.base + "trees/" + stem)], "the plan's tree is copied byte for byte"
    for rel in ("threats.md", "tachi-build/trees/current.json"):
        assert committed[pr2r_path("report", "run/" + rel)] == committed[pr2r_path("trees", "run/" + rel)], "the report scenario continues the trees scenario"


# --------------------------------------------------------------------------- materialize: the same scenarios for a real directory
PR2R_HEX = re.compile(rb"[0-9a-f]{64}")
PR2R_BYTES = re.compile(rb'"bytes": [0-9]+')


@pytest.mark.parametrize("name", PR2R_NAMES)
def test_pr2r_materialize_builds_the_scenario_for_a_real_directory_with_digests_that_hold(committed, tmp_path, name):
    dest = tmp_path / name
    written = gen.materialize(name, str(dest))
    dotted = lambda rel: rel.replace("run/.tachi-build/", "run/tachi-build/", 1)  # noqa: E731
    prefix = "pr2-runs/%s/" % name
    assert written == sorted(written) and sorted(dotted(rel) for rel in written) == sorted(p[len(prefix):] for p in committed if p.startswith(prefix))
    assert (dest / "run" / ".tachi-build").is_dir() and not (dest / "run" / "tachi-build").exists()
    for rel in written:
        data = (dest / rel).read_bytes()
        original = committed[prefix + dotted(rel)]
        restored = data.replace(str(dest).encode("utf-8"), gen.PR2R_ROOT.encode("utf-8"))
        if rel.endswith("/plan.json") or (rel == "expected-outcomes.json" and name in ("trees", "report")):  # these hold digests of files that hold the root
            assert PR2R_BYTES.sub(b'"bytes": N', PR2R_HEX.sub(b"H", restored)) == PR2R_BYTES.sub(b'"bytes": N', PR2R_HEX.sub(b"H", original)), rel
        else:
            assert restored == original, "%s differs from the committed copy beyond its root" % rel
    out = str(dest / "run")
    if name in PR2R_PROVENANCE:
        build = out + "/.tachi-build"
        for kind, schema in (("records", tachi_parts.DISPATCH_RECORD_SCHEMA), ("briefs", tachi_parts.BRIEF_SCHEMA)):
            for rel in written:
                if rel.startswith("run/.tachi-build/%s/" % kind):
                    document = tachi_parts.read_document(str(dest / rel), out, schema)  # the strict loader, as the check reads it
                    if kind == "records":
                        assert document["brief"] == "%s/briefs/%s.json" % (build, document["dispatch_id"])
                        assert tachi_parts.path_guard_problem(document["brief"], out) is None, "its brief is a regular file under {out}"
        for rel, schema in (("idmap.json", tachi_parts.IDMAP_SCHEMA), ("phase1/inventory.json", tachi_parts.INVENTORY_SCHEMA),
                            ("phase1/dispatch.json", tachi_parts.DISPATCH_TABLE_SCHEMA)):
            tachi_parts.read_document("%s/%s" % (build, rel), out, schema)
        assert tachi_parts.path_guard_problem(out + "/architecture.md", out) is None
    else:
        expected = json.loads((dest / "expected-outcomes.json").read_text(encoding="utf-8"))
        info = expected["trees"] if name == "trees" else expected["report"]
        stages = [("trees", info["plan_id"], info["plan_digest"])] if name == "trees" else [
            ("trees", info["trees_plan_id"], info["trees_plan_digest"]), ("report", info["plan_id"], info["plan_digest"])]
        for stage, plan_id, digest in stages:  # D3's guard: the pointer, the plan's digest, every input's and every batch input's
            plan, _ = tachi_parts.trusted_plan(stage, out, plan_id, digest, complete=True, read_inputs=True)
            for entry in plan["batches"]:
                batch = tachi_parts.read_document(tachi_parts.input_path(out, stage, plan_id, entry["batch_id"]), out, tachi_parts.BATCH_INPUT_SCHEMA)
                result = tachi_parts.read_part(tachi_parts.part_path(out, stage, plan_id, entry["batch_id"], 1), out, plan_id, entry["batch_id"], stage,
                                               plan["agent_type"], entry["finding_ids"], batch["units"])
                assert result.state == "done", (stage, entry["batch_id"], result.detail)


@pytest.mark.parametrize("name", ["forms", "report"])
def test_pr2r_a_file_that_names_no_root_is_the_same_for_every_root(tmp_path, name):
    first, second = tmp_path / "one", tmp_path / "second-and-longer"
    written = gen.materialize(name, str(first))
    assert gen.materialize(name, str(second)) == written
    built = gen.pr2r_scenario_files(name, gen.PR2R_ROOT)
    same = [rel for rel in written if rel != "expected-outcomes.json" and gen.PR2R_ROOT not in built[rel.replace("run/.tachi-build/", "run/tachi-build/", 1)]]
    assert len(same) >= 6, "the threat models, the baseline files, the ID map and the Phase 1 tables name no root"
    for rel in same:
        assert (first / rel).read_bytes() == (second / rel).read_bytes(), rel
    differ = [rel for rel in written if (first / rel).read_bytes() != (second / rel).read_bytes()]
    assert all(rel.endswith(".json") for rel in differ) and "run/threats.md" not in differ


def test_pr2r_materialize_refuses_what_it_cannot_write_safely(tmp_path):
    with pytest.raises(ValueError):
        gen.materialize("nope", str(tmp_path))
    for bad in ("relative/dir", "", "/has space/x", '/with"quote', "/up/../out", "/dot/./out", "/back\\slash", "/new\nline", 5, None):
        with pytest.raises(ValueError):
            gen.materialize("forms", bad)
    assert not (tmp_path / "run").exists() and list(tmp_path.iterdir()) == [], "nothing is written for a refused request"


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
