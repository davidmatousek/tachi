# ADR-049: Privilege Contract and Write Confinement for tachi Agents

**Status**: Accepted
**Date**: 2026-11-19
**Deciders**: Architect (owner), Product Manager, Team-Lead
**Feature**: [391-isolated-auditable-operation](../../../specs/391-isolated-auditable-operation/spec.md) (FR-007, FR-008, FR-011 to FR-015, FR-020, FR-021)
**Supersedes**: None
**Superseded by**: None
**Related ADRs**: [ADR-041](ADR-041-claude-permissions-baseline.md) (governs this repository's development-time settings; this ADR adds the adopter-facing matrix to the same standard), [ADR-019](ADR-019-shared-definitions-and-model-field-governance.md) (the `model: sonnet` pins, left unchanged), [ADR-014](ADR-014-gemini-api-optional-image-generation.md) (the optional Gemini host that the Hosts column names), [ADR-022](ADR-022-mmdc-hard-prerequisite.md) (`mmdc`, the renderer child that the write rules cover), [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (the byte-identity suites that show a relocation moves no deliverable)

---

## Context

tachi ships 21 agents and 6 commands. Until this decision nothing stated in one place what they may do, and nothing checked it. Agent frontmatter lists `tools:` and `model:`, and Claude Code applies the tools list at run time, but a pull request could add `Bash` to a read-only agent, add a key such as `permissionMode` or `hooks`, or add an agent file, and no check would notice. The commands declare only a `description`. An operator who wanted to run tachi inside a Claude Code sandbox had no authoritative list of what a run does.

A trace of every agent, command, skill reference and invoked script ([audit](../../../specs/391-isolated-auditable-operation/contracts/audit-write-set.md)) found five kinds of write outside a run's output directory and the temporary directory:

- The report assembler overwrote the installed `templates/tachi/security-report/report-config.typ` and left `report-data.typ` in the installed tree after a failed compile.
- The infographic extraction wrote JSON to `/tmp`, and nothing pinned where the Gemini request, response and decoded image went, so a path the model built could fall back to `/tmp`.
- The report extractor wrote attack-tree and attack-chain PNGs and corrected image copies beside its input, not its output.
- `/tachi.risk-score` rewrote the input `threats.md`, and the risk scorer's text said to write beside the input although the command passed an output directory.
- CPython cached the imported `tachi_parsers` module as bytecode, in `scripts/__pycache__/` or under the interpreter's cache prefix.

The sandbox's default writable set is the working directory and a per-user temporary directory. A write to `/tmp` falls outside it, so it fails or needs an `allowWrite` entry, which the runbook's session profile deliberately never grants. Writes into the installed tree persist between runs: a custom `report-config.typ` carried into later reports, and a kept `report-data.typ`, which holds content derived from the findings, sat where an adopter could commit it.

The audit also found a dispatch defect. `/tachi.security-report` started `senior-backend-engineer` and told it to follow the report assembler's instructions. That agent belongs to the repository's own development tooling, `scripts/install.sh` does not ship it, and its definition declares no `tools:`.

## Decision

Ten decisions follow. D1 to D4 cover the privilege contract, D5 to D8 write confinement, D9 the dispatch fix, and D10 the version stamp, which is marked "if shipped" because it applies only when that work ships.

### D1: A standard-library guard checks the privilege matrix in CI (AD-3, AD-8)

Section 8 of [`docs/standards/CLAUDE_PERMISSIONS.md`](../../standards/CLAUDE_PERMISSIONS.md#8-agent-and-command-privilege-matrix) is the one statement of what each tachi agent and command can do. Its agents table gives each agent's tier, `tools:`, `model:`, shell command families, writes and hosts. Its commands table gives each command's frontmatter keys, dispatches, instructed shell, writes and child processes. §8 is appended after §7 and no earlier heading is renumbered or renamed, because the workflow greps the §3 and §4 headings byte for byte and the AC-2 cross-check script parses the range between §4 and §5.

`scripts/check-agent-privileges.py` (standard library only, Python 3.9 or later) compares the tables with the files and exits 1 on drift. It fails when:

- an agent's `tools:` set or `model:` value differs from its row;
- an agent's frontmatter key set is anything other than `{name, description, tools, model}`, so adding `permissionMode`, `mcpServers`, `hooks`, `disallowedTools` or any other key turns CI red;
- a command's frontmatter keys differ from the commands table (today `{description}`; a value for `allowed-tools` or `model` is recorded in §8 when a command sets one);
- a labeled shell fence in one of the three Bash-capable agents (`tachi-orchestrator`, `tachi-report-assembler`, `tachi-threat-infographic`) uses a command family outside that agent's Bash families cell. Command substitution, backticks, `eval`, `bash -c`, `sh -c` and `xargs` are red, with no allow-list for them, and prose is never scanned;
- the runbook's write-locations table differs from the Writes cells of §8;
- the roster rule in D2 fails.

The guard runs as a step of `tachi-permissions-verify.yml` on pull requests and on pushes to the default branch. The workflow's path anchor gains the agents directory, the tachi commands, the guard script and the runbook. The guard's red cases are a pytest module in the `tachi-pytest.yml` run list. An assertion in the install-fidelity suite checks that the agents an install produces carry the §8 tools sets, so the contract covers what adopters receive as well as the source tree.

`--self-test` copies the tree to a temporary directory, applies five mutations (a tool added to one agent, a planted agent named `helper`, an unlisted file with no frontmatter, a duplicate agent name, and the allow-listed document with frontmatter planted in it) and fails unless each is caught. CI runs it every time, so the guard cannot stop detecting without turning red.

The guard does not check Tier, Hosts, Dispatches, the shell a command instructs, or Child processes (D3).

### D2: The roster rule runs in both directions (AD-8)

The guard walks `.claude/agents/tachi/` recursively and classifies each file:

- A file with leading YAML frontmatter, detected leniently (a byte-order mark, blank lines and CRLF line endings are tolerated), is an agent. Its `name:` must start with `tachi-` and be unique, and §8 must have a row for it.
- `_TACHI_AGENT_BEST_PRACTICES.md` is the one allow-listed non-agent document, and only while it has no leading frontmatter. If it gains frontmatter it is classified as an agent and fails for lack of a row.
- Anything else is red: a symlink at any depth, a non-Markdown file that git tracks, and any other Markdown file without frontmatter. An untracked file such as `.DS_Store` is ignored.

Every agent row in §8 must also have a file. The first direction catches a planted or renamed agent that has no row. The second catches a deleted agent whose row stays behind, which would leave a matrix that looks complete and describes something that is not installed. Allow-listing a name only while it has no frontmatter stops the exempt filename from carrying an agent definition.

### D3: Tools are enforced, the model pin applies by default, the rest is declared (AD-1)

§8.1 states, above the tables, what Claude Code enforces and what is a declaration.

- **Enforced: `tools:`.** The list is an allowlist that Claude Code applies to the subagent. An agent that holds only `Read`, `Glob` and `Grep` can neither write a file nor run a command.
- **Applies by default: `model:`.** An agent's `model:` applies unless the invocation passes a `model` parameter, which takes precedence. No tachi command passes one. `CLAUDE_CODE_SUBAGENT_MODEL` ranks below both, so setting it alone does not change a tachi agent's model, and only `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (Claude Code v2.1.257 or later) overrides them. The Model column records the pin, not the model that served a request. An organization's model allowlist and Claude Code's model fallback can run a request on another model, and Claude Code's session transcripts record the model that served each turn. The pins stay `sonnet`, and this decision changes none.
- **Declared, not enforced:** the Bash families, Writes and Hosts columns, and everything the commands table records as instructed (Dispatches, shell, Writes, Child processes). These declare what an agent's or a command's instructions do; they do not bound a run. The adopter's sandbox bounds where any command can write and connect, not which commands run; the Tools column bounds only which tools an agent holds. Commands declare no `allowed-tools`, so they run in the main session with that session's tools and permission rules.

CI checks that the declarations match the files (D1). It cannot check that a run obeys them, so §8 says which columns are only declarations.

### D4: `Agent` is transitive, and §8 says so (AR-5)

An agent that holds `Agent` can start any subagent type available in the session: tachi's agents and Claude Code's built-in types such as `general-purpose`. A started subagent has the tools its own definition gives it, not the dispatcher's, so the Tools cell of an `Agent` holder understates what its run can do.

Two agents hold `Agent`. `tachi-orchestrator` starts the 14 threat agents and `tachi-threat-report`, and `tachi-threat-report` starts `tachi-attack-tree-delta`. In a [recorded run](../../../specs/391-isolated-auditable-operation/test-results/w0-spike.md), `tachi-threat-report` also started built-in `general-purpose` subagents that ran Bash and Write. No tachi file instructs this.

We declare the capability and do not guard it. §8's legend has a Dispatch paragraph with the declared targets and the observed behavior. The guard pins which agents hold `Agent`, so any other agent gaining the tool turns CI red (D1). It checks nothing about which types they start: the targets are written in prose, which the guard never scans, and no static check can bound a choice the model makes at run time. tachi does not restrict the types.

### D5: A run writes only under `{out}` and `$TMPDIR` (FR-007)

A tachi run writes only under its output directory, `{out}`, and the sandbox's per-user temporary directory, `$TMPDIR`. Python's `tempfile` and the `mmdc` and Chromium children write to `$TMPDIR`. The one exception is `/tachi.architecture`, which writes its own output file (by default `docs/security/architecture.md`, or the `--output` path) and an archive directory, `.archive/v{N}/`, beside it. §8 lists both. Given the precondition below, a sandboxed run needs no `allowWrite` entry. In the live validation on macOS, four of the five run commands ran under the session profile, which grants none, and wrote only under `{out}`; `/tachi.security-report` stopped before its build directory because Chromium could not start inside the sandbox, so its write set rests on the write-confinement test (Mitigation).

`{out}` is the run's output directory. For `/tachi.threat-model` it is `{output_dir}/{timestamp}/`, by default `docs/security/{timestamp}/`. For the other run commands it is the directory named by `--output-dir`, which defaults to the directory the command reads from.

The precondition: `{out}` lies under the working directory. `/tachi.security-report` enforces it in code (D6): the report is built under `{out}`, Typst's `--root .` must contain the build, and the extractor exits 2 for a build directory outside the working directory. The command's option text says so. For every other output path an adopter can set (`--output-dir` on the run commands, `--output` on `/tachi.architecture`) the condition is disclosed and not checked: outside the working directory a write needs an allowance that the session profile does not grant. `/tachi.security-report` also reads infographic images through Typst's root, so its target directory must lie under the working directory when images are present. That predates this decision.

### D6: The extractor owns the build directory and its own writes (AD-4 as amended by RC-T4; AR-1)

The report is compiled from a throwaway copy of the template, and `scripts/extract-report-data.py` manages that copy, not the agent:

- Run with `--target-dir {target_dir} --build-dir {out}/.tachi-build/security-report`, the extractor removes any stale build directory, copies `templates/tachi/security-report/` into it, copies `{target_dir}/report-config.typ` in when one exists, writes `report-data.typ` there and computes every relative path (images, brand assets) against it. The report assembler then runs `typst compile` on `{out}/.tachi-build/security-report/main.typ`, writing `{out}/security-report.pdf`, with `--root .`.
- After a successful compile, `--remove-build-dir {out}/.tachi-build/security-report` removes the build directory. After a failed compile it stays under `{out}` for debugging.
- Both flags run a path-shape guard and exit 2 when it fails. The real path of the build directory must lie under the real path of the working directory and end in `.tachi-build/security-report`. It must not be the working directory or a parent of it, must not be the templates directory and must not be a symlink.
- `templates/tachi/` is never written.
- In build mode every other extractor write also lands under `{out}`: attack-tree PNGs in `{out}/attack-trees/`, attack-chain PNGs in `{out}/attack-chains/`, and a corrected copy of an infographic image whose bytes do not match its extension, in `{out}`. `--target-dir` is only read. The opt-in `--cleanup-mislabeled-images`, which no run recipe passes, deletes a file only when it lies in `{out}`.

### D7: The write paths that agents choose are pinned under `{out}` (AR-2, AR-3)

Three places where an agent's text chose a path or left it open now pin one:

- **Risk scorer.** `tachi-risk-scorer` writes `risk-scores.md` and `risk-scores.sarif` to the output directory named in its prompt. `/tachi.risk-score` runs the in-place populate script on the input `threats.md` only when the output directory is the input directory. With another `--output-dir` the input directory stays read-only.
- **Infographic data.** The extraction writes `{out}/.tachi-build/infographic-{template}.json`, which was `/tmp/infographic-*.json` before, and keeps it.
- **Gemini files.** The request file is `{out}/.tachi-build/gemini-{template}-request.json`, written with the Write tool, and the response file is `{out}/.tachi-build/gemini-{template}-response.json`, written by `curl --output`. The instructions decode the image with `python3`, using the standard library, from the response file into `{out}/threat-{template}.{jpg,png}`. In the live validation the agent decoded each image with a `python3` heredoc, as the instructions say, but it built the specs and the Gemini request files with two helper scripts it wrote under `{out}/.tachi-build/`, so the request files did not come from the Write tool. Every write it made still landed under `{out}`: the pinned paths bound what the instructions say, not what the model does (D3). Both files are kept. The agent has no deletion command, the files are as sensitive as the rest of `{out}`, and the request file is the exact payload sent to the Gemini host. `$TMPDIR` was rejected for them: the file tools need a further permission outside the working directory, and a path the model builds can fall back to `/tmp`.

### D8: The installed scripts write no bytecode cache (AR-14)

Agents and commands run `extract-report-data.py`, `extract-infographic-data.py` and `populate-affected-assets.py`, and each imports `tachi_parsers` from its own directory, so CPython caches that module as bytecode, in `scripts/__pycache__/` or under the interpreter's cache prefix, both outside `{out}` and `$TMPDIR`. Each script sets `sys.dont_write_bytecode = True` under `if __name__ == "__main__":`, before that import. The guarantee lives in the script, so it holds for a paraphrased command and for a person running the script by hand. The interpreter's own standard-library cache lies outside the project and serves every Python program, so it is out of scope.

### D9: `/tachi.security-report` dispatches `tachi-report-assembler` (AD-13)

The command's dispatch step now reads `subagent_type: "tachi-report-assembler"`. The prompt is kept and the command's frontmatter is unchanged. The assembler declares `Read`, `Glob`, `Grep`, `Write` and `Bash`, and its body names no other tool, so those cover its steps. The defect predates this decision. §8's commands table records each command's target in a Dispatches column. The guard does not check that column; a check that command bodies dispatch only tachi agents with a §8 row is a follow-up.

### D10: `tachi_version` in `threats.md` (if shipped)

A `threats.md` declares a schema version, and nothing says which tachi release wrote it. The schema version cannot stand in for that: nothing kept the value in step with the schema file, so files with the same structure declare 1.4, 1.7 and 1.8. This decision records the release in the file without asking the model to write it.

- **Marker.** `templates/tachi/VERSION` is a tracked placeholder, `tachi_version: unknown`, so every copy path resets it. `scripts/install.sh` removes any existing marker before its copy loop. After the loop, inside its containment and symlink guards, it writes `tachi_version: <value>`, where the value is `git describe --tags --always --dirty` of the source clone after any `--version` checkout. A source with no git tree of its own gives `<release manifest version>-release-manifest`, and anything else gives `unknown`. The README's manual-install loop, and the two copies of it in the developer guide, write the same line from `git describe`, with `unknown` as their only fallback. An install that skips the line reads `unknown`.
- **Stamp.** `scripts/stamp-tachi-version.py` copies the marker's value into the frontmatter of `threats.md`, after `schema_version`. It is deterministic and idempotent, and a missing or malformed marker stamps `unknown`. `/tachi.threat-model` runs it as Step 2.6, after the populator re-assert and before it reports results, so the orchestrator's instructions are unchanged and the model never writes the field.
- **Schema 1.5.** `schemas/output.yaml` is the single source of the schema version, and the output template, the output-schemas reference and the SARIF specification now agree with it. Version 1.5 is additive: it declares the six frontmatter keys that producers already wrote (`run_id`, `baseline`, `coverage_gate`, `has_attack_chains`, `has_agentic_patterns` and `has_source_attribution`) and adds `tachi_version`. Parsers are unchanged, and a contract test shows it. Consumers feature-detect `tachi_version` and treat `schema_version` in a file older than 1.5 as declared, not ordinal.
- **What is not written.** The stamp step writes `tachi_version` and no other key. Writing `schema_version` from `schemas/output.yaml` into the tracked outputs was measured and turns five infographic golden files red, so `schema_version` stays model-authored and declared-only, as the schema documents say. The SARIF generator takes `semanticVersion` from the input file's own `schema_version` and falls back to `schemas/output.yaml`, so a regenerated SARIF file agrees with the frontmatter of the file it was generated from. Two tracked SARIF files do not: `examples/agentic-app/sample-report/threats.sarif` says 1.7 for an input that declares 1.4, and `examples/consumer-agent-app/sample-report/threats.sarif` keeps 1.8 when its input is corrected to 1.4. They stay as they are, because this feature moves no tracked SARIF baseline; correcting them is a follow-up.

## Alternatives Considered

### Alternative 1: Document the stray writes instead of relocating them

**Pros**: no change to agents, the extractor or their tests.

**Cons**: a sandboxed session would need `allowWrite` entries, which the session profile names as a weakening and never sets, or the run would fail. Shared `/tmp` names are predictable and symlink-prone, and the default file mode can expose content on a multi-user host. `report-config.typ` would keep persisting across reports.

**Why Not Chosen**: FR-007 and FR-008 require the relocation, and the confinement rule in D5 holds only if nothing is left to document.

### Alternative 2: Manage the build directory from the agent's recipe

The plan's first mechanism had the report assembler remove, create and copy into the build directory with shell commands.

**Pros**: no change to the extractor.

**Cons**: the recipe needs a deletion command, which the repository's deny rules block, and a deletion family would widen the assembler's Bash families, which D1 pins at `python3`, `test` and `typst`. The path check would live in prose, where no test can reach it.

**Why Not Chosen**: the architect amended the mechanism when the tasks were generated (RC-T4). `--build-dir` and `--remove-build-dir` hold the lifecycle and the path-shape guard in code that a test exercises.

### Alternative 3: A pytest-only guard, or a new workflow

**Pros**: pytest is the repository's usual test runner, and a new workflow could carry its own path anchor.

**Cons**: `tachi-permissions-verify.yml` already runs on pull requests and on pushes to the default branch from one path anchor with a read-only token, and it has no Python test runner. A pytest module there would go ungated, because `tachi-pytest.yml` runs an explicit module list, or would pull pytest into that job. A second workflow would repeat the anchor.

**Why Not Chosen**: a standard-library script that the existing job calls directly needs neither. The guard's red cases are still a pytest module, in the pytest workflow.

### Alternative 4: Change the model pins, or bound what `Agent` can start

**Pros**: an `inherit` pin or an installer `--model` flag would let an operator choose the model for every agent. Bounding the types an `Agent` holder may start would close the gap that D4 declares.

**Cons**: a pin change alters the model the agents run on and needs an output-quality and refusal-behavior evaluation first. The `Agent` targets are written in prose, and no static check can bound a choice made at run time.

**Why Not Chosen**: the pins are kept deliberately (the dated Note on ADR-019), and any change to them is a separate ADR-019 amendment. D4 declares the transitivity instead.

### Alternative 5: Suppress bytecode through the invocation, or disclose it

**Pros**: no edit to the scripts.

**Cons**:

- `python3 -B` in the recipes is ten fenced lines in seven files, two of them inside dispatch prompts. It holds only while every agent and session copies the flag, and it misses a person running a script by hand.
- `PYTHONDONTWRITEBYTECODE=1` in the session profile's `env` covers only sessions started with the profile, and it adds a key to the profile's closed key set.
- Disclosure puts a qualifier on the confinement rule. No fixed row can name a location that depends on the interpreter, and in an adopter's project the cache appears as untracked files in a `scripts/` directory that the adopter may share.

**Why Not Chosen**: D8 puts the guarantee in the script, so it holds for every invocation form.

## Consequences

### Positive

- Privileges are reviewable in one place, and drift fails CI on pull requests and on direct pushes to the default branch. A change to a tool list, a model pin, a frontmatter key or the agent roster cannot ride along in an unrelated pull request: it fails until §8 changes in the same one, which puts it in front of a reviewer.
- The write footprint is two locations and one named exception, so the runbook can say that a sandboxed run needs no `allowWrite` entry.
- The installed templates tree is never written. A custom `report-config.typ` no longer persists into later reports, and a failed compile leaves `report-data.typ` under `{out}`.
- Deliverables do not move. Only intermediates changed location, which the byte-identity suites (ADR-021) check.

### Negative

- Every change to an agent's tools, model or fenced shell families needs a §8 edit in the same pull request. §8's tables are a parsed format, with the cell syntax pinned in §8.2.
- The guard compares files with tables and does not observe a run. A declared column can be wrong without CI noticing (D3), and a command that a model builds at run time is invisible to the fence scan.
- `/tachi.security-report` now exits 2 when `{out}` lies outside the working directory. The command's option text and the runbook disclose it.
- Intermediates are kept inside `{out}`: `.tachi-build/` holds the infographic JSON, the Gemini request and response files and, after a failed compile, the report build directory, all as sensitive as the rest of `{out}`. This repository's `.gitignore` ignores `.tachi-build/`. `scripts/install.sh` writes no `.gitignore` into an adopter's project, so an adopter who commits run output must ignore it too.

### Mitigation

- `--self-test` runs on every CI run (D1).
- A write-confinement test hashes the installed templates tree before and after a build and lists every new path, and each must lie under `{out}` or `$TMPDIR`. It also covers the extractor's image writes (D6) and the bytecode guard (D8). It runs in the install-fidelity workflow's Typst-gated job, which fails rather than skips when Typst is missing.
- No automated test pins the paths that agents write (D7). The live validation on macOS (2026-11-20) hashed every file and directory in the scratch project except `.git/` before and after three runs (the key-less pipeline, a `/tachi.risk-score --output-dir` run and the keyed pipeline): every path tachi wrote lay under the run's output directory, nothing under `templates/tachi/` changed and no `__pycache__` appeared, and the only other new paths were two empty `.claude/.cc-writes/` directories that Claude Code itself creates; `/tachi.security-report` did not reach its build directory there, so its writes rest on the test above.

## Known limitations

1. **Skills' `allowed-tools` and `model` are an unguarded privilege surface.** The guard reads agent and command frontmatter and does not read skill frontmatter. None of the seven `.claude/skills/tachi-*/SKILL.md` files sets `allowed-tools`, `model` or `tools` today (each declares only `name` and `description`), so nothing is hidden now. A skill that set one would change what a run can do without turning CI red. Extending the guard to skill frontmatter is a follow-up.
2. **The matrix link in the runbook is pinned to a release and lags `main`.** `docs/standards/CLAUDE_PERMISSIONS.md` is not installed. The installed runbook links to §8 at a URL pinned to the release, and the version in that link moves with each release. An install from `main` after a release therefore links to the previous release's matrix, which can differ from the agents it installed. Before the first release that carries §8, no tagged matrix exists and the link does not resolve. The runbook says so beside the link.
3. **Command frontmatter is declared-only until `allowed-tools` and `model` are set.** Each command declares only `description`, so it runs in the main session with that session's tools and permission rules. Its Dispatches, shell, Writes and Child processes entries in §8 record what the command text instructs, and Claude Code enforces none of them. The guard pins the key set, so adding `allowed-tools` or `model` is a change that must update §8.
4. **`tests/scripts/test_coverage_attestation.py` is ungated.** No workflow runs it. The report relocation edits it (its stale-data swap moves to the build-directory location), so a regression in it would not turn CI red. It is run by hand in a scratch clone before delivery.
5. **The adapter copies carry no `tools:` or `model:` and are out of scope.** The 15 files under `adapters/claude-code/agents/` declare only `name` and `description`, and six agents have no copy there. By Claude Code's documentation, a subagent definition without `tools` inherits every tool available to subagents, and one without `model` runs on the model of the conversation that starts it unless `CLAUDE_CODE_SUBAGENT_MODEL` is set. The guard does not cover the copies, and the repair path is `scripts/install.sh`. Refreshing the adapter roster is tracked in #369.
6. **A downgrade made with an installer from before this feature cannot reset the version marker.** Any install from a source that ships the `templates/tachi/VERSION` placeholder resets the marker, and the current installer also rewrites it after the copy, including for a `--version` tag that is older than the placeholder. An installer from before Feature 391 knows nothing of the file. Checking out an older release in the tachi clone and running that clone's installer replaces the agents and commands and leaves the newer marker in the project, where it names a version that the installed agents do not match (the older `/tachi.threat-model` has no Step 2.6, so it does not stamp that value). Delete `templates/tachi/VERSION` after such a downgrade (the marker then reads `unknown`), or downgrade with a current installer's `--version` option.

## Cross-references

- Feature 391: [spec](../../../specs/391-isolated-auditable-operation/spec.md) (FR-007, FR-008, FR-011 to FR-015, FR-020, FR-021) and [plan](../../../specs/391-isolated-auditable-operation/plan.md) (AD-1, AD-3, AD-4 as amended, AD-7, AD-8, AD-11, AD-13)
- Contracts: [audit-write-set.md](../../../specs/391-isolated-auditable-operation/contracts/audit-write-set.md), [cli-contracts.md](../../../specs/391-isolated-auditable-operation/contracts/cli-contracts.md) (the guard and the extractor flags), [matrix-section.md](../../../specs/391-isolated-auditable-operation/contracts/matrix-section.md)
- Version stamp (D10): the contract [version-marker.md](../../../specs/391-isolated-auditable-operation/contracts/version-marker.md) and the schema [measurement](../../../specs/391-isolated-auditable-operation/test-results/t038a-measurement.md)
- Records: [w1-audit-rulings.md](../../../specs/391-isolated-auditable-operation/test-results/w1-audit-rulings.md) (AR-1 to AR-14), [profile-prestage.md](../../../specs/391-isolated-auditable-operation/test-results/profile-prestage.md) (model selection), [w0-spike.md](../../../specs/391-isolated-auditable-operation/test-results/w0-spike.md) (the recorded run in D4)
- [`docs/standards/CLAUDE_PERMISSIONS.md`](../../standards/CLAUDE_PERMISSIONS.md) §8, and the installed runbook [`docs/guides/ISOLATED_OPERATION_TACHI.md`](../../guides/ISOLATED_OPERATION_TACHI.md) (its section 5 repeats the write locations)
- Claude Code documentation: [subagents: restrict which tools a subagent can use](https://code.claude.com/docs/en/sub-agents#restrict-which-tools-a-subagent-can-use), [subagents: choose a model](https://code.claude.com/docs/en/sub-agents#choose-a-model), [model configuration: environment variables](https://code.claude.com/docs/en/model-config#environment-variables)
