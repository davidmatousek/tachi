# Code Economy Standards

These rules apply to ALL agents that generate or modify code, regardless of stack.
Climb the ladder below **before** writing net-new code. The safety carve-outs in Section 1 are hard constraints — do not deviate without explicit user override.

> Adapted from the "laziness ladder" in [ponytail](https://github.com/DietrichGebert/ponytail) (MIT License, © Dietrich Gebert). AOD takes the concept and wording, not the code, and re-anchors rung 1 to `spec.md` for Triad-governed scope.

---

## 1. Safety Carve-Outs (Never Shortcut)

The ladder optimizes for *less code*, never *less safety*. These are stated **first** because they frame everything below: no rung may trade any of them away for brevity. When a minimal implementation would shorten one of these, the carve-out wins unconditionally — the ladder may never be used to justify removing it.

| Carve-out | Requirement |
|-----------|-------------|
| **Understand first** | Understand the problem fully before writing anything. Economy applies to the solution, never to the analysis. |
| **Input validation** | Validate and sanitize input at every trust boundary. Never drop validation to save lines. |
| **Error handling** | Handle errors that could cause data loss, corruption, or silent failure. Fail loudly, not silently. |
| **Security** | Authentication, authorization, secret handling, and least-privilege / deny-by-default are non-negotiable (OWASP). |
| **Accessibility** | UI changes meet WCAG AA. Accessibility is a requirement, not an enhancement. |
| **One runnable check** | Non-trivial logic ships with at least one runnable check (test, assertion, or executable example). |

These are inviolable. The ladder begins only after they are satisfied.

---

## 2. The Laziness Ladder

Before writing net-new code for any task, climb these rungs **in order** and stop at the lowest one that satisfies the requirement. Each rung is a question; only reach "write new code" when every rung above it is a genuine "no."

1. **Does the spec require this?** — The top rung is **anchored to `spec.md`**, not to agent discretion. Ask "does the spec require this?", not "do I think this is useful?". Scope is a **Triad / PM decision** (constitution X, Product-Spec Alignment); if the spec does not require it, it does not get built. This is YAGNI, governed.
2. **Can existing code do it?** — Reuse an existing function, helper, component, or pattern in the codebase before writing a new one. (Rule of Three: don't abstract until the third instance.)
3. **Can the standard library do it?** — Prefer the language's standard library over hand-rolled logic.
4. **Can a native platform feature do it?** — Prefer a built-in platform / runtime / framework capability over custom machinery.
5. **Can an already-installed dependency do it?** — Use a dependency already in the manifest before adding a new one. (Adding a dependency is itself a rung-1 question for the spec.)
6. **Can it be one line?** — Prefer the smallest expression that is still clear. Clever ≠ economical; clarity is the bar.
7. **Only then: write minimal new code.** — The least code that satisfies the spec *and* the carve-outs above. Nothing speculative.

**Duplication over the wrong abstraction**: a little duplication is cheaper than a premature or wrong abstraction (Sandi Metz). When an abstraction proves wrong, inline it back.

---

## 3. Intentional-Simplification Marker

When you deliberately stop at a low rung — shipping less than the fullest solution because the spec does not (yet) require more — you MAY record the choice with a single-line comment so the next reader knows it was intentional, not an oversight:

```
<host-language comment leader> AOD-SIMPLIFICATION: <ceiling> — upgrade: <path>
```

- `<ceiling>` — what this implementation intentionally does **not** do (the simplification's limit).
- `<path>` — how to extend it if the spec later grows.

Examples:

```
// AOD-SIMPLIFICATION: single-tenant only — upgrade: add tenant_id scoping when multi-tenant lands
#  AOD-SIMPLIFICATION: in-memory cache — upgrade: swap for a shared store if cross-process sharing is needed
```

This is a **documentation convention only**. Nothing parses, tracks, counts, or enforces it; its absence is never a build or review failure. **Do not build a scanner, parser, or tracker for it** — that machinery would be the exact over-engineering this rule exists to prevent.

---

## When This Applies

- Any task that generates new code (functions, components, modules, endpoints, scripts).
- Any task that modifies existing code where a simpler path may exist.
- Does NOT apply to: documentation, configuration files, or CLI-only usage that produces no code.
