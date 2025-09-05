#!/usr/bin/python3
"""This script contains the API for the SPARC'd server
"""

import concurrent.futures
import datetime
import hashlib
import io
import json
from multiprocessing import Lock, synchronize
import os
import re
import shutil
import sys
import tempfile
import threading
import time
import traceback
from typing import Optional
from urllib.parse import urlparse
import uuid
import zipfile
import dateutil.parser
import dateutil.tz
from PIL import Image

import requests
from cryptography.fernet import Fernet, InvalidToken
from minio import Minio
from minio.error import MinioException
from flask import Flask, render_template, request, Response, send_file, send_from_directory,\
                  url_for
from flask_cors import cross_origin

import image_utils
from text_formatters.results import Results
from text_formatters.coordinate_utils import DEFAULT_UTM_ZONE,deg2utm, deg2utm_code, utm2deg
import query_helpers
from sparcd_db import SPARCdDatabase
from sparcd_utils import get_fernet_key_from_passcode, secure_user_settings
from s3_access import S3Connection, DEPLOYMENT_CSV_FILE_NAME, MEDIA_CSV_FILE_NAME, \
                      OBSERVATIONS_CSV_FILE_NAME, CAMTRAP_FILE_NAMES, SPARCD_PREFIX

# Starting point for uploading files from server
RESOURCE_START_PATH = os.path.abspath(os.path.dirname(__file__))

# Allowed file extensions
ALLOWED_FILE_EXTENSIONS=['.png','.jpg','.jepg','.ico','.gif','.html','.css','.js','.woff2']

# Allowed image extensions
ALLOWED_IMAGE_EXTENSIONS=['.png','.jpg','.jpeg','.ico','.gif']

# Environment variable name for database
ENV_NAME_DB = 'SPARCD_DB'
# Environment variable name for passcode
ENV_NAME_PASSCODE = 'SPARCD_CODE'
# Environment variable name for session expiration timeout
ENV_NAME_SESSION_EXPIRE = 'SPARCD_SESSION_TIMEOUT'
# Default timeout in seconds
SESSION_EXPIRE_DEFAULT_SEC = 10 * 60 * 60
# Working database storage path
DEFAULT_DB_PATH = os.environ.get(ENV_NAME_DB,  None)
# Default timeout when requesting an image
DEFAULT_IMAGE_FETCH_TIMEOUT_SEC = 10.0
# Working passcode
CURRENT_PASSCODE = os.environ.get(ENV_NAME_PASSCODE, None)
# Working amount of time after last action before session is expired
SESSION_EXPIRE_SECONDS = os.environ.get(ENV_NAME_SESSION_EXPIRE, SESSION_EXPIRE_DEFAULT_SEC)
# Name of temporary collections file
TEMP_COLLECTION_FILE_NAME = SPARCD_PREFIX + 'coll.json'
# Name of temporary species file
TEMP_SPECIES_FILE_NAME = SPARCD_PREFIX + 'species.json'
# Name of temporary species file
TEMP_LOCATIONS_FILE_NAME = SPARCD_PREFIX + 'locations.json'
# Number of seconds to keep the temporary file around before it's invalid
TEMP_FILE_EXPIRE_SEC = 1 * 60 * 60
# Maximum number of times to try updating a temporary file
TEMP_FILE_MAX_WRITE_TRIES = 7
# Collection table timeout length
TIMEOUT_COLLECTIONS_SEC = 12 * 60 * 60
# Uploads table timeout length
TIMEOUT_UPLOADS_SEC = 3 * 60 * 60
# Timeout for query results on disk
QUERY_RESULTS_TIMEOUT_SEC = 24 * 60 * 60

# UI definitions for serving
DEFAULT_TEMPLATE_PAGE = 'index.html'

# Configuration file name for locations
CONF_LOCATIONS_FILE_NAME = 'locations.json'
# Configuration file name for species
CONF_SPECIES_FILE_NAME = 'species.json'

# Some CAMTRAP definitions
# TODO: Move camtrap definitions to their own file (from here and s3_access)
CAMTRAP_MEDIA_ID_IDX = 0
CAMTRAP_MEDIA_TYPE_IDX = 7
CAMTRAP_OBSERVATION_MEDIA_ID_IDX = 3
CAMTRAP_OBSERVATION_DATE_IDX = 4
CAMTRAP_OBSERVATION_SCIENTIFIC_NAME_IDX = 8
CAMTRAP_OBSERVATION_COUNT_IDX = 9
CAMTRAP_OBSERVATION_COUNT_NEW_IDX = 10
CAMTRAP_OBSERVATION_CONFIDENCE_INDEX = 18
CAMTRAP_OBSERVATION_COMMENT_IDX = 19

# TODO: Move to image_utils.py and add reference as needed
EXIFTOOL_CONFIG_TEXT = """%Image::ExifTool::UserDefined = (
    'Image::ExifTool::Exif::Main' => {
        0x0227 => {
            Name => 'SanimalFlag',
            Writable => 'int16u',
            WriteGroup => 'IFD2'
        },
        0x0228 => {
            Name => 'Species',
            Writable => 'string',
            WriteGroup => 'IFD2'
        },
        0x0229 => {
            Name => 'Location',
            Writable => 'string',
            WriteGroup => 'IFD2'
        },
    },
);
1; #end
"""

# List of known query form variable keys
KNOWN_QUERY_KEYS = ['collections','dayofweek','elevations','endDate','hour','locations',
                    'month','species','startDate','years']

# Don't run if we don't have a database or passcode
if not DEFAULT_DB_PATH or not os.path.exists(DEFAULT_DB_PATH):
    sys.exit(f'Database not found. Set the {ENV_NAME_DB} environment variable to the full path ' \
                'of a valid file')
if not CURRENT_PASSCODE:
    sys.exit(f'Passcode not found. Set the {ENV_NAME_PASSCODE} environment variable a strong ' \
                'passcode (password)')
WORKING_PASSCODE=get_fernet_key_from_passcode(CURRENT_PASSCODE)

# Initialize server
app = Flask(__name__)
#CORS(app, resources={r"/api/*": {"origins":["http://localhost:3000"]}}, supports_credentials=True)
# Secure cookie settings
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=600,
)
app.config.from_object(__name__)

# Intialize the database connection
DB = SPARCdDatabase(DEFAULT_DB_PATH)
DB.connect()
# TODO: clean up old tokens
del DB
DB = None
print(f'Using database at {DEFAULT_DB_PATH}', flush=True)
print(f'Temporary folder at {tempfile.gettempdir()}', flush=True)

def do_encrypt(plain: str) -> Optional[str]:
    """ Encrypts the plaintext string
    Argurments:
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
    engine = Fernet(WORKING_PASSCODE)
    return engine.encrypt(str(plain).encode('utf-8')).decode('utf-8')


def do_decrypt(cipher: str) -> Optional[str]:
    """ Decrypts the cipher to plain text
    Arguments:
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
    engine = Fernet(WORKING_PASSCODE)
    return engine.decrypt(cipher.encode('utf-8')).decode('utf-8')


def generate_hash(values: tuple) -> str:
    """ Generates a value-order-dependent hash from the tuple values and returns it
    Arguments:
        values: the values to get the hash value for
    Return:
        The hash value
    Note:
        All the values are converted into strings and joined for the hash making the
        hash value dependent upon the order of the values in the tuple
    """
    halg = hashlib.sha3_256()
    for one_val in values:
        halg.update(str(one_val).encode('utf-8'))

    return halg.hexdigest()


def web_to_s3_url(url: str) -> str:
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
            cur_url = do_decrypt(url)
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


def token_is_valid(token: str, client_ip: str, user_agent: str, db: SPARCdDatabase) -> bool:
    """Checks the database for a token and then checks the validity
    Arguments:
        token: the token to check
        client_ip: the client IP to check (use '*' to skip IP check)
        user_agent: the user agent value to check
        db: the database storing the token
    Returns:
        Returns True if the token is valid and False if not
    """
    # Get the user information using the token
    db.reconnect()
    login_info = db.get_token_user_info(token)
    #print('HACK:LOGININFO:',login_info["url"] if login_info else '<null>',flush=True)
    if login_info is not None:
        if login_info and 'settings' in login_info:
            login_info['settings'] = json.loads(login_info['settings'])
        if login_info and 'species' in login_info:
            login_info['species'] = json.loads(login_info['species'])

        # Is the session still good
        if abs(int(login_info['elapsed_sec'])) < SESSION_EXPIRE_SECONDS and \
           client_ip.rstrip('/') in (login_info['client_ip'].rstrip('/'), '*') and \
           login_info['user_agent'] == user_agent:
            # Update to the newest timestamp
            db.update_token_timestamp(token)
            return True, login_info

    return False, None


def get_upload_date(date_json: object) -> str:
    """ Returns the date string from an upload's date JSON
    Arguments:
        date_json: the JSON containing the 'date' and 'time' objects
    Returns:
        Returns the formatted date and time, or an empty string if a problem is found
    """
    return_str = ''

    if 'date' in date_json and date_json['date']:
        cur_date = date_json['date']
        if 'year' in cur_date and 'month' in cur_date and 'day' in cur_date:
            return_str += f'{cur_date["year"]:4d}-{cur_date["month"]:02d}-{cur_date["day"]:02d}'

    if 'time' in date_json and date_json['time']:
        cur_time = date_json['time']
        if 'hour' in cur_time and 'minute' in cur_time:
            return_str += f' at {cur_time["hour"]:02d}:{cur_time["minute"]:02d}'

    return return_str


def get_later_timestamp(cur_ts: object, new_ts: object) -> Optional[object]:
    """ Returns the later of the two dates
    Arguments:
        cur_ts: the date and time to compare against
        new_ts: the date and time to check if it's later
    Return:
        Returns the later date. If cur_ts is None, then new_ts is returned.
        If new_ts is None, then cur_ts is returned
    """
    if cur_ts is None:
        return new_ts
    if new_ts is None:
        return cur_ts

    if 'date' in cur_ts and 'date' in new_ts and cur_ts['date'] and new_ts['date']:
        if 'year' in cur_ts['date'] and 'year' in new_ts['date']:
            if int(cur_ts['date']['year']) < int(new_ts['date']['year']):
                return new_ts
        if 'month' in cur_ts['date'] and 'month' in new_ts['date']:
            if int(cur_ts['date']['month']) < int(new_ts['date']['month']):
                return new_ts
        if 'day' in cur_ts['date'] and 'day' in new_ts['date']:
            if int(cur_ts['date']['day']) < int(new_ts['date']['day']):
                return new_ts

    if 'time' in cur_ts and 'time' in new_ts and cur_ts['time'] and new_ts['time']:
        if 'hour' in cur_ts['time'] and 'hour' in new_ts['time']:
            if int(cur_ts['time']['hour']) < int(new_ts['time']['hour']):
                return new_ts
        if 'minute' in cur_ts['time'] and 'minute' in new_ts['time']:
            if int(cur_ts['time']['minute']) < int(new_ts['time']['minute']):
                return new_ts
        if 'second' in cur_ts['time'] and 'second' in new_ts['time']:
            if int(cur_ts['time']['second']) < int(new_ts['time']['second']):
                return new_ts
        if 'nano' in cur_ts['time'] and 'nano' in new_ts['time']:
            if int(cur_ts['time']['nano']) < int(new_ts['time']['nano']):
                return new_ts

    return cur_ts


def load_timed_temp_colls(user: str) -> Optional[list]:
    """ Loads collection information from a temporary file
    Arguments:
        user: username to find permissions for
    Return:
        Returns the loaded collection data if valid, otherwise None is returned
    """
    coll_file_path = os.path.join(tempfile.gettempdir(), TEMP_COLLECTION_FILE_NAME)
    loaded_colls = load_timed_info(coll_file_path, TIMEOUT_COLLECTIONS_SEC)
    if loaded_colls is None:
        return None

    # Get this user's permissions
    user_coll = []
    for one_coll in loaded_colls:
        new_coll = one_coll
        new_coll['permissions'] = None
        if 'allPermissions' in one_coll and one_coll['allPermissions']:
            try:
                for one_perm in one_coll['allPermissions']:
                    if one_perm and 'usernameProperty' in one_perm and \
                                one_perm['usernameProperty'] == user:
                        new_coll['permissions'] = one_perm
                        break
            finally:
                pass
        user_coll.append(new_coll)

    # Return the corrected collections
    return user_coll


def load_timed_info(load_path: str, timeout_sec: int=TEMP_FILE_EXPIRE_SEC):
    """ Loads the timed data from the specified file
    Arguments:
        load_path: the path to load data from
        timeout_sec: the timeout length of the file contents
    Return:
        The loaded data or None if a problem occurs
    """
    # pylint: disable=broad-exception-caught
    loaded_data = None

    if not os.path.exists(load_path):
        return None

    with open(load_path, 'r', encoding='utf-8') as infile:
        try:
            loaded_data = json.loads(infile.read())
        except json.JSONDecodeError as ex:
            infile.close()
            print(f'WARN: Timed file has invalid contents: {load_path}')
            print(ex)
            print('      Removing invalid file')
            try:
                os.unlink(load_path)
            except Exception as ex_2:
                print(f'Unable to remove bad timed file: {load_path}')
                print(ex_2)

            return None

    # Check if the contents are too old
    if not isinstance(loaded_data, dict) or 'timestamp' not in loaded_data or \
                                                    not loaded_data['timestamp']:
        print(f'WARN: Timed file has missing contents: {load_path}')
        print('      Removing invalid file')
        try:
            os.unlink(load_path)
        except Exception as ex:
            print(f'Unable to remove invalid timed file: {load_path}')
            print(ex)
        return None

    old_ts = dateutil.parser.isoparse(loaded_data['timestamp'])
    ts_diff = datetime.datetime.utcnow() - old_ts

    if ts_diff.total_seconds() > timeout_sec:
        print(f'INFO: Expired timed file {load_path}')
        try:
            os.unlink(load_path)
        except Exception as ex:
            print(f'Unable to remove expired timed file: {load_path}')
            print(ex)
        return None

    return loaded_data['data']


def save_timed_temp_colls(colls: tuple) -> None:
    """ Attempts to save the collections to a temporary file on disk
    Arguments:
        colls: the collection information to save
    """
    # pylint: disable=broad-exception-caught
    coll_file_path = os.path.join(tempfile.gettempdir(), TEMP_COLLECTION_FILE_NAME)
    save_timed_info(coll_file_path, colls)


def save_timed_info(save_path: str, data) -> None:
    """ Attempts to save information to a file with a timestamp
    Arguments:
        save_path: the path to the save file
        data: the data to save with a timestamp
    Note:
        If the file is locked, this function sleeps for a second until
        the max retries is reached
    """
    # pylint: disable=broad-exception-caught
    if os.path.exists(save_path):
        try:
            os.unlink(save_path)
        except Exception as ex:
            print(f'Unable to remove old temporaryfile: {save_path}')
            print(ex)
            print('Continuing to try updating the file')

    attempts = 0
    informed_exception = False
    save_info = {'timestamp':datetime.datetime.utcnow().isoformat(),
                 'data':data
                }
    while attempts < TEMP_FILE_MAX_WRITE_TRIES:
        try:
            with open(save_path, 'w', encoding='utf-8') as outfile:
                outfile.write(json.dumps(save_info))
            attempts = TEMP_FILE_MAX_WRITE_TRIES
        except Exception as ex:
            if not informed_exception:
                print(f'Unable to open temporary file for writing: {save_path}')
                print(ex)
                print(f'Will keep trying for up to {TEMP_FILE_MAX_WRITE_TRIES} times')
                informed_exception = True
                time.sleep(1)
            attempts = attempts + 1


def load_sparcd_config(sparcd_file: str, timed_file: str, url: str, user: str, password: str):
    """ Attempts to load the configuration information from either the timed_file or download it
        from S3. If downloaded from S3, it's saved as a timed file
    Arguments:
        sparcd_file: the name of the sparcd configuration file
        timed_file: the name of the timed file to attempt loading from
        url: the URL to the S3 store
        user: the S3 username
        password: the S3 password
    Return:
        Returns the loaded configuration information or None if there's a
        problem
    """
    config_file_path = os.path.join(tempfile.gettempdir(), timed_file)
    loaded_config = load_timed_info(config_file_path)
    if loaded_config:
        return loaded_config

    # Try to get the configuration information from S3
    loaded_config = S3Connection.get_configuration(sparcd_file, url, user, password)
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


def load_locations(s3_url: str, user_name: str, password: str) -> tuple:
    """ Loads locations and converts lat-lon to UTM
    Arguments:
        s3_url - the URL to the S3 instance
        user_name - the user's name for S3
        password: the user's password
    Return:
        Returns the locations along with the converted coordinates
    """
    cur_locations = load_sparcd_config(CONF_LOCATIONS_FILE_NAME, TEMP_LOCATIONS_FILE_NAME, s3_url, \
                                                                                user_name, password)
    if not cur_locations:
        return cur_locations

    for one_loc in cur_locations:
        if 'utm_code' not in one_loc or 'utm_x' not in one_loc or 'utm_y' not in one_loc:
            if 'latProperty' in one_loc and 'lngProperty' in one_loc:
                utm_x, utm_y = deg2utm(float(one_loc['latProperty']), float(one_loc['lngProperty']))
                one_loc['utm_code'] = ''.join([str(one_res) for one_res in \
                                                    deg2utm_code(float(one_loc['latProperty']), \
                                                                 float(one_loc['lngProperty']))
                                              ])
                one_loc['utm_x'] = round(utm_x, 2)
                one_loc['utm_y'] = round(utm_y, 2)

    return cur_locations


def filter_collections(db: SPARCdDatabase, cur_coll: tuple, s3_url: str, user_name: str, \
                       user_token: str, filters: tuple) -> tuple:
    """ Filters the collections in an efficient manner
    Arguments:
        db - connections to the current database
        cur_coll - the list of applicable collections
        s3_url - the URL to the S3 instance
        user_name - the user's name for S3
        user_token - the users security token
        filters - the filters to apply to the data
    Returns:
        Returns the filtered results
    """
    all_results = []
    s3_uploads = []

    # Load all the DB data first
    for one_coll in cur_coll:
        cur_bucket = one_coll['json']['bucketProperty']
        uploads_info = db.get_uploads(s3_url, cur_bucket, TIMEOUT_UPLOADS_SEC)
        if uploads_info is not None and uploads_info:
            uploads_info = [{'bucket':cur_bucket,       \
                             'name':one_upload['name'],                     \
                             'info':json.loads(one_upload['json'])}         \
                                    for one_upload in uploads_info]
        else:
            s3_uploads.append(cur_bucket)
            continue

        # Filter on current DB uploads
        if len(uploads_info) > 0:
            cur_results = query_helpers.filter_uploads(uploads_info, filters)
            if cur_results:
                all_results = all_results + cur_results


    # Load the S3 uploads in an aynchronous fashion
    if len(s3_uploads) > 0:
        user_secret = do_decrypt(db.get_password(user_token))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            cur_futures = {executor.submit(list_uploads_thread, do_decrypt(s3_url), user_name, \
                                                                        user_secret, cur_bucket):
                            cur_bucket for cur_bucket in s3_uploads}

            for future in concurrent.futures.as_completed(cur_futures):
                try:
                    uploads_results = future.result()
                    if 'uploads_info' in uploads_results and \
                                                        len(uploads_results['uploads_info']) > 0:
                        uploads_info = [{'bucket':uploads_results['bucket'],
                                         'name':one_upload['name'],
                                         'info':one_upload,
                                         'json':json.dumps(one_upload)
                                        } for one_upload in uploads_results['uploads_info']]
                        db.save_uploads(s3_url, uploads_results['bucket'], uploads_info)

                        # Filter on current DB uploads
                        if len(uploads_info) > 0:
                            cur_results = query_helpers.filter_uploads(uploads_info, filters)
                            if cur_results:
                                all_results = all_results + cur_results
                # pylint: disable=broad-exception-caught
                except Exception as ex:
                    print(f'Generated exception: {ex}', flush=True)
                    traceback.print_exception(ex)

    return all_results


def cleanup_old_queries(db: SPARCdDatabase, token: str) -> None:
    """ Cleans up old queries off the file system
    Arguments:
        db - connections to the current database
    """
    expired_queries = db.get_clear_queries(token)
    if expired_queries:
        for one_query_path in expired_queries:
            if os.path.exists(one_query_path):
                try:
                    os.unlink(one_query_path)
                # pylint: disable=broad-exception-caught
                except Exception as ex:
                    print(f'Unable to remove old query file: {one_query_path}')
                    print(ex)


def query_raw2csv(raw_data: tuple, settings: dict, mods: tuple=None) -> str:
    """ Returns the CSV of the specified raw query results
    Arguments:
        raw_data: the query data to convert
        settings: user settings
        mods: modifictions to make on the data based upon user settings
    """
    all_results = ''

    # Loop through any modifiers
    location_keys = ['locX', 'locY']
    elevation_keys = ['locElevation']
    timestamp_keys = 'date'
    if not mods is None:
        for one_mod in mods:
            if 'type' in one_mod:
                match one_mod['type']:
                    case 'hasLocations':
                        coord_format = settings['coordinatesDisplay'] if 'coordinatesDisplay' in \
                                                                        settings else 'LATLON'
                        if coord_format == 'UTM':
                            location_keys = ['utm_code', 'utm_x', 'utm_y']

                    case 'hasElevation':
                        measure_format = settings['measurementFormat'] if 'measurementFormat' in \
                                                                        settings else 'meters'
                        if measure_format == 'feet':
                            elevation_keys = ['locElevationFeet']

                    case 'date':
                        date_format = settings['dateFormat'] if 'dateFormat' in settings else 'MDY'
                        time_format = settings['timeFormat'] if 'timeFormat' in settings else '24'

                        timestamp_keys = {'date': 'date'+date_format, 'time': 'time'+time_format}


    for one_row in raw_data:
        # Build up the row based upon modifications
        cur_row = [one_row['image']]

        if isinstance(timestamp_keys, str):
            cur_row.append('"' + one_row['date'] + '"')
        else:
            cur_row.append('"' + one_row[timestamp_keys['date']] + ' ' + \
                                            one_row[timestamp_keys['time']] + '"')

        cur_row.append(one_row['locName'])
        cur_row.append(one_row['locId'])
        for one_key in location_keys:
            cur_row.append(str(one_row[one_key]))
        for one_key in elevation_keys:
            cur_row.append(re.sub(r"[^\d\.]", "", str(one_row[one_key])))

        cur_idx = 1
        while True:
            if 'scientific' + str(cur_idx) in one_row and 'common' + str(cur_idx) in one_row and \
                    'count' + str(cur_idx) in one_row:
                cur_row.append(one_row['scientific' + str(cur_idx)])
                cur_row.append(one_row['common' + str(cur_idx)])
                cur_row.append(str(one_row['count' + str(cur_idx)]))
            else:
                break

            cur_idx += 1

        all_results += ','.join(cur_row) + '\n'

    return all_results


def query_location2csv(location_data: tuple, settings: dict, mods: dict=None) -> str:
    """ Returns the CSV of the specified location query results
    Arguments:
        location_data: the location data to convert
        settings: user settings
        mods: modifictions to make on the data based upon user settings
    """
    all_results = ''


    # Loop through any modifiers
    location_keys = ['locX', 'locY']
    elevation_keys = ['locElevation']
    if not mods is None:
        for one_mod in mods:
            if 'type' in one_mod:
                match one_mod['type']:
                    case 'hasLocations':
                        coord_format = settings['coordinatesDisplay'] if 'coordinatesDisplay' in \
                                                                        settings else 'LATLON'
                        if coord_format == 'UTM':
                            location_keys = ['utm_code', 'utm_x', 'utm_y']
                        break

                    case 'hasElevation':
                        measure_format = settings['measurementFormat'] if 'measurementFormat' in \
                                                                        settings else 'meters'

                        if measure_format == 'feet':
                            elevation_keys = ['locElevationFeet']
                        break

    for one_row in location_data:
        cur_row = [one_row['name'], one_row['id']]

        for one_key in location_keys:
            cur_row.append(str(one_row[one_key]))
        for one_key in elevation_keys:
            cur_row.append(re.sub(r"[^\d\.]", "", str(one_row[one_key])))

        all_results += ','.join(cur_row) + '\n'

    return all_results


def query_species2csv(species_data: tuple, settings: dict, mods: dict=None) -> str:
    """ Returns the CSV of the specified species query results
    Arguments:
        species_data: the species data to convert
        settings: user settings
        mods: modifictions to make on the data based upon user settings
    """
    # pylint: disable=unused-argument
    all_results = ''
    for one_row in species_data:
        all_results += ','.join([one_row['common'], one_row['scientific']]) + '\n'

    return all_results


def query_allpictures2csv(allpictures_data: tuple, settings: dict, mods: dict = None) -> str:
    """ Returns the CSV of the specified Sanderson all pictures query results
    Arguments:
        allpictures_data: the all pictures data to convert
        settings: user settings
        mods: modifictions to make on the data based upon user settings
    """
    # pylint: disable=unused-argument
    all_results = ''
    for one_row in allpictures_data:
        all_results += ','.join([one_row['location'], one_row['species'], one_row['image']]) + '\n'

    return all_results


def list_uploads_thread(s3_url: str, user_name: str, user_secret: str, bucket: str) -> object:
    """ Used to load upload information from an S3 instance
    Arguments:
        s3_url - the URL to connect to
        user_name - the name of the user to connect with
        user_secret - the secret used to connect
        bucket - the bucket to look in
    Return:
        Returns an object with the loaded uploads
    """
    uploads_info = S3Connection.list_uploads(s3_url, \
                                        user_name, \
                                        user_secret, \
                                        bucket)

    return {'bucket': bucket, 'uploads_info': uploads_info}


def zip_downloaded_files(write_fd: int, file_list: list, \
                            files_lock: synchronize.Lock, done_sem: threading.Semaphore, \
                            save_folder: str) -> None:
    """ Compresses the downloaded files and streams the data into the data pipe
    Arguments:
        write_pipe: the pipe to use for the zipping output
        file_list: the list of files to compress
        files_lock: the lock access to the list of files
        done_sem: the lock indicating the downloads have completed
        save_folder: the base folder where the downloads are being saved. Use for relative
                    path names
    """
    if not save_folder.endswith(os.path.sep):
        save_folder += os.path.sep

    with os.fdopen(write_fd, 'wb') as zip_out:
        with zipfile.ZipFile(zip_out, mode='w', compression=zipfile.ZIP_BZIP2, \
                                                                    compresslevel=2) as compressed:
            lock_acquired = False
            while True:
                next_file = None

                # Only get the lock one time
                if not lock_acquired:
                    files_lock.acquire()
                    lock_acquired = True

                # Get the next file to work on and relase the lock if we don't have too
                # many files queued up already
                try:
                    # Check if all the files have been downloaded
                    if len(file_list) == 0:
                        # Release the lock on file list
                        if lock_acquired:
                            files_lock.release()
                            lock_acquired = False

                        # Check if we hit a download lull or we're done
                        if done_sem.acquire(blocking=False, timeout=None):
                            done_sem.release()
                            break

                        # Not done yet, wait for a little
                        time.sleep(0.5)
                        continue

                    # Grab the next file
                    next_file, _, _ = file_list.pop(0) # unused next_bucket, next_s3_path
                finally:
                    # We hold onto the list lock if there's a bunch of files downloaded already.
                    # This will allow us to catch up
                    if len(file_list) < 200 and lock_acquired:
                        files_lock.release()
                        lock_acquired = False

                if not next_file:
                    continue

                compressed.write(next_file, next_file[len(save_folder):])

                os.unlink(next_file)

    # Remove the downloading folder
    shutil.rmtree(save_folder)


def gzip_cb(info: tuple, bucket: str, s3_path: str, local_path: str):
    """ Handles the downloaded file as part of the GZIP creation
    Arguments:
        info: additional information from the calling function
        bucket: the bucket downloaded from
        s3_path: the S3 path of the downloaded file
        local_path: where the data is locally
    """
    # Check for being done and indicate that we're done
    if bucket is None:
        finish_lock = info[2]
        finish_lock.release()

    # Add our file information to the list
    file_list = info[0]
    list_lock = info[1]

    # Add our file to the list
    list_lock.acquire()
    try:
        file_list.append((local_path, bucket, s3_path))
    finally:
        list_lock.release()


def get_zip_dl_info(file_str: str) -> tuple:
    """ Returns the file information for downloading purposes
    Arguments:
        file_str: the file path information to split apart
    Return:
        A tuple containing the bucket, S3 path, and target file
    """
    bucket, s3_path = file_str.split(':')
    if '/Uploads/' in s3_path:
        target_path = s3_path[s3_path.index('/Uploads/')+len('/Uploads/'):]
    else:
        target_path = s3_path

    return bucket, s3_path, target_path


def generate_zip(url: str, user: str, password: str, s3_files: tuple, \
                                        write_fd: int, \
                                        done_sem: threading.Semaphore) -> None:
    """ Creates a gz file containing the images
    Arguments:
        url: the URL to the S3 instance
        user: the S3 user name
        password: the S3 password
        s3_files: the list of files to compress in the format of bucket:path
        write_pipe: the pipe to write the ZIP data to
        done_sem: the lock indicating the last file has been downloaded
    Returns:
        The contents of the compressed files
    """
    # This folder is removed in zip_downloaded_files
    save_folder = tempfile.mkdtemp(prefix=SPARCD_PREFIX + 'gz_')
    downloaded_files = []
    download_files_lock = Lock()

    zip_thread = threading.Thread(target=zip_downloaded_files,
                          args=(write_fd, downloaded_files, download_files_lock, done_sem, \
                                                                                        save_folder)
                         )
    zip_thread.start()

    S3Connection.download_images_cb(url, user, password,
                                        [get_zip_dl_info(one_file) for one_file in s3_files],
                                        save_folder, gzip_cb,
                                        (downloaded_files, download_files_lock, done_sem))


def get_location_info(location_id: str, all_locations: tuple) -> dict:
    """ Gets the location associated with the ID. Will return a unknown location if ID is not found
    Arguments:
        location_id: the ID of the location to use
        all_locations: the list of available locations
    Return:
        The location information
    """
    our_location = [one_loc for one_loc in all_locations if one_loc['idProperty'] == location_id]
    if our_location:
        our_location = our_location[0]
    else:
        our_location = {'nameProperty':'Unknown', 'idProperty':'unknown',
                                    'latProperty':0.0, 'lngProperty':0.0, 'elevationProperty':0.0,
                                    'utm_code':DEFAULT_UTM_ZONE, 'utm_x':0.0, 'utm_y':0.0}

    return our_location


def create_deployment_data(collection_id: str, location: dict) -> tuple:
    """ Returns the tuple containing the deployment data
    Arguments:
        collection_id: the ID of the collection (used for unique names)
        location: the information of the location to use
    Return:
        A tuple containing the deployment data
    """

    return [ collection_id + ':' + location['idProperty'],# Deployment id
             location['idProperty'],                 # Location ID
             location['nameProperty'],               # Location name
             str(location['latProperty']),           # Location latitude
             str(location['lngProperty']),           # Location longitude
             "0",                                    # Coordinate uncertainty
             '',                                     # Start timestamp
             '',                                     # End timestamp
             '',                                     # Setup ID
             '',                                     # Camera ID
             '',                                     # Camera model
             "0",                                    # Camera interval
             str(location['elevationProperty']),     # Camera height (elevation)
             "0.0",                                  # Camera tilt
             "0",                                    # Camera heading
             'TRUE',                                 # Timestamp issues
             '',                                     # Bait use
             '',                                     # Session
             '',                                     # Array
             '',                                     # Feature type
             '',                                     # Habitat
             '',                                     # Tags
             '',                                     # Notes
            ]


def create_media_data(collection_id: str, location_id: str, s3_base_path: str, \
                                                                    all_files: tuple) -> tuple:
    """ Returns the tuple containing the media data
    Arguments:
        collection_id: the ID of the collection (used for unique names)
        location_id: the ID of the location to use
        s3_base_path: the base server path of the files
        all_files: the list of files
    Return:
        A tuple containing tuples of the the media data
    """
    return [
            ('/'.join((s3_base_path,one_file)),     # Media ID
            f'{collection_id}:{location_id}',       # Deployment ID
            '/'.join((s3_base_path,one_file)),      # Sequence ID
            '',                                     # Capture method
            '',                                     # Timestamp
            '/'.join((s3_base_path,one_file)),      # File path
            os.path.basename(one_file),             # File name
            '',                                     # File media type
            '',                                     # EXIF data
            'FALSE',                                # Favorite
            ''                                      # Comments
            )
        for one_file in all_files
        ]


def create_observation_data(collection_id: str, location_id: str, s3_base_path: str, \
                                                                    all_files: tuple) -> tuple:
    """ Returns the tuple containing the observation data
    Arguments:
        collection_id: the ID of the collection (used for unique names)
        location_id: the ID of the location to use
        s3_base_path: the base server path of the files
        all_files: the list of files
    Return:
        A tuple containing tuples of the the observation data
    """
    return [
            ('',                                    # Observation ID
            f'{collection_id}:{location_id}',       # Deployment ID
            '',                                     # Sequence ID
            '/'.join((s3_base_path,one_file)),      # Media ID
            '',                                     # Timestamp
            '',                                     # Observation type
            'FALSE',                                # Camera setup
            '',                                     # Taxon ID
            '',                                     # Scientific name
            '0',                                    # Count
            '0',                                    # Count new species
            '',                                     # Life stage
            '',                                     # Sex
            '',                                     # Behaviour
            '',                                     # Individual ID
            '',                                     # Classification method
            '',                                     # Classified by
            '',                                     # Classification timestmp
            '1.0000',                               # Classification confidence
            '',                                     # Comments
            )
        for one_file in all_files
        ]


def save_camtrap_file(filename: str, data: object) -> bool:
    """ Saves the data to the specified name
    Arguments:
        filename: the name of the file to save to
        data: the data to save
    Return:
        Returns True is the data is saved into the file
    """
    # TODO: make this use CSV instance
    save_path = os.path.join(tempfile.gettempdir(),SPARCD_PREFIX+filename)
    with open(save_path, 'w', encoding='utf-8') as ofile:
        ofile.write(json.dumps(data))

    return True


def load_camtrap_media(url: str, user: str, token: str, db: SPARCdDatabase, bucket: str, \
                                                                    s3_path: str) -> Optional[dict]:
    """ Returns the media camtrap information with the file names as the keys (the filenames are the
        portion of media path after the S3 path)
    Arguments:
        url: the URL to the S3 instance
        user: the S3 user name
        token: the session token
        db: the active database
        bucket: the bucket downloaded from
        s3_path: the S3 path of the CAMTRAP CSV file
    Return:
        A dict with file names as the keys and its row as the value
    Notes:
        e.g.: assuming the S3 path is "/my/s3/path" and the media path is
        "/my/s3/path/to/media.jpg", the key would be "to/media.jpg"
    """
    loaded_media = load_camtrap_info(url, user, token, db, bucket, s3_path, MEDIA_CSV_FILE_NAME)
    if loaded_media:
        s3_path_len = len(s3_path) + 1 # We add one to remove the separator
        return {one_row[CAMTRAP_MEDIA_ID_IDX][s3_path_len:]: one_row for one_row in loaded_media}

    return None

def load_camtrap_observations(url: str, user: str, token: str, db: SPARCdDatabase, bucket: str, \
                                                                    s3_path: str) -> Optional[dict]:
    """ Returns the observations camtrap information with the file names as the keys (the filenames
        are the portion of observations path after the S3 path)
    Arguments:
        url: the URL to the S3 instance
        user: the S3 user name
        token: the session token
        db: the active database
        bucket: the bucket downloaded from
        s3_path: the S3 path of the CAMTRAP CSV file
    Return:
        A dict with file names as the keys and its rows as the value
    Notes:
        e.g.: assuming the S3 path is "/my/s3/path" and the media path is
        "/my/s3/path/to/media.jpg", the key would be "to/media.jpg"
    """
    loaded_obs = load_camtrap_info(url, user, token, db, bucket, s3_path,
                                                                        OBSERVATIONS_CSV_FILE_NAME)

    return_obs = None
    if loaded_obs:
        return_obs = {}
        s3_path_len = len(s3_path) + 1 # We add one to remove the separator
        for one_row in loaded_obs:
            filename = one_row[CAMTRAP_OBSERVATION_MEDIA_ID_IDX][s3_path_len:]
            if filename not in return_obs:
                return_obs[filename] = []
            return_obs[filename].append(one_row)

    return return_obs


def load_camtrap_info(url: str, user: str, token: str, db: SPARCdDatabase, bucket: str, \
                                                    s3_path: str, filename: str) -> Optional[tuple]:
    """ Returns the contents of the CAMTRAP CSV file as a tuple containing row tuples
    Arguments:
        url: the URL to the S3 instance
        user: the S3 user name
        token: the session token
        bucket: the bucket downloaded from
        db: the active database
        s3_path: the S3 path of the CAMTRAP CSV file
        filename: the name of the file to load
    Return:
        A tuple containing the rows of the file as tuples
    Notes:
        Looks on the local file system to see if the contents are available. If not found there,
        the file is downloaded from S3
        See also: save_camtrap_file() which creates files with the same name
    """
    # First try the local file system
    load_path = os.path.join(tempfile.gettempdir(),
                    SPARCD_PREFIX+bucket+'_'+os.path.basename(s3_path)+'_'+filename)
    if os.path.exists(load_path):
        with open(load_path, 'r', encoding='utf-8') as infile:
            try:
                return json.loads(infile.read())
            except json.JSONDecodeError as ex:
                infile.close()
                print(f'Unable to load CAMTRAP file {filename} locally: {load_path}',flush=True)
                print(ex, flush=True)

    # Try S3 since we don't have the data
    return S3Connection.get_camtrap_file(url, user, do_decrypt(db.get_password(token)),
                                                        bucket, '/'.join((s3_path, filename)))

def zip_iterator(read_fd: int):
    """ Reads the data in the pipe and yields it
    Arguments:
        read_conn: the reading pipe to read from
    """
    with os.fdopen(read_fd, 'rb') as zip_in:
        while True:
            data = zip_in.read(1024)
            if not data:
                break
            yield data

def normalize_upload(upload_entry: dict) -> dict:
    """ Normalizes an S3 upload
    Arguments:
        upload_entry: the upload to normalize
    Return:
        The normalized upload
    """
    return {'name': upload_entry['info']['uploadUser'] + ' on ' + \
                                            get_upload_date(upload_entry['info']['uploadDate']),
            'description': upload_entry['info']['description'],
            'imagesCount': upload_entry['info']['imageCount'],
            'imagesWithSpeciesCount': upload_entry['info']['imagesWithSpecies'],
            'location': upload_entry['location'],
            'edits': upload_entry['info']['editComments'],
            'key': upload_entry['key'],
            'date': upload_entry['info']['uploadDate'],
            'folders': upload_entry['uploaded_folders']
          }

def normalize_collection(coll: dict) -> dict:
    """ Takes a collection from the S3 instance and normalizes the data for the website
    Arguments:
        coll: the collection to normalize
    Return:
        The normalized collection
    """
    cur_col = { 'name': coll['nameProperty'],
                'bucket': coll['bucket'],
                'organization': coll['organizationProperty'],
                'email': coll['contactInfoProperty'],
                'description': coll['descriptionProperty'],
                'id': coll['idProperty'],
                'permissions': coll['permissions'],
                'allPermissions': coll['all_permissions'],
                'uploads': []
              }
    cur_uploads = []
    last_upload_date = None
    for one_upload in coll['uploads']:
        last_upload_date = get_later_timestamp(last_upload_date, \
                                                            one_upload['info']['uploadDate'])
        cur_uploads.append(normalize_upload(one_upload))

    cur_col['uploads'] = cur_uploads
    cur_col['last_upload_ts'] = last_upload_date
    return cur_col


def get_sandbox_collections(url: str, user: str, password: str, items: tuple, \
                                                            all_collections: tuple=None) -> tuple:
    """ Returns the sandbox information as collection information
    Arguments:
        url: the URL to the S3 instance
        user: the S3 user name
        password: the S3 password
        items: the sandbox items as returned by the database
        all_collections: the list of known collections
    Return:
        Returns the sandbox entries in collection format
    """
    coll_uploads = {}
    return_info = []

    # Get information on all the items
    for one_item in items:
        add_collection = False
        cur_upload = None
        s3_upload = False

        bucket = one_item['bucket']
        if bucket not in coll_uploads:
            coll_uploads[bucket] = {'s3_collection':False, 'uploads':[]}

        # Try to see if we've added the collection to the list already
        found = [one_info for one_info in return_info if one_info['bucket'] == bucket]
        if found:
            found = found[0]

            # Try to see if we can find the upload
            if 'uploads' in found:
                found_uploads = [one_upload for one_upload in found['uploads'] \
                                            if one_item['s3_path'].endswith(one_upload['key']) ]
                if len(found_uploads) > 0:
                    cur_upload = found_uploads[0]
        else:
            # Try to find the collection in the list of collections, otherwise fetch it
            add_collection = True
            if all_collections:
                found = [one_col for one_col in all_collections if one_col['bucket'] == bucket]
                if found:
                    # Save the found collection and look for the upload
                    found = found[0]

                    found_uploads = [one_upload for one_upload in found['uploads'] \
                                            if one_item['s3_path'].endswith(one_upload['key']) ]
                    if len(found_uploads) > 0:
                        cur_upload = found_uploads[0]
            else:
                found = S3Connection.get_collection_info(url, user, password, bucket,
                                                                            one_item['s3_path'])
                if found:
                    # Indicate we've downloaded collection from S3 and look for the upload
                    coll_uploads[bucket]['s3_collection'] = True

                    found_uploads = [one_upload for one_upload in found['uploads'] \
                                            if one_item['s3_path'] == one_upload['path'] ]
                    if len(found_uploads) > 0:
                        cur_upload = found['uploads'][0]
                        s3_upload = True

        if not found:
            print(f'ERROR: Unable to find collection bucket {bucket}. Continuing')
            continue

        if cur_upload is None:
            cur_upload = S3Connection.get_upload_info(url, user, password, bucket,
                                                                                one_item['s3_path'])
            if cur_upload is None:
                print(f'ERROR: Unable to retrieve upload for bucket {bucket}: ' \
                                                                f'Path: "{one_item['s3_path']}"')
                continue

            s3_upload = True

        # Check if we need to normalize the upload now
        if s3_upload is True and coll_uploads[bucket]['s3_collection'] is False:
            cur_upload = normalize_upload(cur_upload)
            if 'complete' in one_item:
                cur_upload['uploadCompleted'] = one_item['complete']
            coll_uploads[bucket]['uploads'].append(cur_upload)
        else:
            if 'complete' in one_item:
                cur_upload['uploadCompleted'] = one_item['complete']
            coll_uploads[bucket]['uploads'].append(cur_upload)

        if add_collection is True:
            return_info.append(found)

    # Assign the uploads and normalize any return information that's not done already
    for idx, one_return in enumerate(return_info):
        one_return['uploads'] = coll_uploads[one_return['bucket']]['uploads']
        if coll_uploads[one_return['bucket']]['s3_collection'] is True:
            return_info[idx] = normalize_collection(one_return)

    # Return out result
    return return_info


def update_admin_locations(url: str, user: str, password: str, changes: dict) -> bool:
    """ Updates the master list of locations with the changes under the
        'locations' key
    Arguments:
        url: the URL to the S3 instance
        user: the S3 user name
        password: the S3 password
        changes: the list of changes for locations
    Return:
        Returns True unless a problem is found
    """
    # Easy case where there's no changes
    if 'locations' not in changes or not changes['locations']:
        return True

    # Try to get the configuration information from S3
    all_locs = S3Connection.get_configuration(CONF_LOCATIONS_FILE_NAME, url, user, password)
    if all_locs is None:
        return False
    all_locs = json.loads(all_locs)

    all_locs = {generate_hash((one_loc['idProperty'], one_loc['latProperty'],
                                one_loc['lngProperty']))
                    : one_loc
                for one_loc in all_locs}

    for one_change in changes['locations']:
        loc_id = one_change[changes['loc_id']]
        loc_old_lat = one_change[changes['loc_old_lat']]
        loc_old_lon = one_change[changes['loc_old_lng']]

        # Update the entry if we have it, otherwise add it
        cur_key = generate_hash((loc_id, loc_old_lat, loc_old_lon))
        if cur_key in all_locs:
            cur_loc = all_locs[cur_key]
            cur_loc['nameProperty'] = one_change[changes['loc_name']]
            cur_loc['latProperty'] = one_change[changes['loc_new_lat']]
            cur_loc['lngProperty'] = one_change[changes['loc_new_lng']]
            cur_loc['elevationProperty'] = one_change[changes['loc_elevation']]
            if 'activeProperty' in cur_loc:
                cur_loc['activeProperty'] = one_change[changes['loc_active']]
            elif one_change[changes['loc_active']] == 1:
                cur_loc['activeProperty'] = True
        else:
            all_locs[cur_key] = {
                                    'idProperty': one_change[changes['loc_id']],
                                    'nameProperty': one_change[changes['loc_name']],
                                    'latProperty': one_change[changes['loc_new_lat']],
                                    'lngProperty': one_change[changes['loc_new_lng']],
                                    'elevationProperty': one_change[changes['loc_elevation']],
                                    'activeProperty': one_change[changes['loc_active']] == 1
                                }

    all_locs = tuple(all_locs.values())

# HACK
#    with open('x.json','w', encoding='utf-8') as ofile:
#        json.dump(all_locs, ofile, indent=4)
# HACK

    # Save to S3 and the local file system
    S3Connection.put_configuration(CONF_LOCATIONS_FILE_NAME, json.dumps(all_locs, indent=4),
                                    url, user, password)


    config_file_path = os.path.join(tempfile.gettempdir(), TEMP_LOCATIONS_FILE_NAME)
    save_timed_info(config_file_path, all_locs)

    return True


def update_admin_species(url: str, user: str, password: str, changes: dict) -> bool:
    """ Updates the master list of species with the changes under the
        'species' key
    Arguments:
        url: the URL to the S3 instance
        user: the S3 user name
        password: the S3 password
        changes: the list of changes for species
    Return:
        Returns True unless a problem is found
    """
    # Easy case where there's no changes
    if 'species' not in changes or not changes['species']:
        return True

    # Try to get the configuration information from S3
    all_species = S3Connection.get_configuration(CONF_SPECIES_FILE_NAME, url, user, password)
    if all_species is None:
        return False
    all_species = json.loads(all_species)

    all_species = {one_species['scientificName']: one_species for one_species in all_species}

    for one_change in changes['species']:

        # Update the entry if we have it, otherwise add it
        cur_key = one_change[changes['sp_old_scientific']]
        if cur_key in all_species:
            cur_species = all_species[cur_key]
            cur_species['name'] = one_change[changes['sp_name']]
            cur_species['scientificName'] = one_change[changes['sp_new_scientific']]
            cur_species['speciesIconURL'] = one_change[changes['sp_icon_url']]
            cur_species['keyBinding'] = one_change[changes['sp_keybind']] if \
                                                        one_change[changes['sp_keybind']] else None
        else:
            all_species[cur_key] = {
                                    'name': one_change[changes['sp_name']],
                                    'scientificName': one_change[changes['sp_new_scientific']],
                                    'speciesIconURL': one_change[changes['sp_icon_url']],
                                    'keyBinding': one_change[changes['sp_keybind']],
                                }

    all_species = tuple(all_species.values())

# HACK
#    with open('y.json','w', encoding='utf-8') as ofile:
#        json.dump(all_species, ofile, indent=4)
# HACK

    # Save to S3 and the local file system
    S3Connection.put_configuration(CONF_SPECIES_FILE_NAME, json.dumps(all_species, indent=4),
                                    url, user, password)

    config_file_path = os.path.join(tempfile.gettempdir(), TEMP_SPECIES_FILE_NAME)
    save_timed_info(config_file_path, all_species)

    return True


def update_image_file_exif(file_path: str, loc_id: str=None, loc_name: str=None, \
                                            loc_ele: float=None, loc_lat: float=None, \
                                            loc_lon: float=None, species_data: tuple=None) -> bool:
    """ Updates the image file with location exif information
    Arguments:
        file_path: the path to the file to modify
        loc_id: the location id
        loc_name: the location name
        loc_ele: the location elevation
        loc_lat: the location latitude
        loc_lon: the location longitude
        species_data: a tuple containing dicts of each species' common and scientific names, and
                      count
    Return:
        Returns whether or not the file was successfully updated
    """
    exif_location_data = None
    if loc_id and loc_name and loc_ele is not None:
        exif_location_data = ",".join((loc_name, loc_id, str(loc_lat), str(loc_lon), str(loc_ele)))

    exif_species_data = None
    if species_data is not None:
        print('HACK: $$$$ SPECIES:', species_data, flush=True)
        exif_species_data = [','.join((one_species['common'], \
                                       one_species['scientific'], \
                                       str(one_species['count']))) \
                                for one_species in species_data
                            ]

    # Check if we have any changes
    if not exif_location_data and not exif_species_data:
        print(f'HACK: EXIF CHANGE: NO DATA TO UPLOAD', flush=True)
        return True

    # Update the image file
    result = image_utils.write_embedded_image_info(
                        file_path,
                        json.dumps(exif_location_data) if exif_location_data is not None else None,
                        json.dumps(exif_species_data) if exif_species_data is not None else None
                        )

    print(f'HACK: EXIF CHANGE RESULT {result}', flush=True)
    return result


def process_upload_changes(s3_url: str, password: str, username: str, collection_id: str, \
                            upload_name: str, change_locations: tuple=None, \
                            files_info: tuple=None) -> tuple:
    """ Updates the image files with the information passed in
    Argument:
        s3_url: the URL to the S3 endpoint (in clear text)
        password: the user permission
        username: the name of the user associated with the token
        collection_id: the ID of the collection the files are in
        upload_name: the name of the upload
        change_locations: the location information for all the images in an upload
        files_info: the file species changes
    Return:
        Returns a tuple of files that did not update. If a location is specified, this list
        can include files not found in the original list
    Notes:
        If the location information doesn't have a location ID then only the files are processed.
        If the location does have a location ID then all the files in the location are processed,
        including the ones passed in
    """
    success_files = []
    failed_files = []
    # HACK
    print('HACK: PROCESSUPLOADCHANGES:', s3_url, username, collection_id, upload_name,
            change_locations is None, files_info is None, flush=True)
    # HACK

    # Make a dict of the files passed in for easier lookup
    if files_info:
        file_info_dict = {one_file['name']+one_file['s3_path']+one_file['bucket']: one_file for \
                                                                            one_file in files_info}
    else:
        file_info_dict = {}

    # Get the list of files to update
    update_files = files_info if not change_locations else \
                        S3Connection.get_image_paths(s3_url, username, password, collection_id, \
                                                                                        upload_name)

    edit_folder = tempfile.mkdtemp(prefix=SPARCD_PREFIX + 'edits_' + uuid.uuid4().hex)
    print('HACK: TEMPORARYEDITFOLDER:', edit_folder, flush=True)

    # All species and locations in case we have to look something up
    cur_species = load_sparcd_config(CONF_SPECIES_FILE_NAME, TEMP_SPECIES_FILE_NAME, s3_url, \
                                                                                username, password)

    # Loop through the files
    for idx, one_file in enumerate(update_files):
        temp_file_name = ("-"+str(idx)).join(os.path.splitext(\
                                                            os.path.basename(one_file['s3_path'])))
        print('HACK:   TEMPFILENAME:', temp_file_name, idx, one_file, flush=True)
        save_path = os.path.join(edit_folder, temp_file_name)

        file_key = one_file['name']+one_file['s3_path']+one_file['bucket']
        file_edits = file_info_dict[file_key] if file_key in file_info_dict else None

        # Only manipulate the image if there appears to be some reason for downloading it
        if not file_edits and not change_locations:
            success_files.append(one_file)
            continue

        # Get the image to work with
        S3Connection.download_image(s3_url, username, password, one_file['bucket'],
                                                                    one_file['s3_path'], save_path)
        cur_species, cur_location, _ = image_utils.get_embedded_image_info(save_path)

        # Species: get the current species and add our changes to that before writing them out
        save_species = None

        if file_edits:
            for new_species in file_edits['species']:
                found = False
                changed = False
                for orig_species in cur_species:
                    if orig_species['scientific'] == new_species['scientific']:
                        if orig_species['common'] != new_species['common']:
                            orig_species['common'] = new_species['common']
                            changed = True
                        if orig_species['count'] != new_species['count']:
                            orig_species['count'] = new_species['count']
                            changed = True
                        found = True
                        break

                if not found:
                    cur_species.append({'common': new_species['common'], \
                                         'scientific': new_species['scientific'], \
                                         'count': new_species['count']})
                    changed = True

            if changed:
                save_species = cur_species

        # Location: if the location is different from what's in the file, then write the data out
        save_location = None
        if change_locations and \
                        (cur_location is None or change_locations['loc_id'] != cur_location['id']):
            save_location = change_locations

        # Check if we have any changes
        if save_species or save_location:
            # Update the image file
            print('HACK: SAVING EXIF LOCATION:', save_location, flush=True)
            if update_image_file_exif(save_path,
                                    loc_id = save_location['loc_id'] if save_location else None,
                                    loc_name = save_location['loc_name'] if save_location else None,
                                    loc_ele = save_location['loc_ele'] if save_location else None,
                                    loc_lat = save_location['loc_lat'] if save_location else None,
                                    loc_lon = save_location['loc_lon'] if save_location else None,
                                    species_data = save_species):
                # Put the file back onto S3
                print('HACK: PUTTING IMAGE BACK',s3_url, one_file['bucket'], one_file['s3_path'], save_path, flush=True)
                S3Connection.upload_file(s3_url, username, password, one_file['bucket'],
                                                                    one_file['s3_path'], save_path)

                # Register this file as a success
                success_files.append(one_file)
            else:
                # File did not update
                failed_files.append(file_info_dict[file_key] if file_key in file_info_dict else \
                                        one_file|{'species': []})
        else:
            # Register this file as a success
            success_files.append(one_file)

        # Perform some cleanup
        for one_path in [save_path+"_original", save_path]:
            if one_path and os.path.exists(one_path):
                os.unlink(one_path)

    # Remove the downloading folder
    shutil.rmtree(edit_folder)

    return success_files, failed_files

@app.route('/', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def index():
    """Default page"""
    print("RENDERING TEMPLATE",DEFAULT_TEMPLATE_PAGE,os.getcwd(),flush=True)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    print('HACK:     IP:',client_ip, flush=True)
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    print('HACK:     USER AGENT:',client_user_agent, flush=True)
    if not client_user_agent or client_user_agent == '-':
        return 'Resource not found', 404
    return render_template(DEFAULT_TEMPLATE_PAGE)


@app.route('/favicon.ico', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def favicon():
    """ Return the favicon """
    return send_from_directory(app.root_path,
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/<string:filename>', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def sendfile(filename: str):
    """Return root files"""
    print("RETURN FILENAME:",filename,flush=True)

    # Check that the file is allowed
    if not os.path.splitext(filename)[1].lower() in ALLOWED_FILE_EXTENSIONS:
        return 'Resource not found', 404

    fullpath = os.path.realpath(os.path.join(RESOURCE_START_PATH, filename.lstrip('/')))
    print("   FILE PATH:", fullpath,flush=True)

    # Make sure we're only serving something that's in the same location that we are in and that
    # it exists
    if not fullpath or not os.path.exists(fullpath) or not fullpath.startswith(RESOURCE_START_PATH):
        return 'Resource not found', 404

    return send_file(fullpath)


@app.route('/_next/static/<path:path_fagment>', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def sendnextfile(path_fagment: str):
    """Return files"""
    print("RETURN _next FILENAME:",path_fagment,flush=True)

    # Check that the file is allowed
    if not os.path.splitext(path_fagment)[1].lower() in ALLOWED_FILE_EXTENSIONS:
        return 'Resource not found', 404

    fullpath = os.path.realpath(os.path.join(RESOURCE_START_PATH, '_next', 'static',\
                                                                        path_fagment.lstrip('/')))
    print("   FILE PATH:", fullpath,flush=True)

    # Make sure we're only serving something that's in the same location that we are in and that
    # it exists
    if not fullpath or not os.path.exists(fullpath) or not fullpath.startswith(RESOURCE_START_PATH):
        return 'Resource not found', 404

    return send_file(fullpath)


@app.route('/_next/image', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def sendnextimage():
    """Return image files"""
    image_path = request.args.get('url')
    w_param = request.args.get('w')
    q_param = request.args.get('q')
    print("RETURN _next IMAGE:",image_path,flush=True)

    # Normalize parameters
    if w_param:
        try:
            w_param = float(w_param)
        except ValueError:
            print('   INVALID width parameters')
            return 'Resource not found', 404
    if q_param:
        try:
            q_param = int(q_param)
            # make sure quality parameter has something "reasonable"
            # See: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#jpeg
            if q_param <= 0 or q_param > 100:
                q_param = 100
            elif q_param < 5:
                q_param = 5
        except ValueError:
            print('   INVALID quality parameters')
            return 'Resource not found', 404
    else:
        q_param = 100

    image_type = os.path.splitext(image_path)[1][1:].lower()

    # Check that the file is allowed
    if not '.'+image_type in ALLOWED_IMAGE_EXTENSIONS:
        return 'Resource not found', 404

    fullpath = os.path.realpath(os.path.join(RESOURCE_START_PATH, image_path.lstrip('/')))
    print("   FILE PATH:", fullpath,flush=True)

    # Make sure we're only serving something that's in the same location that we are in and
    # that it exists
    if not fullpath or not os.path.exists(fullpath) or not fullpath.startswith(RESOURCE_START_PATH):
        return 'Resource not found', 404

    # Check if sending image "as is"
    if not w_param or w_param <= 1.0:
        return send_file(fullpath)

    # Resize the image and send it
    if image_type.lower() == 'jpg':
        image_type = 'jpeg'

    img = Image.open(fullpath)

    h_param = float(img.size[1]) * (w_param / float(img.size[0]))
    img = img.resize((round(w_param), round(h_param)), Image.Resampling.LANCZOS)

    img_byte_array = io.BytesIO()
    img.save(img_byte_array, image_type.upper(), quality=q_param)

    img_byte_array.seek(0)  # move to the beginning of file after writing

    return send_file(img_byte_array, mimetype="image/" + image_type.lower())



@app.route('/login', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def login_token():
    """ Returns a token representing the login. No checks are made on the parameters
    Arguments: (POST or GET)
        url - the S3 database URL
        user - the user name
        password - the user credentials
        token - the token to check for
    Return:
        Returns the session key and associated user information
    Notes:
        All parameters can be specified. If a token is specified, it's checked
        for expiration first. If valid login information is specified, and the token
        is invalid/missing/expired, a new token is returned
    """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    print('LOGIN',flush=True)

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404
    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()

    if request.method == 'POST':
        url = request.form.get('url', None)
        user = request.form.get('user', None)
        password = request.form.get('password', None)
        token = request.form.get('token', None)
    else:
        url = request.args.get('url')
        user = request.args.get('user')
        password = request.args.get('password')
        token = request.args.get('token')

    # If the token is here for checking, and we have session information, see if it's valid
    if token is not None:
        # Checking the token for validity
        token_valid, login_info = token_is_valid(token, client_ip, user_agent_hash, db)
        if token_valid:
            # Everything checks out
            return json.dumps({'value':token,
                               'name':login_info['name'],
                               'settings':login_info['settings']|{'email':login_info['email']}
                               })

        # Delete the old token from the database
        db.reconnect()
        db.remove_token(token)

    # Make sure we have the components we need for logging in
    if not url or not user or not password:
        return "Not Found", 404

    # Log onto S3 to make sure the information is correct
    try:
        s3_url = web_to_s3_url(url)
        minio = Minio(s3_url, access_key=user, secret_key=password)
        _ = minio.list_buckets()
    except MinioException as ex:
        print('S3 exception caught:', ex)
        return "Not Found", 404

    # Save information into the database
    new_key = uuid.uuid4().hex
    db.reconnect()
    db.add_token(token=new_key, user=user, password=do_encrypt(password), client_ip=client_ip,
                    user_agent=user_agent_hash, s3_url=do_encrypt(s3_url))
    user_info = db.get_user(user)
    if not user_info:
        # Get the species
        cur_species = load_sparcd_config(CONF_SPECIES_FILE_NAME, TEMP_SPECIES_FILE_NAME, s3_url,
                                                                                    user, password)
        user_info = db.auto_add_user(user, species=cur_species)

    # Add in the email if we have user settings
    if 'settings' in user_info and isinstance(user_info['settings'], str) and user_info['settings']:
        try:
            cur_settings = json.loads(user_info['settings'])
            user_info['settings'] = cur_settings|{'email':user_info['email']}
        except json.JSONDecodeError as ex:
            print('Unable to add email to user settings:', user_info, flush=True)
            print(ex)

    user_info['settings'] = secure_user_settings(user_info['settings'])

    return json.dumps({'value':new_key, 'name':user_info['name'],
                       'settings':user_info['settings']})


@app.route('/collections', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def collections():
    """ Returns the list of collections and their uploads
    Arguments: (GET)
        token - the session token
    Return:
        Returns the list of accessible collections
    Notes:
        If the token is invalid, or a problem occurs, a 404 error is returned
    """
    print('COLLECTIONS', flush=True)
    db = SPARCdDatabase(DEFAULT_DB_PATH)

    token = request.args.get('t')
    if not token:
        print('COLLECTIONS TOKEN', flush=True)
        return "Not Found", 404

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        print('COLLECTIONS CLIENT', flush=True)
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Check if we have a stored temporary file containing the collections information
    # and return that
    return_colls = load_timed_temp_colls(user_info['name'])
    if return_colls:
        # Clear all permissions unless we're an owner
        for one_coll in return_colls:
            if not one_coll['permissions'] or not one_coll['permissions']['ownerProperty'] is True:
                del one_coll['allPermissions']
        return json.dumps(return_colls)

    # Get the collection information from the server
    s3_url = web_to_s3_url(user_info["url"])
    all_collections = S3Connection.get_collections(s3_url, user_info["name"], \
                                                            do_decrypt(db.get_password(token)))

    return_colls = []
    for one_coll in all_collections:
        return_colls.append(normalize_collection(one_coll))

    # Save the collections temporarily
    save_timed_temp_colls(return_colls)

    # Return the collections
    return json.dumps([{**one_coll, **{'allPermissions':None}} for one_coll in return_colls])


@app.route('/sandbox', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def sandbox():
    """ Returns the list of sandbox uploads
    Arguments: (GET)
        token - the session token
    Return:
        Returns the list of accessible collections
    Notes:
        If the token is invalid, or a problem occurs, a 404 error is returned
    """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    print('SANDBOX', request, flush=True)

    token = request.args.get('t')
    if not token:
        return "Not Found", 404

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404
    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()

    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the sandbox information from the database
    sandbox_items = db.get_sandbox(user_info["url"])

    # The S3 endpoint in case we need it
    s3_url = web_to_s3_url(user_info["url"])

    # Get the collections to fill in the return data
    # TODO: combine this with a load from S3?
    all_collections = load_timed_temp_colls(user_info['name'])

    return_sandbox = get_sandbox_collections(s3_url, user_info["name"],
                                do_decrypt(db.get_password(token)), sandbox_items, all_collections)

    return json.dumps(return_sandbox)


@app.route('/locations', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def locations():
    """ Returns the list of locations
    Arguments: (GET)
        token - the session token
    Return:
        Returns the list of locations
    Notes:
        If the token is invalid, or a problem occurs, a 404 error is returned
    """
    db = SPARCdDatabase(DEFAULT_DB_PATH)

    token = request.args.get('t')
    if not token:
        return "Not Found", 404

    print('LOCATIONS', request, flush=True)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404
    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()

    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the locations to return
    s3_url = web_to_s3_url(user_info["url"])
    cur_locations = load_locations(s3_url, user_info["name"], do_decrypt(db.get_password(token)))

    # Return the locations
    return json.dumps(cur_locations)


@app.route('/species', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def species():
    """ Returns the list of species
    Arguments: (GET)
        token - the session token
    Return:
        Returns the list of species
    Notes:
        If the token is invalid, or a problem occurs, a 404 error is returned
    """
    db = SPARCdDatabase(DEFAULT_DB_PATH)

    token = request.args.get('t')
    if not token:
        return "Not Found", 404

    print('SPECIES', request, flush=True)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404
    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()

    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the species to return
    s3_url = web_to_s3_url(user_info["url"])
    user_species = user_info['species']

    # Get the current species to see if we need to update the user's species
    cur_species = load_sparcd_config(CONF_SPECIES_FILE_NAME, TEMP_SPECIES_FILE_NAME, s3_url, \
                                            user_info["name"], do_decrypt(db.get_password(token)))

    # TODO: Timestamp the downloaded species and the user-specific species and only update as needed
    keyed_species = {one_species['scientificName']:one_species for one_species in cur_species}
    keyed_user = {one_species['scientificName']:one_species for one_species in user_species}

    # Check the easy path first
    updated = False
    if not user_species:
        user_species = cur_species
    else:
        # Try to find meaningfull differences
        all_keys = tuple(set(keyed_species.keys())|set(keyed_user.keys()))
        for one_key in all_keys:
            # First check for changes to existing species, else check for and add new species
            if one_key in keyed_species and one_key in keyed_user:
                if not keyed_species[one_key]['name'] == keyed_user[one_key]['name']:
                    keyed_user[one_key]['name'] = keyed_species[one_key]['name']
                    updated = True
                if not keyed_species[one_key]['speciesIconURL'] == \
                                                            keyed_user[one_key]['speciesIconURL']:
                    keyed_user[one_key]['speciesIconURL'] = keyed_species[one_key]['speciesIconURL']
                    updated = True
            elif one_key in keyed_species:
                # New species for this user (not in both sets of species but in downloaed species)
                keyed_user[one_key] = keyed_species[one_key]
                updated = True

    # Save changes if any were made
    if updated is True:
        user_species = [keyed_user[one_key] for one_key in keyed_user]
        species_json = json.dumps(user_species)
        db.save_user_species(user_info['name'], species_json)
        return species_json

    # Return the collections
    return json.dumps(user_species)


@app.route('/upload', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def upload():
    """ Returns the list of images from a collection's upload
    Arguments: (GET)
        token - the session token
        id - the ID of the collection
        up - the name of the upload
    Return:
        Returns the list of images for the collection's upload
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)

    token = request.args.get('t')
    collection_id = request.args.get('id')
    collection_upload = request.args.get('up')

    if not token or not collection_id or not collection_upload:
        return "Not Found", 404

    print('UPLOAD', request, flush=True)
    app.config['SERVER_NAME'] = request.host
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404
    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()

    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Save path
    save_path = os.path.join(tempfile.gettempdir(), SPARCD_PREFIX + collection_id + '_' + \
                                                                collection_upload + '.json')

    # The URL to the S3 instance
    s3_url = web_to_s3_url(user_info["url"])

    # Reload the saved information
    all_images = None
    if os.path.exists(save_path):
        all_images = load_timed_info(save_path)
        if all_images is not None:
            all_images = [all_images[one_key] for one_key in all_images.keys()]

    if all_images is None:
        # Get the collection information from the server
        all_images = S3Connection.get_images(s3_url, user_info["name"], \
                                                do_decrypt(db.get_password(token)), \
                                                collection_id, collection_upload)

        # Save the images so we can reload them later
        save_timed_info(save_path, {one_image['key']: one_image for one_image in all_images})

    # Get species data from the database and update the images
    edits = {}
    for one_image in all_images:
        # Find any edits for this image
        upload_path = os.path.dirname(one_image['s3_path'])
        edit_key = one_image['bucket'] + ':' + upload_path
        if not edit_key in edits:
            edits = {**edits,
                     **db.get_image_species_edits(user_info["url"], one_image['bucket'],upload_path)
                    }
        if not one_image['s3_path'] in edits[edit_key]:
            continue

        have_deletes = False        # Use to determine if we need to remove species
        species_edits = edits[edit_key][one_image['s3_path']]
        for one_species in species_edits:
            # Look for exiting species in image
            found = False
            for one_img_species in one_image['species']:
                if one_species[0] == one_img_species['scientificName']:
                    one_img_species['count'] = one_species[1]
                    have_deletes = one_species[1] <= 0
                    found = True
            # Add it in if not found
            if found is False:
                check_species = user_info['species']
                if not check_species:
                    check_species = load_sparcd_config(CONF_SPECIES_FILE_NAME,
                                                        TEMP_SPECIES_FILE_NAME,
                                                        s3_url,
                                                        user_info["name"],
                                                        do_decrypt(db.get_password(token)))


                found_species = [one_item for one_item in check_species if \
                                        one_item['scientificName'] == one_species[0]]
                if found_species and len(found_species) > 0:
                    found_species = found_species[0]
                else:
                    found_species = {'name': 'Unknown'}
                one_image['species'].append({'name':found_species['name'],
                                             'scientificName':one_species[0],
                                             'count':one_species[1]})

        # Fix up the species if we have some removals
        if have_deletes:
            one_image['species'] = [one_species for one_species in one_image['species'] if \
                                                                        one_species['count'] > 0]

    # Prepare the return data
    for one_img in all_images:
        one_img['url'] = url_for('image', _external=True,
                                    i=do_encrypt(json.dumps({ 'k':one_img["key"],
                                                              'p':save_path
                                                             })))
        one_img['s3_path'] = do_encrypt(one_img['s3_path'])
        one_img['upload'] = collection_upload

        del one_img['bucket']
        del one_img['s3_url']
        del one_img['key']

    return json.dumps(all_images)


@app.route('/image', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def image():
    """ Returns the image from the S3 storage
    Arguments: (GET)
        token - the session token
        i - the key of the image
    Return:
        Returns the image
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')

    try:
        image_req = json.loads(do_decrypt(request.args.get('i')))
    except json.JSONDecodeError:
        image_req = None

    # Check what we have from the requestor
    if not token or not image_req or not isinstance(image_req, dict) or \
                not all(one_key in image_req.keys() for one_key in ('k','p')):
        return "Not Found", 404

    image_key = image_req['k']
    image_store_path = image_req['p']

    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_user_agent or client_user_agent is None:
        return "Not Found", 404
    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()

    # Allow a timely request from everywhere
    token_valid, user_info = token_is_valid(token, '*', user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Load the image data
    image_data = load_timed_info(image_store_path)
    if image_data is None or not isinstance(image_data, dict):
        return "Not Found", 404

    # Get the url from the key
    if not image_key in image_data:
        return "Not Found", 404

    # Not to be confused with Flask's request
    res = requests.get(image_data[image_key]['s3_url'],
                       timeout=DEFAULT_IMAGE_FETCH_TIMEOUT_SEC,
                       allow_redirects=False)
    return res.content


@app.route('/query', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def query():
    """ Returns a token representing the login. No checks are made on the parameters
    Arguments: (POST or GET)
        url - the S3 database URL
        user - the user name
        password - the user credentials
        token - the token to check for
    Return:
        Returns the session key and associated user information
    Notes:
        All parameters can be specified. If a token is specified, it's checked
        for expiration first. If valid login information is specified, and the token
        is invalid/missing/expired, a new token is returned
    """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')

    print('QUERY', request)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404
    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()

    have_error = False
    filters = []
    for key, value in request.form.items(multi=True):
        match key:
            case 'collections' | 'dayofweek' | 'elevations' | 'hour' | 'locations' | \
                 'month' | 'species' | 'years':
                try:
                    filters.append((key, json.loads(value)))
                except json.JSONDecodeError:
                    print(f'Error: bad query data for key: {key}')
                    have_error = True
                    break
            case 'endDate' | 'startDate':
                filters.append((key, datetime.datetime.fromisoformat(value)))
                break
            case _:
                print(f'Error: unknown query key detected: {key}')
                have_error = True

    # Check what we have from the requestor
    if not token or have_error:
        print('INVALID TOKEN OR QUERY:',token,have_error)
        return "Not Found", 404
    if not filters:
        print('NO FILTERS SPECIFIED')
        return "Not Found", 404

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.remote_addr))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_user_agent or client_user_agent is None:
        return "Not Found", 404
    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()

    # Restrict requests
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    s3_url = web_to_s3_url(user_info["url"])

    # Get collections from the database
    coll_info = db.get_collections(TIMEOUT_COLLECTIONS_SEC)
    if coll_info is None or not coll_info:
        all_collections = S3Connection.list_collections(s3_url, user_info["name"], \
                                                            do_decrypt(db.get_password(token)))
        coll_info = [{'name':one_coll['bucket'], 'json':one_coll} \
                                                            for one_coll in all_collections]
        if not db.save_collections([{'name':one_coll['bucket'], 'json':json.dumps(one_coll)} \
                                                            for one_coll in all_collections]):
            print('Warning: Unable to save collections to the database')
    else:
        coll_info = [{'name':one_coll['name'],'json':json.loads(one_coll['json'])} \
                                                            for one_coll in coll_info]

    # Filter collections
    cur_coll = coll_info
    for one_filter in filters:
        if one_filter[0] == 'collections':
            cur_coll = [coll for coll in cur_coll if coll['name'] in one_filter[1]]

    # Get uploads information to further filter images
    all_results = filter_collections(db, cur_coll, user_info["url"], user_info["name"], token,
                                                                                            filters)

    # Get the species and locations
    cur_species = load_sparcd_config(CONF_SPECIES_FILE_NAME, TEMP_SPECIES_FILE_NAME, s3_url, \
                                            user_info["name"], do_decrypt(db.get_password(token)))
    cur_locations = load_locations(s3_url, user_info["name"], do_decrypt(db.get_password(token)))

    results = Results(all_results, cur_species, cur_locations,
                        s3_url, user_info["name"], do_decrypt(db.get_password(token)),
                        user_info['settings'], 60) # TODO: add query interval

    # Format and return the results
    results_id = uuid.uuid4().hex
    return_info = query_helpers.query_output(results, results_id)

    # Check for old queries and clean them up
    cleanup_old_queries(db, token)

    # Save the query for lookup when downloading results
    save_path = os.path.join(tempfile.gettempdir(), SPARCD_PREFIX + 'query_' + \
                                                                results_id + '.json')
    save_timed_info(save_path, return_info)
    db.save_query_path(token, save_path)

    return json.dumps(return_info)


@app.route('/query_dl', methods = ['GET'])
@cross_origin(origins="*", supports_credentials=True)
def query_dl():
    """ Returns the results of a query
    Arguments: (GET)
        token - the session token
        t - the name of the tab results to download
    Return:
        Returns the requested query download
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    tab = request.args.get('q')
    target = request.args.get('d')
    print('QUERY DOWNLOAD', request, flush=True)

    # Check what we have from the requestor
    if not token or not tab:
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404
    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()

    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the query information
    query_info_path, _ = db.get_query(token)
    print('           ',query_info_path, flush=True)

    # Try and load the query results
    query_results = load_timed_info(query_info_path, QUERY_RESULTS_TIMEOUT_SEC)
    if not query_results:
        return "Not Found", 404

    match(tab):
        case 'DrSandersonOutput':
            dl_name = target if target else 'drsanderson.txt'
            return Response(query_results[tab], \
                            mimetype='text/text', \
                            headers={'Content-disposition': f'attachment; filename="{dl_name}"'})

        case 'DrSandersonAllPictures':
            dl_name = target if target else 'drsanderson_all.csv'
            return Response(query_allpictures2csv(query_results[tab], user_info['settings'], \
                                    query_results['columsMods'][tab] if tab in \
                                                        query_results['columsMods'] else None), \
                            mimetype='application/csv', \
                            headers={'Content-disposition': f'attachment; filename="{dl_name}"'})

        case 'csvRaw':
            dl_name = target if target else 'allresults.csv'
            return Response(query_raw2csv(query_results[tab], user_info['settings'], \
                                    query_results['columsMods'][tab] if tab in \
                                                        query_results['columsMods'] else None), \
                            mimetype='text/csv', \
                            headers={'Content-disposition': f'attachment; filename="{dl_name}"'})

        case 'csvLocation':
            dl_name = target if target else 'locations.csv'
            return Response(query_location2csv(query_results[tab], user_info['settings'], \
                                    query_results['columsMods'][tab] if tab in \
                                                        query_results['columsMods'] else None),\
                            mimetype='text/csv', \
                            headers={'Content-disposition': f'attachment; filename="{dl_name}"'})

        case 'csvSpecies':
            dl_name = target if target else 'species.csv'
            return Response(query_species2csv(query_results[tab], user_info['settings'], \
                                    query_results['columsMods'][tab] if tab in \
                                                        query_results['columsMods'] else None), \
                            mimetype='text/csv', \
                            headers={'Content-disposition': f'attachment; filename="{dl_name}"'})

        case 'imageDownloads':
            dl_name = target if target else 'allimages.gz'
            s3_url = web_to_s3_url(user_info["url"])
            read_fd, write_fd = os.pipe()

            # Get and acqure the lock: indicates the files are downloaded when released
            # pylint: disable=consider-using-with
            download_finished_lock = threading.Semaphore(1)
            download_finished_lock.acquire()

            # Run the download and compression as a seperate process
            dl_thread = threading.Thread(target=generate_zip,
                                 args=(s3_url, user_info["name"],
                                       do_decrypt(db.get_password(token)),
                                       [row['name'] for row in query_results[tab]],
                                       write_fd, download_finished_lock)
                                )
            dl_thread.start()

            # Return the compressed data as an iterator over the data pipe
            return Response(zip_iterator(read_fd),
                            mimetype='application/gzip',
                            headers={'Content-disposition': f'attachment; filename="{dl_name}"'})

    return "Not Found", 404


@app.route('/settings', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def set_settings():
    """ Updates the user's settings
    Arguments: (GET)
        t - the session token
    Return:
        Returns the user's settings
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('SET SETTINGS', flush=True)

    new_settings = {
        'autonext': request.form.get('autonext', None),
        'dateFormat': request.form.get('dateFormat', None),
        'measurementFormat': request.form.get('measurementFormat', None),
        'sandersonDirectory': request.form.get('sandersonDirectory', None),
        'sandersonOutput': request.form.get('sandersonOutput', None),
        'timeFormat': request.form.get('timeFormat', None),
        'coordinatesDisplay': request.form.get('coordinatesDisplay', None)
    }
    new_email = request.form.get('email', None)

    # Check what we have from the requestor
    if not token:
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Update any settings that have changed
    modified = False
    new_keys = tuple(new_settings.keys())
    for one_key in new_keys:
        if not one_key in user_info['settings'] or \
                                        not new_settings[one_key] == user_info['settings'][one_key]:
            user_info['settings'][one_key] = new_settings[one_key]
            modified = True
    if not new_email == user_info['email']:
        user_info['email'] = new_email
        modified = True

    if modified:
        db.update_user_settings(user_info['name'], json.dumps(user_info['settings']),
                                                                                user_info['email'])

    user_info['settings'] = secure_user_settings(user_info['settings']|{'email':user_info['email']})

    return json.dumps(user_info['settings'])


@app.route('/locationInfo', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def location_info():
    """ Returns details on a location
    Arguments: (GET)
        t - the session token
    Return:
        Returns the location information
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('LOCATION INFO', flush=True)

    loc_id = request.form.get('id', None)
    loc_name = request.form.get('name', None)
    loc_lat = request.form.get('lat', None)
    loc_lon = request.form.get('lon', None)
    loc_ele = request.form.get('ele', None)
    try:
        if loc_lat is not None:
            loc_lat = float(loc_lat)
        if loc_lon is not None:
            loc_lon = float(loc_lon)
        if loc_ele is not None:
            loc_ele = float(loc_ele)
    except ValueError:
        return "Not Found", 406

    # Check what we have from the requestor
    if not all(item for item in [token, loc_id, loc_name, loc_lat, loc_lon, loc_ele]):
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    s3_url = web_to_s3_url(user_info["url"])
    cur_locations = load_locations(s3_url, user_info["name"], do_decrypt(db.get_password(token)))

    for one_loc in cur_locations:
        if one_loc['idProperty'] == loc_id and one_loc['nameProperty'] == loc_name and \
                        one_loc['latProperty'] == loc_lat and one_loc['lngProperty'] == loc_lon and\
                        one_loc['elevationProperty'] == loc_ele:
            return json.dumps(one_loc)

    return json.dumps({'idProperty': loc_id, 'nameProeprty': 'Unknown', 'latProperty':0.0, \
                            'lngProperty':0.0, 'elevationProperty':0.0,
                            'utm_code':DEFAULT_UTM_ZONE, 'utm_x':0.0, 'utm_y':0.0})


@app.route('/sandboxPrev', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def sandbox_prev():
    """ Checks if a sandbox item has been previously uploaded
    Arguments: (GET)
        t - the session token
    Return:
        Returns whether the upload was already atempted and any missing file names
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('SANDBOX PREV', flush=True)

    rel_path = request.form.get('path', None)

    # Check what we have from the requestor
    if not token or not rel_path:
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401


    # Check with the DB if the upload has been started before
    elapsed_sec, uploaded_files, upload_id, old_upload_id = db.sandbox_get_upload(user_info["url"],
                                                                                user_info['name'],
                                                                                rel_path,
                                                                                True)
    print('HACK:     ',upload_id, old_upload_id,flush=True)

    return json.dumps({'exists': (uploaded_files is not None), 'path': rel_path, \
                        'uploadedFiles': uploaded_files, 'elapsed_sec': elapsed_sec, \
                        'id': upload_id})


@app.route('/sandboxNew', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def sandbox_new():
    """ Adds a new sandbox upload to the database
    Arguments: (GET)
        t - the session token
    Return:
        Returns the success of adding the upload to the database
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('SANDBOX NEW', flush=True)

    location_id = request.form.get('location', None)
    collection_id = request.form.get('collection', None)
    comment = request.form.get('comment', None)
    rel_path = request.form.get('path', None)
    all_files = request.form.get('files', None)
    timestamp = request.form.get('ts', None)
    timezone = request.form.get('tz', None)

    # Check what we have from the requestor
    if not all(item for item in [token, location_id, collection_id, comment, rel_path, all_files, \
                                                                            timestamp, timezone]):
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get all the file names
    try:
        all_files = json.loads(all_files)
    except json.JSONDecodeError as ex:
        print('ERROR: Unable to load file list JSON', ex, flush=True)
        return "Not Found", 406

    # Create the upload location
    s3_url = web_to_s3_url(user_info["url"])
    client_ts = datetime.datetime.fromisoformat(timestamp).astimezone(dateutil.tz.gettz(timezone))
    s3_bucket, s3_path = S3Connection.create_upload(s3_url, user_info["name"], \
                                        do_decrypt(db.get_password(token)), collection_id, \
                                        comment, client_ts, len(all_files))

    # Upload the CAMTRAP files to S3 storage
    cur_locations = load_locations(s3_url, user_info["name"], do_decrypt(db.get_password(token)))
    our_location = get_location_info(location_id, cur_locations)
    for one_file in CAMTRAP_FILE_NAMES:
        if one_file == DEPLOYMENT_CSV_FILE_NAME:
            data = ','.join(create_deployment_data(s3_bucket[len(SPARCD_PREFIX):], our_location))
        elif one_file == MEDIA_CSV_FILE_NAME:
            # TODO: just upload the saved CSV file to the server
            media_data = create_media_data(s3_bucket[len(SPARCD_PREFIX):], location_id,
                                                                            s3_path, all_files)
            save_camtrap_file(s3_bucket+'_'+os.path.basename(s3_path)+'_'+MEDIA_CSV_FILE_NAME,
                                                                                    media_data)

            data = '\n'.join([','.join(one_media) for one_media in media_data])
        else:
            data = '\n'.join([','.join(one_media) for one_media in \
                                    create_observation_data(s3_bucket[len(SPARCD_PREFIX):],
                                                            location_id, s3_path, all_files)])

        S3Connection.upload_file_data(s3_url, user_info["name"],
                                        do_decrypt(db.get_password(token)), s3_bucket,
                                        s3_path + '/' + one_file, data, 'application/csv')

    # Add the entries to the database
    upload_id = db.sandbox_new_upload(user_info["url"], user_info['name'], rel_path, all_files,
                                                                s3_bucket, s3_path,
                                                                our_location['idProperty'],
                                                                our_location['nameProperty'],
                                                                our_location['latProperty'],
                                                                our_location['lngProperty'],
                                                                our_location['elevationProperty'])

    # Update the collection to reflect the new upload
    updated_collection = S3Connection.get_collection_info(s3_url, user_info["name"], \
                                                    do_decrypt(db.get_password(token)), s3_bucket)
    if updated_collection:
        updated_collection = normalize_collection(updated_collection)

        # Check if we have a stored temporary file containing the collections information
        return_colls = load_timed_temp_colls(user_info['name'])
        if return_colls:
            return_colls = [one_coll if one_coll['bucket'] != s3_bucket else updated_collection \
                                                                    for one_coll in return_colls ]
            # Save the collections temporarily
            save_timed_temp_colls(return_colls)

    # Return the new ID
    return json.dumps({'id': upload_id})


@app.route('/sandboxFile', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def sandbox_file():
    """ Handles the upload for a new image
    Arguments: (GET)
        t - the session token
    Return:
        Returns the success of storing the uploaded image
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('SANDBOX FILES', flush=True)

    upload_id = request.form.get('id', None)

    # Check what we have from the requestor
    if not token or not upload_id or len(request.files) <= 0:
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the location to upload to
    s3_url = web_to_s3_url(user_info["url"])
    s3_bucket, s3_path = db.sandbox_get_s3_info(user_info['name'], upload_id)

    # Upload all the received files and update the database
    temp_file = tempfile.mkstemp(prefix=SPARCD_PREFIX)
    os.close(temp_file[0])
    for one_file in request.files:
        request.files[one_file].save(temp_file[1])

        cur_species, cur_location, cur_timestamp = image_utils.get_embedded_image_info(temp_file[1])

        # Check if we need to update the location in the file
        sb_location = db.sandbox_get_location(user_info["name"], upload_id)
        print('HACK:     COMPARELOC:', sb_location, cur_location, flush=True)
        if not cur_location or \
                (sb_location and cur_location and sb_location['idProperty'] != cur_location['id']):

            print('HACK:     UPDATING LOCATION', flush=True)
            # Update the location
            if not update_image_file_exif(temp_file[1],
                                            loc_id=sb_location['idProperty'],
                                            loc_name=sb_location['nameProperty'],
                                            loc_ele=sb_location['elevationProperty'],
                                            loc_lat=sb_location['latProperty'],
                                            loc_lon=sb_location['lngProperty'],
                                            ):
                print('Warning: Unable to update sandbox file with the location: ' \
                        f'{request.files[one_file].filename} with upload_id {upload_id}'
                     , flush=True)

        # Upload the file to S3
        S3Connection.upload_file(s3_url, user_info["name"],
                                        do_decrypt(db.get_password(token)), s3_bucket,
                                        s3_path + '/' + request.files[one_file].filename,
                                        temp_file[1])

        # Update the database entry to show the file is uploaded
        file_id = db.sandbox_file_uploaded(user_info['name'], upload_id,
                                request.files[one_file].filename, request.files[one_file].mimetype)

        # Check if we need to store the species and locations in camtrap
        if (cur_species and cur_timestamp) or cur_location:
            db.sandbox_add_file_info(file_id, cur_species, cur_location, cur_timestamp.isoformat())

    os.unlink(temp_file[1])

    return json.dumps({'success': True})


@app.route('/sandboxCounts', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def sandbox_counts():
    """ Returns the counts of the sandbox upload
    Arguments: (GET)
        t - the session token
    Return:
        Returns the counts of how many sandbox images are marked as uploaded
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    upload_id = request.args.get('i')
    print('SANDBOX COUNTS', flush=True)

    # Check what we have from the requestor
    if not token or not upload_id:
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Mark the upload as completed
    counts = db.sandbox_upload_counts(user_info['name'], upload_id)

    return json.dumps({'total': counts[0], 'uploaded': counts[1]})


@app.route('/sandboxReset', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def sandbox_reset():
    """ Resets the sandbox to start an upload from the beginning
    Arguments: (GET)
        t - the session token
    Return:
        Returns the new upload ID
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('SANDBOX RESET', flush=True)

    upload_id = request.form.get('id', None)
    all_files = request.form.get('files', None)

    # Check what we have from the requestor
    if not token or not upload_id or not all_files:
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get all the file names
    try:
        all_files = json.loads(all_files)
    except json.JSONDecodeError as ex:
        print('ERROR: Unable to load file list JSON', ex, flush=True)
        return "Not Found", 406

    # Check with the DB if the upload has been started before
    upload_id = db.sandbox_reset_upload(user_info['name'], upload_id, all_files)

    return json.dumps({'id': upload_id})


@app.route('/sandboxCompleted', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def sandbox_completed():
    """ Marks a sandbox as completely uploaded
    Arguments: (GET)
        t - the session token
    Return:
        Returns success if everything works out
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('SANDBOX COMPLETED', flush=True)

    upload_id = request.form.get('id', None)

    # Check what we have from the requestor
    if not token or not upload_id:
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the sandbox information
    s3_url = web_to_s3_url(user_info["url"])
    print('HACK: SANDBOXCOMPLETE:',user_info['name'], upload_id, flush=True)
    s3_bucket, s3_path = db.sandbox_get_s3_info(user_info['name'], upload_id)
    print('HACK:                :',s3_bucket, s3_path, flush=True)

    # Update the MEDIA csv file to include media types
    media_info = load_camtrap_media(s3_url, user_info["name"], token, db, s3_bucket, s3_path)
    file_mimetypes = db.get_file_mimetypes(user_info['name'], upload_id)

    for one_key,one_type in file_mimetypes:
        media_info[one_key][CAMTRAP_MEDIA_TYPE_IDX] = one_type

    # Upload the MEDIA csv file to the server
    S3Connection.upload_camtrap_data(s3_url, user_info["name"], do_decrypt(db.get_password(token)),
                                     s3_bucket, '/'.join((s3_path, MEDIA_CSV_FILE_NAME)),
                                     (media_info[one_key] for one_key in media_info.keys()) )

    # Update the OBSERVATIONS with species information
    file_species = db.get_file_species(user_info['name'], upload_id)
    if file_species:
        obs_info = load_camtrap_observations(s3_url, user_info["name"], token, db, s3_bucket, s3_path)
        for one_species in file_species:
            added = False
            if one_species['filename'] in obs_info:
                for one_row in obs_info[one_species['filename']]:
                    # See if we have an open entry
                    if not one_row[CAMTRAP_OBSERVATION_SCIENTIFIC_NAME_IDX]:
                        one_row[CAMTRAP_OBSERVATION_DATE_IDX] = one_species['timestamp']
                        one_row[CAMTRAP_OBSERVATION_SCIENTIFIC_NAME_IDX] = one_species['scientific']
                        one_row[CAMTRAP_OBSERVATION_COUNT_IDX] = str(one_species['count'])
                        one_row[CAMTRAP_OBSERVATION_COUNT_NEW_IDX] = '0'
                        one_row[CAMTRAP_OBSERVATION_COMMENT_IDX] = \
                                                            f'[COMMONNAME:{one_species["common"]}]'

                        if not one_row[CAMTRAP_OBSERVATION_CONFIDENCE_INDEX]:
                            one_row[CAMTRAP_OBSERVATION_CONFIDENCE_INDEX] = '1.0000'

                        added = True
                        break
            else:
                # Missing file entry
                obs_info[one_species['filename']] = []

            # Add a new entry if needed
            if not added:
                obs_info[one_species['filename']].append((
                    '',                                                  # Observation ID
                    s3_bucket[len(SPARCD_PREFIX):]+one_species['loc_id'],# Deployment ID
                    '',                                                  # Sequence ID
                    '/'.join((s3_path,one_species['filename'])),         # Media ID
                    one_species['timestamp'],                            # Timestamp
                    '',                                                  # Observation type
                    'FALSE',                                             # Camera setup
                    '',                                                  # Taxon ID
                    one_species['scientific'],                           # Scientific name
                    str(one_species['count']),                           # Count
                    '0',                                                 # Count new
                    '',                                                  # Life stage
                    '',                                                  # Sex
                    '',                                                  # Behavior
                    '',                                                  # Individual ID
                    '',                                                  # Classification method
                    '',                                                  # Classified by
                    '',                                                  # Classification timestamp
                    '1.0000',                                            # Classification confidence
                    f'[COMMONNAME:{one_species["common"]}]'              # Comment
                    ))

        # Upload the OBSERVATIONS csv file to the server
        # Tuple of row tuples for each file. (((,,),(,,)),((,,),(,,)), ...) Each row is also a tuple
        # We flatten further on the call so we're left with a single tuple containing all rows
        row_groups = (obs_info[one_key] for one_key in obs_info)
        S3Connection.upload_camtrap_data(s3_url, user_info["name"],
                                    do_decrypt(db.get_password(token)),
                                     s3_bucket, '/'.join((s3_path, OBSERVATIONS_CSV_FILE_NAME)),
                                     [one_row for one_set in row_groups for one_row in one_set] )

    # Clean up any temporary files we might have
    for one_filename in [MEDIA_CSV_FILE_NAME, OBSERVATIONS_CSV_FILE_NAME]:
        del_path = os.path.join(tempfile.gettempdir(),
                    SPARCD_PREFIX+s3_bucket+'_'+os.path.basename(s3_path)+'_'+one_filename)
        if os.path.exists(del_path):
            os.unlink(del_path)

    # Update the upload metadata with the count of files that have species
    S3Connection.update_upload_metadata_image_species(s3_url, user_info["name"],
                                                                do_decrypt(db.get_password(token)),
                                                                s3_bucket, s3_path, len(obs_info))

    # Update the collection to reflect the new upload metadata
    updated_collection = S3Connection.get_collection_info(s3_url, user_info["name"], \
                                                    do_decrypt(db.get_password(token)), s3_bucket)
    if updated_collection:
        updated_collection = normalize_collection(updated_collection)

        # Check if we have a stored temporary file containing the collections information
        return_colls = load_timed_temp_colls(user_info['name'])
        if return_colls:
            return_colls = [one_coll if one_coll['bucket'] != s3_bucket else updated_collection \
                                                                    for one_coll in return_colls ]
            # Save the collections temporarily
            save_timed_temp_colls(return_colls)

    # Mark the upload as completed
    db.sandbox_upload_complete(user_info['name'], upload_id)

    return json.dumps({'success': True})


@app.route('/uploadLocation', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def image_location():
    """ Handles the location for images changing
    Arguments: (GET)
        t - the session token
    Return:
        Returns success unless there's an issue
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('IMAGE LOCATION', flush=True)

    timestamp = request.form.get('timestamp', None)
    coll_id = request.form.get('collection', None)
    upload_id = request.form.get('upload', None)
    loc_id = request.form.get('locId', None)
    loc_name = request.form.get('locName', None)
    loc_ele = request.form.get('locElevation', None)
    loc_lat = request.form.get('locLat', None)
    loc_lon = request.form.get('locLon', None)

    # Check what we have from the requestor
    if not all (item for item in [token, coll_id, upload_id, loc_id, loc_name, loc_ele, timestamp]):
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    bucket = SPARCD_PREFIX + coll_id
    upload_path = f'Collections/{coll_id}/Uploads/{upload_id}'

    db.add_collection_edit(user_info["url"], bucket, upload_path, user_info['name'], timestamp,
                                                                        loc_id, loc_name, loc_ele)

    s3_url = web_to_s3_url(user_info["url"])
    process_upload_changes(s3_url, do_decrypt(db.get_password(token)), user_info["name"],
                            coll_id, upload_id,
                            {
                                'loc_id': loc_id,
                                'loc_name': loc_name,
                                'loc_ele': loc_ele,
                                'loc_lat': loc_lat,
                                'loc_lon': loc_lon,
                            })

    return json.dumps({'success': True})


@app.route('/imageSpecies', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def image_species():
    """ Handles the species and counts for an image changing
    Arguments: (GET)
        t - the session token
    Return:
        Returns success unless there's an issue
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('IMAGE SPECIES', flush=True)

    timestamp = request.form.get('timestamp', None)
    coll_id = request.form.get('collection', None)
    upload_id = request.form.get('upload', None)
    path = request.form.get('path', None) # Image path on S3 under bucket
    common_name = request.form.get('common', None)
    scientific_name = request.form.get('species', None) # Scientific name
    count = request.form.get('count', None)

    # Check what we have from the requestor
    if not all(item for item in [token, timestamp, coll_id, upload_id, path, common_name, \
                                                                        scientific_name, count]):
        return "Not Found", 406

    path = do_decrypt(path)
    if upload_id not in path or coll_id not in path:
        return "Not Found", 404

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    bucket = SPARCD_PREFIX + coll_id

    db.add_image_species_edit(user_info["url"], bucket, path, user_info['name'], timestamp,
                                                                common_name, scientific_name, count)

    return json.dumps({'success': True})


@app.route('/imageEditComplete', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def image_edit_complete():
    """ Handles updating the image with the changes made
    Arguments: (GET)
        t - the session token
    Return:
        Returns success unless there's an issue
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('IMAGE EDIT COMPLETE', flush=True)

    coll_id = request.form.get('collection', None)
    upload_id = request.form.get('upload', None)
    path = request.form.get('path', None) # Image path on S3 under bucket

    # Check what we have from the requestor
    if not all(item for item in [token, coll_id, upload_id, path]):
        return "Not Found", 406

    path = do_decrypt(path)
    if upload_id not in path or coll_id not in path:
        return "Not Found", 404

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    s3_url = web_to_s3_url(user_info["url"])

    # Get any changes
    upload_location_info = db.get_next_upload_location(user_info["url"], user_info["name"])

    upload_files_info = db.get_next_files_info(user_info["url"], user_info["name"],
                upload_location_info['bucket'] if upload_location_info and \
                                                    'bucket' in upload_location_info else None,
                upload_location_info['base_path'] if upload_location_info and \
                                                    'base_path' in upload_location_info else None
                )

    print('HACK: NEXTFILEDB:', upload_files_info, upload_location_info, flush=True)
    if upload_files_info:
        # Update the image
        success_files, errored_files = process_upload_changes(s3_url,
                                                            do_decrypt(db.get_password(token)),
                                                            user_info["name"],
                                                            coll_id,
                                                            upload_id,
                                                            change_locations=upload_location_info,
                                                            files_info=upload_files_info)

        if success_files:
            # Update the Observations file

            db.complete_image_edits(user_info["name"], success_files)
            if not errored_files and upload_location_info:
                db.complete_upload_location(user_info["url"],
                                            user_info["name"],
                                            upload_location_info['bucket'],
                                            upload_location_info['base_path'])

        if errored_files:
            return {'success': False, 'message': 'Not all the edits could be completed', \
                                                                                'canRetry': True}

    return {'success': True, 'message': "The images have been successfully updated"}


@app.route('/speciesKeybind', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def species_keybind():
    """ Handles the adding/changing a species keybind
    Arguments: (GET)
        t - the session token
    Return:
        Returns success unless an issue is found
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('IMAGE SPECIES', flush=True)

    common = request.form.get('common', None) # Species name
    scientific = request.form.get('scientific', None) # Species scientific name
    new_key = request.form.get('key', None)

    # Check what we have from the requestor
    if not token or not common or not scientific or not new_key:
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the species
    if 'species' in user_info and user_info['species']:
        cur_species = user_info['species']
    else:
        s3_url = web_to_s3_url(user_info["url"])
        cur_species = load_sparcd_config(CONF_SPECIES_FILE_NAME, TEMP_SPECIES_FILE_NAME, s3_url, \
                                            user_info["name"], do_decrypt(db.get_password(token)))

    # Update the species
    found = False
    for one_species in cur_species:
        if one_species['scientificName'] == scientific:
            one_species['keyBinding'] = new_key[0]
            found = True
            break

    # Add entry if it's not in the species
    if not found:
        cur_species.append({'name':common, 'scientificName':scientific, 'keyBinding':new_key[0], \
                                            "speciesIconURL": "https://i.imgur.com/4qz5mI0.png"})

    db.save_user_species(user_info['name'], json.dumps(cur_species))

    return json.dumps({'success': True})


@app.route('/adminCheck', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def admin_check():
    """ Checks if the user might be an admin
    Arguments: (GET)
        t - the session token
    Return:
        Returns True if the user is possibly an admin
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('ADMIN CHECK', flush=True)

    # Check what we have from the requestor
    if not token:
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    return {'value': user_info['admin'] == 1}

@app.route('/adminCheckChanges', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def admin_check_changes():
    """ Checks if the user might be an admin
    Arguments: (GET)
        t - the session token
    Return:
        Returns True if the user is possibly an admin
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('ADMIN CHECK', flush=True)

    # Check what we have from the requestor
    if not token:
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Check for changes in the db
    changed = db.have_admin_changes(user_info["url"], user_info['name'])

    return {'success': True, 'locationsChanged': changed['locationsCount'] > 0, \
            'speciesChanged': changed['speciesCount'] > 0}


@app.route('/settingsAdmin', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def settings_admin():
    """ Confirms the password is correct for admin editing
    Arguments: (GET)
        t - the session token
    Return:
        Returns True if the user is possibly an admin
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('ADMIN CHECK', flush=True)

    pw = request.form.get('value', None)

    # Check what we have from the requestor
    if not token or not pw:
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Log onto S3 to make sure the information is correct
    pw_ok = False
    try:
        s3_url = web_to_s3_url(user_info["url"])
        minio = Minio(s3_url, access_key=user_info["name"], secret_key=pw)
        _ = minio.list_buckets()
        pw_ok = True
    except MinioException as ex:
        print(f'Admin password check failed for {user_info["name"]}:', ex)
        return "Not Found", 401

    return json.dumps({'success': pw_ok})


@app.route('/adminUsers', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def admin_users():
    """ Returns user information for admin editing
    Arguments: (GET)
        t - the session token
    Return:
        Returns the list of registered users and their information
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('ADMIN USERS', flush=True)

    # Check what we have from the requestor
    if not token:
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the users and fill in the collection information
    all_users = db.get_admin_edit_users()

    if not all_users:
        return json.dumps(all_users)

    # Organize the collection permissions by user
    # TODO: Handle when collections have timed out
    all_collections = load_timed_temp_colls(user_info['name'])
    user_collections = {}
    if all_collections:
        for one_coll in all_collections:
            if 'allPermissions' in one_coll and one_coll['allPermissions'] is not None:
                for one_perm in one_coll['allPermissions']:
                    if one_perm['usernameProperty'] not in user_collections:
                        user_collections[one_perm['usernameProperty']] = []
                    user_collections[one_perm['usernameProperty']].append({
                        'name':one_coll['name'],
                        'id':one_coll['id'],
                        'owner':one_perm['ownerProperty'] if 'ownerProperty' in \
                                                                        one_perm else False,
                        'read':one_perm['readProperty'] if 'readProperty' in \
                                                                        one_perm else False,
                        'write':one_perm['uploadProperty'] if 'uploadProperty' in \
                                                                        one_perm else False,
                        })

    # Put it all together
    return_users = []
    # TODO: What to do if collections havent been loaded yet?
    for one_user in all_users:
        return_users.append({'name': one_user[0], 'email': one_user[1], 'admin': one_user[2] == 1, \
                         'auto': one_user[3] == 1,
                         'collections': user_collections[one_user[0]] if user_collections else []})

    return json.dumps(return_users)

@app.route('/adminSpecies', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def admin_species():
    """ Returns "official" species for admin editing (not user-specific)
    Arguments: (GET)
        t - the session token
    Return:
        Returns the list of official species
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('ADMIN SPECIES', flush=True)

    # Check what we have from the requestor
    if not token:
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the species
    s3_url = web_to_s3_url(user_info["url"])
    cur_species = load_sparcd_config(CONF_SPECIES_FILE_NAME, TEMP_SPECIES_FILE_NAME, s3_url,
                                            user_info["name"], do_decrypt(db.get_password(token)))

    return json.dumps(cur_species)

@app.route('/adminUserUpdate', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def admin_user_update():
    """ Confirms the password is correct for admin editing
    Arguments: (GET)
        t - the session token
    Return:
        Returns True if the user is possibly an admin
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('ADMIN USER UDPATE', flush=True)

    old_name = request.form.get('oldName', None)
    new_email = request.form.get('newEmail', None)

    # Check what we have from the requestor
    if not all(item for item in [token, old_name, new_email]):
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    if not user_info['name'] == old_name:
        return {'success': False, 'message': f'User "{old_name}" not found'}

    db.update_user(old_name, new_email)
    return {'success': True, 'message': f'Successfully updated user "{old_name}"'}

@app.route('/adminSpeciesUpdate', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def admin_species_update():
    """ Adds/updates a species entry
    Arguments: (GET)
        t - the session token
    Return:
        Returns True if the the species was put in the database to be updated
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('ADMIN SPECIES UDPATE', flush=True)

    new_name = request.form.get('newName', None)
    old_scientific = request.form.get('oldScientific', None)
    new_scientific = request.form.get('newScientific', None)
    key_binding = request.form.get('keyBinding', '')
    icon_url = request.form.get('iconURL', None)

    # Check what we have from the requestor
    if not all(item for item in [token, new_name, new_scientific, icon_url]):
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the species
    s3_url = web_to_s3_url(user_info["url"])
    cur_species = load_sparcd_config(CONF_SPECIES_FILE_NAME, TEMP_SPECIES_FILE_NAME, s3_url,
                                            user_info["name"], do_decrypt(db.get_password(token)))

    # Make sure this is OK to do
    find_scientific = old_scientific if old_scientific else new_scientific
    found_match = [one_species for one_species in cur_species if \
                                                one_species['scientificName'] == find_scientific]

    # If we're replacing, we should have found the entry
    if old_scientific is not None and (not found_match or len(found_match) <= 0):
        return {'success': False, 'message': f'Species "{old_scientific}" not found'}
    # If we're not replaceing, we should NOT find the entry
    if old_scientific is None and (found_match and len(found_match) > 0):
        return {'success': False, 'message': f'Species "{new_scientific}" already exists'}

    # Put the change in the DB
    if db.update_species(user_info["url"], user_info['name'], old_scientific, new_scientific, \
                                                                new_name, key_binding, icon_url):
        return {'success': True, 'message': f'Successfully updated species "{find_scientific}"'}

    return {'success': False, \
                'message': f'A problem ocurred while updating species "{find_scientific}"'}


@app.route('/adminLocationUpdate', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def admin_location_update():
    """ Adds/updates a location information
    Arguments: (GET)
        t - the session token
    Return:
        Returns True if the location as added to the database
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('ADMIN LOCATION UDPATE', flush=True)

    loc_name = request.form.get('name', None)
    loc_id = request.form.get('id', None)
    loc_active = request.form.get('active', None)
    measure = request.form.get('measure', None)
    loc_ele = request.form.get('elevation', None)
    coordinate = request.form.get('coordinate', None)
    loc_new_lat = request.form.get('new_lat', None)
    loc_new_lng = request.form.get('new_lon', None)
    loc_old_lat = request.form.get('old_lat', None)
    loc_old_lng = request.form.get('old_lon', None)
    utm_zone = request.form.get('utm_zone', None)
    utm_letter = request.form.get('utm_letter', None)
    utm_x = request.form.get('utm_x', None)
    utm_y = request.form.get('utm_y', None)

    # Check what we have from the requestor
    if not all(item for item in [token, loc_name, loc_id, loc_active, measure, coordinate]):
        return "Not Found", 406
    if measure not in ['feet', 'meters'] or coordinate not in ['UTM', 'LATLON']:
        return "Not Found", 406
    if coordinate == 'UTM' and not all(item for item in [utm_zone, utm_letter, utm_x, utm_y]):
        return "Not Found", 406
    if not all(item for item in [loc_new_lat, loc_new_lng]):
        return "Not Found", 406

    if loc_new_lat:
        loc_new_lat = float(loc_new_lat)
    if loc_new_lng:
        loc_new_lng = float(loc_new_lng)
    if loc_old_lat:
        loc_old_lat = float(loc_old_lat)
    if loc_old_lng:
        loc_old_lng = float(loc_old_lng)

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the location
    s3_url = web_to_s3_url(user_info["url"])
    cur_locations = load_locations(s3_url, user_info["name"], do_decrypt(db.get_password(token)))

    # Make sure this is OK to do
    if loc_old_lat and loc_old_lng:
        found_match = [one_location for one_location in cur_locations if \
                                                one_location['idProperty'] == loc_id and
                                                one_location['latProperty'] == loc_old_lat and
                                                one_location['lngProperty'] == loc_old_lng]

        # If we're replacing, we should have found the entry
        if not found_match or len(found_match) <= 0:
            return {'success': False, 'message': f'Location {loc_id} not found with Lat/Lon ' \
                        f'{loc_old_lat}, {loc_old_lng}'}
    else:
        found_match = [one_location for one_location in cur_locations if \
                                                one_location['idProperty'] == loc_id and
                                                one_location['latProperty'] == loc_new_lat and
                                                one_location['lngProperty'] == loc_new_lng]

        # If we're not replacing, we should NOT find the entry
        if found_match and len(found_match) > 0:
            return {'success': False, 'message': f'Location {loc_id} already exists with ' \
                        f'Lat/Lon {loc_new_lat}, {loc_new_lng}'}

    # Convert elevation to meters if needed
    if measure.lower() == 'feet':
        loc_ele = round((loc_ele * 0.3048000097536) * 100) / 100

    # Convert UTM to Lat/Lon if needed
    if coordinate == 'UTM':
        loc_new_lat, loc_new_lng = utm2deg(float(utm_x), float(utm_y), utm_zone, utm_letter)
        utm_code = utm_zone+utm_letter
    else:
        utm_x, utm_y = deg2utm(float(loc_new_lat), float(loc_new_lng))
        utm_code = ''.join([str(one_item) for one_item in deg2utm_code(float(loc_new_lat),
                                                                       float(loc_new_lng))
                            ])

    # Put the change in the DB
    if db.update_location(user_info["url"], user_info['name'], loc_name, loc_id, loc_active,
                                        loc_ele,loc_old_lat,loc_old_lng, loc_new_lat, loc_new_lng):
        return {'success': True, 'message': f'Successfully updated location {loc_name}',
                'data':{'nameProperty': loc_name, 'idProperty': loc_id, \
                        'elevationProperty': loc_ele, 'activeProperty': loc_active, \
                        'latProperty': loc_new_lat, 'lngProperty': loc_new_lng, \
                        'utm_code': utm_code, 'utm_x': utm_x, 'utm_y': utm_y
                        }
                }

    return {'success': False, \
                'message': f'A problem ocurred while updating location {loc_name}'}


@app.route('/adminCollectionUpdate', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def admin_collection_update():
    """ Adds/updates a collection information
    Arguments: (GET)
        t - the session token
    Return:
        Returns True if the collection was updated
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('ADMIN COLLECTION UDPATE', flush=True)

    col_id = request.form.get('id', None)
    col_name = request.form.get('name', None)
    col_desc = request.form.get('description', None)
    col_email = request.form.get('email', None)
    col_org = request.form.get('organization', None)
    col_all_perms = request.form.get('allPermissions', None)

    # Check what we have from the requestor
    if not all(item for item in [token, col_id, col_name, col_all_perms]):
        return "Not Found", 406

    if col_desc is None:
        col_desc = ''
    if col_email is None:
        col_email = ''
    if col_org is None:
        col_org = ''

    col_all_perms = json.loads(col_all_perms)

    # Check the rest of what we got
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get existing collection information and permissions
    s3_url = web_to_s3_url(user_info["url"])
    s3_bucket = SPARCD_PREFIX + col_id

    # TODO: Handle when collections have timed out
    all_collections = load_timed_temp_colls(user_info['name'])

    # Update the entry to what we need
    found_coll = None
    for one_coll in all_collections:
        if one_coll['id'] == col_id:
            one_coll['name'] = col_name
            one_coll['description'] = col_desc
            one_coll['email'] = col_email
            one_coll['organization'] = col_org
            found_coll = one_coll
            break

    if found_coll is None:
        return {'success': False, 'message': "Unable to find collection in list to update"}

    # Upload the changes
    S3Connection.save_collection_info(s3_url, user_info["name"],
                                do_decrypt(db.get_password(token)), found_coll['bucket'],
                                found_coll)

    S3Connection.save_collection_permissions(s3_url, user_info["name"],
                                do_decrypt(db.get_password(token)), found_coll['bucket'],
                                col_all_perms)

    # Update the collection to reflect the changes
    updated_collection = S3Connection.get_collection_info(s3_url, user_info["name"], \
                                                    do_decrypt(db.get_password(token)), s3_bucket)
    if updated_collection:
        updated_collection = normalize_collection(updated_collection)

        # Check if we have a stored temporary file containing the collections information
        return_colls = load_timed_temp_colls(user_info['name'])
        if return_colls:
            return_colls = [one_coll if one_coll['bucket'] != s3_bucket else updated_collection \
                                                                    for one_coll in return_colls ]
            # Save the collections temporarily
            save_timed_temp_colls(return_colls)

    return {'success':True, 'data': updated_collection, \
            'message': "Successfully updated the collection"}


@app.route('/adminCompleteChanges', methods = ['PUT'])
@cross_origin(origins="http://localhost:3000")#, supports_credentials=True)
def admin_complete_changes():
    """ Adds/updates a saved location and species information
    Arguments: (GET)
        t - the session token
    Return:
        Returns True if the collection changes were made
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('ADMIN COMPLETE THE CHANGES', flush=True)

    # Check what we have from the requestor
    if token is None:
        return "Not Found", 406

    # Check the rest of what we got
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the locations and species changes logged in the database
    s3_url = web_to_s3_url(user_info["url"])

    changes = db.get_admin_changes(user_info["url"], user_info['name'])
    if not changes:
        return {'success': True, 'message': "There were no changes found to apply"}

    # Update the location
    if 'locations' in changes and changes['locations']:
        if not update_admin_locations(s3_url, user_info['name'],do_decrypt(db.get_password(token)),
                                      changes):
            return 'Unable to update the locations', 422
    # Mark the locations as done in the DB
    db.clear_admin_location_changes(user_info["url"], user_info['name'])

    # Update the species
    if 'species' in changes and changes['species']:
        if not update_admin_species(s3_url, user_info['name'],do_decrypt(db.get_password(token)),
                                    changes):
            return 'Unable to update the species. Any changed locations were updated', 422
    # Mark the species as done in the DB
    db.clear_admin_species_changes(user_info["url"], user_info['name'])

    return {'success': True, 'message': "All changes were successully applied"}

@app.route('/adminAbandonChanges', methods = ['PUT'])
@cross_origin(origins="http://localhost:3000")#, supports_credentials=True)
def admin_abandon_changes():
    """ Adds/updates a saved location and species information
    Arguments: (GET)
        t - the session token
    Return:
        Returns True if the collection changes were abandoned
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('ADMIN ABANDON THE CHANGES', flush=True)

    # Check what we have from the requestor
    if token is None:
        return "Not Found", 406

    # Check the rest of what we got
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Mark the locations as done in the DB
    db.clear_admin_location_changes(user_info["url"], user_info['name'])

    # Mark the species as done in the DB
    db.clear_admin_species_changes(user_info["url"], user_info['name'])

    return {'success': True, 'message': "All changes were successully abandoned"}
