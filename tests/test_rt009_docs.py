import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class RT009DocsTest(unittest.TestCase):
    def test_rt009_completion_is_marked_done_in_roadmap_pack(self) -> None:
        issue_pack = read("docs/roadmap/2026-06-04-rust-tauri-issue-pack.md")

        self.assertIn("Current completion: 9/9 issue cards, or 100%.", issue_pack)
        self.assertIn(
            "RT-009 is complete after the docs refresh and retirement pass.",
            issue_pack,
        )
        self.assertIn(
            "### RT-009 - Refresh docs and retire legacy compatibility paths",
            issue_pack,
        )
        self.assertIn(
            "Legacy compatibility paths are explicitly transitional or removed.",
            issue_pack,
        )

    def test_rt009_phase_five_is_marked_complete_in_roadmap(self) -> None:
        roadmap = read("docs/product/03_Product_Roadmap/2026-Rust-Tauri-roadmap.md")

        self.assertIn("## Phase 5 - Compatibility Retirement", roadmap)
        self.assertIn("| Compatibility retirement plan | Backlog | Done |", roadmap)
        self.assertIn("| Doc refresh for Rust/Tauri commands | Backlog | Done |", roadmap)
        self.assertIn("| Legacy-test deprecation map | Backlog | Done |", roadmap)

    def test_canonical_testing_guide_no_longer_positions_python_projects(self) -> None:
        testing_guide = read("docs/testing/README.md")

        self.assertIn("Run `make llvm-cov`", testing_guide)
        self.assertNotIn("**Python Projects**:", testing_guide)
        self.assertNotIn("pytest", testing_guide)

    def test_rust_tauri_only_roadmap_bundle_is_cross_linked(self) -> None:
        roadmap = read("docs/roadmap/2026-06-08-rust-tauri-only-roadmap.md")
        issue_cards = read("docs/roadmap/2026-06-08-rust-tauri-only-issue-cards.md")
        merge_plan = read("docs/roadmap/2026-06-08-rust-tauri-only-merge-plan.md")

        self.assertIn("rust-tauri-only-issue-cards.md", roadmap)
        self.assertIn("rust-tauri-only-merge-plan.md", roadmap)
        self.assertIn("RT-010 - Freeze the Python surface inventory", issue_cards)
        self.assertIn(
            "RT-015 - Optimize the Rust path for speed and reliability",
            issue_cards,
        )
        self.assertIn(
            "docs(roadmap): add rust-tauri-only migration roadmap",
            merge_plan,
        )
        self.assertIn(
            "test(docs): lock roadmap and issue-pack contract",
            merge_plan,
        )

    def test_rt009_changelog_entry_is_present(self) -> None:
        changelog = read("CHANGELOG.md")

        self.assertIn(
            "### Rust/Tauri doc refresh and compatibility retirement (RT-009)",
            changelog,
        )
        self.assertIn(
            "Refreshes the canonical docs and retires the remaining legacy compatibility guidance",
            changelog,
        )
