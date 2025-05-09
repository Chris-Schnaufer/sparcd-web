""" Functions to help queries """

def filter_uploads(uploads_info: tuple, filters: tuple) -> tuple:
    """ Filters the uploads against the filters and returns the selected
        images and their associated data
    Arguments:
        uploads_info: the tuple of uploads to filter
        filters: the filters to apply to the uploads
    """
    cur_uploads = uploads_info

    for one_filter in filters:
        new_matches = []
        match(one_filter[0]):
            case 'dayofweek':
            case 'elevations':
            case 'hour':
            case 'locations':
            case 'month':
            case 'species':
            case 'years':
            case 'endDate':
            case 'startDate':