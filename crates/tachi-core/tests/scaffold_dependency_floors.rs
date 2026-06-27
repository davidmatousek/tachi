use serde_json::{json, Value};
use std::{fs, path::PathBuf};

#[test]
fn nextjs_supabase_scaffold_excludes_known_vulnerable_dependency_floors() {
    let manifest_path = workspace_root().join("stacks/nextjs-supabase/scaffold/package.json");
    let manifest = fs::read_to_string(&manifest_path).expect("read scaffold package.json");
    let package_json: Value = serde_json::from_str(&manifest).expect("parse scaffold package.json");

    let failures = [
        dependency_floor_failure(
            &package_json,
            "dependencies",
            "next",
            Version::new(16, 2, 6),
            &[
                "#1 GHSA-8h8q-6873-q5fj",
                "#2 GHSA-36qx-fr4f-26g5",
                "#3 GHSA-267c-6grr-h53f",
                "#4 GHSA-wfc6-r584-vfw7",
                "#5 GHSA-492v-c6pp-mqqv",
                "#6 GHSA-c4j6-fc7j-m34r",
                "#7 GHSA-h64f-5h5j-jqjh",
                "#8 GHSA-mg66-mrh9-m8jx",
                "#9 GHSA-gx5p-jg67-6x7h",
                "#10 GHSA-vfv6-92ff-j949",
                "#11 GHSA-ffhc-5mcf-pf4q",
                "#12 GHSA-3g8h-86w9-wvmq",
                "#13 GHSA-26hh-7cqf-hhc6",
            ],
        ),
        dependency_floor_failure(
            &package_json,
            "devDependencies",
            "vitest",
            Version::new(4, 1, 0),
            &["#14 GHSA-5xrq-8626-4rwp"],
        ),
    ]
    .into_iter()
    .flatten()
    .collect::<Vec<_>>();

    assert!(
        failures.is_empty(),
        "scaffold dependency floors admit known vulnerable versions:\n{}",
        failures.join("\n")
    );
}

#[test]
fn publish_gate_runs_scaffold_dependency_floor_audit() {
    let makefile_path = workspace_root().join("Makefile");
    let makefile = fs::read_to_string(&makefile_path).expect("read Makefile");

    assert!(
        makefile.contains("scaffold-dependency-gate:"),
        "Makefile must expose a scaffold-dependency-gate target for offline Dependabot floor auditing"
    );
    assert!(
        makefile.contains("cargo test -p tachi-core --test scaffold_dependency_floors"),
        "scaffold-dependency-gate must run the focused Rust dependency floor audit"
    );
    assert!(
        makefile.contains("@$(MAKE) scaffold-dependency-gate"),
        "publish-gate must run scaffold-dependency-gate as a release blocker"
    );
}

#[test]
fn publish_gate_targets_the_active_desktop_host() {
    let makefile_path = workspace_root().join("Makefile");
    let makefile = fs::read_to_string(&makefile_path).expect("read Makefile");

    assert!(
        makefile.contains("cargo test -p tachi-desktop --all-targets"),
        "release-gate must validate the active GTK-free desktop host"
    );
    assert!(
        !makefile.contains("cargo test -p tachi-tauri"),
        "release-gate must not target the retired tachi-tauri package"
    );
}

#[test]
fn glib_dependabot_alert_is_absent_from_workspace_lockfile() {
    let lockfile_path = workspace_root().join("Cargo.lock");
    let lockfile = fs::read_to_string(&lockfile_path).expect("read Cargo.lock");

    assert!(
        !lockfile.contains("name = \"tauri\""),
        "Cargo.lock must no longer retain the Tauri desktop stack in the GTK-free workspace"
    );
    assert!(
        !lockfile.contains("name = \"gtk\""),
        "Cargo.lock must no longer retain gtk in the GTK-free workspace"
    );
    assert!(
        !lockfile.contains("name = \"glib\"\nversion = \"0.18.5\""),
        "Cargo.lock must not resolve the vulnerable glib 0.18.5 line after the desktop host migration"
    );
}

#[test]
fn dependency_floor_audit_reports_synthetic_vulnerable_ranges() {
    let package_json = json!({
        "dependencies": {
            "next": ">=16.2.3"
        },
        "devDependencies": {
            "vitest": ">=4.0.0"
        }
    });

    let failures = [
        dependency_floor_failure(
            &package_json,
            "dependencies",
            "next",
            Version::new(16, 2, 6),
            &["#13 GHSA-26hh-7cqf-hhc6"],
        ),
        dependency_floor_failure(
            &package_json,
            "devDependencies",
            "vitest",
            Version::new(4, 1, 0),
            &["#14 GHSA-5xrq-8626-4rwp"],
        ),
    ]
    .into_iter()
    .flatten()
    .collect::<Vec<_>>();

    assert_eq!(failures.len(), 2);
    assert!(failures[0].contains("dependencies.next"));
    assert!(failures[0].contains("16.2.6"));
    assert!(failures[0].contains("#13 GHSA-26hh-7cqf-hhc6"));
    assert!(failures[1].contains("devDependencies.vitest"));
    assert!(failures[1].contains("4.1.0"));
    assert!(failures[1].contains("#14 GHSA-5xrq-8626-4rwp"));
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Version {
    major: u64,
    minor: u64,
    patch: u64,
}

impl Version {
    const fn new(major: u64, minor: u64, patch: u64) -> Self {
        Self {
            major,
            minor,
            patch,
        }
    }
}

fn dependency_floor_failure(
    package_json: &Value,
    section: &str,
    package: &str,
    patched_floor: Version,
    alert_ids: &[&str],
) -> Option<String> {
    let range = package_json
        .get(section)
        .and_then(|deps| deps.get(package))
        .and_then(Value::as_str)
        .unwrap_or_else(|| panic!("{section}.{package} must exist in scaffold package.json"));
    let floor = parse_range_floor(range).unwrap_or_else(|| {
        panic!(
            "{section}.{package} range {range:?} must expose a parseable version floor for alerts {}",
            alert_ids.join(", ")
        )
    });

    (floor < patched_floor).then(|| {
        format!(
            "- {section}.{package} range {range:?} admits vulnerable versions below {}.{}.{} for alerts {}",
            patched_floor.major,
            patched_floor.minor,
            patched_floor.patch,
            alert_ids.join(", ")
        )
    })
}

fn parse_range_floor(range: &str) -> Option<Version> {
    let normalized = range
        .trim()
        .trim_start_matches('^')
        .trim_start_matches('~')
        .trim_start_matches(">=")
        .trim_start_matches('=')
        .trim();
    let mut parts = normalized.split('.');
    Some(Version {
        major: parts.next()?.parse().ok()?,
        minor: parts.next()?.parse().ok()?,
        patch: parts.next()?.parse().ok()?,
    })
}

fn workspace_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(|path| path.parent())
        .expect("workspace root")
        .to_path_buf()
}
