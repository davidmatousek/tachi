# Data Model: Substitution Surface Hardening (Feature 248)

This feature is configuration-and-template-shaped, not domain-object-shaped. The "data" entities are filesystem artifacts whose **shape, lifecycle, and validation rules** F-1 enforces. Each entity below has: definition, fields/structure, validation rules, lifecycle states, and ownership contract.

## E-1 — Personalization Snapshot

**Path**: `.aod/personalization.env`
**Purpose**: Canonical KEY=VALUE record of all 12 placeholder values; sourced by `init.sh` (post-F-1 reordered flow) and `update.sh` to populate `AOD_PERSONALIZATION_<KEY>` env vars consumed by `aod_template_substitute_placeholders`.
**Format**: bash-sourceable file, one `KEY=VALUE` line per canonical placeholder.

### Fields (12 canonical keys, locked under Q-1 Option b)

| Key | Source | Length cap (FR-005) | Validation rule |
|-----|--------|---------------------|------------------|
| `PROJECT_NAME` | `read -p` prompt | 100 chars | non-empty; no newline; no NUL; no 0x00–0x1F control |
| `PROJECT_DESCRIPTION` | `read -p` prompt | 300 chars | same charset; may be empty (post-validation rules permitting) |
| `GITHUB_ORG` | `read -p` prompt | 39 chars (GitHub login limit) | same charset |
| `GITHUB_REPO` | `read -p` prompt + default fallback to `$PROJECT_NAME` | 100 chars | same charset |
| `AI_AGENT` | menu choice | (enum) | one of: claude, gemini, ... |
| `TECH_STACK` | `read -p` prompt | 200 chars | same charset |
| `TECH_STACK_DATABASE` | `read -p` prompt | 200 chars | same charset |
| `TECH_STACK_VECTOR` | derived/default | 200 chars | derived from TECH_STACK |
| `TECH_STACK_AUTH` | derived/default | 200 chars | derived from TECH_STACK |
| `RATIFICATION_DATE` | `date '+%Y-%m-%d'` | (ISO 8601) | computed |
| `CURRENT_DATE` | `date '+%Y-%m-%d'` | (ISO 8601) | computed |
| `CLOUD_PROVIDER` | `read -p` prompt | 100 chars | same charset; may be empty |

### Validation rules

- **No embedded literal newline** in any value (NUL not allowed; control chars not allowed). Enforced by `aod_template_load_personalization_env` at line 205 of template-substitute.sh (returns 8 on violation).
- **All canonical keys non-empty post-init** — validated by the same loader; missing key returns 8.
- **File mode**: 0644 (default umask result).
- **Encoding**: UTF-8 (POSIX locale-safe; bash 3.2 handles UTF-8 byte-string semantics correctly).

### Lifecycle states

```
(absent) → init writes → present (populated, read-only at init's perspective)
                          │
                          ├─ pre-flight check on subsequent init.sh invocation → FATAL exit
                          ├─ sourced by aod_template_load_personalization_env → AOD_PERSONALIZATION_<KEY> env vars set
                          └─ source-of-truth for /aod.update on later runs
```

### Gitignore policy

- Default: gitignored at `.gitignore:222`. Adopters who want it tracked can opt-in by removing the line (Stream 3 documents this in `contracts/personalization-schema.md`).
- Migration command for previously-committed adopters (CHANGELOG): `git rm --cached .aod/personalization.env && git commit -m "chore: untrack personalization snapshot per BLP-02 default"`.

### Ownership contract

- **Producer**: `init.sh` (post-F-1; reorder: write BEFORE substitution loop, not after as in pre-F-1).
- **Consumer**: `aod_template_load_personalization_env` (.aod/scripts/bash/template-substitute.sh:143-234), called by both `init.sh` (post-F-1) and `update.sh`.

## E-2 — Canonical Placeholder Set

**Path**: `.aod/scripts/bash/template-substitute.sh:50-63` (lines locked; bash array `AOD_CANONICAL_PLACEHOLDERS`).
**Purpose**: The closed enumeration of all valid template placeholders. Placeholders not in this set fail the residual scan rather than fail-silent.

### Fields (under Q-1 Option b — locked at 12)

```
PROJECT_NAME
PROJECT_DESCRIPTION
GITHUB_ORG
GITHUB_REPO
AI_AGENT
TECH_STACK
TECH_STACK_DATABASE
TECH_STACK_VECTOR
TECH_STACK_AUTH
RATIFICATION_DATE
CURRENT_DATE
CLOUD_PROVIDER
```

(Under Q-1 Option a fallback — extended to 13 with `PROJECT_PATH` populated via `realpath "$(pwd)"` and validated against character whitelist `[A-Za-z0-9._/-]`.)

### Validation rules

- Array literal in bash 3.2-compatible syntax (no associative arrays; positional indexing).
- The `_aod_substitute_lookup <key>` case-statement at lines 97-115 MUST handle every key in this array; adding a key without updating the case-statement is a contract violation caught by lookup returning 1 (key unknown).

### Lifecycle states

- **Locked under Option b**: no expansion in F-1.
- **Expanded under Option a (fallback)**: PROJECT_PATH added; ADR-038 §Decision documents the lockstep update of array + case-statement + schema + validation rules.

### Ownership contract

- **Producer**: maintainers of `template-substitute.sh` (this is a contract surface; changes require ADR per Constitution).
- **Consumer**: `aod_template_substitute_placeholders` (substitution loop), `aod_template_init_personalization` (snapshot writer), `aod_template_assert_no_residual` (post-substitution scanner).

## E-3 — Vulnerability Event Log

**Path**: `.security/vulnerabilities.jsonl`
**Purpose**: JSONL audit trail capturing `DETECTED → REMEDIATED → WONTFIX` lifecycle for every `/security`-flagged vulnerability. F-1 appends 5 `REMEDIATED` events post-merge; **no schema bump** (NFR-005).

### Existing event shape (preserved)

Each line is a single JSON object. Per existing schema (`schemas/finding.yaml`):

```json
{
  "vuln_id": "TACHI-VULN-<12hex>",
  "event_type": "DETECTED|REMEDIATED|WONTFIX",
  "timestamp": "2026-05-03T18:56:58Z",
  "commit_sha": "<merge-commit-sha>",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
  "owasp_category": "A03|A05|...",
  "title": "<one-line summary>",
  "file_path": "<relative path>",
  "line_number": <int>,
  "cvss_base_score": <float>,
  "cwe": "CWE-<id>",
  ...
}
```

### F-1 contribution (5 new REMEDIATED events post-merge)

| vuln_id | severity | title |
|---------|----------|-------|
| TACHI-VULN-6bc17fd01ac8 | HIGH | sed substitution interprets metachars |
| TACHI-VULN-77f0519f9cfb | MEDIUM | read -p prompts accept any input |
| TACHI-VULN-bc67ca510ea9 | MEDIUM | .aod/personalization.env not gitignored (closure verification) |
| TACHI-VULN-30bbfd90959a | LOW | orphan {{PROJECT_PATH}} placeholder |
| TACHI-VULN-18127be5d214 | LOW | sed calls on constitution.md |

### Lifecycle states

```
(absent) → /security DETECTED → DETECTED entry appended (already present pre-F-1)
                                 │
                                 └─ F-1 squash-merge → REMEDIATED entry appended (with merge SHA + timestamp)
```

### Ownership contract

- **Producer**: `/security` skill (DETECTED events); `/aod.deliver` or post-merge automation (REMEDIATED events; F-1 closing operator authors these).
- **Consumer**: `tachi.compensating-controls`, `tachi.risk-score`, `/aod.deliver` retrospective.

## E-4 — Constitution Variants

**Paths**: `.aod/templates/constitution-clean.md` (NEW); `.aod/templates/constitution-instructional.md` (NEW); `.aod/memory/constitution.md` (existing post-init artifact).
**Purpose**: Two pre-stripped templates replace the runtime `sed -i` cleanup pass. The `clean` variant is copied at init time; the `instructional` variant is retained as documentation for downstream forks who want the embedded HTML-comment instructions and "## Template Instructions" guidance.

### Field shape

- Both variants are markdown files using the constitution structure (Core Principles, AOD Lifecycle Model, System Architecture Constraints, etc.).
- The `instructional` variant additionally contains:
  - HTML comment block at the top (`<!-- ... -->`) with template-author guidance.
  - `## Template Instructions` section near the bottom with derivation rules.
- The `clean` variant is byte-equivalent to running the current sed cleanup over `instructional` (verifies the migration is byte-faithful to the prior behavior).

### Validation rules

- **Byte-faithful relationship**: `instructional` → run-current-sed-cleanup → MUST equal `clean`. This is the migration safety check (manually verified once during Stream 1; not a runtime assertion).
- **Post-init equality**: `.aod/memory/constitution.md` MUST byte-equal `.aod/templates/constitution-clean.md` after `init.sh` completes. Test-4 enforces this.

### Lifecycle states

```
.aod/templates/constitution-clean.md       → static artifact (committed; updated only via PR)
.aod/templates/constitution-instructional.md → static artifact (committed; updated only via PR)
.aod/memory/constitution.md                 → produced at init by `cp .aod/templates/constitution-clean.md`
                                               (post-F-1; replaces the two `sed -i` invocations at init.sh:235-241)
```

### Ownership contract

- **Producer**: maintainers (templates committed once; updated via PR).
- **Consumer**: `init.sh` (cp at init time); downstream forks (instructional variant for docs).

## E-5 — ADR-038 (Architectural Decision Record)

**Path**: `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md` (NEW)
**Purpose**: Public artifact documenting the substitution mechanism migration, alternatives considered, and consequences. Required deliverable per FR-009. Dual-commit Proposed → Accepted lifecycle.

### Field shape (per ADR-000-template.md)

- **Status**: `Proposed` (initial commit) → `Accepted` (subsequent commit after architect adjudication of any concerns).
- **Context**: 2026-05-02 LinkedIn note + multi-hop chain analysis + 5 vuln_ids.
- **Decision**: bash parameter expansion via existing `aod_template_substitute_placeholders`; canonical residual-scan regex character class `[A-Z_]+`; lockstep update commitment if canonical-12 expands.
- **Alternatives Considered**: 4 enumerated (sed escape wrapper, awk -v, Python string.Template, Perl) with rationale for rejection.
- **Consequences**: one canonical pattern; bash 3.2 compatibility; literal-substitution semantics by language; PROJECT_PATH disposition (Option b default); Day 1 benchmark numbers.
- **Related Decisions**: cite ADR-009 as superseded on mechanism axis.
- **Related Findings**: 5 vuln_ids closed.
- **References**: Daniel Wood LinkedIn URL + `web.archive.org` snapshot URL.

### Validation rules

- **Status field**: literal string `Accepted` post dual-commit.
- **Required sections**: Status, Context, Decision, Alternatives Considered, Consequences, Related Decisions, References — all non-empty.

### Lifecycle states

```
(absent) → Stream 4 Day 1 → Proposed (committed) → Architect review → Accepted (committed)
```

### Ownership contract

- **Producer**: senior-backend-engineer (Stream 4 author); Architect (review + Accepted commit).
- **Consumer**: enterprise security architects (pre-sales review); future contributors (mechanism guidance).

## Data Flow Summary

```
adopter → init.sh prompts (validated by aod_init_read_validated) → 12 KEY=VALUE pairs
                                                                    │
                                                                    └─ E-1 .aod/personalization.env (written FIRST per FR-002)
                                                                       │
                                                                       └─ aod_template_load_personalization_env → AOD_PERSONALIZATION_<KEY> env vars
                                                                          │
                                                                          └─ aod_template_substitute_placeholders (literal sub via bash param expansion)
                                                                             │
                                                                             └─ aod_template_assert_no_residual (post-scan; halts on residual)
                                                                                │
                                                                                └─ cp .aod/templates/constitution-clean.md → .aod/memory/constitution.md (FR-008)
                                                                                   │
                                                                                   └─ rm -f scripts/init.sh (existing self-delete; re-init prevention)

post-merge:
   /aod.deliver → 5 REMEDIATED events appended to E-3 .security/vulnerabilities.jsonl (merge SHA + timestamp)
              ↓
   E-5 ADR-038 published in docs/architecture/02_ADRs/ (Status: Accepted)
              ↓
   release-please opens release PR within ~30s (FR-010 belt-and-suspenders verification)
```
