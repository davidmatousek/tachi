# Contributing to tachi

Thanks for being here. tachi exists to make threat modeling automatic, repeatable, and honest about its coverage. Every contribution — code, threat models, integrations, or just telling me how you're using it — makes the next release better.

## Start in Discussions

The front door is [GitHub Discussions](https://github.com/davidmatousek/tachi/discussions), not Issues.

| You want to... | Go here |
|---|---|
| Ask a question about installing or running tachi | [Q&A](https://github.com/davidmatousek/tachi/discussions/categories/q-a) |
| Propose a feature | [Feature Requests](https://github.com/davidmatousek/tachi/discussions/categories/feature-requests) |
| Workshop a rough idea or RFC | [Ideas & RFCs](https://github.com/davidmatousek/tachi/discussions/categories/ideas-rfcs) |
| Tell me how you're using tachi in production | [In the Wild](https://github.com/davidmatousek/tachi/discussions/categories/in-the-wild) |
| Share or review a threat model | [Threat Model Patterns](https://github.com/davidmatousek/tachi/discussions/categories/threat-model-patterns) |
| Publish an integration recipe | [Integrations](https://github.com/davidmatousek/tachi/discussions/categories/integrations) |
| Report a reproducible bug | [Issues](https://github.com/davidmatousek/tachi/issues) |
| Report a security vulnerability | [Private advisory](https://github.com/davidmatousek/tachi/security/advisories/new) — do not post publicly |

## How Feature Requests Become Work

Feature Requests sit at the intake of tachi's Discover phase. They are proposals, not commitments.

```
Discussion (Feature Request)  →  Issue (ICE-scored, Discover)  →  PRD (Define)  →  Build
   You propose                     I promote when ready            Triad reviews      Team ships
```

👍 reactions and concrete use cases in comments are the priority signal. When a request is ready to move, I promote it to an Issue with an ICE score and link back to the Discussion. The Discussion stays open for continued community input.

## Contributing Code

1. **Fork the repository** and clone your fork.
2. **Create a feature branch** named `NNN-descriptive-name` where `NNN` is the Issue number.
3. **Initialize the project** (first-time setup):
   ```bash
   make init
   ```
4. **Verify your environment** has the required prerequisites:
   ```bash
   make check
   ```
5. **Make your changes.** Follow existing patterns. Significant changes go through the ADLC Triad governance workflow (Product Manager + Architect + Team-Lead sign-off via PRD). tachi is built with the [Agentic Oriented Development Kit (AOD Kit)](https://github.com/davidmatousek/agentic-oriented-development-kit) — see there for how the Triad works.
6. **Run the test suite** before opening a PR:
   ```bash
   make test
   ```
7. **Commit using conventional commits:** `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`.
8. **Open a PR** against `main` using the PR template. Link the Issue with `Closes #NNN`.

## Contributing Threat Models and Integrations

Not every contribution is a code PR.

- **Threat model patterns** — redacted examples of models tachi produced, or models you built by hand that tachi should have produced. Post in [Threat Model Patterns](https://github.com/davidmatousek/tachi/discussions/categories/threat-model-patterns).
- **Integration recipes** — working CI configs, IDE wiring, SIEM/ticketing hooks. Post in [Integrations](https://github.com/davidmatousek/tachi/discussions/categories/integrations). If it's substantial, a PR adding a reference config to `examples/` is welcome.
- **In the Wild reports** — anonymized accounts of how tachi fits into your workflow. Post in [In the Wild](https://github.com/davidmatousek/tachi/discussions/categories/in-the-wild). These shape the roadmap more than feature requests do.

## What I Look For in a PR

- The change matches the scope of the linked Issue. No unrelated refactors bundled in.
- Tests exist for new behavior. Regression tests for bug fixes.
- Docs updated when behavior changes.
- No secrets, credentials, or PII in any committed file.
- Commits are atomic and follow the conventional format.

## Review Timeline

I read every Discussion and PR. First response is usually within a couple of days. Larger PRs that touch core pipeline or schemas take longer because they go through the Triad review.

If a week passes without a response, ping the thread. I may have missed it.

## Code of Conduct

All contributors follow the [Code of Conduct](CODE_OF_CONDUCT.md). Be kind. Threat modeling is a craft. People ask "obvious" questions because nobody taught them. Teach them.

## Security

Vulnerabilities in tachi itself go through the private advisory flow at https://github.com/davidmatousek/tachi/security/advisories/new. See [SECURITY.md](SECURITY.md) for details. Do not post vulnerabilities to Issues or Discussions.

## Questions About Contributing

Open a thread in [Q&A](https://github.com/davidmatousek/tachi/discussions/categories/q-a) and tag it `contributing`. I'll get to it.
