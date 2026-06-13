use std::fs;
use std::path::{Path, PathBuf};

#[test]
fn init_sh_declares_trace_hook_for_slow_init_workflow() {
    let init_script = workspace_root().join("scripts/init.sh");
    let init_source = fs::read_to_string(&init_script).expect("read scripts/init.sh");

    assert!(
        init_source.contains("AOD_INIT_TRACE"),
        "expected scripts/init.sh to gate trace output behind AOD_INIT_TRACE"
    );
    assert!(
        init_source.contains("aod_trace_init_phase"),
        "expected scripts/init.sh to define a trace helper for init phases"
    );
    assert!(
        init_source.contains("aod_trace_init_phase \"prerequisites\""),
        "expected scripts/init.sh to trace the prerequisites phase"
    );
    assert!(
        init_source.contains("aod_trace_init_phase \"stack-discovery\""),
        "expected scripts/init.sh to trace the stack-discovery phase"
    );
    assert!(
        init_source.contains("aod_trace_init_phase \"personalization\""),
        "expected scripts/init.sh to trace the personalization phase"
    );
    assert!(
        init_source.contains("aod_trace_init_phase \"substitution\""),
        "expected scripts/init.sh to trace the substitution phase"
    );
    assert!(
        init_source.contains("aod_trace_init_phase \"version-pin\""),
        "expected scripts/init.sh to trace the version-pin phase"
    );
    assert!(
        init_source.contains("aod_trace_init_phase \"precommit\""),
        "expected scripts/init.sh to trace the precommit phase"
    );
    assert!(
        cleanup_trace_precedes_self_delete(&init_source),
        "expected scripts/init.sh to trace cleanup before deleting itself"
    );
}

#[test]
fn init_sh_cleanup_trace_is_explicitly_before_self_delete() {
    let init_script = workspace_root().join("scripts/init.sh");
    let init_source = fs::read_to_string(&init_script).expect("read scripts/init.sh");

    assert!(
        cleanup_trace_precedes_self_delete(&init_source),
        "expected scripts/init.sh to trace cleanup before deleting itself"
    );
}

fn workspace_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .and_then(Path::parent)
        .expect("workspace root")
        .to_path_buf()
}

fn cleanup_trace_precedes_self_delete(init_source: &str) -> bool {
    match (
        init_source.find("aod_trace_init_phase \"cleanup\""),
        init_source.find("rm -f scripts/init.sh"),
    ) {
        (Some(cleanup), Some(delete)) => cleanup < delete,
        _ => false,
    }
}
