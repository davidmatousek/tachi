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
fn active_devops_docs_treat_fastapi_pack_guidance_as_archived_reference_only() {
    let root = workspace_root();

    let docs = [
        ".claude/rules/design-context-loader.md",
        "README.md",
        "docs/devops/README.md",
        "docs/devops/01_Local/README.md",
        "docs/devops/CI_CD_GUIDE.md",
        "docs/devops/environment-variables.md",
    ];

    for doc in docs {
        let content =
            fs::read_to_string(root.join(doc)).unwrap_or_else(|err| panic!("read {doc}: {err}"));
        assert!(
            content.contains("Archived legacy guidance"),
            "active devops doc {doc} should explicitly mark FastAPI pack guidance as archived"
        );
        assert!(
            !content.contains("fastapi-react"),
            "active devops doc {doc} should not instruct adopting fastapi-react"
        );
        assert!(
            !content.contains("fastapi-react-local"),
            "active devops doc {doc} should not instruct adopting fastapi-react-local"
        );
        if doc == "README.md" {
            assert!(
                !content.contains("retained only while compatibility tests are being retired"),
                "root README should not describe retired Python packaging as still retained"
            );
        }
    }
}

#[test]
fn security_readiness_doc_avoids_concrete_fastapi_scaffold_paths() {
    let root = workspace_root();
    let content = fs::read_to_string(root.join("docs/security/OPEN_SOURCE_READINESS.md"))
        .expect("read security readiness doc");

    assert!(
        content.contains("archived FastAPI scaffold guidance"),
        "security readiness doc should label the FastAPI scaffold note as archived"
    );
    assert!(
        !content.contains("stacks/fastapi-react-local/scaffold/backend/app/config.py"),
        "security readiness doc should not expose the concrete FastAPI scaffold config path"
    );
}

#[test]
fn archived_fastapi_consumer_guide_is_generic_about_the_old_pack_name() {
    let root = workspace_root();
    let content = fs::read_to_string(
        root.join("docs/guides/Archive/STACK_PACK_CONSUMER_GUIDE_FASTAPI_REACT.md"),
    )
    .expect("read archived consumer guide");

    assert!(
        content.contains("archived FastAPI stack"),
        "archived consumer guide should stay generic about the retired FastAPI stack"
    );
    assert!(
        !content.contains("fastapi-react-local"),
        "archived consumer guide should not name the retired fastapi-react-local pack"
    );
}
