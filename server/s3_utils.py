""" Utilities to help with S3 access """

import json
import os
import tempfile
from typing import Callable, Optional
from urllib.parse import urlparse

from cryptography.fernet import InvalidToken

from sparcd_utils import load_timed_info, save_timed_info
from s3_access import S3Connection, SPARCD_PREFIX

# Name of temporary collections file
TEMP_COLLECTION_FILE_NAME = SPARCD_PREFIX + 'coll.json'
# Temporary collections file timeout length
TIMEOUT_COLLECTIONS_FILE_SEC = 12 * 60 * 60


def make_s3_path(parts: tuple) -> str:
    """ Makes the parts into an S3 path
    Arguments:
        parts: the path particles
    Return:
        The parts joined into an S3 path
    """
    return "/".join([one_part.rstrip('/').rstrip('\\') for one_part in parts])


def web_to_s3_url(url: str, decrypt: Callable) -> str:
    """ Takes a web URL and converts it to something Minio can handle: converts
        http and https to port numbers
    Arguments:
        url: the URL to convert
    Return:
        Returns a URL that can be used to access minio
    Notes:
        If http or https is specified, any existing port number will be replaced.
        Any params, queries, and fragments are not kept
        The return url may be the same one passed in if it doesn't need changing.
    """
    # Check for encrypted URLs
    if not url.lower().startswith('http'):
        try:
            cur_url = decrypt(url)
            url = cur_url
        except InvalidToken:
            # Don't know what we have, just return it
            return url

    # It's encrypted but not an http(s) url
    if not url.lower().startswith('http'):
        return url

    parsed = urlparse(url)
    port = '80'
    if parsed.scheme.lower() == 'https':
        port = '443'

    return parsed.hostname + ':' + port


def load_sparcd_config(sparcd_file: str, timed_file: str, url: str, user: str, \
                                                                        fetch_password: Callable):
    """ Attempts to load the configuration information from either the timed_file or download it
        from S3. If downloaded from S3, it's saved as a timed file
    Arguments:
        sparcd_file: the name of the sparcd configuration file
        timed_file: the name of the timed file to attempt loading from
        url: the URL to the S3 store
        user: the S3 username
        fetch_password: returns the S3 password
    Return:
        Returns the loaded configuration information or None if there's a
        problem
    """
    config_file_path = os.path.join(tempfile.gettempdir(), timed_file)
    loaded_config = load_timed_info(config_file_path)
    if loaded_config:
        return loaded_config

    # Try to get the configuration information from S3
    loaded_config = S3Connection.get_configuration(sparcd_file, url, user, fetch_password())
    if loaded_config is None:
        return None

    try:
        loaded_config = json.loads(loaded_config)
        save_timed_info(config_file_path, loaded_config)
    except ValueError as ex:
        print(f'Invalid JSON from configuration file {sparcd_file}')
        print(ex)
        loaded_config = None

    return loaded_config


def load_timed_temp_colls(user: str, admin: bool) -> Optional[list]:
    """ Loads collection information from a temporary file
    Arguments:
        user: username to find permissions for and filter on
        admin: if set to True all the collections are returned
    Return:
        Returns the loaded collection data if valid, otherwise None is returned
    """
    coll_file_path = os.path.join(tempfile.gettempdir(), TEMP_COLLECTION_FILE_NAME)
    loaded_colls = load_timed_info(coll_file_path, TIMEOUT_COLLECTIONS_FILE_SEC)
    if loaded_colls is None:
        return None

    # Make sure we have a boolean value for admin and not Truthiness
    if not admin in [True, False]:
        admin = False

    # Get this user's permissions
    user_coll = []
    for one_coll in loaded_colls:
        user_has_permissions = False
        new_coll = one_coll
        new_coll['permissions'] = None
        if 'allPermissions' in one_coll and one_coll['allPermissions']:
            try:
                for one_perm in one_coll['allPermissions']:
                    if one_perm and 'usernameProperty' in one_perm and \
                                one_perm['usernameProperty'] == user:
                        new_coll['permissions'] = one_perm
                        user_has_permissions = True
                        break
            finally:
                pass

        # Only return collections that the user has permissions to
        if admin is True or user_has_permissions is True:
            user_coll.append(new_coll)

    # Return the collections
    return user_coll


def save_timed_temp_colls(colls: tuple) -> None:
    """ Attempts to save the collections to a temporary file on disk
    Arguments:
        colls: the collection information to save
    """
    # pylint: disable=broad-exception-caught
    coll_file_path = os.path.join(tempfile.gettempdir(), TEMP_COLLECTION_FILE_NAME)
    save_timed_info(coll_file_path, colls)
