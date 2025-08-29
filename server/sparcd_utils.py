""" Utility functions for SPARCd server """

import base64
import hashlib
import json
import math


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


def secure_user_settings(settings: dict) -> dict:
    """ Secures the user settings information
    Arguments:
        settings: the user settings
    Return:
        The secured user settings
    """
    if isinstance(settings, str):
        cur_settings = json.loads(settings)
    else:
        cur_settings = settings

    if 'email' in cur_settings and cur_settings['email'] and len(cur_settings['email']) > 2:
        if '@' in cur_settings['email']:
            first_part = cur_settings['email'][:cur_settings['email'].index('@')]
            second_part = cur_settings['email'][cur_settings['email'].index('@'):]
        else:
            first_part = cur_settings['email'][:max(1,math.floor(len(cur_settings['email']) / 2))]
            second_part = cur_settings['email'][max(1,math.ceil(len(cur_settings['email']) / 2)):]
        match len(first_part):
            case 1:
                pass
            case 2:
                first_part = first_part[:1] + '*'
            case 3:
                first_part = first_part[:2] + '*'
            case 4:
                first_part = first_part[:3] + '*'
            case _:
                first_part = first_part[:3] + '*'*(min(7, len(first_part)-3))

        cur_settings['email'] = first_part + second_part

    return cur_settings
