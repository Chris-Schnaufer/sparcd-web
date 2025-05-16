""" Formats header information """

import os

def activityForImageList(results: tuple) -> int:
    """ Returns the number of distinct actions from the result set. Images MUST first be
    filtered by location and species to achieve a total accumulation
    Arguments:
        results: the results to analyze
    Returrns:
        The number of distinct actions found
    Notes:
        Actions are calculated when the time between two images is greater 
        than one hour
    """
    activities = 0

    prev_dt = None

    # Loop through the results and look at all the images
    for one_image in results['sorted_images_dt']:
        # Make sure we have what we need
        if not 'image_dt' in one_image or not one_image['image_dt']:
            continue

        # Get our first timestamp
        if prev_dt is None:
            activities += 1
            prev_dt = one_image['image_dt']
            continue

        # Compare minute difference in time to the limit (1 hour)
        if abs((one_image['image_dt'] - prev_dt).total_seconds()) / 60.0 >= 60:
            activities += 1
            prev_dt = one_image['image_dt']
            continue

    return activities


def periodForImageList(results: tuple, interval_minutes: int) -> int:
    """ Returns the number of distinct periods from the result set. Images MUST first be
    filtered by location and species to achieve a total accumulation
    Arguments:
        results: the results to analyze
        interval_minutes: the interval between images to be considered the same period (in minutes)
    Returrns:
        The number of distinct periods found
    Notes:
        Perriods are calculated when the time between two images is greater 
        than one hour
    """
    periods = 0

    prev_dt = None

    # Loop through the results and look at all the images
    for one_image in results['sorted_images_dt']:
        # Make sure we have what we need
        if not 'image_dt' in one_image or not one_image['image_dt']:
            continue

        # Get our first timestamp
        if prev_dt is None:
            periods += 1
            prev_dt = one_image['image_dt']
            continue

        # Compare minute difference in time to the limit (1 hour)
        if abs((one_image['image_dt'] - prev_dt).total_seconds()) / 60.0 <= interval_minutes:
            periods += 1
            prev_dt = one_image['image_dt']
            continue

    return periods


@dataclasses.dataclass
class HeaderFormatter:
    """ Formats search results headers
    """

    @staticmethod
    def printLocations(results: tuple, res_locations: tuple) -> str:
        """ Formats the locations header information
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
        Return:
            Returns the location header text
        """
        loc_names = [res_locations[one_key]['nameProperty'] for one_key in res_locations.keys() \
                                                    if one_key != "unknown" else "Unkown"]

        return "LOCATIONS " + str(len(res_locations.keys())) + os.linesep + \
            ", ".join(loc_names) + os.linesep + os.linesep

    @staticmethod
    def printSpecies(results: tuple, res_species: tuple) -> str:
        """ Formats the species header information
        Arguments:
            results: the results to search through
            res_species: all distinct result species information
        Return:
            Returns the species header text
        """
        species_names = [res_species[one_key]['name'] for one_key in res_species.keys() \
                                                    if one_key != "unknown" else "Unknown"]

        return "SPECIES " + str(len(res_species.keys())) + os.linesep + \
            ", ".join(species_names) + os.linesep + os.linesep

    @staticmethod
    def printImageAnalysisHeader(results: tuple, res_locations: tuple, res_species: tuple) -> str:
        """ Formats the image analysis header information
        Arguments:
            results: the results to search through
            res_locations: all distinct result locations
            res_species: all distinct result species information
        Return:
            Returns the image analysis text
        """
        total_images = len(results['sorted_images_dt'])
        total_period = periodForImageList(results)

        return "FOR ALL SPECIES AT ALL LOCATIONS " + os.linesep + \
            "Number of pictures processed = " + str(total_images) + os.linesep + \
            "Number of pictures used in activity calculation = " + \
                                activityForImageList(results) + os.linesep + \
            "Number of independent pictures used in analysis = " + \
                                total_period + os.linesep + \
            "Number of sequential pictures of same species at same location within a PERIOD = " + \
                                 (total_images - total_period) + os.linesep + \
            os.linesep
