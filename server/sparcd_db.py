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
            self._conn.close()
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
                       'SELECT u.name, u.email, u.settings, u.administrator, ti.s3_url, ' \
                          'ti.timestamp, ti.elapsed_sec, ti.client_ip, ti.user_agent ' \
                          'FROM users u JOIN ti ON u.name = ti.name',
                    (token,))
        res = cursor.fetchone()
        cursor.close()

        if res and len(res) >= 8:
            return {'name':res[0], 'email':res[1], 'settings':res[2], 'admin':res[3], \
                    'url':res[4], 'timestamp':res[5], 'elapsed_sec':res[6], \
                    'client_ip':res[7], 'user_agent':res[8]}

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
        cursor.execute('SELECT name, email, settings, administrator FROM users WHERE name=(?)',
                                                                                        (username,))
        res = cursor.fetchone()
        cursor.close()

        if res and len(res) >= 4:
            return {'name': res[0], 'email':res[1], 'settings':res[2], 'admin':res[3]}

        return None

    def auto_add_user(self, username: str, email: str=None) -> Optional[dict]:
        """ Add a user that doesn't exist. The user received default permissions as defined
            in the DB
        Arguments:
            username: the name of the user to add
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
            cursor.execute('INSERT INTO users(name, email) VALUES(?,?)', (username,email))
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

    def update_user_settings(self, username: str, settings: str) ->None:
        """ Updates the user's settings in the database
        Arguments
            username: the name of the user to update
            settings: the new settings to set
        """
        if self._conn is None:
            raise RuntimeError('update_user_settings: Attempting to access database before '\
                                    'connecting')


        cursor = self._conn.cursor()
        cursor.execute('UPDATE users SET settings=(?) WHERE name=(?)', (settings,username))
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
        return tuple()

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
            cursor.execute('DELETE FROM table_timeout WHEREname=(?)', (bucket,))
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

    def get_sandbox_upload(self, username: str, path: str, new_upload_id: bool=False) -> \
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

    def new_sandbox_upload(self, username: str, path: str, files: tuple, s3_bucket: str, \
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

    def get_sandbox_s3_info(self, username: str, upload_id: str) -> tuple:
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

    def complete_sandbox_upload(self, username: str, upload_id: str) -> None:
        """ Marks the sandbox upload as completed by resetting the path
        Arguments:
            username: the name of the person starting the upload
            upload_id: the ID of the upload
        """
        if self._conn is None:
            raise RuntimeError('Attempting to reset sandbox upload the database before connecting')

        # Get the date
        cursor = self._conn.cursor()
        cursor.execute('UPDATE sandbox SET path=null WHERE name=(?) AND upload_id=(?)',
                                                                            (username, upload_id))

        self._conn.commit()
        cursor.close()

    def file_uploaded(self, username: str, upload_id: str, filename: str) -> None:
        """ Marks the file as upload as uploaded
        Arguments:
            username: the name of the person starting the upload
            upload_id: the ID of the upload
            filename: the name of the uploaded file to mark as uploaded
        """
        if self._conn is None:
            raise RuntimeError('Attempting to reset sandbox upload the database before connecting')

        # Get the date
        cursor = self._conn.cursor()
        cursor.execute('UPDATE sandbox_files SET uploaded=TRUE WHERE sandbox_files.filename=(?) '\
                            'AND sandbox_id in ' \
                        '(SELECT id FROM SANDBOX WHERE name=(?) AND upload_id=(?))',
                                                                    (filename, username, upload_id))

        self._conn.commit()
        cursor.close()
