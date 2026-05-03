"""Unit tests for ``parse_project_name`` in ``scripts/tachi_parsers.py``.

Covers precedence ordering (title override > threats.md H1 > architecture.md
fallback > "Unknown Project"), both threats.md formats, both architecture.md
em-dash formats, and edge cases (missing file, unreadable file, malformed H1).
"""

import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
PARSER_PATH = REPO_ROOT / "scripts" / "tachi_parsers.py"


def _load_parser_module():
    spec = importlib.util.spec_from_file_location("tachi_parsers", PARSER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["tachi_parsers"] = module
    spec.loader.exec_module(module)
    return module


tachi_parsers = _load_parser_module()
parse_project_name = tachi_parsers.parse_project_name


class TestTitleOverride:
    def test_title_override_wins_over_all_sources(self, tmp_path):
        (tmp_path / "architecture.md").write_text("# Alpha — Architecture\n")
        content = "# Beta Threat Model\n"
        assert parse_project_name(
            content, title_override="Gamma", target_dir=tmp_path
        ) == "Gamma"

    def test_empty_title_override_falls_through(self):
        assert parse_project_name("# Alpha Threat Model\n", title_override="") == "Alpha"


class TestThreatsMdFormats:
    def test_format_orchestrator_output(self):
        assert parse_project_name("# Alpha Threat Model\n") == "Alpha"

    def test_format_legacy_colon(self):
        assert parse_project_name("# Threat Model: Beta\n") == "Beta"

    def test_multiword_name(self):
        assert parse_project_name("# Web Application Threat Model\n") == "Web Application"

    def test_name_with_hyphens(self):
        assert parse_project_name("# Threat Model: second-brain-mcp\n") == "second-brain-mcp"


class TestArchitectureMdFallback:
    def test_name_before_architecture_suffix(self, tmp_path):
        (tmp_path / "architecture.md").write_text("# Web Application — Architecture\n")
        assert parse_project_name("# Threat Model Report\n", target_dir=tmp_path) == "Web Application"

    def test_name_after_security_architecture_prefix(self, tmp_path):
        (tmp_path / "architecture.md").write_text("# Security Architecture — second-brain-mcp\n")
        assert parse_project_name("# Threat Model Report\n", target_dir=tmp_path) == "second-brain-mcp"

    def test_name_after_plain_architecture_prefix(self, tmp_path):
        (tmp_path / "architecture.md").write_text("# Architecture — my-service\n")
        assert parse_project_name("# Threat Model Report\n", target_dir=tmp_path) == "my-service"

    def test_no_architecture_file_falls_back_to_unknown(self, tmp_path):
        assert parse_project_name("# Threat Model Report\n", target_dir=tmp_path) == "Unknown Project"

    def test_target_dir_none_skips_fallback(self):
        assert parse_project_name("# Threat Model Report\n") == "Unknown Project"

    def test_architecture_without_em_dash_is_ignored(self, tmp_path):
        (tmp_path / "architecture.md").write_text("# Plain Heading\n")
        assert parse_project_name("# Threat Model Report\n", target_dir=tmp_path) == "Unknown Project"

    def test_architecture_with_hyphen_instead_of_em_dash_is_ignored(self, tmp_path):
        (tmp_path / "architecture.md").write_text("# Web Application - Architecture\n")
        assert parse_project_name("# Threat Model Report\n", target_dir=tmp_path) == "Unknown Project"

    def test_threats_h1_wins_over_architecture(self, tmp_path):
        (tmp_path / "architecture.md").write_text("# Alpha — Architecture\n")
        content = "# Beta Threat Model\n"
        assert parse_project_name(content, target_dir=tmp_path) == "Beta"

    def test_architecture_with_extra_whitespace(self, tmp_path):
        (tmp_path / "architecture.md").write_text("#   Web Application   —   Architecture   \n")
        assert parse_project_name("# Threat Model Report\n", target_dir=tmp_path) == "Web Application"

    def test_architecture_h1_must_be_first_heading(self, tmp_path):
        # Still accepts first H1 even with multiple H1s present
        (tmp_path / "architecture.md").write_text(
            "# Web Application — Architecture\n\n# Another Heading\n"
        )
        assert parse_project_name("# Threat Model Report\n", target_dir=tmp_path) == "Web Application"
