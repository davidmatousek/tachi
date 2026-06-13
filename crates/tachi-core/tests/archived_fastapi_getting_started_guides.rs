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
fn active_getting_started_guides_treat_fastapi_local_as_archived_reference_only() {
    let root = workspace_root();

    let docs = [
        "docs/guides/AOD_KICKSTART.md",
        "docs/guides/GETTING_STARTED_PATH_B.md",
        "docs/guides/KICKSTART_GUIDE.md",
        "docs/guides/SMOKE_TEST.md",
    ];

    for doc in docs {
        let content =
            fs::read_to_string(root.join(doc)).unwrap_or_else(|err| panic!("read {doc}: {err}"));
        assert!(
            content.contains("Archived legacy guidance"),
            "active getting-started guide {doc} should explicitly mark FastAPI Local guidance as archived"
        );
        assert!(
            !content.contains("you might select `fastapi-react-local`"),
            "active getting-started guide {doc} should not present fastapi-react-local as a current stack choice"
        );
        assert!(
            !content.contains("| Tech Stack | `1` (fastapi-react-local) |"),
            "active getting-started guide {doc} should not present fastapi-react-local as an init prompt answer"
        );
        assert!(
            !content.contains("fastapi-react-local"),
            "active getting-started guide {doc} should not name the archived FastAPI Local pack"
        );
        assert!(
            !content.contains("ls backend/app/"),
            "active getting-started guide {doc} should not instruct inspecting the retired FastAPI backend app tree"
        );
    }
}
