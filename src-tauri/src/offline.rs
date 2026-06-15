use std::fs;
use std::path::{Path, PathBuf};

const OFFLINE_CACHE_FILES: [&str; 4] = [
    ".aod/aod-kit-version",
    "scripts/install.sh",
    "scripts/init.sh",
    "scripts/update.sh",
];

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OfflineRestoreReport {
    pub restored_files: Vec<PathBuf>,
    pub missing_cache_files: Vec<PathBuf>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct UpdateCheck {
    pub current_version: Option<String>,
    pub cached_version: Option<String>,
    pub update_available: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BootstrapReport {
    pub restore: OfflineRestoreReport,
    pub update_check: UpdateCheck,
    pub offline_ready: bool,
}

pub fn restore_offline_cache(
    repo_root: &Path,
    cache_root: &Path,
) -> Result<OfflineRestoreReport, String> {
    let mut restored_files = Vec::new();
    let mut missing_cache_files = Vec::new();

    for relative in OFFLINE_CACHE_FILES {
        let source = cache_root.join(relative);
        let destination = repo_root.join(relative);

        if source.is_file() {
            if let Some(parent) = destination.parent() {
                fs::create_dir_all(parent).map_err(|err| {
                    format!("failed to create {}: {err}", parent.display())
                })?;
            }
            fs::copy(&source, &destination).map_err(|err| {
                format!(
                    "failed to restore {} from {}: {err}",
                    destination.display(),
                    source.display()
                )
            })?;
            restored_files.push(destination);
        } else {
            missing_cache_files.push(destination);
        }
    }

    Ok(OfflineRestoreReport {
        restored_files,
        missing_cache_files,
    })
}

pub fn check_for_update(repo_root: &Path, cache_root: &Path) -> Result<UpdateCheck, String> {
    let current_version = read_version_pin(&repo_root.join(".aod/aod-kit-version"))?;
    let cached_version = read_version_pin(&cache_root.join(".aod/aod-kit-version"))?;
    let update_available = match (&current_version, &cached_version) {
        (_, Some(cached)) => current_version.as_ref() != Some(cached),
        _ => false,
    };

    Ok(UpdateCheck {
        current_version,
        cached_version,
        update_available,
    })
}

pub fn bootstrap_from_cache(repo_root: &Path, cache_root: &Path) -> Result<BootstrapReport, String> {
    let restore = restore_offline_cache(repo_root, cache_root)?;
    let update_check = check_for_update(repo_root, cache_root)?;
    let offline_ready = repo_root.join("scripts/update.sh").is_file()
        && repo_root.join(".aod/aod-kit-version").is_file();

    Ok(BootstrapReport {
        restore,
        update_check,
        offline_ready,
    })
}

fn read_version_pin(path: &Path) -> Result<Option<String>, String> {
    match fs::read_to_string(path) {
        Ok(contents) => Ok(parse_version_pin(&contents)),
        Err(err) if err.kind() == std::io::ErrorKind::NotFound => Ok(None),
        Err(err) => Err(format!("failed to read {}: {err}", path.display())),
    }
}

fn parse_version_pin(contents: &str) -> Option<String> {
    let mut fallback = None;

    for line in contents.lines() {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }
        if let Some(value) = trimmed.strip_prefix("version=") {
            return Some(value.trim().to_string());
        }
        if fallback.is_none() {
            fallback = Some(trimmed.to_string());
        }
    }

    fallback
}
