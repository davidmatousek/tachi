use std::fs;
use std::path::{Component, Path, PathBuf};

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ImageAssets {
    pub funnel_image_path: Option<String>,
    pub baseball_image_path: Option<String>,
    pub architecture_image_path: Option<String>,
    pub maestro_stack_image_path: Option<String>,
    pub maestro_heatmap_image_path: Option<String>,
    pub executive_architecture_image_path: Option<String>,
}

#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct BrandAssets {
    pub has_logo_primary: bool,
    pub has_logo_horizontal: bool,
    pub logo_primary_path: Option<String>,
    pub logo_primary_dark_path: Option<String>,
    pub logo_horizontal_path: Option<String>,
}

const IMAGE_STEMS: &[(&str, &str)] = &[
    ("funnel_image_path", "threat-risk-funnel"),
    ("baseball_image_path", "threat-baseball-card"),
    ("architecture_image_path", "threat-system-architecture"),
    ("maestro_stack_image_path", "threat-maestro-stack"),
    ("maestro_heatmap_image_path", "threat-maestro-heatmap"),
    (
        "executive_architecture_image_path",
        "threat-executive-architecture",
    ),
];

pub fn detect_images(target_dir: &Path, template_dir: &Path) -> ImageAssets {
    let rel_target = relative_path(template_dir, target_dir);
    let mut images = ImageAssets::default();

    for (field, stem) in IMAGE_STEMS {
        let chosen = choose_image(target_dir, stem);
        if let Some(path) = chosen {
            let rel_path = rel_target.join(path.file_name().unwrap_or_default());
            let value = rel_path.to_string_lossy().replace('\\', "/");
            match *field {
                "funnel_image_path" => images.funnel_image_path = Some(value),
                "baseball_image_path" => images.baseball_image_path = Some(value),
                "architecture_image_path" => images.architecture_image_path = Some(value),
                "maestro_stack_image_path" => images.maestro_stack_image_path = Some(value),
                "maestro_heatmap_image_path" => images.maestro_heatmap_image_path = Some(value),
                "executive_architecture_image_path" => {
                    images.executive_architecture_image_path = Some(value)
                }
                _ => {}
            }
        }
    }

    images
}

pub fn detect_brand_assets(template_dir: &Path, brand_dir: Option<&Path>) -> BrandAssets {
    let brand_dir = brand_dir.unwrap_or_else(|| Path::new("brand/final"));
    let rel_brand = relative_path(template_dir, brand_dir);
    let mut result = BrandAssets::default();

    let logo_files = [
        ("logo_primary_path", "tachi-logo-primary.png"),
        ("logo_primary_dark_path", "tachi-logo-primary-dark.png"),
        ("logo_horizontal_path", "tachi-logo-horizontal.png"),
    ];

    for (field, filename) in logo_files {
        let filepath = brand_dir.join(filename);
        if is_nonempty_file(&filepath) {
            let rel_path = rel_brand.join(filename);
            let value = rel_path.to_string_lossy().replace('\\', "/");
            match field {
                "logo_primary_path" => {
                    result.logo_primary_path = Some(value);
                    result.has_logo_primary = true;
                }
                "logo_primary_dark_path" => result.logo_primary_dark_path = Some(value),
                "logo_horizontal_path" => {
                    result.logo_horizontal_path = Some(value);
                    result.has_logo_horizontal = true;
                }
                _ => {}
            }
        }
    }

    result
}

fn choose_image(target_dir: &Path, stem: &str) -> Option<PathBuf> {
    let mut candidates = Vec::new();
    for ext in [".jpg", ".png"] {
        let path = target_dir.join(format!("{stem}{ext}"));
        if is_nonempty_file(&path) {
            candidates.push((ext, path));
        }
    }

    if candidates.is_empty() {
        return None;
    }

    for (ext, path) in &candidates {
        if image_extension_for_file(path.as_path()) == Some(*ext) {
            return Some(path.clone());
        }
    }

    for (_ext, path) in candidates {
        if let Some(fmt) = image_format(path.as_path()) {
            let corrected = target_dir.join(format!("{stem}{}", image_extension_for_format(fmt)));
            eprintln!(
                "Image format mismatch: {} contains {} bytes; writing corrected sibling {}",
                path.file_name()
                    .and_then(|name| name.to_str())
                    .unwrap_or("image"),
                fmt.to_ascii_uppercase(),
                corrected
                    .file_name()
                    .and_then(|name| name.to_str())
                    .unwrap_or("image"),
            );
            if fs::copy(&path, &corrected).is_ok() {
                return Some(corrected);
            }
        }
    }

    None
}

fn image_extension_for_file(path: &Path) -> Option<&'static str> {
    image_format(path).map(image_extension_for_format)
}

fn image_extension_for_format(format: &'static str) -> &'static str {
    match format {
        "png" => ".png",
        "jpeg" => ".jpg",
        _ => "",
    }
}

fn image_format(path: &Path) -> Option<&'static str> {
    let mut file = fs::File::open(path).ok()?;
    let mut head = [0_u8; 8];
    let len = std::io::Read::read(&mut file, &mut head).ok()?;
    let head = &head[..len];

    if head.starts_with(b"\x89PNG\r\n\x1a\n") {
        return Some("png");
    }
    if head.starts_with(b"\xff\xd8\xff") {
        return Some("jpeg");
    }

    None
}

fn is_nonempty_file(path: &Path) -> bool {
    path.exists() && path.metadata().map(|meta| meta.len() > 0).unwrap_or(false)
}

fn relative_path(from: &Path, to: &Path) -> PathBuf {
    let from_components = normalize_components(from);
    let to_components = normalize_components(to);

    let mut shared = 0;
    while shared < from_components.len()
        && shared < to_components.len()
        && from_components[shared] == to_components[shared]
    {
        shared += 1;
    }

    let mut rel = PathBuf::new();
    for _ in shared..from_components.len() {
        rel.push("..");
    }
    for component in to_components.into_iter().skip(shared) {
        rel.push(component);
    }
    if rel.as_os_str().is_empty() {
        rel.push(".");
    }
    rel
}

fn normalize_components(path: &Path) -> Vec<String> {
    path.components()
        .filter_map(|component| match component {
            Component::Prefix(prefix) => Some(prefix.as_os_str().to_string_lossy().to_string()),
            Component::RootDir => Some(String::from("/")),
            Component::CurDir => None,
            Component::ParentDir => Some(String::from("..")),
            Component::Normal(part) => Some(part.to_string_lossy().to_string()),
        })
        .collect()
}
