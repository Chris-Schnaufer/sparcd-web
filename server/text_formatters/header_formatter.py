""" Formats header information """

import dataclasses
import os

from analysis import Analysis
from ..results import Results


# pylint: disable=consider-using-f-string
@dataclasses.dataclass
class HeaderFormatter:
    """ Formats search results headers
    """

    @staticmethod
    def print_locations(results: Results) -> str:
        """ Formats the locations header information
        Arguments:
            results: the query result
        Return:
            Returns the location header text
        """
        loc_names = [one_location['nameProperty'] for one_location in results.get_locations()]

        return "LOCATIONS " + str(len(results.get_locations())) + os.linesep + \
            ", ".join(loc_names) + os.linesep + os.linesep

    @staticmethod
    def print_species(results: Results) -> str:
        """ Formats the species header information
        Arguments:
            results: the query result
        Return:
            Returns the species header text
        """
        species_names = [one_species['name'] for one_species in results.get_species()]

        return "SPECIES " + str(len(results.get_species())) + os.linesep + \
            ", ".join(species_names) + os.linesep + os.linesep

    @staticmethod
    def print_image_analysis_header(results: tuple) -> str:
        """ Formats the image analysis header information
        Arguments:
            results: the results to search through
            interval_minutes: the interval between images to be considered the same period
                                (in minutes)
        Return:
            Returns the image analysis text
        """
        total_images = len(results['sorted_images_dt'])
        total_period = Analysis.period_for_image_list(results)

        return "FOR ALL SPECIES AT ALL LOCATIONS " + os.linesep + \
            "Number of pictures processed = " + str(total_images) + os.linesep + \
            "Number of pictures used in activity calculation = " + \
                                Analysis.activity_for_image_list(results) + os.linesep + \
            "Number of independent pictures used in analysis = " + \
                                total_period + os.linesep + \
            "Number of sequential pictures of same species at same location within a PERIOD = " + \
                                 (total_images - total_period) + os.linesep + \
            os.linesep
