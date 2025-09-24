""" Cryptography functions """

import base64
import hashlib
from typing import Optional

from cryptography.fernet import Fernet

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


def do_encrypt(passcode: str, plain: str) -> Optional[str]:
    """ Encrypts the plaintext string
    Argurments:
    	passcode: the passcode used to encrypt the plaintext
        plain: the string to convert
    Return:
        Returns the encrypted string. None is returned if the string is None
    Notes:
        The plain parameter is forced to a string before encryption (it should
        already be a string)
        The plain text is utf-8 encoded and the cipher is decoded to utf-8
    """
    if plain is None:
        return None
    engine = Fernet(passcode)
    return engine.encrypt(str(plain).encode('utf-8')).decode('utf-8')


def do_decrypt(passcode: str, cipher: str) -> Optional[str]:
    """ Decrypts the cipher to plain text
    Arguments:
    	passcode: the passcode used to encrypt the plaintext
        cipher: the encrypted string
    Return:
        Returns the plain text as a string. None is returned if the cipher is None
    Notes:
        The plain parameter is forced to a string before encryption (it should
        already be a string)
        The cipher is utf-8 encoded and the plain text is decoded to utf-8
    """
    if cipher is None:
        return None
    engine = Fernet(passcode)
    return engine.decrypt(cipher.encode('utf-8')).decode('utf-8')
