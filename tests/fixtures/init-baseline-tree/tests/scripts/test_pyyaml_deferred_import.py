"""Enforce the stdlib-only module-load invariant on tachi pipeline scripts.

The tachi pipeline must remain importable in stdlib-only environments (no
PyYAML installed) so the public-facing CLI scaffolding does not fail at
``import scripts.extract_report_data`` time. Production scripts that need
``yaml.safe_load`` therefore defer the ``import yaml`` statement into the
function body that actually parses YAML — when no YAML-parsing code path
fires, PyYAML is never loaded.

This test parses every Python source file under ``scripts/`` with
``ast.parse``, walks every ``ast.Import`` / ``ast.ImportFrom`` node that
names ``yaml`` (or ``yaml.<sub>``), and asserts that every such node has at
least one ancestor that is an ``ast.FunctionDef`` or ``ast.AsyncFunctionDef``.
A module-level ``import yaml`` fails with a precise ``file:line`` message.

Reference: KB-037 stdlib-only module-load invariant.

Test design notes:
- Auto-discovery globs ``scripts/*.py`` and retains only files whose source
  mentions ``yaml`` so the test stays correct as new yaml-using scripts are
  added.
- A negative-control test parses synthetic source containing a top-level
  ``import yaml`` and asserts the helper correctly flags it.
- Parent ancestry (not lexical scope) is checked so ``import yaml`` inside a
  class body is treated as module-level — class bodies execute at import time
  exactly like module-level code.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable

import pytest

from .conftest import REPO_ROOT


SCRIPTS_DIR = REPO_ROOT / "scripts"


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def _build_parent_map(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    """Return a child→parent map covering every node in ``tree``.

    ``ast`` does not natively expose parent pointers; we build the mapping
    once per module via ``ast.walk`` + ``ast.iter_child_nodes``. The module
    root maps to itself implicitly (it has no parent and never appears as a
    key).
    """
    parent_map: dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parent_map[child] = parent
    return parent_map


def _is_inside_function(
    node: ast.AST, parent_map: dict[ast.AST, ast.AST]
) -> bool:
    """Return True iff ``node`` has any ``FunctionDef`` / ``AsyncFunctionDef`` ancestor.

    Walks up via ``parent_map`` until the chain terminates. Class-body
    ancestors do NOT count — class bodies execute at import time exactly
    like module-level code, so a yaml import nested inside a class body
    still violates the invariant.
    """
    current = parent_map.get(node)
    while current is not None:
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return True
        current = parent_map.get(current)
    return False


def _node_imports_yaml(node: ast.AST) -> bool:
    """Return True iff the import node touches the ``yaml`` package.

    Catches both forms:
      - ``import yaml`` / ``import yaml as y`` / ``import yaml.parser``
      - ``from yaml import safe_load`` / ``from yaml.parser import …``
    """
    if isinstance(node, ast.Import):
        return any(
            alias.name == "yaml" or alias.name.startswith("yaml.")
            for alias in node.names
        )
    if isinstance(node, ast.ImportFrom):
        module = node.module or ""
        return module == "yaml" or module.startswith("yaml.")
    return False


def _yaml_import_nodes(tree: ast.AST) -> Iterable[ast.AST]:
    """Yield every Import / ImportFrom node that touches ``yaml``."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)) and _node_imports_yaml(node):
            yield node


# ---------------------------------------------------------------------------
# Pipeline-script discovery
# ---------------------------------------------------------------------------


_SOURCE_CACHE: dict[Path, str] = {}


def _discover_pipeline_scripts() -> list[Path]:
    """Return every ``scripts/*.py`` file whose source text references ``yaml``.

    Filtering on textual ``yaml`` mention keeps the test surface tight: a
    script that never touches YAML cannot violate the invariant, so we
    drop it from parametrization. Reading the source as text (rather than
    parsing) is fast and good enough — the ast-walk runs only on retained
    files. Future scripts that add YAML usage are picked up automatically.

    Side effect: populates ``_SOURCE_CACHE`` with the source text of every
    discovered file so the downstream parametrized test can ``ast.parse``
    without re-reading from disk.
    """
    selected: list[Path] = []
    for path in sorted(SCRIPTS_DIR.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        if "yaml" in source:
            _SOURCE_CACHE[path] = source
            selected.append(path)
    return selected


PIPELINE_SCRIPTS = _discover_pipeline_scripts()


# ---------------------------------------------------------------------------
# Sanity: discovery actually found something
# ---------------------------------------------------------------------------


def test_discovery_finds_at_least_one_pipeline_script() -> None:
    """Guard against silent regressions where the discovery glob returns nothing.

    If ``scripts/`` is moved or renamed, the parametrized test below would
    silently degrade to zero parametrizations and report PASS — masking the
    invariant entirely. This sanity check fails loudly in that case.
    """
    assert PIPELINE_SCRIPTS, (
        f"Discovery found zero yaml-referencing scripts under {SCRIPTS_DIR}. "
        "If scripts/ moved, update SCRIPTS_DIR; otherwise this is a regression "
        "in the discovery glob."
    )


def test_known_yaml_consumer_is_in_scope() -> None:
    """Anchor: extract-report-data.py is the canonical yaml consumer.

    The deferred-import discipline is preserved here by importing yaml
    inside ``_load_framework_yaml_records``. If discovery ever drops this
    file from the in-scope list, the invariant becomes untested for the
    very file that proved the pattern. Fail loudly in that case.
    """
    expected = SCRIPTS_DIR / "extract-report-data.py"
    assert expected in PIPELINE_SCRIPTS, (
        f"{expected} dropped out of pipeline-script discovery — the "
        f"deferred-import discipline test must keep watching it."
    )


# ---------------------------------------------------------------------------
# Core invariant
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "script_path",
    PIPELINE_SCRIPTS,
    ids=[p.name for p in PIPELINE_SCRIPTS],
)
def test_yaml_import_is_function_scoped(script_path: Path) -> None:
    """Every ``import yaml`` / ``from yaml import …`` MUST live inside a function body.

    Per KB-037 + F-241 FR-014 (preserved by Wave 4.3 task T046), tachi
    pipeline scripts must remain importable without PyYAML installed. A
    module-level ``import yaml`` would break that invariant and fail
    ``python -c 'import scripts.extract_report_data'`` in stdlib-only CI.
    """
    source = _SOURCE_CACHE.get(script_path) or script_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(script_path))
    parent_map = _build_parent_map(tree)

    violations: list[str] = []
    for node in _yaml_import_nodes(tree):
        if not _is_inside_function(node, parent_map):
            # Render the offending source line for the failure message.
            offending_line = source.splitlines()[node.lineno - 1].strip()
            violations.append(
                f"{script_path.name}:{node.lineno} — `{offending_line}`"
            )

    assert not violations, (
        "Module-level yaml import(s) detected — KB-037 stdlib-only module-load "
        "invariant violated. Per F-241 T046 / FR-014, yaml MUST be imported "
        "inside the function body that uses it (e.g. `def _load_framework_yaml_records(): "
        "import yaml; ...`). Offending sites:\n  "
        + "\n  ".join(violations)
    )


# ---------------------------------------------------------------------------
# Negative control: prove the helper actually catches violations
# ---------------------------------------------------------------------------


def test_helper_detects_module_level_yaml_import() -> None:
    """Synthetic AST with module-level ``import yaml`` MUST be flagged.

    Without this check, a bug in ``_is_inside_function`` (e.g. always
    returning True) would silently neutralize the entire test suite.
    """
    synthetic = "import yaml\n\ndef parse():\n    return yaml.safe_load('')\n"
    tree = ast.parse(synthetic)
    parent_map = _build_parent_map(tree)

    yaml_imports = list(_yaml_import_nodes(tree))
    assert len(yaml_imports) == 1, (
        f"Expected exactly 1 yaml import node in synthetic source; got "
        f"{len(yaml_imports)}."
    )

    module_level_import = yaml_imports[0]
    assert not _is_inside_function(module_level_import, parent_map), (
        "_is_inside_function returned True for a module-level `import yaml`; "
        "the helper is broken and the parametrized test above is no longer "
        "trustworthy."
    )


def test_helper_accepts_function_scoped_yaml_import() -> None:
    """Synthetic AST with function-scoped ``import yaml`` MUST be accepted.

    Companion to ``test_helper_detects_module_level_yaml_import``: ensures
    the helper does not over-reject (false positive) on the legitimate
    deferred-import pattern that T046 preserves.
    """
    synthetic = (
        "def _load():\n"
        "    import yaml\n"
        "    return yaml.safe_load('')\n"
    )
    tree = ast.parse(synthetic)
    parent_map = _build_parent_map(tree)

    yaml_imports = list(_yaml_import_nodes(tree))
    assert len(yaml_imports) == 1

    deferred_import = yaml_imports[0]
    assert _is_inside_function(deferred_import, parent_map), (
        "_is_inside_function returned False for a function-scoped `import yaml`; "
        "the helper would reject the very pattern T046 preserves."
    )


def test_helper_rejects_class_body_yaml_import() -> None:
    """Class-body imports execute at import time and MUST be flagged as module-level.

    A class body is not a function body — Python evaluates it during the
    enclosing module's import. So `class Foo: import yaml` would still
    require PyYAML to be installed at module-load time, violating the
    invariant just like a top-level import.
    """
    synthetic = "class Foo:\n    import yaml\n"
    tree = ast.parse(synthetic)
    parent_map = _build_parent_map(tree)

    yaml_imports = list(_yaml_import_nodes(tree))
    assert len(yaml_imports) == 1

    class_body_import = yaml_imports[0]
    assert not _is_inside_function(class_body_import, parent_map), (
        "_is_inside_function returned True for a class-body `import yaml`; "
        "class bodies execute at import time and must be treated as "
        "module-level for the stdlib-only invariant."
    )


def test_helper_detects_from_yaml_import_form() -> None:
    """The helper MUST also flag ``from yaml import safe_load`` at module level.

    ``from yaml import …`` is parsed as ``ast.ImportFrom`` (not ``ast.Import``)
    so the form-detection branch needs separate coverage.
    """
    synthetic = "from yaml import safe_load\n"
    tree = ast.parse(synthetic)
    parent_map = _build_parent_map(tree)

    yaml_imports = list(_yaml_import_nodes(tree))
    assert len(yaml_imports) == 1, (
        "Expected the `from yaml import safe_load` form to be detected by "
        "_node_imports_yaml; got zero matches."
    )
    assert not _is_inside_function(yaml_imports[0], parent_map)
