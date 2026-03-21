# agents/stride/

STRIDE threat agents — one agent per classic STRIDE category. Each agent analyzes an architecture input and produces threat findings for its assigned category.

## STRIDE Categories

| Agent | Threat Class | Focus |
|-------|-------------|-------|
| `spoofing.md` | Spoofing | Identity forgery, authentication bypass |
| `tampering.md` | Tampering | Data integrity violations, unauthorized modifications |
| `repudiation.md` | Repudiation | Audit gaps, deniable actions, missing logging |
| `info-disclosure.md` | Information Disclosure | Data leaks, excessive exposure, side channels |
| `denial-of-service.md` | Denial of Service | Resource exhaustion, availability attacks |
| `privilege-escalation.md` | Elevation of Privilege | Authorization bypass, privilege escalation |

## How Agents Work

Each agent receives the architecture input (data flow diagram, system description) and produces threat findings scoped to its category. Agents run independently and can execute in parallel.
