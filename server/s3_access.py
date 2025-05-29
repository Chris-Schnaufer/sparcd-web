"""This script contains the interface to an S3 instance
"""

import csv
import dataclasses
from io import StringIO
import json
import os
import tempfile
from typing import Optional
import uuid
from minio import Minio, S3Error

SPARCD_PREFIX='sparcd-'

BUCKET_PREFIX = SPARCD_PREFIX
SETTINGS_BUCKET_PREFIX = BUCKET_PREFIX + 'settings'
SETTINGS_BUCKET_LEGACY = 'sparcd'
SETTINGS_FOLDER = 'Settings'

DEPLOYMENT_CSV_FILE_NAME = 'deployments.csv'
MEDIA_CSV_FILE_NAME = 'media.csv'
OBSERVATIONS_CSV_FILE_NAME = 'observations.csv'
CAMTRAP_FILE_NAMES = [DEPLOYMENT_CSV_FILE_NAME, MEDIA_CSV_FILE_NAME, OBSERVATIONS_CSV_FILE_NAME]
S3_UPLOADS_PATH_PART = 'Uploads/'


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
    temp_file = tempfile.mkstemp(prefix=SPARCD_PREFIX)
    os.close(temp_file[0])
    for one_bucket in buckets:
        collections_path = 'Collections'
        base_path = os.path.join(collections_path, one_bucket[len(SPARCD_PREFIX):])

        coll_info_path = os.path.join(base_path, 'collection.json')
        coll_data = get_s3_file(minio, one_bucket, coll_info_path, temp_file[1])
        if coll_data is None or not coll_data:
            continue
        coll_data = json.loads(coll_data)

        permissions_path = os.path.join(base_path, 'permissions.json')
        perm_data = get_s3_file(minio, one_bucket, permissions_path, temp_file[1])

        if perm_data is not None:
            perms = json.loads(perm_data)
            found_perm = None
            for one_perm in perms:
                if one_perm and 'usernameProperty' in one_perm and \
                                            one_perm['usernameProperty'] == user:
                    found_perm = one_perm
                    break
            coll_data.update({'bucket':one_bucket,
                              'base_path': base_path,
                              'permissions': found_perm,
                              'all_permissions': perms
                             })
            user_collections.append(coll_data)
    os.unlink(temp_file[1])

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

        # Get the uploads and their information
        coll_uploads = []
        uploads_path = os.path.join(one_coll['base_path'], S3_UPLOADS_PATH_PART)
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
                upload_info_path = os.path.join(one_obj.object_name, DEPLOYMENT_CSV_FILE_NAME)
                csv_data = get_s3_file(minio, one_coll['bucket'], upload_info_path, \
                                             temp_file[1])
                if csv_data is not None:
                    reader = csv.reader(StringIO(csv_data))
                    for csv_info in reader:
                        if csv_info and len(csv_info) >= 23:
                            coll_uploads.append({
                                         'path':one_obj.object_name,
                                         'info':coll_info,
                                         'location':csv_info[1],
                                         'elevation':csv_info[12],
                                         'key':os.path.basename(one_obj.object_name.rstrip('/\\'))
                                        })
                            break
                else:
                    print(f'Unable to get deployment information: {upload_info_path}')

        new_coll['uploads'] = coll_uploads
        user_collections.append(new_coll)

    os.unlink(temp_file[1])

    return user_collections


def get_images(minio: Minio, bucket: str, upload_paths: tuple) -> tuple:
    """ Finds the images by recursing the specified paths
    Arguments:
        minio: the S3 client instance
        bucket: the bucket to search
        upload_paths: a tuple of upload paths to search
    Return:
        Returns the tuple of found images
    """
    images = []
    cur_paths = [upload_paths]

    # Get the image names and urls
    # pylint: disable=modified-iterating-list
    for cur_path in cur_paths:
        for one_obj in minio.list_objects(bucket, cur_path):
            if one_obj.is_dir:
                if not one_obj.object_name == cur_path:
                    cur_paths.append(one_obj.object_name)
            else:
                _, file_name = os.path.split(one_obj.object_name)
                name, ext = os.path.splitext(file_name)
                if ext.lower().endswith('.jpg'):
                    s3_url = minio.presigned_get_object(bucket, one_obj.object_name)
                    images.append({'name':name,
                                   'bucket':bucket, \
                                   's3_path':one_obj.object_name,
                                   's3_url':s3_url,
                                   'key':uuid.uuid4().hex})

    return images


def get_common_name(csv_comment: str) -> Optional[str]:
    """ Returns the common name from a CSV observation comment
    Arguments:
        csv_comment: the comment to parse
    Return:
        The found common name or None
    Notes:
        The expected common name format is [COMMONNAME:<name>]
    """
    common_name = None

    # Extract the common name if it exists
    if '[' in csv_comment and ']' in csv_comment and 'COMMONNAME:' in csv_comment:
        lindex = csv_comment.find('[')
        rindex = csv_comment.find(']')
        cindex = csv_comment.find('COMMONNAME:')
        if lindex < cindex < rindex:
            start_index = cindex + len('COMMONNAME:')
            common_name = csv_comment[start_index:rindex]

    return common_name


@dataclasses.dataclass
class S3Connection:
    """ Contains functions for handling access connections to an s3 instance
    """

    @staticmethod
    def list_collections(url: str, user: str, password: str) -> Optional[tuple]:
        """ Returns the collection information
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

        return user_collections

    @staticmethod
    def get_collections(url: str, user: str, password: str) -> Optional[tuple]:
        """ Returns the collection information
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

    @staticmethod
    def get_images(url: str, user: str, password: str, collection_id: str, \
                   upload_name: str) -> Optional[tuple]:
        """ Returns the image information for an upload of a collection
        Arguments:
            url: the URL to the s3 instance
            user: the name of the user to use when connecting
            password: the user's password
            collection_id: the ID of the collection of the upload
            upload_name: the name of the upload to get image data on
        Returns:
            Returns the images, or None
        """
        bucket = SPARCD_PREFIX + collection_id
        upload_path = os.path.join('Collections', collection_id, 'Uploads', upload_name)

        minio = Minio(url, access_key=user, secret_key=password)

        images = get_images(minio, bucket, [upload_path])

        images_dict = {obj['s3_path']: obj for obj in images}

        temp_file = tempfile.mkstemp(prefix=SPARCD_PREFIX)
        os.close(temp_file[0])

        # Get the species information for each image
        upload_info_path = os.path.join(upload_path, OBSERVATIONS_CSV_FILE_NAME)
        csv_data = get_s3_file(minio, bucket, upload_info_path, temp_file[1])
        if csv_data is not None:

            reader = csv.reader(StringIO(csv_data))
            for csv_info in reader:
                common_name = get_common_name(csv_info[19])

                # Update the image with a species if we find it
                cur_img = images_dict.get(csv_info[3])
                if cur_img is not None:

                    # Add the species
                    if cur_img.get('species') is None:
                        cur_img['species'] = []
                    cur_img['species'].append({ 'name':common_name, \
                                                'scientificName':csv_info[8], \
                                                'count':csv_info[9]})
                else:
                    print(f'Unable to find collection image: {csv_info[3]}')
        else:
            print(f'Unable to get observations information: {upload_info_path}')

        os.unlink(temp_file[1])

        return images


    @staticmethod
    def list_uploads(url: str, user: str, password: str, bucket: str) -> Optional[tuple]:
        """ Returns the upload information for a collection
        Arguments:
            url: the URL to the s3 instance
            user: the name of the user to use when connecting
            password: the user's password
            bucket: the bucket of the uploads
        Returns:
            Returns the uploads, or None
        """
        if not bucket.startswith(SPARCD_PREFIX):
            print(f'Invalid bucket name specified: {bucket}')
            return None

        uploads_path = os.path.join('Collections', bucket[len(SPARCD_PREFIX):], \
                                                                S3_UPLOADS_PATH_PART)

        minio = Minio(url, access_key=user, secret_key=password)

        temp_file = tempfile.mkstemp(prefix=SPARCD_PREFIX)
        os.close(temp_file[0])
        # Get the uploads and their information
        coll_uploads = []
        for one_obj in minio.list_objects(bucket, uploads_path):
            if one_obj.is_dir and not one_obj.object_name == uploads_path:
                # Get the data on this upload

                # Upload information
                upload_info_path = os.path.join(one_obj.object_name, 'UploadMeta.json')
                meta_info_data = get_s3_file(minio, bucket, upload_info_path, \
                                             temp_file[1])
                if meta_info_data is not None:
                    meta_info_data = json.loads(meta_info_data)
                else:
                    print(f'Unable to get upload information: {upload_info_path}')
                    continue

                # Add the name
                meta_info_data['name'] = os.path.basename(one_obj.object_name.rstrip('/\\'))

                # Location data
                meta_info_data['loc'] = None
                upload_info_path = os.path.join(one_obj.object_name, DEPLOYMENT_CSV_FILE_NAME)
                csv_data = get_s3_file(minio, bucket, upload_info_path, temp_file[1])
                if csv_data is not None:
                    reader = csv.reader(StringIO(csv_data))
                    for csv_info in reader:
                        if len(csv_info) >= 23:
                            meta_info_data['loc'] = csv_info[1]
                            meta_info_data['elevation'] =  csv_info[12]
                            break
                else:
                    print(f'Unable to get deployment information: {upload_info_path}')
                    continue

                # Uploaded images data
                cur_images = []
                upload_info_path = os.path.join(one_obj.object_name, OBSERVATIONS_CSV_FILE_NAME)
                csv_data = get_s3_file(minio, bucket, upload_info_path, temp_file[1])
                if csv_data is not None:
                    cur_row = 0
                    reader = csv.reader(StringIO(csv_data))
                    for csv_info  in reader:
                        cur_row = cur_row + 1
                        if len(csv_info) >= 20:
                            # Get the fields of interest
                            cur_species = { 'name':get_common_name(csv_info[19]), \
                                            'scientificName':csv_info[8], \
                                            'count':csv_info[9]}

                            cur_images.append({ 'name':os.path.basename(csv_info[3].rstrip('/\\')),
                                                'timestamp':csv_info[4],
                                                'species':cur_species})
                        elif csv_info:
                            print(f'Invalid CSV row ({cur_row}) read from {upload_info_path}')
                else:
                    print(f'Unable to get deployment information: {upload_info_path}')
                meta_info_data['images'] = cur_images
                coll_uploads.append(meta_info_data)

        os.unlink(temp_file[1])

        return coll_uploads

    @staticmethod
    def get_configuration(filename: str, url: str, user: str, password: str):
        """ Returns the configuration contained in the file
        Arguments:
            filename: the name of the configuration to download
            url: the URL to the s3 instance
            user: the name of the user to use when connecting
            password: the user's password
        """
        minio = Minio(url, access_key=user, secret_key=password)

        # Find the name of our settings bucket
        settings_bucket = None
        for one_bucket in minio.list_buckets():
            if one_bucket.name == SETTINGS_BUCKET_LEGACY:
                settings_bucket = one_bucket.name
                break
            if one_bucket.name.startswith(SETTINGS_BUCKET_PREFIX):
                settings_bucket = one_bucket.name

        temp_file = tempfile.mkstemp(prefix=SPARCD_PREFIX)
        os.close(temp_file[0])

        file_path = os.path.join(SETTINGS_FOLDER, filename)
        config_data = None
        try:
            config_data = get_s3_file(minio, settings_bucket, file_path, temp_file[1])
        except S3Error as ex:
            print(f'Unable to get configuration file {filename} from {settings_bucket}')
            print(ex)
        finally:
            os.unlink(temp_file[1])

        return config_data

    @staticmethod
    def get_object_urls(url: str, user: str, password: str, object_info: tuple) -> tuple:
        """ Returns the URLs of the objects listed in object_info
        Arguments:
            url: the URL to the s3 instance
            user: the name of the user to use when connecting
            password: the user's password
            object_info: tuple containing tuple pairs of bucket name and the object path
        Return:
            Returns a tuple containing the S3 URLs for the objects (each url subject to timeout)
        """
        minio = Minio(url, access_key=user, secret_key=password)

        return [minio.presigned_get_object(one_obj[0], one_obj[1]) for one_obj in object_info]
