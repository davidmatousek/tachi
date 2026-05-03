"""Unit tests for the mmdc preflight gate and mid-render failure aggregator
in ``scripts/extract-report-data.py::render_mermaid_to_png()``.

The function is loaded via the session-scoped ``extract_report_data`` fixture
defined in ``tests/conftest.py`` (importlib shim for hyphenated filename).
"""

from unittest.mock import patch

import pytest


@pytest.fixture
def render_dirs(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    template = tmp_path / "template"
    template.mkdir()
    return target, template


def _sample_attack_trees():
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


# Preflight gate


def test_preflight_raises_when_mmdc_missing(extract_report_data, render_dirs):
    target_dir, template_dir = render_dirs
    attack_trees = _sample_attack_trees()

    with patch.object(extract_report_data.shutil, "which", return_value=None):
        with pytest.raises(RuntimeError) as exc_info:
            extract_report_data.render_mermaid_to_png(
                attack_trees, target_dir, template_dir
            )

    message = str(exc_info.value)
    assert "@mermaid-js/mermaid-cli" in message
    assert "npm install -g @mermaid-js/mermaid-cli" in message
    assert "Attack path rendering" in message


def test_preflight_skipped_when_attack_trees_empty(extract_report_data, render_dirs):
    target_dir, template_dir = render_dirs

    with patch.object(
        extract_report_data.shutil, "which", return_value=None
    ) as mock_which:
        extract_report_data.render_mermaid_to_png([], target_dir, template_dir)

    assert mock_which.call_count == 0


def test_preflight_error_distinct_from_midrender(extract_report_data, render_dirs):
    target_dir, template_dir = render_dirs
    attack_trees = _sample_attack_trees()

    with patch.object(extract_report_data.shutil, "which", return_value=None):
        with pytest.raises(RuntimeError) as exc_info:
            extract_report_data.render_mermaid_to_png(
                attack_trees, target_dir, template_dir
            )

    assert "Attack path rendering failed for" not in str(exc_info.value)


# Mid-render aggregator


def _render_single_mock_factory(results):
    iterator = iter(results)

    def _mock(entry, tmp_path):
        success, value = next(iterator)
        return (entry, success, value)

    return _mock


def _make_error_record(
    fid: str,
    failure_class: str = "exit:1",
    stderr: "bytes | str" = b"mmdc error output",
):
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


def test_midrender_aggregator_raises_on_any_failure(extract_report_data, render_dirs):
    target_dir, template_dir = render_dirs
    attack_trees = _sample_attack_trees()

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


def test_midrender_aggregator_message_format(extract_report_data, render_dirs):
    target_dir, template_dir = render_dirs
    attack_trees = _sample_attack_trees()

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


def test_midrender_all_success_no_exception(extract_report_data, render_dirs):
    target_dir, template_dir = render_dirs
    attack_trees = _sample_attack_trees()

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


def test_midrender_all_failure_raises_with_full_list(extract_report_data, render_dirs):
    target_dir, template_dir = render_dirs
    attack_trees = _sample_attack_trees()

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


def test_midrender_error_distinct_from_preflight(extract_report_data, render_dirs):
    target_dir, template_dir = render_dirs
    attack_trees = _sample_attack_trees()

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

    assert "npm install -g @mermaid-js/mermaid-cli" not in str(exc_info.value)
