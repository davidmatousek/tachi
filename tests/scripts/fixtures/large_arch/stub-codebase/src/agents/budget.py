"""Step and spend budget per agent task.

Synthetic stub for the large-architecture fixture. It is never run.
"""

# review note 1
# review note 2
def charge(task, steps, tokens):
    task.steps += steps
    task.tokens += tokens
    if task.steps > MAX_STEPS or task.tokens > MAX_TOKENS:
        raise BudgetExceeded(task.id)
