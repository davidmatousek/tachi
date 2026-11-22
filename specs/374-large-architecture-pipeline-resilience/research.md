# Research Summary: Large-Architecture Pipeline Resilience (F-374)

**Date**: 2026-11-22 · **Branch**: `374-large-architecture-pipeline-resilience` (base `b040fa1`, v4.48.4) · **PRD**: [PRD-374 v1.3](../../docs/product/02_PRD/374-large-architecture-pipeline-resilience-2026-11-21.md) · **Feasibility**: [feasibility-check.md](feasibility-check.md)

Four research passes ran in parallel: the knowledge base, the codebase, the architecture records, and platform documentation (GitHub Code Scanning, OASIS SARIF 2.1.0, Claude Code, FIRST CVSS v3.1). Pointers are to `b040fa1`. The only examples cited are tachi's own synthetic samples. A spot-check of 51 of the PRD's file and line pointers found that all of them still match.

---

## PRD corrections and new premises

Each item names the spec ruling (S-n) or requirement that absorbs it.

1. **GitHub computes `primaryLocationLineHash` when a result lacks one.** The `upload-sarif` action fills `partialFingerprints` from the text at `locations[0]`'s start line: a rolling hash over the first 100 non-space characters, plus an occurrence counter. It keeps a value the file already carries. So today's scorer and controls results, which carry no hash, are keyed by whatever line of the architecture file they point at. Editing that line re-keys them, and identical lines collide. → S-6: every result carries tachi's own hash.
2. **Baseline correlation reuses today's SARIF hash recipe.** Phase 3 matches findings on `SHA-256(ruleId|component)` as its secondary key (ADR-018; `baseline-correlation.md:78-106`), and it recomputes that key from `threats.md`. D-5's new per-finding recipe must not leak into matching, and legacy baseline SARIF keeps the old hashes. → S-7.
3. **Claude Code's dispatch limits.**
   - By default, at most **20 subagents run at once**, and nesting goes **at most three layers below the main conversation**.
   - Phase 2 dispatches every applicable agent concurrently (`orchestrator.md:298`), so a per-component re-dispatch over 25 components would pass 20 in flight.
   - The tree agent already sits at depth 3 when the report agent dispatches it.
   - What a caller receives when a subagent stops on `max_tokens` is **not documented**.

   → S-8, and FR-N4.7's detector is spiked before it is built (S-9; KB 25).
4. **Output budget.**
   - Thinking tokens count toward `max_tokens`. Claude Code's documented default is 32,000 output tokens for models it doesn't recognize (cap 128,000), and requests sent without streaming are capped at 64,000. Runs A and B stopped at 64k.
   - A batch is therefore safe only if its expected output leaves room for reasoning at `effort=max`. → S-1 (OQ-5).
5. **Subagent type restrictions.**
   - `tools: Agent(type, …)` is an allow-list only for an agent run as the main thread (`claude --agent`); inside a subagent definition the type list is ignored.
   - Settings-level `Agent(name)` deny rules do exist.
   - So prevention stays FR-N4.1's body text plus #409's static check. A deny rule in the isolated-operation profile is a follow-up, because that profile is pinned by SHA-256 (NFR-3). → S-10.
6. **No tachi SARIF file carries `runAutomationDetails`.** The upload step's `category` input therefore sets each file's category, which R-33's distinct (tool, category) pairs rely on. A file's own `automationDetails.id` would override the input. → S-6 keeps every file free of it.
7. **Python and imports.**
   - `pyproject.toml` allows Python 3.9, while main's gates run 3.11 and #396 adds a 3.9 job.
   - S-13 checks module-level imports only, and skips below 3.10.
   - Every install-fidelity job installs PyYAML, so a lazy `import yaml` on the core path would pass CI.
   - → S-11: 3.9 compatibility, plus a test run with `yaml` blocked.
8. **Only the report agent reads `attack-trees/.manifest.json`.** The PDF extractor globs the tree files (`extract-report-data.py:582-620`), and no script or test reads the manifest. This corrects an aside in D-3. The merged schema-1.0 manifest stays, for the report agent and the tree agent's own carry-forward.
9. **FR-N4.1's stale rosters are body tables**: `finding-format-shared.md:87-88` and `:200-202`, and `coverage-requirements.md:153-154`. The frontmatter `consumers:` list already names all eight AI agents.
10. **Two shipped `threats.md` files write Section 7 as a numbered list** (`consumer-agent-app`, `predictive-ml-app`), which parses as an empty set, and two `risk-scores.md` files use `## Section N:` headings. Today's reader can't build the reference set from them. → S-12, as the PM amended it at the spec review: the readers accept these drift forms, and the oracle keeps the PRD's rule, with these examples as drift-form cases.
11. **The architecture snapshot keeps the source file's basename** (`tachi.threat-model.md:91-102`), but the populator and the downstream commands assume `architecture.md`. This bug predates the bundle, so it is filed as a follow-up and kept out of scope. The D-5 carrier records the user's repo-relative path regardless of the snapshot's name.
12. **Two sources for asset tags.** The scorer reads tags through `parse_component_asset_map()` (`risk-scorer.md` §3.5), and F-302 NFR-2 says `affected_assets` "does NOT affect scoring" (`risk-scorer.md:528`). D-2, however, takes the elevation's tags "from the populator". With `--output-dir`, the populate step is skipped (`tachi.risk-score.md:92-111`), so the block can be stale. → S-13: one named source.
13. **No shared parser reads Section 4a's correlation groups.** `extract-infographic-data.py:614-637` has an ad-hoc reader. The controls renderer's group source (D-5) is new code.
14. **The regeneration-tier generators aren't a drop-in** (confirms D-2):
    - they aren't installed and set no bytecode guard;
    - `generate-threats-sarif.py` hashes `md5(finding_id)`, parses one example's table shape and hardcodes a baseline run ID;
    - `generate-risk-scores-sarif.py` hardcodes an example path (#357), emits peers as top-level results, carries only `findingId/v1` and the placeholder `informationUri` (#412), and loads taxonomies through a PyYAML path.

    Their helpers `artifact_uri_for`, `build_sarif_envelope` and the `RULES` tables can be salvaged.
15. **Scorer SARIF taxa come from `schemas/taxonomy/owasp.yaml` through a PyYAML loader** (ADR-048 FR-012a). That conflicts with R-32's stdlib-only core path, so ADR-050 must source the taxa another way: embedded with a drift test, or passed through from the input.
16. **Python's `random` guarantees the sequence of `random()` across versions, but not that of `choice`, `sample` or `randint`.** The fixture generator derives every choice from `random()` or from a hash. → S-4.
17. **ADRs the PRD doesn't name also change:**
    - ADR-013: D1 co-generation, D4 the hash recipe, and D5 peers in `relatedLocations`;
    - ADR-018: delta classes;
    - ADR-020 Phase 2: the boolean, "all chains recorded", and "no tie possible";
    - ADR-017: D4 "script failure halts" is the precedent for D-3, and D2's largest-remainder rule covers the renderer's percentages.

    → plan input P-1.
18. **CVSS Roundup is not half-up rounding.** It is a ceiling to one decimal, after scaling by 100,000 (FIRST Appendix A). NFR-2's half-up rule applies to composites and the other stored one-decimal values. They are two rules and stay two.

---

## Knowledge Base Findings

The KB has **no entry on output-cap overflow or code hand-backs**. The only records are build notes: F-373 restaged a task after a stall and a 64k overflow (`specs/373-adopter-install-output-fidelity/test-results/w1-exit-checkpoint.md:206`), and F-391's spike saw five `max_tokens` stops across four agents on the smallest input, along with report-agent helpers running Bash (`specs/391-isolated-auditable-operation/test-results/w0-spike.md:63-64`). A KB entry is due at delivery.

| Entry | Lesson | Consequence for F-374 |
|---|---|---|
| KB 1, 9 | A substitution-target edit regenerates the init baseline in the same commit | Targets this bundle may touch include `docs/INSTITUTIONAL_KNOWLEDGE.md`, `docs/architecture/01_system_design/README.md`, `docs/devops/CI_CD_GUIDE.md`, `docs/testing/README.md` and `.claude/README.md` |
| KB 2 | Widen scope in a named phase, not by retries | A FR-K4.3 result that overturns a K4 candidate goes through R-21 and a named tasks phase |
| KB 3 | A module in `paths:` but not in the invocation (or the reverse) is silently ungated | Lock-step wiring per FR-E.5. Moving the CVSS calculator adds an input surface to its test's `paths:` entry |
| KB 6 | Protected detection-tier files need a carve-out in `test_backward_compatibility.py` | FR-N4.7's end marker and FR-N4.1's roster fixes go in shared references, which 17 agent files read, so no protected file is edited (S-9) |
| KB 7 | The post-merge tail gets its own issue | #364's audit leads, the R-17 follow-up and the optional Code Scanning check become `[POST-MERGE]` tasks |
| KB 11, 12 | Fix the source, not the filter; extractors carry values through | The extractors read both formats and never recompute a value the renderer wrote |
| KB 13–16 | Name the consequence scope early, and record literal pre-state totals | The spec lists the consumers (see "Consequence scope"), and T001 records every gate's totals, so #365's known reds aren't misattributed |
| KB 17, 10 | Live validation at delivery; dispositions decided first | D-7's live runs are named tasks; model behavior (SC-3) is measured, not gated |
| KB 18 | A branch behind `main` can re-ship a regression at delivery | PR 2 merges `origin/main` after PR 1's squash, with a full-tree diff |
| KB 19 | Guard an invariant with the producer's own loader; fail closed | Plan and input digests use the renderer's loaders, and a missing or partial part fails |
| KB 20 | Extend the existing gates; check for a needed tool | `/tachi.compensating-controls`' new `python3` step checks that the interpreter is present and names the remedy |
| KB 21 | Delete only behind a double gate | Stale parts are rejected by plan ID, never deleted (D-3) |
| KB 22 | An empty extraction is an error; diff what consumers read; at most two live attempts; dispatch in the foreground | `parse_threats_findings` returns `[]` with a warning when the heading is missing (`tachi_parsers.py:1188-1191`), so the reference-set wrapper raises instead. Re-dispatches and tree batches run in the foreground (S-8) |
| KB 23 | A ledger with a pinned census proves each occurrence was reviewed | Census the four SARIF contract copies, D-6(a)'s seven rewordings and the six platform-neutral clauses |
| KB 24 | Decide "inside" by file identity; every serialization is a trust boundary | The architecture-path carrier uses identity (`samefile`), emits one canonical spelling, and refuses control bytes; FR-E.2 gains a case-variant case |
| KB 25 | Spike a detector against planted failures under production constraints | Spike FR-N4.7 under the session profile: a stop mid-reasoning, a stop mid-output, a stall, an empty return |
| KB 26 | Recompute, never retype; calculators self-test on the publisher's examples | The shipped calculator keeps FIRST's 16 examples, and the `agentic_app` extractor fixture's 9.1 is a named exception |
| F-012 | The original fingerprint hashed rule plus component, and only its stability was verified | FR-E.2 asserts uniqueness among present findings as well as stability, and the recipe excludes model prose |

---

## Codebase Analysis

### Precedents to follow

- **`scripts/populate-affected-assets.py`.** The production precedent for a deterministic value authority (ADR-046 D2):
  - four pure functions, a thin CLI with `--check`, and byte-stable output;
  - `sys.dont_write_bytecode` set before its local import (ADR-049 D8);
  - it does no path validation and writes in place. The renderer adds what NFR-10 requires: a path guard, size caps, an atomic write, and a stated failure path in each command.
- **`extract-report-data.py`.** `_guard_build_dir` (`:2466-2522`) does real-path containment, refuses symlinks and requires a fixed suffix, and `_is_safe_finding_id` (`:654-659`) checks IDs before they become paths. Both can be reused for NFR-10.
- **The CVSS calculator** in `tests/scripts/test_cvss_category_defaults.py`. It has `roundup` (`:66-72`, FIRST's integer method), `base_score` (`:75-87`), the 16 FIRST examples and the schema-drift tests. It moves into a shipped stdlib module that the test imports (D-2).
- **Half-up rounding.** `_funnel_quantize` (`extract-infographic-data.py:1463-1465`) and `tachi_parsers.parse_score` already use `Decimal` with `ROUND_HALF_UP`.
- **The fixture generator** `tests/scripts/generate_pagination_fixture.py` (fixed seed, a hand-rolled serializer). F-374 changes two things: it generates into `tmp_path` and compares with the committed copy, rather than rewriting tracked files, and it derives every choice from `random()`.

### Readers to keep compatible (`scripts/tachi_parsers.py`)

| Reader | Keys on | F-374 |
|---|---|---|
| `parse_threats_findings` (`:1177`) | `## 7. Recommended Actions` | The D-4 reference set, wrapped so that an empty or missing set raises; four callers rely on today's return |
| `parse_resolved_findings` (`:1029`), `delta_status_by_id` (`:862-937`), `parse_baseline_frontmatter` (`:567`) | Section 4c or legacy 4b; the Section 7 Status column; the `baseline:` block | Reused for R-30's open/RESOLVED split, tree-batch planning and D-6(c) |
| `parse_risk_scores_findings` (`:1302`), `parse_risk_scores_severity` (`:808`) | `## 2. Scored Threat Table` and its header names | The renderer emits these headings and headers |
| `parse_compensating_controls_md` (`:1409-1775`) | #373's alias table, Section 4's `#### N. ID —` blocks, and the coverage regexes | It reads both the corrected and the pre-fix formats (FR-K8.2, NFR-1) |
| `detect_artifacts` (`:736-741`) | A non-empty `attack-chains.md` | It falls back to file presence when the Phase 3.5 record is absent |

### Install and CI wiring (one commit per script)

- **The manifest.** The script enters `INSTALL_MANIFEST.md` in three places (the directory row, the Script Files table and the machine-readable block) and joins `REQUIRED_SCRIPT_NAMES`.
- **Imports.** S-13's allowance widens to each new local helper.
- **Bytecode and confinement.** The script sets the bytecode guard, and gets an entry in `ENTRY_SCRIPTS_IMPORTING_PARSERS` (`test_write_confinement.py:1041-1045`).
- **Gating.** Its test module joins one gate's `paths:` list and invocation. `tachi-install-fidelity.yml` (Ubuntu, Python 3.11) is the default for renderer, checker and parser suites; `tachi-pytest.yml` runs 23 modules across macOS and Ubuntu; `tachi-permissions-verify.yml` runs the privilege guard (C1–C7).
- **The §8 matrix.** A fenced `python3` call in an agent or command updates §8.3 or §8.4, §8.5, and the runbook's §5 in the same commit, or C7 goes red.

### Run-directory facts

- **Where commands write.** `/tachi.threat-model` writes `{output_dir}/{timestamp}/`. The scorer and controls commands write to their input directory by default.
- **`.tachi-build/`** is written today only by the infographic and report paths. Nothing on the threat-model, scorer or controls path writes there yet. `.gitignore:207` ignores it in this repository only.
- **The Phase 3.5 outcome.** It is a boolean that the contract never writes. The readers re-derive it: the report agent from the file's presence, `detect_artifacts` from a non-empty file, and the PDF from `prepare_attack_chains`. Five example `threats.md` files carry a de-facto `has_attack_chains:` key, and `consumer-agent-app`'s sample records a zero-chain reason in its body.
- **Schema versions in force.**
  - `threats.md` 1.4 (`output-schemas.md:285` says 1.2, which FR-K4.1 corrects);
  - `risk-scores.md` and `compensating-controls.md` 1.0;
  - the finding IR 1.9;
  - `attack-chains.md` 1.0;
  - the tree manifest 1.0, defined in prose only.

### Consequence scope (consumers of what this bundle changes)

- **Readers of the four renderer-owned files:** `tachi_parsers`, `extract-report-data.py`, `extract-infographic-data.py`, the `golden/` and `report_data/` fixtures, the coverage pins, and the six byte-gated example PDFs (#365).
- **Readers of `attack-chains.md` and the Phase 3.5 outcome:** the report agent, `detect_artifacts`, `prepare_attack_chains`, `main.typ:108` and `:275`, `test_attack_chains.py` and `test_attack_chain_extraction.py`.
- **Tests that pin the regeneration generators:** `test_affected_assets_wiring.py` (SC-006, FR-014), `test_owasp_2026_contract.py` and `test_tachi_parsers.py:611-621`.
- **Shipped examples.** They regenerate through the renderer under #364 (NG5). The best small-run oracles are `mobile-banking-app` (31 findings, consistent across all three files) and `agentic-app` (86).

---

## Architecture Constraints

| Record | In force | What F-374 changes |
|---|---|---|
| **ADR-046** (tier boundary) | D1: production SARIF is LLM-authored. D2: the populator is the only value authority. D4: consistency is test-checked. D5: the structural ideal is deferred | D-2 supersedes D1 for the scorer and controls files at PR 1 (only partly for controls Sections 2 and 4, R-34), and FR-O.1 supersedes it for `threats.sarif` at PR 2. D4 becomes structural where a surface moves. D5 is adopted. D2 and D3 stand |
| **ADR-047** (MAESTRO authority) | One applicability decision; the populator is examples-only | No change unless SV-2b's table rendering ships. FR-E.10 verifies through `classify_maestro_coverage_state`, never re-derives |
| **ADR-049** (privilege and confinement) | D4: `Agent` is unguarded. D5: writes stay under `{out}`. D7: agent-chosen paths are pinned. D8: bytecode suppression. C5: commands keep `{description}`. C7: write-set parity | D7 is amended for part files and the renderer's writes. D4 stands. A dated note, not a D10, because #396 adds D10 |
| **ADR-024** (scoring) | The composite weights and bands | No change (NG7). The arithmetic moves into code, with constants drift-tested (R-32) |
| **ADR-048** (OWASP 2026) | Only 2026 tokens are emitted; enforcement sits in authored prose | The shipped emitters become enforcement points, and the taxa are sourced without PyYAML |
| **ADR-013, 018, 020, 017** | As item 17 above | Each gets a dated note or a Revision History entry |
| **Constitution** (v1.0.0, Standard tier) | X: the gates run in order; an overridden ADR needs a recorded amendment accepted before the build. VI–VII: tests before "done", red CI blocks merge | ADR-050 is accepted at the plan stage (TW-ADR) |

- **ADR-050 is the next free number.** ADR-049 is the highest. 004 and 043 are gaps, and 043 is reserved.
- **The repo's ADR format.** Bold header lines (Status, Date, Deciders, Feature, Supersedes, Related ADRs). Then Context, Decision (`### D1 — …`), Alternatives Considered, Consequences, Known limitations, References and Revision History.
- **Amendments never rewrite the ratified text.** The forms are an erratum blockquote (ADR-024), a one-line amendment annotation plus a Revision History entry (ADR-027 D3), or a dated header note (ADR-014).
- **Docs to update at delivery:**
  - `docs/architecture/README.md` (the index line);
  - `00_Tech_Stack/README.md` (the scripts and outputs);
  - `01_system_design/README.md`;
  - `03_patterns/README.md` ("production SARIF is LLM-authored" goes stale);
  - `CLAUDE_PERMISSIONS.md` §8.3–§8.5 and the runbook's §5;
  - `docs/devops/CI_CD_GUIDE.md`;
  - `docs/INTERFACE-CONTRACT.md` §5 and §7.

---

## Industry Research

### GitHub Code Scanning ([SARIF support](https://docs.github.com/en/code-security/reference/code-scanning/sarif-files/sarif-support), [uploading](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/integrate-with-existing-tools/upload-sarif-file))

- **Matching inputs.** Alerts match across runs on the tool, the category, the `ruleId`, the `primaryLocationLineHash` and the file path. A changed path closes the old alert and opens a new one. How these inputs combine on the server isn't documented.
- **Fingerprints.** GitHub reads only `primaryLocationLineHash`. `baselineState`, `guid`, `correlationGuid` and custom fingerprint keys are not read.
- **Primary location.** Only the first entry of `locations[]` counts. `relatedLocations` sit inside a result, and they are not results.
- **A second upload.** For the same commit, tool and category, it replaces the first. Without a `category` input, each file needs a unique `runAutomationDetails.id`. A file's own `automationDetails.id` overrides the input ([codeql-action `upload-lib.ts`](https://github.com/github/codeql-action/blob/main/src/upload-lib.ts)).
- **Limits.** 10 MB per gzipped file, 20 runs per file, 25,000 results per run (5,000 shown) and 1,000 locations per result. A run at Run B's scale has about 210 deduplicated findings, far below these.
- **Alert lifecycle.** An alert whose result is absent from a new analysis closes. What happens when the result returns isn't documented.

### SARIF 2.1.0 ([OASIS](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html))

- **Fingerprints** (3.27.16): a fingerprint is the same for logically identical results and different for distinct ones. `partialFingerprints` (3.27.17) contribute to that identity.
- **Appendix B:** don't put information a result manager can deduce, or an absolute line number, into a fingerprint.
- **`baselineState`** (3.27.24): if one result carries it, every result must.
- **`guid` and `correlationGuid`** are set by the result management system, not the producer.

### Claude Code ([sub-agents](https://code.claude.com/docs/en/sub-agents), [env vars](https://code.claude.com/docs/en/env-vars), [permissions](https://code.claude.com/docs/en/permissions), [errors](https://code.claude.com/docs/en/errors); [extended thinking](https://platform.claude.com/docs/en/build-with-claude/thinking))

- **Output cap.** `CLAUDE_CODE_MAX_OUTPUT_TOKENS` defaults per model; for unresolved models the default is 32,000 and the cap 128,000. A request sent without streaming is capped at 64,000. Thinking tokens count toward `max_tokens`.
- **Dispatch limits.** 20 concurrent subagents (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`), and nesting up to three layers below the main conversation (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`).
- **Restricting subagent types.** An `Agent(type…)` list in a subagent's `tools:` is ignored. `Agent(name)` deny rules work in `permissions.deny`. `Task(...)` is an alias for `Agent(...)`.
- **Not documented:** what a caller receives when a subagent stops on `max_tokens`, and what happens when a named `subagent_type` isn't installed.

### Large-output patterns

- **Orchestrator-workers, with work stored outside the conversation.** Workers write to external storage and pass references back, which avoids copying large outputs through the context ([Building effective agents](https://www.anthropic.com/engineering/building-effective-agents); [multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)). This supports part files and dispatch records.
- **Model output is untrusted input.** Validate it like any user input ([OWASP LLM05:2025, Improper Output Handling](https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/)). This supports NFR-10.
- **Stable request identity.** Batch APIs key each request by a unique ID ([Message Batches](https://platform.claude.com/docs/en/build-with-claude/batch-processing)). No authoritative source covers plan IDs or resuming from disk; the design rests on D-3's own rules.

### CVSS v3.1 ([FIRST specification](https://www.first.org/cvss/v3.1/specification-document), §7 and Appendix A)

- **Roundup** returns the smallest one-decimal number at or above its input. Appendix A's integer method (scale by 100,000) avoids float error: a naive float ceiling of 0.1 + 0.2 gives 0.4.
- **Python.** Implement it with `Decimal` built from strings, never floats. Half-up rounding for stored one-decimal values is a separate rule: `quantize(Decimal("0.1"), ROUND_HALF_UP)`.

---

## Recommendations for Spec

1. **Thresholds (OQ-5).** Set them by an output budget, not a guess: a batch's expected output stays at or below a quarter of a 32,000-token response, measured per finding on the fixture at plan time (S-1).
2. **Chain rules (OQ-6).** Define one total order on finding IDs, a redundancy rule (identical sets and contained sub-sequences fold; shared tails are kept), a diverse surfacing rule and a bounded artifact. Changes to the link test go to the PM under R-21 (S-2, S-3).
3. **Fixture (OQ-7).** Pin its shape, sizes and determinism rules (S-4).
4. **Identity.** Every result carries tachi's own hash and no file carries `runAutomationDetails` (S-6). The new recipe is decoupled from Phase 3's match key (S-7). The URI is decided by identity, in one canonical spelling (KB 24).
5. **Dispatch.** Stay within 20 concurrent subagents and three nesting layers, and dispatch in the foreground (S-8). Spike the overflow signals before building the detector (S-9).
6. **Runtime.** Python 3.9 compatibility, and a `yaml`-blocked core-path test (S-11).
7. **Oracle and consequences.** Read the shipped drift forms, keep the PRD's oracle rule (S-12, as amended), and name the consequence scope at spec time.
8. **Asset tags.** Name one source for them (S-13).
9. **Census.** Take a disposition census of the SARIF contract copies, the rewordings and the platform-neutral clauses (KB 23).
10. **Out of scope, as follow-ups:** the snapshot-basename bug, and an `Agent(general-purpose)` deny rule for the isolated-operation profile.
