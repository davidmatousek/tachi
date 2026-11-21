---
prd_reference: docs/product/02_PRD/391-isolated-auditable-operation-2026-11-16.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-11-16
    status: APPROVED_WITH_CONCERNS
    notes: "Attempt 2 (delta re-review of v1.1): all 20 attempt-1 findings resolved (4 HIGH, 10 MEDIUM, 6 LOW); every PRD FR maps to a spec FR citing its source; no scope added; the architect's I2-N1 condition for /aod.tasks is met, as are CF-19 and CF-23. Three LOW precision items (A2-1 FR-001 AC vs the ADR-014 Note; A2-2 FR-011a wording vs its matrix link; A2-3 Wording Rules heading reach) folded in v1.2 without re-review, per the PM. A2-4..A2-8 optional. Attempt 1 (v1.0) was CHANGES_REQUESTED: H-1 patch named by area, H-2 unbounded sweep, H-3 PRD FR-20 missing, H-4 term list missing. Full review: .aod/results/pm-spec-391.md."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---
# Feature Specification: Isolated and Auditable Operation

**Feature Branch**: `391-isolated-auditable-operation`
**Created**: 2026-11-16 · **Revised**: 2026-11-16 (v1.2: v1.1 after PM attempt 1; A2-1..A2-3 folded after PM attempt 2, `.aod/results/pm-spec-391.md`)
**Status**: PM APPROVED_WITH_CONCERNS (2026-11-16)
**Input**: User description: "PRD: 391 - isolated-auditable-operation"
**PRD**: `docs/product/02_PRD/391-isolated-auditable-operation-2026-11-16.md` (v1.2, Triad-approved 2026-11-16). This spec restates the PRD's five user stories as independently testable journeys and turns its functional requirements into Given/When/Then acceptance criteria. PRD decisions D-1 to D-12, the v1.1 PM rulings and the trip-wires TW-0, TW-A1..A3 and TW-B0..B4 are binding and are referenced, not restated. The PRD's acceptance criteria (AC-A1.1 to AC-B2.2) and success criteria (SC-A1 to SC-B3) also bind by reference; where a restatement here is narrower, the PRD governs.

## Wording Rules *(binding on the Surface defined below)*

- **Surface**: the six data-locality documents (`README.md`, `docs/guides/DEVELOPER_GUIDE_TACHI.md`, `.claude/rules/scope.md`, `docs/standards/CLAUDE_PERMISSIONS.md`, `SECURITY.md`, the runbook `docs/guides/ISOLATED_OPERATION_TACHI.md`); every other adopter-read file the feature adds or edits (the CHANGELOG entry, ADR-049); the PR title and body.
- **Pattern A, zero hits, no exceptions** (case-insensitive): `CVP[- ]?(ready|approved|certified|verified|compliant|endorsed|validated)`; `(approved|endorsed|certified|verified|sanctioned|accredited) (by|with) Anthropic`; `Anthropic[- ](approved|endorsed|certified|verified|sanctioned|accredited)`.
- **Pattern B, every hit gets a disposition in the sweep record** (case-insensitive, whole words): `\b(endors\w*|certif\w*|accredit\w*|compliant|verified|sanctioned)\b`. Each hit is reworded or recorded by file:line as a technical use that is not a claim of standing. Baseline today: one hit, `CLAUDE_PERMISSIONS.md:218` ("verified at the F-4 merge SHA"), a technical use.
- **Allowed by name**: "Cyber Verification Program", "Verification Portal", `tachi-permissions-verify.yml`.
- **Vocabulary**: the live-validation record says "validated" (D-12), never "verified". The unreleased fix is called "the key-handling patch" and nothing more specific.

## User Scenarios & Testing *(mandatory)*

Part A (User Stories 1 to 3) is the deliverable floor. Part B (User Stories 4 and 5) is gated by the PRD's trip-wires (TW-B0, TW-B1; TW-B2..B4) and may be deferred by honest stop without failing the feature.

### User Story 1 - The adopter learns exactly what leaves the machine (Priority: P1)

An adopter reading tachi's documentation, or deciding whether to set the image-generation key, sees a truthful statement of the two data flows: the Claude Code model provider receives the architecture description, the files tachi reads and the findings on every run; Google's Gemini API receives derived threat-model content only when the key is set and the infographic command runs. tachi sends nothing else; Claude Code's own operational traffic is named separately with the switches that turn it off.

**Why this priority**: A security product with a false "nothing leaves your machine" claim has a credibility defect. This story costs the least and corrects a public statement.

**Independent Test**: Sweep the six data-locality documents for claims that no data leaves the machine; each uses the PRD's D-3 sentence or is gone. Read the README key instruction cold and confirm the Gemini flow is stated before the setup step.

**Acceptance Scenarios**:

1. **Given** the six data-locality documents (`README.md`, `docs/guides/DEVELOPER_GUIDE_TACHI.md`, `.claude/rules/scope.md`, `docs/standards/CLAUDE_PERMISSIONS.md`, `SECURITY.md`, the runbook), **When** a reader searches for any statement that no data leaves the machine, **Then** every such statement uses the D-3 sentence or no longer exists; the immutable records PRD-054, PRD-060 and ADR-014 are excluded by name and stay as written (ADR-014 receives a dated Note instead).
2. **Given** the README's instruction for the image-generation key, **When** the reader reaches it, **Then** the text states what the infographic step sends and to which host before it explains how to set the key.
3. **Given** `CLAUDE_PERMISSIONS.md`, **When** an adopter reads it, **Then** its header says §1–§7 describe the repository's development-time settings, which are not installed; it states that a web fetch outside the allow list falls to "ask" rather than "deny" (in the default permission mode) and that shell `curl` is not covered; the five adopter-facing errors are corrected; and §8 is the adopter-facing matrix.

---

### User Story 2 - A security team runs tachi inside an isolated environment from a validated runbook (Priority: P1)

A security practitioner whose organisation or program requires isolation controls around reduced-safeguard models follows one installed runbook: tachi's egress profile, one session profile passed at launch covering the sandbox and auto mode, probe checks, write locations, retention, reporting routes, a passivity statement, a program mapping section, and a live-validation record stamped with the Claude Code version, operating system, permission mode and date.

**Why this priority**: This is the request that triggered the feature. Without it adopters reverse-engineer tachi's hosts and paths and may disable protections to make it run.

**Independent Test**: In a scratch adopter project installed from the installer, start a Claude Code session with the runbook's profile and run the full pipeline twice, with and without the key. Both runs complete, the probes pass, and there are zero unexpected egress denials, on each platform the runbook header names.

**Acceptance Scenarios**:

1. **Given** the runbook's session profile applied to a fresh session in a scratch adopter project installed with the installer, **When** the five commands run in sequence without the key and again with the key, **Then** every command completes with every probe passing and zero unexpected egress denials, on each platform the runbook header names.
2. **Given** the runbook's egress section, **When** a reader checks it against the agents, skills and scripts, **Then** it lists exactly the two hosts a run reaches, names Claude Code's own operational traffic separately with the switches that turn it off, states that the PDF compiler and the diagram renderer run locally, and rests "nothing is fetched mid-run" on the offline render check rather than on an absence of denials.
3. **Given** the runbook, **When** a reader looks for retention and reporting, **Then** it names the native retention setting at user scope, says the 30-day default meets the floor and must never be lowered, and routes out-of-scope model behaviour to the program's own channel (the Verification Portal unless a public address exists) and tachi defects to the private disclosure route.
4. **Given** the runbook's header, **When** a reader checks freshness, **Then** it carries "Last validated: Claude Code vX.Y.Z on <OS>, <permission mode>, YYYY-MM-DD", the minimum Claude Code version (v2.1.285), an owner and the refresh triggers, and the "validated" claim is scoped to the platforms actually run.
5. **Given** a full run under the profile, **When** the paths it wrote are listed, **Then** every path is under the run's output directory or the sandbox's per-user temporary directory, and the installed templates tree is byte-unchanged, including after a run with a custom report configuration.
6. **Given** the runbook's program mapping section, **When** a reader compares it with the program's guidance, **Then** each item is marked as covered by the session profile or as needing a process-level boundary, with a pointer to Claude Code's documented options for the latter; the guidance is cited and paraphrased, never reproduced; and the Wording Rules hold.

---

### User Story 3 - A reviewer trusts one enforced matrix of agent privileges (Priority: P2)

An enterprise security reviewer approving or upgrading tachi reads one matrix that lists, for every tachi agent and every tachi command, the tier, the declared tools, the model, the exact shell command families, the write locations and the hosts, with a note on which columns Claude Code enforces at runtime and which are declarations. CI fails when the declarations drift from the matrix.

**Why this priority**: The tiering already exists but is implicit, unguarded and partly contradicted by adapter copies that declare no tools. Making it enforceable is cheap and makes every later hardening (such as #360) checkable.

**Independent Test**: Add a tool to any agent in a scratch branch and open a pull request; the guard goes red. Revert; it goes green. Follow each documented install or repair path and diff the installed agents' tool lists against the matrix.

**Acceptance Scenarios**:

1. **Given** the matrix, **When** CI runs on a synthetic change that adds or removes a tool, changes the model, or adds any frontmatter key on any agent in the agents directory, or changes a tachi command's frontmatter, **Then** the guard fails; **Given** the unchanged tree, **When** CI runs, **Then** it passes; the guard's self-test exercises the red path on every run; it runs on pull requests and on pushes to the default branch, where the push-leg evidence arrives at merge as a lagging check.
2. **Given** the agents directory, **When** the guard classifies its files, **Then** every file is exactly one of: an agent file (its name marker matches the tachi prefix, is unique and has a matrix row), a non-agent document on the explicit allow-list, or anything else, which is red; a planted agent with a foreign name, an unlisted file with no frontmatter, and a duplicate name each fail.
3. **Given** every documented install or repair path, **When** an adopter follows it, **Then** the installed agents' declared tools match the matrix, and the repair path points at the installer rather than at adapter copies.
4. **Given** the matrix's row for a shell-capable agent or a command, **When** a reviewer reads it, **Then** it lists the exact command families, the paths written, the hosts and the child processes it spawns (diagram renderer, headless browser, invisible to transcripts and permission rules), and each column says whether Claude Code enforces it at runtime or it is a declaration.

---

### User Story 4 - An operator archives a run and proves which model served each agent (Priority: P2, gated by TW-B0 and TW-B1)

After a run, an operator archives the session's main and subagent transcripts and persisted tool results, unredacted, to a location that cannot be committed, and gets a structured manifest: tachi version, session id, Claude Code versions, the pinned and the served model for each recorded subagent instance, synthetic turns counted separately, tool-call counts, outbound hosts, denied or unexpected egress, and the hash of every artifact in the output directory.

**Why this priority**: In July 2026 a tachi run drew a wrong conclusion about which model ran its agents, and the transcripts needed to check were gone. Provenance is the only way to evidence how a threat model was produced; it is gated because per-agent attribution has never been demonstrated on a tachi run.

**Independent Test**: Run the archiver against the synthetic two-generation fixture and the scrubbed recorded run: every assistant turn is classified (served or synthetic) per recorded subagent instance; a corrupted fixture makes it exit non-zero; dummy keys planted in six places never appear in the manifest; a destination inside a work tree is refused unless ignored.

**Acceptance Scenarios**:

1. **Given** a recorded fixture run, **When** the archiver runs, **Then** the manifest classifies 100% of assistant turns (served or synthetic), main and per recorded subagent instance by agent name; synthetic turns are counted separately and never as served; and any tachi agent that did not appear as a separate subagent is listed rather than inferred.
2. **Given** an unparseable line, a missing required metadata key (agent type, tool-use id), a metadata agent name that differs from the line-level attribution name, zero assistant turns or an empty histogram, **When** the archiver runs, **Then** it exits non-zero and writes no manifest; extra metadata keys are tolerated and recorded.
3. **Given** a destination inside any git work tree (including a dotfiles repository at the home directory), **When** the archiver resolves it, **Then** it refuses unless the ignore check passes on a path inside it; it never writes into a non-empty destination, refuses a live session without the explicit override, creates directories owner-only and files owner-only, and never follows a symlink into a work tree.
4. **Given** dummy keys planted in six places (a shell header, a URL query, URL userinfo, tool-result text, a metadata description, a denial message), **When** the manifest is built, **Then** none appears in it and the run succeeds; **Given** a separately forced leak, **When** the final scan runs, **Then** the run fails and no manifest is written.
5. **Given** a fixture with each denial kind planted (a sandbox refusal, a classifier block, a permission-rule deny), **When** the archiver runs, **Then** each is reported, and the manifest's denial-detection field names the Claude Code versions whose fixture passed and says "not validated" for any other version, never an empty list.

---

### User Story 5 - A consumer of `threats.md` knows which tachi release wrote it (Priority: P3, gated by TW-B0 and the schema reconciliation)

A consumer of a threat model reads the producing tachi version in the artifact's frontmatter, stamped deterministically from the version marker the installer recorded, so taxonomy codes can be interpreted across releases; consumers are told to feature-detect the field and to treat the schema version in older files as declared, not ordinal.

**Why this priority**: It is small and useful, but it depends on reconciling the artifact's conflicting schema declarations first and on an installed version source that does not exist today.

**Independent Test**: Install tachi with the installer into a scratch project, run a threat model, and read `tachi_version`; it equals the version the installer recorded. Install with the README manual loop and read the same marker; install by a path that skips the marker line and read `unknown`. The existing byte-identity checks show no new failures against the pre-change state.

**Acceptance Scenarios**:

1. **Given** a tachi installed by the installer or by the README manual-install loop, **When** a threat model is written, **Then** its frontmatter carries `tachi_version` equal to the version the installer recorded, written by a deterministic step rather than by a model, and the schema change is additive.
2. **Given** an install that skipped the marker line, **When** a threat model is written, **Then** `tachi_version` reads `unknown` and the documentation says so.
3. **Given** the schema declarations found by the plan audit (the installed output schema, the output-schemas template, its checklist, the SARIF spec, the orchestrator's template comment and the SARIF generator constant), **When** the version field lands, **Then** they agree in lock-step first, the de-facto frontmatter keys are documented, and the bump is additive.
4. **Given** the example baselines left at their current schema version, **When** the existing byte-identity checks run, **Then** there are no new failures against the pre-change state (the six pre-existing reds excepted) and no example is regenerated for the new field; the two drifted examples are corrected frontmatter-only after #364, measured first, and carved out to a follow-up if a rendered baseline would move.
5. **Given** the schema documentation, **When** a consumer reads it, **Then** it tells them to feature-detect `tachi_version` and to treat `schema_version` in pre-1.5 files as declared, not ordinal.

---

### Edge Cases

- The key is set but the environment blocks the Gemini host: the image step is skipped and the pipeline continues; the runbook documents the key-less path as the isolated default.
- Auto mode's classifier blocks the Gemini request despite the environment entry: the live-validation record documents the denial; the runbook presents the key-less path.
- Auto mode is unavailable on the maintainer's account at validation time: the run happens in the default permission mode under the same profile, the header stamps the mode actually run, and the auto-mode recipe ships marked as not yet run live, with a follow-up issue.
- Linux or WSL2: the headless browser used by the diagram renderer fails inside the sandbox. Only two fixes are acceptable: a reviewed no-sandbox configuration for the diagram renderer, also checked under auto mode, or a documented default without attack trees. Never an exclusion of an interpreter or tachi script, never a write allowance, never nested user namespaces.
- Native Windows has no sandbox: the runbook says so and scopes the "validated" claim.
- A custom report configuration exists: the relocated write set must still hold (tested explicitly, since a normal run never exercises that path).
- Transcript layout changes between Claude Code versions: the archiver fails loud against a minimal contract and records the Claude Code versions; the synthetic fixture covers two layout generations.
- The archive destination is a nested repository, a dotfiles repository at the home directory, or a symlink into one: refused unless the ignore check passes (identity check, not spelling).
- The session that produced the transcripts is still running: the archiver refuses without the explicit override.
- No subagent transcripts exist for a run: the manifest lists every tachi agent as not recorded; it never infers attribution.
- The runbook's profile is applied in the tachi repository itself rather than a scratch adopter project: development-time allow rules and hooks change the effective configuration, so the validation record is invalid.

## Requirements *(mandatory)*

### Functional Requirements

> **Acceptance Criteria Rule**: Each AC MUST begin with **Given** and follow Given/When/Then structure. Use `[MANUAL-ONLY] <reason>` (reason ≥10 chars) inline to mark ACs that cannot be automated. Each FR names the PRD requirement it restates.

**Group A1 — egress truth (US1)**
- **FR-001** (PRD FR-1): Every data-locality statement at the six-document surface MUST use the D-3 sentence; the immutable records PRD-054, PRD-060 and ADR-014 are not edited (ADR-014 gets a dated Note through FR-015).
  - AC: **Given** the six documents, **When** the sweep runs, **Then** zero statements without the D-3 sentence remain, PRD-054 and PRD-060 are unchanged, and ADR-014 differs only by its dated Note.
- **FR-002** (PRD FR-2): The README key instruction MUST state the Gemini flow before the setup step.
  - AC: **Given** the README, **When** read in order, **Then** the data-flow statement precedes the key setup.
- **FR-003** (PRD FR-3): `CLAUDE_PERMISSIONS.md` MUST say in its header that §1–§7 describe the repository's development-time settings, which are not installed; state the two coverage gaps (web fetch falls to ask in the default permission mode; shell `curl` is uncovered); correct the five adopter-facing errors (the "default-secure for adopters" claim, the "default-deny on outbound network egress" claim, the misnamed deny flag, the §6 fork-and-edit adopter model, §7.4's wildcard claims re-checked against current docs); point to §8 as the adopter-facing matrix; and keep the §3–§5 headings byte-exact.
  - AC: **Given** the standard, **When** read, **Then** the header statement, both gap statements, the five corrections and the §8 pointer are present and the existing section-anchored checks still pass.

**Group A2 — runbook and write confinement (US2)**
- **FR-004** (PRD FR-4): The runbook MUST state the egress profile: the two hosts; Claude Code's own operational traffic named separately with its switches; the local-only tools; the no-fetch, no-install statement backed by FR-010's offline render check.
  - AC: **Given** the runbook, **When** compared with the agents, skills and scripts and with the offline render check, **Then** the host list is exactly two and every statement holds.
- **FR-005** (PRD FR-5, D-6): The runbook MUST give one session profile passed at launch that covers: sandbox enabled, failure when unavailable, no unsandboxed retry; a network allow list containing only the Gemini host with strict allow-listing; TLS termination stated as the prerequisite of credential masking, with its disclosure (experimental; the local proxy can read sandboxed HTTPS) and the fallback of denying the key; the masked image key injected only toward the Gemini host; home-anchored credential-file denies; read denies for secret paths (the primary secret-file control); denies for the web tools; non-essential traffic disabled; MCP servers listed in the deny list or confirmed absent, with the residual that hooks, the status line and local MCP servers run outside the sandbox; no excluded commands, no write allowances, no nested user namespaces; the public probe table plus FR-010's probes. User-global settings are used for retention and offered as an opt-in always-on alternative, merge-not-replace. The runbook MUST state that the effective configuration is a union across scopes and instruct adopters to check it and run the probes under the profile.
  - AC: **Given** the profile applied to a fresh session, **When** the probe table runs, **Then** the probes fail as documented and a planted secrets file is refused through the file-read tool and through a shell read.
  - AC: **Given** the profile text, **When** reviewed, **Then** it contains no excluded-commands entry, no write allowance and no nested-user-namespaces entry; the TLS-termination disclosure, the deny-the-key fallback, the union caveat and the extension note for other credential stores are present.
- **FR-006** (PRD FR-6): The profile's auto-mode block MUST keep the built-in defaults in every list and provide the environment entries (primary use with the passivity statement; host containment; the Gemini host as a trusted domain for the optional image request only; sensitive data locations and audiences naming the derived infographic prompt; retention) and one tool-scoped hard-deny in the PRD's wording that only prohibits; the runbook MUST say that trust is granted only through environment entries and that the classifier reads commands, not their output.
  - AC: **Given** the auto-mode block, **When** reviewed, **Then** every list contains the defaults marker, the hard-deny matches the PRD wording, and nothing contradicts the inherent provider flow.
- **FR-007** (PRD FR-7): tachi MUST write only under the run's output directory and the sandbox's per-user temporary directory, so the runbook can state "no write allowances are needed"; the architecture command's own output file and archive directory inside the working directory are the documented carve-out; the write list comes from the FR-011 audit traced transitively through agents, skills, scripts and child processes.
  - AC: **Given** a full run with and without a custom report configuration, **When** the paths written are listed, **Then** none lies outside the output directory and the temporary directory (carve-out excepted) and the installed templates tree is byte-unchanged.
- **FR-008** (PRD FR-7a): The report-assembler, infographic and infographic-command write sites MUST relocate every write outside the output directory into it; nothing MUST write to the installed templates tree; the byte-identity suites MUST be shown unaffected in a scratch clone and no tracked example image or PDF baseline MUST change.
  - AC: **Given** the relocation, **When** the byte-identity suites run in a scratch clone, **Then** there are no new failures against the pre-change state and no tracked baseline changed.
- **FR-009** (PRD FR-8): The runbook MUST contain: retention (D-7, user scope, never lowered); the two reporting routes (D-10); the D-1 pin wording, adding the manifest sentence only if B1 ships; the passivity statement; the archive-sensitivity statement if B1 ships; the freshness header (D-12) with the minimum Claude Code version; a program mapping, cited and paraphrased, marking each item as covered by the session profile or as needing a process-level boundary, with a pointer to Claude Code's documented options for the latter; the statement that the sandbox covers shell commands only while file and web tools, hooks and MCP servers run outside it, with the domain-fronting caveat; a public Claude Code docs citation for every recipe line.
  - AC: **Given** the runbook, **When** read, **Then** each element is present, conditional items match what shipped, and every recipe line carries its citation.
- **FR-010** (PRD FR-9): The live validation MUST be a dedicated maintainer-run session in a scratch adopter project installed from the installer, with and without the key (key in the process environment only), on macOS and a Linux VM or with the claim scoped to the platforms run (Linux using a fix that FR-005 allows), with these probes: the probe table; a planted secrets file refused through the file-read tool and through a shell read; web fetch denied; the diagram renderer rendering offline to byte-identical images in a scratch clone; the image client trusting the session CA under TLS termination; auto mode working with non-essential traffic disabled, or the pre-ruled fallback applied. The record MUST stamp Claude Code version, operating system, permission mode and date, and the image client form MUST be pinned before the run. `[MANUAL-ONLY] requires a maintainer-launched Claude Code session`
  - AC: **Given** the record, **When** read, **Then** it shows both configurations, every probe, each platform named in the header, the mode actually run, and zero unexpected egress denials.
- **FR-011a** (PRD D-11): The runbook MUST be installed with tachi (manifest and completeness test), linked from the README "How It Works" section, the installed developer guide and the security policy, and MUST NOT live under, or link by local path to, a location that is not installed (for example `docs/security/`); the matrix, which lives in the non-installed permissions standard, is reached through a URL pinned to the installed release.
  - AC: **Given** an installer-based install, **When** the links are followed from the installed guide, **Then** none is dead and the matrix link resolves to the installed release.

**Group A3 — permission matrix and guard (US3)**
- **FR-011** (PRD FR-10): One matrix section (§8 of the permissions standard, appended after §7) MUST list per agent: tier, tools, model, exact shell command families, writes and hosts; a commands table for the six tachi commands; a child-process note; and an "enforced vs declared" statement (tools enforced; model applies unless an invocation passes one, which tachi's commands never do; shell and writes columns are declarations enforced only by the adopter's sandbox and permission rules). The runbook MUST state that the guard covers the agents directory and not the adapter copies.
  - AC: **Given** the matrix, **When** cross-checked against the agent and command frontmatter and the audited write set, **Then** every row matches.
- **FR-012** (PRD FR-11): A stdlib guard MUST fail when: a tool is added or removed, the model changes, or the frontmatter key set departs from the closed set {name, description, tools, model} on any agent; a tachi command's frontmatter changes; a shell command family in a fenced shell block of a shell-capable agent is outside that agent's allow-list (prose is never scanned); or the runbook's write-location list disagrees with the matrix. It MUST classify every file in the agents directory, recursively by path, as an agent (unique tachi-prefixed name with a matrix row), an allow-listed non-agent document, or red; and it MUST have a self-test that mutates a temporary copy and must fail, run on every run.
  - AC: **Given** a synthetic tool addition, a removal, a model change, an added key, a command-frontmatter change, a planted agent with a foreign name, an unlisted file without frontmatter and a duplicate name, **When** the guard runs, **Then** each case fails; **Given** the unchanged tree, **Then** it passes and the self-test red path is exercised.
- **FR-013** (PRD FR-12): The guard MUST run in the existing permissions workflow on pull requests and on pushes to the default branch, with the path anchor gaining the agents directory, the tachi commands, the guard script and the runbook; anchor edits MUST be sequenced with #369; the push-leg evidence arrives at merge as a lagging check.
  - AC: **Given** the workflow, **When** a guarded path changes on a pull request, **Then** the guard runs; **Given** a push to the default branch, **Then** it runs again.
- **FR-014** (PRD FR-13): The installed developer guide's repair path MUST point at the installer; the runbook MUST join the install manifest; the installed-tools assertion MUST join the existing install-fidelity harness; the adapter roster stays out of scope and is recorded as such.
  - AC: **Given** the guide, **When** the repair path is followed, **Then** the installed agents match the matrix.
- **FR-015** (PRD FR-20): ADR-049 MUST record the CI-enforced privilege contract and the write confinement, plus the provenance manifest and the schema change if Part B ships; ADR-014 MUST get a dated Note pointing to the egress profile; ADR-019 MUST get a dated Note that the pins are kept deliberately, adding that the served model is evidenced by the run manifest only if B1 ships and otherwise that it is recorded in Claude Code's transcripts.
  - AC: **Given** the ADRs, **When** read, **Then** ADR-049 is Accepted and both Notes are dated and match what shipped.

**Group B1 — run archive and manifest (US4; gated)**
- **FR-016** (PRD FR-14): The archiver MUST accept a session id or a latest-for-this-project option that finds the project by matching the transcripts' working-directory field to the project's real path; copy the main transcript and the whole session directory (subagent transcripts, metadata, persisted tool results) verbatim; honour the alternate configuration directory; run from a plain shell after the session; be stdlib-only; and join the install manifest's script whitelist.
  - AC: **Given** an installed tachi, **When** the archiver is invoked after a session, **Then** the archive is complete and byte-identical to the source files.
- **FR-017** (PRD FR-15, D-8): The default destination MUST be the user-level runs directory keyed by project directory, date and session; a destination inside any git work tree MUST be refused unless the ignore check passes on a path inside it; the archiver MUST never write into a non-empty destination (re-archiving is a no-op checked by transcript hashes), MUST refuse a live session without the explicit override, MUST create owner-only directories and files, and MUST never follow a symlink into a work tree.
  - AC: **Given** each refusal condition, **When** invoked, **Then** it exits non-zero with the reason; **Given** a dotfiles repository at the home directory with the runs directory ignored, **When** invoked, **Then** the default destination is accepted.
- **FR-018** (PRD FR-16): The manifest MUST be structured-only with a manifest version and a schema document, containing: tachi version (marker or `unknown`), session id, Claude Code versions, start, end and archived timestamps, transcript integrity hashes, main-session and per-recorded-subagent attribution (agent id, agent type, attribution name, spawn depth, parent tool-use id, pinned model, served-model histogram, synthetic turns, turns, tool calls by tool, unknown metadata keys), the list of tachi agents not recorded, permission modes seen, observed egress by host, unparsed egress count, denied egress by host and kind, the denial-detection marker, and artifact hashes (or null with a reason when no output directory is given). Parsing MUST fail against a minimal contract (assistant turn model; subagent agent type and tool-use id; metadata name agreeing with the line-level attribution name; at least one assistant turn; a non-empty histogram) and tolerate extra metadata keys. Redaction MUST be structural first (host names only), then a final scan for known key formats and the values of secret-named environment variables; a hit MUST fail the run with no manifest written.
  - AC: **Given** the fixture run with dummy keys planted in six places, **When** the manifest is produced, **Then** every field is present, no key appears, and the run succeeds.
  - AC: **Given** a separately forced leak, **When** the final scan runs, **Then** the run fails and no manifest is written.
  - AC: **Given** a corrupted or unknown-layout fixture, a name disagreement or an empty histogram, **When** parsed, **Then** the exit is non-zero.
- **FR-019** (PRD FR-17): Fixtures MUST include, always, a synthetic structure-only fixture modelled on the W0' spike and covering two layout generations (the B1 core), and, in addition, the scrubbed W2 recording (main session plus at least two subagents, one shell-capable, each denial kind, a dummy key in all six places), leakage-reviewed by the security analyst; TW-B4 replaces only the recorded fixture with a local-only check; the tests join the pytest gate's explicit module list.
  - AC: **Given** the committed fixtures, **When** inspected, **Then** no real secret, path or personal data is present and both layout generations are covered.

**Group B2 — artifact version (US5; gated)**
- **FR-020** (PRD FR-18, D-9): The installer MUST persist the version it already computes after any version checkout (adding the dirty marker; falling back to the release manifest without a git tree; otherwise `unknown`) to one line at a tachi-owned installed path under the templates tree, written after the copy loop through the installer's containment and symlink guards; the README manual-install loop MUST write the same line; installs that skip it read `unknown` and the docs say so; the format MUST be coordinated with #369; no release-please configuration change.
  - AC: **Given** an installer-based install, a manual-loop install and an install that skipped the line, **When** a threat model is written, **Then** `tachi_version` reads the recorded version, the recorded version, and `unknown` respectively.
- **FR-021** (PRD FR-19): The schema surfaces MUST be reconciled in lock-step (the installed output schema, the output-schemas template, its checklist, the SARIF spec, and any other declaration the plan audit finds, such as the orchestrator template comment and the SARIF generator constant), the de-facto frontmatter keys documented, then the schema bumped additively to 1.5 with `tachi_version` written by a deterministic idempotent step from the marker or as `unknown`; parsers stay unchanged (a static contract test proves it); consumers are told to feature-detect the field and to treat the schema version in pre-1.5 files as declared, not ordinal; example baselines stay at their current version with the two drifted examples corrected per the PM ruling; any edit to the system-design README regenerates the init-baseline fixture in the same commit.
  - AC: **Given** the change, **When** the byte-identity checks run, **Then** no new failures appear against the pre-change state and no example is regenerated for the new field.
  - AC: **Given** the schema documentation, **When** a consumer reads it, **Then** the feature-detection and declared-not-ordinal guidance is present.

**Wording rules (all stories)**
- **FR-022** (PRD D-2, DoD 4): Every artifact on the Wording Rules surface MUST pass the Pattern A sweep with zero hits and MUST have a recorded disposition for every Pattern B hit.
  - AC: **Given** the surface, **When** the sweep runs, **Then** Pattern A has zero hits and every Pattern B hit is reworded or recorded as a technical use.

### Key Entities *(include if feature involves data)*

- **Egress profile**: the exhaustive list of external hosts a tachi run can reach, with the condition for each, and Claude Code's own operational traffic named separately.
- **Permission matrix**: one row per tachi agent and per command: tier, tools, model, command families, write locations, hosts, enforcement status, child processes.
- **Session profile**: one configuration file applied at launch; merge-not-replace with built-in defaults; checked as an effective configuration.
- **Live-validation record**: configurations run, probes, platforms, Claude Code version, permission mode, date, denials observed.
- **Run archive**: the verbatim copied transcripts, metadata and tool results for one session, owner-only, outside committable paths, marked sensitive.
- **Run manifest**: the structured summary of a run (fields in FR-018), with its schema document.
- **Version marker**: the one-line installed record of the tachi release, written by the installer or the manual loop.
- **Sweep record**: the Pattern A and Pattern B results with dispositions.
- **Trip-wire**: a pre-declared condition (TW-0, TW-A1..A3, TW-B0..B4) that triggers a cut or an honest stop.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (PRD SC-A1): A full run, with and without the key, completes in a scratch adopter project under the session profile on each platform the runbook header names: the probe table and the FR-010 probes pass, auto mode works with non-essential traffic off (or the pre-ruled fallback is recorded), and there are zero unexpected egress denials; stamped with Claude Code version, operating system, permission mode and date.
- **SC-002** (PRD SC-A2): Zero data-locality claims without the D-3 sentence in the six documents; PRD-054, PRD-060 and ADR-014 excluded by name as immutable records; evidenced by the sweep record.
- **SC-003** (PRD SC-A3): The guard fails on a synthetic tool addition or removal, model change, added frontmatter key or command-frontmatter change on any agent, and on the three roster negative cases; passes on the unchanged tree; exercises its self-test red path on every run; runs on pull requests and on pushes to the default branch.
- **SC-004** (PRD SC-A4): Every documented install or repair path yields agents whose declared tools match the matrix, asserted in the install-fidelity harness.
- **SC-005** (PRD SC-A5): A full run writes only under the output directory and the per-user temporary directory (carve-out excepted); the installed templates tree is byte-unchanged, including with a custom report configuration.
- **SC-006** (PRD SC-B1, gated): 100% of assistant turns classified (served or synthetic) per recorded subagent instance by agent name; metadata and line-level names agree; each planted denial kind detected; non-zero exit on unparseable structure or an empty histogram.
- **SC-007** (PRD SC-B2, gated): A destination inside any git work tree is refused unless ignored; owner-only modes; no planted key in the manifest; a scan hit writes no manifest.
- **SC-008** (PRD SC-B3, gated): `tachi_version` equals the installer's recorded version (or `unknown`), written deterministically; the schema change is additive; no new byte-identity failures against the pre-change state (the six pre-existing reds excepted).
- **SC-009** (Wording Rules): Pattern A sweep has zero hits on the surface; every Pattern B hit has a recorded disposition.

## Assumptions & Dependencies

- The key-handling patch merges before the build branches (T0); Part A's key text sits on top of it, and the image client form is pinned before the live validation.
- #364 gates the next minor release; Part A may ship alone as a patch under the TW-A2 ruling; Part B ships as a minor after #364.
- #374 overlaps Part B on the output-schemas reference; whichever merges second rebases; any new shell-invoked script changes matrix rows.
- #369: workflow anchor edits never run concurrently, and the version-marker format is coordinated.
- #365 hygiene: scratch clones for any check that runs the test suite or the extractors; a working-tree status check after agents return.
- Claude Code sandbox, auto-mode, launch-profile and retention settings behave as the public documentation described on 2026-11-16; minimum Claude Code version v2.1.285; the runbook records the version it was validated against.
- Anthropic's own transcript-review guidance is not yet published; no review automation is built.
- The maintainer launches the live-validation session; the OpenClaw Phase B run is an optional lagging confirmation, not the gate.

## Out of Scope

Transcript review automation beyond the manifest; shipping settings or auto-mode configuration to adopters; a process-level boundary (container, VM, sandbox runtime), which the mapping only points to; the key-handling patch itself; scope-as-intent blocks in agents (#360); a preflight command and a no-image flag (ideas); changing the agents' model pins (D-1); the adapter roster refresh (#369); SARIF tool version; correcting published copies of the old data-locality claim outside this repository (C-9, maintainer action recorded in `delivery.md`); any wording that fails the Wording Rules.
