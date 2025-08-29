#!/usr/bin/python3

import os
import argparse
import datetime
import logging
import sys

from sparcd_db import SPARCdDatabase

# The name of our script
SCRIPT_NAME = os.path.basename(__file__)

# The default timeout period before we stop processing
DEFAULT_TIMEOUT_PERIOD = 30

# Argparse-related definitions
# Declare the progam description
ARGPARSE_PROGRAM_DESC = 'Processes image files on S3 adding their SPARC\'d EXIF data'
# Declare the help text for the database filename parameter
ARGPARSE_DATABASE_FILE_HELP = 'Path to the Sqlite database file to read image file changes from'
# Increasing the debug level to DEBUG
ARGPARSE_LOGGING_DEBUG_HELP = 'Increases the logging level to include debugging messages'
# The length of time to run before stopping
ARGPARSE_TIMEOUT_HELP = 'Number of minutes to run before stopping.  Defaults to ' \
                        f'{DEFAULT_TIMEOUT_PERIOD} minutes'

def get_arguments(logger: logging.Logger) -> tuple:
    """ Returns the data from the parsed command line arguments
    Returns:
        A tuple consisting of a string containing the EXCEL file name to process, and
        a dict of the command line options
    Exceptions:
        A ValueError exception is raised if the filename is not specified
    Notes:
        If an error is found, the script will exit with a non-zero return code
    """
    parser = argparse.ArgumentParser(prog=SCRIPT_NAME,
                                     description=ARGPARSE_PROGRAM_DESC)
    parser.add_argument('database', help=ARGPARSE_DATABASE_FILE_HELP)
    parser.add_argument('--debug', help=ARGPARSE_LOGGING_DEBUG_HELP)
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT_PERIOD,
                                    help=ARGPARSE_TIMEOUT_HELP)
    args = parser.parse_args()

    # Find the EXCEL file and the password (which is allowed to be eliminated)
    database_file = None
    if not args.database:
        # Raise argument error
        raise ValueError('Missing a required argument')

    if len(args.database) == 1:
        database_file = args.database[0]
    else:
        # Report the problem
        logger.error('Too many arguments specified for Sqlite database')
        parser.print_help()
        sys.exit(10)

    if not os.path.exists(database_file):
        # Report the problem
        logger.error(f'The Sqlite database doesn\'t exit: {database_file}')
        sys.exit(11)

    cmd_opts = {
                'debug': args.debug,
                'timeout': args.timeout,
               }

    # Return the loaded JSON
    return database_file, cmd_opts


def init_logging(level: int=logging.INFO) -> logging.Logger:
    """Initializes the logging
    Arguments:
        filename: name of the file to save logging to
        level: the logging level to use
    Return:
        Returns the created logger instance
    """
    logger = logging.getLogger()
    logger.setLevel(level if level is not None else logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(levelname)s: %(message)s')

    # Console handler
    cur_handler = logging.StreamHandler()
    cur_handler.setFormatter(formatter)
    logger.addHandler(cur_handler)

    return logger

def process_upload_changes(db: SPARCdDatabase, location_info: tuple, files_info: tuple) -> None:
    """ Updates the image files with the information passed in
    Argument:
        location_info: the location information for all the images in an upload
        files_info: the file species changes
    Notes:
        If the location information doesn't have a location ID then only the files are processed.
        If the location does have a location ID then all the files in the location are processed.
    """


def update_files(database_path: str, logging: logging.RootLogger, timeout: int) -> None:
    """ Updates the files on S3 based upon the changes in the database
    Arguments:
        database_path: the full path to the database to use to change images
        logging: the logging instance to use
        timeout: the number of minutes to process images befofe stopping
    """
    logging.info(f'Processing image changes found in {database_path}')
    db = SPARCdDatabase(database_path)
    db.connect()

    end_time = datetime.today() + datetime.timedelta(minutes=timeout)
    try:
        if datatime.today() > end_time:
            logging.info('We have timed out processing images')
            logging.info('Completed processing images')
            return

        upload_location_info = db.get_next_upload_location()    # Only keep the latest and mark the others as completed

        upload_files_info = db.get_next_files_info(upload_location_info['bucket'],
                                                                upload_location_info['base_path'])
        if upload_files_info:
            process_upload_changes(db, upload_location_info, upload_files_info)
        else:
            logging.info('Completed processing images')
            return
    except sqlite3.OperationalError as ex:
        logging.error('An OperationalError exception was caught from the database')
        if logging.level == logging.DEBUG:
            logging.error('', exc_info=True)
        sysExit(100)        

if __name__ == "__main__":
    db_path, user_opts = get_arguments(logging.getLogger())
    user_opts['logger'] = init_logging(user_opts['debug'])
    update_files(db_path, user_opts['logger'], user_opts['timeout'])
