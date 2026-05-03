"""Pytest configuration and shared fixtures for the tachi test suite.

Why the imports are non-standard
--------------------------------
The Python scripts under ``scripts/`` use hyphenated filenames
(e.g. ``extract-infographic-data.py``, ``extract-report-data.py``). Python's
normal ``import`` statement cannot load modules whose file names contain
hyphens — hyphens are not valid in Python identifiers. Renaming these scripts
is not an option because they are invoked by name from slash commands, CI
pipelines, and user documentation across the tachi ecosystem.

To expose them to the test suite, we load each script at runtime via the
``importlib.util`` API: ``spec_from_file_location`` builds a module spec from
the absolute file path, ``module_from_spec`` instantiates a module object, and
``spec.loader.exec_module`` executes the file in that module's namespace. All
three steps are required — skipping any one of them leaves the module in a
partially-initialized state where top-level definitions are not bound.

These loaders are exposed as session-scoped pytest fixtures so the scripts are
only parsed and executed once per test run, regardless of how many tests
consume them.
"""

import importlib.util
from pathlib import Path

import pytest


# Repository root resolved from this file's location:
# tests/conftest.py -> parents[1] == repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"


def _load_hyphenated_script(module_name: str, script_filename: str):
    """Load a hyphenated-name Python script from the scripts/ directory.

    Args:
        module_name: Underscored name to register the module under
            (e.g. ``"extract_infographic_data"``).
        script_filename: Basename of the script file on disk
            (e.g. ``"extract-infographic-data.py"``).

    Returns:
        The fully-initialized module object with all top-level names bound.

    Raises:
        FileNotFoundError: If the script file does not exist.
        ImportError: If ``spec_from_file_location`` fails to build a spec.
    """
    script_path = SCRIPTS_DIR / script_filename
    if not script_path.exists():
        raise FileNotFoundError(
            f"Cannot load {module_name}: script not found at {script_path}"
        )

    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise ImportError(
            f"Failed to build importlib spec for {script_path}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def extract_infographic_data():
    """Session-scoped fixture loading ``scripts/extract-infographic-data.py``.

    Returns the module object so tests can access its public functions
    (e.g. ``extract_infographic_data._compute_trust_zones(...)``).
    """
    return _load_hyphenated_script(
        module_name="extract_infographic_data",
        script_filename="extract-infographic-data.py",
    )


@pytest.fixture(scope="session")
def extract_report_data():
    """Session-scoped fixture loading ``scripts/extract-report-data.py``.

    Returns the module object so tests can access its public functions.
    """
    return _load_hyphenated_script(
        module_name="extract_report_data",
        script_filename="extract-report-data.py",
    )
