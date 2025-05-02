""" Utility functions for SPARCd server """

import base64
import hashlib


def get_fernet_key_from_passcode(passcode: str) -> bytes:
    """ Returns a Fernet key based upon the passcode
    Arguments:
        passcode: the passcode to generate a key from
    Returns:
        Returns the bytes of the key
    """
    hashed_key = hashlib.sha256(passcode.encode('utf-8'))
    hashed_key_digest = hashed_key.digest()
    return base64.b64encode(hashed_key_digest)
