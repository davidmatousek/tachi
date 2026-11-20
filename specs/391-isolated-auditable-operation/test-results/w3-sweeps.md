# W3 sweeps (feature 391)

This file collects the W3 sweep records. T019 created it with the release-please scoping below. T041 appends its sweep sections after the T019 section.

## T019: release-please wiring (DEVOPS-R, 2026-11-19)

Scoping: no release-please change for the version marker; one extra-files entry for the runbook link

**Change.** `release-please-config.json`, `packages["."]["extra-files"]`, gains `docs/guides/ISOLATED_OPERATION_TACHI.md` after `README.md` and `scripts/install.sh` (AD-2). Nothing else in the file changed, and it is still valid JSON (`jq empty`).

**The runbook does not exist yet.** T016 writes it. The question is what release-please does with an `extra-files` path that is missing. Finding: it skips the path with a warning. It does not fail the run.

| Evidence | What it shows |
| - | - |
| Upstream docs, [Updating arbitrary files](https://github.com/googleapis/release-please/blob/main/docs/customizing.md#updating-arbitrary-files) | Silent on a missing file. They describe the annotations and the file-type defaults only |
| Source, `buildChangeSet` in [`src/github.ts`](https://github.com/googleapis/release-please/blob/main/src/github.ts) | It catches `FileNotFoundError`. The code comment reads "if the file is missing and create = false, just continue to the next update", and it logs the warning `file <path> did not exist` |
| Source, `extraFileUpdates` in [`src/strategies/base.ts`](https://github.com/googleapis/release-please/blob/main/src/strategies/base.ts) | Every extra-file updater is built with `createIfMissing: false`, so a plain path such as ours takes the skip branch |
| What this repo runs | `.github/workflows/release-please.yml` uses `googleapis/release-please-action@v4`. Its [`package.json`](https://github.com/googleapis/release-please-action/blob/v4/package.json) depends on release-please `^17.3.0`. The same branch is in [release-please v17.3.0](https://github.com/googleapis/release-please/blob/v17.3.0/src/github.ts) and in the action's built [`dist/index.js`](https://github.com/googleapis/release-please-action/blob/v4/dist/index.js) at tag `v4` (all checked 2026-11-19) |
| Repo conventions | `extra-files` was introduced in commit `dcc65b1` (spec 086) for `README.md` and `scripts/install.sh`, both of which existed, so there is no precedent here for an entry that precedes its file. No test or script in `tests/` or `scripts/` pins the list; the only matches are prose in fixture copies of docs |

Consequence: the entry is safe to land before the runbook. In this feature the runbook ships in the same pull request, so the warning would not appear on `main` in any case.

**Marker rule for the runbook line (T016, T041).** For an existing file, the Generic updater ([`src/updaters/generic.ts`](https://github.com/googleapis/release-please/blob/main/src/updaters/generic.ts)) acts on any line containing `x-release-please-version` and replaces "a semver-looking string on that line". It does so with `line.replace(VERSION_REGEX, ...)` and a non-global expression, so only the first match on that line changes. The `v` prefix stays outside the match, which is why `v4.48.2` works in the README (`README.md:473` is the Markdown precedent: `<!-- x-release-please-version -->` at the end of the line). Three consequences:

- The matrix-link line must carry exactly one semver-looking string (AD-2); `v2.1.285` and any other version stay off it.
- A file with no marker, or a marker on a line with no version, is left unchanged and raises no error. A wrong or missing marker is therefore silent, so a check is worth having.
- Suggested check once the runbook exists (not run; the file is not written yet). It prints how many version-like strings the marked line holds, and the answer should be 1:

  ```bash
  grep 'x-release-please-version' docs/guides/ISOLATED_OPERATION_TACHI.md | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | wc -l
  ```

  Tried offline on two synthetic lines: a matrix link with `v4.48.2` returned 1, and the same line with `v2.1.285` added returned 2.

T041 appends below.
