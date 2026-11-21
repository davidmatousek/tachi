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

## T041: W3 sweeps (tester, 2026-11-20)

**Result: FINDINGS.** Pattern A hits: 0. Pattern B hits: 1 (the baseline hit, a technical use). Failed checks: 1 of 14, FR-009 on the strict reading the task set: 13 recipe lines carry no Claude Code docs link on the line or its bullet, and each of them has one nearby. Everything else passed or is not applicable.

**Method.** Read-only. Files were read from git blobs (`git show <ref>:<path>`, `git grep`, `git diff`) and the two pull requests from `gh pr view <n> --json title,body`, fetched 2026-11-20. Refs: Part A `b71a0d7` (branch `391-isolated-auditable-operation`, equal to the working tree for every file named here), part-b `f34e0ed` (branch `391-isolated-auditable-operation-part-b`), main `39af1ce` (refs were resolved with read-only `rev-parse`, `merge-base`, `log`, `ls-tree` and `rev-list` as well). Sweeps are Python `re` runs over those blobs with the spec's patterns (`spec.md` lines 20 to 26), case-insensitive; Pattern A also ran in a loose form that allows any whitespace, line break or Unicode dash between its words, and the loose form found nothing the literal form missed. No pytest, no extractor, no checkout, no product file edited. A line number is `file:line` at Part A unless a ref is named; a runbook section is written `runbook §N`.

| # | Check | Result | Evidence in brief |
|---|-------|--------|-------------------|
| 1 | SC-A2 sweep, six documents | pass | The D-3 sentence is verbatim at 8 places; 4 unqualified claims on main are gone; 0 remain (1.1, 1.2) |
| 2 | PRD-054 and PRD-060 untouched | pass | Neither file is in the `02_PRD` diff (1.3) |
| 3 | ADR-014 changed only by its dated Note | pass | +2 lines, 0 removed (1.4) |
| 4 | Pattern A, zero hits | pass | 0 hits in 10 sources (2.1) |
| 5 | Pattern B, a disposition for every hit | pass | 1 hit, `CLAUDE_PERMISSIONS.md:225`, a technical use (2.2) |
| 6 | Vocabulary rules | pass | "validated" for the live record; the fix named only as "the key-handling patch" (2.4) |
| 7 | CHANGELOG entry and release notes | n/a | Not written yet; T046 sweeps them (2.5) |
| 8 | FR-002 order | pass | `README.md:164` before `:166` (3.1) |
| 9 | FR-003 | pass | Header scope, two gaps, five corrections, §3 to §5 headings byte-exact (3.2) |
| 10 | FR-009 citations | **fail** | 13 lines without a docs link on the line or bullet (3.3) |
| 11 | FR-011a | pass | Guide links the runbook; one semver on the marked line; slug resolves (3.4) |
| 12 | FR-015 | pass | ADR-014 and ADR-019 Notes dated; part-b ADR-019 is the Part A text (3.5) |
| 13 | Consumer guidance on part-b | pass | Both files carry it (3.6) |
| 14 | Runbook against the outline | pass | Every item present; the US4 items are n/a (3.7) |

### 1. SC-A2 sweep over the six data-locality documents (Part A)

**1.1 The D-3 sentence.** Each occurrence was compared with the sentence in PRD-391 D-3 (1,491 characters once link markup is removed). All 8 match character for character.

| Document | Where the D-3 sentence stands | Result |
|----------|-------------------------------|--------|
| `README.md` | `:164` (Quick Start step 3, before the key step), `:273` (`/tachi.infographic` section) | pass |
| `docs/guides/DEVELOPER_GUIDE_TACHI.md` | `:59` (Setting Up GEMINI_API_KEY), `:1718` (Generating Infographics with Gemini API) | pass |
| `.claude/rules/scope.md` | `:17` ("Data handling") | pass |
| `docs/standards/CLAUDE_PERMISSIONS.md` | `:321` (§8.1, under "Hosts") | pass |
| `SECURITY.md` | `:56` (new "Data handling" section) | pass |
| `docs/guides/ISOLATED_OPERATION_TACHI.md` | `:17` (runbook §1) | pass |

**1.2 Claims on main and what became of them.** Three passes over main and Part A found the claims: a broad data-locality vocabulary (about 60 terms), a narrow pattern for unqualified claims ("never leaves", "no data leaving", "no network egress", "default-deny on outbound" and similar), and every "local", "locally", "your machine" and "your environment" in the five older documents. On main there were 4 unqualified data-locality claims; on Part A there are none.

| Claim on main | On Part A | Result |
|---------------|-----------|--------|
| `scope.md:16` "architecture descriptions never leave their machine" | Removed. `:16` now ends "run it locally"; `:17` carries D-3 | pass |
| `scope.md:37` "NOT a SaaS: no telemetry, no remote inference, no data leaving your environment" | Replaced at `:38` by "there is no tachi-hosted service; what a run sends is stated under 'What tachi Is'" | pass |
| `CLAUDE_PERMISSIONS.md:23` "non-mutating, no network egress, no shell-out to mutating commands" | `:30` now says "Read-only does not mean offline: the `gh` query rules in this category ... call the GitHub API" | pass |
| `CLAUDE_PERMISSIONS.md:43` "default-deny on outbound network egress" | `:50` now says "an allow list, not a default-deny egress control" | pass |

README, the developer guide and SECURITY.md carried no locality claim on main; D-3 was added there. `CLAUDE_PERMISSIONS.md:11` ("default-secure ... for adopters") is a security claim, not a locality claim; it is covered by FR-003 in 3.2.

The runbook has no main version. The narrow pattern gave 8 hits on 7 of its lines (`:49`, `:69`, `:71`, `:75`, `:412`, `:501`, `:510`). All are scoped statements: a desktop notification that stays on the machine (`:49`); templates that import only local files and scripts that load no network library (`:69`); the offline render check (`:71`, `:412`); the air-gapped install note (`:75`); and the program guidance's own wording (`:501`, `:510`). Its other flow statements (runbook §1 hosts and Claude Code's own traffic, `:84`, the TLS and key-handling text in §3, §7) elaborate the D-3 flows and claim nothing about what stays local. The two statements below that need a reader's care are O-2 and O-3.

Statements that remain and are not unqualified claims (observations; no action required unless the maintainer rules otherwise):

| Id | Where | Text | Why it is not a claim that nothing leaves |
|----|-------|------|-------------------------------------------|
| O-1 | `scope.md:16` | "adopters install it into their own project and run it locally" | States where the harness runs. The D-3 bullet follows at `:17` |
| O-2 | runbook `:410` | "It runs no model and sends nothing to a provider." | Scoped to the by-hand report build in §6 (extractor, typst, mmdc). True of that step; the run's data already went to the provider (§1) |
| O-3 | runbook `:501` | "local work that needs no internet access" | The program guidance's own name for its first category, applied to tachi's work. The model connection is item 2 of the table at `:506` and runbook §1. The closest of the three to a misreading; an optional rewording would add "apart from the model connection (§1)" |

**1.3 PRD-054 and PRD-060.** `git diff --name-status main...391-isolated-auditable-operation -- docs/product/02_PRD/` lists `A 391-isolated-auditable-operation-2026-11-16.md` and `M INDEX.md`. Neither `054-security-assessment-pdf-booklet-2026-03-28.md` nor `060-professional-pdf-security-report-branding-2026-03-29.md` appears. The `INDEX.md` diff is the "Last Updated" line and one new row for 391. The same holds on part-b. Result: pass.

**1.4 ADR-014.** The diff against main is `+2` lines (the Note at `ADR-014-gemini-api-optional-image-generation.md:19` and a blank line) and no removed line. The Context sentence "entirely self-contained (no external service dependencies)" is unchanged (`:31` now, `:29` on main). The file is identical on part-b. Result: pass.

### 2. Wording Rules over the Surface (`spec.md` lines 20 to 26)

**2.1 Pattern A (zero hits, no exceptions).** Patterns: `CVP[- ]?(ready|approved|certified|verified|compliant|endorsed|validated)`; `(approved|endorsed|certified|verified|sanctioned|accredited) (by|with) Anthropic`; `Anthropic[- ](approved|endorsed|certified|verified|sanctioned|accredited)`.

| Source | Ref | Hits |
|--------|-----|------|
| `README.md`, `docs/guides/DEVELOPER_GUIDE_TACHI.md`, `.claude/rules/scope.md`, `docs/standards/CLAUDE_PERMISSIONS.md`, `SECURITY.md`, `docs/guides/ISOLATED_OPERATION_TACHI.md` (6 sources) | Part A | 0 |
| `docs/architecture/02_ADRs/ADR-049-privilege-contract-and-write-confinement.md` | Part A | 0 |
| The same ADR-049 | part-b | 0 |
| PR #392 title and body | fetched 2026-11-20 | 0 |
| PR #396 title and body | fetched 2026-11-20 | 0 |

Also 0 hits in: the six documents on part-b, ADR-014 and ADR-019 on both refs, and the 44 adopter-read files the feature edits (the Surface files included; both the lines it added and the whole files). Result: pass.

**2.2 Pattern B (every hit gets a disposition).** Pattern: `\b(endors\w*|certif\w*|accredit\w*|compliant|verified|sanctioned)\b`. One hit in the Surface.

| file:line | Hit | Disposition |
|-----------|-----|-------------|
| `docs/standards/CLAUDE_PERMISSIONS.md:225` (Part A and part-b) | "The current built-in set (verified at the F-4 merge SHA via Claude Code documentation):" | Technical use: it records that the built-in command set was checked against the Claude Code docs at a commit. It is not a claim of standing. It is the baseline hit; the text is unchanged from main, where it stood at `:218`, and the 7 lines the feature added to the file header moved it to `:225` |

No hit in the other five documents, ADR-049 (either ref), PR #392 or PR #396. Result: pass (1 hit, dispositioned).

**2.3 Pattern B outside the Surface as T041 scopes it (not counted above).** Spec line 22 also names "every other adopter-read file the feature adds or edits". A whole-file sweep of the 44 adopter-read files the feature edits (specs, tests, workflows and product records left out) found 42 hits in 12 files: the 1 Surface hit above and 41 hits in 11 other files. Of those 41, 40 sit in text the feature did not write. One is in a line it added: `scripts/extract-report-data.py:30`, "Remove a build directory (use it after a verified compile).", a technical use. None reads as a claim of standing; they are of the kind "verified at T060", "certificate pinning", "sanctioned cleanup path" and the dated `Verified:` lines for the image-model chain.

| File | Hits | Written by this feature |
|------|------|------------------------|
| `docs/architecture/01_system_design/README.md` | 15 | no |
| `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md` | 6 | no |
| `docs/architecture/00_Tech_Stack/README.md` | 6 | no |
| `docs/architecture/README.md` | 3 | no |
| `.claude/skills/tachi-orchestration/references/sarif-specification.md`, `.claude/skills/tachi-report-assembly/references/typst-artifacts.md`, `.claude/skills/tachi-report-assembly/references/typst-template-contract.md` | 2 each | no |
| `.claude/skills/tachi-orchestration/references/output-schemas.md`, `.gitignore`, `docs/architecture/02_ADRs/ADR-014-gemini-api-optional-image-generation.md` | 1 each | no |
| `scripts/extract-report-data.py` | 2 | `:30` yes; `:1794` no |

If the Surface is meant to reach pre-existing lines in edited files, T046 or the PM should rule; no change is needed on the evidence here.

**2.4 Vocabulary rules.**

| Rule | Evidence | Result |
|------|----------|--------|
| The live record says "validated", never "verified" | Runbook: "Last validated" `:5`, `:9`; "What 'validated' covers" `:437`, `:439`; `:547`, `:561`. The word "verified" does not occur in the runbook. Its only "verif" stems are the allowed names "Cyber Verification Program" and "Verification Portal" (`:276`, `:461` to `:463`, `:472`). ADR-049 `:182` says "live validation" | pass |
| The unreleased fix is "the key-handling patch" and nothing more specific | PR #392 body line 9 uses exactly that phrase. The six documents, ADR-049 (both refs) and PR #396 do not mention the fix. A search of the 44 adopter-read files the feature edits (part-b tip; 36 on Part A) for `GHSA`, `key-handling`, `env-loader` and `loader dump` found 0 hits | pass |
| Allowed by name ("Cyber Verification Program", "Verification Portal", `tachi-permissions-verify.yml`) | Used as named, in the runbook, `SECURITY.md:48`, `CLAUDE_PERMISSIONS.md:424` and ADR-049 `:46`, `:138` | pass |

**2.5 CHANGELOG entry and release notes.** `CHANGELOG.md` is unchanged on both branches and holds no entry for 391; no release-notes file exists in the feature diff. Not yet written; T046 sweeps them. Result: n/a.

### 3. W3 doc checks

**3.1 FR-002: the Gemini flow comes before the key step.** `README.md:164` (the D-3 blockquote: names Google's Gemini API and `generativelanguage.googleapis.com`, and says image prompts carry derived threat-model content) comes before `:166` ("If you want infographic images (`.jpg`), set the `GEMINI_API_KEY` environment variable ..."). On part-b the order holds at `:167` and `:169`. The developer guide has the same order: `DEVELOPER_GUIDE_TACHI.md:59` before `:63`. Result: pass.

**3.2 FR-003: `CLAUDE_PERMISSIONS.md`.**

| Required | Evidence (Part A; part-b is identical for all of these) | Result |
|----------|----------------------------------------------------------|--------|
| Header says §1 to §7 are development-time settings, not installed | `:5` "**Scope.** §1–§7 describe the development-time settings of this repository (`.claude/settings.json`). Those settings are not installed ..." | pass |
| Gap 1: a web fetch outside the allow list falls to "ask" in the default permission mode | `:9` "A web fetch outside the allow list is not denied ... falls to "ask" in the `default` permission mode" | pass |
| Gap 2: shell `curl` is not covered | `:10` "**Shell `curl` is not covered.**" | pass |
| Correction 1: "default-secure ... for adopters" (main `:11`) | `:18` now says the baseline governs tachi's own development, is not installed and "does not protect an adopter's project"; "default-secure" no longer occurs | pass |
| Correction 2: "default-deny on outbound network egress" (main `:43`) | `:50` "This is an allow list, not a default-deny egress control"; the phrase no longer occurs | pass |
| Correction 3: `--deny-tool` (main `:235`) | `:244` `claude --disallowedTools "Bash"`; `--deny-tool` no longer occurs | pass |
| Correction 4: §6 fork-and-edit adopter model | `:238` "The baseline ... exists only in a checkout of this repository ... An adopter who installs tachi with `scripts/install.sh` does not receive that file" | pass |
| Correction 5: §7.4 wildcard claims re-checked, bare `*` included | `:278` to `:288`, re-checked 2026-11-19; the bare `*` forms at `:284` to `:286` | pass |
| Pointer to §8 | `:5` (anchor `#8-agent-and-command-privilege-matrix`); heading at `:299` | pass |
| §3 to §5 headings byte-exact against main | The 8 heading lines from `## 3.` to before `## 6.` (including `### 3.1`, `### 3.2` and the three `####` worked-example headings) are identical to main on Part A and part-b. The two greps at `.github/workflows/tachi-permissions-verify.yml:119` and `:120` match on all three refs. The only new headings are §8 and §8.1 to §8.6; none was removed | pass |

**3.3 FR-009: a public Claude Code docs link for every recipe line.** Result: **fail** on the strict reading ("on the line or its bullet"), low severity.

*Definition used.* A recipe line is a line, bullet or table row that tells the reader to set, run, check or avoid something in Claude Code (a setting, flag, environment variable, slash command, `claude` subcommand or permission rule), or that states a documented Claude Code behavior the instruction relies on. Lines about tachi's own files and scripts, the live-validation record (runbook §11) and the paraphrases of program guidance (runbook §8, §9) are outside it. A line counts as cited when a `code.claude.com/docs` link is on the line, anywhere in its bullet (nested bullets and continuation paragraphs included), in the lead-in sentence directly above its list, or in the `Sources:` line directly under its table.

*Totals.* The runbook has 181 links: 156 to Claude Code docs (27 pages, 100 page-and-anchor pairs), 25 to other public pages. None is relative and none is plain http. Whether the links still resolve is the link-rot monitor's job (#332), not this sweep. The runbook is the same file on Part A and part-b.

*(a) The session profile.* A JSON block cannot carry links, so each key is cited in the prose below it. Every one of the 13 key paths and 18 deny rules has a link there:

| Profile entry (block lines) | Docs link in the prose |
|-----------------------------|------------------------|
| `env.CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` (`:95`) | `:17`, `:51` |
| deny `WebFetch`, `WebSearch` (`:98`, `:99`) | `:301`, `:314`, `:487` |
| deny `mcp__*` and the three MCP resource tools (`:100` to `:103`) | `:205` |
| deny `SendMessage`, `ListAgents`, `Monitor`, `RemoteTrigger`, `ShareOnboardingGuide` (`:104` to `:108`) | `:211` to `:216` |
| deny `Workflow`, `Agent(isolation:*)` (`:109`, `:110`) | `:220` |
| deny `Read(~/.ssh/**)`, `Read(~/.aws/**)`, `Read(~/.claude/.credentials.json)` (`:111` to `:113`) | `:187`, `:191` |
| deny `Read(//proc/**)`, `Read(.env*)` (`:114`, `:115`) | `:336`, `:157`, `:313` |
| `sandbox.enabled`, `failIfUnavailable`, `allowUnsandboxedCommands`, `autoAllowBashIfSandboxed` (`:119` to `:122`) | `:169`, `:231`, `:302`, `:306` |
| `sandbox.network.allowedDomains`, `strictAllowlist`, `tlsTerminate` (`:124` to `:126`) | `:169`, `:174`, `:232`, `:312`, `:181` |
| `sandbox.credentials.envVars`, `files` (`:129` to `:134`) | `:181`, `:236`, `:264`, `:187`, `:191` |
| `autoMode.environment`, `hard_deny`, `"$defaults"` (`:138` to `:149`) | `:175`, `:228`, `:229` |

*(b) Recipe lines with no docs link on the line or its bullet.* 13 rows. Each has a docs link nearby, shown in the last column: in the same subsection for 11 of them, and for `:218` and `:294` in the section that the line itself points to. "Claim" means a documented Claude Code behavior the line states; "instruction" means it tells the reader to act.

| Line | Exact text (the recipe clause) | Kind | Nearest docs link |
|------|--------------------------------|------|-------------------|
| `:40` | "Any non-empty value turns the variable on, `0` and `false` included. Unset it to allow the traffic again." | instruction | `:51` (the table's Sources line: environment variables) |
| `:183` | "If you remove `tlsTerminate` from your copy, remove the `credentials.envVars` entry with it." | instruction | `:181` (mask credentials, `tlsTerminate`) |
| `:200` | "Keep credential loading out of the startup files that your session's shell reads for every command: for zsh, `~/.zshenv`. Or launch with `SHELL=/bin/bash` ..." and "`CLAUDE_CODE_SHELL=/bin/bash` is the documented alternative" | instruction | `:195` (environment variables) |
| `:209` | "Command hooks, plugin monitors, LSP servers, mods and helper commands such as the status line and `apiKeyHelper` also run outside the sandbox with your full access." | claim | `:207`, `:485` (what runs outside the sandbox) |
| `:218` | "... are off while `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is set, and the profile sets it (§1)." | claim | `:51` (artifact availability, Remote Control) |
| `:239` (and the code line `:242`) | "Read the key from your secret manager in the command that starts `claude`, so it exists only in that process's environment." | instruction | `:236` (mask environment variables) |
| `:251` (and the code block `:253` to `:260`) | "Launch from a minimal environment that lists only what the session needs." | instruction | `:249` (what the sandbox restricts), `:264` (protect credentials) |
| `:284` | "Provider and authentication configuration that lives in user settings, such as `env`, `apiKeyHelper` and cloud credential helpers, is not read." | claim | `:280` (CLI reference: flags) |
| `:288` | "Your user-scope permission rules and `deniedMcpServers` entries do not load at all." | claim | `:280`, `:285` |
| `:294` | "put your own additions in `~/.claude/settings.json`: the extra credential-store rules, the `deniedMcpServers` entries and, for retention, `cleanupPeriodDays`" | instruction | `:191`, `:207`, `:445` |
| `:310` | probe row `` `touch ~/sandbox-probe` `` | instruction | `:306` (confirm commands run inside the sandbox) |
| `:311` | probe row `` `curl --noproxy '*' https://example.com` `` | instruction | `:306`, `:312` |
| `:317` | probe row "Tool inventory ... ask Claude to list its tools, loaded and deferred, by name, and run `/permissions`" | instruction | `:315` (manage permissions), `:174` |

Not counted, because they are not recipe lines: the 9 rows of the two traffic tables (`:44` to `:49`, `:57` to `:59`), which have a `Sources:` line under each table (`:51`, `:61`); the header, passivity, write-location and live-record text, which describe tachi or what happened; `:226`, a summary of the five bullets under it (`:228` to `:232`), each of which carries a link; `:347`, which says the profile sets no `sandbox.filesystem.allowWrite` entry (an absence, not a step); `:177` and `:334`, which point on to the probes; `:238`, `:245` and `:262`, which are guidance about the key, `op run` and the operating system; and `:266` and `:290`, which record what the docs do not say or what the live run showed. A reader who counts `:238` as a recipe line would make the list 14.

*To close.* Add the link named in the last column to each of the 13 lines, or rule that a link in the same subsection counts. No new source is needed. No recipe element is without a citation anywhere in the runbook.

**3.4 FR-011a: installed, linked, pinned.**

| Required | Evidence | Result |
|----------|----------|--------|
| The installed developer guide links the runbook | `DEVELOPER_GUIDE_TACHI.md:61` and `:1720` link `ISOLATED_OPERATION_TACHI.md` (a sibling file; both are installed: `INSTALL_MANIFEST.md:19`, `:20`, `:134`, `:135`) | pass |
| README "How It Works" links it | `README.md:327` (section starts at `:312`) | pass |
| The security policy links it | `SECURITY.md:48` and `:58` | pass |
| Installed with tachi: manifest and completeness test | `INSTALL_MANIFEST.md:20`, `:135`; `tests/scripts/test_install_manifest_completeness.py:34`, `:762` | pass |
| No link by local path to a non-installed location | 181 markdown links, 0 relative. `docs/standards/` appears only inside the pinned URL (`:533`); the runbook is under `docs/guides/` | pass |
| The matrix-link line has exactly one semver string with its marker | `ISOLATED_OPERATION_TACHI.md:533`. T019's grep (`grep 'x-release-please-version' docs/guides/ISOLATED_OPERATION_TACHI.md \| grep -oE '[0-9]+\.[0-9]+\.[0-9]+' \| wc -l`) prints 1 on Part A, part-b and the working tree; the file has 1 marked line | pass |
| release-please reaches the file; other markers kept | `release-please-config.json:9` lists the runbook. Marker counts match main: `README.md` 2, `scripts/install.sh` 3 | pass |
| The §8 slug resolves to the §8 heading | The link ends `#8-agent-and-command-privilege-matrix`; the GitHub slug of `## 8. Agent and command privilege matrix` (`CLAUDE_PERMISSIONS.md:299`) is the same string | pass |

The pin is `v4.48.2`, which predates §8. The runbook says so at `:535` ("No matrix exists before the first release that carries section 8"), so this is the stated lag, not a defect.

**3.5 FR-015: the ADR Notes.**

| Required | Evidence | Result |
|----------|----------|--------|
| ADR-014: dated Note pointing to the egress profile | `ADR-014-gemini-api-optional-image-generation.md:19` "Note (2026-11-19, Feature 391)": the Context phrase "is not a statement about where a run's data goes"; points to the runbook's egress profile; "This ADR's decisions are unchanged" | pass |
| ADR-019: dated Note, pins kept, served model in the transcripts | `ADR-019-shared-definitions-and-model-field-governance.md:8` "Note (2026-11-19, Feature 391)": the `model: sonnet` pins "are kept deliberately", none changed, "The model that served a run is recorded in Claude Code's transcripts, not in the agent files." | pass |
| On part-b, ADR-019's Note is Part A's wording (B1 honest-stopped) | The whole file is byte-identical to Part A (`diff` empty); no "manifest" or "evidenced" wording | pass |
| ADR-049 records the privilege contract and write confinement; the schema change only if Part B ships | Dated 2026-11-19 (`:4`). Part A: D1 to D4 (privilege contract), D5 to D9 (write confinement). part-b adds D10 `tachi_version` (`:114`) and no run-archive or manifest decision | pass |

**3.6 Consumer guidance on part-b (`f34e0ed`).**

| File | Feature-detect `tachi_version` | `schema_version` is declared, not ordinal | Result |
|------|--------------------------------|-------------------------------------------|--------|
| `.claude/skills/tachi-orchestration/references/output-schemas.md` | `:44` "Feature-detect `tachi_version`. Read it when the key is present ..." (field row `:39`) | `:45` "Treat `schema_version` in files older than 1.5 as declared, not ordinal."; also `:46`, `:47` | pass |
| `schemas/output.yaml` | `:25` to `:27` | `:28` to `:31`; also `:32` to `:36` and the field description `:127` to `:137` | pass |

On Part A neither file mentions `tachi_version` or the guidance, as expected: it is Part B text. ADR-049 D10 (part-b `:114`) repeats it.

**3.7 The runbook against `contracts/runbook-outline.md`.** The outline's US4 items ("if B1 shipped", row 7) are not applicable: B1 was honest-stopped at T051 (`tw-b1-w2.md`), and the runbook holds no archiver, run-manifest or provenance-manifest text (0 hits).

| Outline § | Items | Where in the runbook | Result |
|-----------|-------|----------------------|--------|
| 0 Header | "Last validated" with Claude Code version, OS, permission mode, date; minimum v2.1.285; owner; refresh triggers; platforms the claim covers | `:5` (2.1.330, macOS 26.6.2, auto mode, 2026-11-20), `:6`, `:7`, `:9` to `:13`, `:8` | pass |
| 1 What leaves your machine | D-3 sentence; the two hosts; Claude Code's own traffic with `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, `DISABLE_TELEMETRY`, `DISABLE_ERROR_REPORTING`; typst and mmdc local; nothing fetched or installed mid-run, backed by the offline render check; install-time `git fetch --tags` | `:17`; `:21` to `:30`; `:38` to `:51` (`:40`, `:44`, `:45`); `:69`; `:71`; `:75` | pass |
| 2 Passivity | The passivity sentence | `:79` (verbatim) | pass |
| 3 Session profile | Marked JSON block; `claude --settings <file>`; union caveat and effective-config check; `tlsTerminate` disclosure and deny-the-key fallback; Read denies as the primary secret-file control and the credential-store note; MCP servers and the hooks residual; trust only through `environment` entries; `hard_deny` only prohibits; the classifier reads commands, not output; `--setting-sources` disposition; model selection; key provisioning | `:92`/`:153`; `:90`, `:160`; `:169`, `:171` to `:177`; `:181`, `:183`; `:187`, `:191`; `:207`, `:209`; `:228`; `:229`; `:230`; `:278` to `:290`; `:268` to `:276`; `:234` to `:245`, with the working form at `:681` to `:698` | pass |
| 3 (B1 part) | "Run the archiver under the same wrapper" | none | n/a |
| 4 Probe table | `touch ~/sandbox-probe`; `curl --noproxy '*'`; planted `.env` via Read and `cat`; WebFetch denied | `:310`, `:311`, `:313`, `:314` | pass |
| 5 Write locations | Writes only under `{out}` and `$TMPDIR`, no write allowances; the `/tachi.architecture` carve-out; the output directory under the working directory; the table | `:347`; `:349`; `:351`, `:353`; `:364` to `:386` | pass |
| 6 Platforms | macOS; Linux and WSL2 with `TACHI_MMDC_PUPPETEER_CONFIG` and its trade-off; native Windows unsupported; what "validated" covers | `:394` to `:413`; `:415` to `:431` (`:427`, `:429`); `:433` to `:435`; `:437` to `:439` | pass |
| 7 Retention | `cleanupPeriodDays` at user scope, the 30-day default meets the floor, never lower it, archive before another session if a file lowers it; the D-1 pin wording without the manifest sentence | `:445`; `:453`; pin wording at `:270` to `:276` (runbook §3, "Model selection"), cross-referenced from `:443`; no manifest sentence | pass |
| 7 (B1 part) | Archiver, archive sensitivity, `run-manifest.json` | none | n/a |
| 8 Reporting routes | Out-of-scope model behaviour to the program's channel (Verification Portal, with URL and date); tachi defects to `SECURITY.md` | `:461` (Portal link), `:468` (retrieved 2026-11-19); `:464`, `:465`, `:466` | pass |
| 9 Program mapping | Each guidance item cited, paraphrased and marked; pointers to the sandbox runtime, dev container and VM; the sandbox covers shell commands only; the domain-fronting caveat | `:472`, `:474` to `:481`, `:503` to `:517`; `:477`; `:483` to `:493`; `:497` | pass |
| 10 Privilege matrix | Link to §8 at the pinned URL with the exact slug; the lag caveat; the guard covers `.claude/agents/tachi/**` and `.claude/commands/tachi.*.md`, not the adapter copies | `:533`; `:535`; `:539` | pass |
| 11 Live-validation record | Configurations, probes, platforms, Claude Code version, permission mode, date, denials observed, blockers, fallbacks | `:578`; `:614` to `:626`; `:575`; `:576`; `:577`; `:574`; `:662`, `:663`; `:700` to `:711`; `:664`, `:703` (no fallback needed; one change of method) | pass |

The two statements the task named are present: trust is granted only through `environment` entries (`:228`) and the classifier reads commands, not their output (`:230`); so is the domain-fronting caveat (`:497`, with a pointer from `:34`).

**Open items.** One failed check (FR-009, 3.3) with a cheap fix, and three optional wordings (O-1 to O-3, 1.2). Not done here: link liveness (#332), the CHANGELOG entry and release texts (T046), and a Pattern B ruling on pre-existing lines in edited files (2.3).
