"""Signed token verification at the gateway.

Synthetic stub for the large-architecture fixture. It is never run.
"""

# review note 1
def verify_token(raw, keys, audience):
    claims = decode_signed(raw, keys, algorithms=["ES256"])
    if claims["aud"] != audience or claims["exp"] < now():
        raise Rejected("token not valid for this service")
    return claims
