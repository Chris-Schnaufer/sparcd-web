"""This script contains the interface to an S3 instance
"""

import csv
import dataclasses
from io import StringIO
import json
import os
import tempfile
from typing import Optional
from minio import Minio, S3Error

SPARCD_PREFIX='sparcd-'


def get_s3_file(minio: Minio, bucket: str, file: str, dest_file: str):
    """Downloads files from S3 server
    Arguments:
        minio: the s3 client instance
        bucket: the bucket to download from
        file: the S3 file to download and read
        dest_file: the file to write the download to
    Returns:
        Returns the content of the file or None if there was an error
    """
    try:
        minio.fget_object(bucket, file, dest_file)
        with open(dest_file, 'r', encoding='utf-8') as in_file:
            return in_file.read()
    except S3Error as ex:
        print(('EXCEPTION',ex))
        if ex.code != "NoSuchKey":
            raise ex
    return None


def get_user_collections(minio: Minio, user: str, buckets: tuple) -> tuple():
    """ Gets the collections that the user can access
    Arguments:
        minio: the s3 client instance
        user: the name of the user to check permissions for
        buckets: the list of buckets to check
    Return:
        Returns a tuple containing the collections and buckets that the user has permissions for
    """
    user_collections = []

    # Loop through and get all the information for a collection
    perms_file = tempfile.mkstemp(prefix=SPARCD_PREFIX)
    os.close(perms_file[0])
    for one_bucket in buckets:
        collections_path = 'Collections'
        base_path = os.path.join(collections_path,  one_bucket[len(SPARCD_PREFIX):])
        permissions_path = os.path.join(base_path, 'permissions.json')

        perm_data = get_s3_file(minio, one_bucket, permissions_path, perms_file[1])

        if perm_data is not None:
            perms = json.loads(perm_data)
            found_perm = None
            for one_perm in perms:
                if one_perm and 'usernameProperty' in one_perm and \
                                            one_perm['usernameProperty'] == user:
                    found_perm = one_perm
                    break
            user_collections.append({'bucket':one_bucket,
                                     'base_path': base_path,
                                     'permissions': found_perm,
                                     'all_permissions': perms
                                    })
    os.unlink(perms_file[1])

    return tuple(user_collections)


def update_user_collections(minio: Minio, collections: tuple) -> tuple:
    """Updates the collections returned by get_user_collections() 
    Arguments:
        minio: the s3 client instance
        collections: the tuple of collections
    Return:
        Returns the tuple of updated collections
    """
    user_collections = []

    temp_file = tempfile.mkstemp(prefix=SPARCD_PREFIX)
    os.close(temp_file[0])
    for one_coll in collections:
        new_coll = one_coll
        coll_info_path = os.path.join(one_coll['base_path'], 'collection.json')
        coll_data = get_s3_file(minio, one_coll['bucket'], coll_info_path, temp_file[1])
        if coll_data is not None:
            coll_info = json.loads(coll_data)
            new_coll = new_coll | coll_info

        # Get the uploads and their information
        coll_uploads = []
        uploads_path = os.path.join(one_coll['base_path'], 'Uploads/')
        for one_obj in minio.list_objects(one_coll['bucket'], uploads_path):
            if one_obj.is_dir and not one_obj.object_name == uploads_path:
                # Get the data on this upload

                # Upload information
                upload_info_path = os.path.join(one_obj.object_name, 'UploadMeta.json')
                coll_info_data = get_s3_file(minio, one_coll['bucket'], upload_info_path, \
                                             temp_file[1])
                if coll_info_data is not None:
                    coll_info = json.loads(coll_info_data)
                else:
                    print(f'Unable to get upload information: {upload_info_path}')
                    continue

                # Location data
                upload_info_path = os.path.join(one_obj.object_name, 'deployments.csv')
                csv_data = get_s3_file(minio, one_coll['bucket'], upload_info_path, \
                                             temp_file[1])
                if csv_data is not None:
                    reader = csv.reader(StringIO(csv_data))
                    csv_info = next(reader)
                    coll_uploads.append({'path':one_obj.object_name, 'info':coll_info, \
                                            'location':csv_info[1]})
                else:
                    print(f'Unable to get deployment information: {upload_info_path}')

        new_coll['uploads'] = coll_uploads
        user_collections.append(new_coll)

    os.unlink(temp_file[1])

    return user_collections


@dataclasses.dataclass
class S3Connection:
    """Functions handling access connections to an s3 instance
    """

    @staticmethod
    def get_collections(url: str, user: str, password: str) -> Optional[tuple]:
        """Returns the collection information
        Arguments:
            url: the URL to the s3 instance
            user: the name of the user to use when connecting
            password: the user's password
        Returns:
            Returns the collections, or None
        """
        found_buckets = []

        minio = Minio(url, access_key=user, secret_key=password)
        all_buckets = minio.list_buckets()

        # Get the SPARCd buckets
        found_buckets = [one_bucket.name for one_bucket in all_buckets if \
                                                one_bucket.name.startswith(SPARCD_PREFIX)]

        user_collections = get_user_collections(minio, user, found_buckets)

        return update_user_collections(minio, user_collections)
