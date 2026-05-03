# Quickstart: Substitution Surface Hardening (F-1, BLP-02 Wave 1)

This quickstart documents the post-F-1 init flow for adopters and maintainers. Use it as a sanity check after Stream 1 lands.

## TL;DR

After F-1 lands:
- `scripts/init.sh` no longer uses `sed` for substitution. Bash parameter expansion (literal substitution) replaces it.
- 4 `read -p` prompts now validate input at prompt time (newline / NUL / control / over-length rejection; 3-strikes exit).
- `.aod/personalization.env` is gitignored by default (already true since `b27f3ea` 2026-04-19 — F-1 verifies + documents).
- Constitution cleanup uses `cp` from `.aod/templates/constitution-clean.md` (no `sed`).
- `.claude/mcp-config.json` is removed (Q-1 Option b default; conditional on internal-tooling search).
- ADR-038 documents the migration; release-please publishes the fix in the next release.

## End-to-End Adopter Flow

### Fresh-clone init

```bash
git clone https://github.com/davidmatousek/tachi.git my-project
cd my-project
./scripts/init.sh
```

You will be prompted:

```
Project Name: AT&T
Project Description: A description with a literal & character
GitHub Organization: my-org
GitHub Repository [AT&T]: my-repo
```

Each prompt validates the input. If you paste a value containing a newline, NUL byte, control character (0x00–0x1F), or over-length input, you'll see:

```
[init] Input rejected: <reason>; please re-enter.
```

After 3 consecutive rejections on the same prompt, init aborts with:

```
[init] FATAL: 3 consecutive invalid inputs for PROJECT_NAME; aborting.
```

### Post-init verification

After successful init, verify the substitution semantics held:

```bash
# 1. Verify literal substitution succeeded
grep -r "AT&T" .aod/ docs/ scripts/ 2>/dev/null
# → matches expected count (depends on your PROJECT_NAME)

# 2. Verify no orphan placeholders remain
grep -r '{{[A-Z_]\+}}' . --exclude-dir=.git --exclude-dir=node_modules
# → empty (residual scan post-substitution would have halted init if any survived)

# 3. Verify gitignore default
git status
# → .aod/personalization.env should NOT appear in change set

# 4. Verify constitution byte-equality
diff -q .aod/memory/constitution.md .aod/templates/constitution-clean.md
# → no output (byte-identical)

# 5. Verify self-delete
ls scripts/init.sh
# → "No such file or directory" — init.sh deleted itself per existing self-delete logic
```

### Re-init attempt (should fail)

If you try to run `init.sh` again on an already-personalized tree (e.g., from a fresh clone of the post-init repo):

```bash
./scripts/init.sh
# → [init] FATAL: Repository already personalized. Re-init is not supported.
#   To re-personalize, remove .aod/personalization.env and re-run init.sh.
# → exit code 1
```

(Note: in practice, `init.sh` deletes itself at the end of a successful run, so re-running requires a fresh clone or a manual `git checkout HEAD~1 -- scripts/init.sh`.)

## Migration Path for Existing Adopters

If you already committed `.aod/personalization.env` (i.e., you initialized before `b27f3ea`):

```bash
git rm --cached .aod/personalization.env
git commit -m "chore: untrack personalization snapshot per BLP-02 default"
```

The file remains on disk; only the index entry is removed.

## Maintainer Verification Checklist

After F-1 lands on `main`:

- [ ] `grep -n "sed " scripts/init.sh` returns 0 matches (FR-008 AC-8.1)
- [ ] `grep -n "replace_in_files" scripts/init.sh` returns 0 matches (FR-001 AC-1.1)
- [ ] `find . -name '*.bats'` returns 0 matches (FR-011 AC-11.1)
- [ ] `.claude/mcp-config.json` does not exist under Option b (FR-007 AC-7.1)
- [ ] `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md` exists with Status `Accepted` (FR-009 AC-9.2)
- [ ] `.security/vulnerabilities.jsonl` shows 5 `REMEDIATED` events with merge SHA (SC-001)
- [ ] release-please PR opened within ~30s of squash-merge (FR-010 AC-10.2)
- [ ] CI matrix (macos-latest + ubuntu-latest) shows green on the new pytest tests (FR-011 AC-11.3)

## Adversarial Smoke Test

For Test-6 (manual gating action before marking the feature ready):

```bash
# Clone fresh into tmpdir
git clone https://github.com/davidmatousek/tachi.git /tmp/tachi-smoke
cd /tmp/tachi-smoke

# Run init with a metachar-bearing project name
PROJECT_NAME='AT&T' \
PROJECT_DESCRIPTION='Description with literal & character' \
GITHUB_ORG='my-org' \
GITHUB_REPO='AT&T' \
AI_AGENT='claude' \
TECH_STACK='Python + FastAPI' \
TECH_STACK_DATABASE='PostgreSQL' \
TECH_STACK_VECTOR='pgvector' \
TECH_STACK_AUTH='JWT' \
CLOUD_PROVIDER='Vercel' \
./scripts/init.sh

# Verify literal substitution
grep -r 'AT&T' .aod/ docs/ scripts/ 2>/dev/null | wc -l   # → expected count > 0
grep -r 'tachi' . --exclude-dir=.git 2>/dev/null  # → empty

# Verify gitignore default
git status | grep -F '.aod/personalization.env'  # → empty (gitignored)

# Verify constitution byte-equality
diff -q .aod/memory/constitution.md .aod/templates/constitution-clean.md  # → no output

# Cleanup
cd /tmp && rm -rf tachi-smoke
```

If any step fails, **DO NOT mark F-1 ready**. File a CHANGES_REQUESTED and address the regression.

## Performance Sanity Check (Stream 1 Day 1, NFR-004)

Before and after the substitution swap, time the canonical fixture:

```bash
# Before (on a snapshot of pre-merge state)
time ./scripts/init.sh < canonical-fixture-input.txt

# After (on the F-1 branch)
time ./scripts/init.sh < canonical-fixture-input.txt
```

Record both `real` times. Calculate delta.

| Delta | NFR-004 disposition |
|-------|---------------------|
| ≤ 5% | Holds at 10%; record numbers in ADR-038 §Consequences |
| 5–50% | Loosen to 25% with rationale in ADR-038 |
| > 50% | Escalate to PM for re-scope before merge |

## Day-5 Slip Watch (per Team-Lead Pass 1)

If by EOD Wed 2026-05-08 (Day 5) the CI matrix has not recorded a green run on the new pytest tests, escalate to PM for scope-cut adjudication. Possible scope cuts (in priority order):

1. Drop Test-2 corpus from ≥13 to 8 cases (keep all rejection-class cases; drop substitution-only cases).
2. Defer Stream 4 ADR §Consequences benchmark numbers to a post-merge ADR amendment (PR with the numbers as a follow-up).
3. Defer Test-7 post-merge re-scan documentation to /aod.deliver retrospective.

(Hard floor: do NOT drop Test-1 fixture-replay byte-comparison or Test-2 cases 1–6 substitution-semantics correctness.)

## References

- **PRD**: [docs/product/02_PRD/248-substitution-surface-hardening-2026-05-03.md](../../docs/product/02_PRD/248-substitution-surface-hardening-2026-05-03.md)
- **Spec**: [spec.md](spec.md)
- **Plan**: [plan.md](plan.md)
- **Research**: [research.md](research.md)
- **Helper contract**: [contracts/init-input-helper-contract.md](contracts/init-input-helper-contract.md)
- **Existing safe function**: [.aod/scripts/bash/template-substitute.sh:318-411](../../.aod/scripts/bash/template-substitute.sh)
- **Vulnerability log**: [.security/vulnerabilities.jsonl](../../.security/vulnerabilities.jsonl)
