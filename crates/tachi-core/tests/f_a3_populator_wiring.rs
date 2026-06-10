use std::collections::BTreeSet;
use std::fs;
use std::path::{Path, PathBuf};

const F241_WIRED_HOSTS: &[&str] = &[
    "spoofing.md",
    "tampering.md",
    "info-disclosure.md",
    "privilege-escalation.md",
    "repudiation.md",
    "denial-of-service.md",
    "tool-abuse.md",
    "data-poisoning.md",
    "model-theft.md",
    "prompt-injection.md",
    "agent-autonomy.md",
];

const PRE_EXISTING_WIRED_HOSTS: &[&str] = &[
    "output-integrity.md",
    "misinformation.md",
    "human-trust-exploitation.md",
];

const LINE_CAP: usize = 200;

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn agents_dir(root: &Path) -> PathBuf {
    root.join(".claude/agents/tachi")
}

fn read_agent(root: &Path, filename: &str) -> String {
    let path = agents_dir(root).join(filename);
    fs::read_to_string(&path)
        .unwrap_or_else(|err| panic!("expected agent file {} to load: {err}", path.display()))
}

fn all_detection_hosts() -> BTreeSet<&'static str> {
    F241_WIRED_HOSTS
        .iter()
        .chain(PRE_EXISTING_WIRED_HOSTS.iter())
        .copied()
        .collect()
}

fn source_attribution_agent_files(root: &Path) -> BTreeSet<String> {
    fs::read_dir(agents_dir(root))
        .expect("read tachi agent directory")
        .map(|entry| entry.expect("read agent entry").path())
        .filter(|path| path.extension().and_then(|ext| ext.to_str()) == Some("md"))
        .filter(|path| {
            fs::read_to_string(path)
                .expect("read agent")
                .contains("source_attribution")
        })
        .map(|path| {
            path.file_name()
                .and_then(|name| name.to_str())
                .expect("agent filename should be UTF-8")
                .to_string()
        })
        .collect()
}

fn step5_mentions_source_attribution(text: &str) -> bool {
    let mut in_step5 = false;
    for line in text.lines() {
        let trimmed = line.trim_start();
        if trimmed.starts_with("6.") {
            break;
        }
        if trimmed.starts_with("5.") {
            in_step5 = true;
        }
        if in_step5 && trimmed.contains("source_attribution") {
            return true;
        }
    }
    false
}

#[test]
fn f_a3_populator_wiring_contract_is_rust_native() {
    let root = workspace_root();
    assert!(
        !root
            .join("tests/scripts/test_f_a3_populator_wiring.py")
            .exists(),
        "F-A3 populator wiring coverage should live in Rust tests, not pytest"
    );

    let expected = all_detection_hosts()
        .into_iter()
        .map(ToOwned::to_owned)
        .collect::<BTreeSet<_>>();
    assert_eq!(source_attribution_agent_files(&root), expected);

    for host in F241_WIRED_HOSTS {
        let text = read_agent(&root, host);
        assert!(text.contains("source_attribution:"), "{host} missing block");
        assert!(
            text.contains("relationship: primary"),
            "{host} missing primary relationship"
        );
        assert!(
            text.contains("relationship: related"),
            "{host} missing related relationship"
        );
        assert!(
            text.lines().count() <= LINE_CAP,
            "{host} exceeds {LINE_CAP}-line cap"
        );
        assert!(
            step5_mentions_source_attribution(&text),
            "{host} Step 5 should mention source_attribution"
        );
        assert!(text.contains("ADR-037 D-3"), "{host} missing ADR lineage");
    }
}
