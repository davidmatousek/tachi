"""Token bucket per caller at the edge.

Synthetic stub for the large-architecture fixture. It is never run.
"""

# review note 1
def allow(caller, now):
    bucket = buckets.setdefault(caller, Bucket(rate=RATE, burst=BURST))
    bucket.refill(now)
    return bucket.take(1)
