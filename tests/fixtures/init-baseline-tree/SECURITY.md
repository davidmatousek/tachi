# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Tachi, please report it through [GitHub's private vulnerability reporting](https://github.com/davidmatousek/tachi/security/advisories/new).

**Do not open a public issue for security vulnerabilities.**

### What to include

- Description of the vulnerability
- Steps to reproduce
- Affected components (agents, commands, schemas, templates)
- Potential impact

### What to expect

- **Acknowledgment** within 48 hours
- **Assessment** within 1 week
- **Fix or mitigation** timeline communicated after assessment
- **Credit** in the fix commit and release notes (unless you prefer anonymity)

## Scope

Tachi is a threat modeling toolkit that produces security analysis reports. Its security surface includes:

- **Agent prompt definitions** that could be manipulated to produce misleading threat assessments
- **Schema definitions** that validate input/output contracts
- **Template content** that shapes report generation
- **Configuration files** that reference external services or credentials

Tachi does not run application code, manage databases, or handle user authentication. Findings related to the threat models Tachi *produces* (false positives, missed threats) are quality issues, not security vulnerabilities -- please file those as regular issues.

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest release | Yes |
| Older releases | Best effort |
