"""Encryption of archived objects.

Synthetic stub for the large-architecture fixture. It is never run.
"""

def seal(blob, key_id):
    key = key_service.data_key(key_id)
    nonce = random_bytes(12)
    return nonce + aead_encrypt(key, nonce, blob)
