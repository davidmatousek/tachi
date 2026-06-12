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
fn fastapi_stack_packs_are_archived_legacy_reference_only() {
    let root = workspace_root();

    let stacks_readme =
        fs::read_to_string(root.join("stacks/README.md")).expect("stacks README exists");
    let tech_stack = fs::read_to_string(root.join("docs/architecture/00_Tech_Stack/README.md"))
        .expect("tech stack README exists");

    for pack in ["fastapi-react", "fastapi-react-local"] {
        let stack_doc = fs::read_to_string(root.join(format!("stacks/{pack}/STACK.md")))
            .expect("stack doc exists");
        let conventions =
            fs::read_to_string(root.join(format!("stacks/{pack}/rules/conventions.md")))
                .expect("stack conventions exist");

        assert!(
            stack_doc.contains("Archived legacy pack; retained for historical reference only."),
            "{pack} STACK.md should clearly mark the pack as archived"
        );
        assert!(
            conventions.contains("archived legacy pack; retained for historical reference only"),
            "{pack} conventions should clearly mark the pack as archived"
        );
    }

    let active_section = stacks_readme
        .split("## Active Packs")
        .nth(1)
        .and_then(|section| section.split("## ").next())
        .expect("active packs section");
    assert!(
        !active_section.contains("fastapi-react"),
        "active stack pack index should not list fastapi-react as active"
    );
    assert!(
        !active_section.contains("fastapi-react-local"),
        "active stack pack index should not list fastapi-react-local as active"
    );
    assert!(stacks_readme.contains("## Archived Legacy Packs"));
    assert!(stacks_readme.contains("fastapi-react"));
    assert!(stacks_readme.contains("fastapi-react-local"));

    assert!(tech_stack.contains("| `stacks/fastapi-react/` | Archived |"));
    assert!(tech_stack.contains("| `stacks/fastapi-react-local/` | Archived |"));
}
