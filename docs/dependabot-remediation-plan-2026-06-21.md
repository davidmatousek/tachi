# Dependabot Remediation Plan - 2026-06-21

**Scope**: live GitHub Dependabot alerts for `pratik-saptarshi/tachi-rust`
queried on 2026-06-21.

**Affected manifest**: `stacks/nextjs-supabase/scaffold/package.json`

**Finding summary**:

| Severity | Count | Package | Root cause |
|---|---:|---|---|
| Critical | 1 | `vitest` | Scaffold devDependency admits `>=4.0.0 <4.1.0`. |
| High | 7 | `next` | Scaffold dependency admits vulnerable Next.js 16.0.0-16.2.5 ranges. |
| Medium | 4 | `next` | Same lower-bound range admits vulnerable Next.js versions. |
| Low | 2 | `next` | Same lower-bound range admits vulnerable Next.js versions. |

## Review Finding Classification

| Finding | Alerts | Severity | Package | Patched floor | Category | Disposition |
|---|---|---|---|---|---|---|
| R1-F01 | #14 | Critical | `vitest` | `4.1.0` | Must-fix | Track through `SEC-002`, `SEC-004`, `SEC-006`. |
| R1-F02 | #1-#13 | High aggregate | `next` | `16.2.6` | Must-fix | Track through `SEC-002`, `SEC-003`, `SEC-005`, `SEC-006`. |
| R1-F03 | #1-#14 | High | scaffold policy | n/a | Bundle | Add offline dependency-floor audit to publish gate via `SEC-005`. |

**Final recommendation**: Applied with caveats.

**Caveat**: this plan creates the remediation graph and acceptance criteria. It does
not change dependency versions yet; implementation must follow the RED-GREEN
order in the Beads graph.

**Dissent Ledger**: none.

## Root Cause

The scaffold uses broad lower-bound package ranges:

| Package | Current range | Vulnerable range admitted | Secure floor |
|---|---|---|---|
| `next` | `>=16.2.3` | `>=16.0.0 <16.2.6` | `^16.2.6` or stricter |
| `vitest` | `>=4.0.0` | `>=4.0.0 <4.1.0` | `^4.1.0` or stricter |

The secure implementation should prefer non-vulnerable caret ranges for the
template (`^16.2.6`, `^4.1.0`) rather than open-ended `>=` ranges. This keeps the
scaffold compatible with normal npm resolution while preventing Dependabot from
correctly flagging the manifest as allowing vulnerable installs.

## TDD Remediation Sequence

### Phase 0 - RED dependency-floor audit (`SEC-002`)

Write a test or audit harness that parses
`stacks/nextjs-supabase/scaffold/package.json` and fails before any dependency
version is changed.

Acceptance criteria:

| ID | Criterion |
|---|---|
| AC-002.1 | The test fails against the current manifest because `next` admits `<16.2.6`. |
| AC-002.2 | The test fails against the current manifest because `vitest` admits `<4.1.0`. |
| AC-002.3 | The failure message names the package, current range, secure floor, and alert IDs. |
| AC-002.4 | The test uses real manifest parsing, not mocked dependency data. |
| AC-002.5 | No production manifest changes are included in the RED commit. |

### Phase 1 - GREEN Next.js floor (`SEC-003`)

Update only the `next` scaffold dependency floor.

Acceptance criteria:

| ID | Criterion |
|---|---|
| AC-003.1 | The `next` range excludes `>=16.0.0 <16.2.6`. |
| AC-003.2 | The `SEC-002` audit passes for `next`. |
| AC-003.3 | Dependabot alerts #1-#13 close or are documented as GitHub lag with links. |
| AC-003.4 | No unrelated scaffold dependency is upgraded in this task. |
| AC-003.5 | Scaffold build/test commands remain documented and usable. |

### Phase 2 - GREEN Vitest floor (`SEC-004`)

Update only the `vitest` scaffold devDependency floor.

Acceptance criteria:

| ID | Criterion |
|---|---|
| AC-004.1 | The `vitest` range excludes `>=4.0.0 <4.1.0`. |
| AC-004.2 | The `SEC-002` audit passes for `vitest`. |
| AC-004.3 | Dependabot alert #14 closes or is documented as GitHub lag with link. |
| AC-004.4 | Test runner behavior is not broadened beyond the patched version floor. |
| AC-004.5 | No unrelated scaffold dependency is upgraded in this task. |

### Phase 3 - Regression gate (`SEC-005`)

Wire the dependency-floor audit into the publish/security gate.

Acceptance criteria:

| ID | Criterion |
|---|---|
| AC-005.1 | `make publish-gate` or a documented sub-gate runs the scaffold audit. |
| AC-005.2 | A synthetic vulnerable `next` range fails the gate. |
| AC-005.3 | A synthetic vulnerable `vitest` range fails the gate. |
| AC-005.4 | The current fixed manifest passes without network access. |
| AC-005.5 | Publish-readiness docs identify this as a release blocker. |

### Phase 4 - Closure and release (`SEC-006`)

Validate the remediation locally and remotely.

Acceptance criteria:

| ID | Criterion |
|---|---|
| AC-006.1 | The TDD transcript records RED then GREEN for the dependency audit. |
| AC-006.2 | `make publish-gate` passes. |
| AC-006.3 | `gh api repos/pratik-saptarshi/tachi-rust/dependabot/alerts` shows zero open alerts for the scaffold manifest, or documents GitHub lag. |
| AC-006.4 | Remote Actions pass for the remediation commit. |
| AC-006.5 | Release notes mention scaffold dependency hardening and the alert IDs closed. |

## Epic-Capability-Feature-Task-Function Mapping

| Epic | Capability | Feature | Task | Functions / seams |
|---|---|---|---|---|
| `SEC-001` | Secure dependency posture | Dependabot alert closure | `SEC-002` | `parse_package_manifest`, `assert_dependency_floor` |
| `SEC-001` | Secure scaffold templates | Next.js patched floor | `SEC-003` | `stacks/nextjs-supabase/scaffold/package.json` |
| `SEC-001` | Secure scaffold templates | Vitest patched floor | `SEC-004` | `stacks/nextjs-supabase/scaffold/package.json` |
| `SEC-001` | Release gate hardening | Offline dependency-floor gate | `SEC-005` | `Makefile`, publish gate scripts/tests |
| `SEC-001` | Release verification | Dependabot closure evidence | `SEC-006` | GitHub Dependabot API, Actions runs |

## Alert Traceability

| Alert | Severity | Package | Advisory | Patched | Beads |
|---:|---|---|---|---|---|
| 1 | High | `next` | GHSA-8h8q-6873-q5fj | 16.2.5 | `SEC-003`, `SEC-006` |
| 2 | High | `next` | GHSA-36qx-fr4f-26g5 | 16.2.5 | `SEC-003`, `SEC-006` |
| 3 | High | `next` | GHSA-267c-6grr-h53f | 16.2.5 | `SEC-003`, `SEC-006` |
| 4 | Medium | `next` | GHSA-wfc6-r584-vfw7 | 16.2.5 | `SEC-003`, `SEC-006` |
| 5 | High | `next` | GHSA-492v-c6pp-mqqv | 16.2.5 | `SEC-003`, `SEC-006` |
| 6 | High | `next` | GHSA-c4j6-fc7j-m34r | 16.2.5 | `SEC-003`, `SEC-006` |
| 7 | Medium | `next` | GHSA-h64f-5h5j-jqjh | 16.2.5 | `SEC-003`, `SEC-006` |
| 8 | High | `next` | GHSA-mg66-mrh9-m8jx | 16.2.5 | `SEC-003`, `SEC-006` |
| 9 | Medium | `next` | GHSA-gx5p-jg67-6x7h | 16.2.5 | `SEC-003`, `SEC-006` |
| 10 | Low | `next` | GHSA-vfv6-92ff-j949 | 16.2.5 | `SEC-003`, `SEC-006` |
| 11 | Medium | `next` | GHSA-ffhc-5mcf-pf4q | 16.2.5 | `SEC-003`, `SEC-006` |
| 12 | Low | `next` | GHSA-3g8h-86w9-wvmq | 16.2.5 | `SEC-003`, `SEC-006` |
| 13 | High | `next` | GHSA-26hh-7cqf-hhc6 | 16.2.6 | `SEC-003`, `SEC-006` |
| 14 | Critical | `vitest` | GHSA-5xrq-8626-4rwp | 4.1.0 | `SEC-004`, `SEC-006` |

## Action Items

| Priority | Owner | Action | Source finding |
|---|---|---|---|
| P0 | implementer | Start `SEC-002`; create and verify the RED dependency-floor test. | R1-F01, R1-F02 |
| P0 | implementer | Implement `SEC-003` and `SEC-004` in separate GREEN commits. | R1-F01, R1-F02 |
| P1 | implementer | Implement `SEC-005`; add offline regression coverage to the publish gate. | R1-F03 |
| P1 | reviewer | Complete `SEC-006`; verify GitHub alerts, Actions, and release notes. | R1-F01-R1-F03 |

## Key Decisions

| Decision | Rationale |
|---|---|
| Group 13 Next.js alerts under one task. | They share one manifest root cause and one highest patched floor: `16.2.6`. |
| Keep Vitest separate. | It is the only critical alert and affects a dev server/test runner surface. |
| Require RED before manifest edits. | The current manifest must fail before the package floor changes, proving the audit catches the vulnerability class. |
| Prefer offline floor audit over network-only npm audit. | The vulnerable condition is statically visible in `package.json`; release gating should not require registry access for this class. |
