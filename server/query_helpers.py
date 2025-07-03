""" Functions to help queries """

import datetime
import json
from typing import Optional

from format_dr_sanderson import get_dr_sanderson_output, get_dr_sanderson_pictures
from format_csv import get_csv_raw, get_csv_location, get_csv_species
from format_image_downloads import get_image_downloads
from text_formatters.results import Results

def filter_elevation(uploads: tuple, elevation_filter: dict) -> list:
    """ Returns the uploads that match the filter
    Arguments:
        uploads: the uploads to iterate through
        elevation_filter: the elevation filtering information
    Returns:
        Returns uploads that match the elevation filtering criteria
    Notes:
        The elevation filter needs 'type', 'value', and 'units' fields
        with ('=','<','>','<=','>='), elevation, and ('meters' or 'feet')
    """
    # Get the comparison value in meters
    if elevation_filter['units'] == 'meters':
        cur_elevation = elevation_filter['value']
    else:
        cur_elevation = elevation_filter['value'] * 0.3048

    # Filter the uploads based upon the filter type
    match(elevation_filter['type']):
        case '=':
            return [one_upload for one_upload in uploads if \
                                float(one_upload['info']['elevation']) == cur_elevation]
        case '<':
            return [one_upload for one_upload in uploads if \
                                float(one_upload['info']['elevation']) < cur_elevation]
        case '>':
            return [one_upload for one_upload in uploads if \
                                float(one_upload['info']['elevation']) > cur_elevation]
        case '<=':
            return [one_upload for one_upload in uploads if \
                                float(one_upload['info']['elevation']) <= cur_elevation]
        case '>=':
            return [one_upload for one_upload in uploads if \
                                float(one_upload['info']['elevation']) >= cur_elevation]
        case _:
            raise ValueError('Invalid elevation filter comparison specified: ' \
                             f'{elevation_filter["type"]}')


def get_filter_dt(filter_name: str, filters: tuple) -> Optional[datetime.datetime]:
    """ Returns the datetime of the associated filter
    Arguments:
        filter_name: the name of the filter to find
        filterrs: the list of filters to search
    Return:
        The timestamp as a datetime object, or None if the filter or timestamp is 
        missing or invalid
    """
    found_filter = [one_filter for one_filter in filters if one_filter[0] == filter_name]
    if len(found_filter) > 0:
        return datetime.datetime.fromisoformat(found_filter[0][1])

    return None


def filter_uploads(uploads_info: tuple, filters: tuple) -> tuple:
    """ Filters the uploads against the filters and returns the selected
        images and their associated data
    Arguments:
        uploads_info: the tuple of uploads to filter
        filters: the filters to apply to the uploads
    Notes:
        Does not filter on collection
    """
    cur_uploads = uploads_info

    # Filter at the upload level
    for one_filter in filters:
        match(one_filter[0]):
            case 'locations':
                cur_uploads = [one_upload for one_upload in cur_uploads if \
                                one_upload['info']['loc'] in one_filter[1]]
            case 'elevation':
                cur_uploads = filter_elevation(cur_uploads, json.loads(one_filter[1]))

    # Determine if we'll need image datetime objects
    need_gmt_dt = any(one_filter for one_filter in filters if one_filter[0] in \
                        ['enddata','startdate'])

    # Filter at the image level
    filtering_names = [one_filter[1] for one_filter in filters]
    years_filter = None
    try:
        start_date_ts = None if 'startDate' not in filtering_names else \
                                                        get_filter_dt('startDate', filters)
        end_date_ts = None if 'endDate' not in filtering_names else \
                                                        get_filter_dt('endDate', filters)
    except Exception as ex:
        print('Invalid start or end filter date')
        print(ex)
        raise ex

    matches = []
    for one_upload in cur_uploads:
        cur_images = []
        for one_image in one_upload['info']['images']:
            excluded = False
            image_dt = None
            image_gmt_dt = None
            # pylint: disable=broad-exception-caught
            try:
                image_dt = datetime.datetime.fromisoformat(one_image['timestamp'])
                if need_gmt_dt:
                    image_gmt_dt = datetime.datetime.utcfromtimestamp(image_dt.timestamp())
            except Exception:
                print(f'Error converting image timestamp: {one_image["name"]} ' \
                      f'{one_image["timestamp"]} from upload {one_upload["bucket"]} '\
                      f'{one_upload["name"]}')
                print(ex)
                excluded = True
                continue

            # Filter the image
            for one_filter in filters:
                match(one_filter[0]):
                    case 'dayofweek':
                        if not image_dt.weekday() in one_filter[1]:
                            excluded = True
                    case 'hour':
                        if image_dt.hour not in one_filter[1]:
                            excluded = True
                    case 'month':
                        if image_dt.month not in one_filter[1]:
                            excluded = True
                    case 'species':
                        found = False
                        for one_species in one_image['species']:
                            if one_species['scientificName'] in one_filter[1]:
                                found = True

                        if not found:
                            excluded = True
                    case 'years':
                        if years_filter is None:
                            years_filter = json.loads(one_filter[1])
                        if not years_filter['yearStart'] <= image_dt.year <= \
                                                                            years_filter['yearEnd']:
                            excluded = True
                    case 'endDate': # Need to compare against GMT of filter
                        if image_gmt_dt > end_date_ts:
                            excluded = True
                    case 'startDate': # Need to compare against GMT of filter
                        if image_gmt_dt < start_date_ts:
                            excluded = True

                # Break loop as soon as it's excluded
                if excluded:
                    break

            # Return it if it's not excluded
            if not excluded:
                one_image['image_dt'] = image_dt
                cur_images.append(one_image)

        if len(cur_images) > 0:
            matches.append((one_upload, cur_images))

    return [cur_upload['info']|{'images':cur_images} for cur_upload,cur_images in matches]


def query_output(results: Results, results_id: str) -> tuple:
    """ Formats the results into something that can be returned to the caller
    Arguments:
        results: the results class containing the results of the filter_uploads function
        results_id: the unique identifier for this result
    Return:
        Returns a tuple containing the formatted results
    """
    if not results:
        return tuple()

    if not results.have_results():
        return tuple()

    return {'id': results_id,
            'DrSandersonOutput': get_dr_sanderson_output(results),
            'DrSandersonAllPictures': get_dr_sanderson_pictures(results),
            'csvRaw': get_csv_raw(results),
            'csvLocation': get_csv_location(results),
            'csvSpecies': get_csv_species(results),
            'imageDownloads': get_image_downloads(results),
            'tabs': {   # Information on tabs to display
                 # The order that the tabs are to be displayed
                 'order':['DrSandersonOutput','DrSandersonAllPictures','csvRaw', \
                                            'csvLocation','csvSpecies','imageDownloads'],
                 # The tab names
                 'DrSandersonOutput':'Dr. Sanderson\'s Output',
                 'DrSandersonAllPictures':'Dr. Sanderson\'s Pictures',
                 'csvRaw':'All Results',
                 'csvLocation':'Locations',
                 'csvSpecies':'Species',
                 'imageDownloads':'Image Download'
                },
            # Display column information
            'columns': {
                'DrSandersonAllPictures': {'location':'Location','species':'Species',\
                                           'image':'Image'},
                'csvRaw': {'image':'Image',
                           'date':'Date',
                           'location':{'title':'Location','locName':'Name','locId':'ID', \
                                        'locUtmZone':'UTM Zone','locX':'Easting',\
                                        'locY':'Northing','locElevation':'Elevation'
                                    },
                            'species':{'title':'Species',
                                     'common1':'Common Name','scientific1':'Scientific Name',\
                                     'count1':'Count','common2':'Common Name',\
                                     'scientific2':'Scientific Name','count2':'Count'},
                        },
                'csvLocation': {'name':'Name','id':'ID', 'locX':'Easting', \
                                'locY':'Northing', 'locElevation':'Elevation'},
                'csvSpecies': {'common':'Common Name', 'scientific':'Scientific Name'},
                'imageDownloads': {'name':'Name'}
            },
            # Download file information
            'downloads': {
                'DrSandersonOutput': 'drsanderson.csv',
                'DrSandersonAllPictures': 'drsanderson_all.gz',
                'csvRaw': 'raw.csv',
                'csvLocation': 'locations.csv',
                'csvSpecies': 'species.csv',
                'imageDownloads': 'images.gz',
            }
          }
