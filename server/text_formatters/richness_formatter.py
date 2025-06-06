""" Formats species richness calculations """

import dataclasses
import os

from .analysis import Analysis
from .results import Results

# pylint: disable=consider-using-f-string
@dataclasses.dataclass
class RichnessFormatter:
    """ Formats species richness calculations
    """

    @staticmethod
    def print_location_species_richness(results: Results) -> str:
        """ A table of locations vs. species showing the number of pictures of each species recorded
            at the location. The last column shows the number of species recorded at the location
            (Rich), and the last row shows total number of loations a species was recorded at
            (Richness)
        Arguments:
            results: the results to search through
        Return:
            Returns the image analysis text
        """
        result = 'LOCATIONS BY SPECIES AND LOCATION AND SPECIES RICHNESS' + os.linesep
        result += '  One record of each species per location per PERIOD' + os.linesep
        result += 'Location                          '

        for species in results.get_species_by_name():
            result += '{:<6s} '.format(species['name'][:6])
        result += 'Rich' + os.linesep

        for location in results.get_locations():
            result += '{:<28s}       '.format(location['nameProperty'])

            location_images = results.get_location_images(location['idProperty'])

            horizontal_richness = 0
            for species in results.get_species_by_name():
                location_species_images = results.filter_species(location_images, \
                                                                        species['scientificName'])

                period = Analysis.period_for_image_list(location_species_images, \
                                                                            results.get_interval())
                horizontal_richness = horizontal_richness + (0 if period == 0 else 1)
                result += '{:5d}  '.format(period)

            result += '{:5d}  '.format(horizontal_richness) + os.linesep

        result += 'Richness                           '

        for species in results.get_species():
            richness = 0
            species_images = results.get_species_images(species['scientificName'])

            for location in results.get_locations():
                species_location_images = results.filter_location(species_images, location['idProperty'])
                richness = richness + (0 if len(species_location_images) == 0 else 1)

            result += '{:5d}  '.format(richness)

        result += os.linesep + os.linesep

        return result
