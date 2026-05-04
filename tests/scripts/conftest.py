"""Shared fixtures and path constants for the BLP-01 detection-agent test suites.

Consumed by the detection-agent schema-contract layers (F-1 output_integrity,
F-2 misinformation, F-4 human_trust_exploitation), which all need the same
`finding.id.pattern` regex compiled once per module, plus the F-241 web/API
attestation suites that walk agent and skill catalogs for citation evidence.

Path constants exposed at module scope:
- ``REPO_ROOT`` / ``SCHEMA_PATH`` / ``TAXONOMY_DIR`` — original BLP-01 set
- ``AGENTS_DIR`` / ``SKILLS_DIR`` — F-241 detection-agent catalog roots

Helper functions exposed at module scope:
- ``load_yaml_or_empty(path)`` — yaml.safe_load with None-coalescing to []
- ``monkeypatch_framework_record_counts(monkeypatch, raw, in_scope)`` — stub
  the post-F-241 dual-helper monkeypatch surface used by zero-denominator
  tests across test_coverage_attestation*, test_coverage_percentage_*

Module-scoped fixtures are intentional so each test file pays a single
YAML parse + regex compile cost regardless of test count, while still
leaving `pytest-xdist` workers isolated.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]

_THIS_DIR = str(Path(__file__).resolve().parent)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)
SCHEMA_PATH = REPO_ROOT / "schemas" / "finding.yaml"
TAXONOMY_DIR = REPO_ROOT / "schemas" / "taxonomy"
AGENTS_DIR = REPO_ROOT / ".claude" / "agents" / "tachi"
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"


def load_yaml_or_empty(path: Path) -> Any:
    """Load YAML and coalesce ``None`` (empty file) to ``[]``.

    Mirrors the loader pattern in scripts/extract-report-data.py:
    ``yaml.safe_load(open(path))`` with empty-file → empty-list semantics
    so callers can iterate the result without a None guard.
    """
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return [] if data is None else data


def monkeypatch_framework_record_counts(
    monkeypatch,
    extract_report_data,
    *,
    raw: dict,
    in_scope: dict,
) -> None:
    """Stub the F-241 dual-helper count surface used by zero-denominator tests.

    Replaces both ``load_framework_yaml_record_counts`` (raw) and
    ``load_framework_yaml_in_scope_record_counts`` (filtered) on the
    extract_report_data module. Tests pass dicts keyed on the framework
    names from ``extract_report_data.ORDERED_FRAMEWORKS``; values become
    the new counts the aggregator sees.
    """
    monkeypatch.setattr(
        extract_report_data,
        "load_framework_yaml_record_counts",
        lambda: dict(raw),
    )
    monkeypatch.setattr(
        extract_report_data,
        "load_framework_yaml_in_scope_record_counts",
        lambda: dict(in_scope),
    )


@pytest.fixture(scope="module")
def schema() -> dict:
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def id_pattern(schema: dict) -> re.Pattern:
    return re.compile(schema["finding"]["id"]["pattern"])


@pytest.fixture(scope="session")
def init_run(tmp_path_factory: pytest.TempPathFactory):
    """One canonical scripts/init.sh run, shared across all test_init_sh_* modules.

    Promoted from 4 duplicate module-scoped fixtures (substitution, constitution,
    self_delete) plus an inline function-scoped pattern in adversarial. The
    macos-latest CI runner is 3-4x slower than dev hardware on init.sh cold-
    cache scans (workflow comment in tachi-pytest.yml); each module-scoped
    fixture historically forced its own clone-and-init cycle, multiplying the
    cold-cache cost across modules.

    By promoting to session scope, the suite invokes init.sh once for all
    canonical post-init assertions. The function-scoped pattern in
    test_init_sh_adversarial.test_case_13 is preserved separately because
    that test SEEDS pre-init fixture files into the clone before init.sh
    runs — it cannot share the canonical clone.

    Sharing is safe because every consuming test asserts READ-ONLY properties
    of the post-init clone (file existence, byte content, mode bits). No
    consumer mutates state. The session-scoped tmpdir is cleaned up by
    pytest at session end.

    Returns an InitRun dataclass (returncode, stdout, stderr, tmpdir).
    """
    from init_sh_helpers import (
        build_canonical_stdin,
        clone_into_tmpdir,
        run_init_in_clone,
    )

    tmpdir = tmp_path_factory.mktemp("init_sh_canonical")
    clone_root = clone_into_tmpdir(tmpdir)
    stdin_payload = build_canonical_stdin(clone_root)
    result = run_init_in_clone(clone_root, stdin_payload)
    if result.returncode != 0:
        pytest.fail(
            f"canonical init.sh exited {result.returncode}; stderr tail:\n"
            f"{result.stderr[-1500:]}"
        )
    return result
