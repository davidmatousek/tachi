"""Tests for scripts/archive-run-transcripts.py (feature 391, Part B1, task T033).

The archiver copies a finished Claude Code session verbatim to a place no commit
can reach, then writes ``run-manifest.json``: structured fields only, saying
which model served each agent, which tachi agents were dispatched at any depth
and what became of each dispatch, which hosts the tool calls named, which calls
were denied, and a hash of every archived file. These tests run it against the
two synthetic transcript generations under ``tests/fixtures/transcripts/`` and
against copies of them edited into the cases the committed files do not carry.

Inputs (what a change to any of them can break): this module,
``scripts/archive-run-transcripts.py``, ``tests/fixtures/transcripts/**`` and
``schemas/run-manifest.yaml`` (the schema cross-check only).

Isolation (hard): every test runs with ``HOME``, ``CLAUDE_CONFIG_DIR`` and
``--dest`` pointing into pytest's scratch directory, and an autouse fixture
removes every secret-named variable from the environment. No test resolves the
real ``~/.claude`` or ``~/.tachi``: the runner asserts that every path it hands
the archiver is inside the scratch directory and outside those two directories.

Layout of this module:

* harness: the world builder, the in-process runner, the editing helpers;
* both fixture generations: manifest facts, hash-equal archive, no-op re-archive;
* dispatch topology: depths 2 and 3, the four listing classes, P0B0-2 states;
* non-tachi instances (P0B0-1) and name agreement;
* parse-contract failures, each named, and what is tolerated;
* the refusal matrix, including the P0B0-5 incomplete-archive rule;
* secret handling: six planting sites, forced leaks, and the P0B0-11 floor;
* denial detection and the fail-closed version rule;
* roster, pins, version marker, output directory, discovery, exit code 2;
* the command line, stdlib-only and Python 3.9 guards, the schema cross-check;
* the T034 review: one regression group per finding.

Regression tests for the security review (T034): the last section, "T034 review", holds one group per
finding (H-1 to H-3, M-1 to M-4, L-1 to L-8) and the P0B0-11 amendments; their names start
``test_t034_<finding>_`` so one finding can be run alone (``-k t034_h1``). The three hostile-input bugs
found while writing this module (a Unicode-digit version, a timestamp whose offset overflows, a deeply
nested line) are fixed in the archiver and tested in "Parse contract".

Retuning: the secret-scan floor lives in ``FLOOR`` (one constant, section "P0B0-11 floor"); the key
formats live in ``LEAK_FORMATS`` (section "forced leaks"). Key-shaped dummy values are always
assembled at run time from fragments (ADR-042): this file holds no key-shaped
literal.
"""

from __future__ import annotations

import ast
import base64
import binascii
import datetime
import hashlib
import importlib.util
import itertools
import json
import os
import re
import shlex
import shutil
import stat
import string
import subprocess
import sys
import time
import urllib.parse
from collections import Counter
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "archive-run-transcripts.py"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "transcripts"
SCHEMA = REPO_ROOT / "schemas" / "run-manifest.yaml"

pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="the archiver relies on POSIX file modes, O_NOFOLLOW and symbolic links",
)

MANIFEST = "run-manifest.json"
MANIFEST_TMP = ".run-manifest.json.tmp"
ARCHIVE_GITIGNORE = ".gitignore"  # the archive's own ignore file (T034 H-1): not a copied source file
SYNTHETIC = "<synthetic>"
UNPARSEABLE = "<unparseable>"
PLACEHOLDER_PROJECT = "/__FIXTURE_PROJECT_DIR__"
PLACEHOLDER_KEY = "__DUMMY_KEY__"
STAMP = "2026-11-18T10:01:28.000Z"  # inside the fixtures' time range

# The archiver's amended name list (T034 M-2); the autouse fixture removes every match from the
# environment so a developer's or a runner's own variables can never change a result.
_SECRET_NAME_RE = re.compile(
    r"KEY|TOKEN|SECRET|PASSWORD|PASSWD|PASSPHRASE|PWD|CREDENTIAL|PRIVATE|AUTH|DSN|DATABASE_URL", re.IGNORECASE)
_GIT_LOCATION_VARS = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR", "GIT_PREFIX",
    "GIT_CEILING_DIRECTORIES", "GIT_NAMESPACE", "XDG_CONFIG_HOME",
)


def _passwd_home():
    """The real home directory, read once at import time and only ever used as a string to stay away from."""
    try:
        import pwd

        return pwd.getpwuid(os.getuid()).pw_dir
    except (ImportError, KeyError):
        return os.path.expanduser("~")


REAL_HOME = os.path.realpath(_passwd_home())
FORBIDDEN_STATE_DIRS = (os.path.join(REAL_HOME, ".claude"), os.path.join(REAL_HOME, ".tachi"))


def _inside(path, root):
    real = os.path.realpath(str(path))
    return real == root or real.startswith(root + os.sep)


def _is_forbidden_state(path):
    real = os.path.realpath(str(path))
    return any(real == d or real.startswith(d + os.sep) for d in FORBIDDEN_STATE_DIRS)


def _git_marker_above(path):
    current = path
    while True:
        if os.path.lexists(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


# =============================================================================
# What the committed fixtures contain (tests/fixtures/transcripts/README.md)
# =============================================================================

GENERATIONS = {
    "gen1": {
        "number": 1,
        "session": "11111111-1111-4111-8111-111111111111",
        "version": "2.1.282",
        "dispatch_tool": "Task",
        "main_model": "claude-opus-5",
        "sub_model": "claude-sonnet-5",
        "mode": "acceptEdits",
        "tachi_version": "unknown",
        "turns": {  # role -> (turns, synthetic turns)
            "orchestrator": (10, 1), "spoofing": (2, 0), "tampering": (3, 0),
            "threat-report": (4, 0), "attack-tree-delta": (2, 0), "general-purpose": (3, 0),
        },
    },
    "gen2": {
        "number": 2,
        "session": "22222222-2222-4222-8222-222222222222",
        "version": "2.1.328",
        "dispatch_tool": "Agent",
        "main_model": "claude-opus-5-5",
        "sub_model": "claude-sonnet-5-5",
        "mode": "auto",
        "tachi_version": "v4.49.0-3-gabc1234",
        "turns": {
            "orchestrator": (6, 1), "spoofing": (2, 0), "tampering": (3, 0),
            "threat-report": (3, 0), "attack-tree-delta": (2, 0), "general-purpose": (3, 0),
        },
    },
}
GEN_IDS = sorted(GENERATIONS)

# role -> (agent type, agent number, parent role, spawn depth)
ROLES = {
    "orchestrator": ("tachi-orchestrator", 1, "main", 1),
    "spoofing": ("tachi-spoofing", 2, "orchestrator", 2),
    "tampering": ("tachi-tampering", 3, "orchestrator", 2),
    "threat-report": ("tachi-threat-report", 4, "orchestrator", 2),
    "attack-tree-delta": ("tachi-attack-tree-delta", 5, "threat-report", 3),
    "general-purpose": ("general-purpose", 6, "threat-report", 3),
}
# dispatch key -> the tool_use id suffix (toolu_fx<N>_<suffix>) of the call that starts it
DISPATCH_IDS = {
    "orchestrator": "main_01", "spoofing": "orch_01", "tampering": "orch_02",
    "tool-abuse": "orch_03", "info-disclosure": "orch_04", "threat-report": "orch_05",
    "attack-tree-delta": "rep_01", "general-purpose": "rep_02",
}
ROSTER = (
    "attack-tree-delta", "denial-of-service", "info-disclosure", "misinformation", "model-theft",
    "orchestrator", "privilege-escalation", "repudiation", "spoofing", "tampering",
    "threat-report", "tool-abuse",
)
NOT_DISPATCHED = (
    "tachi-denial-of-service", "tachi-misinformation", "tachi-model-theft",
    "tachi-privilege-escalation", "tachi-repudiation",
)


# =============================================================================
# Fixtures: the module under test and the isolation guard
# =============================================================================


@pytest.fixture(scope="session")
def archiver():
    spec = importlib.util.spec_from_file_location("archive_run_transcripts_under_test", str(SCRIPT))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def scratch_root(tmp_path_factory):
    root = os.path.realpath(str(tmp_path_factory.getbasetemp()))
    marker = _git_marker_above(root)
    if marker is not None:
        pytest.fail(
            "the pytest scratch directory %s lies inside a git work tree (%s); the refusal tests "
            "need a scratch directory outside any work tree: run pytest with --basetemp elsewhere"
            % (root, marker), pytrace=False)
    if _is_forbidden_state(root):
        pytest.fail("the pytest scratch directory %s lies inside ~/.claude or ~/.tachi" % root, pytrace=False)
    return root


@pytest.fixture(autouse=True)
def isolated_environment(tmp_path, monkeypatch, scratch_root, archiver):
    """HOME and CLAUDE_CONFIG_DIR into scratch, no secret-named variables, nothing validated."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "claude-config-unused"))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    for name in _GIT_LOCATION_VARS:
        monkeypatch.delenv(name, raising=False)
    for name in list(os.environ):
        if _SECRET_NAME_RE.search(name):
            monkeypatch.delenv(name, raising=False)
    # The baseline is "no Claude Code version has a recorded-run denial check"; tests that
    # need a validated version say so explicitly. The synthetic fixtures never populate it.
    monkeypatch.setattr(archiver, "VALIDATED_DENIAL_VERSIONS", frozenset())
    assert os.path.realpath(os.path.expanduser("~")) == os.path.realpath(str(home)), "HOME is not the scratch home"
    assert _inside(home, scratch_root) and not _is_forbidden_state(home)
    return home


# =============================================================================
# The world: a copy of one fixture generation, ready to run against
# =============================================================================


class World(object):
    """A copy of ``synthetic-genN`` with the placeholders filled in and every file aged."""

    def __init__(self, base, gen, project_name="project"):
        spec = GENERATIONS[gen]
        self.gen = gen
        self.spec = spec
        self.number = spec["number"]
        self.session_id = spec["session"]
        self.root = base / ("world-" + gen)
        self.dest = base / ("out-" + gen) / "archive"
        self.config_dir = self.root / "claude-config"
        self.project_dir = self.root / project_name
        self.slug_dir = self.config_dir / "projects" / "-fixture-project"
        self.main_path = self.slug_dir / (self.session_id + ".jsonl")
        self.session_dir = self.slug_dir / self.session_id
        self.sub_dir = self.session_dir / "subagents"
        self.results_dir = self.session_dir / "tool-results"
        self._ids = itertools.count(1)

    # -- names -------------------------------------------------------------
    def agent_id(self, role_or_number):
        number = ROLES[role_or_number][1] if isinstance(role_or_number, str) else role_or_number
        return "a%df%014d" % (self.number, number)

    def dispatch_id(self, key):
        return "toolu_fx%d_%s" % (self.number, DISPATCH_IDS[key])

    def message_id(self):
        return "msg_tb_%03d" % next(self._ids)

    def instance_paths(self, agent_id):
        return (self.sub_dir / ("agent-%s.jsonl" % agent_id), self.sub_dir / ("agent-%s.meta.json" % agent_id))

    def role_paths(self, role):
        return self.instance_paths(self.agent_id(role))

    def transcripts(self):
        return [self.main_path] + sorted(self.sub_dir.glob("*.jsonl"))

    def source_tree(self):
        """relative posix path -> source file, for the main transcript and everything under the session directory."""
        files = {self.session_id + ".jsonl": self.main_path}
        for path in sorted(self.session_dir.rglob("*")):
            if path.is_file() and not path.is_symlink():
                files[path.relative_to(self.slug_dir).as_posix()] = path
        return files

    # -- files (every write keeps the file old, so the session never looks live) ----
    def age_file(self, path, seconds=3600):
        old = time.time() - seconds
        os.utime(str(path), (old, old))

    def age(self, seconds=3600):
        for path in sorted(self.config_dir.rglob("*")):
            if not path.is_symlink():
                self.age_file(path, seconds)

    def read_bytes(self, path):
        with open(str(path), "rb") as fh:
            return fh.read()

    def write_bytes(self, path, data):
        with open(str(path), "wb") as fh:
            fh.write(data)
        self.age_file(path)

    def read_text(self, path):
        return self.read_bytes(path).decode("utf-8")

    def write_text(self, path, text):
        self.write_bytes(path, text.encode("utf-8"))

    def read_json(self, path):
        return json.loads(self.read_text(path))

    def write_json(self, path, obj):
        self.write_text(path, json.dumps(obj, separators=(",", ":")))

    def read_jsonl(self, path):
        return [json.loads(line) for line in self.read_text(path).split("\n") if line.strip()]

    def write_jsonl(self, path, objs):
        self.write_text(path, "".join(json.dumps(o, separators=(",", ":")) + "\n" for o in objs))

    def edit_text(self, path, fn):
        self.write_text(path, fn(self.read_text(path)))


def build_world(base, gen, project_name="project"):
    """Copy a fixture generation and fill in the placeholders (the README's protocol)."""
    world = World(base, gen, project_name)
    shutil.copytree(str(FIXTURE_ROOT / ("synthetic-" + gen)), str(world.root))
    if project_name != "project":
        os.rename(str(world.root / "project"), str(world.project_dir))
    real_project = os.path.realpath(str(world.project_dir))
    for path in sorted(world.config_dir.rglob("*")):
        if not path.is_file():
            continue
        text = world.read_text(path)
        if PLACEHOLDER_PROJECT in text:
            filled = json.dumps(real_project)[1:-1] if path.suffix in (".jsonl", ".json") else real_project
            world.write_text(path, text.replace(PLACEHOLDER_PROJECT, filled))
    world.age()
    return world


@pytest.fixture(params=GEN_IDS)
def world(request, tmp_path):
    """Each fixture generation in turn."""
    return build_world(tmp_path, request.param)


@pytest.fixture
def gen2(tmp_path):
    return build_world(tmp_path, "gen2")


@pytest.fixture
def gen1(tmp_path):
    return build_world(tmp_path, "gen1")


# =============================================================================
# Editing helpers: turn a fixture copy into the case under test
# =============================================================================


def update_tool_uses(world, tool_use_id, fn):
    """Apply ``fn(block)`` to every tool_use block with this id, in every transcript."""
    found = False
    for path in world.transcripts():
        lines = world.read_jsonl(path)
        changed = False
        for obj in lines:
            msg = obj.get("message")
            if obj.get("type") == "assistant" and isinstance(msg, dict):
                for block in msg.get("content") or []:
                    if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("id") == tool_use_id:
                        fn(block)
                        changed = found = True
        if changed:
            world.write_jsonl(path, lines)
    assert found, "the fixture has no tool_use %s" % tool_use_id


def update_results(world, tool_use_id, fn):
    """Apply ``fn(block, line)`` to every tool_result block for this id."""
    found = False
    for path in world.transcripts():
        lines = world.read_jsonl(path)
        changed = False
        for obj in lines:
            msg = obj.get("message")
            content = msg.get("content") if isinstance(msg, dict) else None
            if obj.get("type") == "user" and isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result" and block.get("tool_use_id") == tool_use_id:
                        fn(block, obj)
                        changed = found = True
        if changed:
            world.write_jsonl(path, lines)
    assert found, "the fixture has no tool_result for %s" % tool_use_id


def drop_tool_result(world, tool_use_id):
    """Remove every tool_result for this id (and any user line left with no content)."""
    for path in world.transcripts():
        out = []
        for obj in world.read_jsonl(path):
            msg = obj.get("message")
            content = msg.get("content") if isinstance(msg, dict) else None
            if obj.get("type") == "user" and isinstance(content, list):
                kept = [b for b in content
                        if not (isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id") == tool_use_id)]
                if len(kept) != len(content):
                    if not kept:
                        continue
                    msg["content"] = kept
            out.append(obj)
        world.write_jsonl(path, out)


def set_dispatch_type(world, tool_use_id, new_type):
    update_tool_uses(world, tool_use_id, lambda block: block["input"].__setitem__("subagent_type", new_type))


def rename_instance_type(world, agent_id, new_type):
    """Give an instance a new agent type everywhere it is named: metadata, attribution, dispatch."""
    jsonl, meta_path = world.instance_paths(agent_id)
    meta = world.read_json(meta_path)
    old = meta["agentType"]
    meta["agentType"] = new_type
    world.write_json(meta_path, meta)
    lines = world.read_jsonl(jsonl)
    for obj in lines:
        if obj.get("attributionAgent") == old:
            obj["attributionAgent"] = new_type
    world.write_jsonl(jsonl, lines)
    set_dispatch_type(world, meta["toolUseId"], new_type)


def edit_lines(world, path, fn):
    """Apply ``fn(obj)`` to every JSON line of a transcript and write it back."""
    lines = world.read_jsonl(path)
    for obj in lines:
        fn(obj)
    world.write_jsonl(path, lines)


def assistant_lines(world, path):
    return [o for o in world.read_jsonl(path) if o.get("type") == "assistant"]


NO_DENIAL = object()


def append_tool_call(world, owner, name, tool_use_id, tool_input, result="ok", denial=NO_DENIAL, version=None):
    """Append one tool call to a transcript. ``owner`` is "main" or an agent id.

    ``result``: "ok", "error" or None (no tool_result anywhere). ``denial``: a toolDenialKind value
    (any JSON value, ``None`` included); ``NO_DENIAL`` writes no marker.
    """
    version = version or world.spec["version"]
    if owner == "main":
        path, model, attribution = world.main_path, world.spec["main_model"], None
    else:
        path = world.instance_paths(owner)[0]
        model = world.spec["sub_model"]
        attribution = world.read_json(world.instance_paths(owner)[1])["agentType"]
    lines = world.read_jsonl(path)
    call = {
        "type": "assistant", "version": version, "timestamp": STAMP,
        "message": {"id": world.message_id(), "type": "message", "role": "assistant", "model": model,
                    "content": [{"type": "tool_use", "id": tool_use_id, "name": name, "input": tool_input}]},
    }
    if attribution:
        call["attributionAgent"] = attribution
    lines.append(call)
    if result is not None:
        block = {"type": "tool_result", "tool_use_id": tool_use_id, "content": "FIXTURE: appended result"}
        if result == "error":
            block["is_error"] = True
        answer = {"type": "user", "version": version, "timestamp": STAMP,
                  "message": {"role": "user", "content": [block]}}
        if denial is not NO_DENIAL:
            answer["toolDenialKind"] = denial
        lines.append(answer)
    world.write_jsonl(path, lines)


def dispatch_input(subagent_type):
    return {"description": "FIXTURE: appended dispatch", "prompt": "FIXTURE prompt", "subagent_type": subagent_type}


def add_instance(world, agent_id, agent_type, tool_use_id, models=None, attribution="auto", version=None, meta_extra=None):
    """Write ``subagents/agent-<id>.jsonl`` and its metadata file; returns the transcript path.

    ``models``: one model id per assistant turn (``SYNTHETIC`` allowed; ``[]`` is a zero-turn instance).
    ``attribution``: the attributionAgent on each non-synthetic line ("auto" = the agent type, None = none).
    """
    version = version or world.spec["version"]
    models = [world.spec["sub_model"]] if models is None else models
    attr = agent_type if attribution == "auto" else attribution
    lines = [{"type": "user", "version": version, "timestamp": STAMP,
              "message": {"role": "user", "content": "FIXTURE: appended instance prompt"}}]
    for model in models:
        line = {"type": "assistant", "version": version, "timestamp": STAMP,
                "message": {"type": "message", "role": "assistant", "model": model,
                            "content": [{"type": "text", "text": "FIXTURE"}]}}
        if model != SYNTHETIC:
            line["message"]["id"] = world.message_id()
            if attr:
                line["attributionAgent"] = attr
        lines.append(line)
    jsonl, meta_path = world.instance_paths(agent_id)
    world.write_jsonl(jsonl, lines)
    meta = {"agentType": agent_type, "description": "FIXTURE: appended instance", "finished": True,
            "toolUseId": tool_use_id}
    meta.update(meta_extra or {})
    world.write_json(meta_path, meta)
    return jsonl


def add_dispatched_instance(world, owner, agent_id, agent_type, tool_use_id, call_name=None, **kwargs):
    """A dispatch in ``owner``'s transcript plus the instance it started."""
    append_tool_call(world, owner, call_name or world.spec["dispatch_tool"], tool_use_id, dispatch_input(agent_type))
    return add_instance(world, agent_id, agent_type, tool_use_id, **kwargs)


# =============================================================================
# The runner
# =============================================================================

DEFAULT = object()


class Outcome(object):
    def __init__(self, rc, out, err, summary, dest):
        self.rc = rc
        self.out = out
        self.err = err
        self.summary = summary
        self.dest = dest

    @property
    def text(self):
        return self.out + self.err

    @property
    def manifest_path(self):
        return None if self.dest is None else Path(self.dest) / MANIFEST

    def has_manifest(self):
        return self.manifest_path is not None and self.manifest_path.exists()

    def manifest(self):
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))


@pytest.fixture
def run(archiver, capsys, monkeypatch, scratch_root):
    """Call ``main()`` in-process: ``run(world, *extra_args, dest=..., latest=..., ...)`` returns an Outcome."""

    def _run(world, *extra, **kw):
        dest = kw.pop("dest", DEFAULT)
        latest = kw.pop("latest", False)
        session = kw.pop("session", None)
        project_dir = kw.pop("project_dir", None)
        config_dir = kw.pop("config_dir", None)
        output_dir = kw.pop("output_dir", None)
        json_summary = kw.pop("json_summary", True)
        env = kw.pop("env", None) or {}
        assert not kw, "unknown run() options: %s" % sorted(kw)
        for name, value in env.items():
            if value is None:
                monkeypatch.delenv(name, raising=False)
            else:
                monkeypatch.setenv(name, value)
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(config_dir or world.config_dir))
        dest_path = world.dest if dest is DEFAULT else dest
        argv = ["--latest"] if latest else ["--session", session or world.session_id]
        argv += ["--project-dir", str(project_dir or world.project_dir)]
        if dest_path is not None:
            argv += ["--dest", str(dest_path)]
        if output_dir is not None:
            argv += ["--output-dir", str(output_dir)]
        argv += [str(a) for a in extra]
        if json_summary:
            argv.append("--json")
        # The isolation guard: nothing the archiver is told about may be real state.
        for guarded in (os.environ["HOME"], os.environ["CLAUDE_CONFIG_DIR"], dest_path,
                        project_dir or world.project_dir, output_dir):
            if guarded is not None:
                assert _inside(guarded, scratch_root) and not _is_forbidden_state(guarded), \
                    "the test would touch %s outside the scratch directory" % guarded
        capsys.readouterr()
        try:
            rc = archiver.main(argv)
        except SystemExit as exc:  # argparse usage errors
            rc = exc.code if isinstance(exc.code, int) else 1
        captured = capsys.readouterr()
        summary = None
        if json_summary and captured.out.strip().startswith("{"):
            summary = json.loads(captured.out)
        archive = dest_path
        if summary and summary.get("archive_dir"):
            archive = summary["archive_dir"]
            assert _inside(archive, scratch_root) and not _is_forbidden_state(archive), \
                "the archiver wrote outside the scratch directory: %s" % archive
        return Outcome(rc, captured.out, captured.err, summary, None if archive is None else Path(archive))

    return _run


def run_subprocess(world, *extra, **kw):
    """The same command as a real process: ``python -I -B scripts/archive-run-transcripts.py``.

    ``isolated=False`` starts it the plain way (``python script``), which is what the isolation guard
    exists for; ``script`` runs another copy of the script; ``cwd`` and ``timeout`` as for subprocess.
    """
    python = kw.pop("python", sys.executable)
    dest = kw.pop("dest", world.dest)
    isolated = kw.pop("isolated", True)
    script = kw.pop("script", SCRIPT)
    cwd = kw.pop("cwd", None)
    timeout = kw.pop("timeout", 300)
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ["HOME"],
        "CLAUDE_CONFIG_DIR": str(world.config_dir),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    env.update(kw.pop("env", {}) or {})
    assert not kw, "unknown run_subprocess() options: %s" % sorted(kw)
    scratch = os.path.dirname(os.path.realpath(os.environ["HOME"]))  # this test's own scratch directory
    for guarded in (os.environ["HOME"], env["CLAUDE_CONFIG_DIR"], dest, world.project_dir):
        if guarded is not None:
            assert _inside(guarded, scratch) and not _is_forbidden_state(guarded), \
                "the test would touch %s outside the scratch directory" % guarded
    cmd = ([python, "-I", "-B"] if isolated else [python]) + [str(script)] + [str(a) for a in extra]
    if dest is not None:
        cmd += ["--dest", str(dest)]
    return subprocess.run(cmd, env=env, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, universal_newlines=True, timeout=timeout)


# =============================================================================
# Assertion helpers
# =============================================================================


def sha256_file(path):
    digest = hashlib.sha256()
    with open(str(path), "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def archived_tree(dest):
    """relative posix path -> sha256 for every file under ``dest``."""
    dest = Path(dest)
    return {p.relative_to(dest).as_posix(): sha256_file(p) for p in sorted(dest.rglob("*")) if p.is_file()}


def archive_content(dest):
    """Like ``archived_tree`` without the archiver's own two files: what must be hash-equal to the source."""
    tree = archived_tree(dest)
    assert tree.pop(ARCHIVE_GITIGNORE), "the archive has no .gitignore of its own"
    assert tree.pop(MANIFEST), "the archive has no manifest"
    return tree


def mode_of(path):
    return stat.S_IMODE(os.lstat(str(path)).st_mode)


def assert_ok(outcome):
    assert outcome.rc == 0, "exit %s; stderr: %s" % (outcome.rc, outcome.err)
    assert outcome.has_manifest(), "no manifest at %s" % outcome.manifest_path
    manifest = outcome.manifest()
    check_manifest_invariants(manifest)
    if outcome.summary is not None:
        assert outcome.summary["status"] in ("archived", "no-op")
    return manifest


def check_manifest_invariants(m):
    """Properties every manifest must have, whatever the session: checked on every successful run."""
    for entry in [m["main"]] + m["subagents"]:
        assert entry["served_model_histogram"], "an empty histogram reached a manifest"
        assert SYNTHETIC not in entry["served_model_histogram"]
        assert entry["turns"] == sum(entry["served_model_histogram"].values()) + entry["synthetic_turns"]
    ids = [s["agent_id"] for s in m["subagents"]]
    assert len(ids) == len(set(ids))
    order = [(s["spawn_depth"], s["agent_id"]) for s in m["subagents"]]
    assert order == sorted(order)
    keys = [(d["spawn_depth"], d["dispatched_from"], d["tool_use_id"]) for d in m["dispatches"]]
    assert keys == sorted(keys)
    assert [t["path"] for t in m["transcripts"]] == sorted(t["path"] for t in m["transcripts"])
    unrecorded = [(n["dispatched_from"], n["tool_use_id"]) for n in m["tachi_agents_not_recorded"]]
    assert unrecorded == sorted(unrecorded)
    assert m["tachi_agents_not_dispatched"] == sorted(m["tachi_agents_not_dispatched"])
    listed = dict((n["tool_use_id"], n) for n in m["tachi_agents_not_recorded"])
    for d in m["dispatches"]:
        if d["status"] == "recorded":
            assert d["tool_use_id"] not in listed
            owners = [s for s in m["subagents"] if s["parent_tool_use_id"] == d["tool_use_id"]]
            assert len(owners) == 1 and owners[0]["agent_type"] == d["agent"]
            assert owners[0]["spawn_depth"] == d["spawn_depth"]
        else:
            entry = listed[d["tool_use_id"]]
            assert entry["reason"] == {"dispatch-failed": "dispatch-failed", "not-recorded": "no-transcript"}[d["status"]]
            assert (entry["agent"], entry["dispatched_from"]) == (d["agent"], d["dispatched_from"])
    assert len(listed) == len(m["tachi_agents_not_recorded"]) == len([d for d in m["dispatches"] if d["status"] != "recorded"])
    depth = {"main": 0}
    depth.update((s["agent_id"], s["spawn_depth"]) for s in m["subagents"])
    for d in m["dispatches"]:
        if d["dispatched_from"] in depth:
            assert d["spawn_depth"] == depth[d["dispatched_from"]] + 1
    assert m["egress_unparsed_count"] == sum(e["count"] for e in m["egress_observed"] + m["egress_denied"]
                                              if e["host"] == UNPARSEABLE)
    detection = m["denial_detection"]
    seen = detection["validated_claude_code_versions"]
    assert seen == [v for v in m["claude_code_versions"] if v in seen]
    if detection["status"] == "validated":
        assert m["claude_code_versions"] and seen == m["claude_code_versions"]


def assert_failed(outcome, rc=1, mentions=(), keep_manifest=False):
    """A refused or failed run: the exit code, a [391] reason on stderr, and no manifest of any kind.

    ``keep_manifest``: the destination held a finished archive before this run, so its manifest is
    expected to be there still (the caller checks that it was not rewritten).
    """
    assert outcome.rc == rc, "expected exit %d, got %s; stderr: %s" % (rc, outcome.rc, outcome.err)
    assert outcome.err.startswith("[391] "), "stderr does not start with the [391] prefix: %r" % outcome.err[:80]
    if outcome.dest is not None:
        if not keep_manifest:
            assert not (Path(outcome.dest) / MANIFEST).exists(), "a manifest was written"
        assert not (Path(outcome.dest) / MANIFEST_TMP).exists(), "a temporary manifest was left behind"
    for text in mentions:
        assert text in outcome.err, "stderr does not mention %r: %s" % (text, outcome.err)


def by_type(entries, key="agent_type"):
    return {e[key]: e for e in entries}


def recount(world, path):
    """Independent recount of one transcript from the contract's definitions (a turn is one response)."""
    responses, idless, synthetic, calls, seen = {}, Counter(), 0, Counter(), set()
    for obj in world.read_jsonl(path):
        if obj.get("type") != "assistant":
            continue
        msg = obj["message"]
        if msg["model"] == SYNTHETIC:
            synthetic += 1
        elif msg.get("id"):
            responses.setdefault(msg["id"], msg["model"])
        else:
            idless[msg["model"]] += 1
        for block in msg.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use" and block["id"] not in seen:
                seen.add(block["id"])
                calls[block["name"]] += 1
    histogram = Counter(responses.values())
    histogram.update(idless)
    return dict(histogram), synthetic, dict(calls)


def parse_utc(text):
    """Strict ``YYYY-MM-DDTHH:MM:SSZ`` to an aware datetime (strptime: works on 3.9)."""
    return datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)


def _git_test_env():
    """Hermetic git environment for the tests' own git calls: no operator GIT_DIR / GIT_WORK_TREE."""
    env = {k: v for k, v in os.environ.items() if k not in _GIT_LOCATION_VARS}
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    return env


def git(*args, **kw):
    """Run ``git`` for a test; returns the CompletedProcess (text output). Options: ``cwd``, ``check``, ``input``."""
    feed = {"input": kw["input"]} if "input" in kw else {"stdin": subprocess.DEVNULL}
    return subprocess.run(["git"] + [str(a) for a in args], cwd=kw.get("cwd"), env=_git_test_env(),
                          check=kw.get("check", True), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True, **feed)


def committable(work_tree, git_dir=None):
    """Paths git would stage with ``git add -A`` (untracked and not ignored), minus the repo's own .gitignore."""
    args = ["--git-dir", git_dir, "--work-tree", work_tree] if git_dir else ["-C", work_tree]
    status = git(*(args + ["status", "--porcelain", "--untracked-files=all"])).stdout
    paths = [line[3:] for line in status.splitlines()]
    return [p for p in paths if p != ".gitignore"]


def init_repo(path, ignore=None):
    """``git init`` a work tree at ``path`` with an optional .gitignore (hermetic: HOME is scratch)."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True, stdin=subprocess.DEVNULL,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if ignore is not None:
        (path / ".gitignore").write_text(ignore, encoding="utf-8")
    return path


# =============================================================================
# Both fixture generations: manifest facts, hash-equal archive, no-op re-archive
# =============================================================================

EXPECTED_EGRESS = [
    {"host": "generativelanguage.googleapis.com", "tool": "Bash", "count": 1},
    {"host": "registry.example.test", "tool": "Bash", "count": 1},
]


def _fixture_time_range(world):
    stamps = []
    for path in world.transcripts():
        for obj in world.read_jsonl(path):
            stamp = obj.get("timestamp")
            if isinstance(stamp, str):
                stamps.append(datetime.datetime.strptime(stamp[:19], "%Y-%m-%dT%H:%M:%S"))
    return min(stamps), max(stamps)


def test_manifest_top_level_facts(world, run):
    out = run(world)
    manifest = assert_ok(out)
    spec = world.spec
    assert manifest["manifest_version"] == 1
    assert manifest["session_id"] == world.session_id
    assert manifest["tachi_version"] == spec["tachi_version"]
    assert manifest["claude_code_versions"] == [spec["version"]]
    assert manifest["permission_modes_seen"] == [spec["mode"]]
    low, high = _fixture_time_range(world)
    assert parse_utc(manifest["started_at"]).replace(tzinfo=None) == low.replace(microsecond=0)
    assert parse_utc(manifest["ended_at"]).replace(tzinfo=None) == high.replace(microsecond=0)
    archived = parse_utc(manifest["archived_at"])
    assert abs((datetime.datetime.now(datetime.timezone.utc) - archived).total_seconds()) < 120
    assert manifest["artifacts"] is None and manifest["artifacts_reason"] == "no-output-dir"
    assert manifest["egress_observed"] == EXPECTED_EGRESS
    assert manifest["egress_unparsed_count"] == 0
    assert manifest["egress_denied"] == [{"host": "example.com", "kind": "permission-rule", "count": 1}]
    assert manifest["denial_detection"] == {"status": "not-validated", "validated_claude_code_versions": []}
    assert manifest["tachi_agents_not_dispatched"] == list(NOT_DISPATCHED)
    # one successful dispatch left no transcript (the warning the fixtures carry); with no secret-named
    # variable in the environment the scan also says it ran on the key formats alone (T034 M-3)
    warnings = out.summary["warnings"]
    assert len(warnings) == 2
    assert "no subagent transcript" in warnings[0]
    assert warnings[1].startswith("secret scan: no secret-named environment value was available")
    assert out.summary["unknown_entry_types"] == {} and out.summary["unknown_assistant_keys"] == {}


def test_main_session_counts(world, run):
    manifest = assert_ok(run(world))
    main = manifest["main"]
    assert main["served_model_histogram"] == {world.spec["main_model"]: 4}
    assert main["synthetic_turns"] == 1
    assert main["turns"] == 5
    assert main["tool_calls_by_tool"] == {world.spec["dispatch_tool"]: 1, "WebFetch": 1, "Bash": 1}
    assert "pinned_model" not in main


def test_every_instance_matches_an_independent_recount(world, run):
    manifest = assert_ok(run(world))
    by_id = {s["agent_id"]: s for s in manifest["subagents"]}
    assert len(by_id) == 6
    for role, (turns, synthetic) in world.spec["turns"].items():
        inst = by_id[world.agent_id(role)]
        histogram, synth, calls = recount(world, world.role_paths(role)[0])
        assert inst["served_model_histogram"] == histogram
        assert inst["synthetic_turns"] == synth == synthetic
        assert inst["turns"] == turns == sum(histogram.values()) + synth
        assert inst["tool_calls_by_tool"] == calls
        assert inst["unknown_meta_keys"] == []
    histogram, synth, calls = recount(world, world.main_path)
    main = manifest["main"]
    assert (main["served_model_histogram"], main["synthetic_turns"], main["tool_calls_by_tool"]) == (histogram, synth, calls)
    for entry in [main] + manifest["subagents"]:
        assert entry["turns"] == sum(entry["served_model_histogram"].values()) + entry["synthetic_turns"]
        assert entry["served_model_histogram"], "an empty histogram reached a manifest"


def test_response_grouping_differs_between_the_generations(gen1, gen2, run):
    """gen1 has lines without a message.id (each is a turn); gen2 spreads one response over several lines."""
    one_line_each = [o for o in gen1.read_jsonl(gen1.role_paths("orchestrator")[0]) if o.get("type") == "assistant"]
    assert any(not o["message"].get("id") for o in one_line_each if o["message"]["model"] != SYNTHETIC)
    shared = Counter(o["message"].get("id") for o in gen2.read_jsonl(gen2.role_paths("orchestrator")[0])
                     if o.get("type") == "assistant" and o["message"]["model"] != SYNTHETIC)
    assert max(shared.values()) > 1
    for world in (gen1, gen2):
        manifest = assert_ok(run(world, dest=world.dest))
        orchestrator = by_type(manifest["subagents"])["tachi-orchestrator"]
        assert (orchestrator["turns"], orchestrator["synthetic_turns"]) == world.spec["turns"]["orchestrator"]


def test_transcripts_list_every_archived_file(world, run):
    out = run(world)
    manifest = assert_ok(out)
    listed = manifest["transcripts"]
    assert [t["path"] for t in listed] == sorted(t["path"] for t in listed)
    assert len(listed) == 15
    source = world.source_tree()
    assert {t["path"] for t in listed} == set(source)
    for entry in listed:
        assert set(entry) == {"path", "bytes", "sha256"}
        assert entry["sha256"] == sha256_file(source[entry["path"]])
        assert entry["bytes"] == os.path.getsize(str(source[entry["path"]]))
    assert out.summary["files"] == 15 and out.summary["bytes"] == sum(t["bytes"] for t in listed)


def test_archive_is_hash_equal_to_the_source(world, run):
    """Every copied source file is hash-equal to its source; the archiver's own .gitignore and manifest are the only others."""
    out = run(world)
    assert_ok(out)
    source = {rel: sha256_file(path) for rel, path in world.source_tree().items()}
    archive = archive_content(out.dest)
    assert archive == source, "the archive differs from the source tree"
    assert set(archived_tree(out.dest)) == set(source) | {MANIFEST, ARCHIVE_GITIGNORE}
    for rel in ("%s.jsonl" % world.session_id, "%s/tool-results/toolu_fx%d_orch_00.txt" % (world.session_id, world.number)):
        assert rel in archive


def test_archive_modes_are_owner_only(world, run):
    out = run(world)
    assert_ok(out)
    assert mode_of(out.dest) == 0o700
    assert mode_of(out.dest.parent) == 0o700, "a parent the archiver created must be owner-only too"
    for path in sorted(out.dest.rglob("*")):
        expected = 0o700 if path.is_dir() else 0o600
        assert mode_of(path) == expected, "%s has mode %o" % (path, mode_of(path))


def test_manifest_file_format(world, run):
    out = run(world)
    manifest = assert_ok(out)
    text = out.manifest_path.read_text(encoding="utf-8")
    assert text == json.dumps(manifest, sort_keys=True, indent=2) + "\n"
    assert mode_of(out.manifest_path) == 0o600
    assert sorted(p.name for p in out.dest.iterdir()) == sorted(
        [ARCHIVE_GITIGNORE, MANIFEST, world.session_id, world.session_id + ".jsonl"])


def test_every_manifest_string_is_one_short_token(world, run):
    """Structured fields only: no whitespace, no control characters, nothing long, no fixture free text."""
    manifest = assert_ok(run(world))
    strings = []

    def walk(node):
        if isinstance(node, str):
            strings.append(node)
        elif isinstance(node, dict):
            for key, value in node.items():
                strings.append(key)
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(manifest)
    assert strings
    for text in strings:
        assert re.match(r"[^\s\x00-\x1f\x7f]{1,128}\Z", text), "free text or an odd value in the manifest: %r" % text
        assert "FIXTURE" not in text


def test_session_and_latest_pick_the_same_transcript(world, run, tmp_path):
    first = assert_ok(run(world))
    second = run(world, latest=True, dest=tmp_path / "latest-out" / "archive")
    other = assert_ok(second)
    for manifest in (first, other):
        manifest.pop("archived_at")
    assert first == other


def test_reaching_the_same_session_twice_is_a_no_op(world, run):
    out = run(world)
    first = assert_ok(out)
    before = archived_tree(out.dest)
    stamps = {p: os.lstat(str(p)).st_mtime_ns for p in sorted(out.dest.rglob("*"))}
    again = run(world)
    assert again.rc == 0, again.err
    assert again.summary["status"] == "no-op"
    assert "nothing to do" in again.out or again.summary["status"] == "no-op"
    assert archived_tree(out.dest) == before, "a no-op run changed the archive"
    assert {p: os.lstat(str(p)).st_mtime_ns for p in sorted(out.dest.rglob("*"))} == stamps
    assert again.manifest() == first


def test_human_summary_line_without_json(world, run):
    out = run(world, json_summary=False)
    assert out.rc == 0
    assert out.out.startswith("[391] archived session %s to " % world.session_id)
    assert "(15 files, " in out.out
    again = run(world, json_summary=False)
    assert again.rc == 0 and "already archived" in again.out and "nothing to do" in again.out


# =============================================================================
# Dispatch topology: depths 2 and 3, the four listing classes, P0B0-2 states
# =============================================================================


def _aid(world, role_or_id):
    return world.agent_id(role_or_id) if role_or_id in ROLES else role_or_id


def owner_of_call(world, tool_use_id):
    """"main" or the agent id of the transcript that holds this tool_use (found by reading the files)."""
    for path in world.transcripts():
        for obj in assistant_lines(world, path):
            for block in obj["message"].get("content") or []:
                if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("id") == tool_use_id:
                    return "main" if path == world.main_path else path.stem[len("agent-"):]
    raise AssertionError("no transcript holds tool_use %s" % tool_use_id)


def make_zero_turn(world, role_or_id):
    """Strip every assistant line from an instance: it never ran."""
    path = world.instance_paths(_aid(world, role_or_id))[0]
    world.write_jsonl(path, [o for o in world.read_jsonl(path) if o.get("type") != "assistant"])


def mark_result_error(world, tool_use_id, error=True):
    def apply(block, _line):
        if error:
            block["is_error"] = True
        else:
            block.pop("is_error", None)

    update_results(world, tool_use_id, apply)


def expected_dispatches(world):
    rows = [
        ("orchestrator", "main", 1, "recorded"),
        ("spoofing", "orchestrator", 2, "recorded"),
        ("tampering", "orchestrator", 2, "recorded"),
        ("tool-abuse", "orchestrator", 2, "dispatch-failed"),
        ("info-disclosure", "orchestrator", 2, "not-recorded"),
        ("threat-report", "orchestrator", 2, "recorded"),
        ("attack-tree-delta", "threat-report", 3, "recorded"),
    ]
    return [{"agent": "tachi-" + key, "tool_use_id": world.dispatch_id(key),
             "dispatched_from": "main" if parent == "main" else world.agent_id(parent),
             "spawn_depth": depth, "status": status} for key, parent, depth, status in rows]


def test_dispatch_listing_at_every_depth(world, run):
    manifest = assert_ok(run(world))
    assert manifest["dispatches"] == expected_dispatches(world)
    depths = Counter(d["spawn_depth"] for d in manifest["dispatches"])
    assert depths == {1: 1, 2: 5, 3: 1}
    keys = [(d["spawn_depth"], d["dispatched_from"], d["tool_use_id"]) for d in manifest["dispatches"]]
    assert keys == sorted(keys)


@pytest.mark.parametrize("role", ["spoofing", "tampering", "threat-report", "attack-tree-delta", "general-purpose"])
def test_nested_dispatch_attribution_at_depths_2_and_3(world, run, role):
    """Each nested instance is attributed to the call that started it, in its dispatcher's own transcript."""
    manifest = assert_ok(run(world))
    agent_type, _number, parent_role, depth = ROLES[role]
    inst = {s["agent_id"]: s for s in manifest["subagents"]}[world.agent_id(role)]
    assert inst["agent_type"] == inst["attribution_agent"] == agent_type
    assert inst["spawn_depth"] == depth
    assert inst["parent_tool_use_id"] == world.dispatch_id(role)
    assert inst["pinned_model"] == ("sonnet" if agent_type.startswith("tachi-") else None)
    assert owner_of_call(world, inst["parent_tool_use_id"]) == world.agent_id(parent_role)
    # the chain up to main: every parent call sits in the transcript of the instance one level up
    owner, hops = world.agent_id(role), 0
    while owner != "main":
        meta = world.read_json(world.instance_paths(owner)[1])
        owner = owner_of_call(world, meta["toolUseId"])
        hops += 1
    assert hops == depth
    if agent_type.startswith("tachi-"):
        entry = [d for d in manifest["dispatches"] if d["tool_use_id"] == inst["parent_tool_use_id"]]
        assert len(entry) == 1
        assert entry[0]["agent"] == agent_type and entry[0]["status"] == "recorded"
        assert entry[0]["spawn_depth"] == depth
        assert entry[0]["dispatched_from"] == world.agent_id(parent_role)


def test_the_four_listing_classes(world, run):
    """recorded, dispatch-failed, no-transcript and not-dispatched, each listed and never inferred."""
    manifest = assert_ok(run(world))
    dispatches = manifest["dispatches"]
    recorded = sorted(d["agent"] for d in dispatches if d["status"] == "recorded")
    failed = [d for d in dispatches if d["status"] == "dispatch-failed"]
    unrecorded = [d for d in dispatches if d["status"] == "not-recorded"]
    assert recorded == sorted("tachi-" + k for k in
                              ("orchestrator", "spoofing", "tampering", "threat-report", "attack-tree-delta"))
    assert [d["agent"] for d in failed] == ["tachi-tool-abuse"]
    assert [d["agent"] for d in unrecorded] == ["tachi-info-disclosure"]
    listed = manifest["tachi_agents_not_recorded"]
    assert [(n["agent"], n["reason"]) for n in listed] == [("tachi-tool-abuse", "dispatch-failed"),
                                                           ("tachi-info-disclosure", "no-transcript")]
    for entry in listed:
        assert set(entry) == {"agent", "tool_use_id", "dispatched_from", "reason"}
        match = [d for d in dispatches if d["tool_use_id"] == entry["tool_use_id"]]
        assert len(match) == 1 and match[0]["dispatched_from"] == entry["dispatched_from"]
        assert (match[0]["status"], entry["reason"]) in (("dispatch-failed", "dispatch-failed"), ("not-recorded", "no-transcript"))
    # the instances behind the dispatch-failed and no-transcript calls do not exist as subagents
    assert not {"tachi-tool-abuse", "tachi-info-disclosure"} & {s["agent_type"] for s in manifest["subagents"]}
    assert manifest["tachi_agents_not_dispatched"] == list(NOT_DISPATCHED)
    named = {d["agent"] for d in dispatches}
    assert not named & set(manifest["tachi_agents_not_dispatched"])
    # the roster is the 12 installed stubs: dispatched or recorded + not dispatched = the roster
    assert len(named | set(manifest["tachi_agents_not_dispatched"])) == len(ROSTER)
    assert named | set(manifest["tachi_agents_not_dispatched"]) == {"tachi-" + r for r in ROSTER}


def test_the_dispatch_failed_call_and_the_no_transcript_call_differ_only_by_their_result(world, run):
    """Same shape, different outcome: an error result is dispatch-failed, a success is no-transcript."""
    failed, silent = world.dispatch_id("tool-abuse"), world.dispatch_id("info-disclosure")
    for tid, expected in ((failed, True), (silent, None)):
        seen = []
        update_results(world, tid, lambda block, _line: seen.append(block.get("is_error")))
        assert seen == [expected]
    manifest = assert_ok(run(world))
    status = {d["tool_use_id"]: d["status"] for d in manifest["dispatches"]}
    assert status[failed] == "dispatch-failed" and status[silent] == "not-recorded"


@pytest.mark.parametrize("change", ["wrong", "absent"])
def test_depth_comes_from_the_dispatch_chain_not_the_metadata(world, run, change):
    """The metadata spawnDepth is neither required nor cross-checked (P0B0-4(c))."""
    for role in ROLES:
        meta_path = world.role_paths(role)[1]
        meta = world.read_json(meta_path)
        if change == "wrong":
            meta["spawnDepth"] = 9
        else:
            meta.pop("spawnDepth", None)
        world.write_json(meta_path, meta)
    manifest = assert_ok(run(world))
    assert {s["agent_type"]: s["spawn_depth"] for s in manifest["subagents"]} == \
        {agent_type: depth for agent_type, _n, _p, depth in ROLES.values()}
    assert manifest["dispatches"] == expected_dispatches(world)


def test_a_depth_four_dispatch_is_followed(world, run):
    """Attribution follows dispatches at any depth, not only the two the fixtures carry."""
    deep = world.agent_id(7)
    add_dispatched_instance(world, world.agent_id("attack-tree-delta"), deep, "tachi-spoofing", "toolu_tb_depth4")
    manifest = assert_ok(run(world))
    row = [d for d in manifest["dispatches"] if d["tool_use_id"] == "toolu_tb_depth4"]
    assert row == [{"agent": "tachi-spoofing", "tool_use_id": "toolu_tb_depth4", "spawn_depth": 4,
                    "dispatched_from": world.agent_id("attack-tree-delta"), "status": "recorded"}]
    inst = {s["agent_id"]: s for s in manifest["subagents"]}[deep]
    assert (inst["spawn_depth"], inst["parent_tool_use_id"], inst["pinned_model"]) == (4, "toolu_tb_depth4", "sonnet")
    assert manifest["dispatches"][-1]["tool_use_id"] == "toolu_tb_depth4"


def test_legacy_task_and_current_agent_names_mix_in_one_session(world, run):
    """Both dispatch tool names are dispatches, whatever generation wrote them."""
    other = "Agent" if world.spec["dispatch_tool"] == "Task" else "Task"
    update_tool_uses(world, world.dispatch_id("spoofing"), lambda block: block.__setitem__("name", other))
    manifest = assert_ok(run(world))
    assert manifest["dispatches"] == expected_dispatches(world)
    calls = by_type(manifest["subagents"])["tachi-orchestrator"]["tool_calls_by_tool"]
    assert calls[other] == 1 and calls[world.spec["dispatch_tool"]] == 4


def test_a_call_naming_a_non_tachi_type_is_not_a_dispatch(world, run):
    """An Agent or Task call that names a non-tachi type (or none) never reaches a dispatch list."""
    orch = world.agent_id("orchestrator")
    tool = world.spec["dispatch_tool"]
    append_tool_call(world, orch, tool, "toolu_tb_helper_ok", dispatch_input("my-helper"), result="ok")
    append_tool_call(world, orch, tool, "toolu_tb_helper_err", dispatch_input("my-helper"), result="error")
    append_tool_call(world, orch, tool, "toolu_tb_helper_open", dispatch_input("general-purpose"), result=None)
    append_tool_call(world, orch, tool, "toolu_tb_untyped", {"description": "FIXTURE: no subagent_type"}, result="ok")
    manifest = assert_ok(run(world))
    assert manifest["dispatches"] == expected_dispatches(world)
    assert [n["agent"] for n in manifest["tachi_agents_not_recorded"]] == ["tachi-tool-abuse", "tachi-info-disclosure"]
    assert manifest["tachi_agents_not_dispatched"] == list(NOT_DISPATCHED)
    assert by_type(manifest["subagents"])["tachi-orchestrator"]["tool_calls_by_tool"][tool] == 9


# -- P0B0-2: the dispatch states and their fail-closed cases ----------------------------------


@pytest.mark.parametrize("role", ["tampering", "general-purpose"])
def test_p0b0_2_b_zero_turn_instance_with_an_errored_dispatch(world, run, role):
    """(b) never ran and the call errored: dispatch-failed, unlisted as a subagent, files still archived and hashed."""
    make_zero_turn(world, role)
    tid = world.dispatch_id(role)
    mark_result_error(world, tid)
    out = run(world)
    manifest = assert_ok(out)
    assert world.agent_id(role) not in {s["agent_id"] for s in manifest["subagents"]}
    assert len(manifest["subagents"]) == 5
    agent_type = ROLES[role][0]
    if agent_type.startswith("tachi-"):
        assert [d["status"] for d in manifest["dispatches"] if d["tool_use_id"] == tid] == ["dispatch-failed"]
        assert {"agent": agent_type, "tool_use_id": tid, "dispatched_from": world.agent_id(ROLES[role][2]),
                "reason": "dispatch-failed"} in manifest["tachi_agents_not_recorded"]
    else:
        assert tid not in {d["tool_use_id"] for d in manifest["dispatches"]}
        assert [n["agent"] for n in manifest["tachi_agents_not_recorded"]] == ["tachi-tool-abuse", "tachi-info-disclosure"]
    jsonl, meta = world.role_paths(role)
    listed = {t["path"]: t["sha256"] for t in manifest["transcripts"]}
    for path in (jsonl, meta):
        rel = path.relative_to(world.slug_dir).as_posix()
        assert listed[rel] == sha256_file(path) == archived_tree(out.dest)[rel]


@pytest.mark.parametrize("result", ["ok", "none"])
@pytest.mark.parametrize("role", ["tampering", "general-purpose"])
def test_p0b0_2_zero_turns_without_an_error_result_stays_a_failure(world, run, role, result):
    make_zero_turn(world, role)
    if result == "none":
        drop_tool_result(world, world.dispatch_id(role))
    assert_failed(run(world), mentions=("zero assistant turns",))


def test_p0b0_2_c_meta_naming_another_agent_than_the_call_exits_1(world, run):
    """(c) a name disagreement, never filed as "not recorded"."""
    jsonl, meta_path = world.role_paths("tampering")
    meta = world.read_json(meta_path)
    meta["agentType"] = "tachi-misinformation"
    world.write_json(meta_path, meta)
    edit_lines(world, jsonl, lambda o: o.__setitem__("attributionAgent", "tachi-misinformation")
               if o.get("attributionAgent") else None)
    assert_failed(run(world), mentions=("dispatched subagent_type",))


def test_p0b0_2_f_a_dispatch_with_no_result_anywhere_is_not_filed_as_a_failure(world, run):
    """(f) an unknown outcome (an interrupted or live session) is no-transcript, even where an error would have been listed."""
    drop_tool_result(world, world.dispatch_id("tool-abuse"))
    out = run(world)
    manifest = assert_ok(out)
    status = {d["agent"]: d["status"] for d in manifest["dispatches"]}
    assert status["tachi-tool-abuse"] == "not-recorded" and status["tachi-info-disclosure"] == "not-recorded"
    assert {n["agent"]: n["reason"] for n in manifest["tachi_agents_not_recorded"]} == \
        {"tachi-tool-abuse": "no-transcript", "tachi-info-disclosure": "no-transcript"}
    assert any("2 successful tachi dispatch" in w for w in out.summary["warnings"])


def test_a_successful_dispatch_with_no_meta_gives_no_transcript(world, run):
    """(e) the one class that trips the first trip-wire: exit 0, listed, never inferred, and a warning says so."""
    out = run(world)
    manifest = assert_ok(out)
    tid = world.dispatch_id("info-disclosure")
    assert not [p for p in world.sub_dir.glob("*.meta.json")
                if world.read_json(p)["toolUseId"] == tid], "the fixture must have no meta for this call"
    seen = []
    update_results(world, tid, lambda block, _line: seen.append(block.get("is_error")))
    assert seen == [None], "the dispatch must have succeeded"
    assert [d["status"] for d in manifest["dispatches"] if d["tool_use_id"] == tid] == ["not-recorded"]
    assert [n["reason"] for n in manifest["tachi_agents_not_recorded"] if n["tool_use_id"] == tid] == ["no-transcript"]
    assert "tachi-info-disclosure" not in {s["agent_type"] for s in manifest["subagents"]}
    assert "tachi-info-disclosure" not in manifest["tachi_agents_not_dispatched"], "it was dispatched, so it is not 'not dispatched'"
    assert out.summary["dispatch_counts"] == {"recorded": 5, "dispatch-failed": 1, "not-recorded": 1}
    assert out.err.startswith("[391] warning: 1 successful tachi dispatch(es) have no subagent transcript")
    assert "TW-B1" in out.err


@pytest.mark.parametrize("agent_type", ["tachi-repudiation", "my-helper"])
def test_p0b0_2_g_a_meta_matching_no_call_exits_1(world, run, agent_type):
    """(g) the topology cannot be established, for a tachi and a non-tachi instance alike."""
    add_instance(world, world.agent_id(8), agent_type, "toolu_tb_orphan")
    assert_failed(run(world), mentions=("Agent or Task call",))


def test_p0b0_2_g_a_meta_pointing_at_a_call_that_is_not_a_dispatch_exits_1(world, run):
    add_instance(world, world.agent_id(8), "tachi-repudiation", "toolu_fx%d_orch_06" % world.number)  # a Bash call
    assert_failed(run(world), mentions=("Agent or Task call",))


def test_a_subagent_transcript_without_a_meta_file_exits_1(world, run):
    world.role_paths("spoofing")[1].unlink()
    assert_failed(run(world), mentions=("without a metadata file",))


def test_two_metas_for_the_same_call_exit_1(world, run):
    add_instance(world, world.agent_id(8), "tachi-spoofing", world.dispatch_id("spoofing"))
    assert_failed(run(world), mentions=("same tool_use id",))


def test_a_tool_use_id_in_two_transcripts_exits_1(world, run):
    append_tool_call(world, world.agent_id("spoofing"), "Bash", "toolu_fx%d_orch_06" % world.number,
                     {"command": "ls"}, result=None)
    assert_failed(run(world), mentions=("more than one transcript",))


def test_a_replayed_call_is_counted_once(world, run):
    """The same response written twice (same message.id, same tool_use id) is one turn and one call."""
    path = world.role_paths("orchestrator")[0]
    lines = world.read_jsonl(path)
    bash = [o for o in lines if o.get("type") == "assistant"
            and any(b.get("id") == "toolu_fx%d_orch_06" % world.number for b in o["message"]["content"]
                    if isinstance(b, dict))]
    assert len(bash) == 1
    world.write_jsonl(path, lines + [json.loads(json.dumps(bash[0]))])
    inst = by_type(assert_ok(run(world))["subagents"])["tachi-orchestrator"]
    assert inst["tool_calls_by_tool"]["Bash"] == 1
    assert (inst["turns"], inst["synthetic_turns"]) == world.spec["turns"]["orchestrator"]


def test_a_dispatch_chain_that_loops_exits_1(world, run):
    a, b = world.agent_id(7), world.agent_id(8)
    add_instance(world, a, "my-helper-a", "toolu_tb_loop_b")
    add_instance(world, b, "my-helper-b", "toolu_tb_loop_a")
    append_tool_call(world, a, world.spec["dispatch_tool"], "toolu_tb_loop_a", dispatch_input("my-helper-b"))
    append_tool_call(world, b, world.spec["dispatch_tool"], "toolu_tb_loop_b", dispatch_input("my-helper-a"))
    assert_failed(run(world), mentions=("loops back",))


# =============================================================================
# Non-tachi subagent instances (P0B0-1) and name agreement
# =============================================================================


def test_p0b0_1_a_non_tachi_instance_is_listed_with_a_null_pin(world, run):
    manifest = assert_ok(run(world))
    inst = by_type(manifest["subagents"])["general-purpose"]
    assert inst["pinned_model"] is None
    assert inst["attribution_agent"] == "general-purpose"
    assert (inst["spawn_depth"], inst["parent_tool_use_id"]) == (3, world.dispatch_id("general-purpose"))
    assert inst["tool_calls_by_tool"] == {"Bash": 1, "Write": 1}
    assert (inst["turns"], inst["synthetic_turns"]) == world.spec["turns"]["general-purpose"]
    assert len(manifest["subagents"]) == 6
    ordered = [(s["spawn_depth"], s["agent_id"]) for s in manifest["subagents"]]
    assert ordered == sorted(ordered)


def test_p0b0_1_a_non_tachi_type_is_in_none_of_the_three_dispatch_lists(world, run):
    manifest = assert_ok(run(world))
    for listing in (manifest["dispatches"], manifest["tachi_agents_not_recorded"]):
        assert "general-purpose" not in {e["agent"] for e in listing}
        assert world.dispatch_id("general-purpose") not in {e["tool_use_id"] for e in listing}
    assert "general-purpose" not in manifest["tachi_agents_not_dispatched"]
    assert not [n for n in manifest["tachi_agents_not_dispatched"] if not n.startswith("tachi-")]


def test_p0b0_1_the_dispatching_agent_counts_its_agent_calls(world, run):
    by = by_type(assert_ok(run(world))["subagents"])
    tool = world.spec["dispatch_tool"]
    assert by["tachi-threat-report"]["tool_calls_by_tool"][tool] == 2  # attack-tree-delta and general-purpose
    assert by["tachi-orchestrator"]["tool_calls_by_tool"][tool] == 5
    assert "Bash" not in by["tachi-threat-report"]["tool_calls_by_tool"]  # the helper's Bash stays its own


def test_p0b0_1_a_non_tachi_bash_host_is_counted_in_egress(world, run):
    append_tool_call(world, world.agent_id("general-purpose"), "Bash", "toolu_tb_gp_extra",
                     {"command": "curl -sS https://extra-host.example.test/path?x=1#frag"})
    manifest = assert_ok(run(world))
    assert {"host": "extra-host.example.test", "tool": "Bash", "count": 1} in manifest["egress_observed"]
    assert by_type(manifest["subagents"])["general-purpose"]["tool_calls_by_tool"] == {"Bash": 2, "Write": 1}
    assert "Bash" not in by_type(manifest["subagents"])["tachi-threat-report"]["tool_calls_by_tool"]


def test_p0b0_1_negative_a_non_tachi_attribution_disagreement_exits_1(world, run):
    path = world.role_paths("general-purpose")[0]
    lines = world.read_jsonl(path)
    victim = [o for o in lines if o.get("attributionAgent")][1]
    victim["attributionAgent"] = "tachi-spoofing"
    world.write_jsonl(path, lines)
    out = run(world)
    assert_failed(out, mentions=("attributionAgent",))
    assert out.dest.exists(), "the verbatim copy is kept for inspection"


def test_p0b0_1_a_non_tachi_instance_that_fails_the_contract_fails_the_run(world, run):
    path = world.role_paths("general-purpose")[0]
    world.write_jsonl(path, [o for o in world.read_jsonl(path) if o.get("attributionAgent") is None])
    assert_failed(run(world))


def test_p0b0_1_a_tachi_name_missing_from_the_roster_still_has_a_null_pin(world, run):
    add_dispatched_instance(world, world.agent_id("orchestrator"), world.agent_id(7), "tachi-ghost", "toolu_tb_ghost")
    manifest = assert_ok(run(world))
    assert {"agent": "tachi-ghost", "tool_use_id": "toolu_tb_ghost", "spawn_depth": 2, "status": "recorded",
            "dispatched_from": world.agent_id("orchestrator")} in manifest["dispatches"]
    assert by_type(manifest["subagents"])["tachi-ghost"]["pinned_model"] is None
    assert manifest["tachi_agents_not_dispatched"] == list(NOT_DISPATCHED)


def test_p0b0_1_a_project_defined_type_is_listed_but_is_not_a_dispatch(world, run):
    add_dispatched_instance(world, world.agent_id("orchestrator"), world.agent_id(7), "my-helper", "toolu_tb_mine")
    manifest = assert_ok(run(world))
    assert by_type(manifest["subagents"])["my-helper"]["pinned_model"] is None
    assert "toolu_tb_mine" not in {d["tool_use_id"] for d in manifest["dispatches"]}
    assert manifest["dispatches"] == expected_dispatches(world)


def test_p0b0_1_a_non_tachi_instance_feeds_the_session_level_fields(world, run):
    """Versions, denials and permission modes seen only in a non-tachi instance still count."""
    gp = world.agent_id("general-purpose")
    jsonl = world.instance_paths(gp)[0]
    edit_lines(world, jsonl, lambda o: o.__setitem__("version", "2.1.999") if "version" in o else None)
    append_tool_call(world, gp, "Bash", "toolu_tb_gp_denied", {"command": "curl https://blocked.example.test/"},
                     result="error", denial="sandbox", version="2.1.999")
    world.write_jsonl(jsonl, world.read_jsonl(jsonl) + [{"type": "permission-mode", "permissionMode": "plan"}])
    manifest = assert_ok(run(world))
    assert manifest["claude_code_versions"] == [world.spec["version"], "2.1.999"]
    assert {"host": "blocked.example.test", "kind": "sandbox", "count": 1} in manifest["egress_denied"]
    assert "blocked.example.test" not in {e["host"] for e in manifest["egress_observed"]}
    assert manifest["permission_modes_seen"] == sorted([world.spec["mode"], "plan"])


# -- name agreement, with the <synthetic> exemption ---------------------------------------------


def test_a_synthetic_line_is_exempt_from_name_agreement(world, run):
    """The fixtures' <synthetic> line has no attributionAgent; one that names another agent is exempt too."""
    path = world.role_paths("orchestrator")[0]
    synthetic = [o for o in world.read_jsonl(path) if o.get("type") == "assistant" and o["message"]["model"] == SYNTHETIC]
    assert len(synthetic) == 1 and "attributionAgent" not in synthetic[0]
    edit_lines(world, path, lambda o: o.__setitem__("attributionAgent", "tachi-somebody-else")
               if o.get("type") == "assistant" and o["message"]["model"] == SYNTHETIC else None)
    inst = by_type(assert_ok(run(world))["subagents"])["tachi-orchestrator"]
    assert inst["attribution_agent"] == "tachi-orchestrator"
    assert (inst["turns"], inst["synthetic_turns"]) == world.spec["turns"]["orchestrator"]
    assert SYNTHETIC not in inst["served_model_histogram"]


def test_a_non_synthetic_line_naming_another_agent_exits_1(world, run):
    path = world.role_paths("spoofing")[0]
    lines = world.read_jsonl(path)
    [o for o in lines if o.get("attributionAgent")][0]["attributionAgent"] = "tachi-tampering"
    world.write_jsonl(path, lines)
    assert_failed(run(world), mentions=("attributionAgent disagrees with the metadata agentType",))


def test_one_attributed_non_synthetic_line_is_enough(world, run):
    """A line that does not carry the key is not a disagreement while at least one non-synthetic line carries it."""
    path = world.role_paths("tampering")[0]
    lines = world.read_jsonl(path)
    carriers = [o for o in lines if o.get("attributionAgent")]
    assert len(carriers) == 3
    for obj in carriers[1:]:
        del obj["attributionAgent"]
    world.write_jsonl(path, lines)
    assert by_type(assert_ok(run(world))["subagents"])["tachi-tampering"]["attribution_agent"] == "tachi-tampering"


def test_no_non_synthetic_line_carrying_the_attribution_exits_1(world, run):
    path = world.role_paths("spoofing")[0]
    edit_lines(world, path, lambda o: o.pop("attributionAgent", None))
    assert_failed(run(world), mentions=("no non-synthetic line carries attributionAgent",))


def test_a_synthetic_line_alone_cannot_supply_the_attribution(world, run):
    path = world.role_paths("spoofing")[0]
    edit_lines(world, path, lambda o: o.pop("attributionAgent", None))
    lines = world.read_jsonl(path)
    lines.append({"type": "assistant", "timestamp": STAMP, "attributionAgent": "tachi-spoofing",
                  "message": {"type": "message", "role": "assistant", "model": SYNTHETIC,
                              "content": [{"type": "text", "text": "FIXTURE"}]}})
    world.write_jsonl(path, lines)
    assert_failed(run(world), mentions=("no non-synthetic line carries attributionAgent",))


# =============================================================================
# Parse contract: each failure named, and what is tolerated
# =============================================================================


def _rel_main(world):
    return "%s.jsonl" % world.session_id


def _rel_sub(world, role, meta=False):
    return "%s/subagents/agent-%s.%s" % (world.session_id, world.agent_id(role), "meta.json" if meta else "jsonl")


@pytest.mark.parametrize("target", ["main", "subagent", "meta"])
def test_an_invalid_json_line_exits_1_naming_the_file_and_the_line(world, run, target):
    marker = "ZZ_CONTENT_MARKER"
    if target == "meta":
        world.write_text(world.role_paths("spoofing")[1], '{"agentType": "tachi-spoofing", ' + marker)
        rel, where = _rel_sub(world, "spoofing", meta=True), None
    else:
        path = world.main_path if target == "main" else world.role_paths("spoofing")[0]
        lines = world.read_text(path).split("\n")
        lines.insert(2, "{not json " + marker)
        world.write_text(path, "\n".join(lines))
        rel = _rel_main(world) if target == "main" else _rel_sub(world, "spoofing")
        where = "line 3"
    out = run(world)
    assert_failed(out, mentions=("not valid JSON", rel) + (() if where is None else (where,)))
    assert marker not in out.text, "transcript content was echoed"
    assert (out.dest / rel).is_file(), "the verbatim copy is kept for inspection"
    assert out.summary["status"] == "failed"


@pytest.mark.parametrize("key", ["agentType", "toolUseId"])
@pytest.mark.parametrize("damage", ["absent", "empty", "not-a-string"])
def test_a_meta_missing_a_required_key_exits_1(world, run, key, damage):
    meta_path = world.role_paths("tampering")[1]
    meta = world.read_json(meta_path)
    if damage == "absent":
        del meta[key]
    elif damage == "empty":
        meta[key] = ""
    else:
        meta[key] = 7
    world.write_json(meta_path, meta)
    assert_failed(run(world), mentions=("missing required key " + key, _rel_sub(world, "tampering", meta=True)))


def test_a_meta_that_is_not_an_object_exits_1(world, run):
    world.write_text(world.role_paths("tampering")[1], "[1, 2, 3]")
    assert_failed(run(world), mentions=("not a JSON object",))


def test_zero_assistant_turns_in_the_main_transcript_exits_1(world, run):
    world.write_jsonl(world.main_path, [o for o in world.read_jsonl(world.main_path) if o.get("type") != "assistant"])
    assert_failed(run(world), mentions=("zero assistant turns", _rel_main(world)))


def test_zero_assistant_turns_in_an_instance_exits_1(world, run):
    make_zero_turn(world, "attack-tree-delta")
    assert_failed(run(world), mentions=("zero assistant turns", _rel_sub(world, "attack-tree-delta")))


def test_an_empty_histogram_in_the_main_session_exits_1(world, run):
    """Every turn synthetic: turns are not zero, but nothing was served by a real model."""
    edit_lines(world, world.main_path, lambda o: o["message"].__setitem__("model", SYNTHETIC)
               if o.get("type") == "assistant" else None)
    assert_failed(run(world), mentions=("histogram is empty",))


def test_an_empty_histogram_in_an_instance_exits_1(world, run):
    path = world.role_paths("spoofing")[0]
    edit_lines(world, path, lambda o: o["message"].__setitem__("model", SYNTHETIC) if o.get("type") == "assistant" else None)
    assert_failed(run(world), mentions=("histogram is empty",))


@pytest.mark.parametrize("damage", ["absent", "null", "empty", "not-a-string", "has-whitespace"])
def test_an_assistant_line_without_a_usable_model_exits_1(world, run, damage):
    def apply(msg):
        if damage == "absent":
            del msg["model"]
        else:
            msg["model"] = {"null": None, "empty": "", "not-a-string": 5, "has-whitespace": "two words"}[damage]

    lines = world.read_jsonl(world.main_path)
    apply([o for o in lines if o.get("type") == "assistant"][1]["message"])
    world.write_jsonl(world.main_path, lines)
    assert_failed(run(world))


def test_lines_of_one_response_that_disagree_on_the_model_exit_1(world, run):
    path = world.role_paths("spoofing")[0]
    lines = world.read_jsonl(path)
    first, second = [o for o in lines if o.get("type") == "assistant" and o["message"]["model"] != SYNTHETIC][:2]
    second["message"]["id"] = first["message"]["id"]
    second["message"]["model"] = "claude-some-other-model"
    world.write_jsonl(path, lines)
    assert_failed(run(world), mentions=("same message.id",))


def test_extra_meta_keys_are_tolerated_and_listed_by_name_only(world, run):
    meta_path = world.role_paths("spoofing")[1]
    meta = world.read_json(meta_path)
    meta.update({"zzExtraKey": "VALUE_THAT_MUST_NOT_BE_COPIED", "aaOtherKey": {"nested": "ALSO_NOT_COPIED"}})
    world.write_json(meta_path, meta)
    out = run(world)
    manifest = assert_ok(out)
    by = by_type(manifest["subagents"])
    assert by["tachi-spoofing"]["unknown_meta_keys"] == ["aaOtherKey", "zzExtraKey"]
    assert all(s["unknown_meta_keys"] == [] for s in manifest["subagents"] if s["agent_type"] != "tachi-spoofing")
    assert out.summary["instances_with_unknown_meta_keys"] == 1
    text = out.manifest_path.read_text(encoding="utf-8") + out.text
    assert "VALUE_THAT_MUST_NOT_BE_COPIED" not in text and "ALSO_NOT_COPIED" not in text


def test_every_one_of_the_twelve_known_meta_keys_is_known(archiver):
    """The list is the twelve keys observed at Claude Code 2.1.328 (P0B0-4(b)); gen2 uses all of them."""
    known = set(archiver.KNOWN_META_KEYS)
    assert known == {"agentType", "description", "finished", "isBuiltIn", "launchedWithDefaults", "model",
                     "parentAgentId", "pickedEffortModel", "requestNonInteractive", "requestShape",
                     "spawnDepth", "toolUseId"}
    meta = json.loads((FIXTURE_ROOT / "synthetic-gen2" / "claude-config" / "projects" / "-fixture-project" /
                       GENERATIONS["gen2"]["session"] / "subagents" / "agent-a2f00000000000002.meta.json").read_text())
    assert set(meta) == known


def test_unknown_types_keys_and_odd_lines_are_tolerated_and_counted_outside_the_manifest(world, run, tmp_path):
    baseline = assert_ok(run(world, dest=tmp_path / "baseline" / "archive"))
    edit_lines(world, world.main_path, lambda o: o.__setitem__("zzNewAssistantKey", 1)
               if o.get("type") == "assistant" and o["message"]["model"] != SYNTHETIC else None)
    carrying = sum(1 for o in assistant_lines(world, world.main_path) if o["message"]["model"] != SYNTHETIC)
    odd = [
        json.dumps({"type": "zz-future-entry", "timestamp": "2026-11-18T10:00:30.000Z"}),  # inside both ranges
        json.dumps({"type": "zz-future-entry"}),
        "",
        "[1, 2, 3]",
        '"just a string"',
        "42",
        json.dumps({"type": "last-prompt", "timestamp": "not-a-timestamp"}),
    ]
    world.write_text(world.main_path, "\n".join(odd) + "\n" + world.read_text(world.main_path))
    out = run(world)
    manifest = assert_ok(out)
    summary = out.summary
    assert summary["unknown_entry_types"] == {"zz-future-entry": 2, "<non-object>": 3}
    assert summary["entry_types"]["<non-object>"] == 3
    assert summary["blank_lines"] == 1
    assert summary["timestamps_unparsed"] == 1
    assert summary["unknown_assistant_keys"] == {"zzNewAssistantKey": carrying}
    for field in ("main", "dispatches", "subagents", "egress_observed", "egress_denied", "claude_code_versions",
                  "started_at", "ended_at", "tachi_agents_not_recorded", "tachi_agents_not_dispatched"):
        assert manifest[field] == baseline[field], field
    assert "zz-future-entry" not in out.manifest_path.read_text(encoding="utf-8")
    assert "zzNewAssistantKey" not in out.manifest_path.read_text(encoding="utf-8")


@pytest.mark.parametrize("stamp,expected", [
    ("2026-11-18T09:00:00Z", "2026-11-18T09:00:00Z"),
    ("2026-11-18T09:00:00.123456789Z", "2026-11-18T09:00:00Z"),
    ("2026-11-18T09:00:00+00:00", "2026-11-18T09:00:00Z"),
    ("2026-11-18T11:00:00+02:00", "2026-11-18T09:00:00Z"),
    ("2026-11-18T04:00:00-05:00", "2026-11-18T09:00:00Z"),
])
def test_timestamps_are_read_as_utc_in_every_common_spelling(world, run, stamp, expected):
    """Z, a zero offset, an offset and a nanosecond fraction all parse (the fixtures cover Z on 3.9)."""
    lines = world.read_text(world.main_path).split("\n")
    world.write_text(world.main_path, json.dumps({"type": "last-prompt", "timestamp": stamp}) + "\n" + "\n".join(lines))
    manifest = assert_ok(run(world))
    assert manifest["started_at"] == expected


def test_claude_code_versions_sort_by_their_numeric_components(world, run):
    path = world.role_paths("spoofing")[0]
    edit_lines(world, path, lambda o: o.__setitem__("version", "2.1.10") if "version" in o else None)
    edit_lines(world, world.role_paths("tampering")[0], lambda o: o.__setitem__("version", "2.1.9") if "version" in o else None)
    versions = assert_ok(run(world))["claude_code_versions"]
    assert versions == sorted(versions, key=lambda v: [int(p) for p in v.split(".")])
    assert versions.index("2.1.9") < versions.index("2.1.10")
    assert len(versions) == 3


def test_a_transcript_set_with_no_timestamp_at_all_exits_1(world, run):
    for path in world.transcripts():
        edit_lines(world, path, lambda o: o.pop("timestamp", None))
        lines = world.read_jsonl(path)
        for obj in lines:
            if isinstance(obj.get("snapshot"), dict):
                obj["snapshot"].pop("timestamp", None)
        world.write_jsonl(path, lines)
    assert_failed(run(world), mentions=("no parseable timestamp",))


def test_without_a_dest_a_session_with_no_timestamp_is_refused_before_anything_is_written(world, run):
    for path in world.transcripts():
        edit_lines(world, path, lambda o: o.pop("timestamp", None))
    out = run(world, dest=None)
    assert_failed(out, mentions=("pass --dest",))
    assert not (Path(os.environ["HOME"]) / ".tachi").exists()


def test_a_fixture_free_of_dispatch_calls_is_attributed_with_no_dispatch_lists(world, run):
    """The inline-analysing orchestrator: nothing dispatched, yet the not-dispatched listing is never empty."""
    for role in ("spoofing", "tampering", "threat-report", "attack-tree-delta", "general-purpose"):
        for path in world.role_paths(role):
            path.unlink()
    for tid in ("spoofing", "tampering", "tool-abuse", "info-disclosure", "threat-report"):
        for path in world.transcripts():
            lines = world.read_jsonl(path)
            for obj in lines:
                msg = obj.get("message")
                if obj.get("type") == "assistant" and isinstance(msg, dict):
                    msg["content"] = [b for b in msg["content"]
                                      if not (isinstance(b, dict) and b.get("id") == world.dispatch_id(tid))]
            world.write_jsonl(path, lines)
        drop_tool_result(world, world.dispatch_id(tid))
    manifest = assert_ok(run(world))
    assert [d["agent"] for d in manifest["dispatches"]] == ["tachi-orchestrator"]
    assert manifest["tachi_agents_not_recorded"] == []
    assert manifest["tachi_agents_not_dispatched"] == sorted("tachi-" + r for r in ROSTER if r != "orchestrator")
    assert [s["agent_type"] for s in manifest["subagents"]] == ["tachi-orchestrator"]


# -- hostile but valid input: a clean parse failure, never an internal error ------------------------------------------
#
# Valid JSON that stretches the parser's assumptions. The archiver treats transcripts as untrusted, so
# each of these fails the run (exit 1) with a reason that names the file and line, writes no manifest and
# keeps the verbatim copy. (Before the T034 fix pass they ended as "internal error", exit 2.)


def _hostile_version(world):
    edit_lines(world, world.main_path, lambda o: o.__setitem__("version", "2.1.\u00b2") if "version" in o else None)


def _hostile_fullwidth_version(world):
    edit_lines(world, world.main_path, lambda o: o.__setitem__("version", "\uff12.1.328") if "version" in o else None)


def _hostile_timestamp(stamp):
    def apply(world):
        lines = world.read_jsonl(world.main_path)
        [o for o in lines if isinstance(o.get("timestamp"), str)][0]["timestamp"] = stamp
        world.write_jsonl(world.main_path, lines)

    return apply


def _hostile_nesting(world):
    world.write_bytes(world.main_path, world.read_bytes(world.main_path) + b"[" * 200000 + b"]" * 200000 + b"\n")


def _hostile_nesting_in_a_subagent(world):
    path = world.role_paths("spoofing")[0]
    world.write_bytes(path, world.read_bytes(path) + b"[" * 200000 + b"]" * 200000 + b"\n")


def _hostile_nesting_in_a_meta(world):
    world.write_bytes(world.role_paths("spoofing")[1], b'{"agentType":' + b"[" * 200000 + b"]" * 200000 + b"}")


HOSTILE = {
    "version-with-a-superscript-digit": (_hostile_version, "version holds a non-ASCII character"),
    "version-with-a-fullwidth-digit": (_hostile_fullwidth_version, "version holds a non-ASCII character"),
    "timestamp-that-underflows-with-its-offset": (
        _hostile_timestamp("0001-01-01T00:00:00+01:00"), "timestamp is out of range once its UTC offset is applied"),
    "timestamp-that-overflows-with-its-offset": (
        _hostile_timestamp("9999-12-31T23:59:59-01:00"), "timestamp is out of range once its UTC offset is applied"),
    "line-nested-200000-deep": (_hostile_nesting, "nested too deeply to read"),
    "subagent-line-nested-200000-deep": (_hostile_nesting_in_a_subagent, "nested too deeply to read"),
    "meta-file-nested-200000-deep": (_hostile_nesting_in_a_meta, "nested too deeply to read"),
}


@pytest.mark.parametrize("case", sorted(HOSTILE))
def test_hostile_but_valid_input_is_a_clean_parse_failure(world, run, case):
    apply, reason = HOSTILE[case]
    apply(world)
    out = run(world)
    assert_failed(out, rc=1, mentions=(reason,))
    assert "internal error" not in out.err and "Traceback" not in out.err
    assert (out.dest / (world.session_id + ".jsonl")).is_file(), "the verbatim copy is kept for inspection"
    assert out.summary["status"] == "failed"


def test_a_non_ascii_digit_timestamp_is_counted_as_unparsed_not_read(world, run):
    """The timestamp pattern is ASCII-only: a timestamp written in other digits is counted, never parsed."""
    stamp = "\u0662\u0660\u0662\u0666-\u0661\u0661-\u0661\u0668T\u0661\u0660:\u0660\u0660:\u0660\u0660Z"
    world.write_jsonl(world.main_path, [{"type": "last-prompt", "timestamp": stamp}] + world.read_jsonl(world.main_path))
    out = run(world)
    manifest = assert_ok(out)
    assert out.summary["timestamps_unparsed"] == 1
    assert manifest["started_at"].startswith("2026-11-18T10:00:0")


def test_a_year_below_1000_is_zero_padded_on_every_platform(world, run):
    world.write_jsonl(world.main_path, [{"type": "last-prompt", "timestamp": "0999-12-31T23:59:59Z"}]
                      + world.read_jsonl(world.main_path))
    assert assert_ok(run(world))["started_at"] == "0999-12-31T23:59:59Z"


def test_an_out_of_range_first_timestamp_does_not_crash_the_default_destination(world, run):
    """Choosing the default destination reads the first timestamp: a line it cannot place is skipped, not fatal."""
    apply, reason = HOSTILE["timestamp-that-underflows-with-its-offset"]
    apply(world)
    out = run(world, dest=None)
    assert_failed(out, rc=1, mentions=(reason,))  # the run itself still fails closed, on the same reason
    assert "internal error" not in out.err


def test_discovery_skips_an_unrelated_transcript_it_cannot_read(world, run, tmp_path):
    """A deeply nested line in another project's transcript must not stop this project's archive."""
    other_slug = world.config_dir / "projects" / "-another-project"
    other_slug.mkdir()
    foreign = other_slug / "99999999-9999-4999-8999-999999999999.jsonl"
    world.write_bytes(foreign, b"[" * 200000 + b"]" * 200000 + b'\n{"type":"user","cwd":"/elsewhere"}\n')
    world.age_file(foreign, seconds=600)
    assert assert_ok(run(world, latest=True))["session_id"] == world.session_id


# =============================================================================
# Refusal matrix: deny by default
# =============================================================================


def source_digest(world):
    return {rel: sha256_file(path) for rel, path in world.source_tree().items()}


def repo_files(repo):
    return sorted(p.relative_to(repo).as_posix() for p in repo.rglob("*") if ".git/" not in p.as_posix() + "/"
                  and p.name != ".git")


@pytest.mark.parametrize("ignore,dest_rel,accepted", [
    ("", "runs/archive", False),
    ("runs/\n", "runs/archive", True),
    ("runs/\n", "runs/a/b/c/archive", True),
    ("runs/\n", "other/archive", False),
    ("/runs/\n", "runs/archive", True),
    ("archive/\n", "x/archive", True),
    ("*\n", "anything/archive", True),
])
def test_a_destination_in_a_work_tree_is_refused_unless_git_ignores_it(world, run, tmp_path, ignore, dest_rel, accepted):
    repo = init_repo(tmp_path / "repo", ignore=ignore)
    dest = repo / dest_rel
    before = source_digest(world)
    out = run(world, dest=dest)
    if accepted:
        assert_ok(out)
        assert archived_tree(dest)[MANIFEST]
        assert committable(repo) == [], "an accepted destination left committable entries in the work tree"
    else:
        assert_failed(out, mentions=("git work tree", "not ignored"))
        assert not dest.exists()
        assert repo_files(repo) == [".gitignore"], "the refused run left something in the work tree"
    assert source_digest(world) == before


def test_a_destination_ignored_through_the_exclude_file_is_accepted(world, run, tmp_path):
    repo = init_repo(tmp_path / "repo")
    (repo / ".git" / "info" / "exclude").write_text("runs/\n", encoding="utf-8")
    assert_ok(run(world, dest=repo / "runs" / "archive"))


@pytest.mark.parametrize("ignore,accepted", [
    (".tachi/\n", True),
    (".tachi/runs/\n", True),
    ("/.tachi\n", True),
    (".tachi/runs/project/\n", True),
    ("", False),
    (".claude/\n", False),
    (".tachi/other/\n", False),
])
def test_a_dotfiles_repo_at_home_is_accepted_only_when_the_runs_dir_is_ignored(world, run, ignore, accepted):
    """The default destination lives under HOME; a repo rooted there must ignore it."""
    home = Path(os.environ["HOME"])
    init_repo(home, ignore=ignore or None)
    out = run(world, dest=None)
    expected = home / ".tachi" / "runs" / "project" / ("2026-11-18-" + world.session_id)
    if accepted:
        assert_ok(out)
        assert os.path.realpath(out.summary["archive_dir"]) == os.path.realpath(str(expected))
        assert archived_tree(expected).pop(MANIFEST)
        for directory in (home / ".tachi", home / ".tachi" / "runs", home / ".tachi" / "runs" / "project", expected):
            assert mode_of(directory) == 0o700, directory
    else:
        assert_failed(out, mentions=("not ignored",))
        assert not (home / ".tachi").exists(), "a refused run created the default destination"


def test_the_default_destination_without_any_work_tree(world, run):
    """No repo around HOME: the default ~/.tachi/runs/<project>/<date>-<session>/ is used."""
    home = Path(os.environ["HOME"])
    out = run(world, dest=None)
    assert_ok(out)
    assert Path(out.summary["archive_dir"]) == home / ".tachi" / "runs" / "project" / ("2026-11-18-" + world.session_id)


def test_a_non_empty_destination_is_refused_and_left_alone(world, run):
    world.dest.mkdir(parents=True)
    stray = world.dest / "somebody-elses-file.txt"
    stray.write_text("not ours", encoding="utf-8")
    before = source_digest(world)
    out = run(world)
    assert_failed(out, mentions=("not empty",))
    assert sorted(p.name for p in world.dest.iterdir()) == ["somebody-elses-file.txt"]
    assert stray.read_text(encoding="utf-8") == "not ours"
    assert source_digest(world) == before


def test_an_empty_existing_destination_is_used_and_made_owner_only(world, run):
    world.dest.mkdir(parents=True)
    os.chmod(str(world.dest), 0o755)
    out = run(world)
    assert_ok(out)
    assert mode_of(world.dest) == 0o700


def test_a_destination_that_is_a_file_is_refused(world, run):
    world.dest.parent.mkdir(parents=True)
    world.dest.write_text("a file", encoding="utf-8")
    assert_failed(run(world), mentions=("not a directory",))
    assert world.dest.read_text(encoding="utf-8") == "a file"


def test_a_live_session_is_refused_without_allow_live(world, run):
    os.utime(str(world.main_path), None)  # modified just now
    out = run(world)
    assert_failed(out, mentions=("looks live", "--allow-live"))
    assert not out.dest.exists(), "a refused run must not create the destination"
    allowed = run(world, "--allow-live")
    assert_ok(allowed)
    assert archived_tree(allowed.dest)[world.session_id + ".jsonl"] == sha256_file(world.main_path)


def test_a_live_subagent_transcript_makes_the_session_live(world, run):
    os.utime(str(world.role_paths("spoofing")[0]), None)
    assert_failed(run(world), mentions=("looks live",))


@pytest.mark.parametrize("age,window,live", [
    (30, 60, True), (30, 10, False), (30, 0, False), (500, 120, False), (60, 120, True),
])
def test_the_live_window_is_in_seconds_and_zero_disables_it(world, run, age, window, live):
    world.age_file(world.main_path, seconds=age)
    out = run(world, "--live-window-seconds", window)
    if live:
        assert_failed(out, mentions=("looks live",))
    else:
        assert_ok(out)


@pytest.mark.parametrize("which", ["meta", "tool-result", "subagent-transcript", "main-transcript"])
def test_any_file_of_the_session_tree_makes_the_session_live(world, run, which):
    """T034 L-5: the live rule counts every file in the session tree, not the transcripts alone."""
    path = {
        "meta": world.role_paths("spoofing")[1],
        "tool-result": sorted(world.results_dir.glob("*.txt"))[0],
        "subagent-transcript": world.role_paths("spoofing")[0],
        "main-transcript": world.main_path,
    }[which]
    os.utime(str(path), None)
    out = run(world)
    assert_failed(out, mentions=("looks live", "1 file(s) changed"))
    assert not out.dest.exists()
    assert_ok(run(world, "--allow-live"))


def test_a_fresh_file_outside_the_session_tree_does_not_make_it_live(world, run):
    """Only this session's own transcript and directory count: a sibling file or another session does not."""
    sibling = world.slug_dir / "unrelated-notes.txt"
    world.write_text(sibling, "not part of the session")
    other = world.slug_dir / "99999999-9999-4999-8999-999999999999.jsonl"
    world.write_jsonl(other, [{"type": "user", "cwd": "/somewhere/else", "timestamp": STAMP,
                               "message": {"role": "user", "content": "FIXTURE"}}])
    for path in (sibling, other):
        os.utime(str(path), None)
    assert_ok(run(world))


def test_a_negative_live_window_is_a_usage_error(world, run):
    assert_failed(run(world, "--live-window-seconds", "-5"), rc=2, mentions=("must not be negative",))


def test_a_symlink_in_the_destination_path_into_a_work_tree_is_refused(world, run, tmp_path):
    repo = init_repo(tmp_path / "repo", ignore="runs/\n")
    (repo / "runs").mkdir()
    # control: the ignored directory itself is a fine destination
    assert_ok(run(world, dest=repo / "runs" / "control"))
    link = tmp_path / "link"
    link.symlink_to(repo / "runs", target_is_directory=True)
    out = run(world, dest=link / "archive")
    assert_failed(out, mentions=("symbolic link", "git work tree"))
    assert not (repo / "runs" / "archive").exists(), "nothing may be written through the link"


def test_a_destination_that_is_itself_a_symlink_into_a_work_tree_is_refused(world, run, tmp_path):
    repo = init_repo(tmp_path / "repo", ignore="runs/\n")
    (repo / "runs").mkdir()
    link = tmp_path / "dest-link"
    link.symlink_to(repo / "runs" / "target", target_is_directory=True)  # dangling on purpose
    assert_failed(run(world, dest=link), mentions=("symbolic link",))
    assert not (repo / "runs" / "target").exists()


def test_a_symlink_resolving_outside_any_work_tree_is_not_refused(world, run, tmp_path):
    plain = tmp_path / "plain"
    plain.mkdir()
    link = tmp_path / "plain-link"
    link.symlink_to(plain, target_is_directory=True)
    out = run(world, dest=link / "archive")
    assert_ok(out)
    assert (plain / "archive" / MANIFEST).is_file()


def test_a_symlink_inside_a_work_tree_that_leaves_it_is_not_refused(world, run, tmp_path):
    repo = init_repo(tmp_path / "repo")
    plain = tmp_path / "plain"
    plain.mkdir()
    (repo / "outlink").symlink_to(plain, target_is_directory=True)
    assert_ok(run(world, dest=repo / "outlink" / "archive"))
    assert (plain / "archive" / MANIFEST).is_file()


@pytest.mark.parametrize("kind", ["file", "directory", "session-directory", "fifo"])
def test_a_source_tree_that_holds_a_link_or_special_file_is_refused(world, run, tmp_path, kind):
    outside = tmp_path / "outside.txt"
    outside.write_text("outside the session", encoding="utf-8")
    if kind == "file":
        (world.results_dir / "link.txt").symlink_to(outside)
    elif kind == "directory":
        (world.sub_dir / "linkdir").symlink_to(tmp_path, target_is_directory=True)
    elif kind == "fifo":
        os.mkfifo(str(world.results_dir / "pipe"))
    else:
        real = world.slug_dir / "real-session"
        os.rename(str(world.session_dir), str(real))
        world.session_dir.symlink_to(real, target_is_directory=True)
    out = run(world)
    assert_failed(out)
    assert any(word in out.err for word in ("symbolic link", "not a regular file")), out.err
    assert not out.dest.exists(), "nothing is copied from a tree that holds a link"


# -- P0B0-5: a re-archive is a no-op only when the manifest is present -----------------------------


def test_p0b0_5_a_failed_run_does_not_pass_on_its_second_try(world, run):
    """The defect: copy, then fail before the manifest; the next run must not exit 0 as a "no-op"."""
    world.edit_text(world.role_paths("spoofing")[0], lambda t: t + "{not json\n")
    first = run(world)
    assert_failed(first, mentions=("not valid JSON",))
    assert (first.dest / (world.session_id + ".jsonl")).is_file(), "the failed run keeps its verbatim copy"
    second = run(world)
    assert_failed(second, mentions=("incomplete archive", "run-manifest.json absent"))
    assert second.summary["status"] == "refused"
    third = run(world, "--allow-live")
    assert third.rc == 1 and not third.has_manifest()


def test_p0b0_5_an_archive_without_its_manifest_is_incomplete(world, run):
    out = run(world)
    assert_ok(out)
    out.manifest_path.unlink()
    before = archived_tree(out.dest)
    again = run(world)
    assert_failed(again, mentions=("incomplete archive: run-manifest.json absent", "new --dest"))
    assert archived_tree(out.dest) == before, "an incomplete archive must be left exactly as found"


def test_p0b0_5_a_hand_made_copy_without_a_manifest_is_incomplete(world, run):
    for rel, path in world.source_tree().items():
        target = world.dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(path), str(target))
    assert_failed(run(world), mentions=("incomplete archive",))


def test_p0b0_5_a_hash_mismatch_is_refused_and_not_repaired(world, run):
    out = run(world)
    assert_ok(out)
    victim = out.dest / (world.session_id + ".jsonl")
    victim.write_bytes(victim.read_bytes() + b" ")
    before = archived_tree(out.dest)
    again = run(world)
    assert_failed(again, mentions=("does not hold an identical archive",), keep_manifest=True)
    assert archived_tree(out.dest) == before


def test_p0b0_5_a_missing_archived_file_is_refused(world, run):
    out = run(world)
    assert_ok(out)
    (out.dest / world.session_id / "subagents" / ("agent-%s.meta.json" % world.agent_id("spoofing"))).unlink()
    assert_failed(run(world), mentions=("does not hold an identical archive",), keep_manifest=True)


def test_a_changed_source_is_not_a_no_op(world, run):
    """Same destination, different transcript: the archive does not match, so nothing is reused."""
    out = run(world)
    assert_ok(out)
    world.edit_text(world.main_path, lambda t: t + json.dumps({"type": "last-prompt", "timestamp": STAMP}) + "\n")
    before = out.manifest_path.read_bytes()
    assert_failed(run(world), mentions=("does not hold an identical archive",), keep_manifest=True)
    assert out.manifest_path.read_bytes() == before, "the finished archive was rewritten"


# -- git and the work-tree check ----------------------------------------------------------------------


@pytest.mark.parametrize("kind", ["empty-git-dir", "dangling-gitfile"])
def test_a_git_marker_git_cannot_resolve_is_refused(world, run, tmp_path, kind):
    """Deny by default: when git cannot name the enclosing work tree, the destination is refused."""
    broken = tmp_path / "broken"
    broken.mkdir()
    if kind == "empty-git-dir":
        (broken / ".git").mkdir()
    else:
        (broken / ".git").write_text("gitdir: /nonexistent/place/for/the/git/dir\n", encoding="utf-8")
    out = run(world, dest=broken / "out" / "archive")
    assert_failed(out, mentions=("cannot name the enclosing work tree",))
    assert not (broken / "out").exists()


def test_without_git_a_destination_in_a_work_tree_exits_2(world, run, tmp_path):
    repo = init_repo(tmp_path / "repo", ignore="runs/\n")
    no_git = tmp_path / "empty-bin"
    no_git.mkdir()
    out = run(world, dest=repo / "runs" / "archive", env={"PATH": str(no_git)})
    assert_failed(out, rc=2, mentions=("git is required",))
    assert not (repo / "runs").exists()


def test_without_git_a_destination_outside_any_work_tree_is_fine(world, run, tmp_path):
    no_git = tmp_path / "empty-bin"
    no_git.mkdir()
    assert_ok(run(world, env={"PATH": str(no_git)}))


# =============================================================================
# Secret handling: planting sites, forced leaks, structural redaction, the floor
# =============================================================================
#
# Key-shaped dummy values are assembled here at run time from short fragments
# (ADR-042). Nothing in this file is a key-shaped literal.

_ALNUM = string.ascii_letters + string.digits
_UPPER_DIGITS = string.ascii_uppercase + string.digits


def _filler(count, alphabet=_ALNUM, salt=3):
    """``count`` characters of a fixed, low-entropy walk through ``alphabet`` (never a literal)."""
    return "".join(alphabet[(i * 7 + salt) % len(alphabet)] for i in range(count))


def _join(*fragments):
    return "".join(fragments)


def google_key():
    return _join("AI", "za") + _filler(35)


# --- forced leaks: the key formats the final scan knows ------------------------------------------
# (rule id the archiver names in its reason, builder). The security review (T034) may retune this
# table; the leak tests below read nothing else about the formats. Each value is one token (no
# whitespace), so it can reach the manifest as an agent type, a model id, a host label or a version.
LEAK_FORMATS = [
    ("google-api-key", google_key),
    ("anthropic-api-key", lambda: _join("sk", "-", "ant", "-") + _filler(30)),
    ("openai-api-key", lambda: _join("sk", "-", "proj", "-") + _filler(40)),
    ("github-token", lambda: _join("gh", "p", "_") + _filler(40)),
    ("github-fine-grained-token", lambda: _join("github", "_", "pat", "_") + _filler(30)),
    ("aws-access-key-id", lambda: _join("AK", "IA") + _filler(16, _UPPER_DIGITS)),
    ("slack-token", lambda: _join("xo", "xb", "-") + _filler(20)),
    ("stripe-key", lambda: _join("sk", "_", "live", "_") + _filler(24)),
    ("json-web-token", lambda: _join("ey", "J") + _filler(12) + "." + _join("ey", "J") + _filler(12) + "." + _filler(12)),
    ("service-account-token", lambda: _join("op", "s_") + _filler(48)),
    ("url-userinfo-password", lambda: _join("https", "://", "someone", ":") + _filler(14) + "@registry.example.test"),
    # added at T034 (L-7)
    ("huggingface-token", lambda: _join("hf", "_") + _filler(34)),
    ("gitlab-token", lambda: _join("gl", "pat", "-") + _filler(24)),
    ("npm-token", lambda: _join("np", "m_") + _filler(36)),
    ("google-oauth-token", lambda: _join("ya", "29", ".") + _filler(30)),
    ("supabase-key", lambda: _join("sb", "p_") + _filler(40, "0123456789abcdef")),
    ("xai-key", lambda: _join("xa", "i-") + _filler(24)),
    ("groq-key", lambda: _join("gs", "k_") + _filler(44)),
]

# --- the six planting sites -------------------------------------------------------------------------
# context template -> the committed fixtures write it with the placeholder in {k}
SITE_CONTEXTS = {
    "shell-header": "x-goog-api-key: {k}",
    "url-query": "?key={k}",
    "url-userinfo": "fixture-user:{k}@",
    "tool-result-text": "request failed for key {k}",
    "meta-description": "(token {k})",
    "denial-message": "FIXTURE denial text {k}",
}
SITES = sorted(SITE_CONTEXTS)


def plant(world, key, sites):
    """Put ``key`` at the named sites in a fixture copy; returns {site: occurrences planted}."""
    counts = dict((site, 0) for site in sites)
    for path in sorted(world.config_dir.rglob("*")):
        if not path.is_file():
            continue
        text = world.read_text(path)
        changed = text
        for site in sites:
            before = SITE_CONTEXTS[site].format(k=PLACEHOLDER_KEY)
            counts[site] += changed.count(before)
            changed = changed.replace(before, SITE_CONTEXTS[site].format(k=key))
        if changed != text:
            world.write_text(path, changed)
    return counts


def occurrences(root, key):
    """Total occurrences of ``key`` in every file under ``root``."""
    return sum(Path(p).read_bytes().count(key.encode("utf-8")) for p in Path(root).rglob("*") if p.is_file())


def assert_key_absent(key, *texts):
    for text in texts:
        for needle in (key, key.lower(), key[8:24], key[8:24].lower()):
            assert needle not in text, "part of the dummy key reached the output"


def test_the_six_planting_sites_together(world, run):
    """All six sites at once: the run succeeds and the key is in none of the manifest, stdout or stderr."""
    key = google_key()
    counts = plant(world, key, SITES)
    assert all(n >= 1 for n in counts.values()), "the fixture lacks a planting site: %s" % counts
    assert counts["url-query"] == 2 and counts["tool-result-text"] == 2 and counts["meta-description"] == 2
    planted = occurrences(world.config_dir, key)
    assert planted >= 9
    out = run(world)
    manifest = assert_ok(out)
    text = out.manifest_path.read_text(encoding="utf-8")
    assert_key_absent(key, text, out.out, out.err, json.dumps(manifest))
    assert occurrences(out.dest, key) == planted, "the archive is verbatim: it still holds every planted key"
    assert not [w for w in out.summary["warnings"] if key in w]


@pytest.mark.parametrize("site", SITES)
def test_each_planting_site_alone(world, run, site):
    """One site at a time, so a leak names its own site: succeed, and the key stays out of every output."""
    key = google_key()
    counts = plant(world, key, [site])
    assert counts[site] >= 1
    assert occurrences(world.config_dir, key) == counts[site]
    out = run(world)
    manifest = assert_ok(out)
    assert_key_absent(key, out.manifest_path.read_text(encoding="utf-8"), out.out, out.err)
    assert occurrences(out.dest, key) == counts[site]
    assert manifest["egress_observed"] == EXPECTED_EGRESS
    assert manifest["egress_denied"] == [{"host": "example.com", "kind": "permission-rule", "count": 1}]


@pytest.mark.parametrize("rule,build", LEAK_FORMATS, ids=[r for r, _b in LEAK_FORMATS])
def test_a_forced_leak_of_each_key_format_fails_the_run_and_writes_no_manifest(world, run, rule, build):
    """The key reaches the manifest as an agent type: the final scan refuses to write it."""
    key = build()
    rename_instance_type(world, world.agent_id("general-purpose"), key)
    out = run(world)
    assert_failed(out, mentions=("secret scan", rule, "subagents["))
    assert_key_absent(key, out.text, json.dumps(out.summary))
    assert out.summary["status"] == "failed"
    assert occurrences(out.dest, key) >= 1, "the verbatim copy is kept for inspection"
    assert sorted(p.name for p in out.dest.iterdir()) == sorted(
        [ARCHIVE_GITIGNORE, world.session_id, world.session_id + ".jsonl"])


def _carry_in_model_id(world, key):
    edit_lines(world, world.main_path, lambda o: o["message"].__setitem__("model", key)
               if o.get("type") == "assistant" and o["message"]["model"] != SYNTHETIC else None)


def _carry_in_version(world, key):
    edit_lines(world, world.role_paths("spoofing")[0], lambda o: o.__setitem__("version", key) if "version" in o else None)


def _carry_in_host(world, key):
    append_tool_call(world, "main", "Bash", "toolu_tb_leak_host", {"command": "curl https://%s.example.test/" % key.lower()})


def _carry_in_tool_name(world, key):
    update_tool_uses(world, "toolu_fx%d_main_03" % world.number, lambda block: block.__setitem__("name", key))


@pytest.mark.parametrize("carrier,where", [
    (_carry_in_model_id, "main"), (_carry_in_version, "claude_code_versions"),
    (_carry_in_host, "egress_observed"), (_carry_in_tool_name, "main"),
], ids=["model-id-histogram-key", "version", "host-label-lower-cased", "tool-name-dict-key"])
def test_a_forced_leak_is_caught_wherever_it_reaches_the_manifest(world, run, carrier, where):
    """Dict keys, list elements and lower-cased host labels are all scanned."""
    key = google_key()
    carrier(world, key)
    out = run(world)
    assert_failed(out, mentions=("secret scan", "google-api-key", where))
    assert_key_absent(key, out.text)


def test_a_clean_run_then_a_forced_leak_leaves_a_temporary_file_nowhere(world, run):
    rename_instance_type(world, world.agent_id("general-purpose"), google_key())
    out = run(world)
    assert_failed(out)
    leftovers = [p.name for p in out.dest.rglob("*") if "manifest" in p.name]
    assert leftovers == []


# --- the environment-variable half of the scan ----------------------------------------------------------

SECRET_VARIABLES = ["TACHI_TEST_API_KEY", "TACHI_TEST_AUTH_TOKEN", "TACHI_TEST_CLIENT_SECRET",
                    "TACHI_TEST_DB_PASSWORD", "TACHI_TEST_CLOUD_CREDENTIAL", "tachi_test_mixed_Token"]


def _env_secret():
    return "fixture-" + _filler(24)  # long, not shaped like any known key format


@pytest.mark.parametrize("variable", SECRET_VARIABLES)
def test_a_secret_named_variables_value_in_the_manifest_fails_the_run_naming_the_variable(world, run, variable):
    value = _env_secret()
    rename_instance_type(world, world.agent_id("general-purpose"), value)
    out = run(world, env={variable: value})
    assert_failed(out, mentions=("secret scan", "environment variable " + variable))
    assert_key_absent(value + _filler(8), out.text)
    assert value not in out.text


def test_the_scan_matches_a_secret_value_inside_a_longer_manifest_string(world, run):
    value = _env_secret()
    rename_instance_type(world, world.agent_id("general-purpose"), "pre-" + value + "-post")
    assert_failed(run(world, env={"TACHI_TEST_API_KEY": value}), mentions=("TACHI_TEST_API_KEY",))


def test_a_variable_not_named_like_a_secret_is_not_scanned(world, run):
    value = _env_secret()
    rename_instance_type(world, world.agent_id("general-purpose"), value)
    out = run(world, env={"TACHI_TEST_PLAIN": value})
    manifest = assert_ok(out)
    assert value in [s["agent_type"] for s in manifest["subagents"]], "the carrier did not reach the manifest"


def test_hash_fields_are_excluded_from_the_scan(world, run):
    digest = sha256_file(world.main_path)
    out = run(world, env={"TACHI_TEST_SECRET": digest})
    manifest = assert_ok(out)
    assert digest in [t["sha256"] for t in manifest["transcripts"]], "the digest is not in the manifest"


def test_the_scan_reads_the_archivers_own_environment_only(world, run):
    """An unset variable cannot match: with the variable absent the same session archives cleanly."""
    value = _env_secret()
    rename_instance_type(world, world.agent_id("general-purpose"), value)
    assert_ok(run(world))


# --- structural redaction: free text cannot reach the manifest at all ---------------------------------------


def _set_agent_type(world, bad):
    meta_path = world.role_paths("spoofing")[1]
    meta = world.read_json(meta_path)
    meta["agentType"] = bad
    world.write_json(meta_path, meta)


def _set_dispatch_type(world, bad):
    set_dispatch_type(world, world.dispatch_id("spoofing"), bad)


def _set_tool_name(world, bad):
    update_tool_uses(world, "toolu_fx%d_main_03" % world.number, lambda block: block.__setitem__("name", bad))


def _set_version(world, bad):
    edit_lines(world, world.role_paths("spoofing")[0], lambda o: o.__setitem__("version", bad) if "version" in o else None)


def _set_tool_use_id(world, bad):
    update_tool_uses(world, "toolu_fx%d_main_03" % world.number, lambda block: block.__setitem__("id", bad))


@pytest.mark.parametrize("bad", ["two words", "tab\there", "line\nbreak", "x" * 129, "bell\x07"],
                         ids=["space", "tab", "newline", "129-chars", "control"])
@pytest.mark.parametrize("setter", [_set_agent_type, _set_dispatch_type, _set_tool_name, _set_version, _set_tool_use_id],
                         ids=["agentType", "subagent_type", "tool-name", "version", "tool-use-id"])
def test_a_value_that_is_not_one_short_token_stops_the_run(world, run, setter, bad):
    setter(world, bad)
    out = run(world)
    assert_failed(out, mentions=("unexpected shape",))
    assert bad not in out.text and bad.strip() not in out.text


# =============================================================================
# P0B0-11 floor: the one place the secret-scan floor lives
# =============================================================================
#
# Tested as implemented: a secret-named variable's value is matched only when it is at least
# FLOOR characters, is not a boolean literal and is not purely numeric. If the security review
# (T034) retunes the floor, change FLOOR (and the literal lists below) and nothing else.

FLOOR = 8
BOOLEAN_LITERALS = ("true", "false")
NUMERIC_AT_FLOOR = ("1234567890" * 20)[:FLOOR]  # digits only, exactly FLOOR long


def _of_length(count):
    return "fx" + "q" * (count - 2)


def _floor_run(world, run, value, variable="TACHI_TEST_API_KEY"):
    rename_instance_type(world, world.agent_id("general-purpose"), value)
    out = run(world, env={variable: value})
    return out


def test_floor_a_value_just_below_the_floor_that_is_in_the_manifest_does_not_fail_the_run(world, run):
    value = _of_length(FLOOR - 1)
    out = _floor_run(world, run, value)
    manifest = assert_ok(out)
    assert value in [s["agent_type"] for s in manifest["subagents"]], "the carrier did not reach the manifest"


def test_floor_a_value_at_the_floor_that_is_in_the_manifest_fails_the_run_naming_the_variable(world, run):
    value = _of_length(FLOOR)
    out = _floor_run(world, run, value)
    assert_failed(out, mentions=("environment variable TACHI_TEST_API_KEY",))
    assert value not in out.text


def test_floor_a_long_dummy_value_fails_the_run(world, run):
    value = _of_length(FLOOR * 4)
    assert_failed(_floor_run(world, run, value), mentions=("TACHI_TEST_API_KEY",))


@pytest.mark.parametrize("literal", ["auto", "Bash", "recorded"[:FLOOR - 1], "1"])
def test_floor_short_values_that_collide_with_manifest_strings_do_not_fail_the_run(world, run, literal):
    """Counts, mode names, tool names and ids are short; a secret-named variable holding one must not refuse a clean session."""
    rename_instance_type(world, world.agent_id("general-purpose"), literal)
    out = run(world, env={"TACHI_TEST_TOKEN": literal})
    manifest = assert_ok(out)
    assert literal in [s["agent_type"] for s in manifest["subagents"]]


@pytest.mark.parametrize("literal", BOOLEAN_LITERALS)
def test_floor_boolean_literals_never_fail_the_run(world, run, literal):
    out = _floor_run(world, run, literal, variable="TACHI_TEST_SECRET")
    manifest = assert_ok(out)
    assert literal in [s["agent_type"] for s in manifest["subagents"]]


def test_floor_a_digits_only_value_at_the_floor_fails_the_run_when_it_reaches_the_manifest(world, run):
    """T034 amendment 3: a run of FLOOR or more digits cannot be a count or a mode name, so it is scanned."""
    out = _floor_run(world, run, NUMERIC_AT_FLOOR, variable="TACHI_TEST_PASSWORD")
    assert_failed(out, mentions=("environment variable TACHI_TEST_PASSWORD",))
    assert NUMERIC_AT_FLOOR not in out.text


# Shapes the amended rule still skips: they can equal a manifest string by chance (a date, a timestamp,
# a dotted version, an IP literal), and every one of them is FLOOR characters or longer.
BENIGN_SHAPES = ["2026-11-19", "2026-11-19T10:00:00Z", "1.2.3.4.5.6", "10.20.30.40", "192.168.100.200"]


@pytest.mark.parametrize("value", BENIGN_SHAPES)
def test_floor_a_date_timestamp_version_or_ip_shaped_value_never_fails_the_run(world, run, value):
    assert len(value) >= FLOOR
    out = _floor_run(world, run, value, variable="TACHI_TEST_SECRET")
    manifest = assert_ok(out)
    assert value in [s["agent_type"] for s in manifest["subagents"]], "the carrier did not reach the manifest"
    assert out.summary["secret_scan"]["environment_values_skipped"] == 1


@pytest.mark.parametrize("suffix", ["\n", " ", "\r\n", "\t "], ids=["newline", "space", "crlf", "tab-space"])
def test_floor_a_value_is_stripped_before_the_floor_applies(world, run, suffix):
    """T034 M-2: trailing whitespace or a newline neither hides a value nor lets a short one through."""
    value = _of_length(FLOOR)
    rename_instance_type(world, world.agent_id("general-purpose"), value)
    assert_failed(run(world, env={"TACHI_TEST_API_KEY": value + suffix}), mentions=("TACHI_TEST_API_KEY",))
    # padding does not lift a value over the floor: it is skipped, not checked (the coverage counts show which)
    short = _of_length(FLOOR - 1)
    other = world.dest.parent / "short" / "archive"
    rename_instance_type(world, world.agent_id("general-purpose"), short)
    padded = run(world, env={"TACHI_TEST_API_KEY": short + "  "}, dest=other)
    assert_ok(padded)
    cov = padded.summary["secret_scan"]
    assert (cov["environment_values_checked"], cov["environment_values_skipped"]) == (0, 1)


def test_floor_known_key_formats_are_matched_at_any_length_not_by_the_floor(world, run):
    """The patterns are not subject to the floor: a key-shaped value is refused whatever the environment holds."""
    key = google_key()
    rename_instance_type(world, world.agent_id("general-purpose"), key)
    assert_failed(run(world), mentions=("google-api-key",))


# =============================================================================
# Denial detection: permission-rule detected, unrecognised kinds and mixed versions fail closed
# =============================================================================
#
# The fixtures carry the one denial shape observed before the recorded run: a ``toolDenialKind`` on
# the user entry holding the denied call's tool_result. Nothing below invents another placement, and
# nothing populates the shipped validated-versions set: tests that need a "validated" version
# patch the module constant for their own duration only.


def _numeric_key(version):
    return [int(part) for part in version.split(".")]


def _denied_web_fetch(world, name, kind):
    append_tool_call(world, "main", "WebFetch", "toolu_tb_denied_" + name,
                     {"url": "https://%s.denied.example.test/path?q=1" % name, "prompt": "FIXTURE"},
                     result="error", denial=kind)


def test_a_permission_rule_denial_is_detected(world, run):
    out = run(world)
    manifest = assert_ok(out)
    assert manifest["egress_denied"] == [{"host": "example.com", "kind": "permission-rule", "count": 1}]
    assert "example.com" not in {e["host"] for e in manifest["egress_observed"]}, "a denied call is not observed egress"
    assert out.summary["denials_seen"] == 1 and out.summary["unrecognised_denial_kinds"] == {}
    # detecting a denial is not validating the detection: nothing is validated for these versions
    assert manifest["denial_detection"] == {"status": "not-validated", "validated_claude_code_versions": []}


@pytest.mark.parametrize("kind", ["sandbox", "classifier", "permission-rule"])
def test_each_recognised_denial_kind_is_listed_with_its_host(world, run, kind):
    _denied_web_fetch(world, kind, kind)
    manifest = assert_ok(run(world))
    assert {"host": kind + ".denied.example.test", "kind": kind, "count": 1} in manifest["egress_denied"]
    assert kind + ".denied.example.test" not in {e["host"] for e in manifest["egress_observed"]}
    keys = [(d["host"], d["kind"]) for d in manifest["egress_denied"]]
    assert keys == sorted(keys)
    assert manifest["denial_detection"]["status"] == "not-validated"


@pytest.mark.parametrize("marker", ["a-kind-from-the-future", 5, None, ""], ids=["unknown-string", "integer", "null", "empty"])
def test_an_unrecognised_denial_kind_gives_not_validated_even_for_a_validated_version(world, run, archiver, monkeypatch, marker):
    """Fail closed: the call is still treated as denied, but the detection can no longer be called validated."""
    monkeypatch.setattr(archiver, "VALIDATED_DENIAL_VERSIONS", frozenset([world.spec["version"]]))
    _denied_web_fetch(world, "future", marker)
    out = run(world)
    manifest = assert_ok(out)
    assert manifest["denial_detection"] == {"status": "not-validated",
                                            "validated_claude_code_versions": [world.spec["version"]]}
    assert "future.denied.example.test" not in {e["host"] for e in manifest["egress_observed"]}, \
        "an unrecognised denial still marks the call denied"
    assert "future.denied.example.test" not in {e["host"] for e in manifest["egress_denied"]}
    assert sum(out.summary["unrecognised_denial_kinds"].values()) == 1
    assert out.summary["denials_seen"] == 2  # the fixture's permission-rule denial and this one
    assert any("unrecognised kind" in w for w in out.summary["warnings"])


def test_an_empty_denial_list_is_not_read_as_none_denied(world, run, archiver, monkeypatch):
    """With the fixture's denial removed the list is empty; only a validated version may call that "none"."""
    update_results(world, "toolu_fx%d_main_02" % world.number, lambda block, line: line.pop("toolDenialKind", None))
    first = assert_ok(run(world))
    assert first["egress_denied"] == []
    assert first["denial_detection"]["status"] == "not-validated"
    monkeypatch.setattr(archiver, "VALIDATED_DENIAL_VERSIONS", frozenset([world.spec["version"]]))
    second = assert_ok(run(world, dest=world.dest.parent / "validated" / "archive"))
    assert second["egress_denied"] == [] and second["denial_detection"]["status"] == "validated"


def test_denial_detection_fails_closed_with_mixed_versions(world, run, archiver, monkeypatch, tmp_path):
    """validated only when EVERY observed version has a recorded check; the list names the validated subset."""
    other = "2.1.999"
    edit_lines(world, world.role_paths("spoofing")[0], lambda o: o.__setitem__("version", other) if "version" in o else None)
    versions = sorted([world.spec["version"], other], key=_numeric_key)

    def detection(validated, name):
        monkeypatch.setattr(archiver, "VALIDATED_DENIAL_VERSIONS", frozenset(validated))
        manifest = assert_ok(run(world, dest=tmp_path / name / "archive"))
        assert manifest["claude_code_versions"] == versions
        return manifest["denial_detection"]

    assert detection([], "none") == {"status": "not-validated", "validated_claude_code_versions": []}
    assert detection([world.spec["version"]], "first") == {"status": "not-validated",
                                                            "validated_claude_code_versions": [world.spec["version"]]}
    assert detection([other], "second") == {"status": "not-validated", "validated_claude_code_versions": [other]}
    assert detection(versions, "both") == {"status": "validated", "validated_claude_code_versions": versions}
    # a recorded check for a version the session never ran changes nothing
    assert detection(versions + ["9.9.9"], "extra") == {"status": "validated", "validated_claude_code_versions": versions}


def test_a_session_with_no_version_at_all_is_never_validated(world, run, archiver, monkeypatch):
    for path in world.transcripts():
        edit_lines(world, path, lambda o: o.pop("version", None))
    monkeypatch.setattr(archiver, "VALIDATED_DENIAL_VERSIONS", frozenset([world.spec["version"], "2.1.999"]))
    manifest = assert_ok(run(world))
    assert manifest["claude_code_versions"] == []
    assert manifest["denial_detection"] == {"status": "not-validated", "validated_claude_code_versions": []}


def test_the_shipped_validated_versions_never_come_from_the_synthetic_fixtures():
    """Only a recorded run may add a version (T035). The invented older generation never can."""
    spec = importlib.util.spec_from_file_location("archiver_as_shipped", str(SCRIPT))
    shipped = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(shipped)
    assert isinstance(shipped.VALIDATED_DENIAL_VERSIONS, frozenset)
    assert GENERATIONS["gen1"]["version"] not in shipped.VALIDATED_DENIAL_VERSIONS
    for version in shipped.VALIDATED_DENIAL_VERSIONS:
        assert re.match(r"\d+(\.\d+)+\Z", version), version


def test_a_denial_whose_call_names_no_host_is_listed_not_dropped(world, run):
    """B1 interpretation 2: a denied Read, or a call with no URL, is listed under the host "<unparseable>" and counted."""
    append_tool_call(world, "main", "Read", "toolu_tb_denied_read", {"file_path": "/somewhere/else"},
                     result="error", denial="sandbox")
    manifest = assert_ok(run(world))
    assert {"host": UNPARSEABLE, "kind": "sandbox", "count": 1} in manifest["egress_denied"]
    assert manifest["egress_unparsed_count"] == 1


def test_a_denied_dispatch_is_a_failed_dispatch(world, run):
    """P0B0-2(d), the denied variant: no meta and the call was denied, so dispatch-failed and never no-transcript."""
    orch = world.agent_id("orchestrator")
    append_tool_call(world, orch, world.spec["dispatch_tool"], "toolu_tb_denied_dispatch",
                     dispatch_input("tachi-misinformation"), result="error", denial="permission-rule")
    manifest = assert_ok(run(world))
    assert {"agent": "tachi-misinformation", "tool_use_id": "toolu_tb_denied_dispatch", "spawn_depth": 2,
            "dispatched_from": orch, "status": "dispatch-failed"} in manifest["dispatches"]
    assert {"agent": "tachi-misinformation", "tool_use_id": "toolu_tb_denied_dispatch", "dispatched_from": orch,
            "reason": "dispatch-failed"} in manifest["tachi_agents_not_recorded"]
    assert "tachi-misinformation" not in manifest["tachi_agents_not_dispatched"]


def test_a_url_in_a_bash_command_or_webfetch_is_reduced_to_its_host(world, run):
    """Userinfo, port, path, query and fragment never reach the manifest; odd URLs are counted as unparseable."""
    commands = [
        "curl https://user:" + "pw@Mixed-Case.Example.test:8443/a/b?c=d#e",  # userinfo with a password, built in two pieces
        "curl 'http://[2001:db8::1]:8080/x'",
        "git clone ssh://git@code.example.test/repo.git",
        "echo file:///etc/passwd && echo no url here",
    ]
    for index, command in enumerate(commands):
        append_tool_call(world, "main", "Bash", "toolu_tb_url_%d" % index, {"command": command})
    append_tool_call(world, "main", "WebFetch", "toolu_tb_url_bad", {"url": "not a url at all"})
    out = run(world)
    manifest = assert_ok(out)
    hosts = {(e["host"], e["tool"]) for e in manifest["egress_observed"]}
    assert ("mixed-case.example.test", "Bash") in hosts
    assert ("2001:db8::1", "Bash") in hosts
    assert ("code.example.test", "Bash") in hosts
    assert (UNPARSEABLE, "WebFetch") in hosts
    assert not [h for h, _t in hosts if "file" == h or "passwd" in h]
    assert manifest["egress_unparsed_count"] == 1
    text = out.manifest_path.read_text(encoding="utf-8")
    for leaked in ("pw@", ":8443", "/a/b", "c=d", "#e", ":8080", "git@"):
        assert leaked not in text, leaked


# =============================================================================
# Roster, pins and the version marker
# =============================================================================


def agent_file(world, name):
    return world.project_dir / ".claude" / "agents" / "tachi" / (name + ".md")


def test_the_roster_is_the_name_values_of_the_installed_agent_files(world, run):
    agents = world.project_dir / ".claude" / "agents" / "tachi"
    world.write_text(agents / "zz-extra.md", "---\nname: tachi-extra-agent\nmodel: opus\n---\nstub\n")
    world.write_text(agents / "helper.md", "---\nname: helper\nmodel: sonnet\n---\nnot a tachi agent\n")
    world.write_text(agents / "no-frontmatter.md", "name: tachi-no-frontmatter\n")
    world.write_text(agents / "notes.txt", "---\nname: tachi-not-markdown\n---\n")
    (agents / "linked.md").symlink_to(agent_file(world, "spoofing"))
    manifest = assert_ok(run(world))
    assert manifest["tachi_agents_not_dispatched"] == sorted(list(NOT_DISPATCHED) + ["tachi-extra-agent"])


def test_a_missing_permissions_matrix_is_not_an_error(world, run):
    assert not (world.project_dir / "docs").exists()
    assert_ok(run(world))


@pytest.mark.parametrize("line,expected", [
    ("model: opus", "opus"),
    ('model: "haiku"', "haiku"),
    ("model: 'claude-sonnet-5-5'", "claude-sonnet-5-5"),
    ("model: sonnet # the alias", "sonnet"),
    (None, None),
], ids=["opus", "double-quoted", "single-quoted", "trailing-comment", "no-model-line"])
def test_pinned_model_is_the_alias_exactly_as_the_agent_file_writes_it(world, run, line, expected):
    """The archiver never resolves an alias and never compares the pin with what served."""
    path = agent_file(world, "spoofing")
    text = world.read_text(path)
    assert "model: sonnet\n" in text
    world.write_text(path, text.replace("model: sonnet\n", "" if line is None else line + "\n"))
    manifest = assert_ok(run(world))
    by = by_type(manifest["subagents"])
    assert by["tachi-spoofing"]["pinned_model"] == expected
    assert by["tachi-spoofing"]["served_model_histogram"] == {world.spec["sub_model"]: 2}
    assert by["tachi-tampering"]["pinned_model"] == "sonnet"


def test_a_missing_agents_directory_exits_2_before_anything_is_written(world, run):
    agents = world.project_dir / ".claude" / "agents" / "tachi"
    for path in sorted(agents.iterdir()):
        path.unlink()
    agents.rmdir()
    out = run(world)
    assert_failed(out, rc=2, mentions=("no installed tachi agents",))
    assert not out.dest.exists()


def test_a_roster_with_no_tachi_name_exits_2(world, run):
    agents = world.project_dir / ".claude" / "agents" / "tachi"
    for path in sorted(agents.iterdir()):
        world.write_text(path, "---\nname: helper-%s\nmodel: sonnet\n---\n" % path.stem)
    out = run(world)
    assert_failed(out, rc=2, mentions=("no installed tachi agents",))
    assert not out.dest.exists()


@pytest.mark.parametrize("content,expected", [
    ("tachi_version: v4.49.0-3-gabc1234\n", "v4.49.0-3-gabc1234"),
    ("tachi_version: v4.1.0", "v4.1.0"),
    ("tachi_version: unknown\n", "unknown"),
    ("", "unknown"),
    ("tachi_version:\n", "unknown"),
    ("other_key: v4.1.0\n", "unknown"),
    ("tachi_version: v1\ntachi_version: v2\n", "unknown"),
    ("# a comment\ntachi_version: v1\n", "unknown"),
    ("tachi_version: two words\n", "unknown"),
    ("tachi_version: v1\n\n", "unknown"),
], ids=["describe", "no-newline", "unknown", "empty", "no-value", "wrong-key", "two-lines", "comment-first",
        "inner-space", "trailing-blank-line"])
def test_the_version_marker_is_read_as_the_stamp_reads_it(world, run, content, expected):
    marker = world.project_dir / "templates" / "tachi" / "VERSION"
    marker.parent.mkdir(parents=True, exist_ok=True)
    world.write_text(marker, content)
    assert assert_ok(run(world))["tachi_version"] == expected


def test_an_absent_or_unusual_version_marker_reads_unknown(world, run, tmp_path):
    marker = world.project_dir / "templates" / "tachi" / "VERSION"
    if marker.exists():
        marker.unlink()
    assert assert_ok(run(world, dest=tmp_path / "a" / "archive"))["tachi_version"] == "unknown"
    marker.parent.mkdir(parents=True, exist_ok=True)
    real = tmp_path / "real-version"
    real.write_text("tachi_version: v9.9.9\n", encoding="utf-8")
    marker.symlink_to(real)
    assert assert_ok(run(world, dest=tmp_path / "b" / "archive"))["tachi_version"] == "unknown", "a symlinked marker is not read"
    marker.unlink()
    world.write_text(marker, "tachi_version: v1\n" + "#" * 5000)
    assert assert_ok(run(world, dest=tmp_path / "c" / "archive"))["tachi_version"] == "unknown", "an oversized marker is not read"
    marker.unlink()
    marker.mkdir()
    assert assert_ok(run(world, dest=tmp_path / "d" / "archive"))["tachi_version"] == "unknown"


def test_the_version_is_read_from_the_marker_and_from_no_other_file(world, run):
    for name in ("VERSION", ".claude/VERSION", "templates/VERSION", ".claude/agents/tachi/VERSION"):
        path = world.project_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        world.write_text(path, "tachi_version: v0.0.0-from-the-wrong-file\n")
    marker = world.project_dir / "templates" / "tachi" / "VERSION"
    if marker.exists():
        marker.unlink()
    assert assert_ok(run(world))["tachi_version"] == "unknown"


# =============================================================================
# The run's output directory
# =============================================================================


def test_output_dir_files_are_hashed_sorted_and_relative(world, run, tmp_path):
    out_dir = tmp_path / "run-output"
    (out_dir / "sub" / "deeper").mkdir(parents=True)
    contents = {"threats.md": b"# threats\n", "sub/risk-scores.md": b"scores", "sub/deeper/z.sarif": b"{}",
                "A-first.txt": b"", "threats.sarif": bytes(range(256))}
    for rel, data in contents.items():
        (out_dir / rel).write_bytes(data)
    (out_dir / "link-dir").symlink_to(tmp_path, target_is_directory=True)
    (out_dir / "link.txt").symlink_to(out_dir / "threats.md")
    out = run(world, output_dir=out_dir)
    manifest = assert_ok(out)
    expected = [{"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                for rel, data in sorted(contents.items())]
    assert manifest["artifacts"] == expected
    assert "artifacts_reason" not in manifest
    assert any("symbolic link" in w for w in out.summary["warnings"])
    assert any("non-regular" in w for w in out.summary["warnings"])


def test_an_empty_output_dir_is_an_empty_list_not_null(world, run, tmp_path):
    (tmp_path / "empty-output").mkdir()
    manifest = assert_ok(run(world, output_dir=tmp_path / "empty-output"))
    assert manifest["artifacts"] == [] and "artifacts_reason" not in manifest


def test_an_output_dir_that_is_not_a_directory_exits_2(world, run, tmp_path):
    not_a_dir = tmp_path / "file.txt"
    not_a_dir.write_text("x", encoding="utf-8")
    out = run(world, output_dir=not_a_dir)
    assert_failed(out, rc=2, mentions=("--output-dir is not a directory",))
    assert not out.dest.exists()


# =============================================================================
# Discovery by cwd, and the exit-2 infrastructure cases
# =============================================================================


def test_discovery_matches_the_transcripts_cwd_not_the_directory_name(world, run):
    renamed = world.config_dir / "projects" / "-a-completely-different-name"
    os.rename(str(world.slug_dir), str(renamed))
    manifest = assert_ok(run(world))
    assert manifest["session_id"] == world.session_id


def test_a_symlinked_project_dir_still_matches_by_real_path(world, run, tmp_path):
    link = tmp_path / "project-link"
    link.symlink_to(world.project_dir, target_is_directory=True)
    assert_ok(run(world, project_dir=link))


def test_another_projects_transcripts_are_never_selected(world, run, tmp_path):
    other = tmp_path / "other-project"
    shutil.copytree(str(world.project_dir), str(other))
    out = run(world, project_dir=other)
    assert_failed(out, rc=2, mentions=("--project-dir",))
    assert not out.dest.exists()
    latest = run(world, project_dir=other, latest=True, dest=tmp_path / "x" / "archive")
    assert_failed(latest, rc=2, mentions=("--project-dir",))


def test_latest_picks_the_newest_main_transcript_of_this_project_only(world, run, tmp_path):
    """A newer session of another project is ignored; a newer session of this one wins over --session's default."""
    foreign_slug = world.config_dir / "projects" / "-another-project"
    foreign_slug.mkdir()
    foreign = foreign_slug / "99999999-9999-4999-8999-999999999999.jsonl"
    world.write_jsonl(foreign, [{"type": "user", "cwd": str(tmp_path / "somewhere-else"), "timestamp": STAMP,
                                 "message": {"role": "user", "content": "FIXTURE"}}])
    world.age_file(foreign, seconds=600)  # newer than the fixture's one hour, still not live
    manifest = assert_ok(run(world, latest=True))
    assert manifest["session_id"] == world.session_id
    # a newer session of this project: --latest takes it, --session still takes the named one
    newer_id = "88888888-8888-4888-8888-888888888888"
    newer = world.slug_dir / (newer_id + ".jsonl")
    world.write_bytes(newer, world.read_bytes(world.main_path))
    world.age_file(newer, seconds=900)
    latest = run(world, latest=True, dest=tmp_path / "latest" / "archive")
    assert latest.rc == 0, latest.err
    assert latest.manifest()["session_id"] == newer_id
    named = run(world, dest=tmp_path / "named" / "archive")
    assert named.manifest()["session_id"] == world.session_id


def test_a_missing_projects_directory_exits_2(world, run, tmp_path):
    empty = tmp_path / "empty-claude-config"
    empty.mkdir()
    assert_failed(run(world, config_dir=empty), rc=2, mentions=("projects directory not found", "CLAUDE_CONFIG_DIR"))


def test_the_session_id_must_be_a_plain_token_that_exists(world, run):
    for bad in ("../escape", "a/b", ".hidden", "with space", "x" * 200):
        assert_failed(run(world, session=bad), rc=2, mentions=("not a valid session id",))
    assert_failed(run(world, session="77777777-7777-4777-8777-777777777777"), rc=2,
                  mentions=("no transcript for that session id",))


@pytest.mark.parametrize("args", [[], ["--session", "x", "--latest"]], ids=["neither", "both"])
def test_exactly_one_of_session_and_latest_is_required(archiver, capsys, args):
    with pytest.raises(SystemExit) as exc:
        archiver.main(args)
    assert exc.value.code == 2
    assert "usage:" in capsys.readouterr().err


@pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="root reads any file")
def test_an_unreadable_transcript_file_exits_2(world, run):
    victim = world.results_dir / ("toolu_fx%d_gp_01.txt" % world.number)
    os.chmod(str(victim), 0)
    try:
        out = run(world)
    finally:
        os.chmod(str(victim), 0o600)
    assert_failed(out, rc=2, mentions=("cannot read",))


# -- the rest of discovery and the destination (cli-contracts.md) ------------------------------------------------


@pytest.mark.parametrize("link_side", ["project-dir", "transcript-cwd"])
def test_discovery_compares_real_paths_on_both_sides(world, run, tmp_path, link_side):
    """P0B0-4(h): a symlinked --project-dir and a transcript whose cwd is the symlink both still match."""
    link = tmp_path / "project-link"
    link.symlink_to(world.project_dir, target_is_directory=True)
    if link_side == "project-dir":
        assert_ok(run(world, project_dir=link))
        return
    real = os.path.realpath(str(world.project_dir))
    world.edit_text(world.main_path, lambda text: text.replace(json.dumps(real)[1:-1], json.dumps(str(link))[1:-1]))
    assert str(link) in world.read_text(world.main_path)
    assert_ok(run(world))


def test_permission_modes_are_empty_when_the_session_has_none(world, run):
    for path in world.transcripts():
        world.write_jsonl(path, [o for o in world.read_jsonl(path) if o.get("type") != "permission-mode"])
    out = run(world)
    manifest = assert_ok(out)
    assert manifest["permission_modes_seen"] == []
    assert out.summary["permission_mode_entries"] == 0


def test_a_permission_mode_entry_without_a_readable_mode_is_counted_not_listed(world, run):
    world.write_jsonl(world.main_path, world.read_jsonl(world.main_path) + [{"type": "permission-mode"}])
    out = run(world)
    manifest = assert_ok(out)
    assert manifest["permission_modes_seen"] == [world.spec["mode"]]
    assert out.summary["permission_mode_entries_without_a_mode"] == 1


def test_the_default_destination_date_is_the_first_timestamp_in_utc(world, run):
    """A first timestamp late on the 18th in New York is already the 19th in UTC."""
    first = {"type": "last-prompt", "timestamp": "2026-11-18T23:30:00-05:00"}
    world.write_jsonl(world.main_path, [first] + world.read_jsonl(world.main_path))
    out = run(world, dest=None)
    assert_ok(out)
    assert Path(out.summary["archive_dir"]).name == "2026-11-19-" + world.session_id


def test_the_default_destination_names_the_project_after_its_directory(tmp_path, run):
    """Characters outside letters, digits, dot, dash and underscore become underscores."""
    world = build_world(tmp_path, "gen2", project_name="my project (v2)")
    out = run(world, dest=None)
    assert_ok(out)
    archive = Path(out.summary["archive_dir"])
    assert archive.parent.name == "my_project__v2_"
    assert archive.parent.parent == Path(os.environ["HOME"]) / ".tachi" / "runs"


def test_the_json_summary_is_sorted_two_space_indented_json(world, run):
    out = run(world)
    assert_ok(out)
    assert out.out == json.dumps(out.summary, sort_keys=True, indent=2) + "\n"
    assert out.summary["session_id"] == world.session_id
    assert Path(out.summary["manifest"]) == out.manifest_path
    assert out.summary["turns"] == {"main": 5, "subagents": sum(t for t, _s in world.spec["turns"].values())}


# -- egress counting, file naming and large files (B1's documented interpretations) --------------------------------------


def test_a_host_counts_once_per_call_and_once_per_further_call(world, run):
    """One Bash call naming a host twice counts once; a second call naming it counts again."""
    append_tool_call(world, "main", "Bash", "toolu_tb_twice",
                     {"command": "curl https://repeat.example.test/a && curl https://repeat.example.test/b"})
    append_tool_call(world, "main", "Bash", "toolu_tb_again", {"command": "curl https://repeat.example.test/c"})
    manifest = assert_ok(run(world))
    assert {"host": "repeat.example.test", "tool": "Bash", "count": 2} in manifest["egress_observed"]


def test_only_bash_commands_and_webfetch_urls_are_read_for_hosts(world, run):
    """Other tools' inputs are not scanned for URLs (a documented simplification of version 1)."""
    append_tool_call(world, "main", "Read", "toolu_tb_read_url", {"file_path": "https://not-scanned.example.test/x"})
    append_tool_call(world, "main", "Write", "toolu_tb_write_url",
                     {"file_path": "/x", "content": "see https://also-not-scanned.example.test/"})
    manifest = assert_ok(run(world))
    assert manifest["egress_observed"] == EXPECTED_EGRESS


@pytest.mark.parametrize("naming", ["bare-id", "plain-json-sidecar"])
def test_subagent_file_naming_variants(world, run, tmp_path, naming):
    """Files named by the bare id are read like agent-<id> files; a sidecar that is not *.meta.json fails closed."""
    baseline = assert_ok(run(world, dest=tmp_path / "baseline" / "archive"))
    for role in ROLES:
        jsonl, meta = world.role_paths(role)
        if naming == "bare-id":
            os.rename(str(jsonl), str(jsonl.with_name(world.agent_id(role) + ".jsonl")))
            os.rename(str(meta), str(meta.with_name(world.agent_id(role) + ".meta.json")))
        else:
            os.rename(str(meta), str(meta.with_name("agent-%s.json" % world.agent_id(role))))
    out = run(world)
    if naming == "plain-json-sidecar":
        assert_failed(out, mentions=("without a metadata file",))
        return
    manifest = assert_ok(out)
    for field in ("main", "dispatches", "subagents", "tachi_agents_not_recorded", "tachi_agents_not_dispatched"):
        assert manifest[field] == baseline[field], field


def test_a_large_file_is_copied_and_hashed_in_chunks(world, run):
    """Bigger than the 1 MiB copy chunk, and not a multiple of it."""
    data = (b"0123456789abcdef" * 163840) + b"tail"
    world.write_bytes(world.results_dir / "big-output.bin", data)
    out = run(world)
    manifest = assert_ok(out)
    rel = "%s/tool-results/big-output.bin" % world.session_id
    entry = [t for t in manifest["transcripts"] if t["path"] == rel]
    assert entry == [{"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}]
    assert (out.dest / rel).read_bytes() == data
    assert len(manifest["transcripts"]) == 16


def test_files_outside_the_transcript_set_are_archived_but_never_parsed(world, run):
    """The whole session directory is copied verbatim; only subagents/*.jsonl and *.meta.json are read."""
    extras = {
        "tool-results/garbage.jsonl": b"{this is not json\n",
        "tool-results/binary.dat": bytes(range(256)) * 4,
        "subagents/notes.txt": b"a note, not a transcript\n",
        "future-directory/nested/anything.bin": b"\x00\x01\x02",
    }
    for rel, data in extras.items():
        path = world.session_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        world.write_bytes(path, data)
    out = run(world)
    manifest = assert_ok(out)
    listed = {t["path"]: t for t in manifest["transcripts"]}
    assert len(listed) == 15 + len(extras)
    for rel, data in extras.items():
        entry = listed["%s/%s" % (world.session_id, rel)]
        assert entry["sha256"] == hashlib.sha256(data).hexdigest() and entry["bytes"] == len(data)
        assert (out.dest / world.session_id / rel).read_bytes() == data
    assert [s["agent_type"] for s in manifest["subagents"] if s["agent_type"] == "notes"] == []


# =============================================================================
# The command line as a real process
# =============================================================================


def test_the_cli_as_a_real_process_agrees_with_the_in_process_run(world, run, tmp_path):
    """``python -I -B scripts/archive-run-transcripts.py``: same manifest, JSON summary on stdout, warnings on stderr."""
    in_process = assert_ok(run(world, dest=tmp_path / "in-process" / "archive"))
    target = tmp_path / "process" / "archive"
    proc = run_subprocess(world, "--session", world.session_id, "--project-dir", world.project_dir, "--json", dest=target)
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout)["status"] == "archived"
    assert proc.stderr.startswith("[391] warning: 1 successful tachi dispatch(es) have no subagent transcript")
    manifest = json.loads((target / MANIFEST).read_text(encoding="utf-8"))
    for each in (manifest, in_process):
        each.pop("archived_at")
    assert manifest == in_process
    assert archived_tree(target).pop(MANIFEST)


def test_the_cli_human_line_and_the_no_op_as_a_real_process(world, tmp_path):
    target = tmp_path / "process" / "archive"
    args = ("--latest", "--project-dir", world.project_dir)
    first = run_subprocess(world, *args, dest=target)
    assert first.returncode == 0 and first.stdout.startswith("[391] archived session %s to " % world.session_id)
    again = run_subprocess(world, *args, dest=target)
    assert again.returncode == 0 and "already archived" in again.stdout and again.stderr == ""


def test_exit_codes_reach_the_shell(world, tmp_path):
    os.utime(str(world.main_path), None)  # a live session: refused
    refused = run_subprocess(world, "--session", world.session_id, "--project-dir", world.project_dir,
                             dest=tmp_path / "live" / "archive")
    assert refused.returncode == 1 and refused.stderr.startswith("[391] ") and "looks live" in refused.stderr
    assert refused.stdout == ""
    missing = run_subprocess(world, "--session", world.session_id, "--project-dir", tmp_path / "does-not-exist",
                             dest=tmp_path / "x" / "archive")
    assert missing.returncode == 2 and "--project-dir is not a directory" in missing.stderr


def test_help_names_the_program_and_every_option(gen2):
    proc = run_subprocess(gen2, "--help", dest=None)
    assert proc.returncode == 0
    assert "archive-run-transcripts.py" in proc.stdout
    for option in ("--session", "--latest", "--project-dir", "--dest", "--output-dir", "--allow-live",
                   "--live-window-seconds", "--json"):
        assert option in proc.stdout, option


@pytest.mark.parametrize("args", [(), ("--session", "x", "--latest")], ids=["neither", "both"])
def test_a_real_process_without_exactly_one_session_selector_exits_2(gen2, args):
    proc = run_subprocess(gen2, *args, dest=None)
    assert proc.returncode == 2 and "usage:" in proc.stderr


# =============================================================================
# The isolation guard itself
# =============================================================================


def test_the_tests_run_in_an_isolated_environment(scratch_root):
    assert _inside(os.environ["HOME"], scratch_root) and not _is_forbidden_state(os.environ["HOME"])
    assert _inside(os.environ["CLAUDE_CONFIG_DIR"], scratch_root)
    assert not [name for name in os.environ if _SECRET_NAME_RE.search(name)], "a secret-named variable leaked in"
    assert not [name for name in _GIT_LOCATION_VARS if name in os.environ]
    assert os.path.realpath(os.path.expanduser("~")) != REAL_HOME


def test_the_runner_refuses_to_aim_the_archiver_at_state_it_must_not_touch(world, run, tmp_path, monkeypatch):
    """The guard trips before any archiver code runs; the "real" state directory here is a stand-in in scratch."""
    stand_in = tmp_path / "pretend-home" / ".tachi"
    monkeypatch.setattr(sys.modules[__name__], "FORBIDDEN_STATE_DIRS", (os.path.realpath(str(stand_in)),))
    with pytest.raises(AssertionError, match="outside the scratch directory"):
        run(world, dest=stand_in / "runs" / "archive")
    assert not stand_in.exists()
    with pytest.raises(AssertionError, match="outside the scratch directory"):
        run(world, dest=Path(os.path.dirname(os.path.realpath(__file__))) / "never-created")


# =============================================================================
# Guards: stdlib-only (P0B0-8), Python 3.9, no key-shaped literal in this file
# =============================================================================


def imported_modules(tree):
    """(line, top-level module) for every import statement anywhere in the tree."""
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [(node.lineno, alias.name.split(".")[0]) for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            found.append((node.lineno, (node.module or "").split(".")[0]))
    return found


def post_39_api_uses(tree):
    """Names the hard rule forbids in installed scripts (Python 3.9 floor), found by syntax tree."""
    banned_attributes = ("file_digest", "fromisoformat", "pairwise", "bit_count")
    banned_names = ("ExceptionGroup", "BaseExceptionGroup", "tomllib")
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            if node.attr in banned_attributes:
                found.append((node.lineno, node.attr))
            if node.attr == "UTC" and isinstance(node.value, ast.Name) and node.value.id == "datetime":
                found.append((node.lineno, "datetime.UTC"))
        elif isinstance(node, ast.Name) and node.id in banned_names:
            found.append((node.lineno, node.id))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "zip" \
                and any(keyword.arg == "strict" for keyword in node.keywords):
            found.append((node.lineno, "zip(strict=)"))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            found += [(node.lineno, "tomllib") for _l, name in imported_modules(ast.Module(body=[node], type_ignores=[]))
                      if name == "tomllib"]
    return found


def test_the_script_imports_only_the_standard_library():
    """P0B0-8: the 3.9 step installs PyYAML, so only this check can see a third-party import."""
    if sys.version_info < (3, 10):
        pytest.skip("sys.stdlib_module_names needs Python >= 3.10 (P0B0-8)")
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"), filename=str(SCRIPT))
    imports = imported_modules(tree)
    assert len(imports) >= 10, "the walk found suspiciously few imports"
    outside = [(line, name) for line, name in imports if name not in sys.stdlib_module_names]
    assert outside == [], "not standard library: %s" % outside


def test_the_import_check_sees_module_level_and_deferred_third_party_imports():
    source = "import os\nimport yaml\nfrom requests import get\n\ndef later():\n    import numpy\n"
    assert {name for _l, name in imported_modules(ast.parse(source))} == {"os", "yaml", "requests", "numpy"}


@pytest.mark.parametrize("path", [SCRIPT, Path(__file__)], ids=["archiver", "this-module"])
def test_python_39_syntax(path):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path), feature_version=(3, 9))


def test_the_script_avoids_apis_newer_than_python_39():
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"), filename=str(SCRIPT))
    assert post_39_api_uses(tree) == []


def test_the_api_check_catches_what_it_is_for():
    source = ("import hashlib, datetime, tomllib\n"
              "hashlib.file_digest(f, 'sha256')\ndatetime.UTC\ndatetime.datetime.fromisoformat('x')\n"
              "zip(a, b, strict=True)\nExceptionGroup\n")
    names = sorted(name for _l, name in post_39_api_uses(ast.parse(source)))
    assert names == sorted(["file_digest", "datetime.UTC", "fromisoformat", "zip(strict=)", "ExceptionGroup", "tomllib"])


def test_this_module_holds_no_key_shaped_literal(archiver):
    """ADR-042, made executable: the archiver's own key patterns find nothing in this file's text."""
    text = Path(__file__).read_text(encoding="utf-8")
    hits = [(rule, match.group(0)[:6]) for rule, pattern in archiver._KEY_PATTERNS for match in [pattern.search(text)] if match]
    assert hits == [], "key-shaped text in the test module: assemble it from fragments instead: %s" % hits


# =============================================================================
# The schema document matches what the archiver writes
# =============================================================================


def _schema():
    import yaml  # PyYAML is already required by tests/scripts/conftest.py

    return yaml.safe_load(SCHEMA.read_text(encoding="utf-8"))["run_manifest"]


def test_the_schema_lists_exactly_the_manifest_fields(gen2, run, tmp_path):
    doc = _schema()
    fields = doc["fields"]
    out_dir = tmp_path / "run-output"
    out_dir.mkdir()
    (out_dir / "threats.md").write_bytes(b"# threats\n")
    plain = assert_ok(run(gen2))
    with_artifacts = assert_ok(run(gen2, output_dir=out_dir, dest=tmp_path / "artifacts" / "archive"))
    assert set(plain) == set(fields)
    assert set(with_artifacts) == set(fields) - {"artifacts_reason"}
    assert set(plain["main"]) == set(fields["main"]["fields"])
    assert set(plain["denial_detection"]) == set(fields["denial_detection"]["fields"])
    for key in ("transcripts", "dispatches", "subagents", "tachi_agents_not_recorded", "egress_observed",
                "egress_denied"):
        assert plain[key], key
        assert set(plain[key][0]) == set(fields[key]["item_schema"]), key
    assert set(with_artifacts["artifacts"][0]) == set(fields["artifacts"]["item_schema"])
    assert doc["manifest_version"] == plain["manifest_version"] == 1
    assert doc["file"] == MANIFEST and doc["mode"] == "0600"


def test_the_schema_enumerations_match_the_values_the_archiver_writes(world, run, archiver):
    doc = _schema()
    fields = doc["fields"]
    manifest = assert_ok(run(world))
    assert {d["status"] for d in manifest["dispatches"]} == set(fields["dispatches"]["item_schema"]["status"]["enum"]) \
        == set(doc["dispatch_states"])
    assert {n["reason"] for n in manifest["tachi_agents_not_recorded"]} == \
        set(fields["tachi_agents_not_recorded"]["item_schema"]["reason"]["enum"])
    assert set(fields["egress_denied"]["item_schema"]["kind"]["enum"]) == set(archiver.DENIAL_KINDS)
    assert manifest["denial_detection"]["status"] in fields["denial_detection"]["fields"]["status"]["enum"]
    assert set(fields["denial_detection"]["fields"]["status"]["enum"]) == {"validated", "not-validated"}
    description = " ".join(str(fields["subagents"]["item_schema"]["unknown_meta_keys"]["description"]).split())
    for name in archiver.KNOWN_META_KEYS:
        assert name in description, "the schema's list of known metadata keys lacks %s" % name


def test_the_schema_example_obeys_its_own_turn_invariant(archiver):
    example = _schema()["example"]
    for entry in [example["main"]] + example["subagents"]:
        assert entry["turns"] == sum(entry["served_model_histogram"].values()) + entry["synthetic_turns"]
    assert set(example) == set(_schema()["fields"])
    assert example["denial_detection"] == {"status": "not-validated", "validated_claude_code_versions": []}


# =============================================================================
# T034 review: one regression group per finding (H-1 to L-8)
# =============================================================================
#
# specs/391-isolated-auditable-operation/test-results/security-b1.md. Every test name starts
# ``test_t034_<finding>_``, so a finding can be run alone: ``pytest -k t034_h1``. Each group was written so
# that it fails against the archiver as it was before the fix pass (commit f9b5c0a) and passes after it.
# Key-shaped dummy values are assembled from fragments, as everywhere in this module.


# -- H-1: git must ignore every path the run writes, not a probe file ---------------------------------------------------

H1_PROBE_RULES = [".*", ".probe", ".p*", "*probe", "*.jsonl"]
H1_PROBE_IDS = ["dot-star", "probe", "p-star", "star-probe", "jsonl-only"]


@pytest.mark.parametrize("rule", H1_PROBE_RULES, ids=H1_PROBE_IDS)
def test_t034_h1_a_rule_that_matches_a_probe_file_but_not_the_files_the_run_writes_is_refused(world, run, tmp_path, rule):
    """Before the fix a probe at <dest>/.probe passed ``.*``, ``.probe``, ``.p*`` and ``*probe``: 16 committable files."""
    repo = init_repo(tmp_path / "repo", ignore=rule + "\n")
    before = source_digest(world)
    out = run(world, dest=repo / "runs" / "x")
    assert_failed(out, mentions=("not ignored",))
    assert not (repo / "runs").exists(), "a refused run created something in the work tree"
    assert repo_files(repo) == [".gitignore"]
    assert committable(repo) == []
    assert source_digest(world) == before


H1_PARTIAL_RULES = [
    ("runs/x/*\n!runs/x/run-manifest.json\n", "manifest-negated"),
    ("runs/x/*.jsonl\nruns/x/*/\n", "sources-only"),
    ("runs/x/*.jsonl\nruns/x/*/\nruns/x/run-manifest.json\n", "temporary-manifest-name-open"),
]


@pytest.mark.parametrize("rules", [r for r, _i in H1_PARTIAL_RULES], ids=[i for _r, i in H1_PARTIAL_RULES])
def test_t034_h1_every_path_counts_the_manifest_its_temporary_name_and_a_negated_rule(world, run, tmp_path, rules):
    repo = init_repo(tmp_path / "repo", ignore=rules)
    out = run(world, dest=repo / "runs" / "x")
    assert_failed(out, mentions=("not ignored",))
    assert not (repo / "runs").exists()


@pytest.mark.parametrize("rule", ["runs/", "/runs/", "runs/x/", "*\n!.gitignore"],
                         ids=["directory", "anchored-directory", "destination-itself", "whitelist-form"])
def test_t034_h1_a_directory_rule_and_the_whitelist_form_are_accepted_with_nothing_committable(world, run, tmp_path, rule):
    repo = init_repo(tmp_path / "repo", ignore=rule + "\n")
    out = run(world, dest=repo / "runs" / "x")
    assert_ok(out)
    assert committable(repo) == [], "an accepted destination left committable files in the work tree"


def test_t034_h1_a_path_the_work_tree_already_tracks_is_not_ignored_and_is_refused(world, run, tmp_path):
    """A tracked path stays committable whatever the ignore rules say: an index entry for a manifest path counts."""
    repo = init_repo(tmp_path / "repo", ignore="runs/\n")
    sha = git("hash-object", "-w", "--stdin", cwd=repo, input="tracked\n").stdout.strip()
    git("update-index", "--add", "--cacheinfo", "100644,%s,runs/x/%s" % (sha, MANIFEST), cwd=repo)
    out = run(world, dest=repo / "runs" / "x")
    assert_failed(out, mentions=("not ignored",))
    assert not (repo / "runs").exists()


def test_t034_h1_the_check_asks_about_the_manifest_and_its_temporary_name_too(world, run, tmp_path):
    """The only paths that distinguish the fix from a probe: the manifest and its temporary file are asked about."""
    repo = init_repo(tmp_path / "repo", ignore="runs/\n")
    asked = _record_git(tmp_path)
    out = run(world, dest=repo / "runs" / "x", env={"PATH": asked["path"]})
    assert_ok(out)
    stdin_paths = " ".join(asked["stdin"]())
    for name in (MANIFEST, MANIFEST_TMP, world.session_id + ".jsonl"):
        assert "/" + name in stdin_paths, "git was not asked about %s" % name


def test_t034_h1_a_work_tree_with_no_git_entry_gets_no_committable_files(world, run, tmp_path):
    """A bare repository used with --git-dir and --work-tree (a dotfiles layout): no .git entry for the
    archiver to find, so the archive's own .gitignore is what keeps it out of the work tree."""
    work = tmp_path / "work"
    work.mkdir()
    bare = tmp_path / "cfg.git"
    git("init", "--bare", "-q", bare)
    note = work / "note.txt"
    note.write_text("control", encoding="utf-8")
    assert committable(work, git_dir=bare) == ["note.txt"], "the layout is not live: git does not see an untracked file"
    note.unlink()
    out = run(world, dest=work / "runs" / "x")
    assert_ok(out)
    assert committable(work, git_dir=bare) == [], "the archive is committable in a work tree the archiver cannot see"
    assert (out.dest / ARCHIVE_GITIGNORE).is_file()


def test_t034_h1_the_archive_ignores_itself(world, run):
    out = run(world)
    manifest = assert_ok(out)
    path = out.dest / ARCHIVE_GITIGNORE
    rules = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    assert rules == ["*"]
    assert mode_of(path) == 0o600
    assert ARCHIVE_GITIGNORE not in {t["path"] for t in manifest["transcripts"]}
    assert out.summary["files"] == 15, "the archive's own file is not counted among the copied files"


def test_t034_h1_the_archives_own_ignore_file_is_written_before_anything_else(world, run):
    out = run(world)
    assert_ok(out)
    first = os.lstat(str(out.dest / ARCHIVE_GITIGNORE)).st_mtime_ns
    others = [os.lstat(str(p)).st_mtime_ns for p in out.dest.rglob("*") if p.is_file() and p.name != ARCHIVE_GITIGNORE]
    assert others and first <= min(others)


# -- H-2: git never runs a program the repository names, and never sees the secrets -----------------------------------


def _plant_fsmonitor(tmp_path, git_args):
    """A ``core.fsmonitor`` program in the repository named by ``git_args``; returns its marker file."""
    marker = tmp_path / "fsmonitor-ran.txt"
    hook = tmp_path / "fsmonitor-hook.sh"
    hook.write_text("#!/bin/sh\necho ran >> %s\nexit 0\n" % shlex.quote(str(marker)), encoding="utf-8")
    os.chmod(str(hook), 0o755)
    git(*(list(git_args) + ["config", "core.fsmonitor", str(hook)]))
    return marker


def _require_live_plant(marker, probe):
    """The attack only exists where git runs the program: prove it does here, then clear the marker."""
    git(*probe, check=False)
    if not marker.exists():
        pytest.skip("this git does not run a core.fsmonitor program for 'git status'; there is nothing to defend")
    marker.unlink()


@pytest.mark.parametrize("ignore,accepted", [("runs/\n", True), (None, False)], ids=["accepted-destination", "refused-destination"])
def test_t034_h2_a_planted_core_fsmonitor_program_never_runs(world, run, tmp_path, ignore, accepted):
    """Before the fix ``git check-ignore`` ran the program in the secret-bearing shell, for both outcomes."""
    repo = init_repo(tmp_path / "repo", ignore=ignore)
    marker = _plant_fsmonitor(tmp_path, ["-C", repo])
    _require_live_plant(marker, ["-C", repo, "status", "--porcelain"])
    out = run(world, dest=repo / "runs" / "x")
    assert (out.rc == 0) == accepted, out.err
    assert not marker.exists(), "git ran the repository's core.fsmonitor program during the destination check"


def test_t034_h2_the_operators_own_repository_is_asked_without_running_its_fsmonitor(world, run, tmp_path):
    """The query for GIT_DIR / GIT_WORK_TREE (M-4) is a new git call: it must carry the same protection."""
    work = tmp_path / "work"
    work.mkdir()
    (work / ".gitignore").write_text("runs/\n", encoding="utf-8")
    bare = tmp_path / "cfg.git"
    git("init", "--bare", "-q", bare)
    marker = _plant_fsmonitor(tmp_path, ["--git-dir", bare])
    _require_live_plant(marker, ["--git-dir", bare, "--work-tree", work, "status", "--porcelain"])
    out = run(world, dest=work / "runs" / "x", env={"GIT_DIR": str(bare), "GIT_WORK_TREE": str(work)})
    assert_ok(out)
    assert not marker.exists()


def _record_git(tmp_path):
    """Put a ``git`` wrapper first on PATH that logs each call's arguments, environment and stdin, then
    runs the real git. Returns {"path": the PATH to run with, "calls": ..., "stdin": ...}."""
    real = shutil.which("git")
    log = tmp_path / "git-calls.log"
    stdin_log = tmp_path / "git-stdin.log"
    fakebin = tmp_path / "fakebin"
    fakebin.mkdir(exist_ok=True)
    wrapper = fakebin / "git"
    wrapper.write_text(
        "#!/bin/sh\n"
        "{ echo \"ARGS:$*\"; env | sort; echo END; } >> %s\n"
        "case \"$*\" in *--stdin*) tee -a %s | %s \"$@\" ;; *) %s \"$@\" ;; esac\n"
        % (shlex.quote(str(log)), shlex.quote(str(stdin_log)), shlex.quote(real), shlex.quote(real)),
        encoding="utf-8")
    os.chmod(str(wrapper), 0o755)

    def calls():
        found, current = [], None
        for line in (log.read_text(encoding="utf-8", errors="replace").splitlines() if log.exists() else []):
            if line.startswith("ARGS:"):
                current = {"args": line[len("ARGS:"):], "env": {}}
                found.append(current)
            elif line == "END":
                current = None
            elif current is not None and re.match(r"[A-Za-z_][A-Za-z0-9_]*=", line):
                name, _eq, value = line.partition("=")
                current["env"][name] = value
        return found

    def stdin():
        raw = stdin_log.read_bytes() if stdin_log.exists() else b""
        return [part.decode("utf-8", "replace") for part in raw.split(b"\0") if part]

    return {"path": "%s%s%s" % (fakebin, os.pathsep, os.environ["PATH"]), "calls": calls, "stdin": stdin}


def test_t034_h2_git_runs_with_fsmonitor_off_and_an_allowlisted_environment(world, run, tmp_path):
    repo = init_repo(tmp_path / "repo", ignore="runs/\n")
    recorded = _record_git(tmp_path)
    secret = "wrapper-secret-" + _filler(12)
    out = run(world, dest=repo / "runs" / "x", env={
        "PATH": recorded["path"], "TACHI_TEST_API_KEY": secret, "TACHI_TEST_NOTE": "not-a-secret-either"})
    assert_ok(out)
    calls = recorded["calls"]()
    assert calls, "the archiver never started git"
    shell_added = {"PWD", "OLDPWD", "SHLVL", "_"}
    for call in calls:
        assert call["args"].startswith("-c core.fsmonitor=false "), call["args"]
        names = set(call["env"]) - shell_added
        assert {"HOME", "PATH"} <= names
        assert not [n for n in names if n.startswith("TACHI_TEST_")], "a test variable reached git: %s" % sorted(names)
        assert not [n for n in names if _SECRET_NAME_RE.search(n)], "a secret-named variable reached git"
        assert secret not in json.dumps(call["env"])
        assert call["env"].get("GIT_OPTIONAL_LOCKS") == "0"


# -- H-3: a plain start must not import a module planted beside the script ------------------------------------------------

PLANTED_MODULES = ("argparse", "ipaddress", "base64")


def _copy_script_with_planted_modules(tmp_path, script):
    """A copy of the script in its own ``scripts/`` directory, with stdlib-named modules planted beside it."""
    scripts = tmp_path / "planted" / "scripts"
    scripts.mkdir(parents=True)
    copy = scripts / "archive-run-transcripts.py"
    shutil.copyfile(str(script), str(copy))
    os.chmod(str(copy), 0o755)
    marker = tmp_path / "planted-module-ran.txt"
    for name in PLANTED_MODULES:
        (scripts / (name + ".py")).write_text(
            "with open(%r, 'a') as fh:\n    fh.write(%r + '\\n')\nraise SystemExit(97)\n" % (str(marker), name),
            encoding="utf-8")
    return copy, marker


def _plain_env(world):
    return {"PATH": os.environ.get("PATH", ""), "HOME": os.environ["HOME"], "CLAUDE_CONFIG_DIR": str(world.config_dir),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}


def _start(how, world, copy, tmp_path, *args):
    """Start the script the way an operator might, without ``-I``; returns the CompletedProcess."""
    scripts = copy.parent
    env = _plain_env(world)
    kwargs = dict(env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                  universal_newlines=True, timeout=60)
    if how == "plain":
        return subprocess.run([sys.executable, str(copy)] + list(args), **kwargs)
    if how == "inside-scripts-directory":
        return subprocess.run([sys.executable, copy.name] + list(args), cwd=str(scripts), **kwargs)
    if how == "symlink":
        link = tmp_path / "elsewhere" / "archive-link.py"
        link.parent.mkdir()
        link.symlink_to(copy)
        return subprocess.run([sys.executable, str(link)] + list(args), **kwargs)
    assert how == "shebang"
    return subprocess.run([str(copy)] + list(args), **kwargs)


@pytest.mark.parametrize("how", ["plain", "inside-scripts-directory", "symlink", "shebang"])
def test_t034_h3_a_stdlib_named_module_planted_beside_the_script_never_runs(world, tmp_path, how):
    """Before the fix a plain ``python3 scripts/archive-run-transcripts.py`` imported it, in the unsandboxed shell."""
    if how == "shebang" and not shutil.which("python3"):
        pytest.skip("the shebang line needs python3 on PATH")
    copy, marker = _copy_script_with_planted_modules(tmp_path, SCRIPT)
    # control: the plant is live. With the script's directory first on sys.path (a plain start), it runs.
    control = subprocess.run(
        [sys.executable, "-c", "import sys; sys.path.insert(0, %r); import ipaddress" % str(copy.parent)],
        env=_plain_env(world), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, timeout=60)
    assert control.returncode == 97 and marker.exists(), "the planted module is not live in this interpreter"
    marker.unlink()
    proc = _start(how, world, copy, tmp_path, "--help")
    assert not marker.exists(), "a module planted beside the script ran: %s" % marker.read_text(encoding="utf-8")
    assert proc.returncode == 0, proc.stderr
    assert "usage:" in proc.stdout


def test_t034_h3_a_plain_start_archives_normally_keeps_its_arguments_and_does_not_loop(world, tmp_path):
    """The guard restarts once under -I -B: the arguments survive, the archive is complete, the run ends."""
    copy, marker = _copy_script_with_planted_modules(tmp_path, SCRIPT)
    target = tmp_path / "plain-start" / "archive"
    proc = run_subprocess(world, "--session", world.session_id, "--project-dir", world.project_dir, "--json",
                          dest=target, isolated=False, script=copy, timeout=120)
    assert not marker.exists()
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout)["status"] == "archived"
    manifest = json.loads((target / MANIFEST).read_text(encoding="utf-8"))
    assert manifest["session_id"] == world.session_id
    assert archive_content(target) == {rel: sha256_file(path) for rel, path in world.source_tree().items()}


def test_t034_h3_a_plain_start_restarts_once_under_isolated_mode_and_an_isolated_start_not_at_all(world, tmp_path):
    """Measured with a sitecustomize on PYTHONPATH that logs each interpreter start that honours PYTHONPATH:
    a plain start is one such start (the restart is isolated and ignores PYTHONPATH); an isolated start is none."""
    hooks = tmp_path / "start-logger"
    hooks.mkdir()
    log = tmp_path / "interpreter-starts.log"
    (hooks / "sitecustomize.py").write_text(
        "import os, sys\nwith open(%r, 'a') as fh:\n    fh.write('start isolated=%%d\\n' %% sys.flags.isolated)\n" % str(log),
        encoding="utf-8")
    copy, marker = _copy_script_with_planted_modules(tmp_path, SCRIPT)
    plain = run_subprocess(world, "--help", dest=None, isolated=False, script=copy, timeout=60,
                           env={"PYTHONPATH": str(hooks)})
    assert plain.returncode == 0 and "usage:" in plain.stdout and not marker.exists()
    assert log.read_text(encoding="utf-8").splitlines() == ["start isolated=0"], "the restart is not isolated, or it looped"
    log.unlink()
    isolated = run_subprocess(world, "--help", dest=None, isolated=True, script=copy, timeout=60,
                              env={"PYTHONPATH": str(hooks)})
    assert isolated.returncode == 0 and not log.exists()


def test_t034_h3_the_isolated_start_needs_no_restart_and_the_docstring_recommends_it(world, tmp_path, archiver):
    copy, marker = _copy_script_with_planted_modules(tmp_path, SCRIPT)
    proc = run_subprocess(world, "--help", dest=None, isolated=True, script=copy, timeout=60)
    assert proc.returncode == 0 and "usage:" in proc.stdout and not marker.exists()
    assert "python3 -I -B scripts/archive-run-transcripts.py" in archiver.__doc__



# -- M-1: encoded forms of a secret ----------------------------------------------------------------------------------------
#
# A secret-named variable's value, re-encoded into a host label, a tachi- name, a tool name or a file name,
# is still found: raw, hex, base32, base64, base64url (no padding), percent-encoded and JSON-escaped, compared
# lower-cased. Each case runs twice on the same session: once without the variable (the carrier reaches the
# manifest and the run succeeds, so the carrier is real), once with it (the run fails).

SECRET_PLAIN = "fx-secret-" + _filler(14)   # letters, digits and hyphens: a stand-in for most secrets
SECRET_B64 = "fx~secret~" + _filler(12)     # its standard base64 holds "+" and its url-safe form "-"
SECRET_PCT = "p@ss:w/rd+" + _filler(12)     # characters percent-encoding changes
SECRET_JSON = 'ab"cd\\' + "ef" + _filler(12)  # characters JSON-escaping changes

FORM_ORDER = ["raw", "hex", "base32", "base64", "base64url", "percent", "json"]  # the order the archiver tries them


def encode_form(form, secret):
    raw = secret.encode("utf-8")
    return {
        "raw": secret,
        "hex": binascii.hexlify(raw).decode("ascii"),
        "base32": base64.b32encode(raw).decode("ascii").rstrip("=").lower(),
        "base64": base64.b64encode(raw).decode("ascii").rstrip("="),
        "base64url": base64.urlsafe_b64encode(raw).decode("ascii").rstrip("="),
        "percent": urllib.parse.quote(secret, safe=""),
        "json": json.dumps(secret)[1:-1],
    }[form]


def expected_form_label(secret, encoded):
    """The label the archiver reports: the first form (in its order) whose lower-cased text equals the plant."""
    seen = set()
    for form in FORM_ORDER:
        needle = encode_form(form, secret).lower()
        if needle in seen:
            continue
        seen.add(needle)
        if needle == encoded.lower():
            return form
    raise AssertionError("the planted text is not an encoded form of the secret")


def all_strings(node):
    """Every string in a parsed manifest, keys included."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield key
            for text in all_strings(value):
                yield text
    elif isinstance(node, list):
        for value in node:
            for text in all_strings(value):
                yield text


M1_FORMS = {
    "hex": (SECRET_PLAIN, ("host", "tachi-name", "tool-name", "artifact-name")),
    "base32": (SECRET_PLAIN, ("host", "tachi-name", "tool-name", "artifact-name")),
    "base64": (SECRET_B64, ("tachi-name", "tool-name", "artifact-name")),
    "base64url": (SECRET_B64, ("host", "tachi-name", "tool-name", "artifact-name")),
    "percent": (SECRET_PCT, ("tachi-name", "tool-name", "artifact-name")),
    "json": (SECRET_JSON, ("tachi-name", "tool-name", "artifact-name")),
}
M1_CASES = [(form, position) for form in sorted(M1_FORMS) for position in M1_FORMS[form][1]]


def plant_carrier(world, tmp_path, position, text):
    """Put ``text`` where model- or file-chosen text reaches the manifest; returns the --output-dir or None."""
    if position == "host":  # a DNS label: letters, digits, hyphen, underscore, wrapped so it starts and ends well
        append_tool_call(world, "main", "Bash", "toolu_tb_enc_host",
                         {"command": "curl https://x%sy.example.test/" % text.lower()})
    elif position == "tachi-name":
        add_dispatched_instance(world, world.agent_id("orchestrator"), world.agent_id(7), "tachi-" + text, "toolu_tb_enc_tachi")
    elif position == "tool-name":
        append_tool_call(world, "main", text, "toolu_tb_enc_tool", {"x": 1})
    else:
        out_dir = tmp_path / "enc-output"
        out_dir.mkdir()
        (out_dir / text).write_text("x", encoding="utf-8")
        return out_dir
    return None


@pytest.mark.parametrize("form,position", M1_CASES, ids=["%s-in-%s" % case for case in M1_CASES])
def test_t034_m1_an_encoded_secret_in_the_manifest_fails_the_run(world, run, tmp_path, form, position):
    secret = M1_FORMS[form][0]
    encoded = encode_form(form, secret)
    assert secret.lower() not in encoded.lower(), "the encoded form must differ from the raw value"
    out_dir = plant_carrier(world, tmp_path, position, encoded)
    control = run(world, output_dir=out_dir)
    manifest = assert_ok(control)
    assert any(encoded.lower() in text.lower() for text in all_strings(manifest)), "the carrier did not reach the manifest"
    leak = run(world, output_dir=out_dir, dest=tmp_path / "leak" / "archive", env={"TACHI_TEST_API_KEY": secret})
    label = expected_form_label(secret, encoded)
    assert_failed(leak, mentions=("secret scan", "environment variable TACHI_TEST_API_KEY (%s form)" % label))
    assert secret not in leak.text and encoded not in leak.text, "a value reached the output"


def test_t034_m1_the_raw_form_is_still_reported_without_a_form_label(world, run, tmp_path):
    out_dir = plant_carrier(world, tmp_path, "tool-name", SECRET_PLAIN)
    leak = run(world, output_dir=out_dir, env={"TACHI_TEST_API_KEY": SECRET_PLAIN})
    assert_failed(leak, mentions=("environment variable TACHI_TEST_API_KEY);",))  # one hit, and no "(... form)" suffix


# -- M-2: padded and multi-line values, and the names the scan reads ----------------------------------------------------


def pem_like(lines):
    head = "-" * 5 + "BEGIN " + "PRIVATE " + "KEY" + "-" * 5
    tail = "-" * 5 + "END " + "PRIVATE " + "KEY" + "-" * 5
    return "\n".join([head] + list(lines) + [tail])


PEM_LINE = _filler(32, salt=5)
M2_SHAPES = {
    "trailing-newline": (SECRET_PLAIN + "\n", SECRET_PLAIN),
    "trailing-space": (SECRET_PLAIN + " ", SECRET_PLAIN),
    "leading-space": ("  " + SECRET_PLAIN, SECRET_PLAIN),
    "json-blob-spaced": ('{"client": "client-id-0001", "secret": "%s"}' % SECRET_PLAIN, SECRET_PLAIN),
    "json-blob-compact": ('{"client":"client-id-0001","secret":"%s"}' % SECRET_PLAIN, SECRET_PLAIN),
    "pem-like": (pem_like([PEM_LINE, _filler(32, salt=9)]), PEM_LINE),
    "key-value-lines": ("API_KEY=%s\nOTHER_SETTING=plain-value" % SECRET_PLAIN, SECRET_PLAIN),
    "url-with-a-password": ("https://user" + ":" + SECRET_PLAIN + "@db.example.test/name", SECRET_PLAIN),
}


@pytest.mark.parametrize("shape", sorted(M2_SHAPES))
def test_t034_m2_a_padded_or_multi_line_value_is_still_found(world, run, tmp_path, shape):
    value, carrier = M2_SHAPES[shape]
    plant_carrier(world, tmp_path, "tool-name", carrier)
    control = run(world)
    assert_ok(control)
    leak = run(world, dest=tmp_path / "leak" / "archive", env={"TACHI_TEST_API_KEY": value})
    assert_failed(leak, mentions=("secret scan", "environment variable TACHI_TEST_API_KEY"))
    for needle in (value, value.strip(), carrier):
        assert needle not in leak.text, "a value reached the output"


M2_SCANNED_NAMES = ["PASSPHRASE", "PASSWD", "DB_PWD", "AUTH_HEADER", "SENTRY_DSN", "DATABASE_URL", "PRIVATE_NOTE",
                    "API_KEY", "AUTH_TOKEN", "CLIENT_SECRET", "DB_PASSWORD", "CLOUD_CREDENTIAL"]


@pytest.mark.parametrize("name", M2_SCANNED_NAMES)
def test_t034_m2_the_amended_name_list_is_read(world, run, tmp_path, name):
    variable = "TACHI_TEST_" + name
    plant_carrier(world, tmp_path, "tool-name", SECRET_PLAIN)
    assert_ok(run(world))
    leak = run(world, dest=tmp_path / "leak" / "archive", env={variable: SECRET_PLAIN})
    assert_failed(leak, mentions=("environment variable " + variable,))


@pytest.mark.parametrize("name", ["PWD", "OLDPWD", "SSH_AUTH_SOCK"])
def test_t034_m2_shell_state_and_a_socket_path_are_not_secrets_by_name(world, run, tmp_path, name):
    plant_carrier(world, tmp_path, "tool-name", SECRET_PLAIN)
    out = run(world, env={name: SECRET_PLAIN})
    assert_ok(out)
    cov = out.summary["secret_scan"]
    assert cov["environment_values_checked"] == 0 and cov["environment_values_skipped"] == 0


# -- M-3: the run says how much the scan checked -------------------------------------------------------------------------


def test_t034_m3_a_run_with_no_secret_named_variable_prints_the_coverage_line_and_the_warning(world, run):
    out = run(world)
    assert_ok(out)
    found = re.search(r"^\[391\] secret scan: 0 environment value\(s\) checked, (\d+) key-format rules$", out.err, re.M)
    assert found, out.err
    rules = int(found.group(1))
    assert rules >= 13
    assert "[391] warning: secret scan: no secret-named environment value was available, so only the %d key-format " \
        "rules ran; run the archiver under the same secret-injection wrapper as the session" % rules in out.err
    assert out.summary["secret_scan"] == {"environment_values_checked": 0, "environment_variables_checked": [],
                                          "environment_values_skipped": 0, "format_rules": rules}


def test_t034_m3_the_line_names_the_variables_checked_and_counts_the_ones_skipped(world, run):
    env = {"TACHI_TEST_API_KEY": "long-enough-value-1", "TACHI_TEST_AUTH_TOKEN": "another-long-value-2",
           "TACHI_TEST_SHORT_SECRET": "short", "TACHI_TEST_DATE_TOKEN": "2026-11-19"}
    out = run(world, env=env)
    assert_ok(out)
    rules = out.summary["secret_scan"]["format_rules"]
    assert ("[391] secret scan: 2 environment value(s) checked (TACHI_TEST_API_KEY, TACHI_TEST_AUTH_TOKEN), "
            "2 secret-named variable(s) skipped (under 8 characters, or date or version shaped), %d key-format rules"
            % rules) in out.err
    assert "no secret-named environment value was available" not in out.err
    assert out.summary["secret_scan"]["environment_variables_checked"] == ["TACHI_TEST_API_KEY", "TACHI_TEST_AUTH_TOKEN"]
    assert out.summary["secret_scan"]["environment_values_skipped"] == 2
    for value in env.values():
        if len(value) > 6:
            assert value not in out.text, "a value reached the output"


def test_t034_m3_the_coverage_is_reported_on_a_failure_after_the_scan_was_planned_and_not_before(world, run):
    world.edit_text(world.role_paths("spoofing")[0], lambda text: text + "{not json\n")
    late = run(world)
    assert_failed(late, mentions=("not valid JSON",))
    assert "secret scan: 0 environment value(s) checked" in late.err and "secret_scan" in late.summary
    early = run(world, dest=world.dest.parent / "second" / "archive", session="77777777-7777-4777-8777-777777777777")
    assert_failed(early, rc=2)
    assert "secret scan:" not in early.err and "secret_scan" not in early.summary


# -- M-4: a work tree with no .git entry ---------------------------------------------------------------------------------


def bare_layout(tmp_path, ignore=None):
    """A work tree with no .git entry and the bare repository that manages it (a dotfiles layout)."""
    work = tmp_path / "work"
    work.mkdir()
    if ignore is not None:
        (work / ".gitignore").write_text(ignore, encoding="utf-8")
    bare = tmp_path / "cfg.git"
    git("init", "--bare", "-q", bare)
    return work, bare


def test_t034_m4_the_operators_git_dir_and_work_tree_are_asked_and_a_destination_that_is_not_ignored_is_refused(world, run, tmp_path):
    work, bare = bare_layout(tmp_path)
    out = run(world, dest=work / "runs" / "x", env={"GIT_DIR": str(bare), "GIT_WORK_TREE": str(work)})
    assert_failed(out, mentions=("not ignored",))
    assert not (work / "runs").exists(), "a refused run created something in the operator's work tree"


def test_t034_m4_an_ignored_destination_in_the_operators_work_tree_is_accepted_and_nothing_is_committable(world, run, tmp_path):
    work, bare = bare_layout(tmp_path, ignore="runs/\n")
    out = run(world, dest=work / "runs" / "x", env={"GIT_DIR": str(bare), "GIT_WORK_TREE": str(work)})
    assert_ok(out)
    assert committable(work, git_dir=bare) == []


def test_t034_m4_a_destination_outside_the_operators_work_tree_is_not_asked_about(world, run, tmp_path):
    work, bare = bare_layout(tmp_path)
    out = run(world, dest=tmp_path / "elsewhere" / "x", env={"GIT_DIR": str(bare), "GIT_WORK_TREE": str(work)})
    assert_ok(out)


def test_t034_m4_a_git_dir_git_cannot_resolve_is_a_refusal_not_a_pass(world, run, tmp_path):
    work, _bare = bare_layout(tmp_path, ignore="runs/\n")
    out = run(world, dest=work / "runs" / "x", env={"GIT_DIR": str(tmp_path / "missing.git"), "GIT_WORK_TREE": str(work)})
    assert_failed(out, mentions=("GIT_DIR or GIT_WORK_TREE is set but git cannot name a work tree",))
    assert not (work / "runs").exists()


def test_t034_m4_the_operators_variables_do_not_leak_into_the_other_git_queries(world, run, tmp_path):
    """With GIT_DIR set the .git-entry check around the destination still sees the real work tree there."""
    work, bare = bare_layout(tmp_path)
    repo = init_repo(tmp_path / "repo")  # a normal work tree that does not ignore the destination
    out = run(world, dest=repo / "runs" / "x", env={"GIT_DIR": str(bare), "GIT_WORK_TREE": str(work)})
    assert_failed(out, mentions=("not ignored",))
    assert not (repo / "runs").exists()


# -- L-1: a no-op needs a finished archive whose manifest matches the source -----------------------------------------------


def _manifest_variants(manifest, session_id):
    """Replacement manifests an operator, a tool or an attacker could leave behind."""
    other_session = dict(manifest, session_id="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
    altered = json.loads(json.dumps(manifest))
    altered["transcripts"][0]["sha256"] = "0" * 64
    dropped = json.loads(json.dumps(manifest))
    dropped["transcripts"].pop()
    resized = json.loads(json.dumps(manifest))
    resized["transcripts"][0]["bytes"] += 1
    return {
        "empty-object": "{}",
        "empty-file": "",
        "not-json": "this is not json",
        "a-json-list": "[]",
        "foreign-session": json.dumps(other_session),
        "altered-hash": json.dumps(altered),
        "dropped-entry": json.dumps(dropped),
        "wrong-size": json.dumps(resized),
        "no-transcripts": json.dumps({"session_id": session_id}),
    }


L1_VARIANTS = ["empty-object", "empty-file", "not-json", "a-json-list", "foreign-session", "altered-hash",
               "dropped-entry", "wrong-size", "no-transcripts"]


@pytest.mark.parametrize("variant", L1_VARIANTS)
def test_t034_l1_a_no_op_into_a_destination_with_a_replaced_manifest_exits_1(world, run, variant):
    out = run(world)
    manifest = assert_ok(out)
    replacement = _manifest_variants(manifest, world.session_id)[variant]
    world.write_text(out.manifest_path, replacement)
    again = run(world)
    assert_failed(again, mentions=("does not match this session's files", "new --dest"), keep_manifest=True)
    assert out.manifest_path.read_text(encoding="utf-8") == replacement, "the archiver rewrote the manifest it refused"


def test_t034_l1_a_manifest_that_is_a_directory_or_a_link_is_not_a_finished_archive(world, run, tmp_path):
    out = run(world)
    assert_ok(out)
    out.manifest_path.unlink()
    out.manifest_path.symlink_to(tmp_path / "somewhere-else.json")
    assert_failed(run(world), mentions=("incomplete archive",), keep_manifest=True)


def test_t034_l1_extra_files_in_a_finished_archive_are_counted_in_a_warning_not_refused(world, run):
    out = run(world)
    assert_ok(out)
    (out.dest / "stray.txt").write_text("x", encoding="utf-8")
    (out.dest / "stray-dir").mkdir()
    again = run(world)
    assert again.rc == 0 and again.summary["status"] == "no-op"
    assert any("2 file(s) or directories that are not part of the archive" in w for w in again.summary["warnings"])


def test_t034_l1_the_archives_own_files_are_not_counted_as_extra(world, run):
    out = run(world)
    assert_ok(out)
    again = run(world)
    assert again.rc == 0 and not [w for w in again.summary["warnings"] if "not part of the archive" in w]


# -- L-2: a destination that is a symbolic link, and a path that changes under the run ------------------------------------


def test_t034_l2_a_destination_that_is_a_symlink_to_a_plain_directory_is_refused_and_left_untouched(world, run, tmp_path):
    """Before the fix the run wrote through the link and ``chmod`` tightened the directory it pointed at."""
    target = tmp_path / "target"
    target.mkdir()
    os.chmod(str(target), 0o755)
    link = tmp_path / "dest-link"
    link.symlink_to(target, target_is_directory=True)
    out = run(world, dest=link)
    assert_failed(out, mentions=("is a symbolic link",))
    assert mode_of(target) == 0o755, "chmod followed the destination link"
    assert list(target.iterdir()) == []


# -- L-3: --latest reads only plain session ids ------------------------------------------------------------------------------


@pytest.mark.parametrize("stem", ["bad name", "ctl\x07char", "-leading-hyphen", ".hidden", "x" * 129, "ünï"],
                         ids=["space", "control-character", "leading-hyphen", "leading-dot", "129-characters", "non-ascii"])
def test_t034_l3_latest_skips_a_transcript_whose_stem_is_not_a_plain_session_id(world, run, stem):
    bad = world.slug_dir / (stem + ".jsonl")
    world.write_bytes(bad, world.read_bytes(world.main_path))
    world.age_file(bad, seconds=900)  # newer than the fixture's one hour, so --latest would pick it first
    out = run(world, latest=True)
    manifest = assert_ok(out)
    assert manifest["session_id"] == world.session_id
    assert stem not in out.text


# -- L-4: the run summary is scanned too -------------------------------------------------------------------------------------


def _key_as_entry_type(world, key):
    world.write_jsonl(world.main_path, world.read_jsonl(world.main_path) + [{"type": key, "timestamp": STAMP}])
    return "unknown_entry_types"


def _key_as_assistant_key(world, key):
    lines = world.read_jsonl(world.main_path)
    [o for o in lines if o.get("type") == "assistant"][0][key] = 1
    world.write_jsonl(world.main_path, lines)
    return "unknown_assistant_keys"


def _key_as_denial_kind(world, key):
    append_tool_call(world, "main", "WebFetch", "toolu_tb_label_denied", {"url": "https://label.denied.example.test/"},
                     result="error", denial=key)
    return "unrecognised_denial_kinds"


@pytest.mark.parametrize("plant", [_key_as_entry_type, _key_as_assistant_key, _key_as_denial_kind],
                         ids=["entry-type", "assistant-key", "denial-kind"])
def test_t034_l4_a_key_shaped_label_is_shown_as_unparseable_in_the_summary(world, run, plant):
    """Before the fix the label went to stdout in the --json summary although the manifest excluded it."""
    key = google_key()
    section = plant(world, key)
    out = run(world)
    assert_ok(out)
    assert_key_absent(key, out.out, out.err)
    assert out.summary[section].get(UNPARSEABLE, 0) == 1


# -- L-5: the age of the newest change is reported --------------------------------------------------------------------------


def test_t034_l5_the_age_of_the_newest_change_is_in_the_summary_and_the_human_line(world, run, tmp_path):
    out = run(world)
    assert_ok(out)
    assert 3600 <= out.summary["newest_change_age_seconds"] < 3900  # the fixture's files are an hour old
    human = run(world, json_summary=False, dest=tmp_path / "human" / "archive")
    assert human.rc == 0
    assert re.search(r"\[391\] the newest file of the session had changed (\d+) s before this run", human.out)


def test_t034_l5_the_age_is_reported_even_when_the_live_rule_is_waived(world, run):
    os.utime(str(world.role_paths("spoofing")[1]), None)
    out = run(world, "--allow-live")
    assert_ok(out)
    assert out.summary["newest_change_age_seconds"] < 60


# -- L-6: a destination inside Claude Code's own directories -----------------------------------------------------------------


def test_t034_l6_a_destination_under_the_projects_directory_is_refused(world, run):
    """Claude Code's retention sweep can delete it, and --latest could later pick the archived copy up."""
    dest = world.config_dir / "projects" / "-fixture-project" / "archive-here"
    out = run(world, dest=dest)
    assert_failed(out, mentions=("Claude Code projects directory",))
    assert not dest.exists()


def test_t034_l6_a_destination_elsewhere_in_the_config_directory_is_accepted_with_a_warning(world, run):
    out = run(world, dest=world.config_dir / "archives" / "x")
    assert_ok(out)
    assert any("Claude Code configuration directory" in w for w in out.summary["warnings"])


# -- L-7: no false refusals for ordinary names, and a standalone key is still refused ------------------------------------------


def test_t034_l7_long_kebab_case_names_and_long_asia_hosts_do_not_refuse_a_clean_run(world, run, tmp_path):
    """``risk-``, ``task-`` and ``disk-`` end in the prefix ``sk-``; hosts like ``asiapacific...`` start like a key id."""
    out_dir = tmp_path / "named-output"
    out_dir.mkdir()
    names = ["%s-%s.md" % (prefix, "-".join(["assessment"] * 4)) for prefix in ("risk", "task", "disk")]
    for name in names:
        (out_dir / name).write_text("x", encoding="utf-8")
    hosts = ["asiapacificregionalgateway.example.test", "aidaexamplehostnamewithlongtail.example.test",
             "aroaexamplehostnamewithlongtail.example.test"]
    for index, host in enumerate(hosts):
        append_tool_call(world, "main", "Bash", "toolu_tb_asia_%d" % index, {"command": "curl https://%s/" % host})
    manifest = assert_ok(run(world, output_dir=out_dir))
    assert [a["path"] for a in manifest["artifacts"]] == sorted(names)
    assert {e["host"] for e in manifest["egress_observed"]} >= set(hosts)


@pytest.mark.parametrize("where", ["artifact-name", "host-label"])
def test_t034_l7_a_standalone_key_is_still_refused(world, run, tmp_path, where):
    out_dir = None
    if where == "artifact-name":
        out_dir = tmp_path / "key-output"
        out_dir.mkdir()
        (out_dir / google_key()).write_text("x", encoding="utf-8")
    else:
        aws = _join("AK", "IA") + _filler(16, _UPPER_DIGITS)
        append_tool_call(world, "main", "Bash", "toolu_tb_key_host", {"command": "curl https://%s.example.test/" % aws})
    out = run(world, output_dir=out_dir)
    assert_failed(out, mentions=("secret scan",))


# -- L-8: what the documentation says the manifest is -------------------------------------------------------------------------


def test_t034_l8_the_docstring_does_not_call_the_manifest_non_sensitive(archiver):
    doc = " ".join(archiver.__doc__.split())
    assert "The manifest holds no secrets and no message text" in doc
    assert "It still names hosts, file names and session ids, so read it before you share it" in doc
    assert "The manifest is not" not in doc
