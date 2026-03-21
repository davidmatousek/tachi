# Scoring Rubric: OWASP 3x3 Risk Scoring

The scoring rubric defines quality dimensions for evaluating threat model outputs. Review commands score each output against these dimensions to determine production readiness.

## Risk Rating Standard

tachi uses the OWASP 3x3 Risk Rating Matrix. Each finding is assessed on two axes — Likelihood and Impact — each rated LOW, MEDIUM, or HIGH. The intersection determines the Risk Level.

### OWASP 3x3 Risk Matrix

|                    | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|--------------------|----------------|-------------------|-----------------|
| **HIGH Impact**    | Medium         | High              | Critical        |
| **MEDIUM Impact**  | Low            | Medium            | High            |
| **LOW Impact**     | Note           | Low               | Medium          |

## Scoring Scale

| Score | Meaning |
|-------|---------|
| 1 | Unacceptable — fails to meet the dimension's criteria |
| 2 | Below standard — significant gaps or issues |
| 3 | Acceptable — meets minimum requirements |
| 4 | Good — meets requirements with notable quality |
| 5 | Excellent — exceeds requirements, exemplary quality |

## Passing Threshold

**Minimum aggregate score**: 3

An output passes when the average score across all dimensions meets or exceeds this threshold. No individual dimension may score below 2 (floor).

---

## Likelihood Factors

The 8 OWASP likelihood factors used to assess the probability of a threat being exploited:

### Factor 1: Skill Level

**What it measures**: The technical skill required by the attacker to exploit this vulnerability.

| Score | Criteria |
|-------|----------|
| 1 | Security penetration tester or expert required |
| 2 | Advanced programmer or network administrator required |
| 3 | Skilled computer user with some technical knowledge |
| 4 | Minimal technical skills needed |
| 5 | No technical skills required — automated tools available |

### Factor 2: Motive

**What it measures**: How motivated the threat agent is to exploit this vulnerability.

| Score | Criteria |
|-------|----------|
| 1 | No reward or benefit from exploitation |
| 2 | Low or uncertain reward |
| 3 | Moderate reward possible |
| 4 | High reward likely |
| 5 | Extremely high reward — financial, reputational, or strategic |

### Factor 3: Opportunity

**What it measures**: The resources and access required to exploit this vulnerability.

| Score | Criteria |
|-------|----------|
| 1 | Full access to system internals required with special resources |
| 2 | Special access or significant resources required |
| 3 | Some access or resources required |
| 4 | Minimal access needed — publicly reachable attack surface |
| 5 | No special access needed — vulnerability is internet-facing |

### Factor 4: Size

**What it measures**: The size of the threat agent population capable of exploiting this vulnerability.

| Score | Criteria |
|-------|----------|
| 1 | Targeted — only specific individuals or nation-state actors |
| 2 | Small group with specialized knowledge |
| 3 | Moderate population with relevant skills |
| 4 | Large population — common attacker profile |
| 5 | Massive population — any internet user with a script |

### Factor 5: Ease of Discovery

**What it measures**: How easy it is for a threat agent to discover this vulnerability.

| Score | Criteria |
|-------|----------|
| 1 | Practically impossible — requires insider knowledge |
| 2 | Difficult — requires deep analysis or reverse engineering |
| 3 | Moderate — discoverable through careful testing |
| 4 | Easy — discoverable through basic scanning or observation |
| 5 | Automated tools can detect it — public scanners flag it |

### Factor 6: Ease of Exploit

**What it measures**: How easy it is to exploit the vulnerability once discovered.

| Score | Criteria |
|-------|----------|
| 1 | Theoretically possible but no known exploit exists |
| 2 | Difficult — custom exploit development required |
| 3 | Moderate — existing tools need customization |
| 4 | Easy — point-and-click exploit tools available |
| 5 | Automated — wormable or self-propagating exploit exists |

### Factor 7: Awareness

**What it measures**: How well-known the vulnerability class is among threat agents.

| Score | Criteria |
|-------|----------|
| 1 | Unknown — zero-day or novel attack class |
| 2 | Niche — known only in specialized research communities |
| 3 | Somewhat known — discussed in security publications |
| 4 | Well-known — covered in OWASP Top 10 or equivalent |
| 5 | Public knowledge — widely reported in mainstream media |

### Factor 8: Intrusion Detection

**What it measures**: How likely it is that exploitation will be detected by existing security controls.

| Score | Criteria |
|-------|----------|
| 1 | Active detection with automated response and alerting |
| 2 | Detection is logged and reviewed within hours |
| 3 | Detection is logged but reviewed periodically |
| 4 | Minimal logging — exploitation may go undetected for days |
| 5 | No detection capability — exploitation is completely silent |

---

## Impact Factors

The 8 OWASP impact factors used to assess the severity of a successful exploitation:

### Factor 1: Loss of Confidentiality

**What it measures**: The extent of data disclosure resulting from exploitation.

| Score | Criteria |
|-------|----------|
| 1 | Minimal non-sensitive data disclosed |
| 2 | Limited sensitive data disclosed to authorized parties |
| 3 | Significant sensitive data disclosed |
| 4 | Extensive critical data disclosed to unauthorized parties |
| 5 | Complete data breach — all data accessible to attacker |

### Factor 2: Loss of Integrity

**What it measures**: The extent of data corruption or unauthorized modification.

| Score | Criteria |
|-------|----------|
| 1 | Minimal data can be slightly modified — easily correctable |
| 2 | Limited data can be modified — detectable and reversible |
| 3 | Significant data modification possible |
| 4 | Extensive data corruption — integrity of critical records compromised |
| 5 | Complete integrity loss — attacker controls all data modifications |

### Factor 3: Loss of Availability

**What it measures**: The extent of service disruption resulting from exploitation.

| Score | Criteria |
|-------|----------|
| 1 | Minimal disruption — secondary services briefly affected |
| 2 | Limited disruption — primary services degraded temporarily |
| 3 | Significant disruption — primary services intermittently unavailable |
| 4 | Extensive outage — primary services down for hours |
| 5 | Complete outage — all services unavailable for extended period |

### Factor 4: Loss of Accountability

**What it measures**: The ability to trace actions back to the responsible party after exploitation.

| Score | Criteria |
|-------|----------|
| 1 | Full audit trail preserved — all actions traceable |
| 2 | Most actions traceable — minor gaps in audit trail |
| 3 | Partial accountability — some actions untraceable |
| 4 | Limited accountability — attacker actions largely anonymous |
| 5 | No accountability — complete repudiation possible |

### Factor 5: Financial Damage

**What it measures**: The financial impact of a successful exploitation.

| Score | Criteria |
|-------|----------|
| 1 | Negligible — less than the cost of fixing the vulnerability |
| 2 | Minor — below individual project budget impact |
| 3 | Moderate — significant project or department-level cost |
| 4 | Major — organizational-level financial impact |
| 5 | Catastrophic — threatens organizational viability |

### Factor 6: Reputation Damage

**What it measures**: The reputational impact of a successful exploitation.

| Score | Criteria |
|-------|----------|
| 1 | Negligible — no external visibility |
| 2 | Minor — limited negative coverage, quickly forgotten |
| 3 | Moderate — noticeable brand impact requiring response |
| 4 | Major — significant trust erosion with customers or partners |
| 5 | Catastrophic — permanent brand damage, loss of major accounts |

### Factor 7: Non-Compliance

**What it measures**: The regulatory or compliance impact of exploitation.

| Score | Criteria |
|-------|----------|
| 1 | No compliance implications |
| 2 | Minor policy violation — internal remediation sufficient |
| 3 | Moderate compliance gap — regulatory notification may be required |
| 4 | Significant violation — regulatory penalties or mandatory reporting |
| 5 | Critical non-compliance — license revocation, criminal liability |

### Factor 8: Privacy Violation

**What it measures**: The extent of personally identifiable information (PII) exposure.

| Score | Criteria |
|-------|----------|
| 1 | No PII exposed |
| 2 | Minimal PII — non-sensitive identifiers (public profiles) |
| 3 | Moderate PII — contact information or preferences |
| 4 | Sensitive PII — financial, health, or government identifiers |
| 5 | Complete PII breach — full identity exposure enabling fraud |
