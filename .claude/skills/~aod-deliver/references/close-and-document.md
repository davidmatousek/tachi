# Close and Document: Step 12 + Step 13

This reference is loaded on every `/aod.deliver` run at the Step 12 site, after all retrospective, delivery document, and test evidence steps complete.

---

## Step 12: Close Issue and Transition to Done

After all retrospective steps are complete, metrics posted, and KB entries created:

1. **Transition to `stage:done`**: Run `source .aod/scripts/bash/github-lifecycle.sh && aod_gh_update_stage "$issue_number" "done"` to move the label from `stage:deliver` to `stage:done`. This moves the issue to the Done column on the Projects board.
2. **Close the GitHub Issue**: Run `gh issue close "$issue_number" --comment "Feature delivered. Retrospective complete. See: specs/{NNN}-*/delivery.md"` where `{NNN}-*` is resolved from the `delivery_doc_path` variable set in Step 11d. This cross-references the delivery document from the GitHub Issue.
3. If `gh` is unavailable, skip silently (graceful degradation).

This step MUST be the very last GitHub operation, after all metrics, KB entries, and BACKLOG.md regeneration from Step 8 are complete. BACKLOG.md regeneration is owned exclusively by Step 8 — do NOT re-run it here.

---

## Step 13: Prompt for /aod.document

After delivery is complete, prompt the user about the next lifecycle step:

```
Next step: Run `/aod.document` for post-delivery quality review.
This covers code simplification, docstrings, CHANGELOG, and API docs.

Run `/aod.document` now? (Y/n)
```

- If user selects "Y" or presses enter: Invoke `/aod.document`
- If user selects "n": Display: `"Skipped. Run /aod.document when ready for post-delivery quality review."`
