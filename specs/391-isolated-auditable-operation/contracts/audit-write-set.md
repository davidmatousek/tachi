# Write-set and privilege audit (T004)

| Item | Value |
|---|---|
| Feature | 391 Isolated and Auditable Operation, Part A, lane E |
| Task | T004 (feeds T012, T013, T014, T016, T023, T025 C7, T040) |
| Audited tree | commit `46aec8d`, the post-T0 Part A tree. Every `file:line` below cites that commit. Later commits on the branch touch planning records only, so no audited file has drifted. Lane D's uncommitted T014 edits to `scripts/extract-report-data.py` are not reflected |
| Date | 2026-11-19 |
| Method | Read-only trace: 21 agents, 6 commands, the skills they Read, the four scripts they invoke, and the `typst`, `mmdc` and `curl` children. Nothing was run. The Bash families in section 3.2 were derived by hand from the T025 tokenizer rules (`contracts/cli-contracts.md`, C6); T025's implementation is the authority and should reproduce them |
| Not covered | Runtime-only behaviour (what Chromium writes into the temp directory, which tool the infographic agent picks to decode an image, where the built-in subagents seen in the W0' run wrote). T020's write listing is the runtime check for those |

## 1. Result in brief

- **Agents**: 21 audited. All carry exactly the key set `{name, description, tools, model}` and `model: sonnet`. Tool sets: 14 read-only agents with `{Read, Glob, Grep}`; four writers; three Bash-capable agents. One further file, `_TACHI_AGENT_BEST_PRACTICES.md`, has no leading frontmatter (the C1 allow-list case). The agents directory holds no symlink and no non-`.md` file.
- **Commands**: 6 audited. All carry exactly `{description}`: no `allowed-tools`, no `model`. Five dispatch an agent: four a tachi agent, and `/tachi.security-report` (`tachi.security-report.md:162`) a non-tachi agent. `/tachi.architecture` dispatches nothing.
- **Dispatch**: two agents hold `Agent` (`tachi-orchestrator`, `tachi-threat-report`). One tachi file names a non-tachi agent: `tachi.security-report.md:162`.
- **Hosts**: the model provider for everything, plus one more host, `generativelanguage.googleapis.com`, used only by `tachi-threat-infographic` when a key is set. None of the four scripts imports a network module, and the Typst templates import no registry package.
- **Writes**: 27 write rows in section 5. 24 survive relocation (`both` or `post only`); 3 disappear (`pre only`). Not every post-relocation write sits under `{out}`: the report extractor writes into `{target_dir}` (D-2), and `/tachi.risk-score` writes beside its input (D-3).
- **Discrepancies**: 13 in section 7 (1 known and planned, 12 new). Four need an Architect decision (D-2, D-3, D-4, D-6); the first three change what T016 may say about write confinement.

| Consumer | Take from |
|---|---|
| T012, T013, T014 (SBE-D) | 3.2, 5 (rows marked `pre only` and `post only`), 7 (D-4, D-10, D-11, D-12) |
| T016 runbook section 5 (DEVOPS-R) | 2, 5 (rows marked `both` and `post only`), 6, 7 (D-2, D-3, D-9) |
| T023 section 8 (SBE-E) | 2, 3.1, 4.1, 7 (D-5, D-6, D-7, D-8, D-13) |
| T025, T026 (C6, C7) | 3.2, 2 (cell syntax), 7 (D-5, D-7) |
| T040 architect checkpoint | 7 (every Medium row) |

## 2. Notation

Path tokens (a closed set; use them verbatim in section 8 and the runbook so C7 can compare):

| Token | Meaning |
|---|---|
| `{out}` | The run's output directory: the command's `output_dir` (the report assembler calls it `{output_path}`). For `/tachi.threat-model` it is `{output_dir}/{timestamp}/`, default `docs/security/{timestamp}/` |
| `{target_dir}` | The directory a command reads pipeline artifacts from. Each command names it differently: `{target_dir}` (`/tachi.security-report`), `{input_dir}` (`/tachi.risk-score`, `/tachi.compensating-controls`), `{data_source_dir}` (`/tachi.infographic`). It equals `{out}` unless `--output-dir` is passed. `/tachi.threat-model` has no such directory |
| `$TMPDIR` | The sandbox's per-user temporary directory. Python's `tempfile` resolves `TMPDIR`, `TEMP`, `TMP`, then the system temp directories, and as a last resort the working directory |
| `{arch_path}`, `{arch_dir}` | `/tachi.architecture` only: its output file (default `docs/security/architecture.md`, or `--output <path>`) and the directory containing it |
| `{template}`, `{stem}`, `{finding-id}`, `{chain-id}`, `{N}` | Placeholders filled at run time |

Braces without a comma are placeholders. Braces with a comma, such as `{jpg,png}`, are alternatives and expand to one path each. T023 pins the final cell syntax; this file uses comma-separated, backticked values.

Column conventions proposed for T023 (it owns the final pin):

- **Tools**: a set, listed in the order `Read, Glob, Grep, Write, Bash, Agent`.
- **Bash families**: the first tokens that C6 extracts from labelled fences, sorted; `-` for none. Commands the agent runs without a fence are declared in a separate note, not in this column (D-7).
- **Writes**: paths from section 5's Path column, `;`-separated.
- **Phase** (section 5): `both` (written before and after relocation), `post only` (introduced by T012, T013 or T014), `pre only` (removed by them).

## 3. Agents

### 3.1 Candidate rows for section 8 (post-relocation)

Tier: `read-only`, `writer`, `Bash` (highest wins). "Dispatches" is not a column in `contracts/matrix-section.md`; it is proposed here because `Agent` is transitive (D-6).

| Agent | Tier | Tools | Model | Bash families | Writes | Hosts | Dispatches |
|---|---|---|---|---|---|---|---|
| `tachi-agent-autonomy` | read-only | Read, Glob, Grep | sonnet | - | - | model provider | none |
| `tachi-attack-tree-delta` | writer | Read, Glob, Grep, Write | sonnet | - | `{out}/attack-trees/` | model provider | none |
| `tachi-control-analyzer` | writer | Read, Glob, Grep, Write | sonnet | - | `{out}/compensating-controls.{md,sarif}` | model provider | none |
| `tachi-data-poisoning` | read-only | Read, Glob, Grep | sonnet | - | - | model provider | none |
| `tachi-denial-of-service` | read-only | Read, Glob, Grep | sonnet | - | - | model provider | none |
| `tachi-human-trust-exploitation` | read-only | Read, Glob, Grep | sonnet | - | - | model provider | none |
| `tachi-info-disclosure` | read-only | Read, Glob, Grep | sonnet | - | - | model provider | none |
| `tachi-misinformation` | read-only | Read, Glob, Grep | sonnet | - | - | model provider | none |
| `tachi-model-theft` | read-only | Read, Glob, Grep | sonnet | - | - | model provider | none |
| `tachi-orchestrator` | Bash | Read, Glob, Grep, Write, Bash, Agent | sonnet | `python3` | `{out}/threats.md`; `{out}/threats.sarif`; `{out}/attack-chains.md` | model provider | the 14 threat agents and `tachi-threat-report` (declared); any subagent type (reach) |
| `tachi-output-integrity` | read-only | Read, Glob, Grep | sonnet | - | - | model provider | none |
| `tachi-privilege-escalation` | read-only | Read, Glob, Grep | sonnet | - | - | model provider | none |
| `tachi-prompt-injection` | read-only | Read, Glob, Grep | sonnet | - | - | model provider | none |
| `tachi-report-assembler` | Bash | Read, Glob, Grep, Write, Bash | sonnet | `python3`, `test`, `typst` | `{out}/security-report.pdf`; `{out}/.tachi-build/security-report/`; `{target_dir}/attack-trees/`; `{target_dir}/attack-chains/`; `{target_dir}/threat-{stem}.{jpg,png}`; `$TMPDIR` | model provider | none |
| `tachi-repudiation` | read-only | Read, Glob, Grep | sonnet | - | - | model provider | none |
| `tachi-risk-scorer` | writer | Read, Glob, Grep, Write | sonnet | - | `{target_dir}/risk-scores.{md,sarif}` (equals `{out}` unless `--output-dir`; D-3) | model provider | none |
| `tachi-spoofing` | read-only | Read, Glob, Grep | sonnet | - | - | model provider | none |
| `tachi-tampering` | read-only | Read, Glob, Grep | sonnet | - | - | model provider | none |
| `tachi-threat-infographic` | Bash | Read, Glob, Grep, Write, Bash | sonnet | `[`, `echo`, `python3`, `test` | `{out}/threat-{template}-spec.md`; `{out}/threat-{template}.{jpg,png}`; `{out}/.tachi-build/infographic-{template}.json`; Gemini request and response files (location not pinned; D-4) | model provider; `generativelanguage.googleapis.com` when `GEMINI_API_KEY` is set | none |
| `tachi-threat-report` | writer | Read, Glob, Grep, Write, Agent | sonnet | - | `{out}/threat-report.md` | model provider | `tachi-attack-tree-delta` (declared); any subagent type (reach); three built-in `general-purpose` instances observed |
| `tachi-tool-abuse` | read-only | Read, Glob, Grep | sonnet | - | - | model provider | none |

Frontmatter anchors, all at `46aec8d`: the 14 read-only agents carry `tools:` on lines 4-7 and `model:` on line 8; `attack-tree-delta`, `control-analyzer` and `risk-scorer` carry `tools:` on 4-8 and `model:` on 9; `report-assembler`, `threat-infographic` and `threat-report` carry `tools:` on 4-9 and `model:` on 10; `orchestrator` carries `tools:` on 4-10 and `model:` on 11.

### 3.2 Bash families on the live tree (C6 inventory)

Only the three Bash-capable agents are in C6's scope. Labelled shell fences (`bash`, `sh`, `shell`, `zsh`; indented fences included) at `46aec8d`:

| Agent | Fence | Segments after joining `\` continuations and splitting | Family |
|---|---|---|---|
| `orchestrator.md` | `bash`, L684-688 | `python3 scripts/populate-affected-assets.py --architecture <output_dir>/architecture.md --threats <output_dir>/threats.md` | `python3` |
| `report-assembler.md` | `bash`, L124-126 | two `test -f` segments split on `&&` | `test` |
| `report-assembler.md` | `bash`, L157-163 | one `python3 scripts/extract-report-data.py ...` segment; the `[--title ...]` line is a continuation | `python3` |
| `report-assembler.md` | `bash`, L194-196 | `typst compile ... --root .` | `typst` |
| `threat-infographic.md` | `bash`, L144-146 | two `test -f` segments split on `&&` | `test` |
| `threat-infographic.md` | `bash`, L166-171 | `python scripts/extract-infographic-data.py ...` | `python` (becomes `python3` in T013) |
| `threat-infographic.md` | `bash`, indented 3, L347-349 | three segments after splitting on `;`: `if [ -z "${GEMINI_API_KEY:-}" ]`, `then echo "..."`, `fi` (the reserved words `if`, `then` and `fi` are skipped) | `[` and `echo`; the `fi` segment yields none |

Resulting live-tree sets: orchestrator `{python3}`; report-assembler `{python3, test, typst}`; threat-infographic `{[, echo, python, test}`. After T012 the report-assembler set is unchanged (the three new agent commands are `python3`, `typst`, `python3`, plus the `test` preflight). After T013 the infographic set is `{[, echo, python3, test}`. The `w0-prestate.md` list omits `echo` (D-5).

Out of C6's scope, by rule:

- Unlabelled fences: `orchestrator.md` L101-105; `report-assembler.md` L71-73, L130-149, L220-224; `threat-infographic.md` L150-162. None holds a command (a data-flow diagram, error-message text, and the input-boundary example at `orchestrator.md:101-105`).
- The 14 read-only agents have only `yaml` fences.
- Two labelled shell fences exist in tachi skills, both outside the agent files: `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md:255-264` (the pinned `curl` with a heredoc) and `.claude/skills/tachi-report-assembly/references/typst-artifacts.md:118-124` (the extractor with `--cleanup-mislabeled-images`). No other `bash|sh|shell|zsh` fence exists in any `tachi-*` skill (D-7).

Commands the Bash-capable agents are told to run without a labelled fence (declared-only, invisible to C6):

| Agent | Where | What | After relocation |
|---|---|---|---|
| `report-assembler` | `:113-115` (Step 2a) | copy a custom `report-config.typ` over the installed default; no command named | gone: the extractor copies it into the build directory |
| `report-assembler` | `:216` (Step 3d) | delete `report-data.typ`; no command named | gone: `--remove-build-dir` |
| `report-assembler` | `:211` (Step 3c) | check the PDF exists and is non-empty; no command named | unchanged (`test` is in the set, or Read and Glob suffice) |
| `threat-infographic` | skill reference `:255-264` | `curl` to the Gemini host, key via `--config -` from the environment | unchanged; family `curl`, declared in the skill reference |
| `threat-infographic` | skill reference `:297-303` | decode the base64 image and save it; no tool named | unchanged; tool unspecified |

### 3.3 Dispatch capability

Only two agents hold `Agent`; the other 19 can dispatch nothing.

| Dispatcher | Declared targets | Anchor | Observed in the W0' run |
|---|---|---|---|
| main session via `/tachi.threat-model` | `tachi-orchestrator` | `tachi.threat-model.md:108` | depth 1 |
| `tachi-orchestrator` | six STRIDE agents (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation); eight AI agents (prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse, human-trust-exploitation, output-integrity, misinformation); `tachi-threat-report` | `orchestrator.md:31-48`, `:770-785` | six STRIDE agents and `tachi-threat-report` at depth 2 (the input had no AI components) |
| `tachi-threat-report` | `tachi-attack-tree-delta` | `threat-report.md:222` | `tachi-attack-tree-delta` at depth 3, plus three built-in `general-purpose` instances at depth 3 that ran 38 Bash calls and 1 Write (`test-results/w0-spike.md`, observation 2) |

Facts that matter for section 8:

- `Agent` is unrestricted in both files, so it reaches any subagent type available in the session, including built-in ones with the full toolset. The `tools:` column therefore understates what these two agents can do.
- No tachi agent, command or skill names `general-purpose` as a dispatch target (two unrelated prose uses of the phrase). The W0' dispatches were chosen by the model, not instructed.
- `tachi-report-assembler` and `tachi-threat-infographic` are dispatched only by commands. `threat-infographic.md` says its template is "specified by the orchestrator", which is stale wording: no orchestrator file dispatches it.
- Dispatch forms differ: `tachi.security-report.md:162` states `subagent_type: "senior-backend-engineer"`; the four other dispatching commands say "Invoke the `tachi-...` agent"; the orchestrator and `threat-report` use prose with no literal `subagent_type`. A guard check on dispatch targets would have to parse prose.

### 3.4 Skills the agents Read

All `tachi-*` skill directories: 7 carry a `SKILL.md` and 14 (one per threat agent) hold only `references/` files. Every `SKILL.md` has exactly `{name, description}`: no `allowed-tools`, `model`, `tools`, `hooks`, `permissionMode` or `mcpServers`. So the unguarded skill surface that ADR-049 will record as a limitation is empty today.

| Agent(s) | Skill and template reads |
|---|---|
| 14 read-only agents | own `tachi-{name}/references/detection-patterns.md`; `tachi-shared/references/severity-bands-shared.md`; `tachi-shared/references/finding-format-shared.md` |
| `attack-tree-delta` | `tachi-threat-reporting/references/attack-tree-construction.md`, `attack-tree-examples.md` |
| `control-analyzer` | `tachi-control-analysis/references/{control-categories,evidence-criteria,residual-risk}.md`; `tachi-shared/.../severity-bands-shared.md`; `adapters/claude-code/agents/references/sarif-generation.md`; `templates/tachi/output-schemas/compensating-controls.{md,sarif}`; the target codebase (read-only, `--target`) |
| `orchestrator` | `tachi-orchestration/SKILL.md` and nine references; six `tachi-shared` references; `templates/tachi/output-schemas/{threats.md,threats.sarif,threat-report.md}` |
| `report-assembler` | `tachi-report-assembly/references/{typst-artifacts,typst-template-contract,brand-asset-guidelines}.md`; `tachi-shared/.../severity-bands-shared.md`; `templates/tachi/security-report/`; `brand/final/` (via the extractor) |
| `risk-scorer` | `tachi-risk-scoring/references/` (seven files); two `tachi-shared` references; `templates/tachi/output-schemas/{risk-scores.md,risk-scores.sarif,threats.md}` |
| `threat-infographic` | `tachi-infographics/references/` (five files); `tachi-shared/.../severity-bands-shared.md`; `templates/tachi/infographics/infographic-*.md` |
| `threat-report` | `tachi-threat-reporting/references/{attack-tree-construction,narrative-templates}.md`; three `tachi-shared` references; `templates/tachi/output-schemas/threat-report.md` |

`install.sh` ships `.claude/agents/tachi/`, the six commands, all 21 skill directories, `schemas/`, `templates/tachi/`, four scripts, `adapters/claude-code/agents/references/` and `brand/`. It does not ship the agent files under `adapters/claude-code/agents/`, so the audited directory is what adopters receive (but see D-8 for the repair hint).

## 4. Commands

### 4.1 Candidate rows for section 8

| Command | Frontmatter keys | Dispatches | Bash it instructs (declared-only) | Writes | Child processes |
|---|---|---|---|---|---|
| `/tachi.threat-model` | `description` | `tachi-orchestrator` (which dispatches the threat agents and `tachi-threat-report`, which dispatches `tachi-attack-tree-delta`) | `python3` populator (L168-173; the same call is relayed to the orchestrator at L126-128); prose only: create `{out}` (L84), copy the architecture file (L94-95). Part B adds the Step 2.6 stamp script (T048's text, not at `46aec8d`) | `{out}/`; `{out}/architecture.md`; through the agents `{out}/threats.md`, `{out}/threats.sarif`, `{out}/attack-chains.md`, `{out}/threat-report.md`, `{out}/attack-trees/` | `python3` |
| `/tachi.risk-score` | `description` | `tachi-risk-scorer` | `python3` populator (L96-101, only for markdown input with an architecture file); prose only: create the output directory (L67) | `{out}/`; `{target_dir}/threats.md` in place; through the agent `{target_dir}/risk-scores.{md,sarif}` (D-3) | `python3` |
| `/tachi.compensating-controls` | `description` | `tachi-control-analyzer` | none named; prose only: create the output directory (L83) | `{out}/`; through the agent `{out}/compensating-controls.{md,sarif}` | none |
| `/tachi.infographic` | `description` | `tachi-threat-infographic` | `python3` extraction (L160-163, inside the agent prompt); `grep -P` MAESTRO probe (L166; `grep -E` after T013); prose only: create the output directory (L125) | `{out}/`; through the agent `{out}/threat-{template}-spec.md`, `{out}/threat-{template}.{jpg,png}`, `{out}/.tachi-build/infographic-{template}.json` | `python3`; `curl` (agent) |
| `/tachi.security-report` | `description` | `senior-backend-engineer` today (L162); `tachi-report-assembler` after T022 | `which typst` (L42); an `ls` attack-tree probe (L59); `test -f` for attack chains (L60); `command -v mmdc` (L61); prose only: create the output directory (L109) | `{out}/`; through the agent `{out}/security-report.pdf`, `{out}/.tachi-build/security-report/`, `{target_dir}/attack-trees/`, `{target_dir}/attack-chains/`, `{target_dir}/threat-{stem}.{jpg,png}` | `typst`; `mmdc` (up to 4 at once); headless Chromium; `python3` |
| `/tachi.architecture` | `description` | none (runs in the main session) | `mkdir -p {arch_dir}/.archive/v{N}/` (L42); a copy into the archive (L44, command not named); `shasum -a 256 {arch_path}` (L113) | `{arch_path}`; `{arch_dir}/.archive/v{N}/{filename}` | none |

The attack-tree probe at `tachi.security-report.md:59` is `ls "$target_dir"/attack-trees/*.md 2>/dev/null` piped to `head -n 1`; the pipe is omitted from the table cell above to keep the table valid.

### 4.2 Other command facts

- No command sets `allowed-tools`, `model` or `argument-hint`, so each command runs with the session's full toolset. The commands table's frontmatter column records `description` only (C5).
- Option text anchors that T012 and T024 edit: `tachi.security-report.md:15-18` (`--output-dir`), and the repair hints at `tachi.threat-model.md:67`, `tachi.risk-score.md:42`, `tachi.compensating-controls.md:47`, `tachi.infographic.md:56`.
- `tachi.security-report.md:256` documents `--output-dir reports/` together with a separate artifacts path. That is the combination in which `{target_dir}` differs from `{out}` (D-2).
- Display-only text, never executed: the `npm install -g @mermaid-js/mermaid-cli` hint (`tachi.security-report.md:65`, `extract-report-data.py:981`, `:1546`).
- All five run commands create the output directory themselves in the main session (L84, L67, L83, L125, L109); the agents then assume it exists (`control-analyzer.md:77` halts when it does not).

## 5. Write locations

One table. Evidence cites `46aec8d`. `pre only` rows exist at `46aec8d` and disappear with T012, T013 and T014; `post only` rows do not exist yet.

| ID | Path | Writer | Condition | Phase | Evidence |
|---|---|---|---|---|---|
| W01 | `{out}/` | the command's main session, creating the directory | when absent; all five run commands | both | `tachi.threat-model.md:84`, `tachi.risk-score.md:67`, `tachi.compensating-controls.md:83`, `tachi.infographic.md:125`, `tachi.security-report.md:109` |
| W02 | `{out}/architecture.md` | `/tachi.threat-model` main session, verbatim copy | the architecture file exists | both | `tachi.threat-model.md:93-95` |
| W03 | `{out}/threats.md` | `tachi-orchestrator` (Write); updated in place by `scripts/populate-affected-assets.py`, run by the orchestrator and again by the main session | always. Part B's stamp script (T039) updates the same file; no new path | both | `tachi.threat-model.md:115-119`, `:168-173`; `orchestrator.md:684-688`; `populate-affected-assets.py:460` |
| W04 | `{out}/threats.sarif` | `tachi-orchestrator` | always | both | `tachi.threat-model.md:117`; `orchestrator.md:739-741` |
| W05 | `{out}/attack-chains.md` | `tachi-orchestrator`, Phase 3.5 | only when at least one cross-layer chain passes the filter | both | `orchestrator.md:482-488` |
| W06 | `{out}/threat-report.md` | `tachi-threat-report` | Phase 5 on (default; off with `--skip-report`) | both | `threat-report.md:19-21`; `orchestrator.md:770-785` |
| W07 | `{out}/attack-trees/{finding-id}-attack-tree.md`; `{out}/attack-trees/.manifest.json` | `tachi-attack-tree-delta` | Critical or High findings exist (an empty manifest otherwise) | both | `attack-tree-delta.md:42`, `:75-78`, `:91`, `:118` |
| W08 | `{out}/compensating-controls.{md,sarif}` | `tachi-control-analyzer` | always | both | `control-analyzer.md:369`, `:396` |
| W09 | `{out}/threat-{template}-spec.md` | `tachi-threat-infographic` (Write) | each requested template | both | `tachi.infographic.md:153-157`; `threat-infographic.md:94` |
| W10 | `{out}/threat-{template}.{jpg,png}` | `tachi-threat-infographic`; decode tool unspecified | `GEMINI_API_KEY` set and the API returns an image | both | `gemini-prompt-construction.md:297-303` |
| W11 | `{out}/security-report.pdf` | `typst compile`, run by `tachi-report-assembler` | compile succeeds | both | `report-assembler.md:194-196` |
| W12 | `{target_dir}/risk-scores.{md,sarif}` | `tachi-risk-scorer`; equals `{out}` unless `--output-dir` is passed | always | both | `risk-scorer.md:442-446`, `:538-541` (D-3) |
| W13 | `{target_dir}/threats.md`, rewritten in place | `/tachi.risk-score` main session running the populator | markdown input and an `architecture.md` found | both | `tachi.risk-score.md:92-101`; `populate-affected-assets.py:460` |
| W14 | `{out}/.tachi-build/security-report/` (copy of `templates/tachi/security-report/`, a custom `report-config.typ` when present, `report-data.typ`) | `scripts/extract-report-data.py --build-dir`; removed by `--remove-build-dir` | every report run; removed after a successful compile, kept after a compile failure | post only | T012, T014; not at `46aec8d` |
| W15 | `{out}/.tachi-build/infographic-{template}.json` | `scripts/extract-infographic-data.py --output` | each template extraction; kept, never deleted | post only | T013; not at `46aec8d` |
| W16 | Gemini request and response files under `{out}/.tachi-build/` (names to be pinned) | `tachi-threat-infographic` | `GEMINI_API_KEY` set | post only; location unpinned today | `gemini-prompt-construction.md:260-261`, `:266` (D-4) |
| W17 | `{target_dir}/attack-trees/{finding-id}-attack-tree.png`; creates `{target_dir}/attack-trees/` if absent | `scripts/extract-report-data.py` (copy of the `$TMPDIR` render) | attack-tree entries exist and `mmdc` is on PATH | both | `extract-report-data.py:945`, `:953`, `:991-992` (D-2) |
| W18 | `{target_dir}/attack-chains/{chain-id}-attack-chain.png`; creates the directory | `scripts/extract-report-data.py` | `attack-chains.md` present and `mmdc` on PATH | both | `extract-report-data.py:1555-1556`, `:1605-1606` (D-2) |
| W19 | `{target_dir}/threat-{stem}.{jpg,png}`, a corrected sibling | `scripts/extract-report-data.py` (`detect_images`) | an infographic image whose bytes do not match its extension | both | `extract-report-data.py:1775-1796` (D-2) |
| W20 | `{target_dir}/threat-{stem}.{jpg,png}`, deleted | `scripts/extract-report-data.py --cleanup-mislabeled-images` | the flag is passed and a byte-identical correct counterpart exists | both | `extract-report-data.py:1672-1696`; documented only at `typst-artifacts.md:118-128` (D-2) |
| W21 | `$TMPDIR/tmp*/{finding-id}.mmd` and `.png`, and the chain equivalents | `scripts/extract-report-data.py` (`tempfile.TemporaryDirectory`, removed on exit) | attack trees or chains rendered | both | `extract-report-data.py:936`, `:998`, `:1558`, `:1596` |
| W22 | `$TMPDIR/` Chromium profile and caches | headless Chromium started by `mmdc` | same as W21 | both | declared in the Architect baseline; not visible in the repo and not confirmed here |
| W23 | `{arch_path}` | `/tachi.architecture` main session; the frontmatter step rewrites the file | always, unless the guided update ends with no changes | both | `tachi.architecture.md:77-79`, `:109-133` |
| W24 | `{arch_dir}/.archive/v{N}/{filename}` | `/tachi.architecture` main session | an existing architecture file was found | both | `tachi.architecture.md:35-48` |
| W25 | `templates/tachi/security-report/report-config.typ`, overwritten | `tachi-report-assembler`, Step 2a; no command named | `{target_dir}/report-config.typ` exists | pre only | `report-assembler.md:113-115` |
| W26 | `templates/tachi/security-report/report-data.typ` | `scripts/extract-report-data.py --output`; deleted on success (mechanism unnamed), kept after a compile failure | every report run | pre only | `report-assembler.md:158-163`, `:205-206`, `:216`; `typst-artifacts.md:118-124`; `extract-report-data.py:2575-2576` |
| W27 | `/tmp/infographic-data.json` (agent) and `/tmp/infographic-{template_name}.json` (command) | `scripts/extract-infographic-data.py --output` | each template extraction | pre only | `threat-infographic.md:170`; `tachi.infographic.md:163` |

Notes on the table:

- **Carve-out**: W23 and W24 are the `/tachi.architecture` carve-out in FR-007. Both lie inside the working directory in the default case; `--output <path>` is unconstrained.
- **Not writes**: reads outside the working directory are not listed (the `mmdc` install prefix, puppeteer's browser cache, system fonts, `brand/final/`, the baseline directory read by `tachi-attack-tree-delta`).
- **Sensitivity**: everything under `{out}/.tachi-build/` is derived from the same data as the rest of `{out}`, including `report-data.typ`, which is kept after a compile failure.
- **Scale of relocation**: T012, T013 and T014 remove W25 to W27 and add W14 to W16. Rows W17 to W20 are not touched by any task (D-2).
- **Where the `{target_dir}` rows bite**: with the default invocation `{target_dir}` equals `{out}` and the one-sentence confinement claim holds. It stops holding when `--output-dir` points elsewhere (D-2, D-3).

## 6. Child processes, environment, hosts

### 6.1 Scripts the agents and commands invoke

| Script | Invoked by | Imports of note | Writes | Network | Env reads |
|---|---|---|---|---|---|
| `scripts/populate-affected-assets.py` | orchestrator, `/tachi.threat-model`, `/tachi.risk-score` | argparse, pathlib, re, sys | `--threats` in place by default, or `--output`, or stdout; non-atomic `write_text` (L453, L460) | none | none |
| `scripts/extract-report-data.py` | `tachi-report-assembler`; the skill-reference cleanup fence | adds `subprocess`, `shutil`, `tempfile`, `concurrent.futures`, `filecmp` | `--output` file with `mkdir(parents=True)` (L2575-2576); W17 to W21 | none | none today; T014 adds `TACHI_MMDC_PUPPETEER_CONFIG` |
| `scripts/extract-infographic-data.py` | `tachi-threat-infographic`; `/tachi.infographic` prompt | argparse, json, math, re, sys, datetime, decimal, pathlib | `--output` (required, L2142-2146) with `mkdir(parents=True)` (L2214-2216, L2496-2497) | none | none |
| `scripts/tachi_parsers.py` | imported by the three; preflight `test -f` only | dataclasses, decimal, pathlib, re, sys | none | none | none |

`scripts/install.sh` appears in the agents only as repair text. No agent or command runs it.

### 6.2 Other children

| Process | Parent | Notes |
|---|---|---|
| `mmdc -i <tmp>.mmd -o <tmp>.png -s 2 -b transparent` | the extractor, from a 4-worker thread pool, 30 s timeout each | `extract-report-data.py:940`, `:1000`, `:1600`, `:1560`. No `-p` today. After T014, `-p <path>` is added when `TACHI_MMDC_PUPPETEER_CONFIG` is set; the value must be an absolute path to a regular file or the extractor fails loud (AD-9). Invisible to transcripts and permission rules |
| headless Chromium | `mmdc` (puppeteer) | grandchild of the agent's Bash call; same invisibility; writes under `$TMPDIR` (W22) |
| `typst compile <build>/main.typ {out}/security-report.pdf --root .` | `tachi-report-assembler` | the templates import only local files (no `@preview` package), so there is no network access and no package cache write. A future package import would add both |
| `curl` to the Gemini host | `tachi-threat-infographic`, built by the model from the skill reference | the key is delivered through `--config -` from the process environment; never on the command line |
| base64 decode of the image | `tachi-threat-infographic` | tool and location unspecified (D-4) |

### 6.3 Environment

`GEMINI_API_KEY` (read by the agent's key check and the `curl` heredoc; environment only), `TMPDIR` (implicit, through `tempfile`), `TACHI_MMDC_PUPPETEER_CONFIG` (read only after T014).

### 6.4 Hosts

| Host | Who | When | Evidence |
|---|---|---|---|
| the model provider configured in Claude Code | every agent and the main session | always | n/a |
| `generativelanguage.googleapis.com` | `tachi-threat-infographic` | a key is set and the image step is not skipped (`skip_image` for the executive template, an empty threat model for the rest) | `gemini-prompt-construction.md:242`, `:258`. The installed reference `adapters/claude-code/agents/references/infographic-gemini-api.md:100` names the same host; no installed agent references that file |
| none | the four scripts; `typst`; `mmdc` and Chromium (none expected, which T020's offline render check tests) | n/a | section 6.1 imports; templates' `#import` lines |

Install-time `git fetch --tags` in `scripts/install.sh` is not a run-time host of any agent or command.

## 7. Discrepancies

| ID | Severity | Finding | Raised for |
|---|---|---|---|
| D-1 | planned | `tachi.security-report.md:162` dispatches `senior-backend-engineer` | T022 (AD-13) |
| D-2 | Medium | Extractor writes (PNGs, corrected images, opt-in deletion) land in `{target_dir}`, not `{out}`, and no task moves them | T040, T016, T020 |
| D-3 | Medium | `/tachi.risk-score` rewrites `{target_dir}/threats.md`; `risk-scorer` ignores the output directory the command passes | T040, T016 |
| D-4 | Medium | Gemini request, response and decode locations are unpinned; T013 relocates only the extraction JSON | T013 |
| D-5 | Medium | Under the T025 rules the infographic fence set includes `echo`; `w0-prestate.md` lists three of four families | T023, T025, T026 |
| D-6 | Medium | `Agent` reaches any tool; the §8 agents table has no dispatch column; an undeclared dispatch was observed | T023, T040 |
| D-7 | Low | Two labelled shell fences in skill references and several unfenced model-built commands sit outside C6 | T023 |
| D-8 | Medium | The documented repair hint installs adapter copies that have no `tools:` and no `model:` | T024, T023 scope note |
| D-9 | Low | The `{out}`-under-cwd precondition is disclosed only for the security report | T012, T016 |
| D-10 | Low | T013 names `{output_path}` in an agent that defines no output variable; two filenames disagree | T013 |
| D-11 | Low | T012's same-commit list misses prose that states the old image and brand path base | T012 |
| D-12 | Low | Extractor argparse marks three flags `required=True`, which the new recipes would trip | T014 |
| D-13 | Low | The Architect's baseline has gaps (`attack-chains.md` and others) | T023 |

**D-1 (planned).** `tachi.security-report.md:162` reads `Use the Agent tool with subagent_type: "senior-backend-engineer"`. That agent is `.claude/agents/senior-backend-engineer.md`, part of the AOD build set: its frontmatter has no `tools:` key (so it is not restricted to a tool list), it pins `model: sonnet`, and `INSTALL_MANIFEST.md` ships only `.claude/agents/tachi/`, so adopters do not have it. The prompt tells it to read `.claude/agents/tachi/report-assembler.md` and execute that file's steps. It is the only literal non-tachi dispatch in tachi's own agents, commands and skills. T022 changes it to `tachi-report-assembler`; after that the Dispatches cell reads `tachi-report-assembler`, whose tools cover the steps it names (Read, Glob, Grep, Bash, Write; its body names no other tool).

**D-2 (Medium).** `extract-report-data.py` receives only `--target-dir`. It creates `target_dir / "attack-trees"` (L991-992) and `target_dir / "attack-chains"` (L1555-1556), copies PNGs there (L953, L1606), writes a corrected sibling of a mislabeled infographic image there by default (L1790), and deletes under the opt-in flag (L1687). T012 to T014 relocate only `report-data.typ`, `report-config.typ` and the infographic JSON. With `--output-dir` different from the artifact directory (the combination shown at `tachi.security-report.md:256`), FR-007 and SC-005 ("only under the output directory") are not true for W17 to W20, and the Architect's baseline row `{out}/attack-trees/*.png` is accurate only by default. T015's fixture has no attack trees (so W17 and W18 never fire there) and T020's listing does not call for a run with `--output-dir`, so neither observes this. Options for T040: document W17 to W20 as `{target_dir}` rows and qualify the runbook sentence ("the run's output directory, which is the artifact directory unless `--output-dir` is passed"); or give the extractor a flag that redirects them under `{out}`. The audit's tables use the first option. If it stands, add one `--output-dir` run with attack trees to T020's write listing.

**D-3 (Medium).** `tachi.risk-score.md` Step 1.5 runs the populator on `{input_file}`, which rewrites `{target_dir}/threats.md` in place (L96-101; `populate-affected-assets.py:460`). Separately, the command creates `{output_dir}` (L67) and passes `Output directory: {output_dir}` to the agent (L123), but `risk-scorer.md` never mentions an output directory: it writes `risk-scores.md` and `risk-scores.sarif` "to the same directory as the input file" (L442-446, L538-541). The two instructions disagree whenever `--output-dir` is passed; which one the model follows is not determined. `control-analyzer.md` honours the passed directory (L56, L369, L396), so the sibling command is consistent. Handling is the Architect's call (a body-only edit to `risk-scorer.md`, or documenting `{target_dir}`); until then W12 and W13 are keyed to `{target_dir}`.

**D-4 (Medium).** The pinned `curl` form uses `{request_file}` and `{response_file}`, "files the agent writes beside its other intermediates" (`gemini-prompt-construction.md:266`), and the decode step saves `threat-{template-name}.{ext}` with no tool and no directory named (L297-303). After T013 the only named intermediate is `{out}/.tachi-build/infographic-{template}.json`. "Beside" would then mean `{out}/.tachi-build/`, but nothing says so, and a model-built path could still fall to `/tmp`, which the session profile denies; that is the failure mode the relocation exists to prevent. The request file holds the prompt and the response file holds the base64 image, so keep-or-delete also needs a statement (the agent has no `rm` family). Ask for T013's commit: pin both file names under `{out}/.tachi-build/` in the reference, say whether they are kept, and list them in W16.

**D-5 (Medium).** `threat-infographic.md:348` is `if [ -z "${GEMINI_API_KEY:-}" ]; then echo "..."; fi`. Splitting on `;` and skipping reserved words (T025 rules) gives the segments `[ -z ... ]`, `echo "..."` and nothing for `fi`. The families are `[` and `echo`. `w0-prestate.md` note 3 records `{test, python, [}`. If §8 and the guard's allow-list omit `echo`, C6 is red on day one. `test_gemini_key_env_only.py` pins the section's properties (environment only, no `.env`, no loader) and not this line, but the line belongs to the key-handling patch. Handling: allow-list `echo` (a builtin) rather than edit the line; T026's reserved-word case should assert the exact set `{[, echo}` for this fence.

**D-6 (Medium).** `tachi-orchestrator` and `tachi-threat-report` hold an unrestricted `Agent`. In the W0' run `tachi-threat-report` dispatched three built-in `general-purpose` instances, which ran 38 Bash calls and 1 Write; its body names only `tachi-attack-tree-delta` (`:222`), and no tachi file names `general-purpose`. The C2 check pins `tools:` but cannot bound what `Agent` reaches, and `contracts/matrix-section.md` fixes the agents table at Agent, Tier, Tools, Model, Bash families, Writes, Hosts, with no place for agent-to-agent dispatch. Handling for T023: the legend states that `Agent` reaches every tool of every available subagent type; add a Dispatches column (or a legend line) for the two agents. A session-profile control such as the `Agent(general-purpose)` deny that the spike suggests is unconfirmed and belongs to T006 and T020. The write locations of the observed `Write` call were not recorded (the spike is structure-only).

**D-7 (Low).** C6 covers the three agent files by design (TW-A3), so the machine-checked Bash column understates real use in the infographic path (`curl`, a decode) and does not see the report path's extractor cleanup invocation in `typst-artifacts.md:118-124`. `w0-prestate.md` note 3 already asks how §8 declares the `curl`. Proposal: the Bash families column lists only C6's fenced families, and a footnote beside the agents table declares the model-built commands (`curl` with the pinned request form; a base64 decode with no tool named) and the two skill-reference fences as declared-only. Do not move the `curl` fence into an agent body without a heredoc rule in C6, or its body lines (`header = ...`, `EOF`) would be read as commands.

**D-8 (Medium).** All 15 files under `adapters/claude-code/agents/` have frontmatter `{name, description}` only: no `tools:` and no `model:`. Six live agents (`attack-tree-delta`, `control-analyzer`, `report-assembler`, `human-trust-exploitation`, `misinformation`, `output-integrity`) have no adapter copy at all. The repair hints at `tachi.threat-model.md:67`, `tachi.risk-score.md:42`, `tachi.compensating-controls.md:47` and `tachi.infographic.md:56` tell an adopter to `cp -r` those files into `.claude/agents/tachi/`. Following a hint can replace or shadow a pinned, tool-restricted agent with one that, under Claude Code's documented subagent behaviour (not re-confirmed here), inherits the session's tools and model; whether the copy replaces or nests depends on the platform's `cp`. T024 replaces the hints with `scripts/install.sh`, which is the fix. For T023's scope note: the copies stay in the repository, are not covered by the guard, and are unpinned; the note should say so rather than only "not covered".

**D-9 (Low).** The `{out}`-under-cwd precondition appears in T012 and T016 for `/tachi.security-report` only. Under the sandbox's default writable set (the working directory plus the per-user temp directory, per the Architect's ruling D-4), every run command's `--output-dir` and `/tachi.architecture --output` outside the working directory would be denied. The security report also needs `{target_dir}` under the working directory, because the images are read through paths relative to `--root .`. Widen the runbook's disclosure from the report command to every command that takes an output path.

**D-10 (Low).** T013 rewrites the infographic recipe to `--output {output_path}/.tachi-build/infographic-{template}.json`, but `threat-infographic.md` contains no `output_path` or `output_dir` anywhere; the directory reaches the agent only through the command's prompt (`tachi.infographic.md:153`, "Write all output files to: {output_dir}"). T012's equivalence of `{out}`, `{output_path}` and `{output_dir}` holds for the report assembler only. Also, today's two recipes name different files: the agent `/tmp/infographic-data.json` (L170, one name for every template) and the command `/tmp/infographic-{template_name}.json` (L163). T013's per-template name resolves both; it needs to say where the agent learns the directory.

**D-11 (Low).** T012's same-commit list does not include prose that gives the old path base. These lines describe image and brand paths as relative to `templates/tachi/security-report/` or give the literal `../../{target_dir}/` or `../../brand/final/` patterns, which stop being true once T014 computes paths against the build directory: `typst-template-contract.md` L105-111, L260, L294-296, L310, L326, L342, L406; `brand-asset-guidelines.md` L48, L52, L57-59, L78; `docs/guides/DEVELOPER_GUIDE_TACHI.md:1994` (a second compile-path sentence besides the L1609 that T012 lists). `typst-artifacts.md:118-124` is listed as `118-123`; the fence closes on L124 and the flag is on L123.

**D-12 (Low; Lane D's T014 is in flight).** `extract-report-data.py:2302-2316` declares `--target-dir`, `--output` and `--template-dir` as `required=True`. The T012 recipe (`--target-dir ... --build-dir ...`) and `--remove-build-dir PATH` alone would both exit 2 from argparse unless T014 makes those flags mode-dependent. The old `--output`/`--template-dir` form must keep working: several test modules call it (for example `test_extract_report_data.py`, `test_report_posture_contract.py`, `test_backward_compatibility.py`).

**D-13 (Low).** Corrections to the Architect's baseline (`.aod/results/architect-391.md` section 10) for T023 to apply: the orchestrator also writes `{out}/attack-chains.md` (conditional); `attack-tree-delta` also writes `.manifest.json`; the report path's PNG and image-sibling writes are in `{target_dir}`, with an opt-in deletion; `risk-scorer` writes beside its input; the infographic Bash set now includes the key check (`[`, `echo`) and no longer includes `.env` sourcing; the `rm`-style cleanup in the report assembler is model-built and unfenced today.

## 8. Handoff notes

- **T012, T013 (SBE-D)**: the edit sites in D-4, D-10, D-11 and D-12; keep the extractor fence in `typst-artifacts.md` in step with the new flags; do not introduce a bare `export $(` in any fence (`test_gemini_key_env_only.py` fails on it); the infographic set after T013 is `{[, echo, python3, test}`.
- **T014 (SBE-D)**: `TACHI_MMDC_PUPPETEER_CONFIG` becomes the only environment read in any invoked script; both `mmdc` call sites are `:940` and `:1600` at `46aec8d`.
- **T015 (SBE-TA)**: the fixture has no attack trees, so W17 and W18 never fire, and W19 and W20 fire only if it holds a mislabeled infographic image; that is consistent with T015's scope but means D-2 needs T020.
- **T016 (DEVOPS-R)**: build the runbook table from section 5, rows `both` and `post only`, with the path tokens of section 2; state `{target_dir}` rows if T040 chooses to document them; state hosts and child processes from section 6.
- **T023, T025, T026 (SBE-E)**: copy 3.1 and 4.1, resolve D-5 to D-8 and D-13 in the legend, the footnote and the scope note; the day-one allow-lists are orchestrator `{python3}`, report-assembler `{python3, test, typst}`, infographic `{[, echo, python3, test}`; C1 expects the agents directory to hold 21 agent files plus the one allow-listed file, no symlink and no other file type.
- **T040 (architect)**: decisions needed on D-2, D-3, D-4 and D-6; D-8's remedy is already scheduled (T024).
