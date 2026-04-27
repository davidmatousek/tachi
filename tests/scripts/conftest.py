"""Shared fixtures and path constants for the BLP-01 detection-agent test suites.

Consumed by the F-1 (`test_output_integrity.py`), F-2 (`test_misinformation.py`),
and F-4 (`test_human_trust_exploitation.py`) schema-contract layers, which all
need the same `finding.id.pattern` regex compiled once per module. The fixtures
are module-scoped so each test file pays a single YAML parse + regex compile
cost regardless of test count, while still leaving `pytest-xdist` workers
isolated.

Forward-compatible with F-5 (LLM10 — pending) and any future detection-agent
test file: import `REPO_ROOT` / `SCHEMA_PATH` / `TAXONOMY_DIR` and consume
the `schema` / `id_pattern` fixtures by name.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "finding.yaml"
TAXONOMY_DIR = REPO_ROOT / "schemas" / "taxonomy"


@pytest.fixture(scope="module")
def schema() -> dict:
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def id_pattern(schema: dict) -> re.Pattern:
    return re.compile(schema["finding"]["id"]["pattern"])
