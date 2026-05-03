# Deployment

<!-- Rule file for tachi -->
<!-- This file is referenced from CLAUDE.md using @-syntax -->

## Overview

All deployments must be verified by the devops agent before execution to prevent data loss or service disruption.

---

## DevOps Agent Policy

**ALL deployments MUST go through the devops agent.**

**Never deploy without verification** - Mismatched targets can cause data loss or service disruption.

### Why This Matters:
- Prevents deploying to wrong environment (e.g., production instead of staging)
- Ensures environment-specific configurations are correct
- Validates infrastructure state before deployment
- Documents deployment verification in agent logs

---

## Verification Requirements

Before deploying:
1. **Invoke devops agent** (never run deploy commands directly)
2. **DevOps reads**: `docs/architecture/04_deployment_environments/{env}.md`
3. **DevOps reads**: `docs/devops/{01_Local|02_Staging|03_Production}/README.md`
4. **DevOps outputs** verification summary
5. **Only then** proceed with deployment

### Verification Checklist:
- Target environment matches intended deployment
- Environment variables are configured correctly
- Infrastructure dependencies are available
- Database migrations are compatible
- Rollback plan is documented
