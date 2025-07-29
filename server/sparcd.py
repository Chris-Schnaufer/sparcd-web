#!/usr/bin/python3
"""This script contains the API for the SPARC'd server
"""

import concurrent.futures
import datetime
import hashlib
import io
import json
from multiprocessing import connection, Lock, Semaphore, synchronize
import os
import re
import shutil
import sys
import tempfile
import threading
import time
import traceback
from typing import Optional
from urllib.parse import urlparse, quote as urlquote
import uuid
import zipfile
from cachelib.file import FileSystemCache
import dateutil.parser
import dateutil.tz
from PIL import Image

import requests
from cryptography.fernet import Fernet
from minio import Minio
from minio.error import MinioException
from flask import Flask, abort, render_template, request, Response, send_file, send_from_directory,\
                  session, url_for
from flask_cors import CORS, cross_origin
from flask_session import Session

from text_formatters.results import Results
from text_formatters.coordinate_utils import deg2utm, SOUTHERN_AZ_UTM_ZONE
import query_helpers
from sparcd_db import SPARCdDatabase
from sparcd_utils import get_fernet_key_from_passcode
from s3_access import S3Connection

# Our prefix
SPARCD_PREFIX = 'sparcd_'

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
# Environment variable name for session storage folder
ENV_NAME_SESSION_PATH = 'SPARCD_SESSION_FOLDER'
# Environment variable name for session expiration timeout
ENV_NAME_SESSION_EXPIRE = 'SPARCD_SESSION_TIMEOUT'
# Default timeout in seconds
SESSION_EXPIRE_DEFAULT_SEC = 10 * 60 * 60
# Working database storage path
DEFAULT_DB_PATH = os.environ.get(ENV_NAME_DB,  None)
# Working session storage path
DEFAULT_SESSION_PATH = os.environ.get(ENV_NAME_SESSION_PATH, tempfile.gettempdir())
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

# Environment varriable for where to find the UI
ENV_NAME_BUILD_FOLDER = 'SPARCD_BUILD'
# Default path to the UI build
BUILD_FOLDER_DEFAULT = os.path.join(os.getcwd(), 'out')
# Working amount of time after last action before session is expired
WORKING_BUILD_PATH = os.environ.get(ENV_NAME_BUILD_FOLDER, BUILD_FOLDER_DEFAULT)
# UI definitions for serving
DEFAULT_TEMPLATE_PAGE = 'index.html'

# List of known query form variable keys
KNOWN_QUERY_KEYS = ['collections','dayofweek','elevations','endDate','hour','locations',
                    'month','species','startDate','years']

# Camtrap file names
DEPLOYMENT_CSV_NAME = 'deployments.csv'
MEDIA_CSV_NAME = 'media.csv'
CAMTRAP_FILES = [DEPLOYMENT_CSV_NAME, MEDIA_CSV_NAME, 'observations.csv']

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
    SESSION_COOKIE_SECURE=True,         # TODO: Change to True when running over HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=600,
)
SESSION_TYPE = 'filesystem'
SESSION_SERIALIZATION_FORMAT = 'json'
SESSION_CACHELIB = FileSystemCache(threshold=500, cache_dir=DEFAULT_SESSION_PATH)
app.config.from_object(__name__)
Session(app)

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
    if not url.lower().startswith('http'):
        return url

    parsed = urlparse(url)
    port = '80'
    if parsed.scheme.lower() == 'https':
        port = '443'

    return parsed.hostname + ':' + port


def token_is_valid(token:str, client_ip: str, user_agent: str, db: SPARCdDatabase) -> bool:
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
    if login_info and 'settings' in login_info:
        login_info['settings'] = json.loads(login_info['settings'])
    print('USER INFO',login_info,flush=True)
    if login_info is not None:
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
        if 'all_permissions' in one_coll and one_coll['all_permissions']:
            try:
                for one_perm in one_coll['all_permissions']:
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


def load_locations(s3_url: str, user_name: str, user_token: str) -> tuple:
    """ Loads locations and converts lat-lon to UTM
    Arguments:
        s3_url - the URL to the S3 instance
        user_name - the user's name for S3
        user_token - the users security token
    Return:
        Returns the locations along with the converted coordinates
    """
    cur_locations = load_sparcd_config('locations.json', TEMP_LOCATIONS_FILE_NAME, s3_url, \
                                            user_name, user_token)
    if not cur_locations:
        return cur_locations

    for one_loc in cur_locations:
        if 'utm_code' not in one_loc or 'utm_x' not in one_loc or 'utm_y' not in one_loc:
            if 'latProperty' in one_loc and 'lngProperty' in one_loc:
                utm_x, utm_y = deg2utm(float(one_loc['latProperty']), float(one_loc['lngProperty']))
                one_loc['utm_code'] = SOUTHERN_AZ_UTM_ZONE
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
        uploads_info = db.get_uploads(cur_bucket, TIMEOUT_UPLOADS_SEC)
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
            cur_futures = {executor.submit(list_uploads_thread, s3_url, user_name, \
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
                        db.save_uploads(uploads_results['bucket'], uploads_info)

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


def create_deployment_data(collection_id: str, location_id: str, all_locations: tuple) -> tuple:
    """ Returns the tuple containing the deployment data
    Arguments:
        collection_id: the ID of the collection (used for unique names)
        location_id: the ID of the location to use
        all_locations: the list of available locations
    Return:
        A tuple containing the deployment data
    """
    our_location = [one_loc for one_loc in all_locations if one_loc['idProperty'] == location_id]
    if our_location:
        our_location = our_location[0]
    else:
        our_location = {'nameProperty':'Unknown', 'idProperty':'unknown',
                                    'latProperty':0.0, 'lngProperty':0.0, 'elevationProperty':0.0,
                                    'utm_code':SOUTHERN_AZ_UTM_ZONE, 'utm_x':0.0, 'utm_y':0.0}

    return [    collection_id + ':' + location_id,      # Deployment id
                our_location['idProperty'],             # Location ID
                our_location['nameProperty'],           # Location name
                str(our_location['latProperty']),       # Location latitude
                str(our_location['lngProperty']),       # Location longitude
                "0",                                    # Coordinate uncertainty
                '',                                     # Start timestamp
                '',                                     # End timestamp
                '',                                     # Setup ID
                '',                                     # Camera ID
                '',                                     # Camera model
                "0",                                    # Camera interval
                str(our_location['elevationProperty']), # Camera height (elevation)
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
            '',                                     # Count
            '',                                     # Count new species
            '',                                     # Life stage
            '',                                     # Sex
            '',                                     # Behaviour
            '',                                     # Individual ID
            '',                                     # Classification method
            '',                                     # Classified by
            '',                                     # Classification timestmp
            '',                                     # Classification confidence
            '',                                     # Comments
            )
        for one_file in all_files
        ]


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
            'date': upload_entry['info']['uploadDate']
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
        print('HACK: ITEM:',one_item,flush=True)
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
            coll_uploads[bucket]['uploads'].append()
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
    curtime = None
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
            curtime = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()
            # Everything checks out
            # Update our session information
            session['key'] = token
            session['last_access'] = curtime
            return json.dumps({'value':token, 'name':login_info['name'],
                               'settings':login_info['settings'],
                               'admin':login_info['admin']})

        # Delete the old token from the database
        db.reconnect()
        db.remove_token(token)

        # Token not valid and not all login components specified
        if not url or not user or not password:
            return "Not Found", 404

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

    if not curtime:
        curtime = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()

    # Save information into the database
    new_key = uuid.uuid4().hex
    db.reconnect()
    # TODO Move the encryption to S3 instance & pass in the encryption key
    db.add_token(token=new_key, user=user, password=do_encrypt(password), client_ip=client_ip, \
                    user_agent=user_agent_hash, s3_url=s3_url)
    user_info = db.get_user(user)
    if not user_info:
        user_info = db.auto_add_user(user)

    # We have a new login, save everything
    session.clear()
    session['last_access'] = curtime
    session['key'] = new_key
    session.permanent = True
    # TODO: https://flask-session.readthedocs.io/en/latest/security.html#session-fixation
    #base.ServerSideSession.session_interface.regenerate(session)

    return json.dumps({'value':session['key'], 'name':user_info['name'],
                       'settings':user_info['settings'], 'admin':user_info['admin']})


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
    db = SPARCdDatabase(DEFAULT_DB_PATH)

    token = request.args.get('t')
    if not token:
        return "Not Found", 404

    print('COLLECTIONS', request, flush=True)
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

    # Check if we have a stored temporary file containing the collections information
    # and return that
    return_colls = load_timed_temp_colls(user_info['name'])
    if return_colls:
        return json.dumps(return_colls)

    # Get the collection information from the server
    s3_url = web_to_s3_url(user_info["url"])
    # TODO: have s3 instance do the decryption & pass in decrypt key to S3 instance
    all_collections = S3Connection.get_collections(s3_url, user_info["name"], \
                                                            do_decrypt(db.get_password(token)))

    return_colls = []
    for one_coll in all_collections:
        return_colls.append(normalize_collection(one_coll))

    # Everything checks out
    curtime = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()
    # Update our session information
    session['last_access'] = curtime

    # Save the collections temporarily
    save_timed_temp_colls(return_colls)

    # Return the collections
    return json.dumps(return_colls)


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

    token = request.args.get('t')
    if not token:
        return "Not Found", 404

    print('SANDBOX', request, flush=True)
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
    sandbox_items = db.get_sandbox()

    # The S3 endpoint in case we need it
    s3_url = web_to_s3_url(user_info["url"])

    # Get the collections to fill in the return data
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
    cur_species = load_sparcd_config('species.json', TEMP_SPECIES_FILE_NAME, s3_url, \
                                            user_info["name"], do_decrypt(db.get_password(token)))
    # Return the collections
    return json.dumps(cur_species)


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

    # Reload the saved information
    all_images = None
    if os.path.exists(save_path):
        all_images = load_timed_info(save_path)
        if all_images is not None:
            all_images = [all_images[one_key] for one_key in all_images.keys()]

    if all_images is None:
        # Get the collection information from the server
        s3_url = web_to_s3_url(user_info["url"])
        all_images = S3Connection.get_images(s3_url, user_info["name"], \
                                                do_decrypt(db.get_password(token)), \
                                                collection_id, collection_upload)

        # Save the images so we can reload them later
        save_timed_info(save_path, {one_image['key']: one_image for one_image in all_images})

    # Everything checks out
    curtime = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()
    # Update our session information
    session['last_access'] = curtime

    # Prepare the return data
    for one_img in all_images:
        one_img['url'] = url_for('image', _external=True,
                                    i=do_encrypt(json.dumps({ 'k':one_img["key"],
                                                              'p':save_path
                                                             })))
        del one_img['bucket']
        del one_img['s3_path']
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
    token = None
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
            case 'token':
                token = value
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
    all_results = filter_collections(db, cur_coll, s3_url, user_info["name"], token, filters)

    # Get the species and locations
    cur_species = load_sparcd_config('species.json', TEMP_SPECIES_FILE_NAME, s3_url, \
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

    if modified:
        db.update_user_settings(user_info['name'], json.dumps(user_info['settings']))

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
    if not token or not loc_id or not loc_name or not loc_lat or not loc_lon or not loc_ele:
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
                            'utm_code':SOUTHERN_AZ_UTM_ZONE, 'utm_x':0.0, 'utm_y':0.0})


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
    elapsed_sec, uploaded_files, upload_id = db.sandbox_get_upload(user_info['name'],
                                                                                    rel_path, True)

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
    if not token or not location_id or not collection_id or not comment or not rel_path or \
            not all_files or not timestamp or not timezone:
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
        print('HACK:   FILE:',all_files[0])
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
    for one_file in CAMTRAP_FILES:
        if one_file == DEPLOYMENT_CSV_NAME:
            data = ','.join(create_deployment_data(s3_bucket[len(SPARCD_PREFIX):], location_id,
                                                                                    cur_locations))
        elif one_file == MEDIA_CSV_NAME:
            data = '\n'.join([','.join(one_media) for one_media in \
                                    create_media_data(s3_bucket[len(SPARCD_PREFIX):], location_id,
                                                                            s3_path, all_files)])
        else:
            data = '\n'.join([','.join(one_media) for one_media in \
                                    create_observation_data(s3_bucket[len(SPARCD_PREFIX):], location_id,
                                                                            s3_path, all_files)])

        S3Connection.upload_file_data(s3_url, user_info["name"],
                                        do_decrypt(db.get_password(token)), s3_bucket,
                                        s3_path + '/' + one_file, data, 'application/csv')

    # Add the entries to the database
    upload_id = db.sandbox_new_upload(user_info['name'], rel_path, all_files, s3_bucket, s3_path,
                                        location_id)

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
    s3_bucket, s3_path = db.sandbox_get_s3_info(user_info['name'], upload_id)
    s3_url = web_to_s3_url(user_info["url"])

    # Upload all the received files and update the database
    for one_file in request.files:
        print('HACK:   ONEFILE:',request.files[one_file].mimetype,request.files[one_file].content_type,flush=True)
        temp_file = tempfile.mkstemp(prefix=SPARCD_PREFIX)
        os.close(temp_file[0])

        request.files[one_file].save(temp_file[1])

        # Upload the file to S3
        S3Connection.upload_opened_file(s3_url, user_info["name"],
                                        do_decrypt(db.get_password(token)), s3_bucket,
                                        s3_path + '/' + request.files[one_file].filename,
                                        temp_file[1])

        # Update the database entry to show the file is uploaded
        db.sandbox_file_uploaded(user_info['name'], upload_id, request.files[one_file].filename)

        os.unlink(temp_file[1])

    return json.dumps({'success': True})


@app.route('/sandboxCounts', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def sandbox_counts():
    """ Returns the counts of the sandbox upload
    Arguments: (GET)
        t - the session token
    Return:
        Returns the success of storing the uploaded image
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

    # Mark the upload as completed
    db.sandbox_upload_complete(user_info['name'], upload_id)

    return json.dumps({'success': True})
