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
import threading
from typing import Optional
import uuid
import dateutil.parser
import dateutil.tz
from PIL import Image

import requests
from minio import Minio
from minio.error import MinioException
from flask import Flask, render_template, request, Response, send_file, send_from_directory,\
                  url_for
from flask_cors import cross_origin

import spd_crypt as crypt
from camtrap.v016 import camtrap
import camtrap_utils as ctu
import image_utils
import query_helpers
import query_utils
from sparcd_db import SPARCdDatabase
import sparcd_file_utils as sdfu
import sparcd_utils as sdu
from s3_access import S3Connection, make_s3_path, DEPLOYMENT_CSV_FILE_NAME, MEDIA_CSV_FILE_NAME, \
                      OBSERVATIONS_CSV_FILE_NAME, CAMTRAP_FILE_NAMES, SPARCD_PREFIX, \
                      S3_UPLOADS_PATH_PART, SPECIES_JSON_FILE_NAME
import s3_utils as s3u
from text_formatters.results import Results
from text_formatters.coordinate_utils import DEFAULT_UTM_ZONE,deg2utm, deg2utm_code, utm2deg
import zip_utils as zu


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
# Collection table timeout length
TIMEOUT_COLLECTIONS_SEC = 12 * 60 * 60
# Timeout for one upload folder file information
TIMEOUT_UPLOADS_FILE_SEC = 15 * 60
# Timeout for query results on disk
QUERY_RESULTS_TIMEOUT_SEC = 24 * 60 * 60

# Convertion factor of feet to metes
FEET_TO_METERS = 0.3048000097536

# Name of temporary species file
TEMP_SPECIES_FILE_NAME = SPARCD_PREFIX + 'species.json'

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
WORKING_PASSCODE=crypt.get_fernet_key_from_passcode(CURRENT_PASSCODE)

# Initialize server
app = Flask(__name__)
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
del DB
DB = None
print(f'Using database at {DEFAULT_DB_PATH}', flush=True)
print(f'Temporary folder at {tempfile.gettempdir()}', flush=True)


def get_password(token: str, db: SPARCdDatabase) -> Optional[str]:
    """ Returns the password associated with the token in plain text
    Arguments:
        token: the user's token
        db: the database instance
    Return:
        The plain text password
    """
    return crypt.do_decrypt(WORKING_PASSCODE, db.get_password(token))


@app.route('/', methods = ['GET'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def index():
    """Default page"""
    print("RENDERING TEMPLATE",DEFAULT_TEMPLATE_PAGE,os.getcwd(),flush=True)
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent == '-':
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
    print("HACK:   FILE PATH:", fullpath,flush=True)

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
    print("HACK:   FILE PATH:", fullpath,flush=True)

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
        token_valid, login_info = sdu.token_is_valid(token, client_ip, user_agent_hash, db,
                                                                            SESSION_EXPIRE_SECONDS)
        if token_valid:
            # Everything checks out
            return json.dumps(
                {  'value':token,
                   'name':login_info.name,
                   'settings': \
                        sdu.secure_user_settings(login_info.settings|{'email':login_info.email})
               })

        # Delete the old token from the database
        db.reconnect()
        db.remove_token(token)

    # Make sure we have the components we need for logging in
    if not url or not user or not password:
        return "Not Found", 404

    # Log onto S3 to make sure the information is correct
    try:
        s3_url = s3u.web_to_s3_url(url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
        minio = Minio(s3_url, access_key=user, secret_key=password)
        _ = minio.list_buckets()
    except MinioException as ex:
        print('S3 exception caught:', ex, flush=True)
        return "Not Found", 404

    # Save information into the database - also cleans up old tokens if there's too many
    new_key = uuid.uuid4().hex
    db.reconnect()
    db.add_token(token=new_key, user=user, password=crypt.do_encrypt(WORKING_PASSCODE, password),
                    client_ip=client_ip, user_agent=user_agent_hash,
                    s3_url=crypt.do_encrypt(WORKING_PASSCODE, s3_url),
                    token_timeout_sec=SESSION_EXPIRE_SECONDS)
    user_info = db.get_user(user)
    if not user_info:
        # Get the species
        cur_species = s3u.load_sparcd_config(SPECIES_JSON_FILE_NAME, TEMP_SPECIES_FILE_NAME, s3_url,
                                                                            user, lambda: password)
        user_info = db.auto_add_user(user, species=json.dumps(cur_species))

    # Add in the email if we have user settings
    if user_info.settings:
        try:
            cur_settings = json.loads(user_info.settings)
            user_info.settings = cur_settings|{'email':user_info.email}
        except json.JSONDecodeError as ex:
            print('Unable to add email to user settings:', user_info, flush=True)
            print(ex)

    user_info.settings = sdu.secure_user_settings(user_info.settings)

    return json.dumps({'value':new_key, 'name':user_info.name,
                       'settings':user_info.settings})


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
    print('COLLECTIONS', flush=True)

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Check if we have a stored temporary file containing the collections information
    # and return that
    return_colls = sdu.load_timed_temp_colls(user_info.name, bool(user_info.admin))
    if return_colls:
        # Clear all permissions unless we're an owner
        for one_coll in return_colls:
            if not one_coll['permissions'] or not one_coll['permissions']['ownerProperty'] is True:
                del one_coll['allPermissions']
        return json.dumps(return_colls)

    # Get the collection information from the server
    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
    all_collections = S3Connection.get_collections(s3_url, user_info.name, get_password(token, db))

    return_colls = []
    for one_coll in all_collections:
        return_colls.append(sdu.normalize_collection(one_coll))

    # Save the collections temporarily
    sdu.save_timed_temp_colls(return_colls)

    # Return the collections
    if user_info.admin is True:
        # Filter out collections if not an admin
        return_colls = [one_coll for one_coll in return_colls if 'permissions' in one_coll and \
                                                                            one_coll['permissions']]
    return json.dumps([one_coll|{'allPermissions':None} for one_coll in return_colls])


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
    print('SANDBOX', request, flush=True)

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the sandbox information from the database
    sandbox_items = db.get_sandbox(user_info.url)

    # The S3 endpoint in case we need it
    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))

    # Get the collections to fill in the return data
    # TODO: combine this with a load from S3 if not found locally?
    all_collections = sdu.load_timed_temp_colls(user_info.name, bool(user_info.admin))

    return_sandbox = sdu.get_sandbox_collections(s3_url, user_info.name,
                                                get_password(token, db),
                                                sandbox_items, all_collections)

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
    print('LOCATIONS', request, flush=True)

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the locations to return
    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
    cur_locations = sdu.load_locations(s3_url, user_info.name, lambda: get_password(token, db))

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
    print('SPECIES', request, flush=True)

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the species to return
    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
    user_species = user_info.species

    # Get the current species to see if we need to update the user's species
    cur_species = s3u.load_sparcd_config(SPECIES_JSON_FILE_NAME, TEMP_SPECIES_FILE_NAME, s3_url, \
                                            user_info.name, lambda: get_password(token, db))

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
        db.save_user_species(user_info.name, species_json)
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
    print('UPLOAD', request, flush=True)

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Check the rest of the request parameters
    collection_id = request.args.get('id')
    collection_upload = request.args.get('up')

    if not collection_id or not collection_upload:
        return "Not Found", 406

    app.config['SERVER_NAME'] = request.host

    # Save path
    save_path = os.path.join(tempfile.gettempdir(), SPARCD_PREFIX + collection_id + '_' + \
                                                                collection_upload + '.json')

    # The URL to the S3 instance
    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))

    # Reload the saved information
    all_images = None
    if os.path.exists(save_path):
        # Get the images and flatten the structure as needed
        all_images = sdfu.load_timed_info(save_path, TIMEOUT_UPLOADS_FILE_SEC)
        if all_images is not None:
            all_images = [all_images[one_key] for one_key in all_images.keys()]

    if all_images is None:
        # Get the collection information from the server
        all_images = S3Connection.get_images(s3_url, user_info.name,
                                                get_password(token, db),
                                                collection_id, collection_upload)

        # Save the images so we can reload them later
        sdfu.save_timed_info(save_path, {one_image['key']: one_image for one_image in all_images})

    # Get species data from the database and update the images
    edits = {}
    for one_image in all_images:
        # Find any edits for this image
        upload_path = os.path.dirname(one_image['s3_path'])
        edit_key = one_image['bucket'] + ':' + upload_path
        if not edit_key in edits:
            edits = {**edits,
                     **db.get_image_species_edits(user_info.url, one_image['bucket'],upload_path)
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
                check_species = user_info.species
                if not check_species:
                    check_species = s3u.load_sparcd_config(SPECIES_JSON_FILE_NAME,
                                                        TEMP_SPECIES_FILE_NAME,
                                                        s3_url,
                                                        user_info.name,
                                                        lambda: get_password(token, db))


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
                                    i=crypt.do_encrypt(WORKING_PASSCODE,
                                                      json.dumps({ 'k':one_img["key"],
                                                                   'p':save_path
                                                                 })))
        one_img['s3_path'] = crypt.do_encrypt(WORKING_PASSCODE, one_img['s3_path'])
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

    # Check the credentials
    # We aren't concerned with the requestors origin IP
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_user_agent or client_user_agent is None:
        return "Not Found", 404
    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()

    # Allow a timely request from everywhere
    token_valid, user_info = sdu.token_is_valid(token, '*', user_agent_hash, db,
                                                                            SESSION_EXPIRE_SECONDS)
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Check the rest of the parameters
    try:
        image_req = json.loads(crypt.do_decrypt(WORKING_PASSCODE, request.args.get('i')))
    except json.JSONDecodeError:
        image_req = None

    # Check what we have from the requestor
    if not image_req or not isinstance(image_req, dict) or \
                not all(one_key in image_req.keys() for one_key in ('k','p')):
        return "Not Found", 406

    image_key = image_req['k']
    image_store_path = image_req['p']

    # Load the image data
    image_data = sdfu.load_timed_info(image_store_path)
    if image_data is None or not isinstance(image_data, dict):
        return "Not Found", 422

    # Get the url from the key
    if not image_key in image_data:
        return "Not Found", 422

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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Check the rest of the request parameters
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
    if have_error:
        print('INVALID QUERY:',token,have_error)
        return "Not Found", 406
    if not filters:
        print('NO FILTERS SPECIFIED')
        return "Not Found", 406

    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))

    # Get collections from the database
    coll_info = db.get_collections(TIMEOUT_COLLECTIONS_SEC)
    if coll_info is None or not coll_info:
        all_collections = S3Connection.list_collections(s3_url, user_info.name,
                                                        get_password(token, db))
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
    all_results = query_helpers.filter_collections(db, cur_coll,
                                            crypt.do_decrypt(WORKING_PASSCODE, user_info.url),
                                            user_info.name,
                                            lambda: get_password(token, db),
                                            filters)

    # Get the species and locations
    cur_species = s3u.load_sparcd_config(SPECIES_JSON_FILE_NAME, TEMP_SPECIES_FILE_NAME, s3_url,
                                            user_info.name, lambda: get_password(token, db))
    cur_locations = sdu.load_locations(s3_url, user_info.name, lambda: get_password(token, db))

    results = Results(all_results, cur_species, cur_locations,
                        s3_url, user_info.name, get_password(token, db),
                        user_info.settings, 60)

    # Format and return the results
    results_id = uuid.uuid4().hex
    return_info = query_helpers.query_output(results, results_id)

    # Check for old queries and clean them up
    sdu.cleanup_old_queries(db, token)

    # Save the query for lookup when downloading results
    save_path = os.path.join(tempfile.gettempdir(), SPARCD_PREFIX + 'query_' + \
                                                                results_id + '.json')
    sdfu.save_timed_info(save_path, return_info)
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
    print('QUERY DOWNLOAD', request, flush=True)

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Check the rest of the request parameters
    tab = request.args.get('q')
    target = request.args.get('d')

    # Check what we have from the requestor
    if not tab:
        return "Not Found", 406

    # Get the query information
    query_info_path, _ = db.get_query(token)
    print('           ',query_info_path, flush=True)

    # Try and load the query results
    query_results = sdfu.load_timed_info(query_info_path, QUERY_RESULTS_TIMEOUT_SEC)
    if not query_results:
        return "Not Found", 422

    match(tab):
        case 'DrSandersonOutput':
            dl_name = target if target else 'drsanderson.txt'
            return Response(query_results[tab],
                            mimetype='text/text',
                            headers={'Content-disposition': f'attachment; filename="{dl_name}"'})

        case 'DrSandersonAllPictures':
            dl_name = target if target else 'drsanderson_all.csv'
            return Response(query_utils.query_allpictures2csv(query_results[tab],
                                    user_info.settings,
                                    query_results['columsMods'][tab] if tab in \
                                                        query_results['columsMods'] else None),
                            mimetype='application/csv',
                            headers={'Content-disposition': f'attachment; filename="{dl_name}"'})

        case 'csvRaw':
            dl_name = target if target else 'allresults.csv'
            return Response(query_utils.query_raw2csv(query_results[tab],
                                    user_info.settings,
                                    query_results['columsMods'][tab] if tab in \
                                                        query_results['columsMods'] else None),
                            mimetype='text/csv',
                            headers={'Content-disposition': f'attachment; filename="{dl_name}"'})

        case 'csvLocation':
            dl_name = target if target else 'locations.csv'
            return Response(query_utils.query_location2csv(query_results[tab],
                                    user_info.settings,
                                    query_results['columsMods'][tab] if tab in \
                                                        query_results['columsMods'] else None),\
                            mimetype='text/csv',
                            headers={'Content-disposition': f'attachment; filename="{dl_name}"'})

        case 'csvSpecies':
            dl_name = target if target else 'species.csv'
            return Response(query_utils.query_species2csv(query_results[tab],
                                    user_info.settings,
                                    query_results['columsMods'][tab] if tab in \
                                                        query_results['columsMods'] else None),
                            mimetype='text/csv',
                            headers={'Content-disposition': f'attachment; filename="{dl_name}"'})

        case 'imageDownloads':
            dl_name = target if target else 'allimages.gz'
            s3_url = s3u.web_to_s3_url(user_info.url,
                                                    lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
            read_fd, write_fd = os.pipe()

            # Get and acqure the lock: indicates the files are downloaded when released
            # pylint: disable=consider-using-with
            download_finished_lock = threading.Semaphore(1)
            download_finished_lock.acquire()

            # Run the download and compression as a seperate process
            dl_thread = threading.Thread(target=zu.generate_zip,
                                 args=(s3_url, user_info.name,
                                       get_password(token, db),
                                       [row['name'] for row in query_results[tab]],
                                       write_fd, download_finished_lock)
                                )
            dl_thread.start()

            # Return the compressed data as an iterator over the data pipe
            return Response(zu.zip_iterator(read_fd),
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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Check the rest of the request parameters
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

    # Update any settings that have changed
    modified = False
    new_keys = tuple(new_settings.keys())
    for one_key in new_keys:
        if not one_key in user_info.settings or \
                                        not new_settings[one_key] == user_info.settings[one_key]:
            user_info.settings[one_key] = new_settings[one_key]
            modified = True
    if not new_email == user_info.email:
        user_info.email = new_email
        modified = True

    if modified:
        db.update_user_settings(user_info.name, json.dumps(user_info.settings), user_info.email)

    user_info.settings = sdu.secure_user_settings(user_info.settings|{'email':user_info.email})

    return json.dumps(user_info.settings)


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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Check the rest of the request parameters
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

    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
    cur_locations = sdu.load_locations(s3_url, user_info.name, lambda: get_password(token, db))

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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Check the rest of the request parameters
    rel_path = request.form.get('path', None)
    if not rel_path:
        return "Not Found", 406

    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('HTTP_ORIGIN', \
                                    request.environ.get('HTTP_REFERER',request.remote_addr) \
                                    ))
    client_user_agent =  request.environ.get('HTTP_USER_AGENT', None)
    if not client_ip or client_ip is None or not client_user_agent or client_user_agent is None:
        return "Not Found", 404

    user_agent_hash = hashlib.sha256(client_user_agent.encode('utf-8')).hexdigest()
    token_valid, user_info = sdu.token_is_valid(token, client_ip, user_agent_hash, db,
                                                                            SESSION_EXPIRE_SECONDS)
    if not token_valid or not user_info:
        return "Unauthorized", 401


    # Check with the DB if the upload has been started before
    elapsed_sec, uploaded_files, upload_id, _ = db.sandbox_get_upload(user_info.url,
                                                                                user_info.name,
                                                                                rel_path,
                                                                                True)
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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Check the rest of the request parameters
    location_id = request.form.get('location', None)
    collection_id = request.form.get('collection', None)
    comment = request.form.get('comment', None)
    rel_path = request.form.get('path', None)
    all_files = request.form.get('files', None)
    timestamp = request.form.get('ts', None)
    timezone = request.form.get('tz', None)

    # Check what we have from the requestor
    if not all(item for item in [location_id, collection_id, comment, rel_path, all_files, \
                                                                            timestamp, timezone]):
        return "Not Found", 406

    # Get all the file names
    try:
        all_files = json.loads(all_files)
    except json.JSONDecodeError as ex:
        print('ERROR: Unable to load file list JSON', ex, flush=True)
        return "Not Found", 406

    # Create the upload location
    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
    client_ts = datetime.datetime.fromisoformat(timestamp).astimezone(dateutil.tz.gettz(timezone))
    s3_bucket, s3_path = S3Connection.create_upload(s3_url, user_info.name,
                                        get_password(token, db), collection_id,
                                        comment, client_ts, len(all_files))

    # Upload the CAMTRAP files to S3 storage
    cur_locations = sdu.load_locations(s3_url, user_info.name, lambda: get_password(token, db))
    our_location = sdu.get_location_info(location_id, cur_locations)
    deployment_id = s3_bucket[len(SPARCD_PREFIX):] + ':' + location_id
    for one_file in CAMTRAP_FILE_NAMES:
        if one_file == DEPLOYMENT_CSV_FILE_NAME:
            data = ','.join(ctu.create_deployment_data(camtrap.CamTrap,deployment_id, our_location))
        elif one_file == MEDIA_CSV_FILE_NAME:
            media_data = ctu.create_media_data(camtrap.CamTrap, deployment_id, s3_path, all_files)

            data = '\n'.join([','.join(one_media) for one_media in media_data])
        else:
            data = '\n'.join([','.join(one_media) for one_media in \
                    ctu.create_observation_data(camtrap.CamTrap,deployment_id, s3_path, all_files)])

        S3Connection.upload_file_data(s3_url, user_info.name,
                                        get_password(token, db), s3_bucket,
                                        s3_path + '/' + one_file, data, 'application/csv')

    # Add the entries to the database
    upload_id = db.sandbox_new_upload(user_info.url, user_info.name, rel_path, all_files,
                                                                s3_bucket, s3_path,
                                                                our_location['idProperty'],
                                                                our_location['nameProperty'],
                                                                our_location['latProperty'],
                                                                our_location['lngProperty'],
                                                                our_location['elevationProperty'])

    # Update the collection to reflect the new upload
    updated_collection = S3Connection.get_collection_info(s3_url, user_info.name,
                                                    get_password(token, db),
                                                    s3_bucket)
    if updated_collection:
        updated_collection = sdu.normalize_collection(updated_collection)

        # Check if we have a stored temporary file containing the collections information
        return_colls = sdu.load_timed_temp_colls(user_info.name, bool(user_info.admin))
        if return_colls:
            return_colls = [one_coll if one_coll['bucket'] != s3_bucket else updated_collection \
                                                                    for one_coll in return_colls ]
            # Save the collections temporarily
            sdu.save_timed_temp_colls(return_colls)

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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the rest of the request parameters
    upload_id = request.form.get('id', None)

    # Check what we have from the requestor
    if not upload_id or len(request.files) <= 0:
        return "Not Found", 406

    # Get the location to upload to
    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
    s3_bucket, s3_path = db.sandbox_get_s3_info(user_info.name, upload_id)

    # Upload all the received files and update the database
    temp_file = tempfile.mkstemp(prefix=SPARCD_PREFIX)
    os.close(temp_file[0])
    for one_file in request.files:
        request.files[one_file].save(temp_file[1])

        cur_species, cur_location, cur_timestamp = image_utils.get_embedded_image_info(temp_file[1])

        # Check if we need to update the location in the file
        sb_location = db.sandbox_get_location(user_info.name, upload_id)
        if not cur_location or \
                (sb_location and cur_location and sb_location['idProperty'] != cur_location['id']):

            # Update the location
            if not image_utils.update_image_file_exif(temp_file[1],
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
        S3Connection.upload_file(s3_url, user_info.name,
                                        get_password(token, db), s3_bucket,
                                        s3_path + '/' + request.files[one_file].filename,
                                        temp_file[1])

        # Update the database entry to show the file is uploaded
        file_id = db.sandbox_file_uploaded(user_info.name, upload_id,
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
    print('SANDBOX COUNTS', flush=True)

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Check what we have from the requestor
    upload_id = request.args.get('i')
    if not upload_id:
        return "Not Found", 406

    # Mark the upload as completed
    counts = db.sandbox_upload_counts(user_info.name, upload_id)

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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the rest of the request parameters
    upload_id = request.form.get('id', None)
    all_files = request.form.get('files', None)
    if not upload_id or not all_files:
        return "Not Found", 406

    # Get all the file names
    try:
        all_files = json.loads(all_files)
    except json.JSONDecodeError as ex:
        print('ERROR: Unable to load file list JSON', ex, flush=True)
        return "Not Found", 406

    # Check with the DB if the upload has been started before
    upload_id = db.sandbox_reset_upload(user_info.name, upload_id, all_files)

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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the rest of the request parameters
    upload_id = request.form.get('id', None)
    if not upload_id:
        return "Not Found", 406

    # Get the sandbox information
    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
    s3_bucket, s3_path = db.sandbox_get_s3_info(user_info.name, upload_id)

    # Update the MEDIA csv file to include media types
    media_info = ctu.load_camtrap_media(s3_url, user_info.name,
                                                lambda: get_password(token, db), s3_bucket, s3_path)
    file_mimetypes = db.get_file_mimetypes(user_info.name, upload_id)

    if media_info:
        for one_key,one_type in file_mimetypes:
            media_info[one_key][camtrap.CAMTRAP_MEDIA_TYPE_IDX] = one_type

        # Upload the MEDIA csv file to the server
        S3Connection.upload_camtrap_data(s3_url, user_info.name,
                                         get_password(token, db),
                                         s3_bucket,
                                         make_s3_path((s3_path, MEDIA_CSV_FILE_NAME)),
                                         (media_info[one_key] for one_key in media_info.keys()) )

    # Update the OBSERVATIONS with species information
    file_species = db.get_file_species(user_info.name, upload_id)
    num_files_with_species = 0
    if file_species:
        deployment_info = ctu.load_camtrap_deployments(s3_url, user_info.name,
                                                lambda: get_password(token, db), s3_bucket, s3_path)
        obs_info = ctu.load_camtrap_observations(s3_url, user_info.name,
                                                lambda: get_password(token, db), s3_bucket, s3_path)
        obs_info = ctu.update_observations(s3_path, obs_info, file_species,
                                        deployment_info[camtrap.CAMTRAP_DEPLOYMENT_ID_IDX])

        # Upload the OBSERVATIONS csv file to the server
        # Tuple of row tuples for each file. (((,,),(,,)),((,,),(,,)), ...) Each row is also a tuple
        # We flatten further on the call so we're left with a single tuple containing all rows
        row_groups = (obs_info[one_key] for one_key in obs_info)
        S3Connection.upload_camtrap_data(s3_url, user_info.name,
                                    get_password(token, db),
                                    s3_bucket,
                                    make_s3_path((s3_path, OBSERVATIONS_CSV_FILE_NAME)),
                                    [one_row for one_set in row_groups for one_row in one_set] )

        num_files_with_species = len(obs_info)

    # Clean up any temporary files we might have
    for one_filename in [MEDIA_CSV_FILE_NAME, OBSERVATIONS_CSV_FILE_NAME]:
        del_path = os.path.join(tempfile.gettempdir(),
                    SPARCD_PREFIX+s3_bucket+'_'+os.path.basename(s3_path)+'_'+one_filename)
        if os.path.exists(del_path):
            os.unlink(del_path)

    # Update the upload metadata with the count of files that have species
    if num_files_with_species > 0:
        S3Connection.update_upload_metadata_image_species(s3_url, user_info.name,
                                                        get_password(token, db),
                                                        s3_bucket, s3_path, num_files_with_species)

    # Update the collection to reflect the new upload metadata
    updated_collection = S3Connection.get_collection_info(s3_url, user_info.name, \
                                                    get_password(token, db), s3_bucket)
    if updated_collection:
        updated_collection = sdu.normalize_collection(updated_collection)

        # Check if we have a stored temporary file containing the collections information
        return_colls = sdu.load_timed_temp_colls(user_info.name, bool(user_info.admin))
        if return_colls:
            return_colls = [one_coll if one_coll['bucket'] != s3_bucket else updated_collection \
                                                                    for one_coll in return_colls ]
            # Save the collections temporarily
            sdu.save_timed_temp_colls(return_colls)

    # Mark the upload as completed
    db.sandbox_upload_complete(user_info.name, upload_id)

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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the rest of the request parameters
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

    bucket = SPARCD_PREFIX + coll_id
    upload_path = f'Collections/{coll_id}/{S3_UPLOADS_PATH_PART}{upload_id}'

    db.add_collection_edit(user_info.url, bucket, upload_path, user_info.name, timestamp,
                                                                        loc_id, loc_name, loc_ele)

    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
    sdu.process_upload_changes(s3_url, user_info.name, lambda: get_password(token, db),
                                coll_id, upload_id, TEMP_SPECIES_FILE_NAME,
                                change_locations={
                                                    'loc_id': loc_id,
                                                    'loc_name': loc_name,
                                                    'loc_ele': loc_ele,
                                                    'loc_lat': loc_lat,
                                                    'loc_lon': loc_lon,
                                                })

    # Update the Deployments file and the others that are dependent upon the Deployment ID
    deployment_info = ctu.load_camtrap_deployments(s3_url, user_info.name,
                                            lambda: get_password(token, db), bucket, upload_path)
    deployment_id = coll_id + ':' +loc_id
    deployment_info[0][camtrap.CAMTRAP_DEPLOYMENT_LOCATION_ID_IDX] = deployment_id
    deployment_info[0][camtrap.CAMTRAP_DEPLOYMENT_LOCATION_NAME_IDX] = loc_name
    deployment_info[0][camtrap.CAMTRAP_DEPLOYMENT_LONGITUDE_IDX] = loc_lat
    deployment_info[0][camtrap.CAMTRAP_DEPLOYMENT_LATITUDE_IDX] = loc_lon
    deployment_info[0][camtrap.CAMTRAP_DEPLOYMENT_CAMERA_HEIGHT_IDX] = loc_ele

    S3Connection.upload_camtrap_data(s3_url, user_info.name,
                        get_password(token, db),
                        bucket,
                        make_s3_path((upload_path, DEPLOYMENT_CSV_FILE_NAME)),
                        deployment_info )

    # Get and update the Media information
    media_info = ctu.load_camtrap_media(s3_url, user_info.name,
                                            lambda: get_password(token, db), bucket, upload_path)
    for one_media in media_info:
        media_info[one_media][camtrap.CAMTRAP_MEDIA_DEPLOYMENT_ID_IDX] = deployment_id

    S3Connection.upload_camtrap_data(s3_url, user_info.name,
                                get_password(token, db),
                                bucket, make_s3_path((upload_path, MEDIA_CSV_FILE_NAME)),
                                media_info )

    # Get and update the Observation information
    obs_info = ctu.load_camtrap_observations(s3_url, user_info.name,
                                            lambda: get_password(token, db), bucket, upload_path)

    for one_file in obs_info:
        for one_obs in obs_info[one_file]:
            one_obs[camtrap.CAMTRAP_OBSERVATION_DEPLOYMENT_ID_IDX] = deployment_id

    S3Connection.upload_camtrap_data(s3_url, user_info.name,
                                get_password(token, db),
                                bucket, make_s3_path((upload_path, OBSERVATIONS_CSV_FILE_NAME)),
                                obs_info )

    # Get and update the Observation information

    # Update the collection to reflect the new upload location
    updated_collection = S3Connection.get_collection_info(s3_url, user_info.name, \
                                                    get_password(token, db),
                                                    bucket)
    if updated_collection:
        updated_collection = sdu.normalize_collection(updated_collection)

        # Check if we have a stored temporary file containing the collections information
        return_colls = sdu.load_timed_temp_colls(user_info.name, bool(user_info.admin))
        if return_colls:
            return_colls = [one_coll if one_coll['bucket'] != bucket else updated_collection \
                                                                    for one_coll in return_colls ]
            # Save the collections temporarily
            sdu.save_timed_temp_colls(return_colls)

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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the rest of the request parameters
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

    path = crypt.do_decrypt(WORKING_PASSCODE, path)
    if upload_id not in path or coll_id not in path:
        return "Not Found", 404

    bucket = SPARCD_PREFIX + coll_id

    db.add_image_species_edit(user_info.url, bucket, path, user_info.name, timestamp,
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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the rest of the request parameters
    coll_id = request.form.get('collection', None)
    upload_id = request.form.get('upload', None)
    path = request.form.get('path', None) # Image path on S3 under bucket

    # Check what we have from the requestor
    if not all(item for item in [token, coll_id, upload_id, path]):
        return "Not Found", 406

    path = crypt.do_decrypt(WORKING_PASSCODE, path)
    if upload_id not in path or coll_id not in path:
        return "Not Found", 406

    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))

    # Get any changes
    upload_files_info = db.get_next_files_info(user_info.url, user_info.name, path)

    if not upload_files_info:
        return {'success': True, 'retry': True, 'message': "No changes found for file", \
                                        'collection':coll_id, 'upload_id': upload_id, \
                                        'path': request.form.get('path', None), \
                                        'filename': os.path.basename(path), \
                                        'error': False}

    # Update the image and the observations information
    upload_files_info = [one_file|{'name': \
                    one_file['s3_path'][one_file['s3_path'].index(upload_id)+len(upload_id)+1:]} \
                                                                for one_file in upload_files_info]
    success_files, errored_files = sdu.process_upload_changes(s3_url,
                                                        user_info.name,
                                                        lambda: get_password(token, db),
                                                        coll_id,
                                                        upload_id,
                                                        TEMP_SPECIES_FILE_NAME,
                                                        files_info=upload_files_info)

    if success_files:
        db.complete_image_edits(user_info.name, success_files)

    if errored_files:
        return {'success': False, 'retry': True, 'message': 'Not all the edits could be completed',\
                           'error':True, 'collection':coll_id, 'upload_id': upload_id, 'path': path}


    return {'success': True, 'message': "The images have been successfully updated", 'error': False}


@app.route('/imagesAllEdited', methods = ['POST'])
@cross_origin(origins="http://localhost:3000", supports_credentials=True)
def images_all_edited():
    """ Handles completing changes after images have been edited
    Arguments: (GET)
        t - the session token
    Return:
        Returns success unless there's an issue
    Notes:
         If the token is invalid, or a problem occurs, a 404 error is returned
   """
    db = SPARCdDatabase(DEFAULT_DB_PATH)
    token = request.args.get('t')
    print('IMAGES ALL FINISHED', flush=True)

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the rest of the request parameters
    coll_id = request.form.get('collection', None)
    upload_id = request.form.get('upload', None)
    timestamp = request.form.get('timestamp', datetime.datetime.now().isoformat())

    # Check what we have from the requestor
    if not all(item for item in [coll_id, upload_id]):
        return "Not Found", 406

    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))

    # Get any changes
    edited_files_info = db.get_edited_files_info(user_info.url, user_info.name, upload_id)

    if not edited_files_info:
        return {'success': True, 'retry': True, 'message': "No changes found for to the upload", \
                                                    'collection':coll_id, 'upload_id': upload_id}

    # Update the image and the observations information
    edited_files_info = [one_file|{'filename':one_file['s3_path']\
                                        [one_file['s3_path'].index(upload_id)+len(upload_id)+1:]} \
                                                                for one_file in edited_files_info]

    s3_bucket = SPARCD_PREFIX + coll_id
    s3_path = make_s3_path(('Collections', coll_id, S3_UPLOADS_PATH_PART, upload_id))

    deployment_info = ctu.load_camtrap_deployments(s3_url, user_info.name,
                                                                lambda: get_password(token, db),
                                                                s3_bucket, s3_path, True)
    obs_info = ctu.load_camtrap_observations(s3_url, user_info.name,
                                                                lambda: get_password(token, db),
                                                                s3_bucket, s3_path, True)
    for one_file in edited_files_info:
        # Do the update
        obs_info = ctu.update_observations(s3_path, obs_info,
                        [one_species| \
                                {'filename':one_file['filename'], 'timestamp':timestamp} \
                                        for one_species in one_file['species']],
                        deployment_info[0][camtrap.CAMTRAP_DEPLOYMENT_ID_IDX])

    # Upload the OBSERVATIONS csv file to the server
    # Tuple of row tuples for each file. (((,,),(,,)),((,,),(,,)), ...) Each row is also a
    # tuple. We flatten further on the call so we're left with a single tuple containing all
    # rows
    row_groups = (obs_info[one_key] for one_key in obs_info)
    S3Connection.upload_camtrap_data(s3_url, user_info.name,
                                get_password(token, db),
                                s3_bucket, make_s3_path((s3_path, OBSERVATIONS_CSV_FILE_NAME)),
                                [one_row for one_set in row_groups for one_row in one_set] )

    db.finish_image_edits(user_info.name, edited_files_info)

    # Update the upload metadata with an editing comment
    S3Connection.update_upload_metadata_comment(s3_url, user_info.name,
                                        get_password(token, db),
                                        s3_bucket,s3_path,
                                        f'Edited by {user_info.name} on ' + \
                                                datetime.datetime.fromisoformat(timestamp).\
                                                        strftime("%Y.%m.%d.%H.%M.%S"))

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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the rest of the request parameters

    common = request.form.get('common', None) # Species name
    scientific = request.form.get('scientific', None) # Species scientific name
    new_key = request.form.get('key', None)

    # Check what we have from the requestor
    if not common or not scientific or not new_key:
        return "Not Found", 406

    # Get the species
    if user_info.species:
        cur_species = user_info.species
    else:
        s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
        cur_species = s3u.load_sparcd_config(SPECIES_JSON_FILE_NAME, TEMP_SPECIES_FILE_NAME, \
                                            s3_url, user_info.name, lambda: get_password(token, db))

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

    db.save_user_species(user_info.name, json.dumps(cur_species))

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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    return {'value': user_info.admin == 1}

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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Make sure this user is an admin
    if user_info.admin != 1:
        return "Not Found", 404

    # Check for changes in the db
    changed = db.have_admin_changes(user_info.url, user_info.name)

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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the rest of the request parameters
    pw = request.form.get('value', None)
    if not pw:
        return "Not Found", 406

    # Make sure this user is an admin
    if user_info.admin != 1:
        return "Not Found", 404

    # Log onto S3 to make sure the information is correct
    pw_ok = False
    try:
        s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
        minio = Minio(s3_url, access_key=user_info.name, secret_key=pw)
        _ = minio.list_buckets()
        pw_ok = True
    except MinioException as ex:
        print(f'Admin password check failed for {user_info.name}:', ex)
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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Make sure this user is an admin
    if user_info.admin != 1:
        return "Not Found", 404

    # Get the users and fill in the collection information
    all_users = db.get_admin_edit_users()

    if not all_users:
        return json.dumps(all_users)

    # Organize the collection permissions by user
    # TODO: Combine load_timed_temp_colls with S3Connection.get_collections? See /collections
    #       here and elsewhere
    all_collections = sdu.load_timed_temp_colls(user_info.name, True)
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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Make sure this user is an admin
    if user_info.admin != 1:
        return "Not Found", 404

    # Get the species
    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
    cur_species = s3u.load_sparcd_config(SPECIES_JSON_FILE_NAME, TEMP_SPECIES_FILE_NAME, s3_url,
                                            user_info.name, lambda: get_password(token, db))

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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the rest of the request parameters
    old_name = request.form.get('oldName', None)
    new_email = request.form.get('newEmail', None)

    # Check what we have from the requestor
    if not all(item for item in [old_name, new_email]):
        return "Not Found", 406

    # Make sure this user is an admin
    if user_info.admin != 1:
        return "Not Found", 404

    if not user_info.name == old_name:
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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the rest of the request parameters
    new_name = request.form.get('newName', None)
    old_scientific = request.form.get('oldScientific', None)
    new_scientific = request.form.get('newScientific', None)
    key_binding = request.form.get('keyBinding', '')
    icon_url = request.form.get('iconURL', None)

    # Check what we have from the requestor
    if not all(item for item in [new_name, new_scientific, icon_url]):
        return "Not Found", 406

    # Make sure this user is an admin
    if user_info.admin != 1:
        return "Not Found", 404

    # Get the species
    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
    cur_species = s3u.load_sparcd_config(SPECIES_JSON_FILE_NAME, TEMP_SPECIES_FILE_NAME, s3_url,
                                            user_info.name, lambda: get_password(token, db))

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
    if db.update_species(user_info.url, user_info.name, old_scientific, new_scientific, \
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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the rest of the request parameters
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
    if not all(item for item in [loc_name, loc_id, loc_active, measure, coordinate]):
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

    # Make sure this user is an admin
    if user_info.admin != 1:
        return "Not Found", 404

    # Get the location
    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
    cur_locations = sdu.load_locations(s3_url, user_info.name, lambda: get_password(token, db))

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
        loc_ele = round((loc_ele * FEET_TO_METERS) * 100) / 100

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
    if db.update_location(user_info.url, user_info.name, loc_name, loc_id, loc_active,
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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Get the rest of the request parameters
    col_id = request.form.get('id', None)
    col_name = request.form.get('name', None)
    col_desc = request.form.get('description', None)
    col_email = request.form.get('email', None)
    col_org = request.form.get('organization', None)
    col_all_perms = request.form.get('allPermissions', None)

    # Check what we have from the requestor
    if not all(item for item in [col_id, col_name, col_all_perms]):
        return "Not Found", 406

    if col_desc is None:
        col_desc = ''
    if col_email is None:
        col_email = ''
    if col_org is None:
        col_org = ''

    col_all_perms = json.loads(col_all_perms)

    # Make sure this user is an admin
    if user_info.admin != 1:
        return "Not Found", 404

    # Get existing collection information and permissions
    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))
    s3_bucket = SPARCD_PREFIX + col_id

    all_collections = sdu.load_timed_temp_colls(user_info.name, True)

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
    S3Connection.save_collection_info(s3_url, user_info.name,
                                get_password(token, db), found_coll['bucket'],
                                found_coll)

    S3Connection.save_collection_permissions(s3_url, user_info.name,
                                get_password(token, db), found_coll['bucket'],
                                col_all_perms)

    # Update the collection to reflect the changes
    updated_collection = S3Connection.get_collection_info(s3_url, user_info.name,
                                                    get_password(token, db), s3_bucket)
    if updated_collection:
        updated_collection = sdu.normalize_collection(updated_collection)

        # Check if we have a stored temporary file containing the collections information
        return_colls = sdu.load_timed_temp_colls(user_info.name, True)
        if return_colls:
            return_colls = [one_coll if one_coll['bucket'] != s3_bucket else updated_collection \
                                                                    for one_coll in return_colls ]
            # Save the collections temporarily
            sdu.save_timed_temp_colls(return_colls)

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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Make sure this user is an admin
    if user_info.admin != 1:
        return "Not Found", 404

    # Get the locations and species changes logged in the database
    s3_url = s3u.web_to_s3_url(user_info.url, lambda x: crypt.do_decrypt(WORKING_PASSCODE, x))

    changes = db.get_admin_changes(user_info.url, user_info.name)
    if not changes:
        return {'success': True, 'message': "There were no changes found to apply"}

    # Update the location
    if 'locations' in changes and changes['locations']:
        if not sdu.update_admin_locations(s3_url, user_info.name,
                                      get_password(token, db),
                                      changes):
            return 'Unable to update the locations', 422
    # Mark the locations as done in the DB
    db.clear_admin_location_changes(user_info.url, user_info.name)

    # Update the species
    if 'species' in changes and changes['species']:
        updated_species = sdu.update_admin_species(s3_url, user_info.name, get_password(token, db),
                                                                                            changes)
        if updated_species is None:
            return 'Unable to update the species. Any changed locations were updated', 422

        s3u.save_sparcd_config(updated_species, SPECIES_JSON_FILE_NAME, TEMP_SPECIES_FILE_NAME,
                                            s3_url, user_info.name, lambda: get_password(token, db))
    # Mark the species as done in the DB
    db.clear_admin_species_changes(user_info.url, user_info.name)

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

    # Check the credentials
    token_valid, user_info = sdu.token_user_valid(db, request, token, SESSION_EXPIRE_SECONDS)
    if token_valid is None or user_info is None:
        return "Not Found", 404
    if not token_valid or not user_info:
        return "Unauthorized", 401

    # Make sure this user is an admin
    if user_info.admin != 1:
        return "Not Found", 404

    # Mark the locations as done in the DB
    db.clear_admin_location_changes(user_info.url, user_info.name)

    # Mark the species as done in the DB
    db.clear_admin_species_changes(user_info.url, user_info.name)

    return {'success': True, 'message': "All changes were successully abandoned"}
