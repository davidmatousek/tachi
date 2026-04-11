"""Unit tests for Feature 130 — mmdc preflight gate and mid-render loud failure.

These tests cover ``scripts/extract-report-data.py::render_mermaid_to_png()``.
The function is loaded via the session-scoped ``extract_report_data`` fixture
defined in ``tests/conftest.py`` (importlib shim for hyphenated filename).

Two test groups:
1. Preflight gate (T004) — ``shutil.which("mmdc")`` returns None → RuntimeError
2. Mid-render aggregator (T009) — mmdc present but ``_render_single`` reports
   one or more failures → RuntimeError with per-finding detail

Canonical error message tokens (FR-130.1):
- ``@mermaid-js/mermaid-cli``
- ``npm install -g @mermaid-js/mermaid-cli``
- ``Attack path rendering``

Mid-render aggregator message prefix (R6):
- ``Attack path rendering failed for`` (distinct from preflight message)
"""

from pathlib import Path
from unittest.mock import patch

import pytest


# =============================================================================
# Preflight gate (T004) — Architect refinements R5, R7
# =============================================================================


def _sample_attack_trees():
    """Return a non-empty attack_trees list with minimum required fields."""
    return [
        {
            "id": "F-001",
            "mermaid_code": "flowchart TD\n    A[Attacker] --> B[System]\n",
        },
        {
            "id": "F-002",
            "mermaid_code": "flowchart TD\n    X[External] --> Y[Service]\n",
        },
    ]


def test_preflight_raises_when_mmdc_missing(extract_report_data, tmp_path):
    """Preflight gate raises RuntimeError when shutil.which returns None.

    Asserts the canonical error message contains all three tokens:
    @mermaid-js/mermaid-cli, the install command, and "Attack path rendering".
    """
    attack_trees = _sample_attack_trees()
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    template_dir = tmp_path / "template"
    template_dir.mkdir()

    with patch.object(extract_report_data.shutil, "which", return_value=None):
        with pytest.raises(RuntimeError) as exc_info:
            extract_report_data.render_mermaid_to_png(
                attack_trees, target_dir, template_dir
            )

    message = str(exc_info.value)
    assert "@mermaid-js/mermaid-cli" in message
    assert "npm install -g @mermaid-js/mermaid-cli" in message
    assert "Attack path rendering" in message


def test_preflight_skipped_when_attack_trees_empty(extract_report_data, tmp_path):
    """Empty attack_trees list bypasses preflight entirely.

    Asserts (a) no exception raised, (b) shutil.which is not called because the
    empty-list early return fires before the preflight check.
    """
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    template_dir = tmp_path / "template"
    template_dir.mkdir()

    with patch.object(
        extract_report_data.shutil, "which", return_value=None
    ) as mock_which:
        extract_report_data.render_mermaid_to_png([], target_dir, template_dir)

    assert mock_which.call_count == 0


def test_preflight_skipped_when_only_low_medium_findings(
    extract_report_data, tmp_path
):
    """Proxy for Low/Medium-only filtering.

    Filtering to Critical/High happens in the caller, so the function receives
    an empty list when all findings are Low/Medium. This test uses an empty
    list as the proxy — same behavior as the empty-list early return above.
    """
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    template_dir = tmp_path / "template"
    template_dir.mkdir()

    with patch.object(
        extract_report_data.shutil, "which", return_value=None
    ) as mock_which:
        extract_report_data.render_mermaid_to_png([], target_dir, template_dir)

    assert mock_which.call_count == 0


def test_preflight_error_distinct_from_midrender(extract_report_data, tmp_path):
    """Preflight RuntimeError does not contain the mid-render aggregator prefix.

    FR-130.4 produces a distinct RuntimeError message shape starting with
    "Attack path rendering failed for N findings:". The preflight message must
    not be confused with it. This guarantees stderr readers can distinguish
    "mmdc missing" from "mmdc present but render failed".
    """
    attack_trees = _sample_attack_trees()
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    template_dir = tmp_path / "template"
    template_dir.mkdir()

    with patch.object(extract_report_data.shutil, "which", return_value=None):
        with pytest.raises(RuntimeError) as exc_info:
            extract_report_data.render_mermaid_to_png(
                attack_trees, target_dir, template_dir
            )

    message = str(exc_info.value)
    assert "Attack path rendering failed for" not in message


# =============================================================================
# Mid-render aggregator (T009) — Architect refinements R5, R6, R7
# =============================================================================


def _render_single_mock_factory(results):
    """Build a _render_single replacement that yields canned per-entry results.

    Each call pops the next (success, failure_class_or_dest) tuple from
    ``results`` and returns a (entry, success, value) triple matching the
    production function's return signature.
    """
    iterator = iter(results)

    def _mock(entry, tmp_path):
        success, value = next(iterator)
        return (entry, success, value)

    return _mock


def _make_error_record(
    fid: str, failure_class: str = "exit:1", stderr: str = b"mmdc error output"
):
    """Build a structured failure record matching the T010 return shape."""
    if isinstance(stderr, bytes):
        stderr_excerpt = stderr[:200].decode("utf-8", errors="replace")
    else:
        stderr_excerpt = stderr[:200]
    return {
        "id": fid,
        "file_path": f"attack-trees/{fid.lower()}.mmd",
        "failure_class": failure_class,
        "stderr_excerpt": stderr_excerpt,
    }


def test_midrender_aggregator_raises_on_any_failure(extract_report_data, tmp_path):
    """A single failure among successes triggers RuntimeError.

    With mmdc present, ``_render_single`` yields one failure and one success;
    the aggregator must raise RuntimeError rather than silently marking
    has_image=False on the failing entry.
    """
    attack_trees = _sample_attack_trees()
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    template_dir = tmp_path / "template"
    template_dir.mkdir()

    canned = [
        (True, "target/attack-trees/f-001-attack-tree.png"),
        (False, _make_error_record("F-002")),
    ]

    with patch.object(extract_report_data.shutil, "which", return_value="/fake/mmdc"):
        with patch.object(
            extract_report_data,
            "_render_single",
            side_effect=_render_single_mock_factory(canned),
        ):
            with pytest.raises(RuntimeError):
                extract_report_data.render_mermaid_to_png(
                    attack_trees, target_dir, template_dir
                )


def test_midrender_aggregator_message_format(extract_report_data, tmp_path):
    """Aggregator RuntimeError message matches R6 format specification.

    Required content:
    - Summary line ``Attack path rendering failed for N findings:``
    - The failed finding ID
    - The failed file path
    - A failure class token (``exit``, ``timeout``, or ``signal``)
    - At least one byte of stderr excerpt
    """
    attack_trees = _sample_attack_trees()
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    template_dir = tmp_path / "template"
    template_dir.mkdir()

    canned = [
        (True, "target/attack-trees/f-001-attack-tree.png"),
        (
            False,
            _make_error_record(
                "F-002", failure_class="exit:2", stderr=b"Parse error on line 5"
            ),
        ),
    ]

    with patch.object(extract_report_data.shutil, "which", return_value="/fake/mmdc"):
        with patch.object(
            extract_report_data,
            "_render_single",
            side_effect=_render_single_mock_factory(canned),
        ):
            with pytest.raises(RuntimeError) as exc_info:
                extract_report_data.render_mermaid_to_png(
                    attack_trees, target_dir, template_dir
                )

    message = str(exc_info.value)
    assert "Attack path rendering failed for" in message
    assert "F-002" in message
    assert "attack-trees/f-002.mmd" in message
    assert "exit" in message
    assert "Parse error" in message


def test_midrender_all_success_no_exception(extract_report_data, tmp_path):
    """When every render succeeds, the function returns normally.

    Verifies happy-path byte identity: no exception, and every entry gets
    has_image=True and a valid image_path.
    """
    attack_trees = _sample_attack_trees()
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    template_dir = tmp_path / "template"
    template_dir.mkdir()

    canned = [
        (True, "target/attack-trees/f-001-attack-tree.png"),
        (True, "target/attack-trees/f-002-attack-tree.png"),
    ]

    with patch.object(extract_report_data.shutil, "which", return_value="/fake/mmdc"):
        with patch.object(
            extract_report_data,
            "_render_single",
            side_effect=_render_single_mock_factory(canned),
        ):
            extract_report_data.render_mermaid_to_png(
                attack_trees, target_dir, template_dir
            )

    for entry in attack_trees:
        assert entry["has_image"] is True
        assert entry["image_path"] != ""


def test_midrender_all_failure_raises_with_full_list(extract_report_data, tmp_path):
    """When every render fails, the RuntimeError lists every finding ID."""
    attack_trees = _sample_attack_trees()
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    template_dir = tmp_path / "template"
    template_dir.mkdir()

    canned = [
        (False, _make_error_record("F-001", failure_class="timeout", stderr=b"hung")),
        (False, _make_error_record("F-002", failure_class="exit:1", stderr=b"bad")),
    ]

    with patch.object(extract_report_data.shutil, "which", return_value="/fake/mmdc"):
        with patch.object(
            extract_report_data,
            "_render_single",
            side_effect=_render_single_mock_factory(canned),
        ):
            with pytest.raises(RuntimeError) as exc_info:
                extract_report_data.render_mermaid_to_png(
                    attack_trees, target_dir, template_dir
                )

    message = str(exc_info.value)
    assert "F-001" in message
    assert "F-002" in message


def test_midrender_error_distinct_from_preflight(extract_report_data, tmp_path):
    """Mid-render RuntimeError does not contain the preflight install command.

    FR-130.1 produces a distinct RuntimeError shape containing
    ``npm install -g @mermaid-js/mermaid-cli``. The mid-render aggregator's
    message must not duplicate that tokens so stderr readers can distinguish
    the two failure modes.
    """
    attack_trees = _sample_attack_trees()
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    template_dir = tmp_path / "template"
    template_dir.mkdir()

    canned = [
        (False, _make_error_record("F-001", failure_class="exit:1", stderr=b"err")),
        (False, _make_error_record("F-002", failure_class="exit:1", stderr=b"err")),
    ]

    with patch.object(extract_report_data.shutil, "which", return_value="/fake/mmdc"):
        with patch.object(
            extract_report_data,
            "_render_single",
            side_effect=_render_single_mock_factory(canned),
        ):
            with pytest.raises(RuntimeError) as exc_info:
                extract_report_data.render_mermaid_to_png(
                    attack_trees, target_dir, template_dir
                )

    message = str(exc_info.value)
    assert "npm install -g @mermaid-js/mermaid-cli" not in message
