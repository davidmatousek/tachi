### Upgrading: update your tachi clone, then re-run `install.sh`

Earlier install manifests left out three skills, `tachi-output-integrity`, `tachi-misinformation` and `tachi-human-trust-exploitation`, so those three threat agents ran without their detection references. They also left out the Affected Assets populator, `scripts/populate-affected-assets.py`. Re-installing adds all four. It also moves infographic image rendering to the current Gemini image models, `gemini-3-pro-image` and then `gemini-3.1-flash-image`. On the previous release, the infographic agent generated no images: its image request was rejected, and the models it named are now shut down.

`install.sh` copies from your local tachi clone, so update the clone first. Then re-run the installer from your project root and restart Claude Code:

```bash
git -C ~/Projects/tachi pull
~/Projects/tachi/scripts/install.sh
```

Use your clone's path if it lives elsewhere. If you install with `--version`, pull first anyway, so that the updated `install.sh` is the one that runs.

**Symlinked destinations now stop the install.** `install.sh` stops before writing anything when a destination inside your project is a symlink or passes through one, for example a linked `.claude`, `.claude/skills`, `docs` or `scripts` folder. Pass `--follow-symlinks` to install through such links: `install.sh` then names each resolved destination, copies into it, and never deletes through a link. Even with the flag, `install.sh` refuses broken, looping or wrong-type links, links nested inside an installed folder, and destinations inside the tachi source clone.

**Output changes:**

- **PDF recommendations.** Where the compensating-controls report gives a finding no recommendation, the PDF report now shows the threat model's mitigation, marked `Threat-model mitigation:`. A finding with neither shows `No recommendation available`.
- **Risk funnel.** The funnel now narrows by risk volume. The Risk Reduction figure on the funnel and on the baseball card is now computed from the compensating-controls report's per-finding rows, so it can differ from that report's summary.
- **Older report data.** Compiling an older or hand-built `report-data.typ` outside `/tachi.security-report` now stops with an instruction to regenerate it. `/tachi.security-report` regenerates the file on every run, so its own runs are unaffected.
