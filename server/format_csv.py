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
        loc_name = image_loc['name'] if image_loc and 'name' in image_loc else ''
        loc_id = image_loc['idProperty'] if image_loc and 'idProperty' in image_loc else ''
        loc_utm_zone = image_loc['utmZone'] if image_loc and 'utmZone' in image_loc else ''
        loc_x = image_loc['latProperty'] if image_loc and 'latProperty' in image_loc else ''
        loc_y = image_loc['lngProperty'] if image_loc and 'lngProperty' in image_loc else ''
        loc_elevation = image_loc['elevation'] if image_loc and 'elevation' in image_loc else ''
        if 'species' in one_image and one_image['species']:
            for index, one_species in enumerate(one_image['species']):
                csv_results.append({
                    'image': one_image['name'],
                    'date': one_image['image_dt'],
                    'locName': loc_name,
                    'locId': loc_id,
                    'locUtmZone': loc_utm_zone,
                    'locX': loc_x,
                    'locY': loc_y,
                    'locElevation': loc_elevation,
                    'common' + str(index + 1): one_species['name'],
                    'scientific' + str(index + 1): one_species['scientificName'],
                    'count' + str(index + 1): str(one_species['count'])
                    })

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
        csv_results.append({'name': one_loc['name'],
                            'id': one_loc['idProperty'],
                            'locUtmZone': one_loc['utmZone'],
                            'locX': one_loc['latProperty'],
                            'locY': one_loc['lngProperty'],
                            'locElevation': one_loc['elevation']
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
