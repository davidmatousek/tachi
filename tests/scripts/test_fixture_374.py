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

Not here: chain formation on the fixture's chain material, which T115 and T116 test with the real script, and
the variants (T040, T148 and T103 extend this module as their parts land).

How they run (H15): the generator is imported and driven through ``main(argv)``, in-process. Standard library
and pytest only, and Python 3.9 syntax.
"""

from __future__ import annotations

import ast
import json
import math
import re
import types
from pathlib import Path

import pytest

from ..conftest import _load_hyphenated_script
from . import generate_large_arch_fixture as gen

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "large_arch"
GENERATOR = HERE / "generate_large_arch_fixture.py"

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
