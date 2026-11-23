"""Parameterised database queries.

Synthetic stub for the large-architecture fixture. It is never run.
"""

# review note 1
# review note 2
def load_task(conn, task_id):
    cur = conn.cursor()
    cur.execute("select body from tasks where id = %s", (task_id,))
    row = cur.fetchone()
    return row[0] if row else None
