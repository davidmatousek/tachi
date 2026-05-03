# Validation Results: T047-T050 (OWASP, Correlations, Existing Examples, Quickstart)

**Date**: 2026-03-23
**Validator**: tester agent
**Status**: PASS
**Issues Found**: 0

---

## Summary

| Task | Description | Result | Issues |
|------|-------------|--------|--------|
| T047 | Correlated findings in agentic-app Section 4a | PASS | 0 |
| T048 | OWASP appendix accuracy (all 3 examples) | PASS | 0 |
| T049 | Existing example directories intact | PASS | 0 |
| T050 | Quickstart.md file path validation | PASS | 0 |

---

## T047: Agentic-App Correlated Findings Validation

**Requirement**: Section 4a must contain at least 1 correlation group with valid finding references.

### Groups Found: 2

#### CG-1: Data Integrity Correlation

| Field | Value | Valid |
|-------|-------|-------|
| Findings | T-2, LLM-2 | YES - both exist in Sections 3.2 and 4.2 |
| Component | LLM Agent Orchestrator | YES - both T-2 and LLM-2 target LLM Agent Orchestrator |
| Correlation Rule | CR-1 (Tampering + Data-Poisoning) | YES - T-2 is Tampering, LLM-2 is data poisoning |
| Risk Level | Medium | YES - T-2 is Medium, LLM-2 is Medium; highest = Medium |

**T-2 verification**: Section 3.2, Component = LLM Agent Orchestrator, Risk = Medium. Present.
**LLM-2 verification**: Section 4.2, Component = LLM Agent Orchestrator, Risk = Medium. Present.

#### CG-2: Excessive Permissions Correlation

| Field | Value | Valid |
|-------|-------|-------|
| Findings | E-1, AG-1 | YES - both exist in Sections 3.6 and 4.1 |
| Component | LLM Agent Orchestrator | YES - both E-1 and AG-1 target LLM Agent Orchestrator |
| Correlation Rule | CR-2 (Privilege-Escalation + Agent-Autonomy) | YES - E-1 is Elevation of Privilege, AG-1 is Agentic autonomy escalation |
| Risk Level | High | YES - E-1 is High, AG-1 is High; highest = High |

**E-1 verification**: Section 3.6, Component = LLM Agent Orchestrator, Risk = High. Present.
**AG-1 verification**: Section 4.1, Component = LLM Agent Orchestrator, Risk = High. Present.

### T047 Verdict: PASS
- At least 1 correlation group: YES (2 groups found)
- All finding IDs exist in Sections 3 and 4: YES (T-2, LLM-2, E-1, AG-1 all verified)
- Correlation rules followed: YES (CR-1 for CG-1, CR-2 for CG-2)
- Same component per group: YES (both groups target LLM Agent Orchestrator)
- Risk Level = highest among members: YES (Medium for CG-1, High for CG-2)

---

## T048: OWASP Appendix Accuracy

### web-app

**Framework**: OWASP Top 10 Web 2025 (A01-A10)

**Distinct categories referenced**:

| Category | Category Name | Finding Count |
|----------|---------------|---------------|
| A01:2025 | Broken Access Control | 2 (E-1, E-2) |
| A02:2025 | Security Misconfiguration | 2 (T-2, I-2) |
| A04:2025 | Cryptographic Failures | 1 (I-3) |
| A05:2025 | Injection | 1 (T-3) |
| A06:2025 | Insecure Design | 2 (D-1, D-2) |
| A07:2025 | Authentication Failures | 4 (S-1, S-2, S-3, I-1) |
| A08:2025 | Software or Data Integrity Failures | 1 (T-1) |
| A09:2025 | Security Logging and Alerting Failures | 3 (R-1, R-2, R-3) |
| A10:2025 | Mishandling of Exceptional Conditions | 2 (D-1, D-2) |

**Distinct categories**: 9 (meets minimum of 5)

**Finding ID cross-check** (all 16 findings verified in STRIDE tables):
S-1, S-2, S-3, T-1, T-2, T-3, R-1, R-2, R-3, I-1, I-2, I-3, D-1, D-2, E-1, E-2 -- all present in Section 3 STRIDE tables.

**Result**: PASS

### agentic-app

**Frameworks**: OWASP Top 10 Web 2025 + OWASP Agentic Top 10 2026 (ASI) + OWASP MCP Top 10 2025 (MCP)

**STRIDE findings mapped to OWASP Web 2025**:

| Finding ID | OWASP Category | Verified in STRIDE |
|------------|----------------|--------------------|
| S-1 | A07 | YES (Section 3.1) |
| S-2 | A08 | YES (Section 3.1) |
| S-3 | A08 | YES (Section 3.1) |
| T-1 | A08 | YES (Section 3.2) |
| T-2 | A02 | YES (Section 3.2) |
| T-3 | A09 | YES (Section 3.2) |
| R-1 | A09 | YES (Section 3.3) |
| R-2 | A09 | YES (Section 3.3) |
| R-3 | A09 | YES (Section 3.3) |
| I-1 | A01 | YES (Section 3.4) |
| I-2 | A01 | YES (Section 3.4) |
| I-3 | A04 | YES (Section 3.4) |
| D-1 | A06 | YES (Section 3.5) |
| D-2 | A06 | YES (Section 3.5) |
| E-1 | A01 | YES (Section 3.6) |
| E-2 | A05 | YES (Section 3.6) |

**AG findings mapped to OWASP Agentic Top 10 2026 (ASI)**:

| Finding ID | ASI Category | Verified in Section 4.1 |
|------------|--------------|-------------------------|
| AG-1 | ASI03 (Identity and Privilege Abuse) | YES |
| AG-2 | ASI02 (Tool Misuse and Exploitation) | YES |
| AG-3 | ASI01 (Agent Goal Hijack) | YES |
| AG-4 | ASI02 (Tool Misuse and Exploitation) | YES |

**Distinct ASI categories**: 3 (ASI01, ASI02, ASI03) -- meets minimum of 3.

**LLM/MCP findings mapped to OWASP MCP Top 10 2025 (MCP)**:

| Finding ID | MCP Category | Verified in Section 4.2 |
|------------|--------------|-------------------------|
| LLM-1 | MCP10 (Context Injection and Over-Sharing) | YES |
| LLM-2 | MCP03 (Tool Poisoning) | YES |
| LLM-3 | MCP05 (Command Injection and Execution) | YES |

**Distinct MCP categories**: 3 (MCP03, MCP05, MCP10) -- meets minimum of 2.

**Finding ID cross-check**: All 23 Finding IDs in the appendix (S-1 through E-2, AG-1 through AG-4, LLM-1 through LLM-3) verified as present in their respective STRIDE (Section 3) or AI (Section 4) tables.

**Result**: PASS

### microservices

**Framework**: OWASP Top 10 Web 2025 (A01-A10)

**Distinct categories referenced**:

| Category | Category Name | Finding Count |
|----------|---------------|---------------|
| A01:2025 | Broken Access Control | 6 (T-3, I-2, I-3, E-1, E-2, E-3) |
| A02:2025 | Security Misconfiguration | 3 (I-1, I-4, D-4) |
| A04:2025 | Cryptographic Failures | 2 (S-4, T-2) |
| A06:2025 | Insecure Design | 2 (D-3, E-4) |
| A07:2025 | Authentication Failures | 3 (S-1, S-2, S-3) |
| A08:2025 | Software or Data Integrity Failures | 2 (T-1, T-4) |
| A09:2025 | Security Logging and Alerting Failures | 3 (R-1, R-2, R-3) |
| A10:2025 | Mishandling of Exceptional Conditions | 2 (D-1, D-2) |

**Distinct categories**: 8 (meets minimum of 5). File itself states "8 of 10 categories referenced."

**Finding ID cross-check** (all 23 findings verified in STRIDE tables):
S-1, S-2, S-3, S-4, T-1, T-2, T-3, T-4, R-1, R-2, R-3, I-1, I-2, I-3, I-4, D-1, D-2, D-3, D-4, E-1, E-2, E-3, E-4 -- all present in Section 3 STRIDE tables.

**Result**: PASS

### T048 Verdict: PASS
- web-app: 9 distinct OWASP Web categories, all finding IDs verified
- agentic-app: 3 ASI categories (min 3), 3 MCP categories (min 2), all IDs verified
- microservices: 8 distinct OWASP Web categories, all finding IDs verified

---

## T049: Existing Example Directories Integrity

**Requirement**: Three pre-existing example directories must remain intact and unmodified.

### ascii-web-api

| File | Status |
|------|--------|
| `examples/ascii-web-api/input.md` | EXISTS |
| `examples/ascii-web-api/threats.md` | EXISTS |

**git diff main**: No changes detected.

### free-text-microservice

| File | Status |
|------|--------|
| `examples/free-text-microservice/input.md` | EXISTS |
| `examples/free-text-microservice/threats.md` | EXISTS |

**git diff main**: No changes detected.

### mermaid-agentic-app

| File | Status |
|------|--------|
| `examples/mermaid-agentic-app/input.md` | EXISTS |
| `examples/mermaid-agentic-app/threats.md` | EXISTS |
| `examples/mermaid-agentic-app/attack-trees/` | EXISTS (directory with 14 items) |
| `examples/mermaid-agentic-app/threat-infographic-spec.md` | EXISTS |
| `examples/mermaid-agentic-app/threat-report.md` | EXISTS |

**git diff main**: No changes detected.

### T049 Verdict: PASS
- All three directories exist with their original files
- `git diff main` shows zero modifications to any existing example file
- `git status` reports clean working tree for these directories

---

## T050: Quickstart.md File Path Validation

**Requirement**: All file paths referenced in `specs/024-example-threat-models/quickstart.md` must exist in the repository.

| Path | Exists |
|------|--------|
| `examples/README.md` | YES |
| `examples/web-app/architecture.md` | YES |
| `examples/web-app/threats.md` | YES |
| `examples/agentic-app/architecture.md` | YES |
| `examples/agentic-app/threats.md` | YES |
| `examples/microservices/architecture.md` | YES |
| `examples/microservices/threats.md` | YES |

### T050 Verdict: PASS
- All 7 file paths verified as present in the repository.

---

## Overall Result

**STATUS: PASS**
**Issues Found: 0**
**All 4 validation tasks passed with no issues.**
