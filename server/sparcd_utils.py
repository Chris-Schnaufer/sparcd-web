""" Utility functions for SPARCd server """

import datetime
import json
import math
import os
import time
from typing import Optional

import dateutil.parser
import dateutil.tz


# Maximum number of times to try updating a temporary file
TEMP_FILE_MAX_WRITE_TRIES = 7
# Number of seconds to keep the temporary file around before it's invalid
TEMP_FILE_EXPIRE_SEC = 1 * 60 * 60


def secure_user_settings(settings: dict) -> dict:
    """ Secures the user settings information
    Arguments:
        settings: the user settings
    Return:
        The secured user settings
    """
    if isinstance(settings, str):
        cur_settings = json.loads(settings)
    else:
        cur_settings = settings

    if 'email' in cur_settings and cur_settings['email'] and len(cur_settings['email']) > 2:
        if '@' in cur_settings['email']:
            first_part = cur_settings['email'][:cur_settings['email'].index('@')]
            second_part = cur_settings['email'][cur_settings['email'].index('@'):]
        else:
            first_part = cur_settings['email'][:max(1,math.floor(len(cur_settings['email']) / 2))]
            second_part = cur_settings['email'][max(1,math.ceil(len(cur_settings['email']) / 2)):]
        match len(first_part):
            case 1:
                pass
            case 2:
                first_part = first_part[:1] + '*'
            case 3:
                first_part = first_part[:2] + '*'
            case 4:
                first_part = first_part[:3] + '*'
            case _:
                first_part = first_part[:3] + '*'*(min(7, len(first_part)-3))

        cur_settings['email'] = first_part + second_part

    return cur_settings


def save_timed_info(save_path: str, data, num_retries: int=TEMP_FILE_MAX_WRITE_TRIES) -> None:
    """ Attempts to save information to a file with a timestamp
    Arguments:
        save_path: the path to the save file
        data: the data to save with a timestamp
        num_retries: optional parameter for the number of times to retry writing the data out
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
    while attempts < num_retries:
        try:
            with open(save_path, 'w', encoding='utf-8') as outfile:
                outfile.write(json.dumps(save_info))
            attempts = num_retries
        except Exception as ex:
            if not informed_exception:
                print(f'Unable to open temporary file for writing: {save_path}')
                print(ex)
                print(f'Will keep trying for up to {TEMP_FILE_MAX_WRITE_TRIES} times')
                informed_exception = True
                time.sleep(1)
            attempts = attempts + 1


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



def get_later_timestamp(cur_ts: object, new_ts: object) -> Optional[object]:
    """ Returns the later of the two dates
    Arguments:
        cur_ts: the date and time to compare against
        new_ts: the date and time to check if it's later
    Return:
        Returns the later date. If cur_ts is None, then new_ts is returned.
        If new_ts is None, then cur_ts is returned
    """
    # pylint: disable=too-many-return-statements,too-many-branches
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
