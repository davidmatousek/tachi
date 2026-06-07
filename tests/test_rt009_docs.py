from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_rt009_issue_pack_is_marked_complete():
    issue_pack = read("docs/roadmap/2026-06-04-rust-tauri-issue-pack.md")

    assert "Current completion: 9/9 issue cards" in issue_pack
    assert "### RT-009 - Refresh docs and retire legacy compatibility paths" in issue_pack
    assert "**Status**: Done" in issue_pack
    assert "Legacy compatibility paths are explicitly transitional or removed." in issue_pack
    assert "Python" not in issue_pack
    assert "pytest" not in issue_pack


def test_rt009_roadmap_phase_5_is_complete():
    roadmap = read("docs/product/03_Product_Roadmap/2026-Rust-Tauri-roadmap.md")

    assert "## Phase 5 - Compatibility Retirement" in roadmap
    assert "| Compatibility retirement plan | Backlog | Done |" in roadmap
    assert "| Doc refresh for Rust/Tauri commands | Backlog | Done |" in roadmap
    assert "| Legacy-test deprecation map | Backlog | Done |" in roadmap
    assert "Canonical docs now point at Rust/Tauri commands instead of stale legacy instructions" in roadmap
    assert "Any remaining transitional surface is explicitly marked transitional or removed." in roadmap
    assert "Python" not in roadmap
    assert "pytest" not in roadmap


def test_rt009_changelog_mentions_doc_refresh_and_retirement():
    changelog = read("CHANGELOG.md")
    rt009_block = changelog.split(
        "### Rust/Tauri doc refresh and compatibility retirement (RT-009)",
        1,
    )[1].split("\n### ", 1)[0]

    assert "Rust/Tauri doc refresh and compatibility retirement (RT-009)" in changelog
    assert "Refreshes the canonical docs and retires the remaining legacy compatibility guidance" in rt009_block
    assert "Python" not in rt009_block
    assert "pytest" not in rt009_block


def test_rt009_readme_points_at_rust_native_tests():
    readme = read("README.md")

    assert "cargo test" in readme
    assert "Rust-backed coverage audit" in readme
    assert "pytest" not in readme
    assert "Python script tests" not in readme


def test_rt009_testing_guide_points_at_rust_tooling():
    testing = read("docs/testing/README.md")

    assert "Rust Projects" in testing
    assert "cargo test" in testing
    assert "Rust-backed audit binary" in testing
    assert "Python" not in testing
    assert "pytest" not in testing
