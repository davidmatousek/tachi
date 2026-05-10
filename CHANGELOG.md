# Changelog

All notable changes to tachi will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Unreleased

### Hardened config-file load (BLP-02 F-2)

Replaced four bash `source`/`eval` config-file load sites with a hardened
`aod_template_load_kv_file` library (KV parser; bash 3.2-compatible).

**New library**: `.aod/scripts/bash/template-config-load.sh` — canonical
config-load primitive. 7-step contract: arg validation → file existence →
single-cat TOCTOU mitigation → per-line iteration → regex validation →
whitelist enforcement → defensive identifier check + `printf -v` assignment.
Internal `eval` carve-out: ONE invocation for bash 3.2 indirect array access
(per ADR-040 Decision Item 7).

**Refactored sites**:
- `scripts/init.sh:106` — defaults.env load (Site A; closes
  TACHI-VULN-6f5a95085056 HIGH). New variables prefixed `STACK_*`
  (e.g., `STACK_TECH_STACK`).
- `.aod/scripts/bash/template-git.sh` reader+writer round-trip
  (Site B; closes TACHI-VULN-bf5496e9fcdf HIGH). Uses
  `<key_case>=lower` mode for aod-kit-version field naming.
- `.aod/scripts/bash/template-substitute.sh` 4× `eval` removal
  (Site C; closes TACHI-VULN-9a7512071b4a MEDIUM). Replaced with
  `${!var}` / `printf -v`.
- `.aod/scripts/bash/template-substitute.sh` `aod_template_load_personalization_env`
  47-line body collapsed to 7-line library delegation (Site D;
  closes TACHI-VULN-4dc6cf8f88ea MEDIUM).

**New env var**: `AOD_FETCH_TIMEOUT` (default 60s; positive integer regex
`^[1-9][0-9]*$`) for `aod_template_fetch_upstream` clone watchdog
(Stream 4; closes TACHI-VULN-851fd6a21ba9 LOW).

**Adopter migration — F-1 contract amendment**: `aod_init_read_validated`
in `.aod/scripts/bash/init-input.sh` now additionally rejects `$`,
`\`, and backtick at the prompt boundary (per B-2 Path R-2). If your
deployment relies on these characters in personalization values, you
must migrate before adopting this release. New error message:
`[init] Input rejected: metachar ($, \, backtick) not allowed; please re-enter.`

**Reference**: ADR-040 (config file parsing hardening). Closes 5 vuln_ids:
TACHI-VULN-6f5a95085056 (HIGH), TACHI-VULN-bf5496e9fcdf (HIGH),
TACHI-VULN-9a7512071b4a (MEDIUM), TACHI-VULN-4dc6cf8f88ea (MEDIUM),
TACHI-VULN-851fd6a21ba9 (LOW).

### SECURITY.md and private disclosure channel (BLP-02 F-3)

Restructured `SECURITY.md` to GitHub-canonical sections (Supported Versions /
Reporting a Vulnerability / What to expect / Scope / Out-of-scope) and enabled
the GitHub repo's **Private vulnerability reporting** toggle so the *Report a
vulnerability* button surfaces on the Security tab.

- **Supported Versions**: latest-minor-only of v4.x; older minors deprecated
  immediately on next minor release.
- **Reporting**: primary path is the Security-tab button; fallback URL retained.
- **Response SLA**: 5 business days to acknowledge.
- **Scope**: tachi codebase + scaffolds-as-shipped in-scope; Claude Code,
  third-party MCP servers, and adopter personalization explicitly out-of-scope.
- **README pointer**: one-line link to `SECURITY.md` from the Community section.

Closes [TACHI-VULN-05abc41ad4cc](.aod/results/security-scan.md) (INFO,
A05 Security Misconfiguration). BLP-02 Wave 3.

### Claude Code permissions baseline (BLP-02 F-4)

Replaced tachi's 26-rule allow-only `.claude/settings.json` with a curated,
categorized, fully-documented permissions baseline. Added
`docs/standards/CLAUDE_PERMISSIONS.md` (operator handbook with per-rule
rationale + opt-out paths) and accepted ADR-041.

The new baseline materializes a four-category model — read-only auto-approve,
local-state auto-approve, destructive `deny`+`ask`, and network host-allowlist
with 19 explicit per-subdomain entries — replacing the prior allow-only posture
that surfaced an unconditionally-permitted `Edit` / `Write` surface and zero
deny rules. Cross-file deny precedence (Claude Code documented behavior) is
honestly documented in the new operator handbook with two worked examples
(within-file rule + cross-file rule).

- **`.claude/settings.json`** — full rewrite, 93 rules (23 deny / 13 ask /
  57 allow across Categories 1/2/4); replaces the prior 26-rule allow-only
  file. Strict JSON (RFC 8259; no JSONC), all rationale lives out-of-line in
  CLAUDE_PERMISSIONS.md so the JSON file stays minimal.
- **`docs/standards/CLAUDE_PERMISSIONS.md`** — new 7-section operator
  handbook (~289 LOC). Covers the four-category model, settings precedence
  (within-file + cross-file with worked examples), per-rule rationale table,
  built-in read-only set, three opt-out paths, and known limitations
  (Bash-pattern fragility R-8, process-wrapper bypass R-9, built-in shadow
  R-10, subdomain non-transitive matching).
- **`docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md`** —
  new ADR (~195 LOC, 6 alternatives evaluated with Pros / Cons /
  Why-Not-Chosen sections). ADR-041 LOC slightly exceeds the FR-008 ~150
  advisory ceiling — accepted with PR-description note per architect P1
  review on the trade-off that trimming would degrade SecOps audit value.
- **`.gitignore`** — FR-003 enforcement fix; appended
  `.claude/settings.local.json` to the project gitignore at line 236
  (T013 build-stage discovery — adopters cloning tachi without the
  maintainer's personal global gitignore would have lacked the pattern,
  risking accidental commits of personal allows/denies).

**Adopter migration note**: Existing `.claude/settings.local.json`
customizations continue to work for adding personal allows on operations
that are not denied at the project level — no breaking change for current
adopters. However, `.claude/settings.local.json` does NOT override project
denies (Claude Code cross-file deny precedence holds across files).
Adopters who relied on local `.claude/settings.local.json` to override a
baseline-denied operation must migrate to the load-bearing override path:
fork-and-edit `.claude/settings.json` directly per CLAUDE_PERMISSIONS.md
§Opt-Out-Paths Path 2.

Reference: [ADR-041](docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md)
(claude permissions baseline). BLP-02 Wave 4 of 5.

### Pre-commit secret-scanning defaults (BLP-02 F-5)

Shipped a default-secure pre-commit secret-scanning hook (gitleaks via the
`pre-commit` framework) with a tachi-authored wrapper that augments the
refused-commit stderr to a four-item structured contract (rule ID + file:line
+ `SKIP=gitleaks` bypass + docs link). Added the operator handbook
`docs/standards/PRECOMMIT_HOOKS.md` (per-rule rationale catalog +
installation paths + bypass mechanisms + known limitations) and the architecture
decision record ADR-042. Closes the BLP-02 enterprise-hardening initiative
(5/5 — final feature alongside F-1 substitution surface, F-2 config-file
parsing, F-3 SECURITY.md / private disclosure, F-4 Claude Code permissions
baseline).

The hook runs `gitleaks git --pre-commit --redact --staged --verbose
--config=.gitleaks.toml` on every `git commit`, scanning **staged content
only**. Coverage: ~150+ default credential patterns (AWS / GitHub /
OpenAI / Anthropic / Stripe / private key blocks) inherited via `useDefault =
true`, plus three tachi-additive allow-lists (env-var placeholders, convention
paths, vendored/generated/archived content) and two warn-only custom rules
(`tachi-personalization-env`, `tachi-security-exceptions-jsonl`). Adopter
opt-in posture is split: **new adopters** receive a default-Y prompt during
`scripts/init.sh` first-run (skipped silently in non-TTY contexts; flag
overrides `--precommit` and `--no-precommit`); **existing adopters do NOT
auto-receive the local hook on `git pull`** (FR-010) — to enable, run
`pre-commit install` from the repo root after `git pull`.

- **`.pre-commit-config.yaml`** — new pre-commit framework config pinning
  gitleaks v8.30.1 via the wrapper script. The `rev` field carries the tag
  for human readability and is replaced with a pinned commit SHA via
  `pre-commit autoupdate --freeze` at install time (per ADR-042 §Decision
  Item 6 supply-chain hygiene).
- **`.gitleaks.toml`** — new gitleaks v8.30.1+ config inheriting the upstream
  default ruleset (`[extend] useDefault = true`), adding three allow-lists
  scoped to tachi conventions, and adding two warn-only custom rules for
  defense-in-depth on `.aod/personalization.env` value leakage and manual
  edits to `.security/exceptions.jsonl`.
- **`.aod/scripts/bash/precommit-wrap.sh`** — new ~50 LOC bash 3.2-compatible
  wrapper that invokes gitleaks and augments the refused-commit stderr with
  the four-item contract (rule ID + file:line + bypass guidance + docs
  link). Preserves gitleaks' exit code verbatim (Pre-Mortem FM-5 pattern:
  capture rc BEFORE augmentation). LOCAL-ONLY scope — the CI parity workflow
  invokes gitleaks directly to preserve native SARIF output.
- **`.aod/personalization.env.example`** — new opt-in template documenting
  the `AOD_PERSONALIZATION_*` keys consumed by `scripts/init.sh` and the F-2
  substitution pipeline. Allow-listed in `.gitleaks.toml` so the placeholder
  values do not trip the secret-scanning hook.
- **`docs/standards/PRECOMMIT_HOOKS.md`** — new ~250 LOC operator handbook
  with 9 sections: Why this hook ships / Installation paths (3) / What gets
  scanned with per-rule rationale catalog / Bypass mechanisms / Refused-commit
  error message contract / CI parity / Re-init behavior / Known limitations
  (7 items including the v3.5.0 framework floor justification per Architect
  CONCERN-3) / Adopter customization (per-rule additions, merge conflict
  guidance, tool swap path, directory-rename considerations).
- **`docs/architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md`**
  — new ADR (~265 LOC, 9 alternatives evaluated with Pros / Cons /
  Why-Not-Chosen sections including the corrected note that **trufflehog v3
  runtime is Go, not Python** as the original PRD comparison matrix had it).
  Status `Proposed` at branch HEAD; flips to `Accepted` at squash-merge per
  /aod.deliver T034.
- **`.github/workflows/gitleaks.yml`** — new CI parity workflow running
  gitleaks against full-repo content on every PR as a back-stop for
  `git commit --no-verify` deliberate bypass. Downloads the gitleaks binary
  directly with SHA256 verification (NOT the proprietary `gitleaks-action@v2`
  which requires a paid `GITLEAKS_LICENSE` for org repos). SARIF upload to
  GitHub Code Scanning surfaces findings inline on the PR Files-changed tab.
- **`scripts/init.sh`** — delta: new prompt phase `Install pre-commit
  secret-scanning hook? [Y/n]` with default-Y in TTY contexts, silently
  skipped in non-TTY. Two flag overrides: `--precommit` forces install
  regardless of TTY/answer; `--no-precommit` forces skip. The flags affect
  **first-run only** (init.sh is one-shot per F-1 #248). Pre-commit framework
  v3.5.0 floor check emits a `WARN` (not abort) if the system version is
  below the floor.
- **`README.md`** — delta: one-line pointer to
  `docs/standards/PRECOMMIT_HOOKS.md` adjacent to the F-3 SECURITY.md
  pointer. Single-line addition; the security/community section is otherwise
  unchanged.

**Synthetic-fixture rule-interaction test**: `tests/fixtures/gitleaks-rule-interaction/`
ships 16 synthetic fixtures (6 should-fire real-format credentials + 10
should-NOT-fire allow-listed/excluded paths) with a co-located runner
(`run.sh`) and a pytest matrix (`tests/scripts/test_init_precommit_matrix.py`)
that exercises the init.sh prompt-flag combinations. Catches schema breaks
at gitleaks pin-bump time and accidental allow-list misconfigurations on
adopter-driven `.gitleaks.toml` modifications (Architect C-4 preventive
verification).

**Existing-adopter opt-in path**: pulling the F-5 update does NOT install
`.git/hooks/pre-commit`. **To enable, run `pre-commit install` from the repo
root after `git pull`.** Three opt-out paths cover the legitimate scenarios
(`SKIP=gitleaks` per-commit, `# gitleaks:allow` inline comment,
`pre-commit uninstall` full opt-out); `git commit --no-verify` is honestly
disclosed as a one-flag bypass with the CI parity workflow as the back-stop.

Reference: [ADR-042](docs/architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md)
(pre-commit secret-scanning default). BLP-02 Wave 4+ of 5 — initiative complete.

### Bug Fixes

* **250:** Adversarial Unit Extraction Hot-Fix + Permanent CI Test Process Hardening — eliminates the cold-cache 300s subprocess timeout class on `macos-latest` that admin-overrode F-248's closing CI run (`25314246672`). **Three new pytest modules** at `tests/scripts/`: `test_template_substitute_unit.py` (8 substitution-semantics cases extracted from integration to unit-level), `test_init_input_unit.py` (5 input-rejection cases incl. positive-path canary FR-007), `test_substitute_shim_canary.py` (TC-1 closure asserting `shopt -u patsub_replacement` shim stays in `template-substitute.sh`). Process-substitution invocation pattern (`< <(printf '%s\n' "$INPUT")`) replaces shell pipe to avoid pipe-subshell `printf -v` caller-scope assignment loss (R-1 mitigation, FR-006). `LC_ALL=C` pinned in every per-case subprocess invocation to defend the multibyte UTF-8 case (R-4, FR-008). 12 init.sh integration invocations dropped to 5 (FR-014 / SC-003) — case 13 trailing-newline byte-identity + `test_no_residual_placeholders_after_init` + 3 retained integration modules. **Phase 6 Option Z scope expansion** (mid-build, authorized after CI run `25325616748` exposed recurring root causes the original F-250 PRD scope did not address; TC-4 fences explicitly relaxed; FR-019/FR-020 byte-unchanged invariants on `template-substitute.sh` and `init-input.sh` PRESERVED): session-scoped `init_run` fixture in `tests/scripts/conftest.py` collapses 5 module-scoped duplicates → 1 canonical clone (drops macos cold-cache cost from 5×300s+ to 2×300s+); asymmetric file-set check in `test_init_sh_substitution.py` (drops are FAIL — substitution regression; additions are TOLERATED — repo growth not a regression); substitution-target-only baseline restricted ~600 → ~53 files via refactored `tests/fixtures/regenerate-baseline.sh`; `run_init_in_clone(timeout_sec=)` default bumped 300s → 900s; pytest `--timeout` 360s → 1080s; `tachi-pytest.yml` `paths:` filter and `pytest` invocation extended to include the 3 new unit modules (workflow filter completeness gap). **Observed KPIs on PR #253 own merge**: `macos-latest` 5m19s wall time (target ≤15 min — FAR under; baseline band 30-40 min), `ubuntu-latest` 1m29s (unchanged), CI savings vs baseline `25314246672` ≈ 25-35 min per run (SC-005 ≥25 min target ✓). Both legs green; release-please PR #254 (`chore(main): release 4.28.1`) auto-opened ~35s post-merge. **ADR-039** (Test Architecture: Fixture Scope and Asymmetric Baseline, Accepted 2026-05-04) records the new test-architecture canon repo-wide. **KB Entry 2** captures the meta-lesson: when CI evidence contradicts a PRD's root-cause assumption mid-build, authorize a documented scope expansion (Phase 6 header naming relaxed fences) rather than papering over with retry loops or quick patches; preserved byte-unchanged invariants keep the relaxation reviewable. **Sustained tracking window** (T021) 2026-05-04 → 2026-05-18 captures the next 5 merges to confirm SC-002/SC-004/SC-005 hold under multi-merge load. Helper contracts (ADR-038) byte-unchanged: `git diff main -- .aod/scripts/bash/template-substitute.sh .aod/scripts/bash/init-input.sh` empty post-merge. 29/29 tasks complete (T020 release-please verification + T021 initial KPI sample closed by `/aod.deliver` retrospective). PR #253 squash-merged 2026-05-04 with `fix(250):` Conventional Commit title per R12 belt-and-suspenders enforcement. See `specs/250-adversarial-unit-extraction-hotfix/` for spec/plan/tasks/delivery.

### Features

* **248:** Substitution Surface Hardening (BLP-02 Wave 1) — `scripts/init.sh` substitution swap from sed to bash parameter expansion (FR-001), new prompt input validator `aod_init_read_validated` rejecting newline / NUL / control character / over-length input (FR-005), re-init pre-flight check halting on existing `.aod/personalization.env` (FR-003), residual placeholder scan on `personalized` category from `.aod/template-manifest.txt` (FR-004 closed-contract; canonical 12 only), constitution template migration from `sed -i` cleanup to `cp .aod/templates/constitution-clean.md` (FR-008), and `.gitignore` default for `.aod/personalization.env` (FR-006 local-only posture; opt-in commit via `git rm --cached` migration documented in `specs/248-substitution-surface-hardening/contracts/personalization-schema.md`). Stream 1 substitution swap measured +658% init-time delta (50.7s vs 6.7s baseline) — accepted trade-off documented in ADR-038 §Consequences: bash parameter expansion preserves literal metachars (`AT&T`, `\1\2 backref`, regex metachars, pipes, slashes) verbatim where sed corrupts them, and init.sh is one-time per adopter so the +43s first-run cost is not recurring. **5 NEW pytest test files** (`tests/scripts/test_init_sh_*.py`): Test-1 fixture-replay byte-comparison (skipped until baseline regenerated post-Stream-1), Test-2 ≥13 adversarial inputs covering substitution + rejection classes, Test-4 constitution byte-compare, Test-5' self-delete preservation. **2 NEW templates** (`.aod/templates/constitution-{clean,instructional}.md`) shipping the pre-stripped post-substitution variant alongside the full instructional-block variant. **1 NEW helper** (`.aod/scripts/bash/init-input.sh` providing `aod_init_read_validated`). **ADR-038** (Status: Proposed at branch HEAD, Accepted at architect promotion in Wave 5 T036). **Migration command for adopters previously committing `personalization.env`**: `git rm --cached .aod/personalization.env && git commit -m "chore: gitignore .aod/personalization.env per F-248 default posture"` (stops tracking without deleting local copy; `/aod.update` continues to re-substitute from local snapshot). See `specs/248-substitution-surface-hardening/` for spec/plan/tasks/contracts.

* **237:** Mobile Top 10 Coverage Bundle — `spoofing` + `tampering` + `info-disclosure` + `privilege-escalation` + `repudiation` enriched (BLP-01 Tier 2 second feature after F-6 ML Top 10 closure; **fourth execution of Heuristic A enrichment branch**; **first at four-or-five-agent scope** with M8 dual-host carve-up). Closes OWASP **Mobile Top 10:2024** on the BLP-01 Coverage Matrix (M1 + M3 → spoofing; M2 + M4 + M7 → tampering; M5 + M6 + M9 + M10 → info-disclosure; M8 dual-host → privilege-escalation + repudiation); combined with prior coverage: **OWASP four-framework total = 40/40 Covered** (LLM Top 10:2025 = 10/10 + Agentic Top 10:2026 = 10/10 + ML Top 10:2023 = 10/10 + Mobile Top 10:2024 = 10/10) — **second framework family closure milestone** (after the OWASP AI security family closed at F-6). **10 additive host-file edits** across 5 host pairs: `.claude/agents/tachi/spoofing.md` + companion (M1 / M3 mobile credential + auth/authz Pattern Categories N+1 / N+2); `.claude/agents/tachi/tampering.md` + companion (M2 / M4 / M7 mobile supply chain + IPC input validation + binary protections Pattern Categories 11 / 12 / 13); `.claude/agents/tachi/info-disclosure.md` + companion (M5 / M6 / M9 / M10 mobile communication + privacy + data storage + cryptography Pattern Categories N+1 / N+2 / N+3 / N+4); `.claude/agents/tachi/privilege-escalation.md` + companion (M8 privilege-gain variant Pattern Category 11); `.claude/agents/tachi/repudiation.md` + companion (M8 accountability-loss variant Pattern Category 9). **M8 dual-host cross-agent decomposition** (ADR-036 D-4): M8 Security Misconfiguration decomposes across two owning STRIDE categories — privilege-gain variant (`privilege-escalation` host: debug endpoints + ContentProvider exports + missing app-attestation enabling privilege gain) AND accountability-loss variant (`repudiation` host: missing audit logging + disabled crash reporting + debug log leakage enabling audit-trail loss); same architecture surfaces both — neither is a duplicate. **Third BLP-01 sub-pattern with cross-agent decomposition** after F-5's Q1 SPLIT (vector axis) and F-6's ML06 two-facet split (corpus-side vs artifact-side); first at the architectural-tell layer rather than the entry-decomposition layer. **M4 cross-agent boundary with F-1 `output-integrity`** (ADR-036 D-5): Cat 12 Mobile IPC Input Validation (tampering host) owns mobile-IPC-input-side validation (Intent extras / URL-scheme parameters / deep-link payloads / exported ContentProvider gates / pasteboard injection); F-1's `output-integrity` agent owns LLM-output-side sanitization (LLM-generated content flowing into browser/SQL/shell sinks); disjoint architectural-tells prevent duplicate emission on hybrid LLM+mobile architectures. **ATT&CK Mobile catalog gap propagation 3-of-3 prose-only (worst-case scale)**: all 3 cited ATT&CK Mobile techniques (T1474 Supply Chain Compromise + T1626 Abuse Elevation Control Mechanism + T1398 Boot or Logon Initialization Scripts) are NOT catalog-resolvable per `mitre-attack.yaml` (verified 0/0/0 absent at Wave 1.0 T012) and ship as prose-only worked-example narratives (NOT in references arrays); 0 of 3 are catalog-resolvable. ADR-036 D-7 codifies the rule per F-A2 referential-integrity contract; F-7 establishes worst-case scale extending F-5 1-of-1 + F-6 3-of-6 ATLAS-gap precedent. **Zero schema bump** (`schemas/finding.yaml` unchanged at 1.8): F-7 reuses existing `S` + `T` + `I` + `E` + `R` STRIDE prefixes; **fourth BLP-01 detection feature with no schema bump** after F-3 single-agent + F-5 two-agent + F-6 three-agent; **first at four-or-five-agent scope**; explicit asymmetry to ADR-031 D8 regex-alternation rule (does not apply when enrichment reuses existing prefixes); explicit asymmetry to F-1 / F-2 / F-4 minor bumps. **28-file zero-edit invariant preserved** (10 modified — 5 host agents + 5 companion catalogs; 18 NOT-edited — 9 other agents + 7 infrastructure consumers + 2 non-F-7 detection companions). **ADR-036** (Status: Accepted at squash commit `e962a0e`) with **10 Decisions**: D-1 enrichment-vs-new-agent at four-or-five-agent scope (rejected `mobile-platform` 13th-agent alternative; signal-class cleave aligns precisely with existing five STRIDE host-agent boundaries); D-2 additive-only edits across 10 host files; D-3 canonical 11-row Mobile Top 10 sub-pattern → owning-agent mapping table populated COMPLETE (with severity-hint annotation column; M8 occupies 2 rows for dual-host carve); D-4 M8 dual-host disjoint architectural-tells; D-5 M4 cross-agent boundary with F-1 `output-integrity`; D-6 no schema bump (fourth BLP-01 detection feature reusing existing prefixes; first at four-or-five-agent scope); D-7 ATT&CK Mobile catalog gap codified (3-of-3 prose-only worst-case); D-8 no functional orchestrator/dispatch edit (all 5 STRIDE host agents already registered); D-9 Pattern Category Disambiguation across 5 companion catalogs; D-10 no `source_attribution` populator wiring extension (F-A3 deferral; third BLP-01 detection feature to defer populator wiring after F-5 + F-6). **New `examples/mobile-banking-app/` baseline** (7th example — WellnessBank Android banking app archetype with 6 mobile-platform topology indicators: exposed deep-link Intent extras + hybrid WebView + biometric step-up + secure-storage paths + cleartext HTTP residual + binary-protection gaps): 16 NEW F-7 findings emerged on regen; 62 total findings on regen. 6/6 byte-identical baselines under `SOURCE_DATE_EPOCH=1700000000` (web-app + microservices + ascii-web-api + mermaid-agentic-app + free-text-microservice + maestro-reference); **mobile-platform topology gate (FR-016)** properly filters mobile-tier categories on non-mobile architectures (no Android/iOS surface, no deep-link Intent receivers, no exported ContentProvider/Service, no biometric APIs, no secure-storage APIs, no mobile transport surface, no mobile binary). Test infrastructure update at `tests/scripts/test_backward_compatibility.py`: removed F-7 hosts from `DETECTION_AGENT_PATHS` (8 → 4) and added `tachi-spoofing` + `tachi-info-disclosure` + `tachi-privilege-escalation` + `tachi-repudiation` to `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset (5 → 9). **56 enrichment tests** in new pytest suite `tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py` (line caps + structural byte-identity presence + MAESTRO grep + Pattern Category Disambiguation + new pattern categories + per-fixture references-array + ATT&CK Mobile catalog-resolvability + MANDATORY Read directive); -98 lines applied via `/aod.document` /simplify pass — wave-rot lineage trim from module docstring + per-feature delivery narration collapse in `test_backward_compatibility.py` + ADR-036 D-N cross-axis prose trim from 4 test docstrings + Section G assertion message simplification + `_all_fixture_refs_joined()` converted from function to `@pytest.fixture(scope="module")` (eliminates 22 redundant YAML parses: 33 → 11 per Section G parametrize); 56/56 pass in 0.22s; backward-compat zero-edit invariant test passes. 82/82 build tasks complete (100%); zero schema-bump scope; zero new runtime dependencies; PR #238 squash-merged 2026-04-29 with `feat(237):` Conventional Commit title (R12 release-please mitigation enforced); release-please PR #239 fired correctly within ~30s post-merge. **OWASP four-framework total now 40/40** — second framework family closure milestone (LLM Top 10 2025 + Agentic Top 10 2026 + ML Top 10 2023 closed at F-6 / Mobile Top 10 2024 closed at F-7). See `specs/237-mobile-top-10-coverage-bundle/` for spec/plan/tasks/delivery.

* **232:** ML Top 10 Coverage Bundle — `tampering` + `data-poisoning` + `model-theft` enriched (BLP-01 Tier 2 first feature after F-1..F-5 Tier 1 closure; **third execution of Heuristic A enrichment branch**; **first at three-agent scope**). Closes OWASP **ML Top 10:2023** on the BLP-01 Coverage Matrix (six F-6 closures ML01/ML03/ML04/ML06/ML07/ML08 + pre-existing ML02/ML05/ML10 + F-1's ML09 documentation-only bundling); combined with prior coverage: **OWASP three-framework total = 30/30 Covered** (LLM Top 10:2025 = 10/10 + Agentic Top 10:2026 = 10/10 + ML Top 10:2023 = 10/10) — **full closure of the OWASP AI security framework family** by tachi's existing detection agents. **6 additive host-file edits** across 3 host pairs: `.claude/agents/tachi/tampering.md` + `.claude/skills/tachi-tampering/references/detection-patterns.md` (Cat 10 Adversarial Input Manipulation appended; +Disambiguation extension; Primary Sources extended); `.claude/agents/tachi/data-poisoning.md` + `.claude/skills/tachi-data-poisoning/references/detection-patterns.md` (Cat 8 Transfer Learning Supply Chain + Cat 9 Feedback-Loop Model Skewing + Cat 10 Predictive-ML Supply Chain Completeness; +Disambiguation extension); `.claude/agents/tachi/model-theft.md` + `.claude/skills/tachi-model-theft/references/detection-patterns.md` (Cat 12 Model Inversion + Cat 13 Membership Inference + Cat 14 Predictive-ML Artifact Supply Chain; +Disambiguation extension; Primary Sources extended). **ML06 two-facet cross-agent decomposition** (ADR-035 D-4): AI Supply Chain entry decomposes into corpus-side (data-poisoning Cat 10 over Public Dataset Repository / Internal Merchant Transaction History / Feast Feature Store) AND artifact-side (model-theft Cat 14 over MLflow Model Registry / Weight Checkpoint Storage); **second BLP-01 sub-pattern with cross-agent decomposition** after F-5's Q1 SPLIT vector axis; first across two distinct host agents at three-agent scope (architectural-surface axis). **ML03 vs ML04 ATLAS-shared-but-mitigation-disjoint** (ADR-035 D-5): both target FraudDetectionML Prediction API and cite AML.T0024 (Exfiltration via ML Inference API), but ML03 → output-minimization mitigations (logit clipping / output sanitization) vs ML04 → inference-privacy mitigations (differential privacy / membership-query budgeting); **first BLP-01 feature where two OWASP entries share an ATLAS catalog reference but get independent Pattern Categories** with disjoint mitigation taxonomies. **ATLAS catalog gap propagation 3x F-5 scale**: 3 of 6 cited ATLAS techniques (AML.T0015 + AML.T0019 + AML.T0031) are NOT catalog-resolvable per `mitre-atlas.yaml` and ship as prose-only worked-example narratives (NOT in references arrays); 3 of 6 (AML.T0018 + AML.T0020 + AML.T0024) are catalog-resolvable and ship in references arrays; ADR-035 D-7 codifies the rule per F-A2 referential-integrity contract. **Zero schema bump** (`schemas/finding.yaml` unchanged at 1.8): F-6 reuses existing `T-{N}` (tampering) + `D-{N}` (data-poisoning) + `LLM-{N}` (model-theft) prefixes; **third BLP-01 detection feature with no schema bump** after F-3 single-agent + F-5 two-agent; **first at three-agent scope**; explicit asymmetry to ADR-031 D8 regex-alternation rule (does not apply when enrichment reuses existing prefixes); explicit asymmetry to F-1 / F-2 / F-4 minor bumps. **22-file zero-edit invariant preserved** (10 other agents + 7 infrastructure consumers + 5 non-F-6 detection companions NOT-edited; F-6 = 30 detection-tier files post-F-5 inventory + 6 file edits + 0 net-new). **F-A2 referential-integrity contract — sixth validation** (three new producers in one feature: T-{N} via tampering host + D-{N} via data-poisoning host + LLM-{N} via model-theft host; 8 independent populators production-tested post-F-6 cumulative). **ADR-035** (Status: Accepted at squash commit `e325375` post-merge SHA fill at T060) with **10 Decisions**: D-1 enrichment-vs-new-agent at three-agent scope (signal-class identity rationale per Heuristic A); D-2 additive-only edits across 6 host files; D-3 **canonical 8-row mapping table populated COMPLETE** (7 closure rows + 4 reference rows + severity-hint annotation column); D-4 ML06 two-facet split (corpus-side data-poisoning Cat 10 vs artifact-side model-theft Cat 14); D-5 ML03 vs ML04 disjoint architectural-tells on shared AML.T0024 prediction-API surface; D-6 no schema bump (third BLP-01 detection feature reusing existing prefixes; first at three-agent scope); D-7 no consumers-list edit; D-8 no functional orchestrator/dispatch edit; D-9 Pattern Category Disambiguation across 3 companion catalogs (tampering Cat 10 vs Cat 1-9 + data-poisoning Cat 8/9/10 vs Cat 1-7 + model-theft Cat 12/13/14 vs Cat 1-11); D-10 no `source_attribution` populator wiring extension (F-A3 deferral; second BLP-01 detection feature to defer populator wiring after F-5). **New `examples/predictive-ml-app/` baseline** (7th example; tachi's first non-LLM ML topology baseline — fraud-detection predictive-ML architecture): 9 NEW F-6 findings emerged on regen — T-10 (tampering Cat 10 ML01 — Adversarial Input Manipulation) + D-8 (Cat 8 ML07 Transfer Learning) + D-9 (Cat 9 ML08 Model Skewing) + D-10/D-11 (Cat 10 ML06 corpus-side two findings) + LLM-1/LLM-2 (model-theft Cat 12/13 ML03/ML04 disjoint-tells) + LLM-3/LLM-4 (Cat 14 ML06 artifact-side two findings); 43 total findings on regen. 6/6 byte-identical baselines under `SOURCE_DATE_EPOCH=1700000000` (web-app + microservices + ascii-web-api + mermaid-agentic-app + free-text-microservice + maestro-reference); **predictive-ML topology gate (FR-016)** properly filters ML-tier categories on non-predictive-ML architectures (zero false-positive emission on agentic-app baseline regen verified). Test infrastructure update at `tests/scripts/test_backward_compatibility.py`: removed F-6 hosts from `DETECTION_AGENT_PATHS` (10 → 8) and added `tachi-tampering` + `tachi-data-poisoning` to `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset (3 → 5; documentation discrepancy: tasks.md asserted "5 → 7" but actual baseline was 3 — flagged in T059 retrospective). **36 enrichment tests** in new pytest suite `tests/scripts/test_ml_top_10_coverage_bundle_enrichment.py` (line caps + MAESTRO grep + MANDATORY Read directive + Pattern Category Disambiguation + new pattern categories + per-fixture references-array + ATLAS catalog-resolvability sweeps; -41 lines applied via /aod.document /simplify pass — module-docstring brittle line-count snapshot trim + assertion-message wave-rot parenthetical drop + Section F prose-only sweep parametrize collapse + test_backward_compatibility.py rule-form comment refactor); 36/36 pass in 0.23s; 13/14 backward-compat tests PASS / 1 SKIP (pre-existing F-142 mermaid-agentic-app limitation, unchanged by F-6). **Branch History Incident — PR #233 partial-merge cherry-pick recovery**: PR #233 squash-merged at `b84552a` with only Wave 1.0+1.1 (16/64 tasks); remaining 38 tasks cherry-picked onto `232-build-closeout` and shipped via PR #235 squash-merged 2026-04-28T17:03:28Z (commit `e325375`); release-please PR #234 v4.25.0 auto-aggregates BOTH `feat(232)` commits (open since PR #233 merge; updated 22s post-PR-#235-merge — F-212 incident NOT invoked); ~1h cherry-pick recovery overhead added but did not delay 2.5-day envelope. 64/64 tasks complete (100%); zero new runtime dependencies; PR #233 + PR #235 squash-merged 2026-04-28 with `feat(232):` Conventional Commit titles per R12 belt-and-suspenders enforcement. See `specs/232-ml-top-10-coverage-bundle/` for spec/plan/tasks/delivery.

* **229:** llm10 unbounded consumption verification — BLP-01 Tier 1 fifth feature (after F-1 `output-integrity`, F-2 `misinformation`, F-3 `tool-abuse` ASI07 enrichment, F-4 `human-trust-exploitation`); **second execution of Heuristic A enrichment branch** (vs. F-3 single-agent first execution); **first execution at two-agent scope** — `denial-of-service` + `model-theft` jointly carve the LLM10 surface across availability and economic damage axes. Closes OWASP **LLM10:2025 Unbounded Consumption** on the BLP-01 Coverage Matrix; combined with F-4's ASI09 closure: **OWASP AI top-10 = 20/20 Covered** (LLM Top 10:2025 = 10/10 + Agentic Top 10:2026 = 10/10) — full closure milestone across both AI threat frameworks. **4 additive host-file edits**: `.claude/agents/tachi/denial-of-service.md` (additive metadata + `## Purpose` LLM-inference-exhaustion extension + Detection Workflow Step 5 references list, +5 lines); `.claude/skills/tachi-denial-of-service/references/detection-patterns.md` (Cat 12 Inference-Request Flooding + Cat 13 Context-Window Latency + Pattern Category Disambiguation appended after Cat 11; Primary Sources extended with `OWASP LLM10:2025`, +51 lines); `.claude/agents/tachi/model-theft.md` (`## Purpose` cost-amplification + denial-of-wallet extension, +2 lines); `.claude/skills/tachi-model-theft/references/detection-patterns.md` (Cat 10 Cost Amplification + Cat 11 Denial-of-Wallet + Pattern Category Disambiguation appended after Cat 9; Primary Sources extended; T1496 prose-only on Cat 10/11, +57 lines). **Q1 SPLIT cross-agent vector decomposition** (first BLP-01 sub-pattern with cross-agent vector decomposition within a single OWASP catalog entry): Cat 13 Context-Window Exhaustion bifurcates into Vector A (latency-DoS, owned by `denial-of-service`) and Vector B (cost-DoW, owned by `model-theft`); same architecture surface, disjoint mitigation vocabularies. **Q3 severity-floor 2-condition CRITICAL rule** on Cat 11 (Denial-of-Wallet): defaults to HIGH; CRITICAL only fires when (a) multi-tenant freemium structurally evident AND (b) BOTH per-tenant token budget AND cost alerting absent — first BLP-01 finding-emission rule with a 2-condition gated severity floor. **T1496 prose-only on Cat 10/11**: MITRE ATT&CK T1496 (Resource Hijacking) appears in worked-example narrative prose but is explicitly absent from any `references` array entry across both companions and all 5 fixtures (T1496 not catalog-resolvable per `schemas/taxonomy/mitre-attack.yaml`); 2 prose mentions / 0 references-array entries verified. **Zero schema bump** (`schemas/finding.yaml` `id.pattern` regex unchanged at 12-prefix family `S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE`) — F-5 reuses existing `D-{N}` (DoS) and `LLM-{N}` (model-theft) prefixes; second BLP-01 detection feature with no schema bump after F-3 and **first at two-agent scope**; explicit asymmetry to ADR-031 D8 regex-alternation rule (does not apply when enrichment reuses existing prefixes); explicit asymmetry to F-1 / F-2 / F-4 minor bumps. **5/5-dimension reduction re-holds at two-agent scope** (no new agent file / no new skill directory / no schema bump / no consumers-list edit / no functional orchestrator-dispatch edit per Q2 default-NO at architect plan-day decision). **24-file zero-edit invariant preserved** (post-F-4 inventory: 28 detection-tier files; F-5 edits 4 host files; the remaining 24 stay byte-identical). **F-A2 referential-integrity contract — fifth validation** (two new producers in one feature: D-{N} via DoS host + LLM-{N} via model-theft host); 5 independent populators production-tested post-F-5 (F-1 OI + F-2 MI + F-3 AG enrichment + F-4 TE + F-5 D + LLM combined); regex-agnostic `parse_threats_findings` requires zero validator changes. **ADR-034** (Status: Accepted at squash commit `e086d31`) with 9 Decisions: D1 enrichment-vs-new-agent at two-agent scope (signal-class identity rationale per Heuristic A — infrastructure-resource-exhaustion same-class as DoS availability-degradation surface; extraction-driven-resource-abuse same-class as model-theft Category 6 unbounded-inference-consumption surface); D2 additive-only edits across 4 host files; D3 **canonical 5-row LLM10 sub-pattern → owning-agent mapping table populated COMPLETE** with severity-hint annotation column (audit deliverable per team-lead MEDIUM-1); D4 no schema bump; D5 no consumers-list edit; D6 no functional orchestrator/dispatch edit; D7 Pattern Category Disambiguation across two companion catalogs (DoS Cat 9 vs Cat 12/13 + model-theft Cat 6 vs Cat 10/11 boundary subsections); D8 no `source_attribution` populator wiring extension (F-A3 deferral); D9 public-only governance per SDR-001 Option C. **Wave 2 pipeline regen** on `examples/agentic-app/` surfaces 4 NEW findings — D-10 (Cat 12 Inference-Flooding, Critical), D-11 (Cat 13 Context-Window Latency Vector A, Critical), LLM-15 (Cat 10 Cost-Amplification, Critical), LLM-16 (Cat 11 Denial-of-Wallet Vector B, High per Q3 default — single-tenant) — all citing `OWASP LLM10:2025` with cohesive category rendering preserved (single Section 3.5 DoS + single Section 3.8 LLM in `threat-report.md` with no fragmentation; correlation group CG-8 binds all 4 in Theme 5 of regenerated narrative). **22 functional requirements** (FR-001 through FR-022) + **22 success criteria** (SC-001 through SC-022) all PASS; **26 enrichment tests** in new pytest suite `tests/scripts/test_llm10_unbounded_consumption_enrichment.py` (line caps + MAESTRO grep + MANDATORY Read directive + Pattern Categories + Disambiguation + T1496 prose-only + per-fixture references-array + Q3 severity-floor + agent metadata + Detection Workflow Step 5; -34 lines applied via /aod.document /simplify pass — REPO_ROOT consolidation + WHAT-comment trim + 16-line internal-monologue collapse + leaky helper docstring shrink); backward-compat baselines 5/5 PASS (+1 bonus = 6/6) under `SOURCE_DATE_EPOCH=1700000000`; 1 pre-existing F-142 mermaid-agentic-app SKIP unrelated to F-5. Test infrastructure update at `tests/scripts/test_backward_compatibility.py`: removed F-5 hosts from `DETECTION_AGENT_PATHS` (12 → 10) and added to `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset (extending F-3's single-host pattern to multi-host enrichment branch). 85/85 tasks complete; zero new runtime dependencies; PR #230 squash-merged 2026-04-27 with `feat(229):` Conventional Commit title; release-please PR #226 (v4.24.0) opened cleanly within ~30s of squash-merge per R12 belt-and-suspenders enforcement (no F-212 empty-marker fallback invoked). See `specs/229-llm10-unbounded-consumption-verification/` for spec/plan/tasks/delivery.

* **224:** human-trust-exploitation threat agent (OWASP ASI09:2026 communication axis) — BLP-01 Tier 1 fourth feature (after F-1 `output-integrity`, F-2 `misinformation`, F-3 `tool-abuse` ASI07 enrichment); third execution of Heuristic A standalone-new-agent branch. Closes ASI09:2026 **communication axis** on the BLP-01 Coverage Matrix (autonomy axis remains attributed to `agent-autonomy`). **New AI-tier detection agent** `.claude/agents/tachi/human-trust-exploitation.md` (122 lines, ≤150 cap) + companion skill `tachi-human-trust-exploitation/` with 5 numbered pattern categories: Undisclosed AI Authorship, Authority Claim Emission, Persuasion Manipulation, Persona Boundary Violation, Synthetic Relationship Exploitation. **Two-part emission gate (FR-013)**: agent fires only when (a) Process is consumer-facing AI keyword match AND (b) at least one human-user-facing emission indicator (outgoing flow to human-named External Entity OR consumer-facing prose match OR persistent persona/multi-turn dialogue OR wellness/coaching authority). Five categories emit one finding each on qualifying baselines; zero false-positive emission on non-consumer-facing baselines verified via R6 Wave 4 sweep. **Schema bump 1.7 → 1.8** (`schemas/finding.yaml`) — `id.pattern` regex extended from `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\d+$` to `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$` (12-prefix family); 3rd application of ADR-030 Decision 8 regex-alternation minor-bump rule. **Three-prefix-family discipline within agentic surface** (`AG` autonomy-axis / `AGP` multi-agent-topology / `TE` communication-axis) plus the LLM family from F-2 (`LLM` input-side / `OI` output-sanitization / `MI` factual-integrity) yields a **6-prefix-family AI threat surface** with Heuristic A signal-class boundary preservation across both AI-tier sub-categories. **26-file zero-edit invariant preserved INCLUDING `agent-autonomy.md` NOT-edit** despite the ASI09 sub-scope carve-up — the carve-up is documented at the ADR-033 D2 layer only; `agent-autonomy.md`'s `owasp_references` already lists ASI-09 (verified at T004) so no metadata edit was needed. **F-4 = third net-new producer of `source_attribution`** (after F-1 + F-2; F-3 used the enrichment-branch pattern), proving F-A2 referential-integrity contract against three independent populators. **ADR-033** (Status: Accepted) with 10 numbered body items: D1-D8 PRD-original (new-agent adoption, Heuristic A signal-class partition resolving four scope boundaries plus the ASI09 sub-scope carve-up between agent-autonomy autonomy axis and human-trust-exploitation communication axis, lean-agent ADR-023 detection-variant conformance, regex-alternation Complex-Shape Clarifier 3rd application, 26-file zero-edit invariant preservation including critical zero-diff on `agent-autonomy.md`, Proposed → Accepted dual-commit governance), D9 **Naming Disambiguation** (HIGH-1 — explicit `human-trust-exploitation` agent name hyphen-cased / agent-to-human ASI09 scope vs. existing `agentic_pattern: "trust_exploitation"` schema-enum value underscore-cased / agent-to-agent multi-agent-topology scope per Feature 142), D10 **DFD Target Decision** (BLOCKING-1 — `dfd_targets: [Process]` only, mirroring F-1 / F-2 single-target precedent; no External Entity declaration). **R11 mitigation (FR-018)**: grep-checkable `test_no_agp_te_prose_synthesis` test asserts `AGP-{N}` and `TE-{N}` digit-suffixed finding IDs never co-occur in same paragraph/bullet/sentence in regenerated `threat-report.md`. **R12 mitigation (FR-019)**: two-step Conventional Commit enforcement — pre-merge title check + post-merge release-please verification per `.claude/rules/git-workflow.md` (recovers from F-212-class incident pattern). **New `examples/consumer-agent-app/` baseline** (clean-slate per architect Wave 3 Step 1 Q5 lean decision): WellnessCompanionChatbot mental-health/wellness companion archetype with all 4 FR-006 emission indicators engaged; 5 TE findings (TE-1..TE-5) emitted on regen; 19 total findings (1 Critical, 8 High, 7 Medium, 3 Low); pipeline regen byte-identical (40-page PDF, SHA-256 `7ac0b639...269bce5`) per ADR-021 `SOURCE_DATE_EPOCH=1700000000` invariant; 6/6 infographic JPEGs generated. **Tests**: 33/33 pytest pass on `tests/scripts/test_human_trust_exploitation.py` (schema-contract layer Cases A/B/C + F-A2 referential-integrity Wave 5 regen + Wave 1.1 fixture-driven validator coverage; -32 lines applied via /aod.document /simplify pass — comment trim + module-scoped fixture); backward-compat baselines 5/5 PASS (+1 bonus); 1 pre-existing F-142 mermaid-agentic-app SKIP unrelated to F-4. 73/73 tasks complete; zero new runtime dependencies; PR #225 squash-merged 2026-04-26 with `feat(224):` Conventional Commit title. See `specs/224-trust-exploitation-threat-agent/` for spec/plan/tasks/delivery.

* **212:** improve executive-architecture infographic — three-level upgrade. **L1 prompt rewrite** for OpenClaw-style structural clarity (rounded-rectangle component nodes, explicit inter-layer arrows, leader-line-anchored callouts, compact empty-layer badges, additive layer-fill pastels — extends the canonical visual-design-system without modifying severity colors). **L2 callout selection rework** via Largest Remainder Method with per-layer floor (every qualifying layer ≥1 callout) + per-layer ceiling (≤4 callouts/layer) + `layer_overflow` annotation (`"+ N more in this layer"`). **L3 payload schema extension** with `flow_edges[]` and `clusters[]` top-level arrays — explicit arrow-rendering data sourced from `parse_scope_data().data_flows` and trust-zone-grouping data sourced from `parse_scope_data().trust_boundaries`, with consumer-locked field names (`destination` not `target`, `members` not `components`, `trust_level` not `trust-level`) and deterministic sort orders (`(source.casefold(), destination.casefold())` for flow_edges; `(_TRUST_LEVEL_ORDER.get(trust_level, 99), name.casefold())` for clusters mirroring `_compute_trust_zones:784`). Truncates `flow_edges[]` to first 50 entries with stderr warning when producer emits more (FR-212-17). 23 functional requirements (FR-212-1 through FR-212-23) and 8 success criteria (SC-212-1 through SC-212-8) all PASS. 12 new drift-guard tests (`tests/scripts/test_executive_architecture_payload.py`). F-128 zero-finding skip-behavior contract preserved across three F-212 waves (PDF byte-identity SHA-256 unchanged: `1ff48532f301114c463bd39babbff726a3857d9a71a7c37103fde835b625d458`). Determinism preserved per ADR-017. Runtime within +10% of Phase-2 baseline (mean warm-runs 40 ms post-US3 vs 40 ms post-US2 baseline). See `specs/212-improve-executive-architecture-infographic/` for spec/plan/tasks/artifacts.
* **219:** asi07 tool-abuse agent enrichment — first execution of Heuristic A enrichment branch (BLP-01 Tier 1, third feature after F-1 + F-2 new-agent branch). Enriches the existing `tool-abuse` threat agent with OWASP ASI07:2026 (Insecure Inter-Agent Communication) coverage WITHOUT spawning a new agent. **Two new Pattern Categories** appended to `.claude/skills/tachi-tool-abuse/references/detection-patterns.md`: Category 9 "Insecure Inter-Agent Communication (A2A)" (multi-agent topologies — direct RPC, message bus, shared queue, MCP-to-MCP bridge — without declared mutual authentication, message signing, replay protection, or taint propagation) and Category 10 "MCP-to-MCP Trust Propagation" (multi-hop trust chains without per-hop attestation, signed-capability handoff, or trust-chain validator). Both include ≥4 indicators, anti-indicators, worked examples, and primary/related citations (`OWASP ASI07:2026`, `CWE-287`, `CWE-345`, `MITRE ATLAS AML.T0060`, `OWASP LLM03:2025`). **Three additive edits** to `.claude/agents/tachi/tool-abuse.md` (metadata `owasp_references += ASI-07`; `## Purpose` 1-line A2A/MCP-to-MCP surface naming extension; Detection Workflow Step 5 references list extension); line count 98 → 100 (well under 150 cap). **5/5-dimension reduction** vs. F-2 new-agent branch: zero new agent file, zero new skill directory, zero schema bump (first BLP-01 detection feature reusing existing `AG-{N}` ID space — explicit asymmetry from ADR-031 D8 regex-alternation rule), zero consumers-list edit, zero functional orchestrator edit. **Wave 3 pipeline regen** on `examples/agentic-app/` surfaces AG-8 [NEW] finding on Inter-Agent Communication Channel component citing `OWASP ASI07:2026` + `CWE-287` + `MITRE ATLAS AML.T0060`; renders cohesively in `threat-report.md` §3.7 alongside Categories 1-8 findings (no fragmentation across artificial sub-section headings). **24-file zero-edit invariant preserved** per ADR-032 D2 (22 original + F-1 + F-2 additions; F-3 modifies only host files). 21 functional requirements (FR-219-1 through FR-219-21) all PASS; 30/31 tests pass (1 pre-existing F-142 known-limitation skip on `mermaid-agentic-app` unrelated to F-3); ADR-032 (Status: Accepted) with 7 numbered Decisions documenting the Heuristic A consolidation rationale and ADR-031 D8 asymmetry; new pytest suite `tests/scripts/test_tool_abuse_enrichment.py` (385 lines) covering structural invariants and F-A2 referential-integrity validation on Cat-9/10 fixtures. KB-039 captures the 5/5-dimension cost reducer pattern as Tier 2 ML+Mobile guidance for F-6/F-7. Build envelope held: <24h clock vs PRD's 1-day target. OWASP Agentic Top 10:2026 framework coverage advances 5/10 → 6/10 (ASI07 joins ASI-01, ASI-02, ASI-04, MCP-03, MCP-05). See `specs/219-asi07-tool-abuse-enrichment/` for spec/plan/tasks/delivery.

---

## [4.35.0](https://github.com/davidmatousek/tachi/compare/v4.34.0...v4.35.0) (2026-05-10)


### Features

* **282:** pre-commit secret-scanning defaults ([#283](https://github.com/davidmatousek/tachi/issues/283)) ([18378bd](https://github.com/davidmatousek/tachi/commit/18378bd406a5633f1d13b443d1d1ea7a28a0d295))

## [4.34.0](https://github.com/davidmatousek/tachi/compare/v4.33.0...v4.34.0) (2026-05-09)


### Features

* **277:** claude permissions baseline (BLP-02 F-4) ([#278](https://github.com/davidmatousek/tachi/issues/278)) ([896588b](https://github.com/davidmatousek/tachi/commit/896588bc739d4760d36ff64b1b3f313498b4befa))

## [4.33.0](https://github.com/davidmatousek/tachi/compare/v4.32.0...v4.33.0) (2026-05-08)


### Features

* **272:** SECURITY.md and private disclosure channel ([#273](https://github.com/davidmatousek/tachi/issues/273)) ([7b1cc53](https://github.com/davidmatousek/tachi/commit/7b1cc53e6f57486b356b72b978a86920d7663480))

## [4.32.0](https://github.com/davidmatousek/tachi/compare/v4.31.0...v4.32.0) (2026-05-07)


### Features

* **264:** adopt dual-frame public positioning (harness reframe) ([#265](https://github.com/davidmatousek/tachi/issues/265)) ([b558025](https://github.com/davidmatousek/tachi/commit/b558025fefe5f5afd90683248523673283e8329e)), closes [#264](https://github.com/davidmatousek/tachi/issues/264)


### Bug Fixes

* **266:** retitle CONTRIBUTING.md for tachi ([#267](https://github.com/davidmatousek/tachi/issues/267)) ([abde9cd](https://github.com/davidmatousek/tachi/commit/abde9cd13197689bf245435de48c753fcc225989)), closes [#266](https://github.com/davidmatousek/tachi/issues/266)
* **268:** disentangle tachi-scanner from AOD-Kit positioning in scope.md ([#271](https://github.com/davidmatousek/tachi/issues/271)) ([b2bef11](https://github.com/davidmatousek/tachi/commit/b2bef1178961e66d86ee525c1d0ef1407e14317c)), closes [#268](https://github.com/davidmatousek/tachi/issues/268)

## [4.31.0](https://github.com/davidmatousek/tachi/compare/v4.30.0...v4.31.0) (2026-05-06)


### Features

* **260:** asset-sensitivity tag prototype ([#262](https://github.com/davidmatousek/tachi/issues/262)) ([3dfe6a7](https://github.com/davidmatousek/tachi/commit/3dfe6a7295c37d2685ec41ff4180742a6ceb7eb5))

## [4.30.0](https://github.com/davidmatousek/tachi/compare/v4.29.0...v4.30.0) (2026-05-05)


### Features

* **256:** file-size cap + regular-file check on KV loader ([#258](https://github.com/davidmatousek/tachi/issues/258)) ([9964a72](https://github.com/davidmatousek/tachi/commit/9964a72316db748a702ff996262026b3de05484a))

## [4.29.0](https://github.com/davidmatousek/tachi/compare/v4.28.0...v4.29.0) (2026-05-05)


### Features

* **256:** harden source-pattern surface — bash source/eval → KV parser + clone timeout ([#257](https://github.com/davidmatousek/tachi/issues/257)) ([f959622](https://github.com/davidmatousek/tachi/commit/f959622d4ce765f68aa55906a12f8c20185c3539))


### Bug Fixes

* **250:** permanent CI test process hardening ([#253](https://github.com/davidmatousek/tachi/issues/253)) ([75866d9](https://github.com/davidmatousek/tachi/commit/75866d9662842aff319e66853b2351dd9e95d983))

## [4.28.0](https://github.com/davidmatousek/tachi/compare/v4.27.1...v4.28.0) (2026-05-04)


### Features

* **248:** harden init.sh substitution surface — sed → bash param expansion + input validation + gitignore default ([#249](https://github.com/davidmatousek/tachi/issues/249)) ([6db9a25](https://github.com/davidmatousek/tachi/commit/6db9a2590ba458964db93f8627272962d22abf70))

## [4.27.1](https://github.com/davidmatousek/tachi/compare/v4.27.0...v4.27.1) (2026-05-02)


### Bug Fixes

* restore Apache 2.0 license overwritten by /aod.update bug ([f8f3c2e](https://github.com/davidmatousek/tachi/commit/f8f3c2e8cc6759e86c790d0bd9e093df712e9a2d))

## [4.27.0](https://github.com/davidmatousek/tachi/compare/v4.26.0...v4.27.0) (2026-05-02)


### Features

* **241:** F-8 + F-A3 Web/API Coverage Attestation + Populator Wiring [Tier 3] ([#242](https://github.com/davidmatousek/tachi/issues/242)) ([e8a5370](https://github.com/davidmatousek/tachi/commit/e8a5370a7eb8598717af1fe2b718bb8d811c891a))

## [4.26.0](https://github.com/davidmatousek/tachi/compare/v4.25.0...v4.26.0) (2026-04-29)


### Features

* **237:** Mobile Top 10 Coverage Bundle ([#238](https://github.com/davidmatousek/tachi/issues/238)) ([e962a0e](https://github.com/davidmatousek/tachi/commit/e962a0e5b06d69c45aa3aa6217ebf9945b01f09e))

## [4.25.0](https://github.com/davidmatousek/tachi/compare/v4.24.0...v4.25.0) (2026-04-28)


### Features

* **232:** ML Top 10 build closeout — data-poisoning + model-theft + tests ([#235](https://github.com/davidmatousek/tachi/issues/235)) ([e325375](https://github.com/davidmatousek/tachi/commit/e32537592307eadd787f84f56109dda553ed8648))
* **232:** ML Top 10 Coverage Bundle ([#233](https://github.com/davidmatousek/tachi/issues/233)) ([b84552a](https://github.com/davidmatousek/tachi/commit/b84552a519f929d3f02f9780550591fe599085d6))

## [4.24.0](https://github.com/davidmatousek/tachi/compare/v4.23.0...v4.24.0) (2026-04-27)


### Features

* **224:** human-trust-exploitation threat agent (ASI09) ([#225](https://github.com/davidmatousek/tachi/issues/225)) ([feaeb95](https://github.com/davidmatousek/tachi/commit/feaeb95019340a85681b65198a4b42e3a92b16a4))
* **229:** llm10 unbounded consumption verification ([#230](https://github.com/davidmatousek/tachi/issues/230)) ([e086d31](https://github.com/davidmatousek/tachi/commit/e086d31e4bead0dd7cb3de3fd63e4a120da59133))

## [4.23.0](https://github.com/davidmatousek/tachi/compare/v4.22.1...v4.23.0) (2026-04-26)


### Features

* **219:** asi07-tool-abuse-enrichment ([#220](https://github.com/davidmatousek/tachi/issues/220)) ([f7bf204](https://github.com/davidmatousek/tachi/commit/f7bf20483bc7f805ce4f9f879c6bb6d23a88a211))

## [4.22.1](https://github.com/davidmatousek/tachi/compare/v4.22.0...v4.22.1) (2026-04-25)


### Bug Fixes

* **215:** byte-probe image detection in extract-report-data ([#216](https://github.com/davidmatousek/tachi/issues/216)) ([672b7fb](https://github.com/davidmatousek/tachi/commit/672b7fb56295b53680f37975d4f9a243af920ec0))

## [4.22.0](https://github.com/davidmatousek/tachi/compare/v4.21.1...v4.22.0) (2026-04-25)


### Features

* **212:** improve executive-architecture infographic ([904d952](https://github.com/davidmatousek/tachi/commit/904d9520f5db8e85493814872b4cf26fdcd5342b))

## [4.21.1](https://github.com/davidmatousek/tachi/compare/v4.21.0...v4.21.1) (2026-04-24)


### Bug Fixes

* **209:** producer/consumer contract drift across extractor pipeline ([#210](https://github.com/davidmatousek/tachi/issues/210)) ([d517ac6](https://github.com/davidmatousek/tachi/commit/d517ac6f3bc475c7e99f2e702142396f5b8a5393)), closes [#209](https://github.com/davidmatousek/tachi/issues/209)

## [4.21.0](https://github.com/davidmatousek/tachi/compare/v4.20.0...v4.21.0) (2026-04-24)


### Features

* **206:** misinformation threat agent (OWASP LLM09:2025) ([#207](https://github.com/davidmatousek/tachi/issues/207)) ([b703e52](https://github.com/davidmatousek/tachi/commit/b703e52be2fac041dd9b5ffc23b1f5b610e8a262))

## [4.20.0](https://github.com/davidmatousek/tachi/compare/v4.19.0...v4.20.0) (2026-04-20)


### Features

* update template from AOD-kit (first F129 run) ([a36a73f](https://github.com/davidmatousek/tachi/commit/a36a73fc28a367047c1eabb2860ba83c60a83e5d))

## [4.19.0](https://github.com/davidmatousek/tachi/compare/v4.18.1...v4.19.0) (2026-04-19)


### Features

* **201:** output-integrity threat agent (OWASP LLM05:2025) ([#202](https://github.com/davidmatousek/tachi/issues/202)) ([558e75e](https://github.com/davidmatousek/tachi/commit/558e75eb333ad7787167833c97b645bc251492e1))

## [4.18.1](https://github.com/davidmatousek/tachi/compare/v4.18.0...v4.18.1) (2026-04-18)


### Bug Fixes

* **198:** merge source_attribution onto Tier 1/2 findings ([#199](https://github.com/davidmatousek/tachi/issues/199)) ([e637d31](https://github.com/davidmatousek/tachi/commit/e637d31927c1e2c66f4f0afe5b2ab2b9ea8abcd1))

## [4.18.0](https://github.com/davidmatousek/tachi/compare/v4.17.0...v4.18.0) (2026-04-18)


### Features

* **194:** Coverage Attestation Report Section (F-B / BLP-01) ([#195](https://github.com/davidmatousek/tachi/issues/195)) ([c4b8dc6](https://github.com/davidmatousek/tachi/commit/c4b8dc68f36b59ee7ab49cc587661526ffd1a818))

## [4.17.0](https://github.com/davidmatousek/tachi/compare/v4.16.0...v4.17.0) (2026-04-18)


### Features

* **189:** F-A2 source attribution schema extension ([#189](https://github.com/davidmatousek/tachi/issues/189)) ([#190](https://github.com/davidmatousek/tachi/issues/190)) ([6d5d890](https://github.com/davidmatousek/tachi/commit/6d5d890c388af5f546246f4e39f8a4d61fe840b1))

## [4.16.0](https://github.com/davidmatousek/tachi/compare/v4.15.0...v4.16.0) (2026-04-17)


### Features

* **180:** F-A1 Taxonomy Crosswalk Collection ([#181](https://github.com/davidmatousek/tachi/issues/181)) ([8b7c7bf](https://github.com/davidmatousek/tachi/commit/8b7c7bf59a6de93a0d3f5016a4395755de19c79e))

## [4.15.0](https://github.com/davidmatousek/tachi/compare/v4.14.1...v4.15.0) (2026-04-16)


### Features

* **142:** MAESTRO Phase 3 — Agentic Threat Pattern Expansion ([#172](https://github.com/davidmatousek/tachi/issues/172)) ([c0b7378](https://github.com/davidmatousek/tachi/commit/c0b73780c83aa3df16ac7965738bc76034e88454))

## [4.14.1](https://github.com/davidmatousek/tachi/compare/v4.14.0...v4.14.1) (2026-04-14)


### Bug Fixes

* fall back to architecture.md H1 when threats.md lacks project name ([#165](https://github.com/davidmatousek/tachi/issues/165)) ([b746cb7](https://github.com/davidmatousek/tachi/commit/b746cb74595f9a15041c50bcdef69e5e0ed21709))

## [4.14.0](https://github.com/davidmatousek/tachi/compare/v4.13.0...v4.14.0) (2026-04-14)


### Features

* **129:** attack tree delta sub-agent — extract Section 5 generation ([#162](https://github.com/davidmatousek/tachi/issues/162)) ([0729490](https://github.com/davidmatousek/tachi/commit/072949017f633d029ac4af22032da21efcb67b17))


### Bug Fixes

* auto-detect newest docs/security run directory in tachi commands ([#164](https://github.com/davidmatousek/tachi/issues/164)) ([39c962c](https://github.com/davidmatousek/tachi/commit/39c962c4eaed2e4cec899f5036169ba005b6d163))

## [4.13.0](https://github.com/davidmatousek/tachi/compare/v4.12.0...v4.13.0) (2026-04-12)


### Features

* **141:** MAESTRO Phase 2 — Cross-Layer Attack Chain Analysis ([#159](https://github.com/davidmatousek/tachi/issues/159)) ([5a108e9](https://github.com/davidmatousek/tachi/commit/5a108e984aa8623df3a856007c876006cdff6eb3))


### Bug Fixes

* **141:** constrain attack chain diagram height to fit one page ([2310af3](https://github.com/davidmatousek/tachi/commit/2310af313128aaec1cd147a3f028aba41a2f2150))

## [4.12.0](https://github.com/davidmatousek/tachi/compare/v4.11.1...v4.12.0) (2026-04-12)


### Features

* **154:** deterministic Gemini prompt scaffold for infographic quality stability ([f2ad9be](https://github.com/davidmatousek/tachi/commit/f2ad9be2f24d8d94168dc82cd49048623164f4de))


### Bug Fixes

* **154:** add .claude/skills/tachi-*/ to INSTALL_MANIFEST ([6547360](https://github.com/davidmatousek/tachi/commit/6547360d39c44301adb51c8b8ec23cc722a13e8a))
* **154:** infographic quality — extract risk metrics, update Gemini model config ([3cd5d27](https://github.com/davidmatousek/tachi/commit/3cd5d27edde4310dc0ad650ef7265bcc49f098d6))
* **154:** MAESTRO layer detection in /tachi.infographic checks wrong file and pattern ([30f9ad9](https://github.com/davidmatousek/tachi/commit/30f9ad96b49178b447c79a3d6e49b97977b6ab0d))

## [4.11.1](https://github.com/davidmatousek/tachi/compare/v4.11.0...v4.11.1) (2026-04-12)


### Bug Fixes

* **154:** PDF report — attack trees, MAESTRO headings, landscape whitespace ([#155](https://github.com/davidmatousek/tachi/issues/155)) ([7f047b7](https://github.com/davidmatousek/tachi/commit/7f047b7fe42736bd51e60d8dfca18af33cb86d98)), closes [#154](https://github.com/davidmatousek/tachi/issues/154)

## [4.11.0](https://github.com/davidmatousek/tachi/compare/v4.10.1...v4.11.0) (2026-04-12)


### Features

* **082:** threat agent skill references — detection tier lean refactor ([#151](https://github.com/davidmatousek/tachi/issues/151)) ([6f9a40d](https://github.com/davidmatousek/tachi/commit/6f9a40dbe17b14a04f10b56357f1a81bb025e24d))

## [4.10.1](https://github.com/davidmatousek/tachi/compare/v4.10.0...v4.10.1) (2026-04-11)


### Bug Fixes

* **130:** enforce mmdc as hard prerequisite with loud preflight/mid-render aborts ([#148](https://github.com/davidmatousek/tachi/issues/148)) ([d35a667](https://github.com/davidmatousek/tachi/commit/d35a6676dd8e409d32b06eb5e03760a0aab3f560))

## [4.10.0](https://github.com/davidmatousek/tachi/compare/v4.9.2...v4.10.0) (2026-04-10)


### Features

* **136:** align MAESTRO layer names with canonical CSA taxonomy ([#146](https://github.com/davidmatousek/tachi/issues/146)) ([31356fb](https://github.com/davidmatousek/tachi/commit/31356fb5bb48ac02b62ce8ead35f19d91db36c13))

## [Unreleased]

### Added — Agentic Pattern Schema Extension (#142, Feature 142)

**Schema Version Bump (`schemas/finding.yaml` 1.3 → 1.4)**: Schema version bumped from `1.3` to `1.4` to accommodate the new `agentic_pattern` enum field introduced by MAESTRO Phase 3 (Feature 142 — Agentic Threat Pattern Expansion). Per [ADR-026](docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md), this is a **minor bump** because the change is additive: a new enum-typed field with a default value (`none`) is introduced, the schema shape is unchanged, and no existing required fields are removed or renamed. The bump extends the Feature 136 enum-VALUE-rename minor-bump rule (ADR-020 Revision History) to cover NEW enum-typed field additions under the same three additive-compatibility conditions.

**threats.md Output Schema Bump (1.3 → 1.4)**: The `templates/tachi/output-schemas/threats.md` frontmatter `schema_version` is bumped from `1.3` to `1.4` alongside `finding.yaml` to reflect the additive structural changes to the output: (a) new Pattern column in Section 7 between Category and Component, and (b) new conditional Section 4b "Findings by Agentic Pattern" gated by `has-agentic-patterns: true`. Per the Feature 104 precedent (threat-report.md 1.0 → 1.1 for baseline delta propagation), additive structural changes to an output schema warrant a minor bump on that schema. The change is purely additive and backward-compatible: pre-Feature-142 parsers reading the new output see `schema_version: "1.4"` but the Pattern column renders `—` on legacy-style data (pattern=`none`) and Section 4b is suppressed entirely. The `.claude/skills/tachi-orchestration/references/output-schemas.md` frontmatter example and descriptive table are updated to match.

#### New `agentic_pattern` Enum Field

The finding IR gains a required `agentic_pattern` field with eight permitted values surfacing the six canonical CSA MAESTRO agentic threat patterns plus two sentinel values:

| Value | Meaning |
|-------|---------|
| `agent_collusion` | Multiple compromised agents coordinating to achieve malicious objectives |
| `emergent_behavior` | Exploiting unpredictable behaviors arising from agent interactions |
| `temporal_attack` | Sleeper agents, gradual corruption, seasonal exploitation, time-delayed activation |
| `trust_exploitation` | Identity spoofing between agents, reputation manipulation, trust chain attacks |
| `communication_vulnerability` | Inter-agent message interception, protocol manipulation, routing attacks |
| `resource_competition` | Resource monopolization, priority manipulation, coordination disruption between agents |
| `none` | Finding does not map to any canonical pattern (sentinel; default) |
| `multiple` | Finding exemplifies two or more patterns equally (rare; prefer the dominant pattern when one exists) |

The default value is `none`. The field is populated during orchestrator Phase 3.6 (Pattern Synthesis Engine) using a deterministic rule-based classification engine. The multi-agent gate predicate (FR-006) ensures that single-agent architectures receive `none` for every finding, preserving backward compatibility on the 5 baseline architectures (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`).

#### `id.pattern` Regex Extension — `AGP-` Prefix

The `finding.id.pattern` regex has been extended from `^(S|T|R|I|D|E|AG|LLM)-\d+$` to `^(S|T|R|I|D|E|AG|LLM|AGP)-\d+$` to accept the new `AGP-` prefix reserved for **net-new findings** generated by Phase 3.6 for previously-uncovered patterns (Agent Collusion, Emergent Behavior, Temporal Attack). `AGP-NN` findings map to `category: agentic` and are appended to the deduplicated finding IR only when the architecture satisfies the multi-agent gate predicate AND no existing detection-tier finding already carries the pattern label. See [data-model.md Entity 5](specs/142-maestro-agentic-pattern-expansion/data-model.md) for the full net-new finding generation contract.

#### Backward Compatibility

The addition is **backward-compatible** per FR-017. Pre-Feature-142 baseline findings (which lack the `agentic_pattern` field) parse correctly with default `agentic_pattern: none` when consumed by Feature 142 parsers. The 5 non-multi-agent baseline PDFs remain byte-identical under `SOURCE_DATE_EPOCH=1700000000` per [ADR-021](docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) because the multi-agent gate predicate evaluates `false` on those architectures, causing every finding to receive `agentic_pattern: none` and the Pattern column to render as `—` for all rows (with Section 4b "Findings by Agentic Pattern" suppressed entirely).

#### References

- ADR-026: [docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md](docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md)
- Spec: [specs/142-maestro-agentic-pattern-expansion/spec.md](specs/142-maestro-agentic-pattern-expansion/spec.md)
- Plan: [specs/142-maestro-agentic-pattern-expansion/plan.md](specs/142-maestro-agentic-pattern-expansion/plan.md)
- Data model: [specs/142-maestro-agentic-pattern-expansion/data-model.md](specs/142-maestro-agentic-pattern-expansion/data-model.md)
- GitHub Issue: [#142](https://github.com/davidmatousek/tachi/issues/142)

---

### Changed — Detection Quality and Lean Agent Architecture Complete (#151, Feature 082)

**All 17 Tachi Agents Now Use Lean-Agent Architecture**: The 11 remaining threat detection agents (6 STRIDE + 5 AI-specific) have been migrated from self-contained inline shape to the lean-agent + skill references pattern, completing the lean-agent architecture for the entire tachi agent fleet. Pre-refactor, STRIDE agents were 113-141 lines and AI agents were 167-201 lines (3 AI agents were over the 180-line hard cap); post-refactor, STRIDE agents are 50-54 lines and AI agents are 78-114 lines — every agent within FR-10 tier caps (STRIDE ≤120, AI ≤150, hard cap ≤180). Detection quality has been enriched with +30 new pattern categories across the 11 agents, covering OWASP LLM Top 10 2025, MITRE ATLAS v5.1+ (including the October 2025 agent techniques AML.T0058-T0062), OWASP AI Exchange, CWE Top 25 2024, and NIST AI 600-1. Users running `/tachi.threat-model` on an agentic AI application will see additional findings surfaced that the pre-refactor inline patterns could not reach.

#### Detection Variant of Lean-Agent Pattern

Feature 082 introduces a second documented shape of the lean-agent pattern, sibling to the methodology variant already used by `control-analyzer`. The detection variant loads its companion reference at invocation start via a single `**MANDATORY**: Read` directive rather than phase-gated loads. All 11 threat agents now host their detection patterns at `.claude/skills/tachi-<name>/references/detection-patterns.md` (byte-preserved from the pre-refactor agent content plus enriched categories).

| Pattern Variant | Used By | Load Style |
|-----------------|---------|------------|
| Methodology variant | control-analyzer | Phase-gated loads per workflow step |
| **Detection variant** (new) | 11 threat agents | Single-point load at detection start |

See [ADR-023](docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md) for the full pattern definition, the MAESTRO ownership rule, and the additive-only shared reference invariant.

#### New Enrichment Categories (+30 / ≥22 Floor)

All 11 threat agents gained new detection pattern categories sourced from authoritative primaries:

| Source | Coverage Added |
|--------|---------------|
| OWASP LLM Top 10 2025 | Prompt injection variants, data poisoning vectors, model theft techniques, excessive agency patterns |
| MITRE ATLAS v5.1+ | AML.T0058 context poisoning, AML.T0059 memory corruption, AML.T0060 agent-in-the-middle, AML.T0061 excessive agency runtime, AML.T0062 cascading agent failures |
| OWASP AI Exchange | Cross-cutting AI supply chain, model lifecycle, and training data governance patterns |
| MITRE ATT&CK v15+ | STRIDE-side technique mappings (especially T1078 valid accounts, T1550 alt auth, T1562 impair defenses) |
| CWE Top 25 2024 | Modernized weakness enumeration with 2024 updates |
| NIST AI 600-1 | Generative AI risk management profile controls |

T048 security review (Wave 13) flagged 5 first-draft categories for primary-source realignment; T048a (Wave 13.5) rebuilt all 5 byte-verbatim preserving substance. The final aggregate was **30 new categories** against a **≥22 floor** (SC-006 / FR-7) — **+8 margin**. See [KB-030 in INSTITUTIONAL_KNOWLEDGE.md](docs/INSTITUTIONAL_KNOWLEDGE.md) for the "cite primary sources in first draft" lesson that emerged from the T048 rebuild cycle.

#### Additive-Only Shared Reference Consolidation

`finding-format-shared.md` gains a new "For Threat Agents" producer section describing the finding construction responsibility for detection-tier agents. The existing "For Risk Scorer / Control Analyzer / Threat Report" consumer sections remain byte-identical — the edit is **additive-only** (T046 invariant), preventing regressions in the 6 infrastructure agents that were already in production. All 11 threat agents' Skill References tables register the shared reference for load at detection start. The OWASP 3×3 risk matrix now lives in exactly one canonical file (`severity-bands-shared.md:72`), normalized to Unicode `×` to match the SC-004 canonical-form audit. Wave 16 remediation removed 22 inline "OWASP 3×3" brand-name mentions from agent prose.

#### Backward Compatibility

Feature 082 is **purely agent-behavior-facing**. The PDF pipeline reads committed `threats.md`, `risk-scores.md`, `compensating-controls.md`, and `attack-trees/` files — none of which are modified by this feature. Typst templates, `extract-report-data.py`, and `extract-infographic-data.py` are untouched. The 5 byte-deterministic example PDFs (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) remain **byte-identical** under `SOURCE_DATE_EPOCH=1700000000` per [ADR-021](docs/architecture/02_ADRs/ADR-021-deterministic-pdf-comparison.md). The 6th example (`agentic-app`) was regenerated as the T057 US2 AC-3 independent test, surfacing **+8 new AI findings** (22 baseline → 30) — consistent with the Option B+ gate prediction. Zero new runtime dependencies (SC-014 — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`).

#### Option B+ Gate Methodology

Phase 1a / 1b (2-agent prototype) and Phase 3 (11-agent scale) regression gates used **content-equivalence + DFD-vs-pattern matching** rather than live orchestrator invocation. The method was ratified by the T021 joint architect + team-lead gate approval under the "±2 tolerance interpretation (b)" ruling: pre-existing pattern categories must delta=0, new categories can have any non-negative delta from enrichment. T050 full regression gate (Wave 15) used Option B+ to prove SC-005 for all 11 agents × 6 examples; T057 live regeneration on `agentic-app` (Wave 17) then confirmed the prediction was exact.

#### References

- PRD: [docs/product/02_PRD/082-threat-agent-skill-references-2026-04-11.md](docs/product/02_PRD/082-threat-agent-skill-references-2026-04-11.md)
- Spec: [specs/082-threat-agent-skill/spec.md](specs/082-threat-agent-skill/spec.md)
- Plan: [specs/082-threat-agent-skill/plan.md](specs/082-threat-agent-skill/plan.md)
- Delivery retrospective: [specs/082-threat-agent-skill/delivery.md](specs/082-threat-agent-skill/delivery.md)
- ADR-023: [docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md](docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md)
- PR: [#151](https://github.com/davidmatousek/tachi/pull/151)
- GitHub Issue: [#82](https://github.com/davidmatousek/tachi/issues/82)

---

### Breaking Changes — Correctness Fix (#148, Feature 130)

**mmdc Is Now a Hard Prerequisite**: When `/tachi.security-report` is run against a project containing Critical/High attack trees, `@mermaid-js/mermaid-cli` (`mmdc`) must be installed on `PATH`. Previously, a missing `mmdc` triggered a silent text fallback that shipped 40+ lines of raw `flowchart TD` source per attack-path page inside the PDF; the pipeline reported exit 0 and the broken output was only discoverable by paging through the PDF manually. The text-fallback Typst branch has been deleted outright, and two defense-in-depth preflight gates now raise a loud error with the canonical install command.

#### Install

```sh
npm install -g @mermaid-js/mermaid-cli
```

The check is gated on input detection — projects without `attack-trees/` content continue to work unchanged without `mmdc`. See [ADR-022](docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md) for the full governance rationale, rejected alternatives (pymmdc, Kroki, auto-install), and the Future Work clause.

#### Error Output on Missing Prerequisite

```
Attack path rendering requires @mermaid-js/mermaid-cli (mmdc).
Install with: npm install -g @mermaid-js/mermaid-cli
Then re-run /tachi.security-report.
```

The same canonical message fires from both enforcement points: a shell-level `command -v mmdc` check in `.claude/commands/tachi.security-report.md` Step 1 (mirrors the existing Typst check) and a Python-level `shutil.which("mmdc") → raise RuntimeError(...)` inside `scripts/extract-report-data.py::render_mermaid_to_png()`.

#### Mid-Render Failures Now Abort With Per-Finding Detail

When `mmdc` is present but a specific attack tree fails to render (invalid Mermaid syntax, subprocess crash, timeout), the pipeline now aggregates per-finding errors and raises `RuntimeError("Attack path rendering failed for N findings: ...")` with each failing finding's ID, source path, failure class (`exit:<code>`, `timeout`, or `signal`), and a 200-byte stderr excerpt. Previously, each failing entry was silently marked `has_image=False` and the text fallback kicked in. No PDF is emitted when mid-render failures occur.

#### Backward Compatibility

The happy path (mmdc present, all trees render) is byte-identical to the pre-Feature 130 output under `SOURCE_DATE_EPOCH=1700000000`. The 5 byte-deterministic baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) remain unchanged. Projects without `attack-trees/` content are completely unaffected.

#### Documentation

- **README.md** gains a new `## Prerequisites` section naming `typst` and `@mermaid-js/mermaid-cli` with per-OS install commands (macOS/Linux/WSL).
- **scripts/install.sh** gains a courtesy `command -v mmdc` warning at setup time.
- **docs/architecture/00_Tech_Stack/README.md** mmdc section rewritten as a hard prerequisite with ADR-022 cross-reference.
- **specs/112-attack-path-pages/spec.md** SC-004 inverted (text fallback is no longer a supported shipping mode) with audit-trail comment.
- **specs/112-attack-path-pages/research.md** pymmdc description corrected (GPL-3.0 Node.js wrapper, not a pure-Python renderer) with a Durable Decision Rationale block.
- **New CI workflow** `.github/workflows/tachi-mmdc-preflight.yml` asserts the loud-failure path fires on `ubuntu-latest` (no mmdc preinstalled) and fails the job if `mmdc` is unexpectedly present on `PATH`.

---

### Breaking Changes — Correctness Fix (#136)

**MAESTRO Canonical Layer Alignment**: tachi's MAESTRO seven-layer taxonomy has been aligned with the canonical CSA Ken Huang reference. Three L5/L6/L7 layer names, the acronym expansion, and a third-divergent name ("Integration Services") in the Typst PDF template have been corrected. This is a **correctness fix**, not a feature addition.

#### Enum Value Migration (`schemas/finding.yaml` `maestro_layer`)

The `maestro_layer` enum in `schemas/finding.yaml` has changed values. Downstream consumers (dashboards, scripts, tooling built on the enum) MUST update their code.

| Old Value | New Value |
|-----------|-----------|
| `L5 — Security` | `L5 — Evaluation and Observability` |
| `L6 — Agent Ecosystem` | `L6 — Security and Compliance` |
| `L7 — User Interface` | `L7 — Agent Ecosystem` |
| `L6 — Integration Services` (Typst template bug) | `L6 — Security and Compliance` |

L1–L4 enum values are unchanged.

#### Schema Version Bump

`schemas/finding.yaml` schema version bumped from `1.2` to `1.3`. This signals the enum-value-only breaking change. The schema shape and required fields are unchanged — only the allowed values for `maestro_layer` changed. Per ADR-020, enum-value-only breaking changes warrant a minor schema bump (not major), provided schema shape and required fields are unchanged.

#### Acronym Correction

The MAESTRO acronym expansion in `.claude/skills/tachi-shared/references/maestro-layers-shared.md` (line 17) and `docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md` (line 123) has been corrected from:

- **Old**: "Multi-Agent Environment Security Toolkit for Reasoning and Orchestration"
- **New**: "Multi-Agent Environment, Security, Threat, Risk, and Outcome"

The new form matches the canonical CSA source.

#### Typst PDF Template Fix

`templates/tachi/security-report/maestro-findings.typ` fallback dictionary (lines 132-134) previously contained `"L6": "Integration Services"` — a third divergent name matching neither the canonical CSA spec nor the prior shared reference. This pre-existing bug was corrected as part of this fix.

#### Regenerated Example Outputs

All six example architectures in `examples/*` have had their threat model outputs regenerated with canonical layer names:

- `examples/web-app/` — threats.md + security-report.pdf.baseline
- `examples/microservices/` — threats.md + security-report.pdf.baseline
- `examples/ascii-web-api/` — threats.md + security-report.pdf.baseline
- `examples/free-text-microservice/` — threats.md + security-report.pdf.baseline
- `examples/mermaid-agentic-app/` — threats.md + threat-report.md + threat-infographic-spec.md + attack-trees/ + security-report.pdf.baseline
- `examples/agentic-app/sample-report/` — full pipeline (threats.md, risk-scores.md, compensating-controls.md, threat-report.md, infographic specs, security-report.pdf)

The five non-agentic-app PDF baselines are byte-deterministic under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. The agentic-app sample remains intentionally excluded from byte-determinism testing due to non-deterministic Gemini infographic generation.

#### New L5 Keyword Set

A new L5 Evaluation and Observability keyword section has been added covering: audit log, monitoring, observability, telemetry, anomaly detection, SIEM, forensics, behavioral monitoring, metrics, human oversight, log aggregation. Previously, findings targeting audit loggers and observability components had no dedicated layer and were misrouted or lost.

#### Downstream Migration Guidance

If you consume tachi output programmatically:

1. Update any hardcoded references to the old layer names (see enum migration table above)
2. Update any scripts parsing `maestro_layer` values from `threats.md`, `risk-scores.md`, or `compensating-controls.md`
3. Regenerate any custom report templates that reference layer names
4. Check `schema_version` field — expect `"1.3"` going forward

#### References

- PRD: [docs/product/02_PRD/136-maestro-canonical-layer-correctness-fix-2026-04-10.md](docs/product/02_PRD/136-maestro-canonical-layer-correctness-fix-2026-04-10.md)
- Spec: [specs/136-maestro-canonical-layer/spec.md](specs/136-maestro-canonical-layer/spec.md)
- Plan: [specs/136-maestro-canonical-layer/plan.md](specs/136-maestro-canonical-layer/plan.md)
- ADR-020 (canonical taxonomy rule): [docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md](docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md)
- GitHub Issue: [#136](https://github.com/davidmatousek/tachi/issues/136)

---

## [4.9.2](https://github.com/davidmatousek/tachi/compare/v4.9.1...v4.9.2) (2026-04-10)


### Bug Fixes

* **138:** lowercase attack tree PNG filenames to match convention ([#139](https://github.com/davidmatousek/tachi/issues/139)) ([1400e47](https://github.com/davidmatousek/tachi/commit/1400e478ff58a9f1357f69d42c62ea0437e0d4c8)), closes [#138](https://github.com/davidmatousek/tachi/issues/138)

## [4.9.1](https://github.com/davidmatousek/tachi/compare/v4.9.0...v4.9.1) (2026-04-10)


### Bug Fixes

* **134:** threat-report attack tree baseline, MAESTRO layer rendering, filename convention ([#135](https://github.com/davidmatousek/tachi/issues/135)) ([716df8e](https://github.com/davidmatousek/tachi/commit/716df8e9c98768eb5edf5d87be943833aab81ab1)), closes [#134](https://github.com/davidmatousek/tachi/issues/134)

## [4.9.0](https://github.com/davidmatousek/tachi/compare/v4.8.0...v4.9.0) (2026-04-10)


### Features

* **128:** add executive threat architecture infographic with early-page PDF positioning ([#131](https://github.com/davidmatousek/tachi/issues/131)) ([7b217fe](https://github.com/davidmatousek/tachi/commit/7b217fe2447ba758db770ec1be0ac428e23fa252))

## [4.8.0](https://github.com/davidmatousek/tachi/compare/v4.7.0...v4.8.0) (2026-04-09)


### Features

* **120:** add architecture lifecycle command ([#124](https://github.com/davidmatousek/tachi/issues/124)) ([f814c02](https://github.com/davidmatousek/tachi/commit/f814c027db03cf5424599b640bd99ac1aa8cd37e))

## [4.7.0](https://github.com/davidmatousek/tachi/compare/v4.6.0...v4.7.0) (2026-04-09)


### Features

* **121:** rename tachi commands to tachi.* dot-namespace ([#122](https://github.com/davidmatousek/tachi/issues/122)) ([7d0f968](https://github.com/davidmatousek/tachi/commit/7d0f9684166a8fd6af10517fcca3f1aa85abad73))

## [Unreleased]

### Added

- **Executive Threat Architecture Infographic** (Feature 128) — New `/tachi.infographic --template executive-architecture` (alias: `exec`) generates a layered architecture diagram with Critical/High finding callouts, designed for CISO-level readers. In the compiled PDF security report the new page lands immediately after the Executive Summary (pages 2–3 area) so executives see the visual threat narrative within their first-glance window. Included in the `all` shorthand expansion alongside the existing five templates. Backward compatible — example PDFs without a generated `threat-executive-architecture.jpg` render byte-identical to the pre-F-128 baseline. Ships with tachi's first project-level pytest harness (`pyproject.toml`, `requirements-dev.txt`, `tests/`) and five committed `.baseline` PDFs guarding backward compatibility against silent regressions.
- **Architecture Lifecycle Command** (Feature 120) — `/tachi.architecture` now tracks versions with YAML frontmatter (version, date, description, SHA-256 checksum), archives previous versions to `.archive/v{N}/`, and supports guided updates through change categories. `/tachi.threat-model` automatically snapshots the architecture file into each timestamped output folder for full traceability. Backward compatible with existing architecture files.

### Changed

- **Command Namespace Migration** (Feature 121) — All tachi pipeline commands renamed from unprefixed names to `tachi.*` namespace prefix. New `/tachi.architecture` command added. Install script now cleans up deprecated command files on upgrade. See migration table below.

#### Command Name Migration

| Old Command | New Command |
|-------------|-------------|
| `/threat-model` | `/tachi.threat-model` |
| `/risk-score` | `/tachi.risk-score` |
| `/compensating-controls` | `/tachi.compensating-controls` |
| `/infographic` | `/tachi.infographic` |
| `/security-report` | `/tachi.security-report` |
| *(new)* | `/tachi.architecture` |

Upgrading: Run `install.sh` — it automatically removes old unprefixed command files and installs the new `tachi.*` versions.

---

## [4.6.0](https://github.com/davidmatousek/tachi/compare/v4.5.0...v4.6.0) (2026-04-09)


### Features

* **119:** auto-polish release notes via Claude API after release ([a44127f](https://github.com/davidmatousek/tachi/commit/a44127fccd11aef959cc1939670158ac8dffabb6)), closes [#119](https://github.com/davidmatousek/tachi/issues/119)


### Bug Fixes

* **119:** move release notes polishing to local-only script ([0dd33fd](https://github.com/davidmatousek/tachi/commit/0dd33fd4c4fd686393207837485386afac16ad03))

## [4.5.0](https://github.com/davidmatousek/tachi/compare/v4.4.2...v4.5.0) (2026-04-09)

### Added

- **Attack Path Pages in PDF Reports** (Feature 112) — Each Critical and High finding with an attack tree now gets a dedicated page in the security report PDF, showing a rendered Mermaid diagram, plain-English narrative explaining the attack chain, and specific remediation steps. Pages are ordered by severity (Critical first) and introduced by an "Attack Path Analysis" section divider with TOC entry. Mermaid diagrams render to PNG at 2x resolution via `mmdc`; graceful text fallback when the tool is unavailable. Fully backward compatible — reports without attack trees generate identically to before.
- **Automated release notes polishing** (Feature 119) — Local script (`scripts/polish-release-notes.sh`) rewrites auto-generated release notes into user-facing language via Claude API. Run after merging a Release PR.
- **README refresh** — Updated with MAESTRO layer classification, `/security-report` command, baseline delta tracking, all 5 infographic templates, and 6 examples (was 3).

### Changed

- release-please now hides `docs`, `chore`, `refactor`, `test`, and `style` commits from auto-generated CHANGELOG entries. Only `feat`, `fix`, and `perf` appear.

---

## [4.4.2](https://github.com/davidmatousek/tachi/compare/v4.4.1...v4.4.2) (2026-04-09)

### Fixed

- MAESTRO heading detection now falls back gracefully when headings use inconsistent formatting in threat-report.md. Attack trees regenerated fresh for all 6 examples. MAESTRO Findings section now appears in all reports and PDF output.

---

## [4.4.1](https://github.com/davidmatousek/tachi/compare/v4.4.0...v4.4.1) (2026-04-09)

### Fixed

- Attack tree generation no longer includes RESOLVED findings. Previously, findings marked as resolved in a baseline comparison still produced attack trees, cluttering the report with irrelevant attack paths.

---

## [4.4.0](https://github.com/davidmatousek/tachi/compare/v4.3.4...v4.4.0) (2026-04-09)

### Added

- **Downstream Baseline Propagation** (Feature 104) — Baseline severity and status fields from `threats.md` now propagate through all pipeline stages: risk scoring, compensating controls, threat report, infographics, and PDF report. Delta annotations (NEW, UNCHANGED, UPDATED, RESOLVED) carry through the entire pipeline. New Section 8 (Delta Summary) in `threats.md` and `threat-report.md`. All 6 example outputs regenerated with baseline columns.

---

## [4.3.4](https://github.com/davidmatousek/tachi/compare/v4.3.3...v4.3.4) (2026-04-08)

### Fixed

- Baseline-aware pipeline now enforces mandatory Phase 2 discovery even when a baseline exists, preventing false confidence from carry-forward-only runs.

---

## [4.3.3](https://github.com/davidmatousek/tachi/compare/v4.3.2...v4.3.3) (2026-04-08)

### Fixed

- Baseline auto-detection now correctly resolves paths, and downstream commands (`/risk-score`, `/compensating-controls`) no longer exceed context limits when processing large baseline files.

---

## [4.3.2](https://github.com/davidmatousek/tachi/compare/v4.3.1...v4.3.2) (2026-04-08)

### Fixed

- Version reporting (`install.sh`) now fetches tags before checking the installed version, showing the correct tag instead of a commit hash.
- release-please respects `release-please-config.json` instead of using a hardcoded release type.

---

## [4.3.1](https://github.com/davidmatousek/tachi/compare/v4.3.0...v4.3.1) (2026-04-08)

### Fixed

- Version examples in README and `install.sh` now auto-bump via release-please extra-files configuration.

---

## [4.3.0](https://github.com/davidmatousek/tachi/compare/v4.2.1...v4.3.0) (2026-04-08)

### Added

- **MAESTRO Infographic Templates and PDF Report Section** (Feature 091) — Two new infographic templates for MAESTRO-aware threat visualization: `maestro-stack` (vertical seven-layer risk distribution diagram) and `maestro-heatmap` (component-by-layer severity grid). New MAESTRO Findings page in the PDF security report. `maestro` shorthand in `/infographic` generates both templates in one invocation. All gated by `has-maestro-data` for backward compatibility with non-agentic threat models.

---

## [4.2.1](https://github.com/davidmatousek/tachi/compare/v4.2.0...v4.2.1) (2026-04-08)

### Fixed

- release-please workflow now supports `workflow_dispatch` for manual re-runs.

---

## [4.2.0](https://github.com/davidmatousek/tachi/compare/v4.1.0...v4.2.0) (2026-04-08)

### Added

- **MAESTRO Layer Mapping** (Feature 084) — Every threat finding is now classified into the CSA MAESTRO seven-layer taxonomy (L1 Foundation Model through L7 User Interface). The orchestrator assigns layers via keyword classification in Phase 1, and the mapping propagates downstream through risk scoring, compensating controls, and the threat report. New `maestro_layer` field in the finding schema (v1.2), SARIF `maestro-layer` tags, and MAESTRO Layer columns in all output tables. All 6 example outputs regenerated.

---

## [4.1.0](https://github.com/davidmatousek/tachi/compare/v4.0.0...v4.1.0) (2026-04-07)

### Added

- **Automated Release Tagging** (Feature 086) — Releases are now automated via Google's release-please GitHub Action. Conventional commits on main trigger a Release PR with auto-generated CHANGELOG entries. Merging the Release PR creates the git tag and GitHub Release. New files: `.github/workflows/release-please.yml`, `release-please-config.json`, `.release-please-manifest.json`.

---

## 4.0.x — Pre-release-please Features

*These features shipped between v4.0.0 and v4.1.0, before release-please was adopted. They were not individually tagged.*

### Feature 112 context already captured in v4.5.0 above.

### Feature 078 — Agent Context Optimization

Restructured 6 tachi agents from monolithic prompts to lean definitions with on-demand skill references. Created 4 skill directories with 25+ granular reference files. Shared severity bands, STRIDE+AI categories, and finding format as single-source-of-truth. 40-60% prompt size reduction across methodology agents.

### Feature 075 — Tachi Agent Best Practices

Shared best practices document with tier caps (Leaf 300, Report 800, Methodology 1,000 lines), 8-criterion quality checklist. Extracted domain knowledge from orchestrator (-39%), report agent (-41%), and control-analyzer (-30%) into dedicated skills.

### Feature 074 — Baseline-Aware Pipeline

Baseline-aware threat detection with 4-phase correlation (detect, carry-forward, discover, merge+dedup), coverage checklists per component type, delta annotations (NEW, UNCHANGED, UPDATED, RESOLVED), and SARIF `baselineState` properties. Compare threat model runs to track risk posture changes over time.

### Feature 071 — Deterministic Infographic Data Extraction

Shared parser module (`scripts/tachi_parsers.py`) and deterministic extraction script (`scripts/extract-infographic-data.py`) replacing LLM-based markdown parsing for infographics. Largest Remainder Method for percentage rounding, deterministic tie-breaking, 4-tier risk funnel computation. Python 3.9+ stdlib only.

### Feature 067 — Deterministic Report Data Extraction

Deterministic Python parsing script (`scripts/extract-report-data.py`) replacing LLM-based markdown extraction for PDF report generation. 3-tier severity source selection, internal consistency validation, scope data extraction. Zero external dependencies.

### Feature 066 — Install Script and Version Tagging

Single-command install script (`scripts/install.sh`) replacing 6+ manual `cp` commands. Supports `--source` override, `--version` pinned installs with trap-based cleanup. First semantic version tag `v4.0.0`.

### Feature 060 — Professional PDF Security Report

Professional branded PDF with modular Typst template system: disclaimer, TOC, methodology, scope, theme, and report-config pages. `brand/` asset directory with logo variants. Extended `security-report.yaml` schema v1.1.

### Feature 054 — Security Assessment PDF Booklet

`/security-report` command and report-assembler agent for generating multi-page PDF security assessment booklets from tachi pipeline artifacts. 7 Typst templates, graceful degradation for partial pipelines, full-bleed landscape infographic pages.

### Feature 053 — Risk Reduction Funnel

4-tier risk reduction funnel infographic template with graceful degradation (4-tier/3-tier/1-tier modes), ghost tiers with CTAs, and metrics sidebar.

### Feature 048 — Infographic Tiered Pipeline Auto-Detection

Three-tier data source auto-detection for `/infographic` (compensating-controls.md > risk-scores.md > threats.md). Residual risk extraction, enhancement tips at each pipeline tier, risk label distinction across templates.

### Feature 045 — Developer Guide

Comprehensive developer guide covering tachi's command pipeline with step-by-step walkthrough, pipeline diagram, and command reference.

### Feature 039 — Standalone /infographic Command

`/infographic` as a standalone command with auto-detection, dual-path extraction, and template selection. Removed from `/threat-model` pipeline (now 5-phase only).

### Feature 036 — Compensating Controls Analysis

`/compensating-controls` command with 6-phase pipeline, 8 STRIDE + 2 AI control categories, effectiveness classification, residual risk calculation, and dual-format output (markdown + SARIF).

### Feature 035 — Quantitative Risk Scoring

`/risk-score` command with four-dimensional scoring (CVSS 3.1, exploitability, scalability, reachability), weighted composite scores, governance fields, and dual-format output (markdown + SARIF).

### Feature 029 — Agent Right-Sizing

Right-sized 3 threat agents via reference-extraction pattern: orchestrator (-39%), report (-41%), infographic (-30%). 6 reference docs extracted. Portable `.claude/agents/tachi/` agent set.

### Feature 024 — Example Threat Models

Three end-to-end examples: web-app (STRIDE), agentic-app (STRIDE + AI), microservices (cross-service STRIDE). Each with Mermaid architecture and schema v1.1 output.

### Feature 021 — Platform Adapters

Adapters for 5 targets: Claude Code, Generic, Cursor, Copilot, GitHub Actions (with SARIF upload).

### Feature 018 — Threat Infographic Agent

Visual risk spec generation with Gemini API image output. Integrated as orchestrator Phase 6.

### Feature 015 — Threat Report Agent & Attack Trees

Narrative threat report with STRIDE+AI attack trees (Mermaid). 7-section template with 12 attack tree examples.

### Feature 012 — SARIF Output Generation

SARIF 2.1.0 output with STRIDE+AI rule mapping, CVSS severity alignment, deterministic fingerprints, and optional OWASP/CWE taxonomies.

### Feature 010 — Deduplication & Risk Rating

Cross-agent finding correlation with 5 deterministic rules, three-state coverage matrix, and OWASP 3x3 risk calibration. Schema v1.1.

### Feature 007 — AI Threat Agents

5 AI threat agent prompts: prompt injection, data poisoning, tool abuse, model theft, agent autonomy.

### Feature 003 — Orchestrator Agent

Orchestrator with 4-phase OWASP workflow, 5-format input parsing, 11-agent dispatch, and structured output assembly.

### Feature 001 — Project Skeleton

Project skeleton with STRIDE + AI threat agent prompts, schemas, output template, interface contract, and 3 example inputs.

---

## [4.0.0](https://github.com/davidmatousek/tachi/compare/v3.0.0...v4.0.0) (2026-02-08)

### BREAKING CHANGES

- **AOD Rebranding** — `.specify/` directory renamed to `.aod/`, `docs/SPEC_KIT_TRIAD.md` renamed to `docs/AOD_TRIAD.md`, environment variables and log prefixes updated. Update any local scripts referencing `.specify/` paths.

### Added

- 3 new thinking lenses: Four Causes, Cargo Cult Detection, Golden Mean.

---

## [3.0.0](https://github.com/davidmatousek/tachi/compare/v2.1.0...v3.0.0) (2026-02-07)

### BREAKING CHANGES

- **SpecKit commands removed** — All `/speckit.*` commands consolidated into `/triad.*`. See [migration table in previous CHANGELOG](https://github.com/davidmatousek/tachi/blob/v3.0.0/CHANGELOG.md) for command mapping.

### Added

- 4 new triad commands: `/triad.clarify`, `/triad.analyze`, `/triad.checklist`, `/triad.constitution`.

### Removed

- All 8 `/speckit.*` command files and "Vanilla Commands" documentation.

---

## [2.1.0](https://github.com/davidmatousek/tachi/compare/v2.0.0...v2.1.0) (2026-01-31)

### Added

- Agent refactoring: all 12 agents restructured to consistent 8-section format (58% line reduction). Team-lead split into team-lead + orchestrator (13 agents). New thinking-lens skill.

---

## [2.0.0](https://github.com/davidmatousek/tachi/compare/v1.1.0...v2.0.0) (2026-01-24)

### Added

- **Parallel Triad Reviews** — PM + Architect reviews run simultaneously with context forking. Triple sign-off executes in parallel.
- Automatic Claude Code version detection with feature flags and graceful degradation.

---

## [1.1.0](https://github.com/davidmatousek/tachi/compare/v1.0.0...v1.1.0) (2025-12-15)

### Added

- Modular rules system: governance, git workflow, deployment, scope, commands, and context loading extracted from CLAUDE.md (192 → 70 lines).

---

## [1.0.0](https://github.com/davidmatousek/tachi/releases/tag/v1.0.0) (2025-12-04)

### Added

- Initial release: product-led governance template, SDLC Triad framework, 13 agents, 8 skills, triad + vanilla commands, documentation structure.
