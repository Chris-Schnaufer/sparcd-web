#!/usr/bin/python3
"""This script contains the API for the SPARC'd server
"""

import datetime
import hashlib
import json
import os
import sys
import tempfile
import time
from typing import Optional
from urllib.parse import urlparse
import uuid
from cachelib.file import FileSystemCache
import dateutil.parser
from minio import Minio
from minio.error import MinioException
from flask import Flask, abort, request, session
from flask_cors import CORS, cross_origin
from flask_session import Session

from sparcd_db import SPARCdDatabase
from s3_access import S3Connection

# Environment variable name for database
DB_ENV_NAME = 'SPARCD_DB'
# Environment variable name for session storage folder
SESSION_PATH_ENV_NAME = 'SPARCD_SESSION_FOLDER'
# Environment variable name for session expiration timeout
SESSION_EXPIRE_ENV_NAME = 'SPARCD_SESSION_TIMEOUT'
# Default timeout in seconds
SESSION_EXPIRE_DEFAULT_SEC = 10 * 60 * 60
# Working database storage path
DB_PATH_DEFAULT = os.environ.get(DB_ENV_NAME,  None)
# Working session storage path
SESSION_PATH_DEFAULT = os.environ.get(SESSION_PATH_ENV_NAME, tempfile.gettempdir())
# Working amount of time after last action before session is expired
SESSION_EXPIRE_SECONDS = os.environ.get(SESSION_EXPIRE_ENV_NAME, SESSION_EXPIRE_DEFAULT_SEC)
# Name of temporary collections file
TEMP_COLLECTION_FILE_NAME = 'sparcd_coll.json'
# Number of seconds to keep the temporary file around before it's invalid
TEMP_COLLECTION_FILE_EXPIRE_SEC = 1 * 60 * 60
# Maximum number of times to try updating the temporary collections file
TEMP_COLLECTION_FILE_MAX_WRITE_TRIES = 20

# Don't run if we don't have a database
if not DB_PATH_DEFAULT or not os.path.exists(DB_PATH_DEFAULT):
    sys.exit(f'Database not found. Set {DB_ENV_NAME} environment variable to a valid file')

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
SESSION_CACHELIB = FileSystemCache(threshold=500, cache_dir=SESSION_PATH_DEFAULT)
app.config.from_object(__name__)
Session(app)

# Intialize the database connection
DB = SPARCdDatabase(DB_PATH_DEFAULT)
DB.connect()
# TODO: clean up old tokens
del DB
DB = None
print(f'Using database at {DB_PATH_DEFAULT}')

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
        client_ip: the client IP to check
        user_agent: the user agent value to check
        db: the database storing the token
    Returns:
        Returns True if the token is valid and False if not
    """
    # Get the user information using the token
    db.reconnect()
    login_info = db.get_token_user_info(token)
    print('USER INFO',login_info)
    if login_info is not None:
        # Is the session still good
        if abs(int(login_info['elapsed_sec'])) < SESSION_EXPIRE_SECONDS and \
           login_info['client_ip'] == client_ip and login_info['user_agent'] == user_agent:
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
            return_str += str(cur_date['year']) + '-' + str(cur_date['month']) + \
                          '-' + str(cur_date['day'])

    if 'time' in date_json and date_json['time']:
        cur_time = date_json['time']
        if 'hour' in cur_time and 'second' in cur_time:
            return_str += ' at ' + str(cur_time['hour']) + ':' + str(cur_time['second'])

    return return_str


def load_timed_temp_colls(user: str) -> Optional[list]:
    """ Loads collection information from a temporary file
    Arguments:
        user: username to find permissions for
    Return:
        Returns the loaded collection data if valid, otherwise None is returned
    """
    # pylint: disable=broad-exception-caught
    coll_file_path = os.path.join(tempfile.gettempdir(), TEMP_COLLECTION_FILE_NAME)
    if not os.path.exists(coll_file_path):
        return None

    with open(coll_file_path, 'r', encoding='utf-8') as infile:
        try:
            loaded_colls = json.loads(infile.read())
        except json.JSONDecodeError as ex:
            infile.close()
            print(f'WARN: Collections temporary file has invalid contents: {coll_file_path}')
            print(ex)
            print('      Removing invalid file')
            try:
                os.unlink(coll_file_path)
            except Exception as ex_2:
                print(f'Unable to remove bad temporary collections file: {coll_file_path}')
                print(ex_2)
            return None

    # Check if the contents are too old
    if not isinstance(loaded_colls, dict) or 'timestamp' not in loaded_colls or \
                                                    not loaded_colls['timestamp']:
        print(f'WARN: Collections temporary file has missing contents: {coll_file_path}')
        print('      Removing invalid file')
        try:
            os.unlink(coll_file_path)
        except Exception as ex:
            print(f'Unable to remove invalid temporary collections file: {coll_file_path}')
            print(ex)
        return None

    old_ts = dateutil.parser.isoparse(loaded_colls['timestamp'])
    ts_diff = datetime.datetime.utcnow() - old_ts

    if ts_diff.total_seconds() > TEMP_COLLECTION_FILE_EXPIRE_SEC:
        print('HACK: EXPIRED TEMP FILE')
        try:
            os.unlink(coll_file_path)
        except Exception as ex:
            print(f'Unable to remove expired temporary collections file: {coll_file_path}')
            print(ex)
        return None

    # Get this user's permissions
    user_coll = []
    for one_coll in loaded_colls['collections']:
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


def save_timed_temp_colls(colls: tuple) -> None:
    """ Attempts to save the collections to a temporary file on disk
    Arguments:
        colls: the collection information to save
    """
    # pylint: disable=broad-exception-caught
    coll_file_path = os.path.join(tempfile.gettempdir(), TEMP_COLLECTION_FILE_NAME)
    if os.path.exists(coll_file_path):
        try:
            os.unlink(coll_file_path)
        except Exception as ex:
            print(f'Unable to remove old temporary collections file: {coll_file_path}')
            print(ex)
            print('Continuing to try updating the file')

    attempts = 0
    informed_exception = False
    collection_info = {'timestamp':datetime.datetime.utcnow().isoformat(),
                       'collections':colls
                      }
    while attempts < TEMP_COLLECTION_FILE_MAX_WRITE_TRIES:
        try:
            with open(coll_file_path, 'w', encoding='utf-8') as outfile:
                outfile.write(json.dumps(collection_info))
            attempts = TEMP_COLLECTION_FILE_MAX_WRITE_TRIES
        except Exception as ex:
            if not informed_exception:
                print(f'Unable to open temporary collection file for writing: {coll_file_path}')
                print(ex)
                print(f'Will keep trying for up to {TEMP_COLLECTION_FILE_MAX_WRITE_TRIES} times')
                informed_exception = True
                time.sleep(1)
            attempts = attempts + 1


@app.route('/login', methods = ['POST', 'GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def login_token():
    """Returns a token representing the login. No checks are made on the parameters
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
    db = SPARCdDatabase(DB_PATH_DEFAULT)

    print('LOGIN', request)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.remote_addr))
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
        print('TOKEN SESSION', session.get('key'), token, session.get('last_access'))
        # See if the session is still valid
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
        print('DELETING OLD TOKEN', token)
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
    # TODO: SECURE PASSWORD
    db.add_token(token=new_key, user=user, password=password, client_ip=client_ip, \
                    user_agent=user_agent_hash, s3_url=s3_url)
    user_info = db.get_user(user)

    # We have a new login, save everything
    session.clear()
    session['last_access'] = curtime
    session['key'] = new_key
    session.permanent = True
    # TODO: https://flask-session.readthedocs.io/en/latest/security.html#session-fixation
    #base.ServerSideSession.session_interface.regenerate(session)

    print(json.dumps({'value':session['key']}))
    return json.dumps({'value':session['key'], 'name':user_info['name'],
                       'settings':user_info['settings'], 'admin':user_info['admin']})


@app.route('/collections', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def collections():
    """Returns a token representing the login. No checks are made on the parameters
    Arguments: (GET)
        token - the session token
    Return:
        Returns the list of accessible collections
    Notes:
        If the token is invalid a 404 error is returned
    """
    db = SPARCdDatabase(DB_PATH_DEFAULT)

    token = request.args.get('token')

    print(('COLLECTIONS', request), flush=True)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.remote_addr))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found 1", 404
    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()

    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
    if not token_valid or not user_info:
        return "Not Found 2", 404

    # Check if we have a stored temporary file containing the collections information
    # and return that
    return_colls = load_timed_temp_colls(user_info['name'])
    if return_colls:
        return json.dumps(return_colls)

    # Get the collection information from the server
    s3_url = web_to_s3_url(user_info["url"])
    print('GETTING COLLECTIONS',flush=True)
    all_collections = S3Connection.get_collections(s3_url, user_info["name"], \
                                                                db.get_password(token))
    print('   ',all_collections,flush=True)

    return_colls = []
    for one_coll in all_collections:
        cur_col = { 'name': one_coll['nameProperty'],
                    'bucket': one_coll['bucket'],
                    'organization': one_coll['organizationProperty'],
                    'email': one_coll['contactInfoProperty'],
                    'description': one_coll['descriptionProperty'],
                    'id': one_coll['idProperty'],
                    'permissions': one_coll['permissions'],
                    'uploads': []
                  }
        cur_uploads = []
        for one_upload in one_coll['uploads']:
            print('UPLOAD',one_upload.keys(), one_upload, flush=True)
            print('      ',one_upload['info'].keys(), one_upload['info'], flush=True)
            cur_uploads.append({'name': one_upload['info']['uploadUser'] + ' on ' + \
                                                get_upload_date(one_upload['info']['uploadDate']),
                                'description': one_upload['info']['description'],
                                'imagesCount': one_upload['info']['imageCount'],
                                'imagesWithSpeciesCount': one_upload['info']['imagesWithSpecies'],
                                'location': '',
                                'edits': one_upload['info']['editComments']
                              })
        cur_col['uploads'] = cur_uploads
        return_colls.append(cur_col)

    # Everything checks out
    curtime = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()
    # Update our session information
    session['last_access'] = curtime

    # Save the collections temporarily
    save_timed_temp_colls(return_colls)

    # Return the collections
    return json.dumps(return_colls)
