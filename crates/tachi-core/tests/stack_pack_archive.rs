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

#[test]
fn fastapi_pack_agent_supplements_and_defaults_are_archived_legacy_reference_only() {
    let root = workspace_root();

    for pack in ["fastapi-react", "fastapi-react-local"] {
        let defaults = fs::read_to_string(root.join(format!("stacks/{pack}/defaults.env")))
            .expect("defaults env exists");
        assert!(
            defaults.contains("Archived legacy pack; retained for historical reference only."),
            "{pack} defaults.env should clearly mark the pack as archived"
        );
        assert!(
            defaults.contains("TECH_STACK=\"fastapi-react\"")
                || defaults.contains("TECH_STACK=\"fastapi-react-local\""),
            "{pack} defaults.env should keep the historical tech stack marker"
        );

        for agent in [
            "code-reviewer",
            "debugger",
            "devops",
            "frontend-developer",
            "security-analyst",
            "senior-backend-engineer",
            "tester",
            "ux-ui-designer",
        ] {
            let path = root.join(format!("stacks/{pack}/agents/{agent}.md"));
            let content = fs::read_to_string(&path).expect("agent supplement exists");
            assert!(
                content.contains("Archived legacy pack; retained for historical reference only."),
                "{pack} agent supplement {agent} should clearly mark the pack as archived"
            );
        }

        let extra_paths: &[&str] = match pack {
            "fastapi-react" => &[
                "rules/security.md",
                "rules/design-quality-tailwind.md",
                "scaffold/docker-compose.yml",
            ],
            "fastapi-react-local" => &["rules/security.md"],
            _ => unreachable!(),
        };

        for rel in extra_paths {
            let content = fs::read_to_string(root.join(format!("stacks/{pack}/{rel}")))
                .expect("extra pack file exists");
            assert!(
                content.contains("Archived legacy pack; retained for historical reference only."),
                "{pack} extra file {rel} should clearly mark the pack as archived"
            );
        }
    }
}
