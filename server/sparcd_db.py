"""This script contains the database interface for the SPARCd Web app
"""

import logging
import sqlite3
from time import sleep
from typing import Optional
import uuid

class SPARCdDatabase:
    """Class handling access connections to the database
    """

    def __init__(self, db_path: str, logger: logging.Logger=None):
        """Initialize an instance
        """
        self._conn = None
        self._path = db_path
        self._verbose = False
        self._logger = logger

    def __del__(self):
        """Handles closing the connection and other cleanup
        """
        if self._conn is not None:
            self._conn = None

    def database_info(self) -> tuple:
        """ Returns information on the database as a tuple of strings
        """
        return (
             'SQLite database',
             f'Version: {sqlite3.sqlite_version}',
             f'thread safety: {sqlite3.threadsafety}',
             f'api level: {sqlite3.apilevel}',
            )

    def connect(self, database_path: str = None) -> None:
        """Performs the actual connection to the database
        Arguments:
            database: the database to connect to
        """
        database_path = database_path if database_path is not None else self._path
        if self._conn is None:
            if self._verbose:
                print_params = \
                    (param for param in (
                        f'database={database_path}' if database_path is not None else None,
                   ) if param is not None)
                self._logger.info(f'Connecting to the database {print_params}')
            self._conn = sqlite3.connect(database_path)

    def reconnect(self) -> None:
        """Attempts a reconnection if we're not connected
        """
        if self._conn is None:
            self.connect()

    def is_connected(self) -> bool:
        """ Returns whether this class instance is connected (true), or not (false)
        """
        return self._conn is not None

    def add_token(self, token: str, user: str, password: str, client_ip: str,
                  user_agent: str, s3_url: str) -> None:
        """ Saves the token and associated user information
        Arguments:
            token: the unique token to save
            user: the user associated with the token
            password: the password associated with the user
            client_ip: the IP address of the client
            user_agent: a user agent value
            s3_url: the URL of the s3 instance
        """
        if self._conn is None:
            raise RuntimeError('save_token: attempting to access database before connecting')

        cursor = self._conn.cursor()
        query = 'INSERT INTO tokens(token, name, password, s3_url, timestamp, client_ip, ' \
                'user_agent) VALUES(?,?,?,?,strftime("%s", "now"),?,?)'
        cursor.execute(query, (token, user, password, s3_url, client_ip, user_agent))
        self._conn.commit()
        cursor.close()

    def update_token_timestamp(self, token: str) -> None:
        """Updates the token's timestamp to the database's now
        Arguments:
            token: the token to update
        """
        if self._conn is None:
            raise RuntimeError('update_token_timestamp: attempting to access database before ' \
                                        'connecting')

        cursor = self._conn.cursor()
        query = 'UPDATE tokens SET timestamp=strftime("%s", "now") WHERE token=?'
        cursor.execute(query, (token,))
        self._conn.commit()
        cursor.close()

    def remove_token(self, token: str) -> None:
        """ Attempts to remove the token from the database
        Arguments:
            token: the token to remove
        """
        if self._conn is None:
            raise RuntimeError('remove_token: attempting to access database before connecting')

        cursor = self._conn.cursor()
        cursor.execute('DELETE FROM tokens WHERE token=(?)', (token,))
        self._conn.commit()
        cursor.close()

    def get_token_user_info(self, token: str) -> Optional[dict]:
        """ Looks up token and user information
        Arguments:
            The token to lookup
        Return:
            The user name, timestamp, elapsed seconds, email, settings, and admin level
            if the token exists, and None if not
        """
        if self._conn is None:
            raise RuntimeError('get_token_user_info: attempting to access database before ' \
                                    'connecting')

        cursor = self._conn.cursor()
        cursor.execute('WITH ti AS (SELECT token, name, timestamp, client_ip, user_agent,' \
                          '(strftime("%s", "now")-timestamp) AS elapsed_sec, s3_url FROM TOKENS ' \
                          'WHERE token=(?)) '\
                       'SELECT u.name, u.email, u.settings, u.species, u.administrator, ' \
                          'ti.s3_url, ti.timestamp, ti.elapsed_sec, ti.client_ip, ti.user_agent ' \
                          'FROM users u JOIN ti ON u.name = ti.name',
                    (token,))
        res = cursor.fetchone()
        cursor.close()

        if res and len(res) >= 8:
            return {'name':res[0], 'email':res[1], 'settings':res[2], 'species':res[3], \
                    'admin':res[4], 'url':res[5], 'timestamp':res[6], 'elapsed_sec':res[7], \
                    'client_ip':res[8], 'user_agent':res[9]}

        return None

    def get_user(self, username: str) -> Optional[dict]:
        """ Looks up the specified user
        Arguments:
            username: the name of the user to lookup
        Returns:
            A dict containing the user's name, email, settings, and admin level.
        """
        if self._conn is None:
            raise RuntimeError('get_user: attempting to access database before connecting')

        cursor = self._conn.cursor()
        cursor.execute('SELECT name, email, settings, species, administrator FROM users ' \
                                'WHERE name=(?)', (username,))
        res = cursor.fetchone()
        cursor.close()

        if res and len(res) >= 4:
            return {'name': res[0], 'email':res[1], 'settings':res[2], 'species':res[3], \
                    'admin':res[4]}

        return None

    def auto_add_user(self, username: str, species: str, email: str=None) -> Optional[dict]:
        """ Add a user that doesn't exist. The user received default permissions as defined
            in the DB
        Arguments:
            username: the name of the user to add
            species: the species information for the user
            email: the user's email
        Returns:
            A dict containing the user's name, email, settings, and admin level
        Note:
            Assumes the user to be added has already been vetted. It is not an error if the user
            already exists in the database - however, the user's email won't be updated if the
            user already exists.
        """
        if self._conn is None:
            raise RuntimeError('auto_add_user: attempting to access database before connecting')

        cursor = self._conn.cursor()
        try:
            cursor.execute('INSERT INTO users(name, email, species) VALUES(?,?,?)',
                                                                        (username,email,species))
            self._conn.commit()
        except sqlite3.IntegrityError as ex:
            # TODO: Track this exception here to prevent something?
            # If the user already exists, we ignore the error and continue
            if not ex.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
                raise ex
        finally:
            cursor.close()

        return self.get_user(username)

    def get_password(self, token: str) -> str:
        """ Returns the password associated with the token
        Arguments:
            token: the token to lookup
        Return:
            Returns the associated password, or an empty string if the token is not found
        """
        if self._conn is None:
            raise RuntimeError('Attempting to access database before connecting')

        cursor = self._conn.cursor()
        cursor.execute('SELECT password FROM tokens WHERE token=(?)', (token,))

        res = cursor.fetchone()
        cursor.close()

        if res and len(res) >= 1:
            return res[0]

        return ''

    def update_user_settings(self, username: str, settings: str, email: str) ->None:
        """ Updates the user's settings in the database
        Arguments
            username: the name of the user to update
            settings: the new settings to set
            email: the updated email address
        """
        if self._conn is None:
            raise RuntimeError('update_user_settings: Attempting to access database before '\
                                    'connecting')

        cursor = self._conn.cursor()
        cursor.execute('UPDATE users SET settings=(?), email=(?) WHERE name=(?)',
                                                                        (settings,email,username))
        self._conn.commit()
        cursor.close()


    def get_collections(self, timeout_sec:int) -> Optional[list]:
        """ Returns the collection information stored in the database
        Arguments:
            timeout_sec: the amount of time before the table entries can be
                         considered expired
        Returns:
            Returns the collections or None if there are no collections
        """
        if self._conn is None:
            raise RuntimeError('Attempting to access database before connecting')

        cursor = self._conn.cursor()
        cursor.execute('SELECT (strftime("%s", "now")-timestamp) AS elapsed_sec ' \
                       'from table_timeout where name="collections" ORDER BY ' \
                       'elapsed_sec DESC LIMIT 1')

        res = cursor.fetchone()
        if not res or len(res) < 1 or int(res[0]) >= timeout_sec:
            return None

        cursor.execute('SELECT name, json FROM collections')

        res = cursor.fetchall()
        if not res or len(res) < 1:
            return None

        return [{'name':row[0], 'json':row[1]} for row in res]

    def save_collections(self, collections: tuple) -> bool:
        """ Saves the collections to the database
        Arguments:
            collections: a tuple of dicts containing the collection name and data json
        Return:
            Returns True if data is saved, and False if something went wrong
        """
        # TODO: have a hash value to check to see if record JSON has changed
        if self._conn is None:
            raise RuntimeError('Attempting to access database before connecting')

        cursor = self._conn.cursor()

        tries = 0
        while tries < 10:
            try:
                print('HACK:COLL: DELETE',tries)
                cursor.execute('DELETE FROM collections')
                break
            except sqlite3.Error as ex:
                if ex.sqlite_errorcode == sqlite3.SQLITE_BUSY:
                    tries = tries + 1
                    sleep(1)
                else:
                    print(f'Save collections clearing sqlite error detected: {ex.sqlite_errorcode}')
                    print('    Not processing request further: delete')
                    print('   ',ex)
                    tries = 10
        if tries >= 10:
            self._conn.rollback()
            cursor.close()
            return False

        tries = 0
        for one_coll in collections:
            try:
                print('HACK:COLL: INSERT: ',one_coll['name'])
                cursor.execute('INSERT INTO collections(name,json) values(?, ?)', \
                                                (one_coll['name'], one_coll['json']))
                tries += 1
            except sqlite3.Error as ex:
                print(f'Unable to update collections: {ex.sqlite_errorcode} {one_coll}')
                break

        if tries < len(collections):
            self._conn.rollback()
            cursor.close()
            return False

        # Update the timeout table for collections and do some cleanup if needed
        print('HACK:COLL: TIMEOUT TABLE')
        cursor.execute('SELECT COUNT(1) FROM table_timeout WHERE name="collections"')
        res = cursor.fetchone()

        count = int(res[0]) if res and len(res) > 0 else 0
        if count > 1:
            # Remove multiple old entries
            cursor.execute('DELETE FROM table_timeout WHERE name="collections"')
            count = 0
        if count <= 0:
            cursor.execute('INSERT INTO table_timeout(name,timestamp) ' \
                                'VALUES ("collections",strftime("%s", "now"))')
        else:
            cursor.execute('UPDATE table_timeout SET timestamp=strftime("%s", "now") ' \
                                'WHERE name="collections"')

        self._conn.commit()
        cursor.close()

        return True

    def get_sandbox(self) -> Optional[tuple]:
        """ Returns the sandbox items
        Returns:
            A tuple containing the known sandbox items
        """
        if self._conn is None:
            raise RuntimeError('Attempting to get sandbox information from the database before ' \
                                                                                    'connecting')
        # Get the Sandbox information
        cursor = self._conn.cursor()
        cursor.execute('SELECT path, bucket, s3_base_path, location_id FROM sandbox')
        res = cursor.fetchall()

        if not res or len(res) < 1:
            return tuple()

        return [{'complete': not row[0] or row[0] == '',
                 'bucket': row[1],
                 's3_path': row[2],
                 'location_id': row[3]
               } for row in res]

    def get_uploads(self, bucket: str, timeout_sec: int) -> Optional[tuple]:
        """ Returns the uploads for this collection from the database
        Arguments:
            timeout_sec: the amount of time before the table entries can be
                         considered expired
            The bucket to get uploads for
        Return:
            Returns the loaded tuple of upload names and data
        """
        if self._conn is None:
            raise RuntimeError('Attempting to access database before connecting')

        # Check for expired collection uploads
        cursor = self._conn.cursor()
        cursor.execute('SELECT (strftime("%s", "now")-timestamp) AS elapsed_sec from ' \
                       'table_timeout where name=(?) ORDER BY elapsed_sec DESC LIMIT 1', \
                       (bucket,))

        res = cursor.fetchone()
        if not res or len(res) < 1 or int(res[0]) >= timeout_sec:
            return None

        cursor.execute('SELECT name,json FROM uploads WHERE collection=(?)', (bucket,))
        res = cursor.fetchall()

        if not res or len(res) < 1:
            return None

        return [{'name':row[0], 'json':row[1]} for row in res]

    def save_uploads(self, bucket: str, uploads: tuple) -> bool:
        """ Save the upload information into the table
        Arguments:
            bucket: the bucket name to save the uploads under
            uploads: the uploads to save containing the collection name,
                upload name, and associated JSON
        Return:
            Returns True if the data was saved and False if something went wrong
        """
        # TODO: have a hash value to check to see if record JSON has changed
        if self._conn is None:
            raise RuntimeError('Attempting to access database before connecting')

        cursor = self._conn.cursor()

        tries = 0
        while tries < 10:
            try:
                cursor.execute('DELETE FROM uploads where collection=(?)', (bucket,))
                break
            except sqlite3.Error as ex:
                if ex.sqlite_errorcode == sqlite3.SQLITE_BUSY:
                    tries += 1
                    sleep(1)
                else:
                    print(f'Save uploads delete sqlite error detected: {ex.sqlite_errorcode}')
                    print('    Not processing request further: delete')
                    print('   ',ex)
                    tries = 10
        if tries >= 10:
            cursor.execute('ROLLBACK TRANSACTION')
            cursor.close()
            return False

        tries = 0
        for one_upload in uploads:
            try:
                cursor.execute('INSERT INTO uploads(collection,name,json) values(?,?,?)', \
                                        (bucket, one_upload['name'], one_upload['json']))
                tries += 1
            except sqlite3.Error as ex:
                print(f'Unable to update collections: {ex.sqlite_errorcode} {one_upload}')
                break

        if tries < len(uploads):
            cursor.execute('ROLLBACK TRANSACTION')
            cursor.close()
            return False

        # Update the timeout table for collections and do some cleanup if needed
        cursor.execute('SELECT COUNT(1) FROM table_timeout WHERE name=(?)', (bucket,))
        res = cursor.fetchone()

        count = int(res[0]) if res and len(res) > 0 else 0
        if count > 1:
            # Remove multiple old entries
            cursor.execute('DELETE FROM table_timeout WHERE name=(?)', (bucket,))
            count = 0
        if count <= 0:
            cursor.execute('INSERT INTO table_timeout(name,timestamp) ' \
                                'VALUES (?,strftime("%s", "now"))', (bucket,))
        else:
            cursor.execute('UPDATE table_timeout SET timestamp=strftime("%s", "now") ' \
                                'WHERE name=(?)', (bucket,))

        cursor.execute('COMMIT TRANSACTION')
        cursor.close()

        return True

    def save_query_path(self, token: str, file_path: str) -> bool:
        """ Stores the specified query file path in the database
        Arguments:
            token: a token associated with the path - can be used to manage paths
            file_path: the path to the saved query information
        Return:
            True is returned if the path is saved and False if a problem occurrs
        """
        if self._conn is None:
            raise RuntimeError('Attempting to save query paths in the database before connecting')

        # Check for expired collection uploads
        cursor = self._conn.cursor()
        cursor.execute('INSERT INTO queries(token,path,timestamp) ' \
                                'VALUES (?,?,strftime("%s", "now"))', (token, file_path))

        cursor.execute('COMMIT TRANSACTION')
        cursor.close()

        return True

    def get_clear_queries(self, token: str) -> tuple:
        """ Returns a tuple of saved query paths associated with this token and removes
            them from the database
        Arguments:
            token: a token associated with the paths to clean return
        """
        if self._conn is None:
            raise RuntimeError('Attempting to save query paths in the database before connecting')

        # Check for queries associated with the token
        cursor = self._conn.cursor()
        cursor.execute('SELECT id, path FROM queries WHERE token=(?)', (token,))

        res = cursor.fetchall()
        if not res or len(res) < 1:
            return []

        path_ids = [row[0] for row in res]
        return_paths = [row[1] for row in res]

        # Clean up the queries
        tries = 0
        while tries < 10:
            try:
                cursor.execute('DELETE FROM queries where id in (' + \
                                                    ','.join(['?'] * len(path_ids)) + ')', path_ids)
                break
            except sqlite3.Error as ex:
                if ex.sqlite_errorcode == sqlite3.SQLITE_BUSY:
                    tries += 1
                    sleep(1)
                else:
                    print(f'Saved queries delete sqlite error detected: {ex.sqlite_errorcode}')
                    print('    Not processing request further: delete')
                    print('   ',ex)
                    tries = 10
        if tries >= 10:
            cursor.execute('ROLLBACK TRANSACTION')

        cursor.execute('COMMIT TRANSACTION')
        cursor.close()

        return return_paths

    def get_query(self, token: str) -> tuple:
        """ Returns a tuple of saved query paths associated with this token
        Arguments:
            token: a token associated with the paths to clean return
        """
        if self._conn is None:
            raise RuntimeError('Attempting to save query paths in the database before connecting')

        # Check for queries associated with the token
        cursor = self._conn.cursor()
        cursor.execute('SELECT path,(strftime("%s", "now")-timestamp) AS elapsed_sec FROM queries '\
                                    'WHERE token=(?) ORDER BY elapsed_sec DESC LIMIT 1', (token,))

        res = cursor.fetchone()
        if not res or len(res) < 2:
            return []

        cursor.close()

        return res[0], res[1]

    def sandbox_get_upload(self, username: str, path: str, new_upload_id: bool=False) -> \
                                                                                    Optional[tuple]:
        """ Checks if an upload for the user exists and returns the files that were loaded
        Arguments:
            username: the user associated with the upload
            path: the source path of the uploads
            new_upload_id: creates a new upload ID for an existing upload
        Returns:
            Returns a tuple containing the timestamp for the existing upload, and another tuple
            containing the files that have been uploaded, and a new upload ID if upload exists or
            None if new_upload_id is False or the upload doesn't exist
        """
        if self._conn is None:
            raise RuntimeError('Attempting to get sandbox uploads from the database before ' \
                                                                                    'connecting')

        # Find the upload
        cursor = self._conn.cursor()
        cursor.execute('SELECT id, (strftime("%s", "now")-timestamp) AS elapsed_sec ' \
                        'FROM sandbox WHERE name=(?) and path=(?) LIMIT 1',
                                                                                (username, path))

        res = cursor.fetchone()
        if not res or len(res) < 2:
            cursor.close()
            return None, None, None

        sandbox_id = res[0]
        elapsed_sec = res[1]

        cursor.close()

        # Update the upload ID if requested
        upload_id = None
        if new_upload_id is not False:
            upload_id = uuid.uuid4().hex
            cursor = self._conn.cursor()
            cursor.execute('UPDATE sandbox SET upload_id=(?) WHERE name=(?) AND path=(?)',
                                    (upload_id,username,path))
            self._conn.commit()
            cursor.close()

        # Get all the uploaded files
        cursor = self._conn.cursor()
        cursor.execute('SELECT source_path FROM sandbox_files WHERE sandbox_id=(?) AND ' \
                                                                    'uploaded=TRUE', (sandbox_id,))
        res = cursor.fetchall()

        if not res or len(res) < 1:
            cursor.close()
            return elapsed_sec, [], upload_id

        loaded_files = [row[0] for row in res]

        cursor.close()

        return elapsed_sec, loaded_files, upload_id

    def sandbox_new_upload(self, username: str, path: str, files: tuple, s3_bucket: str, \
                                                            s3_path: str, location_id: str) -> str:
        """ Adds new sandbox upload entries
        Arguments:
            username: the name of the person starting the upload
            path: the source path of the images
            files: the list of filenames (or partial paths) that's to be uploaded
            s3_bucket: the S3 bucket to load into
            s3_path: the base path of the S3 upload
            location_id: the ID of the location associated with the upload
        Return:
            Returns the upload ID if entries are added to the database
        """
        if self._conn is None:
            raise RuntimeError('Attempting to add a new sandbox upload to the database before ' \
                                                                                    'connecting')

        # Create the upload
        upload_id = uuid.uuid4().hex
        cursor = self._conn.cursor()
        cursor.execute('INSERT INTO sandbox(name, path, bucket, s3_base_path, ' \
                                                            'location_id, timestamp, upload_id) ' \
                                    'VALUES(?,?,?,?,?,strftime("%s", "now"),?)', 
                            (username, path, s3_bucket, s3_path, location_id, upload_id))

        sandbox_id = cursor.lastrowid

        for one_file in files:
            cursor.execute('INSERT INTO sandbox_files(sandbox_id, filename, source_path, ' \
                                                                                    'timestamp) ' \
                                    'VALUES(?,?,?,strftime("%s", "now"))',
                            (sandbox_id, one_file, one_file))

        self._conn.commit()
        cursor.close()

        return upload_id

    def sandbox_get_s3_info(self, username: str, upload_id: str) -> tuple:
        """ Returns the bucket and path associated with the sandbox
        Arguments:
            username: the name of the person starting the upload
            upload_id: the ID of the upload
        Return:
            Returns a tuple of the bucket and upload path of the S3 instance. If the user and path
            aren't found, None is returned for both items
        """
        if self._conn is None:
            raise RuntimeError('Attempting to get sandbox S3 information from the database before '\
                                                                                    'connecting')

        # Get the date
        cursor = self._conn.cursor()
        cursor.execute('SELECT bucket, s3_base_path FROM sandbox WHERE name=(?) AND upload_id=(?)',
                                                                            (username, upload_id))

        res = cursor.fetchone()
        if not res or len(res) < 2:
            return None, None

        cursor.close()

        return res[0], res[1]

    def sandbox_upload_counts(self, username: str, upload_id: str) -> tuple:
        """ Returns the total and uploaded count of the files
        Arguments:
            username: the name of the person starting the upload
            upload_id: the ID of the upload
        Return:
            Returns a tuple with the number of files marked as uploaded and the total
            number of files
        """
        if self._conn is None:
            raise RuntimeError('Attempting to count sandbox uploaded files in the database '\
                                                                                'before connecting')

        # Get the date
        cursor = self._conn.cursor()
        cursor.execute('WITH '\
                'upid AS ' \
                    '(SELECT id FROM sandbox WHERE name=(?) AND upload_id=(?) AND path <> ""),' \
                'uptot AS ' \
                    '(SELECT sandbox_id,count(1) AS tot FROM sandbox_files,upid WHERE ' \
                                                                    'sandbox_id=upid.id),' \
                ' uphave AS ' \
                    '(SELECT sandbox_id,count(1) AS have FROM sandbox_files,upid WHERE ' \
                                        'sandbox_id = upid.id AND sandbox_files.uploaded=TRUE)' \
                'SELECT uptot.tot,uphave.have FROM uptot LEFT JOIN uphave ON '\
                                                    'uptot.sandbox_id=uphave.sandbox_id LIMIT 1',
                                                                            (username, upload_id))

        res = cursor.fetchone()
        if not res or len(res) < 2:
            return 0, 0

        cursor.close()

        return res[0] if res[0] is not None else 0, res[1] if res[1] is not None else 0

    def sandbox_reset_upload(self, username: str, upload_id: str, files: tuple) -> str:
        """ Resets an upload for another attempt
        Arguments:
            username: the name of the person starting the upload
            upload_id: the ID of the upload
            files: the list of filenames (or partial paths) that's to be uploaded
        Return:
            Returns the upload ID if entries are added to the database
        """
        if self._conn is None:
            raise RuntimeError('Attempting to add a new sandbox upload to the database before ' \
                                                                                    'connecting')

        # Get the sandbox ID
        cursor = self._conn.cursor()
        cursor.execute('SELECT id FROM sandbox WHERE name=(?) AND upload_id=(?)',
                                                                            (username, upload_id))
        res = cursor.fetchone()
        if not res or len(res) < 1:
            return None

        sandbox_id = res[0]
        if sandbox_id is None:
            return None

        cursor.close()

        # Clear the old files and add the new ones
        cursor = self._conn.cursor()

        cursor.execute('DELETE FROM sandbox_files WHERE sandbox_id=(?)', (sandbox_id, ))

        for one_file in files:
            cursor.execute('INSERT INTO sandbox_files(sandbox_id, filename, source_path, ' \
                                                                                    'timestamp) ' \
                                    'VALUES(?,?,?,strftime("%s", "now"))',
                            (sandbox_id, one_file, one_file))

        self._conn.commit()
        cursor.close()

        return upload_id

    def sandbox_upload_complete(self, username: str, upload_id: str) -> None:
        """ Marks the sandbox upload as completed by resetting the path
        Arguments:
            username: the name of the person starting the upload
            upload_id: the ID of the upload
        """
        if self._conn is None:
            raise RuntimeError('Attempting to complete sandbox upload in the database '\
                                                                                'before connecting')

        # Get the date
        cursor = self._conn.cursor()
        cursor.execute('UPDATE sandbox SET path="" WHERE name=(?) AND upload_id=(?)',
                                                                            (username, upload_id))

        self._conn.commit()
        cursor.close()

    def sandbox_file_uploaded(self, username: str, upload_id: str, filename: str, \
                                                                    mimetype: str) -> Optional[str]:
        """ Marks the file as upload as uploaded
        Arguments:
            username: the name of the person starting the upload
            upload_id: the ID of the upload
            filename: the name of the uploaded file to mark as uploaded
            mimetype: the mimetype of the file uploaded
        Return:
            Returns the ID of the updated file
        """
        if self._conn is None:
            raise RuntimeError('Attempting to mark file as uploaded in the database ' \
                                                                                'before connecting')

        # Get the file's ID
        cursor = self._conn.cursor()
        cursor.execute('SELECT id FROM sandbox_files WHERE '\
                            'sandbox_files.filename=(?) AND sandbox_id in ' \
                        '(SELECT id FROM SANDBOX WHERE name=(?) AND upload_id=(?)) LIMIT 1',
                                                        (filename, username, upload_id))

        res = cursor.fetchall()
        if not res or len(res) < 1:
            return None

        sandbox_file_id = res[0][0]

        # Update the file's mimetype
        cursor.execute('UPDATE sandbox_files SET uploaded=TRUE, mimetype=(?) WHERE '\
                            'sandbox_files.filename=(?) AND id=(?)',
                                                        (mimetype,filename, sandbox_file_id))

        self._conn.commit()
        cursor.close()

        return sandbox_file_id

    def sandbox_add_file_info(self, file_id: str, species: tuple, location: dict, \
                                                                        timestamp: str) -> None:
        """ Marks the file as upload as uploaded
        Arguments:
            file_id: the ID of the uploaded file add species and location to
            species: a tuple containing tuples of species common and scientific names, and counts
            location: a dict containing name, id, and elevation information
            timestamp: the timestamp associated with the entries
        """
        if self._conn is None:
            raise RuntimeError('Attempting to add species and location to an upload file in the ' \
                                                                    'database before connecting')

        if not species or species is None or not location or location is None:
            print('INFO: No species or location specified for updating uploaded file ',
                        f'{file_id}', flush=True)
            return

        cursor = self._conn.cursor()
        if species:
            cursor.executemany('INSERT INTO ' \
                                    'sandbox_species(sandbox_file_id, obs_date, obs_common,' \
                                                                    'obs_scientific, obs_count) ' \
                                    'VALUES (?,?,?,?,?)',
                    ((file_id,timestamp,one_species['common'],one_species['scientific'], \
                                    int(one_species['count'])) \
                            for one_species in species) )

        if location:
            cursor.execute('INSERT INTO sandbox_locations(sandbox_file_id, loc_name, loc_id, ' \
                                                                                'loc_elevation) ' \
                                    'VALUES (?,?,?,?)', 
                        (file_id, location['name'], location['id'], \
                                                                float(location['elevation'])) )

        self._conn.commit()
        cursor.close()


    def get_file_mimetypes(self, username: str, upload_id: str) -> Optional[tuple]:
        """ Returns the file paths and mimetypes for an upload
        Arguments:
            username: the name of the person starting the upload
            upload_id: the ID of the upload
        Return:
            Returns a tuple containing tuples of the found file paths and mimetypes
        """
        if self._conn is None:
            raise RuntimeError('Attempting to get upload mimetypes from the database '\
                                                                                'before connecting')

        # Get the date
        cursor = self._conn.cursor()
        cursor.execute('SELECT source_path, mimetype FROM sandbox_files WHERE sandbox_id IN '\
                        '(SELECT id FROM SANDBOX WHERE name=(?) AND upload_id=(?))',
                                                                            (username, upload_id))

        res = cursor.fetchall()
        if not res or len(res) < 1:
            return ()

        cursor.close()

        return ((one_row[0], one_row[1]) for one_row in res)


    def get_file_species(self, username: str, upload_id: str) -> Optional[tuple]:
        """ Returns the file species information for an upload
        Arguments:
            username: the name of the person starting the upload
            upload_id: the ID of the upload
        Return:
            Returns a tuple containing a dict for each species entry of the upload. Each dict
            has the filename, timestamp, scientific name, count, common name, and location id
        """
        if self._conn is None:
            raise RuntimeError('Attempting to get upload mimetypes from the database '\
                                                                                'before connecting')

        # Get the date
        cursor = self._conn.cursor()
        query = \
            'WITH loc AS (SELECT id, location_id as loc_id ' \
                                                'FROM sandbox WHERE name=(?) AND upload_id=(?)),' \
                    'files AS (SELECT loc.loc_id AS loc_id,sf.id AS id, sf.filename ' \
                                        'FROM sandbox_files sf,loc WHERE sf.sandbox_id=loc.id) ' \
                'SELECT files.loc_id, files.filename, ssp.obs_date, ssp.obs_common, ' \
                                                            'ssp.obs_scientific, ssp.obs_count ' \
                            'FROM sandbox_species ssp, files WHERE ssp.sandbox_file_id=files.id'

        cursor.execute(query, (username, upload_id))

        res = cursor.fetchall()
        if not res or len(res) < 1:
            return ()

        cursor.close()

        return ({'loc_id': one_row[0],
                 'filename': one_row[1],
                 'timestamp': one_row[2],
                 'common': one_row[3],
                 'scientific': one_row[4],
                 'count': one_row[5]
                 } for one_row in res)

    def add_collection_edit(self, bucket: str, upload_path: str, username: str, timestamp: str, \
                                                                            loc_id: str) -> None:
        """ Stores the edit for a collection
        Arguments:
            bucket: the S3 bucket the collection is in
            upload_path: the path to the uploads folder under the bucket
            username: the name of the user making the change
            timestamp: the timestamp of the change
            loc_id: the new location ID
        """
        if self._conn is None:
            raise RuntimeError('Attempting to save collection changes to the database '\
                                                                                'before connecting')

        # Add the entry to the database
        cursor = self._conn.cursor()
        cursor.execute('INSERT INTO collection_edits(bucket, s3_base_path, username, ' \
                                                                        'edit_timestamp, loc_id) '\
                                    'VALUES(?,?,?,?,?)', 
                            (bucket, upload_path, username, timestamp, loc_id))

        self._conn.commit()
        cursor.close()

    def add_image_species_edit(self, bucket: str, file_path: str, username: str, timestamp: str, \
                                                                species: str, count: str) -> None:
        """ Adds a species entry for a file to the database
        Arguments:
            bucket: the S3 bucket the file is in
            file_path: the path to the file the change applies to
            username: the name of the user making the change
            timestamp: the timestamp of the change
            species: the scientific name of the species
            count: the number of individuals of the species
        """
        if self._conn is None:
            raise RuntimeError('Attempting to save file species changes to the database '\
                                                                                'before connecting')

        # Add the entry to the database
        cursor = self._conn.cursor()
        cursor.execute('INSERT INTO image_edits(bucket, s3_file_path, username, edit_timestamp, ' \
                                                                    'obs_scientific, obs_count) '\
                                    'VALUES(?,?,?,?,?,?)', 
                            (bucket, file_path, username, timestamp, species, count))

        self._conn.commit()
        cursor.close()

    def save_user_species(self, username: str, species: str) -> None:
        """ Saves the species entry for the user
        Arguments:
            username: the name of the user to update
            species: the species information to save
        """
        if self._conn is None:
            raise RuntimeError('Attempting to update a user file species to the database '\
                                                                                'before connecting')

        # Add the entry to the database
        cursor = self._conn.cursor()
        cursor.execute('UPDATE users SET species=? WHERE name=?', (species,username))

        self._conn.commit()
        cursor.close()

    def get_image_species_edits(self, bucket: str, upload_path: str) -> dict:
        """ Returns all the saved edits for this bucket and upload path
        Arguments:
            bucket: the S3 bucket the collection is in
            upload_path: the upload path to get the edit for
        Return:
            Returns a dict with the edits. The dict has a key of <bucket>:<upload_path> and
            contains a dict with keys consisting of the file's S3 paths. The value associated with
            the file's paths is a tuple of tuples that contain the scientific name and the count
        """
        if self._conn is None:
            raise RuntimeError('Attempting to fetch image species edits from the database '\
                                                                                'before connecting')

        # Get the edits
        cursor = self._conn.cursor()
        cursor.execute('SELECT s3_file_path,obs_scientific,obs_count FROM image_edits WHERE ' \
                                    'bucket=? AND s3_file_path like ? ORDER BY edit_timestamp ASC',
                            (bucket, upload_path+'%'))

        res = cursor.fetchall()
        if not res or len(res) < 1:
            return {bucket + ':' + upload_path:tuple()}

        file_species = {}
        for one_result in res:
            if one_result[0] in file_species:
                file_species[one_result[0]].append(one_result[1:])
            else:
                file_species[one_result[0]] = [one_result[1:]]

        return {bucket + ':' + upload_path:file_species}

    def get_admin_edit_users(self) -> tuple:
        """ Returns the user information for administrative editing
        Return:
            Returns a tuple of name, email, administrator privileges, and if they were auto-added
            for each user
        """
        if self._conn is None:
            raise RuntimeError('Attempting to fetch image species edits from the database '\
                                                                                'before connecting')

        # Get the edits
        cursor = self._conn.cursor()
        cursor.execute('SELECT name, email, administrator, auto_added FROM users ORDER BY name ASC')

        res = cursor.fetchall()
        if not res or len(res) < 1:
            return []

        return res


    def admin_count(self) -> int:
        """ Returns the count of administrators in the database
        Returns:
            The count of administrators in the database
        """
        if self._conn is None:
            raise RuntimeError('Attempting to count number of admins from the database '\
                                                                                'before connecting')

        # Get the edits
        cursor = self._conn.cursor()
        cursor.execute('SELECT count(1) FROM users where administrator=1')

        res = cursor.fetchall()
        if not res or len(res) < 1:
            return []

        return int(res[0])

    def update_user(self, old_name: str, new_email: str):
        """ Updates the user in the database
        Arguments:
            old_name: the old user name
            new_email: the new email to set for the user
        """
        if self._conn is None:
            raise RuntimeError('Attempting to update the user name & email in the database before '\
                                    'connecting')

        cursor = self._conn.cursor()
        cursor.execute('UPDATE users SET email=? WHERE name=?',
                                                                    (new_email, old_name))
        self._conn.commit()
        cursor.close()

    def update_species(self, username: str, old_scientific: str, new_scientific: str, \
                                        new_name: str, new_keybind: str, new_icon_url: str) -> bool:
        """ Adds the species in the database for later submission
        Arguments:
            username: the name of the user making the change
            old_scientific: the old scientific name of the species
            new_scientific: the new scientific name of the species
            new_name: the new name of the species
            new_keybind: the new keybinding of the species
            new_icon_url: the new icon url
        Return:
            Returns True if no issues were found and False otherwise
        """
        if self._conn is None:
            raise RuntimeError('Attempting to add a species update into the database before ' \
                                                                                    'connecting')

        cursor = self._conn.cursor()
        cursor.execute('SELECT id FROM users WHERE name=?', (username,))

        res = cursor.fetchall()
        if not res or len(res) < 1:
            return False
        user_id = res[0][0]

        cursor.execute('INSERT INTO admin_species_edits(user_id, timestamp, old_scientific_name, ' \
                                                'new_scientific_name, name, keybind, iconURL) ' \
                            'VALUES(?,strftime("%s", "now"),?,?,?,?,?)',
                                    (user_id, old_scientific, new_scientific, new_name, \
                                            new_keybind, new_icon_url))
        self._conn.commit()
        cursor.close()

        return True

    def update_location(self, username: str, loc_name: str, loc_id: str, loc_active: bool, \
                        loc_ele: float, loc_old_lat: float, loc_old_lng: float, \
                        loc_new_lat: float, loc_new_lng: float) -> bool:

        """ Adds the location information to the database for later submission
        Arguments:
            username: the name of the user making the change
            loc_name: the name of the location
            loc_id: the ID of the location
            loc_active: is this an active location
            loc_ele: location elevation in meters
            loc_old_lat: the old latitude
            loc_old_lon: the old longitude
            loc_new_lat: the new latitude
            loc_new_lon: the new longitude
        Return:
            Returns True if no issues were found and False otherwise
        """
        if self._conn is None:
            raise RuntimeError('Attempting to add a location update into the database before ' \
                                                                                    'connecting')

        cursor = self._conn.cursor()
        cursor.execute('SELECT id FROM users WHERE name=?', (username,))

        res = cursor.fetchall()
        if not res or len(res) < 1:
            return False
        user_id = res[0][0]

        cursor.execute('INSERT INTO admin_location_edits(user_id, timestamp, loc_name, loc_id, ' \
                                        'loc_active, loc_ele, loc_old_lat, loc_old_lng, ' \
                                        'loc_new_lat, loc_new_lng) ' \
                            'VALUES(?,strftime("%s", "now"),?,?,?,?,?,?,?,?)',
                                    (user_id, loc_name, loc_id, loc_active, loc_ele, loc_old_lat, \
                                            loc_old_lng, loc_new_lat,loc_new_lng))
        self._conn.commit()
        cursor.close()

        return True

    def get_admin_changes(self, username: str) -> dict:
        """ Returns any saved administrative location and species changes
        Arguments:
            username: the name of the user to fetch for
        Return:
            Returns a dict of 'locations' and 'species' changes as tuples off the keys. Also returns
            keys for the index of the columns in the returned data - 'loc_*' for locations, 
            and 'sp_*' for species
        """
        if self._conn is None:
            raise RuntimeError('Attempting to get administrative changes from the database before '\
                                                                                    'connecting')

        cursor = self._conn.cursor()

        location_idxs = {'loc_name':0, 'loc_id':1, 'loc_active':2, 'loc_elevation':3, \
                         'loc_old_lat':4, 'loc_old_lng':5, 'loc_new_lat':6, 'loc_new_lng':7 }
        cursor.execute('WITH u AS (SELECT id FROM users WHERE name=?) ' \
                        'SELECT loc_name, loc_id, loc_active, loc_ele, loc_old_lat, loc_old_lng, ' \
                            'loc_new_lat, loc_new_lng FROM admin_location_edits lae, u '\
                        'WHERE lae.user_id = u.id and lae.location_updated = 0 ' \
                        'ORDER BY timestamp ASC', (username,))
        res = cursor.fetchall()
        if not res:
            locations = []
        else:
            locations = res

        species_idxs = {'sp_old_scientific':0, 'sp_new_scientific':1, 'sp_name':2, 'sp_keybind': 3,\
                        'sp_icon_url':4}
        cursor.execute('WITH u AS (SELECT id FROM users WHERE name=?) ' \
                        'SELECT old_scientific_name, new_scientific_name, name, keybind, iconURL '\
                        'FROM admin_species_edits ase, u ' \
                        'WHERE ase.user_id = u.id and ase.s3_updated = 0 ' \
                        'ORDER BY timestamp ASC', (username, ))
        res = cursor.fetchall()
        if not res:
            species = []
        else:
            species = res

        return {'locations': locations, 'species': species} | location_idxs | species_idxs

    def have_admin_changes(self, username: str) -> dict:
        """ Returns any saved administrative location and species changes
        Arguments:
            username: the name of the user to fetch for
        Return:
            Returns a dict of 'locationsCount' and 'speciesCount'
        """
        if self._conn is None:
            raise RuntimeError('Attempting to get administrative change counts from the database '\
                                                                                'before connecting')

        cursor = self._conn.cursor()
        cursor.execute('WITH u AS (SELECT id FROM users WHERE name=?) ' \
                        'SELECT count(1) FROM admin_location_edits lae, u ' \
                        'WHERE lae.user_id = u.id and lae.location_updated = 0', (username,))
        res = cursor.fetchall()
        if not res or len(res) <= 0:
            locations_count = 0
        else:
            locations_count = res[0][0]

        cursor = self._conn.cursor()
        cursor.execute('WITH u AS (SELECT id FROM users WHERE name=?) ' \
                        'SELECT count(1) FROM admin_species_edits ase, u ' \
                        'WHERE ase.user_id = u.id and ase.s3_updated = 0', (username,))
        res = cursor.fetchall()
        if not res or len(res) <= 0:
            species_count = 0
        else:
            species_count = res[0][0]

        return {'locationsCount': locations_count, 'speciesCount': species_count}

    def clear_admin_location_changes(self, username: str) -> None:
        """ Cleans up the administration location changes for this use
        Arguments:
            username: the name of the user to mark the locations for
        """
        if self._conn is None:
            raise RuntimeError('Attempting to clear administrative locations in the database '\
                                                                                'before connecting')

        cursor = self._conn.cursor()
        query = 'UPDATE admin_location_edits SET location_updated = 1 WHERE user_id in ' \
                    '(SELECT id FROM users where name=?)'
        cursor.execute(query, (username,))

        self._conn.commit()
        cursor.close()

    def clear_admin_species_changes(self, username: str) -> None:
        """ Cleans up the administration species changes for this use
        Arguments:
            username: the name of the user to mark the species for
        """
        if self._conn is None:
            raise RuntimeError('Attempting to clear administrative species in the database '\
                                                                                'before connecting')

        cursor = self._conn.cursor()
        query = 'UPDATE admin_species_edits SET s3_updated = 1 WHERE user_id in ' \
                    '(SELECT id FROM users where name=?)'
        cursor.execute(query, (username,))

        self._conn.commit()
        cursor.close()
