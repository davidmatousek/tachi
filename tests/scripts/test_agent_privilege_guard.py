"""Tests for the CI privilege guard ``scripts/check-agent-privileges.py`` (feature 391, T026).

The guard pins ``docs/standards/CLAUDE_PERMISSIONS.md`` section 8 (the privilege matrix) to
what the tachi agent and command files declare, so a tool, a model, a frontmatter key or a
shell command family cannot change without the matrix changing in the same commit. A guard
nobody has seen go red proves nothing, so this module shows each check red on a mutated copy
and green on the unchanged tree. It is a black-box test: every case runs the CLI in a
subprocess and judges the exit code, the ``--json`` summary and the human lines. Only the
self-test red path loads the script in-process, because a mutation that "fails to fail" can
be forced only by wrapping the guard's own ``run_checks``.

Inputs (read-only in the repo; nothing is written there, and no test touches the network):

- ``scripts/check-agent-privileges.py``: the guard under test. A missing guard FAILS every
  test here (``require_guard``); nothing in this module skips.
- ``.claude/agents/tachi/**`` and ``.claude/commands/tachi.*.md``: the agent and command
  files. Each case copies them, with the matrix and the runbook, to a temp directory.
- ``docs/standards/CLAUDE_PERMISSIONS.md``: section 8, the matrix the files are held to.
- ``docs/guides/ISOLATED_OPERATION_TACHI.md``: the runbook whose section 5 table check C7
  compares with the matrix.

What each group proves:

- live tree: the guard is green on the real inputs (default root, from another working
  directory), looks at every agent and command file that exists, and ``--self-test`` is green
  too (that is the command CI runs).
- C2, C3, C4 (frontmatter): a tool added, removed or swapped, a missing ``tools:`` key, a model
  change, an added key and a missing key are red; tool lists written as a flow list or a
  comma string, in another order, stay green, and so do a BOM, leading blank lines and CRLF.
- C1 (roster, bidirectional): a planted ``name: helper``, an unlisted file without
  frontmatter, a duplicate name, an agent nested in a subdirectory, an agent renamed in its
  file only, the allow-listed document with planted frontmatter (also behind a BOM, blank
  lines and CRLF), a missing file for a matrix row and a symlink are red. With a git tree only a TRACKED non-``.md`` file is red
  (an untracked ``.DS_Store`` is ignored); with no git tree every such file is red except
  known OS junk.
- exit 2 (infrastructure, never drift): every unparseable ``tools:`` shape, a malformed matrix
  cell or table, a missing matrix, an unclosed frontmatter, a delimiter-shaped line inside the
  frontmatter (an indented ``---`` or a ``...`` line with a key hidden after it, in an agent or
  a command), a first line that starts with ``---`` but is not ``---`` (the allow-listed
  document with a ``---yaml`` opener), a ``.git`` that git cannot read; exit 2 also outranks
  exit 1.
- C5 (commands, bidirectional): a command frontmatter key added or removed, a command file
  without a row, a row without a file.
- C6 (shell command families): ``$(...)``, backticks, process substitution, ``eval``,
  ``bash -c`` and ``xargs``; a family chained after ``&&``, ``||``, ``;``, ``|``, ``&`` or
  ``|&``; an env-prefixed or continued command; every fence shape and label the guard scans;
  a line that cannot be tokenized is red, never skipped; a CRLF agent file is scanned like an
  LF one; ``if [ ... ]; then ... fi`` gives the family ``[``; a quoted ``|`` regex stays one
  token.
- C7 (write locations): the runbook table and matrix section 8.5 against the Writes cells,
  in both directions, and a duplicated row.
- C8 (self-test): five mutations are detected on a clean tree. A drifted tree stays exit 1 with
  the self-test passing, also when the drift is an unlisted agent that sorts before every real
  agent (M1 must pick an agent with a section 8 row) or frontmatter already in the allow-listed
  document or a file the self-test plants itself (a mutation whose finding is already red is
  reported as already red, not as having failed to fail). A guard that is blind to a check, or
  a tree with no mutation target, ends in exit 2.
- output contract: ``--json`` parses, is ``json.dumps(sort_keys=True, indent=2)`` and lists
  every violation with its check id; the human lines and the ``[391]`` prefix.
- negative controls: a mutation helper that changes nothing fails instead of passing, the
  baseline copy is asserted green before any mutation, and the digest fixture fails the
  module if a test changed the repo's inputs.

Stdlib and pytest only; Python 3.9 syntax; ASCII source (the BOM is built with chr()).
"""

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, NamedTuple, Optional, Sequence

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / "scripts" / "check-agent-privileges.py"

MATRIX = "docs/standards/CLAUDE_PERMISSIONS.md"
RUNBOOK = "docs/guides/ISOLATED_OPERATION_TACHI.md"
AGENTS = ".claude/agents/tachi"
COMMANDS = ".claude/commands"
ALLOW_LISTED = "_TACHI_AGENT_BEST_PRACTICES.md"

PREFIX = "[391]"
TIMEOUT_SECONDS = 180
BOM = chr(0xFEFF)

# Agent files the mutations act on, by file stem; the name: value is "tachi-" + stem.
READ_ONLY = "tampering"  # tools: Read, Glob, Grep; no shell fences
OTHER_READ_ONLY = "spoofing"
THIRD_READ_ONLY = "repudiation"
ORCHESTRATOR = "orchestrator"  # Bash-capable; Bash families: python3
REPORT_ASSEMBLER = "report-assembler"  # Bash-capable; Bash families: python3, test, typst
INFOGRAPHIC = "threat-infographic"  # Bash-capable; Bash families: [, echo, python3, test
BASH_AGENTS = (ORCHESTRATOR, REPORT_ASSEMBLER, INFOGRAPHIC)

# A command family that no agent's Bash families cell holds.
CURL = "curl -s http://example.invalid/x"


def agent_path(stem: str) -> str:
    return f"{AGENTS}/{stem}.md"


def command_path(name: str) -> str:
    return f"{COMMANDS}/tachi.{name}.md"


# =============================================================================
# Running the guard
# =============================================================================


class Run(NamedTuple):
    code: int
    out: str
    err: str

    def show(self) -> str:
        return f"exit {self.code}\n--- stdout\n{self.out}\n--- stderr\n{self.err}"

    def data(self) -> Dict[str, Any]:
        """The ``--json`` summary; fails with the raw output when stdout is not one JSON document."""
        try:
            return json.loads(self.out)
        except ValueError:
            raise AssertionError("stdout is not a JSON document:\n" + self.show())


def require_guard() -> Path:
    """The guard script, or a test FAILURE (never a skip) when it is missing."""
    if not GUARD.is_file():
        pytest.fail(
            f"the privilege guard is missing: {GUARD} (T025 ships it; without it every "
            "privilege-matrix check is silently absent, so this must fail, not skip)",
            pytrace=False,
        )
    return GUARD


def clean_env(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """The caller's environment minus every GIT_* variable (a hook may export GIT_DIR)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(extra or {})
    return env


def run_guard(
    *args: str,
    root: Optional[Path] = None,
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
) -> Run:
    """``python3 scripts/check-agent-privileges.py [--repo-root ROOT] ARGS`` in a subprocess."""
    command = [sys.executable, str(require_guard())]
    if root is not None:
        command += ["--repo-root", str(root)]
    command += list(args)
    proc = subprocess.run(
        command,
        cwd=str(cwd) if cwd is not None else None,
        env=clean_env(env),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=TIMEOUT_SECONDS,
    )
    return Run(
        proc.returncode,
        proc.stdout.decode("utf-8", "replace"),
        proc.stderr.decode("utf-8", "replace"),
    )


def git(root: Path, *args: str) -> None:
    """Run git in a temp tree, ignoring the user's and the system's git configuration."""
    env = clean_env(
        {"HOME": str(root.parent), "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    )
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=TIMEOUT_SECONDS,
    )
    assert proc.returncode == 0, f"git {' '.join(args)} failed: {proc.stderr.decode('utf-8', 'replace')}"


def digest(files: Iterable[Path]) -> str:
    """One hash over the names and bytes of the given files (a symlink counts by its target)."""
    h = hashlib.sha256()
    for path in sorted(files):
        h.update(str(path).encode("utf-8", "surrogateescape") + b"\0")
        h.update(os.readlink(path).encode("utf-8", "surrogateescape") if path.is_symlink() else path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def live_inputs() -> List[Path]:
    """Every repo file the guard reads (and so every file this module must leave alone)."""
    files = [GUARD, REPO_ROOT / MATRIX, REPO_ROOT / RUNBOOK]
    files += [p for p in (REPO_ROOT / AGENTS).rglob("*") if p.is_file() or p.is_symlink()]
    files += list((REPO_ROOT / COMMANDS).glob("tachi.*.md"))
    return [p for p in files if p.exists() or p.is_symlink()]


# =============================================================================
# The tree under mutation
# =============================================================================


class Tree:
    """A temp copy of the guard's inputs; the helpers below mutate it, never the repo."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def path(self, rel: str) -> Path:
        return self.root / rel

    def read(self, rel: str) -> str:
        return self.path(rel).read_bytes().decode("utf-8")

    def write(self, rel: str, text: str) -> None:
        target = self.path(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))

    def replace(self, rel: str, old: str, new: str) -> None:
        """Replace the first ``old`` in a file; a missing ``old`` fails, so no mutation is ever a silent no-op."""
        text = self.read(rel)
        assert old in text, f"{rel} has no {old!r}: the live file changed shape, so this mutation proves nothing"
        self.write(rel, text.replace(old, new, 1))

    def append(self, rel: str, block: str) -> None:
        self.write(rel, self.read(rel).rstrip("\n") + "\n\n" + block)

    def run(self, *args: str, env: Optional[Dict[str, str]] = None) -> Run:
        # a neutral working directory: the guard must depend on --repo-root only
        return run_guard(*args, root=self.root, cwd=self.root.parent, env=env)

    def check(self, *args: str, env: Optional[Dict[str, str]] = None) -> Run:
        return self.run("--json", *args, env=env)


def copy_inputs(dest: Path) -> None:
    """Copy the guard's inputs (the matrix, the runbook, the agent and command files) under dest."""
    sources = [REPO_ROOT / MATRIX, REPO_ROOT / RUNBOOK]
    sources += sorted(p for p in (REPO_ROOT / AGENTS).rglob("*.md") if p.is_file() and not p.is_symlink())
    sources += sorted((REPO_ROOT / COMMANDS).glob("tachi.*.md"))
    for src in sources:
        if not src.is_file():
            pytest.fail(f"a guard input is missing from the repo: {src}", pytrace=False)
        target = dest / src.relative_to(REPO_ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(src), str(target))


class Pristine(NamedTuple):
    root: Path
    summary: Dict[str, Any]


@pytest.fixture(scope="module", autouse=True)
def repo_inputs_stay_unchanged():
    """Fail the module if any test changed a file the guard reads in the repo (mutations act on copies)."""
    before = digest(live_inputs()) if GUARD.exists() else ""
    yield
    if GUARD.exists():
        assert digest(live_inputs()) == before, "a test changed one of the guard's inputs in the repo tree"


@pytest.fixture(scope="session")
def pristine(tmp_path_factory) -> Pristine:
    """One copy of the live inputs, asserted green once; every case works on a copy of this copy."""
    root = tmp_path_factory.mktemp("privilege-guard-pristine") / "tree"
    copy_inputs(root)
    run = run_guard("--json", root=root, cwd=root.parent)
    if run.code != 0:
        pytest.fail(
            "a copy of the live inputs is not green, so the mutation cases would prove nothing; "
            "see test_live_tree_is_green for the findings:\n" + run.show(),
            pytrace=False,
        )
    return Pristine(root, run.data())


@pytest.fixture
def tree(pristine, tmp_path) -> Tree:
    root = tmp_path / "tree"
    shutil.copytree(str(pristine.root), str(root), symlinks=True)
    return Tree(root)


@pytest.fixture(scope="module")
def guard_module():
    """The guard loaded in-process (only the self-test red path needs this)."""
    spec = importlib.util.spec_from_file_location("check_agent_privileges_under_test", str(require_guard()))
    module = importlib.util.module_from_spec(spec)
    keep = sys.dont_write_bytecode
    sys.dont_write_bytecode = True  # a .pyc under scripts/ would dirty the tree being tested
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = keep
    return module


# =============================================================================
# Mutations (each acts on a Tree and fails loudly when it would change nothing)
# =============================================================================

TOOLS_BLOCK = re.compile(r"(?m)^tools:\n(?:  - .*\n)+")


def tools_of(tree: Tree, stem: str) -> List[str]:
    match = TOOLS_BLOCK.search(tree.read(agent_path(stem)))
    assert match, f"{stem}: no block-list tools: in the frontmatter (the live file changed shape)"
    return [line.strip()[2:] for line in match.group(0).splitlines()[1:]]


def set_tools_block(tree: Tree, stem: str, block: str) -> None:
    """Replace the whole ``tools:`` block (a block list in every live agent file) with raw text."""
    rel = agent_path(stem)
    text = tree.read(rel)
    new, count = TOOLS_BLOCK.subn(lambda _m: block, text, count=1)
    assert count == 1 and new != text, f"{rel}: the tools: block was not replaced"
    tree.write(rel, new)


def set_tools(tree: Tree, stem: str, tools: Sequence[str]) -> None:
    set_tools_block(tree, stem, "tools:\n" + "".join(f"  - {t}\n" for t in tools))


def add_tool(tree: Tree, stem: str, tool: str) -> None:
    tools = tools_of(tree, stem)
    assert tool not in tools, f"{stem} already has {tool}"
    set_tools(tree, stem, tools + [tool])


def remove_tool(tree: Tree, stem: str, tool: str) -> None:
    tools = tools_of(tree, stem)
    assert tool in tools, f"{stem} has no {tool}"
    set_tools(tree, stem, [t for t in tools if t != tool])


def set_model(tree: Tree, stem: str, model: str) -> None:
    tree.replace(agent_path(stem), "\nmodel: sonnet\n", f"\nmodel: {model}\n")


def add_agent_key(tree: Tree, stem: str, line: str) -> None:
    tree.replace(agent_path(stem), "\nmodel: sonnet\n---\n", f"\nmodel: sonnet\n{line}\n---\n")


def drop_line(tree: Tree, rel: str, prefix: str) -> None:
    """Delete the first line that starts with ``prefix``."""
    lines = tree.read(rel).split("\n")
    hits = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    assert hits, f"{rel} has no line starting {prefix!r}"
    del lines[hits[0]]
    tree.write(rel, "\n".join(lines))


def agent_text(name: str, tools: Sequence[str] = ("Read", "Glob", "Grep"), model: str = "sonnet") -> str:
    lines = ["---", f"name: {name}", 'description: "planted by the T026 test"', "tools:"]
    lines += [f"  - {t}" for t in tools] + [f"model: {model}", "---", "# Planted by the T026 test", ""]
    return "\n".join(lines)


def plant(tree: Tree, rel: str, text: str) -> None:
    assert not tree.path(rel).exists(), f"{rel} already exists"
    tree.write(rel, text)


def fenced(*body: str, label: str = "bash") -> str:
    return "```" + label + "\n" + "\n".join(body) + "\n```\n"


def table_row(lines: List[str], key: str) -> int:
    """Index of the one table row whose first cell is ``key`` (a backticked token)."""
    hits = [i for i, line in enumerate(lines) if line.startswith(f"| {key} |")]
    assert len(hits) == 1, f"expected exactly one table row starting {key}, found {len(hits)}"
    return hits[0]


def edit_cells(tree: Tree, rel: str, key: str, edit: Callable[[List[str]], List[str]]) -> None:
    lines = tree.read(rel).split("\n")
    i = table_row(lines, key)
    cells = [c.strip() for c in lines[i].strip()[1:-1].split("|")]
    new = edit(list(cells))
    assert new != cells, f"{rel}: the row {key} did not change"
    lines[i] = "| " + " | ".join(new) + " |"
    tree.write(rel, "\n".join(lines))


def set_cell(index: int, value: str) -> Callable[[List[str]], List[str]]:
    def edit(cells: List[str]) -> List[str]:
        cells[index] = value
        return cells

    return edit


def drop_row(tree: Tree, rel: str, key: str) -> None:
    lines = tree.read(rel).split("\n")
    del lines[table_row(lines, key)]
    tree.write(rel, "\n".join(lines))


def insert_row_after(tree: Tree, rel: str, key: str, row: str, times: int = 1) -> None:
    lines = tree.read(rel).split("\n")
    i = table_row(lines, key)
    lines[i + 1 : i + 1] = [row] * times
    tree.write(rel, "\n".join(lines))


def allow_bash_family(tree: Tree, stem: str, family: str) -> None:
    """Add ``family`` to the Bash families cell of the agent's matrix row (cell 4)."""
    edit_cells(
        tree, MATRIX, f"`tachi-{stem}`",
        lambda cells: cells[:4] + [cells[4] + f", `{family}`"] + cells[5:],
    )


def make_agents_dir_a_symlink(tree: Tree) -> None:
    real, moved = tree.path(AGENTS), tree.path(AGENTS + "-real")
    real.rename(moved)
    os.symlink(moved.name, str(real))


def symlink(tree: Tree, rel: str, target: str) -> None:
    path = tree.path(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(target, str(path))


# =============================================================================
# Judging a run
# =============================================================================


class Want(NamedTuple):
    """One expected finding: a check id, the file it names (no :line) and a message substring."""

    check: str
    file: str
    text: str


def listing(violations: Iterable[Dict[str, str]]) -> str:
    return "\n".join(f"  {v['check_id']} {v['file']}: {v['message']}" for v in violations) or "  (none)"


def assert_wants(data: Dict[str, Any], wants: Sequence[Want]) -> None:
    violations = data["violations"]
    for w in wants:
        hits = [
            v for v in violations
            if v["check_id"] == w.check and v["file"].split(":")[0] == w.file and w.text in v["message"]
        ]
        assert hits, f"no {w.check} finding in {w.file} containing {w.text!r}; findings:\n{listing(violations)}"
    # nothing else fired: a mutation must turn exactly the expected checks red, not shake loose a neighbour
    assert {v["check_id"] for v in violations} == {w.check for w in wants}, listing(violations)


def assert_red(tree: Tree, wants: Sequence[Want], *args: str) -> Dict[str, Any]:
    run = tree.check(*args)
    assert run.code == 1, "expected exit 1 (drift)\n" + run.show()
    data = run.data()
    assert data["status"] == "drift" and data["infra"] == [], run.show()
    assert_wants(data, wants)
    return data


def assert_green(tree: Tree, *args: str) -> Dict[str, Any]:
    run = tree.check(*args)
    assert run.code == 0, "expected exit 0 (pass)\n" + run.show()
    data = run.data()
    assert data["status"] == "pass" and data["violations"] == [] and data["infra"] == [], run.show()
    return data


def assert_infra(tree: Tree, check: str, file: str, text: str) -> Dict[str, Any]:
    run = tree.check()
    assert run.code == 2, "expected exit 2 (infrastructure)\n" + run.show()
    data = run.data()
    assert data["status"] == "infra", run.show()
    hits = [i for i in data["infra"] if i["check_id"] == check and i["file"] == file and text in i["message"]]
    assert hits, f"no {check} infra entry for {file} containing {text!r}:\n{json.dumps(data['infra'], indent=2)}"
    assert f"{PREFIX} ERROR {check}" in run.err, run.show()
    return data


# =============================================================================
# The live tree and the guard itself
# =============================================================================


def test_the_guard_script_is_present():
    assert require_guard().is_file()


def test_a_missing_guard_fails_the_run_instead_of_skipping_it(tmp_path, monkeypatch):
    monkeypatch.setitem(globals(), "GUARD", tmp_path / "check-agent-privileges.py")
    with pytest.raises(pytest.fail.Exception):
        run_guard("--json", root=tmp_path)


def test_live_tree_is_green(tmp_path):
    run = run_guard(cwd=tmp_path)  # the default root: the checkout the script sits in
    assert run.code == 0, run.show()
    assert f"{PREFIX} RESULT: pass (exit 0)" in run.out
    assert run.err == ""


def test_live_tree_summary_is_green_and_complete():
    data = run_guard("--json", root=REPO_ROOT).data()
    assert data["status"] == "pass"
    assert data["violations"] == data["drift"] == data["infra"] == []
    assert data["roster"]["red"] == []
    assert data["roster"]["allowlisted"] == [f"{AGENTS}/{ALLOW_LISTED}"]
    assert data["self_test"] is None
    # a guard that scanned nothing would be green too: it must have seen every file there is
    agent_files = [p for p in (REPO_ROOT / AGENTS).rglob("*.md") if p.name != ALLOW_LISTED]
    command_files = list((REPO_ROOT / COMMANDS).glob("tachi.*.md"))
    assert data["roster"]["agents"] == len(agent_files) > 0
    assert data["counts"]["commands"] == len(command_files) > 0
    assert data["counts"]["paths"] > 0
    assert data["counts"]["bash_agents"] == len(data["bash_families"]) > 0
    for agent, families in data["bash_families"].items():
        assert set(families["found"]) <= set(families["allowed"]), agent


def test_live_tree_self_test_is_green():
    data = run_guard("--self-test", "--json", root=REPO_ROOT).data()
    assert data["status"] == "pass" and data["self_test"] == "pass"
    assert {d["id"]: d["expected_check"] for d in data["self_test_detail"]} == {
        "M1": "C2", "M2": "C1", "M3": "C1", "M4": "C1", "M5": "C1",
    }
    assert all(d["detected"] for d in data["self_test_detail"])
    # a green tree has nothing to be already red on: every mutation is proven, none hides behind that
    assert not any(d["already_red"] for d in data["self_test_detail"])
    for d in data["self_test_detail"]:
        assert set(d) == {"id", "mutation", "expected_check", "expected_file", "exit_code", "detected", "already_red"}


def test_live_tree_self_test_in_human_mode_is_the_ci_step(tmp_path):
    run = run_guard("--self-test", cwd=tmp_path)  # the exact command the CI workflow runs
    assert run.code == 0, run.show()
    assert f"{PREFIX} C8 self-test" in run.out and "PASS" in run.out
    assert f"{PREFIX} RESULT: pass (exit 0)" in run.out
    assert run.err == ""


# =============================================================================
# C2, C3, C4: tools, model, key set
# =============================================================================

TAMPERING = agent_path(READ_ONLY)

FRONTMATTER_RED = [
    pytest.param(
        lambda t: add_tool(t, READ_ONLY, "Bash"),
        [Want("C2", TAMPERING, "(added ['Bash'], removed [])")], id="tool-added-bash",
    ),
    pytest.param(
        lambda t: add_tool(t, READ_ONLY, "Write"),
        [Want("C2", TAMPERING, "(added ['Write'], removed [])")], id="tool-added-write",
    ),
    pytest.param(
        lambda t: remove_tool(t, READ_ONLY, "Grep"),
        [Want("C2", TAMPERING, "(added [], removed ['Grep'])")], id="tool-removed",
    ),
    pytest.param(
        lambda t: set_tools(t, READ_ONLY, ["Read", "Glob", "Write"]),
        [Want("C2", TAMPERING, "(added ['Write'], removed ['Grep'])")], id="tool-swapped-same-count",
    ),
    pytest.param(
        lambda t: set_tools_block(t, READ_ONLY, ""),
        [Want("C2", TAMPERING, "no tools: key"), Want("C4", TAMPERING, "missing ['tools']")],
        id="tools-key-removed",
    ),
    pytest.param(
        lambda t: set_model(t, READ_ONLY, "opus"),
        [Want("C3", TAMPERING, "model 'opus' differs from the section 8 row")], id="model-changed",
    ),
    pytest.param(
        lambda t: drop_line(t, TAMPERING, "model:"),
        [Want("C3", TAMPERING, "no model: key"), Want("C4", TAMPERING, "missing ['model']")],
        id="model-key-removed",
    ),
    pytest.param(
        lambda t: add_agent_key(t, READ_ONLY, "permissionMode: bypassPermissions"),
        [Want("C4", TAMPERING, "unexpected ['permissionMode']")], id="key-added",
    ),
    pytest.param(
        lambda t: drop_line(t, TAMPERING, "description:"),
        [Want("C4", TAMPERING, "missing ['description']")], id="key-removed",
    ),
]


@pytest.mark.parametrize("mutate, wants", FRONTMATTER_RED)
def test_frontmatter_drift_is_red(tree, mutate, wants):
    mutate(tree)
    assert_red(tree, wants)


EQUIVALENT_TOOLS = [
    pytest.param("tools: [Read, Glob, Grep]\n", id="flow-list"),
    pytest.param("tools: [Grep, Read, Glob]\n", id="flow-list-other-order"),
    pytest.param("tools: Glob, Read, Grep\n", id="comma-string-other-order"),
    pytest.param('tools: "Read, Glob, Grep"  # a comment\n', id="quoted-comma-string-with-comment"),
    pytest.param("tools:\n- 'Read'\n- \"Glob\"\n- Grep\n", id="block-list-at-column-0-with-quoted-items"),
    pytest.param("tools: [Read, Glob, Grep,]\n", id="flow-list-trailing-comma"),
]


@pytest.mark.parametrize("block", EQUIVALENT_TOOLS)
def test_tools_written_in_another_shape_stay_green(tree, block):
    set_tools_block(tree, READ_ONLY, block)
    assert_green(tree)


LENIENT_FRONTMATTER = [
    pytest.param(lambda text: BOM + text, id="bom"),
    pytest.param(lambda text: "\n\n" + text, id="leading-blank-lines"),
    pytest.param(lambda text: text.replace("\n", "\r\n"), id="crlf"),
]


@pytest.mark.parametrize("transform", LENIENT_FRONTMATTER)
def test_an_agent_file_with_a_bom_blank_lines_or_crlf_is_still_compared_and_green(tree, transform):
    tree.write(TAMPERING, transform(tree.read(TAMPERING)))
    assert_green(tree)
    tree.replace(TAMPERING, "model: sonnet", "model: opus")  # still compared: drift is red behind the same disguise
    assert_red(tree, [Want("C3", TAMPERING, "model 'opus' differs")])


# =============================================================================
# C1: roster
# =============================================================================

HELPER = f"{AGENTS}/helper.md"
UNLISTED = f"{AGENTS}/notes.md"
DOC = f"{AGENTS}/{ALLOW_LISTED}"
PLANTED_DOC = agent_text("tachi-planted-doc")


def plant_in_doc(transform: Callable[[str], str]) -> Callable[[Tree], None]:
    def mutate(tree: Tree) -> None:
        tree.write(DOC, transform(PLANTED_DOC + tree.read(DOC)))

    return mutate


def duplicate_tampering(tree: Tree) -> None:
    plant(tree, agent_path("tampering-copy"), tree.read(TAMPERING))


def delete_tampering(tree: Tree) -> None:
    tree.path(TAMPERING).unlink()


ROSTER_RED = [
    pytest.param(
        lambda t: plant(t, HELPER, agent_text("helper")),
        [Want("C1", HELPER, "does not start with 'tachi-'"),
         Want("C1", HELPER, "has no row in the section 8 agents table")],
        id="planted-name-helper",
    ),
    pytest.param(
        lambda t: plant(t, HELPER, agent_text("tachi-extra")),
        [Want("C1", HELPER, "agent 'tachi-extra' has no row in the section 8 agents table")],
        id="tachi-name-without-a-row",
    ),
    pytest.param(
        lambda t: plant(t, HELPER, "---\ndescription: x\n---\n# no name\n"),
        [Want("C1", HELPER, "frontmatter has no name: key"), Want("C4", HELPER, "missing ['model', 'name', 'tools']")],
        id="frontmatter-without-a-name",
    ),
    pytest.param(
        lambda t: plant(t, UNLISTED, "# Not an agent and not on the allow-list\n"),
        [Want("C1", UNLISTED, ".md file without frontmatter that is not on the allow-list")],
        id="unlisted-file-without-frontmatter",
    ),
    pytest.param(
        duplicate_tampering,
        [Want("C1", TAMPERING, "duplicate agent name 'tachi-tampering'"),
         Want("C1", agent_path("tampering-copy"), "duplicate agent name 'tachi-tampering'")],
        id="duplicate-name",
    ),
    pytest.param(
        lambda t: plant(t, f"{AGENTS}/nested/deeper/helper.md", agent_text("helper")),
        [Want("C1", f"{AGENTS}/nested/deeper/helper.md", "does not start with 'tachi-'"),
         Want("C1", f"{AGENTS}/nested/deeper/helper.md", "has no row in the section 8 agents table")],
        id="planted-agent-in-a-subdirectory",
    ),
    pytest.param(
        lambda t: plant(t, f"{AGENTS}/sub/{ALLOW_LISTED}", "# The allow-listed name is allowed only at the top\n"),
        [Want("C1", f"{AGENTS}/sub/{ALLOW_LISTED}", ".md file without frontmatter that is not on the allow-list")],
        id="allow-listed-name-in-a-subdirectory",
    ),
    pytest.param(
        plant_in_doc(lambda text: text),
        [Want("C1", DOC, "allow-listed document has leading frontmatter"),
         Want("C1", DOC, "agent 'tachi-planted-doc' has no row")],
        id="allow-listed-document-with-planted-frontmatter",
    ),
    pytest.param(
        plant_in_doc(lambda text: BOM + text),
        [Want("C1", DOC, "allow-listed document has leading frontmatter")],
        id="planted-frontmatter-behind-a-bom",
    ),
    pytest.param(
        plant_in_doc(lambda text: "\n\n" + text),
        [Want("C1", DOC, "allow-listed document has leading frontmatter")],
        id="planted-frontmatter-behind-blank-lines",
    ),
    pytest.param(
        plant_in_doc(lambda text: text.replace("\n", "\r\n")),
        [Want("C1", DOC, "allow-listed document has leading frontmatter")],
        id="planted-frontmatter-in-crlf",
    ),
    pytest.param(
        delete_tampering,
        [Want("C1", AGENTS, "section 8 row 'tachi-tampering' has no agent file under")],
        id="matrix-row-without-a-file",
    ),
    pytest.param(
        lambda t: t.replace(TAMPERING, "name: tachi-tampering\n", "name: tachi-renamed\n"),
        [Want("C1", TAMPERING, "agent 'tachi-renamed' has no row in the section 8 agents table"),
         Want("C1", AGENTS, "section 8 row 'tachi-tampering' has no agent file under")],
        id="agent-renamed-in-the-file-only",
    ),
    pytest.param(
        lambda t: symlink(t, agent_path("alias"), "tampering.md"),
        [Want("C1", agent_path("alias"), "symlink in the agents directory")], id="symlink-to-an-agent-file",
    ),
    pytest.param(
        lambda t: symlink(t, agent_path("ghost"), "no-such-target.md"),
        [Want("C1", agent_path("ghost"), "symlink in the agents directory")], id="dangling-symlink",
    ),
    pytest.param(
        lambda t: symlink(t, f"{AGENTS}/linked-dir", str(t.path(COMMANDS))),
        [Want("C1", f"{AGENTS}/linked-dir", "symlink in the agents directory")], id="symlink-to-a-directory",
    ),
    pytest.param(
        make_agents_dir_a_symlink,
        [Want("C1", AGENTS, "the agents directory is a symlink")], id="agents-directory-is-a-symlink",
    ),
]


@pytest.mark.parametrize("mutate, wants", ROSTER_RED)
def test_roster_drift_is_red(tree, mutate, wants):
    mutate(tree)
    assert_red(tree, wants)


# Non-.md files: a git tree decides (tracked is red, untracked junk is ignored); with no git
# tree every such file is red except known OS junk.
NON_MD = [
    pytest.param(".DS_Store", False, False, False, id="no-git-ds-store-is-os-junk"),
    pytest.param("Thumbs.db", False, False, False, id="no-git-thumbs-db-is-os-junk"),
    pytest.param("desktop.ini", False, False, False, id="no-git-desktop-ini-is-os-junk"),
    pytest.param("notes.txt", False, False, True, id="no-git-other-file-is-red"),
    pytest.param(".DS_Store", True, False, False, id="git-untracked-ds-store-is-ignored"),
    pytest.param("notes.txt", True, False, False, id="git-untracked-other-file-is-ignored"),
    pytest.param(".DS_Store", True, True, True, id="git-tracked-ds-store-is-red"),
    pytest.param("notes.txt", True, True, True, id="git-tracked-other-file-is-red"),
]


@pytest.mark.parametrize("name, git_tree, tracked, red", NON_MD)
def test_non_md_files_in_the_agents_directory(tree, name, git_tree, tracked, red):
    if git_tree:
        git(tree.root, "init", "-q")
        git(tree.root, "add", "-A")
    rel = f"{AGENTS}/{name}"
    tree.path(rel).write_bytes(b"\x00\x00\x00\x01Bud1")
    if tracked:
        git(tree.root, "add", "-f", rel)
    if red:
        assert_red(tree, [Want("C1", rel, "tracked non-.md file in the agents directory")])
    else:
        assert_green(tree)


# =============================================================================
# Exit 2: infrastructure, never drift
# =============================================================================

BAD_TOOLS = [
    pytest.param("tools: {Read: true}\n", "not a list or a comma string", id="flow-mapping"),
    pytest.param("tools: |\n  Read\n  Glob\n", "continues on later lines", id="block-scalar"),
    pytest.param("tools: Read,\n  Glob,\n  Grep\n", "continues on later lines", id="multi-line-plain-scalar"),
    pytest.param("tools: [Read,\n  Glob]\n", "continues on later lines", id="multi-line-flow-list"),
    pytest.param("tools:\n", "has no value", id="null"),
    pytest.param("tools: *shared\n", "not a list or a comma string", id="alias"),
    pytest.param("tools: &shared [Read, Glob, Grep]\n", "not a list or a comma string", id="anchor"),
    pytest.param("tools: !!seq [Read]\n", "not a list or a comma string", id="tag"),
    pytest.param("tools: [[Read], Glob]\n", "unsupported YAML shape", id="nested-list"),
    pytest.param("tools:\n  - Read: yes\n  - Glob\n", "mapping-shaped item", id="mapping-shaped-item"),
    pytest.param("tools: [Read, , Grep]\n", "empty item", id="empty-item"),
    pytest.param('tools: ["Read, Glob]\n', "unterminated quote", id="unterminated-quote"),
]


@pytest.mark.parametrize("block, text", BAD_TOOLS)
def test_an_unparseable_tools_shape_is_exit_2_not_drift(tree, block, text):
    set_tools_block(tree, READ_ONLY, block)
    assert_infra(tree, "C2", TAMPERING, text)


def break_cell_syntax(tree: Tree) -> None:
    edit_cells(tree, MATRIX, "`tachi-tampering`", set_cell(2, "Read, Glob, Grep"))


def write_empty_set_as_hyphen(tree: Tree) -> None:
    edit_cells(tree, MATRIX, "`tachi-tampering`", set_cell(4, "-"))


def repeat_a_token(tree: Tree) -> None:
    edit_cells(tree, MATRIX, "`tachi-tampering`", set_cell(2, "`Read`, `Read`, `Glob`"))


def drop_a_cell(tree: Tree) -> None:
    edit_cells(tree, MATRIX, "`tachi-tampering`", lambda cells: cells[:-1])


def rename_a_command(tree: Tree) -> None:
    edit_cells(tree, MATRIX, "`/tachi.risk-score`", set_cell(0, "`/risk-score`"))


def unclose_the_frontmatter(tree: Tree) -> None:
    plant(tree, HELPER, "---\nname: tachi-helper\ntools:\n  - Read\n")


def repeat_a_key(tree: Tree) -> None:
    plant(tree, HELPER, agent_text("tachi-helper").replace("model: sonnet\n", "model: sonnet\nmodel: opus\n"))


# Delimiter-shaped lines inside the frontmatter. Each case puts a key (in the third, a command's
# allowed-tools) after a line that strips to --- or ..., then closes with a --- at the start of a line.
# A guard that stops at the first such line never sees the key and, the key set being unchanged, stays
# green; a parser that closes only at the column-0 --- may read it. Two parsers may disagree on where the
# frontmatter ends, so the guard must refuse the file (exit 2).
def hide_a_key_behind_an_indented_delimiter(tree: Tree) -> None:
    drop_line(tree, TAMPERING, "description:")  # it comes back below, as a block scalar that holds the ---
    add_agent_key(
        tree, READ_ONLY, "description: |\n  planted by the T026 test\n  ---\npermissionMode: bypassPermissions"
    )


def hide_a_key_behind_a_document_end_marker(tree: Tree) -> None:
    add_agent_key(tree, READ_ONLY, "...\npermissionMode: bypassPermissions")


def hide_allowed_tools_behind_an_indented_delimiter(tree: Tree) -> None:
    rel = command_path("risk-score")
    tree.replace(rel, "---\ndescription: ", "---\ndescription: |\n  ")  # the live description becomes the block
    tree.replace(rel, "\n---\n", "\n  ---\nallowed-tools: Bash\n---\n")  # the first closer is the real one


def remove_the_agents_directory(tree: Tree) -> None:
    shutil.rmtree(str(tree.path(AGENTS)))


INFRA = [
    pytest.param(break_cell_syntax, "MATRIX", MATRIX, "breaks the set syntax", id="cell-without-backticks"),
    pytest.param(write_empty_set_as_hyphen, "MATRIX", MATRIX, "breaks the set syntax", id="empty-set-is-not-an-em-dash"),
    pytest.param(repeat_a_token, "MATRIX", MATRIX, "repeats a token", id="cell-repeats-a-token"),
    pytest.param(drop_a_cell, "MATRIX", MATRIX, "has 6 cells, the header has 7", id="row-with-a-missing-cell"),
    pytest.param(rename_a_command, "MATRIX", MATRIX, "is not /tachi.<name>", id="command-cell-is-not-a-tachi-command"),
    pytest.param(
        lambda t: t.replace(MATRIX, "| Agent | Tier |", "| Agents | Tier |"),
        "MATRIX", MATRIX, "section 8.3 agents table not found", id="agents-table-header-changed",
    ),
    pytest.param(
        lambda t: t.replace(MATRIX, "## 8. Agent and command privilege matrix", "## Agent and command privilege matrix"),
        "MATRIX", MATRIX, "section 8: heading not found", id="section-8-heading-missing",
    ),
    pytest.param(
        lambda t: t.path(MATRIX).unlink(),
        "MATRIX", MATRIX, "cannot read file", id="matrix-file-missing",
    ),
    pytest.param(
        lambda t: t.replace(RUNBOOK, "## 5. Write locations", "## 5. Write places"),
        "C7", RUNBOOK, "runbook section 5: heading not found", id="runbook-section-5-heading-changed",
    ),
    pytest.param(unclose_the_frontmatter, "C1", HELPER, "never closes", id="frontmatter-never-closes"),
    pytest.param(repeat_a_key, "C1", HELPER, "duplicate frontmatter key 'model'", id="frontmatter-key-repeated"),
    pytest.param(
        hide_a_key_behind_an_indented_delimiter,
        "C1", TAMPERING, "inside the frontmatter", id="indented-delimiter-hides-a-key",
    ),
    pytest.param(
        hide_a_key_behind_a_document_end_marker,
        "C1", TAMPERING, "inside the frontmatter", id="document-end-marker-hides-a-key",
    ),
    pytest.param(
        hide_allowed_tools_behind_an_indented_delimiter,
        "C5", command_path("risk-score"), "inside the frontmatter",
        id="command-indented-delimiter-hides-allowed-tools",
    ),
    # a first line that starts with --- but is not --- reads as "no frontmatter" to a guard that wants an exact
    # ---, and the allow-listed document may have none; another reader may take that line as an opener
    pytest.param(
        plant_in_doc(lambda text: text.replace("---\n", "---yaml\n", 1)),
        "C1", DOC, "is not exactly ---", id="allow-listed-document-with-a-yaml-opener",
    ),
    pytest.param(remove_the_agents_directory, "C1", AGENTS, "agents directory not found", id="agents-directory-missing"),
]


@pytest.mark.parametrize("mutate, check, file, text", INFRA)
def test_an_input_the_guard_cannot_interpret_is_exit_2(tree, mutate, check, file, text):
    mutate(tree)
    assert_infra(tree, check, file, text)


def test_a_git_tree_that_git_cannot_read_is_exit_2(tree):
    (tree.path(".git")).mkdir()  # looks like a git tree, is not one
    run = tree.check(env={"GIT_CEILING_DIRECTORIES": str(tree.root.parent)})
    assert run.code == 2, run.show()
    assert any(i["check_id"] == "C1" and "git ls-files failed" in i["message"] for i in run.data()["infra"]), run.show()


def test_exit_2_outranks_exit_1_and_keeps_the_drift_listed(tree):
    set_tools_block(tree, READ_ONLY, "tools: {Read: true}\n")  # infrastructure
    set_model(tree, OTHER_READ_ONLY, "opus")  # drift
    run = tree.check()
    assert run.code == 2, run.show()
    data = run.data()
    assert data["status"] == "infra"
    assert [i["check_id"] for i in data["infra"]] == ["C2"]
    assert [(v["check_id"], v["file"]) for v in data["violations"]] == [("C3", agent_path(OTHER_READ_ONLY))]


# =============================================================================
# C5: commands
# =============================================================================

RISK_SCORE = command_path("risk-score")
ARCHITECTURE = command_path("architecture")

COMMAND_RED = [
    pytest.param(
        lambda t: t.replace(RISK_SCORE, "---\ndescription:", "---\nallowed-tools: Bash\ndescription:"),
        [Want("C5", RISK_SCORE, "frontmatter keys ['allowed-tools', 'description'] differ from the section 8 row ['description']")],
        id="key-added",
    ),
    pytest.param(
        lambda t: drop_line(t, ARCHITECTURE, "description:"),
        [Want("C5", ARCHITECTURE, "frontmatter keys [] differ from the section 8 row ['description']")],
        id="key-removed",
    ),
    pytest.param(
        lambda t: t.write(RISK_SCORE, "## No frontmatter at all\n"),
        [Want("C5", RISK_SCORE, "frontmatter keys [] differ from the section 8 row ['description']")],
        id="frontmatter-removed",
    ),
    pytest.param(
        lambda t: plant(t, command_path("extra"), "---\ndescription: a new command\n---\n"),
        [Want("C5", command_path("extra"), "has no row in the section 8 commands table")],
        id="command-file-without-a-row",
    ),
    pytest.param(
        lambda t: t.path(ARCHITECTURE).unlink(),
        [Want("C5", MATRIX, "section 8 row /tachi.architecture has no command file matching")],
        id="matrix-row-without-a-file",
    ),
]


@pytest.mark.parametrize("mutate, wants", COMMAND_RED)
def test_command_drift_is_red(tree, mutate, wants):
    mutate(tree)
    assert_red(tree, wants)


# =============================================================================
# C6: shell command families
# =============================================================================

ORCH = agent_path(ORCHESTRATOR)

BASH_RED = [
    # chaining: each separator starts a new command whose family has to be allowed
    pytest.param(fenced("python3 x.py && " + CURL), ["command family 'curl'"], id="chained-with-and"),
    pytest.param(fenced("python3 x.py || " + CURL), ["command family 'curl'"], id="chained-with-or"),
    pytest.param(fenced("python3 x.py ; " + CURL), ["command family 'curl'"], id="chained-with-semicolon"),
    pytest.param(fenced("python3 x.py | " + CURL), ["command family 'curl'"], id="piped-into"),
    pytest.param(fenced("python3 x.py & " + CURL), ["command family 'curl'"], id="backgrounded-then"),
    pytest.param(fenced("python3 x.py |& " + CURL), ["command family 'curl'"], id="piped-with-stderr-into"),
    pytest.param(fenced("python3 x.py \\", "  && " + CURL), ["command family 'curl'"], id="continuation-line-is-joined"),
    # a prefix does not hide the family
    pytest.param(fenced("FOO=bar " + CURL), ["command family 'curl'"], id="env-prefixed"),
    pytest.param(fenced("A=1 python3 x.py && B=2 " + CURL), ["command family 'curl'"], id="env-prefixed-after-a-separator"),
    # every fence shape and label the guard scans
    pytest.param("   ```bash\n   " + CURL + "\n   ```\n", ["command family 'curl'"], id="fence-indented-3-spaces"),
    pytest.param("        ```bash\n        " + CURL + "\n        ```\n", ["command family 'curl'"], id="fence-indented-8-spaces"),
    pytest.param("\t```bash\n\t" + CURL + "\n\t```\n", ["command family 'curl'"], id="fence-indented-tab"),
    pytest.param("- ```bash\n  " + CURL + "\n  ```\n", ["command family 'curl'"], id="fence-in-a-list-item"),
    pytest.param("> ```bash\n> " + CURL + "\n> ```\n", ["command family 'curl'"], id="fence-in-a-blockquote"),
    pytest.param("~~~bash\n" + CURL + "\n~~~\n", ["command family 'curl'"], id="fence-with-tildes"),
    pytest.param(fenced(CURL, label="sh"), ["command family 'curl'"], id="label-sh"),
    pytest.param(fenced(CURL, label="shell"), ["command family 'curl'"], id="label-shell"),
    pytest.param(fenced(CURL, label="zsh"), ["command family 'curl'"], id="label-zsh"),
    pytest.param(fenced(CURL, label="Bash"), ["command family 'curl'"], id="label-capitalised"),
    # constructs that are red whatever they run
    pytest.param(fenced("python3 x.py $(cat /etc/passwd)"), ["command substitution $("], id="command-substitution"),
    pytest.param(fenced('python3 x.py "$(cat /etc/passwd)"'), ["command substitution $("], id="command-substitution-in-double-quotes"),
    pytest.param(fenced("python3 x.py `id`"), ["backtick command substitution"], id="backticks"),
    pytest.param(fenced("python3 x.py <(cat /etc/passwd)"), ["process substitution <("], id="process-substitution"),
    pytest.param(fenced('eval "$CMD"'), ["eval is not allowed"], id="eval"),
    pytest.param(fenced("bash -c 'python3 x.py'"), ["bash -c (inline shell evaluation)"], id="bash-c"),
    pytest.param(fenced("sh -c 'python3 x.py'"), ["sh -c (inline shell evaluation)"], id="sh-c"),
    pytest.param(fenced("python3 x.py | xargs python3"), ["xargs is not allowed"], id="xargs"),
    # a line that cannot be read is red, never skipped
    pytest.param(fenced("python3 x.py 'unterminated"), ["cannot tokenize the command line"], id="unterminated-quote"),
    # reserved words are skipped, so the next word is the family
    pytest.param(fenced("if [ -f x ]; then python3 y.py; fi"), ["command family '['"], id="reserved-words-then-bracket"),
    pytest.param(
        fenced("if [ -f x ]; then " + CURL + "; fi"), ["command family '['", "command family 'curl'"],
        id="reserved-words-then-curl",
    ),
    # an unquoted | is a pipe
    pytest.param(
        fenced("grep -E a|b notes.txt"), ["command family 'grep'", "command family 'b'"], id="unquoted-pipe-splits",
    ),
]


@pytest.mark.parametrize("block, needles", BASH_RED)
def test_shell_fence_drift_is_red(tree, block, needles):
    tree.append(ORCH, block)
    assert_red(tree, [Want("C6", ORCH, needle) for needle in needles])


@pytest.mark.parametrize("stem", BASH_AGENTS)
def test_every_bash_capable_agent_is_scanned(tree, stem):
    tree.append(agent_path(stem), fenced("python3 x.py && " + CURL))
    assert_red(tree, [Want("C6", agent_path(stem), "command family 'curl'")])


def test_an_agent_that_gains_bash_is_scanned_against_its_empty_families_cell(tree):
    add_tool(tree, READ_ONLY, "Bash")
    tree.append(TAMPERING, fenced("echo hello"))
    assert_red(tree, [
        Want("C2", TAMPERING, "(added ['Bash'], removed [])"),
        Want("C6", TAMPERING, "command family 'echo'"),
    ])


BASH_GREEN = [
    pytest.param(ORCHESTRATOR, fenced("LANG=C python3 x.py --flag 'a b'"), id="env-prefixed-allowed-family"),
    pytest.param(ORCHESTRATOR, fenced("python3 x.py \\", "  " + CURL), id="continuation-line-is-an-argument-not-a-command"),
    pytest.param(ORCHESTRATOR, fenced(CURL, label=""), id="unlabelled-fence-is-out-of-scope"),
    pytest.param(ORCHESTRATOR, fenced(CURL, label="text"), id="text-fence-is-out-of-scope"),
    pytest.param(READ_ONLY, fenced(CURL), id="read-only-agent-fence-is-not-scanned"),
    pytest.param(INFOGRAPHIC, fenced('if [ -n "$X" ]; then echo ok; fi'), id="reserved-words-with-allowed-bracket-and-echo"),
    pytest.param(INFOGRAPHIC, fenced("echo 'a|b'"), id="single-quoted-pipe"),
    pytest.param(INFOGRAPHIC, fenced('echo "a && b ; c | d"'), id="operators-inside-double-quotes"),
    pytest.param(INFOGRAPHIC, fenced("echo ';' '|' '&' curl"), id="lone-quoted-operators-are-data"),
    pytest.param(INFOGRAPHIC, fenced("echo \\; curl"), id="lone-escaped-semicolon-is-data"),
]


@pytest.mark.parametrize("stem, block", BASH_GREEN)
def test_shell_fences_that_stay_green(tree, stem, block):
    tree.append(agent_path(stem), block)
    assert_green(tree)


CRLF_FENCES = [
    pytest.param(fenced("python3 x.py \\", "  " + CURL), [], id="continuation-still-joins"),
    pytest.param(
        fenced("python3 x.py && " + CURL), [Want("C6", ORCH, "command family 'curl'")], id="fence-still-scanned"
    ),
]


@pytest.mark.parametrize("block, wants", CRLF_FENCES)
def test_a_crlf_bash_agent_file_is_scanned_like_an_lf_one(tree, block, wants):
    tree.append(ORCH, block)
    tree.write(ORCH, tree.read(ORCH).replace("\n", "\r\n"))
    if wants:
        assert_red(tree, wants)
    else:
        assert_green(tree)


def test_reserved_words_are_skipped_and_the_bracket_is_the_family(tree, pristine):
    tree.append(ORCH, fenced("if [ -f x ]; then python3 y.py; fi"))
    data = assert_red(tree, [Want("C6", ORCH, "command family '['")])
    before = set(pristine.summary["bash_families"]["tachi-orchestrator"]["found"])
    found = set(data["bash_families"]["tachi-orchestrator"]["found"])
    assert found - before == {"["}  # not if, then or fi


def test_a_quoted_pipe_regex_stays_one_token(tree, pristine):
    allow_bash_family(tree, ORCHESTRATOR, "grep")  # so that only the quoting decides
    tree.append(ORCH, fenced("grep -E 'a|b' notes.txt"))
    data = assert_green(tree)
    before = set(pristine.summary["bash_families"]["tachi-orchestrator"]["found"])
    assert set(data["bash_families"]["tachi-orchestrator"]["found"]) - before == {"grep"}  # no second command "b"


def test_the_same_regex_unquoted_is_a_pipe_and_red(tree):
    allow_bash_family(tree, ORCHESTRATOR, "grep")
    tree.append(ORCH, fenced("grep -E a|b notes.txt"))
    assert_red(tree, [Want("C6", ORCH, "command family 'b'")])


# =============================================================================
# C7: write locations
# =============================================================================

THREATS_SARIF = "`{out}/threats.sarif`"


def omit_from_runbook(tree: Tree) -> None:
    drop_row(tree, RUNBOOK, THREATS_SARIF)


def list_in_runbook(tree: Tree) -> None:
    insert_row_after(tree, RUNBOOK, THREATS_SARIF, "| `{out}/extra.txt` | someone | always |")


def repeat_in_runbook(tree: Tree) -> None:
    insert_row_after(tree, RUNBOOK, THREATS_SARIF, f"| {THREATS_SARIF} | `tachi-orchestrator` | always |")


def add_to_a_writes_cell(tree: Tree) -> None:
    edit_cells(tree, MATRIX, "`tachi-tampering`", set_cell(5, "`{out}/tamper.txt`"))


def omit_from_section_8_5(tree: Tree) -> None:
    drop_row(tree, MATRIX, THREATS_SARIF)


WRITES_RED = [
    pytest.param(
        omit_from_runbook,
        [Want("C7", RUNBOOK, "runbook section 5 omits path '{out}/threats.sarif'")], id="runbook-row-dropped",
    ),
    pytest.param(
        list_in_runbook,
        [Want("C7", RUNBOOK, "runbook section 5 lists path '{out}/extra.txt' that no section 8 Writes cell contains")],
        id="runbook-row-added",
    ),
    pytest.param(
        repeat_in_runbook,
        [Want("C7", RUNBOOK, "lists path '{out}/threats.sarif' more than once")], id="runbook-row-repeated",
    ),
    pytest.param(
        add_to_a_writes_cell,
        [Want("C7", RUNBOOK, "runbook section 5 omits path '{out}/tamper.txt'"),
         Want("C7", MATRIX, "section 8.5 canonical list omits path '{out}/tamper.txt'")],
        id="writes-cell-gains-a-path",
    ),
    pytest.param(
        omit_from_section_8_5,
        [Want("C7", MATRIX, "section 8.5 canonical list omits path '{out}/threats.sarif'")], id="section-8-5-row-dropped",
    ),
]


@pytest.mark.parametrize("mutate, wants", WRITES_RED)
def test_write_location_drift_is_red(tree, mutate, wants):
    mutate(tree)
    assert_red(tree, wants)


# =============================================================================
# C8: the self-test
# =============================================================================


EVIL = f"{AGENTS}/Evil.md"  # sorts before every lower-case file name
SELF_TEST_UNLISTED = f"{AGENTS}/_selftest-unlisted.md"  # the file the self-test's own M3 plants


class Drifted(NamedTuple):
    """What the self-test makes of a drifted tree.

    ``wants`` are the findings the drift itself causes (exactly those checks are red).
    ``already_red`` are the mutations whose expected finding the tree already had: they add nothing
    new, so the guard reports them as already red (not as having failed to fail).
    """

    wants: List[Want]
    already_red: List[str]


def real_agent_paths(root: Path) -> List[str]:
    """Repo-relative paths of the agent files a clean tree has: every ``.md`` bar the allow-listed one."""
    return sorted(f"{AGENTS}/{p.name}" for p in (root / AGENTS).glob("*.md") if p.name != ALLOW_LISTED)


def drift_the_m1_target(tree: Tree) -> Drifted:
    first = tree.check("--self-test")
    assert first.code == 0, first.show()
    target = re.search(r"added to (tachi-[\w-]+)", first.data()["self_test_detail"][0]["mutation"]).group(1)
    stem = target.replace("tachi-", "", 1)
    add_tool(tree, stem, "WebFetch")  # drift the very agent M1 would mutate
    return Drifted([Want("C2", agent_path(stem), "(added ['WebFetch'], removed [])")], [])


def plant_an_unlisted_agent_that_sorts_first(tree: Tree) -> Drifted:
    # No section 8 row, so C2 can never fire for it: M1 must not pick it just because it sorts first.
    assert EVIL < real_agent_paths(tree.root)[0], "Evil.md must sort before every real agent, or this proves nothing"
    plant(tree, EVIL, agent_text("helper"))
    return Drifted(
        [Want("C1", EVIL, "does not start with 'tachi-'"),
         Want("C1", EVIL, "has no row in the section 8 agents table")],
        [],
    )


def plant_frontmatter_in_the_allow_listed_document(tree: Tree) -> Drifted:
    # The document sorts before every real agent and now parses as one without a row. M5 plants the
    # very thing that is already there, so it can add no finding: it is already red.
    assert DOC < real_agent_paths(tree.root)[0], "the allow-listed document must sort first, or this proves nothing"
    plant_in_doc(lambda text: text)(tree)
    return Drifted(
        [Want("C1", DOC, "allow-listed document has leading frontmatter"),
         Want("C1", DOC, "agent 'tachi-planted-doc' has no row")],
        ["M5"],
    )


def plant_the_file_the_self_test_plants(tree: Tree) -> Drifted:
    plant(tree, SELF_TEST_UNLISTED, "# Not an agent and not on the allow-list\n")  # M3 writes this same file
    return Drifted(
        [Want("C1", SELF_TEST_UNLISTED, ".md file without frontmatter that is not on the allow-list")],
        ["M3"],
    )


DRIFTED_TREES = [
    pytest.param(drift_the_m1_target, id="tool-added-to-the-m1-target"),
    pytest.param(plant_an_unlisted_agent_that_sorts_first, id="unlisted-agent-sorting-before-every-real-agent"),
    pytest.param(plant_frontmatter_in_the_allow_listed_document, id="allow-listed-document-already-has-frontmatter"),
    pytest.param(plant_the_file_the_self_test_plants, id="file-already-named-like-a-self-test-mutation"),
]


@pytest.mark.parametrize("drift", DRIFTED_TREES)
def test_self_test_stays_valid_on_a_drifted_tree(tree, pristine, drift):
    drifted = drift(tree)
    run = tree.check("--self-test")
    # the drift is exit 1 and is listed; the self-test never turns it into exit 2 (a guard failure)
    assert run.code == 1, run.show()
    data = run.data()
    assert data["status"] == "drift" and data["self_test"] == "pass", run.show()
    assert data["infra"] == [] and run.err == "", run.show()
    assert_wants(data, drifted.wants)
    detail = data["self_test_detail"]
    assert [d["id"] for d in detail] == ["M1", "M2", "M3", "M4", "M5"], run.show()
    # every mutation is detected, or its expected finding was already red; none failed to fail
    unproven = [d for d in detail if not d["detected"]]
    assert [d["id"] for d in unproven] == drifted.already_red, run.show()
    assert all(d["already_red"] for d in unproven), run.show()
    # M1 acts on a real agent that has a section 8 row and no finding of its own
    m1_file = detail[0]["expected_file"]
    assert m1_file in real_agent_paths(pristine.root), run.show()
    assert m1_file not in {v["file"].split(":")[0] for v in data["violations"]}, run.show()


@pytest.mark.parametrize("drift", DRIFTED_TREES)
def test_self_test_on_a_drifted_tree_reads_as_drift_in_the_human_output(tree, drift):
    drifted = drift(tree)
    run = tree.run("--self-test")  # the exact command the CI workflow runs
    assert run.code == 1, run.show()
    lines = run.out.splitlines()
    assert f"{PREFIX} RESULT: drift (exit 1)" in lines, run.show()
    assert any(line.startswith(f"{PREFIX} C8 self-test") and line.endswith("PASS") for line in lines), run.show()
    assert run.err == "", run.show()  # no "ERROR C8" line sends the reviewer to the guard instead of the PR
    mutation_lines = [line for line in lines if line.startswith(f"{PREFIX} C8 M")]
    assert [line.split()[2] for line in mutation_lines] == ["M1", "M2", "M3", "M4", "M5"], run.show()
    assert not any("NOT DETECTED" in line for line in mutation_lines), run.show()
    assert [line.split()[2] for line in mutation_lines if "already red in " in line] == drifted.already_red, run.show()
    # the drift itself is listed, one FAIL line per finding
    for w in drifted.wants:
        assert any(
            line.startswith(f"{PREFIX} FAIL {w.check} {w.file}: ") and w.text in line for line in lines
        ), f"no FAIL line for {w}\n" + run.show()


def test_self_test_leaves_the_tree_it_checks_untouched(tree):
    before = digest(p for p in tree.root.rglob("*") if p.is_file())
    assert tree.run("--self-test").code == 0
    assert digest(p for p in tree.root.rglob("*") if p.is_file()) == before


def test_self_test_is_exit_2_when_no_agent_is_left_to_mutate(tree):
    for path in tree.path(AGENTS).glob("*.md"):
        if path.name != ALLOW_LISTED:
            path.unlink()
    run = tree.check("--self-test")
    assert run.code == 2, run.show()
    data = run.data()
    assert data["status"] == "infra" and data["self_test"] == "fail" and data["self_test_detail"] == []
    assert any(
        i["check_id"] == "C8" and "no agent with a section 8 row and a parsable tools" in i["message"]
        for i in data["infra"]
    )
    assert f"{PREFIX} ERROR C8" in run.err


BLIND = [
    pytest.param(("C1", "C2", "C3", "C4", "C5", "C6", "C7"), ["M1", "M2", "M3", "M4", "M5"], id="blind-to-everything"),
    pytest.param(("C2",), ["M1"], id="blind-to-c2-only-the-tool-add-escapes"),
    pytest.param(("C1",), ["M2", "M3", "M4", "M5"], id="blind-to-c1-the-four-roster-mutations-escape"),
]


@pytest.mark.parametrize("blind_to, escaped", BLIND)
def test_self_test_is_exit_2_when_a_mutation_fails_to_fail(tree, guard_module, monkeypatch, capsys, blind_to, escaped):
    real = guard_module.run_checks

    def blind(ctx):
        report = real(ctx)
        report.findings = [f for f in report.findings if f["check_id"] not in blind_to]
        return report

    # run_self_test calls run_checks by module-global name on the live tree and on every mutated copy
    monkeypatch.setattr(guard_module, "run_checks", blind)
    code = guard_module.main(["--repo-root", str(tree.root), "--self-test", "--json"])
    captured = capsys.readouterr()
    assert code == 2, captured.out + captured.err
    data = json.loads(captured.out)
    assert data["status"] == "infra" and data["self_test"] == "fail"
    assert [d["id"] for d in data["self_test_detail"] if not d["detected"]] == escaped
    assert sorted(i["file"] for i in data["infra"] if i["check_id"] == "C8") == sorted(
        d["expected_file"] for d in data["self_test_detail"] if not d["detected"]
    )
    for mutation_id in escaped:
        assert f"mutation {mutation_id} " in captured.err


def test_an_already_red_mutation_does_not_hide_a_blind_check_on_a_tree_that_is_red_elsewhere(
    tree, guard_module, monkeypatch, capsys
):
    # Two kinds of red on one tree. The allow-listed document already has frontmatter: M5 is already red.
    # M1's target is red in C3 (a model drift): the guard is red on that very file, so only the check id
    # tells "C2 was already red" (it was not) from "C2 failed to fire". A guard blind to C2 is still exit 2,
    # and the ERROR lines name the mutation that failed to fail (M1), not the one that was already red (M5).
    plant_in_doc(lambda text: text)(tree)
    set_model(tree, Path(real_agent_paths(tree.root)[0]).stem, "opus")
    real = guard_module.run_checks

    def blind_to_c2(ctx):
        report = real(ctx)
        report.findings = [f for f in report.findings if f["check_id"] != "C2"]
        return report

    monkeypatch.setattr(guard_module, "run_checks", blind_to_c2)
    code = guard_module.main(["--repo-root", str(tree.root), "--self-test", "--json"])
    captured = capsys.readouterr()
    assert code == 2, captured.out + captured.err
    data = json.loads(captured.out)
    assert data["status"] == "infra" and data["self_test"] == "fail"
    detail = {d["id"]: d for d in data["self_test_detail"]}
    assert [i for i, d in detail.items() if not d["detected"]] == ["M1", "M5"]
    assert detail["M1"]["already_red"] is False and detail["M5"]["already_red"] is True
    assert detail["M1"]["expected_file"] in {v["file"] for v in data["violations"]}  # red there, in C3
    assert [i["file"] for i in data["infra"] if i["check_id"] == "C8"] == [detail["M1"]["expected_file"]]
    assert "mutation M1 " in captured.err and "mutation M5 " not in captured.err


# =============================================================================
# Output contract
# =============================================================================


def mutate_every_check(tree: Tree) -> None:
    plant(tree, UNLISTED, "# stray\n")  # C1
    add_tool(tree, READ_ONLY, "Write")  # C2
    set_model(tree, OTHER_READ_ONLY, "opus")  # C3
    add_agent_key(tree, THIRD_READ_ONLY, "permissionMode: bypassPermissions")  # C4
    tree.replace(RISK_SCORE, "---\ndescription:", "---\nallowed-tools: Bash\ndescription:")  # C5
    tree.append(ORCH, fenced("python3 x.py && " + CURL))  # C6
    omit_from_runbook(tree)  # C7


CHECK_WORDS = {
    "C1": "roster", "C2": "tools", "C3": "model", "C4": "keyset", "C5": "command", "C6": "bash", "C7": "writes",
}


def test_json_lists_every_violation_with_its_check_id(tree, pristine):
    mutate_every_check(tree)
    run = tree.check()
    assert run.code == 1, run.show()
    data = run.data()
    assert data["status"] == "drift"
    seen: Dict[str, set] = {}
    for v in data["violations"]:
        assert set(v) == {"check_id", "check", "file", "message"}, v
        seen.setdefault(v["check_id"], set()).add(v["check"])
    assert seen == {cid: {word} for cid, word in CHECK_WORDS.items()}, listing(data["violations"])
    # the GuardResult drift list carries C2..C7 (the roster has its own section)
    assert {d["check_id"] for d in data["drift"]} == set(CHECK_WORDS) - {"C1"}
    for d in data["drift"]:
        assert d["check"] == CHECK_WORDS[d["check_id"]]
        assert {"agent", "expected", "actual", "file", "message"} <= set(d)
    assert data["roster"]["red"] == [UNLISTED]
    assert data["roster"]["agents"] == pristine.summary["roster"]["agents"]
    assert data["infra"] == []


def test_json_is_one_sorted_indented_document_on_stdout(tree):
    add_tool(tree, READ_ONLY, "Bash")
    run = tree.check()
    assert run.code == 1, run.show()
    assert run.out == json.dumps(json.loads(run.out), sort_keys=True, indent=2) + "\n"
    assert run.err == ""  # drift is reported on stdout only; stderr is for infrastructure errors


def test_json_infra_entries_carry_the_check_id(tree):
    set_tools_block(tree, READ_ONLY, "tools: {Read: true}\n")
    data = tree.check().data()
    assert data["status"] == "infra"
    assert [(i["check_id"], i["file"]) for i in data["infra"]] == [("C2", TAMPERING)]
    assert set(data["infra"][0]) == {"check_id", "file", "message"}


def test_human_output_for_drift(tree):
    add_tool(tree, READ_ONLY, "Bash")
    run = tree.run()
    assert run.code == 1, run.show()
    lines = run.out.splitlines()
    assert all(line.startswith(PREFIX) for line in lines), run.out
    assert any(line.startswith(f"{PREFIX} C2 tools") and "FAIL" in line for line in lines), run.out
    assert any(line.startswith(f"{PREFIX} FAIL C2 {TAMPERING}: tools differ") for line in lines), run.out
    assert f"{PREFIX} RESULT: drift (exit 1)" in lines
    assert any(line.startswith(f"{PREFIX} HINT") for line in lines)
    assert run.err == ""


def test_human_output_for_infrastructure(tree):
    set_tools_block(tree, READ_ONLY, "tools: {Read: true}\n")
    run = tree.run()
    assert run.code == 2, run.show()
    assert f"{PREFIX} RESULT: infra (exit 2)" in run.out.splitlines()
    assert run.err.startswith(f"{PREFIX} ERROR C2 {TAMPERING}: "), run.err
