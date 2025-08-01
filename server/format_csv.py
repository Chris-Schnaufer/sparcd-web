""" Returns the results of queries in csv-friendly format """

from text_formatters.results import Results


def get_csv_raw(results: Results) -> str:
    """ Returns the "raw" results as CSV-compatible data
    Arguments:
        results: the query results
    Returns:
        A tuple of the csv fields in dict format
    """
    # TODO: coordinate conversion (return X and Y for all corrdinate systems)
    csv_results = []
    for one_image in results.get_images():
        image_loc = results.get_image_location(one_image['loc'])
        loc_name = image_loc['nameProperty'] if image_loc and 'nameProperty' in image_loc else ''
        loc_id = image_loc['idProperty'] if image_loc and 'idProperty' in image_loc else ''
        loc_x = image_loc['latProperty'] if image_loc and 'latProperty' in image_loc else ''
        loc_y = image_loc['lngProperty'] if image_loc and 'lngProperty' in image_loc else ''
        loc_elevation = image_loc['elevationProperty'] if image_loc and 'elevationProperty' \
                                                                            in image_loc else '0'
        utm_code = image_loc['utm_code'] if image_loc and 'utm_code' in image_loc else ''
        utm_x = image_loc['utm_x'] if image_loc and 'utm_x' in image_loc else ''
        utm_y = image_loc['utm_y'] if image_loc and 'utm_y' in image_loc else ''

        # Base image information, we add the species next
        cur_image = {
                    'image': one_image['name'],
                    'date': one_image['image_dt'].isoformat(),
                    'dateMDY':  one_image['image_dt'].strftime('%B %d, %Y'),
                    'dateSMDY': one_image['image_dt'].strftime('%b %d, %Y'),
                    'dateNMDY': one_image['image_dt'].strftime('%m/%d/%Y'),
                    'dateDMY': one_image['image_dt'].strftime('%d %B %Y'),
                    'dateDSMY': one_image['image_dt'].strftime('%d %b %Y'),
                    'dateDNMY': one_image['image_dt'].strftime('%d/%m/%Y'),
                    'time24': one_image['image_dt'].strftime('%H:%M'),
                    'time24s': one_image['image_dt'].strftime('%H:%M:%S'),
                    'time12': one_image['image_dt'].strftime('%I:%M %p'),
                    'time12s': one_image['image_dt'].strftime('%I:%M:%S %p'),
                    'locName': loc_name,
                    'locId': loc_id,
                    'locX': loc_x,
                    'locY': loc_y,
                    'utm_code': utm_code,
                    'utm_x': utm_x,
                    'utm_y': utm_y,
                    'locElevation': str(loc_elevation) + 'm',
                    's3_bucket':one_image['bucket'],
                    's3_path':one_image['s3_path'],
                    'locElevationFeet': str(round(float(loc_elevation)*3.28084, 2)) + 'ft',
                    }

        if 'species' in one_image and one_image['species']:
            for index, one_species in enumerate(one_image['species']):
                cur_image['common' + str(index + 1)] = one_species['name']
                cur_image['scientific' + str(index + 1)] = one_species['scientificName']
                cur_image['count' + str(index + 1)] = str(one_species['count'])


        # Set the default user's date-time
        date_format = results.user_settings['dateFormat'] if 'dateFormat' in results.user_settings else 'MDY'
        time_format = results.user_settings['timeFormat'] if 'timeFormat' in results.user_settings else '24'
        cur_image['dateDefault'] = cur_image['date'+date_format] + ' ' + \
                                   cur_image['time'+time_format]

        csv_results.append(cur_image)

    return csv_results


def get_csv_location(results: Results) -> str:
    """ Returns the locations results as CSV-compatible data
    Arguments:
        results: the query results
    Returns:
        A tuple of the csv fields in dict format
    """
    # TODO: Handle coordinate system formats
    csv_results = []
    for one_loc in results.get_locations():
        csv_results.append({'name': one_loc['nameProperty'],
                            'id': one_loc['idProperty'],
                            'locX': one_loc['latProperty'],
                            'locY': one_loc['lngProperty'],
                            'locElevation': str(one_loc['elevationProperty']) + 'm',
                            'utm_code': one_loc['utm_code'],
                            'utm_x': one_loc['utm_x'],
                            'utm_y': one_loc['utm_y'],
                            'locElevationFeet': \
                                str(round(float(one_loc['elevationProperty'])*3.28084, 2)) + 'ft',
                            })

    return  csv_results


def get_csv_species(results: Results) -> str:
    """ Returns the species results as CSV-compatible data
    Arguments:
        results: the query results
    Returns:
        A tuple of the csv fields in dict format
    """
    csv_results = []
    for one_species in results.get_species():
        csv_results.append({'common': one_species['name'], \
                            'scientific': one_species['scientificName']})

    return csv_results
