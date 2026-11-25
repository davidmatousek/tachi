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
- command-line refusals (EC-5): a bad flag combination, a missing flag reported
  before an unknown one, an unknown flag on its own, ``--target-dir`` equal to or
  inside the build directory and a file at its path each exit 2 with a one-line
  reason and write nothing. Needs no Typst.
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
- AR-14: a stock ``python3 scripts/<entry> --help`` of each installed entry
  script that imports ``tachi_parsers`` (the three extractors, ``tachi-stage.py``,
  the two renderers and PR 2's four entries), with its local-import closure installed
  beside it, leaves no bytecode cache, in the project or under a test-owned
  ``PYTHONPYCACHEPREFIX``.
- F-374 (ADR-050 D16): ``tachi-stage.py`` runs ``plan``, ``reconcile`` and
  ``fail`` for each batched stage on the gated fixture, in a throwaway project,
  and every write lands under ``--out``. Its ``architecture-source`` command is
  the one write outside ``--out``: it edits only the ``--threats`` file, and it
  refuses a symlinked or non-regular one with exit 2. No run writes bytecode.
  Needs no Typst.
- F-374 (ADR-050 D16): ``render-risk-scores.py`` runs on the same fixture, after
  ``tachi-stage.py`` has planned and reconciled the ``risk-score`` stage and this
  module has written its parts as the scorer agent does. The renderer loads
  ``populate-affected-assets.py`` by path at run time, so the project installs that
  file beside it, and a case holds the install manifest to listing it. Every write
  of a first run, and of a run over earlier outputs, lands under ``--out``; a
  refused run writes nothing; no run writes bytecode. Needs no Typst.
- F-374 (ADR-050 D16): ``render-compensating-controls.py`` runs on the same fixture,
  after the scorer's whole run has left its ``risk-scores.md`` in ``--out``, and after
  ``tachi-stage.py`` has planned and reconciled the ``compensating-controls`` stage and
  this module has written its parts as the control-analyzer agent does. It loads no
  script by path, so its install is its import closure. Every write of a first run, and
  of a run over earlier outputs, lands under ``--out``, and none of the scorer's files
  changes; a refused run writes nothing; no run writes bytecode. Needs no Typst.
- F-374 (ADR-050 D16), PR 2: ``join-threats-md.py``, ``attack-chains.py``, ``assemble-report.py``
  and ``generate-threats-sarif.py`` each run as a process in a project of their own.
  The generator reads the gated fixture; the other three read a synthetic run that their
  own test modules build, and this module takes the builder from them. Every write lands
  under the one directory that the entry writes (``--out``, or ``--run-dir`` for the chain
  script and the assembler), the inputs and the baseline are unchanged, a refused run
  writes nothing, and no run writes bytecode. Needs no Typst.
- AR-1 case 4 and the T015 static assertion: no fenced block in the eight
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
import json
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

# The one definition of what a script needs installed beside it: the manifest test's import closure (ADR-050 D16),
# and its reader of the installer's machine-readable block.
from .test_install_manifest_completeness import MANIFEST_PATH, _import_closure, read_manifest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
SCHEMAS_DIR = REPO_ROOT / "schemas"
TEMPLATE_DIR = REPO_ROOT / "templates" / "tachi" / "security-report"
# Tier 1, three findings, no attack trees or chains, no images: the
# extractor never shells out to mmdc on it (also used by the posture contract).
FIXTURE_DIR = (
    REPO_ROOT / "tests" / "scripts" / "fixtures" / "fidelity_373" / "posture_mmdc_free"
)
# The installed set the report build needs: the extractor, ``tachi_parsers.py`` and the helper that
# ``tachi_parsers.py`` imports at module load (ADR-050 D3). The report-assembler's preflight (step 2b) names
# all three, and ``test_contract_text_374.py`` keeps it equal to the extractor's import closure.
INSTALLED_SCRIPTS = ("extract-report-data.py", "tachi_parsers.py", "tachi_parts.py")

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


# The extractor's refusals of a bad command line or build directory, one case each:
# ``case -> (flags after the script name, a fragment of the reason on stderr)``, with
# ``{t}`` the target directory, ``{b}`` the build directory and ``{o}`` an --output path.
CLI_REFUSALS = {
    # _resolve_cli_mode: the legacy form needs all three of its flags
    "legacy-without-template-dir": ("--target-dir {t} --output {o}", "required: --template-dir"),
    # _resolve_cli_mode: --build-dir replaces --output and needs --target-dir
    "build-dir-with-output": (
        "--target-dir {t} --build-dir {b} --output {o}",
        "--output cannot be combined with --build-dir",
    ),
    # the newline ends the reason at --target-dir; the legacy form would list all three flags
    "build-dir-without-target-dir": ("--build-dir {b}", "required: --target-dir\n"),
    # _resolve_cli_mode: --remove-build-dir takes no other flag
    "remove-build-dir-with-target-dir": (
        "--remove-build-dir {b} --target-dir {t}",
        "--remove-build-dir cannot be combined with --target-dir",
    ),
    # main: a missing flag is reported before an unknown one, as argparse's own check always did
    "missing-flag-before-unknown-flag": (
        "--target-dir {t} --output {o} --bogus",
        "required: --template-dir",
    ),
    # main: an unknown flag on its own is refused, never ignored
    "unknown-flag-alone": ("--target-dir {t} --build-dir {b} --bogus", "unrecognized arguments: --bogus"),
    # _guard_build_dir: the two rules that no other case reaches
    "target-dir-is-the-build-dir": (
        "--target-dir {b} --build-dir {b}",
        "it contains the target directory",
    ),
    # recreating a build directory that holds the target directory would delete the inputs
    "target-dir-inside-the-build-dir": (
        "--target-dir {b}/inputs --build-dir {b}",
        "it contains the target directory",
    ),
    "build-dir-is-a-file": ("--target-dir {t} --build-dir {b}", "it exists and is not a directory"),
}


@pytest.mark.parametrize("case", CLI_REFUSALS)
def test_a_bad_command_line_or_build_dir_exits_2_with_its_reason_and_writes_nothing(
    project: Project, case: str
):
    """Exit 2, the reason on stderr, and nothing written anywhere. Needs no Typst."""
    if case == "build-dir-is-a-file":
        project.build.parent.mkdir()
        project.build.write_text("a file where the build directory belongs", encoding="utf-8")
    flags, reason = CLI_REFUSALS[case]
    argv = [sys.executable, "scripts/extract-report-data.py"] + flags.format(
        t=project.rel(project.target),
        b=project.rel(project.build),
        o=project.rel(project.out / "report-data.typ"),
    ).split()
    before = project.snapshot()

    proc = project._run(argv)
    assert proc.returncode == 2, _describe(proc)
    assert reason in proc.stderr, _describe(proc)
    assert project.snapshot() == before, "a refused run must not touch anything"


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

# The installed entry scripts that import the sibling ``tachi_parsers`` at module level, directly or through
# ``sarif_common``. Each turns bytecode writing off itself when run as a script, before its first local import.
# A new entry joins this tuple and gets its own group below (ADR-050 D16).
ENTRY_SCRIPTS_IMPORTING_PARSERS = (
    "extract-report-data.py",
    "extract-infographic-data.py",
    "populate-affected-assets.py",
    "tachi-stage.py",
    "render-risk-scores.py",
    "render-compensating-controls.py",
    "join-threats-md.py",
    "attack-chains.py",
    "assemble-report.py",
    "generate-threats-sarif.py",
)

# The scripts an entry loads by path when it runs. No import statement names them, so the import closure can't see
# them, and an install places them beside the entry all the same (the manifest lists each). ``render-risk-scores.py``
# takes the populator's component join (ADR-050 D2), and stops with exit 1 when the file is not installed.
# ``render-compensating-controls.py`` loads none (it reads the threat model that its plan names, and joins no component
# to an asset tag), so it has no row. Nor have PR 2's four entries, which import their helpers and load nothing else.
LOADED_BY_PATH = {
    "render-risk-scores.py": ("populate-affected-assets.py",),
}  # type: Dict[str, Tuple[str, ...]]


def _install_with_closure(entry: str, scripts: Path) -> List[str]:
    """Copy ``entry``, its local-import closure and what it loads by path into ``scripts``, as an install places them.

    The closure is the manifest test's own (``_import_closure``), so a script that gains an import is installed
    with it here, and the manifest must list it. ``LOADED_BY_PATH`` adds the scripts that the entry loads at run
    time, and the closure of those too. Returns the names of the siblings copied.
    """
    loaded = LOADED_BY_PATH.get(entry, ())
    seeds = {"scripts/" + name for name in (entry,) + loaded}
    closure = sorted({Path(ref).name for ref in _import_closure(seeds)} | set(loaded))
    assert closure, "%s imports no sibling script, so the closure is empty: update this case" % entry
    for name in sorted({entry} | set(closure)):
        shutil.copy2(str(SCRIPTS_DIR / name), str(scripts / name))
    return closure


@pytest.mark.parametrize("entry", sorted(LOADED_BY_PATH))
def test_each_script_loaded_by_path_is_in_the_install_manifest(entry: str):
    """The manifest test's import closure can't see a script that an entry loads by path, so this names each one.

    ``LOADED_BY_PATH`` says an install places these beside the entry. This holds the manifest to it, so an entry
    that starts to load another script at run time fails here, and not in an adopter's project.
    """
    listed = read_manifest(MANIFEST_PATH.read_text(encoding="utf-8"))
    for name in (entry,) + LOADED_BY_PATH[entry]:
        assert "scripts/" + name in listed, "INSTALL_MANIFEST.md doesn't list scripts/%s (%s loads it by path)" % (name, entry)


@pytest.mark.parametrize("entry", ENTRY_SCRIPTS_IMPORTING_PARSERS)
def test_a_stock_run_of_each_entry_script_leaves_no_bytecode_cache(tmp_path: Path, entry: str):
    """AR-14: ``python3 scripts/<entry> --help``, with no ``-B`` and no
    ``PYTHONDONTWRITEBYTECODE``, caches none of the project's own modules.

    A stock run would cache the imported siblings (``tachi_parsers`` and what it imports) in
    ``scripts/__pycache__/``, or, on an interpreter with a default cache prefix (macOS's
    ``/usr/bin/python3``), outside the project. A test-owned ``PYTHONPYCACHEPREFIX`` sends every
    cache to a directory this test reads, on any interpreter, so the case fails whenever the
    script's guard is missing. The interpreter caches the standard library under the prefix too;
    only the project's own modules are checked.
    """
    project = tmp_path / "project"
    scripts = project / "scripts"
    scripts.mkdir(parents=True)
    _install_with_closure(entry, scripts)
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
# F-374 (ADR-050 D16): tachi-stage.py writes only under {out} and leaves no bytecode
# =============================================================================
#
# Each new entry gets a group like this one: it runs the entry's commands on the gated fixture in a throwaway
# project, and fails on any path written outside ``{out}``. The gated fixture is the subset of S-4's synthetic
# large-architecture fixture that the gated tests read. Standard library and pytest only.

GATED_FIXTURE = REPO_ROOT / "tests" / "scripts" / "fixtures" / "large_arch" / "gated-subset"
STAGE_ENTRY = "tachi-stage.py"
STAGE_DATE = "2026-11-22"
# Each batched stage, with the extra arguments its plan takes from the fixture's inputs.
STAGES = {
    "risk-score": (),
    "compensating-controls": ("--risk-scores", "run/risk-scores.md", "--target", "run"),
}  # type: Dict[str, Tuple[str, ...]]
StageState = Tuple[Snapshot, Snapshot]


class EntryProject:
    """A throwaway adopter project that runs installed entry scripts, and the checks that every F-374 group makes of a run.

    Layout under ``root``: ``project/`` is the working directory. It holds ``scripts/``, where each entry that the project
    is given sits with its local-import closure, as an install places them. ``systmp/`` is ``$TMPDIR`` of every child, and
    ``pycache-prefix/`` takes any bytecode an interpreter writes outside the project. ``out_name`` is the one directory of
    ``project/`` that a run may write: ``out`` for the entries that take ``--out``, and ``run`` for the two that take
    ``--run-dir``. A subclass makes that directory and puts the run's inputs where its entry reads them.
    """

    out_name = "out"

    def __init__(self, root: Path, *entries: str):
        self.cwd = root / "project"
        self.out = self.cwd / self.out_name
        self.systmp = root / "systmp"
        self.prefix = root / "pycache-prefix"
        scripts = self.cwd / "scripts"
        for directory in (scripts, self.systmp, self.prefix):
            directory.mkdir(parents=True)
        for entry in entries:
            _install_with_closure(entry, scripts)

    def state(self) -> StageState:
        """The whole project, and ``$TMPDIR`` apart from it, as two snapshots."""
        return _snapshot(self.cwd), _snapshot(self.systmp)

    def run_entry(self, entry: str, *args: str) -> "subprocess.CompletedProcess":
        """``python3 scripts/<entry> ARGS`` in the project: the stock invocation, with bytecode caching left on."""
        env = dict(os.environ)
        env["TMPDIR"] = str(self.systmp)
        env["PYTHONPYCACHEPREFIX"] = str(self.prefix)  # a cache written outside the project lands where this reads
        env.pop("PYTHONDONTWRITEBYTECODE", None)  # a developer's setting must not mask a regression (AR-14)
        return subprocess.run(
            [sys.executable, "scripts/" + entry] + list(args),
            cwd=str(self.cwd),
            env=env,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=SUBPROCESS_TIMEOUT,
        )

    def assert_writes_only_under_out(
        self, before: StageState, after: StageState, label: str, also: Tuple[str, ...] = ()
    ) -> Tuple[Set[str], Set[str], Set[str]]:
        """Every path added, changed or removed since ``before`` sits under ``out_name`` or is one of ``also``.

        ``$TMPDIR`` must be as it was: the stage's writes are atomic in their own directory, so nothing goes there.
        Returns ``(added, changed, removed)`` over the project.
        """
        added, changed, removed = _diff(before[0], after[0])
        stray = sorted(p for p in added | changed | removed if not any(_within(p, base) for base in (self.out_name,) + also))
        assert not stray, "%s: wrote outside %s/: %s" % (label, self.out_name, stray)
        assert before[1] == after[1], "%s: wrote under $TMPDIR: %s" % (label, sorted(set(before[1]) ^ set(after[1])))
        return added, changed, removed

    def assert_no_bytecode(self) -> None:
        """No ``__pycache__`` or ``.pyc`` anywhere in the project, and none cached for its modules under the prefix."""
        found = sorted(
            p.relative_to(self.cwd).as_posix() for p in self.cwd.rglob("*") if p.name == "__pycache__" or p.suffix == ".pyc"
        )
        assert not found, "a run wrote bytecode into the project: %s" % found
        cached = sorted(
            path.relative_to(self.prefix).as_posix()
            for module in (self.cwd / "scripts").glob("*.py")
            for path in self.prefix.rglob(module.stem + ".cpython-*.pyc")
        )
        assert not cached, "a run cached the project's own modules under the prefix: %s" % cached


class StageProject(EntryProject):
    """A throwaway adopter project that runs ``tachi-stage.py`` on the gated fixture.

    Layout under ``root``: ``project/`` is the working directory. It holds ``scripts/`` (the entry and its
    local-import closure, as an install places them), ``run/`` (the fixture's three inputs: ``threats.md``,
    ``risk-scores.md`` and ``architecture.md``) and ``out/``, which exists before the first command, as a command
    creates it. ``systmp/`` is ``$TMPDIR`` of every child, and ``pycache-prefix/`` takes any bytecode an
    interpreter writes outside the project.
    """

    def __init__(self, root: Path):
        super().__init__(root, STAGE_ENTRY)
        self.inputs = self.cwd / "run"
        for directory in (self.inputs, self.out):
            directory.mkdir(parents=True)
        for source, name in (
            (GATED_FIXTURE / "baseline" / "threats.md", "threats.md"),
            (GATED_FIXTURE / "baseline" / "risk-scores.md", "risk-scores.md"),
            (GATED_FIXTURE / "architecture" / "architecture.md", "architecture.md"),
        ):
            shutil.copy2(str(source), str(self.inputs / name))

    def run(self, *args: str) -> "subprocess.CompletedProcess":
        """``python3 scripts/tachi-stage.py ARGS``: the stock invocation, with bytecode caching left on."""
        return self.run_entry(STAGE_ENTRY, *args)


@pytest.mark.parametrize("stage", sorted(STAGES))
def test_tachi_stage_plan_reconcile_and_fail_write_only_under_out(tmp_path: Path, stage: str):
    """``plan``, ``reconcile`` and ``fail`` write only under ``--out``, and leave the inputs and the scripts as they were.

    No part is ever written, so every batch is pending: ``reconcile`` splits them and exits 3, and ``fail``
    quarantines nothing and writes the stage record. The digest each command prints is the one the next takes.
    """
    project = StageProject(tmp_path)
    start = project.state()

    plan = project.run("plan", "--stage", stage, "--out", "out", "--date", STAGE_DATE,
                       "--threats", "run/threats.md", *STAGES[stage])
    assert plan.returncode == 0, _describe(plan)
    planned = json.loads(plan.stdout)
    added, _, _ = project.assert_writes_only_under_out(start, project.state(), "after plan")
    assert any(p.endswith("/plan.json") for p in added), "the snapshot must see the plan"

    reconcile = project.run("reconcile", "--stage", stage, "--out", "out",
                            "--plan", planned["plan_id"], "--plan-digest", planned["plan_digest"])
    assert reconcile.returncode == 3, _describe(reconcile)
    project.assert_writes_only_under_out(start, project.state(), "after reconcile")

    failed = project.run("fail", "--stage", stage, "--out", "out", "--plan", planned["plan_id"],
                         "--plan-digest", json.loads(reconcile.stdout)["plan_digest"], "--reason", "check-failed")
    assert failed.returncode == 0, _describe(failed)
    end = project.state()
    added, _, _ = project.assert_writes_only_under_out(start, end, "after fail")
    assert any(p.endswith("/stage-record.json") for p in added), "the snapshot must see the stage record"

    # The inputs and the installed scripts are byte-unchanged end to end, and nothing wrote bytecode.
    assert _under(end[0], "run") == _under(start[0], "run"), "the stage changed one of its inputs"
    assert _under(end[0], "scripts") == _under(start[0], "scripts"), "the stage changed an installed script"
    project.assert_no_bytecode()


def test_tachi_stage_architecture_source_edits_only_the_threats_file(tmp_path: Path):
    """``architecture-source`` is the one write outside ``--out``: it edits the ``--threats`` file in place.

    Nothing else changes, ``out/`` stays empty, and a second run finds the line already there.
    """
    project = StageProject(tmp_path)
    before = project.state()

    ran = project.run("architecture-source", "--threats", "run/threats.md", "--architecture", "run/architecture.md")
    assert ran.returncode == 0, _describe(ran)
    assert json.loads(ran.stdout)["action"] == "added"
    after = project.state()
    added, changed, removed = project.assert_writes_only_under_out(before, after, "after architecture-source",
                                                                   also=("run/threats.md",))
    assert changed == {"run/threats.md"} and not added and not removed, (added, changed, removed)
    assert set(_under(after[0], "out")) == {"out"}, "architecture-source wrote under out/"

    again = project.run("architecture-source", "--threats", "run/threats.md", "--architecture", "run/architecture.md")
    assert again.returncode == 0, _describe(again)
    assert json.loads(again.stdout)["action"] == "unchanged"
    assert project.state() == after, "a second run changed something"
    project.assert_no_bytecode()


@pytest.mark.parametrize("shape", ("symlink", "directory"))
def test_tachi_stage_architecture_source_refuses_a_link_or_a_non_regular_threats_file(tmp_path: Path, shape: str):
    """A symlinked or non-regular ``--threats`` exits 2 and writes nothing: an edit in place must not follow a link."""
    project = StageProject(tmp_path)
    threats = "run"
    if shape == "symlink":
        (project.inputs / "threats-link.md").symlink_to("threats.md")
        threats = "run/threats-link.md"
    before = project.state()

    ran = project.run("architecture-source", "--threats", threats, "--architecture", "run/architecture.md")
    assert ran.returncode == 2, _describe(ran)
    assert "TACHI THREAT-MODEL FAILED" in ran.stderr, _describe(ran)
    assert project.state() == before, "a refused run must write nothing"
    project.assert_no_bytecode()


# =============================================================================
# F-374 (ADR-050 D16): render-risk-scores.py writes only under {out} and leaves no bytecode
# =============================================================================
#
# The renderer reads what ``tachi-stage.py`` planned and what the scorer agent wrote, so its project is a
# ``StageProject`` that also holds the renderer and writes the parts. A run is the command's Steps 2 to 5 on the
# gated fixture: plan, one part per batch, reconcile, render. The renderer loads ``populate-affected-assets.py`` by
# path (``LOADED_BY_PATH``), so that file is installed beside it, as an install places it.

RENDER_ENTRY = "render-risk-scores.py"
SCORER_STAGE = "risk-score"
SUBSCORE_NAMES = (
    "known_techniques", "attack_complexity", "tooling_availability", "skill_level",
    "scriptability", "target_scope", "resource_requirements", "detection_difficulty",
)
# A narrative field keeps its digits in slots, which the renderer fills (ADR-050 D3). Free digits would take the
# fallback sentence and a flag, and this check wants a clean run.
SCORER_RATIONALE = {
    "cvss": "The base score is {{score:cvss_base}} for {{name:component}}.",
    "exploitability": "Public techniques give a mean of {{score:exploitability}}.",
    "scalability": "Repeatable at scale, with a mean of {{score:scalability}}.",
    "reachability": "{{name:zone}} yields {{score:reachability}}, with {{count:auth_barriers}} authentication "
                    "layers and {{count:network_boundaries}} network boundaries.",
}
TRUST_LEVELS = {"untrusted": "Untrusted", "semi-trusted": "Semi-Trusted", "trusted": "Trusted"}
# What an earlier run left in ``{out}``: the renderer replaces both, and the plan records them as its preimage.
EARLIER_OUTPUTS = {"risk-scores.md": b"# the earlier run's markdown\n", "risk-scores.sarif": b'{"earlier": "run"}\n'}


def _trust_zones(threats_text: str) -> Dict[str, Tuple[str, str]]:
    """``{component: (zone, trust level)}`` from the ``### Trust Zones`` table of a ``threats.md``.

    The level is the agent's spelling (``Semi-Trusted``), not the table's label (``Semi-trusted``).
    """
    zones = {}  # type: Dict[str, Tuple[str, str]]
    for line in threats_text.split("### Trust Zones", 1)[1].splitlines():
        if line.startswith("#"):  # the next heading ends the table
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not line.startswith("|") or cells[0] == "Zone" or not cells[0].strip("-"):
            continue  # prose, the header row or the rule under it
        for member in cells[2].split(","):
            zones[member.strip()] = (cells[0], TRUST_LEVELS[cells[1].lower()])
    assert zones, "the fixture's Section 2 lists no trust zone"
    return zones


class RenderProject(StageProject):
    """A ``StageProject`` that also installs ``render-risk-scores.py`` and writes the scorer's parts.

    ``write_parts`` stands in for the scorer agent (``contracts/part-files.md``): one part file per batch, holding one
    valid item for every finding that the batch input lists. Each item's zone and trust level are what Section 2 of
    the fixture's ``threats.md`` gives its component, so the renderer has nothing to correct.
    """

    def __init__(self, root: Path):
        super().__init__(root)
        _install_with_closure(RENDER_ENTRY, self.cwd / "scripts")
        self.zones = _trust_zones((self.inputs / "threats.md").read_text(encoding="utf-8"))

    def write_parts(self, planned: dict) -> None:
        """One part file per batch of the plan that ``planned`` is the output of, at the path its batch input names."""
        for wave in planned["waves"]:
            for entry in wave:
                batch = json.loads(Path(entry["input_path"]).read_text(encoding="utf-8"))
                items = []
                for unit in batch["units"]:
                    zone, trust = self.zones[unit["component"]]
                    items.append({
                        "finding_id": unit["finding_id"],
                        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N",
                        "exploitability": dict(zip(SUBSCORE_NAMES[:4], (5, 5, 5, 5))),
                        "scalability": dict(zip(SUBSCORE_NAMES[4:], (4, 4, 4, 4))),
                        "reachability": {"zone": zone, "trust_level": trust, "auth_barriers": 1, "network_boundaries": 0},
                        "rationale": dict(SCORER_RATIONALE),
                    })
                part = {
                    "schema": "tachi.part/1", "plan_id": batch["plan_id"], "batch_id": batch["batch_id"],
                    "stage": batch["stage"], "agent_type": batch["agent_type"], "finding_ids": list(batch["finding_ids"]),
                    "items": items, "fragments": [],
                }
                path = Path(batch["part_path"])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(part), encoding="utf-8")

    def prepare(self) -> Tuple[str, str]:
        """The command's Steps 2 to 4: plan, write the parts, reconcile. Returns ``(plan_id, plan_digest)``."""
        plan = self.run("plan", "--stage", SCORER_STAGE, "--out", "out", "--date", STAGE_DATE,
                        "--threats", "run/threats.md", "--architecture", "run/architecture.md")
        assert plan.returncode == 0, _describe(plan)
        planned = json.loads(plan.stdout)
        self.write_parts(planned)
        reconcile = self.run("reconcile", "--stage", SCORER_STAGE, "--out", "out",
                             "--plan", planned["plan_id"], "--plan-digest", planned["plan_digest"])
        assert reconcile.returncode == 0, _describe(reconcile)
        return planned["plan_id"], json.loads(reconcile.stdout)["plan_digest"]

    def render(self, plan_id: str, digest: str) -> "subprocess.CompletedProcess":
        """``python3 scripts/render-risk-scores.py --out out --plan ID --plan-digest HEX``: the command's Step 5."""
        return self.run_entry(RENDER_ENTRY, "--out", "out", "--plan", plan_id, "--plan-digest", digest)


@pytest.mark.parametrize("earlier", (False, True), ids=("first-run", "over-earlier-outputs"))
def test_render_risk_scores_writes_only_under_out(tmp_path: Path, earlier: bool):
    """The renderer writes both files and its record under ``--out``, and leaves the inputs and the scripts alone.

    Exit 5 is a success with warnings (the fixture's baseline is not on disk), so 0 and 5 both write both files.
    Over earlier outputs the two canonical files change instead of appearing. ``$TMPDIR`` stays as it was: the
    renderer stages inside the plan directory. The loaded-by-path populator caches no bytecode either.
    """
    project = RenderProject(tmp_path)
    if earlier:
        for name, content in EARLIER_OUTPUTS.items():
            (project.out / name).write_bytes(content)
    start = project.state()

    plan_id, digest = project.prepare()
    project.assert_writes_only_under_out(start, project.state(), "after plan, the parts and reconcile")

    rendered = project.render(plan_id, digest)
    assert rendered.returncode in (0, 5), _describe(rendered)
    end = project.state()
    added, changed, _ = project.assert_writes_only_under_out(start, end, "after render")
    outputs = {"out/risk-scores.md", "out/risk-scores.sarif"}
    assert outputs <= (changed if earlier else added), "both files must be written: %s" % sorted(added | changed)
    assert any(p.endswith("/stage-record.json") for p in added), "the snapshot must see the stage record"
    if earlier:
        assert all((project.out / name).read_bytes() != content for name, content in EARLIER_OUTPUTS.items())

    # The inputs and the installed scripts are byte-unchanged end to end, and nothing wrote bytecode.
    assert _under(end[0], "run") == _under(start[0], "run"), "the renderer changed one of its inputs"
    assert _under(end[0], "scripts") == _under(start[0], "scripts"), "the renderer changed an installed script"
    assert (project.cwd / "scripts" / "populate-affected-assets.py").is_file(), "the populator must be installed"
    project.assert_no_bytecode()


@pytest.mark.parametrize("case", ("digest-mismatch", "no-plan"))
def test_render_risk_scores_refuses_without_writing(tmp_path: Path, case: str):
    """A digest that differs exits 2 and a run directory with no plan exits 1, and neither writes anything."""
    project = RenderProject(tmp_path)
    if case == "digest-mismatch":
        plan_id, _ = project.prepare()
        digest, code = "0" * 64, 2
    else:
        plan_id, digest, code = "20261122T100000Z-0123456789ab", "0" * 64, 1
    before = project.state()

    refused = project.render(plan_id, digest)
    assert refused.returncode == code, _describe(refused)
    assert "TACHI RISK-SCORE FAILED" in refused.stderr, _describe(refused)
    assert project.state() == before, "a refused run must write nothing"
    project.assert_no_bytecode()


# =============================================================================
# F-374 (ADR-050 D16): render-compensating-controls.py writes only under {out} and leaves no bytecode
# =============================================================================
#
# The controls renderer reads the scorer's ``risk-scores.md``, what ``tachi-stage.py`` planned and what the control-analyzer
# agent wrote. So its project is a ``RenderProject`` that first runs the scorer, which is the command's own input, and then
# drives the controls stage as ``/tachi.compensating-controls`` does: plan, one part per batch, reconcile, render. The
# renderer loads no script by path, so the install it needs is its import closure, and ``score`` removes the one script
# that only the scorer loads by path before the stage runs.

CONTROLS_ENTRY = "render-compensating-controls.py"
CONTROLS_STAGE = "compensating-controls"
CONTROL_CATEGORIES = (
    "authentication", "input-validation", "rate-limiting", "encryption",
    "logging-audit", "csrf-protection", "csp-security-headers", "access-control",
)
# The display form of each status, as a Section 2 row spells it. A category is spelled by its slug, which the renderer
# reads as equal to the display name (``contracts/module-signatures.md``, the controls ``matrix_row``).
CONTROL_STATUS_CELLS = {"found": "Control Found", "partial": "Partial Control", "missing": "No Control Found"}
# The one file of the scanned codebase that a found or partial control cites. The project holds it under ``target/``.
CONTROLS_EVIDENCE_FILE = "src/gateway.py"
CONTROLS_EVIDENCE = {
    "file": CONTROLS_EVIDENCE_FILE, "line": 1, "language": "python",
    "snippet": "def check(request):\n    return verify(request.token)",
    "summary": "The handler verifies the caller before it runs.",
}
# The agent's recommendation for a partial or missing control: the four keys, once each and in order, and an Effort that
# starts with a level (``contracts/part-files.md``).
CONTROLS_RECOMMENDATION = (
    "**What to Implement**: Add a check in front of every handler.\n\n"
    "**Where to Implement**: src/gateway.py\n\n"
    "**Reference Patterns**: One shared middleware that every route passes through.\n\n"
    "**Effort Estimate**: Medium — one new module."
)
# What an earlier controls run left in ``{out}``: the renderer replaces both, and the plan records them as its preimage.
EARLIER_CONTROLS_OUTPUTS = {
    "compensating-controls.md": b"# the earlier run's controls markdown\n",
    "compensating-controls.sarif": b'{"earlier": "controls run"}\n',
}


def _maestro_layers(threats_text: str) -> Dict[str, str]:
    """``{component: layer code}`` from the ``### Components`` table of a ``threats.md``: ``L4`` for a cell that opens with it."""
    layers = {}  # type: Dict[str, str]
    for line in threats_text.split("### Components", 1)[1].splitlines():
        if line.startswith("#"):  # the next heading ends the table
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not line.startswith("|") or cells[0] == "Component" or not cells[0].strip("-"):
            continue  # prose, the header row or the rule under it
        layers[cells[0]] = cells[2].split()[0]
    assert layers, "the fixture's Section 1 lists no component"
    return layers


class ControlsProject(RenderProject):
    """A ``RenderProject`` that also installs ``render-compensating-controls.py`` and writes the control analyzer's parts.

    ``score`` is the scorer's whole run, which leaves the controls stage its input, ``out/risk-scores.md``.
    ``write_controls_parts`` stands in for the control-analyzer agent (``contracts/part-files.md``): one part file per
    batch, holding one valid item for every finding that the batch input lists. A finding's status and category are a
    fixed function of its ID, so a run repeats, and a found or partial control cites a file that ``target/`` holds. Each
    row's component and MAESTRO layer are what the fixture's ``threats.md`` gives the finding, so nothing is flagged.
    """

    def __init__(self, root: Path):
        super().__init__(root)
        _install_with_closure(CONTROLS_ENTRY, self.cwd / "scripts")
        self.layers = _maestro_layers((self.inputs / "threats.md").read_text(encoding="utf-8"))
        cited = self.cwd / "target" / CONTROLS_EVIDENCE_FILE
        cited.parent.mkdir(parents=True)
        cited.write_text("# a synthetic module of the scanned codebase\n", encoding="utf-8")

    def score(self) -> None:
        """The scorer's whole run, the command's Steps 2 to 5, which writes ``out/risk-scores.md`` for the controls stage.

        The scripts that only the scorer loads by path are removed afterwards. The controls stage loads none, so it must
        run without them: an install places them, and a by-path load added to the controls renderer would fail here.
        """
        plan_id, digest = self.prepare()
        scored = self.render(plan_id, digest)
        assert scored.returncode in (0, 5), _describe(scored)
        for name in LOADED_BY_PATH[RENDER_ENTRY]:
            (self.cwd / "scripts" / name).unlink()

    def _controls_item(self, unit: dict) -> dict:
        """One valid ``compensating-controls`` item for a unit row of the batch input."""
        seed = sum(ord(char) for char in unit["finding_id"])
        status = ("found", "partial", "missing")[seed % 3]
        category = CONTROL_CATEGORIES[seed % len(CONTROL_CATEGORIES)]
        # K8's 11 cells: the computed ones as slot tokens, and CF as the dash the renderer fills.
        cells = [unit["finding_id"], "—", unit["component"], self.layers[unit["component"]], unit["threat"],
                 "{{score:inherent}}", "{{band:inherent}}", CONTROL_STATUS_CELLS[status], category,
                 "{{score:residual}}", "{{band:residual}}"]
        return {
            "finding_id": unit["finding_id"], "control_status": status, "control_category": category,
            "confidence": None if status == "missing" else "High", "carried_forward": False,
            "evidence": [] if status == "missing" else [dict(CONTROLS_EVIDENCE)],
            "matrix_row": "| " + " | ".join(cells) + " |",
            "recommendation_body": None if status == "found" else CONTROLS_RECOMMENDATION,
        }

    def write_controls_parts(self, planned: dict) -> None:
        """One part file per batch of the plan that ``planned`` is the output of, at the path its batch input names."""
        for wave in planned["waves"]:
            for entry in wave:
                batch = json.loads(Path(entry["input_path"]).read_text(encoding="utf-8"))
                part = {
                    "schema": "tachi.part/1", "plan_id": batch["plan_id"], "batch_id": batch["batch_id"],
                    "stage": batch["stage"], "agent_type": batch["agent_type"], "finding_ids": list(batch["finding_ids"]),
                    "items": [self._controls_item(unit) for unit in batch["units"]], "fragments": [],
                }
                path = Path(batch["part_path"])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(part), encoding="utf-8")

    def prepare_controls(self) -> Tuple[str, str]:
        """The controls command's Steps 2 to 4: plan, write the parts, reconcile. Returns ``(plan_id, plan_digest)``."""
        plan = self.run("plan", "--stage", CONTROLS_STAGE, "--out", "out", "--date", STAGE_DATE,
                        "--risk-scores", "out/risk-scores.md", "--target", "target", "--architecture", "run/architecture.md")
        assert plan.returncode == 0, _describe(plan)
        planned = json.loads(plan.stdout)
        self.write_controls_parts(planned)
        reconcile = self.run("reconcile", "--stage", CONTROLS_STAGE, "--out", "out",
                             "--plan", planned["plan_id"], "--plan-digest", planned["plan_digest"])
        assert reconcile.returncode == 0, _describe(reconcile)
        return planned["plan_id"], json.loads(reconcile.stdout)["plan_digest"]

    def render_controls(self, plan_id: str, digest: str) -> "subprocess.CompletedProcess":
        """``python3 scripts/render-compensating-controls.py --out out --plan ID --plan-digest HEX``: the command's Step 5."""
        return self.run_entry(CONTROLS_ENTRY, "--out", "out", "--plan", plan_id, "--plan-digest", digest)


@pytest.mark.parametrize("earlier", (False, True), ids=("first-run", "over-earlier-outputs"))
def test_render_compensating_controls_writes_only_under_out(tmp_path: Path, earlier: bool):
    """The renderer writes both files and its record under ``--out``, and leaves its inputs and the scorer's files alone.

    Exit 5 is a success with warnings, so 0 and 5 both write both files. Over earlier outputs the two canonical files
    change instead of appearing. ``$TMPDIR`` stays as it was: the renderer stages inside the plan directory.
    """
    project = ControlsProject(tmp_path)
    project.score()
    if earlier:
        for name, content in EARLIER_CONTROLS_OUTPUTS.items():
            (project.out / name).write_bytes(content)
    start = project.state()

    plan_id, digest = project.prepare_controls()
    project.assert_writes_only_under_out(start, project.state(), "after plan, the parts and reconcile")

    rendered = project.render_controls(plan_id, digest)
    assert rendered.returncode in (0, 5), _describe(rendered)
    end = project.state()
    added, changed, _ = project.assert_writes_only_under_out(start, end, "after render")
    outputs = {"out/compensating-controls.md", "out/compensating-controls.sarif"}
    assert outputs <= (changed if earlier else added), "both files must be written: %s" % sorted(added | changed)
    assert any(p.startswith("out/.tachi-build/compensating-controls/") and p.endswith("/stage-record.json") for p in added), (
        "the snapshot must see the stage record"
    )
    if earlier:
        assert all((project.out / name).read_bytes() != content for name, content in EARLIER_CONTROLS_OUTPUTS.items())

    # What the stage reads is byte-unchanged end to end: the run's inputs, the scanned codebase, the installed scripts and
    # the scorer's own files. And nothing wrote bytecode.
    for tree in ("run", "target", "scripts", "out/risk-scores.md", "out/risk-scores.sarif", "out/.tachi-build/risk-score"):
        assert _under(end[0], tree) == _under(start[0], tree), "the controls renderer changed %s" % tree
    project.assert_no_bytecode()


@pytest.mark.parametrize("case", ("digest-mismatch", "no-plan"))
def test_render_compensating_controls_refuses_without_writing(tmp_path: Path, case: str):
    """A digest that differs exits 2 and a run directory with no plan exits 1, and neither writes anything."""
    project = ControlsProject(tmp_path)
    project.score()
    if case == "digest-mismatch":
        plan_id, _ = project.prepare_controls()
        digest, code = "0" * 64, 2
    else:
        plan_id, digest, code = "20261122T100000Z-0123456789ab", "0" * 64, 1
    before = project.state()

    refused = project.render_controls(plan_id, digest)
    assert refused.returncode == code, _describe(refused)
    assert "TACHI COMPENSATING-CONTROLS FAILED" in refused.stderr, _describe(refused)
    assert project.state() == before, "a refused run must write nothing"
    project.assert_no_bytecode()


# =============================================================================
# F-374 (ADR-050 D16), PR 2: the four Track O entries write only under {out} and leave no bytecode
# =============================================================================
#
# ``join-threats-md.py``, ``attack-chains.py``, ``assemble-report.py`` and ``generate-threats-sarif.py`` each run as a process, in a project
# of their own. Every path that a run adds, changes or removes must sit under the one directory that its entry writes: ``--out`` for the joiner
# and the generator, ``--run-dir`` for the chain script and the assembler. The generator reads the gated fixture. The other three read a run that
# the planner (T092's PR 2 modes) and the orchestrator leave, and neither is part of this process, so each of their test modules builds that run
# from the contracts' key sets, checked by ``tachi_parts``' own validators, and this module takes the builder from it. Each builder is imported
# when a case first needs it, as ``test_sarif_identity.py`` does for its harness, so a change in one of those modules can't break the F-391 cases
# or PR 1's groups. A refused run writes nothing, and no run writes bytecode. Needs no Typst.
#
# AOD-SIMPLIFICATION: three of the runs are stand-ins for T092's planner and the orchestrator — upgrade: drive tachi-stage.py's PR 2 plans here once T092 lands

JOIN_ENTRY = "join-threats-md.py"
CHAINS_ENTRY = "attack-chains.py"
ASSEMBLE_ENTRY = "assemble-report.py"
SARIF_ENTRY = "generate-threats-sarif.py"
# The run-level plan's ID, which only ``attack-chains.py check`` takes, for its hand-off file's place.
CHAINS_PLAN_ID = "20261124T120000Z-0123456789ab"
# What an earlier run, or an agent, left where an entry writes: each entry replaces its own file and leaves every other path as it was.
EARLIER_THREATS = b"# the earlier run's threats.md\n"
EARLIER_SARIF = b'{"earlier": "run"}\n'
EARLIER_TREE = b"# the earlier run's attack tree\n"
EARLIER_REPORT = b"# the report that an agent wrote\n"


def _files_among(snap: Snapshot, paths: Set[str]) -> Set[str]:
    """The paths of ``paths`` that ``snap`` records as files: a directory that a write makes on its way is no output of its own."""
    return {p for p in paths if snap[p][0] == "file"}


@pytest.mark.parametrize("out_name", ("out", "run"))
def test_the_checks_every_group_relies_on_flag_what_they_exist_to_flag(tmp_path: Path, out_name: str):
    """Each check of ``EntryProject`` is shown red on a planted fault, so that a green group means something.

    A write beside the entry's directory, a write under the other directory that an entry may take (``run/`` is a stray in a project whose entry
    takes ``--out``, and ``out/`` in one whose entry takes ``--run-dir``), a write under ``$TMPDIR`` and a bytecode cache are each refused. A write
    under the entry's own directory is not.
    """
    other = "run" if out_name == "out" else "out"
    project = type("Probe", (EntryProject,), {"out_name": out_name})(tmp_path)
    for name in (out_name, other):
        (project.cwd / name).mkdir()
    start = project.state()

    (project.cwd / out_name / "inside.txt").write_text("written by the entry", encoding="utf-8")
    project.assert_writes_only_under_out(start, project.state(), "an inside write")
    project.assert_no_bytecode()

    for stray in (project.cwd / "beside.txt", project.cwd / other / "other.txt"):
        stray.write_text("written outside", encoding="utf-8")
        with pytest.raises(AssertionError, match="wrote outside %s/" % out_name):
            project.assert_writes_only_under_out(start, project.state(), "a stray write")
        stray.unlink()
    (project.systmp / "tmpfile").write_text("written to TMPDIR", encoding="utf-8")
    with pytest.raises(AssertionError, match="wrote under .TMPDIR"):
        project.assert_writes_only_under_out(start, project.state(), "a TMPDIR write")
    (project.systmp / "tmpfile").unlink()

    (project.cwd / "scripts" / "__pycache__").mkdir()
    with pytest.raises(AssertionError, match="wrote bytecode"):
        project.assert_no_bytecode()
    (project.cwd / "scripts" / "__pycache__").rmdir()
    (project.prefix / "x").mkdir()
    (project.prefix / "x" / "helper.cpython-311.pyc").write_bytes(b"\0")
    (project.cwd / "scripts" / "helper.py").write_text("", encoding="utf-8")
    with pytest.raises(AssertionError, match="cached the project's own modules"):
        project.assert_no_bytecode()


class JoinProject(EntryProject):
    """An ``EntryProject`` that runs ``join-threats-md.py`` on a synthetic ``threats-md`` run in ``out/``.

    ``JoinRun`` (``test_threats_md_join.py``) leaves the run as the orchestrator and the planner would: the section manifest, the plan, its pointer,
    a batch input for each part and the parts. ``planned=False`` leaves the manifest alone, so the run has no plan.
    """

    def __init__(self, root: Path, planned: bool = True):
        from .test_threats_md_join import Run as JoinRun  # imported when a case first needs it

        super().__init__(root, JOIN_ENTRY)
        self.world = JoinRun(self.cwd)
        if planned:
            self.world.ready()
        else:
            self.world.write_manifest()

    def join(self, plan_id: Optional[str] = None, digest: Optional[str] = None) -> "subprocess.CompletedProcess":
        """``python3 scripts/join-threats-md.py --out out --plan ID --plan-digest HEX``: the orchestrator's step after the last reconcile."""
        return self.run_entry(JOIN_ENTRY, "--out", "out", "--plan", plan_id or self.world.plan_id,
                              "--plan-digest", digest or self.world.digest)


@pytest.mark.parametrize("earlier", (False, True), ids=("first-run", "over-earlier-output"))
def test_join_threats_md_writes_only_under_out(tmp_path: Path, earlier: bool):
    """The joiner writes ``threats.md`` and its stage record under ``--out``, and changes nothing that it reads.

    Over an earlier ``threats.md`` the file changes instead of appearing. The staged copy moves onto its name, so no file is left in a
    staging directory, and ``$TMPDIR`` stays as it was: the joiner stages inside the plan directory.
    """
    project = JoinProject(tmp_path)
    if earlier:
        (project.out / "threats.md").write_bytes(EARLIER_THREATS)
    start = project.state()

    joined = project.join()
    assert joined.returncode == 0, _describe(joined)
    end = project.state()
    added, changed, removed = project.assert_writes_only_under_out(start, end, "after join")
    record = "out/.tachi-build/threats-md/%s/stage-record.json" % project.world.plan_id
    assert _files_among(end[0], added) == ({record} if earlier else {"out/threats.md", record}), sorted(added)
    assert changed == ({"out/threats.md"} if earlier else set()) and not removed, (changed, removed)
    if earlier:
        assert (project.out / "threats.md").read_bytes() != EARLIER_THREATS
    assert set(json.loads(joined.stdout)) == {"record", "counts"}, _describe(joined)
    assert not [p for p in end[0] if "/staged/" in p and end[0][p][0] == "file"], "the staged file moved onto its name"
    project.assert_no_bytecode()


@pytest.mark.parametrize("case", ("digest-mismatch", "no-plan"))
def test_join_threats_md_refuses_without_writing(tmp_path: Path, case: str):
    """A digest that differs exits 2 and a run with no plan exits 1, and neither writes anything."""
    project = JoinProject(tmp_path, planned=(case == "digest-mismatch"))
    plan_id, code = (None, 2) if case == "digest-mismatch" else ("20261122T100000Z-0123456789ab", 1)
    before = project.state()

    refused = project.join(plan_id, "0" * 64)
    assert refused.returncode == code, _describe(refused)
    assert "TACHI THREATS-MD FAILED" in refused.stderr, _describe(refused)
    assert project.state() == before, "a refused run must write nothing"
    project.assert_no_bytecode()


class ChainsProject(EntryProject):
    """An ``EntryProject`` that runs ``attack-chains.py`` on a synthetic run in ``run/``, the entry's ``--run-dir``.

    ``plain_islands`` (``test_chain_script.py``) writes the run's ``threats.md`` and its Phase 1 inventory: two islands, so two surfaced
    chains. ``make_plan_dir`` leaves the run-level plan's directory, with its ``checks/``, as ``tachi-stage.py plan --stage threat-model`` would,
    because ``check`` writes its hand-off file there and nothing makes the plan directory for it.
    """

    out_name = "run"

    def __init__(self, root: Path):
        from .test_chain_script import plain_islands  # imported when a case first needs it

        super().__init__(root, CHAINS_ENTRY)
        self.world = plain_islands(self.cwd, 2)
        self.world.make_plan_dir(CHAINS_PLAN_ID)

    def chains(self, mode: str, *args: str) -> "subprocess.CompletedProcess":
        """``python3 scripts/attack-chains.py MODE --run-dir run ARGS``."""
        return self.run_entry(CHAINS_ENTRY, mode, "--run-dir", "run", *args)

    def narrate(self, plan_stdout: str) -> List[str]:
        """The orchestrator's narratives, for the surfaced chains that ``plan`` printed and for those only. Returns their IDs."""
        from .test_chain_script import default_texts, surfaced_ids, write_narratives  # imported when a case first needs them

        ids = surfaced_ids(plan_stdout)
        write_narratives(self.world, default_texts(ids))
        return ids


def test_attack_chains_plan_render_and_check_write_only_under_the_run_directory(tmp_path: Path):
    """Phase 3.5's three calls, each held to what its contract lets it write, and all of them to ``--run-dir``.

    ``plan`` writes ``chains.json`` and nothing else. ``render`` writes ``attack-chains.md`` and upserts the outcome record in ``threats.md``, the one
    file that it changes. ``check`` on that record changes nothing and writes its hand-off file. The orchestrator's ``narratives.json`` is written
    between the first two, by this test, and the Phase 1 inventory is read and never written.
    """
    project = ChainsProject(tmp_path)
    start = project.state()

    planned = project.chains("plan")
    assert planned.returncode == 0, _describe(planned)
    after_plan = project.state()
    added, changed, removed = project.assert_writes_only_under_out(start, after_plan, "after plan")
    assert _files_among(after_plan[0], added) == {"run/.tachi-build/chains/chains.json"} and not changed and not removed, (added, changed, removed)

    assert len(project.narrate(planned.stdout)) == 2, "two islands surface two chains: %s" % _describe(planned)
    narrated = project.state()

    rendered = project.chains("render")
    assert rendered.returncode == 0, _describe(rendered)
    after_render = project.state()
    added, changed, removed = project.assert_writes_only_under_out(narrated, after_render, "after render")
    assert _files_among(after_render[0], added) == {"run/attack-chains.md"} and changed == {"run/threats.md"} and not removed, (added, changed, removed)

    checked = project.chains("check", "--plan", CHAINS_PLAN_ID)
    assert checked.returncode == 0, _describe(checked)
    end = project.state()
    added, changed, removed = project.assert_writes_only_under_out(after_render, end, "after check")
    handoff = "run/.tachi-build/threat-model/%s/checks/attack-chains.json" % CHAINS_PLAN_ID
    assert _files_among(end[0], added) == {handoff} and not changed and not removed, (added, changed, removed)

    project.assert_writes_only_under_out(start, end, "over the whole run")
    assert _under(end[0], "run/.tachi-build/phase1") == _under(start[0], "run/.tachi-build/phase1"), "the inventory is read, never written"
    project.assert_no_bytecode()


# Each refusal, with the exit code that its mode gives it: a ``--run-dir`` that is no directory is 1 for ``plan`` and ``render`` and 2 for ``check``,
# whose codes have no 1 (``contracts/cli.md``), and a ``render`` that finds no ``chains.json`` is 1.
CHAINS_REFUSALS = {
    "plan-no-run-dir": (("plan", "--run-dir", "no-such-dir"), 1),
    "render-no-chains-json": (("render", "--run-dir", "run"), 1),
    "check-no-run-dir": (("check", "--run-dir", "no-such-dir", "--plan", CHAINS_PLAN_ID), 2),
}  # type: Dict[str, Tuple[Tuple[str, ...], int]]


@pytest.mark.parametrize("case", sorted(CHAINS_REFUSALS))
def test_attack_chains_refuses_without_writing(tmp_path: Path, case: str):
    """A run directory that isn't there, and a ``render`` with no ``chains.json``, are refused with their own exit codes, and write nothing."""
    project = ChainsProject(tmp_path)
    argv, code = CHAINS_REFUSALS[case]
    before = project.state()

    refused = project.run_entry(CHAINS_ENTRY, *argv)
    assert refused.returncode == code, _describe(refused)
    assert "TACHI ATTACK-CHAINS FAILED" in refused.stderr, _describe(refused)
    assert project.state() == before, "a refused run must write nothing"
    project.assert_no_bytecode()


class AssembleProject(EntryProject):
    """An ``EntryProject`` that runs ``assemble-report.py`` on a synthetic run in ``run/``, the entry's ``--run-dir``.

    ``World`` (``test_report_assembly.py``) leaves the ``trees`` stage as the planner and the attack-tree agents would: ``threats.md``, the plan, a
    batch input and a part for each batch, the agents' tree files and an earlier run's ``baseline/``. ``rule1`` takes most trees from that
    baseline and generates the rest, so the baseline is read and the plan's own tree files are copied. ``report_stage`` adds the ``report`` stage's
    plan and parts, which the planner writes after ``trees`` has run, on the manifest that ``trees`` wrote.
    """

    out_name = "run"

    def __init__(self, root: Path):
        from .test_report_assembly import World as ReportWorld  # imported when a case first needs it

        super().__init__(root, ASSEMBLE_ENTRY)
        self.world = ReportWorld(self.cwd, rule="rule1").build("trees")

    def assemble(self, mode: str, plan_id: Optional[str] = None, digest: Optional[str] = None) -> "subprocess.CompletedProcess":
        """``python3 scripts/assemble-report.py MODE --run-dir run --plan ID --plan-digest HEX``."""
        return self.run_entry(ASSEMBLE_ENTRY, mode, "--run-dir", "run", "--plan", plan_id or self.world.ids[mode],
                              "--plan-digest", digest or self.world.digest[mode])

    def report_stage(self) -> None:
        """The ``report`` stage's plan, batch inputs and parts, as the planner leaves them once ``trees`` has exited 0."""
        self.world.build_report()


@pytest.mark.parametrize("earlier", (False, True), ids=("first-run", "over-earlier-output"))
def test_assemble_report_trees_and_report_write_only_under_the_run_directory(tmp_path: Path, earlier: bool):
    """``trees`` copies and merges the trees under ``attack-trees/``, and ``report`` writes ``threat-report.md``. Each writes its stage record.

    Nothing else under ``--run-dir`` changes: the plans, the batch inputs, the parts, the agents' tree files and ``threats.md`` are read, and the
    baseline is read and never written. Over an earlier run, a tree and the report that an agent wrote are replaced, and each changes instead of
    appearing. ``$TMPDIR`` stays as it was.
    """
    project = AssembleProject(tmp_path)
    world = project.world
    trees = {world.tree_path(finding_id).relative_to(project.cwd).as_posix() for finding_id in world.tree_ids}
    replaced = sorted(trees)[0]
    if earlier:
        (project.cwd / replaced).parent.mkdir(parents=True, exist_ok=True)
        (project.cwd / replaced).write_bytes(EARLIER_TREE)
        (project.out / "threat-report.md").write_bytes(EARLIER_REPORT)
    start = project.state()

    first = project.assemble("trees")
    assert first.returncode == 0, _describe(first)
    after_trees = project.state()
    added, changed, removed = project.assert_writes_only_under_out(start, after_trees, "after trees")
    outputs = trees | {"run/attack-trees/.manifest.json", "run/.tachi-build/trees/%s/stage-record.json" % world.ids["trees"]}
    assert _files_among(after_trees[0], added) | changed == outputs and not removed, (sorted(added), sorted(changed), sorted(removed))
    assert changed == ({replaced} if earlier else set()), changed
    assert _under(after_trees[0], "baseline") == _under(start[0], "baseline"), "the baseline is read, never written"

    project.report_stage()
    staged = project.state()
    second = project.assemble("report")
    assert second.returncode == 0, _describe(second)
    end = project.state()
    added, changed, removed = project.assert_writes_only_under_out(staged, end, "after report")
    outputs = {"run/threat-report.md", "run/.tachi-build/report/%s/stage-record.json" % world.ids["report"]}
    assert _files_among(end[0], added) | changed == outputs and not removed, (sorted(added), sorted(changed), sorted(removed))
    assert changed == ({"run/threat-report.md"} if earlier else set()), changed
    assert (project.out / "threat-report.md").read_bytes() != EARLIER_REPORT

    project.assert_writes_only_under_out(start, end, "over the whole run")
    assert _under(end[0], "baseline") == _under(start[0], "baseline"), "the baseline is read, never written"
    project.assert_no_bytecode()


@pytest.mark.parametrize("case", ("trees-digest-mismatch", "report-no-plan"))
def test_assemble_report_refuses_without_writing(tmp_path: Path, case: str):
    """A ``trees`` plan digest that differs exits 2, and a ``report`` stage with no plan exits 1. Neither writes anything."""
    project = AssembleProject(tmp_path)
    mode, code = ("trees", 2) if case == "trees-digest-mismatch" else ("report", 1)
    before = project.state()

    refused = project.assemble(mode, plan_id=project.world.ids[mode], digest="0" * 64)
    assert refused.returncode == code, _describe(refused)
    assert "TACHI %s FAILED" % mode.upper() in refused.stderr, _describe(refused)
    assert project.state() == before, "a refused run must write nothing"
    project.assert_no_bytecode()


class SarifProject(StageProject):
    """A ``StageProject`` that also installs ``generate-threats-sarif.py``, which reads the fixture's ``threats.md`` and ``architecture.md``."""

    def __init__(self, root: Path):
        super().__init__(root)
        _install_with_closure(SARIF_ENTRY, self.cwd / "scripts")

    def generate(self, *args: str) -> "subprocess.CompletedProcess":
        """``python3 scripts/generate-threats-sarif.py ARGS``: Step 2.10, which passes the command's own architecture path."""
        return self.run_entry(SARIF_ENTRY, *args)


SARIF_ARGS = ("--threats", "run/threats.md", "--out", "out", "--architecture", "run/architecture.md")


@pytest.mark.parametrize("earlier", (False, True), ids=("first-run", "over-earlier-output"))
def test_generate_threats_sarif_writes_only_under_out(tmp_path: Path, earlier: bool):
    """The generator writes ``threats.sarif`` under ``--out`` and nothing else, and leaves its inputs and the scripts as they were.

    Over an earlier file it changes instead of appearing. It keeps no plan directory and no record, so that one file is the whole write set.
    """
    project = SarifProject(tmp_path)
    if earlier:
        (project.out / "threats.sarif").write_bytes(EARLIER_SARIF)
    start = project.state()

    generated = project.generate(*SARIF_ARGS)
    assert generated.returncode == 0, _describe(generated)
    end = project.state()
    added, changed, removed = project.assert_writes_only_under_out(start, end, "after generate")
    assert _files_among(end[0], added) == (set() if earlier else {"out/threats.sarif"}), sorted(added)
    assert changed == ({"out/threats.sarif"} if earlier else set()) and not removed, (changed, removed)
    printed = json.loads(generated.stdout)
    assert printed["output"] == "threats.sarif" and printed["results"] > 0, _describe(generated)
    if earlier:
        assert (project.out / "threats.sarif").read_bytes() != EARLIER_SARIF
    project.assert_no_bytecode()


@pytest.mark.parametrize("case", ("no-threats-file", "no-out-directory"))
def test_generate_threats_sarif_refuses_without_writing(tmp_path: Path, case: str):
    """A ``--threats`` file that isn't there and an ``--out`` that is no directory are both exit 1, and write nothing."""
    project = SarifProject(tmp_path)
    argv = (("--threats", "run/missing.md", "--out", "out") if case == "no-threats-file"
            else ("--threats", "run/threats.md", "--out", "no-such-dir"))
    before = project.state()

    refused = project.generate(*argv)
    assert refused.returncode == 1, _describe(refused)
    assert "TACHI THREATS-SARIF FAILED" in refused.stderr, _describe(refused)
    assert project.state() == before, "a refused run must write nothing"
    project.assert_no_bytecode()


# =============================================================================
# Static assertion (T015) and AR-1 case 4: the recipes never name a bad write target
# =============================================================================

# The three documents T015 names, plus the two skill references AR-1 case 4 adds, plus the three commands whose
# fences run F-374's scripts (ADR-050 D16): /tachi.risk-score and /tachi.threat-model (W2), and
# /tachi.compensating-controls (W3). Each wave that adds a command to the batched pipeline adds it here.
RECIPE_DOCS = (
    ".claude/agents/tachi/report-assembler.md",
    ".claude/agents/tachi/threat-infographic.md",
    ".claude/commands/tachi.infographic.md",
    ".claude/skills/tachi-infographics/references/gemini-prompt-construction.md",
    ".claude/skills/tachi-report-assembly/references/typst-artifacts.md",
    ".claude/commands/tachi.risk-score.md",
    ".claude/commands/tachi.threat-model.md",
    ".claude/commands/tachi.compensating-controls.md",
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
