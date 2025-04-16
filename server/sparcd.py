#!/usr/bin/python3
"""This script contains the API for the SPARC'd server
"""

import datetime
import json
import os
import tempfile
import uuid
from cachelib.file import FileSystemCache
from flask import Flask, abort, request, session
from flask_cors import CORS, cross_origin
from flask_session import Session

# Environment variable name for session storage folder
SESSION_DIR_ENV_NAME = 'SPARCD_SESSION_FOLDER'
# Environment variable name for session expiration timeout
SESSION_EXPIRE_ENV_NAME = 'SPARCD_SESSION_TIMEOUT'
# Default session storage path
SESSION_DIR_DEFAULT = os.environ.get(SESSION_DIR_ENV_NAME, tempfile.gettempdir())
# Default timeout in seconds
SESSION_EXPIRE_DEFAULT_SEC = 10 * 60 * 60
# Amount of time after last action before session is expired
SESSION_EXPIRE_SECONDS = os.environ.get(SESSION_EXPIRE_ENV_NAME, SESSION_EXPIRE_DEFAULT_SEC)

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
SESSION_CACHELIB = FileSystemCache(threshold=500, cache_dir=SESSION_DIR_DEFAULT)
app.config.from_object(__name__)
Session(app)

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
        Returns the session key, None, or 'invalid'. 
        None means the session has expired.
        'invalid' indicates a required parameter value was not specified
    Notes:
        All parameters can be specified. If a token is specified, it's checked
        for expiration first. If login information is specified, and the token
        is invalid/missing/expired, a new token is returned
    """
    curtime = None

    print('LOGIN', request, request.environ)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', request.remote_addr))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

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
        # Check the previous IP address for validity
        print('CLIENT_IP', 'client_ip' in session, session.get('client_ip'))
        print('CLIENT_USER_AGENT', 'client_user_agent' in session, session.get('client_user_agent'))
        if session.get('client_ip') is not None and session.get('client_ip') == client_ip \
           and session.get('client_user_agent') is not None and session.get('client_user_agent') == client_user_agent:
            # Checking the token for validity
            if session.get('key') == token and session.get('last_access') is not None:
                curtime = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
                before = datetime.datetime.fromtimestamp(session['last_access'])
                # Is the session still good? Update last access timestamp
                if abs(curtime - before) < SESSION_EXPIRE_SECONDS:
                    session['last_access'] = curtime
                    return json.dumps({'value': token})
        # Token not valid and not all login components specified
        print('URL', url);
        print('USER', url);
        print('PASSWORD', url);
        if not url or not user or not password:
            return "Not Found", 404

    return json.dumps({'value':'ABCDE'})
    # Make sure we have the components we need for logging in
    if not url or not user or not password:
        return "Not Found", 404

    if not curtime:
        curtime = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp()

    session.clear()
    session['last_access'] = curtime
    session['url'] = url
    session['user'] = user
    session['password'] = password
    session['client_ip'] = client_ip
    session['client_user_agent'] = client_user_agent
    session['key'] = uuid.uuid4().hex
    session.permanent = True
    # TODO: https://flask-session.readthedocs.io/en/latest/security.html#session-fixation
    #base.ServerSideSession.session_interface.regenerate(session)

    print(json.dumps({'value':session['key']}))
    return json.dumps({'value':session['key']})
