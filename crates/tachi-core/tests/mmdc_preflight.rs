use tachi_core::facade::{
    ensure_attack_path_renderer_available, format_attack_path_render_failure_summary,
    MermaidRenderFailure, MMDC_INSTALL_HINT,
};

#[test]
fn preflight_skips_renderer_lookup_when_no_attack_trees_exist() {
    assert!(ensure_attack_path_renderer_available(0, false).is_ok());
}

#[test]
fn preflight_errors_when_renderer_is_missing_for_attack_trees() {
    let error =
        ensure_attack_path_renderer_available(2, false).expect_err("expected preflight error");
    println!("preflight_error={error}");

    assert!(error.contains("@mermaid-js/mermaid-cli"));
    assert!(error.contains("npm install -g @mermaid-js/mermaid-cli"));
    assert!(error.contains("Attack path rendering"));
}

#[test]
fn preflight_message_is_the_canonical_install_hint() {
    assert_eq!(
        MMDC_INSTALL_HINT,
        "Attack path rendering requires @mermaid-js/mermaid-cli (mmdc).\nInstall with: npm install -g @mermaid-js/mermaid-cli\nThen re-run /tachi.security-report."
    );
}

#[test]
fn render_failure_summary_includes_all_failure_records() {
    let summary = format_attack_path_render_failure_summary(&[
        MermaidRenderFailure {
            id: String::from("F-001"),
            file_path: String::from("attack-trees/f-001.mmd"),
            failure_class: String::from("exit:1"),
            stderr_excerpt: String::from("Parse error on line 1"),
        },
        MermaidRenderFailure {
            id: String::from("F-002"),
            file_path: String::from("attack-trees/f-002.mmd"),
            failure_class: String::from("timeout"),
            stderr_excerpt: String::from("renderer hung"),
        },
    ]);

    assert!(summary.contains("Attack path rendering failed for 2 findings:"));
    assert!(summary.contains("F-001 (attack-trees/f-001.mmd)"));
    assert!(summary.contains("failure: exit:1"));
    assert!(summary.contains("stderr: Parse error on line 1"));
    assert!(summary.contains("F-002 (attack-trees/f-002.mmd)"));
    assert!(summary.contains("failure: timeout"));
    assert!(summary.contains("stderr: renderer hung"));
}

#[test]
fn render_failure_summary_is_distinct_from_preflight_hint() {
    let summary = format_attack_path_render_failure_summary(&[MermaidRenderFailure {
        id: String::from("F-001"),
        file_path: String::from("attack-trees/f-001.mmd"),
        failure_class: String::from("exit:1"),
        stderr_excerpt: String::from("Parse error"),
    }]);

    assert!(!summary.contains(MMDC_INSTALL_HINT));
    assert!(summary.contains("Attack path rendering failed for 1 findings:"));
}
