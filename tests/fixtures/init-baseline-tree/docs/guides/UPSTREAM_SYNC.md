# Upstream Sync Guide

**Purpose**: Step-by-step guide for AOD template adopters to safely pull upstream template improvements into their customized projects.

**Script**: `scripts/sync-upstream.sh`

---

## Prerequisites

- **git** >= 2.30 installed
- **bash** (macOS 3.2+ or Linux 4+)
- A project that was forked or cloned from the AOD template

---

## Step 1: Configure Upstream Remote (One-Time)

Run the setup subcommand to add the canonical AOD template as an upstream remote:

```bash
scripts/sync-upstream.sh setup
```

This adds the `upstream` remote pointing to the AOD template repository and fetches the latest refs.

**Custom upstream URL** (if using a different template source):

```bash
scripts/sync-upstream.sh setup --url https://github.com/myorg/my-template.git
```

**Idempotent**: Running setup again reports "already configured" without duplicating the remote.

---

## Step 2: Check for Upstream Changes

See what changed upstream since your last sync:

```bash
scripts/sync-upstream.sh check
```

Output shows files grouped by category:

```
Upstream changes available:

  Skills:    3 files
  Rules:     1 files
  Scripts:   2 files
  Docs:      5 files

  Total: 11 files changed
```

If nothing changed, you'll see:

```
Already up to date
  Last sync point: 2026-02-01 12:00:00 -0500
```

---

## Step 3: Preview the Merge (Dry Run)

Before making any changes, preview what the merge would do:

```bash
scripts/sync-upstream.sh merge --dry-run
```

This shows a `git diff --stat` of what would change, then aborts — no files are modified.

---

## Step 4: Merge Upstream Changes

When ready to apply changes:

```bash
scripts/sync-upstream.sh merge
```

**What happens automatically**:

1. **Pre-flight checks**: Verifies clean working tree and upstream remote
2. **Backup branch**: Creates `pre-sync-backup-YYYYMMDD-HHMMSS` at your current state
3. **Memory protection**: Backs up `.aod/memory/` and restores it after merge
4. **Merge**: Runs `git merge upstream/main --no-edit`
5. **Report**: Shows files updated, conflicts (if any), and next steps

**If the merge completes cleanly**: You're done — run `validate` to verify.

**If there are conflicts**: See "Resolving Conflicts" below.

---

## Step 5: Resolve Conflicts (If Any)

When the merge reports conflicts:

1. Open each conflicted file and look for git conflict markers:
   ```
   <<<<<<< HEAD
   Your version
   =======
   Upstream version
   >>>>>>> upstream/main
   ```

2. Edit the file to keep the version you want, then:
   ```bash
   git add <resolved-file>
   ```

3. After resolving all conflicts:
   ```bash
   git commit   # Completes the merge
   ```

**File ownership reference**:

| Category | Strategy | Example Files |
|----------|----------|--------------|
| Template-managed | Accept upstream | `.claude/skills/`, `.aod/templates/`, `docs/core_principles/` |
| Adopter-owned | Keep yours | `.aod/memory/`, `docs/product/`, `specs/` |
| Mixed | Merge manually | `CLAUDE.md`, `Makefile`, `.gitignore` |

**Quick resolution commands**:

```bash
# Keep your version of a file
git checkout --ours path/to/file && git add path/to/file

# Accept upstream version of a file
git checkout --theirs path/to/file && git add path/to/file
```

**To abort and restore**:

```bash
git merge --abort
# Or restore from backup:
git checkout pre-sync-backup-YYYYMMDD-HHMMSS
```

---

## Step 6: Validate Post-Sync Integrity

After a merge, verify your project is in good shape:

```bash
scripts/sync-upstream.sh validate
```

This checks:

1. **File existence**: Expected AOD directories and files are present
2. **YAML frontmatter**: Spec/plan/tasks files have valid frontmatter
3. **Placeholder leaks**: No `{{PLACEHOLDER}}` values leaked from upstream templates
4. **Constitution integrity**: Your `.aod/memory/constitution.md` still has your values

Each issue includes a specific remediation step.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Not a git repository" | Run from within your project's git repo root |
| "No upstream remote configured" | Run `scripts/sync-upstream.sh setup` first |
| "Working tree has uncommitted changes" | Commit or stash changes before merging |
| "Failed to fetch from upstream" | Check network access and upstream URL |
| Too many conflicts to resolve | `git merge --abort` then selectively cherry-pick changes |
| `.aod/memory/` was modified | Script auto-restores, but check with `git diff .aod/memory/` |
| Lost your changes | Restore from backup: `git checkout pre-sync-backup-*` |

---

## Recommended Sync Schedule

- **Monthly**: Check for upstream changes on the first week of each month
- **On-demand**: When upstream releases important bug fixes or new features
- **Before new features**: Sync before starting major new feature work

---

## Reference

- **Script source**: `scripts/sync-upstream.sh`
- **Fork setup details**: [FORK_SETUP.md](../planning/FORK_SETUP.md)
- **File ownership matrix**: Defined in FORK_SETUP.md and used by the sync script's file categorization
