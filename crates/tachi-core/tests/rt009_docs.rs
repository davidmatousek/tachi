use std::fs;
use std::path::{Path, PathBuf};

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

#[test]
fn rt009_documentation_contract_is_rust_native() {
    let root = workspace_root();

    assert!(
        !root.join("tests/test_rt009_docs.py").exists(),
        "RT-009 documentation coverage should live in Rust tests, not pytest"
    );

    let issue_pack = fs::read_to_string(root.join("docs/roadmap/2026-06-04-rust-tauri-issue-pack.md"))
        .expect("legacy issue pack exists");
    assert!(issue_pack.contains("Current completion: 9/9 issue cards, or 100%."));
    assert!(issue_pack.contains("RT-009 is complete after the docs refresh and retirement pass."));
    assert!(issue_pack.contains("### RT-009 - Refresh docs and retire legacy compatibility paths"));
    assert!(issue_pack.contains("Legacy compatibility paths are explicitly transitional or removed."));

    let product_roadmap = fs::read_to_string(
        root.join("docs/product/03_Product_Roadmap/2026-Rust-Tauri-roadmap.md"),
    )
    .expect("product roadmap exists");
    assert!(product_roadmap.contains("## Phase 5 - Compatibility Retirement"));
    assert!(product_roadmap.contains("| Compatibility retirement plan | Backlog | Done |"));
    assert!(product_roadmap.contains("| Doc refresh for Rust/Tauri commands | Backlog | Done |"));
    assert!(product_roadmap.contains("| Legacy-test deprecation map | Backlog | Done |"));

    let testing_guide =
        fs::read_to_string(root.join("docs/testing/README.md")).expect("testing guide exists");
    assert!(testing_guide.contains("Run `make llvm-cov`"));
    assert!(!testing_guide.contains("**Python Projects**:"));
    assert!(!testing_guide.contains("pytest"));

    let roadmap =
        fs::read_to_string(root.join("docs/roadmap/2026-06-08-rust-tauri-only-roadmap.md"))
            .expect("rust tauri roadmap exists");
    let issue_cards =
        fs::read_to_string(root.join("docs/roadmap/2026-06-08-rust-tauri-only-issue-cards.md"))
            .expect("rust tauri issue cards exist");
    let merge_plan =
        fs::read_to_string(root.join("docs/roadmap/2026-06-08-rust-tauri-only-merge-plan.md"))
            .expect("rust tauri merge plan exists");

    assert!(roadmap.contains("rust-tauri-only-issue-cards.md"));
    assert!(roadmap.contains("rust-tauri-only-merge-plan.md"));
    assert!(roadmap.contains("Current roadmap completion: 17% (1 of 6 cards complete)."));
    assert!(roadmap.contains("| RT-010 | Complete |"));
    assert!(roadmap.contains("| RT-011 | In progress |"));
    assert!(roadmap.contains("| RT-012 | In progress |"));
    assert!(roadmap.contains("| RT-013 | Pending |"));
    assert!(roadmap.contains("| RT-014 | Pending |"));
    assert!(roadmap.contains("| RT-015 | Pending |"));
    assert!(issue_cards.contains("RT-010 - Freeze the Python surface inventory"));
    assert!(issue_cards.contains("RT-015 - Optimize the Rust path for speed and reliability"));
    assert!(issue_cards.contains("Current roadmap completion: 17% (1 of 6 cards complete)."));
    assert!(issue_cards.contains("| RT-010 | Complete |"));
    assert!(issue_cards.contains("| RT-011 | In progress |"));
    assert!(issue_cards.contains("| RT-012 | In progress |"));
    assert!(issue_cards.contains("| RT-013 | Pending |"));
    assert!(issue_cards.contains("| RT-014 | Pending |"));
    assert!(issue_cards.contains("| RT-015 | Pending |"));
    assert!(merge_plan.contains("docs(roadmap): add rust-tauri-only migration roadmap"));
    assert!(merge_plan.contains("test(docs): lock roadmap and issue-pack contract"));

    let changelog = fs::read_to_string(root.join("CHANGELOG.md")).expect("changelog exists");
    assert!(changelog.contains("### Rust/Tauri roadmap status refresh"));
    assert!(changelog.contains("### Rust/Tauri doc refresh and compatibility retirement (RT-009)"));
    assert!(changelog.contains(
        "Refreshes the canonical docs and retires the remaining legacy compatibility guidance"
    ));
}
