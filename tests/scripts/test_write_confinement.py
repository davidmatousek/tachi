"""Write confinement of the report build path (feature 391, T015; SC-005, AR-1).

A report run must write only under the output directory ``{out}`` and the
per-user temporary directory, and must leave the installed
``templates/tachi/`` tree and the target directory byte-unchanged, custom
``report-config.typ`` included. This module runs the three commands the
report-assembler agent issues (extract with ``--build-dir``, ``typst compile``,
extract with ``--remove-build-dir``) in a throwaway adopter project under
``tmp_path`` and proves it with whole-tree before/after snapshots: any new,
changed or removed path outside ``{out}`` and ``$TMPDIR`` fails a test.

What each group proves:

- core case (== AR-1 case 1): target and output are separate directories, a
  custom ``report-config.typ`` sits in the target, the fixture has no attack
  trees (no ``mmdc``); extract, compile, remove. Typst-gated.
- ``--remove-build-dir`` removes only the build directory and refuses every
  path that is not one; ``--build-dir`` refuses a path outside the project.
- AR-1 case 2: a mislabeled infographic (a ``.jpg`` holding PNG bytes) yields
  its corrected copy under ``{out}``; ``--cleanup-mislabeled-images`` deletes
  only inside ``{out}``, and nothing in the target. Typst-gated for the compile.
- AR-1 case 3: an attack tree and an attack chain are rendered through a stub
  ``mmdc`` (no Chromium); the PNGs land under ``{out}/attack-trees/`` and
  ``{out}/attack-chains/``. No CI workflow installs ``mmdc``, so this stub is
  the only CI evidence for W17 and W18. Typst-gated for the compile.
- X-1 (AD-9): ``TACHI_MMDC_PUPPETEER_CONFIG``, at each of the two mmdc call sites
  (attack trees, attack chains), through the real extractor and the same stub,
  which records what it was called with. Unset, mmdc gets no ``-p``; an absolute
  path to a regular file reaches it as ``-p <path>``; an empty, relative, missing
  or directory value stops the run with an error that names the variable, before
  mmdc starts and before anything is written. Needs no Typst.
- legacy mode (``--output``) still writes next to the artifacts, as before.
- AR-14: a stock ``python3 scripts/<entry> --help`` of each of the three
  installed scripts that import ``tachi_parsers`` leaves no bytecode cache, in
  the project or under a test-owned ``PYTHONPYCACHEPREFIX``.
- AR-1 case 4 and the T015 static assertion: no fenced block in the five
  recipe documents names ``templates/tachi/`` as a write target or uses ``/tmp``.

Typst gating: tests that compile are skipped when ``typst`` is not on PATH,
UNLESS ``TACHI_REQUIRE_TYPST=1`` is set (the ``report-posture`` CI job), in
which case a missing Typst FAILS rather than skips. The rest needs no Typst.

Interpreter note: every child runs the stock invocation, as a recipe or a person
runs it: no ``-B``, and ``PYTHONDONTWRITEBYTECODE`` is removed from the child's
environment so that a developer's shell setting cannot mask a regression. The
installed scripts turn bytecode writing off themselves when run as a script
(AR-14), so CPython caches no ``tachi_parsers`` and the snapshots stay exact.
The AR-14 cases also set a ``PYTHONPYCACHEPREFIX``, because an interpreter such
as macOS's ``/usr/bin/python3`` keeps its cache outside the project.

Layout under ``tmp_path`` (``harness/`` is excluded from every snapshot)::

    harness/   stub mmdc, its canned PNG and one file per call it received
    systmp/    $TMPDIR of every child process
    project/   working directory and Typst root
      scripts/ schemas/ templates/tachi/security-report/   installed copies
      run/     --target-dir
      out/     the output directory {out}

Stdlib and pytest only; Python 3.9 syntax.
"""

import hashlib
import os
import re
import shlex
import shutil
import struct
import subprocess
import sys
import zlib
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set, Tuple

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
SCHEMAS_DIR = REPO_ROOT / "schemas"
TEMPLATE_DIR = REPO_ROOT / "templates" / "tachi" / "security-report"
# Tier 1, three findings, no attack trees or chains, no images: the
# extractor never shells out to mmdc on it (also used by the posture contract).
FIXTURE_DIR = (
    REPO_ROOT / "tests" / "scripts" / "fixtures" / "fidelity_373" / "posture_mmdc_free"
)
# The pair the report-assembler's own preflight requires: the installed set.
INSTALLED_SCRIPTS = ("extract-report-data.py", "tachi_parsers.py")

CUSTOM_FOOTER = "T015 custom footer"
SUBPROCESS_TIMEOUT = 300
# The environment variable that forwards a puppeteer config file to mmdc (AD-9).
PUPPETEER_ENV = "TACHI_MMDC_PUPPETEER_CONFIG"

Snapshot = Dict[str, Tuple[str, str]]


# =============================================================================
# Typst gate (same contract as tests/scripts/test_report_posture_contract.py)
# =============================================================================


def _require_typst() -> None:
    """Skip, unless TACHI_REQUIRE_TYPST=1 demands a hard failure instead.

    The report-posture CI job sets TACHI_REQUIRE_TYPST=1 so a broken Typst
    provisioning step cannot silently turn this gate into a no-op.
    """
    if shutil.which("typst"):
        return
    if os.environ.get("TACHI_REQUIRE_TYPST") == "1":
        pytest.fail(
            "TACHI_REQUIRE_TYPST=1 but `typst` is not on PATH. The "
            "report-posture CI job must fail loudly, not skip, when its "
            "own Typst provisioning step is broken."
        )
    pytest.skip("typst CLI not available in test environment")


# =============================================================================
# Helpers: images, snapshots
# =============================================================================


def _png_bytes(rgb: Tuple[int, int, int] = (200, 30, 30), size: int = 8) -> bytes:
    """A small valid PNG: what the stub mmdc renders, and a stand-in infographic."""
    row = b"\x00" + bytes(rgb) * size

    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(row * size))
        + chunk(b"IEND", b"")
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot(root: Path, skip: Tuple[str, ...] = ()) -> Snapshot:
    """Every path under ``root`` as ``relative posix path -> (kind, digest)``.

    Directories are recorded too, so an empty ``mkdir`` outside ``{out}`` is
    seen. ``skip`` names top-level directories (relative to ``root``) that are
    pruned.
    """
    snap = {}  # type: Snapshot
    for dirpath, dirnames, filenames in os.walk(str(root)):
        here = Path(dirpath)
        dirnames[:] = sorted(
            d for d in dirnames if (here / d).relative_to(root).as_posix() not in skip
        )
        for name in dirnames + sorted(filenames):
            path = here / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                snap[rel] = ("link", os.readlink(str(path)))
            elif path.is_dir():
                snap[rel] = ("dir", "")
            else:
                snap[rel] = ("file", _sha256(path))
    return snap


def _diff(before: Snapshot, after: Snapshot) -> Tuple[Set[str], Set[str], Set[str]]:
    """``(added, changed, removed)`` path sets between two snapshots."""
    added = set(after) - set(before)
    removed = set(before) - set(after)
    changed = {p for p in set(before) & set(after) if before[p] != after[p]}
    return added, changed, removed


def _within(rel: str, base: str) -> bool:
    return rel == base or rel.startswith(base + "/")


def _under(snap: Snapshot, prefix: str) -> Snapshot:
    return {p: v for p, v in snap.items() if _within(p, prefix)}


def _tail(text: str, limit: int = 2500) -> str:
    return text if len(text) <= limit else "..." + text[-limit:]


def _describe(proc: "subprocess.CompletedProcess") -> str:
    return "exit %s\nstdout:\n%s\nstderr:\n%s" % (
        proc.returncode,
        _tail(proc.stdout),
        _tail(proc.stderr),
    )


def _pdf_text(pdf: Path) -> Optional[str]:
    """Text of the PDF's first pages, or None when ``pdftotext`` is unavailable."""
    if not shutil.which("pdftotext"):
        return None
    proc = subprocess.run(
        ["pdftotext", "-f", "1", "-l", "12", str(pdf), "-"],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    return proc.stdout if proc.returncode == 0 else None


# =============================================================================
# The adopter project
# =============================================================================


MMDC_STUB = """#!/bin/sh
# Stub mmdc (T015): write the canned PNG to the path after -o. No Chromium.
# X-1: first record the arguments, one per line, in a file of their own, so a
# test can read back what the extractor passed (the optional -p <config>).
printf '%s\\n' "$@" > {calls}/$$
out=
while [ "$#" -gt 0 ]; do
  if [ "$1" = "-o" ]; then out=$2; fi
  shift
done
[ -n "$out" ] || exit 64
cp {png} "$out"
"""

ATTACK_TREE_MD = """# Attack Tree: T-1 — Synthetic threat T-1

| Field | Value |
|-------|-------|
| Finding ID | T-1 |
| Component | API Gateway |
| Risk Level | High |
| Threat | Synthetic threat T-1 |

```mermaid
flowchart TD
    T1_root["Exhaust the API Gateway"]
    T1_leaf["Send an unbounded request flood"]
    T1_root --> T1_leaf
```
"""

ATTACK_CHAINS_MD = """---
schema_version: "1.0"
date: "2026-01-14"
chain_count: 1
surfaced_count: 1
---

# Cross-Layer Attack Chains: Synthetic Fixture

## Section 2: Chain Details

### CHAIN-001: Synthetic gateway flood to worker log leak

**Layers**: L3 → L4
**Max Severity**: High
**Surfaced**: Yes

#### Member Findings

| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |
|------------|---------------|------|-----------|----------|----------|
| T-1 | L3 — Agent Framework | initial_exploit | API Gateway | Denial of Service | High |
| T-3 | L4 — Deployment Infrastructure | terminal_impact | Batch Worker | Information Disclosure | Low |

#### Attack Progression

A synthetic progression paragraph for the fixture.

#### Chain-Breaking Controls

**Target**: T-1 (L3 — Agent Framework)
**Rationale**: Synthetic rationale.
**Recommendation**: Synthetic recommendation.
"""

# Where the rich fixture's rendered diagrams must land, relative to {out}.
TREE_PNG = "attack-trees/t-1-attack-tree.png"
CHAIN_PNG = "attack-chains/chain-001-attack-chain.png"


class Project:
    """An adopter project as ``scripts/install.sh`` leaves one, under ``tmp_path``.

    ``target`` and ``out`` are directory names below the working directory;
    pass the same name for both to model ``{out} == {target_dir}`` (the
    command's default). ``create_out=False`` leaves ``out/`` for the extractor
    to create.
    """

    def __init__(self, root: Path, target: str = "run", out: str = "out", create_out: bool = True):
        self.root = root
        self.cwd = root / "project"
        self.harness = root / "harness"
        self.systmp = root / "systmp"
        self.target = self.cwd / target
        self.out = self.cwd / out
        self.build = self.out / ".tachi-build" / "security-report"
        self.templates = self.cwd / "templates" / "tachi" / "security-report"
        self.pdf = self.out / "security-report.pdf"
        self.canned_png = self.harness / "canned.png"
        self.bin = self.harness / "bin"
        self.calls_dir = self.harness / "mmdc-calls"

        for directory in (self.cwd, self.harness, self.systmp, self.bin, self.calls_dir, self.target):
            directory.mkdir(parents=True, exist_ok=True)
        if create_out:
            self.out.mkdir(parents=True, exist_ok=True)

        # The installed copies the report-assembler recipe relies on.
        (self.cwd / "scripts").mkdir()
        for name in INSTALLED_SCRIPTS:
            shutil.copy2(str(SCRIPTS_DIR / name), str(self.cwd / "scripts" / name))
        shutil.copytree(str(SCHEMAS_DIR), str(self.cwd / "schemas"))
        shutil.copytree(
            str(TEMPLATE_DIR),
            str(self.templates),
            ignore=shutil.ignore_patterns("report-data.typ", ".DS_Store"),
        )

        # Stub mmdc, used only by runs that ask for it.
        self.canned_png.write_bytes(_png_bytes())
        stub = self.bin / "mmdc"
        stub.write_text(
            MMDC_STUB.format(
                png=shlex.quote(str(self.canned_png)), calls=shlex.quote(str(self.calls_dir))
            ),
            encoding="utf-8",
        )
        stub.chmod(0o755)

    # -- fixtures -----------------------------------------------------------

    def add_artifacts(self, trees_and_chains: bool = False) -> None:
        """Copy the mmdc-free fixture into the target; optionally add one tree and one chain."""
        for source in sorted(FIXTURE_DIR.glob("*.md")):
            shutil.copy2(str(source), str(self.target / source.name))
        if trees_and_chains:
            self.add_attack_tree()
            self.add_attack_chain()

    def add_attack_tree(self) -> None:
        """One High-severity attack tree (T-1): the extractor renders it through mmdc."""
        (self.target / "attack-trees").mkdir()
        (self.target / "attack-trees" / "t-1-attack-tree.md").write_text(
            ATTACK_TREE_MD, encoding="utf-8"
        )

    def add_attack_chain(self) -> None:
        """One surfaced attack chain (CHAIN-001): the extractor renders it through mmdc."""
        (self.target / "attack-chains.md").write_text(ATTACK_CHAINS_MD, encoding="utf-8")

    def add_custom_config(self) -> bytes:
        """Write a custom report-config.typ into the target (the shipped default plus a footer)."""
        default = (self.templates / "report-config.typ").read_text(encoding="utf-8")
        marker = "#let custom-footer-text = none"
        assert marker in default, "report-config.typ no longer declares custom-footer-text; update T015"
        custom = default.replace(marker, '#let custom-footer-text = "%s"' % CUSTOM_FOOTER)
        (self.target / "report-config.typ").write_text(custom, encoding="utf-8")
        return custom.encode("utf-8")

    def add_image(self, name: str, data: bytes) -> None:
        (self.target / name).write_bytes(data)

    # -- commands (the three the report-assembler agent issues) ---------------

    def rel(self, path: Path) -> str:
        return os.path.relpath(str(path), str(self.cwd))

    def _run(
        self, argv: List[str], stub_mmdc: bool = False, puppeteer_config: Optional[str] = None
    ) -> "subprocess.CompletedProcess":
        env = dict(os.environ)
        env.update(
            {
                "TMPDIR": str(self.systmp),
                "SOURCE_DATE_EPOCH": "1700000000",
            }
        )
        env.pop("PYTHONDONTWRITEBYTECODE", None)  # stock run: a developer's setting must not mask a regression (AR-14)
        env.pop(PUPPETEER_ENV, None)  # a developer's sandbox config must not leak in
        if puppeteer_config is not None:
            env[PUPPETEER_ENV] = puppeteer_config  # "" is a value too: set but empty (X-1)
        if stub_mmdc:
            env["PATH"] = str(self.bin) + os.pathsep + env.get("PATH", "")
        return subprocess.run(
            argv,
            cwd=str(self.cwd),
            env=env,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=SUBPROCESS_TIMEOUT,
        )

    def extract(
        self,
        *extra: str,
        stub_mmdc: bool = False,
        build: Optional[str] = None,
        puppeteer_config: Optional[str] = None,
    ) -> "subprocess.CompletedProcess":
        """``python3 scripts/extract-report-data.py --target-dir T --build-dir B``.

        ``puppeteer_config`` is the value of ``TACHI_MMDC_PUPPETEER_CONFIG`` for
        this run; None leaves the variable unset.
        """
        argv = [
            sys.executable, "scripts/extract-report-data.py",
            "--target-dir", self.rel(self.target),
            "--build-dir", build if build is not None else self.rel(self.build),
        ] + list(extra)
        return self._run(argv, stub_mmdc=stub_mmdc, puppeteer_config=puppeteer_config)

    def extract_legacy(self, output: Path, *extra: str) -> "subprocess.CompletedProcess":
        """The pre-391 form: ``--output FILE --template-dir DIR``."""
        argv = [
            sys.executable, "scripts/extract-report-data.py",
            "--target-dir", self.rel(self.target),
            "--output", self.rel(output),
            "--template-dir", self.rel(self.templates),
        ] + list(extra)
        return self._run(argv, stub_mmdc=True)

    def compile(self) -> "subprocess.CompletedProcess":
        """``typst compile {build}/main.typ {out}/security-report.pdf --root .``."""
        argv = [
            "typst", "compile",
            self.rel(self.build / "main.typ"),
            self.rel(self.pdf),
            "--root", ".",
        ]
        return self._run(argv)

    def remove(self, path: Optional[str] = None) -> "subprocess.CompletedProcess":
        """``python3 scripts/extract-report-data.py --remove-build-dir PATH``."""
        argv = [
            sys.executable, "scripts/extract-report-data.py",
            "--remove-build-dir", path if path is not None else self.rel(self.build),
        ]
        return self._run(argv)

    # -- observation ------------------------------------------------------------

    def mmdc_calls(self) -> List[List[str]]:
        """The arguments of every run of the stub mmdc so far, in no set order.

        Empty when mmdc never started: a run that stops before a render leaves
        the directory empty.
        """
        return [
            path.read_text(encoding="utf-8").splitlines() for path in sorted(self.calls_dir.iterdir())
        ]

    def snapshot(self) -> Snapshot:
        return _snapshot(self.root, skip=("harness",))

    def key(self, path: Path) -> str:
        """Snapshot key of ``path``."""
        return path.relative_to(self.root).as_posix()

    def assert_confined(
        self, before: Snapshot, after: Snapshot, stage: str, allowed: Tuple[Path, ...] = ()
    ) -> Tuple[Set[str], Set[str], Set[str]]:
        """Fail on any new, changed or removed path outside ``{out}`` and ``$TMPDIR``.

        ``allowed`` replaces ``{out}`` as the writable area for the one case
        where the output directory is the target itself.
        """
        zones = [self.key(p) for p in (allowed or (self.out,))] + [self.key(self.systmp)]
        added, changed, removed = _diff(before, after)
        strays = sorted(p for p in added | changed | removed if not any(_within(p, z) for z in zones))
        assert not strays, "%s: wrote outside %s: %s" % (stage, zones, strays)
        return added, changed, removed

    def assert_untouched(self, before: Snapshot, after: Snapshot, path: Path, what: str) -> None:
        """Fail unless every path under ``path`` is byte-identical in both snapshots."""
        prefix = self.key(path)
        old, new = _under(before, prefix), _under(after, prefix)
        assert old == new, "%s changed: %s" % (
            what,
            sorted(p for p in set(old) | set(new) if old.get(p) != new.get(p)),
        )


@pytest.fixture
def project(tmp_path: Path) -> Project:
    """A project whose target holds the mmdc-free fixture; ``out/`` exists and is empty."""
    p = Project(tmp_path)
    p.add_artifacts()
    return p


# =============================================================================
# Core case (T015; also AR-1 case 1): extract, compile, remove
# =============================================================================


def test_core_case_extract_compile_remove_confine_every_write(project: Project):
    """Output directory without ``.tachi-build/``, a custom config in the target,
    a fixture without attack trees: nothing outside ``{out}`` and ``$TMPDIR``
    is written, the installed templates and the target stay byte-unchanged, and
    ``--remove-build-dir`` removes only the build directory."""
    _require_typst()
    custom_config = project.add_custom_config()
    default_config = (project.templates / "report-config.typ").read_bytes()
    assert custom_config != default_config
    assert not (project.out / ".tachi-build").exists()
    before = project.snapshot()

    # 1. extract --------------------------------------------------------------
    extract = project.extract()
    assert extract.returncode == 0, _describe(extract)
    assert "Using custom report-config.typ from" in extract.stderr, _describe(extract)
    assert not (project.out / "attack-trees").exists(), "the fixture must not need mmdc"
    assert (project.build / "report-config.typ").read_bytes() == custom_config
    assert (project.build / "report-data.typ").is_file()
    after_extract = project.snapshot()
    added, _, _ = project.assert_confined(before, after_extract, "after extraction")
    assert project.key(project.build / "report-data.typ") in added, "the snapshot must see the new build dir"

    # 2. compile ----------------------------------------------------------------
    compiled = project.compile()
    assert compiled.returncode == 0, _describe(compiled)
    assert project.pdf.is_file() and project.pdf.stat().st_size > 0
    after_compile = project.snapshot()
    added, _, _ = project.assert_confined(before, after_compile, "after compile")
    assert project.key(project.pdf) in added
    text = _pdf_text(project.pdf)
    if text is not None:
        assert CUSTOM_FOOTER in text, "the custom report-config.typ did not reach the compiled PDF"

    # 3. remove ---------------------------------------------------------------------
    removed_run = project.remove()
    assert removed_run.returncode == 0, _describe(removed_run)
    final = project.snapshot()
    project.assert_confined(before, final, "after --remove-build-dir")
    assert not project.build.exists()
    assert (project.out / ".tachi-build").is_dir(), "only the build directory goes, not .tachi-build/"
    assert project.pdf.is_file()
    added, changed, removed = _diff(after_compile, final)
    build_key = project.key(project.build)
    assert not added and not changed, (added, changed)
    assert removed == set(_under(after_compile, build_key)), "removal must take the build dir and nothing else"

    # The installed templates and the target are byte-unchanged end to end.
    project.assert_untouched(before, final, project.templates, "the installed templates")
    project.assert_untouched(before, final, project.target, "the target directory")
    assert (project.templates / "report-config.typ").read_bytes() == default_config
    assert not (project.templates / "report-data.typ").exists()


# =============================================================================
# --remove-build-dir and --build-dir: scope and refusals
# =============================================================================


def test_remove_build_dir_removes_only_the_build_dir(project: Project):
    """Siblings of the build directory survive, whatever they are."""
    assert project.extract().returncode == 0
    (project.out / "keep.txt").write_text("out", encoding="utf-8")
    (project.out / ".tachi-build" / "keep.txt").write_text("hidden", encoding="utf-8")
    (project.out / "attack-trees").mkdir()
    (project.out / "attack-trees" / "x.png").write_bytes(_png_bytes())
    project.pdf.write_bytes(b"%PDF-stub")
    before = project.snapshot()

    proc = project.remove()
    assert proc.returncode == 0, _describe(proc)
    after = project.snapshot()
    added, changed, removed = _diff(before, after)
    assert not added and not changed, (added, changed)
    assert removed == set(_under(before, project.key(project.build)))
    assert removed, "the build directory held files, so the snapshot must see them go"
    for survivor in ("keep.txt", ".tachi-build/keep.txt", "attack-trees/x.png", "security-report.pdf"):
        assert (project.out / survivor).is_file(), survivor
    project.assert_untouched(before, after, project.templates, "the installed templates")
    project.assert_untouched(before, after, project.target, "the target directory")


REMOVE_REFUSALS = (
    "wrong-suffix",
    "output-directory-itself",
    "working-directory",
    "parent-of-working-directory",
    "dotdot-back-out",
    "installed-templates",
    "outside-working-directory",
    "symlinked-build-dir",
    "symlinked-parent",
)


def _real_build_dir(root: Path, name: str) -> Path:
    """A correctly shaped build directory holding a sentinel, under ``root/name``."""
    real = root / name / ".tachi-build" / "security-report"
    real.mkdir(parents=True)
    (real / "sentinel.txt").write_text("must survive", encoding="utf-8")
    return real


def _refusal_argument(p: Project, case: str) -> str:
    """Prepare ``case`` and return the ``--remove-build-dir`` argument that exercises it.

    The two symlink cases point at a build directory of the right shape that
    lies inside the project, so only the no-symlink rule can refuse them.
    """
    _real_build_dir(p.root, "elsewhere")  # outside the working directory, for the outside case
    if case == "symlinked-build-dir":
        _real_build_dir(p.cwd, "other")
        shutil.rmtree(str(p.build))
        os.symlink(os.path.join("..", "..", "other", ".tachi-build", "security-report"), str(p.build))
    elif case == "symlinked-parent":
        _real_build_dir(p.cwd, "real_out")
        os.symlink("real_out", str(p.cwd / "link_out"))
    return {
        "wrong-suffix": "out/.tachi-build",
        "output-directory-itself": "out",
        "working-directory": ".",
        "parent-of-working-directory": "..",
        "dotdot-back-out": "out/.tachi-build/security-report/../..",
        "installed-templates": "templates/tachi/security-report",
        "outside-working-directory": str(p.root / "elsewhere" / ".tachi-build" / "security-report"),
        "symlinked-build-dir": p.rel(p.build),
        "symlinked-parent": "link_out/.tachi-build/security-report",
    }[case]


@pytest.mark.parametrize("case", REMOVE_REFUSALS)
def test_remove_build_dir_refuses_everything_that_is_not_a_build_dir(project: Project, case: str):
    """Exit 2 and a byte-identical tree (the whole of ``tmp_path``) for each bad path."""
    assert project.extract().returncode == 0
    (project.out / "keep.txt").write_text("out", encoding="utf-8")
    argument = _refusal_argument(project, case)
    before = project.snapshot()

    proc = project.remove(argument)
    assert proc.returncode == 2, _describe(proc)
    assert "--remove-build-dir" in proc.stderr, _describe(proc)
    assert project.snapshot() == before, "a refused removal must not touch anything"


@pytest.mark.parametrize("case", ("outside-working-directory", "wrong-suffix"))
def test_build_dir_outside_the_project_or_of_the_wrong_shape_is_refused_untouched(
    project: Project, case: str
):
    """``--build-dir`` fails before extraction and writes nothing."""
    bad = {
        "outside-working-directory": str(project.root / "elsewhere" / ".tachi-build" / "security-report"),
        "wrong-suffix": "out/build",
    }[case]
    before = project.snapshot()
    proc = project.extract(build=bad)
    assert proc.returncode == 2, _describe(proc)
    assert "--build-dir" in proc.stderr, _describe(proc)
    assert project.snapshot() == before


# =============================================================================
# AR-1 case 2: a mislabeled infographic and the opt-in cleanup
# =============================================================================


def _add_infographics(p: Project) -> bytes:
    """A mislabeled baseball card (PNG bytes in a .jpg) and a correctly labelled funnel (.png)."""
    mislabeled = _png_bytes((10, 120, 200))
    p.add_image("threat-baseball-card.jpg", mislabeled)
    p.add_image("threat-risk-funnel.png", _png_bytes((10, 200, 60)))
    return mislabeled


def _data_value(build: Path, name: str) -> str:
    """The string a ``#let NAME = "..."`` line of report-data.typ binds."""
    data = (build / "report-data.typ").read_text(encoding="utf-8")
    match = re.search(r'^#let %s = "([^"]*)"' % re.escape(name), data, re.M)
    assert match, "report-data.typ binds no %s" % name
    return match.group(1)


def test_mislabeled_infographic_is_corrected_under_out_and_the_report_compiles(project: Project):
    """AR-1 case 2: the corrected copy appears in ``{out}``, the target is untouched,
    a correctly labelled infographic is still read from the target, the PDF compiles."""
    _require_typst()
    mislabeled = _add_infographics(project)
    before = project.snapshot()

    extract = project.extract()
    assert extract.returncode == 0, _describe(extract)
    corrected = project.out / "threat-baseball-card.png"
    assert corrected.is_file(), "the corrected copy must land in {out}: %s" % _describe(extract)
    assert corrected.read_bytes() == mislabeled
    assert "writing corrected sibling threat-baseball-card.png in " in extract.stderr, _describe(extract)
    assert _data_value(project.build, "baseball-image-path") == "../../threat-baseball-card.png"
    # a correctly labelled infographic is still read from the target
    assert _data_value(project.build, "funnel-image-path") == "../../../run/threat-risk-funnel.png"

    compiled = project.compile()
    assert compiled.returncode == 0, _describe(compiled)
    after = project.snapshot()
    project.assert_confined(before, after, "after extraction and compile")
    project.assert_untouched(before, after, project.target, "the target directory")
    assert not (project.target / "threat-baseball-card.png").exists()


def test_cleanup_flag_deletes_nothing_when_out_is_not_the_target(project: Project):
    """Moment A (a mislabeled file beside its byte-identical counterpart) and
    Moment B (a mislabeled file alone) both leave the target as it was."""
    mislabeled = _png_bytes((10, 120, 200))
    project.add_image("threat-baseball-card.jpg", mislabeled)  # Moment A: a pair
    project.add_image("threat-baseball-card.png", mislabeled)
    project.add_image("threat-system-architecture.jpg", _png_bytes((90, 90, 200)))  # Moment B: alone
    before = project.snapshot()

    proc = project.extract("--cleanup-mislabeled-images")
    assert proc.returncode == 0, _describe(proc)
    after = project.snapshot()
    project.assert_confined(before, after, "with --cleanup-mislabeled-images")
    project.assert_untouched(before, after, project.target, "the target directory")
    assert "Cleanup: deleted" not in proc.stderr, _describe(proc)
    for skipped in ("threat-baseball-card.jpg", "threat-system-architecture.jpg"):
        assert re.search(r"Cleanup skipped for .*%s: it lies outside" % re.escape(skipped), proc.stderr), (
            skipped,
            _describe(proc),
        )
    # Moment B still gets its corrected copy, under {out}
    assert (project.out / "threat-system-architecture.png").is_file()


def test_cleanup_flag_deletes_only_inside_out_when_out_is_the_target(tmp_path: Path):
    """``{out} == {target_dir}`` (the command's default) keeps the pre-391 behaviour."""
    p = Project(tmp_path, target="run", out="run")
    p.add_artifacts()
    mislabeled = _png_bytes((10, 120, 200))
    p.add_image("threat-baseball-card.jpg", mislabeled)  # Moment A
    p.add_image("threat-baseball-card.png", mislabeled)
    p.add_image("threat-system-architecture.jpg", _png_bytes((90, 90, 200)))  # Moment B
    before = p.snapshot()

    proc = p.extract("--cleanup-mislabeled-images")
    assert proc.returncode == 0, _describe(proc)
    after = p.snapshot()
    _, _, removed = p.assert_confined(before, after, "{out} == target", allowed=(p.target,))
    assert removed == {
        p.key(p.target / "threat-baseball-card.jpg"),
        p.key(p.target / "threat-system-architecture.jpg"),
    }, removed
    assert (p.target / "threat-baseball-card.png").read_bytes() == mislabeled
    assert (p.target / "threat-system-architecture.png").is_file()
    assert proc.stderr.count("Cleanup: deleted mislabeled duplicate") == 2, _describe(proc)
    assert "Cleanup skipped" not in proc.stderr


# =============================================================================
# AR-1 case 3: attack-tree and attack-chain PNGs through a stub mmdc
# =============================================================================


def _rich_project(tmp_path: Path) -> Project:
    """Target with one attack tree, one surfaced chain and a mislabeled infographic;
    ``out/`` does not exist yet (the extractor must create it)."""
    p = Project(tmp_path, create_out=False)
    p.add_artifacts(trees_and_chains=True)
    _add_infographics(p)
    return p


def test_attack_tree_and_chain_pngs_land_under_out_not_under_the_target(tmp_path: Path):
    """AR-1 case 3 (extraction only): one tree and one chain through the stub mmdc."""
    p = _rich_project(tmp_path)
    before = p.snapshot()

    proc = p.extract(stub_mmdc=True)
    assert proc.returncode == 0, _describe(proc)
    assert "Attack trees: 1 Critical/High entries extracted" in proc.stderr, _describe(proc)
    assert "Attack chains: 1 surfaced chain(s) extracted" in proc.stderr, _describe(proc)
    canned = p.canned_png.read_bytes()
    for image in (TREE_PNG, CHAIN_PNG):
        assert (p.out / image).is_file(), "%s must be rendered under {out}: %s" % (image, _describe(proc))
        assert (p.out / image).read_bytes() == canned, "%s must be the stub's PNG, not a real mmdc's" % image

    after = p.snapshot()
    added, _, _ = p.assert_confined(before, after, "after rendering through the stub mmdc")
    p.assert_untouched(before, after, p.target, "the target directory")
    assert {p.key(p.out / TREE_PNG), p.key(p.out / CHAIN_PNG)} <= added

    # every image path the data file emits resolves from the build directory
    data = (p.build / "report-data.typ").read_text(encoding="utf-8")
    emitted = re.findall(r'image-path: "([^"]+)"', data)
    assert sorted(os.path.normpath(e) for e in emitted) == sorted(
        [os.path.normpath("../../" + TREE_PNG), os.path.normpath("../../" + CHAIN_PNG)]
    ), emitted
    for rel in emitted:
        assert (p.build / rel).resolve().is_file(), rel


def test_attack_images_rendered_under_out_compile_and_the_run_stays_confined(tmp_path: Path):
    """AR-1 case 3 end to end: the ``../../attack-*`` paths resolve under Typst's ``--root .``."""
    _require_typst()
    p = _rich_project(tmp_path)
    before = p.snapshot()

    assert p.extract(stub_mmdc=True).returncode == 0
    compiled = p.compile()
    assert compiled.returncode == 0, _describe(compiled)
    removed = p.remove()
    assert removed.returncode == 0, _describe(removed)
    after = p.snapshot()
    p.assert_confined(before, after, "extract, compile and remove with attack images")
    p.assert_untouched(before, after, p.target, "the target directory")
    p.assert_untouched(before, after, p.templates, "the installed templates")
    assert p.pdf.is_file() and not p.build.exists()
    assert (p.out / TREE_PNG).is_file() and (p.out / CHAIN_PNG).is_file()


# =============================================================================
# X-1 (AD-9): TACHI_MMDC_PUPPETEER_CONFIG reaches both mmdc call sites, or stops the run
# =============================================================================

# The two production code paths that spawn mmdc. Each is reached through the real
# extractor CLI by a project that needs only that one, and a recorded call is told
# apart by the output name the extractor hands mmdc:
#   trees   render_mermaid_to_png  -> _render_single        (one attack tree)
#   chains  _render_chain_diagrams -> _render_chain_single  (one surfaced chain)
SITES = ("trees", "chains")
SITE_OUTPUT = {"trees": "t-1.png", "chains": "chain-001.png"}

# The four values AD-9 refuses. A traceback echoes the source line of the call
# site, and that line names the variable in a comment, so the error is looked for
# on an unindented line (the exception message), not anywhere in stderr.
BAD_PUPPETEER_VALUES = ("empty", "relative", "missing", "directory")
NAMES_PUPPETEER_ENV = re.compile(r"^\S.*\b%s\b" % re.escape(PUPPETEER_ENV), re.M)


def _site_project(tmp_path: Path, site: str) -> Project:
    """A project whose run renders through ``site`` and through no other mmdc call site;
    ``out/`` does not exist yet (the extractor must create it)."""
    p = Project(tmp_path, create_out=False)
    p.add_artifacts()
    if site == "trees":
        p.add_attack_tree()
    else:
        p.add_attack_chain()
    return p


def _the_one_call(p: Project, site: str) -> List[str]:
    """The stub mmdc's only call, checked to have come from ``site``."""
    calls = p.mmdc_calls()
    assert len(calls) == 1, "expected one mmdc call, from the %s site: %s" % (site, calls)
    argv = calls[0]
    assert "-o" in argv, argv
    output = os.path.basename(argv[argv.index("-o") + 1])
    assert output == SITE_OUTPUT[site], "the call did not come from the %s site: %s" % (site, argv)
    return argv


def _bad_puppeteer_value(p: Project, case: str) -> str:
    """Prepare ``case`` and return the value to put in the variable.

    The relative value names a real regular file that resolves from the working
    directory, so only the absolute-path rule can refuse it. The other three are
    absolute: nothing at the path, a directory at it, or an empty string.
    """
    if case == "empty":
        return ""
    if case == "relative":
        (p.cwd / "puppeteer.json").write_text("{}", encoding="utf-8")
        return "puppeteer.json"
    if case == "missing":
        return str(p.harness / "no-such-puppeteer.json")
    directory = p.harness / "puppeteer-dir"
    directory.mkdir()
    return str(directory)


@pytest.mark.parametrize("site", SITES)
def test_mmdc_gets_no_puppeteer_flag_when_the_variable_is_unset(tmp_path: Path, site: str):
    """No variable, no ``-p``. The run has to reach the call site for this to mean anything."""
    p = _site_project(tmp_path, site)

    proc = p.extract(stub_mmdc=True)
    assert proc.returncode == 0, _describe(proc)
    argv = _the_one_call(p, site)
    assert "-p" not in argv, argv


@pytest.mark.parametrize("site", SITES)
def test_mmdc_gets_an_absolute_puppeteer_config_file_as_dash_p(tmp_path: Path, site: str):
    """An absolute path to a regular file reaches mmdc as ``-p <path>``, verbatim, once."""
    p = _site_project(tmp_path, site)
    config = p.harness / "puppeteer-no-sandbox.json"
    config.write_text('{"args": ["--no-sandbox"]}', encoding="utf-8")

    proc = p.extract(stub_mmdc=True, puppeteer_config=str(config))
    assert proc.returncode == 0, _describe(proc)
    argv = _the_one_call(p, site)
    assert argv.count("-p") == 1, argv
    assert argv[argv.index("-p") + 1] == str(config), argv


@pytest.mark.parametrize("case", BAD_PUPPETEER_VALUES)
@pytest.mark.parametrize("site", SITES)
def test_a_bad_puppeteer_config_stops_the_run_before_mmdc_starts(tmp_path: Path, site: str, case: str):
    """Anything but an absolute path to a regular file fails the run loudly, naming
    the variable, with mmdc never started and nothing written (``out/`` is never
    created). The stub is on PATH, so the mmdc-missing preflight cannot be what
    stops the run."""
    p = _site_project(tmp_path, site)
    value = _bad_puppeteer_value(p, case)
    before = p.snapshot()

    proc = p.extract(stub_mmdc=True, puppeteer_config=value)
    assert proc.returncode != 0, _describe(proc)
    assert NAMES_PUPPETEER_ENV.search(proc.stderr), "the error must name the variable: %s" % _describe(proc)
    assert p.mmdc_calls() == [], "mmdc must not start: %s" % _describe(proc)
    assert p.snapshot() == before, "a refused run must not write anything"


# =============================================================================
# Legacy mode (--output) still writes next to the artifacts
# =============================================================================


def test_legacy_mode_still_writes_next_to_the_artifacts(tmp_path: Path):
    """``--output`` mode: diagrams, the corrected copy and the cleanup stay in the target."""
    p = Project(tmp_path)
    p.add_artifacts(trees_and_chains=True)
    mislabeled = _add_infographics(p)
    legacy_data = p.cwd / "legacy-out" / "report-data.typ"
    before = p.snapshot()

    proc = p.extract_legacy(legacy_data)
    assert proc.returncode == 0, _describe(proc)
    after = p.snapshot()
    added, changed, removed = _diff(before, after)
    target, legacy_out = p.key(p.target), p.key(legacy_data.parent)
    expected = {
        legacy_out,
        legacy_out + "/report-data.typ",
        target + "/attack-trees/t-1-attack-tree.png",
        target + "/attack-chains",
        target + "/attack-chains/chain-001-attack-chain.png",
        target + "/threat-baseball-card.png",
    }
    assert not changed and not removed, (changed, removed)
    assert {a for a in added if not _within(a, p.key(p.systmp))} == expected, sorted(added)
    assert (p.target / "threat-baseball-card.png").read_bytes() == mislabeled
    assert "writing corrected sibling threat-baseball-card.png\n" in proc.stderr, _describe(proc)

    # image paths stay relative to the template directory, as before
    data = legacy_data.read_text(encoding="utf-8")
    to_target = os.path.relpath(str(p.target), str(p.templates)).replace(os.sep, "/")
    assert 'image-path: "%s/attack-trees/t-1-attack-tree.png"' % to_target in data
    assert 'image-path: "%s/attack-chains/chain-001-attack-chain.png"' % to_target in data
    assert '#let baseball-image-path = "%s/threat-baseball-card.png"' % to_target in data

    # the opt-in cleanup deletes the mislabeled duplicate in the target, as before
    again = p.extract_legacy(legacy_data, "--cleanup-mislabeled-images")
    assert again.returncode == 0, _describe(again)
    assert not (p.target / "threat-baseball-card.jpg").exists()
    assert (p.target / "threat-baseball-card.png").read_bytes() == mislabeled
    assert "Cleanup: deleted mislabeled duplicate" in again.stderr, _describe(again)


# =============================================================================
# AR-14: a stock run of each installed entry script leaves no bytecode cache
# =============================================================================

# The installed scripts that import the sibling ``tachi_parsers`` at module level.
# Each turns bytecode writing off itself when run as a script, before that import.
ENTRY_SCRIPTS_IMPORTING_PARSERS = (
    "extract-report-data.py",
    "extract-infographic-data.py",
    "populate-affected-assets.py",
)


@pytest.mark.parametrize("entry", ENTRY_SCRIPTS_IMPORTING_PARSERS)
def test_a_stock_run_of_each_entry_script_leaves_no_bytecode_cache(tmp_path: Path, entry: str):
    """AR-14: ``python3 scripts/<entry> --help``, with no ``-B`` and no
    ``PYTHONDONTWRITEBYTECODE``, caches none of the project's own modules.

    A stock run would cache the imported ``tachi_parsers`` in ``scripts/__pycache__/``,
    or, on an interpreter with a default cache prefix (macOS's ``/usr/bin/python3``),
    outside the project. A test-owned ``PYTHONPYCACHEPREFIX`` sends every cache to a
    directory this test reads, on any interpreter, so the case fails whenever the
    script's guard is missing. The interpreter caches the standard library under
    the prefix too; only the project's own modules are checked.
    """
    project = tmp_path / "project"
    scripts = project / "scripts"
    scripts.mkdir(parents=True)
    for name in (entry, "tachi_parsers.py"):
        shutil.copy2(str(SCRIPTS_DIR / name), str(scripts / name))
    prefix = tmp_path / "pycache-prefix"
    prefix.mkdir()

    env = dict(os.environ)
    env["PYTHONPYCACHEPREFIX"] = str(prefix)
    env.pop("PYTHONDONTWRITEBYTECODE", None)  # a developer's setting must not mask a regression
    proc = subprocess.run(
        [sys.executable, "scripts/" + entry, "--help"],
        cwd=str(project),
        env=env,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=SUBPROCESS_TIMEOUT,
    )

    # Exit 0 also proves the module-level ``tachi_parsers`` import ran.
    assert proc.returncode == 0, _describe(proc)
    assert not (scripts / "__pycache__").exists(), "a stock run wrote scripts/__pycache__/"
    cached = sorted(
        path.relative_to(prefix).as_posix()
        for module in scripts.glob("*.py")
        for path in prefix.rglob(module.stem + ".cpython-*.pyc")
    )
    assert not cached, "a stock run cached the project's own modules under the prefix: %s" % cached


# =============================================================================
# Static assertion (T015) and AR-1 case 4: the recipes never name a bad write target
# =============================================================================

# The three documents T015 names, plus the two skill references AR-1 case 4 adds.
RECIPE_DOCS = (
    ".claude/agents/tachi/report-assembler.md",
    ".claude/agents/tachi/threat-infographic.md",
    ".claude/commands/tachi.infographic.md",
    ".claude/skills/tachi-infographics/references/gemini-prompt-construction.md",
    ".claude/skills/tachi-report-assembly/references/typst-artifacts.md",
)
METADATA_LANGUAGES = ("yaml", "yml")

_FENCE_OPEN = re.compile(r"^\s*(`{3,}|~{3,})([^`]*)$")
_FENCE_CLOSE = re.compile(r"^\s*(`{3,}|~{3,})\s*$")
# /tmp, /var/tmp and their /private forms, but not a/tmp, {out}/tmp, ~/tmp or ./tmp.
_TMP_PATH = re.compile(r"(?<![\w.~}\])/])(?:/private)?/(?:var/)?tmp(?!\w)")
_WRITE_FLAGS = {
    "--output", "-o", "--out", "--output-dir", "--outdir",
    "--build-dir", "--remove-build-dir", "--dest", "--destination",
}
_ALL_ARGS_ARE_WRITES = {"rm", "rmdir", "unlink", "mv", "touch", "mkdir", "tee", "truncate", "chmod", "chown"}
_LAST_ARG_IS_WRITE = {"cp", "install", "rsync", "ln"}
_COMMAND_WRAPPERS = {"sudo", "command", "env", "time", "exec"}
_TYPST_OUTPUT_SUFFIXES = (".pdf", ".png", ".svg", ".html")
_QUOTES = "\"'`"


def _fenced_blocks(text: str) -> Iterator[Tuple[str, int, List[str]]]:
    """Yield ``(language, first body line number, body lines)`` per fenced block.

    A leading ``---`` front-matter pair is skipped. An unclosed fence yields
    what it holds, so a malformed document is scanned rather than ignored.
    """
    lines = text.splitlines()
    index = 0
    if lines and lines[0].strip() == "---":
        index = 1
        while index < len(lines) and lines[index].strip() != "---":
            index += 1
        index += 1
    fence = None  # (character, length) of the open fence
    language, start = "", 0
    body = []  # type: List[str]
    for number in range(index, len(lines)):
        line = lines[number]
        if fence is None:
            opening = _FENCE_OPEN.match(line)
            if opening:
                fence = (opening.group(1)[0], len(opening.group(1)))
                info = opening.group(2).split()
                language, start, body = (info[0].lower() if info else ""), number + 2, []
        else:
            closing = _FENCE_CLOSE.match(line)
            if closing and closing.group(1)[0] == fence[0] and len(closing.group(1)) >= fence[1]:
                yield language, start, body
                fence = None
            else:
                body.append(line)
    if fence is not None:
        yield language, start, body


def _logical_lines(lines: List[str]) -> Iterator[str]:
    """Join backslash-continued lines."""
    pending = ""
    for line in lines:
        if line.rstrip().endswith("\\"):
            pending += line.rstrip()[:-1] + " "
        else:
            yield pending + line
            pending = ""
    if pending:
        yield pending


def _write_targets(lines: List[str]) -> List[str]:
    """Paths a shell-like fence writes to or deletes, best effort and prose-tolerant.

    Sources: an option that takes an output path (``--output``, ``--build-dir``,
    ``--remove-build-dir``, ``-o`` ...), a redirection, the destination of
    ``cp``/``install``/``rsync``/``ln``, every argument of ``rm``/``mv``/``touch``/
    ``mkdir``/``tee`` ..., and the output file of ``typst compile``. Reading a
    path (``test -f``, a ``cp`` source, ``typst compile``'s input) is not a write.
    """
    targets = []  # type: List[str]
    for line in _logical_lines(lines):
        for segment in re.split(r"&&|\|\||[;|]", line):
            tokens = segment.split()
            while tokens and (re.match(r"^[A-Za-z_]\w*=", tokens[0]) or tokens[0] in _COMMAND_WRAPPERS):
                tokens = tokens[1:]
            if not tokens:
                continue
            command = os.path.basename(tokens[0].strip(_QUOTES))
            args = [t.strip(_QUOTES) for t in tokens[1:]]
            positional = [a for a in args if not a.startswith("-")]
            if command in _ALL_ARGS_ARE_WRITES:
                targets += positional
            elif command in _LAST_ARG_IS_WRITE and positional:
                targets.append(positional[-1])
            elif command == "typst":
                targets += [a for a in args if a.endswith(_TYPST_OUTPUT_SUFFIXES)]
            for position, token in enumerate(tokens):
                bare = token.strip(_QUOTES)
                following = tokens[position + 1].strip(_QUOTES) if position + 1 < len(tokens) else ""
                flag, equals, value = bare.partition("=")
                if flag in _WRITE_FLAGS:
                    targets.append(value.strip(_QUOTES) if equals else following)
                redirect = re.match(r"^(?:\d|&)?>>?(.*)$", bare)
                if redirect:
                    targets.append(redirect.group(1).strip(_QUOTES) or following)
    return [t for t in targets if t]


def _violations(text: str) -> List[str]:
    """Every ``/tmp`` use, and every write target under ``templates/tachi/``, in ``text``'s fences.

    Metadata (YAML) blocks may name the read-only template source, so they are
    exempt from the write-target rule; nothing is exempt from the ``/tmp`` rule.
    """
    found = []
    for language, first_line, body in _fenced_blocks(text):
        joined = "\n".join(body)
        for match in _TMP_PATH.finditer(joined):
            found.append("line %d (%s fence): uses %s" % (first_line, language or "plain", match.group(0)))
        if language in METADATA_LANGUAGES:
            continue
        for target in _write_targets(body):
            if "templates/tachi" in target:
                found.append("line %d (%s fence): writes %s" % (first_line, language or "plain", target))
    return found


@pytest.mark.parametrize("rel", RECIPE_DOCS)
def test_recipe_fences_never_write_under_templates_or_use_tmp(rel: str):
    """T015's static assertion, and AR-1 case 4 for the two skill references."""
    text = (REPO_ROOT / rel).read_text(encoding="utf-8")
    assert not _violations(text), "%s:\n  %s" % (rel, "\n  ".join(_violations(text)))


@pytest.mark.parametrize("rel", RECIPE_DOCS)
def test_the_fence_scanner_sees_each_recipe_document(rel: str):
    """Guards the guard: a scanner that finds no fence or no write target proves nothing."""
    blocks = list(_fenced_blocks((REPO_ROOT / rel).read_text(encoding="utf-8")))
    shell_like = [b for b in blocks if b[0] not in METADATA_LANGUAGES]
    assert shell_like, "%s: no non-metadata fenced block found" % rel
    assert any(_write_targets(body) for _, _, body in shell_like), "%s: no write target recognised" % rel
    if rel.endswith(("report-assembler.md", "threat-infographic.md")):
        assert any(b[0] in METADATA_LANGUAGES for b in blocks), "%s: its metadata block was not seen" % rel


# The pre-391 recipes, verbatim in shape: both must be caught.
OLD_EXTRACT_FENCE = r"""python3 scripts/extract-report-data.py \
  --target-dir {target_dir} \
  --output templates/tachi/security-report/report-data.typ \
  --template-dir templates/tachi/security-report/ \
  [--title "{title_override}"]
"""
OLD_CLEANUP_FENCE = r"""python3 scripts/extract-report-data.py \
  --target-dir {target_dir} \
  --output templates/tachi/security-report/report-data.typ \
  --template-dir templates/tachi/security-report/ \
  --cleanup-mislabeled-images
"""


def _as_markdown(body: str, language: str = "bash") -> str:
    return "# doc\n\n```%s\n%s```\n" % (language, body)


@pytest.mark.parametrize(
    "body",
    [
        pytest.param(OLD_EXTRACT_FENCE, id="old-extract-output-into-templates"),
        pytest.param(OLD_CLEANUP_FENCE, id="old-cleanup-output-into-templates"),
        pytest.param(
            "cp {target_dir}/report-config.typ templates/tachi/security-report/report-config.typ\n",
            id="cp-destination",
        ),
        pytest.param("rm templates/tachi/security-report/report-data.typ\n", id="rm"),
        pytest.param("mv x.typ ./templates/tachi/security-report/\n", id="mv"),
        pytest.param("echo hi > templates/tachi/security-report/x.typ\n", id="redirect"),
        pytest.param("echo hi >> templates/tachi/security-report/x.typ\n", id="append"),
        pytest.param("tee templates/tachi/security-report/x.typ < in.typ\n", id="tee"),
        pytest.param(
            "typst compile main.typ templates/tachi/security-report/out.pdf --root .\n",
            id="typst-output",
        ),
        pytest.param("python3 s.py --output=templates/tachi/security-report/data.typ\n", id="output-equals"),
        pytest.param("python3 s.py --build-dir templates/tachi/security-report\n", id="build-dir"),
        pytest.param("curl -o templates/tachi/x.json https://example.test\n", id="curl-o"),
        pytest.param("python3 s.py --output /tmp/data.json\n", id="tmp-output"),
        pytest.param('cd "${TMPDIR:-/tmp}"\n', id="tmp-fallback"),
        pytest.param("cp x /private/tmp/x\n", id="private-tmp"),
    ],
)
def test_the_scanner_flags_what_it_exists_to_flag(body: str):
    assert _violations(_as_markdown(body)), body


@pytest.mark.parametrize(
    "body",
    [
        pytest.param("test -f templates/tachi/security-report/main.typ\n", id="test-reads"),
        pytest.param(
            'cp -R templates/tachi/security-report/. "{out}/.tachi-build/security-report/"\n',
            id="cp-source",
        ),
        pytest.param(
            "typst compile {output_path}/.tachi-build/security-report/main.typ "
            "{output_path}/security-report.pdf --root .\n",
            id="typst-compile",
        ),
        pytest.param(
            "python3 scripts/extract-report-data.py \\\n  --target-dir {target_dir} \\\n"
            "  --build-dir {output_path}/.tachi-build/security-report\n",
            id="extract-build-dir",
        ),
        pytest.param(
            "python3 scripts/extract-report-data.py "
            "--remove-build-dir {output_path}/.tachi-build/security-report\n",
            id="extract-remove-build-dir",
        ),
        pytest.param(
            "python3 scripts/extract-infographic-data.py --target-dir {d} --template t "
            "--output {output_dir}/.tachi-build/infographic-t.json\n",
            id="infographic-output",
        ),
        pytest.param(
            'curl --output "{response_file}" --config - <<EOF\nheader = "x-goog-api-key: $GEMINI_API_KEY"\nEOF\n',
            id="curl-output",
        ),
        pytest.param("echo $TMPDIR/x ; ls {out}/tmp ~/tmp ./tmp ../tmp a/tmp\n", id="tmp-lookalikes"),
        pytest.param('if [ -z "${GEMINI_API_KEY:-}" ]; then echo "not set"; fi\n', id="key-check"),
    ],
)
def test_the_scanner_accepts_reads_and_confined_writes(body: str):
    assert not _violations(_as_markdown(body)), body


def test_the_scanner_exempts_metadata_blocks_from_the_write_rule_only():
    """YAML metadata may name the read-only template source; front matter is not a fence."""
    metadata = (
        "references:\n  templates:\n"
        "    directory: ../../../templates/tachi/security-report/  # read-only source\n"
    )
    assert not _violations(_as_markdown(metadata, "yaml"))
    assert _violations(_as_markdown("output_files:\n  - /tmp/report.pdf\n", "yaml"))
    with_frontmatter = "---\nname: x\ndescription: \"```bash\"\n---\n\nprose\n"
    assert not list(_fenced_blocks(with_frontmatter)), "front matter is not a fence"
