use std::path::PathBuf;

use serde_json::Value;

use tachi_shell::commands::infographic_data_output;

const TEMPLATE_DIR: &str = "templates/tachi/infographics";
const THRETS_MD: &str = r#"
# Agentic AI Application

### Components

| Component | Type | MAESTRO Layer |
| --- | --- | --- |
| LLM Agent Orchestrator | Service | L2 — Foundation Model |
| MCP Tool Server | Service | L2 — Foundation Model |
| Guardrails Service | Service | L5 — Infrastructure Controls |

#### Risk by MAESTRO Layer

| MAESTRO Layer | Finding Count | Highest Severity |
| --- | --- | --- |
| L2 — Foundation Model | 2 | High |
| L5 — Infrastructure Controls | 1 | Critical |

## 7. Recommended Actions

| Finding ID | Component | MAESTRO Layer | Risk Level | Threat | Mitigation |
| --- | --- | --- | --- | --- | --- |
| S-1 | LLM Agent Orchestrator | L2 — Foundation Model | High | Prompt override risk | Harden instruction guards |
| A-1 | MCP Tool Server | L2 — Foundation Model | Medium | Tool abuse injection | Validate tool args |
| I-1 | Guardrails Service | L5 — Infrastructure Controls | Critical | Model output exfiltration | Enforce egress controls |

## 6. Risk Summary

| Risk Level | Count |
| --- | --- |
| Critical | 1 |
| High | 1 |
| Medium | 1 |
| Low | 0 |
| Note | 0 |
| Total | 3 |
"#;

#[test]
fn infographic_data_command_returns_maestro_stack_payload_json() {
    let root = setup_fixture_dir();
    let payload = infographic_data_output(&root, "maestro-stack").expect("payload generated");
    let value: Value = serde_json::from_str(&payload).expect("valid JSON");

    assert_eq!(value["template"], "maestro-stack");
    assert_eq!(value["template_data"]["has_maestro_data"], true);
    assert_eq!(
        value["template_data"]["most_exposed_layer"],
        "L2 — Data Operations"
    );
    assert_eq!(
        value["template_data"]["per_layer_summaries"][0]["layer_id"],
        "L2"
    );
}

fn setup_fixture_dir() -> PathBuf {
    let mut path = std::env::temp_dir();
    path.push(format!(
        "tachi-rust-infographic-cmd-{}-{}",
        std::process::id(),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));

    std::fs::create_dir_all(&path).expect("create fixture dir");
    std::fs::write(path.join("threats.md"), THRETS_MD).expect("write threats");

    let template_dir = path.join(TEMPLATE_DIR);
    std::fs::create_dir_all(&template_dir).expect("create template dir");
    std::fs::write(
        template_dir.join("infographic-maestro-stack.md"),
        r##"## Gemini Prompt
```text
DATA CONTENT (render this)
FOOTER
```"##,
    )
    .expect("write template");
    std::fs::write(
        template_dir.join("infographic-maestro-heatmap.md"),
        r##"## Gemini Prompt
```text
DATA CONTENT (render this)
FOOTER
```"##,
    )
    .expect("write template");

    path
}
