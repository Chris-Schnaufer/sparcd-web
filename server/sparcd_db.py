"""This script contains the database interface for the SPARCd Web app
"""

import logging
import sqlite3
from typing import Optional

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
                'user_agent) VALUES(?,?,?,?,strftime(\'%s\', \'now\'),?,?)'
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
        query = 'UPDATE tokens SET timestamp=strftime(\'%s\', \'now\') WHERE token=?'
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
            A dict containing the user's name, email, settings, and admin level
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
