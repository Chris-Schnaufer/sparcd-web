#!/usr/bin/python3
"""This script contains the API for the SPARC'd server
"""

import datetime
import hashlib
import json
import os
import sys
import tempfile
from urllib.parse import urlparse
import uuid
from cachelib.file import FileSystemCache
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
    port = 80
    if parsed.scheme.lower() == 'https':
        port = 443

    return parsed.hostname + port


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

    print('COLLECTIONS', request)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.remote_addr))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404
    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()

    token_valid, user_info = token_is_valid(token, client_ip, user_agent_hash, db)
#    if not token_valid or not user_info:
#        return "Not Found", 404

    # Get the collection information from the server
    s3_url = web_to_s3_url(user_info.url)
    all_collections = S3Connection.get_collections(s3_url, user_info.name, user_info.password)

    return_colls = []
    for one_coll in all_collections:
        cur_col = { 'name': one_coll['nameProperty'],
                    'bucket': one_coll['bucket'],
                    'organization': one_coll['organizationProperty'],
                    'email': one_coll['contactInfoProperty'],
                    'description': one_coll['descriptionProperty'],
                    'id': one_coll['idProperty'],
                    'uploads': []
                  }
        cur_uploads = []
        for one_upload in cur_col['uploads']:
            cur_uploads.append({'name': one_upload['name'],
                                'description': one_upload['description'],
                                'imagesCount': one_upload['imageCount'],
                                'imagesWithSpeciesCount': one_upload['imagesWithSpecies'],
                                'location': '',
                                'edits': one_upload['editComments']
                              })
        cur_col['uploads'] = cur_uploads
        return_colls.append(cur_col)

    # Everything checks out
    curtime = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()
    # Update our session information
    session['last_access'] = curtime

    # Return the collections
    return json.dumps(return_colls)
