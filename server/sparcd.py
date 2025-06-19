#!/usr/bin/python3
"""This script contains the API for the SPARC'd server
"""

import datetime
import hashlib
import io
import json
import os
import sys
import tempfile
import time
from typing import Optional
from urllib.parse import urlparse, quote as urlquote
import uuid
from cachelib.file import FileSystemCache
import dateutil.parser
from PIL import Image

import requests
from cryptography.fernet import Fernet
from minio import Minio
from minio.error import MinioException
from flask import Flask, abort, render_template, request, send_file, send_from_directory, session, \
                  url_for
from flask_cors import CORS, cross_origin
from flask_session import Session

from text_formatters.results import Results
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
            return_str += str(cur_date['year']) + '-' + str(cur_date['month']) + \
                          '-' + str(cur_date['day'])

    if 'time' in date_json and date_json['time']:
        cur_time = date_json['time']
        if 'hour' in cur_time and 'minute' in cur_time:
            return_str += ' at ' + str(cur_time['hour']) + ':' + str(cur_time['minute'])

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
    loaded_colls = load_timed_info(coll_file_path)
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


def load_timed_info(load_path: str):
    """ Loads the timed data from the specified file
    Arguments:
        load_path: the path to load data from
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

    if ts_diff.total_seconds() > TEMP_FILE_EXPIRE_SEC:
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


@app.route('/', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def index():
    """Default page"""
    print("RENDERING TEMPLATE",DEFAULT_TEMPLATE_PAGE,os.getcwd(),flush=True)
    return render_template(DEFAULT_TEMPLATE_PAGE)


@app.route('/favicon.ico', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def favicon():
    """ Return the favicon """
    return send_from_directory(os.path.join(app.root_path, 'static'),
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

    # Make sure we're only serving something that's in the same location that we are in and that it exists
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

    fullpath = os.path.realpath(os.path.join(RESOURCE_START_PATH, '_next','static',path_fagment.lstrip('/')))
    print("   FILE PATH:", fullpath,flush=True)

    # Make sure we're only serving something that's in the same location that we are in and that it exists
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

    # Make sure we're only serving something that's in the same location that we are in and that it exists
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

    imgByteArr = io.BytesIO()
    img.save(imgByteArr, image_type.upper(), quality=q_param)
    
    imgByteArr.seek(0)  # move to the beginning of file after writing
    
    return send_file(imgByteArr, mimetype="image/" + image_type.lower())



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
        print('HACK:     AUTO ADDING USER',user,flush=True)
        user_info = db.auto_add_user(user)
        print('HACK:       ',user_info,flush=True)

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

    token = request.args.get('token')
    if not token:
        return "Not Found", 404

    print(('COLLECTIONS', request), flush=True)
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
        last_upload_date = None
        for one_upload in one_coll['uploads']:
            last_upload_date = get_later_timestamp(last_upload_date, one_upload['info']['uploadDate'])
            cur_uploads.append({'name': one_upload['info']['uploadUser'] + ' on ' + \
                                                get_upload_date(one_upload['info']['uploadDate']),
                                'description': one_upload['info']['description'],
                                'imagesCount': one_upload['info']['imageCount'],
                                'imagesWithSpeciesCount': one_upload['info']['imagesWithSpecies'],
                                'location': one_upload['location'],
                                'edits': one_upload['info']['editComments'],
                                'key': one_upload['key']
                              })
        cur_col['uploads'] = cur_uploads
        cur_col['last_upload_ts'] = last_upload_date
        return_colls.append(cur_col)

    # Everything checks out
    curtime = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()
    # Update our session information
    session['last_access'] = curtime

    # Save the collections temporarily
    save_timed_temp_colls(return_colls)

    # Return the collections
    return json.dumps(return_colls)


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

    token = request.args.get('token')
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

    # Allow a timely request from everywhere
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
    all_results = []
    for one_coll in cur_coll:
        cur_bucket = one_coll['json']['bucketProperty']
        uploads_info = db.get_uploads(cur_bucket, TIMEOUT_UPLOADS_SEC)
        if uploads_info is not None and uploads_info:
            uploads_info = [{'bucket':cur_bucket,       \
                             'name':one_upload['name'],                     \
                             'info':json.loads(one_upload['json'])}         \
                                    for one_upload in uploads_info]
        else:
            uploads_info = S3Connection.list_uploads(s3_url, \
                                                user_info["name"], \
                                                do_decrypt(db.get_password(token)), \
                                                cur_bucket)
            if len(uploads_info) > 0:
                uploads_info = [{'bucket':cur_bucket,
                                 'name':one_upload['name'],
                                 'info':one_upload,
                                 'json':json.dumps(one_upload)
                                } for one_upload in uploads_info]
                db.save_uploads(one_coll['json']['bucket'], uploads_info)

        # Filter on current uploads
        if len(uploads_info) > 0:
            cur_results = query_helpers.filter_uploads(uploads_info, filters)
            if cur_results:
                all_results = all_results + cur_results

    # Get the species and locations
    species = load_sparcd_config('species.json', TEMP_SPECIES_FILE_NAME, s3_url, \
                                            user_info["name"], do_decrypt(db.get_password(token)))
    locations = load_sparcd_config('locations.json', TEMP_LOCATIONS_FILE_NAME, s3_url, \
                                            user_info["name"], do_decrypt(db.get_password(token)))

    results = Results(all_results, species, locations,
                        s3_url, user_info["name"], do_decrypt(db.get_password(token)),
                        60) # TODO: add query interval

    # Format and return the results
    return_info = query_helpers.query_output(results)
    return json.dumps(return_info)
