# Delivery Document: Feature 066 — Install Script and Version Tagging

**Delivery Date**: 2026-04-06
**Branch**: `066-install-script-and`
**PR**: #85

---

## What Was Delivered

- **Created `scripts/install.sh`** — single-command install replacing 6+ manual `cp` commands for tachi adoption
- **Added machine-parseable manifest section** to `INSTALL_MANIFEST.md` with `<!-- BEGIN MANIFEST -->` / `<!-- END MANIFEST -->` markers
- **Implemented auto-detection** of source tachi directory from script location via `BASH_SOURCE[0]` + `dirname` + `pwd`
- **Implemented `--source` override** for non-default tachi clone locations
- **Implemented `--version` pinned installs** with dirty tree check, branch recording, trap-based cleanup on all exit paths (success, error, Ctrl+C)
- **Updated README.md** Quick Start Step 2: scripted install as primary path, manual commands in collapsible `<details>` fallback
- **Updated Developer Guide** install section to match README with scripted primary path
- **Updated architecture docs** with install script component (C1-C5) and data flow diagram

---

## How to See & Test

1. **Run help**: `scripts/install.sh --help` — displays usage with --source, --version, --help flags
2. **Fresh install**: From an empty target directory, run `bash /path/to/tachi/scripts/install.sh` — all manifest files copied, summary displayed
3. **Idempotent re-run**: Run install again — identical result, zero errors
4. **Custom source**: `bash install.sh --source /path/to/tachi` — uses explicit source path
5. **Version pinned** (after v4.0.0 tag): `bash install.sh --version v4.0.0` — installs from tagged version, restores source repo state
6. **Verify README**: Open README.md — scripted install is primary Quick Start, manual commands in collapsible section
7. **Verify Developer Guide**: Open docs/guides/DEVELOPER_GUIDE_TACHI.md — matches README install path

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 6.25 hrs (team-lead) / 7-10 hrs (PRD) |
| Actual Duration | 1 day (2026-04-06, single session) |
| Variance | Faster than estimated |
| Tasks | 19/20 complete (T018 deferred — post-merge git tag) |
| Execution Waves | 4 (Wave 5 is post-merge) |

---

## Surprise Log

Implementation completed faster than estimated — well-defined manifest paths and exhaustive acceptance criteria in the spec made the bash script a straightforward translation exercise with minimal design decisions during coding.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Process / Estimation | Manifest-driven bash scripts with exhaustive specs complete faster than estimated — when all distributable paths are pre-defined and acceptance criteria are concrete, implementation is translation, not design. | PAT-019 in INSTITUTIONAL_KNOWLEDGE.md |

---

## Feedback Loop

**New Ideas**: None

---

## Deferred Items

| Item | Reason | Action Required |
|------|--------|-----------------|
| T018 — `v4.0.0` git tag | Must be created after PR merge to main | Run: `git tag -a v4.0.0 -m "Release v4.0.0 — first tagged release with install script" && git push origin v4.0.0` |
