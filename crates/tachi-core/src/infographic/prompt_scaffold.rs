use std::fs;
use std::path::{Path, PathBuf};

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct PromptScaffold {
    pub preamble: String,
    pub postamble: String,
    pub found: bool,
}

pub trait PromptScaffoldStore {
    fn load_template(&self, template_name: &str) -> Option<String>;
}

const SCAFFOLD_TEMPLATES: [&str; 5] = [
    "baseball-card",
    "risk-funnel",
    "system-architecture",
    "maestro-stack",
    "maestro-heatmap",
];

const TEMPLATE_FILES: [(&str, &str); 5] = [
    ("baseball-card", "infographic-baseball-card.md"),
    ("risk-funnel", "infographic-risk-funnel.md"),
    ("system-architecture", "infographic-system-architecture.md"),
    ("maestro-stack", "infographic-maestro-stack.md"),
    ("maestro-heatmap", "infographic-maestro-heatmap.md"),
];

struct FilesystemPromptScaffoldStore {
    repo_root: PathBuf,
}

impl PromptScaffoldStore for FilesystemPromptScaffoldStore {
    fn load_template(&self, template_name: &str) -> Option<String> {
        let template_file = TEMPLATE_FILES
            .iter()
            .find(|(name, _)| *name == template_name)
            .map(|(_, file)| *file)?;

        let template_path = self
            .repo_root
            .join("templates")
            .join("tachi")
            .join("infographics")
            .join(template_file);
        fs::read_to_string(template_path).ok()
    }
}

pub fn extract_prompt_scaffold(template_name: &str, repo_root: Option<&Path>) -> PromptScaffold {
    let repo_root =
        repo_root.unwrap_or_else(|| Path::new(env!("CARGO_MANIFEST_DIR")).parent().unwrap());
    let store = FilesystemPromptScaffoldStore {
        repo_root: repo_root.to_path_buf(),
    };
    extract_prompt_scaffold_from_store(template_name, &store)
}

pub fn extract_prompt_scaffold_from_store(
    template_name: &str,
    store: &dyn PromptScaffoldStore,
) -> PromptScaffold {
    if !SCAFFOLD_TEMPLATES.contains(&template_name) {
        return PromptScaffold::default();
    }

    let Some(content) = store.load_template(template_name) else {
        return PromptScaffold::default();
    };

    let mut in_prompt_section = false;
    let mut in_fence = false;
    let mut fence_lines = Vec::new();
    let mut prompt_text = None;

    for line in content.lines() {
        let stripped = line.trim();
        if !in_prompt_section
            && stripped.starts_with("##")
            && stripped.contains("Gemini")
            && stripped.contains("Prompt")
        {
            in_prompt_section = true;
            continue;
        }

        if in_prompt_section && !in_fence && stripped.starts_with("```") {
            in_fence = true;
            continue;
        }

        if in_fence && stripped.starts_with("```") {
            prompt_text = Some(fence_lines.join("\n"));
            break;
        }

        if in_fence {
            fence_lines.push(line.to_string());
        }
    }

    let Some(prompt_text) = prompt_text else {
        return PromptScaffold::default();
    };

    let marker = "DATA CONTENT (render this";
    let Some(marker_idx) = prompt_text.find(marker) else {
        return PromptScaffold::default();
    };

    let marker_line_end = prompt_text[marker_idx..]
        .find('\n')
        .map(|offset| marker_idx + offset)
        .unwrap_or(prompt_text.len());

    let preamble = format!("{}\n", prompt_text[..marker_line_end].trim_end());

    let footer_idx = prompt_text
        .find("\nFOOTER")
        .or_else(|| prompt_text.find("FOOTER"))
        .unwrap_or(prompt_text.len());
    let postamble = prompt_text[footer_idx..].trim().to_string();

    PromptScaffold {
        preamble,
        postamble,
        found: true,
    }
}

#[cfg(test)]
mod tests {
    use super::{extract_prompt_scaffold, extract_prompt_scaffold_from_store, PromptScaffoldStore};
    use std::fs;
    use std::path::PathBuf;
    use std::sync::atomic::{AtomicU64, Ordering};

    struct FakeTemplateStore<'a> {
        template: &'a str,
        content: &'a str,
    }

    impl<'a> PromptScaffoldStore for FakeTemplateStore<'a> {
        fn load_template(&self, template_name: &str) -> Option<String> {
            (template_name == self.template).then(|| self.content.to_string())
        }
    }

    struct DirTemplateStore {
        repo_root: PathBuf,
    }

    impl PromptScaffoldStore for DirTemplateStore {
        fn load_template(&self, template_name: &str) -> Option<String> {
            let template_file = match template_name {
                "maestro-stack" => "infographic-maestro-stack.md",
                _ => return None,
            };

            fs::read_to_string(
                self.repo_root
                    .join("templates")
                    .join("tachi")
                    .join("infographics")
                    .join(template_file),
            )
            .ok()
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

        let scaffold = extract_prompt_scaffold("maestro-stack", Some(repo_root.as_path()));

        assert!(scaffold.found);
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

        let scaffold = extract_prompt_scaffold_from_store("maestro-stack", &store);

        assert!(scaffold.found);
        assert_eq!(
            scaffold.preamble,
            "Prompt intro\nDATA CONTENT (render this as visible text):\n"
        );
        assert_eq!(scaffold.postamble, "FOOTER\nPrompt outro");
    }

    #[test]
    fn extract_prompt_scaffold_from_store_matches_filesystem_adapter() {
        let repo_root = unique_temp_dir();
        let template_dir = repo_root.join("templates/tachi/infographics");
        fs::create_dir_all(&template_dir).expect("create template dir");

        fs::write(
            template_dir.join("infographic-maestro-stack.md"),
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

        let filesystem = extract_prompt_scaffold("maestro-stack", Some(repo_root.as_path()));
        let injected = extract_prompt_scaffold_from_store(
            "maestro-stack",
            &DirTemplateStore {
                repo_root: repo_root.clone(),
            },
        );

        assert_eq!(filesystem, injected);
    }

    fn unique_temp_dir() -> PathBuf {
        static UNIQUE: AtomicU64 = AtomicU64::new(0);
        let mut path = std::env::temp_dir();
        path.push(format!(
            "tachi-rust-infographic-scaffold-{}-{}",
            std::process::id(),
            UNIQUE.fetch_add(1, Ordering::Relaxed)
        ));
        path
    }
}
