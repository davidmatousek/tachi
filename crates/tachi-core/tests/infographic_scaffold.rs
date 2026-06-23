use std::fs;
use std::path::PathBuf;

use pretty_assertions::assert_eq;

struct FakeTemplateStore<'a> {
    template: &'a str,
    content: &'a str,
}

impl<'a> tachi_core::infographic::PromptScaffoldStore for FakeTemplateStore<'a> {
    fn load_template(&self, template_name: &str) -> Option<String> {
        (template_name == self.template).then(|| self.content.to_string())
    }
}

#[test]
fn extract_prompt_scaffold_reads_template_prompt_segments() {
    let repo_root = unique_temp_dir();
    let template_dir = repo_root.join("templates/tachi/infographics");
    fs::create_dir_all(&template_dir).expect("create template dir");

    let template_path = template_dir.join("infographic-maestro-stack.md");
    fs::write(
        &template_path,
        r#"# Maestro Stack

## Gemini Prompt

```text
Prompt intro
DATA CONTENT (render this as visible text):
Visible data
FOOTER
Prompt outro
```
"#,
    )
    .expect("write template");

    let scaffold = tachi_core::infographic::extract_prompt_scaffold(
        "maestro-stack",
        Some(repo_root.as_path()),
    );

    assert_eq!(scaffold.found, true);
    assert_eq!(
        scaffold.preamble,
        "Prompt intro\nDATA CONTENT (render this as visible text):\n"
    );
    assert_eq!(scaffold.postamble, "FOOTER\nPrompt outro");
}

#[test]
fn extract_prompt_scaffold_uses_injected_store_without_repo_root() {
    let store = FakeTemplateStore {
        template: "maestro-stack",
        content: r#"# Maestro Stack

## Gemini Prompt

```text
Prompt intro
DATA CONTENT (render this as visible text):
Visible data
FOOTER
Prompt outro
```
"#,
    };

    let scaffold =
        tachi_core::infographic::extract_prompt_scaffold_from_store("maestro-stack", &store);

    assert_eq!(scaffold.found, true);
    assert_eq!(
        scaffold.preamble,
        "Prompt intro\nDATA CONTENT (render this as visible text):\n"
    );
    assert_eq!(scaffold.postamble, "FOOTER\nPrompt outro");
}

fn unique_temp_dir() -> PathBuf {
    let mut path = std::env::temp_dir();
    path.push(format!(
        "tachi-rust-infographic-scaffold-{}-{}",
        std::process::id(),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .expect("clock")
            .as_nanos()
    ));
    path
}
