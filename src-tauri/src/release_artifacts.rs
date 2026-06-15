use std::collections::BTreeSet;
use std::fs;
use std::path::{Path, PathBuf};

use sha2::{Digest, Sha256};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ReleaseArtifact {
    pub relative_path: PathBuf,
    pub sha256: String,
    pub size_bytes: u64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ReleaseManifest {
    pub artifacts: Vec<ReleaseArtifact>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PackageContentReport {
    pub expected_files: Vec<PathBuf>,
    pub actual_files: Vec<PathBuf>,
    pub missing_files: Vec<PathBuf>,
    pub unexpected_files: Vec<PathBuf>,
}

pub fn build_release_manifest(
    root: &Path,
    relative_paths: &[&str],
) -> Result<ReleaseManifest, String> {
    let mut artifacts = Vec::new();

    for relative in relative_paths {
        let path = root.join(relative);
        let bytes = fs::read(&path)
            .map_err(|err| format!("failed to read {}: {err}", path.display()))?;
        let mut hasher = Sha256::new();
        hasher.update(&bytes);
        artifacts.push(ReleaseArtifact {
            relative_path: PathBuf::from(relative),
            sha256: format!("{:x}", hasher.finalize()),
            size_bytes: bytes.len() as u64,
        });
    }

    artifacts.sort_by(|left, right| left.relative_path.cmp(&right.relative_path));

    Ok(ReleaseManifest { artifacts })
}

pub fn verify_checksum_matrix(root: &Path, manifest: &ReleaseManifest) -> Result<(), String> {
    for artifact in &manifest.artifacts {
        let path = root.join(&artifact.relative_path);
        let bytes = fs::read(&path)
            .map_err(|err| format!("failed to read {}: {err}", path.display()))?;
        let mut hasher = Sha256::new();
        hasher.update(&bytes);
        let checksum = format!("{:x}", hasher.finalize());

        if checksum != artifact.sha256 {
            return Err(format!(
                "checksum mismatch for {}: expected {} but found {}",
                path.display(),
                artifact.sha256,
                checksum
            ));
        }

        if bytes.len() as u64 != artifact.size_bytes {
            return Err(format!(
                "size mismatch for {}: expected {} but found {}",
                path.display(),
                artifact.size_bytes,
                bytes.len()
            ));
        }
    }

    Ok(())
}

pub fn validate_package_contents(
    root: &Path,
    expected_paths: &[&str],
) -> Result<PackageContentReport, String> {
    let mut expected_files = expected_paths
        .iter()
        .map(|relative| root.join(relative))
        .collect::<Vec<_>>();
    expected_files.sort();

    let mut actual_files = collect_files(root)?;
    actual_files.sort();

    let expected_set = expected_files.iter().cloned().collect::<BTreeSet<_>>();
    let actual_set = actual_files.iter().cloned().collect::<BTreeSet<_>>();

    let missing_files = expected_set
        .difference(&actual_set)
        .cloned()
        .collect::<Vec<_>>();
    let unexpected_files = actual_set
        .difference(&expected_set)
        .cloned()
        .collect::<Vec<_>>();

    Ok(PackageContentReport {
        expected_files,
        actual_files,
        missing_files,
        unexpected_files,
    })
}

fn collect_files(root: &Path) -> Result<Vec<PathBuf>, String> {
    let mut files = Vec::new();
    let mut stack = vec![root.to_path_buf()];

    while let Some(current) = stack.pop() {
        let entries = fs::read_dir(&current)
            .map_err(|err| format!("failed to read {}: {err}", current.display()))?;
        for entry in entries {
            let entry = entry
                .map_err(|err| format!("failed to read {}: {err}", current.display()))?;
            let path = entry.path();
            let file_type = entry
                .file_type()
                .map_err(|err| format!("failed to inspect {}: {err}", path.display()))?;
            if file_type.is_dir() {
                stack.push(path);
            } else if file_type.is_file() {
                files.push(path);
            }
        }
    }

    Ok(files)
}
